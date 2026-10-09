# Commercial Risk Profile

- **Status:** proposed
- **Table:** `commercial_banking.gold_risk_profile`
- **Primary key:** `business_id` (one row per business borrower)

One row per business borrower: exposure, utilisation, collateral cover, risk grade, covenant breaches, arrears and latest analyst commentary.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `business_id` | Business identifier | proposed |
| `legal_name` | Legal name of business (PII: business identity) | proposed |
| `industry` | Industry classification | proposed |
| `country` | Country code | proposed |
| `region` | Reporting region. Observed: `APAC`, `EMEA`, `AMER` | proposed |
| `relationship_manager` | Relationship manager name (PII: person name) | proposed |
| `facilities` | Number of facilities | proposed |
| `total_limit_aud` | Total facility limits in AUD | proposed |
| `total_drawn_aud` | Total drawn amount in AUD | proposed |
| `utilisation_pct` | Utilisation percentage (drawn / limit) | proposed |
| `collateral_aud` | Collateral value in AUD | proposed |
| `collateral_cover_ratio` | Collateral cover ratio | proposed |
| `risk_grade` | Risk grade (1 = strong to 10 = default) | proposed |
| `risk_band` | Risk band derived from risk grade | proposed |
| `probability_of_default_pct` | Probability of default percentage | proposed |
| `covenant_breaches_6_months` | Covenant breaches in last 6 months | proposed |
| `missed_repayments_6_months` | Missed repayments in last 6 months | proposed |
| `max_days_late` | Maximum days late for any repayment | proposed |
| `arrears_aud` | Total arrears in AUD | proposed |
| `latest_review_date` | Date of latest review | proposed |
| `latest_analyst_commentary` | Latest analyst commentary (free text; may contain sensitive details) | proposed |

## Relationships

- `commercial_banking.gold_risk_profile.business_id` -> `commercial_banking.silver_business_customers.business_id` (inferred)
- Aggregates from `commercial_banking.silver_facilities`, `commercial_banking.silver_covenants`, `commercial_banking.silver_repayments`, `commercial_banking.silver_collateral`, `commercial_banking.silver_credit_reviews` (inferred lineage)

## Open questions

- How is `collateral_cover_ratio` defined (e.g. collateral / drawn, collateral / limit)?
- What is the mapping between `risk_grade` (1-10) and `risk_band`?
- How is `probability_of_default_pct` estimated?