# Month-End Premium Drift on Snowflake Streams: Missing Endorsements and the dbt Gate That Caught Them

Faiz Elahi — [LinkedIn](https://www.linkedin.com/in/faizilahi) — [pendataco.com](https://pendataco.com) — [GitHub](https://github.com/faizilahi)

Synthetic policy, endorsement, and premium ledger rows power every query below.

## The close that did not reconcile

On a commercial lines month-end close, booked premium in the finance mart came in under the actuarial control total after a Stream + Task refresh landed overnight. Source extracts and the stage load both looked complete. The gap lived in how incremental CDC treated endorsement-style adjustments that share a `policy_id` but carry a different `endorsement_seq`.

This repository reconstructs that investigation locally with DuckDB standing in for Snowflake warehouses, Streams/Tasks as offset-driven SQL modules, and dbt-style YAML tests that fail closed when the endorsement grain is dropped.

## What broke in the Stream/Task path

The Task merged into `fact_premium_ledger` on `policy_id` only. Mid-month endorsements (additional insured, limit increases, mid-term cancellations) arrived as new rows with the same `policy_id` and a higher `endorsement_seq`. The merge upserted the base policy and silently discarded the endorsement identity.

## SQL that finds the missing endorsement rows

See `sql/01_find_missing_endorsements.sql`. After the broken merge, that query returns every actuarial endorsement with `endorsement_seq > 0` that has no matching mart row — the exact dollars that explain the close gap.

## dbt test that locks the grain

`models/marts/schema.yml` enforces unique `(policy_id, endorsement_seq, close_month)`.  
`tests/assert_premium_reconciles_to_actuarial.sql` fails CI when absolute gap exceeds $1.00.

## Layout

| Path | Role |
|------|------|
| `sql/` | Investigation and merge-fix SQL |
| `src/` | DuckDB runner: broken then fixed Task |
| `models/` | dbt-style staging + mart SQL + YAML |
| `scripts/generate_close_data.py` | Synthetic close extracts with planted drift |
| `docs/close_timeline.md` | Incident timeline |

## Run locally

```powershell
cd snowflake-healthcare-finance-elt-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_close_data.py
python src/run_close_investigation.py
```

Expected stdout shows the endorsement gap under the broken merge key, then a clean reconcile after the compound-key Task rewrite.
