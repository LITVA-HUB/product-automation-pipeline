from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.adapters.repositories.models import HumanReviewRow


class HumanReviewRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record(
        self,
        product_id: UUID,
        operator: str,
        decision: str,
        corrections: dict,
        before: dict,
        after: dict,
    ) -> HumanReviewRow:
        row = HumanReviewRow(
            product_id=str(product_id),
            operator=operator,
            decision=decision,
            corrections=corrections,
            before=before,
            after=after,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def list_for_product(self, product_id: UUID) -> list[HumanReviewRow]:
        return (
            self.session.query(HumanReviewRow)
            .filter(HumanReviewRow.product_id == str(product_id))
            .order_by(HumanReviewRow.created_at.asc(), HumanReviewRow.id.asc())
            .all()
        )
