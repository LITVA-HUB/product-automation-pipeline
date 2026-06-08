from fastapi.testclient import TestClient

from app.api.dependencies import get_settings
from app.main import app


def teardown_function() -> None:
    get_settings.cache_clear()


def test_raw_intake_api_requires_telegram_auth_in_prod(monkeypatch):
    _enable_prod_auth(monkeypatch)
    client = TestClient(app)

    response = client.get("/intake/events")

    assert response.status_code == 401


def test_manual_product_api_requires_telegram_auth_in_prod(monkeypatch):
    _enable_prod_auth(monkeypatch)
    client = TestClient(app)

    response = client.post("/products/manual", json={"supplier": "Test Supplier"})

    assert response.status_code == 401


def _enable_prod_auth(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token")
    get_settings.cache_clear()
