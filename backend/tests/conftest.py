"""
Test configuration: overrides database to SQLite for isolated, fast tests.

SQLite + aiosqlite avoids asyncpg connection conflicts. The production app
uses PostgreSQL; tests use SQLite with compatible type compilation.
"""

import os
import json

# Override BEFORE any app code imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.types import TypeDecorator, CHAR, Text
from sqlalchemy.ext.compiler import compiles
import sqlalchemy.types as types
import uuid as _uuid


# ---- SQLite-compatible type overrides ----


class SQLiteJSONB(TypeDecorator):
    """Store JSONB as TEXT in SQLite."""
    impl = types.Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


class SQLiteUUID(TypeDecorator):
    """Store UUID as VARCHAR in SQLite."""
    impl = CHAR(32)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value).replace("-", "")
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return _uuid.UUID(value)
        return None


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(element, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def _compile_uuid_sqlite(element, compiler, **kw):
    return "VARCHAR(32)"


# Enable foreign keys
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


# ---- Test fixtures ----

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.database import engine, Base, async_session_factory, get_db
from app.main import app


@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_database():
    """Create all tables once per test session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    """Clean all data between tests."""
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def db_session():
    """Provide a DB session with dependency override for the app."""
    async with async_session_factory() as session:
        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        try:
            yield session
        finally:
            app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(db_session):
    """HTTP client sharing the test DB session."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
