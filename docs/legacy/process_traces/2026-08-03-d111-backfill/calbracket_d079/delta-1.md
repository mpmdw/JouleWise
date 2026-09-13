```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FAIL: named fix probes pass, but three D-102 freshness/provenance blockers remain in same-identity filtering, estimator-digest scope, and cross-root trigger observation.",
  "workspace": {
    "base_requested": "a14d1fe",
    "base_mode": "exact",
    "head_start": "a14d1fe189734a9a58035736becb75612a85a157",
    "head_end": "a14d1fe189734a9a58035736becb75612a85a157",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [],
  "unowned_dirty": [
    "joulewise/analysis_engine/claims.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/whole_window.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_reduce.py",
    "tests/test_whole_window_selection.py",
    "configs/calibration/calibration_acceptance_d079_v2.json",
    "tests/verify_calibration_acceptance_corpus.py"
  ],
  "verdict": {
    "overall": "fail",
    "blocker_present": true,
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Freshness scanning confuses D-102 identity equality with full T1 selection eligibility",
        "evidence": "docs/decision_log.md:6294-6302; joulewise/calibration_bracketing.py:643-680",
        "scenario": "An authenticated range-expander with the same six-field D-102 identity epoch but a different non-epoch T1 field such as mlx_version is excluded from matching, so a later normal pair passes fresh with no trigger. T1 selection must remain exact, but freshness requires a separate same-identity candidate set."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Estimator digest omits modules that directly affect b_fiducial_s",
        "evidence": "joulewise/calibration_bracketing.py:47-50,317-319; joulewise/powermetrics_fiducial.py:33-38,946-975,1079-1085",
        "scenario": "Mutating uncertainty_evidence.py or adapters/powermetrics.py does not stale the artifact, although those modules derive the additive trace-anchor bound and parse raw intervals consumed by the fiducial estimator. D-102 requires protocol/estimator byte changes to trigger re-derivation."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "The production supplied-candidate boundary leaves cross-runs-root mandatory triggers unobservable",
        "evidence": "docs/decision_log.md:6297-6302; joulewise/calibration_bracketing.py:508-519,830-887",
        "scenario": "calibration_bracket_for_bundles discovers candidates only under the evaluated window's runs_root. A valid same-identity range-expander or corpus-doubling member in another prior root is absent, allowing the old artifact to license a later root. No authenticated global registry or caller completeness proof closes the hole."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_calibration_bracketing tests.test_whole_window_selection tests.test_whole_window tests.test_analysis_integration tests.test_analysis_claims tests.test_floor_extraction tests.test_d078_reason_registry",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 321 tests in 69.312s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 321 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_calibration_bracketing.CalibrationBracketingTests.test_d102_decimal_boundary_sweep_is_exact_and_inclusive tests.test_calibration_bracketing.CalibrationBracketingTests.test_unselected_same_identity_range_expander_stales_artifact tests.test_calibration_bracketing.CalibrationBracketingTests.test_rekeyed_self_consistent_artifact_is_not_authenticated tests.test_calibration_bracketing.CalibrationBracketingTests.test_estimator_module_byte_change_stales_artifact_at_load tests.test_whole_window_selection.MaxBracketConsumptionTests.test_legacy_bracket_basis_hash_is_byte_identical",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 0.004s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B tests/verify_calibration_acceptance_corpus.py --repo-root /Users/edr/code/JouleWise --artifact configs/calibration/calibration_acceptance_d079_v2.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "max=0.03355875667989999 (20260722T222332-901c5c13) range=0.010817749309353528",
          "mean=0.026950033977532761 sample_sd=0.002970761365307205",
          "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_whole_window_selection.MaxBracketConsumptionTests.test_d079_real_selector_to_real_reducer_embeds_allowance_once",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 36.941s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s\\n\\nOK"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B - <<'PY'\nfrom tests.test_calibration_bracketing import CalibrationBracketingTests as T\nfrom joulewise.calibration_bracketing import evaluate_calibration_bracket\nt=T(); t.setUp()\nother=dict(t.bindings); other['mlx_version']='same-epoch-different-t1'\ncs=[t.candidate('same-epoch-range-expander',99,'0.022',bindings=other),t.candidate('current-pre',199,'0.025'),t.candidate('current-post',211,'0.026')]\nr,x=evaluate_calibration_bracket(cs,window_start_s=200,window_end_s=210,bindings=t.bindings,policy=t.policy)\nprint(r['status'],x,r['acceptance']['freshness']['status'],r['acceptance']['prospective_rederivation']['observed_triggers'])\nprint('identity_equal',all(other[k]==t.bindings[k] for k in ('os_build','hardware_model','power_policy','sampling_interval_ms','estimator_revision','pulse_protocol_id')))\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "passed () fresh []",
          "identity_equal True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "calibration_acceptance_bound_stale"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B - <<'PY'\nimport shutil,tempfile\nfrom pathlib import Path\nimport joulewise.calibration_bracketing as c\nwith tempfile.TemporaryDirectory() as d:\n root=Path(d)\n for rel in (*c.ESTIMATOR_CODE_PATHS,'joulewise/uncertainty_evidence.py','joulewise/adapters/powermetrics.py'):\n  dst=root/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(Path(rel),dst)\n old=c._REPO_ROOT\n try:\n  c._REPO_ROOT=root\n  print('baseline',c.load_calibration_acceptance_bound() is not None)\n  for rel in ('joulewise/powermetrics_fiducial.py','joulewise/reduce.py','joulewise/uncertainty_evidence.py','joulewise/adapters/powermetrics.py'):\n   p=root/rel; raw=p.read_bytes(); p.write_bytes(raw+b'\\n# byte mutation\\n'); print(rel,c.load_calibration_acceptance_bound() is None); p.write_bytes(raw)\n finally: c._REPO_ROOT=old\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "joulewise/powermetrics_fiducial.py True",
          "joulewise/reduce.py True",
          "joulewise/uncertainty_evidence.py False",
          "joulewise/adapters/powermetrics.py False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "uncertainty_evidence.py True.*adapters/powermetrics.py True"
      }
    },
    {
      "id": "V7",
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
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The prompt records global runs-root scanning as out of scope, but D-102 makes same-identity range expansion and corpus doubling mandatory triggers. No external authenticated candidate-registry contract was found.",
      "needs": "Preserve D-102 by supplying an authenticated complete registry/set or obtain a named decision explicitly narrowing trigger observation."
    },
    {
      "id": "FL2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The artifact is untracked at a14d1fe, so the requested git-show comparison cannot literally run. Removing the two new estimator-digest leaves and restoring the canonical derivation digest reconstructed bytes hashing exactly to ade322ab485813c39dfb5f5ffb3c8bfe89c86d23b94a4d858238bf1b9af4e8f2.",
      "needs": "Retain the old artifact bytes in audit custody if a literal byte diff is required."
    },
    {
      "id": "FL3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The four inspected 2026-07-22 members lack raw/powermetrics.plist locally; their stored decimal lexemes and both artifact hashes were byte-verified, but physical re-fit was impossible. The two locally retained a10 members physically re-fit exactly.",
      "needs": "Recover archived raw custody and independently re-fit at least two additional corpus members."
    },
    {
      "id": "FL4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The independent audit ran focused tests, not the optional full suite or a complete real passed-corpus basis replay.",
      "needs": "Lead runs the authoritative full suite at the final dirty head and completes the real passed-corpus replay."
    }
  ]
}
```

