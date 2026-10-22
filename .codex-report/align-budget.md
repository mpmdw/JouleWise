# Alignment budget lane — fix round 1

## SUMMARY
Continued lane/2026-10-21-align-budget from 58750718f; never restarted from spine.
Implemented sampler tail waiting, explicit CLI energy channels and linear reduction.
Added counter-edge enclosures and parameterized power-edge uncertainty.
Summaries retain partial rates/J, measured/missing counts and per-flag trial counts.
Replaced token shredding with recorded contiguous spans and a 13-token disclosure.
Separated seed rows and added seeded subject-stratified rosters with fingerprint metadata.
Added streamed, content-addressed trace storage and ordinary-Episode hydration readers.
The source now contains 37 test methods, including 12 review regressions.
VERIFICATION BLOCKED: the executor remained starting/offline; zero Python tests ran.
Changes were saved by sequential fast-forward GitHub commits; protected contracts are unchanged.

## FILES
Changed this round:
- joulewise/align/budget/conditions.py: recorded deletion_span_count; contiguous-span
  and explicit legacy-token deletion; nullable serving fields; finish reasons.
- joulewise/align/budget/score.py: first YES/NO-token parsing, truncated-verdict flag,
  configurable monitor token ceiling including its reasoning.
- joulewise/align/budget/energy.py: O(n) integration; counter edge enclosures;
  prospective power envelope; jitter-aware gap diagnostic; structured sampler flags.
- joulewise/align/budget/items.py: subject preservation, equal-allocation seeded
  stratified_roster and selected-row/seed/allocation metadata.
- joulewise/align/budget/run.py: tail waiting outside Episode brackets, continuation
  fallback, partial summaries/counts, one row per seed, exclusion counts for
  uncalibrated budget trials, fingerprint metadata and streamed checkpoint reads.
- joulewise/align/budget/synthetic.py: intact 13-token disclosure, a sampler with
  positive acquisition jitter and no closing sample, exact design-survival formula,
  optional conditions keyword for sensitivity runs.
- joulewise/align/budget/storage.py: streaming JSON and content-addressed trace
  sidecars; checkpoint support; hydrated result/Episode readers.
- joulewise/align/budget/__main__.py: explicit energy reducer config, stratified
  roster, compact streamed exports and nonzero total-failure exit.
- tests/align/test_budget.py: existing independent-seed coverage retained; independent
  integrator clips to the actual Episode rather than counting the new sampler tail;
  disclosure assertions now require the complete sentence; coverage bar justified.
- tests/align/test_budget_review.py: 12 review regression methods covering jittered
  sampling at both intervals, partial evidence, parser/truncation, edge physics,
  deletion sensitivities, clustered seeds, the subject roster, missing calibration,
  nullable responses, continuation fallback, compact storage/resume and CLI behavior.
- docs/align/budget_pilot.md: revised provisional internal protocol, controls,
  sensor limits, flag counts, storage/readers and frontier kill condition.
- .codex-report/align-budget.md: current report and finding dispositions.

Inherited fixture.py and __init__.py remain unchanged. No registry exception was
used. No NVML-lane file, protected contract, repository status file or other
out-of-scope path was modified. The appendix scripts could not be written to
/workspace/JouleWise/.review1 because no filesystem command could launch; they
are not committed or silently reconstructed elsewhere.

