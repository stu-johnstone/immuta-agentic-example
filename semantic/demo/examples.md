# Example Questions

All `proposed`. SQL is written for the `sqlite` dialect reported by `list_tables`.

## What was revenue by customer segment?

- **Status:** proposed

```sql
SELECT c.segment, SUM(o.total) AS revenue
FROM orders AS o
JOIN customers AS c ON o.customer_id = c.id
WHERE o.status = 'completed'
GROUP BY c.segment
ORDER BY revenue DESC
```

## What was revenue by month?

- **Status:** proposed

```sql
SELECT strftime('%Y-%m', created_at) AS month, SUM(total) AS revenue
FROM orders
WHERE status = 'completed'
GROUP BY month
ORDER BY month
```

## How many completed orders were there?

- **Status:** proposed

```sql
SELECT COUNT(*) AS order_count
FROM orders
WHERE status = 'completed'
```
