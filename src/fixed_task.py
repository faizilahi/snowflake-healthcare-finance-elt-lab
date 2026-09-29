"""Fixed Task merge: compound key (policy_id, endorsement_seq, close_month)."""
from __future__ import annotations

import duckdb


def run_fixed_merge(con: duckdb.DuckDBPyConnection) -> dict:
    con.execute("DELETE FROM fact_premium_ledger")
    con.execute(
        """
        INSERT INTO fact_premium_ledger
        SELECT
            policy_id,
            endorsement_seq,
            premium_amt,
            CAST(close_month AS DATE),
            endorsement_type,
            CAST(loaded_at AS TIMESTAMP)
        FROM stream_policy_endorsement
        """
    )
    con.execute("DROP TABLE IF EXISTS mart_premium_by_endorsement")
    con.execute(
        """
        CREATE TABLE mart_premium_by_endorsement AS
        SELECT
            e.policy_id,
            e.endorsement_seq,
            e.premium_amt,
            e.close_month,
            e.endorsement_type,
            a.premium_amt AS actuarial_premium_amt,
            e.premium_amt - a.premium_amt AS variance_amt
        FROM fact_premium_ledger e
        LEFT JOIN raw_actuarial_premium a
          ON e.policy_id = a.policy_id
         AND e.endorsement_seq = a.endorsement_seq
         AND e.close_month = CAST(a.close_month AS DATE)
        """
    )
    con.execute(
        """
        UPDATE meta_stream_offsets
        SET last_offset_ts = (SELECT MAX(loaded_at) FROM stream_policy_endorsement),
            last_row_count = (SELECT COUNT(*) FROM stream_policy_endorsement),
            updated_at = CURRENT_TIMESTAMP
        WHERE stream_name = 'STREAM_POLICY_ENDORSEMENT'
        """
    )
    mart = con.execute("SELECT ROUND(SUM(premium_amt), 2) FROM mart_premium_by_endorsement").fetchone()[0]
    actuarial = con.execute("SELECT ROUND(SUM(premium_amt), 2) FROM raw_actuarial_premium").fetchone()[0]
    return {
        "mart_total": float(mart),
        "actuarial_total": float(actuarial),
        "gap": round(float(actuarial) - float(mart), 2),
    }


def run_reconcile_test(con: duckdb.DuckDBPyConnection, tolerance: float = 1.0) -> bool:
    row = con.execute(
        """
        SELECT ABS(
            (SELECT SUM(premium_amt) FROM mart_premium_by_endorsement)
          - (SELECT SUM(premium_amt) FROM raw_actuarial_premium)
        )
        """
    ).fetchone()[0]
    return float(row) <= tolerance
