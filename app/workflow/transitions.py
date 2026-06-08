from __future__ import annotations

from app.workflow.states import WorkflowEvent, WorkflowStatus

TRANSITIONS: dict[tuple[WorkflowStatus, WorkflowEvent], WorkflowStatus] = {
    (WorkflowStatus.IMPORTED, WorkflowEvent.PARSE_OK): WorkflowStatus.PARSED,
    (WorkflowStatus.IMPORTED, WorkflowEvent.PARSE_FAIL): WorkflowStatus.MISSING_DATA,
    (WorkflowStatus.PARSED, WorkflowEvent.EXTRACT_OK): WorkflowStatus.LLM_EXTRACTED,
    (WorkflowStatus.LLM_EXTRACTED, WorkflowEvent.LOW_CONFIDENCE): WorkflowStatus.LLM_LOW_CONFIDENCE,
    (WorkflowStatus.LLM_EXTRACTED, WorkflowEvent.EXTRACT_CONFIDENT): WorkflowStatus.NORMALIZED,
    (WorkflowStatus.NORMALIZED, WorkflowEvent.NAMED_OK): WorkflowStatus.NAMED,
    (WorkflowStatus.NAMED, WorkflowEvent.PRICED_OK): WorkflowStatus.PRICED,
    (WorkflowStatus.PRICED, WorkflowEvent.NO_DUPLICATE): WorkflowStatus.DUPLICATE_CHECKED,
    (WorkflowStatus.PRICED, WorkflowEvent.HARD_OR_SOFT_MATCH): WorkflowStatus.POSSIBLE_DUPLICATE,
    (WorkflowStatus.DUPLICATE_CHECKED, WorkflowEvent.VALID): WorkflowStatus.VALIDATED_BEFORE_MS,
    (WorkflowStatus.DUPLICATE_CHECKED, WorkflowEvent.INVALID): WorkflowStatus.VALIDATION_FAILED,
    (WorkflowStatus.VALIDATED_BEFORE_MS, WorkflowEvent.MS_OK): WorkflowStatus.CREATED_IN_MS,
    (WorkflowStatus.VALIDATED_BEFORE_MS, WorkflowEvent.MS_ERROR): WorkflowStatus.MS_CREATION_FAILED,
    (WorkflowStatus.CREATED_IN_MS, WorkflowEvent.VERIFY_OK): WorkflowStatus.MS_VERIFIED,
    (WorkflowStatus.MS_VERIFIED, WorkflowEvent.SITE_OK): WorkflowStatus.CREATED_ON_SITE,
    (WorkflowStatus.MS_VERIFIED, WorkflowEvent.SITE_ERROR): WorkflowStatus.SITE_CREATION_FAILED,
    (WorkflowStatus.CREATED_ON_SITE, WorkflowEvent.VERIFY_OK): WorkflowStatus.SITE_VERIFIED,
    (WorkflowStatus.SITE_VERIFIED, WorkflowEvent.NEEDS_REVIEW): WorkflowStatus.READY_FOR_REVIEW,
    (WorkflowStatus.SITE_VERIFIED, WorkflowEvent.AUTO_OK): WorkflowStatus.APPROVED,
    (WorkflowStatus.READY_FOR_REVIEW, WorkflowEvent.OPERATOR_APPROVE): WorkflowStatus.APPROVED,
    (WorkflowStatus.READY_FOR_REVIEW, WorkflowEvent.OPERATOR_REJECT): WorkflowStatus.REJECTED,
    (WorkflowStatus.APPROVED, WorkflowEvent.PUBLISH_OK): WorkflowStatus.PUBLISHED,
    (WorkflowStatus.POSSIBLE_DUPLICATE, WorkflowEvent.OPERATOR_CREATE_NEW): WorkflowStatus.DUPLICATE_CHECKED,
}
