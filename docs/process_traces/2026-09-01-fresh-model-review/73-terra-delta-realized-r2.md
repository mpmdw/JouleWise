```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Delta is exactly the requested test, but its two vectors do not bind a full hash comparison against several plausible weakened comparators.",
  "workspace": {
    "base_requested": "0d14893e",
    "base_mode": "exact",
    "head_start": "3c8393fdde546ada01c2a5b7c6f42edba34f61a4",
    "head_end": "3c8393fdde546ada01c2a5b7c6f42edba34f61a4",
    "upstream_end": null,
    "branch": "feat/2026-09-01-realized-prefill"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "text": "The new test kills a first-56-character comparator, but a tail-only or sorted-character comparator survives both cases; it therefore does not substantiate its every-character mutation-guard claim."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff 0d14893e..3c8393fd --stat && git diff --name-only 0d14893e..3c8393fd",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["tests/test_bundle_read.py | 24 ++++++++++++++++++++++++", "1 file changed, 24 insertions(+)", "tests/test_bundle_read.py"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_bundle_read\\.py"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_bundle_read",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-realized']"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox has no writable temporary directory, so the focused suite could not import; conclusions rely on source inspection.",
      "needs": "Re-run the focused suite in an environment with a writable temporary directory."
    }
  ]
}
```

## Findings

- F1 — should_fix: `[:56]` comparison is killed, but `if expectation.get("token_ids_sha256")[-8:] != token_ids_sha256[-8:]:` survives: the tail differs in case one, while uppercase remains rejected before comparison. `if sorted(expectation.get("token_ids_sha256")) != sorted(token_ids_sha256):` also survives. Add vectors with an early-only difference and a same-multiset reordered hash.

## Residual risk

Uppercase as `evidence_missing` is advisory-correct: an ill-formed hash is unusable evidence at the validation gate, and treating it as missing preserves ruling 44c’s refusal rather than allowing absence to pass.