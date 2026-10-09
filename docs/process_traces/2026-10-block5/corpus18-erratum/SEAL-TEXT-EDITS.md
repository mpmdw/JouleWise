# The text edits of `ERRATUM.md` section 4.5, as applied to the two seal documents

Written 2026-10-09 by the Opus 5.5 seat that made the edits. The seat edited two files in the worktree
`/Users/edr/code/JouleWise-wt-corpus18-seal` and wrote this file. It changed no code and no configuration, ran
no git command that changes anything, ran no test, started no agent, made no network request and opened no
file of a claim window. The lead commits.

| File | SHA-256 before | Lines before | SHA-256 after (placeholders still in it) | Lines after |
|---|---|---|---|---|
| `configs/campaigns/v5_claim_25g83/registration_block5.md` | `4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841` (checked first; equal to the brief's) | 6,173 | `74cdec02c263844ab0cc043789ea17d34b866e6041fb057e11722f90c9893a0b` | 6,366 |
| `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` | `1172a4501e2311a98508e6102420de657daa88c8c455603717b8ff7b2a1e1b8a` (equal to section 4.5, rule 1) | 999 | `d82113f5000ec3106fcc934ac330f05357d187011e01596a9cbb4382360d1506` | 1,018 |

**How the edits were made.** One program per file read the sealed bytes, checked the SHA-256, and replaced
text at the sealed line numbers. Before each replacement it checked that the quoted old wording stood exactly
once in the named lines; a wording that was not there would have stopped the program with nothing written.
Every old wording was found at the lines section 4.5 gives. Lines that an edit does not touch keep their
bytes and their line breaks. New sentences are wrapped at 118 columns, the width of the sealed text.

**Counts.** Section 4.5 has 43 edits (39 for the registration, 4 for the analysis plan). Applied as written:
39. Applied with a difference of wording: 4 (R16, R17 part (e), R21, R23; each difference is stated in the
table). Not applied: 0. Extra: 1 (X1, section 2). Filling a placeholder with a value the brief gave counts as
"applied as written".

## 1. Section 4.5, edit by edit

"Sealed lines" are lines of the sealed text. "Now at" is the first line of the edited passage in the edited
file.

### Table R, the registration

| Edit | Sealed lines | Now at | Result |
|---|---|---|---|
| R1 | 3 | 3 | applied; `<SEAL_DATE>` left |
| R2 | 87 to 89 | 88 | applied |
| R3 | 406 | 409 | applied |
| R4 | 754 to 756 | 758 | applied; the three plan-tree digests filled with the brief's values (also recomputed by this seat with `shasum -a 256` at the build branch head `94a60fff4`, equal). Lines 747 to 753 untouched |
| R5 | 976 | 986 | applied |
| R6 | 1411 | 1421 | applied |
| R7 | 1650, 1651 | 1660 | applied; `<NEW_H_CLAIM>` left. The sentence "changes no file under `joulewise/` or `scripts/`" was checked: `git diff --stat main...HEAD -- joulewise scripts` in the build worktree prints nothing |
| R8 | 1789 (insert) | 1803 | applied; both dry-render placeholders left. **Conditional:** section 4.5 says the sentence is written only if the new record shows exactly those counts. This seat found no new dry-render record (only `dry-records` and `dry-records-2` exist under `/Users/edr/night-archive/gate-prune/`), so it could not check. The lead keeps or strikes the sentence when the record exists |
| R9 | 2240, 2241 | 2259 | applied |
| R10 | 2246, 2247 | 2265 | applied as written, with a note: the text says "216 GiB free on 2026-10-09 (`df -g`)", the drafting seat's reading. This seat read 214 GiB with `df -g /Users/edr` on the same date. The 216 was written as section 4.5 has it. See question 1 |
| R11 | 2261, 2262 and 2272 | 2281, 2293 | applied, both parts |
| R12 | 2523 | 2544 | applied; the identity-pins digest filled. The sentence "no model or runtime pin in it changed" was checked: the file's diff against main has three changed lines, the three plan-tree digests |
| R13 (a) (b) (c) | 2705; 2709 (insert); 2711 to 2714 | 2729, 2733, 2739 | applied, three parts |
| R14 | 2752 | 2781 | applied; the title is one line |
| R15 | 2754 to 2757 | 2783 | applied |
| R16 | 2759, 2760 | 2795 | applied **with a difference**: one sentence added before "These figures are a guide": "The "one fewer lost" columns show the chance that one member is still spare for the harvest's physics drop (below)." It is the sentence that follows the same table in `ERRATUM.md` section 2.3. Without it the table's third and fifth columns are not explained anywhere in the registration. The lead may strike it (line 2818, first sentence). The two tables were copied unchanged; this seat recomputed the binomial table and every cell agrees |
| R17 (a) (b) (c) (d) | 2770 to 2772; 2775; 2813, 2814; 2819 | 2832, 2840, 2880, 2886 | applied, four parts |
| R17 (e) | after 2846 (insert) | 2915 | applied **with a difference, by the lead's decision 2**. Section 4.5 had: "or the harvest's always-on clean bound must handle it ... such a window must still fail or be re-derived correctly". Written instead: "First, a stored bracket that carries a NEG-8 condition other than the two bound-underived ones leaves the screen failed, as item 3 says of case (a). That the harvest now builds the clean bound on every window, so that case (c) holds on every window too, does not change this: the harvest program pinned for these windows (§11 item 4) is tested on a stored bracket that carries another NEG-8 condition, and the test must show the screen failed." Second difference: "the allowance consumer" is glossed at this, its first use in the registration: "(the core function that reads a window's drift allowance for a claim)". Sealed lines 2838 to 2840 are untouched |
| R18 (a) (b) | 2848, 2849; 2878 | 2927, 2957 | applied |
| R19 (a) (b) | 2887; 2892 to 2894 | 2966, 2973 | applied |
| R20 | 2908 to 2911 | 2989 | applied |
| R21 | after 2911 (insert) | 2995 | applied **with a difference, by the lead's decision 1**: in the paragraph "What the cap is, and what it is not", after "n is therefore 10, 11 or 12, as §0.12 says" the words ", with t = 2.262, 2.228 and 2.201 (the table in `joulewise/aggregate.py`)" were added (line 3035). The decision says the registration states 2.228 for n = 11, and no edit of 4.5 printed a multiplier for n = 11. Read from `joulewise/aggregate.py` lines 41 to 59 at the build head: 9 → 2.262, 10 → 2.228, 11 → 2.201. The † marks and the outer quotation marks were not copied |
| R22 | 3012, 3013 | 3161 | applied; 12,336 s is `corpus_retry_s` in the real `sizing_b5.json` |
| R23 | 3018 to 3020 | 3167 | applied **with a difference**: section 4.5 says the under-charge "is inside the span's margin of more than 70,000 s over the expected chain". From the real sizer output and the registration's own expected chains, the margin on the block-3 basis is 73,887 s for ALPHA, 75,237 s for BETA and 66,588 s for GAMMA (95,754 − 29,166), so "more than 70,000 s" is false for GAMMA. Written: "is inside the span's margin over the expected chain, which is more than 66,000 s in every pack (the table below)" |
| R24 | 3026 | 3180 | applied; the sizing digest filled |
| R25 | 3056 to 3058 | 3213 | applied. Members, spans and deadlines are the real sizer output. The four expected-chain figures of each row are not in the sizer output; this seat recomputed them from the sums of R27 and R28 and they agree |
| R26 | 3068 to 3072 | 3227 | applied. 74,375 s is `members_s` in the sizer output; 106,890 − 74,375 − 9,625 − 12,336 − 5,424 = 5,130 |
| R27 | 3094 to 3096 | 3253 | applied |
| R28 | 3110 to 3112 | 3269 | applied |
| R29 | 3190, 3191 | 3349 | applied |
| R30 | 3286, 3288 | 3444, 3446 | applied, both parts |
| R31 | 4498 | 4656 | applied |
| R32 | 4743, 4744 | 4901, 4902 | applied, both parts |
| R33 (a) | 4991 | 5149 | applied |
| R33 (b) | after 5017 (insert) | 5177 | applied; deviation 9 is the cold ruling's sentence word for word |
| R34 | 5542, 5543 | 5709 | applied; `<NEW_H_CLAIM>` and `<SEAL_DATE>` left |
| R35 | 5690 | 5859 | applied; plan-tree, sizing and identity-pins digests filled; `<REGISTRY_SHA256>` left (see question 2). The row is one line |
| R36 | 5753 | 5922 | applied |
| R37 | 5773 | 5942 | applied |
| R38 | after 5918 (insert) | 6089 | applied; `<NEW_H_CLAIM>` left. Its section references were checked against the edited file's headings (§0, §2, §4.6, §5.5, §13, §16) |
| R39 | 6124 (insert) | 6315 | applied |

### Table P, the analysis plan

| Edit | Sealed lines | Now at | Result |
|---|---|---|---|
| P1 | 3 | 3 | applied inside the line, no line break added; `<SEAL_DATE>` left |
| P2 | 597 to 599 | 601 | applied |
| P3 | after 508 (insert) | 509 | applied |
| P4 | after 999 (insert) | 1000 (an empty line; the entry begins at 1010) | applied; `<SEAL_DATE>` left |

Rule 2 of section 4.5: line 354 of the analysis plan is byte-identical and is still line 354 (checked by the
program before it wrote).

## 2. Extra edit

| # | Sealed lines | Now at | What and why |
|---|---|---|---|
| X1 | 3060 to 3063 | 3217 | The sentence under the sizing table said the spans "are read from the sizing output with the SHA-256 printed above for `fe28e5a0c` and `9395cecfb`" and "Each span is revision 6's plus the 5,424 s of spare retries". After R25 the table holds the new spans, so both statements were false. The lead's decision 7 says the seal text takes the sizer's output. Written: "The programmed spans and `WINDOW_MAX_S` are read from the sizing output with the SHA-256 printed above for H_claim. Each span is the first seal's (98,826, 101,226 and 87,690 s, read from the sizing output with the SHA-256 printed above for `fe28e5a0c` and `9395cecfb`) plus 8,064 s for the six corpus members that the erratum of 2026-10-09 added (§14 Q16): 6 × 672 s in the corpus stage and 6 × 672 s in the one corpus retry. Each of the first seal's spans was revision 6's plus the 5,424 s of spare retries (93,402, 95,802 and 82,266 s at `a434e363d`)." Checked: 98,826 + 8,064 = 106,890; 101,226 + 8,064 = 109,290; 87,690 + 8,064 = 95,754. Section 4.5 did not order this edit; the lead may revert it, but then the sentence contradicts the table |

## 3. Questions for the lead

1. **Free disk reading (R10).** 216 GiB (section 4.5) or 214 GiB (this seat's `df -g`, 2026-10-09)? Both are
   far above the 90.4 GiB an arm needs.
2. **`<REGISTRY_SHA256>` (R35).** The brief gave no value. At the build head `94a60fff4`,
   `shasum -a 256 configs/pins/registry.json` prints
   `64930f7521d9b447269fd24e06531b735655a2163e3ac30f40791f35add6491a`. Left as a placeholder in case the
   registry is refreshed again before the merge.
3. **R8** is conditional on a dry-render record that this seat could not find (table R).
4. **Sentences that section 4.5 does not list, that hold none of the searched numbers, and that the new
   sizing table makes stale.** Not edited. Each cites the table or the deadline and prints a figure derived
   from the first seal's spans. With the values the edited table would give:
   - line 383 (the change list of an earlier revision): "27 h, against a projected chain of 4.8 to 5.7 h".
     Dated history of a revision; probably stays.
   - line 2713 (§5.1): "the window's deadline (§5.5, 28.4 h for ALPHA)" → 30.6 h.
   - lines 3294 to 3296 (§5.5): "24.4, 27.5 and 28.1 h for GAMMA, ALPHA and BETA (the table above), about
     27 h" → 26.6, 29.7 and 30.4 h, about 29 h; "The projected chain is 4.8 to 5.7 h, about 5 to 6 h, and the
     block-3 basis 7.7 to 9.1 h" → 5.1 to 5.9 h and 8.1 to 9.5 h. ("about five times its projected length,
     or about three times the block-3 basis" still holds: 5.4 and 3.3.)
   - lines 3307 to 3309 (§5.5, block duration): "(15.9 h of chain)" → 16.6 h (20,278 + 21,328 + 18,244 =
     59,850 s); "(25.6 h of chain)" → 26.7 h (33,003 + 34,053 + 29,166 = 96,222 s); the totals "about
     18–23 h" and "about 28–33 h" each grow by about 0.7 and 1.1 h.
   - line 3206 (§5.5, on lane L10): "the members per class (61 / 40)". True of lane L10 when written; the
     table now says 67 / 40.
   All are planning figures that gate nothing. The lead decides whether the seal carries them as they are,
   with one sentence saying so, or corrected.
5. **Tests that read the two documents** were not run by this seat (no test run was allowed):
   `tests/test_b5_seal_landing.py`, `tests/test_digest_pin_census.py`, `tests/test_harvest_b5_window.py`,
   `tests/flags/test_flags_collect.py`.

## 4. Residual hits of the text gate's search, and why each stands

Searched in both edited files: `12`, `119`, `101`, `126`, `108`, `24,045,944,832`, `24045944832`, `98,826`,
`101,226`, `87,690`, the seven old digest prefixes, and the first seal's H_claim `a64000884`. Line numbers are
of the edited files. The analysis plan has no hit except `12` (below).

### Registration: `119`, `101`, `126`, `108`, the byte count, the spans

| Hit | Line | Why it stands |
|---|---|---|
| "revision 6 showed 119 × 182 MiB" | 2283 | dated history, kept inside R11 |
| "over 119 members" (three times) | 3263 to 3265 | the per-member savings were measured over the 119 members of an earlier plan (section 4.5's table of lines that stay, sealed 3104 to 3106) |
| "Below about 119 s", "gaps 119–740 s" | 3273, 3274 | a time in seconds, unrelated |
| "0 of 119 bundles" | 3337 | the record of a window of revision 4 (sealed 3178) |
| "the counts of 119 and 101 run ids in §16" | 6108 | R38's own sentence naming what stays |
| "119 run ids each", "the same 101 run ids" | 6314 | the record of the first seal's checks (sealed 6123); R39's sentence follows it |
| "GAMMA's 101 planned members" (twice) | 6315, 6346 | R39's sentence, and the record it names (sealed 6153) |
| "101.08 J" (twice) | 1249, 1266 | a synthetic energy in §0.12's worked example, unrelated |
| "126 of 536", "126 of the 536", "All 126", "126 of them" | 2206, 5087, 5088, 6311 | a count of sensor publications in the battery rule, unrelated |
| "showed 126 × 182 MiB" | 2282 | dated history of the first seal, written by R11 |
| `108` | none | no hit |
| `24,045,944,832`, `24045944832` | none | no hit |
| "98,826, 101,226 and 87,690 s" | 3218 | extra edit X1 names them as the first seal's spans |

### Registration: old digests and the first seal's H_claim

| Hit | Line | Why it stands |
|---|---|---|
| `1d87a309…`, `0cdb3383…`, `8b1d1d71…` in full | 753 to 755 | the dated record of the int5 head `fe28e5a0c` (sealed 750 to 752; the lead's decision 3) |
| `a0865895…` in full | 2548 | the dated earlier value, kept by R12 (sealed 2524) |
| `89e7ea70…` in full | 3184 | the dated earlier value, kept by R24 (sealed 3027) |
| `a0865895…` in full | 5859 | R35's row, in the part that begins "At the first seal's H_claim" |
| the five abbreviated digests | 5890 | the row records a check "as at `fe28e5a0c`" (sealed 5721) |
| `0ec9d68a`, `74ccdaec` | none | neither document ever printed them |
| `a64000884…` | 759, 1663, 5710, 6100 | each is called "the first seal's H_claim" or "Under the first seal" by R4, R7, R34, R38 |

### Registration: `12`

Hits of `12` as a number of its own (not inside a longer number, a digest, a date or a section number such
as §0.12), by class.

| Class | Lines | Why it stands |
|---|---|---|
| "Revision 12", "revision 12", `B5-REV12-SYNC` | 3, 23, 41, 77, 428, 1673, 1732, 1736, 1904, 1916, 3456, 4508, 4835, 5009, 5069, 5568, 5693 to 5715, 5910, 5925, 5954, 6039, 6073, 6324, 6339, 6351 | the revision's number |
| "§12", "§11 and §12", "§12 step N", "## 12. Seal" | 7, 22, 27, 55, 59, 315, 421, 429, 432, 447, 498, 508, 515, 548, 980, 1140, 1512, 1519, 1526, 1732, 1734, 1744, 2513, 2551, 2900, 3179, 3191, 3956, 3968, 4833, 5057 to 5061, 5202 to 5417, 5542, 5706, 5716, 5887, 5917 | a section number |
| list item "12." and "item 12" | 537, 547 | a list number |
| chain exit code 12 | 390, 2652, 3339, 3422, 3431, 3639, 3655, 3994, 4579 | the chain's exit code for a failed pre-calibration screen |
| "PLAN2 row 12", "step 12", "(12 tests)", "12 record files", table row "\| 12 \|" | 4629, 4887, 5885, 5921, 6126 | unrelated counts and row numbers |
| "twelve questions", "twelve places" | 432, 2687 | unrelated |
| the dry render record of 2026-10-07: "12 listed and 12 kept", "the 12 NEG-8 corpus members", 12/12/12 six times | 1786 to 1788, 1793 to 1798 | the record of the first seal's render (sealed 1772 to 1784); R8 adds the new record after it |
| "The rendered comments still say 12" | 1807 | R8, deviation 9 |
| "revision 4 wrote 12" | 89 | R2, dated history |
| "at most 12", "the first 12", "10, 11 or 12", "capped at 12", "caps the deciding corpus at 12", "12 whenever at most six" | 91, 2742, 2789, 2790, 2990, 3022, 3030, 3035, 3036, 5150, 5184, 6089, 6096 | the cap of 12 (R2, R13, R15, R20, R21, R33, R38) |
| "n their count (10, 11 or 12; §5.3)" | 1014 | sealed 1004; the cold ruling's section B item 4 says it stays |
| "Twelve corpus ..." in §0.12's worked example | 1243 | a corpus of 12 kept members is the normal case under the cap (sealed 1233 to 1236) |
| "a corpus of 12", "all 12" (twice), ""10 of 12"", "(12 planned)", "12 members, at most 2 lost", "12, at most 1 lost", "a 12-member corpus survives one burst" | 2795 to 2821 | R16: the first seal's 12-member corpus and its loss rates |
| "the first seal's 12-member corpus", "with a 12-member corpus" | 2266, 2282 | R10, R11: dated history |
| "the historical 12-member manifest", "the historical 12-member file", "sealed with a 12-member corpus" | 2832, 3000, 3050 | R17, R21: the historical corpus |
| "members 11, 12 and 13", "leaves 11, 12 and 13" | 2739, 2740 | R13 (c): member positions in the worked example |
| the table row "\| 12 \| 2.36 σ ...", "2.51 σ at 12" | 3008, 3013 | R21: the simulation's row for n = 12 |
| "members 1 to 12", the two lists "..., 11, 12, 13, ...", "twelve energies" (twice), "which twelve", "ten of twelve" | 3043, 3053 to 3060 | R21: member positions and the capped corpus |
| "The estimate for 12 bundles" | 3168 | R23: the estimate was made for 12 |
| "`planned_bound_bundles` 12", "the 12 science order manifests", "computed for 12 members", "still say 12, 10 and 11" | 5177 to 5184 | R33 (b): deviations 8 and 9; the 12 science order manifests are an unrelated count |
| "10 or 11 of 12 when the question was closed" | 5942 | R37 |
| "2 and 3 of their 12 corpus members", ""10 of 12"", "bound bundles 12/12/12" | 6093, 6094, 6107 | R38: the first seal's corpus and what stays as history |
| "whose corpus had 12 members" | 6316 | R39 |
| "a 10- or 11-member bound before" | 2918 | R17 (e): the first seal's behaviour |

### Analysis plan: `12`

| Hit | Line | Why it stands |
|---|---|---|
| "Revision 12" , "revisions 4 to 12", "revision 12 filled" | 3, 5, 779, 951 | the revision's number |
| "registration §12" | 3, 775, 952, 959, 966 | a section number |
| table row "\| 12 \| Results cold gate" | 172 | a row number |
| "## 12. What the analysis never does" | 753 | a section number |
| "corpus size (10, 11 or 12: ..." | 601 | P2: the cap |
| "for a NEG-8 corpus of 10 or 11 members" | 815 | §14's entry for revision 4, dated history |
| "at most 12 of them" | 1011 | P4: the cap |

No hit was found that section 4.5 missed and that the ruling plainly requires changing. The stale sentences of
question 4 hold none of the searched strings.

## 5. Placeholders left, with lines (edited files)

Every one is a name of section 4.5's placeholder table. `<PT_ALPHA_SHA256>`, `<PT_BETA_SHA256>`,
`<PT_GAMMA_SHA256>`, `<SIZING_SHA256>` and `<PINS_SHA256>` were filled with the brief's values and do not occur
any more. Neither document prints the order-manifest or settled-corpus digest, the new seal commit, the new
sealed inventory's digest or the new harvest pin, so no placeholder stands for them.

| Placeholder | `registration_block5.md` | `analysis_plan_block5.md` |
|---|---|---|
| `<SEAL_DATE>` | 3, 5709 | 3, 1010 |
| `<NEW_H_CLAIM>` | 1660, 5709, 6101 | none |
| `<DRY_RENDER_RECORD_PATH>` | 1805 | none |
| `<DRY_RENDER_RECORD_SHA256>` | 1805 | none |
| `<REGISTRY_SHA256>` | 5859 | none |

A search for `<` followed by a capital letter finds these and nothing else. Filling `<SEAL_DATE>` on line 3 of
the analysis plan adds no line break, so line 354 stays line 354.

Values filled, for the record:

| Name | Value | Registration lines |
|---|---|---|
| ALPHA plan tree | `2ec3625a31b796e3fa37e2c39f37508618b649d0d9f61ddbd3fdfe2c5a282809` | 762, 5859 |
| BETA plan tree | `e77e4f6e74f663190d1acfe95c3e2499ec69c1b27ba9e3564c531affee980707` | 763, 5859 |
| GAMMA plan tree | `da8028977dfe44b3bf1d13e79e7bfea2b1390aa985bef7faa891369c8e3985bc` | 764, 5859 |
| `sizing_b5.json` | `a8e8d53036f08b5d6edc648ec77f01f75890ae904a817204600d6daac912cfad` | 3180, 5859 |
| `identity_pins.json` | `513d7d4a98f464c7236b34c53f51cd523a9f45b4d9f05f2282a4a22424b4841d` | 2544, 5859 |

If the merge changes any of these five files, the same lines change.

## 6. The free-disk arithmetic, as verified

From the plan trees in `/Users/edr/code/JouleWise-wt-corpus18` (build head `94a60fff4`), by the rule of
`joulewise/b5/plan.py` lines 766 to 777 (members are the sum of `expected_count` over the collection stages;
spares are the largest spare set of each reference stage; planned bytes are 182 MiB for each):

| Pack | Members (collection stages) | Spares | Members + spares | Planned bytes | In GiB | 3 copies + 20 GiB |
|---|---|---|---|---|---|---|
| ALPHA | 18 + 3 + 10 + 20 + 20 + 1 + 10 + 20 + 20 + 3 = 125 | 3 + 1 + 3 = 7 | 132 | 132 × 182 MiB = 25,190,989,824 | 23.46 | 90.38, printed 90.4 |
| BETA | the same stage counts, 125 | 7 | 132 | 25,190,989,824 | 23.46 | 90.4 |
| GAMMA | 18 + 3 + 20 + 1 + 20 + 1 + 20 + 1 + 20 + 3 = 107 | 7 | 114 | 114 × 182 MiB = 21,755,854,848 | 20.26 | 80.79, printed 80.8 |

The member counts equal `members` in the real `sizing_b5.json` (125, 125, 107). The figures verified are
**90.4 GiB for ALPHA and BETA and 80.8 GiB for GAMMA**, as the brief states.

Other sizing figures read from the real `sizing_b5.json` (SHA-256 `a8e8d530…`) and found equal to section 4.5:
programmed spans 106,890, 109,290 and 95,754 s; `window_max_s` 110,220, 112,620 and 99,060 s; `corpus_retry_s`
12,336 s; `members_s` for ALPHA 74,375 s; members by class 125 / 0, 25 / 100 and 67 / 40.

## 7. `git diff --stat` of the worktree

```
 .../v5_claim_25g83/analysis_plan_block5.md         |  27 +-
 .../v5_claim_25g83/registration_block5.md          | 355 ++++++++++++++++-----
 2 files changed, 297 insertions(+), 85 deletions(-)
```

`git status --short` lists the two files as modified and nothing else. The worktree's head is `3f564499e`.

## Lead's decisions on the five open points (magistrate activation 1aed44f9, 2026-10-09 09:10 PDT)

1. The free-disk figure of R10 is filled at the seal from `df -g /Users/edr` read at that moment; it is a
   dated observation, and the arm measures free disk itself.
2. The pin registry's digest is filled at the seal from the merged head, with the other placeholders.
3. R8's dry-render record does not exist yet. The lead writes it from the renders of the builder and the
   reviewer before the seal (ruling section D gate 2), then fills the path and digest.
4. The stale durations at the new lines 2713, 3206, 3294 to 3296 and 3307 to 3309 go to the text gate
   (ruling section D gate 4(c)), which reads the whole diff and the search list; they are corrected there,
   not silently here.
5. The extra edit X1 and the sentence added to R16 stay: both remove a sentence that the other edits
   made false.
