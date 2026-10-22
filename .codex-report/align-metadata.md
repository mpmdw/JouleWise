# Alignment metadata baseline — fix round 1 (fix1e)

## SUMMARY

Continued the existing metadata branch without rewriting its history.
Fixed logged decode features to exclude hidden tokens while retaining logged timing.
Added within-task-pair permutation inference that refits the whole grouped CV.
The independent-draw null and visible side-task checks pass in repository CI.
Derived bootstrap bandwidth/start budgets and adopted the lead's four-SE coverage bar.
All alignment tests and the full CI workflow pass on the implementation head.
Shared records, interfaces and pipeline files remain unchanged; core is stdlib-only.
Verification used GitHub CI because the shell never became available.
Three shell-dependent check groups remain for the lead; the patch and script are included.

## FILES

- joulewise/align/metadata_baseline.py: corrected logged-view features, leave-pair-out CV, new refitted permutation procedure and statistics re-exports.
- joulewise/align/stats.py: reusable stdlib statistics, conditional-CV interval documentation, derived bootstrap bandwidth/start budget and Newton precision explanation.
- tests/align/test_metadata_baseline.py: hand arithmetic, hidden-stripped equality, training-fold isolation, serializer-to-classifier visible world with calibrated inference, deterministic paired leakage control.
- tests/align/test_metadata_baseline_review.py: reviewer worlds and exact-equality repros, independent-draw null calibration, label-count/refit/hand-p mechanics and invalid-input flags.
- tests/align/test_stats.py: arithmetic, literal resampling precision replay, numerical flags and four-SE coverage bar.
- tests/test_shard_tests.py: registry exception only; existing discovery prefix changed from "align.test_" to "align." to include twins, matching sibling lanes.
- .codex-report/align-metadata.md: this report, patch and lead-run probe.

## PUBLIC API

All original signatures remain unchanged and are exported by metadata_baseline.
Reusable AUC, DeLong, bootstrap and logistic functions live in stats.

```python
def features(episode: Episode, *, logged_only: bool = True) -> dict[str, float]: ...
def auc(scores: Sequence[float], labels: Sequence[int]) -> float: ...
def delong_ci(scores: Sequence[float], labels: Sequence[int], level: float = 0.95) -> tuple[float, float]: ...
def paired_auc_difference(scores_a: Sequence[float], scores_b: Sequence[float], labels: Sequence[int]) -> tuple[float, float, float]: ...
def fit_logistic(X: Sequence[Sequence[float]], y: Sequence[int], *, l2: float) -> list[float]: ...
def grouped_cv_scores(episodes: Sequence[Episode], *, l2: float, feature_names: Sequence[str] | None = None) -> list[tuple[str, float]]: ...
def cluster_bootstrap_auc_ci(scores: Sequence[float], labels: Sequence[int], groups: Sequence[str], *, level: float = 0.95, n_boot: int | None = None, seed: int = 0) -> tuple[float, float, int]: ...
def grouped_cv_permutation_test(episodes: Sequence[Episode], *, l2: float, n_permutations: int, seed: int = 0, feature_names: Sequence[str] | None = None) -> tuple[float, float, int]: ...
```

The new function returns (observed_auc, two_sided_p, permutations_used).
Its statistic is abs(AUC - 0.5); p=(1+k)/(B+1), ties included, and resolution
is 1/(B+1). It preserves within-pair class counts and refits all held-out
models for every shuffled vector. It does not mutate input episodes.
Invalid budgets or undefined CV return flagged NaNs; undefined permutations
are never discarded. Other result flags propagate.

Feature names remain stable: turns, prefill_tokens, decode_tokens, hidden_tokens,
tool_calls, duration_s, decode_per_turn_mean, decode_per_turn_max,
tool_calls_per_turn, decode_tokens_per_second, fraction_turns_with_tool_calls,
and log1p companions for turns, prefill_tokens, decode_tokens, hidden_tokens,
tool_calls. Result subclasses retain the specified base interfaces and expose
a flags tuple; callers must preserve it explicitly when serialising.

DeLong and cluster-bootstrap intervals applied to pooled CV scores are
**conditional on the fitted fold models**. They do not estimate the variation
of refitting the classifier and must not be used alone to claim separation.

## TESTS RUN

