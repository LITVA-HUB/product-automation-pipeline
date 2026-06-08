from decimal import Decimal

from app.adapters.bitrix.mappers import candidate_to_bitrix_payload
from app.adapters.moysklad.mappers import candidate_to_ms_product
from tests.unit.helpers import make_candidate


def test_candidate_to_ms_product_maps_prices_to_minor_units_and_attributes():
    candidate = make_candidate(retail_price=Decimal("1000.00"), purchase_price=Decimal("800.00"))
    maps = {
        "uom": {"м²": {"meta": {"href": "https://api/uom/1", "type": "uom"}}},
        "folder": {"Atlas": {"meta": {"href": "https://api/folder/1", "type": "productfolder"}}},
        "supplier": {
            "Test Supplier": {"meta": {"href": "https://api/counterparty/1", "type": "counterparty"}}
        },
        "price_types": {
            "retail": {"meta": {"href": "https://api/pricetype/retail"}},
            "purchase": {"meta": {"href": "https://api/pricetype/purchase"}},
        },
        "attributes": {
            "Код поставщика": {"meta": {"href": "https://api/attr/code"}},
            "Тип карточки": {"meta": {"href": "https://api/attr/card"}},
        },
    }

    payload = candidate_to_ms_product(candidate, maps)

    assert payload["name"] == candidate.generated_name
    assert payload["article"] == "ART-001"
    assert payload["uom"]["meta"]["type"] == "uom"
    assert payload["salePrices"][0]["value"] == 100000
    assert payload["buyPrice"]["value"] == 80000
    assert {"meta": {"href": "https://api/attr/code"}, "value": "SUP-001"} in payload["attributes"]


def test_candidate_to_bitrix_payload_sets_site_fixed_fields():
    candidate = make_candidate(site_price=Decimal("1150.00"), unit_coefficient=Decimal("1.44"))
    property_codes = {
        "unit_coefficient": "UNIT_COEFFICIENT",
        "site_card_type": "CARD_TYPE",
        "supplier": "SUPPLIER_NAME",
    }

    payload = candidate_to_bitrix_payload(candidate, property_codes)

    assert payload["catalog"]["price"] == Decimal("1150.00")
    assert payload["catalog"]["quantityAccounting"] is False
    assert payload["properties"]["UNIT_COEFFICIENT"] == Decimal("1.44")
    assert payload["properties"]["CARD_TYPE"] == "Ламинат"
    assert payload["properties"]["SUPPLIER_NAME"] == "Test Supplier"
