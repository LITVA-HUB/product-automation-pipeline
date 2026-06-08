from __future__ import annotations

from app.domain.product_candidate import ProductCandidate
from app.workflow.states import WorkflowStatus


class PublicationService:
    def __init__(self, ms_client, site_client=None) -> None:
        self.ms_client = ms_client
        self.site_client = site_client

    async def publish(self, candidate: ProductCandidate) -> ProductCandidate:
        if candidate.status != WorkflowStatus.APPROVED:
            raise ValueError("Product must be approved before publication")
        if not candidate.ms_product_id:
            raise ValueError("ms_product_id is required before publication")

        await self.ms_client.set_published_flag(candidate.ms_product_id, True)
        if self.site_client is not None and candidate.site_product_id:
            await self.site_client.publish(candidate.site_product_id)
        candidate.status = WorkflowStatus.PUBLISHED
        return candidate
