```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round 4 is RESIDUAL: the unit suite is green, but the production v2-span path crashes, malformed v2 plans fail open, the handoff can target unowned PIDs, its reaper is not PID-race/survivor safe, and the prompt does not fence arbitrary plan measurement roots.",
  "workspace": {
    "base_requested": "4a23c119",
    "base_mode": "exact",
    "head_start": "1e324e3d40ea956610cf0df627fde7e47b93749b",
    "head_end": "1e324e3d40ea956610cf0df627fde7e47b93749b",
    "upstream_end": "a39e33a20561eed48381fa91d42e7c7bfcdd3adb",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [
    "docs/process_traces/2026-09-03-watchdog-build/10-delta-reaudit-round-4.md"
  ],
  "unowned_dirty": [
    "M docs/process_traces/2026-09-03-watchdog-build/01-sol-landing-report.md",
    "?? docs/process_traces/2026-09-03-watchdog-build/09-sol-fix-round-4-report.md"
  ],
  "verdict": {
    "line": "RESIDUAL (F1, F2, F3, F4, F5)",
    "cures": {
      "B-1": "NOT CURED",
      "M-2": "NOT CURED",
      "M-3": "NOT CURED",
      "Q4": "NOT CURED",
      "Q5": "NOT CURED",
      "Q1 installer checks": "CURED",
      "Q2 SUPERVISOR_POLL_S pin": "CURED"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The real watchdog crashes on every active valid-v2 plan",
        "evidence": "scripts/magistrate_watchdog.py:334-342 omits Probes.measurement_head, required at joulewise/night_gate.py:163-169; the hand-built real CLI raised TypeError before state.json was written.",
        "counterfactual": "One valid v2 plan whose span is active, with or without a retired-v1 sibling."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Round 4 makes corrupt, unreadable, and invalid-v2 plans fail open",
        "evidence": "scripts/magistrate_watchdog.py:535-551 catches every Exception, records plan_unparsable, and never fills plan_errors; decide can therefore reach LAUNCHING at :893-952.",
        "counterfactual": "An armed schema-v2 plan missing measurement_head produced decision=LAUNCHING and launch=true."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "handoff-inventory includes PPID-1 lookalikes with no magistrate-tree provenance",
        "evidence": "scripts/magistrate_watchdog.py:711-722 unions every matching global orphan into the kill list; the executed counterexample listed PIDs 700/701 outside the interactive tree.",
        "counterfactual": "Another live Claude session owns a PPID-1 --bg-pty-host and child while this magistrate invokes handoff-inventory."
      },
      {
        "id": "F4",
        "severity": "blocker",
        "title": "The documented detached reaper does not uphold its PID/start and survivor claims",
        "evidence": "docs/process/MAGISTRATE_WATCHDOG.md:145-172 snapshots once before all TERM calls and never rechecks recorded survivors after KILL; success depends only on the narrower production census.",
        "counterfactual": "A recorded PID exits and is reused between the initial snapshot and TERM, or a recorded non-agent descendant remains live after KILL while the agent census is empty."
      },
      {
        "id": "F5",
        "severity": "blocker",
        "title": "The relaunch prompt fences one literal checkout, not the armed plan's measurement_root",
        "evidence": "docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:9-13 hard-codes /Users/edr/JouleWise-measurement-20260813, while NightPlan accepts any absolute measurement_root at joulewise/night_gate.py:238-245.",
        "counterfactual": "A valid v2 plan using /private/tmp/alternate-measurement-checkout parses, but that root is absent from the 23-line prompt."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_magistrate_watchdog.FenceTests.test_retired_v1_is_ignored_once_and_only_v2_plan_sets_span",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.004s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test.*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from scripts.magistrate_watchdog import production_census; production_census()'",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["TypeError: Probes.__init__() missing 1 required positional argument: 'measurement_head'", "state.json absent after CLI"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from scripts.magistrate_watchdog import *;P=ProcessInfo;r=[P(9,8,\"\",\"x\"),P(8,1,\"\",\"claude x\"),P(7,1,\"\",\"claude --bg-pty-host x\")];print(handoff_inventory(r,9)[\"pids\"])'",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["[7, 8]"]},
      "expected": {"exit_code": 0, "tail_regex": "^\\[8\\]$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; p=Path(\"docs/process/MAGISTRATE_RELAUNCH_PROMPT.md\").read_text(); print(len(p.splitlines()))'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["23"]},
      "expected": {"exit_code": 0, "tail_regex": "^(?:[1-9]|1[0-9]|2[0-5])$"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 scripts/magistrate_watchdog.py --dry-run --custody-root /private/tmp/watchdog-r4-v1only.SA3OLV/magistrate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["decision=NETWORK_UNCERTAIN reason=positive control rc=128: fatal: unable to access 'https://github.com/mpmdw/JouleWise.git/': Could not resolve host: github.com", "WOULD_SPAWN none"]},
      "expected": {"exit_code": 0, "tail_regex": "decision=(?!HOLD_UNSAFE)"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_night_gate tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 145 tests in 8.439s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 145 tests.*OK"}
    }
  ],
  "flags": [
    {"id": "F1", "kind": "residual_risk", "level": "blocking", "text": "Production census construction is incompatible with the integrated Probes contract.", "needs": "Pass a measurement_head callable and add a real-CLI active-v2 regression."},
    {"id": "F2", "kind": "residual_risk", "level": "blocking", "text": "Non-v1 plan failures are ignored instead of held.", "needs": "Ignore only positively identified retired v1; retain fail-closed errors for every other read/parse/validation failure."},
    {"id": "F3", "kind": "residual_risk", "level": "blocking", "text": "The handoff kill inventory can contain unrelated processes.", "needs": "Require auditable magistrate-tree provenance or explicit adjudication for each orphan before it becomes a signal target."},
    {"id": "F4", "kind": "residual_risk", "level": "blocking", "text": "The reaper's executable procedure has a PID-reuse race and an incomplete survivor check.", "needs": "Revalidate PID/start immediately before each signal and prove every recorded PID gone after KILL before accepting census."},
    {"id": "F5", "kind": "residual_risk", "level": "blocking", "text": "The prompt's checkout fence is not derived from the armed v2 plan.", "needs": "Render or state the any-armed-plan measurement_root fence required by the ruling."},
    {"id": "F6", "kind": "verification_gap", "level": "nonblocking", "text": "The dedicated installer test module was read but not executed because the preflight allowlist named only three other modules.", "needs": "Lead may replay tests.test_install_night_agent outside this seat if desired."}
  ]
}
```

