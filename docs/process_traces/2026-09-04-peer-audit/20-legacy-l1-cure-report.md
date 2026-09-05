```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Cured the capstone producer so the legacy L1 page is an unmistakable VOIDED historical pipeline demonstration with no energy results.",
  "workspace": {"base_requested":"5e416c47","base_mode":"exact","head_start":"5e416c47b6236e66eeb861584ad19aeff4e012a4","head_end":"5e416c47b6236e66eeb861584ad19aeff4e012a4","upstream_end":null,"branch":"feat/2026-09-04-legacy-l1"},
  "pathspec": ["scripts/build_capstone.py","docs/report_src/chapters/07_results.md","docs/report_src/generated/rpt001_vertical_slice.md","docs/report_src/README.md","tests/test_build_capstone.py","docs/process_traces/2026-09-04-peer-audit/20-legacy-l1-cure-report.md"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"ready"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_build_capstone","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["..","----------------------------------------------------------------------","Ran 2 tests in 0.000s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 2 tests in [0-9.]+s\\n\\nOK"}},
    {"id":"V2","kind":"build","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build_capstone.py --profile rpt001 --offline --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["build_capstone: check OK (no drift)"]},"expected":{"exit_code":0,"tail_regex":"build_capstone: check OK \\(no drift\\)"}},
    {"id":"V3","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nfrom pathlib import Path\npage = Path('docs/report_src/generated/rpt001_vertical_slice.md').read_text(encoding='utf-8')\nassert '## VOIDED' in page\nassert 'Evidence class: **VOIDED' in page\nassert 'README void disposition' in page\nassert '| stack_id |' not in page\nassert '![' not in page\nfor forbidden in ('47.2', '304.0', 'primary'):\n    assert forbidden not in page.lower()\nprint('void fence inspection: OK')\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["void fence inspection: OK"]},"expected":{"exit_code":0,"tail_regex":"void fence inspection: OK"}},
    {"id":"V4","kind":"lint","cmd":"python3 -B - <<'PY'\nimport subprocess\nsubprocess.run(['git', 'diff', '--check'], check=True)\nprint('diff-check: OK')\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["diff-check: OK"]},"expected":{"exit_code":0,"tail_regex":"diff-check: OK"}}
  ],
  "flags": [
    {"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Per the mandatory preflight, the discovery suite and existing legacy report test module were not run.","needs":"Lead owns broader verification."},
    {"id":"F2","kind":"residual_risk","level":"nonblocking","text":"tests/test_rpt001_report_slice.py retains assertions for the superseded results table and label; it was outside this session's write scope.","needs":"Lead should retire those obsolete assertions in a separately authorized change before expecting the broader suite to pass."}
  ]
}
```

## Change

The producer now emits a README-linked VOIDED evidence class, no energy table or values, and only a provenance statement for the retained historical figure. Report-source guidance matches that disposition. Two focused tests cover the generated artifact and prove that injecting the pre-cure label kills the void-fence assertion.

## Verification notes

Verification followed the caller's focused-test restriction; no discovery suite, agent launcher, historical evidence regeneration, or quiet-machine work ran.

## Residual risk

The older report-slice test still encodes the now-forbidden table and label. It was preserved because it was outside the exhaustive write scope.
