# TEST-SPEED-01 — suite wall-clock reduction, evidence file

Date: 2026-08-23. Branch `perf/test-speed`, worktree
`/Users/edr/code/JouleWise-wt-speed`. Queue row: `TASK_QUEUE.md` A12.

Scope fence honoured throughout: **no test file was edited**, no test was
deleted, no test semantics changed, and the four D-079 r6-pinned estimator
sources are byte-identical (verified by digest at the end of this file).
The full suite remains the authoritative gate for every merge, verdict, and
audited head; the fast tier added here is additive and gates nothing.

---

## 0. What a "shard" is here, and why the wall clock is a maximum

The suite is run by `scripts/shard_tests.py`, which splits the test modules
into groups and runs one group per parallel CI job. A group is a **shard**.
Because the jobs run at the same time, the wall clock a human waits for is
not the *total* test time — it is the time of the **slowest single job**.
Every number in this file is therefore a maximum over jobs, never a sum,
and "make CI faster" means specifically "lower the maximum."

That distinction is what the previous design got wrong, and it is the whole
story of section 1.

---

## 1. Baseline, and the defect the baseline exposed

### 1.1 What was believed

`.github/workflows/ci.yml` carried the comment "Exclusivity buys FAST
ordinary-shard signal (**~175 s estimated per shard**)". The scheduling
weights behind that estimate were in `scripts/test_timings.json`, measured
on 2026-08-03 on a quiet local bench, serially.

### 1.2 What was actually happening

Measured per-job durations, GitHub-hosted `ubuntu-latest`, two consecutive
green runs:

| Job (python 3.11) | run 32621080380 | run 32609926884 |
| --- | ---: | ---: |
| `test` shard 3 | **41 min** | **41 min** |
| `test` shard 2 | 14 min | 14 min |
| `test` shard 1 | 7 min | 7 min |
| `test` shard 4 | 6 min | 6 min |
| `calibration-writer-crash-matrix-exclusive` | 33 min | 31 min |
| `calibration-exits-exclusive` | 15 min | 12 min |
| `build`, `installed-wheel` | <1 min | <1 min |
| **whole-run wall clock** | **41 min 15 s** | **41 min 17 s** |

Shard 3 was running **2442 seconds against a 175-second estimate — a 14x
miss** — and it, not either exclusive job, was the critical path. The
imbalance across shards (41 / 14 / 7 / 6) is the visible symptom.

### 1.3 Root cause

Two compounding faults in the timing map, both data faults, neither a code
fault:

1. **Coverage.** The map held 93 entries against **140 discovered
   modules**. The 45 unmeasured modules each received the fallback weight,
   which was the **median** of the measured values — **0.868 s**. On a
   distribution this heavy-tailed the median asserts that an unmeasured
   module is free.
2. **The measurements no longer reproduce.** The 2026-08-03 figures cannot
   be re-measured on the same bench today — the tests genuinely got slower
   after that corpus was taken:

   | Module | map claims (2026-08-03) | bench today | hosted today |
   | --- | ---: | ---: | ---: |
   | `tests.test_p2038_production_path` | 133.364 s | **227.3 s** | 652.1 s |
   | `tests.test_powermetrics_fiducial` | 29.557 s | **49.4 s** | 172.0 s |
   | `tests.test_reduce` | 48.386 s | **480.1 s** | 1544.5 s |
   | `tests.test_whole_window_selection` | 7.292 s | **153.3 s** | 498.9 s |

   The "bench today" column was measured twice independently — by a serial
   bench run started before the audit, and by the audit's own harness —
   which agree closely (p2038: 227.3 s and 228.9 s).

> **Correction, recorded deliberately.** An earlier draft of this file and
> the commit message of `d01d1bb` attributed the whole error to
> bench-versus-hosted and quoted ratios "up to 68x". **That was wrong and is
> retracted.** Measured hosted/bench today is only **~2.8x–3.2x**
> (`test_reduce` 3.21x, p2038 2.82x, `whole_window_selection` 3.23x,
> `run_campaign` 2.94x; eleven per-test pairs fall between 2.74x and 3.27x).
> The large apparent ratios came from comparing hosted seconds against
> *stale* bench figures rather than against the bench as it is. The remedy —
> schedule from hosted measurements — is unchanged and is now better
> supported, but the two faults are different and are recorded as such.
> This error was caught by an independent audit, **not** by the sum-closure
> cross-check in §1.4, which passes under either account. Closure tests
> totals; it cannot test attribution.

