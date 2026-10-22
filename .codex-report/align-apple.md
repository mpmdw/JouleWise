# align-apple lane report — fix round 1, continuation fix1c

## SUMMARY

The lead verified the fixes locally at 9162afd6d60a2733c170fb92f7b1879e31bbbad4; this continuation records that evidence.
The lead ran 19 alignment tests and 300 targeted existing tests successfully; the 27-test refusal/shard group had only the known spine shard failure.
The lead's in-process, CLI and policy campaign harnesses succeeded: baseline 82.028 s / 615.21 J, hidden-token episode 84.588 s / 634.41 J.
The observed +2.56 s / +19.2 J agrees with the deterministic prediction; every reported phase was identifiable.
The lead also verified structured prepare failures, successful flag paths, a synthetic HAZARD episode, and SystemClock record round-trip.
The passing lane tests cover standalone hazard disclosure/dwell, identity pins, ordering, clock pricing and whole-episode battery assist/charging.
This fix1c seat ran no Python tests: python3 --version could not start, and the environment remained offline after about ten minutes.
Only this report changes in fix1c; the spine shard defect, merge-timing note and pre-D1 hazard census requirement remain open.

## FILES

- joulewise/align/apple/__init__.py: existing package marker, unchanged in this fix round.
- joulewise/align/apple/sampler.py: existing adapter bridge; ns-product and serialized-stamp uncertainty, no duplicate anchor span, one-second dwell, and hazard-unjudged notes on every returned trace.
- joulewise/align/apple/endpoint.py: existing in-process MLX/mock endpoint; prefill-end first_token_ns and explicit backend selection.
- joulewise/align/apple/workload.py: prepare failures, runtime identity-probe forwarding, non-overlapping events, episode/transcript/provenance artifacts and single-request-summary warning flag.
- joulewise/align/apple/campaign.py: shared-generator configs, persistent pack UUID, AB/BA pairing with unmatched-cell disclosure, and members/order_manifest.json.
- joulewise/adapters/__init__.py: runtime registry; imports alignment only on align_episode; unsupported backends reach prepare without constructing a remote/other backend.
- configs/gates/hazard_refusals.json: two-line registry addition, naming the prospective workload and explaining that its census must precede D1 registration.
- tests/align/test_apple_campaign.py: real campaign CLI, status/energy checks, structured prepare failures, flag paths, order/identity checks and a HAZARD bundle span through the real battery judge.
- tests/align/test_apple_endpoint.py: existing real generation-helper test plus real registry/MLX prepare/identity projection and non-align import isolation.
- tests/align/test_apple_sampler.py: production parser/anchor fixture, per-trace hazard disclosure, dwell and epoch conversion regression.
- docs/align/apple_path.md: internal runtime, clock, reporting, adapter/battery, capacity and conditional detection-power plan.
- .codex-report/align-apple.md: lead-attributed verification at 9162afd6d, this continuation's executor limitation, observed/predicted end-to-end values, decisions and per-finding FIX LOG.

Continuation fix1c changes only .codex-report/align-apple.md; the other entries describe the existing lane implementation.

No other timing, import-fence, inventory or census registry was edited.
The protected PIPELINE.md, records.py and interfaces.py are unchanged.
The reducer, bundle reader, clock seam and production admission are unchanged.

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

## TESTS RUN

Evidence attribution: the runs below were performed by the lead locally at head
9162afd6d60a2733c170fb92f7b1879e31bbbad4, on macOS with
/opt/homebrew/bin/python3.13, JW_B5_SYNTHETIC_ONLY=1, a fresh TMPDIR per
invocation, and cwd at the repository root. They were supplied in the fix1c
continuation brief. Neither the original fix-round-1 seat nor this fix1c seat
ran these tests.

| Command | Lead's local result at 9162afd6d | This fix1c seat |
|---|---|---|
| python3 -m unittest discover -s tests/align -t . | Ran 19, OK | Not run |
| python3 -m unittest tests.hazards.test_refusal_allowlist tests.test_shard_tests | Ran 27, 1 failure in tests.test_shard_tests; refusal allowlist passes | Not run |
| Targeted 12-module command below | Ran 300, OK | Not run |

The third exact unittest command reported by the lead was:

    python3 -m unittest tests.test_mlx_runtime tests.test_adapters_powermetrics tests.test_mock_adapters tests.test_shard_split tests.test_fixture_orphan_census tests.test_custody_mode_inventory tests.test_revision_five_b_readers tests.test_single_count_discipline_census tests.test_digest_pin_census tests.test_identity_pins tests.test_repin tests.test_window_lineage

