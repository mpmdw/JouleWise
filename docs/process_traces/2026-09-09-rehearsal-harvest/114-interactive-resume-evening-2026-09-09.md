# 114 — Interactive resume after usage exhaustion and a machine sleep (2026-09-09 evening)

Author: interactive Fable magistrate (Claude Code session `01MrRehZWopqKNDv5Uy466AC`), bench = canonical `/Users/edr/code/JouleWise`.
Wall clock at write: ~20:48 PDT. Every fact below was executed or read this session unless marked otherwise.

## What happened after checkpoint T38e (~17:05 PDT)

Headless activation `2145630c` finished PR #312's gauntlet (seat 108, refuters 110/111, terminal review 112, replay 113: 6e0bbf67 alone,
5653 tests rc 0) and pushed its traces (`02f9d75c`, `cba9b6a4`); CI green on both. It did not reach the merge. The watchdog's
`~/night-custody/magistrate/events.jsonl` then records (epoch → PDT converted by the bench):

```
seq 28  18:21:31  ACTIVE → BACKOFF        session exit=1 class=generic_error   (launch_failure)
seq 31  18:28:37  ACTIVE → BACKOFF_USAGE  session exit=1 class=usage_exhausted
seq 33  18:48:32  LAUNCHING → ACTIVE      spawned activation 517e8df5
seq 34  18:48:42  ACTIVE → BACKOFF_USAGE  session exit=1 class=usage_exhausted
seq 36  19:23:41  LAUNCHING → ACTIVE      spawned activation 11f3e9b0
seq 37  19:23:51  ACTIVE → BACKOFF_USAGE  session exit=1 class=usage_exhausted
seq 38  20:37:15  BACKOFF_USAGE → CLOCK_UNCERTAIN  wall and monotonic deltas disagree
```

Each relaunched activation exited within ten seconds with the usage-exhausted class (the Claude usage window). The CLOCK_UNCERTAIN
transition is the sleep signature: at 20:35 the bench found the laptop on battery (`pmset -g batt`: 98 %, discharging) with the
battery profile `sleep 1` / `displaysleep 5`, i.e. the machine had been unplugged and idle-slept, which stops launchd ticks and every
resident process. Ed's report ("the machine stops when the system falls asleep") matches.

## Actions this session

1. Local main fast-forwarded `83ab38ed → cba9b6a4`; 27 untracked trace files in `docs/process_traces/2026-09-08-handoff-redo/` were
   byte-identical to their tracked origin/main copies (diffed one by one) and were removed so the fast-forward could proceed.
2. **PR #312 merged at `7e294284`** (`gh pr merge --merge`; tests only, production diff empty). Gate shape at merge: refuters 110 (Astra
   execution) and 111 (Opus contract, 0 blockers), no fix round, terminal review 112, replay 113 rc 0, all CI checks pass on 6e0bbf67,
   gate ledger present in the PR body (CI `gate-ledger` job pass), no commit after the review. Ruling 111's note stands: not recorded
   against ARM-INTEGRATION-LOAD-01's under-load clause.
3. **Watchdog held, not raced.** `state.json` showed `CLOCK_UNCERTAIN` with `clock_sane_samples` climbing toward the two-sample recovery,
   after which `decide()` would have launched a headless activation alongside this interactive one (no launch predicate inspects
   interactive sessions; only lock owners and resumed twins). The documented local switch `~/night-custody/magistrate/STOP`
   (docs/process/MAGISTRATE_WATCHDOG.md §local switch) was placed for the duration of this bookkeeping and lifted at hand-back.
4. **Sleep guard.** Ed plugged the laptop in during the session. Observed 20:45 PDT (`pmset -g custom`, AC Power): `sleep 0`,
   `displaysleep 0`, `powermode 0` (Automatic). A user LaunchAgent `com.edr.keepawake` running `/usr/bin/caffeinate -i -s` was installed
   at 20:41 as a no-sudo guard and REMOVED at 20:46 (`launchctl bootout`, plist deleted): `_derive_process_census` in
   `joulewise/arm_readiness_evidence_t0.py` runs `/usr/bin/pgrep -x caffeinate` and `_expect_absent` refuses any hit
   (`t0.no_stray_keepawake`), and docs/phase_2/window_runbook.md §E-10 states the chain's own `caffeinate -is` is the one reviewed
   keep-awake. On AC the profile already never sleeps, so the agent's only value was on battery, where the loop is dead anyway.
   After removal `pgrep -lf caffeinate` shows only the Claude Code harness's own transient `caffeinate -i -t 300`.
5. Residual sleep risk that no agent can remove: a closed lid (needs Ed's `sudo pmset -a disablesleep 1` if he ever wants it closed) and
   unplugging (battery profile sleeps after one minute). The standing machine state in the decision log — lid open, AC attached — is the guard.
6. The same census refuses any interactive `claude`/`codex`/`t3` process at arm authoring (`agent` probe), so every interactive session,
   including this one and any second Terminal/T3 session, must be closed before the 2026-09-10 03:00–06:30 install window.

## Not done here

No kernel row changes (PR #312 has no row; consult 99's follow-up is recorded on PR #311's terminal review 96). No arm, no install,
no night action. Next exact action unchanged: the headless activation alive in the 09-10 03:00–06:30 PDT window executes runbook 67.
