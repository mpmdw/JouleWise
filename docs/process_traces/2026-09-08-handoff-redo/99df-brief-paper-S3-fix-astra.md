WRITE_SCOPE: ["joulewise/analysis_engine/claim_side_bound.py","joulewise/paper_custody.py","tests/test_paper_custody.py","tests/test_claim_side_bound.py","tests/fixtures/paper_custody/run_kills.py","docs/contracts/paper_claim_side_bound.md","docs/contracts/paper_comparison_placements.md","docs/paper/results-fill-registry.md","tests/test_paper_comparison_placements.py","configs/paper_supply/supply_map.json"]

# Paper S3 — fix round (gpt-6-astra, HIGH, genre implementation)
Head ed44276a on feat/2026-09-08-paper-S3. Two refuters: Opus contract lens at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99cz-ref-paper-S3-opus-contract-review.md (BLOCKERS 1–2, should-fix 3 + placements v1/v2 drift, nits 4–5) and the
Astra execution delta at /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99de-delta-paper-S3-astra-report.md (F1). Cure all, verifying each line by reading the code:
B1 (Opus 1): `ratio_estimand` in the verdict metric is the exact six-key B8 mapping (joulewise/analysis_engine/ratio.py
   ~:34–44, RATIO_ESTIMAND_KEYS; artifact.py ~:190/:1823–1827), never a bare string. The sidecar COPIES the object
   verbatim and reads `ratio_estimand["form"]` for the estimand kind; None stays None for absolute contrasts. Fix the
   contract row rule (paper_claim_side_bound.md ~:56) and the registry binding (results-fill-registry.md ~:1138–1141).
B2 (Opus 2): "J/token" does not exist; the registry vocabulary is `J/committed_output_token` and
   `J/accepted_draft_token` (configs/analysis_registry/ap_spec_draft_front.v2.json ~:115,:128; the native MTP twin).
   RULING: `unit` is copied from the verdict and must be a member of the registry vocabulary {J,
   J/committed_output_token, J/accepted_draft_token} read from the analysis registry (not a literal list — load the
   registry's unit vocabulary or pin it with a regression against those files); the `_j` guard keys on "unit ≠ J"
   (any per-token unit rendered into a J-typed cell refuses). Rewrite test_ratio_in_j_cell against the REAL schema
   (a B8 mapping + a real per-token unit) so it cannot manufacture the schema it tests.
S3 (Opus 3) RULED: injectivity is keyed on (estimand kind, ordered cell list): two contrasts may share an ordered
   cell list when their estimand kind differs (absolute-J contrast and its per-token companion); refuse only when
   BOTH coincide. Record the exemption in the contract with the companion-estimand rationale and add the positive case.
S4: docs/contracts/paper_comparison_placements.md ~:75–76 still says "claim_side_bound.v1 and source-cell join" —
   update to v2 wording identical to the registry twin; keep the S1 three-table agreement tests green (update pins
   and say so).
N4/N5 (Opus nits): in run_kills.py, count DISTINCT guards honestly in the contract's clause-to-test table (say "20
   mutations over N distinct guards"); rename the sidecar key holding only the terms list to `deterministic_terms`
   (the verdict's `deterministic_bounds` is the {terms,total,decision_interval} object) and update contract + tests.
F1 (Astra): `Decimal()` on extreme exponents (`0e9999999999999999999`, `1e-9999999999999999999`) raises
   decimal.InvalidOperation through both public APIs; convert to the structured refusal
   `paper_claim_side_bound_numeral_unparseable` (enumerate it in the contract) with a regression for both inputs.
If the source census digest moves, hash-only repin supply_map.json (diff must show only digest fields; assert it).
Acceptance (rc-gated to a log): tests.test_claim_side_bound tests.test_paper_custody tests.test_paper_comparison_placements
tests.test_paper_rendering tests.test_gen_state tests.test_docs_freshness; run_kills.py --s3 (report N distinct
guards); git diff --check; no commit; header < 8192 bytes; report per finding with file:line and counterfactual.
