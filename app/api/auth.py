from __future__ import annotations

from fastapi import HTTPException, status

from app.config import Settings
from app.services.telegram.webapp_auth import verify_telegram_webapp_init_data


def require_telegram_operator(settings: Settings, init_data: str | None) -> None:
    if settings.app_env != "prod":
        return
    if not settings.telegram_bot_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram bot token is not configured",
        )
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram initData is required",
        )
    try:
        verify_telegram_webapp_init_data(
            init_data,
            settings.telegram_bot_token,
            max_age_seconds=settings.telegram_webapp_max_age_seconds,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
