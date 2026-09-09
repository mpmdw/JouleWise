```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "S3 implementation and 20 mutation kills completed; custody acceptance needs an out-of-scope fixture digest repin.",
  "workspace": {
    "base_requested": "main ac092ccd",
    "base_mode": "exact",
    "head_start": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "head_end": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "upstream_end": "0a29b07564b595b9f9d8189e869de3e5939c2a18",
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
    "docs/contracts/paper_claim_side_bound.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
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
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 22 tests in 0.126s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=19)", "PENDING production Git-blob role: fixture coverage is not production coverage", "KILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_claims",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 64 tests in 0.322s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_state",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 43 tests in 3.338s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 31 tests in 0.926s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 130, "tail": ["KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: source-census changes invalidate fixture receipt and inventory digest pins in configs/paper_supply/supply_map.json. All 19 custody failures stop at stale receipt assertions. The unlisted map was preserved; no scope violation occurred.",
      "needs": "Authorize a hash-only repin of the map, or have the lead apply it, then rerun custody acceptance."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical discovery was interrupted during retained-evidence reads for the scope handoff. It did not complete and preceded the final numeric-domain hardening. Final targeted checks were rerun.",
      "needs": "Run the canonical suite after repinning and integration."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced by 10 commits while this checkout remained at the exact requested base. No commit or rebase was performed.",
      "needs": "Lead integrates with concurrent S2 work."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["configs/paper_supply/supply_map.json"],
    "reason": "Required source-census changes stale the five synthetic families' receipt and inventory digest pins.",
    "blocked_work": "Passing tests.test_paper_custody and completing integrated acceptance.",
    "minimal_change": "Recompute only receipt.expected_sha256 and inventory.expected_sha256 for the five fixture roles; preserve roles, modes, inputs and production dispositions."
  }
}
```

## Change

Implemented synthesis items 1–7 within scope:

| Item | Implementation |
|---|---|
| 1. Copy B and every component | [claim_side_bound.py:135](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/analysis_engine/claim_side_bound.py:135), copy-only producer at line 145. |
| 2. Typed v2 wire | Unit/estimand checks at [claim_side_bound.py:116](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/analysis_engine/claim_side_bound.py:116); closed schema documented in [paper_claim_side_bound.md:38](/Users/edr/code/JouleWise-wt-paper-S3/docs/contracts/paper_claim_side_bound.md:38). |
| 3. Verdict-resolution join | Ordered concatenation, usable statuses and injectivity at [claim_side_bound.py:80](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/analysis_engine/claim_side_bound.py:80). No manifest change. |
| 4. Exact numeral equality | Raw-byte producer/validator at [claim_side_bound.py:145](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/analysis_engine/claim_side_bound.py:145). `isclose` remains diagnostic-only. |
| 5. Endpoint provenance and anchor | Required anchor and copied intervals at [claim_side_bound.py:133](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/analysis_engine/claim_side_bound.py:133). |
| 6. Mutation union | [test_claim_side_bound.py:65](/Users/edr/code/JouleWise-wt-paper-S3/tests/test_claim_side_bound.py:65), [run_kills.py:103](/Users/edr/code/JouleWise-wt-paper-S3/tests/fixtures/paper_custody/run_kills.py:103); counterfactuals below. |
| 7. Gate, fixture and documentation | Verdict-only reevaluation at [paper_custody.py:590](/Users/edr/code/JouleWise-wt-paper-S3/joulewise/paper_custody.py:590), registration at line 650, census at line 790; replacement fixture at [test_paper_custody.py:867](/Users/edr/code/JouleWise-wt-paper-S3/tests/test_paper_custody.py:867). [Registry notes:1121](/Users/edr/code/JouleWise-wt-paper-S3/docs/paper/results-fill-registry.md:1121) preserve the display stop; [D-178:11162](/Users/edr/code/JouleWise-wt-paper-S3/docs/decision_log.md:11162) records the ruling. |

All 20 counterfactual kills passed. Test lines below refer to `tests/test_claim_side_bound.py`.

| Mutation | Counterfactual without the guard | Line |
|---|---|---:|
| Anchor-only substitution | Accept 1 instead of B=4 | 81 |
| Dropped kind | Accept incomplete components | 84 |
| Sum-for-mean | Accept 8 instead of 4 | 87 |
| Precedence flip | Accept arm-bound total 18 instead of 4 | 90 |
| Decision fed as CI95 | Accept D as I | 93 |
| Double widening | Accept another expansion by B | 96 |
| Edited interval/scalar | Accept coherently changed B and D | 102 |
| Coherently shifted intervals | Accept replaced endpoint provenance | 109 |
| `1e-13` drift | Accept a numerically close substitute | 117 |
| Sign flip | Accept the wrong expansion sign | 120 |
| Numeral equality weakened | Accept different numeral bytes | 182 |
| Permuted cells | Accept reordered provenance | 124 |
| Deduplicated cells | Lose repeated resolution cells | 128 |
| Refused resolution | Admit unusable source cells | 132 |
| Missing anchor | Produce without the required kind | 143 |
| Noninjective join | Alias two contrasts to one ordered list | 147 |
| Ratio in J cell | Mislabel J/token as J | 153 |
| Boolean bound | Produce a boolean numeric field | 169 |
| Producer normalization | Erase original numeral spelling | 182 |
| Producer anchor substitution | Emit anchor instead of total | 65 |

## Verification notes

**NEEDS_SCOPE:** authorize the hash-only update to `configs/paper_supply/supply_map.json`, then rerun custody acceptance and the canonical suite. Existing receipt assertions were preserved.

Exit-code records are in the [acceptance log](/tmp/paper-s3-acceptance.log); individual kill evidence is in [paper-s3-kills.json](/tmp/paper-s3-kills.json). `tests.test_analysis_engine_claims` does not exist; the existing `tests.test_analysis_claims` passed.

The isolated gate regression mocks upstream custody boundaries and does not replace full custody verification. Canonical discovery was interrupted; its [log](/tmp/paper-s3-canonical.log) ends with `KeyboardInterrupt`.

## Residual risk

Final integration and custody verification remain lead-owned. X6/X7 remain `PROPOSED_STOP_FILL`; no renderer, display projection, live measurement, or commit was made.