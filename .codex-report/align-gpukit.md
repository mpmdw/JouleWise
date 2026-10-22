# align-gpukit — FIX ROUND 1, continuation fix1c

## SUMMARY

Continued lane/2026-10-21-align-gpukit from bed93a0950c9da1a699173609ddfe60d65084d72.
C1 recomputes missing efficiency/token-volume flags from the current estimate inputs instead of replaying stale template labels.
C2 applies amended R4: measurement_ready must be the JSON boolean true before any model starts.
Unready, absent, null or non-boolean readiness now refuses with nvml_measurement_not_ready and preserves the sealed report/bundle.
Kept the original failing arithmetic test unchanged; added one input-flag regression and expanded report/CLI refusal worlds.
Updated the runbook with strict readiness and the custom preflight --out/--device report contract.
The source inventory is 37 offline test methods; no shell/Python command, test, repro or package installation executed in this seat.
The director's supplied bed93a095 results are recorded separately; final-head tests and integrated repros remain NOT RUN.
Both code steps were fast-forward pushed through GitHub; PR #521 remains draft, with no merge, rental or hardware run.

## FILES

Continuation changes from bed93a095 (all within WRITE_SCOPE):
cost.py (C1 flags), session.py (C2 gate), test_gpukit.py (regressions),
gpukit.md (runbook), and this report. No config or public signature changed.

Full lane inventory (retained from the previous round):

- configs/align/shade.json: five-pair/two-agent baseline, per-model layouts, cited hardware/model inputs, null production volumes/allowances/bounds.
- configs/align/moe_stage_a.json: corresponding MoE-only repeat with the same source/null conventions.
- configs/align/budget.json: 200-item protocol at 58750718f, Qwen3-Next replacing Phi, off-box gpt-oss monitor, fresh/trial/monitor counts, BF16/FP8 alternatives.
- joulewise/align/gpukit/bootstrap.sh: order-independent wrapper flags, required probe timeout/device settings, preinstall isolation, pinned install and repeat-venv path.
- joulewise/align/gpukit/session.py: strict boolean measurement-ready gate (C2), report-based preflight, measured pool/TP, explicit monitor placement, nonce, process groups, complete-output checks, throttle snapshots and sealed receipts.
- joulewise/align/gpukit/runner_adapter.py: only requested config placeholders, outer task_pair, optional clock/domain, off-box monitor/judge bindings and per-session matrix IDs.
- joulewise/align/gpukit/matrix.py: null planning inputs, numerical provenance walk, records-derived conditions/visibilities and per-model layout validation.
- joulewise/align/gpukit/matrix.schema.json: matching nullable inputs, condition/visibility enums, sourced efficiency constraint and cited example-price rows.
- joulewise/align/gpukit/throughput.py: input-lookup-excluded decode weight reads and decimal two-digit display.
- joulewise/align/gpukit/cost.py: current-input cost flags (C1), fresh Episode accounting, agent-only token cost, one load/model, TP memory arithmetic, both layout alternatives, extra monitor-GPU line and calibration input.
- joulewise/align/gpukit/throttle.py: old/current clock-event XML fields, raw DTD/XML capture, power limits, cumulative-counter deltas and hardware flags.
- tests/align/test_gpukit.py: 37 methods (original 17 retained, 20 added across the fix round); C1 leaves test_independent_hand_arithmetic byte-identical to bed93a095 and adds test_static_missing_input_flags_are_recomputed. C2 expands existing preflight/CLI tests for unready, missing, null, numeric and string readiness, absent runner marker/model directories, retained flags/report and sealed manifests. Other complete/defective, placement, TP, cleanup, calibration and throttle worlds remain.
- docs/align/gpukit.md: revised runbook, approval inputs, count/weight derivations, explicit settings, completeness and supply hazards, pending verification and calibration limitations.
- .codex-report/align-gpukit.md: this handoff and FIX LOG.

Registry exceptions: none. No shared contracts, runner.py, tests/test_shard_tests.py,
or other out-of-scope repository file was changed. No .review1 files were committed.
joulewise/align/gpukit/__init__.py remains as it was before this round.

## PUBLIC API

All modules are under joulewise.align.gpukit; private helpers are omitted.
C1/C2 change no public signature. run_session now refuses unless the preflight
report demonstrates measurement_ready is the JSON boolean true.

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

This continuation executed **no shell or Python process**. Initial and final
attempts of pwd and python3 --version failed before launch with
"No usable execution environment is available." The environment wait remained
pending; the runtime tool reported observations_current=true, observed_phase=pending
and connectivity=offline. No local checkout, git command, .review1 file, integrated
tree, pip install, test or repro could be materialized/executed. All writes used
the explicitly authorized connected-GitHub fallback with non-forced expected-head
updates. This is an execution-environment failure, not an approval rejection.

Own checks actually performed through GitHub tools and JavaScript (not Python tests):

- Read the pushed report first, then shared contracts, AGENTS/M0/intake and
  orchestration; TASK_QUEUE.md is empty, no active stop card, explicit user lane
  direction selects this task. No local status or network-policy file could be read.
