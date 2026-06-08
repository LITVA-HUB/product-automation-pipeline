from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.moysklad.ru/api/remap/1.2"


class MoySkladRestClient:
    def __init__(self, token: str, base_url: str = BASE_URL) -> None:
        self.token = token
        self.base_url = base_url.rstrip("/")

    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
        }

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        async with httpx.AsyncClient(headers=self.headers()) as client:
            response = await client.get(f"{self.base_url}/{path.lstrip('/')}", params=params)
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, payload: dict) -> dict:
        async with httpx.AsyncClient(headers=self.headers()) as client:
            response = await client.post(f"{self.base_url}/{path.lstrip('/')}", json=payload)
            response.raise_for_status()
            return response.json()
