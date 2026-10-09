# AGENTS.md — Semantic SQL Agent PoC

## Overview

Build a small proof-of-concept (PoC) that allows an AI coding agent, such as Claude Code or OpenCode, to query an analytical SQL database using a simple, human-reviewable semantic layer.

The goal is **not** to build a production semantic layer or a Databricks Genie replacement.

The goal is to prove this workflow:

1. Connect to a SQL warehouse.
2. Inspect its schema.
3. Have an LLM generate a proposed semantic layer.
4. Allow a human to review/edit the semantic layer.
5. Give the semantic layer and live database schema to an AI agent.
6. Let the agent generate and execute read-only SQL.
7. Return useful results and explanations.

Keep the implementation small, obvious, and easy to modify.

---

## Core Principles

### 1. Off-the-shelf libraries, thin custom glue

The only custom code is a **small, warehouse-neutral MCP server** (a few hundred lines of Python). Everything else is an existing free library, Markdown, or a prompt.

- **No vendor MCP servers** (no Databricks/Snowflake/Google-managed MCP). One server works the same way for every warehouse.
- **Vendor code is limited to standard SQL drivers** (SQLAlchemy dialects), selected by connection URL.
- **Semantic layer:** plain Markdown in Git, read directly by the agent.
- **Semantic layer generation:** a prompt run by the coding agent itself — no custom LLM-calling code.
- **Review/approval:** Git diff and code review.

### 2. Keep it simple

A developer should be able to understand the whole project in an afternoon.

| Prefer | Avoid |
| --- | --- |
| SQLAlchemy for connections and introspection | Vendor-specific code paths |
| `sqlglot` for SQL parsing | Home-grown SQL parsers/compilers |
| Official MCP Python SDK | Agent frameworks |
| Markdown files in Git | Databases for storing metadata |
| Prompts run by the coding agent | Custom LLM-calling code |
| Database permissions for safety | Web apps, microservices, queues, Kubernetes |

### 3. Separate semantics from the physical database

**Terminology:** the *semantic layer* is the set of local Markdown files in `semantic/<dataset>/`. *Catalog* only ever means a warehouse catalog (e.g. Databricks Unity Catalog). Generating the semantic layer writes local files and never changes the database.

The semantic layer describes entities, tables, columns, relationships, metrics, business definitions, example questions and example SQL.

It must **not** be tied to a particular warehouse. Warehouse specifics live only in the connection URL and SQL dialect.

---

## Tooling

| Concern | Tool |
| --- | --- |
| Packaging / environments | `uv` + `pyproject.toml` |
| MCP server | Official MCP Python SDK |
| Connections, schema introspection, execution | SQLAlchemy + warehouse dialect (optional extras) |
| SQL parsing, SELECT-only check, `LIMIT` injection | `sqlglot` |
| Tests | pytest (against SQLite) |
| Lint / format | Ruff, `markdownlint-cli2` |
| Agent client config | `.mcp.json` (Claude Code), `opencode.json` (OpenCode) |

### Warehouses

| Warehouse | SQLAlchemy dialect package | `sqlglot` dialect | PoC status |
| --- | --- | --- | --- |
| Databricks | `databricks-sqlalchemy` | `databricks` | **Implement first** |
| SQLite | built in | `sqlite` | Local demo and tests |
| BigQuery | `sqlalchemy-bigquery` | `bigquery` | Later |
| Snowflake | `snowflake-sqlalchemy` | `snowflake` | Later |
| Redshift | `sqlalchemy-redshift` | `redshift` | Later (check SQLAlchemy version compatibility) |

Install dialects as optional extras (e.g. `uv sync --extra databricks`). Adding a warehouse should mean adding an extra and a dialect mapping — nothing else.

### Known dialect quirks

Do not assume every dialect implements every SQLAlchemy feature. For example, `databricks-sqlalchemy` does not report a server version and does not support setting `isolation_level`. The server must not depend on either.