- GitHub head was bed93a0950c9da1a699173609ddfe60d65084d72; C1 and C2 have
  exactly one preceding parent each and were fast-forward pushed.
- Read back all four changed code/test/runbook files at 18d3beb196989397b415c6945b2356f3531bb359:
  exact equality with authored contents.
- Source inventory: 36 old and 37 current test methods, no old method removed;
  test_independent_hand_arithmetic is byte-identical to bed93a095.
- Compared bed93a095..18d3beb1: two commits ahead, zero behind, only
  docs/align/gpukit.md, joulewise/align/gpukit/{cost,session}.py and
  tests/align/test_gpukit.py changed before the report commit.
- PR #521 was open, draft and unmerged. No claim of final-head green CI.

Director-provided execution evidence, **at bed93a095, not this seat's results**:
macOS Python 3.13, stdlib only, no PYTHONPATH, TMPDIR set,
JW_B5_SYNTHETIC_ONLY=1.

| Director command/run | Supplied result |
|---|---|
| python3 -m unittest tests.align.test_gpukit | Ran 36, one failure, two skips (both optional jsonschema) |
| Same focused suite with jsonschema | Ran 36, one failure, no skips |
| python3 -m unittest discover -s tests/align -t . | Ran 40, one failure, two skips (both optional jsonschema) |

The sole reported failure was MatrixTests.test_independent_hand_arithmetic line
122: throughput_efficiency_not_supplied was replayed from matrix.flags after
efficiencies were supplied. C1 fixes the implementation; the test is unchanged.
The director did not supply an extra-enabled discovery result or exact venv
installation command, so neither is inferred.

Director-provided repro evidence at bed93a095:

- GK-1: session_probe modes ok/dup/short/onesample all false with mock-power,
  coordinate, count and coverage reasons respectively; MODE=real positive world
  true. Integrated zero-turn endpoint.error.AttributeError world false.
- GK-7: runner mocks with explicit clock, external monitoring: 30 Episodes/model,
  at least 12 Turns each, 90 verdicts/model, no factory.error.* or endpoint.error.*;
  completeness false only for mock power.
- GK-8 Pass-Through accepted; MIG, VGPU and Host VGPU refused.
- GK-9 hang: zero live grandchildren, elapsed 5.5 s; readiness worker orphans zero.
  MIG CLI exited 2 without preflight.
- GK-12 typos each produced one schema error. GK-14 both bootstrap argument orders
  exited 0; MIG stopped before venv/pip.
- GK-5 all three cost CLIs printed unavailable with named missing inputs;
  budget counts were 36,000 generation Episodes and 26,400 monitor calls.
- GK-13 decimal output was 0.47, 1.9, 0.57.
- GK-2 real NVML preflight, without NVML: argv included --out and --device 0;
  no usage error, exit 0, refused=false, measurement_ready=false, flag
  "preflight_incomplete: NVML library unavailable; optional pynvml is not installed".
  Both agent models then ran. C2 deliberately changes that outcome to refusal;
  its final-head integrated repro remains NOT RUN.

The following exact final-head commands are **NOT RUN**. Counts, pass/failure
results and actual skips are unknown. The source inventory of 37 is not a run count.
From /workspace/JouleWise, without installing the repository or setting PYTHONPATH,
set TMPDIR=/tmp/gk-tmp and JW_B5_SYNTHETIC_ONLY=1:

    python3 -m unittest tests.align.test_gpukit -v
    python3 -m unittest discover -s tests/align -t .

Extra-dependent setup/reruns, also **NOT RUN**:

    python3 -m venv /tmp/gpukit-jsonschema
    /tmp/gpukit-jsonschema/bin/pip install jsonschema
    /tmp/gpukit-jsonschema/bin/python -m unittest tests.align.test_gpukit -v
    /tmp/gpukit-jsonschema/bin/python -m unittest discover -s tests/align -t .

No skip guard was added to an existing test; the two jsonschema guards and
Bash guard remain unchanged. C2 changes the false-readiness expected outcome
because the owner amended R4, not to make a failing implementation pass.

Every supplied final-head reviewer repro is **NOT RUN**:

    python3 -I /workspace/JouleWise/.review1/session_probe.py /workspace/JouleWise /workspace/JouleWise/.review1
    python3 -I /workspace/JouleWise/.review1/gpu_probe.py /workspace/JouleWise /workspace/JouleWise/.review1/bin
    python3 -I /workspace/JouleWise/.review1/boot_probe.py /workspace/JouleWise /workspace/JouleWise/.review1
    python3 -I /workspace/JouleWise/.review1/ready_probe.py /workspace/JouleWise /workspace/JouleWise/.review1
    /tmp/gpukit-jsonschema/bin/python -I /workspace/JouleWise/.review1/schema_probe.py /workspace/JouleWise
    python3 -I /workspace/JouleWise/.review1/bounds_noembed.py /workspace/JouleWise
    python3 -I /workspace/JouleWise/.review1/bounds.py /workspace/JouleWise

