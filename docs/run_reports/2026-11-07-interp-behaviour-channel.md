# Behaviour-channel desk tool — 2026-11-07

Implemented the requested Stage 0 behaviour-channel arithmetic on
`interp/2026-11-07-behaviour-channel`, already checked out at intake from
`3edb715df`. This is synthetic desk validation, not a metered result, completed
ASTRA-2CH experiment, registration, or evidence of a fixed-token physics null.

## Scope and intake

Read the design study and relevant EDIT-FRONTIER/two-channel checks, repository
AGENTS/CLAUDE guidance, Mission M0, targeted restart/queue sections, the source
map, and D-009/D-014/D-053/D-067. No active stop card was present. The explicit
user brief selects this bounded desk task and overrides generic full-suite and
coordination-write expectations: no kernel task was registered, and
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`,
`tests/test_gen_state.py`, and `PROJECT_STATUS.md` were not edited.

The intake worktree was clean. No network, weights, telemetry, real measurement
data, Block 5 pipeline, external archive/custody paths, or real restricted
directories were used. Absolute data/archive paths appearing in tracked text
were not followed. No processes associated with the existing analysis job
were inspected or controlled. Tests ran serially by module, without the full
suite or sharded/quick-suite launchers. No subagents or external consults.

## Files and behavior

- `joulewise/interp_energy/__init__.py`: new dependency-free desk package.
- `joulewise/interp_energy/behaviour_channel.py`: validated answer/model/scenario
  records; per-answer modeled gross energy; all-attempts J/correct; a labeled
  above-idle secondary view when identified; symmetric decomposition; analytic
  delta-method and seeded paired/independent bootstrap intervals.
- `scripts/interp_energy/behaviour_energy.py`: offline JSON `compare` and
  `scenario` commands, explicit coefficient provenance/basis, strict input
  validation and JSON output. Reads only its named input; provenance is opaque.
- `joulewise/interp_energy/README.md`: model units and token convention,
  equations, inference limitations, JSON examples/CLI commands, and tracked
  public/unblinded parameter-source leads.
- `tests/interp_energy/__init__.py`, `test_behaviour_channel.py`, and
  `test_behaviour_energy_cli.py`: synthetic arithmetic, covariance, closure,
  scenario, import-independence, inference and real-CLI regressions.
- This report: handoff and limitations in place of lead-owned coordination edits.

The model is `E = fixed + a*p + b*d + c*(p*d + d*(d-1)/2) + idle_w*t`.
Above-idle coefficients plus idle duration predict gross energy; coefficients
already fit on gross energy must specify `gross` and zero extra idle power.
Both arms must use the same coefficient basis. If either idle rate is nonzero,
both arms need durations for the symmetric counterfactual decomposition.

The decomposition allocates half the work/rate interaction to each term:
`behaviour = midpoint(theta) · delta(work)` and
`rate = delta(theta) · midpoint(work)`. Their sum equals the modeled energy
difference up to floating point rounding. The output separates token/context,
per-token rates, idle duration, idle power and fixed overhead. For J/correct,
work includes all failed attempts and the correctness denominator. This is an
exploratory accounting convention, not a change to a registered estimator or
a causal attribution of switching power. With a shared model, zero rate effect
is assumed rather than measured.

The scenario command defaults to the study's public .930/.331 cap-hit and
.079/.481 accuracy rates at a 32,768-token cap. Assumed noncap lengths
3k/5k/8k reproduce approximately 14.5/13.2/11.7 times fewer decode tokens per
correct answer. It computes the mixture of context exposures, rather than
context exposure at the mean decode length. Coefficients remain user supplied;
scenario fractions do not invent a sample size or CI. Changing the cap or
configuration changes the comparison.

## Verification

Final targeted Python 3.13 runs, one module at a time:

```text
python3.13 -B -m unittest tests.interp_energy.test_behaviour_channel
25 tests, OK (2.744 s)

python3.13 -B -m unittest tests.interp_energy.test_behaviour_energy_cli
7 tests, OK (2.245 s)

python3.13 -B -m compileall -q joulewise/interp_energy scripts/interp_energy tests/interp_energy
PASS

git diff --cached --check
PASS
```

The core module includes a seeded coverage regression over 32 synthetic paired
datasets of 160 problems each, with 200 bootstrap draws per dataset. For known
per-answer total/behaviour/rate effects and the per-correct total effect, each
interval method met the threshold of covering truth in at least 26/32 datasets.
This is a regression check, not a guarantee of 95% coverage. Other checks cover
binary-exact closure examples, 64 randomized scenario closure/sign-reversal
cases, a hand-derived ratio SE retaining correctness/energy covariance, paired
covariance cancellation, deterministic seeds, sparse/zero-correct outcomes,
invalid inputs and CLI failures. The import test forbids any request to import
MLX, mlx-lm, Torch or transformers.

Only Python 3.13 runtime tests were available here; no Python 3.11 executable
was found on PATH. The full suite was intentionally not run under the binding
brief and the existing machine-load constraint. No MLX/native code is part of
this component, so **there are no native MLX tests for the lead to run**.

## Limits, open choices and exact next step

Sampling CIs condition on fixed supplied coefficients. They include energy /
correctness covariance and paired-arm covariance but exclude calibration
uncertainty, metrological bounds/floors, multiplicity and claim gates. Normal
delta-method intervals are unreliable with sparse accuracy. A bootstrap draw
with zero correct answers is counted, not discarded; the affected percentile
interval is withheld with an explicit status. Finite delta-method output does
not repair that denominator weakness. All-correct samples carry a warning too.
Repeated seeds within a problem require a separately specified cluster analysis;
this API assumes one independent problem per ID.

No J/token defaults or transferable calibration are asserted. Public source
pointers are the design study §1.2, PC-4/PC-5/PC-6 in the question bank, the
known-bytes slot and its reading rule. Known-bytes values are J/GB contrasts,
not decode-token rates, and the microbenchmark's latency-bound regime limits
transfer. Their worst-case half-widths are not statistical SEs. The scenario's
single noncap length also omits real noncap length variance, which would add
context exposure. These limitations are explicit in the package README.

Next exact step: the lead reviews the local commit, then supplies matched,
unblinded coefficients (model/dtype/device/physical boundary and token-count
convention) and a chosen prospective sampling plan before using this tool on
new behaviour-channel outputs. Independent calibration uncertainty or useful
finite ratio intervals at roughly three base successes need an additional
statistical design; this tool makes neither claim. Include thinking-off and
budget-cap comparators in the later experiment. Any hardware collection remains
with a clean, lead-controlled measurement session.

Local commit: the commit containing this report; no push requested or performed.
