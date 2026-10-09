# Text gate on the seal commit's two documents (ruling A.7, section D gate 4(c))

Written 2026-10-09 by the Opus 5.5 seat that ran the gate: one reader, one pass. The seat did not write the
edits it checked. It edited the two documents in the worktree `/Users/edr/code/JouleWise-wt-corpus18-seal` and
wrote this file. It changed no code and no configuration, ran no git command that changes anything, ran no
test, started no agent, made no network request and opened no file of a claim window. The lead commits.

**Object.** `git diff 3f564499e HEAD` (HEAD `8ce450ad5`) of `registration_block5.md` and
`analysis_plan_block5.md` under `configs/campaigns/v5_claim_25g83/`: 40 hunks, 36 in the registration and 4 in
the analysis plan.

**Checked against.** `RULING.md`; the lead's decisions at the end of `CORRECTIONS-APPLIED.md` and
`SEAL-TEXT-EDITS.md`; `ERRATUM.md` section 4.5; the build worktree `/Users/edr/code/JouleWise-wt-corpus18` at
`778e52b0d` (its `joulewise/` and `scripts/` do not differ from main `3f564499e`); the desk rule as built,
`/Users/edr/code/JouleWise-wt-harvest-cap/joulewise/b5/harvest.py` at `273fc48db` (`neg8_corpus_physics` at
5355 to 5491, `NEG8_CLEAN_CORPUS_MAXIMUM_N = 12` at 861, the re-screen guard at 4918 to 4938 and 5244).

| File | SHA-256 as the gate received it | SHA-256 as the gate leaves it (uncommitted) | Lines |
|---|---|---|---|
| `registration_block5.md` | `74cdec02c263844ab0cc043789ea17d34b866e6041fb057e11722f90c9893a0b` | `98107c8e9822a48cff56aeea1622664066f8f155448a262ea484498621d76306` | 6,366 → 6,382 |
| `analysis_plan_block5.md` | `d82113f5000ec3106fcc934ac330f05357d187011e01596a9cbb4382360d1506` | `cd4d56269ed85e6bece4735e870c7a43b5b8c8dabbc59aedc6166d9664b59ba3` | 1,018 → 1,024 |

Line numbers below are lines of the files as the gate leaves them. The gate made 17 corrections, G1 to G17
(16 in the registration, 1 in the analysis plan). Line 354 of the analysis plan is byte-identical to main's.

**Values recomputed by this seat** (`shasum -a 256`, and `python3 -I` arithmetic on the real files):

- Plan trees: ALPHA `2ec3625a…2809`, BETA `e77e4f6e…0707`, GAMMA `da802897…85bc`; each equals the pack's
  `plan_tree.sha256` and the digest recorded in `sizing_b5.json`. `sizing_b5.json` `a8e8d530…cfad`.
  `identity_pins.json` `513d7d4a…841d` (its diff against main is three changed lines, the plan-tree digests).
  `configs/pins/registry.json` `64930f75…491a` (placeholder left, as ordered).
- Sizer output: members 125, 125, 107 (by class 125 / 0, 25 / 100, 67 / 40); `programmed_span_s` 106,890,
  109,290, 95,754; `window_max_s` 110,220, 112,620, 99,060; `corpus_retry_s` 12,336; ALPHA `members_s` 74,375.
- Expected chains: 33,003, 34,053, 29,166 s (block-3 basis) and 20,278, 21,328, 18,244 s (projected); the
  hours printed for each; the margins 73,887, 75,237 and 66,588 s.
- Disk: 132 × 182 MiB = 25,190,989,824 bytes = 23.46 GiB, 90.4 GiB required; 114 × 182 MiB = 20.26 GiB, 80.8 GiB.
- The binomial table of R16 (all 20 cells, and 0.72 and 0.4%); the worked example of R21 (s 0.2217,
  U_3 100.3033, L_3 99.7433, 0.5600, 0.3983, and 0.5767 from 14 members).
- The t table (`joulewise/aggregate.py` 41 to 59): 2.262, 2.228, 2.201 at 9, 10, 11 degrees of freedom.
- Corpus: 18 rows `neg8-refcorpus-r01` to `-r18`, `planned_n_bundles` 18, the two new ids; each plan tree's
  corpus stage `expected_count` 18; `planned_bound_bundles` 12 in all three calibration plans.
