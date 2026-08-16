# SemiconPlus Modeling Decisions

## 1. Production quantities

Production-lot quantities are authoritative for manufacturing volume and yield.

- Input = quantity_started
- First-pass good = quantity_passed
- First-pass fail = quantity_failed
- FPY = SUM(first-pass good) / SUM(input)

Stored source yield is retained only for reconciliation.

## 2. Test-batch hierarchy

The source contains no mother-lot or sublot fields. SemiconPlus therefore
creates simulated analytical identifiers named `test_batch_id` and
`test_lot_id`.

These identifiers are not physical manufacturing genealogy. Their mappings are
persisted, and existing lots are never renumbered during incremental processing.

## 3. Retest source

Unit-test results contain sampled unit outcomes. The combination of `lot_id`
and `unit_sequence` is unique, so repeated test attempts cannot be inferred.

A seeded deterministic synthetic retest source will demonstrate retest
modeling. Every synthetic record will be explicitly labeled.

## 4. OEE source

Observed equipment events provide alarms, states, and downtime information but
do not represent a complete operating schedule.

Standard OEE will therefore use a separate seeded synthetic hourly operations
source. Observed equipment events remain in a separate fact table.

## 5. Production day

Source timestamps remain in UTC. Reporting timestamps are converted to
Asia/Taipei.

The production date is calculated using an 08:00 local production-day boundary.

## 6. Tester logs

`silver.tester_logs` currently contains zero rows. It is excluded from the
redesigned Gold model.

Repairing the tester-log parser is deferred until the base reporting model is
complete.

## 7. Historical-retention audit

The repository audit reviewed 36 code-bearing files, including 26 Databricks
notebooks.

No current-date or latest-only business filter was found that removes the
five-year reporting history.

Existing Gold `CREATE OR REPLACE TABLE` statements rebuild legacy tables from
complete Silver history. Redesigned persistent mappings and incremental facts
will use idempotent processing during Days 2–4.

Display limits, processing timestamps, fixed validation dates, and descriptive
uses of “latest” do not restrict business history.

The workflow-quality-metrics deletion is recorded for run-scope verification
during the Day 5 governance review.

## 8. Portfolio disclosure

GitHub and Power BI will distinguish fields and datasets as:

- SOURCE
- DERIVED
- MAPPED
- SYNTHETIC

Synthetic test-batch, retest, and OEE data will not be represented as actual
factory genealogy or observed operational measurements.