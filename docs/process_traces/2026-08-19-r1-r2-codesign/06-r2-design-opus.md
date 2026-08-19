# R2 — Mint-lane fan-out shape (pack identity) — OPUS INDEPENDENT DESIGN SEAT

Read-only design at `integration/phase2-transaction` @ `9f7f091`, worktree
`scratchpad/wtTXN`. Every load-bearing claim below is cited to `file:line` I
opened myself, or to a command I ran myself in that tree. Nothing was written
into the repo.

---

## 0. Executive summary of the decision

**Do both, in one transaction, in this order: generation-index the mint lane's
screen/rule, then mint a `_v3` pack family bound to r4.**

The brief poses generation-indexing and the `_v3` family as competing options.
They are not alternatives — they are two different layers, and each one alone
is provably insufficient:

- **Generation-indexing alone** leaves the three claim-bearing packs frozen on
  acceptance `…_n19_r2`, whose bracket screen `0.010818` was derived from a
  corpus that *included* the contaminated member `20260722T222332-901c5c13`
  (the old maximum, 33.559 ms) that anchor-v3 refuses
  (`03-cold-science-review.md:69-74`). No pack at r4 would exist.
- **A `_v3` family alone** cannot work, because the kernel validators can only
  admit one screen at a time. Emitting a `_v3` pack whose spec carries
  `max(observed_drift_s,0.009724)` while `floor_mint_estimator._ALLOWANCE_RULE`
  still equals `max(observed_drift_s,0.010818)` refuses at
  `joulewise/floor_mint_estimator.py:166` — I executed that refusal (§(d)).
  Flipping the constant instead *is* the refuted flat migration.

I also found three facts that settle the pack-identity question without
appealing to preference at all — all three are executed or byte-verified:

1. **The `_v2` generator mechanically refuses in-place regeneration.**
   `python3 configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py --check`
   exits `generation failed: the current frozen identity requires preserve mode`
   (guard at `generate_configs.py:270-275`). "Regenerate the `_v2` packs" is not
   a design option that the committed tooling permits.
2. **A `_v3` pack emits correctly today with zero code changes.** I ran the
   `_v2` generator with `--pack-id d117_floor_qwen25_1p5b_v3 --family-suffix _v3
   --output-root <tmp>`: it produced 100 science configs, the pack tree, and
   `configs/floor_mint/d117_qwen25_1p5b_v3_extraction_spec.json`, status
   `unfrozen draft`. It bound **r2**, which is the one substantive generator
   edit the design needs.
3. **Regenerating `_v2` would break the freeze chain a successor needs.**
   `_authenticate_freeze_predecessor` recomputes the predecessor's *committed*
   pack-tree digest and refuses on divergence
   (`joulewise/arm_readiness.py:5028-5037`). The `_v2` bytes must stay exactly
   as committed for any later member to chain to them.

And the parked plan's step 6 — "freeze-0002 re-mints" — should be **replaced by
freeze-0003 mints on the new `_v3` roots**. The committed freeze-0002 receipts
stay untouched as the historical attestation of the `_v2` family at head
`54f990d1` (`configs/campaigns/d117_floor_qwen25_1p5b_v2/arm_readiness.evidence/evidence-multicell-mint.json`
records `head_commit 54f990d156eee3da3467b368b816d4ac4a50f806`).

---

## (a) The decision, as a ratifiable spec

**R2-SPEC-1 — The screen is generation-resolved, never copied.**
No module, script, schema, or generator in the mint lane may carry a literal
bracket-screen scalar or a screen-substituted allowance-rule string. Every such
site resolves the pair from the **acceptance generation the artifact under
validation itself names** (`acceptance_id`), through a single public accessor
whose ONE home is `joulewise/calibration_bracketing.py` (where the D-102
corpus-indexed derivation table already lives at
`calibration_bracketing.py:155-188`). An unregistered `acceptance_id` is a
refusal, never a default.

New public API in `joulewise/calibration_bracketing.py` (adjacent to
`_D102_GENERATION_DERIVATIONS` at `:179-186`):

```python
def acceptance_generation_operatives(acceptance_id: str) -> Mapping[str, str] | None
def acceptance_bracket_screen_s(acceptance_id: str)     -> str | None
def acceptance_allowance_rule(acceptance_id: str)       -> str | None
    # returns f"max(observed_drift_s,{bracket_screen_s})", or None
```

The rendering convention is fixed and reproduces every historical string
exactly: `n19 → "max(observed_drift_s,0.010818)"`,
`n17_r3/n17_r4 → "max(observed_drift_s,0.009724)"`. It is identical to the
rendering the mint tool already performs from artifact bytes at
`scripts/mint_floor_artifact_generalized.py:2200-2202` — which is exactly why
the two disagreed and produced the 33 reds (§(f)).

**R2-SPEC-2 — Pack generations are minted, never rewritten.**
A pack identity `d117_*_v<N>` that carries a D-134 freeze receipt is immutable.
Binding a different acceptance generation, or landing any edit to a source file
recorded in its freeze evidence, produces the successor member `_v<N+1>` with a
`predecessor` lineage binding — not a regeneration. R2 therefore mints
`d117_floor_qwen25_1p5b_v3`, `d117_floor_qwen25_7b_v3`,
`d117_contrast_qwen25_1p5b_vs_7b_v3`, each bound to
`d079_calibration_acceptance_v2_n17_r4`, each chaining `freeze-0003 →
freeze-0002`.

**R2-SPEC-3 — `_ACCEPTANCE_SELECTION` does not move.**
`floor_mint_estimator.py:42` stays `"issued_d116_artifact_only"`; every emitted
spec keeps `"acceptance_selection": "issued_d116_artifact_only"`. It is a
*role* selector ("only an issued artifact, never a fixture") checked at
`floor_mint_estimator.py:165` and `arm_readiness_evidence.py:934`, orthogonal to
the generation axis. (Observation for the record, not a change: the literal's
name reads like a pin to the D-116 *generation*, which it is not. Renaming it
is a separate, independent-axis decision.)

