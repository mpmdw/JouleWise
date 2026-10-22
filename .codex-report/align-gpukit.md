# align-gpukit — FIX ROUND 2

## SUMMARY

Continued lane/2026-10-21-align-gpukit from a37655231799dccd0339140f1dabf7d15bb42c8e; retained GK2-1 through GK2-7 fixes.
Corrected GK2-1's sensor-clock test to supply ClockMapping in the Episode constructor; preserved its world and every assertion.
No production code, config, numerical input, bar, skip or test count changed in this continuation.
R5 supported-channel coverage, per-model parsers, failed-session exit 3, shared identities, CUDA ordering and modern power limits remain implemented.
The lead executed 56 alignment tests at a37655231: one constructor error (corrected here), three skips; jsonschema was not installed.
The lead's five real-sampler session worlds all had data_complete=true; independent coverage replay agreed, including both incomplete 40 s probes.
The lead also verified parser argv, missing-matrix failure before hardware calls, identity calibration and round-1 cleanup/MIG regressions.
This seat could not launch a shell or Python process; the corrected test, jsonschema runs and schema probe were NOT RUN by this seat.
Pushed the test correction and evidence report through the explicitly authorized GitHub fallback; PR #521 remains draft and unmerged.
No hardware, rental, spend or scientific result is claimed.

## FILES

Fix2c continuation changes only tests/align/test_gpukit_round2.py (constructor mapping)
and this report (lead evidence and current handoff). All other entries below describe
the retained Round-2 implementation, not new production changes.

Round-2 files (each within WRITE_SCOPE):

- joulewise/align/gpukit/coverage.py: R5 notes/channel grouping, serial read time, expected/realized spacing, coverage flags and ratios.
- joulewise/align/gpukit/identity.py: shared delimited model identity matcher.
- joulewise/align/gpukit/session.py: production coverage integration/metrics, explicit serve parsers, early matrix failure, exit codes and CUDA device order.
- joulewise/align/gpukit/cost.py: calibration uses the shared model matcher.
- joulewise/align/gpukit/matrix.py: validates explicit agent/monitor/layout serving fields.
- joulewise/align/gpukit/matrix.schema.json: requires matching nullable parser fields and explicit monitor_serving.
- joulewise/align/gpukit/throttle.py: modern current_power_limit fallback for enforced, requested limits and read v12/v13 citations.
- configs/align/shade.json: agent/monitor serving specs and lead-quoted pinned HF provenance; numerical work/weight inputs unchanged.
- configs/align/moe_stage_a.json: same serving/provenance changes for the MoE repeat.
- configs/align/budget.json: hybrid/Next/FP8/monitor parser choices and pinned provenance; 36,000 fresh Episodes/26,400 monitor calls unchanged.
- tests/align/test_gpukit.py: all 37 old methods retained; child device-order assertions, one R5-mandated mock assertion change and a new real-session v13-limits method (38 source methods).
- tests/align/test_gpukit_round2.py: 14 Round-2 methods for R5 worlds, per-model argv/schema, failure exits, identity calibration and provenance/limits; fix2c adds an optional clock_mappings helper argument and passes it into Episode construction before record validation.
- docs/align/gpukit.md: reconciled R5 completeness, parser provenance, exit codes, CUDA ordering and modern-driver limits.
- .codex-report/align-gpukit.md: current handoff, attributed lead execution at a37655231, this seat's unexecuted checks, retained round-1 FIX LOG and Round 2 correction.

Unchanged lane modules remain bootstrap.sh (preinstall whole-GPU check/pinned
install), runner_adapter.py (runner translation), throughput.py (decode weights
and decimal display), and __init__.py. No registry exceptions. No changes to
PIPELINE.md, records.py, interfaces.py, sibling lanes or any other repository
path. No .review2 harness/evidence was committed or materialized by this seat; the lead ran its own appendix harness.

## PUBLIC API

All modules are under joulewise.align.gpukit; private helpers are omitted except the replay seam below. No public signature changed in fix2c; the test-only episode() helper now accepts clock_mappings=() and supplies it to Episode at construction.
Existing public signatures below are retained. run_session requires boolean
measurement_ready=true before serving, and now seals status=failed on invalid
matrix/session failure. main returns 3 for failed, 2 for refused, 0 for completed
or completed_with_flags.

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


