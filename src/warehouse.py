"""DuckDB warehouse stand-in for Snowflake databases used in the close."""
from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "premium_close.duckdb"


def connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DB_PATH))


def bootstrap(con: duckdb.DuckDBPyConnection) -> None:
    data = ROOT / "data"
    for t in [
        "dim_policy",
        "raw_actuarial_premium",
        "raw_policy_endorsement",
        "stream_policy_endorsement",
        "fact_premium_ledger",
        "mart_premium_by_endorsement",
        "meta_stream_offsets",
    ]:
        con.execute(f"DROP TABLE IF EXISTS {t}")

    con.execute(f"CREATE TABLE dim_policy AS SELECT * FROM read_csv_auto('{(data / 'dim_policy.csv').as_posix()}')")
    con.execute(
        f"CREATE TABLE raw_actuarial_premium AS SELECT * FROM read_csv_auto('{(data / 'raw_actuarial_premium.csv').as_posix()}')"
    )
    con.execute(
        f"CREATE TABLE raw_policy_endorsement AS SELECT * FROM read_csv_auto('{(data / 'raw_policy_endorsement.csv').as_posix()}')"
    )
    con.execute("CREATE TABLE stream_policy_endorsement AS SELECT * FROM raw_policy_endorsement")
    con.execute(
        """
        CREATE TABLE fact_premium_ledger (
            policy_id VARCHAR,
            endorsement_seq INTEGER,
            premium_amt DOUBLE,
            close_month DATE,
            endorsement_type VARCHAR,
            loaded_at TIMESTAMP
        )
        """
    )
    con.execute(
        """
        CREATE TABLE meta_stream_offsets (
            stream_name VARCHAR,
            last_offset_ts TIMESTAMP,
            last_row_count BIGINT,
            task_name VARCHAR,
            updated_at TIMESTAMP
        )
        """
    )
    con.execute(
        """
        INSERT INTO meta_stream_offsets VALUES
        ('STREAM_POLICY_ENDORSEMENT', NULL, 0, 'TASK_MERGE_PREMIUM_LEDGER', CURRENT_TIMESTAMP)
        """
    )
