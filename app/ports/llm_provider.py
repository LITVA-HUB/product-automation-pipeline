from __future__ import annotations

from typing import Any, Protocol


class LLMProvider(Protocol):
    def build_chat_payload(
        self,
        system_prompt: str,
        user_content: str | list[dict[str, Any]],
        schema_name: str,
        temperature: float = 0.0,
    ) -> dict[str, Any]: ...
