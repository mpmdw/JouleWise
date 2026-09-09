```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Resolved all merge markers and preserved S2/S3/S7 rulings; acceptance is blocked by an out-of-scope Round-7 registry parser defect.",
  "workspace": {
    "base_requested": "af8956ea",
    "base_mode": "exact",
    "head_start": "af8956ea55ca107ddda338c4ed1d0d0494e67648",
    "head_end": "af8956ea55ca107ddda338c4ed1d0d0494e67648",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "int/2026-09-08-paper-s2-s3-s7"
  },
  "pathspec": [
    "configs/paper_supply/supply_map.json",
    "docs/contracts/paper_comparison_placements.md",
    "docs/contracts/paper_supply_custody.md",
    "docs/paper/results-fill-registry.md",
    "tests/test_paper_comparison_placements.py",
    "docs/decision_log.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "cd /tmp/paper-s2-s3-s7-qidqh369/checkout && env PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_reported_energy tests.test_paper_custody tests.test_paper_rendering tests.test_claim_side_bound tests.test_analysis_ratio tests.test_paper_comparison_placements tests.test_paper_comparison_contract tests.test_paper_successor_migration tests.test_paper_round7_artifacts tests.test_d165_rationale_census tests.test_d117_floor_qwen25_1p5b_plan tests.test_gen_state tests.test_docs_freshness > /tmp/paper-integration-acceptance.log 2>&1\npaper_rc=$?\nprintf '\\nACCEPTANCE_RC=%s\\n' \"$paper_rc\" >> /tmp/paper-integration-acceptance.log\ntail -55 /tmp/paper-integration-acceptance.log\nexit \"$paper_rc\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=1, errors=12)",
          "ACCEPTANCE_RC=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ACCEPTANCE_RC=0"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "cd /tmp/paper-s2-s3-s7-qidqh369/kills && env PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 tests/fixtures/paper_custody/run_kills.py --s3 > /tmp/paper-integration-s3-kills.log 2>&1\npaper_rc=$?\nprintf '\\nS3_KILLS_RC=%s\\n' \"$paper_rc\" >> /tmp/paper-integration-s3-kills.log\ncat /tmp/paper-integration-s3-kills.log\nexit \"$paper_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "S3 KILL SUMMARY: 21/21 killed; 21 mutations over 10 distinct guards (including producer sites); scoped bytes restored.",
          "S3_KILLS_RC=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "S3_KILLS_RC=0"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/paper-integration-inspect.py > /tmp/paper-integration-inspection.log 2>&1\npaper_rc=$?\ncat /tmp/paper-integration-inspection.log\nexit \"$paper_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "STATE_PINS_UNCHANGED: EXPECTED_IDS and count 150 match kernel",
          "SUPPLY_PASS: five fixture roles; two digest-free pending production roles",
          "SCOPE_PASS: six allowlisted files changed, no unowned dirty paths, HEAD unchanged"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SCOPE_PASS:"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check > /tmp/paper-integration-diff-check.log 2>&1\npaper_rc=$?\nprintf 'DIFF_CHECK_RC=%s\\n' \"$paper_rc\" >> /tmp/paper-integration-diff-check.log\ncat /tmp/paper-integration-diff-check.log\nexit \"$paper_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["DIFF_CHECK_RC=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DIFF_CHECK_RC=0"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "grep -rn '^<<<<<<<\\|^=======$\\|^>>>>>>>' . > /tmp/paper-integration-markers.log 2>&1\npaper_rc=$?\nif [ \"$paper_rc\" -eq 1 ] && [ ! -s /tmp/paper-integration-markers.log ]; then\n  printf 'MARKER_SCAN_EMPTY\\n'\n  exit 0\nfi\ncat /tmp/paper-integration-markers.log\nexit 1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["MARKER_SCAN_EMPTY"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MARKER_SCAN_EMPTY"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Scope expansion is required, but no out-of-scope workspace edits were made. The Round-7 parser mistakes X5 proposal rows for historical retirement records and rejects the required RETIRED_FALLBACK wording.",
      "needs": "Authorize the two requested paths, repair proposal-versus-retirement parsing with regression coverage, then rerun named acceptance."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Acceptance and mutation tests ran in separate temporary checkouts to contain transient out-of-scope writes. Both checkouts matched every tracked workspace file after execution.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "scripts/check_paper_round7_artifacts.py",
      "tests/test_paper_round7_artifacts.py"
    ],
    "reason": "_retired_sites scans every table row containing RETIRED_FALLBACK, including the required X5 comparison proposals, then demands historical retirement metadata.",
    "blocked_work": "Complete Round-7 acceptance and obtain a green named-module replay.",
    "minimal_change": "Distinguish comparison proposal rows from historical retirement records while preserving strict historical validation; add a regression covering the merged X5 rows."
  }
}
```

## Change

- **Supply map — ten digest hunks:** recomputed receipt and inventory hashes for each of the five fixture families against the merged census. Preserved both S2 pending production roles and S3’s claim-evidence registration; added no production digests.
- **Placements contract — nested hunks:** retained S2’s X5 five-field census and retirement, S3’s X6/X7 v2 verdict-resolution join, and S7’s D-177 requirement in every X5 Missing-evidence cell. Preserved the adjacency block and X13–X16 omissions.
- **Custody mirror — nested hunks:** applied the same combination; retained S3’s census/gate documentation.
- **Registry — nested hunks:** applied the same combination. All 66 rows agree across shared columns and row order; custody retains its existing schema without the Location column.
- **Placement tests — one hunk:** retained both lane tests, updated S1’s closed-vocabulary pin to the merged X5 wording, and added combined-disposition and row-order checks.
- **Decision log:** ordered D-176–D-179 numerically in body and index without changing decision content. Each already existed exactly once; no deduplication was needed. `tests/test_gen_state.py` remains unchanged: `EXPECTED_IDS` and count **150** match the kernel.

No commit was made.

## Verification notes

The named suite ran **248 tests**, with **1 failure and 12 errors**, all in Round-7 tests. The root error is:

`RegistryError: X5 must carry exactly one dated retirement note`

The parser needs the scope expansion above; changing the required X5 wording would violate the merge rulings. The standalone placement checks passed, and all **21 S3 mutations** were killed.

Next step: the lead authorizes the two parser/regression paths and resumes this task. Logs: [acceptance](/tmp/paper-integration-acceptance.log), [S3 kills](/tmp/paper-integration-s3-kills.log), [scope and snapshot inspection](/tmp/paper-integration-inspection.log).