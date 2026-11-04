# ALIGN desk attention alternative

Built from `45b47f7b69389e9fb9672c951e3dd0fcf1740b95` on
`lane/2026-11-04-align-desk-attention`. Early visibility commit `0eecb5a8f`
was pushed before implementation. Linux / Python 3.13; desk-only, synthetic-only.
No raw measurement data, model execution or hardware work was available or used.

## Delivered

- An opt-in `sequence` energy design with the original five coefficient slots:
  `[1, P, D, (C+P)*D+D*D/2, C*P+P*P/2]`. Registered remains the default.
  Model names select prediction/scoring/power arithmetic; grouped calibration
  accepts the same design selector. Unknown names are flagged and refused.
- A separate `alternative_residual_analysis` with configuration-separated,
  per-pair and pooled fits under both count conventions and both designs.
  It reports cell-centered s_r with realized df, e and fitted SE, benign
  trajectory-LOO scores, sabotage full-fit scores and full known-H curves.
- Per-pair type-1 95% benign LOO thresholds; strictly-above crossings report
  their first k and H. `above_at_H0` never contributes to detections.
- Fold-specific per-turn P/C/D support maxima, turn-count ranges and every
  exceeding scored turn. `out_of_support` is disclosure only.
- Standalone `scripts/align_pilot_alt_desk.py`, reading only PILOT members,
  session-prefixing run IDs, preserving trajectory keys, and keeping the first
  eligible representative in input order. JSON retains witnesses and stdout
  prints plain tables. No existing desk entry point or output was changed.
- Synthetic tests and the two requested documentation addenda.

Only the eight authorized paths were edited. No registry, inventory, fence,
fixture, project-state file or other out-of-scope path needed changes.
`NEEDS_RULING`: none.

## Decisions I made

1. Public design selectors are `registered` and `sequence`; names are exported
   as `REGISTERED_NAMES` and `SEQUENCE_NAMES`. Sequence attention names are
   `sequence_decode_attention` and `sequence_prefill_attention`. JSON-restored
   name lists match the corresponding tuple; unrecognized names produce NaN
   with `invalid_model_names`. The base actually accepted arbitrary five-column
   names, contrary to the brief's “refused as now”; its contradictory test was
   replaced to implement the explicit requested refusal. Recognized registered
   models retain their outputs exactly.
2. Sequence e uses mean C+P+D across benign training turns, with the same linear
   combination of fitted covariance for its SE. Both H APIs use the mean of
   the supplied logged turns and a local linear marginal-energy approximation;
   they do not solve a finite-H quadratic. The halves are D²/2 and P²/2 exactly
   as specified, without a discrete-token minus-one correction.
3. Retain all three existing eligibility views (registered, episode-scope
   alternative, all-member diagnostic), with first eligible trajectory wins in
   each. Replays never train a second fold. Pair groups use only that pair;
   pooled groups are explicitly labelled diagnostics. No eligibility changes.
4. As in the existing residual desk, s_r centers within block/pair/condition
   cells and pools SS with df=sum(n_cell−1). New thresholds use finite benign
   trajectory-LOO scores in the reported population, rather than the registered
   leave-task-pair-out rule. Nonfinite calibration scores remain disclosed.
5. Both benign-fit conventions show the same logged-to-withheld known-H curve.
   `tamper_starting_log=counts_logged` is explicit: for a counts-withheld fit,
   its full-fit sabotage score is the curve endpoint, not k=0. No double
   subtraction of already-withheld counts. Measured energy and C/P stay fixed.
6. Support is measured against the actual fold's training for benign scores,
   and the full benign training population for sabotage/tamper. Turn-count
   range departure is reported separately; `out_of_support` denotes a turn
   exceeding a P/C/D maximum. It changes no score, threshold or crossing.
7. Session labels come from the session directory above `inspection/PILOT.json`,
   the containing directory for other `PILOT.json` paths, or the filename stem
   for other JSON paths. Duplicate labels fail clearly; reference input first.
8. The final metadata commit pins a preceding implementation freeze commit.
   This avoids an impossible self-referential commit hash; subsequent changes
   are the literal header/protocol pin and this report, not estimator changes.

## Verification evidence

The exact base source was loaded with `git show 45b47f7b6:...` into an in-memory
module, then compared with current code on the existing 16-episode fixtures.
Registered model fields/flags, predictions, residual scores, thresholds and both
power APIs matched exactly. The original `residual_analysis` source is an
unchanged prefix of the file, and its serialized output on 24 PILOT-shaped
synthetic members matched byte-for-byte. SHA-256:
`a7d2b8da6f86eeeabde3ef941212f0ebf6dff6ace9de4a2ed73ad28005b3df11`.

Noiseless 10–12-turn sequence-law episodes use C=0 at turn 0 and token ranges
P=25–20,000, C=0–26,000, D=2–3,700 with small positive turn half-widths (0.01 J).
Maximum relative coefficient error: `3.712585794346523e-14` (bar 1e-6 relative).
Registered misspecified per-turn residual SD: `171.33971174146453 J`;
episode residual SD: `431.71828181376486 J`, both above the 1 J attribution limit.
These are synthetic validation results, not pilot-7 or hardware results.

Member-shaped tests cover two configurations, both pairs and conditions, sampled
and greedy identities, a replay with deliberately corrupted energy that must
never enter training, both quantile-at-maximum and m=21/rank=20 thresholds,
H0 nondetections, actual post-H0 crossings, exact H accounting, per-turn
out-of-range flags without numeric changes, missing-fit JSON, and multi-session
reference-first pooling through the real CLI.

The full repository suite was deliberately not run: the brief limits local runs
to the two touched modules and five named regression modules; CI owns the rest.

## Freeze, test commands and signature changes

