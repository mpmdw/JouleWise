```json
{
 "schema": "claude-codex-report/v1",
 "genre": "review",
 "status": "clean",
 "completion": "partial",
 "summary": "LANDABLE: M1/M2/M3 are caught; G4-excluded baseline passes; process census is sandbox-blocked.",
 "workspace": {
  "base_requested": "678d9bcc",
  "base_mode": "exact",
  "head_start": "678d9bcc480192238d9db4220c39e125e765edf4",
  "head_end": "678d9bcc480192238d9db4220c39e125e765edf4",
  "upstream_end": null,
  "branch": null
 },
 "pathspec": [],
 "unowned_dirty": [],
 "verdict": {
  "decision": "LANDABLE",
  "findings": [],
  "M1": {
   "mutation": "configs/campaigns/d117_contrast_v5/generate_configs.py:2697 restored legacy producer keys; producer FAIL and consumer ERROR both catch it.",
   "failure_lines": [
    "test_generated_plan_tree_uses_canonical_root_leaf_keys (tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_plan_tree_uses_canonical_root_leaf_keys) ... FAIL",
    "test_generated_gamma_roots_pass_and_legacy_keys_are_refused (tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_generated_gamma_roots_pass_and_legacy_keys_are_refused) ... ERROR",
    "joulewise.arm_readiness_evidence_t0.T0EvidenceAuthoringError: arm roots do not derive from frozen leaves"
   ],
   "tail": [
    "AssertionError: {'claim_leaf': 'runs_d117_contrast_qwen3-1p7b_vs_[76 chars]und'} != {'claim_root_leaf': 'runs_d117_contrast_qwen3-1p7[86 chars]und'}",
    "- {'bound_leaf': 'runs_d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5_bound',",
    "+ {'bound_root_leaf': 'runs_d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5_bound',",
    "?         +++++",
    "",
    "-  'claim_leaf': 'runs_d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5'}",
    "+  'claim_root_leaf': 'runs_d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5'}",
    "?         +++++",
    "",
    "",
    "----------------------------------------------------------------------",
    "Ran 2 tests in 1.089s",
    "",
    "FAILED (failures=1, errors=1)"
   ]
  },
  "M2": {
   "mutation": "tests/test_arm_readiness_evidence_t0.py:947 feeds legacy_roots to the positive call; expected refusal occurs.",
   "tail": [
    "    ^",
    "  File \"/private/tmp/magistrate-d6888966/gamma-exec-copy/joulewise/arm_readiness_evidence_t0.py\", line 1020, in _root_observation",
    "    raise _underivable(kind, \"arm roots do not derive from frozen leaves\")",
    "joulewise.arm_readiness_evidence_t0.T0EvidenceAuthoringError: arm roots do not derive from frozen leaves",
    "",
    "----------------------------------------------------------------------",
    "Ran 1 test in 0.575s",
    "",
    "FAILED (errors=1)"
   ]
  },
  "M3": {
   "mutation": "joulewise/arm_readiness_evidence_t0.py:1017 adds legacy fallback to both root-key lookups; consumer negative assertion catches loosening; producer passes.",
   "failure_lines": [
    "test_generated_plan_tree_uses_canonical_root_leaf_keys (tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_plan_tree_uses_canonical_root_leaf_keys) ... ok",
    "test_generated_gamma_roots_pass_and_legacy_keys_are_refused (tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_generated_gamma_roots_pass_and_legacy_keys_are_refused) ... FAIL"
   ],
   "tail": [
    "    ^",
    "AssertionError: T0EvidenceAuthoringError not raised",
    "",
    "----------------------------------------------------------------------",
    "Ran 2 tests in 1.082s",
    "",
    "FAILED (failures=1)"
   ]
  },
  "isolation": {
   "baseline_tmp_before": 704,
   "baseline_tmp_after": 708,
   "baseline_tmp_added": [
    "gamma-cr",
    "iw-epoch.log",
    "tmp6krv2m_r",
    "tmp85_oo29z",
    "tmpb07nin37",
    "tmpijm9lde8",
    "tmpnu91gdvs",
    "tmpug2pn7af-shallow"
   ],
   "baseline_tmp_removed": [
    "analysis-v5-singleton-8wcr0n5f",
    "tmpctpht413",
    "tmpdusb1o9l",
    "tmpxv_6f1ug"
   ],
   "baseline_attribution": "Global /tmp delta cannot be attributed to this baseline; initial-run leak attribution is unverifiable.",
   "process_counts_before": {
    "python": null,
    "vllm": null,
    "pgrep": null
   },
   "process_counts_after": {
    "python": null,
    "vllm": null,
    "pgrep": null
   },
   "process_leaks": "Unverifiable: /bin/ps launch denied with PermissionError(1, Operation not permitted).",
   "rerun_tracked_temp_paths": 257,
   "rerun_surviving_tracked_temp_paths": [],
   "failure_cleanup": {
    "directories": [
     "/tmp/d117-v5-roots-k7dxpgf8",
     "/tmp/t0-gamma-roots-69uaw8u3"
    ],
    "exists_after": [
     false,
     false
    ]
   },
   "cleanup_result": "Both TemporaryDirectory contexts were forced to fail after pack generation; both directories were absent afterward. All four mutated files restored byte-for-byte; restored regressions pass."
  }
 },
 "verification": [
  {
   "id": "V1",
   "kind": "suite",
   "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_contrast_v5_pack tests.test_arm_readiness_evidence_t0",
   "cwd": "/tmp/magistrate-d6888966/gamma-exec-copy",
   "observed": {
    "result": "fail",
    "exit_code": 1,
    "tail": [
     "    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
     "AssertionError: 3 != 0 : sysmon request failed with error: sysmond service not found",
     "pgrep: Cannot get process list",
     "",
     "",
     "----------------------------------------------------------------------",
     "Ran 121 tests in 548.099s",
     "",
     "FAILED (failures=2, skipped=1)"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "OK"
   }
  },
  {
   "id": "V2",
   "kind": "suite",
   "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B .gamma_exec_evidence/run_baseline_excluding_g4.py",
   "cwd": "/tmp/magistrate-d6888966/gamma-exec-copy",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "----------------------------------------------------------------------",
     "Ran 120 tests in 550.888s",
     "",
     "OK (skipped=1)"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "OK \\(skipped=1\\)"
   }
  },
  {
   "id": "V3",
   "kind": "test",
   "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B .gamma_exec_evidence/run_mutations.py",
   "cwd": "/tmp/magistrate-d6888966/gamma-exec-copy",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "RESTORED_ALL_FOUR_FILES true"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "RESTORED_ALL_FOUR_FILES true"
   }
  },
  {
   "id": "V4",
   "kind": "inspection",
   "cmd": "git -C /Users/edr/code/JouleWise-wt-ref-gamma status --short",
   "cwd": "/Users/edr/code/JouleWise-wt-ref-gamma",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": []
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "^$"
   }
  }
 ],
 "flags": [
  {
   "id": "F1",
   "kind": "environment",
   "level": "nonblocking",
   "text": "Only tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect was excluded by listing every other test. Its two subtests failed because pgrep returned 3: sysmond service not found. The rerun uses an audit-only sitecustomize hook to record tempfile.mkdtemp paths; command argv is in .gamma_exec_evidence/baseline-excluding-g4-argv.json.",
   "needs": ""
  },
  {
   "id": "F2",
   "kind": "verification_gap",
   "level": "nonblocking",
   "text": "Active python/vllm/pgrep counts and process leaks could not be verified because ps is forbidden. test_acid_real_boot_session_then_real_arm_generator_reaches_go skips because kern.bootsessionuuid sysctl is denied. No network or hardware collection was performed.",
   "needs": "Lead may replay the process census and denied platform checks in its permitted environment."
  }
 ]
}
```