- `DRY-RENDER.md` `7bb10119c923a36d76e6045926e01d9d4aa49191d0e82e38ab374b54ec98f3c2`, the same bytes in the
  records worktree and in the build branch.

**Taken from a record, not re-run by this seat:** the `--check` exit codes of the generators, the sizer and the
identity pins (`pr492-gates.md` line 29); what the two first-seal ALPHA chains lost (the erratum's section 1.1,
from window records this seat may not open); the judge's simulation table.

## 1. The 43 edits and X1

| Edit | Line | Verdict |
|---|---|---|
| R1 | 3 | correct |
| R2 | 89 | corrected here (G1): "the deciding bound" was used with no meaning given; added "(the bound by which the screen and the allowance are judged)" at line 91 |
| R3 | 410 | correct |
| R4 | 759 | correct; the three digests are true of the build head |
| R5 | 987 | correct |
| R6 | 1422 | correct |
| R7 | 1661 | corrected here (G3): "four generator literals" → "literals in the four pack generators". Four generator files changed, with ten changed lines between them (ruling D item 2) |
| R8 | 1806 | corrected here (G4): both placeholders filled, and the sentence rewritten, because the record does not show what the sentence said. See the note under this table |
| R9 | 2264 | correct |
| R10 | 2270 | correct in its arithmetic. "216 GiB free on 2026-10-09" at line 2271 is left: the lead fills it at the seal (decision 1). This seat read 213 GiB with `df -g /Users/edr` |
| R11 | 2286, 2298 | correct, both parts |
| R12 | 2549 | correct |
| R13 (a) (b) (c) | 2734, 2739, 2744 | correct; the example's counts hold (9 of 18 succeeded, the retry measures six, 15 succeeded) |
| R14 | 2786 | correct |
| R15 | 2788 | corrected here (G6): the paragraph headed "Registered rule" said only "from at most 12 of those members", so which 12 could not be read from the rule. Now: "the first 12, in the committed order, on which none of the six physics codes fired (the codes are listed under "A fourth source of omission" below), or all such members when only 10 or 11 remain". "The mint" is glossed at this use, which now comes before its definition |
| R16 | 2803 | corrected here (G7): the accepted extra sentence named "the "one fewer lost" columns", a label no column carries; now "The third and fifth columns allow one loss fewer: ...". Both tables equal the erratum's and the recomputation |
| R17 (a) to (d) | 2842, 2850, 2890, 2896 | correct; the historical manifest's path is the one the core reader uses (`whole_window.py` 150 to 157) |
| R17 (e) | 2925 | corrected here (G9): the lead's wording said a stored bracket with another NEG-8 condition "leaves the screen failed" with no limit. As built and as sealed, that holds when the window has no loss; a reference newly lost at harvest or a corpus member dropped for physics still lets the re-screen decide (`harvest.py` 4922 to 4923, 5244). The limit is now stated, with the sentence that the cap and a clean bound built with no physics drop lift nothing |
| R18 (a) (b) | 2941, 2970 | correct |
| R19 (a) (b) | 2979, 2986 | correct |
| R20 | 3002 | correct |
| R21 | 3008 | corrected here twice. G10 (3041): the bare code word `corpus_physics_clean` now reads "`derived/neg8-screen.json` then records `bound_used` as `corpus_physics_clean`" (`harvest.py` 5338, 5346). G11 (3049): "t = 2.262, 2.228 and 2.201" now says "respectively" and names 9, 10 and 11 degrees of freedom. Steps (i) to (vi) are the ruling's words and match the code |
| R22 | 3176 | correct |
| R23 | 3181 | correct, with the accepted difference ("more than 66,000 s in every pack" is true; the smallest margin is 66,588 s) |
| R24 | 3194 | correct |
| R25 | 3227 | correct, all 18 cells |
| R26 | 3241 | correct |
| R27 | 3267 | correct |
| R28 | 3283 | correct |
| R29 | 3363 | correct |
| R30 | 3458, 3460 | correct |
| R31 | 4671 | correct |
| R32 | 4916 | correct (80 + 7 + 2 + 18 = 107) |
| R33 (a) | 5164 | correct |
| R33 (b) | 5192 | deviation 9 correct, word for word. Deviation 8 corrected here (G16): "The plan tree's `runtime_budget.bound_count` reads 18" is true of ALPHA's and BETA's plan trees (line 3912 of each); GAMMA's has no such field. The sentence now says so |
| R34 | 5725 | correct |
| R35 | 5875 | correct; `<REGISTRY_SHA256>` left |
| R36 | 5938 | correct |
| R37 | 5958 | correct |
| R38 | 6105 | correct; both commit hashes resolve (`git rev-parse`) |
| R39 | 6331 | correct |
| P1 | 3 | correct; no line break added |
| P2 | 601 | corrected here (G17): "in-window bound", "clean bound", "deciding bound", "desk cap" and "mint" had no meaning given anywhere in the analysis plan. Four sentences added at 608 to 614 that state each |
| P3 | 509 | correct |
| P4 | 1016 | correct; its third bullet stays true (G17 is below line 354) |
| X1 | 3232 | correct; 98,826 + 8,064, 101,226 + 8,064 and 87,690 + 8,064 give the table's spans |

