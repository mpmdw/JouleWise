# 11 — Opus contract-lens refuter, D5-T1 liveness floor (independent of the cold-gate judge)

Read-only. Worktree `JouleWise-wt-coldgate-d0b83820` @ `42cc9f35`; code under judgment read via `git show 37ca3c35:`.

## The contract, stated before it is used

`scripts/sample_quiet_predicate_evidence.py:771-778` (`duty_periods` docstring) promises exactly four things: (1) **thread-CPU budgets** — CPU consumed per period is bounded by `share x elapsed` plus a *measured* overshoot bound; (2) **absolute wall deadlines** — periods end on the nominal boundary, never later by burning; (3) **no catch-up** — "unsatisfied CPU is never carried forward under contention"; (4) the explicit disclaimer at :778, "**This is a measured CPU bound, not a real-time scheduling guarantee.**"

Derivable from that promise: **upper bounds only**, plus accounting honesty. Every assertion that is an upper bound on burned CPU (aggregate ceiling, per-period ceiling, kernel ceiling `charged_s <= .14*duration + STARTUP_CPU_S`) and the no-fabrication direction (`charged_s >= claimed_s - .01`) is derivable. **Not derivable: any lower bound on CPU in a real-load run.** A lower bound on `claimed_s` is a statement about what the scheduler handed out, i.e. exactly (4)'s disclaimer inverted. Lower bounds ARE derivable under a fake clock, where no scheduler exists — which is why `tests/...:662` (`cpu_used_s >= work_budget - max_quantum`) is legitimate and `:640` is not.

## Q1 — ruled option: **(d)** = the deletion of (a) **plus** a mandated deterministic replacement. (a) alone is refuted; (c) is refuted.

**Exact deletion** — remove `tests/test_sample_quiet_predicate_evidence.py:640` verbatim:

```python
        self.assertGreater(claimed_s, 0.0, "no CPU burned: the real burn profile did no work")
```

**Exact replacement**, a new deterministic test in `LoadTests` (no `skipUnless`; fake clock, no scheduler, no subprocess):

```python
    def test_load_worker_runs_its_window_after_the_rendezvous(self):
        clock = FakeClock()
        sent = []
        connection = SimpleNamespace(send=sent.append, recv=lambda: 1.0, close=lambda: None)
        with patch.object(harness, "set_qos", lambda qos: None), \
                patch.object(harness, "identity", return_value={"pid": 11}), \
                patch.object(harness, "burn_profile", return_value=clock.burn), \
                patch.object(harness, "Clock", return_value=clock):
            harness.load_worker(connection, {"share": .1, "duration_s": 3, "period_s": .5,
                "qos": "user-initiated", "profile": "scalar", "seed": 1})
        self.assertEqual(len(sent), 2, sent)
        self.assertNotIn("error", sent[1])
        periods = sent[1]["periods"]
        self.assertGreater(len(periods), 0, "worker reported no period rows for its window")
        self.assertAlmostEqual(sum(p["cpu_used_s"] for p in periods), .3, delta=.001)
        self.assertEqual(clock.monotonic(), 4.0)   # rendezvous at 1.0 plus the 3 s window
```

### Why (a) alone fails: the strongest defect it hides, executed

Delete `:640` and **every remaining real-load assertion is an upper bound or a loop over rows**, so a report with **zero period rows passes vacuously**. The concrete production mutation: `scripts/sample_quiet_predicate_evidence.py:869`, the rendezvous `clock.sleep_until(start)` -> `clock.sleep_until(start + config['duration_s'])` — the child sleeps through the window it was launched to load. Executed (P7b): `load_worker` returns **6 -> 0 rows, `claimed_s = 0`, no `error` key**; with the measured startup-only charge `charged_s ~ 0.34 s` (Exhibit B: correct runs charge 0.634-0.644 against claimed 0.300, so residual ~ 0.34), the four survivors evaluate `fraction .0 <= .14` True, per-period loop 0 iterations, `charged >= claimed - .01` True, `charged <= .92` True -> **mutation SURVIVES**. No fake-clock test covers `:869`; the existing ones call `duty_periods` with an explicit `start=`. The alignment/anchor tests that kill the seat's `alignment` mutation (Exhibit B table) are clock-anchor tests and do not touch this line.

### Why (c) also fails

Same mutation, guard `charged_s > STARTUP_CPU_S` (= 0.5, `tests/...:20`): executed `0.34 > 0.5` is **False** -> the assertion never fires -> **(c) survives the same defect**. (c) therefore buys no demonstrated unique kill over (a): the seat's `clock` mutation is already killed by the kernel ceiling, and a row-zeroing mutation inside `duty_periods` is killed by the fake-clock totals at `:657`. An assertion with no demonstrated unique kill and a nonzero false-failure mode on correct code is precisely what refutation 12 condemned in the floor; consistency forbids re-adopting it under a guard.

### The structural finding

Correct-but-starved and mutated-to-skip-the-window are **observationally identical** at the real-load layer: both give `claimed_s = 0`, zero rows, `charged_s ~ startup`, no error. No assertion over those observables can separate them. The coverage therefore cannot live in the real-load test at all; it must live where the scheduler is not a variable — the fake-clock layer, which the replacement test supplies.

### Same-signature statements under the ruled option

