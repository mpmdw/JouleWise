# Record 03a — bench addendum (activation 28ff4b28): module run, full replay, class rerun on the quiet machine, orphan census

All executed this session by the magistrate in `JouleWise-wt-argv-f0b608b7` with `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B` (Python 3.14.7).

## Whole module at e32ea56c (round 0), 20:20 PDT
`python3 -B -m unittest tests.test_run_night` → `Ran 184 tests in 92.785s — OK` (log `/tmp/mag-28ff4b28/test_run_night_module.log`, rc 0).

## Full sharded replay at 3855ad25 (fix round 1), 20:26–21:09 PDT (record 08)
`python3 -B scripts/shard_tests.py --workers 4 --split` → rc 0; 4 shards; summed `Ran N tests` lines = 6,426 tests; 241 `OK` module lines; 0 `FAILED`, 0 `ERROR:`/`FAIL:` lines. Ran concurrently with the Astra delta re-audit seat (load average peaked ≈ 7.2 with fseventsd/mds indexing active after Ed's 17:40 reboot), which is why the delta seat's own class run hit the external 8 s watchdog on `journal_block` and `startup_hang` (record 06 V-GAP-01; lane TEST-BIND-SUPERVISION-ENV-SENSITIVITY-01, kernel 237, is exactly this sensitivity). Exact log: `08-full-replay-3855ad25.log.gz`.

## Class rerun at 3855ad25 on the quiet machine, 21:10 PDT (closes record 06 V-GAP-01)
Load average 1.69 at start, no seats alive. `python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests` → `Ran 22 tests in 30.743s — OK`.

## Fixture-orphan census (record 06 ENV-01; the seat sandbox denied `ps`)
`ps -eo pid,args | grep -E 'python[^ ]*.* [^ ]*bind_supervision\.py' | grep -v grep` → empty after the module run, the replay, the three refuter seats and the class rerun. No orphaned bench workers.

## Hosted CI on 3855ad25 (PR #359, run 35418532801)
All jobs green except `gate-ledger` (rows still PENDING at that time): quick, build, fences, installed-wheel, calibration-exits-exclusive, calibration-writer-crash-matrix-exclusive ×2, test (3.13, 1–6). **`test (3.13, 5)` passed in 11m24s — the Linux execution of the counterfactual that was red twice on main `b55909e3`.**
