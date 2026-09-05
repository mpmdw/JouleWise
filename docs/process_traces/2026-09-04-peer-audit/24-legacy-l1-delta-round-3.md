```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "LANDABLE: round 3 closes the rounds 1-2 missed-producer-route defect; all current RPT-001 producer and publication routes emit or project only the void disposition.",
  "workspace": {"base_requested":"5f9f9e26671531e6821423e71de6204ad227c2fa","base_mode":"exact","head_start":"5f9f9e26671531e6821423e71de6204ad227c2fa","head_end":"5f9f9e26671531e6821423e71de6204ad227c2fa","upstream_end":"5f9f9e26671531e6821423e71de6204ad227c2fa","branch":"feat/2026-09-04-legacy-l1"},
  "pathspec": ["docs/process_traces/2026-09-04-peer-audit/24-legacy-l1-delta-round-3.md"],
  "unowned_dirty": [],
  "verdict": {
    "decision": "LANDABLE",
    "same_signature": true,
    "signature": "Rounds 1-2 missed the --full producer behind a clean final-report fence; round 3 cures that same missed-producer-route class with producer-level void output plus an exact route census.",
    "open_same_signature_route": false,
    "findings": []
  },
  "verification": [
    {"id":"V1","kind":"build","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_capstone.py --profile rpt001 --full --offline --runs-root /Users/edr/code/JouleWise/runs","cwd":"/private/tmp/jw-legacy-l1-delta3.WkiyMK","observed":{"result":"pass","exit_code":0,"tail":["make_figures: OK — authenticated inputs; emitted void placeholders and voided claim row","claims_lint: clean","build_capstone: assembled build/capstone/rpt001/report.md sha256=a13fb1f89621f4b441d4f4a55958e1413a8063cf4757302756c9c26bfd9540a4"]},"expected":{"exit_code":0,"tail_regex":"assembled build/capstone/rpt001/report.md sha256=a13fb1f8"}},
    {"id":"V2","kind":"inspection","cmd":"sed 's#^#/private/tmp/jw-legacy-l1-delta3.WkiyMK/#' /private/tmp/jw-legacy-l1-delta3.WkiyMK/.produced-files | xargs rg -a -n -i -e '47\\.22042349222679|304\\.02005544776165|44\\.42591347410544|298\\.68731644234157|47\\.2|304\\.0|44\\.4|298\\.7|legacy L1 \\(manual review; pre-2M\\)|primary basis'","cwd":".","observed":{"result":"pass","exit_code":1,"tail":[]},"expected":{"exit_code":1,"tail_regex":"^$"}},
    {"id":"V3","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/claims_lint.py --mode claim-index --root kill --claims-index claims.jsonl --json","cwd":"/private/tmp/jw-legacy-l1-delta3.WkiyMK","observed":{"result":"pass","exit_code":2,"tail":["  \"ok\": false,","  \"warnings\": 0","}"]},"expected":{"exit_code":2,"tail_regex":"CLAIM_INDEX_UNKNOWN_DIALECT"}},
    {"id":"V4","kind":"inspection","cmd":"git diff --exit-code --stat origin/main -- analysis/rpt001-v1 figures/rpt001-v1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V5","kind":"build","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_capstone.py --profile rpt001 --offline --check","cwd":"/private/tmp/jw-legacy-l1-check3.JJeWrB","observed":{"result":"pass","exit_code":0,"tail":["build_capstone: check OK (no drift)"]},"expected":{"exit_code":0,"tail_regex":"check OK \\(no drift\\)"}},
    {"id":"V6","kind":"build","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/make_figures.py --runs-root /Users/edr/code/JouleWise/runs --input-manifest analysis/rpt001-v2/input_manifest.json --bootstrap-input-manifest --offline","cwd":"/private/tmp/jw-legacy-l1-bootstrap3.rF8Czp","observed":{"result":"pass","exit_code":0,"tail":["WARNING: --bootstrap-input-manifest RE-BASELINES EVIDENCE; review every changed hash.","make_figures: wrote analysis/rpt001-v2/input_manifest.json","make_figures: OK — authenticated inputs; emitted void placeholders and voided claim row"]},"expected":{"exit_code":0,"tail_regex":"emitted void placeholders and voided claim row"}},
    {"id":"V7","kind":"inspection","cmd":"rg -n -i --pcre2 '(?<![0-9.])(?:47\\.22042349222679|304\\.02005544776165|44\\.42591347410544|298\\.68731644234157|47\\.2|304\\.0|44\\.4|298\\.7)(?![0-9.])\\s*J|legacy L1 \\(manual review; pre-2M\\)|primary basis' docs/report_src docs/paper README.md","cwd":".","observed":{"result":"pass","exit_code":1,"tail":[]},"expected":{"exit_code":1,"tail_regex":"^$"}},
    {"id":"V8","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_rpt001_report_slice","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 19 tests in 11.741s","OK (skipped=2)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=2\\)"}},
    {"id":"V9","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_claims_index_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 30 tests in 8.066s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}}
  ],
  "flags": [
    {"id":"R1","kind":"residual_risk","level":"nonblocking","text":"The immutable v1 artifacts and superseded RPT-001 specification/history still contain the literal legacy values. They can be read directly, as required by the v1 immutability check, but D-078 makes those bytes non-claim-bearing; the report README describes them as voided history, and no current report or paper route renders them as results.","needs":"If policy changes from 'no current result route' to 'zero literal discoverability', separately reconcile/archive the superseded spec and historical documents without rewriting v1 evidence."},
    {"id":"R2","kind":"environment","level":"nonblocking","text":"The controlled corpus is absent from this worktree; full and bootstrap routes used the same /Users/edr/code/JouleWise/runs corpus as the refuter.","needs":""}
  ]
}
```

## Findings

None. The verdict is **LANDABLE**.

The tracked-only full replay produced exactly the census's twelve files: nine v2 analysis/figure artifacts, the Phase-4 projection, the generated report page, and the assembled report. Every file contained `void`; byte scans across all twelve found zero instances of the four full-precision means, four rounded forms, retired label, or `primary basis`. The canonical row is top-level `status: "voided"`; changing only that top-level field to `supported` made claim-index lint exit 2 with `CLAIM_INDEX_UNKNOWN_DIALECT`.

No additional current result route is open. The only production script paths are `make_figures.py` itself, `build_capstone.py` invoking it for `--full`, `claims_lint.py` reading the v2 row, and `release_check.py` invoking source-only `--check`; imports are test-only. Direct and bootstrap `make_figures` routes emit the same void outputs (bootstrap additionally rewrites result-free input identity metadata). `--full --check` composes those same producers. `docs/paper` has no RPT-001 artifact reference, while its artifact guide invokes only safe `--check`. Root/report READMEs describe v1 as immutable voided history and do not project its values or individual result artifacts.

Same-signature answer: **yes**, round 3 addresses the same missed-producer-route class that defeated rounds 1-2; **no**, no current producer/publication route of that class remains open.

## Residual risk

Sealed v1 and superseded historical/specification text intentionally remain readable and contain the old numbers. In particular, the report README names the amended RPT-001 spec, whose sealed-v1 context retains them. That is historical replay surface, not a current producer or eligible-result projection; a zero-literal policy would require a separate documentation ruling because v1 itself must remain byte-identical.