## PUBLIC API
Existing reviewer names and positional call shapes are retained. Principal APIs:

    HintItem(..., provenance="authored-fixture", flags=(), subject="unspecified")
    ItemBatch(items, flags=(), metadata={})
    ItemSource.load() -> ItemBatch
    HubMMLUSource(timeout_s, pin=<existing pinned MMLU bytes>, seed=0,
                  fetch=_download).load() -> ItemBatch
    hint_suite(rows, *, seed=0, provenance="authored-fixture") -> ItemBatch
    stratified_roster(batch: ItemBatch, count: int | None, *, seed: int = 0) -> ItemBatch

    Condition(name, mode="on", fraction=None, concise_prompt=CONCISE_PROMPT,
              deletion_span_count: int | None = 4)
    delete_spans(text, *, remove_tokens, codec, seed, span_count: int | None = 4) -> Deletion
    cap_tokens(median_tokens, fraction) -> int
    LocalEndpoint.chat(messages, *, tools=(), max_tokens, temperature, seed) -> ChatResult

    HintMonitor(endpoint, model="openai/gpt-oss-20b", max_tokens=2048, seed=0,
                revision="unspecified")
    HintMonitor.assess(item, reasoning, *, visibility="full") -> MonitorAssessment
    judge_hint_use(item, answer_text, paired_text) -> HintUse
    parse_answer(text, labels) -> str | None
    wilson(successes, trials, *, confidence=0.95) -> Rate
    episode_energy(episode, *, channels=None, power_max_w=None, gap_factor=1.5) -> Energy

    Settings(max_tokens, answer_max_tokens, calibration_repetitions=3,
             temperature=0.6, confidence=0.95, thinking_open="<think>",
             thinking_end="\n</think>\n", measurement_id="unmeasured",
             sampler_tail_intervals=2.0, sampler_interval_ns=100000000,
             power_max_w=None)
    run_matrix(items, models, conditions, *, seeds, settings, monitor,
               checkpoint=None, sampler_factory=None, clock=time.monotonic_ns,
               run_metadata=None) -> MatrixResult
    summarize(trials, *, confidence=0.95, energy_reducer=episode_energy) -> tuple[Summary, ...]
    summary_table(rows) -> str

    write_result(path: Path, result: MatrixResult) -> None
    read_result(path: Path) -> MatrixResult
    write_episode_views(path: Path, episodes: Iterable[Episode], *,
                        trace_file="result.traces.jsonl") -> None
    read_episode_views(path: Path) -> Iterator[Episode]
    read_trial_episode(path: Path, trial_id: str) -> Episode

    run_synthetic(*, count=200, seeds=(0,), with_power=True, sizes_b=(4.0,),
                  checkpoint=None, conditions=FIVE_CONFIGURATIONS) -> MatrixResult
    deletion_survival_probability(total, removed, phrase_length, span_count=4) -> float
    main(argv=None) -> int

BudgetTrial, ModelSpec, Generation, Calibration, Rate, ScriptedModel.chat,
ScriptedMonitor, ScriptedSampler, SyntheticClock, WordCodec and synthetic.HintMonitor
remain available with compatible existing calls. BudgetTrial's existing Episode
and serialization conventions are retained in memory. New Condition/Settings
fields carry the span and sampler parameters into trial records.

Summary adds seed, flag_counts, missing_monitor_verdicts, missing_energies,
measured_trials, excluded_trials and configuration. Existing catch_rate,
false_flag_rate, mean_joules, mean_reasoning_tokens and flags remain available.
MatrixResult adds metadata containing the roster and requested analysis settings.

On disk, result/Episode views and checkpoints reference SHA-256-addressed
PowerTrace records in sibling JSONL sidecars. Use the hydration readers above
before passing an exported Episode to another lane. Shared records.to_json(trial)
still deliberately produces a fully materialized legacy compatibility view.

## TESTS RUN
**Current-head Python tests executed: 0. Runtime pass/failure/skip counts: unknown.**
Source inventory: 25 inherited methods plus 12 new methods = 37. One inherited
method is guarded by skipUnless(pyarrow importable); no current-head skip actually
occurred because Python never launched.

Repeated attempts at the following exact command from /workspace/JouleWise were
rejected before shell/process creation:

    python3 -m unittest discover -s tests/align -t .

The same execution-tool error also blocked pwd and git status --short --branch:

    No usable execution environment is available. Wait for an environment to become available before using this tool.

wait_for_environment was started at intake and repeatedly awaited while work
continued through the connector. environment_status continued to report
observed_phase=starting, connectivity=offline, failure=null. Thus local checkout,
fetch, compiler/import checks, git diff --check, fixture census, the appendix
scripts and the extra-dependency installation could not run. No network call was
made by a test. No full repository suite was requested or run.

The reviewer's baseline is external evidence supplied in the brief, not a run
by this seat: at 58750718f, Python 3.13 ran 25 tests, OK, one pyarrow skip, in 35 s.

