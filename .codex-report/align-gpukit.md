# align-gpukit — FIX ROUND 1

## SUMMARY

Continued lane/2026-10-21-align-gpukit from 280866c8d3f0ccd74877d354559aaf5fc15b5401.
Implemented GK-1 through GK-15 and GK-S; GK-16 is informational and untouched.
Preflight report verdicts now gate model startup, and completeness checks coordinates, turns, failures and physical trace coverage.
Monitor/judge placement is explicit and off measured devices; runner timeouts kill the full process group.
Budget follows 58750718f: 200 items, 36,000 fresh Episodes and 26,400 off-box monitor calls, with multi-GPU precision layouts.
Unsourced volumes/allowances are null; cost output is unavailable until supported, with a partial measured calibration projection.
Added supply/power-cap snapshots, corrected decode weights, schema validation and decimal display, and parameterized bootstrap checks.
The lane contains 36 authored offline tests; no shell command, Python test, repro, package install or hardware run executed in this seat.
All changes were committed and fast-forward pushed through GitHub; PR #521 remains draft and is not merge-ready.

## FILES

Round changes (all within WRITE_SCOPE):

- configs/align/shade.json: five-pair/two-agent baseline, per-model layouts, cited hardware/model inputs, null production volumes/allowances/bounds.
- configs/align/moe_stage_a.json: corresponding MoE-only repeat with the same source/null conventions.
- configs/align/budget.json: 200-item protocol at 58750718f, Qwen3-Next replacing Phi, off-box gpt-oss monitor, fresh/trial/monitor counts, BF16/FP8 alternatives.
- joulewise/align/gpukit/bootstrap.sh: order-independent wrapper flags, required probe timeout/device settings, preinstall isolation, pinned install and repeat-venv path.
- joulewise/align/gpukit/session.py: report-based preflight, measured pool/TP, explicit monitor placement, nonce, process groups, complete-output checks, throttle snapshots and sealed receipts.
- joulewise/align/gpukit/runner_adapter.py: only requested config placeholders, outer task_pair, optional clock/domain, off-box monitor/judge bindings and per-session matrix IDs.
- joulewise/align/gpukit/matrix.py: null planning inputs, numerical provenance walk, records-derived conditions/visibilities and per-model layout validation.
- joulewise/align/gpukit/matrix.schema.json: matching nullable inputs, condition/visibility enums, sourced efficiency constraint and cited example-price rows.
- joulewise/align/gpukit/throughput.py: input-lookup-excluded decode weight reads and decimal two-digit display.
- joulewise/align/gpukit/cost.py: fresh Episode accounting, agent-only token cost, one load/model, TP memory arithmetic, both layout alternatives, extra monitor-GPU line and calibration input.
- joulewise/align/gpukit/throttle.py: old/current clock-event XML fields, raw DTD/XML capture, power limits, cumulative-counter deltas and hardware flags.
- tests/align/test_gpukit.py: original 17 methods retained and updated for the rulings; 19 added methods, including complete/defective worlds, preflight, placement, TP, child cleanup, calibration and throttle paths.
- docs/align/gpukit.md: revised runbook, approval inputs, count/weight derivations, explicit settings, completeness and supply hazards, pending verification and calibration limitations.
- .codex-report/align-gpukit.md: this handoff and FIX LOG.

Registry exceptions: none. No shared contracts, runner.py, tests/test_shard_tests.py,
or other out-of-scope repository file was changed. No .review1 files were committed.
joulewise/align/gpukit/__init__.py remains as it was before this round.

## PUBLIC API

All modules are under joulewise.align.gpukit; private helpers are omitted.

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
- cost.Estimate(gpu_class, trial_rows, measured_episodes, monitor_calls, lower_bound_wall_seconds, lower_bound_gpu_hours, lower_bound_total_usd, wall_seconds, gpu_hours, usd_per_gpu_hour, total_usd, flags, model_load_count=0, monitor_gpu_hours=None, monitor_total_usd=None, generation_wall_seconds=None, calibration_basis={}, layouts=(), layout_alternatives=())
  (calibration_basis uses dataclasses.field(default_factory=dict), not a shared mutable default.)