**R2-SPEC-4 — One transaction.**
Kernel edits, schema edit, generator retarget, `_v3` emission, golden
re-derivation, evidence re-author, freeze-0003 mints, and doc/test pins land as
ONE commit series with canonical FULL GREEN as the exit gate. No partial
adoption (cold-science-review condition 6,
`03-cold-science-review.md:112-114`).

---

## (b) Pack-identity semantics

**A pack identity is the tuple** (pack tree bytes, plan + sidecar, extraction
spec, bound acceptance generation, evidence set, freeze receipt). Concretely,
that tuple is what `freeze-000N.pack_identity` + `.predecessor` binds
(`configs/campaigns/d117_floor_qwen25_1p5b_v2/arm_readiness.freeze.receipts/freeze-0002.json`:
`pack_identity{pack_id, pack_root, plan_id, plan_path, plan_sha256, window_id}`,
`predecessor{pack_id, pack_path, pack_sha256, plan_sha256, evidence_set_sha256,
freeze_receipt{receipt_id,path,sha256}, identity_receipt, pack_digest_algorithm}`).

**What is frozen.** Once `freeze-000N.json` exists with `status: PASS`, the
pack's committed tree digest is load-bearing for every later member:
`_authenticate_freeze_predecessor` recomputes `committed_pack_tree_sha256`
(`arm_readiness.py:2553`, algorithm id `joulewise.committed_pack_tree_sha256.v1`
at `:42`) and refuses on any divergence (`:5028-5037`), and it refuses unless
the predecessor receipt recorded `PASS` (`:5048-5050`).

**What supersedes.** The newest family member admitted by `_plan_profile`
becomes the live pack for its profile. `_PROFILE_BY_PACK`
(`arm_readiness.py:255-259`) is the *immutable historical* v1 mapping; anything
later is admitted by `_SUCCESSOR_PROFILE_PATTERNS` (`:260-266`), whose regexes
are `^d117_floor_qwen25_1p5b_v(?:[2-9]|[1-9][0-9]+)$` and siblings — i.e. **`_v3`
is already admitted, no code allowlist edit required.** Predecessor members stay
verifiable forever; nothing is deleted.

**What carries lineage.** `freeze-0003.predecessor` binds the `_v2` pack and its
`freeze-0002`, and the ordinal is checked to be exactly predecessor + 1
(`arm_readiness.py:2194-2201`, via `_freeze_receipt_ordinal` at `:1266-1280`).
The generational machinery was explicitly designed to generalise past `_v2`:
`_pack_generation`'s docstring says so verbatim — *"This generalizes to
arbitrary `_v<N>`, not only the v2 family the D-139 consult licensed… nothing is
unlocked by parsing a higher generation"* (`arm_readiness.py:1283-1295`).

**Acceptance generations are a parallel immutable chain**, not the same axis.
`ISSUED_ACCEPTANCE_REGISTRY` (`calibration_bracketing.py:109-134`) holds all
four issued generations; `_acceptance_bound_from_authenticated_bytes` selects
the expected digest *by the document's own `acceptance_id`* so "a caller cannot
present one issued generation's bytes under another generation's pin"
(`:621-636`). A pack binds exactly one. The observed pairing is
`_v1 ↔ n19`, `_v2 ↔ n19_r2`, `_v3 ↔ n17_r4` — I verified `_v1` and `_v2`
directly from the committed specs (`configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json`
`cells[0].calibration_basis.issued_acceptance.acceptance_id = d079_calibration_acceptance_v2_n19`;
the `_v2` spec `= …_n19_r2`). Note the pairing is not a bijection: r3 is a
retained intermediate acceptance generation with no pack, which is fine and
already contemplated (`calibration_bracketing.py:96-98`).

**The precedent is decisive and it is the packs' own committed policy text.**
The `_v1` spec says a successor acceptance "REQUIRES pack regeneration (packs
are unfrozen drafts)". The `_v2` spec says a successor acceptance "**REQUIRES a
newly generated pack**; the committed D-134 freeze receipt and its plan-tree
attachment are authoritative for this pack's freeze state"
(`successor_acceptance_artifact_policy` in
`configs/floor_mint/d117_qwen25_1p5b_v2_extraction_spec.json`; source strings at
`configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py:480-490`,
selected by `successor_regeneration_rule()` at `:493-505`). The policy changed
*precisely because* the `_v2` family became frozen. And the `_v2` family itself
was minted for a **science-neutral** acceptance reissue (r2 changed no physical
value — `calibration_bracketing.py:63-67`). If a science-neutral reissue earned
a new family, a science-changing one (new corpus n=17, new screen, new
preflight comparator) cannot earn less.

---

## (c) Enumerated touch points (all verified in the tree)

### C1 — Kernel: the ONE home for the mapping

| Site | Current | Change |
|---|---|---|
| `joulewise/calibration_bracketing.py:155-188` | `_D102_N19_DERIVATION`, `_D102_N17_DERIVATION`, `_D102_GENERATION_DERIVATIONS` | **unchanged.** Add the three public accessors of R2-SPEC-1 beneath `:188`. |
| `joulewise/calibration_bracketing.py:138-140` | `DEFAULT_ACCEPTANCE_BOUND_SHA256 = 9a264c57…` | rename only (see §(f) incidentals) |

`_D102_N19_DERIVATION.operatives.bracket_screen_s = "0.010818"` (`:161`) and
`_D102_N17_DERIVATION.operatives.bracket_screen_s = "0.009724"` (`:173`) already
exist and are already routed for r3/r4 (`:182-185`). **The generation table
needed by R2 is already built and already correct.** R2 only extends its reach
one layer down.

