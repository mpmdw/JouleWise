```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "P1R2-1's literal counterfactual is cured, but two same-signature masking defects in the new parsers keep the fix round not landable.",
  "workspace": {
    "base_requested": "88aab375417dd1eb8aa3ff2d10e734d715e2e6b3",
    "base_mode": "exact",
    "head_start": "88aab375417dd1eb8aa3ff2d10e734d715e2e6b3",
    "head_end": "88aab375417dd1eb8aa3ff2d10e734d715e2e6b3",
    "upstream_end": "88aab375417dd1eb8aa3ff2d10e734d715e2e6b3",
    "branch": "feat/2026-09-04-fan-p1-rows"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/p1-rows/04-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "prior_findings": [
      {
        "id": "P1R2-1",
        "disposition": "CURED",
        "evidence": "The touched module passes at HEAD; restoring the four contiguous Still required bullets and all five old matrix statuses produces six failures."
      }
    ],
    "same_signature": "P1R3-1 and P1R3-2 share P1R2-1's signature: an operative status regression is masked by the regression-test parser, although their paragraph-boundary and duplicate-key triggers are new.",
    "findings": [
      {
        "id": "P1R3-1",
        "severity": "blocker",
        "location": "tests/test_phase1_row_dispositions.py:25-31,50-53",
        "text": "The current-status regression inspects only the first nonempty paragraph after `Still required:`. Reintroducing a removed required item after a blank line leaves the assertion equal to the calendar bullet and passes, so the test does not establish that calendar mapping is the sole open item.",
        "counterfactual": "An in-memory one-line replacement appends a blank line and `- Supervisor approval and scope confirmation (Step 1).` after the calendar bullet; the named test reports Ran 1 test / OK."
      },
      {
        "id": "P1R3-2",
        "severity": "should_fix",
        "location": "tests/test_phase1_row_dispositions.py:34-42,55-69",
        "text": "The evidence-matrix parser silently overwrites duplicate item keys. A stale `Supervisor approval and scope | pending` row immediately before the correct row leaves a contradictory operative matrix while the named regression passes.",
        "counterfactual": "An in-memory one-line insertion adds the stale duplicate row before the current row; the named test reports Ran 1 test / OK."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_phase1_row_dispositions",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 0.002s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -c 'import sys,unittest; from tests import test_phase1_row_dispositions as m; t=m.CHECKLIST.read_text(encoding=\"utf-8\"); t=t.replace(\"- Calendar mapping (Step 7).\", \"- Supervisor approval and scope confirmation (Step 1).\\n- Wall-meter decision (Step 3).\\n- Network/interconnect plan with physical topology (Step 4).\\n- NVIDIA/Orin access evidence (Step 6).\\n- Calendar mapping (Step 7).\", 1); t=t.replace(\"complete by later authority (2026-07-30)\", \"pending\", 1).replace(\"complete; acquisition pending (2026-07-30)\", \"pending\", 1).replace(\"blocker recorded; physical confirmation pending\", \"partially checked\", 1).replace(\"pending with recorded blocker\", \"pending\"); m.Phase1RowDispositionTests.setUpClass=classmethod(lambda cls:setattr(cls,\"text\",t)); r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(m)); sys.exit(0 if len(r.failures)==6 and not r.errors else 1)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 0.003s",
          "FAILED (failures=6)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FAILED \\(failures=6\\)$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -c 'import sys,unittest; from tests import test_phase1_row_dispositions as m; t=m.CHECKLIST.read_text(encoding=\"utf-8\").replace(\"- Calendar mapping (Step 7).\", \"- Calendar mapping (Step 7).\\n\\n- Supervisor approval and scope confirmation (Step 1).\", 1); m.Phase1RowDispositionTests.setUpClass=classmethod(lambda cls:setattr(cls,\"text\",t)); r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(\"Phase1RowDispositionTests.test_current_status_keeps_only_calendar_mapping_open\", m)); sys.exit(not r.wasSuccessful())'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.000s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -c 'import sys,unittest; from tests import test_phase1_row_dispositions as m; t=m.CHECKLIST.read_text(encoding=\"utf-8\").replace(\"| Supervisor approval and scope | complete by later authority (2026-07-30)\", \"| Supervisor approval and scope | pending | stale duplicate disposition | stale duplicate |\\n| Supervisor approval and scope | complete by later authority (2026-07-30)\", 1); m.Phase1RowDispositionTests.setUpClass=classmethod(lambda cls:setattr(cls,\"text\",t)); r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(\"Phase1RowDispositionTests.test_evidence_matrix_pins_reconciled_dispositions\", m)); sys.exit(not r.wasSuccessful())'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.000s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "test \"$(git rev-parse HEAD)\" = 88aab375417dd1eb8aa3ff2d10e734d715e2e6b3; git show --format= --name-only HEAD; git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tests/test_phase1_row_dispositions.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_phase1_row_dispositions.py$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/p1-rows/04-delta-reaudit-round-1.md\"); lines=p.read_text(encoding=\"utf-8\").splitlines(); fence=chr(96)*3; assert lines[0] == fence+\"json\"; end=lines.index(fence,1); b=(\"\\n\".join(lines[1:end])+\"\\n\").encode(\"utf-8\"); obj=json.loads(b); assert len(b)<=8192; assert obj[\"verdict\"][\"gauntlet\"]==\"NOT LANDABLE\"; print(\"report-envelope-ok\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report-envelope-ok"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report-envelope-ok$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "Same-signature status masking remains in both new parsing helpers.",
      "needs": "Assert the entire Still required region through the next semantic label, reject duplicate Evidence Matrix item keys, and rerun positive and adverse cases."
    }
  ]
}
```

## Findings

- **P1R3-1 — blocker.** `_first_paragraph_after` stops at the first blank
  line, so it proves only that the first paragraph equals the calendar bullet.
  A restored open requirement in the next paragraph is still inside `Still
  required` but survives the named regression. Assert the full region up to
  the next label (`The original Phase 1 paperwork gates...` or an explicit
  subheading), not one paragraph.

- **P1R3-2 — should_fix.** `_matrix_statuses` stores rows in a dictionary
  without rejecting a repeated first cell. A later correct row masks an earlier
  stale disposition. Make duplicate item names an assertion failure before
  checking expected statuses.

P1R2-1 is **CURED** for its literal counterfactual: the touched module is green
at HEAD and the contiguous four-bullet plus five-status restoration fails six
assertions. Both new findings are **same-signature** with P1R2-1—operative
status drift remains green—but arise from parser behavior added in fix round 1.

## Residual risk

Per the preflight rule, only `tests.test_phase1_row_dispositions`, the sole test
module touched by the fix commit, was executed. No repository-wide or unrelated
test module was run. Counterfactuals were injected in memory, leaving repository
files unchanged.
