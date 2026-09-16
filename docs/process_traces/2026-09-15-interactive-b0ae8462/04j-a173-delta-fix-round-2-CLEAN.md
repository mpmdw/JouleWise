```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "CLEAN: all three mutations were caught; same-signature recurrence NO; both requested modules green.",
  "workspace": {
    "base_requested": "60f24fdafe591f5b0aaa76f8e7d52fc1f2509d46",
    "base_mode": "exact",
    "head_start": "60f24fdafe591f5b0aaa76f8e7d52fc1f2509d46",
    "head_end": "60f24fdafe591f5b0aaa76f8e7d52fc1f2509d46",
    "upstream_end": "60f24fdafe591f5b0aaa76f8e7d52fc1f2509d46",
    "branch": "feat/2026-09-15-arm-census-idle"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "mutation_results": [
      {
        "mutation": "Restore discovery-hit intersection at both own-root selection call sites",
        "red": "exit 1; helper_only falsely BLOCKED at tests/test_arm_census.py:222; workload and sibling cells also failed",
        "green": "exit 0 after restoration"
      },
      {
        "mutation": "Remove unreadable-hit branch from _own_root",
        "red": "exit 1; test_unreadable_own_root_retains_known_side_work, busy=True, failed at tests/test_arm_census.py:389",
        "green": "exit 0 after restoration"
      },
      {
        "mutation": "Return the innermost qualifying ancestor",
        "red": "exit 1; 5 failures across two existing tests",
        "catching_cells": [
          "test_outermost_exact_own_agent_root_is_selected: interactive Claude and T3 cells reject extra root 25 at tests/test_arm_census.py:269",
          "test_outermost_exact_own_agent_root_is_selected: outer headless --print=json cell falsely BLOCKED at tests/test_arm_census.py:266",
          "test_unreadable_outer_own_hit_scans_work_and_exempts_idle_helpers: idle cell falsely BLOCKED at tests/test_arm_census.py:411; busy cell loses workload at line 413"
        ],
        "green": "Entire tests.test_arm_census module: 20 tests, OK after restoration"
      }
    ],
    "same_signature": {
      "recurrence": "NO",
      "shape": "launchd(1) -> claude -p(4493) -> zsh(4498) -> census caller(4600); codex mcp-server(4514) under 4493; code-mode host(4519) under 4514; codex exec siblings 52077 and 52207 under separate parents outside 4493",
      "with_siblings": {
        "hits": [4514, 4519, 52077, 52207],
        "exit_code": 3,
        "verdict": "BLOCKED",
        "foreign_pids": [52077, 52207],
        "workloads": [],
        "own_root": 4493,
        "helpers_exempt": true
      },
      "without_siblings": {
        "hits": [4514, 4519],
        "exit_code": 0,
        "verdict": "CLEAR",
        "foreign_pids": [],
        "workloads": [],
        "own_root": 4493,
        "helpers_exempt": true
      },
      "additional_nested_shape": "Interactive Claude -> zsh -> headless Claude -> zsh -> caller: CLEAR, outermost interactive root 100 selected, helpers under both roots exempt"
    },
    "non_stub_exit_3": "Unreachable: joulewise/arm_census.py:56 requires REHEARSAL_STUB for publication_blocked; line 313 returns 3 only for that property. Executed DIAGNOSTIC_NO_PACK and TRANSACTION_PACK with and without siblings: all exit 0, diagnostic only. Existing busy-workload CLI matrix also passed.",
    "unchanged": ["joulewise/night_gate.py", "scripts/run_night.py"],
    "modules": {
      "tests.test_arm_census": "20 tests, OK",
      "tests.test_run_night": "104 tests, OK"
    },
    "integrity": "Baseline digest, HEAD, index and clean status matched; scratch source restored byte-for-byte; diff --check passed.",
    "next_step": "Lead final review and disposition of the exact reviewed head."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/.audit/tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B .audit/mutations.py revert",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta2-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["revert-red: exit=1", "FAILED (failures=3)", "revert-green: exit=0", "OK", "RESTORED_SOURCE_OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "RESTORED_SOURCE_OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/.audit/tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B .audit/mutations.py unreadable",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta2-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["unreadable-red: exit=1", "FAILED (failures=1)", "unreadable-green: exit=0", "OK", "RESTORED_SOURCE_OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "RESTORED_SOURCE_OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/.audit/tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B .audit/mutations.py innermost",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta2-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["innermost-red: exit=1", "FAILED (failures=5)", "innermost-green: exit=0", "Ran 20 tests in 0.038s", "OK", "RESTORED_SOURCE_OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "RESTORED_SOURCE_OK"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "TMPDIR=\"$PWD/.audit/tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B .audit/probes.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta2-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["SAME_SIGNATURE_RECURRENCE=NO; all 7 CLI verdicts matched"]
      },
      "expected": {"exit_code": 0, "tail_regex": "SAME_SIGNATURE_RECURRENCE=NO; all 7 CLI verdicts matched"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/.audit/tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night > .audit/night.log 2>&1",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta2-copy",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["joulewise.night_gate.PackNightRefusal: rehearsal_roots_not_disjoint: measurement_root", "Ran 104 tests in 20.799s", "FAILED (errors=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=\"${PWD%/night-repo}/tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night > ../night-disjoint.log 2>&1",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta2-copy/.audit/night-repo",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 104 tests in 20.114s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "python3 -B .audit/integrity.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta2-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["BASELINE_DIGEST_HEAD_INDEX_STATUS_OK", "NIGHT_GATE_AND_DRIVER_UNCHANGED; DIFF_CHECK_OK", "BOTH_SCRATCH_COPIES_MATCH_REVIEWED_SOURCE"]
      },
      "expected": {"exit_code": 0, "tail_regex": "BOTH_SCRATCH_COPIES_MATCH_REVIEWED_SOURCE"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Resolved audit-layout error: placing TMPDIR inside the copied repository violated an existing disjoint-root fixture assumption. Reran unchanged tests and production files in .audit/night-repo with sibling .audit/tmp, all inside the authorized scratch copy: 104 tests passed.",
      "needs": ""
    }
  ]
}
```

## Residual risk

Process-shape evidence uses mocked discovery and exact-record fixtures. No live hardware validation or real `launchctl` was performed.