### C2 — Kernel: `joulewise/floor_mint_estimator.py`

- `:39` `_BRACKET_SCREEN = Decimal("0.010818")` → **delete**
- `:40` `_ALLOWANCE_RULE = "max(observed_drift_s,0.010818)"` → **delete**
- `:42` `_ACCEPTANCE_SELECTION` → **untouched** (hard constraint)
- `:124-205` `_validate_calibration_basis(...)` → resolve
  `screen`/`rule` from `calibration_acceptance["acceptance_id"]` at the top;
  raise `_MintEstimatorError("unregistered acceptance generation …")` if the id
  is not in the registry.
- `:166` `basis.get("allowance_rule") != _ALLOWANCE_RULE` → compare to the
  resolved rule.
- `:192-195` `screen != _BRACKET_SCREEN` / `applied != max(observed, _BRACKET_SCREEN)`
  / projection `allowance_rule != _ALLOWANCE_RULE` → resolved.
- `:204` the refusal message hardcodes `max(observed_drift_s,0.010818)` → render
  the resolved rule into the message.

Import safety verified: `detection_floor → whole_window → calibration_bracketing`
is an existing edge (`joulewise/whole_window.py:52`), and
`calibration_bracketing` imports none of them
(`calibration_bracketing.py:18-41`). I imported both modules together and
confirmed no cycle.

### C3 — Kernel: `joulewise/detection_floor.py` (the claim-side v2 pinset reader)

- `:2446-2448` `post.get("allowance_rule") != "max(observed_drift_s,0.010818)"`
  and `post.get("bracket_screen_s") != "0.010818"` → resolved from
  `acceptance["acceptance_id"]`, which is already in scope in the same producer
  loop (bound at `:2331`, shape-validated at `:2342-2348`).
- `:2491` `applied_allowance != max(observed_drift, Decimal("0.010818"))` →
  resolved.
- **Untouched** (already generation-neutral, symbolic form): `:517`, `:641`
  `"max(observed_drift_s,bracket_screen_s)"`.
- `_V2_POSTCOLLECTION_KEYS` (`:2112-2124`) and `_V2_ACCEPTANCE_KEYS` (`:2095-2097`)
  unchanged — the shape already carries everything needed. Note
  `derivation_rule_id` is the acceptance *schema_version*, identical across r2
  and r4, so `acceptance_id` is the only discriminator.

### C4 — Kernel: `scripts/mint_floor_artifact_generalized.py`

- `:64` `V2_ALLOWANCE_RULE`, `:65` `V2_BRACKET_SCREEN_S` → replace with
  `allowance_rule_for(acceptance_id)` / `bracket_screen_s_for(acceptance_id)`
  thin wrappers over the `calibration_bracketing` accessors (already imported
  from that module at `:47-51`).
- `:570` `_parse_v2_postcollection(value, label)` → add keyword `acceptance_id`;
  the sole caller at `:889-891` already has `acceptance["acceptance_id"]` in
  scope (bound at `:777-786`).
- `:619-625`, `:639` the three comparisons → resolved.
- `:2173-2203` `_v2_allowance_projection` → **unchanged**; it already derives
  both screen and rule from the authenticated artifact
  (`issued_calibration_allowance_projection` at
  `calibration_bracketing.py:642-690`, rule rendered at `:2200-2202`).

### C5 — Contract schema: `scripts/floor_mint_pinsets/schema_v2.json`

- `$defs.allowanceContract` (`:180-198`) — `const` at `:190`, `:193`
- `$defs.finalPostcollection` (`:400-…`) — `const` at `:461`, `:468`

Replace each `const` with an `enum` of the registered generations' values, and
add an `allOf`/`if`/`then` at `$defs.finalProducer` (`:634`) and
`$defs.pinRequirements` (`:858`) binding
`calibration_acceptance.acceptance_id` to the matching pair. `finalProducer`
already has `calibration_acceptance` and `cells` as siblings, so the conditional
is expressible without restructuring. The schema is a contract artifact (not a
runtime validator — the mint has its own `_parse_v2_*`), but it is byte-pinned
into MULTICELL_MINT evidence (`joulewise/arm_readiness_evidence.py:1300`) and is
skipped by the pinset scan (`detection_floor.py:2662`), so it must move in the
same transaction.

### C6 — The three `_v2` pack generators

These are the three campaign generators (I verified there is no other triple in
the tree; see §(h) disagreement 3):

| Generator | Sites |
|---|---|
| `configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py` | `:143-152` `SUCCESSOR_ACCEPTANCE_{REL,SHA256,DERIVATION_SHA256,ID}` → r4; `:1397` `"allowance_rule": "max(observed_drift_s,0.010818)"` → derived from `acceptance_pin()` |
| `configs/campaigns/d117_floor_qwen25_7b_v2/generate_configs.py` | `:200-208` same block → r4; `:928` same literal |
| `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py` | `:348-357` `SUCCESSOR_ACCEPTANCE` dict → r4. No allowance literal (contrast packs carry no floor mint; acceptance policy emitted at `:1721-1725`) |

**Regression safety proven:** these edits cannot disturb the frozen `_v2` bytes.
In preserve mode `_generate` copies the committed bytes verbatim and never calls
`calibration_basis()` or `acceptance_pin()`
(`d117_floor_qwen25_1p5b_v2/generate_configs.py:1940-1945`). I ran
`--check --preserve-current-frozen-bytes` and it verified:
`verified d117_floor_qwen25_1p5b_v2 frozen by d134 receipt: 100 science configs`.
The `_v1` generators need no edit at all (`_v1 --check` verified clean).

The retargeted `SUCCESSOR_ACCEPTANCE_*` constants are carried into the emitted
`_v3` generator verbatim by `embedded_generator_bytes()` (`:381-391`), which
rewrites only the family-suffix declaration and the allowlisted identity tokens
(`_SUCCESSOR_IDENTITY_TOKENS`, `:305-330`) — the acceptance ids are deliberately
not in that allowlist, so they pass through unmangled.

