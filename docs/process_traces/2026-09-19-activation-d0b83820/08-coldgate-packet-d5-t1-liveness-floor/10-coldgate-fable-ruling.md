# Cold-gate ruling 10 (packet 08) — D5-T1 liveness floor: DELETE it; burn-noop killed by a deterministic burn_profile test; F3 affirmed

Judge: cold Fable 5.1 seat, worktree `JouleWise-wt-coldgate-d0b83820`, 2026-09-19 08:01:29 → 08:0x PDT (validator start to file write). Single foreground session, no subagents, no background work.

## Validator and contamination disclosure

- Typo digest (`…a880…`): `"result":"REFUSE","reason":"charter_trusted_observed_mismatch"`, rc=2.
- True digest `099de884…c95d81` + packet `5448c4e4…6926`: `"result":"PASS"`, rc=0, five exhibits `expected == observed`.
- Auto-loaded before any choice: global `~/.claude/CLAUDE.md`, worktree `CLAUDE.md`, `MEMORY.md` index (one-line pointers; the top line names this activation and "EPOCH_EQUIVALENCE FAIL", which the packet does not depend on). Not opened: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, any memory file, any record beyond exhibits A–E. Code read only as `git show 37ca3c35:` copies under `/tmp`. No tracked file touched except this one. Canonical root, measurement roots, night custody, LaunchAgents untouched.

## Executed probes

