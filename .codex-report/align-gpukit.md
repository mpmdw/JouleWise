# align-gpukit — FIX ROUND 2

## SUMMARY

Continued lane/2026-10-21-align-gpukit from 28b9a22f4bccd0bd7fc52a8618b3da58e1b053ad.
Implemented GK2-1 through GK2-7; GK2-8 is informational and unchanged.
R5 checks supported-channel cadence, edges and power holes, recording covered read loss and per-model margins.
Every served model now declares its reasoning/tool parsers and sources; Qwen3-Next uses deepseek_r1.
Invalid matrices fail before hardware calls; failed sessions exit 3, refusals 2, completed sessions 0.
CUDA children use PCI_BUS_ID; calibration shares identity matching; modern enforced/requested limits are retained.
Replaced model dimension/count provenance with the lead's verbatim pinned HF quotations without changing numerical inputs.
Preserved all 37 prior test methods; source inventory is now 52 gpukit methods, not an executed test count.
No shell/Python process, test, repro, package installation or integrated world ran: executor startup never became usable.
All steps were fast-forward pushed through the authorized GitHub fallback; PR #521 remains draft, unmerged, with no rental.

## FILES

Round-2 changes (each within WRITE_SCOPE):

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
- tests/align/test_gpukit_round2.py: 14 new source methods for R5 worlds, per-model argv/schema, failure exits, identity calibration and provenance/limits.
- docs/align/gpukit.md: reconciled R5 completeness, parser provenance, exit codes, CUDA ordering and modern-driver limits.
- .codex-report/align-gpukit.md: current handoff, NOT RUN inventory and retained round-1 FIX LOG plus Round 2 block.

Unchanged lane modules remain bootstrap.sh (preinstall whole-GPU check/pinned
install), runner_adapter.py (runner translation), throughput.py (decode weights
and decimal display), and __init__.py. No registry exceptions. No changes to
PIPELINE.md, records.py, interfaces.py, sibling lanes or any other repository
path. No .review2 harness/evidence was committed or materialized.

## PUBLIC API

All modules are under joulewise.align.gpukit; private helpers are omitted.
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

**No shell or Python process launched in this seat.** Initial and repeated
attempts of `pwd` and `python3 --version` failed before launch with
"No usable execution environment is available. Wait for an environment to become
available before using this tool." The environment wait stayed pending; runtime
status reported observed_phase=starting and connectivity=offline. Therefore no
local checkout, git command, /etc/codex/network-policy.json read, .review2 copy,
chmod, integrated tree, test, repro or pip installation was possible.
This is executor unavailability, not an automatic approval rejection.
The brief explicitly authorizes GitHub fallback in this case.

Actually performed (GitHub tools/JavaScript only, not Python tests):

- Read the existing report first; then the three shared contracts, AGENTS.md,
  targeted RUN_STATE intake/status, empty TASK_QUEUE, M0 and orchestration.
  ACTIVE_STOP_CARD is NONE. No local workspace state could be inspected.
- Confirmed starting branch head 28b9a22f4 and PR #521 open/draft/unmerged.
  Each pushed commit has the previous lane head as parent; ref updates used
  expected_sha and force=false.
- Read telegraf schema_v12 and schema_v13 types.go at
  2156aa5089436522eec36b05fad94d850c728388 through GitHub. Both modern
  gpu_power_readings structs expose current/requested limits; legacy
  power_readings exposes enforced_power_limit.
- Read NvmlSampler notes construction from the sibling branch: supported,
  timing_half_width_ns, field_timestamps_us, sensor_facts and
  output_averaging_window_ns match the new coverage inputs.
- GitHub comparison at b259f5f showed seven commits ahead, zero behind, exactly
  13 changed code/config/test/runbook files in scope. Subsequent source-audit/test
  commits also touch only those paths; the final report is the fourteenth.
- Read back all 13 code/config/test/runbook files at 163f943f and compared them
  exactly with authored text. Later 22fbf2fc strengthens only the new R5 tests.
  b14078f2 quotes R6's supplied hybrid Qwen3-8B example exactly; each model's
  separate pinned card URL remains recorded without invented command quotes.
