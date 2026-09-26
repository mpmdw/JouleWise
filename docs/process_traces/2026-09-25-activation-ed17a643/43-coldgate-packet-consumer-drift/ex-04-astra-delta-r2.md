```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Partial delta audit: committed parser tests pass, but computed-session custody replay and R2-7 remain incomplete; mandatory fresh probes, revert tests, and the importer sweep are unfinished.",
  "workspace": {
    "base_requested": "e02350ff",
    "base_mode": "descendant",
    "head_start": "80753b97b3ddf5af05ca4c13ff7396782471d872",
    "head_end": null,
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "FIX-FIRST",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "scripts/issue_calibration_acceptance_generation.py",
        "line": 358,
        "summary": "The computed-session dry-run loop authenticates committed verdicts without replaying custody or comparing the recorded verdict.",
        "evidence": "Executed source inspection found load_committed_verdict followed by status use, without validate_window or compare_verdict. The corresponding prepare-candidate loop performs all three checks.",
        "limitation": "The prepared deleted/tampered-custody behavioral reproducer was not executed before the final-report request."
      },
      {
        "id": "F2",
        "severity": "nit",
        "path": "docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/06-harvest-final-obligations-v1.1-source.md",
        "line": 170,
        "summary": "R2-7 remains open: the consumer list omits epoch_equivalence_check and still describes the superseded continuation gate.",
        "evidence": "Executed inspection returned false for the equivalence entry and continuation outright-refusal documentation. The fixture README update and C-3 banner are present."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 47 tests in 42.783s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_epoch_equivalence_check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 28 tests in 13.172s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_epoch_continuation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 68 tests in 59.236s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_revision_five_b_readers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 0.006s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 141 tests in 142.875s", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 71 tests in 42.973s", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "/usr/sbin/sysctl -n kern.osversion",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["sysctl: sysctl fmt -1 1024 1: Operation not permitted"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".+"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The final-report request arrived before the audit completed. The 22 fresh structural mutations, obligation revert tests, and custody-bypass reproducer were prepared but not executed. Only 30 of 69 inventoried modules had confirmed completion at the last checkpoint.",
      "needs": "Complete the outstanding probes, revert-and-restore tests, importer modules, and failure baseline replays before accepting this audit."
    },
    {
      "id": "G2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox denies sysctl identity reads. The issuer live-identity test failed, and two AXI modules reported campaign start identity unavailable.",
      "needs": "Verify these failures in an environment with the required read-only identity access."
    },
    {
      "id": "G3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The unchanged arm-readiness liveness test failed at 600 seconds plus 1 ns. The ruling already identifies this issue as open, but the prepared baseline replay was not executed.",
      "needs": "Preserve its separate disposition and complete the baseline replay."
    }
  ]
}
```

## Findings

**F1 — MATERIAL: computed sessions still lack custody replay in the dry run.**  
At [the computed-session loop](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/scripts/issue_calibration_acceptance_generation.py:358), `load_committed_verdict` is followed by use of the recorded status. The loop omits `validate_window` and `compare_verdict`, both required by R2-5 and present in candidate preparation.

Thus the missing-record fix does not close the entire consumer gate. This finding is established by source inspection; the prepared deleted/tampered-file reproduction remains **unexecuted**. It is retained as [bypass_probe.py](/tmp/bfgd-astra-r2-audit/bypass_probe.py).

**F2 — NIT: R2-7 bookkeeping remains unfinished.**  
[Obligations §4.5](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/06-harvest-final-obligations-v1.1-source.md:170) omits the equivalence tool and retains the former continuation-gate description. The fixture README and C-3 banner are present. The live sweep test also still labels the three repaired C-2 readers `UNGATED`.

No parser BLOCKER was established by the executed evidence. The committed battery module passed 47 tests, including its **15-positive/108-negative corpus**, four-site rejection checks, refusal-site mutation checks, and grammar pin tests. A fresh read-only `ioreg` capture also parsed successfully: 59 properties, 0 mA, fresh `UpdateTime`. The required independent fresh-mutation run remains outstanding.

The `25G99` fixture move is appropriate for the surviving tool mechanics. An AST comparison confirmed all 26 original equivalence-test assertion sets are unchanged. Continuation changes retain the mechanical checks while replacing Revision-5 gate expectations with the mandated outright refusal.

## Residual risk

This is a **partial report**, not a completed re-audit. At the last verified checkpoint, **30 modules had run 1,099 tests**, with six failures across four modules and 11 skips. The runner had started `tests.test_evidence_night`; subsequent results were not inspected before this final response.

| Completed module (`tests.` prefix) | Tests | Result |
|---|---:|---|
| `test_battery_float` | 47 | OK |
| `test_battery_float_sweep` | 2 | OK |
| `test_revision_five_b_readers` | 3 | OK |
| `test_epoch_equivalence_check` | 28 | OK |
| `test_epoch_continuation` | 68 | OK |
| `test_issue_calibration_acceptance_generation` | 141 | 1 failure: live identity unavailable |
| `test_validate_powermetrics_fiducial` | 12 | OK |
| `test_write_derivation_night_inputs` | 16 | OK |
| `test_controller` | 74 | OK |
| `test_paper_anchor_correction_quantified` | 12 | OK |
| `test_acc_25g83_rev5` | 12 | OK |
| `test_agent_census_concurrency` | 3 | 3 skipped |
| `test_analysis_integration` | 116 | OK |
| `test_arm_census` | 20 | OK |
| `test_arm_readiness` | 71 | 1 failure: existing liveness boundary |
| `test_arm_readiness_evidence_t0` | 78 | OK, 5 skipped |
| `test_arm_readiness_integration` | 13 | OK |
| `test_arm_readiness_lifecycle` | 69 | OK, 1 skipped |
| `test_arm_retry` | 36 | OK |
| `test_audit_amplification` | 8 | OK |
| `test_axi_controller_events` | 7 | 2 failures: start identity unavailable |
| `test_axi_mock_spec` | 11 | 2 failures: start identity unavailable |
| `test_calibration_cadence_report` | 9 | OK |
| `test_capture_t0_step` | 31 | OK |
| `test_cli` | 11 | OK |
| `test_cli_run` | 130 | OK |
| `test_corpus_strict_validation` | 3 | OK, 1 skipped |
| `test_determinism_gate` | 40 | OK, 1 skipped |
| `test_envelope_gate` | 27 | OK |
| `test_evidence_arm_sequence` | 1 | OK |

The [changed-path list](/tmp/bfgd-astra-r2-audit/changed.txt) comes from `git diff --name-only faf0ea01 e02350ff`. The [69-module importer census](/tmp/bfgd-astra-r2-audit/import-census.txt) includes AST imports and filename searches; a separate filename grep found no unclassified matches.

Outstanding work is preserved in [fresh_structural.py](/tmp/bfgd-astra-r2-audit/fresh_structural.py), [mutations.py](/tmp/bfgd-astra-r2-audit/mutations.py), and [baseline_failures.py](/tmp/bfgd-astra-r2-audit/baseline_failures.py). Their existence is **not execution evidence**.

The pin proof was empty. No repository files were modified. No full discovery, subagents, or live measurement campaign was run.

**FIX-FIRST**