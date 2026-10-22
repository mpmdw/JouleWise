# Alignment attribution lane — fix round 2

## SUMMARY
- Continued the existing lane from e3db70aeb27d3f9d4ac83e34421a771b12058ba4.
- Implemented C2: full endpoint hold-versus-line differences, duty-gap sensitivity and within-window cut sensitivity.
- Every C2 term applies to public interval queries, episode segments and episode totals; each states its one-step assumption.
- Implausible counter drops count zero with counter.decrease and poll sensitivity; absent non-reset peak evidence yields infinite uncertainty.
- Cold point queries construct only requested spans; repeated public calls cache the latest immutable trace/mapping preparation.
- Preserved the 100% world-coverage assertions and the invisible-burst control; removed obsolete expected-failure decorators and stale coverage claims.
- Added round-1/C1/C2 coverage and signed tool-bias reporting, including five reset-counter worlds.
- Changes are committed and pushed within WRITE_SCOPE; the cloud runtime remains unavailable, so no local Python result or post-fix measurement is claimed.
- C2 printed widths, twin disagreement deltas and the full-request partial-coverage reading still require lead review.

## FILES
- `joulewise/align/attribution.py`: integration, additive C2 uncertainty, physical counter-drop classification, lazy point spans and a single-entry preparation cache.
- `tests/align/test_attribution.py`: closed-form C2 expectations, duty-gap overlap, counter dip/first-drop/no-peak regressions and a cold-query construction-count regression.
- `tests/align/test_attribution_worlds.py`: twenty-turn production-shaped worlds, round-1/C1/C2 statistics, signed tool bias, reset counters and public-query/prepared-episode agreement checks.
- `.codex-report/align-attribution.md`: current report, retained round-1 FIX LOG and round-2 dispositions.
- No registry, workflow, inventory or shared-contract file changed. `tests/test_shard_tests.py` is untouched.
- Twin files and the two .review2 scripts were read from the brief/public twin branch but could not be written into the unavailable VM. They are not committed.

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
**Nothing ran locally in this seat.** No Python version, test count, skip count,
coverage count or runtime has been measured here. Repeated shell attempts fail
before starting the command:
`No usable execution environment is available. Wait for an environment to become available before using this tool.`

An environment wait was started and remained unresolved across repeated retries.
Runtime status alternated between starting and pending, always offline, with
failure=null. Diagnostics returned history_status=not_found and no records.
A text request to restart/reattach the VM was sent to the user while independent
authorized code work continued. This is the brief's execution-unavailable
fallback, not successful verification.

The following exact command requests were rejected before any process started:
```bash
python3 --version
python3 -m unittest discover -s tests/align -t .
python3 -m unittest discover -s tests/align -t . -p 'test_attribution*.py'
python3 -m unittest discover -s tests/align -t . -p test_twin_attribution.py
python3 -P /workspace/JouleWise/.review2/r2_truth.py /workspace/JouleWise 12
python3 -P /workspace/JouleWise/.review2/r2_edges.py /workspace/JouleWise
```
The required checkout/fetch, uncommitted repro-file setup and the following exact
verification commands cannot execute until a usable VM is attached. All commands
are from `/workspace/JouleWise` unless the command itself gives an absolute path:
```bash
python3 -m unittest discover -s tests/align -t . -p 'test_attribution*.py'
python3 -m unittest discover -s tests/align -t . -p test_attribution_worlds.py
python3 -m unittest discover -s tests/align -t . -p test_twin_attribution.py
python3 -P /workspace/JouleWise/.review2/r2_truth.py /workspace/JouleWise 12
python3 -P /workspace/JouleWise/.review2/r2_edges.py /workspace/JouleWise
```
Cwd-independent import/discovery regression, from `/tmp`:
```bash
python3 -m unittest discover -s /workspace/JouleWise/tests/align -t /workspace/JouleWise -p test_attribution.py
```
No extras were installed. Production code and authored tests use stdlib only;
there is no extra-dependent run or measured dependency skip.

Historical baseline only: **reviewer-measured at e3db70aeb**: 62 align tests ran,
including two expected failures. This is not verification of this round's code.

Hosted intermediate evidence at code commit
374ea7465670496e77d08e8bdf2f93c5b95b2817:
https://github.com/mpmdw/JouleWise/actions/runs/39713701147
The build job succeeded. The fence steps completed successfully but the job
was cancelled by the next authorized lane push; quick/test/downstream jobs were
cancelled. No attribution test count or final-head success is inferred.
The known quick-tier discovery-namespace failure is outside WRITE_SCOPE.

## END-TO-END
Authored chain: independent rectangular true power -> point, trailing-window or
cumulative-counter sampling -> bounded analogue noise plus quantization ->
PowerTrace/ClockMapping -> twenty-turn Episode -> JSON round trip ->
attribute_episode -> exact tiling, conservation, tool contrast and own-half-width
coverage assertions. Public trace_energy queries are also compared to the episode
preparation and the former eager span/start representation over every segment
and total on the same five seeds.

