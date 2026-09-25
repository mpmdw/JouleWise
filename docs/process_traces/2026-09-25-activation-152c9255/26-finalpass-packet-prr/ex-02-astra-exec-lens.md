```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Execution and archive checks passed; one SHOULD-FIX disposition-reference ambiguity and one NIT remain.",
  "workspace": {
    "base_requested": "c034a56f",
    "base_mode": "exact",
    "head_start": "3c52518dbe9d9541d0134f628a4dfbc4d0465465",
    "head_end": "3c52518dbe9d9541d0134f628a4dfbc4d0465465",
    "upstream_end": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "branch": "feat/2026-09-25-acc-registration-rev5"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "scripts/issue_calibration_acceptance_generation.py",
        "line": 381,
        "title": "Disposing decision reference does not identify the dated entry",
        "fix": "Give the disposition a unique dated identifier or explicit subsection reference; use it in the registry, DISPOSITION_DECISION_ID, successor prior set, and assertions."
      },
      {
        "id": "F2",
        "severity": "nit",
        "path": "scripts/sim_acc_25g83_rev5.py",
        "line": 105,
        "title": "Simulation docstring describes superseded issuer behavior",
        "fix": "Replace the claim that the current CLI refuses n=12 and S=C with the actual Revision 5 behavior."
      }
    ],
    "r4": {
      "archive_census": "n1: 12 evidence documents, 4 valid; n2: 12 evidence documents, 7 valid. No additional valid target-epoch observation in either archive.",
      "identity_verification": "Independently SHA-256-hashed instrument_evidence.json and manifest.json, then hashed their canonical JSON hash map. All eleven IDs and B values match the registry and decision-log table. Manifest artifact hashes also matched archived bytes.",
      "counterfactual": "Focused fixture test passed: empty registry refuses A-7; populated registry permits candidate preparation; all eleven IDs enter the prior set; successor freshness is fresh.",
      "decision_binding": "Registry and prior set carry only D-126. The issuer compares that literal and the mechanism; it does not resolve the dated decision-log entry."
    },
    "r17": {
      "method": "NUL-separated plist records; positive integer elapsed_ns divided by 1e6; first record discarded per stream; R5(n) compares median of capture medians strictly greater than 150 ms.",
      "n1": {
        "captures": 12,
        "intervals": 10296,
        "median_of_medians_ms": 247.93733275,
        "maximum_ms": 353.265125,
        "verdict": "STOP"
      },
      "n2": {
        "captures": 12,
        "intervals": 10285,
        "median_of_medians_ms": 248.39447875,
        "maximum_ms": 419.063458,
        "verdict": "STOP"
      },
      "interactive_session_C": {
        "raw_streams": 21,
        "intervals": 6134,
        "median_of_medians_ms": 131.736749,
        "maximum_ms": 140.791541,
        "verdict": "CONTINUE",
        "selection": "All 21 Interactive main/idle/idle-post streams copied into temporary report input; each owning job.plist verified ProcessType=Interactive."
      },
      "pins": "Report imports only standard-library modules. Four pinned estimator modules and the derivation chain are unchanged."
    },
    "r10": {
      "alternate_seed": 25098313,
      "model_order": ["gaussian", "heavy_excursions", "serial_ar1", "block_drift"],
      "false_admissions_per_200": [0, 0, 0, 0],
      "later_level_refusals_per_200": [12, 8, 14, 12],
      "floor_passes_per_200": [0, 0, 0, 0],
      "decision_interval_passes_per_200": [0, 0, 0, 0],
      "half_yield_w1_futility_per_200": [82, 83, 77, 77],
      "half_yield_w3_openings_per_200": [27, 28, 24, 24],
      "half_yield_shortfalls_after_w3": [0, 0, 0, 0],
      "half_yield_false_admissions": [0, 0, 0, 0],
      "tree": "W1 valid count below 6 stops; otherwise W2; W3 only when W1+W2 retain fewer than 12. All valid members retained; no equivalence branch.",
      "block_drift": "Both blocks move: W1 mean 0.026 s and W2 mean 0.034 s around the 0.030 s baseline, each with 0.0015 s noise; later probe uses the high block.",
      "finite_bound": "0/200 has exact one-sided 95% upper bound 1.4867039231%; the document reports it and explicitly requires council reopening for nonzero admission.",
      "stability": "Qualitative conclusions reproduced. Exact refusal percentages and model rankings are not seed-stable."
    },
    "physics": "The 1e-6 s screen quantum and 1e-15 s level quantum are microscopic arithmetic resolutions, not demonstrated instrument precision. At the simulation's 33 W they represent 3.3e-5 J and 3.3e-14 J. No new microscopic physical acceptance margin was found. The inherited 4.8e-16 s maximum-versus-rounded-screen discrepancy remains the ruling's acknowledged arithmetic issue, not grounds for an invented tolerance."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_acc_25g83_rev5 tests.test_calibration_cadence_report tests.test_preregistration_chain_digest",
      "cwd": "/tmp/152c9255/prr-lens-astra/repo",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 19 tests in 8.833s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 19 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests.test_revision_five_exact_epoch_permits_twelve_and_zero_headroom",
      "cwd": "/tmp/152c9255/prr-lens-astra/repo",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.002s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test.*OK"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/152c9255/prr-lens-astra/audit_archive.py",
      "cwd": "/tmp/152c9255/prr-lens-astra/repo",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ARCHIVE_AUDIT_PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "ARCHIVE_AUDIT_PASS"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from scripts import sim_acc_25g83_rev5 as s; s.SEED=25098313; s.main()'",
      "cwd": "/tmp/152c9255/prr-lens-astra/repo",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["      \"zero_event_upper_bound_95\": 0.014867039231272083", "    }", "  ]", "}"]
      },
      "expected": {"exit_code": 0, "tail_regex": "0\\.014867039231272083"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --quiet c034a56f 3c52518d -- joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py scripts/night_chains/calibration_derivation_only.zsh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — SHOULD-FIX: bind the dated disposition explicitly.**  
`scripts/issue_calibration_acceptance_generation.py:381`, `configs/calibration/observation_dispositions.json:4`, `docs/decision_log.md:12179`.

The magistrate’s concern is confirmed narrowly. `D-126` identifies both the original policy at `docs/decision_log.md:8481` and the new disposition at `:12176`. The issuer checks the literal at `:1140`, then records the same undifferentiated token through `:1533–1535` and `:1741`. It does not bind the exact dated entry.

This does **not** invalidate the verified eleven content IDs or demonstrate a present membership bypass. It weakens the successor’s authority reference.

**Exact fix:** assign an explicit identifier such as `D-126-disposition-25G83-v3-2026-09-25`, declare its unique anchor in the dated entry, and use it consistently in the registry, issuer constant, prior-set assertions and tests. Keep the original D-126 policy identifier unchanged.

**F2 — NIT: stale simulation explanation.**  
`scripts/sim_acc_25g83_rev5.py:105` says the current CLI still refuses `n=12` and `S=C`. This PR implements and tests their acceptance for Revision 5.

**Exact fix:** describe the helper as reproducing the current Revision 5 issuer arithmetic; remove the superseded refusal claim.

## Residual risk

Archive replay and fixture tests establish the reviewed behaviors; they do not validate future Interactive captures or constitute actual successor issuance. No live collection or full discovery suite was run.

The simulation checks the stated models and an artifact fixed at 80% of its allowed timing bound. Its finite-sample result is conditional on those assumptions, not a general false-admission guarantee. PR-L integration and replacement of registration placeholders remain lead-owned gates.