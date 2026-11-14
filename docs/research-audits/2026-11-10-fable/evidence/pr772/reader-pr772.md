# Reader report, PR #772 (Block 6 paper fills)

Reader: Sonnet 5.5 reader seat (separate from the fill seat), for the laptop lead
Time: Fri Nov 13 19:19 PST 2026 (from `date`)
Target: branch `paper/2026-11-13-b6-fills`, head `a2563016e`, worktree `/Volumes/JW-EXT/jw-wt/b6-paper-fills` (read only)
Reader code (mine, not the fill seat's): `/Volumes/JW-EXT/scratch/b6-rr3/rr3_reader.py`, `rr3_b.py`, `rr3_c.py`, `rr3_d.py`, run with `python3.13 -I`. `fill_check_b6.py` was not run or imported (I read its docstring and rounding-rule comments only, to learn the stated rule).

## 1. Input hashes
- `restricted.json` sha256 `92e67c38...c14bb`: matches the required value.
- `public.json` sha256 `c2b5c409...107f8`: matches the release record (`outputs_sha256.dry.public` and `outputs_sha256.dry.public`, origin/main).
- `structure.json` sha256 `18a129f218d002516cc2bbf2a13243ea7e977ce90328e63c29a46bb78132d8e5`. The release record carries no digest for it. Internally its `digests.restricted_file` and `public_restricted_sha256` both equal the restricted hash above, and `digests.public_file` equals the public hash. Its `digests.program_sha256` is `4a9f5944...2ea11`, the same as the release record's `scripts/independent_recompute_b6.py` (r2).
- Release record restricted digest for the dry run: `92e67c38...` (same).

## 2. Manifest rows (`docs/analysis/b6/fill_keys_b6.tsv`, 1,417 rows)
Each row was re-read from the source file by key path. I compared the manifest raw value with the source value, recomputed the printed text under the rule, and looked for the printed text in the B6-added lines of paper1.md (the markers are gone after filling, so "marker location" is taken as the PR's added lines; see section 7).
Rounding rule applied (RL-52/RL-60): joules = 2 decimals or 3 sig figs, whichever shows more digits; per token 4 sig figs; dominance R 4 decimals; magnitude ratios 3 decimals; shares 2 decimals; estimates and difference operands to nearest, interval ends outward, sd and limits up.

- Rows checked: 1,417
- Agree: 1,417
- Disagree: 0

How the 1,417 break down:
- 1,394 rows passed the automatic check (key path exists, raw equals source, printed equals the rounded value, printed text is in the added paper text).
- 3 rows read `attempts.jsonl`. I counted that file directly: `/Volumes/JW-EXT/b6-custody/attempts.jsonl` (sha256 `1203f37b...9c32`), 9 rows, 3 each for alpha, beta, gamma, all `counting`, cause null. Agrees with the paper's "3 counting sessions of the 3 targeted, from 3 attempts" for each pack.
- 20 rows are derived or non-scalar, and the automatic pass could not take them. I checked each by hand:
  - 8 "compared minus both_null" rows (calibration 9, contrast 30, inclusive 144, neg8 27, replication 2, run_phase_energy 2,892, side_by_side 48, summary 144): all equal compared minus both_null from `block.option_c.comparator.classes`.
  - 5 term-7 total rows (compared 3,296; both_null 0; first_program_only 945; failed 0; unmatched 0): my sums over the 17 class blocks give the same.
  - 1 row, class count 17: `len(classes)` is 17.
  - 2 REPWORD rows, session count 3: `len(sessions)` is 3 for each phase.
  - 3 DOM "failed" list rows: the printed names are a faithful mapping of the source lists, and they match the paper sentence for r1-gamma, r2-gamma and r3-gamma.
  - 1 `block.option_c.families` row: source values are right (e.g. harvest_energy 2,892, section11_replication 2), but the printed text is a JSON dump that does not appear in the paper. See note A below.
- Word/text/list rows (110 words, plus mapped words such as `1_same_round` printed as "same round", `below_registered_minimum` as "below registered minimum", `direction_supported` as "direction supported") match the source after the mapping.
- The manifest TSV quotes JSON values Excel-style; I parsed it with default CSV quoting. Nothing was wrong with it.

Note A (not a number disagreement): the `families` row is a manifest row with no place in the paper. Harmless, but the manifest overstates what is printed. Likewise the manifest has two keys for one printed cell in many rows (a `side_by_side|...|sessions|rX` key and the `sessions|rX|quantities|...` key; also the WAITED/WM duplicates), so row counts exceed distinct printed cells. Presence is checked per value, not per cell position: for each printed text I confirmed it occurs in the added lines, and the multiplicity shortfalls (133 distinct values where rows exceed text occurrences) were all of this duplicate-key kind in the cases I inspected (e.g. 0.1001, 101.67, 1.8708). I did not align every row to its exact table cell.

## 3. Disagreements
None.

## 4. Unmatched numbers (sweep of the B6-added paper text against the manifest)
Method: take the numbers in the lines this PR adds to paper1.md, strip labels (session ids, "1.7B", "8B", Table and section numbers, "(2,048)", dates, RL numbers, 10^k exponents), then compare the multiset of remaining numbers with the manifest's printed values (leading "+" ignored). Every number with a decimal point or with 3 or more digits that is not in the manifest, and the leftovers among small integers, were read in context.

Numbers with no manifest row, and what each is:
- `14.531`, `10.818`, `3.713`, `0.175` (J/ms): inside the P1-B6-SIDEBYSIDE `timing_regime_label` text row, which is a manifest row (the whole sentence). Covered.
- `5.432`, `0.54` (w, c_q): inside the P1-B6-CONTENTION `label` text row ("registered outside-processor rule (w = 5.432 J per CPU-s, c_q = 0.54 CPU-s)"). Covered. Registration §11 states w = 5.432.
- `13` (S-13), `12.3` (§12.3 item 4): registration constants. S-13 and §12.3 item 4 in `block6_replication_DRAFT.md` (sha256 `7243a2ba...3324ead`, the release record's registration hash). Bars in Table S9 agree with S-13 as made definite in §17-R2: J 5 decimals (5x10^-6), ratios 4 decimals and p 4 decimals (5x10^-5), per token 8 (5x10^-9), b_op 6 decimals (5x10^-7 s), run phase 1 mJ.
- `256` (SHA-256), `15` (runbook step 15), `5` ("registered minimum of 5 quads", "5 or more quads"): constants. The minimum-quads figure is registration §11.4 (5 kept units) and the §9 contrast minimum.
- `13 November 2026`, `§17-R13`, `r2`, "four" whole-machine values: registration §17-R13: dated 2026-11-13, "four side-by-side differences", tag `b6/analysis-r2`, program sha `4a9f5944...2ea11`. Cited and consistent.
- `3,296` and `945` appear 3 and 2 times: paragraph and Table S9 Total row; one manifest row each. Same fact repeated.
- Small integers in the leftover count (1-9 slightly exceed manifest rows): labels such as "decision 6 (a)", "Table 6a", "n = ..." counts. I spot-checked the "n = 2, 4, 3, 2, 2, 0" and "n_r / n_b" values in the contention line: the manifest holds them (CONTENTION `n_r`, `n_b`, and the gamma `n` rows), and their printed values equal the source. No finding.
- `72` ("72 of 72 family and session rows hold their disclosure"): FINDING. No manifest row, not a registration constant, and I cannot verify it from the released outputs. It is a statement about another reader's work (the "eight copied disclosure families" check). Whoever owns that reader record should confirm 72/72; this reader did not check disclosure copying (see section 7).
- "every printed value of Section 6.8 is rendered by key ... and re-read by key by a separate reader" (paper text, §S9 paragraph): a claim that this report is meant to support. It is only true if the lead accepts this report; it should not be printed before that.
No unmatched numeric result (any measured value with decimals) was found.

Still placeholders (not fills, not numbers): `P1-B6-CARRIED`, `P1-RECOMPUTE-SUMMARY-B6-MAXDIFF`, `P1-B6-WM-DEF` remain as `{{FILL: ...}}` in the B6 region. They have no manifest rows and nothing to check.

## 5. Totals check (agreement paragraph and Table S9 against `structure.json` `term7`)
- `term7.totals`: compared 3,296; both_null 0; first_program_only 945; agreeing_on_a_value 3,296. Paper paragraph: 3,296 compared, 0 failed, 0 unmatched, 0 null on both sides, 3,296 agreeing, 945 first-program-only. Agrees. Total row of Table S9: 3,296 | 0 | 0 | 0 | 3,296 | 945. Agrees.
- `term7.per_class` vs Table S9, all 17 class rows: compared, both_null, agreeing (= compared - both_null) and first-program-only (= `listed`) match for every class (0 mismatches). Failed and unmatched match `restricted.json` `block.option_c.comparator.classes` (all 0). The nine classes with compared = 0 and shown as "—" are attribution_floor, contrast_word, cross_session, descriptive, dominance, floor, lines, per_token, reported: this is exactly the set with compared = 0, and the paper names the same nine.
- Class sums, from my own addition over the 17 class blocks in the restricted output: compared 3,296, first_program_only 945, failed 0, unmatched 0, both_null 0.
- The term-7 label counts in the paper (100 single-source, 183 not independently recomputed, 24 single implementation, 8 gate-only) equal `term7.distinct_keys_by_label_kind`. `term7.result` is "pass".
- The 945 split by class (12, 42, 18, 84, 24, 39, 156, 474, 12, 84) sums to 945.

## 6. Replication-branch check (section 5.7)
Registered definition (registration §11.2): "replicated" means every counting block-6 GAMMA session gives the same outcome word as Block 5's analysed GAMMA session and the same sign of d-bar. Otherwise "not replicated" (5.7.2). If Block 5's contrast is `not_estimable` (no d-bar), "replicated" is not used (5.7.3). If GAMMA closes short, the sentence reads "short: k counting block-6 sessions of the 3 targeted" (5.7.4).

Inputs, `restricted.json`:
- `block.replication.decode`: block5_outcome `direction_supported`, block5_direction `positive`; sessions r1-gamma, r2-gamma, r3-gamma each `direction_supported` / `positive`; short false; short_sentence null; flagged_inclusive_sessions []; word `replicated`.
- `block.replication.prefill-p2048`: identical (block 5 `direction_supported` / `positive`, three sessions each `direction_supported` / `positive`, short false, word `replicated`).
- `block.short.GAMMA`: counting 3, short false, below_commitment false. `attempts.jsonl` (custody): 3 GAMMA attempts, all counting.
- Cross-check from the per-session outputs: `sessions.rN-gamma.quantities.contrast/{decode,prefill-p2048}/{outcome,direction}` are `direction_supported` / `positive` for all three sessions, and the three counting GAMMA sessions are `counting: true`.

Comparison: for each contrast, Block 5 is estimable (has a direction), the pack is not short, and every one of the 3 counting sessions has Block 5's word and sign. Branch 5.7.1 holds for both contrasts. 5.7.2 (not replicated), 5.7.3 (not estimable) and 5.7.4 (short) do not apply. The paper's choice of 5.7.1 for decode and for 2,048-token prefill, the word "replicated" in both the contrast paragraphs and the closing sentence, and "every one of the 3 counting replication sessions" are correct. The flagged-inclusive sentence ("the same ... with no session added") matches `flagged_inclusive_sessions: []` and `block.flagged_inclusive.*.added_sessions: []`. The paper's "short is false" HTML comment is also right. (The comment says "fill_check_b6.py" as its source; I did not use it.)

## 7. What I could not check
- Exact cell position: the markers were replaced during filling, so I could not confirm each printed number sits in the cell its key names. I confirmed value presence in the B6-added lines and checked S9 row by row; I did not align all 1,417 rows to table cells or sentence positions. Duplicate printed values (two keys for one cell, or the same number in different cells) can mask a misplaced cell.
- The rounding rule's own correctness for "which side of a difference counts as an operand beside a difference" is taken from the stated rule (RL-52/RL-60 as in the fill seat's docstring) and from how the 1,394 rows came out under my own implementation; I did not re-read RL-60 verbatim (it lives on `origin/audit/2026-11-10-fable`, which I did not open). Zero disagreements under that reading, including R's threshold-at-2 extra-digit rule (no R value fell in that case, as all rows agreed under plain 4 decimals).
- The recompute bars (S-13/§17-R2 print precision) were compared with the registration text; I did not open the pinned `precision.json` (it is not on origin/main under that path).
- `max_observed_difference` is not in the released outputs; the MAXDIFF placeholder stays open.
- "72 of 72 disclosure rows" and the disclosure-family copy check (the eight copied families) were not in my brief and not checked.
- The loop `attempts.jsonl` hash was not checked against the run-input document's `external.loop_attempts` digest (I counted rows only).
- I did not re-run or import anything of the analysis, and I did not open `samples.jsonl`, `process.json` or the per-session custody directories.
