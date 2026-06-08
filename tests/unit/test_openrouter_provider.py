from app.adapters.llm.openrouter import (
    OPENROUTER_GEMINI_FLASH_LITE_MODEL,
    OpenRouterLLMProvider,
)

import httpx
import pytest


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


@pytest.mark.asyncio
async def test_openrouter_extract_fields_posts_to_chat_completion_endpoint():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["authorization"] = request.headers["Authorization"]
        seen["payload"] = request.read().decode("utf-8")
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"fields":{"article":{"value":"A-1","confidence":1,'
                                '"source":"raw"}},"needs_human_review":false,"warnings":[]}'
                            )
                        }
                    }
                ]
            },
        )

    provider = OpenRouterLLMProvider(
        api_key="test-key",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    result = await provider.extract_fields(
        raw={"raw_name": "Tile", "raw_article": "A-1"},
        supplier_hint={"supplier": "Kerama"},
    )

    assert seen["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert seen["authorization"] == "Bearer test-key"
    assert '"model":"google/gemini-3.1-flash-lite"' in seen["payload"]
    assert result.fields["article"].value == "A-1"


@pytest.mark.asyncio
async def test_openrouter_extract_fields_raises_on_missing_choice_content():
    provider = OpenRouterLLMProvider(
        api_key="test-key",
        http_client=httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"choices": []}))
        ),
    )

    with pytest.raises(ValueError, match="message content"):
        await provider.extract_fields(raw={"raw_name": "Tile"}, supplier_hint=None)
