```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "PR-0 replay golden and sweep are implemented, but the ruled mutation gate fails with 840 unlisted survivors.",
  "workspace": {
    "base_requested": "7929a7ec",
    "base_mode": "exact",
    "head_start": "7929a7ec25da416b61147b9858f806d9663bdcdf",
    "head_end": "7929a7ec25da416b61147b9858f806d9663bdcdf",
    "upstream_end": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "branch": "test/2026-09-25-claimgate-pr0-golden"
  },
  "pathspec": [
    "scripts/capture_claim_replay_golden.py",
    "scripts/claimgate_golden_sweep.py",
    "tests/golden/claimgate_v1_replay.json",
    "tests/test_claim_replay_golden.py"
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
      "cmd": "python3 -B scripts/claimgate_golden_sweep.py --coverage",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["unlisted uncovered arcs: []"]},
      "expected": {"exit_code": 0, "tail_regex": "unlisted uncovered arcs: \\[\\]"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B scripts/claimgate_golden_sweep.py --mutate",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["mutants=1112 killed=271 listed-equivalent=1 unlisted-survivors=840"]},
      "expected": {"exit_code": 0, "tail_regex": "unlisted-survivors=0"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_claim_replay_golden -v",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 8 tests in 623.108s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -B scripts/capture_claim_replay_golden.py >/dev/null && git hash-object tests/golden/claimgate_v1_replay.json && python3 -B scripts/capture_claim_replay_golden.py >/dev/null && git hash-object tests/golden/claimgate_v1_replay.json",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["82450aa5499fb25967714835cb0d0aaecb92d372", "82450aa5499fb25967714835cb0d0aaecb92d372"]},
      "expected": {"exit_code": 0, "tail_regex": "82450aa5499fb25967714835cb0d0aaecb92d372\\n82450aa5499fb25967714835cb0d0aaecb92d372"}
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
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the one implementation round leaves 840 unlisted mutation survivors. Examples: joulewise/analysis_engine/artifact.py:1008:if_false@12 and joulewise/analysis_engine/claims.py:370:LtE_to_Lt@16:0. No acceptance criterion or exception list was weakened.",
      "needs": "Magistrate redesign consult and a new ruling before another implementation round."
    }
  ]
}
```

## Change

The golden now has the ruled v2 invariant and transition layout. The capture constructs the production claim gate context directly, records the unmocked side-bound outcome, and pins the invalid verdict wire. The new sweep measures the seven named functions and runs AST mutants in temporary clones. Only the four authorized paths changed; `joulewise/` was untouched, and no commit was made. The new golden Git blob SHA is `82450aa5499fb25967714835cb0d0aaecb92d372`.

## Verification notes

| Function | Arcs | Covered | Uncovered | Allowlisted |
|---|---:|---:|---:|---:|
| `claims.evaluate_claim` | 108 | 103 | 5 | 5 |
| `claims._inside_equivalence` | 2 | 2 | 0 | 0 |
| `claims._interval` | 8 | 8 | 0 | 0 |
| `claims._finite` | 6 | 6 | 0 | 0 |
| `multiplicity.holm_adjust` | 4 | 4 | 0 | 0 |
| `analysis_engine._resolve_contrast_floor` | 32 | 32 | 0 | 0 |
| `epoch_equivalence_check.evaluate_session` | 10 | 9 | 1 | 1 |

| Mutants | Killed | Listed equivalent | Unlisted survivors |
|---:|---:|---:|---:|
| 1,112 | 271 | 1 | **840** |

Two regenerations were byte-identical. The focused suite passed seven tests and failed only `test_golden_mutation_sweep_zero_unlisted_survivors`. The ruled zero-survivor gate remains open.

## Residual risk

**NEEDS_RULING:** The surviving validator and boundary mutations require a redesign decision under the ruling’s one-round limit. The next exact step is the magistrate’s redesign consult; this branch is not ready for acceptance.