# Delta re-audit of fix round 1 at 7e389b53 (terra xhigh, direct codex-run-v3, review genre), verbatim

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "All eight round-1 source findings are closed; the specified delta is LANDABLE.",
  "workspace": {
    "base_requested": "077b6cf3",
    "base_mode": "exact",
    "head_start": "7e389b53a7fea6b1f4f28b54b64b8a39d61fc1c9",
    "head_end": "7e389b53a7fea6b1f4f28b54b64b8a39d61fc1c9",
    "upstream_end": null,
    "branch": "feat/2026-09-02-paper-e"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "LANDABLE",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["7e389b53a7fea6b1f4f28b54b64b8a39d61fc1c9"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^7e389b53a7fea6b1f4f28b54b64b8a39d61fc1c9$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["......", "----------------------------------------------------------------------", "Ran 6 tests in 1.936s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests in [0-9.]+s\\n\\nOK$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check 077b6cf3 -- docs/paper/draft-v2-skeleton.md docs/paper/figures/fig5_phase_record_overlap.svg docs/paper/figures-plan.md docs/paper/figures/README.md",
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
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "SVG validation used XML titles, visible source text, and coordinates; no raster-render accessibility review was run.",
      "needs": ""
    }
  ]
}
```

## Findings

| Source finding | Severity | Disposition | Landed evidence |
|---|---|---|---|
| 03-B1 | BLOCKER | Closed | Draft 946–53 states equal phase width, shifted alignment, and a narrower middle record; 967–77 supplies the causal mechanism. SVG 38–43 and 67–92 implements it. |
| 03-B2 | BLOCKER | Closed | Draft 934–38 gives the record-count reason and explicitly distinguishes the §4 cell-floor reason. |
| 03-SF1 | SHOULD-FIX | Closed | Plain first-use glosses for retained (955–56), diagnostic-era (982–84), prospective demonstration (989–92), and non-claim-bearing (992–93). |
| 03-SF2 | SHOULD-FIX | Closed | Draft 980–85 identifies phase class, 1.5B configuration, July 2026 window, and population. |
| 03-SF3 | SHOULD-FIX | Closed | Draft 919–42 defines sampling record, interval, positive overlap, overlap count/record support, and one three-record minimum; target-range synonym sweep found no retired forms. |
| 03-SF4 | SHOULD-FIX | Closed | Draft 955–63 makes the population the retained power trace, then states its 406-record basis. |
| 03-N1 | NIT | Closed | Draft 963–67 states endpoint/timestamp equality and the enforced tiling tolerance; the statistics JSON defines that tolerance as 0.000001 s. |
| 03-N2 | NIT | Closed | Draft 949–50 limits the claim to data marks. SVG has 23 `data-mark` elements, all with nonempty titles and visible mark-class labels. |

Mechanical first-use audit: 34/34 changed §6 sentence units passed in reader order.

| IDs | Lines | Disposition |
|---|---:|---|
| D01–D08 | 919–938 | Sampling record through `not_resolvable_sample_count`: built earlier or glossed in-place; floor reason bridged. |
| D09–D14 | 940–953 | Diagram/caption vocabulary: components built first or explained in the same caption sentence. |
| D15–D21 | 955–970 | Retention, durations, trace population, IQR, spacing, endpoint equality, and width mechanism: glossed or sourced. |
| D22–D26 | 972–978 | Median warning, alignment limit, intervening-record requirement, observed count, and verdict: built before use. |
| D27–D34 | 980–995 | Population, diagnostic-era, frequencies, conclusion scope, prospective demonstration, non-claim-bearing, and G2-a response: identified/glossed/built. |

SVG coordinate check passed: upper phase `[300,485]`, lower `[330,515]`; both width `185`, shifted; counts `2` and `3`; lower middle record width `150 < 185`; `23/23` data marks have titles.

Numeric sweep passed. The §6 literals `0.121034145`, `0.121`, `406`, `120.9186`, `5.9508`, `405`, `120.9224`, `5.8949`, `1.5`, `2026`, `37`, `50`, and `13` occur verbatim in DG-067–DG-077 and/or the statistics JSON. SVG’s rule counts 2/3 trace to DG-072/DG-073; layout coordinates are illustrative drawing primitives, audited above rather than result claims.

Test tail:

```text
......
----------------------------------------------------------------------
Ran 6 tests in 1.936s

OK
```

## Residual risk

No raster/browser render was inspected; this audit verified the SVG’s source labels and geometry directly.