# Daily Deposits

- **Status:** proposed
- **Table:** `retail_banking.gold_daily_deposits`
- **Primary key:** (`txn_date`, `branch_id`)

Deposits per day and branch in AUD, split into cash and salary. Answers "what were total deposits today/last month by branch/region".

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `txn_date` | Date of transactions | proposed |
| `branch_id` | Branch identifier | proposed |
| `branch_name` | Branch name | proposed |
| `region` | Reporting region. Observed: `APAC`, `EMEA`, `AMER` | proposed |
| `country` | Country code. Observed: `AU`, `NZ`, `GB`, `SG`, `US` | proposed |
| `deposit_count` | Number of deposit transactions | proposed |
| `total_deposits_aud` | Total deposits in AUD | proposed |
| `cash_deposits_aud` | Cash deposits in AUD | proposed |
| `salary_deposits_aud` | Salary deposits in AUD | proposed |

## Relationships

- `retail_banking.gold_daily_deposits.branch_id` -> `retail_banking.silver_branches.branch_id` (inferred)

## Open questions

- Is `txn_date` in the timezone of the branch/country? How is it bounded (cutoff time)?
- Are reversals/exceptions excluded from `deposit_count` and totals?