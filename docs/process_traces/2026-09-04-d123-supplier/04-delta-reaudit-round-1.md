```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Fix round 1 remains NOT LANDABLE: the unauthenticated projection-producer seam and outer-gate-masked mutation test repeat their original signatures and require consult.",
  "workspace": {
    "base_requested": "8f4c38ea",
    "base_mode": "exact",
    "head_start": "8f4c38eade7296615c3791a0d098018289884d10",
    "head_end": "8f4c38eade7296615c3791a0d098018289884d10",
    "upstream_end": "8f4c38eade7296615c3791a0d098018289884d10",
    "branch": "feat/2026-09-04-d123-reported-mean"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-d123-supplier/04-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "same_signature": "YES: execution B1/contract F1 and execution S2 repeat the same defect signatures; this is decisive and routes both to consult before another fix round.",
    "reaudit": [
      {"id": "execution-B1", "result": "NOT CURED", "evidence": "V1 executes two accepted source/issuance/render paths whose alpha and beta numeric projections are independently fixture-authored over the same production-shaped extraction-report bytes."},
      {"id": "execution-B2", "result": "CURED", "evidence": "V1 mutates one of 50 allowed denominator sources to server_usage; ratio-of-sums still issues and records both sources."},
      {"id": "execution-B3", "result": "CURED", "evidence": "V1 injects a second alpha artifact in both orders; alpha alone STOP_FILLs and beta remains stable."},
      {"id": "execution-S1", "result": "CURED", "evidence": "V1 removes all four custody hashes from one member; the refused member carries nulls and no zero digest."},
      {"id": "execution-S2", "result": "NOT CURED", "evidence": "V1 now reseals more than 500 mutations, but every source-derived issuer check asserts only generic StopFill after whole-artifact inequality; no field-specific named relation is asserted."},
      {"id": "contract-F1", "result": "NOT CURED", "evidence": "Same executed evidence as execution-B1; validate_d117_mint_consumption_report authenticates an unrelated report while build_reported_phase_energy_source copies the caller-supplied projection."},
      {"id": "contract-F2", "result": "CURED", "evidence": "V1 reseals a t95 artifact and a matching caller manifest; current alpha placements still STOP_FILL and the issuer raises issuance_composition_rule_not_current."},
      {"id": "contract-F3", "result": "CURED", "evidence": "V1 checks all 20 exact-token rows for the artifact schema, default rule, refusal language, and VALUE_UNISSUED; inspected rows bind the correct role and field."},
      {"id": "contract-F4", "result": "CURED", "evidence": "Same executed mixed-source counterfactual as execution-B2."},
      {"id": "contract-F5", "result": "CURED", "evidence": "V1 reseals changed member energy and dependent arithmetic; the old expected issuance digest leaves all alpha tokens STOP_FILL."},
      {"id": "contract-F6", "result": "CURED", "evidence": "Same executed both-order duplicate counterfactual as execution-B3."},
      {"id": "contract-F7", "result": "CURED", "evidence": "Same executed missing-custody counterfactual as execution-S1."}
    ],
    "findings": [
      {
        "id": "R1-B1",
        "severity": "blocker",
        "file": "joulewise/reported_phase_energy.py:332",
        "text": "The new source producer validates a real extraction report but does not produce or authenticate the numeric reported-energy projection; it copies that caller-authored wrapper into a self-addressed source.",
        "counterfactual": "The green V1 fixture uses the identical production-shaped extraction report for alpha and beta while independently inventing 102.55 J and 402.55 J decode means; both sources, issuances, and paper values are accepted.",
        "cure_shape": "Derive the projection from authenticated producer bytes and validate every projected member value/digest against them; add a production-shaped end-to-end negative in which altered projection data is refused. Route to consult because this repeats B1/F1."
      },
      {
        "id": "R1-S2",
        "severity": "should_fix",
        "file": "tests/test_reported_phase_energy.py:729",
        "text": "The expanded mutation loop remains outer-gate masked: source/artifact inequality can satisfy every generic assertRaises even if inner digest and arithmetic relations are not checked.",
        "counterfactual": "For each resealed mutant, build_reported_phase_energy_issuance compares the entire artifact with its rebuilt source artifact before validation, while the test asserts only StopFill and never the expected named relation/refusal.",
        "cure_shape": "Partition mutations by contract relation, call the validator that owns that relation with required parent bytes, and assert its exact reason; retain a separate issuance-binding mutation. Route to consult because this repeats S2."
      }
    ],
    "new_defects": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_reported_phase_energy",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 51.166s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test in .*s[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_floor_qwen3_v5_generate tests.test_floor_extraction",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 181 tests in 11.894s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 181 tests in .*s[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 2.710s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 13 tests in .*s[\\s\\S]*OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["source_path.write_bytes(_source_bytes(sources[0]))", "result = subprocess.run("]},
      "expected": {"exit_code": 0, "tail_regex": "result = subprocess.run\\("}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Two original defect signatures repeated after fix round 1; the prompt's repeat rule is triggered.",
      "needs": "Route R1-B1 and R1-S2 to the required consult before fix round 2."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical whole suite was excluded by the preflight rule and was not run.",
      "needs": "Lead may run broader verification after the consult-driven cure."
    }
  ]
}
```

## Findings

### R1-B1 — blocker — NOT CURED

The new CLI calls the established report validator, but its numeric `reported_energy_projection` is already present in caller-authored source material. The producer checks only its self-hash, role, parent report digest, and three-cell census before copying it. V1 therefore proves the old production-path defect survives: one unrelated real-shaped report licenses two independently fabricated role projections and rendered values.

### R1-S2 — should_fix — NOT CURED

The mutation census and resealing improved, but the asserted oracle is still an outer envelope: artifact inequality at `reported_phase_energy.py:1294` precedes inner validation, and the test accepts any `StopFill`. That is the same masking signature as the original stale-address test, not field-specific evidence.

## Residual risk

Fixture evidence only; no live or quiet-machine measurement was attempted. The mandated preflight excluded the canonical suite.
