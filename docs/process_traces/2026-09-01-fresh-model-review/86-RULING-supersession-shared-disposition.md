# 86 — Ruling: shared disposition for multiple same-bundle supersession rows (SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01, phase 2)

Date: 2026-09-01. Input: the phase-1 exhibition (PR #260,
`tests/test_supersession_cross_consumer.py`) and its truth table
(`78-sol-supersession-truth-table.md`), which proposed "refuse: multiple
recognizable rows for X" for every multi-row shape and asked for a ruling.

## Why this is a parameter alignment, not a reinterpretation

The WRITER already carries the disposition. `require_occurrence_supersession_recordable`
(`joulewise/whole_window.py:2779-2785`) is documented as "Refuse a second
disposition for one bundle in one campaign log" and refuses to append a
second recognizable row for a bundle. The three READERS diverge from it:
the cooldown join refuses (`analysis_engine/inputs.py:2338-2358`, via the
complete-unknown payload), while whole-window membership
(`scripts/run_campaign.py` `_matching_supersession`) and membership binding
(`joulewise/whole_window.py:4703 _supersession_is_logged`) select a row, and
the D-093 `supersession_visibility_scan` reports clean. A reader that
tolerates what the writer refuses is the defect; the writer's rule is the
ruled shape, so aligning the readers installs it rather than changing it.

Counterfactual check against retained evidence (bench, 2026-09-01): across
all 33 `runs*/campaign_log.jsonl` files, 7 supersession rows exist and NO
bundle carries more than one — the refusal disposition voids no retained
evidence.

## Ruling

R-1. **Disposition:** for any bundle with MORE THAN ONE recognizable
`campaign_occurrence_supersession` row in one campaign log, every consumer
refuses — the cooldown join (already), whole-window membership, membership
binding, and the D-093 scan (which must REPORT the shape, not "clean").
Order-independent; byte-identical duplicates count as two rows; a valid
row plus an invalid same-bundle row is two recognizable rows (invalid
evidence stays visible as a competing disposition — truth-table row 4).
R-2. **Exactly one valid row** is the only selecting shape (truth-table row
1). No consumer may pick "latest" among several.
R-3. **Reason code:** one shared constant, `campaign_occurrence_supersession_multiple_rows`,
exported from `joulewise/whole_window.py` beside the existing
`REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_*` names and imported by the other
consumers (not re-typed).
R-4. **D-156 fences hold:** the cure is reader-side only; no historical log
bytes are rewritten, deleted, or reordered.
R-5. **Regressions:** the phase-1 exhibition tests are re-pointed from
"exhibits divergence" to "all four consumers refuse with R-3's code", one
test per truth-table row, plus the positive coherent row (single valid row
selects). Mutation table for the cure round: (m1) restore latest-wins in
`_matching_supersession`; (m2) restore `_supersession_is_logged` existence-only
membership; (m3) D-093 scan drops the multi-row report; (m4) reason code
retyped as a different string in one consumer — each must be killed by a
named test.
