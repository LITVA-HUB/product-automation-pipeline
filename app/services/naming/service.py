from __future__ import annotations

from app.domain.product_candidate import ProductCandidate


def construct_names(candidate: ProductCandidate) -> ProductCandidate:
    product_type = _title(candidate.product_type.value)
    site_manufacturer = _text(candidate.site_manufacturer.value)
    site_collection = _text(candidate.site_collection.value)
    color = _text(candidate.color.value)
    article = _text(candidate.article.value)
    size = _size(candidate.width_mm.value, candidate.height_mm.value)

    candidate.generated_name = " ".join(
        part
        for part in [product_type, site_manufacturer, site_collection, color, size, article]
        if part
    )

    manufacturer = _text(candidate.manufacturer.value)
    brand_collection = _text(candidate.brand_collection.value)
    candidate.original_name = " ".join(
        part for part in [manufacturer, brand_collection, size, article] if part
    )
    return candidate


def _text(value: object) -> str:
    return "" if value is None else str(value).strip()


def _title(value: object) -> str:
    text = _text(value)
    return text[:1].upper() + text[1:] if text else ""


def _size(width: object, height: object) -> str:
    if width is None or height is None:
        return ""
    return f"{width}x{height}"
