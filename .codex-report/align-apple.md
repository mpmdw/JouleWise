# align-apple lane report — fix round 1

## SUMMARY
NOT EXECUTED: the cloud executor never became usable; these are source fixes, not a verified build.
Removed overlapping turn phases and made campaign/edge tests require successful energy summaries.
Unavailable tasks, specs, mirrors and unsupported backends now fail at prepare with RUNTIME_UNAVAILABLE.
Clock mapping prices ns-product rounding; standalone sampling discloses missing hazard judgments and dwells one second.
Campaign packs now have explicit counterbalanced order, episode tags and persistent pack-unique run ids.
Added real-bundle battery-assist/charging and real MLX identity-projection regression paths using synthetic native computation.
The D1 plan includes per-member cooldown, explicit energy/noise parameters and the 140 W adapter/battery disposition.
Only authorized paths changed; no hardware, arming, installation, contract edits or force pushes occurred.

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
- .codex-report/align-apple.md: execution limitations, decisions and per-finding FIX LOG.

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
Nothing ran. Executed test count: 0. Pass/fail/skip counts are unavailable; no green result is claimed.
Even the first requested command, python3 --version, failed before process creation.

Every exec attempt returned:

    No usable execution environment is available. Wait for an environment to become available before using this tool.

The executor stayed pending/offline with observations_current=true, capabilities=[], and no reported failure reason.
It remained unavailable beyond the brief's approximately ten-minute fallback interval and through the final source checks.
No TMPDIR or .review1 harness files could be materialized, and no local fetch/checkout, syntax/import validation, unittest process or harness process started.
The APPENDIX commands below were submitted to the executor, but rejected before launch.
The mktemp expression requests a fresh external TMPDIR for each eventual invocation; it did not execute here.

Exact commands attempted from /workspace/JouleWise:

    python3 --version
    JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR="$(mktemp -d)" python3 -m unittest discover -s tests/align -t .
    JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR="$(mktemp -d)" python3 -m unittest tests.hazards.test_refusal_allowlist tests.test_shard_tests
    JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR="$(mktemp -d)" python3 -m unittest tests.test_mlx_runtime tests.test_adapters_powermetrics tests.test_mock_adapters tests.test_shard_split tests.test_fixture_orphan_census tests.test_custody_mode_inventory tests.test_revision_five_b_readers tests.test_single_count_discipline_census tests.test_digest_pin_census tests.test_identity_pins tests.test_repin tests.test_window_lineage
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 .review1/e2e_inproc.py /workspace/JouleWise keep
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 .review1/e2e_cli.py /workspace/JouleWise keep
    JW_B5_SYNTHETIC_ONLY=1 REV_IDLE=0 TMPDIR="$(mktemp -d)" python3 .review1/e2e_policy2.py /workspace/JouleWise policy
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 .review1/edge.py /workspace/JouleWise keep
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 .review1/hazard.py /workspace/JouleWise keep
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 .review1/sysclock.py /workspace/JouleWise keep
    JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d)" python3 .review1/e2e_policy2.py /workspace/JouleWise keep

The whole suite was never requested or run.
No optional dependency was installed; no extra-dependent run or skip result exists.
The synthetic native-MLX tests inject the library computation boundary while retaining the real adapter/helper/projection functions; they require no installed MLX extra.

Read-only GitHub inspection and compare confirmed the parent head, scoped file list, two-line hazard registry delta and successive fast-forward updates.
Those API checks are source/custody checks, not executed Python tests.
The work continued from 74b559d554f3172bddcfc5ecad323711e75e4ee8 through GitHub tools because the VM never started.
One large tree-creation call was cancelled; storing the registry blob separately then creating its tree succeeded. No lane update was lost or force-pushed.

## END-TO-END
No run printed end-to-end numbers in this seat. No observed duration, joules, mapping uncertainty, summary status or battery judgment is reported.
The reviewer's observations in the brief are not relabelled as this seat's results.

