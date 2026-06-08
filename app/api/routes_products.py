from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.adapters.repositories.product_repository import ProductRepository
from app.api.auth import require_telegram_operator
from app.api.dependencies import get_db_session, get_settings
from app.config import Settings
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
async def create_manual_product(
    request: ManualProductRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_init_data: str | None = Header(default=None),
) -> ProductCandidate:
    require_telegram_operator(settings, x_telegram_init_data)
    candidate = ProductCandidate(
        supplier=request.supplier,
        source_type="manual",
        source_url=request.source_url,
        raw_name=request.raw_name,
        raw_article=request.raw_article,
        raw_price=request.raw_price,
        raw_description=request.raw_description,
    )
    ProductRepository(session).save(candidate)
    return candidate


@router.get("/{product_id}", response_model=ProductCandidate)
async def get_product(
    product_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_telegram_init_data: str | None = Header(default=None),
) -> ProductCandidate:
    require_telegram_operator(settings, x_telegram_init_data)
    product = ProductRepository(session).get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
