```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Execution checks pass; one should-fix coverage gap: the first head-pin mutation survives, and rank reversion fails only two tests.",
  "workspace": {
    "base_requested": "6d2d62d8",
    "base_mode": "exact",
    "head_start": "8afd6adecc1f13cc8afd51605c8eb4a491fbf47e",
    "head_end": "8afd6adecc1f13cc8afd51605c8eb4a491fbf47e",
    "upstream_end": "3b53478a330f0d7ab9d5e2657b641b6723d07072",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [".venv"],
  "verdict": {
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "file": "tests/test_gen_state.py",
        "line": 1301,
        "summary": "The first updated agent-head pin is not exercised by the current kernel.",
        "evidence": "Reverting only line 1301 to WO-LAUNCH-BINDING leaves all 44 tests passing. The agent lane has active rows, so test_run_state_gate_suppresses_lane_heads_but_active_work_continues takes the CONTINUE branch at line 1325 and bypasses the expected head assertion at lines 1338-1344. Reverting INSTALL-WINDOWS-MULTI-01 to rank 171 fails only test_clearing_gate_restores_exact_dependency_rank_heads and test_live_empty_gate_state_and_synthetic_gate_both_render_exactly, not the claimed three head-pin tests.",
        "proposed_closure_shape": "Retain active-work continuation coverage and add a no-active-agent subcase that asserts the gated agent head against this oracle. Repeat both mutations: the first pin reversion should fail this test, and rank reversion should fail all three head-pin tests."
      }
    ],
    "kernel": {
      "base_row_count": 174,
      "head_row_count": 174,
      "task_ids_unchanged": true,
      "selectable_task_ids": [
        "ED-DATES-01",
        "INSTALL-WINDOWS-MULTI-01",
        "V5-G2A-PREFILL-PROBE-01"
      ],
      "successor_result": "Deleting INSTALL-WINDOWS-MULTI-01 and satisfying ARM-RETRY-CLASS-01's dependency with synthetic scratch-only evidence makes the successor dependency-ready, but WO-LAUNCH-BINDING at rank 1 wins over its unchanged rank 172. Explicitly moving the successor to rank 0 makes it the head. The bookkeeping rank move is necessary; dependency satisfaction does not perform it."
    },
    "reference_scan": {
      "hits": 180,
      "classification_file": "/tmp/pr338-reference-classification.tsv",
      "classification": "163 historical; 7 valid live non-head references; 2 historical or unrelated test-rank comments; 6 unrelated strategy-ranking references; 1 historical unrelated kernel-rank note; 1 task dependency reference without a head claim.",
      "conclusion": "No stale live WO-LAUNCH-BINDING head pointer found. Current occurrences in EXPECTED_IDS and the kernel identify a still-live task; the updated comments correctly describe rank 0 ahead of rank 1. Historical snapshots remain historical. No matching hits in scripts/ or joulewise/."
    },
    "record_55": {
      "first_heading": "# 55 — Ed's directive issue #337, verbatim (author `mpmdw`, filed 2026-09-14 16:43:56 PDT; https://github.com/mpmdw/JouleWise/issues/337)",
      "separator_lines": [5],
      "cr_bytes": 0,
      "trailing_whitespace_lines": [],
      "final_lf": true,
      "issue_body_byte_identity": "Not independently established offline."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "pr338_scratch=$(mktemp -d /tmp/pr338-execution.XXXXXX)\nset -o pipefail\ngit archive HEAD | tar -x -C \"$pr338_scratch\"\nPYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python3 \"$pr338_scratch/scripts/gen_state.py\"\ndiff -u RUN_STATE.md \"$pr338_scratch/RUN_STATE.md\"\ndiff -u TASK_QUEUE.md \"$pr338_scratch/TASK_QUEUE.md\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "archive_rc=0 scratch=/tmp/pr338-execution.8xO0yo",
          "regenerate_rc=0",
          "RUN_STATE_diff_rc=0",
          "TASK_QUEUE_diff_rc=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "TASK_QUEUE_diff_rc=0"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python3 -m unittest tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "............................................",
          "----------------------------------------------------------------------",
          "Ran 44 tests in 5.501s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 44 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python3 /tmp/pr338-probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DEP_STATES: ('pending', 'satisfied')",
          "HEAD count: 174",
          "HEAD selectable_task_ids: ['ED-DATES-01', 'INSTALL-WINDOWS-MULTI-01', 'V5-G2A-PREFILL-PROBE-01']",
          "A unchanged rank: 172 selectable_task_ids: ['ED-DATES-01', 'V5-G2A-PREFILL-PROBE-01', 'WO-LAUNCH-BINDING']",
          "A rank=0 selectable_task_ids: ['ARM-RETRY-CLASS-01', 'ED-DATES-01', 'V5-G2A-PREFILL-PROBE-01']",
          "B rejected: tasks[INSTALL-WINDOWS-MULTI-01]: duplicate lane rank 0 (also ARM-RETRY-CLASS-01)",
          "C rejected: tasks[ARM-RETRY-CLASS-01]: pending hard start dependency requires status=blocked",
          "D test_rc: 0",
          "Ran 44 tests in 5.049s",
          "E test_rc: 1",
          "FAIL: test_clearing_gate_restores_exact_dependency_rank_heads (tests.test_gen_state.TestWorkSelectionFidelity.test_clearing_gate_restores_exact_dependency_rank_heads)",
          "FAIL: test_live_empty_gate_state_and_synthetic_gate_both_render_exactly (tests.test_gen_state.TestWorkSelectionFidelity.test_live_empty_gate_state_and_synthetic_gate_both_render_exactly)",
          "Ran 44 tests in 5.105s",
          "FAILED (failures=2)",
          "Probes complete; D survived; E caught by two tests; scratch mutations restored."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Probes complete; D survived; E caught by two tests; scratch mutations restored\\."
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -n 'WO-LAUNCH-BINDING|rank 1' docs/ tests/ scripts/ joulewise/ > /tmp/pr338-head-references.txt\nwc -l /tmp/pr338-head-references.txt",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["     180 /tmp/pr338-head-references.txt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "180 /tmp/pr338-head-references.txt"
      }
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check 6d2d62d8..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No network was used. Record 55's local formatting was verified, but its body could not be compared with independently fetched issue bytes.",
      "needs": "Lead may compare against the original issue-body capture."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main changed externally during review from 6d2d62d8d1820fb9d71bb7550705aab5eeac1a05 to 3b53478a330f0d7ab9d5e2657b641b6723d07072. HEAD remained unchanged; this review covers exactly the requested 6d2d62d8..HEAD diff.",
      "needs": "Lead owns integration verification against the current upstream."
    }
  ]
}
```