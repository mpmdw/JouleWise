```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "I1 is a new scanner-edge-case signature, its counterfactual fails as expected, and the guard introduces no tested defects.",
  "workspace": {
    "base_requested": "1529b09a",
    "base_mode": "exact",
    "head_start": "1529b09a9fc0f11216b2a6b6e5c91c2cbbc190fc",
    "head_end": "2983cdd4e2c9d9ad81ba5d66707911e90c6312fe",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "verdict": "CLEAN",
    "classification_code": "NEW",
    "classification": "NEW: I1 is distinct from round 1's naive-pipe-split defect. Round 1 introduced a stateful GFM-aware scanner that correctly handled escaped pipes and code spans, but incorrectly treated an escaped backtick outside a span as opening scanner state. The failure trigger is therefore a scanner edge case, not the original representation-blind split.",
    "findings": [],
    "counterfactual": "With the guard removed, the new row splits as [\"4\", \"gate \\\\` literal tick | RUN evidence.txt |\"], so item 4 is omitted and check() returns [\"gate-ledger: item 4: missing\"]. The new test consequently fails. With the guard, the evidence cell is retained.",
    "edge_cases": [
      {
        "id": "escaped_backtick_outside",
        "input": "| 4 | gate \\` literal tick | RUN scripts/check_gate_ledger.py |",
        "scanner_cells": ["4", "gate \\` literal tick", "RUN scripts/check_gate_ledger.py"],
        "gfm_cells": ["4", "gate ` literal tick", "RUN scripts/check_gate_ledger.py"],
        "assessment": "Correct cell boundaries; scanner intentionally retains source escapes."
      },
      {
        "id": "escaped_backtick_inside_code_span",
        "input": "| 4 | gate ``a \\` | b`` | RUN scripts/check_gate_ledger.py |",
        "scanner_cells": ["4", "gate ``a \\` | b``", "RUN scripts/check_gate_ledger.py"],
        "gfm_cells": ["4", "gate a ` | b", "RUN scripts/check_gate_ledger.py"],
        "assessment": "Correct; code_ticks is non-null, so the guard does not apply and the backslash remains literal inside the code span."
      },
      {
        "id": "even_backslashes",
        "input": "| 4 | gate \\\\` literal tick` | RUN scripts/check_gate_ledger.py |",
        "scanner_cells": ["4", "gate \\\\` literal tick`", "RUN scripts/check_gate_ledger.py"],
        "gfm_cells": ["4", "gate \\ literal tick", "RUN scripts/check_gate_ledger.py"],
        "assessment": "Correct boundaries; an even backslash count leaves the backtick unescaped."
      },
      {
        "id": "three_tick_run",
        "input": "| 4 | gate \\``` literal tick`` | RUN scripts/check_gate_ledger.py |",
        "scanner_cells": ["4", "gate \\``` literal tick``", "RUN scripts/check_gate_ledger.py"],
        "gfm_cells": ["4", "gate ` literal tick", "RUN scripts/check_gate_ledger.py"],
        "assessment": "Correct; the guard consumes only the escaped first tick and the remaining two-tick run opens the span."
      },
      {
        "id": "cell_exactly_backslash",
        "input": "| 4 | \\ | RUN scripts/check_gate_ledger.py |",
        "scanner_cells": ["4", "\\", "RUN scripts/check_gate_ledger.py"],
        "gfm_cells": ["4", "\\", "RUN scripts/check_gate_ledger.py"],
        "assessment": "Correct."
      },
      {
        "id": "escaped_pipe_after_escaped_backtick",
        "input": "| 4 | gate \\`\\| literal tick | RUN scripts/check_gate_ledger.py |",
        "scanner_cells": ["4", "gate \\`\\| literal tick", "RUN scripts/check_gate_ledger.py"],
        "gfm_cells": ["4", "gate `| literal tick", "RUN scripts/check_gate_ledger.py"],
        "assessment": "Correct; the guard resets backslash state, then the following escaped pipe is handled normally."
      },
      {
        "id": "crlf",
        "input": "| 4 | gate 4 | RUN scripts/check_gate_ledger.py |\\r\\n",
        "scanner_cells": ["4", "gate 4", "RUN scripts/check_gate_ledger.py"],
        "gfm_cells": ["4", "gate 4", "RUN scripts/check_gate_ledger.py"],
        "assessment": "Correct; splitlines() and strip() remove CRLF framing."
      }
    ]
  },
  "tests": [
    {
      "id": "counterfactual",
      "result": "PASS",
      "observed": "Baseline 1529b09a returns item 4 missing for the new escaped-backtick row; current guard preserves the row."
    },
    {
      "id": "named_suite",
      "result": "PASS",
      "observed": "Ran 21 tests in 1.051s; OK."
    },
    {
      "id": "synthetic_12_row",
      "result": "PASS",
      "observed": "gate-ledger: 12/12 RUN"
    }
  ],
  "same_signature": {
    "round_1": [
      ["merge-ref versus PR-head binding", "KILLED"],
      ["naive pipe split ignoring GFM", "KILLED"],
      ["_check_pointer path-rule parity", "KILLED"],
      ["items 1-11 commit-or-path acceptance", "KILLED"],
      ["real outside-file traversal refusal coverage", "KILLED"],
      ["malformed RUN refusal", "KILLED"],
      ["item-12 non-SHA refusal", "KILLED"],
      ["stable input-error refusal", "KILLED"],
      ["template labels and pointer-only orchestration contract", "KILLED"]
    ],
    "I1": ["NEW scanner edge-case signature", "KILLED"],
    "overall": "All nine round-1 classes are KILLED; I1 is NEW and KILLED. Nothing survives."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".....................",
          "----------------------------------------------------------------------",
          "Ran 21 tests in 1.051s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 21 tests in [0-9.]+s\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 - <<'PY'  # synthetic 12-row body under TMPDIR; item 12 is subprocess.check_output([\"git\", \"rev-parse\", \"HEAD\"]); invoke scripts/check_gate_ledger.py PY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["gate-ledger: 12/12 RUN"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^gate-ledger: 12/12 RUN$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check 1529b09a..2983cdd4 -- scripts/check_gate_ledger.py tests/test_check_gate_ledger.py",
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

## Findings

None.

## Residual risk

None identified in the requested guard-focused cases.