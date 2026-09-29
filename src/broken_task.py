"""Broken Task merge: collapses endorsement grain onto policy_id."""
from __future__ import annotations

import duckdb


def run_broken_merge(con: duckdb.DuckDBPyConnection) -> dict:
    con.execute("DELETE FROM fact_premium_ledger")
    # Simulates MERGE ON policy_id only: base rows land, endorsement deltas never get their own key
    # and are discarded when a later endorsement upsert overwrites with a single policy-level row
    # that retained only endorsement_seq = 0 premium.
    con.execute(
        """
        INSERT INTO fact_premium_ledger
        SELECT
            policy_id,
            0 AS endorsement_seq,
            premium_amt,
            CAST(close_month AS DATE) AS close_month,
            endorsement_type,
            CAST(loaded_at AS TIMESTAMP) AS loaded_at
        FROM stream_policy_endorsement
        WHERE endorsement_seq = 0
        """
    )
    con.execute("DROP TABLE IF EXISTS mart_premium_by_endorsement")
    con.execute(
        """
        CREATE TABLE mart_premium_by_endorsement AS
        SELECT policy_id, endorsement_seq, premium_amt, close_month, endorsement_type
        FROM fact_premium_ledger
        """
    )
    mart = con.execute(
        "SELECT ROUND(SUM(premium_amt), 2) FROM mart_premium_by_endorsement WHERE close_month = DATE '2025-08-01'"
    ).fetchone()[0]
    actuarial = con.execute(
        "SELECT ROUND(SUM(premium_amt), 2) FROM raw_actuarial_premium WHERE CAST(close_month AS DATE) = DATE '2025-08-01'"
    ).fetchone()[0]
    missing = con.execute(
        """
        SELECT COUNT(*), ROUND(SUM(a.premium_amt), 2)
        FROM raw_actuarial_premium a
        LEFT JOIN mart_premium_by_endorsement m
          ON a.policy_id = m.policy_id AND a.endorsement_seq = m.endorsement_seq
        WHERE CAST(a.close_month AS DATE) = DATE '2025-08-01'
          AND a.endorsement_seq > 0
          AND m.policy_id IS NULL
        """
    ).fetchone()
    return {
        "mart_total": float(mart),
        "actuarial_total": float(actuarial),
        "gap": round(float(actuarial) - float(mart), 2),
        "missing_endorsement_rows": int(missing[0]),
        "missing_endorsement_premium": float(missing[1] or 0),
    }
