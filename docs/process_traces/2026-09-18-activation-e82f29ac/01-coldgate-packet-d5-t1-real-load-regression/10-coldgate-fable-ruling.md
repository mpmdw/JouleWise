# Cold-gate ruling 10 — D5-T1: what a real-scheduler regression may assert about delivered CPU share

Judge: cold Fable 5.1 seat, worktree `JouleWise-wt-coldgate-e82f29ac`, 2026-09-18 ~23:20–23:33 PDT. Validator: REFUSE on the deliberately mistyped charter digest (`...a880...`, reason `charter_trusted_observed_mismatch`), PASS on the true digest `099de884…c95d81` with packet `38e90169…8ba2e6` and all five exhibit digests matching.

## Contamination disclosure

Auto-loaded before I chose anything: the global `~/.claude/CLAUDE.md`, this worktree's `CLAUDE.md`, and the memory index `MEMORY.md` (one-line pointers only; several mention lane 232 and "D5-T1 NOT FIXED", which I already knew from the packet). I did not open CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, any memory file, or any record beyond the verbatim extracts in exhibits A–E. Code read only via `git show 498ad1d0:` copies under `/tmp`. No subagents, no background work, no edits to tracked files other than this one.

## Q1 — ruled option: (c), a stronger form of (a)

**Ruling.** Drop the delivery minimum from the real-load test (both the tight two-sided check and the lateness-keyed relaxation). Keep the self-reported over-burn ceiling, the pre-launch share guard, the cleanup assertions, and the fake-clock tests as the budgeting oracle. Add one thing (a) lacks: a kernel-side cross-check. The parent process reads the operating system's own CPU accounting for its reaped children (`resource.getrusage(RUSAGE_CHILDREN)`) before and after the run, and requires that the CPU the worker *claims* it burned (sum of `cpu_used_s`) agrees with the CPU the kernel *charged* the child. This holds under any starvation, because starvation reduces both numbers equally, yet it catches every real-path defect the fake clock cannot see (a mis-wired thread clock, a busy-wait sleep), which is exactly what a real-subprocess test exists to prove.

**Why not (b).** Recording initial lateness and a per-period preemption ratio would still leave the bound heuristic (preemption between the last clock check and the boundary, missing periods that emit no row at all, see probe: the 2 s late start emits only rows 4 and 5). The no-catch-up rule (Exhibit A, lines 775–778) means the worker guarantees nothing about delivery; a test that asserts delivery is asserting the scheduler, not the code. Delivered share is *reported* (`stationarity.mean_busy_cores`) for the memo, not gated.

**Exact assertion text** (replaces Exhibit B lines 621–631, from `fraction = ...` through the `else:` branch; add `import resource` at module top):

```python
        periods = [p for worker in report["workers"] for p in worker["periods"]]
        claimed_s = sum(p["cpu_used_s"] for p in periods)
        fraction = claimed_s / args.duration_s
        charged_s = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
        # Over-burning is a budgeting defect under any scheduling: never allowed.
        # Delivery has no minimum: the no-catch-up controller guarantees nothing a
        # starved scheduler must honour (D5-T1, cold-gate ruling 10).
        self.assertLessEqual(fraction, .1 + .04, f"over-burned: {fraction:.4f} cores")
        # Kernel cross-check: what the worker claims must agree with what the OS
        # charged the reaped child. Starvation lowers both equally; a mis-wired
        # thread clock or a spinning sleep breaks the agreement.
        self.assertGreaterEqual(charged_s, claimed_s - .01,
            f"kernel charged {charged_s:.3f} s < worker claimed {claimed_s:.3f} s")
        self.assertLessEqual(charged_s, claimed_s + STARTUP_CPU_S,
            f"kernel charged {charged_s:.3f} s; worker claimed {claimed_s:.3f} s")
        self.assertLessEqual(charged_s, .14 * args.duration_s + STARTUP_CPU_S,
            f"child burned {charged_s:.3f} s of kernel-accounted CPU in {args.duration_s} s")
```

