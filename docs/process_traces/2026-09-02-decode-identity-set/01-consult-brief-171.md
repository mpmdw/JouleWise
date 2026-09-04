ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
WRITE_SCOPE: []

# Consult 171 — decode identity-unit semantics: a real `_v5` pack cannot freeze

Read-only. Checkout: `/Users/edr/code/JouleWise-wt-proj02-b` (detached at
`a37b0b9f` = branch `feat/v5-prefill-realized-projection-02`; main `a63d45bd`
differs only by clause-7e bookkeeping in the generator + kernel rows). Write
nothing under the checkout; `TMPDIR` = a subdirectory you create under
`<scratchpad>/`.
Python: `/Users/edr/code/JouleWise/.venv/bin/python`. You may run one-off
read-only python snippets (imports, hashing, loading JSON). No git write
commands; do not run the test suite.

Licence to disagree with the magistrate's lean (end of brief) and to propose
an option not listed. One round; the magistrate decides.

## Verified facts (bench, 2026-09-02 ~04:00)

1. Runbook `scratchpad/p8/p8.py` (transcript `scratchpad/p8/dry-run.log`)
   generated a real `_v5` pack at
   `scratchpad/p8/root/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`
   (80 member configs) from the frozen generator with the REAL Qwen3
   tokenizers (both models share `tokenizer.json` sha `aeb13307…dae4`; the
   512-token pin reproduces, token-ids sha `cf6bcfee…`). Steps 1-3 clean.
2. `freeze_projection(pack)` REFUSES:
   `IdentityPinProjectionError: identity unit 'A/decode' config declaration differs from pack`
   at `joulewise/identity_pins.py:1452` (branch; main `:1380`).
3. Diff, declared vs observed (`_declared_identity_from_config`, `:1236`):
   `workload_profile.prompt_tokens` declared `42` / observed absent;
   `workload_profile.suite_manifest_ref` + `suite_manifest_sha256` declared
   absent / observed present (per-arm, per-prompt manifest path + sha).
   Source: the generator's decode config workload is built at
   `configs/campaigns/d117_contrast_v5/generate_configs.py:1862-1875`
   (`suite_manifest_ref`, `suite_manifest_sha256`, no `prompt_tokens`), while
   the projection's `declared_identity.workload_profile` is built at
   `:2570-2590` from `workload_for("decode")` (`:1305-1315`: `prompt_tokens:
   DECODE_PROMPT_TOKENS["A"]`). Both shapes entered in the SAME commit,
   `76c2dcc0` (#241, 2026-08-30).
4. Deeper: per unit — `A/decode` 20 configs, 8 distinct `suite_manifest_ref`,
   8 distinct `scientific_config_identity_sha256`, 8 distinct declared
   identities; same for `B/decode`; both prefill units 1/1/1. Decode blocks
   rotate prompts by `decode_prompt_index(block) = (block-1) % len(prompts)`
   (`:1373`). So even after a declared-identity patch, `_derive_projection_units`
   refuses with "multiple scientific config identities" (`:1461-1466`).
5. The v3 pack (`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/…/*decode*a1.json`)
   used ONE decode workload (`df_ph_decode`, `prompt_tokens: 128`, no
   manifests) — the shape D-131 was designed for. D-131 cl.2
   (`docs/decision_log.md` "## D-131", cl.2): "Every unit carries the same
   model/runtime/config triple used by the shared floor mint."
6. No test freezes a generated pack (`grep freeze_projection tests/test_d117_contrast_v5_pack.py`
   → none); `tests/test_identity_pins.py:134,246` derives the fixture's
   `declared_identity` FROM the config, so the fixture family cannot detect
   this class. Refuters 149/150/151/155/157/159 of projection-02 all ran on
   such fixtures.
7. The generator file is bench-editable subject to ONE invariant: the
   dominance-criterion registration digest
   `sha256(canonical_json_bytes(dominance_criterion_registration()))` =
   `1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`
   must be unchanged (`tests/test_d117_contrast_v5_pack.py` pins it — find
   the assertion). Frozen corpora and the v3 pack are immutable.

## Questions (answer all; cite file:line for every factual claim)

Q1. What IS the scientific identity of the `_v5` decode arm under the
    contract's own rules? Establish first, from the code, what
    `scientific_config_identity` (`identity_pins.py:~200-243`) keeps from
    `workload_profile`, what the shared floor mint's decode identity is for
    `_v5` (find the floor producer plan the unit references —
    `producer_plan_reference.path` `../d117_floor_qwen3-1p7b_v5/calibration_plan.json`;
    does it exist in the generated root? what decode workload does the floor
    declare — one prompt? `prompt_tokens: 42`?), and how D-165's dominance
    analysis / D-117 floor binding consume the decode floor (does the floor
    have to share the consumer's exact prompt, or only model/runtime/
    profile?). Then: does an 8-prompt rotating decode arm even have ONE
    identity that a per-arm floor can bind to?
Q2. Options for the fix — evaluate at least:
    (a) Manifest-set identity: the decode unit's declared and scientific
        identity carry the profile fields plus the SORTED SET of the 8
        manifest sha256s (or a set digest); `scientific_config_identity`
        projects `suite_manifest_ref/sha256` into that set form so all 20
        configs normalize to one identity. Per-run manifest binding stays a
        realization fact (like prompt_realizations for prefill).
    (b) Eight units per arm (`A/decode/p01`…): what breaks (D-131 cl.2's
        "exactly four ordered units", U8 readiness ordered unit IDs, floor
        producer references, receipt schema, gamma docs).
    (c) Generator declares what it writes: `declared_identity` built from
        the actual config, and the freeze rule relaxed to allow N scientific
        identities in a unit — say why this is or is not a quiet weakening of
        D-131 cl.3 "any pack-versus-config mismatch fails closed".
    (d) Anything better.
    For each: which files change, what the D-131 amendment text must say,
    whether the registration digest survives, and the regression that would
    have caught today's defect (mutation-cure rule: name the counterfactual
    input and the production call site).
Q3. The standing regression: specify a test in
    `tests/test_d117_contrast_v5_pack.py` that GENERATES a pack with the
    synthetic `write_prefill_pin` fixture and calls `freeze_projection` on
    it end-to-end (then `verify_frozen_projection`, and arm re-verification
    with a custody root as `tests/test_identity_pins.py:~1272` does). Is a
    synthetic pin enough to exercise the decode path? What does the test
    need to monkeypatch (tokenizer? model files? `_probe_live_environment`?)
    — read what `freeze_projection` reads from the filesystem beyond the
    pack (`_derive_projection_units`, model enumeration, stack identity).
Q4. Sequencing: this blocks any pack-bound night. Should the fix land on
    the projection-02 branch (unmerged, holds prompt_realizations) or as a
    separate branch after projection-02 merges? Cold-gate triggers that
    apply (a D-131 amendment is a process/contract change).

Magistrate's lean: (a), landed as a separate branch after projection-02
merges, with a D-131 cl.2 amendment ("one scientific identity per unit,
where a decode identity's workload is the profile plus the closed set of its
pinned prompt manifests"), plus the Q3 generated-pack freeze test as a
permanent CI regression. Disagree if warranted.

## Report

Envelope first (`claude-codex-report/v1`, genre `review`), then under 110
lines. Lead with your option and the one sentence a reviewer would need.
