# SUMMARY
- Implements the exact A10 ConfigRow and four requested public function signatures.
- Computes strict joule/token Pareto frontiers and Kendall tau-b with cost ties.
- Adds exact-binomial/normal cheapest-reaching probabilities with a 10,001-draw default.
- Adds Spearman and OLS-residual percentile intervals and the energy-divergence gate.
- Supplies 19 unittest cases, including two production-shaped episode/trace worlds.
- Core and tests use only the Python standard library; no hardware or paid services.
- Pushed checkpoints to lane/2026-10-21-align-frontier using connected GitHub tools.
- UNVERIFIED: the managed VM never became usable; no Python tests have executed.

# FILES
- joulewise/align/frontier.py: immutable lane-local row, frontier math, uncertainty bootstraps and flag-preserving return adapters.
- tests/align/test_frontier.py: 19 tests for hand frontiers, rank ties, bootstrap probabilities, divergence and shared-record synthetic worlds.
- .codex-report/align-frontier.md: this report.
- Registry exceptions: none. No files outside the three paths above changed.
- Protected PIPELINE.md, records.py and interfaces.py were read at spine commit 4d47c4362352ccd8d4d904134a79f0d8260b21b5 and were not modified.

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

Return details, pinned for the independent twin:
- pareto_frontier: list of config ids, ascending cost then id, with a tuple-valued .flags attribute.
- frontier_agreement: joules_frontier and tokens_frontier are sets; symmetric_difference is a set; kendall_tau is tau-b; identical is set equality; kill_condition_met is that equality on a valid nonempty input; flags is a tuple.
- cheapest_reaching: every unique config id maps to its unconditional cheapest-and-reaching probability. The dict-compatible adapter exposes .flags, .n_boot, .mc_se_bound and .no_reach_probability. These attributes are not extra config keys.
- joule_token_divergence: spearman_rho, spearman_ci, residual_sd, residual_sd_ci, median_half_width, diverges, level, n_boot, n_pairs, flags, valid_rho_resamples and valid_residual_resamples. Intervals are (lower, upper) tuples.
- Unavailable numeric values are NaN, paired with flags. Analysis outputs are not Episode records: set/NaN outputs and mapping attributes need explicit handling when exporting to strict JSON.

# TESTS RUN
- Python test commands executed: none; executed tests 0, skips 0, pass/fail status UNKNOWN.
- Every attempted exec_command (including the minimal `pwd` readiness probe) failed before executing with: "No usable execution environment is available. Wait for an environment to become available before using this tool."
- wait_for_environment was attempted repeatedly; the environment remained offline, moving between pending and starting. The latest status observation was pending, desired_phase running, network-policy state unknown, failure null. No root cause is asserted.
- Required next exact commands, from /workspace/JouleWise:
  - `python3 -m unittest discover -s tests/align -t .`
  - `python3 -m unittest discover -s tests`
  - `python3 scripts/fixture_orphan_census.py --fail-on-orphans`
  - `git diff --check origin/lane/2026-10-21-align-spine...HEAD`
- No extras installed, imported or required; no extra-dependent tests exist. Extra-dependency run: not applicable.
- A separate JavaScript hand calculation of the fixture's nominal dominance relationships confirmed the expected differing frontier memberships below. This is design checking, not execution of the Python implementation or unittest evidence.
- No workflow runs were attached to the second pushed checkpoint when checked; CI evidence is not claimed.

