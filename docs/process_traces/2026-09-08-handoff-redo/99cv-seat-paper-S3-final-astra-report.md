```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "S3 implementation complete; approved hash-only fixture repin verified and all requested acceptance checks pass.",
  "workspace": {
    "base_requested": "main ac092ccd",
    "base_mode": "exact",
    "head_start": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "head_end": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-paper-S3"
  },
  "pathspec": [
    "joulewise/analysis_engine/claim_side_bound.py",
    "joulewise/paper_custody.py",
    "tests/test_paper_custody.py",
    "tests/test_claim_side_bound.py",
    "tests/fixtures/paper_custody/run_kills.py",
    "docs/contracts/paper_supply_custody.md",
    "docs/paper/results-fill-registry.md",
    "docs/decision_log.md",
    "docs/contracts/paper_claim_side_bound.md",
    "configs/paper_supply/supply_map.json"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py --s3",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["S3 KILL SUMMARY: 20/20 killed; scoped bytes restored."]},
      "expected": {"exit_code": 0, "tail_regex": "S3 KILL SUMMARY: 20/20 killed"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_claim_side_bound",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 22 tests in 0.047s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 29 tests in 39.795s",
          "",
          "OK",
          "KILLED 110 owner-source mutations and 5 grant-policy mutations: stale receipts refused",
          "PENDING production Git-blob role: fixture coverage is not production coverage",
          "KILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_claims",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 64 tests in 0.314s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_state",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 43 tests in 1.968s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 31 tests in 0.905s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/paper-s3-repin.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["MAP DIFF PASS: exactly 10 fixture receipt/inventory digest fields; roles, grants, production and all other fields unchanged."]
      },
      "expected": {"exit_code": 0, "tail_regex": "MAP DIFF PASS"}
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Parallel S2 changes also repin this map. These fixture hashes bind the S3 branch source census.",
      "needs": "Integrate S2/S3, then repin the combined tree once and perform lead verification."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "All requested acceptance checks passed. Earlier canonical discovery was interrupted; full discovery was not repeated for this hash-only resume.",
      "needs": "Canonical integrated-tree verification remains lead-owned."
    }
  ]
}
```

## Change

The scope blocker is resolved. Diffing [supply_map.json:47](/Users/edr/code/JouleWise-wt-paper-S3/configs/paper_supply/supply_map.json:47) against HEAD confirms **only ten digest fields changed**: `receipt.expected_sha256` and `inventory.expected_sha256` under each of:

- `roles.fixture.claim_evidence`
- `roles.fixture.d165_closeout`
- `roles.fixture.reported_energy_parents`
- `roles.fixture.transfer_projection`
- `roles.fixture.whole_window_verdict`

No role, grant, production digest, input digest, or other field was added or changed.

Implementation by synthesis item:

| Item | Result and location |
|---|---|
| 1 | Complete B and per-kind components copied by [claim_side_bound.py:135](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/analysis_engine/claim_side_bound.py:135). |
| 2 | Typed v2 wire with unit, estimator and ratio estimand at [claim_side_bound.py:116](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/analysis_engine/claim_side_bound.py:116). |
| 3 | Ordered verdict-resolution join, usable statuses and injectivity at [claim_side_bound.py:80](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/analysis_engine/claim_side_bound.py:80); manifest schema unchanged. |
| 4 | Exact numeral-byte copying and validation at [claim_side_bound.py:145](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/analysis_engine/claim_side_bound.py:145); booleans rejected, arithmetic tolerance diagnostic-only. |
| 5 | Required anchor and copied CI/decision endpoints at [claim_side_bound.py:133](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/analysis_engine/claim_side_bound.py:133). |
| 6 | Regression union and executable counterfactuals at [run_kills.py:103](/Users/edr/code/JouleWise-wt-paper-S3/tests/fixtures/paper_custody/run_kills.py:103). |
| 7 | Verdict-only gate at [paper_custody.py:590](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/paper_custody.py:590), registration at line 650, producer census at line 790; replacement fixture at [test_paper_custody.py:867](/Users/edr/code/JouleWise-wt-paper-S3/tests/test_paper_custody.py:867). |

The [new contract:8](/Users/edr/code/JouleWise-wt-paper-S3/docs/contracts/paper_claim_side_bound.md:8) defines symbols, formulas, wire, refusal codes and custody roles. [Registry notes:1121](/Users/edr/code/JouleWise-wt-paper-S3/docs/paper/results-fill-registry.md:1121) bind DS-26/28/29 while preserving `PROPOSED_STOP_FILL`; [D-178:11162](/Users/edr/code/JouleWise-wt-paper-S3/docs/decision_log.md:11162) records items 1–7. No renderer projection or commit was made.

Each counterfactual below was killed. Line numbers refer to [tests/test_claim_side_bound.py](/Users/edr/code/JouleWise-wt-paper-S3/tests/test_claim_side_bound.py:65).

| Mutation | Counterfactual without the guard | Line |
|---|---|---:|
| Anchor-only | Accept 1 instead of B=4 | 81 |
| Dropped kind | Accept incomplete components | 84 |
| Sum-for-mean | Accept 8 instead of 4 | 87 |
| Precedence flip | Accept arm-bound total 18 instead of 4 | 90 |
| Decision as CI95 | Accept D as I | 93 |
| Double widening | Accept another expansion by B | 96 |
| Edited interval/scalar | Accept coherently changed B and D | 102 |
| Shifted intervals | Accept replaced endpoint provenance | 109 |
| `1e-13` drift | Accept a numerically close substitute | 117 |
| Sign flip | Accept the wrong expansion sign | 120 |
| Weakened numeral equality | Accept different numeral bytes | 182 |
| Permuted cells | Accept reordered provenance | 124 |
| Deduplicated cells | Lose repeated resolution cells | 128 |
| Refused resolution | Admit unusable source cells | 132 |
| Missing anchor | Produce without the required kind | 143 |
| Noninjective join | Alias two contrasts to one ordered list | 147 |
| Ratio in J cell | Mislabel J/token as J | 153 |
| Boolean bound | Produce a boolean numeric field | 169 |
| Producer normalization | Erase original numeral spelling | 182 |
| Producer substitution | Emit anchor instead of total | 65 |

## Verification notes

The [resumed acceptance log](/tmp/paper-s3-resumed-acceptance.log) records every exit code. `tests.test_analysis_engine_claims` is absent; the existing `tests.test_analysis_claims` was run instead.

Earlier canonical discovery was interrupted. This hash-only resume reran the complete requested acceptance list, not full discovery. Synthetic tests establish software behavior, not live hardware validation.

## Residual risk

S2 repins the same map on its branch. After integrating S2/S3, **repin the combined tree once**, then perform lead verification. X6/X7 remain `PROPOSED_STOP_FILL`; rendering stays with the later seat.