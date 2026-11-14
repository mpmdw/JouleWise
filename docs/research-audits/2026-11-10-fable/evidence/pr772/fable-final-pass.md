# RL-147 final pass on PR #772 (Block 6 paper fills): ADMIT WITH FIXES (2026-11-13 19:50 PST)

Research lead (Fable 5.2). Written 2026-11-13 19:50 PST (`date`).

**Verdict: ADMIT WITH FIXES.** Three text-only fixes (findings 1 to 3), none of which changes a printed value or needs a reader re-read. `P1-RELEASE` is admitted conditionally (finding 4). After the fixes and green CI the PR may merge without coming back to me.

**Read.** `paper1.md` diff `a2563016e..4ccf5eb04` in full; `docs/analysis/b6/DEVIATION-LOG.md`; the reader's delta report on the audit branch (`evidence/pr772/reader-pr772-delta.md`, 167 of 167, 0 disagree); the manifest's row counts at `f813150c0` and at the head. I ran `python3.13 -I docs/paper/paper1/fill_check_b6.py` at the head: `19 fills rendered; 1536 printed elements by key; PASS`. From the released output I re-read the load-sensitivity and battery-assist lines in all 18 cells and contrasts (each equals the registered estimate, same counts) and the six floor-gate values. Read-only; nothing edited, committed or commented.

## Findings

1. **Fix (my wording, RL-147 §8): the conclusion overstates.** Line ~1838 says the sessions "differed from one another by more than their within-session intervals cover". The printed within-session intervals include the timing bound and cover every session difference by a wide margin; what the differences exceed is the statistical half-widths. Replace the clause with: "and the sessions differed from one another by more than their statistical half-widths cover (timing bounds not included)." The error is in the text I gave; the fill seat applied it verbatim.

2. **Fix (reader item (a)): soften "most of the data".** The figure behind it is mixed: by the printed counts the rule would leave 24 of 112 floor-cell quads and 13 of 57 contrast quads, but 78 of 118 repeats, so "most" is true of quads and not of repeats. No new number is needed. In the contention line replace "It was not adopted for this block for that reason, as registered, and the replication's sessions confirm it would have removed most of the data." with: "It was not adopted for this block, as registered; applied to the replication's sessions it leaves no cell and no contrast at the registered minimum." Also end the lead-in before it with a full stop instead of the colon ("…its result is printed beside each cell.").

3. **Fix: abstract wording.** "were *direction supported* and *direction supported*" becomes "were both *direction supported*". The rest of the assembled `P1-ABS-PART1` is admitted: it carries the decision-free L1 statement with intervals, "one session", kept over planned quads, the branch, no p-value and no §6.8 number, and my replication clause unchanged (RL-4 (i) to (iii)).

4. **`P1-RELEASE`: admitted conditionally; I do not need to see it before the merge.** Conditions, all mechanical: (i) PR #773 is merged; (ii) the fill is RL-147 §4 items 2 and 3 verbatim, with ⟨date⟩ the merge date of #773 taken from `git`; (iii) the seal record's new section gives 8 November 2026 11:17 PST and the released output `c06ee7c8…`, as the Block 5 clause says; (iv) the reader re-reads the digests and the two times in the filled clause against the two records, and `fill_check_b6.py` asserts them; (v) B6-DL-2 gets the written date. If (iii) fails, or the section's content differs from what §4 item 1 lists, it comes to me. `P1-RELEASE-BYTES` and `P1-B6-DISCLOSURES` stay pending as ruled.

5. **Reader item (b): fine.** The abstract's Block 5 values are Block 5 numbers under RL-3's closed gate and `fill_check_b5.py`'s ledger; they do not belong in the Block 6 manifest. The reader's match against Block 5's output is a welcome extra, not a requirement.

6. **Reader item (c): accepted.** Registration §7 item 3 supports "its own registered checkout". The sentence stays whole.

7. **The count "1,534 of 1,534": accepted, with what it means stated here.** It is the manifest at `f813150c0`, every row covered by one of the two reader passes; the seat's and the reader's credit splits differ (1,423 + 111 against 1,416 + 118) and the total is equal. The head's manifest has 1,536 rows: the two extra are the rows that quote the reader's own counts, which the reader cannot re-read without recursion. No action; if a later change adds a printed value, RL-147 §7 item 3 applies again.

8. **Applied as ruled, checked in the diff:** §1 sentence and B6-DL-1; §2 paragraph and Table 6a column (the reader's three sets equal mine); §3 definition, twelve sensitivities rounded up, both caption sentences, with Block 5's range added because its output holds it; §5 caption sentence and 1.99975; §6 floor-gate rows (10.18, 7.79, 7.21, 6.96; 8.84, 7.98, 7.79, 7.79; rounded up, "—" for Δ and summary), the two amended replication sentences, the 8a sentence and B6-DL-3, "decision 6 (a)" dropped from the label; §8's edits and the §5.4 addendum verbatim; §10's two lines, the paragraph, the pending marker and the caption sentence. The fill seat's placement of §10 (c) and (d) is accepted.

9. **Small, accept as is:** the load-sensitivity and battery-assist lines begin "no kept unit was removed only by…" and "no kept unit held…"; both are true as written (0 restored, 0 removed in 18 of 18). The "measured alone … in alternation" clause in the between-sessions paragraph stays; it describes the packs' designs and the sentence says no cause was tested.

## Not verified by me

- I did not re-read the 167 delta rows; the reader did. I spot-read the floor gates and the two labelled lines only.
- PR #773's content and CI; finding 4 is conditional on it.
- The full test suite and CI on the head; ledger rows 2 and 3 are the lead's.
- Cell-by-cell position of printed values, as in RL-147 §7 item 5.

**Owner.** The fill seat: findings 1 to 3, then finding 4 after #773. The reader: finding 4 (iv). The lead: ledger, CI, merge, and telling me after.

**Gate.** Ledger row 4 (cold Fable final pass) is this document once findings 1 to 3 are in; row 1 is the reader's two reports.
