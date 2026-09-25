```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented A1; the golden regenerated identically twice at blob caa18e1535b858af393647df79bce61dd25ba3b6, and all four targeted mutants were killed.",
  "workspace": {
    "base_requested": "1b8bae45",
    "base_mode": "exact",
    "head_start": "1b8bae45e5fef586445212b4ae915626e545c0ec",
    "head_end": "1b8bae45e5fef586445212b4ae915626e545c0ec",
    "upstream_end": "1b8bae45e5fef586445212b4ae915626e545c0ec",
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
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "python3 scripts/capture_claim_replay_golden.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["wrote tests/golden/claimgate_v1_replay.json"]},
      "expected": {"exit_code": 0, "tail_regex": "wrote tests/golden/claimgate_v1_replay.json"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "git hash-object tests/golden/claimgate_v1_replay.json",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["caa18e1535b858af393647df79bce61dd25ba3b6"]},
      "expected": {"exit_code": 0, "tail_regex": "caa18e1535b858af393647df79bce61dd25ba3b6"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "python3 scripts/capture_claim_replay_golden.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["wrote tests/golden/claimgate_v1_replay.json"]},
      "expected": {"exit_code": 0, "tail_regex": "wrote tests/golden/claimgate_v1_replay.json"}
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "git hash-object tests/golden/claimgate_v1_replay.json",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["caa18e1535b858af393647df79bce61dd25ba3b6"]},
      "expected": {"exit_code": 0, "tail_regex": "caa18e1535b858af393647df79bce61dd25ba3b6"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_claim_replay_golden",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 8 tests in 45.590s", "FAILED (errors=1)", "FileNotFoundError: tests/golden/claimgate_v1_sensitivity_certificate.json"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 /private/tmp/claimgate_a1_targeted.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["KILLED 620:if_false@4 by floor_anchor_mismatch_wire", "KILLED 626:if_false@4 by binding_mismatch_wire", "KILLED 626:Or_delete_0@7 by empty_subjects_wire", "KILLED 626:Or_delete_1@7 by binding_mismatch_wire"]},
      "expected": {"exit_code": 0, "tail_regex": "KILLED 626:Or_delete_1@7"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "python3 -c 'from scripts.claimgate_golden_sweep import _validate_exceptions; _validate_exceptions(); print(\"exception proofs valid\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["exception proofs valid"]},
      "expected": {"exit_code": 0, "tail_regex": "exception proofs valid"}
    },
    {
      "id": "V8",
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
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The focused module's certificate pin test errors because the certificate file is absent; the requested full --certify sweep was not run.",
      "needs": "Magistrate runs full certification at the bench and pins the resulting certificate."
    }
  ]
}
```

## Change

Added the three A1 real-wire refusal rows and a capture guard that rejects any record differing from the ruling. Listed exactly the eight ruled post-632 paper-custody mutants, barred pre-632 issuance mutants from the exception list, and fixed a `TypeError` exposed while validating those entries. No `joulewise/` file changed; no commit was made.

For the PR body: `floor_anchor_mismatch_wire` kills `620:if_false@4`; `binding_mismatch_wire` and `empty_subjects_wire` kill `626:if_false@4`; `empty_subjects_wire` kills `626:Or_delete_0@7`; `binding_mismatch_wire` kills `626:Or_delete_1@7`.

## Verification notes

Both regenerations produced golden blob `caa18e1535b858af393647df79bce61dd25ba3b6`. The targeted comparison killed all four named mutants. The focused module passed 7 of 8 tests; its sole error is the absent sensitivity certificate.

## Residual risk

Full `--certify` and the certificate pin remain for the magistrate’s bench run.