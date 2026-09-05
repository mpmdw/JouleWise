```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Portable arm-readiness fixture repositories now copy the complete frozen detection-floor registry bundle and fail on partial source bundles.",
  "workspace": {"base_requested":"f607e98690fbe00a24988bcff0f13e78522724f9","base_mode":"exact","head_start":"f607e98690fbe00a24988bcff0f13e78522724f9","head_end":"f607e98690fbe00a24988bcff0f13e78522724f9","upstream_end":"f607e98690fbe00a24988bcff0f13e78522724f9","branch":"feat/2026-09-04-fan-FIXTURE-MODERNIZATION-01"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/FIXTURE-MODERNIZATION-01/05-sol-wave2-seam-fix.md","tests/test_arm_readiness_lifecycle.py"],
  "unowned_dirty": ["docs/process_traces/2026-09-04-fanout/FIXTURE-MODERNIZATION-01/04-delta-reaudit-round-1.md"],
  "verdict": {"implementation":"implemented","acceptance":"ready"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_lifecycle","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 67 tests in 123.995s","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 67 tests in .*s\\n\\nOK \\(skipped=1\\)"}},
    {"id":"V2","kind":"test","cmd":"fixture_seam_source=$PWD/tests/test_arm_readiness_lifecycle.py && fixture_seam_tmp=$(mktemp -d /tmp/joulewise-fixture-seam.XXXXXX) && git archive origin/int/2026-09-04-fan-wave-2 | tar -x -C \"$fixture_seam_tmp\" && cp \"$fixture_seam_source\" \"$fixture_seam_tmp/tests/test_arm_readiness_lifecycle.py\" && cd \"$fixture_seam_tmp\" && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_fixture_repo_copies_detection_floor_registry_bundle","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 0.456s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test in .*s\\n\\nOK"}},
    {"id":"V3","kind":"lint","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": []
}
```

## Change

`make_go_fixture` now installs `joulewise/detection_floor_registry.py` together with the frozen registry JSON and checksum whenever MODULARITY-01's source bundle is present. A partial source bundle raises instead of producing another misleading portable fixture. The regression independently pins all three required paths.

Red before the copy was wired:

```text
FileNotFoundError: .../repo/joulewise/detection_floor_registry.py
Ran 1 test in 0.502s
FAILED (errors=1)
```

Green after the copy was wired:

```text
Ran 1 test in 0.498s
OK
```

## Verification notes

The full touched module passed on this branch. The focused regression also passed in a temporary export of the Wave-2 integration ref, proving the seam against MODULARITY-01's real registry files without changing that ref or running unrelated test modules.
