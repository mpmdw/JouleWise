```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "D5-T1's original late-wake example passes, but its starvation-failure signature survives. Both module runs pass; all three mutations are killed.",
  "workspace": {
    "base_requested": "05e90616",
    "base_mode": "descendant",
    "head_start": "498ad1d0c0f9ad0293adce6649eb71af6cd8958e",
    "head_end": "498ad1d0c0f9ad0293adce6649eb71af6cd8958e",
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
        "title": "Real-load assertion still fails on correct code under scheduler starvation",
        "disposition": "NOT FIXED",
        "call_site": "tests/test_sample_quiet_predicate_evidence.py:625-631",
        "counterfactual_input": "Unmodified duty_periods(.1, 3, .5, burn, clock, start=0), with the worker first scheduled at monotonic time 2.0; alternatively, burn advances wall time 100 times faster than thread CPU time.",
        "observed": "Late initial scheduling yields fraction=0.03333333333333437 and late_s=0; burn preemption yields fraction=0.010033333333333288 and late_s=0.02499999999997371. Both fail the actual test's tight assertion despite correct budgeting.",
        "recommendation": "Retain deterministic budgeting and pre-launch configuration checks; make the real scheduling assertion account for initial and in-period starvation, or avoid imposing a delivery minimum that the scheduler cannot guarantee."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/delta2-run.py module1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 41 tests in 5.437s", "OK", "WALL module1 5.887117s EXIT 0"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/delta2-run.py module2",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 41 tests in 5.459s", "OK", "WALL module2 5.904835s EXIT 0"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/delta2-run.py cores",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 41 tests in 1.525s", "FAILED (failures=1)", "MUTATION cores run 41 failures 1 errors 0"]
      },
      "expected": {"exit_code": 1, "tail_regex": "MUTATION cores run 41 failures 1 errors 0"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/delta2-run.py alignment",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 41 tests in 5.338s", "FAILED (failures=2)", "MUTATION alignment run 41 failures 2 errors 0"]
      },
      "expected": {"exit_code": 1, "tail_regex": "MUTATION alignment run 41 failures 2 errors 0"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/delta2-run.py observer",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 41 tests in 5.411s", "FAILED (failures=1)", "MUTATION observer run 41 failures 1 errors 0"]
      },
      "expected": {"exit_code": 1, "tail_regex": "MUTATION observer run 41 failures 1 errors 0"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/delta2-fixtures.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ACTUAL_ASSERTION late_wakes PASS",
          "ACTUAL_ASSERTION burn_preempted FAIL 0.010033333333333288 != 0.1 within 0.04 delta (0.08996666666666672 difference)",
          "ACTUAL_ASSERTION initial_wake_late FAIL 0.03333333333333437 != 0.1 within 0.04 delta (0.06666666666666564 difference)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "ACTUAL_ASSERTION initial_wake_late FAIL"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git diff --check 05e90616 HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "498ad1d0c0f9ad0293adce6649eb71af6cd8958e"]
      },
      "expected": {"exit_code": 0, "tail_regex": "498ad1d0c0f9ad0293adce6649eb71af6cd8958e"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The supplied mutations.py exists, but its sibling cores.py, alignment.py and observer.py are absent. The scratch adapter executes that runner unchanged while supplying HEAD source with the original substitutions recovered from /tmp/delta-507514d5-check.py; every substitution matched exactly once.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Module timing uses a /tmp sitecustomize hook to print the changed test's locals and elapsed time. Both children execute python3 -B -m unittest tests.test_sample_quiet_predicate_evidence. The supervisor imposes a 50-second process-group timeout; every run completed normally within six seconds.",
      "needs": ""
    }
  ]
}
```

## Findings

**D5-T1 — should_fix; NOT FIXED overall.** The original witness is fixed, but the same failure signature survives.

**E1 — Original counterfactual.** Unmodified `duty_periods` with each sleep waking 1.05 seconds late produces two rows:

```text
fraction = 0.03333333333333437
late_s   = 2.0999999999999996
bound    = .1 - .04 - .1 * 2.1 / 3 = -.01
```

