# Alignment attribution lane — fix round 1

## SUMMARY
- Continued the existing attribution lane from e64cd15c2bb92ebdb3d6653552376e40208968aa.
- Tools are clipped to the episode and retain their owning turn, including runner tools after model completion.
- Counter decreases restart from zero, with reset flags and a polling-interval sensitivity allowance.
- Empty traces report zero joules with infinite uncertainty; short and zero-duration intervals use only their own support.
- A mislabeled mapping retains its known offset and records the destination-domain mismatch.
- Synthetic worlds now use unaligned phases, poll jitter, derived sensor quanta, and host-clock NVML without a mapping.
- The 100% window-sensor coverage assertions remain, marked expectedFailure for M2; structural checks remain ordinary tests.
- All code is pushed within WRITE_SCOPE; Python verification and measured re-review deltas remain blocked by the unavailable cloud runtime.

## FILES
- `joulewise/align/attribution.py`: reconstruction, uncertainty, reset handling, mapping selection and episode-wide tool overlay.
- `tests/align/test_attribution.py`: 28 authored closed-form/record tests, including runner tools, reset, window-edge ambiguity, short intervals and cwd-independent import.
- `tests/align/test_attribution_worlds.py`: seven authored production-shaped tests, including two explicitly expected coverage failures and a twenty-turn runner convention world.
- `.codex-report/align-attribution.md`: report and per-finding fix log.
- No registry, workflow, inventory or shared-contract file was changed. In particular, `tests/test_shard_tests.py` remains untouched.
- The independent twin and probe scripts have not been written into the unavailable workspace and have not been committed.

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
**No local Python test has executed in this seat. Counts, skips and seed-coverage measurements are unavailable, not passing.**
Repeated `exec_command` requests, including `pwd`, return
`No usable execution environment is available. Wait for an environment to become available before using this tool.`
Two environment waits were attempted; runtime observations alternate between
pending/starting, always offline, with no reported failure or retained diagnostic
record. An asynchronous request to restart/reattach the environment is pending.

Required commands still blocked (from `/workspace/JouleWise` unless specified):
```bash
python3 -m unittest discover -s tests/align -t .
python3 -m unittest discover -s tests/align -t . -p test_twin_attribution.py
python3 -P /workspace/JouleWise/.review1/truth_and_edges.py /workspace/JouleWise
python3 -P /workspace/JouleWise/.review1/probes.py /workspace/JouleWise
python3 -P /workspace/JouleWise/.review1/lane_world_unaligned.py /workspace/JouleWise
```
Cwd regression, to run from `/tmp`:
```bash
python3 -m unittest discover -s /workspace/JouleWise/tests/align -t /workspace/JouleWise -p test_attribution.py
```
The authorized local setup/fetch and uncommitted repro-file creation remain
pending for the same reason. No extras were installed; core and tests require
only stdlib. There is no extra-dependent test run or dependency skip to report.

Existing CI evidence at intermediate code commit 711148d337c86e15c13b2105f29507575d738069:
https://github.com/mpmdw/JouleWise/actions/runs/39707828576
- changes, fences, build and installed-wheel jobs succeeded.
- quick and downstream test jobs were cancelled by subsequent lane pushes;
  no attribution test result or passing count is inferred.
- This is intermediate-head evidence, not final-head verification.
The pre-existing quick-tier discovery-namespace failure identified in the brief
remains outside this lane's scope; no fix or approval request for it is pending.

## END-TO-END
Authored chain: independent rectangular true-power timeline -> point or trailing
window sensor sampling -> bounded analogue noise and quantization -> PowerTrace
and ClockMapping -> twenty-turn Episode -> to_json/from_json -> attribute_episode
-> exact segment-identity, conservation, tool-effect and own-half-width checks.

