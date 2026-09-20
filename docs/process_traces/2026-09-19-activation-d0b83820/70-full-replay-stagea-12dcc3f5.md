# Record 70 — full sharded replay at the reviewed Stage A head `12dcc3f5`, 2026-09-19 15:03–16:04 PDT

Branch worktree `JouleWise-wt-stagea-d0b83820` at `12dcc3f5` (untouched during the run; the bench commits went to a different worktree). `scripts/shard_tests.py --workers 4 --split` → four shards. Log: `70-full-replay-stagea-12dcc3f5.log.gz`.

| shard | modules | tests | failures | errors | skipped | result |
|---|---|---|---|---|---|---|
| 1 | 60 | 1787 | 0 | 0 | 76 | PASS |
| 2 | 61 | 1665 | 0 | 1 | 5 | FAIL |
| 3 | 61 | 1677 | 0 | 0 | 20 | PASS |
| 4 | 62 | 1412 | 0 | 0 | 2 | PASS |

Total 6,541 tests / 244 modules; 243 modules PASS; the one error is `tests.test_arm_readiness_evidence_t0.test_g4_real_ruled_census_pgrep_dialect` (pattern `powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)`): the real-process census matched a live delegated seat whose argv (the review brief, which names `powermetrics`) is multi-line — the TEST-PGREP-DIALECT-MULTILINE-01 class seen in records 14/34/60; at the time of writing `pgrep -lf` on that pattern still returns the seat pids `79986 #  `. Environmental; the module is re-run alone at the final head after the last seat ends (record 70b carries that re-run). No Stage A module failed; the two cross-module findings of record 60 (generated policy block, direct git init) are gone at this head.
