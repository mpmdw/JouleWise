# Ruling 171a — decode-unit identity under prompt rotation (D-131 cl.2/cl.3 amendment)

Magistrate (Fable), 2026-09-02, over: consult 171 (Opus 5 / blind Fable / Sol
xhigh, split three ways), cold gate 182 (fresh Fable: UPHOLD WITH AMENDMENTS)
and 183 (Opus contract-lens refuter: four blockers against the draft). Every
fact below was re-verified at the bench by the magistrate or by two seats.

## What the cold gate corrected in the draft (no dissent; all adopted)
- C1/B2: "producer and consumer carry EQUAL unit-set hashes" is unsatisfiable
  and was never checked. v3 receipts: floor `alpha` config_set `bf0ea6a3…`,
  consumer `A/decode` `604f6e22…` with identical declared workload; the
  difference is pack-specific tags/notes inside `scientific_config_identity`.
  Floor→consumer binding is condition-family transport
  (`analysis_manifest_v3.py:3395-3420`, `inputs.py:3934-3973`). STRUCK.
- B1/cold bench: the FIRST live refusal is the declaration-equality check
  (`identity_pins.py:1376-1382` main; declared matches 0/20 decode configs
  because `generate_configs.py:2572-2588` re-types from `workload_for()`),
  not the multiplicity check. Both are cured below; the regression's
  counterfactual (iv) covers the first.
- B4/C3: no new exact-key receipt or unit field. `identity_unit_config_set_sha256`
  is WITHDRAWN. The set and census live in `declared_identity.workload_profile`
  (free mapping, `identity_pins.py:62-71, 509-513`).
- B3/S4: a member-derived set with a manifest-only census would ADMIT a
  member whose tags/notes drifted (today it refuses). Cured by R-4 below.
- S3: `_v5` prefill units are `prefill_p512` (G2-a pin), while D-131 cl.2,
  U8 (`gamma_arm_readiness.md:11-13`) and D-165 (`d165_dominance_closeout.md:63`)
  still say `prefill_p256`. Ruled below (R-6); the rewrite must not erase it.

## Rulings
R-1 (exact identities stay exact). `scientific_config_identity` is not
redefined. D-044 stands. Replacement matching (`inputs.py:2911-2950`), NEG-8,
bundle mint unchanged. Option (a-i) REJECTED (operator-entered identity field
against cl.3; loosens replacement lineage). Option (a′) REJECTED (freeze-local
cure leaves mint and analysis refusing). Option (d) ADOPTED as amended.

R-2 (declared closed set, from the rule, never folded). The generator
declares, per decode unit, in `declared_identity.workload_profile`:
`suite_manifest_set` = the ordered list of {manifest ref, effective sha256,
declared member count} computed from the pre-registered rotation rule
(`decode_prompt_index(block) = (block-1) % 8` × the block schedule), plus the
common profile (the workload fields shared by every member, i.e. the config
workload minus `suite_manifest_ref`/`suite_manifest_sha256`). The generator
NEVER derives the declaration by reading emitted configs and never re-types
it from `workload_for()`; `generate_configs.py:1334`'s hardcoded
`DECODE_PROMPT_TOKENS["A"]` is removed with it.

R-3 (freeze compares declaration to emission, fail-closed). For each unit,
`freeze_projection`: (i) projects each config's workload to the common
profile and requires equality with the declared common profile; (ii)
requires each config's manifest sha to be a declared member; (iii) requires
every declared member to be emitted with exactly its declared count; (iv)
refuses any extra, missing, duplicate, or unauthenticated member.
Prefill units: one member, unchanged behaviour.

R-4 (one identity per manifest class — closes B3). Within a unit, members
that bind the same manifest sha must share ONE `scientific_config_identity`;
the number of distinct member identities must equal the number of declared
manifests. A drifted tag or note on any member therefore still refuses,
exactly as today.

R-5 (unit config-set digest; no new key). `config_set_sha256` on the unit is
the unit's config-set digest: one distinct member identity → that hash
(byte-compatible with every committed receipt and the shared-mint producer
pin); several → `SHA256("joulewise.identity_unit_config_set.v1" ‖ "\n" ‖
"\n".join(sorted(distinct member scientific hashes)))`. The domain string
is fixed here. The representative-config triple (`identity_pins.py:1390,
1419, 1498`) is replaced by this digest so no value depends on set-iteration
order (S1).

