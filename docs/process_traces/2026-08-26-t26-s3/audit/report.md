```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "A94 is met; A93 is not met because the constant still controls authentication and no durable ruling binds the policy.",
  "workspace": {"base_requested":"2fd7c920314333535ea2631bec887a19b964f834","base_mode":"exact","head_start":"2fd7c920314333535ea2631bec887a19b964f834","head_end":"2fd7c920314333535ea2631bec887a19b964f834","upstream_end":"2bc5daabc347035208eaf0ac8204225ba69b89d0","branch":"fix/packauth-soundness-rows"},
  "pathspec": ["docs/process_traces/2026-08-26-t26-s3/audit/report.md","docs/process_traces/2026-08-26-t26-s3/audit/replay-prechange-spotcheck.sh","docs/process_traces/2026-08-26-t26-s3/audit/replay-finding-controls.sh","docs/process_traces/2026-08-26-t26-s3/audit/replay-baseline-performance.sh"],
  "unowned_dirty": ["docs/contracts/receipt_histsem_verifier.md","joulewise/arm_readiness.py","joulewise/arm_readiness_evidence.py","tests/test_arm_readiness_evidence_packauth.py","tests/test_receipt_histsem.py","docs/process_traces/2026-08-26-t26-s3/** except audit/**"],
  "verdict": {
    "acceptance": {
      "A93": {"status":"NOT MET","rests_on":"F1 constant dependency and F2 missing durable ruling."},
      "A94": {"status":"MET","rests_on":"Authenticated pre-freeze regeneration plus projected anchor/replay; V5/V6 pin the shape."}
    },
    "checks": {
      "C1":"PASS: no configs/campaigns or scripts change.",
      "C2":"PASS: exact six-key predicate unchanged; 99 committed receipts validate.",
      "C3":"PASS: no re-mint required.",
      "C4":"PASS: projected _v4 uses anchor+replay; unchanged CLI/regressions pass. Full verifier rose 37.54s to 60.77s but is bounded and the runsheet has no deadline.",
      "C5":"FAIL: F1.",
      "C6":"PASS normally: AST-only discovery, python -I -B, bounded subprocesses, clean temp trees, no pack __pycache__. F3 covers allocation failure.",
      "Q1":"CONFIRMED: no production caller requests preserve; both author and histsem apply the regenerated-only guard.",
      "Q2":"CONFIRMED: four claimed pre-change failures reproduced in V6.",
      "Q3":"A94's derivation branch is discharged; no semantic consumer missing from the inventory was found.",
      "Q4":"NOT CONFIRMED: only recommendation.md calls the A93 choice a ruling.",
      "Q5":"F3 and F4; no missing timeout or normal-path leak found."
    },
    "findings": [
      {"id":"F1","severity":"blocker","title":"Authentication still depends on CURRENT_FROZEN_RECEIPT_SHA256","file_line":"joulewise/arm_readiness_evidence.py:1172","failure_scenario":"A flagless generator is refused solely because the constant exists; computed, malformed, duplicate, or non-SHA constants also refuse before authentication. This contradicts C5 and A93 despite authentication_dependency=false.","suggested_cure":"Separate preserve-capability classification from constant extraction. Make extraction total/diagnostic-only, never use constant presence or value for PASS/REFUSE, and regression-test constant variants against one fixed derivation."},
      {"id":"F2","severity":"blocker","title":"A93 has no durable ruling","file_line":"docs/process_traces/2026-08-26-t26-s3/recommendation.md:3","failure_scenario":"The only artifact calling the policy a ruling is an untracked recommendation trace; neither the decision log nor the modified normative contract records constant non-authority. A93 evidence (b) is absent.","suggested_cure":"Record the adopted choice in binding decision authority or an explicitly normative adopted contract, with alternatives and regression pointer."},
      {"id":"F3","severity":"should_fix","title":"Temporary-workspace failure escapes governed histsem refusal","file_line":"joulewise/arm_readiness.py:3491","failure_scenario":"TemporaryDirectory allocation failure raises raw OSError. Freeze/arm gates catch HistoricalSemanticsError only, so operator entry points can traceback.","suggested_cure":"Translate temp creation/materialization/cleanup errors to an existing histsem reason and test freeze and arm boundaries."},
      {"id":"F4","severity":"should_fix","title":"Unrelated constant is mislabeled names_predecessor","file_line":"joulewise/arm_readiness_evidence.py:1904","failure_scenario":"Every non-absent digest unequal to current is labeled names_predecessor even when constant_matches_predecessor is false.","suggested_cure":"Use names_predecessor only on equality; record a distinct mismatch/other relation and test it."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_arm_readiness_evidence_packauth","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 25 tests in 48.767s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_receipt_histsem","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 35 tests in 202.443s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)"}},
    {"id":"V3","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_arm_readiness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 37 tests in 0.747s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V4","kind":"smoke","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B scripts/verify_receipt_histsem.py --repository-root .","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["  \"receipt_count\": 99,","  \"status\": \"PASS\"","}","real 60.77"]},"expected":{"exit_code":0,"tail_regex":"\"status\": \"PASS\""}},
    {"id":"V5","kind":"test","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_preserve_echo_accepts_science_row_tamper_but_cannot_set_generator_pass tests.test_receipt_histsem.PackAuthenticationRegenerationTests.test_projected_pack_pack_auth_receipt_survives_histsem_regeneration_gate tests.test_receipt_histsem.PackAuthenticationRegenerationTests.test_v4_prefreeze_authors_then_postfreeze_bare_refuses_without_invalidating_recorded_authentication","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 22.931s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V6","kind":"test","cmd":"sh docs/process_traces/2026-08-26-t26-s3/audit/replay-prechange-spotcheck.sh","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["Ran 4 tests in 13.429s","","FAILED (failures=2, errors=2)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=2, errors=2\\)"}},
    {"id":"V7","kind":"test","cmd":"sh docs/process_traces/2026-08-26-t26-s3/audit/replay-finding-controls.sh","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["C5 evidence_author_pack_authentication_underivable flagless generator has a preserve branch or frozen-receipt constant","TMP OSError None simulated tmp exhaustion"]},"expected":{"exit_code":0,"tail_regex":"TMP OSError None simulated tmp exhaustion"}},
    {"id":"V8","kind":"other","cmd":"sh docs/process_traces/2026-08-26-t26-s3/audit/replay-baseline-performance.sh","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["real 37.54","user 16.08","sys 17.66"]},"expected":{"exit_code":0,"tail_regex":"^real "}}
  ],
  "flags": [
    {"id":"R1","kind":"verification_gap","level":"nonblocking","text":"The operator-owned real _v4 mint was not executed; the projected author/freeze/histsem path was traced and regression-run.","needs":"Lead retains final live transaction verification."},
    {"id":"R2","kind":"residual_risk","level":"nonblocking","text":"Shallow history is covered, but a partial/promisor clone missing selected non-pack blobs was not constructed.","needs":"Test if supported; otherwise document unsupported and fail closed."}
  ]
}
```

