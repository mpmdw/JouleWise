```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round 5 is RESIDUAL: the required CLI path and handoff/conflict mechanics work, but retired-v1 recognition is label-only, resident plan holds do not drain the live agent, activation-scoped diagnostic dedupe never receives a new activation, and the doc-example test survives a missing required field.",
  "workspace": {
    "base_requested": "8e0042af",
    "base_mode": "descendant",
    "head_start": "aeacba6176f6e4695c4ebfe3070f949b3d945d8e",
    "head_end": "aeacba6176f6e4695c4ebfe3070f949b3d945d8e",
    "upstream_end": "aeacba6176f6e4695c4ebfe3070f949b3d945d8e",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [
    "docs/process_traces/2026-09-03-watchdog-build/15-delta-reaudit-round-5.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "line": "RESIDUAL (F1, F2, F3, F4)",
    "same_signature": "YES — F1 and F2 repeat the unit-green/production-broken signature.",
    "clauses": {
      "R-2": "CURED",
      "R-3": "CURED",
      "R-4": "NOT CURED",
      "R-5": "CURED",
      "R-6": "NOT CURED",
      "R-7": "NOT CURED",
      "AD-1": "CURED",
      "AD-2": "CURED",
      "AD-3": "NOT CURED",
      "AD-4": "CURED",
      "AD-5": "CURED",
      "AD-6": "CURED",
      "AD-7": "CURED",
      "AD-8": "CURED",
      "AD-9": "CURED",
      "AD-10": "CURED",
      "AD-11": "CURED",
      "AD-12": "CURED",
      "AD-13": "NOT CURED"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Retired-v1 recognition trusts one label instead of proving the golden v1 shape",
        "evidence": "scripts/magistrate_watchdog.py:578-587 ignores every mapping whose schema label is joulewise.night_plan.v1; an executed writer-v2 mapping relabeled v1 produced no error and decision=LAUNCHING.",
        "counterfactual": "A torn or wrongly re-authored current-shaped plan retains/receives the v1 label while carrying v2-only fields; it is treated as harmless residue rather than unknown preregistration evidence."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "A resident session never drains after a malformed plan or armed-plan conflict",
        "evidence": "scripts/magistrate_watchdog.py:1522-1538 writes standdown.request and HOLD_UNSAFE but returns to the same branch forever instead of calling _enforce_drain at :1456-1488; after 601 seconds the executed resident remained live with zero signals.",
        "counterfactual": "A plan becomes truncated, malformed, or conflicting after the magistrate is already resident; the agent continues through the protected window despite the durable HOLD_UNSAFE label."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "The AD-3 per-activation event key is permanent because activations are reused",
        "evidence": "scripts/magistrate_watchdog.py:1316-1349 never clears activation_id and :1591 reuses any existing value; the executed clean-exit counterexample retained activation-a and a later identical retired-v1 diagnostic remained at one event.",
        "counterfactual": "The same diagnostic recurs in a genuinely later relaunch and is suppressed as if it belonged to the prior activation."
      },
      {
        "id": "F4",
        "severity": "nit",
        "title": "The AD-13 documentation regression test still does not validate documented plans",
        "evidence": "tests/test_magistrate_watchdog.py:951-964 compiles heredocs and validates a separate test plan; deleting measurement_head from the documented NightPlan constructor left the named test green.",
        "counterfactual": "A documentation edit drops a required NightPlan argument; the example fails when followed but CI remains green."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_night_gate tests.test_run_night tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 163 tests in 14.712s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 163 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "grep -n \"dict\\|{\" tests/test_magistrate_watchdog_cli.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["93:            f\"{self.bin_dir}:/usr/bin:/bin:/usr/sbin:/sbin\""]},
      "expected": {"exit_code": 0, "tail_regex": "^93:.*bin_dir.*$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "in an archived temp checkout, delete scripts/run_night.py:290 measurement_head=measurement_head; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog_cli; restore with apply_patch and rerun",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["TypeError: Probes.__init__() missing 1 required positional argument: 'measurement_head'", "Ran 1 test in 0.713s", "FAILED (failures=1)", "restored: Ran 1 test in 0.703s", "restored: OK"]},
      "expected": {"exit_code": 1, "tail_regex": "TypeError: Probes.__init__.*measurement_head.*FAILED \\(failures=1\\)"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/magistrate_watchdog.py tick --custody-root /private/tmp/joulewise-watchdog-hand.el1IH9/magistrate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["state=HOLD_UNSAFE", "event_kinds=plan_malformed,plan_retired_v1,plan_unreadable,transition", "retired_v1_count=1", "attempts_exists=false"]},
      "expected": {"exit_code": 0, "tail_regex": "state=HOLD_UNSAFE.*retired_v1_count=1.*attempts_exists=false"}
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY' # executed classifier, handoff, conflict/prompt, resident-drain, and activation-dedupe counterfactuals shown below\nPY",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["mislabeled_current_shape_decision=LAUNCHING launch=true", "resident_malformed state=HOLD_UNSAFE child_live=true signals=[]", "activation_after_clean_exit=activation-a retired_events_after_next_tick=1", "handoff owned=[100,110] unclassified_candidates=[700,701]", "overlap=HOLD_UNSAFE nonoverlap=LAUNCHING prompt_lines=23"]},
      "expected": {"exit_code": 0, "tail_regex": "mislabeled_current_shape_decision=HOLD_UNSAFE.*child_live=false.*retired_events_after_next_tick=2"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "in the archived temp checkout, delete docs/process/MAGISTRATE_WATCHDOG.md:245 measurement_head; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog.ContractTests.test_documented_example_plans_use_the_production_writer",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.003s", "OK"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "parse the leading JSON envelope; assert schema/genre/pathspec, one JSON fence, <=8192 UTF-8 bytes, final newline, no trailing whitespace; git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["REPORT_OK envelope_bytes=7952 lines=254"]},
      "expected": {"exit_code": 0, "tail_regex": "REPORT_OK envelope_bytes=[0-9]+ lines=[0-9]+"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No live install, launchd mutation, process signal, agent start, or quiet-machine measurement was performed.",
      "needs": "The lead and cold gate retain the live handoff and hardware gates."
    }
  ]
}
```

