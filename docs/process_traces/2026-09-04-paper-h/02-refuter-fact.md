```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "FACT-01",
        "severity": "should_fix",
        "location": "docs/paper/draft-v2-skeleton.md:74",
        "text": "The new claim that JouleWise creates edges ‘whose physical times it controls’ is not traceable to the registry or issued evidence and conflicts with the paper's issued diagnostic evidence. The harness records command stamps; the fitted physical response may lag them. The retained capture at lines 212 and 226 reports onset and offset lag intervals, and Appendix A.3 at lines 1451 and 1634 distinguishes commanded stamps from allowed fitted edge positions.",
        "exact_cure_shape": "Replace lines 74–75 with: ‘To measure the edge problem rather than assume its size, JouleWise uses recorded command times as reference points for GPU-pulse edges.’ Keep the following first-use definition of commanded graphics-processor pulses."
      }
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FACT refutation found one unsupported command-time/physical-edge equivalence; all authorized regression checks pass.",
  "workspace": {
    "base_requested": "daf696f5",
    "base_mode": "exact",
    "head_start": "daf696f58e376d67ea6fbd08fe68039314e3f674",
    "head_end": "daf696f58e376d67ea6fbd08fe68039314e3f674",
    "upstream_end": "daf696f58e376d67ea6fbd08fe68039314e3f674",
    "branch": null
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-paper-h/02-refuter-fact.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["..........", "----------------------------------------------------------------------", "Ran 10 tests in 1.729s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["...", "----------------------------------------------------------------------", "Ran 3 tests in 1.390s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "review_tmp_dir=$(mktemp -d /tmp/paper-h-refuter.XXXXXX); for outcome in A B REFUSAL; do python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output \"$review_tmp_dir/$outcome.md\" --outcome \"$outcome\"; done; rm \"$review_tmp_dir/A.md\" \"$review_tmp_dir/B.md\" \"$review_tmp_dir/REFUSAL.md\"; rmdir \"$review_tmp_dir\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200",
          "selected B: transfer_slots=3, failed_component_slots=3, verdict_slots=4, refusal_reason_slots=1, abstract_words=209",
          "selected REFUSAL: transfer_slots=3, failed_component_slots=0, verdict_slots=1, refusal_reason_slots=4, abstract_words=222"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "selected A: .*abstract_words=200\\nselected B: .*abstract_words=209\\nselected REFUSAL: .*abstract_words=222"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show HEAD -- docs/paper",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["-a failure. Terms inventoried: 265; FAILS: 0.", "+a failure. Terms inventoried: 266; FAILS: 0."]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Terms inventoried: 266; FAILS: 0\\."
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The selector counts the currently unfilled Abstract; later substitutions can change the rendered word count.",
      "needs": "Rerun select_outcome_branches.py --check-rendered on the fully filled draft."
    }
  ]
}
```

## Findings

### FACT-01 — should_fix

At [docs/paper/draft-v2-skeleton.md:74](../../paper/draft-v2-skeleton.md), “edges whose physical times it controls” collapses the commanded reference time into the physical GPU-response edge. That equivalence is neither registered nor supported by the issued diagnostic capture: the paper itself records nonzero fitted onset and offset lag relative to the commands. Apply the exact replacement in `verdict.findings[0].exact_cure_shape`; no number or outcome branch needs to change.

All other changed factual statements are definitions or frozen method/identity claims traceable through the registry's `DRAFT`, `AUTH`, `D165`, `PANEL`, and `WORKLOAD` sources. The only numeric text change is the mechanical ledger count, 265 to 266, matching the 266 parsed rows and `FAILS: 0`. Inspection of `git show HEAD -- docs/paper` found no changed hunk inside any Abstract, Discussion, or Conclusion `OUTCOME-BRANCH` group; those groups remain byte-identical to the parent.

## Residual risk

The selected unfilled Abstracts are within the 250-word budget at 200, 209, and 222 words. Final filled prose must still pass the selector's `--check-rendered` mode because substituted result text can increase those counts.