All 43 edits are present. 34 are correct as applied; 9 carry a correction (R2, R7, R8, R15, R16, R17 (e), R21,
R33 (b), P2).

**Note on R8 (G4).** Section 4.5 made the sentence conditional: write it only if the new record shows the six
renders repeated with bound bundles 18/18/18 and the corpus 18 listed and 18 kept. `DRY-RENDER.md` is a
different and narrower check, the one ruling D gate 2 orders: the three chain scripts rendered at `a5ae00c46`
with scratch names and parsed with `zsh -n`; corpus stage `expected_count` 18; `--max-failures 18` on the stage
and on its retry; two comment lines per script that say 12. No stand-in window ran, so no bundle count exists.
The sentence as applied was therefore false. It now reads (1806 to 1813): the chain of each pack was rendered
again at `a5ae00c46`; the record's path and SHA-256; "That check is narrower than the six renders above. It
renders the three chain scripts with scratch directory names and parses each with `zsh -n` (a syntax check that
runs nothing); it runs no stand-in window, so it repeats none of the table's counts"; then the three facts the
record shows. The lead may strike the sentence instead; nothing else depends on it.

## 2. Hunks that are none of the listed edits

None. The 40 hunks are R1; R2; R3; R4; R5; R6; R7; R8; R9 with R10; R11 (two hunks); R12; R13; R14 to R16;
R17 (a) (b); R17 (c) (d); R17 (e) with R18 (a); R18 (b); R19; R20 with R21; R22 to R24; R25 with X1 and R26;
R27; R28; R29; R30; R31; R32; R33 (a); R33 (b); R34; R35; R36; R37; R38; R39; and P1, P3, P2, P4.

## 3. The search over both whole files

### 3.1 Hits corrected

| # | Line | Old | New | Source |
|---|---|---|---|---|
| G2 | 382 to 384 | "the deadline is about 27 h, against a projected chain of 4.8 to 5.7 h" | "about 29 h, against a projected chain of 5.1 to 5.9 h (about 27 h and 4.8 to 5.7 h before the erratum of 2026-10-09 gave the corpus 18 members, §14 Q16)" | spans 95,754 to 109,290 s; projected chains 18,244 to 21,328 s. The sentence cites §5.5 in the present tense, so it is corrected like R2 and R3, with the old values kept |
| G5 | 2718 | "the window's deadline (§5.5, 28.4 h for ALPHA)" | "30.6 h for ALPHA" | `window_max_s` 110,220 s |
| G8 | 2834 | "still knows only the full corpus" | "still knows only the full corpus it was written for (the historical 12-member one, item 2)" | the full corpus is now 18 members, and the core reader does not know it |
| G12 | 3220 | "the members per class (61 / 40)" | "(61 / 40 when the lane landed; 67 / 40 since the erratum of 2026-10-09, §14 Q16)" | `members_by_class` small 67, large 40 |
| G13 | 3308 to 3310 | "24.4, 27.5 and 28.1 h ... about 27 h"; "4.8 to 5.7 h ... 7.7 to 9.1 h" | "26.6, 29.7 and 30.4 h ... about 29 h"; "5.1 to 5.9 h ... 8.1 to 9.5 h" | the sizer's spans; the chains of R27 and R28. "about 5 to 6 h" and "about five times ... about three times" still hold (5.3 and 3.3) |
| G14 | 3322 to 3323 | "about 18–23 h ... (15.9 h of chain) and about 28–33 h ... (25.6 h of chain)" | "about 19–24 h ... (16.6 h of chain) and about 29–34 h ... (26.7 h of chain)" | 59,850 s and 96,222 s of chain; totals by the paragraph's own rule (chain + 3 × 0.6 to 1.6 h + 3 arms of 4 to 46 min): 18.6 to 23.7 h and 28.7 to 33.8 h |
| G15 | 4112 | "(the collected-subset bound, a reference lost at harvest, a corpus member dropped for physics)" | "(..., the clean bound, which since the erratum of 2026-10-09 the harvest builds on every window)" | the list names the three re-screen cases of §5.3, and R17 (c) changed the third |

