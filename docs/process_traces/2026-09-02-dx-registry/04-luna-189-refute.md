```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "R7F replay passes, but three fail-open contract paths and one signed-rendering defect remain.",
  "workspace": {
    "base_requested": "a63d45bd",
    "base_mode": "descendant",
    "head_start": "a63d45bd",
    "head_end": "2a6d3841ed6426c53d90820601f8622636f1fd3b",
    "upstream_end": "a63d45bd",
    "branch": "feat/2026-09-02-dx-registry"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "verdict": "NOT CLEAN",
    "findings": [
      {
        "id": "R7F-REFUSAL-BUCKET-001",
        "severity": "blocker",
        "lens": "EXECUTION",
        "file": "scripts/check_paper_round7_artifacts.py",
        "line": "399-413",
        "summary": "DX-021 checks only the anchor_unresolved list length; an extra refusal-token bucket is ignored and the fence still passes.",
        "replacement_text": "In the DX-021 renderer, require the refusal-token map to contain exactly anchor_unresolved, require its list length to equal the exact refused integer, and require derived + refused == population_size:\nsummary = artifacts['AQ'].get('summary')\nbuckets = summary.get('v3_refusals_by_token') if isinstance(summary, dict) else None\nif not isinstance(buckets, dict) or set(buckets) != {'anchor_unresolved'}:\n    raise ValueError('v3 refusal tokens are not exclusively anchor_unresolved')\nderived_i = _exact_int(derived)\nrefused_i = _exact_int(refused)\npopulation_i = _exact_int(summary['population_size'])\nif derived_i + refused_i != population_i:\n    raise ValueError('v3 derived/refused counts do not partition population_size')\nrefusal_ids = buckets['anchor_unresolved']\nif not isinstance(refusal_ids, list) or len(refusal_ids) != refused_i:\n    raise ValueError('anchor_unresolved list does not match v3_refused_count')"
      },
      {
        "id": "R7F-EXACT-INTEGER-001",
        "severity": "blocker",
        "lens": "EXECUTION",
        "file": "scripts/check_paper_round7_artifacts.py",
        "line": "388-418",
        "summary": "Exact-integer rows use int(), silently truncating malformed numeric artifact fields; a reissued AQ with population_size 15.9 passes as 15.",
        "replacement_text": "Add before render_row and use for every integer/count value:\ndef _exact_int(value: Any) -> int:\n    if isinstance(value, bool) or not isinstance(value, int):\n        raise ValueError(f'not an exact integer: {value!r}')\n    return value\nReplace every int(values[i]) and int(refused/count) in the integer, count, flip, control, and derived_refused_counts branches with _exact_int(values[i])."
      },
      {
        "id": "R7F-F4-COMMAND-001",
        "severity": "blocker",
        "lens": "CONTRACT",
        "file": "scripts/check_paper_round7_artifacts.py",
        "line": "222-230",
        "summary": "DX-003's full F4 replay command is unstructured prose; removing --svg from the registry row still returns R7F 181/0.",
        "replacement_text": "Add an exact DX-003 command assertion in parse_registry_text after row_id is parsed:\nexpected_f4_command = 'python3 scripts/paper_excursion_decomposition.py --corpus-root /Users/edr/code/JouleWise --out docs/paper/round7/excursion-decomposition.json --svg docs/paper/figures/fig4_edge_excursions.svg'\nif row_id == 'DX-003' and f'full replay is `{expected_f4_command}`.' not in supplier:\n    raise RegistryError('DX-003 must carry the exact full F4 replay command including --svg')"
      },
      {
        "id": "DX-027-SIGNED-001",
        "severity": "should_fix",
        "lens": "CONTRACT",
        "file": "docs/paper/results-fill-registry.md",
        "line": "778",
        "summary": "DX-027 is the signed median_pct statistic but renders without the explicit positive sign used by DX-024.",
        "replacement_text": "| DX-027 — successor-draft median relative delta | +0.61 % | `AQ#summary.delta_v3_vs_stored_relative.median_pct`, parent DX-002; the issued artifact names this field `median_pct` (not `median_abs_pct`); render an explicit sign and two decimals followed by ` %`; `R7F_RENDER=signed_2_percent` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |\nAlso add the renderer branch: `if rule == 'signed_2_percent' and len(values) == 1: return f'{_signed(values[0], 2)} %'`."
      }
    ],
    "mutations": [
      {
        "id": "M1",
        "what": "Changed DX-014 from 2.5 ms to 2.6 ms in a scratch registry copy.",
        "result": "FAIL rc=2; MISMATCH row DX-014; R7F 181/1."
      },
      {
        "id": "M2",
        "what": "Changed DX-011 from −5.5 ms to +5.5 ms in a scratch registry copy.",
        "result": "FAIL rc=2; MISMATCH row DX-011; R7F 181/1."
      },
      {
        "id": "M3",
        "what": "Changed one F4 SVG mark coordinate in a scratch copy.",
        "result": "FAIL rc=2; MISMATCH digest F4 and figure onset marks."
      },
      {
        "id": "M4",
        "what": "Changed AQ population_size to 15.9 and updated its registry digest/size.",
        "result": "UNEXPECTED PASS rc=0; R7F 181/0."
      },
      {
        "id": "M5",
        "what": "Added an extra AQ v3 refusal-token bucket and updated its registry digest/size.",
        "result": "UNEXPECTED PASS rc=0; R7F 181/0."
      },
      {
        "id": "M6",
        "what": "Removed --svg from DX-003's documented full replay command.",
        "result": "UNEXPECTED PASS rc=0; R7F 181/0."
      }
    ],
    "tests": "test_paper_round7_artifacts: OK (17); test_paper_replay_fence: OK (8, skipped=1); test_docs_freshness: OK (6); combined: Ran 32 tests / OK (skipped=1)"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_round7_artifacts tests.test_paper_replay_fence tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK \\(skipped=1\\)$"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_paper_round7_artifacts.py --literals-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R7F COMPARED 181 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^R7F COMPARED 181 / MISMATCHES 0$"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_paper_round7_artifacts.py --corpus-root /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp189/r7f-missing.m22CMg",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 3,
        "tail": [
          "EXIT=3"
        ]
      },
      "expected": {
        "exit_code": 3,
        "tail_regex": "^EXIT=3$"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_paper_round7_artifacts.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R7F COMPARED 184 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^R7F COMPARED 184 / MISMATCHES 0$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 -c \"import json,sys; from pathlib import Path; sys.path.insert(0,'scripts'); import shard_tests; m=shard_tests.discover_test_modules(); p=json.loads(Path('scripts/test_timings.json').read_text()); assert 'tests.test_paper_round7_artifacts' in m; print('CI_DISCOVERY',len(m),'R7_INCLUDED',True,'R7_WEIGHT',p['unknown_module_weight_seconds'])\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CI_DISCOVERY 179 R7_INCLUDED True R7_WEIGHT 29.834"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^CI_DISCOVERY 179 R7_INCLUDED True R7_WEIGHT 29\\.834$"
      }
    }
  ],
  "flags": [
    {
      "id": "BASELINE-DRIFT-001",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The point-in-time registry-v5 verifier exits at its stale old_keys assertion when run at this later HEAD. Independent comparison shows the DG row keys are unchanged and the pending DG/DS/PG census remains 37.",
      "needs": ""
    }
  ]
}
```

## Findings

The 16 numeric rows independently recompute exactly from XD/AQ. DX-027 is truthfully sourced from signed `median_pct`; neither the skeleton nor checklist describes it as a magnitude. The defect is only the missing explicit `+`.

R7F correctly inspects all 118 marks, rejects the three required mutations, returns exit 3 for absent corpus, and passes retained replay at 184/0. CI runtime discovery includes the new module.

The historical v5 verifier is stale by design: its own docstring says it is point-in-time, and it fails before the DG mutation assertion when run against this later HEAD (`docs/process_traces/2026-08-31-registry-v5/01-verify-registry-v5.py:2-5,78-81`). Independent DG comparison found 128 unchanged DG rows and 37 pending-family rows.

## Residual risk

The legacy replay-fence module had one expected corpus skip; direct R7F replay against the retained corpus passed.