from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.adapters.repositories.intake_repository import IntakeRepository, row_to_event
from app.api.auth import require_telegram_operator
from app.api.dependencies import get_db_session, get_settings
from app.config import Settings

router = APIRouter(prefix="/intake", tags=["intake"])


@router.get("/events")
async def list_intake_events(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_init_data: str | None = Header(default=None),
) -> list[dict]:
    require_telegram_operator(settings, x_telegram_init_data)
    rows = IntakeRepository(session).list_pending()
    return [row_to_event(row).model_dump(mode="json") for row in rows]
