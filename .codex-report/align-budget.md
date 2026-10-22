# Alignment budget lane — fix1c continuation

## SUMMARY
Continued lane/2026-10-21-align-budget from pushed head 0480271fa.
Fixed the 10 ms gap diagnostic by measuring completed sampling cycles, including acquisition.
Kept cadence selection and energy reduction linear in sample count.
Preserved the five-by-200 world and its rate checks; moved interval separation to 2000 items.
Decorrelated disclosure-position and deletion seeds in the 4000-transcript sensitivity test.
Empty/excluded budget rows now leave all four token means empty.
Retained the earlier fixes, compact storage, explicit channels and counted sampler flags.
All source/doc changes are pushed; the three protected contracts are unchanged.
Current-head execution is blocked: the managed executor never became usable.
The lead's measured 0480271fa evidence is recorded below, separately from this seat's zero runs.

## FILES
Changed in fix1c:
- joulewise/align/budget/energy.py: median observed acquisition cadence, derived
  missed-cycle bar, linear-time median selection and existing linear integration.
- joulewise/align/budget/run.py: optional token means and empty table cells when n=0.
- tests/align/test_budget.py: retains five configurations x 200 items; checks
  scripted probabilities against Wilson intervals and resolves the unchanged
  interval-separation assertion on an additional 2000-item world.
- tests/align/test_budget_review.py: independent position/deletion streams over
  4000 transcripts, missing-poll negative controls at both intervals, empty means.
- docs/align/budget_pilot.md: revised cadence physics and test-world interpretation.
- .codex-report/align-budget.md: current handoff, lead evidence and fix dispositions.

Inherited lane files:
- joulewise/align/budget/items.py: authored/pluggable items, pinned verified MMLU
  loading, subject preservation and seeded equal-allocation stratified rosters.
- joulewise/align/budget/conditions.py: thinking controls, budget caps, recorded
  contiguous deletion spans, tokenizer and nullable local serving adapter.
- joulewise/align/budget/score.py: paired hint-use judgment, robust first YES/NO
  parsing, missing/truncated monitor flags and Wilson intervals.
- joulewise/align/budget/synthetic.py: scripted model/monitor, thirteen-token
  disclosure, jittered sampler without a closing sample, survival probabilities.
- joulewise/align/budget/storage.py: streamed result/checkpoint I/O, unique
  content-addressed trace sidecars and ordinary-Episode hydration readers.
- joulewise/align/budget/__main__.py: CLI, explicit energy channel configuration,
  roster metadata/fingerprint, compact exports and nonzero failure status.
- joulewise/align/budget/fixture.py: authored multiple-choice fixture.
- joulewise/align/budget/__init__.py: package entry.

No registry exception was used. No NVML-lane file was copied or edited.
No shared contract, repository status file or other out-of-scope path was changed.
The appendix files could not be written to /workspace/JouleWise/.review1:
no filesystem process could launch. Nothing under .review1 is committed.

## PUBLIC API
Existing reviewer names and positional call shapes remain available.

    HintItem(..., provenance="authored-fixture", flags=(), subject="unspecified")
    ItemBatch(items, flags=(), metadata={})
    ItemSource.load() -> ItemBatch
    HubMMLUSource(timeout_s, pin=<pinned MMLU bytes>, seed=0, fetch=_download).load() -> ItemBatch
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

BudgetTrial retains its shared Episode and recorded Condition/Settings, including
span count. ModelSpec, Generation, Calibration, Rate, ScriptedModel.chat,
ScriptedMonitor, ScriptedSampler, SyntheticClock, WordCodec and synthetic.HintMonitor
retain their existing call shapes.

Summary retains condition, catch_rate, false_flag_rate, mean_joules, flags,
seed, flag_counts, missing_monitor_verdicts, missing_energies, measured_trials,
excluded_trials and configuration. Its four mean_*tokens fields are now
float | None: an empty group has no measured mean. Rate keeps estimate,
successes, trials and interval. MatrixResult.metadata carries roster and analysis
settings into the fingerprint.

Disk result/Episode/checkpoint views reference unique SHA-256-addressed
PowerTrace records in sibling JSONL sidecars. Hydration readers above return
ordinary shared Episodes for attribution. Shared records.to_json(trial) remains
the fully materialized compatibility view; it intentionally is not the compact writer.

## TESTS RUN
Current-head Python tests executed by this seat: 0.
Current-head pass/failure/skip counts: unavailable; the interpreter never launched.
Source inventory remains 37 test methods (25 inherited + 12 review regressions).
The pyarrow decoder remains guarded by skipUnless; no current-head skip occurred.

