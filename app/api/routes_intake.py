from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.adapters.repositories.intake_repository import IntakeRepository, row_to_event
from app.api.dependencies import get_db_session

router = APIRouter(prefix="/intake", tags=["intake"])


@router.get("/events")
async def list_intake_events(
    session: Annotated[Session, Depends(get_db_session)],
) -> list[dict]:
    rows = IntakeRepository(session).list_pending()
    return [row_to_event(row).model_dump(mode="json") for row in rows]
