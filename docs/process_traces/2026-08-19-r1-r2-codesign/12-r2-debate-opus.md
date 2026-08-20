# R2 DEBATE ROUND 1 — OPUS SEAT

Read-only at `9f7f091` in `wtTXN`; all runs `PYTHONDONTWRITEBYTECODE=1`, temp
output roots only. `git status --porcelain` empty throughout.

---

## Item 1 — RESOLVER SOURCING · **AMEND**

**Executed** (`tests.test_floor_mint_estimator`, the n=19 replay module,
identical harness, three resolver modes monkeypatched):

| Mode | Result |
|---|---|
| **artifact-sourced** (terra F2: read `acceptance["decimal_derivation"]["ratified_operatives"]`) | **`run=37 failures=14 errors=49`** |
| **registry-sourced** (opus G5) | `run=37 failures=0 errors=0` |
| **hybrid** (amended clause below) | `run=37 failures=0 errors=0` |

Cause: the historical replay fixture supplies a three-key acceptance stub with
no `decimal_derivation` (`tests/test_floor_mint_estimator.py:38-42`), and
terra's own "authenticates by its own registry entry" step would reject the stub
outright. Artifact-sourcing is only viable if the n=19 replay fixture is
rewritten — which is the one thing replay integrity forbids.

But terra's *stated requirement* — "cross-pairing an r2 acceptance with the r4
screen, or r4 with the old screen, refuses" (F2) — is right, and bare
registry-sourcing gets it only via the downstream rule comparison. So I amend
rather than merely maintain. **Executed** on the amended resolver:

```
r4 id + r4 operatives (honest)        -> screen 0.009724
r4 id + r2 operatives (CROSSWIRE)     -> REFUSED: supplied operatives disagree with the registered generation
n19 id + r4 operatives (CROSSWIRE)    -> REFUSED: supplied operatives disagree with the registered generation
n19 id, stub (historical replay)      -> screen 0.010818
unregistered id                       -> REFUSED: unregistered generation
```

**AMENDED CLAUSE (replaces opus R2-SPEC-1 sentence 2 and terra F2 bullet 2):**

> The mint policy for a supplied acceptance is resolved **from the registered
> D-102 generation entry keyed by that acceptance's own `acceptance_id`**
> (`calibration_bracketing._D102_GENERATION_DERIVATIONS`), which is the sole
> authority. An unregistered `acceptance_id` refuses. **If** the supplied
> acceptance additionally carries a `decimal_derivation.ratified_operatives`,
> its `bracket_screen_s` MUST equal the registered value or the call refuses
> (`supplied acceptance operatives disagree with the registered generation`).
> Callers supplying only an identity stub are served from the registry; callers
> supplying full authenticated artifact bytes get both checks.

This is safe because `_valid_acceptance_bound` already forces artifact/registry
agreement on any authenticated document (`calibration_bracketing.py:550-559`),
so the cross-check can never fire on honest input — only on a crosswire.

---

## Item 2 — TOOLING · **CONCEDE (in part) + AMEND**

### I CONCEDE terra F3's "do not edit the `_v2` generators". My §C6 was wrong.

**Executed evidence against my own design:**

```
d117_floor_qwen25_1p5b_v2       plan_tree.generator.sha256 == sha256(generate_configs.py)  MATCH
d117_floor_qwen25_7b_v2         MATCH
d117_contrast_qwen25_1p5b_vs_7b_v2  MATCH
```

Each `_v2` generator's sha256 is pinned in **three committed files inside its
own frozen pack** — `plan_tree.json`, `arm_readiness.sources/pack-authentication.json`,
`arm_readiness.sources/multicell-mint.json` — and the latter two are the exact
source files whose digests `freeze-0002.json` pins (`freeze-pack-authentication-v1`,
`freeze-multicell-mint-v1`). `committed_pack_tree_sha256` frames
`(path, mode, length, sha256(content))` over **every** committed blob under the
pack root (`arm_readiness.py:2652-2677`), so `generate_configs.py` is inside the
pack digest. The three `_v2` pack digests are additionally published as the
frozen family's identity in `docs/run_reports/2026-08-18-t10-session.md` and
`docs/process/ed-morning-packet-2026-08-18.md`. Editing them is an M-2
frozen-bytes violation. Conceded without reservation.

