```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "Content-repair replacement verified; the literal unwritable-directory courier-launch guarantee requires a lead ruling because run_courier fails independently before spawning.",
  "workspace": {
    "base_requested": "17f374f2b4e4f67b5f84cea66adabfe1244474b4",
    "base_mode": "exact",
    "head_start": "17f374f2b4e4f67b5f84cea66adabfe1244474b4",
    "head_end": "17f374f2b4e4f67b5f84cea66adabfe1244474b4",
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
        "title": "No replacement of this helper alone guarantees courier launch with an unwritable night directory",
        "location": "scripts/run_night.py:1294",
        "detail": "_acquire_courier_lock raises PermissionError at scripts/run_night.py:1232 before Popen at scripts/run_night.py:1316. A real chmod-based scratch test reproduced this."
      },
      {
        "id": "R2",
        "severity": "should_fix",
        "title": "Normalize parsing failures, type-check the state, and guard the entire helper",
        "location": "scripts/run_night.py:1243",
        "detail": "The proposed replacement repairs malformed content, preserves valid states, and contains Exception failures, including exception-formatting failures."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/d0b83820-consult-check.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 9 tests in 4.258s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 9 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night.EvidenceProbeTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 13 tests in 11.376s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 13 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: distinguish helper exception containment from guaranteed courier launch when the whole night directory is unwritable.",
      "needs": "Recommend accepting the helper-local guarantee and recording the caller storage prerequisite; otherwise a separate caller-level degraded-delivery design is required."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only consult: proposal exercised from /tmp, repository unchanged. Full canonical suite not run; verification was limited to the proposed behavior and EvidenceProbeTests.",
      "needs": "Lead applies the adjudicated replacement and owns final verification."
    }
  ]
}
```

## Findings

**R1 — blocker: the literal contract is not achievable entirely inside this function.**

A genuinely unwritable `night` directory prevents creating `courier.lock`; that exception escapes before `Popen`. The scratch check reproduced this with directory permissions, without mocking the lock. Consequently, **no courier launches or reports anything in that case**. [scripts/run_night.py:1232](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:1232), [scripts/run_night.py:1294](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:1294), [/tmp/d0b83820-consult-check.py:68](/tmp/d0b83820-consult-check.py:68).

**NEEDS_RULING:** accept “this helper never suppresses delivery through an `Exception`, subject to the caller’s storage prerequisites,” or require delivery despite globally unwritable storage? Recommend the former for this repair; the latter requires a separate caller-level design. Independent code and test advice is complete below; unconditional acceptance of the requested unwritable-directory launch test remains blocked.

**R2 — should_fix: Q1 replacement.**

Replace the whole function with the following. Parsing failures map to `None`; missing files supply empty input. Other **read failures return a diagnostic without deleting an unreadable, potentially valid outcome**. One outer exception boundary includes admission checks, imports, cleanup, repair, and refusal creation; the guarded diagnostic formatter prevents an exception’s broken `__str__` from escaping. [Current defect: scripts/run_night.py:1245](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:1245), [verified proposal: /tmp/d0b83820-consult-replacement.py:1](/tmp/d0b83820-consult-replacement.py:1).

```python
def _evidence_cleanup_error(plan, night_dir):
    """Best-effort evidence repair; never suppress delivery via Exception."""
    try:
        def parse_outcome(raw):
            try:
                return json.loads(raw)
            except Exception:
                return None

        if not (night_dir / "chain.started").exists():
            return None
        receipt = json.loads((night_dir / "receipt.json").read_bytes())
        if receipt.get("plan_id") != plan.plan_id or night_gate.validate_receipt(receipt):
            return None
        c5 = next((row for row in receipt["conditions"]
                   if row["condition_id"] == "C5"), {})
        if (c5.get("status") != "PASS"
                or c5.get("measured", {}).get("payload_kind") != "quiet_predicate_evidence"):
            return None

        from joulewise.quiet_predicate_campaign import cleanup_record, write_refusal
        cleanup = cleanup_record(night_dir)
        cleanup_proven = cleanup["cleanup_proven"] is True
        path = night_dir / "evidence_outcome.json"
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            raw = b""
        outcome = parse_outcome(raw)
        state = outcome.get("outcome") if isinstance(outcome, dict) else None
        detail = "chain ended without evidence outcome"
        if not (isinstance(state, str) and state in {"complete", "partial", "refused"}):
            path.unlink(missing_ok=True)
            _write_json(path, {"outcome": "refused", "error": detail,
                               "cleanup_proven": cleanup_proven})
            state = "refused"
        elif state == "refused":
            recorded_error = outcome.get("error")
            if isinstance(recorded_error, str) and recorded_error:
                detail = recorded_error
        if state == "refused" and not _refusal_paths(night_dir):
            write_refusal(night_dir, plan, detail)
        if not cleanup_proven:
            return "evidence collector/recorder/sampler cleanup unproven; report the cleanup record"
        return None
    except Exception as exc:
        try:
            return f"evidence outcome/cleanup unavailable: {type(exc).__name__}: {exc}"
        except Exception:
            return "evidence outcome/cleanup unavailable; diagnostic formatting failed"
```

