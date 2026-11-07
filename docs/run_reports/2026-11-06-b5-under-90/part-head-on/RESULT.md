# Block-5 head-on result

- Host: `nproc = 3`; Python 3.12.13; 2 workers; committed synthetic S10 fixtures only.
- Run: completed in 1001.716 s (exit 2). The nonzero exit is the requested `--stop-after 4` boundary: step 5 records raw code `synthetic_stop_after` (`step-codes.jsonl:8`), not a pre-step-4 refusal.

| Step | Wall (s) | Status |
|---|---:|---|
| 0 | 17.683 | ok |
| 1 | 335.443 | ok |
| 2 | 18.980 | ok |
| 3 | 0.813 | ok |
| 3b | 338.621 | ok |
| 4 alpha | 288.615 (shared step wall) | ok |
| 4 beta | 288.615 (shared step wall) | ok |
| 5 | 0.041 | unclassified_refusal (`synthetic_stop_after`) |
| 8, 6, 9, 9b, 10, 11 | — | not_run |

No step before 4 refused. Step 4 completed successfully for both alpha and beta; its cell-level fail-closed messages are retained in `failure-logs/`.
