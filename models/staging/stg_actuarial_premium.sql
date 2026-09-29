SELECT
    policy_id,
    endorsement_seq,
    CAST(premium_amt AS DECIMAL(18, 2)) AS premium_amt,
    CAST(close_month AS DATE) AS close_month,
    endorsement_type,
    source_system,
    extracted_at
FROM {{ source('actuarial', 'raw_actuarial_premium') }}
WHERE close_month IS NOT NULL
  AND policy_id IS NOT NULL
