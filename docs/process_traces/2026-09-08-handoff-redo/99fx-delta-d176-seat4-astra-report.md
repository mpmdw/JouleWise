```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One new G7 custody escape reproduced; 303 focused tests passed; frozen seams preserved and worktree clean.",
  "workspace": {
    "base_requested": "e73e5439",
    "base_mode": "descendant",
    "head_start": "3032dd9371d262450ede4418f784c8ea4a9055c7",
    "head_end": "3032dd9371d262450ede4418f784c8ea4a9055c7",
    "upstream_end": "3032dd9371d262450ede4418f784c8ea4a9055c7",
    "branch": "feat/2026-09-08-d176-seat4-rehearsal"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "scripts/run_night.py",
        "line": 1316,
        "summary": "A symlinked control/night redirects G7 writes into completed rehearsal custody while the producer reports PASS."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_run_night tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_arm_readiness tests.test_rehearse_t0_unattended tests.test_docs_freshness > /tmp/d176-seat4-reaudit-suite.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 303 tests in 444.597s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp PYTHONPATH=. python3 /tmp/d176-seat4-delta-audit.py > /tmp/d176-seat4-delta-audit.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 38 tests in 11.549s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp PYTHONPATH=. python3 /tmp/d176-seat4-g7-symlink.py > /tmp/d176-seat4-g7-symlink.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["G7_SYMLINK_CUSTODY_ESCAPE_REPRODUCED"]},
      "expected": {"exit_code": 0, "tail_regex": "G7_SYMLINK_CUSTODY_ESCAPE_REPRODUCED"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/d176-seat4-frozen-audit.py > /tmp/d176-seat4-frozen-audit.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["FROZEN_SEAMS_OK"]},
      "expected": {"exit_code": 0, "tail_regex": "FROZEN_SEAMS_OK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import subprocess; assert subprocess.check_output([\"git\", \"status\", \"--short\"]) == b\"\"; print(\"WORKTREE_CLEAN\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["WORKTREE_CLEAN"]},
      "expected": {"exit_code": 0, "tail_regex": "^WORKTREE_CLEAN$"}
    }
  ],
  "flags": [
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Initial control consumption triggers 'G7 control must be fresh' without a FAIL artifact. Consumption introduced during presentation produces absence=false and verdict=FAIL.",
      "needs": "Reconcile the earlier freshness refusal with audit requirement (d)."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "G5 independently rejects corrupted evidence despite verdict=GO, but changing verdict alone to REFUSED fails schema validation. Literal verdict-field independence is not implemented.",
      "needs": "Clarify requirement (c) against the contract's GO-required schema."
    }
  ]
}
```

## Findings

**F1 — should_fix:** [produce_g7_control](/Users/edr/code/JouleWise-wt-d176-seat4/scripts/run_night.py:1316) checks supplied paths for symlinks but misses `<control>/night`. Its freshness crawl skips directory-symlink contents, and `mkdir(exist_ok=True)` accepts the link.

With that directory linked to the completed rehearsal’s `night`, the real producer and launcher presentations returned **PASS** and created `presented_rehearsal_receipt.json`, `presented_go_receipt.json`, and `g7_refusal.json` inside the completed rehearsal. Existing hashes remained unchanged, but its custody gained three files.

Reject symlinked destination directories before any write and enforce writes beneath the verified control directory. Add this destination-symlink regression. The bundle loader’s later rejection cannot undo these writes.

## Residual risk

Synthetic fixtures only; no live qualification. Both pre-ARM refusals had exact details and zero ARM reads. All four purpose/window cases, G5 evidence failures, and locator tampering behaved as recorded. F2/F3 identify precise differences from the requested acceptance wording.