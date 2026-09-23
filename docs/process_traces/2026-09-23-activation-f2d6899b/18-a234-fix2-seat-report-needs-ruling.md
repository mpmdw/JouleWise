```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "F1, F2, S1, S3 and the Opus N1 regression are in place; F3 needs a ruling on the plan-bound runs root.",
  "workspace": {
    "base_requested": "4c76ab69",
    "base_mode": "exact",
    "head_start": "4c76ab6979a16e80e15d2174eafe4e1857aabac3",
    "head_end": "4c76ab6979a16e80e15d2174eafe4e1857aabac3",
    "upstream_end": "4c76ab6979a16e80e15d2174eafe4e1857aabac3",
    "branch": "feat/2026-09-23-refusal-early-release-f3"
  },
  "pathspec": [
    "scripts/magistrate_watchdog.py",
    "joulewise/arm_retry.py",
    "tests/test_magistrate_watchdog.py",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_magistrate_watchdog.py -k 'live_driver_without_agent_census_match or replaced_result_same_plan_and_root or undelivered_chain_refusal_keeps_deadman_tail or result_chain_fields_veto_zero_capture_release'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["3 failed, 1 passed, 107 deselected in 0.36s"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "3 failed, 1 passed"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_magistrate_watchdog.py -k 'live_driver_without_agent_census_match or replaced_result_same_plan_and_root or unreadable_replacement_result or undelivered_chain_refusal_keeps_deadman_tail or result_chain_fields_veto_zero_capture_release or production_driver_probe_uses_bracketed'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["6 passed, 107 deselected in 0.29s"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "6 passed"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_magistrate_watchdog.py tests/test_magistrate_watchdog_cli.py tests/test_arm_retry.py tests/test_install_magistrate_watchdog.py tests/test_evidence_night.py tests/test_docs_freshness.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["302 passed, 754 subtests passed in 331.37s (0:05:31)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "302 passed, 754 subtests passed"
      }
    },
    {
      "id": "V4",
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
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The gate's NightPlan has no runs_root; the derivation generator permits an explicit --runs-root override. The watchdog cannot establish the plan's instrument_validation inventory from the gate's own plan code as specified.",
      "needs": "Rule the authoritative plan-bound runs-root source and any required scope expansion before F3 is implemented."
    },
    {
      "id": "F3-TESTS",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "F3 disk-fact tests and its three single-fact mutants were not added because the inventory operand is unresolved.",
      "needs": "Implement and run them after the runs-root ruling."
    },
    {
      "id": "EARLY-RELEASE",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "This partial branch can still release with a nested consumed marker. It is not ready to land.",
      "needs": "Complete F3 and repeat verification."
    }
  ]
}
```

## Change

- **F1:** [The watchdog](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:70) now injects the exact driver `pgrep` probe and requires it and the agent census to be empty on the same tick; the census event records the driver observation. [The hold-then-release test](/Users/edr/code/wt-f2d6899b-f3/tests/test_magistrate_watchdog.py:247) returned `LAUNCHING` before and passes now.
- **F2:** [The release key](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:819) includes SHA-256 of `result.json` bytes; an unreadable result has no key. [The replacement test](/Users/edr/code/wt-f2d6899b-f3/tests/test_magistrate_watchdog.py:269) returned `LAUNCHING` without a new census before and now holds with a census.
- **S1:** [The undelivered chain-started tail](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:867) retains the dead-man bound. [Its test](/Users/edr/code/wt-f2d6899b-f3/tests/test_magistrate_watchdog.py:301) was false at baseline and passes now.
- **S3:** Both first-use paragraphs now define the refusal class, tick and `SUPERVISOR_POLL_S = 10`, notice, owner veto, exact window bound, both probes, and one-way release: [handback](/Users/edr/code/wt-f2d6899b-f3/docs/process/NIGHT_HANDBACK.md:57), [runbook](/Users/edr/code/wt-f2d6899b-f3/docs/phase_2/derivation_night_runbook.md:1856).
- **Opus N1:** [The `decide()` regression](/Users/edr/code/wt-f2d6899b-f3/tests/test_magistrate_watchdog.py:314) passes with the existing chain-field guard and fails against the specified `if False` mutant (`FENCED` expected, `LAUNCHING` observed). Its baseline pass is inherent: this guard already existed at 4c76ab69.

## Verification notes

The specified suite passed. No commit was made. The required `rg -n zero_capture_evidence --type py -g '!tests/**'` found no production writer; production matches are reads in `joulewise/arm_retry.py`. Archival scripts under `docs/process_traces/` do contain writers, so the finding is specifically about production code.

**NEEDS_RULING — F3.** [The gate’s `NightPlan`](/Users/edr/code/wt-f2d6899b-f3/joulewise/night_gate.py:348) has no `runs_root`. [The derivation generator](/Users/edr/code/wt-f2d6899b-f3/scripts/gen_derivation_night.py:557) defaults to `custody_root/runs` **or accepts `--runs-root`**; [the production inventory](/Users/edr/code/wt-f2d6899b-f3/joulewise/arm_readiness.py:245) also names `measurement_root/runs`. Which plan-bound source must the watchdog use? I considered either fixed path and parsing a chain wrapper; neither is the gate’s authoritative resolver for every plan. I recommend ruling a pinned runs-root source and the exact additional write scope it requires. That blocks F3 and its three mutants.

## Residual risk

A fixture probe at this head returned `consumption LAUNCHING` with a nested `*.consumed.json`; `chain.started` returned `FENCED`. The magistrate should double-check the runs-root ruling and keep this partial branch unmerged until F3 and its required tests pass.