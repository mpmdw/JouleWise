# Reader report, PR #772 delta (RL-147 changes)

Reader: Sonnet 5.5 reader seat (separate from the fill seat), for the laptop lead
Time: Fri Nov 13 19:46 PST 2026 (from `date`)
Head read: `f813150c0` in `/Volumes/JW-EXT/jw-wt/b6-paper-fills` (read only). First-pass head was `a2563016e`.
Own code (python3.13 -I): `/Volumes/JW-EXT/scratch/b6-rr3/d1.py` (row re-read), `d2.py`/`d3.py` (section 2 sets), `d4.py` (manifest vs delta), `d5.py` (LOADSENS/BATT), `d6.py` (derived rows), `d7.py` (presence), `d8.py` (sweep). `fill_check_b6.py` was not run or imported.

## Inputs by hash
- `dry-r2/restricted.json` `92e67c38...c14bb`: matches.
- Block 5 `recompute.json` `c06ee7c8...cacc`: matches.
- Block 5 catalog `flag_catalog.json` `5d77c725...ee8d`: matches.
- Block 6 catalog at tag `b6/analysis-r2`: `b5bce6c6...a42a`, equals the release record's `catalog_sha256`.

## 1. Delta manifest (`fill_keys_b6_delta_rl147.tsv`, 219 rows: 167 new or changed, 52 removed)
New or changed: re-read from the source file by key; raw value equals source; printed text follows the rounding rule (nearest for estimates and operands; outward for ends; up for floor gate, edge-shift and the other limits, RL-147 §3; Block 5 R_cm of 1.7B prefill prints 1.99975 = 1.9997482608... at 5 decimals nearest); printed text present in the paper at the head.
- Rows checked: 167. Agree: 167. Disagree: 0.
  - 118 key-by-key rows passed the automatic check.
  - 21 rows are the carried-code record rows (9 x `code.executed_differs_from_sealed`, in both P1-B6-SIDEBYSIDE and P1-B6-CARRIED, plus the r2-beta `neg8.screen_failed` conditions, the r2-gamma midpoint reason, and the r2-beta/r2-gamma entries): all agree with section 2 below.
  - 28 derived rows done by hand from the source: the 4 edge-shift min/max rows (12 Block 6 cells 6.451 / 11.122 -> 6.45 (down), 11.13 (up); 4 Block 5 cells 6.797 / 12.172 -> 6.79, 12.18; the p42 cells are not in either set); the catalog count 32; `neg8/verdict` passed for all nine; the WM-DEF constants (source text `+/-2 samples at 50 Hz` and `.2 * ... + .8 * ...` present in `independent_recompute_b5.py` at `6e6d1b18a`); the cross-session count of 7 false of 12 (6 for 8B, 1 for 1.7B r1-gamma prefill); min and max |delta| 0.352 / 0.549 (8B) and +0.372; the percentages 0.2, 0.4 and 1.4; Block 5 cross-window -0.422 (differed) and -0.261 (agreed); the 8B absolute floor min/max and Block 5 values and the min/max session deltas 1.69 and 3.23; the `0.175` text row; the count of Block 5 independent-corner R at least 2 (8 of 8); the contention rows (0 of 12 floor cells computed; contrast n from 0 to 4); the replication session count 3; and the 2 rows that cite my first report ("Rows checked" and "Agree", 1,417 each: my first report says exactly that).
- The 36 LOADSENS and BATT rows (18 each): for every cell and contrast the load-sensitivity and battery-assist estimate equals the registered estimate exactly (mean_j or dbar_j), with 0 units restored (load) and 0 removed (battery), by stratum. Agrees with the two new labelled lines ("equals the registered estimate in each of the 12 floor cells and the 6 contrasts").
- The floor-gate rows (Block 5 10.18, 8.84; sessions 7.79, 7.21, 6.96 and 7.98, 7.79, 7.79) round up correctly.

Removed rows: 52 listed.
- 51 of the 52 are the same keys and values re-listed among the new rows (d-bar and its intervals and decision interval, contrast n, `neg8/verdict`); their printed text is still in the paper and unchanged in value, only the cell label changed ("computed and compared (decision 6 (a))" is now "computed and compared"; the n and verdict now print in Table 6a). I compared the old and new full manifests: the real net change is 1 row removed and 118 added; the delta's `removed` list over-counts by 51.
- 1 row is really replaced: Block 5 R_cm 1.7B prefill, old printed `1.9997` (4 decimals), now `1.99975`. The old text is gone from the paper (no standalone `1.9997`); the new text is present.
- Two rows are in the full manifest but missing from the delta list: `P1-B6-DOM` 8B decode comparative R, r2-beta 1.3108 and r3-beta 1.6865. Both agree with source (1.31079 and 1.68648). The delta manifest should list them.

## 2. RL-147 §2: the three sets (own code, from the two sources)
- 32 codes with `effect == EXCLUDE_WINDOW` in Block 5's catalog (`5d77c725...`): confirmed, 32.
- Still excluding in Block 6's catalog (`b5bce6c6...`): 7 codes: `calibration.capture_battery_pair_failed`, `calibration.capture_battery_span`, `calibration.capture_battery_unmeasured`, `cell.below_minimum`, `clock.step_overlap_calibration`, `records.source_changed_during_harvest`, `roster.no_science_bundles`. The other 25 are DISCLOSE in Block 6.
- Per session, set of `code` in `sessions.<sid>.copied_disclosures.families.block5_codes_carried[0].record` (JSON lines; 145 to 190 records per session) intersected with the 32:
  - all nine sessions (r1/r3/r4-alpha, r1/r2/r3-beta, r1/r2/r3-gamma): `{code.executed_differs_from_sealed}`, two records each, both window level (one has attempt "1", the other 1). 
  - r2-beta: additionally `neg8.screen_failed`, one record, window level: `decision: failed`, reasons `bracket_not_passed`, `neg8_conditions`, conditions `neg8_bracket_reference_invalid`, `neg8_drift_bound_underived`, `neg8_idle_sub_drift_bound_underived`.
  - None of the 7 still-excluding codes occurs in any session.
