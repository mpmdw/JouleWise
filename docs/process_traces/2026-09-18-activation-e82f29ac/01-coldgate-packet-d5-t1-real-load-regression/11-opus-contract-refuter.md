# 11 — Opus contract-lens refuter, D5-T1 (packet 00-PACKET.md sha256 38e90169… verified)

Read-only worktree `JouleWise-wt-coldgate-e82f29ac` @ `6f837e02`. Probes: `shasum`, `git show 498ad1d0:…`, two fake-clock snippets under `/tmp` (no load, no test module run).

## Contract lens (the deciding argument)

`duty_periods` promises, in its own docstring: "unsatisfied CPU is never carried forward under contention… a **measured CPU bound**, not a real-time scheduling guarantee." That is an **upper** bound on delivered thread CPU and an explicit refusal of any **lower** bound. A delivery *minimum* in the real-load test therefore asserts a promise the code under test does not make: it tests the OS scheduler, not the harness. The 498ad1d0 starvation branch did not fix that, it re-parameterised it — `wake_late_s` is the lateness of the sleep *inside* `duty_periods` only, so starvation before period 0 (`:869`) and preemption during a burn (`:800`) leave no trace in the term the bound is keyed to.

**Impossibility result (mine, arithmetic, not opinion).** Any assertion that is a lower bound on the aggregate fraction alone must ACCEPT 0.0100 cores (burn preempted 100×) and REJECT 0.0500 cores (on-time half-budget). 0.0100 < 0.0500, so no monotone threshold on `fraction` can do both. Option (a)/(c) is thus forced *unless* new evidence fields are emitted (option (b)); and under (a)/(c) the half-budget defect must be, and is, rejected elsewhere.

## Q1 — ruled option: (c), = (a) plus two contract-shaped assertions

Drop the share-keyed delivery minimum entirely (both branches of 498ad1d0). Keep the pre-launch share guard, the cleanup/reaping block, and the fake-clock tests as the budgeting oracle. Replace the delivery block with:

```python
        periods = [p for worker in report["workers"] for p in worker["periods"]]
        fraction = sum(p["cpu_used_s"] for p in periods) / args.duration_s
        # The controller promises a measured CPU *ceiling* and no catch-up; it
        # promises nothing about CPU the scheduler declines to hand out. So this
        # real-scheduler test asserts only the ceiling (per period and in
        # aggregate) and liveness. Delivery against the requested share is
        # proved deterministically by test_cpu_budget_overshoot_and_frozen_duty.
        self.assertLessEqual(fraction, .1 + .04, f"over-burned: {fraction:.4f} cores")
        for period in periods:
            self.assertLessEqual(period["cpu_used_s"],
                period["budget_cpu_s"] + period["overshoot_bound_cpu_s"] + 1e-9,
                f"period {period['period']} burned past its budget: {period}")
        self.assertGreater(sum(p["cpu_used_s"] for p in periods), 0.0,
            "no CPU burned: the real burn profile did no work")
```

Contract change: **none**. No harness field is added or removed; the JSON row shape under `joulewise.quiet_predicate_evidence.v1` is untouched; `budget_cpu_s` and `overshoot_bound_cpu_s` already exist (Exhibit A `:820`). Mutation kills are not weakened: `cores` dies at the pre-launch share guard (`:609`) and at the fake-clock budget test, `alignment` at `:118/:206`, `observer` at `:388` — none of them at the deleted minimum (record 05 E3).

Why not (b): it is a contract change (a worker-level `start_late_s` and a per-period burn-wall field) that buys **no unique mutation kill** — its only extra catch, the on-time half-budget defect, is already killed by the named fake-clock oracle — while adding a second heuristic bound with fresh false-failure surface (calibration `duty` shrinkage and `debt` carry are legitimate correct-code deficits that its starvation terms still do not cover). If the magistrate nonetheless wants `start_late_s`, take it as **diagnostic evidence only**, never as an assertion input, and declare it as an additive schema change (the ROUND_KEYS test at `tests/…:403` is a subset check, so additive fields do not break it).

## Q2 — residual and limitation statement

The real-load test proves that the worker starts with the share the command line asked for, that it never burns more CPU than its own per-period budget plus the measured overshoot allowance, that it does some work, and that every child process is reaped and gone. It proves **nothing** about how much CPU the worker actually receives: a machine's scheduler may delay the worker's first wake, or interrupt it mid-burn, and the controller deliberately discards the CPU it was not given rather than catching up later. Both are ordinary behaviour of a busy computer, not faults in this program, and the log cannot tell them apart from a program that simply asked for too little. The claim "the load ran at 0.1 of a core" is therefore backed by the deterministic simulated-clock test, which pins total burned CPU to 1.8 CPU-seconds within 0.01 for a 0.2-core, 9-second run — plus the recorded per-period rows in the evidence file, which state what each real run actually delivered. The residual (a controller that under-burns on time) is **not accepted as uncovered**: `test_cpu_budget_overshoot_and_frozen_duty` catches it — executed here, a half-budget mutant delivers 0.9001 CPU-s against the required 1.8 ± 0.01.