These exact commands were submitted from /workspace/JouleWise and rejected
before shell/process creation:

    python3 -m unittest discover -s tests/align -t .
    python3 -m unittest discover -s tests/align -t . -p 'test_budget*.py'
    python3 scripts/fixture_orphan_census.py --fail-on-orphans

The execution tool also rejected python3 --version and
git -C /workspace/JouleWise status --short --branch with:

    No usable execution environment is available. Wait for an environment to become available before using this tool.

wait_for_environment was started twice and repeatedly awaited. The supported
status tool alternated pending/starting, connectivity=offline, failure=null.
No usable filesystem or Python process was obtained. No package was installed,
no appendix script was created or executed, and no whole-repository suite ran.

External evidence from the lead's run at 0480271fa (Python 3.13), supplied in the
continuation brief; these are NOT this seat's runs:

- python3 -m unittest discover -s tests/align -t . -p 'test_budget*.py':
  37 tests, 2 failures, 1 skip (pyarrow absent). Failures were the marginal
  Wilson separation assertion and the 10 ms acquisition/gap diagnostic.
- With pyarrow installed, the optional decoder test passed.
- Every appendix probe ran; measured outcomes are in END-TO-END.
- Real pinned-file count=200 CLI roster: all 57 subjects, 29 with four items
  and 28 with three; roster_seed=0, allocation and 200 selected IDs recorded.
  The individual subject-name/count map was not supplied; it cannot be
  reconstructed honestly without loading the pinned bytes.
- The supplied three-size synthetic CLI smoke wrote result.json 62.4 MB,
  result.traces.jsonl 48.7 MB (6600 unique traces), checkpoint 63.0 MB and
  checkpoint trace sidecar 48.7 MB.

Commands required on a usable executor (all paths and world parameters unchanged):

    git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-budget
    git -C /workspace/JouleWise checkout -B lane/2026-10-21-align-budget origin/lane/2026-10-21-align-budget
    python3 -m unittest discover -s tests/align -t .
    python3 -m unittest discover -s tests/align -t . -p 'test_budget*.py'
    git diff --check
    python3 scripts/fixture_orphan_census.py --fail-on-orphans

Write every appendix script verbatim under .review1 (including build_combined.sh,
mmlu_roster.py and independent_counts.py), then run:

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

CLI failure repro (must exit nonzero):

    mkdir -p /tmp/x
    echo '{"models": []}' > /tmp/x/bad.json
    python3 -I -c "import sys; sys.path.insert(0,'/workspace/JouleWise'); from joulewise.align.budget.__main__ import main; sys.exit(main(sys.argv[1:]))" --config /tmp/x/bad.json --output /tmp/x/out
    echo $?

Extra-dependency and roster commands, not run by this seat:

    python3 -m venv /tmp/pa
    /tmp/pa/bin/pip install pyarrow
    /tmp/pa/bin/python -m unittest discover -s tests/align -t .
    /tmp/pa/bin/python -m unittest tests.align.test_budget.BudgetItemsTests.test_optional_parquet_uses_verified_bytes_offline -v
    mkdir -p /tmp/mmlu
    curl -sSL -o /tmp/mmlu/test.parquet https://huggingface.co/datasets/cais/mmlu/resolve/c30699e8356da336a370243923dbaf21066bb9fe/all/test-00000-of-00001.parquet
    /tmp/pa/bin/python -I /workspace/JouleWise/.review1/mmlu_roster.py /tmp/mmlu/test.parquet

After loading those bytes, also print Counter(i.subject for i in
stratified_roster(batch, 200, seed=0).items); the appendix prints raw first-N order,
which is intentionally unchanged.

Explicit-channel CLI verification remains pending. The existing offline CLI
regression injects a sampled matrix and checks propagation of energy.channels
through the real reducer/writer; it was not run at this head. A production-shaped
mock-config run with energy={"channels":[["nvml_energy","gpu0:energy"]]} must be
recorded when execution exists. No live endpoint or hardware was contacted.

Read-only verification actually completed:
- Fetched all five fix1c source/test/doc files back from 93eed44a and checked
  exact text identity against the saved edits.
- GitHub compare 0480271fa...93eed44a reports ahead_by=6, behind_by=0,
  only the five allowed source/test/doc paths, before this report update.
- Source inventory remains 37 methods. This is not a Python parse or test result.
- Updates used the contents API on the named lane branch with current blob SHAs;
  every write created a descendant commit. No force push or other-branch write.

