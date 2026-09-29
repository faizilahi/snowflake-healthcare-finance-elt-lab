WITH actuarial AS (
    SELECT policy_id, endorsement_seq, premium_amt, close_month, endorsement_type
    FROM raw_actuarial_premium
    WHERE close_month = DATE '2025-08-01'
),
mart AS (
    SELECT policy_id, endorsement_seq, premium_amt, close_month
    FROM mart_premium_by_endorsement
    WHERE close_month = DATE '2025-08-01'
)
SELECT
    a.policy_id,
    a.endorsement_seq,
    a.endorsement_type,
    a.premium_amt AS expected_premium,
    m.premium_amt AS mart_premium,
    a.premium_amt - COALESCE(m.premium_amt, 0) AS drift_amt
FROM actuarial a
LEFT JOIN mart m
    ON a.policy_id = m.policy_id
   AND a.endorsement_seq = m.endorsement_seq
   AND a.close_month = m.close_month
WHERE m.policy_id IS NULL
   OR ABS(a.premium_amt - COALESCE(m.premium_amt, 0)) > 0.01
ORDER BY drift_amt DESC;
