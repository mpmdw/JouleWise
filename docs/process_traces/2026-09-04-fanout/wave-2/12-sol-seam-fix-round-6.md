```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Restored exact v1 refusal semantics for every mutated frozen four-row AP-2 metric declaration while retaining fail-closed successor registry enumeration.",
  "workspace": {
    "base_requested": "727ce86b3596ee8bfb36b77219c68b91fb81825c",
    "base_mode": "exact",
    "head_start": "727ce86b3596ee8bfb36b77219c68b91fb81825c",
    "head_end": "727ce86b3596ee8bfb36b77219c68b91fb81825c",
    "upstream_end": "727ce86b3596ee8bfb36b77219c68b91fb81825c",
    "branch": "int/2026-09-04-fan-wave-2"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/wave-2/12-sol-seam-fix-round-6.md",
    "joulewise/analysis_manifest_v2.py",
    "tests/test_analysis_manifest_v2.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_analysis_manifest_v2 tests.test_analysis_manifest_v3 tests.test_modularity",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 34 tests in 2.431s",
          "FAILED (failures=4)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 34 tests[\\s\\S]*OK$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_analysis_manifest_v2 tests.test_analysis_manifest_v3 tests.test_modularity",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 34 tests in 2.451s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 34 tests[\\s\\S]*OK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport json\nfrom pathlib import Path\nfrom joulewise import analysis_manifest as v1\nfrom joulewise import analysis_manifest_v2 as v2\nr=json.loads(Path('configs/analysis_registry/slice_2m_ap2.v1.json').read_text()); r['metrics'][0]={'metric_tag':'idle_subtracted_request','name':'idle_subtracted_energy_j','window_class':'request','unit':'J','ratio_estimand':None}; a=v1.validate_analysis_registry(r); b=v2.validate_analysis_registry(r); print(f'frozen_four_mutation v1={\"refuse\" if a else \"accept\"} v2={\"refuse\" if b else \"accept\"} same_errors={a == b}'); raise SystemExit(0 if a and b and a == b else 1)\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "frozen_four_mutation v1=refuse v2=refuse same_errors=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "v1=refuse v2=refuse same_errors=True$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "current=$(shasum -a 256 joulewise/analysis_manifest.py | awk '{print $1}'); base=$(git show 727ce86b:joulewise/analysis_manifest.py | shasum -a 256 | awk '{print $1}'); test \"$current\" = \"$base\"; printf 'analysis_manifest_sha256=%s byte_identical=yes\\n' \"$current\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "analysis_manifest_sha256=5b4ba3ff4962bb9941c64a7f7acad98e6128119c5b4b93ad686e104a746e8cc9 byte_identical=yes"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "analysis_manifest_sha256=5b4ba3ff.*byte_identical=yes$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Only the three preflight-authorized test modules ran; no repository-wide or live/quiet-machine gate ran.",
      "needs": "The magistrate owns broader final verification."
    }
  ]
}
```

## Change

The v2 seam now recognizes an exactly four-row metric declaration as the
frozen AP-2 shape. It retains every v1 metric error for that shape and bypasses
successor registry authentication, so an authenticated replacement cannot
launder a mutation of any frozen row. Larger successor enumerations still pass
only through the authenticated detection-floor registry, and generalized
condition-pair validation is unchanged.

The regression executes the auditor's row-zero replacement and authenticated
replacements at each other frozen index. Each must reproduce v1's nonempty
error list exactly. The v1 module was not edited.

## Verification notes

V1 is the required red run: all four frozen-row subtests failed before the
implementation change because v2 returned no errors. V2 is the green replay;
V3 isolates the auditor's exact mutation; V4 confirms v1 byte identity. No
tests outside the preflight allowlist ran.

## Residual risk

Broader final-suite verification remains magistrate-owned.
