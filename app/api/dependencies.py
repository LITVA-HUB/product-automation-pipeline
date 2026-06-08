from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy.orm import Session, sessionmaker

from app.adapters.repositories.models import Base
from app.config import Settings
from app.db import make_session_factory


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    settings = get_settings()
    factory = make_session_factory(settings.database_url)
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(factory.kw["bind"])
    return factory


def get_db_session() -> Iterator[Session]:
    factory = get_session_factory()
    with factory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
