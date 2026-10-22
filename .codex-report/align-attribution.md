# Alignment attribution lane — fix round 2, continuation fix2c

## SUMMARY

- Continued the pushed lane from 19a9bdf2a9bb2abfe50afdd07ba8c939f5e9811e; production attribution code is unchanged in fix2c.
- Restored expectedFailure only for the counter-world coverage test: C2 covers 498/505 segments and 5/5 totals, measured by the lead at 19a9bdf2a.
- Kept its exact 100% coverage assertion and the structural/conservation checks outside expectedFailure.
- INA3221, NVML power and powermetrics each cover 505/505 lane-world segments and 5/5 totals, measured by the lead at 19a9bdf2a.
- On the reviewer worlds C2 reaches exactly the requested counts: 635/635 INA3221, 1988/2134 NVML power, 1983/1987 powermetrics and 2193/2198 counters.
- Recorded C2's cost: reviewer NVML median episode-total half-width 2.39e3 J versus median error 39.5 J; lane totals widen from about 0.28 J to 598–645 J.
- Recorded the counter-edge fixes, cold-query speedup, same-sign tool bias for A7 and all reported twin comparison categories/deltas.
- Nothing ran in this seat: the runtime stayed offline; numerical evidence is explicitly measured by the lead at 19a9bdf2a, reviewer-measured at e3db70aeb, or derived.
- Committed only the counter test disposition and this report through the lane branch; C2 and the partial-coverage reading still await the lead's ruling.

## FILES

- `joulewise/align/attribution.py`: existing integration, C2 sensitivities, physical counter-drop classification, lazy point spans and latest-trace preparation cache; unchanged in fix2c.
- `tests/align/test_attribution.py`: existing closed-form C2, counter and cold-query regressions; unchanged in fix2c.
- `tests/align/test_attribution_worlds.py`: existing twenty-turn worlds, three-reading statistics, signed tool bias and public/eager agreement checks; fix2c adds the counter expectedFailure decorator and sourced coverage docstring.
- `.codex-report/align-attribution.md`: this report and retained finding history.
- Fix2c writes only the last two paths. No registry, workflow, inventory, shared contract or `tests/test_shard_tests.py` change.
- The VM could not receive the uncommitted twin or .review2 files. The lead's runs used a git archive of 19a9bdf2a, the twin files at 43e9ffed1 and the verbatim appendix probes. No twin/probe files are committed.

## PUBLIC API
```python
@dataclass(frozen=True)
class EnergyEstimate:
    joules: float
    half_width_j: float
    method: str
    flags: tuple[str, ...]

def trace_energy(trace: PowerTrace, t0_ns: int, t1_ns: int, *,
                 mapping: ClockMapping | None = None,
                 idle_watts: float = 0.0) -> EnergyEstimate: ...

@dataclass(frozen=True)
class SegmentEnergy:
    turn: int | None
    kind: str
    start_ns: int
    end_ns: int
    energy: EnergyEstimate

@dataclass(frozen=True)
class EpisodeAttribution:
    episode_id: str
    channel: str
    total: EnergyEstimate
    segments: tuple[SegmentEnergy, ...]
    flags: tuple[str, ...]

def attribute_episode(episode: Episode, *, source: str, channel: str,
                      idle_watts: float = 0.0) -> EpisodeAttribution: ...
```

## TESTS RUN

**Nothing ran in this continuation seat.** An environment wait and repeated
retries did not produce a usable executor. Runtime status reported starting,
offline and failure=null. Each shell request below failed before starting any
process with:
`No usable execution environment is available. Wait for an environment to become available before using this tool.`

Exact attempted commands, with cwd `/workspace/JouleWise`:

```bash
python3 --version
python3 -m unittest discover -s tests/align -t .
python3 -P -m unittest discover -s tests/align -t . -p 'test_attribution*.py'
python3 -P -m unittest discover -s tests/align -t . -p test_twin_attribution.py
python3 -P /workspace/JouleWise/.review2/r2_truth.py /workspace/JouleWise 12
python3 -P /workspace/JouleWise/.review2/r2_edges.py /workspace/JouleWise
```