Completed [CI run 39733292767](https://github.com/mpmdw/JouleWise/actions/runs/39733292767)
on implementation head 895d3fb1c20bd5910eee03d0e06edb4cc195e5ff.
All CI workflow jobs passed. PR #523 is a draft against
lane/2026-10-21-align-spine (base 4d47c4362352ccd8d4d904134a79f0d8260b21b5);
CI checks its PR merge, not a current-main integration. The report-only commit
preserves the tested production and test blobs. Its automatically queued CI
is separate from the completed evidence recorded here.

All following module counts and seconds were printed by the named CI job
in **run 39733292767**:

| CI job | Module | Tests | Failures | Errors | Skips | Seconds |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| test (3.13, 9) | tests.align.test_metadata_baseline | 9 | 0 | 0 | 0 | 3.897 |
| test (3.13, 8) | tests.align.test_metadata_baseline_review | 5 | 0 | 0 | 0 | 119.532 |
| test (3.13, 5) | tests.align.test_records | 4 | 0 | 0 | 0 | 0.007 |
| test (3.13, 4) | tests.align.test_stats | 13 | 0 | 0 | 0 | 40.608 |

All new/changed metadata cases are timed below, exactly as printed by the
named CI job in **run 39733292767**. Millisecond-rounded 0.000 is not a claim
that no work occurred. Every new case is below the brief's approximate
three-minute compute limit.

| CI job | Test | Printed runtime (s) |
| --- | --- | ---: |
| test (3.13, 8) | align.test_metadata_baseline_review.IndependentNullTests.test_refitted_procedure_independent_null | 108.807 |
| test (3.13, 8) | align.test_metadata_baseline_review.PermutationTests.test_invalid_and_undefined_inputs_flagged | 0.000 |
| test (3.13, 8) | align.test_metadata_baseline_review.PermutationTests.test_label_counts_real_refits_and_hand_p_value | 0.018 |
| test (3.13, 8) | align.test_metadata_baseline_review.ReviewReproTests.test_r2_leak_exact_equality | 10.271 |
| test (3.13, 8) | align.test_metadata_baseline_review.ReviewReproTests.test_r2_solworld_exact_equality | 0.436 |
| test (3.13, 9) | align.test_metadata_baseline.FeatureTests.test_all_work_view_and_no_outcome_leakage | 0.000 |
| test (3.13, 9) | align.test_metadata_baseline.FeatureTests.test_empty_and_zero_duration_are_flagged | 0.000 |
| test (3.13, 9) | align.test_metadata_baseline.FeatureTests.test_logged_hidden_tokens_equal_stripped_log | 0.000 |
| test (3.13, 9) | align.test_metadata_baseline.FeatureTests.test_overlaps_are_recorded | 0.000 |
| test (3.13, 9) | align.test_metadata_baseline.FeatureTests.test_stable_logged_feature_values_and_count_logs | 0.000 |
| test (3.13, 9) | align.test_metadata_baseline.GroupedPipelineTests.test_end_to_end_visible_side_task | 3.644 |
| test (3.13, 9) | align.test_metadata_baseline.GroupedPipelineTests.test_grouped_training_only_and_input_order | 0.156 |
| test (3.13, 9) | align.test_metadata_baseline.GroupedPipelineTests.test_intercept_only_and_impossible_folds_preserve_rows | 0.053 |
| test (3.13, 9) | align.test_metadata_baseline.GroupedPipelineTests.test_paired_fixture_is_only_a_deterministic_leakage_control | 0.043 |

The first saved fix checkpoint also completed successfully:
[run 39729753270](https://github.com/mpmdw/JouleWise/actions/runs/39729753270),
head 97974a1832c9b21a45886c61827146d250e04171. Its F1 repros passed before
the statistical update was pushed.

No shell command succeeded: python3 --version was attempted first and retried
over the requested ten-minute window; a later retry still returned
"No usable execution environment is available." Neither requested local
entrypoint below was executed locally:
```sh
python3 -m unittest discover -s tests/align -t .
python3 -m unittest discover -s tests
```
The GitHub route executed the discovered modules through the repository's
ordinary and exclusive CI shards instead. No optional extra was installed,
and there are no extra-dependent lane tests or lane skips.

Exact test commands used by CI:
```sh
python3 scripts/quick_suite.py --tier quick --workers 4
python -m compileall -q joulewise tests
python -m unittest -v tests.test_calibration_exits
```

CI job **quick, run 39733292767** printed:
```text
QUICK SUMMARY tier=quick modules=212 excluded=178 failures=0 seconds=154.165 result=PASS
```
Alignment modules are unknown-weight quick exclusions, and are executed by
the full shards. The existing inventory test passes without twin files;
the twin-present check remains unexecuted below.

Exact ordinary-suite command, with SHARD_COUNT=12 and SHARD_INDEX selecting
each of its partitions, from CI jobs **test (3.13, 1) through test (3.13, 12),
run 39733292767**:
```sh
python - <<'PY'
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, "scripts")
import shard_tests

overlay = json.loads(Path("scripts/test_timings.json").read_text())
exclusive = frozenset(overlay["exclusive_modules"])
discovered = shard_tests.discover_test_modules()
assert exclusive <= set(discovered), (exclusive, discovered)
timings = shard_tests.load_timing_map()
ordinary = tuple(module for module in discovered if module not in exclusive)

# UNIT-atomic, not module-atomic. Modules in split_modules (today
# test_reduce and test_controller_g2b_attachment, each audited for
# per-test independence) are spread across shards at test
# granularity, so no single module floors the shard time. This edits no test file and
# skips nothing: expand_units emits one unit per declared heavy
# test plus ONE remainder unit holding every other test in that
# module, and verify_split_declaration fails the build closed if
# a declared id no longer exists.
splits = {
    module: declaration
    for module, declaration in shard_tests.load_split_declarations().items()
    if module in set(ordinary)
}
unknown = shard_tests.conservative_unknown_weight()
units, weights = shard_tests.expand_units(
    ordinary, timings, splits, unknown_weight=unknown
)
count = int(os.environ["SHARD_COUNT"])
partitions = shard_tests.partition_modules(
    units, weights, count, unknown_weight=unknown
)
totals = shard_tests.partition_totals(
    partitions, weights, unknown_weight=unknown
)
print("ORDINARY SHARD ESTIMATES", ",".join(f"{value:.3f}" for value in totals))
index = int(os.environ["SHARD_INDEX"])
raise SystemExit(shard_tests.run_units(partitions[index - 1], count, index))
PY
```

Printed ordinary-shard receipts, **run 39733292767**; all report PASS:

| CI job | Tests | Failures | Errors | Skips |
| --- | ---: | ---: | ---: | ---: |
| test (3.13, 1) | 565 | 0 | 0 | 10 |
| test (3.13, 2) | 626 | 0 | 0 | 7 |
| test (3.13, 3) | 610 | 0 | 0 | 12 |
| test (3.13, 4) | 794 | 0 | 0 | 9 |
| test (3.13, 5) | 761 | 0 | 0 | 18 |
| test (3.13, 6) | 706 | 0 | 0 | 18 |
| test (3.13, 7) | 655 | 0 | 0 | 11 |
| test (3.13, 8) | 795 | 0 | 0 | 11 |
| test (3.13, 9) | 990 | 0 | 0 | 15 |
| test (3.13, 10) | 1286 | 0 | 0 | 24 |
| test (3.13, 11) | 949 | 0 | 0 | 6 |
| test (3.13, 12) | 1096 | 0 | 0 | 4 |

CI job **calibration-exits-exclusive (3.13), run 39733292767** printed
48 tests in 825.853 s and OK, with no skips.
CI jobs **calibration-writer-crash-matrix-exclusive (3.13, 1)** and
**calibration-writer-crash-matrix-exclusive (3.13, 2)**, **run 39733292767**,
printed respectively 1 test in 478.831 s and 19 tests in 236.049 s;
both have zero failures/errors/skips. Their exact driver, with SHARD_INDEX
selecting each partition, is:
```sh
python - <<'PY'
import os
import sys

sys.path.insert(0, "scripts")
import shard_tests

module = "tests.test_calibration_writer_crash_matrix"
timings = shard_tests.load_timing_map()
splits = shard_tests.load_split_declarations()
unknown = shard_tests.conservative_unknown_weight()
# expand_units runs verify_split_declaration, which fails closed if
# the declared heavy test id no longer exists. That is the case a
# computed remainder would otherwise absorb in silence, handing one
# shard ~20 minutes of unaccounted work while the weights disagree.
units, weights = shard_tests.expand_units(
    (module,), timings, {module: splits[module]}, unknown_weight=unknown
)
partitions = shard_tests.partition_modules(
    units, weights, 2, unknown_weight=unknown
)
totals = shard_tests.partition_totals(
    partitions, weights, unknown_weight=unknown
)
print("CRASH-MATRIX SHARD ESTIMATES", ",".join(f"{v:.3f}" for v in totals))
index = int(os.environ["SHARD_INDEX"])
raise SystemExit(shard_tests.run_units(partitions[index - 1], 2, index))
PY
```

Build, installed-wheel smoke, compilation, generated-state/repin/documentation
fences, historical receipts and CLI/mock checks also passed in that run.
The separate gate-ledger workflow remains red for the draft's lead-owned
NOT-RUN rows; no review or merge gate is claimed.

<details>
<summary>Existing full-suite skip reasons, verbatim from CI jobs test (3.13, 1) through test (3.13, 12), run 39733292767</summary>

- ACCEPTANCE GATE SKIP: determinism gate requires the retained runs/ corpus
- ACCEPTANCE GATE SKIP: six frozen legacy corpus bundles require the retained runs/ corpus
- CommonCrypto is macOS only
- Darwin pgrep ancestor exclusion; Linux pgrep has no such rule
- FLAG joulewise/arm_readiness.py:7621: committed GAMMA lacks freeze authority; writer/ARM cannot continue. No nonphysical semantic shortcut is allowed.
- NEEDS-RULING: config-authenticated mock telemetry is excluded by the production claim loader, so the existing canned fixture cannot satisfy D-158's DATA-only predicate without loosening a production gate or building a new corpus fixture
- POWER-Z KM003C not on the USB bus
- STRUCTURAL-BLOCKED: generator targets uninstalled _v2 family while the registry installs _v5
- STRUCTURAL-BLOCKED: synthetic _v5 fixture omits the family-publication marker required before self-predecessor validation
- U2 successor engine pending
- a desk run of the real read-only probes (macOS)
- block-3 b3w1 archive is local to the measurement Mac
- clonefile(2) is an APFS call
- controlled runs corpus unavailable
- design/2026-10-05-v5-claim-block-draft is not in this clone
- full scored corpus (set JOULEWISE_FULL_CORPUS=1)
- full-fixture proof runs in d117-production-proof
- gate-prune inventory is not on this machine
- jsonschema not installed
- jsonschema not installed (optional)
- kern.bootsessionuuid is Darwin-only
- kern.bootsessionuuid is a Darwin kernel value
- lead-reviewed D-079 import custody inputs are unavailable
- lead-reviewed D-079 import inputs are unavailable
- live identity probes need macOS sysctl
- local Qwen3 tokenizer mirrors are absent
- local model mirrors absent (CI environment): ['qwen25_0p5b', 'qwen25_1p5b', 'qwen25_7b']
- local model mirrors absent (CI environment): ['qwen3-1p7b', 'qwen3-8b']
- lsof is not installed
- markdown-it-py not installed; the build cannot run here
- matplotlib ([analysis] extra) not installed
- measurement ledger not on this machine
- native QoS requires macOS
- optional jsonschema dependency is absent
- pinned MATH source absent
- reads the macOS kernel clock
- reads the real SMC (macOS)
- reads the real gauge (macOS)
- reads the real host CPU ticks (macOS)
- reads the real kernel clock (macOS)
- reads the real notify bus (macOS)
- reads the real process table (macOS)
- real Qwen3 tokenizer test requires the optional tokenizers library and local tokenizer.json
- real campaign-log corpus is unavailable
- real collect subprocess runs the macOS census and power-policy probes (pmset, sysctl); on Linux every round errors and, since fix round 4, an all-error session exits 1 by design
- real launchctl required
- real runs corpus unavailable
- real spawned worker uses native QoS; hosted Linux shards feed the runner via stdin, which spawn cannot re-import
- requires Darwin and explicit QG_LIVE_DARWIN=1 real-acquisition opt-in
- requires Darwin fchflags/st_flags
- requires Darwin's POSIX extended regular expressions
- requires Darwin's real boot-session sysctl command
- requires Darwin's real caffeinate process
- requires Darwin's real pgrep command semantics
- requires Darwin's real sysctl command
- retained XD/AQ corpora are not present; run the default R7F CLI where both corpora live
- retained capture 20260722T145535-e941c821 is not on this machine; run scripts/check_paper_replay_fence.py where the corpus lives
- retained runs corpus is absent
- runs/ corpus absent (clean checkout without bundles)
- runs_window corpus absent (clean checkout without bundles)
- source corpus unavailable: /Users/edr/code/JouleWise/runs_window_a5_20260723
- split production proof requires a registered JOULEWISE_D117_PROOF_PARTITION
- stopped-after-exec probe requires Darwin POSIX_SPAWN_START_SUSPENDED
- successor member not minted yet; shape check is vacuous
- successor mirrors are still absent/incomplete: ['qwen3-1p7b', 'qwen3-8b']
- temporary filesystem is case-sensitive
- the 2026-09-22 harvest archives are not on this machine
- the block-3 reference archive and the measurement interpreter are on Ed's Mac only
- the block-5 design branch is not in this clone
- the gate-prune inventory is not on this machine
- the real kern.bootsessionuuid exists only on macOS
- the two pilot-night archives are not on this machine
- this file system gave the replacement lock the inode number of the lock just unlinked (4522143); the reclaimer tells the two apart by device and inode number only, so here it cannot (known limit of scripts/run_campaign.py _hazard_reclaim_stale_campaign_lock; APFS on the measurement Mac does not reuse numbers)
- window-B quarantine custody path is absent

</details>

## END-TO-END

The visible fixture runs shared Episode/Turn/ToolCall construction through
to_json/from_json, logged features, leave-one-task-pair-out training,
held-out probabilities, AUC, intervals and the new whole-CV permutation test.
The brief's five-pair, two-condition, thirty-seed shape is retained, with
multi-turn model/tool episodes. Sabotage adds visible calls/tokens and hidden
reasoning; the logged feature adapter removes only the hidden token counts.

CI job **test (3.13, 9), run 39733292767** printed:
```text
METADATA VISIBLE auc=0.772933333
delong_conditional_on_fitted_fold_models=(0.7168155120613808, 0.820711935337398)
bootstrap_conditional_on_fitted_fold_models=(0.7499111111111111, 0.8029333333333334, 18577)
permutation=(0.7729333333333334, 0.047619047619047616, 20)
interval_flags=()
```
The visible side task therefore passes the calibrated strict p < 0.05 check.
The two intervals above are **conditional on the fitted fold models**.

The previous visible values came from CI job **test (3.13, 9), run 39708018448**:
AUC 0.785022222; conditional DeLong [0.7302036860122262, 0.8312761210834372];
conditional bootstrap [0.77, 0.8065333333333333], B=25600.
The current test printed the movement from those previous printed values
in CI job **test (3.13, 9), run 39733292767**:
```text
delta_auc_from_previous_print=-0.012088889
delta_delong=(-0.01338817395084535, -0.010564185746039234)
delta_bootstrap=(-0.020088888888888934, -0.0035999999999999366, -7023)
```
F1 changes the visible inputs and AUC/DeLong values; N1/N2 change the automatic
bootstrap schedule. No solver stopping threshold was changed by N3.

CI job **test (3.13, 8), run 39733292767** printed the F1 exact-equality repros:
- r2_solworld visible: lane and hidden-stripped AUC both 0.772933333; both conditional DeLong intervals [0.7168155120613808, 0.820711935337398].
- r2_solworld hidden-only: both AUCs 0.500000000 and both conditional DeLong intervals [0.5, 0.5].
- r2_leak timing held fixed: both mean AUCs 0.478666667; both first conditional DeLong intervals [0.4528910302264275, 0.5835420642216815].
- r2_leak physical timing: both mean AUCs 1.000000000 and both first conditional DeLong intervals [1.0, 1.0]. Recorded generation time remains visible to the baseline.
The assertions compare exact features, score vectors, AUCs and intervals before
rounding. The degenerate paired hidden-only case is a leakage control, not the
null used to assess inference.

The independent null instead draws every episode independently. Sabotage adds
an unlogged hidden turn/tool call inside existing slack, with no change to the
logged-feature distribution. Real features, refits and held-out AUCs are used
on every permutation; no fitted path is mocked.
CI job **test (3.13, 8), run 39733292767** printed:
```text
worlds=40 pairs=5 seeds=30 B=20
auc_mean=0.501978889 delta_mean_from_old_paired_null=0.001978889
auc_sd=0.045176035
delong_conditional_on_fitted_fold_models_claims=6
bootstrap_conditional_on_fitted_fold_models_claims=15
refitted_permutation_claims=2 four_se_bar=7.513619501
runtime_s=108.804
```
The enclosing null test printed 108.807 s. It passes the lead's count bar;
the conditional bootstrap's measured false claims exceed that same bar.
The old point-null AUC is replaced by a distribution of independently drawn
worlds, with the printed mean movement above. The full requested null runs
are not represented by these shorter CI results; they remain explicitly
unexecuted below.

The same CI job printed the hand mechanics check:
```text
PERMUTATION HAND B=31 real_fit_calls=96 k=8 p=0.28125
```
Every permuted vector retains each pair's class count. The real fit wrapper
counts every fold in the observed CV and each permutation; the tiny-case
rank arithmetic independently determines which statistics are extreme.

CI job **test (3.13, 4), run 39733292767** printed the literal-resample automatic
precision check and fixed-score interval coverage:
```text
AUTO BOOTSTRAP B=18577 bandwidth=0.008218251
endpoint_mc_se=(0.0013938148986703351, 0.0) target=0.003700000
interval=(0.26, 1.0, 18577)
INTERVAL COVERAGE truth=0.689691027 worlds=200 delong_hits=190 bootstrap_hits=190
COVERAGE BAR four_se=0.061644140 delta_from_old_one_se=0.046233105
```
Coverage counts stay at the previous printed values; the acceptance bar changes
by the printed amount under F4/N4. This fixed-score coverage experiment is
separate from the refitted-CV null experiment. The automatic endpoint target
remains a plug-in estimate, with the budget/degeneracy limitations documented
in the public function; no hardware result is claimed.

## DECISIONS I MADE

- F1 is decided by the records' hidden-token definition and the lead's ruling. Every logged decode feature subtracts each selected turn's hidden_tokens. The all-work view retains full decode and hidden counts. Episode.totals is not changed.
- Logged timestamps remain visible, including time spent generating hidden tokens; duration_s remains whole-episode elapsed time and decode throughput uses selected turn time.
- F2 uses option (a), a within-task-pair label permutation test with whole-CV refitting. With only a few pairs its exchangeability-based level is preferable to a refitting cluster bootstrap's small-cluster approximation.
- Separation uses the lead's strict two-sided p < 0.05. The calibration compute budget is B=20, with resolution 1/21. B=19 cannot produce p < 0.05 because its minimum p is exactly 0.05. This resolves the brief's strict-comparison/B=19 mismatch without weakening the requested comparison.
- The independent null uses the reviewer's episode generator and seed sequence. Every condition draws its own episodes; sabotage adds only an unlogged hidden turn and tool call inside existing slack. Its logged-feature distribution is unchanged. The old identical-pair fixture is retained solely as a deterministic leakage control and supplies no inferential evidence.
- Calibration uses the specified four-binomial-SE false-separation bar, with world count and permutation count explicit compute budgets. The visible side task must also pass the calibrated procedure.
- F4/N4 follows the lead's ruling in place of the original literal one-SE requirement. Four binomial SEs reduce the normal-approximation false-alarm rate to about 6e-5 and, at 200 worlds, detect coverage below 0.888. No additional seed-selected or optional under-coverage condition was added.
- N1 uses Bofinger's normal-reference MSE-optimal quantile-density bandwidth: B^(-1/5) * [4.5 phi(z)^4/(2z^2+1)^2]^(1/5), z=Phi^-1(p), clipped to p at the tails. N5 replays this rule on literal episode resamples.
- N2 starts at ceil(p(1-p)/(0.01 |z| phi(z))^2), obtained by substituting a normal density and half-width into the brief's endpoint Monte Carlo target. Doubling remains only a compute schedule; both estimated endpoint SEs must meet the target. Unresolved floating-point targets and exhausted budgets are flagged.
- N3 keeps the required coefficient-relative Newton step of 1e-10 and relates it to 1% of the printed AUC half-widths, rather than to an agreement-test bar. The stopping rule is not itself an uncertainty guarantee.
- F3 changes only the existing registry exception to "align.", matching sibling lanes and covering twin subpackages.
- Core and tests remain stdlib-only. No optional extra was installed; no extra-dependent tests or skips exist in this lane.
- All writes are confined to WRITE_SCOPE and its explicit registry exception. No twin or review_repro file is committed, and every branch update is a non-force fast-forward of the metadata lane.
- Counts have log1p companions; duration and rate features do not. Empty denominators produce zero plus flags, and no episode is excluded. Positive labels mean sabotage and larger probabilities mean greater suspicion.
- Logistic fitting minimises summed negative log likelihood plus l2/2 times squared standardised slopes, leaving the intercept unpenalised. Only training population means/SDs are used; constant columns receive zero slopes and coefficients are returned on the original scale. Numerical/compute failures carry flags.
- CV holds out one whole task pair, preserves input order and uses feature insertion order by default. An empty feature_names list requests intercept-only fitting; unknown names retain all episode IDs with flagged NaNs.
- DeLong uses sample placement variances and a logit-transformed normal interval. Boundary/zero-variance intervals are flagged, not interpreted as zero population uncertainty. Paired DeLong uses placement differences to retain covariance.
- The conditional cluster bootstrap resamples whole task pairs with multiplicity. Single-class draws are counted in flags and redrawn; returned B counts valid replicates. Group-pair U sums are checked against literal episode resampling. Configurable bootstrap/Newton limits are compute budgets, not inferential thresholds.
- The fixed-score interval coverage experiment retains its original Normal(0,1) versus Normal(0.7,1) worlds, whose true AUC is Phi(0.7/sqrt(2)), and its existing seeds. Only the lead-ruled coverage bar changes; no seed selection was used.
- Exact equality is used for identical integer feature inputs passed through identical deterministic code, IDs, names and reproducibility. Other numerical comparisons retain the brief's relative/float-noise bars with their existing derivations.

## CONTRACT-CHANGE

none. The logged-view interpretation is a lane-local adapter over the frozen
records contract. No shared record, interface or pipeline plan was edited.

## OPEN ISSUES

The new public grouped_cv_permutation_test needs an independent twin.
Its direct tests verify pair class counts, real refit counts and a hand-derived
tiny-case p-value; those tests do not constitute independent twin agreement.
Automatic bootstrap endpoint precision remains a plug-in estimate with explicit
budget/degeneracy flags. No hardware, live campaign, current-main merge-tree
validation or merge approval is claimed. Draft PR #523 remains a checkpoint;
the separate gate-ledger workflow reports its lead-owned NOT-RUN rows.

### NOT EXECUTED (no VM): lead to run

The first shell command was python3 --version; repeated attempts over the
requested ten-minute window all failed with "No usable execution environment
is available". These checks require a working tree with uncommitted twin/probe
files, so the GitHub-only route could not execute them. Run from a review
checkout at the pushed metadata head. The patch was prepared from twin commit
4419b472e2d6455a62470e460b64c110961ae12a; its source files match the branch snapshot read here.
Fetch its files without committing them:

```sh
git fetch origin lane/2026-10-21-align-metadata-twin
mkdir -p tests/align/twins
for f in tests/align/twins/__init__.py tests/align/twins/metadata_twin.py tests/align/twins/test_metadata_twin_selfcheck.py tests/align/test_twin_metadata.py; do
    git show 4419b472e2d6455a62470e460b64c110961ae12a:"$f" > "$f"
done
```

1. F1 twin agreement, first as fetched and then after applying the patch below:

```sh
python3 -m unittest tests.align.test_twin_metadata tests.align.twins.test_metadata_twin_selfcheck -v
git apply /tmp/align-metadata-twin-f1.patch
python3 -m unittest tests.align.test_twin_metadata tests.align.twins.test_metadata_twin_selfcheck -v
```

Save the unified diff below as /tmp/align-metadata-twin-f1.patch. Neither agreement
run was executed here, so no failure count or passing twin result is claimed.
Explain every first-run failure by F1 and require the patched run to pass.

2. F3 registry repro, with the twin files still present:

```sh
python3 tests/test_shard_tests.py
```

3. F2 full independent-null calibration at both requested shapes, using the
complete null_cov2.py extension below and the brief's worlds.py beside it:

```sh
python3 review_repro/null_cov2.py 200 5 30
python3 review_repro/null_cov2.py 60 17 30
```

The extension defaults to B=20 for strict p<0.05, retains the lane/twin
conditional-interval coverage counts, prints separation counts side by side,
and asserts the lead's four-SE bar. The full-run bars remain at most 22 claims
and at most 9 claims respectively; no result for either command is claimed.

### Twin patch (not applied or committed here)

```diff
--- a/tests/align/twins/metadata_twin.py
+++ b/tests/align/twins/metadata_twin.py
@@ -21,16 +21,11 @@
 R1  Feature names. The brief fixes the quantities, not the strings. This twin
     uses ``FEATURE_NAMES`` below, in that order. The comparer maps names.
 
-R2  ``decode_tokens`` includes hidden tokens. ``records.Turn`` says hidden
-    tokens "are part of ``decode_tokens``", and the brief says to take the
-    counts "from ``episode.totals(logged_only=...)``". So with
-    ``logged_only=True`` the twin's ``decode_tokens`` (and every decode-derived
-    feature: per-turn mean and max, per second, log1p) still counts hidden
-    tokens; only the ``hidden_tokens`` feature (and its log1p) is set to zero.
-    If the real module instead subtracts hidden tokens from decode in the
-    logged view, every decode feature differs by the hidden count. This choice
-    decides whether hidden reasoning is visible to the baseline at all, so it
-    changes the baseline's AUC on any world whose sabotage adds hidden tokens.
+R2  Fix-round-1 F1 ruling: hidden tokens are part of records.Turn.decode_tokens,
+    but the log does not show them. Subtract hidden tokens in every logged
+    decode-derived feature and zero the hidden count. Keep logged timestamps,
+    including time spent generating hidden work. The all-work view keeps full
+    decode and hidden counts. This supersedes the original opposite reading.
 
 R3  Zero denominators. A ratio with a zero denominator (no turns in the
     view, or zero turn time) is 0.0, and the per-turn max over no turns is 0.0.
@@ -195,8 +190,9 @@
     fraction of turns with tool calls, and the log1p of each count").
 
     ``hidden_tokens`` is zero when ``logged_only`` is true, because a log does
-    not show hidden tokens. ``decode_tokens`` is taken from ``totals()`` as is,
-    and ``records.Turn`` counts hidden tokens inside it (R2).
+    not show hidden tokens. Logged decode counts subtract each turn's hidden
+    component (F1 ruling); all-work decode counts remain full. Logged timestamps
+    stay visible, including time spent generating hidden tokens.
     """
     totals = episode.totals(logged_only=logged_only)
     view_turns = episode.logged_turns() if logged_only else episode.turns
@@ -206,12 +202,13 @@
     counts = {
         "turns": totals["turns"],
         "prefill_tokens": totals["prefill_tokens"],
-        "decode_tokens": totals["decode_tokens"],
+        "decode_tokens": totals["decode_tokens"] - (totals["hidden_tokens"] if logged_only else 0),
         "hidden_tokens": 0 if logged_only else totals["hidden_tokens"],
         "tool_calls": totals["tool_calls"],
     }
 
-    per_turn_decode = [turn.decode_tokens for turn in view_turns]
+    per_turn_decode = [turn.decode_tokens - (turn.hidden_tokens if logged_only else 0)
+                       for turn in view_turns]
     turn_time_ns = sum(turn.end_ns - turn.start_ns for turn in view_turns)
     turns_with_calls = 0
     for turn in view_turns:
--- a/tests/align/twins/test_metadata_twin_selfcheck.py
+++ b/tests/align/twins/test_metadata_twin_selfcheck.py
@@ -102,16 +102,16 @@
             self.assertAlmostEqual(got[name], value, delta=bar(4, value), msg=name)
 
     def test_logged_view_by_hand(self):
-        # logged turns 0 and 1: turns 2, prefill 1300, decode 300 (turn 0's 50 hidden
-        # tokens are inside its 200 decode tokens, R2), hidden shown as 0, tool calls 2
+        # logged turns 0 and 1: turns 2, prefill 1300, decode 250 (turn 0's 50 hidden
+        # tokens are subtracted from its 200 decode tokens, F1), hidden shown as 0, tool calls 2
         # (turn 1's call is unlogged), turn time 2 s + 1 s.
         expected = {
-            "turns": 2.0, "prefill_tokens": 1300.0, "decode_tokens": 300.0, "hidden_tokens": 0.0,
-            "tool_calls": 2.0, "duration_s": 10.0, "decode_per_turn_mean": 150.0,
-            "decode_per_turn_max": 200.0, "tool_calls_per_turn": 1.0,
-            "decode_tokens_per_turn_second": 100.0, "fraction_turns_with_tool_calls": 0.5,
+            "turns": 2.0, "prefill_tokens": 1300.0, "decode_tokens": 250.0, "hidden_tokens": 0.0,
+            "tool_calls": 2.0, "duration_s": 10.0, "decode_per_turn_mean": 125.0,
+            "decode_per_turn_max": 150.0, "tool_calls_per_turn": 1.0,
+            "decode_tokens_per_turn_second": 250.0 / 3.0, "fraction_turns_with_tool_calls": 0.5,
             "log1p_turns": math.log(3.0), "log1p_prefill_tokens": math.log(1301.0),
-            "log1p_decode_tokens": math.log(301.0), "log1p_hidden_tokens": 0.0,
+            "log1p_decode_tokens": math.log(251.0), "log1p_hidden_tokens": 0.0,
             "log1p_tool_calls": math.log(3.0),
         }
         self.assert_features(twin.features(hand_episode()), expected)
```

### Full review_repro/null_cov2.py extension (not committed as a probe file)

The portable paths below work in either the cloud checkout or the lead's Mac
review checkout. The world generator remains the reviewer's APPENDIX worlds.py.

```python
"""Refit-aware extension of the reviewer's null_cov2.py; keep worlds.py beside it."""
import math
import statistics
import sys
import time
from pathlib import Path

# Portable to both the cloud checkout and the lead's Mac review worktree.
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from worlds import world
from joulewise.align import metadata_baseline as mb
from joulewise.align.metadata_baseline import grouped_cv_permutation_test
from tests.align.twins import metadata_twin as tw

N = int(sys.argv[1])
pairs = int(sys.argv[2])
seeds = int(sys.argv[3])
# Explicit compute budget. B=20 has resolution 1/21; B=19 cannot yield p<0.05.
B = int(sys.argv[4]) if len(sys.argv) > 4 else 20
aucs = []
dcov = bcov = tcov = claims = 0
bhw = []
dhw = []
t0 = time.time()
for seed in range(N):
    eps = world(5000 + seed, mode="null", pairs=pairs, seeds=seeds)
    pred = mb.grouped_cv_scores(eps, l2=1.0)
    sc = [s for _, s in pred]
    lab = [int(e.condition == "sabotage") for e in eps]
    g = [e.task_pair for e in eps]
    a = mb.auc(sc, lab)
    d = mb.delong_ci(sc, lab)
    # 999 is the reviewer's explicit conditional-bootstrap compute budget.
    b = mb.cluster_bootstrap_auc_ci(sc, lab, g, n_boot=999, seed=seed)
    tb = tw.cluster_bootstrap_auc_ci(sc, lab, g, n_boot=999, seed=seed)
    calibrated = grouped_cv_permutation_test(eps, l2=1.0, n_permutations=B, seed=seed)
    assert math.isfinite(calibrated[1]), calibrated.flags
    assert calibrated[0] == a  # Identical deterministic CV on identical inputs.
    claims += calibrated[1] < 0.05
    aucs.append(a)
    dcov += d[0] <= 0.5 <= d[1]
    bcov += b[0] <= 0.5 <= b[1]
    tcov += tb[0] <= 0.5 <= tb[1]
    bhw.append((b[1] - b[0]) / 2)
    dhw.append((d[1] - d[0]) / 2)
sd = statistics.stdev(aucs)
# 1.96 is the standard-normal 97.5th percentile rounded to two decimals.
# The false-separation bar is the lead's nominal count plus four binomial SEs.
bar = 0.05 * N + 4 * math.sqrt(0.0475 * N)
print(f"pairs={pairs} seeds={seeds} worlds={N} B={B} resolution={1/(B+1):.9f} "
      f"mean AUC={statistics.mean(aucs):.4f} true sd={sd:.4f} "
      f"(1.96 sd={1.96*sd:.4f}) "
      f"mean DeLong half-width conditional on the fitted fold models={statistics.mean(dhw):.4f} "
      f"mean boot half-width conditional on the fitted fold models={statistics.mean(bhw):.4f} "
      f"cover0.5 conditional on the fitted fold models: DeLong {dcov}/{N} "
      f"lane-boot {bcov}/{N} twin-boot {tcov}/{N}; "
      f"false separation conditional on the fitted fold models: DeLong {N-dcov}/{N} "
      f"lane-boot {N-bcov}/{N} twin-boot {N-tcov}/{N}; "
      f"refitted-permutation p<0.05 {claims}/{N} four-SE bar={bar:.6f} "
      f"t={time.time()-t0:.0f}s", flush=True)
assert claims <= bar, (claims, bar)
```

## NEEDS_RULING

none

## FIX LOG

- F1: fixed in 97974a1832c9b21a45886c61827146d250e04171; exact logged-feature/score/AUC/interval equality passes in CI. Twin agreement remains unexecuted as listed in OPEN ISSUES.
- F2: fixed in 895d3fb1c20bd5910eee03d0e06edb4cc195e5ff; independent null, refitted within-pair permutation inference, conditional interval labels and direct mechanics tests pass. Full null runs remain unexecuted as listed in OPEN ISSUES.
- F3: fixed in 97974a1832c9b21a45886c61827146d250e04171; prefix is "align." and CI inventory passes. The twin-present repro remains unexecuted as listed in OPEN ISSUES.
- F4: fixed in 895d3fb1c20bd5910eee03d0e06edb4cc195e5ff; lead-ruled four-binomial-SE bar and its false-alarm/detection derivation are beside the assertion.
- N1: fixed in 895d3fb1c20bd5910eee03d0e06edb4cc195e5ff; Bofinger bandwidth names its rule, exponent and constant.
- N2: fixed in 895d3fb1c20bd5910eee03d0e06edb4cc195e5ff; normal-reference starting B is derived from the stated endpoint precision rule.
- N3: fixed in 895d3fb1c20bd5910eee03d0e06edb4cc195e5ff; unchanged 1e-10 Newton bar is justified against printed uncertainty rather than the agreement-test bar.
- N4: fixed in 895d3fb1c20bd5910eee03d0e06edb4cc195e5ff; same lead-ruled coverage change as F4.
- N5: fixed in 895d3fb1c20bd5910eee03d0e06edb4cc195e5ff; independent literal-resampling replay uses the derived Bofinger bandwidth and passes the endpoint precision check.