R-6 (consumers). (a) `inputs.py:3881` — consumer evidence identities must be
non-empty and a SUBSET of the frozen consumer unit's declared set (read from
the frozen receipt bound by the U8 readiness record); any identity outside
the set refuses; the exact-cell route (`:3905-3916`) stays single-identity.
(b) `bind_floor_artifact_evidence` cell gate `inputs.py:1952-1977`,
`mint_floor_artifact.py:_source_regime` (~:755-805) and `:1406-1408`,
`mint_floor_artifact_generalized.py:2346-2354` and `:2722-2724`,
`detection_floor.py:2098`: gain set semantics ONLY IF the `_v5` ALPHA/BETA
floor plans rotate prompts. FLOOR PROMPT REGIME IS RULED NOW so the fix seat
is not blocked: the `_v5` floor packs use ONE prompt manifest per floor
unit (single identity), matching every committed floor receipt; the
decode-floor manifest is the rotation's index-0 manifest, pre-registered in
the floor plan. Consequently (b) sites are NOT changed in this fix; a test
pins that a single-identity unit's `config_set_sha256` is byte-identical to
today's value. Rotating floors, if ever wanted, is a new ruling.

R-7 (D-131 cl.2 replacement text). "GAMMA retains exactly four ordered
units: `A/decode`, `A/prefill_p<N>`, `B/decode`, `B/prefill_p<N>`, where N
is the prefill token length fixed by the G2-a `joulewise.prefill_prompt_pin.v2`
record (512 for `_v5`; the `prefill_p256` literals in this clause, in U8, and
in the D-165 census example were `_v3`-era values and are superseded by
`<N>`). A references the smaller model's producer plan and B the larger's,
each using the same model/runtime pins as the shared floor mint. Each unit
binds an independently declared, closed set of exact scientific-config
identities, digested into `config_set_sha256` as the unit's config-set digest
(one member identity: the scientific hash; several: the domain-separated set
digest). Within a unit the declared per-manifest member census — computed
from the pre-registered rotation rule, never folded from emitted configs —
must equal the emitted census at freeze, and members binding one manifest
share one identity; a missing, extra, duplicate, drifted, or unauthenticated
member refuses. Which manifest a member binds is a realization fact recorded
per config. Floor producer and consumer units bind through condition-family
transport; their config-set digests are not required to be equal."
Cl.3 rider: "Raw config bytes and inventory bindings remain authoritative for
member identity; the declaration compares the projected common profile plus
the declared set, never a re-typed workload."

R-8 (regression, red first). `tests/test_d117_contrast_v5_pack.py` gains a
generated-pack freeze + `verify_frozen_projection` PASS test (Sol 171 F3
recipe: temp git repo, `write_prefill_pin`, module-level model-artifact fake,
realistic `_runtime_probe_metadata` stub, `_mint_git_anchor` patched).
Counterfactuals, each its own assertion: (i) current generator output FAILS
before the cure, PASSES after; (ii) one decode member on an unlisted manifest
→ REFUSE; (iii) declared census off by one → REFUSE; (iv) declaration
re-typed from `workload_for()` → REFUSE at the declaration check; (v) one
member with a drifted tag → REFUSE (R-4); (vi) a single-identity unit's
`config_set_sha256` unchanged byte-for-byte vs the v3 receipt value.

R-9 (sequencing). Separate branch off the projection-02 merge head (PR
#269). Commit 1 = red test; commit 2 = cure. Arming stays forbidden until U8
passes. Closure evidence = regenerate and freeze/verify all three `_v5`
packs (ALPHA, BETA, GAMMA) — the P-8 runbook re-run live by the magistrate.
Registration digest `1c0a4a11…` must be unchanged (pinned tests).

R-10 (process). Two seats plus the synthesis carried "producer/consumer sets
equal" from prose into draft contract text without opening a committed
receipt. The pre-transaction "decided ≠ done" sweep gains one line: any
cross-pack equality clause is checked against one committed receipt pair.
Queued for the cold gate with the Opus 159 §E proposal (rule 11: not adopted
by this ruling).