Commands still required once the executor exists (do not substitute the inventory
above for their real results):

    git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-budget
    git -C /workspace/JouleWise checkout -B lane/2026-10-21-align-budget origin/lane/2026-10-21-align-budget
    python3 -m unittest discover -s tests/align -t .
    python3 -m unittest tests.align.test_budget_review -v
    git diff --check

Write the provided appendix verbatim to .review1 first, then:

    git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-nvml:refs/remotes/origin/lane/2026-10-21-align-nvml
    sh /workspace/JouleWise/.review1/build_combined.sh /tmp/budget-combined
    python3 -I /workspace/JouleWise/.review1/world_nvml_integration.py /tmp/budget-combined 100000000
    python3 -I /workspace/JouleWise/.review1/world_nvml_integration.py /tmp/budget-combined 10000000
    python3 -I /workspace/JouleWise/.review1/world_summary_refusals.py
    python3 -I /workspace/JouleWise/.review1/world_edges.py
    python3 -I /workspace/JouleWise/.review1/world_edge_interpolation.py
    python3 -I /workspace/JouleWise/.review1/world_deletion_spans.py
    python3 -I /workspace/JouleWise/.review1/world_seed_pooling.py 60
    python3 -I /workspace/JouleWise/.review1/world_minor_checks.py /tmp/budget-combined
    python3 -I /workspace/JouleWise/.review1/world_record_size.py /tmp/budget-combined
    python3 -I /workspace/JouleWise/.review1/independent_counts.py

No script, world parameter or assertion was altered in a .review1 copy: no copy
could be created. The legacy size probe calls shared to_json(trial), which remains
a materialized view; it does not measure the new compact writer. The new storage
regression measures unique trace records in actual result/checkpoint sidecars,
round-trips the records, and resumes sampled trials without another model call.

No extra was installed. Both the ordinary and extra-dependent runs remain
required; even the synthetic 14042-row roster test could not execute:

    python3 -m venv /tmp/pa
    /tmp/pa/bin/pip install pyarrow
    /tmp/pa/bin/python -m unittest discover -s tests/align -t .
    /tmp/pa/bin/python -m unittest tests.align.test_budget.BudgetItemsTests.test_optional_parquet_uses_verified_bytes_offline -v
    mkdir -p /tmp/mmlu
    curl -sSL -o /tmp/mmlu/test.parquet https://huggingface.co/datasets/cais/mmlu/resolve/c30699e8356da336a370243923dbaf21066bb9fe/all/test-00000-of-00001.parquet
    /tmp/pa/bin/python -I /workspace/JouleWise/.review1/mmlu_roster.py /tmp/mmlu/test.parquet

Actual pinned-file CLI roster subject counts: NOT RUN. The authored synthetic
test expects 57 subjects, with 29 counts of four and 28 counts of three; this is
an allocation identity (200=29*4+28*3), not an observed roster. Real subject names,
selected row IDs and counts will be in result.metadata.roster.

Required explicit-channel CLI verification, not yet executed:
write a valid local/mock transport config with
energy={"channels":[["nvml_energy","gpu0:energy"]]}, then run

    python3 -m joulewise.align.budget --config /tmp/budget-counter.json --seeds 0 --output /tmp/budget-counter

The offline regression exercises CLI channel propagation using injected endpoints
and the real reducer/exporter. The exact external NVML CLI run still needs the
combined tree and a valid configured endpoint; no live endpoint was contacted.

Read-only checks actually completed through tools:
- Every saved changed source/doc file through code commit 63b8e31 was fetched
  back and matched the authored text; subsequent storage/test updates were saved.
- GitHub compare from 58750718f showed only allowed lane files.
- A V8 lexical scan found balanced strings/delimiters and no trailing whitespace
  in the ten changed Python source/test texts at that point. This is NOT a Python
  parser, import check, test run or second-model numerical implementation.
- Commits were sequential children of the previous lane head; branch updates
  used expected-head checks and force=false. No other branch was changed.

## END-TO-END
**Implemented but not executed in this round. No new measured counts/J/runtime
are claimed.**

The actual production chain remains:
authored/pinned items -> per-item uncapped calibration -> hinted/no-hint calls ->
forced continuation -> optional post-hoc contiguous deletion -> fixed local
ChatEndpoint monitor -> BudgetTrial/shared Episode -> summary -> energy reducer.

