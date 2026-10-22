# SUMMARY
- Fixes F1 by validating only consumed fields and computing on the remaining valid rows/pairs.
- Flags every excluded identity and count used; accepts integer-like scalars and negative net joules.
- Fixes F2: identical frontiers trigger the kill only across at least two valid model sizes, with no exclusions.
- Fixes F3: uncomputed agreement and divergence gates return None.
- Adds production-shaped regressions plus an optional NumPy scalar test (30 declared tests total).
- Fixes F5/F6 with model-specific Gaussian noise, an 8 J independent-source record chain, and the threshold derivation.
- Refreshes the report to distinguish the reviewer's prior 19-test runs from this seat's unexecuted fixes.
- NOT EXECUTED: the managed VM never became usable; no Python tests or reviewer probes ran in this seat.

# FILES
- joulewise/align/frontier.py: immutable ConfigRow, Pareto/rank/bootstrap arithmetic and selective normalization with diagnostic flags.
- tests/align/test_frontier.py: 22 declared unittest methods; hand calculations, probabilities, divergence and Episode/PowerTrace production fixtures.
- tests/align/test_frontier_inputs.py: 8 declared regression methods covering F1-F3, including stdlib integer-like values and an optional NumPy check.
- .codex-report/align-frontier.md: this report and finding dispositions.
- Registry exceptions: none; no registry failure could be observed without an executor.
- Protected docs/align/PIPELINE.md, joulewise/align/records.py and joulewise/align/interfaces.py were read at the existing lane head and were not modified.
- No committed reviewer/twin files or scratch probes; VM startup prevents creating the requested local-only .review1 files.

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
- frontier_agreement uses one common valid panel for both frontier sets and tau-b. identical and kill_condition_met are None when no row survives; kill is otherwise True only for equal frontiers, at least two valid positive model sizes, and no excluded row. Negative net energy is flagged but does not invalidate a row.
- cheapest_reaching excludes invalid config ids from the mapping. It retains .n_boot, .flags, .mc_se_bound and .no_reach_probability. Unavailable global options produce flagged NaNs for included ids.
- joule_token_divergence retains spearman_rho, spearman_ci, residual_sd, residual_sd_ci, median_half_width, diverges, level, n_boot, n_pairs, valid_rho_resamples, valid_residual_resamples and flags. n_pairs counts retained pairs. Unidentified residual fits/intervals produce diverges=None.
- _percentile(values, fraction) remains available and is called four times for a computed divergence result.
- production_world(varying_energy=...) still returns (rows, by_model).
- Unavailable numeric estimates remain NaN; gate unavailability is None. Strict JSON exporters must preserve flags and convert nonfinite values explicitly.

# TESTS RUN
- This fix seat: nothing ran. Executed Python tests 0; executed probes 0; skips 0; pass/fail UNKNOWN.
- The actual readiness command attempted was `pwd`; exec_command failed before execution with "No usable execution environment is available. Wait for an environment to become available before using this tool."
- wait_for_environment remained pending while repeated runtime observations alternated pending/starting, offline, failure=null. No underlying cause is asserted.
- Historical evidence supplied by the reviewer, not executed or independently verified by this seat: the PRE-FIX head passed 19/19 lane tests on Python 3.13.1 and 3.11. This does not validate these fixes.
- Required, still UNEXECUTED commands from /workspace/JouleWise:
  - `python3 -m unittest discover -v -s /workspace/JouleWise/tests/align -t /workspace/JouleWise -p 'test_frontier.py'`
  - `python3 -m unittest discover -v -s tests/align -t . -p 'test_frontier*.py'`
  - `python3 -m unittest discover -s tests/align -t .`
  - `python3 -m unittest discover -s tests`
  - `python3 scripts/quick_suite.py --tier touched --since 9b7d8be66a77d6fa32c0a2cbdf76ff09074fb875`
  - `python3 scripts/fixture_orphan_census.py --fail-on-orphans`
  - `git diff --check origin/lane/2026-10-21-align-spine...HEAD`
