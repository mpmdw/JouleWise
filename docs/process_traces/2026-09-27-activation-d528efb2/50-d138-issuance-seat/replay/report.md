```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "REPLAY: PASS — all six independent replay items and all additional estimator, cap, ancestry, and diff checks passed.",
  "workspace": {
    "base_requested": "c81f65b8",
    "base_mode": "exact",
    "head_start": "c81f65b8b703f348c0e2375407782028a5d3057b",
    "head_end": "c81f65b8b703f348c0e2375407782028a5d3057b",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "replay": "PASS"
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
          "issued sha256=9e5c735bf7b4d27604bfadd87809750974322258b943fd1afb04d1873e824c06"
        ],
        "item": "i",
        "committed_bytes_and_registry_pin": "Independently confirmed by V2."
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^issued sha256=9e5c735bf7b4d27604bfadd87809750974322258b943fd1afb04d1873e824c06$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay-d528efb2/independent/check_bytes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["BYTE AND BINDING CHECKS PASS"],
        "item": "ii, plus i pin authentication",
        "protected_paths": 22,
        "comparison": "Parsed values and original serialized source spans identical; all line-diff changes confined to section 5.5.",
        "candidate_sha256": "dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2",
        "issued_sha256_equals_registry": "9e5c735bf7b4d27604bfadd87809750974322258b943fd1afb04d1873e824c06",
        "input_seal_both": "e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011",
        "candidate_whole_seal": "fac6e6f89e764dc4b00516d9a35f5d1c1eaca9821e76725f5f1fb66b5b206073",
        "issued_whole_seal": "2e0d88b5e0186f43a6d7fc45810e5ca78cb7aa8c75fafce78710e282d5de017b"
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "BYTE AND BINDING CHECKS PASS"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay-d528efb2/independent/independent_math.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["iii INDEPENDENT STATISTICS PASS"],
        "item": "iii",
        "method": "80-digit Decimal; independent transformed-density binomial integration and bisection; pi by Gauss-Legendre AGM; no repository imports. Registered binary64 prediction multiplication retained.",
        "n": 12,
        "df": 11,
        "t975": "2.20098516009163986788",
        "t995": "3.10580651553928100710",
        "sample_sd_presentation_s": "0.004330477884879059",
        "S": "0.013701",
        "C": "0.01902064410651988",
        "level_screen_s": "0.038078579302948",
        "maximum_excess_s": "0.00531964410651988",
        "comparison": "Exact printed-digit matches."
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "iii INDEPENDENT STATISTICS PASS"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B scripts/issue_calibration_acceptance_generation.py verify-members --artifact /Users/edr/code/JouleWise-wt-d138-replay-d528efb2/configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json --corpus-root /Users/edr/night-custody",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "member \"d079-epoch-25g83-derivation-w2-20260927-d10\": PASS"
        ],
        "item": "iv",
        "members_pass": 12,
        "members_fail": 0,
        "custody_files_hashed_before_and_after": 84,
        "all_custody_digests_unchanged": true,
        "before_after_manifest_sha256": "38b471f7a12d932c7b62ed91f4d1709e0c04010c8832becf2f1f578daab7f880"
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "member .*d10.*: PASS"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay-d528efb2/independent/custody_replay.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "v D3 PASS byte_equal=True sha256=dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2",
          "custody files unchanged 84 ledger unchanged=True",
          "CUSTODY AND D3 PASS"
        ],
        "item": "v",
        "D3_source": "docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/run1-command.txt",
        "execution": "Replayed recorded prepare-candidate arguments with /opt/homebrew/bin/python3 -B, scratch output, and explicit real W2 ledger path; all other recorded arguments retained.",
        "output": "/tmp/d138-replay-d528efb2/independent/D3-candidate.json",
        "candidate_byte_equal": true
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CUSTODY AND D3 PASS"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay-d528efb2/independent/freshness.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "vi FRESHNESS PASS default 25G83=fresh explicit R7 25F84=fresh"
        ],
        "item": "vi",
        "ledger": "/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl",
        "ledger_sequence": 276,
        "ledger_head": "476e2ae857d4d6279bfa3c59c39bb5bc6f983d282948ce0abb95e3df62d49737",
        "ledger_sha256_before_and_after": "23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d",
        "default_25G83": "fresh",
        "explicit_R7_25F84": "fresh",
        "stale_fields_both": [],
        "snapshot_authentication": "valid; committed pin required; read_replay; baselines 276 and 76"
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "vi FRESHNESS PASS default 25G83=fresh explicit R7 25F84=fresh"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "shasum -a 256 joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92  joulewise/powermetrics_fiducial.py",
          "b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8  joulewise/uncertainty_evidence.py",
          "70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4  joulewise/adapters/powermetrics.py",
          "7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc  joulewise/reduce.py"
        ],
        "comparison": "All four full digests equal science addendum A1 binding B1 and the candidate estimator block."
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc  joulewise/reduce.py"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay-d528efb2/independent/check_bytes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["BYTE AND BINDING CHECKS PASS"],
        "DETECTION_PROJECTION_CELL_BUDGET": 165000
      },
      "expected": {"exit_code": 0, "tail_regex": "BYTE AND BINDING CHECKS PASS"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay-d528efb2/independent/check_bytes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["BYTE AND BINDING CHECKS PASS"],
        "ancestry": "git merge-base --is-ancestor <commit> HEAD returned 1 separately for bda7ffe0, aeea07b6, ea10e3c8, and 5135c1d2."
      },
      "expected": {"exit_code": 0, "tail_regex": "BYTE AND BINDING CHECKS PASS"}
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-replay-d528efb2/independent/check_bytes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["estimator diff intersection=[]", "BYTE AND BINDING CHECKS PASS"],
        "diff": "git diff --name-only e7c8bcc6...HEAD names none of the four estimator files."
      },
      "expected": {"exit_code": 0, "tail_regex": "BYTE AND BINDING CHECKS PASS"}
    }
  ],
  "flags": []
}
```

REPLAY: PASS

## Findings

None. Repository clean; HEAD unchanged. Writes confined to authorized scratch. No capture, powermetrics execution, live battery read, or Claude call.

Replay scripts, exact D3 command, logs, line diff, and per-file custody digests are in [independent replay evidence](/tmp/d138-replay-d528efb2/independent).

## Residual risk

Freshness checks used explicit epoch identities and no bracket endpoints; both also returned `instrument_calibration_bracket_missing`. They establish freshness, not measurement readiness.

This seat completed §9 step 2. The lead retains the remaining transaction gates and final verification.