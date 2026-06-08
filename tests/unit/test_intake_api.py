from fastapi.testclient import TestClient

from app.api.store import INTAKE_EVENTS
from app.main import app


def test_telegram_webhook_stores_intake_event_for_review_queue():
    INTAKE_EVENTS.clear()
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
    INTAKE_EVENTS.clear()
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "expected-secret")
    client = TestClient(app)

    response = client.post(
        "/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
        json={"message": {"from": {"id": 100}, "chat": {"id": 200}, "text": "ART-001 плитка"}},
    )

    assert response.status_code == 401
    assert INTAKE_EVENTS == []
