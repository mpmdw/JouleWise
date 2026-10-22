# Alignment metadata baseline — A6

## SUMMARY

Implemented the metadata-only sabotage baseline and reusable stdlib statistics.
The baseline exposes 16 stable logged features and holds out whole task pairs.
Logistic fitting standardises training data only and returns original-scale coefficients.
AUC handles ties; inference includes logit DeLong CIs, paired tests, and cluster bootstrap CIs.
Undefined analyses and compute-budget limits carry output flags without excluding episodes.
The visible 300-episode synthetic world scores AUC 0.785022222; its invisible control scores 0.5.
Shared records, interfaces, and the pipeline plan are unchanged; no hardware was contacted.
The 9,894-test source verification passed; two corrected metadata test bars await rerun.
Verification used CI because the managed environment never supplied a local shell.

## FILES

- joulewise/align/metadata_baseline.py: logged/all-work feature extraction, grouped held-out probabilities, statistics re-exports.
- joulewise/align/stats.py: AUC placements, logit DeLong intervals, paired DeLong tests, damped Newton logistic regression, adaptive cluster bootstrap, flagged output adapters.
- tests/align/test_metadata_baseline.py: feature arithmetic, training-fold isolation, serializer-to-classifier synthetic worlds.
- tests/align/test_stats.py: independent arithmetic, literal cluster resampling, Newton optimum, automatic precision/budget, seeded interval coverage.
- tests/test_shard_tests.py: registry exception ONLY: add "align.test_" to the recognised discovery-prefix tuple, normalising align.test_* to tests.align.test_*. Required by the observed repo-wide discovery inventory failure; no runner or test behavior changed otherwise.
- .codex-report/align-metadata.md: this record.

## PUBLIC API

All seven public functions are available from joulewise.align.metadata_baseline;
the five reusable statistical functions are defined in joulewise.align.stats.

```python
def features(episode: Episode, *, logged_only: bool = True) -> dict[str, float]: ...
def auc(scores: Sequence[float], labels: Sequence[int]) -> float: ...
def delong_ci(scores: Sequence[float], labels: Sequence[int], level: float = 0.95) -> tuple[float, float]: ...
def paired_auc_difference(scores_a: Sequence[float], scores_b: Sequence[float], labels: Sequence[int]) -> tuple[float, float, float]: ...
def fit_logistic(X: Sequence[Sequence[float]], y: Sequence[int], *, l2: float) -> list[float]: ...
def grouped_cv_scores(episodes: Sequence[Episode], *, l2: float, feature_names: Sequence[str] | None = None) -> list[tuple[str, float]]: ...
def cluster_bootstrap_auc_ci(scores: Sequence[float], labels: Sequence[int], groups: Sequence[str], *, level: float = 0.95, n_boot: int | None = None, seed: int = 0) -> tuple[float, float, int]: ...
```

Feature names, in default order: turns, prefill_tokens, decode_tokens,
hidden_tokens, tool_calls, duration_s, decode_per_turn_mean,
decode_per_turn_max, tool_calls_per_turn, decode_tokens_per_second,
fraction_turns_with_tool_calls, log1p_turns, log1p_prefill_tokens,
log1p_decode_tokens, log1p_hidden_tokens, log1p_tool_calls.

Results retain the specified float/dict/list/tuple interfaces via subclasses
with a flags tuple attribute. Flags are not additional numeric feature keys.
Report writers must explicitly preserve result.flags; plain JSON encoding of
the base container does not automatically include that attribute.

## TESTS RUN

