# Generate the Semantic Catalog

You are analyzing an unfamiliar analytical database. Your job is to create a **proposed** semantic catalog as Markdown files in `semantic/`.

The result will be reviewed by a human before being used.

## Steps

1. Call `list_tables` to see the tables, their comments and the SQL dialect.
2. Call `describe_table` for each relevant table.
3. Optionally run a few **small, read-only** sampling queries with `run_query` (for example, `SELECT DISTINCT status FROM orders LIMIT 20`) to understand values. Do not scan large tables.
4. Write the catalog following the format in [`semantic/README.md`](../semantic/README.md):
   - `semantic/entities/<table>.md` — one file per important table
   - `semantic/metrics.md` — likely metrics
   - `semantic/glossary.md` — business terms that can reasonably be inferred
   - `semantic/examples.md` — example questions with SQL in the reported dialect
5. Summarise what you created and list the main open questions for the reviewer.

## Rules

- Use the database schema (tables, columns, keys, comments) as your primary source of truth.
- Do **not** invent facts or business definitions that cannot reasonably be inferred.
- Distinguish observations (from the schema or data) from guesses.
- Use actual foreign keys and comments when available; otherwise mark inferred relationships as guesses.
- Mark **every** definition as `Status: proposed`. Never mark anything `approved`.
- Always include physical table and column names in backticks.
- Prefer concise descriptions.
- Record ambiguities under an **Open questions** heading.
- Check that every example SQL query runs successfully with `run_query`.
- If `semantic/` already contains files, update them rather than overwriting human edits, and never change `approved` definitions.

Identify:

- important entities
- important tables
- columns
- relationships
- likely metrics
- useful business concepts
- example questions
- example SQL
