# Paper 1 seat 6: Opus re-derivation of the corrections of fact

Date: 2026-11-10 23:13 PST. Reviewer: Opus 5.5 (re-derivation seat under RL-24 seat 6).
Branch reviewed: `docs/2026-11-10-paper1-corrections` at `89d0ae338`. Base: `origin/main` = `a9dd335b3`.
Checklist under review: `docs/paper/paper1/CORRECTIONS-2026-11-10.md`. Builder's report:
`docs/run_reports/2026-11-10-p1-seat6.md`.

**Verdict: ADMIT-WITH-FIXES.** 30 of the 32 logical hunks re-derive as true, as corrections of statements that
were wrong, and as within RL-5's scope. Two corrections bring in new inaccuracies that must be fixed before
merge (R-1 and R-2 below). There are also two small fixes (R-3 and R-4) and one precision note for seat 9 (R-5).
Nothing was filled. No outcome word, no realised branch and no Block 5, Block 6 or BYTES number entered the
manuscript. No section moved.

## Method and access

- Every cited source was opened at the cited ref. The sources: RL-4(viii), RL-5, RL-7(a, f) and RL-24, and the
  paper audit (§2.1 C-1 to C-11, §4.1 to §4.2, §5 F-01 to F-23, §6), at `origin/audit/2026-11-10-fable`
  `24b549f25`. The 11-07 audit's P1 to P12 and Decisions 9 and 10 at `origin/research/2026-11-07-b5-release-to-paper`
  `79d8e2dbb`. `bytes_pack_v1.md` at `origin/lane/2026-11-07-bytes-stage1` `912cf8c3a`.
- At base I read: `SEAL_RECORD.md`, `l9-rulings/RULING.md` J5, `DEVIATION-LOG.md` (DLE-0 to DLE-10 headings,
  DLE-0, DLE-1, DLE-3/D5b, DLE-5), `decision_log.md` D-078, D-178 and D-188 to D-190, `recompute_bars.json` (every
  family), and `LEAN-COVERAGE-AUDIT.md` §2 to §4. Also `registration_block5.md` (1518-1547, 2600-2603, 3946-3949,
  4851-4854), `analysis_plan_block5.md` §9, §10 and §12, `block6_replication_DRAFT.md` §11.2, §12.3 and S-13,
  `RUN_STATE.md` items 33, 59, 71, 83, 108, 181 and line 902 and the BY-EXT-1 status line,
  `joulewise/detection_floor.py` (1525-1540, 1810-1842) and `joulewise/analysis_engine/claims.py`
  (142-205, 330-385).
- Read only from the worktree and git objects. I did not read custody, night, archive or restricted paths, and
  I read no Block 6, BYTES held-out or v4 data. Block 5 release text was read only where the paper audit quotes it.

## Diffs

- **Against `paper1/blind-draft-2026-10-27`.** The tag peels to `a1a5029fb` (committed 2026-10-27T22:05Z). Under
  `docs/paper/paper1/`, `git diff paper1/blind-draft-2026-10-27 origin/main` is empty, so the branch-against-tag
  diff of the paper directory equals the branch-against-main diff. The repository-wide tag diff is about 9,100
  files. That comes from `main` moving since 10-27, not from this branch.
- **Against `origin/main`.** 10 files:
  - `paper1.md`, `build_fill_index.py` and the regenerated `fill_index.md`;
  - `build_figures.py` and the regenerated `fig_p1_pipeline.svg`;
  - the Tier B and Tier C variants;
  - the new checklist and two run reports.
- **Checks.** `git diff --check` is clean. Section headings and their order are identical to base.
- **Regeneration.**
  - Running `python3 -I docs/paper/paper1/build_fill_index.py` from the repo root printed `235 214 218 173`. The
    tree stayed clean, and `fill_index.md` SHA-256 `579a8276…f7d` equals the committed file.
  - Placeholder ids were compared by occurrence count against base, in `paper1.md` and all five variants, and in
    the index's id column. The only removed id is `P1-BYX-RESULTS`, one occurrence. RL-5 item 5 requires that
    deletion ("`P1-BYX-RESULTS` is deleted"), and the paper audit §4.1 repeats it.
  - `build_figures.py` regenerates all five SVGs byte for byte; only Figure 5 differs from base.
  - `tests.test_paper_build` passes: 5 tests, 2 renderer tests skipped.

