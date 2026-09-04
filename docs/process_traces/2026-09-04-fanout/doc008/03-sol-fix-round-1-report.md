```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "FIX ROUND 1 is blocked because every refuter cure requires paths excluded by the runner-authoritative WRITE_SCOPE.",
  "workspace": {
    "base_requested": "8a3b81ccaf14c42f3966c1eef299e551ad91985d",
    "base_mode": "exact",
    "head_start": "8a3b81ccaf14c42f3966c1eef299e551ad91985d",
    "head_end": "8a3b81ccaf14c42f3966c1eef299e551ad91985d",
    "upstream_end": "8a3b81ccaf14c42f3966c1eef299e551ad91985d",
    "branch": "feat/2026-09-04-fan-doc008"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/doc008/03-sol-fix-round-1-report.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/doc008/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "test \"$(git rev-parse HEAD)\" = 8a3b81ccaf14c42f3966c1eef299e551ad91985d && test \"$(git branch --show-current)\" = feat/2026-09-04-fan-doc008 && printf 'HEAD/branch gate: PASS\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["HEAD/branch gate: PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^HEAD/branch gate: PASS$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'allowed={\"docs/agent_playbook.md\",\"docs/orchestration.md\",\"docs/phase_2/phase_2_exit_checklist.md\",\"docs/planning_reflection_protocol.md\",\"docs/project_status_history.md\"}; needed={\"AGENT_PLAN.md\",\"README.md\",\"PROJECT_STATUS.md\",\"tests/test_docs_freshness.py\"}; assert not (allowed & needed); print(\"scope gate: NEEDS_SCOPE AGENT_PLAN.md README.md PROJECT_STATUS.md tests/test_docs_freshness.py\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["scope gate: NEEDS_SCOPE AGENT_PLAN.md README.md PROJECT_STATUS.md tests/test_docs_freshness.py"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^scope gate: NEEDS_SCOPE AGENT_PLAN.md README.md PROJECT_STATUS.md tests/test_docs_freshness.py$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --no-index --check /dev/null docs/process_traces/2026-09-04-fanout/doc008/03-sol-fix-round-1-report.md; rc=$?; test \"$rc\" -eq 1",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "F-001 cannot be cured inside the exhaustive allowlist: the stale intake routes and uncompacted advisor view are in three excluded root documents.",
      "needs": "Resume with AGENT_PLAN.md, README.md, and PROJECT_STATUS.md added to WRITE_SCOPE; the magistrate must review and sign the PROJECT_STATUS.md draft."
    },
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "F-002 cannot be cured inside the exhaustive allowlist: the required biting regressions belong in the excluded existing module tests/test_docs_freshness.py.",
      "needs": "Resume with tests/test_docs_freshness.py added to WRITE_SCOPE."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "No test module was run because no authorized production or test cure could be made; rerunning the known-green module would not establish either blocked counterfactual.",
      "needs": "After scope expansion, add the regressions and run only tests.test_docs_freshness plus independent reverse-mutation probes."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "AGENT_PLAN.md",
      "README.md",
      "PROJECT_STATUS.md",
      "tests/test_docs_freshness.py"
    ],
    "reason": "The refuter's F-001 production cures exist only in the three named root documents, and F-002 requires biting checks in the repository's existing docs-freshness test module.",
    "blocked_work": "Retire the remaining root intake/reflection routes, compact the advisor status page under lead review, and add independent regressions that reject each exact base-version counterfactual named by the refuter.",
    "minimal_change": "Add only the four named paths to the resumed WRITE_SCOPE; retain the current six documentation paths and DOC-008 trace wildcard."
  }
}
```

## Change

No refuter cure was written. The runner-authoritative allowlist omits every
production and regression path required by F-001 and F-002, despite the prior
magistrate ruling authorizing the three root documents. The refuter verdict
was preserved as unowned input, and this report is the only session write.

Finding-to-cure map:

| finding | required cure and named counterfactual regression | file:line |
|---|---|---|
| F-001 | Replace the stale direct `RUN_STATE.md` / `TASK_QUEUE.md` / planning-reflection intake with Mission M0 and the kernel route. Compact the advisor page to at most seven H2 sections under magistrate review. Add a regression that feeds the stale root intake text and the current 16-H2 advisor page, then requires rejection. | `AGENT_PLAN.md:10`; `README.md:249`; `PROJECT_STATUS.md:71`; `tests/test_docs_freshness.py:552` |
| F-002 | Add a focused DOC-008 contract checker and four independent mutation regressions. Each mutation must feed the exact merge-base version named by the refuter: old M0 plus checklist route, live reflection checklist, orchestration without the two exact procedures, and absent status-history archive. Each must fail while current inputs pass. | `tests/test_docs_freshness.py:552` |

No magistrate-owned kernel, queue, run-state, or decision-log row is needed for
these cures, so there is no row text to hand off.

## Verification notes

No test module was run: only this trace report changed, and the required test
module is outside WRITE_SCOPE. The exact HEAD/branch gate and whitespace check
passed. The next resumed seat should run `tests.test_docs_freshness` and the
four independent reverse-mutation probes only; the whole suite remains
forbidden by the preflight rule.

## Residual risk

The landing remains not landable. A session can still follow the superseded
root intake route, the advisor page remains uncompacted, and the six-path DOC-008
delta still has no biting behavioral regression.
