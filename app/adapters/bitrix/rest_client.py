from __future__ import annotations

from typing import Any

import httpx


class BitrixRestClient:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url.rstrip("/")

    def method_url(self, method: str) -> str:
        return f"{self.webhook_url}/{method}"

    async def call(self, method: str, payload: dict[str, Any]) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(self.method_url(method), json=payload)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise RuntimeError(f"Bitrix API error: {data['error']}")
            return data