- "real-load assertion fails on correct code under scheduler starvation": **ABSENT.** Executed (P3) zero-service input (first wake 3.001 s of a 3 s window) yields `periods=[]`, `claimed_s=0`; remaining real-load assertions all pass (P5/P7b evaluation above). Starvation can only make an upper bound easier to satisfy.
- "assertion keyed to a quantity starvation destroys": **ABSENT** in the real-load test (no lower bound on any scheduler-supplied quantity remains). The replacement test's lower bounds are keyed to `FakeClock`, which starvation cannot touch.

### Burden checks (packet Q1 (d))

Accepts all four inputs — 1.05 s late wakes and 2 s-late first scheduling (`:655`, passes), burn preempted 100x (`:669`, passes), zero-service (P3, no assertion touches it). Still kills `clock` (kernel ceiling, executed 3.195601 > .92; my P1 recomputation of the bound: `.14*3 + 0.5 = 0.92`, `3.0 <= 0.92` **False** -> fails -> killed, so the answer to the packet's probe question is **yes, the ceiling alone kills it, at 3.0 s and at 3.195601 s**) and `catchup-capped` (`:657` .30002 vs .1; per-period .25002 > .0501).

## Q2 — ruled: **(b), fix in this round**. `burn-noop` is a **real hole, not an equivalent mutant**.

Plain reason: this program's product is a *synthetic CPU load of a named profile*. `burn_profile` (`:751-767`) promises an LCG state advance and, for `--profile memory`, 16 MB of committed pages touched per iteration. A no-op burn still fills the period rows with the loop's own overhead, so every downstream number reports "0.1 cores of scalar load" while the machine actually ran an empty timing loop — and `--profile memory` silently becomes identical to `--profile scalar`, with no memory traffic at all. Different observable artifact, same tests passing: a hole.

Exact test text (no schema change, deterministic, ~4 lines):

```python
    def test_burn_profiles_advance_their_generator(self):
        for profile in ("scalar", "memory"):
            burn = harness.burn_profile(profile, 1)
            self.assertNotEqual(burn(1000), burn(1), f"{profile} burn did no work")
```

Executed (P4): real scalar `burn(1) = 1015568748`, `burn(1000) = 3200001012` -> distinguishable, test passes; `lambda count: seed` -> 1 vs 1, and the seat's `lambda count: None` -> None vs None -> **assertion fails, mutation killed**.

**Row-shape question, answered:** adding `work_units` to the period row **is a contract change** — period rows are published evidence, reduced into `rounds.jsonl`/`load.json` and covered by the journal-replay contract lane; do not take that route for this. The test-local assertion above changes no schema. Register as a lane (NOT this round) only the residual: a differential proving `--profile memory` actually writes its buffer.

## Q3 — **AFFIRMED**: record 11's `wake_late_s < .05` at `tests/...:679` for the preempted-burn regression; ruling 10's `< 1e-3` retained only for the late-start regression.

Executed (P2), `FakeClock.ratio = 100.0`, `duty_periods(.1, 3, .5, clock.burn, clock, start=0.0)`, 6 periods, sum CPU 0.0301:

```
wake_late_s = [0.005, 0.0, 0.0, 0.0, 0.01, 0.01]   max = 0.009999999999990461
all < 1e-3 -> False        all < .05 -> True
```

Ruling 10's `< 1e-3` is refuted by execution: it fails correct code by 10x. Executed (P6) late-start case (`clock.now = 2.0`): `wake_late_s = [0.0, 0.0]`, all `< 1e-3` True -> the stricter pin stands there. Optional, not required: the fake clock is pure arithmetic, so `.05` may be tightened to `<= .01 + 1e-9`; `.05` as ruled is sound and acceptance is not conditioned on tightening it.

## Named gaps

- Charter digest not independently verified: no separately supplied pin reached this refuter's brief.
- One permitted suite run; the (b)/(d) test texts ran as standalone probes against the same `37ca3c35` sources, not inside the suite.

## Commands run, with outcomes

1. `ls` packet dir + `cat 00-PACKET.md` — packet and 5 exhibits present.
2. `git show 37ca3c35:{scripts/sample_quiet_predicate_evidence.py,tests/test_sample_quiet_predicate_evidence.py} | sed -n ...` + `grep -n` — contract :771-778, `load_worker` :861-878, rendezvous :869, `burn_profile` :751, floor :640, ceiling :646, `STARTUP_CPU_S=0.5` :20, regressions :655/:669.
3. `grep -n -i 'alignment|noop|Mutation' exhibit-B-seat-06-report.md`; `sed -n '150,200p'` — mutation table, three real-load runs, F1/F2/F3.
4. `python -B /tmp/magistrate-d0b83820/opus-gate-scratch/probe.py` (P1-P5) — outputs quoted above.
5. `python -B /tmp/magistrate-d0b83820/opus-gate-scratch/probe2.py` (P6-P7) — outputs quoted above.
6. `git rev-parse HEAD` in `JouleWise-wt-harness-232` -> `37ca3c352077ed11050c7800663c45a6736eaa0b`; the one permitted suite run -> **Ran 43 tests in 4.753s, OK** (Exhibit B's green claim independently corroborated).

Writes: only `/tmp/magistrate-d0b83820/opus-gate-scratch/{harness.py,probe.py,probe2.py}` and this file. No git mutation, no canonical-root, custody, LaunchAgents or measurement-directory access.
