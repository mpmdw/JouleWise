```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Final-head review found two stale trace-index records and one broken packet reference; code, kernel, delta cures, and required checks pass.",
  "workspace": {
    "base_requested": "c05cf181",
    "base_mode": "exact",
    "head_start": "162049bd6146ba13fc2191138faaee292e603de9",
    "head_end": "162049bd6146ba13fc2191138faaee292e603de9",
    "upstream_end": "403998e164e037a59d7681dda0e786ad94b8d796",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 2,
      "nit": 1
    },
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "docs/process_traces/2026-09-02-process-rules/README.md:5-6",
        "summary": "Three installation file:line anchors no longer measure their claimed targets.",
        "evidence": "At HEAD, tests/test_docs_freshness.py:313 is blank and the clause-map test is at :670; docs/decision_log.md:10351 is the old smoke-corpus trace and Q2 is at :10355; docs/decision_log.md:10567 is a dependency sentence and the Q1/Q2 summary is at :10583. The other sampled anchors bridge_protocol.md:54 and agent_playbook.md:60 remain correct."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "docs/process_traces/2026-09-02-t26-items-1-4/MAGISTRATE-NOTES.md:26-66",
        "summary": "The final PR-gate notes have an incomplete bench-commit and branch-history ledger.",
        "evidence": "Line 26 promises a bench commit 'below', but the Bench commits section lists only d8451daa and f84be217. Replaying the displayed git-log command produces eleven commits, while its recorded output stops at f84be217 and omits 10845c14, c05cf181, and final head 162049bd."
      },
      {
        "id": "F3",
        "severity": "nit",
        "file": "docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md:8",
        "summary": "The ruling names a nonexistent packet basename.",
        "evidence": "test -e docs/process_traces/2026-09-02-process-rules/coldgate-process.md returned 1; the actual custodied file is PACKET-coldgate-process.md and exists."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_docs_freshness tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 65 tests in 2.051s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 65 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 scripts/gen_state.py --check",
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
      "cmd": "git show 10845c14:docs/process/state_kernel.json | python3 -c \"\nimport json,re,sys\nk=json.load(sys.stdin)\nprint(len(k['tasks']))\nfor kid,v in k['tasks'].items():\n    m=sorted(set(re.findall(r'S9-\\d+[a-z]?',json.dumps(v))))\n    if m: print(kid, m, v['status'])\n\"   # census of rows whose JSON cites an S9-nn label, kernel at 10845c14 (replayable; re-executed 2026-09-02 after luna 238 K1)",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "120",
          "AUTHENTICATOR-ALLOWLIST-GUARD-01 ['S9-09'] queued",
          "COLLECTOR-MANIFEST-SHA-IDENTITY-01 ['S9-01'] blocked",
          "GAMMA-UNIT-ROSTER-GUARD-01 ['S9-04'] queued",
          "L10-A-G2B-CONTRACT-PREFIX-01 ['S9-12'] blocked",
          "L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01 ['S9-01', 'S9-07', 'S9-12'] blocked",
          "RECORDER-SINGLE-OPERATOR-PREAMBLE-01 ['S9-13'] queued",
          "REISSUE-V3-GENERATION-GUARD-01 ['S9-11'] queued",
          "TRANSACTION-RULED-ARTIFACTS-01 ['S9-10'] queued"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^120\\nAUTHENTICATOR-ALLOWLIST-GUARD-01[\\s\\S]*TRANSACTION-RULED-ARTIFACTS-01 \\['S9-10'\\] queued$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show d01fd4c5 --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/process/state_kernel.json     | 974 ++++++++++++++++++++++++++++++++++++-",
          "5 files changed, 1049 insertions(+), 29 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "docs/process/state_kernel.json[\\s\\S]*5 files changed"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git show d01fd4c5:docs/process/state_kernel.json | grep -c 'GAMMA-UNIT-ROSTER-GUARD-01'\ngit show d01fd4c5:docs/process/state_kernel.json | grep -c 'L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "4",
          "4"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^4\\n4$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The prospective *-impl.md test selects zero current reports; its assertion helper and direct/nested dated-directory selector were exercised separately in scratch and passed.",
      "needs": ""
    },
    {
      "id": "R2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "_has_executed_evidence remains shape-only and checks a repository-relative worktree path rather than the Git HEAD object; the prior magistrate disposition accepts this because CI uses a clean checkout.",
      "needs": ""
    }
  ]
}
```
VERDICT: SHOULD-FIX 2

## Findings

- F1 — SHOULD-FIX — `docs/process_traces/2026-09-02-process-rules/README.md:5-6`: refresh the three stale installation anchors. Executed spot-checks found the actual targets at `tests/test_docs_freshness.py:670`, `docs/decision_log.md:10355`, and `docs/decision_log.md:10583`.

- F2 — SHOULD-FIX — `docs/process_traces/2026-09-02-t26-items-1-4/MAGISTRATE-NOTES.md:26-66`: add the missing `c05cf181` and `162049bd` bench records and refresh the displayed branch log. The replay also contains `10845c14`, absent from the recorded output.

- F3 — NIT — `docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md:8`: `coldgate-process.md` does not exist; the filename is `PACKET-coldgate-process.md`.

The requested delta checks otherwise pass:

- The S1 gloss now exactly matches `_dated_process_trace_files` and `DATED_DIRECTORY`: it uses a `YYYY-MM-DD`-prefixed dated directory component at any depth.
- The displayed S9 census was replayed verbatim. Its stdout was byte-equal to the recorded body: 422/422 bytes, empty stderr, exit 0.
- `d01fd4c5` introduced both named task IDs: each has four occurrences in that commit’s kernel and zero in its parent.
- All 13 changed kernel tasks have an `acceptance.pointer.path` present at HEAD and a resolving JSON pointer.
- The sampled D-170 ruling spans `:269-279`, `:281-290`, `:317-331`, §B4 `:245-247`, and `scripts/gen_state.py:185-218` measure correctly.

Mandatory tail:

```text
----------------------------------------------------------------------
Ran 65 tests in 2.051s

OK
TWO_MODULE_EXIT=0
GEN_STATE_EXIT=0
```

## Residual risk

The clause-map file-level test is intentionally prospective and currently selects zero real `*-impl.md` reports. Scratch probes confirmed that both direct and nested dated-directory reports are selected and that malformed clause maps fail. No repository files were modified.