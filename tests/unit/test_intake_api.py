from fastapi.testclient import TestClient

from app.adapters.repositories.models import IntakeEventRow
from app.api.dependencies import get_session_factory, get_settings
from app.main import app


def test_telegram_webhook_stores_intake_event_for_review_queue():
    _clear_intake_events()
    client = TestClient(app)

    response = client.post(
        "/telegram/webhook",
        json={"message": {"from": {"id": 100}, "chat": {"id": 200}, "text": "ART-001 плитка"}},
    )

    assert response.status_code == 202
    assert response.json()["item"]["kind"] == "text"

    queue = client.get("/intake/events")

    assert queue.status_code == 200
    assert queue.json()[0]["item"]["payload"]["text"] == "ART-001 плитка"


def test_telegram_webhook_rejects_invalid_secret(monkeypatch):
    _clear_intake_events()
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "expected-secret")
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post(
        "/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
        json={"message": {"from": {"id": 100}, "chat": {"id": 200}, "text": "ART-001 плитка"}},
    )

    assert response.status_code == 401
    queue = client.get("/intake/events")
    assert queue.status_code == 200
    assert queue.json() == []
    monkeypatch.delenv("TELEGRAM_WEBHOOK_SECRET")
    get_settings.cache_clear()


def _clear_intake_events() -> None:
    factory = get_session_factory()
    with factory() as session:
        session.query(IntakeEventRow).delete()
        session.commit()
