from decimal import Decimal

from app.domain.product_candidate import FieldWithConfidence, ProductCandidate


def make_candidate(**overrides) -> ProductCandidate:
    data = {
        "supplier": "Test Supplier",
        "source_type": "manual",
        "source_url": "https://supplier.example/product/1",
        "raw_name": "Atlas Concorde Boost Pearl 60x120",
        "raw_article": "ART-001",
        "raw_description": "Supplier product page",
        "product_type": FieldWithConfidence(value="керамогранит", confidence=1, source="test"),
        "article": FieldWithConfidence(value="ART-001", confidence=1, source="test"),
        "supplier_code": FieldWithConfidence(value="SUP-001", confidence=1, source="test"),
        "unit": FieldWithConfidence(value="м²", confidence=1, source="test"),
        "units_per_package": FieldWithConfidence(
            value=Decimal("1.44"), confidence=1, source="test"
        ),
        "width_mm": FieldWithConfidence(value=600, confidence=1, source="test"),
        "height_mm": FieldWithConfidence(value=1200, confidence=1, source="test"),
        "thickness_mm": FieldWithConfidence(value=9, confidence=1, source="test"),
        "color": FieldWithConfidence(value="бежевый", confidence=1, source="test"),
        "surface": FieldWithConfidence(value="матовая", confidence=1, source="test"),
        "texture": FieldWithConfidence(value="камень", confidence=1, source="test"),
        "country": FieldWithConfidence(value="Италия", confidence=1, source="test"),
        "manufacturer": FieldWithConfidence(value="Atlas Concorde", confidence=1, source="test"),
        "brand_collection": FieldWithConfidence(value="Boost", confidence=1, source="test"),
        "site_manufacturer": FieldWithConfidence(value="Atlas", confidence=1, source="test"),
        "site_collection": FieldWithConfidence(value="Boost Pearl", confidence=1, source="test"),
        "faces_count": FieldWithConfidence(value=6, confidence=1, source="test"),
        "weight_kg": FieldWithConfidence(value=20, confidence=1, source="test"),
        "package_weight_kg": FieldWithConfidence(value=28, confidence=1, source="test"),
        "retail_price": Decimal("1000.00"),
        "purchase_price": Decimal("800.00"),
        "site_price": Decimal("1150.00"),
        "unit_coefficient": Decimal("1.44"),
        "generated_name": "Керамогранит Atlas Boost Pearl бежевый 600x1200 ART-001",
        "original_name": "Atlas Concorde Boost Pearl 60x120",
        "package_type": "УПК",
        "group_ms": "Atlas",
        "main_image": "/images/main.jpg",
    }
    data.update(overrides)
    return ProductCandidate(**data)
