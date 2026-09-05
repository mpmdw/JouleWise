```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The refreshed DOC-008 delta is in scope and its claimed checks pass, but the ruled root completion is absent and none of the behavioral documentation changes has a biting regression test.",
  "workspace": {
    "base_requested": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "8a3b81ccaf14c42f3966c1eef299e551ad91985d",
    "head_end": "8a3b81ccaf14c42f3966c1eef299e551ad91985d",
    "upstream_end": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "branch": "feat/2026-09-04-fan-doc008"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/doc008/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "F-001",
        "severity": "blocker",
        "location": "AGENT_PLAN.md:10; README.md:249; PROJECT_STATUS.md:71",
        "text": "The magistrate ruled that DOC-008 resume as one seat with AGENT_PLAN.md, README.md, and PROJECT_STATUS.md in scope, but none has a mission delta. PROJECT_STATUS.md still has 16 H2 sections and 6,048 words rather than the required maximum seven-section compact current view, while AGENT_PLAN.md and README.md still route substantial work through the retired planning-reflection protocol. The landing therefore remains the pre-ruling partial implementation described by 01-sol-report.md, not the ruled resumed mission.",
        "counterfactual": "A new session following AGENT_PLAN.md:10-15 or README.md:249-260 still takes the superseded RUN_STATE/TASK_QUEUE/reflection intake path, and an advisor opening PROJECT_STATUS.md still receives the uncompacted historical/current mixture and pre-D-171 process prose."
      },
      {
        "id": "F-002",
        "severity": "blocker",
        "location": "tests/test_docs_freshness.py:1",
        "text": "The delta adds no test. In separate throwaway clones, reverting each behavioral group independently—agent_playbook plus the phase-2 checklist, the reflection stub, orchestration, and the status-history archive—left all 23 tests.test_docs_freshness tests green. Reverting the entire six-path mission delta also left tests.test_docs_freshness (23), tests.test_gen_state (42), and gen_state.py --check green. The claimed checks therefore do not establish the behavioral changes.",
        "counterfactual": "The required biting inputs are the base versions with the old M0/close-out route, the live planning-reflection checklist, orchestration without the exact two procedures, and no project_status_history.md; each was supplied independently and every claimed relevant test still passed."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --name-only \"$base\"..HEAD; git diff --name-only \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/agent_playbook.md",
          "docs/orchestration.md",
          "docs/phase_2/phase_2_exit_checklist.md",
          "docs/planning_reflection_protocol.md",
          "docs/process_traces/2026-09-04-fanout/doc008/01-sol-report.md",
          "docs/project_status_history.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "docs/project_status_history.md$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 23 tests in 1.172s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 23 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gen_state -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 42 tests in 2.933s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 42 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 scripts/gen_state.py --check",
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
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path as P; s=P(\"docs/specs/c027/doc-008_state_kernel.md\").read_text(); f=lambda m:s.split(m,1)[1].split(\"```markdown\\n\",1)[1].split(\"\\n```\",1)[0]+\"\\n\"; r=P(\"docs/planning_reflection_protocol.md\").read_text(); o=P(\"docs/orchestration.md\").read_text(); assert r==f(\"### 6.3 Exact redirect stub\"); assert f(\"### 7.1 Two-writer rule\") in o; assert f(\"### 7.2 Credential-boundary push procedure\") in o; print(\"redirect stub exact: PASS\"); print(\"orchestration mandated blocks: 2/2 exact\")'; python3 -c 'from pathlib import Path as P; s=P(\"PROJECT_STATUS.md\").read_text(); a=P(\"docs/project_status_history.md\").read_text(); parts=[s.split(\"## Update Ledger\\n\",1)[1].split(\"\\n<!-- ADVISOR-PAGE-END -->\",1)[0].strip(),s.split(\"## Evolution From The Original Architecture Sketch\\n\",1)[1].split(\"\\n## Risks And Minimum Viable Outcome\",1)[0].strip(),s.split(\"## Process Note\\n\",1)[1].split(\"\\n## Maintenance Of This Document\",1)[0].strip()]; assert all(x in a for x in parts); print(\"archive source prose: 3/3 verbatim\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "redirect stub exact: PASS",
          "orchestration mandated blocks: 2/2 exact",
          "archive source prose: 3/3 verbatim"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "archive source prose: 3/3 verbatim"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "set -e; base=$(git merge-base origin/main HEAD); for item in 'intake:docs/agent_playbook.md docs/phase_2/phase_2_exit_checklist.md' 'reflection:docs/planning_reflection_protocol.md' 'orchestration:docs/orchestration.md' 'archive:docs/project_status_history.md'; do case_name=${item%%:*}; paths=${item#*:}; probe_dir=$(mktemp -d /tmp/doc008-cf.XXXXXX); git clone -q --shared . \"$probe_dir\"; git diff \"$base\"..HEAD -- ${=paths} | git -C \"$probe_dir\" apply -R; (cd \"$probe_dir\" && python3 -m unittest tests.test_docs_freshness -q); printf '%s counterfactual unexpectedly green\\n' \"$case_name\"; done",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "intake counterfactual unexpectedly green",
          "reflection counterfactual unexpectedly green",
          "orchestration counterfactual unexpectedly green",
          "archive counterfactual unexpectedly green"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG-001",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Every behavioral counterfactual remained green under the claimed focused documentation test module.",
      "needs": "Add focused regressions that reject each reverted DOC-008 procedure/archive state, then rerun the independent mutations."
    }
  ]
}
```

## Findings

### F-001 — blocker

The scope and protected-state check passes: the six pre-review delta paths are
exactly the six paths listed by the seat report, and `RUN_STATE.md`,
`TASK_QUEUE.md`, `docs/process/state_kernel.json`, and
`docs/decision_log.md` have no delta. However, the magistrate's post-report
ruling authorized and required the three root paths as one resumed seat. At
this head those files are unchanged. The original seat's own partial/blocking
conditions therefore remain observable rather than cured.

### F-002 — blocker

The positive checks are genuinely green, and the exact redirect stub, both
mandated orchestration blocks, and the three archived prose bodies match their
DOC-008 sources. They are not protected by the claimed tests. Four isolated
reverse-delta probes and one full-mission reversal all stayed green, proving
that the suite result is independent of every behavioral edit in this landing.

No previous refuter verdict exists in the DOC-008 directory or its Git history,
so there was no prior DOC-008-specific non-staleness blocker to retest. The
examples named in the prompt (spoofable CLI, mutable ID, occupied root, false
counterfactual) do not occur as prior findings for this mission; the newly
executed counterfactual failure is F-002.

## Residual risk

The review did not run the whole suite, per the preflight rule. No code module,
hardware path, or quiet-machine behavior changed; residual risk is confined to
documentation semantics beyond the exact contract checks above.
