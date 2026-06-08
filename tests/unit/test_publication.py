import pytest

from app.services.publication.service import PublicationService
from app.workflow.states import WorkflowStatus
from tests.unit.helpers import make_candidate


class FakeMoySkladPublisher:
    def __init__(self) -> None:
        self.calls = []

    async def set_published_flag(self, ms_id: str, value: bool) -> dict:
        self.calls.append((ms_id, value))
        return {"id": ms_id, "published": value}


class FakeSitePublisher:
    def __init__(self) -> None:
        self.calls = []

    async def publish(self, site_id: str) -> None:
        self.calls.append(site_id)


@pytest.mark.asyncio
async def test_publication_publishes_only_approved_candidate():
    ms = FakeMoySkladPublisher()
    site = FakeSitePublisher()
    candidate = make_candidate(
        status=WorkflowStatus.APPROVED,
        ms_product_id="ms-1",
        site_product_id="site-1",
    )

    updated = await PublicationService(ms, site).publish(candidate)

    assert updated.status == WorkflowStatus.PUBLISHED
    assert ms.calls == [("ms-1", True)]
    assert site.calls == ["site-1"]


@pytest.mark.asyncio
async def test_publication_rejects_unapproved_candidate():
    candidate = make_candidate(status=WorkflowStatus.SITE_VERIFIED)

    with pytest.raises(ValueError, match="approved"):
        await PublicationService(FakeMoySkladPublisher(), FakeSitePublisher()).publish(candidate)
