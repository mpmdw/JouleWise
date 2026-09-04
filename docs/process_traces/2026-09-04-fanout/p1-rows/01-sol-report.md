```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Reconciled four stale Phase 1 evidence records, preserved every live-hardware caveat, and recommended replacement of the mixed calendar row.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-p1-rows"
  },
  "pathspec": [
    "docs/phase_1/phase_1_exit_checklist.md",
    "docs/process_traces/2026-09-04-fanout/p1-rows/01-sol-report.md",
    "tests/test_phase1_row_dispositions.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_phase1_row_dispositions tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 27 tests in 1.087s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_phase1_row_dispositions tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 27 tests in 1.204s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
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
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/p1-rows/01-sol-report.md\"); t=p.read_text(encoding=\"utf-8\"); f=t.split(\"\u0060\u0060\u0060\",2); assert f[0] == \"\" and f[1].startswith(\"json\\n\"); b=f[1][5:].encode(\"utf-8\"); assert len(b) <= 8192; json.loads(b); print(\"report-envelope-ok\", len(b))'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "json.decoder.JSONDecodeError: Unterminated string starting at: line 80 column 14 (char 2075)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report-envelope-ok [0-9]+$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/p1-rows/01-sol-report.md\"); lines=p.read_text(encoding=\"utf-8\").splitlines(); fence=chr(96)*3; assert lines[0] == fence+\"json\"; end=lines.index(fence,1); b=(\"\\n\".join(lines[1:end])+\"\\n\").encode(\"utf-8\"); assert len(b) <= 8192; json.loads(b); print(\"report-envelope-ok\", len(b))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report-envelope-ok 4217"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report-envelope-ok [0-9]+$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "P1-008 mixes unresolved academic dates with acceptance and hardware questions that later authorities separated.",
      "needs": "The magistrate should retire P1-008 and open a narrow external-input row for the final-report and colloquium dates; no dates were invented here."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide unit-test suite was not run, as the preflight rule forbids it for this seat.",
      "needs": "Use the focused passing command in V2 for harvest; the magistrate owns any broader verification."
    }
  ]
}
```

## Change

The Phase 1 exit checklist now distinguishes a planning disposition from live
hardware validation. A **blocker record** names the missing external fact that
prevents a measurement; it is not evidence that the device or link works. The
new focused regression module keeps those distinctions from silently reverting.

| Kernel row | Disposition | Evidence and reason | Mechanical action |
|---|---|---|---|
| P1-001 | Already done elsewhere | D-091 records the supervisor-ratified metrology-centred scope, and `docs/contracts/capstone_scope.md` records protected deliverables, stretch work, cut conditions, and forbidden claims. D-091 landed in commit `49c18763b8b91ad05eeea0bf972ebbff7b6bd5dd`; the earlier scope contract was installed with D-052 in `556b69eb132c88442f20028cd262e89c81ff1988`. | Replaced the empty meeting-note placeholder with pointers to the dated authorities. The magistrate should remove the stale live row from the protected kernel and preserve it as completed history. |
| P1-003 | Already done elsewhere | D-092 says explicitly that P1-003 is answered: the path is `to-buy`, no meter is currently available, and external measurement can validate whole-machine totals but not phase allocation. D-092 landed in commit `49c18763b8b91ad05eeea0bf972ebbff7b6bd5dd`. | Reconciled the checklist while leaving purchase, exact model selection, safe-fixture qualification, timing alignment, and characterization open under their later owners. The magistrate should close the stale decision row without closing those execution gates. |
| P1-004 | Already done elsewhere | The cited Phase 1 plan accepts either a known topology or a documented blocker. The checklist, introduced in commit `817f47047972091bd734b07bb1c7f712dae85e0d`, records the controller tools, candidate link classes, verification methods, transfer fields, and the missing node/adapter/cable assignment. | Made the blocker disposition explicit and stated that no physical link was measured. A fresh topology task is needed only if future split-inference hardware work opens. |
| P1-006 | Already done elsewhere | The kernel acceptance itself permits an explicit pending-with-blocker record. The NVIDIA and Orin sections have said `pending device access` since commit `817f47047972091bd734b07bb1c7f712dae85e0d`; the live-promotion checklist remains the authority for later device proof. | Named the missing SSH/device contact separately for NVIDIA and Orin, and pinned the rule that fixture evidence cannot promote provisional protocol claims. The magistrate should close this paperwork row while leaving the live-promotion row open. |
| P1-008 | Recommend retirement | `docs/milestones.md` still has no final-report date, colloquium date, borrow window, or derived phase targets. The row also asks again about the acceptance bar and Mac-only fallback already governed by D-091 and `docs/contracts/capstone_scope.md`, while the current NVIDIA portability row defers split work and owns its own access trigger. Keeping these concerns in one row makes partial evidence look like total completion. | No date or acceptance criterion was invented. Replace this row with a narrow external-input row for the final-report and colloquium dates, then derive internal cut dates. Keep borrow scheduling with its hardware owner and keep claim acceptance with the scope and claims contracts. |

No protected state file was edited. The required kernel, queue, run-state, and
decision-log changes are the magistrate actions stated in the table.

## Verification notes

The first focused run failed only because one test compared a wrapped Markdown
sentence as an unbroken string. The assertion was changed to accept whitespace,
and the identical focused command then passed. The repository-wide suite was
not run because the mission's preflight rule expressly forbids it.

## Residual risk

The academic dates remain unknown. Until the user or program supplies them,
`docs/milestones.md` cannot derive defensible phase targets or activate the
date-based cut rule. NVIDIA, Orin, wall-meter, and network statements remain
planning dispositions only; none is live measurement evidence.
