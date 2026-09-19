# Record 17 — magistrate diff gate (gate-ledger rows 7/8), branch `fix/2026-09-19-head-pin-test-drift` at `ff788ef7` (lead, 2026-09-19 08:4x PDT)

## What the magistrate read, in full

`git diff 2f79e633 ff788ef7` — five test files, +194/−18, production untouched (`git diff --stat` verified by both refuters and by the lead):

1. `tests/test_calibration_bracketing.py` — the test renamed to `…_artifact_and_head_pin_ordering_and_schema` with a docstring saying the loader enforces digest-in-chain; `cutoff == pin` replaced by schema equality, `cutoff.sequence <= pin.sequence`, a 64-hex regex on the pin digest, and digest equality only at equal sequences; the `76` / `08456d50…` literals moved onto the r6 artifact's `ledger_cutoff` read from its own path. Every artifact byte-pin, identity, derivation and eligibility assertion retained.
2. `tests/test_campaign_generator_core.py` — module constants `GENERATION_LEDGER_HEAD_BYTES` (the exact `a816036f` bytes) and their digest `6bbe2625…`; inside `assert_generation_uses_shared_write_boundary`, for ALPHA/BETA only, `sha256_file` on the loaded generator module is patched by a wrapper that returns the fixture digest for `REPO_ROOT / LEDGER_HEAD_REL` and delegates every other path to the real function; the fixture digest is self-checked against the bytes on every use; the comment names lane GENERATOR-HEAD-FILE-BYTE-PIN-01. GAMMA and the write-boundary observer untouched.
3. `tests/test_calibration_ledger.py` — helpers `_commit_fixture_pin`, `_committed_extended_chain`, `_committed_snapshot_at` and three regressions through the PRODUCTION loader with `require_committed_pin=True, verify_custody=True`: advanced pin authenticates; wrong non-genesis cutoff digest → `calibration_ledger_baseline_missing`; committed pin below the cutoff → refuses with both codes on the full chain, and with `baseline_missing` ALONE after a consistent physical rollback (the D-109 R1.4 branch no test executed before).
4. `tests/test_arm_readiness_evidence_packauth.py` — the drift test installs and commits the historical head bytes inside its disposable clone only; the negative oracle now requires `pinned input drifted: <acceptance path>`.
5. `tests/test_d117_floor_qwen3_v5_generate.py` — `load_generator(pack_id, *, repository=ROOT)`; `generation_repository()` makes a `git clone --shared` of the checkout under the test's temporary directory and writes the historical head bytes there; the determinism/`--check` subprocess runs the generator from that clone.

## Design-level questions answered

1. **Does any test now claim more than it proves?** No. The bracketing test's name and docstring name the weaker property (ordering + schema from committed bytes). The ledger regressions prove the full relation on synthetic chains through the production loader. The generator fixtures test the live generators as functions of their declared inputs and say so.
2. **Is any soundness fence weakened?** No (refuter 12c table C4 lists the surviving test for each fence: drift refusal on regenerate, preserve = echo, D-109 anti-rollback, physical rollback, §0.4 head-equals-pin). The pin stays 176; no generator, frozen pack, contract or production file changed.
3. **False-failure surface on the next pin advance?** None: refuter 12x committed a synthetic pin at 999 with a fresh digest and all five modules passed.
4. **Row 8 prune.** The fixture bytes/digest constants live in `test_campaign_generator_core` and are imported by two other test modules — acceptable (one home). The `git clone --shared` fixture is heavier than an in-process patch but is the only way the subprocess path sees the historical input (consult 07 F3); it stays. Nothing dead; no comment lies.

## Bench verification (lead, this session)

Quick tier at `ff788ef7` in the fix worktree: `QUICK SUMMARY tier=quick modules=153 excluded=85 failures=0 seconds=81.547 result=PASS` (the seat's and the execution refuter's single quick-tier failure was the sandbox's blocked `/bin/ps` in `tests.test_axi_controller_events`, environmental; it does not reproduce at the bench).

## Verdict

MERGE-READY subject to: Opus counter-review (record 15) on `ff788ef7`, the full sharded replay at the bench, hosted CI on the PR head (this branch is the fix-forward for the red quick tier on main since `22b92ec7`), and the terminal review. Lane B1 (GENERATOR-HEAD-FILE-BYTE-PIN-01) is registered as queue data for the cold gate; it is NOT part of this PR.
