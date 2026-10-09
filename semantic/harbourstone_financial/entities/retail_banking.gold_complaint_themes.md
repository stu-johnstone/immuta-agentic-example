# Complaint Themes

- **Status:** proposed
- **Table:** `retail_banking.gold_complaint_themes`
- **Primary key:** None explicit (grain is `received_month`, `category`, `region`)

Complaints per month, category and region, with resolution times, compensation and the latest example.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `received_month` | Month the complaints were received (first of month) | proposed |
| `category` | Complaint category | proposed |
| `region` | Reporting region. Observed: `APAC`, `EMEA`, `AMER` | proposed |
| `complaints` | Number of complaints | proposed |
| `unresolved` | Number of unresolved complaints | proposed |
| `escalated` | Number of escalated complaints | proposed |
| `avg_days_to_resolve` | Average days to resolve (for resolved complaints) | proposed |
| `total_compensation` | Total compensation paid in AUD | proposed |
| `latest_example` | Latest complaint example text (free text; may contain sensitive details) | proposed |

## Relationships

None declared; grain ties to `retail_banking.silver_complaints` aggregated by month/category/region (inferred).

## Open questions

- How is `category` derived (standardised taxonomy)?
- Is `avg_days_to_resolve` calculated on closed/resolved cases only?
- What qualifies as `escalated`?