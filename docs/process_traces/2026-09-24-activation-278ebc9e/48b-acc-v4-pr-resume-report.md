```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Revision 4 validator and historical protocol fixes are complete; replay passes and every remaining V1 failure is an r7 digest-pin failure.",
  "workspace": {
    "base_requested": "8379b1ea",
    "base_mode": "exact",
    "head_start": "8379b1ea96e77c328214bd7eb98ca2706af6696b",
    "head_end": "8379b1ea96e77c328214bd7eb98ca2706af6696b",
    "upstream_end": "8379b1ea96e77c328214bd7eb98ca2706af6696b",
    "branch": "feat/2026-09-24-acc-25g83-v4-rev4"
  },
  "pathspec": [
    "configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
    "joulewise/calibration_bracketing.py",
    "scripts/issue_calibration_acceptance_generation.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_issue_calibration_acceptance_generation.py",
    "tests/test_powermetrics_fiducial.py",
    "tests/test_reduce.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_issue_calibration_acceptance_generation tests.test_calibration_ledger tests.test_calibration_exits tests.test_reduce tests.test_run_campaign tests.test_generate_g2a_probe_inputs tests.test_calibration_custody_store tests.test_calibration_writer_crash_matrix tests.test_powermetrics_fiducial tests.test_validate_powermetrics_fiducial tests.test_validate_powermetrics_fiducial_derivation_only tests.test_preregistration_chain_digest tests.test_reissue_calibration_acceptance tests.test_arm_readiness tests.test_acc_25g83_v4_rev4",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 933 tests in 880.723s",
          "FAILED (failures=40, errors=7, skipped=3)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=40, errors=7, skipped=3\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_acc_25g83_v4_rev4 tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests tests.test_calibration_bracketing.RevisionFourEnvelopeValidatorTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 47 tests in 9.145s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
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
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\np=Path('docs/process_traces/2026-09-24-activation-278ebc9e/37-acc-stale-number-audit.md')\ns=p.read_text()\nitems=('0.032898493715362','0.009724','0.010165','0.010818','calibration_bracket_max_drift_s')\nprint('audit:', 'PASS' if all(x in s for x in items) else 'FAIL')\nfor x in items: print(x, 'present' if x in s else 'MISSING')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "audit: PASS",
          "0.032898493715362 present",
          "0.009724 present",
          "0.010165 present",
          "0.010818 present",
          "calibration_bracket_max_drift_s present"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "audit: PASS"
      }
    },
    {
      "id": "REPLAY",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/wt-278ebc9e-accv4 python3 -B -c 'import sys, runpy; from joulewise import powermetrics_fiducial as detector; assert detector.PULSE_DURATION_S == 2.0; sys.argv = [\"replay.py\", \"--output\", \"/tmp/accv4-replay-results-final.json\"]; runpy.run_path(\"/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py\", run_name=\"__main__\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "n2-d12  fitted=True recorded=[] v3=[] comparison=exact_match v4=[]",
          "R-ACC-1(b): PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R-ACC-1\\(b\\): PASS"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "All 47 remaining V1 failure/error outcomes are caused by comparisons with r7's protocol_sha256 or estimator_code_sha256; 41 distinct tests are listed below.",
      "needs": "Magistrate performs the separately ruled r8 science-neutral reissue."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The live macOS identity test skips because this sandbox denies sysctl; its mocked probe tests pass.",
      "needs": ""
    }
  ]
}
```

## Change

The approved E1 validator change is in [calibration_bracketing.py](/Users/edr/code/wt-278ebc9e-accv4/joulewise/calibration_bracketing.py:273): the 12-member floor and `C = max(predecessor C, Q99, S)` apply only to the exact 25G83/v4 epoch; `C = S` admits zero headroom. Historical v3 evidence remains admissible, and the validator accepts the ruled r8 shape with v3 identity and a v4 protocol pin. [Regression tests](/Users/edr/code/wt-278ebc9e-accv4/tests/test_calibration_bracketing.py:4098) cover those branches.

| Ruled item | Implementation |
|---|---|
| 1(a) | v4 identity, 2.0 s pulse and 1.8–2.2 s authentication in [fiducial.py](/Users/edr/code/wt-278ebc9e-accv4/joulewise/powermetrics_fiducial.py:46), [protocol_v4.json](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/powermetrics_fiducial/protocol_v4.json:1), and [run-bundle contract](/Users/edr/code/wt-278ebc9e-accv4/docs/contracts/run_bundle_layout.md:615). |
| 2(a), 2(b) | Epoch, seal inputs and two-window schedule in [Revision 4](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:608). |
| 2(c) | Epoch-scoped n ≥ 12 in [issuer](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:372), [validator](/Users/edr/code/wt-278ebc9e-accv4/joulewise/calibration_bracketing.py:538), and [D-126 addendum](/Users/edr/code/wt-278ebc9e-accv4/docs/decision_log.md:8485). |
| 2(d), 2(e) | Count-only W3, futility and blindness in [Revision 4](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:616). |
| 2(f) | Disclosed inputs and the cold replay addendum’s **verbatim** anchor-failure sentence in [Revision 4](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:625). |
| 2(g), 2(h) | Diagnostic-only old screen challenge, excursion label and >0.25 s refusal in [issuer](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:1393). |
| 2(i) | Zero-headroom issuance in [issuer](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:1434), matching validator rule and [D-125 addendum](/Users/edr/code/wt-278ebc9e-accv4/docs/decision_log.md:8457). |
| 2(j), 2(l) | All five stale numbers in the [audit](/Users/edr/code/wt-278ebc9e-accv4/docs/process_traces/2026-09-24-activation-278ebc9e/37-acc-stale-number-audit.md:5); barrier basis in [Revision 4](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:651). |
| 3(c) | Per-window native-frame cadence flag in [reduce.py](/Users/edr/code/wt-278ebc9e-accv4/joulewise/reduce.py:441), emitted at lines 3343 and 3708. |
| 7 | Registration and protocol digest seal mechanism in [Revision 4](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:612). |

