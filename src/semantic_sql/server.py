"""MCP server exposing schema introspection and read-only SQL to coding agents."""

import functools
import os
import sys

from dotenv import find_dotenv, load_dotenv
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError

from semantic_sql.database import Database, QueryResult, TableInfo
from semantic_sql.safety import UnsafeQueryError, prepare_query

DEFAULT_MAX_ROWS = 100
DEFAULT_MAX_RESULT_CHARS = 20_000
DEFAULT_SEMANTIC_DIR = "semantic"

INSTRUCTIONS = """\
Read-only access to an analytical SQL database.
Call list_tables first: it reports the SQL dialect and the semantic layer directory
(local Markdown files). Before writing SQL, read them (metrics, entities, examples) and prefer
definitions with Status: approved. Use describe_table to confirm columns.
Use table names exactly as list_tables shows them (schema-qualified if shown that way).
"""

READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False)

mcp = MCPServer("semantic-sql", instructions=INSTRUCTIONS)


@functools.cache
def get_database() -> Database:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ToolError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")
    schemas = [s.strip() for s in os.environ.get("DATABASE_SCHEMAS", "").split(",") if s.strip()]
    return Database.from_url(url, schemas=schemas)


def semantic_dir() -> str:
    return (os.environ.get("SEMANTIC_DIR") or DEFAULT_SEMANTIC_DIR).rstrip("/")


@mcp.tool(annotations=READ_ONLY)
def list_tables() -> str:
    """List tables and views, the SQL dialect, and the semantic layer directory (local Markdown)."""
    db = get_database()
    try:
        tables = db.list_tables()
    except SQLAlchemyError as e:
        raise ToolError(f"Could not list tables: {_error_message(e)}") from e
    return format_tables(db.dialect, semantic_dir(), tables)


@mcp.tool(annotations=READ_ONLY)
def describe_table(table: str) -> str:
    """Describe one table: columns, types, nullability, keys, relationships and comments.

    Pass the table name exactly as list_tables shows it (e.g. ``schema.table``).
    """
    db = get_database()
    try:
        info = db.describe_table(table)
    except NoSuchTableError as e:
        raise ToolError(f"Table not found: {table}. Use list_tables to see table names.") from e
    except SQLAlchemyError as e:
        raise ToolError(f"Could not describe {table}: {_error_message(e)}") from e
    return format_table(db.dialect, info)


@mcp.tool(annotations=READ_ONLY)
def run_query(sql: str) -> str:
    """Run one read-only SQL query (SELECT/WITH/UNION) and return the results.

    Results are limited to MAX_ROWS rows; aggregate or filter rather than fetching raw rows.
    """
    db = get_database()
    max_rows = _int_env("MAX_ROWS", DEFAULT_MAX_ROWS)
    try:
        prepared = prepare_query(sql, db.dialect, max_rows)
    except UnsafeQueryError as e:
        raise ToolError(f"Query rejected: {e}") from e
    try:
        result = db.run_query(prepared, max_rows)
    except SQLAlchemyError as e:
        raise ToolError(f"Query failed: {_error_message(e)}") from e

    text = format_result(result)
    if prepared != sql.strip().rstrip(";").strip():
        text = f"-- executed: {prepared}\n{text}"
    return truncate(text, _int_env("MAX_RESULT_CHARS", DEFAULT_MAX_RESULT_CHARS))


def format_tables(dialect: str, semantic_layer_dir: str, tables: list[str]) -> str:
    lines = [
        f"dialect: {dialect}",
        f"semantic layer (local Markdown files): {semantic_layer_dir}/",
        "tables:",
    ]
    lines += [f"  {name}" for name in tables]
    return "\n".join(lines)


def format_table(dialect: str, info: TableInfo) -> str:
    references = {
        column: f"{fk.referred_table}.{referred}"
        for fk in info.foreign_keys
        for column, referred in zip(fk.columns, fk.referred_columns, strict=False)
    }
    lines = [f"{info.name}  (dialect: {dialect})"]
    if info.comment:
        lines.append(f"  -- {info.comment}")
    for col in info.columns:
        line = f"  {col.name}: {col.type}"
        if col.name in info.primary_key:
            line += " PK"
        if col.name in references:
            line += f" FK -> {references[col.name]}"
        if not col.nullable and col.name not in info.primary_key:
            line += " NOT NULL"
        if col.comment:
            line += f"  -- {col.comment}"
        lines.append(line)
    return "\n".join(lines)


def format_result(result: QueryResult) -> str:
    if not result.columns:
        return "(no result set)"
    lines = ["\t".join(result.columns)]
    lines += ["\t".join(_cell(value) for value in row) for row in result.rows]
    if result.truncated:
        lines.append(f"({len(result.rows)} rows shown; more available - aggregate or filter)")
    else:
        lines.append(f"({len(result.rows)} rows)")
    return "\n".join(lines)


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... (output truncated at {max_chars} characters)"


def _cell(value: object) -> str:
    if value is None:
        return "NULL"
    return str(value).replace("\t", " ").replace("\n", " ")


def _error_message(error: SQLAlchemyError) -> str:
    return str(getattr(error, "orig", None) or error)


def _int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    return int(value) if value else default


def main() -> None:
    load_dotenv(find_dotenv(usecwd=True))
    if not os.environ.get("DATABASE_URL"):
        sys.exit("semantic-sql: DATABASE_URL is not set. Copy .env.example to .env and fill it in.")
    mcp.run()


if __name__ == "__main__":
    main()