The following evidence is **measured by the lead at 19a9bdf2a**, on macOS,
Python 3.13.1, with the archive/twin/probe setup described above. It is not
a run by this seat or a final-head passing claim.

| Exact command (from the archive root) | Lead result |
|---|---|
| `python3 -P -m unittest discover -s tests/align -t . -p 'test_attribution*.py'` | Ran 69 tests; FAILED (failures=1). Only failure: counter-world 498/505 own-half-width coverage; totals 5/5. No dependency skip or expected failure was reported. |
| `python3 -P .review2/r2_truth.py /workspace/JouleWise 12` | Completed; sensor counts and numerical output below. INA3221 uses 4 seeds, the other sensors 12 each. This is a probe, not a unittest count. |
| `python3 -P .review2/r2_edges.py /workspace/JouleWise` | Completed; counter, coverage and runtime results below. This is a probe, not a unittest count. |
| `python3 -P -m unittest discover -s tests/align -t . -p test_twin_attribution.py` | Ran 5 tests; FAILED (failures=66 subtests), all half-width comparisons in full-coverage worlds. No skip was reported. |

Fix2c adds expectedFailure to that one counter test. The resulting disposition
would be 69 tests with one expected failure if the same numerical outcomes
repeat; that is a deduction, **not a measured post-fix test run**. Structural,
tiling, conservation and tool-clearance checks still run outside that decorator.

No full-align discovery result for 19a9bdf2a was supplied by the lead.
The all-align command above could not start here. Historical baseline only:
**reviewer-measured at e3db70aeb**, 62 lane tests ran successfully, including
two expected failures. Do not treat that baseline as verification of this head.

No extras were installed. Production code and authored lane tests are
stdlib-only, so no extra-dependent test run applies. No network or hardware
test ran. The quick-tier discovery-namespace failure remains outside scope;
`tests/test_shard_tests.py` was not changed.

## END-TO-END

The lane's tested chain (lead run) is independent rectangular true power ->
point, trailing-window or cumulative-counter sampling -> bounded analogue
noise and quantization -> PowerTrace/ClockMapping -> twenty-turn Episode ->
JSON round trip -> attribute_episode -> exact tiling, conservation, tool
contrast and own-half-width coverage. Public interval queries are compared
with episode preparation and the former eager span/start representation over
each segment and total on the same five seeds.

Fixture choices: twenty turns, twenty tools of 0.2–30 s, 101 segments per
episode; 100 ms NVML polling with 25 ms duty, 1 ms INA3221 point sampling,
100 ms whole-window powermetrics and 100 ms cumulative-counter polling with
one restart inside the longest tool. Existing quanta are physical:
integer mW = .001 W, integer mJ = .001 J, and INA3221
40 uV / 5 mOhm * 5 V = .04 W. Existing clock half-widths derive from
the synthetic brackets: .5 ms INA3221, 1 ms powermetrics; host-clock NVML
power has no mapping. Load variation, grid phase, jitter and workload levels
remain explicit fixture parameters.

Lane coverage below is **measured by the lead at 19a9bdf2a**. Earlier
readings are algebraic replays on the same observations:
round1 = current C2 width - window sensitivities - half the full endpoint
difference; C1 = current C2 width - window sensitivities. They isolate width
readings, retaining the current counter-drop handling.

| Lane sensor (5 seeds each) | Round1 segments; totals | C1 segments; totals | C2 segments; totals | Maximum segment error |
|---|---|---|---|---:|
| INA3221 | 505/505; 5/5 | 505/505; 5/5 | 505/505; 5/5 | .0128 J |
| NVML power | 228/505; 0/5 | 409/505; 0/5 | 505/505; 5/5 | 15.51 J |
| powermetrics | 131/505; 5/5 | 201/505; 5/5 | 505/505; 5/5 | 1.54 J |
| NVML counter | 347/505; 5/5 | 498/505; 5/5 | 498/505; 5/5 | 13.008 J |

