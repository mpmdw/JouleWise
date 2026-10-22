# align-residual lane report

## SUMMARY

Round 2 is in progress from 971b2f31c7d7cf4c4e4603c6c098184e2b910121.
The VM remains pending/starting and offline; no local round-2 execution yet.


- Round-1 fixes are saved on lane/2026-10-21-align-residual.
- Excludes unusable fit rows and held-out scores with counted flags.
- Prediction uses shared parameter covariance plus n*sigma2; episode uncertainty is added once.
- Fits identifiable columns, while retaining the five-feature public model.
- Unidentified decode energy gives flagged NaN H_min without disabling scores.
- Model flags no longer add a dataclass constructor field.
- Calibration is iid; Monte Carlo tests use the lead's four-standard-error bars.
- Adds review-world exclusion identities and an M3 variance mutation regression.
- CI ran all three residual modules: 26 tests, no failures/errors, one optional NumPy skip.
- Local commands, independent-twin agreement and reviewer probes remain blocked by offline startup.

## FILES

- joulewise/align/energy_residual.py: WLS, subset identification, exclusion counts,
  separate-integral prediction, score, grouped quantile and hidden-token power.
- tests/align/test_energy_residual.py: ruled episode physics/formula, missing
  attribution score identity and five-field dataclass round trip.
- tests/align/test_energy_residual_power.py: iid calibration, conditional theories
  using true-turn variance, and four-SE Monte Carlo bars.
- tests/align/test_energy_residual_regressions.py: 7910-row reviewer-world
  exclusions/identities, independent three-column OLS and M3 variance regression.
- docs/align/energy_residual.md: corrected formulas, flags, reduced designs,
  caller uncertainty contract and unchanged re-derived planning examples.
- .codex-report/align-residual.md: this report.
- No registry edits this round; tests/test_shard_tests.py remains unchanged.

## PUBLIC API

The required public signatures and five EnergyModel fields are unchanged:

```python
TurnRow(episode_id: str, group: str, context_tokens: int, prefill_tokens: int,
        decode_tokens: int, duration_s: float, energy_j: float,
        energy_half_width_j: float)
EnergyModel(names: tuple[str, ...], coef: tuple[float, ...],
            cov: tuple[tuple[float, ...], ...], sigma2_per_turn: float, n_turns: int)
design_row(r: TurnRow) -> list[float]
fit_energy_model(rows: Sequence[TurnRow]) -> EnergyModel
predict_episode(model: EnergyModel, rows: Sequence[TurnRow]) -> tuple[float, float]
residual_score(model: EnergyModel, logged_rows: Sequence[TurnRow],
               measured_total_j: float, measured_half_width_j: float) -> float
grouped_benign_threshold(
    benign: Mapping[str, tuple[Sequence[TurnRow], float, float]], *, alpha: float
) -> float
min_detectable_hidden_decode_tokens(
    model: EnergyModel, logged_rows: Sequence[TurnRow], *, alpha: float,
    power: float, measured_half_width_j: float
) -> float
turn_rows_from_episode(
    episode: Episode, turn_energy: Mapping[int, tuple[float, float]]
) -> tuple[TurnRow, ...]
```

Read .flags before arithmetic, comparison, JSON encoding or field-only model
copies; float/tuple diagnostics do not survive these operations.

## TESTS RUN

The selected cloud environment has remained offline, cycling pending/starting.
Terminal execution of even pwd is rejected with:
"No usable execution environment is available. Wait for an environment to become
available before using this tool." There has been no usable executor this round.
No local package installation, checkout, file staging, or local test run is claimed.
Commits are fast-forward updates through connected GitHub tools; only named
in-scope paths are in the trees. No probe or twin file is committed.

### Executed CI evidence

Run 39717562529 at 1b306448e8d36522ff20beba2728d1097eafe394:
https://github.com/mpmdw/JouleWise/actions/runs/39717562529

All three residual test modules executed on Python 3.13:
26 tests, 0 failures, 0 errors, 1 skip, total module runtime 38.004 s.

