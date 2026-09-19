```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One should-fix: malformed outcomes can still bypass refusal creation. Evidence tests pass; full-module verification has three reproducible watchdog failures.",
  "workspace": {
    "base_requested": "12dcc3f5",
    "base_mode": "descendant",
    "head_start": "17f374f2b4e4f67b5f84cea66adabfe1244474b4",
    "head_end": "17f374f2b4e4f67b5f84cea66adabfe1244474b4",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 1,
      "nit": 0
    },
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "title": "Malformed outcomes escape the garbled-outcome repair",
        "call_site": "scripts/run_night.py:1257 and scripts/run_night.py:1260, _evidence_cleanup_error",
        "counterfactual": "Through EvidenceProbeTests.deliver(), a file containing {not-json remains byte-identical and refusal.json is absent, although the real courier launches. A JSON object with outcome=[] produces the same failure.",
        "cause": "JSONDecodeError occurs before the repair branch; an unhashable outcome raises TypeError during set membership. The outer Exception handler returns a diagnostic without replacing the outcome or writing refusal.json.",
        "recommendation": "Normalize JSON decoding failures to an invalid outcome and type-check the state before membership testing. Add regressions for invalid JSON and non-string outcome values."
      }
    ],
    "requested_checks": {
      "F1": "Exactly two production hunks and two added regressions; only scripts/run_night.py and tests/test_run_night.py differ. Total: 33 insertions, 3 deletions.",
      "F2": {
        "a": "PASS: injected ImportError still launches the courier and appears by type in night.log.",
        "b": "PASS: {} becomes outcome=refused and a schema-valid refusal.json is written.",
        "c": "PASS: complete outcome remains byte-identical; no refusal document.",
        "d": "FAIL: non-JSON bytes remain unchanged; refusal.json absent; courier launches.",
        "additional": "Unknown string state repairs successfully; list-valued state fails like case d."
      },
      "F3": {
        "exceptions": "Injected KeyboardInterrupt and SystemExit propagate through the real run_courier call; Popen is not called. Both derive from BaseException, not Exception. InterruptedError is caught, but the signal handler raising it belongs to the separate executor process (quiet_predicate_campaign.py:463-465); run_night installs no such handler.",
        "ordering": "quiet_predicate_evidence.zsh:16 execs the executor. quiet_predicate_campaign.py:521 writes the outcome before execute returns at :526. run_night.py:956 waits for chain exit before recording it; :3000 completes _run_chain_once before :3079 calls _finish_reporting, which invokes run_courier at :1634. Unproven termination suppresses delivery at :3076. The dead-man checks chain-group liveness at :3138 onward and refuses a live group before its courier call at :3197. Thus the replacement unlink does not race the executor on these production paths."
      },
      "F4": "EvidenceProbeTests: 13 passed. Full module: 199 tests, 3 failures, 9 skipped. The three watchdog failures reproduced in a focused rerun. Git status was clean before and after.",
      "F5": "FINDINGS"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --stat 12dcc3f5 HEAD && git diff 12dcc3f5 HEAD -- scripts/run_night.py tests/test_run_night.py && git diff --name-only 12dcc3f5 HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/run_night.py",
          "tests/test_run_night.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "scripts/run_night\\.py\\ntests/test_run_night\\.py"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/d0b83820-review-probes.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 8 tests in 4.900s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night.EvidenceProbeTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 13 tests in 10.672s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 13 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: external watchdog (8 s): bind supervisor blocked in startup_hang",
          "",
          "----------------------------------------------------------------------",
          "Ran 199 tests in 206.454s",
          "",
          "FAILED (failures=3, skipped=9)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 199 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go tests.test_run_night.BindSupervisionProcessTests.test_blocking_join_startup_and_post_publication tests.test_run_night.BindSupervisionProcessTests.test_startup_hang_is_nonblocking",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 3 tests in 24.029s",
          "",
          "FAILED (failures=3)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git diff --name-only && git ls-files --others --exclude-standard && git diff --check 12dcc3f5 HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "17f374f2b4e4f67b5f84cea66adabfe1244474b4"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)\\n17f374f2b4e4f67b5f84cea66adabfe1244474b4"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Full-module verification is not green: three unchanged BindSupervisionProcessTests hit their 8-second external watchdog, involving journal_block and startup_hang. All three reproduced when rerun alone. Root cause and baseline behavior were not established.",
      "needs": "Lead must resolve or adjudicate these verification failures before treating the module gate as passed."
    }
  ]
}
```

## Findings

**R1 — should_fix:** [The outcome validation](/Users/edr/code/JouleWise-wt-saopus2-d0b83820/scripts/run_night.py:1257) still leaves malformed evidence without a refusal document. Invalid JSON raises before repair; `{"outcome":[]}` raises during set membership. Both deliver successfully but retain the garbled file.

Next step: normalize malformed outcomes into the refusal branch and add both regressions. The reproduction script is [here](/tmp/d0b83820-review-probes.py).

## Residual risk

Courier checks used the real function with fixture-mocked transport and liveness; no live delivery or hardware collection occurred. The [full-module log](/tmp/d0b83820-run-night-tests.log) and [focused rerun log](/tmp/d0b83820-supervision-recheck.log) retain the unresolved watchdog failures. No repository files changed.