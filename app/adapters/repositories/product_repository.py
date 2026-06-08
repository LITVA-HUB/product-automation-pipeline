from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.adapters.repositories.models import ProductRow
from app.domain.product_candidate import ProductCandidate


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, candidate: ProductCandidate) -> None:
        payload = candidate.model_dump(mode="json")
        row = self.get_row(candidate.id)
        values = {
            "supplier": candidate.supplier,
            "source_type": candidate.source_type,
            "source_url": candidate.source_url,
            "status": candidate.status.value,
            "human_review_required": candidate.human_review_required,
            "review_reasons": candidate.review_reasons,
            "candidate": payload,
            "article": candidate.article.value,
            "supplier_code": candidate.supplier_code.value,
            "ms_product_id": candidate.ms_product_id,
            "ms_product_code": candidate.ms_product_code,
            "site_product_id": candidate.site_product_id,
        }
        if row is None:
            self.session.add(ProductRow(id=str(candidate.id), **values))
            return
        for key, value in values.items():
            setattr(row, key, value)

    def get(self, product_id: UUID) -> ProductCandidate | None:
        row = self.get_row(product_id)
        if row is None:
            return None
        return ProductCandidate.model_validate(row.candidate)

    def get_row(self, product_id: UUID) -> ProductRow | None:
        return self.session.get(ProductRow, str(product_id))