The refusal check also covers an existing valid `refused` outcome lacking a refusal document, while preserving that outcome’s bytes. Existing `complete` and `partial` outcomes acquire no refusal. Creation uses the existing schema-validating writer; existing refusal paths suppress duplication. [/tmp/d0b83820-consult-replacement.py:32](/tmp/d0b83820-consult-replacement.py:32), [joulewise/quiet_predicate_campaign.py:211](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/joulewise/quiet_predicate_campaign.py:211), [scripts/run_night.py:316](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:316).

**Q2 — regression names and intent.**

For each malformed-content case, use `EvidenceProbeTests.deliver()` and assert the **entire replacement mapping**, a boolean `cleanup_proven`, exactly one refusal, and `validate_refusal(...) == []`. Exercise both cleanup booleans; the existing delivery helper asserts one launch. [tests/test_run_night.py:4786](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/tests/test_run_night.py:4786), [tests/test_run_night.py:4876](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/tests/test_run_night.py:4876), [/tmp/d0b83820-consult-check.py:27](/tmp/d0b83820-consult-check.py:27).

| Proposed test | One-line intent |
|---|---|
| `test_missing_evidence_outcome_is_repaired` | Absent file produces the refused mapping and schema-valid refusal; courier launches. |
| `test_invalid_json_evidence_outcome_is_repaired` | Test both `b"{not-json"` and `b"\xff"`; decode failures reach repair. |
| `test_list_evidence_outcome_is_repaired` | JSON `[]` reaches repair. |
| `test_missing_outcome_state_is_repaired` | `{}` reaches repair. |
| `test_list_outcome_state_is_repaired` | `{"outcome":[]}` reaches repair without unhashable-membership failure. |
| `test_numeric_outcome_state_is_repaired` | `{"outcome":5}` reaches repair. |
| `test_unknown_outcome_state_is_repaired` | `{"outcome":"weird"}` reaches repair. |
| `test_complete_outcome_is_untouched` | Preserve bytes across repeated delivery; create no refusal. |
| `test_refused_outcome_and_existing_refusal_are_untouched` | Preserve both files and refusal-path count across repeated delivery. |
| `test_cleanup_import_error_never_suppresses_the_courier` | Keep the existing injected `ImportError` launch/log assertion. |
| `test_unwritable_night_directory_returns_diagnostic` | Real permission denial returns a diagnostic; the additional launch assertion is blocked by R1. |

The existing `ImportError` regression is at [tests/test_run_night.py:4829](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/tests/test_run_night.py:4829); valid-state preservation and real permission behavior were exercised at [/tmp/d0b83820-consult-check.py:42](/tmp/d0b83820-consult-check.py:42) and [:68](/tmp/d0b83820-consult-check.py:68).

Also add `test_partial_outcome_is_untouched`, `test_repair_permission_error_does_not_suppress_courier`, `test_unreadable_valid_outcome_is_preserved`, and `test_exception_formatting_failure_is_contained`; retain explicit `KeyboardInterrupt`/`SystemExit` propagation checks. These distinguish denied repair writes from a globally unusable courier directory and cover the exception boundary itself. [/tmp/d0b83820-consult-check.py:42](/tmp/d0b83820-consult-check.py:42), [:62](/tmp/d0b83820-consult-check.py:62), [:79](/tmp/d0b83820-consult-check.py:79), [:91](/tmp/d0b83820-consult-check.py:91), [:99](/tmp/d0b83820-consult-check.py:99).

**Q3 — two-sentence recommendation.**

Moving repair into `execute.finally` centralizes producer ownership, but misses failures before `execute`, failures before its `try`, and interruptions within finalization; those paths exist in the current structure. [joulewise/quiet_predicate_campaign.py:451](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/joulewise/quiet_predicate_campaign.py:451), [:511](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/joulewise/quiet_predicate_campaign.py:511), [:537](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/joulewise/quiet_predicate_campaign.py:537).  
**Keep the driver fallback**, with the executor remaining the primary outcome writer and the courier process reading the resulting artifacts. [joulewise/quiet_predicate_campaign.py:521](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/joulewise/quiet_predicate_campaign.py:521), [scripts/run_night.py:1288](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:1288), [:1143](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:1143).

## Residual risk

Refusal creation remains impossible when an earlier import, cleanup operation, outcome read/unlink/create, or refusal discovery/write raises. Examples include permissions/ACLs, read-only storage, missing parent directories, exhausted storage, and I/O failure; unlink-then-create can leave the outcome absent or partially written if creation fails. These return diagnostics, not fabricated cleanup proof. [/tmp/d0b83820-consult-replacement.py:21](/tmp/d0b83820-consult-replacement.py:21), [scripts/run_night.py:165](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:165).

`_refusal_paths` checks filenames, not document validity: a pre-existing corrupt refusal can suppress creation of a valid one. Thus the requested “unless one already exists” shortcut assumes existing refusal documents are valid. [scripts/run_night.py:280](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:280).

When courier storage remains usable, the diagnostic is appended to `night.log`; the courier is instructed to report missing evidence as a limitation. The exact diagnostic is **not guaranteed to appear in its email**, and successful delivery returns `last_error=None`. [scripts/run_night.py:1288](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:1288), [:1368](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:1368), [docs/process/NIGHT_COURIER_PROMPT.md:46](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/docs/process/NIGHT_COURIER_PROMPT.md:46).