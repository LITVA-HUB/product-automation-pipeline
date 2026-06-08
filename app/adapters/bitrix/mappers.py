from __future__ import annotations

from typing import Any

from app.domain.product_candidate import ProductCandidate


def candidate_to_bitrix_payload(
    candidate: ProductCandidate, property_codes: dict[str, str]
) -> dict[str, Any]:
    return {
        "ms_product_code": candidate.ms_product_code,
        "catalog": {
            "price": candidate.site_price,
            "quantityAccounting": False,
        },
        "properties": {
            property_codes["unit_coefficient"]: candidate.unit_coefficient,
            property_codes["site_card_type"]: "Ламинат",
            property_codes["supplier"]: candidate.supplier,
        },
        "images": {
            "extra": candidate.face_images,
            "announce": candidate.interior_images,
            "detail": candidate.interior_images,
        },
    }
