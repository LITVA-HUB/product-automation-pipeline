from __future__ import annotations

from app.domain.extraction import ExtractionResult
from app.domain.product_candidate import FieldWithConfidence, ProductCandidate


class ExtractionService:
    def __init__(self, confidence_threshold: float = 0.75) -> None:
        self.confidence_threshold = confidence_threshold

    def apply_result(
        self,
        candidate: ProductCandidate,
        result: ExtractionResult,
        prompt_version: str | None = None,
    ) -> ProductCandidate:
        for field_name, field_value in result.fields.items():
            current = getattr(candidate, field_name, None)
            if isinstance(current, FieldWithConfidence):
                setattr(candidate, field_name, field_value)
                if field_value.confidence < self.confidence_threshold:
                    self._mark_review(candidate, "low_confidence")

        if result.needs_human_review:
            self._mark_review(candidate, "llm_requested_review")
        candidate.warnings.extend(result.warnings)
        candidate.llm_prompt_version = prompt_version
        return candidate

    def _mark_review(self, candidate: ProductCandidate, reason: str) -> None:
        candidate.human_review_required = True
        if reason not in candidate.review_reasons:
            candidate.review_reasons.append(reason)
