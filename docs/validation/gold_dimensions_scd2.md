- Surrogate-key strategy: deterministic xxhash64 over business keys.
- Unknown-member strategy: surrogate key 0 in every dimension.
- SCD Type 2 attributes: product group, package, target yield, lifecycle.
- DV001 controlled change: version 1 ends 2025-12-31; version 2 begins
  2026-01-01 with lifecycle status MATURE.
- Exactly one current row per device and no overlapping date ranges.
- Snapshot and SCD reruns preserve row counts.
