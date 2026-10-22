# NVML lane implementation report

## SUMMARY

Implemented stdlib ctypes NVML power and cumulative-energy sampling.
Fresh sampler cycles retain query brackets, sensor facts and raw counter discontinuities.
Added duty-window pooling with coverage, quantum, timing and repeatability uncertainty.
Added whole-GPU preflight, opt-in clock commands, owned load cleanup and JSON evidence.
The connected driver/thread/record world recovered 1,161 J within its 0.103840 J half-width.
The independent numerical twin passed; 95% duty intervals missed 52 of 1,000 seeds.
Final CI executed 52 lane tests: 51 passed and one optional-pynvml test skipped.
Build, wheel smoke, repository fences and the 212-module quick suite passed.
The full suite failed an existing courier timeout; local commands remain blocked by Cloud startup.
Shared contracts and the NVIDIA parser are unchanged; no hardware measurements were performed.

## FILES

- `joulewise/align/power/__init__.py`: stdlib-only instrumentation package.
- `joulewise/align/power/nvml.py`: NVML ABI binding, inventory and sampler.
- `joulewise/align/power/duty.py`: phase plans and uncertainty-aware window pooling.
- `joulewise/align/power/preflight.py`: inventory/load/clock CLI and predictive movement criterion.
- `tests/align/test_power_nvml.py`: ctypes-shaped driver, sampling and failure paths.
- `tests/align/test_power_duty.py`: multi-turn worlds, calibration and serialization.
- `tests/align/test_power_duty_twin.py`: independently authored direct-grid numerical oracle.
- `tests/align/test_power_preflight.py`: real executable/process paths and nominal false-alarm calibration.
- `docs/align/nvidia_runbook.md`: first whole-GPU collection procedure.
- `tests/test_shard_tests.py`: ONLY addition of the `align.` namespace to the shard census normalizer, under the brief's registry exception. CI run 39704268162 failed because the inventory named `tests.align.*` while unittest returned `align.*`; no timing weights or test coverage were weakened.
- `.codex-report/align-nvml.md`: this report.

## PUBLIC API

- `NvmlSampler(device_indices: Sequence[int] | None = None, *, interval_ns: int = 10_000_000, clock_domain: str | None = None, nvml: Any | None = None, library: Any | None = None, power_bound_w: float | None = None, repeat_group: str | int | None = None, clock_ns: Callable[[], int] = time.monotonic_ns, wall_clock_ns: Callable[[], int] = time.time_ns, stop_timeout_s: float = 5.0)`
- `NvmlSampler.start() -> None`
- `NvmlSampler.stop() -> tuple[PowerTrace, ...]`
- `CtypesNvml(library: Any | None = None)`: pynvml-shaped subset of the NVML API used by sampling/inventory.
- `open_nvml(*, library: Any | None = None, prefer_pynvml: bool = False) -> Any`
- `device_inventory(nvml: Any, index: int) -> dict[str, Any]`
- `plan_offsets(period_ns: int, duty_fraction: float, repeats: int) -> list[int]`
- `estimate_energy(runs: Sequence[tuple[PowerTrace, int, int]]) -> DutyEstimate`
- `DutyEstimate(joules: float, half_width_j: float, coverage_fraction: float, flags: tuple[str, ...])`
- `assess_power_movement(traces: Sequence[PowerTrace], idle_interval: tuple[int, int], load_interval: tuple[int, int], *, false_alarm_rate: float) -> dict[str, Any]`
- `run_preflight(*, device_indices=None, idle_seconds=2.0, load_seconds=2.0, recovery_seconds=1.0, interval_ns=10_000_000, load_cmd=None, try_lock_clocks=False, graphics_clock_mhz=None, false_alarm_rate=0.01, matmul_size=2048, command_timeout_s=5.0, nvml=None, library=None) -> dict[str, Any]`
- `main(argv: Sequence[str] | None = None) -> int`, exposed as `python3 -m joulewise.align.power.preflight --out report.json [--load-cmd ...]`.

NVML trace notes use JSON format `joulewise.align.nvml.v1`. They retain query half-widths, raw field timestamps, mapped window endpoints/uncertainty, support/failures, device facts, raw integer energy values, discontinuities and optional power bound/phase label. Unknown capabilities remain explicit.

## TESTS RUN

Final executed source: `023c9d29592626e92f8715cd2af3d1f77f2f0f5c`.
CI: <https://github.com/mpmdw/JouleWise/actions/runs/39709783657>.
Python 3.13, stdlib-only test jobs; build/fence/wheel jobs also used Python 3.11.

