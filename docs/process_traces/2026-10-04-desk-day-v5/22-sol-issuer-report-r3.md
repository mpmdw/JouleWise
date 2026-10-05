```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented F1/F2; focused checks and archived replays pass; changes remain uncommitted.",
  "workspace": {
    "base_requested": "a1126009",
    "base_mode": "exact",
    "head_start": "a112600925b36beb41d3c55bae06342e10330921",
    "head_end": "a112600925b36beb41d3c55bae06342e10330921",
    "upstream_end": "a112600925b36beb41d3c55bae06342e10330921",
    "branch": "feat/2026-10-04-g2a-issuer-harvest-bound"
  },
  "pathspec": [
    "scripts/issue_g2a_prefill_prompt_pin.py",
    "tests/test_issue_g2a_prefill_prompt_pin.py",
    "tests/test_summarize_g2a_prefill_probe.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry3 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_issue_g2a_prefill_prompt_pin.py tests/test_summarize_g2a_prefill_probe.py tests/test_select_g2a_prefill_length.py tests/test_d117_contrast_v5_pack.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["102 passed, 209 subtests passed in 122.83s (0:02:02)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\\d+ passed, \\d+ subtests passed"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry3 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_issue_g2a_prefill_prompt_pin.py::IssueG2APrefillPromptPinTests::test_selection_coordinate_alias_resolves_inside_verified_archive",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["1 passed in 3.43s"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 passed"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry3 PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-issuer-dry3/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 XDG_CACHE_HOME=/tmp/dd5-issuer-dry3/cache /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-issuer-dry3/replay.py select final",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"exit_code\": 0, \"g2a_record_sha256\": \"c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222\", \"pin_sha256\": \"d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"exit_code\": 0.*c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222.*d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry3 PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-issuer-dry3/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 XDG_CACHE_HOME=/tmp/dd5-issuer-dry3/cache /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-issuer-dry3/replay.py recover final",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "G2-a prompt pin refused: harvest_committed_harvest_mismatch",
          "exit_code=2"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "harvest_committed_harvest_mismatch[\\s\\S]*exit_code=2"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry3 PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-issuer-dry3/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 XDG_CACHE_HOME=/tmp/dd5-issuer-dry3/cache /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-issuer-dry3/replay.py counterexamples",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "relabeled_block2: exit_code=2; G2-a prompt pin refused: archive_sha256sum_mismatch",
          "new_selection_over_recover: exit_code=2; G2-a prompt pin refused: harvest_committed_harvest_mismatch",
          "whitespace_both_hashes_updated: exit_code=2; G2-a prompt pin refused: harvest_committed_harvest_mismatch",
          "null_relabeled_recover: exit_code=2; G2-a prompt pin refused: harvest_committed_harvest_mismatch"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "null_relabeled_recover: exit_code=2; G2-a prompt pin refused: harvest_committed_harvest_mismatch"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check",
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
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Git staging failed with Operation not permitted when creating the worktree index.lock outside sandbox writable roots. Changes remain uncommitted; nothing was pushed.",
      "needs": "Lead review and stage/commit the patch for PR #471."
    }
  ]
}
```

## Change

F1 anchors harvest and selection bytes to Git HEAD records, verifies archive checksums and derived output hashes, and binds the frozen plan to block-3 policy. Superseded r1 RECOVER records refuse.

F2 accepts zero large members and reuses the summarizer’s `_run_provenance` to derive the selected rung’s valid receipt members. Added regressions cover V6 and all four provenance counterexamples.

## Verification notes

The initial run exposed two synthetic fixture anchor collisions; corrected and rerun successfully. The final selection-path normalization received a separate focused check. The whole suite was omitted as instructed.

Sandbox restrictions prevented committing. Next step: lead review and commit for PR #471.