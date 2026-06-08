from fastapi.testclient import TestClient

from app.adapters.repositories.models import IntakeEventRow
from app.api.dependencies import get_session_factory, get_settings
from app.main import app


def test_miniapp_index_serves_operator_ui():
    client = TestClient(app)

    response = client.get("/miniapp")

    assert response.status_code == 200
    assert "Новая плитка" in response.text
    assert "Откройте через Telegram" in response.text
    assert "/miniapp/api/intake/events" in response.text
    assert "К очереди" in response.text
    assert "Открыть" in response.text
    assert "Добавить данные" in response.text
    assert "Добавить в очередь" in response.text


def test_miniapp_intake_events_available_in_dev():
    client = TestClient(app)

    response = client.get("/miniapp/api/intake/events")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_miniapp_can_submit_text_to_queue():
    _clear_intake_events()
    client = TestClient(app)

    response = client.post(
        "/miniapp/api/intake/text",
        json={"text": "Новые плиты ART-123 Atlas 60x120 цена 2400"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["source"] == "miniapp"
    assert body["item"]["kind"] == "text"
    assert body["item"]["payload"]["text"] == "Новые плиты ART-123 Atlas 60x120 цена 2400"


def test_miniapp_can_submit_file_to_queue(tmp_path, monkeypatch):
    _clear_intake_events()
    monkeypatch.setenv("LOCAL_STORAGE_PATH", str(tmp_path))
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post(
        "/miniapp/api/intake/file",
        files={"file": ("prices.xlsx", b"fake sheet", "application/vnd.ms-excel")},
        data={"caption": "Прайс поставщика"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["source"] == "miniapp"
    assert body["item"]["kind"] == "table"
    assert body["item"]["payload"]["caption"] == "Прайс поставщика"
    assert body["item"]["payload"]["storage_path"].startswith(str(tmp_path))
    get_settings.cache_clear()


def _clear_intake_events() -> None:
    factory = get_session_factory()
    with factory() as session:
        session.query(IntakeEventRow).delete()
        session.commit()
