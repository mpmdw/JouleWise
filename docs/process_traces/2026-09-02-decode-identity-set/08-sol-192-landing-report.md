```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented declared decode identity sets, deterministic unit digests, frozen-set analysis binding, regression coverage, and replicable contract documentation.",
  "workspace": {
    "base_requested": "PR #269 merge head",
    "base_mode": "exact",
    "head_start": "e4f52e34f5d8f4ab21457edf3fd29d041d0e49ee",
    "head_end": "e4f52e34f5d8f4ab21457edf3fd29d041d0e49ee",
    "upstream_end": null,
    "branch": "fix/2026-09-02-decode-identity-set"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "docs/contracts/identity_pin_projection.md",
    "joulewise/analysis_engine/inputs.py",
    "joulewise/identity_pins.py",
    "tests/test_analysis_inputs.py",
    "tests/test_d117_contrast_v5_pack.py",
    "tests/test_identity_pins.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V0",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_v5_pack_freezes_and_verifies",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "IdentityPinProjectionError: identity unit 'A/decode' config declaration differs from pack",
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "config declaration differs from pack[\\s\\S]*FAILED \\(errors=1\\)"
      }
    },
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_identity_pins tests.test_analysis_inputs tests.test_mlx_runtime",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".........................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 121 tests in 14.579s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 121 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_d165_dominance_closeout tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "..........................................................................................",
          "----------------------------------------------------------------------",
          "Ran 90 tests in 7.543s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 90 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. python3 \"$TMPDIR/d117_v5_regeneration_verify.py\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "freeze_status=PASS",
          "verify_status=PASS",
          "{\"config_set_sha256\": \"636ce7b8e247a8ce3e80197380cd52ba3445d97ae0ddf3c8537d5cc4a3d95580\", \"distinct_identity_count\": 8, \"identity_unit_id\": \"A/decode\", \"manifest_census\": [4, 4, 2, 2, 2, 2, 2, 2], \"member_count\": 20}",
          "{\"config_set_sha256\": \"13cddd1dd8951782f362556c1da96dfab6a858c96def311135d4c8d4196e2926\", \"distinct_identity_count\": 1, \"identity_unit_id\": \"A/prefill_p512\", \"manifest_census\": [], \"member_count\": 20}",
          "{\"config_set_sha256\": \"99ceafec74ae0cec904e126a86ad3565536d522ba1987bde4e2ba99b3fcdb04e\", \"distinct_identity_count\": 8, \"identity_unit_id\": \"B/decode\", \"manifest_census\": [4, 4, 2, 2, 2, 2, 2, 2], \"member_count\": 20}",
          "{\"config_set_sha256\": \"f46d86f35dd2f0a30d2e902f0f27a4ca8a76cb9f12624e7d07775d495f336118\", \"distinct_identity_count\": 1, \"identity_unit_id\": \"B/prefill_p512\", \"manifest_census\": [], \"member_count\": 20}",
          "temp_root=<scratchpad>/tmp192/d117-v5-identity-regeneration-final-fdfpcxtf"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "freeze_status=PASS[\\s\\S]*verify_status=PASS[\\s\\S]*\"identity_unit_id\": \"B/prefill_p512\""
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'import hashlib,importlib.util,json,pathlib; p=pathlib.Path(\"configs/campaigns/d117_contrast_v5/generate_configs.py\"); s=importlib.util.spec_from_file_location(\"d117_v5_pin_check\",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(hashlib.sha256(json.dumps(m.dominance_criterion_registration(),sort_keys=True,separators=(\",\",\":\"),ensure_ascii=False,allow_nan=False).encode(\"utf-8\")).hexdigest())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " joulewise/identity_pins.py                         | 232 +++++++++++++-",
          " tests/test_analysis_inputs.py                      | 193 ++++++++++++",
          " tests/test_d117_contrast_v5_pack.py                | 345 ++++++++++++++++++++-",
          " tests/test_identity_pins.py                        |  60 ++++",
          " 7 files changed, 1324 insertions(+), 82 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "7 files changed, 1324 insertions\\(\\+\\), 82 deletions\\(-\\)"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check && git status --short --branch && git diff --name-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "configs/campaigns/d117_contrast_v5/generate_configs.py",
          "docs/contracts/identity_pin_projection.md",
          "joulewise/analysis_engine/inputs.py",
          "joulewise/identity_pins.py",
          "tests/test_analysis_inputs.py",
          "tests/test_d117_contrast_v5_pack.py",
          "tests/test_identity_pins.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_identity_pins.py$"
      }
    }
  ],
  "flags": []
}
```

