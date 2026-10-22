# align-apple lane report

## SUMMARY
This is a pushed, unverified source draft; the build is not execution-validated.
The Apple sampler delegates capture, native parsing and anchoring to the existing powermetrics adapter.
The endpoint reuses in-process MlxRuntimeAdapter generation and records model/revision/MLX identity.
The workload registry routes align_episode members through the existing controller and campaign CLI.
Episodes, full transcripts and turn provenance are returned as ordinary run-bundle artifacts.
An immutable reader joins episode records with the controller's power trace and clock evidence.
Nine stdlib synthetic tests and a provisional D1 capacity/power/cost plan are supplied.
Both required test commands were attempted but could not start: the cloud executor remained unavailable.
No hardware was measured, armed, installed or loaded; the three protected contract files were unchanged.

## FILES
- joulewise/align/apple/__init__.py: package marker.
- joulewise/align/apple/sampler.py: PowerSampler, epoch-to-monotonic mapping, integer-ns observations and interval-support representation.
- joulewise/align/apple/endpoint.py: in-process MLX ChatEndpoint, existing mock-runtime scripting, explicit tool-envelope parsing, per-turn provenance.
- joulewise/align/apple/workload.py: EpisodeSpec, RuntimeAdapter wrapper, episode/tool loop and immutable bundle-to-Episode join.
- joulewise/align/apple/campaign.py: deterministic episode configs through scripts.generate_matrix.build_config and shared campaign-generator rendering/write checks.
- joulewise/adapters/__init__.py: the sole runtime registry addition: resolve_runtime dispatches workload_profile.name == "align_episode" to the lane adapter. Other workload dispatch is unchanged.
- tests/align/test_apple_campaign.py: three tests, including the real generator -> run_campaign subprocess -> normal CLI/controller/mock adapters -> bundle reader chain.
- tests/align/test_apple_sampler.py: four tests through the real native parser/current anchor, unresolved evidence, permission denial and malformed sample flags.
- tests/align/test_apple_endpoint.py: two tests, including the existing MLX _generate helper driven by a synthetic native-computation stream.
- docs/align/apple_path.md: execution/clock semantics, prospective registration, model-memory arithmetic, capacity and quiet-time scenarios.
- .codex-report/align-apple.md: this report.

No shard-timing, import-fence, inventory or census registry was edited: a repository-wide test never started, so the brief's conditional authority to change those registries was not triggered.

## PUBLIC API
All modules are under joulewise.align.apple.

- sampler.seconds_ns(seconds: float) -> int
- sampler.monotonic_ns(stamp: ClockStamp) -> int
- sampler.stamp_mapping(stamps: Sequence[ClockStamp], *, episode_domain: str, evidence: Mapping[str, Any] | None = None) -> tuple[ClockMapping, tuple[str, ...]]
- sampler.power_records(samples: Sequence[PowerSample], *, nominal_interval_ns: int, evidence: Mapping[str, Any] | None = None) -> tuple[tuple[PowerTrace, ...], tuple[str, ...]]
- sampler.ApplePowerSampler(config: BenchmarkConfig, clock: Clock, *, episode_domain: str, context: RunContext | None = None, adapter: Any | None = None)
- ApplePowerSampler.start() -> None
- ApplePowerSampler.stop() -> tuple[PowerTrace, ...]
- ApplePowerSampler.clock_mappings, flags and uncertainty_evidence expose recorded conversion/collector evidence.
- endpoint.parse_completion(text: str, *, reasoning_tokens: int = 0) -> tuple[str, str, tuple[ToolCallRequest, ...], tuple[str, ...]]
- endpoint.MlxEndpoint(runtime: Any, config: BenchmarkConfig, clock: Clock, *, episode_domain: str, prepare_metadata: Mapping[str, Any] | None = None, mock_turns: Sequence[Mapping[str, Any]] = ())
- MlxEndpoint.chat(messages: Sequence[ChatMessage], *, tools: Sequence[Mapping[str, Any]] = (), max_tokens: int, temperature: float, seed: int | None) -> ChatResult
- workload.EpisodeSpec(task_factory: str, condition: Condition, seed: int, max_turns: int, max_tokens: int, temperature: float, task_kwargs: Mapping[str, Any] = {}, mock_turns: tuple[Mapping[str, Any], ...] = (), schema: str = SPEC_SCHEMA)
- EpisodeSpec.to_text() -> str
- EpisodeSpec.from_text(text: str) -> EpisodeSpec
- workload.EpisodeRuntimeAdapter(runtime: Any, clock: Clock)
- EpisodeRuntimeAdapter.prepare(config, context=None) -> AdapterResult
- EpisodeRuntimeAdapter.warmup(config, context=None) -> AdapterResult
- EpisodeRuntimeAdapter.run_workload(config, context=None) -> RuntimeResult
- EpisodeRuntimeAdapter.cleanup(config, context=None) -> AdapterResult
- workload.read_episode_bundle(bundle: Path) -> Episode
- campaign.generate_campaign(base: BenchmarkConfig, specs: Sequence[EpisodeSpec], output_root: Path, *, model_tag: str) -> tuple[Path, ...]

