import os
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy.engine import URL

from app.core.config import PROJECT_ROOT, Settings
from app.db import session as database
from app.main import app


@pytest.fixture(autouse=True)
def clear_database_state() -> None:
    database.dispose_engine()
    yield
    database.dispose_engine()


def test_database_url_reads_unprefixed_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_url = (
        "postgresql+psycopg://launchshield_user:secret@localhost:5432/launchshield_ai"
    )
    monkeypatch.setenv("DATABASE_URL", database_url)

    settings = Settings(_env_file=None)

    assert settings.database_url == SecretStr(database_url)


def test_database_url_reads_prefixed_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_url = (
        "postgresql+psycopg://launchshield_user:secret@localhost:5432/launchshield_ai"
    )
    monkeypatch.setenv("LAUNCHSHIELD_DATABASE_URL", database_url)

    settings = Settings(_env_file=None)

    assert settings.database_url == SecretStr(database_url)


def test_missing_database_url_is_optional(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("LAUNCHSHIELD_DATABASE_URL", raising=False)

    assert Settings(_env_file=None).database_url is None


def test_env_file_path_is_anchored_at_project_root() -> None:
    assert Settings.model_config["env_file"] == PROJECT_ROOT / ".env"


def test_secret_settings_representation_hides_credentials() -> None:
    secret = "postgresql+psycopg://launchshield_user:never-show@localhost/db"
    settings = Settings(_env_file=None, DATABASE_URL=secret)

    assert secret not in repr(settings)
    assert "never-show" not in repr(settings.database_url)
    assert str(settings.database_url) == "**********"


def test_database_url_parses_url_encoded_credentials() -> None:
    secret = (
        "postgresql+psycopg://launchshield_user:p%40ss%3Aword"
        "@localhost:5432/launchshield_ai"
    )
    settings = Settings(_env_file=None, DATABASE_URL=secret)

    parsed_url = database._database_url(settings)

    assert isinstance(parsed_url, URL)
    assert parsed_url.password == "p@ss:word"
    assert "p@ss:word" not in repr(parsed_url)


def test_database_url_rejects_superuser() -> None:
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgresql+psycopg://postgres:secret@localhost/launchshield_ai",
    )

    with pytest.raises(database.DatabaseConfigurationError) as error:
        database._database_url(settings)

    assert "launchshield_user application role" in str(error.value)
    assert "secret" not in str(error.value)


def test_engine_is_created_lazily_and_uses_safe_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        _env_file=None,
        DATABASE_URL=(
            "postgresql+psycopg://launchshield_user:secret@localhost:5432/launchshield_ai"
        ),
    )
    engine = Mock()
    create_engine = Mock(return_value=engine)
    monkeypatch.setattr(database, "get_settings", lambda: settings)
    monkeypatch.setattr(database, "create_engine", create_engine)

    assert database._engine is None
    assert database.get_engine() is engine
    assert database.get_engine() is engine
    create_engine.assert_called_once()
    assert create_engine.call_args.kwargs == {
        "pool_pre_ping": True,
        "echo": False,
        "hide_parameters": True,
    }


def test_engine_creation_requires_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        database,
        "get_settings",
        lambda: Settings(_env_file=None),
    )

    with pytest.raises(database.DatabaseConfigurationError) as error:
        database.get_engine()

    assert "DATABASE_URL is required" in str(error.value)


def test_session_dependency_closes_without_committing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = Mock()
    monkeypatch.setattr(database, "get_session_factory", lambda: lambda: session)

    dependency = database.get_db_session()
    assert next(dependency) is session
    with pytest.raises(StopIteration):
        next(dependency)

    session.close.assert_called_once()
    session.commit.assert_not_called()


def test_session_factory_is_cached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()
    create_engine = Mock(return_value=engine)
    monkeypatch.setattr(
        database,
        "get_settings",
        lambda: Settings(
            _env_file=None,
            DATABASE_URL=(
                "postgresql+psycopg://launchshield_user:secret@localhost:5432/"
                "launchshield_ai"
            ),
        ),
    )
    monkeypatch.setattr(database, "create_engine", create_engine)

    factory = database.get_session_factory()

    assert database.get_session_factory() is factory
    assert factory.kw["bind"] is engine
    assert factory.kw["autoflush"] is False
    assert factory.kw["autocommit"] is False
    create_engine.assert_called_once()


def test_dispose_engine_disposes_and_clears_cached_state() -> None:
    engine = Mock()
    factory = Mock()
    database._engine = engine
    database._session_factory = factory

    database.dispose_engine()

    engine.dispose.assert_called_once()
    assert database._engine is None
    assert database._session_factory is None


def test_app_shutdown_disposes_initialized_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dispose = Mock()
    monkeypatch.setattr("app.main.dispose_engine", dispose)

    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "healthy"}

    dispose.assert_called_once()


@pytest.mark.skipif(
    os.getenv("RUN_DATABASE_INTEGRATION_TEST") != "1",
    reason="Set RUN_DATABASE_INTEGRATION_TEST=1 to enable PostgreSQL integration test.",
)
def test_postgresql_select_one_integration() -> None:
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError

    settings = database.get_settings()
    if settings.database_url is None:
        pytest.skip("DATABASE_URL is not configured.")

    url = database._database_url(settings)
    if url.username != "launchshield_user":
        pytest.fail(
            "The database integration test requires the launchshield_user application role.",
            pytrace=False,
        )

    engine = database.get_engine()
    try:
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one() == 1
    except SQLAlchemyError:
        pytest.fail(
            "PostgreSQL connection test failed; detailed connection information is suppressed.",
            pytrace=False,
        )
    finally:
        database.dispose_engine()
