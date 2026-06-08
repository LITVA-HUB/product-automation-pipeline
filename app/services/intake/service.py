from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

IntakeKind = Literal["text", "table", "image_invoice", "supplier_url", "unknown_file"]


class IntakeItem(BaseModel):
    kind: IntakeKind
    payload: dict = Field(default_factory=dict)


class IntakeService:
    def from_text(self, text: str) -> IntakeItem:
        stripped = text.strip()
        url = _first_url(stripped)
        if url:
            return IntakeItem(kind="supplier_url", payload={"url": url, "text": stripped})
        return IntakeItem(kind="text", payload={"text": stripped})

    def from_file(self, file_name: str, content_type: str, storage_path: str) -> IntakeItem:
        payload = {
            "file_name": file_name,
            "content_type": content_type,
            "storage_path": storage_path,
        }
        lower_name = file_name.lower()
        if content_type.startswith("image/"):
            return IntakeItem(kind="image_invoice", payload=payload)
        if lower_name.endswith((".csv", ".xls", ".xlsx")) or "spreadsheet" in content_type:
            return IntakeItem(kind="table", payload=payload)
        return IntakeItem(kind="unknown_file", payload=payload)


def _first_url(text: str) -> str | None:
    match = re.search(r"https?://\S+", text)
    return match.group(0).rstrip(".,)") if match else None
