# Alignment budget lane report

## SUMMARY
Implemented the budget pilot harness, CLI and provisional rented-GPU protocol.
Added a pinned, digest-checked MMLU source and eight authored offline fixture questions.
Added thinking controls, per-item median calibration, forced continuations and deletion controls.
Added paired hint-use labels, a fixed local monitor, Wilson rates and accuracy.
Added resumable trial records with shared Episodes and flagged whole-episode energy summaries.
Added 25 unittest methods, including five configurations x 200 items and 80-seed coverage.
All changes are saved on lane/2026-10-21-align-budget; protected contracts are unchanged.
Verification is INCOMPLETE: the cloud workspace never became executable; no Python test ran.

## FILES
- joulewise/align/budget/__init__.py: stdlib package entry.
- joulewise/align/budget/__main__.py: synthetic/local-server CLI, checkpoint and result exports.
- joulewise/align/budget/items.py: ItemSource, HF revision/digest pin, MMLU loaders and hint generation.
- joulewise/align/budget/fixture.py: eight authored questions in an installed Python module.
- joulewise/align/budget/conditions.py: condition definitions, backend options, token deletion and HTTP/tokenizer adapter.
- joulewise/align/budget/score.py: paired answer judge, fixed monitor and Wilson score intervals.
- joulewise/align/budget/energy.py: flagged gross-episode power/counter integration and conditional sensor bounds.
- joulewise/align/budget/run.py: frozen trial/calibration/summary records, matrix execution and append-only resumption.
- joulewise/align/budget/synthetic.py: scripted reasoning/monitor endpoints, mock tokenizer, clock and noisy sampled power.
- tests/align/test_budget.py: 25 test methods; one optional pyarrow method uses skipUnless.
- docs/align/budget_pilot.md: internal protocol, usage, model order, NVML repetition dependency and kill condition.
- .codex-report/align-budget.md: this report.

No registry file was changed. No repository-wide test could run, so no registry
exception was invoked. The temporary fixture.json introduced during checkpoints
was removed; fixture.py is the single committed fixture source.

## PUBLIC API

Types and functions use the signatures in their modules; the principal entrypoints are:

    ItemSource.load() -> ItemBatch
    HintItem(item_id, question, choices, correct_answer, hinted_answer, hint_kind,
             provenance="authored-fixture", flags=())
    HintItem.prompt(*, hinted: bool = True) -> str
    ItemBatch(items: tuple[HintItem, ...], flags: tuple[str, ...] = ())
    HubPin(repository: str, revision: str, path: str, sha256: str)
    FixtureSource(seed: int = 0).load() -> ItemBatch
    HubMMLUSource(timeout_s: float, pin: HubPin = <committed cais/mmlu pin>,
                  seed: int = 0, fetch = _download).load() -> ItemBatch
    hint_suite(rows, *, seed: int = 0, provenance: str = "authored-fixture") -> ItemBatch

    Condition(name: str, mode: str = "on", fraction: float | None = None,
              concise_prompt: str = CONCISE_PROMPT)
    default_conditions(fractions = (1.0, 0.6, 0.4, 0.3)) -> tuple[Condition, ...]
    thinking_options(backend: str, enabled: bool) -> dict[str, Any]
    cap_tokens(median_tokens: float, fraction: float) -> int
    delete_spans(text: str, *, remove_tokens: int, codec: TokenCodec, seed: int) -> Deletion
    TokenCodec.encode(text: str) -> Sequence[int]
    TokenCodec.decode(tokens: Sequence[int]) -> str
    LocalEndpoint(base_url, model, backend, timeout_s, options={}, transport=None)
    LocalEndpoint.configured(options: Mapping[str, Any]) -> LocalEndpoint
    LocalEndpoint.chat(messages, *, tools=(), max_tokens, temperature, seed) -> ChatResult
    LocalEndpoint.encode(text: str) -> Sequence[int]
    LocalEndpoint.decode(tokens: Sequence[int]) -> str

    parse_answer(text: str, labels: Sequence[str]) -> str | None
    judge_hint_use(item: HintItem, answer_text: str, paired_text: str) -> HintUse
    HintMonitor(endpoint, model="openai/gpt-oss-20b", max_tokens=64, seed=0,
                revision="unspecified")
    HintMonitor.assess(item: HintItem, reasoning: str, *, visibility="full") -> MonitorAssessment
    wilson(successes: int, trials: int, *, confidence: float = 0.95) -> Rate
    Energy(joules: float | None, uncertainty_j: float | None = None, flags=())
    episode_energy(episode: Episode, *, channels=None) -> Energy

    ModelSpec(model, size_b, backend, endpoint_identity, codec, endpoint_factory,
              attention_design="unspecified", clock_domain="client:monotonic",
              clock_mappings=(), controls_verified=False)
    Settings(max_tokens, answer_max_tokens, calibration_repetitions=3,
             temperature=0.6, confidence=0.95, thinking_open="<think>",
             thinking_end="\n</think>\n", measurement_id="unmeasured")
    BudgetTrial(trial_id, model, size_b, attention_design, condition, settings,
                monitor_configuration, item_id, hint_kind, seed, reasoning_tokens,
                answer_tokens, visible_reasoning_tokens, median_reasoning_tokens,
                requested_cap_tokens, start_ns, end_ns, monitor_verdict,
                monitor_flagged, monitor_result, hint_use, generation, paired,
                episode, removed_tokens=0, deleted_spans=(), source_trial_id=None,
                flags=(), schema="joulewise.align.budget.v1")
    run_matrix(items, models, conditions, *, seeds, settings, monitor,
               checkpoint=None, sampler_factory=None,
               clock=time.monotonic_ns) -> MatrixResult
    summarize(trials, *, confidence=0.95,
              energy_reducer=episode_energy) -> tuple[Summary, ...]
    summary_table(rows: Sequence[Summary]) -> str

    synthetic_items(count: int = 200) -> ItemBatch
    run_synthetic(*, count=200, seeds=(0,), with_power=True, sizes_b=(4.0,),
                  checkpoint=None) -> MatrixResult
    main(argv: list[str] | None = None) -> int

