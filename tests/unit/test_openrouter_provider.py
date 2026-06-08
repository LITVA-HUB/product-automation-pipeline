from app.adapters.llm.openrouter import (
    OPENROUTER_GEMINI_FLASH_LITE_MODEL,
    OpenRouterLLMProvider,
)


def test_openrouter_provider_uses_strict_gemini_flash_lite_model():
    assert OPENROUTER_GEMINI_FLASH_LITE_MODEL == "google/gemini-3.1-flash-lite"


def test_openrouter_payload_uses_strict_model_and_json_response_format():
    provider = OpenRouterLLMProvider(api_key="test-key")

    payload = provider.build_chat_payload(
        system_prompt="Return JSON.",
        user_content="Extract product fields.",
        schema_name="ExtractionResult",
    )

    assert payload["model"] == "google/gemini-3.1-flash-lite"
    assert payload["response_format"]["type"] == "json_object"
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"
