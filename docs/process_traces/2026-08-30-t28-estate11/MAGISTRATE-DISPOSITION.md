# Estate 11 — magistrate disposition (Fable, 2026-08-30)

Estate 11 (the D-157/D-164 mint-path rehearsal) ran in a throwaway
commit-exact clone at BASE `0438566b` (newest main head with green CI,
containing #209 and #228) and HALTED at runsheet §1.1's anchor-map re-check —
REFUSE, 4/15 anchors matched. Director's evidence records are custodied in
this directory (step index `001-*`, halt record `070-*`); the clone's own
custody transcripts were session-local and are summarized by those records.

## Classification RATIFIED: PROCEDURE DRIFT, the instrument behaved correctly

Ten of the eleven mismatches are pure line drift (`arm_readiness.py` moved
+10..+554 lines since the delta's coordinates); the eleventh is a renamed
symbol. Nothing downstream ran; no pack, no freeze, no mint. The halt is the
anchor gate doing its job on a stale delta, not an instrument defect.

## R-1. Anchor #14's rename is CORRECT; the delta pins the new name

PR #228 renamed `test_pinset_is_byte_pinned_and_has_no_update_lane` to
`test_pinset_is_byte_pinned_and_has_no_unreviewed_update_lane` because D-161
R-1 installed a REVIEWED refresh lane — the invariant properly narrowed from
"no update lane" to "no unreviewed update lane." RULED: the runsheet/delta
pins the new name; the narrowing is the reviewed design, not drift. (#228
should have appended a delta section when it touched pinned surface — the
decided≠done class; recorded, no further action beyond this ruling.)

## R-2. Estate 12 derives anchors AT CUT, pinned by symbol

The delta's frozen line numbers go stale on nearly every merge. RULED: the
estate-12 delta (and the delta template it inherits) replaces frozen
line-number anchors with SYMBOL-pinned anchors resolved at estate cut — the
cut step derives each anchor's current line from its pinned symbol name and
records the derivation in the estate evidence; a symbol that no longer
resolves is the halt condition. The three stale immutable-audit ranges and
the §0.3 `PINSET`/`PINSET_SHA256` citations re-derive the same way.

## R-3. S3 D6 review-record correction: COMPLETE

All four custody tools' bytes equal their tracked `.sha256` sidecars at BASE;
`build_v4_histsem_pinset.py` is `d72c1560…`. The S-1 `MANIFEST.md` §6 record
of `29335e6f…` is hereby SUPERSEDED by this estate's re-pin record
(`040-s3d6-tool-digest-repin.txt`); the pinned MANIFEST bytes were not
edited, per the ruling that created the correction item.

## Standing results

W-10 is confirmed installed at BASE (`_admit_bound_analysis_manifest` at
`arm_readiness.py:5271`, called from `generate_freeze_receipt` at `:7584`,
with both test modules present; 76 pre-author tests ok). Estate 11's purpose
— rehearse the mint path and surface drift before a live window — is served;
the full §§1.2–5 rehearsal folds into ESTATE 12 on the `_v5` pack, whose
delta must be cut per R-2 after the `_v5` generator lands (PR #241).
