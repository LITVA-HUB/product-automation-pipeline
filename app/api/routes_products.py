from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.store import PRODUCTS
from app.domain.product_candidate import ProductCandidate

router = APIRouter(prefix="/products", tags=["products"])


class ManualProductRequest(BaseModel):
    supplier: str
    raw_name: str | None = None
    raw_article: str | None = None
    raw_price: str | None = None
    raw_description: str | None = None
    source_url: str | None = None


@router.post("/manual", response_model=ProductCandidate, status_code=status.HTTP_201_CREATED)
async def create_manual_product(request: ManualProductRequest) -> ProductCandidate:
    candidate = ProductCandidate(
        supplier=request.supplier,
        source_type="manual",
        source_url=request.source_url,
        raw_name=request.raw_name,
        raw_article=request.raw_article,
        raw_price=request.raw_price,
        raw_description=request.raw_description,
    )
    PRODUCTS[candidate.id] = candidate
    return candidate


@router.get("/{product_id}", response_model=ProductCandidate)
async def get_product(product_id: UUID) -> ProductCandidate:
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
