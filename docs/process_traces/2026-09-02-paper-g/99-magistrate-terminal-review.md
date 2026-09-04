# Paper G — magistrate terminal review (apex read)

Date: 2026-09-04. Merge candidate: `feat/2026-09-02-paper-g` at c8ba4f5d (= round-4 head 114092f9 + origin/main e8e1fd9e merged, skeleton ledger conflicts resolved by a Sol seat, report 12).

## What I read (primary artifacts, not summaries)

- The full `docs/paper` diff of the branch against main before the merge: the three OUTCOME-BRANCH groups (Abstract, Section 7 discussion, Section 10 conclusion) with A / B / Refusal alternatives; the Section 1 definitions paragraph; the first-use ledger changes (233 → 265 rows after integration); the registry amendments for DS-32 / PG-08 and the successor-slot section; `fill-rehearsal/branch-selection.md`; `select_outcome_branches.py` in full and its test module; the retensing-plan diff.
- The round-4 delta re-audit (trace 11, CLEAN, four executed verifications) and the merge-resolution report (trace 12), plus the resolved hunks.

## Design-level answers (row 7)

1. **Outcome selection is mechanical and refuses ambiguity.** The selector requires exactly one complete group per section, the three alternatives in fixed order, quoted content lines only, the exact bold label, and slot counts per outcome (TR-01 ×1 per group; OB-01 only under B; DS-32/PG-08 absent under Refusal; OR-01 only under Refusal), then re-checks whole-document counts (Table 3 retains one verdict slot each; the Section 4 Refusal form retains one OR-01) and a 250-word Abstract budget on reader-facing text. It refuses to overwrite its input or an existing output. This is the right shape: the paper cannot print a verdict inferred from the ratio outcome.
2. **Refusal has two stages with one carrier.** Before-comparison (window excluded / verdict absent) and at-close-out (ratio missing / unauthenticated / zero denominator) are both named in prose and printed through `[FILL:OR-01]`; the registry binds DS-32/PG-08 REFUSAL table renderings so no marker survives a Refusal fill. Consistent across skeleton, branch-selection doc, retensing plan and registry.
3. **Pedagogy.** The ledger test passes on the integrated reading order (title → selected Abstract → Sections 1–11). RESIDUAL, non-blocking: the new Section 1 definitions paragraph glosses ~25 terms in one block before they are used. It satisfies the first-use test but is a glossary dump rather than terms built from physical reality at their first use; queued for the paper-H polish pass as `PAPER-H-INTRO-GLOSSARY-01`, not a merge blocker (moving definitions is a prose reorganisation the outcome-branch work does not depend on).

## Overbuild / merge-ability (row 8)

Nothing to prune: the selector and its test are the minimum that makes selection mechanical; the `--check-rendered` guard is required by the 250-word rule after filling.

## Integration replay (row 9)

Full unpiped suite on the integration tree c8ba4f5d (paper-G + main with #279/#280/#281), log `~/.claude/jobs/3c46c831/tmp/int-paper-g-replay-final.log`. Exact tail appended below when it completes.