- runner_adapter.runner_matrix(matrix: Mapping[str, Any], *, model: str, endpoint: str, output_dir: Path, settings: Mapping[str, Any], session_id: str | None = None, monitor_endpoint: str | None = None, judge_endpoint: str | None = None, device_indices: Sequence[int] = ()) -> tuple[dict[str, Any], tuple[str, ...]]
- runner_adapter.write_runner_matrix(path: Path, matrix: Mapping[str, Any], *, model: str, endpoint: str, output_dir: Path, settings: Mapping[str, Any], **bindings: Any) -> tuple[str, ...]
- session.SessionOptions(matrix, output, runner_command, ready_timeout_s, poll_s, command_timeout_s, runner_timeout_s, monitor_placement, preflight_command=(), ready_command=(), vllm_command=("vllm",), gpu_index=0, port=8000, destination=None, copy_kind="rsync", runner_settings=None, gpu_indices=(), monitor_base_url=None, judge_base_url=None, monitor_gpu_index=None, monitor_port=None, calibration_slice=False)
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

New required session CLI/Python policy: runner_timeout_s / --runner-timeout-s,
monitor_placement / --monitor-placement. Bootstrap requires probe timeout and
GPU selection through the documented flags/environment settings. --calibration-slice
is optional. Default runner remains python -m joulewise.align run --matrix
{runner_matrix}; budget's default translation remains explicitly unavailable.

## TESTS RUN

No shell or Python process launched. Initial, intermediate and final attempts of:

    pwd
    python3 --version

were rejected before execution with "No usable execution environment is available."
The environment wait never yielded a usable executor; runtime status continued to
report starting/pending and offline. No local checkout, git fetch/checkout, .review1
materialization, scratch integrated tree, pip installation or test execution was
possible. The brief explicitly permits the GitHub fallback; all changes used
connected GitHub tools with expected-head, non-forced fast-forward updates.

The following are **NOT RUN**, with run counts, passes, failures and skips unknown.
From /workspace/JouleWise, no installed repo and no external PYTHONPATH, the
requested environment is TMPDIR=/tmp/gk-tmp JW_B5_SYNTHETIC_ONLY=1:

    python3 -m unittest tests.align.test_gpukit -v
    python3 -m unittest discover -s tests/align -t .

The extra-dependent setup and same runs are also **NOT RUN**:

    python3 -m venv /tmp/gpukit-jsonschema
    /tmp/gpukit-jsonschema/bin/pip install jsonschema
    /tmp/gpukit-jsonschema/bin/python -m unittest tests.align.test_gpukit -v
    /tmp/gpukit-jsonschema/bin/python -m unittest discover -s tests/align -t .

Source inventory is 36 authored test methods, not an observed test-run count.
The original optional-jsonschema test keeps its existing skipUnless and reason
"optional jsonschema is not installed". The new schema test uses that same optional
dependency guard. Existing Bash skipUnless is unchanged. No existing test received
a new skip or a widened numerical agreement bar. Existing assertions were updated
for mandated budget counts, corrected decode arithmetic, preflight refusal semantics
and the explicit bootstrap argv; assertions on failure evidence, bounds, complete
positive output, energy, custody and subprocess cleanup remain.

Every supplied reviewer repro is **NOT RUN**:

    python3 -I /workspace/JouleWise/.review1/session_probe.py /workspace/JouleWise /workspace/JouleWise/.review1
    python3 -I /workspace/JouleWise/.review1/gpu_probe.py /workspace/JouleWise /workspace/JouleWise/.review1/bin
    python3 -I /workspace/JouleWise/.review1/boot_probe.py /workspace/JouleWise /workspace/JouleWise/.review1
    python3 -I /workspace/JouleWise/.review1/ready_probe.py /workspace/JouleWise /workspace/JouleWise/.review1
    /tmp/gpukit-jsonschema/bin/python -I /workspace/JouleWise/.review1/schema_probe.py /workspace/JouleWise
    python3 -I /workspace/JouleWise/.review1/bounds_noembed.py /workspace/JouleWise
    python3 -I /workspace/JouleWise/.review1/bounds.py /workspace/JouleWise

