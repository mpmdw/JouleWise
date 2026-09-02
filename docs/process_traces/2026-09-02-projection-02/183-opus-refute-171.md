# 183 — Opus contract-lens refutation of the 171a draft ruling

Read-only on `/Users/edr/code/JouleWise` @ main a63d45bd; line numbers are this
checkout (seats used the proj02-b worktree, offset ~-8). Verdict: **the draft
does not survive contract review** — four blockers, four should-fixes.

## BLOCKER B1 — (d) does not cure the refusal it was chosen to cure

`_derive_projection_units` refuses TWICE and the draft addresses only the second.
`identity_pins.py:1376-1382` compares each config's
`_declared_identity_from_config(config)` to the unit's single `declared_identity`
and refuses on any difference (the multiplicity refusal is `:1384-1389`), and
`_declared_identity_from_config` (`:1231-1248`) returns the **whole**
`workload_profile` — which for decode carries `suite_manifest_ref`/`_sha256`
(`configs/campaigns/d117_contrast_v5/generate_configs.py:1862-1875`).
Bench counterfactual (run): two decode-shaped configs differing only in the
rotated manifest ref/sha → declared identities **unequal**, so freeze stops at
`:1378` before ever reaching `:1384`. Items 1-5 change nothing about
`declared_identity`, so a `_v5` pack regenerated under (d)+census **still
refuses**, same reason code, earlier line. Opus's (a′) and Fable's (a-i) (both
compare sites, second at `:1453-1464`) close this; (d) alone does not.

## BLOCKER B2 — "producer and consumer carry an EQUAL set" is unsatisfiable

Item 2 and the cl.2 amendment require the floor producer and every consumer of a
unit to carry equal sets of **exact scientific-config identities**. Committed v3
evidence refutes this: contrast `A/decode` `config_set_sha256` = `604f6e2210e8…`
vs floor `alpha` = `bf0ea6a32d7d…`, with identical model artifact `fea4cb94…`,
runtime identity `f1347557…` and declared `workload_profile`
(`d117_contrast_qwen25_1p5b_vs_7b_v3` / `d117_floor_qwen25_1p5b_v3`
`identity_pin_projection.receipts/projection-0001.json`). Bench diff of the two
members' `scientific_config_identity`: they differ only in `hardware_target.notes`
(campaign prose) and `run_metadata.tags` (`d117-floor-…` vs `d117-contrast-…`,
`floor-calibration` vs `comparative-contrast`, `measurement-arm=`,
`df-condition=`) — both inside the identity (`identity_pins.py:212-231` strips
only `run_id`, replacement/calibration tags, `repN`) and campaign-specific by
construction.
Such sets can therefore never be equal across a floor and a contrast pack:
clause 2's cross-pack leg either never passes, or it forces stripping notes/tags
from `scientific_config_identity` — the exact D-044 loosening item 1 claims to
reject. Relatedly, the exact-cell route (`analysis_engine/inputs.py:3909-3916`,
cell identity == consumer identity) never fires for v3 for the same reason;
production binds through the transport/condition-family route (`:3934-3973`),
which does not compare the producer at all. The draft's mechanism is not the
shape of the existing binding.

## BLOCKER B3 — derived set + manifest-only census is a NET WEAKENING at freeze

Item 2 defines `identity_unit_config_set_sha256` as SHA256 over the observed
members' own hashes — **derived**, i.e. the same tautology the draft used to
reject option (c). Its only external constraint is producer/consumer equality,
but `producer_plan_reference` is never machine-consumed (`_validate_unit_bindings`,
`identity_pins.py:414-441`, is shape-only; Facts line 41), so at freeze nothing
bounds identity multiplicity; item 3's census counts **manifest** shas, not
scientific identities. Counterfactual: regenerate with one decode member whose
`hardware_target.notes` or `run_metadata.tags` drift (say a dropped
`measurement-arm=decode` tag). Census still reads 4/4/2/2/2/2/2/2 → passes; the
unit set silently becomes nine members; no producer exists to compare against →
**freeze accepts** a unit that today refuses at `:1384-1389`. Item 5's
"independently declared … set" also contradicts item 2's derivation and D-131
cl.3 "derive; never enter" (`decision_log.md:8416-8422`) — it cannot be both.