The five-configuration 200-item world remains thinking_on, budget_0.6,
budget_0.4, budget_0.3 and deletion_0.6. It now uses a complete 13-token disclosure
and the positive-jitter/no-closing-sample sampler, so missing tail waiting,
token shredding and fragment-only monitoring are detectable on the real path.
Budgets still floor 1024-token medians to 614/409/307. The pre-existing independent
80-seed coverage test remains and uses the exact new span-survival probability.
A separate 60-world test reproduces item-clustered draws for seeds (0,) and
(0,1,2), prints each coverage count and demands >=53/60. Binomial(60,.95) gives
P(<=52)=.0098, the review's derived one-in-100 false-failure bar.

Additional real-path tests run five configurations x 200 items under legacy
token deletion, one contiguous span and four contiguous spans, including both
deletion_0.6 and deletion_0.3; they print numerator, denominator, rate and Wilson
interval for each reading. A 2000-transcript world independently contrasts the
intact sentence under those readings and requires interval separation.
A six-item/two-condition world exercises bracketing at 100 ms and 10 ms polling,
with a fixed +10 ms acquisition delay, and a zero-tail negative control.

Analytical design probabilities only (not production-run catch measurements):
- deletion_0.6: legacy token deletion 0.00123015; one span 0.583255; four spans
  0.549668. Budget disclosure probability is (614/1024)^2 = 0.359531.
- deletion_0.3: legacy 0.000000131900; one span 0.280145; four spans 0.248462.
- These follow combinatorial counts of intact windows, not fitted thresholds.

Delta re-review ledger; new measured deltas are blocked by the executor:
- B1: reviewer 0/12 measurable at each interval -> new result NOT RUN. The
  explicit counter channel now reaches the CLI reducer; no automatic channel
  default was added.
- B2: reviewer one malformed verdict blanked budget_0.6 catch, and one missing
  trace blanked J despite 199 measured trials (reviewer mean 1017.774 J) ->
  new result NOT RUN. The new denominators explicitly retain scored/available
  trials and counts. Punctuation alone is now scored; a genuinely empty reply
  is covered separately.
- M1: reviewer power 4995 +/-0.010 J and counter 4990 +/-0.001 J against truth
  5000 J -> new execution NOT RUN. Algebraically, the counter's two 15 J edge
  enclosures give 30.001 J; a prospective 250 W envelope gives a power width
  25.010 J. Without any power envelope, the honest bound is unbounded, with
  energy_power_max_missing; the finite J estimate is still retained.
- M2: reviewer default shredded the sentence (2/2000 intact) versus its four-span
  comparison (1095/2000) -> new measured outcomes NOT RUN. Both requested
  fractions/readings are printed by the new sensitivity regression.
- M3: reviewer pooled coverage approximately 48/60 vs single-seed 57/60 ->
  new coverage NOT RUN. Each seed now has a separate Wilson row.
- M4: reviewer first 200 rows had only two subjects (100 each) -> new roster NOT
  RUN. Equal allocation across 57 nonempty subjects gives the prospective
  29*4 + 28*3 composition; no outcome filtering is used.
- m4 runtime: reviewer 0.80/2.22/8.74 s at 6100/11000/21000 samples -> new
  runtimes NOT RUN. The code now scans once plus two binary searches; there
  is no wall-clock assertion.
- m6 bytes: reviewer estimated about 960 bytes/sample/trial in the materialized
  view -> actual compact-file byte sizes NOT RUN. The sidecar regression checks
  uniqueness across all physical generations and deletion reuse. Shared
  to_json(trial) intentionally retains its previous representation.

The lane's own five-by-200 before/after numerical summary and all measured
sensitivity tables remain required. The supplied independent_counts.py predicts
144 hint-using trials and budget catches 50/144, 21/144, 14/144
for the unchanged scripted draws, as stated in the previous seat report; these are inherited design evidence,
not this seat's production execution. The new deletion counts and sensor integrals
must be printed by Python, not substituted with arithmetic sketches.

## DECISIONS I MADE
- Continued the supplied lane head. Used the installed GitHub connector when
  local execution never became available; saved each meaningful step with a
  fast-forward update on the authorized branch only.
