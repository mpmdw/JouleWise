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