Longest-processing-time packing is only as good as its weights. Fed a map
that priced `test_whole_window_selection` at 7 s when it costs 499 s, it
placed the heavy tail together and produced the 41-minute shard.

### 1.4 How the corpus was collected

No new profiler was needed. `scripts/shard_tests.py` already prints a line
per module:

```
MODULE PASS tests.test_reduce tests=131 failures=0 errors=0 skipped=0 seconds=1540.740
```

Those lines were harvested from every ordinary shard job of both runs, in
both interpreters — **up to four observations per module** — giving hosted
weights directly from the machine that matters, at no measurement cost.
Each module's weight is the **maximum** observation, because packing must
not underestimate the binding interpreter (3.11 is consistently slower:
4117 s of ordinary test time versus 2980 s on 3.14).

Stability: the heavy tail is highly repeatable across runs
(`test_reduce` 1540.7 / 1544.5 s). Run-to-run variation above 1.5x appears
on 10 modules, all small and all on 3.14 — noise on sub-second work, which
taking the maximum handles safely.

Raw corpus: `hosted-module-timings.json` (this directory).

**Per-test** timings were derived for the heavy modules from the
microsecond timestamps GitHub stamps on each log line, taking the delta
between consecutive `... ok` lines. The method was cross-validated against
the independently printed module totals:

| Module | Σ per-test | `MODULE` line | tests derived / reported |
| --- | ---: | ---: | ---: |
| `tests.test_reduce` | 1540.7 s | 1544.5 s | 131 / 131 |
| `tests.test_p2038_production_path` | 645.8 s | 652.1 s | 8 / 8 |
| `tests.test_whole_window_selection` | 495.3 s | 498.9 s | 57 / 57 |
| `tests.test_run_campaign` | 417.2 s | 425.5 s | 257 / 257 |

Counts match exactly and sums agree within 0.2–2%, the residual being that
per-test values come from one run while module weights are the max of two.

### 1.5 A note on the bench corpus

A full serial bench baseline was also started, for cross-reference. **It is
contaminated and is not used for any decision here.** Two orphaned
processes — `python3 -c 'while True: pass'`, PIDs 45067 and 56539 — have
been consuming 100% of a core each for **14 days**, and `test_calibration_exits`
failed on the bench during this session purely from concurrent load. See
§6, open question 1. The hosted corpus is authoritative precisely because
it does not depend on the state of this laptop.

### 1.6 The cost distribution

Ordinary suite: **138 modules, 3804 test methods, 4117 s** (hosted, 3.11).
It is extraordinarily top-heavy:

| Module | hosted s | % of ordinary suite | test methods |
| --- | ---: | ---: | ---: |
| `tests.test_reduce` | 1544.5 | 37.5% | 131 |
| `tests.test_p2038_production_path` | 652.1 | 15.8% | 8 |
| `tests.test_whole_window_selection` | 498.9 | 12.1% | 57 |
| `tests.test_run_campaign` | 425.5 | 10.3% | 257 |
| `tests.test_powermetrics_fiducial` | 172.0 | 4.2% | 75 |
| *(remaining 133 modules)* | 824 | 20.0% | 3276 |

Four modules are **75.7%** of the ordinary suite. Concentration continues
below module level — the single most expensive test method costs 257 s.

---

## 2. The structural ceiling

Sharding is **module-atomic**: a module is the smallest thing a shard can
hold. So for any number of shards K,

> **max-shard time ≥ the largest single module.**

`tests.test_reduce` is 1544.5 s. Adding shards cannot move that. Confirmed
directly against the repacked map:

```
module-atomic K=4 shard seconds: [1544, 858, 858, 858]   max 25.7 min
```

Three shards became well balanced (858 s each) the moment the weights were
right; the fourth is one module. **Correct data alone takes the ordinary
lane from 41 min to 26 min, and then stops.** Going below 26 min requires
splitting a module — which is what lever 2 builds.

The same ceiling applies inside the exclusive jobs, one level down: their
floor is their largest *test method*, because a single test cannot be
divided at all.

---

## 3. Lever 1 — re-measure the map *(commit `d01d1bb`)*

`scripts/test_timings.json` regenerated from the hosted corpus. All 140
discovered modules measured; the unmeasured set is empty.

