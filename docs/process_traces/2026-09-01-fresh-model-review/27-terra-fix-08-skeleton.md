```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Repaired the ratio close-out rule, local STOP_FILL omissions, replication prose, figure requirements, and first-use ledger.",
  "workspace": {
    "base_requested": "913cd59d",
    "base_mode": "exact",
    "head_start": "913cd59d",
    "head_end": "913cd59d",
    "upstream_end": "a043ca97",
    "branch": "feat/2026-09-01-skeleton"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/round7/survival-map.md"
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
      "cmd": "python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 3 tests in 0.759s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 scripts/paper_terms_lint.py lexicon --draft docs/paper/draft-v2-skeleton.md --out /private/tmp/draft-v2-final-terms.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "437 terms; wrote /private/tmp/draft-v2-final-terms.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "terms; wrote"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "(no output)"
        ]
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
      "text": "Campaign values remain intentionally withheld in registered STOP_FILL sentences; no measurement was run.",
      "needs": "Issue authenticated artifacts before filling values."
    }
  ]
}
```

## Change

The draft now has three exclusive close-out dispositions: A, B only when all ratios are authenticated/evaluable and one is below two, and a separate refusal that selects neither branch and stops branch-dependent filling. All 50 STOP_FILL placements across 33 rows now carry local row-specific omissions; 36 use the checklist’s exact registered sentence.

| Finding | File:line | Cure |
|---|---|---|
| A-F1 | draft:544 | Limited B to authenticated, evaluable ratios with at least one below 2. |
| A-F1 | draft:548 | Added separate missing/unauthenticated/zero-denominator refusal; selects neither branch. |
| A-F2 | draft:37 | Added local registered omissions to abstract build placements. |
| A-F2 | draft:627 | Added local omissions in result-table stopped cells. |
| A-F2 | draft:675 | Added DG-071/DG-075 omissions and IQR gloss. |
| B-FU-01 powermetrics | draft:112 | Glossed as macOS’s built-in interval-power sampler. |
| B-FU-02 timing screen | draft:128 | Replaced “screen” with minimum allowance; gave provenance, formula, and 25/29-ms example. |
| B-FU-03 allowance | draft:132 | Defined stage, energy family, and whole-window allowance before use. |
| B-FU-04 admitted | draft:243 | Defined admitted energy. |
| B-FU-05 independent unit | draft:247 | Defined units for absolute and comparative calculations. |
| B-FU-06 guarded floor | draft:443 | Built resolution bound/cell floor before use. |
| B-FU-07 dominance | draft:315 | Defined the fixed \(R\ge2\) meaning. |
| B-FU-08 registered | draft:327 | Defined registered rounding through fixed plan bytes and SHA-256. |
| B-FU-09 member | draft:132 | Defined a block member as one of four runs. |
| B-FU-10 producer | draft:333 | Removed the internal role name. |
| B-FU-11 \(b\) | draft:128 | Bridged \(B_{\mathrm{fiducial}}\), operative \(b\), and the bracket formula. |
| B-FU-12 MLX | draft:542 | Expanded MLX at first use. |
| B-FU-13 inserted gap | draft:542 | Defined the post-campaign inserted-gap check. |
| B-FU-14 resolution bound | draft:443 | Defined as the largest false difference the cell permits. |
| B-FU-15 \(A_k\) | draft:459 | Built both source quantities and the maximum calculation. |
| B-FU-16 raw \(p\) | draft:494 | Specified statistic, null, distribution, tails, and ten blocks. |
| B-FU-17 not resolvable | draft:510 | Defined as failure to clear the floor, not zero. |
| B-FU-18 intervals | draft:511 | Named and constructed measurement and decision intervals before using them. |
| B-FU-19 deterministic bound | draft:514 | Defined source and per-kind aggregation; retained 0.25-J example. |
| B-FU-20 planning terms | draft:510 | Removed undefined planning-only/planning-sum wording. |
| B-FU-21 stage | draft:132 | Defined at Figure 2’s first use. |
| B-FU-22 freeze receipt | draft:619 | Defined as plan bytes plus freeze time. |
| B-FU-23 reducer | draft:726 | Defined as the program converting retained bundles to phase energies. |
| B-R1 timing bracket | draft:128 | Added both constants’ origin, units, formula, and worked bracket. |
| B-R2 shared/local split | draft:333 | Rebuilt the sign replay and binary64 outward-padding calculation. |
| B-R3 \(b\) provenance | draft:128 | Unified timing-bound naming. |
| B-R4 \(g(n)\) | draft:443 | Explained the 10-unit residual-degree-of-freedom origin and \(n\ge5\) rule. |
| B-R5 \(A_k\) sources | draft:459 | Named the retained endpoint-bound fields and worked 10.0/10.6/10.2-J example. |
| B-R6 direction test | draft:494 | Made the Student-\(t\) test and Holm inputs reproducible. |
| B-R7 §4 diagram | draft:552 | Added Figure 3 requirement with paths, signs, corners, intervals, stops, and outcomes. |
| B-R8 short-prefill diagram | draft:668 | Required a record-support/prefill-overlap diagram. |
| B-R9 G2-a rationale | draft:717 | Explained why Qwen3-8B probes exist but do not select the rung. |
| B-O1 \(A_k\) ordering | draft:459 | Removed the premature caption use; definition now precedes use. |
| B-O2 admitted/member ordering | draft:132,243 | Defined both before their analytical use. |
| B-O3 safeguards before outcome | draft:443,534 | Moved outcome forms after safeguards and gates. |
| B-O4 resolvability ledger | draft:510,1103 | Defined it at use and rebuilt the ledger. |
| B-O5 G2-a minimum | draft:706 | Put overlap mechanics before the three-record consequence. |
| Ledger defect | draft:1103 | Rebuilt the first-use ledger from final text; it now records the repaired terms. |
| Map support | survival-map:22 | Required exact local STOP_FILL omissions. |
| Map branch rule | survival-map:249 | Preserved separate refusal and B’s authenticated/evaluable constraint. |

## Verification notes

- STOP_FILL inspection: `50` placements, `33` unique rows, `36` checklist-exact placements; pass.
- Survival-map partition: `45` ranges covering frozen lines `1–672` exactly once.
- Final first-use review rebuilt a 437-term lexicon and manually rechecked every reported first-use finding. Terms I could not build: none.
- No measurements or quiet-window commands were run.