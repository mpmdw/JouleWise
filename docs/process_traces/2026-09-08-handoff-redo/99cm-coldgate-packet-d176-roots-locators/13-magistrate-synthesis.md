# Magistrate synthesis — D-176 seat-2 rulings: PRODUCTION_CUSTODY_ROOTS and driver locators (interactive magistrate, 2026-09-08 ~13:55 PDT)

Three seats on packet sha 0194d808… at 0a29b075: cold Fable (10), Opus contract lens (11), Astra consult (12). All
three reject a literal path list and rule a DERIVATION-SHAPED frozen census; all three rule the ARM receipt is
driver-written, never selected; all three want substitution to be a digest mismatch. Adopted text (to be installed by
seat 2 as a dated "§10.3 seat-2 rulings (2026-09-08)" block, propagated to §§2–6, the key tables and its §9 rows):

Q1 — PRODUCTION_CUSTODY_ROOTS
1. SHAPE (judge Q1.1 governs): a frozen tuple of `ProductionRootSpec(role, kind, value, predicate)` in the
   arm_readiness.py constants area plus a pure resolver `production_custody_roots(*, home, inventory) ->
   tuple[ProductionRoot, ...]` returning the existing `t0_rehearsal.ProductionRoot`. `kind` ∈ {LITERAL, HOME_RELATIVE,
   CLONE_DERIVED, INVENTORY}; `predicate` ∈ {DISJOINT, SIBLING_CHILD}. Changing a role or derivation is a reviewed diff.
2. ROLES: `magistrate_state` HOME_RELATIVE `night-custody/magistrate` DISJOINT (watchdog :55); `night_custody_parent`
   HOME_RELATIVE `night-custody` SIBLING_CHILD (judge Q1.2: rehearsal `custody_root` passes iff its parent is the
   resolved night-custody dir AND its basename equals the prefixed ARM window id; `measurement_root` must be wholly
   outside; equality, deeper nesting, another basename refuse); `backup_icloud` HOME_RELATIVE
   `Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup` DISJOINT (the three script literals are pinned to
   the constant by a regression; the `JOULEWISE_BACKUP_ROOTS` env override is NOT honoured by the census — all three
   seats); `quiet_guard_state` LITERAL `/Library/Application Support/JouleWise/quiet-guard` DISJOINT (quiet_guard.py:39);
   `repo_runs` CLONE_DERIVED `Path(arm_readiness.__file__).resolve().parents[1]/"runs"` DISJOINT (Opus Q1.4; the
   ledger home per calibration_ledger.py:94); `deployment_measurement_root` INVENTORY DISJOINT for EVERY entry of a
   NEW HEAD-pinned `configs/production_custody_inventory.json` (Astra F1: `{deployment_id, measurement_root,
   custody_root|null, ledger_path|null, notes}` for the canonical checkout and each retained measurement clone —
   today: /Users/edr/code/JouleWise, /Users/edr/JouleWise-measurement-20260813, /Users/edr/JouleWise-measurement-20260818,
   /Users/edr/JouleWise-measurement-v5-20260910-1c83f2a; a new clone is a reviewed diff). The judge's unevidenced
   HOME_GLOB role is REPLACED by the inventory. The calibration custody store has no code default and is excluded with
   a comment (judge). ARM-context roots are NOT census members (judge; Opus Q1.2 rejected because for a T0_REHEARSAL
   they are the rehearsal's own roots and would self-collide); the consumer applies the predicate to EACH of them.
3. PREDICATE (judge Q1.2 + Opus Q1.7 + Astra Q1.3): rehearsal side — plan `custody_root`, `measurement_root` and each
   ARM-context root must be absolute, non-symlink and `resolve(strict=True)` (night_gate must require an absolute
   `custody_root`; contract §6 amended; refusal `launch_go_receipt_invalid` naming the field); production side —
   specs resolve `strict=False` (a missing production root still counts); containment = the existing `_contains`
   (t0_rehearsal.py ~:741–746, `relative_to` on resolved paths, equality included, BOTH directions), never a string
   prefix; any DISJOINT containment → `rehearsal_roots_not_disjoint`; `resolution_error` → FAIL.
4. G6 (judge Q1.3 + Astra): the bundle loader derives `EvidenceBundle.production_roots` from the resolver; the
   manifest's `production_roots` list stays as an EVIDENCE RECORD that must equal the derived census (role set and
   resolved paths) or the loader raises `BundleLoadError("production-root census incomplete")` — this discharges the
   §7 incomplete-census replay. The fixture carries the full role set under a synthetic home + inventory.

Q2 — driver locators and ARM-before-GO
5. pack_root (judge Q2.1): `pack_night` gains an exact key `pack_root` (absolute, non-symlink, basename == pack_id);
   `committed_pack_tree_sha256(pack_root)` is recomputed at preparation, GO and consumption and must equal
   `pack_night.pack_sha256` and ARM `receipt["pack"]["pack_sha256"]`; ARM `receipt["pack"]["pack_root"]` must equal
   the resolved plan value. (Opus's "pack_root = measurement_root" is rejected: the pack is the campaign directory
   whose committed tree digest is pack_sha256, not the clone root.)
6. ARM receipt (all three, judge's path): never selected; the driver's own ARM step writes
   `<custody_root>/<pack_id>/arm_readiness.receipts/arm-NNNN.json` and presents exactly that path; GO binds
   `arm_receipt{receipt_id, sha256}`; supersession scan and `.consumed.json` refuse any other; driver refuses before
   GO on a higher-numbered unconsumed receipt or any consumption this boot.
7. Launch manifest (judge Q2.3, existing convention): fixed name
   `<custody_root>/<pack_id>/arm_readiness.t0.inputs/launch-manifest.json`; absent/symlinked/digest ≠ the T-0
   author's attested sha256 → refuse; GO `launch_manifest_sha256` is that digest.
8. Preparation (judge Q2.4, in-process, no new subcommand): census → read pinned plan bytes (plan_sha256; v3 parse)
   → preparation (recompute pack tree digest; re-read and re-digest both record locators; mismatch → refusal in
   night/receipt.json, no GO) → ARM (author T-0 evidence + ARM receipt, then `_verify_arm_receipt` on the written
   path with require_unconsumed; NO_GO → refuse) → GO (C1–C5; O_EXCL 0600 night/go_receipt.json) → launcher argv with
   `stdin=DEVNULL`: `--pack-root --arm-receipt --arm-readiness-custody-root --launch-manifest --night-plan
   --go-receipt --step6-confirmation-table --expected-confirmation-digest` (seat 3's six required inputs), replacing
   the direct chain exec for TRANSACTION_PACK only; the sidecar digest check stays.
9. Refusal rule (Opus Q2.6): missing → `launch_go_receipt_missing`; duplicate/ambiguous candidate or any digest
   disagreement between plan, GO and bytes on disk → `launch_go_receipt_invalid` with `detail` naming the field; no
   preference-order fallback.

Ownership: seat 2 installs 1–2, 4–8 (plan key, census constant + inventory file + resolver, G6 loader, driver
sequence, GO producer) and the §10.3 text; the consumer-side predicate of item 3 on ARM-context roots and the absolute
`custody_root` refusal are seat 3's (a bounded seat-3 follow-up after its current run); item 9 is shared.
