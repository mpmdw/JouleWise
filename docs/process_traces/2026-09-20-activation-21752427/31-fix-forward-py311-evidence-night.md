# Record 31 — fix-forward after PR #372: the hosted Linux 3.11 shard has no `python3.13` (2026-09-20 09:50–10:00 PDT)

## §1 Defect (executed evidence)
Post-merge run 35522762217 on main `2b6cb947`: `test (3.11, 5)` FAILURE, fail-fast cancelled eight shards; 3.13 shards 3/4 and 3.11 shards 3/6 passed. Job 106109917369 log (`/tmp/magistrate-21752427/pm372-shard5.log` lines 1430–1660): 13 `tests.test_evidence_night.PrepareTests` errors, every one `FileNotFoundError: [Errno 2] No such file or directory: 'python3.13'` raised from `joulewise/evidence_night.py:379 run(["python3.13", "--version"])` on the pre-clone path — round 2's C9 added the bench step-1 probe unconditionally; the hosted 3.13 runners have `python3.13`, the 3.11 runners do not; the PR matrix runs only 3.13, so the PR head was green and the post-merge matrix caught it (Ed's 09-16 ruling: fix forward).

## §2 Fix (branch `fix/2026-09-20-evidence-night-py311`, `8963dcf0` + `ab95e377`, diff gate by the magistrate)
The probe moves INTO `build_venv` (the real recipe: `python3.13 --version` → `python3.13 -m venv .venv` → the two constrained installs → exact-lock freeze) — offline tests inject a builder, so the prepare path never needs `python3.13` on the host; the recipe test asserts the probe as the builder's first call, and the prepare test asserts it ABSENT from the prepare path. First push (`8963dcf0`) broke those two assertions at the bench (the lead pushed before re-running the module — corrected within four minutes by `ab95e377`; lesson: run the module before every push, even for a three-line move).
Bench (both interpreters, module alone):
```
/opt/homebrew/bin/python3.11 -B -m unittest -q tests.test_evidence_night → Ran 23 tests in 66.559s (first attempt: FAILED 1+1) → after ab95e377: OK
/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -q tests.test_evidence_night → OK
```
Replay for row 9: the delta is one module + its test; the round-1 full replay (record 26 §2, 6,637 tests) covers the surrounding suite; module re-run alone on both interpreters above; hosted matrix on the PR head + post-merge.

## §3 Counter-review (rows 1/2/6/10)
(appended: Opus review)

## §4 Terminal review (row 12) and hosted result (row 11)
(appended before merge)
