from decimal import Decimal

import pytest

from app.adapters.bitrix.rest_client import BitrixRestClient
from app.adapters.moysklad.client import MoySkladRestClient


class RecordingMoySkladClient(MoySkladRestClient):
    def __init__(self) -> None:
        super().__init__(token="secret")
        self.calls = []

    async def get(self, path: str, params: dict | None = None) -> dict:
        self.calls.append(("get", path, params))
        return {"rows": [{"id": "p1"}]}

    async def post(self, path: str, payload: dict) -> dict:
        self.calls.append(("post", path, payload))
        return {"id": "created"}

    async def put(self, path: str, payload: dict) -> dict:
        self.calls.append(("put", path, payload))
        return {"id": "updated"}


class RecordingBitrixClient(BitrixRestClient):
    def __init__(self) -> None:
        super().__init__("https://example.bitrix24.ru/rest/1/token")
        self.calls = []

    async def call(self, method: str, payload: dict) -> dict:
        self.calls.append((method, payload))
        if method == "catalog.product.list":
            return {"result": {"products": [{"id": 10}]}}
        if method == "catalog.product.add":
            return {"result": {"product": {"id": 11}}}
        return {"result": True}


@pytest.mark.asyncio
async def test_moysklad_rest_client_port_methods_use_expected_endpoints():
    client = RecordingMoySkladClient()

    found = await client.find_product_by_article("A-1")
    created = await client.create_product({"name": "Tile"})
    updated = await client.update_product("p1", {"name": "Tile 2"})
    image = await client.upload_image("p1", "/tmp/main.jpg")

    assert found == {"id": "p1"}
    assert created == {"id": "created"}
    assert updated == {"id": "updated"}
    assert image == {"id": "created"}
    assert ("get", "entity/product", {"filter": "article=A-1"}) in client.calls
    assert ("post", "entity/product", {"name": "Tile"}) in client.calls
    assert ("put", "entity/product/p1", {"name": "Tile 2"}) in client.calls
    assert client.calls[-1][1] == "entity/product/p1/images"


@pytest.mark.asyncio
async def test_bitrix_rest_client_port_methods_use_catalog_calls():
    client = RecordingBitrixClient()

    found = await client.find_product_by_ms_code("MS-1")
    created = await client.create_or_update_product({"name": "Tile"})
    await client.set_catalog_price("11", Decimal("1150.00"))
    await client.set_unit_coefficient("11", Decimal("1.44"))
    await client.disable_quantity_accounting("11")
    await client.set_card_type("11", "Ламинат")
    await client.set_supplier_name("11", "Supplier")

    assert found == {"id": 10}
    assert created == {"id": 11}
    methods = [method for method, _ in client.calls]
    assert "catalog.product.list" in methods
    assert "catalog.product.add" in methods
    assert methods.count("catalog.product.update") >= 5