Lane episode-total half-widths (same lead run):
NVML power round1 .276–.292 J versus C2 598.1–645.0 J;
powermetrics .292–.308 J under every reading; counter round1 36.8–39.1 J
versus C2 40.7–44.7 J. The NVML increase is about 598–645 J.
For counters the lower range endpoint increases by 3.9 J and the upper
by 5.6 J (derived from the rounded endpoints, without claiming paired-seed
deltas). INA3221 coverage stays unchanged.
No estimator joules change under the width replay.

The independent reviewer worlds use 24–36 turns, 0–3 tools after each
model call, phase power ripple and NVML counter resets. Historical
round1/C1 counts below are **reviewer-measured at e3db70aeb**; implemented
C2 counts are **measured by the lead at 19a9bdf2a**.

| Reviewer sensor | Round1 segments; totals | Isolated C1 segments; totals | Implemented C2 segments; totals |
|---|---|---|---|
| INA3221 (4 seeds) | 635/635; 4/4 (derived total) | 635/635; 4/4 (derived total) | 635/635; 4/4 |
| NVML power (12 seeds) | 816/2134; 0/12 | — (see provenance note) | 1988/2134; 12/12 |
| powermetrics (12 seeds) | 866/1987; 12/12 | — (see provenance note) | 1983/1987; 12/12 |
| NVML counter (12 seeds) | 1940/2198; 12/12 | 2193/2198; 12/12 | 2193/2198; 12/12 |

Provenance note: the supplied e3db70aeb review does not give isolated C1
counts for NVML power or powermetrics. INA3221 round1/C1 totals 4/4 follow
from the lead's maximum absolute total error .025 J and the original
resolution budget alone (positive .04 W times a multi-minute episode);
this is **derived**, not an additional old-head probe run. The post-C2
probe's C1/C2 columns below add terms a second time and cannot fill the
two isolated-C1 cells. No values are invented for those cells.

Here is the full set of coverage readings actually printed by the supplied
post-C2 probe, **measured by the lead at 19a9bdf2a**. Only “own C2” is the
implementation's coverage. “Own C2 + old endpoint” and the last column
correspond to the script's now-double-added C1 and C2 columns.

| Reviewer sensor | Own C2 segments; totals | Own C2 + old endpoint segments; totals | Own C2 + old endpoint + window segments; totals |
|---|---|---|---|
| INA3221 | 635/635; 4/4 | 635/635; 4/4 | 635/635; 4/4 |
| NVML power | 1988/2134; 12/12 | 1994/2134; 12/12 | 2014/2134; 12/12 |
| powermetrics | 1983/1987; 12/12 | 1985/1987; 12/12 | 1987/1987; 12/12 |
| NVML counter | 2193/2198; 12/12 | 2198/2198; 12/12 | 2198/2198; 12/12 |

Reviewer-world C2 deltas from round1 are therefore **derived from the
sourced counts**: INA3221 +0 covered segments, NVML power +1172 and
+12 covered totals, powermetrics +1117 segments, counters +253 segments.
All are exactly the reviewer's requested C2 target counts.

Other reviewer-world output, **measured by the lead at 19a9bdf2a**:

| Sensor | Segments >=1 s inside | Tools inside | Worst error/width | Total absolute error median / max (J) | Median total half-width (J) | Max relative conservation residual |
|---|---|---|---:|---:|---:|---:|
| INA3221 | 247/247 | 158/158 | .0939 | .0105 / .025 | 24.4 | 0.0 |
| NVML power | 851/851 | 507/509 | 216 | 39.5 / 125 | 2.39e3 | 1.6e-16 |
| powermetrics | 772/772 | 470/470 | 1.52 | .00617 / .168 | 1.05 | 1.5e-16 |
| NVML counter | 853/858 | 532/535 | 1.24 | .0415 / 14.1 | 9.65 | 1.2e-16 |

