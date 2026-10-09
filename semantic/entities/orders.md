# Order

- **Status:** proposed
- **Table:** `orders`
- **Primary key:** `id`

A purchase made by a customer.

## Columns

| Column | Description | Status |
| --- | --- | --- |
| `id` | Unique order identifier | proposed |
| `customer_id` | Customer who placed the order (FK -> `customers.id`) | proposed |
| `total` | Order value (gross) | proposed |
| `status` | Order status: `completed`, `cancelled` or `pending` (observed) | proposed |
| `created_at` | Date the order was created | proposed |

## Relationships

- `orders.customer_id` -> `customers.id` — each order belongs to a customer (observed FK).

## Open questions

- What is the full lifecycle of `status`? Only `completed`, `cancelled` and `pending` were observed; are there others?
- Is `total` gross or net of refunds/taxes? No comment or documentation available.
- Is `created_at` the order date or the completion date?
