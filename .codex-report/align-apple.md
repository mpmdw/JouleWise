# align-apple lane report — fix round 2

## SUMMARY

Round 2 continues b7739911b72709b02213a9773ab04b7e81fe1f79 and fixes R2-1 through R2-6 in source.
Task reset/prompts now run in prepare; zero-token measured episodes raise AdapterFailure(UNKNOWN_ERROR), while partial episodes keep flags.
Bundles and readiness share prepared model artifact, actual/requested sampler settings and a fixed registered-budget output policy.
Episode outcomes stay recorded outside identity; both endpoint paths flag a turn that reaches its token budget.
The D1 plan now uses sourced 1.5B/7B energy inputs, defines pair/window variance, and derives conditional quiet time.
Battery guidance corrects the model-load observation, cites the overload validation and specifies pilot/sensitivity/sustained-deficit checks.
Nothing ran in Python this round: the executor remained unavailable after about ten minutes; all round-2 fixes are NOT EXECUTED.
Prior lead/reviewer evidence is attributed below; R2-7 and all lead-owned hardware, census and registration gates remain open.

## FILES

Round-2 changed paths only:

- joulewise/align/apple/workload.py: startup validation before admission; zero-output model failure; shared bundle/readiness model, sampler and fixed policy; episode_outcome.
- joulewise/align/apple/endpoint.py: turn_token_budget_reached:<index> on both mock and MLX paths.
- tests/align/test_apple_campaign.py: reset/prompt prepare faults, FakeClock/SystemClock empty-run failures, partial-run disclosure, H3 final-turn cut, governed identity across outcomes and temperatures, and readiness agreement. In the existing battery test only the comment changed; all values/assertions remain intact.
- tests/align/test_apple_endpoint.py: native-helper budget flag; actual MLX adapter prepare/generation/bundle/readiness chain with only native computation synthesized.
- docs/align/apple_path.md: corrected evidence attribution, battery evidence/pilot checks, sourced detection-power arithmetic, variance units and quiet-time scenarios.
- .codex-report/align-apple.md: this report, historical verification attribution and preserved round-1 plus round-2 FIX LOG.

The existing lane also includes apple/__init__.py, sampler.py and campaign.py;
they are unchanged this round. The sole workload registry remains
joulewise/adapters/__init__.py (lazy align_episode wrapping); the earlier
configs/gates/hazard_refusals.json two-line prospective census exemption is
unchanged. No round-2 registry exception/addition was needed.

Read workloads.py, workload_profile.py, campaign_generator_core.py, suite.py,
adapters/mlx_runtime.py, adapters/powermetrics.py and the existing anchor code.
No change to those files, the reducer/controller/identity builder or any
hazard code. The protected PIPELINE.md, records.py and interfaces.py are
unchanged. Nothing under .review2/ is committed.

## PUBLIC API

All modules below are under joulewise.align.apple; the shared records remain the crossing contract.

