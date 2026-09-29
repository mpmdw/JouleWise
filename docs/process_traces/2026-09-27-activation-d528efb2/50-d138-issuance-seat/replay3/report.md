```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "REPLAY: PASS — all requested checks passed at b953f4b0; repository, custody files and real ledger unchanged.",
  "workspace": {
    "base_requested": "b953f4b0",
    "base_mode": "exact",
    "head_start": "b953f4b0119f0e05bf02cb9ac206eaf4498b08e3",
    "head_end": "b953f4b0119f0e05bf02cb9ac206eaf4498b08e3",
    "upstream_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "replay": "PASS",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B scripts/promote_calibration_candidate.py --check configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "issued sha256=d7076c78ddab564c9b7eefa9a24b658bdbbdd29b685373de7cb66cf48c565c2e"
        ],
        "item": "(i)",
        "independent_pin_check": "V2 independently hashed the file, matched the registry pin and compared its bytes with git show HEAD."
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "issued sha256=d7076c78ddab564c9b7eefa9a24b658bdbbdd29b685373de7cb66cf48c565c2e"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay3-d528efb2/bytes_bindings.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "HEAD=b953f4b0119f0e05bf02cb9ac206eaf4498b08e3"
        ],
        "item": "(ii), independent file pin and seals",
        "protected_paths": 22,
        "parsed_values_equal": true,
        "original_serialized_values_equal": true,
        "line_diff_only_allowed": true,
        "issued_sha256": "d7076c78ddab564c9b7eefa9a24b658bdbbdd29b685373de7cb66cf48c565c2e",
        "input_seal": "e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011",
        "whole_file_seal": "d3e4da75cdd99b36caeef8a0145c8a0ea430d08604abad6faeb69a0dd3ad420a"
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "HEAD=b953f4b0119f0e05bf02cb9ac206eaf4498b08e3"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay3-d528efb2/numerics.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "iii PASS precision=80 S=0.013701 C=0.01902064410651988 level=0.038078579302948 excess=0.00531964410651988 printed_digits_equal=True"
        ],
        "item": "(iii)",
        "member_count": 12,
        "quantile_method": "Independent integration of the df=11 Student-t density using t=sqrt(11)*tan(theta), a cos^10 integral recurrence, independently calculated pi and 300 bisections; no repository quantile imports.",
        "t_975_printed": "2.20098516009163986788",
        "t_995_printed": "3.10580651553928100710",
        "mean_printed": "0.029591582579198539",
        "sample_sd_printed": "0.004330477884879059",
        "range": "0.013701485381050852",
        "prediction_95": "0.013479318561660503",
        "prediction_99": "0.01902064410651988",
        "prediction_arithmetic": "Registered binary64 multiplication using rounded sample SD, following 80-digit Decimal derivation."
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "iii PASS .*printed_digits_equal=True"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay3-d528efb2/custody_d3.py > /tmp/d138-replay3-d528efb2/custody_d3.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "iv PASS custody_files=84 all_digests_unchanged=True ledger_unchanged=True"
        ],
        "item": "(iv)",
        "executed_child_command": "/opt/homebrew/bin/python3 -B scripts/issue_calibration_acceptance_generation.py verify-members --artifact configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json --corpus-root /Users/edr/night-custody",
        "members_pass": 12,
        "members_fail": 0,
        "custody_files_hashed_before_and_after": 84,
        "ledger_sha256": "23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d"
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "iv PASS custody_files=84 all_digests_unchanged=True ledger_unchanged=True"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay3-d528efb2/custody_d3.py > /tmp/d138-replay3-d528efb2/custody_d3.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "D3 byte_equal=True sha256=dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2",
          "v PASS custody_files=84 all_digests_unchanged=True ledger_unchanged=True"
        ],
        "item": "(v), D3",
        "executed_child_command": "/opt/homebrew/bin/python3 -B scripts/issue_calibration_acceptance_generation.py prepare-candidate --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md --preregistration-sha256 81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1 --registration-session-id d079-epoch-25g83-derivation-w1-20260927 --registration-session-id d079-epoch-25g83-derivation-w2-20260927 --d125-ruling 'docs/decision_log.md, D-125 addendum (2026-09-25): Revision 5 screen and ceiling for epoch 25G83/v3 (ACCEPTANCE-25G83-02 §5 R5(i), R9)' --out /tmp/d138-replay3-d528efb2/D3-candidate.json --corpus-root /Users/edr/night-custody --predecessor-acceptance configs/calibration/calibration_acceptance_d079_v2_n17_r7.json --ledger /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl",
        "candidate_byte_equal": true
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "v PASS custody_files=84 all_digests_unchanged=True ledger_unchanged=True"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay3-d528efb2/freshness.py > /tmp/d138-replay3-d528efb2/freshness.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "vi-a PASS default_R7 25G83=stale stale_fields=[os_build] 25F84=fresh stale_fields=[]"
        ],
        "item": "(vi-a)",
        "default_acceptance": "d079_calibration_acceptance_v2_n17_r7",
        "real_ledger_head_sequence": 276,
        "real_ledger_head_digest": "476e2ae857d4d6279bfa3c59c39bb5bc6f983d282948ce0abb95e3df62d49737"
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "vi-a PASS default_R7 25G83=stale.*25F84=fresh"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay3-d528efb2/freshness.py > /tmp/d138-replay3-d528efb2/freshness.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "vi-b PASS reason=acceptance_artifact_claim_held artifact=None"
        ],
        "item": "(vi-b)",
        "content_source": "calibration_bracketing.inspect_acceptance_without_claim_authority",
        "production_loader_returned": null,
        "evaluation_artifact": null,
        "refusal": "acceptance_artifact_claim_held"
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "vi-b PASS reason=acceptance_artifact_claim_held artifact=None"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay3-d528efb2/freshness.py > /tmp/d138-replay3-d528efb2/freshness.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "vi-c PASS in_memory_hold_empty 25G83=fresh stale_fields=[] hold_restored=True",
          "ledger_sha256=23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d unchanged=True"
        ],
        "item": "(vi-c)",
        "mutation_scope": "CLAIM_HELD_OS_BUILDS cleared only in scratch process memory, then restored."
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ledger_sha256=23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d unchanged=True"
      }
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay3-d528efb2/bytes_bindings.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "bindings PASS diff_estimator_paths=[]",
          "HEAD=b953f4b0119f0e05bf02cb9ac206eaf4498b08e3"
        ],
        "item": "Additional estimator, cap and ancestry bindings",
        "estimator_sha256": {
          "joulewise/powermetrics_fiducial.py": "386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92",
          "joulewise/uncertainty_evidence.py": "b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8",
          "joulewise/adapters/powermetrics.py": "70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4",
          "joulewise/reduce.py": "7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc"
        },
        "DETECTION_PROJECTION_CELL_BUDGET": 165000,
        "merge_base_is_ancestor_exit_codes": {
          "bda7ffe0": 1,
          "aeea07b6": 1,
          "ea10e3c8": 1,
          "5135c1d2": 1
        },
        "git_diff_e7c8bcc6_triple_dot_HEAD_estimator_paths": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "HEAD=b953f4b0119f0e05bf02cb9ac206eaf4498b08e3"
      }
    }
  ],
  "flags": []
}
```

REPLAY: PASS

## Findings

None. All requested items passed independently. Repository write scope remained empty; scratch evidence is under [/tmp/d138-replay3-d528efb2](/tmp/d138-replay3-d528efb2).

## Residual risk

This verifies the requested replay. Freshness probes used no bracket endpoints, so “fresh” does not establish a passing measurement bracket. No capture, powermetrics session, or live battery read occurred.

Next step: the lead incorporates this evidence into the remaining ruling §7 gates and final verification.