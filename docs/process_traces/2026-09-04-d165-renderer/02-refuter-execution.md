{"verdict":{"gauntlet":"NOT LANDABLE","findings":[{"id":"B1","severity":"blocker","file":"docs/paper/results-fill-registry.md","line":919,"text":"The registry does not register any complete professor-facing OB-01 or OR-01 rendering string: OB-01 still says no renderer exists and both rows remain STOP_FILL / VALUE_UNISSUED / TOKEN_MISSING. The implementation and same-commit fixtures therefore invent exact punctuation and phrasing that cannot be checked character for character against an independent registry oracle.","counterfactual":"A renderer could change the Oxford-comma list form, em dash, parentheses, Qwen-pair wording, or model/verdict phrase while preserving the registry's semantic prose; changing the same-commit fixture would keep the acceptance test green because no registered complete literal exists to reject the drift."}]}}

# D165-OUTCOME-RENDERER-01 execution refuter

Date: 2026-09-04  
Seat: Sol high, execution lens  
Reviewed head: `4de528404b29c84eb25df0ba9aff6b1d4d21619d` (exact requested prefix `4de52840`)  
Diff reviewed: `git show HEAD`  
Seat report: `docs/process_traces/2026-09-04-d165-renderer/01-seat-landing-report.md`

## Findings

### B1 — blocker — registry has no character-exact rendering oracle

`docs/paper/results-fill-registry.md:919` still says that no professor-facing
OB-01 list renderer exists and records `STOP_FILL`, `VALUE_UNISSUED`, and
`TOKEN_MISSING`. Line 921 does the same for OR-01. By contrast, exact complete
strings are introduced only by the implementation's own fixtures
(`tests/fixtures/results_fill_outcome/branch_b.json:5`,
`before_comparison_absent_verdict.json:14`,
`before_comparison_refusal.json:14`, and `closeout_refusal.json:6`).

The keys `OB-01` / `OR-01` and stage-label substrings `before comparison` /
`at close-out` do match the registry byte-for-byte. None of the four complete
non-STOP fixture strings occurs in the registry. Thus the required
character-for-character verification fails at the authority boundary even
though the implementation is semantically consistent with the prose rule.

Counterfactual: change the implementation's Oxford comma, em dash,
parenthesization, fixed-pair wording, or model/verdict phrase and update the
same-commit fixture. The test remains green, while no independent registered
literal can detect the change. The exact public templates must be ruled and
registered before this code can be landable; then the acceptance test must
compare against those registered bytes.

## Execution evidence

- Permitted suite: `python3 -m unittest tests.test_results_fill_outcome tests.test_d165_dominance_closeout` exited 0: `Ran 48 tests in 10.056s`, `OK`.
- Independent counterfactual harness built fresh D-165 sources, mutated only in memory, and observed exactly `{"OB-01":"STOP_FILL","OR-01":"STOP_FILL"}` for all four cases:
  1. one `comparative_common_mode_ratios` census entry removed;
  2. authenticated close-out's floor-source digest replaced with 64 zeroes;
  3. valid at-close-out refusal combined with an authenticated before-comparison window stop and before-comparison precedence;
  4. before-comparison claim-evaluation stop carrying `outcome: present`.
- In-memory mutation: the renderer was changed to accept an unauthenticated whole-window record and synthesize `inferred_<outcome>` as its reason. The committed acceptance test failed at `tests/test_results_fill_outcome.py:164`, observing `before comparison: Qwen3-1.7B measurement window — inferred_excluded` instead of `STOP_FILL`. Result: mutant killed, one test run, one expected failure. No repository source was mutated.
- Registry literal inspection: all four complete non-STOP fixture strings were absent; the exact keys and two stage-label substrings were present.

## Residual risk

The normalized before-comparison seam trusts an upstream `authenticated: true`
attestation rather than revalidating source bytes itself
(`joulewise/results_fill_outcome.py:79-128`). That is explicitly documented as
future-successor responsibility, so this review does not elevate it separately;
the eventual integration must prove that untrusted input cannot set the bit.
