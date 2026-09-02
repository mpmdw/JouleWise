```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Focused checks pass; two documentation/evidence defects remain.",
  "workspace": {
    "base_requested": "10845c14",
    "base_mode": "exact",
    "head_start": "10845c14e7ef77c6f46013b18acc8d8569900d8a",
    "head_end": "c05cf1815f01747502c61ca7d238266432f868ba",
    "upstream_end": "c05cf1815f01747502c61ca7d238266432f868ba",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 2, "nit": 1},
    "findings": [
      {
        "id": "C1",
        "severity": "should_fix",
        "lens": "CONTRACT",
        "file": "docs/contracts/bridge_protocol.md:77-80",
        "summary": "The new date gloss says filename or heading dates control selection, but the test uses dated directory components.",
        "evidence": "tests/test_docs_freshness.py:108-118 and :673 select only dated directory components; the proposal itself says directory date at COLD-GATE-RULING.md:283-284."
      },
      {
        "id": "K1",
        "severity": "should_fix",
        "lens": "KERNEL",
        "file": "docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md:310-319",
        "summary": "The census evidence block is not replayable: $S is used in the shell redirection, but the quoted heredoc passes the literal $S path to Python.",
        "evidence": "Independent stdin census reproduced 120 tasks and the claimed rows; the addendum fact is true, but its displayed command sequence cannot produce that output."
      },
      {
        "id": "K2",
        "severity": "nit",
        "lens": "KERNEL",
        "file": "docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md:291-294",
        "summary": "The cited WAVE-ROWS provenance is stale or contradictory.",
        "evidence": "WAVE-ROWS.md:3-4 says it records the wave, but :18 says S9-04 and S9-12 are not yet owned and lists neither kernel row. The kernel mapping itself is valid."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_docs_freshness tests.test_gen_state",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 65 tests in 2.005s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 65 tests in [0-9.]+s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff main -- docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": []
}
```

VERDICT: SHOULD-FIX 2

## Findings

### CONTRACT

C1 is the only contract defect. SF1–SF5 and NIT1, NIT3, NIT9 are installed correctly. The D-170 citations measure correctly: proposal `:269-279` is the quoted body, `:281-290` is the superseded enforcement paragraph, and `:317-331` is the dated replacement addendum.

### EXECUTION

Clean. In-memory mutants produced the required failures:

- SF2 `NOT-FOUND.md` census mutant: named `assertIn` failed.
- SF3 `cells[0]` mutant: four-column control failed.
- Four-column rows with empty required cells or `NOT PINNED:` in the quote column were rejected; production-site `NOT PINNED:` was accepted.

### KERNEL

The base census reproduced 120 tasks and correctly identified the existing S9-04 and S9-12-related rows. Their mechanisms match SHORTLIST.md:228-245 and :432-441, not merely their labels. All five new S9 rows have existing, relevant source citations; no invented `FINDINGS-TABLE.md` citation was found.

All seven D-170 dependencies are `kind: decision`, `scope: start`, `state: pending`, `strength: hard`, with null evidence, and all seven tasks are correctly `blocked` under invariant 3.

## Residual risk

The sibling gate-ledger ruling file and future S9 implementation tests are not present in this detached tree; they are prospective work, not audit failures.