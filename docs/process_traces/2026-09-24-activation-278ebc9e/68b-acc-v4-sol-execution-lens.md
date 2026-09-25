```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Counterfactuals and 47 focused tests pass; one protocol-pin exception is broader than the ruled r8 reissue.",
  "workspace": {
    "base_requested": "bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1",
    "base_mode": "descendant",
    "head_start": "53e6d23d91068e4c51b38f39a4ad391d1a268c28",
    "head_end": "53e6d23d91068e4c51b38f39a4ad391d1a268c28",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "location": "joulewise/calibration_bracketing.py:289",
        "issue": "The pin predicate admits a v4 protocol digest for every v3 identity, although ruling 1(c) authorizes that pairing for the r8 reissue.",
        "witness": "_registered_protocol_pin_matches({'pulse_protocol_id': PROTOCOL_V3_ID}, protocol_sha256(PROTOCOL_ID)) returned True.",
        "cure": "Pass the acceptance identity into the predicate and confine the v3-identity/v4-pin exception to r8; retain the v3 pin rule for other historical generations."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/278ebc9e/v4lens-execution PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -q tests.test_acc_25g83_v4_rev4 tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests tests.test_calibration_bracketing.RevisionFourEnvelopeValidatorTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 47 tests in 9.562s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 47 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONPATH=/Users/edr/code/wt-278ebc9e-v4lens-sol TMPDIR=/tmp/278ebc9e/v4lens-execution PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/278ebc9e/v4lens-execution/probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "v4-n11 rc 3: below the required floor 12; v4-n12 rc 0, zero_headroom; v4-n19 rc 0, corpus_n 19",
          "v4-B08x2 rc 0, excursion_limited; v4-B026 rc 3: exceeds one native sample interval (0.25 s)",
          "v3-n11/v3-n12 rc 3: floor 19; v3-n19 rc 0, corpus_n 19",
          "v4 1.79 s and 2.21 s, v3 1.0 s under v4, and v4 2.0 s under v3: duration refusal",
          "0.8 s native frame: a243_trigger_flag True"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "a243_trigger_flag.*True"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "for mutation in weaken_n drop_epoch_scope drop_excursion_refusal; do PYTHONPATH=/Users/edr/code/wt-278ebc9e-v4lens-sol TMPDIR=/tmp/278ebc9e/v4lens-execution PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/278ebc9e/v4lens-execution/mutate.py \"$mutation\" > \"/tmp/278ebc9e/v4lens-execution/mutant-$mutation.log\" 2>&1; rc=$?; echo \"$mutation rc=$rc\"; tail -n 9 \"/tmp/278ebc9e/v4lens-execution/mutant-$mutation.log\"; done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "weaken_n rc=1: test_n12_zero_headroom_issues_and_n11_refuses failed",
          "drop_epoch_scope rc=1: test_twelve_does_not_issue_under_historical_v3_epoch failed",
          "drop_excursion_refusal rc=1: test_excursion_label_and_over_interval_refusal failed"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "drop_excursion_refusal rc=1"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nfrom joulewise.calibration_bracketing import _registered_protocol_pin_matches\nfrom joulewise.powermetrics_fiducial import PROTOCOL_V3_ID, PROTOCOL_ID, protocol_sha256\nv4=protocol_sha256(PROTOCOL_ID)\nprint('arbitrary_v3_identity_accepts_v4_pin',_registered_protocol_pin_matches({'pulse_protocol_id':PROTOCOL_V3_ID},v4))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["arbitrary_v3_identity_accepts_v4_pin True"]
      },
      "expected": {"exit_code": 0, "tail_regex": "arbitrary_v3_identity_accepts_v4_pin True"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "A broader test invocation was interrupted during a slow reducer test. The 47 focused tests and executed counterfactuals completed; this seat did not independently classify all broad-suite failures.",
      "needs": "Lead's full-tier run and r8 pin reissue."
    }
  ]
}
```

## Findings

| ID | Severity | Executed witness | Cure |
|---|---|---|---|
| F1 | should_fix | The [pin predicate](/Users/edr/code/wt-278ebc9e-v4lens-sol/joulewise/calibration_bracketing.py:289) returned `True` for an arbitrary v3 identity paired with the v4 digest. This demonstrates a broadened check, **not** that a forged historical artifact passes full validation. | Limit the exception to the ruled r8 acceptance identity. |

## Accepted clauses

- **1(a):** v4 geometry rejects 1.79 s and 2.21 s pulses and rejects cross-protocol 1.0 s/v3 and 2.0 s/v4 captures.
- **2(c), 2(i):** v4 refuses n = 11 and issues n = 12 and 19; the tight n = 12 corpus records `zero_headroom`. Historical v3 retains its 19-member floor.
- **2(g), 2(h):** Two 0.08 s members issue with `excursion_limited`; a 0.26 s member refuses with the native-sample-interval mechanism named.
- **3(c):** A claim window containing a 0.8 s native frame sets the A243 cadence flag.
- **Mutation checks:** Weakening n, dropping epoch scope, and dropping excursion refusal each killed the named regression test in V3.

## Residual risk

The focused set passed. The broader suite was interrupted, so this seat cannot independently confirm that every remaining broad-suite failure is solely an r7 digest pin. The replay addendum’s 24-capture result was read from the seat report, not rerun here.