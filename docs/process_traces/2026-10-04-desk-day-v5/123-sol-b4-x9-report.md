```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented G10 placement and measured-offset preflight; 108 scoped tests pass; legacy G10 fixture updates require scope expansion.",
  "workspace": {
    "base_requested": "bda1c180",
    "base_mode": "exact",
    "head_start": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "head_end": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "upstream_end": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "branch": "lane/2026-10-05-b4-x9"
  },
  "pathspec": [
    "scripts/ed_session/capture_t0_anchor_positive_control.py",
    "scripts/write_v5_qualification_plan.py",
    "joulewise/v5_qualification.py",
    "joulewise/t0_rehearsal.py",
    "tests/test_v5_block4_x9.py",
    "tests/test_capture_t0_anchor_positive_control.py",
    "tests/test_capture_t0_anchor_positive_control_g10.py",
    "tests/test_v5_qualification_plan.py"
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
      "cmd": "TMPDIR=/tmp/dd5-x9 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_block4_x9 tests.test_capture_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control_g10 > /tmp/dd5-x9/x9-final.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x9 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_qualification_plan tests.test_v5_s1_qualification tests.test_harvest_v5_qualification tests.test_v5_block4_composed tests.test_v5_block4_clock > /tmp/dd5-x9/required-final.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-x9 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_t0_anchor_positive_control tests.test_v5_block4_x4.G10CustodyTests > /tmp/dd5-x9/legacy-g10.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=6, errors=31)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x9 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests > /tmp/dd5-x9/canonical.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 130, "tail": ["KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK"}
    },
    {
      "id": "V5",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The actual legacy G10 tests are outside WRITE_SCOPE. Their runners lack collector handling and their fixtures require updated sizing and placement bindings. Both files were preserved.",
      "needs": "Resume with the two requested test paths authorized, or have the lead adapt them."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical 7991-test run was interrupted before completion after the legacy fixture failures were established separately.",
      "needs": "Run the complete canonical suite after fixture adaptation and integration."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/test_t0_anchor_positive_control.py",
      "tests/test_v5_block4_x4.py"
    ],
    "reason": "These contain the existing G10 tests; the two positive-control test filenames supplied in WRITE_SCOPE were absent at intake.",
    "blocked_work": "Updating all existing G10 tests and obtaining complete canonical verification.",
    "minimal_change": "Add fixed-collector runner handling and sizing fixture support; replace a1 placement with a2 expiry and s1 boundary bindings."
  }
}
```

## Change

G10 custody now falls after a2’s expiry check and before the s1 writer’s time or s1’s earliest captured T-0 boundary, on the same boot.

The fixed R0 collector runs before input copying or ON. Offset refusals retain custody and report `g10_attempt: false`. Replay verifies the raw preflight, computed agreement, command support, stamps, polls and OFF receipt.

Preparation copies inputs at `capture_t0_anchor_positive_control.py:204`; it cannot reach `_arm_reference`’s resync ON at `capture_t0_step.py:769`. The isolation kill-test covers this, so no `g10_prep_resynced` branch was needed.

Recipe 46 was preserved. The lead must update its placement, measured-offset prerequisites, preflight-first sequence, and non-spending wait/lead outcomes.

## Verification notes

The 15 focused tests and required 93-test suite pass. Two baseline fixture errors were fixed by updating their reference paths to `_v5`.

Legacy G10 tests remain blocked by scope. A representative legacy test also failed with the baseline helper. Canonical verification remains incomplete.

## Residual risk

Evidence is fixture-only; the author’s sizing replay seam is injected. No live G10 validation occurred. Changes remain uncommitted; nothing was pushed.