# Claims Overview

- **Status:** proposed
- **Table:** `insurance.gold_claims_overview`
- **Primary key:** `claim_id` (one row per claim)

One row per claim with product, peril, status, amounts, fraud flags and latest file note.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `claim_id` | Unique claim identifier | proposed |
| `policy_id` | Policy identifier (joins to `insurance.silver_policies.policy_id`) | proposed |
| `product_code` | Product code | proposed |
| `product_line` | Product line | proposed |
| `peril` | Cause of loss | proposed |
| `loss_date` | Date of loss | proposed |
| `reported_date` | Date claim reported | proposed |
| `days_to_report` | Days from loss to report | proposed |
| `claim_status` | Claim status | proposed |
| `is_open` | Whether the claim is open | proposed |
| `days_since_reported` | Days since reported | proposed |
| `claimed_amount` | Claimed amount in AUD | proposed |
| `total_paid` | Total paid to date in AUD | proposed |
| `reserve_amount` | Reserve amount in AUD | proposed |
| `incurred_amount` | Incurred amount (paid + reserve) in AUD | proposed |
| `fraud_flags` | Number of fraud flags raised | proposed |
| `max_fraud_score` | Maximum fraud score | proposed |
| `latest_note` | Latest file note (free text; may contain sensitive details) | proposed |
| `state` | State/province | proposed |
| `country` | Country code | proposed |
| `region` | Reporting region. Observed: `APAC`, `EMEA`, `AMER` | proposed |

## Relationships

- `insurance.gold_claims_overview.policy_id` -> `insurance.silver_policies.policy_id` (inferred)

## Open questions

- What values can `claim_status` take?
- How is `max_fraud_score` computed and what scale is it?
- Does `incurred_amount` always equal `total_paid + reserve_amount`?
- Which peril and product codes are standardised?