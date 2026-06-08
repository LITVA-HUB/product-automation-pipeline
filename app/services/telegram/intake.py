from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.services.intake.service import IntakeItem, IntakeService


class IntakeEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source: str
    operator_id: str | None = None
    chat_id: str | None = None
    item: IntakeItem
    raw_update: dict
    status: str = "pending"


class TelegramIntakeService:
    def __init__(self, intake_service: IntakeService | None = None) -> None:
        self.intake_service = intake_service or IntakeService()

    def from_update(self, update: dict) -> IntakeEvent:
        message = update.get("message") or update.get("edited_message") or {}
        item = self._message_to_intake(message)
        return IntakeEvent(
            source="telegram",
            operator_id=_string_id(message.get("from", {}).get("id")),
            chat_id=_string_id(message.get("chat", {}).get("id")),
            item=item,
            raw_update=update,
        )

    def _message_to_intake(self, message: dict) -> IntakeItem:
        if text := message.get("text"):
            return self.intake_service.from_text(text)
        if document := message.get("document"):
            file_id = document["file_id"]
            item = self.intake_service.from_file(
                file_name=document.get("file_name") or file_id,
                content_type=document.get("mime_type") or "application/octet-stream",
                storage_path=f"telegram://{file_id}",
            )
            item.payload["telegram_file_id"] = file_id
            if caption := message.get("caption"):
                item.payload["caption"] = caption
            return item
        if photos := message.get("photo"):
            photo = max(photos, key=lambda item: item.get("width", 0) * item.get("height", 0))
            file_id = photo["file_id"]
            item = self.intake_service.from_file(
                file_name=f"{file_id}.jpg",
                content_type="image/jpeg",
                storage_path=f"telegram://{file_id}",
            )
            item.payload["telegram_file_id"] = file_id
            if caption := message.get("caption"):
                item.payload["caption"] = caption
            return item
        if caption := message.get("caption"):
            return self.intake_service.from_text(caption)
        return IntakeItem(kind="text", payload={"text": ""})


def _string_id(value: object) -> str | None:
    return None if value is None else str(value)
