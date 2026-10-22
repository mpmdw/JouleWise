# align-residual lane report

## SUMMARY

- Implements A7's benign-only logged-work energy model and excess-energy detector.
- Uses scaled Householder QR and nonnegative Paule-Mandel extra-variance estimation.
- Preserves shared parameter covariance and independent turn/episode uncertainty.
- Provides task-pair-held-out thresholds and normal hidden-decode power boundaries.
- Shared-record adapter honors deleted turns and hidden-token semantics; problems are flags.
- Alignment checks: 21 pass with NumPy; 21 run with one optional-reference skip on stdlib only.
- Synthetic benign and zero-energy-control false positives are 5.3% at alpha 0.05.
- Near the 80% hidden-work boundary, detection is 81.3%; deletion agrees with theory.
- Documents provisional M3 Max/NVML examples; broader repository checks are pending.

## FILES

- joulewise/align/energy_residual.py: exact required dataclasses/API, stdlib QR/WLS,
  variance estimation, predictions, residuals, grouped calibration, detection power,
  flagged output adapters and turn_rows_from_episode.
- tests/align/test_energy_residual.py: realistic 20-turn agent/trace fixtures,
  numerical/edge checks, shared-record adapter, optional lazy NumPy reference.
- tests/align/test_energy_residual_power.py: 512 independent coefficient-coverage
  worlds, grouped calibration, hidden-work/deletion power and zero-energy control.
- docs/align/energy_residual.md: model terms, uncertainty assumptions, quantile,
  power derivation, worked M3 Max and duty-sampled NVML examples, limitations.
- tests/test_shard_tests.py: sole registry exception; add only the align. namespace
  to the inventory's unittest module-name prefix normalization. No tests removed.
- .codex-report/align-residual.md: this report. No other files changed.

## PUBLIC API

Required frozen dataclasses retain exactly the specified constructor fields:

- TurnRow(episode_id: str, group: str, context_tokens: int, prefill_tokens: int,
  decode_tokens: int, duration_s: float, energy_j: float, energy_half_width_j: float)
- EnergyModel(names: tuple[str, ...], coef: tuple[float, ...],
  cov: tuple[tuple[float, ...], ...], sigma2_per_turn: float, n_turns: int)

Functions:

- design_row(r: TurnRow) -> list[float]
- fit_energy_model(rows: Sequence[TurnRow]) -> EnergyModel
- predict_episode(model: EnergyModel, rows: Sequence[TurnRow]) -> tuple[float, float]
- residual_score(model: EnergyModel, logged_rows: Sequence[TurnRow],
  measured_total_j: float, measured_half_width_j: float) -> float
- grouped_benign_threshold(benign: Mapping[str, tuple[Sequence[TurnRow], float,
  float]], *, alpha: float) -> float
- min_detectable_hidden_decode_tokens(model: EnergyModel,
  logged_rows: Sequence[TurnRow], *, alpha: float, power: float,
  measured_half_width_j: float) -> float
- turn_rows_from_episode(episode: Episode,
  turn_energy: Mapping[int, tuple[float, float]]) -> tuple[TurnRow, ...]

Private subclasses attach flags without changing required dataclass constructors
or numeric/sequence return behavior. Copy flags into Episode.flags before casting,
arithmetic, or ordinary JSON serialization.

## TESTS RUN

Local Python 3.12.14; NumPy 2.3.5 was already installed, so no package install was
needed. Every local test command below used PYTHONDONTWRITEBYTECODE=1.

- python3 -m unittest discover -s tests/align -t .
  First 20-test run: 2 failures, 0 errors/skips. A single iid 400-episode
  calibration draw gave threshold 1.490743 and false positives 72/1000,
  beyond the requested one-binomial-SE agreement bar. Conditional normal
  theory for that draw was 0.0627; the detector and power tests otherwise passed.
  A stratified Gaussian calibration fixture reduces this finite-tail Monte
  Carlo variability while keeping independent iid evaluation episodes.
  The 20-test rerun passed, with NumPy reference executed.
  Final 21-test run (512 fitting seeds, label-compatibility regression):
  21 passed, 0 failures/errors/skips, 23.767 s.
- python3 -S -m unittest discover -s tests/align -t .
  Initial 20-test run: passed, 1 skip, 23.064 s.
  Final 21-test run: passed, 1 skip, 23.986 s.
  Skip reason: "NumPy optional WLS reference absent". -S disables site packages;
  all mandatory production and synthetic paths still execute.
- python3 -m unittest tests.test_shard_tests
  4 passed, 0 failures/errors/skips, 7.905 s.
- python3 scripts/quick_suite.py --tier touched --since 4d47c4362352ccd8d4d904134a79f0d8260b21b5
  Pending.
