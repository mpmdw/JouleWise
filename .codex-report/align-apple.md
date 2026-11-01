# align-apple — fix2c lead verification record

## SUMMARY

Continues lane/2026-10-21-align-apple from c94b2f648b2ccaac762dfcd849516c2cfe842056, preserving parent history.
This continuation changes only this report and docs/align/apple_path.md; source fixes in a17561bc3 and c94b2f648 remain unchanged.
The lead executed all 30 lane tests at c94b2f648 on local macOS in 97.6 s: OK.
The unchanged reviewer repros confirm structured runtime failures, partial evidence retention, token caps and identity parity.
Parsing, finite-score handling, hidden-prefill accounting and malformed-spec outcomes passed the lead's checks.
The four-member synthetic CLI campaign succeeded with a 22.500000000009436 J sabotage effect against 22.5 J predicted, and strict validation clean.
The 16 existing modules ran 450 tests with one known spine shard failure, zero errors and zero skips.
This cloud seat executed zero Python tests because no process could start; the executed acceptance evidence is attributed to the lead.
The mock-only condition-correlated hidden-prefill availability flag is disclosed; hardware, registration and other lead-owned issues remain open.

## FILES

Changed in this fix2c verification continuation, starting at c94b2f648:

- .codex-report/align-apple.md — lead-attributed executed results, per-finding outputs, updated acceptance status and mock-flag disclosure.
- docs/align/apple_path.md — execution history and the lead's completed acceptance checks in place of the pending-verification paragraph.

No source, tests or registries are changed in this continuation.

Earlier second-review changes against 86f441c93 (retained for handoff context):

- joulewise/align/apple/endpoint.py — native finish-reason observation around the unchanged MLX generator; enforced mock cap/default finish semantics; complete think-span extraction; Qwen/Llama tool parsing and malformed/unsupported flags; per-turn prior_hidden_prefill_tokens.
- joulewise/align/apple/workload.py — spec shape/temperature validation; finite score handling; fault/cut episode outcomes; UNKNOWN_ERROR on runtime faults after returned work; buffered failure-artifact salvage using EvidenceCustodyProvider.
- tests/align/test_apple_endpoint.py — five new tests through run_benchmark with only the native mlx_lm module and distribution-version lookup injected; native faults on both clocks, stop/length semantics, parsing, NaN scorer, prior-hidden prefill and full governed identity parity.
- tests/align/test_apple_campaign.py — two new SystemClock tests for malformed specs and actual mock budget enforcement; existing partial-fault regression now requires the authorized structured failure while retaining partial counts/flags/raw energy; existing ambiguous-budget fixture explicitly supplies finish_reason=None.
- docs/align/apple_path.md — execution/failure semantics, finish reasons, supported parsing, transcript choice and prefill counterfactual, measured repeatability source and lead-attributed fix2c verification.
- .codex-report/align-apple.md — current report and per-finding FIX LOG.

No registry file is changed in this continuation. Existing modules contain the
new tests, so no module registry names are added. The original workload registry
is joulewise/adapters/__init__.py; the earlier minimal
configs/gates/hazard_refusals.json census exemption is unchanged.
No protected contract, controller, reducer, shared MLX adapter, hazard, or
machine-state file is modified. No .review3 script is committed.

