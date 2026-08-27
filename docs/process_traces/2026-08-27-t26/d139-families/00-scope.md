# S8 scope note — D-139 A2 / D-157 W-10, the gamma families block

Stream S8, branch `fix/d139-a2-gamma-families`. Written by the S8 director
before implementation, from live probes at `d4e57383`; every claim below was
executed, not inferred, unless it says otherwise. Terms used here: the **gamma
pack** is `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/` (the D-117
1.5B-vs-7B contrast pack); the **`_v4` transaction** is the atomic re-freeze
that mints `_v4` successor packs; the **prospective manifest** is the
pre-registered analysis contract that claim consumption reads, validated by
`validate_prospective_analysis_manifest_v3`; the **draft manifest** is the
different, looser shape the pack generator emits today.

## (i) What the `_v4` transaction mints, and where gamma's manifest comes from

The transaction mints **three** `_v4` pack roots, and the gamma pack is
**generated from the `_v3` generator at mint time** — it is not copied.

- Runbook step C1 (`docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:515-521`):
  "Each `_v3` generator is run with `--pack-id <the _v4 id> --family-suffix _v4
  --no-preserve-current-frozen-bytes`, then all three roots are committed in one
  commit."
- Runsheet §3.1 (`docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:1482-1500`)
  gives the three literal commands: the gamma pack from
  `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py`,
  the two floor packs from their own `_v3` generators.
- The allowlist contract (§2.1, `:1311-1350`) enumerates 37 paths per `_v4`
  root plus the successor pinset = 112 entries. Every path is a `_v4` path.

Consequence: a change to the gamma `_v3` **generator** propagates into the
minted `_v4` bytes. The committed `_v3` pack bytes need not — and cannot —
change: `PRESERVE_CURRENT_FROZEN_BYTES` is False while `PACK_STATUS` is
`frozen_by_d134_receipt`, so `GenerationIdentity.__init__`
(`generate_configs.py:202-210`) refuses both in-place regeneration and `--check`
of the current identity ("the current frozen identity requires preserve mode" —
observed live). The successor emission is the only legal generation.

## (ii) The estate-10 clone proof minted the defective manifest, and nothing noticed

Verified live at `d4e57383`, emitting `_v4` exactly as C1 does, into a temp root:

    families: null
    ctr-d117-decode-…      test=two_sided  direction=positive
                           multiplicity={"method":"Holm","alpha":0.05,"m":1,
                             "note":"family_m=1 is contingent on unresolved …"}
    ctr-d117-prefill-p256-… test={"status":"EMPTY",…TODO(lead authority)…}
                           direction=null
                           multiplicity={"status":"EMPTY",…}
                           floor_dependency={"status":"EMPTY",…}

This matches the preserved estate-10 `_v4` manifest the Sol seat read
(`01-sol-seat.md`: "no `families` key at all, decode m=1, prefill EMPTY,
`draft_status: as_generated_pre_d134_freeze`").

**Why §3.10 and §4 passed anyway:** the transaction never validates the analysis
manifest's scientific content. `grep -in
'analysis_manifest|prospective|multiplicity'` over the whole S-0 runsheet
(`s0-runsheet-r4.md`, 4400+ lines) returns **zero hits**. §3.10 is a test-suite
green record and §4 is a tamper/allowlist probe battery; both treat the manifest
as opaque bytes whose only property is its digest. `validate_prospective_…` has
no callers outside its own module and tests (three-seat finding F-2), and the
freeze/readiness path (`joulewise/arm_readiness.py` ~:4948-4963) never calls it.
That is precisely the hole D-157 R-2 closes.

## (iii) The predicates the regenerated manifest must satisfy

Entry point `validate_prospective_analysis_manifest_v3`
(`joulewise/analysis_manifest_v3.py:2777`; body ~:2150-2630).

| Predicate | Site | Refusal code |
|---|---|---|
| Top keys exactly `_PROSPECTIVE_TOP_KEYS` (15 keys) | `:997-1012` | `analysis_prospective_schema_invalid` / `…_unknown_key` |
| `freeze_status == "frozen"` | validator body | `analysis_prospective_not_frozen` |
| No EMPTY/TODO slot anywhere | `_contains_unresolved_slot` `:1376`, emitted `:1928` | `analysis_prospective_unresolved_slot` |
| `families` nonempty array | `:2181-2190` | `analysis_prospective_family_invalid` |
| Each family's keys exactly `FAMILY_KEYS` | `:254-262` | `analysis_prospective_family_invalid` |
| `multiplicity` keys exactly `MULTIPLICITY_KEYS`, scalar types | `:263`, `:2222-2252` | `analysis_prospective_multiplicity_invalid` |
| Null-p admission through the production table (`len(p_values) == m`) | `:2255-2273` → `analysis_engine/multiplicity.py:28-31` | `analysis_prospective_multiplicity_invalid` |
| Exactly two contrasts covering decode + prefill_p256 | `:2276-2285`, `:2596-2604` | `analysis_prospective_contrast_cover_mismatch` |
| Contrast keys exactly `_PROSPECTIVE_CONTRAST_KEYS` (note `equivalence`, `prompt`) | `:1039-1060` | `analysis_prospective_schema_invalid` |
| Families cover each frozen contrast exactly once | `:2623-2630` | `analysis_prospective_family_invalid` |
| 80 unique members ordered 1..80, 20 distinct ABBA blocks, block numbers 1..10 per arm | `:2588-2622` | `…_member_cover_mismatch` / `…_block_cover_mismatch` |
| Four declared attachment roles in `finalization_contract` | `:2632-2660`, `_REQUIRED_ATTACHMENT_ROLES` `:1092` | `analysis_prospective_schema_invalid` |

Second and third consumers of the same numbers: `analysis_engine/registry.py`
(~:431) carries the production m=2 value, and claim-time validation requires
`family.m == len(contrast_ids)` (`analysis_engine/artifact.py:1574-1577`).

**Live baseline (before the fix), on the emitted `_v4` manifest — four refusals:**

    analysis_prospective_schema_invalid   missing design, families,
        finalization_contract, freeze_status, frozen_semantics_sha256,
        manifest_id, replacement_policy
    analysis_prospective_unknown_key      draft_status, postcollection_attachments
    analysis_prospective_unresolved_slot  manifest contains an EMPTY/TODO placeholder
    analysis_prospective_not_frozen       manifest.freeze_status must be 'frozen'

So the fix is not "change m from 1 to 2": the generator emits a **draft-shaped**
manifest that is missing seven of the fifteen prospective top keys and carries
two keys the prospective contract does not know. D-157 R-1's "production
resolver … the full prospective top-key set" is the correct scope, and admission
— zero refusals — is the acceptance test, not the m literal alone.

## RUNBOOK DELTA — changed-set consequence (D-157 R-5)

**Files whose bytes change in this PR:**

1. `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py`
2. `joulewise/arm_readiness.py` (the R-2 mint-admission seam)
3. `tests/test_d117_decode_contrast_plan.py`, plus two new test modules
4. this note, and the S8 bookkeeping lines in `TASK_QUEUE.md` /
   `docs/process/state_kernel.json`

No committed pack byte changes. No `_v4` pack is created in the repository.

**Not in the 112-entry allowlist.** Every allowlist entry is a `_v4` path
(§2.1 `ROOTS`/`SLUGS`/`PINSET`, `s0-runsheet-r4.md:1330-1350`); the generator is
not among them, and the `_v4` pack digests are minted at C1/C8, never pre-pinned.
No expected `plan_sha256`/`tree_sha256` literal is recorded anywhere in the
runbook, the runsheet, or the repo (`grep` for the current emitted values
returns nothing), so no literal in either document goes stale.

**Not in `build_v4_histsem_pinset.py`'s delta.** `_row` (`:121-131`) compares the
`_v4` root's tree at the historical (pre-authoring) head against the current
head; both are post-C1, so an edit made before the transaction is invisible to
it. `_delta` (`:80-118`) additionally whitelists `generate_configs.py`
explicitly (`arm_readiness.py:_HISTSEM_ALLOWED_MODIFICATIONS`, `:2995-3000`).

**COLLISION — NEEDS-RULING before merge.** `generate_configs.py` lives *inside*
the `_v3` pack root, and `committed_pack_tree_sha256`
(`joulewise/arm_readiness.py:2726-2760`) hashes **every committed blob** in that
root from `git ls-tree HEAD`. `verify_receipt_histsem_pack` (`:3481`) recomputes
it and refuses on inequality with the committed pin:

    if current_digest != row["current_pack_sha256"]:      # arm_readiness.py:3517
        raise HistoricalSemanticsError("histsem_pinset_mismatch", …)

Measured now: the `_v3` root's tree digest is
`0d07194143702b266267f0faa7b051695ffb5e1c56dc7a69d0b2dca8aaa883ef`, exactly the
`current_pack_sha256` pinned for `d117_contrast_qwen25_1p5b_vs_7b_v3` in
`configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`, and
`verify_receipt_histsem_pack` passes. **Committing any change to that generator
changes the digest and makes the committed pinset row stale**, so
`verify_receipt_histsem_pack` on the `_v3` pack refuses `histsem_pinset_mismatch`
and `tests/test_receipt_histsem.py` (30 passed / 1 skipped / 150 subtests in
~128 s at this head, measured) goes red at
`verify_all_receipt_histsem(ROOT, require_published=True)` (`:254`).

Note the digest is computed from `ls-tree HEAD`, so the breakage appears only
**after the commit** — an uncommitted worktree with the edit still passes. Any
"tests green" report from a delegated session is therefore *not* evidence on this
point; the S8 director verifies it post-commit.

**Measured, not inferred.** In a throwaway worktree at `3ec0110f` the director
appended one comment line to the gamma generator, committed it, and re-ran:

    digest after commit: 6a39a3993ffd99d537024058ef8b48e6eba24d5e9346ccf4f6287ad2d1cbc2fc
    verify_receipt_histsem_pack → HistoricalSemanticsError:
        current committed pack differs from the governed pin
    pytest tests/test_receipt_histsem.py → 1 failed, 29 passed, 1 skipped
        FAILED …::test_full_corpus_verifies_two_coordinates_and_facts
        (joulewise/arm_readiness.py:3518)

Baseline at the same head before the probe commit: 30 passed, 1 skipped, 150
subtests. The probe commit was reverted. One field is stale and one test fails —
the scope of the cure is exactly the `_v3` row's `current_pack_sha256` in
`configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`; the repository has
no builder for that v1 pinset (`scripts/build_v4_histsem_pinset.py` builds the
successor `_v4` pinset *from* it), so the re-derivation is a governed hand edit
of one hex literal, or a new one-shot derivation script.

The cure is to re-derive that one row's `current_pack_sha256` (the mechanism
anticipates generator edits: `_HISTSEM_ALLOWED_MODIFICATIONS` names
`generate_configs.py`), which is a **pinset edit** — outside this stream's
authority and outside its WRITE_SCOPE. Raised to the magistrate as NEEDS-RULING
per D-157 R-5. Options as the director sees them, for the magistrate to rule on:
(a) re-derive the `_v3` row in `legacy_receipt_histsem_pinset_v1.json` in this
PR under an explicit ruling; (b) land it as a separate governed commit;
(c) some route that keeps the ruled values out of the `_v3` pack root entirely —
the director found none, because the generator rewrites its own source to emit
the successor, so the values must live in that file.

## Post-implementation addendum (same head, after D-157 landed)

D-157 was ruled while this note was being written and expanded the stream's
scope (R-1 the full prospective top-key set, R-2 the mint-time admission check,
R-3 the estate-11 requirement). The findings above are unchanged by it; the
collision below is D-157 R-5's NEEDS-RULING item, restated with the exact value
the cure needs.

At the S8 branch head with both commits applied, the gamma `_v3` pack root's
committed tree digest is

    4e2cb634ea9d336f26cc6b76559a9110072143c3574449665beff8804ccb8579

and `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json` still pins the
pre-edit value `0d07194143702b266267f0faa7b051695ffb5e1c56dc7a69d0b2dca8aaa883ef`
for `pack_id: d117_contrast_qwen25_1p5b_vs_7b_v3`. Exactly one field is stale,
and exactly one test fails because of it
(`tests/test_receipt_histsem.py::ReceiptHistoricalSemanticsTests::test_full_corpus_verifies_two_coordinates_and_facts`).
The digest is a function of the final committed generator bytes, so it must be
recomputed at whatever head the magistrate rules on — the value above is
correct for this head only.
