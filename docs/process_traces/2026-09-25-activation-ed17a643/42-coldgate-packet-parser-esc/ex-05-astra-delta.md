```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-FIRST: malformed battery objects still pass, computed-session authentication failures disappear from the dry run, and two runbook commands omit required flags.",
  "workspace": {
    "base_requested": "df33888f",
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
    "candidate": "faf0ea01",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "FX-1 still accepts wrong-class and malformed nested objects",
        "location": "joulewise/battery_float.py:22,124",
        "evidence": "Changing only the header's class to OtherBattery produced parsed passed=True, evaluate_night GO, dynamic-gate PENDING without rejection, and validate_window pass. A malformed nested dictionary also parsed passed=True."
      },
      {
        "id": "M1",
        "severity": "should_fix",
        "title": "Computed-session authentication failures are silently omitted",
        "location": "scripts/issue_calibration_acceptance_generation.py:358",
        "evidence": "Deleting omitted W1's committed verdict from the working tree made the dry run for W1-prime and W2 return 0 and registration admissible: yes; prepare-candidate returned 3 for W1's unauthenticated verdict."
      },
      {
        "id": "M2",
        "severity": "should_fix",
        "title": "FX-7 leaves documented check invocations unusable",
        "location": "docs/phase_2/derivation_night_runbook.md:2495,2950",
        "evidence": "Both documented flag shapes returned 5 on an authenticated Revision-5 fixture, with the blocker requiring --preregistration and --preregistration-sha256. The later runbook invocation explicitly promises exit 0."
      }
    ],
    "mutation_results": {
      "FX-1": "killed: 16 assertion failures",
      "FX-2-check-5": "killed: 2 assertion failures",
      "FX-2-writer": "killed: 1 assertion failure",
      "FX-3": "killed: 1 assertion failure",
      "FX-4": "killed: 1 assertion failure",
      "FX-5": "killed: 1 assertion failure",
      "FX-6": "killed: 1 assertion failure",
      "FX-7-cadence": "killed: 1 assertion failure",
      "FX-7-continuation": "killed: 2 assertion failures",
      "FX-8": "killed: 1 assertion failure",
      "FX-9": "killed: 1 assertion failure"
    },
    "pin_proof": "Required c6814dd8-to-faf0ea01 protected-path diff is empty.",
    "registry_seam": "Lead condition satisfied: the three registry-pin tests passed, including the unpatched production digest check and altered-registry refusal."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_battery_float tests.test_calibration_cadence_report tests.test_issue_calibration_acceptance_generation.BatteryFloatRevisionFiveTests tests.test_acc_25g83_rev5.RevisionFiveTests.test_tracked_registry_digest_is_the_pinned_constant tests.test_acc_25g83_rev5.RevisionFiveTests.test_an_appended_row_under_the_fixed_id_refuses_on_digest tests.test_acc_25g83_rev5.RevisionFiveTests.test_a4_route_refuses_on_digest_and_the_tracked_registry_refuses_on_a7",
      "cwd": "/tmp/bfg-delta-astra-ub8g2ihp",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 70 tests in 64.190s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B delta_repros.py",
      "cwd": "/tmp/bfg-delta-astra-ub8g2ihp",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OMITTED_NO_RECORD_CHECK 0 registration admissible for prepare-candidate: yes",
          "OMITTED_NO_RECORD_PREPARE 3 REFUSED: battery-float harvest verdict missing or uncommitted for W1: working tree differs from HEAD; not issued",
          "INVENTORY_ALL 2",
          "INVENTORY_SKIP_REFUSED session W1: --window capture paths disagree with ledger inventory"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "INVENTORY_SKIP_REFUSED"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B delta_mutations.py",
      "cwd": "/tmp/bfg-delta-astra-ub8g2ihp",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ALL_SIX_MUTATIONS_KILLED"]
      },
      "expected": {"exit_code": 0, "tail_regex": "ALL_SIX_MUTATIONS_KILLED"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B delta_more_mutations.py",
      "cwd": "/tmp/bfg-delta-astra-ub8g2ihp",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ALL_FIVE_ADDITIONAL_MUTATIONS_KILLED"]
      },
      "expected": {"exit_code": 0, "tail_regex": "ALL_FIVE_ADDITIONAL_MUTATIONS_KILLED"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night.NightDriverTests.test_production_battery_probe_uses_ten_second_timeout_only_for_ioreg tests.test_epoch_continuation.EpochContinuationTests.test_revision_five_registration_digest_missing_or_wrong_refuses tests.test_epoch_continuation.EpochContinuationTests.test_revision_five_session_refuses_without_a_record_or_on_custody_failure tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census",
      "cwd": "/tmp/bfg-delta-astra-ub8g2ihp",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 4 tests in 2.272s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --stat c6814dd8 faf0ea01 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs",
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
      "text": "Supplemental cases were appended to the temporary repro script after V2, but were not executed before the immediate-return request. Their prospective results are not claimed.",
      "needs": ""
    }
  ]
}
```

