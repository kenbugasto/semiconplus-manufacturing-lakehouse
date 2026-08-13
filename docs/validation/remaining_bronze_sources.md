# Remaining Bronze Sources Validation

## Sources loaded

- 60 equipment-event TSV files: 255,640 records
- 60 unit-test-result JSON files: 181,250 records
- 60 tester LOG files: 18,125 records
- Four reference CSV files: 63 records
- 25 binary maintenance documents
- Two source manifest files

All file-based records retain source lineage and pipeline-run metadata.
Auto Loader sources use independent schema and checkpoint locations.

The 60 streaming-event JSON files remain unprocessed and are reserved for
the Structured Streaming implementation.

## Validation

- Source and target record controls passed
- Source-file coverage passed
- Lineage completeness passed
- Reference-key checks passed
- Binary payload checks passed
- Rescued-data review passed
- Checkpoint idempotency passed

## Result

Status: PASSED