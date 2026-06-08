from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.store import PRODUCTS, REVIEWS
from app.workflow.states import WorkflowStatus

router = APIRouter(prefix="/review", tags=["review"])


class ReviewDecisionRequest(BaseModel):
    decision: str
    operator: str = "operator"
    corrections: dict = Field(default_factory=dict)
    before: dict = Field(default_factory=dict)
    after: dict = Field(default_factory=dict)


@router.post("/{product_id}/decision")
async def apply_review_decision(product_id: UUID, request: ReviewDecisionRequest) -> dict:
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if request.decision == "approve":
        product.status = WorkflowStatus.APPROVED
        product.human_review_required = False
        PRODUCTS[product.id] = product
        review = _record_review(product_id, request)
        return {"id": str(product.id), "status": product.status.value, "review": review}
    if request.decision == "reject":
        product.status = WorkflowStatus.REJECTED
        PRODUCTS[product.id] = product
        review = _record_review(product_id, request)
        return {"id": str(product.id), "status": product.status.value, "review": review}
    raise HTTPException(status_code=400, detail="Unsupported review decision")


def _record_review(product_id: UUID, request: ReviewDecisionRequest) -> dict:
    review = {
        "product_id": str(product_id),
        "operator": request.operator,
        "decision": request.decision,
        "corrections": request.corrections,
        "before": request.before,
        "after": request.after,
    }
    REVIEWS.append(review)
    return review
