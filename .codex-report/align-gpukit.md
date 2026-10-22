# align-gpukit — FIX ROUND 2b

## SUMMARY

Continued lane/2026-10-21-align-gpukit from 2e0155dd8; preserved the earlier GK2 fixes.
Split structural matrix failures from record-only flags throughout session and runner translation.
Bootstrap now validates before installation and checks the session's complete measured/monitor GPU pool.
Empty sessions and argument errors exit 3; physical refusals retain exit 2 and precedence.
Added independent preflight/copy limits, explicit process-stop grace, GPU-release checks and thermal flags.
Bound served identity to checkpoint, recorded precision/monitor revision, and masked unsourced cost inputs.
Prices echo exactly; the runbook is procedural and explains repeated MoE coordinates and cost.
All own Python, shell, stdlib/extra tests and reviewer repros are NOT RUN: no executable environment launched.
Pushed each implementation step through the authorized GitHub fallback; PR #521 stays draft, with no rental or merge.

## FILES

Round 2b changed these authorized paths:

- joulewise/align/gpukit/matrix.py: structural_flags(), full record validation, served checkpoint identity, dated public citations and key-referencing derivations.
- joulewise/align/gpukit/runner_adapter.py: preserve record flags while translating executable coordinates; safe optional campaign label.
- joulewise/align/gpukit/session.py: shared validate-only/layout, coordinate counts, no-run failure/exit 3, independent required time limits, group reaping/GPU release, precision/monitor pins and malformed optional flag handling.
- joulewise/align/gpukit/bootstrap.sh: preserve device argv, environment fallback only without flags, validate/check full pool before venv/pip, exit 2 for isolation and 3 for arguments.
- joulewise/align/gpukit/cost.py: mask unsourced inputs/decode dependencies while retaining independent figures, exact agent/monitor input prices, tolerant optional calibration label.
- joulewise/align/gpukit/matrix.schema.json: reserved-host URL pattern and access-date format/range shape.
- joulewise/align/gpukit/throttle.py: hardware/software thermal reasons and software thermal counter; prior enforced-limit behavior retained.
- tests/align/test_gpukit.py: 22 added source methods; old fixture sources/policy arguments and fake install interpreter's validate-only response updated; every old assertion retained.
- tests/align/test_gpukit_round2.py: three newly required policy arguments in CLI/Python calls; no assertion/bar/skip changed.
- docs/align/gpukit.md: run procedure, codes, timeout derivations, structural/record distinction, identities, prices, thermal flags and MoE duplicate-cost paragraph; seat status removed.
- .codex-report/align-gpukit.md: current evidence handoff; entire earlier FIX LOG retained verbatim plus Round 2b.

Configs, coverage.py, identity.py and throughput.py are unchanged. No registry
exception, sibling/protected-contract edit or out-of-scope write. No .review3
materialization or commit: the executor never launched.
Implementation/test head before this report: bce45811a23ab8e9d09a76e78bedcae4f7b26d11.

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
- session._stop_group(process: subprocess.Popen, *, grace_s: float) -> None; returns after group disappearance.
- session._validate_output(path: Path, *, expected_count: int, router: bool, model: str, expected_coordinates: Sequence[tuple[str, str, int]] = (), measured_devices: Sequence[int] = (), power_metrics: dict[str, Any] | None = None) -> tuple[str, ...]; coordinates override declared expected_count.
- coverage.Coverage(flags: tuple[str, ...], incomplete: bool, lost_reads: bool, max_gap_over_bar: float, max_cycle_over_two_expected: float), unchanged.
- coverage.power_coverage(episode: Episode, measured_devices: Sequence[int] = ()) -> Coverage, unchanged.
- identity.model_identity_matches(identity: str, model: str) -> bool, unchanged.

