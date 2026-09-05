```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: the delta captures immutable validated snapshots but does not implement or test the ruled snapshot-to-judge transport and runner receipt.",
  "workspace": {
    "base_requested": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "41a18902055a8cbc1a9a7cc724c41d2983ddc85a",
    "head_end": "41a18902055a8cbc1a9a7cc724c41d2983ddc85a",
    "upstream_end": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "branch": "feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "G1",
        "severity": "blocker",
        "location": "scripts/validate_gate_packet.py:392",
        "text": "The mission delta stops at capture_and_validate and never implements the magistrate-adopted canonical JSON/base64 request, exactly-once stdin delivery, transport-observed request-digest comparison, judge request/session identity, or runner receipt. The only production CLI still calls validate(), discards the snapshot, and emits the validation-only v2 receipt. This leaves acceptance item 3 wholly absent and items 1-2 unconnected to judge invocation.",
        "counterfactual": "For a valid packet whose packet, charter, and exhibit paths are replaced or whose exhibit inode is overwritten after validation, no in-delta runner exists that can deliver the retained bytes or refuse before judge invocation; therefore no judge-bound outcome can be observed at all. A transport that rereads the changed paths remains neither prevented nor detected by this landing."
      },
      {
        "id": "G2",
        "severity": "blocker",
        "location": "tests/test_validate_gate_packet.py:167",
        "text": "The three new tests inspect the returned snapshot directly; none constructs a judge request, invokes a fake transport, captures transported bytes, checks a transport-observed digest, or verifies a bound identity/runner receipt. Thus the path-replacement and same-inode tests are not the ruled delivery counterfactual and cannot discharge any of the three mission acceptance statements.",
        "counterfactual": "A future/broken runner that ignores ValidatedGateSnapshot and rereads all three mutated paths would still leave these tests green because they never call that runner. Exact reversion in a temporary copy makes the tests error only because capture_and_validate no longer exists, proving API presence rather than snapshot-to-judge binding."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --name-status $(git merge-base origin/main HEAD)..HEAD && git diff --quiet b0ed6991c11f3a515ad293760c6dfc031adda8e1..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "A\tdocs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/00-design.md",
          "A\tdocs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/01-sol-report.md",
          "M\tscripts/validate_gate_packet.py",
          "M\ttests/test_validate_gate_packet.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "00-design\\.md[\\s\\S]*01-sol-report\\.md[\\s\\S]*scripts/validate_gate_packet\\.py[\\s\\S]*tests/test_validate_gate_packet\\.py"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_validate_gate_packet",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 31 tests in 2.604s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 31 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "cf_tmp=$(mktemp -d /tmp/coldgate-refuter-replay.XXXXXX) && mkdir -p \"$cf_tmp/scripts\" \"$cf_tmp/tests\" && cp tests/test_validate_gate_packet.py \"$cf_tmp/tests/test_validate_gate_packet.py\" && touch \"$cf_tmp/tests/__init__.py\" && git archive b0ed6991c11f3a515ad293760c6dfc031adda8e1 scripts/validate_gate_packet.py | tar -x -C \"$cf_tmp\" && (cd \"$cf_tmp\" && ! python3 -m unittest tests.test_validate_gate_packet.ValidateGatePacketTests.test_snapshot_survives_post_validation_path_replacement tests.test_validate_gate_packet.ValidateGatePacketTests.test_snapshot_survives_same_inode_mutation_through_second_descriptor tests.test_validate_gate_packet.ValidateGatePacketTests.test_refusal_never_releases_a_snapshot)",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.005s",
          "FAILED (errors=3)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "has no attribute 'capture_and_validate'[\\s\\S]*Ran 3 tests in [0-9.]+s[\\s\\S]*FAILED \\(errors=3\\)"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "rg -n 'base64|runner receipt|request_digest|request_sha256|judge_(request|session|identity)|stdin|subprocess' scripts/validate_gate_packet.py tests/test_validate_gate_packet.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tests/test_validate_gate_packet.py:117:        return subprocess.run(",
          "tests/test_validate_gate_packet.py:121:            stdout=subprocess.PIPE,",
          "tests/test_validate_gate_packet.py:122:            stderr=subprocess.PIPE,",
          "tests/test_validate_gate_packet.py:128:        completed: subprocess.CompletedProcess[bytes],"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_validate_gate_packet\\.py:.*subprocess"
      }
    }
  ],
  "flags": []
}
```

## Findings

### G1 — blocker: the ruled runner handoff is absent

The mission authority requires the convening runner to deliver exactly the
validated bytes and bind both the request digest and judge request/session
identity. The refreshed magistrate ruling adopts Option A: canonical JSON,
base64 source bytes, one stdin delivery, and a transport-observed request
digest. The delta adds only an immutable `ValidatedGateSnapshot`; repository
search finds no consumer other than the new tests. The existing CLI deliberately
discards the snapshot and retains `judge_handoff_bound: false`.

### G2 — blocker: the new tests stop before the behavioral boundary

The path-replacement test checks that the Python `bytes` fields remain equal
after filesystem replacement. The same-inode test checks the same property for
one exhibit. The refusal test checks `snapshot is None`. None observes judge
invocation or request bytes, so a runner that rereads the mutated paths would
not fail these tests. This is snapshot-unit coverage, not the required
snapshot-to-judge counterfactual.

## Evidence

The mission-only range contains exactly the four paths declared by the seat's
scope of record: `00-design.md`, `01-sol-report.md`, the validator, and its test
module. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and
`docs/decision_log.md` have no delta.

The only touched/importing test module passed: 31 tests, `OK`. No whole-suite
run was performed. Exact reversion of the validator to the merge base in a
temporary copy produced three expected errors from the three new tests:

| New behavior | Counterfactual input | Reverted-copy result |
|---|---|---|
| Immutable packet/charter/exhibit snapshot | Valid inputs, then atomically replace all three paths | Errors: `capture_and_validate` absent |
| Same-inode exhibit retention | Valid inputs, then overwrite the exhibit through a second descriptor | Errors: `capture_and_validate` absent |
| Fail-closed snapshot release | Manifest-valid packet with exhibit bytes tampered before capture | Errors: `capture_and_validate` absent |

That establishes that the new tests depend on the snapshot API. It does not
establish the missing judge-delivery behavior described in G1-G2.

No earlier refuter verdict is present in this mission directory, so there is no
persisted previous-round non-staleness blocker to re-test. The historical
validator CLI/privacy/fence regressions included in the focused 31-test module
remain green.

## Residual risk

The standing operational fence remains necessary: validator PASS must not
convene a cold judge until the ruled runner, transport acknowledgement checks,
runner receipt, and discriminating fake-transport tests exist and pass.
