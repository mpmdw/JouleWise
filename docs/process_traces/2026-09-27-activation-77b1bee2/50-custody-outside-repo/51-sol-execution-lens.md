```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The repair passes the real-locator and synthetic custody checks, but the adopted rule permits two corpus roots for a crafted capture path.",
  "workspace": {
    "base_requested": "b69c39eb26c8b9234f957d32efe0741207b4d399",
    "base_mode": "exact",
    "head_start": "c84b1dc2fbb52f2296e9cce0b52afe9be5de5d5b",
    "head_end": "c84b1dc2fbb52f2296e9cce0b52afe9be5de5d5b",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "scripts/issue_calibration_acceptance_generation.py:949",
        "text": "The first-part and last-part checks permit the same canonical capture under two different corpus roots when the session directory name repeats. This follows the literal site 1 rule but contradicts design C's claim that the ledger path fixes exactly one parent."
      },
      {
        "id": "F2",
        "severity": "nit",
        "file": "tests/test_issuer_corpus_root.py:179",
        "text": "The verifier tests omit deletion of a primary file and a mismatched prior-row session. Independent synthetic probes confirmed both refuse."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-lens-sol-77b1bee2 /opt/homebrew/bin/python3 -c 'from pathlib import Path; import unittest; import tests.test_issuer_corpus_root as t; t.SCRATCH=Path(\"/tmp/corpus-lens-sol-77b1bee2\"); result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(t)); raise SystemExit(0 if result.wasSuccessful() else 1)'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 8 tests in 9.702s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 8 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-lens-sol-77b1bee2 /opt/homebrew/bin/python3 /tmp/corpus-lens-sol-77b1bee2/base_red.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["base RED: tests=1 errors= 1 failures= 0", "base RED reason: --corpus-root absent from parser = True"]},
      "expected": {"exit_code": 0, "tail_regex": "base RED reason: --corpus-root absent from parser = True"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-lens-sol-77b1bee2 /opt/homebrew/bin/python3 /tmp/corpus-lens-sol-77b1bee2/adversarial.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["naming: baseline PASS; refusals 11 relative,parent,double_separator,trailing_separator,outside_root,root_too_high,root_too_low,wrong_session,wrong_capture,missing_capture,directory_symlink", "verify: baseline PASS; refusals 14 absolute,parent,double_separator,trailing_separator,wrong_session,wrong_capture,wrong_digest,wrong_value,prior_wrong_session,prior_missing,wrong_root,missing_primary,symlink_primary,symlink_directory"]},
      "expected": {"exit_code": 0, "tail_regex": "verify: baseline PASS; refusals 14"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-lens-sol-77b1bee2 /opt/homebrew/bin/python3 /tmp/corpus-lens-sol-77b1bee2/r8_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["projected unique triples=24; accepted=24; too_high=24/24 refused; too_low=24/24 refused; checkout=24/24 refused"]},
      "expected": {"exit_code": 0, "tail_regex": "accepted=24; too_high=24/24 refused"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-lens-sol-77b1bee2 /opt/homebrew/bin/python3 /tmp/corpus-lens-sol-77b1bee2/root_ambiguity.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["same canonical capture accepted under two roots: ['same-session/same-session/runs/instrument_validation/same-session-d01', 'same-session/runs/instrument_validation/same-session-d01']"]},
      "expected": {"exit_code": 0, "tail_regex": "same canonical capture accepted under two roots"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-lens-sol-77b1bee2 /opt/homebrew/bin/python3 /tmp/corpus-lens-sol-77b1bee2/flag_invariance.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["synthetic flag comparison PASS: 20 member IDs/order/values, derivation_input_sha256, and normalized artifact fields identical"]},
      "expected": {"exit_code": 0, "tail_regex": "synthetic flag comparison PASS"}
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-lens-sol-77b1bee2 /opt/homebrew/bin/python3 -m unittest tests.test_reissue_calibration_acceptance tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 99 tests in 0.797s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 99 tests.*OK \\(skipped=1\\)"}
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-lens-sol-77b1bee2 /opt/homebrew/bin/python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: None is not an instance of <class 'str'>", "Ran 156 tests in 371.378s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 156 tests.*OK"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Design C's literal site 1 accepts a crafted path under two roots, while the synthesis says exactly one root can work.",
      "needs": "Rule whether to require the fixed <session>/runs/instrument_validation/<capture> shape or limit the uniqueness claim to the 24 recorded locators."
    },
    {
      "id": "G2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The issuer suite's sole failure is its live OS probe: sandboxed /usr/sbin/sysctl -n kern.osversion returns Operation not permitted.",
      "needs": "Rerun that live-probe test where sysctl is permitted."
    }
  ]
}
```

## Findings

- **F1 — BLOCKER.** [The naming function](/Users/edr/code/JouleWise-wt-corpus-lens-77b1bee2/scripts/issue_calibration_acceptance_generation.py:949) accepts a synthetic capture at `P/s/s/runs/instrument_validation/s-d01` with either `P` or `P/s` as the root, producing different stored paths. This is allowed by Fable site 1’s literal checks, so it needs a lead ruling rather than an unreviewed code change. All 24 real locators have the fixed four-part shape; each accepted the intended root and refused the three wrong roots tested.

- **F2 — NIT.** [The verifier tests](/Users/edr/code/JouleWise-wt-corpus-lens-77b1bee2/tests/test_issuer_corpus_root.py:179) lack missing-primary and prior-row-session refusal cases. Both passed independent synthetic refusal probes.

The diff otherwise follows sites 1–7 and rulings 1–4 in effect: only three scoped files changed; the old naming function is byte-identical; no-flag legacy path tests pass; path guards run before member evidence parsing; and the flag does not redirect ledger, pin, battery, or git inputs. A synthetic comparison found identical member IDs and order, `derivation_input_sha256`, and all artifact fields after removing the intended path, note, and whole-file hash differences. The new end-to-end test went RED on the base issuer. The verifier implements its authentication directly rather than calling the existing reissue helper, to apply the ruled path and no-follow checks.

## Residual risk

No W1/W2 measured value was opened or parsed; the real-ledger probe projected only locator and ID strings. No real issuance or full discovery suite was run. The issuer suite passed 155 of 156 tests; its live OS probe needs a run where `sysctl` is permitted.

LENS: FAIL