The NVML median total width moved from .82 J
(**reviewer-measured at e3db70aeb**) to 2.39e3 J (lead at 19a9bdf2a),
an increase of approximately 2.39e3 J, derived at the coarser printed
precision. The median total error remains 39.5 J, maximum 125 J.
The supplied evidence does not give old median widths for the other sensors;
the seed-0 twin width comparisons in OPEN ISSUES give concrete deltas
without presenting them as old-lane medians.

Other lane chain output, **measured by the lead at 19a9bdf2a**:
the midpoint-reset world returns 45554.76 J against truth 45559.33 J,
half-width 44.75 J; the preceding partial interval has half-width 313.37 J
(the lead output's “before” field names that earlier interval, not a
pre-C2 episode-total width). Runner post-model tools remain twenty each:
NVML power 14582.35 J against truth 14542.26 J;
INA3221 807.918 J against truth 807.903 J.

The invisible-burst control is unchanged: **derived**
400 W * .050 s = 20 J unseen excess inside a 75 ms duty gap versus
.001 W * .1 s = .0001 J nominal width for identical means. C2 adds zero
when observed means are identical. Its success is a control demonstrating
the limit, not a certificate for invisible work.

Counter edges, **measured by the lead at 19a9bdf2a**, compared with the
**reviewer-measured at e3db70aeb** outputs (deltas derived by subtraction):

| Case | Current joules / half-width (J) | Change in joules / half-width (J) | Current flag |
|---|---:|---:|---|
| Steady | 1200.0 / .002 | 0 / 0 | no reset |
| Stuck | 0.0 / .002 | 0 / 0 | no reset |
| Reset at first step | 1170.0 / 30.002 | -60 / -30 | counter.decrease |
| Two resets | 1200.0 / 90.002 | 0 / 0 | counter.reset |
| 1 mJ non-reset dip | 1200.001 / 60.003 | about -5000570.0 / -5000509.998 | counter.decrease |

The last deltas use the printed old 5001770.0 J and 5000570.001 J;
the joules delta is rounded to the old reading's .1 J printed precision.
The dip now covers 1200 J truth without a megajoule-scale width.
**Derived physics:** ignoring one 30 J poll is offset by the following
60.001 J recovery; 1200 - 30 + 30.001 = 1200.001 J. That recovery is a
non-reset 600.01 W step; the ignored dip itself does not set the peak.
One .1 s poll at that observed peak plus two .001 J quanta gives 60.003 J.
The first-drop reading 60 J exceeds .1 s * 300 W = 30 J, so it counts
zero; 39 * 30 J = 1170 J with a 30 J poll allowance still covers truth.
The two-resets fixture includes three drops including its first step;
all fit the physical limit, retaining the 90 J sensitivity.

Cold runtime, **measured by the lead at 19a9bdf2a**:
one 10 s query on a one-hour 1 kHz trace (3.6 M samples) takes .06 s,
twin .003 s, with equal joules. The lead's before value is 3.58 s;
the original reviewer separately measured 3.52 s at e3db70aeb.
This is cold-span construction plus a latest-trace/mapping cache,
not a cache-only speedup. The lane's public/prepared/eager numerical
agreement regression had no reported
failure in the lead's 69-test run; it checks joules and widths using
1e-6 relative capped at 1% of the smaller width and a million-ulp floor.

## DECISIONS I MADE

- Continue from the pushed 19a9bdf2a head. With no usable VM, use the
  connected GitHub file/commit tools on this lane only, preserving ancestry.
  No force push, main write, local checkout or uncommitted local setup is
  claimed.
- Read the existing report first, then PIPELINE.md, records.py and
  interfaces.py. Also inspect root AGENTS.md, Mission M0, orchestration,
  phase_share.py and reduce._integrate. The active stop card is NONE.
  The delegated WRITE_SCOPE overrides other generated-state bookkeeping.
- Fix2c changes no production code: the lead's reviewer-world own-width
  counts exactly match the prescribed C2 targets. Its only test edit
  restores expectedFailure for the remaining 498/505 counter coverage,
  with a measured-by-lead docstring; the 100% assertion stays intact.
  The three fully covering lane sensors remain ordinary tests.
