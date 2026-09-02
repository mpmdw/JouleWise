```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Added all 37 dictated ledger rows, updated audience vocabulary and inventory count, with one nonblocking earlier-home anomaly.",
  "workspace": {
    "base_requested": "c8509d84",
    "base_mode": "exact",
    "head_start": "c8509d848ff34ce4c51485f569fb333072731243",
    "head_end": "c8509d848ff34ce4c51485f569fb333072731243",
    "upstream_end": "c8509d848ff34ce4c51485f569fb333072731243",
    "branch": "feat/2026-09-01-skeleton"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 6 tests in 1.043s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " docs/paper/draft-v2-skeleton.md | 41 +++++++++++++++++++++++++++++++++++++++--",
          " 1 file changed, 39 insertions(+), 2 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 file changed, 39 insertions\\(\\+\\), 2 deletions\\(-\\)"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff | grep '^@@'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "@@ -1194,7 +1194,7 @@ transfer assumption. -->",
          "@@ -1215,6 +1215,7 @@ The inventory excludes literal field names and reason names inside quoted omissi",
          "@@ -1222,15 +1223,19 @@ The inventory excludes literal field names and reason names inside quoted omissi",
          "@@ -1247,10 +1252,13 @@ The inventory excludes literal field names and reason names inside quoted omissi",
          "@@ -1266,12 +1274,14 @@ The inventory excludes literal field names and reason names inside quoted omissi",
          "@@ -1282,10 +1292,13 @@ The inventory excludes literal field names and reason names inside quoted omissi",
          "@@ -1295,14 +1308,20 @@ The inventory excludes literal field names and reason names inside quoted omissi",
          "@@ -1310,10 +1329,13 @@ The inventory excludes literal field names and reason names inside quoted omissi",
          "@@ -1323,9 +1345,13 @@ The inventory excludes literal field names and reason names inside quoted omissi",
          "@@ -1333,28 +1359,39 @@ The inventory excludes literal field names and reason names inside quoted omissi"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^@@ -1194"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "half-width first occurs on body line 394 under Comparing the boundary-moved and point-only bounds, earlier than the supplied line-925 location; the dictated status was preserved.",
      "needs": ""
    }
  ]
}
```

## Change

Added rows:

| Term | First reader-facing home | Status |
|---|---|---|
| trace-coverage | Bracketed pulse-train algorithm | glossed-at-first-use |
| unbounded | Bracketed pulse-train algorithm | glossed-at-first-use |
| curvature | Bracketed pulse-train algorithm | glossed-at-first-use |
| third-party provenance / provenance | Every input and every refusal remains visible | glossed-at-first-use |
| three-record minimum | Why the selected prompt length is not yet stated | glossed-at-first-use |
| count floor | Why the selected prompt length is not yet stated | glossed-at-first-use |
| release manifest / manifest | Appendix A. Reproducing this work | glossed-at-first-use |
| admission predicates | A.1 What a reader needs | glossed-at-first-use |
| property-list | A.3 Formal calibration algorithms | glossed-at-first-use |
| Seidel-type | A.3 Formal calibration algorithms | glossed-at-first-use |
| nonconvergent | A.3 Formal calibration algorithms | glossed-at-first-use |
| custody | A.4 Executable verification order | glossed-at-first-use |
| degrees of freedom | Bracketed pulse-train algorithm | audience-vocabulary |
| cumulative counter | A.3 Formal calibration algorithms | audience-vocabulary |
| argmin | A.3 Formal calibration algorithms | audience-vocabulary |
| members | Bracketed pulse-train algorithm | glossed-at-first-use |
| reintegrate | Comparing the boundary-moved and point-only bounds | glossed-at-first-use |
| ulp | Comparing the boundary-moved and point-only bounds | glossed-at-first-use |
| serially correlated | Adding publication safeguards after the ratio | glossed-at-first-use |
| MLX | Outcome sentence forms | glossed-at-first-use |
| ppm | A.3 Formal calibration algorithms | glossed-at-first-use |
| interval aggregate | A.3 Formal calibration algorithms | built-before |
| half-width | Comparing the boundary-moved and point-only bounds | glossed-at-first-use |
| rollover | A.3 Formal calibration algorithms | built-before |
| van der Corput sequence | A.3 Formal calibration algorithms | glossed-at-first-use |
| affine | A.3 Formal calibration algorithms | glossed-at-first-use |
| Fourier–Motzkin elimination | A.3 Formal calibration algorithms | glossed-at-first-use |
| first-parse lag | A.3 Formal calibration algorithms | glossed-at-first-use |
| admissible | A.3 Formal calibration algorithms | built-before |
| MAD | A.3 Formal calibration algorithms | glossed-at-first-use |
| Amplitude | A.3 Formal calibration algorithms | glossed-at-first-use |
| Significance | A.3 Formal calibration algorithms | glossed-at-first-use |
| monotone | A.3 Formal calibration algorithms | glossed-at-first-use |
| bisect | A.3 Formal calibration algorithms | glossed-at-first-use |
| depth-first | A.3 Formal calibration algorithms | glossed-at-first-use |
| Projection | A.3 Formal calibration algorithms | glossed-at-first-use |
| percentile | A.3 Formal calibration algorithms | glossed-at-first-use |

The audience list now includes the three requested expressions, and the count reads `Terms inventoried: 189; FAILS: 0.` All 37 definitions are at most 20 words.

## Verification notes

The sole anomaly is `half-width`: its true first body occurrence is line 394, so its ledger home is the earlier “Comparing the boundary-moved and point-only bounds” section. No alternative collisions were found. The first diff hunk begins at line 1194, below the ledger heading at line 1193; the body is untouched.