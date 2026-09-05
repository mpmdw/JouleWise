```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented immutable validated-byte snapshots and mutation regressions; actual judge transport and registry ratification remain blocked on a magistrate ruling and Ed approval.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/00-design.md",
    "docs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/01-sol-report.md",
    "scripts/validate_gate_packet.py",
    "tests/test_validate_gate_packet.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_validate_gate_packet",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AttributeError: 'NoneType' object has no attribute '__dict__'. Did you mean: '__dir__'?"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 31 tests.*OK"
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
          "Ran 31 tests in 3.451s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 31 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The cited consult requires the follow-on runner to choose its actual judge transport before byte-to-request binding is specified, but no later authority chooses that transport.",
      "needs": "Magistrate chooses the transport contract and names the first concrete judge launcher; option A in 00-design.md is recommended."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The cold-gate charter registry still promises exact sealed-byte delivery and is Ed-ratified; this session was expressly forbidden to edit it.",
      "needs": "Cold-gate ruling followed by Ed ratification of the proposed registry text in 00-design.md."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "No actual judge request was constructed or delivered, so judge-received payload equality and judge-identity binding are not yet verified.",
      "needs": "After F1 and F2, implement the ruled runner receipt and launcher adapter, run defect-shaped fake-transport tests, then perform the lead-owned clean-environment live gate."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The standing operational constraint remains: validator PASS is not launch authorization and must not convene a cold judge.",
      "needs": "Keep the fence until the complete runner and concrete transport pass review and live verification."
    }
  ]
}
```

## Change

The validator now exposes one transport-neutral programmatic operation that
captures packet, charter, and exhibit content as immutable in-process byte
snapshots, calculates receipt digests from those same bytes, and releases the
snapshot only with a PASS receipt. The existing validator command and receipt
format are unchanged: they still describe validation-time observation and do
not claim judge handoff.

The focused tests are counterfactual-shaped. Removing the snapshot operation
removes the API they call; rereading any input pathname after capture makes the
path-replacement or same-inode mutation assertion fail. A validation refusal is
also proved never to release a snapshot.

The design artifact records the forcing race, three transport options, the
recommended canonical-request approach, a worked byte example, and the exact
registry amendment proposed for later cold-gate and Ed ratification.

| Finding or decision | Disposition | Evidence |
|---|---|---|
| Packet and charter bytes need one-time custody | Implemented as immutable snapshots hashed and returned from the same validation operation | `scripts/validate_gate_packet.py`; focused path-replacement test |
| An open exhibit descriptor does not seal its inode | Implemented by reading the exhibit into immutable bytes before PASS | Focused second-descriptor overwrite test |
| Refused validation must not expose handoff material | Implemented: every refusal returns `snapshot=None` | Focused tampered-exhibit test |
| Actual byte-to-request mapping | NEEDS_RULING; recommend canonical UTF-8 JSON with base64 source bytes on standard input and a transport-observed request digest | `00-design.md`, options and recommendation |
| Judge request or session identity binding | Blocked with the transport choice; belongs in a separate runner receipt, never validator receipt version 2 | `00-design.md`, recommendation and worked example |
| Ed-ratified registry wording | Not edited; proposed replacement text is preserved for ratification | `00-design.md`, pending ratification section |
| Kernel, task queue, run state, and decision log | Not edited as instructed | Magistrate must update status only after adjudicating this partial implementation |

## Verification notes

The first focused run failed before collecting tests because Python's dataclass
decorator is incompatible with the test module's existing unregistered dynamic
import. Replacing the records with immutable named tuples fixed that harness
compatibility issue. The repeated focused module then passed all tests. The
repository-wide suite was not run, exactly as required by the preflight rule.

## Residual risk

NEEDS_RULING checklist:

1. Choose the transport contract and the first concrete launcher. Recommendation:
   option A in `00-design.md`; do not infer a launcher from current operator
   practice.
2. Route the proposed charter-registry amendment through a cold gate and Ed
   ratification.
3. In a resumed implementation, construct the request only from
   `ValidatedGateSnapshot`; record the canonical request digest and the returned
   judge request or session identity in a new runner receipt.
4. Add defect-shaped tests for request capture after pathname replacement,
   same-inode overwrite, missing or unequal transport acknowledgement, missing
   identity, and exact decoded source-digest equality.
5. Have the lead perform the clean-environment live launch and final diff gate.
6. Only after those checks, update `docs/process/state_kernel.json`,
   `TASK_QUEUE.md`, and `RUN_STATE.md` and remove the standing operational fence.
