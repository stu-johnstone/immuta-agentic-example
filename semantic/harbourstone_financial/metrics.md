# Metrics

All definitions are `proposed` and require human review.

## Retail Banking

### Total customers

- **Status:** proposed
- **Definition:** Count of unique retail customers. Consideration: exclude `DECEASED` customers from active customer counts.

```sql
COUNT(DISTINCT customer_id) -- FROM retail_banking.gold_customer_360 WHERE customer_status != 'DECEASED'
```

### Active customers

- **Status:** proposed
- **Definition:** Count of customers with `customer_status = 'ACTIVE'`.

```sql
COUNT(*) -- FROM retail_banking.gold_customer_360 WHERE customer_status = 'ACTIVE'
```

### Total customer balances (AUD)

- **Status:** proposed
- **Definition:** Sum of total balance across all customers in AUD.

```sql
SUM(total_balance_aud) -- FROM retail_banking.gold_customer_360
```

### Total deposits (AUD)

- **Status:** proposed
- **Definition:** Sum of deposits across all days/branches in AUD.

```sql
SUM(total_deposits_aud) -- FROM retail_banking.gold_daily_deposits
```

### Cash deposits (AUD)

- **Status:** proposed
- **Definition:** Sum of cash deposits in AUD.

```sql
SUM(cash_deposits_aud) -- FROM retail_banking.gold_daily_deposits
```

### Salary deposits (AUD)

- **Status:** proposed
- **Definition:** Sum of salary deposits in AUD.

```sql
SUM(salary_deposits_aud) -- FROM retail_banking.gold_daily_deposits
```

### Open complaints

- **Status:** proposed
- **Definition:** Total count of open/unresolved complaints.

```sql
SUM(open_complaints) -- FROM retail_banking.gold_customer_360 (aggregate view) or SUM(complaints - resolved) from themes
```

### Complaints with compensation

- **Status:** proposed
- **Definition:** Total compensation paid for complaints in AUD.

```sql
SUM(total_compensation) -- FROM retail_banking.gold_complaint_themes
```

## Commercial Banking

### Total commercial exposure (AUD)

- **Status:** proposed
- **Definition:** Total drawn amount across the commercial portfolio in AUD.

```sql
SUM(total_drawn_aud) -- FROM commercial_banking.gold_portfolio_by_industry
```

### Total commercial limits (AUD)

- **Status:** proposed
- **Definition:** Total facility limits across the commercial portfolio in AUD.

```sql
SUM(total_limit_aud) -- FROM commercial_banking.gold_portfolio_by_industry
```

### Portfolio utilisation

- **Status:** proposed
- **Definition:** Overall portfolio utilisation (total drawn / total limit).

```sql
(SUM(total_drawn_aud) / NULLIF(SUM(total_limit_aud), 0)) * 100 -- FROM commercial_banking.gold_portfolio_by_industry
```

### High-risk exposure (AUD)

- **Status:** proposed
- **Definition:** Drawn amount for high-risk borrowers in AUD.

```sql
SUM(high_risk_drawn_aud) -- FROM commercial_banking.gold_portfolio_by_industry
```

### Total arrears (AUD)

- **Status:** proposed
- **Definition:** Total arrears across commercial portfolio in AUD.

```sql
SUM(arrears_aud) -- FROM commercial_banking.gold_portfolio_by_industry
```

## Insurance

### Total incurred claims (12 months, AUD)

- **Status:** proposed
- **Definition:** Total incurred claims over last 12 months in AUD.

```sql
SUM(incurred_claims_12_months) -- FROM insurance.gold_loss_ratio
```

### Total earned premium (12 months, AUD)

- **Status:** proposed
- **Definition:** Total earned premium over last 12 months in AUD.

```sql
SUM(earned_premium_12_months) -- FROM insurance.gold_loss_ratio
```

### Loss ratio

- **Status:** proposed
- **Definition:** Loss ratio percentage (incurred claims / earned premium) * 100.

```sql
(SUM(incurred_claims_12_months) / NULLIF(SUM(earned_premium_12_months), 0)) * 100 -- FROM insurance.gold_loss_ratio
```

### Open claims count

- **Status:** proposed
- **Definition:** Count of open claims.

```sql
COUNT(*) -- FROM insurance.gold_claims_overview WHERE is_open = true
```

### Total claims paid (AUD)

- **Status:** proposed
- **Definition:** Total paid on claims to date in AUD.

```sql
SUM(total_paid) -- FROM insurance.gold_claims_overview
```
