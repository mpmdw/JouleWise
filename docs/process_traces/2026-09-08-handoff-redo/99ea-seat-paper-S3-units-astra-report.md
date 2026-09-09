```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the B8 unit vocabulary; requested acceptance and all 21 mutations pass; full discovery was interrupted.",
  "workspace": {
    "base_requested": "9760ee53",
    "base_mode": "exact",
    "head_start": "9760ee535c646a61dcef1792dc747ed7fa1072e4",
    "head_end": "9760ee535c646a61dcef1792dc747ed7fa1072e4",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-paper-S3"
  },
  "pathspec": [
    "joulewise/analysis_engine/ratio.py",
    "joulewise/analysis_engine/claim_side_bound.py",
    "tests/test_claim_side_bound.py",
    "tests/test_analysis_ratio.py",
    "tests/fixtures/paper_custody/run_kills.py",
    "docs/contracts/paper_claim_side_bound.md",
    "docs/paper/results-fill-registry.md",
    "joulewise/paper_custody.py",
    "tests/test_paper_custody.py",
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
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_claim_side_bound tests.test_analysis_ratio tests.test_paper_custody tests.test_paper_comparison_placements tests.test_docs_freshness > /tmp/paper-s3-unit-acceptance.log 2>&1; rc=$?; tail -12 /tmp/paper-s3-unit-acceptance.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 107 tests in 64.475s",
          "OK",
          "KILLED 113 owner-source mutations and 5 grant-policy mutations: stale receipts refused",
          "PENDING production Git-blob role: fixture coverage is not production coverage",
          "KILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B tests/fixtures/paper_custody/run_kills.py --s3 > /tmp/paper-s3-unit-kills.log 2>&1; rc=$?; tail -24 /tmp/paper-s3-unit-kills.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "S3-units_membership: KILLED",
          "S3 KILL SUMMARY: 21/21 killed; 21 mutations over 10 distinct guards (including producer sites); scoped bytes restored."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "21/21 killed; 21 mutations over 10 distinct guards"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -B /tmp/paper-s3-unit-audit.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS: 10 digest-only changes; all 10 changed paths in scope; manifest/artifact unchanged; HEAD unchanged."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS: 10 digest-only changes;"}
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check > /tmp/paper-s3-unit-diff-check.log 2>&1; rc=$?; cat /tmp/paper-s3-unit-diff-check.log; exit $rc",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests > /tmp/paper-s3-unit-full-suite.log 2>&1; rc=$?; tail -25 /tmp/paper-s3-unit-full-suite.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Full discovery was intentionally interrupted after inspection showed it includes long calibration crash-matrix jobs. The explicitly requested acceptance group passed.",
      "needs": "Lead retains canonical-suite completion and final integration verification."
    }
  ]
}
```

## Change

Implemented all four requested items without committing.

| Item | Implementation and verification | Counterfactual |
|---|---|---|
| 1. Shared authority | `ratio.py:34` defines constants; `ratio.py:290` validates pairings. `test_analysis_ratio.py:11,28` cover exact units and B8 mappings. Follow-up registered at `paper_claim_side_bound.md:197`. | Changing either constant, admitting J with a mapping, or bypassing exact B8 validation fails the regressions. |
| 2. S3 and documentation | `claim_side_bound.py:123` calls the shared validator. Contract `:51` and registry `:1141` name B8 vocabulary. `test_claim_side_bound.py:188` preserves J-cell refusal coverage. | Restoring AP-SPEC acceptance fails the vocabulary regression; allowing J relabeling fails the J-cell regression. Documentation corrections were inspected. |
| 3. Both APIs and mutation | `test_claim_side_bound.py:155` exercises both forms with matching source/candidate fields. `run_kills.py:136` removes membership alone. | Membership removal produced **16 assertion failures** across both APIs. Result: **21 mutations over 10 distinct guards**. |
| 4. Census and repin | `paper_custody.py:793` registers the shared validator; `test_paper_custody.py:948` pins it. Supply-map changes comprise ten digest fields only. | Omitting the census member fails its assertion; changing any non-digest field fails the structural audit. |

## Verification notes

Full discovery was interrupted, so no canonical-suite pass is claimed. Manifest and verdict acceptance remain unchanged. `UNIT-VOCAB-SHARED-01` records their deferred integration.

Next step: lead diff review and final integration verification.