### C7 — Emitted `_v3` artifacts (new, not edits)

- `configs/campaigns/d117_floor_qwen25_1p5b_v3/**` (100 science configs + plan,
  sidecar, plan_tree, producer_contract, order manifests, condition families,
  README, embedded `generate_configs.py`)
- `configs/campaigns/d117_floor_qwen25_7b_v3/**`
- `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/**`
- `configs/floor_mint/d117_qwen25_1p5b_v3_extraction_spec.json`
- `configs/floor_mint/d117_qwen25_7b_v3_extraction_spec.json`
- per-pack `arm_readiness.sources/`, `arm_readiness.evidence/`,
  `identity_pin_projection.receipts/`,
  `arm_readiness.freeze.receipts/freeze-0003.json{,.sha256}`

I confirmed the emission path end-to-end by running it to a temp root; the
`_v3` spec came out with `draft_status: as_generated_pre_d134_freeze` and the
freeze-neutral successor policy text.

### C8 — Evidence author

- `joulewise/arm_readiness_evidence.py:884-965` `_derive_acceptance_owner` —
  **no edit needed**: it resolves the artifact through
  `_ISSUED_ACCEPTANCE_REGISTRY` by the pack's declared `issued_artifact_id`
  (`:892-900`) and copies the screen out of the loaded artifact (`:915-917`).
  r4 is already registered.
- `joulewise/arm_readiness_evidence.py:1287-1310` `_derive_multicell_mint` —
  **no edit needed**, but note it *runs* three of the currently-red mint tests
  (`:1289-1296`) and byte-pins `schema_v2.json`,
  `mint_floor_artifact_generalized.py`, `floor_mint_estimator.py`,
  `test_mint_floor_artifact_generalized.py` (`:1299-1305`). This is the hard
  sequencing constraint: **evidence cannot be authored until the 33 mint reds
  are green**, and every C2–C5 edit changes a digest this receipt pins.
- `tests/test_arm_readiness_evidence_author.py:120-125` acceptance copy-list —
  **must add r3 and r4** (see §(f)).

### C9 — Test pins and goldens behind the 33 reds

Confirmed at `9f7f091`: `python3 -m unittest tests.test_mint_floor_artifact_generalized`
→ **`Ran 75 tests … FAILED (failures=11, errors=22, skipped=2)`** = exactly the
33 mint-lane reds, and the module runs in 7.6 s (cheap iteration loop).

- `tests/test_mint_floor_artifact_generalized.py:1276-1298` — the independent
  golden block: `SYNTHETIC_COMPONENT_SHA256S`, `SYNTHETIC_PRODUCER_PIN_SHA256S`,
  `SYNTHETIC_PRODUCER_SET_SHA256`, `CLI_COMPONENT_SHA256S`. Its own comment
  (`:1281-1287`) states these "move with a D-079 issuance. Re-derived for the
  D-138 detection-budget reissue … with the independent fixture oracle
  `_fixture_canonical_sha256`, never with the mint code under test." R2 repeats
  that documented procedure for r4.
- `tests/test_mint_floor_artifact_generalized.py:834-836`, `:1228`, `:1353`,
  `:2729`, `:5075`, `:5208`, `:6032-6033`, `:8749`, `:9465-9467` — fixtures that
  reference `generalized.V2_ALLOWANCE_RULE` / `V2_BRACKET_SCREEN_S`
  *symbolically*. These follow the kernel automatically once the constants
  become resolvers; only the call shape changes.
- `tests/test_mint_floor_artifact_generalized.py:1363`, `:1369`, `:9092` —
  hardcoded `0.010818` / `"0.0108180"` literals; must become generation-derived
  or be explicitly re-labelled as n19-era fixtures.
- `tests/test_floor_mint_estimator.py:29-58` — **this is the n=19 estimator
  replay** (§(d)). Stays byte-identical.
- `tests/test_detection_floor.py:709,722`; `tests/test_floor_extraction.py:2565,2570`;
  `tests/test_whole_window_selection.py:2428`;
  `tests/test_calibration_bracketing.py:1656,1750,1818`;
  `tests/test_d117_floor_qwen25_1p5b_plan.py:1408,1434-1436`;
  `tests/test_d117_floor_qwen25_7b_plan.py:1319-1321` — all n19-era pins against
  `_v1`-generation artifacts. **All stay unchanged**; that is the replay-integrity
  requirement, and generation-indexing is what makes it satisfiable.
- **Missing coverage to add:** there is no test module for the `_v2` packs at
  all (the three plan-test modules target `_v1`:
  `test_d117_floor_qwen25_1p5b_plan.py:26`, `test_d117_floor_qwen25_7b_plan.py:38`,
  `test_d117_decode_contrast_plan.py:28`), and no test exercises the `_v2`
  generator emitting `_v3` (the successor tests at
  `test_d117_floor_qwen25_7b_plan.py:546-628` exercise `_v1 → _v2`). See §(f).

---

## (d) Replay integrity — the argument, and the executed proof

The n=19 estimator replay is `tests/test_floor_mint_estimator.py`. Its fixture
(`:29-58`) constructs a synthetic n19-generation `calibration_basis` carrying
`"allowance_rule": "max(observed_drift_s,0.010818)"` and
`"acceptance_id": "d079_calibration_acceptance_v2_n19"`, and passes it to
`estimator.selection_from_authenticated_spec` with a **stub** acceptance mapping
that contains only `acceptance_id`, `derivation_sha256`, `schema_version` —
no `decimal_derivation`.

I ran three experiments in `wtTXN`:

| Experiment | Result |
|---|---|
| Baseline `tests.test_floor_mint_estimator` at `9f7f091` | `Ran 37 tests … OK` |
| **Flat migration simulated** (`_BRACKET_SCREEN=0.009724`, `_ALLOWANCE_RULE` flipped) | **`FAILED (failures=8, errors=49)`** |
| **Generation-indexed simulated** (resolve screen+rule from `_D102_GENERATION_DERIVATIONS[acceptance_id]`) | **`Ran 37 tests … OK` (0 failures, 0 errors)`** |

So the brief's executed refutation reproduces independently, and the proposed
shape survives it. The mechanism is exact: the historical basis names generation
`n19`; the resolver returns `0.010818` for `n19`; the rendered rule is
byte-identical to the committed lexeme; every `_v1`- and `_v2`-era spec, pinset,
and fixture continues to authenticate against the same bytes it always did.

I also confirmed the other direction — that current code is genuinely the
blocker for r4:

```
CURRENT CODE, r4 basis         -> REFUSED: authenticated spec calibration_basis policy literals are not canonical
GEN-INDEXED (r4 resolved)      -> default            # accepted
```

**Why resolve from the code-side registry rather than from the artifact's own
`decimal_derivation.ratified_operatives`?** Three reasons, one of them executed:

1. **Executed:** the historical fixtures pass stub acceptance mappings with no
   `decimal_derivation` (`tests/test_floor_mint_estimator.py:38-42`).
   Artifact-sourcing breaks them; registry-sourcing keeps 37/37.
2. **Fail-closed:** an unregistered `acceptance_id` yields `None` → refusal.
   Artifact-sourcing would silently adopt whatever screen a well-formed but
   unregistered document declared.
3. **No divergence risk:** `_valid_acceptance_bound` already requires the
   artifact's `rounding.operative_bracket_screen.value_s` and
   `ratified_operatives` to equal the registry's generation entry
   (`calibration_bracketing.py:550-559`), and re-derives the screen from the
   member table (`:567-580`). Registry and artifact cannot disagree on an
   authenticated document.

**The house precedent.** This is not a new invention. The preflight comparator
already works exactly this way one layer up:
`scripts/validate_powermetrics_fiducial.py:301-371` derives
`PREFLIGHT_SYSTEMATIC_SCREEN_S` from the authenticated acceptance instead of
copying it (`:376-380`), and there is a dedicated guard test forbidding a copied
scalar in the writer —
`tests/test_powermetrics_fiducial.py:1609-1624` asserts the source does **not**
contain `PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")` **or**
`… Decimal("0.032898493715362")`. R2 applies the ratified pattern to the last
surface in the mint lane that still copies.

---

## (e) Tooling plan

**No new acceptance-derivation tooling is required, and the D-079 reissue tool
is not in R2's path at all.** r4 is already issued and registered
(`configs/calibration/calibration_acceptance_d079_v2_n17_r4.json`, sha
`dcb3d3ed…` — I verified the file digest matches
`ANCHOR_V3_R4_ACCEPTANCE_BOUND_SHA256` at `calibration_bracketing.py:103-105`).
R2 mints no acceptance generation, so the reissue tool's scalar-comparison
limitation never binds. This is a real simplification relative to the brief's
framing (see §(h) disagreement 4).

What R2 needs, all of it existing:

1. **Generation resolver** — new code, ~15 lines, in `calibration_bracketing.py`
   (R2-SPEC-1). This *is* the design; it is not tooling.
2. **Pack emission** — the committed generators, already capable:
   `python3 configs/campaigns/<pack>_v2/generate_configs.py --pack-id <pack>_v3
   --family-suffix _v3`. Executed today; produces the full tree plus the
   external `_v3` extraction spec (`generated_relative_path`/`extraction_spec_rel`,
   `generate_configs.py:393-413`). Write-boundary and symlink guards run
   pre-write (`:1938-1939`).
3. **Pack self-check** — `… --check` on each `_v3` root after emission; and
   `… --check --preserve-current-frozen-bytes` on each `_v2` root as a
   regression assertion that the frozen family is untouched.
4. **Golden re-derivation** — the module's own independent oracle
   `_fixture_canonical_sha256`
   (`tests/test_mint_floor_artifact_generalized.py:848-857`), driven from a
   throwaway scratchpad script, values pasted into `:1276-1298` under review.
   **Deliberately not a tracked regeneration tool**: the block's comment
   mandates "regenerated only by an explicit fixture-review step, never by the
   mint implementation under test" (`:1276-1277`), and a tracked `--write-goldens`
   flag would erode exactly that.
5. **Evidence author** — existing `scripts/author_arm_readiness_evidence.py`,
   run per pack at the measurement checkout.
6. **Freeze** — existing lifecycle; `freeze-0003` with `predecessor` → the `_v2`
   pack + its `freeze-0002` (ordinal check at `arm_readiness.py:2198`).
7. **New guard test (recommended)** — mirror
   `test_writer_has_no_copied_preflight_scalar_and_comparison_is_derived`: assert
   that `joulewise/floor_mint_estimator.py`, `joulewise/detection_floor.py`,
   `scripts/mint_floor_artifact_generalized.py`, and the three generators
   contain **no** `0.010818` or `0.009724` literal. This is what stops the next
   generation from reproducing this exact fan-out.

**Not needed:** an R1 row-registry install. The committed registry is
`joulewise.arm_readiness_row_registry.v1`
(`configs/arm_readiness/d117_row_registry_v1.json`), not the
`R1_ROW_REGISTRY_SCHEMA = joulewise.arm_readiness_row_registry.v2`
(`arm_readiness.py:45`) that would gate `_plan_profile` on
`successor_pack_ids`. `_v3` is admitted by the shape-only route
(`arm_readiness.py:2717-2725`) with the existing patterns. **Interaction to
record:** if the R1 *row registry* install (a distinct item from R1 the
capture-flip ruling) lands before the `_v3` freeze, it MUST install
`successor_pack_ids = {ALPHA: …_1p5b_v3, BETA: …_7b_v3, GAMMA: …_contrast_…_v3}`
or `_plan_profile` refuses with `readiness_row_registry_mismatch` (`:2713-2716`).

