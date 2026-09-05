```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: R5-F2 is cured, but R5-F1 recurs because v2 accepts a mutation of the frozen four-row AP-2 metric declaration that v1 refuses.",
  "workspace": {
    "base_requested": "8daa1a12997b6121269877f4feb7023722d6abc9",
    "base_mode": "exact",
    "head_start": "8daa1a12997b6121269877f4feb7023722d6abc9",
    "head_end": "8daa1a12997b6121269877f4feb7023722d6abc9",
    "upstream_end": "8daa1a12997b6121269877f4feb7023722d6abc9",
    "branch": "int/2026-09-04-fan-wave-2"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/wave-2/11-refuter-round-5-delta.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "prior": {"R5-F1":"OPEN_SAME_SIGNATURE","R5-F2":"CURED"},
    "same_signature": "YES — the generalized fallback again admits changed declarations under the frozen AP-2 v1 identity; this is the MOD-R2-004/R5-F1 trusted-mutation signature, now on a metric row.",
    "findings": [
      {
        "id": "R5D-F1",
        "severity": "blocker",
        "location": "joulewise/analysis_manifest_v2.py:172-184; tests/test_analysis_manifest_v2.py:40-48",
        "text": "The v2 fallback discards every v1 metric-identity error before registry validation. Replacing one of the frozen four AP-2 metrics with a different authenticated detection-floor metric therefore returns [] in v2 while v1 refuses the same four-row registry. The positive-only equivalence test does not kill this mutation.",
        "cure": "Retain v1 identity/order semantics whenever the declaration is the frozen four-row AP-2 shape; admit generalized metric enumeration only through an unambiguous successor shape/identity, and add the executed frozen-row mutation as a regression."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "current=$(sha256sum joulewise/analysis_manifest.py | awk '{print $1}'); upstream=$(git show origin/main:joulewise/analysis_manifest.py | sha256sum | awk '{print $1}'); test \"$current\" = \"$upstream\"; printf 'analysis_manifest_sha256=%s byte_identical=yes\\n' \"$current\"",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["analysis_manifest_sha256=5b4ba3ff4962bb9941c64a7f7acad98e6128119c5b4b93ad686e104a746e8cc9 byte_identical=yes"]},
      "expected": {"exit_code":0,"tail_regex":"analysis_manifest_sha256=5b4ba3ff.*byte_identical=yes"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_modularity tests.test_analysis_manifest_v3 tests.test_analysis_manifest_v2 tests.test_docs_freshness",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 64 tests in 3.548s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"Ran 64 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport io, unittest\nimport tests.test_modularity as tm\nfrom joulewise import analysis_manifest as v1\nfrom joulewise import analysis_manifest_v2 as v2\nnames=['tests.test_modularity.ClosedSetRegistryTests.test_analysis_condition_pairs_are_validated_as_registry_declarations','tests.test_modularity.ClosedSetRegistryTests.test_frozen_ap2_row_requires_all_pairs_from_its_four_profiles']\ndef run(fn):\n tm.validate_analysis_registry=fn; r=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.TestLoader().loadTestsFromNames(names)); return len(r.failures),len(r.errors),r.testsRun\na,b=run(v1.validate_analysis_registry),run(v2.validate_analysis_registry); assert a==(2,0,2) and b==(0,0,2); print(f'repointed_tests v1_failures={a[0]} v2_failures={b[0]} tests={b[2]}')\nPY",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["repointed_tests v1_failures=2 v2_failures=0 tests=2"]},
      "expected": {"exit_code":0,"tail_regex":"v1_failures=2 v2_failures=0 tests=2"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport json\nfrom pathlib import Path\nfrom joulewise import analysis_manifest as v1\nfrom joulewise import analysis_manifest_v2 as v2\nr=json.loads(Path('configs/analysis_registry/slice_2m_ap2.v1.json').read_text()); r['metrics'][0]={'metric_tag':'idle_subtracted_request','name':'idle_subtracted_energy_j','window_class':'request','unit':'J','ratio_estimand':None}; a=v1.validate_analysis_registry(r); b=v2.validate_analysis_registry(r); print(f'frozen_four_mutation v1={\"refuse\" if a else \"accept\"} v2={\"refuse\" if b else \"accept\"}'); raise SystemExit(0 if a and b else 1)\nPY",
      "cwd": ".",
      "observed": {"result":"fail","exit_code":1,"tail":["frozen_four_mutation v1=refuse v2=accept"]},
      "expected": {"exit_code":0,"tail_regex":"frozen_four_mutation v1=refuse v2=refuse"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -n -F 'retired from routine agent processes; the retained drift file is reference-only' PROJECT_STATUS.md; rg -n -F 'Retired public-site reference:' PROJECT_STATUS.md",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["136:| Public status site | retired from routine agent processes; the retained drift file is reference-only for Ed's optional manual dispatch | `docs/site/DRIFT.md` |","193:- Retired public-site reference: `docs/site/DRIFT.md`. Ed alone chooses whether"]},
      "expected": {"exit_code":0,"tail_regex":"193:- Retired public-site reference"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Only the four preflight-authorized test modules ran; no repository-wide or live/quiet-machine gate ran.",
      "needs": "Magistrate owns broader final verification after R5D-F1 is cured."
    }
  ]
}
```

## Findings

R5D-F1 — blocker. `analysis_manifest_v2.validate_analysis_registry` treats any v1 metric-identity refusal as permission to enter its generalized path. A four-row registry with the unchanged frozen `slice_2m_ap2_v1` identity can therefore replace `gross_energy_j` with authenticated `idle_subtracted_energy_j`: v1 refuses; v2 accepts. This is a same-signature recurrence of the trusted-mutation defect behind MOD-R2-004/R5-F1, not a new defect class. R5-F2 is cured: both `PROJECT_STATUS.md` sentences match D-136's retired/reference-only/manual-dispatch posture.

## Residual risk

The permitted 64-test batch is green and the two re-pointed tests demonstrably fail on v1/pass on v2, but neither positive result covers the frozen-row mutation. Broader suite and live gates remain lead-owned.
