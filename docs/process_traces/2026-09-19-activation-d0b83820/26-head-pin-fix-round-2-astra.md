```json
{
  "schema":"claude-codex-report/v1",
  "genre":"implementation",
  "status":"findings",
  "completion":"complete",
  "summary":"Repaired five modules; 78 module tests completed OK with one existing skip, and all 10 negative-oracle tests rejected corrupted fixture bytes.",
  "workspace":{"base_requested":"d3c8b3559a3c635e43de46e98918e0e468201919","base_mode":"exact","head_start":"d3c8b3559a3c635e43de46e98918e0e468201919","head_end":"d3c8b3559a3c635e43de46e98918e0e468201919","upstream_end":"d3c8b3559a3c635e43de46e98918e0e468201919","branch":"fix/2026-09-19-head-pin-test-drift"},
  "pathspec":["tests/test_arm_readiness_registry.py","tests/test_d117_decode_contrast_plan.py","tests/test_d117_floor_qwen25_1p5b_plan.py","tests/test_d117_floor_qwen25_7b_plan.py","tests/test_d117_v3_family.py"],
  "unowned_dirty":[],
  "verdict":{"implementation":"implemented","acceptance":"ready"},
  "verification":[
    {"id":"V1","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_arm_readiness_registry","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 6 tests in 47.233s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V2","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_decode_contrast_plan","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 25 tests in 75.384s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)$"}},
    {"id":"V3","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_floor_qwen25_1p5b_plan","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 22 tests in 31.547s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V4","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_floor_qwen25_7b_plan","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 20 tests in 36.456s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V5","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_v3_family","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 5 tests in 38.416s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V6","kind":"other","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/head_pin_round2_negative_oracle.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Negative oracle: 10/10 tests failed on head-pin refusal","Evidence: /tmp/head-pin-round2-negative-tsamudjl"]},"expected":{"exit_code":0,"tail_regex":"Negative oracle: 10/10 tests failed on head-pin refusal"}},
    {"id":"V7","kind":"inspection","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/head_pin_round2_inspect.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Assertions preserved: 852; modified paths: 5; untracked paths: 0","Final source matches tested snapshot after formatting normalization"]},"expected":{"exit_code":0,"tail_regex":"Assertions preserved: 852; modified paths: 5; untracked paths: 0"}},
    {"id":"V8","kind":"inspection","cmd":"git diff --check\ngit diff --stat\ngit status --short --branch","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" 5 files changed, 259 insertions(+), 68 deletions(-)"," M tests/test_arm_readiness_registry.py"," M tests/test_d117_decode_contrast_plan.py"," M tests/test_d117_floor_qwen25_1p5b_plan.py"," M tests/test_d117_floor_qwen25_7b_plan.py"," M tests/test_d117_v3_family.py"]},"expected":{"exit_code":0,"tail_regex":"5 files changed"}},
    {"id":"V9","kind":"other","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python scripts/fixture_orphan_census.py --fail-on-orphans","cwd":".","observed":{"result":"fail","exit_code":2,"tail":["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]},"expected":{"exit_code":0,"tail_regex":"^(?!.*error).*"}},
    {"id":"V10","kind":"suite","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/head_pin_round2_full_suite.py","cwd":".","observed":{"result":"fail","exit_code":130,"tail":["KeyboardInterrupt"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V11","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_generated_gamma_roots_pass_and_legacy_keys_are_refused","cwd":"/tmp/head-pin-round2-suite-82ll4oi1/repository","observed":{"result":"fail","exit_code":1,"tail":["AssertionError: 3 != 0 : sysmon request failed with error: sysmond service not found","pgrep: Cannot get process list","Ran 2 tests in 1.911s","FAILED (failures=2)"]},"expected":{"exit_code":0,"tail_regex":"OK"}}
  ],
  "flags":[
    {"id":"F1","kind":"environment","level":"nonblocking","text":"Session-end orphan census exited 2 because the sandbox denies ps; no independent process-cleanup census was possible.","needs":"Lead rerun scripts/fixture_orphan_census.py --fail-on-orphans in an environment allowing process observation."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"Canonical discovery was interrupted after the real-pgrep census test failed in two subcases. Focused replay confirmed inaccessible sysmond/process listing. Full suite is not certified. Shutdown also reported no accessible Metal device. All requested acceptance checks completed.","needs":"Lead run canonical discovery in a suitable bench environment; logs are /tmp/head-pin-round2-full-suite.log and /tmp/head-pin-round2-canonical-failure-replay.log."}
  ]
}
```

## Change

Generators now run from disposable shared clones containing the imported historical head bytes and working-tree generator files. Emitted successors resolve their inputs through the same fixtures. All 852 existing assertions remain; nothing was committed.

| Module | Before → now | False-failure surface on next head-pin advance |
|---|---|---|
| Arm readiness registry | Frozen/draft parity and receipt checks → same checks with both repositories fixtured | None |
| Decode contrast | Exact v2/v3 transactions, downgrade refusal, freeze-neutral wording → same proofs with fixtured predecessor and successor inputs | None |
| Qwen 1.5B floor | Successor identity, lineage and byte preservation → same proofs with historical inputs | None |
| Qwen 7B floor | Inventory, invalid modes, symlink refusals and lineage → same proofs, plus explicit invalid-mode refusal messages | None |
| V3 family | Working-tree v2→v3 emission and missing-output refusal → same proofs from disposable repositories | None |

## Verification notes

The contrast module retains its existing structural skip for the authenticated freeze transition.

The [negative-oracle results](/tmp/head-pin-round2-negative-tsamudjl/results.json) record all 10 expected failures, including all four 7B symlink subcases.

The broader canonical replay encountered the process-observation limitation described above and was interrupted; it is **not** a full-suite pass. Next step: lead review of the scoped diff, then canonical replay and orphan census in the bench environment.