The original power fixtures are unchanged: 100 ms NVML polling with 25 ms duty,
1 ms INA3221 point sampling and 100 ms whole-window powermetrics. Tools span
0.2–30 s; the constructed regular episode has 101 segments and 20 tools.
Sensor quanta remain derived in code: integer mW = .001 W, integer mJ = .001 J,
and 40 uV / 5 mOhm * 5 V = .04 W. Clock brackets remain .5 ms for INA3221,
1 ms for powermetrics and unknown/no mapping for host-clock NVML power.

The added counter worlds use the same twenty-turn timing, 100 ms polls,
integer-mJ quantization, an exact synthetic offset and one restart inside the
longest tool. Their workload levels are fixture choices; 300 W decode keeps
the shortest tool's contrast above its partial-counter sensitivities. Restart
placement keeps a reset's uncertainty below that long tool's contrast.
The original midpoint-reset world and runner-post-model tool worlds remain.

The world output now emits coverage_by_reading, totals_by_reading,
total_half_widths_j, segment_half_width_delta_j_range, signed_tool_error_j and
tool_count. Earlier readings are replayed algebraically on the same observations:
round1 = C2 width - window terms - half the full endpoint term;
C1 = C2 width - window terms. The original three worlds retain their fixtures.
No new output from that chain exists yet because Python cannot start.

The invisible-burst control is unchanged: derived 400 W * .050 s = 20 J of
unseen excess inside a 75 ms NVML duty gap, versus derived .001 W * .1 s
= .0001 J nominal width for identical window means. C2 adds zero when all
observed means are identical and therefore does not certify that burst.

Reference coverage below is **reviewer-measured at e3db70aeb**, using the
reviewer's candidate additions to that old code. It is not a run of the current
implementation. “Not supplied” means the brief contains no such measurement.

| Worlds / sensor | Round-1 segments; totals | C1 segments; totals | C2 segments; totals |
|---|---|---|---|
| Lane / INA3221 | 505/505; 5/5 | not supplied | not supplied |
| Lane / NVML power | 228/505; 0/5 | not supplied | not supplied |
| Lane / powermetrics | 131/505; 5/5 | not supplied | not supplied |
| Lane / new counter worlds | unexecuted | unexecuted | unexecuted |
| Reviewer / INA3221 | 635/635; totals not supplied | 635/635; totals not supplied | 635/635; totals not supplied |
| Reviewer / NVML power | 816/2134; 0/12 | not supplied | 1988/2134; 12/12 |
| Reviewer / powermetrics | 866/1987; 12/12 | not supplied | 1983/1987; 12/12 (totals derived from nonnegative widening) |
| Reviewer / NVML counter | 1940/2198; 12/12 | 2193/2198; 12/12 (totals derived) | 2193/2198; 12/12 (totals derived) |

Current-code segment/totals coverage for all three readings, numerical width
deltas and signed tool errors on both sets of worlds are unmeasured.
The ordinary 100% assertions have not been relaxed. Their execution must confirm
that removing the two obsolete expectedFailure decorators is correct; if a
sensor remains below 100%, the brief requires restoring its expectedFailure
with the actually measured count in its docstring.

Counter edge deltas below are **derived**, rounded here to the integer-mJ
reporting quantum; no repro execution is claimed. The comparison uses the
reviewer's old outputs and the current physical classification:
| Reviewer edge | New J | New half-width J | Change in J / half-width J |
|---|---:|---:|---|
| Steady | 1200.000 | .002 | 0 / 0 |
| Stuck counter | 0 | .002 | 0 / 0 |
| Reset at first step | 1170.000 | 30.002 | -60 / -30 |
| Two resets | 1200.000 | 90.002 | 0 / 0 |
| 1 mJ non-reset dip | 1200.001 | 60.003 | about -5,000,570 / -5,000,510 |

For the dip, ignoring one 30 J poll is offset by the following 60.001 J recovery:
1200 - 30 + 30.001 = 1200.001 J. That recovery, a non-reset step, sets
600.01 W observed peak; the ignored dip contributes no power peak. Its .1 s
ambiguity allowance is 60.001 J, plus two .001 J quanta. The old megajoule
baseline can no longer inflate the peak to about 50 MW.
For the first drop, 60 J exceeds .1 s * 300 W = 30 J: count zero, retain
39 * 30 J and add one 30 J poll. Its 1200 J truth remains inside the width.
The two-resets fixture actually includes three drops, including its first step;
each new reading fits the physical poll limit, so its 90 J sensitivity stays.