| Module | Tests | Skips | Runtime s |
| --- | ---: | ---: | ---: |
| tests.align.test_energy_residual | 13 | 1 | 0.375 |
| tests.align.test_energy_residual_power | 6 | 0 | 22.550 |
| tests.align.test_energy_residual_regressions | 7 | 0 | 15.079 |

Only skip: "NumPy optional WLS reference absent". No extra-dependency run has
been possible because there is no local executor and CI installs no extras.
CI build, fences, installed-wheel and quick passed. The remainder of CI was
still running when this checkpoint was prepared; no full-suite pass is claimed.
No whole-repository suite was launched locally.

The existing CI ordinary-shard command that executed these modules is:

```bash
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
    partitions, weights, count, unknown_weight=unknown
)
print("ORDINARY SHARD ESTIMATES", ",".join(f"{value:.3f}" for value in totals))
index = int(os.environ["SHARD_INDEX"])
raise SystemExit(shard_tests.run_units(partitions[index - 1], count, index))
PY
```

SHARD_COUNT=12; residual regression, base and power modules were in
SHARD_INDEX=5, 9 and 8 respectively. This is CI evidence, not the requested
local discovery command.

### Required commands still NOT-RUN

Counts/skips for these commands are unavailable because execution never started.
Run from /workspace/JouleWise after startup and checkout of this lane:

```bash
python3 -m unittest discover -s tests/align -t .
python3 -m unittest tests.test_shard_tests
```

Both are still required once with the fetched twin files and once without them.
Also run the stdlib-only discovery with site packages disabled:

```bash
python3 -S -m unittest discover -s tests/align -t .
```

Run the following once on the twin agreement file exactly as fetched, record
the old-R6 failures, then apply only the local uncommitted diff in OPEN ISSUES
and rerun. Neither execution has occurred this round:

```bash
python3 -m unittest tests.align.test_twin_residual tests.align.twins.test_residual_twin_selfcheck -v
```

These reviewer probe commands are also NOT-RUN; the appendix scripts have been
prepared in session memory, but cannot be written into the unavailable checkout:

```bash
python3 /workspace/JouleWise/review_repro/resid_world.py
python3 /workspace/JouleWise/review_repro/resid_edges.py
python3 /workspace/JouleWise/review_repro/resid_e2e.py detect
python3 /workspace/JouleWise/review_repro/m3_power.py m3max
python3 /workspace/JouleWise/review_repro/m3_power.py nvml8b
python3 /workspace/JouleWise/review_repro/r6_mag.py
python3 -c "import sys,dataclasses; sys.path.insert(0,'/workspace/JouleWise'); from joulewise.align import energy_residual as L; m=L.fit_energy_model([]); print((m.sigma2_per_turn+0), getattr(abs(L.grouped_benign_threshold({},alpha=.05)),'flags','LOST')); L.EnergyModel(**dataclasses.asdict(m))"
```

Extend the uncommitted resid_edges.py after its verbatim run to print case 8's
grouped threshold and H_min, as the brief requests. Fetch/materialize the four
twin files by the brief's exact git commands; do not commit them or the probes.

## END-TO-END

CI executed the regenerated worlds through the real API. Each measured turn
is true model energy plus intrinsic deviation plus independent turn sensor
noise; the episode total is true turn energies plus independent episode noise.
The shared Episode/Turn/ToolCall adapter, synthetic 100 ms cumulative trace,
fit, prediction and scoring paths all execute in the base end-to-end test.
No live attribution/hardware result is claimed.

Coverage uses the same 512 seed values with regenerated iid noise. The mean
printed standard errors and one-SE coverage were:

| feature | mean SE | coverage | previous coverage | change |
| --- | ---: | ---: | ---: | ---: |
| intercept | 1.05944 | 0.6855 | 0.6758 | +0.0097 |
| prefill | 0.00195808 | 0.6777 | 0.6504 | +0.0273 |
| decode | 0.00395628 | 0.6758 | 0.6758 | 0.0000 |
| context-decode | 2.83081e-7 | 0.6719 | 0.6504 | +0.0215 |
| context-prefill | 1.51605e-7 | 0.6953 | 0.6680 | +0.0273 |

