# Consult 171 — magistrate synthesis and DRAFT ruling (for the cold gate; not yet in force)

Question: the generated `_v5` pack cannot freeze because each decode unit
carries 8 distinct `scientific_config_identity` hashes (one per rotated
prompt manifest), while `freeze_projection` demands one (bench-verified:
`identity_pins.py:1445-1466`). Three seats read the code independently:

| Seat | Position | Decisive fact it contributed |
|---|---|---|
| Opus 5 (`out/171-opus-decode-identity-consult.md`) | (a′) manifest-MULTISET identity, computed inside `_derive_projection_units` only; keep `scientific_config_identity` exact | Changing the shared identity function would let a prompt-7 bundle replace a prompt-1 member (NEG-8 gate, replacement matching, bundle mint). Measured histogram 4/4/2/2/2/2/2/2 — a bare set admits a rebalanced pack. Generator must not re-type identity from `workload_for()` (root cause; fired twice, same signature). Nine committed frozen receipts pin derivation identity. |
| Blind Fable (`out/171-fable-decode-identity-consult.md`) | (a-i) carry `workload_profile.suite_manifest_set_sha256` in every config and project in the SHARED `scientific_config_identity` | A freeze-local fix leaves `mint_floor_artifact.py:_source_regime` and `analysis_engine/inputs.py:3866-3918` refusing multi-identity units → a night could be collected into an un-mintable, un-analyzable pack. MAGISTRATE VERIFIED both refusal sites at the bench. |
| Sol xhigh (`out/171-sol-decode-identity-consult.md`) | (d) keep per-config exact hashes; add `identity_unit_config_set_sha256 = SHA256(domain ‖ sorted unique member scientific hashes)`; producer and consumer unit sets must be equal; mint/analysis binding compares unit sets | (a) as written still yields 8 hashes because the `decode-prompt=…` tag stays in identity; D-044 says sameness is hash equality; D-165 census fixes four cells; floor plans ALPHA/BETA do not exist yet, so cross-pack set equality is unprovable today. |

## Magistrate lean: (d), amended by Opus's two findings

1. Exact identities stay exact. `scientific_config_identity` is NOT
   redefined (D-044 stands; replacement matching, NEG-8, bundle mint
   unchanged). This rejects Fable's (a-i) on Opus's harm.
2. Unit binding by closed SET. New field
   `identity_unit_config_set_sha256 = SHA256("joulewise.identity_unit_config_set.v1" ‖ "\n" ‖ "\n".join(sorted(unique member scientific hashes)))`
   per projection unit. Floor producer and consumer must carry EQUAL
   unit-set hashes; `_source_regime` (both mints) and the analysis claim
   gate compare unit-set hashes, not single scientific identities. Set,
   not multiset, for CROSS-PACK equality because floor packs may
   legitimately carry different member counts.
3. Balance is a freeze-time DECLARATION check, not an identity. The
   generator declares, per decode unit, the manifest census
   (manifest sha → member count, e.g. 4/4/2/2/2/2/2/2) computed from its
   rotation RULE (prompt list × block schedule), independently of the
   emitted configs; `freeze_projection` compares declared census to
   observed and refuses on any difference. This takes Opus's multiset
   point without weakening cross-pack binding, and answers Sol's (c)
   objection: the declaration is independent (from the rule), not folded
   from the artefacts it checks.
4. Prefill units are unaffected (1/1/1); their unit set has one member.
5. D-131 cl.2 amendment text (proposed): "GAMMA retains exactly four
   ordered units. Each unit binds an independently declared, closed,
   domain-separated set of exact scientific-config identities
   (`identity_unit_config_set_sha256`); the floor producer and every
   consumer of that unit carry an equal set; a missing, extra, duplicate,
   or unauthenticated member refuses. Within a unit, the declared
   per-manifest member census must equal the emitted census at freeze."
   Cl.3 unchanged in substance; add: "raw config and inventory bindings
   remain authoritative for member identity."
6. Permanent regression: `tests/test_d117_contrast_v5_pack.py` gains a
   generated-pack freeze + committed `verify_frozen_projection` PASS test
   (Sol F3 recipe: temp git repo, `write_prefill_pin`, module-level model
   fake, realistic probe, `_mint_git_anchor` patched); counterfactuals:
   (i) unchanged current generator output → must FAIL before the cure and
   PASS after; (ii) regenerated pack with one decode member on an unlisted
   manifest → REFUSE; (iii) declared census off by one → REFUSE.
7. Sequencing: separate branch from the projection-02 merge head; red
   test first commit, cure second (Fable Q4). Arming stays forbidden until
   U8 passes (D-131). Regenerate and freeze/verify all three packs as the
   closure evidence (Sol residual risk).
8. Registration digest `1c0a4a11…` untouched by every option (Sol V3,
   Fable item 7).

## Open for the cold gate

Q-A: Is (d)+census strictly better than Fable's (a-i)? Fable's route
changes ONE function and every consumer follows; (d) changes ~5 binding
sites (two mints, analysis gate, identity_pins, generator). Cost of a
missed site under (d) = a night refused late; cost of (a-i) = exact
replacement semantics lost. The magistrate prefers the fail-closed error.
Q-B: Should the unit-set hash be serialized into configs (schema change,
`publication_privacy.py` allowlist) or live only in projection/receipt
artefacts? Lean: projection + receipts only; configs unchanged.
Q-C: Anything in the three reports the synthesis dropped that changes the answer.