## Cure-table audit

| Item | Verdict | Executed/read evidence |
|---|---|---|
| B-1 | **NOT CURED** | The named regression passes (`tests/test_magistrate_watchdog.py:149-186`). In the hand-built mixed root, `load_plans` returned only `valid-v2`, its span was active, and exactly one persisted `plan_retired_v1` event existed. But the real CLI then crashed through `production_census` (`scripts/magistrate_watchdog.py:334-342`) before emitting a decision or `state.json` (F1). Round 4 also changed all other plan failures from `HOLD_UNSAFE` to ignored (F2). |
| M-2 | **NOT CURED** | The helper adds every command-shaped PPID-1 orphan at `scripts/magistrate_watchdog.py:711-722`; executed input with an unrelated session's orphan host/child returned both in `inventory_pids` (F3). The eventual reaper also has the F1/F4 failures. |
| M-3 | **NOT CURED** | Shell-snapshot roots use the same global, provenance-free selection at `scripts/magistrate_watchdog.py:711-720`; the only test (`tests/test_magistrate_watchdog.py:662-689`) supplies no unrelated orphan lookalike. |
| Q4 | **NOT CURED** | The six actions and measurement-checkout install wording are present (`docs/process/MAGISTRATE_WATCHDOG.md:84-179`; `docs/process/NIGHT_HANDBACK.md:73-76`), but the executable handoff cannot complete: its post-kill `production_census()` crashes (F1), and its kill list/reaper violate the stated ownership/survivor rules (F3/F4). |
| Q5 | **NOT CURED** | The prompt is 23 lines and bars rule changes (`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:20`), carries the exit obligation (`:12`), and fences the current literal checkout (`:10`), but it does not fence an arbitrary valid plan's `measurement_root` (F5). |
| Q1 installer checks | **CURED** | `scripts/install_night_agent.sh:51-72` parses through `NightPlan`, uses `PLAN_MAX_AGE_S`, rejects future authorship as `night_plan_malformed`, and rejects age greater than 36 h as `night_plan_stale` before git probes. Defect-shaped tests were read at `tests/test_install_night_agent.py:131-145`; preflight prohibited executing that fourth module. |
| Q2 `SUPERVISOR_POLL_S` pin | **CURED** | Literal `10` at `scripts/magistrate_watchdog.py:68`, used for run-loop cadence at `:1367-1373`; the permitted suite executed the literal and TERM→KILL deadline regressions at `tests/test_magistrate_watchdog.py:356-388`. |

## Findings

Diff attribution: F2, F3, and F4 are newly introduced by `4a23c119..HEAD`. F1 is an integrated-base incompatibility exposed by the mandatory real-CLI case (the watchdog constructor predates the plan-pin field), and F5 is the round-3 cure's surviving literal-path gap; both still block this round's integrated verdict.

### F1 — blocker — production active-plan path crashes

