from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.store import PRODUCTS
from app.workflow.states import WorkflowStatus

router = APIRouter(prefix="/review", tags=["review"])


class ReviewDecisionRequest(BaseModel):
    decision: str


@router.post("/{product_id}/decision")
async def apply_review_decision(product_id: UUID, request: ReviewDecisionRequest) -> dict[str, str]:
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if request.decision == "approve":
        product.status = WorkflowStatus.APPROVED
        product.human_review_required = False
        PRODUCTS[product.id] = product
        return {"id": str(product.id), "status": product.status.value}
    if request.decision == "reject":
        product.status = WorkflowStatus.REJECTED
        PRODUCTS[product.id] = product
        return {"id": str(product.id), "status": product.status.value}
    raise HTTPException(status_code=400, detail="Unsupported review decision")