Integrated cases, each **NOT RUN**, with the required added policy options shown:

    python3 -I /workspace/JouleWise/.review1/run_session.py /tmp/gk-integ /tmp/gk-integ -- configs/align/shade.json --output /tmp/gk-e2e/gk-shade --runner-settings /workspace/JouleWise/.review1/settings-gk.json --ready-timeout-s 20 --command-timeout-s 120 --runner-timeout-s 120 --monitor-placement none --poll-s 0.2 --port 18841 --preflight-command '["preflight-ok"]'
    python3 -I /workspace/JouleWise/.review1/run_session.py /tmp/gk-integ /tmp/gk-integ -- configs/align/shade.json --output /tmp/gk-e2e/default-preflight --runner-settings /workspace/JouleWise/.review1/settings-gk.json --ready-timeout-s 20 --command-timeout-s 120 --runner-timeout-s 120 --monitor-placement none --poll-s 0.2 --port 18842
    python3 -I /workspace/JouleWise/.review1/run_session.py /tmp/gk-integ /tmp/gk-integ -- configs/align/shade.json --output /tmp/gk-e2e/default-mock2 --runner-settings /workspace/JouleWise/.review1/settings-mock.json --ready-timeout-s 20 --command-timeout-s 120 --runner-timeout-s 120 --monitor-placement none --poll-s 0.2 --port 18843 --preflight-command '["preflight-ok"]'

Those port values are suggested harness settings, not observed free ports.
No actual default-preflight report exists from this seat: its verdict, flags,
measurement readiness and log contents are unknown. The argv construction now
includes --out and one --device per measured index by source inspection only.
The runner scratch SyntaxError patch and all archive/extraction checks are NOT RUN.
The repository-wide suite was not launched, as the brief explicitly directs.

Static checks actually performed using connected tools/JavaScript, **not Python tests**:

- Read report, AGENTS/M0/intake, shared contracts, runner docs/code and NVML main;
  read budget run.py/conditions.py/doc at 58750718f, and SHADE judge documentation.
- GitHub comparison from 280866c8d confirmed forward-only ancestry and that every
  round code/config/test change stays within WRITE_SCOPE.
- Read back all 13 changed code/config/test/runbook files at
  ada1c7e86fef0c837f2a28bec679890b473028ad: exact equality with authored text.
- A JavaScript implementation of the sibling-source/derivation walk on actual
  old-head configs found 18 unsupported numeric leaves in EACH of shade/MoE/budget;
  on the revised configs it found zero in EACH. This demonstrates the old-head
  source failures without claiming numeric_provenance's Python test executed.
- JavaScript source inventory confirmed all original 17 test method names remain,
  with 19 added. Connected GitHub metadata confirmed PR #521 open, draft, unmerged.
- Read public Qwen card mirrors, Qwen3-Next config-source registry, driver DTD/XML
  mirrors and NVIDIA-authored NVML header. No model weights or packages fetched.

Reviewer-supplied evidence on OLD 280866c8d is not this seat's verification:
17 gpukit tests passed with/without jsonschema, and 21 alignment tests passed with
one optional-jsonschema skip in the bare environment. No final-head pass, green
CI, independent executing review, cross-model arithmetic comparison or cold final
pass is claimed.

## END-TO-END

**NOT RUN.** There are no observed current-head Episode counts, Joules, durations,
child-process counts, flags or archive-verification results.

Authored production-path worlds (design numbers, not results):

- Bash bootstrap -> real session -> stub whole-GPU XML/report-writing preflight/
  vLLM process -> subprocess fixture writing shared Episodes -> read_episodes and
  coordinate/power checks -> manifest/archive/local copy -> digest/mutation checks.
  Full SHADE world: 60 Episodes, each 12 Turns, eight tool calls, 40,000 uncached
  prefill tokens, 8,000 generated tokens, 148 virtual seconds, 1,481 samples at
  100 ms. Power alternates +/-1 W about 280 W, with 80 W lower power across eight
  2 s tool waits. Hand integral: 148*280 - 8*2*80 = 40,160 J. The 1e-6 relative
  arithmetic bar is unchanged. Traces use an NVML source LABEL solely to exercise
  the non-mock positive validation branch; their notes explicitly say synthetic,
  and no actual NVML/hardware observation is claimed.
- The complete world must give data_complete=true. Separate real-path worlds
  replace the source with mock, duplicate half the coordinates, omit an Episode,
  retain one sample, remove Turns, or add endpoint.error.AttributeError.
  Missing coverage is almost 148 s versus I+W=100 ms, well above the required bar.
  All must give false and the specific reason. A different-model world fails;
  an endpoint identity containing the correct model succeeds.
- Preflight worlds write refused=true/exit 2, exit 2/no report, or refused=false/
  measurement_ready=false. Tests check no model directories and absent runner
  marker on refusal, sealed bundles, CLI exit 2, and retained false readiness.
