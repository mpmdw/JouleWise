```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Execution review complete: all 315 required tests pass, but independent probes expose one blocker and one should-fix.",
  "workspace": {
    "base_requested": "c9081c6e",
    "base_mode": "exact",
    "head_start": "c9081c6ee61103c11c17216eda4fffb4f4e814c2",
    "head_end": "c9081c6ee61103c11c17216eda4fffb4f4e814c2",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "R1",
        "severity": "blocker",
        "path": "joulewise/battery_float.py",
        "line": 827,
        "summary": "Mandatory containers encoded as valid UTF-16 or UTF-32 return pass instead of CustodyUnreadable.",
        "authority": "Addendum-3 ruling section 3: non-UTF-8 mandatory containers are CustodyUnreadable; amendment 29.",
        "fix": "Decode container bytes explicitly as UTF-8 inside the existing exception boundary before json.loads; add valid UTF-16 and UTF-32 object cases for all three wrappers."
      },
      {
        "id": "R2",
        "severity": "should_fix",
        "path": "joulewise/battery_float.py",
        "line": 1004,
        "summary": "A genuine pre-only shape-(iii) envelope returns post evidence missing rather than the required single quiet span unavailable reason.",
        "authority": "Erratum amendment 30 shape-(iii) clause and T30-f/P-B.",
        "fix": "After pair authentication preserves raw-custody raises, normalize battery-recorded shape-(iii) verdicts to battery_float_evidence_missing with reasons exactly ('quiet span unavailable',). Add a pre-only first-write fixture."
      }
    ],
    "closure": {
      "amendment_29": "OPEN",
      "amendment_30_erratum": "OPEN",
      "amendment_31_S0": "CLOSED",
      "S-1": "CLOSED",
      "S-2": "CLOSED"
    },
    "same_signature": "yes",
    "honest_shapes_wrongly_raising": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep tests.test_evidence_night tests.test_night_kinds > /tmp/s0-r4-execution-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...................................",
          "----------------------------------------------------------------------",
          "Ran 315 tests in 779.698s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 315 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/s0-r4-execution-probes.py > /tmp/s0-r4-execution-probes.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PROBES COMPLETE"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PROBES COMPLETE"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/s0-r4-counterexamples.py > /tmp/s0-r4-counterexamples.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "",
          "----------------------------------------------------------------------",
          "Ran 2 tests in 0.513s",
          "",
          "FAILED (failures=10)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V4",
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
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R1 retains the ruled non-UTF-8 mandatory-container custody-to-status/pass signature after round 4.",
      "needs": "Return the recurrence to the cold gate under the charge and addendum-3 disposition before another fix round."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "P-D remains reproducible in the S2-owned summary: a deleted completed journal raises in the S0 helper, while summarize returns no_rounds with sources [].",
      "needs": "Complete the separately assigned S1/S2 erratum obligations before claim-bearing use."
    }
  ]
}
```

## Findings

**R1 — BLOCKER: valid non-UTF-8 containers are admitted.**

At `joulewise/battery_float.py:827`, `json.loads(body, ...)` automatically recognizes UTF-16 and UTF-32. Re-encoding an otherwise passing `session.json`, `metadata.json`, or `instrument_evidence.json` in either encoding returned **`pass`** in all six cases. The ruling explicitly assigns non-UTF-8 mandatory containers to `CustodyUnreadable`.

The existing T16-a bytes `b"\xff\xfe"` do not expose this: they are also an incomplete JSON document.

Exact reproduction: [counterexample script](/tmp/s0-r4-counterexamples.py), test `Counterexamples.test_non_utf8_containers_must_refuse`. It creates each repository fixture, executes `path.write_bytes(path.read_text().encode(encoding))`, and calls the corresponding wrapper.

Fix: change the parser input to `body.decode("utf-8")` inside the existing `try`, retaining the duplicate-key hook and exception conversion. Add both valid alternative-encoding cases to each wrapper’s matrix.

**R2 — SHOULD-FIX: the actual P-B shape misses the required reason.**

A first-write envelope contains only the pre battery record. With `end_stamp` absent, a pre-only `battery_float`, and the post raw absent, authentication returns:

```text
battery_float_evidence_missing
('post evidence missing: phase not recorded',)
```

