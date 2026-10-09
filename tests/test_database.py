import pytest
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError

from semantic_sql.database import Database


def test_dialect(db):
    assert db.dialect == "sqlite"


def test_list_tables(db):
    assert db.list_tables() == ["customers", "orders"]


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


def test_list_tables_across_schemas_is_qualified_in_configured_order(multi_schema_db):
    assert multi_schema_db.list_tables() == ["main.customers", "main.orders", "finance.invoices"]


def test_describe_schema_qualified_table(multi_schema_db):
    info = multi_schema_db.describe_table("finance.invoices")

    assert info.name == "finance.invoices"
    assert [c.name for c in info.columns] == ["id", "customer_id", "amount"]
    assert info.primary_key == ["id"]


def test_describe_unqualified_table_uses_default_schema(multi_schema_db):
    assert multi_schema_db.describe_table("customers").primary_key == ["id"]


def test_describe_unqualified_table_uses_single_configured_schema(demo_db_path):
    db = Database.from_url(f"sqlite:///file:{demo_db_path}?mode=ro&uri=true", schemas=["main"])

    assert db.list_tables() == ["main.customers", "main.orders"]
    # Foreign key targets use the same qualified names as list_tables.
    assert db.describe_table("orders").foreign_keys[0].referred_table == "main.customers"


def test_query_across_schemas(multi_schema_db):
    result = multi_schema_db.run_query(
        "SELECT c.name, i.amount FROM main.customers c "
        "JOIN finance.invoices i ON i.customer_id = c.id ORDER BY i.id",
        max_rows=10,
    )

    assert result.rows == [("Acme Corp", 100), ("Globex", 250)]


def test_read_only_connection_blocks_writes_even_without_server_checks(db):
    """The database credential is the primary boundary; the sqlglot check is extra."""
    with pytest.raises(SQLAlchemyError, match="readonly"):
        db.run_query("DELETE FROM orders", max_rows=1)

    assert db.run_query("SELECT COUNT(*) FROM orders", max_rows=1).rows == [(24,)]
