# align-residual lane report

## SUMMARY

- Round 2 continues lane/2026-10-21-align-residual from 971b2f31c7d7cf4c4e4603c6c098184e2b910121.
- Defines turn energy as all owned prefill, decode and tool segments; unowned gaps remain residual.
- Adds held-out calibration mean/SD diagnostics without changing any threshold value.
- Adds calibrated hidden-token power beside the unchanged normal-theory API.
- Flags a sample-maximum quantile and undefined calibration SD without dropping data.
- Normalizes indexable and whole-real token counts before all design arithmetic.
- Adds opt-in reported reasoning-token counts while preserving default subtraction.
- Adds record-path regressions for all four findings; protected contracts and registries are untouched.
- Local tests and repros have NOT EXECUTED: the VM remains pending/starting and offline.

## FILES

Round-2 changes are restricted to four explicitly allowed files:

- joulewise/align/energy_residual.py: owned-energy docstrings; normalized count
  validation/design; threshold diagnostics and three summary attributes; calibrated
  power function; reasoning-count adapter parameter.
- tests/align/test_energy_residual_regressions.py: the existing seven regressions plus
  ten new tests. New fixtures build shared Episode/Turn/ToolCall records with realistic
  cached contexts, tool waits, sensor noise and independent whole-episode integrals.
  Checks owned versus omitted tool energy, location/SD departures, calibrated power,
  quantile rank boundaries, count representations and reported scratchpad counts.
- docs/align/energy_residual.md: ownership, flags, both power formulas, plain-number
  calling convention, labelled M3/NVML examples, lead-provided scale-world comparisons,
  and reasoning-count visibility.
- .codex-report/align-residual.md: this report, preserving all round-1 FIX LOG lines.

tests/align/test_energy_residual.py and test_energy_residual_power.py are unchanged.
No new module or registry edit; no twin/probe file is committed. The three protected
files docs/align/PIPELINE.md, joulewise/align/records.py and interfaces.py are unchanged.
First round-2 checkpoint d96a6cf901fafc5782db2fae3448a5488192b71e defined ownership;
implementation, regressions and expanded documentation are in e7e69393e6c13cd08c3199a4dc94478465662cd2.
Follow-up 914ff040e52d5f97f775d1b6a33df0cf3110903d keeps training-exclusion provenance flags
from invalidating power on valid scored rows; its regression extends the existing
missing-turn test without changing its earlier assertions.

## PUBLIC API

The required signatures and dataclass fields remain exactly as specified:

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
```

Additions this round:

```python
calibrated_min_detectable_hidden_decode_tokens(
    model: EnergyModel, logged_rows: Sequence[TurnRow], *, threshold: float,
    power: float, measured_half_width_j: float,
    benign_mean: float | None = None, benign_sd: float | None = None,
) -> float

