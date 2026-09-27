```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All 301 focused tests pass, but two executed custody downgrades remain, including a journal deletion that returns pass.",
  "workspace": {
    "base_requested": "5d5a0b7533335c1c0c85286a6728d72e2041f7db",
    "base_mode": "descendant",
    "head_start": "783a09bec56996f5cdeaa9d4c62c5d9e5246f0ed",
    "head_end": "783a09bec56996f5cdeaa9d4c62c5d9e5246f0ed",
    "upstream_end": "5d5a0b7533335c1c0c85286a6728d72e2041f7db",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "same_signature": "yes",
    "closure": {
      "C1": "CLOSED",
      "C2": "CLOSED",
      "C3": "CLOSED",
      "C4": "CLOSED",
      "C5": "CLOSED",
      "C6": "CLOSED",
      "C7": "CLOSED",
      "C8": "CLOSED",
      "C9": "CLOSED",
      "C10": "CLOSED",
      "C11": "CLOSED",
      "C12": "CLOSED",
      "C13": "CLOSED",
      "A20": "CLOSED",
      "A21": "CLOSED",
      "A22": "CLOSED",
      "A23": "CLOSED",
      "A24": "CLOSED",
      "A25": "CLOSED",
      "A27": "CLOSED",
      "A28": "CLOSED"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Malformed mandatory JSON masks raw custody failure",
        "evidence": "For each of quiet, bundle and capture, deleting the recorded post raw file raises CustodyFailure; replacing session.json, metadata.json or instrument_evidence.json with '{' changes the result to battery_float_evidence_missing.",
        "fix": "Raise CustodyUnreadable when a mandatory wrapper JSON file is missing, unreadable, malformed or not an object. Keep evidence_missing for absent pair fields inside a readable object."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Deleting rounds.jsonl converts a custody mismatch to pass",
        "evidence": "A capture-shaped quiet envelope with a mismatching round raw digest raises CustodyFailure. Deleting rounds.jsonl returns pass with no reasons.",
        "fix": "Obtain a ruling amending C1: bind the journal's required presence and row count to capture-shaped sessions, while retaining the explicitly empty refusal-shaped journal."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 301 tests in 859.807s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 301 tests in .*s.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float.RoundThreeAuthenticationTests tests.test_battery_float.S0FreezeTests tests.test_battery_float_consumers.ConsumerGuardTests tests.test_battery_float_sweep.SweepGuardTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 41 tests in 46.281s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 41 tests in .*s.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_s0_freeze_audit.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["base/head closure and pins: 39 identical", "round 3/3b frozen edits: ['CustodyFailure']"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "base/head closure and pins: 39 identical.*round 3/3b frozen edits: \\['CustodyFailure'\\]"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_s0_delta_repro.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["quiet: CustodyFailure -> battery_float_evidence_missing", "bundle: CustodyFailure -> battery_float_evidence_missing", "capture: CustodyFailure -> battery_float_evidence_missing", "deleted rounds.jsonl: CustodyFailure -> pass"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "quiet: CustodyFailure -> battery_float_evidence_missing.*deleted rounds.jsonl: CustodyFailure -> pass"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_s0_c10_mutations.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["no_skipped RED failures 0 errors 1", "no_exemption RED failures 1 errors 0", "unreadable_kind RED failures 1 errors 0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "no_skipped RED.*no_exemption RED.*unreadable_kind RED"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "F2 follows C1's explicit rule that a missing rounds.jsonl means zero rows; closing this accepting counterexample requires changing that rule.",
      "needs": "Lead to obtain a ruling before claiming S0 custody closure."
    }
  ]
}
```

## Findings

**F1 — BLOCKER. Same signature: yes.** The exception handlers in [battery_float.py](/Users/edr/code/JouleWise-wt-s0delta-sol-f8d6cab1/joulewise/battery_float.py:923) turn unreadable `session.json`, `metadata.json` and `instrument_evidence.json` into empty objects. The [reproducer](/tmp/bfgs_s0_delta_repro.py), run with V4, shows that corrupting any one of those files changes an existing deleted-raw-file `CustodyFailure` into a status. Raise `CustodyUnreadable` for an unreadable mandatory file or invalid JSON object; preserve the status for missing pair fields in a readable object.

**F2 — BLOCKER.** V4 also shows `rounds.jsonl` deletion changing a digest mismatch from `CustodyFailure` to `pass`. [C1’s ruling](/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/60-bfgs-s0/41-fix-contract-round3.md) explicitly treats a missing journal as zero rows. C1’s specified malformed and unreadable cases are closed, but this accepting case needs a lead ruling on journal presence for capture-shaped sessions.

The closure labels in the envelope refer to each item’s **written S0 acceptance**; they do not override F1 or F2. Executed evidence is:

| Items | Closure evidence |
|---|---|
| C1 | Round mismatch and malformed or unreadable journal tests pass; V4 exposes F2 under the missing-journal rule. |
| C2 | Span validity, owed span and custody-before-span tests pass. |
| C3 | Raw symlink rejection test passes. |
| C4 | Duplicate-key tests pass for all five JSON input types. |
| C5–C6 | Missing kind flag journals a refusal; stale `check.json` is refused. |
| C7 | V3 independently recomputes all 39 base-source pins; every closure definition matches main. Only `CustodyFailure` changed during rounds 3/3b, and the bench restored it. Production consumers use `.detail` or catch `CustodyFailure`; none require a nonempty `.failures` list or the exception’s message prefix. |
| C8 | The nine replacement exceptions are keyed by path, function and call text. Guard tests cover new calls, allowed calls and stale entries. |
| C9 | `False` and `0.0` exit-code refusal tests pass. |
| C10 | Baseline-green guard (C10): V5 independently turns each of the three guards red with its corresponding mutation. |
| C11 | All three aliased `observe` forms are detected by the phase sweep. |
| C12–C13 | Bundle digest and capture identity tests pass. |
| A20–A25, A27–A28 | S0-owned conversion, span, stamp, digest, factory, identity and test obligations pass in V1/V2. A26 and the S1/S2 clauses remain with their assigned owners. |

The worktree is clean at the requested candidate commit. No repository files were changed.

## Residual risk

This review used fixtures and temporary files under `/tmp`; it did not perform live hardware validation.