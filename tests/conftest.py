import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event

from semantic_sql import server
from semantic_sql.database import Database

SEED_SQL = Path(__file__).resolve().parent.parent / "demo" / "seed.sql"


@pytest.fixture
def demo_db_path(tmp_path: Path) -> Path:
    path = tmp_path / "demo.db"
    with closing(sqlite3.connect(path)) as conn:
        conn.executescript(SEED_SQL.read_text())
    return path


@pytest.fixture
def readonly_url(demo_db_path: Path) -> str:
    """SQLite opened read-only at the connection level, mirroring a read-only credential."""
    return f"sqlite:///file:{demo_db_path}?mode=ro&uri=true"


@pytest.fixture
def db(readonly_url: str) -> Database:
    return Database.from_url(readonly_url)


@pytest.fixture
def multi_schema_db(demo_db_path: Path, tmp_path: Path) -> Database:
    """Two read-only schemas: ``main`` (demo data) and an attached ``finance``."""
    finance_path = tmp_path / "finance.db"
    with closing(sqlite3.connect(finance_path)) as conn:
        conn.executescript(
            "CREATE TABLE invoices (id INTEGER PRIMARY KEY, customer_id INTEGER, amount NUMERIC);"
            "INSERT INTO invoices VALUES (1, 1, 100), (2, 2, 250);"
        )
    engine = create_engine(f"sqlite:///file:{demo_db_path}?mode=ro&uri=true")

    @event.listens_for(engine, "connect")
    def attach_finance(dbapi_connection, _record):
        dbapi_connection.execute(f"ATTACH DATABASE 'file:{finance_path}?mode=ro' AS finance")

    return Database(engine, schemas=["main", "finance"])


@pytest.fixture
def mcp_server(readonly_url: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", readonly_url)
    for name in ("DATABASE_SCHEMAS", "SEMANTIC_DIR", "MAX_ROWS", "MAX_RESULT_CHARS"):
        monkeypatch.delenv(name, raising=False)
    server.get_database.cache_clear()
    yield server.mcp
    server.get_database.cache_clear()
