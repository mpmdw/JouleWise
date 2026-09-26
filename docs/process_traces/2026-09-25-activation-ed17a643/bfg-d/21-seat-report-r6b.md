```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented C-1, C-2, and C-3; one environment-dependent test in the required sweep remains unverified.",
  "workspace": {
    "base_requested": "f5525aac",
    "base_mode": "descendant",
    "head_start": "0c5b8ded64fc942c90716c448288bc86ed91f229",
    "head_end": "0c5b8ded64fc942c90716c448288bc86ed91f229",
    "upstream_end": "0c5b8ded64fc942c90716c448288bc86ed91f229",
    "branch": "feat/2026-09-25-bfg-d"
  },
  "pathspec": [
    "tests/test_validate_powermetrics_fiducial.py",
    "tests/test_write_derivation_night_inputs.py",
    "tests/test_revision_five_b_readers.py",
    "scripts/calibration_ledger_backfill.py",
    "scripts/paper_anchor_correction_quantified.py",
    "joulewise/controller.py",
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "C1-RED",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_validate_powermetrics_fiducial.ContinuedEpochPreflightTests",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 12 tests in 7.717s", "FAILED (failures=5)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "C1-GREEN",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_validate_powermetrics_fiducial.ContinuedEpochPreflightTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 12 tests in 7.455s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "C2-RED",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_revision_five_b_readers",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 3 tests in 0.008s", "FAILED (failures=6)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "C2-GREEN",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_revision_five_b_readers",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 0.006s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "C3-RED",
      "kind": "inspection",
      "cmd": "git show f5525aac:docs/phase_2/derivation_night_runbook.md | rg -q 'Revision 5 route for epoch 25G83'",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "C3-GREEN",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 31 tests in 0.449s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "SWEEP-ISSUER",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 141 tests in 124.119s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "PIN",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float.GrammarFreezeTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 0.012s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The required issuer-module sweep has one live-probe failure: observe_machine returned os_build=None despite the macOS sysctl path existing. Its test and implementation are unchanged from f5525aac.",
      "needs": "Lead rerun the live-probe test in an environment where sysctl identity is available."
    }
  ]
}
```

## Change

- **C-1:** [The continuation preflight helper](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_validate_powermetrics_fiducial.py:48) now reads the fixture’s committed head pin at its current path. RED: 5 failures; GREEN: 12 tests OK. The importer sweep also exposed a mock using the old epoch; [that mock](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_write_derivation_night_inputs.py:103) now uses the continuation fixture’s epoch. RED: 1 failure; GREEN: 16 tests OK. Assertions were unchanged.
- **C-2:** [Backfill](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/scripts/calibration_ledger_backfill.py:47), [paper analysis](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/scripts/paper_anchor_correction_quantified.py:709), and the [controller attachment](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/joulewise/controller.py:438) refuse Revision-5 identity or a `battery_float` key before using B. The [Revision-5 fixture regressions](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_revision_five_b_readers.py:38) were RED with 6 subtest failures against code identical to `f5525aac`, then GREEN with 3 tests OK.
- **C-3:** The [runbook banner](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/docs/phase_2/derivation_night_runbook.md:2644) identifies the Revision-5 route while retaining the historical text. Banner check: RED at `f5525aac`, GREEN here; docs freshness: 31 tests OK.

## Verification notes

The required fixture-import sweep tails were:

| Module | Tail |
|---|---|
| `tests.test_acc_25g83_rev5` | Ran 12 tests in 14.617s — OK |
| `tests.test_calibration_cadence_report` | Ran 9 tests in 1.876s — OK |
| `tests.test_epoch_continuation` | Ran 68 tests in 50.221s — OK |
| `tests.test_epoch_equivalence_check` | Ran 28 tests in 11.032s — OK |
| `tests.test_validate_powermetrics_fiducial_derivation_only` | Ran 27 tests in 204.492s — OK |
| `tests.test_validate_powermetrics_fiducial` | Ran 12 tests in 7.497s — OK |
| `tests.test_issue_calibration_acceptance_generation` | Ran 141 tests in 124.119s — FAILED (failures=1) |
| `tests.test_write_derivation_night_inputs` | RED: Ran 16 tests in 0.686s — FAILED (failures=1); GREEN: Ran 16 tests in 0.671s — OK |

Existing reader checks passed: `tests.test_paper_anchor_correction_quantified` (12 OK), `tests.test_controller` (74 OK), and `tests.test_p2038_production_path` (8 OK). The final focused run passed 64 tests. `git diff --check` passed.

**Pin proof:** `git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs` was empty. The battery grammar was untouched, and its freeze tests passed. Changes remain uncommitted.

## Residual risk

The issuer module’s sole failure is `test_live_probes_report_this_machine_against_the_active_epoch`: `os_build` was `None` in this environment. The lead needs to rerun that live-probe test where macOS identity probing is available.