## TESTS RUN
No test process executed. The executor was unavailable from initial intake through the latest status check. Counts: 0 executed; pass/fail/skip counts unavailable, not zero failures or a green suite.

Exact commands attempted from /workspace/JouleWise:

    JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/align -t .
    JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests

Each exec_command call returned before process creation:

    No usable execution environment is available. Wait for an environment to become available before using this tool.

The required fresh external TMPDIR could not be created for the same reason. Repeated pwd attempts failed identically. environment_status reported pending/starting, offline, observations_current=true, without failure details; diagnostic inventory had no retained records. Waiting for startup did not yield a usable executor. The user was asked asynchronously to restart/reattach the workspace.

Nine new unittest test methods were statically inventoried. They are unrun, including syntax/import validation. No skip result is claimed. No optional dependency was installed, so there is no extra-dependent run. The fake MLX generation test uses the real stdlib-importable adapter with an injected computation stream, not an installed MLX runtime.

GitHub read-only inspection covered the protected records/interfaces/plan and the six named workload/runtime/instrument files, plus intake, orchestration, clock/fiducial/transition, controller, bundle, validation and generator code. GitHub was also used to commit/fast-forward only the authorized lane because the local executor never became available.

## END-TO-END
UNEXECUTED TEST WORLD, not an observed result:

- Six model calls, five local ledger tools, one benign and one sabotage episode sharing seed 19.
- Uncached prompt counts: 2048, 3072, 4096, 5120, 6144, 7168; total 27,648.
- Base output counts: 512, 512, 768, 768, 1024, 1024; total 4,608.
- Tool delays: 1.5, 2.0, 0.8, 3.0, 1.0 s; total 8.3 s.
- D-019's existing 1 ms/prompt-token and 10 ms/output-token mock runtime predicts 82.028 s, and the existing 7.5 W mock telemetry predicts 615.21 J.
- Add 256 hidden final-turn tokens while preserving visible decode counts: predicted +2.56 s and +19.2 J, giving 84.588 s and 634.41 J. The 19.2 J effect exceeds the brief's ~1 J attribution bar, so its absence fails the planned assertion.
- Planned chain: generate_campaign -> existing build_config/shared generator core -> scripts/run_campaign.py subprocess -> ordinary CLI/default runtime registry -> existing controller -> MockRuntimeAdapter and MockTelemetryAdapter -> raw/trace/episode/transcript/provenance artifacts -> BundleReader/read_episode_bundle -> existing integration and repeated phase windows.
- Separate native collector world: 601 plist records, 100 ms steady cadence, a 999 ms first support, integer-mW powers with 0.2 W rail oscillations, and the repository's epoch-scale paired-clock fixture. Only collection is injected; production plist parsing, current rate-aware anchoring, timestamp reconstruction and trace projection run in the proposed test.
- The native world and effect/control worlds have not run. No HAZARD_PACK lineage fixture or live instrument result is claimed.

