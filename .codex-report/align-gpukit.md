# align-gpukit — FIX ROUND 2b, fix2c continuation

## SUMMARY

Continued lane/2026-10-21-align-gpukit from pushed head 7aed47856; retained the Round 2b fixes.
Late session_failed:* exceptions now remain failed/exit 3 after earlier model work, with data_complete false.
Process cleanup waits at the operator's poll cadence, bounded separately after SIGTERM and SIGKILL.
A surviving group records process_group_survived_sigkill in its model/runner or monitor receipt.
Bootstrap preserves set -euo pipefail while guarding empty arrays for macOS Bash 3.2.
Failed structural/layout validation now prints its JSON to stderr before bootstrap exits 3.
Added three regression methods, strengthened the layout diagnostic test and preserved every old assertion.
Reconciled the lead's macOS execution at 7aed47856: 78 tests, one Bash 3.2 failure; all supplied repro pass conditions held.
This seat could not launch any shell/Python process: current-head tests and repros are NOT RUN.
Each fix was committed/pushed through GitHub; PR #521 remains draft/unmerged and no rental ran.

## FILES

This continuation changed exactly these authorized paths:

- joulewise/align/gpukit/session.py: preserve late failure; bounded signal waits, positive polling and cleanup-flag propagation for runner, agent server and monitor.
- joulewise/align/gpukit/bootstrap.sh: Bash 3.2 guarded empty-array expansions; echo failed validation JSON before returning its failure code.
- tests/align/test_gpukit.py: three added methods for late failure, persistent SIGKILL survival, and cleanup receipt propagation; required poll_s in the existing group test; existing layout test additionally checks stderr.
- docs/align/gpukit.md: amended bounded cleanup semantics, late-failure exit behavior and validation diagnostics.
- .codex-report/align-gpukit.md: attributed historical lead execution, current unexecuted status and four correction hashes.

Retained kit inventory: matrix.py validates structural/record fields and provenance;
matrix.schema.json describes the campaign shape; runner_adapter.py translates to
runner coordinates; cost.py/throughput.py compute sourced planning figures;
coverage.py checks R5 trace coverage; identity.py reconciles endpoint identity;
throttle.py records board limits and thermal/power observations. The three
configs/align matrices and test_gpukit_round2.py are unchanged in this continuation.
No registry exception, protected-contract change or out-of-scope write. No local
checkout or .review3 files could be materialized because the executor never started.
Implementation/test head before this report: dd29144d2feb80f78f3dea480075d491a0ac3606.

## PUBLIC API

Modules below are under joulewise.align.gpukit. Retained signatures plus the
required SessionOptions fields and optional monitor price field:

- matrix.Run(model: str, task_pair: str, condition: str, seed: int)
- matrix.expand(matrix: Mapping[str, Any]) -> tuple[Run, ...]
- matrix.numeric_provenance(matrix: Mapping[str, Any]) -> tuple[str, ...]
- matrix.validate(matrix: Mapping[str, Any]) -> tuple[str, ...]
- matrix.load_matrix(path: Path) -> tuple[dict[str, Any], tuple[str, ...]]
- throughput.ceilings(matrix: Mapping[str, Any], gpu_class: str, model: str) -> tuple[float, float] | None
- throughput.display_number(value: float | None, *, lower_bound: bool = False) -> float | None
- cost.work_counts(matrix: Mapping[str, Any]) -> dict[str, tuple[int, int]]
- cost.memory_fit(matrix: Mapping[str, Any], gpu_class: str, model: Mapping[str, Any]) -> dict[str, Any]
- cost.calibration_slice(matrix: Mapping[str, Any]) -> dict[str, Any]
- cost.estimate(matrix: Mapping[str, Any], gpu_class: str, *, usd_per_gpu_hour: float | None = None, calibration: Path | None = None, monitor_placement: str = "none", monitor_usd_per_gpu_hour: float | None = None) -> Estimate
- cost.printable(result: Estimate) -> dict[str, Any]
- cost.main(argv: list[str] | None = None) -> int
- cost.Estimate(gpu_class, trial_rows, measured_episodes, monitor_calls, lower_bound_wall_seconds, lower_bound_gpu_hours, lower_bound_total_usd, wall_seconds, gpu_hours, usd_per_gpu_hour, total_usd, flags, model_load_count=0, monitor_gpu_hours=None, monitor_total_usd=None, generation_wall_seconds=None, calibration_basis={}, layouts=(), layout_alternatives=(), monitor_usd_per_gpu_hour=None)
  (calibration_basis uses dataclasses.field(default_factory=dict), not a shared mutable default.)
