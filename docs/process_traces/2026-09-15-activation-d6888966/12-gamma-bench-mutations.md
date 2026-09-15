# 12 — Lead bench: GAMMA root-key fix, mutation kills and module runs (07:22 PDT, clock-read)

Worktree `/Users/edr/code/JouleWise-wt-gamma-keys`, branch `fix/2026-09-15-gamma-root-keys` at `678d9bcc`
(committed before any mutation). Run by the magistrate, not a seat. The contract-lens refuter (record 11) could
not run these in its read-only sandbox (its `/tmp` writes are denied); its source review found no defect.

## Modules at the bench (real `pgrep`; the G4 census test passes here)
```
TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_contrast_v5_pack   → OK (45)
TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_arm_readiness_evidence_t0 → OK
```

## Mutation A — generator reverted to the legacy keys (line 2697 → `{"claim_leaf": …, "bound_leaf": …}`)
```
ERROR: test_generated_gamma_roots_pass_and_legacy_keys_are_refused (tests.test_arm_readiness_evidence_t0…)
joulewise.arm_readiness_evidence_t0.T0EvidenceAuthoringError: arm roots do not derive from frozen leaves
FAIL: test_generated_plan_tree_uses_canonical_root_leaf_keys (tests.test_d117_contrast_v5_pack…)
AssertionError: {'claim_leaf': 'runs_d117_contrast_qwen3-1p7b_vs_[76 chars]und'} != {'claim_root_leaf': 'runs_d117_contrast_qwen3-1p7[86 chars]und'}
Ran 2 tests in 0.913s
FAILED (failures=1, errors=1)
```
Both regressions fail, each on the defect's own signature. Restored with `git checkout --`.

## Mutation B — the T-0 regression's positive call fed `legacy_roots` instead of the generated `tree["roots"]` (line 947)
```
ERROR: test_generated_gamma_roots_pass_and_legacy_keys_are_refused (…)
joulewise.arm_readiness_evidence_t0.T0EvidenceAuthoringError: arm roots do not derive from frozen leaves
Ran 1 test in 0.464s
FAILED (errors=1)
```
The positive path exercises the real `_root_observation` refusal branch (line 1020), not a copy. Restored.

## After restore
`git status --short` empty; the two regressions: `OK`.

The first attempt at Mutation A (07:19) mis-loaded the test ids (a `unittest.loader._FailedTest`, identical before and
after restore) and proved nothing; it is superseded by the runs above, which used `-k canonical_root_leaf_keys -k
legacy_keys_are_refused` over the two modules.
