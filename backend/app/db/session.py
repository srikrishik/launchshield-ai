from collections.abc import Generator
from threading import Lock

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings


class DatabaseConfigurationError(RuntimeError):
    """Raised when database settings are missing or unsafe."""


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None
_engine_lock = Lock()


def _database_url(settings: Settings) -> URL:
    if settings.database_url is None:
        raise DatabaseConfigurationError(
            "DATABASE_URL is required for database operations."
        )

    try:
        url = make_url(settings.database_url.get_secret_value())
    except ArgumentError:
        raise DatabaseConfigurationError(
            "DATABASE_URL must be a valid SQLAlchemy URL with URL-encoded credentials."
        ) from None

    if url.drivername != "postgresql+psycopg":
        raise DatabaseConfigurationError(
            "DATABASE_URL must use the postgresql+psycopg driver."
        )
    if url.username != "launchshield_user":
        raise DatabaseConfigurationError(
            "DATABASE_URL must use the launchshield_user application role."
        )
    if not url.database:
        raise DatabaseConfigurationError(
            "DATABASE_URL must specify a database name."
        )

    return url


def get_engine() -> Engine:
    global _engine

    if _engine is None:
        with _engine_lock:
            if _engine is None:
                _engine = create_engine(
                    _database_url(get_settings()),
                    pool_pre_ping=True,
                    echo=False,
                    hide_parameters=True,
                )
    assert _engine is not None
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory

    engine = get_engine()
    if _session_factory is None:
        with _engine_lock:
            if _session_factory is None:
                _session_factory = sessionmaker(
                    bind=engine,
                    autoflush=False,
                    autocommit=False,
                    expire_on_commit=False,
                )
    assert _session_factory is not None
    return _session_factory


def dispose_engine() -> None:
    global _engine, _session_factory

    with _engine_lock:
        if _engine is not None:
            _engine.dispose()
        _engine = None
        _session_factory = None


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