## DECISIONS I MADE
- Workload kind is the existing open workload_profile.name string. The registry addition is joulewise/adapters/__init__.py; there is no new enum or change to schemas.py, suite.py, workloads.py, workload_profile.py or campaign_generator_core.py.
- Use the existing in-process MLX generation helper, including the suite's natural-EOS path, because current MLX workloads already use it. No server, alternate model copy or new measurement controller is introduced.
- Require a local MLX model directory at episode prepare time; record a flag instead of allowing implicit weight downloads.
- Preserve the existing greedy sampler pin. Nonzero requested temperatures, missing revision/version identity and retokenized reasoning counts are explicit flags.
- Task factories implement AgentTask and can accept the injected clock, keeping production and simulated tool timing on the same controller clock.
- Reuse the existing current native anchor and paired ClockStamp observations; never estimate a spawn midpoint. Carry the complete adapter bound plus bridge/representation uncertainty.
- Shared records contain integer-ns timestamps, including hardware clock observations. Raw controller-clock metadata remains in ordinary bundle provenance.
- Do not infer a sensor quantum from the adapter's mW-to-W unit conversion.
- Preserve variable averaging supports in trace notes and raw/CSV evidence; record a flag rather than treating them as point measurements.
- Runtime writes a trace-join marker in the episode; read_episode_bundle joins the controller's later telemetry in memory. A finalized bundle is never rewritten.
- Turn intervals delimit model calls. Following tool intervals stay grouped under the originating turn, which the records contract permits. Indexed phase events expose both.
- Keep task scoring/serialization outside Episode.end_ns, recording that the ordinary controller's measured interval includes the harness tail. The future analysis must register its interval.
- Use the ordinary campaign generator and runner. The provisional align_pack.json does not pretend to be an authenticated HAZARD_PACK or registered statistical plan.
- Synthetic scripts alter response text only after actual mock generation; the workload timeline and telemetry still run through the repository's real adapters.
- Capacity and detection figures in apple_path.md are explicitly conditional planning inputs. window_duration_margins.py supplies authenticated duration/sample/cadence margins, not a campaign scheduler; no scheduling result is attributed to it.

## CONTRACT-CHANGE
Requested prospective improvements, with lane-local workarounds already supplied:

1. Add optional per-sample integer averaging supports to PowerTrace. records.v1 has only one averaging_window_ns, which cannot exactly represent variable native supports. Current workaround: integer interval notes plus the existing raw/CSV source for integration.
2. Expose an optional clock-mapping capability on PowerSampler. The current protocol returns traces only; ApplePowerSampler provides clock_mappings as a lane-local property.
3. Consider a post-telemetry artifact-finalization capability in the controller/runtime interface so an episode can be serialized with its trace once. Current workaround: immutable episode + trace bundle inputs joined by read_episode_bundle.

No protected contract file was modified. These are proposals, not installed semantics or a request to block independent lane work.

## OPEN ISSUES
- Blocking: no usable cloud executor. Both required suites, syntax/import checks and all nine new tests remain unrun. The source is not ready for measurement.
- Run the tests from a local checkout of the pushed lane, with JW_B5_SYNTHETIC_ONLY=1 and a fresh external TMPDIR; resolve actual failures within scope before treating this draft as implemented.
- Run repo-wide timing/import-fence/inventory checks; add only the new names if an actual failure invokes the brief's limited registry authority.
- Exercise authenticated synthetic HAZARD_PACK lineage, idle admission, dwell and flags end to end. The proposed campaign test exercises the ordinary runner/controller path, not an authenticated window fixture.
- Independently verify the numerical planning example and future analysis implementation under PIPELINE.md's different-model rule. No numerical-analysis implementation is supplied here.
- Real MLX/model, calibration transfer, instrument attribution and campaign registration remain future hardware/lead gates. No physical validation was attempted.
- The endpoint deliberately reuses private MLX generation/tokenizer helpers; verify them against the pinned MLX adapter version in the actual executor.
- The prospective D1 plan needs registered analysis/extraction membership and authenticated launch objects; this draft neither issues nor installs them.

## NEEDS_RULING
None. No research-data inclusion rule or claim number was selected. The execution blocker is environment availability, not a methodology choice.
