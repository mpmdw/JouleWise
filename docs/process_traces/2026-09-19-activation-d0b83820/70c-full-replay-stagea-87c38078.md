# Record 70c — full sharded replay at the FINAL head `87c38078` (`87c380781d7025cde9954a28309bc45ede3a38db`), 2026-09-19 17:24–18:09 PDT

Branch worktree `JouleWise-wt-stagea-d0b83820` fast-forwarded to `87c38078` and untouched during the run. `scripts/shard_tests.py --workers 4 --split`. Log: `70c-full-replay-stagea-87c38078.log.gz`.

| shard | modules | tests | failures | errors | skipped | result |
|---|---|---|---|---|---|---|
| 1 | 60 | 1438 | 0 | 0 | 13 | PASS |
| 2 | 61 | 1494 | 0 | 1 | 2 | FAIL |
| 3 | 62 | 1893 | 0 | 0 | 81 | PASS |
| 4 | 62 | 1757 | 0 | 0 | 7 | PASS |

Total 6,582 tests / 245 module runs (244 PASS). The one error is once more `tests.test_arm_readiness_evidence_t0.test_g4_real_ruled_census_pgrep_dialect` (fresh-eyes seat 83 was alive for the run's first quarter-hour; the TEST-PGREP-DIALECT-MULTILINE-01 class). The module was then run ALONE at `87c38078` with no seat alive (`70c-census-module-alone-87c38078.log`): **76 tests OK in 570 s**. No Stage A module failed in any of records 60/70/70b/70c.