- Placement world serves two agent processes on measured GPU 0 serially and one
  persistent monitor process on GPU 1. It inspects per-process CUDA_VISIBLE_DEVICES,
  translated monitor port, sampler device list and measured-only preflight argv.
  Separate TP world uses devices 2,4, checks TP=2 and both traces; removing GPU 4's
  trace must fail completeness.
- Runner timeout world launches a sleep grandchild and uses a 5 s policy timeout;
  the test requires no live descendant. This is scheduling policy, not physics.
- Throttle worlds run the real session with stub XML for clear/active/advancing/
  missing fields. Positive printed microsecond ticks trigger hardware flags;
  software-cap deltas are retained; none refuses or invalidates otherwise complete
  agent/power data. Before/after XML and sealed manifests are checked.
- Calibration SHADE slice runs the same chain with first seed: 20 Episodes. The
  generation-only projection is 60*148 = 8,880 synthetic seconds, with observed
  mean prefill/decode 40,000/8,000. It must retain unavailable full rental time.

GK-6 derived per-token weights, from source fields and arithmetic (not execution):

| Model | This round B | Reviewer B (last printed digit) |
|---|---:|---:|
| Qwen3-4B | 3.988956160 -> 3.99 | 3.99 |
| Qwen3-8B | 7.572329856 -> 7.57 | 7.57 |
| Qwen3-14B | 13.977912320 -> 13.98 | 13.98 |
| Qwen3-30B-A3B | 2.988835072 -> 2.99 | 2.99 |
| Phi-3.5-mini | 3.701499392 -> 3.70 | 3.70 |
| Qwen3-Next-80B-A3B-Thinking | 2.688835072 | not supplied |

## DECISIONS I MADE

- Follow the existing remote lane head, not the spine, and use the explicitly
  permitted GitHub fallback. Never force-push, merge, rent, modify another branch
  or expand the repository write scope.
- Follow the cloud-runtime skill for status/network diagnosis while available.
  No credential values, secret files or environment dumps were read or printed.
- R4 report semantics control refusal: a missing/unreadable/invalid-verdict report
  means no demonstration of sampling and refuses; readable refused=false proceeds
  even with false readiness or nonzero command status. Exit code alone is not a
  verdict. All raw reports and verdict fields are preserved.
- Inventory all measured TP indices plus an explicitly selected separate monitor
  device. Preflight/sampling use measured devices only. GPU count and precision
  are per-model; whole-box billing still includes allocated idle measured devices.
- Require explicit external/gpu/none monitor placement, with no default host.
  The separate local GPU persists for the whole session and is never sampled.
  Monitor/judge share its served model; an independently served judge can use the
  external mode. Missing/failed/overlapping scoring service is deferred, not a
  refusal. Monitor/judge token work is absent from agent inference estimates.
- The adapter substitutes only requested keys. Exact placeholders preserve types;
  embedded placeholders are strings. task_pair belongs at the outer component.
  Clock/domain settings pass through, which is essential for runner-owned mocks.
- A fresh UUID session_id in the receipt enters each model matrix_id. Direct
  adapter calls without an ID get a fresh UUID too. Reusing an explicit ID is
  reserved for deliberate replay; custom drivers must use the supplied session ID.
- Match model IDs inside conforming endpoint identities. The built-in declared
  mock/synthetic endpoint identifies synthetic-8B, not the planned HF model:
  its wholly mock traces already make it incomplete, so that explicit mock world
  does not acquire a second model-mismatch reason. Non-mock different models do.
- Completeness compares Counter(task_pair, condition, seed) with expand() per model,
  not only a count or ID set. Require Turns and coverage for all measured gpuN
  channels. Apply clock offsets, then the exact I+W boundary allowance.
- Work-breaking runner flags include dotted endpoint/runner/factory errors, any
  component .factory_error., task setup, sampler, interrupted/max-turn, power.empty,
  unknown condition, usage/clock/tool/token-counter errors, and unclosed/uncounted
  scratchpads. Monitor/score errors can be repaired off-box and do not erase the
  captured agent/power product. power.notes is descriptive metadata, not an error.
- Separate runner and probe timeouts. Runner/vLLM process groups are always cleaned,
  including workers of an exited parent. The runner timeout is explicit policy.
