from __future__ import annotations

from uuid import UUID

from app.adapters.repositories.product_repository import ProductRepository
from app.db import make_session_factory
from app.services.pipeline.orchestrator import PipelineOrchestrator
from app.tasks.celery_app import celery_app
from app.workflow.states import WorkflowEvent, WorkflowStatus


@celery_app.task(name="app.tasks.pipeline_tasks.healthcheck")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@celery_app.task(name="app.tasks.pipeline_tasks.advance_if_current")
def advance_if_current(
    product_id: str,
    expected_status: str,
    event: str,
    actor: str,
    database_url: str | None = None,
    session_factory=None,
) -> dict[str, str]:
    factory = session_factory or make_session_factory(_require_database_url(database_url))
    with factory() as session:
        repo = ProductRepository(session)
        orchestrator = PipelineOrchestrator(repo)
        candidate = orchestrator.apply_event_if_current(
            product_id=UUID(product_id),
            expected_status=WorkflowStatus(expected_status),
            event=WorkflowEvent(event),
            actor=actor,
        )
        session.commit()
        return {"id": str(candidate.id), "status": candidate.status.value}


def _require_database_url(database_url: str | None) -> str:
    if database_url:
        return database_url
    import os

    value = os.environ.get("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required for pipeline task execution")
    return value