This occurs with the journal absent, empty, truncated to `{`, or containing a provisional row. Amendment 30 requires exactly `('quiet span unavailable',)`.

The committed T30-f fixture retains **both** phase records after removing `end_stamp`, concealing this gap.

Exact reproduction: the same [script](/tmp/s0-r4-counterexamples.py), test `Counterexamples.test_honest_pre_only_provisional_shape`.

Fix: after `authenticate_pair` has preserved its custody raises, normalize only battery-recorded shape-(iii) verdicts to the required status and single reason. Keep historical handling and the core rung order unchanged.

Run both reproductions from the reviewed checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/s0-r4-counterexamples.py
```

Observed: **2 tests, 10 failing subcases**. [Full output](/tmp/s0-r4-counterexamples.log).

**same signature: yes**

Specifically, R1 retains the custody-to-status/`pass` branch of the ruled class. The tested missing-file, read-error, truncated-JSON, duplicate-key, symlink, directory, and non-object cases otherwise refuse correctly where required. I found no surviving empty fallback for those tested failures.

**Closure, with executed evidence**

| Item | State | Observed |
|---|---|---|
| Amendment 29 | **OPEN** | R1; prescribed T16 fixtures pass. |
| Amendment 30, erratum | **OPEN** | R2; count and journal-custody rules pass. |
| Amendment 31, S0 | **CLOSED** | Malformed/non-object/missing events raise; valid events lacking stage bounds yield span unavailable; raw loss still raises. |
| T16-a | **CLOSED, literal matrix** | All eight specified forms across three kinds raise. Valid UTF-16/32 extension exposes R1. |
| T16-b | **CLOSED** | Missing battery key and malformed digest remain the prescribed statuses. |
| T16-c | **CLOSED** | Duplicate container keys raise `CustodyUnreadable`. |
| T30-a | **CLOSED** | Digest disagreement raises; deleting that journal raises `round journal missing`. |
| T30-b | **CLOSED** | Empty completed journal raises, including the raw-plus-session rewrite variant. |
| T30-c | **CLOSED** | Honest zero-row completion passes. |
| T30-d | **CLOSED** | Missing refusal journal raises. |
| T30-e | **CLOSED** | A refusal journal containing a row raises. |
| T30-f | **OPEN** | Journal is correctly ignored and pre raw loss raises, but genuine pre-only P-B has the wrong reason: R2. |
| T30-g | **CLOSED** | Readable historical session without `battery_float` remains evidence missing; journal absence/corruption is ignored. |
| T30-h | **CLOSED** | Fixture records `journal_rows` and writes completed/refusal journals by default. |
| T30-i | **CLOSED** | Absent, boolean, string, and negative counts raise; P-A’s one row/two workers does not raise. |
| T30-j | **CLOSED** | Mismatching second row raises; removing it causes the count-mismatch raise. |
| S-1 | **CLOSED** | Decorator and nested rebinding mutations each made the actual pin test RED. |
| S-2 | **CLOSED** | `copy.replace`, direct/aliased imports, and `x.__replace__` are flagged. |

E1–E5’s specified counterexamples are closed by the executed tests and probes. No tested honest P-A or P-B shape raised wrongly.

The [190-case scratch run](/tmp/s0-r4-execution-probes.py) exercised all five containers, applicable envelope shapes, field removal, invalid witnesses, injected read failures, and the requested mutations. [Results](/tmp/s0-r4-execution-probes.log).

Independently traversing `FROZEN_ROOTS` in the base and candidate found **39 byte-identical closure members**. All **39 pins** equal independently computed base-segment hashes under the test’s segment rule. Only `AuthenticatedSlot` and `AuthenticatedVerdict` pins changed from round 3, as authorized.

All five required modules passed: **315 tests, 779.698 seconds**. Repository files remain unchanged and the checkout is clean.

## Residual risk

P-D remains an explicitly S2-owned dependency: the helper raises for a deleted completed journal, but `summarize` returns `no_rounds` with `sources: []`. S1/S2’s remaining erratum obligations were not implemented by this read-only review.

Removing `end_stamp`, or removing refusal `error_class`, demotes the envelope to shape (iii) according to the erratum’s object-only classification. Executed probes yielded evidence missing, never `pass`; this is prescribed behavior, not a newly identified implementation defect.

Verification used fixtures and scratch files, not live hardware measurement.