- Kept the three protected shared contracts unchanged. Forced questions retain
  two Turns because Turn means one model call; budget conditions remain local
  while Episode.condition is benign, as the shared contract requires.
- B1: wait two exposed poll intervals outside the call bracket, configurable
  and recorded, with a recorded fallback interval for protocol-only samplers.
  This allows one next poll and one acquisition period; extraordinary delays
  are still flagged rather than manufacturing a closing sample.
- B1: require explicit (source, channel) selection when multiple traces exist;
  no default channel was added. CLI energy options enter metadata/fingerprint.
- B2: report rates over scored labels/verdicts and mean J over available traces;
  count missing evidence and every Episode/structured trace flag per trial.
  Empty denominators remain empty. No nonphysical imperfection blanks good data.
- M1: use counter increments around edges, not an average-power surrogate, for
  counter edge bounds. For power require a prospective envelope from operator
  settings/config or sampler notes; never equate observed peak to physical
  maximum. Missing maximum is an unbounded transient Energy half-width and flag;
  summaries export an unknown bound, preserving finite JSON and J.
- M1: explicitly condition power integration on a piecewise-linear interior and
  distinguish interpolation/quantization bounds from sensor accuracy or a
  confidence interval on the mean. Duty-cycle uncertainty remains unresolved.
- M2: provisionally choose four nonoverlapping contiguous spans with uniformly
  composed positive lengths and uniformly selected distinct kept-token gaps.
  Store requested count in Condition/configuration and actual spans in the trial.
  Keep span_count=None as the explicit old token-level sensitivity control.
- M2: replace the one-token marker with a full 13-token disclosure; the monitor
  requires the intact phrase. Its survival formula counts valid retained windows.
- M3: print one row per seed rather than introduce a bootstrap tuning parameter.
  This is explicitly allowed by the review and avoids pooled-item independence.
- M4: equal subject allocation, seeded subject/row order, selected row IDs and
  roster seed in metadata and fingerprint. The raw pinned-file order is unchanged.
- m1: keep uncalibrated generation records, exclude them from budget numbers,
  and print excluded_trials plus budget_uncalibrated_excluded counts.
- m2/m5: validate required config keys before fetching; exit nonzero on total
  failure; treat nullable serving fields as absent; flag tagless-answer fallback.
- m3: 1.5 intervals is the midpoint between one poll and a missed poll near two.
  It allows the observed +9/+10 ms acquisition jitter at 100 ms; it is also
  configurable. The sample-gap diagnostic does not refuse energy.
- m4: interpolate only the two bracket edges by bisect, walk interior samples
  directly, and keep runtime evidence out of wall-clock assertions.
- m6: keep full in-memory Episodes and the shared JSON compatibility API, but
  persist traces once in a content-addressed sidecar. Stream JSON output and
  checkpoint input. Hydrate ordinary Episodes through lane-local readers.
- Monitor max_tokens=2048 is explicitly an operator ceiling, not a derived
  guarantee; include reasoning in that budget and preflight truncation. The
  default is recorded, as are synthetic 0.75 hint use, 0.05 false markers and
  0.5 concise fraction, which are design inputs rather than empirical bars.
- Coverage's secondary 99% interval uses the review's one-in-100 false-failure
  convention; across four conditions the union bound is at most four percent.
  The original independent-seed check was retained, alongside clustered seeds.
- No real hardware, paid endpoint, credentials, external messages or whole
  repository test suite was used.

## CONTRACT-CHANGE
none required. Local configured endpoints still carry template/continuation
options outside the shared ChatEndpoint signature. PowerTrace has no flags field,
so the local adapter reads structured JSON notes.flags. Compact disk exports are
read through lane-local hydration functions; their resulting Episodes satisfy
the unchanged shared contract.

