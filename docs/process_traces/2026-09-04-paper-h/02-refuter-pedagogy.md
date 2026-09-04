```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "PED-01",
        "severity": "should_fix",
        "location": "docs/paper/draft-v2-skeleton.md:88",
        "text": "The first reader-facing use of 'monotonic clock' says only 'never-adjusted'; the physical definition (a counter that advances and is not corrected to civil time) now arrives in Section 2 at line 178.",
        "cure": "At the Section 1 first use, add the physical appositive: 'monotonic clock—a counter that advances but is never corrected to civil time—'."
      },
      {
        "id": "PED-02",
        "severity": "should_fix",
        "location": "docs/paper/draft-v2-skeleton.md:97",
        "text": "'Component' is restated as two calculation-category labels ('within-model repeat calculation' and 'four-run between-model calculation') instead of being built from the observations; the physical constructions arrive only in Section 4 at lines 476-477.",
        "cure": "Replace the dictionary line with a physical build: repeated runs of one model produce a spread, four-run model comparisons produce differences, JouleWise bounds each source separately, and each separately bounded source is a component."
      },
      {
        "id": "PED-03",
        "severity": "should_fix",
        "location": "docs/paper/draft-v2-skeleton.md:120",
        "text": "The formula for the shared-error ratio introduces U_cmp,shared and U_cmp,point without assigning either symbol to a physical quantity; those assignments arrive only in Section 4 at lines 526 and 657.",
        "cure": "Before the quotient, name U_cmp,point as the four-run comparison's recorded-edge limit and U_cmp,shared as its largest limit after one calibration-error sign is replayed across all blocks plus one local sign per block; then divide them."
      }
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Selected-A pedagogy review finds three later-dependent or dictionary-style first uses; fill markers and permitted checks are intact.",
  "workspace": {
    "base_requested": "daf696f58e376d67ea6fbd08fe68039314e3f674",
    "base_mode": "exact",
    "head_start": "daf696f58e376d67ea6fbd08fe68039314e3f674",
    "head_end": "daf696f58e376d67ea6fbd08fe68039314e3f674",
    "upstream_end": "daf696f58e376d67ea6fbd08fe68039314e3f674",
    "branch": "feat/2026-09-04-paper-h"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-paper-h/02-refuter-pedagogy.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 10 tests in 1.718s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 10 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 1.401s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "tmp_dir=$(mktemp -d); PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output \"$tmp_dir/draft-v2-selected.md\" --outcome A",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200"]},
      "expected": {"exit_code": 0, "tail_regex": "selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show HEAD^:docs/paper/draft-v2-skeleton.md | rg -o '\\[FILL:[^]]+\\]' | wc -l; rg -o '\\[FILL:[^]]+\\]' docs/paper/draft-v2-skeleton.md | wc -l",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["140", "140"]},
      "expected": {"exit_code": 0, "tail_regex": "140\\s+140"}
    }
  ],
  "flags": []
}
```

## Findings

### PED-01 — should_fix

At [docs/paper/draft-v2-skeleton.md:88](../../paper/draft-v2-skeleton.md), “never-adjusted monotonic clock” does not yet tell the reader what the object is or how it differs physically from the wall clock. The missing construction appears at line 178, after the first-use point. Cure shape: insert “a counter that advances but is never corrected to civil time” as an appositive at the Section 1 use.

### PED-02 — should_fix

At [docs/paper/draft-v2-skeleton.md:97](../../paper/draft-v2-skeleton.md), the moved definition of “component” is a dictionary classification made from two still-abstract calculation names. Section 4 finally supplies the physical distinction: spread among repeated runs of one model versus differences from four-run model comparisons. Cure shape: build those two observed false-difference sources first, say each is bounded separately, and only then name each source a component.

### PED-03 — should_fix

At [docs/paper/draft-v2-skeleton.md:120](../../paper/draft-v2-skeleton.md), the prose prints `U_cmp,shared/U_cmp,point` without assigning either symbol. The reader must wait until lines 526 and 657. Cure shape: define the recorded-edge comparative quantity and the shared/local replay quantity in physical words, attach the two symbols, then print their quotient.

## Changed-hunk term audit

The walk used the selected-A order: title, selected Abstract A, then Sections 1 through 11. “Built-before” below means the physical referent precedes the label; “glossed-at-first-use” means the construction is completed at that first use.

| Term in reader-facing changed prose | First use | Decision |
|---|---:|---|
| `powermetrics` / power sampler | 50 | glossed-at-first-use |
| sampling record | 50 | glossed-at-first-use |
| prompt processing / prefill | 52-54 | glossed-at-first-use |
| token generation / decode | 54-55 | glossed-at-first-use |
| phase edge | 55-56 | glossed-at-first-use |
| integrated energy | 61-62 | glossed-at-first-use |
| shared repeat displacement / run-to-run scatter | 64-66 | built-before |
| commanded graphics-processor pulses / GPU work | 75-77 | glossed-at-first-use |
| measurement window | 77 | glossed-at-first-use |
| pulse-derived limit | 78-79 | glossed-at-first-use |
| pulse-to-model edge-transfer assumption | 79-81 | built-before |
| inserted-gap check | 81-84 | glossed-at-first-use |
| rate-aware clock mapping | 86-93 | glossed-at-first-use |
| monotonic clock | 88 | **FAILS — PED-01** |
| bracketed readings | 89-91 | glossed-at-first-use |
| fixed-rate, offset mapping | 90-91 | glossed-at-first-use |
| pulse calibration | 92 | built-before |
| configuration cell / cell | 95-96 | glossed-at-first-use |
| component | 97 | **FAILS — PED-02** |
| resolution bound / detection floor / cell floor | 98-102 | glossed-at-first-use |
| permitted edge movement | 104-105 | glossed-at-first-use |
| `U_point` / recorded-edge limit | 106-107 | glossed-at-first-use |
| `U_corner` / moved-edge limit | 108-110 | glossed-at-first-use |
| independent-edge ratio | 110-112 | glossed-at-first-use |
| four-run comparison / A/B/B/A block | 112-115 | glossed-at-first-use |
| timing-error sign | 115 | glossed-at-first-use |
| shared sign / local sign | 115-117 | glossed-at-first-use |
| `U_cmp,shared` / `U_cmp,point` / shared-error ratio | 117-120 | **FAILS — PED-03** |
| authentication | 124-125 | glossed-at-first-use |
| evaluation / evaluable | 125-126 | glossed-at-first-use |
| twofold boundary contribution | 127-129 | glossed-at-first-use |
| decision rule | 131-134 | glossed-at-first-use |
| interpolation edge | 825-830 | glossed-at-first-use |
| power sample / sampler record | 826-827 | glossed-at-first-use |
| deterministic-bound kinds | 830-834 | glossed-at-first-use |

No term newly re-homed by the ledger (`members`, `R_cm`, or `missing / malformed`) acquires an earlier use in selected A. The `[FILL:...]` count is 140 at `HEAD^` and 140 at `HEAD`; no marker was lost. Selector removal leaves 104 markers in selected A, as expected for discarded branches.

## Residual risk

The two permitted modules enforce ledger homes and selected exact gloss phrases, but they do not detect whether a nominal gloss is physically explanatory. This review was confined to terms introduced or materially re-homed by the changed hunks; unchanged prose was read in order only to detect late-arriving meanings.
