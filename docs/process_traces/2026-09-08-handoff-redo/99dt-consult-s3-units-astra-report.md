```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "S3 must use the B8 verdict vocabulary J/token; AP-SPEC units belong to a separate manifest path.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "9760ee535c646a61dcef1792dc747ed7fa1072e4",
    "head_end": "9760ee535c646a61dcef1792dc747ed7fa1072e4",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-paper-S3"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"B1","severity":"blocker","summary":"Sidecar vocabulary confuses AP-SPEC estimands with B8 verdict metrics."},
      {"id":"S1","severity":"should_fix","summary":"Membership regression needs a valid B8 object on both acceptance and rejection cases."}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_claim_side_bound",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK$"}
    }
  ],
  "flags": []
}
```

## Findings

**B1 — Blocker.** Both reviews were read. 99dn’s retraction is correct, with a qualification: the cited ratio rule belongs to the **v1/B8** manifest path, not a universal v3 normalization.

1. **Origin and propagation.** Both requested AP-SPEC JSON files declare `J/committed_output_token` at line 115 and `J/accepted_draft_token` at line 128. Their sibling manifest preserves the estimands by exact equality (`joulewise/analysis_engine/registry.py:619`). That v2 manifest is explicitly rejected by `analyze-claims` (`joulewise/analysis_engine/inputs.py:635–638`). There is **no AP-SPEC → B8 unit conversion** here.

   For B8, the manifest author supplies `metric.unit`; `joulewise/analysis_manifest.py:397,1320–1321` requires exactly `J/token`, without rewriting it. AP-2 base registry metrics require `J` and null ratio (`:540–541`). The verdict builder copies the metric unchanged (`joulewise/analysis_engine/__init__.py:1608`); the cited test supplies `J/token` (`tests/test_analysis_claims.py:1723`). `ratio.py:287–303` derives a temporary `J` numerator view for evidence lookup, explicitly preserving the artifact metric. Current finalized v3 construction emits `J`/null (`joulewise/analysis_manifest_v3.py:3918–3923`).

2. **Exact S3 vocabulary.** For its supported absolute/B8 contract, accept **`J` with null ratio**, or **`J/token` with a valid exact B8 mapping**. Refuse every other unit, including both AP-SPEC strings, `J/parsecs`, empty/non-string values, and incompatible unit/ratio pairings. Copy accepted strings verbatim. Current `claim_side_bound.py:24,125` reverses the required ratio acceptance. The contract’s registry pin is also wrong (`docs/contracts/paper_claim_side_bound.md:51`).

3. **Shared authority.** No existing importable validator or constant owns this complete vocabulary. `artifact.py:1818–1827` requires only a nonempty unit string; it imposes **no unit vocabulary**. `ratio.py:34–44,267–284` owns B8 keys/forms and `denominator_unit="token"`, but never checks the enclosing metric unit. Extract a shared metric-unit/ratio validator and canonical constants, then use them in manifest validation, verdict validation, and S3. Merely importing `validate_ratio_estimand` cannot solve this.

**S1 — Should-fix.** `tests/test_claim_side_bound.py:165–170` leaves the ratio null, allowing another guard to mask missing membership enforcement. For **each B8 form**, hold all other source fields valid: `J/token` must produce and validate successfully; `J/parsecs` must return `paper_claim_side_bound_unit_mismatch` through both APIs. Removing only membership enforcement must fail that regression. Include both AP-SPEC strings as rejected cases.

The read-only probe confirmed current behavior: valid B8 + `J/token` refuses; both AP-SPEC strings pass.

## Residual risk

The 26 existing sidecar tests pass despite this defect. Probes used synthetic inputs; no end-to-end custody or hardware validation was performed. No files changed.