## FIX LOG
- B1 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; jittered end-to-end regressions in ed4fb030ddfad86946db72e0eff9c9ec44ede10c.
- B2 — fixed (not run), 819b397719a804fc1abbf71b3b9f6a0610120aa1 and 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; genuine missing-verdict/partial-J regressions in ed4fb030ddfad86946db72e0eff9c9ec44ede10c.
- M1 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9 and ed4fb030ddfad86946db72e0eff9c9ec44ede10c; missing Pmax is honestly unbounded.
- M2 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; both-fraction sensitivity regressions in ed4fb030ddfad86946db72e0eff9c9ec44ede10c.
- M3 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; item-clustered 60-world regression in ed4fb030ddfad86946db72e0eff9c9ec44ede10c.
- M4 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; 14042-row/57-subject regression in ed4fb030ddfad86946db72e0eff9c9ec44ede10c.
- m1 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9.
- m2 — fixed (not run), 819b397719a804fc1abbf71b3b9f6a0610120aa1; early required-key validation in 63b8e31a088cd59ad35d9fa055366ad934fe20e2.
- m3 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9.
- m4 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9.
- m5 — fixed (not run), 819b397719a804fc1abbf71b3b9f6a0610120aa1 and 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; continuation regression in ed4fb030ddfad86946db72e0eff9c9ec44ede10c.
- m6 — fixed (not run), ed4fb030ddfad86946db72e0eff9c9ec44ede10c and e3d4416b2d4ea29e0be29ea0defac4b49c59a87a; compact disk format deduplicates traces; shared to_json remains the materialized compatibility view.
- owner supply/flag propagation — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; per-trial battery/cap/throttle counts covered in ed4fb030ddfad86946db72e0eff9c9ec44ede10c.

## OPEN ISSUES
- BLOCKING: provide a usable executor and run every current-head command above.
  No Python syntax/import validity, test pass, coverage, runtime, compact byte
  size, real roster or measured numerical delta is claimed.
- The .review1 files, combined NVML scratch tree and optional pyarrow environment
  could not be created. They must be prepared exactly from the brief.
- M6's existing size script measures the retained legacy materialization API.
  Run it unchanged as requested, but also measure actual streamed result and
  trace-sidecar bytes; the new regression checks that each trace is persisted
  once. Its legacy copy-count display is expected to remain unchanged.
- Unknown Pmax keeps power uncertainty unbounded. Select a prospective instrument
  envelope before any finite-uncertainty joule-frontier claim; the counter path
  does not need that assumption for its bracket-edge enclosure.
- Sampler tail waiting assumes acquisition/scheduling fits the recorded tail
  allowance. Actual bracketing is checked by the reducer; preflight must tune
  the parameter for extraordinary acquisition latency.
- No different-model number-producing implementation was executed. The reviewer's
  supplied worlds are retained as references; the same-seat combinatorial and
  Decimal checks do not establish different-model provenance.
- Real vLLM/llama.cpp controls, monitor ceiling and paid hardware remain subject
  to the separately authorized pilot preflight.

## NEEDS_RULING
These choices are provisional, do not block building, and change printed results.
Measured sensitivity outcomes are NOT AVAILABLE because the executor never ran.

1. M2 default spans: legacy token-level, one span, or four spans (chosen).
   The new test prints both deletion_0.6 and deletion_0.3 for all three.
   Analytical probabilities, respectively:
   0.6 -> 0.00123015 / 0.583255 / 0.549668;
   0.3 -> 0.000000131900 / 0.280145 / 0.248462.
   These are design probabilities, not empirical catch rates. Run the regression
   before adjudicating the printed rates.
2. M4 allocation: equal across subjects (chosen) or proportional to subject size.
   Prior first-N outcome from the reviewer: 100 abstract_algebra +100 anatomy.
   Equal's prospective count identity: 29 subjects x4, 28 x3, all 57.
   Actual pinned-file roster counts/IDs and proportional comparisons remain
   unmeasured; no fabricated counts are supplied.
3. M1 power envelope: retain an unknown/unbounded power bound when no prospective
   maximum is available (chosen), versus supply a measured/declared physical
   maximum as a recorded parameter. On the supplied step-world algebra,
   missing maximum -> unbounded, 250 W -> 25.010 J half-width, while counter
   half-width ->30.001 J. No 250 W default or observed-peak assumption was added.
   The kill condition is inconclusive with an unresolved power bound.

No B1 default-channel ruling is needed: the harness still requires explicit
selection, as the reviewer requested for the CLI.
