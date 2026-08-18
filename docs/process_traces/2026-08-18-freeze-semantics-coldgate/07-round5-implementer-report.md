# Round-5 implementer report (Opus 5, 2026-08-18) — verbatim

Round 5 complete on `impl/successor-generator-repairs` — commit `0cb9bf2`, clean tree. **Delta-5 B2 is NOT implemented: I hit the exact circularity the brief told me to stop on, and I have executed evidence.**

## NEEDS_RULING — the specified transition makes the pack permanently unarmable

**The constraint chain (all mechanically resolved in this worktree):**

1. `joulewise/arm_readiness.py:3481` — the freeze receipt embeds `_pack_identity(root, tree)`.
2. `joulewise/arm_readiness.py:2252-2266` — `_pack_identity` pins `plan_sha256` = SHA-256 of **`calibration_plan.json` bytes**.
3. `calibration_plan.json`'s `draft_status` **is** one of the enumerated transition sites (gamma `generate_configs.py:741`, whose own in-source comment reads *"The D-134 freeze receipt pins calibration_plan.json by SHA."*). It also embeds `prefill_prompt_candidate.json`'s SHA, itself a status site — so ≥2 of the enumerated sites move the pinned plan bytes.
4. `joulewise/arm_readiness.py:3225` — `_load_freeze_reference` refuses unconditionally when `receipt["pack_identity"] != _pack_identity(pack_root, tree)`. Its callers are `generate_dry_run_receipt` (3723), `generate_arm_receipt` (4026), `_derive_arm_semantics_for_verification` (4203) — i.e. the `dry-run`, `arm`, and `verify` CLI gates.
5. The generator can only see FROZEN after the receipt is **committed** (`plan_arm_readiness_attachment:1912-1955` skips receipts absent from HEAD), so the receipt is always minted over draft plan bytes. There is no re-mint: `generate_freeze_receipt` hardwires `number = 1`, `supersedes: None`, and its idempotent branch returns before re-deriving `pack_identity`.

**Executed proof** (`scratchpad/probe_freeze_pin.py`, log at `scratchpad/freeze-pin-circularity.log`): gamma v2 emitted, committed, genuine receipt minted via the round-4 fixture runtime, committed; then a **full coherent frozen-status regeneration** (non-preserve, all sites, all dependent hashes and the plan-tree sidecar re-derived, receipt pin retained), committed:

```
pinned plan sha  : a5a24e22…  on-disk plan sha : a5a24e22…  match: True
full frozen regeneration exit 0
frozen-status sites now serialized: 95
full coherent transition (committed): REFUSED code='readiness_freeze_receipt_mismatch'
    message=freeze receipt pack identity differs from committed pack bytes
re-mint attempt exit 1  →  "mutated": false   (receipt cannot be re-pinned)
```

Intermediate partial states refuse earlier and just as hard (`readiness_pack_digest_mismatch`: *"frozen plan differs from committed bytes"*, then *"plan.actual_sha256 differs…"*, then *"plan.declared_sha256 differs…"*). No in-scope change can satisfy this; a resolution requires `joulewise/arm_readiness.py` (superseding-receipt support, or removing `plan_sha256` from the freeze pin, or reordering the freeze transaction), which is outside my six files and design-bearing.

**Mode question, answered from the code anyway:** the governed transaction could only ever invoke **preserve mode**. After a v2 receipt lands, the emitted generator's default `PRESERVE_CURRENT_FROZEN_BYTES` computes False (the receipt SHA ≠ the pinned 2026-08-13 constant), and the `GenerationIdentity` guard then fail-closes plain regeneration — observed: `generation failed: the current frozen identity requires preserve mode`. So a transition would have to be a preserve-mode *pending-transition* detection keyed on authenticated state vs. serialized bytes (D-2-safe: the flag would still not be the trigger). I did not build it.

**Note for the ruling:** M-2's upheld core (`docs/decision_log.md:9155-9157`) — *"receipts govern over descriptive bytes; frozen bytes are never repaired"* — plus the v1 carve-out in `freeze_aware_status` ("without rewriting the 2026-08-13 frozen bytes") read as the same constraint already ratified once. Options are (a) rule delta-5 B2 not-a-defect and keep M-2's operator note un-retired; (b) two-phase freeze with a superseding receipt (the schema has `supersedes`, the vocabulary has `readiness_receipt_superseded`) — an `arm_readiness.py` contract change; (c) transition only receipt-unpinned artifacts (README). All three are magistrate calls.

## What I did land

- **B1 disposition** (instructed): a registered-residual comment inside `validate_generation_write_boundary()` in all three generators — alpha `:487`, beta `:2553`, gamma `:412` — stating the boundary is check-then-write, that post-validation link substitution needs a concurrent adversarial program, which D-139 A1 and single-operator discipline exclude, and that no dirfd/O_NOFOLLOW hardening is attempted.
- **Mechanical repins** forced by those bytes: generator source SHAs in `tests/test_d117_decode_contrast_plan.py:39`, `tests/test_d117_floor_qwen25_1p5b_plan.py:74`, `tests/test_d117_floor_qwen25_7b_plan.py:79`, plus `EXPECTED_PACK_SHA256` in `tests/test_d117_floor_qwen25_1p5b_plan.py:72` (`b7b7d72e…` → `549d4fb1…`; round 4 repinned the same constant).
- **No new tests.** Every regression the brief asked for asserts frozen serialized bytes, which is exactly the blocked behavior; asserting the current draft-after-freeze bytes would ratify a disposition that is the magistrate's to make.

## Verification (real exit codes)

| Run | Result |
|---|---|
| `python3 -m unittest tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan tests.test_d117_decode_contrast_plan` | Ran 61 tests, **OK**, exit 0 |
| `…D117GammaPlanTest.test_authenticated_freeze_transition_preserves_frozen_bytes` | Ran 1 test, **OK**, exit 0 |
| `…D117GammaPlanTest.test_dual_generation_transaction_and_generational_induction` | Ran 1 test, **OK**, exit 0 |
| `git diff --check` | exit 0 |

**Pre-existing environment sensitivity (not mine, reproduced at `b6b5e6d`):** `pack_digest()` and the alpha/beta inventory assertions `rglob` without the `__pycache__` filter gamma's `actual_inventory` documents, so a `__pycache__` left in a v1 pack fails 3 tests. All runs above used `PYTHONDONTWRITEBYTECODE=1` with the pack caches cleared; without it, `b6b5e6d` fails identically. Worth a cheap fix in a later round (align alpha/beta with gamma's filter) so "61 OK" is not environment-dependent.
