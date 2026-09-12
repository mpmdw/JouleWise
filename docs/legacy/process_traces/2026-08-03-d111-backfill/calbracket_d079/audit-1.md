```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FAIL: three claim-semantic blockers exist in Decimal boundary handling and D-102 freshness/provenance enforcement; the suite is green but does not cover them.",
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
        "title": "Binary64 endpoint storage falsely refuses an exact D-102 ceiling",
        "evidence": "joulewise/calibration_bracketing.py:69,414,596-614,667-684",
        "scenario": "Decimal endpoints 0.020 and 0.032093166090593858 have exact drift 0.012093166090593858 and must pass inclusively; conversion to float changes the post endpoint to 0.03209316609059386 and the implementation refuses observed drift 0.01209316609059386."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Mandatory prospective freshness triggers do not stale the old artifact",
        "evidence": "joulewise/calibration_bracketing.py:561-570,632-646",
        "scenario": "A prior same-identity capture expands the observed range, but a later window selecting newer normal endpoints passes as fresh with observed_triggers=[]; the old artifact can therefore license later claims without mandatory re-derivation."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "Alternate acceptance artifacts can rekey the old corpus to another identity",
        "evidence": "joulewise/calibration_bracketing.py:104-168,251-266,433-478",
        "scenario": "Changing the old n=19 artifact identity from OS 25F84 to 25F85 and recomputing its unkeyed derivation digest produces a fresh passing bound for 25F85 through the exported acceptance_bound path; corpus-member identities are never authenticated from primary evidence."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "Regressions omit the exact-boundary and freshness-bypass cases",
        "evidence": "tests/test_calibration_bracketing.py:128-276; tests/test_whole_window_selection.py:1834-1915",
        "scenario": "The artifact-tamper test does not recompute derivation_sha256, and no test exercises exact ceiling arithmetic, an unselected range-expander, or a rekeyed alternate artifact. The D-079 whole-window linkage test also mocks both selection and re-reduction."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "set -o pipefail\n/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest discover -s tests -v 2>&1 | tee /tmp/calbracket-unittest-v.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2426 tests in 580.219s",
          "OK (skipped=85)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=85\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_calibration_bracketing tests.test_whole_window_selection -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 60 tests in 7.230s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
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
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -c \"from decimal import Decimal;from tests.test_calibration_bracketing import CalibrationBracketingTests as T;from joulewise.calibration_bracketing import evaluate_calibration_bracket as e;t=T();t.setUp();a=Decimal('0.020');d=Decimal('0.012093166090593858');r,x=e([t.candidate('pre',99,float(a)),t.candidate('post',111,float(a+d))],window_start_s=100,window_end_s=110,bindings=t.bindings,policy=t.policy);print(r['status'],x,r['acceptance']['drift']['observed_s'])\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "failed ('instrument_calibration_mismatch',) 0.01209316609059386"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "passed \\(\\) 0.012093166090593858"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -c \"from tests.test_calibration_bracketing import CalibrationBracketingTests as T;from joulewise.calibration_bracketing import evaluate_calibration_bracket as e;t=T();t.setUp();cs=[t.candidate('range-expander',99,.022),t.candidate('current-pre',199,.025),t.candidate('current-post',211,.026)];r,x=e(cs,window_start_s=200,window_end_s=210,bindings=t.bindings,policy=t.policy);print(r['status'],x,r['acceptance']['freshness']['status'],r['acceptance']['prospective_rederivation']['observed_triggers'])\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "passed () fresh []"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "calibration_acceptance_bound_stale"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -c \"import copy;from tests.test_calibration_bracketing import CalibrationBracketingTests as T;from joulewise.calibration_bracketing import load_calibration_acceptance_bound as l,_canonical_sha256 as h,evaluate_calibration_bracket as e;t=T();t.setUp();a=copy.deepcopy(l());a['identity_epoch']['os_build']='25F85';a['derivation_sha256']=h({k:v for k,v in a.items() if k!='derivation_sha256'});b=dict(t.bindings);b['os_build']='25F85';r,x=e([t.candidate('pre',99,.02,bindings=b),t.candidate('post',111,.021,bindings=b)],window_start_s=100,window_end_s=110,bindings=b,policy=t.policy,acceptance_bound=a);print(r['status'],x,r['acceptance']['freshness']['status'])\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "passed () fresh"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "calibration_acceptance_bound_stale"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "a14d1fe189734a9a58035736becb75612a85a157",
          "git diff --check: no output"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "a14d1fe189734a9a58035736becb75612a85a157"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The 85 skips comprise 64 advisory site-lane tests, 9 matplotlib tests, 3 jsonschema tests, 3 socket-dependent tests, and 6 worktree-corpus/path-dependent tests.",
      "needs": "Run the six corpus/path-dependent tests from the bench checkout with retained runs/ evidence; run optional site/dependency lanes if required by the lead gate."
    },
    {
      "id": "FL2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Only the two a10 corpus members retain raw powermetrics bytes locally; 17/19 member directories retain manifest/evidence summaries but not raw captures. A full physical re-fit of four members was therefore impossible here.",
      "needs": "Recover archived raw custody and independently rederive at least two additional corpus members at the lead gate."
    },
    {
      "id": "FL3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "A full current-head replay of the 47-member real window-C verdict was interrupted during its expensive raw fiducial re-reduction; synthetic legacy-basis hashing and the smaller a9 base/current comparison were identical.",
      "needs": "Complete a real passed-corpus base/current replay at the bench."
    }
  ]
}
```

