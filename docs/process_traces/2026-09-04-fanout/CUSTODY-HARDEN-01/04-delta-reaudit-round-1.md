```json
{
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": [],
    "closures": [
      {"id":"F1","disposition":"CURED","evidence":"The exact sibling-manifest regression passes at HEAD; restoring the pre-fix *.json registry scan makes it fail because untracked.json authenticates."},
      {"id":"F2","disposition":"CURED","evidence":"Both required site-specific regressions pass at HEAD; independently removing the mint postcondition or the claim-row require_corpus_identity argument makes its corresponding regression fail."},
      {"id":"F3","disposition":"CURED","evidence":"The mandatory exact ## Clause map heading exists at line 177; mutating that heading in a temporary HEAD copy makes the shape check fail."}
    ],
    "new_defects": [],
    "same_signature": "NO: arbitrary sibling authority, unexecuted production-site proof, and missing clause-map signatures do not survive or recur."
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Delta re-audit finds every refuter blocker cured with biting counterfactuals, no fix-introduced defect, and CUSTODY-HARDEN-01 LANDABLE.",
  "workspace": {"base_requested":"a2e88e02fb45093aa9e183114cce5b7fc6a4ef56","base_mode":"exact","head_start":"a2e88e02fb45093aa9e183114cce5b7fc6a4ef56","head_end":"a2e88e02fb45093aa9e183114cce5b7fc6a4ef56","upstream_end":"a2e88e02fb45093aa9e183114cce5b7fc6a4ef56","branch":"feat/2026-09-04-fan-CUSTODY-HARDEN-01"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/04-delta-reaudit-round-1.md"],
  "unowned_dirty": [],
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git rev-parse HEAD && git branch --show-current && git diff-tree --no-commit-id --name-only -r HEAD && git diff --check HEAD^ HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["a2e88e02fb45093aa9e183114cce5b7fc6a4ef56","feat/2026-09-04-fan-CUSTODY-HARDEN-01","docs/contracts/adapter_contracts.md","joulewise/whole_window.py","tests/test_run_campaign.py"]},"expected":{"exit_code":0,"tail_regex":"a2e88e02[\\s\\S]*docs/contracts/adapter_contracts.md[\\s\\S]*joulewise/whole_window.py[\\s\\S]*tests/test_run_campaign.py"}},
    {"id":"V2","kind":"test","cmd":"python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_untracked_sibling_manifest_cannot_authenticate_forged_corpus tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_derivation_cli_mint_rejects_source_identity_postcondition_failure tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_claim_row_rejects_structurally_valid_unregistered_drift_corpus","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 0.041s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 3 tests in .*s[\\s\\S]*OK"}},
    {"id":"V3","kind":"suite","cmd":"python3 -m unittest tests.test_run_campaign","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 275 tests in 226.601s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 275 tests in .*s[\\s\\S]*OK"}},
    {"id":"V4","kind":"other","cmd":"cd /private/tmp/jw-custody-delta-a2e88e02-f1 && python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_untracked_sibling_manifest_cannot_authenticate_forged_corpus","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["AssertionError: True is not false","Ran 1 test in 0.008s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"True is not false[\\s\\S]*FAILED \\(failures=1\\)"}},
    {"id":"V5","kind":"other","cmd":"cd /private/tmp/jw-custody-delta-a2e88e02-mint && python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_derivation_cli_mint_rejects_source_identity_postcondition_failure","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["AssertionError: ValueError not raised","Ran 1 test in 0.035s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"ValueError not raised[\\s\\S]*FAILED \\(failures=1\\)"}},
    {"id":"V6","kind":"other","cmd":"cd /private/tmp/jw-custody-delta-a2e88e02-claim && python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_claim_row_rejects_structurally_valid_unregistered_drift_corpus","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["AssertionError: True is not false","Ran 1 test in 0.003s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"True is not false[\\s\\S]*FAILED \\(failures=1\\)"}},
    {"id":"V7","kind":"inspection","cmd":"rg -n '^## Clause map$' docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/01-sol-report.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["177:## Clause map"]},"expected":{"exit_code":0,"tail_regex":"177:## Clause map"}},
    {"id":"V8","kind":"other","cmd":"cd /private/tmp/jw-custody-delta-a2e88e02-f3 && rg -n '^## Clause map$' docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/01-sol-report.md","cwd":".","observed":{"result":"pass","exit_code":1,"tail":[]},"expected":{"exit_code":1,"tail_regex":"^$"}}
  ],
  "flags": [
    {"id":"F1","kind":"residual_risk","level":"nonblocking","text":"Per preflight, verification was limited to the only test module touched by the fix commit; repository-wide discovery was not run.","needs":""}
  ]
}
```

## Findings

None.

F1 — CURED. At HEAD, `test_untracked_sibling_manifest_cannot_authenticate_forged_corpus` passes. In an archived HEAD copy, restoring the pre-fix sibling `*.json` scan makes the same test fail with `True is not false`, proving the exact-path cure bites.

F2 — CURED. The mint and claim-row regressions both pass at HEAD. Removing only the mint-time source-byte postcondition makes the first fail with `ValueError not raised`; independently removing only claim-row `require_corpus_identity=True` makes the second fail with `True is not false`. Both formerly unexecuted production sites are now pinned.

F3 — CURED. The dated implementation report contains exact heading `## Clause map` at line 177 and all eight rows. Changing that heading to `## Clause maps` in an archived HEAD copy makes the exact shape check exit 1.

No new defect was introduced by the fix commit. Its production delta replaces directory-wide JSON discovery with one governed filename and retains caller-custodied exact-byte authentication unchanged. The refactored fixture and three new regressions pass in the complete touched module.

Same-signature statement: **NO**. None of the three original defect classes survives in a new form. The fix report's five-path session signature spans worker output plus runner custody: `01-sol-report.md` and `03-sol-fix-round-1-report.md` were custodied in immediately preceding commit `50f64f05`; the requested `git show HEAD` audit signature is exactly the three declared implementation paths shown in V1.

## Residual risk

Per the preflight rule, only `tests.test_run_campaign` ran. No repository-wide discovery suite or unrelated test module ran.
