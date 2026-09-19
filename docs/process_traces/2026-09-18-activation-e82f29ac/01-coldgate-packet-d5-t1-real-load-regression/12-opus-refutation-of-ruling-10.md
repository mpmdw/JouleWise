# 12 — Opus contract-lens refutation of cold-gate ruling 10 (kernel rusage cross-check)

Read-only worktree `JouleWise-wt-coldgate-e82f29ac` @ `6f837e02`. Probes: `git show 498ad1d0:…`, two `/tmp` snippets (three no-op spawn children, ≈0.03 s each; no load, no test module).

## (1) Does the rusage delta actually capture the worker? — AGREE, and it is already proved by an existing assertion

`resource.getrusage(RUSAGE_CHILDREN)` counts only **terminated and reaped** children. Executed probe (spawn context, this host, Python 3.14.7):

```text
trial0 exit=0 pre_reap=0.0000 post_reap=0.0268
trial1 exit=0 pre_reap=0.0000 post_reap=0.0264   # delta appears only after join()
```

`load()` reaps in its `finally`: `process.join(timeout=.5)` at `:932` (then terminate/`:935`, kill/`:938`), and only afterwards builds `report["cleanup"]` at `:941` from `p.exitcode`. The existing test already asserts `exitcode == 0` and `alive` false for every child, so a non-reaped child is a pre-existing test failure, not a silent hole in the cross-check. Pollution: `popen_spawn_posix._launch` starts the `resource_tracker` child, but it is long-lived and unreaped during the window, so it contributes 0 (confirmed: `pre_reap=0`). Residual (nit): if a *dead* tracker is reaped by `ensure_running()` inside the window, its CPU lands in the delta — bounded by one interpreter startup (≈0.03 s).

## (2) `STARTUP_CPU_S` sizing — DISAGREE: the stated basis is wrong and the floor exceeds the whole budget

The ruling's 0.20 s "no-op spawn child" was measured by a probe whose child **re-ran the probe script** (the ruling itself notes "the table printed twice"). Clean measurement: no-op spawn child = **0.026 s**; harness import = **0.163 s** (`PYTHONPATH` set, module path) → real child startup ≈ **0.19 s**. `max(0.5, 2 × 0.19)` = **0.5 s**.

The whole run's budget CPU is `0.1 × 3 s = 0.30 s`. **The tolerance (0.5 s) is larger than the entire quantity being checked (0.30 s).** The ruling's own sensitivity rule — a thread clock scaled by 1/k is caught only while `(k−1) × 0.3 > STARTUP_CPU_S` — therefore holds for **no finite k**: the maximum achievable gap (k→∞, `claimed = 0`) is 0.30 s < 0.5 s. `assertLessEqual(charged_s, claimed_s + STARTUP_CPU_S)` has **zero kill power at this operating point** while carrying the false-failure risk: with `-B`/`PYTHONDONTWRITEBYTECODE=1` in the acceptance command the child recompiles the harness source on every spawn, and contention inflates charged CPU further.

Worse, it reproduces **the D5-T1 signature a third time**: its slack is keyed to `claimed_s`, the quantity starvation destroys. Under the packet's own counterexample (burn preempted 100×, `claimed = 0.03 s`) the bound is `0.53 s`; a child whose startup charges 0.55 s under contention **false-fails on correct code**. The gate was convened to remove exactly this shape.

The other two kernel assertions are sound: `charged ≥ claimed − .01` is scheduler-independent (process CPU ≥ thread CPU, with ≈0.19 s of startup headroom) and `charged ≤ .14 × duration + S` is a pure ceiling, unkeyed to delivery, where 0.5 s is harmless because its targets are ≥ 1-core burns.

## (3) Unique catches — PARTLY DISAGREE with the ruling's claim

- The ruling's named example, mutation `clock` (`Clock.cpu → 0`), is **not** a unique catch: `cpu_used_s` is then 0 in every row, so report 11's liveness assertion (`sum > 0`) kills it, and so does the kernel *ceiling* (charged ≈ 3 s, the burn loop then exits only on the wall deadline). Assertion 2 is not what kills it.
- Genuine unique catch for the kernel **ceiling**: a thread clock wired to the wrong (idle) thread — child truly burns a core, reports a plausible 0.05 s. Report 11 passes it on all three checks (aggregate 0.017 ≤ .14, per-period ✓, live ✓); `charged 3.0 > 0.92` kills it. Keep the ceiling.
- Genuine unique catch for the kernel **lower bound**: an over-reporting clock (claims 0.3 s, burns 0.05 s) — invisible to every self-reported check, `0.24 < 0.29` kills it.
- Unique catches the ruling **loses**: report 11's **capped catch-up** mutation (0.075 cores aggregate, per-period ceiling broken — executed in report 11) and a **dead worker** (claimed 0, charged ≈ 0.19 s startup) pass every assertion in ruling 10's block. A real burn profile that produces no work is only exercised on this path.

## (4) Correct code the ruled block still rejects — YES

The starvation cases themselves, once startup CPU exceeds ≈0.5 s (cold `-B` compile plus contention): assertion 2's bound collapses with `claimed_s` to 0.53 s while charged CPU does not. Second case: any correct run where `load()` falls through the terminate/kill path with a child still alive at `:938` — the delta then omits it and the lower bound fires (masked today only because the `exitcode == 0` assertion fails first).

## Recommendation

Take the **union, minus ruling 10's second assertion**. Concretely: report 11's aggregate ceiling, per-period `budget_cpu_s + overshoot_bound_cpu_s` ceiling and liveness assertion (these carry the capped-catch-up and dead-worker kills), plus ruling 10's kernel **lower bound** (`charged ≥ claimed − .01`) and kernel **ceiling** (`charged ≤ .14 × duration + STARTUP_CPU_S`, `STARTUP_CPU_S = 0.5`), which carry the two wrong-thread/over-reporting kills that self-reported fields cannot see. **Delete `assertLessEqual(charged_s, claimed_s + STARTUP_CPU_S)`** — it kills nothing at 0.1 cores × 3 s and is the same delivery-keyed shape D5-T1 is about. **BLOCKER flag on adopting ruling 10 verbatim**: assertion 2 is a fourth false-failure surface keyed to delivered CPU; the rest of the ruling (option (c), no contract change, Q3 fixtures) stands, and its Q3 spec should be merged with report 11's, which additionally names the capped-catch-up counterfactual.