## Q3 — regression specification (fix round 2)

```python
    def test_late_initial_scheduling_never_catches_up(self):
        clock = FakeClock(); clock.now = 2.0          # first wake 2 s after start
        periods = harness.duty_periods(.1, 3, .5, clock.burn, clock, start=0.0)
        self.assertAlmostEqual(sum(p["cpu_used_s"] for p in periods), .1, delta=.002)
        self.assertEqual([p["period"] for p in periods], [4, 5])
        for p in periods:
            self.assertLessEqual(p["cpu_used_s"], p["budget_cpu_s"] + p["overshoot_bound_cpu_s"] + 1e-9)
            self.assertAlmostEqual(p["wake_late_s"], 0.0, delta=2e-4)   # lateness is blind to this

    def test_preempted_burn_exits_on_the_wall_deadline(self):
        clock = FakeClock(); clock.ratio = 100.0      # burn advances wall 100x thread CPU
        periods = harness.duty_periods(.1, 3, .5, clock.burn, clock, start=0.0)
        self.assertAlmostEqual(sum(p["cpu_used_s"] for p in periods), .03, delta=.005)
        self.assertLessEqual(periods[-1]["end_mono_s"], 3.0 + 1e-9)      # window still honoured
        for p in periods:
            self.assertLessEqual(p["cpu_used_s"], p["budget_cpu_s"] + p["overshoot_bound_cpu_s"] + 1e-9)
            self.assertLess(p["wake_late_s"], .05)
```

`FakeClock` gains two attributes (`ratio` default 1.0 scaling the wall advance in `burn`; `now` already settable) — test-file only, no production change. Correct code must produce exactly these numbers (executed below). Counterfactual mutations killed: (i) **reverting the no-catch-up rule** at `:796` so unmet budget carries forward — under the late-start fixture a *capped* catch-up (total never exceeding `share × duration`) delivers 0.0750 cores, which passes both the 0.14 ceiling and the old ±0.04 check yet breaks the per-period ceiling: this defect is invisible to every assertion that exists today and dies only here; an uncapped catch-up delivers 0.1834; (ii) **dropping `clock.monotonic() < boundary` from the burn loop** at `:800` — the preempted burn then runs to its CPU budget and overruns the window, failing the `end_mono_s`/total assertions; (iii) an **on-time under-burning controller** stays the property of `test_cpu_budget_overshoot_and_frozen_duty` (0.9001 vs 1.8 ± 0.01).

The real-load test **stays** a macOS-only real-subprocess test (it is the only exercise of spawn, native QoS, the real burn profile and child reaping) but loses every delivery claim; both new tests are deterministic and platform-independent. Bench acceptance: `python3 -B -m unittest tests.test_sample_quiet_predicate_evidence` twice (expect 43 tests OK), then the three mutation modules from record 02a of activation 507514d5 — `cores`, `alignment`, `observer` — each still failing ≥ 1 test.

## Executed probes (fake clock, `/tmp`, no load, no test module)

```text
case                           cores  late_s  498ad1d0   aggCeil  perPeriodCeil  live
correct/idle                  0.1000   0.000      True      True           True  True
correct/wake 1.05s late       0.0333   2.100      True      True           True  True
correct/first sched +2s       0.0333   0.000     False      True           True  True
correct/burn wall x100        0.0100   0.025     False      True           True  True
DEFECT/half budget ontime     0.0500   0.000     False      True           True  True
capped-catchup/first sched +2s: cores=0.0750 aggCeil=True old_two_sided=True perPeriodCeil=False
half-budget vs the fake-clock oracle: total_cpu=0.9001 (needs 1.8 +/- .01) -> killed=True
catchup(uncapped)/first sched +2s: 0.1834 ; catchup/idle: 0.3500  (both fail aggCeil and perPeriodCeil)
```

Both packet counterexamples reproduced to the auditor's digits (0.0333 / late 0; 0.0100 / late 0.025). The ruled assertions accept all three correct-code inputs and reject the on-time half-budget defect only via the named oracle, as declared.

## Ruling refutation

Ruling not yet available at my budget; independent answers only.
