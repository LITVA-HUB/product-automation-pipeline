import pytest

from app.adapters.moysklad.mappers import candidate_to_ms_product
from app.domain.product_candidate import ProductCandidate
from app.domain.publication import PublicationMode
from app.services.pipeline.product_pipeline import ProductPipeline
from app.services.publication.service import PublicationService
from app.workflow.states import WorkflowStatus
from tests.unit.helpers import make_candidate
from tests.unit.test_product_pipeline import (
    FakeImageClassifier,
    FakeMoySkladClient,
    extraction_result,
    ms_maps,
    raw_candidate,
)


def test_product_candidate_defaults_to_ms_only_publication_mode():
    candidate = ProductCandidate(supplier="Supplier", source_type="manual")

    assert candidate.publication_mode == PublicationMode.MS_ONLY
    assert candidate.site_export_required is False


def test_ms_payload_sets_site_export_flag_false_by_default():
    candidate = make_candidate(publication_mode=PublicationMode.MS_ONLY)

    payload = candidate_to_ms_product(candidate, ms_maps())

    assert {"meta": {"href": "https://api/attr/site-export"}, "value": False} in payload[
        "attributes"
    ]


@pytest.mark.asyncio
async def test_pipeline_creates_product_in_ms_only_without_site_client():
    pipeline = ProductPipeline(image_classifier=FakeImageClassifier())
    candidate = pipeline.prepare_for_ms(raw_candidate(), extraction_result(), [])
    ms_client = FakeMoySkladClient()

    updated = await pipeline.create_in_ms(candidate, ms_client=ms_client, ms_maps=ms_maps())

    assert updated.status == WorkflowStatus.MS_VERIFIED
    assert updated.ms_product_id == "ms-id-1"
    assert updated.site_product_id is None
    assert ms_client.uploads == [("ms-id-1", "main.jpg")]
    assert ms_client.created_payloads[0]["attributes"][-1]["value"] is False


@pytest.mark.asyncio
async def test_publication_service_activates_site_export_flag_in_ms_only():
    class FakeMoySkladPublisher:
        def __init__(self) -> None:
            self.calls = []

        async def set_published_flag(self, ms_id: str, value: bool) -> dict:
            self.calls.append((ms_id, value))
            return {"id": ms_id, "published": value}

    candidate = make_candidate(
        status=WorkflowStatus.APPROVED,
        ms_product_id="ms-1",
        site_product_id=None,
        publication_mode=PublicationMode.MS_AND_SITE_ACTIVE,
    )
    publisher = FakeMoySkladPublisher()

    updated = await PublicationService(publisher).publish(candidate)

    assert updated.status == WorkflowStatus.PUBLISHED
    assert publisher.calls == [("ms-1", True)]
