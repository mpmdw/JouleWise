```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Expanded and pinned the PR-0 v1 replay golden; focused tests and all nine supplied mutations pass.",
  "workspace": {
    "base_requested": "ab48c5d3",
    "base_mode": "exact",
    "head_start": "ab48c5d381e74f402e0cde3366f494aa61e3918c",
    "head_end": "ab48c5d381e74f402e0cde3366f494aa61e3918c",
    "upstream_end": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "branch": "test/2026-09-25-claimgate-pr0-golden"
  },
  "pathspec": [
    "scripts/capture_claim_replay_golden.py",
    "tests/golden/claimgate_v1_replay.json",
    "tests/test_claim_replay_golden.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_claim_replay_golden -v",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 5 tests", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 5 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/claimgate-final-mut.wpDBBO/mut.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["M8 window floor selector ignores metric       -> KILLED", "M9 issuance gate skips verdict validation     -> KILLED"]},
      "expected": {"exit_code": 0, "tail_regex": "M1.*KILLED[\\s\\S]*M9.*KILLED"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "python3 scripts/capture_claim_replay_golden.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Two regenerations produced identical SHA-256: 6440e60a342b0485ef94e7dbe8e431b3868eb96248eb14bfdb68feb78115a045"]},
      "expected": {"exit_code": 0, "tail_regex": "wrote tests/golden/claimgate_v1_replay.json"}
    },
    {
      "id": "V4",
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
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No selected checked-in finalized v1 manifest exists; v1_golden_manifest_ids is []. Fixture-family replay remains non-issuing.",
      "needs": "Carry the empty manifest set and fixture limitation into the PR body."
    }
  ]
}
```

## Change

Added the claim decision matrix, window-engine replay, issuance-gate probe, pinned path list, and explicit manifest-ID selection rule. The golden is now indented and has blob SHA `e5e84930185e3add160ec3b4a7f6c363fe4f9447`. Only the three allowed files changed; no `joulewise/` file changed or commit was made.

## Verification notes

The focused suite passed. In a `/tmp` clone, **M1–M9 were all killed**. Two regenerations were byte-identical. A separate clone check confirmed that an untracked file under `joulewise/` makes the capture script refuse a refresh.

## Residual risk

The fixture-family section authenticates non-issuing fixtures. The admitting issuance probe uses the existing test seams for manifest, sidecar, floor acceptance, and the valid-case verdict wire; its rejected case exercises real verdict validation.