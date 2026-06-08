from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.adapters.repositories.models import Base
from app.adapters.repositories.product_repository import ProductRepository
from app.adapters.repositories.review_repository import HumanReviewRepository
from tests.unit.helpers import make_candidate


def test_human_review_repository_records_corrections_with_before_after_snapshots():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False, future=True)
    candidate = make_candidate()

    with Session() as session:
        ProductRepository(session).save(candidate)
        review_repo = HumanReviewRepository(session)
        review = review_repo.record(
            product_id=candidate.id,
            operator="operator@example.com",
            decision="fix",
            corrections={"color": "серый"},
            before={"color": "бежевый"},
            after={"color": "серый"},
        )
        session.commit()

    with Session() as session:
        rows = HumanReviewRepository(session).list_for_product(candidate.id)

    assert review.id is not None
    assert len(rows) == 1
    assert rows[0].decision == "fix"
    assert rows[0].corrections == {"color": "серый"}
    assert rows[0].before == {"color": "бежевый"}
    assert rows[0].after == {"color": "серый"}