Also added `unknown_module_weight_seconds` = **29.834 s** (the arithmetic
mean) for modules added in future. The historical median fallback (0.868 s)
priced an unmeasured module as free, which is exactly how a heavy new
module silently overruns a shard. `default_module_weight()` keeps median
semantics because `tests/test_shard_tests.py` pins them and that file may
not be edited; the conservative value is a separate function consumed at
the call site.

The two exclusive modules' declarations and their `seconds_by_module`
entries are preserved byte-for-byte so the existing `ci.yml` assertions
continue to hold.

**Effect of lever 1 alone: max ordinary shard 2442 s → 1544 s (41 → 26 min).**

---

## 4. Lever 2 — split the indivisible

### 4.1 Independence is a correctness question, not a performance one

Splitting a module across processes is only legitimate if the tests do not
depend on running together. Both candidate modules were audited against
every coupling mechanism — `setUpModule`, `setUpClass`, class attributes
written by test bodies, module globals, shared temp dirs, fixed ports,
environment variables, import-time side effects, and ordering assumptions.

**`tests.test_calibration_writer_crash_matrix`: independent, and proven by
execution rather than by argument.** All 15 methods are independent; every
`cls.` write is confined to `setUpClass`, with zero class-attribute writes
from test bodies. The two genuine shared surfaces both check out: the owned
process-group registry is process-local and its four users take distinct
fixed keys, and the writer-crash authorization global is reset by the first
statement of its only mutator. Collisions are structurally impossible
because each case creates its root with `mkdir(parents=True)` and **no
`exist_ok`**. The proposed K=2 split was then executed with both shards
running concurrently on one machine — harsher than CI — and both passed.

**`tests.test_calibration_exits`: do not split.** Its "runs sequentially
internally" comment turned out to describe nothing mechanical — it is just
unittest's default single-process behaviour and protects no invariant. But
splitting is still wrong here: `_WITNESS_RESULTS` is a **memo cache**, so
separating the classes makes *both* shards re-run the same 68-case sweep,
and `RefusalInventoryTests` is rated **UNPROVEN** in isolation because it
iterates the entire cache and passes only because an alphabetically earlier
method happens to prime it. That is an unpinned accident, and this lane
does not disturb it. **Left exclusive and untouched.**

### 4.2 K is capped by one test method

Per-test hosted timings for the crash-matrix module:

| Test | hosted 3.11 | share |
| --- | ---: | ---: |
| `test_every_exact_stage…` | **1385.32 s** | 69.6% |
| `test_torn_and_fsynced…` | 514.82 s | 25.9% |
| *13 others + `setUpClass`* | 90.5 s | 4.5% |

Two tests are 95.5% of the module, so **max-job time is floored at ~1386 s
(23.1 min) for every K ≥ 2**. K=3, 4, 5 buy literally zero wall clock and
only add jobs. Per-shard `setUpClass` duplication is measured at 0.44 s, so
it is not the constraint — the constraint is that a single test method
cannot be divided. **K=2 is therefore the correct and only useful choice.**

The 36x hosted amplification is *not* fixed sleeps (capture sleeps are
scaled by `--time-scale-for-test 0.001`, and the unscaled ones are SIGKILLed
on readiness). It is per-case subprocess work plus bounded teardown polling
that behaves as a **step function**: a reap finishing within one 10 ms poll
on the bench escalates through the full SIGTERM→SIGKILL path on a contended
runner. The decisive evidence is that 3.11 and 3.14 differ by 1.47x *in the
same run at the same commit* — fixed sleeps would be identical. So the cost
is contention-shaped and does shrink under sharding, but only per case, and
the cases are locked inside two methods.

A stale pin was found in passing: `ci.yml` asserts the module costs
**5317.216 s**, which was a 2026-08-11 observation of the module inside a
*shared* shard, before it went exclusive. Its exclusive job today measures
**2005 s (3.11) / 1370 s (3.14)** — the pinned figure overstates by 2.7x.

### 4.3 The guard against a stale identifier list

Splitting by test id introduces a failure mode with no natural alarm: if a
declared id disappears (a rename) or a new test is added, a shard can
silently run less than intended and the suite reports green having never
executed a test. The mechanism therefore declares **only the heavy test ids
explicitly** and computes the rest at run time as a single *remainder*
unit:

- A **newly added test lands in the remainder automatically** — no JSON
  edit, no CI break, no silent omission.