Unexecuted regression paths now present in source:
- generate_campaign -> shared build_config/render/write checks -> explicit order manifest -> run_campaign.py -> CLI registry/controller -> existing mock runtime/telemetry -> immutable bundle -> read_episode_bundle/BundleReader and integration.
- The production-shaped world has six turns, five local ledger tools, the given context/output shapes and a hidden-token/control pair. Tests assert succeeded, non-null gross/phase energy, unchanged visible counts and the derived deterministic energy/duration comparisons. Analytic predictions remain clearly labelled in apple_path.md, not claimed here as measurements.
- build_window/run_member -> real synthetic HAZARD bundle -> its sampling-marker span -> real battery.span_findings with real-byte gauge fixtures and 1 Hz SMC readings. The clean control expects no finding; a -865 mA burst inside the late tool wait expects battery.assist, while +865 mA inside a turn expects battery.member_span. Both exceed the code's 200 mA limit. None of these outcomes has been observed here.
- Generated align MLX configs -> real runtime registry -> real prepare with only native-library computation injected -> forwarded identity_projection_metadata -> real identity_pins probe and model/runtime/config derivation.
- Native plist fixture -> existing PowermetricsTelemetryAdapter parser/current anchor -> clock mapping and PowerTrace representation. The separate clock regression uses an exact-rational oracle for epoch-product conversion error and detects duplicate anchor-span charging.

## DECISIONS I MADE
- Continue the existing lane head, preserving its implementation and protected contracts; use the brief's GitHub fallback after execution stayed unavailable. Push each meaningful source step without force.
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
- Source inspection finds the requested battery-assist remedy already in span_findings/smc_span_findings. Keep DISCLOSE for on-AC discharge; keep charging, AC loss and missing-evidence exclusions. The new real-bundle test must still execute before calling that path verified.
- The repository's bundle contract writes summary_metrics.json. Tests use that name; no out-of-scope bundle compatibility change was introduced for the APPENDIX e2e_cli.py reference to summary.json.

## CONTRACT-CHANGE
No installed contract change. Preserve the previous lane-local proposals:
1. Optional per-sample integer averaging supports on PowerTrace; current workaround is interval notes and authoritative raw/CSV evidence.
2. Optional clock-mapping capability on PowerSampler; current workaround is ApplePowerSampler.clock_mappings.
3. Post-telemetry artifact finalization; current workaround is an immutable episode/trace bundle join in read_episode_bundle.

These are prospective suggestions, not approval blockers or modifications to the three protected files.

## OPEN ISSUES
- Blocking verification: the executor never became usable. All source fixes, syntax/import checks, fifteen lane test methods (static source inventory only), requested suites and APPENDIX harnesses remain NOT EXECUTED.
- Materialize the APPENDIX under untracked .review1/ in an executable checkout and run the recorded commands with fresh TMPDIRs. Nothing under .review1/ was committed.
- Harness mismatch: APPENDIX e2e_cli.py reads summary.json, but the existing bundle writer produces summary_metrics.json. Its summary read must use the existing contract before that harness can finish. No harness result or silent check removal is claimed.
- tests.test_shard_tests has the reviewer-established spine defect: shard entries name tests.align.* while discovery finds align.*. It remains unchanged and out of scope. The requested command was attempted here but no process started, so this seat has not observed a new failure.
- Merging joulewise/adapters/__init__.py makes existing registered packs carry code.changed_since_registration. The lead decides merge timing.
- The minimal hazard registry exemption covers the prospective branch only; complete its census before registering an actual D1 HAZARD pack.
- Real MLX/model, hardware attribution, calibration transfer, registered extraction membership and authenticated launch remain future lead/hardware gates. No physical validation or registration was attempted.
- Conditional capacity/power arithmetic needs the required independent analysis check and pilot-supported inputs before any printed research number. This plan creates no claim-bearing result.