- sampler.seconds_ns(seconds: float) -> int
- sampler.monotonic_ns(stamp: ClockStamp) -> int
- sampler.stamp_mapping(stamps: Sequence[ClockStamp], *, episode_domain: str, evidence: Mapping[str, Any] | None = None) -> tuple[ClockMapping, tuple[str, ...]]
- sampler.power_records(samples: Sequence[PowerSample], *, nominal_interval_ns: int, evidence: Mapping[str, Any] | None = None) -> tuple[tuple[PowerTrace, ...], tuple[str, ...]]
- sampler.ApplePowerSampler(config: BenchmarkConfig, clock: Clock, *, episode_domain: str, context: RunContext | None = None, adapter: Any | None = None)
- ApplePowerSampler.start() -> None
- ApplePowerSampler.stop() -> tuple[PowerTrace, ...]
- ApplePowerSampler.clock_mappings, flags, uncertainty_evidence: recorded adapter/bridge evidence.
- sampler.HAZARD_UNJUDGED: hazard.unjudged:battery,ac,thermal,contention.
- sampler.POST_WINDOW_DWELL_S: 1.0, from quiet_mac_exploratory.json:post_window_sampling_dwell_s.
- endpoint.parse_completion(text: str, *, reasoning_tokens: int = 0) -> tuple[str, str, tuple[ToolCallRequest, ...], tuple[str, ...]]
- endpoint.MlxEndpoint(runtime: Any, config: BenchmarkConfig, clock: Clock, *, episode_domain: str, prepare_metadata: Mapping[str, Any] | None = None, mock_turns: Sequence[Mapping[str, Any]] = ())
- MlxEndpoint.chat(messages: Sequence[ChatMessage], *, tools: Sequence[Mapping[str, Any]] = (), max_tokens: int, temperature: float, seed: int | None) -> ChatResult
- workload.EpisodeSpec(task_factory: str, condition: Condition, seed: int, max_turns: int, max_tokens: int, temperature: float, task_kwargs: Mapping[str, Any] = {}, mock_turns: tuple[Mapping[str, Any], ...] = (), schema: str = SPEC_SCHEMA)
- EpisodeSpec.to_text() -> str; EpisodeSpec.from_text(text: str) -> EpisodeSpec
- workload.EpisodeRuntimeAdapter(runtime: Any, clock: Clock): runtime is None only for a structured unsupported-backend prepare failure.
- EpisodeRuntimeAdapter.prepare(config: BenchmarkConfig, context: RunContext | None = None) -> AdapterResult
- EpisodeRuntimeAdapter.identity_projection_metadata(config: BenchmarkConfig) -> dict[str, Any]
- EpisodeRuntimeAdapter.warmup(config: BenchmarkConfig, context: RunContext | None = None) -> AdapterResult
- EpisodeRuntimeAdapter.run_workload(config: BenchmarkConfig, context: RunContext | None = None) -> RuntimeResult
- EpisodeRuntimeAdapter.cleanup(config: BenchmarkConfig, context: RunContext | None = None) -> AdapterResult
- workload.read_episode_bundle(bundle: Path) -> Episode
- campaign.generate_campaign(base: BenchmarkConfig, specs: Sequence[EpisodeSpec], output_root: Path, *, model_tag: str, counterbalance: bool = True) -> tuple[Path, ...]

Round-2 signatures are unchanged. Behavioral/output changes:

- prepare validates task.reset(seed), system_prompt(condition), user_prompt()
  before runtime preparation/admission; failures retain task_unavailable:<type>:<message>
  and RUNTIME_UNAVAILABLE.
- run_workload raises AdapterFailure(UNKNOWN_ERROR, ...) if no chat result
  returned generated tokens, independently of clock domain.
- identity_projection_metadata(config) and bundle workload_provenance carry
  the same model/sampler/output_policy. model now includes name, source,
  revision and prepared artifact_identity. sampler preserves the inner MLX
  greedy controls (or mock deterministic greedy controls), plus
  requested_temperature and max_tokens.
- output_policy contains name=agent_episode, requested_tokens=max_turns*max_tokens,
  max_turns, max_tokens_per_turn and the fixed stop_condition
  episode_returns_or_turn_budget_reached.
- workload_provenance.episode_outcome and metadata.adapters.runtime.align_episode carry the actual
  emitted_tokens and stop_condition (episode_returned or turn_budget_reached);
  those outcome fields do not enter the governed identity.
- MlxEndpoint.flags and Episode.flags add turn_token_budget_reached:<turn>
  on exact integer equality with the per-turn token budget.

## TESTS RUN

**Nothing ran this round. Executed Python test count: 0.**
No own pass/fail/skip counts, Python version, syntax/import check or harness
result exists. No optional dependency was installed; there is no extra run.

The first command attempted from /workspace/JouleWise was python3 --version.
It failed before process creation:

    No usable execution environment is available. Wait for an environment to become available before using this tool.

The managed instance stayed pending/offline, capabilities [], with no reported
failure. A startup wait and retries after approximately ten minutes still
could not launch Python. The same command failure prevented local fetch/checkout,
reading /etc/codex/network-policy.json, creation of a fresh TMPDIR, and
materializing the APPENDIX scripts under .review2/. Changes were made through
GitHub from the confirmed existing apple head with non-forced, expected-head
fast-forward updates.

