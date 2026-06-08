from app.services.intake.service import IntakeService


def test_intake_classifies_supplier_url_from_text():
    item = IntakeService().from_text("https://supplier.example/tile/atlas-boost")

    assert item.kind == "supplier_url"
    assert item.payload["url"] == "https://supplier.example/tile/atlas-boost"


def test_intake_classifies_plain_text_list():
    item = IntakeService().from_text("ART-001 Atlas Boost 60x120\nART-002 Atlas Boost Grey")

    assert item.kind == "text"
    assert "ART-001" in item.payload["text"]


def test_intake_classifies_table_file():
    item = IntakeService().from_file(
        file_name="new-products.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        storage_path="local_storage/inbox/new-products.xlsx",
    )

    assert item.kind == "table"
    assert item.payload["storage_path"] == "local_storage/inbox/new-products.xlsx"


def test_intake_classifies_invoice_image():
    item = IntakeService().from_file(
        file_name="invoice.jpg",
        content_type="image/jpeg",
        storage_path="local_storage/inbox/invoice.jpg",
    )

    assert item.kind == "image_invoice"
    assert item.payload["file_name"] == "invoice.jpg"