- Final readback at b14078f2: all 13 changed code/config/test/runbook files
  matched authored text exactly; there were no readback errors. This is byte
  custody/source checking, not compilation or execution.
- Source comparison: no old test method removed, no new skip on an old test,
  no deleted old assertion or widened bar. The independent hand arithmetic,
  decode-weight test and complete-session positive control are byte-identical
  to 28b9a22f4. The single changed old expectation is explained in FIX LOG.
- Source inventory: 38 methods in test_gpukit.py and 14 in
  test_gpukit_round2.py. These are NOT run counts. Three jsonschema guards
  (two retained, one new) use reason "optional jsonschema is not installed";
  the existing Bash guard remains. Actual counts/skips are unknown.

Reviewer-supplied evidence at **old head 28b9a22f4**, not this seat's execution:
41 alignment tests passed with two optional-jsonschema skips; with jsonschema
4.26, 41 passed with no skips. All round-1 repros and GK-S passed there.
The reviewer/lead's real-sampler worlds exposed GK2-1 and parser/provenance/wiring
findings; their R5 table is retained below. None establishes a final-head pass.

All commands below are **NOT RUN**, with pass/failure counts and actual skips
unknown. From /workspace/JouleWise, uninstalled repository, no PYTHONPATH, with
TMPDIR=/tmp/gk-tmp and JW_B5_SYNTHETIC_ONLY=1:

    python3 -m unittest tests.align.test_gpukit -v
    python3 -m unittest tests.align.test_gpukit_round2 -v
    python3 -m unittest discover -s tests/align -t .

Extra-dependent setup and reruns, also **NOT RUN**:

    python3 -m venv /tmp/gpukit-jsonschema
    /tmp/gpukit-jsonschema/bin/pip install jsonschema
    /tmp/gpukit-jsonschema/bin/python -m unittest tests.align.test_gpukit -v
    /tmp/gpukit-jsonschema/bin/python -m unittest tests.align.test_gpukit_round2 -v
    /tmp/gpukit-jsonschema/bin/python -m unittest discover -s tests/align -t .

No extra dependency was installed. No repository-wide test suite was run, as
directed. Compilation, subprocess cleanup and manifest verification are NOT RUN.

### Integrated repros — all NOT RUN

No .review2 files could be written; use the verbatim appendix files and chmod
the h/bin, r1/bin and r1/bin503 stubs. No harness or CLI adaptation is needed.

The brief's integrated heads are runner 52999e6a2a7e165901dcfe813cc7ae68157c59ea
and NVML 95a37eef8. No integrated head was actually executed. A GitHub metadata
check later found runner still at 52999e6a2 and NVML advanced to
4244d060836ccfdcb6f47209ab4df00e5f3fab71; record whichever NVML head is used
for the lead's rerun. The notes-source read above came from that later branch.
There was no runner patch and no claim that an integrated tree was built.

Requested construction, **NOT RUN**:

    git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-runner lane/2026-10-21-align-nvml
    rm -rf /tmp/gk-integ
    mkdir -p /tmp/gk-integ /tmp/gk-tmp /tmp/gk-dest
    git -C /workspace/JouleWise archive HEAD | tar -x -C /tmp/gk-integ
    git -C /workspace/JouleWise archive origin/lane/2026-10-21-align-runner joulewise/align/runner.py joulewise/align/mock_world.py joulewise/align/__main__.py joulewise/align/tamper.py | tar -x -C /tmp/gk-integ
    git -C /workspace/JouleWise archive origin/lane/2026-10-21-align-nvml joulewise/align/power | tar -x -C /tmp/gk-integ
    cp /workspace/JouleWise/.review2/h/gkr2fix.py /tmp/gk-integ/gkr2fix.py

