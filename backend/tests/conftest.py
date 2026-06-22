"""Test configuration: override database to use SQLite for CI/offline testing."""

import os

# Override database URL BEFORE any app imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.types import TypeDecorator, Text
import sqlalchemy.types as types
import json


class SQLiteJSONB(TypeDecorator):
    """SQLite-compatible JSONB implementation that stores as TEXT."""
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


# Register JSONB compilation for SQLite
from sqlalchemy.ext.compiler import compiles


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(element, compiler, **kw):
    return "TEXT"


# Enable foreign keys for SQLite
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