- Retain C2, explicitly requested by FIX ROUND 2, under NEEDS_RULING:
  C1 uses the full endpoint hold/linear difference; C2 additionally uses
  abs(neighbour mean jump) * overlapping gap seconds / 2 and
  range(three neighbouring means) * window seconds / 4 at each strict
  interior window cut. Each derivation assumes at most one step per
  partial interval, duty gap or averaging window and is stated in code.
- C2 is observed-variation sensitivity, with the same invisible-burst
  limitation and window.edge_allocation_unresolved flag. Its reviewer
  NVML coverage is 1988/2134, not full coverage; its episode-total cost
  is explicitly part of the ruling.
- Retain the physical counter test: establish the nondecreasing-step
  peak before classifying drops; a new reading above poll seconds *
  observed peak counts zero with counter.decrease and contributes no
  peak. Plausible resets count from zero. Both add overlapping-poll
  sensitivity. No non-reset step means no observed peak: flag
  counter.peak_missing and use infinite uncertainty on affected
  intervals/partial coverage. A flat step establishes observed 0 W;
  a dead sensor still cannot certify unseen work.
- Retain lazy requested point spans plus one latest-trace/mapping
  preparation cache keyed by trace identity/mapping equality.
  Cold calls retain the O(n) finite-value validation but construct O(q)
  queried spans; cached point queries use O(log n + q) work.
  Missing-coverage peak calculation remains lazy. The numerical agreement
  regression compares to former eager spans on the same worlds.
- Use only the lead/reviewer measurements supplied by the continuation
  when the runtime is unavailable. Keep isolated-C1 omissions explicit;
  never relabel the script's double-added columns as historical C1/C2.
- Keep literal full-request idle subtraction, W resolution and endpoint
  clock sensitivity on partial coverage; the brief names [t0,t1].
  Empty reconstructions still return zero J and infinite uncertainty.
- Retain recorded-tool ownership after model completion, overlap flags,
  episode clipping, missing-first-token handling, integer-epoch
  arithmetic, missing-term flags and known-offset rules.
  The duty method companion is exactly
  `window_average_W;duty.uncovered_fraction=<repr(float)>`.
  Numerator: internal uncovered ns; denominator: requested ns.
- Keep stdlib-only core/tests and import reduce._integrate. No hardware,
  paid model, external-service test, credential or personal-address
  fixture is added.

## CONTRACT-CHANGE

No public API or shared-contract file changed.
If the lead ratifies C2, the independent twin needs the same full C1
endpoint differences and both window terms. Its counter reset treatment
also lacks the lane's physical decrease classification/poll sensitivity.
PowerTrace has no certified bound on unseen power/variation; C2 does not
supply that missing contract for invisible bursts.

## FIX LOG

### Round 1
Statuses below mean code/report treatment, not a claim that blocked repros ran.
- B1 fixed 865700936f4b3128e72b56dd59bd5699dcc1a0dc; twenty-turn runner regression in 3fd2cf697c6c7215e6db9fe17a626f7ef5028b4b.
- M1 fixed 480a0a3b6bc7035e71596f15b19c1554032822d3: restart from zero; observed-peak reset sensitivity.
- M2 fixed 711148d337c86e15c13b2105f29507575d738069, with hand counterexample in 74a7fc811cabcfc30ce48eab0cc5d6e3cb4354f5; coverage ruling and measured docstrings remain open.
- m1 fixed 480a0a3b6bc7035e71596f15b19c1554032822d3: zero joules/infinite half-width for missing data.
- m2 fixed c7cd8f57e6992c9dae94a08d9018428432fe7bd0: retained explicit requested-interval reading and printed both alternatives below.
- m3 fixed 480a0a3b6bc7035e71596f15b19c1554032822d3: query-clipped comparisons and zero-duration early return.
- m4 fixed 480a0a3b6bc7035e71596f15b19c1554032822d3: counter hold includes its sample jump; both readings tabulated.
- m5 rejected: the brief expressly lets the lane state the companion-field format; current documented representation is valid and independent comparisons parse both spellings. No data or number changes are justified by representation alone.
- m6 fixed 480a0a3b6bc7035e71596f15b19c1554032822d3: subprocess cwd is the checkout root.
- m7 fixed 480a0a3b6bc7035e71596f15b19c1554032822d3, refined in 74a7fc811cabcfc30ce48eab0cc5d6e3cb4354f5: retain source-domain offset and distinguish mismatch from missing.
- Numeric test findings fixed in 480a0a3b6bc7035e71596f15b19c1554032822d3 and 711148d337c86e15c13b2105f29507575d738069: exact-zero derivations, agreement floor, physical quanta and host NVML clock.