## Findings

### F1 — blocker — retired-v1 classification is label-only

The golden fixture is byte-stable at SHA-256 `d5c484c4afd95cf9fffcd33222da2b4b0737cb8a9c608c8c446ac00ae955cc3f`. Its exact keys are `schema`, `plan_id`, `receipt_class`, `t0_epoch_s`, `window_max_s`, `authored_epoch_s`, `repo_head`, `chain_path`, `chain_sha256_path`, `custody_root`, and `registration_path`; it has **no `schema_version`**, `measurement_root`, or `measurement_head`. Yet the recognizer at `scripts/magistrate_watchdog.py:578-587` tests only `raw.get("schema") == "joulewise.night_plan.v1"`, not that golden shape.

The repository's night-plan discriminator is named `schema`, not `schema_version` (`joulewise/night_gate.py:198-217`). Deleting that actual discriminator from writer-produced v2 bytes correctly produced `night_plan_malformed`. The mandatory shape check nevertheless failed: changing only the same writer-produced v2 mapping's `schema` value to the v1 label, while retaining both v2-only measurement fields, yielded:

```text
mislabeled_current_shape_errors=[]
mislabeled_current_shape_diagnostics=[]
mislabeled_current_shape_decision=LAUNCHING
mislabeled_current_shape_launch=true
```

Counterfactual: a current/torn producer emits a current-shaped mapping with a stale v1 label. A positive retired-v1 identification must require the frozen legacy shape (and label), not the label alone.

### F2 — blocker — resident unsafe-plan holds do not enforce stand-down

The short tick correctly holds malformed input at `scripts/magistrate_watchdog.py:1068-1076`. The resident path at `:1512-1538`, however, writes `standdown.request`, transitions to `HOLD_UNSAFE`, and returns `True`. Every later step takes that same branch. It never calls the monotonic TERM/KILL ladder at `:1456-1488`.

Executed counterfactual: start the fake resident with its exact PID/start-owned process, replace its valid writer plan with truncated JSON, step once, advance wall and monotonic clocks by `STOP_COOPERATIVE_S + STOP_TERM_GRACE_S + 1`, and step again:

```text
first_continues=true
second_continues_after_drain_deadline=true
state=HOLD_UNSAFE request_exists=true child_live=true signals=[]
```

The same branch handles `plan_conflict`, so a conflict armed after launch also leaves the old prompt/session alive. This is a production control-flow defect, not a label-only state discrepancy.

### F3 — should_fix — AD-3's activation component never changes

