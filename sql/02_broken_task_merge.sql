-- BROKEN Task body — MERGE keyed only on policy_id
MERGE INTO fact_premium_ledger AS tgt
USING (
    SELECT
        policy_id,
        MAX(endorsement_seq) AS endorsement_seq,
        SUM(premium_amt) AS premium_amt,
        close_month,
        MAX(loaded_at) AS loaded_at
    FROM stream_policy_endorsement
    GROUP BY policy_id, close_month
) AS src
ON tgt.policy_id = src.policy_id
AND tgt.close_month = src.close_month
WHEN MATCHED THEN UPDATE SET
    premium_amt = src.premium_amt,
    endorsement_seq = src.endorsement_seq,
    loaded_at = src.loaded_at
WHEN NOT MATCHED THEN INSERT (policy_id, endorsement_seq, premium_amt, close_month, loaded_at)
VALUES (src.policy_id, src.endorsement_seq, src.premium_amt, src.close_month, src.loaded_at);