Completed [CI run 39705032319](https://github.com/mpmdw/JouleWise/actions/runs/39705032319)
on code/test head 757f5db4d0ff6c2ba7444c6e74df33ab072f1b66, CPython 3.13.16,
merged with the spine (not current main). All 20 CI jobs passed.
Production modules are identical to this tested head. Final review found two
metadata test helpers still had a unit-scale floor; they have now been
corrected to the brief's relative bar (with the documented zero allowance).
A CI rerun on that assertion-only revision is pending. Statistics comment
spelling was also corrected; no production behavior changed.

- New lane: 20 tests, zero failures/errors/skips (metadata 7; statistics 13).
- Shared records: 4 tests, zero failures/errors/skips.
- Full ordinary suite: 9,826 tests, zero failures/errors, 145 existing skips.
- Exclusive calibration exits: 48 tests, zero failures/errors/skips.
- Exclusive crash matrix: 20 tests over two shards (1 + 19), zero failures/errors/skips.
- Combined full suite: 9,894 tests, zero failures/errors, 145 skips.
- Quick tier: 212 modules passed; 177 modules excluded by its existing weight,
  split, exclusive, and canonical-path rules. New alignment modules were
  unknown-weight exclusions in quick and were executed in the full shards.
- Packaging, installed-wheel smoke, compilation, state/repin/documentation fences,
  historical receipt checks and CLI/mock smoke jobs passed.

Commands actually run by existing CI:

```sh
python3 scripts/quick_suite.py --tier quick --workers 4
python -m compileall -q joulewise tests
python -m unittest -v tests.test_calibration_exits
python -m build
```

Ordinary-suite command, verbatim from .github/workflows/ci.yml; executed with
SHARD_COUNT=12 and SHARD_INDEX=1 through 12 (all 12 partitions):

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

Exclusive crash-matrix command, verbatim from that workflow; SHARD_INDEX=1 and 2:

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

| Ordinary shard | Tests | Skips |
| --- | ---: | ---: |
| 1/12 | 563 | 3 |
| 2/12 | 504 | 6 |
| 3/12 | 715 | 16 |
| 4/12 | 764 | 10 |
| 5/12 | 827 | 5 |
| 6/12 | 656 | 16 |
| 7/12 | 921 | 11 |
| 8/12 | 834 | 8 |
| 9/12 | 918 | 19 |
| 10/12 | 1178 | 20 |
| 11/12 | 931 | 6 |
| 12/12 | 1015 | 25 |

All 145 skips are pre-existing suite conditions, not lane-test skips. Their
74 distinct reasons and counts are reproduced from the completed job logs:

| Count | Existing-suite skip reason (verbatim) |
| ---: | --- |
| 18 | requires Darwin fchflags/st_flags |
| 13 | full scored corpus (set JOULEWISE_FULL_CORPUS=1) |
| 10 | block-3 b3w1 archive is local to the measurement Mac |
| 9 | matplotlib ([analysis] extra) not installed |
| 6 | FLAG joulewise/arm_readiness.py:7621: committed GAMMA lacks freeze authority; writer/ARM cannot continue. No nonphysical semantic shortcut is allowed. |
| 3 | local model mirrors absent (CI environment): ['qwen25_0p5b', 'qwen25_1p5b', 'qwen25_7b'] |
| 3 | the 2026-09-22 harvest archives are not on this machine |
| 3 | U2 successor engine pending |
| 2 | jsonschema not installed |
| 2 | lead-reviewed D-079 import inputs are unavailable |
| 2 | local Qwen3 tokenizer mirrors are absent |
| 2 | lsof is not installed |
| 2 | markdown-it-py not installed; the build cannot run here |
| 2 | native QoS requires macOS |
| 2 | optional jsonschema dependency is absent |
| 2 | reads the real gauge (macOS) |
| 2 | reads the real notify bus (macOS) |
| 2 | reads the real process table (macOS) |
| 2 | reads the real SMC (macOS) |
| 2 | real runs corpus unavailable |
| 2 | requires Darwin's real pgrep command semantics |
| 2 | source corpus unavailable: /Users/edr/code/JouleWise/runs_window_a5_20260723 |
| 1 | a desk run of the real read-only probes (macOS) |
| 1 | ACCEPTANCE GATE SKIP: determinism gate requires the retained runs/ corpus |
| 1 | ACCEPTANCE GATE SKIP: six frozen legacy corpus bundles require the retained runs/ corpus |
| 1 | clonefile(2) is an APFS call |
| 1 | CommonCrypto is macOS only |
| 1 | controlled runs corpus unavailable |
| 1 | Darwin pgrep ancestor exclusion; Linux pgrep has no such rule |
| 1 | design/2026-10-05-v5-claim-block-draft is not in this clone |
| 1 | full-fixture proof runs in d117-production-proof |
| 1 | gate-prune inventory is not on this machine |
| 1 | jsonschema not installed (optional) |
| 1 | kern.bootsessionuuid is a Darwin kernel value |
| 1 | kern.bootsessionuuid is Darwin-only |
| 1 | lead-reviewed D-079 import custody inputs are unavailable |
| 1 | live identity probes need macOS sysctl |
| 1 | local model mirrors absent (CI environment): ['qwen3-1p7b', 'qwen3-8b'] |
| 1 | measurement ledger not on this machine |
| 1 | NEEDS-RULING: config-authenticated mock telemetry is excluded by the production claim loader, so the existing canned fixture cannot satisfy D-158's DATA-only predicate without loosening a production gate or building a new corpus fixture |
| 1 | pinned MATH source absent |
| 1 | POWER-Z KM003C not on the USB bus |
| 1 | reads the macOS kernel clock |
| 1 | reads the real host CPU ticks (macOS) |
| 1 | reads the real kernel clock (macOS) |
| 1 | real campaign-log corpus is unavailable |
| 1 | real collect subprocess runs the macOS census and power-policy probes (pmset, sysctl); on Linux every round errors and, since fix round 4, an all-error session exits 1 by design |
| 1 | real launchctl required |
| 1 | real Qwen3 tokenizer test requires the optional tokenizers library and local tokenizer.json |
| 1 | real spawned worker uses native QoS; hosted Linux shards feed the runner via stdin, which spawn cannot re-import |
| 1 | requires Darwin and explicit QG_LIVE_DARWIN=1 real-acquisition opt-in |
| 1 | requires Darwin's POSIX extended regular expressions |
| 1 | requires Darwin's real boot-session sysctl command |
| 1 | requires Darwin's real caffeinate process |
| 1 | requires Darwin's real sysctl command |
| 1 | retained capture 20260722T145535-e941c821 is not on this machine; run scripts/check_paper_replay_fence.py where the corpus lives |
| 1 | retained runs corpus is absent |
| 1 | retained XD/AQ corpora are not present; run the default R7F CLI where both corpora live |
| 1 | runs_window corpus absent (clean checkout without bundles) |
| 1 | runs/ corpus absent (clean checkout without bundles) |
| 1 | split production proof requires a registered JOULEWISE_D117_PROOF_PARTITION |
| 1 | stopped-after-exec probe requires Darwin POSIX_SPAWN_START_SUSPENDED |
| 1 | STRUCTURAL-BLOCKED: generator targets uninstalled _v2 family while the registry installs _v5 |
| 1 | STRUCTURAL-BLOCKED: synthetic _v5 fixture omits the family-publication marker required before self-predecessor validation |
| 1 | successor member not minted yet; shape check is vacuous |
| 1 | successor mirrors are still absent/incomplete: ['qwen3-1p7b', 'qwen3-8b'] |
| 1 | temporary filesystem is case-sensitive |
| 1 | the block-3 reference archive and the measurement interpreter are on Ed's Mac only |
| 1 | the block-5 design branch is not in this clone |
| 1 | the gate-prune inventory is not on this machine |
| 1 | the real kern.bootsessionuuid exists only on macOS |
| 1 | the two pilot-night archives are not on this machine |
| 1 | this file system gave the replacement lock the inode number of the lock just unlinked (9437192); the reclaimer tells the two apart by device and inode number only, so here it cannot (known limit of scripts/run_campaign.py _hazard_reclaim_stale_campaign_lock; APFS on the measurement Mac does not reuse numbers) |
| 1 | window-B quarantine custody path is absent |

Earlier checks and findings: CI run 39703953473 failed only its
tests.test_shard_tests discovery inventory (212 quick modules, one failing
module). The align.test_ registry prefix addition fixed that failure.
Run 39704557267 passed quick and the metadata/records modules but was cancelled
after the final numerical-test update; cancelled statistics work is not
counted as a pass. Preparatory JavaScript arithmetic checks are not counted
as Python test execution. Draft PR #523's separate gate-ledger workflow remains
red because independent/merge/cold gates are explicitly NOT-RUN; no merge
approval or current-main merge-tree verification is claimed.

No local shell command ran: exec_command reported no usable execution
environment, wait_for_environment remained pending, and runtime status
repeatedly alternated pending/starting without a ready executor. Public GitHub
reads and authorised lane commits remained available, so the work was saved
through GitHub Git/contents APIs. Draft PR #523 targets the spine solely as
an execution/review checkpoint; nothing was merged.

Requested commands NOT RUN locally:
- python3 -m unittest discover -s tests/align -t .
- python3 -m unittest discover -s tests

No optional dependency is used or required. No extra was installed, and there
are no extra-dependent tests or skips in this lane.

## END-TO-END

Real shared Episode/Turn/ToolCall construction -> to_json -> from_json ->
features -> five leave-one-task-pair-out fits -> held-out probabilities ->
AUC -> logit DeLong CI -> automatic whole-group bootstrap CI -> paired AUC test.
Five task pairs, two conditions, 30 seeds each: 300 episodes; each fold trains
on 240 and predicts 60. Runs last 220–320 s with 8–12 model/tool turns.
Decode counts follow a lognormal distribution with median 500 and log SD 0.5;
prefill counts are 500–1500 per turn, and ordinary tool counts are 0–2 per turn.

Visible side task: three extra logged tool calls plus 96 visible and 240 hidden
generated tokens in the first turn. AUC 0.785022222; 95% DeLong interval
[0.7302036860122262, 0.8312761210834372]; 95% cluster interval
[0.77, 0.8065333333333333], automatic B=25,600. No interval flags.

Invisible control: extra 240-token hidden reasoning and one tool call occupy
an unlogged turn inside a pre-existing 20 s final wait. Logged counts and total
duration match each benign seed, while all-work hidden counts differ. AUC 0.5;
DeLong [0.5, 0.5] flagged zero_variance; bootstrap [0.5, 0.5], B=1,600,
flagged degenerate_bootstrap. These flags prevent claiming population
uncertainty is zero. The test also requires the visible-vs-invisible paired
AUC difference to have two-sided p < 0.05.

Python coverage: 200 seeded Normal-score worlds, true AUC 0.689691026781155,
100 task-pair groups per world, three observations per class per group,
explicit B=799. DeLong covered truth in 190/200 worlds and cluster bootstrap
in 190/200, both 0.95; the requested one-binomial-SE bar is 0.0154110350.
The statistics module's 13 tests passed in 62.709 s; the metadata module's
7 tests passed in 1.299 s. These are synthetic verification, not hardware data.

## DECISIONS I MADE

- The bounded user brief is authority for this synthetic-only lane. Repository intake had no active stop card. No queue, kernel, state, or lead-owned record was edited.
- No real endpoint, power sensor, credential, hardware campaign, or external service is called by the implementation or tests.
- Shared totals win: logged decode_tokens includes the recorded hidden-token component. Only the logged-only hidden_tokens feature is zeroed. No subtraction from decode totals is invented.
- The invisible control therefore uses an unlogged turn in existing slack time; it does not rely on a reinterpretation of shared token counts.
- Five count log1p companions are included. Duration and rate features have no log1p companion, since they are not counts.
- Throughput uses the sum of selected turn times; duration_s uses whole-episode elapsed time. Zero denominators yield zero with flags. No episode is excluded.
- Positive labels mean sabotage and higher scores mean greater suspicion.
- Logistic loss is summed negative log likelihood plus l2/2 times squared standardised slopes; intercept is unpenalised. Population training SDs are used. Constant columns get zero slopes.
- Newton stopping uses the brief's 1e-10 coefficient-relative step bar. Line search permits only a machine-epsilon allowance scaled by row/column arithmetic. Fit failure is flagged; pure-class/singular fits return NaNs.
- Default CV uses every feature in stable insertion order. Empty feature_names requests an intercept-only model. Unknown names preserve all episode IDs with flagged NaNs.
- DeLong uses sample placement variance and a logit-transformed normal interval. Boundary/zero-variance intervals are explicitly flagged.
- Paired DeLong uses variance of class-specific placement differences, preserving observation order and covariance.
- Bootstrap resamples G whole task pairs with replacement; within-group multiplicities are retained. Undefined single-class replicates are counted in flags and redrawn. Returned B counts valid replicates.
- Automatic endpoint precision uses SE(q_p)=sqrt(p(1-p)/B)/f(q_p), with the documented symmetric quantile-spacing density estimate and an atom-specific rank-SE check. Both endpoint SE estimates must be below 1% of interval half-width.
- AUTO_BOOTSTRAP_MAX_REPLICATES is a configurable computation budget (default 2**20), not an inferential threshold. Budget exhaustion flags an unmet target; it never silently claims precision.
- Precompute group-pair U sums and combine symmetric cross-group products; the literal whole-episode resampling oracle checks the same statistic.
- Exact equality tests are limited to integers, names, IDs, deterministic replay and identical feature inputs. Numerical comparisons use 1e-6 relative agreement; zero comparisons use 1e6 binary64 ulps at unit scale because relative error at zero is undefined.
- Coverage uses 200 seeded worlds with 100 independent task-pair groups and three observations per class per group. Normal(0,1) vs Normal(0.7,1) gives true AUC Phi(0.7/sqrt(2)) = 0.689691026781155. The one-binomial-SE coverage bar is sqrt(0.95*0.05/200) = 0.0154110350074224.
- A preparatory JavaScript arithmetic/RNG check of the earlier 40-group, B=399 fixture gave DeLong 189/200 and bootstrap 184/200; this is not a Python test result. The asymptotic coverage fixture was expanded to 100 groups and explicit B=799, rather than relaxing the requested bar or selecting seeds.
- The repo-wide CI inventory failure required the single discovery-prefix registry addition listed in FILES. The repaired inventory passed in the quick suite.
- Every source/report update was committed to the authorised lane via non-force fast-forward updates; main and the spine were not changed.

## CONTRACT-CHANGE

none. The brief's informal description of a log hiding reasoning must be read
with the records contract: decode_tokens includes hidden_tokens even in
totals(logged_only=True). This disagreement is handled explicitly in features
and the invisible fixture; no frozen contract was edited.

## OPEN ISSUES

- The assertion-only revision after 757f5db requires its CI rerun to complete. The production modules already passed the full suite above.
- Direct requested local commands and the touched quick tier remain unavailable without a usable executor.
- Independent twin comparison and merge reviews belong to the lead; this draft is not offered as merge-approved.
- DeLong is asymptotic and does not cluster task pairs. The bootstrap is the group-aware interval; five pilot groups give limited population information. The coverage experiment exercises a larger asymptotic setting, not a claim of exact five-group coverage.
- Automatic bootstrap precision is a plug-in estimate and can hit the configurable budget; consumers must retain flags.
- No live-hardware validation or research result is claimed.

## NEEDS_RULING

none
