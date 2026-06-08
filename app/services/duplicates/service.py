from __future__ import annotations

from dataclasses import dataclass

from app.domain.product_candidate import ProductCandidate


@dataclass(frozen=True)
class DuplicateDecision:
    result: str
    matches: list[ProductCandidate]


class DuplicateDetectionService:
    def __init__(self, existing_candidates: list[ProductCandidate] | None = None) -> None:
        self.existing_candidates = existing_candidates or []

    def check(self, candidate: ProductCandidate) -> DuplicateDecision:
        hard_matches = [
            existing
            for existing in self.existing_candidates
            if _same_present(existing.article.value, candidate.article.value)
            or _same_present(existing.supplier_code.value, candidate.supplier_code.value)
        ]
        if hard_matches:
            return DuplicateDecision(result="duplicate", matches=hard_matches)

        soft_matches = [
            existing for existing in self.existing_candidates if _soft_match(existing, candidate)
        ]
        if soft_matches:
            candidate.human_review_required = True
            if "possible_duplicate" not in candidate.review_reasons:
                candidate.review_reasons.append("possible_duplicate")
            return DuplicateDecision(result="possible_duplicate", matches=soft_matches)

        return DuplicateDecision(result="unique", matches=[])


def _same_present(left: object, right: object) -> bool:
    return left is not None and right is not None and str(left).strip() == str(right).strip()


def _soft_match(left: ProductCandidate, right: ProductCandidate) -> bool:
    checks = [
        _same_present(left.site_manufacturer.value, right.site_manufacturer.value),
        _same_present(left.site_collection.value, right.site_collection.value),
        _same_present(left.width_mm.value, right.width_mm.value),
        _same_present(left.height_mm.value, right.height_mm.value),
        _same_present(left.color.value, right.color.value),
        _same_present(left.surface.value, right.surface.value),
    ]
    return sum(checks) >= 5
