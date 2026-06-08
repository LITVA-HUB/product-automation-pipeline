from decimal import Decimal

from app.domain.product_candidate import FieldWithConfidence
from app.services.naming.service import construct_names
from app.services.validation.service import validate_before_ms, validate_site
from tests.unit.helpers import make_candidate


def test_construct_names_uses_normalized_fields_deterministically():
    candidate = make_candidate(generated_name=None, original_name=None)

    result = construct_names(candidate)

    assert result.generated_name == "Керамогранит Atlas Boost Pearl бежевый 600x1200 ART-001"
    assert result.original_name == "Atlas Concorde Boost 600x1200 ART-001"


def test_validate_before_ms_passes_complete_candidate():
    candidate = make_candidate()

    result = validate_before_ms(candidate)

    assert result.passed is True
    assert result.errors == []


def test_validate_before_ms_reports_required_field_failures():
    candidate = make_candidate(
        article=FieldWithConfidence(value=None, confidence=0, source="test"),
        main_image=None,
    )

    result = validate_before_ms(candidate)

    assert result.passed is False
    assert {error.field for error in result.errors} >= {"article", "main_image"}


def test_validate_site_checks_price_coefficient_accounting_and_card_type():
    candidate = make_candidate(site_price=Decimal("1150.00"), unit_coefficient=Decimal("1.44"))
    site_snapshot = {
        "found_by_ms_code": True,
        "site_price": "1150.00",
        "unit_coefficient": "1.44",
        "quantity_accounting_enabled": False,
        "site_card_type": "Ламинат",
        "supplier": "Test Supplier",
    }

    result = validate_site(candidate, site_snapshot)

    assert result.passed is True
    assert result.errors == []
