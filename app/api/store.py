from __future__ import annotations

from uuid import UUID

from app.domain.product_candidate import ProductCandidate

PRODUCTS: dict[UUID, ProductCandidate] = {}
REVIEWS: list[dict] = []
INTAKE_EVENTS: list[dict] = []
