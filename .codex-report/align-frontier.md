# SUMMARY
- A10 frontier lane started from align-spine at 4d47c4362352ccd8d4d904134a79f0d8260b21b5.
- Required pipeline, records and interfaces read before writing, via GitHub while the VM starts.
- Implements immutable ConfigRow, strict Pareto dominance and tie-aware Kendall tau-b.
- Includes hand-computable dominance, tie and agreement checks.
- Adds exact-binomial/normal cheapest-reaching bootstrap and a pairs-bootstrap divergence gate.
- Draft tests now include two worlds of 800 twelve-turn episodes each, with tools and sampled traces.
- No live hardware, paid APIs or external test network calls.
- This is candidate analysis, not registered evidence or a hardware result.

# FILES
- joulewise/align/frontier.py: candidate frontier math and flag-preserving list adapter.
- tests/align/test_frontier.py: hand-built frontiers and Kendall checks.
- .codex-report/align-frontier.md: lane status, decisions and verification.

# PUBLIC API
- ConfigRow(config_id: str, model: str, params_b: float, trials: int, caught: int, joules_mean: float, joules_half_width: float, tokens_mean: float)
- pareto_frontier(rows: Sequence[ConfigRow], *, cost: str) -> list[str]
- frontier_agreement(rows: Sequence[ConfigRow]) -> dict[str, object]
- cheapest_reaching(rows: Sequence[ConfigRow], target_catch: float, *, cost: str, n_boot: int | None = None, seed: int = 0) -> dict[str, float]
- joule_token_divergence(pairs: Sequence[tuple[float, float, float]], *, level: float = 0.95, n_boot: int | None = None, seed: int = 0) -> dict[str, object]

# TESTS RUN
Not yet run: managed environment is pending/offline. Initial checkpoint is explicitly unverified.

# END-TO-END
In progress.

# DECISIONS I MADE
- Strict Pareto comparison uses exact integer cross-products for catch rates.
- Equal cost/equal catch retain both ids, ordered by id.
- Kendall uses tau-b, preserving rather than arbitrarily breaking cost ties.
- Invalid inputs produce flagged unavailable results; no rows are silently dropped.
- Pareto's exact list return contract uses a list subclass with a flags attribute.
- Empty/invalid data never constitutes evidence for the kill condition.
- Only the lane module, lane tests and this report are changed.

# CONTRACT-CHANGE
Token costs have no uncertainty field; add an optional token standard uncertainty or explicitly ratify fixed token means. Current lane-local behavior holds token cost fixed and records token_cost_uncertainty_unavailable.

# OPEN ISSUES
- Execute the bootstrap and divergence tests and production-shaped worlds; all code is currently unverified.
- Execute the alignment suite and repo-wide canonical suite once the VM is available.
- Independent cross-model twin comparison remains lead-owned.

# NEEDS_RULING
Question: should token costs remain fixed, or should ConfigRow gain token uncertainty? Options: fixed means (current flagged adapter), or optional token uncertainty. Recommendation: fixed means until a measured token uncertainty exists. Blocked: no implementation work; uncertainty interpretation needs lead review before printing probabilities.
