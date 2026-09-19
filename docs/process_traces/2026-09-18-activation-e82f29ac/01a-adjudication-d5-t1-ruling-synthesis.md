# Record 01a — adjudication of the D5-T1 cold gate (lead, 2026-09-18 23:16–23:2x PDT)

## Seats

| Seat | File | Wall | Result |
|---|---|---|---|
| Cold Fable judge (claude -p, detached worktree at `6f837e02`, doctrine-free apart from the auto-loaded `~/.claude/CLAUDE.md`, repo `CLAUDE.md`, `MEMORY.md` index — disclosed) | `01-…/10-coldgate-fable-ruling.md` | 23:06:11 → 23:10:36 (rc=0) | Q1 option (c): drop the delivery minimum, add a kernel `getrusage(RUSAGE_CHILDREN)` cross-check; no contract change; Q3 two fake-clock regressions + `clock` mutation |
| Opus contract refuter, independent answers written BEFORE the ruling existed | `01-…/11-opus-contract-refuter.md` | 23:06 → 23:10:04 | Q1 option (c): drop the minimum, add a per-period ceiling (`cpu_used_s ≤ budget_cpu_s + overshoot_bound_cpu_s`) and a liveness assertion; impossibility argument (no aggregate threshold accepts 0.0100 and rejects 0.0500); capped catch-up mutation (0.075 cores) dies only on the per-period ceiling |
| Opus refutation of ruling 10 (fresh seat) | `01-…/12-opus-refutation-of-ruling-10.md` | 23:12 → 23:15:5x | (1) AGREE rusage folds in at `load()`'s `join` (`:932`), executed; (2) DISAGREE with `charged_s ≤ claimed_s + STARTUP_CPU_S`: judge's 0.20 s startup figure came from a self-re-importing probe (clean: ≈0.19 s), the 0.5 s floor exceeds the whole 0.30 s budget, so the assertion kills no clock-scaling defect and is keyed to `claimed_s` — the D5-T1 shape again; (3) `clock` mutation is killed by liveness, not uniquely by the kernel check; kernel lower bound and ceiling DO carry unique kills (wrong-thread clock, over-reporting clock); (4) correct code can still fail assertion 2 once child startup CPU tops ≈0.5 s. BLOCKER on adopting ruling 10 verbatim; recommendation: union minus assertion 2 |

Anomalies: ruling 10 dates itself "~23:20–23:33 PDT"; the convene script's stdout `rc=0` line and the ruling file's mtime put it at 23:06–23:10. The judge's `STARTUP_CPU_S` measurement was polluted by its own probe's re-import (it noted the double print and did not correct the number); record 12 re-measured it.

## Adjudication (lead synthesis — split verdicts are synthesized, not majority-voted)

1. **Q1 ruled: option (c) as synthesized below.** The delivery minimum leaves the real-load test in both of its `498ad1d0` forms. Deciding argument: the docstring contract (Exhibit A, lines 775–778) promises a measured CPU *ceiling* and no catch-up, so any delivery minimum asserts the scheduler; record 11's impossibility result (0.0100 must pass, 0.0500 must fail, no monotone threshold on the aggregate fraction can do both) makes (a)/(c) forced without new fields. **No contract change**: no row field under `joulewise.quiet_predicate_evidence.v1` is added or altered; test file only.
2. **Written dissent from ruling 10 (rule 11: the magistrate overrules a cold verdict only with dissent Ed sees — this record and the stand-down email carry it):** ruling 10's second kernel assertion `charged_s ≤ claimed_s + STARTUP_CPU_S` is NOT adopted. Lead-checked arithmetic: budget CPU is 0.1 × 3 s = 0.30 s; with the ruling's own floor `STARTUP_CPU_S = 0.5` the bound is ≥ 0.5 s for every value of `claimed_s`, while a clock scaled by 1/k charges ≈ 0.30 + 0.19 s — never above 0.5 s — so the assertion cannot fail on any defect at this operating point, and it is keyed to `claimed_s`, the quantity starvation destroys. The rest of ruling 10 stands.
3. **The real-load assertion block for fix round 2** (replaces Exhibit B lines 621–631; `import resource` at module top; `before = resource.getrusage(resource.RUSAGE_CHILDREN)` immediately before `harness.load(args)`, `after` immediately after it returns; module constant `STARTUP_CPU_S = 0.5`):

