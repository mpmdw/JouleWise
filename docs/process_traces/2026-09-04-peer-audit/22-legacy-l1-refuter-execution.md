```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REFUTED: the final capstone Markdown is fenced, but its full publication route still regenerates and lint-accepts a supported legacy L1 claim projection containing the voided energy values.",
  "workspace": {"base_requested":"a379b5aff212de05356048a6bd410dcf4a3fedaf","base_mode":"exact","head_start":"a379b5aff212de05356048a6bd410dcf4a3fedaf","head_end":"a379b5aff212de05356048a6bd410dcf4a3fedaf","upstream_end":"a379b5aff212de05356048a6bd410dcf4a3fedaf","branch":"feat/2026-09-04-legacy-l1"},
  "pathspec": ["docs/process_traces/2026-09-04-peer-audit/22-legacy-l1-refuter-execution.md"],
  "unowned_dirty": [],
  "verdict": {
    "claim": "REFUTED",
    "findings": [
      {"id":"F1","severity":"blocker","text":"scripts/build_capstone.py --full invokes make_figures.py and claims_lint.py --write-projection. That live route regenerates analysis/rpt001-v2/claims_index.jsonl with status=supported, strict_validation.result=passed, the retired legacy label, and idle-subtracted values 44.42591347410544 J / 298.68731644234157 J; it also regenerates docs/phase_4/claims_index.md with those values and L1/supported. Phase-4 lint exits 0 and only warns that the grandfathered row was skipped. This is a current publication route assembling the voided values as a supported result."},
      {"id":"F2","severity":"should_fix","text":"The same producer regenerates Table T1 with gross means 47.2 J / 304.0 J and companions 44.4 J / 298.7 J, plus F1_legacy_l1_instrument_results.svg with the retired label and 'idle-subtracted energy_request_j (primary basis)'. The assembled capstone and paper sources do not render that figure, but the full route regenerates and manifest-pins it."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"build","cmd":"python3 scripts/build_capstone.py --profile rpt001 --offline --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["build_capstone: check OK (no drift)"]},"expected":{"exit_code":0,"tail_regex":"check OK"}},
    {"id":"V2","kind":"build","cmd":"python3 scripts/build_capstone.py --profile rpt001","cwd":"/private/tmp/jw-legacy-l1-refuter-a379b5af.UQxkah","observed":{"result":"pass","exit_code":0,"tail":["build_capstone: assembled build/capstone/rpt001/report.md sha256=a4970342b014224e573aea811580c47e24ed690edc1fe803f2437ea464a14c12"]},"expected":{"exit_code":0,"tail_regex":"assembled .*sha256="}},
    {"id":"V4","kind":"build","cmd":"python3 scripts/build_capstone.py --profile rpt001 --full --offline --runs-root /Users/edr/code/JouleWise/runs","cwd":"/private/tmp/jw-legacy-l1-refuter-a379b5af.UQxkah","observed":{"result":"pass","exit_code":0,"tail":["warning   claim-index  analysis/rpt001-v2/claims_index.jsonl:1  CLAIM_INDEX_PRE_P2037_LEGACY_SKIPPED  pre-P2-037 manual-review L1 row has no governed verdict artifact","build_capstone: assembled build/capstone/rpt001/report.md sha256=a4970342b014224e573aea811580c47e24ed690edc1fe803f2437ea464a14c12"]},"expected":{"exit_code":0,"tail_regex":"assembled .*sha256="}},
    {"id":"V5","kind":"build","cmd":"python3 scripts/make_figures.py --runs-root /Users/edr/code/JouleWise/runs --input-manifest analysis/rpt001-v2/input_manifest.json --offline","cwd":"/private/tmp/jw-legacy-l1-refuter-a379b5af.UQxkah","observed":{"result":"pass","exit_code":0,"tail":["make_figures: OK — dataset, aggregates, figure, T1, S1, claims row, artifact manifest"]},"expected":{"exit_code":0,"tail_regex":"make_figures: OK"}},
    {"id":"V6","kind":"lint","cmd":"python3 scripts/claims_lint.py --mode phase4 --write-projection","cwd":"/private/tmp/jw-legacy-l1-refuter-a379b5af.UQxkah","observed":{"result":"pass","exit_code":0,"tail":["warning   claim-index  analysis/rpt001-v2/claims_index.jsonl:1  CLAIM_INDEX_PRE_P2037_LEGACY_SKIPPED  pre-P2-037 manual-review L1 row has no governed verdict artifact"]},"expected":{"exit_code":0,"tail_regex":"CLAIM_INDEX_PRE_P2037_LEGACY_SKIPPED"}},
    {"id":"V7","kind":"inspection","cmd":"rg -n -i '47\\.2|44\\.4|304\\.0|298\\.7|legacy L1 \\(manual review; pre-2M\\)|primary basis|per-output-token|energy_output_token_j' docs/report_src/generated/rpt001_vertical_slice.md build/capstone/rpt001/report.md","cwd":"/private/tmp/jw-legacy-l1-refuter-a379b5af.UQxkah","observed":{"result":"pass","exit_code":1,"tail":[]},"expected":{"exit_code":1,"tail_regex":"^$"}},
    {"id":"V8","kind":"inspection","cmd":"rg -n -i '47\\.2|44\\.4|304\\.0|298\\.7|primary basis|legacy L1 \\(manual review; pre-2M\\)' docs/report_src","cwd":".","observed":{"result":"pass","exit_code":1,"tail":[]},"expected":{"exit_code":1,"tail_regex":"^$"}},
    {"id":"V9","kind":"inspection","cmd":"rg -n -i --pcre2 '(?<![0-9.])(?:47\\.2|44\\.4|304\\.0|298\\.7)(?![0-9.])\\s*J|primary basis|legacy L1 \\(manual review; pre-2M\\)' docs/paper","cwd":".","observed":{"result":"pass","exit_code":1,"tail":[]},"expected":{"exit_code":1,"tail_regex":"^$"}},
    {"id":"V10","kind":"test","cmd":"python3 -m unittest tests.test_build_capstone","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 0.000s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V11","kind":"test","cmd":"python3 -m unittest tests.test_rpt001_report_slice","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 19 tests in 0.234s","OK (skipped=3)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=3\\)"}},
    {"id":"V12","kind":"test","cmd":"python3 -c 'from tests.test_build_capstone import BuildCapstoneVoidFenceTests, PRE_CURE_LABEL, build_capstone; build_capstone.LEGACY_LABEL = PRE_CURE_LABEL; BuildCapstoneVoidFenceTests().assert_voided_results_page(build_capstone.generate_results_page())'","cwd":"/private/tmp/jw-legacy-l1-refuter-a379b5af.UQxkah","observed":{"result":"pass","exit_code":1,"tail":["AssertionError: 'VOIDED' not found in 'legacy L1 (manual review; pre-2M)'"]},"expected":{"exit_code":1,"tail_regex":"AssertionError: 'VOIDED' not found"}},
    {"id":"V13","kind":"smoke","cmd":"python3 scripts/build_capstone.py --profile __refuter_unknown__ --check","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["build_capstone: ERROR: unknown profile: __refuter_unknown__"]},"expected":{"exit_code":1,"tail_regex":"unknown profile"}}
  ],
  "flags": [
    {"id":"R1","kind":"residual_risk","level":"nonblocking","text":"No current capstone or docs/paper renderer was found to inline the stale legacy figure; the refutation rests on the full route's supported claims artifacts and projection, not on the final report Markdown.","needs":"Lead should void or retire the producer/claims row and make lint hard-fail it before reasserting the global claim."},
    {"id":"R2","kind":"environment","level":"nonblocking","text":"This worktree has no runs/ directory; full mode was replayed in a scratch copy of the exact head against the existing controlled corpus at /Users/edr/code/JouleWise/runs.","needs":""}
  ]
}
```

## Findings

F1 — blocker. The claim is REFUTED. `build_capstone --full` still regenerates a human-readable L1/`supported` claims projection containing 44.42591347410544 J and 298.68731644234157 J. Its canonical JSONL says `status: supported` and strict validation passed; the linter exits 0 after skipping it as grandfathered. The final assembled Markdown is clean, but the global “no publication route” assertion is false.

F2 — should_fix. The producer also regenerates the 47.2 J / 304.0 J table and a manifest-pinned figure carrying the retired label and “primary basis.” Exact semantic greps of `docs/report_src` and `docs/paper` were clean, and no current renderer reference to the figure was found.

## Residual risk

The capstone's default and full final Markdown both omit the values, old label, and figure. Regeneration of `rpt001_vertical_slice.md` remains clean, and the producer-label kill test bites. The remaining exposure is the separately generated claims/table/figure publication surface accepted by the full route.
