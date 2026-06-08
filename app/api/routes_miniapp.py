from __future__ import annotations

from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.moysklad.client import MoySkladRestClient
from app.adapters.repositories.intake_repository import IntakeRepository, row_to_event
from app.adapters.repositories.product_repository import ProductRepository
from app.api.auth import require_telegram_operator
from app.api.dependencies import get_db_session, get_settings
from app.config import Settings
from app.domain.publication import PublicationMode
from app.services.intake.service import IntakeService
from app.services.miniapp.workflow import (
    CreateMoySkladRequest,
    DraftFromIntakeRequest,
    ProductDraftPatch,
    apply_operator_patch,
    build_ms_payload,
    candidate_from_intake,
    load_ms_maps,
    validate_operator_candidate,
)
from app.services.telegram.intake import IntakeEvent
from app.workflow.states import WorkflowStatus

router = APIRouter(prefix="/miniapp", tags=["miniapp"])


@router.get("", response_class=HTMLResponse)
async def miniapp_index() -> HTMLResponse:
    html = Path(__file__).with_name("miniapp.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


class MiniAppTextIntakeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)


@router.get("/api/intake/events")
async def miniapp_intake_events(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_init_data: str | None = Header(default=None),
) -> list[dict]:
    require_telegram_operator(settings, x_telegram_init_data)
    rows = IntakeRepository(session).list_pending(limit=200)
    return [row_to_event(row).model_dump(mode="json") for row in rows]


@router.post("/api/intake/text", status_code=status.HTTP_201_CREATED)
async def miniapp_submit_text_intake(
    request: MiniAppTextIntakeRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_init_data: str | None = Header(default=None),
) -> dict:
    require_telegram_operator(settings, x_telegram_init_data)
    item = IntakeService().from_text(request.text)
    event = IntakeEvent(
        source="miniapp",
        item=item,
        raw_update={"miniapp": {"type": "text", "text": request.text}},
    )
    row = IntakeRepository(session).save(event)
    return row_to_event(row).model_dump(mode="json")


@router.post("/api/intake/file", status_code=status.HTTP_201_CREATED)
async def miniapp_submit_file_intake(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    file: Annotated[UploadFile, File()],
    caption: Annotated[str, Form()] = "",
    x_telegram_init_data: str | None = Header(default=None),
) -> dict:
    require_telegram_operator(settings, x_telegram_init_data)
    event_id = uuid4()
    storage_path = await _save_miniapp_upload(settings, event_id, file)
    item = IntakeService().from_file(
        file_name=file.filename or f"{event_id}.bin",
        content_type=file.content_type or "application/octet-stream",
        storage_path=str(storage_path),
    )
    if caption.strip():
        item.payload["caption"] = caption.strip()
    event = IntakeEvent(
        id=event_id,
        source="miniapp",
        item=item,
        raw_update={
            "miniapp": {
                "type": "file",
                "file_name": file.filename,
                "content_type": file.content_type,
                "caption": caption,
            }
        },
    )
    row = IntakeRepository(session).save(event)
    return row_to_event(row).model_dump(mode="json")


@router.post(
    "/api/intake/events/{event_id}/draft",
    status_code=status.HTTP_201_CREATED,
)
async def miniapp_create_draft_from_intake(
    event_id: UUID,
    request: DraftFromIntakeRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_init_data: str | None = Header(default=None),
) -> dict:
    require_telegram_operator(settings, x_telegram_init_data)
    intake_repository = IntakeRepository(session)
    row = intake_repository.get(event_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intake event not found")

    event = row_to_event(row)
    candidate = candidate_from_intake(event, request)
    ProductRepository(session).save(candidate)
    row = intake_repository.set_status(
        event_id,
        "drafted",
        {"product_id": str(candidate.id)},
    )
    return {
        "intake": row_to_event(row).model_dump(mode="json") if row else None,
        "product": candidate.model_dump(mode="json"),
    }


@router.put("/api/products/{product_id}/draft")
async def miniapp_save_product_draft(
    product_id: UUID,
    request: ProductDraftPatch,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_init_data: str | None = Header(default=None),
) -> dict:
    require_telegram_operator(settings, x_telegram_init_data)
    product_repository = ProductRepository(session)
    candidate = product_repository.get(product_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    candidate = apply_operator_patch(candidate, request)
    product_repository.save(candidate)
    return candidate.model_dump(mode="json")


@router.post("/api/products/{product_id}/validate")
async def miniapp_validate_product(
    product_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_init_data: str | None = Header(default=None),
) -> dict:
    require_telegram_operator(settings, x_telegram_init_data)
    product_repository = ProductRepository(session)
    candidate = product_repository.get(product_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    candidate, validation = validate_operator_candidate(candidate)
    product_repository.save(candidate)
    payload = candidate.model_dump(mode="json")
    payload["validation"] = validation.model_dump(mode="json")
    return payload


@router.post("/api/products/{product_id}/create-ms")
async def miniapp_create_product_in_ms(
    product_id: UUID,
    request: CreateMoySkladRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_init_data: str | None = Header(default=None),
) -> dict:
    require_telegram_operator(settings, x_telegram_init_data)
    if not settings.moysklad_writes_enabled:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="MoySklad writes are disabled",
        )
    if not request.confirm_ms_only:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="MS-only confirmation is required",
        )
    if not settings.moysklad_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MoySklad token is not configured",
        )

    product_repository = ProductRepository(session)
    candidate = product_repository.get(product_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if candidate.publication_mode != PublicationMode.MS_ONLY:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only MS-only creation is allowed from the Mini App",
        )

    candidate, validation = validate_operator_candidate(candidate)
    if not validation.passed:
        product_repository.save(candidate)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Product validation failed",
                "errors": validation.model_dump(mode="json"),
            },
        )

    ms_maps = _load_maps_or_503(settings)
    ms_payload = build_ms_payload(candidate, ms_maps)
    ms_client = MoySkladRestClient(settings.moysklad_token)
    existing = await ms_client.find_product_by_article(str(candidate.article.value))
    if existing:
        candidate.status = WorkflowStatus.POSSIBLE_DUPLICATE
        candidate.human_review_required = True
        if "moysklad_duplicate" not in candidate.review_reasons:
            candidate.review_reasons.append("moysklad_duplicate")
        product_repository.save(candidate)
        return {
            "status": "duplicate",
            "product": candidate.model_dump(mode="json"),
            "existing": existing,
        }

    ms_product = await ms_client.create_product(ms_payload)
    candidate.ms_product_id = ms_product["id"]
    candidate.ms_product_code = ms_product.get("code")
    candidate.status = WorkflowStatus.CREATED_IN_MS
    if candidate.main_image:
        await ms_client.upload_image(candidate.ms_product_id, candidate.main_image)
    candidate.status = WorkflowStatus.MS_VERIFIED
    product_repository.save(candidate)
    return {"status": "created", "product": candidate.model_dump(mode="json")}


def _load_maps_or_503(settings: Settings) -> dict:
    try:
        return load_ms_maps(settings.moysklad_maps_path)
    except (FileNotFoundError, ValueError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MoySklad maps are not configured",
        ) from exc


async def _save_miniapp_upload(settings: Settings, event_id: UUID, file: UploadFile) -> Path:
    suffix = Path(file.filename or "").suffix
    target_dir = Path(settings.local_storage_path) / "miniapp" / str(event_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"source{suffix}"
    target.write_bytes(await file.read())
    return target
