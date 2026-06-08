from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from app.domain.product_candidate import ProductCandidate

PURCHASE_PRICE_FACTOR = Decimal("0.8")
SITE_PRICE_FACTOR = Decimal("1.15")
MONEY_QUANT = Decimal("0.01")
PACKAGE_TYPE = "УПК"
SITE_CARD_TYPE = "Ламинат"


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def require_decimal(value: object, field_name: str) -> Decimal:
    if value is None:
        raise ValueError(f"{field_name} is required")
    return Decimal(str(value))


def apply_business_rules(candidate: ProductCandidate) -> ProductCandidate:
    retail_price = require_decimal(candidate.retail_price, "retail_price")
    units_per_package = require_decimal(candidate.units_per_package.value, "units_per_package")

    candidate.package_type = PACKAGE_TYPE
    candidate.purchase_price = money(retail_price * PURCHASE_PRICE_FACTOR)
    candidate.site_price = money(retail_price * SITE_PRICE_FACTOR)
    candidate.unit_coefficient = units_per_package
    candidate.site_card_type = SITE_CARD_TYPE

    if candidate.site_manufacturer.value:
        candidate.group_ms = str(candidate.site_manufacturer.value)

    return candidate
