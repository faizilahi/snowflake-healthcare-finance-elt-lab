SELECT
    e.policy_id,
    e.endorsement_seq,
    e.premium_amt,
    e.close_month,
    e.endorsement_type,
    a.premium_amt AS actuarial_premium_amt,
    e.premium_amt - a.premium_amt AS variance_amt
FROM {{ ref('stg_policy_endorsement') }} e
LEFT JOIN {{ ref('stg_actuarial_premium') }} a
    ON e.policy_id = a.policy_id
   AND e.endorsement_seq = a.endorsement_seq
   AND e.close_month = a.close_month
