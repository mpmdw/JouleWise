```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_RULING: baseline and concurrency audit completed; artifact-identity semantics and CI workflow scope block implementation.",
  "workspace": {
    "base_requested": "e991ef89ef2d713e228792319c063adb4c60ca42",
    "base_mode": "exact",
    "head_start": "e991ef89ef2d713e228792319c063adb4c60ca42",
    "head_end": "e991ef89ef2d713e228792319c063adb4c60ca42",
    "upstream_end": "213847b377d9bd022208c912274d4ec3b1e30193",
    "branch": "perf/2026-09-15-calexits-pool"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B -m unittest tests.test_calibration_exits > /private/tmp/calexits-before.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 48 tests in 505.380s",
          "OK",
          "real 505.99",
          "user 373.48",
          "sys 31.27"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)Ran 48 tests in .*s\\s+OK\\s+real"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B - <<'PY'\nimport hashlib\nfrom tests.test_calibration_exits import PublicGovernedExitWitnessTests, WITNESS_CASES, RefusalCode\ncase = next(c for c in WITNESS_CASES if c.code is RefusalCode.LEDGER_PENDING)\nobserved = []\nfor _ in range(2):\n    witness = PublicGovernedExitWitnessTests(methodName='runTest')\n    try:\n        witness.setUp()\n        witness._execute_case(case)\n        raw = witness.ledger.read_bytes()\n        observed.append(raw)\n        print('LEDGER_SHA256', hashlib.sha256(raw).hexdigest())\n    finally:\n        witness.doCleanups()\nassert observed[0] != observed[1]\nprint('UNCHANGED_SERIAL_REPEAT_LEDGER_BYTES_DIFFER=1')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "LEDGER_SHA256 8e4926a67c9288fc3ce26ff2e6b1b59d4537e9a55f9d04e336d09f8de2ad0f81",
          "LEDGER_SHA256 5aaf16082c081317c03eafb840764aa0a40c27530a67aeb2e69bc3f55154466b",
          "UNCHANGED_SERIAL_REPEAT_LEDGER_BYTES_DIFFER=1",
          "real 1.54",
          "user 1.03",
          "sys 0.47"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "UNCHANGED_SERIAL_REPEAT_LEDGER_BYTES_DIFFER=1"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Required scope expansion identified; no deviation performed. .github/workflows/ci.yml:160-161 pins evidence_range_seconds to [648.0,2036.0] and seconds to 2036.0. Updating the authorized timing declaration alone would fail CI.",
      "needs": "Expand WRITE_SCOPE to include .github/workflows/ci.yml, or assign the coordinated workflow change to the lead."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The literal every-artifact byte-identity condition fails for unchanged serial repetitions: receipts bind random absolute sandbox custody paths. PublicExecutionEvidence also contains real PID/PGID and execution-order tokens; preservation evidence contains inode identity. No normalization or evidence changes were made.",
      "needs": "Specify the exact artifact inventory and comparison setup. Recommend byte comparison of every governed capture artifact and rederivation output, controlled identical per-case paths for any included ledgers/plans, and relational checks for process/inode evidence. Alternatively retain literal all-file identity and authorize a deterministic comparison harness after defining its boundaries."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The expensive corrected-writer paths themselves perform machine-wide census and must remain serial under the instruction. WitnessSandbox.close also asserts globally that no owned fake sampler survives, which is incompatible with overlapping active sampler cases. A conservative partition has 55 pool candidates and 17 serial cases; it cannot deliver the projected speedup of pooling the CPU-heavy writers.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "No implementation, after timing, or serial-versus-pooled corpus digest comparison was performed pending the ruling. Crash-matrix timing was not measured or changed.",
      "needs": "Resume after the artifact-comparison ruling and workflow scope disposition."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      ".github/workflows/ci.yml"
    ],
    "reason": "The workflow hard-pins the timing declaration that this task requires changing.",
    "blocked_work": "Install a measured calibration-exits timing declaration without breaking its exclusive CI job.",
    "minimal_change": "Update the calibration-exits timing assertions and sequential-execution comment while preserving the declaration consistency check, fallback-rejection guard, and 30-minute ceiling."
  }
}
```

## Change

No changes or hunks; worktree remains clean. The supplied baseline digest verified.

The conservative serial partition would retain:

- `LIVE_WRITER_CONTENTION`: real lease holder.
- `FINALIZATION_BINDING_CONFLICT`, `PRE_SLOT_NOT_READY`, `WRITER_BRACKET_ARGUMENTS`, `WRITER_BRACKET_REDERIVE_CONFLICT`, `FROZEN_PROTOCOL_INVALID`, `REDERIVE_OUTPUT_REQUIRED`, `REDERIVE_FAILED`, `OUTPUT_REQUIRES_REDERIVE`, `QUIET_MAC_AUTH_REQUIRED`, `POWER_POLICY_REQUIRED`, `DERIVATION_ONLY_EPOCH_UNCHANGED`, `DERIVATION_ONLY_SESSION_KIND_REQUIRED`, `SAMPLER_NEVER_READY`, `ROLLOVER_GATE_TIMEOUT`: capture or corrected-capture paths reach the census.
- `DISPLAY_ARM_FAILED`, `DERIVATION_SESSION_REQUIRES_DERIVATION_ONLY`: conservatively retain with the writer family; their refusal paths stop before sampler capture.

The separate decoy, lease, and maintenance-race tests would remain serial and unchanged.

## Verification notes

Before: **505.99 seconds wall**, 48 tests passed. After: not run. The 1.54-second identity probe briefly overlapped the baseline; this is an agent-loaded bench measurement.

The probe demonstrates existing serial variability, not pooled equivalence. Relevant sites: `tests/test_calibration_exits.py:975` creates random roots; `:4178` binds custody paths; `:1084` checks global sampler survivors. Production census records sibling commands at `scripts/validate_powermetrics_fiducial.py:1097–1184`.

The unchanged lane has a **300-second fallback threshold** and **1,800-second job ceiling**. This bench baseline lies between them; it does not establish hosted or optimized timeout headroom.

Next exact step: issue the artifact-comparison ruling and workflow scope disposition, then resume implementation and before/after digest verification.