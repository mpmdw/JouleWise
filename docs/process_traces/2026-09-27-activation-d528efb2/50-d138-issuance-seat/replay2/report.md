```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "REPLAY: FAIL — items (i)–(v) and estimator guards pass; item (vi) requires a ruling because the required claim hold prevents fresh evaluation.",
  "workspace": {
    "base_requested": "8458f797",
    "base_mode": "exact",
    "head_start": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "head_end": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "upstream_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "return": "NEEDS_RULING",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Item (vi)'s fresh expectation conflicts with the required hold refusal",
        "location": "joulewise/calibration_bracketing.py:1337",
        "observed": "Loading the new file with allow_claim_held=True succeeds, but evaluate_calibration_bracket re-authenticates it through the loader without that keyword. Evaluation returns stale / acceptance_artifact_claim_held.",
        "authority_conflict": "Addendum section 8.1 step 4 requires fresh; section 3.3 R-3 through R-5 requires this refusal, which tests/test_claim_hold_routes.py:146 also asserts.",
        "question": "Which non-claim evaluation procedure is authorized to establish the new file's freshness while preserving the production hold?",
        "options_considered": [
          "Authorize an explicitly isolated, in-memory governance replay that supplies the keyword during re-authentication.",
          "Revise item (vi) to require the observed hold refusal.",
          "Change production evaluation behavior; this would require a new ruling and write scope."
        ],
        "recommendation": "Specify the isolated non-claim replay procedure while preserving the production refusal.",
        "blocked_work": "Certifying item (vi) and returning REPLAY: PASS."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay2-d528efb2/replay.py i",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "promote_calibration_candidate.py --check exited 0; issued bytes equal HEAD.",
          "issued_sha256=d6de84b854a4c5d7f6d73dfde2ae0f14d71a483355c7289a36882e0dfcccd5ea; equals registry pin.",
          "candidate_sha256=dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2",
          "recomputed_input_seal=e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011",
          "recomputed_candidate_whole_seal=fac6e6f89e764dc4b00516d9a35f5d1c1eaca9821e76725f5f1fb66b5b206073",
          "recomputed_issued_whole_seal=8726a11bd4da79fe20cdca5321bf554cd11f6903a39b0710af6db2fd93de3333",
          "i PASS"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "i PASS"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay2-d528efb2/replay.py ii",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Independent source-span comparison: all 22 protected paths equal in parsed value and original serialized text.",
          "All six line-diff groups confined to section 5.5's permitted lines.",
          "ii PASS protected_paths 22 members=12 prior_rows=86"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "ii PASS protected_paths 22 members=12 prior_rows=86"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay2-d528efb2/replay.py iii",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Independent Student-t computation: transformed-density binomial integration, Gauss-Legendre pi, bisection; Decimal precision 80; no repository quantile imports.",
          "t(0.975,11)=2.20098516009163986788; t(0.995,11)=3.10580651553928100710",
          "CDF residuals: 1E-80 and 2E-80.",
          "sample_sd_presentation_s=0.004330477884879059",
          "prediction_95_two_draw_s=0.013479318561660503; prediction_99_two_draw_s=0.01902064410651988",
          "S=0.013701; C=0.01902064410651988; level=0.038078579302948; excess=0.00531964410651988",
          "All operatives match to the printed digit, using the registered binary64 prediction step.",
          "iii PASS precision=80 independently_computed_t=True"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "iii PASS precision=80 independently_computed_t=True"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay2-d528efb2/replay.py iv",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Executed scripts/issue_calibration_acceptance_generation.py verify-members --artifact configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json --corpus-root /Users/edr/night-custody.",
          "12 member PASS results; verifier exit 0.",
          "iv PASS members=12 custody_files=84 before_after_equal=True manifest_sha256=24e50cf4c5a1b05d42c9889208707b461330ac729cb3b0520a459b7143d98ef4"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "iv PASS members=12 custody_files=84 before_after_equal=True"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay2-d528efb2/replay.py v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "D3 located through the recorded 30-run1/run1-command.txt; original preparation arguments retained, with requested interpreter, scratch output, and explicit real-ledger path.",
          "candidate written (NOT ISSUED): /tmp/d138-replay2-d528efb2/candidate-D3.json",
          "corpus n: 12",
          "screen_rule: floored_range_envelope_screen",
          "ledger_sha256 23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d unchanged=True",
          "v D3 PASS byte_equal=True sha256=dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2 custody_still_equal=True"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "v D3 PASS byte_equal=True"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay2-d528efb2/replay.py vi",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Real ledger: /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl",
          "Authenticated head: 276 / 476e2ae857d4d6279bfa3c59c39bb5bc6f983d282948ce0abb95e3df62d49737; no snapshot refusals.",
          "default R7 / 25G83: stale; stale_fields=['os_build'].",
          "default R7 / 25F84: fresh; stale_fields=[]; instrument_calibration_bracket_missing.",
          "New file loader: returned with allow_claim_held=True; None without keyword.",
          "New file / 25G83 evaluation: stale; reason=acceptance_artifact_claim_held; refusal=calibration_acceptance_bound_stale.",
          "Ledger and committed head-pin file digests unchanged.",
          "AssertionError: new file loaded with keyword does not evaluate fresh in unmodified evaluator"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "vi PASS"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay2-d528efb2/replay.py guards",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/powermetrics_fiducial.py 386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92",
          "joulewise/uncertainty_evidence.py b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8",
          "joulewise/adapters/powermetrics.py 70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4",
          "joulewise/reduce.py 7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc",
          "All four digests also compared directly with science addendum A1 B1.",
          "DETECTION_PROJECTION_CELL_BUDGET 165000",
          "git merge-base --is-ancestor <commit> HEAD returned 1 for each of bda7ffe0, aeea07b6, ea10e3c8, 5135c1d2.",
          "git diff --name-only e7c8bcc6...HEAD named none of the four estimator files.",
          "guards PASS four_estimator_files_absent_from_diff=True"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "guards PASS four_estimator_files_absent_from_diff=True"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "All requested replay items were executed, but item (vi)'s required fresh outcome conflicts with the intentionally enforced production hold. No bypass or production modification was attempted.",
      "needs": "Define the authorized non-claim freshness replay or amend the expected outcome, then resume this seat."
    }
  ]
}
```

REPLAY: FAIL

## Findings

**F1 — NEEDS_RULING.** Items (i)–(v), all four estimator digests, the cap, ancestry exclusions, and estimator diff guard pass.

The new file loads with `allow_claim_held=True`, but [explicit evaluation re-authenticates it without that keyword](/Users/edr/code/JouleWise-wt-d138-replay2-d528efb2/joulewise/calibration_bracketing.py:1337), producing `stale / acceptance_artifact_claim_held`. This is also the [required test expectation](/Users/edr/code/JouleWise-wt-d138-replay2-d528efb2/tests/test_claim_hold_routes.py:146).

The lead must specify an isolated non-claim freshness procedure or revise item (vi). I recommend preserving the production refusal and explicitly authorizing the governance replay.

Evidence: [replay script](/tmp/d138-replay2-d528efb2/replay.py), [freshness results](/tmp/d138-replay2-d528efb2/freshness-results.json), [digest manifest](/tmp/d138-replay2-d528efb2/evidence-sha256.json). Repository remains clean at `8458f797`; writes were confined to authorized scratch.

## Residual risk

Freshness probes used the real authenticated ledger and supplied epoch identities, with no bracket endpoints. They establish no measurement readiness or live hardware validation.