- Use budget run.py/conditions.py/doc at 58750718f as R1 authority. Read current
  sibling head 819b3977 only for context; no count changed based on that later head.
  There is no code/doc disagreement for requested count rules: calibration is per
  item/repetition, unpaired/unmonitored; forced two-call work is one Episode;
  deletion reuses generation. Original Phi/32-item/local-Qwen-monitor planning is
  superseded by the owner's R1/R2 rulings.
- Keep the four budget effort categories plus deletion controls outside shared
  Episode.condition. The shared contract wins; a lane-local budget driver is still
  required, rather than relabeling effort as benign/sabotage.
- The per-model BF16/4 and FP8/2 Next alternatives use 80B and cited 80 GB H100
  memory. Headroom stays null instead of inventing a KV/context allowance.
  FP8 checkpoint existence was checked through public card/registry mirrors.
- Set every unsourced production volume/wait/host/setup/load/router allowance null;
  remove the old typical-SHADE-shape claim. Nulls are valid format inputs and yield
  unavailable results with named flags, not fabricated zero work.
- Numeric provenance is a sibling/parent dated HTTPS citation with quote/note, or
  a sibling/parent derivation naming cited inputs. The walk checks numerical
  leaves in workload/gpu_classes/model_parameters; example prices stay empty.
- Keep optimistic roofline inputs distinct from throughput. Dense Qwen decode uses
  non-embedding count + output head to avoid differences of independently rounded
  totals; MoE/Phi use active count - input table. Prefill's active-count FLOP
  approximation remains explicit. No KV attention, TP efficiency or FP8 compute
  rate is invented.
- All derived display arithmetic is decimal, with two significant digits and
  downward bounds. Exact integer counts/byte inventories remain exact.
- Calibrate all SHADE/MoE task/condition/model strata at first seed. Accept an
  Episodes JSONL or bundle to project generation brackets with a printed basis.
  Do not present that as a full rental plan without setup/load/scoring-wait time.
  Budget needs its calibration/effort/pair strata, so its pooled Episode projection
  is explicitly unavailable. This is an OPEN ISSUE permitted by R3.
- Capture raw --dtd XML at start and before/after model work. Support old throttle
  and new event names, keep board GPU power limits distinct from module limits,
  compare cumulative counters exactly in printed microseconds, flag resets/missing
  evidence. Any positive hardware tick is evidence; software power cap is a quantity.
  No snapshot condition refuses the session.
- Retain existing failure/custody/energy assertions; update expected counts,
  corrected weight arithmetic and command arguments to the governing rulings.
  Added large defects plus complete positive worlds. Do not add skips to old tests.
- Preserve draft PR #521 and report authored/unexecuted work plainly. The lead
  still owns integrated execution, independent review, CI and merge gates.

## CONTRACT-CHANGE

No edits requested to PIPELINE.md, records.py or interfaces.py.

Request to the nvml lane: record clock-event/throttle reasons and cumulative
violation durations with each power sample, using nvmlDeviceGetViolationStatus
and/or clock-event-reason calls. Before/after snapshots cannot place a supply
brake or software cap within an individual Episode. This is additional telemetry,
not a new refusal rule. Keep unsupported counters explicitly flagged.

Budget's shared benign/sabotage Condition remains unchanged. Its driver should
preserve trial effort, paired/calibration identity and reuse metadata in lane-local
output while exporting fresh shared Episodes, so the kit can validate/extrapolate
the correct physical work without counting deletion views twice.

## OPEN ISSUES

- Everything requiring a shell remains NOT RUN: both unittest commands, jsonschema
  setup/reruns, every reviewer script, integrated cases, compilation and manifests.
  No current-head pass or hardware readiness is established.
- Required reviewer harness call adaptations were NOT WRITTEN because .review1
  could not be materialized. Add runner_timeout_s and monitor_placement to
  SessionOptions calls (hang uses 5 s); append corresponding CLI options to
  ready_probe/main and integrated commands; supply bootstrap probe-timeout/device
  settings. gkfix task now reads context.task_pair, without requiring that key in
  config; settings-gk explicitly requests model/base_url and sampler interval
  placeholders. Both settings files pass clock={"factory":"mock.clock"} and
  clock_domain="mock.monotonic"; the obsolete gkfix time monkeypatch can be removed
  when moving to that explicit clock. These are wiring-only adaptations; no world
  or printed check needs weakening.
