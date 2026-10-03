```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "R2 and R3 implemented; admission test-contract conflict requires ruling, and sandbox prevents requested commits.",
  "workspace": {
    "base_requested": "b317866d",
    "base_mode": "exact",
    "head_start": "b317866d04b4b2af1eaf4522df6563d87e8bafe3",
    "head_end": "b317866d04b4b2af1eaf4522df6563d87e8bafe3",
    "upstream_end": "b317866d04b4b2af1eaf4522df6563d87e8bafe3",
    "branch": "feat/2026-10-02-g2a-night-integration"
  },
  "pathspec": [
    "scripts/gen_g2_phase_d.py",
    "scripts/generate_g2a_probe_inputs.py",
    "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
    "docs/phase_2/window_runbook.md",
    "tests/test_gen_g2_phase_d.py",
    "tests/test_generate_g2a_probe_inputs.py"
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
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_g2_phase_d tests.test_generate_g2a_probe_inputs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 36 tests in 16.297s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_g2_phase_d tests.test_generate_g2a_probe_inputs tests.test_summarize_g2a_prefill_probe tests.test_select_g2a_prefill_length tests.test_harvest_window tests.test_gen_derivation_night tests.test_check_window_provenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 181 tests in 82.123s",
          "",
          "OK",
          "PASS built G2-a prompt ladder, configs, and manifests",
          "PASS bound G2-a inputs to the calibration window"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_gate tests.test_run_night_probe_cadence tests.test_run_night_probe_worker_cadence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 111 tests in 6.653s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated Phase D matches pinned runbook bytes"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS generated Phase D matches pinned runbook bytes$"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_g2_phase_d.py --emit-chain /tmp/g2a-lane/chain.zsh --night-date 20261003",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["emitted /tmp/g2a-lane/chain.zsh"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^emitted /tmp/g2a-lane/chain.zsh$"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "/bin/zsh -n /tmp/g2a-lane/chain.zsh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-defect-check.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS all four defect tests reject the base implementation (six failure assertions)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS all four defect tests reject the base implementation"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-base-night-tests.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: False is not true : test interpreter must load the battery fixture in child Pythons",
          "Ran 2 tests in 0.512s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V9",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V10",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_g2_phase_d tests.test_run_night tests.test_run_night_probe_cadence tests.test_run_night_probe_worker_cadence tests.test_night_agent_install tests.test_night_gate tests.test_generate_g2a_probe_inputs tests.test_summarize_g2a_prefill_probe tests.test_select_g2a_prefill_length tests.test_harvest_window tests.test_gen_derivation_night tests.test_check_window_provenance",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V11",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: existing Revision 6 start-condition tests use D-166 registration bytes while asserting Revision 6 manifest fields and the 7680-second budget. R1 requires exact Revision 6 registration authentication, so these tests cannot remain unchanged and retain their existing expectations.",
      "needs": "Authorize correcting the affected test fixtures to authenticate the actual Revision 6 registration while preserving their assertions."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "git add and git commit both exited 128: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-g2a-lane/index.lock': Operation not permitted. No changes are staged or committed.",
      "needs": "Provide a runner with writable worktree Git metadata, or commit the reviewed changes lead-side."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Two sampled installer tests fail because the specified venv cannot load the child-Python battery fixture. Both failures reproduce against byte-identical requested-base driver, installer, and fixture code.",
      "needs": "Resolve the test interpreter fixture environment before claiming the complete suite is green."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Canonical and combined requested suites were interrupted for the required early return. R1 and R4-R7 remain unimplemented; new-window plan emission, preflight, installer render, argv-only mutation proof, harvest, and low-count campaign proof are not completed.",
      "needs": "Resume this lane after the ruling and runner correction, then complete implementation and all required verification."
    }
  ]
}
```

## Change

The [producer](/Users/edr/code/JouleWise-g2a-lane/scripts/generate_g2a_probe_inputs.py:695) now rejects every ledger snapshot refusal (+2 lines). Its tests (+34 lines) cover the stale 76-row ledger and a pending-ledger refusal.

The [generator](/Users/edr/code/JouleWise-g2a-lane/scripts/gen_g2_phase_d.py:23) derives screen literals through the existing authenticated writer (+41/−2 lines). It refreshes both source documents and regenerates their governed regions. Tests (+51 lines) cover stale source, stale generated output, mutually consistent stale literals, regeneration, and emission. Documentation changes are 9 replaced runbook lines and 6 replaced runsheet lines.

| Ruling | Disposition and evidence |
|---|---|
| R1 | **NEEDS_RULING**; admission untouched. Existing `test_start_manifest_first_window_records_null_prior_and_all_conditions` exposes the fixture conflict. |
| R2 | Implemented: `test_stale_76_row_ledger_refuses_against_current_acceptance`, `test_any_ledger_snapshot_refusal_is_fatal`. |
| R3 | Implemented: `test_screen_check_detects_stale_source_and_rendered_literals`, `test_emission_derives_screen_even_from_stale_source`. |
| R4 | Pending; no installer or inspection-surface changes. |
| R5 | Pending. |
| R6 | Pending; no new-window command or plan authored. |
| R7 | Pending; no harvester or low-count campaign proof added. Capture and reducer untouched. |
| R8 | No seed code change. The retained C2 376-row ledger authenticates; the stale-prefix producer regression passes. |

## Verification notes

**NEEDS_RULING**

- **Question:** May the existing Revision 6 test fixtures be corrected while retaining their assertions?
- **Evidence:** [Fixture setup](/Users/edr/code/JouleWise-g2a-lane/tests/test_run_night.py:412) copies D-166 registration bytes; [Revision 6 assertions](/Users/edr/code/JouleWise-g2a-lane/tests/test_run_night.py:939) require Revision 6 custody, and line 991 requires its budget.
- **Options considered:** Correct fixture registration identity; or retain broad admission, which contradicts R1.
- **Recommendation:** Correct fixture identity only.
- **Blocked work:** R1 implementation under the unchanged-test requirement; remaining lane integration stopped for this early return.

No repository scope expansion is requested. No prohibited live operations ran. The emitted chain passed shell syntax; its unsafe current inspection flags were not executed.

`NIGHT_PROGRAMMED_SPAN_S` was **not authored**. The fixed subtotal remains:

`9×600 + 8×20 + 24×(75+5+1) + 2×196.703125 + 2×(20+5) = 7947.40625 s`.

No variable-work allowance or final integer span is claimed.

## Residual risk

The window is not yet armable or harvestable. Six files remain unstaged and uncommitted. Next step: lead ruling on fixture correction and a writable Git-metadata runner, then resume this lane.