### Round 2

- R2-M2 fixed 6a54c7da4b3df57233fb20dbf1f56302a7d7d147; full C1 and both C2 sensitivities with one-step derivations. World reporting is in 47f8b75e32ad260afc86cb5a22fb57e619491e36. Lead measurement at 19a9bdf2a confirms the prescribed reviewer-world C2 counts; the remaining counter-world shortfall is handled below.
- R2-m1 fixed 3572ac7f12a43d2c0ea305b131372f08dac4ff1b (report) and 374ea7465670496e77d08e8bdf2f93c5b95b2817 (tests); removed the false 100% comment. Fix2c below supplies the lead's measurements and restores the required counter expectedFailure.
- R2-m2 fixed 19fa3d5b4fb447fef6b6e5dfe6c0749576db3033; impossible restart readings become counter.decrease, count zero, stay out of the peak and retain poll sensitivity. No non-reset peak gives infinite uncertainty. Lead edge results are tabulated above.
- R2-m3 fixed 374ea7465670496e77d08e8bdf2f93c5b95b2817; lazy requested spans plus a single-entry cache. Lead cold-query measurement is .06 s versus 3.58 s before, with equal joules; the public/eager agreement regression has no reported failure.
- R2-m4 rejected: the brief says idle_watts is “subtracted as a constant power over [t0,t1]”; retain that reading while the lead rules. Lead-confirmed numbers appear below; no code change.
- R2-M2 fixed f364db3dcf6ace7af7986accf7a165e77d34830f (fix2c); restored counter expectedFailure with lead-measured C2 498/505 segments, totals 5/5, retaining the exact 100% assertion and separate structural checks.
- R2-m1 fixed f364db3dcf6ace7af7986accf7a165e77d34830f (fix2c docstring); records the lead's measured coverage at 19a9bdf2a. This continuation report replaces stale execution placeholders with explicitly sourced counts, costs, biases and deltas.

## OPEN ISSUES

- **Execution:** nothing ran in this seat, including the final-head test
  after adding expectedFailure. The lead's 69-test baseline had the one
  counter coverage failure described above. The repeat commands are in
  TESTS RUN; the continuation's runtime-unavailable fallback is used.
- **R2-M2 coverage:** C2 leaves 7/505 counter segments outside their own
  widths in lane worlds. In reviewer worlds it leaves 146/2134 NVML
  power, 4/1987 powermetrics and 5/2198 counter segments outside.
  These counts are derived by subtraction from the lead's measurements.
  Worst NVML error/width is 216. Episode-total coverage is 5/5 lane and
  12/12 reviewer for these sensors. No threshold was relaxed.
- **Twin comparisons — measured by the lead at 19a9bdf2a:** the comparison
  run has 66 failed subtests, every one a half-width comparison:
  INA3221 6, NVML power 20, powermetrics 20, NVML counter 20.
  Exactly 60 first failures are episode totals and 6 are INA3221 gap
  segments. No twin file was edited. The supplied evidence gives the
  following seed-0 numerical examples; it does not include a per-subtest
  delta list for the remaining seeds, so those magnitudes are not invented.

  | Seed-0 comparison | Lane half-width (J) | Twin half-width (J) | Lane minus twin (J, derived from printed values) |
  |---|---:|---:|---:|
  | NVML power total | 2440.40 | .854 | +2439.55 |
  | powermetrics total | 1.325 | .908 | +.417 |
  | NVML counter total | 11.67 | 5.84 | +5.83 |
  | INA3221 gap | .017050 | .017040 | +.000010 |

  Each subtest stops at its first mismatch. The lead separately checked
  joules on seeds 0–3, every segment and total: all agree at the brief's
  1e-6 relative bar, with maximum relative differences 4.1e-14 INA3221,
  1.2e-13 NVML power, 6.4e-13 powermetrics and 1.9e-7 counter.
  The additive C1/C2 terms explain width divergence; the physical
  counter-drop sensitivity is another lane/twin difference.
