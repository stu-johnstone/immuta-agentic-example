import pytest
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError


def test_dialect(db):
    assert db.dialect == "sqlite"


def test_list_tables(db):
    assert db.list_tables() == [("customers", None), ("orders", None)]


def test_describe_table(db):
    info = db.describe_table("orders")

    assert [c.name for c in info.columns] == ["id", "customer_id", "total", "status", "created_at"]
    assert info.primary_key == ["id"]
    assert len(info.foreign_keys) == 1
    fk = info.foreign_keys[0]
    assert (fk.columns, fk.referred_table, fk.referred_columns) == (
        ["customer_id"],
        "customers",
        ["id"],
    )
    status = next(c for c in info.columns if c.name == "status")
    assert status.nullable is False


def test_describe_missing_table(db):
    with pytest.raises(NoSuchTableError):
        db.describe_table("nope")


def test_run_query(db):
    result = db.run_query("SELECT id, status FROM orders ORDER BY id LIMIT 2", max_rows=10)

    assert result.columns == ["id", "status"]
    assert result.rows == [(1, "completed"), (2, "completed")]
    assert result.truncated is False


def test_run_query_truncates_at_max_rows(db):
    result = db.run_query("SELECT id FROM orders", max_rows=3)

    assert len(result.rows) == 3
    assert result.truncated is True


def test_colons_are_not_bind_parameters(db):
    assert db.run_query("SELECT '10:30' AS t, ':name' AS u", max_rows=1).rows == [
        ("10:30", ":name")
    ]


def test_read_only_connection_blocks_writes_even_without_server_checks(db):
    """The database credential is the primary boundary; the sqlglot check is extra."""
    with pytest.raises(SQLAlchemyError, match="readonly"):
        db.run_query("DELETE FROM orders", max_rows=1)

    assert db.run_query("SELECT COUNT(*) FROM orders", max_rows=1).rows == [(24,)]
