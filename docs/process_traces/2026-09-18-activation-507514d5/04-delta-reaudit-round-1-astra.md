```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Original findings are fixed within the authorized 0.1-core scope; all three mutations are killed. One new should-fix: the load regression can fail under valid scheduler delays.",
  "workspace": {
    "base_requested": "d066d271",
    "base_mode": "descendant",
    "head_start": "05e90616bad6e22a220d5520170d0a3fb7dc0c4e",
    "head_end": "05e90616bad6e22a220d5520170d0a3fb7dc0c4e",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 1, "nit": 0},
    "findings": [
      {
        "id": "D5-T1",
        "severity": "should_fix",
        "title": "Real-load regression confuses scheduler starvation with incorrect core budgeting",
        "call_site": "tests/test_sample_quiet_predicate_evidence.py:622",
        "counterfactual_input": "Correct duty_periods(.1, 3, .5, burn, clock), with each sleep waking 1.05 seconds late.",
        "observed": "The deterministic scheduling fixture produces 0.03333333333333437 cores, below the test's 0.06-core minimum, despite correct configuration and intentional no-catch-up behavior.",
        "recommendation": "Keep deterministic budget and CLI-to-worker assertions; distinguish scheduler shortfall from implementation failure in the real scheduling check."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_sample_quiet_predicate_evidence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 41 tests in 5.561s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -c \"exec(compile(open('/tmp/delta-507514d5-check.py').read(), '/tmp/delta-507514d5-check.py', 'exec'), {'__name__': 'audit_driver'})\" alignment",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 41 tests in 5.357s", "FAILED (failures=2)", "MUTATION alignment run 41 failures 2 errors 0"]
      },
      "expected": {"exit_code": 1, "tail_regex": "MUTATION alignment run 41 failures 2 errors 0"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -c \"exec(compile(open('/tmp/delta-507514d5-check.py').read(), '/tmp/delta-507514d5-check.py', 'exec'), {'__name__': 'audit_driver'})\" observer",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 41 tests in 5.466s", "FAILED (failures=1)", "MUTATION observer run 41 failures 1 errors 0"]
      },
      "expected": {"exit_code": 1, "tail_regex": "MUTATION observer run 41 failures 1 errors 0"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -c \"exec(compile(open('/tmp/delta-507514d5-check.py').read(), '/tmp/delta-507514d5-check.py', 'exec'), {'__name__': 'audit_driver'})\" cores",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 41 tests in 1.764s", "FAILED (failures=1)", "MUTATION cores run 41 failures 1 errors 0"]
      },
      "expected": {"exit_code": 1, "tail_regex": "MUTATION cores run 41 failures 1 errors 0"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/delta-507514d5-check.py fixture",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ROW_KEYS_REMOVED []",
          "SHARED_TYPES_CHANGED []",
          "SHARED_VALUES_CHANGED []",
          "SCHEDULING_COUNTEREXAMPLE {\"wake_delay_s\": 1.05, \"window_s\": 3, \"period_s\": 0.5, \"fraction\": 0.03333333333333437, \"passes_new_test\": false}",
          "REMOVED_ASSERT_LINES []"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "REMOVED_ASSERT_LINES \\[\\]"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git diff --check d066d271 HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "05e90616bad6e22a220d5520170d0a3fb7dc0c4e"]
      },
      "expected": {"exit_code": 0, "tail_regex": "05e90616bad6e22a220d5520170d0a3fb7dc0c4e"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Supplied mutation modules contain the old 1071-line source, rather than the 1152-line current head. V2-V4 execute the supplied mutations.py unchanged, using an in-memory loader applying its exact original substitutions to HEAD. An initial file-based wrapper caused multiprocessing spawn artifacts; the corrected -c replay has only intended failures.",
      "needs": ""
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "R3's original mutation and missing end-to-end coverage are addressed at 0.1 cores. The fix brief's additional 0.2-core case remains absent and was not run under the explicit 0.1-core cap.",
      "needs": "Lead retains disposition of the previously requested 0.2-core exception."
    }
  ]
}
```

## Findings

**D5-T1 — should_fix: the new load test can flake under scheduler contention.**

The assertion at [tests/test_sample_quiet_predicate_evidence.py:622](/Users/edr/code/JouleWise-wt-ref-delta-507514d5/tests/test_sample_quiet_predicate_evidence.py:622) requires **0.1 ± 0.04 cores over three seconds**, using 500-ms periods. That allows ±0.12 CPU-seconds.

Production explicitly discards unmet budgets under contention and never catches up ([scripts/sample_quiet_predicate_evidence.py:770](/Users/edr/code/JouleWise-wt-ref-delta-507514d5/scripts/sample_quiet_predicate_evidence.py:770)). V5 injects 1.05-second wake delays with a fake clock: correct budgeting produces **0.033333 cores**, failing the test’s minimum. This establishes a possible false failure without stressing the machine; no spontaneous flake occurred during this audit.

Keep the deterministic budget/configuration checks, and distinguish scheduling shortfall from incorrect budgeting in the real-load assertion.

**D1 — original finding dispositions**

Test names below are in `tests/test_sample_quiet_predicate_evidence.py`.

