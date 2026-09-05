```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "The line-audit guard now refuses the refuter's same-length shifted range by authenticating each pinned coordinate-and-content extract.",
  "workspace": {
    "base_requested": "56b2d666533bd0e914d78f007ffdc911fae102fe",
    "base_mode": "exact",
    "head_start": "56b2d666533bd0e914d78f007ffdc911fae102fe",
    "head_end": "56b2d666533bd0e914d78f007ffdc911fae102fe",
    "upstream_end": "56b2d666533bd0e914d78f007ffdc911fae102fe",
    "branch": "feat/2026-09-04-fan-LINE-AUDIT-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md",
    "docs/process_traces/2026-09-04-fanout/LINE-AUDIT-GUARD-01/03-sol-fix-round-1-report.md",
    "tests/test_s0_line_audit_guard.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/LINE-AUDIT-GUARD-01/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_s0_line_audit_guard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 5 tests in 1.631s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
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
  "flags": []
}
```

## Change

F1 is closed. The runsheet retains the existing per-spec grammar, non-empty,
and demanded-count checks, then computes SHA-256 over the exact `source +
ranges` string, a NUL separator, and the selected unnumbered source bytes. The
expected digest is pinned per audited source. This binds both coordinates and
content while leaving the successful numbered `006-pinned-line-audit.txt`
bytes unchanged.

The regression uses the refuter's exact counterfactual: at
`f125ae70c5a57403d9543c197f9b4e41db581881`, it replaces
`scripts/generate_arm_readiness.py 28,192p` with the same-cardinality
`27,191p`. The guard now refuses with `line audit coordinate/content
mismatch`, while the unchanged pin set still passes and remains byte-identical
to the legacy transcript.

| Finding | Cure | File:line |
|---|---|---|
| F1 blocker: a same-length shifted range passed count validation | Authenticate each canonical coordinate-and-content extract and refuse digest mismatch | `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:1128` |
| F1 regression gap: no exact shifted-range case | Execute the refuter's `28,192p` to `27,191p` mutation and require refusal | `tests/test_s0_line_audit_guard.py:186` |

No magistrate-owned state row is required for the cure, and no such file was
edited. The magistrate may close the existing kernel row after the gauntlet;
there is no new row text to apply.

## Verification notes

Per the prompt's preflight restriction, only the touched test module was run;
the repository-wide suite was not run.