Use the director's authorized harness adaptations listed in FIX LOG. Build the
integrated scratch tree per the brief (runner/NVML lane heads must be recorded).
Patch the runner SyntaxError only in scratch if the fetched head still has it.
Integrated commands, all **NOT RUN** (ports are harness policy, not observed free ports):

    python3 -I /workspace/JouleWise/.review1/run_session.py /tmp/gk-integ /tmp/gk-integ -- configs/align/shade.json --output /tmp/gk-e2e/gk-shade --runner-settings /workspace/JouleWise/.review1/settings-gk.json --ready-timeout-s 20 --command-timeout-s 120 --runner-timeout-s 120 --monitor-placement none --poll-s 0.2 --port 18841 --preflight-command '["preflight-ok"]'
    python3 -I /workspace/JouleWise/.review1/run_session.py /tmp/gk-integ /tmp/gk-integ -- configs/align/shade.json --output /tmp/gk-e2e/default-preflight --runner-settings /workspace/JouleWise/.review1/settings-gk.json --ready-timeout-s 20 --command-timeout-s 120 --runner-timeout-s 120 --monitor-placement none --poll-s 0.2 --port 18842
    python3 -I /workspace/JouleWise/.review1/run_session.py /tmp/gk-integ /tmp/gk-integ -- configs/align/shade.json --output /tmp/gk-e2e/default-mock2 --runner-settings /workspace/JouleWise/.review1/settings-mock.json --ready-timeout-s 20 --command-timeout-s 120 --runner-timeout-s 120 --monitor-placement none --poll-s 0.2 --port 18843 --preflight-command '["preflight-ok"]'

Expected amended default-preflight outcome for the director's no-NVML report:
status refused, nvml_measurement_not_ready, no model-* directories, bundled
report and sealed archive, CLI exit 2. This is the ruling/implementation expectation,
not an executed result. No repository-wide suite was run, per the brief.

## END-TO-END

**NOT RUN by this continuation seat.** There are no observed final-head Episode
counts, Joules, durations, child-process counts or archive-verification results.

Director-provided bed93a095 observations: the fixture runner's non-mock-labeled
positive control gave data_complete=true; its mock/duplicate/short/single-sample
worlds gave false with specific flags. The integrated real runner with clocked mock
factories produced 30 Episodes per model, at least 12 Turns per Episode and
90 monitor verdicts per model under external placement, and was incomplete only
for mock power. Hang cleanup left zero live grandchildren. These are synthetic
integration observations at the old head, not physical GPU measurements or
verification of this continuation's final head. The real preflight without NVML
reported measurement_ready=false yet spent both models; C2 closes that gate.

Authored production-path worlds (design numbers below, not results of this seat):

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
  measurement_ready=false, plus missing/null/string/numeric readiness. C2 now
  requires every such unready world to refuse, with no model directories or runner
  marker, sealed bundles, CLI exit 2, and retained report fields/flags. The existing
  fully ready complete-world positive control still requires true completeness.
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
- C2 explicitly amends R4: missing/unreadable/invalid-verdict reports refuse.
  A readable refused=true report refuses; any measurement_ready value other than
  JSON boolean true also refuses with nvml_measurement_not_ready. This is the
  physical instrument-readiness gate, before both monitor and agent startup.
  refused=false plus measurement_ready=true may proceed despite a nonzero command
  exit, which remains a flag. Exit code alone is never a verdict; reports are kept.
- C1 treats throughput_efficiency_not_supplied and workload_token_volumes_unavailable
  as evaluated input flags, not permanent template context. The selected GPU's
  agent-model efficiencies and current prefill/decode values determine them.
  Other static context/provisional flags remain. The original arithmetic test is
  unchanged; a new regression checks stale-token removal and partial efficiencies.
- Use the user-authorized GitHub fallback because executor startup did not become
  usable. Distinguish own static/readback checks from the director's executed
  bed93a095 evidence and mark all own Python/shell tests/repros NOT RUN.
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
- Preserve draft PR #521 and report authored/unexecuted final-head work plainly.
  The director's old-head evidence is retained without claiming a final-head pass.
  The lead still owns final executing review, CI and merge gates.

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

- Final-head shell/Python tests, jsonschema installation/reruns, every reviewer
  repro, integrated tree and manifest checks are NOT RUN in this seat. Executor
  calls still fail before launch; no final-head pass or hardware readiness is
  established. The director's bed93a095 results are recorded in TESTS RUN.
- Reviewer .review1 files were not materialized here. The director already
  reconciled the preflight-ok fixture to write the NVML report format, and the
  continuation explicitly authorizes the same harness wiring adaptations.
  Use the list in FIX LOG; no production stdout bypass is needed or added.
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

"fixed" below means implementation pushed; no Python/shell verification ran in
this seat. Director-supplied execution at bed93a095 is separately recorded in
TESTS RUN and does not establish a final-head pass. Earlier checkpoints remain:

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