---

## Datasets

| Dataset | Database | Schemas | Semantic layer | Status |
| --- | --- | --- | --- | --- |
| Demo | SQLite (`demo/seed.sql`) | default | `semantic/demo/` | Working |
| Harbourstone Financial | Databricks (catalog set by `DATABRICKS_CATALOG`) | `retail_banking`, `commercial_banking`, `insurance` | `semantic/harbourstone_financial/` | **Current focus** |
| Harbourstone HR / Marketing | Redshift / BigQuery | — | — | Later |

Harbourstone data is loaded into the warehouses separately; this repository neither contains nor loads it. Everything the agent knows comes from the **live schema** (via MCP) and the reviewed semantic layer. The tables use bronze/silver/gold layers, have table and column comments (including PII markers), and **no declared primary/foreign keys** — relationships are recorded in the semantic layer.

---

## Architecture

```text
                 Claude Code / OpenCode
                   |               |
        reads files|               | MCP (stdio)
                   v               v
  semantic/<dataset>/*.md     semantic-sql MCP server
         (meaning)            (schema + read-only SQL)
                                   |
                                   | SQLAlchemy + dialect
                                   v
                       Databricks / SQLite / BigQuery / ...
```

- The **semantic layer** answers *"What does 'revenue' mean?"*
- The **schema** (via MCP) answers *"Where does the data live?"*

### Workflow A: Generate the semantic layer

```text
MCP schema tools -> coding agent + prompts/generate-semantic-layer.md -> semantic/<dataset>/*.md (proposed) -> human review -> git commit
```

### Workflow B: Query the database

```text
User question
   |
   v
Claude Code / OpenCode
   +--> reads semantic/<dataset>/*.md (directory reported by list_tables)
   +--> MCP: list_tables / describe_table
   |
   v
Generated SQL -> MCP: run_query (read-only) -> Results + explanation
```

---

## Repository Structure

```text
.
├── AGENTS.md
├── README.md
├── CLAUDE.md                 # Imports AGENTS.md for Claude Code
├── pyproject.toml
├── .env.example              # Committed template; copy to .env (git-ignored)
├── .mcp.json                 # Claude Code -> semantic-sql MCP server
├── opencode.json             # OpenCode   -> semantic-sql MCP server
├── .claude/
│   ├── settings.json         # Pre-approves the three read-only MCP tools
│   └── commands/generate-semantic-layer.md
├── .opencode/commands/generate-semantic-layer.md
├── src/
│   └── semantic_sql/
│       ├── __init__.py
│       ├── server.py         # MCP tool definitions
│       ├── database.py       # Engine, introspection, execution
│       └── safety.py         # sqlglot SELECT-only check + LIMIT
├── tests/
├── semantic/
│   ├── README.md             # Semantic layer format and rules (shared by all datasets)
│   ├── demo/                 # One semantic layer per dataset, selected by SEMANTIC_DIR
│   │   ├── entities/
│   │   ├── metrics.md
│   │   ├── glossary.md
│   │   └── examples.md
│   └── harbourstone_financial/
├── prompts/
│   └── generate-semantic-layer.md
└── demo/
    └── seed.sql              # customers/orders demo data
```

Do not add modules or layers unless they are actually needed.

---

## MCP Server

### Tools

Expose a small number of tools — not dozens.

| Tool | Input | Returns |
| --- | --- | --- |
| `list_tables` | — | SQL dialect, semantic layer directory, and table/view names (`schema.table` when `DATABASE_SCHEMAS` is set) |
| `describe_table` | `table` (as shown by `list_tables`) | Columns, types, nullability, primary key, foreign keys, table/column comments |
| `run_query` | `sql` | Column names, rows, row count, whether results were truncated |

Output must be compact and LLM-friendly, for example:

```text
orders  (dialect: databricks)
  id: bigint PK
  customer_id: bigint FK -> customers.id
  total: decimal  -- Gross order value
  status: string
  created_at: timestamp
```