```python
        periods = [p for worker in report["workers"] for p in worker["periods"]]
        claimed_s = sum(p["cpu_used_s"] for p in periods)
        fraction = claimed_s / args.duration_s
        charged_s = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
        # The controller promises a measured CPU ceiling and never catches up; it
        # promises nothing about CPU the scheduler declines to hand out (D5-T1,
        # cold-gate ruling 10 + refutation 12). Delivery is reported, never asserted;
        # budgeting is proved by test_cpu_budget_overshoot_and_frozen_duty.
        self.assertLessEqual(fraction, .1 + .04, f"over-burned: {fraction:.4f} cores")
        for period in periods:
            self.assertLessEqual(period["cpu_used_s"],
                period["budget_cpu_s"] + period["overshoot_bound_cpu_s"] + 1e-9,
                f"period {period['period']} burned past its budget: {period}")
        self.assertGreater(claimed_s, 0.0, "no CPU burned: the real burn profile did no work")
        # Kernel cross-check on the reaped child (rusage folds in at load()'s join):
        # what the worker claims can never exceed what the OS charged it, and the
        # OS-charged total is bounded by the ceiling plus the child's start-up CPU.
        self.assertGreaterEqual(charged_s, claimed_s - .01,
            f"kernel charged {charged_s:.3f} s < worker claimed {claimed_s:.3f} s")
        self.assertLessEqual(charged_s, .14 * args.duration_s + STARTUP_CPU_S,
            f"child burned {charged_s:.3f} s of kernel-accounted CPU in {args.duration_s} s")
```

   Lead check of the false-failure margin: correct code charges ≈ 0.30 + 0.19 s ≈ 0.49 s against a ceiling of 0.42 + 0.5 = 0.92 s; a wrong-thread clock (child burns a core, claims 0.05 s) charges ≈ 3 s → killed. Tolerance sized to the instrument (Ed's sensible-gates directive), not to delivery.
4. **Q2**: the memo wording of record 11 §Q2 is adopted (it names the independent killer and reads without project grounding); the ruling's Q2 sensitivity clause about clock scaling is superseded by dropping assertion 2.
5. **Q3 — regression spec**: record 11's two deterministic tests verbatim (`test_late_initial_scheduling_never_catches_up`, `test_preempted_burn_exits_on_the_wall_deadline`; `FakeClock` gains `ratio`, test-file only), with ruling 10's additional pins folded in where they are stricter (period ids `[4, 5]`; every `wake_late_s < 1e-3`; `work_budget_cpu_s ≤ .1 × elapsed_s + 1e-9`). Mutation set for acceptance: `cores`, `alignment`, `observer` (record 02a of 507514d5) + `clock` (`Clock.cpu → 0`; expected to die on liveness AND the kernel ceiling) + `catchup-capped` (carry unmet budget forward, total capped at share × duration; expected to die on the per-period ceiling and on the 0.1 CPU-s pin of test (i)) + `burn-noop` (`burn_profile` returns a no-op; the seat REPORTS which assertion kills it — the budget loop still accrues loop CPU, so liveness may not; if nothing kills it, that is a finding, not a fix). Real-load test stays macOS-only, real subprocess. Acceptance at the bench, unarmed census-clean machine: the single module twice under `unittest` (expect 43 tests OK), every mutation ≥ 1 failure, `charged_s − claimed_s` pasted from three unmodified runs.
6. **Order for the successor**: fix round 2 is a seat (Astra high, `WRITE_SCOPE: [tests/test_sample_quiet_predicate_evidence.py]`, brief = this record §3 and §5 + records 10/11/12) → bench verification → delta re-audit round 3 (fresh seat, read-only; same-signature statement against "real-load assertion fails on correct code under scheduler starvation" AND the new signature "assertion keyed to a quantity starvation destroys") → PR gate (sharded replay, hosted CI on the branch head, twelve-row ledger, terminal review, merge under D-072). Not this activation: the night is armed and the bench cannot run the real-load test without a load experiment.

## Executed evidence (this session)

- Packet validator PASS on `38e90169…` / charter `099de884…` (record 01 assembly, 23:05). Judge convened detached at 23:06:11 (pid 18022 group), rc=0 at 23:10:36; no `claude -p` alive after. Opus seats via the Agent tool, both complete by 23:16; no load runs, no test-module runs by any seat (the judge marked its module run NOT EXECUTED).
- Canonical root untouched at `422cdebb`; measurement root untouched at `d595aa9f`; all three LaunchAgents loaded; `standdown.request` absent at every slice boundary; directive issues none.
