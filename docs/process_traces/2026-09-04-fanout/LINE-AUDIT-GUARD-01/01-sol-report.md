```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "The S-0 immutable-line audit now refuses empty, malformed, short, and past-end per-file extracts while preserving the established successful transcript bytes.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-LINE-AUDIT-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md",
    "docs/process_traces/2026-09-04-fanout/LINE-AUDIT-GUARD-01/01-sol-report.md",
    "tests/test_s0_line_audit_guard.py"
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
      "cmd": "python3 -m unittest -v tests.test_s0_line_audit_guard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 4 tests in 1.885s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests in [0-9.]+s\\n\\nOK"
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

An extract is the numbered source lines selected by one file's cited ranges.
The runsheet now stages each file's extract separately, validates the inclusive
range grammar, calculates the demanded line count, and refuses an empty or
short result before appending it to `006-pinned-line-audit.txt`. Successful
output retains the former filename and exact bytes.

The regression module executes the fenced runsheet block itself. Its positive
case replays the unchanged pin set at the estate head recorded by the issued
S-0 completion record and compares the resulting transcript byte-for-byte with
the former pipeline. Its counterfactual cases place an invalid file before a
valid file, which is the shape that the former combined non-emptiness check
accepted.

### Scoped design

**Forcing problem.** A single non-empty file could mask a short or empty file
in the combined transcript, so the audit did not establish that every cited
range was present.

**Options.** Keeping the combined check cannot meet the kernel acceptance. A
repository helper would add a tool-availability dependency to a runsheet that
audits an independently pinned Git head. Generating a new helper inside the
proof estate would add another sizeable audited program. The selected option
is a small inline guard around the existing pipeline.

**Recommendation.** Keep the inline guard. It derives the expected count from
the ranges already present in the runsheet and introduces no new source of
coordinates or executable dependency.

**Worked example.** A citation requesting `1,4p` from a file containing two
lines emits two lines. If a later file emits valid content, the old final
`test -s` still passed; the new guard stops on the first file with its expected
and emitted counts. A citation wholly past the file end stops as an empty
per-file extract.

### Finding and decision table

| ID | Kind | Finding or decision | Disposition |
|---|---|---|---|
| F1 | Defect | Combined non-emptiness did not prove that each file contributed all cited lines. | Closed by per-file emptiness and count checks. |
| D1 | Design | Count the existing inclusive ranges inline and stage each extract before concatenation. | Implemented; no new coordinate registry or helper dependency. |
| D2 | Contract | The pinned range set and successful `006-*` transcript must not change. | Preserved and checked at the issued S-0 estate head. |
| H1 | Hardware or external dependency | No acceptance item requires hardware, Ed action, or a pending dependency. | None. |
| B1 | Magistrate-owned bookkeeping | The kernel row and its generated queue and run-state projections need closure after review. | Not edited under the prompt's explicit ownership fence. |

No unresolved design choice remains, so there is no `NEEDS_RULING` item. The
magistrate's exact next step is to review this diff, record the row's closure
in `docs/process/state_kernel.json`, and regenerate its owned projections.

## Verification notes

The repository-wide unit-test suite was not run, as required by the preflight
rule. Verification was limited to the focused module and diff-whitespace
inspection recorded in the envelope.
