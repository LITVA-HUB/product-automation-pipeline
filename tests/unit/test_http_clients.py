from app.adapters.bitrix.rest_client import BitrixRestClient
from app.adapters.moysklad.client import MoySkladRestClient


def test_moysklad_client_builds_bearer_headers():
    client = MoySkladRestClient(token="secret")

    headers = client.headers()

    assert headers["Authorization"] == "Bearer secret"
    assert headers["Content-Type"] == "application/json"


def test_bitrix_client_builds_method_url_from_webhook():
    client = BitrixRestClient(webhook_url="https://example.bitrix24.ru/rest/1/token/")

    assert (
        client.method_url("catalog.product.list")
        == "https://example.bitrix24.ru/rest/1/token/catalog.product.list"
    )
