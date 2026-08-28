# Opus seat — live-proof path (Opus 5, read-only, blind). Verbatim.

Read-only; nothing modified. Answer follows.

---

## Three code facts that change the question

**F1 — the plan cannot be shrunk below ten blocks.** `joulewise/analysis_manifest_v3.py:2152-2159` refuses any prospective manifest whose `design.sampling_plan.planned_n_blocks != 10`; `PLANNED_N_BLOCKS = 10` (`:34`) and the frozen block roster must have exactly that length (`:946`). A `--n-blocks 1` family is therefore not a generator-only cure: it requires editing the claim-bearing analysis-manifest validator. The runsheet's B2 "smallest cure" is understated by that whole module.

**F2 — one A/B/B/A block cannot answer for a DATA reason.** One block is one observation (`analysis_engine/__init__.py:645-691`: positions A1/B1/B2/A2 collapse to one `value_a`/`value_b`). At `:696-697` `complete_blocks < 2` emits `insufficient_complete_blocks`; at `:698-699` `complete_blocks < planned_n` emits `fixed_n_plan_incomplete`. Both are registered (`claims.py:92,176`) and neither is in `DATA_REASON_CODES` (`reason_kinds.py:36-50`), so `CONTRACT_REASON_CODES = REASON_CODES − DATA − DEAD − LOCK` (`:63-65`) contains both. `insufficient_complete_blocks` fires first. Path (B) as posed **fails its own gate**; against the real `_v4` manifest it never even reaches that code, because nine missing blocks give per-contrast `bundle_missing` (also CONTRACT).

The DATA member is a different code: `randomization_check_insufficient_blocks`, emitted when `len(deltas) < 6` (`sensitivity.py:116-123`), propagated at `__init__.py:1208-1209`, DATA at `reason_kinds.py:47`. So the minimum block count that can answer DATA is **2**, and the only count the validator permits is **10**.

**F3 — the registry installs exactly three ids.** `d117_row_registry_v2.json → freeze_evidence_lifecycle.successor_policy.successor_pack_ids` is `{ALPHA/BETA/GAMMA: …_v4}`; anything else refuses at `arm_readiness.py:4128-4131`. But `family_publication_first_generation: 4` plus `arm_readiness.py:7335-7338` means a pack whose predecessor is `_v3` (generation 3 < 4) **skips `_gate_family_publication` entirely** — B9 dissolves on its own, no admission exception needed. `cross_chain_numbering` is `monotonic_predecessor_ordinal`, not adjacency, so an invented `_v8` was never required either.

## (A) Diagnostic family — more expensive than budgeted, and the bypass is real

Touched: three `configs/campaigns/*/generate_configs.py` (`N_BLOCKS` `:92`, identity `:168-180`), `joulewise/arm_readiness.py` (admission + GENESIS), `scripts/generate_arm_readiness.py`, `capture_t0_step.py`, `prewindow_check.sh`, `mint_floor_artifact_generalized.py`, **plus `analysis_manifest_v3.py:34,946,2152-2159`** (F1). Mint-path implication is worse than "estate 11 re-runs": `_r1_changed_paths(derivation_commit → current_head)` (`arm_readiness.py:4715-4732`) subtracts only `irrelevant_path_allowlist` — 112 entries, **zero** under `joulewise/` or `scripts/` — so every estate-11 receipt derived before the cure refuses `readiness_r1_dependency_changed_set`. And the diagnostic family needs its own full estate (29 evidence policies, 35 row policies) derived at the smoke head. Estimate: 4-6 Sol-days, two estates, one relaxed claim-bearing validator. The bypass risk is not hypothetical — F1 forces the relaxation to live inside the validator that defines a legal claim.

## (B) Shakedown-as-proof — contamination answers

Contaminates only through three shared authorities:
1. **Same `RUNS_ROOT`**: a duplicate bundle directory makes `ordinary_present_bundle_paths` (`whole_window.py:2315-2337`) return >1 → `"ambiguous"` (`run_campaign.py:5402-5405`). A separate runs root cannot contaminate.
2. **The calibration ledger**: one repo-level chain at `calibration_ledger.py:95` with a *tracked* pin (`configs/calibration/calibration_ledger_head.json`, sequence 76). Brackets run in the main checkout advance it and force a committed pin bump on main.
3. Nothing else. Occurrence supersession is per-runs-root; `whole_window_verdict_conflict` is stored-vs-derived inside one root (`whole_window.py:5326-5386`); `capture_pipeline_superseded` is anchor-method era, not time order (`uncertainty_evidence.py:1302-1325`); the seal is procedural (`real-transaction-runbook.md:1220-1234`).

**Copy-safe: yes.** `analyze-claims` reads `--runs-root` and writes only `--output` (`cli.py:2010-2019`).

**New blocker the runsheet misses (B10):** a fresh checkout has the tracked pin at 76 but not the untracked `runs/calibration_observation_ledger.jsonl` → `calibration_ledger_missing` (`calibration_ledger.py:2019-2021`) + `calibration_ledger_rollback` (`:2043-2048`). Copy the 136 KB ledger in. Custody bytes are *not* needed: all 38 locators are absolute iCloud paths, so `repo_root` is unused (`:1781-1783`).

## (C) Recommendation — the real `_v4` run is the proof; buy the insurance separately

**(i)** Zero new Sol-days of code. Two rehearsals, then the honest run:
- **Arm-abort rehearsal** on the real frozen pack: `arm_to_consume_budget_ns = 300 s` (registry `arm_policy`), so registry admission, successor chain, freeze receipt, T-0 env keys and prewindow check all prove out in five minutes with no bundle written. Caveat to verify first: `t0.single_launch_capability.v1` requires `attempt_ids_unused`/`session_id_unused` (`arm_readiness.py:980-984`) — use throwaway ids.
- **Desk rehearsal** of binding → verdict → extraction → mint → finalize → `analyze-claims` on a copied tree (copy-safe per above).
- Then the single real night; a surviving CONTRACT defect surfaces inside the first block (~10 min), not at hour three.

**Must not touch:** `analysis_manifest_v3.py`, `analysis_engine/*`, `arm_readiness.py`, the three generators, `d117_row_registry_v2.json`. Any of them re-opens the R1 changed set and voids estate 11.

**(ii)** C — same head, same pack, same code, same corpus. A is the *weakest* evidence despite the highest cost: a different pack, a bypass lane, and a relaxed validator.

**(iii)** Strongest argument against C: no gamma corpus exists on disk (`ls runs/*v3*` → none), so extraction/mint/finalize are rehearsed on non-gamma bytes and a corpus-shaped defect is found only after the machine time is spent. That is the risk the gate was written to buy, and C does not fully buy it.

**(iv)** Same night — same *run*. The 5-minute arm budget means the rehearsal arm must be a separate, earlier arm; it cannot straddle the T-0 dwell.
