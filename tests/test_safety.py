import pytest

from semantic_sql.safety import UnsafeQueryError, prepare_query


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM orders",
        "select id from orders where status = 'completed'",
        "WITH c AS (SELECT customer_id, SUM(total) AS t FROM orders GROUP BY 1) SELECT * FROM c",
        "SELECT id FROM orders UNION ALL SELECT id FROM customers",
        "(SELECT 1)",
        "SELECT '10:30' AS t",
    ],
)
def test_allows_read_only_queries(sql):
    assert prepare_query(sql, "sqlite", max_rows=100)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM main.sales.orders",
        "SELECT `order id` FROM `main`.`sales`.`orders`",
        "SELECT date_trunc('MONTH', created_at) AS m, count(*) FROM orders GROUP BY 1",
        "SELECT *, row_number() OVER (PARTITION BY customer_id ORDER BY created_at) AS rn "
        "FROM orders QUALIFY rn = 1",
        "SELECT explode(array(1, 2, 3)) AS x",
    ],
)
def test_allows_databricks_queries(sql):
    assert prepare_query(sql, "databricks", max_rows=100)


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO orders (id) VALUES (1)",
        "UPDATE orders SET total = 0",
        "DELETE FROM orders",
        "DROP TABLE orders",
        "ALTER TABLE orders ADD COLUMN x INT",
        "CREATE TABLE x AS SELECT * FROM orders",
        "TRUNCATE TABLE orders",
        "MERGE INTO orders t USING s ON t.id = s.id WHEN MATCHED THEN DELETE",
        "GRANT SELECT ON TABLE orders TO `someone`",
        "REVOKE SELECT ON TABLE orders FROM `someone`",
        "OPTIMIZE orders",
        "VACUUM orders",
        "SET spark.sql.ansi.enabled = false",
        "USE CATALOG other",
        "INSERT OVERWRITE TABLE orders SELECT * FROM orders",
    ],
)
def test_rejects_non_queries(sql):
    with pytest.raises(UnsafeQueryError):
        prepare_query(sql, "databricks", max_rows=100)


@pytest.mark.parametrize(
    "sql",
    [
        "WITH d AS (DELETE FROM orders RETURNING *) SELECT * FROM d",
        "SELECT * INTO orders_copy FROM orders",
    ],
)
def test_rejects_writes_hidden_inside_queries(sql):
    with pytest.raises(UnsafeQueryError):
        prepare_query(sql, "postgres", max_rows=100)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1; DROP TABLE orders",
        "SELECT 1; SELECT 2",
    ],
)
def test_rejects_multiple_statements(sql):
    with pytest.raises(UnsafeQueryError, match="exactly one statement"):
        prepare_query(sql, "sqlite", max_rows=100)


@pytest.mark.parametrize("sql", ["", "   ", ";", "SELEC * FRM orders", "SELECT FROM WHERE ("])
def test_rejects_empty_or_unparseable_sql(sql):
    with pytest.raises(UnsafeQueryError):
        prepare_query(sql, "sqlite", max_rows=100)


def test_adds_limit_one_above_max_rows():
    assert prepare_query("SELECT * FROM orders", "sqlite", max_rows=10) == (
        "SELECT * FROM orders LIMIT 11"
    )


def test_clamps_large_limit():
    assert prepare_query("SELECT * FROM orders LIMIT 5000", "sqlite", max_rows=10) == (
        "SELECT * FROM orders LIMIT 11"
    )


def test_limits_set_operations():
    sql = prepare_query("SELECT id FROM orders UNION SELECT id FROM customers", "sqlite", 10)
    assert sql.endswith("LIMIT 11")


def test_keeps_small_limit_and_original_sql():
    sql = "SELECT  id FROM orders  LIMIT 5;"
    assert prepare_query(sql, "sqlite", max_rows=10) == "SELECT  id FROM orders  LIMIT 5"
