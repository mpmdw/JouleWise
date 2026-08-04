```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Audit found two D-109 blocker-grade fail-open paths and one should-fix regression-discrimination gap; scope and remaining clauses were conformant.",
  "workspace": {
    "base_requested": "a14d1fe189734a9a58035736becb75612a85a157",
    "base_mode": "exact",
    "head_start": "83831134492d463bc7dc7408a7162ee39a07692e",
    "head_end": "83831134492d463bc7dc7408a7162ee39a07692e",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "clauses": ["D-109 R1.2", "D-109 R1.4"],
        "title": "Minted-consumption sessions bypass the mandatory ledger snapshot refusal",
        "evidence": [
          "joulewise/whole_window.py:416",
          "joulewise/whole_window.py:490",
          "joulewise/whole_window.py:508",
          "joulewise/whole_window.py:4584"
        ]
      },
      {
        "id": "B2",
        "severity": "blocker",
        "clauses": ["D-109 R2.3", "D-109 R2.6"],
        "title": "A content-bearing abandoned attempt is accepted as classifiable although the prior-observation schema cannot represent it",
        "evidence": [
          "scripts/validate_powermetrics_fiducial.py:372",
          "joulewise/calibration_ledger.py:303",
          "joulewise/calibration_ledger.py:715",
          "joulewise/calibration_bracketing.py:884"
        ]
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "clauses": ["D-109 R1.3", "D-109 R2.5", "D-109 R2.8", "original F3 regression fence"],
        "title": "Four mandated regressions do not fail under their corresponding narrow defect",
        "evidence": [
          "tests/test_calibration_bracketing.py:540",
          "tests/test_calibration_bracketing.py:623",
          "tests/test_calibration_bracketing.py:643",
          "tests/test_calibration_ledger.py:156"
        ]
      }
    ],
    "audit": [
      {
        "question": "R1",
        "result": "B1 affects universal snapshot enforcement; otherwise clauses 1-7 conform",
        "evidence": [
          "joulewise/calibration_bracketing.py:628",
          "scripts/validate_powermetrics_fiducial.py:357",
          "scripts/validate_powermetrics_fiducial.py:399",
          "joulewise/calibration_ledger.py:357",
          "joulewise/calibration_ledger.py:414",
          "joulewise/calibration_ledger.py:451",
          "joulewise/calibration_ledger.py:517",
          "joulewise/calibration_ledger.py:533",
          "joulewise/calibration_ledger.py:1",
          "scripts/calibration_ledger_backfill.py:2"
        ]
      },
      {
        "question": "Single snapshot",
        "result": "Non-minted paths reuse one object; B1 is a missing-snapshot bypass, not a double-load TOCTOU",
        "evidence": [
          "scripts/run_campaign.py:5215",
          "scripts/run_campaign.py:5261",
          "scripts/run_campaign.py:6754",
          "joulewise/floor_extraction.py:1616",
          "joulewise/analysis_engine/inputs.py:1255",
          "joulewise/analysis_engine/inputs.py:2677",
          "scripts/mint_floor_artifact.py:1959",
          "scripts/mint_floor_artifact.py:1974",
          "scripts/mint_floor_artifact.py:2017"
        ]
      },
      {
        "question": "R2",
        "result": "B2 affects abandoned observations; content subtraction, total-38 counting, and issuance refusal otherwise conform",
        "evidence": [
          "joulewise/calibration_ledger.py:120",
          "joulewise/calibration_bracketing.py:253",
          "joulewise/calibration_bracketing.py:708",
          "joulewise/calibration_bracketing.py:870",
          "joulewise/calibration_bracketing.py:879",
          "joulewise/calibration_bracketing.py:890",
          "configs/calibration/calibration_acceptance_d079_v2.json:8"
        ]
      },
      {
        "question": "F1/F2",
        "result": "Conformant: six-field epoch and exact four-module digest closure",
        "evidence": [
          "joulewise/calibration_ledger.py:41",
          "joulewise/calibration_bracketing.py:54",
          "joulewise/calibration_bracketing.py:748",
          "configs/calibration/calibration_acceptance_d079_v2.json:39"
        ]
      },
      {
        "question": "Fences",
        "result": "Conformant: full-T1 exact matching, candidate authentication preserved, Window A still cannot form, and budget boundary regressions retained",
        "evidence": [
          "joulewise/calibration_bracketing.py:452",
          "joulewise/calibration_bracketing.py:849",
          "joulewise/calibration_bracketing.py:1115",
          "tests/test_calibration_bracketing.py:290",
          "tests/test_calibration_bracketing.py:310",
          "tests/test_calibration_bracketing.py:396",
          "tests/test_calibration_bracketing.py:415"
        ]
      },
      {
        "question": "Regressions",
        "result": "Rollback, off-ledger, pending and budget tests discriminate; S1 covers the weak fork, cross-root, prior-set and 38-total cases",
        "evidence": [
          "tests/test_calibration_ledger.py:103",
          "tests/test_calibration_ledger.py:140",
          "tests/test_calibration_bracketing.py:585"
        ]
      },
      {
        "question": "Scope",
        "result": "Exactly 17 paths changed; audit modified none and final tree remained clean",
        "evidence": ["git diff --name-only a14d1fe 8383113"]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_bracketing.CalibrationBracketingTests.test_unissued_fixture_cannot_license_default_claim_evaluation tests.test_calibration_bracketing.CalibrationBracketingTests.test_d079_budgeted_drift_above_obsolete_cliff_passes_with_allowance tests.test_calibration_bracketing.CalibrationBracketingTests.test_d079_drift_beyond_budget_refuses_with_recorded_basis tests.test_calibration_bracketing.CalibrationBracketingTests.test_t1_mismatched_candidate_remains_ineligible_under_d079_v2 tests.test_calibration_bracketing.CalibrationBracketingTests.test_window_a_t1_mismatch_shape_still_cannot_form_bracket tests.test_calibration_bracketing.CalibrationBracketingTests.test_unselected_same_identity_range_expander_stales_artifact tests.test_calibration_bracketing.CalibrationBracketingTests.test_off_ledger_candidate_refuses_even_beside_registered_pair tests.test_calibration_bracketing.CalibrationBracketingTests.test_prior_set_subtraction_does_not_treat_known_holdout_as_new tests.test_calibration_bracketing.CalibrationBracketingTests.test_corpus_doubling_counts_38_total_valid_distinct_observations",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 9 tests in 0.007s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 9 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'compile every changed Python source'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["COMPILE_OK 15"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "COMPILE_OK 15"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "shasum -a 256 configs/calibration/calibration_acceptance_d079_v2.json joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Acceptance byte pin and all four estimator digests matched their recorded values."]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_ledger",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FileNotFoundError: No usable temporary directory found", "FAILED (errors=9)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 9 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 0,
        "tail": ["Not run: sandbox has no writable temporary directory."]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Filesystem-backed ledger regressions and the canonical suite could not run because tempfile found no writable directory.",
      "needs": "Lead must replay V4 and V5 with a writable TMPDIR."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "SIGKILL/SIGTERM were not launched; Python atexit is normal-termination-only, so hard termination relies on the lingering pending/head-mismatch refusal.",
      "needs": "Replay the hard-kill regression in a writable process sandbox if live process evidence is required."
    }
  ]
}
```

