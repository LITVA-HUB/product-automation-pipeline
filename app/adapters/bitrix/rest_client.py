from __future__ import annotations

from decimal import Decimal
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

    async def find_product_by_ms_code(self, ms_code: str) -> dict | None:
        response = await self.call(
            "catalog.product.list",
            {"filter": {"xmlId": ms_code}, "select": ["id", "iblockId", "xmlId", "name"]},
        )
        products = response.get("result", {}).get("products", [])
        return products[0] if products else None

    async def create_or_update_product(self, payload: dict) -> dict:
        if payload.get("id"):
            response = await self.call("catalog.product.update", {"id": payload["id"], "fields": payload})
            return response.get("result", {})
        response = await self.call("catalog.product.add", {"fields": payload})
        return response.get("result", {}).get("product", response.get("result", {}))

    async def set_properties(self, site_id: str, properties: dict) -> None:
        await self.call("catalog.product.update", {"id": site_id, "fields": {"propertyValues": properties}})

    async def upload_images(
        self,
        site_id: str,
        extra: list[str],
        announce: list[str],
        detail: list[str],
    ) -> None:
        await self.call(
            "catalog.product.update",
            {
                "id": site_id,
                "fields": {"extraImages": extra, "announceImages": announce, "detailImages": detail},
            },
        )

    async def set_catalog_price(self, site_id: str, price: Decimal) -> None:
        await self.call("catalog.product.update", {"id": site_id, "fields": {"price": str(price)}})

    async def set_unit_coefficient(self, site_id: str, coef: Decimal) -> None:
        await self.call(
            "catalog.product.update",
            {"id": site_id, "fields": {"unitCoefficient": str(coef)}},
        )

    async def disable_quantity_accounting(self, site_id: str) -> None:
        await self.call("catalog.product.update", {"id": site_id, "fields": {"quantityTrace": "N"}})

    async def set_card_type(self, site_id: str, value: str = "Ламинат") -> None:
        await self.call("catalog.product.update", {"id": site_id, "fields": {"cardType": value}})

    async def set_supplier_name(self, site_id: str, supplier: str) -> None:
        await self.call("catalog.product.update", {"id": site_id, "fields": {"supplierName": supplier}})

    async def publish(self, site_id: str) -> None:
        await self.call("catalog.product.update", {"id": site_id, "fields": {"active": "Y"}})
