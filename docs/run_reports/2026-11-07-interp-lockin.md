# Interp × energy lock-in desk tools — 2026-11-07

Implemented on `interp/2026-11-07-lockin` from `3edb715df`. The requested
branch already existed and was clean at intake. This is synthetic desk work:
no sealed outcomes, measurement files, acquisition, model weights or network
were used. No running job was inspected or changed. Coordination state was
left untouched under the task's explicit override of the normal M0 close-out.
No subagents or external consults were used.

## Deliverables and semantics

- `joulewise/interp_energy/__init__.py`: dependency-free package entry.
- `joulewise/interp_energy/lockin.py`: lazy NumPy generator and estimators.
  Square, ABBA/BAAB and random Manchester bi-phase schedules; interval-average
  references; white and finite-trace 1/f noise, thermal warm-up, signed steps
  and overlapping Poisson contention bursts. Rail-like 1–10 Hz and synthetic
  1 kHz windows are supported. The latter is **not** a verified KM003C cadence
  or noise specification: the study itself describes 50 Hz delivered meter
  samples. White SD is per delivered window, not a physical noise density.
- `joulewise/interp_energy/power.py`: stdlib normal-approximation sizing,
  two-sided detection power, budget MDE, required units/hours and the study
  reproduction. A supplied systematic bound never averages down.
- `scripts/interp_energy/power_analysis.py`: JSON CLI; no data-file arguments
  or collectors. It compares randomized slow ABBA with a faster synchronous
  reference at equal acquisition time using common synthetic noise draws.
- `tests/interp_energy/`: four targeted unittest modules, optional NumPy gates,
  deterministic identities, synthetic Monte Carlo coverage/unbiasedness,
  missing-dependency behavior and noise-dependent design comparisons.
- `pyproject.toml`: optional `interp-energy` NumPy extra; core dependencies
  remain empty. No dependency was installed in this session.

The estimand is signed **B−A watts**. Reference signs are A=−1, B=+1; injected
power is `baseline_w + baseline_w * effect_fraction * reference / 2`. Thus the
fraction uses the unmodulated baseline, and at equal duration it also describes
an energy fraction. It does not size free-running behavior changes.

Matched-reference demodulation uses the known square/coded waveform and its
harmonics. Square-wave fundamental mode uses the known phase at
`1/(2*chip_seconds)`, calibrated against the actual window-averaged square
reference. Both remove the intercept and optionally a linear time trend;
fundamental mode estimates a signed contrast, not an FFT magnitude. Edge guards
discard whole windows. ABBA forms signed `(B1+B2−A1−A2)/2` block contrasts and
requires equal within-chip observed duration and time centroids, preserving
linear-drift cancellation. It refuses incomplete arms instead of imputing them.

Uncertainty uses chronological **four-chip blocks**, not independent kHz samples:
Bartlett/Newey–West HAC, or basic circular moving-block bootstrap of centered
block influence scores (ABBA: centered block differences). Defaults and supplied
lag/block lengths are reported in these units. At least eight blocks are
required; fewer than 30 carry an asymptotic warning. These exploratory CIs do
not replace D-014/D-053 claim procedures, D-054 instrument bounds, equivalence
gates or a registration. Neither method cures schedule-correlated bias, long
memory extending beyond chosen blocks, or unmodelled swap transients.

## Reproduction and illustrative planning result

Study authority: design study §2.2 and the lock-in/PRBS checks (§§1, 11) in
`docs/research-audits/2026-11-07/interp-weight-edit-energy{,-checks}.md`.
No external sources were fetched. For paired SD 2.97 J on 2700 J,
two-sided α=.05 and power=.8:

`n = ceil(((z_.975 + z_.8) * 2.97 / (2700 * fraction))**2)`.

| Fraction | Required pairs | Replays (two per pair) |
|---|---:|---:|
| 1e−4 | 950 | 1,900 |
| 3e−5 | 10,553 | 21,106 |
| 1e−5 | 94,972 | 189,944 |

The study's rounded multiplier 2.80 gives 94,864 pairs at 1e−5, explaining its
“about 95,000”. At an **illustrative**, unmeasured 100 seconds per replay,
94,972 pairs cost 5,276.22 acquisition hours. Setup/idle overhead is excluded.

The committed `2026-11-07-interp-lockin-example.json` is the complete default
CLI result (128 trials, seed 20261107). It uses 27 W baseline, 1e−5 contrast,
1024-second independent sessions at 8 Hz, .03 W white SD, .1 W pink RMS,
.1 W thermal warm-up with τ=300 s, .01 bursts/s of .1 W with mean 1 s length.
Schedules are randomized independently of noise on every trial. Both designs
see the same per-trial noise; only chip timing and estimator differ.

| Synthetic design | Session SD (W) | Nominal 95% HAC coverage | Required independent sessions | Acquisition hours |
|---|---:|---:|---:|---:|
| 16 s randomized ABBA chips | .0106204 | .9141 | 12,144 | 3,454.29 |
| 2 s randomized chips, synchronous demodulation | .0037843 | .9609 | 1,542 | 438.61 |