- Reviewer setup (fetch the frontier-twin branch and copy its four specified test files locally) remains UNEXECUTED. The twin agreement tests need Python >=3.12; no interpreter version could be inspected and no Python install attempted.
- Required twin command after that setup: `python3 -m unittest -v tests.align.test_twin_frontier tests.align.twins.test_frontier_twin_selfcheck` with Python >=3.12.
- Required reviewer probes, all UNEXECUTED: `python3 /workspace/JouleWise/.review1/repro_f1_whole_result_refusal.py`, `python3 /workspace/JouleWise/.review1/probe1.py`, `python3 /workspace/JouleWise/.review1/probe3.py`.
- Required F2 command, UNEXECUTED: `python3 -c "import sys; sys.path.insert(0,'/workspace/JouleWise'); from joulewise.align import frontier as F; r=F.frontier_agreement([F.ConfigRow('a','m',4.0,40,20,1000.,10.,2000.)]); print(r['kill_condition_met'], r['flags'])"`.
- Optional dependency run: NOT EXECUTED; no venv, NumPy installation or import occurred. The NumPy unittest uses unittest.skipUnless(importlib.util.find_spec("numpy") is not None, reason); no actual skip is claimed.
- Required extra commands when an executor exists: `python3 -m venv /tmp/np`, `/tmp/np/bin/pip install numpy`, `/tmp/np/bin/python -m unittest -v tests.align.test_frontier_inputs`, `/tmp/np/bin/python /workspace/JouleWise/.review1/probe1.py`.
- No printed binomial-CDF error, exact-integral probability comparison, brute-force mismatch counts, Fraction residual comparison, or post-fix production intervals exist from this seat. Those remain pending, not zero or passing.

# END-TO-END
- This fix seat ran NO end-to-end world. The following describes committed fixture construction and expected outcomes, not measured runtime evidence.
- Each production world constructs 4 models x 5 conditions x 40 trials = 800 Episodes, 20 ConfigRows, 9,600 Turns and 9,600 ToolCalls; by_model has 200 (tokens, joules, half-width) pairs for each model.
- Models are Qwen3 4B, 8B, 14B and Jamba-12B-hybrid-attention, with active sizes 4, 8, 14 and 12 billion. Conditions are thinking_off, thinking_on, budget_half, concise and random_delete.
- Each episode has twelve tool-using turns and 2,304-9,216 decode tokens, lasting 40.8-127.2 s. Traces carry 100 ms sample intervals, 25 ms averaging windows, duty fraction .25 and .001 W sensor resolution.
- Chain: real ToolCall/Turn/MonitorVerdict/PowerTrace/Episode construction -> first-trial JSON roundtrip per configuration -> trapezoidal integration -> Episode token totals/catch counts -> ConfigRows -> frontiers/agreement -> cheapest probabilities -> per-model divergence.
- F5 now gives every model a separate seeded Gaussian error stream at SD .3 J, grounded in RUN_STATE.md's repeatability versus attribution distinction (~.3 J versus ~1 J). Errors are centered within fixed-token conditions to preserve designed cost means. Means print to .001 J (0.1% of the 1 J width), removing integration round-off from deliberately equal means.
- In varying_energy=True, the hybrid model additionally carries an independent Gaussian source with world-parameter SD 8 J, eight times the 1 J half-width. This source is encoded into trace power before integration and must open the real divergence gate. The three Qwen models must stay closed, with their upper residual interval below the 1 J width. In varying_energy=False, all four models are noise-only controls.
- Different-energy world parameters remain token factors (1.5, 1, .75, 1.25) and J/token (1, 2, 4, .7). Qwen3-14B/thinking_on has half the 4B token cost but twice the energy. Expected joule frontier: five hybrid conditions plus Qwen3-14B/thinking_on; expected token frontier: five Qwen3-14B conditions; expected symmetric difference size nine.
- Reviewer-supplied PRE-FIX execution confirmed those memberships and tau-b about -.0963. The new centered-noise fixture preserves the nominal row means, but no post-fix Python result is claimed.
- Agreement control uses 2 J/token across sizes; expected identical five-configuration 14B frontiers, tau-b 1 and kill_condition_met=True.
- F1 regressions run the production panel through failed-trace normalization and token-cost probabilities. A NaN at pair 17 must retain 199 pairs and match the identically seeded explicit 199-pair calculation; -.4 J at pair 5 must retain all 200 and flag the pair.
- Separate null gate fixture remains Gaussian SD 1 J at 1 J half-width across 40 seeds, central level .95 and B=399, with an upper opening-count bar from Binomial(40,.025)'s .99 quantile. No positive lower opening-count bound is justified: P(K=0)=.975**40 approximately .363. The independent-source fixtures exercise positive openings instead.
- All printed post-fix residual SDs, bootstrap bounds, false-opening counts and reviewer numerical comparisons remain UNEXECUTED.

