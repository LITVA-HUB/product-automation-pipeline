import hashlib
import hmac
from urllib.parse import urlencode

import pytest

from app.services.telegram.webapp_auth import verify_telegram_webapp_init_data


def test_verify_telegram_webapp_init_data_accepts_signed_payload():
    init_data = _signed_init_data({"auth_date": "100", "user": '{"id":42,"username":"operator"}'})

    user = verify_telegram_webapp_init_data(init_data, "bot-token", now=120)

    assert user.id == 42
    assert user.username == "operator"


def test_verify_telegram_webapp_init_data_rejects_invalid_hash():
    init_data = _signed_init_data({"auth_date": "100", "user": '{"id":42}'}) + "broken"

    with pytest.raises(ValueError, match="invalid"):
        verify_telegram_webapp_init_data(init_data, "bot-token", now=120)


def test_verify_telegram_webapp_init_data_rejects_expired_payload():
    init_data = _signed_init_data({"auth_date": "100", "user": '{"id":42}'})

    with pytest.raises(ValueError, match="expired"):
        verify_telegram_webapp_init_data(init_data, "bot-token", max_age_seconds=10, now=120)


def _signed_init_data(values: dict[str, str], bot_token: str = "bot-token") -> str:
    data_check_string = "\n".join(f"{key}={values[key]}" for key in sorted(values))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    payload = dict(values)
    payload["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(payload)
