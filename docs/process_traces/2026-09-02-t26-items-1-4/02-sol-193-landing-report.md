```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Installed T26 cold-gate items 1 and 4 plus D-170; the mandated regex widening exposes one pre-existing D-150-family ordering inconsistency.",
  "workspace": {
    "base_requested": "300ca7f2",
    "base_mode": "exact",
    "head_start": "300ca7f25c711b2b7fc2027cecff08660d3b78d2",
    "head_end": "300ca7f25c711b2b7fc2027cecff08660d3b78d2",
    "upstream_end": "3e6243df8943f6a4ec152cab7ea791a8a161efea",
    "branch": "feat/2026-09-02-t26-install"
  },
  "pathspec": [
    "docs/decision_log.md",
    "docs/agent_playbook.md",
    "tests/test_docs_freshness.py",
    "docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md",
    "docs/process_traces/2026-08-27-t26/process-proposals/README.md"
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
      "cmd": "python3 -m unittest tests.test_docs_freshness tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "First differing element 150:",
          "'D-150'",
          "'D-150b'",
          "Ran 50 tests in 1.414s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 50 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "build",
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
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness.DocsFreshnessTests.test_decision_index_status_vocabulary_is_closed tests.test_docs_freshness.DocsFreshnessTests.test_open_decisions_name_an_installing_kernel_task tests.test_docs_freshness.DocsFreshnessTests.test_dated_magistrate_rulings_carry_executed_evidence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.011s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -c 'import sys,unittest; from unittest.mock import patch; import tests.test_docs_freshness as m; original=m._read; broken=original(\"docs/decision_log.md\").replace(\"open (installs via T26-RULING-INSTALL-01)\",\"invented\",1); suite=unittest.TestSuite([m.DocsFreshnessTests(\"test_decision_index_status_vocabulary_is_closed\")]); context=patch.object(m,\"_read\",lambda path: broken if path == \"docs/decision_log.md\" else original(path)); context.start(); result=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite); context.stop(); sys.exit(0 if not result.wasSuccessful() else 1)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "AssertionError: 'invented' not found in {'ratified', 'superseded', 'open', 'adjudicated', 'adopted', 'recorded', 'proposed', 'executed', 'accepted'} : D-170: status token is outside the closed vocabulary: 'invented'",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "D-170: status token is outside the closed vocabulary"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -c 'import sys,unittest; from unittest.mock import patch; import tests.test_docs_freshness as m; original=m._read; broken=original(\"docs/process/state_kernel.json\").replace(\"D-170\",\"D-171\"); suite=unittest.TestSuite([m.DocsFreshnessTests(\"test_open_decisions_name_an_installing_kernel_task\")]); context=patch.object(m,\"_read\",lambda path: broken if path == \"docs/process/state_kernel.json\" else original(path)); context.start(); result=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite); context.stop(); sys.exit(0 if not result.wasSuccessful() else 1)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "AssertionError: [] is not true : D-170: no kernel task has a kind: decision dependency on this row",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "D-170: no kernel task has a kind: decision dependency"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -c 'import re,sys,unittest; from unittest.mock import patch; import tests.test_docs_freshness as m; read=m._read; text=read(\"docs/decision_log.md\"); normalized=re.sub(r\"(^\\| D-150b .*$)\\n(^\\| D-150a .*$)\\n(^\\| D-150 .*$)\",r\"\\3\\n\\2\\n\\1\",text,flags=re.M); broken=normalized.replace(\"## D-150a:\",\"## D-X150a:\",1); suite=unittest.TestSuite([m.DocsFreshnessTests(\"test_decision_index_matches_decision_bodies\")]); context=patch.object(m,\"_read\",lambda path: broken if path == \"docs/decision_log.md\" else read(path)); context.start(); result=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite); context.stop(); sys.exit(0 if not result.wasSuccessful() else 1)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "First differing element 151:",
          "'D-150b'",
          "'D-150a'",
          "Second list contains 1 additional elements.",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "First differing element 151:.*D-150"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "python3 -c 'import sys,unittest; from pathlib import Path; from unittest.mock import patch; import tests.test_docs_freshness as m; Fake=type(\"FakePath\",(),{\"relative_to\":lambda self,root:Path(\"docs/process_traces/2026-09-02-mutation/MAGISTRATE-RULING-BROKEN.md\"),\"read_text\":lambda self,encoding=None:\"## Rulings\\n\\n## Executed evidence\\n\\nNo execution record.\\n\"}); suite=unittest.TestSuite([m.DocsFreshnessTests(\"test_dated_magistrate_rulings_carry_executed_evidence\")]); context=patch.object(m,\"_dated_magistrate_rulings\",lambda:[Fake()]); context.start(); result=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite); context.stop(); sys.exit(0 if not result.wasSuccessful() else 1)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "AssertionError: False is not true : docs/process_traces/2026-09-02-mutation/MAGISTRATE-RULING-BROKEN.md: dispositive ruling lacks a valid ## Executed evidence section",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MAGISTRATE-RULING-BROKEN.md: dispositive ruling lacks"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/agent_playbook.md",
          " M docs/decision_log.md",
          " M docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md",
          " M tests/test_docs_freshness.py",
          "?? docs/process_traces/2026-08-27-t26/process-proposals/README.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^( M|\\?\\?) (docs/decision_log.md|docs/agent_playbook.md|tests/test_docs_freshness.py|docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md|docs/process_traces/2026-08-27-t26/process-proposals/README.md)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The required D-id regex widening reveals a real historical order mismatch: bodies order D-150, D-150a, D-150b while the index orders D-150b, D-150a, D-150.",
      "needs": "Magistrate should authorize a separate historical-row reorder or accept the focused suite remaining red; this session did not paper over it."
    }
  ]
}
```

## Change

- A — [docs/decision_log.md](/Users/edr/code/JouleWise-wt-t26-a/docs/decision_log.md:212): added the D-170 index/body, D-118 additive pointer at line 7830, and D-160 R-5 pointer at line 10349. This records items 1–4 from `COLD-GATE-RULING.md:67-86`, `:128-143`, `:196-215`, and `:270-282`.
- B — [docs/decision_log.md](/Users/edr/code/JouleWise-wt-t26-a/docs/decision_log.md:14): installed item 1’s closed status vocabulary and kernel-backed `open (installs via <TASK-ID>)` form (`:67-101`).
- C — [tests/test_docs_freshness.py](/Users/edr/code/JouleWise-wt-t26-a/tests/test_docs_freshness.py:236): widened D-id matching and added the status, install-pointer, and executed-evidence checks at lines 243, 256, and 292 (`:88-101`, `:285-286`).
- D — [MAGISTRATE-RULING-T0-UNATTENDED.md](/Users/edr/code/JouleWise-wt-t26-a/docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:85): appended item 3’s dated Horizon amendment (`:196-215`, `:248-251`).
- E — [docs/agent_playbook.md](/Users/edr/code/JouleWise-wt-t26-a/docs/agent_playbook.md:57) and [process-proposals/README.md](/Users/edr/code/JouleWise-wt-t26-a/docs/process_traces/2026-08-27-t26/process-proposals/README.md:1): installed Mission M0’s uninstalled-ruling warning and documented the three branches plus item 4’s scratchpad-only consult-template obligation (`:103-109`, `:287-300`).

## Verification notes

The named-module suite’s sole failure is the historical D-150-family ordering inconsistency exposed by the required regex widening. No mutation was left in the worktree, and only WRITE_SCOPE paths are dirty.

## Residual risk

D-170 correctly remains open until the item 2 and item 3 sibling branches land and the magistrate records their installing PRs.