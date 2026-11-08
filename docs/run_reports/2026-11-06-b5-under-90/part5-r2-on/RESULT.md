# Block-5 part 5: r2-on

Synthetic S10 fixtures only. The run used `python3.12`, 2 workers on an `nproc` count of **3**, and completed without the outer timeout in **2375.509 s**. The harness exit code was **2** because `--stop-after 5` produced the expected step 8 `synthetic_stop_after` refusal.

| Step | Wall (s) | Status |
|---|---:|---|
| 0 | 15.713 | ok |
| 1 | 324.579 | ok |
| 2 | 17.491 | ok |
| 3 | 0.808 | ok |
| 3b | 570.478 | ok |
| 4 alpha | 280.508 | ok |
| 4 beta | 280.508 | ok |
| 5 | 1164.235 | ok |
| 8 | 0.074 | unclassified_refusal (`synthetic_stop_after`) |
| 6 | — | not_run |
| 9 | — | not_run |
| 9b | — | not_run |
| 10 | — | not_run |
| 11 | — | not_run |

No step before step 4 refused, so no pre-step-4 refusal diagnosis applies.
