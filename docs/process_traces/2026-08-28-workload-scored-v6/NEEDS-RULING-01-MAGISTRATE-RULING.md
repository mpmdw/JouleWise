# NEEDS-RULING-01 — magistrate ruling (Fable, 2026-08-30)

On the WORKLOAD-SCORED-01 filing (`NEEDS-RULING-01-condition-family-suite.md`):
the `_v6` scored leg needs a floor cell and manifest arm whose workload is a
suite manifest, and two frozen contracts refuse that. The proposed minimal
amendment is ADOPTED with the three open choices ruled:

**(a) New version, never extend v1.** `joulewise.condition_family_definition.v2`
with the exact alternative key set as proposed
(`{name, suite_manifest_sha256, suite_item_count, output_cap_tokens,
output_policy, repetitions, warmup_runs}`); v1 stays byte-stable and every
existing `condition_family_sha256` is unmoved. A definition carries EITHER the
v1 integer pair OR the suite set, never both; the `schema_version` string
selects the validator branch, and an unknown version refuses. The v2
canonicalisation covers the new keys.

**(b) The identity fix dispatches on config shape, not campaign generation.**
When `workload_config.suite_manifest_sha256` is present, the identity test is
the suite pair (manifest-hash equality AND
`requested_tokens == suite_item_count × output_cap_tokens`); otherwise the
existing scalar comparison, byte-unchanged. No `_v6`-only special case keyed
on campaign identity — shape dispatch is the general rule and is what keeps
the scalar path's behavior provably unchanged (regression: all retained
non-suite bundles produce identical identity verdicts before/after).

**(c) The `_v6` analysis-manifest sibling is owned by WORKLOAD-SCORED-01.**
S15 owns `_v5` only. This stream builds the `_v6` sibling (cell =
`(model, suite_manifest_sha256)`, floor metric `phase_energy_j.decode` via
multi-interval pairing) as ruled by D-166 R-3, with `affine_mod_ladder_v1` as
the contamination-free control leg.

Boundaries restated: no change to `_v5` (forced-budget integer path); D-041
untouched; the `_v6` leg runs post-campaign after the fiducial night and
carries its own council + contract-lens review + estate before any claim.
The contract change (new schema version) is a council trigger at PR time.
