# ALIGN v4 R22-2 synthetic simulation — Sol1 handoff

Branch `align/2026-11-08-r22-sim-sol`, precreated and retained; clean base
`09d7b3c7fc5aecd74ffe7b24eeb36ef5377c3bf8`. Authority: the explicit r22-sim
brief and `origin/main:RUN_STATE.md` item 234 / R22-2, R22-5 at
`e9b94bd400a384db8cba42fcfba76cb6330d2fc0`. This is an `[AGENT]` synthetic
qualification task; the brief supersedes queue selection and prohibits all
coordination-state writes. No kernel task or registration change was made.

Full assumptions, requested comparisons, Monte Carlo CIs, prospective repairs,
exact-count checks and verbatim output:
[R22-SIM-sol1.md](../align/v4/b3-sim/R22-SIM-sol1.md).

## Finding

Blind structural replacement improves supply and maximum-rule FPR versus
discarding windows without replacement, but it does not remove informative
missingness. With hot-correlated bars, q=.25, independent member loss e=.10,
tau=.5 s_r and no trend, R22 maximum FPR is **4.040% [4.017,4.063]**, versus
oracle **2.321% [2.309,2.333]**, fixed8 without replacement **4.438%**, and
old count stop **4.636%**. The paired R22−oracle maximum-threshold shift is
**−.221 s_r [−.224,−.217]**. Conditioning future tests on the same structural
gate gives R22 **2.245% [2.231,2.260]**, which changes the target population.

At e=.10, exact R22 qualification probabilities are **88.0489%** and
**52.5588%** for q=1/8 and 1/4. P(m≥39 both) can be larger because a study
with seven admitted windows still fails R22's exactly-eight-window gate.
The report shows both probabilities with Monte Carlo CIs.

The smallest tested frozen margin restoring oracle-level mean FPR across the
84-setting grid is **+.75 s_r**, using both each rule's own qualification
population and paired common-success contrasts. It does not restore nominal
2.5%/5% under every drift stress. A post-discovery **+1.25 s_r** candidate
passes nominal mean targets on the finite grid using monotonicity for 82
settings already passing at +1.0 and fresh-seed validation for the two
exceptions. In the worst selected e=.20, tau=.807692, b=.05 setting, fresh-seed
maximum/rank05 FPRs at +1.25 are **1.954% [1.943,1.965]** and
**3.535% [3.520,3.551]**. These are model-dependent prospective candidates,
not adopted constants, simultaneous bounds or live guarantees.

Literal rank 38 is reported separately: at m>39 it is not the nominal 5% rule.
The m-dependent rank05 is ceil(.95*(m+1)). B5-informed tau uses only R22-5's
.13%/.21% relative-energy priors with explicit hypothetical residual CVs;
there is no measured s_r conversion here.

## Changed files and verification

Only new files under `docs/align/v4/b3-sim/` plus this report:

* `simulate_r22_sol1.py`, reusing the unchanged earlier simulator helpers;
  `validate_r22_sol1.py` for independent-seed selected-case validation.
* `R22-SIM-sol1.md`, three numeric CSVs, full stdout/stderr, metadata,
  LF-normalization digest receipt, discovery-selection manifest, and the
  fresh-seed validation JSON/stdout/stderr.

One completed 84-setting × 100,000-study run took 592.4 s, Python 3.14.6 /
NumPy 2.2.6. Fresh-seed validation covered three settings × 200,000 studies
in 35.9 s. One process and one numerical thread were used. The sandbox rejected
the requested `nice` adjustment; both runs continued at ordinary priority and
the warning is preserved. No other job was inspected or controlled.

Checks and their numerical purpose:

* New simulator's eight unittest checks passed: exact structural-tape/scalar
  selection agreement, cap and failed replacements, no count-based reserves,
  ranks/ties, no-bar identity, tail arithmetic/immutability, independent exact
  count enumeration and byte-identical serialized replay.
* Every scenario checked qualification against exact binomial probabilities;
  tau=0,b=0 checked FPR against exact iid random-m rank expectations.
* `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 -B docs/align/v4/b3-sim/simulate_sol1.py --check`:
  six passed, .483 s.
* `python3.13 -B -m unittest tests.align.test_v4_estimands`: 15 passed, .002 s.
* Python 3.13 AST checks passed for both new scripts. Python 3.13 lacks NumPy
  here; no installation was attempted. Supported Python 3.11/3.13 + NumPy
  reproduction remains a lead gate before using a constant.
* Stdlib audit: 336 count, 3,024 score and 1,344 margin rows; finite values,
  CI ordering, pair means, admitted-hot fractions, source/helper digests and
  quoted stdout checked. CSV CRLF→LF normalization preserved parsed rows;
  its receipt binds raw metadata hashes to delivered bytes.
* Fresh-seed own-population/paired restoration and nominal exception bounds
  passed; validation source/selection digests checked. The initial output
  audit correctly refused to declare a nominal-target candidate through 1.0;
  the exploratory 1.25 extension is disclosed, not relabeled predeclared.
* Final artifact hashes, row counts, report links, verbatim stdout and staged
  whitespace/scope checks passed. All 15 added files are within this study
  directory or this run report; protected files and the reused helper are
  unchanged.

Full suite and pytest were not run, per the explicit machine-load constraint.
No product, runtime or MLX code changed; this artifact requires no new native
MLX test. The lead still owns the native common-scorer/eligibility gates.
No network, weights, measurements, real restricted directory, external
checkout, push or integration was used. Coordination state is unchanged.

## Intake disclosure and open decisions

The authority excerpt inadvertently included adjacent RUN_STATE item 232, a
numerical Block 5 result summary. No underlying measurement path or outcome
document was opened; those values were not used or reproduced. Only the
task-authorized R22-5 priors enter the simulation. Complete outcome blindness
cannot be claimed for this session; the lead should obtain a fresh blind
replication if that standard is required.

Next exact step: lead chooses the all-window versus structurally admitted
future target, confirms rank semantics and desired availability, reproduces
on a supported numerical runtime, converts tau_rel using a prospective W1/C1
residual scale, and rules a margin/admission design with detection-cost
qualification before registration. Unresolved model limits include actual
bar dependence, state persistence, score tails, final eligibility/scorer
validity and the post-reserve test calendar. No scientific policy is installed.