Exact commands submitted before fixes (cwd /workspace/JouleWise):

    python3 --version
    JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR="$(mktemp -d)" python3 -m unittest discover -s tests/align -t .
    JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR="$(mktemp -d)" python3 -m unittest tests.align.test_apple_campaign tests.align.test_apple_endpoint

The module command and discovery command were also submitted after the runtime
fixes; both failed before launch with the same unavailable-executor error.
The fresh-TMPDIR shell expression itself did not execute. The whole suite was
not requested or run. No test was weakened.

Required reruns on an executable checkout (all NOT EXECUTED this round;
JW_B5_SYNTHETIC_ONLY=1 and a fresh TMPDIR per invocation, cwd repository root):

    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 -m unittest discover -s tests/align -t .
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 -m unittest tests.align.test_apple_campaign tests.align.test_apple_endpoint
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 -P .review2/h1_offset_phase.py /workspace/JouleWise 100
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 -P .review2/h3_edges.py /workspace/JouleWise
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 -P .review2/h4_sys_zero_turn.py /workspace/JouleWise
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 -P .review2/id_probe.py /workspace/JouleWise

No APPENDIX checks were adapted or removed: the scripts could not be written
locally. On rerun H4 needs only the brief-authorized H3-style try/except around
read_episode_bundle, because prepare refusals and raised measured failures
write no episode artifact. H2 was deliberately not attempted: it requires
Apple Silicon, MLX packages and the lead's local model snapshot. The lead
re-runs H2 after push. The synthetic-native MLX test requires no MLX install.

Historical executed evidence, not this seat's results:

| Source | Exact command / harness | Reported result |
|---|---|---|
| Lead-measured at 9162afd6d, macOS /opt/homebrew/bin/python3.13 | python3 -m unittest discover -s tests/align -t . | 19, OK |
| Lead-measured at 9162afd6d | python3 -m unittest tests.hazards.test_refusal_allowlist tests.test_shard_tests | 27, one known spine shard failure; allowlist passes |
| Lead-measured at 9162afd6d | 12-module command below | 300, OK |
| Reviewer-measured at b7739911b, same Python/flags/fresh TMPDIR convention | python3 -m unittest discover -s tests/align -t . | 19, all passed |
| Reviewer-measured at b7739911b | 16 existing modules (the 12 below plus test_refusal_allowlist, test_shard_tests, hazards.test_battery, test_controller_hazard_flags) | 450, one known spine shard failure |
| Reviewer-measured at b7739911b | H1 at 100 Hz | Both succeeded; FAILURES 0; worst turn error 0.02 J |
| Reviewer-measured at b7739911b | H2, real Qwen3-1.7B-4bit MLX / mock telemetry | Succeeded; 2 turns, 5 parsed/run tool calls; identity absent before R2-2 |
| Lead-measured at b7739911b | H3, H4 and id_probe | Before values in brief: reset/turn-0 defects, missing sampler/artifact identity, missing final-turn budget flag |

Historical targeted command (lead-measured at 9162afd6d):

    python3 -m unittest tests.test_mlx_runtime tests.test_adapters_powermetrics tests.test_mock_adapters tests.test_shard_split tests.test_fixture_orphan_census tests.test_custody_mode_inventory tests.test_revision_five_b_readers tests.test_single_count_discipline_census tests.test_digest_pin_census tests.test_identity_pins tests.test_repin tests.test_window_lineage

The supplied evidence does not separately report skip counts/reasons; none
are inferred. The reviewer/lead observations do not verify this round's edits.
Read-only GitHub inspection, branch ancestry and file comparisons are source
checks, not executed Python. Planning arithmetic below is derived.

## END-TO-END

This round added regressions through real production paths, all NOT EXECUTED:

- AgentTask startup -> real registry/controller prepare -> unsupported,
  RUNTIME_UNAVAILABLE before idle/warmup, for reset and both prompt faults.
  A short SystemClock reset case and a both-clocks turn-0 model failure
  require the same outcomes as FakeClock; a later failed call retains a
  successful partial episode with endpoint_error.