1. `/tmp/cg2-d0b83820/probe.py`: fake clock (copy of the test-file `FakeClock` plus a `true_cpu` counter standing in for the kernel's charge, `charged = true_cpu + 0.19 s` start-up per refutation 12), the round-2 assertion block re-implemented as a function with the floor switchable, run against `duty_periods` from `37ca3c35` (`PYTHONPATH` = the read-only harness worktree). Output, verbatim:

```text
--- floor kept = True ---
zero-service (first wake 3.001s)   rows=0 claimed=0.0000 charged=0.1900 fails=['liveness_floor']
first scheduled 2s late            rows=2 claimed=0.1000 charged=0.2900 fails=NONE
burn preempted 100x                rows=6 claimed=0.0301 charged=0.2201 fails=NONE
no starvation control              rows=6 claimed=0.3000 charged=0.4900 fails=NONE
MUTATION clock (cpu->0)            rows=6 claimed=0.0000 charged=3.1900 fails=['liveness_floor', 'kernel_ceiling']
--- floor kept = False ---
zero-service (first wake 3.001s)   rows=0 claimed=0.0000 charged=0.1900 fails=NONE
first scheduled 2s late            rows=2 claimed=0.1000 charged=0.2900 fails=NONE
burn preempted 100x                rows=6 claimed=0.0301 charged=0.2201 fails=NONE
no starvation control              rows=6 claimed=0.3000 charged=0.4900 fails=NONE
MUTATION clock (cpu->0)            rows=6 claimed=0.0000 charged=3.1900 fails=['kernel_ceiling']
ratio=100 wake_late_s: [0.005, 0.0, 0.0, 0.0, 0.01, 0.01] max 0.009999999999990461
late-start wake_late_s: [0.0, 0.0]
burn_profile(scalar,1)(1) = 1015568748 expected 1015568748
second call differs: 1586005467
memory profile returns int: True
noop kill: True
```

   The zero-service witness (seat V8) reproduces: `periods=[]`, `claimed_s = 0`, only the floor fails. With the floor removed the four correct-code inputs pass and the `clock` mutation still dies on the kernel ceiling (3.19 s > 0.92 s), matching the seat's real-path diagnostic (3.195601 > .92) and refutation 12 §3.
2. Single test-module run, read-only, `wt-harness-232` at `37ca3c35` (clean before and after): `Ran 43 tests in 4.854s — OK`, rc=0.

## Q1 — ruled: option (a). DELETE the liveness floor.

**Exact deletion** (tests/test_sample_quiet_predicate_evidence.py, real-load test, the one line between the per-period loop and the kernel cross-check comment):

```python
        self.assertGreater(claimed_s, 0.0, "no CPU burned: the real burn profile did no work")
```

Remove that line and nothing else. The block that remains is: aggregate ceiling `fraction <= .14`; per-period ceiling `cpu_used_s <= budget_cpu_s + overshoot_bound_cpu_s + 1e-9`; kernel lower bound `charged_s >= claimed_s - .01`; kernel ceiling `charged_s <= .14 * duration_s + STARTUP_CPU_S`; cleanup assertions. Replace the deleted line's job with the comment already present ("Delivery is reported, never asserted") — no new comment needed.

**Deciding evidence.** Probe rows above: the floor is the only assertion any correct-code input fails, and the only mutation it kills (`clock`) dies on the kernel ceiling regardless (executed on the real path by the seat: 3.195601 > .92; executed here on the fake clock: 3.19 > .92). An assertion that kills nothing unique and is the only source of a correct-code failure has no kill power to trade against its false-failure surface; it goes.

**Why not (b).** Declaring the assumption does not remove the signature; it labels it. The gate was convened (third round, same defect) to remove the shape "assertion fails on correct code under starvation", and D-161/sensible-gates cover tolerance *size*, not a tolerance of zero on a quantity the scheduler owns.

**Why not (c).** Conditioning on `charged_s > STARTUP_CPU_S` is safe (zero-service: charged 0.19 < 0.5, floor skipped) but it is still keyed to a starvation-destroyed quantity — now `charged_s` — and every input on which the condition fires (charged > 0.5 s with claimed = 0) already fails the kernel ceiling or is a ≥ 0.31 s-of-kernel-CPU-with-zero-claim case that the kernel lower bound does not see and that no bench input produces. (c) equals (a) in kill power plus a second heuristic constant. Rejected.

**Same-signature statements under (a):**

- "real-load assertion fails on correct code under scheduler starvation": **NOT FOUND**. Executed: zero-service, first-wake-2 s-late, burn-preempted-100×, and control all pass with `fails=NONE`. Structural reason: every remaining assertion is either a ceiling on a quantity starvation can only lower (`fraction`, per-row `cpu_used_s`, `charged_s`) or the kernel lower bound, whose right-hand side (`claimed_s`) starvation lowers, which loosens it.
- "assertion keyed to a quantity starvation destroys": **NOT FOUND in the failing direction**. One remaining assertion references `claimed_s` (the kernel lower bound), but only as a bound that starvation relaxes; process CPU ≥ thread CPU holds for any schedule. No assertion becomes tighter as delivered CPU falls.

**Accepted residual (state in the memo, one sentence):** the real-load test no longer proves that the spawned child performed any work; a child that starts, emits no rows and exits 0 passes. That property is proved deterministically by `test_cpu_budget_overshoot_and_frozen_duty` (1.8 ± 0.01 CPU-s) and, after Q2 below, by a direct test of the burn function.

## Q2 — ruled: option (b), fix in this round. Exact test text

Add to `LoadTests` (or any class in the module; test-file only, no row field added or altered, so **no contract change** under `joulewise.quiet_predicate_evidence.v1`):

```python
    def test_burn_profile_performs_the_generator_work(self):
        # Kills the burn-noop mutation: the budget loop accrues its own CPU, so no
        # accounting assertion can tell "burned the work" from "spun the loop".
        # The burn returns its generator state; one LCG step from seed 1 is fixed.
        burn = harness.burn_profile("scalar", 1)
        self.assertEqual(burn(1), (1664525 * 1 + 1013904223) & 0xFFFFFFFF)   # 1015568748
        self.assertNotEqual(burn(1), 1015568748)                              # state advanced
        self.assertIsInstance(harness.burn_profile("memory", 1)(16), int)
```

Executed: `burn_profile("scalar", 1)(1) == 1015568748`, second call `1586005467`, memory profile returns an int. The mutation `burn_profile → lambda count: None` fails the first assertion (`None != 1015568748`, probe line `noop kill: True`); a constant-returning no-op fails the second. This is the smallest assertion that distinguishes work from loop overhead, and it is deterministic. Reason a reader without project grounding can follow: the real-load test measures CPU *time*, and an empty loop also spends CPU time, so time cannot prove work; the burn function's own return value can. Bench acceptance for this round adds `burn-noop` to the must-die list (expect exactly this test to fail).

## Q3 — F3: AFFIRM the seat's resolution

Preempted-burn regression keeps record 11's `self.assertLess(p["wake_late_s"], .05)`; late-start regression keeps ruling 10's `< 1e-3`. Executed: under `FakeClock.ratio = 100` correct rows carry `wake_late_s = [0.005, 0, 0, 0, 0.01, 0.01]`, so `< 1e-3` fails correct code on four of six rows; under the late-start fixture lateness is `[0.0, 0.0]`, so `< 1e-3` holds there. The `.05` figure is sized to the instrument: lateness at ratio 100 is at most one calibrated batch of wall time (batch ≈ 10 × 10 µs CPU × 100 = 0.01 s), and `.05` gives 5× margin over the largest observed value. Ruling 10's `< 1e-3` on the preempted fixture was wrong; record 11's executed value stands.

## Order

Fix round 3 = the one-line deletion (Q1) + the one added test (Q2), same file, same WRITE_SCOPE; bench: module twice (expect 44 OK), mutations `cores`, `alignment`, `observer`, `clock`, `catchup-capped`, `burn-noop` each ≥ 1 failure; then delta re-audit with the two same-signature statements above; then the PR gate.