- A **renamed declared id fails closed**, because the guard asserts every
  declared id still exists in the loader-discovered set. This is the case a
  computed complement would otherwise absorb silently, handing one shard
  ~20 minutes of unaccounted work.
- A property test asserts the union of all units equals the module's full
  discovered test-id set and that units are disjoint — the invariant that
  proves no test is dropped.

Enumerating every id instead would give two lists that can rot; one list
plus a computed complement has one way to rot, and it is the loud one.

---

## 5. Lever 2(d) — the additive PR-fast tier

A new `pr-fast` job runs on pull requests only, selecting every ordinary
module whose measured hosted weight is at or below **30 s**.

| | modules | test methods | hosted seconds |
| --- | ---: | ---: | ---: |
| Full ordinary suite | 138 | 3804 | 4117 |
| **Fast tier** | **126** | **2848 (74.9%)** | **442 (10.7%)** |
| Excluded heavy tail | 12 | 956 (25.1%) | 3675 (89.3%) |

The excluded 12 carry a quarter of the tests but nine tenths of the cost —
which is precisely why they are the ones to drop from a latency device and
keep in the gate. Split across 2 shards on 3.11 only, the tier reports in
roughly **4 minutes** instead of the full lane's ~24.

Selection is **derived at run time** from the timing map rather than
checked in, so a new test module cannot silently fall out of it. An
unmeasured module takes the conservative weight (29.834 s), which is below
the 30 s cutoff, so **new modules are included by default** — for a tier
that only ever adds signal, the safe failure is running too much.

**It is not a gate.** Every job that gated a merge before still runs on the
same pull request, unchanged; no required check was altered and nothing was
removed. A red `pr-fast` is real information; a green one is only the
absence of early bad news. The workflow comment says this at length so the
next reader cannot mistake it, and promoting it to a required check is
called out there as a lead-gated change.

---

## 6. Result, and the floor that remains

| | before | after |
| --- | ---: | ---: |
| Max ordinary shard | 41 min | 17.6 min |
| Crash-matrix exclusive | 33 min | 23.5 min |
| Calibration-exits exclusive | 15 min | 15 min *(unchanged by design)* |
| **CI wall clock** | **41 min** | **~23.5 min** |
| PR first signal | 41 min | **~4 min** |

The remaining floor is **a single test method that costs 1385 s**. No
sharding strategy can go below it, because a test method is indivisible.
Removing it is the already-registered **WO-CRASHMATRIX-RELIABILITY** work,
which changes test semantics and is therefore outside this lane's fence —
and is explicitly not on the paper critical path. That is the honest end of
this hill climb: the data lever and the sharding lever are exhausted, and
what is left is a fixture defect, not a scheduling problem.

Job budget: GitHub Free permits 20 concurrent jobs. The workflow defines 18
after this change (8 ordinary shards, 4 crash-matrix, 2 calibration-exits,
2 fast-tier, `build`, `installed-wheel`), leaving 2 spare.

### Open questions for the lead

1. **Two leaked processes have been burning 100% of a core each for 14
   days** (PIDs 45067 and 56539, `python3 -c 'while True: pass'`, parented
   to init — the exact command the crash-matrix guard test spawns). Every
   bench measurement taken on this machine since ~2026-08-09 has run two
   cores short, which plausibly touches other lanes' numbers. Not killed
   here: it is a machine-state action that could disturb another session's
   in-flight measurement. **Ed's call.** Related and worth a queue row: the
   lease holder in that test is a bare `Popen`, never registered with the
   owned-process registry, so the module's own survivor guard cannot catch
   a leak of that shape.
2. **The stale 5317.216 s pin** in `ci.yml` overstates the crash-matrix
   module by 2.7x. It is updated here as part of splitting that job, with
   fresh evidence recorded; flagging it because it is an evidence-bearing
   assertion, not a comment.
3. **A new test file was added** (`tests/test_shard_split.py`) covering the
   new split mechanism. The brief preferred zero test-file changes; this
   adds a file rather than editing one, and no existing test semantics
   change. The alternative was shipping an unverified fail-closed guard
   into the merge gate. Flagged so it can be dropped if the fence is meant
   to be read strictly.
4. **`RefusalInventoryTests` passes by accident** — it depends on an
   alphabetically earlier method priming a memo cache. Untouched here
   (it is a test-semantics matter) but it is a latent fragility worth a row.