Derived hand C2 delta: the 0/63/100 W means at 0/100/200 ms and query [37,100] ms
still give 3.969 J against 6.3 J true energy. Half-width increases from
1.3594455 J to 5.218828 J (+3.8593825 J): C1 adds 1.3593825 J and C2's
100 W * .1 s / 4 adds 2.5 J. This is a closed-form regression expectation.
The reviewer-world numerical half-width distribution deltas cannot be reported
as measured until r2_truth runs.

## DECISIONS I MADE
- Continue the named lane from e3db70aeb, never reset it to the spine. With no
  usable filesystem runtime, use connected GitHub tree/commit/ref tools with
  the inspected parent SHA, expected-head checks and force=false. No other
  branch is written. The local checkout remains unperformed.
- Read the existing report before edits, then PIPELINE.md, records.py,
  interfaces.py, phase_share.py and reduce._integrate. Root AGENTS.md and
  Mission M0 were read; the generated stop card is NONE. WRITE_SCOPE
  overrides generated-state bookkeeping. No sensor_sim.py exists on this
  branch, so retain and extend the existing test-local independent generator.
- Implement the explicitly authorized C2 reading while retaining it under
  NEEDS_RULING because printed half-widths change. C1 replaces half the
  absolute hold/linear difference by the full difference at each endpoint.
  C2 adds |neighbour mean jump| * overlapping duty-gap seconds / 2, and
  range(neighbouring three means) * window seconds / 4 at each strictly
  interior window cut. Every term includes its one-step derivation in code.
- C2 is an observed-variation sensitivity under the stated one-step
  assumptions, not a universal bound on invisible bursts. Retain
  window.edge_allocation_unresolved and the unchanged invisible-burst test.
- R2-m2: determine the peak of nondecreasing counter steps before reading
  decreases. Accept a restart only when its new nonnegative reading is no
  larger than poll duration * that peak. Otherwise count zero with
  counter.decrease and exclude the drop from the peak. Both categories add
  overlap duration * observed peak with distinct interval flags.
- A counter with no nondecreasing step has no observed peak: all its drops
  count zero with counter.decrease, counter.peak_missing and infinite
  uncertainty for affected intervals/partial coverage. A flat nondecreasing
  step establishes observed 0 W; as with the old dead-counter control, that
  sensitivity cannot certify unobserved work from a dead sensor.
- R2-m3: use lazy point-span construction plus a single latest-trace/mapping
  cache, keyed by trace identity and mapping equality. Cold calls retain an
  O(n) finite-value validation scan to preserve global flags, but create O(q)
  spans for q queried brackets. Repeated calls reuse that validation and do
  O(log n + q) work. Full-trace peak evaluation is lazy when missing coverage
  needs it. Window/counter preparations remain reusable eager reconstructions.
  No estimator formula, integration order or public signature changes here.
- Compare public queries with episode preparation and the former eager
  span/start arrays on every own world using
  1e-6 relative agreement capped at 1% of the smaller printed width, and
  assert the million-ulp floor. The cold-query test counts requested spans
  plus two endpoint comparisons rather than using an arbitrary timing bar.
  These checks are authored, not yet executed.
- Remove the two old expectedFailure decorators because C2 now supplies the
  one-step sensitivity exercised by these rectangular worlds; retain their
  exact 100% assertions and record the unresolved execution confirmation.
- Keep full-request idle subtraction, W resolution and requested-endpoint
  clock sensitivity for partial coverage. The brief explicitly says idle
  is subtracted “over [t0,t1]”. Empty reconstructions still return zero J and
  infinite uncertainty, without subtracting idle from nonexistent readings.
- Retain previous tool ownership/episode clipping, missing-first-token,
  integer-epoch, missing-term flag, method-format and known-offset rules.
  Method companion remains exactly
  window_average_W;duty.uncovered_fraction=<repr(float)>.
  Duty numerator is internal uncovered ns; denominator is requested ns.
- Keep core/tests stdlib-only and import reduce._integrate. No hardware,
  paid model, network test, credential or person-address fixture was added.

