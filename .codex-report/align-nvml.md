# NVML lane implementation report

## SUMMARY

Implemented stdlib ctypes NVML power and cumulative-energy sampling.
Separate device workers retain query brackets, sensor facts and raw counter discontinuities.
Added duty-window pooling with coverage, quantization and run-repeatability uncertainty.
Declared phase labels preserve scheduler jitter through a normalized auxiliary interval.
Added whole-GPU preflight, opt-in clock commands, owned load cleanup and JSON evidence.
Added realistic multi-turn worlds, ctypes/executable fakes and an independent numerical twin.
Documented the first rented-GPU session without performing hardware measurements.
Executed lane tests pass in CI; the final connected-path/lifecycle additions are awaiting CI.
Shared contracts and the existing NVIDIA adapter are unchanged.

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

Executed through GitHub CI (Python 3.13, stdlib-only), source `7fd8641d6dea558b2b0809d78c03bb473e5ace6e`:
- NVML: 14 tests, 0 failures/errors, 1 skip.
- Duty worlds: 9 tests, 0 failures/errors/skips.
- Independent twin: 12 tests, 0 failures/errors/skips.
- Preflight: 12 tests, 0 failures/errors/skips.
- Thus 47 lane tests: 46 passed and 1 optional-package skip. The existing records module's 4 tests also passed.
- The skip is `test_optional_pynvml_uses_the_same_sampler_path`: "optional nvidia-ml-py is not installed; ctypes path is tested".

Final connected-path/lifecycle regressions are not yet executed; this checkpoint precedes the final CI run.

The managed environment repeatedly remained pending/starting (observed revisions 3 through 11); every attempted shell command returned no usable execution environment. No local checkout, pip install, local unittest run or live hardware measurement is claimed.

Existing GitHub CI was invoked with draft PR <https://github.com/mpmdw/JouleWise/pull/524>, targeting the spine branch. At source head `7fd8641d6dea558b2b0809d78c03bb473e5ace6e`, run <https://github.com/mpmdw/JouleWise/actions/runs/39705591969>:
- `python3 scripts/quick_suite.py --tier quick --workers 4`: passed after the census namespace addition.
- `python -m compileall -q joulewise tests`: passed in all twelve ordinary shards before execution.
- Full stdlib suite ran through the unchanged `.github/workflows/ci.yml` embedded `python -` shard driver: `shard_tests.run_units(partitions[index - 1], count, index)`, using stdlib `unittest.TestLoader`/`TextTestRunner`. Ten ordinary shards passed; shard 4 failed an existing timeout assertion; shard 10 was cancelled by matrix fail-fast. The eleven completed ordinary shards ran 8,567 tests with 1 failure, 0 errors and 118 skips (including the optional lane skip above). Base-suite skip reasons are retained in the linked job logs.
- Exclusive commands `python -m unittest -v tests.test_calibration_exits` and the existing embedded crash-matrix shard driver passed: 48 calibration-exit tests and 20 crash-matrix tests, no skips.
- The failure outside this lane was `tests.test_v5_s1_qualification.QualificationSubsetTests.test_delivered_courier_journal_assembles_with_observed_exit_and_timeout`, subtest `still_running=True`: observed duration 30.20556086700026 s failed its existing <5 s assertion. The failing assertion is in the existing courier helper at tests/test_run_night.py:6572. Neither file nor its thresholds was changed. Its root cause was not established from this seat. This is an observed failure, not a claim of a green whole-repository suite.
- Build, installed-wheel smoke, state/pin/doc/receipt fences and strict mock CLI flow passed.

Required local commands remain blocked by workspace startup:
- `python3 -m unittest discover -s tests/align -t .`
- `python3 -m unittest discover -s tests`
- `python3 scripts/fixture_orphan_census.py --fail-on-orphans`

Optional nvidia-ml-py is guarded by unittest.skipUnless. No optional package was installed from this seat; the extra-dependent run is pending a usable environment. The default path needs no extras.

## END-TO-END

Observed CI world output at `7fd8641`:

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

The driver-connected variant uses the same waveform through real ctypes pointers, worker threads, mapped driver timestamps, estimate_energy and record serialization. Preflight worlds execute fake nvidia-smi/load programs on PATH, with a 50 W idle baseline, 250 W load, 0.2 W ripple, 5 ms polling, and a no-movement control. Separate 1,000-seed Gaussian idle worlds test the predictive criterion's declared 5% nominal rate.

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
- No real NVIDIA hardware, sensor age semantics, Gaussian idle assumptions, sensor accuracy or actual 25-of-100 ms behavior has been validated.
- Declared-phase jitter uncertainty is approximate/provisional; independent arithmetic agreement does not establish hardware calibration.
- Clock reset-to-default semantics are explicit; prior clock-lock policy cannot be queried/restored by the chosen NVML subset.
- If both cleanup-owner threads cannot start, native references remain until process exit, explicitly flagged; no shutdown races an active native call.
- Raw energy integers preserve precision near uint64 wrap that cumulative float joules cannot retain.
- Draft PR merge gates (main integration, executing independent review and cold claim/measurement review) belong to the integrating lead. No merge-readiness claim is made.

## NEEDS_RULING

none