---

## (f) Test fan-out plan to FULL GREEN

**Measured starting point** (all my own runs at `9f7f091`, and the canonical log
at `bb81323` at
`/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-…/scratchpad/final-full.log`):

| Bucket | Count | Owner |
|---|---|---|
| `test_mint_floor_artifact_generalized` (11 F + 22 E) | **33** | **R2** |
| `test_arm_readiness_evidence_author.test_authored_evidence_makes_synthetic_pack_freeze_pass` (author rc=2) | 1 | strict downstream of R2 |
| `test_authentication_io` ×2 (`ISSUED_REDUCE_SHA256` drift; 5 `reduce.py` direct reads) | 2 | anchor-v3 capture arc / R1 lane |
| `test_docs_freshness.test_current_sections_do_not_copy_volatile_literals` (README says "3,688 tests") | 1 | bookkeeping |
| `test_whole_window_selection.test_d079_real_selector_to_real_reducer_embeds_allowance_once` (`calibration_ledger_custody_invalid`) | 1 | R1 |
| **Total at bb81323** | **38** (16 F / 22 E) | |

**Simulation of the fan-out.** I patched the mint tool's two constants and the
estimator's two constants to their r4 resolutions and re-ran the module:
`R4-RESOLVED MINT LANE: run=75 failures=10 errors=22`. So the *scalar* half of
the change alone barely moves the count — the residual is dominated by two
things visible in the errors:

- `aggregate/component hash mismatch: producer pin 0 expected 6fb779c2…` →
  the frozen goldens at `tests/test_mint_floor_artifact_generalized.py:1288-1293`
  (whose comment already tells you they move with an issuance).
- `constructed v2 cell artifact is invalid: artifact.pinset: explicit pinset: pins…`
  → the same golden-digest family propagating through pinset self-hashes.

That is the honest shape of the work: **the code change is small and the
fixture-review step is the bulk.** Sequenced plan:

1. **Kernel + schema + generator retarget** (C2–C6). Iterate against
   `tests.test_floor_mint_estimator` (must stay 37/37 — the replay gate) and
   `tests.test_mint_floor_artifact_generalized` (7.6 s loop).
2. **Golden re-derivation** with `_fixture_canonical_sha256`; update `:1276-1298`,
   and re-express the three hardcoded literals at `:1363`, `:1369`, `:9092`.
   Target: `test_mint_floor_artifact_generalized` 73 passed / 2 skipped / 0 red.
3. **Emit the three `_v3` packs + two `_v3` extraction specs** (C7); `--check`
   each; `--check --preserve-current-frozen-bytes` each `_v2` as the
   frozen-family regression assertion.
4. **New tests:** (i) the no-copied-scalar guard (§(e).7); (ii) a `_v2 → _v3`
   successor-emission test mirroring
   `test_d117_floor_qwen25_7b_plan.py:546-628`; (iii) `_v3`-generation plan tests
   mirroring the three `_v1` plan modules, asserting the `_v3` specs bind r4 and
   carry `max(observed_drift_s,0.009724)`; (iv) a positive assertion that the
   `_v1`/`_v2` specs still carry `…0.010818` under the new resolver.
5. **Copy-list fix** (`tests/test_arm_readiness_evidence_author.py:120-125`) —
   add `…_n17_r3.json` and `…_n17_r4.json`. Required, not optional: a
   `_v3`-generation authoring fixture resolves the r4 artifact via
   `_ISSUED_ACCEPTANCE_REGISTRY` (`arm_readiness_evidence.py:892-900`) and
   `_pinned_artifact` fails if those bytes are absent from the fixture repo.
6. **Evidence re-author** ×3 at the measurement checkout → clears
   `test_authored_evidence_makes_synthetic_pack_freeze_pass`.
7. **freeze-0003** ×3 at the measurement checkout.
8. **Docs/bookkeeping** — README suite count (clears `test_docs_freshness`),
   RUN_STATE, CLAIMS_STATUS, decision-log rows.
9. **Canonical FULL GREEN.** The two `test_authentication_io` reds and the
   `test_whole_window_selection` red must also be green; they belong to R1's
   lane, so the two rulings must land in one integration tree before the merge
   wave (§(h) disagreement 5).

**Carried limitation to record, not to fix here:** `_derive_pack_family` reads
the immutable historical v1 family (`arm_readiness_evidence.py:49-60`,
`:1347-1391`); a registry-driven successor route "is NOT yet built (reported to
the magistrate with the R1 registry install)" — the module says so verbatim.
This did not block `_v2`'s freeze and will not block `_v3`'s: PACK_FAMILY
cross-checks the v1 family's identity consistency, which is generation-independent.

---

## (g) Rejected alternatives

**G1 — Flat migration of the `0.010818` constant. REJECTED; refutation
independently reproduced.**
Baseline `tests.test_floor_mint_estimator` = 37/37 OK; with the flat flip
simulated = **8 failures + 49 errors**. Mechanism: every committed `_v1` and
`_v2` extraction spec carries the n19-era lexeme (6 occurrences each in
`configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json`,
`…_1p5b_v2_…`, `…_7b_…`, `…_7b_v2_…`), and `_validate_calibration_basis`
compares them to the single module constant (`floor_mint_estimator.py:166`).
A flat flip makes the entire n19 era unauthenticatable. Verdict: **correctly
refuted; do not revisit.**

