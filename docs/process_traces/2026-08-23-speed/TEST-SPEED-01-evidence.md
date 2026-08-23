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
microsecond timestamps GitHub stamps on each log line. This required a
correction worth recording, because it is a trap for anyone repeating the
method.

`unittest -v` writes a test's description when the test **starts** and its
outcome word when it **ends**. For an *undocstrung* test the description is
one line, `name (id) ... ok`, and the line is therefore stamped at the
test's END. For a *docstrung* test the description spans two lines — a bare
`name (id)` stamped at START, then `<docstring> ... ok` stamped at END.
Naively differencing consecutive outcome lines therefore attaches the right
*durations* to the **wrong tests** wherever docstrung and undocstrung tests
are interleaved.

> The first pass of this analysis made exactly that error, and reported a
> 252.9 s test that does not exist — it was two adjacent tests (218.2 s and
> 34.7 s) summed. **The sum-closure check below did not catch it**, and
> could not: closure tests totals, and a misattribution preserves the
> total. It was caught by an independent audit. Corrected per-test values
> use the docstring-aware rule.

| Module | Σ per-test | `MODULE` line | tests derived / reported |
| --- | ---: | ---: | ---: |
| `tests.test_reduce` | 1540.7 s | 1544.5 s | 131 / 131 |
| `tests.test_p2038_production_path` | 645.8 s | 652.1 s | 8 / 8 |
| `tests.test_whole_window_selection` | 495.3 s | 498.9 s | 57 / 57 |

Counts match exactly and sums agree within 0.2–2%, the residual being that
per-test values come from one run while module weights are the max of two.

Because attribution proved to be the fragile part, **only per-test values
confirmed by two independent methods** — docstring-aware log parsing *and*
a direct bench harness — are used as scheduling weights. Where the two
methods disagreed (two ~87 s tests in `test_reduce`), the tests are left in
the computed remainder rather than declared under a disputed identity. This
costs nothing: see §4.3.

### 1.5 A note on the bench corpus

A full serial bench baseline was run for cross-reference: 140 modules,
2931 s, completing after the hosted corpus was already in use. It is the
source of the "bench today" column in §1.3, and it independently reproduces
the audit's amplification figures from a separate process:

| Module | this bench run | audit's harness | hosted | ratio |
| --- | ---: | ---: | ---: | ---: |
| `tests.test_reduce` | 481.9 s | 480.1 s | 1544.5 s | 3.20x |
| `tests.test_p2038_production_path` | 227.3 s | 228.9 s | 652.1 s | 2.87x |
| `tests.test_whole_window_selection` | 148.6 s | 153.3 s | 498.9 s | 3.36x |
| `tests.test_run_campaign` | 149.3 s | 143.6 s | 425.5 s | 2.85x |

Two independent measurements agreeing to within a few percent are what
retire the "68x" claim in §1.3.

**The bench is nonetheless contaminated and no scheduling decision rests on
it.** Two orphaned
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

The guard is exercised against the **real checked-in map** by
`tests/test_shard_split.py`, not only against fixtures — so a renamed
declared id fails the merge gate the moment it lands, rather than whenever
someone next happens to run `--split`.

### 4.4 What actually shipped, and why so little of `test_reduce` is declared

Only **three** test ids are declared for `tests.test_reduce`, leaving 128
tests in the remainder. That is deliberate on three grounds:

1. **It is sufficient.** The remainder is 1002.6 s, already below the
   1029 s even-four-way share, so the partition reaches its optimum. The
   measured plan is `1036.7 / 1036.7 / 1036.7 / 1036.7` — balanced to
   0.001 s.
2. **It avoids the disputed attributions.** The three declared ids are the
   ones both measurement methods agree on. Naming the contested ~87 s tests
   would buy no wall clock while risking a weight pinned to the wrong test.
3. **Splitting is not free.** Each process that touches `test_reduce`
   re-fills two module-level memo caches (~17 s and ~14 s hosted). Carving
   out many units would pay that repeatedly — measured elsewhere as 153.6 s
   becoming 212.8 s when a class was fully separated. Three units is the
   knee.

Note the consequence, since it bounds future work: because the remainder is
itself an atomic unit, adding shards beyond ~5 buys **nothing** for the
ordinary lane until more of `test_reduce` is declared. The lane's floor is
now 1002.6 s.

### 4.5 Backward compatibility

Proven rather than asserted: every function on the module-atomic path is
byte-identical to the previous HEAD; partitions match HEAD exactly at shard
counts 1, 2, 3, 4, 5, 8 and 16; `main()` is unchanged unless the new opt-in
`--split` flag is passed; `tests/test_shard_tests.py` passes untouched; and
**20 of 20 seeded mutants were killed**, including
remainder-resolves-to-nothing, remainder-re-includes-declared, and
vanished-id-silently-dropped.

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

All figures below are measured or planned against this tree; the plan rows
come from extracting and executing all six python blocks embedded in
`ci.yml`.

| | before | after |
| --- | ---: | ---: |
| Max ordinary shard | 41 min (2442 s) | **17.6 min** (1036.7 s ×4, balanced) |
| Crash-matrix exclusive | 33 min (2005 s) | **23.5 min** (1385.3 / 605.3 s) |
| Calibration-exits exclusive | 15 min | 15 min *(unchanged by design)* |
| **CI wall clock** | **41 min** | **~23.5 min** |
| PR first signal | 41 min | **~4 min** (236.1 s ×2) |

Job budget: GitHub Free permits 20 concurrent jobs. The workflow defines 18
after this change (8 ordinary shards, 4 crash-matrix, 2 calibration-exits,
2 fast-tier, `build`, `installed-wheel`), leaving 2 spare.

