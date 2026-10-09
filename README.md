# Semantic SQL Agent PoC

Let Claude Code or OpenCode answer analytical questions against a SQL warehouse, using a human-reviewed Markdown semantic layer and a small read-only MCP server.

See [`AGENTS.md`](AGENTS.md) for the design.

## How it works

- `semantic/` — Markdown business definitions (what "revenue" means). Reviewed in Git.
- `semantic-sql` MCP server — three read-only tools: `list_tables`, `describe_table`, `run_query`. Works with any SQLAlchemy dialect; Databricks and SQLite are set up.
- `prompts/generate-catalog.md` — prompt the agent follows to draft the semantic catalog.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and `sqlite3`.

```bash
uv sync --extra databricks
cp .env.example .env            # then edit .env
sqlite3 demo/demo.db < demo/seed.sql
```

`.env` is git-ignored. Set `DATABASE_URL` there:

- **Local demo:** the default in `.env.example` (read-only SQLite).
- **Databricks:** use the `databricks://` template in `.env.example`, with a **read-only** service principal or token.

The MCP server is configured for Claude Code in `.mcp.json` and for OpenCode in `opencode.json`. Start the agent from the repository root so it picks up `.env`.

## Demo

In Claude Code or OpenCode:

```text
> Follow prompts/generate-catalog.md
```

Review the proposed catalog, edit it, and change `Status: proposed` to `Status: approved` where you agree:

```bash
git diff semantic/
git add semantic/ && git commit
```

Then ask a question:

```text
> What was revenue by customer segment last month?
```

Switch `DATABASE_URL` to Databricks and ask again — `semantic/` does not change (assuming the same logical tables exist).

## Safety

1. **Read-only credentials** are the real boundary. For Databricks, grant the service principal only `USE CATALOG`, `USE SCHEMA` and `SELECT`, plus `CAN USE` on the SQL warehouse. Set a statement timeout on the warehouse.
2. The server also rejects anything that is not a single `SELECT`/`WITH`/`UNION` query (parsed with `sqlglot`), caps rows (`MAX_ROWS`) and output size (`MAX_RESULT_CHARS`), and never commits.

## Development

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
npx markdownlint-cli2 "**/*.md"
```

Tests use SQLite only; no warehouse is needed.
