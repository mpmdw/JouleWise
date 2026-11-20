Committed locally on `analysis/2026-11-11-b5-ledger-ext`:

- `87a698c0f`: extended table / print-authority candidate.
- `5e210562d`: round-2 report.

Added **618 rows**, bringing the ledger to **1,419**. All 801 prior rows remain byte-identical. Six custody files passed before/after hash checks. No new mismatch or outside-unseal source; row 249 remains the sole, previously ruled mismatch.

Changed the ledger, `REDERIVATION.md`, a new stdlib checker, the existing test module, and the [run report](/Volumes/JW-EXT/jw-wt/sol-p1-b5-ledger-ext2/docs/run_reports/2026-11-11-p1-b5-ledger-ext.md).

Verification: `python3.13 -B -m unittest tests.b5_analysis.test_hand_check_phase2` — **37 passed**. Independent replay and integrity checks passed. RESULTS and protected coordination files are unchanged.

BETA decode’s registered load-line refusal remains visible beside the uncompared RC result. Next: Opus cold review and lead adjudication. No additional ruling requested. Working tree clean; nothing pushed.