G1, G3, G4, G6, G7, G9, G10, G11, G16 and G17 are in the table of section 1.

### 3.2 Hits that stand: `119`, `101`, `126`, `108`, the byte count, the spans

| Hit | Line | Why it stands |
|---|---|---|
| "101.08 J" (twice) | 1250, 1267 | a synthetic energy in §0.12's example |
| "126 of 536", "126 of the 536", "All 126", "126 of them" | 2211, 5102, 5103, 6327 | sensor publications in the battery rule |
| "showed 126 × 182 MiB", "revision 6 showed 119 × 182 MiB" | 2287, 2288 | dated history, kept by R11 |
| "over 119 members" (three times) | 3277 to 3279 | per-member savings measured over an earlier plan's 119 members |
| "about 119 s", "gaps 119–740 s" | 3287, 3288 | times in seconds |
| "0 of 119 bundles" | 3351 | the record of a revision-4 window |
| "the counts of 119 and 101 run ids in §16" | 6124 | R38 naming what stays |
| "119 run ids each", "the same 101", "GAMMA's 101 planned members" (twice) | 6330, 6331, 6362 | the record of the first seal's checks; R39's sentence says so |
| "98,826, 101,226 and 87,690 s" | 3232 | X1 names them as the first seal's spans |
| `108`, `24,045,944,832`, `24045944832` | none | no hit |

The analysis plan has no hit for any of these.

### 3.3 Hits that stand: old digests and the first seal's H_claim

