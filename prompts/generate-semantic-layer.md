# Generate the Semantic Layer

> **What this does:** writes **local Markdown files** in this repository that describe the connected database in business terms. It does **not** change the database — all database access is read-only. It has nothing to do with warehouse catalogs (such as Databricks Unity Catalog).

You are analyzing an unfamiliar analytical database. Your job is to create a **proposed** semantic layer: Markdown files in the directory that `list_tables` reports as `semantic layer (local Markdown files)` — referred to below as `<semantic-dir>`.

If `<semantic-dir>` does not exist yet, create it. That is normal on the first run.

The result will be reviewed by a human before being used.

## Steps

1. Call `list_tables` to see the tables, the SQL dialect and `<semantic-dir>`.
2. Call `describe_table` for the relevant tables. Table and column comments are often the best description available.
3. Optionally run a few **small, read-only** sampling queries with `run_query` to understand **code values only** (for example, `SELECT status, COUNT(*) FROM <table> GROUP BY 1`). Do not scan large tables and do not select personal data.
4. Write the files following the format in [`semantic/README.md`](../semantic/README.md):
   - `<semantic-dir>/entities/<table>.md` — one file per important table (use the name exactly as `list_tables` shows it)
   - `<semantic-dir>/metrics.md` — likely metrics
   - `<semantic-dir>/glossary.md` — business terms that can reasonably be inferred
   - `<semantic-dir>/examples.md` — example questions with SQL in the reported dialect
5. Summarise what you created and list the main open questions for the reviewer.

## Large datasets

If there are many tables, or tables are layered (for example `bronze_`, `silver_`, `gold_`):

- Cover **business-ready (gold) tables first and in full**: they are what questions should be answered from.
- Cover silver tables next, focusing on the columns gold tables are built from.
- Describe raw (bronze) tables briefly, mainly to record lineage and where sensitive data originates.
- Group metrics, glossary terms and examples by schema or business area with headings.

## Rules

- The **live database** (tables, columns, keys, comments, and small sampling queries) is your only source of truth. Do not use other files in the repository as sources, apart from `semantic/README.md` (the format) and existing files in `<semantic-dir>`.
- Do **not** invent facts or business definitions that cannot reasonably be inferred.
- Distinguish observations (from the schema, comments or data) from guesses.
- Use declared foreign keys when available. When there are none, infer relationships from matching column names, and mark them as inferred.
- Mark **every** definition as `Status: proposed`. Never mark anything `approved`.
- Always include physical table and column names in backticks.
- Record sensitivity stated in column comments (for example `PII: email`) in the column description.
- **Never copy personal or sensitive data values** (names, emails, phone numbers, dates of birth, tax/ID/card/account numbers, free-text notes) into these files. They are committed to Git.
- Prefer concise descriptions.
- Record ambiguities under an **Open questions** heading.
- Check that every example SQL query runs successfully with `run_query`.
- If `<semantic-dir>` already contains files, update them rather than overwriting human edits, and never change `approved` definitions.

Identify:

- important entities
- important tables
- columns
- relationships
- likely metrics
- useful business concepts
- example questions
- example SQL
