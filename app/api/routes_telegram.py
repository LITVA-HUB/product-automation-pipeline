from __future__ import annotations

import os

from fastapi import APIRouter, Header, HTTPException, status

from app.api.store import INTAKE_EVENTS
from app.services.telegram.intake import TelegramIntakeService

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def telegram_webhook(
    update: dict,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    expected_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if expected_secret and x_telegram_bot_api_secret_token != expected_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram webhook secret")

    event = TelegramIntakeService().from_update(update)
    payload = event.model_dump(mode="json")
    INTAKE_EVENTS.append(payload)
    return payload