## Change

- R-1 — CONFIRMED: exact scientific identity and exact-key receipt/runtime schemas remain unchanged; replacement matching was not altered ([identity_pins.py:74](/Users/edr/code/JouleWise-wt-decode-id/joulewise/identity_pins.py:74), [inputs.py:2709](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:2709)).
- R-2 — CONFIRMED: decode declarations derive their ordered manifest census from the registered block rotation, yielding `4/4/2/2/2/2/2/2`; prefill retains its legacy declaration shape ([generate_configs.py:1472](/Users/edr/code/JouleWise-wt-decode-id/configs/campaigns/d117_contrast_v5/generate_configs.py:1472)).
- R-3 — CONFIRMED: freeze and re-verification enforce common-profile equality, declared membership, exact census, unique declaration rows, and closed-set cardinality using existing refusal tokens ([identity_pins.py:1472](/Users/edr/code/JouleWise-wt-decode-id/joulewise/identity_pins.py:1472), [identity_pins.py:2381](/Users/edr/code/JouleWise-wt-decode-id/joulewise/identity_pins.py:2381)).
- R-4 — CONFIRMED: every manifest class must resolve to exactly one scientific identity, and distinct identity count must equal declared manifest count ([identity_pins.py:1626](/Users/edr/code/JouleWise-wt-decode-id/joulewise/identity_pins.py:1626)).
- R-5 — CONFIRMED: deterministic multi-identity set digest uses the ruled domain/preimage; singleton hashes remain unchanged, and all members must share runtime pins and complete stack identity ([identity_pins.py:247](/Users/edr/code/JouleWise-wt-decode-id/joulewise/identity_pins.py:247), [identity_pins.py:1765](/Users/edr/code/JouleWise-wt-decode-id/joulewise/identity_pins.py:1765)).
- R-6(a) — CONFIRMED: the frozen set was reachable through authenticated launch lineage → pack root → U8 freeze receipt → `u11-freeze-projection` → frozen identity receipt. Evidence identities must be nonempty and a subset; multi-identity evidence can use only condition-family transport ([inputs.py:3858](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:3858), [inputs.py:4055](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:4055)).
- R-6(b) — CONFIRMED: floor sites remain unchanged, and the committed v3 singleton digest is reproduced byte-for-byte ([test_identity_pins.py:407](/Users/edr/code/JouleWise-wt-decode-id/tests/test_identity_pins.py:407)).
- R-7 — NOT DONE: the supplied ruling contains no R-7 clause; no semantics were invented.
- R-8 — CONFIRMED: RED-first failure was observed at declaration equality, followed by PASS and individual unlisted-manifest, census, retyped-declaration, and drifted-tag refusal tests ([test_d117_contrast_v5_pack.py:933](/Users/edr/code/JouleWise-wt-decode-id/tests/test_d117_contrast_v5_pack.py:933)); set-digest/common-profile and analysis-path tests are also present ([test_identity_pins.py:367](/Users/edr/code/JouleWise-wt-decode-id/tests/test_identity_pins.py:367), [test_analysis_inputs.py:340](/Users/edr/code/JouleWise-wt-decode-id/tests/test_analysis_inputs.py:340)).
- Contract clauses are replicable from the vocabulary, digest construction, freeze algorithm, analysis route, receipt mapping, worked two-manifest example, and test table ([identity_pin_projection.md:53](/Users/edr/code/JouleWise-wt-decode-id/docs/contracts/identity_pin_projection.md:53), [identity_pin_projection.md:767](/Users/edr/code/JouleWise-wt-decode-id/docs/contracts/identity_pin_projection.md:767)).

## Verification notes

The generator is GAMMA-only and does not generate the ALPHA/BETA floor packs, so no floor regeneration was applicable. The first standalone temp-harness invocation omitted `PYTHONPATH` and failed before loading product code; V3 is the corrected exact rerun.