The remaining floor is **a single test method that costs 1385 s**. No
sharding strategy can go below it, because a test method is indivisible.
The scheduling levers are now exhausted — which is exactly why §7 matters
more than anything in this file.

### 6.1 Exactly which CI check names change

Adding a shard dimension to a matrix **renames** its jobs, so this is
recorded explicitly rather than left to be discovered.

| Check name | change |
| --- | --- |
| `test (3.11, 1..4)`, `test (3.14, 1..4)` | **unchanged** (same matrix dimensions) |
| `calibration-exits-exclusive (3.11 / 3.14)` | **unchanged** |
| `build`, `installed-wheel` | **unchanged** |
| `calibration-writer-crash-matrix-exclusive (3.11)` | **renamed** → `(3.11, 1)` and `(3.11, 2)` |
| `calibration-writer-crash-matrix-exclusive (3.14)` | **renamed** → `(3.14, 1)` and `(3.14, 2)` |
| `pr-fast (1)`, `pr-fast (2)` | **new**, additive, pull-request only |

**No required status check is broken, because this repository configures
none.** Verified 2026-08-23: `repos/:owner/:repo/branches/main/protection`
returns *"Branch not protected"* (404) and `repos/:owner/:repo/rulesets`
returns `[]`. Merge gating is by convention and lead review, not by GitHub
branch protection.

That is why the rename was applied rather than proposed. **If branch
protection is ever introduced, the two renamed crash-matrix checks are the
ones to re-register**, and promoting `pr-fast` to required would be a
separate, lead-gated decision that §5 argues against.

One further behavioural change in that job: `fail-fast: false` is now set,
so a failure on one interpreter or shard no longer cancels its siblings.
That trades a little runner time for complete failure information, which is
the right side of the trade for a module whose failures are load-dependent.

---

## 7. The finding worth more than everything above — NOT APPLIED

The audit of `tests.test_reduce` found a **legitimate, semantics-preserving
speedup of 6.2x**, and this lane deliberately did not take it.

### The defect

`tests/test_reduce.py:65` defines the `self_consistent_calibration`
fixture, which costs **5.25 s on the bench and ~17 s hosted per cold
call**. It is pure CPU — no subprocess, no sleep: it builds a 1.02 MB
synthetic plist, re-parses it, then runs pulse detection (13.7M overlap
calls) and an exact-`Fraction` clock-anchor solve.

It is memoised at `tests/test_reduce.py:77-84`. **The memo is keyed on
whether the caller passed `None`, not on the argument values.** Its main
consumer `_bundle_with_calibration` (`:2910`, **37 call sites**) always
passes an explicit `float(capture_wall_time_s) - 1.95` (`:2947`) — which is
*exactly* the default value, since
`(1784490850.05 + 1.95) - 1.95 == 1784490850.05` in IEEE-754. So the
argument is always the default, is never `None`, and **the cache therefore
misses on every single call** while producing byte-identical output.

Five test modules import this fixture, including
`tests/test_calibration_exits.py` — the other exclusive job.

### The fix, and its measured effect

Key the memo on resolved argument values. Demonstrated by wrapping the
module attribute at run time, with **no file edited**:

```
AS-IS         70.22 s   run=3 ok=True fail=0 err=0
VALUE-KEYED   11.26 s   run=3 ok=True fail=0 err=0
outcome identical: True     speedup: 6.2x
```

No assertion weakened, no iteration count reduced, no case skipped, no
production code path touched — it changes a *test helper's cache key*.

### Why this lane did not apply it

It edits a test file, and TEST-SPEED-01 is fenced against that. **Proposed,
not applied**, per the instruction to propose rather than apply when in
doubt. It is recorded here so the decision is the lead's.

### Why it is worth more than the sharding

Sharding divides work across machines; this removes the work. It attacks
the cost directly and, unlike sharding, it is **not** bounded by the
indivisible-test floor:

- `tests.test_reduce` is 1544.5 s and 37.5% of the ordinary suite.
- The fixture is imported by five modules, `test_calibration_exits`
  (a 15-min exclusive job) among them.
- The crash-matrix module belongs to the same declared
  "CPU-amplifying-fixture" class.

If the effect carries at anything near the measured 6.2x, it plausibly
reaches the **real** critical path — the 1385 s test that §6 identifies as
the hard floor — in a way that no amount of scheduling can. The scheduling
work in this file buys 41 → 23.5 min and then stops; this is the lever that
could go further.

Suggested home: it is the same defect class as the registered
**WO-CRASHMATRIX-RELIABILITY** and **WO-CALEXITS-RELIABILITY** rows.

### What was checked and rejected as *not* legitimate

Recorded so the line is visible: passing the production physics cache into
the D078R01 tests (a cache hit sets `fresh = None` at
`joulewise/reduce.py:1535-1536`, skipping the containment gate those tests
exist to prove); trimming the 70-iteration boundary sweep; removing the
real `time.sleep` at `test_p2038_production_path.py:254` (the child needs
wall time to exit); bytecode warming (`ci.yml` already runs `compileall`);
and `-O` flags. None of these are available.

Note also that `joulewise/reduce.py` is one of the four **D-079 r6-pinned**
estimator sources, so a library-side fix to `test_reduce`'s cost is
categorically unavailable — it would force an r7 reissue. That is precisely
why the runner-side split was the only lever inside the fence, and why the
test-helper memo key is the only cheap one outside it.

### Open questions for the lead

0. **Take the memo-key fix?** §7. A measured **6.2x** on the single most
   expensive module, semantics-preserving, ~10 lines, blocked only by this
   lane's no-test-file-edits fence. It is the highest-value item on this
   page by a wide margin and the only one that can reach past the
   indivisible-test floor. Proposed, not applied.

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
