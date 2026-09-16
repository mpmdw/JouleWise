```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FINDINGS: R1's new regression supplies an ancestor PID that Darwin pgrep excludes; idle own-root helpers still block a stub.",
  "workspace": {
    "base_requested": "c3eedd8d0d41568f8be589edca97d8cc12cf0cb4",
    "base_mode": "exact",
    "head_start": "c3eedd8d0d41568f8be589edca97d8cc12cf0cb4",
    "head_end": "c3eedd8d0d41568f8be589edca97d8cc12cf0cb4",
    "upstream_end": "c3eedd8d0d41568f8be589edca97d8cc12cf0cb4",
    "branch": "feat/2026-09-15-arm-census-idle"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FINDINGS",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "R1 regression passes with an ancestor hit that Darwin discovery excludes",
        "locations": [
          "tests/test_arm_census.py:206",
          "joulewise/arm_census.py:189",
          "joulewise/arm_census.py:201",
          "joulewise/arm_census.py:258"
        ],
        "detail": "Darwin pgrep excludes its ancestors unless -a is supplied. Both discovery argv forms omit -a. The new regression includes own claude -p ancestor PID 20 in discovery hits, enabling roots.update(hits & own). With the same tree but realistic helper-only hits (50,60), observation/classification returns own=(20,30,90), sessions=(), workloads=(), foreign=(50,60), publication_blocked=True. The new exemption never reaches the headless own root.",
        "recommendation": "Identify the own activation from exact ancestry independently of discovery membership in both observation and classification. Add a helper-only discovery regression, retaining workload blocking and sibling-seat rejection."
      }
    ],
    "same_signature": "YES: the prior Astra R1 false refusal for idle MCP helpers under the caller's headless root recurs when discovery correctly omits ancestors. The newly added regression hides that unresolved case. No recurrence found for R2-R5.",
    "specific_checks": {
      "a": "Constructed own-root unittest workload blocks the stub and is identified as workload PID 71. The realistic ancestor-omission case exposes F1.",
      "b": "Constructed sibling codex exec outside the own subtree remains foreign and blocks the stub.",
      "c": "Local Darwin pgrep(1) documents -f as full-argument matching and -l as output formatting only. Same regex and remaining flags imply the same population, including ancestor exclusion. Both attempted live probes returned exit 3 because sysmond was unavailable.",
      "d": "Sole exit-3 return remains guarded by publication_blocked, which requires REHEARSAL_STUB. Constructed main() cases for both real classes returned 0 with workload and foreign observations.",
      "e": "joulewise/night_gate.py and scripts/run_night.py are unchanged across the delta."
    },
    "docs": "Both pinned-interpreter commands and both exit-1 explanations checked. Five generated-region checks pass; changed arm-census prose is hand-authored.",
    "evidence_directory": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy/audit_logs",
    "mutation_tails": [
      "R1-own-idle: RED exit=1 FAILED (failures=2); restored GREEN exit=0 OK",
      "R1-runbook: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R1-handback: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R2-command-first: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R2-command-final: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R2-exit-one-prose: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R2-exit-one-table: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R3-timeout: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R3-timeout-handler: RED exit=1 FAILED (errors=1); restored GREEN exit=0 OK",
      "R4-unreadable-oracle: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R4-t3-oracle: RED exit=1 FAILED (failures=2); restored GREEN exit=0 OK",
      "R4-exit2-oracle: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R5-pid-only: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R5-parser: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R5-counted: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK",
      "R5-report: RED exit=1 FAILED (failures=1); restored GREEN exit=0 OK"
    ],
    "coverage_reversions": "Individually removing each R4 coverage addition lets its forbidden mutant pass the complete arm module. Restoring coverage kills unreadable-hit, widened-T3 and exit-2 mutants with 1, 2 and 1 assertion failures respectively. Restoring implementation returns GREEN."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/audit_tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B review_mutations.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["MUTATIONS 16/16 RED; ALL RESTORED GREEN"]},
      "expected": {"exit_code": 0, "tail_regex": "MUTATIONS 16/16 RED; ALL RESTORED GREEN"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/audit_tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B review_coverage.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["COVERAGE REVERSIONS 3/3 DISCRIMINATE; ALL RESTORED GREEN"]},
      "expected": {"exit_code": 0, "tail_regex": "COVERAGE REVERSIONS 3/3 DISCRIMINATE; ALL RESTORED GREEN"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/audit_tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v review_delta",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["ANCESTOR_EXCLUDED own=(20, 30, 90) sessions=() workloads=() foreign=(50, 60) blocked=True", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/audit_tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_arm_census",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 19 tests in 0.036s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/audit_tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 59 tests in 0.573s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/audit_tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["joulewise.night_gate.PackNightRefusal: rehearsal_roots_not_disjoint: measurement_root", "Ran 104 tests in 19.882s", "FAILED (errors=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/../audit_tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night.PackNightProducerTests.test_rehearsal_plan_and_arm_context_roots_follow_sibling_child_rule",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy/driver_bench",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.212s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/audit_tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_gen_derivation_night",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: no census-clean temporary directory available", "Ran 40 tests in 0.905s", "FAILED (failures=35)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/audit_tmp\" PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_gen_derivation_night.GeneratedRegionTests",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 5 tests in 0.629s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "python3 -B review_integrity.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-delta-astra-copy",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["BASELINE_DIGEST_MATCH; HEAD_UNCHANGED; INDEX_UNCHANGED; WORKTREE_CLEAN", "ALL FOUR DELTA PATHS RESTORED BYTE-FOR-BYTE", "NIGHT_GATE_AND_RUN_NIGHT_UNCHANGED"]},
      "expected": {"exit_code": 0, "tail_regex": "NIGHT_GATE_AND_RUN_NIGHT_UNCHANGED"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Both live pgrep probes returned exit 3: sysmon request failed; sysmond service not found. No bypass attempted; process-shape conclusions use constructed observations and the installed Darwin manual.",
      "needs": "Lead-owned live confirmation if required."
    },
    {
      "id": "E2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Auxiliary generator tests reject scratch paths containing claude; five renderer checks pass. Driver module had 103 passes and one scratch-containment error; that unchanged test passes from a nested copy with sibling scratch fixtures.",
      "needs": ""
    }
  ]
}
```

## Findings

**F1 — blocker:** The new regression at [test_arm_census.py:206](/Users/edr/code/JouleWise-wt-a173/tests/test_arm_census.py:206) supplies the caller’s headless ancestor as a discovery hit. Darwin `pgrep` excludes ancestors by default. Removing that impossible hit reproduces the previous false refusal: idle helpers become foreign despite no workloads.

Next step: correct own-root selection independently of discovery membership, then re-audit the helper-only discovery fixture.

## Residual risk

Live process population comparison remains unverified because sysmond was unavailable. T3 remains PROVISIONAL. No hardware collection or real `launchctl` ran.