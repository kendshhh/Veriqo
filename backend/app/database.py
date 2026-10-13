"""PostgreSQL connection helpers; imports do not open a database connection."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def database_url(value: str | None = None) -> URL:
    if value is None:
        load_dotenv(PROJECT_ROOT / ".env")
        value = os.getenv("DATABASE_URL")
    if not value or not value.strip():
        raise ValueError("Set DATABASE_URL in the environment or .env.")
    try:
        url = make_url(value)
    except ArgumentError:
        raise ValueError("DATABASE_URL must be a valid PostgreSQL connection string.") from None
    if url.drivername not in {"postgres", "postgresql", "postgresql+psycopg"}:
        raise ValueError("DATABASE_URL must use PostgreSQL with the psycopg driver.")
    return url.set(drivername="postgresql+psycopg")


def make_engine(value: str | None = None) -> Engine:
    return create_engine(
        database_url(value), pool_pre_ping=True, connect_args={"connect_timeout": 5}
    )