Each real-sampler world, **NOT RUN** (remove any prior output for that world
before a replay; no prior output exists from this seat):

    export TMPDIR=/tmp/gk-tmp JW_B5_SYNTHETIC_ONLY=1
    H=/workspace/JouleWise/.review2/h
    for w in ideal period100 noinstant l40s; do
      GKR2_NVML=$w python3 -I $H/run.py /tmp/gk-integ $w configs/align/shade.json --runner-settings $H/settings-nvml.json --preflight-command '["preflight-ok"]' --ready-timeout-s 20 --command-timeout-s 120 --poll-s 0.2 --runner-timeout-s 500 --monitor-placement none --port 18761 --copy-kind local --destination /tmp/gk-dest
    done
    GKR2_BRAKE=1 GKR2_NVML=ideal python3 -I $H/run.py /tmp/gk-integ brake configs/align/shade.json --calibration-slice --runner-settings $H/settings-nvml.json --preflight-command '["preflight-ok"]' --ready-timeout-s 20 --command-timeout-s 120 --poll-s 0.2 --runner-timeout-s 500 --monitor-placement none --port 18762 --copy-kind local --destination /tmp/gk-dest
    python3 -I $H/cover.py /tmp/gk-integ /workspace/JouleWise/.review2/e2e/*/model-*/episodes.jsonl

