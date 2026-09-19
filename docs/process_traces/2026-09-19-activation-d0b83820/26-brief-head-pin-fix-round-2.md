SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/test_arm_readiness_registry.py", "tests/test_d117_decode_contrast_plan.py", "tests/test_d117_floor_qwen25_1p5b_plan.py", "tests/test_d117_floor_qwen25_7b_plan.py", "tests/test_d117_v3_family.py"]

# Head-pin test repair, fix round 2 — the remaining regenerate-mode tests that run a campaign generator against the live checkout

Cwd is the linked worktree of branch `fix/2026-09-19-head-pin-test-drift` at `d3c8b3559a3c635e43de46e98918e0e468201919` (`git log -1`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; scratch under `/tmp` only; no `sudo`, no `powermetrics`. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python` (read-only use). Do not commit. Do not end your turn before the report is complete.

## Why

The committed ledger head pin `configs/calibration/calibration_ledger_head.json` advanced 76 → 176 (legitimately; D-109's append protocol). Twelve campaign generators byte-pin that file (`LEDGER_HEAD_FILE_SHA256` = `6bbe2625…`, the `a816036f` bytes) and refuse regeneration with `pinned input drifted` / `external input drift`. Round 1 (already on this branch; read `git log -3 -p -- tests/test_campaign_generator_core.py tests/test_d117_floor_qwen3_v5_generate.py`) fixed two modules with a fixture: the generation-time head bytes (`GENERATION_LEDGER_HEAD_BYTES` / `_SHA256` in `tests/test_campaign_generator_core.py`) installed in a disposable `git clone --shared` of the checkout, with the working tree's generator files copied over the clone's, and generators run from that clone. The full replay (record: `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/14-full-replay-d74b1be5.log.gz`) shows five more modules failing on exactly this signature; the lead re-ran them at this head and they still fail:

| Module | Failing tests | Signature |
|---|---|---|
| `tests/test_arm_readiness_registry.py:445` | `test_generators_check_both_without_and_with_committed_freeze_receipts` | generator subprocess rc 1, `pinned input drifted` |
| `tests/test_d117_decode_contrast_plan.py` | `test_dual_generation_transaction_and_generational_induction`, `test_emitted_successor_generator_refuses_downgrade_targets`, `test_emitted_successor_pack_bytes_carry_no_freeze_variant_wording` | same |
| `tests/test_d117_floor_qwen25_1p5b_plan.py` | `test_successor_generation_threads_plan_identity_and_lineage` | same |
| `tests/test_d117_floor_qwen25_7b_plan.py` | `test_target_status_inventory_and_invalid_modes_are_fail_closed`, `test_generation_refuses_symlinked_write_inventory_before_any_write` (×4 subcases), `test_successor_generation_threads_plan_identity_and_lineage` | `external input drift for …calibration_ledger_head.json: 6b2d37c8… != 6bbe2625…` (the check fires BEFORE the refusal the test expects) |
| `tests/test_d117_v3_family.py` | `test_check_still_refuses_missing_generator_owned_output`, `test_unedited_v2_generators_emit_v3_successors` | both spellings |

## Do

Apply the round-1 pattern to each: run the generator (in-process or subprocess) from a disposable repository that carries the historical head bytes and the WORKING TREE's generator files (import the two constants from `tests.test_campaign_generator_core`; do not duplicate the bytes). Where a test's purpose is a DIFFERENT refusal (symlinked write inventory, downgrade targets, missing generator-owned output, invalid modes), the fixture must let the generator get past the head-pin check so the intended refusal is what fires — assert the intended message, and add nothing that would pass if the head-pin refusal fired instead. Keep every existing assertion. Do NOT touch production code, any generator, `configs/calibration/*`, frozen packs, or the two round-1 modules. If a test cannot be fixtured without changing what it proves, finish the others and return NEEDS_RULING naming it.

## Bench acceptance (execute; paste tails)

- Each of the five modules individually: OK (some take minutes).
- Negative oracle on a `/tmp` copy: with the fixture bytes deliberately wrong, each fixtured test must FAIL on the head-pin refusal (proves the fixture is load-bearing).
- `git diff --stat`: only the five scoped files; `git status` shows no other change.
- Name the false-failure surface on the NEXT pin advance for each module (must be none).

## Report

`claude-codex-report/v1` envelope for `--genre implementation`; JSON header under 8000 bytes; commands with outcomes; per-module what the test proved before and proves now.