### I MAINTAIN that no new bespoke tooling survives. **Executed:**

```
$ generate_configs.py(_v2, UNEDITED) --output-root <tmp> --pack-id …_v3 --family-suffix _v3
  -> generated d117_floor_qwen25_1p5b_v3 unfrozen draft: 100 science configs
$ git status --porcelain
  (empty)                                   # _v2 bytes untouched by the emission
emitted _v3 plan_tree.generator.sha256 == sha256(emitted _v3/generate_configs.py)   MATCH
emitted _v3 generator: SOURCE_PATH = Path(__file__).resolve();  REPO_ROOT = parents[3]
emitted _v3 generator still carries: SUCCESSOR_ACCEPTANCE_ID = …_n19_r2 (:152),
                                     CURRENT_FROZEN_RECEIPT_SHA256 = ddbbb409… (:72, v1's),
                                     "allowance_rule": "max(…,0.010818)" (:1397)
```

The three constants that must change are now inside a **new, unfrozen file**.
Terra's three tools are unnecessary: tool 2 (deterministic v3 builder) is
`embedded_generator_bytes()`, already ratified and already deterministic; tool 3
(family verifier) is `--check` per `_v3` root plus
`--check --preserve-current-frozen-bytes` per `_v2` root (both executed green);
tool 1 (mint-policy derivation command) is the item-1 resolver.

**AMENDED CLAUSE (replaces opus §C6 and terra F4 items 1–3):**

