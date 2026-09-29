# Close timeline — August commercial premium

| Time (ET) | Event |
|-----------|-------|
| Mon 22:10 | Stage COPY lands actuarial + endorsement feeds for close_month 2025-08 |
| Mon 22:40 | Stream on endorsement feed shows unread rows |
| Mon 23:05 | Task merges on policy_id only |
| Tue 06:15 | Finance mart refresh completes under actuarial control |
| Tue 08:40 | Actuarial control arrives — drift ticket opened |
| Tue 10:20 | Investigation SQL isolates endorsement_seq > 0 rows absent from mart |
| Tue 13:00 | Task rewritten to (policy_id, endorsement_seq); dbt singular test added |
| Tue 14:30 | Re-run: mart matches actuarial within $0.00 |
