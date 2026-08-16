## Authoritative yield quantities

The authoritative lot-level quantity source is
`semiconplus_portfolio.silver.production_lots`.

- input_quantity = quantity_started
- first_pass_good_quantity = quantity_passed
- first_pass_fail_quantity = quantity_failed
- lot_fpy = quantity_passed / quantity_started

The following invariant was confirmed across the accepted Silver dataset:

quantity_started = quantity_passed + quantity_failed

Stored yield percentages are retained for reconciliation only. Aggregated
Power BI measures will be recalculated from summed quantities.

## Unit-test result purpose

`silver.unit_test_results` contains ten sampled unit results per production lot.
It supports defect, test-time, program-revision, equipment, and lot
investigation. It is not the authoritative production-quantity source.

`unit_sequence` identifies sampled units within a lot. No repeated
lot/unit-sequence records exist; therefore, it cannot be interpreted as a
test-attempt or retest sequence.

## Retest limitation and resolution

The existing generated dataset does not contain explicit retest input, retest
pass, retest fail, or test-attempt fields. Retest metrics will not be inferred
from sampled unit-test results.

A dedicated deterministic synthetic retest source will be generated and
processed through Bronze, Silver, and Gold. Retest quantities must reconcile
to each lot's first-pass failed quantity.

## Lot hierarchy

Mother-lot, sublot, and wafer-batch identifiers are not present in the source.
Stable deterministic mappings will be generated, persisted, and clearly
documented as simulated portfolio attributes.

## Equipment-event support

The source supports event-level equipment-state, downtime, alarm, duration,
site, equipment, and UTC timestamp analysis. Event end timestamps and local
timestamps will be derived.

## OEE limitation and resolution

Equipment-event records do not represent complete daily scheduled-time
coverage. Average observed event time is approximately 10,637 seconds per
equipment/day.

A deterministic equipment operating-calendar source will provide scheduled
time. Availability and utilization will not use observed-event duration as a
substitute for scheduled production time.

## Planned-overrun limitation

Current generated event durations do not exceed 3,600 seconds. Controlled
planned-overrun events will be added so the greater-than-60-minute rule can be
tested and demonstrated.

## Tester-log limitation

Bronze contains 18,125 tester-log records, while the current Silver tester-log
table contains zero records. The redesigned Gold model will not depend on this
table unless its parsing pipeline is repaired and reconciled.

## Simulated test-batch hierarchy

The generated source does not contain physical mother-lot or sublot genealogy.
The model therefore does not present derived identifiers as manufacturing
mother lots or material sublots.

For analytical drill-down, source production lots are grouped into simulated
test batches by stable device code and configurable production day.

Identifier format:

- test_batch_id = YY + device_code + MMDD
- test_lot_id = test_batch_id + T + three-digit stable sequence

Example:

- test_batch_id: 21DV0070501
- test_lot_id: 21DV0070501T001

The production date is based on lot completion time converted to Asia/Taipei,
using an 08:00 local production-day boundary.

Lot completion time is derived from the maximum unit-test event timestamp for
the source lot, with the production-lot start timestamp used only as a fallback.

The test-batch hierarchy is a deterministic simulated analytical grouping. It
does not represent source material genealogy or physical mother-lot lineage.

Mappings are persisted. Existing source-lot-to-test-lot assignments are never
renumbered during incremental processing.