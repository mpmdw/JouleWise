# 07 — Delta review (contract lens), commit `aceffb26`

Fresh non-author reviewer, read-only, worktree `/Users/edr/code/JouleWise-wt-paper-l` at
`aceffb26`. Scope: the two test files in that commit plus report 06. No edits, no commits,
no discovery runs.

**Verdict: DEFECTS — 1 should-fix, 2 nits. The option-(b) call itself is correct.**

## Executed evidence

All runs used `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise`,
one target at a time, from the worktree root.

E1 — new d117 pin (single target):

```
tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_decode_assignment_is_fixed_zero_for_all_blocks_and_arms ... ok
Ran 1 test in 0.130s
OK
```

E2 — the decisive probe for Q1. Ran two committed identity-set tests with the new
`_generate_two_manifest_decode_pack` helper neutralized (`mock.patch.object` replacing it
with `fixture.generate_pack(root)`), i.e. against the **real, unpatched D-166 generator**,
whose A/decode inventory is a genuine singleton:

```
test_production_accepts_same_authenticated_fixture_without_receipt_perturbation ... ok
test_production_refuses_identity_outside_authenticated_set_with_named_reason ... ok
Ran 2 tests in 9.657s
OK
```

## 1. Is (b) the right call, and does the gate accept a real singleton?

**Yes on both counts.**

The singleton is the intended production state, not an accident.
`decode_prompt_index` (`configs/campaigns/d117_contrast_v5/generate_configs.py:1398`)
returns `0` unconditionally, and `validate_decode_prompt_assignment_rule`
(`:683`, called at `:951` and `:3021`) **raises** if any block's index is non-zero — the
generator refuses to emit a rotating assignment at all. `decode_declared_suite_manifest_set`
(`:1496`) therefore declares one member with `declared_member_count = 20` per arm. Option (a)
— reintroducing per-run scientific variation to satisfy the old fixture — would have to
defeat that guard. (b) is the only option compatible with D-166.

The frozen consumer gate accepts a real singleton. `identity_unit_config_set_sha256`
(`joulewise/identity_pins.py:262-273`) has an explicit singleton branch (`len(distinct) == 1`
returns the member hash), and the same function is used on the producer side and by the
consumer at `joulewise/analysis_engine/inputs.py:4059-4063`, so the fold agrees. Downstream,
`_floor_request_or_refusal` (`inputs.py:4126-4130`) sets `consumer_identity` precisely when
the evidence carries one identity, which is the **exact-cell** path — a singleton is the
*happy* case there, not an edge. E2 confirms this end-to-end on a real D-166 pack: acceptance
with empty `reason_codes`, and the drift refusal still fires.

**Should-fix (S1): after this commit, no committed test drives the real singleton D-166 pack
through the consumer gate.** `_generated_frozen_gate_pack`
(`tests/test_analysis_inputs.py:432`) is the single pack source for 11 of the 13
`FrozenConsumerIdentitySetTests`, and line 439 now routes every one of them through
`_generate_two_manifest_decode_pack`. Before `aceffb26`, the four exact-cell tests (`:723`,
`:747`, `:782`, `:794`) ran against the real singleton pack and passed — that is exactly what
report 06's V0 shows (6 failures, all six being the `_generated_transport_case` users at
`:767`, `:863`, `:882`, `:1008`, `:1018`, `:1145`). So the commit did not merely repair
broken coverage; it also **silently removed working coverage of the production shape**.
The producer half survives — `test_generated_v5_pack_freezes_and_verifies`
(`tests/test_d117_contrast_v5_pack.py:969`) still freezes and verifies the real singleton
pack — but nothing exercises `_frozen_consumer_identity_set` +
`_floor_request_or_refusal` against a singleton *declared* set. That matters because the
singleton is the only shape D-166 production can ever present, and the fold's singleton
branch (`identity_pins.py:270-271`) is a distinct code path from the multi-member domain-
separated fold.

Remedy is cheap and already demonstrated: one added test that builds the pack with the plain
`fixture.generate_pack(root)`, asserts `len(_frozen_consumer_identity_set(...)) == 1`, and
asserts `_generated_exact_case` resolves with no reason codes. E2 shows it runs in ~10 s.

## 2. Do the refusals still refuse? Is the fixture hollow?

**They still refuse, and the fixture is not hollow.** The six refusals are preserved because
the fixture produces two *genuinely distinct* scientific identities through the real
machinery, not by hand-editing a pack:

- The second binding is a real suite manifest written into the pack. `decode_suite_relpath`
  and `decode_suite_manifest` are both patched, and the generator writes every prompt index
  (`generate_configs.py:3081-3087`) and inventories every one (`:1291-1293`), so the fixture
  file `02_identity_set_fixture_prompt_zero.json` exists on disk under the patched name.
- The mutated `suite_id` is **re-validated**, not smuggled: `render_suite_manifest_bytes`
  (`:1205-1209`) runs `SuiteManifest.from_mapping` on the mutated mapping before serializing,
  and the declared digest comes from `suite_manifest_sha256(manifest(arm, 1))` over the same
  object.
- The projection census actually enforces the declaration. `_derive_projection_units`
  (`joulewise/identity_pins.py:1629-1646`) re-reads each declared manifest from the pack and
  compares digests; `:1680-1697` refuses any config emitting an undeclared manifest;
  `:1698-1712` refuses a `declared_member_count` census that differs from the emitted counts;
  and the `divergent_manifests` check immediately after requires each declared manifest to map
  to exactly one scientific identity. The fixture's 10/10 declaration must therefore be true
  of the pack, and it is — otherwise freeze would raise.
- The guard against silent re-collapse is retained: `_generated_transport_case` still asserts
  `len(configs) == 2` (`tests/test_analysis_inputs.py:537`). If a future change made the
  fixture emit one identity again, the transport tests fail loudly rather than degrading into
  vacuous singleton passes.
- The new assertions strengthen rather than weaken: `:1160` upgrades subset to set equality,
  and `:1164-1183` re-read both manifests from disk, re-verify their SHA-256 against the
  config bindings, and prove the two identities differ *only* in suite bindings while prompt,
  token IDs, output policy and tags agree.

No refusal is bypassed by construction. The one unproducible aspect is stylistic: production
would never emit two differently-named manifests carrying an identical prompt-zero payload.
Nothing in the gate inspects prompt content, so no refusal depends on that — see N1.

## 3. Is the d117 pin correct and stable?

**Correct, and appropriately stable.** `tests/test_d117_contrast_v5_pack.py:1039-1060` asserts,
for each arm: 20 decode configs, 20 distinct `run_id`s, exactly **one** distinct
`scientific_config_identity_sha256`, and `decode_declared_suite_manifest_set(arm)` member
counts `[20]`. That is the true post-D-166 shape (E1 passes; report 06 V5 independently shows
`distinct_scientific_identities: 1`, `declared_manifest_counts [20]`).

It is not brittle against ordinary drift: the identity normalizer strips `run_id` and the four
`_CALIBRATION_COLLECTION_TAG_PREFIXES` tags (`joulewise/identity_pins.py:174-179`,
`:233-252`), so block/label/sequence/plan-SHA variation cannot break the count-1 assertion,
and the placeholder plan SHA `"a" * 64` is filtered too. It *would* break if the campaign's
block count or ABBA membership changed (20 and `[20]` are hard-coded) — but the enclosing test
already hard-codes 10 blocks, and such a change should be loud. It would also break if D-166
were superseded by a rotating rule, which is the point of the pin.

Gap, not defect: the pin does not assert that arms A and B differ from each other, nor pin the
identity digest itself.

## 4. Anything else

**N1 (nit).** The fixture replaces prompt index 1's real manifest for both arms, so the
generated pack contains a manifest set no production run of this campaign could emit. Harmless
today (no validator links prompt content to suite naming), but it means these six tests now
describe a hypothetical pack shape rather than the campaign's. Worth one comment line at
`tests/test_analysis_inputs.py:367` saying so explicitly beyond "synthetic"; the docstring
currently explains *why* two manifests, not *that the pack is no longer campaign-shaped*.

**N2 (nit).** `_generate_two_manifest_decode_pack` hard-codes the 10/10 split as
`run["block_index"] > 5` while `declaration()` hard-codes members `10, 10`. The two are
coupled by hand. The inner `assertEqual(members[0]["declared_member_count"], 20)` at
`:415-416` does catch a divergence, but via the projection census rather than at the split —
deriving the halves from the observed count would be self-maintaining.

No production code, generator, supersession JSON, contract or gate logic was touched by
`aceffb26`; the diff is tests plus report 06 only (`git show aceffb26 --stat`: 3 files, 306
insertions, 1 deletion). Report 06's claims that I could check independently (V0's six-failure
attribution, V5's identity counts, the option-(b) rationale) all hold.
