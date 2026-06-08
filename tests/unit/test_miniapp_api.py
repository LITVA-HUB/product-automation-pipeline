from fastapi.testclient import TestClient

from app.main import app


def test_miniapp_index_serves_operator_ui():
    client = TestClient(app)

    response = client.get("/miniapp")

    assert response.status_code == 200
    assert "Очередь товаров" in response.text
    assert "Откройте через Telegram" in response.text
    assert "/miniapp/api/intake/events" in response.text
    assert "К очереди" in response.text


def test_miniapp_intake_events_available_in_dev():
    client = TestClient(app)

    response = client.get("/miniapp/api/intake/events")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