The variance ratio is 7.876 for this noise model. The slow design has only
16 blocks per session and carries the small-sample warning. Coverage MC SE
around .95 is .0193 at 128 trials; SDs and the gain also have Monte Carlo
uncertainty. A separate white-only test checks that no lock-in gain is assumed.
The illustrative gain is **not transferable** to the study's measured 2.97 J
pair SD without the later noise-PSD gate. Sizing repeats independent randomized
sessions; it does not extrapolate a single continuous 1/f trace as 1/√time.
Swap chips are not counted as whole-model replays. No hardware detectability or
new instrument bound has been established.

## Use

Stdlib study reproduction and pair budgeting:

```sh
python3.13 -B scripts/interp_energy/power_analysis.py --paired-only
```

Synthetic comparison (use an interpreter with NumPy installed):

```sh
python3 -B scripts/interp_energy/power_analysis.py
python3 -B scripts/interp_energy/power_analysis.py --pink-sd-w 0 --thermal-amplitude-w 0 --burst-rate-hz 0
```

Use `--help` for noise, chip timing, cadence, step, effect, budget and systematic
bound parameters. `--step 211:0.05` supplies a synthetic +.05 W step at 211 s.
Simulation duration must contain at least eight complete four-chip blocks of
both designs. For library use, call `make_schedule`, `simulate_trace`, then
`demodulate(..., ci_method='hac'|'block_bootstrap')` or `estimate_abba(...)`.
CI lag lengths and bootstrap lengths are tunable; choose them prospectively.

## Verification and environment limitation

Every test module ran sequentially, with no full/quick/sharded suite. Total
targeted test time including reruns was well below one minute, within the
task's 20-minute limit. NumPy runs limited BLAS threads with
`OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1`.

| Command suffix | Python 3.14.6 / NumPy 2.2.6, `-B -s -W error` | Python 3.13, `-B -s` |
|---|---|---|
| `-m unittest tests.interp_energy.test_lockin` | 12 passed | 12 skipped (NumPy absent) |
| `-m unittest tests.interp_energy.test_coverage` | 3 passed | 3 skipped (NumPy absent) |
| `-m unittest tests.interp_energy.test_power_simulation` | 3 passed | 3 skipped (NumPy absent) |
| `-m unittest tests.interp_energy.test_power` | 9 passed | 9 passed |

The coverage module uses 180 independent trials per population, including
white-only and white+pink+thermal+steps+bursts, for both HAC and bootstrap and a
separate fundamental white-noise check. Mean bias is bounded by four empirical
MC SEs; nominal .95 coverage must lie within four binomial SEs (about .065).
This is a fast regression check, not a precise empirical coverage certificate.
Tests also exercise 1/8/10/1000 Hz, nulls, signs, interval edges, exact linear
drift cancellation, input preservation, refusal cases and optional imports.

The initial local Python 3.14/NumPy build unexpectedly mutated input arrays
with infix arithmetic (minimal `a=arange(32768)/8; b=minimum(a+1/8,4096)` inside
a function changed `a`) and emitted nonfinite-operation warnings from finite
matrix products. The final implementation uses explicit ufuncs for shared
arrays and direct scalar trend projection, avoiding those observed paths.
The final ordinary unittest runs passed with warnings treated as errors;
no tracing, warning suppression or dependency patch was used. Supported CI
Python 3.11/3.13 **with NumPy** was unavailable locally, so that combination
remains a lead check rather than a claimed pass.

Additional checks:

- Python 3.13 targeted compileall passed:
  `PYTHONPYCACHEPREFIX=/private/tmp/interp-lockin-pycache python3.13 -B -s -m compileall -q joulewise/interp_energy scripts/interp_energy tests/interp_energy`.
- Default synthetic CLI passed with `-W error`; its JSON is committed alongside
  this report. `--paired-only` and imports pass in a subprocess using `-S`
  (no NumPy or MLX); missing NumPy produces structured CLI exit 2.
- Final `git diff --check` passed. No push or merge was performed.

## Handoff / open gates

No design ruling is blocked. The next exact verification is to run the four
targeted unittest module commands above **one at a time**, on Python 3.11 or
3.13 with NumPy installed, outside this sandbox. This task adds no MLX code or
MLX-dependent tests; there are no additional native-MLX tests to run for this
branch.

Before any measurement deployment, the lead still owns the study's noise-PSD
gate, actual delivered cadence/window timing, A/A′ and content-swap controls,
chip-length sweep, thermal/frequency checks, sensor validity and systematic
bounds. Those require a later authorized quiet-machine session; none was
attempted here. The finite-trace pink RMS, per-window white SD, burst shapes,
normal planning approximation and independent-session assumption are explicit
modelling choices, not hardware findings. Raw effects can be signed; all
planning detection thresholds are two-sided. No outcome-dependent sample-size
selection or claim eligibility is provided by these tools.
