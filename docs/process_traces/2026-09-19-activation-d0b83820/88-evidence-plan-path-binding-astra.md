```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented published-plan binding and regressions; focused checks pass, with environment and baseline failures in broader verification.",
  "workspace": {
    "base_requested": "a9e48ae900a608b3254a732fb8e7463d66bdef1e",
    "base_mode": "exact",
    "head_start": "a9e48ae900a608b3254a732fb8e7463d66bdef1e",
    "head_end": "a9e48ae900a608b3254a732fb8e7463d66bdef1e",
    "upstream_end": "a9e48ae900a608b3254a732fb8e7463d66bdef1e",
    "branch": "fix/2026-09-19-evidence-plan-path-binding"
  },
  "pathspec": [
    "scripts/gen_evidence_night.py",
    "joulewise/night_agent_install.py",
    "tests/test_gen_evidence_night.py",
    "tests/test_night_agent_install.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_gen_evidence_night tests.test_night_agent_install.EvidencePlanPublicationTests tests.test_night_agent_install.EvidenceProbeReceiptTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 14 tests in 10.184s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_evidence_night tests.test_night_agent_install tests.test_night_gate tests.test_run_night tests.test_quiet_predicate_campaign",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 392 tests in 1063.251s",
          "",
          "FAILED (failures=2, skipped=9)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "QUICK SUMMARY tier=quick modules=153 excluded=89 failures=1 seconds=102.341 result=FAIL"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "result=PASS$"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/evidence-plan-path-dry-replay.py --updated-expectations",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS fixture publication preserves bytes and published probe bindings pass",
          "PASS synthetic receipt validator: schema, verify-only, no collect/load, cleanup, <6 h freshness",
          "PASS actual step5 assertions on synthetic plists; wrong schedule/argv/root/RunAtLoad refuse",
          "DRY CHECK COMPLETE: fixture checks passed; staging/publication binding repaired"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DRY CHECK COMPLETE: fixture checks passed; staging/publication binding repaired"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/evidence-plan-path-baseline-check.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: external watchdog (8 s): bind supervisor blocked in journal_block",
          "Ran 1 test in 8.007s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Sandbox process-list restrictions affect tests.test_night_agent_install.LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted (pgrep: Cannot get process list), plus tests.test_axi_controller_events.AxiControllerEventTests.test_campaign_prebundle_process_failure_retains_identity_receipt_and_row and test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure (campaign start identity unavailable through /bin/ps). The required orphan census also cannot observe ps.",
      "needs": "Lead reruns these tests and the orphan census where process-list access is available."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go times out after 8 seconds. It reproduces both independently on the changed tree and against untouched HEAD extracted into a disposable /tmp checkout.",
      "needs": "Lead adjudicates the pre-existing journal-supervision timeout separately."
    }
  ]
}
```

## Change

The wrapper now binds `<custody_root>/night_plan.json`. Probe bindings derive the same path and refuse staged inputs with `evidence plan not at its published path`.

Regressions cover atomic publication, staged-probe refusal, and identical generated artifacts before and after publication. Existing wrong-class, v4, frozen-window, overwrite, and tampering refusals pass.

**Same-signature audit:** no other wrapper literal binds a render-time path.

| Export | Source |
|---|---|
| `NIGHT_PAYLOAD_KIND` | Constant |
| `PYTHONDONTWRITEBYTECODE` | Constant |
| `EVIDENCE_PLAN_PATH` | Plan’s `custody_root` |
| `EVIDENCE_MANIFEST_PATH` | Plan’s `chain_path`; `--out` must match |
| `EVIDENCE_MANIFEST_SHA256` | Sealed manifest bytes |
| `EVIDENCE_CHAIN_SOURCE_SHA256` | Manifest’s tracked chain digest |
| `PY` | Plan’s `measurement_root` |
| `PYTHONPATH` | Plan’s `measurement_root` |

Non-exported guards and execution paths also derive from plan content or constants.

`quiet_predicate_campaign` reads the published plan during verification and refusal handling. The chain requires that export; installer rendering supplies the same published path as the night driver’s `--plan`.

## Verification notes

Seat 87’s original checker explicitly expects the defect and therefore fails its obsolete refusal assertion after this repair. The replay harness updates those expectations **in memory**, uses branch code in `/tmp` fixtures, and preserves the original source. Both `CONFIRMED BLOCKER` output lines are gone.

Broader failures are identified in F1/F2; no unrelated repairs were made. Verification used the requested modules and quick tier. Full discovery was not run because A211 identifies canonical-checkout dependencies incompatible with this task’s isolation restriction.

## Residual risk

Process-census clearance remains unproven in this sandbox. Next: lead reviews the four-file diff, reruns the census-dependent checks, adjudicates the baseline timeout, and commits by pathspec.