Round-2 additions:

- coverage.Coverage(flags: tuple[str, ...], incomplete: bool, lost_reads: bool, max_gap_over_bar: float, max_cycle_over_two_expected: float)
- coverage.power_coverage(episode: Episode, measured_devices: Sequence[int] = ()) -> Coverage
- identity.model_identity_matches(identity: str, model: str) -> bool
- session.MatrixInputError(ValueError): invalid campaign input, caught into a failed receipt.
- Private replay seam: session._validate_output(path: Path, *, expected_count: int, router: bool, model: str, expected_coordinates: Sequence[tuple[str, str, int]] = (), measured_devices: Sequence[int] = (), power_metrics: dict[str, Any] | None = None) -> tuple[str, ...]. It fills the optional metrics dictionary used by each model receipt, including zero counts for unexecuted models.

Matrix v2 now requires reasoning_parser (string or null) and a dated
reasoning_parser_source per served agent/monitor. monitor_serving is the explicit
monitor spec, with id matching monitor_model. tool_call_parser (string or null),
tool_call_parser_source and enable_auto_tool_choice are also required, including
layout alternatives. No new CLI option or reviewer-harness signature change.

## TESTS RUN

### This seat: no executable runtime

Attempted `pwd` and `python3 --version` first. The execution tool rejected
the request before launching either process with "No usable execution environment
is available. Wait for an environment to become available before using this tool."
A subsequent `pwd` attempt failed identically. The environment wait remained
pending; cloud-environment-runtime status reported observed_phase=pending,
connectivity=offline, no runtime capabilities, and network-policy state unknown.
This is executor unavailability, not an automatic approval rejection.

Consequently there was no local checkout, git process, /etc/codex/network-policy.json
read, .review2 materialization/chmod, integration build, pip installation, test,
repro, compilation, subprocess census or manifest verification by this seat.
No fallback interpreter or remote test execution is claimed. The explicit
no-executor branch in fix2c permits GitHub edits and requires this disclosure.

Actually performed through GitHub tools/JavaScript (source checks, not Python tests):

- Read the existing report first, then PIPELINE.md, records.py and interfaces.py.
  Read AGENTS.md, targeted RUN_STATE intake/status/workspace sections, the empty
  TASK_QUEUE.md, M0, AGENT_PLAN.md and orchestration. ACTIVE_STOP_CARD is NONE.
  The explicit fix2c user task overrides normal queue selection; write scope
  overrides repository-wide bookkeeping and test commands.
- Confirmed the lane started at a37655231799dccd0339140f1dabf7d15bb42c8e.
- Pushed eb2b446ad7a459973c0fd5b45dee147c01ee217e through update_file on this
  lane only; read back its diff. Only the test helper signature, Episode keyword
  arguments, and the failing test's construction call changed. All assertions,
  numerical constants, gaps, clock domain, offset/uncertainty and skip guards remain.
- Confirmed PR #521 open, draft=true, merged=false with the corrected test at its head.
  No PR mutation, merge or rental was performed.

Own required commands below are all **NOT RUN**, counts/skips unknown at the
corrected head. Intended cwd is /workspace/JouleWise, without PYTHONPATH or package
installation, with TMPDIR=/tmp/gk-tmp and JW_B5_SYNTHETIC_ONLY=1:

    python3 -m unittest tests.align.test_gpukit -v
    python3 -m unittest tests.align.test_gpukit_round2 -v
    python3 -m unittest discover -s tests/align -t .
    python3 -m venv /tmp/gpukit-jsonschema
    /tmp/gpukit-jsonschema/bin/pip install jsonschema
    /tmp/gpukit-jsonschema/bin/python -m unittest tests.align.test_gpukit -v
    /tmp/gpukit-jsonschema/bin/python -m unittest tests.align.test_gpukit_round2 -v
    /tmp/gpukit-jsonschema/bin/python -m unittest discover -s tests/align -t .
    /tmp/gpukit-jsonschema/bin/python -I /workspace/JouleWise/.review2/r1/schema_probe.py /workspace/JouleWise

