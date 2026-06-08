from __future__ import annotations

from fastapi import APIRouter

from app.api.store import INTAKE_EVENTS

router = APIRouter(prefix="/intake", tags=["intake"])


@router.get("/events")
async def list_intake_events() -> list[dict]:
    return INTAKE_EVENTS
