```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented all four D-102/D-079 audit fixes; focused, audit-probe, primary-evidence, legacy-hash, and 2433-test full-suite verification pass.",
  "workspace": {
    "base_requested": "a14d1fe",
    "base_mode": "exact",
    "head_start": "a14d1fe189734a9a58035736becb75612a85a157",
    "head_end": "a14d1fe189734a9a58035736becb75612a85a157",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [
    "joulewise/calibration_bracketing.py",
    "configs/calibration/calibration_acceptance_d079_v2.json",
    "tests/test_calibration_bracketing.py",
    "tests/test_reduce.py",
    "tests/test_whole_window_selection.py"
  ],
  "unowned_dirty": [
    "joulewise/analysis_engine/claims.py",
    "joulewise/whole_window.py",
    "tests/verify_calibration_acceptance_corpus.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
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
          "----------------------------------------------------------------------",
          "Ran 321 tests in 69.753s",
          "",
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
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -c \"from decimal import Decimal;from tests.test_calibration_bracketing import CalibrationBracketingTests as T;from joulewise.calibration_bracketing import evaluate_calibration_bracket as e;t=T();t.setUp();a=Decimal('0.020');d=Decimal('0.012093166090593858');r,x=e([t.candidate('pre',99,float(a)),t.candidate('post',111,float(a+d))],window_start_s=100,window_end_s=110,bindings=t.bindings,policy=t.policy);print(r['status'],x,r['acceptance']['drift']['observed_s'])\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "passed () 0.012093166090593858"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^passed \\(\\) 0\\.012093166090593858$"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -c \"from tests.test_calibration_bracketing import CalibrationBracketingTests as T;from joulewise.calibration_bracketing import evaluate_calibration_bracket as e;t=T();t.setUp();cs=[t.candidate('range-expander',99,.022),t.candidate('current-pre',199,.025),t.candidate('current-post',211,.026)];r,x=e(cs,window_start_s=200,window_end_s=210,bindings=t.bindings,policy=t.policy);print(r['status'],x,r['acceptance']['freshness']['status'],r['acceptance']['prospective_rederivation']['observed_triggers'])\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "failed ('calibration_acceptance_bound_stale',) stale ['new_valid_same_identity_capture_expands_observed_range']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "calibration_acceptance_bound_stale.*new_valid_same_identity_capture_expands_observed_range"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -c \"import copy;from tests.test_calibration_bracketing import CalibrationBracketingTests as T;from joulewise.calibration_bracketing import load_calibration_acceptance_bound as l,_canonical_sha256 as h,evaluate_calibration_bracket as e;t=T();t.setUp();a=copy.deepcopy(l());a['identity_epoch']['os_build']='25F85';a['derivation_sha256']=h({k:v for k,v in a.items() if k!='derivation_sha256'});b=dict(t.bindings);b['os_build']='25F85';r,x=e([t.candidate('pre',99,.02,bindings=b),t.candidate('post',111,.021,bindings=b)],window_start_s=100,window_end_s=110,bindings=b,policy=t.policy,acceptance_bound=a);print(r['status'],x,r['acceptance']['freshness']['status'])\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "failed ('calibration_acceptance_bound_stale',) stale"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^failed \\('calibration_acceptance_bound_stale',\\) stale$"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -c \"from joulewise.whole_window import build_evaluation_basis;bracket={'pre':{'manifest_sha256':'a'*64,'evidence_sha256':'b'*64,'b_fiducial_s':.02},'post':{'manifest_sha256':'c'*64,'evidence_sha256':'d'*64,'b_fiducial_s':.021},'b_fiducial_s':.021,'status':'passed'};basis=build_evaluation_basis(policy_sha256='e'*64,member_occurrences=[{'bundle_id':'m','bundle_path':'m'}],calibration_bracket=bracket);print(basis['sha256'],basis['calibration_bracket_set'])\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "e1e93a54eb17a7d9eeb3766659d879dc388c4bbe4a90694c668b12860b4ee959 {'pre': {'manifest_sha256': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'evidence_sha256': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'b_fiducial_s': 0.02}, 'post': {'manifest_sha256': 'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc', 'evidence_sha256': 'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd', 'b_fiducial_s': 0.021}}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^e1e93a54eb17a7d9eeb3766659d879dc388c4bbe4a90694c668b12860b4ee959 "
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_whole_window_selection.MaxBracketConsumptionTests.test_d079_real_selector_to_real_reducer_embeds_allowance_once",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 1 test in 37.328s",
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
      "id": "V7",
      "kind": "inspection",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B tests/verify_calibration_acceptance_corpus.py --repo-root /Users/edr/code/JouleWise --artifact configs/calibration/calibration_acceptance_d079_v2.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "n=19 min=0.022741007370546462 (20260722T215127-eeef661a)",
          "max=0.03355875667989999 (20260722T222332-901c5c13) range=0.010817749309353528",
          "mean=0.026950033977532761 sample_sd=0.002970761365307205",
          "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK$"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "shasum -a 256 configs/calibration/calibration_acceptance_d079_v2.json joulewise/powermetrics_fiducial.py joulewise/reduce.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "9a03e5810862a96544b9051926f7b80c02c7a197523d3f758cfe29c28e19050e  configs/calibration/calibration_acceptance_d079_v2.json",
          "21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3  joulewise/powermetrics_fiducial.py",
          "5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615  joulewise/reduce.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615  joulewise/reduce.py$"
      }
    },
    {
      "id": "V9",
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
      "id": "V10",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 2433 tests in 614.763s",
          "",
          "OK (skipped=85)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2433 tests in .*s\\n\\nOK \\(skipped=85\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "ENV-RUFF",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Optional Ruff check could not run because the repository venv reports: /Users/edr/code/JouleWise/.venv/bin/python: No module named ruff.",
      "needs": ""
    },
    {
      "id": "RISK-INTEGRATION-FIXTURE",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The real reducer integration neutralizes only two unrelated environment-admission functions because the retained fixture predates their custody schema; selector, candidate authentication, calibration verification, reducer, and re-reducer are real.",
      "needs": "Lead should confirm this fixture boundary is acceptable."
    }
  ]
}
```

