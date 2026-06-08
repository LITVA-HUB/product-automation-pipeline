from app.domain.product_candidate import FieldWithConfidence
from app.services.duplicates.service import DuplicateDecision, DuplicateDetectionService
from tests.unit.helpers import make_candidate


def test_duplicate_detection_returns_duplicate_for_exact_article_match():
    existing = [make_candidate()]
    service = DuplicateDetectionService(existing_candidates=existing)

    decision = service.check(make_candidate())

    assert decision.result == "duplicate"
    assert decision.matches[0].article.value == "ART-001"


def test_duplicate_detection_returns_possible_duplicate_for_soft_match():
    existing = [
        make_candidate(
            article=FieldWithConfidence(value="OTHER", confidence=1, source="test"),
            supplier_code=FieldWithConfidence(value="OTHER-CODE", confidence=1, source="test"),
        )
    ]
    service = DuplicateDetectionService(existing_candidates=existing)

    decision = service.check(make_candidate(article=FieldWithConfidence(value="NEW", confidence=1)))

    assert decision.result == "possible_duplicate"
    assert decision.matches


def test_duplicate_detection_marks_candidate_for_review_on_possible_duplicate():
    existing = [
        make_candidate(
            article=FieldWithConfidence(value="OTHER", confidence=1, source="test"),
            supplier_code=FieldWithConfidence(value="OTHER-CODE", confidence=1, source="test"),
        )
    ]
    candidate = make_candidate(article=FieldWithConfidence(value="NEW", confidence=1))
    service = DuplicateDetectionService(existing_candidates=existing)

    decision = service.check(candidate)

    assert isinstance(decision, DuplicateDecision)
    assert candidate.human_review_required is True
    assert "possible_duplicate" in candidate.review_reasons
