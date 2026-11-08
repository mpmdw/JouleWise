# Part 5 — HEAD stack samples

- **Host:** 3 logical CPUs (`nproc`)
- **Run:** completed without timeout in 2,232.041 s; the driver exited 2 and the wrapper exited 1 because `--stop-after 5` produced the expected step 8 `synthetic_stop_after` refusal.
- **Synthetic data only:** yes

| Step | Wall (s) | Status |
|---:|---:|---|
| 0 | 16.773 | ok |
| 1 | 321.916 | ok |
| 2 | 17.098 | ok |
| 3 | 0.783 | ok |
| 3b | 330.068 | ok |
| 4 alpha | 280.464 | ok |
| 4 beta | 280.464 | ok |
| 5 | 1263.268 | ok |
| 8 | 0.061 | unclassified_refusal (`synthetic_stop_after`) |
| 6, 9, 9b, 10, 11 | — | not_run |

No step before step 4 refused.