The upper check passes, the starvation branch fires, and `0.033333 ≥ −0.01` passes. V6 also passes these rows through the actual regression test.

However, this is a **heuristic allowance, not a general bound derived from the no-catch-up rule**. Production explicitly discards unsatisfied CPU budgets at `scripts/sample_quiet_predicate_evidence.py:775-778`. That rule does not guarantee CPU availability during a period.

Two correct-code counterexamples fail the actual assertion at `tests/test_sample_quiet_predicate_evidence.py:627`:

| Scheduling input | Achieved cores | Summed lateness | Result |
|---|---:|---:|---|
| Initial worker wake at `start + 2 s` | 0.033333 | 0 | Fails |
| During burning, wall time advances 100× thread CPU time | 0.010033 | 0.025 s | Fails |

The initial sleep occurs outside `duty_periods`, at `scripts/sample_quiet_predicate_evidence.py:869`; its lateness is not included in any row. In-period preemption can exhaust the wall deadline at `:800` while leaving only small lateness at the subsequent sleep. The new predicate therefore does not capture all scheduler starvation.

**E2 — Under-burning guard.** A scratch mutation changing `budget = share * elapsed` to half that budget at `scripts/sample_quiet_predicate_evidence.py:796` produced:

```text
half_budget_on_time: fraction=0.050006667 late_s=0.0 accepted=false
half_budget_late:    fraction=0.016673333 late_s=2.1 accepted=true
```

Thus on-time half-budget burning still fails. With sufficient lateness, under-burning can hide behind the relaxed bound; above 1.8 seconds of summed lateness, the lower bound is nonpositive.

For this generic half-budget defect, that relaxation is an acceptable residual of the scheduling check because `test_cpu_budget_overshoot_and_frozen_duty`, at `tests/test_sample_quiet_predicate_evidence.py:643`, independently requires 1.8 CPU-seconds within `.01`. The mutation delivers `0.900070000000117` and fails that assertion. It does not resolve D5-T1’s false failures.

**E3 — Mutations against HEAD.** All three original substitutions matched HEAD exactly once; no replacement substitution was necessary. The missing companion modules required the in-memory adapter described in F1.

```text
Ran 41 tests in 1.525s
FAILED (failures=1)
MUTATION cores run 41 failures 1 errors 0

Ran 41 tests in 5.338s
FAILED (failures=2)
MUTATION alignment run 41 failures 2 errors 0

Ran 41 tests in 5.411s
FAILED (failures=1)
MUTATION observer run 41 failures 1 errors 0
```

The cores mutation fails the pre-launch share guard (`:609`), so it never launches a one-core load. Alignment fails assertions at `:118` and `:206`; observer accounting fails at `:388`.

**E4 — Field and formatting safety.** Every emitted period row unconditionally receives numeric `wake_late_s = max(0.0, clock.monotonic() - boundary)` at `scripts/sample_quiet_predicate_evidence.py:820`. Workers return these rows directly at `:870-873`. On this real-load path the field cannot be missing or `None`; an empty list also sums safely. Both message operands are numeric, so `.4f` and `.3f` formatting is safe. No finding here.

**E5 — Timing.** Both runs executed the requested unittest module, with scratch instrumentation:

| Run | Module time | Process wall time | Changed test | `late_s` | Branch |
|---|---:|---:|---:|---:|---|
| 1 | 5.437 s | 5.887 s | 3.789 s | 0.900572206 | Starvation |
| 2 | 5.459 s | 5.905 s | 3.787 s | 0.820701539 | Starvation |

The changed test remained below five seconds; the complete module did not. The branch was the same in both runs.

**E6 — same-signature: real-load assertion fails on correct code under scheduler starvation.**

Repository state remained clean at `498ad1d0`. Only `/tmp` scratch was written. Next step: lead adjudicates the surviving D5-T1 counterexamples before closing the finding.

## Residual risk

The deterministic budget test covers the generic half-budget mutation, but does not prove absence of defects conditional on native execution or the specific `.1` setting. No power collection, canonical discovery suite, or hardware validation was performed.