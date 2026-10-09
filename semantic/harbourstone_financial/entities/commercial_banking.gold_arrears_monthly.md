# Commercial Arrears (Monthly)

- **Status:** proposed
- **Table:** `commercial_banking.gold_arrears_monthly`
- **Primary key:** None explicit (grain is `due_month`, `facility_type`, `region`)

Repayments due, paid, late and missed per month, facility type and region.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `due_month` | Month repayments are due (first of month) | proposed |
| `facility_type` | Facility type | proposed |
| `region` | Reporting region. Observed: `APAC`, `EMEA`, `AMER` | proposed |
| `repayments_due` | Number of repayments due | proposed |
| `amount_due` | Amount due in AUD | proposed |
| `amount_paid` | Amount paid in AUD | proposed |
| `missed_repayments` | Number of missed repayments | proposed |
| `late_repayments` | Number of late repayments | proposed |
| `shortfall_aud` | Shortfall (amount due - amount paid) in AUD | proposed |

## Relationships

Aggregated from `commercial_banking.silver_repayments` (inferred).

## Open questions

- Is `shortfall_aud` capped at 0 or can it be negative (overpayment)?
- How is "late" vs "missed" defined (days past due threshold)?
- Does `due_month` reflect the due date or processing month?