- runner_adapter.runner_matrix(matrix: Mapping[str, Any], *, model: str, endpoint: str, output_dir: Path, settings: Mapping[str, Any], session_id: str | None = None, monitor_endpoint: str | None = None, judge_endpoint: str | None = None, device_indices: Sequence[int] = ()) -> tuple[dict[str, Any], tuple[str, ...]]
- runner_adapter.write_runner_matrix(path: Path, matrix: Mapping[str, Any], *, model: str, endpoint: str, output_dir: Path, settings: Mapping[str, Any], **bindings: Any) -> tuple[str, ...]
- session.SessionOptions(matrix, output, runner_command, ready_timeout_s, poll_s, command_timeout_s, runner_timeout_s, monitor_placement, preflight_timeout_s, copy_timeout_s, stop_grace_s, preflight_command=(), ready_command=(), vllm_command=("vllm",), gpu_index=0, port=8000, destination=None, copy_kind="rsync", runner_settings=None, gpu_indices=(), monitor_base_url=None, judge_base_url=None, monitor_gpu_index=None, monitor_port=None, calibration_slice=False)
- session.whole_gpu(*, gpu_index: int, timeout_s: float) -> dict[str, Any]
- session.wait_ready(process: subprocess.Popen, endpoint: str, *, timeout_s: float, poll_s: float, ready_command: Sequence[str], log: Path, probe: Callable[[str, float], bool] = _healthy) -> tuple[str, ...]
- session.package_results(directory: Path) -> tuple[Path, Path]
- session.verify_manifest(directory: Path) -> tuple[str, ...]
- session.copy_back(paths: Sequence[Path], *, kind: str, destination: str, log: Path, timeout_s: float) -> tuple[str, ...]
- session.run_session(options: SessionOptions, *, probe: Callable[[str, float], bool] = _healthy) -> dict[str, Any]
- session.main(argv: list[str] | None = None) -> int
- throttle.parse_snapshot(xml: str) -> dict[str, Any]
- throttle.snapshot(*, gpu_index: int, directory: Path, label: str, timeout_s: float) -> dict[str, Any]
- throttle.compare(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]


Additional public functions/replay seams:

- matrix.structural_flags(matrix: Mapping[str, Any]) -> tuple[str, ...]
- session.session_layout(matrix: dict[str, Any], options: SessionOptions) -> dict[str, Any]
- session.validate_session(options: SessionOptions) -> dict[str, Any]
- session.SessionParser(argparse.ArgumentParser); error(self, message: str) -> None exits 3.
- session._stop_group(process: subprocess.Popen, *, grace_s: float, poll_s: float) -> tuple[str, ...]; bounded TERM/KILL waits return process_group_survived_sigkill if still present.
- session._runner_command(argv: Sequence[str], log: Path, *, timeout_s: float, grace_s: float, poll_s: float) -> tuple[int, bool, tuple[str, ...]]; return code, timeout marker and cleanup flags.
- session._validate_output(path: Path, *, expected_count: int, router: bool, model: str, expected_coordinates: Sequence[tuple[str, str, int]] = (), measured_devices: Sequence[int] = (), power_metrics: dict[str, Any] | None = None) -> tuple[str, ...]; coordinates override declared expected_count.
- coverage.Coverage(flags: tuple[str, ...], incomplete: bool, lost_reads: bool, max_gap_over_bar: float, max_cycle_over_two_expected: float), unchanged.
- coverage.power_coverage(episode: Episode, measured_devices: Sequence[int] = ()) -> Coverage, unchanged.
- identity.model_identity_matches(identity: str, model: str) -> bool, unchanged.

CLI requires --preflight-timeout-s, --copy-timeout-s and --stop-grace-s alongside
the previous ready/command/runner timeouts, poll cadence and monitor placement.
--validate-only prints measured_gpu_indices, monitor_gpu_index, flags and
structural_flags without output creation/hardware calls; exit 0 valid, 3 invalid.
Normal execution: physical refusal 2; no runner started or session_failed:* 3;
otherwise 0 with data_complete describing collection. Late failure stays failed
and data_complete false even after an earlier runner completed. Bootstrap echoes
invalid validate-only JSON to stderr before exiting. copy_timeout is a transfer flag beside the
retained archive; nvml_preflight_timeout is a distinct instrument-readiness refusal.

## TESTS RUN

### This continuation: Python/shell tests and repros NOT RUN

Both `pwd` and `python3 --version` were attempted independently, with later
rechecks. Every process launch failed before execution:
"No usable execution environment is available. Wait for an environment to become
available before using this tool." The environment wait remained pending; runtime
status reported starting/offline with no capabilities and unknown policy enforcement.
This was executor unavailability, not an automatic approval-review rejection.

No local git, shell, Python, Bash version check, installation, test, compilation,
manifest verification, process census or repro executed here. No extra dependency
was installed. No actual test count or skip result exists for this continuation.
The user-authorized GitHub fallback pushed all four fixes as fast-forwards with
expected-head checks and force=false.

Requested current-head commands, all **NOT RUN** here. Cwd /workspace/JouleWise,
no installed package or PYTHONPATH, TMPDIR=/tmp/gk-tmp JW_B5_SYNTHETIC_ONLY=1:

    python3 -m unittest tests.align.test_gpukit -v
    python3 -m unittest tests.align.test_gpukit_round2 -v
    python3 -m unittest discover -s tests/align -t .
    python3 -m venv /tmp/gpukit-jsonschema
    /tmp/gpukit-jsonschema/bin/pip install jsonschema
    /tmp/gpukit-jsonschema/bin/python -m unittest tests.align.test_gpukit -v
    /tmp/gpukit-jsonschema/bin/python -m unittest tests.align.test_gpukit_round2 -v
    /tmp/gpukit-jsonschema/bin/python -m unittest discover -s tests/align -t .

The source inventory is 63 test methods in test_gpukit.py and 14 in
test_gpukit_round2.py (77 methods, **not an executed discovery count**).
All three optional-jsonschema guards and the existing Bash class guard remain.
No original assertion, expected result or test method was removed; no bar widened
and no skip added. The existing real SIGTERM-ignoring group test now supplies
poll_s=0.01 as required by the amended helper; its SIGKILL/group-gone assertions
are unchanged. The bootstrap layout test adds a stderr flag assertion.

