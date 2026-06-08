from __future__ import annotations

from uuid import UUID

from app.adapters.repositories.product_repository import ProductRepository
from app.domain.product_candidate import ProductCandidate
from app.workflow.engine import WorkflowEngine
from app.workflow.states import WorkflowEvent, WorkflowStatus


class PipelineOrchestrator:
    def __init__(
        self,
        product_repository: ProductRepository,
        workflow_engine: WorkflowEngine | None = None,
    ) -> None:
        self.product_repository = product_repository
        self.workflow_engine = workflow_engine or WorkflowEngine()

    def apply_event(
        self,
        product_id: UUID,
        event: WorkflowEvent,
        actor: str,
        details: dict | None = None,
    ) -> ProductCandidate:
        candidate = self._require_product(product_id)
        from_status = candidate.status
        to_status = self.workflow_engine.next_status(from_status, event)
        candidate.status = to_status
        self.product_repository.save(candidate)
        self.product_repository.add_audit_log(
            product_id=candidate.id,
            actor=actor,
            action=event.value,
            from_status=from_status.value,
            to_status=to_status.value,
            details=details or {},
        )
        return candidate

    def apply_event_if_current(
        self,
        product_id: UUID,
        expected_status: WorkflowStatus,
        event: WorkflowEvent,
        actor: str,
        details: dict | None = None,
    ) -> ProductCandidate:
        candidate = self._require_product(product_id)
        if candidate.status != expected_status:
            return candidate
        return self.apply_event(product_id, event, actor, details)

    def _require_product(self, product_id: UUID) -> ProductCandidate:
        candidate = self.product_repository.get(product_id)
        if candidate is None:
            raise ValueError(f"Product {product_id} not found")
        return candidate
