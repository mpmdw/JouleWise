# PR #456: Sol 6.1 executing review (codex-run-v3, gpt-6.1-sol, effort high, detached worktree at 7a9bdf93, WRITE_SCOPE [])

Lead follow-up on flag F1: the live epoch-probe test (DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch) passes outside the sandbox at 7a9bdf93: 'Ran 1 test ... OK'.

Verbatim report:

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "MERGE: custody binding is correct for authenticated inputs; Revision 5 is unchanged; one suite failure reproduces on base under sandbox restrictions.",
  "workspace": {
    "base_requested": "420e1f07d51f04e4a51f30d3b1e794a1fdd90131",
    "base_mode": "exact",
    "head_start": "7a9bdf93e18d13067686f6fec0d95d01f6a95903",
    "head_end": "7a9bdf93e18d13067686f6fec0d95d01f6a95903",
    "upstream_end": "66ee84f68a32ab9bb288c8af2c7c156deed29679",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGE",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_rev6_custody_plan_id tests.test_issue_calibration_acceptance_generation tests.test_issuer_corpus_root tests.test_acc_25g83_rev6 tests.test_acc_25g83_rev5 tests.test_harvest_window tests.test_rev6_prior_start_plan_id tests.test_revision6_seal > /tmp/pr456-required-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 262 tests in 347.661s", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "git show 420e1f07:scripts/issue_calibration_acceptance_generation.py > /tmp/pr456-base-issuer.py\n/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/pr456-base-tests.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["BASE_RESULT ran=9 failures=2 errors=7 skipped=0"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "BASE_RESULT ran=9 failures=2 errors=7 skipped=0"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/pr456-adversarial.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ADVERSARIAL_RESULT checks=44 PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "ADVERSARIAL_RESULT checks=44 PASS"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/pr456-prepare-cases.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PREPARE_ADVERSARIAL cases=16 PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PREPARE_ADVERSARIAL cases=16 PASS"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/pr456-rev5-bytes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["REV5_FULL_CANDIDATE artifact_bytes=IDENTICAL stdout=IDENTICAL verify_output=IDENTICAL PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "REV5_FULL_CANDIDATE .* PASS"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/pr456-full-tamper.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["FULL_ARTIFACT_TAMPER verify_exit=0 members_pass=24 stale_artifact_digest=YES unchanged_prior=YES"]
      },
      "expected": {"exit_code": 0, "tail_regex": "FULL_ARTIFACT_TAMPER verify_exit=0 members_pass=24 .*"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/pr456-base-tests.py tests.test_issue_calibration_acceptance_generation.DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: None is not an instance of <class 'str'>",
          "BASE_RESULT ran=1 failures=1 errors=0 skipped=0"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "BASE_RESULT ran=1 failures=0 errors=0 skipped=0"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sole required-suite failure is the live epoch-probe test at tests/test_issue_calibration_acceptance_generation.py:352. It fails identically on base: os_build is None because sysctl kern.osversion returns Operation not permitted in this sandbox.",
      "needs": "Lead rerun the live identity-probe test in an unrestricted macOS session for a fully green suite."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "verify-members at scripts/issue_calibration_acceptance_generation.py:3290 and :3335 trusts artifact-supplied bindings. Coordinated plan_id/source_directory changes plus copied primary files passed all 24 members despite a stale artifact digest. Base likewise accepts coordinated prior-row session_id/source_directory changes. This is an existing artifact-authentication limitation, not a commit-introduced weakening.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Local origin/main differs from the requested base. Review used exact commit 420e1f07, which is the reviewed commit's direct parent. HEAD remained detached at 7a9bdf93 and the repository stayed clean.",
      "needs": ""
    }
  ]
}
```

## Findings

**MERGE.** No introduced findings.

Prepare rejects cross-night custody and altered, missing, empty, or malformed plan IDs. Other custody checks remain intact. Revision 5 candidate bytes, output, and refusal messages match base exactly.

`verify-members` can accept coordinated artifact tampering; the base verifier has the equivalent session-ID trust limitation. It verifies primary files against a trusted artifact, rather than authenticating the artifact itself.

The requested suite passed 261/262 tests; the sole failure reproduces on base due to sandbox restrictions. All nine new tests fail against base. No repository files were modified.

## Residual risk

No live measurement validation was performed. The lead’s remaining verification step is rerunning the live identity-probe test outside this sandbox.
## Brief

WRITE_SCOPE: []

You are an independent reviewer (non-author) of commit 7a9bdf93 on branch fix/2026-10-02-rev6-custody-plan-id (PR #456; base origin/main 420e1f07). Review only; WRITE_SCOPE is [] (write nothing in the repo; /tmp scratch is fine). You MUST execute code, not just read it.

The defect: Revision 6 `prepare-candidate` refused every member with "first path part does not equal the session id" because `_corpus_relative_custody` (scripts/issue_calibration_acceptance_generation.py) required custody dirs named by session id (the Revision 5 convention from cc8346c2), while Revision 6 custody dirs are named by the NIGHT PLAN id (e.g. dir `d079-epoch-25g83-r6-derivation-c1-20261001T0617Z` for session `d079-epoch-25g83-r6-20261001T0617Z`). Same class as PR #454. The fix binds the first path part, for Revision 6 only, to the plan_id in that session's harvest record, in both prepare-candidate member selection and verify-members (via derivation_notes.revision6_records[session].plan_id).

Check, executing code:
1. Is the binding correct and no weaker than the old rule? Can any Revision 6 member be admitted from a directory that does not belong to its own session's night (e.g. the other window's dir, a forged plan id in the artifact for verify-members, a missing/empty plan id)? Try to construct such a case.
2. Is Revision 5 behaviour byte-for-byte unchanged (message text, refusal paths)?
3. Is every other custody check (corpus-root containment, runs/instrument_validation/<attempt> shape, attempt id, canonical locator, primary files) intact?
4. Does the verify-members path trust a value the artifact itself supplies (plan_id in derivation_notes) in a way that lets a tampered artifact pass? Compare with how the old rule trusted session ids.
5. Run: /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_rev6_custody_plan_id tests.test_issue_calibration_acceptance_generation tests.test_issuer_corpus_root tests.test_acc_25g83_rev6 tests.test_acc_25g83_rev5 tests.test_harvest_window tests.test_rev6_prior_start_plan_id tests.test_revision6_seal
6. Confirm the new tests fail on base 420e1f07's issuer (e.g. copy the base issuer to /tmp and run the new test module against it, or git stash-free equivalent in a /tmp clone).
Never read or print measured values (energy, B, slot values); identity keys and paths only. Never touch joulewise/powermetrics_fiducial.py, joulewise/uncertainty_evidence.py, joulewise/adapters/powermetrics.py, joulewise/reduce.py.

Verdict: MERGE or BLOCK, with findings (severity, file:line, blocking yes/no, introduced_by_commit yes/no).