## END-TO-END
No current-head world ran in this seat. The following measured numbers are
explicitly the lead's observations at 0480271fa from the continuation brief.

The real production chain is authored/pinned items -> per-item calibration ->
paired hinted/no-hint model calls -> forced continuation -> optional post-hoc
deletion -> fixed ChatEndpoint monitor -> BudgetTrial/shared Episode ->
summaries -> selected-channel energy reduction -> compact export.

Five configurations x 200 items, seed 0, scripted 1024-token reasoning:
- 144 hint-using and 56 non-hint-using trials.
- thinking_on catch 144/144; budget_0.6 50/144; budget_0.4 21/144;
  budget_0.3 14/144; deletion_0.6 69/144.
- False flags 3/56 except deletion_0.6 2/56.
- Caps 614/409/307; disclosure probability on positives p(f)=f^2.
- Default deletion's observed 69/144=0.4792 has Wilson lower 0.3991789623;
  budget_0.6's upper is 0.4280371306. Their overlap explains the old
  assertion failure; it does not invalidate each interval's coverage.
- A single missing energy leaves budget_0.6 mean 1017.752 J over 199/200.
  Complete per-configuration J rows were not supplied and are not invented.

Fix1c preserves that five-by-200 world and explicitly checks each scripted
probability inside its Wilson interval. An additional three-configuration
2000-item world applies the original nonoverlapping-Wilson assertion.
With approximately 1500 positives, the sum of worst-case marginal 95% widths
is z/sqrt(1500), about 0.051, smaller than half the designed 0.190 catch gap.
Its actual counts, intervals, runtimes and J remain unexecuted.

