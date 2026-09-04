# Delta re-audit of fix round 3 at 43967519 (terra xhigh, direct run), verbatim

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Round-3 closes B9: all four §3 status cells match the planned primitives and unissued registry, with no new result claim or first-use/anchor regression.",
  "workspace": {
    "base_requested": "b7abc4fe",
    "base_mode": "exact",
    "head_start": "439675191b678fb7c5c53f92e33a4d055009f308",
    "head_end": "439675191b678fb7c5c53f92e33a4d055009f308",
    "upstream_end": "439675191b678fb7c5c53f92e33a4d055009f308",
    "branch": "feat/2026-09-02-paper-f"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "LANDABLE",
    "findings": [],
    "same_signature": "No findings; therefore no finding repeats a class from 02, 03, or 07."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "nl -ba configs/campaigns/d117_contrast_v5/generate_configs.py | sed -n '1757,1810p;2143,2211p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["phase_energy_j.decode", "phase_energy_j.prefill", "planned_reference_bundles: 9", "gamma-reference-start", "gamma-reference-end"]
      },
      "expected": {"exit_code": 0, "tail_regex": "phase_energy_j\\.(decode|prefill).*gamma-reference-end"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "nl -ba /Users/edr/code/JouleWise-wt-floorgen/configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py | sed -n '574,613p;796,847p;1766,1856p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["prompt_tokens: 42", "output_tokens: 512", "Fixed contiguous null A/B/B/A", "abba_alias_relation: A_equals_B", "alpha-reference-start", "alpha-reference-end"]
      },
      "expected": {"exit_code": 0, "tail_regex": "null A/B/B/A.*A_equals_B.*alpha-reference-end"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "nl -ba docs/paper/results-fill-registry.md | sed -n '428,451p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["No characterization report has been issued.", "KEY_FROZEN / VALUE_UNISSUED", "rows.linearity", "rows.null", "rows.phase_attribution", "rows.drift_settling"]
      },
      "expected": {"exit_code": 0, "tail_regex": "No characterization report has been issued.*VALUE_UNISSUED"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "rg -n -F -e '**Workload response:**' -e '**Identical-condition null:**' -e '**Phase accounting:**' -e '**Drift and recovery:**' docs/paper/results-fill-registry.md docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["DS-02/03/05/06 anchors each occur in the registry and §3."]
      },
      "expected": {"exit_code": 0, "tail_regex": "DS-02/03/05/06"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".............", "----------------------------------------------------------------------", "Ran 13 tests in 3.117s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?s)Ran 13 tests.*OK"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check b7abc4fe -- docs/paper/draft-v2-skeleton.md docs/paper/round7/built-terms-lexicon.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Generator evidence establishes planned primitive collection, not a live characterization result; §3 and the registry explicitly preserve that unissued state.",
      "needs": ""
    }
  ]
}
```

## Findings

| Check | Result | Evidence |
|---|---|---|
| B9 four-row status cells | PASS | Workload/null: floor generator defines phase metrics, fixed 512 output, and null A/B/B/A with `A_equals_B`. Phase: contrast generator targets decode/prefill phase energy. Drift: both plans schedule start/interior/end references. |
| Unissued characterization values | PASS | Registry V5 states no characterization report has issued; its linearity, null, phase-attribution, and drift-settling values are `KEY_FROZEN / VALUE_UNISSUED`. |
| Result-promise scan | PASS | §3 says inputs only and “does not issue” each report; the only result wording is conditional (“If issued”) or explicit omission. |
| Reader-order first use | PASS | New `floor packs` is glossed at lines 253–256; `contrast pack` is glossed in its first row use; restored table terms have preceding or same-cell constructions. Mechanical ledger/terms suite passes. |
| DS-02/03/05/06 anchors | PASS | Both registry and §3 grep results retain the four exact anchors. |
| Same-signature | PASS | No B9 supplier-set mismatch, prior first-use class, factual-regression class, or prior missing-figure class is introduced by this delta. |

Test tail:

```text
.............
----------------------------------------------------------------------
Ran 13 tests in 3.117s

OK
```

## Residual risk

This is a static plan-and-registry audit, not live campaign execution; the paper correctly avoids representing it as one.