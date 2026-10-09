# Catastrophe Exposure

- **Status:** proposed
- **Table:** `insurance.gold_catastrophe_exposure`
- **Primary key:** None explicit (grain is `peril`, `region`, `country`)

Exposure to catastrophic events by peril, region and country.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `peril` | Peril type (e.g. cyclone, flood, earthquake) | proposed |
| `region` | Reporting region. Observed: `APAC`, `EMEA`, `AMER` | proposed |
| `country` | Country code | proposed |
| `policies_exposed` | Number of policies exposed | proposed |
| `sum_insured_aud` | Total sum insured in AUD | proposed |
| `expected_loss_aud` | Expected loss estimate in AUD | proposed |
| `max_potential_loss_aud` | Maximum potential loss estimate in AUD | proposed |

## Relationships

Aggregated from `insurance.silver_policies`, `insurance.silver_properties`, `insurance.silver_vehicles` (inferred).

## Open questions

- How are "exposed" policies determined (location-based zoning, event footprint)?
- What models underpin `expected_loss_aud` and `max_potential_loss_aud`?
- Is the grain at peril-region-country level and does it include all lines of business?