# Opus 5.5 cold delta review, PR #762 (head aaa2f3086), 2026-11-13 ~14:52 PST

Recovered verbatim from the lead session transcript (agent hand-back); not written to a file at the time.

PR #762 cold delta review (Block 6 analysis re-pin r2). Verdict: PASS-WITH-NITS. No blocking defect. AIR-QUIET.lock was absent; I ran no tests and opened no custody or Block 6 output path.

1. (OK) The code change matches RL-142 §2 item 2 byte for byte. `git diff 3551e1a7d aaa2f3086` touches only `scripts/independent_recompute_b6.py` (one line becomes two) and `tests/independent_recompute/test_block6.py` (additions only). The hash moves from 90e22603…5759 to 4a9f5944…11ea. The checker is unchanged at 634c991c…: it lives at `joulewise/b6_analysis_check.py`, not under `scripts/` as the brief said.
2. (OK) The fix is correct and complete.
   - `block5_quantities` (RC:998-1030) makes six key families: reported/T, floor/T, dominance/T/…/R, dominance/T/…/comparative/R_cm, contrast/…, and lines/whole_machine/T.
   - The two clauses cannot both match one key: clause 1 needs the second segment to be the tag, clause 2 needs it to be "whole_machine". The tags are distinct and GAMMA's code path is untouched, so no key can land in two packs.
   - No other `lines/<scope>` family comes from Block 5.
   - The only program caller is `block_lines` (RC:1051). The probe snippet is the only other user.
   - The checker reads the unfiltered keys (CHK:154-159). After the fix, the side-by-side delta covers every finite Block 5 key.
3. (Low, residual) `tag_of` (RC:850) falls back to `str(model)` for a model outside MODEL_TAG, and that key then belongs to no pack. The new b5-probe `unassigned` hold now catches this case.
4. (Low, pre-existing, out of scope) The whole-machine loop (RC:1027-1030) maps every non-p42 cell id through `contrast_key`. Any id without "decode" becomes prefill-p2048, so a third cell would silently overwrite one. The checker uses the same keys and would not notice. The four section10 names point to exactly four keys, so this is fine for now.
5. (Nit) Test strength.
   - `test_pack_filter_keeps_each_packs_whole_machine_keys` catches partial regressions: a missing phase, a fix for only one pack, a filter that ignores the tag (other-pack check plus exactly-one owner), and GAMMA leakage.
   - The block test catches the reverted fix at `failures == []`. It does not assert the "eight names" from the ruling's mutant spec; that rests on the builder's claim.
   - Alone, the block test would miss a filter that ignores the tag (the extra rows from Block 5 only have delta None on both sides). The unit test covers that, so the pair is adequate.
   - sd is checked only indirectly, through the checker's section10 inside `failures == []`.
6. (Nit) The repro's "fixed" function (`repro.py`:23-27, `tag in k.split("/")[1:3]`) is broader than Fable's text. Its exit-0 result therefore does not validate the pinned text; the PR's block test does.
7. (OK) Tools branch.
   - The new hash is the same in `b6_real_run.py`:62 (PIN_TABLE), `b6_structure_probe.py`:41 (EXPECT_PROGRAM_SHA256) and `test_b6_real_run.py`:382. No stale 90e22603 remains in tools code; it appears only in comments.
   - The cherry-pick b2376e6c4 is byte-identical to aaa2f3086 for both files (empty diff), and the tools branch's base program was 3551e1a7d's.
   - The b5-probe hold order is right: total=0, then unassigned (exit 5), then predeclared (exit 5). The `by_pack != PREDECLARED_BY_PACK` dict comparison is exact.
   - The tools tests exercise both the pre-r2 and r2 filter texts.
8. (Low) In the tools, `--predeclared` is opt-in (`b6_release_record.py`:395). The records file's E2 step does pass it.
   - `unassigned` cannot detect a key kept by two packs; only the `--predeclared` count comparison would.
   - `block5_checks` (`b6_structure_probe.py`:508) and release condition 4 compare the total only, not per pack. Neither checks that the `--block5-expected` file came from r2 with `--predeclared`.
   - The failure is safe: passing the old 44 file makes the check depart and hold.
9. (Medium, process) RL-142 §2 item 5 requires names-only comparisons (a) gate r2 against gate attempt 2 and (b) dry r2 against dry 1. The records file has no commands or tool for either, and I found none in scratch. §17-R13's sentence "No other printed value changes" depends on (b). Build and review that tool before the dry run, or the hold rule has nothing to apply.
10. (Info) Release condition 3 fails unless every `*/record.json` under RUN is in the ledger. The first attempts (gate, gate-2, dry) must all be ledger rows.
11. (Nit) There are three blank lines before `if __name__` in `test_block6.py` (around 963-965); this is cosmetic.
12. (Nit) The R3 table's line numbers are off by one after RC:1037 (records open point 2). The probe is unaffected, but the published table would be stale.

Nothing found would make the r2 gate or dry run refuse wrongly. Finding 9 is the only gap that could leave the release record's claim without support.