Delta re-review ledger (58750718f -> lead's 0480271fa, then fix1c intent):
- B1: explicit counter channel 0/12 ->12/12 measurable at both intervals.
  Lead's 100 ms summary: 12.923 +/-11.010 J and 15.947 +/-11.008 J;
  10 ms: 12.800 +/-1.750 J and 15.902 +/-1.513 J. Last samples follow
  Episode.end by 102–184 ms /14–29 ms respectively. Default multi-channel
  reduction still flags energy_channels_unspecified by design.
- B2: punctuation no longer blanks a row. Budget catches 50/21/14 of 144
  agree with independent_counts.py, with false flags 3/56. A genuinely empty
  verdict has separate regression coverage and uses remaining scored trials.
  One missing energy changed blank J to 1017.752 J over 199; versus the old
  reviewer's available-trial 1017.774 J, difference -0.022 J (jittered grid).
- M1: estimates remain power 4995 J (-5 J error), counter 4990 J (-10 J).
  Power half-width 0.010 J ->unknown/infinite without a supplied maximum;
  counter 0.001 J ->30.001 J, an increase of 30 J from edge enclosures.
  With the step world's prospective 250 W maximum, derived power width
  is 25.010 J; that is a parameterized sensitivity, not a default.
- M2: unchanged reviewer script gives 1224/2000=0.612 intact versus old
  2/2000=0.001, a +0.611 change. Its shared phrase/deletion seed is correlated.
  Lead's independently seeded 4000-transcript runs gave one span 0.5853,
  four spans 0.5545, matching design 0.5833/0.5497. The old lane test's
  shared-seed one-span count 479/2000 was misleading. Fix1c uses a separate
  position namespace and prints all readings; its new empirical counts are pending.
- M3: repeated-item coverage 48/60 ->57/60 (+9 covered worlds); single seed
  remains 57/60. Summaries split seeds rather than pool repeated items.
- M4: first-N count=200 roster had 2/57 subjects ->equal stratified 57/57
  (+55 subjects), 29 counts of four and 28 counts of three. Raw order unchanged.
- m1: uncalibrated budget trials no longer enter budget numbers; fix1c also
  changes the empty row's misleading 0.0 token means to None/blank.
- m2: invalid config prints pilot_error:ValueError and exits 1 (previously 0).
- m3: lead confirmed no false gap at 100 ms, but 12/12 false gaps at 10 ms.
  Fix1c compares to observed wait+acquisition cadence, with a retained test
  that removing an interior poll is flagged. Current-head counts are pending.
- m4: lead's 21000 samples reduce in 0.01 s versus original 8.74 s.
  The other two timing values were not supplied. Fix1c's cadence selection
  uses linear median-of-five selection, so sorting does not restore n log n
  work. There is no wall-clock assertion.
- m5: tool_calls=null returns content. Existing regression also covers
  cached_tokens=null and reasoning-only continuation fallback.
- m6: legacy to_json(trial) still displays three trace copies intentionally.
  Actual CLI disk files are 62.4+48.7=111.1 MB versus 150 MB (38.9 MB less);
  checkpoint plus sidecar 63.0+48.7=111.7 MB versus 151 MB (39.3 MB less).
  The sidecar has 6600 unique traces. These are lead-measured file sizes,
  not sizes of a current-head run.

The independent 80-seed coverage test and the 60-world item-clustered test
remain. The latter requires >=53/60: Binomial(60,.95) has P(<=52)=.0098.
The 4000-transcript test now separates position and deletion RNG streams.
Sensitivity runs print deletion_0.6 and deletion_0.3 under legacy tokens,
one span and four spans through the actual matrix/monitor/scoring path.
Those current-head output tables remain required.

## DECISIONS I MADE
- Continued the pushed lane, using the installed GitHub connector because no
  executor became usable. All changes are descendant commits on the authorized
  lane only. No extra plugin, paid endpoint or hardware operation was used.
- Fixed m3 using the median observed interval, bounded below by nominal wait:
  event.wait(T) followed by acquisition A produces cycle T+A. A missed cycle
  is near 2*(T+A); 1.5 is their midpoint. For scripted waits 10/100 ms plus
  10 ms acquisition, cycles are 20/110 ms and bars 30/165 ms respectively.
  This diagnostic assumes most polls completed normally. It never refuses J.
- Kept the reducer linear by deterministic median-of-five selection:
  T(n)<=T(n/5)+T(7n/10)+O(n). Five is an algorithmic grouping size, not a
  measurement threshold. Interior integration remains one pass with two edge searches.
- Preserved the five-by-200 world. Kept the original Wilson-separation bar
  on a 2000-item companion world rather than require nonoverlap from two
  uncertain marginal intervals on 144 positives. Added each scripted rate's
  own Wilson-coverage assertion on the original world.
- Independent position RNG namespace prevents correlated phrase/span placement.
  Increased that test's design roster to 4000 transcripts, matching the lead's
  sensitivity size; at p near one half the nominal 95% half-width is about 0.0155.
- Empty excluded strata carry no token mean; use None in records and blank cells.
  Exclusion counts/flags remain visible.
- Kept prior decisions: two configurable sampler-tail periods outside Episode;
  explicit channel selection for multiple traces; rates over scored trials and
  J over available trials; counted Episode/structured trace flags including
  battery discharge, power-cap and throttle conditions.
- Kept counter-edge increments as assumption-free edge enclosures. Power
  uncertainty needs a prospective envelope, never an observed sampled maximum.
  Missing envelope retains finite J and an unbounded/unknown uncertainty flag.
- Kept four provisional contiguous deletion spans and explicit legacy/one-span
  sensitivity controls, recorded in Condition, actual spans and configuration.
- Kept one Wilson row per generation seed and equal subject allocation with
  roster seed/row IDs/counts in the fingerprint.
- Kept null-field/final-reasoning fallbacks, nonzero total-failure status,
  streamed deduplicated sidecars and ordinary-Episode hydration readers.
- Monitor max_tokens=2048 and calibration_repetitions=3 remain recorded operator
  ceilings/design inputs, not precision guarantees. Synthetic probabilities
  0.75/0.05/0.5 are design inputs. Coverage's secondary 99% interval uses the
  review's one-in-100 false-failure convention.
- Shared Turn means one model call, so a forced question has two Turns;
  local budget conditions coexist with Episode.condition="benign" as required
  by the records contract. All three protected contracts remain untouched.

## CONTRACT-CHANGE
none. Local configured endpoints carry continuation/template options outside the
shared ChatEndpoint signature. PowerTrace lacks flags, so the adapter reads JSON
notes.flags. Lane-local hydration readers reconstruct shared Episodes from compact
disk records. Summary's optional means are lane-local, not shared-contract changes.

## FIX LOG
All lines retain "fixed (not run)" for the current head as required by the
executor-unavailable exception. Supplied lead evidence at 0480271fa is identified
separately above; it is not a current-head validation claim.

- B1 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; lead's baseline repro passes both intervals; current rerun blocked.
- B2 — fixed (not run), 819b397719a804fc1abbf71b3b9f6a0610120aa1 and 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; lead's baseline repro passes; missing-verdict regression retained.
- M1 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; lead's baseline repro passes, with missing-Pmax flag/unbounded width.
- M2 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; fix1c separation in 67b5b4179956e524338863af1561d1ad6c22d22c, independent position seeds in bcfb7cf2ad723dd15efa51333042b345e97b6716.
- M3 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; lead measured 57/60 coverage on both baseline lines.
- M4 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; lead's real-file baseline roster covers 57 subjects; full subject map pending.
- m1 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; empty means corrected in d51397ab6701e7625cba34357f9189fdaf8034d9, regression in bcfb7cf2ad723dd15efa51333042b345e97b6716.
- m2 — fixed (not run), 819b397719a804fc1abbf71b3b9f6a0610120aa1 and 63b8e31a088cd59ad35d9fa055366ad934fe20e2; lead measured nonzero baseline exit.
- m3 — fixed (not run), 36e6bfe7805bec4555dbd99d91dfcf1c8eb66001 and 93eed44a5a2b2aed69454aed1da624f6ad5a4570; positive/negative controls at both intervals in bcfb7cf2ad723dd15efa51333042b345e97b6716.
- m4 — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; lead measured 21000 samples in 0.01 s; linear cadence selection preserved in 93eed44a5a2b2aed69454aed1da624f6ad5a4570.
- m5 — fixed (not run), 819b397719a804fc1abbf71b3b9f6a0610120aa1 and 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; lead's null-field baseline repro passes; continuation regression retained.
- m6 — fixed (not run), ed4fb030ddfad86946db72e0eff9c9ec44ede10c and e3d4416b2d4ea29e0be29ea0defac4b49c59a87a; lead's actual compact sizes recorded above; legacy materialization stays compatible.
- owner supply/flag propagation — fixed (not run), 7f8e669c0ef9d4c0407e04b496f866ad982af8d9; per-trial battery/cap/throttle counts retained in ed4fb030ddfad86946db72e0eff9c9ec44ede10c.

## OPEN ISSUES
- BLOCKING verification: a usable executor is still required for current-head
  Python syntax/import checks, the full alignment suite, every unchanged appendix
  probe, actual sensitivity/count tables, explicit-channel CLI run and pyarrow run.
  No current-head pass or measured numerical result is claimed.
- .review1 files and /tmp/budget-combined could not be created because no shell
  could launch. Prepare them exactly from the brief; never import NVML into this
  lane's own tests or commit its source to this branch.
- Full named-subject roster counts and the proportional-allocation sensitivity
  still need execution, beyond the lead's supplied all-57 count distribution.
- m6's legacy size script still reports three copies in to_json(trial). Use
  write_result and its sidecar to measure persistent size; hydration is required
  to read compact Episode exports. Lead-measured totals are recorded above.
- Unknown prospective power maximum leaves a power frontier inconclusive;
  duty-cycle repetition and actual instrument uncertainty remain pilot preflight.
- Observed-median gap diagnosis cannot identify a sensor that uniformly loses
  polls, or a majority of missing cycles. Tail waiting assumes acquisition fits
  its recorded allowance; extraordinary latency still yields a bracket flag.
- Real model controls, monitor ceiling and hardware require separately
  authorized pilot preflight. Different-model arithmetic review remains the
  lead's supplied probes; this seat ran no independent Python implementation.

## NEEDS_RULING
Provisional choices retained; they do not block building.

1. M2 default deletion spans: legacy tokens /one contiguous span /four spans
   (chosen). Design survival at deletion_0.6 is
   0.00123015 /0.583255 /0.549668; at deletion_0.3 it is
   0.000000131900 /0.280145 /0.248462.
   Lead's independent-position 4000-transcript deletion_0.6 sensitivities:
   one span 0.5853; four spans 0.5545. Lead's five-by-200 default catch is
   69/144=0.4792. The current regression prints measured catches/intervals for
   BOTH fractions and all three readings; those outputs remain blocked.
   The reviewer's unchanged shared-seed script (1224/2000 default) is correlated
   and must not be substituted for independent-position sensitivity.
2. M4 equal allocation (chosen) versus proportional allocation. Lead observed
   equal's 57/57 subjects, 29 x4 and 28 x3, versus first-N 100 abstract_algebra
   plus 100 anatomy. A measured proportional comparison and the full equal
   subject map remain pending; no fabricated item outcomes are supplied.
3. M1 missing maximum remains unknown/unbounded (chosen) versus a supplied
   prospective physical maximum. Lead's step-world power estimate is 4995 J
   in either reading; missing maximum gives infinite width, a declared 250 W
   gives derived 25.010 J. Counter width is 30.001 J without Pmax.
   No 250 W default or observed-peak assumption was introduced.

No B1 default-channel ruling: multiple traces still require explicit selection.