Exact commands and outcomes:
- `python3 scripts/quick_suite.py --tier quick --workers 4`: 212 modules, 179 excluded by the existing quick tier, 0 failures, PASS (152.545 s).
- `python -m compileall -q joulewise tests`: PASS in all twelve ordinary shards.
- Ordinary CI jobs execute `python -` with SHARD_COUNT=12 and SHARD_INDEX=1..12. The exact stdin program is the "Unit tests (stdlib core only, per D-009/D-017)" here-doc in the [unchanged workflow](https://github.com/mpmdw/JouleWise/blob/023c9d29592626e92f8715cd2af3d1f77f2f0f5c/.github/workflows/ci.yml). It invokes `shard_tests.run_units(partitions[index - 1], count, index)`, using stdlib unittest loader/runner. It does not invoke the local discovery CLI.

| Lane module | Tests | Failures | Errors | Skips |
|---|---:|---:|---:|---:|
| tests.align.test_power_nvml | 17 | 0 | 0 | 1 |
| tests.align.test_power_duty | 10 | 0 | 0 | 0 |
| tests.align.test_power_duty_twin | 12 | 0 | 0 | 0 |
| tests.align.test_power_preflight | 13 | 0 | 0 | 0 |
| Total | 52 | 0 | 0 | 1 |

The skip is `test_optional_pynvml_uses_the_same_sampler_path`: "optional nvidia-ml-py is not installed; ctypes path is tested". The existing records module's 4 tests also passed, so all 56 alignment tests completed (55 passed, 1 skipped), even though some enclosing repository jobs were later cancelled.

- Completed ordinary-module groups across all final logs: 288 groups, 7,122 tests, 1 failure, 0 errors, 76 skips. These are exact completed-module counters, excluding interrupted modules; they are not a whole-suite pass count. The 76 include the one lane skip and 75 pre-existing-suite skips for unavailable Darwin/live-hardware probes, optional libraries, retained corpora/model mirrors, or registered proof/structural prerequisites. Their literal per-test reasons remain in the linked job logs.
- Ordinary shard summaries: shard 8 PASS (827 tests, 13 skips), shard 12 PASS (917 tests, 5 skips), shard 2's runner PASS (479 tests, 11 skips, though its enclosing job was cancelled), shard 4 FAIL (843 tests, 1 failure, 9 skips). Other ordinary jobs were cancelled by matrix fail-fast after already executing the lane modules.
- `python -m unittest -v tests.test_calibration_exits`: 48 tests, PASS, no skips (677.168 s).
- Crash-matrix exclusive jobs execute `python -` with the exact "Exclusive calibration-writer crash-matrix module" here-doc in the same workflow: 1 + 19 = 20 tests, PASS, no skips.
- `python -m unittest -v tests.test_docs_freshness`: 31 tests, PASS, no skips, as part of fences. Build (`python -m build`), installed-wheel smoke, state/pin/receipt fences and strict mock CLI flow also passed.

The full-suite failure is `tests.test_v5_s1_qualification.QualificationSubsetTests.test_delivered_courier_journal_assembles_with_observed_exit_and_timeout`, subtest `still_running=True`. Its existing helper at `tests/test_run_night.py:6572` measured 30.204094708999946 s against its <5 s assertion. Neither that helper, its caller, nor its threshold was changed. Root cause was not established from this seat. Fixing that failure would require work outside WRITE_SCOPE; no green full-suite claim is made.

Earlier CI evidence:
- Run [39704268162](https://github.com/mpmdw/JouleWise/actions/runs/39704268162) failed the quick-suite shard census because unittest's `align.*` names did not match inventory `tests.align.*`. The sole registry exception corrected that namespace normalization.
- Run [39705591969](https://github.com/mpmdw/JouleWise/actions/runs/39705591969), source `7fd8641d6dea558b2b0809d78c03bb473e5ace6e`, passed all then-existing 47 lane tests (46 pass, one optional skip), quick/build/fences/wheel and the exclusive jobs. Eleven completed ordinary shards ran 8,567 tests with 1 failure, 0 errors and 118 skips; the same courier helper measured 30.20556086700026 s against <5 s, and fail-fast cancelled shard 10.

The final branch tip changes only this report after the tested source above; no additional implementation/test run is implied by that report-only commit.

The managed environment never provided a shell (observed revisions 3 through 15 remained pending/starting and offline). Every attempted shell command returned no usable execution environment. These exact required local commands were NOT RUN:
- `python3 -m unittest discover -s tests/align -t .`
- `python3 -m unittest discover -s tests`
- `python3 scripts/fixture_orphan_census.py --fail-on-orphans`

No optional package could be installed from this seat, so the extra-dependent run was NOT RUN. The optional test is guarded with unittest.skipUnless, and the ctypes path executed without extras. No local checkout, local unittest result or real hardware measurement is claimed.

Draft PR [524](https://github.com/mpmdw/JouleWise/pull/524) targets the spine solely for review/CI. Its gate ledger explicitly leaves executing independent review, current-main integration, final-head green CI and the cold Fable measurement pass NOT-RUN. Static review and independently authored tests are distinguished from those merge gates.

## END-TO-END

Observed CI world output at `023c9d2` (also reproduced at `7fd8641`):

| Repeats | Estimate J | Absolute error J | Coverage | Half-width J |
|---|---:|---:|---:|---:|
| 1 | 966 | 195 | 0.25 | infinity |
| 2 | 1144.5 | 16.5 | 0.50 | infinity |
| 4 | 1161 | 0 | 1 | infinity |
| 8 | 1161 | 0 | 1 | 0.003 |
| 16 | 1161 | 0 | 1 | 0.003 |

Infinity records unidentified within-phase repeatability when there is only one replica; it is not a refusal. Single-run error is visibly larger than the repeated estimate's own half-width.

Declared multi-turn world: six 1 s turns, six local tool calls, 4,608 prefill tokens, 240 decode tokens and 48 hidden tokens. Each turn has a 75 ms 320 W prefill, 775 ms decode at 210 W with 20 W ripple, and a 150 ms 45 W tool wait. Exact 25 ms bin integration gives a 1,161 J target. A simulated 25-of-100 ms sensor runs at phase plans for 1/2/4/8/16 repeats through PowerTrace, estimate_energy and Episode JSON round-trip. The printed 0.001 W quantum gives a 0.003 J deterministic full-coverage half-width (6 s times q/2), so the 1% agreement bar is 0.00003 J and exceeds one million float ulps at this energy scale.

Coverage calibration is predeclared at seeds 0..999, 64 repeats, independent Gaussian 2 W run shifts, and nominal 95%; the allowed miss-fraction deviation is one binomial standard error sqrt(0.05*0.95/1000). The executed miss count was 52/1,000 = 0.052 against nominal 0.05, within the predeclared standard error 0.006892024376045114. No outcomes were used to select seeds or sample count.

The driver-connected variant ran the same waveform through real ctypes pointers, actual worker threads, monotonic call brackets, mapped driver timestamps, estimate_energy and Episode JSON round-trip. Eight runs retained 60 instantaneous samples each (480 observations). It returned 1160.999993675 J against 1161 J: absolute error approximately 0.000006325 J, half-width 0.10383991662699932 J and coverage 0.9999999916666666. The synthetic 100 ns clock-call increments and full driver microsecond rounding bound yield 1,050 ns window-timing bounds. The tiny uncovered boundary is retained, not rounded away. Re-estimating the serialized Episode reproduced the result bit-for-bit.

Preflight worlds executed actual fake nvidia-smi/load programs on PATH through the production ctypes sampler and process-cleanup paths: 50 W idle, 250 W load, 0.2 W ripple and 5 ms polling. The retained instant channel had 5 idle and 3 load readings; its fake-sensor/thinning phase yielded idle mean 49.8 W, sigma 0 W and threshold 49.801 W. Load peak 249.8 W gave measurement_ready=True; the 49.8 W no-movement control gave False. A separate 1,000-seed Gaussian idle world (0.5 W sigma, 64 idle readings and one held-out reading) exercised nonzero-noise predictive thresholds: 54/1,000 = 0.054 exceeded against nominal 0.05, within binomial SE 0.006892024376045111. Seeds and counts were fixed before results.

The independent oracle was authored by GPT-6-astra without viewing production duty.py. Commits `1e454773786b7de6882cbabb9ae2d35f2b24595c` and `22d85e54b54653f0a5ac8a142b128df660321a8b` preserve its authorship. It enumerates a rational interval grid rather than production's event sweep and independently inverts Student-t. It checks complete/sparse/overhanging windows, timing, unequal replica weights, 16 mixed seeded worlds and an analytic jitter fixture.

## DECISIONS I MADE

- Selected this explicitly assigned synthetic-only lane over unrelated queue work; scope overrides general repository bookkeeping. ACTIVE_STOP_CARD was NONE. No RUN_STATE/TASK_QUEUE/kernel or shared-contract edits were made.
- Created the lane from the exact spine ref after confirming no earlier lane head existed. Preserved early work through GitHub commits while the local runtime was unavailable; every branch update was a fast-forward with no force.
- Kept four separate channels per device: legacy power, field 186 instant, field 185 average, cumulative energy. Unsupported channels retain empty explanatory traces.
- Used ctypes by default and lazy optional pynvml fallback/explicit selection. ABI details were checked against NVIDIA's public go-nvml nvml.h.
- Restricted the supplied 25-of-100 ms assumption to A100/Ampere and H100/Hopper model matches, citing the shared records contract. Unknown architectures/models receive no guessed window/duty.
- Retained one-second legacy/field output averages but flagged them as not a single physical slice; the estimator does not use that incompatible window model.
- Kept query midpoint/bracket in the record, and separately mapped driver Unix-microsecond timestamps with a bracketed local wall-clock read. A full microsecond covers unspecified driver rounding. The physical window-end meaning remains a stated hardware assumption.
- Preserved exact raw mJ integers and flagged all counter decreases. The half-uint64-range criterion identifies a shortest-modular-increment wrap candidate; it does not silently join a reset.
- Cycled a minimal ceil(1/d) phase tiling to obtain actual replicas. Actual observed endpoints are never rounded to make replicas.
- Used exact Fraction geometry for coverage and kernel mismatch, and a linear sum of quantum, systematic/timing and repeatability half-widths. Missing bounds or unidentified spread produce infinity plus flags.
- Required a caller-justified instantaneous bound when coverage, smoothing or timing needs it. An enforced average power limit is not automatically that bound.
- Used a declared 95% Gaussian-run-shift Welch interval. Planned repeat_group labels use normalized auxiliary weights and center-distance widening; varying geometry is explicitly provisional.
- Rejected malformed/noncontributing runs with flags without allowing them to set another run's duration or uncertainty state.
- Preflight refuses confirmed vGPU/MIG slices. Unknown isolation evidence and parent MIG mode remain flags; whole-device passthrough is allowed.
- Derived the movement threshold from idle sigma, one quantum, predictive Student-t and Bonferroni alpha allocation. Retained support must fit inside the idle/load phase, and readiness requires movement for every selected board.
- Clock locking is opt-in, using an explicit or advertised frequency. -rgc means driver defaults, not restoration of an unobservable prior lock; this policy is recorded.
- Made samplers reusable across episode start/stop cycles with fresh immutable traces. A still-active old worker/cleanup owner produces flagged empty traces, preserving the old stop event so no old worker is revived. Balanced native ownership is tested through worker-start and cleanup-owner-start failure.
- Preflight inspects actual live workers when cleanup-owner creation fails. It transfers outstanding native references to one finalizer, or explicitly retains them if no cleanup owner can start; it never shuts NVML down under a blocked call.
- Owned load groups are terminated even after leader exit, with SIGKILL escalation. Optional CUDA runs in a killable subprocess with atomic readiness publication. Native NVML shutdown waits for outstanding calls.
- Opened draft PR 524 against the spine solely to obtain existing CI execution; it remains unmerged and is not a main-branch merge request.
- Applied the sole registry exception to the shard census's new align namespace. No timing or acceptance thresholds were loosened.
- Independent static reviews found architecture-data loss, load-child leakage, unkillable CUDA threads, shutdown races, excess virtual-mode refusal, timing attribution, invalid-run contamination and readiness/fixture races; the corresponding bounded fixes/regressions were applied. A fresh read-only reviews of NVML commit `3b54f87147cb46ccaad3aa10cb46310e2eca0ee9` and preflight commit `dc530c51762ab2f8eb676c4b366d8ba4b08a1bfa` found no further defects in their bounded lifecycle deltas. Reviewer execution was not claimed.

## CONTRACT-CHANGE

Request structured per-sample timing/flags/sensor-support metadata and separate query versus sensor-window endpoints in PowerTrace. Also request a representation of noncontiguous slices combined into a one-second NVML output average. The existing contract's slice assumption alone cannot describe that output. The lane uses JSON notes and explicit incompatible-output flags as its adapter; PIPELINE.md, records.py and interfaces.py remain byte-unchanged.

## OPEN ISSUES

- Local required commands, optional-package execution and fixture census are blocked by Cloud startup; CI execution is distinguished above.
- Whole-repository CI remains red at the existing courier timeout assertion in `tests/test_run_night.py:6572`, called by `tests/test_v5_s1_qualification.py:132`. A follow-up there is outside this lane's WRITE_SCOPE; failure and cancelled coverage are retained above.
- No real NVIDIA hardware, sensor age semantics, Gaussian idle assumptions, sensor accuracy or actual 25-of-100 ms behavior has been validated.
- Declared-phase jitter uncertainty is approximate/provisional; independent arithmetic agreement does not establish hardware calibration.
- Clock reset-to-default semantics are explicit; prior clock-lock policy cannot be queried/restored by the chosen NVML subset.
- If both cleanup-owner threads cannot start, native references remain until process exit, explicitly flagged; no shutdown races an active native call.
- Raw energy integers preserve precision near uint64 wrap that cumulative float joules cannot retain.
- Draft PR merge gates (main integration, executing independent review and cold Fable claim/measurement review) remain explicitly NOT-RUN. No merge-readiness claim is made.

## NEEDS_RULING

none
