```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "verdict": {
    "result": "CLEAN",
    "findings": [],
    "dispositions": [
      {"id":"PED-01","result":"CURED"},
      {"id":"PED-02","result":"CURED"},
      {"id":"PED-03","result":"CURED"},
      {"id":"FACT-01","result":"CURED"}
    ],
    "same_signature": "NONE SURVIVE; no same-signature escalation is triggered."
  },
  "status": "clean",
  "completion": "complete",
  "summary": "All four round-1 findings are cured without an introduced defect; exact ledger, fill-marker, and Abstract-budget checks pass.",
  "workspace": {
    "base_requested": "9bec33b4f1040a7d467578e7b7e6ecb9da346214",
    "base_mode": "exact",
    "head_start": "9bec33b4f1040a7d467578e7b7e6ecb9da346214",
    "head_end": "9bec33b4f1040a7d467578e7b7e6ecb9da346214",
    "upstream_end": "9bec33b4f1040a7d467578e7b7e6ecb9da346214",
    "branch": "feat/2026-09-04-paper-h"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-paper-h/04-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["..........","----------------------------------------------------------------------","Ran 10 tests in 1.708s","","OK"]},
      "expected": {"exit_code":0,"tail_regex":"Ran 10 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["...","----------------------------------------------------------------------","Ran 3 tests in 1.394s","","OK"]},
      "expected": {"exit_code":0,"tail_regex":"Ran 3 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "review_tmp_dir=$(mktemp -d /private/tmp/paper-h-delta-r1.XXXXXX); for outcome in A B REFUSAL; do PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output \"$review_tmp_dir/$outcome.md\" --outcome \"$outcome\" || exit; done",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200","selected B: transfer_slots=3, failed_component_slots=3, verdict_slots=4, refusal_reason_slots=1, abstract_words=209","selected REFUSAL: transfer_slots=3, failed_component_slots=0, verdict_slots=1, refusal_reason_slots=4, abstract_words=222"]},
      "expected": {"exit_code":0,"tail_regex":"selected A: .*abstract_words=200\\nselected B: .*abstract_words=209\\nselected REFUSAL: .*abstract_words=222"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show HEAD^:docs/paper/draft-v2-skeleton.md | rg -o '\\[FILL:[^]]+\\]' | wc -l; rg -o '\\[FILL:[^]]+\\]' docs/paper/draft-v2-skeleton.md | wc -l; rg -n \"Terms inventoried:|FAILS:\" docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["140","140","1997:a failure. Terms inventoried: 266; FAILS: 0."]},
      "expected": {"exit_code":0,"tail_regex":"140\\s+140\\s+1997:a failure\\. Terms inventoried: 266; FAILS: 0\\."}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "sed -n '74,80p;218,232p;1457,1463p;1625,1645p' docs/paper/draft-v2-skeleton.md; rg -n '\"event_type\": \"pulse_command_(on|off)\"' /Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/events.jsonl | sed -n '19,20p'; sed -n '20,50p' docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["\"member_id\": \"20260722T145535-e941c821\",","\"projection_evaluated_cell_count\": 122859,","\"pulse_count\": 59,","\"v3_disposition\": \"bounded\""]},
      "expected": {"exit_code":0,"tail_regex":"projection_evaluated_cell_count.*122859[\\s\\S]*pulse_count.*59[\\s\\S]*v3_disposition.*bounded"}
    }
  ],
  "flags": [
    {"id":"F1","kind":"residual_risk","level":"nonblocking","text":"The selected Abstracts are still unfilled; later substitutions can increase rendered word counts.","needs":"Rerun the selector with --check-rendered after filling."}
  ]
}
```

## Findings

No blocker, should-fix, or nit survives, and inspection of `git show HEAD -- docs/paper` found no defect introduced by the fix.

| Finding | Disposition | New first-use sentence / factual replacement | Assessment |
|---|---|---|---|
| PED-01 | **CURED** | “A rate-aware clock mapping does not assume that the computer's wall clock and its monotonic clock—a counter that advances but is never corrected to civil time—advance at exactly the same rate.” | **BUILDS** the term from the physical situation: an advancing counter is distinguished from civil time by the absence of correction. It does not merely attach a dictionary synonym. |
| PED-02 | **CURED** | “JouleWise bounds each source separately; each separately bounded source is a component.” | **BUILDS** the term: the two preceding sentences first construct the sources from same-model phase-energy spread and the four-run \((B_1+B_2-A_1-A_2)/2\) difference, then this sentence names each separately bounded source. |
| PED-03 | **CURED** | “Shared movement uses a different numerator: let \(U_{\mathrm{cmp,point}}\) be the four-run comparison's recorded-edge limit, and let \(U_{\mathrm{cmp,shared}}\) be its largest limit after one calibration-error sign is replayed across all blocks and one local sign is chosen per block.” | **BUILDS** both symbols from the physical calculation before printing the quotient: recorded edges versus one globally replayed calibration sign plus per-block local signs. |
| FACT-01 | **CURED** | “To measure the edge problem rather than assume its size, JouleWise records command timestamps for GPU pulses whose physical onset is observed in the power record.” | The sentence no longer equates command time with controlled physical-edge time. The cited issued `events.jsonl` contains distinct on/off command stamps; draft lines 218 and 232 define fitted lag as observed edge minus command and report nonzero onset/offset intervals; Appendix A.3.1/A.3.5 defines independently stamped commands and a power-record-fitted accepted edge region. The issued re-derivation authenticates the capture, 59 pulses, and bounded fit. |

New-defect audit: none of the four changed passages introduces a later-dependent term. `monotonic clock` is physically built in its first sentence; the two component sources precede `component`; `recorded-edge limit`, four-run comparison, sign, and block are already built before the two `U_cmp` assignments. `[FILL:...]` markers are unchanged at 140 in `HEAD^` and `HEAD`. The selector reports Abstract A/B/REFUSAL at 200/209/222 words, all within the 250-word budget. The ledger test proves its printed count equals its parsed row count; the exact sentence is `Terms inventoried: 266; FAILS: 0.`

Same-signature statement: **NONE SURVIVE**. The three later-dependent/dictionary-style pedagogy classes are killed by physical construction at first use, and the command-time/physical-edge equivalence is killed by expressly separating recorded command timestamps from the onset fitted in the power record. No second consecutive same-signature failure exists, so the escalation trigger does not fire.

## Residual risk

The Abstract figures are pre-fill counts. Final substituted prose still requires the selector's `--check-rendered` budget check. Per the prescribed preflight, no broader test suite was run.