Five deterministic seeds per sensor retain the original requirement: every
segment and every episode total within its own printed half-width. Timing now
uses integer-ns phase draws, a parameterized 37%-of-poll grid phase, and up to
2 ms poll jitter capped at a quarter period. Whole-window samples remain
back-to-back, because fixed-width windows cannot describe jittered contiguous
support. The regular worlds have 20 tools and 101 segments; tools span 0.2–30 s.
The runner-convention world ends each model turn before its tool and has 20
tools and 81 segments. Hidden tokens and logged=False turns/calls remain present.

Sensor fixtures:
- NVML power: 100 ms poll, 25 ms duty window, 0.001 W quantum from integer mW.
  Primary coverage/runner worlds use the host clock with no ClockMapping.
  The standalone reviewer adapter's default world retains a foreign domain
  with an exact synthetic offset and zero clock half-width.
- INA3221: 1 ms sampling; 40 uV shunt LSB / fixture 5 mOhm shunt * 5 V bus
  = 0.04 W. A one-sample timestamp bracket gives a 0.5 ms clock half-width.
- Powermetrics: 100 ms whole window, 0.001 W quantum from integer mW; a
  synthetic 2 ms synchronization bracket gives a 1 ms half-width. That clock
  term does not substitute for the M3 instrument's separate ~1 J attribution
  limitation.
- Bounded noise before quantization is half a quantum; rounding adds at most
  another half, matching the resolution term.
- The invisible-burst control remains: 400 W excess for 50 ms inside a 75 ms
  unobserved NVML gap is 20 J, exceeding the 0.0001 J resolution-only width.

**No seed outcomes or runtimes have been measured in this seat.** The expected
failure docstrings explicitly retain that pending status; the requested measured
coverage text must be installed after the first runnable verification.

Derived hand-case deltas (algebraic expectations, not claimed repro executions):
| Case | Old lane | Twin | Revised lane |
|---|---:|---:|---:|
| P1 tool [4,9] s, 1 kHz trace | no tool; 0 J | one tool; 449.99 J | one tool; 449.99 J |
| P2 300 W reset, [0,4] s | -4,999,370 J; hw .002 J | 1,200 J | 1,200 J; hw 30.002 J |
| P3 zero-length ramp | 0 J; hw 25 J | 0 J; hw 0 J | 0 J; hw 0 J |
| P4 ramp [.4,.5] s | 4.5 J; hw 27.26 J | 4.5 J; hw 4.51 J | 4.5 J; hw 4.51 J |
| Missing trace, 20 s, 70 W idle | -1,400 J; hw 0 J | 0 J; method none | 0 J; hw infinity |

P1 derives 450 J minus the 0.001 s terminal trapezoid's 20 W / 2 correction
= 449.99 J. P2 adds 5,000,570 J relative to the old negative estimate; its
30 J extra sensitivity is one 100 ms poll at the observed 300 W peak.

B1 delta re-review is still required on the reviewer's exact worlds. The
review-provided references were old 0 tools / 0 J versus twin 20 tools /
399.1 J (INA3221) and 13,623.8 J (NVML, truth 13,597.2 J). The revised
reconstruction is intended to reproduce those twin tool energies; **those new
world numbers have not been measured here**, so they are references for the
pending rerun, not verification. Episode gross totals are unaffected by B1;
the same interval's energy moves from gap/model phases into tool.

## DECISIONS I MADE
- This explicit bounded brief selects [AGENT] synthetic/code work. WRITE_SCOPE
  overrides repository-wide generated state/report writes. No hardware or paid
  model service was used.
- Read the previous report first, then PIPELINE.md, records.py, interfaces.py,
  phase_share.py and reduce._integrate before writes. Also inspected root
  AGENTS.md, the stop-card/intake texts, Mission M0 and orchestration guidance.
  The generated stop card is NONE and TASK_QUEUE.md is empty on this lane.
- The managed runtime never became usable. Continued the existing branch
  through the connected GitHub tools, using e64cd15c2 as parent and
  expected-head, non-forced fast-forward updates. The required local checkout
  is still pending. Public source reads include runner.py and the independent
  twin/comparison test; the twin was not copied into lane production code.
