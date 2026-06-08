from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_manual_product_endpoint_creates_and_reads_candidate():
    client = TestClient(app)

    created = client.post(
        "/products/manual",
        json={"supplier": "Kerama", "raw_name": "Tile", "raw_article": "A-1"},
    )

    assert created.status_code == 201
    product_id = created.json()["id"]

    loaded = client.get(f"/products/{product_id}")

    assert loaded.status_code == 200
    assert loaded.json()["supplier"] == "Kerama"
    assert loaded.json()["raw_name"] == "Tile"


def test_review_approve_moves_ready_item_to_approved():
    client = TestClient(app)
    created = client.post(
        "/products/manual",
        json={"supplier": "Kerama", "raw_name": "Tile", "raw_article": "A-1"},
    )
    product_id = created.json()["id"]

    review = client.post(f"/review/{product_id}/decision", json={"decision": "approve"})

    assert review.status_code == 200
    assert review.json()["status"] == "approved"


def test_review_decision_accepts_audit_ready_corrections():
    client = TestClient(app)
    created = client.post(
        "/products/manual",
        json={"supplier": "Kerama", "raw_name": "Tile", "raw_article": "A-1"},
    )
    product_id = created.json()["id"]

    review = client.post(
        f"/review/{product_id}/decision",
        json={
            "decision": "approve",
            "operator": "operator@example.com",
            "corrections": {"color": "серый"},
            "before": {"color": "бежевый"},
            "after": {"color": "серый"},
        },
    )

    assert review.status_code == 200
    assert review.json()["review"]["corrections"] == {"color": "серый"}
