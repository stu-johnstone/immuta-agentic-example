import asyncio

from mcp import Client

from semantic_sql import server


def call(mcp_server, tool, arguments=None):
    async def go():
        async with Client(mcp_server) as client:
            return await client.call_tool(tool, arguments or {})

    return asyncio.run(go())


def text_of(result) -> str:
    return "\n".join(c.text for c in result.content)


def test_tools_are_registered_and_read_only(mcp_server):
    async def go():
        async with Client(mcp_server) as client:
            return (await client.list_tools()).tools

    tools = {t.name: t for t in asyncio.run(go())}

    assert set(tools) == {"list_tables", "describe_table", "run_query"}
    assert all(t.annotations.read_only_hint for t in tools.values())


def test_list_tables(mcp_server):
    result = call(mcp_server, "list_tables")

    assert not result.is_error
    assert text_of(result).splitlines() == [
        "dialect: sqlite",
        "semantic layer (local Markdown files): semantic/",
        "tables:",
        "  customers",
        "  orders",
    ]


def test_list_tables_reports_configured_schemas_and_semantic_dir(mcp_server, monkeypatch):
    monkeypatch.setenv("DATABASE_SCHEMAS", " main , ")
    monkeypatch.setenv("SEMANTIC_DIR", "semantic/demo/")
    server.get_database.cache_clear()

    result = call(mcp_server, "list_tables")

    assert text_of(result).splitlines() == [
        "dialect: sqlite",
        "semantic layer (local Markdown files): semantic/demo/",
        "tables:",
        "  main.customers",
        "  main.orders",
    ]
    described = call(mcp_server, "describe_table", {"table": "main.orders"})
    assert not described.is_error
    assert text_of(described).startswith("main.orders  (dialect: sqlite)")


def test_describe_table(mcp_server):
    result = call(mcp_server, "describe_table", {"table": "orders"})

    assert not result.is_error
    text = text_of(result)
    assert text.startswith("orders  (dialect: sqlite)")
    assert "  id: INTEGER PK" in text
    assert "  customer_id: INTEGER FK -> customers.id NOT NULL" in text


def test_describe_missing_table(mcp_server):
    result = call(mcp_server, "describe_table", {"table": "nope"})

    assert result.is_error
    assert "Table not found: nope" in text_of(result)


def test_run_query_revenue_by_segment(mcp_server):
    sql = """
        SELECT c.segment, SUM(o.total) AS revenue
        FROM orders o JOIN customers c ON c.id = o.customer_id
        WHERE o.status = 'completed'
          AND o.created_at >= '2026-09-01' AND o.created_at < '2026-10-01'
        GROUP BY c.segment
        ORDER BY c.segment
    """
    result = call(mcp_server, "run_query", {"sql": sql})

    assert not result.is_error
    lines = text_of(result).splitlines()
    assert lines[0].startswith("-- executed:")  # LIMIT was added
    assert lines[1:] == [
        "segment\trevenue",
        "Consumer\t109.5",
        "Enterprise\t31850",
        "SMB\t6280",
        "(3 rows)",
    ]


def test_run_query_rejects_mutations(mcp_server):
    result = call(mcp_server, "run_query", {"sql": "DELETE FROM orders"})

    assert result.is_error
    assert "Query rejected" in text_of(result)


def test_run_query_returns_database_errors_to_the_agent(mcp_server):
    result = call(mcp_server, "run_query", {"sql": "SELECT no_such_column FROM orders"})

    assert result.is_error
    assert "Query failed" in text_of(result)
    assert "no_such_column" in text_of(result)


def test_run_query_enforces_max_rows(mcp_server, monkeypatch):
    monkeypatch.setenv("MAX_ROWS", "5")

    result = call(mcp_server, "run_query", {"sql": "SELECT id FROM orders ORDER BY id"})

    lines = text_of(result).splitlines()
    assert lines[0] == "-- executed: SELECT id FROM orders ORDER BY id LIMIT 6"
    assert lines[1:] == [
        "id",
        "1",
        "2",
        "3",
        "4",
        "5",
        "(5 rows shown; more available - aggregate or filter)",
    ]


def test_run_query_enforces_max_result_chars(mcp_server, monkeypatch):
    monkeypatch.setenv("MAX_RESULT_CHARS", "50")

    result = call(mcp_server, "run_query", {"sql": "SELECT * FROM orders LIMIT 20"})

    text = text_of(result)
    assert text.endswith("... (output truncated at 50 characters)")
    assert len(text) < 100


def test_missing_database_url(mcp_server, monkeypatch):
    monkeypatch.delenv("DATABASE_URL")
    server.get_database.cache_clear()

    result = call(mcp_server, "list_tables")

    assert result.is_error
    assert "DATABASE_URL is not set" in text_of(result)