The lead's Mac uses /bin/bash 3.2.57, which treats an empty array as unset under
set -u; Bash >=4.4 accepts the old expansion. A modern Linux VM Bash cannot
demonstrate that Mac-specific failure. This VM's Bash was never launched or
versioned. The existing test_bootstrap_flag_order_and_passthrough covers the
empty-array/environment-fallback path; the lead must rerun it on the Mac.

Reviewer harness commands below were **executed by the lead's agent (local macOS)
at 7aed47856**, as supplied in the continuation brief, and are **NOT RUN by this
seat at the corrected head**. Integrated heads were gpukit 7aed47856,
runner ec4a37270 and NVML 432f14c7a. The APPENDIX harness was used exactly as
written, including --preflight-timeout-s 60 --copy-timeout-s 60 --stop-grace-s 5.
No sibling head was integrated locally here. Materialize the appendix, fetch the
NVML test fake, chmod the stubs and build /tmp/gk-integ as the brief directs.

    export TMPDIR=/tmp/gk-tmp JW_B5_SYNTHETIC_ONLY=1
    H=/workspace/JouleWise/.review3/h
    I=/tmp/gk-integ
    O=/tmp/gk-out
    NEW="--preflight-timeout-s 60 --copy-timeout-s 60 --stop-grace-s 5"
    python3 -I $H/run_world.py $I $O/e2e/nvml-shade -- configs/align/shade.json --runner-settings $H/settings-nvml.json --preflight-command '["preflight"]' --ready-timeout-s 20 --command-timeout-s 120 $NEW --poll-s 0.2 --runner-timeout-s 500 --monitor-placement external --monitor-base-url http://10.9.9.9:8000/v1 --judge-base-url http://10.9.9.9:8000/v1 --port 18431
    python3 -I $H/run_world.py $I $O/e2e/nvml-noinstant --env GK_UNSUPPORTED_FIELDS=186 -- configs/align/shade.json --runner-settings $H/settings-nvml.json --preflight-command '["preflight"]' --ready-timeout-s 20 --command-timeout-s 120 $NEW --poll-s 0.2 --runner-timeout-s 500 --monitor-placement external --monitor-base-url http://10.9.9.9:8000/v1 --judge-base-url http://10.9.9.9:8000/v1 --port 18433
    python3 -I $H/run_world.py $I $O/e2e/mock-shade -- configs/align/shade.json --runner-settings $H/settings-mock.json --preflight-command '["preflight"]' --ready-timeout-s 20 --command-timeout-s 120 $NEW --poll-s 0.2 --runner-timeout-s 500 --monitor-placement external --monitor-base-url http://10.9.9.9:8000 --port 18434
    python3 -I $H/probes.py $I $O/probes
    python3 -I $H/gate_probe.py $I $O/gates
    python3 -I $H/boot.py $I $O/boot
    python3 -I $H/throttle_probe.py $I $O/throttle
    env -C $I python3 -m joulewise.align.gpukit.cost configs/align/shade.json --gpu-class H100-SXM-80GB --calibration $O/e2e/nvml-shade
    /tmp/gpukit-jsonschema/bin/python -I $H/schema_probe.py $I


The extra interpreter path above is the prescribed replay command; the lead
reported jsonschema 4.23.0, without supplying its local venv path/install argv.
The whole repository suite was not run, as directed. The old I+W per-channel
coverage printouts are information; R5 governs completeness. Delete previous
output/archive names before rerunning a world.

New late-failure command, **NOT RUN** here; the lead ran the pre-fix version at
7aed47856 and supplied the failure described below:

    python3 -I /workspace/JouleWise/.review3/late_failure_probe.py /tmp/gk-integ /workspace/JouleWise/.review3/h /tmp/gk-out/late

### Executed by the lead's agent (local macOS) at 7aed47856

Supplied evidence, not this seat's execution: Python 3.13, no PYTHONPATH,
TMPDIR set and JW_B5_SYNTHETIC_ONLY=1. Integrated heads as above.

- `python3 -m unittest discover -s tests/align -t .` on the gpukit-only checkout:
  78 tests, 1 failure, 3 skipped. The three skips need optional jsonschema:
  MatrixTests.test_json_schema, FixArithmeticTests.test_schema_typos_and_cited_price_rows,
  and ServeTests.test_jsonschema_rejects_missing_parser (module/class names follow
  the source). With jsonschema 4.23.0: 78 tests, 1 failure, 0 skipped.
  Both failures were SessionTests.test_bootstrap_flag_order_and_passthrough:
  bootstrap.sh line 36, session_args[@]: unbound variable on Bash 3.2.57.
  Corrected by 9217d60b9fb471bc62d3bdf22fe1f182e8cbaac6; no corrected-head executed pass is claimed.
- Every supplied repro pass condition held: nvml-shade/noinstant complete,
  complete/gap controls distinguish coverage, and mock-shade incomplete only for
  episode_power_mock. Per-model power metrics are in END-TO-END.
- Three record gates each rc=0, completed_with_flags, data_complete=True,
  models_run=2, preflight_ran=True, vllm_started=True. Structural condition typo:
  rc=3, failed, models_run=0, preflight_ran=False, vllm_started=False, smi_calls=0.
