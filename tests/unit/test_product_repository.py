from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.adapters.repositories.models import Base
from app.adapters.repositories.product_repository import ProductRepository
from tests.unit.helpers import make_candidate


def test_product_repository_create_and_get_round_trips_candidate():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False, future=True)

    candidate = make_candidate()
    with Session() as session:
        repo = ProductRepository(session)
        repo.save(candidate)
        session.commit()

    with Session() as session:
        repo = ProductRepository(session)
        loaded = repo.get(candidate.id)

    assert loaded is not None
    assert loaded.id == candidate.id
    assert loaded.article.value == "ART-001"
    assert loaded.supplier_code.value == "SUP-001"
    assert loaded.ms_product_code is None


def test_product_repository_updates_index_columns_from_candidate_fields():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False, future=True)

    candidate = make_candidate()
    candidate.ms_product_code = "00042"
    with Session() as session:
        repo = ProductRepository(session)
        repo.save(candidate)
        session.commit()

        row = repo.get_row(candidate.id)

    assert row.article == "ART-001"
    assert row.supplier_code == "SUP-001"
    assert row.ms_product_code == "00042"
