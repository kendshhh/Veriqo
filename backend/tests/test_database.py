from uuid import uuid4

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from app.database import database_url
from app.models import AnalyzedEmail, Base, Classification, User
from app.seed import DEMO_EMAILS, DEMO_USER_ID, seed_database
from conftest import migration_config
from sqlalchemy import delete, func, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def test_connection_url_preserves_neon_parameters_without_exposing_credentials():
    url = database_url("postgresql://name:secret@db.example.invalid/db?sslmode=require")
    assert url.drivername == "postgresql+psycopg"
    assert url.query["sslmode"] == "require"
    assert "secret" not in str(url)


@pytest.mark.parametrize("scheme", ["postgres", "postgresql", "postgresql+psycopg"])
def test_connection_url_normalizes_driver_and_preserves_credentials_and_tls(scheme):
    url = database_url(
        f"{scheme}://name:p%40ss%25word@db.example.invalid/db"
        "?sslmode=require&channel_binding=require"
    )
    assert url.drivername == "postgresql+psycopg"
    assert url.password == "p@ss%word"
    assert url.query == {"sslmode": "require", "channel_binding": "require"}


def test_connection_url_uses_environment_without_overwriting_it(monkeypatch):
    monkeypatch.setattr("app.database.load_dotenv", lambda path: None)
    monkeypatch.setenv("DATABASE_URL", "postgresql://name:secret@db.example.invalid/db")
    assert database_url().host == "db.example.invalid"


def test_connection_url_requires_configuration(monkeypatch):
    monkeypatch.setattr("app.database.load_dotenv", lambda path: None)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="Set DATABASE_URL"):
        database_url()


@pytest.mark.parametrize("value", ["", "not-a-url", "sqlite:///test.db"])
def test_connection_url_rejects_invalid_configuration(value):
    with pytest.raises(ValueError):
        database_url(value)


@pytest.mark.postgres
def test_migration_matches_models_and_can_be_rerun(postgres_engine):
    seed_database(postgres_engine)
    with postgres_engine.begin() as connection:
        config = migration_config(connection)
        command.upgrade(config, "head")
        assert set(inspect(connection).get_table_names()) == {
            "users",
            "analyzed_emails",
            "alembic_version",
        }
        assert connection.scalar(select(func.count()).select_from(AnalyzedEmail)) == 3
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0001"
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []


@pytest.mark.postgres
def test_migration_downgrade_then_upgrade_on_disposable_schema(postgres_engine):
    with postgres_engine.begin() as connection:
        config = migration_config(connection)
        command.downgrade(config, "base")
        assert inspect(connection).get_table_names() == ["alembic_version"]
        command.upgrade(config, "head")
        assert "analyzed_emails" in inspect(connection).get_table_names()


@pytest.mark.postgres
def test_registering_matching_existing_schema_preserves_records(postgres_engine):
    with postgres_engine.begin() as connection:
        config = migration_config(connection)
        command.downgrade(config, "base")
        connection.execute(text("DROP TABLE alembic_version"))
        # Model a populated database that has no Alembic revision record yet.
        # Metadata creation is confined to this disposable test schema.
        Base.metadata.create_all(connection)
    seed_database(postgres_engine)
    with postgres_engine.begin() as connection:
        assert (
            compare_metadata(
                MigrationContext.configure(connection, opts={"compare_server_default": True}),
                Base.metadata,
            )
            == []
        )
        config = migration_config(connection)
        command.stamp(config, "0001")
        command.upgrade(config, "head")
        assert connection.scalar(select(func.count()).select_from(AnalyzedEmail)) == 3
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0001"


@pytest.mark.postgres
def test_synthetic_seed_is_repeatable_and_uses_the_relationship(postgres_engine):
    seed_database(postgres_engine)
    seed_database(postgres_engine)
    with Session(postgres_engine) as session:
        user = session.get(User, DEMO_USER_ID)
        assert user.email == "demo@example.invalid"
        assert len(user.analyzed_emails) == 3
        assert {email.classification_result for email in user.analyzed_emails} == set(
            Classification
        )
        assert all(email.created_at.tzinfo is not None for email in user.analyzed_emails)
        assert all(email.user_id == user.id for email in user.analyzed_emails)


@pytest.mark.postgres
def test_database_generates_id_timestamp_and_empty_indicator_array(postgres_engine):
    with Session(postgres_engine) as session, session.begin():
        user = User(email="generated@example.invalid")
        session.add(user)
        session.flush()
        values = {
            k: v
            for k, v in DEMO_EMAILS[0].items()
            if k not in {"id", "user_id", "threat_indicators"}
        }
        email = AnalyzedEmail(user_id=user.id, **values)
        session.add(email)
        session.flush()
        assert user.id.version == 4
        assert email.id.version == 4
        assert email.created_at.tzinfo is not None
        assert email.threat_indicators == []


@pytest.mark.postgres
@pytest.mark.parametrize("email", [" DEMO@EXAMPLE.INVALID ", "   "])
def test_user_email_uniqueness_and_nonblank_constraint(postgres_engine, email):
    seed_database(postgres_engine)
    with pytest.raises(IntegrityError), Session(postgres_engine) as session, session.begin():
        session.add(User(email=email))
        session.flush()


@pytest.mark.postgres
@pytest.mark.parametrize("confidence", [-0.01, 100.01, float("nan"), float("inf"), -float("inf")])
def test_confidence_is_a_finite_percentage(postgres_engine, confidence):
    seed_database(postgres_engine)
    with pytest.raises(IntegrityError), postgres_engine.begin() as connection:
        connection.execute(
            text("UPDATE analyzed_emails SET confidence_score=:value"), {"value": confidence}
        )


@pytest.mark.postgres
@pytest.mark.parametrize("confidence", [0, 100])
def test_confidence_accepts_percentage_boundaries(postgres_engine, confidence):
    seed_database(postgres_engine)
    with postgres_engine.begin() as connection:
        connection.execute(
            text("UPDATE analyzed_emails SET confidence_score=:value"), {"value": confidence}
        )
        assert connection.scalar(select(AnalyzedEmail.confidence_score).limit(1)) == confidence


@pytest.mark.postgres
@pytest.mark.parametrize("indicators", ["{}", "null", "[1]", "[null]", '[["urgency"]]'])
def test_indicators_require_a_json_array_of_strings(postgres_engine, indicators):
    seed_database(postgres_engine)
    with pytest.raises(IntegrityError), postgres_engine.begin() as connection:
        connection.execute(
            text("UPDATE analyzed_emails SET threat_indicators=CAST(:value AS jsonb)"),
            {"value": indicators},
        )


@pytest.mark.postgres
@pytest.mark.parametrize("column", ["raw_content", "ai_explanation"])
def test_content_and_explanation_cannot_be_blank(postgres_engine, column):
    seed_database(postgres_engine)
    with pytest.raises(IntegrityError), postgres_engine.begin() as connection:
        connection.execute(text(f"UPDATE analyzed_emails SET {column}=' '"))


@pytest.mark.postgres
def test_foreign_key_and_cascade_delete(postgres_engine):
    seed_database(postgres_engine)
    with pytest.raises(IntegrityError), postgres_engine.begin() as connection:
        connection.execute(text("UPDATE analyzed_emails SET user_id=:id"), {"id": uuid4()})
    with postgres_engine.begin() as connection:
        connection.execute(delete(User).where(User.id == DEMO_USER_ID))
        assert connection.scalar(select(func.count()).select_from(AnalyzedEmail)) == 0
