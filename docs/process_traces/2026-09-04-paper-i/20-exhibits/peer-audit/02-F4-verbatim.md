### F4 — should_fix — Floor consumption incompletely binds uncertainty operands

**What is wrong.** The analysis loader calls `bind_floor_artifact_evidence` (`analysis_engine/inputs.py:3175-3184`). Its binding loop validates bundles, complete hashes, config/order/stack identities and point metric equality (`1866-1901,1933-1989`), but does not rederive and compare member/block uncertainty widths. The floor validator recomputes widened floors from widths supplied **by the floor record** (`detection_floor.py:3123-3163`).

The mint is stronger: `floor_mint_estimator.py:683-717` recomputes common-mode widths from authenticated sources and checks exact equality. That path is called by `scripts/mint_floor_artifact_generalized.py:4127`, not the above analysis binder. A coherently generated wrong-width floor is therefore not independently caught at every consumption boundary. Finalized-manifest byte seals do catch subsequent substitution (`analysis_engine/inputs.py:842-866,883-897`); this is not a one-field-edit bypass. The paper already acknowledges incomplete floor binding (`draft-v1.md:398,672`).

**What I would do differently.** Reuse the mint's authenticated recomputation on the exact submission floors. Share that path with the consumer if needed; do not create another estimator or custody service.

**Minimum paper evidence.** Source members, actual widths, bracket/basis, estimator identity and reconstructed/published floor comparison. Acceptance: correct points with coherently wrong widths cannot count as source-reproduced; actual submission floors independently match. **Cost:** half to one day with sources available. **D-161:** a relevant generator/operator mistake class; mint protection exceeds generic consumption protection.

