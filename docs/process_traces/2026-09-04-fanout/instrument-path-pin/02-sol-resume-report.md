```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "The governed r7 calibration-acceptance successor is issued and registered, and all 134 focused acceptance and production-path tests pass.",
  "workspace": {"base_requested":null,"base_mode":null,"head_start":"9c43947036479c55065567e14fbe1a85ab685918","head_end":"9c43947036479c55065567e14fbe1a85ab685918","upstream_end":"9c43947036479c55065567e14fbe1a85ab685918","branch":"feat/2026-09-04-instrument-path-pin"},
  "pathspec": ["configs/calibration/calibration_acceptance_d079_v2_n17_r7.json","docs/process_traces/2026-09-04-fanout/instrument-path-pin/02-sol-resume-report.md","docs/process_traces/2026-09-04-fanout/instrument-path-pin/issue_r7.py","joulewise/calibration_bracketing.py","tests/test_calibration_bracketing.py","tests/test_powermetrics_fiducial.py"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"ready"},
  "verification": [
    {"id":"V1","kind":"build","cmd":"python3 docs/process_traces/2026-09-04-fanout/instrument-path-pin/issue_r7.py . --check && git diff --check && python3 -m py_compile docs/process_traces/2026-09-04-fanout/instrument-path-pin/issue_r7.py joulewise/calibration_bracketing.py tests/test_calibration_bracketing.py tests/test_powermetrics_fiducial.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["CHECKED d079_calibration_acceptance_v2_n17_r7","PATH configs/calibration/calibration_acceptance_d079_v2_n17_r7.json","FILE_SHA256 40af3fb15745f626cb80d771085b17fe770c594076475257634f55bc3d7624f3","DERIVATION_SHA256 de35900ac6a6bf022a74eb4a656d226d04cf95ea728768ecbbc9ada1d437b9ce","PIN_MOVED joulewise/powermetrics_fiducial.py 386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92 -> f68650ede04bdc9088610fd6cd6a544f98707cee88428ae61fe91b2bfb8dce71"]},"expected":{"exit_code":0,"tail_regex":"^PIN_MOVED joulewise/powermetrics_fiducial\\.py .+ -> .+$"}},
    {"id":"V2","kind":"test","cmd":"python3 -m unittest tests.test_powermetrics_fiducial tests.test_calibration_bracketing tests.test_p2038_production_path","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 134 tests in 1493.101s","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"^OK \\(skipped=1\\)$"}}
  ],
  "flags": []
}
```

## Change

Added an exact-generation `r7` issuer following the established `r6` producer pattern. Its write mode authenticated the registered `r6` predecessor, required the sole changed governed source to be `joulewise/powermetrics_fiducial.py`, preserved every corpus and scientific field, and exclusively created the authorized successor. The executed issuance reported artifact SHA-256 `40af3fb15745f626cb80d771085b17fe770c594076475257634f55bc3d7624f3` and derivation SHA-256 `de35900ac6a6bf022a74eb4a656d226d04cf95ea728768ecbbc9ada1d437b9ce`.

Registered `r7` as the live acceptance generation while retaining `r6` under its original exact-byte pin. Updated the focused live-generation assertions and added an explicit retained-`r6` authentication check.

## Verification notes

The repository-wide suite was intentionally not run, as required by the preflight rule. V2 is the complete focused three-module boundary used by the prior report; its previously stale acceptance-artifact failure is resolved.