- `neg8.midpoint_lost` (not one of the 32: DISCLOSE in both catalogs): one record, r2-gamma only; reason `contention.request_overlap`, slot midpoint, reference counts start 3, midpoint 0, end 3. `neg8.n_mid` is 1 in all nine sessions, so the drift screen used the midpoint. No other session has the code.
- Union of the 32 that occur: `{code.executed_differs_from_sealed, neg8.screen_failed}`.
- Match with Fable's expected sets: yes, on every point (the two codes, the one window-level code in all nine, `neg8.screen_failed` in r2-beta only, none of the 7, `neg8.midpoint_lost` in r2-gamma).
- Paper check: the CARRIED paragraph says one of the 32 is carried by all nine sessions (`code.executed_differs_from_sealed`), the r2-gamma lost-midpoint rule is disclosed as dropped, and r2-beta's `neg8.screen_failed` is disclosed and not listed as carried, with the three conditions named and "the registered drift screen passed in that session, as in all nine" (verdicts: passed, nine of nine). All agree. Table 6a's new column "Primary-block codes carried" shows `code.executed_differs_from_sealed` in all nine rows, with "lost-midpoint rule (dropped)" added to r2-gamma only, and nothing about `neg8.screen_failed` in r2-beta's row. All agree. (Table 6a kept units also agree with source: decode/prefill n 10 and 8, 10 and 9, 10 and 10 for the three gamma sessions.)

## 3. Sweep of the new prose for numbers with no manifest row
Paragraphs read: abstract/intro replication clause, "What the replication shows" (between sessions, floors), dominance (c) sentence, contention (d), WM-DEF definition, the LOADSENS and BATT lines, Table 6 floor-gate rows and caption, Table S9 paragraph. Numbers not in the manifest, with what each is:
- Abstract Block 5 values (51.21 [48.92, 53.49]; 26.25 [23.32, 29.19]; 198.36 [195.23, 201.49]; 128.28 [125.19, 131.38]; 6 of 10 and 5 of 10 planned quads): not B6 numbers. I checked them against the Block 5 output: all agree (cell means; interval ends outward; d_k lengths 6 and 5; "10" is the planned quads). These have no row in the delta or B6 manifest; they belong to the Block 5 manifest.
- `0.175`, `3.713`, `14.531`, `10.818`, `5.432`, `0.54`: inside manifest text rows (timing_regime_label, contention label). Covered.
- `50`, `0.2`, `0.8`: WM-DEF constants; manifest "constant" rows cite the source text. (`50 a second` is the meter sample rate; "median over 50 kept runs" are measured counts.)
- `12` (cross-session comparisons, floor cells), `6` (contrasts), `5` ("5 required", registered minimum quads), `3` and `9` (sessions): constants or counts checked by me (12 comparisons: 3 gamma sessions x 2 models x 2 phases; 7 differ; 12 floor cells; 6 contrasts).
- `72` ("8 families in 9 sessions: 72 of 72 rows hold their disclosure", and the P1-B6-DISCLOSURES placeholder text): not checkable from the released outputs; 8 x 9 = 72 is arithmetic only. UNMATCHED, same as in the first pass.
- `13 November 2026`, `256`, `3,296` (repeated), `945`: constants or repeats, as in the first pass.
- "the replication's sessions confirm it would have removed most of the data" (contention (d)): a quantitative claim with no number; no row. Wording only; I could not tie "most" to a figure (0 of 12 cells keep the minimum; contrasts keep 0 to 4 quads of 5).
- Paper sentence "re-read by key by a separate reader (1,417 of 1,417 printed elements agreed)": the count is from my first report, true of head `a2563016e`. RL-147 §7 item 3 says it becomes the new total after this re-read. For the lead: the current full manifest has 1,534 rows (1,417 - 1 removed + 118 added); of those, 1,416 were read in pass one (some printed positions have since changed) and 118 in this pass, plus the 51 re-listed rows. If the sentence is to name a new total and report digest, that is the number to use; the digest of this report is not self-referential, so the lead must hash it after I write it.
- One placeholder remains: `P1-B6-DISCLOSURES` (follow-up PR per RL-147 §10). Nothing to check.

## Disagreements
None.

## What I could not check
- Which cell or sentence each of the 167 new rows lands in; I checked value presence (with number boundaries) in the paper at the head, and read each new paragraph, but did not align every row to its cell.
- The rounding rule for "up" on `edge_shift_sensitivity` and the floor-gate rows is taken from RL-147 §3 and the table caption; I did not open RL-147's own text beyond §2, §5 and §7, and did not reread RL-60.
- The "72 of 72" disclosure-copy count (needs the disclosure reader's record).
- The collection checkout cite in the CARRIED paragraph (RL-147 §12: "its own registered checkout", registration §7); I did not read §7 line by line.
- Table S9 and the first-pass sentence digests were not re-derived in this pass (structure.json unchanged).