| Hit | Line | Why it stands |
|---|---|---|
| `1d87a309…`, `0cdb3383…`, `8b1d1d71…` in full | 754 to 756 | the dated record of the int5 head `fe28e5a0c` (lead's decision 3) |
| `a0865895…` in full | 2553, 5875 | the dated earlier value, kept by R12 and R35 |
| `89e7ea70…` in full | 3198 | the dated earlier value, kept by R24 |
| the five abbreviated digests | 5906 | the row records a check "as at `fe28e5a0c`" |
| `a64000884…` | 760, 1664, 5726, 6116 | each is named as the first seal's H_claim |
| `0ec9d68a`, `74ccdaec` | none | neither document prints them |

### 3.4 Hits that stand: `12`, "twelve", "10 or 11"

Every `12` that is a number of its own (not part of a longer number, a digest, a date, or a "§" reference) was
listed by program and read. Registration:

| Class | Lines | Why it stands |
|---|---|---|
| "Revision 12", `B5-REV12-SYNC` | 3, 23, 41, 77, 429, 1674, 1733, 1737, 1909, 1921, 3470, 4523, 4850, 5024, 5084, 5584, 5709 to 5744, 5926, 5941, 5970, 6055, 6089, 6340, 6355, 6367 | the revision's number |
| "§12", "## 12. Seal" | 448, 5558, and every "§12" | a section number |
| list item 12, "item 12", "PLAN2 row 12", "step 12", table row 12 | 538, 548, 4644, 4902, 6142 | numbering |
| "exit 10, 11 or 12", exit code 12 | 391, 2657, 3353, 3436, 3445, 3653, 3669, 4008, 4594 | the chain's exit codes |
| "(12 tests)", "12 record files", "the 12 science order manifests" | 5901, 5937, 5194 | unrelated counts |
| "twelve questions", "twelve places" | 433, 2692 | unrelated |
| the cap: "at most 12", "the first 12", "10, 11 or 12", "capped at 12", "12 whenever" | 91, 2747, 2794, 2797, 3003, 3035, 3044, 3049, 3050, 5165, 5200, 6105, 6112 | the desk cap of 12 |
| "n their count (10, 11 or 12; §5.3)" | 1015 | sealed; ruling B item 4 says it stays |
| "Twelve corpus gross energies" | 1244 | §0.12's example: 12 kept members is the normal case under the cap |
| the dry render record of 2026-10-07: "12 listed and 12 kept", "the 12 NEG-8 corpus members", 12/12/12 | 1787 to 1789, 1794 to 1799 | the first seal's record; R8 follows it |
| "two comment lines that say 12" | 1811 | R8, deviation 9 |
| "revision 4 wrote 12" | 89 | R2, dated history |
| "the first seal's 12-member corpus", "with a 12-member corpus" | 2271, 2287, 3013 | dated history |
| R16: "a corpus of 12", "all 12", ""10 of 12"", "(12 planned)", the table's "12 members" columns, "a 12-member corpus survives one burst" | 2803 to 2830 | the first seal's corpus and its loss rates |
| "the historical 12-member one / manifest / file" | 2834, 2842, 3064 | the historical corpus the core reader knows |
| member positions: "11, 12 and 13", "members 1 to 12", "..., 11, 12, 13, ..." | 2744, 2745, 3067, 3069, 3070 | positions in worked examples |
| the simulation's row for 12, "2.51 σ at 12" | 3021, 3026 | the judge's table |
| "twelve energies", "which twelve", "ten of twelve" | 3057, 3067, 3071, 3074 | the capped corpus |
| "The estimate for 12 bundles" | 3182 | R23: the estimate was made for 12 |
| "`planned_bound_bundles` 12", "computed for 12 members", "still say 12, 10 and 11" | 5192, 5197, 5200 | deviations 8 and 9 |
| "10 or 11 of 12 when the question was closed" | 5958 | R37 |
| "2 and 3 of their 12 corpus members", ""10 of 12"", "12/12/12" | 6109, 6110, 6123 | R38: the first seal |
| "whose corpus had 12 members" | 6332 | R39 |
| "where revision 10 or 11 had" | 449 | revision numbers |
| "when only 10 or 11 remain" | 2796 | G6: the rule |
| "a 10- or 11-member bound before" | 2928 | R17 (e): the first seal's behaviour |

Analysis plan: "Revision 12" and "revisions 4 to 12" (3, 5, 785, 957), table row 12 (172), "## 12." (759) and
every "§12" are numbering; "10, 11 or 12" (601), "the first 12" (611), "at most 12" (1017) and "when only 10 or
11 remain" (613) are the cap; "for a NEG-8 corpus of 10 or 11 members" (821) is §14's dated entry for
revision 4.

### 3.5 Durations and other figures read and left

| Line | Text | Why it stands |
|---|---|---|
| 2730 | "A normal ALPHA chain reaches its last stage 5–9 h after the pre capture" | the ALPHA chain is now 5.6 to 9.2 h, and its last stage starts before its end; 20.1 h is still more than twice 9.2 h |
| 2733 | "the window is lost about 1 h into the chain while the chain runs about 7 h more" | a round figure: the corpus now ends 0.8 to 1.4 h into the chain and 4.7 to 7.8 h remain |
| 2806 | "runs in its first hour" | the corpus stage is 41 to 71 min of members; still roughly the first hour |
| 2271 | "87.2 and 77.6 GiB", "83.5 and 73.9 GiB" | labelled as the first seal's and revision 6's |
| 3232 to 3236 | "93,402, 95,802 and 82,266 s" | labelled as revision 6's |
| 1226 | "when the corpus was cleaned" | a condition that now holds on every window; not false |
| 3204 | "22,494 s span and 25,800 s window" | block 4's committed figures |

## 4. The rule as §5.3 and §0.12 now state it

Read as someone who must rebuild the mechanism from the text alone, after the gate's corrections:

- **18 members, all run, committed order.** Stated in the "Registered rule" paragraph (2788 to 2791) and in
  §0.12 (987). Correct.
- **In the window only the count changes.** The retry below 10 succeeded (§5.1, 2734; "The in-window bound",
  3061), the in-window bound from all kept members, n from 10 to 18, and "That bound is a diagnostic" with the
  reason (3063 to 3065). Correct.
- **At the desk.** Before the gate, the rule paragraph said "at most 12 of those members" and left which 12 to
  a paragraph 230 lines later. It now names them in the rule (G6). The mechanism paragraph (3032 to 3042) gives
  the six steps in the ruling's words, in the order the code runs them: members of the validated in-window
  bound; ordered by the committed order manifest; the six physics codes removed; the first 12 kept, or all if
  fewer; `neg8.bound_not_derived` below 10; the clean bound built, validated and written. It matches
  `neg8_corpus_physics` as built.
- **Members beyond the cap.** Recorded under `beyond_cap`, no flag, no catalog code, "their energies are used
  by nothing" (3044 to 3047). Correct.
- **Multipliers.** 2.262, 2.228 and 2.201 at n = 10, 11 and 12, now with "respectively" and the degrees of
  freedom (G11). §0.12 gives t = t(0.975, n − 1) and n "(10, 11 or 12; §5.3)".
- **A stored bracket with another NEG-8 condition.** Stated wrongly wide before the gate; now limited to a
  window with no loss, as the code and the sealed sentence at 2916 have it (G9).
- **A re-screen that cannot run leaves the screen failed.** The sealed sentence stands at 2916 to 2917.
- **Terms.** In-window bound and clean bound are defined in bold at first use (2792 to 2794); the desk cap, the
  envelope, the allowance consumer, route 1 and route 2 and the core reader are each built or glossed at or
  before first use. Four were not and are now: "the deciding bound" (G1), "the mint" in the rule paragraph
  (G6), `corpus_physics_clean` (G10), and all five terms in the analysis plan (G17).

One thing the registration does not state, recorded and not added: as built, the harvest reads the order
manifest from its copy of the repository and requires its bytes to hash to the plan tree's pin; if they do
not, or the file cannot be read, no clean bound is built and the window carries `neg8.bound_not_derived`
(`harvest.py` 5414 to 5437). The ruling's steps do not mention it. It is a desk refusal on an input that failed
its own hash, it can only remove a bound, and desk code may be fixed after the seal (§7.5), so the gate did not
write a new registered behaviour into the seal text.

## 5. Placeholders

`<DRY_RENDER_RECORD_PATH>` and `<DRY_RENDER_RECORD_SHA256>` are filled (registration 1807 to 1808) and occur
nowhere else. Remaining, each used as section 4.5 defines it (a date; a 40-character hash; a SHA-256), each in
backticks:

| Placeholder | `registration_block5.md` | `analysis_plan_block5.md` |
|---|---|---|
| `<SEAL_DATE>` | 3, 5725 | 3, 1016 |
| `<NEW_H_CLAIM>` | 1661, 5725, 6117 | none |
| `<REGISTRY_SHA256>` | 5875 | none |

A search for `<` followed by a capital letter finds these eight occurrences and nothing else. "TODO" occurs
only inside the file name `INTEGRATION_TODO.md` (sealed text).

Three values that are not placeholders but that the lead sets or confirms at the seal:

- Registration 2271, "216 GiB free on 2026-10-09 (`df -g`)": the lead's decision 1 fills it from a reading at
  the seal.
- The five digests filled from the build head (registration 763 to 765, 2549, 3194, 5875) are true of
  `778e52b0d`. If the merge changes one of the five files, the same lines change.
- Registration 1806 to 1807 cites the build commit `a5ae00c46` and says its pack bytes are those H_claim
  carries. True unless the merge changes a pack file.

## 6. Not settled by this gate

Nothing is open. Two things were outside what the gate may do and are stated so that nobody assumes them:

- The tests that read the two documents were not run (`tests/test_b5_seal_landing.py`,
  `tests/test_digest_pin_census.py`, `tests/test_harvest_b5_window.py`, `tests/flags/test_flags_collect.py`).
  The gate's 17 corrections moved registration lines by 16 and analysis-plan lines below 608 by 6; line 354 of
  the analysis plan did not move.
- The hashes and line counts in `SEAL-TEXT-EDITS.md` describe the files before this gate; the table at the top
  of this file has the current ones.

TEXT GATE: PASS