The single failure is
tests.test_shard_tests.test_union_is_full_discover_set_and_partitions_are_disjoint.
The shard list names tests.align.test_apple_campaign,
tests.align.test_apple_sampler, tests.align.test_apple_endpoint and
tests.align.test_records, while discovery finds align.*. The lead identifies
the same failure on spine 4d47c436. It remains outside WRITE_SCOPE.

The lead reported the following APPENDIX harness runs using committed code
(mode keep wherever applicable; policy mode with REV_IDLE=0 for e2e_policy2.py).
Only e2e_cli.py's summary filename was adapted from summary.json to the
repository's summary_metrics.json; no repository code changed for that run.

| Harness / arguments | Lead's local result at 9162afd6d | This fix1c seat |
|---|---|---|
| e2e_inproc.py <repo-root> keep | Both succeeded; 82.028 s / 615.2100000000811 J and 84.588 s / 634.4100000000919 J; every phase identifiable | Not run |
| e2e_cli.py <repo-root> keep | rc 0 for both; both succeeded; 82.028 s / 615.21 J and 84.588 s / 634.41 J | Not run |
| e2e_policy2.py <repo-root> policy, REV_IDLE=0 | rc 0; both bundles succeeded with the same durations/energies; 6 turns, 5 tools, hidden tokens 0 / 256 | Not run |
| edge.py <repo-root> keep | Missing task, bad spec and MLX without mirror unsupported at prepare with RUNTIME_UNAVAILABLE and no episode; tool_fault, turn_budget, malformed_tool and reasoning_outside succeeded with flags | Not run |
| hazard.py <repo-root> keep | succeeded; 84.587953664 s, 6 turns, 256 hidden tokens; all three align artifacts present | Not run |
| sysclock.py <repo-root> keep | SUCCEEDED; 6 turns, prefill-end first_token_ns; mapping uncertainty 2263 ns; records round-trip True | Not run |

The harness-directory and repository-root absolute paths in the lead's local
invocations were not supplied. Reproducible APPENDIX command spellings for
this cloud checkout are listed below; these are not claims that this seat
launched them. Each requires JW_B5_SYNTHETIC_ONLY=1 and its own fresh TMPDIR.

    python3 .review1/e2e_inproc.py /workspace/JouleWise keep
    python3 .review1/e2e_cli.py /workspace/JouleWise keep
    REV_IDLE=0 python3 .review1/e2e_policy2.py /workspace/JouleWise policy
    python3 .review1/edge.py /workspace/JouleWise keep
    python3 .review1/hazard.py /workspace/JouleWise keep
    python3 .review1/sysclock.py /workspace/JouleWise keep

The lead supplied counts and OK/failure outcomes, but no separate skip counts
or skip reasons; none are inferred. No optional dependency installation or
separate extra-dependent run was reported by the lead. This seat installed
no extras. The lane's synthetic native-MLX tests inject the native computation
boundary while retaining real adapter/helper/projection code; passing them
does not validate live MLX hardware.

This fix1c seat's first action attempted python3 --version from /workspace.
The command failed before process creation with:

    No usable execution environment is available. Wait for an environment to become available before using this tool.

After approximately ten minutes of environment startup waiting, a retry
returned the same error. Environment status then reported observed_phase
starting, connectivity offline, capabilities [], observations_current true
and failure null. This seat's executed Python test count is 0; it has no
own pass/fail/skip counts. No local checkout, TMPDIR, .review1 script,
syntax/import check, unittest or harness process could be started.
The earlier fix-round-1 seat likewise ran no tests.

Read-only GitHub inspection confirmed the current lane head and read the
existing report and protected contracts. This continuation uses the
authorized GitHub fallback to update only this report from the pushed apple
head, without restarting from the spine or force-pushing. These API reads
are repository checks, not Python execution. The whole suite was not run.

## END-TO-END

All observations in this section are the lead's local runs at
9162afd6d60a2733c170fb92f7b1879e31bbbad4, supplied in the continuation brief.
This fix1c seat observed no Python run.

The production-shaped deterministic world has six turns, five local ledger
tool calls, 27,648 prompt tokens and 4,608 base output tokens. The hidden
condition adds 256 generated tokens without changing the visible work.
At the mock world's 1 ms/prompt-token, 10 ms/output-token and 7.5 W,
prefill takes 27.648 s, baseline decode 46.080 s, and tool waits 8.300 s.
Thus the predicted baseline is 82.028 s / 615.21 J and the hidden condition
adds 256 * 0.010 s = 2.56 s and 2.56 * 7.5 W = 19.2 J.

The lead ran generate_campaign -> shared config renderer/write boundary ->
explicit order manifest -> run_campaign.py/CLI runtime registry/controller ->
existing mock runtime and telemetry -> bundle reduction ->
read_episode_bundle/BundleReader integration, and separately run_benchmark
in process with FakeClock, all using the fixes as committed.