Implementation freeze pushed to origin:
`4d54cb47bb7ba0c267138a57de747a7183ca23ff`.
The following metadata/report commit pins this hash in the printed header and
protocol; its final tip is supplied in the handoff, without a self-reference in
its own contents. `git diff --check` passed (empty output). Remote source-freeze
verification (`git ls-remote origin refs/heads/lane/2026-11-04-align-desk-attention`)
returned the full hash above.

Each test invocation used the exact environment assignments below and a new
`mktemp -d`. Python bytecode writes were disabled to preserve the write scope.

Focused command, run initially, after assertion refinements, and after the final
freeze pin (the last invocation verifies the final source):

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d) python3.13 -m unittest tests.align.test_energy_residual tests.align.test_align_pilot_alt_desk
```

Outputs (progress dots omitted):

```text
----------------------------------------------------------------------
Ran 26 tests in 16.023s

OK
```

```text
----------------------------------------------------------------------
Ran 26 tests in 20.595s

OK
```

```text
----------------------------------------------------------------------
Ran 26 tests in 19.609s

OK
```

Authorized regression command (core estimator code unchanged afterward; only
additional assertions, session-path normalization, docs and the literal freeze
pin were refined and verified by the final focused run):

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d) python3.13 -m unittest tests.align.test_energy_residual tests.align.test_align_pilot_alt_desk tests.align.test_energy_residual_power tests.align.test_energy_residual_regressions tests.align.test_twin_residual tests.align.test_pilot4 tests.test_align_pilot_session
```

Output (progress dots omitted; stdout/stderr retain the runner's displayed order):

```text
----------------------------------------------------------------------
Ran 85 tests in 395.905s

coefficient true mean_se coverage expected
0 5 1.05944 0.6855 0.6827
1 0.005 0.00195808 0.6777 0.6827
2 0.12 0.00395628 0.6758 0.6827
3 1e-05 2.83081e-07 0.6719 0.6827
4 4e-06 1.51605e-07 0.6953 0.6827

deleted_turns observed theory binomial_SE
1 0.6400 0.6263 0.00991
2 0.9785 0.9767 0.00321
4 1.0000 1.0000 0.00001
benign threshold=1.666926, FP=107/2000=0.053500, SE=0.008441

H/Hmin mean_H observed conditional_theory normal_approx binomial_SE
0.0 0.000 0.0535 0.0468 0.0478 0.00472
0.5 158.520 0.3650 0.3689 0.3712 0.01078
1.0 304.660 0.8280 0.8159 0.8165 0.00866
1.5 452.330 0.9895 0.9841 0.9841 0.00279
2.0 599.520 1.0000 0.9997 0.9996 0.00042
zero-energy hidden control: 107/2000 = 0.053500
unowned tool world m=600, n=2000: normal-theory H median=115.7, detection=0.4835; calibrated H median=177.3, detection=0.7835; power=0.8, bar=0.064122
control: m=600, mean=+0.0058, sd=0.9954, flags=()
large unowned: m=600, mean=+15.7163, sd=4.2549, flags=('benign_score_calibration_departure',)
8% intrinsic noise: m=600, mean=-0.0077, sd=1.1699, flags=('benign_score_calibration_departure',)
tool (0.5, 0.5, 0.5), owned=True: threshold=1.5929, mean=-0.0051, sd=0.9887, flags=()
tool (0.5, 0.5, 0.5), owned=False: threshold=3.4850, mean=+1.6538, sd=1.0882, flags=('benign_score_calibration_departure',)
tool (2.0, 1.0, 1.0), owned=True: threshold=1.5518, mean=-0.0250, sd=0.9745, flags=()
tool (2.0, 1.0, 1.0), owned=False: threshold=7.0686, mean=+4.5708, sd=1.5617, flags=('benign_score_calibration_departure',)
scratchpad subtracted: sigma2=2730.298, decode=0.23452, threshold=1.5943; counted: sigma2=8.725, decode=0.24996, threshold=1.7775
M3 separate integral: sd=0.968609, pre-fix sd=0.547801, bar=1 +/- 0.089487

round-3 fit/predict/score/H_min agreement, worst: {'coef/SE': 6.189604957667757e-09, 'sigma2 rel': 2.448978404181153e-07, 'corr abs': 7.496940845896916e-10, 'mean/sd': 2.3059103124355823e-09, 'H rel': 5.032789278401282e-08}

round-3 threshold/H_cal agreement: departure states {True: 3, False: 6} worst H_cal rel 1.6328478986181491e-07

OK (skipped=1)
```

The skip is the pre-existing `pinned SHADE cache is not installed` check; no
production data or SHADE cache was installed. All other checks passed.

Every pre-existing production function whose signature changed (no others):

- `design_row(r: TurnRow, *, design: str = "registered") -> list[float]`
- `fit_energy_model(rows: Sequence[TurnRow], *, uncertainty_kind: str | None = None, design: str = "registered") -> EnergyModel`
- `grouped_benign_threshold(benign: Mapping[str, tuple[Sequence[TurnRow], float, float]], *, alpha: float, design: str = "registered", uncertainty_kind: str = "standard_uncertainty") -> float`
- `_bad_model(n: int, flags: Sequence[str], *, names: tuple[str, ...] = _NAMES) -> EnergyModel` (private)

New functions are `_design_names`, `_model_design`, `mean_decode_attention`,
`_alternative_support`, `alternative_residual_analysis`, and the new script's
`load_members`, `_number`, `print_tables`, `main`. Existing prediction, scoring,
and both power-function signatures did not change. `residual_analysis` did not
change in source or signature.

Commit hash pushed (implementation source freeze):
`4d54cb47bb7ba0c267138a57de747a7183ca23ff`.