- Both Qwen agents use reasoning-parser qwen3; parser/CUDA unit assertions remain.
  Calibration basis covers both models, 30 observed episodes each, no
  calibration_model_missing and generation_wall_seconds 19.0.
- Bootstrap tp2-gpu-index: rc=0, nvidia-smi indices ['0','1'], argv --gpu-index 0
  with no --gpu-indices, measured [0,1], two models, no layout/executable flag.
  fresh and tp2-layout-invalid rc=3 before venv/pip; mig-fresh and
  vgpu-monitor-fresh rc=2 before venv/pip; check-skip and skip-check rc=0.
- ready-never/ready-exit rc=3, failed; refusals rc=2; every other probe rc=0.
  The late-failure probe exposed a distinct regression: one runner_returncode
  recorded, session_failed:RuntimeError, data_complete=False, but exit 0 and
  completed_with_flags. Corrected by 459cbb90e1341f435d94299a515d8454aa2b12d0; its new unit world and final-head
  probe remain NOT RUN here.
- Modern thermal start reasons: hw_thermal_slowdown=True and
  sw_thermal_slowdown=False; throttle_hardware_active:hw_thermal_slowdown present.
  Brake counter advancement/legacy parsing retained; enforced limit 700 W in all
  three worlds. Healthy NVML completeness stays true with the thermal flag.
- mon-gpu records monitor_revision_unpinned. Existing identity/precision/monitor
  revision-key tests had no reported failure.
- Invented bare derivations list provenance flags and print lower_bound_status
  unavailable None, plan_status unavailable None, usd None, price echo 2.49.
  Committed configs: schema_errors=0, validate=[]; typo/price-row results unchanged.
- Round-1/GK2 regressions unchanged: MIG/vGPU/MIG-monitor refuse rc=2 before
  preflight/vLLM; every preflight case; no surviving worker grandchild; monitor
  on GPU 1/own port with measured devices alone sampled/preflighted; overlap flag;
  TP2 layout; runner timeout kills its grandchild; slice ten per model; failed
  copies keep the archive.
- The lead identified the unbounded busy cleanup loop and silent bootstrap
  validation stderr by inspection/repro. The amended survival-bound unit world
  and strengthened stderr assertion have not been executed by this seat.

### Source-only checks performed by this continuation

- Read the pushed report first, then PIPELINE.md, records.py and interfaces.py;
  read AGENTS.md/M0/orchestration and targeted RUN_STATE intake/status/workspace.
  ACTIVE_STOP_CARD is NONE. The explicit brief determines scope and test commands.
- Confirmed branch initially 7aed478564b93fe0bab48bab75f96d7b3ded5bfa and PR #521
  open/draft/unmerged. Read back all four implementation/test/runbook files at
  dd29144d2feb80f78f3dea480075d491a0ac3606, matching the authored bytes exactly.
- JavaScript source comparison found no deleted old assertion lines or changed
  skip guards; method inventory above is source-only. This is not Python parsing,
  test execution or proof of process-cleanup behavior.
- GitHub comparison 7aed47856...dd29144d2 was ahead-only by four commits,
  behind zero, with exactly session.py, bootstrap.sh, test_gpukit.py and the
  runbook changed. Each is inside WRITE_SCOPE. The report is the fifth path.
- The only code changes address the four continuation defects. No hardware,
  credentials, service calls from tests, rental, merge or PR-state change.

### Executed by the lead's agent (local macOS) at 2e0155dd8

Supplied brief results, **not this seat's execution**: Python 3.13, no PYTHONPATH,
TMPDIR set, JW_B5_SYNTHETIC_ONLY=1. Integrated heads: gpukit 2e0155dd8,
runner ec4a37270 (code identical to 5a5d2d200), NVML 432f14c7a. Harness was the
appendix before the new options/portable additions. No new-head pass is inferred.

- `python3 -m unittest discover -s tests/align -t .`: 56 tests, OK, 3 skipped.
  Three source guards require jsonschema; no individual skip transcript supplied.
  Venv with jsonschema 4.23.0: 56 tests, OK; separate skip count/setup argv/verbose
  module commands not supplied.
- nvml-shade completed_with_flags, data_complete true; metrics below.
  nvml-noinstant complete with unsupported instant channel and no power-missing.
  MoE noinstant calibration: 10 checked, zero power incomplete, incomplete only
  for absent router capture.
- probes gap incomplete with channel hole, complete control true. qwen3 argv for
  both agents, deepseek_r1 budget unit check and PCI_BUS_ID child checks passed.
- Cost calibration: both agents 30 observed episodes, no calibration_model_missing,
  generation_wall_seconds 19.0.
- Old defects reproduced: record gates failed rc 3/zero models; bootstrap TP2
  measured GPU 0 only; empty/readiness sessions rc 0; fresh bootstrap installed
  before argument error; invented sources printed lower bound 1500 s, plan
  6900 s, USD 4.8 and price echo 2.5. These are defect evidence, not valid estimates.
- Enforced/current 700 W with no unavailable-enforced flag; modern thermal reason
  absent before this fix.
- Round-1 regressions passed: MIG/vGPU/MIG monitor rc 2 before preflight/vLLM,
  Pass-Through, all listed preflight verdicts, readiness/worker/runner-grandchild
  cleanup, distinct monitor GPU/port with only measured devices preflighted/
  sampled, overlap flag, direct TP2 CUDA 0,1 and both preflight devices,
  10-per-model calibration, copy failures retaining archives.