## Per-hunk verdicts

C = confirmed (the new text is true, the old text was wrong or overstated, and the change is in scope).
C\* = confirmed with a required fix listed below.

| Hunk | Verdict | Re-derivation |
|---|---|---|
| H01 abstract | C | COVER §2-§4: seven families are not recomputed, and the recompute takes selection, anchors, calibration fits, flags and NEG-8 membership as stored inputs. "Every headline number from the raw records" overstated this (P3/C-3). Block 6 is collected and sealed (PA §2.4), so the old "and a replication" was wrong to read as a result (C-11). |
| H02 abstract and contribution 3 | C | `bytes_pack_v1.md` roster has 3 fit models and 7 held out (4 dense, 3 MoE), so "ten" was wrong (F-17, RL-5(5)). The commitment is a requirement, not done: PA §4.2, F-08 and RL-7(a). |
| H03 §1.2 | C\* (R-2) | Tag commit 10-27 is after Block 5 collection closed (10-12) and before release (11-08). P5 and C-8 hold, and "recomputed ... before release" was also wrong (DLE-1(b) runs at release). But see R-2: the sentence is no longer true of all branch prose. |
| H04 §1.3 item 2 | C | C-10 lists §1.3 item 2 as an occurrence of the unconditional gloss. P11 shows that gloss is false for `not_estimable` and for `floor_transport_inapplicable`. "Remain sealed" matches PA §2.4. The change from "defined before any data" to "before replication collection" also holds: the B6 registration was added 2026-10-14, after Block 5 data existed. |
| H05 §3.6 floor gate | C | J5(a), (b)2-6 and (d), and item 33(b). `detection_floor.py:1534-1536` gives `drift_widened_guarded_floor_j = guarded + allowance`, and lines 1818-1838 give `floor_gate_j = max(abs, cmp)` of those values. The allowance is the whole gross allowance, once per form, after the guard. It is absent from the point, corner, dominance and attribution floors. D carries GAMMA's own allowance (J5(b)8). The old text left out the allowance (F-03). The ruling date is 2026-10-12 and the code was not changed: confirmed. |
| H06 §3.7 terms | C | RL-4(viii) and F-10. The new paragraph defines the three terms only and gives no branch. |
| H07 §4.3 seals | C | SEAL_RECORD: Erratum 1 is the second seal (H_claim `c27485347`, seal `be6525e5a`). Addenda 3 and 4 hold Errata 2 and 3, each written before the arm of the attempts it governs. |
| H08 §4.4 close | C | PA §2.4 and item 59: Block 6 closed 2026-10-21, 9 of 9 counting, 3 per pack. These are structure facts only. |
| H09 §4.5 mechanism and change list | C | `registration_block5.md:1546-1547` makes `code.executed_differs_from_sealed` a harvest finding that removes the window. §4.7 at 2602 says the only identity refusal at arm is OS build plus machine model. Lines 1522-1525 cover the harvest fault on a registration-digest mismatch. Each list entry matches its DLE, D-188/189/190 or L9 source (DLE-3 D5b is blind and post-collection, P7). The cited file paths exist (`ERRATUM-RULING.md`, `ROSTER-RULING.md`, `2026-10-20-magistrate-6cff3515/L9-RULING-ADDENDUM.md`). |
| H10 §4.6 structural read | C | R2P Decision 10(i), and DLE-3's Source line: the lead ruled status and reason words structural, then D5b. |
| H11 §4.6 release order | C | DLE-1 says "The numbers that print are the dry run's L9 outputs, which (a) verifies byte for byte". The old text "registered analysis ran after it" and "replication numbers were released" were both wrong (P2, C-5, C-11). |
| H12 §4.7, P1-RECOMPUTE | C | Every bar was checked against `recompute_bars.json`: joule, watt and ratio families max(1e-6, 1e-6×\|v\|); `contrast_p` and `rho` 1e-6 absolute; `b_op_s` 1e-6 relative; `count` exact; `window_edge_s` 1e-6 s. It is fixed blind (item 83 ruling 1, laptop lead; DLE-0). Block 6 S-13 matches `block6_replication_DRAFT.md:1206` (§12.3). The seven gaps match COVER §2 items 1-7. The load line is uncompared (COVER §3). |
| H13 B-share | C | `analysis_plan_block5.md:771-772` (§12): unregistered analyses are exploratory only (P9, RL-5(6)). |
| H14 Table 3 caption | C | J5(b)2-3 and (e). The old caption, "the larger component, never their sum", left out the allowance. |
| H15 §5.5.4-5.5.5 gloss | C\* (R-2) | `claims.py`: `effect_not_above_floor`, `deterministic_bound_obscures_direction` and `floor_transport_inapplicable` are in `_NOT_RESOLVABLE`, and `floor_artifact_invalid` is in `_NOT_ESTIMABLE`, which takes precedence. D5b maps binding failures to `floor_artifact_invalid`. D-189 says non-issuance is not an empirical negative. P11 asks for a gloss table with a branch per code. The old 5.5.4 sentence (tag line 806) is the one P11 cites. |
| H16 §6.4 and §6.5 | C | `RUN_STATE.md:902` drops Qwen3.8-27B "under its registered rule ('extension sessions are dropped first')". The BY-EXT-1 line: Nemotron had no MLX build that the pinned mlx-lm loads. `P1-BYX-RESULTS` is deleted and `P1-BYX-STATUS` is kept as a structural slot. |
| H17 §7.1 and Figure 5 caption | C\* (R-1, R-4) | RL-5(3) and P4: item 108 shows dry runs with custody under the user account, and `registration_block5.md:4853` says "kept by rule, not by the file system". The three false claims are gone. But the new text calls the measurement-Mac agent the "lead" (R-1). |
| H18 §7.2 items 1, 2, 5, 7 | C\* (R-2) | Same sources as H09, H12 and H03. |
| H19 §7.3 first bullet | C\* (R-1) | RL-5(3) and C-7. The deleted clause "a shell guard refuses agent commands while a session is active" has no source I could find in the repository. Removing it adds nothing false. Seat 9 may restore it with a source. |
| H20 §8 | C\* (R-2) | Same sources as H16 and H03. |
| H21 §9 first paragraph | C | C-2 and C-11. No result is stated. |
| H22 §9.C and closing | C\* (R-2) | RL-5(5) removes the unconditional sentence, and P5 covers the closing sentence. |
| H23 fill-index sources | C\* (R-3) | Every source string agrees with J5, DLE, BARS, COVER, SEAL and EXT, except one wrong section number (R-3). |
| H24 Figure 5 | C\* (R-1) | The labels follow RL-5(3), P2 and P4, but one label repeats the "headless lead" error. |
| H25 Tier C abstract | C | Same as H01. |
| H26 Tier B header | C | F-20 cites items 349 and 898. RL-24 sets the scope freeze at 5 December. |
| H27 Tier B abstract | C | Same as H02. |
| H28 Tier B per-model rule | C | `bytes_pack_v1.md:280`, RL-7(f), and main draft §6.3 at 1101-1104. Two deletions were not needed: the sentence "Because B dominates ... one pass loses little precision" was supported by registration line 280, and the limitations pointer to the replication's between-session summaries was also supported. Both are minor scope over-reach and do not block. |
| H29 Tier B extensions | C | Same as H16. |
| H30 §6.3 commitment | C | PA §4.2 ("not yet true in a checkable sense"), RL-7(a). |
| H31 availability | C | Synthesis P12. Only the required fields are named; nothing is filled. |
| H32 worked example | C | `bytes_pack_v1.md:297` uses the pilot's four-decimal b and R ("the 30B-A3B's pilot regressors (b = 1.9378 GB ...)"). F-22: the printed three-decimal table reproduces the numbers only to about five significant figures. The synthetic numbers are unchanged. |

