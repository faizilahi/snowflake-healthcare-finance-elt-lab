"""Generate synthetic August close extracts with planted endorsement drift."""
from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)
random.seed(20250801)

ENDORSEMENT_TYPES = ["BASE", "ADD_INSURED", "LIMIT_INCREASE", "MIDTERM_CANCEL", "PREMIUM_AUDIT"]


def main() -> None:
    policies = []
    actuarial = []
    endorsements = []
    close_month = "2025-08-01"
    base_ts = datetime(2025, 8, 31, 22, 10, 0)

    for i in range(1, 401):
        policy_id = f"POL-{i:05d}"
        base_premium = round(random.uniform(2000, 25000), 2)
        policies.append(
            {
                "policy_id": policy_id,
                "line_of_business": random.choice(["GL", "WC", "PROPERTY", "AUTO"]),
                "state": random.choice(["NY", "NJ", "CT", "PA"]),
                "effective_date": "2025-01-01",
            }
        )
        actuarial.append(
            {
                "policy_id": policy_id,
                "endorsement_seq": 0,
                "premium_amt": base_premium,
                "close_month": close_month,
                "endorsement_type": "BASE",
                "source_system": "ACTUARIAL_CTRL",
                "extracted_at": base_ts.isoformat(),
            }
        )
        endorsements.append(
            {
                "policy_id": policy_id,
                "endorsement_seq": 0,
                "premium_amt": base_premium,
                "close_month": close_month,
                "endorsement_type": "BASE",
                "loaded_at": (base_ts + timedelta(minutes=i % 40)).isoformat(),
            }
        )
        if i % 3 == 0:
            seq = 1
            extra = round(random.uniform(150, 4200), 2)
            etype = random.choice(ENDORSEMENT_TYPES[1:])
            row = {
                "policy_id": policy_id,
                "endorsement_seq": seq,
                "premium_amt": extra,
                "close_month": close_month,
                "endorsement_type": etype,
                "source_system": "ACTUARIAL_CTRL",
                "extracted_at": base_ts.isoformat(),
            }
            actuarial.append(row)
            endorsements.append(
                {
                    "policy_id": policy_id,
                    "endorsement_seq": seq,
                    "premium_amt": extra,
                    "close_month": close_month,
                    "endorsement_type": etype,
                    "loaded_at": (base_ts + timedelta(minutes=50 + i % 30)).isoformat(),
                }
            )
        if i % 11 == 0:
            seq = 2
            extra = round(random.uniform(80, 1800), 2)
            actuarial.append(
                {
                    "policy_id": policy_id,
                    "endorsement_seq": seq,
                    "premium_amt": extra,
                    "close_month": close_month,
                    "endorsement_type": "PREMIUM_AUDIT",
                    "source_system": "ACTUARIAL_CTRL",
                    "extracted_at": base_ts.isoformat(),
                }
            )
            endorsements.append(
                {
                    "policy_id": policy_id,
                    "endorsement_seq": seq,
                    "premium_amt": extra,
                    "close_month": close_month,
                    "endorsement_type": "PREMIUM_AUDIT",
                    "loaded_at": (base_ts + timedelta(minutes=80 + i % 20)).isoformat(),
                }
            )

    def write_csv(name: str, rows: list[dict]) -> None:
        path = DATA / name
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {path} ({len(rows)} rows)")

    write_csv("dim_policy.csv", policies)
    write_csv("raw_actuarial_premium.csv", actuarial)
    write_csv("raw_policy_endorsement.csv", endorsements)
    act_total = sum(float(r["premium_amt"]) for r in actuarial)
    endo_only = sum(float(r["premium_amt"]) for r in actuarial if int(r["endorsement_seq"]) > 0)
    print(f"actuarial_total={act_total:.2f}")
    print(f"endorsement_delta_planted={endo_only:.2f}")


if __name__ == "__main__":
    main()