## END-TO-END

The following worlds were **executed by the lead's agent (local macOS) at
7aed47856**, with runner ec4a37270 and NVML 432f14c7a. None was rerun here.
For comparison the supplied older 2e0155dd8 metrics are beside them:

| World/model | 7aed checked/incomplete/lost | 7aed max gap/B | 7aed max C/2E | 2e0155dd8 max gap/B | 2e0155dd8 max C/2E |
|---|---|---:|---:|---:|---:|
| nvml-shade Qwen3-8B | 30 / 0 / 0 | 0.724 | 0.749 | 0.836 | 0.749 |
| nvml-shade Qwen3-30B-A3B | 30 / 0 / 0 | 0.662 | 0.749 | 0.761 | 0.749 |
| nvml-noinstant Qwen3-8B | 30 / 0 / 0 | 0.668 | 0.750 | not supplied | not supplied |
| nvml-noinstant Qwen3-30B-A3B | 30 / 0 / 0 | 0.793 | 0.750 | not supplied | not supplied |

The chain is bootstrap/session -> served stub endpoint -> real runner ->
real NvmlSampler using a driver-shaped fake H100 -> shared Episode JSONL ->
R5 coverage -> receipt/manifest/archive. The fake instant field advances every
100 ms; agent/tool delays are real-time. Both NVML worlds were
completed_with_flags/data_complete true. Unsupported field 186 adds
episode_power_channel_unsupported:gpu0:power_instant without episode_power_missing.

The fixture complete control is complete. Removing 60 s from every 148 s,
12-turn/eight-tool Episode produces episode_power_coverage_hole:gpu0:power_instant
and incomplete data. The runner's own mock factories produce 30 Episodes/model,
12–13 turns and 90 verdicts/model; data_complete is false only through
episode_power_mock. Calibration uses both agents' 30 observed Episodes and
prints generation_wall_seconds 19.0. These are synthetic/mocked, not hardware.

Lead gate/bootstrap/throttle/source worlds and their exact categorical results
are recorded in TESTS RUN. No new coverage rule, data eligibility bar, planning
number or price was introduced by this continuation.

New continuation worlds, **NOT RUN**, expectations only:

- Two-model session through real CLI/session/fixture runner and shared records:
  first model completes all 30 coordinates (12 turns, eight tools, 148 virtual
  seconds/Episode), then the second readiness probe raises RuntimeError. Require
  one runner_returncode, session_failed:RuntimeError, failed/3, incomplete,
  retained manifest/archive.
- Existing real SIGTERM-ignoring group receives the operator's 50 ms grace at
  10 ms cadence, then SIGKILL, retaining exact SIGKILL/group-absent assertions.
- Injected persistent group uses grace_s=0.05, poll_s=0.01 and a controlled
  monotonic clock. It must return process_group_survived_sigkill within two
  grace periods plus one poll; every sleep must be positive. This is a policy
  scheduling bound, not a measured-quantity agreement bar.
- A real two-model/monitor fixture session wraps actual cleanup, then injects
  its survival flag to check all five cleanup call sites (two runners, two
  servers, monitor), matching receipt entries and unchanged data completeness.
- Existing TP2/one-device bootstrap world additionally requires
  runner_measured_gpu_layout_invalid on stderr before any installation.
  Existing empty-array flag-order world is retained for the Mac's Bash 3.2.

## DECISIONS I MADE

- Continue the pushed 7aed47856 head and implement only the four continuation
  defects; retain all earlier matrix/coverage/parser/source/cost fixes.
- R8/R13 late session_failed:* remains failed with data_complete false, even
  after earlier runner work. Empty-session flags and physical-refusal handling
  stay intact. No science/data inclusion rule changes.
- Amended R18 replaces the earlier infinite-wait instruction: each of SIGTERM
  and SIGKILL gets at most stop_grace_s. Sleep min(poll_s, remaining positive
  budget), never sleep(0); poll/reap without an unbounded process.wait().
  Surviving groups are flag-only observations. Propagate returned flags to
  model receipts for agent/runner groups and to monitor_server.flags for monitor.
- Preserve Linux child-subreaper/adopted-worker reaping and the existing bounded
  GPU process-release check. Longer cleanup allowance delays progression only.
- Guard all three potentially empty session_args expansions with Bash 3.2's
  guarded-array form, preserving quoting, argument identity and set -euo pipefail.
  Keep the existing Mac-failing test and all its assertions.
- Bootstrap captures validate-only's actual exit status, prints any JSON to
  stderr on failure, then exits before inventory/install. Argument-parser stderr
  remains visible when no JSON exists. Strengthen the existing TP2 layout test.
- Add late-failure/surviving-group/receipt-wiring worlds; no old expected answer,
  threshold or skip changes. Required helper poll_s arguments are wiring, not
  relaxed expectations.
- Attribute the lead's historical 78-test failure and passing repros at 7aed47856
  separately from own NOT RUN corrected-head commands. Source readback is not
  an executed test. A modern Linux Bash cannot certify the Mac-specific case;
  this VM never launched Bash.
- Preserve prior decisions: R11 executable structure vs record flags, coordinates
  determine completeness, device argv/layout shared with validation, independent
  preflight/copy limits, checkpoint=id, pinned monitor evidence, thermal flags,
  sourced-only cost outputs/exact input prices and duplicated MoE cost disclosure.