Probe generation, independent lead replay, identity calibration and round-1
regressions, **all NOT RUN**:

    S=/workspace/JouleWise/.review2
    python3 -I $S/make_probes.py $S/e2e/ideal/model-0/episodes.jsonl $S/probe
    python3 -I $S/lead_rule.py $S/e2e/*/model-*/episodes.jsonl $S/probe/*.jsonl
    python3 -I $S/make_ident.py $S/e2e/ideal $S/ident

From /tmp/gk-integ, also **NOT RUN**:

    python3 -m joulewise.align.gpukit.cost configs/align/shade.json --gpu-class H100-SXM-80GB --calibration /workspace/JouleWise/.review2/ident

Round-1 commands, **NOT RUN**, no script-call adaptation:

    R=/workspace/JouleWise/.review2/r1
    python3 -I $R/session_probe.py /workspace/JouleWise $R
    python3 -I $R/ready_probe.py /workspace/JouleWise $R
    /tmp/gpukit-jsonschema/bin/python -I $R/schema_probe.py /workspace/JouleWise

Remaining finding-specific repros, **all NOT RUN**: inspect every vLLM argv log
for its matrix parser/no --enable-reasoning; capture every child's PCI_BUS_ID;
missing-matrix session must exit 3 without any SMI/preflight/vLLM call; forced
session_failed must exit 3; MIG must still exit 2 with no preflight; v13 enforced
and requested limits must be retained without an unavailable-enforced flag.
The tests author each of these checks, but authoring is not execution.

The production replay seam is _validate_output(..., power_metrics=metrics).
For every world/probe file, compare metrics.episodes_checked,
episodes_incomplete_on_power and episodes_with_lost_reads with the independent
lead_rule.check results exactly. Compare unrounded max_gap_over_bar and
max_cycle_over_two_expected at 1e-6 relative, the brief's exact-input arithmetic
bar. Print data_complete via the same _incomplete_flag predicate as run_session.
Both probes must be false with channel/check flags; clean worlds true, with
unsupported/read-loss/provenance notes retained. This comparison is **NOT RUN**;
there is no observed agreement or discrepancy to report.

## END-TO-END

**No world was run by this seat.** No observed final-head counts, margins,
durations, joules, child environments, manifests or exit statuses are claimed.

The requested chain is session CLI -> stub whole-GPU inventory/preflight/vLLM ->
real runner -> real NvmlSampler over ABI-shaped fake NVML -> 12-turn/tool-call
mock agent episodes on host monotonic time -> production output validator ->
receipt/margins -> SHA-256 manifest/archive -> local transfer. The requested
worlds are 30 Episodes/model (60 total); brake's calibration slice is 10/model
(20 total). These are requested/design counts, not this seat's results.

Lead/reviewer R5 evidence (from the fix-2 brief, their macOS execution at
28b9a22f4, **not this seat's measurements**). Each model's values are separated
by a slash. Our VM columns are all NOT RUN.

| Supplied world | Episodes | Incomplete | Lost reads | max gap/B | max C/2E | This seat |
|---|---|---|---|---|---|---|
| ideal, reviewer | 30/30 | 0/0 | 0/0 | 0.864/0.907 | 0.745/0.748 | NOT RUN |
| ideal, lead | 30/30 | 0/0 | 0/0 | 0.769/0.787 | 0.749/0.749 | NOT RUN |
| period100 | 30/30 | 0/0 | 0/0 | 0.770/0.720 | 0.749/0.749 | NOT RUN |
| noinstant, reviewer | 30/30 | 0/0 | 0/0 | 0.747/0.714 | 0.749/0.749 | NOT RUN |
| noinstant, lead | 30/30 | 0/0 | 1/0 | 1.135/0.806 | 0.749/0.749 | NOT RUN |
| l40s | 30/30 | 0/0 | 0/0 | 0.755/0.788 | 0.748/0.749 | NOT RUN |
| brake | 10/10 | 0/0 | 0/0 | 0.793/0.710 | 0.749/0.748 | NOT RUN |
| period100, facts removed | 30 | 0 | 0 | 0.770 | 0.749 | NOT RUN |
| two_samples_40s | 30 | 30 (cycle) | 0 | 0.5 | 1988 | NOT RUN |
| stall_40s | 30 | 30 (hole) | 30 | 1987.5 | 0.248 | NOT RUN |

Authored production-path worlds, **design arithmetic only**:

- R5 JSONL worlds use shared Episode/Turn/ToolCall/PowerTrace records, twelve
  turns with 1,200 prefill/160 decode tokens each, and a two-second synthetic
  clock bracket. Notes carry the real sampler's supported/timing/sensor/driver/
  averaging keys; samples are off boundaries.
- Clean world: 10 ms median spacing, one 18/2 ms jitter pair, 5 ms head and
  15 ms tail on energy; a separate 100 ms deduplicated average ends 95 ms
  before the episode end; an unsupported empty instantaneous channel remains.
  Supported read calls each have 50 us half-width: D=0.2 ms, energy B=20.4 ms.
  The independent analytic expectations are max gap/B=18/20.4 and max C/2E=0.5,
  with no power incompleteness/read loss. These assertions have NOT RUN.
- One 25 ms gap with 10 ms median cadence exceeds B=20.2 ms for one channel.
  The cumulative counter and a 1 s averaged watt trace record lost reads and
  remain complete; an unaveraged watt trace has a hole. A 25 ms tail fails
  the edge; 5 ms clock-offset uncertainty covers that excess only at edges.
  A separate 100 ms offset half-width cannot hide an interior 25 ms hole.
- The two 40 s probes retain all four NVML-shaped channels. A two-sample
  trace fails cycle; a 39.99 s interior stall fails watt-hole checks while the
  energy counter records read loss. Incomplete and lost-read episode counts
  are asserted independently. No result is claimed.
- Existing complete production-shaped session fixture remains unchanged:
  bootstrap/session/stub endpoint/real subprocess runner writes 60 Episodes,
  twelve turns, eight two-second tools, 40,000 prefill/8,000 decode tokens,
  148 virtual seconds and 1,481 samples per Episode. Its hand energy is
  148*280 - 8*2*80 = 40,160 J. The boundary-sample positive control remains.
  This is fixture design arithmetic; it was NOT RUN here.
- New v13 session fixture follows the real session/subprocess/package path,
  asserting enforced "700.00 W" from current_power_limit and requested
  "650.00 W". These are exact XML strings, not a physical measurement.
- Identity calibration writes both models' endpoint-form agent_model identities
  through real JSONL and cost.estimate; basis count/identity and two-second
  mean duration are asserted. It was NOT RUN.

## DECISIONS I MADE

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

- Every Python/shell test and repro above is NOT RUN; no final-head execution,
  independent arithmetic replay agreement, cleanup census, manifest pass or
  hardware readiness is established. The lead must execute the appendix worlds
  and compare unrounded metrics with lead_rule.py before accepting the fix.
- The integrated tree was not built; NVML advanced beyond the brief's head.
  Record the actual sibling SHAs and rerun without silently patching their code.
  Runner's earlier SyntaxError is fixed per the brief, so no patch was authored.
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
this seat has no executed evidence that contradicts the supplied rule.

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


### Round 2

"fixed" means implementation fast-forward pushed, **not an executed pass**.

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

Round-2 appendix changes: none. Files were not materialized because no executor
launched; no new CLI option or harness-call adaptation was required. All reviewer/
lead repros and all tests are NOT RUN, including the stdlib and extra-dependent
runs; actual counts/skips/ratios are unknown. The lead's table above is supplied
evidence, never this seat's result.
