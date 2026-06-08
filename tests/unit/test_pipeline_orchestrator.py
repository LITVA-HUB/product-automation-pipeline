from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.adapters.repositories.models import Base
from app.adapters.repositories.product_repository import ProductRepository
from app.services.pipeline.orchestrator import PipelineOrchestrator
from app.workflow.states import WorkflowEvent, WorkflowStatus
from tests.unit.helpers import make_candidate


def test_orchestrator_applies_workflow_event_and_writes_audit_log():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False, future=True)
    candidate = make_candidate(status=WorkflowStatus.IMPORTED)

    with Session() as session:
        repo = ProductRepository(session)
        repo.save(candidate)
        orchestrator = PipelineOrchestrator(repo)

        updated = orchestrator.apply_event(candidate.id, WorkflowEvent.PARSE_OK, actor="ingestion")
        session.commit()

    with Session() as session:
        repo = ProductRepository(session)
        loaded = repo.get(candidate.id)
        audit_logs = repo.list_audit_logs(candidate.id)

    assert updated.status == WorkflowStatus.PARSED
    assert loaded.status == WorkflowStatus.PARSED
    assert len(audit_logs) == 1
    assert audit_logs[0].from_status == "imported"
    assert audit_logs[0].to_status == "parsed"


def test_orchestrator_idempotently_skips_when_status_already_advanced():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False, future=True)
    candidate = make_candidate(status=WorkflowStatus.PARSED)

    with Session() as session:
        repo = ProductRepository(session)
        repo.save(candidate)
        orchestrator = PipelineOrchestrator(repo)

        updated = orchestrator.apply_event_if_current(
            candidate.id,
            expected_status=WorkflowStatus.IMPORTED,
            event=WorkflowEvent.PARSE_OK,
            actor="ingestion",
        )
        session.commit()

        audit_logs = repo.list_audit_logs(candidate.id)

    assert updated.status == WorkflowStatus.PARSED
    assert audit_logs == []