with `before = resource.getrusage(resource.RUSAGE_CHILDREN)` taken immediately before `harness.load(args)` and `after = ...` immediately after it returns (the `finally` in `load`, Exhibit A-adjacent lines 928–933, joins the child, so its CPU has folded into the parent's children accounting; the cleanup rows already assert `exitcode == 0`). `STARTUP_CPU_S` is a module constant: the CPU a spawned child spends importing the harness before the burn. Probe measured 0.20 s for a no-op spawn child; the seat measures the real child (three runs, `charged_s − claimed_s` on the unmodified branch) and sets `STARTUP_CPU_S = max(0.5, 2 × max observed)`, recorded in the round-2 record. Sensitivity to note: a defect that scales the thread clock by 1/k is caught only while `(k−1) × 0.3 s > STARTUP_CPU_S`, so the constant must stay under about 1.0 s; if measurement forces more, report it and this ruling's kernel ceiling still kills a full-core burn (3 s ≫ 0.42 s + 1.0 s).

**Contract change:** none. No period-row field is added or altered; `joulewise.quiet_predicate_evidence.v1` is untouched. No paired refuters are required on the schema; the ordinary delta re-audit suffices.

**Reason / deciding evidence.** Executed fake-clock probe (below): both surviving counterexamples fail the current relaxed check (`old_relaxed_ok=False`) and pass the ruled ceiling-only check; the 1.05 s late-wake witness passes both; the on-time half-budget defect passes the ruled check but is killed by `test_cpu_budget_overshoot_and_frozen_duty` (probe: correct code sums 1.7998 against the 1.8 ± 0.01 pin; Exhibit E, E2: the half-budget mutation sums 0.900). Corroborating: Exhibit E, E5 shows the "tight" branch never fires on an idle host, so the current delivery minimum was already dead as a guard and alive only as a false-failure source.

## Q2 — residual and limitation statement (memo wording)

The real-load test runs the load worker as a genuine operating-system process for three seconds at a requested tenth of one core and proves four things: the worker is launched with the requested share; it never burns more than 0.14 cores by its own thread clock, nor more than that plus a fixed start-up allowance by the kernel's accounting; the CPU it reports agrees with the CPU the kernel charged it; and it exits cleanly and is reaped. It does not prove that the worker *received* a tenth of a core. The worker asks for its budget in each half-second period and discards whatever the scheduler did not let it run (it never catches up), so on a busy machine the delivered share can legitimately be far below the setting with no defect in the code. The delivered share is therefore reported as a measurement (`mean_busy_cores`), never asserted. The one defect class that could hide behind starvation, a controller that asks for less than its budget while on time, is caught independently by the fake-clock budget test, which requires exactly 1.8 CPU-seconds from a 0.2-core, 9-second run within 0.01 s; the probe and record 05 E2 both show a half-budget controller failing it. Accepted residual: a thread-clock scaling defect smaller than the start-up allowance (see Q1 sensitivity note) is not caught on the real path.

## Q3 — regression specification for fix round 2

```text
Files: tests/test_sample_quiet_predicate_evidence.py only (harness untouched).
Real-load test stays macOS-only, real subprocess, non-deterministic in delivery;
its assertions are now scheduler-independent (Q1 block). Two new deterministic
fake-clock tests beside it, using FakeClock subclasses defined in the test module:

(i) test_duty_periods_late_first_schedule_burns_only_reachable_periods
    clock = FakeClock(); clock.now = 2.0
    rows = harness.duty_periods(.1, 3, .5, clock.burn, clock, start=0.0)
    Correct code: rows for periods {4, 5} only; sum cpu_used_s == 0.1 ± 0.001;
      every row cpu_used_s >= work_budget_cpu_s - max_quantum_cpu_s (ask met);
      every wake_late_s < 1e-3; every overrun_cpu_s <= overshoot_bound_cpu_s.
    Also assert the ruled real-load ceiling on these rows: sum/3 <= .14.
    Kills: "carry-forward" mutation (delete the `if boundary <= now: index = ...`
      re-index so periods 0-3 are burned after start+2, or `budget = share *
      (boundary - start)` on the first row) -> sum cpu_used_s 0.3, fails the pin.

(ii) test_duty_periods_preempted_burn_exhausts_wall_not_budget
    class PreemptedClock(FakeClock): burn advances now by 100x the cpu it adds.
    rows = harness.duty_periods(.1, 3, .5, clock.burn, clock, start=0.0)
    Correct code: 6 rows; sum cpu_used_s == 0.03 ± 0.001 (0.005 per period);
      every row cpu_used_s < work_budget_cpu_s (ask unmet);
      every wake_late_s < 1e-3 (the loop stopped AT the wall deadline);
      no catch-up: work_budget_cpu_s of each row <= .1 * elapsed_s + 1e-9.
    Kills: drop the wall-deadline term (`and clock.monotonic() < boundary`) from
      the burn loop -> each period burns to budget over ~5 s wall, wake_late_s
      ~4.5 s and sum cpu 0.3, fails both pins; reinstating catch-up (debt made
      negative / carried) fails the work_budget bound.

(iii) The on-time under-burn defect (budget halved at script line 796) needs no
    new test: test_cpu_budget_overshoot_and_frozen_duty kills it (0.900 vs 1.8).
    Add scratch mutation `clock` (Clock.cpu = staticmethod(lambda: 0.0)) to prove
    the kernel cross-check bites on the real path: expected to fail the kernel
    ceiling (child burns ~3 s, claims 0). File it beside the three in record 02a.

Acceptance (bench, unarmed census-clean machine, from the branch worktree):
  env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest \
      tests.test_sample_quiet_predicate_evidence          # twice, both OK
  mutations: cores, alignment, observer (record 02a of activation 507514d5)
      + clock -> each must report >= 1 failure/error; paste counts.
  STARTUP_CPU_S measurement: three unmodified runs, paste charged_s - claimed_s.
  Then delta re-audit round 3 (one changed test, two added), then the PR gate.
```

## Executed probes (commands and outputs, abbreviated)

1. Validator, typo digest → `"result":"REFUSE","reason":"charter_trusted_observed_mismatch"`, rc=2. True digest → `"result":"PASS"`, five exhibits `expected == observed`, rc=0.
2. `git show 498ad1d0:scripts/sample_quiet_predicate_evidence.py > /tmp/cg_script.py` and the test file likewise; read `Clock` (105–119), `duty_periods` (770–828), `stationarity` (830–846), `load_worker` (860–875), `load` (880–933), `FakeClock` (test 18–40). Worktree `wt-harness-232` at `498ad1d0`, clean, untouched.
3. `/tmp/cg_probe.py` (fake clock; `PYTHONPATH` = the branch worktree, read-only), output:

```text
late wakes 1.05s (round 1)     rows= 2 frac=0.0333 late=2.100 sum_work_budget=0.1000 ceiling_ok=True old_tight_ok=False old_relaxed_ok=True
first scheduled at start+2s    rows= 2 frac=0.0333 late=0.000 sum_work_budget=0.1000 ceiling_ok=True old_tight_ok=False old_relaxed_ok=False
burn preempted 100x            rows= 6 frac=0.0100 late=0.025 sum_work_budget=0.3000 ceiling_ok=True old_tight_ok=False old_relaxed_ok=False
no starvation (control)        rows= 6 frac=0.1000 late=0.000 sum_work_budget=0.2999 ceiling_ok=True old_tight_ok=True  old_relaxed_ok=True
half-budget on time (defect)   rows= 6 frac=0.0500 late=0.000 sum_work_budget=0.1497 ceiling_ok=True old_tight_ok=False old_relaxed_ok=False
fake-clock oracle, correct .2-> sum=1.7998 (needs 1.8±.01)
spawn no-op child: children cpu 0.201 s, wall 0.21 s, exit 0
```

   (The table printed twice because the spawn child re-imported the probe script; harmless, one process, 0.2 s.) The two counterexample numbers match record 05 exactly (0.03333, late 0; 0.01003, late 0.025).
4. Single test-module run: NOT EXECUTED (not needed for the ruling; wall budget reserved). No load run. Every process ended inside 2 s. Canonical root, measurement roots, night custody and LaunchAgents untouched.