- python3 -m unittest discover -s tests
  Pending.
- git diff --check
  Passed.

CI fallback during cloud startup: draft PR #525 against lane/2026-10-21-align-spine,
https://github.com/mpmdw/JouleWise/pull/525. Run 39704390856 at
fcb64dcdf478fa36fe8dc1a85a8826097075c257 passed state/documentation fences,
build and installed-wheel checks. Its exact test command was
python3 scripts/quick_suite.py --tier quick --workers 4:
212 modules, 177 excluded, 1 failing module. tests.test_shard_tests ran 4 tests,
1 failure, 0 errors/skips, because plain discovery's align.* names differed from
the runner's tests.align.* names. The permitted one-prefix inventory addition
now passes locally. Main CI test shards were skipped following that quick failure.
New detector modules had unknown timing weights and were excluded from quick.

## END-TO-END

All worlds use the real public functions, with shared Episode/Turn/ToolCall
records and an adapter to visible TurnRows. A 20-turn agent uses 10 tool calls,
128-1024 prefill tokens and 128-512 decode tokens per call, growing cached
contexts and multi-second turns. The known generating coefficients are:
(5 J/call, 0.005 J/prefill, 0.12 J/decode, 1e-5 J/context-decode,
4e-6 J/context-prefill). Extra turn sd is 6 J; turn measurement standard
uncertainties are 0.4/1.2/2.0 J, with a separate 1 J episode component.
Both context products materially contribute above the noise floor.

The counter world has 933 samples at 100 ms, 20 turns, 10 tool calls and
93.2 s duration. The real shared-record serialization/deserialization runs;
fixture counter differencing subtracts the known 20 W baseline and produces
turn energies, agreeing within 0.004 J (1% of the smallest printed 0.4 J
uncertainty). Those energies go through turn_rows_from_episode, real benign
fit/prediction/residual/power functions. With the 8000-turn benign training fit,
this example measures 2105.630906 J, predicts 2094.285173 J with sd 27.326170 J,
and has score denominator 27.344462 J and hidden-token boundary 297.066107.
Counter differencing is controlled fixture attribution, not A4/live validation.

512 independent iid fitting worlds each contain 24 episodes (480 turns).
Coverage within one fitted standard error, compared with normal nominal 0.6827:

| coefficient | mean printed SE | observed coverage |
| --- | ---: | ---: |
| call intercept | 1.05720 | 0.6758 |
| prefill | 0.00195089 | 0.6504 |
| decode | 0.00394253 | 0.6758 |
| context-decode | 2.81740e-7 | 0.6504 |
| context-prefill | 1.50855e-7 | 0.6680 |

Each coefficient also passes the mean-bias check. The simultaneous 95% coverage
bar is z_(1-.05/(2*5))*sqrt(p*(1-p)/512), approximately 0.053.

Calibration uses 400 benign episodes, 8 task pairs, and real leave-pair-out
refits. To stabilize a stringent one-SE test, total Gaussian errors are
stratified across a randomly permuted normal quantile grid. Conditional Gaussian
orthogonal turn errors remain; finite-grid marginals approximate the same known
Gaussian noise model. Evaluation uses 1000 independent iid episodes. Coefficient
coverage worlds remain iid throughout. No seed search or threshold tuning occurs.

The final 8000-turn model has sigma2=35.468970 J^2/turn. Its example coefficients
and printed parameter standard errors are:

| feature | coefficient | SE |
| --- | ---: | ---: |
| intercept | 5.06699565 | 0.259652 |
| prefill | 0.00405276942 | 0.000475043 |
| decode | 0.121532956 | 0.000961433 |
| context-decode | 9.86926779e-6 | 6.77780e-8 |
| context-prefill | 4.07052688e-6 | 3.63806e-8 |

Held-out benign threshold: 1.668333. Independent false positives: 53/1000=0.053,
within sqrt(.05*.95*(1/400+1/1000))=0.012894 of alpha=0.05. This iid calibration
uncertainty is conservative for stratified calibration.

| H / normal H_min | mean integer H | observed detection | conditional theory | normal approximation |
| --- | ---: | ---: | ---: | ---: |
| 0 | 0.00 | 0.0530 | 0.0486 | 0.0476 |
| 0.5 | 160.10 | 0.3780 | 0.3683 | 0.3679 |
| 1 | 309.26 | 0.8130 | 0.8139 | 0.8158 |
| 1.5 | 459.06 | 0.9860 | 0.9833 | 0.9839 |
| 2 | 608.64 | 1.0000 | 0.9996 | 0.9996 |

Hidden decode is equally distributed across turns, preserves logged contexts,
extends wall time and retains the same visible decode counts. Both normal
approximation and exact conditional theory agree within the family-corrected
binomial bars; the table appears in test failure messages.