The real V1 failures from the first run were fixed: historical night-count wording, v3 candidate/r8 protocol-pin validation, historical v3 evidence bytes, and the reducer golden’s comparison with the additive cadence flag. The live-probe test now skips only when the sandbox denies `sysctl`. Changes remain **uncommitted**; no issued artifact or fixture was edited.

## Verification notes

Replay verdict: **PASS** — 22/22 fitted v3 captures match their recorded miss indices, two captures are correctly labelled unfitted, and v4 has **0/1,416** interior misses. The wrapper pre-imported this worktree’s detector because the archived script inserts its own checkout ahead of `PYTHONPATH`; output went to `/tmp`.

For V1, **P** means r7’s `protocol_sha256`; **E** means r7’s `estimator_code_sha256` for `powermetrics_fiducial.py` and `reduce.py`. The remaining failed tests are:

- **P only:** `tests.test_powermetrics_fiducial`: `test_main_preserves_symlinked_custody_spelling_used_by_reservation`.
- **E only:** `tests.test_powermetrics_fiducial`: `test_preflight_screen_is_derived_bit_exactly_from_real_artifact`; `tests.test_reduce`: `test_d138_reduce_source_bytes_remain_at_issued_pin`.
- **P/E preflight guard — `tests.test_calibration_ledger`:** `test_recover_cli_refuses_a_slot_outside_the_declared_list`.
- **P/E preflight guard — `tests.test_calibration_exits`:** `test_abort_witness_payload_survives_nonowned_sampler_census_decoy`, `test_logical_producer_delay_preserves_exact_evidence_bytes`, `test_parameterized_durable_public_cli_witnesses`, `test_correct_preflight_registry_executes_every_correction_surface`, `test_enum_inventory_and_discovered_executed_witnesses_are_exact_sets_per_class`, `test_every_hard_stop_has_pre_handler_preservation_evidence`, `test_internal_off_ledger_candidate_guard_raise_path`.
- **P/E preflight guard — `tests.test_calibration_writer_crash_matrix`:** `test_ambient_writer_crash_stage_is_inert_without_capability`, `test_derivation_resume_finalize_never_uses_the_prior_epoch_screen`, `test_detection_budget_refuses_with_terminal_custody_and_released_lease`, `test_every_exact_stage_pre_and_post_sigkill_reaches_fresh_governed_exit`, `test_post_detection_budget_has_terminal_custody_and_released_lease`, `test_torn_and_fsynced_append_boundaries_resume_from_fresh_processes`, `test_two_process_lease_contention_then_fresh_resume`.
- **P/E preflight guard — `tests.test_powermetrics_fiducial`:** `test_acceptance_artifact_refusals_are_distinct_and_emit_no_output`.
- **P/E preflight guard — `tests.test_validate_powermetrics_fiducial`:** `test_contract_documented_key_lists_equal_emitted_preflight_and_screen_basis`, `test_derivation_basis_forwards_snapshot_and_refuses_unbacked_continuation`, `test_derivation_basis_lists_original_and_continued_judged_epochs`, `test_g2a_live_vectors_use_real_continuation_preflight`, `test_ordinary_preflight_accepts_continuation_with_unchanged_screen`, `test_snapshot_preflight_authenticates_terminal_session_and_records_basis`, `test_derivation_only_cli_uses_snapshot_before_epoch_guard`, `test_derivation_only_refuses_continued_epoch_before_capture`, `test_invalid_acceptance_id_returns_named_cli_refusal_without_traceback`, `test_snapshot_preflight_refuses_absent_or_nonterminal_continuation_session`, `test_unregistered_or_rotated_continuation_refuses_with_epoch_reason`.
- **P/E preflight guard — `tests.test_validate_powermetrics_fiducial_derivation_only`:** `test_bracket_kind_session_refuses_a_derivation_only_capture`, `test_capture_succeeds_with_the_night_budget_marker_inherited`, `test_derivation_slot_of_a_differing_epoch_appends_valid_with_provenance`, `test_ordinary_artifact_top_level_key_sets_require_deliberate_schema_changes`, `test_ordinary_continued_epoch_capture_requires_registered_continuation`, `test_ordinary_mode_refuses_a_derivation_kind_slot_and_appends_nothing`, `test_success_receipt_carries_the_healthy_custody_timing`, `test_matching_identity_epoch_refuses_because_derivation_only_would_bypass_the_screen`, `test_standalone_derivation_only_refuses_without_a_declared_session_slot`, `test_writer_stall_under_the_inherited_night_marker_still_times_out`, `test_writer_under_lease_stall_preserves_open_session`.

Those are 41 distinct tests and 47 V1 outcomes because several have subtests. **NEEDS_RULING: none.**

## Residual risk

The separately ruled **r8 science-neutral reissue** must repin the active protocol and estimator digests before live derivation capture. This seat did not create r8.