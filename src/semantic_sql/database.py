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
    def __init__(self, engine: Engine, schema: str | None = None):
        self.engine = engine
        self.schema = schema

    @classmethod
    def from_url(cls, url: str, schema: str | None = None) -> "Database":
        return cls(create_engine(url), schema)

    @property
    def dialect(self) -> str:
        """The sqlglot dialect name for this database (e.g. ``databricks``)."""
        name = self.engine.dialect.name
        return _SQLGLOT_DIALECTS.get(name, name)

    def list_tables(self) -> list[tuple[str, str | None]]:
        """Return ``(name, comment)`` for every table and view in the schema."""
        inspector = inspect(self.engine)
        names = set(inspector.get_table_names(schema=self.schema))
        names.update(_optional(inspector.get_view_names, [], schema=self.schema))
        return [(name, self._table_comment(inspector, name)) for name in sorted(names)]

    def describe_table(self, table: str) -> TableInfo:
        """Return columns, keys and comments for one table."""
        inspector = inspect(self.engine)
        columns = [
            Column(
                name=c["name"],
                type=str(c["type"]),
                nullable=bool(c.get("nullable", True)),
                comment=c.get("comment") or None,
            )
            for c in inspector.get_columns(table, schema=self.schema)
        ]
        pk = _optional(inspector.get_pk_constraint, {}, table, schema=self.schema)
        fks = _optional(inspector.get_foreign_keys, [], table, schema=self.schema)
        return TableInfo(
            name=table,
            comment=self._table_comment(inspector, table),
            columns=columns,
            primary_key=list(pk.get("constrained_columns") or []),
            foreign_keys=[
                ForeignKey(
                    columns=list(fk["constrained_columns"]),
                    referred_table=fk["referred_table"],
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

    def _table_comment(self, inspector: Any, table: str) -> str | None:
        comment = _optional(inspector.get_table_comment, {}, table, schema=self.schema)
        return comment.get("text") or None


def _optional(method: Any, default: Any, *args: Any, **kwargs: Any) -> Any:
    """Call an inspector method that some dialects do not implement."""
    try:
        return method(*args, **kwargs)
    except NotImplementedError:
        return default
