```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Reclassified the F+B expression as a non-gating planning formula while preserving the legacy wire key and the implemented two-gate rule.",
  "workspace": {"base_requested":"8e8e3506","base_mode":"exact","head_start":"8e8e3506d779bfc62530cf81fdc1d736281fccab","head_end":"8e8e3506d779bfc62530cf81fdc1d736281fccab","upstream_end":null,"branch":"feat/2026-09-04-fb-metadata"},
  "pathspec": ["joulewise/detection_floor.py","tests/test_detection_floor.py","tests/test_analysis_claims.py","docs/process_traces/2026-09-04-peer-audit/31-fb-metadata-seat-report.md"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"ready"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_detection_floor","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 160 tests in 2.608s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_claims","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 60 tests in 0.304s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}}
  ],
  "flags": [
    {"id":"F1","kind":"verification_gap","level":"nonblocking","text":"The runner preflight prohibited the discovery suite and limited execution to the two focused modules, one at a time.","needs":"Lead owns any broader verification."}
  ]
}
```

## Change

The canonical discipline now emits `planning_sizing_formula`, `gating: false`, and a one-sentence two-gate note. The legacy formula remains byte-for-byte under `effective_clearable_effect_formula` and points to the planning key through `deprecated_alias_of`; `both_terms_required` is unchanged. The focused consumer scan found propagation or equality-to-canonical-emitter validation, with no closed nested key schema. The regression witness asserts 6 J is below the 5 J + 4 J planning sum yet remains `direction_supported` and claim-ready, killing an additive-gate mutation.

## Verification notes

The discovery suite was not run by explicit preflight rule.
