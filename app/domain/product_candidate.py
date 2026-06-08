from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.workflow.states import WorkflowStatus


class FieldWithConfidence(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    value: Any | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str | None = None
    warning: str | None = None


class ValidationErrorItem(BaseModel):
    scope: str
    field: str
    message: str


class ProductCandidate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    supplier: str
    source_type: str
    source_url: str | None = None

    raw_name: str | None = None
    raw_article: str | None = None
    raw_price: str | None = None
    raw_description: str | None = None
    raw_fields: dict[str, Any] = Field(default_factory=dict)
    raw_images: list[str] = Field(default_factory=list)

    product_type: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    article: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    supplier_code: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    unit: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    units_per_package: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    width_mm: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    height_mm: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    thickness_mm: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    color: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    surface: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    texture: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    country: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    manufacturer: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    brand_collection: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    site_manufacturer: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    site_collection: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    faces_count: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    weight_kg: FieldWithConfidence = Field(default_factory=FieldWithConfidence)
    package_weight_kg: FieldWithConfidence = Field(default_factory=FieldWithConfidence)

    generated_name: str | None = None
    original_name: str | None = None
    package_type: str = "УПК"
    retail_price: Decimal | None = None
    purchase_price: Decimal | None = None
    site_price: Decimal | None = None
    unit_coefficient: Decimal | None = None
    site_card_type: str = "Ламинат"

    main_image: str | None = None
    face_images: list[str] = Field(default_factory=list)
    interior_images: list[str] = Field(default_factory=list)

    mapping_fields: dict[str, Any] = Field(default_factory=dict)
    group_ms: str | None = None

    ms_product_id: str | None = None
    ms_product_code: str | None = None
    site_product_id: str | None = None

    status: WorkflowStatus = WorkflowStatus.IMPORTED
    human_review_required: bool = False
    review_reasons: list[str] = Field(default_factory=list)
    validation_errors: list[ValidationErrorItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    llm_prompt_version: str | None = None
    normalization_rules_version: str | None = None
    mapping_rules_version: str | None = None
    validator_version: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
