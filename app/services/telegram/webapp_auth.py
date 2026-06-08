from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl


@dataclass(frozen=True)
class TelegramWebAppUser:
    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


def verify_telegram_webapp_init_data(
    init_data: str,
    bot_token: str,
    max_age_seconds: int = 24 * 60 * 60,
    now: int | None = None,
) -> TelegramWebAppUser:
    values = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = values.pop("hash", None)
    if not received_hash:
        raise ValueError("Telegram initData hash is missing")

    data_check_string = "\n".join(f"{key}={values[key]}" for key in sorted(values))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("Telegram initData hash is invalid")

    auth_date = int(values.get("auth_date", "0"))
    current_time = int(time.time()) if now is None else now
    if max_age_seconds > 0 and current_time - auth_date > max_age_seconds:
        raise ValueError("Telegram initData is expired")

    raw_user = values.get("user")
    if not raw_user:
        raise ValueError("Telegram initData user is missing")
    user = json.loads(raw_user)
    return TelegramWebAppUser(
        id=int(user["id"]),
        username=user.get("username"),
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
    )
