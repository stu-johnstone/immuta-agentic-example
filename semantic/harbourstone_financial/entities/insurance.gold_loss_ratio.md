# Loss Ratio

- **Status:** proposed
- **Table:** `insurance.gold_loss_ratio`
- **Primary key:** None explicit (grain is `product_code`, `region`)

Earned premium and claims incurred in the last 12 months, and loss ratio by product and region.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `product_code` | Product code | proposed |
| `region` | Reporting region. Observed: `APAC`, `EMEA`, `AMER` | proposed |
| `policies_in_force` | Number of policies in force for the period | proposed |
| `earned_premium_12_months` | Earned premium over last 12 months in AUD | proposed |
| `claims_12_months` | Number of claims in last 12 months | proposed |
| `incurred_claims_12_months` | Incurred claims over last 12 months in AUD | proposed |
| `loss_ratio_pct` | Loss ratio percentage (incurred / earned premium) | proposed |

## Relationships

Aggregated from `insurance.silver_policies` and `insurance.silver_claims` (inferred).

## Open questions

- How is "last 12 months" defined (trailing 12 months vs accounting year)?
- Is `loss_ratio_pct` calculated as (incurred_claims_12_months / earned_premium_12_months) * 100?
- Does this include IBNR (Incurred But Not Reported) adjustments?