> The `_v2` generators and every other byte inside the three frozen `_v2` pack
> roots are READ-ONLY in this transaction. The `_v3` family is produced by
> running each **unedited** `_v2` generator with
> `--pack-id <family>_v3 --family-suffix _v3`, landing the emitted tree, then
> editing the emitted, unfrozen `configs/campaigns/<family>_v3/generate_configs.py`
> at exactly three sites — `SUCCESSOR_ACCEPTANCE_{REL,SHA256,DERIVATION_SHA256,ID}`
> → the target generation; `calibration_basis()["allowance_rule"]` → derived from
> `acceptance_pin()`; `CURRENT_FROZEN_RECEIPT_SHA256` → that pack's own `_v2`
> `freeze-0002` sha (hygiene: it is currently inherited as v1's `ddbbb409…`) —
> and then self-regenerating the `_v3` tree and running `--check`.
> **New code in this transaction is limited to:** the ~15-line generation
> resolver, its call-site rewiring, the `schema_v2.json` conditional, and a
> no-copied-scalar guard test. No new tracked CLI. A tracked golden regenerator
> stays barred (`tests/test_mint_floor_artifact_generalized.py:1276-1277`).

---

## Item 3 — `DEFAULT_ACCEPTANCE_BOUND_SHA256` · **MAINTAIN (strengthened) + AMEND**

**Executed**, applying terra F3 row 1 literally (value → r4's digest):

```
fixture artifact_role         : schema_fixture_unissued
BASELINE  authenticates?      : True
AFTER value change ->         : False          # genesis fixture stops authenticating
_acceptance_artifact_sha256(fixture): 9a264c57…  ->  dcb3d3ed…   # now returns r4's digest for a FIXTURE-role doc
tests.test_calibration_bracketing, BOTH states: Ran 42 tests / OK (skipped=1)
```

The digest is the genesis-fixture authentication value consumed at
`calibration_bracketing.py:629` and `:722`; changing it silently disables the
fixture-role path **and no test catches it**. That is worse than my original
"live trap" framing: it is a *silently uncovered* live regression, exactly the
class of defect this fan-out exists to stop.

**AMENDED CLAUSE (replaces terra F3 row 1's second half):**

> `DEFAULT_ACCEPTANCE_BOUND_SHA256` is **renamed only**, to
> `GENESIS_FIXTURE_ACCEPTANCE_SHA256`, value `9a264c57…` unchanged, with a
> comment stating it authenticates the retained `schema_fixture_unissued`
> genesis bytes and is NOT the digest of `DEFAULT_ACCEPTANCE_BOUND_PATH`. Its
> two call sites are renamed with it. A regression test is added asserting that
> the genesis fixture bytes authenticate and that `_acceptance_artifact_sha256`
> returns the genesis digest for a fixture-role document — closing the coverage
> gap that let the misnaming survive.

---

## Item 4 — ACCEPTANCE BINDING UNDER THE R1 OUTCOME (r5)

### (a) What rebinds, what does not

**Rebinds to r5** (all identity/digest carriers):

- `joulewise/calibration_bracketing.py` — four new module constants (path / id /
  file sha), one `ISSUED_ACCEPTANCE_REGISTRY` row (`:109-134`), one
  `_D102_GENERATION_DERIVATIONS` row (`:179-186`), and
  `ACTIVE_ACCEPTANCE_ID` / `DEFAULT_ACCEPTANCE_BOUND_PATH` (`:136-137`) → r5.
- `joulewise/arm_readiness.py:4148` — add r5 to the "not a corpus-GROWTH
  successor" issued set (one line).
- `tests/verify_calibration_acceptance_corpus.py:55` — alias r5 → r3's expected
  statistics (one line, exactly the r4 pattern at `:53-56`).
- Emitted `_v3/generate_configs.py` ×3 — `SUCCESSOR_ACCEPTANCE_*` → r5.
- **Regenerated, never hand-edited:** the two `_v3` extraction specs'
  `calibration_basis.issued_acceptance` (4 fields × 6 cells × 2 specs) and the
  three `_v3` plan trees' `acceptance_policy`.
- `tests/test_arm_readiness_evidence_author.py:120-125` copy-list → r3 + r4 + r5.
- `tests/test_mint_floor_artifact_generalized.py:1276-1298` goldens — they embed
  the live issued acceptance identity and both digests, by their own comment at
  `:1281-1283`.
- Live-default path literals: `tests/test_calibration_writer_crash_matrix.py:106,107,119,154`;
  `tests/test_powermetrics_fiducial.py:1548`; `tests/test_calibration_exits.py:759,2274,2278`.

**Untouched**, because r5 is science-neutral to r4 (same n=17 corpus, same
member table, therefore the same D-102 derivation — the r3→r4 relationship,
`calibration_bracketing.py:90-98, 183-185`):

- The screen `0.009724` and the rendered rule `max(observed_drift_s,0.009724)`,
  **everywhere**. `_D102_N17_DERIVATION` itself. Consequently the value enums in
  `schema_v2.json` do not change (there remain exactly two screens); only the
  acceptance-id branch list gains r5, and if that branch is written over the
  *n17 generation set* rather than per-id it is one list entry.
- `_ACCEPTANCE_SELECTION`. All n19-era pins (`_v1`/`_v2` specs,
  `tests/test_floor_mint_estimator.py`, the three plan modules). r4 stays
  registered and retained as an intermediate generation, exactly as r3 is.

### (b) Cheapest safe sequencing (no step done twice)

| # | Step | Why here |
|---|---|---|
| S0 | **R2 kernel:** resolver + estimator/detection_floor/mint-tool rewiring + `schema_v2.json` + genesis rename | The only R2 work that is **r5-neutral**; and the goldens cannot be re-derived to green while the validators still hardcode `0.010818` |
| S1 | **R1 flip + r5 issuance** (one commit, R1's design) + the three one-line r5 rows above + `ACTIVE_ACCEPTANCE_ID` → r5 | Live default is r5 from here on |
| S2 | **Golden re-derivation ONCE against r5** (`_fixture_canonical_sha256`) + r4→r5 path literals + copy-list → r3+r4+r5 | `test_mint_floor_artifact_generalized` green |
| S3 | **Emit `_v3` ×3** from unedited `_v2` generators → edit the emitted generators to **r5** → self-regenerate → `--check` ×3, plus `--check --preserve-current-frozen-bytes` on each `_v2` | `_v3` is born bound to r5; never touched twice |
| S4 | Evidence re-author ×3 at the measurement checkout | Requires S2 green (MULTICELL_MINT runs three of the 33) |
| S5 | **freeze-0003 ×3** | MUST be last acceptance-bearing step |
| S6 | Docs / bookkeeping / canonical FULL GREEN | |

**Two hard ordering invariants:**

1. **freeze-0003 must be the last acceptance-bearing step.** If it lands before
   r5, `_v3` is frozen at r4 and r5 forces a `_v4`.
2. **`_v3` must never be emitted at r4 and retargeted later.** The generator
   pins the acceptance *file* sha at emission
   (`generate_configs.py:1963`); since r4's file is unchanged by an r5 issuance,
   the pin would **not** refuse — an r4-emitted `_v3` would silently keep
   binding a superseded generation. Silent, not fail-closed. Bind at birth.

### (c) Does my design make r5 harder? **No — strictly easier.**

Under the status-quo hardcoded shape, an r5 whose screen differed would require
chasing eleven literal sites across four files. Under the resolver it is one
`_D102_GENERATION_DERIVATIONS` row; for a *science-neutral* r5 it is a one-line
alias to `_D102_N17_DERIVATION`, byte-identical in form to the r4 line already
in the tree (`:183-185`). The item-2 amendment also helps: because the `_v2`
generators are never edited, an r5 landing mid-transaction perturbs nothing
frozen. The only R2 element that could bite is invariant 2 above, and it is
discharged by sequencing, not by new mechanism. My proposed no-copied-scalar
guard forbids the literals `0.010818`/`0.009724` in kernel sources — r5-neutral,
since r5 keeps `0.009724`.

---

## OFF-AGENDA BLOCKER FLAG (one)

**terra F3, "Evidence author" row — "For successor generations derive the three
same-ordinal siblings from the input pack identity, rather than binding `_v3`
evidence to v1 trees" (and F5 item 5, "without monkey-patching the historical
map"). This is a blocker and must be struck from R2.**

1. It is another ruling's territory by the module's own words:
   `joulewise/arm_readiness_evidence.py:49-55` states the v1 map is immutable
   and that "a registry-driven successor route for PACK_FAMILY derivation is
   **NOT yet built** (reported to the magistrate with the R1 registry install)."
2. It retroactively changes frozen evidence semantics. I verified that the
   `_v2` packs' committed `arm_readiness.sources/pack-family.json` references
   exactly `d117_floor_qwen25_1p5b_v1`, `d117_floor_qwen25_7b_v1`,
   `d117_contrast_qwen25_1p5b_vs_7b_v1`, and that
   `evidence-pack-family.json` byte-pins that source
   (`source_sha256 7d9e7b11…`), which `freeze-0002.json` in turn pins. Making
   `_derive_pack_family` read same-ordinal siblings means the sole producer of
   that file no longer reproduces the bytes the frozen `_v2` receipt attests —
   destroying the replay property terra's own F1 insists on.
3. It is unnecessary: `_v2` was frozen successfully with the v1-family
   derivation, which cross-checks identity consistency in a
   generation-independent way. `_v3` can freeze the same way.

Recommended disposition: R2 keeps `arm_readiness_evidence.py` **unedited**, and
the successor PACK_FAMILY route stays queued to the arm_readiness R1 row-registry
install as a recorded carried limitation.

---

## Net position after Round 1

Composite shape unchanged. One concession (no `_v2` generator edits — terra was
right, my C6 was wrong), one amendment adopting terra's anti-crosswire
requirement on top of registry sourcing, one maintained-and-strengthened item
(rename-only, now shown to be a *silent* regression), one new r5 sequencing
answer, one blocker flagged.
