```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All 273 focused tests pass, but execution found three blocker acceptance paths in the S0 helper.",
  "workspace": {
    "base_requested": "64e39bb937e79c710886acf13fbfab295526aa18",
    "base_mode": "descendant",
    "head_start": "26ab72342e7200ebf0494f6e627bbb56e14f266c",
    "head_end": "26ab72342e7200ebf0494f6e627bbb56e14f266c",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "title": "Capture pair passes with conflicting attempt and slot identities"},
      {"id": "F2", "severity": "blocker", "title": "Reversed quiet-session span passes"},
      {"id": "F3", "severity": "blocker", "title": "Malformed round journal bypasses a custody mismatch"},
      {"id": "F4", "severity": "should_fix", "title": "Raw symlink outside the container passes"},
      {"id": "F5", "severity": "should_fix", "title": "Wrappers accept duplicate JSON keys"},
      {"id": "F6", "severity": "should_fix", "title": "A kind missing battery_brackets escapes without a check record"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["....", "----------------------------------------------------------------------", "Ran 273 tests in 1077.061s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /private/tmp/bfgs-s0-review-probe-26ab7234.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "fence_calibration: RETURN; check={'payload_kind': 'calibration', 'verdict': 'pass'}; journal_updated=True",
          "fence_qpe: Refused; check={'reason': \"battery_brackets: 'quiet_predicate_evidence' has no pair collector\", 'verdict': 'fail'}; journal_updated=True",
          "fence_unknown: Refused; check={'reason': \"battery_brackets: 'unknown' has no pair collector\", 'verdict': 'fail'}; journal_updated=True",
          "fence_none: Refused; check={'reason': 'battery_brackets: None has no pair collector', 'verdict': 'fail'}; journal_updated=True",
          "fence_missing_attribute: AttributeError; check={'reason': 'battery_brackets: None has no pair collector', 'verdict': 'fail'}; journal_updated=False"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "fence_missing_attribute: AttributeError"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check 64e39bb9 26ab7234",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full repository suite and live hardware gates were outside this focused read-only review.",
      "needs": ""
    }
  ]
}
```

## Findings

- **F1 — BLOCKER.** [authenticate_capture](/Users/edr/code/JouleWise-wt-s0-sol-6bec2aa6/joulewise/battery_float.py:920) returned `pass` when `instrument_evidence.validation_id` was `capture-owner`, while the pre/post records named different foreign attempts and slots. It takes the expected session identity from the pre record itself. **Fix:** require both attempt IDs to equal the evidence validation ID, require the pair’s session and slot identities to agree, and bind those identities to the authenticated ledger owner before accepting a capture.

- **F2 — BLOCKER.** [authenticate_pair](/Users/edr/code/JouleWise-wt-s0-sol-6bec2aa6/joulewise/battery_float.py:760) returned `pass` for `span=(80, 20)`; `authenticate_quiet_session` also passed a session whose start stamp was 80 ns and end stamp 20 ns. **Fix:** validate an ordered, non-negative integer span for every kind before the coverage comparisons; return `battery_float_evidence_missing` for a reversed or malformed span. The gap-fill permits equal bounds.

- **F3 — BLOCKER.** [authenticate_quiet_session](/Users/edr/code/JouleWise-wt-s0-sol-6bec2aa6/joulewise/battery_float.py:865) raised `CustodyFailure` for a mismatched round digest, then returned `pass` when the same `rounds.jsonl` was replaced with malformed JSON. Its parse error becomes an empty row list. **Fix:** refuse an existing but unreadable or malformed round journal; never convert it to zero rows.

- **F4 — SHOULD-FIX.** A `raw/battery_float.pre.ioreg` symlink to a file outside the custody container returned `pass` when its bytes matched the recorded digest. **Fix:** open raw files without following symlinks and require every path component to remain inside the container.

- **F5 — SHOULD-FIX.** Duplicate `session` and `run_id` JSON keys, with a foreign value followed by the expected value, both returned `pass`. **Fix:** reject duplicate object keys while decoding every wrapper input, including JSONL records.

- **F6 — SHOULD-FIX.** Through `evidence_night.check`, calibration recorded a passing bracket check; QPE, unknown, and `None` payloads recorded failures. An injected kind without `battery_brackets` instead raised `AttributeError` and wrote no new check journal. **Fix:** treat a missing attribute as a failed `battery_brackets` inspection, then persist the normal refusal record.

The other requested probes rejected wrong phase, a single-record identity swap, an unmodified pre/post record swap, `../` raw path, uppercase digest, non-integer or boolean monotonic fields used by a span, and NaN or infinite wall time. Missing raw bytes raised `CustodyFailure` ahead of a status. The working tree remains clean.

## Residual risk

Verification covered the S0 focused suites and synthetic fixtures in `/private/tmp`. It did not cover the full repository suite or live hardware.