# SUMMARY
- Continued pushed lane head 5801e762e; round-2 code is pushed in 797197d43365958136470847a59c2f2efdff8138.
- R2-1 retains unknown-size rows in both frontiers and Kendall tau, flags their size, and keeps the kill gate false.
- Adds the reviewer's three-row and production-panel unknown-size regressions without weakening existing tests.
- R2-4 documents mean-cost standard uncertainty, hint-using trial denominators and missing joule means.
- Records the three required budget-to-frontier mappings; adapter construction and uncertainty combination belong to the lead.
- R2-7 derives the exact all-success singleton probability beside its assertion.
- R2-3 preserves the percentile divergence gate and records its rate question, reviewer measurements and derived pivot references.
- NOT EXECUTED: no Python command ran in this seat after waiting and retries; reviewer evidence is labelled separately.

# FILES
- joulewise/align/frontier.py: ConfigRow readings and unknown-size agreement handling; the Pareto, cheapest and divergence computations otherwise retain their behavior.
- tests/align/test_frontier.py: unchanged; 22 declared methods, including the shared production_world fixture and 40-seed upper-count test.
- tests/align/test_frontier_inputs.py: 10 declared methods (8 existing plus 2 round-2 regressions); exact-probability derivation added. Total declared lane tests: 32, not an executed count.
- .codex-report/align-frontier.md: current report, preserved round-1 FIX LOG and rulings, round-2 dispositions.
- Registry exceptions: none; no repo-wide test ran, so no registry addition was justified.
- Protected docs/align/PIPELINE.md, joulewise/align/records.py and joulewise/align/interfaces.py were read remotely before editing and remain unchanged.
- No twin, appendix or scratch files were committed. There is no usable VM in which to create the requested local-only .review2 files.

# PUBLIC API
```python
@dataclass(frozen=True)
class ConfigRow:
    config_id: str
    model: str
    params_b: float
    trials: int
    caught: int
    joules_mean: float
    joules_half_width: float
    tokens_mean: float

def pareto_frontier(rows: Sequence[ConfigRow], *, cost: str) -> list[str]: ...
def frontier_agreement(rows: Sequence[ConfigRow]) -> dict[str, object]: ...
def cheapest_reaching(rows: Sequence[ConfigRow], target_catch: float, *, cost: str, n_boot: int | None = None, seed: int = 0) -> dict[str, float]: ...
def joule_token_divergence(pairs: Sequence[tuple[float, float, float]], *, level: float = 0.95, n_boot: int | None = None, seed: int = 0) -> dict[str, object]: ...
```

- Public signatures and named return attributes/keys remain unchanged.
- pareto_frontier returns ascending-cost ids, then id order for exact cost/catch ties; .flags names exclusions and rows_used when filtering occurs.
- frontier_agreement uses one common cost/count-valid panel for both frontier sets and tau-b. Unknown sizes remain in that panel with invalid_params_b:<id>. identical and kill_condition_met are None when no row survives; kill is otherwise True only for equal frontiers, at least two distinct finite positive model sizes, no unknown size and no excluded row. Negative net energy is flagged but does not invalidate a row.
- cheapest_reaching excludes invalid config ids from the mapping. It retains .n_boot, .flags, .mc_se_bound and .no_reach_probability. Unavailable global options produce flagged NaNs for included ids.
- joule_token_divergence retains spearman_rho, spearman_ci, residual_sd, residual_sd_ci, median_half_width, diverges, level, n_boot, n_pairs, valid_rho_resamples, valid_residual_resamples and flags. n_pairs counts retained pairs. Unidentified residual fits/intervals produce diverges=None.
- _percentile(values, fraction) remains available and is called four times for a computed divergence result.
- production_world(varying_energy=...) still returns (rows, by_model).
- Unavailable numeric estimates remain NaN; gate unavailability is None. Strict JSON exporters must preserve flags and convert nonfinite values explicitly.


