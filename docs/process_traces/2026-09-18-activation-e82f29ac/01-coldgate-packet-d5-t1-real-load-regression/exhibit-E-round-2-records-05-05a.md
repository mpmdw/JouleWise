# Exhibit E — delta re-audit round 2 (activation 8bd030d2, record 05, Astra high) finding and the lead's adjudication (record 05a)

## Record 05 findings block (verbatim)
```json
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
```

## Record 05 prose (verbatim, after the envelope)


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

## Record 05a (verbatim)

# Record 05a — adjudication of delta re-audit round 2 (D5-T1 stays OPEN), and close-out (lead, 2026-09-18 22:55–23:1x PDT)

## Seat 05 outcome

Record 05 (Astra high, read-only, detached worktree at `498ad1d0`, 4 min, status OK / findings / complete): blocker 0, should_fix 1, nit 0. E3: all three mutations (`cores`, `alignment`, `observer`) still killed against HEAD (1/2/1 failures). E4: `wake_late_s` is unconditional and numeric on every real-load period row (`scripts/sample_quiet_predicate_evidence.py:820`), no finding. E5: module 5.44 s / 5.46 s, changed test 3.79 s both runs. E6: **same-signature: FOUND** — "real-load assertion fails on correct code under scheduler starvation".

**D5-T1 NOT FIXED.** The bench fix `498ad1d0` closes only the witness the round-1 auditor happened to use (each sleep 1.05 s late → `late_s` = 2.1 → bound −0.01 → passes). Two further correct-code inputs still fail the tight ±0.04 check (`tests/test_sample_quiet_predicate_evidence.py:627`):

| Scheduling input (correct code) | Achieved cores | Summed `wake_late_s` | Result |
|---|---:|---:|---|
| worker first scheduled 2 s after `start` (the initial sleep at `:869` is outside `duty_periods`, never recorded) | 0.0333 | 0 | FAIL |
| during burning, wall time advances 100× thread CPU time (preemption exhausts the wall deadline at `:800`) | 0.0100 | 0.025 | FAIL |

The root cause is structural: the fix keyed the relaxation to `wake_late_s`, but that field measures only sleep-wake lateness inside `duty_periods`; starvation before the first period and preemption during a burn leave no trace in it. The no-catch-up rule (`:775-778`) discards unmet budgets and guarantees nothing about delivery, so any delivery *minimum* on a real-scheduler test is a heuristic. Corroborating datum: on this idle machine both instrumented runs recorded `late_s` ≈ 0.82–0.90 s, so the starvation branch fired every time and the "tight two-sided check" is dead code in practice.

E2 (did the fix weaken the guard): an on-time half-budget defect still fails (fraction 0.050, `late_s` 0); with ≥ 1.8 s of summed lateness the lower bound turns non-positive and such a defect could hide — acceptable residual because `test_cpu_budget_overshoot_and_frozen_duty` (`:643`) independently pins 1.8 CPU-s within 0.01 on the fake clock and kills that mutation. The over-burn ceiling (≤ 0.14 cores) is the only assertion in the real-load test that is both sound and load-bearing.

## Adjudication

1. D5-T1 remains a **should_fix, OPEN** against `feat/2026-09-18-quiet-predicate-evidence-harness` at `498ad1d0`. The branch is not PR-ready until it is closed.
2. Under rule 11 any second fix round on the same defect is a mandatory cold-gate trigger, and this is a design question (what a real-scheduler regression may legitimately assert), so this activation authors **no round 2**. The next spend on D5-T1 is a **consult**, not another bench edit.
3. Candidate resolutions for the consult packet (lead's view, not a ruling): (a) drop the delivery minimum from the real-load test entirely — keep the over-burn ceiling, the pre-launch share guard, the reaping/cleanup assertions and the fake-clock budget tests as the budgeting oracle; or (b) make the harness emit per-period starvation evidence that covers the initial sleep and in-burn preemption (e.g. record `start` lateness and per-period wall-vs-CPU ratio), and assert the deficit against that. (a) is smaller and leaves the mutation kills intact (E3 shows `cores` dies at the pre-launch guard, not at the delivery check); (b) is the stronger instrument but is harness scope, not test scope.
4. No repository code changed in this activation. Seat worktree `JouleWise-wt-ref-delta2-8bd030d2` removed after the seat exited; no `codex exec` alive at close-out.

## Executed evidence (this session)

- Seat launch 22:48:40 PDT, `codex-run exit: OK`, rc=0 at 22:52; manifest and status filed alongside.
- `pgrep -fl "codex exec"` after the seat: none.
- Canonical root `/Users/edr/code/JouleWise` untouched (`422cdebb`), measurement root untouched at `d595aa9f`; both night agents and the magistrate agent loaded throughout.

## Successor's next exact actions (unchanged order, one item amended)

After 02:35 PDT + `night/courier.sent`: harvest per runbook §2.0–§2.5, uninstall both night agents, `epoch_equivalence_check`. Then lane 232 harness: **convene the D5-T1 consult** (cold Fable seat + Opus contract refuter per rule 11; packet = records 04, 04a, 05, 05a), apply the ruling as fix round 2 with a defect-shaped regression for BOTH surviving counterexamples, delta re-audit it, then the PR gate (sharded replay, hosted CI on the branch head, twelve-row ledger, terminal review, merge under D-072).
