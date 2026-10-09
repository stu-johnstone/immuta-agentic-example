# Examples

All examples are `proposed` and require human review. Example SQL uses the Databricks dialect.

## Retail Banking

### What was total deposits last month by region?

```sql
SELECT region, SUM(total_deposits_aud) AS total_deposits
FROM retail_banking.gold_daily_deposits
WHERE txn_date >= DATEADD(month, -1, TRUNC(CURRENT_DATE(), 'MM'))
  AND txn_date < TRUNC(CURRENT_DATE(), 'MM')
GROUP BY region
ORDER BY total_deposits DESC
```

### How many active customers are there by segment and region?

```sql
SELECT segment, region, COUNT(*) AS active_customers
FROM retail_banking.gold_customer_360
WHERE customer_status = 'ACTIVE'
GROUP BY segment, region
ORDER BY segment, region
```

### Which branches had the highest cash deposits yesterday?

```sql
SELECT branch_name, region, SUM(cash_deposits_aud) AS cash_deposits
FROM retail_banking.gold_daily_deposits
WHERE txn_date = CURRENT_DATE() - INTERVAL 1 DAY
GROUP BY branch_name, region
ORDER BY cash_deposits DESC
```

### What are the top complaint categories by number of complaints?

```sql
SELECT category, SUM(complaints) AS total_complaints
FROM retail_banking.gold_complaint_themes
GROUP BY category
ORDER BY total_complaints DESC
```

## Commercial Banking

### What is the overall portfolio utilisation by industry?

```sql
SELECT industry,
       SUM(total_limit_aud) AS total_limit,
       SUM(total_drawn_aud) AS total_drawn,
       (SUM(total_drawn_aud) / NULLIF(SUM(total_limit_aud), 0)) * 100 AS utilisation_pct
FROM commercial_banking.gold_portfolio_by_industry
GROUP BY industry
ORDER BY utilisation_pct DESC
```

### Which industries have the highest arrears?

```sql
SELECT industry, SUM(arrears_aud) AS total_arrears
FROM commercial_banking.gold_portfolio_by_industry
GROUP BY industry
ORDER BY total_arrears DESC
```

### Which high-risk borrowers (by business) have the largest drawn exposure?

```sql
SELECT business_id, legal_name, industry, region, total_drawn_aud, risk_grade, risk_band
FROM commercial_banking.gold_risk_profile
WHERE risk_band IN ('HIGH', 'WATCHLIST')
ORDER BY total_drawn_aud DESC
LIMIT 10
```

## Insurance

### What is the loss ratio by product line and region?

```sql
SELECT product_code, region,
       SUM(earned_premium_12_months) AS earned_premium_12m,
       SUM(incurred_claims_12_months) AS incurred_claims_12m,
       (SUM(incurred_claims_12_months) / NULLIF(SUM(earned_premium_12_months), 0)) * 100 AS loss_ratio_pct
FROM insurance.gold_loss_ratio
GROUP BY product_code, region
ORDER BY loss_ratio_pct DESC
```

### Which perils have the most open claims?

```sql
SELECT peril, COUNT(*) AS open_claims, SUM(claimed_amount) AS total_claimed
FROM insurance.gold_claims_overview
WHERE is_open = true
GROUP BY peril
ORDER BY open_claims DESC
```

### What are the largest claims by incurred amount?

```sql
SELECT claim_id, policy_id, product_line, peril, claim_status, incurred_amount, total_paid, reserve_amount
FROM insurance.gold_claims_overview
ORDER BY incurred_amount DESC
LIMIT 10
```
