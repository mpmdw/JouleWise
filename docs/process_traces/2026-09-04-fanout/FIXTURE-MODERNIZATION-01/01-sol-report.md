```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Modernized arm-readiness fixtures to emit registry-governed R1 content and execution receipts, restored the blocked fixture paths, and proved stale-boot and authenticated predecessor behavior with focused tests.",
  "workspace": {
    "base_requested": "origin/main@849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "base_mode": "exact",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-FIXTURE-MODERNIZATION-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/FIXTURE-MODERNIZATION-01/01-sol-report.md",
    "tests/test_arm_readiness_dry_run.py",
    "tests/test_arm_readiness_evidence_t0.py",
    "tests/test_arm_readiness_integration.py",
    "tests/test_arm_readiness_lifecycle.py",
    "tests/test_s0_blocked_enumeration.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_dry_run 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "..",
          "----------------------------------------------------------------------",
          "Ran 10 tests in 75.507s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_integration 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".......",
          "----------------------------------------------------------------------",
          "Ran 10 tests in 94.614s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_lifecycle 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "............",
          "----------------------------------------------------------------------",
          "Ran 66 tests in 112.295s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 66 tests in .*s\\n\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_evidence_t0 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".............",
          "----------------------------------------------------------------------",
          "Ran 66 tests in 406.923s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 66 tests in .*s\\n\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_s0_blocked_enumeration 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 1.398s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s\\n\\nOK"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
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
      "id": "V7",
      "kind": "inspection",
      "cmd": "python3 -c 'import subprocess; groups={\"frozen\":[\"joulewise/powermetrics_fiducial.py\",\"joulewise/uncertainty_evidence.py\",\"joulewise/adapters/powermetrics.py\",\"joulewise/reduce.py\"],\"forbidden\":[\"docs/process/state_kernel.json\",\"TASK_QUEUE.md\",\"RUN_STATE.md\",\"docs/decision_log.md\",\"docs/paper/draft-v2-skeleton.md\"]}; [print(f\"{name}_unchanged={subprocess.run([chr(103)+chr(105)+chr(116),chr(100)+chr(105)+chr(102)+chr(102),chr(45)+chr(45)+chr(113)+chr(117)+chr(105)+chr(101)+chr(116),chr(72)+chr(69)+chr(65)+chr(68),chr(45)+chr(45),*paths]).returncode == 0}\") for name,paths in groups.items()]'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "frozen_unchanged=True",
          "forbidden_unchanged=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "frozen_unchanged=True\\nforbidden_unchanged=True"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The kernel acceptance still names an authenticated _v4-to-_v3 predecessor proof, while the current governed registry and tests install _v5 and authenticate its _v3 predecessor.",
      "needs": "The magistrate should update docs/process/state_kernel.json to name the currently installed _v5-to-_v3 chain; that file was intentionally not edited here."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The restricted macOS environment denies the kern.bootsessionuuid sysctl, so the real-boot variant remains skipped; the synthetic full transaction and stale-boot invalidation paths pass.",
      "needs": "Replay tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go in an ordinary macOS process if real sysctl coverage is required."
    }
  ]
}
```

## Change

The fixture author now builds the two revision-one (R1) generic evidence forms selected by the evidence-class registry: a content receipt for facts that can be reproduced from committed bytes, and an execution receipt for facts bound to a particular execution. Content facts are re-derived with the production doctrine-pin and pack-family derivation functions. Execution facts use the registry's policy, dependencies, boot identity, time horizon, and calibration-plan fingerprint. Inapplicable rows are omitted, and the freeze ordinal is derived from the authenticated predecessor rather than hard-coded.

The surrounding fixtures now preserve the caller's stage graph, install the governed closeout backup requirement, restrict the older temporal-evidence helper to arm-only rows, and derive each horizon from its registry entry. Family publication is supplied through an explicitly authenticated synthetic marker at the fixture boundary. The lifecycle coverage now proves that an arm receipt from a prior boot is rejected for both verification and consumption. The historical coverage uses the production freeze generator to mint the current successor and checks that the receipt names and hashes the authenticated predecessor.

The forcing problem was that the exact readiness gate rejects the former generic fixture schema before downstream behavior can be tested. Three designs were considered: bypass the gate, reproduce a complete external evidence-authoring run in every test, or build registry-shaped fixture receipts while retaining real re-derivation for reproducible content. Gate bypass would not test the contract, and complete external runs would couple unit tests to unrelated machinery. The implemented recommendation is the third design. For example, a doctrine-pin fixture receipt carries the committed derivation and dependency manifest without a boot deadline, while an execution-bound receipt carries the boot identity and registry-derived horizon. The counterfactual test `test_passing_freeze_fixture_authors_only_r1_generic_receipts` requires the exact R1 schema set, so restoring the legacy serializer fails directly.

| Finding or decision | Evidence | Disposition |
|---|---|---|
| Legacy generic fixture receipts were the common readiness blocker. | V1–V5 reach the intended dry-run, integration, lifecycle, temporal, and blocked-census assertions. | Replaced with registry-governed R1 fixture receipts. |
| Stale boot state must invalidate both read and consume operations. | V3 includes the end-to-end stale-boot lifecycle test. | Implemented and passing. |
| Historical proof must use the authenticated installed chain. | V3 includes production successor minting and predecessor digest assertions. | Implemented for the governed `_v5 → _v3` chain. |
| The kernel's `_v4 → _v3` wording is stale. | Current registry and test-family declarations install `_v5`; F1 records the mismatch. | Magistrate metadata correction requested; no code ruling needed. |
| Real boot-session lookup is unavailable in this sandbox. | V4 passes with the single real-sysctl variant skipped; F2 gives the replay target. | Synthetic transaction and stale-boot acceptance are complete; optional bench replay remains. |

## Verification notes

The repository-wide unit-test suite was not run, as required by the preflight rule. Only the modified fixture modules and their focused blocked-census module were executed. The lifecycle module's remaining skip is the pre-existing gate-shadowing structural case. The temporal-evidence module's remaining skip is the real macOS boot-session lookup described in F2; the synthetic boot-session transaction, synthetic clock, and changed-boot rejection tests all ran.

## Residual risk

The implementation does not alter production evidence logic; it exercises that logic through richer synthetic repositories. A normal macOS replay can add host-sysctl coverage, and the magistrate should align the protected kernel row with the already-governed `_v5 → _v3` family name.