The event key itself is correctly `(activation_id, plan_dir, kind, digest)` at `scripts/magistrate_watchdog.py:489-549`. But `_finish_child` at `:1316-1349` does not clear `state["activation_id"]`, and `start_session` at `:1591-1593` explicitly reuses a retained value. After an executed clean exit, the value remained `activation-a`; recording the same retired-v1 diagnostic on the next tick left the count at one. Thus later activations do not independently report as AD-3 required.

### F4 — nit — AD-13's replacement test is still nondiscriminating

`tests/test_magistrate_watchdog.py:951-964` compiles each documentation heredoc but does not execute or semantically validate its `NightPlan` constructor; it validates a separate test-owned plan afterward. In an archived temporary checkout I deleted the required `measurement_head` argument from the first documented constructor. The exact named test still reported `Ran 1 test ... OK`. A static AST assertion or a side-effect-isolated execution/semantic extraction must connect the examples themselves to `write_night_plan`/`NightPlan`.

### Clause audit

| Clause | Verdict | Executed/read evidence |
|---|---|---|
| R-2 | **CURED** | `tests/test_magistrate_watchdog_cli.py:122-191` calls `sys.executable` + the real script and never mocks subprocess/main. `grep -n "dict\|{" tests/test_magistrate_watchdog_cli.py` returned only line 93's PATH f-string. The five-module suite passed; the hand-built non-dry-run four-sibling tick is recorded below. |
| R-3 | **CURED** | `joulewise/night_plan_writer.py:15-62` owns mapping/atomic publication; tests construct `NightPlan` then call it (`tests/test_magistrate_watchdog_cli.py:99-120`). The only production `Probes(` is `scripts/run_night.py:284-291`; census consumes the narrow protocol at `joulewise/night_gate.py:172-176,399-425`. The required constructor mutation failed the real CLI test. |
| R-4 | **NOT CURED** | Unreadable/malformed/future plans populate the hold at `scripts/magistrate_watchdog.py:552-602,1068-1073`, and the old fail-open test was replaced at `tests/test_magistrate_watchdog.py:208-287`. F1 defeats positive v1 identification; F2 defeats fail-closed behavior for an existing resident. |
| R-5 | **CURED** | Inventory classification/adoption is at `scripts/magistrate_watchdog.py:775-898`; the fake unrelated PIDs 700/701 executed as `unclassified_candidates` and never `owned`. The reaper at `docs/process/MAGISTRATE_WATCHDOG.md:119-207` reads only `owned`, pair-checks before each signal, records absent/reuse, puts root last, waits `STOP_COOPERATIVE_S`, snapshots after TERM/KILL, and fails on survivors independently of census. |
| R-6 | **NOT CURED** | Pure/short-tick mechanics pass: `scripts/magistrate_watchdog.py:642-710,1068-1076,1153-1168`; the hand check gave overlapping=`HOLD_UNSAFE`, nonoverlapping=`LAUNCHING`, and a 23-line prompt containing both armed roots. F2 means a conflict discovered by a running resident does not actually stand the session down. |
| R-7 | **NOT CURED** | The five-module suite passed, but AD-3 and AD-13 remain (F3/F4), in addition to the two ruling-level blockers. |
| AD-1 | **CURED** | `scripts/magistrate_watchdog.py:335-342` calls `make_probes`; `scripts/run_night.py:267-291` is the single production constructor; `joulewise/night_gate.py:172-176,425` narrows census. Mutation V3 proves the real CLI crosses it. |
| AD-2 | **CURED** | `scripts/magistrate_watchdog.py:552-602` has live unreadable/malformed producers for `PlanSnapshot.errors`; manual R-2 tick consumed both at `:1072-1073`. |
| AD-3 | **NOT CURED** | Key implementation is `scripts/magistrate_watchdog.py:489-549`; executed clean-exit/later-tick counterexample proves activation reuse at `:1316-1349,1591`. F3. |
| AD-4 | **CURED** | Event payload uses `plan_dir` and distinct `plan_path` at `scripts/magistrate_watchdog.py:530-546`; manual events named the discovered sibling directories. |
| AD-5 | **CURED** | `load_plans` is read-only at `scripts/magistrate_watchdog.py:552-602`; persistence occurs at tick/supervisor boundaries (`:1512-1517,1735-1744`). `tests/test_magistrate_watchdog.py:236-278` proves dry-run storage does not remember suppression; suite passed. |
| AD-6 | **CURED** | The watchdog-superset relation is documented at `docs/process/MAGISTRATE_WATCHDOG.md:7`; the old-but-valid gate plan remains `FENCED` in `tests/test_magistrate_watchdog.py:343-351`, executed in V1. |
| AD-7 | **CURED** | `scripts/magistrate_watchdog.py:775-783` and `scripts/install_magistrate_watchdog.sh:84-89` reject `-p`/`--print`; `tests/test_magistrate_watchdog.py:864-870` executed green. |
| AD-8 | **CURED** | Detached reaper `signal_matching` distinguishes `already_gone` from `reused_skipped` at `docs/process/MAGISTRATE_WATCHDOG.md:155-168`; heredoc compilation executed in V1. |
| AD-9 | **CURED** | Reaper imports and sleeps `STOP_COOPERATIVE_S` at `docs/process/MAGISTRATE_WATCHDOG.md:132-175`; production constant is nine minutes at `scripts/magistrate_watchdog.py:72`. |
| AD-10 | **CURED** | `watchdog_checkout` is captured and resolved, inserted into `sys.path`, then used for import at `docs/process/MAGISTRATE_WATCHDOG.md:122-136`. |
| AD-11 | **CURED** | Both overlap/different-root and same-root/different-head checks are implemented at `scripts/magistrate_watchdog.py:668-697`; executed overlap/nonoverlap hand check and suite tests at `tests/test_magistrate_watchdog.py:289-341` passed. |
| AD-12 | **CURED** | Corrupt-plan assertions now demand HOLD at `tests/test_magistrate_watchdog.py:208-234` and `tests/test_magistrate_watchdog_cli.py:157-180`; manual non-dry-run tick confirmed no attempts. |
| AD-13 | **NOT CURED** | `tests/test_magistrate_watchdog.py:951-964` no longer counts strings, but the required-field documentation mutation survived. F4. |

