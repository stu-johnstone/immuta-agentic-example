"""Defense-in-depth checks for agent-generated SQL.

The primary safety boundary is a read-only database credential. This module only
rejects SQL that is not obviously a single read-only query, and caps the row count.
"""

import sqlglot
from sqlglot import exp
from sqlglot.errors import SqlglotError

# Nodes that must not appear anywhere in a query, including inside CTEs/subqueries.
_FORBIDDEN_NODES = (
    exp.DML,  # INSERT, UPDATE, DELETE, MERGE, COPY
    exp.DDL,  # CREATE, ...
    exp.Drop,
    exp.Alter,
    exp.TruncateTable,
    exp.Grant,
    exp.Revoke,
    exp.Into,  # SELECT ... INTO creates a table
    exp.Command,  # anything sqlglot could not parse into a known statement
    exp.Set,
    exp.Use,
)


class UnsafeQueryError(ValueError):
    """Raised when SQL is rejected before reaching the database."""


def prepare_query(sql: str, dialect: str, max_rows: int) -> str:
    """Validate that ``sql`` is a single read-only query and cap its row count.

    Returns SQL to execute. If the query has no ``LIMIT``, or a ``LIMIT`` larger than
    ``max_rows``, it is rewritten with ``LIMIT max_rows + 1`` so the caller can detect
    truncation. Otherwise the original SQL is returned unchanged.
    """
    sql = sql.strip().rstrip(";").strip()
    if not sql:
        raise UnsafeQueryError("Empty query.")

    try:
        statements = [s for s in sqlglot.parse(sql, read=dialect) if s is not None]
    except SqlglotError as e:
        raise UnsafeQueryError(f"Could not parse SQL as {dialect}: {e}") from e

    if len(statements) != 1:
        raise UnsafeQueryError(f"Expected exactly one statement, got {len(statements)}.")

    query = statements[0]
    if not isinstance(query, exp.Query):
        raise UnsafeQueryError(
            f"Only read-only queries (SELECT/WITH/UNION) are allowed, got {query.key.upper()}."
        )

    for node in query.walk():
        if isinstance(node, _FORBIDDEN_NODES):
            raise UnsafeQueryError(f"Query contains a forbidden {node.key.upper()} clause.")

    limit = _literal_limit(query)
    if limit is not None and limit <= max_rows:
        return sql
    return query.limit(max_rows + 1).sql(dialect=dialect)


def _literal_limit(query: exp.Query) -> int | None:
    limit = query.args.get("limit")
    if isinstance(limit, exp.Limit) and isinstance(limit.expression, exp.Literal):
        try:
            return int(limit.expression.this)
        except ValueError:
            return None
    return None