CLI requires --preflight-timeout-s, --copy-timeout-s and --stop-grace-s alongside
the previous ready/command/runner timeouts, poll cadence and monitor placement.
--validate-only prints measured_gpu_indices, monitor_gpu_index, flags and
structural_flags without output creation/hardware calls; exit 0 valid, 3 invalid.
Normal execution: physical refusal 2; no runner started 3; otherwise 0 with
data_complete describing collection. copy_timeout is a transfer flag beside the
retained archive; nvml_preflight_timeout is a distinct instrument-readiness refusal.

## TESTS RUN

### This seat: all Python/shell checks NOT RUN

Initial and later attempts of `pwd` and `python3 --version` were rejected
before process launch: "No usable execution environment is available. Wait for an
environment to become available before using this tool." Runtime status was
pending/offline, no capabilities, network-policy state unknown. This is executor
unavailability, not an automatic approval rejection.

No shell, Python, local git, installation, compilation, test, manifest verification,
process census or repro executed here. No local checkout, harness chmod, integrated
tree or NVML fake extraction was possible. No extra dependency was installed.
All commands below are **NOT RUN**, counts/failures/actual skips unknown.

Requested cwd /workspace/JouleWise, uninstalled package, no PYTHONPATH, with
TMPDIR=/tmp/gk-tmp JW_B5_SYNTHETIC_ONLY=1:

    python3 -m unittest tests.align.test_gpukit -v
    python3 -m unittest tests.align.test_gpukit_round2 -v
    python3 -m unittest discover -s tests/align -t .
    python3 -m venv /tmp/gpukit-jsonschema
    /tmp/gpukit-jsonschema/bin/pip install jsonschema
    /tmp/gpukit-jsonschema/bin/python -m unittest tests.align.test_gpukit -v
    /tmp/gpukit-jsonschema/bin/python -m unittest tests.align.test_gpukit_round2 -v
    /tmp/gpukit-jsonschema/bin/python -m unittest discover -s tests/align -t .

Source inventory: 60 methods in test_gpukit.py, 14 in test_gpukit_round2.py
(74 source methods, **not an executed count**). All original 38 + 14 remain.
No original assertion line removed or skip added. Three optional-jsonschema
guards retain "optional jsonschema is not installed"; the existing SessionTests
Bash guard retains "bootstrap requires Bash". No new dependency.

