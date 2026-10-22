# Alignment attribution lane

## SUMMARY
- Implemented the exact frozen EnergyEstimate, SegmentEnergy and EpisodeAttribution records and public A4 functions.
- Integrates clipped point-power, trailing-window means with duty-gap interpolation, and cumulative counters.
- Carries clock, endpoint interpolation, resolution and partial-coverage sensitivity terms.
- Tiles recorded turns, prefill/decode phases, tools and all episode gaps; tampered work remains attributable.
- Added twenty closed-form/record tests and three production-shaped synthetic tests across NVML, INA3221 and powermetrics shapes.
- All changes are committed on lane/2026-10-21-align-attribution; shared contracts remain untouched.
- Validation is incomplete: the managed execution environment remains starting/offline, and CI's quick gate fails on a pre-existing discovery-namespace bug.
- Draft PR https://github.com/mpmdw/JouleWise/pull/519 provides existing CI feedback; no merge is requested.

## FILES
- `joulewise/align/attribution.py`: sensor reconstruction, imported reducer integration, uncertainty, flags and episode tiling.
- `tests/align/test_attribution.py`: twenty closed-form, uncertainty, selection, malformed-record and stdlib import tests.
- `tests/align/test_attribution_worlds.py`: independent rectangular-timeline oracle, sensor simulation and twenty-turn end-to-end checks.
- `.codex-report/align-attribution.md`: this report.
- No registry file has been changed.

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
Local shell setup, focused tests, the required
`python3 -m unittest discover -s tests/align -t .`,
`python3 -m unittest discover -s tests`, the touched tier and fixture census
have NOT run: exec_command reports "No usable execution environment is available."
No extras were installed or required. No extra-dependent tests were introduced.

Existing GitHub CI run https://github.com/mpmdw/JouleWise/actions/runs/39703208325
at d5e1c567a34f07a412680bffed9ffdcf985b9252:
- `python3 scripts/quick_suite.py --tier quick --workers 4`: 212 modules selected, 177 excluded, 211 passing modules, one failing module. Passing-module test counts are not emitted by this runner.
- Failing module `tests.test_shard_tests`: 4 tests, 1 failure, 0 errors, 0 skips. Its comparison receives `align.test_*` from unittest and `tests.align.test_*` from the shard inventory, including the pre-existing `test_records`.
- The two new attribution modules and pre-existing align record tests are excluded from the quick tier as unknown timing weights; full shards are skipped after that gate fails. Thus no attribution tests have executed yet.
- State, pin, documentation, historical-receipt and strict mock CLI fences passed.
- Wheel/source build and clean installed-wheel smoke passed.
- The separate merge-readiness ledger fails because review/validation entries are pending. The PR remains draft.

## END-TO-END
Authored, not yet executed: independent true-power timeline -> trailing-window
or point sensor observations -> bounded analogue noise plus quantization ->
PowerTrace and ClockMapping -> twenty-turn Episode -> to_json/from_json ->
attribute_episode -> every-segment true-integral and conservation checks.
Five deterministic seeds per sensor; every seed must pass. This is an empirical
regression requirement, not an inference about population coverage.

Each world has 20 turns, 20 tools, 101 contiguous phase/tool/gap segments,
growing cached context, 600 prompt tokens/s and 40 decode tokens/s fixture rates,
hidden tokens and unlogged turns/tools. Tools span 0.2--30 s. Sensor parameters:
- NVML: 100 ms period, trailing 25 ms window, 1 W quantum, 50 ms mock synchronization half-width; gap/prefill/decode/tool power 70/330/240/90 W before seed variation.
- INA3221: 1 ms period, instantaneous samples, 0.02 W quantum, 0.5 ms mock synchronization half-width; 3/18/12/5 W.
- Powermetrics: 100 ms period and window, 0.1 W quantum, 10 ms mock synchronization half-width; 8/45/30/12 W. Its clock contribution is about the M3 instrument's 1 J attribution limit.
- Noise is bounded by half a quantum before rounding; total observation error is bounded by one quantum, matching the resolution contribution.
- A separate invisible-burst control places a 400 W excess for 50 ms inside the 75 ms unobserved NVML gap. Its 20 J effect exceeds the nominal 7.1 J half-width and must retain duty.uncovered.
Observed seed statistics and totals remain pending execution; no synthetic result is claimed as hardware validation.

