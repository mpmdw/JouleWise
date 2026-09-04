```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented and focused-tested a dirfd-relative, atomic, fsync-complete validator-receipt publication primitive; the absent convening-runner call site needs a lead ruling.",
  "workspace": {
    "base_requested": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "base_mode": "exact",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-CGV-HARDEN-01"
  },
  "pathspec": [
    "docs/designs/cgv_harden_01.md",
    "docs/process_traces/2026-09-04-fanout/CGV-HARDEN-01/01-sol-report.md",
    "joulewise/coldgate_receipt.py",
    "tests/test_coldgate_receipt.py"
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
      "cmd": "python3 -m unittest tests.test_coldgate_receipt",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 7 tests in 0.013s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 7 tests in .*\\n\\nOK"
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
          "Ran 28 tests in 3.018s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 28 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport json\nfrom pathlib import Path\np=Path('docs/process_traces/2026-09-04-fanout/CGV-HARDEN-01/01-sol-report.md')\ntext=p.read_text(encoding='utf-8')\nassert text.startswith('```json\\n')\npayload, _=text[8:].split('\\n```\\n', 1)\nvalue=json.loads(payload)\nassert value['schema']=='claude-codex-report/v1'\nassert value['genre']=='implementation'\nprint('report envelope: valid')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report envelope: valid"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report envelope: valid$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "No convening cold-gate runner exists at the requested base, so there is no authorized, contract-defined production call site for receipt persistence.",
      "needs": "Choose the future runner file and interface, then require it to pass the validator's exact stdout bytes to persist_validator_receipt and treat every publication exception as non-success."
    }
  ]
}
```

## Change

Added a runner-facing receipt writer that anchors the destination with an open
directory file descriptor (dirfd), performs all later name operations relative
to that descriptor, writes and synchronizes a private file, publishes without
overwrite through an atomic hard link, removes the private name, and
synchronizes the directory. It returns only after confirmed durability. A
directory-sync failure is reported as uncertain because the complete receipt
may already be visible.

The focused design records the forcing race, three options, the recommended
mechanism, and a worked publication example. It keeps receipt durability
separate from `COLDGATE-HANDOFF-01`, which owns delivery of validated bytes to
the judge.

Tests are counterfactual-shaped: removing descriptor anchoring writes into one
of the replacement trees; removing either synchronization call breaks the
observed sequence or failure behavior; direct or overwrite publication breaks
the collision and partial-write assertions.

## Finding and decision table

| ID | Finding or decision | Disposition |
|---|---|---|
| D1 | The validator emits canonical receipt bytes on standard output and must not regain `--receipt-out`. | The new primitive accepts bytes; the validator remains unchanged. |
| D2 | A path check followed by a path write can be redirected when the directory name is replaced. | Hold a real directory open, reject identity change, and use only descriptor-relative create, link, unlink, and sync operations. |
| D3 | Replacement publication would silently clobber a prior receipt. | Publish with an atomic hard link, which fails when the final name exists. |
| F1 | No convening runner exists at this base. | **NEEDS_RULING:** choose the runner file, command interface, receipt directory, and naming rule. Recommendation: integrate this primitive into the runner introduced by the adjacent runner work, without adding judge handoff here. |

## Scoped design

The forcing problem, alternatives, recommendation, and worked example are in
`docs/designs/cgv_harden_01.md`. The safe mechanical boundary is complete. The
runner integration is intentionally not invented: the cited ruling fixes
ownership and separation, but not a runner path, command line, receipt locator,
or naming contract.

## Clause map

| Authority clause | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| State kernel lines 871-872: dirfd-relative, atomic, file-sync and parent-directory-sync publication | `joulewise/coldgate_receipt.py:136` | `test_success_is_byte_exact_atomic_and_fsync_complete` at `tests/test_coldgate_receipt.py:30`; `test_final_name_is_absent_while_receipt_bytes_are_being_written` at `tests/test_coldgate_receipt.py:129` | Replace descriptor-relative staging and link publication with a direct path write; the final name becomes observable during byte writes and the assertion fails. |
| State kernel line 873: distinguish path replacement | `joulewise/coldgate_receipt.py:144` | `tests.test_coldgate_receipt.ValidatorReceiptPublicationTests.test_directory_path_replacement_refuses_without_writing_either_tree` at `tests/test_coldgate_receipt.py:54` | Remove the opened-directory identity check or write through the replaced path; one tree gains a receipt and the assertion fails. |
| State kernel line 873: distinguish durability failure | `joulewise/coldgate_receipt.py:150` and `joulewise/coldgate_receipt.py:172` | `test_file_fsync_failure_leaves_no_published_receipt` at `tests/test_coldgate_receipt.py:96`; `test_directory_fsync_failure_is_reported_as_durability_uncertain` at `tests/test_coldgate_receipt.py:76` | Remove either synchronization call or report directory-sync failure as success; the corresponding test fails. |
| State kernel line 871: the convening runner invokes persistence | **NOT PINNED: no convening runner exists at base HEAD.** | No production-call assertion can exist until the runner interface is ruled. | Add an ad hoc call site under an invented interface; that would cross the unresolved design boundary and could collide with `COLDGATE-HANDOFF-01`. |

## Verification notes

The repository-wide suite was not run, as the preflight rule forbids it. Only
the new receipt module and the existing validator module were exercised.

## Residual risk

**NEEDS_RULING:** Which production runner and locator contract own the call to
`persist_validator_receipt`? Options considered were a new persistence-only
command, a new validator wrapper, or integration into the future convening
runner. Recommendation: integrate into the future convening runner because a
second command would split error handling and a validator wrapper would create
another public interface without authority. Until that ruling is applied, the
kernel row should remain open.

After integration and focused verification, the magistrate should update
`docs/process/state_kernel.json` and regenerate its projections in
`TASK_QUEUE.md` and `RUN_STATE.md`. This session did not edit those lead-owned
files.
