from fastapi.testclient import TestClient

from app.adapters.repositories.models import IntakeEventRow, ProductRow
from app.api.dependencies import get_session_factory, get_settings
from app.main import app


def test_manager_can_turn_intake_text_into_product_draft():
    _clear_manager_data()
    client = TestClient(app)
    intake = client.post(
        "/telegram/webhook",
        json={
            "message": {
                "from": {"id": 100},
                "chat": {"id": 200},
                "text": "Новые плиты ART-777 Atlas Boost Pearl 60x120 цена 2100",
            }
        },
    ).json()

    response = client.post(
        f"/miniapp/api/intake/events/{intake['id']}/draft",
        json={"supplier": "Test Supplier"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["intake"]["status"] == "drafted"
    assert body["product"]["supplier"] == "Test Supplier"
    assert body["product"]["source_type"] == "telegram_text"
    assert body["product"]["status"] == "parsed"
    assert body["product"]["raw_article"] == "ART-777"


def test_manager_can_save_validate_and_keep_site_disabled_by_default():
    _clear_manager_data()
    client = TestClient(app)
    product = client.post(
        "/products/manual",
        json={"supplier": "Test Supplier", "raw_name": "Atlas Boost Pearl"},
    ).json()

    saved = client.put(
        f"/miniapp/api/products/{product['id']}/draft",
        json=_valid_product_patch(),
    )
    validated = client.post(f"/miniapp/api/products/{product['id']}/validate")

    assert saved.status_code == 200
    assert validated.status_code == 200
    body = validated.json()
    assert body["status"] == "validated_before_ms"
    assert body["publication_mode"] == "ms_only"
    assert body["site_export_required"] is False
    assert body["purchase_price"] == "1680.00"
    assert body["site_price"] == "2415.00"


def test_ms_create_endpoint_is_blocked_until_writes_are_enabled():
    _clear_manager_data()
    get_settings.cache_clear()
    client = TestClient(app)
    product = client.post("/products/manual", json={"supplier": "Test Supplier"}).json()
    client.put(f"/miniapp/api/products/{product['id']}/draft", json=_valid_product_patch())
    client.post(f"/miniapp/api/products/{product['id']}/validate")

    response = client.post(
        f"/miniapp/api/products/{product['id']}/create-ms",
        json={"confirm_ms_only": True},
    )

    assert response.status_code == 423
    assert response.json()["detail"] == "MoySklad writes are disabled"


def test_miniapp_html_exposes_manager_workflow_controls():
    client = TestClient(app)

    response = client.get("/miniapp")

    assert response.status_code == 200
    assert "Завести в МС" in response.text
    assert "Проверить поля" in response.text
    assert "miniapp/api/products" in response.text


def _valid_product_patch() -> dict:
    return {
        "supplier": "Test Supplier",
        "raw_name": "Atlas Boost Pearl 60x120",
        "article": "ART-777",
        "supplier_code": "SUP-777",
        "unit": "м²",
        "units_per_package": "1.15",
        "width_mm": 600,
        "height_mm": 1200,
        "thickness_mm": 9,
        "color": "бежевый",
        "surface": "матовая",
        "texture": "камень",
        "site_manufacturer": "Atlas",
        "site_collection": "Boost Pearl",
        "retail_price": "2100.00",
        "group_ms": "Atlas",
        "main_image": "/images/main.jpg",
        "publication_mode": "ms_only",
    }


def _clear_manager_data() -> None:
    factory = get_session_factory()
    with factory() as session:
        session.query(IntakeEventRow).delete()
        session.query(ProductRow).delete()
        session.commit()
