```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One B1 coverage gap: both argument-contract mutants survive; routing parity, Phase A exports, N1, and historical-byte preservation verified.",
  "workspace": {
    "base_requested": "f0fedc91a5bf35189fed34962506b65d4903d8d8",
    "base_mode": "exact",
    "head_start": "3e016b042f46354f9bb63a0b40ef91d8823475a0",
    "head_end": "3e016b042f46354f9bb63a0b40ef91d8823475a0",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 1, "nit": 0},
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "file": "tests/test_check_window_provenance.py",
        "line": 641,
        "title": "B1 does not behaviorally pin exactly one argument or exclude an environment fallback",
        "detail": "Both temporary mutants preserve every asserted source string: one normalizes two positional arguments to one before the arity guard; another supplies the missing argument from NIGHT_PLAN. The rewritten B1 test passes for both, and executing each mutated routing prefix confirms acceptance with exit 0.",
        "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/g2a_delta_audit.py",
        "recommendation": "Add executable refusal assertions for two positional arguments and for zero arguments with NIGHT_PLAN populated."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_window_provenance tests.test_preflight tests.test_gen_g2_phase_d tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 110 tests in 32.104s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 110 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/g2a_delta_audit.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "B1 MUTANT SURVIVED second test=PASS routing_exit=0",
          "B1 MUTANT SURVIVED fallback test=PASS routing_exit=0",
          "A0_CANONICAL_V2_EQUALS_DRIVER_EXPORTS",
          "DOC_ADDITIONS_ONLY SHAKEDOWN-G2-RUNSHEET.md 18 0",
          "DOC_ADDITIONS_ONLY RUNSHEET.md 8 0",
          "DOC_ADDITIONS_ONLY 00-verification-notes.md 1 0"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "A0_CANONICAL_V2_EQUALS_DRIVER_EXPORTS"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated Phase D matches pinned runbook bytes"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS generated Phase D matches pinned runbook bytes"}
    }
  ],
  "flags": []
}
```

## Findings

**R1 — should_fix — `tests/test_check_window_provenance.py:641`.** B1 checks source-string presence, but both argument-contract bypasses survive. Replay: `PYTHONDONTWRITEBYTECODE=1 python3 /tmp/g2a_delta_audit.py`.

The independently derived ranges match the emitter and test. Drifted ranges and a missing heading produce `FAIL` with exit 1. At `20260910`, the routing body is byte-identical to HEAD~1; the complete chain differs only in its source-range comment.

Phase A’s actual jq commands match `_run_chain_once`’s root/head exports for a writer-produced v2 plan. N1 is one test containing two direct program invocations; both passed. All three documentation diffs contain additions only. No additional regression was found.

## Residual risk

Routing mutation probes execute isolated prefixes; the driver export probe intercepts process launch. No live measurement or hardware validation was performed.