- H3's final turn emits exactly max_tokens and requires
  turn_token_budget_reached:5; the existing MLX helper world emits its exact
  512-token budget and requires turn_token_budget_reached:0.
- Real mock runtime/telemetry -> bundle -> build_stack_identity -> readiness
  _runtime_probe_metadata/derive_model_runtime_config_from_metadata. Matching
  registered budgets with episode_returned versus turn_budget_reached must
  have equal identities; requested temperature 0.7 must differ from 0.0 and
  retain its mismatch flag. Both outcomes and actual emitted counts stay recorded.
- Real MLX registry/prepare/_generate/controller/bundle and readiness with a
  synthetic native stream, local synthetic weight bytes, 2048 prompt tokens
  and D-019 10 ms/token timing; projected model/sampler/policy must match.

Prior observed production-shaped world (lead-measured at 9162afd6d):
six turns, five ledger tools, 27,648 prompt tokens, 4,608 base output tokens
and 8.3 s tool waits. At D-019's 1 ms/prompt token, 10 ms/output token and
7.5 W, derived baseline duration is
27.648 + 46.080 + 8.300 = 82.028 s, energy 615.21 J.
Adding 256 hidden output tokens gives derived +2.56 s / +19.2 J.
The lead ran generate_campaign -> shared renderer/write boundary ->
members/order_manifest -> campaign CLI/controller -> existing mock runtime
and telemetry -> immutable bundle/reduction -> read_episode_bundle.
In-process, CLI and policy harnesses succeeded with these values:

| Quantity | Derived baseline / hidden | Lead-measured at 9162afd6d baseline / hidden |
|---|---:|---:|
| Duration | 82.028 / 84.588 s | 82.028 / 84.588 s |
| Gross energy | 615.21 / 634.41 J | 615.2100000000811 / 634.4100000000919 J |
| Prefill energy | 207.36 / 207.36 J | 207.36 / 207.36 J |
| Decode energy | 345.60 / 364.80 J | 345.60 / 364.80 J |
| Tool energy | 62.25 / 62.25 J | 62.25 / 62.25 J |

The lead's observed dE was 19.200000000010846 J; this agrees with the
derived 19.2 J within the brief's 1e-6 relative deterministic bar.
The real synthetic HAZARD fixture was 84.587953664 s, six turns and 256
hidden tokens. Its 46.336 microsecond deficit against derived 84.588 s
comes from epoch-scale FakeClock float sleeps; at 7.5 W that is about
0.35 mJ, below the approximately 1 J attribution limit. The lead's passing
battery test covered the whole episode request: clean control, -865 mA
late-tool assist disclosure and +865 mA charging exclusion. The model-load
origin of the real -865 mA observation is now correctly stated.

Reviewer-measured at b7739911b, H1 used an offset monotonic clock with a
6 microsecond read bracket and 100 Hz phase-dependent telemetry:
40 W prefill, 25 W decode, 6 W tool waits, 7.5 W otherwise.
Every turn and tool integration passed its derived sample-edge bar;
worst-turn error was 0.02 J. The hidden-token effect was
63.999944957700336 J against derived 256 * 0.010 * 25 = 64.0 J;
FAILURES 0. Its first-token/prefill checks passed.
Reviewer-measured at b7739911b, the SystemClock record round-tripped
exactly with uncertainty 2740 ns. Lead-measured at 9162afd6d, its earlier
SystemClock harness had uncertainty 2263 ns and exact record round-trip.

Derived D1 arithmetic only: at h=128, B=2 J and the stated
sigma_window=5 J scenario, rounded historical e=0.0998 gives
delta=12.7744 J and ceil((2.801585218*5/10.7744)^2)=2 windows/model;
e=0.37575 gives delta=48.096 J and
ceil((2.801585218*5/46.096)^2)=1.
For two models at six hours/window, science time is 24 h / 12 h;
adding one six-hour pilot per model gives 36 h / 24 h.
These are known-sigma calculations, not a recommendation that one pilot
estimates window variance. The plan explicitly requires pilot-estimated
variance and t quantiles; independent analysis and registration remain open.

