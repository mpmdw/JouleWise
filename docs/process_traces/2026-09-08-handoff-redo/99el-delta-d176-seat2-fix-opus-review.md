Executed evidence: worktree `/Users/edr/code/JouleWise-wt-d176-seat2`, `git rev-parse --short HEAD` = **f60e3348**. Acceptance suite (9 modules) re-run this session: `Ran 329 tests … OK`. Five mutation probes run and reverted (`git status --porcelain` empty after).

## Findings 1–8

**1 PASS.** `docs/contracts/pack_night_go_receipt.md:502–505`: rows 3–4 now state SIBLING_CHILD (direct child named by the prefixed id; measurement wholly outside; equality/deeper/other-basename refuse). §9 S4 (`:838`) pins `tests/test_run_night.py` `test_rehearsal_plan_and_arm_context_roots_follow_sibling_child_rule` + `tests/test_rehearse_t0_unattended.py:51`. Rows 1–2 verified against `joulewise/night_gate.py:833–836` (`rehearsal_purpose_on_production_id` / `purpose`), asserted with reason at `tests/test_run_night.py:2192–2198`.

**2 PASS.** Fence at `night_gate.py:1067` is `plan.pack_night is None` only — no caller argument. `:910–911` `del pack_conditions`. C1/C2 are derived in `_evaluate_pack_conditions` (`:867`) from re-read custody bytes and a replay of the supplied ARM path. Probes: restoring `or pack_conditions is None` → `test_valid_v3_pack_without_driver_arguments_lifts_unbuilt_fence` **fails**; disabling the record digest check → `test_gate_reauthenticates_c1_and_c2_despite_forged_driver_pass_rows` **fails**. A forged PASS row yields GO only when the bytes themselves re-authenticate, and `measured` carries no `forged` key.

**3 PASS.** `tests/test_arm_readiness_schemas.py:1694` pins the shipped file. Deleting `JouleWise-measurement-20260818` → **fails**.

**4 PASS.** B1 `:816`, B5 `:820`, S2 `:820`, S3, S4, S6, N1 all now carry named tests; no NOT PINNED/PARTIAL remains among the seven.

**5 PASS.** `scripts/run_night.py:1041–1044`: reason = `night_probe_error` (registry `night_gate.py:75`) for unregistered driver causes, detail `"<true reason>: <detail>"`, `refusal.json` authoritative. `tests/test_run_night.py:1968` validates all six receipts under the frozen validator. Setting `receipt_reason = reason` → **fails** (3 subcases).

**6 PASS.** `night_gate.py:848–850` skips SIBLING_CHILD containment for every field except `measurement_root`; contract `:492–498` matches. Deleting that `continue` branch → `test_rehearsal_plan_and_arm_context_roots_follow_sibling_child_rule` **fails** on the own-custody positive case; production-custody placements still refuse.

**7 PASS.** `night_gate.py:842` uses `readiness.ARM_CONTEXT_KEYS - readiness.ARM_CONTEXT_NON_PATH_KEYS` (`arm_readiness.py:442`).

**8 PASS.** `:469` ledger gloss + "disjoint from production roots" restored; `:249` now "all eight flags of §5"; §7.1 seat-2 row (`:616`) records the four added files, the resolver-tests-only share and the additive watchdog test; `tests/test_magistrate_watchdog.py:328` asserts `night_plan_malformed` + HOLD_UNSAFE for a v2 `TRANSACTION_PACK`.

**Frozen seams.** `_RECEIPT_KEYS`, `validate_receipt` (5936 bytes both revs), `NIGHT_DRIVER_REASON_CODES`, `_REFUSAL_KEYS`, `_CONDITION_KEYS`, `RECEIPT_CLASSES`: byte-identical to `0a7c5858`. `NIGHT_GATE_REASON_CODES` is byte-identical to `4b25d29f` (this round touched nothing) but differs from `0a7c5858` by the two `launch_go_receipt_missing`/`_invalid` entries added by the ruled install at the pre-fix head — flagging for the record, not as a fix-round breach.

## New defects

**N1 SHOULD-FIX — every §9/§10.3 citation the fix round wrote for `test_run_night.py` and `run_night.py` is stale.** `test_run_night.py` rows are uniformly +12 low: `2052→2064`, `1987→1999`, `2100→2112`, `2135→2147`, `2119→2131`, `2035→2047`, `2111→2123`, `2064→2076`, `2077→2089`, `2017→2029`. `scripts/run_night.py` is +3: `1105→1108`, `1111→1114`, `1149→1152`, `1173→1176`, `1252→1255`, `1269→1272`. `tests/test_night_plan_writer.py:165→177`. Test *names* are correct, so the rows are findable, but no cited line lands on its symbol. Cure: rewrite those 17 numbers.

**N2 NIT —** `night_gate.py:832` does `from scripts.rehearse_t0_unattended import _production_inventory`: `joulewise/` now depends on `scripts/` (no `scripts/__init__.py`), and `ModuleNotFoundError` is outside the `(OSError, ValueError, RuntimeError, KeyError, TypeError)` catch at `:1080`, so an import failure crashes rather than refuses. Cure: move `_production_inventory` into `arm_readiness.py`, or add `ImportError` to the tuple.

**N3 NIT —** `_pack_evidence` (`:787`) compares `arm_state["authored"]["receipt_paths"]` against an `expected_paths` set it derives identically; `_evaluate_pack_conditions:895` now supplies that same derivation, so the check is tautological. Its force survives via the ARM-evidence membership test at `:800`.

**N4 NIT —** `ARM_CONTEXT_NON_PATH_KEYS` re-states the four keys, and `tests/test_run_night.py:2163` derives its loop from the same expression, so a key mis-classified as non-path is checked by nothing.

**VERDICT: LAND-WITH-FIXES** (N1 before merge — mechanical; N2–N4 deferrable).
