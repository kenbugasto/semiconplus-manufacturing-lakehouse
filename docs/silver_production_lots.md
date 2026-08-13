# Silver Production Lots Validation

## Transformation

The Silver pipeline standardizes Bronze production-lot records, applies
approved business data types, removes duplicate business keys, validates
device references, reconciles quantities, and recalculates yield.

Accepted records are written to:
`semiconplus_portfolio.silver.production_lots`

Rejected records are written to:
`semiconplus_portfolio.quarantine.production_lots`

## Quality controls

- Required production-lot identifiers
- Strict date, timestamp, quantity, and yield types
- Deterministic lot-level deduplication
- Device-reference validation
- Quantity reconciliation
- Valid yield range
- Rescued source-field detection
- Bronze-to-Silver/quarantine reconciliation
- Repeatable transformation reruns

## Quarantine behavior

The deliberately injected duplicate lot and unknown-device record remain
available in quarantine with explicit rejection reasons and source lineage.
Valid records continue through the pipeline.

## Result

Status: PASSED