Reviewer repros, **all NOT RUN**: materialize the appendix at .review3/h verbatim,
chmod h/pywrap and h/bin/*, and fetch runner/NVML and nvml_fake_base.py as directed.
Build /tmp/gk-integ from this lane plus the four runner files and NVML power/.
No sibling patch or integrated sibling head was used here. Record actual SHAs
on execution; the supplied prior run used runner ec4a37270 and NVML 432f14c7a.

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

Delete previous output/archive names before replay. Use subprocess cwd for cost
if env -C is unavailable. The old I+W per-channel lines are information, not R5
pass conditions. The appendix already supplies all three required new options.
No appendix file was changed or materialized here. The whole repository suite
was intentionally not run, as directed.

Actually performed through GitHub/JavaScript, **source checking only**:

- Read report first, shared contracts, AGENTS.md, M0, orchestration, targeted
  RUN_STATE intake/status/workspace and empty TASK_QUEUE. ACTIVE_STOP_CARD is NONE.
  User scope overrides repo bookkeeping/full-suite instructions.
- Confirmed initial head 2e0155dd8 and PR #521 open/draft/unmerged. Each commit
  parents the prior head; each lane update uses expected_sha and force=false.
- Read back ten code/test/runbook files at 4a2b91948, exactly matching authored
  text; later source follow-ups are in FIX LOG and remain unexecuted.
- Compared prior/current test method names, assertion lines and skip guards:
  no old method/assertion line removed or skip added.
- Parsed unchanged configs/schema as JSON. A separate JavaScript source scan
  found no numeric leaf lacking a citation or key-referencing formula in the
  three configs. This is not Python validate(), jsonschema or schema_probe.
- Branch comparison was ahead-only and contained only authorized paths.

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

No Python/shell world ran here. These were **executed by the lead's agent
(local macOS) at 2e0155dd8**, with the integrated heads above:

| World/model | Lead checked | Lead power incomplete | Lead lost reads | Lead max gap/B | Lead max C/2E | Own rerun |
|---|---:|---:|---:|---:|---:|---|
| nvml-shade Qwen3-8B | 30 | 0 | 0 | 0.836 | 0.749 | NOT RUN |
| nvml-shade Qwen3-30B-A3B | 30 | 0 | 0 | 0.761 | 0.749 | NOT RUN |
| nvml-noinstant each model | per-model count not supplied | complete | not supplied | not supplied | not supplied | NOT RUN |

Driver-shaped H100 fields advance every 100 ms; real NvmlSampler/runner use a
real-time endpoint with tools. Unsupported field 186 stays a flag. The 60 s hole
in each 148 s fixture Episode is incomplete; its complete control passes. R5
coverage code/factors are unchanged. The supplied mock world has 30 Episodes per
model, 12–13 turns and 90 verdicts; mock power alone makes all 30 incomplete.
No new coverage margin or already-fixed-id repro is measured here.

New authored worlds below are **NOT RUN**, expected behavior only:

- Existing production-shaped fixture: 5 pairs x 2 conditions x 3 seeds x 2 models
  = 60 Episodes, 12 turns, eight 2 s tools, 40,000 prefill/8,000 decode tokens,
  148 virtual seconds, 100 ms cadence, 1,481 samples/Episode, alternating 1 W
  fixture noise. Nominal hand energy: 148*280 - 8*2*80 = 40,160 J.
- Provenance/stale-count/malformed-workload worlds traverse load/validate -> real
  adapter -> stub vLLM -> fixture runner -> shared Episode JSONL -> coordinate/
  power validator -> receipt/manifest/archive. Two-seed stale world has 20 rows
  per model/40 total while old 60/180 declarations stay flagged; data is complete.
- Condition typo/differing served checkpoint fail before hardware; malformed
  optional flag metadata remains record-only.
- Budget uses valid settings, reaches all four actual adapters, then skips with
  budget_runner_adapter_required; failed/session_ran_no_model, CLI exit 3.
- TP2 bootstrap checks second-device MIG before install and fails short explicit
  layout before install, using actual shell/session validation.
- Preflight sleep 0.2 s vs explicit 0.05 s preflight policy refuses distinctly.
  Short probes at 0.05 s with preflight allowance 30 s still collect. A sleeping
  copy expires separate 0.05 s copy policy and retains the archive.
- SIGTERM-ignoring group must vanish after explicit 0.05 s grace/SIGKILL.
  Persistent GPU process_info after 1 s fixture cleanup allowance is only a flag.
- Active hardware/software thermal reasons traverse session/snapshots without
  changing completeness. Exact categorical fields/counter strings are identities.
- Invented unsourced inputs suppress dependent figures; unsourced setup alone
  leaves the independent lower bound. Old synthetic arithmetic inputs/assertions
  are unchanged and now cited. Operator prices 2.49/3.79 echo exactly.

Scheduling policies above are test parameters, not sensor/uncertainty bars.
All own stdlib/extra/reviewer worlds remain NOT RUN; no paid/hardware evidence
or current-head pass is claimed.

## DECISIONS I MADE

- Continue existing lane at 2e0155dd8; no restart, force push, merge, draft-state
  change or rental. Use explicit GitHub fallback, retain honest NOT RUN labels.
- R11 structural check examines executable fields/coordinates only; full validate
  keeps citations/counts/planning flags. Carry separation through adapter and
  session skip logic. Optional malformed flag metadata cannot stop collection.
- Expected counts come from expanded coordinates, including inside validator;
  record flags never change data_complete. Optional campaign labels have a safe
  fallback and do not select scientific coordinates.
- R13 run means a model receipt with runner_returncode. No run fails/3; physical
  refusal has precedence/2; any run completes/0 with data_complete for data faults.
  Argument errors and invalid validate-only inputs use 3.
- Share GPU layout between validation/execution. Preserve GPU flags exactly;
  environment applies only without either flag. Preinstall checks include every
  measured/monitor index; argument-free check-only remains a literal index check.
- Require separate preflight/copy/stop policy values, no invented defaults.
  Preserve short-probe timeout; distinguish expiry from launch failure. Runbook
  uses the ruled 22 s plus startup and 44e3*N*T*G copy derivations.
- R18 stops complete groups with explicit grace. Linux process-local child
  subreaper (prctl PR_SET_CHILD_SUBREAPER=36) is enabled before spawning so adopted
  worker zombies can be reaped by group without depending on container PID 1.
  Poll group disappearance after SIGKILL. GPU-release timeout remains flag-only.
  Zero sleeps are scheduler yields, not scientific time bars.
- R15 requires checkpoint=id only for served entries; cost alternatives retain
  checkpoints. Record precision and monitor revision/unpinned flag. Preserve
  BF16/4 default; an FP8 rental is its own checkpoint id, already ruled.
- R16 adds exactly two thermal reasons/software duration counter; retain enforced
  limits and flag-only throttle semantics.
- R17 rejects reserved/private/local hosts and invalid ISO dates, and requires
  real key references in derivations. Mask unsourced inputs/decode dependencies
  before cost arithmetic; preserve independent figures/calibration observations.
- R19 echoes input prices exactly; derived display stays two significant digits
  with downward lower bounds. Remove all seat/run status from the runbook.
- Keep every old test method/assertion/bar/skip. Only required policy arguments,
  synthetic citation metadata and installation-stub validate-only protocol change
  old fixtures. Add stronger no-run assertions; no old expected answer changed.
- Explain duplicated MoE coordinates/cost; operator selects matrices. No config
  numeric input/count or R5 bar changes. Earlier parser/HF/identity/CUDA/enforced
  fixes remain intact and require no replacement.
- Separate source audits, historical lead evidence and NOT RUN final-head checks.
  No new measured contradiction is inferred from an unavailable executor.

## CONTRACT-CHANGE

No change to PIPELINE.md, records.py or interfaces.py.

Retain NVML-lane requests: closing sample in stop(), and per-sample throttle/
clock-event reasons/cumulative violation durations where supported. R5 coverage
does not depend on them. Snapshot deltas cannot place events inside an Episode.
No sibling file was modified.

## OPEN ISSUES

- All final-head Python/shell tests, verbose/discovery runs, jsonschema setup/
  reruns and reviewer repros are NOT RUN. Executing lead must materialize appendix,
  build integration, record sibling SHAs and run exact commands before acceptance.
  Source inspection is not process-cleanup or final-head correctness evidence.
- Prior 56-test/world results at 2e0155dd8 establish earlier fixes only. The old
  a37655231 constructor error below is historical; supplied 2e0155dd8 passed after
  eb2b446ad corrected it.
- Budget custom driver/translator is sibling-owned. Generic adapter still flags/
  skips it and now fails honestly when nothing ran. Hybrid truncated thinking
  output still needs budget content-prefix handling.
- Factory registration, staged public data/model revisions, router capture and
  actual serving/layout/headroom need integrated rehearsal/live preflight.
  Serving pins are operator inputs; hermes provenance stays explicitly not fetched.
- Rental estimates need sourced setup/load/wait/efficiency or complete receipt
  calibration including budget strata. Unknowns stay unavailable. Ed must approve
  provider/spend/cap/layout/precision/matrix choice before any rental.
- NVML requests, independent final review, CI and merge remain lead-owned;
  PR #521 stays draft/unmerged. No spend or provider approval was presumed.

## NEEDS_RULING

none. R11–R19 determine this build. Provider/spend and eventual distinct served
configuration selection are pre-rental operator approvals, not unresolved code/
count rulings. No new measured numbers force a question.

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

"fixed" means pushed implementation, not an executed pass. All own tests and
repros below are **NOT RUN** because no executor launched. Earlier lead results
at 2e0155dd8 are attributed above; every earlier FIX LOG line is retained verbatim.

- GK2B-1: fixed e47d3282ccb60f3e3b49e0cf26ac14263b48fca1 (GK2-1; constructor correction eb2b446ad), repro re-run: NOT RUN; lead controls complete/gap incomplete; R5 unchanged.
- GK2B-2: fixed 91612a5c334bc170dd2c1690ba38084da1152749; adapter follow-up 4a2b91948d23b3c83a7db070d2a2becddf9205f3; coordinate/record follow-up 55fdd026f6394060985f88ea64ae40ba5c418162; repro re-run: NOT RUN.
- GK2B-3: fixed d48ecf855b9781286140c2da1d53ad706ad04114 (GK2-2), repro re-run: NOT RUN; lead qwen3/deepseek_r1 checks passed at 2e0155dd8.
- GK2B-4: fixed af3f48945f6de3aabae67ca7b8b4e66fc44fa666 (GK2-3), repro re-run: NOT RUN; lead 30 observed/model, no identity missing, generation_wall_seconds 19.0.
- GK2B-5: fixed bf7155b7059af930a1eabbec70e1f196948a339b; layout regression 55fdd026f6394060985f88ea64ae40ba5c418162; repro re-run: NOT RUN.
- GK2B-6: fixed d8d838475ae350079b8c4825d7c2fc01ac9263af; preinstall wiring bf7155b7059af930a1eabbec70e1f196948a339b; budget CLI regression bce45811a23ab8e9d09a76e78bedcae4f7b26d11; repro re-run: NOT RUN.
- GK2B-7: fixed 614223ceae52ef88fc8a96c73ae7d208dcf483db; independent preflight/copy limits and flags; repro re-run: NOT RUN.
- GK2B-8: fixed 1df60966407e4db2f7be12308209fd6491f23f42 (thermal); enforced half fixed b259f5f04fffb822a01616303cf4088608debce6 (GK2-5), repro re-run: NOT RUN; lead enforced 700 W passed.
- GK2B-9: fixed 67fe51e1980801c753ee5ce048deb2304a3f37a8 (GK2-7), repro re-run: NOT RUN; lead child-environment check passed at 2e0155dd8.
- GK2B-10: fixed 991ae09e2783a225c06f7bb6c5855a830220af86; checkpoint identity, precision/monitor pins; repro re-run: NOT RUN.
- GK2B-11: fixed 8e9c3ac375c78b3b7ba724fbf6f5821535824e44; malformed-planning guard 55fdd026f6394060985f88ea64ae40ba5c418162; repro re-run: NOT RUN. JSON/source scan is not validate()/jsonschema.
- GK2B-12: fixed 1a6b2d91f7136ad09e810ea7098e1373941e2992; remaining-GPU regression 55fdd026f6394060985f88ea64ae40ba5c418162; repro re-run: NOT RUN.
- GK2B-13: fixed f1850a8a79c121ae4e72d83bbd401b418f29f51e (price/runbook); HF half fixed a33ff4f785206e6be8a57182f355962f721de658 (GK2-4), repro re-run: NOT RUN; HF configs unchanged.
- GK2B-14: info, runbook paragraph 2b7490533cd58271d49c0c06b299f766e4491392; no code change for overlap.

Old-test changes in Round 2b: no assertion deleted/bar widened/skip added/old
expected result changed. Both modules supply required options. Fake installation
interpreter returns validate-only JSON. planning_fixture gets dated synthetic
sources without numerical changes. Existing readiness failure additionally
asserts failed/session_ran_no_model under R13. New budget skip world supplies
valid settings to reach all adapters, then asserts failure and CLI exit 3.
No .review3 appendix edits/files materialized or committed.