## DECISIONS I MADE

- Continue the existing apple head b7739911b, preserve round-1 fixes and push
  each meaningful step with a non-forced expected-head update. The executor
  never started; use the brief's unexecuted-fix fallback, with no claimed Python results.
- R2-1 follows the lead's installed disposition: validate reset and both
  prompts in prepare. Tasks must tolerate repeated reset(seed); prepare's
  validation reset is outside measured energy, warmup resets, and the measured
  episode resets again.
- Use FailureReason.UNKNOWN_ERROR for a prepared measured run in which no
  model call returns generated tokens. The controller maps it to failed;
  RUNTIME_UNAVAILABLE would map to unsupported, which is appropriate for
  prepare/configuration failures instead. Include endpoint/episode flags in
  the AdapterFailure message. A returned positive completion count followed
  by any later task/model fault stays a recorded partial episode.
- Generated token counts are integers: positive means returned work, and
  exact equality with max_tokens means a per-turn budget cut. No float
  tolerance is applied to those integer properties.
- Govern model identity from the inner runtime's prepare metadata. Preserve
  MLX's actual greedy sampler fields, record requested_temperature separately,
  retain the mismatch flag, and include max_tokens in sampler identity.
  The mock inner runtime has no probe; the lane-local adapter supplies its
  actual deterministic tokenizer/greedy identity using the prepared version.
- The identity builder retains only output-policy name, requested_tokens and
  stop_condition. Use a fixed total requested-token budget, stable stop rule,
  and explicit max_turns/max_tokens_per_turn in bundle/probe policy.
  Sampler max_tokens preserves per-turn budget identity even when different
  budget factorizations share the same total. No outcome enters that policy.
- Keep actual stop_condition/emitted_tokens in episode_outcome and the
  existing metadata.adapters.runtime.align_episode record. No shared records contract edit.
- Keep in-process MLX: existing workloads use the same model load, tokenizer,
  pinned greedy sampler, stream_generate and events. No server or duplicate
  model is launched, and all optional imports remain lazy.
- No new workload registry is needed: adapters/__init__.py already wraps
  align_episode lazily. Production admission/dwell/hazards, the reducer and
  clock anchor remain unchanged.
- Retain round-1 disjoint indexed prefill/decode/tool events, prefill-end
  first_token_ns, clock half-ulp accounting, standalone hazard disclosure and
  dwell, pack UUID/ABBA ordering, and the warning that generic ttft_s,
  decode_latency_s and energy_token_j are not episode reporting metrics.
- R2-4 removes the unsourced coefficient, uses the explicitly labelled
  Qwen2.5-1.5B reconstruction and the nearest-size Qwen2.5-7B absolute-cell
  member mean (n=10), and preserves their D-117 diagnostic/pre-genesis status.
  All planning results are derived from printed inputs, not measurements here.
  N counts independent windows in the table; shared window variance does not
  vanish by increasing pairs. Sigma=5 J is a scenario parameter. Small z-based
  counts assume known sigma; pilot estimation and t quantiles determine practice.
- R2-5 follows the quoted 2026-10-06 ruling, which corrects -865 mA to model
  load. Only the existing battery test comment changes. Keep DISCLOSE for
  on-AC discharge and the existing charging/AC/missing-evidence exclusions.
  Carry item-5 sensitivity and item-6 reopen evidence into the pilot.
  Battery capacity/resume-charge state of charge are pilot parameters, not
  invented constants. Hazard docstring/cooldown proposals go to the lead.
- R2-6 attributes prior observations to the lead at 9162afd6d or reviewer/lead
  at b7739911b; this seat's arithmetic is labelled derived and its changed tests
  remain NOT EXECUTED. H2 is reserved for the lead's real Apple Silicon rerun.
- R2-7 makes no changes: the brief explicitly excludes the spine shard defect
  and leaves registry merge timing to the lead.

## CONTRACT-CHANGE

No installed contract change. Preserve the prior lane-local proposals:

1. Optional per-sample integer averaging supports on PowerTrace; current
   workaround is interval notes and authoritative raw/CSV evidence.
