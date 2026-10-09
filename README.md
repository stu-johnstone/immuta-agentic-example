# Semantic SQL Agent PoC

Let OpenCode (or Claude Code) answer analytical questions against a SQL warehouse, using a human-reviewed Markdown semantic layer and a small read-only MCP server.

See [`AGENTS.md`](AGENTS.md) for the design.

## How it works

- `semantic-sql` MCP server — three read-only tools the agent can call: `list_tables`, `describe_table`, `run_query`. Works with any SQLAlchemy dialect; Databricks and SQLite are set up.
- `semantic/<dataset>/` — Markdown business definitions (what "revenue" means), one semantic layer per dataset. Reviewed in Git.
- `/generate-semantic-layer` — a slash command that makes the agent draft that semantic layer for you (instructions in [`prompts/generate-semantic-layer.md`](prompts/generate-semantic-layer.md)).

## One-time setup

Requires [uv](https://docs.astral.sh/uv/), `sqlite3`, and [OpenCode](https://opencode.ai) (or Claude Code).

```bash
uv sync --extra databricks
cp .env.example .env                    # skip if .env already exists
sqlite3 demo/demo.db < demo/seed.sql    # local demo data
```

## Choose a dataset

`.env` (git-ignored) decides which database the agent talks to. Enable exactly one block in it:

| Block | What to fill in |
| --- | --- |
| **Local demo** (SQLite) | Nothing |
| **Harbourstone Financial** (Databricks) | `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, `DATABRICKS_CATALOG`, `DATABRICKS_TOKEN` |

For Harbourstone, the data must already be loaded into your Databricks catalog (this repository does not load it). Use a **read-only** token: `USE CATALOG` on the catalog, `USE SCHEMA` and `SELECT` on the three schemas, and `CAN USE` on the SQL warehouse.

> The MCP server reads `.env` when it starts. After editing `.env`, quit and restart OpenCode (or Claude Code).

## Demo, step by step

Everything below is typed into the agent's chat, not into a shell, unless it says otherwise.

### 1. Start OpenCode in this folder

In a terminal, from the repository root, check the MCP server first, then start OpenCode:

```bash
opencode mcp list    # should show: ✓ semantic-sql connected
opencode
```

OpenCode starts the `semantic-sql` server automatically from `opencode.json` — there is nothing to approve. If it is not connected, check `.env`.

### 2. Check the connection

```text
What tables can you see?
```

The agent calls `list_tables`. You should see the SQL dialect (`sqlite` or `databricks`), the semantic layer folder (`semantic/demo/` or `semantic/harbourstone_financial/`), and the table names.

### 3. Draft the semantic layer

The **semantic layer** is a set of local Markdown files in `semantic/<dataset>/` that explain the data in business terms (what "revenue" or "loss ratio" means, how tables join). This step writes those files on your machine. It does **not** change anything in Databricks, and it has nothing to do with Databricks catalogs. On the first run the folder does not exist yet — the agent creates it.

Make sure OpenCode is in **Build** mode (press `Tab` to switch) — Plan mode cannot write files. Then type:

```text
/generate-semantic-layer
```

This slash command (`.opencode/commands/generate-semantic-layer.md`) tells the agent to follow [`prompts/generate-semantic-layer.md`](prompts/generate-semantic-layer.md). The agent will:

1. List and describe the tables in the live database (table and column comments are used as descriptions).
2. Run a few small read-only queries to see code values (for example, the possible `status` values).
3. Write Markdown files into the semantic layer folder: `entities/`, `metrics.md`, `glossary.md` and `examples.md`. Every definition is marked `Status: proposed`.
4. Finish with a summary and a list of open questions for you.

OpenCode does not ask before tool calls or file edits by default, so it writes the files directly — you review them in step 4. (It does block reading `.env` by default, so the agent never sees your token.) For a large dataset like Harbourstone (63 tables) this step takes a while.

Without the slash command, typing `Read prompts/generate-semantic-layer.md and follow its instructions` does the same thing.

> **Using Claude Code instead?** Run `claude`, approve the `semantic-sql` server when asked, and check it with `/mcp`. `/generate-semantic-layer` works the same (`.claude/commands/`). Claude Code asks before writing files; the three read-only database tools are pre-approved in `.claude/settings.json`.

### 4. Review the semantic layer (in your editor and a shell)

Open the new files in `semantic/<dataset>/`, correct anything wrong, answer the open questions, and change `Status: proposed` to `Status: approved` for definitions you agree with. Then:

```bash
git diff semantic/
git add semantic/ && git commit -m "Review semantic layer"
```

### 5. Ask questions

Back in the agent, ask in plain English. For the local demo:

```text
What was revenue by customer segment last month?
```

For Harbourstone, for example:

```text
What is the loss ratio by product over the last 12 months, and why is the worst one so high?
Which high-risk borrowers have collateral cover below 1x?
How much cash was deposited at branches in the last 7 days, by region?
```

For each question the agent reads the semantic layer, checks the tables, writes SQL, runs it read-only, and answers — including the SQL it ran and which definitions (approved or proposed) it relied on.

### 6. Switch datasets

Enable the other block in `.env`, restart the agent, and repeat. The server, slash command and workflow do not change.

## Safety

1. **Read-only credentials** are the real boundary. For Databricks, grant the token's principal only `USE CATALOG`, `USE SCHEMA` and `SELECT`, plus `CAN USE` on the SQL warehouse. Set a statement timeout on the warehouse.
2. The server also rejects anything that is not a single `SELECT`/`WITH`/`UNION` query (parsed with `sqlglot`), caps rows (`MAX_ROWS`) and output size (`MAX_RESULT_CHARS`), and never commits.
3. The semantic layer generator is told never to copy personal data values into `semantic/`, because it is committed to Git.

## Development

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
npx markdownlint-cli2 "**/*.md"
```

Tests use SQLite only; no warehouse is needed.