**G2 — Generation-indexing via `_D102_GENERATION_DERIVATIONS`. ADOPTED, but
insufficient alone.**
Verdict: **adopt as the code layer.** It is the right mechanism, it reuses the
table that already exists and is already correct for r3/r4
(`calibration_bracketing.py:167-186`), it preserves the replay (37/37 executed),
and it mirrors the ratified preflight precedent. But by itself it produces no
r4-bound pack, and the `_v2` packs would remain the live claim surface while
carrying screens derived from a corpus containing a member the current method
refuses. That is a science defect, not a bookkeeping one.

**G3 — A new `_v3` pack family instead of regenerating `_v2`. ADOPTED, and it is
not really a choice.**
Verdict: **adopt as the artifact layer.** Not because it is tidier, but because
(i) the `_v2` generator refuses in-place regeneration —
`generation failed: the current frozen identity requires preserve mode`,
executed; (ii) the `_v2` spec's own committed policy text mandates "a newly
generated pack"; (iii) `_authenticate_freeze_predecessor` requires the `_v2`
committed tree digest to be stable (`arm_readiness.py:5028-5037`); (iv) the
lifecycle already generalises to arbitrary `_v<N>` by explicit design
(`arm_readiness.py:1283-1295`) and `_SUCCESSOR_PROFILE_PATTERNS` already admits
`_v3` (`:260-266`); (v) the science-neutral r2 reissue earned a whole new family,
so a science-changing one cannot earn less.

**G4 — Regenerate `_v2` in place ("supersede under the same identity").
REJECTED.**
Beyond G3's mechanical refusals: the `_v2` freeze evidence records the sha256 of
every executed source file
(`configs/campaigns/d117_floor_qwen25_1p5b_v2/arm_readiness.sources/multicell-mint.json`),
and I verified three of those already diverge at `9f7f091`
(`powermetrics.py` recorded `7380eea8…` vs current `9f165a51…`;
`uncertainty_evidence.py` `77412d19…` vs `2e5ecef9…`;
`calibration_bracketing.py` `62111af1…` vs `a84b0563…`). Re-minting
`freeze-0002` under new bytes would overwrite the only record that the old
triple was ever attested, and would leave nothing replayable for the `_v2` era.
Supersession-with-lineage costs one directory and preserves both.

**G5 — Resolve the screen from the acceptance artifact's own
`decimal_derivation` rather than the code registry. REJECTED (executed).**
The historical fixtures pass stub acceptance mappings without
`decimal_derivation` (`tests/test_floor_mint_estimator.py:38-42`); artifact
sourcing breaks the replay, registry sourcing keeps it 37/37. Registry sourcing
is also strictly more fail-closed on unregistered ids, and cannot diverge from
the artifact on an authenticated document
(`calibration_bracketing.py:550-559`).

**G6 — Accept any registered generation's screen (set-membership check).
REJECTED.**
It decouples screen from generation, so a pinset could declare acceptance r4
while carrying the r2 screen. That is precisely the crosswire the mint's
site-limited crosswire tests exist to catch
(`test_site_limited_postcollection_default_crosswire_is_caught` and siblings).

**G7 — Keep the mint lane pinned at r2 and defer the fan-out. REJECTED on
science.**
r2's `0.010818` is the rounded range of the n=19 corpus that includes
`20260722T222332-901c5c13`, whose stamp rectangles admit no single affine wall
rate (disjoint by ≥15 ppm) and which v2 had accepted as the corpus *maximum*
(`03-cold-science-review.md:59-74`). Publishing a floor whose never-zero
allowance descends from that corpus embeds a falsified clock model in the claim.

**G8 — Move `_ACCEPTANCE_SELECTION` to a generation-indexed value. REJECTED
(and barred by the brief).**
It is a role selector, not a generation pin (`floor_mint_estimator.py:42,165`;
`arm_readiness_evidence.py:934`). Moving it would be a genuine axis change with
no benefit to R2.

**G9 — A tracked golden-regeneration CLI. REJECTED.**
`tests/test_mint_floor_artifact_generalized.py:1276-1277` mandates that goldens
be "regenerated only by an explicit fixture-review step, never by the mint
implementation under test". A tracked tool converts a review step into a button.

---

## (h) Explicit disagreements with the brief's framing

**H1 — "generation-indexing **vs** `_v3` pack family" is a false dichotomy.**
They are orthogonal layers (code vs artifact) and the transaction needs both.
Each alone fails for a reason I executed (§0, §(g) G2/G3). This is my principal
disagreement and it changes the shape of the ruling: the magistrate should
ratify a *composite* spec, not pick a winner.

**H2 — "stale `DEFAULT_ACCEPTANCE_BOUND_SHA256` genesis digest (zero
consumers)" is not quite right, and the fix is a rename, not a value change.**
The digest `9a264c57…` has **two live code call sites**
(`calibration_bracketing.py:629` selects it as the expected digest for the
`schema_fixture_unissued` role; `:722` returns it for non-issued artifacts) and
one live test pin (`tests/test_calibration_bracketing.py:90-91`, exercised at
`:182-184` against a base85-embedded genesis fixture). It has zero *production*
consumers because no file under `configs/calibration/` has that role — I hashed
all five and none matches. So it is not stale and not dead; the trap is the
**name**: `DEFAULT_ACCEPTANCE_BOUND_PATH` now points at r4
(`:137`) whose digest is `dcb3d3ed…`, so a future fan-out will "update"
`DEFAULT_ACCEPTANCE_BOUND_SHA256` and silently break genesis-fixture
authentication. **Fold in, as a rename only** (e.g.
`GENESIS_FIXTURE_ACCEPTANCE_SHA256`) with a comment — zero behaviour change,
and `calibration_bracketing.py` is already being edited, so the marginal cost is
nil.

**H3 — "the three `_v2` pack generators (floor-mint / detection-floor / pack)"
does not map onto the tree.**
There are exactly three `_v2` pack generators and they are the three campaign
`generate_configs.py` files (§C6). The `(floor-mint / detection-floor / pack)`
triple reads better as the three *kernel validator surfaces*:
`scripts/mint_floor_artifact_generalized.py` (floor-mint),
`joulewise/detection_floor.py` (detection-floor), and the generators (pack). My
enumeration in §(c) covers both readings; the ruling should adopt the explicit
file list rather than the parenthetical.