- Zero-duration turns advance gap support once and do not duplicate it.
- B1: model/gap support is built first, and every episode-clipped tool overlays
  it with owning turn index. Earlier-starting calls win overlapping time;
  adjacent distinct calls stay distinct, and a call crossing phase boundaries
  coalesces back to one tool segment. Calls outside a turn are valid runner
  output. Only crossing the episode limits adds tool.outside_episode.
- M1: NVML counter decreases mean restart since driver load, not a modular
  wrap or negative megajoules. The reset increment is the new reading.
  Retain counter.wrap for compatibility and add counter.reset. For a query
  intersecting the reset interval, add duration * observed trace peak and
  counter.reset_interval to represent missing pre-reset work. This is the
  brief's observed-peak sensitivity convention, not a guarantee against
  unsampled power spikes.
- M2/READING-A: "partial sample interval" means the raw timestamp bracket,
  including for window sensors. Use that bracket for the hold-versus-line
  term. This removes the artificial zero from constant reconstruction spans
  without claiming a bound on within-window allocation. Add
  window.edge_allocation_unresolved when a query cuts a support span.
  No guessed variability multiplier or widened reporting quantum is used.
- Preserve the 100% coverage assertion in separate M2 expectedFailure tests.
  Structural, record-roundtrip, conservation and detectable-tool checks run
  independently as ordinary tests so expectedFailure cannot conceal them.
  Selection of extra window/duty uncertainty remains NEEDS_RULING below.
- m1: no observed reconstruction means zero estimated energy with infinite
  half-width. Retain the exact API's supported base method names rather than
  introduce method none. Never subtract idle from a nonexistent observation.
- m2/READING-C: retain idle subtraction and W resolution over the full requested
  interval, and clock sensitivity at the requested endpoints. The brief says
  "over [t0,t1]" and resolution times "interval length"; the alternative
  overlap-only reading changes printed numbers and is recorded below.
- m3/READING-B: clip both partial-interval comparisons to the query. A
  zero-duration query has exactly zero energy and zero uncertainty.
- m4/READING-E: a left-held cumulative counter jumps at the right sample.
  Include that jump in the hold-minus-line difference when the partial start
  interval reaches the sample. This selects the twin's physically explicit
  sample-and-hold reading; it changes a printed half-width, so the alternative
  remains visible under NEEDS_RULING.
- m5/READING-D: retain the explicitly documented lane representation:
  window_average_W;duty.uncovered_fraction=<repr(float)>, numerator actual
  internal duty-gap ns and denominator requested ns. Out-of-trace ns do not
  enter the numerator. duty.uncovered is the flag. Missing terms retain
  clock.uncertainty_missing, interpolation.missing and resolution.missing.
  The brief requires a stated format, not the twin's spellings.
- m6: the -S import subprocess explicitly uses the checkout root as cwd.
- m7: prefer exact domain mapping, then a known source-domain translation with
  clock.episode_domain_mismatch. Reserve clock.mapping_missing for absence
  of any translation; never discard a known offset merely because its
  destination label is malformed.
- Remove scale=100 around exact zero quantities: equality is justified by
  identical limits or identically absent terms. Idle-subtraction agreement
  now uses 1% of the smaller printed width and explicitly checks the
  one-million-ulp floor. Conservation retains its separate operation-count
  gamma_n derivation. All fixture sensor quanta now have physical/reporting
  derivations beside their definitions.
- Core and tests remain stdlib-only. Continue importing reduce._integrate;
  subtract integer ns epochs before float conversion. Prepare reconstruction
  once per episode and binary-search affected spans.

## CONTRACT-CHANGE
No shared contract files changed. Proposed extension, pending ruling:
document a within-window allocation uncertainty term, and for duty sensors
supply a certified maximum-power or temporal-variation bound if finite coverage
against unobserved work is required. PowerTrace currently supplies neither.
For nonnegative whole-window power, the total known window energy can bound
how much energy lies on either side of a cut; the specified three terms do
not currently include that envelope. A local sensitivity flag is implemented
without inventing a shared-record field.