- No external spend/provider choice, hardware run, sibling change, force push,
  merge or non-draft PR transition. Scope also excludes repo bookkeeping files.

## CONTRACT-CHANGE

No change to PIPELINE.md, records.py or interfaces.py.

Retain NVML-lane requests: closing sample in stop(), and per-sample throttle/
clock-event reasons/cumulative violation durations where supported. R5 coverage
does not depend on them. Snapshot deltas cannot place events inside an Episode.
No sibling file was modified. Amended R18 is installed by the continuation brief,
not a shared-record contract change.

## OPEN ISSUES

- Current-head Python/Bash/discovery/extra tests, reviewer repros and late-failure
  probe are NOT RUN here because the executor remained starting/offline.
  The lead must rerun the supplied commands at the corrected head, including
  Bash 3.2 on macOS. Historical 7aed47856 evidence does not certify these fixes.
- New process-group survival bounds/receipt tests and late-failure test require
  execution. No process census or hardware-memory release behavior was verified.
- Budget custom driver/translator is sibling-owned; generic adapter flags/skips
  it and honestly fails when nothing ran. Hybrid truncated-thinking content-prefix
  handling remains budget-owned.
- Factory registration, staged public data/model revisions, router capture and
  real serving/layout/headroom still require integrated/live preflight.
- Estimates need sourced setup/load/wait/efficiency or complete receipt calibration
  including budget strata. Unknowns stay unavailable. Ed must approve provider,
  spend/cap/layout/precision and matrix choice before rental.
- Independent final review, CI, merge and NVML requests remain lead-owned.
  PR #521 stays draft/unmerged; no spend/provider approval was presumed.

## NEEDS_RULING

none. The continuation's four explicit corrections and amended R18 determine
this build. No new measured number or data-eligibility choice forces a question.

## FIX LOG

"fixed" below means implementation pushed. The round-1 lines are retained as
historical entries, including their then-NOT RUN disclosures; they do not
describe this continuation's test status. Supplied execution at a37655231 is
recorded in TESTS RUN and does not establish a corrected-head pass. Earlier
checkpoints remain:

- GK-1: fixed eca533727ce543330aa6bfeacd2925d0cfbeb397 (follow-ups 0c402afe, ada1c7e8).
- GK-2: fixed d9a2d7cc185d5684c58b30b0908aa0935a61658e; C2 readiness amendment in 18d3beb196989397b415c6945b2356f3531bb359.
- GK-3: fixed a4c9931ac52efdf4cb186c34ff9c00a6d959e738.
- GK-4: fixed 2b1307dc8a6ec73e4f6deec9e981e34b0298169b.
- GK-5: fixed a4c9931ac52efdf4cb186c34ff9c00a6d959e738 (partial calibration/final limitations 6fac9635; stale input-flag follow-up C1 in 746fc6f9cbf8788a9cefe0028aaef660e660d266).
- GK-6: fixed 71190036ca3761e6b1d78470ee5081b1365ef2df; old bounds.py/bounds_noembed.py are expected incompatible with null volumes/new counts, NOT RUN.
- GK-7: fixed 2b1307dc8a6ec73e4f6deec9e981e34b0298169b (explicit mock identity follow-up 6fac9635).
- GK-8: fixed 71190036ca3761e6b1d78470ee5081b1365ef2df.
- GK-9: fixed 2b1307dc8a6ec73e4f6deec9e981e34b0298169b.
- GK-10: fixed 2b1307dc8a6ec73e4f6deec9e981e34b0298169b (disjoint-set assertion 6d79f95d).
- GK-11: fixed eca533727ce543330aa6bfeacd2925d0cfbeb397.
- GK-12: fixed a4c9931ac52efdf4cb186c34ff9c00a6d959e738.
- GK-13: fixed 71190036ca3761e6b1d78470ee5081b1365ef2df.
- GK-14: fixed 71190036ca3761e6b1d78470ee5081b1365ef2df.
- GK-15: fixed a4c9931ac52efdf4cb186c34ff9c00a6d959e738.
- GK-16: info, no change.
- GK-S: fixed 1db023047da5e79c9f00334012845f9d487b873a (board-limit follow-up 16f5a8f7).

- C1: fixed 746fc6f9cbf8788a9cefe0028aaef660e660d266. Recompute evaluated efficiency/token-volume flags, retain static context; original failing arithmetic test unchanged; add missing/supplied/partial-input regression. NOT RUN here.
- C2: fixed 18d3beb196989397b415c6945b2356f3531bb359. Require measurement_ready is True; flag nvml_measurement_not_ready and refuse before all model starts otherwise. Expanded report/CLI refusal tests and runbook. The previous false-readiness-proceeds assertion was changed under the owner's explicit R4 amendment, not weakened to pass a test. NOT RUN here.
- C3: execution unavailable; recorded the director's bed93a095 evidence separately and all own tests/repros NOT RUN. No result is claimed.

Reviewer .review1 copy changes: none materialized in this continuation because
the executor is unavailable. The director's authorized adaptations, to reuse:

- SessionOptions calls: runner_timeout_s and monitor_placement="none"; hang uses
  runner_timeout_s=5.0. ready_probe CLI adds --runner-timeout-s 5
  --monitor-placement none. No mode/world/printed check changes.
