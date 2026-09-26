```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-FIRST: an unnamed computed window with failed raw-byte custody receives a false admissible dry run; R2-7 bookkeeping remains open.",
  "workspace": {
    "base_requested": "faf0ea014e7320eb5758ab4ef4ceb0af60a09854",
    "base_mode": "descendant",
    "head_start": "80753b97b3ddf5af05ca4c13ff7396782471d872",
    "head_end": "80753b97b3ddf5af05ca4c13ff7396782471d872",
    "upstream_end": "e02350ff90430fc75716ff4ddbae0d49d813ea20",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FIX-FIRST",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "tier": "MATERIAL",
        "path": "scripts/issue_calibration_acceptance_generation.py:332",
        "summary": "The dry-run bound authenticates an unnamed computed session's verdict but skips raw-byte custody replay and compare_verdict; check says admissible while prepare-candidate refuses."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "tier": "MATERIAL",
        "path": "docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/06-harvest-final-obligations-v1.1-source.md:170",
        "summary": "R2-7 is incomplete: §4.5 omits epoch_equivalence_check and still specifies the removed Revision-5 continuation verdict gate."
      },
      {
        "id": "F3",
        "severity": "nit",
        "tier": "NIT",
        "path": "tests/test_battery_float_sweep.py:46",
        "summary": "The sweep inventory still labels all three C-2 readers UNGATED/NEEDS_SCOPE after their refusals landed."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgd_delta_import_sweep.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": ["SUMMARY 63 modules; 6 failed: test_arm_readiness,test_axi_controller_events,test_axi_mock_spec,test_issue_calibration_acceptance_generation,test_run_night,test_t0_rehearsal"]
      },
      "expected": {"exit_code": 0, "tail_regex": "SUMMARY 63 modules; 0 failed"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 47 tests in 45.979s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 47 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgd_delta_fresh_mutations.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS: 12 fresh structural mutations x parse/observe/night/dynamic/window"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS: 12 fresh structural mutations"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgd_delta_real_cli.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R2-2-equivalence rc 3", "R2-10-continuation rc 3", "C-2-backfill rc 2", "C-2-paper rc 3"]},
      "expected": {"exit_code": 0, "tail_regex": "C-2-paper rc 3"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgd_delta_custody_repro.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["check_rc 0", "check_admissible_yes True", "prepare_rc 3", "prepare_custody_refusal True", "candidate_exists False"]},
      "expected": {"exit_code": 0, "tail_regex": "candidate_exists False"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgd_delta_revert_checks.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R2-1 grammar exit 1", "R2-2 equivalence exit 1", "R2-3 dry-run exit 1", "R2-4 runbook flags exit 1", "R2-9 grammar pin exit 1", "R2-10 continuation exit 1", "R2-11 text stdout exit 1", "C-1 pin path exit 1", "C-2 B readers exit 1"]},
      "expected": {"exit_code": 0, "tail_regex": "C-2 B readers exit 1"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "B1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Six importer modules failed; their eight failing cases reproduced with the same assertions in a faf0ea01 export. The issuer failure is the unavailable live os_build; the others are two liveness boundaries, four campaign-start identity cases, and one blocked-journal timeout.",
      "needs": "Track separately from this delta."
    }
  ]
}
```

## Findings

**No parser BLOCKER.** The committed corpus ran: 15 positives and 108 negatives, with the negatives refused at `parse`/`observe`, both night gates, and `validate_window`. My 12 additional structural mutations were also refused at every site. A read-only live `ioreg` sample parsed successfully with 59 properties. The freeze pin and the specified pin proof passed.

- **F1 — MATERIAL.** In [the dry-run bound](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/scripts/issue_calibration_acceptance_generation.py:332), an unnamed computed session’s committed verdict is loaded without `validate_window` or `compare_verdict`. I built W1 and W2 with authentic passing verdicts, altered W1’s retained pre-probe bytes, and named only W2. The real `check` path exited **0** with `registration admissible for prepare-candidate: yes`; the real `prepare-candidate` path exited **3**, named W1’s custody failure, and wrote no candidate. This leaves the R2-5 consumer gate incomplete. The scripted replay is `/tmp/bfgd_delta_custody_repro.py`.

- **F2 — MATERIAL.** [Obligations v1.1 §4.5](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/06-harvest-final-obligations-v1.1-source.md:170) still omits the equivalence tool and says Revision-5 continuation uses the committed-verdict gate. Both tools now refuse Revision 5 outright. The fixture README portion of R2-7 is present; this consumer-list portion remains open.

- **F3 — NIT.** [The sweep inventory](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/tests/test_battery_float_sweep.py:46) still marks controller, backfill, and paper analysis `UNGATED` after C-2 added their refusals. Its green result checks the file inventory, so it does not establish that those gate descriptions are current.

The other closure checks held under focused `/tmp` reversions: R2-1, R2-2, R2-3, R2-4, R2-9, R2-10, R2-11, C-1, and C-2 tests failed when their fixes were removed. The old parser accepted the R2-8 wrong-type examples that the current parser refuses; removing the `FullyCharged` type check also failed the corpus test. C-3’s banner is present and absent at its pre-fix base. The equivalence, continuation, backfill, and paper-analysis refusals were reproduced through their CLI entry points. The test-mechanics fixtures’ move to hypothetical `25G99` preserves their assertions and gives the surviving tools a non-Revision-5 domain.

The `git diff --name-only faf0ea01 e02350ff` import scan covered these 63 test modules, including importers of the changed production files and fixture builders:

```text
test_acc_25g83_rev5 test_agent_census_concurrency test_analysis_integration
test_arm_census test_arm_readiness test_arm_readiness_evidence_t0
test_arm_readiness_integration test_arm_readiness_lifecycle test_arm_retry
test_audit_amplification test_axi_controller_events test_axi_mock_spec
test_battery_float test_battery_float_sweep test_calibration_cadence_report
test_cli test_cli_run test_controller test_corpus_strict_validation
test_custody_mode_inventory test_determinism_gate test_docs_freshness
test_envelope_gate test_epoch_continuation test_epoch_equivalence_check
test_evidence_arm_sequence test_evidence_night test_experiment
test_gate_sensibility_rounding test_gen_derivation_night test_gen_evidence_night
test_gen_state test_install_night_agent test_issue_calibration_acceptance_generation
test_launch_window test_magistrate_watchdog_cli test_mint_floor_artifact_generalized
test_night_agent_install test_night_gate test_night_kinds test_night_plan_writer
test_nvidia_node_integration test_p2038_production_path test_package_bundle_pack
test_paper_anchor_correction_quantified test_powermetrics
test_preregistration_chain_digest test_quiet_admission test_quiet_predicate_campaign
test_reduce test_report test_revision_five_b_readers test_rpt001_report_slice
test_run_night test_run_night_probe_cadence test_run_night_probe_worker_cadence
test_sample_quiet_predicate_evidence test_schemas test_t0_rehearsal
test_validate_powermetrics_fiducial test_validate_powermetrics_fiducial_derivation_only
test_window_env_allowlist test_write_derivation_night_inputs
```

**Verdict: FIX-FIRST.**

## Residual risk

Six modules in that sweep remain red in this environment. All eight failing cases reproduced at `faf0ea01` with the same assertions, so they do not establish a round-2 regression. No full discovery was run, as charged.