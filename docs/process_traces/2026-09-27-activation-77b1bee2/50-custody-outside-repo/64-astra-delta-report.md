```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "C1–C3 are implemented as dictated; adversarial probes and three mutation cuts found no new defect.",
  "workspace": {
    "base_requested": "f783a3fd",
    "base_mode": "exact",
    "head_start": "f783a3fd348df984e3278e25842dc396059443a4",
    "head_end": "f783a3fd348df984e3278e25842dc396059443a4",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "reviewed_delta": "c84b1dc2..f783a3fd",
    "findings": [],
    "same_signature": "No recurrence of Sol F1 path-shape ambiguity."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-delta-77b1bee2 /opt/homebrew/bin/python3 -m unittest tests.test_issuer_corpus_root tests.test_reissue_calibration_acceptance tests.test_calibration_bracketing > /tmp/corpus-delta-77b1bee2/focused.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 114 tests in 20.918s", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-delta-77b1bee2 /opt/homebrew/bin/python3 /tmp/corpus-delta-77b1bee2/audit.py > /tmp/corpus-delta-77b1bee2/audit.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "legacy helper byte-identical to 670756f3: PASS",
          "naming and verify-members: 10/10 malformed cases refused each",
          "nested P/s/s: naming and verifier accept P/s; refuse P",
          "duplicate pre-pass: valid+3 non-valid retries accepted; valid duplicate refused before reads",
          "same-ledger flag equivalence and no-flag c84b1dc2 byte-equivalence: PASS",
          "real path projection: 24/24 accepted; 3 wrong roots each refused 24/24",
          "real disposition projection: {'ordinary-invalid': 12, 'valid': 12}; valid duplicate attempt_ids=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "valid duplicate attempt_ids=0"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-delta-77b1bee2 /opt/homebrew/bin/python3 /tmp/corpus-delta-77b1bee2/cuts.py > /tmp/corpus-delta-77b1bee2/cuts.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["three named cuts killed: PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "three named cuts killed: PASS"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-delta-77b1bee2 /opt/homebrew/bin/python3 -m unittest tests.test_issue_calibration_acceptance_generation > /tmp/corpus-delta-77b1bee2/issuer.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: None is not an instance of <class 'str'>",
          "Ran 156 tests in 303.030s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "/usr/sbin/sysctl -n kern.osversion",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["sysctl: sysctl fmt -1 1024 1: Operation not permitted"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".+"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check c84b1dc2 f783a3fd",
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
      "id": "G1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The issuer suite's sole failure is test_live_probes_report_this_machine_against_the_active_epoch at tests/test_issue_calibration_acceptance_generation.py:352. Sandboxed sysctl is denied, matching the prior Sol lens's environmental failure.",
      "needs": "Lead reruns the live-probe test where sysctl is permitted."
    }
  ]
}
```

## Findings

None at **BLOCKER**, **SHOULD-FIX**, or **NIT** severity.

| Closure | Verified implementation and evidence |
|---|---|
| C1 | `scripts/issue_calibration_acceptance_generation.py:950` and `:2393` enforce exactly four parts, literal middle components, and bound session/attempt IDs. Both functions accept nested `P/s/s/...` under `P/s` and refuse `P`. Both refuse all ten adversarial cases: 3-/5-part, wrong-middle, case variants, trailing slash, Unicode lookalikes, and empty segment. |
| C2 | `tests/test_issuer_corpus_root.py:123` exercises Revision 5 with ledger/pin/verdicts/git confined to the run checkout. `:156` checks same-ledger flag equivalence, including member order, input digest, cutoff, and only the permitted differences. |
| C3(a) | Issuer `:1275` skips non-valid rows before checking duplicate IDs. Synthetic ordinary-invalid, systematic-invalid, and abandoned retries do not trigger refusal; duplicate valid rows refuse before evidence reads. |
| C3(b) | Issuer `:2441` refuses duplicate member IDs and source directories; tests at `:437` cover both independently. |
| C3(c–e) | Tests `:390` cover missing-primary and prior-session mismatch; `:28` uses `TemporaryDirectory`; issuer `:2540` correctly describes the two roots. |

The delta touches only the issuer and focused tests. `_repo_relative_custody` is byte-identical to `670756f3`; no-flag synthetic output is byte-identical to `c84b1dc2`. Guard F2 holds.

The real ledger’s **top-level observation projection contains 12 valid and 12 ordinary-invalid rows, with zero duplicate attempt IDs among valid rows**. Nested control-record copies are excluded. All 24 custody locators accept the intended root and refuse each prescribed wrong root.

The tests are defect-shaped. Three executed cuts went RED:

- Relax both path-shape guards: both targeted tests fail.
- Route battery authentication to the corpus root: Revision-5 success assertion fails.
- Remove duplicate refusals: both duplicate tests fail.

**Rule 11:** no finding repeats Sol F1’s path-shape ambiguity; that defect is closed.

## Residual risk

The larger issuer suite passed 155/156 tests; its sole failure is the sandboxed live probe described in G1. Full discovery and real issuance were not run. Real custody inspection remained outcome-blind: permitted projections and filesystem metadata only; no W1/W2 measured values were decoded.

DELTA: PASS