- boot_probe environment: JOULEWISE_PROBE_TIMEOUT_S=30, JOULEWISE_GPU_INDICES=0.
- gkfix.py task factory: remove the obsolete config["task_pair"] assertion;
  task identity comes through FactoryContext. settings-gk explicitly supplies
  endpoint_config={"model":"{agent_model}","base_url":"{agent_base_url}"} and
  sampler_config={"interval_ns":"{interval_ns}"}.
- Runner mock settings: clock={"factory":"mock.clock"},
  clock_domain="mock.monotonic", so ScriptedEndpoint advances the shared clock.
- preflight-ok writes {"fixture":true,"refused":false,"measurement_ready":true,
  "flags":[]} to the path after --out. This is the director-authorized harness
  repair for R4; stdout-only original cannot satisfy the production contract.
- Integrated command lines add the required runner-timeout and explicit monitor
  placement. External placement in the director's mock control is identified in
  TESTS RUN; do not infer that result for a new none-placement run.

No worlds or printed checks were weakened, no existing skip added, and no
out-of-scope registry or fixture-signature file changed. NEEDS_RULING is retained
unchanged from bed93a095.


### Round 2

"fixed" names implementation commits. The lead subsequently executed these fixes
at a37655231; results are attributed above. This seat did not execute a test.

- GK2-1: fixed e47d3282ccb60f3e3b49e0cf26ac14263b48fca1.
- GK2-2: fixed d48ecf855b9781286140c2da1d53ad706ad04114.
- GK2-3: fixed af3f48945f6de3aabae67ca7b8b4e66fc44fa666.
- GK2-4: fixed a33ff4f785206e6be8a57182f355962f721de658.
- GK2-5: fixed b259f5f04fffb822a01616303cf4088608debce6.
- GK2-6: fixed 2f5fac98641b346e62862de5baab2364d3f20b23.
- GK2-7: fixed 67fe51e1980801c753ee5ce048deb2304a3f37a8.
- GK2-8: info, no change.

R5 follow-ups: 163f943ffe252451ae5154e8a5beb199177e4caa initializes metrics for every model
and reconciles the old runbook meaning; 22fbf2fc3452de834420645635f7cf07c4f96320 strengthens the
new probes to four channels and checks interior offset cancellation.
R6 quotation follow-up: b14078f2ae520137eb171d6c494acaac84bbd8ea uses the supplied Qwen3-8B
example verbatim while preserving each hybrid model's pinned card URL.

Only changed old expected answer: test_placeholder_configs_and_per_session_ids
now expects episode_power_coverage_cycle:gpu0 and the generic incomplete flag
alongside episode_power_mock. Its two samples are 1 s apart at I=100 ms,
so C=1 s > 2E=200 ms under R5. The declared mock still has no model-mismatch
flag. The complete positive-control world retains all boundary samples and its
old assertions byte-for-byte. The per-token weight and independent arithmetic
tests are also byte-identical to 28b9a22f4. No other old expected answer, assertion
bar or skip changed. Added environment assertions apply to both served roles.

Fix2c correction to GK2-1's test:
eb2b446ad7a459973c0fd5b45dee147c01ee217e passes clock_mappings into the
Episode constructor through the test helper. The world is still a 25 ms
power_instant interior gap on a sensor clock with 100 ms mapping half-width.
Every assertion is retained: incomplete, hole present, edge absent. No expected
answer or bar changed. This fixes the constructor error found in the lead's
56-test run, but the corrected test is NOT RUN by this seat.

Fix2c evidence reconciliation: recorded the lead's local macOS execution at
a37655231 in SUMMARY, TESTS RUN and END-TO-END, replacing blanket pending labels
for the covered worlds/replays/regressions. Discovery was 56 tests, one error,
three skips; extra-dependent tests/schema probe remained unexecuted. This seat's
shell never launched, so none was rerun here.

Round-2 appendix changes: none. No new CLI option or harness-call adaptation.
The lead used the unchanged appendix with runner 52999e6a2 and nvml 95a37eef8;
no .review2 files were materialized or committed by this seat. Source inspection
and GitHub readback are not test execution.


### Round 2b

"fixed" means pushed implementation. Repro results below were **executed by the
lead's agent (local macOS) at 7aed47856** with runner ec4a37270/NVML 432f14c7a,
not by this continuation. All corrected-head tests/repros here are **NOT RUN**
because no executor launched. Every earlier round-1/Round-2 FIX LOG line above
is retained verbatim.