No extra dependency was installed by this seat. Do not infer a post-correction
pass from the lead's pre-correction run. The whole repository suite was not run,
as the brief directs. The required final-head stdlib/extra/schema runs remain
for an executing seat.

### Executed by the lead (local macOS) at a37655231

These results are supplied in the fix2c continuation brief, **not this seat's
execution**. Lead environment: Python 3.13, no PYTHONPATH, TMPDIR set,
JW_B5_SYNTHETIC_ONLY=1. Integrated tree used gpukit a37655231,
runner 52999e6a2 and nvml 95a37eef8, with the appendix harness unchanged and
no sibling patch. Those are the heads used for the results below; a later NVML
branch head is not silently substituted.

- `python3 -m unittest discover -s tests/align -t .`: 56 tests, 1 error,
  3 skipped (two require jsonschema, one requires the absent NVML lane).
  CoverageTests.test_interior_hole_is_not_widened_by_clock_uncertainty errored
  in Episode.__post_init__: PowerTrace domain 'sensor' has no ClockMapping.
  The post-construction replace never ran. eb2b446ad fixes that construction
  order; no assertion or expected answer changed.
- jsonschema was not installed on the lead's host. Extra-dependent tests and
  `schema_probe.py` were NOT RUN by the lead; this seat also could not run them.
  Separate verbose module runs were not supplied by the lead.
- Session CLI real-sampler runs ideal, noinstant, period100, l40s: 30 episodes
  per model, two models; brake calibration slice: 10 per model.
  All ten model runs: data_complete=true, zero incomplete on power, zero
  episodes with lost reads. Measured ratios and flags are in END-TO-END.
- `lead_rule.py` versus every receipt's power_coverage: counts equal exactly,
  both unrounded ratios relative difference 0.0 across all ten model runs
  (within the mandated 1e-6 relative exact-input arithmetic bar).
- `coverage.power_coverage` replay on the reviewer's ideal, period100,
  noinstant and l40s files; lead's one-lost-read noinstant file; period100
  with sensor facts removed; both 40 s probes: same counts and ratios to
  supplied printed digits. Exact replay comparison argv/unrounded outputs
  were not supplied for this older-file comparison; no stronger claim is made.
  two_samples_40s: all 30 incomplete by cycle. stall_40s: all 30 incomplete
  by hole, 30 with lost reads. Lead's noinstant lost-read file: 1 episode
  with lost reads, max gap/B=1.1347, complete.
- vLLM argv logs: --reasoning-parser qwen3 for Qwen/Qwen3-8B and
  Qwen/Qwen3-30B-A3B, no --enable-reasoning.
- Nonexistent matrix: status=failed, exit 3,
  matrix_read_failed:FileNotFoundError and session_failed:MatrixInputError;
  no nvidia-smi or vLLM call.
- GK2-3 identity bundle through the cost CLI: a basis entry for both models,
  30 observed episodes each, no calibration_model_missing.
- `session_probe.py`: ok, dup, short, onesample each data_complete=False with
  its reason flag. Hang finished in 5.5 s, orphan grandchildren alive: 0.
- `ready_probe.py`: worker orphans: 0; CLI MIG rc 2, status refused,
  preflight ran: False.
- noinstant: episode_power_channel_unsupported:gpu0:power_instant present.
  l40s: episode_power_sensor_period_from_driver_timestamps on power_instant
  and power_average. brake: throttle_hardware_counter_advanced:hw_power_brake.
  No world: throttle_power_limit_unavailable:enforced.

