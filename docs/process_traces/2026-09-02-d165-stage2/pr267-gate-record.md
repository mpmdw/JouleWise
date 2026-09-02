## Gate record — final head `28501410` (operation-loop §5, C-028 gauntlet)

**Refuters on `6296ce93` (distinct lenses):**
- terra 152, execution lens — all six ruled mutants killed by named tests; R-4 digest `9127a51d…` reproduced from the pristine base tree; `_v5` pack five rows, four-row mutation refuses; 387 passed / 2 skipped. F1 (contract clause-7 wording vs the pre-D-134 frozen v3 pack) → **R-11**, prose only.
- Opus 153, contract lens — F1 BLOCKER: an unruled second `common_mode_replay.result` shape (`status: "refused"`) → **R-5 ACCEPTED, deleted**; F2 `/tmp` pin path → **R-6, ruled R-4c stands, docstring only**; F3 ownership census folds only enumerated syntaxes → **R-7, compiled `co_consts` walk**; F4a refusal at bind not selection → **R-8, moved**; F5 R-1a executed backwards (`ec761c04` red on the pack suite, generator edit in `2b2bb166`) → **R-9 recorded, branch not rewritten**; N3/N4/N5 → **R-10**; N1/N2/N6 recorded, no change.

**Ruling 153a** (magistrate; scratchpad → archived under `docs/process_traces/` with the kernel transaction).

**Fix round 4, Sol xhigh 156 → `28501410`:** R-5 zero denominator now reaches the existing `closeout_input_malformed` boundary; regression asserts no sidecar AND no `floor.json` (rollback holds). R-7 census walks every `joulewise/**` and `scripts/**` module's compiled constants (mutants `"a" + "b"` and placeholder-free f-string in a fifth module: killed). R-8 refusal at first common-mode selection in the gate pass; bind non-entry asserted. Bench: `test_d165_dominance_closeout test_mint_floor_artifact_generalized test_analysis_manifest_v3 test_analysis_finalizer` → 164 OK (2 skipped); generator digest unchanged; no `/tmp` leftovers.

**Delta re-audit of the fix round, luna xhigh 158 (different model from implementer and both refuters):** no BLOCKER, no SHOULD-FIX. Every ruling done as ruled; the hand-built old refused shape is rejected by the validator (`extra keys ['refusal_reason', 'status']`); premature-sidecar mutant fails the R-5 regression; R-8 production call graph CLI → `mint_multi_cell_floor_artifact` → active mint → `_build_v2_artifacts` with sink → selection refusal; the sinkless helper `mint_multi_cell_authenticated_artifact` has no non-test caller (residual, D-161: not an adversary route). N1: runtime-split `join` forms left open by R-7 (recorded).

**Fable apex pass (magistrate, primary diff read):** builder validates its own output before any write; three-path exclusive write with reverse-order rollback; `--d165-replay-out` absent ⇒ legacy write path byte-identical; present with zero common-mode cells ⇒ `d165_replay_output_unused_without_common_mode`. Approved.

**Process record (R-9):** bisectability on `ec761c04` is lost; the head is green. No dissent from any refuter verdict; the one BLOCKER (Opus 153 F1) was accepted, not downgraded.

Merge: magistrate self-merge under D-072 after CI green on `28501410`.