Prefer `describe_table` per table over dumping the entire schema into context. **Keep table and column comments** — they are valuable input for the semantic layer.

`list_tables` deliberately returns names only: some dialects (e.g. Databricks) need one round trip per table to fetch comments, which is too slow for large schemas. `describe_table` returns comments.

### Configuration

All configuration comes from environment variables. The server loads them from a git-ignored `.env` file in the working directory; `.env.example` is the committed template.

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy URL (e.g. `databricks://...`, `sqlite:///demo/demo.db`). For Databricks, `.env` builds it from `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, `DATABRICKS_CATALOG` and `DATABRICKS_TOKEN` using python-dotenv `${VAR}` expansion | required |
| `DATABASE_SCHEMAS` | Comma-separated schemas to expose; table names become `schema.table` | connection default schema |
| `SEMANTIC_DIR` | Semantic semantic layer directory for this dataset, reported by `list_tables` | `semantic` |
| `MAX_ROWS` | Maximum rows returned by `run_query` | `100` |
| `MAX_RESULT_CHARS` | Maximum size of a `run_query` response | `20000` |

- The SQL dialect is derived from the SQLAlchemy engine; do not configure it separately.
- Credentials use the normal provider mechanisms (for Databricks, a service principal via OAuth M2M; a personal access token is acceptable for the PoC).
- **Never** put credentials in source, YAML, Markdown or committed config files. Only `.env` (git-ignored) holds secrets.

---

## SQL Safety

The database connection **MUST** be read-only. The agent must never be able to execute `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `MERGE`, `GRANT` or `REVOKE`.

Safety layers, in priority order:

1. **Database permissions (primary boundary).** Use a dedicated read-only principal. For Databricks: a service principal with only `USE CATALOG`, `USE SCHEMA` and `SELECT` in Unity Catalog, plus `CAN USE` on the SQL warehouse.
2. **Server checks (defense-in-depth).** In `run_query`:
   - Parse with `sqlglot` using the engine's dialect.
   - Allow exactly **one** statement.
   - **Allow-list** read-only queries (`SELECT`, `UNION`, `WITH ... SELECT`); reject everything else, including anything that fails to parse.
   - Apply `MAX_ROWS` (add/clamp `LIMIT`, and stop fetching after `MAX_ROWS`).
   - Truncate responses larger than `MAX_RESULT_CHARS`.
3. **Warehouse settings.** Use warehouse-level statement timeouts (e.g. Databricks SQL warehouse `STATEMENT_TIMEOUT`) rather than building timeout logic.

---

## SQL Dialect

`list_tables` reports the dialect (e.g. `databricks`).

Dialect matters for date arithmetic, timestamp handling, functions, identifier quoting, casting, array/struct syntax and approximate aggregations.

Do not build a universal SQL dialect abstraction. Let the LLM generate dialect-specific SQL.

---

## Semantic Layer (Markdown)

Use Markdown because it is easy for humans and LLMs to read, edit and diff, and coding agents can read it without extra tooling.

### Rules

- One semantic layer directory per dataset: `semantic/<dataset>/`, selected by `SEMANTIC_DIR`.
- One file per entity in `<semantic-dir>/entities/` (named `<schema>.<table>.md` when names are qualified), plus `metrics.md`, `glossary.md` and `examples.md`.
- **Never copy personal or sensitive data values** into the semantic layer — it is committed to Git. Describe columns instead, and record sensitivity stated in column comments.
- Always include the **physical** table and column names in backticks.
- Every definition has a `Status:` of `proposed` or `approved`.
- Keep descriptions concise. Record ambiguities under an **Open questions** heading.
- No credentials or connection details in the semantic layer.
- The exact format can evolve. Do not over-design it.

### Example entity: `semantic/demo/entities/orders.md`