Generation, Calibration, MatrixResult, Summary, Deletion, HintUse, Rate and
MonitorAssessment are lane-local dataclasses. The shared to_json/from_json
functions round-trip them, including integer nanoseconds and nested Episodes.
BudgetTrial follows the shared unknown-schema rejection convention.

## TESTS RUN

**Python: 0 tests executed; actual discovered counts and skip outcomes are unknown.**
The source defines 25 methods, with one optional pyarrow decoder test. This is
an inventory, not a passing test count. No import, compile, unit, integration,
CLI or end-to-end Python command was launched successfully.

The execution tool rejected both initial workspace inspection and a later pwd
attempt before launching a shell:

    No usable execution environment is available. Wait for an environment to become available before using this tool.

The selected environment remained offline and pending/starting, with no failure
detail, throughout work. wait_for_environment remained pending. An asynchronous
request for a restarted/running environment was sent. Therefore the requested
local fetch/checkout, git status and baseline checks were also not executable.

The exact commands still REQUIRED from /workspace/JouleWise are:

    python3 -m unittest discover -s tests/align -t .
    python3 -m unittest tests.align.test_budget -v
    python3 -m joulewise.align.budget --synthetic --count 200 --seeds 0 --sizes 4,8,14 --output /tmp/budget-smoke --checkpoint /tmp/budget-smoke.jsonl
    python3 -m unittest discover -s tests
    git diff --check

No extra was installed; shell/pip execution was unavailable. Once the environment
works, record the stdlib-only run first. If installation is permitted, also run:

    python3 -m pip install pyarrow
    python3 -m unittest discover -s tests/align -t .
    python3 -m unittest tests.align.test_budget.BudgetItemsTests.test_optional_parquet_uses_verified_bytes_offline -v

The optional test constructs Parquet bytes in memory and passes them through
the real digest/decoder/hint path. No test fetches public data or contacts an
endpoint. Tests patch both HTTP entrypoints to fail if reached.

Read-only checks actually performed through the connected tools:
- GitHub compare showed only the 12 allowed files above, all added relative to
  spine 4d47c4362352ccd8d4d904134a79f0d8260b21b5.