## DECISIONS I MADE
- The explicit brief selects this bounded AGENT task. WRITE_SCOPE overrides global planning/report writes; no hardware, rentals, credentials or paid model services are used.
- Read PIPELINE.md, records.py and interfaces.py before writes, plus phase_share.py and reduce.py's trapezoidal integration. They remain unchanged.
- TASK_QUEUE.md is empty on the spine; RUN_STATE.md has no active stop card. Only the root AGENTS.md applies in the inspected directories.
- No sensor_sim.py exists on the starting spine; the generator stays inside the allowed test files.
- Core and tests are stdlib-only. Reuse reduce._integrate via two-point spans; subtract integer nanosecond origins before converting to seconds, following phase_share.
- Prepare reconstruction once per episode; binary-search the affected spans for each segment. This avoids a quadratic interpolation scan on 1 kHz episodes.
- Mapping is t_episode=t_trace+offset_ns. At a power sample knot, both touching brackets contribute to the local endpoint peak; counter peak power is its adjacent observed slope.
- Window support starts at first_timestamp-window, including a single valid window sample. Constant means own their covered windows; neighbouring means bridge each actual uncovered gap.
- Method format is exactly `window_average_W;duty.uncovered_fraction=<repr(float)>` when a query intersects gaps, with `duty.uncovered`. The fraction is internal uncovered nanoseconds divided by full requested nanoseconds; out-of-trace time is excluded from the numerator and separately flagged.
- Endpoint interpolation compares a left hold with the linear reconstruction over [t0, span.end] and [span.start, t1]; constant window support contributes zero. A held cumulative reading allocates zero partial counter increment.
- Counter resolution is twice its J quantum. No wrap modulus is present in records: preserve the signed observed counter difference and flag counter.wrap rather than inventing unwrapping.
- Idle subtraction covers the full requested interval, including out-of-trace duration, exactly as the brief states. Gross integration covers only available overlap; missing time adds peak-power sensitivity.
- Missing clock, interpolation or resolution terms contribute zero and name the missing term in flags. Negative estimates are preserved and flagged. Nonfinite samples are omitted with a flag; reversed intervals and nonfinite idle return flagged sentinel estimates rather than refusals.
- Attribute all recorded work regardless of logged flags. Unknown first-token times use decode with turn.no_first_token. Every positive-duration tool is carved out, and gaps include episode edges.
- Records allow overlapping/out-of-order turns, out-of-turn tools and overlapping windows. Lane-local adapters sort/clip, flag anomalies and assign earlier-starting intervals (earlier-ending windows) precedence; tools take precedence over model phases. This prevents double counting without changing shared validation.
- Duplicate source/channel traces or clock mappings use the first matching entry plus an ambiguity flag. Missing selection produces a flagged empty reconstruction.
- Closed forms use the brief's 1e-6 relative agreement rule, capped at 1% of compared uncertainty where present and checked to clear 1e6 ulps. Conservation uses a gamma_n floating-operation bound derived from span/segment count and absolute energy sum.
- Nominal half-widths describe only the specified additive sensitivity terms. Duty-gap interpolation cannot bound arbitrary invisible bursts; the explicit negative control preserves that scientific limitation.
- A connected-GitHub fallback created and committed this branch while the shell was unavailable. Never force-pushed or wrote another branch. The required local checkout remains pending.
- Opened a draft PR against the spine to obtain existing public CI feedback. Pending ledger entries truthfully keep it unready.

## CONTRACT-CHANGE
none. Endpoint and method-string conventions are documented above for the independent twin.
No shared contract file was modified.

## OPEN ISSUES
- Managed environment startup remains unavailable; local setup and all required local verification are blocked.
- CI is blocked before full shards by discovery naming in tests/test_shard_tests.py.
- Independent twin comparison has not run; no independent agreement is claimed.
- The specified bound cannot certify arbitrary unobserved duty-gap work; consumers must retain duty.uncovered.
- No physical hardware was accessed or validated.

## NEEDS_RULING
No scientific/data-selection ruling is needed.

A WRITE_SCOPE expansion is pending for a concrete one-line inventory fix:
in `tests/test_shard_tests.py`, change
`loader.discover(os.fspath(TESTS_DIR))` to
`loader.discover(os.fspath(TESTS_DIR), top_level_dir=os.fspath(ROOT))`.
This corrects the discovered namespace for both the spine's record tests and the new modules.
The brief permits only name additions to registries, so that logic change has NOT been made.
Options: allow the one-line fix (recommended), or preserve the file and leave CI blocked.
Blocked work: full CI shards, including attribution test execution.
