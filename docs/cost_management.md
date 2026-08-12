
# Cost Management

## Budget policy

- Absolute Azure ceiling: USD 100
- Operational stop: USD 80
- Protected billing-delay reserve: USD 20

## Cost controls

- Dedicated single-node development compute
- Ten-minute automatic termination
- Manual termination after every development session
- Serverless SQL warehouse with automatic stop
- Development-scale synthetic datasets
- Triggered rather than continuously running streams
- Temporary resources paused or removed after demonstration
- Cost reviews before and after major workload runs

## Spending gates

- USD 25: Review the detailed cost report.
- USD 50: Optimize and approve remaining paid runs.
- USD 70: Remove optional paid demonstrations.
- USD 80: Stop paid project processing.
- USD 80–100: Protected billing-delay reserve only.

## Cost ledger

| Date | Activity | Starting cost | Ending cost | Increment | Notes |
|---|---:|---:|---:|---:|---|
| 2026-08-12 | Environment verification | TBD | TBD | TBD | Existing course-environment baseline |
| 2026-08-13 | Unity Catalog foundation | TBD | TBD | TBD | Short single-node compute session |
