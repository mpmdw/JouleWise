**GENRE:** implementation  
**Mission:** Implement the first S6 increment: a typed successor rendering contract and executable non-issuing scenario fixtures. The issuing renderer is a separately scoped follow-on after S1/S3 and supplier adoption.

**Forcing problem:** `docs/paper/fill-rehearsal/select_outcome_branches.py:14` accepts only `METHODS_DIAGNOSTIC`, while `docs/paper/fill-rehearsal/branch-selection.md:3` describes nonexistent active A/B/REFUSAL groups. `joulewise/paper_rendering.py:41` and `:60` expose only partial cell/verdict projections.

**WRITE_SCOPE:**
```json
[
  "docs/contracts/paper_comparison_rendering.md",
  "tests/test_paper_comparison_contract.py"
]
```

**NEW:** Both paths.

**Deliverables and regressions:**

- Specify typed inputs and placement/token contracts for floor cells, decode and prefill comparisons, repeated model verdicts, ratio A/B disposition, D-166 split refusal, characterization prefix, and two-stage OR-01 precedence.
- Mark S1 placement decisions and S3 quantity semantics as dependencies; unresolved fields remain explicitly unbound. Never infer model verdicts from ratio A/B.
- Encode a scenario matrix with non-issuing expected outputs: A and B crossed with independently valid model outcomes; production-window non-admission; close-out refusal; unavailable evidence; prefill-only refusal; unaffected decode survival; conflicting stages.
- Specify transactional behavior: validate all required inputs before writing output; unexpected failure emits no partial paper prose. A licensed result surviving an unrelated refusal must be distinguished from an incomplete write.
- Include strict magnitude equality, sign disagreement, Holm failure, exact repeated-verdict consistency, and Abstract ≤250-word cases.
- **Counterfactuals:** ratio A forcing a directional model claim, missing evidence becoming an issued refusal, loss of unaffected decode results, conflicting repeated verdicts, a 251-word Abstract, or partial emission after a late failure must each invalidate a fixture.
- Fixtures remain synthetic and cannot obtain production capabilities. Leave the current selector and skeleton unchanged; supply an explicit list of requirements for the later issuing implementation.

**Acceptance — named modules only:** `tests.test_paper_comparison_contract`.

**Constraints:** The contract requires all eventual empirical suppliers to call D-173 `open_paper_input`. No production gate registration, frozen measurement-input changes, paper fill, collection, repository-wide suite, or git commit. No extra writes for bookkeeping. Escalate authority/scope gaps rather than encoding guesses.

**Return contract:** First fenced `claude-codex-report/v1` JSON, `genre="implementation"`, **<8192 UTF-8 bytes**; implementation `implemented|partial|no_change`, acceptance `ready|pending_verification|needs_ruling`. “Implemented” here refers only to this contract/fixture increment.
