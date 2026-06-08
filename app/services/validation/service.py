from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.product_candidate import ProductCandidate, ValidationErrorItem


class ValidationResult(BaseModel):
    scope: str
    passed: bool
    errors: list[ValidationErrorItem] = Field(default_factory=list)


def validate_before_ms(candidate: ProductCandidate) -> ValidationResult:
    errors: list[ValidationErrorItem] = []
    _required(errors, "name", candidate.generated_name)
    _required(errors, "article", candidate.article.value)
    _required(errors, "supplier", candidate.supplier)
    _required(errors, "group_ms", candidate.group_ms)
    _required(errors, "unit", candidate.unit.value)
    _required(errors, "units_per_package", candidate.units_per_package.value)
    _required(errors, "retail_price", candidate.retail_price)
    _required(errors, "supplier_code", candidate.supplier_code.value)
    _required(errors, "main_image", candidate.main_image)

    if candidate.package_type != "УПК":
        errors.append(_error("before_ms", "package_type", "package_type must be УПК"))
    if candidate.purchase_price is not None and candidate.retail_price is not None:
        expected = Decimal(str(candidate.retail_price)) * Decimal("0.8")
        if Decimal(str(candidate.purchase_price)) != expected.quantize(Decimal("0.01")):
            errors.append(_error("before_ms", "purchase_price", "purchase price must be retail * 0.8"))

    return ValidationResult(scope="before_ms", passed=not errors, errors=errors)


def validate_site(candidate: ProductCandidate, site_snapshot: dict) -> ValidationResult:
    errors: list[ValidationErrorItem] = []
    if not site_snapshot.get("found_by_ms_code"):
        errors.append(_error("site", "site_product", "product must be found by МойСклад code"))
    if Decimal(str(site_snapshot.get("site_price", "0"))) != Decimal(str(candidate.site_price)):
        errors.append(_error("site", "site_price", "site price must be retail * 1.15"))
    if Decimal(str(site_snapshot.get("unit_coefficient", "0"))) != Decimal(
        str(candidate.unit_coefficient)
    ):
        errors.append(_error("site", "unit_coefficient", "coefficient must equal package quantity"))
    if site_snapshot.get("quantity_accounting_enabled") is not False:
        errors.append(_error("site", "quantity_accounting", "quantity accounting must be disabled"))
    if site_snapshot.get("site_card_type") != "Ламинат":
        errors.append(_error("site", "site_card_type", "site card type must be Ламинат"))
    if site_snapshot.get("supplier") != candidate.supplier:
        errors.append(_error("site", "supplier", "supplier name must be copied from МойСклад"))
    return ValidationResult(scope="site", passed=not errors, errors=errors)


def _required(errors: list[ValidationErrorItem], field: str, value: object) -> None:
    if value is None or value == "":
        errors.append(_error("before_ms", field, f"{field} is required"))


def _error(scope: str, field: str, message: str) -> ValidationErrorItem:
    return ValidationErrorItem(scope=scope, field=field, message=message)
