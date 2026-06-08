import pytest

from app.workflow.engine import WorkflowEngine
from app.workflow.states import WorkflowEvent, WorkflowStatus


def test_workflow_allows_documented_happy_path_transition():
    engine = WorkflowEngine()

    result = engine.next_status(WorkflowStatus.IMPORTED, WorkflowEvent.PARSE_OK)

    assert result == WorkflowStatus.PARSED


def test_workflow_rejects_undocumented_transition():
    engine = WorkflowEngine()

    with pytest.raises(ValueError, match="Invalid workflow transition"):
        engine.next_status(WorkflowStatus.IMPORTED, WorkflowEvent.MS_OK)


def test_workflow_routes_possible_duplicates_to_human_review():
    engine = WorkflowEngine()

    result = engine.next_status(WorkflowStatus.PRICED, WorkflowEvent.HARD_OR_SOFT_MATCH)

    assert result == WorkflowStatus.POSSIBLE_DUPLICATE