## BLOCKER B4 — the new unit key breaks the nine committed frozen receipts

`IDENTITY_UNIT_FIELDS` (`identity_pins.py:89-96`) and `RECEIPT_UNIT_FIELDS`
(`:118-127`) are **exact-key** sets enforced by `_require_exact_keys` (`:370-377`)
at `:499` and `:628`; there is no optional-key path. The nine committed packs
carry frozen projections whose units hold exactly the six keys
(`…/plan_tree.json` → `arm_attachments.identity_pin_projection.identity_units`),
and the nine receipts exactly the eight. Bench (run): adding
`identity_unit_config_set_sha256` to either set makes the v3 pack unit and the v3
receipt unit **REFUSE** with `readiness_identity_artifact_unreadable`. D-131 cl.1
pins the exact-key schema `joulewise.identity_pin_projection_receipt.v1`
(`decision_log.md:8401-8409`), so a field added to v1 mutates a versioned frozen
schema and breaks arm re-verification of every existing pack. Q-B's lean
("projection + receipts only") is exactly the placement that does this — and
Opus's seat adopted "no new identity-unit key" *for this reason*, a constraint
the draft drops while claiming to adopt Opus's findings; item 8 checks only the
registration digest.

## SHOULD-FIX
- **S1 — the triple is undefined for a multi-identity unit.** `config_set_sha256`
  (`:344-356`) is cl.2's third leg; freeze pins `next(iter(scientific_hashes))`
  (`:1498`) against a triple derived from `representative = configs[0]` (`:1390`,
  `:1419`) — with eight hashes that value is arbitrary set-iteration order — while
  the generalized mint requires the producer's single value
  (`mint_floor_artifact_generalized.py:2346-2354`). The draft is silent; every
  resolution collides with the mint path or cl.3.
- **S2 — missed consumer sites; Q-A's "~5 binding sites" undercounts.** Not named:
  the `bind_floor_artifact_evidence` cell gate `analysis_engine/inputs.py:1952-1977`
  ("calibration cell does not have one scientific config identity"), which bites
  the `_v5` FLOOR pack item 7 makes closure evidence; the exact-cell route
  `inputs.py:3909-3916` (distinct from the `:3881` check the draft did name);
  `scripts/mint_floor_artifact.py:1406-1408` and
  `mint_floor_artifact_generalized.py:2722-2724` (absolute vs comparative);
  `generalized:2346-2354`; `detection_floor.py:2098`. Real count ≥ 8.
- **S3 — the amendment text silently deletes live constraints.** Current cl.2
  (`decision_log.md:8410-8415`) enumerates the unit IDs, maps A→1.5B / B→7B
  producers, and requires "the same model/runtime/config triple used by the shared
  floor mint"; the replacement keeps only "exactly four ordered units". Separately
  `_v5` uses `prefill_p512`, so cl.2's literals,
  `docs/phase_2/gamma_arm_readiness.md:11-13` (U8 four-ID list) and D-165's census
  example `cell-prefill_p256-a/-b` (`docs/contracts/d165_dominance_closeout.md:63`)
  are already stale — the rewrite erases that conflict instead of ruling it.
- **S4 — set-vs-multiset rationale fails.** Item 2 picks SET "because floor packs
  may carry different member counts"; per B2 counts are moot, content already
  differs. Within a pack the multiset was Opus's rebalance guard; the census
  restores it only over manifests, leaving B3's identity-drift hole.

## NITs, and Q-C
- **N1** — Q-B is right that `publication_privacy.py:79-92` / `_unknown_keys`
  (`:412-416`) closes only *config* keys, so a projection-only field escapes it;
  the draft records that saving, not the cost transfer to B4's schema.
- **N2** — item 6 counterfactual (i) ("FAIL before the cure and PASS after") is
  unobservable under (d): per B1 it fails at `:1378` both before and after.
- **Q-C** — the synthesis dropped Opus's "no new identity-unit key" constraint
  (its §Q2 files paragraph) and Fable's point that the declared decode identity
  describes a schema-forbidden config (`prompt_tokens` with `suite_manifest_ref`).
  Both are load-bearing: the first is B4, the second is B1.