- R4 conflicts with the supplied preflight-ok stub: it prints {"fixture":true} to
  stdout and never writes --out. Under the required semantics this MUST refuse
  with nvml_preflight_unavailable, so unchanged happy-path reviewer probes cannot
  reach their runner worlds. The lead must reconcile that harness fixture to write
  a readable refused=false report; this seat did not change that supplied stub or
  add a production stdout bypass. Authored tests use a real report-writing stub.
- bounds.py/bounds_noembed.py use stale budget/local-monitor counts and null token
  fields after R1/R2/R3. They are expected to fail as old planning-table repros,
  not regressions. They were not run and no exception/result is claimed.
  Independent updated weight/count arithmetic is authored in the lane tests.
- GK-16 runner SyntaxError at the cited a5a25d7a5 head: patch only the integrated
  scratch copy exactly as the brief specifies, or use its subsequently fixed head
  after recording that source. No repository runner.py was edited.
- Discovery census tests/test_shard_tests.py is explicitly nvml/lead-owned; its
  fix is on that lane. No registry exception was needed or used here.
- Generic budget runner translation is unavailable. Its custom driver, immutable
  item/hint roster, fresh hinted/paired/calibration export and session identity
  integration must be completed and rehearsed before any budget rental.
- Calibration projects SHADE/MoE generation brackets only. A complete receipt-based
  setup/load/off-box-wait rental extrapolation is unfinished; budget additionally
  needs effort/calibration/pair strata. Full rental cost remains null, as permitted
  by R3's OPEN ISSUES fallback. Approve only a separately capped calibration slice;
  provider auto-shutdown must bound the entire paid period.
- Real factory registrations, actual NVML/vLLM compatibility and MoE worker router
  capture remain sibling-integration dependencies. Do not engineer these on the
  rental meter. Real model/tokenizer/server/data revisions remain to be pinned.
- GPU/layout fit is not verified without explicit KV/scales/allocator headroom.
  Next's thinking-off control is unsupported by its card and must stay a flagged
  condition, not an outcome-dependent omission. FP8 is a different configuration.
- Current XML names are corroborated by driver DTD/XML mirrors; the actual rented
  driver's --dtd capture and counter support remain to be checked. Direct NVIDIA/HF
  access was unavailable in this executor-less seat; source mirrors and inherited
  datasheet citations are distinguished in the configs/runbook.
- Independent executing/cross-model review, merged-tree checks, final CI and cold
  merge verification remain lead-owned and NOT RUN. No merge or rental authorized.

## NEEDS_RULING

Choose the budget Qwen3-Next physical configuration before rental:

- BF16 on 4 H100-SXM-80GB: 80B*2 = 160 GB weights in 320 GB capacity, with headroom
  supplied explicitly. This preserves BF16 across model sizes.
- Published Qwen FP8 checkpoint on 2 H100-SXM-80GB: approximately 80 GB weight bytes
  in 160 GB capacity before scales/KV/allocator, headroom supplied explicitly.

Recommendation: BF16/4 if Ed approves its cost, to retain common precision; otherwise
record FP8/2 as a distinct configuration. Both options are printed/configurable.
Blocked work: real budget allocation/measurement, not this lane's code authoring.
Provider, price, spend ceiling and actual headroom are also required operator
approval/input, not invented defaults. No other science-count/printed-number
ruling is requested.

## FIX LOG

"fixed" below means implementation pushed, **not executed verification**.
Later test/runbook commits supplement these implementation checkpoints.

- GK-1: fixed eca533727ce543330aa6bfeacd2925d0cfbeb397 (follow-ups 0c402afe, ada1c7e8).
- GK-2: fixed d9a2d7cc185d5684c58b30b0908aa0935a61658e.
- GK-3: fixed a4c9931ac52efdf4cb186c34ff9c00a6d959e738.
- GK-4: fixed 2b1307dc8a6ec73e4f6deec9e981e34b0298169b.
- GK-5: fixed a4c9931ac52efdf4cb186c34ff9c00a6d959e738 (partial calibration/final limitations 6fac9635).
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

Reviewer .review1 copy changes: none were materialized or executed. Pending
call/settings adaptations and the R4 stub incompatibility are listed in OPEN ISSUES;
no worlds, modes, printed checks or assertions were weakened. No out-of-scope
registry or fixture-signature files were changed.