Untagged hunks were checked as well. The §4.4 replication-word sentence ("before replication collection") is
justified, as under H04. The §6.5 template comment and the run reports are process text. All were in scope. No
hunk is unjustified.

Checklist mappings were spot-checked against their sources: the P1-P12 table, C-1 to C-11, the PA §4.2 rows
and F-01 to F-23. The no-change and handoff dispositions are consistent with RL-24's seat split: seat 9 owns
§7.3, seat 10 the title and structure, seats 4 and 12 the numbers and fills, and seat 8 the registry and DLE
entries. RL-5(4)'s full §7.3 rewrite is correctly deferred to seat 9 (RL-24 assigns RL-5 items 3 and 4 there).

## Required fixes

**R-1 (must fix): new false identification, "headless lead".**

- **Where.** `paper1.md:1305` ("a headless lead agent runs on that laptop and arms collection"), `paper1.md:1365`
  ("the headless lead runs between sessions and owns arming"), and the Figure 5 label in `build_figures.py`
  ("headless lead between sessions", with the regenerated SVG).
- **Why it is wrong.** §7.1 (`paper1.md:1296-1297`) defines one **lead** session as the one that "decomposed the
  work ... checked every change before it merged and kept the project's record". The agent on the measurement Mac
  is a different session: C-7 calls it "a headless agent, the magistrate". `RUN_STATE` item 181 separates the
  "Laptop lead" from "the magistrate [who] owns measurement orchestration on the MacBook Pro". RL-5(3) says only
  "a headless agent".
