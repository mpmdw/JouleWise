```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-FIRST: a Revision 5 result reader still bypasses the harvest-verdict gate, and two runbook commands now fail.",
  "workspace": {
    "base_requested": "df33888ff145a7153e25f171e84dc49945edf4bd",
    "base_mode": "descendant",
    "head_start": "1fda46c14deff8d0074a65af59b486593131ffac",
    "head_end": "1fda46c14deff8d0074a65af59b486593131ffac",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FIX-FIRST",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "scripts/epoch_equivalence_check.py:608",
        "title": "Equivalence check reads Revision 5 B values without a committed harvest verdict",
        "evidence": "In a Revision 5 fixture with no verdict file, the checker wrote an equivalence record containing b_fiducial_s='0.03'. This is a surviving sibling of the pre-verdict read finding."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "location": "docs/phase_2/derivation_night_runbook.md:2495",
        "title": "Two documented check invocations omit required Revision 5 flags",
        "evidence": "The §2.2 and §4.1 command shapes each returned rc 5 with '--preregistration and --preregistration-sha256 are required'."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "cd /tmp/bfgd-delta-bym8xqah && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float tests.test_calibration_cadence_report tests.test_issue_calibration_acceptance_generation.BatteryFloatRevisionFiveTests.test_terminal_uncommitted_pin_verdict_commit_and_three_cli_consumers tests.test_issue_calibration_acceptance_generation.BatteryFloatRevisionFiveTests.test_dry_run_never_reads_member_evidence_without_authentic_verdict tests.test_issue_calibration_acceptance_generation.BatteryFloatRevisionFiveTests.test_dry_run_blocks_one_computed_non_pass_session_omitted tests.test_issue_calibration_acceptance_generation.BatteryFloatRevisionFiveTests.test_check_requires_registration_file_and_matching_digest tests.test_run_night.NightDriverTests.test_production_battery_probe_uses_ten_second_timeout_only_for_ioreg tests.test_epoch_continuation.EpochContinuationTests.test_revision_five_registration_digest_missing_or_wrong_refuses",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 50 tests in 24.214s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 50 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "cd /tmp/bfgd-delta-bym8xqah && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_acc_25g83_rev5.RevisionFiveTests.test_tracked_registry_digest_is_the_pinned_constant tests.test_acc_25g83_rev5.RevisionFiveTests.test_an_appended_row_under_the_fixed_id_refuses_on_digest tests.test_acc_25g83_rev5.RevisionFiveTests.test_a4_route_refuses_on_digest_and_the_tracked_registry_refuses_on_a7",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 4.260s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 /tmp/bfgd_mutation_runner.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["=== FX-9 exit=1 ===", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "FX-9 exit=1[\\s\\S]*FAILED \\(failures=1\\)"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "cd /tmp/bfgd-delta-bym8xqah && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/bfgd_delta_probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "equivalence_without_verdict False 5 ['0.03']",
          "section_2_2 5 ['blocker: session derivation-night-1: --preregistration and --preregistration-sha256 are required']",
          "section_4_1 5 ['blocker: session derivation-night-1: --preregistration and --preregistration-sha256 are required']",
          "omitted_plist session derivation-night-1: --window capture paths disagree with ledger inventory",
          "different_digest 3 REFUSED: ledger: calibration_ledger_head_mismatch",
          "stale_genesis 3 REFUSED: ledger: calibration_ledger_head_mismatch"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "stale_genesis 3 REFUSED: ledger: calibration_ledger_head_mismatch"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --stat c6814dd8 faf0ea01 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The charge prohibited full discovery and live machine work; this seat ran focused checks in a temporary copy.",
      "needs": ""
    }
  ]
}
```

## Findings

**BLOCKER F1.** [epoch_equivalence_check.py](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/scripts/epoch_equivalence_check.py:608) reaches member evidence without checking the committed battery verdict. An executed Revision 5 fixture had no verdict file, yet the checker wrote `b_fiducial_s: 0.03` to its output record. This read path predates the fix round and survives the same-signature audit. Gate Revision 5 evaluation before reading member evidence.

**MATERIAL F2.** The [runbook](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/docs/phase_2/derivation_night_runbook.md:2495) still shows `check` commands in §§2.2 and 4.1 without the now-required digest; §2.2 also omits the preregistration file. Both documented command shapes returned rc 5 on a Revision 5 fixture. Update both invocations and their expected-result text.

The six required `/tmp` mutations—FX-1, FX-2 check 5, FX-3, FX-4, FX-5, and FX-9—each made its targeted test fail. The unmutated focused run passed 50 tests. The FX-2 end-to-end test passed; the separate registry-pin tests passed on the unpatched digest path. Mismatched and stale working-tree pins refused, an omitted finalized plist refused, and the FX-9 test confirmed the other probe retained its 30-second timeout. The requested `c6814dd8` pin diff was empty. **Verdict: FIX-FIRST.**

## Residual risk

The lead’s reported 379-test run, including live identity, was not repeated here; the charge prohibited full discovery and live machine work.