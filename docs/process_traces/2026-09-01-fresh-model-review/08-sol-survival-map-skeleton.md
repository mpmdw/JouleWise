```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Produced the complete _v5 survival map and successor-paper skeleton with fresh-results build notes, reproducible ratio methods, and mechanical first-use auditing.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "head_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "upstream_end": null,
    "branch": "feat/2026-09-01-skeleton"
  },
  "pathspec": [
    "docs/paper/round7/survival-map.md",
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
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_paper_terms_lint tests.test_paper_build tests.test_results_prose_template tests.test_render_results_fills tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...s...s.................................................",
          "----------------------------------------------------------------------",
          "Ran 57 tests in 3.776s",
          "",
          "OK (skipped=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 57 tests in [0-9.]+s\\n\\nOK \\(skipped=2\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "shasum -a 256 docs/paper/draft-v1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab  docs/paper/draft-v1.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab  docs/paper/draft-v1\\.md$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The frozen draft contains 672 lines on disk and in the fill registry, rather than the 673 stated in the task; the survival map covers lines 1–672 without gaps.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Registry rows that remain STOP_FILL still require authenticated suppliers before final results prose can be written; undefined claim-side-bound columns are deliberately omitted.",
      "needs": "Issue the registered suppliers or refusal outcomes before filling campaign results."
    }
  ]
}
```

## Change

The [survival map](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/round7/survival-map.md) classifies all 45 frozen headings and continuously covers lines 1–672. It records every permitted quote-level edit, every rewrite’s build order and registry inputs, and the complete retired-label census.

The [successor skeleton](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/draft-v2-skeleton.md) carries surviving text, leaves the abstract, introduction, discussion, and conclusion as build notes, and builds \(R\), \(R_{cm}\), both exact outcome branches, G2-a selection, and the 37-of-50 negative from physical inputs and worked numbers.

The mechanical first-use audit passed for 35 terms: LLM, prefill, decode, sampling record/support, phase boundary, SHA-256, pulse plateau, monotonic clock, cell, absolute and comparative components, A/B/B/A block, point-only bound, sample standard deviation, Student-\(t\), corner, \(R\), twofold safety factor, zero-denominator refusal, shared/local error, \(R_{cm}\), absolute-\(R_{cm}\) non-applicability, cell floor, signed clearance/shortfall, Holm correction, fail-closed, resolvability, G2-a, RAPL, NVML, binary64, fiducial, set membership, accepted region, and observed sample maximum.

## Verification notes

The task described the frozen source as 673 lines; its verified content and registry binding are 672 lines. No frozen or retained-corpus file was modified.

## Residual risk

Final prose must continue to honor every `STOP_FILL` row. In particular, the undefined “claim-side bound” has no reader-facing column until a physical calculation and authenticated supplier are registered.