from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.adapters.repositories.models import Base
from app.adapters.repositories.product_repository import ProductRepository
from app.tasks.pipeline_tasks import advance_if_current
from app.workflow.states import WorkflowStatus
from tests.unit.helpers import make_candidate


def test_advance_if_current_task_uses_orchestrator_idempotently():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False, future=True)
    candidate = make_candidate(status=WorkflowStatus.IMPORTED)

    with Session() as session:
        ProductRepository(session).save(candidate)
        session.commit()

    result = advance_if_current.run(
        product_id=str(candidate.id),
        expected_status="imported",
        event="parse_ok",
        actor="ingestion",
        session_factory=Session,
    )

    with Session() as session:
        loaded = ProductRepository(session).get(candidate.id)

    assert result["status"] == "parsed"
    assert loaded.status == WorkflowStatus.PARSED