## Change

- FIX-1 — complete. Authenticated evidence retains the source decimal lexeme through candidate selection and D-102 drift/preflight/allowance comparisons. Binary64 projection occurs only in recorded descriptor/reducer fields. Regressions cover exact screen, exact screen-plus-cap inclusive, one decimal unit beyond, one binary64 ULP beyond, and zero drift.

- FIX-2 — complete. Prospective triggers scan every authenticated same-identity candidate in the supplied set, including unselected range expanders. The acceptance record explicitly identifies that boundary and records that no global runs-root scan occurred. Estimator authentication binds `joulewise/powermetrics_fiducial.py`, which authenticates/rederives `b_fiducial_s`, and `joulewise/reduce.py`, which performs anchor-envelope re-reduction. Those are the code paths D-102 identifies; orchestration and formatting modules were excluded.

- FIX-3 — complete using option (a). Every file-based acceptance artifact must match the checked-in byte SHA-256, and an explicitly supplied mapping must equal the authenticated pinned artifact. This supplies an external trust root; recomputing an unkeyed derivation digest cannot authorize self-asserted identity fields.

- FIX-4 — complete. Added the rehashed-member arithmetic-validator test, full decimal boundary sweep, unselected-expander test, rekey refusal, legacy-basis hash pin, Window-A and Window-B semantic guards, estimator-byte mismatch test, and selector-to-real-reducer single-embedding regression.

The acceptance artifact’s old SHA-256 was `ade322ab485813c39dfb5f5ffb3c8bfe89c86d23b94a4d858238bf1b9af4e8f2`; the regenerated SHA-256 is `9a03e5810862a96544b9051926f7b80c02c7a197523d3f758cfe29c28e19050e`. Its new derivation digest is `daeaafbcc97487906c6525948529d2ef230a55c91f60ffb005666b32dda19d66`. Every D-102 decimal remains unchanged.

Changed files: [calibration_bracketing.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket/joulewise/calibration_bracketing.py), [calibration_acceptance_d079_v2.json](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket/configs/calibration/calibration_acceptance_d079_v2.json), [test_calibration_bracketing.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket/tests/test_calibration_bracketing.py), [test_reduce.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket/tests/test_reduce.py), and [test_whole_window_selection.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket/tests/test_whole_window_selection.py).

## Verification notes

An intermediate exploratory command contained a nonexistent unittest selector and failed at selector loading; it was superseded by the clean 321-test focused run and 2433-test canonical suite. The optional Ruff command also could not run because Ruff is not installed in the venv.

No commit was created. HEAD remains `a14d1fe189734a9a58035736becb75612a85a157`.

## Residual risk

The lead should double-check the two-file estimator-byte boundary, the checked-in artifact/pin pair when staging, and the narrowly patched environment-admission boundary in the real-reducer fixture. Pre-existing edits in `claims.py`, `whole_window.py`, and the untracked corpus verifier were preserved.