## FIX LOG
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

## OPEN ISSUES
- BLOCKING VERIFICATION: no usable cloud execution environment. The local
  checkout, uncommitted twin/probe setup, every required Python command,
  final test counts, measured coverage docstrings, performance measurement
  and review-world delta measurements are still outstanding.
- M2's required 100% window coverage is not certified by the specified terms;
  two explicit expected failures preserve the requirement.
- Counter reset sensitivity assumes the observed peak for missing time,
  just as partial coverage does; unseen larger excursions cannot be certified.
- Partial-coverage and counter-start half-width conventions remain available
  for the lead's ruling, with numerical alternatives below.
- CI's pre-existing discovery namespace failure is outside scope; no edit to
  tests/test_shard_tests.py is requested.
- No hardware validation or statistical population-coverage claim is made.

## NEEDS_RULING
**M2 / READING-A — finite window/duty uncertainty.**
Question: should the printed half-width remain the specified three sensitivity
terms, or add a nonnegative whole-window allocation envelope and an explicit
bound on power/variation in duty gaps? Recommend the latter only with a
documented physical bound; otherwise retain the unresolved flags and the
100%-coverage expected failures. Blocked: certifying own-half-width coverage.

Derived off-grid hand world: whole 100 ms window, true power 0 -> 100 W at
37 ms, means 0/63/100 W at 0/100/200 ms, query [37,100] ms, zero clock
uncertainty and .001 W quantum. True energy is 6.3 J; every reconstruction
prints 3.969 J (error 2.331 J). Old lane width is .000063 J; twin and revised
raw-bracket width is 1.3594455 J. Neither covers the edge allocation error.
This counterexample is an ordinary regression test, not a coverage relaxation.

Review-provided world coverage, **not remeasured in this seat**:
| Sensor | Old lane | Twin | Revised lane |
|---|---|---|---|
| INA3221 | 100% | not reported | pending runtime |
| NVML power | 35%; totals 0/8 | not reported | pending runtime |
| Powermetrics | 6%; worst err/hw 27.9 | 32% | pending runtime |
| NVML counter | 77% | not reported | pending runtime |
The old own-world 37 ms replay reported powermetrics 150/505 (or 136/505 with
1 ms clock) and NVML 373/505 at 1 ms clock. Those old source worlds used widened
quanta and aligned phase durations. Revised primary worlds correct both and
therefore require fresh measurement; no percentage is fabricated here.

**m2 / READING-C — requested versus observed interval.**
Question: retain literal full-request idle/resolution/clock sensitivity, or
apply all three only to overlap? Recommend full-request as implemented,
because the brief explicitly names [t0,t1]; every partial estimate is flagged.
For the review's constant 50 W, 20 s request, idle 10 W, quantum .04 W,
same clock and trace beginning at 10 s: old/revised 300 J with hw 500.8 J,
twin 400 J with hw 500.4 J; true net energy 800 J. If the trace is entirely
after the request: old/revised -200 J with hw 1000.8 J, twin 0 J with hw
1000 J. These are closed-form derived outcomes; execution is pending.
Blocked: settling the published partial-coverage convention, not code work.

**m4 / READING-E — cumulative hold jump at the start bracket.**
Question: compare just the linear remainder, or compare the held counter's
actual jump minus that remainder? Recommend the latter, implemented here.
For 0/100/300 J at 0/1/2 s, query [.25,1.5] s and no clock/resolution term:
all readings give 175 J; old width 87.5 J, twin/revised width 62.5 J
(delta -25 J). The start bracket contains a held 100 J jump versus a
75 J linear increment; its contribution is |100-75|/2 = 12.5 J.
The stop contributes |0-100|/2 = 50 J. With a .001 J quantum add .002 J
to every width. Derived regression expectations; repro execution pending.
Blocked: lead endorsement of the printed half-width convention.