2. Optional clock-mapping capability on PowerSampler; current workaround is
   ApplePowerSampler.clock_mappings.
3. Post-telemetry artifact finalization; current workaround is the immutable
   episode/trace join in read_episode_bundle.

Round 2 needs no additional shared contract change. The mock identity fallback,
fixed policy and outcome fields are lane-local. The three protected files are
unchanged.

## OPEN ISSUES

- R2-7: tests.test_shard_tests has the spine defect: shard names tests.align.*
  versus discovery's align.*. Lead-measured at 9162afd6d and reviewer-measured
  at b7739911b, the relevant existing groups had this sole failure. Do not
  repair it in this lane.
- R2-7: merging joulewise/adapters/__init__.py makes registered packs carry
  code.changed_since_registration; merge timing is the lead's call.
- Round-2 Python verification is unavailable: materialize the unchanged
  APPENDIX H1/H3/H4/id_probe scripts and execute the commands above on a usable
  host. H4 permits only the specified absent-episode exception wrapper.
  The lead must also rerun H2 on real MLX to check the governed bundle identity.
- Lead-owned outside scope: joulewise/hazards/battery.py line 11 still calls
  the corrected model-load bursts "during inference"; fix that docstring.
- Lead-owned outside scope: decide whether campaign cooldown should also
  wait for IsCharging = No before the next member. Sustained adapter deficit
  can drain the battery across members and later charging costs excluded data;
  record per-member assist energy, state of charge and charging transitions.
- Complete the prospective align hazard census before registering a real D1
  HAZARD pack; the earlier registry exemption is not registration authority.
- D1 pilot must measure whole-machine draw per candidate, battery capacity
  and resume-charge state of charge, window/pair variance, cooldown and fit/KV
  memory. Print each cell with and without battery.assist members; monitor
  power-limit transitions, matched-second throughput/rails/frequency and
  battery temperature for ruling reopen evidence.
- Independent analysis, hardware attribution/calibration transfer, registered
  extraction membership and authenticated launch remain lead/hardware gates.
  No hardware was armed, installed, loaded or measured by this seat, and no
  claim-bearing research result or registration was created.

## NEEDS_RULING

none. All six authorized fixes follow the lead's dispositions. Existing
data-membership rules and claim numbers are unchanged. The outside-scope
battery cooldown proposal and shard/merge issues stay with the lead.

## FIX LOG