The lead's command families below are the appendix commands with its local
paths represented by $W (checkout), $I (integrated tree), $S=$W/.review2,
$H=$S/h, $R=$S/r1 and $D (local destination). The brief supplies the command
templates and results, not the lead's raw absolute-path transcript:

    for w in ideal period100 noinstant l40s; do
      GKR2_NVML=$w python3 -I $H/run.py $I $w configs/align/shade.json --runner-settings $H/settings-nvml.json --preflight-command '["preflight-ok"]' --ready-timeout-s 20 --command-timeout-s 120 --poll-s 0.2 --runner-timeout-s 500 --monitor-placement none --port 18761 --copy-kind local --destination $D
    done
    GKR2_BRAKE=1 GKR2_NVML=ideal python3 -I $H/run.py $I brake configs/align/shade.json --calibration-slice --runner-settings $H/settings-nvml.json --preflight-command '["preflight-ok"]' --ready-timeout-s 20 --command-timeout-s 120 --poll-s 0.2 --runner-timeout-s 500 --monitor-placement none --port 18762 --copy-kind local --destination $D
    python3 -I $S/make_probes.py $S/e2e/ideal/model-0/episodes.jsonl $S/probe
    python3 -I $S/lead_rule.py $S/e2e/*/model-*/episodes.jsonl $S/probe/*.jsonl
    python3 -I $S/make_ident.py $S/e2e/ideal $S/ident

Cost command from $I:

    python3 -m joulewise.align.gpukit.cost configs/align/shade.json --gpu-class H100-SXM-80GB --calibration $S/ident

Round-1 command templates:

    python3 -I $R/session_probe.py $W $R
    python3 -I $R/ready_probe.py $W $R

No appendix file/signature/CLI adaptation was made. The lead's reported integrated
runs replace the prior report's blanket NOT RUN status for those worlds, parser
logs, identity calibration and round-1 probes; they are still not final-head reruns
by this seat. Child PCI_BUS_ID, forced session_failed and modern/legacy limit
assertions were among the pre-correction unit tests, not separately reported
standalone harness repros. The lead supplied no separate cover.py output.

### Earlier evidence retained

At old head 28b9a22f4 the reviewer reported 41 alignment tests passed, two
jsonschema skips; with jsonschema 4.26, 41 passed with no skips. All round-1
repros and GK-S passed there. These historical passes do not substitute for
the required final-head schema tests.

The fix-2 seat actually read telegraf schema_v12 and schema_v13 types.go at
2156aa5089436522eec36b05fad94d850c728388 via GitHub; modern gpu_power_readings
uses current/requested limits and legacy power_readings uses enforced_power_limit.
Its source-only preservation audit retained all 37 original methods, with no
removed assertion, widened bar or new skip on an old method. Its original
52 gpukit source-method inventory was not an executed count; the lead's discovery
count is 56 alignment tests. This continuation changes neither inventory.

## END-TO-END

### Executed by the lead (local macOS) at a37655231

Chain: session CLI -> stub nvidia-smi whole-GPU inventory/preflight/vLLM ->
real runner (52999e6a2) -> real NvmlSampler (95a37eef8) over its ABI-shaped
fake NVML library -> twelve-turn/tool-call mock agent episodes on the host
monotonic clock -> production validator -> receipt/coverage metrics ->
SHA-256 packaging/local copy. This is synthetic execution, not real GPU evidence.

All five worlds had data_complete=true, no episode_power_coverage_incomplete,
no episode_power_missing, zero episodes incomplete on power and zero with lost
reads. Values below are supplied measurements, not new numbers chosen by this seat.
Each slash separates the two model runs. The lead supplied max(C/2E) only as the
overall range 0.749–0.750, so no invented per-model decimals are printed.

| Lead world at a37655231 | Episodes | Incomplete | With lost reads | max gap/B | max C/2E |
|---|---|---|---|---|---|
| ideal | 30/30 | 0/0 | 0/0 | 0.787/0.843 | 0.749–0.750 |
| noinstant | 30/30 | 0/0 | 0/0 | 0.825/0.808 | 0.749–0.750 |
| period100 | 30/30 | 0/0 | 0/0 | 0.729/0.809 | 0.749–0.750 |
| l40s | 30/30 | 0/0 | 0/0 | 0.796/0.764 | 0.749–0.750 |
| brake calibration slice | 10/10 | 0/0 | 0/0 | 0.737/0.504 | 0.749–0.750 |

The independent lead_rule.py replay matched the receipts on all ten model runs:
integer episode/incomplete/lost-read counts exactly, and both unrounded ratios
with relative difference 0.0 (mandated agreement bar: 1e-6 relative for identical
input arithmetic without an uncertainty).

noinstant retained the unsupported gpu0:power_instant note without marking data
incomplete; l40s derived periods from driver timestamps on the two field channels;
brake retained the hardware-power-brake advance. No unavailable-enforced-limit
flag remained. The argv logs showed qwen3 on both SHADE agents, without
--enable-reasoning. Identity replay produced two calibration basis entries,
30 observed episodes each, without calibration_model_missing.

The lead also replayed coverage on the reviewer's original worlds, a noinstant
world with one harmless lost read (max gap/B=1.1347, complete), period100 with
sensor facts removed, and both 40 s probes. Counts and ratios matched the
independent rule to supplied printed digits. two_samples_40s: 30/30 incomplete
by cycle, zero lost-read episodes. stall_40s: 30/30 incomplete by hole and 30
with lost reads. No new ruling is forced by these supplied results.

For comparison, the older R5 table from the fix-2 brief follows. These are the
lead/reviewer's independent-rule results on macOS at 28b9a22f4, not the session
validator's then-buggy completeness or this seat's measurements.

| Earlier supplied world | Episodes | Incomplete | With lost reads | max gap/B | max C/2E |
|---|---|---|---|---|---|
| ideal, reviewer | 30/30 | 0/0 | 0/0 | 0.864/0.907 | 0.745/0.748 |
| ideal, lead | 30/30 | 0/0 | 0/0 | 0.769/0.787 | 0.749/0.749 |
| period100 | 30/30 | 0/0 | 0/0 | 0.770/0.720 | 0.749/0.749 |
| noinstant, reviewer | 30/30 | 0/0 | 0/0 | 0.747/0.714 | 0.749/0.749 |
| noinstant, lead | 30/30 | 0/0 | 1/0 | 1.135/0.806 | 0.749/0.749 |
| l40s | 30/30 | 0/0 | 0/0 | 0.755/0.788 | 0.748/0.749 |
| brake | 10/10 | 0/0 | 0/0 | 0.793/0.710 | 0.749/0.748 |
| period100, facts removed | 30 | 0 | 0 | 0.770 | 0.749 |
| two_samples_40s | 30 | 30 (cycle) | 0 | 0.5 | 1988 |
| stall_40s | 30 | 30 (hole) | 30 | 1987.5 | 0.248 |

### Test world preserved by fix2c

The corrected test constructs twelve turns with production-sized token counts
and tool calls, then writes shared Episode JSONL and calls session._validate_output,
the same function the receipt uses. A sensor-clock power_instant trace has
10 ms typical gaps and one 25 ms interior gap, at 10 ms polling with 50 us
read half-width: D=0.1 ms, E=10.1 ms, median C=10 ms, B=20.2 ms.
The ClockMapping has offset 0 and uncertainty half-width 100 ms. That uncertainty
covers the edges but cancels in same-trace differences: 25 ms > 20.2 ms is a hole.

Previously Episode rejected the unmapped trace before the test could reach its
replace call. The helper now takes clock_mappings=() and the test passes the
mapping into the initial Episode constructor. Kept all three assertions:
incomplete, channel-specific hole flag present, edge flag absent. No number,
bar, gap, skip or assertion changed. The corrected world is **NOT RUN** by this
seat; the lead's run at a37655231 reached the constructor error, not these checks.

Other retained fixtures exercise clean off-boundary jitter (up to 18 ms on a
10 ms cadence), 100 ms deduplicated fields, unsupported empty channels, a 25 ms
covered counter/1 s averaged-power lost read versus an unaveraged-power hole,
and the two 40 s probe shapes. The round-1 boundary-sample complete world remains
unchanged: 60 Episodes, twelve turns, eight two-second tools, 40,000 prefill/
8,000 decode tokens, 148 virtual seconds and 1,481 samples per Episode; hand energy
148*280 - 8*2*80 = 40,160 J. These are fixture-design quantities, not physical
measurements or a new execution claim.

No integrated world, test or VM margin was measured by this seat. All own
end-to-end replays are **NOT RUN** because no executable environment launched.

## DECISIONS I MADE

Fix2c continuation decisions:

- Continue from a37655231 and retain the already-reviewed production fixes.
  Change only the erroring test construction and this report, since no new run
  exposed a production defect.
- Supply the ClockMapping when Episode first validates its trace domains.
  Keep the 25 ms hole, sensor clock, zero offset, 100 ms uncertainty, every
  assertion and all skip guards. Do not construct an invalid intermediate record.
- Use the authorized GitHub fallback when pwd/Python cannot launch. Do not
  fabricate a local checkout, harness materialization, test pass, installation
  or completed environment startup.
- Attribute every supplied result to the lead's local macOS run at a37655231;
  preserve its 56-test/one-error/three-skip outcome. Record the corrected head
  as unexecuted, and leave jsonschema/schema_probe and final-head reruns explicit.
- Keep the existing rental precision question and sibling requests. The lead's
  independent R5 agreement supplies no reason to change bars or counting policy.
- Use only the lane branch; no force push, PR merge/draft-state change or spend.

Retained fix-2 implementation decisions (historical seat actions are not new
claims of this continuation's execution):

- Continue the existing lane from 28b9a22f4, never restart from the spine.
  Use the brief's explicit GitHub fallback after shell launch failures.
  Push each requested step in order with expected-head, non-forced updates.
  Do not rent, merge, change PR draft status, delegate or touch other branches.
- Follow shared records over prose; never change the three protected files.
  All round-1 work/count rulings remain: budget has 36,000 fresh Episodes,
  26,400 monitor calls; forced two-call work is one Episode; deletion reuses
  generation; generic budget translation remains unavailable.
- R5's literal supported=false excludes a channel; other/missing notes count
  as supported. Group by channel prefix before colon, require supported
  evidence for each measured GPU and samples for every supported trace.
  power.empty alone no longer determines completeness.
- D sums twice the maximum recorded call half-width per supported trace/device.
  Only deduplicated fields use sensor period; absent facts use the driver's
  median microsecond timestamp step, with a provenance flag. Use notes'
  output averaging window, not the trace's older physical averaging field.
- Implement the ruled factors exactly: E=max(I+D,P), C=median(overlapping gaps)
  or E, cycle failure C>2E, B=2*max(C,E), edges>B+u, watts holes>max(B,A).
  Cumulative counters span gaps. Offset cancels inside a trace, so u widens
  edges only. Lost reads without a hole are flags and counts, not incomplete.
- Receipt metrics aggregate over every supported trace and count Episodes,
  including lost-read Episodes that are also incomplete on another trace.
  Models that cannot run carry zero checked counts/maxima, never a coverage
  success claim. Generic incompleteness and channel/check detail flags coexist.
- R6 chooses parser values only from each config entry. Hybrid Qwen3 uses qwen3:
  unlike deepseek_r1, it preserves thinking-off content without closing tags.
  Next Thinking and FP8 use deepseek_r1 because the template supplies <think>.
  vLLM 0.10.2 gets no --enable-reasoning. gpt-oss monitor gets null; SHADE/MoE's
  Qwen3-4B monitor gets qwen3. All monitors call no tools.
- Keep agent hermes explicitly per model with tool_call_parser_source_not_fetched
  rather than claiming an unfetched source. Automatic tool choice is explicit
  and off for monitors. Source attribution says lead-fetched, not seat-fetched.
- Quote the supplied hybrid serve example exactly from the pinned Qwen3-8B
  card; retain each hybrid model's supplied pinned card in model_card_url.
  Do not manufacture model-specific command quotations from an example.
- Keep serving revisions null. R7's provenance commits pin the supplied config/
  card evidence without silently selecting checkpoints. Quotes are verbatim,
  including the cards' "Paramaters" spelling; dimensions and count inputs/formulas
  are unchanged, as is the independent decode-weight test.
- Invalid/missing/unreadable matrix is a failed command before hardware probing.
  Any caught session_failed:* sets failed/data_complete=false. Exit 3 is distinct
  from refusal 2; completed/completed_with_flags keep 0. This is CLI status,
  not a new physical refusal or scientific admission rule.
- Set CUDA_DEVICE_ORDER=PCI_BUS_ID for both serving children; retain the explicit
  CUDA_VISIBLE_DEVICES pool/monitor separation. NVIDIA's canonical env-var
  reference is linked without claiming this seat fetched it.
- Share one delimited identity matcher between validator and calibration; a bare
  ID or vllm:<ID>@<URL> matches, another model or suffixed checkpoint does not.
  Preserve the separate declared-all-mock identity exception in validation.
- Modern current_power_limit supplies enforced limits; explicit legacy
  enforced_power_limit still wins. requested_power_limit (legacy power_limit
  fallback) is retained, and module readings cannot overwrite board readings.
  Telegraf v12/v13 sources were actually read through GitHub.
- Never weaken an old bar, remove an old test/assertion or add an old-test skip.
  The R5 slow-cycle expectation in the declared mock world is the only changed
  old expected result; the complete boundary-sample control is unchanged.
  New methods/guards do not claim execution.
- Separate actual GitHub/source checks from supplied old-head execution and
  unexecuted final-head commands. No synthetic fixture is hardware evidence.
  No new scientific question is inferred from an unavailable execution world.

## CONTRACT-CHANGE

No change requested to PIPELINE.md, records.py or interfaces.py.

Request to the NVML lane: take a closing sample in stop() so the episode end has
a bracketed final reading. R5 is implemented without depending on that change.

Retain the request for per-sample clock-event/throttle reasons and cumulative
violation durations, using NVML violation/event calls where supported; before/
after XML cannot place a brake within an Episode. Unsupported telemetry stays
flagged. No out-of-scope NVML edit was made.

Budget's lane-local adapter must preserve effort, pairing, calibration and reuse
identity while exporting fresh shared Episodes; shared benign/sabotage condition
and physical work accounting remain unchanged.

## OPEN ISSUES

- Corrected-test/final-head execution is unavailable in this seat. The lead's
  a37655231 run had 56 tests, one constructor error (fixed in eb2b446ad),
  three skips; rerun discovery and both verbose gpukit modules at the new head.
  No post-correction pass is claimed.
- jsonschema installation, extra-dependent reruns and schema_probe.py remain
  NOT RUN by this seat and were also absent from the lead's a37655231 run.
  An executing seat must run them in a throwaway venv. Their old-head pass
  does not validate the revised schema.
- The lead already executed the integrated tree with runner 52999e6a2 and
  nvml 95a37eef8: clean worlds complete, probe worlds incomplete, independent
  metrics equal, identity calibration and round-1 cleanup/MIG checks passed.
  These results are attributed in TESTS RUN/END-TO-END; no corrected-head
  rerun, VM measurements or hardware readiness is established here.
- Budget driver/session integration remains unavailable (GK2-8): expand() trial
  counts and coordinates do not match generation Episodes, including calibration
  and hinted/paired work. A budget-specific translator/validator is required.
- Budget driver must check content beginning with <think> under qwen3 when
  max_tokens truncates a hybrid thinking block before </think>; parser output
  then lands in content. This lane cannot edit budget/run.py.
- hermes's source was not fetched; retained agent settings carry an explicit flag.
  Model/tokenizer/data/serving revisions and device/layout fit still need freezing
  and an actual serving preflight, before paid work.
- Full rental-time/cost extrapolation still lacks measured setup/load/off-box
  waits and budget strata. Costs remain unavailable when those inputs are null.
  Approve only a separately capped calibration slice with provider shutdown.
- NVML closing/per-sample throttle requests remain sibling-owned. Whole-GPU
  hardware support, sensor behavior, MoE worker router capture and production
  factory registration still need integrated offline rehearsal and live preflight.
- Lead-owned independent review, CI, cold merge review and merge remain pending.
  PR #521 stays draft. No spend/provider/rental approval was sought or presumed.

## NEEDS_RULING

Retained configuration question before any budget rental: BF16 on four H100-SXM
80 GB GPUs (160 GB weights in 320 GB capacity), or the published FP8 checkpoint
on two (about 80 GB ideal weights in 160 GB capacity before scales/KV/allocator).
Recommendation: BF16/4 if Ed approves the cost, preserving common precision;
otherwise record FP8/2 as a distinct configuration. Blocked work is real budget
allocation/measurement, not code authoring. Explicit headroom/provider/price/spend
are operator inputs, not invented defaults. No new R5 science ruling is requested:
the lead's supplied independent replay supports the rule, and this seat has
no new executed evidence. The retained rental configuration question is not a
blocker to this test/report correction.

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
