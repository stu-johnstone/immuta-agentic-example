# AML Overview

- **Status:** proposed
- **Table:** `retail_banking.gold_aml_overview`
- **Primary key:** None explicit (grain is `alert_status`, `risk_level`, `reviewer`, `month_opened`)

AML alerts overview with case counts, ageing and value at risk.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `alert_status` | Alert status | proposed |
| `risk_level` | Risk level | proposed |
| `reviewer` | Reviewer assigned (PII: person name) | proposed |
| `month_opened` | Month the alert was opened (first of month) | proposed |
| `alerts` | Number of alerts | proposed |
| `avg_days_open` | Average days open | proposed |
| `max_days_open` | Maximum days open | proposed |
| `value_at_risk_aud` | Value at risk in AUD | proposed |

## Relationships

Aggregated from `retail_banking.silver_aml_alerts` (inferred).

## Open questions

- What statuses are included (e.g. OPEN, IN_REVIEW, CLOSED)?
- How is `value_at_risk_aud` calculated?
- Does `month_opened` use the alert creation date?