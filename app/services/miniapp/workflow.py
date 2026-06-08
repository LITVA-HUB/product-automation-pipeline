from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.adapters.moysklad.mappers import candidate_to_ms_product
from app.domain.product_candidate import FieldWithConfidence, ProductCandidate, ValidationErrorItem
from app.domain.publication import PublicationMode
from app.services.naming.service import construct_names
from app.services.rules.product_rules import apply_business_rules
from app.services.telegram.intake import IntakeEvent
from app.services.validation.service import ValidationResult, validate_before_ms
from app.workflow.states import WorkflowStatus


class DraftFromIntakeRequest(BaseModel):
    supplier: str = "Не указан"
    group_ms: str | None = None


class ProductDraftPatch(BaseModel):
    supplier: str | None = None
    raw_name: str | None = None
    raw_article: str | None = None
    raw_price: str | None = None
    raw_description: str | None = None
    source_url: str | None = None
    article: str | None = None
    supplier_code: str | None = None
    product_type: str | None = None
    unit: str | None = None
    units_per_package: str | Decimal | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    thickness_mm: str | Decimal | None = None
    color: str | None = None
    surface: str | None = None
    texture: str | None = None
    country: str | None = None
    manufacturer: str | None = None
    brand_collection: str | None = None
    site_manufacturer: str | None = None
    site_collection: str | None = None
    retail_price: str | Decimal | None = None
    group_ms: str | None = None
    main_image: str | None = None
    publication_mode: PublicationMode = PublicationMode.MS_ONLY


class CreateMoySkladRequest(BaseModel):
    confirm_ms_only: bool = False


def candidate_from_intake(event: IntakeEvent, request: DraftFromIntakeRequest) -> ProductCandidate:
    text = _event_text(event)
    source_url = event.item.payload.get("url")
    storage_path = event.item.payload.get("storage_path")
    raw_images = [storage_path] if event.item.kind == "image_invoice" and storage_path else []
    candidate = ProductCandidate(
        supplier=request.supplier,
        source_type=f"{event.source}_{event.item.kind}",
        source_url=source_url,
        raw_name=_guess_name(text),
        raw_article=_first_article(text),
        raw_price=_first_price(text),
        raw_description=text or event.item.payload.get("caption"),
        raw_fields=event.item.payload,
        raw_images=raw_images,
        group_ms=request.group_ms,
        status=WorkflowStatus.PARSED,
    )
    if candidate.raw_article:
        candidate.article = _operator_field(candidate.raw_article)
    return candidate


def apply_operator_patch(candidate: ProductCandidate, patch: ProductDraftPatch) -> ProductCandidate:
    updates = patch.model_dump(exclude_unset=True)
    for field in (
        "supplier",
        "raw_name",
        "raw_article",
        "raw_price",
        "raw_description",
        "source_url",
    ):
        if field in updates:
            setattr(candidate, field, updates[field])
    if "article" in updates:
        candidate.article = _operator_field(updates["article"])
    if "supplier_code" in updates:
        candidate.supplier_code = _operator_field(updates["supplier_code"])
    if "product_type" in updates:
        candidate.product_type = _operator_field(updates["product_type"])
    if "unit" in updates:
        candidate.unit = _operator_field(updates["unit"])
    if "units_per_package" in updates:
        candidate.units_per_package = _operator_field(
            _decimal_or_none(updates["units_per_package"])
        )
    if "width_mm" in updates:
        candidate.width_mm = _operator_field(updates["width_mm"])
    if "height_mm" in updates:
        candidate.height_mm = _operator_field(updates["height_mm"])
    if "thickness_mm" in updates:
        candidate.thickness_mm = _operator_field(_decimal_or_none(updates["thickness_mm"]))
    for field in (
        "color",
        "surface",
        "texture",
        "country",
        "manufacturer",
        "brand_collection",
        "site_manufacturer",
        "site_collection",
    ):
        if field in updates:
            setattr(candidate, field, _operator_field(updates[field]))
    if "retail_price" in updates:
        candidate.retail_price = _decimal_or_none(updates["retail_price"])
    if "group_ms" in updates:
        candidate.group_ms = updates["group_ms"]
    if "main_image" in updates:
        candidate.main_image = updates["main_image"]
    if "publication_mode" in updates:
        candidate.publication_mode = updates["publication_mode"]
        candidate.site_export_required = updates["publication_mode"] != PublicationMode.MS_ONLY
    candidate.status = WorkflowStatus.READY_FOR_REVIEW
    return candidate


def validate_operator_candidate(
    candidate: ProductCandidate,
) -> tuple[ProductCandidate, ValidationResult]:
    candidate = construct_names(candidate)
    try:
        candidate = apply_business_rules(candidate)
    except ValueError as exc:
        candidate.status = WorkflowStatus.VALIDATION_FAILED
        candidate.human_review_required = True
        validation = ValidationResult(
            scope="before_ms",
            passed=False,
            errors=[
                ValidationErrorItem(
                    scope="before_ms",
                    field=str(exc).split(" ", 1)[0],
                    message=str(exc),
                )
            ],
        )
        candidate.validation_errors = validation.errors
        return candidate, validation

    validation = validate_before_ms(candidate)
    candidate.validation_errors = validation.errors
    candidate.human_review_required = not validation.passed
    candidate.status = (
        WorkflowStatus.VALIDATED_BEFORE_MS
        if validation.passed
        else WorkflowStatus.VALIDATION_FAILED
    )
    return candidate, validation


def build_ms_payload(candidate: ProductCandidate, maps: dict[str, Any]) -> dict[str, Any]:
    if candidate.status != WorkflowStatus.VALIDATED_BEFORE_MS:
        candidate, validation = validate_operator_candidate(candidate)
        if not validation.passed:
            raise ValueError("candidate must pass validation before МойСклад write")
    return candidate_to_ms_product(candidate, maps)


def load_ms_maps(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _event_text(event: IntakeEvent) -> str:
    payload = event.item.payload
    parts = [
        payload.get("text"),
        payload.get("caption"),
        payload.get("url"),
        payload.get("file_name"),
    ]
    return "\n".join(str(part) for part in parts if part)


def _guess_name(text: str) -> str | None:
    if not text:
        return None
    cleaned = re.sub(r"https?://\S+", "", text).strip()
    return cleaned[:180] or None


def _first_article(text: str) -> str | None:
    match = re.search(
        r"\b(?=[A-ZА-Я0-9._/-]*[A-ZА-Я])(?=[A-ZА-Я0-9._/-]*\d)[A-ZА-Я0-9._/-]{4,}\b",
        text,
    )
    return match.group(0) if match else None


def _first_price(text: str) -> str | None:
    match = re.search(
        r"(?:цена|price)?\s*(\d{3,}(?:[,.]\d{1,2})?)",
        text,
        flags=re.IGNORECASE,
    )
    return match.group(1).replace(",", ".") if match else None


def _operator_field(value: object) -> FieldWithConfidence:
    return FieldWithConfidence(value=value, confidence=1, source="operator")


def _decimal_or_none(value: object) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))
