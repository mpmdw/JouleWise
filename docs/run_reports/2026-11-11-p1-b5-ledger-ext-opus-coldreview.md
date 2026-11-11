# Paper 1 Block 5 ledger extension (RL-52 step 1): Opus cold review

2026-11-11 03:40 PST (11:40Z) · Opus 5.5 cold reviewer (RL-38 condition 9, RL-52) · target
`origin/analysis/2026-11-11-b5-ledger-ext` @ `61c87eb5184be9d5d8db0c73624ef34666e659d1`.
Authority read verbatim: RL-3, RL-38, RL-41, RL-42 and RL-52 in
`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
Model for the review: `docs/run_reports/2026-11-10-p1-seat4-opus-coldreview.md`.
Not a repair seat. This review changes no ledger row, no `RESULTS.md` byte, no analysis code and nothing in
custody. It adds this report and one check script that holds no data,
[`docs/analysis/b5/opus_coldreview_rl52_check.py`](../analysis/b5/opus_coldreview_rl52_check.py).

## Verdict: ADMIT-WITH-FIXES

All 881 new rows are confirmed. Every row checks against its pinned source leaf, or against an independent
recomputation, or against both. **None is refuted.** The fixes are to prose and scripts, not to rows:

- the sentence that names the one cross-session "differ" cell gives the wrong cell (F1);
- the seat-12 fill check breaks when this table lands on `main` (F2);
- the round-1 replay script fails at HEAD (F3).

F4 and F5 are presentation and scope notes for the second fill. Row 249 remains the only MISMATCH, and it is
the erratum already ruled.

**Blind status.** Block-5-aware (RL-38 condition 10). Blind to Block 6, BYTES and ALIGN v4. I opened none of
their outputs or custody, and no `night-*`, archive or other-block path. One pinned file (EXC) names a
`night-custody` harvest root as text. I did not follow it.

## 1. Custody files opened

There were six files, all inside the two RL-38 roots, and all are pinned. RESULTS.md §0 pins RC, FILL, DISC
and EXC in full. RESULTS.md §0 gives prefixes for PROJ-A and PROJ-B; seat 4's table and the extension
report's table give their full hashes, and each file is named by its own hash.

- **Before reading:** I hashed each file with `shasum -a 256` at 11:26Z, and the script hashed each again
  before parsing.
- **After:** I re-hashed all six at the end.
- **Result:** before = after = pin for every file.

| Alias | Path (relative to `/Users/edr/jw-b5-custody`) | SHA-256 (before = after) |
|---|---|---|
| RC | `release-check-final-20261108T0942Z/recompute.json` | `c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc` |
| FILL | `dry-m/dry-run/restricted/outputs/a29c6cf2…-results-fill-input.json` | `a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4` |
| DISC | `dry-m/dry-run/restricted/disclosures/77be1a3e….json` | `77be1a3ed3a851206a0762334cbdeaab5b40e83e3d9fcdbcf404da5e4d871f6a` |
| EXC | `dry-m/dry-run/restricted/finalized/analysed-attempt-exclusions-a9954365….json` | `a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46` |
| PROJ-A | `dry-m/dry-run/restricted/outputs/ed3cadb1…-projection-alpha.json` | `ed3cadb1f0ac2fc137efab3f4528702c704055ffa5bdf24399c335081570f5bf` |
| PROJ-B | `dry-m/dry-run/restricted/outputs/db6d5251…-projection-beta.json` | `db6d525129f90ef24bb46f83ab5e66283424970c743f35d322c8961f9b683e2e` |

- **Access:** I listed no directory, followed no path found inside a file, and wrote nothing in custody.
  Scratch files lived in this session's scratchpad.
- **Committed values:** the committed record carries counts, words, row numbers and residuals only.
- **Leak scan:** I scanned the new rows against about 27,600 member-level leaves. The only matches at printed
  precision are of two kinds:
  - registered extremes that are one member's value by definition (the attribution-floor minima and ρ
    minimum, maximum, median and quartiles);
  - 4-digit coincidences.
- No member array is committed.

## 2. Checks

| # | Check | Result |
|---|---|---|
| 1a | Rows 2-539 (538 original rows) and header vs `origin/main` `rederivation.tsv` | byte-identical (`cmp`). Note: `main` holds only these 538 rows. The 263 round-1 rows exist only on this branch. |
| 1b | Rows 2-802 (801 rows) vs round-1 commit `b9ea4cd11` (SHA-256 `91342319…`) | byte-identical |
| 1c | `RESULTS.md` vs `origin/main` | identical, SHA-256 `fb5f81e8…6f55` |
| 1d | Files-opened hashes in the extension report vs pins and vs my own hashes | all six equal |
| 2 | RL-52 scope | covered. See §4; gaps outside the letter of RL-52 are in F5. |
| 3 | Independent recompute (own stdlib script, no repository analysis, recompute or checker import) | 0 MISMATCH. Counts in §3. |
| 4 | Ledger words (RL-41, RL-42) | consistent. All 881 residuals have at most 2 significant figures. The 299 within-rounding residuals equal mine at 2 s.f. Whole ledger: 731 exact, 555 within-rounding, 98 recorded-judgment, 34 single-source, 1 MISMATCH = 1,419. The only MISMATCH is row 249, the ruled RL-39 erratum. |
| 5 | `python3.13 -B -m unittest tests.b5_analysis.test_hand_check_phase2` | 37 tests OK (0.51 s) |
| 5 | Seat replay `hand_check_rl52_round2.py` (no `--write`) | exit 0. Six hashes before = after; prefix unchanged; counts as reported. |
| 5 | `hand_check_phase2.py --repo-only` | exit 0 |
| 5 | `hand_check_rl52.py` (round-1 replay) | **exit 1** ("extension differs"). See F3. |
| 6 | BETA decode load-line refusal vs registered behaviour | matches. See §5. |

## 3. Independent recomputation

**Script.** [`opus_coldreview_rl52_check.py`](../analysis/b5/opus_coldreview_rl52_check.py) runs in about
0.3 s. I wrote it from the registered text:

- analysis plan §4 steps 1-7;
- §5 (point floor, guard, corner widening, comparative widths);
- §6 (R and R_cm);
- §8.1 (cross-window rule, load line, battery line, stage temperature);
- §8.2 (ρ, percentiles, hard band, spread);
- the disclosure producer's own `bound_formula` line, for NEG-8.

**Own numerics.** The script has its own Student t: a closed-form integer-df CDF with bisection. It reproduces
the plan's pinned quantiles, for example t(0.975, 9) = 2.2621571627982 and t(0.975, 4) = 2.776445105.

**Inputs.**

- Member values from `RC.members.*`: `E_j`, `a_bop_j`, `r_j`.
- Member values from the whole-machine records: `RC.disclosures.whole_machine.windows.*.members[*].phases.request`.
- Stored per-member exclusion codes, from `RC.exclusions_rederivation.{ALPHA,BETA}` and `EXC.members_excluded`.
- Code families, from DISC's `flag_count` lines.
- Stage thermistor readings, from DISC.
- The pinned comparative `shared_j` trace-sweep widths. These cannot be derived from member scalars, as in the
  accepted seat-4 review.

**What it derives itself.** Kept and removed units come from the member codes and are not copied. They equal
the stored `kept_units` in all four cells and in all eight floor forms. The NEG-8 deciding corpus comes from
the stored status and physics codes plus the first-12 desk cap. It equals `RC.windows.*.neg8.corpus_ids` for
both windows.

**Method.** Every new row (540-1420) gets two comparisons where possible:

- **source:** the row's key path is resolved in the named pinned file;
- **hand:** the row is compared with my own value.

| Comparison | exact | within-rounding | MISMATCH | not applicable |
|---|---:|---:|---:|---:|
| Source leaf equality (881 rows) | 516 | 311 | 0 | 54 derived counts and words with no single leaf; all 54 are hand-checked |
| Independent recompute (881 rows) | 422 | 299 | 0 | 160 source-only: 92 recorded-judgment, 20 single-source, 48 sourced metadata (status words, refusal code, FILL class and source words, attempt numbers) |

**Required targets.**

| Target | Rows | Result |
|---|---|---|
| 8 R and 4 R_cm with numerator, denominator, n and pass (RC and DISC copies), branch, failure counts | 540-606, 803-864 | 76 within-rounding, 36 exact. The 12 DISC `status = complete` rows are sourced exactly. Branch B; 0 R fail; 3 R_cm fail. Anchor: R_cm 1.7B prefill 1.9997 (own value 1.99975). |
| 4 comparative floors (RC `floor_cmp_j` and DISC `minted_j`) | 550, 566, 582, 598, 865-868 | 8 within-rounding |
| B kind averages (RC, PROJ-A, PROJ-B) | 607-609, 627-629, 657-659, 684-686, 950-952, 980-982, 1022-1024, 1066-1068 | 16 within-rounding, 8 exact (the zero kind) |
| Attaining run of the attribution floor (argmax of the first-kind bound over kept members) and its minimum | 610-611, 630-631, 660-661, 687-688, 953-954, 983-984, 1025-1026, 1069-1070 | all agree |
| XWIN Δ, h_G, h_F, booleans and words (rule \|G−F\| ≤ √(h_G²+h_F²)) | 623-626, 653-656, 680-683, 709-712, 974-978, 1006-1010, 1054-1058, 1096-1100 | 24 within-rounding, 12 exact. Three agree; **8B decode differs**. |
| Seeded sample of disclosure rows (pool 607-802 and 885-1420; `random.Random(20261111)`, k = 40) | 650, 660, 682, 684, 689, 696, 719, 720, 726, 751, 767, 792, 889, 892, 932, 945, 963, 967, 983, 1000, 1010, 1012, 1042, 1060, 1124, 1144, 1158, 1171, 1174, 1178, 1185, 1257, 1285, 1316, 1330, 1338, 1339, 1355, 1384, 1385 | 33 recomputed (19 exact, 14 within-rounding). 7 are recorded-judgment or single-source rows, sourced (5 exact, 2 within-rounding). 0 MISMATCH. |

**Beyond the sample.** The script also recomputes every row of these kinds, with 0 MISMATCH:

- removed-unit and contrast-quad code and family unions;
- load and battery lines with restored counts;
- ρ summaries for all three packs;
- both NEG-8 families' bound terms, statistics, excursions, allowances and screen words;
- reference and corpus counts;
- physics counts;
- stage rises, plateaus and flags;
- attempt counts, cause sets and multiplicities;
- analysed collected/planned counts.

**Seat 12's printed values against the new rows.** I compared 64 pairs of rows that print the same quantity,
with all 64 equal:

| Seat-12 row | Matching new rows |
|---|---|
| reported cells (rows 133-167) | DISC primary rows and RC battery-line rows |
| cross-window deltas (rows 169-172) | 623/974, 680/1006, 709/1096, 653/1054 |
| R_cm (rows 276-279) | 554/843, 570/848, 586/853, 602/858 |

## 4. Scope against RL-52's list

| RL-52 item | Rows | Covered |
|---|---|---|
| 8 R with 16 terms, 4 comparative floors, n of each form | 540-606, 803-868 | yes |
| Floor-limit class words | 869-884 (FILL, both contrasts, both resolutions) | yes. They are sourced exactly. `attribution_limited` agrees with every gating absolute cell having R > 2. |
| Attempt causes and counts | 885-949 (ALPHA, BETA, superseded ALPHA) | yes |
| Removed units with codes | 612-614, 632-638, 662-665, 689-694, 955-1038, 1071-1080 | yes |
| Arm hazards | 1163-1180, 1291-1308 | yes, as recorded-judgment |
| NEG-8 | 785-802, 1255-1287, 1383-1420 | yes, both families |
| Monitor cost | 1160-1162, 1288-1290 | yes, single-source with the RL-41 label |
| Per-cell battery and load lines | 615-622, 639-652, 666-679, 695-708, 959-1111 | yes |
| ρ per pack | 722-784, 1243-1254, 1371-1382 | yes |
| Three B kind averages and the attaining run | see §3 | yes |
| XWIN agree/differ words by the registered rule | see §3 | yes |
| Per-quad contrast removal codes | 713-721, 1112-1159 | yes |

Nothing on RL-52's list is missing. F5 lists what the per-session placeholders ask for beyond that list.

## 5. The BETA decode load-line refusal (check 6)

The seat's sentence matches the registered behaviour.

- **What the registered producer issued.** For this cell, DISC carries `status = refused` with
  `code = whole_window_verdict_provenance_invalid`, restored counts {repeat 3, quad 1} and family
  PHYSICS_IN_SPAN, at `DISC.cells[label=load_correlated_cell, cell_id=…decode-qwen3-8b]`.
- **What the registered rule says.** Analysis plan §8.1 prints the line beside the primary and never in its
  place. A refused registered output issues a code, not a number: "never zero by default".
  `docs/phase_2/refusal_scope_spec.md` classes the code as a custody or authentication refusal.
- **Where the number comes from.** The numeric line exists only in RC, at `RC.disclosures.load_sensitivity`.
  `LEAN-COVERAGE-AUDIT.md` exempts that whole family from comparison, so the RC value is uncompared.
- **Independent restoration.** Mine gives the same restored set:
  - repeats r03, r06 and r10, contention only;
  - quad b10, contention only;
  - b01 and b04 stay removed, because their codes are mixed or not load-correlated.

  That gives n_r = 10 and n_b = 8. RC's mean and interval agree within rounding.
- **Conclusion.** The correct presentation is the one the seat describes: the registered refusal printed next
  to the hand-checked, uncompared recompute value.
- **One fact the pinned files do not explain.** The spec scopes this code globally, yet BETA prefill's load
  line, from the same window, computed. The ledger correctly sources the refusal as metadata. It does not
  claim to reproduce the predicate. No row changes; the label in F4 covers this.

## 6. Findings

| # | Severity | Finding | Required action |
|---|---|---|---|
| F1 | **Medium** (paper-bound prose) | `REDERIVATION.md` line 739 ("the latter is 8B prefill") and the run report lines 283-284 name **8B prefill** as the one "differ" cell. It is **8B decode**: Δ = −0.42167 J against √(h_G²+h_F²) ≈ 0.229 J. Ledger rows 656, 1057 and 1058, DISC, RC, `RESULTS.md` §1.2 and my recomputation all agree on this. 8B prefill agrees. The rows are right; only the sentence is wrong. | Before the second fill, change both sentences to "8B decode". No row changes. |
| F2 | **Medium** (integration) | `docs/paper/paper1/fill_check_b5.py` on `main` (seat 12) pins the 538-row ledger hash `0462f814…`. Run against this branch's ledger, it reports `FAIL: 1 problem(s)` (ledger SHA-256 is not the print authority). It is not wired into CI, but seat 12's fill gate turns red as soon as this table merges. The branch merges cleanly with `main` otherwise. | In this PR (after merging `main`), re-pin the check to the unchanged 538-row prefix, or to the new authority hash `5546bfd2…` once the lead records it. Otherwise the second fill must do it first. Do not merge with the check silently failing. |
| F3 | Low (hygiene) | `docs/analysis/b5/hand_check_rl52.py`, the standalone round-1 replay, exits 1 at HEAD with `ValueError: extension differs`, because the ledger now has 1,419 rows. The round-2 script replays the same arithmetic, so nothing goes unchecked. But a committed replay that fails is a trap, and the run report's table implies it still runs. | Scope it to rows 540-802, as was done for `hand_check_phase2.py`, or delete it as superseded by round 2. |
| F4 | Low (presentation) | Rows 647-651 (BETA decode RC load line) say `print` and still carry the round-1 note "disclosure-source cross-check pending access ruling". Their registered counterpart is the refusal in rows 1064-1065. This follows the RL-42 precedent of rows 376-384, and `REDERIVATION.md` states the pairing in prose, but a fill seat citing row 649 alone would see a bare `print`. | The second fill prints rows 647-651 only with the refusal of rows 1064-1065 and the label "recompute only; not compared". Optionally add that pairing to the RL-52 table in `REDERIVATION.md`; the rows themselves are immutable. |
| F5 | Medium (scope, outside RL-52's letter) | **(a) Session-level battery counts.** `P1-B5-HAZARDS` asks for per-session "battery-assist counts". The window-level `battery_counts` lines (`DISC.window_lines.{alpha,beta}[160]`: `battery.assist`, `battery.assist_outside_request`, `calibration.capture_battery_assist`, `battery.smc_unavailable`, pair assists) have no rows. Only per-cell kept-member assist counts do. **(b) GAMMA.** The per-session placeholders (ATTEMPTS, HAZARDS, NEG8) also cover GAMMA, but RL-52 scoped disclosures to ALPHA and BETA. GAMMA's NEG-8 screen word and bound terms, its stage temperatures, and its arm lines other than battery amperage have no rows. Its DISC attempt-count and cause line has no row either; row 511 records only "first". GAMMA's monitor cost, collected/planned counts, deciding references and corpus size do have rows (348-350, 212-218). | Lead's call. Either add a small sourcing extension (window battery counts, plus the GAMMA session lines on the same pattern), or have the second fill print these per-session items for ALPHA and BETA only and leave GAMMA's pending with a reason. |
| F6 | Info | The brief's "801 prior rows vs `origin/main`" cannot hold literally: `main` has only the 538 original rows. Both prefixes were checked against their own commits, `main` and `b9ea4cd11`, and are identical. | None. |

## 7. Reproduce

`python3.13 -I -B docs/analysis/b5/opus_coldreview_rl52_check.py [--seed 20261111 --sample 40]`

It prints:

- the per-word counts for source and hand checks, and every FLAG (none at this sha);
- the residual-precision and residual-agreement counts;
- the seed, the sample rows and the sample's word counts;
- the target-group counts;
- the seat-12 pair check;
- the whole-ledger words;
- the before = after hashes.

It prints no member value and writes nothing.

---

## Delta review: rounds 3 and 4 (RL-55)

2026-11-11 04:15 PST (12:15Z) · same reviewer · target `analysis/2026-11-11-b5-ledger-ext` @
`8dc82e24e17d3b00dfa3272e18328fecaa75c724`. The reported print authority is `ffe8137be`; its ledger and
coverage table equal HEAD's. Ledger SHA-256 is `2f15d081…8469`, with 1,844 rows. I read RL-55 verbatim on
the audit branch.

### Delta verdict: ADMIT-WITH-FIXES

All 425 round-4 rows are confirmed, with 0 MISMATCH and 0 `source-outside-unseal`. F1-F4 are closed. One
Medium finding remains (D1): RL-55's five-decimal R_cm row does not exist. One Low finding (D2) concerns
reason words.

**Blind status.** Unchanged. In round 4 the seat opened RC, DISC and CMP (`round4_sources.tsv`). CMP is
`release-check-final-20261108T0942Z/comparison.json`, `b12b7e1b32b27159be894221dcde7e334784061314fe91a39166faa36f72f4c9`,
pinned in RESULTS.md §0. I added CMP to my pinned set and hashed it before reading. I opened the same seven
files as before plus CMP. Every file's hash equalled its pin before and after (re-hashed 12:15Z). I listed no
directory and followed no path.

### Checks

| # | Check | Result |
|---|---|---|
| 1 | Rows 1-1420 vs my reviewed commit `a1f916e9b` | byte-identical. `RESULTS.md` is unchanged. |
| 2 | F1 | closed. `REDERIVATION.md` lines 757 and 814 and the run report now say **8B decode**; no "8B prefill differ" remains. |
| 2 | F2 | closed. `fill_check_b5.py` asserts the 538-row prefix against `0b8763f0a` and the full hash `2f15d081…`. `--paper-ref origin/main` gives PASS: 69 filled ids, 111 rows. |
| 2 | F3 | closed. `hand_check_rl52.py` and `hand_check_rl52_round2.py` both exit 0 at HEAD. |
| 2 | F4 | closed. `REDERIVATION.md` line 775 has the pairing instruction for rows 647-651 with 1064-1065, and the coverage table's LOAD-LINE element carries it. |
| 3 | Independent recompute of rows 1421-1845 | see the next table; 0 MISMATCH |
| 4 | Coverage table vs `origin/main` `paper1.md` (`84ad2c5be`; `paper1.md` is unchanged to `6a7493f40`) | Every pending Block 5 placeholder is present: 65 ids, 1,581 elements, lines and descriptions identical. Every one of the 1,539 row elements cites the row whose key it names. No cited row is `not-printed` or MISMATCH. The other 42 elements carry an RL-55 reason. Placeholders not in the table are Block 6, BYTES, automation, the abstract's Part 2, or Appendix B historical counts (DX-010 to DX-013, DG-067/068/135/136); none is a Block 5 output. `fill_coverage_b5.py` passes. Exceptions: D1 and D2. |
| 5 | R_cm 1.7B prefill 1.99975 row, and the double-row rule | The rule is documented (`REDERIVATION.md` lines 46-51). The row is **absent** (D1). |
| - | Seat tests and replays | 58 tests OK. `hand_check_rl55_round4.py` exits 0, with counts 370 exact, 25 within-rounding, 30 recorded-judgment. |
| - | Seat edit to my script | Round 3 added `--repo-only` and capped the rows-540-1420 loop. The logic is otherwise unchanged. My round-4 extension reads rows 1421 onward separately. |

### Round-4 recompute

The extension lives in `round4()` in the same script. It imports nothing from the seat's code. It derives:

- **Battery counts and arm-unread counts:** from the second stored flag record (`RC.exclusions_rederivation.*.rederived.flag_counts.by_code`; `EXC.flag_counts.by_code` for GAMMA), not from the DISC line.
- **GAMMA NEG-8 (both families):**
  - the deciding corpus, from the status and physics codes plus the desk cap; it equals `corpus_ids`;
  - the bound terms, statistic, excursion and allowance; the allowance equals `RC.windows.GAMMA.neg8.allowance_j`;
  - the screen words;
  - reference counts, lost run, slot and reason, and corpus counts.
- **GAMMA physics counts and stage temperatures:** physics counts from the member codes; rise, plateau and producer flag from the stored readings.
- **GAMMA attempt line:** count and causes, with collected and planned recounted from the member records.
- **Removed-unit positions, stratum and unit ID:** from the stored exclusion records, RC rederived for the cells and EXC for the contrasts.
- **Per-family compared, pass/fail, largest |L9 − recompute| and agreement word:** from `CMP.comparisons` itself. `window_edge_s` compares 0 rows, giving `not-compared`. This is the one family RL-52 asks the summary to name.

| Group | Rows | Recomputed (exact / within-rounding) | Sourced only | MISMATCH |
|---|---:|---|---:|---:|
| Battery-count and arm-unread lines, all three packs | 21 | 21 / 0 | 0 | 0 |
| All GAMMA rows: NEG-8, references, corpus, temperatures, arm, physics, attempt, contrast removed units | 182 | 120 / 12 | 50 (30 recorded-judgment, 10 stage names, 10 other identifiers) | 0 |
| Rest: CMP summary, cell removed-unit structure, ALPHA/BETA stage names and lost reference | 229 | 146 / 13 | 70 (bars, stage names, identifiers) | 0 |
| Seeded sample of the rest (`Random(20261115)`, k = 40) | 40 | 28 / 3 | 9 | 0 |
| **All 425** | 425 | 280 / 25 | 120 | **0** |

**Source-leaf equality:** 337 exact, 16 within-rounding, 0 MISMATCH. 72 derived rows have no single leaf, and
all 72 are recomputed. All residuals have at most 2 significant figures. The whole-ledger count with row 249 as
the only MISMATCH is reproduced by the seat's replay: 1,101 exact, 580 within-rounding, 128 recorded-judgment,
34 single-source and 1 MISMATCH. The groups overlap: rows that are both GAMMA and battery or arm lines are
counted in each. The "All 425" row is exact.

### Delta findings

| # | Severity | Finding | Required action |
|---|---|---|---|
| D1 | **Medium** (paper-bound) | **No ledger row prints 1.99975.** RL-55 assumed the ledger held R_cm for 1.7B prefill twice, "1.9997 from RESULTS.md and 1.99975 from the extension". In fact rows 570 and 848, and rows 277 and 502, all print **1.9997**, each with residual 0.000048. `REDERIVATION.md` line 48 says row 570 holds 1.99975, which is false. The coverage element "fullest-precision 1.7B prefill R_cm (RL-55)" under CP-X02-conclusion cites row 570 (1.9997). Under RL-52 every printed value is a row, so the second fill cannot print 1.99975 as things stand. The value itself is right: my own R_cm is 1.9997482608, which rounds to 1.99975. | Append one row: printed `1.99975`, key `RC.dominance.common_mode[Qwen3-1.7B-4bit/prefill].R_cm`, `within-rounding`, residual `-1.7e-6`. Re-point the coverage element to it and correct line 48. No existing row changes. |
| D2 | Low | Five BYTES elements carry the reason "not a leaf of a registered output": P1-M-ACCEPT, P1-LEDGER, P1-DEV-LIST, P1-RELEASE and P1-AVAIL. That reason is inaccurate, because they are BYTES registered outputs; their own instructions say "sealed and outside this Block 5 output ledger". None of RL-55's three reasons fits. | Relabel them "outside Block 5 (BYTES; sealed)", or have the lead accept the label as a stand-in. This changes no row. |
| D3 | Info | The coverage table pins `paper1.md` at `84ad2c5be`. Main is now `6a7493f40`, with `paper1.md` unchanged. | After main is merged into the branch, re-run `fill_coverage_b5.py` against the merged paper. |
