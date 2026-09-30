```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "AUDIT: FINDINGS — two should-fix promotion test gaps and one loader test nit; no demonstrated production regression.",
  "workspace": {
    "base_requested": "9eab16f8",
    "base_mode": "exact",
    "head_start": "e9827f3344a250b1d5fe5656ea2b766ce502af5b",
    "head_end": "e9827f3344a250b1d5fe5656ea2b766ce502af5b",
    "upstream_end": "32ff901374024defa97fc3d137c5a699423676e7",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "audit": "FINDINGS",
    "contract": "pass",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "tests/test_promote_calibration_candidate.py",
        "line": 70,
        "guard": "scripts/promote_calibration_candidate.py:224",
        "summary": "Deleting overwrite protection survives the tests; a direct mutant probe overwrites existing different bytes.",
        "cmd": "python3 -B /tmp/d138aaudit/survivor-check.py"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "tests/test_promote_calibration_candidate.py",
        "line": 152,
        "guard": "scripts/promote_calibration_candidate.py:144",
        "summary": "Deleting preserved-log plain-text digest verification survives the cited-evidence tests and accepts mismatched provenance.",
        "cmd": "python3 -B /tmp/d138aaudit/survivor-check.py"
      },
      {
        "id": "F3",
        "severity": "nit",
        "file": "tests/test_calibration_dispositions.py",
        "line": 54,
        "guard": "joulewise/calibration_dispositions.py:92",
        "summary": "Deleting the parser's production-pin table-equality guard survives the tests; a direct table-drift probe distinguishes original and mutant.",
        "cmd": "python3 -B /tmp/d138aaudit/survivor-check.py"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_calibration_dispositions tests.test_promote_calibration_candidate tests.test_calibration_bracketing tests.test_issue_calibration_acceptance_generation tests.test_reissue_calibration_acceptance tests.test_acc_25g83_rev5 tests.test_epoch_continuation > /tmp/d138aaudit/requested-suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 355 tests in 234.211s", "FAILED (failures=1, skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/d138aaudit/mutate.py > /tmp/d138aaudit/mutations.jsonl",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["13 mutations completed; scratch sources restored."]
      },
      "expected": {"exit_code": 0, "tail_regex": "13 mutations completed; scratch sources restored\\."}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B /tmp/d138aaudit/survivor-check.py > /tmp/d138aaudit/survivor-check.jsonl",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["M3, M9, M10 each survived 125 tests; original-versus-mutant probes distinguished all three."]
      },
      "expected": {"exit_code": 0, "tail_regex": "extended_tests_exit.*0"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B /tmp/d138aaudit/digest-mutation.py > /tmp/d138aaudit/M1-broader.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["FAILED (failures=1)", "mutant exit: 1"]
      },
      "expected": {"exit_code": 0, "tail_regex": "mutant exit: 1"}
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "python3 -B /tmp/d138aaudit/corpus.py /tmp/d138aaudit/base > /tmp/d138aaudit/corpus-base.json\npython3 -B /tmp/d138aaudit/corpus.py /tmp/d138aaudit/m > /tmp/d138aaudit/corpus-head.json\ncmp /tmp/d138aaudit/corpus-base.json /tmp/d138aaudit/corpus-head.json",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "python3 -B /tmp/d138aaudit/probes.py > /tmp/d138aaudit/promotion-probes.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["No implicit config writes; explicit --out can create unregistered bytes; different existing bytes preserved."]
      },
      "expected": {"exit_code": 0, "tail_regex": "different existing bytes preserved"}
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "python3 -B /tmp/d138aaudit/check_numeric_preservation.py > /tmp/d138aaudit/numbers.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "All promotion-protected fields unchanged; four estimator files byte-identical to base.",
          "S=0.013701 C=0.01902064410651988 level=0.038078579302948"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "four estimator files byte-identical"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_issue_calibration_acceptance_generation.DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch > /tmp/d138aaudit/base-live-probe.log 2>&1",
      "cwd": "/tmp/d138aaudit/base",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 1 test in 0.019s", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V9",
      "kind": "other",
      "cmd": "/usr/sbin/sysctl -n kern.osversion",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["sysctl: sysctl fmt -1 1024 1: Operation not permitted"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".+"}
    },
    {
      "id": "V10",
      "kind": "other",
      "cmd": "/usr/sbin/sysctl -n hw.model",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["sysctl: sysctl fmt -1 1024 1: Operation not permitted"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".+"}
    },
    {
      "id": "V11",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "SANDBOX-ONLY: the requested suite's sole failure is the live OS-build probe. The base test fails identically; both underlying sysctl commands report Operation not permitted. No pgrep failure observed.",
      "needs": "Lead reruns the live identity test in its normal environment."
    },
    {
      "id": "E2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No full canonical suite, live measurement campaign, raw-member custody verifier, or independent quantile-proof validation was executed.",
      "needs": ""
    },
    {
      "id": "E3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Main is 32ff9013. Its advance includes tests/test_gen_state.py fixture maintenance alongside documentation/bookkeeping. Calibration comparison used exact requested base 9eab16f8.",
      "needs": ""
    }
  ]
}
```

