# Portfolio by Industry

- **Status:** proposed
- **Table:** `commercial_banking.gold_portfolio_by_industry`
- **Primary key:** None explicit (grain is `industry`, `region`)

Commercial lending book by industry and region: exposure, average risk grade, high-risk borrowers, breaches and arrears.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `industry` | Industry classification | proposed |
| `region` | Reporting region. Observed: `APAC`, `EMEA`, `AMER` | proposed |
| `borrowers` | Number of borrowers | proposed |
| `total_limit_aud` | Total facility limits in AUD | proposed |
| `total_drawn_aud` | Total drawn amount in AUD | proposed |
| `utilisation_pct` | Utilisation percentage (drawn / limit) | proposed |
| `avg_risk_grade` | Average risk grade (1 = strong to 10 = default) | proposed |
| `high_risk_borrowers` | Number of high-risk borrowers | proposed |
| `high_risk_drawn_aud` | Drawn amount for high-risk borrowers in AUD | proposed |
| `covenant_breaches_6_months` | Covenant breaches in last 6 months | proposed |
| `arrears_aud` | Total arrears in AUD | proposed |

## Relationships

Aggregated from `commercial_banking.silver_facilities`, `commercial_banking.silver_business_customers` (inferred).

## Open questions

- What threshold defines "high-risk" (risk grade band)?
- How is `avg_risk_grade` weighted (by exposure vs by borrower)?
- Does `utilisation_pct` use committed limits or total limits?