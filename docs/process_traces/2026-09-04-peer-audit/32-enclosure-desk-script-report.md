```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented and verified the authenticated desk-only partial-record enclosure; broad origin/main identity is blocked by concurrent out-of-scope baseline drift.",
  "workspace": {
    "base_requested": "6a928897",
    "base_mode": "exact",
    "head_start": "6a92889733c58246b099461525bd2a8ea67b2a70",
    "head_end": "6a92889733c58246b099461525bd2a8ea67b2a70",
    "upstream_end": "6a92889733c58246b099461525bd2a8ea67b2a70",
    "branch": "feat/2026-09-04-estimand-enclosure"
  },
  "pathspec": [
    "joulewise/reduce.py",
    "docs/contracts/run_bundle_layout.md",
    "tests/goldens/axi_summary_v062.json",
    "tests/goldens/d078_r01_reducer_052.json",
    "tests/test_reduce.py",
    "scripts/paper/partial_record_enclosure.py",
    "tests/test_partial_record_enclosure.py",
    "docs/paper/results-fill-registry.md",
    "docs/process_traces/2026-09-04-peer-audit/32-enclosure-desk-script-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_reduce",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["----------------------------------------------------------------------", "Ran 132 tests in 345.287s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 132 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_partial_record_enclosure",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["----------------------------------------------------------------------", "Ran 8 tests in 2.342s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 8 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_cli_run",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["----------------------------------------------------------------------", "Ran 130 tests in 37.545s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 130 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --quiet origin/main -- joulewise/reduce.py docs/contracts/run_bundle_layout.md tests/goldens/axi_summary_v062.json tests/goldens/d078_r01_reducer_052.json tests/test_reduce.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["(empty)"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --quiet origin/main -- joulewise tests/goldens",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "M joulewise/analysis_engine/inputs.py; D joulewise/analysis_manifest_v2.py; M joulewise/arm_readiness.py; D joulewise/campaign_generator_core.py",
          "M joulewise/campaign_provenance.py; D joulewise/coldgate_receipt.py; M joulewise/detection_floor.py; D joulewise/detection_floor_registry.py",
          "M joulewise/floor_extraction.py; M joulewise/identity_pins.py; D joulewise/phase_share.py; M joulewise/quiet_guard_process.py; M joulewise/whole_window.py; D joulewise/workload_sizing.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["(empty)"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "git fetch origin main could not write FETCH_HEAD because this worktree's Git metadata is outside the writable sandbox; the shared origin/main ref later advanced concurrently to 82636d67.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "The requested broad joulewise/tests-goldens identity check fails only on 14 pre-existing branch-vs-82636d67 paths outside WRITE_SCOPE; all five restored in-scope artifacts match current origin/main bytes.",
      "needs": "Lead rebase this feature branch onto 82636d67 or accept V4 as the scoped restoration proof, then rerun V5."
    },
    {
      "id": "F3",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Making V5 empty in this delegated session would require writes outside the exhaustive allowlist.",
      "needs": "Lead-owned rebase is recommended; otherwise resume with the requested paths added to WRITE_SCOPE."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/analysis_engine/inputs.py",
      "joulewise/analysis_manifest_v2.py",
      "joulewise/arm_readiness.py",
      "joulewise/campaign_generator_core.py",
      "joulewise/campaign_provenance.py",
      "joulewise/coldgate_receipt.py",
      "joulewise/detection_floor.py",
      "joulewise/detection_floor_registry.py",
      "joulewise/floor_extraction.py",
      "joulewise/identity_pins.py",
      "joulewise/phase_share.py",
      "joulewise/quiet_guard_process.py",
      "joulewise/whole_window.py",
      "joulewise/workload_sizing.py"
    ],
    "reason": "These branch-vs-main differences prevent the exact broad identity command from exiting 0 after origin/main advanced.",
    "blocked_work": "Only the requested broad identity proof; implementation and focused verification are complete.",
    "minimal_change": "Prefer a lead-owned rebase onto origin/main at 82636d67, then rerun the three suites and V5."
  }
}
```

## Change

Restored the rejected reducer field, roster entry, goldens, and reducer tests to current `origin/main` bytes. Added the pinned desk script, using `BundleReader.summed_curve`/`phase_windows` (`joulewise/bundle_read.py:352,576`) and reducer `_integrate` (`joulewise/reduce.py:157`), with fixed-window scope, digest-stable authenticated reads, SHA-256 census, domain refusals, and no bound composition. Added all requested oracles, the Q/2 mutation kill, tracked strict-bundle immutability proof, and exactly one DERIVE registry row.

## Verification notes

The three permitted modules ran one at a time in the required order. The first tracked-fixture attempt used the incomplete D-078 fixture and correctly strict-refused; the final test uses `tests/fixtures/d117_v2_production/strict_seed_bundle`. No discovery suite ran. No commit was made.

## Residual risk

`origin/main` advanced during the session. V5 cannot pass without a lead-owned rebase or expanded authority over the 14 listed paths.
