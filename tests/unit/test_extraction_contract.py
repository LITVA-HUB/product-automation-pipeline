import json

import pytest

from app.adapters.llm.openrouter import OpenRouterLLMProvider
from app.domain.extraction import ExtractionResult


def test_extraction_result_validates_field_with_confidence_payload():
    payload = {
        "fields": {
            "article": {"value": "A-1", "confidence": 0.92, "source": "raw_article"},
            "color": {"value": "серый", "confidence": 0.8, "source": "description"},
        },
        "needs_human_review": False,
        "warnings": [],
    }

    result = ExtractionResult.model_validate(payload)

    assert result.fields["article"].value == "A-1"
    assert result.needs_human_review is False


def test_openrouter_provider_parses_valid_json_content_into_schema():
    provider = OpenRouterLLMProvider(api_key="test-key")
    content = json.dumps(
        {
            "fields": {"article": {"value": "A-1", "confidence": 1, "source": "test"}},
            "needs_human_review": False,
            "warnings": [],
        }
    )

    result = provider.parse_extraction_content(content)

    assert result.fields["article"].value == "A-1"


def test_openrouter_provider_rejects_invalid_json_content():
    provider = OpenRouterLLMProvider(api_key="test-key")

    with pytest.raises(ValueError, match="valid JSON"):
        provider.parse_extraction_content("not-json")
