# 13 — Apex Fable code-reading diff gate + overbuild prune, GAMMA root keys (rows 7 and 8), 07:45 PDT (clock-read)

Magistrate `d6888966` (Fable 5.1), full session context. Diff read: `git diff 664b3f6c..678d9bcc` — the one-line
emitter change at `configs/campaigns/d117_contrast_v5/generate_configs.py:2697`, the 14-line pack regression
(`tests/test_d117_contrast_v5_pack.py:952–965`), and the 51-line T-0 regression
(`tests/test_arm_readiness_evidence_t0.py:907–957`), plus the reader at `joulewise/arm_readiness.py:8505–8522`
and `joulewise/arm_readiness_evidence_t0.py:1008–1022`. Inputs: contract refuter (record 11), lead bench mutations
(record 12), Opus counter-review (`lt-gamma-opus-counter-review.md`, lieutenant bookkeeping branch).

## Design-level questions and answers

1. **Is the emitter the right side to change, not the reader?** Yes. The T-0 reader binds a live ARM runs root's
   basename to a leaf frozen in the pre-registered plan tree; that is an evidence/pre-registration fence, the class
   D-161 keeps fail-closed. Both floor `_v5` generators and this generator's own calibration-plan emitter
   (`:1881–1884`) already use the canonical pair; the plan-tree emitter was the odd one out. A tolerant reader would
   buy no live capability (no legacy-key pack is on the live roster) and would ratchet the accepted spellings.
2. **Does the change disturb any frozen artifact?** No. The GAMMA `_v5` directory holds only the generator and two
   D-166 registration JSONs; no plan tree, sidecar or receipt exists for it on main. The generator's blob sha is
   pinned nowhere. Historical v1/v2/v3 trees keep their legacy keys as frozen bytes (sidecars verified matching by
   the counter-review, E5b) and are not read semantically by current code.
3. **Are the regressions defect-shaped and do they exercise production call sites?** Yes. The pack regression runs
   the real `generator.generate` and pins the emitted mapping exactly; the T-0 regression calls the real
   `t0._root_observation` with the generated tree (positive) and the legacy pair (negative, refusal at line 1020).
   Bench mutations A/B (record 12) and the counter-review's E5/E6 kill in both directions (emitter reverted; reader
   loosened to require the legacy pair).
4. **Is anything design-bearing left open?** Two items, both outside this diff and both to REGISTER, not to fold in:
   (a) the plan-tree `roots` key set has no ONE home in `docs/contracts/`; the schema lives only in two readers and
   ten emitters, which is the mechanism of this defect (counter-review F2). Creating a contract section is
   process-bearing under rule 11 → lane with a cold-gate or Ed step for the contract text itself.
   (b) `joulewise/arm_readiness.py:8511–8514` lets a `root_namespace` mapping (`claim_leaf`/`bound_leaf`) override
   the canonical `roots` pair; no producer of `root_namespace` exists anywhere in the repository; the T-0 reader has
   no such fallback, so a hand-written tree would pass the receipt binding and be refused by the T-0 author
   (counter-review F3). Delete-or-mirror is a live-code change to a fail-closed binding → its own lane with its own
   refuter.
   Nits F4 (tree-faithful negative fixture) and F5 (`methodName` in the cross-module fixture reach-in) are optional
   and ride the next touch of these files; not folded in (fix rounds introduce defects; the head is complete).

## Prune (row 8)

Nothing overbuilt: one-line rename plus two witnesses that do not duplicate each other (one pins the emitter's
shape, one pins the reader's accept/refuse). No shim, no new abstraction, no compatibility path. Merge-able as is
once rows 2 (execution refuter), 9 (replay) and 11 (CI) close.

Verdict for row 7: PASS at `678d9bcc` (content) / `804eb394` (merge of main, bookkeeping-only commits since
`664b3f6c`).
