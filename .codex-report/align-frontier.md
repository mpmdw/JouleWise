# SUMMARY
- A10 frontier lane started from align-spine at 4d47c4362352ccd8d4d904134a79f0d8260b21b5.
- Required pipeline, records and interfaces read before writing, via GitHub while the VM starts.
- Implements immutable ConfigRow, strict Pareto dominance and tie-aware Kendall tau-b.
- Includes hand-computable dominance, tie and agreement checks.
- Cheapest-reaching bootstrap and the joule-token divergence gate remain in progress.
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
- Remaining two functions: in progress.

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
In progress: token costs have no uncertainty field; energy uncertainty cannot be reused in token units.

# OPEN ISSUES
- Complete and execute the bootstrap and divergence tests and production-shaped worlds.
- Execute the alignment suite and repo-wide canonical suite once the VM is available.
- Independent cross-model twin comparison remains lead-owned.

# NEEDS_RULING
None yet; token-cost uncertainty handling will be stated explicitly in the completed implementation/report.