## Findings

**AUDIT: FINDINGS.** No blockers or demonstrated defects in the current guards. The findings concern missing discriminating regressions.

1. **F1 — should-fix:** `tests/test_promote_calibration_candidate.py:70`, guarding `scripts/promote_calibration_candidate.py:224`. Deleting overwrite protection leaves both the 113-test focused suite and 125-test extended suite green. A direct probe shows the original refuses and preserves existing different bytes; the mutant overwrites them. Add a refusal-and-byte-preservation regression.

2. **F2 — should-fix:** `tests/test_promote_calibration_candidate.py:152`, guarding `scripts/promote_calibration_candidate.py:144`. Deleting the decompressed-log digest comparison survives both suites. False `plain_text_sha256` provenance is refused by the original and accepted by the mutant. Add an adversarial preserved-log digest test.

3. **F3 — nit:** `tests/test_calibration_dispositions.py:54`, guarding `joulewise/calibration_dispositions.py:92`. Deleting production-pin table equality survives both suites. Changing the code table by one content ID distinguishes original refusal from mutant acceptance. The existing test checks shipped table agreement, but not parser refusal under drift.

Commands for these findings: `python3 -B /tmp/d138aaudit/mutate.py` and `python3 -B /tmp/d138aaudit/survivor-check.py`. [Detailed results](/tmp/d138aaudit/survivor-check.jsonl).

All 13 initial mutations used:

```text
python3 -B -m unittest tests.test_calibration_dispositions tests.test_promote_calibration_candidate tests.test_calibration_bracketing
```

| Mutant | Change | Observed result |
|---|---|---|
| M1 | Remove registry digest guard | SURVIVES focused suite; broader `test_an_appended_row_under_the_fixed_id_refuses_on_digest` RED by assertion |
| M2 | Remove duplicate-key parser hook | `test_issuer_rejects_duplicate_json_keys` RED by assertion |
| M3 | Remove parser/table equality | SURVIVES; F3 |
| M4 | Remove declaration equality | `test_l10_undeclared_decision_touching_prior_set_refuses` RED by assertion |
| M5 | Remove diagnostic-row skip | `test_l1_synthetic_disposed_diagnostics_validate` RED by assertion |
| M6 | Remove disposed-exclusion guard | SURVIVES; existing completeness equality makes this guard redundant |
| M7 | Count disposed diagnostics | `test_corpus_doubling_excludes_disposed_diagnostics` RED by assertion |
| M8 | Replace issuer delegation with plain JSON parsing | `test_issuer_rejects_duplicate_json_keys` RED by assertion |
| M9 | Remove overwrite refusal | SURVIVES; F1 |
| M10 | Remove preserved-log digest comparison | SURVIVES; F2 |
| M11 | Remove issued-input seal guard | `test_p7_issued_input_seal_drift_stops` RED by assertion |
| M12 | Remove cited-file verification | `test_p6_cited_evidence_and_disclosure_mutations_refuse` RED by assertion |
| M13 | Remove required issuance-text argument | `test_cli_requires_explicit_issuance_text` RED by assertion |

No mutant reported RED solely through an uncaught exception. [Mutation log](/tmp/d138aaudit/mutations.jsonl).

The requested suite completed **355 tests: one failure, one skip**. The failure is **SANDBOX-ONLY**: the live OS-build test receives `None`; it fails identically on the base export, and both underlying `sysctl` probes report `Operation not permitted`. [Suite log](/tmp/d138aaudit/requested-suite.log).

For **all seven registered generations**, base/head results are identical: loading succeeds, `_valid_acceptance_bound` is true, and prior valid count is 30. Executing the production counting expression at threshold−1 and threshold gives identical results: 37/38 for n19 generations, 33/34 for r3–r7. **R7 remains the default.**

Promotion probes found no implicit config writes. Missing issuance text or output action exits 2. Different existing bytes, including a symlink target, remain unchanged with refusal exit 1. Explicit `--out` can create scratch config bytes, but the acceptance loader rejects that unregistered output.

Candidate arithmetic reproduced independently: minimum, maximum, range, mean, sample SD, operative rounding, and prediction values using the recorded quantiles. Promotion preserves protected fields; all four estimator files remain byte-identical to base.

My [independent findings](/tmp/d138aaudit/independent-findings.md) were written before reading Opus. I agree with its contract, registration, default, and current write-guard conclusions. My execution verdict adds F1–F3 to its test-quality assessment.

Repository status is clean; HEAD is unchanged. Next step: add the discriminating tests for F1/F2, optionally F3, then rerun them and the live identity check.

## Residual risk

The corpus comparison executed the production counting expression with corpus-derived fixtures; it was not a live bracket campaign. Synthetic issuance proves preservation, not reproduction of withdrawn ruled issuance bytes. Raw measurements, custody, quantile proofs, and the full canonical suite were not independently revalidated.