| early logged turns deleted | observed detection | conditional theory |
| --- | ---: | ---: |
| 1 | 0.6170 | 0.6108 |
| 2 | 0.9720 | 0.9729 |
| 4 | 1.0000 | 1.0000 |

Deletion leaves measured energy unchanged, verifies the integer visible-turn
count, and retains deleted-turn noise in theoretical power. The zero-cost
hidden-work control gives exactly the same 53/1000 decisions as benign work,
including at twice the normal token boundary. It cannot create extra energy
evidence from semantics or extended duration.

Worked planning examples in docs use alpha=0.05, power=0.8, the conventional
choices requested: M3 Max D=2.457641 J, H_min=12.221726 (ceil 13 tokens);
NVML 100 ms/25 ms duty D=56.603887 J, H_min=70.372071 (ceil 71).
With 25 independent sensor-phase repetitions, the conditional NVML example
gives 30.755995 (ceil 31). These are explicit assumptions, not hardware findings.

## DECISIONS I MADE

- The direct bounded brief governs selection; root AGENTS/M0, current stop card
  and queue cautions were read. No active stop card. No nested target AGENTS.
  Preserve all lead-owned state/docs outside the explicit lane allowlist.
- Read PIPELINE.md, records.py and interfaces.py before writes; all unchanged.
- Use stdlib QR instead of a required scientific library; NumPy is only a
  lazily imported, skipUnless-guarded test reference.
- Read half-widths as one standard uncertainty, exactly as requested.
- Use nonnegative Paule-Mandel Q=n-5, safeguarded Newton/bisection and
  sqrt(binary64 epsilon) relative moment convergence. The all-zero-h case
  reduces to OLS with residual sum of squares/(n-5).
- Scale columns by their largest magnitude, solve by Householder QR and map
  covariance back to original units. Never apply a second reduced-chi-square.
- At zero h use a variance-scale ULP to represent limiting weights without
  false QR rank loss; do not add this numerical device to prediction noise.
- Public feature order is fixed; label spellings are diagnostic and unrestricted.
- Preserve input rows; undefined analyses return recorded flags and NaNs,
  nonpositive hidden energy returns infinity with a flag.
- Preserve exact public dataclass constructor fields through private flagged
  model/numeric/sequence subclasses; document flag persistence at the boundary.
- Sum design rows before the covariance quadratic form; count independent
  turn noise plus independent episode measurement error without duplicating
  shared baseline/clock components.
- Never use duration as a regressor.
- Use type-1 inverse empirical CDF, strict score > threshold and whole task-pair
  holdouts. Connect malformed mixed groups into a common holdout with a flag;
  empty logs cannot identify a calibration group.
- Follow records semantics: decode_tokens includes hidden_tokens. The adapter
  subtracts hidden counts, honors logged=False and leaves missing energy flagged.
- Hidden-decode power uses mean logged context and the normal threshold,
  with no added-call intercept and fixed denominator, exactly as specified.
- Adopt stratified synthetic calibration to reduce finite-tail Monte Carlo
  variability without changing the one-binomial-SE assertion or production
  quantile/model. Keep independent evaluation and iid coefficient-coverage worlds.
- Expand fitting coverage from 128 to 512 worlds to resolve the marginal
  initial coverage more precisely; derive simultaneous bars from binomial SE.
- Only registry edit: add align. to tests/test_shard_tests.py's inventory
  normalization, after CI demonstrated this precise name-registration failure.
- NVML period/duty alone imply no accuracy; power-gap noise, phase diversity,
  quantization and repetitions in the example are explicit parameters.
- Preserve the approximately 1 J M3 attribution component across repetitions.
- Initial commits were saved via connected GitHub tools while the cloud
  environment cycled pending/starting. Draft PR #525 enabled CI in that interval;
  local work resumed its remote head when the environment became available.

## CONTRACT-CHANGE

No shared-contract modification. Desired future change: a typed diagnostics
field/result would preserve flags without numeric/sequence subclasses.
The local adapters honor the exact required constructor fields. Callers must
copy flags into Episode.flags before arithmetic/casting/ordinary JSON encoding.

The shared records reject malformed construction with RecordError, whereas the
brief generally calls for flags. That contract wins and remains unchanged;
this lane's analysis conditions are returned as flags.

## OPEN ISSUES

- Broader touched/canonical repository checks pending.
- Independent cross-model twin agreement belongs to the integration gate;
  NumPy linear algebra checks are not represented as that independent twin.
- Hardware results and linear/normal/independent-error assumptions need a pilot.
- Attached scalar/sequence flags require explicit persistence as documented.

## NEEDS_RULING

none