The nominal coverage is 0.6827, with four-SE bar about 0.082. Mean-bias checks
also pass. Compared with the old SEs (1.05720, 0.00195089, 0.00394253,
2.81740e-7, 1.50855e-7), the printed SE changes are +0.00224,
+0.00000719, +0.00001375, +1.341e-9, +7.50e-10 respectively.
These changes reflect the required regenerated noise, not changed seed values.

Calibration/evaluation budgets increased from 400/1000 to 1000/2000 iid
episodes, or 20000/40000 turns. The power module took 22.550 s in CI.
Threshold moved from 1.668333 (stratified world) to 1.666926 (iid world),
a change of -0.001407. FP and zero-energy control both give exactly
107/2000=0.053500, formerly 53/1000=0.053000: +0.000500 in rate.
The combined FP SE is 0.008441; four SE are 0.033764.

| H/H_min | mean integer H | detection | conditional theory | normal approximation |
| --- | ---: | ---: | ---: | ---: |
| 0.0 | 0.000 | 0.0535 | 0.0468 | 0.0478 |
| 0.5 | 158.520 | 0.3650 | 0.3689 | 0.3712 |
| 1.0 | 304.660 | 0.8280 | 0.8159 | 0.8165 |
| 1.5 | 452.330 | 0.9895 | 0.9841 | 0.9841 |
| 2.0 | 599.520 | 1.0000 | 0.9997 | 0.9996 |

From the previous printed table, mean H changes at ratios .5/1/1.5/2 are
-1.580/-4.600/-6.730/-9.120 tokens. Detection-rate changes across all five
ratios are +0.0005/-0.0130/+0.0150/+0.0035/0.0000. Conditional theory changes
are -0.0018/+0.0006/+0.0020/+0.0008/+0.0001; normal-approximation changes
are +0.0002/+0.0033/+0.0007/+0.0002/0.0000. These are comparisons of
different mandated worlds/budgets; they do not isolate just the R6 term.

Deletion of 1/2/4 early turns gives observed rates 0.6400/0.9785/1.0000,
conditional theory 0.6263/0.9767/1.0000; the measured total keeps every
deleted turn's intrinsic variance. Previous observed rates were
0.6170/0.9720/1.0000, changes +0.0230/+0.0065/0.0000. Theory changes from
0.6108/0.9729/1.0000 are +0.0155/+0.0038/0.0000.

The separate M3 calibration/evaluation world has 300/1000 episodes,
coefficients (1, .0004, .35, .15/4096, 5e-8), extra turn sd .5 J,
turn half-widths .3-1.2 J and episode half-width 1 J. New score sd 0.968609
passes 1 +/- 0.089487; applying the pre-fix formula on the same fitted world
gives 0.547801, a +0.420808 correction and an explicit failed mutation.

The reviewer's 300-episode, 7910-row world executes in the regression suite:
one invalid turn fits identically to the other 7909 rows; an empty episode
leaves the threshold bit-identical; a failed total yields exactly the real
ceil(.95*299)-th finite held-out score; all 1000 +500 J evaluation episodes
are flagged. Independent three-column OLS, identifiable covariance embedding,
constant-decode H_min, and all unusable fit-field checks pass.

The prior report's example model coefficients, sigma2 and counter-world
mean/sd/H_min were tied to the old stratified world and are retired. They
have not been reprinted here without execution of an equivalent new diagnostic.
The separate appendix probes and twin comparisons are still blocked, so their
expected outputs from the brief are not represented as observed results.

The doc's planning arithmetic was independently re-derived in binary64 using
unrounded z_0.95 and z_0.8. (D J, H_min tokens):
M3 Max (2.457641, 12.221726); NVML (56.603887, 70.372071);
NVML with 25 phase repetitions (24.738634, 30.755995).
All moved by 0 at six-decimal printed precision.

## DECISIONS I MADE

- FIX ROUND 1 supplies all requested scientific rulings; no new ruling needed.
- Read the existing lane report, PIPELINE.md, records.py and interfaces.py
  before preparing changes; the three frozen files remain unchanged.