### Mandatory executed evidence

The required constructor mutation was performed in `/private/tmp/joulewise-watchdog-mutation.NW1ZVV`, an archive of `HEAD` initialized as its own temporary Git repository. After deleting only `scripts/run_night.py:290`, the failure tail was:

```text
  File "/private/tmp/joulewise-watchdog-mutation.NW1ZVV/scripts/run_night.py", line 284, in make_probes
    return Probes(
TypeError: Probes.__init__() missing 1 required positional argument: 'measurement_head'

----------------------------------------------------------------------
Ran 1 test in 0.713s

FAILED (failures=1)
```

The line was restored with `apply_patch`; the same module then ran one test in 0.703 s and passed. The audited repository remained clean.

The manual R-2 build used `/private/tmp/joulewise-watchdog-hand.el1IH9`: a real initialized Git measurement checkout, writer-authored active v2, byte-copied golden v1, 40%-truncated writer bytes, and writer bytes minus `measurement_head`. The real command, without `--dry-run`, exited 0 with empty stdout/stderr. Parsed result:

```text
{
  "state": "HOLD_UNSAFE",
  "launch": false,
  "attempts_exists": false,
  "event_kinds": ["plan_malformed", "plan_retired_v1", "plan_unreadable", "transition"],
  "retired_v1_count": 1,
  "reason_names": ["missing-field/night_plan.json", "torn/night_plan.json"]
}
```

The handoff fake table and conflict/prompt checks were independent one-off calls, not restatements of unit assertions:

```text
handoff owned=[100,110]
handoff unclassified_candidates=[700,701]
overlap state=HOLD_UNSAFE reason=plan_conflict: overlapping spans use different measurement roots
nonoverlap state=LAUNCHING plan_conflict=false
prompt_lines=23; rendered triples=canonical repo + left armed root + right-later armed root
```

Same-signature statement: **YES.** F1 and F2 again leave all permitted unit/CLI tests green while a production-relevant classification/control-flow path fails the safety contract. The new CLI boundary cures the former missing-`Probes` composition, but it does not cover a falsely v1-labelled current shape or an already-running resident's response to later plan failure.

Verdict: **RESIDUAL (F1, F2, F3, F4)**

## Residual risk

The detached reaper remains executable documentation rather than a separately installed program. Its destructive signaling path, live install/launchd state, and first real handoff were intentionally not executed. No `[QUIET-MAC]` measurement was started or continued. Temporary counterfactuals stayed under `/private/tmp`; the only repository write is this trace.
