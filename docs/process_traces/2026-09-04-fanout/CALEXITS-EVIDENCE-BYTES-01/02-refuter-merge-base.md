```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "The refreshed mission-only delta is scope-clean, the focused regression passes twice, and a controlled reverted-copy counterfactual kills exactly the two intended artifact comparisons.",
  "workspace": {
    "base_requested": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "946897b198c77587541c53a2411ad165378c5e9a",
    "head_end": "946897b198c77587541c53a2411ad165378c5e9a",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-CALEXITS-EVIDENCE-BYTES-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/CALEXITS-EVIDENCE-BYTES-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".", "----------------------------------------------------------------------", "Ran 1 test in 60.141s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".", "----------------------------------------------------------------------", "Ran 1 test in 67.902s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --name-only \"$base\"..HEAD; for p in RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md; do git diff --quiet \"$base\"..HEAD -- \"$p\" || exit 1; done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["docs/process_traces/2026-09-04-fanout/CALEXITS-EVIDENCE-BYTES-01/01-sol-report.md", "tests/test_calibration_exits.py"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "01-sol-report\\.md\\ntests/test_calibration_exits\\.py$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "cd /private/tmp/calexits-refuter.D85DAL && env PATH=\"/private/tmp/calexits-refuter.D85DAL/mutant-bin:$PATH\" python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["----------------------------------------------------------------------", "Ran 1 test in 74.829s", "", "FAILED (failures=2)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check $(git merge-base origin/main HEAD)..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This refuter verified the required focused module locally but did not observe a hosted-CI execution; CI remains a later merge-gate input named by the mission acceptance row.",
      "needs": "Lead should require the focused hosted-CI leg before closing CALEXITS-EVIDENCE-BYTES-01."
    }
  ]
}
```

## Findings

None.

## Evidence

- Review range was exactly `b0ed6991c11f3a515ad293760c6dfc031adda8e1..946897b198c77587541c53a2411ad165378c5e9a`, where the left endpoint was computed with `git merge-base origin/main HEAD`. Its only paths are `tests/test_calibration_exits.py` and the implementer report, exactly matching that report's declared scope. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta in that range.
- The only behavioral change is test-fixture behavior. Each independent capture installs a private `ps` executable first on `PATH`, supplies the same PID and command, and asserts that the emitted census event contains exactly that row. Production census code is unchanged. The exact claimed regression passed twice at final HEAD.
- Counterfactual input: baseline census reports PID 111 / `counterfactual-A`, while the delayed capture reports PID 222 / `counterfactual-B`. In a temporary copy, the mission hunk was reverted and a fake `ps` keyed those outputs directly to absence/presence of `JW_FAKE_MLX_DELAY_S`. The test failed on exactly `events.jsonl` and its downstream `instrument_evidence.json`; raw sampler and CSV bytes did not fail. This is the failure shape the fixture cure is intended to remove.
- An initial call-count-based fake-`ps` attempt passed and was rejected as a false counterfactual because a writer may census more than once. The input-keyed replay above removed that ambiguity and killed the reverted test. The mission directory contains no previous-round refuter verdict, so there was no prior non-staleness blocker to re-test; the refreshed range itself was used without raising a staleness finding.
- No whole-suite run was performed, per the preflight rule. `git diff --check` passed.

## Residual risk

Hosted CI was not available in this review turn. That is a nonblocking merge-gate evidence gap, not a defect in the reviewed delta.
