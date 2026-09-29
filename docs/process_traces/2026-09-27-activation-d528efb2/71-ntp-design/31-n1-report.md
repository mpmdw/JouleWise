```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the N1 network-time records, per-capture verdict, driver lifecycle, launch refusals, and report modes; driver-suite acceptance remains pending.",
  "workspace": {
    "base_requested": "9eab16f8",
    "base_mode": "descendant",
    "head_start": "921a795318505c53d8e6df272f1eba2be3ab0911",
    "head_end": "921a795318505c53d8e6df272f1eba2be3ab0911",
    "upstream_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "branch": "feat/2026-09-28-ntp-n1"
  },
  "pathspec": [
    "joulewise/network_time_window.py",
    "tests/test_network_time_window.py",
    "scripts/run_night.py",
    "tests/test_run_night.py",
    "joulewise/night_gate.py",
    "tests/test_night_gate.py",
    "joulewise/arm_retry.py",
    "tests/test_arm_retry.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_network_time_window tests.test_night_gate tests.test_arm_retry",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 164 tests in 3.376s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest -v tests.test_run_night > /tmp/jw-n1-run-night-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 241 tests in 205.063s", "FAILED (failures=3, skipped=9)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_run_night.NightDriverTests.test_network_time_route_refuses_real_night_until_consumer_lands tests.test_run_night.NightDriverTests.test_network_time_off_wrong_output_refuses_and_attempts_on tests.test_run_night.NightDriverTests.test_network_time_order_is_off_chain_query_on tests.test_run_night.NightDriverTests.test_dead_man_recovers_before_courier_sent_early_return",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 4 tests in 0.353s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
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
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The full driver module has three 8-second external-watchdog timeouts in BindSupervisionProcessTests: blocked_journal_never_blocks_deadline_or_grants_go, blocking_join_startup_and_post_publication, and startup_hang_is_nonblocking. They exercise the unchanged bind supervisor through subprocess fault fixtures; one reproduced alone.",
      "needs": "Lead reruns or adjudicates these three failures before acceptance."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The old-log case used an injected header-only runner. No real log query or network-time switch was run, as instructed.",
      "needs": "Lead performs the ruling's live bench checks."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The enforced-kind set remains empty. The chain-side idle harvest call is exposed by run_window_query(who='chain') but belongs to N3's consumer change.",
      "needs": "N3 places that call before its in-chain ON and pilot summary, then the lead enables the kind."
    }
  ]
}
```

## Change

- §3: Added write-once H5/H6 records, digest-checked `capture_verdict`, and the closed historic exemptions in `attestation_required`. Missing or invalid evidence refuses a capture.
- §§4–5: The driver now creates a restore marker, records OFF before launching the chain, queries after a proved chain end, records ON, and recovers interrupted restores at driver and dead-man entry. Real nights refuse while `NETWORK_TIME_ENFORCED_KINDS` is empty. The query starts at least 3,600 seconds before OFF; a witness must be a `timed:data` line older than OFF.
- §6.3/§6.5: The independent module parses timestamp offsets and continuation lines, refuses unplaceable lines, and provides `report --h6` and `report --h7`. H6 prints no B.

The new window tests each target a distinct defect: header-only acceptance; witnesses inside a capture, inside its lead, after OFF, or in the `text` category; a shortened or lengthened 180-second lead; a query starting too late or running too early; lost continuation markers; accepted orphan lines; dropped UTC offsets; missed markers in invalid runs or on a bad header’s first line; trusted damaged digests; incorrect OFF output or one-clock-only settling; recovery beside a live chain; failure to requery an invalid run; open-ended historic exemptions; lost failed-ON receipts; blocked fresh OFF after a failed recovery; and H6/H7 output drift.

The four new driver tests cover the empty-kind refusal, wrong OFF output and ON attempt, OFF → chain → query → ON order, and dead-man recovery before its early return. The updated reason-registry and retry tests catch missing registrations and accidental automatic-retry classification.

Two planted defects produced assertion failures as intended: removing `MARKERS` made the 179-second marker test return `clean`; promoting `timed:text` to `timed:data` made the category test return `clean`. Both were in-memory mutations and were removed.

## Verification notes

The full driver module ran: 241 tests, with three subprocess watchdog timeouts and no other failures. The focused N1 tests and the other three in-scope modules pass. No real system log, `sudo`, `systemsetup`, capture, power sampler, or battery read was used.

No `NEEDS_SCOPE` or `NEEDS_RULING` request.