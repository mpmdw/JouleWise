```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Inventory enforcement and ratchets implemented; R7F acceptance and commits are blocked.",
  "workspace": {
    "base_requested": "9eab16f8",
    "base_mode": "descendant",
    "head_start": "05fca1af59720c4d6cee1652c9501e37c740caec",
    "head_end": "05fca1af59720c4d6cee1652c9501e37c740caec",
    "upstream_end": "05fca1af59720c4d6cee1652c9501e37c740caec",
    "branch": "feat/2026-09-28-paper-number-inventory"
  },
  "pathspec": [
    "scripts/check_paper_number_inventory.py",
    "tests/test_paper_number_inventory.py",
    "docs/paper/number-inventory.json",
    "scripts/gen_paper_number_inventory.py",
    "docs/paper/draft-v2-skeleton.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_paper_number_inventory > /private/tmp/paperinv-tests-final.txt 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 7.091s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 31 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_paper_number_inventory tests.test_paper_terms_lint tests.test_paper_first_use_ledger tests.test_paper_replay_fence tests.test_paper_successor_migration tests.test_paper_round7_artifacts tests.test_select_outcome_branches tests.test_d165_rationale_census > /private/tmp/paperinv-all-skeleton-tests.txt 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 162 tests in 26.872s", "FAILED (failures=6, skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_paper_round7_artifacts > /private/tmp/paperinv-r7f-tests.txt 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 69 tests in 8.196s", "FAILED (failures=6)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B scripts/gen_paper_number_inventory.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PAPER-NUMBER-INVENTORY GENERATOR: PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "GENERATOR: PASS"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 -B scripts/check_paper_number_inventory.py --check > /private/tmp/paperinv-check-final.txt",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["CHECK PASS: 0 finding(s)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CHECK PASS: 0 finding\\(s\\)"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -B /private/tmp/paperinv-proof.py > /private/tmp/paperinv-proof.txt 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R7F DX regions: 1",
          "R7F original: prose mismatches=4",
          "R7F scratch-mutation: prose mismatches=3"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F DX regions: 1"
      }
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "python3 -B scripts/check_paper_round7_artifacts.py --literals-only > /private/tmp/paperinv-r7f-cli-original.txt 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["R7F PLACED 0/4", "R7F LITERALS-ONLY COMPARED 420 / MISMATCHES 8"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MISMATCHES 0"
      }
    },
    {
      "id": "V8",
      "kind": "smoke",
      "cmd": "python3 -B scripts/check_paper_round7_artifacts.py --literals-only --skeleton /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/joulewise-paperinv-proof-c8os_4bk/offset-count.md > /private/tmp/paperinv-r7f-cli-mutant.txt 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": ["R7F PLACED 0/4", "R7F LITERALS-ONLY COMPARED 419 / MISMATCHES 7"]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "MISMATCHES [1-9]"
      }
    },
    {
      "id": "V9",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V10",
      "kind": "other",
      "cmd": "git add -- scripts/check_paper_number_inventory.py tests/test_paper_number_inventory.py docs/paper/number-inventory.json scripts/gen_paper_number_inventory.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": [
          "fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-paperinv-opus0928/index.lock': Operation not permitted"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: restoring the quote activates R7F's mandatory marker checks and breaks six R7F tests. No out-of-scope files were modified.",
      "needs": "Grant checker/test scope after ruling on the R7F integration route."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: quote-only restoration conflicts with R7F's requirement for DX markers. Options are authorizing additional skeleton marker/wording edits with updated tests, or adapting R7F to validate the adopted inventory bindings. Recommend the inventory route.",
      "needs": "Choose the route; passing R7F acceptance and independent mutation evidence remain blocked."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "blocking",
      "text": "Git staging was denied by the filesystem sandbox. No commits were created; all five changes remain unstaged. Nothing was pushed.",
      "needs": "Resume in an environment with authorized write access to the worktree Git metadata."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The R7F scratch mutation exits non-zero, but the original already fails; this is not independent evidence that R7F catches that numeric mutation.",
      "needs": "Repeat the mutation after the original R7F check passes."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "scripts/check_paper_round7_artifacts.py",
      "tests/test_paper_round7_artifacts.py"
    ],
    "reason": "The existing R7F marker contract and zero-region test assumptions conflict with the requested quote restoration.",
    "blocked_work": "Passing R7F tests and proving a DX numeric mutation fails from a passing baseline.",
    "minimal_change": "After a lead ruling, validate marker-free DX values through the inventory bindings and update R7F placement/count assertions."
  }
}
```

## Change

Implemented `--check`, fixed 155/853 ratchet ceilings, a self-contained deterministic generator, and anchor-based tests. The skeleton change adds only the requested curly quote.

Scratch mutations of the offset count, both onset-median sites, and spelled count each produce exactly one inventory `MISMATCH` and exit 1.

## Verification notes

All six affected-module failures are in R7F. The combined sweep preceded the final added anchor-CLI test; the final inventory module passed separately. Canonical discovery was not run for this tooling-only change.

R7F now finds the DX region but rejects its missing markers. Resolving that conflict requires the scope expansion and ruling above.

No commits exist because Git staging was sandbox-denied. The next step is a lead ruling, scoped R7F repair, renewed acceptance checks, then commits with the requested prefix in a Git-writable environment.