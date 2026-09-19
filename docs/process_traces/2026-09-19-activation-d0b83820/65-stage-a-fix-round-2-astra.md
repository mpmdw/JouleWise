```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Git-fixture fix and renderer pin implemented; document regeneration needs scope expansion and a placement ruling.",
  "workspace": {
    "base_requested": "6cbd84e443b44b0e930f26de5126d2880b80be38",
    "base_mode": "exact",
    "head_start": "6cbd84e443b44b0e930f26de5126d2880b80be38",
    "head_end": "6cbd84e443b44b0e930f26de5126d2880b80be38",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "joulewise/arm_retry.py",
    "tests/test_arm_retry.py",
    "tests/test_gen_evidence_night.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_arm_retry tests.test_git_fixture_maintenance tests.test_gen_evidence_night tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 116 tests in 10.327s", "", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --exit-code HEAD -- docs/process/NIGHT_HANDBACK.md docs/phase_2/derivation_night_runbook.md; git diff --check",
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
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [" 3 files changed, 10 insertions(+), 2 deletions(-)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "3 files changed, 10 insertions\\(\\+\\), 2 deletions\\(-\\)"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: the exact-block test also requires regenerating docs/phase_2/derivation_night_runbook.md, which is outside WRITE_SCOPE. No out-of-scope writes occurred.",
      "needs": "Authorize the additional document path."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the handback's generated markers contain two extra probe-refusal rows and the ruled-registration/QPE prose at lines 136–148. Regeneration would delete these additions, including text required to remain untouched.",
      "needs": "Choose whether to relocate the additions verbatim outside the generated block or incorporate them into the renderer. Recommend relocation, preserving their wording and the current policy enumerations."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox denied ps, so the fixture-orphan census could not observe processes.",
      "needs": "Lead reruns the census in an authorized environment."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["docs/phase_2/derivation_night_runbook.md"],
    "reason": "Both documents must contain the same render_policy() output.",
    "blocked_work": "Complete regeneration and pass test_both_document_blocks_are_exact.",
    "minimal_change": "Regenerate the runbook policy block with the updated registration-refusal row."
  }
}
```

## Change

Moved the existing handback refusal wording into the source table and pinned its rendered row. Routed evidence-fixture Git initialization through the shared helper.

Both documents remain byte-for-byte unchanged, preserving all prior amendments. No commit was made.

## Verification notes

The requested bench passed 115 of 116 tests. Only `test_both_document_blocks_are_exact` failed; the maintenance guard, evidence-generator tests, and new renderer pin passed.

Next step: expand scope to the runbook and rule on relocating the handback additions. Then regenerate both blocks and rerun the bench. Broader verification remains pending this early return.