- Every saved source/doc file was fetched back and compared to the authored text.
- A lightweight V8 lexical scan found balanced delimiters/strings and no trailing
  whitespace in the ten Python files. This is NOT Python syntax compilation.
- Protected file blob IDs match the initially read spine:
  PIPELINE.md 829c944bb26e2ced2f5e260f8f799ac4626a62f7;
  records.py ca3523d5fce7abd97e0ca985ecf7d0e768da4c20;
  interfaces.py b0468f41721add4ee3b95edf68edeea0e7e2ff98.
- A separate V8 arithmetic sketch reproduced SHA-256's standard abc vector and
  CPython's integer-seed-zero MT first draw, then checked the scripted design's
  marker counts and interval separation. It did not execute production Python.
  This sketch and the Decimal score-test oracle were authored by this same seat;
  neither satisfies the plan's different-model provenance requirement.

## END-TO-END

**Implemented, NOT EXECUTED through Python.** The intended test chain is:

authored items -> per-item uncapped calibration -> hinted + no-hint calls ->
forced continuation where selected -> token deletion on reused source work ->
fixed ChatEndpoint monitor -> BudgetTrial/shared Episode -> summaries -> energy.

The five configurations are thinking_on, budget_0.6, budget_0.4, budget_0.3 and
deletion_0.6, each with 200 items. The default full condition list additionally
covers thinking off, concise, budget_1.0 and deletion controls at every default
fraction. Separate tests cover those paths and the zero-cap continuation.

Designed quantities, not hardware observations:
- 1024 uncapped reasoning tokens, two answer tokens and 256-token prefills.
- Median calibration: three uncapped passes per item, stored with their Episodes.
- Floors of fractional medians: 614, 409 and 307 reasoning tokens.
- Positive hint-use probability 0.75. Given a positive, disclosure probability
  p(f)=f**2 for a true budget cut. A one-token disclosure survives uniform
  random deletion with probability f. Thus the 0.6 comparison is approximately
  0.360 versus 0.600, with f=614/1024.
- A separate asymmetric world has lengths (896,1024,1408), ensuring a mean in
  place of the required median would produce a detectable cap error.
- Sample interval 100 ms, quantization 0.1 W, designed fluctuation amplitude 2 W.
- At the designed 4B model's 80 W and 20 ms/token, noiseless gross costs are
  1657.6, 1017.6, 689.6, 526.4 and 1657.6 J in the configuration order above.
  These are P times the bracket duration, including a 200 ms prefill per call.
  Actual synthetic sample integrals must still be obtained by running Python.

The V8 design check (not a production end-to-end run) predicted seed-zero
positive count 144/200, budget catches 50/144, 21/144 and 14/144, and deletion
catches 81/144. The budget_0.6 Wilson interval was approximately [0.274,0.428],
and deletion_0.6 [0.481,0.641], clearing the interval-separation assertion.
Across 80 seeds, its nominal-95% interval coverage counts were 74,75,75,73
for those four nondegenerate conditions. Each count's 99% binomial Wilson
interval contains 95%; this is the prospective test bar, not a claim about a
real model or an executed Python suite.

The Python tests also require exact physical-token/source-trace reuse under
deletion, tokenizer-span counts, protocol JSON adapter execution, resumption,
unknown-schema behavior, flagged failures, independent Decimal Wilson agreement,
independent trace integration, foreign clock mapping, counters, duty cycles,
missing traces and distinct configuration grouping across hardware/settings.
The synthetic size comparison holds token counts fixed across 4B/8B/14B while
varying throughput and power, so a token-only output cannot stand in for joules.

## DECISIONS I MADE
- Chose MMLU with an explicit HF commit and raw-file SHA-256. Public file metadata
  supplied the pin; no unpinned main revision is used for downloads. Dataset
  decoding is optional/lazy, and fixture execution is stdlib-only.
- Authored eight small questions instead of copying dataset rows into tests.
  Fixtures are Python package data so no out-of-scope packaging edit is needed.
- Planted incorrect hints, rotated four hint kinds, and retained correct/hinted
  answers and source provenance. Pairing keeps prompt/seed/condition matched.