## Findings

F1 — blocker: the fix closes the named V5 only when the unselected candidate also matches every T1 field. D-102 defines the acceptance identity using six fields; `mlx_version`, `powermetrics_sha256`, and `anchor_method_version` are not among them. Selection should continue using exact T1 matching, but trigger observation needs a distinct six-field same-identity set. A second bypass exists because corpus membership is inferred from the directory basename alone: a new authenticated candidate reusing a corpus member ID but carrying different hashes/value also passed fresh.

F2 — blocker: the two-file digest is not a complete estimator boundary. `uncertainty_evidence.py` computes the trace-anchor term added to `b_fiducial_s`, and `adapters/powermetrics.py` parses the raw records used to fit every pulse. Mutating either went undetected. Binding `reduce.py` is conservative for downstream consumption, but does not replace binding these upstream estimator inputs. A versioned digest over the complete estimator dependency bundle would be safer than another hand-picked filename.

F3 — blocker: each production call scans only `runs_root/instrument_validation`. A trigger observed in another window root disappears from all later evaluations unless a human has already rotated the artifact. Recording `"global_runs_root_scan": false` makes the limitation visible but does not satisfy D-102’s mandatory-trigger language. A global filesystem sweep is not the only remedy; an authenticated append-only calibration registry supplied to the selector would also close it.

Checks performed — clean areas:

- V4 and the complete boundary sweep land correctly: exact screen passes; exact ceiling passes with observed `0.012093166090593858`; one decimal unit and one binary64 ULP beyond refuse; zero drift passes with allowance `0.010818`.
- The original V5 returns stale, V6 rekey refuses stale, and the legacy basis remains `e1e93a54eb17a7d9eeb3766659d879dc388c4bbe4a90694c668b12860b4ee959`.
- Production decimal flow retains the evidence lexeme through range, preflight, drift, excess, and allowance comparisons. Binary64 projections do not replace the local Decimal values. The float-only compatibility branch is not reachable from authenticated candidate loading.
- File and mapping pinning close F3’s self-rekey attack. A future legitimate re-fit is deliberately blocked until an atomic reviewed update changes the artifact, byte pin, estimator digests, and any D-102-derived validator constants. No runtime self-authorization path exists.
- Artifact reconstruction accounts for every changed leaf: two new estimator digests plus `derivation_sha256` `0dee15fe… → daeaafbc…`. Identity epoch, all 19 members, and every decimal leaf are unchanged. The reconstructed old and current file hashes are exactly `ade322ab…` and `9a03e581…`.
- All 19 stored lexemes and manifest/evidence hashes match. Statistics reproduce exactly: n=19, min `0.022741007370546462`, max `0.03355875667989999`, range `0.010817749309353528`, mean `0.026950033977532761`, sample SD `0.002970761365307205`.
- Four 2026-07-22 members independently matched their evidence lexeme and both SHA-256s. The two available a10 raw captures physically re-fit exactly to `0.024879191521227362` and `0.025045994537554683`.
- T1 candidate selection remains exact, window A remains bracket-unformable, and window B’s systematic preflight shape remains refused.
- The real-reducer integration patches only the two unrelated environment-admission functions. It proves real selector → candidate authentication → physical verification → reducer/re-reducer → single allowance embedding, but intentionally proves nothing about environment admission.
- `claims.py` adds only `calibration_acceptance_bound_stale` to `REDUCER_REASON_CODES`; classification remains inherited through `_NOT_RESOLVABLE`.
- No repository files were modified by this audit.

## Residual risk

Before landing, the lead must run the authoritative full suite, repeat the bench corpus checks, recover archived raw custody and physically re-fit at least two additional members, and complete a real passed-corpus evaluation-basis replay. The lack of a literal old artifact at `a14d1fe` should also be reconciled in retained audit custody, although the exact old SHA was reconstructed successfully.