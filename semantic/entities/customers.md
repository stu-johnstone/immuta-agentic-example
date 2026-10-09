# Customer

- **Status:** proposed
- **Table:** `customers`
- **Primary key:** `id`

A customer account that can place orders.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `id` | Unique customer identifier | proposed |
| `name` | Customer name (company or individual) | proposed |
| `segment` | Customer segment: `Enterprise`, `SMB` or `Consumer` (observed) | proposed |
| `created_at` | Date the customer record was created | proposed |

## Relationships

- `orders.customer_id` -> `customers.id` — each order belongs to a customer (observed FK).

## Open questions

- Does `segment` ever change over time, or is it fixed at creation?
- Is `name` always a company, or can it be an individual (observed: `Jane Doe`, `John Smith`)?
