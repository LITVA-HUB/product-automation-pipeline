from __future__ import annotations

import json
from typing import Any

import httpx
from pydantic import ValidationError

from app.domain.extraction import ExtractionResult

OPENROUTER_GEMINI_FLASH_LITE_MODEL = "google/gemini-3.1-flash-lite"
OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterLLMProvider:
    def __init__(
        self,
        api_key: str,
        model: str = OPENROUTER_GEMINI_FLASH_LITE_MODEL,
        app_title: str = "Product Automation Pipeline",
        site_url: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        if model != OPENROUTER_GEMINI_FLASH_LITE_MODEL:
            raise ValueError(f"Only {OPENROUTER_GEMINI_FLASH_LITE_MODEL} is allowed")
        self.api_key = api_key
        self.model = model
        self.app_title = app_title
        self.site_url = site_url
        self.http_client = http_client

    def build_headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": self.app_title,
        }
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        return headers

    def build_chat_payload(
        self,
        system_prompt: str,
        user_content: str | list[dict[str, Any]],
        schema_name: str,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        return {
            "model": self.model,
            "temperature": temperature,
            "response_format": {
                "type": "json_object",
                "schema_name": schema_name,
            },
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        }

    def parse_extraction_content(self, content: str) -> ExtractionResult:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("OpenRouter response content must be valid JSON") from exc
        try:
            return ExtractionResult.model_validate(payload)
        except ValidationError as exc:
            raise ValueError("OpenRouter response JSON does not match ExtractionResult") from exc

    async def extract_fields(
        self,
        raw: dict,
        supplier_hint: dict | None,
        system_prompt: str | None = None,
    ) -> ExtractionResult:
        payload = self.build_chat_payload(
            system_prompt=system_prompt or _default_extraction_prompt(),
            user_content=json.dumps(
                {"raw": raw, "supplier_hint": supplier_hint or {}},
                ensure_ascii=False,
                sort_keys=True,
            ),
            schema_name="ExtractionResult",
        )
        response = await self._post_chat_completion(payload)
        content = _message_content(response)
        return self.parse_extraction_content(content)

    async def _post_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.http_client is not None:
            response = await self.http_client.post(
                OPENROUTER_CHAT_COMPLETIONS_URL,
                headers=self.build_headers(),
                json=payload,
            )
        else:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    OPENROUTER_CHAT_COMPLETIONS_URL,
                    headers=self.build_headers(),
                    json=payload,
                )
        response.raise_for_status()
        return response.json()


def _message_content(response: dict[str, Any]) -> str:
    choices = response.get("choices") or []
    if not choices:
        raise ValueError("OpenRouter response must contain message content")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str) or not content:
        raise ValueError("OpenRouter response must contain message content")
    return content


def _default_extraction_prompt() -> str:
    return (
        "Extract product fields from supplier data. Return only valid JSON matching "
        "ExtractionResult: fields is an object of FieldWithConfidence values with "
        "value, confidence, source, and optional warning. Do not calculate prices, "
        "do not publish, and do not write to external systems."
    )
