# VERDICT: FAIL

## P1 — Successor validator does not bind absorbed additions to the recorded parent judgment

The consult requires derivation basis additions to be “judged under the parent artifact before absorption.” The loader instead constructs additions solely from post-cutoff valid prior rows:

> `post_cutoff_valid_ids = { row["content_id"] ... }`  
> `artifact_basis_ids != parent_basis_ids | post_cutoff_valid_ids`

at [calibration_bracketing.py:1029](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:1029), while `trigger_judgment.new_content_ids` receives only syntactic list/hash validation at [calibration_bracketing.py:1159](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:1159). There is no equality/subset binding between the recorded judgment and absorbed additions.

Reproduced failing scenario:

1. Build the valid n=20 successor containing one post-cutoff addition.
2. Replace `lineage.trigger_judgment.new_content_ids` with `[]`.
3. Recompute artifact and registry hashes.
4. `_valid_acceptance_bound(...)` returns `True`.
5. `load_calibration_acceptance_registry(...)` accepts the full registry.

Thus an issued artifact can absorb an observation without recording that the parent judged it. This violates the D-125 two-universe rule and its lineage evidence contract. A negative regression binding basis additions to `trigger_judgment.new_content_ids` is missing.

## P2 — `COLD-GATE-U2-PENDING` is not absent everywhere

The requested grep is nonempty because the test contains:

> `self.assertNotIn("COLD-GATE-U2-PENDING", build.artifact["decision_ids"])`

at [test_calibration_acceptance_successor.py:886](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:886).

This is only a negative assertion, not an issued tuple member, but it still fails the explicit “absent everywhere (grep)” obligation.

## Obligations that passed

- Migration shim deleted; `_load_registry_for_current_active_selection()` is exactly the plain committed load.
- Screen and ceiling candidates use `Decimal`, `1e-18`, `ROUND_HALF_EVEN`; comparison is post-quantization with zero margin.
- `screen >= ceiling` refuses as `successor_screen_exceeds_budget_ceiling`; cap is `ceiling - screen`, with no clamp.
- Validator requires `screen < ceiling`, exact cap equality, and positive cap.
- Q5 is record-shape only: the field is preserved/validated but never changes observation consumption.
- Q4 freeze test is genuinely two-site: adding a supported successor rule without a recompute branch makes the test error at test time.
- Trigger/basis separation works in the builder: current 30-trigger inventory retains n=19 basis; Window-B is inert; 38 triggers produce n=27 and next boundary 76.
- Runtime classification and fields match §6. `budget_exceeded` necessarily has both excesses positive.
- Worked examples reproduced exactly:
  - n=19 inherited cap `0.001275166090593858`.
  - `0.011581436` → `passed_budgeted`, screen excess `0.000763436`.
  - `0.010000` → `passed_screen`, allowance `0.010818`.
  - `0.012200` → `budget_exceeded`, excesses `0.001382` and `0.000106833909406142`.
  - Degraded n=30 gives `Q95=0.011569565992286168`, `Q99=0.015592473312419959`.
- Zero SD inherits the ordered genesis pair; n=2 refuses under the n≥19 licensing gate; exact screen/ceiling equality behavior is correct.
- No introduced production Decimal/float mixing found. The legacy synthetic-float branch remains isolated and boundary-tested.
- No-clamp test is discriminatory: equal mocked quantiles make a clamping implementation return zero cap, so it would fail to raise and the test would fail.
- Issued n=19 artifact is unchanged: identical SHA-256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`.
- Q3 evidence passes: 160 unique grid cells; kernel 79–80 digits; oracle/absdev 120 digits; exponents retained; truth-minus-pin signs positive; one governing status.
- Generator reproduced the committed grid byte-for-byte under mpmath 1.4.1: SHA-256 `438e7f4e779dad69d3f543b186af15534b90139851f1d9e4973f236ca8684cbe`.
- F1 adjudication passes for drift classification: `instrument_calibration_mismatch` occurs there only when `drift > ceiling`. A low-drift mismatch remains possible only for the separate, coherent systematic preflight-level failure, explicitly recorded as `not_evaluated_systematic_preflight_failure`.

## Same-signature question

**YES — fabricated-evidence signature only.** Silent clamping and incoherent drift refusal are closed, and Q3 evidence is genuine. However, the P1 validator hole admits an authenticated successor whose parent-judgment record omits the observation it absorbs—an evidence/lineage attestation not bound to the claimed fact.

Checks performed: exact diff/status/grep; focused U2 suite `86 OK`; canonical suite `2736 OK (skipped=87)`; independent arithmetic and mutation probes; exact Q3 byte regeneration; artifact hash comparison; `git diff --check`; final worktree clean. No repository files were edited.