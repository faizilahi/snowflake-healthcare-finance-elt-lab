CREATE TABLE IF NOT EXISTS meta_stream_offsets (
    stream_name       VARCHAR,
    last_offset_ts    TIMESTAMP,
    last_row_count    BIGINT,
    task_name         VARCHAR,
    updated_at        TIMESTAMP
);
