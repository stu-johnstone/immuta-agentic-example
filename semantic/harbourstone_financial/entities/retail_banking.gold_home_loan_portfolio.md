# Home Loan Portfolio

- **Status:** proposed
- **Table:** `retail_banking.gold_home_loan_portfolio`
- **Primary key:** None explicit (grain is `region`, `country`, `state`, `rate_type`, `arrears_bucket`)

Home loan book by region, state, rate type and arrears bucket, with LVR metrics.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `region` | Reporting region. Observed: `APAC`, `EMEA`, `AMER` | proposed |
| `country` | Country code | proposed |
| `state` | State/province | proposed |
| `rate_type` | Interest rate type | proposed |
| `arrears_bucket` | Arrears bucket | proposed |
| `loans` | Number of loans | proposed |
| `total_balance` | Total loan balance in AUD | proposed |
| `avg_loan_to_value_pct` | Average loan-to-value percentage | proposed |
| `loans_over_80_pct_lvr` | Number of loans with LVR > 80% | proposed |
| `avg_interest_rate` | Average interest rate (percentage) | proposed |

## Relationships

Aggregated from `retail_banking.silver_home_loans` (inferred).

## Open questions

- What are the arrears bucket boundaries?
- How is LVR calculated (value at origination vs current valuation)?
- Does `total_balance` include or exclude offset amounts?