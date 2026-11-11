Committed `393d93fdc` on `ops/2026-11-11-w1-offload-r2`. Working tree clean; no push.

- Added O-1 tests for conflicting receipts (exit 3, receipt retained, no upload) and unreachable `stat` (exit 5, receipt retained).
- Added O-2’s docstring sentence. No executable or release/deletion logic changed.
- Appended “Round 2” to the [run report](/Volumes/JW-EXT/jw-wt/sol-w1-offload-r2/docs/run_reports/2026-11-11-w1-offload.md:208), including exact test commands and red/green evidence.

All **221 targeted tests pass**. The 17-state characterization is unchanged, and the forced-true mutant is killed. Compile and diff checks pass.

Limitations: the fixture census failed because sandboxed `ps` was denied. Lead review and isolated remote native checks remain. No implementation questions remain.

The initial broad Git ruling read included Block 5 summaries; no real custody or measurement data was accessed.