## Findings

B1 — blocker: minted consumption bypasses D-109’s universal snapshot gate.

`AuthenticatedConsumptionSession` deliberately avoids loading a snapshot for minted semantics at `joulewise/whole_window.py:416`, then skips snapshot/refusal checks at `joulewise/whole_window.py:490` and becomes ready from stored summaries at `joulewise/whole_window.py:508`. The secondary verifier also permits a missing session at `joulewise/whole_window.py:4584`.

A read-only probe supplied a snapshot containing `calibration_ledger_pending`; the minted session returned `ready=True` with no refusal. Thus pending, rollback, or stale-head state can be ignored on this consumer route, contrary to D-109 R1.4’s “every consumer path” requirement. Non-minted paths correctly reuse one object—there was no observed double-load TOCTOU.

B2 — blocker: content-bearing `abandoned` observations can silently pass R2.

The atexit handler finalizes as `abandoned` while hashing whatever custody bytes already exist (`scripts/validate_powermetrics_fiducial.py:372`). Finalization derives a content ID whenever manifest/evidence hashes exist (`joulewise/calibration_ledger.py:715`), while abandoned receipts bypass the ordinary finalized-observation requirements (`joulewise/calibration_ledger.py:303`).

R2’s prior-set schema permits valid, systematic-invalid, ordinary-invalid, blind-holdout, or unresolved—not abandoned (`joulewise/calibration_bracketing.py:263`). Nevertheless, trigger evaluation explicitly accepts `abandoned` as classifiable (`joulewise/calibration_bracketing.py:884`). An in-memory probe added a new content-bearing abandoned observation beside an otherwise valid bracket; evaluation returned `status=passed`, no reasons, and no trigger. The currently unissued fixture still blocks immediate production consumption, but the intended issued path is contract-incomplete.

S1 — should-fix: four mandated regressions are insufficiently defect-shaped.

- The cross-root expander test directly invokes the low-level evaluator (`tests/test_calibration_bracketing.py:540`), so restoring the original caller-root directory enumeration would not make that test fail.
- The prior-set test’s known observation is valid, in-range, and below 38 (`tests/test_calibration_bracketing.py:623`); treating it as “new” still produces no trigger.
- The 38-total test constructs 38 distinct observations that are all outside the prior set (`tests/test_calibration_bracketing.py:643`). A defective “38 post-cutoff” implementation therefore also passes. A separate 19-prior + 19-new probe confirmed the implementation itself currently uses total counting.
- The fork test appends an exact duplicate receipt (`tests/test_calibration_ledger.py:156`). Removing predecessor/fork checking alone still trips sequence and duplicate checks at `joulewise/calibration_ledger.py:383`; it does not isolate a distinct sibling fork.

## Residual risk

The canonical suite and filesystem-backed ledger tests require lead replay with a writable `TMPDIR`. Also, `atexit` runs only for normal interpreter termination: neither default SIGTERM nor SIGKILL executes it. The code’s actual hard-kill protection is therefore the lingering pending receipt plus physical-head mismatch, which static inspection confirmed at `joulewise/calibration_ledger.py:414` and `joulewise/calibration_ledger.py:533`.