```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Applied the cold-gate round-2 first-use cures, repaired the one cure-local late label, and passed the two authorized paper tests.",
  "workspace": {"base_requested":"21374496","base_mode":"exact","head_start":"213744968b6aa11c7161f9fa4d836421b5e43d41","head_end":"213744968b6aa11c7161f9fa4d836421b5e43d41","upstream_end":"213744968b6aa11c7161f9fa4d836421b5e43d41","branch":"feat/2026-09-04-paper-h"},
  "pathspec": ["docs/paper/draft-v2-skeleton.md","docs/process_traces/2026-09-04-paper-h/07-sol-fix-round-2-report.md"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"ready"},
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"tmp_dir=$(mktemp -d /private/tmp/paper-h-round2-audit.XXXXXX) && python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output \"$tmp_dir/selected-a.md\" --outcome A","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200"]},"expected":{"exit_code":0,"tail_regex":"selected A: .*abstract_words=200"}},
    {"id":"V2","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[".............","----------------------------------------------------------------------","Ran 13 tests in 2.713s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 13 tests in .*s\\n\\nOK"}}
  ],
  "flags": [
    {"id":"F1","kind":"residual_risk","level":"nonblocking","text":"Selected-A Abstract line 25 retains the frozen phrase 'required calculation' without the Section-1 twelve-ratio enumeration, as the ruling expressly places that text outside seat H.","needs":"Abstract owner records or cures the note in its authorized seat."}
  ]
}
```

## Change

Applied Q3's two replacements, Q4's CR-02 and CR-03 replacements, the Section-4 terminology unification, and CR-04's one-word rename. Added ledger rows for `power-measurement boundary` and `twelve required ratios`; the exact mechanical count is now 268 with zero `FAILS`.

The first CR-03 transcription used the ruled words “absolute and comparative” / “comparative components.” The required reading-order check showed that `comparative component` was first defined later in Section 4; the first authorized test run confirmed the same home mismatch. Under the brief's cure-local fallback, only that ruled sentence was amended to name its already-built physical sources: “within-model repeat and four-run comparison” and “four-run comparison components.” No other prose changed.

Selected A was produced at `/private/tmp/paper-h-round2-audit.k3NJzx/selected-a.md`. Cure audit (line references are to that selected file):

- CR-02 configuration-cell sentence, lines 78–81: `configuration cell`, `cell`, `set`, and `runs` are constructed there; `phase` and `energy` are built at 34–45; `model` at 52; machine/hardware, software, and workload at 50–54; `macOS`, `power sampler`, and `processor power` at 31–33; `power-measurement boundary`, counted `power`, and `wall outlet` are glossed in the cure itself at 79–81 (the outlet contrast also appears at 25).
- Q3 four-run-comparison sentence, lines 82–85: `cell` is built at 78–81; `measurement`, `model`, and `phase energy` at 31–45 and 50–52; `spread`, `repeat`, and averaging/mean subtraction are physically built at 46–48 and 82–83; `four-run model comparison`, its `runs`, `difference`, `result`, and division by the symbol `two` are built by the calculation at 83–85.
- Q3 A/B/B/A sentence, lines 103–104: `timing error` is present at 25 and 102; `runs`/`repeat` at 46–48; the symbols/labels `A` and `B`, `A/B/B/A block`, `order`, and `conditions` are introduced and glossed in that sentence; the conditions are identified as the two `models`, built at 52.
- Timing-error-sign sentence, line 105: `timing error` is built at 102; the label `timing-error sign` and noun `direction` are glossed in the sentence; allowed error/edge movement is built at 61–64 and 93–100; `energy` is built at 43–45.
- CR-04 symbol sentence, lines 108–110: `U_cmp,point`, `four-run comparison`, and `recorded-edge limit` are built at 83–85 and 95–96/108; `U_cmp,shared` is defined at 109–110; `timing-error sign` at 105; `block` at 103–104; `local sign` at 106–107; and `limit` at 61–62 and 95–99.
- CR-03 falsifier sentence, lines 118–119: `ratio` is built at 99–100 and 111–112; the label `twelve required ratios` is glossed within the same paragraph at 119–122; the symbol `2` and the decision nouns `claim` and `equality` are given their operative falsify/pass meaning at 118–124.
- CR-03 enumeration sentence, lines 119–122: `independent-edge ratio` is built at 99–100; `component` at 86–87; `models` at 52; `phases` at 34–45; `within-model repeat` at 46–48 and 82–83; `four-run comparison` at 83–85; `shared-error ratio` at 108–112; and the count symbols `twelve`, `eight`, `two`, and `four` are resolved by the enumeration itself. No label first built later remains.
- CR-02 Section-4 rename sentence, lines 469–470: `cell`, `runs`, `phase`, `workload`, `model`, hardware/machine, `software`, and `power-measurement boundary` are all built at 34–54 and 78–81. The sentence introduces no new noun, symbol, or label.

## Verification notes

The first authorized run failed only `absolute component / comparative component` home placement because the exact ruling text introduced `comparative components` in Section 1. After the cure-local wording repair above, the same two-module command passed. `git diff --check` also passed.

## Residual risk

The selected-A Abstract still says “required calculation” at line 25. The cold-gate ruling freezes that digest and assigns the nonblocking first-use note to the Abstract owner; seat H did not alter it.
