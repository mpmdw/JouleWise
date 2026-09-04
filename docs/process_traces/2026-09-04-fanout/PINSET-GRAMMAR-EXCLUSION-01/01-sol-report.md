```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "The pre-authoring custody exception now admits only direct projection freeze receipts and sidecars with the ruled filename grammar, with a counterfactual regression for nested paths.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-PINSET-GRAMMAR-EXCLUSION-01"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "tests/test_receipt_histsem.py",
    "docs/process_traces/2026-09-04-fanout/PINSET-GRAMMAR-EXCLUSION-01/01-sol-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "git diff --check && python3 -m unittest tests.test_receipt_histsem.PreAuthoringProjectionCustodyTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "........",
          "----------------------------------------------------------------------",
          "Ran 8 tests in 15.134s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests in [0-9.]+s\\n\\nOK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_receipt_histsem",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": [
          "    ready = selector.select(timeout)",
          "  File \"/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/selectors.py\", line 398, in select",
          "    fd_event_list = self._selector.poll(timeout)",
          "KeyboardInterrupt"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'import joulewise.arm_readiness as r; rows=r._load_histsem_pinset(\".\"); refused=[row[\"pack_id\"] for row in rows if r._histsem_tree_has_authoring_custody(r._historical_pack_tree(\".\", row[\"pack_path\"], row[\"head_commit\"])[1])]; assert not refused, refused; print(f\"governed historical trees admitted: {len(rows)}\")'\ngit diff --check && echo 'git diff --check: PASS'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "governed historical trees admitted: 9",
          "git diff --check: PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "governed historical trees admitted: 9\\ngit diff --check: PASS$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The complete focused module was manually interrupted after extended silence in ReceiptHistsemRefreshLaneTests.test_refresh_lane_is_idempotent_and_canonical; all progress before that point showed no failure, but an interrupted run is not a pass.",
      "needs": "Re-run python3 -m unittest tests.test_receipt_histsem with enough time to obtain its final summary."
    }
  ]
}
```

## Change

The pre-authoring custody test checks that a historical Git coordinate predates evidence authoring. It previously exempted every path below `identity_pin_projection.receipts`, although the projection freeze grammar permits only `projection-NNNN.json` and `projection-NNNN.sha256`, with four or more digits, directly below that directory.

The predicate now exempts only those two direct-child forms. A nested path or any other filename makes the historical coordinate ineligible at this gate, so refusal no longer depends on the later identity membrane or the pack-authentication addition fence. The established post-authoring rule remains unchanged: legitimate projection artifacts may still be added below the full custody-directory set.

| Finding | Decision | Evidence |
|---|---|---|
| The custodied PR #182 refuter finding showed that the pre-authoring test treated the projection-receipt directory as an unrestricted exception. | Implement the row's primary cure: constrain the exception to the existing projection freeze grammar. | The nested builder regression now stops with `historical coordinate is not pre-authoring`; removing the new predicate branch makes it advance to the later plan-tree gate and fail the test. |
| The previous positive fixture used `record-0001.json` and its ordinary `.json.sha256` sidecar, neither of which is a lawful projection freeze pair. | Make that fixture model the issued artifact names, `projection-0001.json` and `projection-0001.sha256`. | The grammar table admits the four-digit and longer forms for both extensions and refuses short ordinals, doubled extensions, arbitrary names, and nested paths. |
| The minimal alternative would test only the neighboring refusal layers. | Do not use the minimal alternative because it would preserve the unrestricted exception identified by the authoritative finding. | The shared predicate itself now refuses the counterexample, and all three consumers continue to call it. |

No hardware, user action, dependency, or new design ruling is needed for the code change.

## Verification notes

The repository-wide unit-test suite was not run, as required by the mission preflight rule. The acceptance-specific eight-test class passed. A read-only inspection also evaluated the tightened predicate against every governed historical row loaded from the committed pinset chain; all nine rows remained admissible.

The complete `tests.test_receipt_histsem` module was started as a neighboring compatibility check. It was manually interrupted with exit code 130 while waiting in the refresh lane's second subprocess invocation. This is a verification gap, not an observed assertion failure.

## Residual risk

- Re-run `python3 -m unittest tests.test_receipt_histsem` with enough time to receive a final summary; the interrupted run cannot be credited as green.
- After lead verification, update the forbidden lead-owned state surfaces: mark `PINSET-GRAMMAR-EXCLUSION-01` complete in `docs/process/state_kernel.json`, point its closure evidence to this report, and regenerate the corresponding `TASK_QUEUE.md` and `RUN_STATE.md` projections. No change is needed in `docs/decision_log.md` or `docs/paper/draft-v2-skeleton.md`.
- No `NEEDS_RULING` or `NEEDS_SCOPE` item remains.