- Root AGENTS/M0 intake is read-only under this exhaustive write scope.
  No active stop card; no hardware task selected. No whole-repository suite.
- The existing branch was 5e37d2bf5034dc1c7ed57e8cc75c896046bfc83c.
  Cloud startup remains pending/starting and offline, so the first two
  fast-forward commits were saved with connected GitHub tools on that branch.
- Exclusion flags are excluded_turn_rows=N, excluded_empty_episodes=N and
  excluded_heldout_scores=N. Explanatory flags remain on the returned result.
  Bad episode totals do not remove separately measured turns from other folds.
- Half-widths are standard uncertainties. Duration is diagnostic only.
- Select columns once in contract order on the unweighted scaled design.
  Use scaled Householder QR in WLS and n-p_kept moment degrees of freedom.
  Keep the existing sqrt(epsilon) moment bar, QR roundoff rank bar, variance-ULP
  limiting weight, mant_dig+1 iteration cap and covariance roundoff clamp.
- Unidentified coefficients/covariance rows are exactly zero with named flags.
  An unidentified decode coefficient makes H_min undefined, not the scores.
- The lead ruled prediction variance s'cov s+n*sigma2; the separate episode
  integral contributes its uncertainty exactly once through residual_score.
- The lead ruled iid calibration and four-SE Monte Carlo comparisons, replacing
  stratification, one-SE FP bars and 95% family bars before seeing new outputs.
  Budgets m=1000, n=2000 resolve FP departures of 0.0338 (0.0516 at m=400,n=1000);
  coverage at 512 seeds resolves 0.082 and catches factor-two covariance errors.
- Preserve type-1 empirical quantiles, strict greater-than detection,
  whole-pair holdouts and connected holdouts for mixed-group episodes.
- Preserve shared-record hidden/deleted token semantics in the lane adapter.
- Model flags are a plain subclass attribute, not a dataclass field.
- Planning coefficients, power-gap variation, phase independence and quantum
  remain labelled assumptions; conventional alpha=.05/power=.8 and about 1 J
  M3 attribution limit remain explicit. No hardware finding is claimed.

## CONTRACT-CHANGE

No shared-file modification. Desired future contract: typed diagnostics results,
so callers cannot silently lose flags through arithmetic, comparisons or JSON.
The records contract's construction errors still win over the general flag
doctrine; no shared record behavior is altered.

## OPEN ISSUES

- Required local commands and probes remain blocked by offline environment
  startup; CI's passing residual modules do not replace these requested runs.
- The independent twin needs RES-R1-01 counted exclusions and preservation of
  separately measured rows when an episode total is unusable.
- The independent twin needs RES-R1-03 identifiable subset fitting, reduced
  degrees of freedom, zero embedded coefficients/covariance and H_min flags.
- The twin agreement file's old R6 correction must compare with the plain twin.
  The exact proposed local diff follows; it has NOT been executed or applied in
  a checkout this round. The original identity assertion adds sum(h_i^2), and
  the helper adds that term in the score/power and grouped-threshold tests.
  The expected old-R6 tests are test_predict_episode_r6_identity,
  test_score_and_power_agree_under_reconciled_r6, and
  test_grouped_threshold_agrees_under_reconciled_r6; their actual failures and
  the patched 31-test result still require execution. The lead can apply this
  diff to the twin branch; no twin file/branch is changed by this lane.

