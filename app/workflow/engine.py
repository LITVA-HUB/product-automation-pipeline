from __future__ import annotations

from app.workflow.states import WorkflowEvent, WorkflowStatus
from app.workflow.transitions import TRANSITIONS


class WorkflowEngine:
    def next_status(self, status: WorkflowStatus, event: WorkflowEvent) -> WorkflowStatus:
        try:
            return TRANSITIONS[(status, event)]
        except KeyError as exc:
            raise ValueError(f"Invalid workflow transition: {status} + {event}") from exc
