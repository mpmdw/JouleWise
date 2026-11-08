# Block-5 `head-on` result

- **Host:** `nproc` = 3; Python 3.12.13 (`python3.13` was unavailable).
- **Run outcome:** completed without timeout in 1618.440 s; driver exit code 2 because the requested `--stop-after 5` produced the `synthetic_stop_after` control refusal at step 8.
- **Synthetic-data scope:** committed S10 fixtures only (`synthetic_only: true`).

| Step | Wall seconds | Status |
|---|---:|---|
| 0 | 18.256 | ok |
| 1 | 319.902 | ok |
| 2 | 16.017 | ok |
| 3 | 0.733 | ok |
| 3b | 313.092 | ok |
| 4 alpha | 146.259 (shared step wall) | ok |
| 4 beta | 146.259 (shared step wall) | ok |
| 5 | 802.486 | ok |
| 8 | 0.056 | unclassified_refusal (`synthetic_stop_after`) |
| 6, 9, 9b, 10, 11 | — | not_run |

No step before step 4 refused. The two step-4 fail-closed cell refusals are recorded in `failure-logs/0529-4-alpha.stderr.log` and `failure-logs/0530-4-beta.stderr.log`; the harness classifies both window statuses as `ok`.

## L4 calibration-bracket counters

- `L4_calibration_bracket:fill`: 3
- `L4_calibration_bracket:hit`: 6
- `L4_calibration_bracket:miss`: 6