## NEEDS_RULING
none. No data inclusion rule or claim number was changed. The outstanding blockers are execution availability and the stated harness-path mismatch.

## FIX LOG
- 1 — fixed (NOT EXECUTED), 84fc4efefb73aa587497cc5d3931ded641ea87ef: remove enclosing align_turn_N phases; retain indexed inner events and turn records.
- 2 — fixed (NOT EXECUTED), 84fc4efefb73aa587497cc5d3931ded641ea87ef: disable idle_admission.enabled in the synthetic campaign test only.
- 3 — fixed (NOT EXECUTED), 84fc4efefb73aa587497cc5d3931ded641ea87ef, b9b0235e883272e04dc4bf2b8dab4724df017c22, 69a0bd56a1948c78fe52e33442b7f16de7507b27: assert success/energy on valid campaign, flag and HAZARD paths, and structured early failure on invalid paths.
- 4 — fixed (NOT EXECUTED), b9b0235e883272e04dc4bf2b8dab4724df017c22: two-line configs/gates/hazard_refusals.json entry; alignment import stays branch-local; merge timing is disclosed above.
- 5 — fixed (NOT EXECUTED), 84fc4efefb73aa587497cc5d3931ded641ea87ef, 69a0bd56a1948c78fe52e33442b7f16de7507b27: bad tasks/specs/mirrors return RUNTIME_UNAVAILABLE at prepare; no failed-spec benign episode is written.
- 6 — fixed (NOT EXECUTED), 84fc4efefb73aa587497cc5d3931ded641ea87ef, b9b0235e883272e04dc4bf2b8dab4724df017c22, 69a0bd56a1948c78fe52e33442b7f16de7507b27: support only mock/MLX execution, reject every other backend at prepare, forward the runtime probe and test real align identity derivation.
- 7 — fixed (NOT EXECUTED), 0882e9ecff2c2ce9ec106badf3e6d7f10abd3a59, 69a0bd56a1948c78fe52e33442b7f16de7507b27: ns-product half-ulp pricing, serialized-stamp resolution and no second charge of the anchor span; clock.py untouched.
- 8 — fixed (NOT EXECUTED), b9b0235e883272e04dc4bf2b8dab4724df017c22, 69a0bd56a1948c78fe52e33442b7f16de7507b27: sourced historical e evidence, explicit e/sigma sensitivity, and policy-key-derived per-member cooldown in capacity.
- 9 — fixed (NOT EXECUTED), b9b0235e883272e04dc4bf2b8dab4724df017c22: runner-compatible members/order_manifest.json and default matched AB/BA order.
- 10 — fixed (NOT EXECUTED), 0882e9ecff2c2ce9ec106badf3e6d7f10abd3a59: hazard.unjudged flag on every standalone trace and one-second post-window dwell.
- 11 — fixed (NOT EXECUTED), 84fc4efefb73aa587497cc5d3931ded641ea87ef, b9b0235e883272e04dc4bf2b8dab4724df017c22: episode/artifact flag names all three misleading summary fields; docs prohibit printing them for align.
- 12 — fixed (NOT EXECUTED), 84fc4efefb73aa587497cc5d3931ded641ea87ef: first_token_ns uses the prefill end event.
- 13 — fixed (NOT EXECUTED), b9b0235e883272e04dc4bf2b8dab4724df017c22: episode ordinal tags and persistent pack-unique UUID run ids.
- Battery assist continuation — fixed (NOT EXECUTED), b9b0235e883272e04dc4bf2b8dab4724df017c22: real-bundle whole-episode span control, late tool-wait discharge and in-turn charging tests, plus per-candidate draw parameters and the DISCLOSE disposition.
- tests.test_shard_tests — rejected: the brief explicitly identifies the discovery/shard naming mismatch as a spine defect outside WRITE_SCOPE; no source change made, command attempt blocked before execution.
