```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "PR-0 golden and corpus are regenerated, but a confirmed pre-632 gated mutant survives the ruled oracle; certification needs a magistrate ruling.",
  "workspace": {
    "base_requested": "576f3989",
    "base_mode": "exact",
    "head_start": "576f39893804f9811f4d916de9371850dda7a29d",
    "head_end": "576f39893804f9811f4d916de9371850dda7a29d",
    "upstream_end": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "branch": "test/2026-09-25-claimgate-pr0-golden"
  },
  "pathspec": [
    "scripts/capture_claim_replay_golden.py",
    "scripts/claimgate_golden_sweep.py",
    "tests/golden/claimgate_v1_replay.json",
    "tests/golden/claimgate_v1_corpus_bases/gate_fixture.json",
    "tests/golden/claimgate_v1_corpus_bases/minimal.json",
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
      "cmd": "python3 -B scripts/capture_claim_replay_golden.py --write-corpus-bases",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["wrote tests/golden/claimgate_v1_corpus_bases"]},
      "expected": {"exit_code": 0, "tail_regex": "wrote tests/golden/claimgate_v1_corpus_bases"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B scripts/capture_claim_replay_golden.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["wrote tests/golden/claimgate_v1_replay.json"]},
      "expected": {"exit_code": 0, "tail_regex": "wrote tests/golden/claimgate_v1_replay.json"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B scripts/claimgate_golden_sweep.py --coverage",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["unlisted uncovered arcs: []"]},
      "expected": {"exit_code": 0, "tail_regex": "unlisted uncovered arcs: \\[\\]"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "time python3 -B -m unittest tests.test_claim_replay_golden -v",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 8 tests in 56.355s", "FAILED (errors=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "Isolated temporary clone: rewrite joulewise/paper_custody.py:620:if_false@4 with _mutations/_rewrite, then run the exact C(3) worker command",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["key joulewise/paper_custody.py:620:if_false@4 exit 0 stderr_tail"]},
      "expected": {"exit_code": 1, "tail_regex": "exit 1"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -B scripts/claimgate_golden_sweep.py --certify",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 130, "tail": ["KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "mutation"}
    },
    {
      "id": "V7",
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
      "text": "NEEDS_RULING: joulewise/paper_custody.py:620:if_false@4 survives the exact standing-test oracle. Line 620 precedes the v1 KeyError at line 632, so the permitted v1-wire-unreachable exception cannot apply. The mutation removes the floor-anchor mismatch check and is not semantically equivalent. Acceptance v3 forbids paper-custody rows.",
      "needs": "Magistrate consult and ruling on how PR-0 may cover this pre-632 behavior; do not affirm it as an equivalent mutant."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The aggregate certification was interrupted after the independent survivor proof. No certificate or complete gated/measured mutation table was produced; the certificate pin test therefore errors.",
      "needs": "Resume certification only under the next ruling."
    }
  ]
}
```

## Change

Implemented the v3 golden capture, 19,895 deterministic validator cases from two tracked bases, the split gated/measured certification sweep, and the revised standing tests. Only the allowed paths changed. No commit was made. The new golden blob SHA is `3a4cc5604136eedbae124f38a69d54a1faa8ebb5`.

Two regenerations in a fresh temporary clone produced identical golden and base blobs. Coverage has **zero unlisted arcs**:

| Function | Arcs | Covered | Allowlisted |
|---|---:|---:|---:|
| `evaluate_claim` | 108 | 103 | 5 |
| `_inside_equivalence`, `_interval`, `_finite` | 16 | 16 | 0 |
| `holm_adjust` | 4 | 4 | 0 |
| `_resolve_contrast_floor` | 32 | 32 | 0 |
| `evaluate_session` | 10 | 9 | 1 |

The sweep enumerates 178 gated and 989 measured mutants. Kill counts and the validator’s after-corpus kill rate are **uncertified**; its prior rate was 164/934.

## Verification notes

The focused suite finished in **56.355 seconds**. The six existing standing tests and new corpus-base test passed. `test_sensitivity_certificate_pinned` errored because no certificate was issued. The targeted exact-oracle replay returned exit 0 for `paper_custody.py:620:if_false@4`, confirming an unlisted survivor.

## Residual risk

The next spend is the ruled **consult**, not another implementation round. The magistrate must resolve the pre-632 survivor before certification and the certificate hash can be completed.