#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.extraction import ExtractionResult, ImageClassification
from app.domain.product_candidate import FieldWithConfidence
from app.services.ingestion.service import IngestionService
from app.services.pipeline.product_pipeline import ProductPipeline


class DemoImageClassifier:
    def classify_image_path(self, image_path: str) -> ImageClassification:
        if "interior" in image_path:
            return ImageClassification(image_type="interior", confidence=0.95, warning=None)
        if "face" in image_path:
            return ImageClassification(image_type="face", confidence=0.95, warning=None)
        return ImageClassification(image_type="main", confidence=0.95, warning=None)


def build_demo_extraction(row: dict[str, str]) -> ExtractionResult:
    return ExtractionResult(
        fields={
            "product_type": FieldWithConfidence(
                value="керамогранит", confidence=0.95, source="dry_run"
            ),
            "article": FieldWithConfidence(
                value=row["raw_article"], confidence=0.99, source="raw_article"
            ),
            "supplier_code": FieldWithConfidence(
                value="SUP-001", confidence=0.95, source="dry_run"
            ),
            "unit": FieldWithConfidence(value="м²", confidence=0.99, source="dry_run"),
            "units_per_package": FieldWithConfidence(
                value=Decimal("1.44"), confidence=0.99, source="dry_run"
            ),
            "width_mm": FieldWithConfidence(value=600, confidence=0.95, source="dry_run"),
            "height_mm": FieldWithConfidence(value=1200, confidence=0.95, source="dry_run"),
            "thickness_mm": FieldWithConfidence(value=9, confidence=0.95, source="dry_run"),
            "color": FieldWithConfidence(value="бежевый", confidence=0.9, source="dry_run"),
            "surface": FieldWithConfidence(value="матовая", confidence=0.9, source="dry_run"),
            "texture": FieldWithConfidence(value="камень", confidence=0.9, source="dry_run"),
            "country": FieldWithConfidence(value="Италия", confidence=0.9, source="dry_run"),
            "manufacturer": FieldWithConfidence(
                value="Atlas Concorde", confidence=0.95, source="dry_run"
            ),
            "brand_collection": FieldWithConfidence(
                value="Boost", confidence=0.95, source="dry_run"
            ),
            "site_manufacturer": FieldWithConfidence(
                value="Atlas", confidence=0.95, source="dry_run"
            ),
            "site_collection": FieldWithConfidence(
                value="Boost Pearl", confidence=0.95, source="dry_run"
            ),
            "weight_kg": FieldWithConfidence(value=20, confidence=0.9, source="dry_run"),
            "package_weight_kg": FieldWithConfidence(
                value=28, confidence=0.9, source="dry_run"
            ),
        },
        needs_human_review=False,
        warnings=[],
    )


def run(input_path: Path) -> dict:
    field_map = {
        "raw_name": "raw_name",
        "raw_article": "raw_article",
        "raw_price": "raw_price",
        "raw_description": "raw_description",
    }
    candidates = IngestionService().from_csv(
        supplier="Demo Supplier", path=input_path, field_map=field_map
    )
    raw_rows = json_rows(input_path)
    pipeline = ProductPipeline(image_classifier=DemoImageClassifier())
    products = []
    for candidate, row in zip(candidates, raw_rows, strict=True):
        candidate.source_url = row["source_url"]
        candidate.raw_images = [row["main_image"], row["face_image"], row["interior_image"]]
        candidate.retail_price = Decimal(row["raw_price"])
        prepared = pipeline.prepare_for_ms(
            candidate,
            extraction=build_demo_extraction(row),
            existing_candidates=[],
            prompt_version="dry_run",
        )
        products.append(
            {
                "id": str(prepared.id),
                "status": prepared.status.value,
                "generated_name": prepared.generated_name,
                "purchase_price": str(prepared.purchase_price),
                "site_price": str(prepared.site_price),
                "publication_mode": prepared.publication_mode.value,
                "site_export_required": prepared.site_export_required,
                "main_image": prepared.main_image,
                "face_images": prepared.face_images,
                "interior_images": prepared.interior_images,
                "review_required": prepared.human_review_required,
                "review_reasons": prepared.review_reasons,
            }
        )
    return {"processed": len(products), "products": products}


def json_rows(input_path: Path) -> list[dict[str, str]]:
    import csv

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the product pipeline without external writes.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = run(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Processed {payload['processed']} product(s):")
    for product in payload["products"]:
        print(f"- {product['generated_name']} -> {product['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