- 1 — fixed, verified by the lead's local run at 9162afd6d, 84fc4efefb73aa587497cc5d3931ded641ea87ef: remove enclosing align_turn_N phases; retain indexed inner events and turn records.
- 2 — fixed, verified by the lead's local run at 9162afd6d, 84fc4efefb73aa587497cc5d3931ded641ea87ef: disable idle_admission.enabled in the synthetic campaign test only.
- 3 — fixed, verified by the lead's local run at 9162afd6d, 84fc4efefb73aa587497cc5d3931ded641ea87ef, b9b0235e883272e04dc4bf2b8dab4724df017c22, 69a0bd56a1948c78fe52e33442b7f16de7507b27: assert success/energy on valid campaign, flag and HAZARD paths, and structured early failure on invalid paths.
- 4 — fixed, verified by the lead's local run at 9162afd6d, b9b0235e883272e04dc4bf2b8dab4724df017c22: two-line configs/gates/hazard_refusals.json entry; alignment import stays branch-local; merge timing is disclosed above.
- 5 — fixed, verified by the lead's local run at 9162afd6d, 84fc4efefb73aa587497cc5d3931ded641ea87ef, 69a0bd56a1948c78fe52e33442b7f16de7507b27: bad tasks/specs/mirrors return RUNTIME_UNAVAILABLE at prepare; no failed-spec benign episode is written.
- 6 — fixed, verified by the lead's local run at 9162afd6d, 84fc4efefb73aa587497cc5d3931ded641ea87ef, b9b0235e883272e04dc4bf2b8dab4724df017c22, 69a0bd56a1948c78fe52e33442b7f16de7507b27: support only mock/MLX execution, reject every other backend at prepare, forward the runtime probe and test real align identity derivation.
- 7 — fixed, verified by the lead's local run at 9162afd6d, 0882e9ecff2c2ce9ec106badf3e6d7f10abd3a59, 69a0bd56a1948c78fe52e33442b7f16de7507b27: ns-product half-ulp pricing, serialized-stamp resolution and no second charge of the anchor span; clock.py untouched.
- 8 — fixed (documentation), b9b0235e883272e04dc4bf2b8dab4724df017c22, 69a0bd56a1948c78fe52e33442b7f16de7507b27: sourced historical e evidence, explicit e/sigma sensitivity, and policy-key-derived per-member cooldown in capacity. The lead's local Python runs at 9162afd6d do not independently verify this planning arithmetic; the independent-analysis/pilot requirement remains open.
- 9 — fixed, verified by the lead's local run at 9162afd6d, b9b0235e883272e04dc4bf2b8dab4724df017c22: runner-compatible members/order_manifest.json and default matched AB/BA order.
- 10 — fixed, verified by the lead's local run at 9162afd6d, 0882e9ecff2c2ce9ec106badf3e6d7f10abd3a59: hazard.unjudged flag on every standalone trace and one-second post-window dwell.
- 11 — fixed, verified by the lead's local run at 9162afd6d, 84fc4efefb73aa587497cc5d3931ded641ea87ef, b9b0235e883272e04dc4bf2b8dab4724df017c22: episode/artifact flag names all three misleading summary fields; docs prohibit printing them for align.
- 12 — fixed, verified by the lead's local run at 9162afd6d, 84fc4efefb73aa587497cc5d3931ded641ea87ef: first_token_ns uses the prefill end event.
- 13 — fixed, verified by the lead's local run at 9162afd6d, b9b0235e883272e04dc4bf2b8dab4724df017c22: episode ordinal tags and persistent pack-unique UUID run ids.
- Battery assist continuation — fixed, verified by the lead's local run at 9162afd6d, b9b0235e883272e04dc4bf2b8dab4724df017c22: real-bundle whole-episode span control, late tool-wait discharge and in-turn charging tests, plus per-candidate draw parameters and the DISCLOSE disposition.
- tests.test_shard_tests — rejected: the brief explicitly identifies the discovery/shard naming mismatch as a spine defect outside WRITE_SCOPE; no source change made. The lead's local run at 9162afd6d reproduced the single known failure in the 27-test refusal/shard group; this fix1c seat could not execute a rerun.

### Round 2

- R2-1 — fixed (NOT EXECUTED), 10446eec7068b4d77458a04a73d66d159167080d: validate task startup at prepare; UNKNOWN_ERROR/failed when no model call returns generated tokens; FakeClock/SystemClock and partial-episode regressions.
- R2-2 — fixed (NOT EXECUTED), 5d9a3719c07868c43ff1a283bcb2adf9d199764c, c08068e80d6b990b813f0f113b6ed27f5ef0c13e: prepared artifact and sampler provenance, stable registered-budget policy, outcome outside identity, mock/native readiness-versus-bundle regressions.
- R2-3 — fixed (NOT EXECUTED), 10446eec7068b4d77458a04a73d66d159167080d: exact-integer turn-token-budget flag shared by mock and MLX, with H3/native-helper assertions.
- R2-4 — fixed (NOT EXECUTED), 0102dd0b47368989006efc7d85c04702d2868e6a: sourced 1.5B/7B coefficients, pair/window variance model, known-sigma/t-pilot caveat and derived quiet-time arithmetic.
- R2-5 — fixed (NOT EXECUTED), 0102dd0b47368989006efc7d85c04702d2868e6a: correct model-load wording/comment only in existing battery test, cite overload validation, add pilot/sensitivity/sustained-deficit guidance and lead-owned proposals.
- R2-6 — fixed (NOT EXECUTED), 0102dd0b47368989006efc7d85c04702d2868e6a: replace stale execution statements with attributed lead/reviewer results and this round's unexecuted status.
- R2-7 — rejected: the round-2 brief explicitly says no action outside this lane; preserve the spine shard defect and adapters/__init__.py merge-timing note in OPEN ISSUES.