# DECISIONS I MADE
- Continued the existing lane head 9b7d8be66a77d6fa32c0a2cbdf76ff09074fb875, using connected GitHub commits and non-forced ref updates because no VM could run checkout/fetch.
- Read the existing report first, then PIPELINE.md, records.py, interfaces.py, AGENTS.md and intake/orchestration guidance. No active stop card was present. The user's exact write allowlist governs over repo-wide bookkeeping rules.
- A function validates only fields it consumes: counts/id and chosen mean for Pareto; additionally joule half-width for joule-cost bootstrap; both means and model size for common-panel agreement; all three pair fields for divergence.
- Counts normalize through operator.index; real values through float. Optional-library scalar types do not require optional imports in the core.
- Invalid required fields exclude only that row/pair, with its id/index and retained/input count flagged. Duplicate ids exclude all ambiguous occurrences with the existing duplicate_config_id flag. Excluded cheapest config ids are ABSENT, not mapped to NaN.
- Negative idle-subtracted joules are valid, retained and flagged; negative token counts and half-widths are invalid. Nonfinite inputs are excluded.
- Agreement uses one jointly valid panel, preventing missing energy from manufacturing a frontier disagreement. Valid positive params_b values identify distinct model sizes. A single-size panel is flagged and cannot kill; excluded rows prevent a kill even when retained frontiers agree.
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
- No shared contracts, dependencies, hardware gates, review files or registry entries were modified. No hardware use, credentials or network calls from tests.

# CONTRACT-CHANGE
- Add an optional token standard uncertainty, or explicitly ratify fixed token means for cost="tokens". The current dimensionally valid adapter uses fixed token means and records the missing uncertainty.
- Consider an explicit diagnostics-bearing result record for cheapest_reaching/pareto_frontier in a future contract revision; their current exact return types leave no ordinary mapping/list field for flags. Current API signatures are preserved.
- No new contract change requested by this fix round.

# OPEN ISSUES
- Managed environment never became usable: all post-fix tests, probes, twin numerical comparisons and fixture census remain unexecuted. This branch is APPLIED_UNVERIFIED, not merge-safe on this seat's evidence.
- On resume, fetch/checkout this lane, read this report, install the local-only reviewer files as instructed, then run the exact commands above, including Python >=3.12 and NumPy runs if available.
- The optional NumPy case is declared but no dependency availability, skip result or extra run has been observed.
- Registry compatibility is unknown until repo-wide tests execute. No exception addition was guessed.
- The reviewer's exact-CDF/integral/brute-force/Fraction checks must be rerun and their printed numbers recorded; no numerical result was fabricated in their absence.
- Bootstrap degeneracy and fixed-token-cost questions below remain the prior lane's lead rulings, outside this round.
- No local git status, process census or network-policy file could be inspected because no executor existed. Only remote branch/file state is confirmed.
- Remote comparison against intake head confirmed exactly four changed paths: the module, two allowed test modules and this report. No protected file changed. A JavaScript whitespace inspection of the prepared three Python sources found zero trailing-whitespace lines and final newlines present; this is not Python execution or git diff --check.
- No hardware validation or claim-bearing result; power remains blind to reasoning inside one forward pass.

# FIX LOG
F1 fixed (NOT EXECUTED) 7ce523a7ec6cb5ef73899bf6682828348efc6cfd — selective normalization, flagged exclusions/counts, integer-like inputs and retained negative net joules; regression cases added.
F2 fixed (NOT EXECUTED) 7ce523a7ec6cb5ef73899bf6682828348efc6cfd — kill requires at least two valid model sizes and no excluded row.
F3 fixed (NOT EXECUTED) 7ce523a7ec6cb5ef73899bf6682828348efc6cfd — uncomputed gates return None.
F4 fixed (NOT EXECUTED) d70b5f55cc8bc6f3b3bbabaaef69867a4c906c71 — report distinguishes reviewer-supplied prior 19/19 runs from this seat's zero executed tests and pending probes.
F5 fixed (NOT EXECUTED) 7ce523a7ec6cb5ef73899bf6682828348efc6cfd — independent Gaussian model streams and an 8 J source traverse Episode/PowerTrace; a positive null-count lower bound is unjustified because P(Binomial(40,.025)=0) is about .363.
F6 fixed (NOT EXECUTED) 7ce523a7ec6cb5ef73899bf6682828348efc6cfd — threshold 50 is derived as the midpoint of suspicion scores 0 and 100.

# NEEDS_RULING
Question: should token costs remain fixed, or should ConfigRow gain a token standard uncertainty?
Options considered: (1) fixed token means, recording unavailable uncertainty; (2) an additive optional token uncertainty, with measured values supplied by the owning lane.
Recommendation: keep the current flagged fixed means until measured token uncertainty exists; never convert joule widths to token units.
Blocked work: no code construction; interpretation of token-cost probabilities for a printed result needs lead adjudication.


Question: how should divergence bootstrap degeneracy be handled in the comparison contract?
Options considered: (1) fixed B draws with finite values retained separately per statistic, counted/flagged (this lane); (2) redraw until B resamples have both statistics defined (independent twin).
Recommendation: retain fixed-draw accounting and statistic-specific valid counts; valid OLS fits with constant energy have residual SD zero and should not be discarded merely because rho is undefined.
Blocked work: no implementation work; final comparison of small/tied worlds and any printed intervals require lead adjudication of this estimator convention.
