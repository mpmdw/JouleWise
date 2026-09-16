```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_RULING: F2 targets an absent allowlisted file; F1 conflicts with issued source-byte pins; required calibration captures are unhydrated. No edits.",
  "workspace": {
    "base_requested": "e991ef89ef2d713e228792319c063adb4c60ca42",
    "base_mode": "exact",
    "head_start": "e991ef89ef2d713e228792319c063adb4c60ca42",
    "head_end": "e991ef89ef2d713e228792319c063adb4c60ca42",
    "upstream_end": "213847b377d9bd022208c912274d4ec3b1e30193",
    "branch": "perf/2026-09-15-fitter-multiset"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B -m unittest tests.test_powermetrics_fiducial",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 75 tests in 66.642s",
          "OK",
          "real 67.19",
          "user 63.05",
          "sys 3.67"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 75 tests in .*s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B -m unittest tests.test_p2038_production_path",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 8 tests in 253.609s",
          "OK",
          "real 254.48",
          "user 239.10",
          "sys 2.88"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests in .*s\\s+OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch && git diff --check && git rev-parse HEAD '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## perf/2026-09-15-fitter-multiset...origin/main [behind 1]",
          "e991ef89ef2d713e228792319c063adb4c60ca42",
          "213847b377d9bd022208c912274d4ec3b1e30193"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "e991ef89ef2d713e228792319c063adb4c60ca42"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Scope expansion required; no deviation performed. joulewise/derive_powermetrics_anchor_v3.py does not exist. derive_powermetrics_anchor_v3 and _lp2 live in joulewise/uncertainty_evidence.py:814 and :622. The parsed-plist cache belongs at joulewise/adapters/powermetrics.py:2056 (_powermetrics_documents), outside WRITE_SCOPE.",
      "needs": "Authorize joulewise/adapters/powermetrics.py for F2."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "F1 cannot preserve the existing source-byte hash gate: configs/calibration/calibration_acceptance_d079_v2_n17_r6.json pins powermetrics_fiducial.py, adapters/powermetrics.py and uncertainty_evidence.py. tests/test_powermetrics_fiducial.py:1588 requires current source hashes to equal those issued pins; scripts/validate_powermetrics_fiducial.py:393 refuses changed source as acceptance_artifact_stale. Numerical identity does not preserve source hashes.",
      "needs": "Rule whether to stage the optimization with an explicitly pending stale-pin gate, or provide a lead-owned atomic acceptance-reissue plan. Recommend the reissue plan for the requested all-green acceptance; preserve the existing hash gate."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "tests/fixtures/d117_v2_production/custody_store contains zero hydrated powermetrics.plist captures. The d078_r01 and d117 strict_seed_bundle event files contain zero pulse_command_on rows. These available bundle captures cannot substitute for the required retained pulse-calibration corpus.",
      "needs": "Hydrate the authenticated calibration corpus in this worktree and identify the complete replay fixture set before resuming."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Stopped before edits under NEEDS_RULING. No identity harness, after timings, whole_window_selection timing, or reduce timing was executed. Existing fiducial hash gates and production strict-rederivation tampering tests passed only on the unchanged baseline.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/adapters/powermetrics.py"
    ],
    "reason": "The actual parsed-plist implementation is outside the exhaustive allowlist.",
    "blocked_work": "F2 content-digest parsed-document caching.",
    "minimal_change": "Cache _powermetrics_documents results by SHA-256 of capture bytes, with cache isolation and tamper regressions in the already-authorized test file."
  }
}
```

## Change

No hunks or commits. The tree remains clean. The supplied baseline’s canonical digest matched.

## Verification notes

Before wall times: fiducial **67.19 s**; production path **254.48 s**. After times and float-identity proof are unavailable because implementation stopped at the authority conflicts.

Next exact step: the lead corrects F2’s write scope, rules on issued-pin handling, and hydrates the authenticated pulse captures; then resumes this task.