# END-TO-END
The following worlds are implemented in the tests but have NOT EXECUTED:
- Each world has 4 model identities x 5 conditions x 40 hint-using trials = 800 episodes, 20 ConfigRows, 9,600 turns and 9,600 tool calls. Both worlds total 1,600 episodes and 19,200 turns/tools.
- Models: Qwen3-4B, Qwen3-8B, Qwen3-14B and a synthetic Jamba-12B-hybrid-attention identity; active parameter sizes 4, 8, 14 and 12 billion.
- Conditions: thinking_off, thinking_on, budget_half, concise and random_delete. Twelve turns per episode, 256 prefill tokens per turn, 192-768 generated tokens per turn, 2,304-9,216 generated tokens per episode, 80 token/s model rate plus a one-second tool span each turn.
- Episodes last 40.8-127.2 seconds. PowerTrace uses 100 ms samples (409-1,273 samples), 25 ms averaging windows, duty fraction .25 and .001 W resolution (NVML's milliwatt reporting quantum). Each episode has balanced +/-1 J measurement error and a stated 1 J half-width, based on the attribution limit in the brief.
- Chain: construct real ToolCall/Turn/MonitorVerdict/PowerTrace/Episode records -> JSON round-trip the first trial per configuration -> trapezoidal sample integration -> episode token totals and monitor catch counts -> ConfigRows -> pareto_frontier/frontier_agreement -> cheapest_reaching -> per-model joule_token_divergence. No mock replaces any frontier/statistics function.
- Different-energy world parameters: token factors (1.5, 1, .75, 1.25), J/token (1, 2, 4, .7). For thinking_on, Qwen3-4B has 9,216 tokens and nominal 9,216 J; Qwen3-14B has 4,608 tokens and nominal 18,432 J. Token ratio .5, energy ratio 2.
- Nominal joule frontier, from the separate hand design calculation: all five hybrid-attention conditions in cost order (thinking_off, concise, budget_half, random_delete, thinking_on), then Qwen3-14B/thinking_on. Nominal token frontier: the five Qwen3-14B conditions in that same condition order. Symmetric difference: nine config ids. Python assertions for the actual integrated world remain unverified.
- Agreement control sets all four J/token values to 2: both frontiers should equal the five Qwen3-14B configurations and tau-b should be 1.
- Separate divergence worlds use 160 twelve-turn episode totals (1,536-9,216 tokens), energy 400 + 1.5*tokens + Gaussian noise of SD 1 J at a 1 J width. Forty seeds at level .95 check false openings against the .99 quantile of Binomial(40, .025), since the lower tail is (1-.95)/2. The added-source world adds independent SD 8 J, eight times the floor. No opening counts, probabilities or measured intervals are claimed until these tests run.

# DECISIONS I MADE
- Followed the spine records contract and read AGENTS.md, intake/stop-card sections, Mission M0 and orchestration guidance through the public GitHub connection while the VM was unavailable. There was no active stop card in the inspected spine.
- No frontier branch existed at intake. Created it from the requested spine head using the connected GitHub equivalent of checkout/commit/push. Local checkout/fetch could not run.
- PIPELINE.md calls this candidate research, not registered research. The brief's "registered kill condition" is implemented as the requested diagnostic boolean without claiming registration or experimental support.
- Catch denominators are supplied hint-using trial counts; this analysis does not silently select/filter episodes. Fixture trials all carry hint_used=True.
- Token cost in these worlds is generated/decode token count; the core uses the caller's tokens_mean as supplied. params_b is active parameter size, metadata only; costs are absolute per-episode costs and are not divided by parameter count.
- Strict dominance follows the supplied definition, using integer cross-products for catch rates. Cost comparisons use recorded values directly. No arbitrary tolerance changes membership. Equal cost/equal catch retain both ids in id order.
- Kendall tau-b includes all configs and accounts for tied costs; simultaneous ties contribute to neither denominator factor. Undefined tau is flagged. Single-size input is flagged; its set equality is still exposed.
- Invalid/nonfinite inputs return flagged unavailable estimates rather than raising or silently deleting rows. Empty/invalid panels never supply a kill-condition signal.
- Joule costs are independent normal draws with joules_half_width interpreted as ONE STANDARD UNCERTAINTY. No coverage-factor conversion. Negative normal draws are retained as specified and flagged, not clipped into a different distribution.
- Exact binomial sampling uses an inverse CDF built by normalized recurrence outward from the mode. This avoids both normal approximations and O(trials) random draws per replicate.
- Token means stay fixed, with token_cost_uncertainty_unavailable flagged: the contract supplies no uncertainty in token units. Reusing a joule width in token units would be dimensionally invalid.
- Sort configurations by id before seeded sampling for input-order invariance. Split an exact cheapest tie evenly within that replicate, without arbitrary id preference.
- Cheapest probabilities are unconditional; no-reach mass remains visible through .no_reach_probability. Successful probabilities are never renormalized conditional on reaching.
- Default B = floor(.25/.005**2)+1 = 10,001 because SE(p_hat) <= sqrt(1/(4B)); this makes the worst-case Monte Carlo SE strictly below .005, half a percentage point and below the .01 two-decimal print quantum. Explicit n_boot is honored.
- Divergence uses average tied ranks for Spearman, an OLS intercept and slope, and residual SD sqrt(SSE/(n-2)). A constant token predictor cannot identify the slope and is flagged; it does not open the gate.
- Resample complete observations, preserving token-energy association. Do not add another Gaussian noise draw to energy already containing measurement noise.
- Both intervals use equal-tailed percentile bounds with linear interpolation at (B-1)*p. Default B also bounds empirical-CDF Monte Carlo SE below .005; explicit test budgets remain parameters.
- Count and flag degenerate bootstrap fits; their undefined statistic is excluded from that interval, and valid resample counts are returned. An unidentified original fit cannot reopen the question.
- The gate is exactly residual_sd_ci[0] > median(original half-widths); rho is diagnostic, with no invented rho cutoff.
- Kept exact list/dict[str,float] API signatures by using lane-local container subclasses for diagnostics. Mapping attributes must be preserved explicitly on export.
- Synthetic values, targets, confidence levels, seeds and sample sizes are fixture/API parameters, not claimed hardware observations. Agreement bars and statistical test bars carry derivations beside assertions.
- No extra dependencies, hardware use, credentials, test network calls, changes to shared contracts or writes outside scope.

# CONTRACT-CHANGE
- Add an optional token standard uncertainty, or explicitly ratify fixed token means for cost="tokens". The current dimensionally valid adapter uses fixed token means and records the missing uncertainty.
- Consider an explicit diagnostics-bearing result record for cheapest_reaching/pareto_frontier in a future contract revision; their current exact return types leave no ordinary mapping/list field for flags. Current API signatures are preserved.

# OPEN ISSUES
- ALL Python implementation and test execution is blocked by managed environment startup. This checkpoint must not be treated as passing CI or runtime verification.
- On resume, checkout origin/lane/2026-10-21-align-frontier, read this report first, then run the commands above; repair any discovered lane defects and only then claim completion.
- Repo-wide registry exceptions cannot be determined before the canonical suite executes.
- The independent cross-model twin has not been compared. This lane did not spawn a same-model substitute or claim independent verification.
- No hardware validation or claim-bearing result; power remains blind to reasoning inside one forward pass.
- Local /workspace/JouleWise status, local git checkout and fixture-process census could not be inspected. All changes described here are confirmed remote commits, not a claimed local workspace state.

# NEEDS_RULING
Question: should token costs remain fixed, or should ConfigRow gain a token standard uncertainty?
Options considered: (1) fixed token means, recording unavailable uncertainty; (2) an additive optional token uncertainty, with measured values supplied by the owning lane.
Recommendation: keep the current flagged fixed means until measured token uncertainty exists; never convert joule widths to token units.
Blocked work: no code construction; interpretation of token-cost probabilities for a printed result needs lead adjudication.