- GK2B-1: fixed e47d3282ccb60f3e3b49e0cf26ac14263b48fca1 (GK2-1; constructor correction eb2b446ad), lead repro re-run at 7aed47856: nvml-shade/noinstant complete, every model 30 checked/0 power incomplete/0 lost; unsupported instant flag without missing-power; gap incomplete and complete control true. R5 unchanged; metrics in END-TO-END.
- GK2B-2: fixed 91612a5c334bc170dd2c1690ba38084da1152749; adapter follow-up 4a2b91948d23b3c83a7db070d2a2becddf9205f3; coordinate/record follow-up 55fdd026f6394060985f88ea64ae40ba5c418162; lead repro re-run at 7aed47856: all three record gates run two models/rc0/complete; structural typo rc3 before hardware (smi_calls=0).
- GK2B-3: fixed d48ecf855b9781286140c2da1d53ad706ad04114 (GK2-2), lead repro re-run at 7aed47856: both agents qwen3; existing deepseek_r1 parser test retained with no reported failure.
- GK2B-4: fixed af3f48945f6de3aabae67ca7b8b4e66fc44fa666 (GK2-3), lead repro re-run at 7aed47856: 30 observed/model, no calibration_model_missing, generation_wall_seconds 19.0.
- GK2B-5: fixed bf7155b7059af930a1eabbec70e1f196948a339b; layout regression 55fdd026f6394060985f88ea64ae40ba5c418162; lead repro re-run at 7aed47856: TP2 contiguous devices [0,1], argv --gpu-index 0 preserved, two models; MIG/invalid-layout before installation. Fix2c corrections: 9217d60b9fb471bc62d3bdf22fe1f182e8cbaac6 guards every possibly empty session_args expansion for Bash 3.2; dd29144d2feb80f78f3dea480075d491a0ac3606 echoes failed validation JSON/stderr. The lead's discovery exposed Bash 3.2 failure; corrected-head Mac test NOT RUN here.
- GK2B-6: fixed d8d838475ae350079b8c4825d7c2fc01ac9263af; preinstall wiring bf7155b7059af930a1eabbec70e1f196948a339b; budget CLI regression bce45811a23ab8e9d09a76e78bedcae4f7b26d11; lead repro re-run at 7aed47856: fresh/layout rc3 without install, readiness failures failed/3, refusals/2, other probes/0. Fix2c corrections: 459cbb90e1341f435d94299a515d8454aa2b12d0 preserves failed/3/data_complete false after a late session_failed:* even with one prior runner; 9217d60b9fb471bc62d3bdf22fe1f182e8cbaac6 and dd29144d2feb80f78f3dea480075d491a0ac3606 correct Bash 3.2 and silent validation. Added late two-model unit world; strengthened stderr assertion; corrected-head tests/late_failure_probe NOT RUN here.
- GK2B-7: fixed 614223ceae52ef88fc8a96c73ae7d208dcf483db; independent preflight/copy limits and flags unchanged. Lead 78-test runs at 7aed47856 had only the unrelated Bash failure (three optional skips without jsonschema); timeout tests had no reported failure. Corrected-head rerun NOT RUN here.
- GK2B-8: fixed 1df60966407e4db2f7be12308209fd6491f23f42 (thermal); enforced half fixed b259f5f04fffb822a01616303cf4088608debce6 (GK2-5), lead repro re-run at 7aed47856: hardware thermal active flagged, software false, brake advancement/legacy retained and enforced 700 W in all three; healthy NVML completeness unchanged.
- GK2B-9: fixed 67fe51e1980801c753ee5ce048deb2304a3f37a8 (GK2-7), lead repro re-run at 7aed47856: child-environment assertions had no reported failure; round-1 measured/monitor device behavior unchanged.
- GK2B-10: fixed 991ae09e2783a225c06f7bb6c5855a830220af86; lead repro re-run at 7aed47856: mon-gpu flags monitor_revision_unpinned; checkpoint/precision/revision-key tests had no reported failure.
- GK2B-11: fixed 8e9c3ac375c78b3b7ba724fbf6f5821535824e44; malformed-planning guard 55fdd026f6394060985f88ea64ae40ba5c418162; lead repro re-run at 7aed47856: invented-input provenance flags, lower bound/plan unavailable, USD None; all committed configs schema_errors=0 validate=[], typo/price-row results unchanged.
- GK2B-12: fixed 1a6b2d91f7136ad09e810ea7098e1373941e2992; GPU regression 55fdd026f6394060985f88ea64ae40ba5c418162; lead repro re-run at 7aed47856: ready-spawn/hang no surviving grandchild. Fix2c correction 8994e128a49167f260784b8d2aa4a120c1f95b70 implements amended R18: positive poll cadence, at most one grace per signal, surviving-group flag returned/recorded for every caller. Added persistent-group bound and receipt-wiring worlds; existing SIGKILL/group-gone assertions unchanged, adding required poll_s only. Corrected-head reruns NOT RUN here.
- GK2B-13: fixed f1850a8a79c121ae4e72d83bbd401b418f29f51e (price/runbook); HF half fixed a33ff4f785206e6be8a57182f355962f721de658 (GK2-4), lead repro re-run at 7aed47856: price echo 2.49; committed configs clean. HF configs unchanged; runbook stays procedural.
- GK2B-14: info, runbook paragraph 2b7490533cd58271d49c0c06b299f766e4491392; no code change for overlap; 30B MoE coordinates measured twice if both matrices run.

Old-test changes in Round 2b: no assertion deleted/bar widened/skip added/old
expected result changed. Both modules supply required options. Fake installation
interpreter returns validate-only JSON. planning_fixture gets dated synthetic
sources without numerical changes. Existing readiness failure additionally
asserts failed/session_ran_no_model under R13. New budget skip world supplies
valid settings to reach all adapters, then asserts failure and CLI exit 3.

Fix2c changes to old tests: existing _stop_group calls supply poll_s=0.01;
existing bootstrap layout failure additionally asserts its named flag on stderr.
Every old assertion remains. Three new test methods cover late failure, bounded
survival and flag propagation. No .review3 appendix edits/files materialized or
committed. Own tests and repros remain NOT RUN; supplied lead results at 7aed47856
replace pending labels only for that head.