```markdown
# Order

- **Status:** proposed
- **Table:** `orders`
- **Primary key:** `id`

A purchase made by a customer.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `id` | Unique order identifier | proposed |
| `customer_id` | Customer who placed the order | proposed |
| `total` | Gross order value | proposed |
| `status` | Order status | proposed |
| `created_at` | Date the order was created | proposed |

## Relationships

- `orders.customer_id` -> `customers.id` — each order belongs to a customer.

## Open questions

- Which values can `status` take besides `completed` and `cancelled`?
```

### Example metric: `semantic/demo/metrics.md`

````markdown
## Revenue

- **Status:** proposed
- **Definition:** Revenue from completed orders. Cancelled orders are excluded.

```sql
SUM(orders.total) -- WHERE orders.status = 'completed'
```
````

### Example query: `semantic/demo/examples.md`

````markdown
## What was revenue last month?

```sql
SELECT SUM(total)
FROM orders
WHERE status = 'completed'
  AND created_at >= ...
```
````

### Inferred vs. approved

The semantic layer generated by an LLM is **not** automatically authoritative.

- Everything generated starts as `Status: proposed`.
- Humans edit the Markdown and change definitions to `Status: approved`.
- When answering questions, agents prefer `approved` definitions and must say when they rely on a `proposed` one.
- Do not build an approval system — Git and code review are sufficient.

---

## Semantic Layer Generation

There is no custom CLI or LLM code. Generation is a prompt run by the coding agent, exposed as a `/generate-semantic-layer` slash command (`.claude/commands/` and `.opencode/commands/`) that tells the agent to follow `prompts/generate-semantic-layer.md`:

```text
/generate-semantic-layer
```

The agent should:

1. Use `list_tables` and `describe_table` to inspect the schema.
2. Propose table/column descriptions, entities, relationships, metrics, business terminology, example questions and example SQL.
3. Write the result to the semantic layer directory reported by `list_tables`, following the [semantic layer format](#semantic-layer-markdown).
4. Mark everything as `Status: proposed`.

### Prompt requirements

`prompts/generate-semantic-layer.md` must tell the agent that:

- It is inspecting an unfamiliar database.
- It must not invent facts.
- It should distinguish observations from guesses.
- It should use actual schema relationships and comments when available.
- For large or layered datasets, it should cover gold tables first, then silver, and describe bronze briefly.
- When no foreign keys are declared, it should infer relationships from column names and mark them as inferred.
- It must never copy personal or sensitive data values into the semantic layer.
- It may propose useful definitions, but those require human review.
- It should prefer concise descriptions.
- It must follow the Markdown semantic layer format.
- It must include the underlying physical table/column names.
- It should list ambiguities under **Open questions**.
- It must only run small, read-only sampling queries, if any.

Example prompt:

```text
You are analyzing an unfamiliar analytical database.

Your job is to create a proposed semantic layer as Markdown files in the semantic layer directory reported by list_tables.

Use the database schema from the MCP tools as your primary source of truth.

Do not invent business definitions that cannot reasonably be inferred.

When something is uncertain, mark it as proposed and record it under "Open questions".

Identify:
- important entities
- important tables
- columns
- relationships
- likely metrics
- useful business concepts
- example questions
- example SQL

The result will be reviewed by a human before being used.
```

### Human review

The PoC does **not** need a UI:

```bash
git diff semantic/<dataset>/
# review, edit, change Status to approved where appropriate
git commit
```

---

## Query Workflow

When the agent receives a question such as:

> How much revenue did we generate last quarter by customer segment?

it should:

1. Read the relevant files in the semantic layer directory reported by `list_tables` (metrics, entities, examples).
2. Use `describe_table` to confirm the tables and columns it needs.
3. Identify the required joins.
4. Generate dialect-specific SQL.
5. Execute it with `run_query`.
6. Inspect errors/results and correct the SQL if necessary.
7. Return the result, the SQL used, and which semantic definitions (and their status) it relied on.

---

## Testing

The normal test suite must **not** require a live warehouse. Use SQLite and the demo dataset.

At minimum, test:

- `list_tables` and `describe_table` output (including PK/FK and comments where SQLite allows).
- Multiple schemas (`DATABASE_SCHEMAS`), using SQLite `ATTACH DATABASE`.
- `run_query` returns columns, rows and row count.
- `MAX_ROWS` and `MAX_RESULT_CHARS` are enforced.
- Mutating and non-`SELECT` statements are rejected (`INSERT`, `DELETE`, `DROP`, `MERGE`, `GRANT`, …).
- Multiple statements are rejected.
- Unparseable SQL is rejected.
- The safety check parses Databricks-dialect SQL correctly (pure `sqlglot`, no connection needed).
- MCP tools are registered and callable.

Also run `ruff check`, `ruff format --check` and `markdownlint-cli2` on Markdown.

### Example demo database

```text
customers            orders
---------            ------
id                   id
name                 customer_id
segment              total
created_at           status
                     created_at
```

- **Relationship:** `orders.customer_id -> customers.id`
- **Metric:** `revenue = SUM(orders.total) WHERE orders.status = 'completed'`

---

## End-to-End Demo

The README should eventually demonstrate:

```console
$ sqlite3 demo/demo.db < demo/seed.sql
$ cp .env.example .env     # demo block: DATABASE_URL + SEMANTIC_DIR=semantic/demo

# In Claude Code / OpenCode (MCP server configured in .mcp.json / opencode.json):
> /generate-semantic-layer

$ git diff semantic/demo/   # review, edit, approve
$ git commit

> What was revenue by customer segment last month?
```

Then point `DATABASE_URL` at Databricks and ask the same question **without changing the semantic layer** (assuming the same logical tables exist).

---

## What NOT to Build

Do **not** build:

- Integrations with vendor-managed MCP servers
- A CLI beyond starting the MCP server
- Custom LLM-calling code
- A web dashboard or React frontend
- A hosted SaaS application
- Authentication or multi-tenancy
- A metadata database
- A complex semantic compiler or proprietary query language
- Automatic business-definition approval
- A vector database or RAG infrastructure (unless a real problem appears)
- An elaborate agent framework
- Support for every warehouse immediately
- Production-grade orchestration

The Python code should stay at a few hundred lines.

---

## Future Direction

If the PoC works, possible future improvements include:

- More warehouses (BigQuery, Snowflake, Redshift via dialect extras)
- Better semantic metric definitions
- Column/value profiling
- Query examples generated from actual data
- SQL cost estimation
- Automatic discovery of common joins
- Automated semantic layer reference checking
- Human review UI
- Query/evaluation test suites
- Business glossary
- Metric definitions that compile into dialect-specific SQL

None of these should be implemented until the basic workflow works.

---

## Definition of Done

The PoC is successful when:

- [ ] 1. The MCP server connects to Databricks with a read-only service principal.
- [ ] 2. The agent discovers the schema through `list_tables` / `describe_table`.
- [ ] 3. The agent generates a proposed Markdown semantic layer.
- [ ] 4. A human reviews/edits the semantic layer in Git.
- [ ] 5. Claude Code or OpenCode is connected to the MCP server.
- [ ] 6. A natural-language analytical question is asked.
- [ ] 7. The agent reads the semantic definitions.
- [ ] 8. The agent reads the database schema.
- [ ] 9. The agent generates valid Databricks SQL.
- [ ] 10. The SQL executes read-only.
- [ ] 11. The agent explains the result and the definitions it used.
- [ ] 12. Mutating SQL is rejected by both the server and the database.

**The most important demonstration:** the same semantic layer, MCP server and agent workflow remain unchanged when `DATABASE_URL` is switched between warehouses (SQLite -> Databricks, later others).

Keep everything boring, explicit, and easy to replace.