`Probes.measurement_head` became required (`joulewise/night_gate.py:163-169`), but `production_census()` does not provide it (`scripts/magistrate_watchdog.py:334-342`). The hand-built real CLI reached this call for the valid v2 span and raised `TypeError`. The same function is called after the install-handoff reaper has signaled the old tree (`docs/process/MAGISTRATE_WATCHDOG.md:165-172`), so that procedure also cannot produce its required clean receipt.

Counterfactual: one valid active v2 plan. The retired-v1 sibling is not required to trigger the crash.

### F2 — blocker — invalid current plans are treated as retired

The prior `plan_errors` hold remains in `decide` (`scripts/magistrate_watchdog.py:893-895`) but round 4 no longer populates the list: the broad handler at `:535-551` ignores JSON errors, I/O errors, invalid v2 schemas, and every future schema. Executed counterfactual `{"schema":"joulewise.night_plan.v2","plan_id":"armed-v2","t0_epoch_s":0}` produced:

```text
{"decision": "LAUNCHING", "event_kinds": ["plan_unparsable"], "input": "schema-v2 missing required fields", "launch": true}
```

Only a mapping positively identified as schema v1 may take the retired-plan ignore path. Everything else must remain fail closed.

### F3 — blocker — handoff inventory can authorize killing another session

The helper correctly finds the invoking interactive ancestor, but then independently selects every PPID-1 `--bg-pty-host` or shell-snapshot lookalike on the machine (`scripts/magistrate_watchdog.py:701-722`). It has no edge, token, socket, activation, or operator classification tying those roots to that ancestor. Executed counterfactual:

```text
{'classified_magistrate_tree': [100, 110, 800, 900], 'inventory_pids': [100, 110, 700, 701], 'unclassified_listed': [700, 701]}
```

Input PIDs 700/701 were a PPID-1 host and child labeled as another session. This violates the mandatory “never lists a pid it did not classify as magistrate-tree” condition and makes the documented kill step unsafe.

### F4 — blocker — detached reaper's stated invariants are not executable

The reaper snapshots once before the TERM loop (`docs/process/MAGISTRATE_WATCHDOG.md:145-157`), leaving a PID-exit/reuse race before each `os.kill`. After KILL it never snapshots the recorded list again (`:158-172`); an empty agent census can declare success while a recorded non-agent descendant survives. Revalidate PID/start immediately before every signal and require every recorded PID/start pair absent after KILL before census can close the handoff.

### F5 — blocker — prompt fence and plan schema disagree

The 23-line prompt satisfies its size, ordering, process-rule, and canonical-checkout assertions. But schema v2 accepts any absolute `measurement_root` (`joulewise/night_gate.py:238-245`), while the no-move rule names only `/Users/edr/JouleWise-measurement-20260813` (`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:10`). A parsed plan at `/private/tmp/alternate-measurement-checkout` was not fenced by the prompt. The ruling's “any armed plan's `measurement_root`” protection remains absent.

## Mandatory-check evidence

1. Mixed v1/v2 root: unit regression passed. Hand construction plus real CLI persisted exactly one retired-v1 event and parsed/activated only `valid-v2`, then failed F1 before a watchdog decision:

   ```text
   {"active_plan_ids": ["valid-v2"], "ignored_event_count": 1, "ignored_events": [["plan_retired_v1", "retired-v1"]], "parsed_plan_ids": ["valid-v2"], "plan_errors": [], "state_exists_after_cli": false}
   TypeError: Probes.__init__() missing 1 required positional argument: 'measurement_head'
   ```

2. `handoff-inventory` ownership: **FAIL**, counterexample in F3.

3. Relaunch prompt: **23 lines**; canonical checkout fence present, plan-relative checkout fence **FAIL** (F5).

4. v1→`HOLD_UNSAFE`: **PASS**. `load_plans` identifies v1 only as `plan_retired_v1` (`scripts/magistrate_watchdog.py:530-552`); its unit regression passes, and the v1-only real CLI dry-run returned `NETWORK_UNCERTAIN` under the network-denied sandbox, never `HOLD_UNSAFE`, with `WOULD_SPAWN none`.

Permitted three-module suite tail:

```text
.................................................................................................................................................
----------------------------------------------------------------------
Ran 145 tests in 8.439s

OK
```

Named mixed-root regression tail:

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```

## Residual risk

No live launchd install/handoff was attempted, appropriately. The preflight test allowlist excluded `tests.test_install_night_agent`; its Q1 regressions were inspected but not executed. Temporary counterfactual custody stayed under `/private/tmp`; no default custody, launchd state, night, or repository path outside this trace was changed.

Verdict: **RESIDUAL (F1, F2, F3, F4, F5)**
