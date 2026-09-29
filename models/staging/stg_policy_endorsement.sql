SELECT
    policy_id,
    endorsement_seq,
    CAST(premium_amt AS DECIMAL(18, 2)) AS premium_amt,
    CAST(close_month AS DATE) AS close_month,
    endorsement_type,
    loaded_at
FROM {{ source('cdc', 'raw_policy_endorsement') }}
WHERE endorsement_seq >= 0
