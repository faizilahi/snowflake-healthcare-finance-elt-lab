MERGE INTO fact_premium_ledger AS tgt
USING (
    SELECT policy_id, endorsement_seq, premium_amt, close_month, endorsement_type, loaded_at
    FROM stream_policy_endorsement
) AS src
ON tgt.policy_id = src.policy_id
AND tgt.endorsement_seq = src.endorsement_seq
AND tgt.close_month = src.close_month
WHEN MATCHED THEN UPDATE SET
    premium_amt = src.premium_amt,
    endorsement_type = src.endorsement_type,
    loaded_at = src.loaded_at
WHEN NOT MATCHED THEN INSERT (
    policy_id, endorsement_seq, premium_amt, close_month, endorsement_type, loaded_at
) VALUES (
    src.policy_id, src.endorsement_seq, src.premium_amt, src.close_month,
    src.endorsement_type, src.loaded_at
);
