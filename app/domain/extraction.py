from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.product_candidate import FieldWithConfidence


class ExtractionResult(BaseModel):
    fields: dict[str, FieldWithConfidence]
    needs_human_review: bool = False
    warnings: list[str] = Field(default_factory=list)


class ImageClassification(BaseModel):
    image_type: str
    confidence: float = Field(ge=0, le=1)
    warning: str | None = None
