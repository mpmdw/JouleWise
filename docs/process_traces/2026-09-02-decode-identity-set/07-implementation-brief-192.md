WRITE_SCOPE: ["configs/campaigns/d117_contrast_v5/generate_configs.py","joulewise/identity_pins.py","joulewise/analysis_engine/inputs.py","tests/test_d117_contrast_v5_pack.py","tests/test_identity_pins.py","tests/test_analysis_inputs.py","docs/contracts/identity_pin_projection.md"]
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: implementation

# FIX — decode-unit identity under prompt rotation (ruling 171a; D-131 cl.2/cl.3 amendment)

You are implementing a magistrate RULING, not a design. Where the ruling is
silent you may choose; where it speaks you follow it verbatim. If a ruled
clause cannot be implemented as written (a cited site does not exist, a
required input is unreachable from the call path), STOP that clause and
return early with a `NEEDS_RULING` flag naming the clause, the obstacle, and
two concrete options — do NOT improvise a semantics. Everything else in the
brief still gets done and reported.

Worktree: this linked worktree, branch `fix/2026-09-02-decode-identity-set`
off the PR #269 merge head. You cannot commit (linked worktree; the magistrate
commits). Never run `python -m unittest discover`; run named modules only.
`TMPDIR` is preset to a scratchpad subdir — keep every temp path under it.
NEVER edit `docs/process/state_kernel.json`, `docs/decision_log.md`, any
`runs*/`, `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/`, or any
file outside WRITE_SCOPE.

## Hard invariant (pinned; the run fails if it moves)

`sha256(canonical_json_bytes(dominance_criterion_registration()))` in
`configs/campaigns/d117_contrast_v5/generate_configs.py` must remain
`1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`
(pinned at `tests/test_d117_contrast_v5_pack.py` ~:966-971,
`tests/test_d165_dominance_closeout.py` ~:1616/1770, `tests/test_night_gate.py`
~:188). Run those three modules at the end and report.

## The defect (verified at the bench and by the cold gate)

Generated `_v5` decode units (`A/decode`, `B/decode`) hold 20 configs that
rotate over 8 prompt manifests (`suite_manifest_ref`/`suite_manifest_sha256`
per config; histogram 4/4/2/2/2/2/2/2), so they yield 8 distinct
`scientific_config_identity_sha256` values. `freeze_projection`
(`joulewise/identity_pins.py`) refuses twice: FIRST at the declaration-
equality check (the unit's `declared_identity` is re-typed from
`workload_for()` in `generate_configs.py` ~:1305-1315, ~:1862-1875,
~:2572-2588 with a hardcoded `DECODE_PROMPT_TOKENS["A"]` ~:1334, so it matches
0/20 emitted decode configs), SECOND at the multiplicity check (one identity
per unit). Prefill units (`prefill_p512`, one member) are fine. Locate the
exact current lines yourself (`grep -n`); the numbers above are from main
before #269 and may have shifted.

## Rulings to implement (R-1..R-8 of ruling 171a)

R-1 Exact identities stay exact. Do NOT redefine `scientific_config_identity`.
Do NOT touch replacement matching (`inputs.py` ~:2911-2950), NEG-8, the bundle
mint, the mint producer-pin compare, `_source_regime`, `bind_floor_artifact_evidence`,
or `detection_floor.py`. Do NOT add any new key to `RECEIPT_UNIT_FIELDS` or
`MODEL_RUNTIME_CONFIG_FIELDS` (exact-key validated; committed receipts must
keep loading).

R-2 Declared closed set, from the RULE, never folded. The generator declares,
per decode unit, inside `declared_identity.workload_profile` (a free mapping):
`suite_manifest_set` = the ORDERED list of
`{"suite_manifest_ref": <ref>, "suite_manifest_sha256": <effective sha>,
"declared_member_count": <int>}` computed from the pre-registered rotation
rule (decode prompt index = (block − 1) mod 8 over the block schedule — find
the registered rule in the generator and USE it; do not re-derive from emitted
configs), plus the common profile = the workload fields shared by every member
(the config workload minus `suite_manifest_ref`/`suite_manifest_sha256`).
The generator must NOT build the declaration by reading the configs it just
emitted, and must NOT re-type it from `workload_for()`; remove the hardcoded
`DECODE_PROMPT_TOKENS["A"]` use from the declaration path. Prefill units:
single-member declaration, unchanged shape except that a one-element
`suite_manifest_set` is acceptable if it simplifies the code (state which you
chose).

R-3 Freeze compares declaration to emission, fail-closed. In
`freeze_projection` (and mirrored in `verify_frozen_projection` where the
same comparison is re-run), per unit: (i) project each config's workload to
the common profile and require equality with the declared common profile;
(ii) require each config's manifest sha to be a declared member; (iii) require
every declared member to be emitted with EXACTLY its declared count; (iv)
refuse any extra, missing, duplicate, or unauthenticated (sha not matching the
manifest bytes on disk, if the code already authenticates manifests — check)
member. Refusal reasons use the existing refusal vocabulary style in the
contract §7; add new reason tokens only if none fits, and document them.

R-4 One identity per manifest class. Within a unit, members binding the same
manifest sha must share ONE `scientific_config_identity`; the number of
distinct member identities must EQUAL the number of declared manifests. A
drifted tag/note on any member therefore still refuses.

