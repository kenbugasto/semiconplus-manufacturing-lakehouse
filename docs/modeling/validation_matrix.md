# SemiconPlus Validation Matrix

| Object | Validation | Pass condition |
|---|---|---|
| All dimensions | Business-key uniqueness | Duplicate count = 0 |
| All dimensions | Surrogate-key uniqueness | Duplicate count = 0 |
| All facts | Referential integrity | Unresolved foreign keys = 0 |
| dim_date | Historical coverage | Every source business date is covered |
| dim_lot | Stable mapping | One source lot maps to one test lot |
| dim_lot | Incremental stability | Existing mappings never change |
| Yield facts | Quantity balance | Input = FP good + FP fail |
| Yield facts | FPY range | 0 <= FPY <= 1 |
| Retest source | Eligibility | Retest input <= FP failures |
| Retest source | Quantity balance | Retest input = good + fail |
| Yield facts | Final quantity | Final good <= input |
| Yield facts | FTY relationship | FPY <= FTY <= 1 |
| Retest fact | Zero denominator | RPR is null when retest input = 0 |
| OEE source | Planned time | 0 <= planned production <= scheduled |
| OEE source | Operating time | 0 <= operating <= planned production |
| OEE source | Unit quantities | 0 <= good <= total <= theoretical output |
| OEE fact | KPI ranges | Availability, Utilization, Quality and OEE are within [0,1] |
| OEE fact | Rolling calculation | Recomputed from summed components |
| Event fact | Event key | event_id is unique and non-null |
| Event fact | Timestamp order | Event end >= event start |
| Event fact | Duration boundaries | 300/301 and 3600/3601 tests pass |
| Incremental tables | Idempotence | Identical rerun creates zero duplicates |
| Secure views | Row filtering | Only authorized product groups are visible |
| Secure views | Masking | Restricted equipment remains masked |
| Power BI | Reconciliation | Measures match Databricks SQL |
| Synthetic objects | Disclosure | Simulation flag and seed are present |
| Full model | Historical retention | Five-year history remains after rerun |

## Conformed Model Acceptance

| Validation | Result |
|---|---:|
| Source and lot-fact rows | 18,124 |
| Persistent lot mappings | 18,124 |
| Periodic yield rows | 17,228 |
| Input quantity | 19,937,318 |
| First-pass good quantity | 18,673,344 |
| First-pass fail quantity | 1,263,974 |
| Duplicate dimension/fact keys | 0 |
| Unresolved foreign keys | 0 |
| Historical coverage | 2021-01-01 to 2025-12-31 |
| Mapping rerun insertions | 0 |
| Final status | PASSED |