## Findings

F1 — blocker: exact Decimal acceptance is not preserved.

The comparator constants are pinned correctly, but endpoint values have already become floats before the drift is formed: `CalibrationCandidate.b_fiducial_s` is a float at `joulewise/calibration_bracketing.py:69`, production loading casts the rederived result at line 414, and lines 596–608 merely apply `Decimal(str(...))` after that loss.

Boundary sweep:

- Below screen: passes with allowance `0.010818`.
- Exactly screen: passes.
- Exactly `screen + cap`: incorrectly refuses.
- One decimal unit or one binary64 ULP beyond: refuses.
- Zero drift: passes with nonzero allowance `0.010818`.
- Negative endpoint bound: refuses `instrument_calibration_invalid`.

This is claim-blocking under the requested severity rule.

F2 — blocker: prospective freshness is observational only and incomplete.

Lines 632–646 test range expansion only for the selected `pre` and `post`. An earlier authenticated same-identity capture outside the n=19 range disappears from trigger evaluation once a newer pre-calibration is selected. The later window then passes under the obsolete artifact as `fresh`.

Additionally, D-102’s `protocol_or_estimator_byte_change` trigger is not mechanically complete: the artifact binds the protocol JSON digest, but neither the artifact nor protocol file carries an estimator-code digest.

F3 — blocker: alternate artifact provenance is self-rekeyable.

The default checked-in artifact is byte-pinned and a plain observed-identity change correctly returns `calibration_acceptance_bound_stale`. However, the exported optional `acceptance_bound` route validates only a recomputable canonical digest and formatted member hashes. It does not authenticate the member evidence’s identity epoch. The old corpus can therefore be relabelled for OS `25F85`, rehashed, and accepted as fresh.

F4 — should fix: the new tests miss all three blocker shapes.

The artifact tamper at `tests/test_calibration_bracketing.py:271-276` changes a member without recomputing `derivation_sha256`, so digest rejection alone satisfies it. An independent rehashed-member tamper did refuse, confirming the arithmetic validator itself is sound, but the regression does not prove that behavior.

The D-079 whole-window linkage test verifies scalar pass-through with mocked selection and mocked re-reduction. Existing real reducer tests support the single-embedding path, but an integrated selector-to-real-reducer regression would better pin it.

Checks performed — clean areas:

- Pin fidelity is otherwise exact at `joulewise/calibration_bracketing.py:54-59` and `configs/calibration/calibration_acceptance_d079_v2.json:171-218`. Artifact SHA-256 is `ade322ab485813c39dfb5f5ffb3c8bfe89c86d23b94a4d858238bf1b9af4e8f2`. Presentation-only values are labelled.
- Allowance construction is correct at `calibration_bracketing.py:686-702`: `max(drift, 0.010818)` is positive and embedded once in `b_fiducial_s`.
- Downstream consumption passes that operative scalar once at `whole_window.py:461-480,576-580`; the reducer substitutes it as the fiducial component at `reduce.py:1820-1845`. No second calibration-drift energy term was added. The existing NEG-8 whole-window energy allowance is a distinct D-078 term.
- Candidate byte authentication and exact ten-field T1 matching remain unchanged at `calibration_bracketing.py:317-416,552-559`. Latest-pre/earliest-post selection remains intact.
- Real window A authenticated only its original pre and T1-incompatible deviation post; current evaluation returned `pre=None`, `post=None`, `instrument_calibration_bracket_missing`.
- Four stored-evidence spot checks—including min, max, first, and final members—matched `b_fiducial_s` lexemes and both byte SHA-256s. All 19 artifact rows matched the banked statistics through V3. The two locally retained a10 raw captures also physically rederived exactly.
- The four intended defect assertions are red on the archived `a14d1fe` tree: no allowance embedding, 11 ms drift refusal, identity change passing, and no D-079 basis fields. Fence regressions such as T1 mismatch correctly remain green on base.
- A legacy bracket without an acceptance object produced the identical base/current evaluation-basis hash `e1e93a54eb17a7d9eeb3766659d879dc388c4bbe4a90694c668b12860b4ee959`.
- `claims.py:61` only adds the new refusal spelling; existing vocabulary/classification is unchanged.

## Residual risk

`verify_calibration_acceptance_corpus.py:29-82` does re-read every listed `manifest.json` and `instrument_evidence.json`, compare stored decimal lexemes, recompute both file hashes, and recompute summary statistics. It trusts the artifact’s member list, does not discover whether the set is complete, does not authenticate each manifest’s internal artifact graph, and does not rerun fiducial physics.

The lead gate should fix F1–F3, add the missing adversarial regressions, recover archived raw evidence for two more physical corpus rederivations, complete a real passed-window base/current replay, and rerun the six corpus-dependent tests from the bench checkout.