## CONTRACT-CHANGE
No shared contract file or public API changed.
If the lead rules C2, the independent twin needs the same full C1 endpoint
differences and both C2 window terms; until then its half-width comparisons
are expected to differ by those additive terms. Its existing counter reset
reading also lacks the lane's physical drop classification and poll sensitivity.
PowerTrace supplies no certified power/variation bound for an invisible burst;
such a guarantee still needs a separately ruled physical contract.

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
- R2-M2 fixed 6a54c7da4b3df57233fb20dbf1f56302a7d7d147; added full C1 and both C2 sensitivities with one-step derivations. World reporting is in 47f8b75e32ad260afc86cb5a22fb57e619491e36. Post-fix measurements remain blocked by the unavailable runtime; no passing repro is claimed.
- R2-m1 fixed 3572ac7f12a43d2c0ea305b131372f08dac4ff1b (report) and 374ea7465670496e77d08e8bdf2f93c5b95b2817 (tests); removed the false 100% comment and obsolete expectedFailure docstrings. This report replaces unexecuted placeholders with explicit unavailable results and labeled reviewer/derived references, using the brief's execution-unavailable fallback.
- R2-m2 fixed 19fa3d5b4fb447fef6b6e5dfe6c0749576db3033; classify impossible restart readings as counter.decrease, count zero, exclude the drop from peak and retain poll sensitivity. No non-reset peak gives infinite uncertainty.
- R2-m3 fixed 374ea7465670496e77d08e8bdf2f93c5b95b2817; lazy requested point spans plus a single-entry preparation cache. Construction-count and own-world numerical agreement regressions are authored; timing is unmeasured.
- R2-m4 rejected: the brief says idle_watts is “subtracted as a constant power over [t0,t1]”; retain that reading while the lead rules on it. Updated reference numbers are labeled below; no code change.

## OPEN ISSUES
- EXECUTION BLOCKER: no usable VM. Local checkout/setup, actual Python version,
  align/twin/repro runs, final counts/skips, C2 coverage confirmation, expected
  failure disposition, width-distribution deltas and runtime measurements have
  not executed. No final-head passing claim is made. Next action is attach a
  usable VM, fetch/check out this branch, create only the uncommitted twin and
  supplied .review2 files, then run the exact commands in TESTS RUN.
- TWIN DELTAS: the required comparison command is unexecuted, so an exhaustive
  measured comparison/delta list does not exist. Analytically, for ordinary
  fully covered traces, lane width minus the unchanged twin is its old
  interpolation term plus C2's window terms, plus the lane's pre-existing
  reset-poll allowance for counters. Example derived differences: the
  37 ms window cut above +3.8593825 J; the [.25,1.5] s 0/100/300 J counter
  query is now 125.002 J versus twin 62.502 J (+62.5 J). Partial coverage
  also retains the separately listed full-request reading. Twin files were
  not edited.
- A7 TOOL BIAS: post-C2 summed signed tool error and tool counts on both
  world sets are unmeasured. Own-world reporting now emits both. References,
  **reviewer-measured at e3db70aeb**, are NVML power +1122 J over 509 tools,
  NVML counter +1196 J over 535 tools and INA3221 approximately 0 J (tool
  count not supplied); powermetrics bias was not supplied. C2 changes
  half-widths, not reconstructions. These same-sign errors accumulate across
  tools; consumers combining segment widths as independent random errors
  can under-cover that bias.
- The reviewer-world C2 candidate still covers fewer than all segments:
  NVML power 1988/2134, powermetrics 1983/1987 and counters 2193/2198.
  These are reviewer-measured candidate results on e3db70aeb, not a passing
  claim for this implementation. C2 needs a delta re-review and a lead ruling.
- Counter reset/dip and missing-coverage allowances assume the observed peak;
  unseen larger power and dead sensors remain uncertified. The cache retains
  at most one latest immutable trace, which may itself be large.
- CI's discovery namespace issue is outside scope. No hardware validation or
  statistical population-coverage claim is made.

## NEEDS_RULING
**R2-M2 / C2 — changes printed half-widths.**
Question: ratify full endpoint interpolation differences plus the two
single-step window sensitivities? Options are the round-1 reading, C1 only,
or C2. Recommend C2 as explicitly requested by this fix brief, with its
one-step assumptions and invisible-burst limitation retained. The code
implements C2; certification/merge awaits lead delta review.
The labeled reference table in END-TO-END gives every available reviewer
number for the three readings on both sets of worlds. Actual current-code
coverage, total/segment width deltas, tool bias and C1-only figures absent
from the brief are unmeasured because Python cannot start. They must be
filled from the required runs, not inferred from the reviewer candidates.

**R2-m4 / READING-C — requested versus observed interval.**
Question: retain literal full-request idle/resolution/clock sensitivity,
or apply them only to overlap? Recommend the current full-request reading,
because the brief expressly names [t0,t1].
**Reviewer-measured at e3db70aeb:** trace begins 5 s late, 50 W, idle 10 W,
request [0,20] s: lane 550 J (half-width 250.2 J), twin 600 J
(250.15 J). A trace wholly before or after gives lane -200 J with
energy.negative, twin 0 J. These reconstructions and widths are unchanged
by C2 for this constant waveform (derived: endpoint/window differences are
zero). No new repro run occurred here.
For a wholly disjoint constant trace, derived lane width is 50 W * 20 s
+ .01 W * 20 s = 1000.2 J; twin overlap resolution contributes zero,
giving 1000 J. The missing 5 s case subtracts an additional 10 W * 5 s
= 50 J and adds .01 W * 5 s = .05 J resolution relative to the twin.
The ruling changes printed energy, not just a flag.
