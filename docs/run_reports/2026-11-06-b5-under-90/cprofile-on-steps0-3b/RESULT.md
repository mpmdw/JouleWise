# head-cprof result

- **Synthetic data only:** committed S10 fixtures.
- **Host:** `nproc = 3`; Python 3.12; 2 workers.
- **Run:** completed without the 3000-second timeout in 1795.171 seconds. Steps through `3b` succeeded; the requested `--stop-after 3b` then produced the expected step 4 synthetic refusal (`synthetic_stop_after`).

| Step | Wall seconds | Status |
|---|---:|---|
| 0 | 26.229 | ok |
| 1 | 852.480 | ok |
| 2 | 29.183 | ok |
| 3 | 1.309 | ok |
| 3b | 884.437 | ok |
| 4 | 0.027 | unclassified_refusal (requested synthetic stop) |
| 5 | — | not_run |
| 8 | — | not_run |
| 6 | — | not_run |
| 9 | — | not_run |
| 9b | — | not_run |
| 10 | — | not_run |
| 11 | — | not_run |

No step before `3b` refused. The dominant costs were step 1 (`k.anchor`/`k.pm_parse` in validation workers) and step `3b` (`w.future` under `op.brackets`); see `detail.txt` and `report.txt` for the profile breakdown.