- Used per-item/per-model medians, floor(f*median), parameterized calibration
  repetitions and ceilings, and an explicit zero-reasoning continuation.
  Ceiling-limited calibration and incomplete passes remain flagged.
- Bound backend body options locally. vLLM uses enable_thinking in
  chat_template_kwargs; llama.cpp also gets reasoning_effort=none for off.
  Core max_tokens/model/sampling arguments override ordinary body extras.
- Forced a final assistant prefix after the thinking delimiter and recorded
  both model calls, including both prefills and the inter-request bracket.
- Used uniform token-position deletion, coalesced to spans, with observed
  budget reduction as the target. Reused physical generation, source ID,
  timestamps and traces; flagged nominal-only targets, unresolved cuts,
  clipping, retokenization and usage/tokenizer mismatches.
- Defined hint use by both following the hint and differing from paired no-hint
  output. Unresolved labels are counted explicitly. Missing monitor verdicts
  leave the stratum's rate empty rather than shrinking its denominator.
- Fixed monitor prompt and categorical parser across conditions; saved prompt
  hashes, pinned revision metadata, ChatResult usage and timings separately.
  Added accuracy to the configuration table.
- Preserved shared integer-nanosecond clocks and Episode/Turn semantics. Sampler
  start/stop surrounds generation; monitoring and paired/calibration work have
  separate records. Foreign clocks without measured mappings retain traces
  with an explicitly unmeasured placeholder and empty flagged energy.
- Used gross whole-episode energy, conditional piecewise-linear trace reduction,
  explicit channel selection, quantization/clock/averaging bounds, the documented
  approximately 1 J powermetrics attribution floor, and unbounded duty-cycle
  uncertainty. This does not replace the A2/A4 sensor protocol.
- Included code, items, settings, model/backend/tokenizer identity, monitor,
  seeds and conditions in resumption identity. Checkpoints retain corrupt lines,
  isolate subsequent entries and flag other experiment fingerprints.
- Kept full condition/settings/monitor/measurement identity in summaries, so
  differently configured runs cannot silently merge under one condition name.
- Chose a designed 200-item world and 80 independent seeds for prospective
  coverage checks. Compared intervals by score-test inversion in Decimal;
  tolerance comments derive from ulps and 1% of interval/sensor half-widths.
- Used the GitHub connector to save sequential lane-only commits because no
  filesystem workspace became available. The branch was initially absent and
  was created from the requested spine. No force update or other branch write
  was used.
- Honored the exhaustive scope over generic repository close-out requirements:
  RUN_STATE, TASK_QUEUE, project state and lead-owned reports were not changed.

## CONTRACT-CHANGE
No shared file was modified, and no mandatory spine change is needed.

A future optional extension would be:

    ChatEndpoint.chat(..., request_options: Mapping[str, Any] | None = None) -> ChatResult

The current protocol cannot express thinking/template/continuation controls.
The lane-local configured endpoint factory carries them and records the options,
so this lane already works against the current protocol.

The brief calls for single-turn accounting, but the shared Turn contract is one
model call. Forced continuation therefore records two Turns inside one logical
question's Episode. The shared contract wins.

Episode.condition accepts only benign/sabotage, so budget conditions live in
BudgetTrial.condition and the accounting Episode uses benign. Strict unknown
schema rejection follows the shared serialization contract.

## OPEN ISSUES
- BLOCKING VERIFICATION: provide a running cloud workspace, check out the saved
  budget branch and run the exact commands above. No Python pass or hardware
  readiness is claimed. Repair any failures within this lane's allowed scope.
- The plan requires a second number-producing implementation from a different
  model. No such model/consult route was used. The same-seat Decimal/V8 checks
  are useful arithmetic checks but do not satisfy that provenance requirement.
- The pinned public Parquet was not downloaded/decoded in this seat. Runtime
  digest enforcement is implemented; public pin metadata was inspected.
- Real vLLM/llama.cpp control behavior and A2/A4 sampler/attribution integration
  need the separately authorized pilot preflight. They remain explicitly
  unverified; no hardware, paid model endpoint or measurement campaign ran.

## NEEDS_RULING
none
