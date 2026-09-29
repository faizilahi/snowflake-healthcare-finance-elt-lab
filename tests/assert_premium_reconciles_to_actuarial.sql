WITH totals AS (
    SELECT
        (SELECT COALESCE(SUM(premium_amt), 0)
         FROM {{ ref('mart_premium_by_endorsement') }}
         WHERE close_month = DATE '2025-08-01') AS mart_total,
        (SELECT COALESCE(SUM(premium_amt), 0)
         FROM {{ ref('stg_actuarial_premium') }}
         WHERE close_month = DATE '2025-08-01') AS actuarial_total
)
SELECT mart_total, actuarial_total, ABS(mart_total - actuarial_total) AS abs_gap
FROM totals
WHERE ABS(mart_total - actuarial_total) > 1.00
