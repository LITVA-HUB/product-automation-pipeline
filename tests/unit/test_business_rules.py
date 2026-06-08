from decimal import Decimal

import pytest

from app.domain.product_candidate import FieldWithConfidence, ProductCandidate
from app.services.rules.product_rules import apply_business_rules


def candidate(**overrides):
    data = {
        "supplier": "Test Supplier",
        "raw_name": "Porcelain Tile 60x120",
        "raw_article": "ART-001",
        "source_type": "manual",
        "article": FieldWithConfidence(value="ART-001", confidence=1, source="test"),
        "supplier_code": FieldWithConfidence(value="SUP-001", confidence=1, source="test"),
        "unit": FieldWithConfidence(value="м²", confidence=1, source="test"),
        "units_per_package": FieldWithConfidence(
            value=Decimal("1.44"), confidence=1, source="test"
        ),
        "site_manufacturer": FieldWithConfidence(
            value="Atlas Concorde", confidence=1, source="test"
        ),
        "retail_price": Decimal("1000.00"),
    }
    data.update(overrides)
    return ProductCandidate(**data)


def test_business_rules_apply_fixed_values_and_money_formulas():
    result = apply_business_rules(candidate())

    assert result.package_type == "УПК"
    assert result.purchase_price == Decimal("800.00")
    assert result.site_price == Decimal("1150.00")
    assert result.unit_coefficient == Decimal("1.44")
    assert result.site_card_type == "Ламинат"
    assert result.group_ms == "Atlas Concorde"


def test_business_rules_reject_missing_retail_price():
    with pytest.raises(ValueError, match="retail_price"):
        apply_business_rules(candidate(retail_price=None))


def test_business_rules_reject_missing_units_per_package():
    with pytest.raises(ValueError, match="units_per_package"):
        apply_business_rules(
            candidate(
                units_per_package=FieldWithConfidence(value=None, confidence=0, source="test")
            )
        )
