from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.adapters.repositories.intake_repository import IntakeRepository, row_to_event
from app.api.dependencies import get_db_session, get_settings
from app.config import Settings
from app.services.telegram.webapp_auth import verify_telegram_webapp_init_data

router = APIRouter(prefix="/miniapp", tags=["miniapp"])


@router.get("", response_class=HTMLResponse)
async def miniapp_index() -> HTMLResponse:
    html = Path(__file__).with_name("miniapp.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@router.get("/api/intake/events")
async def miniapp_intake_events(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_init_data: str | None = Header(default=None),
) -> list[dict]:
    _require_telegram_operator(settings, x_telegram_init_data)
    rows = IntakeRepository(session).list_pending(limit=200)
    return [row_to_event(row).model_dump(mode="json") for row in rows]


def _require_telegram_operator(settings: Settings, init_data: str | None) -> None:
    if settings.app_env != "prod":
        return
    if not settings.telegram_bot_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram bot token is not configured",
        )
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Telegram initData is required"
        )
    try:
        verify_telegram_webapp_init_data(
            init_data,
            settings.telegram_bot_token,
            max_age_seconds=settings.telegram_webapp_max_age_seconds,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