- **Fix.** Use "a headless supervisory agent", or the equivalent, in all three places. This matches §7.3's
  existing "a headless supervisory session". Then regenerate Figure 5.

**R-2 (must fix): the provenance sentence is no longer true of all branch prose.**

- **Where.** Four places say "the draft's additional branch prose was written before release, at commit
  `a1a5029fb`": H03 (`paper1.md:95`), H18 (`:1351`), H20 (`:1457`) and H22 (the closing sentence).
- **Why it is wrong.** This seat rewrote Block 5 branch prose after the 2026-11-08 release, in a seat that was not
  blind to Block 5. It changed the branch 5.5.4 gloss sentence and its FILL description. It added the 5.5.5
  sentence and the four-row reason-code table. These branches are not the realised ones, so no outcome was
  steered. But the provenance claim is now false as worded.
- **Fix, part 1.** Qualify the claim, for example: "... at commit `a1a5029fb`, after primary collection; factual
  corrections to non-selected branch glosses were made after release on 10 November 2026 and are listed in
  `CORRECTIONS-2026-11-10.md`." Put this in §1.2 at least, and point the other three sites to it.
- **Fix, part 2.** Rename the table column "Fixed interpretation" (`paper1.md:892`) to "Interpretation". These
  glosses are seat 6's draft wording, not registered fixed sentences. Their verbatim and registered status
  belongs to DLE-9 and seat 8.

**R-3 (small): wrong section number.** `build_fill_index.py`, `P1-B5-B-SHARE` source: "analysis plan §10" should
be "analysis plan §12 (lines 771-772)". §10 is the analysis-plan rows table, and the exploratory rule is in §12.
Regenerate `fill_index.md`.

**R-4 (small): unclear reference.** `paper1.md:1306`, "under the same account", has nothing earlier in the
sentence to be the same as. Suggested wording: "under the user account that holds custody".

**R-5 (precision note, seat 9).** "arms collection" and "owns arming" are present tense in a passage about the
study's collection. C-7 dates the magistrate's ownership of arming from item 181 (2026-11-06), after Block 5 and
Block 6 collection had closed. RL-5(3)'s wording supports the sentence as an interim text. Seat 9's rewrite from
the record should date it.

## Other observations (not blocking)

- The `FACT Hxx` HTML comments are invisible when rendered. Strip them at seat 10 or at fill.
- The builder's report (`docs/run_reports/2026-11-10-p1-seat6.md`) and
  `docs/run_reports/interp-energy-desk/p1-seat6-sol-report.md` both say the commits are not pushed. They are now
  on origin. The second file also links to absolute `/Volumes/JW-EXT/...` paths. Neither affects the paper.

## New false claims introduced

R-1 (the measurement-Mac agent called the "lead") and R-2 (the provenance sentence, falsified by this seat's own
post-release edits to branch text). R-3 is a wrong locator in the fill index, not in the manuscript. No other
correction introduced a falsehood.

## Overall

**ADMIT-WITH-FIXES.** Apply R-1 to R-4 and regenerate the fill index and Figure 5. The research lead can then
admit without another re-derivation: the fixes are wording only, and they touch no source claim re-derived above.