turn_rows_from_episode(
    episode: Episode, turn_energy: Mapping[int, tuple[float, float]], *,
    hidden_token_counts_logged: bool = False,
) -> tuple[TurnRow, ...]
```

The calibrated function is in __all__. Threshold results add n_scores: int,
benign_mean: float and benign_sd: float (sample SD, denominator m-1).
These are lane-local float-subclass attributes, like .flags. Arithmetic/JSON loses
them: pass benign_mean and benign_sd explicitly with a plain threshold number and
persist n_scores and flags separately. The calibrated function's formula is
max(0, (threshold-benign_mean+z_power*benign_sd)*D/e); it assumes approximately
normal benign scores. The existing power function assumes unit-normal scores.
D and e are identical between the functions.

New flags: benign_score_calibration_departure, insufficient_calibration_scores,
quantile_at_sample_max; invalid_calibration_summary reports missing, nonfinite or
negative-SD summaries in the new function. Existing unidentified-column and hidden
decode-energy flags propagate. No new dataclass field is added.

## TESTS RUN

Nothing ran locally in round 2. Counts and skips for all requested local commands
are unavailable, not zero-pass evidence. The VM was waited on for several minutes,
then repeatedly checked with the runtime status tool: observed phase pending or
starting, connectivity offline, no failure explanation. exec_command("pwd") was
rejected before execution with:

> No usable execution environment is available. Wait for an environment to become
> available before using this tool.

There is no usable shell in which to checkout, create /tmp/residual-r2, materialize
twins or install NumPy. No package installation or extra-dependent run occurred.
All mutations use connected GitHub create-tree/create-commit/fast-forward-update
tools, with an explicit list of allowed paths and force=False. Every round-2 finding
is consequently marked fixed (NOT EXECUTED).

Read the report first, then PIPELINE.md, records.py, interfaces.py, root AGENTS.md
and targeted M0/orchestration intake through connected GitHub tools. No active stop
card exists. Nested AGENTS.md paths in all touched directories return 404.
The attribution branch's _segments source was inspected through GitHub at lines
431-560; it assigns tool segments to their turn and gaps to None. This is a source
read, not execution of the requested git/sed command.

The independent twin's four files were read verbatim through GitHub from
8849015cde5ec1695f2afdd585ad93af99258aec; they were not committed or locally materialized.
The new round-2 agreement source compares the seven numeric functions directly.
One exact flag assertion in TestTwinResidualAgreement.test_grouped_threshold_agrees
still expects () when rank=m (for example alpha=.01 and m=60 or m=20, and alpha=.025
with m=20). That conflicts with this round's mandatory quantile_at_sample_max flag.
After a verbatim replay, the local uncommitted twin expectation should include that
flag exactly when ceil((1-alpha)*m)==m; this changes no numeric bar. No twin edit or
replay is claimed. No existing in-scope assertion was weakened or changed to accept
a new flag: the new tests assert the required flags directly.

### Requested local commands: all NOT EXECUTED

From /workspace/JouleWise, when an executor becomes available:

```bash
git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-residual
git -C /workspace/JouleWise checkout -B lane/2026-10-21-align-residual origin/lane/2026-10-21-align-residual
git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-residual-twin
mkdir -p /workspace/JouleWise/tests/align/twins
for f in tests/align/twins/__init__.py tests/align/twins/residual_twin.py tests/align/twins/test_residual_twin_selfcheck.py tests/align/test_twin_residual.py; do git -C /workspace/JouleWise show origin/lane/2026-10-21-align-residual-twin:$f > /workspace/JouleWise/$f; done
python3 -m unittest tests.align.test_twin_residual tests.align.twins.test_residual_twin_selfcheck -v
python3 -m unittest discover -s tests/align -t .
python3 -m unittest tests.test_shard_tests
python3 -m pip install numpy
```

Run alignment discovery with the twin files present and again after moving only those
four fetched files out of the checkout; do not commit them. Run the agreement command
before and after the fix, on the baseline 971b2f31c and final round-2 tree respectively.
The requested before/after executions were impossible here. Also run the stdlib path:

```bash
python3 -S -m unittest discover -s tests/align -t .
```

Optional skip reasons in the lane tests are "NumPy optional WLS reference absent"
(existing test) and "optional NumPy table scalars absent" (new test). The new stand-in
__index__ and whole-float tests need only the stdlib. No actual skip count is claimed.

All seven appendix scripts must be materialized outside the repository, with only the
specified world2.py path substitution, for these required replays (all NOT EXECUTED):

```bash
python3 /tmp/residual-r2/world2.py
python3 /tmp/residual-r2/out_of_turn.py 0 0 0
python3 /tmp/residual-r2/out_of_turn.py 0.5 0.5 0.5
python3 /tmp/residual-r2/out_of_turn.py 2 1 1
python3 /tmp/residual-r2/out_of_turn.py 6 4 2
python3 /tmp/residual-r2/hetero.py 0.08
python3 /tmp/residual-r2/edges2.py
python3 /tmp/residual-r2/calib_probe.py 0 0 0
python3 /tmp/residual-r2/calib_probe.py 0.5 0.5 0.5
python3 /tmp/residual-r2/calib_probe.py 2 1 1
python3 /tmp/residual-r2/calib_probe.py 6 4 2
python3 /tmp/residual-r2/calib_probe.py 0 0 0 0.08
python3 /tmp/residual-r2/owned_tool.py 0.5 0.5 0.5
python3 /tmp/residual-r2/owned_tool.py 2 1 1
python3 /tmp/residual-r2/case10_logged.py
git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-attribution
git -C /workspace/JouleWise show origin/lane/2026-10-21-align-attribution:joulewise/align/attribution.py | sed -n 431,560p
```

After each verbatim replay, extend only the local probes to print:
- owned_tool: threshold.flags (departure absent in both settings);
- calib_probe: actual threshold.flags, maximum relative H_cal difference and detection
  using calibrated_min_detectable_hidden_decode_tokens; compare with the probe's h_c;
- edges2: plain-int versus NumPy sigma2 and whole-float versus plain-int fits;
- case10_logged: a row set built with hidden_token_counts_logged=True and its equality
  with the hand-built rows, then the same printed fit/threshold digits.
No extended-probe outputs are available; the expected values below are the lead's,
not represented as observations. No whole-repository suite was launched.

### CI

Latest code-head CI run 39733328023 at 914ff040e52d5f97f775d1b6a33df0cf3110903d was queued at
the latest read: https://github.com/mpmdw/JouleWise/actions/runs/39733328023
This is not a local test result; no successful test run/count is claimed here.

Earlier run 39732765372 at e7e69393e6c13cd08c3199a4dc94478465662cd2 completed changes, fences and
build successfully; installed-wheel's smoke step succeeded before the job was marked
cancelled, and quick was still running at that read. A later push superseded it.
Gate-ledger run 39732765227 failed because the draft PR body explicitly leaves all
five merge gates NOT-RUN; the log lists rows 1 through 5 as "still NOT-RUN".
Those lead-owned gates are not represented as complete and the PR body was not edited.
Final-report-only heads start their own CI runs; the final response reports the
available final-head run status without waiting for completion.

## END-TO-END

New tests, NOT EXECUTED here, run shared records -> turn_rows_from_episode -> benign
WLS -> grouped held-out calibration -> episode prediction -> residual score -> both
power functions. The reviewer-shaped fixture has 6-30 turns, a 2700-4300-token first
prefill, subsequent lognormal tool-result prefills (30-8000 plus 20 wrapper tokens),
visible decode 15-2000, cached context growth, 0.2-3 s real ToolCall records, and
8000/90 prefill/decode tokens per second. Its known coefficient tuple is
(2, .0008, .25, 2.5e-6, 1.5e-7), with intrinsic SD 3 J, turn standard uncertainty
sqrt(.4^2+(.02*mean_energy)^2) J and separate episode standard uncertainty 2 J.
These are planning/scale parameters, not measurements. Both context products are active.

Budgets and seeds reproduce the lead's scale world: 600 calibration episodes across
12 pairs (seed 600000), 2000 evaluation episodes across 20 independently generated pairs (seed 700000),
with independent tool-energy draws at seeds 1/2. Tool energy A+B*wait+N(0,C^2) is
added to the total and, for the ownership control, the owning turn's energy too.
The regression checks absent departure flags when owned and present flags when omitted
from turn energies for both (.5,.5,.5) and (2,1,1). Separate tests check a control,
the (6,4,2) out-of-turn case and 8% multiplicative intrinsic noise (including SD-only
departure), independently reconstructing every held-out mean/SD and quantile.

The calibrated power regression uses the (2,1,1) total-only world, shifts each
evaluation episode by its predicted normal-theory or calibrated token boundary times
the TRUE per-token energy, and compares detection. The lead's specified bar is
4*sqrt(phi(z_power)^2*(1/m+z_power^2/(2*(m-1)))+power*(1-power)/n), approximately
.064 for m=600,n=2000,power=.8. This combines the estimated cut-point SE and
evaluation binomial SE; four SE have about 6e-5 false failure under the approximation.
The same bar must pass calibrated power and fail normal-theory power. Formula
agreement has no printed uncertainty, so the test uses 1e-6 relative. Plain-number
and attribute-based calls use identical inputs and must match bit-for-bit.

Lead-provided reference results, not locally reproduced:

| world A/B/C (J/W/J) | departure | normal-theory median H_min tokens | detection at H_min | calibrated median H_cal tokens | detection at H_cal |
| --- | --- | ---: | ---: | ---: | ---: |
| 0/0/0 | absent | 115.7 | .8195 | 113.4 | .8090 |
| .5/.5/.5 | present | 115.7 | .7205 | 127.8 | .7965 |
| 2/1/1 | present | 115.7 | .4835 | 177.3 | .7835 |
| 6/4/2 | present | 115.7 | .2070 | 449.1 | .7700 |
| 8% multiplicative, 0/0/0 | present (SD) | 278.3 | .6650 | 325.0 | .7845 |

The skewed 6/4/2 mixture has no .80+/- .064 acceptance bar; H_cal remains a normal
approximation. The unchanged grouped thresholds should print 1.607, 3.485, 7.069
and about 21.8; hetero 8% prints 1.912. Owned-tool mean/SD departures should be
.13/.39 SE and .61/.88 SE, with normal-theory boundary detection .8170/.8200.
These are expectations from the brief, not execution evidence.

The same record-path test module adds:
- alpha=.05, m=19/20 quantile-max boundaries and a single finite-score calibration;
- exact fits/thresholds for plain ints, __index__ stand-ins, whole floats and optional
  numpy.int64, with invalid values excluded and counted;
- the median-300-token benign scratchpad world. Retained counts must match manually
  constructed rows and their fits/thresholds exactly. Lead reference: subtraction
  sigma2=2730.3 J^2, decode=.2345 J/token, threshold=1.5943; retention sigma2=8.725,
  decode=.24996 (true .25), threshold=1.7775; no scratchpad sigma2=8.618, threshold=1.5199.

The docs retain labelled planning examples for a 20-turn 8B episode at alpha=.05,
power=.8. Normal-theory and calibrated numbers are both printed; calibrated values
add the explicit assumption t=z_.95, benign mean=0 and SD=1. Under that assumption
(D J, normal-theory H_min tokens, calibrated H_cal tokens) are:
M3 Max (2.457641,12.221726,12.221726);
NVML 100 ms/25 ms duty (56.603887,70.372071,70.372071);
25 independent phase repetitions (24.738634,30.755995,30.755995).
These are existing planning arithmetic, not new hardware or local test results.
Without a benign score summary the hardware calibrated value is unknown.

## DECISIONS I MADE

- Follow the user-authorized GitHub fallback after waiting for an unusable VM.
  Fast-forward only the residual lane; no force push, other branch mutation or PR
  comment. No claims of locally executed tests or installed extras.
- Apply the lead's three RES-R2-01 items; do not stop for a new ruling.
- Turn energy includes every owned attribution segment, including tools. Keep
  unowned gaps in measured totals, document their residual and propose modelling
  separately; the fixed five-term design is unchanged and duration stays diagnostic.
- Use one departure spelling benign_score_calibration_departure, OR of the specified
  four-SE mean and SD tests. Use insufficient_calibration_scores at fewer than two
  finite scores; neither changes data selection or any quantile.
- Check the actual implemented rank==m for quantile_at_sample_max, preserving the
  existing binary-float quantile definition and all numeric values.
- Expose calibration n_scores, benign_mean and benign_sd; accept explicit mean/SD
  numbers in calibrated_min_detectable_hidden_decode_tokens so attributes need not
  survive arithmetic. Keep normal-theory and calibrated numbers distinctly labelled.
- Normalize operator.index scalars or finite whole reals to Python ints before
  validation/design products and mean context. Reject bool, negative, fractional,
  nonfinite and string counts through the existing exclusion/flag path.
- Add hidden_token_counts_logged=False keyword-only to the lane-local adapter;
  default subtraction is unchanged, True keeps reported reasoning-token counts.
  The same reading must be chosen for calibration and scored episodes.
- Training exclusion flags remain diagnostics: they do not invalidate otherwise
  usable scored counts in either power function. Validate the scored rows themselves.
- Retain all numerical bars and derivations from round 1. New four-SE diagnostics
  and calibrated-power bars are the lead's. Pure representation/row identities use
  exact equality because normalized integers feed identical arithmetic.
- Add ten tests to the existing regression module, not a new test module or registry.
  Optional NumPy imports only inside the test guarded by unittest.skipUnless.
- The current twin's obsolete round-1 caveats are retired: its round-2 source already
  matches separate-integral prediction. Only its empty-flags assertion at the newly
  flagged sample maximum needs a local expectation update; no numeric bar may change.

## CONTRACT-CHANGE

No shared contract file was modified.

Turn.hidden_tokens joins "content the monitor never sees" with "count the log does
not hold"; the detector needs to distinguish them. A future shared record should
separate content visibility from token-count visibility. The lane-local explicit
hidden_token_counts_logged parameter supplies both readings without changing defaults.

A typed diagnostics/calibration-summary record would preserve flags and score moments
through serialization; currently callers must persist them explicitly. This remains
a proposal, not a modification of EnergyModel or any cross-lane record.

## OPEN ISSUES

- No usable VM: all requested local discovery, twin before/after, optional NumPy,
  shard checks and verbatim/extended repro execution are outstanding.
- The held-out score flags and H_cal do not model remaining unowned gap energy.
  Propose a future design term for harness/gap work (and measured tool-work predictors
  if justified by calibration), with independent validation. Do not add it to the
  five-term design fixed by this API. Correctly include tool-owned energy first.
- H_cal assumes approximately normal held-out benign scores, stable configuration
  and unchanged D/e under hidden work. A departure flag is diagnostic, not a repair
  for skew, mixtures, fold dependence or changed serving behavior.
- The twin agreement test's exact empty-flag expectation conflicts with the required
  sample-max flag. Its numeric comparisons remain applicable; run it verbatim before
  making the explicitly permitted local expectation-only update, never commit twins.
- Read/persist flags and calibration attributes before arithmetic or serialization.
- PR #525 remains draft; review, hardware validation and merge belong to the lead.

## NEEDS_RULING

Which hidden tokens should the detector treat as unlogged in benign calibration and
scored episodes: only counts absent from the log, or all content hidden from the monitor?
The default remains subtraction; hidden_token_counts_logged=True implements the
reported-count interpretation without altering shared records. The lead's benign
reasoning world gives sigma2 2730.3 J^2 / threshold 1.5943 / decode .2345 J/token
under subtraction, versus 8.725 / 1.7775 / .24996 when counts are kept (true .25);
no scratchpad gives 8.618 / 1.5199. Intrinsic-variance-only denominator inflation is
about sqrt(2730.3/9)=17 under subtraction. This changes which work is counted and a
power statement, so the visibility policy remains the lead's ruling. No requested
implementation is blocked: both readings are available with the ruled default.

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

- RES-R2-01 fixed (NOT EXECUTED) e7e69393e6c13cd08c3199a4dc94478465662cd2; ownership checkpoint d96a6cf901fafc5782db2fae3448a5488192b71e; provenance follow-up 914ff040e52d5f97f775d1b6a33df0cf3110903d.
- RES-R2-02 fixed (NOT EXECUTED) e7e69393e6c13cd08c3199a4dc94478465662cd2: quantile_at_sample_max at rank=m, no threshold change.
- RES-R2-03 fixed (NOT EXECUTED) e7e69393e6c13cd08c3199a4dc94478465662cd2: normalize indexable/whole-real counts to Python ints.
- RES-R2-04 fixed (NOT EXECUTED) e7e69393e6c13cd08c3199a4dc94478465662cd2: hidden_token_counts_logged=False; True retains reported reasoning counts.