R-5 Unit config-set digest; no new key. The unit's `config_set_sha256`
becomes: one distinct member identity → that identity hash (byte-identical
to today for every committed receipt and the shared-mint producer pin);
several → `SHA256("joulewise.identity_unit_config_set.v1" ‖ "\n" ‖
"\n".join(sorted(distinct member scientific hashes)))` (hex digest of that
UTF-8 byte string, exactly this construction). Replace the
representative-config triple (`configs[0]` / `typed_configs[0]` used for the
unit's identity, ~`identity_pins.py:1467-1468, 1614`) so that no unit-level
value depends on set-iteration order; the representative may still be used
for `_runtime_probe_metadata` if all members share runtime pins (assert that
they do; refuse otherwise).

R-6(a) Analysis gate. `joulewise/analysis_engine/inputs.py` ~:3881
(`if len(consumer_identities) != 1: return None`): consumer evidence
identities must be NON-EMPTY and a SUBSET of the frozen consumer unit's
declared set; any identity outside the set → return None (refuse); the
exact-cell route (~:3905-3916) stays single-identity-only (if the evidence
carries several identities, only the condition-family transport route may
bind). The declared set is to be read from the FROZEN RECEIPT bound by the U8
readiness record. INVESTIGATE how that receipt (or the frozen unit's member
identity hashes) is reachable from this function's call path
(`contrast`, `artifact`, evidence rows' metadata, the analysis manifest). If it
is reachable, implement. If it is NOT reachable without a new plumbing
decision, return `NEEDS_RULING` for R-6(a) ONLY with the two cheapest concrete
plumbing options (file:line for each), and leave `:3881` unchanged — the rest
of the fix still lands.

R-6(b) Floor sites: UNCHANGED (the `_v5` floor units are ruled single-manifest).
Add ONE test that a single-identity unit's `config_set_sha256` is
byte-identical to a committed v3 receipt value (read
`configs/campaigns/d117_floor_qwen25_1p5b_v3/identity_pin_projection.receipts/projection-0001.json`
or the contrast v3 receipt; assert the code path reproduces that hash for a
single-identity set).

R-8 Regression, RED FIRST. In `tests/test_d117_contrast_v5_pack.py` add a
generated-pack freeze + `verify_frozen_projection` PASS test built the way
the existing pack tests build packs (temp git repo, `write_prefill_pin`,
module-level model-artifact fake, a realistic `_runtime_probe_metadata` stub,
`_mint_git_anchor` patched — look at the existing tests in that file and at
`tests/test_identity_pins.py` ~:134/:246 for the fixture idiom). Each
counterfactual is its OWN test method, named for what it refuses:
(i) `test_generated_v5_pack_freezes_and_verifies` — the current generator's
    GAMMA output freezes and verifies (this is the RED test: it must FAIL on
    the pre-fix code at the declaration check, PASS after);
(ii) one decode member re-pointed to an unlisted manifest → REFUSE;
(iii) declared census count off by one → REFUSE;
(iv) declaration re-typed from `workload_for()` (the old code path, reproduced
     in the test) → REFUSE at the declaration check specifically (assert the
     reason token);
(v) one member with a drifted tag → REFUSE (R-4);
(vi) single-identity `config_set_sha256` byte-identical to the v3 receipt
     value (R-6(b) test above may live here or in test_identity_pins).
In `tests/test_identity_pins.py` add unit tests for the set digest (two known
hashes → the expected hex, computed by hand in the test) and for the
common-profile projection.

Contract: update `docs/contracts/identity_pin_projection.md` (§2 vocabulary,
§6 freeze, §7 receipt schema, §10 tests) so a reader can REPLICATE the set
digest and the freeze comparison from the text alone: define every term at
first use, give the domain string verbatim, and extend the §8 worked example
with a two-manifest decode unit (real hex digests you compute, clearly
labelled as example values). Writing standard: no term does unpaid work; a
reader must be able to rebuild the mechanism.

## Deliverable layout (so the magistrate can commit RED then CURE)

Keep test additions and production changes in separate files as they are;
the magistrate will stage `tests/` first, run (i) to confirm it is red, commit,
then stage the cure. Therefore (i) must fail on the pre-fix code for the
RIGHT reason (declaration check), and every other test module you touch must
still IMPORT cleanly against the pre-fix code (guard any new symbol import
with the pattern already used in the repo, or place the set-digest unit tests
after the pack tests so that only the intended assertions fail).

## Verification you must run and report (verbatim tails)

- `python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_identity_pins tests.test_analysis_inputs tests.test_mlx_runtime`
- `python3 -m unittest tests.test_d165_dominance_closeout tests.test_night_gate` (digest pins)
- the generator's own regeneration into a temp root (find its CLI in the file
  header / existing tests) for GAMMA and, if the ALPHA/BETA floor plans are
  generated by the same script, for those too; then `freeze_projection` +
  `verify_frozen_projection` on each generated root under TMPDIR; report the
  per-unit member counts, distinct-identity counts, and `config_set_sha256`.
- `git diff --stat` and confirm nothing outside WRITE_SCOPE is dirty.

FINAL message = `claude-codex-report/v1` envelope (genre implementation) with
`verification` entries for each command above, `flags` for any NEEDS_RULING,
followed by a prose "Change" section listing every ruled clause R-1..R-8 with
CONFIRMED (file:line) or NOT DONE (why).
