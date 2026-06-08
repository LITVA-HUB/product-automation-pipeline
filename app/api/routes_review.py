from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.repositories.product_repository import ProductRepository
from app.adapters.repositories.review_repository import HumanReviewRepository
from app.api.dependencies import get_db_session
from app.workflow.states import WorkflowStatus

router = APIRouter(prefix="/review", tags=["review"])


class ReviewDecisionRequest(BaseModel):
    decision: str
    operator: str = "operator"
    corrections: dict = Field(default_factory=dict)
    before: dict = Field(default_factory=dict)
    after: dict = Field(default_factory=dict)


@router.post("/{product_id}/decision")
async def apply_review_decision(
    product_id: UUID,
    request: ReviewDecisionRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> dict:
    product_repository = ProductRepository(session)
    product = product_repository.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if request.decision == "approve":
        product.status = WorkflowStatus.APPROVED
        product.human_review_required = False
        product_repository.save(product)
        review = _record_review(session, product_id, request)
        return {"id": str(product.id), "status": product.status.value, "review": review}
    if request.decision == "reject":
        product.status = WorkflowStatus.REJECTED
        product_repository.save(product)
        review = _record_review(session, product_id, request)
        return {"id": str(product.id), "status": product.status.value, "review": review}
    raise HTTPException(status_code=400, detail="Unsupported review decision")


def _record_review(session: Session, product_id: UUID, request: ReviewDecisionRequest) -> dict:
    row = HumanReviewRepository(session).record(
        product_id=product_id,
        operator=request.operator,
        decision=request.decision,
        corrections=request.corrections,
        before=request.before,
        after=request.after,
    )
    return {
        "id": row.id,
        "product_id": str(product_id),
        "operator": request.operator,
        "decision": request.decision,
        "corrections": request.corrections,
        "before": request.before,
        "after": request.after,
    }
