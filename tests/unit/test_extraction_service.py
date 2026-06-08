from app.domain.extraction import ExtractionResult
from app.domain.product_candidate import FieldWithConfidence
from app.services.extraction.service import ExtractionService
from tests.unit.helpers import make_candidate


def test_extraction_service_applies_only_supported_confidence_fields():
    candidate = make_candidate(article=FieldWithConfidence(value=None, confidence=0))
    result = ExtractionResult(
        fields={
            "article": FieldWithConfidence(value="A-100", confidence=0.9, source="raw"),
            "retail_price": FieldWithConfidence(value="999999", confidence=1, source="llm"),
        },
        needs_human_review=False,
    )

    updated = ExtractionService().apply_result(candidate, result, prompt_version="extract_v1")

    assert updated.article.value == "A-100"
    assert updated.retail_price == candidate.retail_price
    assert updated.llm_prompt_version == "extract_v1"


def test_extraction_service_marks_low_confidence_for_review():
    candidate = make_candidate()
    result = ExtractionResult(
        fields={"article": FieldWithConfidence(value="A-100", confidence=0.4, source="raw")},
        needs_human_review=False,
    )

    updated = ExtractionService(confidence_threshold=0.75).apply_result(candidate, result)

    assert updated.human_review_required is True
    assert "low_confidence" in updated.review_reasons
