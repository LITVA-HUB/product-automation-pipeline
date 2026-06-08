from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.domain.product_candidate import ProductCandidate
from app.domain.publication import PublicationMode


def candidate_to_ms_product(candidate: ProductCandidate, maps: dict[str, Any]) -> dict[str, Any]:
    if not candidate.group_ms:
        raise ValueError("group_ms is required before mapping to МойСклад payload")
    payload: dict[str, Any] = {
        "name": candidate.generated_name,
        "article": candidate.article.value,
        "description": candidate.source_url or candidate.raw_description,
        "uom": maps["uom"][candidate.unit.value],
        "productFolder": maps["folder"][candidate.group_ms],
        "supplier": maps["supplier"][candidate.supplier],
        "salePrices": [
            {
                "value": _minor_units(candidate.retail_price),
                "priceType": maps["price_types"]["retail"],
            }
        ],
        "buyPrice": {
            "value": _minor_units(candidate.purchase_price),
            "priceType": maps["price_types"]["purchase"],
        },
        "attributes": [],
    }

    add_attribute(payload, maps, "Код поставщика", candidate.supplier_code.value)
    add_attribute(payload, maps, "Тип карточки", candidate.site_card_type)
    add_attribute(payload, maps, "Выгружено на сайте", _site_export_flag(candidate))
    return payload


def add_attribute(payload: dict[str, Any], maps: dict[str, Any], name: str, value: object) -> None:
    attribute = maps.get("attributes", {}).get(name)
    if attribute and value is not None:
        payload["attributes"].append({"meta": attribute["meta"], "value": value})


def _minor_units(value: Decimal | None) -> int:
    if value is None:
        raise ValueError("price is required")
    return int((Decimal(str(value)) * Decimal("100")).quantize(Decimal("1")))


def _site_export_flag(candidate: ProductCandidate) -> bool:
    return candidate.publication_mode == PublicationMode.MS_AND_SITE_ACTIVE
