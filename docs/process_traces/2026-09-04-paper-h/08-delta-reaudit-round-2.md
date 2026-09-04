```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "RESIDUAL: four round-2 cure-local meanings arrive on later selected-A lines, so same_signature is YES and Q5 returns the lane to a cold gate.",
  "workspace": {"base_requested":"dfdef440","base_mode":"exact","head_start":"dfdef4400400b0dec32b1a33e3ff86800262be20","head_end":"dfdef4400400b0dec32b1a33e3ff86800262be20","upstream_end":null,"branch":null},
  "pathspec": ["docs/process_traces/2026-09-04-paper-h/08-delta-reaudit-round-2.md"],
  "unowned_dirty": [],
  "verdict": {
    "result": "RESIDUAL",
    "same_signature": "YES",
    "landable": false,
    "findings": [
      {"id":"R2-01","severity":"blocker","location":"selected A:79-81,103-104,109-110,118-122","text":"Round-2 cure words and symbols precede their line-granular build or gloss; Q5.4 requires a cold gate."},
      {"id":"R2-02","severity":"blocker","location":"docs/paper/draft-v2-skeleton.md:134","text":"The implemented CR-03 enumeration does not match the exact Q4 text required by Q5.1."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /private/tmp/paper-h-delta-reaudit-r2.iGt8Hw/selected-a.md --outcome A","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200"]},"expected":{"exit_code":0,"tail_regex":"selected A: .*abstract_words=200"}},
    {"id":"V2","kind":"inspection","cmd":"python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /private/tmp/paper-h-delta-reaudit-r2.iGt8Hw/selected-b.md --outcome B","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["selected B: transfer_slots=3, failed_component_slots=3, verdict_slots=4, refusal_reason_slots=1, abstract_words=209"]},"expected":{"exit_code":0,"tail_regex":"selected B: .*abstract_words=209"}},
    {"id":"V3","kind":"inspection","cmd":"python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /private/tmp/paper-h-delta-reaudit-r2.iGt8Hw/selected-refusal.md --outcome REFUSAL","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["selected REFUSAL: transfer_slots=3, failed_component_slots=0, verdict_slots=1, refusal_reason_slots=4, abstract_words=222"]},"expected":{"exit_code":0,"tail_regex":"selected REFUSAL: .*abstract_words=222"}},
    {"id":"V4","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 13 tests in 2.752s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 13 tests in .*s\\n\\nOK"}},
    {"id":"V5","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PAPER_FIRST_USE_DRAFT=/private/tmp/paper-h-delta-reaudit-r2.iGt8Hw/selected-a.md python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 1.636s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 10 tests in .*s\\n\\nOK"}},
    {"id":"V6","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PAPER_FIRST_USE_DRAFT=/private/tmp/paper-h-delta-reaudit-r2.iGt8Hw/selected-b.md python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 1.638s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 10 tests in .*s\\n\\nOK"}},
    {"id":"V7","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PAPER_FIRST_USE_DRAFT=/private/tmp/paper-h-delta-reaudit-r2.iGt8Hw/selected-refusal.md python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 1.619s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 10 tests in .*s\\n\\nOK"}},
    {"id":"V8","kind":"inspection","cmd":"rg -o '\\[FILL' docs/paper/draft-v2-skeleton.md | wc -l; git show HEAD^:docs/paper/draft-v2-skeleton.md | rg -o '\\[FILL' | wc -l","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["140","140"]},"expected":{"exit_code":0,"tail_regex":"140\\n140"}}
  ],
  "flags": [
    {"id":"G1","kind":"lead_ruling","level":"blocking","text":"same_signature: YES; Q5.4 forbids a discretionary round 3.","needs":"Do not merge dfdef440; return the lane to a fresh cold gate."}
  ]
}
```

## Findings

- **R2-01 — blocker — same_signature: YES.** I generated selected A with the selector and read lines 1–904 in order, title through the end of Section 4. The cure-sentence inventory below lists every noun, symbol, and label; “self” means built in that cure rather than earlier prose.

  - CR-02 introduction, selected A 78–81: `configuration cell`/`cell`/`set` (self, 78); `runs` (46–48); `phase` (34–45); `workload` (54); `model` (31–32, 52); `hardware`/`software` (50–54); `power-measurement boundary` (first 79, gloss 80–81: **late**); `power`/`processor power`/`macOS` (31–45); `wall outlet` (25).
  - Q3 comparison, 83–85: `four-run model comparison` (25, 31–32); `difference`/`result` and subtraction/division operation (25, 82–85 self); `phase energies` (43–45, 82); `runs` (46–48, 78); `model` (52); count labels `four`, `two`, `one`/`other` (25, self). No later build.
  - Q3 A/B/B/A, 103–104: `A/B/B/A block`/`block`/`order` (self, 103–104); `runs` (46–48, 78); symbols/labels `A` and `B` (first 103, identified as model labels 104: **late**); `conditions` (self-mapped at 104); `models` (52); count labels `four`/`two` (25, self).
  - CR-04 renamed occurrence, 108–110: symbols `U_cmp,point` (self-defined 108) and `U_cmp,shared` (first 109, replay semantics completes 110: **late**); `four-run comparison` (83–85); `recorded-edge limit`/`limit` (61–62, 95–99); `timing-error sign` (105); `blocks` (103); `local sign` (106–107).
  - CR-03 falsifier, 118–119: `ratio` (99–112); count symbol `2` (116); `twelve required ratios` (first 118, enumerated 119–122: **late**); `claim`/`equality` (self-operational at 119).
  - CR-03 enumeration, 119–122: count labels `twelve`/`one`/`eight`/`two`/`four` (self-enumerated 119–122); `independent-edge ratio` (100); `components` (86–87); `models` (52); `phases`/`phase energy` (34–45); `within-model repeat` (46–48, 82–83); `four-run comparison` (83–85); `shared-error ratio` (111–112); `four-run comparison components` (83–87). No additional later build.
  - CR-02 Section-4 rename, 469–470: `cell` (78); `runs` (46–48); `phase` (34–45); `workload` (54); `model` (52); `hardware`/`software` (50–54); `power-measurement boundary` (79–81). This occurrence is later than the introduction, though that introduction itself fails line granularity.

  The authorized tests pass because their gloss check joins wrapped paragraph lines; that does not satisfy ruling Q2's explicit later-*line* prohibition. The named ledger rows exist at selected-A 1694 and 1698, and their Introduction homes match the true first reader-facing uses at 79 and 118. Their `glossed-at-first-use` statuses are nevertheless false under the binding line rule.

- **R2-02 — blocker.** Q5.1 requires Q4's exact CR-03 text. The ruling says `absolute and comparative` and `four comparative components`; HEAD instead says `within-model repeat and four-run comparison` and `four four-run comparison components` (selected A 120–122; skeleton 134–136). The exact ruled terms `absolute component` and `comparative component` are first built only at selected-A 471–472, which explains the implementer's substitution but does not authorize it.

The literal `[FILL` count is unchanged at 140 before and after `dfdef440`. The two authorized modules pass, and the ledger test passes with `PAPER_FIRST_USE_DRAFT` set separately to A, B, and REFUSAL.

## Residual risk

This delta re-audit covers the round-2 cures only. CR-05 through CR-08 and the ruling's frozen Abstract note remain outside this seat, as Q4 directs.
