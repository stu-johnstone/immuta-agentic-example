# Metrics

All definitions are `proposed` and require human review.

## Revenue

- **Status:** proposed
- **Definition:** Sum of `orders.total` for orders with `status = 'completed'`. Cancelled and pending orders are excluded. This matches the convention described in `AGENTS.md`.

```sql
SUM(orders.total) -- WHERE orders.status = 'completed'
```

## Order count

- **Status:** proposed
- **Definition:** Number of orders with `status = 'completed'`.

```sql
COUNT(*) -- WHERE orders.status = 'completed'
```

## Average order value

- **Status:** proposed
- **Definition:** Revenue divided by the number of completed orders.

```sql
AVG(orders.total) -- WHERE orders.status = 'completed'
```
