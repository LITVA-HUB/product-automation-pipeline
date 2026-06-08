from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.adapters.repositories.intake_repository import IntakeRepository
from app.adapters.repositories.models import Base
from app.services.telegram.intake import TelegramIntakeService


def test_telegram_text_update_becomes_supplier_url_intake():
    update = {
        "message": {
            "message_id": 1,
            "from": {"id": 100, "username": "operator"},
            "chat": {"id": 200},
            "text": "посмотри https://supplier.example/tile/123",
        }
    }

    event = TelegramIntakeService().from_update(update)

    assert event.source == "telegram"
    assert event.operator_id == "100"
    assert event.chat_id == "200"
    assert event.item.kind == "supplier_url"
    assert event.item.payload["url"] == "https://supplier.example/tile/123"


def test_telegram_document_update_becomes_table_intake():
    update = {
        "message": {
            "from": {"id": 100},
            "chat": {"id": 200},
            "document": {
                "file_id": "file-1",
                "file_name": "new-products.xlsx",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
        }
    }

    event = TelegramIntakeService().from_update(update)

    assert event.item.kind == "table"
    assert event.item.payload["telegram_file_id"] == "file-1"
    assert event.item.payload["storage_path"] == "telegram://file-1"


def test_telegram_photo_update_becomes_invoice_image_intake_with_caption():
    update = {
        "message": {
            "from": {"id": 100},
            "chat": {"id": 200},
            "caption": "накладная по новым плитам",
            "photo": [
                {"file_id": "small", "width": 100, "height": 100},
                {"file_id": "large", "width": 1200, "height": 900},
            ],
        }
    }

    event = TelegramIntakeService().from_update(update)

    assert event.item.kind == "image_invoice"
    assert event.item.payload["telegram_file_id"] == "large"
    assert event.item.payload["caption"] == "накладная по новым плитам"


def test_intake_repository_persists_telegram_event():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False, future=True)
    event = TelegramIntakeService().from_update(
        {"message": {"from": {"id": 100}, "chat": {"id": 200}, "text": "ART-001 плитка"}}
    )

    with Session() as session:
        repo = IntakeRepository(session)
        row = repo.save(event)
        session.commit()

    with Session() as session:
        rows = IntakeRepository(session).list_pending()

    assert row.id is not None
    assert len(rows) == 1
    assert rows[0].kind == "text"
    assert rows[0].payload["text"] == "ART-001 плитка"
