# Retail Customer 360

- **Status:** proposed
- **Table:** `retail_banking.gold_customer_360`
- **Primary key:** `customer_id` (one row per customer)

A business-ready, one-row-per-customer view of a retail customer: their accounts, balances, cards, home loan, open complaints, open AML alerts and their most recent contact. This is the primary table for "tell me about this customer" and customer-segment questions.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `customer_id` | Unique customer identifier (joins to `retail_banking.silver_customers.customer_id`) | proposed |
| `first_name` | Given name (PII: person name) | proposed |
| `last_name` | Family name (PII: person name) | proposed |
| `email` | Email address (PII: email) | proposed |
| `age_band` | Banded age. Observed: `18-24`, `25-34`, `35-49`, `50-64`, `65+` | proposed |
| `segment` | Customer segment. Observed: `MASS`, `AFFLUENT`, `PRIVATE` | proposed |
| `customer_status` | Lifecycle status. Observed: `ACTIVE`, `DORMANT`, `DECEASED` | proposed |
| `home_branch_name` | Name of the customer's home branch (e.g. `Digital Banking`) | proposed |
| `country` | Country code. Observed: `AU`, `NZ`, `GB`, `SG`, `US` | proposed |
| `region` | Reporting region. Observed: `APAC`, `EMEA`, `AMER` | proposed |
| `accounts` | Number of accounts this customer holds | proposed |
| `total_balance_aud` | Total balance across accounts, in AUD | proposed |
| `active_cards` | Number of active cards | proposed |
| `has_home_loan` | Whether the customer has a home loan | proposed |
| `home_loan_balance` | Current home loan balance (null when `has_home_loan` is false) | proposed |
| `home_loan_days_in_arrears` | Days the home loan is in arrears (0 when current) | proposed |
| `open_complaints` | Number of unresolved complaints | proposed |
| `open_aml_alerts` | Number of open AML alerts | proposed |
| `last_contact_date` | Date of the most recent CRM contact (null if none) | proposed |
| `last_contact_topic` | Topic of the most recent contact | proposed |
| `last_contact_notes` | Notes from the most recent contact (free text; may contain sensitive details) | proposed |

## Relationships

- `retail_banking.gold_customer_360.customer_id` -> `retail_banking.silver_customers.customer_id` (inferred; no declared FK)
- `retail_banking.gold_customer_360.home_branch_name` corresponds to `retail_banking.silver_branches.branch_name` (inferred)

## Open questions

- Are `DORMANT` and `DECEASED` customers included in balance and customer-count metrics, or should they be excluded?
- Is `total_balance_aud` the balance of open accounts only?
- What defines an "open" complaint or AML alert (which statuses count)?
- `home_loan_balance` is null for customers without a home loan; confirm this is intentional rather than 0.