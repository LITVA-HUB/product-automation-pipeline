from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.repositories.intake_repository import IntakeRepository, row_to_event
from app.api.dependencies import get_db_session, get_settings
from app.config import Settings
from app.services.telegram.files import TelegramFileDownloader
from app.services.telegram.intake import TelegramIntakeService

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def telegram_webhook(
    update: dict,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    if settings.telegram_webhook_secret and (
        x_telegram_bot_api_secret_token != settings.telegram_webhook_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram webhook secret"
        )

    event = TelegramIntakeService().from_update(update)
    if settings.telegram_bot_token and event.item.payload.get("telegram_file_id"):
        downloader = TelegramFileDownloader(
            settings.telegram_bot_token,
            storage_root=settings.local_storage_path,
        )
        try:
            event = await downloader.download_for_event(event)
        finally:
            await downloader.close()

    row = IntakeRepository(session).save(event)
    return row_to_event(row).model_dump(mode="json")