**H4 — The reissue tool's scalar-comparison limitation is not a constraint on
R2.**
R2 mints no acceptance generation — r4 is already issued, registered
(`calibration_bracketing.py:99-105, 127-133`), and its file digest verifies. The
bespoke derive/build route was needed for r3/r4 themselves, not for their
downstream fan-out. The brief's item 4 should be answered "none required" rather
than "specify the derive/build scripts".

**H5 — The "evidence-author acceptance copy-list omits r3/r4" item is not
incidental; it is a required part of R2.**
`tests/test_arm_readiness_evidence_author.py:120-125` must gain r3 and r4 or a
`_v3`-generation authoring fixture cannot resolve its acceptance bytes
(`arm_readiness_evidence.py:892-900` → `_pinned_artifact`). It moves inside the
transaction by necessity.

**H6 — The parked step 6 ("freeze-0002 re-mints") should be amended to
"freeze-0003 mints on the `_v3` roots".** Same measurement-checkout
path-binding, same three packs, but chaining forward rather than overwriting.
This is a change to the recorded plan and should be explicit in the ruling.

**H7 — Naming collision worth fixing in the record.** "R1" is being used for two
different things in the same session: the production capture-pipeline v3
adoption ruling, and the `arm_readiness` **R1 row registry**
(`R1_ROW_REGISTRY_SCHEMA`, `validate_r1_lifecycle_registry`,
`arm_readiness.py:45, 2693-2716`). §(e) records the real interaction with the
latter. The ruling should disambiguate.

---

## (i) Open questions only Ed can rule on

1. **Family marker / supersession record.** My design mints `_v3` and leaves the
   `_v2` freeze receipts standing as history, but it does not *mark* `_v2`
   superseded anywhere machine-readable. The trace lists "family-marker
   particulars" as an Ed-owed ruling. If the marker design is intended to be the
   record-side complement of a family bump, R2's `_v3` mint is the first thing
   that needs it — but I have deliberately not designed it here, because a
   supersession marker is a schema/contract change ("big" under D-144) and
   belongs to its own co-design pass. **Question: does `_v3` land before, with,
   or after the family marker?** My recommendation: land `_v3` first (it is
   blocking FULL GREEN and Ed's confirmation table), retrofit the marker.

2. **Should `_v3` land as an unfrozen draft, or frozen inside this
   transaction?** Freezing requires the measurement checkout at
   `/Users/edr/JouleWise-measurement-20260818` at the final head — an Ed-hardware
   session. Freezing inside the transaction gives a complete, auditable
   confirmation table with step-4 receipt hashes (which is what was correctly
   refused at the park). Deferring the freeze gets FULL GREEN sooner but leaves
   the confirmation table incomplete again. **This is the only item in R2 that
   requires Ed's machine, so it also sets the batching.**

3. **Do the `_v3` packs supersede the `_v2` packs as the live capture targets
   for the upcoming windows, or is `_v2` retained as a parallel arm?** The
   trace records Ed advising "v2-arm = coin-flip; recommendation = complete the
   cycle". My design assumes single-arm supersession (`_v3` is the live pack).
   If a `_v2` arm is retained, `_plan_profile` admits only one pack per profile
   through the registry route (`arm_readiness.py:2699-2712` requires exactly one
   match), so a parallel arm would need a design I have not built.

4. **R1 row-registry ordering** (§(e)): if the registry install is scheduled
   before the `_v3` freeze, its `successor_pack_ids` reserved values must name
   the `_v3` ids. That is one of the "R1 registry reserved values (five items)"
   already on Ed's list; R2 supplies three of the five.

---

## Appendix — commands I ran (all read-only, `PYTHONDONTWRITEBYTECODE=1`)

```
python3 -m unittest tests.test_mint_floor_artifact_generalized
  -> Ran 75 tests in 7.572s / FAILED (failures=11, errors=22, skipped=2)      # the 33

python3 -m unittest tests.test_floor_mint_estimator
  -> Ran 37 tests / OK                                                        # n19 replay baseline

<flat-migration simulation, monkeypatch only>
  -> Ran 37 tests / FAILED (failures=8, errors=49)                            # refutation reproduced

<generation-indexed simulation, monkeypatch only>
  -> Ran 37 tests / OK                                                        # replay preserved

<r4 basis through selection_from_authenticated_spec>
  current code -> REFUSED "policy literals are not canonical"
  gen-indexed  -> accepted ("default")

<r4-resolved mint lane, monkeypatch only>
  -> run=75 failures=10 errors=22                                             # residual = goldens

configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py --check
  -> generation failed: the current frozen identity requires preserve mode    # in-place regen refused

... --check --preserve-current-frozen-bytes
  -> verified d117_floor_qwen25_1p5b_v2 frozen by d134 receipt: 100 science configs

... --output-root <tmp> --pack-id d117_floor_qwen25_1p5b_v3 --family-suffix _v3
  -> generated d117_floor_qwen25_1p5b_v3 unfrozen draft: 100 science configs
     emitted configs/floor_mint/d117_qwen25_1p5b_v3_extraction_spec.json
     issued_acceptance.acceptance_id = d079_calibration_acceptance_v2_n19_r2   # <- the one edit needed

configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py --check
  -> verified unfrozen draft: 100 science configs                             # _v1 untouched, still green

shasum -a 256 configs/calibration/*.json
  -> r3 73f02263… r4 dcb3d3ed… r2 3c92dd66… n19 316113 96…                    # all match the code pins
     (no file matches DEFAULT_ACCEPTANCE_BOUND_SHA256 9a264c57… — see H2)
```
