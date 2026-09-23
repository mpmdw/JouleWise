# Activation f2d6899b — lead bench notes (Opus 5.5 magistrate), 2026-09-23

## 1. Full-suite replay at the unreviewed seat head `31124f68`

Command, from `/Users/edr/code/wt-5fe5a59b-a234`: `/Users/edr/code/JouleWise/.venv/bin/python scripts/shard_tests.py --workers 8 --split` (log `/tmp/f2d6899b/replay-31124f68.log`).
Result: exit 0; eight shard summaries all `result=PASS`: 48 + 676 + 1,009 + 958 + 950 + 1,207 + 1,212 + 854 = 6,914 tests, 0 failures, 0 errors, 103 skipped.
This closes the seat's flag F1 (pytest was missing in its environment) for `31124f68` only. The fix head needs its own replay.

## 2. F3 fix round: the one-way latch (a defect in the fix seat's round, fixed at the bench)

In its round, the Sol seat made the release census-backed. After `courier.sent` exists, the watchdog censuses on every tick and records the release in `state.json` only on a tick whose census is empty. Its code also removed that record whenever a later census came back non-empty ("a later non-empty census restores the hold").
That breaks the feature. Once the release is recorded, the watchdog returns `LAUNCHING` and starts a magistrate. The magistrate is a `claude` process, so it matches the census pattern (`[c]odex|[c]laude|[t]3`), and the next tick's census is non-empty. The release record is then removed, `plan_is_armed` is true again, the checkout fence returns, and `decide()` returns `HOLD_CENSUS` with a notice for as long as the magistrate runs. That would undo the early release for the rest of the nominal window.
Bench fix (commit `4c76ab69`): released keys are never removed while their plan is loaded. They are pruned only when the plan is no longer loaded, and the census runs only for candidates that have not been released yet. Regression test `test_delivered_refusal_release_is_one_way` replaces the seat's `test_delivered_refusal_rechecks_census_after_recorded_release`, which asserted the defective behaviour. Mutation check: a mutant that restores the un-release makes the new test fail (`1 failed`), and the latched code passes it.
Focused run at `4c76ab69`: the watchdog, CLI, arm_retry, installer, evidence_night and docs-freshness modules gave 296 passed with 754 subtests.

## 3. A271 bench facts

- Real log text: `/usr/bin/log show --last 24h --style syslog --predicate 'process == "launchd" AND eventMessage CONTAINS "corecaptured"'` returned 1,212 lines. Those are 605 `Successfully spawned corecaptured[PID] because xpc event` lines and 606 `service inactive` lines, all from the 09-22 loop. The last spawn was 01:20:06 PDT 09-23; none have appeared since (the Wi-Fi toggle cure was at 01:41). The Sol sandbox cannot run `log` ("Cannot run while sandboxed"), so the lead captured the fixtures.
- Timing of the new t0 read, measured twice: 1.46 s and 1.19 s wall (`/usr/bin/time -p`).
- Detector on real data, from the production module at `f81e34ec`: the live 10-minute read gives count 0. The 09-22 fixture evaluated at its last line gives count 8. Across the full 24 h loop capture, the maximum per 10-minute window is 8, far above the threshold (more than 2).
- Design ruling given to the seat (record 05): t0 is detection-only; remediation (the Wi-Fi toggle, a 180 s wait, a recount of post-toggle spawns, and one fseventsd restart) happens only in the arm check.
- Focused run at `f81e34ec`: 231 passed with 648 subtests.
- Residual risk, recorded for the refuters: the t0 probe runner has no timeout. A hung `log show` at t0 would hang the gate. The existing probes (pgrep, ps) share that property.