# TESTS RUN
- This fix2c seat: nothing ran in Python. Executed tests 0; executed probes 0; actual skips 0; pass/fail UNKNOWN. Python version UNKNOWN. No interpreter, package install, venv or optional import was available.
- Attempted from /workspace/JouleWise: `python3 --version` and `python3 -m unittest discover -v -s tests/align -t . -p 'test_frontier*.py'`. Both were retried after waiting; every call failed before execution with "No usable execution environment is available. Wait for an environment to become available before using this tool."
- `wait_for_environment` was requested for the selected environment. Repeated environment_status observations reported observed_phase=pending, connectivity=offline, failure=null; this does not identify a root cause. No local network-policy or git-status inspection was possible.
- Reviewer-measured at 5801e762e (supplied in this round's brief, NOT rerun here): test_frontier.py 22/22 and test_frontier_inputs.py 8/8, with one NumPy skip on stdlib and none in a NumPy venv, on Python 3.11, 3.12, 3.13 and 3.14; agreement 11/11. These validate the prior head, not the two new methods or the round-2 change.
- Still NOT EXECUTED in this seat, exact commands from /workspace/JouleWise:
  - `python3 -m unittest discover -v -s tests/align -t . -p 'test_frontier*.py'`
  - `python3 -m unittest discover -s tests/align -t .`
  - `python3 -m unittest discover -s tests`
  - After fetching lane/2026-10-21-align-frontier-twin and copying the four instructed files locally: `python3 -m unittest -v tests.align.test_twin_frontier tests.align.twins.test_frontier_twin_selfcheck`
  - `python3 /workspace/JouleWise/.review2/repro_r2_params_b_agreement.py`
  - `python3 /workspace/JouleWise/.review2/probe_null.py`
  - `python3 /workspace/JouleWise/.review2/repro_halfwidth_contract.py`
  - `sed -n 40,75p /workspace/JouleWise/.codex-report/align-frontier.md` and the brief's R2-2 grep (no merge-safety verdict is included).
  - `python3 scripts/quick_suite.py --tier touched --since 5801e762eca6c9ad9855aadbd55cefd2742f656b`
  - `python3 scripts/fixture_orphan_census.py --fail-on-orphans`
  - `git diff --check origin/lane/2026-10-21-align-spine...HEAD`
- Twin interpreter requirement: Python >=3.12 for random.Random.binomialvariate. No actual interpreter skip is claimed; a Python install could not run.
- Extra-dependency run, NOT EXECUTED: `python3 -m venv /tmp/np`, `/tmp/np/bin/pip install numpy`, `/tmp/np/bin/python -m unittest -v tests.align.test_frontier_inputs`. The optional unittest.skipUnless guard and reason remain unchanged.
- Round-1 scratch probes are also unexecuted by this seat; no historical unexecuted result is converted into a pass.
- Remote/static checks only: GitHub comparison from 5801e762e to b85dd52fd357d17915c414c8ff533d40a17d3527 confirmed exactly frontier.py, test_frontier_inputs.py and this report changed, with 2 fast-forward commits and no protected-file changes; read back the pushed code diff; count 22+10 declared methods; inspect prepared Python sources for trailing whitespace and terminal newlines; verify the changed paths remain inside WRITE_SCOPE. JavaScript-derived reference arithmetic below is not Python testing.

# END-TO-END
- This seat executed no synthetic world. Construction and derived expectations are distinguished from reviewer measurements.
- Fixture construction (derived from code): 4 models x 5 conditions x 40 hint-using trials = 800 Episodes, 20 ConfigRows, 9,600 Turns and 9,600 ToolCalls per world; 200 divergence pairs per model. Models: Qwen3-4B, Qwen3-8B, Qwen3-14B and Jamba-12B-hybrid-attention. Conditions: thinking_off, thinking_on, budget_half, concise, random_delete.
- Production path: real ToolCall/Turn/MonitorVerdict/PowerTrace/Episode -> first-trial JSON roundtrip per configuration -> trapezoidal energy integration -> Episode token totals and monitor counts -> ConfigRows -> frontiers/agreement -> cheapest probabilities -> per-model divergence.
- World parameters: twelve tool-using turns, 2,304-9,216 decode tokens, 40.8-127.2 s, 100 ms trace cadence, 25 ms averaging window, .25 duty fraction, .001 W NVML resolution. Model-specific Gaussian repeatability SD .3 J follows RUN_STATE.md; the hybrid's independent source SD 8 J is eight times the 1 J half-width. Within-condition centering preserves chosen mean costs; means print to .001 J (0.1% of the width).
- Varying-energy frontier memberships (derived from the nominal costs/counts; reviewer confirmed these at 5801e762e): joules = all five Jamba-12B-hybrid-attention conditions plus Qwen3-14B/thinking_on; tokens = all five Qwen3-14B conditions. Reviewer-measured at 5801e762e: Kendall tau -0.086; symmetric difference size 9. No post-fix Python recomputation is claimed.
- Agreement control (derived expectation): 2 J/token across all sizes gives identical five-condition Qwen3-14B frontiers, tau 1, symmetric difference 0 and kill True.
- Per-model divergence: Qwen3-4B, Qwen3-8B and Qwen3-14B are designed to return False; Jamba-12B-hybrid-attention is designed to return True only in the varying-energy world. The median half-width is 1 J by construction for each model. Residual SDs and bootstrap intervals for all four models are UNEXECUTED in this seat and were not supplied as reviewer measurements; none are fabricated.
- R2-1 regressions retain the reviewer's x row when params_b is None, zero or nonfinite; derived frontiers are ['x', 'q4', 'q14'] and ['q4', 'q14'], symdiff {'x'}, identical False, kill False. They also set the production panel's cheapest hybrid size to None/zero and require exact preservation of both frontiers, tau and symmetric difference with no excluded_row/rows_used caused by size.
- The noise-only 40-seed test is unchanged: its sole count bar is the .99 quantile of Binomial(40,.025). A positive lower count bound is unjustified because P(K=0)=.975**40 is about .363 (derived).
- The reviewer's larger null/power probe counts and the half-width contract probe are labelled in NEEDS_RULING and CONTRACT-CHANGE below.

# DECISIONS I MADE
- Round 2 continued 5801e762eca6c9ad9855aadbd55cefd2742f656b, using connected GitHub commits and non-forced, expected-head ref updates because no VM could run checkout/fetch. Round 1 continued 9b7d8be66a77d6fa32c0a2cbdf76ff09074fb875.
- Read the existing report first, then PIPELINE.md, records.py, interfaces.py, AGENTS.md and intake/orchestration guidance. No active stop card was present. The user's exact write allowlist governs over repo-wide bookkeeping rules.
- A function validates only fields it consumes: counts/id and chosen mean for Pareto; additionally joule half-width for joule-cost bootstrap; both means for common-panel agreement, with size read only for the kill decision; all three pair fields for divergence.
- Counts normalize through operator.index; real values through float. Optional-library scalar types do not require optional imports in the core.
- Invalid required fields exclude only that row/pair, with its id/index and retained/input count flagged. Duplicate ids exclude all ambiguous occurrences with the existing duplicate_config_id flag. Excluded cheapest config ids are ABSENT, not mapped to NaN.
- Negative idle-subtracted joules are valid, retained and flagged; negative token counts and half-widths are invalid. Nonfinite inputs are excluded.
- Agreement uses one jointly valid panel, preventing missing energy from manufacturing a frontier disagreement. Only finite positive params_b values identify distinct model sizes. Unknown sizes get invalid_params_b:<id>, remain in both frontiers and tau, and alone add neither excluded_row:<id> nor rows_used. Any unknown size prevents a kill even with two known sizes and identical frontiers. A single-size panel is flagged and cannot kill; excluded rows also prevent a kill.
- Empty/all-excluded agreement returns identical=None and kill_condition_met=None. Unidentified residual fits or unavailable residual intervals return diverges=None. No substantive negative result is implied when a gate did not run.
- Catch denominators remain supplied hint-using trial counts. Strict catch comparisons retain integer cross-products and exact supplied cost ordering; no tolerance changes membership. Exact cost/catch ties retain all ids in id order.
- Kendall tau-b still accounts for ties over all retained configurations. Undefined tau remains flagged.
- Joule half-width remains ONE STANDARD UNCERTAINTY for independent normal cost draws. Negative draws remain unclipped and flagged.
- Token means remain fixed with token_cost_uncertainty_unavailable: no token uncertainty exists in ConfigRow, and a joule width cannot be converted to token units.
- Binomial mode-centered inverse-CDF sampling, seed/input-order invariance, fractional exact-minimum tie credit and unconditional probability accounting remain unchanged.
- Default B=floor(.25/.005**2)+1=10,001 follows SE <= sqrt(1/(4B)) < .005, below the two-decimal probability print quantum. Explicit bootstrap sizes remain parameters.
- Divergence still uses average tied ranks, intercept-plus-slope OLS, sqrt(SSE/(n-2)), whole-observation resampling and equal-tailed linearly interpolated percentile intervals.
- Fixed-draw bootstrap degeneracy accounting remains unchanged: retain finite values separately per statistic, flag discarded draws and expose valid counts. The gate remains lower residual-SD endpoint > median original half-width.
- Production-world Gaussian streams differ per model. The 8 J source is independent of tokens before within-condition centering, and traverses real trace construction/integration. Centering preserves the frontier fixture's chosen mean costs; the separate uncentered null fixture tests nominal gate behavior.
- The F5 null-count test keeps its binomial upper bar. With 40 worlds and a .025 nominal opening rate, a positive 99% lower count bar would reject legitimate zero-opening samples (~36.3% probability). This is why no arbitrary positive lower bound was added.
- F6's 50.0 monitor threshold is the midpoint of binary suspicion scores 0 and 100.
- PIPELINE.md calls this candidate research; the requested kill boolean does not claim registration or live experimental support.
- R2-3 leaves the percentile interval and strict divergence gate unchanged: choosing a different reopening rule changes a printed decision and belongs to the lead. The 40-seed upper-count test remains unchanged.
- R2-4 documents the existing ConfigRow readings; it adds no adapter or new field. Budget Summary.trials, max_measurement_uncertainty_j and possibly missing mean_joules need the mappings below.
- R2-7 documents the exact singleton identity beside the assertion; no test was weakened.
- Additional pivot rates below are derived Gaussian references, not matched-seed probe measurements. Exact even-df chi-square survival sums avoid a Wilson-Hilferty approximation.
- No shared contracts, dependencies, hardware gates, review files or registry entries were modified. No hardware use, credentials or network calls from tests.


# CONTRACT-CHANGE
- Preserve the prior request: optional token standard uncertainty, or explicit ratification of fixed token means for cost="tokens". The current code keeps token means fixed and flags the missing uncertainty.
- Preserve the prior suggestion: explicit diagnostics-bearing result records for cheapest_reaching/pareto_frontier in a future revision. Exact public signatures remain unchanged.
- R2-4: a budget Summary -> ConfigRow adapter must use one standard uncertainty of the configuration's mean joules; Summary.max_measurement_uncertainty_j (largest per-trial bound, explicitly not a mean confidence interval) is NOT a valid joules_half_width.
- Summary.trials counts every trial, whereas ConfigRow.trials is the hint-using catch-rate denominator: use Summary.catch_rate.trials and its corresponding caught count.
- Summary.mean_joules=None maps to a row excluded from joule-cost outputs with invalid_joules_mean:<id>/excluded_row:<id>. Token-only outputs can still use valid token costs and counts. Agreement uses the common valid energy/token panel and flags the exclusion.
- Read the budget lane's Summary and its table note remotely; no adapter was added because its source module is absent from this branch and a new adapter module is outside WRITE_SCOPE.
- Reviewer-measured at 5801e762e: the records-chain world has median SE of a configuration mean 772 J versus per-trial bounds about 37-40 J. cheapest_reaching(.6, cost="joules", seed=1) changes the top answer from Qwen3-4B/concise, probability .586 under SE of the mean, to Falcon-H1-7B-hybrid/thinking_off, probability .595 under the per-trial bound. These are the reviewer-supplied winners; both complete top-3 lists are UNEXECUTED and were not supplied, so they cannot be reported here.
- Question reserved to the lead and adapter author: how should per-trial measurement bounds combine with between-episode spread into the standard uncertainty of the configuration mean? No combination rule is chosen here.

# OPEN ISSUES
- No usable executor after waiting and retries. Round-2 Python tests, appendix probes, full suites and the optional NumPy run remain unexecuted; the first two new regression methods are declared, not certified passing.
- Fetch this lane on a usable VM, copy the twin files and appendix scripts exactly as instructed, then run every command above with Python >=3.12 for the twin. Record actual counts, Python versions, full top-3 lists and each model's residual SD/interval before relying on numerical evidence.
- Registry compatibility is unknown until repo-wide checks run; no allowlist exception was guessed.
- R2-3's estimator choice and R2-4's uncertainty adapter are assigned to the lead; no adapter, interval-method change or test weakening was attempted.
- Fixed-token-cost and bootstrap-degeneracy rulings below remain the prior lane's questions, outside this round.
- No local git status or network-policy read was possible. Only remote branch/file state was inspected; no local user work was touched.
- No hardware validation or claim-bearing result; power remains blind to reasoning inside one forward pass.

# FIX LOG
## Round 1
F1 fixed (NOT EXECUTED) 7ce523a7ec6cb5ef73899bf6682828348efc6cfd — selective normalization, flagged exclusions/counts, integer-like inputs and retained negative net joules; regression cases added.
F2 fixed (NOT EXECUTED) 7ce523a7ec6cb5ef73899bf6682828348efc6cfd — kill requires at least two valid model sizes and no excluded row.
F3 fixed (NOT EXECUTED) 7ce523a7ec6cb5ef73899bf6682828348efc6cfd — uncomputed gates return None.
F4 fixed (NOT EXECUTED) d70b5f55cc8bc6f3b3bbabaaef69867a4c906c71 — report distinguishes reviewer-supplied prior 19/19 runs from this seat's zero executed tests and pending probes.
F5 fixed (NOT EXECUTED) 7ce523a7ec6cb5ef73899bf6682828348efc6cfd — independent Gaussian model streams and an 8 J source traverse Episode/PowerTrace; a positive null-count lower bound is unjustified because P(Binomial(40,.025)=0) is about .363.
F6 fixed (NOT EXECUTED) 7ce523a7ec6cb5ef73899bf6682828348efc6cfd — threshold 50 is derived as the midpoint of suspicion scores 0 and 100.

## Round 2
R2-2 fixed (NOT EXECUTED) b85dd52fd357d17915c414c8ff533d40a17d3527 — report uses the authorized no-executor fallback, removes the prior merge-safety verdict, labels reviewer-measured at 5801e762e separately, and records zero tests/probes executed in this seat; round-1 checks were NOT executed this round.
R2-1 fixed (NOT EXECUTED) 797197d43365958136470847a59c2f2efdff8138 — retain unknown-size rows in both frontiers and tau; flag invalid_params_b without size-only exclusion; unknown size keeps kill False; three-row and production regressions added.
R2-3 rejected (NOT EXECUTED) — changing the gate's definition requires the lead's ruling; its existing percentile computation and 40-seed upper-bound test are unchanged; reviewer-measured rates and derived pivot references are under NEEDS_RULING.
R2-4 fixed (NOT EXECUTED) 797197d43365958136470847a59c2f2efdff8138 — ConfigRow documents mean uncertainty, hint-using trials and missing energy; adapter itself is deferred to the lead under CONTRACT-CHANGE.
R2-7 fixed (NOT EXECUTED) 797197d43365958136470847a59c2f2efdff8138 — the exact singleton probability assertion now derives every-replicate unit credit and B/B bit identity for B below 2**53.

# NEEDS_RULING
Question: should token costs remain fixed, or should ConfigRow gain a token standard uncertainty?
Options considered: (1) fixed token means, recording unavailable uncertainty; (2) an additive optional token uncertainty, with measured values supplied by the owning lane.
Recommendation: keep the current flagged fixed means until measured token uncertainty exists; never convert joule widths to token units.
Blocked work: no code construction; interpretation of token-cost probabilities for a printed result needs lead adjudication.


Question: how should divergence bootstrap degeneracy be handled in the comparison contract?
Options considered: (1) fixed B draws with finite values retained separately per statistic, counted/flagged (this lane); (2) redraw until B resamples have both statistics defined (independent twin).
Recommendation: retain fixed-draw accounting and statistic-specific valid counts; valid OLS fits with constant energy have residual SD zero and should not be discarded merely because rho is undefined.
Blocked work: no implementation work; final comparison of small/tied worlds and any printed intervals require lead adjudication of this estimator convention.

Question (R2-3): should the divergence reopening gate restore the nominal Gaussian false-opening rate, or retain the percentile gate and print its measured rate?
Options considered: (1) a studentized or chi-square-pivot lower bound; (2) keep the percentile gate and print its measured false-opening rate beside each result. The code still implements option 2's existing gate; adding rate output or adopting option 1 needs the lead's ruling.
Recommendation: have the lead compare the two options on the same seeded null/power worlds before choosing. The Gaussian pivot reference below suggests higher power with nominal null rate, but it is not a matched-world execution.
Blocked work: no authorized code fix; changing a printed reopening decision belongs to the lead. probe_null.py and a same-world pivot scratch probe could not execute in this seat.

Reviewer-measured at 5801e762e (NOT this seat's runs), alongside derived Gaussian references:

| n | extra SD / half-width | worlds | percentile openings (reviewer) | pivot opening probability (derived) | pivot count SD (derived) |
|---|---|---|---|---|---|
| 30 | 0 | 1000 | 1/1000 = .001 | .025 | 4.937 |
| 200 | 0 | 1000 | 9/1000 = .009 | .025 | 4.937 |
| 200 | .5 | 300 | 157/300 = .5233 | .624685 | 8.387 |
| 200 | 1 | 300 | 300/300 = 1 | .999997936 | .024885 |
| 40 | 1 | 300 | not supplied; probe unexecuted here | .869835 | 5.828 |

Derived binomial count SD is sqrt(N*p*(1-p)); divide by N for rate SD. At the nominal null p=.025, both 1000-world count SDs are 4.937 (rate SD .004937). The true percentile p is unknown: no count SD is inferred as zero from 300/300 openings. Its universal count-SD bound is sqrt(N/4), hence 15.811 for N=1000 and 8.660 for N=300, from p(1-p)<=1/4. These are derived reference scales, not acceptance bars.

Derived pivot calculation only (JavaScript arithmetic, no Python or matched seeds): conditional on a nonconstant token design and independent Gaussian errors with SD=half-width*sqrt(1+extra**2), SSE/[half-width**2*(1+extra**2)] follows chi-square with df=n-2. The proposed lower endpoint at L=.95 is s*sqrt(df/q_.975); therefore its opening probability is P(chi-square_df > q_.975/(1+extra**2)).
For even df, survival(q)=exp(-q/2)*sum((q/2)**j/j!, j=0..df/2-1). Solving survival(q)=.025 by bisection until adjacent floating-point endpoints gives q_.975=44.46079183631775 at df=28 and 238.86122058627063 at df=198 (df=38: 56.89552053505598). This uses the exact finite-sum form for even df, not Wilson-Hilferty, so there is no Wilson-Hilferty approximation error to quote. These numerical references are not independently validated quantile software or a new gate implementation.

Question (R2-4): which rule combines per-trial bounds and between-episode spread into the standard uncertainty of the mean for the budget adapter?
Options considered: a rule explicitly separating correlated systematic measurement bounds from episode-to-episode random spread, or another lead-approved uncertainty model based on the instrument contract. The budget field cannot be copied as-is.
Recommendation: lead and adapter author specify the uncertainty model and catch-rate denominator, then validate the adapter through the records chain and both top-3 probability lists.
Blocked work: the adapter module is outside this lane's WRITE_SCOPE and budget code is absent from this branch; existing frontier behavior is documented and unchanged.