| Finding | Disposition | Guard and evidence |
|---|---|---|
| R1 | FIXED | `test_absolute_anchor_endpoints_reject_known_arrival_offset` (:106) and strengthened `test_real_production_rate_anchor_and_clock_step_refusal` (:185); alignment mutation fails both. |
| R2 | FIXED | `test_observer_cost_includes_known_reaped_child_delta` (:376); asserts 0.9 CPU-seconds, mutation yields 0.2. |
| R3 | FIXED within 0.1-core scope | `test_real_load_tracks_point_one_core_and_guards_worker_budget` (:601); mutation rejected before worker launch. Additional 0.2-core case remains deferred; new timing defect is D5-T1. |
| R4 | FIXED | `test_real_collect_no_power_reaps_all_recorded_workers` (:326); real subprocess, persisted rows, missing-power reasons, reaping and PID absence. |
| R5 | FIXED | `test_empty_directory_cli_writes_reasoned_null_summary` (:696). |
| R6 | FIXED | `test_summary_preserves_exact_session_provenance` (:707). |
| R7 | FIXED | `test_smoke_temporary_journal_writes_stay_under_output` (:304), plus filesystem audit in the real collection test. |
| F1 | FIXED | `test_partial_round_retains_concurrent_census_and_marks_contamination` (:268), `test_round_without_completed_census_is_reasoned_unknown` (:291), and `test_summary_never_pools_census_conditions_or_reference` (:672). |
| F2 | FIXED | `test_summary_preserves_exact_session_provenance` (:707) checks returned and persisted PROVISIONAL status, alignment model and network-time provenance against session metadata. |

Final mutation tails, executing the supplied runner against HEAD:

```text
Ran 41 tests in 5.357s
FAILED (failures=2)
MUTATION alignment run 41 failures 2 errors 0

Ran 41 tests in 5.466s
FAILED (failures=1)
MUTATION observer run 41 failures 1 errors 0

Ran 41 tests in 1.764s
FAILED (failures=1)
MUTATION cores run 41 failures 1 errors 0
```

**D2 — assertion preservation**

Inspected `git diff d066d271 HEAD -- tests/`. Removed `assert*` lines: **none**. No existing assertion was weakened or made conditional. The macOS-only decorator applies to the newly added native-QoS load test.

**D3 — schema comparison**

The schema remains `joulewise.quiet_predicate_evidence.v1`. Comparing equivalent before/after round objects produced:

```text
ROW_KEYS_ADDED ['census_clean', 'census_clean_reason', 'census_errors', 'censuses', 'censuses_reason']
ROW_KEYS_REMOVED []
SHARED_TYPES_CHANGED []
SHARED_VALUES_CHANGED []
```

No existing row field was renamed or retyped. The changes are additive ([scripts/sample_quiet_predicate_evidence.py:576](/Users/edr/code/JouleWise-wt-ref-delta-507514d5/scripts/sample_quiet_predicate_evidence.py:576)). Summary grouping deliberately changes to include census condition; a mixed-condition reference becomes null with separate `references_by_census`, as required by F1.

**D4 — missing census and mixed directory**

V5 constructs [the two-row fixture](/tmp/delta-507514d5-two-rows/rounds.jsonl) through `new_row`: one clean row at 1 W and one census-unknown row at 100 W. Output:

```text
NO_CENSUS {"census_clean": null, "census_clean_reason": "no census completed during round"}
TWO_ROWS {"reference": null, "references_by_census": [{"census_clean": null, "complete_rounds": 1, "cpu_w": 100.0}, {"census_clean": true, "complete_rounds": 1, "cpu_w": 1.0}], "groups": [{"census_clean": null, "complete_rounds": 1, "cpu_w": 100.0}, {"census_clean": true, "complete_rounds": 1, "cpu_w": 1.0}]}
```

No census is unknown, never clean. Clean and unknown rows remain separate in both groups and references ([scripts/sample_quiet_predicate_evidence.py:995](/Users/edr/code/JouleWise-wt-ref-delta-507514d5/scripts/sample_quiet_predicate_evidence.py:995)).

**D4b — census exit-code semantics**

The codes match production; **no blocker found**:

- The sampler preserves the subprocess return code directly at [quiet_admission.py:268](/Users/edr/code/JouleWise-wt-ref-delta-507514d5/joulewise/quiet_admission.py:268).
- Its validator requires exit 0 with nonempty output or exit 1 without non-whitespace output at [quiet_admission.py:188](/Users/edr/code/JouleWise-wt-ref-delta-507514d5/joulewise/quiet_admission.py:188).
- Concurrent census results preserve the probe code through `_bind_worker_result` and `_census_record` at `scripts/run_night.py:2023` and `:394`; `_binding_census` rejects malformed combinations at `:2298`.
- Production explicitly treats sampler exit 0 as an agent hit at [run_night.py:2515](/Users/edr/code/JouleWise-wt-ref-delta-507514d5/scripts/run_night.py:2515).

V5 confirms: `0 + hit → false`, `1 + empty → true`, and `0 + empty`, `1 + hit`, or `2 + empty → null`.

**D5 — timing**

The requested module passed **41 tests in 5.561 seconds**; measured process wall time was **6.059 seconds**. A second run with per-test instrumentation passed in 5.500 seconds:

```text
test_real_collect_no_power_reaps_all_recorded_workers 1.571 s
test_real_load_tracks_point_one_core_and_guards_worker_budget 3.777 s
```

No individual test exceeded five seconds in that run. The module as a whole does. Scheduling sensitivity is D5-T1.

**D6 — same-signature: none found**

## Residual risk

The 0.2-core case remains unimplemented under the explicit cap. No power capture, canonical discovery suite, or hardware validation was performed.

Repository state remained clean at `05e90616`; only `/tmp` audit scripts, fixtures and logs were written. Next step: lead adjudicates D5-T1 and the deferred 0.2-core coverage.