"""Run the premium drift investigation end to end."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.broken_task import run_broken_merge
from src.fixed_task import run_fixed_merge, run_reconcile_test
from src.warehouse import bootstrap, connect


def main() -> None:
    data = ROOT / "data" / "raw_actuarial_premium.csv"
    if not data.exists():
        print("Run scripts/generate_close_data.py first.")
        sys.exit(1)

    con = connect()
    bootstrap(con)

    print("=== BROKEN Task merge (policy_id only) ===")
    broken = run_broken_merge(con)
    for k, v in broken.items():
        print(f"  {k}: {v}")

    print("\n=== Investigation: missing endorsement rows ===")
    rows = con.execute(
        """
        SELECT a.policy_id, a.endorsement_seq, a.endorsement_type,
               a.premium_amt AS expected_premium,
               a.premium_amt AS drift_amt
        FROM raw_actuarial_premium a
        LEFT JOIN mart_premium_by_endorsement m
          ON a.policy_id = m.policy_id
         AND a.endorsement_seq = m.endorsement_seq
        WHERE a.endorsement_seq > 0 AND m.policy_id IS NULL
        ORDER BY a.premium_amt DESC
        LIMIT 10
        """
    ).fetchall()
    for r in rows:
        print(f"  {r}")

    print("\n=== FIXED Task merge (policy_id, endorsement_seq) ===")
    fixed = run_fixed_merge(con)
    for k, v in fixed.items():
        print(f"  {k}: {v}")

    ok = run_reconcile_test(con)
    print(f"\n=== dbt singular reconcile test passed: {ok} ===")
    if not ok:
        sys.exit(2)
    print("Close gate green — mart matches actuarial within $1.00")


if __name__ == "__main__":
    main()