## Findings

**B1 — BLOCKER: the original structural-parser finding survives FX-1.**

The header regex authenticates the object’s displayed name but accepts arbitrary text inside `<…>`. Replacing only `class AppleSmartBattery` with `class OtherBattery` retained `passed=True`, reached `GO` through `evaluate_night`, passed the dynamic battery gate (`PENDING`, rather than a refusal), and produced window status `pass`.

The nested-depth handling also skips nested property-opening lines while already inside a dictionary. A second dictionary’s closing brace therefore prematurely returns parsing to top level. Executed malformed input containing an unclosed outer dictionary and required properties inside it returned `passed=True`.

The new regression tests kill a full reversion but miss both surviving counterexamples. Authenticate the actual class field and track nested structure correctly.

**M1 — MATERIAL: authentication failures disappear from the computed session set.**

`_dry_run_epoch_bound` catches `NoRecord` and continues. With W1 omitted from the requested registration and its verdict deleted from the working tree:

- `check`’s dry run returned **0**, `registration admissible for prepare-candidate: yes`.
- `prepare-candidate` returned **3**, refusing W1’s verdict because its working-tree bytes differed from HEAD.

This preserves the false-admissibility signature behind FX-6 and weakens FX-7 for computed sessions: an authentication failure removes the session from consideration instead of blocking. Propagate those failures as blockers.

**M2 — MATERIAL: two runbook commands lack FX-7’s required flags.**

Runbook §2.2 still supplies only `--session-ids`; the later registration preflight supplies `--preregistration` but omits its digest. Both flag shapes returned **5** with the required-registration blocker. The later passage explicitly promises **rc 0**.

Update both invocations. The corrected §2.2a invocation does not repair these other entry points.

The remaining closure evidence is:

| FX | Re-audit result |
|---|---|
| 1 | **Incomplete:** B1 above; original regression mutation killed. |
| 2 | End-to-end fixture passed; writer and check-5 mutations killed. Wrong digest, stale sequence, future sequence, and alternate pin path all refused without writing a record. |
| 3 | Merge-history regression passed; reverting full-history authentication failed it. |
| 4 | Swap, extra-capture, and tamper tests passed. An inventory containing valid and ordinary-invalid finalized rows reported both; supplying only one refused. Mutation killed. |
| 5 | Missing-verdict member-read guard passed and killed its mutation. |
| 6 | Required omitted-non-pass test passed and killed its mutation; related authentication gap remains as M1. |
| 7 | Missing/wrong-digest tests passed for the named consumers; cadence and continuation mutations killed. Computed-session and documentation gaps remain. |
| 8 | Clean-environment CLI bootstrap passed; removing it failed the test. |
| 9 | Mocked production wiring recorded 10 seconds for battery ioreg and unchanged 30 seconds for the control command. Mutation killed. The conditional override leaves other argv unchanged by inspection. |
| 10–11 | Required bracket-test reference, 610-second documentation, and fixture `.gitattributes` are present. Liveness arithmetic test passed. |

The registry-seam condition is satisfied, and the protected scientific/configuration diff is empty. No repository files were modified.

## Residual risk

The sibling search also identified `epoch_equivalence_check`: it reads member evidence and computes results without the battery-verdict gate. That route was inspected but not behaviorally reproduced before the immediate-return request; it warrants a focused follow-up, especially if Revision-5 sessions remain accepted by this older tool.

No full discovery or live hardware validation was performed, as charged. Supplemental temporary-script additions were not executed and support no claimed result.

**FIX-FIRST.**