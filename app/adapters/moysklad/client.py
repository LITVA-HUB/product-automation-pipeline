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

    async def put(self, path: str, payload: dict) -> dict:
        async with httpx.AsyncClient(headers=self.headers()) as client:
            response = await client.put(f"{self.base_url}/{path.lstrip('/')}", json=payload)
            response.raise_for_status()
            return response.json()

    async def find_product_by_article(self, article: str) -> dict | None:
        return _first_row(await self.get("entity/product", {"filter": f"article={article}"}))

    async def find_product_by_supplier_code(self, code: str) -> dict | None:
        return _first_row(await self.get("entity/product", {"filter": f"code={code}"}))

    async def search_products(self, query: str) -> list[dict]:
        response = await self.get("entity/product", {"search": query})
        return response.get("rows", [])

    async def create_product(self, payload: dict) -> dict:
        return await self.post("entity/product", payload)

    async def update_product(self, ms_id: str, payload: dict) -> dict:
        return await self.put(f"entity/product/{ms_id}", payload)

    async def upload_image(self, ms_id: str, image_path: str) -> dict:
        return await self.post(
            f"entity/product/{ms_id}/images",
            {"filename": image_path.rsplit("/", 1)[-1], "path": image_path},
        )

    async def get_or_create_folder(self, name: str) -> dict:
        existing = _first_row(await self.get("entity/productfolder", {"filter": f"name={name}"}))
        if existing:
            return existing
        return await self.post("entity/productfolder", {"name": name})

    async def get_uom(self, name: str) -> dict | None:
        return _first_row(await self.get("entity/uom", {"filter": f"name={name}"}))

    async def find_counterparty(self, name: str) -> dict | None:
        return _first_row(await self.get("entity/counterparty", {"filter": f"name={name}"}))

    async def set_published_flag(self, ms_id: str, value: bool) -> dict:
        return await self.update_product(ms_id, {"attributes": [{"name": "Выгружено на сайте", "value": value}]})


def _first_row(response: dict) -> dict | None:
    rows = response.get("rows", [])
    return rows[0] if rows else None
