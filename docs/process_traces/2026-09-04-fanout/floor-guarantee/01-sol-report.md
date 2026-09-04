```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Added the scoped cell-floor guarantee, sampling-cadence rationale, anchor-correction evidence, Figure 4 treatment, and first-use ledger coverage.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-floor-guarantee-cadence"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/round7/built-terms-lexicon.md",
    "docs/process_traces/2026-09-04-fanout/floor-guarantee/01-sol-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 6 tests in 1.975s",
          "FAILED (failures=5)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 2.636s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
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
  "flags": []
}
```

## Change

The paper now states the cell floor's mechanical promise and limits in plain
language, explains why a 100-ms request is useful without treating it as an
achieved cadence, and gives the phase/request observation-density gates from
the fixed reducer constants. The anchor correction is quantified from its
issued analysis: 2 of 14 formerly accepted captures are now refused, while
the 12 numerical changes have median +0.61% and maximum absolute 4.05%.
Figure 4 is embedded in the calibration method, cross-referenced from the
transfer limitation, and captioned element by element. Four new or newly used
terms are recorded in both first-use inventories; the mechanical draft count
is now 228 with zero failures.

### Finding/decision table

| Item | Evidence inspected | Decision and implementation |
|---|---|---|
| W3 cell-floor guarantee | `docs/phase_2/floor_mint_contract.md` W3 rules 7–8 and the existing Section 4 equations | State only the fixed-calculation guarantee: at-or-below-floor differences are not called resolvable. Explicitly deny automatic truth, direction, importance, cross-cell transfer, unmeasured-bias coverage, and future-sample coverage. No floor semantics changed. |
| W4 100-ms cadence | `joulewise/reduce.py`: phase ratio 2.0, request ratio 4.0, minimum phase records 3, and the observed-gap denominator | Explain the calibration/request resolution benefit, calculate eligibility from achieved gaps, and state the within-record, short-phase, and clock-alignment limits. The code identifiers remain in a non-reader-facing evidence comment. |
| W5 anchor correction | `docs/paper/round7/anchor-correction-quantified.md` and its issued JSON | Use the verified 2-of-14, +0.61%, and 4.05% results together with the required 15-population, 12-derived/3-refused, and old-anchor control context. Keep the statistics diagnostic and state that old floor ratios were not recomputed. |
| W5 Figure 4 | SVG plus `fig4-verification.md`, `excursion-decomposition.md`, issued JSON, and registry rows DX-003/DX-010–017 | Embed the existing figure without editing it; name the surface, title/subtitle, grid, axes/ticks, zero line/label, marks/rings, median lines/labels, callout, legend, and notes. Section 7 uses its one-capture provenance to narrow transfer. |
| First use | Embedded audit ledger and round-7 lexicon | Add `cadence ratio`, `best-fit lag`, `allowed edge interval`, and `edge timing excursions`; first three are glossed at first use and the fourth is built immediately beforehand. |
| Scope | Initial and final status/diff inspection | Only the two authorized paper files and this authorized report are changed; no pre-existing or concurrent dirty paths were present. |

### Changed-sentence first-use audit

The named test mechanically scanned the complete changed draft after each
fix. This table accounts for every added reader-facing manuscript sentence;
the image alternative text is included because it is reader-visible.

| ID | Sentence identifier | First-use result |
|---|---|---|
| C1 | “The requested 100-ms interval is a design choice…” | `sampler cadence` was already audited; no new term. |
| C2 | “It places about ten record periods…” | `plateau` and interval averaging were already built. |
| C3 | “The calculation checks the achieved observation density…” | Plain-language bridge; no new term. |
| C4 | “The cadence ratio is the window duration…” | `cadence ratio` glossed in this sentence. |
| C5 | “A short phase must have a ratio…” | Uses the just-built ratio; constants trace to `reduce.py`. |
| C6 | “These rules say which windows have enough time support…” | Plain-language interpretation of C4–C5. |
| C7 | “They cannot reveal a change within one averaged record…” | Phase, record, clocks, refusal, and bounds were already built. |
| A1 | “The following are diagnostic-era instrument statistics…” | Rate-aware clock anchor was built in the preceding paragraph. |
| A2 | “The associated historical energy values remain void…” | Plain limitation; no new term. |
| A3 | “Re-deriving a historical corpus…” | Claim/evidence vocabulary was already built. |
| A4 | “Across 15 retained captures…” | Accepted/refused capture vocabulary was already built. |
| A5 | “The old-anchor control reproduced…” | The sentence itself explains the control. |
| A6 | “Of the 14 captures previously accepted…” | Uses built capture/refusal vocabulary. |
| A7 | “Among the 12 numerical changes…” | Median and relative change are audience statistics vocabulary. |
| A8 | “The analysis did not recompute…” | Phase-energy floor ratios were built before Section 2. |
| F1 | “Figure 4 opens one of those retained captures…” | Plain transition; no new term. |
| F2 | “The single shift that best aligns an edge…” | `best-fit lag` glossed in this sentence, including sign. |
| F3 | “An allowed edge interval is the wider range…” | `allowed edge interval` glossed in this sentence. |
| F4 | “The points show best-fit lags…” | Uses F2–F3; distinguishes point from bound. |
| F5 | Figure 4 image alternative text | Uses the built best-fit-edge concept; no new term. |
| F6 | Caption label “Edge timing excursions…” | `edge timing excursions` built by F2 before first use. |
| F7 | “The white plotting field carries the title…” | Common figure vocabulary; every named element is visible in the SVG. |
| F8 | “The black horizontal line…marks commanded edge time…” | Commanded edge and zero were built by F2. |
| F9 | “White-ringed blue circles show…” | Switch-on/off lags and medians were built or are audience vocabulary. |
| F10 | “A short leader identifies pulse index 9…” | Allowed interval was built by F3. |
| F11 | “The two-symbol legend states…” | Legend, late, and early are plain visual vocabulary. |
| F12 | “The notes below the legend explain…” | Best-fit points, allowed intervals, clock anchor, and fit step were built. |
| G1 | “In plain words, the cell floor guarantees…” | Cell floor and guarded components were constructed immediately above. |
| G2 | “It does not guarantee that a difference above…” | Registered direction was built earlier; no new term. |
| G3 | “Clearing the floor is only permission…” | Plain-language limit; direction analysis follows. |
| G4 | “The floor also does not cover…” | Cell, sampler configuration, bias, and admitted evidence were already built or plain. |
| L1 | “Figure 4's 118 plotted edge lags…” | Figure concepts were built in Section 2; sentence explicitly limits transfer. |

The two changed lexicon-introduction sentences and three generated-table
description sentences are maintainer metadata rather than manuscript prose;
they introduce no scientific term. The four ledger row fragments reproduce
the audited dispositions above, and the count fragment records 228/0.

## Verification notes

The initial focused run failed on five first-occurrence checks: the bold
`cadence ratio` phrase was split across lines, and the new wording moved
`admitted`, `reducer`, `fitted edge time`/`command time`, and `percentile`
ahead of their existing ledger homes. The cure kept the new bold phrase on one
line, replaced the four accidental early uses with plain equivalents, added
the intended term rows, and reran the same command after the final caption and
ledger edits. The repository-wide suite was intentionally not run under the
mission's preflight rule.
