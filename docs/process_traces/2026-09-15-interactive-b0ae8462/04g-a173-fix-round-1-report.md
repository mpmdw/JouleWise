```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented R1–R5 within scope; both modules pass and every required mutant fails, then restores GREEN.",
  "workspace": {
    "base_requested": "e09dd964a0c0336f9a34482e209d1d0d37b77a79",
    "base_mode": "exact",
    "head_start": "e09dd964a0c0336f9a34482e209d1d0d37b77a79",
    "head_end": "e09dd964a0c0336f9a34482e209d1d0d37b77a79",
    "upstream_end": "e09dd964a0c0336f9a34482e209d1d0d37b77a79",
    "branch": "feat/2026-09-15-arm-census-idle"
  },
  "pathspec": [
    "joulewise/arm_census.py",
    "tests/test_arm_census.py",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_arm_census",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 19 tests in 0.036s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 19 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 104 tests in 19.769s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 104 tests[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-fix1-mutations/fix1_mutations.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R1_own_root RED exit=1: FAILED (failures=2)",
          "R1_own_root GREEN exit=0: OK",
          "R3_timeout RED exit=1: FAILED (failures=1)",
          "R3_timeout GREEN exit=0: OK",
          "R4_unreadable RED exit=1: FAILED (failures=1)",
          "R4_unreadable GREEN exit=0: OK",
          "R4_t3_root RED exit=1: FAILED (failures=2)",
          "R4_t3_root GREEN exit=0: OK",
          "R4_exit_two RED exit=1: FAILED (failures=1)",
          "R4_exit_two GREEN exit=0: OK",
          "R5_injection RED exit=1: FAILED (failures=1)",
          "R5_injection GREEN exit=0: OK",
          "R5_parser_only RED exit=1: FAILED (failures=1)",
          "R5_parser_only GREEN exit=0: OK",
          "R3_timeout_catch RED exit=1: FAILED (errors=1)",
          "R3_timeout_catch GREEN exit=0: OK",
          "ALL 8 MUTANTS RED; ALL 8 RESTORED MODULES GREEN"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ALL 8 MUTANTS RED; ALL 8 RESTORED MODULES GREEN"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -B scripts/bridge scope-check --baseline .codex-bridge/baselines/mag-a173-fix1-20260915.json --expect-digest sha256:6ca51593ada1ed618a2cb8ce50bd2cf43562fde3b8bb3b8672b86015ab1a245e --lease-id lease-6d9a4a71a10f4d98b01494dc4bfbb092 --scope joulewise/arm_census.py tests/test_arm_census.py docs/phase_2/derivation_night_runbook.md docs/process/NIGHT_HANDBACK.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "\"verdict\":\"SCOPE_OK\""}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Change

- `joulewise/arm_census.py:24,188,202,219,223,280`: own-root idle exemption; numeric discovery; 30-second timeout; counted diagnostics; actual discovery argv in output.
- `tests/test_arm_census.py:105,194,218,235,248,262,272,297,309,348`: required regression cells and updated discovery fixtures.
- `docs/phase_2/derivation_night_runbook.md:643,647,665,674,1617,2675`: interpreter, ownership and exit-1 corrections.
- `docs/process/NIGHT_HANDBACK.md:51`: matching own-root rule.

No commits. Next step: lead review of the scoped diff.

## Verification notes

Mutation probes ran exclusively in the `cp -R` scratch copy; each GREEN reran all 19 arm-census tests. The additional timeout-handler mutant failed with the expected uncaught `TimeoutExpired`.

Single modules only, as instructed. Night production paths and Git index remain unchanged; scratch source is restored.

## Residual risk

Process evidence is fixture-based. Node/T3 remains PROVISIONAL; live verification remains lead-owned.