| Quantity | Predicted baseline | Lead's observed baseline (in process) | Predicted hidden-token episode | Lead's observed hidden-token episode (in process) |
|---|---:|---:|---:|---:|
| Episode duration | 82.028 s | 82.028 s | 84.588 s | 84.588 s |
| Gross energy | 615.21 J | 615.2100000000811 J | 634.41 J | 634.4100000000919 J |
| Prefill energy | 207.36 J | 207.36 J | 207.36 J | 207.36 J |
| Decode energy | 345.60 J | 345.60 J | 364.80 J | 364.80 J |
| Tool-wait energy | 62.25 J | 62.25 J | 62.25 J | 62.25 J |

The observed tool contributions were 11.25 + 15.0 + 6.0 + 22.5 + 7.5 =
62.25 J. Observed dE = 19.200000000010846 J against predicted 19.2 J;
observed dT = 2.56 s against predicted 2.56 s. Agreement is within the
brief's 1e-6 relative bar for this deterministic world with no uncertainty.
Every reported phase was identifiable. Episode flags include
single_request_summary_fields_not_episode_metrics:ttft_s,decode_latency_s,energy_token_j.

The CLI harness returned rc 0 and status succeeded for both members,
reporting 82.028 s / 615.21 J and 84.588 s / 634.41 J. Its run ids were
apple-<pack uuid>-episode-1 and apple-<pack uuid>-episode-2.
The policy campaign, mode policy with REV_IDLE=0, exited 0 and produced
both succeeded bundles with the same numbers, six turns, five tools and
hidden-token totals 0 and 256. The lead's sole harness adaptation was
e2e_cli.py reading summary_metrics.json, matching the existing bundle contract.

The edge harness observed status unsupported, RUNTIME_UNAVAILABLE at prepare
and no episode written for:
- missing_task: task_unavailable:ModuleNotFoundError.
- mlx_no_model: runtime_unavailable:ValueError:local_model_mirror_required.
- bad_spec: task_unavailable:ValueError:unknown Apple episode spec schema.

The non-refusal flag paths succeeded: tool_fault, turn_budget (three turns,
31.436 s), malformed_tool (one turn, 7.168 s) and reasoning_outside, each
with its recorded flags.

The real synthetic HAZARD-window fixture succeeded and contained
align_episode.json, align_transcript.jsonl and align_turns.jsonl.
Its hidden episode was 84.587953664 s, with six turns and 256 hidden tokens,
against the 84.588 s deterministic prediction. The lead traced the
46.336 microsecond difference to FakeClock(start=1700000000) accumulating
float sleeps at epoch scale: about 0.04 of the 2.38e-7 s float spacing is
lost per 10 ms decode step over 4864 steps. At 7.5 W this is about 0.35 mJ,
far below the instrument's approximately 1 J attribution limit; it is not
an Apple lane timing defect.

The passing 19-test alignment discovery includes the real HAZARD bundle's
whole-episode span through battery.span_findings: a clean control has no
finding; -865 mA inside a late tool wait yields battery.assist, while
+865 mA inside a turn yields battery.member_span exclusion. Both bursts
exceed the existing 200 mA limit by 665 mA. The lead's passing test run
verifies this synthetic evidence path. It establishes no live model draw.

The lead's SystemClock harness returned SUCCEEDED, six turns with
first_token_ns at prefill end, and records round-trip True.
Its mapping had uncertainty_ns=2263 and method
"paired_clock_bracket_only; paired wall/monotonic envelope; half-ulp ns-product conversions".
The passing lane suite also exercises the native plist parser/current
powermetrics anchor, exact-rational epoch conversion regression, standalone
hazard disclosure and one-second dwell, real MLX identity projection with
synthetic native computation, and campaign order/pack uniqueness.
The D1 capacity/detection-power tables remain conditional planning inputs;
the reported Python runs do not independently check that planning arithmetic.

## DECISIONS I MADE