A93 NOT MET — rests on F1 (the constant remains an authentication dependency) and F2 (no durable ruling satisfies evidence item (b)).

A94 MET — rests on the authenticated pre-freeze regeneration replay and the projected anchor+replay regressions in V5, plus the executed mode characterization for evidence item (a).

## Findings

### F1 — blocker — The authentication verdict still depends on `CURRENT_FROZEN_RECEIPT_SHA256`

At [arm_readiness_evidence.py:1172](/Users/edr/code/JouleWise-wt-s3-packauth/joulewise/arm_readiness_evidence.py:1172), a flagless generator is rejected when the constant merely exists. Earlier, [line 1079](/Users/edr/code/JouleWise-wt-s3-packauth/joulewise/arm_readiness_evidence.py:1079) makes duplicate, nonliteral, or malformed constant syntax an authoring refusal, and `_derive_pack_authentication` calls that parser before the authentication path. V7 reproduced the refusal. The emitted `authentication_dependency: false` therefore describes a policy the code does not obey.

The fix must make constant extraction total and observational only. Preserve capability may govern invocation selection, but constant presence, syntax, and value may not affect PASS/REFUSE. The regression should hold the derivation coordinate fixed while varying the constant through absent, valid-current, valid-predecessor, unrelated-valid, malformed, and computed forms; every case must have the same authentication verdict while the diagnostic changes.

### F2 — blocker — A93's selected policy has no durable ruling

The only artifact titled as the ruling is [recommendation.md:3](/Users/edr/code/JouleWise-wt-s3-packauth/docs/process_traces/2026-08-26-t26-s3/recommendation.md:3), inside the untracked implementation trace. No `docs/decision_log.md` entry names A93/A94, and the modified histsem contract explains explicit no-preserve replay without declaring the constant compatibility-only and non-authoritative. A93 evidence item (b) explicitly requires a ruling, so this is an acceptance blocker independently of F1.

Record the adopted choice in the repository's binding decision authority, or in a clearly normative contract section that the decision log adopts, with the rejected refresh option, the diagnostic-only rule, and the exact regression pointer.

### F3 — should_fix — Temporary-workspace failure escapes as raw `OSError`

The new `TemporaryDirectory` context opens outside the translation block at [arm_readiness.py:3491](/Users/edr/code/JouleWise-wt-s3-packauth/joulewise/arm_readiness.py:3491). V7 forced allocation failure and observed `OSError` with no reason code. The CLI happens to catch `OSError`, but the pre-freeze and pre-arm library gates catch only `HistoricalSemanticsError`; those operator paths can traceback instead of returning their governed REFUSE objects.

Translate temporary workspace creation/materialization/cleanup errors into the existing histsem vocabulary, and test the public freeze and arm boundaries rather than only the helper.

### F4 — should_fix — An unrelated constant is reported as `names_predecessor`

At [arm_readiness_evidence.py:1904](/Users/edr/code/JouleWise-wt-s3-packauth/joulewise/arm_readiness_evidence.py:1904), every non-absent digest that does not equal the current receipt is labeled `names_predecessor`; the separately recorded `constant_matches_predecessor` may simultaneously be false. This can publish a false diagnostic even after F1 is fixed. Use `names_predecessor` only for equality and add a distinct mismatch/other relation.

No nit findings.

## Residual risk

The audit did not execute the real operator-owned `_v4` mint. It read the §3.4/§3.7/§4 path, verified the unchanged script digests, ran the projected author→freeze→historical-replay regressions, and ran the real nine-pack verifier, but the lead still owns the live transaction gate.

The existing shallow-clone refusal is governed and regression-covered. A partial/promisor clone missing selected non-pack library blobs was not constructed, so lazy-fetch behavior for that unsupported clone shape remains unverified.
