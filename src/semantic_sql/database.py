"""Thin SQLAlchemy wrapper: schema introspection and read-only query execution.

Warehouse-specific behaviour comes only from the SQLAlchemy dialect selected by the
connection URL. Do not rely on optional dialect features (server version, isolation
levels, comments, constraints); treat them as best-effort.
"""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Engine, create_engine, inspect

# SQLAlchemy dialect name -> sqlglot dialect name, where they differ.
_SQLGLOT_DIALECTS = {"postgresql": "postgres", "mssql": "tsql"}


@dataclass(frozen=True)
class Column:
    name: str
    type: str
    nullable: bool
    comment: str | None


@dataclass(frozen=True)
class ForeignKey:
    columns: list[str]
    referred_table: str
    referred_columns: list[str]


@dataclass(frozen=True)
class TableInfo:
    name: str
    comment: str | None
    columns: list[Column]
    primary_key: list[str]
    foreign_keys: list[ForeignKey]


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[tuple[Any, ...]]
    truncated: bool


class Database:
    """A database, optionally limited to a list of schemas.

    With no schemas, the connection's default schema is used and table names are
    unqualified. With schemas, table names are qualified as ``schema.table``.
    """

    def __init__(self, engine: Engine, schemas: list[str] | None = None):
        self.engine = engine
        self.schemas = list(schemas or [])

    @classmethod
    def from_url(cls, url: str, schemas: list[str] | None = None) -> "Database":
        return cls(create_engine(url), schemas)

    @property
    def dialect(self) -> str:
        """The sqlglot dialect name for this database (e.g. ``databricks``)."""
        name = self.engine.dialect.name
        return _SQLGLOT_DIALECTS.get(name, name)

    def list_tables(self) -> list[str]:
        """Return table and view names, qualified as ``schema.table`` if schemas are set.

        Comments are deliberately not fetched here: some dialects (e.g. Databricks) need
        one round trip per table. ``describe_table`` returns them.
        """
        inspector = inspect(self.engine)
        if not self.schemas:
            return sorted(_table_and_view_names(inspector, None))
        return [
            f"{schema}.{name}"
            for schema in self.schemas
            for name in sorted(_table_and_view_names(inspector, schema))
        ]

    def describe_table(self, table: str) -> TableInfo:
        """Return columns, keys and comments for one table (``table`` or ``schema.table``)."""
        schema, name = self._split_name(table)
        inspector = inspect(self.engine)
        columns = [
            Column(
                name=c["name"],
                type=str(c["type"]),
                nullable=bool(c.get("nullable", True)),
                comment=c.get("comment") or None,
            )
            for c in inspector.get_columns(name, schema=schema)
        ]
        pk = _optional(inspector.get_pk_constraint, {}, name, schema=schema)
        fks = _optional(inspector.get_foreign_keys, [], name, schema=schema)
        comment = _optional(inspector.get_table_comment, {}, name, schema=schema)
        return TableInfo(
            name=table,
            comment=comment.get("text") or None,
            columns=columns,
            primary_key=list(pk.get("constrained_columns") or []),
            foreign_keys=[
                ForeignKey(
                    columns=list(fk["constrained_columns"]),
                    referred_table=_qualify(fk.get("referred_schema"), fk["referred_table"]),
                    referred_columns=list(fk["referred_columns"]),
                )
                for fk in fks
            ],
        )

    def run_query(self, sql: str, max_rows: int) -> QueryResult:
        """Execute SQL and fetch at most ``max_rows`` rows.

        The SQL must already have passed ``safety.prepare_query``. The transaction is
        never committed. ``exec_driver_sql`` is used so SQLAlchemy does not interpret
        colons in the SQL as bind parameters.
        """
        with self.engine.connect() as conn:
            result = conn.exec_driver_sql(sql)
            if not result.returns_rows:
                return QueryResult(columns=[], rows=[], truncated=False)
            columns = list(result.keys())
            rows = [tuple(row) for row in result.fetchmany(max_rows + 1)]
            result.close()
        return QueryResult(columns=columns, rows=rows[:max_rows], truncated=len(rows) > max_rows)

    def _split_name(self, table: str) -> tuple[str | None, str]:
        if "." in table:
            schema, name = table.rsplit(".", 1)
            return schema, name
        return (self.schemas[0] if len(self.schemas) == 1 else None), table


def _table_and_view_names(inspector: Any, schema: str | None) -> set[str]:
    names = set(inspector.get_table_names(schema=schema))
    names.update(_optional(inspector.get_view_names, [], schema=schema))
    return names


def _qualify(schema: str | None, name: str) -> str:
    return f"{schema}.{name}" if schema else name


def _optional(method: Any, default: Any, *args: Any, **kwargs: Any) -> Any:
    """Call an inspector method that some dialects do not implement."""
    try:
        return method(*args, **kwargs)
    except NotImplementedError:
        return default
