from __future__ import annotations

import json
from typing import Any

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
    ) -> None:
        if model != OPENROUTER_GEMINI_FLASH_LITE_MODEL:
            raise ValueError(f"Only {OPENROUTER_GEMINI_FLASH_LITE_MODEL} is allowed")
        self.api_key = api_key
        self.model = model
        self.app_title = app_title
        self.site_url = site_url

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