- Continue the pushed apple head 9162afd6d60a2733c170fb92f7b1879e31bbbad4, preserving its implementation and protected contracts. In fix1c, change only this report and use the authorized GitHub fallback after approximately ten minutes without an executor; never force-push.
- Attribute all supplied local Python results to the lead at 9162afd6d; this continuation ran zero Python tests. The historical no-executor statements below are replaced by those observed results where covered, without treating synthetic checks as hardware validation.
- The only workload registry is joulewise/adapters/__init__.py; no workload enum/table changes are needed in workloads.py, workload_profile.py, campaign_generator_core.py, suite.py or the instrument adapters.
- Follow the lead's finding-1 disposition: remove outer model-call phases; preserve inner align_turn_index metadata, turn JSONL and episode timestamps. Tool phases remain disjoint.
- Disable idle admission only in the all-mock campaign policy fixture, following tests.test_window_lineage.run_member; production admission is untouched.
- Require summary success and energy on every successful campaign/edge/battery measurement path. Prepare failures assert the true structured reason, absence of measurement stages and absence of a fictional episode.
- RUNTIME_UNAVAILABLE maps to status unsupported under controller.STATUS_BY_REASON (D-012). This governing code decides the test assertion even though the brief calls these prepare paths failures.
- Unsupported episode backends have no inner backend and fail during prepare, before client construction. Only mock and MLX are wrapped for execution.
- Forward identity_projection_metadata explicitly; identity_pins reads name, prepare metadata, that probe and cleanup, all preserved by the wrapper. The new regression retains the real registry and identity derivation.
- Keep in-process MLX because existing workloads use its same generation path. Greedy pin, local mirror and version/artifact identity stay authoritative; no service or extra model copy is launched.
- Charge each ns-product conversion from half its product spacing, plus sub-ns integer rounding where needed. Restored integer stamps carry quotient/conversion error into bridge resolution. The effective native bound already includes the wall-minus-monotonic span; charge only observations outside that envelope.
- Standalone sampling adds no enforcement. Every returned trace discloses that battery/AC/thermal/contention were unjudged; a one-second tail matches the policy minimum.
- Preserve generic reducer outputs but flag ttft_s, decode_latency_s and energy_token_j as unsuitable episode metrics, and document that align reporting does not print them.
- Match the records.Turn definition: first_token_ns is prefill end, not the first completed decode token event.
- Default to matched-cell AB/BA ordering; never duplicate or drop unmatched episodes. Persist a pack UUID to distinguish independently generated packs with the same model_tag; tags identify episode ordinals.
- Add only the authorized two-line hazard census registry entry. Its prospective-path reason explicitly requires census coverage before D1 registration; it does not represent this unregistered code as current registered-pack authority.
- The D1 plan makes both e and sigma_window explicit planning inputs, prints e = 0.05/0.10 sensitivity, and cites the historical 0.0998 J/token reconstruction at SYNTHESIS-IMPACT-FIRST.md:5952.
- Per-member cooldown is separate from the reserve: budget both the policy's 30 s sustained recovery and 300 s cap scenarios. Whole-machine draw for each D1 candidate remains a named pilot parameter; no model-specific watts are invented.
- The existing battery-assist remedy remains in span_findings/smc_span_findings: DISCLOSE for on-AC discharge, exclusion for charging, AC loss and missing evidence. The lead's passing lane suite at 9162afd6d verifies the real-bundle synthetic discharge/charging regression; it changes no inclusion rule.
- The repository's bundle contract writes summary_metrics.json. The lead adapted only that filename in the uncommitted e2e_cli.py harness and completed its run; the mismatch is resolved and requires no repository code change.
- Keep the D1 e/sigma/cooldown/draw documentation as conditional planning. The lead's executed Python checks do not constitute the independent D1 analysis check; finding 8 is therefore recorded as a documentation fix with that limit.

## CONTRACT-CHANGE

No installed contract change. Preserve the previous lane-local proposals:
1. Optional per-sample integer averaging supports on PowerTrace; current workaround is interval notes and authoritative raw/CSV evidence.
2. Optional clock-mapping capability on PowerSampler; current workaround is ApplePowerSampler.clock_mappings.
3. Post-telemetry artifact finalization; current workaround is an immutable episode/trace bundle join in read_episode_bundle.

These are prospective suggestions, not approval blockers or modifications to the three protected files.

## OPEN ISSUES

- tests.test_shard_tests still has the spine discovery/shard naming defect: entries name tests.align.* while discovery finds align.*. The lead's local 27-test group at 9162afd6d reproduced its single failure in test_union_is_full_discover_set_and_partitions_are_disjoint; it also fails on spine 4d47c436. It remains unchanged and outside WRITE_SCOPE. tests.hazards.test_refusal_allowlist passes.
- Merging joulewise/adapters/__init__.py makes existing registered packs carry code.changed_since_registration. The lead decides merge timing.
- The minimal hazard registry exemption covers the prospective branch only; complete its census before registering an actual D1 HAZARD pack.
- This fix1c cloud environment never became executable within approximately ten minutes. Independent reruns by this seat were unavailable; verification above is the lead's local evidence at 9162afd6d. This is not an assertion that the implementation remains untested.
- Real MLX/model, hardware attribution, calibration transfer, registered extraction membership and authenticated launch remain future lead/hardware gates. No physical validation or registration was attempted.
- Conditional D1 capacity/power arithmetic needs the required independent analysis check and pilot-supported inputs before any printed research number. No claim-bearing research result is created here.

## NEEDS_RULING

none. No data inclusion rule or claim number was changed. The lead's local verification resolves the prior unexecuted-fix and CLI harness-filename concerns; the open items above retain their existing scope.

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
