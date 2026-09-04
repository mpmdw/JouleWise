# Magistrate watchdog — Sol fix round 4

Date: 2026-09-04 PDT  
Base/HEAD at intake: `4a23c1191460ebb9ae173bdbb3ce11b1990937b3`  
Branch: `feat/2026-09-03-magistrate-watchdog`  
Install/session/commit actions: none.

## Finding → cure → evidence

| Finding | Cure | Biting evidence |
|---|---|---|
| B-1: the integrated watcher held on retired-v1 custody and its fixture/examples were v1 | Every sibling plan is still parsed through `NightPlan.from_mapping`. Retired v1 and otherwise unparsable plans now append one durable event per custody root (`plan_retired_v1` or `plan_unparsable`) and contribute neither a span nor `HOLD_UNSAFE`. The fixture and both runnable doc plans are v2 with measurement pins. | The mixed-root regression sees only the valid-v2 span and one durable ignored event even through a fresh `Storage`; a second test pins the general unparsable path. The required mutation makes `decide` hold on v1 and fails the new test with `HOLD_UNSAFE != FENCED`. |
| M-2/M-3: daemon/spare and PID-1 residues escaped the adopted tree | Added read-only `handoff-inventory`. From the invoking ancestry it selects the Terminal-hosted interactive twin and its descendants; it also selects PID-1 `--bg-pty-host` and shell-snapshot orphan roots and their descendants. It emits PID/start/command rows, excludes its transient caller chain, and never signals. | The fake process-table test includes twin, daemon, host, spare, both orphan trees, unrelated Codex, and unrelated Claude; only the ruled set is returned and the signal log stays empty. |
| M-2/M-3 + Q4: install handoff lacked an executable order | Replaced the install handoff with the ruled six-step checklist: stop tasks; preserve both old custody trees under `retired-v1`; capture `handoff-<epoch>.json`; install; run a detached PID/start-revalidating reaper that signals only the recorded list and proves the production census empty; verify that the next launchd tick creates the first watchdog-owned `-p` attempt. | A documentation contract test pins the six actions in order and the never-kill-unowned sentence. The checklist cites the launchd proof in file 17n on main. No handoff was executed in this session. |
| Q4: the install checkout was not explicit in the relaunch/handback text | The relaunch prompt (23 lines), handback, and watchdog doc now require v2 plans and installation of both night agents FROM the plan's `measurement_root` at `measurement_head`. | Prompt and handback contract assertions pin v2, FROM, and `measurement_root`. |

## Required verification

Watchdog module, exit 0:

```text
...........................................
----------------------------------------------------------------------
Ran 43 tests in 0.095s

OK
```

Watchdog plus night-gate modules after all implementation/doc edits, exit 0:

```text
..........................................................................................
----------------------------------------------------------------------
Ran 90 tests in 0.637s

OK
```

Executed v1-hold mutation, expected exit 1:

```text
AssertionError: 'HOLD_UNSAFE' != 'FENCED'
- HOLD_UNSAFE
+ FENCED

----------------------------------------------------------------------
Ran 1 test in 0.004s

FAILED (failures=1)
```

Required integrated command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_night_gate tests.test_run_night
```

Its first run reached 144 tests and failed seven `tests.test_run_night` installer cases. All seven copied the fixed fixture `authored_epoch_s = 2026-09-02 00:59 local`; on 2026-09-04 the merged install validator correctly refused it as `night_plan_stale: plan is older than 36 hours` before each intended assertion. `tests/test_run_night.py` and `scripts/install_night_agent.sh` are outside this round's exhaustive write scope, so neither freshness nor the unowned fixture was changed.

Final rerun, exit 1 tail:

```text
AssertionError: 3 != 0 : night_plan_stale: plan is older than 36 hours

----------------------------------------------------------------------
Ran 145 tests in 5.401s

FAILED (failures=7)
```

## Scope and residual gates

Only runner-authorized paths were modified. No package was installed, no launchd or night action ran, no custody tree was touched, no additional Claude/Codex session was started, and no commit was created. The watchdog cure is focused-green; the required integrated acceptance remains pending correction of the time-expired installer fixture in `tests/test_run_night.py` by the lead or a newly scoped round. The minimal scope expansion is that single path so `_installer_plan` can refresh `authored_epoch_s` for installer-specific fixtures without weakening the 36-hour production check.
