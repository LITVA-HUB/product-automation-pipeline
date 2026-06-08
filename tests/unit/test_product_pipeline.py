from decimal import Decimal

import pytest

from app.domain.extraction import ExtractionResult, ImageClassification
from app.domain.product_candidate import FieldWithConfidence, ProductCandidate
from app.services.pipeline.product_pipeline import ProductPipeline
from app.workflow.states import WorkflowStatus
from tests.unit.helpers import make_candidate


class FakeImageClassifier:
    def classify_image_path(self, image_path: str) -> ImageClassification:
        if "interior" in image_path:
            return ImageClassification(image_type="interior", confidence=0.95)
        if "face" in image_path:
            return ImageClassification(image_type="face", confidence=0.95)
        return ImageClassification(image_type="main", confidence=0.95)


class FakeMoySkladClient:
    def __init__(self) -> None:
        self.created_payloads = []
        self.uploads = []

    async def create_product(self, payload: dict) -> dict:
        self.created_payloads.append(payload)
        return {"id": "ms-id-1", "code": "MS-0001"}

    async def upload_image(self, ms_id: str, image_path: str) -> dict:
        self.uploads.append((ms_id, image_path))
        return {"id": "image-1"}


class FakeSiteClient:
    def __init__(self) -> None:
        self.calls = []

    async def create_or_update_product(self, payload: dict) -> dict:
        self.calls.append(("create_or_update_product", payload))
        return {"id": "site-id-1"}

    async def set_properties(self, site_id: str, properties: dict) -> None:
        self.calls.append(("set_properties", site_id, properties))

    async def upload_images(
        self, site_id: str, extra: list[str], announce: list[str], detail: list[str]
    ) -> None:
        self.calls.append(("upload_images", site_id, extra, announce, detail))

    async def set_catalog_price(self, site_id: str, price: Decimal) -> None:
        self.calls.append(("set_catalog_price", site_id, price))

    async def set_unit_coefficient(self, site_id: str, coef: Decimal) -> None:
        self.calls.append(("set_unit_coefficient", site_id, coef))

    async def disable_quantity_accounting(self, site_id: str) -> None:
        self.calls.append(("disable_quantity_accounting", site_id))

    async def set_card_type(self, site_id: str, value: str = "Ламинат") -> None:
        self.calls.append(("set_card_type", site_id, value))

    async def set_supplier_name(self, site_id: str, supplier: str) -> None:
        self.calls.append(("set_supplier_name", site_id, supplier))


def extraction_result() -> ExtractionResult:
    return ExtractionResult(
        fields={
            "article": FieldWithConfidence(value="ART-001", confidence=0.95, source="raw"),
            "supplier_code": FieldWithConfidence(value="SUP-001", confidence=0.95, source="raw"),
        },
        needs_human_review=False,
    )


def raw_candidate() -> ProductCandidate:
    candidate = make_candidate(
        article=FieldWithConfidence(value=None, confidence=0),
        supplier_code=FieldWithConfidence(value=None, confidence=0),
        raw_images=["main.jpg", "face-1.jpg", "interior.jpg"],
        main_image=None,
        generated_name=None,
        original_name=None,
        purchase_price=None,
        site_price=None,
        unit_coefficient=None,
        group_ms=None,
        status=WorkflowStatus.PARSED,
    )
    return candidate


def test_product_pipeline_prepares_unique_candidate_until_validated_before_ms():
    pipeline = ProductPipeline(image_classifier=FakeImageClassifier())

    candidate = pipeline.prepare_for_ms(
        raw_candidate(),
        extraction=extraction_result(),
        existing_candidates=[],
        prompt_version="extract_v1",
    )

    assert candidate.status == WorkflowStatus.VALIDATED_BEFORE_MS
    assert candidate.generated_name
    assert candidate.purchase_price == Decimal("800.00")
    assert candidate.site_price == Decimal("1150.00")
    assert candidate.main_image == "main.jpg"
    assert candidate.face_images == ["face-1.jpg"]
    assert candidate.interior_images == ["interior.jpg"]


def test_product_pipeline_stops_possible_duplicate_before_external_writes():
    duplicate = make_candidate(
        article=FieldWithConfidence(value="OTHER", confidence=1),
        supplier_code=FieldWithConfidence(value="OTHER", confidence=1),
    )
    pipeline = ProductPipeline(image_classifier=FakeImageClassifier())

    candidate = pipeline.prepare_for_ms(
        raw_candidate(),
        extraction=extraction_result(),
        existing_candidates=[duplicate],
        prompt_version="extract_v1",
    )

    assert candidate.status == WorkflowStatus.POSSIBLE_DUPLICATE
    assert candidate.human_review_required is True
    assert "possible_duplicate" in candidate.review_reasons


@pytest.mark.asyncio
async def test_product_pipeline_writes_ms_and_site_with_configured_values():
    pipeline = ProductPipeline(image_classifier=FakeImageClassifier())
    candidate = pipeline.prepare_for_ms(raw_candidate(), extraction_result(), [])
    ms_client = FakeMoySkladClient()
    site_client = FakeSiteClient()

    updated = await pipeline.create_in_ms_and_configure_site(
        candidate,
        ms_client=ms_client,
        site_client=site_client,
        ms_maps=ms_maps(),
        bitrix_property_codes=bitrix_property_codes(),
    )

    assert updated.status == WorkflowStatus.SITE_VERIFIED
    assert updated.ms_product_id == "ms-id-1"
    assert updated.ms_product_code == "MS-0001"
    assert updated.site_product_id == "site-id-1"
    assert ms_client.uploads == [("ms-id-1", "main.jpg")]
    assert ("set_card_type", "site-id-1", "Ламинат") in site_client.calls


def ms_maps() -> dict:
    return {
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


def bitrix_property_codes() -> dict:
    return {
        "unit_coefficient": "UNIT_COEFFICIENT",
        "site_card_type": "CARD_TYPE",
        "supplier": "SUPPLIER_NAME",
    }
