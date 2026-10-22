# align-apple — second independent review continuation

## SUMMARY

Continues lane/2026-10-21-align-apple from 86f441c938a803e8f98d08326fb84685ddaa2ecf; all pushes preserve parent history.
Source fixes cover the remaining runtime-fault outcome, native finish reasons, mock token caps and malformed envelopes.
Partial runtime failures now use UNKNOWN_ERROR and preserve buffered episode evidence through the controller's existing custody hook.
Parsing handles template-prefilled and multiple think spans, bare Llama tool JSON and flagged unsupported tool-like formats.
Non-finite main scores become None with a flag; malformed temperatures and mapping shapes stop during prepare.
Per-turn provenance records earlier hidden reasoning's contribution to full-prompt prefill, retaining the raw conversation.
The instrument paragraph cites measured 0.29–0.49 J repeatability on about 50 J points; fix2c verification is attributed to the lead at 86f441c93.
Seven new production-path regression tests are committed, but this executor never became usable: zero Python tests or reviewer repros executed here.
Findings 1–7 remain subject to executing verification; the known spine shard failure is untouched.

## FILES

Changed against 86f441c93:

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

Read the report first, then PIPELINE.md, records.py and interfaces.py.
Inspected root AGENTS.md, the generated stop/queue pointers, Mission M0 and
orchestration. No active stop card/global gate applied; the direct brief selects
this bounded AGENT work. Nested AGENTS.md paths under joulewise, align/apple,
tests/align, docs/align and .codex-report return 404 at this head.
Read the workload/generator/adapter registration surfaces and the existing
powermetrics/fiducial/kernel-clock/transition machinery. Their implementations
and anchor remain unchanged. The historical report is retained in Git at
[86f441c93](https://github.com/mpmdw/JouleWise/blob/86f441c938a803e8f98d08326fb84685ddaa2ecf/.codex-report/align-apple.md).

## PUBLIC API

Under joulewise.align.apple (unchanged signatures except the added custody hook):

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

**Own executed count: 0. There are no own pass/fail/skip counts or repro outputs.**
No Python process could start, before or after the source changes. No dependency
was installed, so no extra-dependency run occurred. The source-only check is not
a test result and does not satisfy the reviewer's acceptance gates.

The managed environment repeatedly reported observations_current=true,
pending/starting, connectivity=offline, capabilities=[], failure=null.
Two startup waits, status retries and retained-diagnostic metadata inspection
found no usable executor or retained diagnostic capture. Every exec command
failed before process creation with:

    No usable execution environment is available. Wait for an environment to become available before using this tool.

This prevented local fetch/checkout/status, reading /etc/codex/network-policy.json,
materializing the unchanged APPENDIX scripts in .review3/, creating fresh
TMPDIRs/outdirs and running any harness. GitHub inspection confirmed the initial
head exactly matched 86f441c93. Commits use that head's tree, one parent, force=false
and an expected-head lease, on the apple branch only. No local user files were
read or overwritten. The networking policy was not inferred from unready state.

Exact submitted baseline/setup commands (none launched):

    git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-apple
    JW_B5_SYNTHETIC_ONLY=1 python3 -B /workspace/JouleWise/.review3/e2e_mlx_r2.py /workspace/JouleWise /tmp/apple-review-baseline raise

Exact submitted test commands, before and after the changes as applicable,
workdir /workspace/JouleWise (none launched; even mktemp did not execute):

    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 -m unittest discover -s tests/align -t .
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 -m unittest tests.align.test_apple_campaign tests.align.test_apple_endpoint

The reviewer module group was submitted as separate processes/TMPDIRs:

```sh
for apple_module in tests.hazards.test_refusal_allowlist tests.test_shard_tests tests.test_mlx_runtime tests.test_adapters_powermetrics tests.test_mock_adapters tests.test_shard_split tests.test_fixture_orphan_census tests.test_custody_mode_inventory tests.test_revision_five_b_readers tests.test_single_count_discipline_census tests.test_digest_pin_census tests.test_identity_pins tests.test_repin tests.test_window_lineage tests.hazards.test_battery tests.test_controller_hazard_flags
do
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 -m unittest "$apple_module"
done
```

All reviewer harness commands were also submitted, but the shell never started.
The .review3 scripts remain unmaterialized; running them requires writing the
APPENDIX verbatim first. Use a fresh TMPDIR/outdir for each invocation, with
JW_B5_SYNTHETIC_ONLY=1 and cwd /workspace/JouleWise:

    python3 -B .review3/e2e_cli_r2.py /workspace/JouleWise <fresh outdir>
    python3 -B .review3/e2e_mlx_r2.py /workspace/JouleWise <fresh outdir> normal
    python3 -B .review3/e2e_mlx_r2.py /workspace/JouleWise <fresh outdir> truncate
    python3 -B .review3/e2e_mlx_r2.py /workspace/JouleWise <fresh outdir> raise
    python3 -B .review3/e2e_mlx_r2.py /workspace/JouleWise <fresh outdir> raise0
    python3 -B .review3/e2e_mlx_r2.py /workspace/JouleWise <fresh outdir> think
    python3 -B .review3/mlx_plain_ref.py /workspace/JouleWise <fresh outdir>
    python3 -B .review3/edge_r2.py /workspace/JouleWise <fresh outdir>
    python3 -B .review3/sysclock_r2.py /workspace/JouleWise <fresh outdir>
    python3 -B .review3/hazard_r2.py /workspace/JouleWise
    python3 -B .review3/strict_identity.py /workspace/JouleWise <e2e_cli outdir> <fresh ref outdir>

Historical execution supplied by the lead/reviewer, not this seat:

| Source | Command/check | Result |
|---|---|---|
| Lead, 86f441c93 | python3 -m unittest discover -s tests/align -t . | 23 tests, all OK, 47.6 s; fix2c strict campaign correction executed |
| Lead, 86f441c93 | e2e_mlx_r2.py normal/truncate/think | strict []; harvest and arm identity ab28006118e6c92f; agent_episode / episode_returns_or_turn_budget_reached on both sides |
| Lead, 86f441c93 | e2e_mlx_r2.py raise0 | failed/unknown_error; no_model_call_returned_tokens |
| Lead, 86f441c93 | edge_r2.py and sysclock_r2.py reset_raises | unsupported/runtime_unavailable; task_unavailable:RuntimeError |
| Lead, 86f441c93 | sysclock_r2.py normal | succeeded, 17.14 J; mapping uncertainty 2263 ns; first token within 477 ns of prefill end; strict clean |
| Reviewer, b7739911b | 16 existing modules listed above | 450 ran, one pre-existing spine shard failure |
| Reviewer, b7739911b | tests/align | 19 ran, all passed |

Skip counts/reasons were not separately supplied for those historical runs;
none are invented. Seven added methods imply 30 discovered tests if discovery
remains unchanged; **30 is a source count, not an executed result**.
No existing test is skipped, deleted or weakened to suppress a defect:
the partial-fault test retains counts/flags and raw measured energy and adds
the newly authorized failure outcome/artifact assertions. The ambiguous
at-budget fixture now explicitly lacks a finish reason, preserving its cut
assertion while new complete-at-budget cases exercise the opposite result.

## END-TO-END

Own execution is blocked. New tests use real run_benchmark and either
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
The independent character arithmetic was checked in JavaScript here; it is not
Python execution or validation of the implementation.

The SystemClock mock world has 1500/1800/2200 prompt tokens, 180/300/90 normal
completion tokens, two short tool waits and 10 Hz telemetry. An alternate
5000-token script must produce only 300 on turn 1 and an unclosed envelope.
Nine malformed-spec variants stop during real prepare with SystemClock.

Lead/reviewer-measured eight-turn campaign world (supplied in this brief):
generate_campaign -> shared renderer/order manifest -> run_campaign CLI ->
existing mock runtime/telemetry -> bundle/reducer -> read_episode_bundle.
Two seeds by two conditions; eight tools including two in one turn and one
zero-duration return. Baseline totals are 38,850 prompt tokens, 3,890 completion
tokens and 15.5 s tools. D-019 timing gives 38.85 + 38.90 + 15.50 = 93.25 s,
at 7.5 W = 699.375 J. The sabotage turn adds 300 hidden tokens:
+300 * 0.010 s * 7.5 W = 22.5 J, for 96.25 s / 721.875 J.
Measured difference was 22.500000000009 J, worst per-turn relative error
2.2e-15; turn plus tool energy equaled gross, ABBA order and strict validation
were clean. The required agreement bar is 1e-6 relative because these synthetic
constants have no printed uncertainty; the effect exceeds the brief's ~1 J
attribution bar. At 86f441c93 the sabotage-only equality-based cut flag remained;
the new finish-reason logic is intended to remove it, but has no executed repro.

The lead's HAZARD fixture succeeded with 96.24996 s; the reported 40 microsecond
gap is epoch-scale FakeClock accumulation. Historical real MLX H2 at 10352c24b
also succeeded with Qwen3-1.7B-4bit / mlx_lm 0.31.3 / SystemClock / mock telemetry,
one turn, 168 prefill and 768 decode tokens, exact record round-trip. It predates
this continuation. No hardware was run by this seat.

## DECISIONS I MADE

- Continue the existing lane; never reset to spine or force-push. With the
  executor unusable, perform the independently doable source work via GitHub
  and explicitly leave all executable acceptance gates open. Historical
  evidence is attributed; current repro outputs are not fabricated.
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

- Executing verification is blocked by the managed environment. Materialize
  APPENDIX .review3 scripts verbatim and run every listed repro, lane discovery
  and each reviewer module with its own TMPDIR at the pushed head. No current
  finding is claimed to have passed a repro here. F1–F7 source changes and
  failure-artifact salvage especially require execution before acceptance.
- tests.test_shard_tests: known spine mismatch align.test_records versus
  tests.align.test_records. Report it on rerun; do not repair it in this lane.
- No real D1 registration/census, model fitting/KV pilot, power calibration,
  battery/charging/cooldown ruling or independent residual analysis was done.
  The prospective hazard census and adapters/__init__.py merge timing remain
  lead-owned. No arming, installation, model load or hardware capture occurred.
- Prior lead-owned outside-scope battery.py docstring correction and cooldown
  IsCharging proposal remain unchanged; preserve the installed battery assist
  DISCLOSE/exclusion rules and the documented pilot/sensitivity requirements.

## NEEDS_RULING

none. The runtime-failure option and other changes are authorized by this brief.
Unavailable execution is an infrastructure blocker, not a data-membership ruling.

## FIX LOG

This section numbers the **second independent review findings 1–9**.
"Fixed (source)" means implemented and pushed, not an executed pass.
There is no own post-fix repro output because no Python process could start.

1. **fixed (source), a17561bc3689beb1e5635540d12cecf2d8b80c9a**. Earlier zero-output/startup cases were fixed by
   10446eec7068b4d77458a04a73d66d159167080d. Lead at 86f441c93:
   raise0 => failed/unknown_error/no_model_call_returned_tokens;
   reset_raises on both harness clocks => unsupported/runtime_unavailable.
   Remaining partial fault now records endpoint_error, fails the summary and
   preserves partial artifacts after sampling. Native both-clock regression
   added. Own raise/raise0 repro: BLOCKED before process creation with the
   executor error quoted in TESTS RUN; no post-fix output.
2. **fixed (source), a17561bc3689beb1e5635540d12cecf2d8b80c9a**. Native finish reasons govern cut detection;
   mock oversize turns are actually capped; incomplete envelopes are flagged;
   complete exact-budget stop is not cut; episode outcomes disclose cuts.
   Native and SystemClock/mock regressions cover both directions. Own truncate,
   mock_over_budget and e2e_cli repros: BLOCKED, no post-fix output.
3. **fixed (by 5d9a3719c07868c43ff1a283bcb2adf9d199764c and
   b839ba2f96513660edaf1de25775fd5d572d78bf)**. Lead output at 86f441c93:
   harvest identity ab28006118e6c92f = arm identity ab28006118e6c92f;
   agent_episode / episode_returns_or_turn_budget_reached on both sides;
   normal/truncate/think strict []. No identity policy change this round;
   new native full-stack/pin parity and realized-count regression retained.
   Own identity/strict repros at pushed head: BLOCKED, no output.
4. **fixed (source), a17561bc3689beb1e5635540d12cecf2d8b80c9a**. Prefilled/missing think opener is counted and
   flagged; all closed blocks stripped; bare Llama tool JSON parsed; unknown
   tool-like formats flagged. Four native parsing worlds through run_benchmark.
   Own parsing repro execution: BLOCKED, no post-fix output.
5. **fixed (source), a17561bc3689beb1e5635540d12cecf2d8b80c9a**. Non-finite main score becomes None plus
   task_scoring_error:main_score_not_finite_numeric, allowing serialization.
   Native NaN scorer regression requires succeeded plus written artifacts.
   Own edge score_nan: BLOCKED, no post-fix output.
6. **fixed (source), a17561bc3689beb1e5635540d12cecf2d8b80c9a**. Raw assistant history is a documented choice;
   generation.prior_hidden_prefill_tokens/method records each turn's
   counterfactual template difference. Native regression requires 1795-1721=74
   on turn 2, and governed identity equality. Own think harness: BLOCKED;
   the 74-token result is the lead's prior observation, not a current repro.
7. **fixed (source), a17561bc3689beb1e5635540d12cecf2d8b80c9a**. from_text rejects non-numeric/non-finite
   temperature and non-mapping task_kwargs/mock entries. Nine SystemClock
   prepare-world variants require unsupported/runtime_unavailable.
   Own malformed-spec edge repro: BLOCKED, no post-fix output.
8. **fixed (documentation), 4d59950cffe07a2fb32e8502af2e4681a6b1638d**. Source read at 86f441c93,
   docs/decision_log.md lines 4751–4768, D-078 clause 11 (2026-07-25):
   "Repeatability is 0.29-0.49 J on ~50 J points"; per-member
   "clock-anchor-shift envelope of ~0.7-1.0 J". apple_path.md now cites that
   measured context and attributes 23 passing lane tests / strict [] to the
   lead at 86f441c93. Source inspection finds neither stale NOT EXECUTED text
   for fix2c nor "approximately 0.3 J" in that document. No runtime repro needed.
9. **rejected — explicitly outside lane scope**. The reviewer reproduced
   tests.test_shard_tests identically on spine 4d47c436. No source/registry edit.
   Own module rerun was submitted with its own TMPDIR but BLOCKED before launch;
   no claim of a fresh failing count. Historical reviewer group: 450 tests,
   one spine shard failure.

Earlier round-1/fix2c commit-by-commit logs remain in the linked historical
report at 86f441c93. They are not reclassified as current execution evidence.