```diff
--- a/tests/align/test_twin_residual.py
+++ b/tests/align/test_twin_residual.py
@@ -94,9 +94,8 @@
 
 
 def _twin_predict_lane_r6(model, rows):
-    """Twin predict_episode with the lane's R6 term (sum h_i**2) added; nothing else changed."""
-    mean, sd = _TWIN_PREDICT(model, rows)
-    return mean, math.sqrt(sd * sd + math.fsum(float(r.energy_half_width_j) ** 2 for r in rows))
+    """The lead ruled R6 as the twin's existing whole-episode-integral variance."""
+    return _TWIN_PREDICT(model, rows)
 
 
 _TWIN_PREDICT = T.predict_episode
@@ -148,14 +147,13 @@
                 mean_t, sd_t = T.predict_episode(mt, rt)
                 # The mean has a printed uncertainty (the sd): 1% of the smaller sd.
                 self.assertLessEqual(abs(mean_l - mean_t), 0.01 * min(sd_l, sd_t), (eid, mean_l, mean_t))
-                # R6: the lane's variance exceeds the twin's by exactly sum(h_i**2)
-                # of the scored rows. No printed uncertainty on a variance: 1e-6 relative.
-                h2 = math.fsum(s[7] ** 2 for s in ep_specs)
-                self.assertTrue(_close(sd_l ** 2, sd_t ** 2 + h2), (eid, sd_l ** 2, sd_t ** 2, h2))
+                # Ruled R6: both use s'cov s + n*sigma2 for a separate integral.
+                # No printed uncertainty on a variance: 1e-6 relative.
+                self.assertTrue(_close(sd_l ** 2, sd_t ** 2), (eid, sd_l ** 2, sd_t ** 2))
                 # Same model into both (duck-typed): isolates predict from fit.
                 mean_x, sd_x = T.predict_episode(ml, rt)
                 self.assertTrue(_close(mean_l, mean_x), (eid, mean_l, mean_x))
-                self.assertTrue(_close(sd_l ** 2, sd_x ** 2 + h2), (eid, sd_l, sd_x))
+                self.assertTrue(_close(sd_l ** 2, sd_x ** 2), (eid, sd_l, sd_x))
 
     def test_score_and_power_agree_under_reconciled_r6(self):
         with mock.patch.object(T, "predict_episode", _twin_predict_lane_r6):
```
- Read and persist numeric/sequence flags before operations that lose them.
- Linear/Gaussian/independent-error assumptions await a hardware pilot.
- PR #525 remains draft; CI does not replace the lead's merge/review authority.

## NEEDS_RULING

none

## FIX LOG

- RES-R1-01 fixed 50075672d7a0f248a4f26b5bf282996be668a323; regression cases in 1b306448e8d36522ff20beba2728d1097eafe394.
- RES-R1-02 fixed 50075672d7a0f248a4f26b5bf282996be668a323; M3 regression and documentation in 1b306448e8d36522ff20beba2728d1097eafe394.
- RES-R1-03 fixed 50075672d7a0f248a4f26b5bf282996be668a323; reduced-design regressions in 1b306448e8d36522ff20beba2728d1097eafe394.
- RES-R1-04 fixed 50075672d7a0f248a4f26b5bf282996be668a323: iid calibration and the lead's four-SE bars.
- RES-R1-05 fixed 50075672d7a0f248a4f26b5bf282996be668a323: flags are not dataclass fields; diagnostic-loss limits documented.
- N1 fixed 50075672d7a0f248a4f26b5bf282996be668a323: retained sqrt(epsilon), with n-p_kept moment degrees of freedom.
- N2 fixed 50075672d7a0f248a4f26b5bf282996be668a323: extended the QR roundoff derivation to column identifiability.
- N3 fixed 50075672d7a0f248a4f26b5bf282996be668a323: retained the variance-ULP limiting-weight derivation.
- N4 fixed 50075672d7a0f248a4f26b5bf282996be668a323: retained the binary-mantissa iteration-cap derivation.
- N5 fixed 50075672d7a0f248a4f26b5bf282996be668a323: retained the 25-product covariance roundoff-clamp derivation.
- N6 fixed 50075672d7a0f248a4f26b5bf282996be668a323: four combined SEs on iid calibration and evaluation.
- N7 fixed 50075672d7a0f248a4f26b5bf282996be668a323: retained 0.004 J as 1% of the smallest printed 0.4 J half-width.
- N8 fixed 1b306448e8d36522ff20beba2728d1097eafe394: every planning number remains labelled as an assumption or parameter.
- N9 fixed 1b306448e8d36522ff20beba2728d1097eafe394: re-derived all three examples, unchanged at six decimals.

### Round 2

Implementation and regression work in progress. No round-2 test or repro has run.