This seat read the report first, then PIPELINE.md, records.py and interfaces.py.
Inspected root AGENTS.md, the generated stop/queue pointers, Mission M0 and
orchestration. No active stop card/global gate applied; the direct brief selects
this bounded AGENT documentation work. docs/AGENTS.md, docs/align/AGENTS.md and
.codex-report/AGENTS.md return 404 at c94b2f648. TASK_QUEUE.md needed the Git blob
reader because the contents reader returned an empty payload for the large file.
The previous seat read the workload/generator/adapter registration surfaces and
powermetrics/fiducial/kernel-clock/transition machinery; their implementations
and anchor remain unchanged here. Historical reports remain in Git at
[86f441c93](https://github.com/mpmdw/JouleWise/blob/86f441c938a803e8f98d08326fb84685ddaa2ecf/.codex-report/align-apple.md)
and [c94b2f648](https://github.com/mpmdw/JouleWise/blob/c94b2f648b2ccaac762dfcd849516c2cfe842056/.codex-report/align-apple.md).

## PUBLIC API

No public API changes in this fix2c verification continuation. Retained API under
joulewise.align.apple, including the second-review custody hook:

- sampler.seconds_ns(seconds: float) -> int
- sampler.monotonic_ns(stamp: ClockStamp) -> int
- sampler.stamp_mapping(stamps: Sequence[ClockStamp], *, episode_domain: str, evidence: Mapping[str, Any] | None = None) -> tuple[ClockMapping, tuple[str, ...]]
- sampler.power_records(samples: Sequence[PowerSample], *, nominal_interval_ns: int, evidence: Mapping[str, Any] | None = None) -> tuple[tuple[PowerTrace, ...], tuple[str, ...]]
- sampler.ApplePowerSampler(config: BenchmarkConfig, clock: Clock, *, episode_domain: str, context: RunContext | None = None, adapter: Any | None = None)
- ApplePowerSampler.start() -> None
- ApplePowerSampler.stop() -> tuple[PowerTrace, ...]
- ApplePowerSampler.clock_mappings, flags, uncertainty_evidence expose adapter/bridge evidence.
- endpoint.parse_completion(text: str, *, reasoning_tokens: int = 0) -> tuple[str, str, tuple[ToolCallRequest, ...], tuple[str, ...]]
- endpoint.MlxEndpoint(runtime: Any, config: BenchmarkConfig, clock: Clock, *, episode_domain: str, prepare_metadata: Mapping[str, Any] | None = None, mock_turns: Sequence[Mapping[str, Any]] = ())
- MlxEndpoint.chat(messages: Sequence[ChatMessage], *, tools: Sequence[Mapping[str, Any]] = (), max_tokens: int, temperature: float, seed: int | None) -> ChatResult
- workload.EpisodeSpec(task_factory: str, condition: Condition, seed: int, max_turns: int, max_tokens: int, temperature: float, task_kwargs: Mapping[str, Any] = {}, mock_turns: tuple[Mapping[str, Any], ...] = (), schema: str = SPEC_SCHEMA)
- EpisodeSpec.to_text() -> str
- EpisodeSpec.from_text(text: str) -> EpisodeSpec
- workload.EpisodeRuntimeAdapter(runtime: Any, clock: Clock)
- EpisodeRuntimeAdapter.prepare(config: BenchmarkConfig, context: RunContext | None = None) -> AdapterResult
- EpisodeRuntimeAdapter.identity_projection_metadata(config: BenchmarkConfig) -> dict[str, Any]
- EpisodeRuntimeAdapter.warmup(config: BenchmarkConfig, context: RunContext | None = None) -> AdapterResult
- EpisodeRuntimeAdapter.run_workload(config: BenchmarkConfig, context: RunContext | None = None) -> RuntimeResult
- EpisodeRuntimeAdapter.salvage_custody(context: RunContext) -> list[dict[str, Any]] — existing optional controller protocol, now implemented here for buffered failures.
- EpisodeRuntimeAdapter.cleanup(config: BenchmarkConfig, context: RunContext | None = None) -> AdapterResult
- workload.read_episode_bundle(bundle: Path) -> Episode
- campaign.generate_campaign(base: BenchmarkConfig, specs: Sequence[EpisodeSpec], output_root: Path, *, model_tag: str, counterbalance: bool = True) -> tuple[Path, ...]

New lane-local data:

- Mock script finish_reason defaults to stop for a completion fitting max_tokens;
  an oversize completion is generated at max_tokens and records length, with
  proportional text truncation explicitly flagged. Explicit None exercises the
  no-native-reason fallback.
- align_turns.jsonl generation records finish_reason, the adapter's original
  runtime_stop_condition on MLX, and prior_hidden_prefill_tokens/method.
  The latter is an integer token-count difference for MLX, zero without prior
  recognized hidden spans, or null/flagged when scripted mock counts do not
  provide the counterfactual. Negative deltas are kept with a flag.
- episode_outcome uses endpoint_error/episode_error for faults,
  turn_budget_reached for episode turn exhaustion, turn_token_budget_reached
  when a per-turn cut occurred, otherwise episode_returned.
- A partial runtime fault is a structured failed/unknown_error member. Its
  summary failure_message contains the outcome and original fault flag.
  outputs/align_failure.json retains outcome, provenance and realized counts;
  align_runtime_events.jsonl retains completed-call events. The episode,
  transcript and turn rows are preserved too; cleanup metadata repeats outcome.
  Zero-output failures retain the previous no-episode-artifact behavior.

## TESTS RUN

**Own executed Python count: 0.** No own pass/fail/skip counts or reviewer
repro outputs exist. No dependency was installed and no extra-dependency run
occurred here. The managed environment reported observations_current=true,
observed_phase=starting, connectivity=offline and capabilities=[].
The initial pwd check and the lane-test attempt below failed before process
creation; even mktemp did not execute. The test command was submitted with
workdir /workspace/JouleWise.

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR="$(mktemp -d /tmp/align-apple-fix2c.XXXXXXXX)" python3 -m unittest discover -s tests/align -t .
```

Tool error:

    No usable execution environment is available. Wait for an environment to become available before using this tool.

Local fetch/checkout/status and /etc/codex/network-policy.json could not be read.
GitHub inspection confirmed the starting branch head was exactly c94b2f648.
Documentation commits use the existing tree, one parent, force=false and an
expected-head lease on the apple branch only. No local user files are touched.
Source-text consistency checks through the GitHub connector and JavaScript
orchestration are not counted as Python tests. The prior seat's submitted,
unlaunched commands remain in the historical c94b2f648 report.

**Lead's executed results at c94b2f648** (supplied in this continuation brief):
local macOS, /opt/homebrew/bin/python3.13, JW_B5_SYNTHETIC_ONLY=1, fresh TMPDIR
per run, detached worktree at c94b2f648. The reviewer's APPENDIX harnesses from
the fix2 brief were unchanged. These are the lead's results, not this seat's.

    python3 -m unittest discover -s tests/align -t .

Ran 30 tests in 97.6 s, OK. No skips were reported.

The lead also executed the reviewer's 16 existing modules:

    python3 -m unittest tests.hazards.test_refusal_allowlist tests.test_shard_tests tests.test_mlx_runtime tests.test_adapters_powermetrics tests.test_mock_adapters tests.test_shard_split tests.test_fixture_orphan_census tests.test_custody_mode_inventory tests.test_revision_five_b_readers tests.test_single_count_discipline_census tests.test_digest_pin_census tests.test_identity_pins tests.test_repin tests.test_window_lineage tests.hazards.test_battery tests.test_controller_hazard_flags

Ran 450 tests, 1 failure, 0 errors, 0 skipped. The sole failure is
tests.test_shard_tests.ShardPartitionInvariantTests.test_union_is_full_discover_set_and_partitions_are_disjoint:
the known spine mismatch align.test_records versus tests.align.test_records
(finding 9), with the same count as the reviewer's run. It is untouched here.

Lead-supplied harness/check invocations are recorded as supplied below;
ephemeral directory arguments are not reconstructed. Per-finding outputs are
in FIX LOG; the other-path outputs and synthetic campaign numbers are in
END-TO-END.

| Command/check | Lead's result at c94b2f648 |
|---|---|
| e2e_mlx_r2.py raise0 | failed/unknown_error; no_model_call_returned_tokens plus original fault |
| e2e_mlx_r2.py raise | failed/unknown_error after 180 tokens; partial failure artifacts retained |
| edge_r2.py reset_raises; sysclock_r2.py reset_raises | unsupported/runtime_unavailable under both clocks |
| e2e_mlx_r2.py truncate | succeeded; cut and malformed-envelope flags, outcome emitted_tokens=480, strict [] |
| edge_r2.py mock_over_budget | succeeded, 2 turns, decode 1420, cap/truncation/malformed flags |
| e2e_cli_r2.py | all 4 members succeeded, no turn-budget flags; derived energy and per-turn agreement confirmed |
| e2e_mlx_r2.py normal; e2e_mlx_r2.py truncate; e2e_mlx_r2.py think | harvest/arm identity ab28006118e6c92f, fixed episode policy agrees, strict [] each |
| mlx_plain_ref.py | plain MLX harvest/arm identity 0928802c004cc79c agrees |
| strict_identity.py on CLI members | strict [], identity ok 39db4c7bdeaa for both align members |
| parse_completion, direct reviewer cases | prefilled/multiple think spans, Llama JSON and python-tag calls, unsupported/malformed/plain-prose cases agree |
| edge_r2.py score_nan | succeeded, score None, finite-score flag, 8 turns, 699.375 J |
| e2e_mlx_r2.py think | prior-hidden prefill counts 0, 0, 74, 74, method chat_template_token_count_difference |
| edge_r2.py spec_temperature_nan; edge_r2.py spec_temperature_str | unsupported/runtime_unavailable, temperature must be numeric and finite |
| edge_r2.py spec_extra_key; edge_r2.py spec_max_turns_bool; edge_r2.py factory_no_colon | unsupported as before |
| docs/align/apple_path.md, measured repeatability citation | 0.29–0.49 J cited; no "approximately 0.3 J" remains |
| sysclock_r2.py normal | succeeded, 17.59 J, 3 turns, 2 tool calls, strict [] |
| hazard_r2.py | succeeded, 721.8747 J, 8 turns/tools, hidden 300, strict [] |
| edge_r2.py tool_returns_dict; edge_r2.py score_raises; edge_r2.py max_turns_1; edge_r2.py temperature_0.7 | succeeded with the respective disclosure flags, unchanged from the reviewer's run |

No extra-dependency installation/run was supplied for the lead's c94b2f648
verification. The injected native-library worlds above are production-path
synthetic checks; they are not fresh real-model or hardware measurements.

Earlier attributed evidence, retained as history:

| Source | Command/check | Result |
|---|---|---|
| Lead, 86f441c93 | python3 -m unittest discover -s tests/align -t . | 23 tests, all OK, 47.6 s; earlier fix2c strict campaign correction executed |
| Lead, 86f441c93 | e2e_mlx_r2.py normal/truncate/think | strict []; harvest/arm ab28006118e6c92f; agent_episode / episode_returns_or_turn_budget_reached |
| Lead, 86f441c93 | e2e_mlx_r2.py raise0 | failed/unknown_error; no_model_call_returned_tokens |
| Lead, 86f441c93 | edge_r2.py and sysclock_r2.py reset_raises | unsupported/runtime_unavailable; task_unavailable:RuntimeError |
| Lead, 86f441c93 | sysclock_r2.py normal | succeeded, 17.14 J; uncertainty 2263 ns; first token within 477 ns; strict clean |
| Reviewer, b7739911b | 16 existing modules listed above | 450 ran, one pre-existing spine shard failure |
| Reviewer, b7739911b | tests/align | 19 ran, all passed |

Skip counts/reasons were not separately supplied for those older historical
runs. Seven tests added by the previous seat are now included in the lead's
executed 30-test result. No test was skipped, deleted or weakened here.

## END-TO-END

This seat executed no Python. The lead completed the acceptance runs at
c94b2f648; the fixture descriptions below are retained from the source-fix
report. The added tests use real run_benchmark and either
SystemClock or MLX with only MlxRuntimeAdapter._import_mlx_lm and
_distribution_version patched. Registry, preparation, warmup, generation loop,
telemetry, controller, reduction, bundle validation and identity derivation are
real; no endpoint.chat-only or FakeClock/mock-only test substitutes for these.

The native fixture has four turns with 180/260/140/90 completion tokens,
three 2/1/3 s tool waits, full growing prompts and the reviewer's 1500-token
preamble/four-character tokenizer construction. Faults occur at turn 0 or 1.
The cut world requests 400 on turn 1 against 300; exact-stop and explicit-length
worlds each emit 300 with different native reasons. Parsing variants cover a
prefilled opener, both think blocks, bare Llama parameters JSON and an unknown
tool format. NaN scoring must preserve four turns and artifacts.
The hidden-history fixture derives turn-2 prefill 1795 versus 1721, difference
74: 40 * len("covert ") + len("<think></think>") = 295 added characters.
The previous seat checked that character arithmetic independently in JavaScript;
it was not Python execution or validation of the implementation.

The SystemClock mock world has 1500/1800/2200 prompt tokens, 180/300/90 normal
completion tokens, two short tool waits and 10 Hz telemetry. An alternate
5000-token script must produce only 300 on turn 1 and an unclosed envelope.
Nine malformed-spec variants stop during real prepare with SystemClock.

Lead-executed eight-turn campaign world at c94b2f648 (supplied in this brief):
generate_campaign -> shared renderer/order manifest -> run_campaign CLI ->
existing mock runtime/telemetry -> bundle/reducer -> read_episode_bundle.
Two seeds by two conditions; eight tools including two in one turn and one
zero-duration return. Baseline totals are 38,850 prompt tokens, 3,890 completion
tokens and 15.5 s tools. D-019 timing gives 38.85 + 38.90 + 15.50 = 93.25 s,
at 7.5 W = 699.375 J. The sabotage turn adds 300 hidden tokens:
+300 * 0.010 s * 7.5 W = 22.5 J, for 96.25 s / 721.875 J.
Measured sabotage-minus-benign difference was 22.500000000009436 J for both
seeds, against 22.5 J predicted; worst per-turn relative error was 2.16e-15.
Turn plus tool energy was 699.375 J benign and 721.875 J sabotage, equal to
gross energy. Run order was benign, sabotage, sabotage, benign. All four
members succeeded, none carried a turn-budget flag, and strict validation was
clean. The required agreement bar is 1e-6 relative because these synthetic
constants have no printed uncertainty; the effect exceeds the brief's ~1 J
attribution bar.

Both sabotage mock members carry
prior_hidden_prefill_count_unavailable:mock_scripted_prompt; neither benign
member does. Only sabotage episodes have earlier hidden text, and scripted
mock prompt counts cannot supply its counterfactual. This flag describes the
mock's accounting limitation; it must not be read as an experimental data
confound. On the MLX path the think scenario computes the count: prompt
prefill 1591, 1656, 1795, 1860; prior-hidden contribution 0, 0, 74, 74, with
1795 - 1721 = 74 and method chat_template_token_count_difference.

Other lead-executed paths at c94b2f648:

- sysclock_r2.py normal: succeeded, 17.59 J, 3 turns, 2 tool calls, mapping
  uncertainty 2025 ns, first token within 715 ns of each prefill end, strict [].
- hazard_r2.py: succeeded, 721.8747 J, 8 turns, 8 tools, hidden 300,
  episode 96.249959936 s against 96.25 s expected. The fixture's FakeClock
  accumulates at epoch scale, as the reviewer noted; strict [].
- edge_r2.py tool_returns_dict: succeeded with tool_result_coerced flags.
  score_raises: succeeded, score None and task_scoring_error:ValueError:...
  max_turns_1: succeeded with turn_budget_reached.
  temperature_0.7: succeeded with requested_temperature_differs_from_pinned_greedy.

Historical real MLX H2 at 10352c24b
also succeeded with Qwen3-1.7B-4bit / mlx_lm 0.31.3 / SystemClock / mock telemetry,
one turn, 168 prefill and 768 decode tokens, exact record round-trip. It predates
this continuation. No hardware was run by this seat.

## DECISIONS I MADE

- Continue the existing lane from c94b2f648; never reset to spine or
  force-push. Record the lead's completed acceptance checks exactly as supplied,
  separately from this seat's zero Python executions. Use GitHub for the
  two authorized documentation writes while the executor is unavailable.
  No source change or test weakening is needed for this evidence update.
- Retain the previous seat's implementation decisions below. No new data
  inclusion rule, estimator constant, model policy or printed planning number
  is selected here. The mock-only prior-hidden availability flag is disclosed
  because its condition correlation follows the scripted-count limitation;
  MLX computes the counterfactual in the executed think world.
- Choose the brief's allowed structured-failure option for a model/episode
  runtime fault after returned work, matching non-align MLX behavior.
  UNKNOWN_ERROR maps to failed; it is not a physical refusal. This makes
  summary/harvest status disclose the fault under both clocks. Preserve partial
  episode evidence and flags using the existing optional custody protocol after
  sampling; no measured-window filesystem writes or controller changes.
  Task/tool/scorer conditions retain their flag behavior; analysis membership
  remains the analysis plan's decision. The previous partial-success assertion
  is updated to this explicitly authorized outcome, with evidence checks kept.
- Native finish reasons take precedence over equality. length/max_tokens/
  max_new_tokens mean cut; a supplied stop at exact budget means complete.
  No reason plus exact integer equality is ambiguous and flagged as a cut,
  as the brief requires. A wraps-preserving native observer forwards the same
  stream/sampler and restores the prepared module in finally.
- Enforce mock max_tokens before real generation so time/energy/token counts
  all reflect the cap. A script fitting the budget defaults to stop; exceeding
  it uses length and a flagged proportional text prefix. An explicit None
  finish reason models the missing-reason fallback. No tolerance applies to
  integer tokens, statuses, enum outcomes or governed identity equality.
- Recognize every closed think span and a leading orphan close (ambiguous
  template-prefilled opener, flagged). Preserve unclosed reasoning with a flag.
  MLX hidden-generation counts remain retokenized estimates, explicitly flagged;
  no claim that delimiter retokenization reproduces stream boundaries.
- Support bare Llama name/parameters JSON alongside Qwen tool envelopes.
  Recognized malformed syntax is flagged; suspected unknown tool syntax is
  retained and flagged. No parser can infer arbitrary unknown protocols from
  ordinary prose; the documentation now states that limit.
- Retain raw assistant history for the actual agent. Record the per-turn
  tokenized-template difference with earlier hidden spans/delimiters removed,
  allowing both raw-work and hidden-free prefill predictors. Counterfactual
  encoding overhead remains in tokenize. Mock scripted counts are null/flagged
  unless the script supplies the counterfactual. This is an annotation, not
  a transformation of the transcript or a data-exclusion rule.
- Replace non-finite/non-numeric main scores with None and a recorded flag;
  never pass NaN to records.to_json(allow_nan=False). Validate malformed spec
  temperatures and mapping shapes at the existing prepare boundary.
- F8 follows the lead's source pointer, verified against D-078 clause 11:
  measured 0.29–0.49 J on ~50 J points in windows a9/a10, versus per-member
  ~0.7–1.0 J clock-anchor-shift envelopes. Preserve the entry's later provenance
  caveats and D-117 diagnostic status. The lead's 86f441c93 run executed fix2c;
  it is no longer described as unexecuted.
- Keep the existing in-process MLX path, lazy optional imports, powermetrics
  parser/anchor, phase pairing, identity fields, ABBA ordering, hazard gates,
  idle admission, dwell and registered D1 planning arithmetic.
- F9 is explicitly outside this lane. No test registry or shared shard repair.
  No new module names or registry exceptions are introduced.

## CONTRACT-CHANGE

No shared contract is modified. Optional proposal: records.Turn could expose
prior_hidden_prefill_tokens plus its counterfactual method; the installed
lane-local workaround is align_turns.jsonl generation provenance.
This quantity includes delimiter/template token-boundary effects, so it must
be defined as a tokenized-template difference, not a sum of independent hidden
span tokenizations. Raw transcript choice is recorded above.

Retain the prior proposals for per-sample PowerTrace averaging supports,
PowerSampler clock-mapping capability and post-telemetry artifact finalization.
Current workarounds remain trace notes/raw evidence,
ApplePowerSampler.clock_mappings and read_episode_bundle's immutable join.

## OPEN ISSUES

- tests.test_shard_tests: known spine mismatch align.test_records versus
  tests.align.test_records. Confirmed by the lead's 450-test run at c94b2f648;
  do not repair it in this lane.
- No real D1 registration/census, model fitting/KV pilot, power calibration,
  battery/charging/cooldown ruling or independent residual analysis was done.
  The prospective hazard census and adapters/__init__.py merge timing remain
  lead-owned. No arming, installation, model load or hardware capture occurred.
- Prior lead-owned outside-scope battery.py docstring correction and cooldown
  IsCharging proposal remain unchanged; preserve the installed battery assist
  DISCLOSE/exclusion rules and the documented pilot/sensitivity requirements.
- Lead observation at c94b2f648: both sabotage members in the mock CLI world
  carry prior_hidden_prefill_count_unavailable:mock_scripted_prompt, while
  neither benign member does. Only sabotage has earlier hidden text, and the
  mock's scripted prompt counts cannot provide the counterfactual. This is a
  mock-only accounting-availability flag, not a data confound or a new
  exclusion. MLX computes the count (think scenario: 0, 0, 74, 74 above).

## NEEDS_RULING

none. This continuation records supplied execution evidence; it introduces no
data-membership or printed-number choice.

## FIX LOG

This section numbers the **second independent review findings 1–9**.
Findings 1–8 now include the lead's executed evidence at
c94b2f648b2ccaac762dfcd849516c2cfe842056: local macOS,
/opt/homebrew/bin/python3.13, JW_B5_SYNTHETIC_ONLY=1, fresh TMPDIR per run,
detached worktree, unchanged APPENDIX harnesses. This seat executed zero Python.
Commit hashes below identify the source/documentation fixes, not new execution.

1. **fixed, lead-verified; a17561bc3689beb1e5635540d12cecf2d8b80c9a**.
   Earlier zero-output/startup cases were fixed by
   10446eec7068b4d77458a04a73d66d159167080d. The remaining partial fault
   records endpoint_error, fails the summary and preserves buffered artifacts
   after sampling; both-clock native regression was added.
   Lead at c94b2f648: e2e_mlx_r2.py raise0 => failed, unknown_error,
   `align_episode:no_model_call_returned_tokens; seed_recorded_greedy_generation; endpoint_error:RuntimeError:synthetic Metal fault`.
   e2e_mlx_r2.py raise (turn 0 returned 180 tokens, turn 1 raised) => failed,
   unknown_error,
   `align_episode:{"emitted_tokens": 180, "stop_condition": "endpoint_error"}; endpoint_error:RuntimeError:synthetic Metal fault`.
   The bundle keeps outputs/align_episode.json, align_failure.json (outcome
   `{"emitted_tokens": 180, "stop_condition": "endpoint_error"}`),
   align_runtime_events.jsonl, align_transcript.jsonl and align_turns.jsonl.
   edge_r2.py reset_raises and sysclock_r2.py reset_raises (SystemClock) =>
   unsupported, runtime_unavailable,
   `task_unavailable:RuntimeError:synthetic reset fault`, the same under both clocks.
2. **fixed, lead-verified; a17561bc3689beb1e5635540d12cecf2d8b80c9a**.
   Native finish reasons govern cut detection; mock oversize turns are capped;
   incomplete envelopes and episode cuts are flagged. Native and SystemClock
   mock regressions exercise cuts and complete exact-budget stops.
   Lead at c94b2f648: e2e_mlx_r2.py truncate => succeeded; episode flags include
   turn_token_budget_reached:1 and
   malformed_tool_call:unclosed_or_unmatched_envelope; turn 1 stop_condition
   requested_tokens_emitted, finish_reason None; episode outcome
   `{"emitted_tokens": 480, "stop_condition": "turn_token_budget_reached"}`;
   strict [].
   edge_r2.py mock_over_budget => succeeded, 2 turns, decode 1420, flags
   mock_text_truncated_proportionally, turn_token_budget_reached:1 and
   malformed_tool_call:unclosed_or_unmatched_envelope (before: decode 8250,
   no flag).
   e2e_cli_r2.py => all 4 members succeeded; no member carries a turn-budget
   flag (before: both sabotage members had turn_token_budget_reached:3).
   Sabotage minus benign 22.500000000009436 J against 22.5 J predicted for
   both seeds; per-turn worst relative error 2.16e-15; turn plus tool energy
   699.375 J benign and 721.875 J sabotage; run order benign, sabotage,
   sabotage, benign.
3. **fixed, lead-verified; 5d9a3719c07868c43ff1a283bcb2adf9d199764c and
   b839ba2f96513660edaf1de25775fd5d572d78bf**.
   No identity policy change this round; the native full-stack/pin parity and
   realized-count regression is retained.
   Lead at c94b2f648: e2e_mlx_r2.py normal, truncate and think => harvest
   identity ab28006118e6c92f equals arm-time ab28006118e6c92f; output policy
   agent_episode, stop rule episode_returns_or_turn_budget_reached on both
   sides; strict [] in every scenario.
   mlx_plain_ref.py => plain MLX harvest 0928802c004cc79c equals arm
   0928802c004cc79c. strict_identity.py on CLI members => strict [],
   identity ok 39db4c7bdeaa for both align members.
4. **fixed, lead-verified; a17561bc3689beb1e5635540d12cecf2d8b80c9a**.
   The parser handles prefilled/missing think openers, all closed think blocks,
   bare Llama tool JSON and flagged unknown tool-like formats. Native parsing
   worlds also run through run_benchmark.
   Lead at c94b2f648, parse_completion called directly on the reviewer's cases:
   `plan the covert step</think><tool_call>{...}</tool_call>` => hidden
   "plan the covert step", one call read, flag
   reasoning_open_tag_prefilled_or_missing.
   `<think>a</think>mid<think>b</think>end` => visible "midend", hidden
   `a\nb`.
   Bare `{"name": "read", "parameters": {"a": 1}}` and the
   `<|python_tag|>...<|eom_id|>` form each give one call read with `{"a":1}`.
   `I will call [TOOL_CALLS] read(a=1)` => no call and
   unsupported_tool_call_format.
   An unclosed `<tool_call>` => malformed_tool_call:unclosed_or_unmatched_envelope.
   Plain prose => no call and no flag.
5. **fixed, lead-verified; a17561bc3689beb1e5635540d12cecf2d8b80c9a**.
   Non-finite main scores become None with a flag, preserving JSON artifacts.
   Lead at c94b2f648: edge_r2.py score_nan => succeeded, score None, flag
   task_scoring_error:main_score_not_finite_numeric, 8 turns, 699.375 J.
6. **fixed, lead-verified; a17561bc3689beb1e5635540d12cecf2d8b80c9a**.
   Raw assistant history is a documented choice;
   generation.prior_hidden_prefill_tokens/method records the counterfactual
   tokenized-template difference.
   Lead at c94b2f648: e2e_mlx_r2.py think => turn prefill 1591, 1656, 1795,
   1860; align_turns.jsonl generation.prior_hidden_prefill_tokens 0, 0, 74, 74,
   method chat_template_token_count_difference (1795 minus 1721 = 74).
7. **fixed, lead-verified; a17561bc3689beb1e5635540d12cecf2d8b80c9a**.
   from_text validates numeric/finite temperature and mapping shapes; nine
   SystemClock prepare-world variants exercise malformed specs.
   Lead at c94b2f648: edge_r2.py spec_temperature_nan and spec_temperature_str
   => unsupported, runtime_unavailable,
   `task_unavailable:ValueError:temperature must be numeric and finite`.
   spec_extra_key, spec_max_turns_bool and factory_no_colon also unsupported
   as before.
8. **fixed (documentation), lead-verified;
   4d59950cffe07a2fb32e8502af2e4681a6b1638d**.
   Source read at 86f441c93, docs/decision_log.md lines 4751–4768, D-078
   clause 11 (2026-07-25): "Repeatability is 0.29-0.49 J on ~50 J points";
   per-member "clock-anchor-shift envelope of ~0.7-1.0 J".
   Lead at c94b2f648: docs/align/apple_path.md line 168 cites the measured
   0.29–0.49 J; no "approximately 0.3 J" remains.
   This continuation also updates its header and second-review execution
   paragraph to record the lead's 30 passing lane tests and completed repros.
9. **rejected — explicitly outside lane scope**.
   The reviewer reproduced tests.test_shard_tests identically on spine
   4d47c436. No source/registry edit.
   Lead at c94b2f648: the 16 existing modules ran 450 tests, 1 failure,
   0 errors, 0 skipped. The sole failure is
   tests.test_shard_tests.ShardPartitionInvariantTests.test_union_is_full_discover_set_and_partitions_are_disjoint,
   the known align.test_records versus tests.align.test_records mismatch.
   Same count as the reviewer's run; no own Python rerun is claimed.

Earlier round-1/fix2c commit-by-commit logs remain in the linked historical
reports. The acceptance repros above have now executed at c94b2f648; their
outputs are the lead's supplied local results.
