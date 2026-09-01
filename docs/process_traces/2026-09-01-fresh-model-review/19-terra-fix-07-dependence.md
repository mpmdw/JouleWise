```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "All nine dependence-sensitivity findings are cured within the authorized three files.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "head_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "upstream_end": null,
    "branch": "feat/2026-09-01-dependence"
  },
  "pathspec": [
    "docs/paper/round7/dependence-sensitivity.md",
    "scripts/dependence_sensitivity.py",
    "tests/test_dependence_sensitivity.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_dependence_sensitivity",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "............",
          "----------------------------------------------------------------------",
          "Ran 12 tests in 1.518s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 12 tests in [0-9.]+s\\n\\nOK"
      }
    }
  ],
  "flags": []
}
```

## Change

| Finding | Cure | File:line | Regression test |
|---|---|---|---|
| F1 | Fully composed repeat, stochastic-metrology, and deterministic intervals; gates inspect both composed intervals; p-values use total SE. | [script](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:192), [document](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:25) | `test_worked_example...`, `test_registered...`, `test_zero_rho...` |
| F2 | Alpha is fixed at 0.05; no alpha option exists. | [script](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:34) | `test_fixed_alpha...` |
| F3 | Exactly ten deltas required; no arbitrary-size mode. | [script](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:78) | `test_analyze_guards...`, `test_cli_refuses...` |
| F4 | Replaced invalid consumers with four dedicated sensitivity placements and authentication/omit rules. | [document](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:99), [script](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:333) | `test_document_retains...`, `test_artifact_hashes...` |
| F5 | Holm equality is explicitly inclusive. | [document](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:51) | `test_document_retains...` |
| F6 | Renamed the halving scenario and added the rho counterexamples. | [document](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:49) | `test_document_retains...`, `test_ar1_multiplier...` |
| F7 | Uses the H30 replacement verbatim. | [document](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:63) | `test_document_retains...` |
| F8 | Definitions precede the table and first uses are glossed. | [document](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:9) | `test_document_retains...` |
| F9 | Added golden arithmetic, engine-endpoint parity, refusal subprocesses, critical-value parity, strict boundaries, hashes, and output-key checks. | [tests](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:61) | Full targeted module: 12 passing tests |