- **A7 tool bias — measured by the lead at 19a9bdf2a:**

  | Sensor | Lane worlds: summed lane-minus-truth / tools | Reviewer worlds: summed lane-minus-truth / tools |
  |---|---:|---:|
  | INA3221 | +.22 J / 100 | 0.0 J / 158 (at printed precision) |
  | NVML power | +477.96 J / 100 | +1122.0 J / 509 |
  | powermetrics | +60.46 J / 100 | +126.9 J / 470 |
  | NVML counter | +683.38 J / 100 | +1195.7 J / 535 |

  Linear reconstruction moves energy from high-power decode into the
  following tool. C2 changes widths only, leaving this bias unchanged.
  Its sign accumulates across tools (about +2.2 J/tool for reviewer
  NVML power/counter, derived by dividing the table sums by counts).
  A7 must not combine these per-segment sensitivities as independent
  random errors; doing so can under-cover the systematic sum.
- C2 episode-total conservatism and the partial-coverage interpretation
  await rulings below. The cache holds at most one immutable trace,
  which can be large. Counter/coverage allowances use observed peaks;
  unseen larger peaks and dead sensors remain uncertified.
- The quick-tier discovery-namespace issue remains outside scope.
  No hardware validation or statistical population-coverage claim is made.

## NEEDS_RULING

**R2-M2 / C2 — changes printed half-widths.**
Question: ratify full endpoint differences plus both single-step window
sensitivities? Options: round1, C1 alone, or implemented C2.
Recommend C2 with its stated assumptions and invisible-burst limitation,
as requested by FIX ROUND 2, subject to delta re-review.

The coverage tables in END-TO-END distinguish historical isolated readings
from double additions. **Measured by the lead at 19a9bdf2a**, C2 gives
all 505/505 lane segments for each W sensor but 498/505 counters;
reviewer NVML power remains 1988/2134 (93%), worst error/width 216.
The cost belongs beside this recommendation: reviewer NVML median
episode-total width is 2.39e3 J against median error 39.5 J (max 125 J),
while lane total widths are 598–645 J versus round1 about .28 J.
C2 adds every duty gap's one-step term across the whole episode, even
when signed integration errors cancel. This widens total sensitivities
far more than the observed total errors. C2 is implemented; ratification
and certification/merge remain the lead's work. No further code is
blocked in this continuation's authorized scope.

**R2-m4 / READING-C — requested versus observed interval.**
Question: keep full-request idle/resolution/clock sensitivity, or use
only overlap? Recommend the current literal full-request reading:
idle_watts is “subtracted as a constant power over [t0,t1]”.

**Measured by the lead at 19a9bdf2a** (unchanged from the
reviewer-measured e3db70aeb repro): constant 50 W starting 5 s late,
idle 10 W, request [0,20] s yields lane 550 J (half-width 250.2 J),
twin 600 J (250.15 J). A wholly before/after trace gives lane -200 J
with energy.negative, twin 0 J. The lead reported all trace-coverage
lines unchanged. **Derived:** the extra subtraction is
10 W * 5 s = 50 J; the extra W-resolution width is
.01 W * 5 s = .05 J. For a wholly disjoint constant trace lane width
is 50 W * 20 s + .01 W * 20 s = 1000.2 J, twin 1000 J.
C2 adds zero for a constant waveform. This ruling changes printed
joules, so no alternative reading was silently installed.
