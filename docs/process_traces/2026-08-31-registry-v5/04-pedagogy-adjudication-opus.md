# Round-7 retensing plan — fresh pedagogy adjudication (blind seat)

**Seat:** fresh pedagogy adjudication, blind to the drafting process. Judged only what is on the page.
**Inputs:** `docs/paper/draft-v1.md` (frozen, read in full), `docs/paper/round7/retensing-plan.md` (read in full).
**Method:** each replacement imagined substituted at its stated draft line, inheriting only what precedes that line.
**Standard applied:** a reader must be able to replicate the mechanism from the text alone; every term of art, criteria word, or verb doing technical work is built from physical reality before first use, glossed in plain words AT first use, or deleted; no word does unpaid work.

**Counts: 17 BL / 15 SF / 7 N.**
(15 hazard blocks carry blockers, plus 2 plan-level blockers; 14 blocks carry should-fixes, plus 1 plan-level should-fix.)

**Overall verdict: NOT USABLE FOR SUBSTITUTION.**

A note on shape before the findings: 11 of the 15 blocking blocks inherit from exactly two root defects (R1 and R2 below). Fixing those two roots plus the six independent blockers clears the majority of this list. The lint passed because both roots are defects of *what the draft still says after the substitution* and of *mechanism the paper never contains* — neither is a token-ordering property.

---

## BLOCKERS

### R1 (root) — The paper's acceptance criterion silently changes from "exceeds" to "at least 2," and the old criterion survives on the page

Sites: H01, H03, H04, H06, H07, H22, H27, H28, H29, H48, Item 10.

Every A/B branch in the plan decides the headline result on a quotient of "at least 2" — plan line 15: "Every quotient must be at least 2"; H06-A "at least twice the bound from repeated point measurements alone"; H28-A "the quotient was at least 2"; H04-A heading "What a twofold boundary contribution changes."

The draft's registered criterion is *exceedance*, not doubling, and it is stated three times in text that no block replaces:

- line 21: "The finding is falsified for a phase if the timing-widened bound **does not exceed** the point-only repeatability bound."
- line 185: "A component is labelled *attribution-limited* only when … the exact linear corner maximum used by the code's predicate **strictly exceeds** the guarded point-only value."
- line 356 (same paragraph as H28/H29/H47): "**Where edge placement contributes more than repeatability**, phase-boundary attribution dominates the cell's resolution bound."

After substitution, line 356 will read "Where edge placement contributes more than repeatability, phase-boundary attribution dominates…" one sentence away from H28-A's "the quotient was at least 2." Two different accept criteria for one test, adjacent.

Separately and independently: **the number 2 is never built anywhere.** No replacement sentence says why 2, or even that 2 was fixed before collection. `grep -c "doubl"` on the draft returns six hits, all "double-headed arrows" and "doubling the prompt" — no threshold. The word doing the most technical work in the entire retensing is unpaid.

Required before substitution: (a) a built justification of the 2 at its first use, or explicit "a threshold of 2 fixed before collection, chosen because …"; and (b) retensing blocks for draft lines 21, 185, and the surviving clause of 356, so the paper carries one criterion.

### R2 (root) — The "shared-error ratio" decides the result and has no mechanism anywhere in the paper

Sites: H06, H07, H22, H27, H28, H29, Item 10, H48.

Plan line 36 makes it decisive: "A comparative shared-error value is mandatory, and a value below 2 selects B even when every independent-edge ratio passes." The paper-facing gloss is, at best, H06-A's "when timing error shared within each four-run comparison moved together" and, at worst, H07-A's "with its shared timing error moving together."

The draft's §4 defines corners as the *only* enumeration: line 148, "Enumerate all \(2^n\) joint *corners*, where a corner is one simultaneous lower-or-upper choice for every interval." There is no construction anywhere — §3, §4, or Appendix A — for recomputing a component with the shared part of the timing error forced to move as one: no split of \(h_i\) into shared and independent parts, no statement of what fraction is shared, no worked number. The draft's single mention of the concept is at line 308, **fifty lines after §6 and in the limitations**: "The shared-error alternative for four-run blocks also rests on a physical premise: common onset and offset errors within a block. Arithmetic tests validate the calculation, not that premise."

So the reader meets a decision-bearing quantity in the Abstract, is told in §6 and §10 that it selected the outcome, and is never told how it is computed or why it is a stricter test than the independent-corner one. That fails the replication bar outright, and it fails the first-use test at the Abstract.

### BL-3 — Item 10: the Results opening states a bare ratio, never saying what is divided by what

Item 10 A: "**Every independent-edge component ratio was at least 2**, and every comparative ratio remained at least 2 when timing error shared within each four-run block moved together."

This is the paper's single most load-bearing results sentence and it names no numerator and no denominator. "Independent-edge" is never glossed (independent of *what* — the other edge, the other runs?); "component ratio" is never expanded. Contrast H28-A, which does the job in one clause: "the complete interval-edge bound was divided by the point-only bound." At draft line 243, §4 line 185 has discussed the corner maximum against the guarded point value but has never formed a quotient; the only ratios the reader has seen are the diagnostic-era "paired ratios … 10.92, 5.92, and 7.02" at line 103. Item 10 must carry H28-A's clause.

### BL-4 — H39 strands the A/B/B/A notation and deletes the paper's only statement of the sign convention

H39 replaces *both* prose paragraphs at draft lines 55 and 57. Two casualties:

1. The deleted line 55 contains the only expansion of the block order: "grouped into A/B/B/A blocks—**condition A, condition B, condition B, condition A**." The replacement uses "A/B/B/A science blocks" at line 55 — the paper's first occurrence — with no gloss. The next definition is §5 line 227, and the member letters are bound only at §4 line 117 ("A block with member energies \(A_1,B_1,B_2,A_2\)"). The replacement also prints the formula "`(B1 + B2 - A1 - A2)/2`" at line 57 with all four symbols undefined for another sixty lines. This is precisely the signature that failed the two earlier rounds.
2. The deleted line 57 contains the paper's **only** statement of the sign convention: "steady linear drift subtracts from \((B_1+B_2-A_1-A_2)/2\), **whose positive sign means B used more energy**." I checked: no other line in the draft states it (§4 line 120, §5 line 229, and Table 3's "for the registered positive direction, the lower endpoint controls" all omit it). After substitution the paper reports a signed directional claim between two models and never tells the reader which sign means which model used more energy.

### BL-5 — H21: "requested maximum" and "generator estimate" are unglossed and carry the sentence's whole point

H21-A/C: "no **requested maximum** or **generator estimate** is substituted for one."

Neither term exists anywhere in the draft. "requested" appears in the draft only of sampler cadence ("the requested 100-ms sampler cadence", "a requested \(10\) Hz"), so at line 276 it reads as a sampling term. The sentence's entire force — that a per-token denominator must be the count actually observed at runtime, not the count asked for nor a library's own figure — is invisible to a reader who cannot decode the two nouns. Gloss both at use ("the output-token count requested of the runtime" / "a count reported by the generation library").

### BL-6 — H14: "thinking disabled" and "the Qwen3 chat template" are unglossed terms doing decisive technical work

H14-A: "each token-generation member rendered one of eight fixed real prompts through **the Qwen3 chat template** with **thinking disabled**, then generated exactly 512 output tokens greedily, always choosing the highest-scored next token."

The last clause is a model gloss of a term of art. The first two are not glossed at all. "Thinking disabled" names a Qwen3 reasoning mode that changes how many tokens are emitted and therefore what energy was measured; a reader who does not already know Qwen3 cannot replicate the workload and cannot tell what was switched off. Six words each fixes both. (The same phrase recurs in H45's Table 3 arm label; fixing it here covers that site.)

### BL-7 — H02 is meta-prose about itself and is not substitutable as written

The frozen sentence "Collection has not occurred, so no null value or outcome is stated here." must be replaced — it is false once collection ran. What H02 offers, in all three branches, describes the paper rather than being the paper: "**the Results opening states first whether** the separate identical-workload test was collected, then reports that every required ratio was at least 2."

Substituted at line 243, a reader *inside* the Results opening reads a sentence telling them what the Results opening does. And unlike H10 — which says plainly "Superseded by Item 10; insert no second opening sentence at this site" — H02 is not marked superseded, so the operator cannot tell whether to insert this text verbatim, insert nothing, or write something. Either mark it superseded by Item 10 (with H11 and U02 continuing to supply their own sentences) or supply real prose.

### BL-8 — H48 mandates a Methods disclosure "in the same words" that no block supplies

H48's subtitle rule: "The Methods text must disclose this branch rule **in the same words** before results are shown." No block in the substitution sheet contains that Methods text, and no draft line is named for it. The ruling cannot be executed from this sheet. (H48 also gates the word "attribution-limited" on the ≥2 rule while draft line 185 defines that exact word by the strictly-exceeds predicate — see R1.)

### BL-9 (plan level) — Census gap: two survivors hard-code the retired 256-token prompt

The census at plan line 504 keys on the string `will `, so two sentences without it were never swept:

- **Draft line 260, final sentence:** "This is not decode-only: **the 256-token prefill arm** prospectively overrides the earlier decode-only default." Survives intact beside H15's `[PREFILL_LENGTH]` and H46's four-rung ladder.
- **Draft line 198 (§4):** "for the registered decode and **fixed-p256** prompt-processing contrasts." U08's Notes claim it "replaces the superseded fixed-p256 wording," but U08 sits at line 264; line 198 is untouched.

After substitution the paper states three different prompt lengths for one arm: `[PREFILL_LENGTH]`, 256 (line 260), and p256 (line 198).

### BL-10 (plan level) — The campaign is renamed `_v5` in one place and left `_v4` in three

H28-A introduces "every usable **`_v5`** Qwen3-1.7B and Qwen3-8B … component" at line 356. `_v4` survives, unswept, at:

- line 294: "Nothing in the frozen `_v4` campaign tests that transfer."
- line 314: "does not enter `_v4`: that pack is frozen"
- line 358: "`_v4` transports a timing bound measured with commanded GPU pulses"

Line 356 and line 358 are consecutive paragraphs of §10. A reader cannot tell whether `_v4` and `_v5` are one campaign or two, and neither label is ever glossed.

---

## SHOULD-FIX

**SF-1 — "registered" is used before its own plain gloss, in the Abstract.** H06-A ("every **registered** boundary movement") lands at draft line 11; U01's gloss "the direction **fixed before collection**" lands one sentence later on the same line. The word carries the paper's whole pre-registration discipline; put the gloss at first use. Recurs in H03-A, H07-A, Item 10.

**SF-2 — H22's `not_applicable` gloss renames more than it explains, and idealizes.** "absolute rows report the shared-error ratio as `not_applicable` because **a uniform shared shift cancels after subtracting the cell mean**." A shift *of what*? The mechanism is a shared *timing* error producing an energy displacement, and that displacement is uniform across runs only if each run's power step is identical — which the paper never claims. State the quantity and the idealization.

**SF-3 — H15 uses a five-record rule six lines before H46 explains it, and overloads "floor."** H15-A requires "at least five overlapping power records" at line 260, where the reader's most recent instruction (line 254) is "A phase is resolvable only when at least three records count." The why arrives at H46 (lines 266–272). H15-C then introduces "**below the pre-registered count floor of 5**" — "floor" is one of this paper's most heavily built terms, meaning a bound in joules. Also: H15-C files the no-rung-cleared *fallback* under the *refusal* branch, which is not what outcome C means (plan line 19), and H15-A's "the unresolved parameter chosen before collection" is process vocabulary in paper prose.

**SF-4 — H20, H21, H26 stop defining Table 2/Table 3 columns that remain in the paper.** Each replaces a caption sentence whose job was to define a column with a statement that the column has no supplier, while the plan keeps the columns ("The table columns remain"). The reader meets a "Gross J/request", "J per prompt token", and "Sizing sum F+B; signed planning clearance" header the caption no longer explains.

**SF-5 — H23 deletes its column's definition.** "The point will be the mean of ten block differences." becomes a value: "The token-generation point estimate is `[E_decode_contrast_signed_J_per_request]` J per request." The definition is recoverable from lines 229 and 260, but a schema caption that prints a result while the cell below prints the same token reads as a patch.

**SF-6 — H41 and H44 both invoke "the worked record" long before it exists, with full-precision floats in narrative prose.** H41 lands at draft line 35 (second paragraph of §2): "in **the worked record**, 0.9169149999999999 W CPU, 0.00898937 W GPU…". H44 lands at line 308: "**the worked record's** 0.103 J counter total agrees with 0.10299995484180416 J". The worked record is introduced at line 438, in Appendix A.3.1. Name the appendix at both sites and round the values in body prose.

**SF-7 — H31 and H43 are prose insertions positioned inside Table 1.** H31 says "Replacement after that sentence," where the sentence lives inside the workload-response *table cell* at line 94; H43 says "Insertion after the identical-condition row" at line 95. A 90-word and a 70-word paragraph inserted there would land inside the markdown table. Both belong in the prose after the table (near line 99). The content of both is good — H31's analytic-corner explanation is the clearest thing in the sheet.

**SF-8 — H32: one 90-word sentence with nested em-dashes, production vocabulary in the paper, and a dropped operative rule.** "…**this limitation remains open for camera-ready** unless the implementation and its independent audit close it first." A paper does not discuss its own camera-ready status. The replacement also drops the current operative rule the frozen sentence stated (a floor may support a claim only in one custody session under one manifest), leaving only the neighbouring "Standalone or externally supplied floor artifacts remain non-claim-bearing" to carry it.

**SF-9 — H34 and H35 delete every point-of-use flag of the pulse→inference transfer.** After both deletions, §2 ends at the algorithm and §4 step 5 uses the timing envelopes, with nothing at either site telling the reader the bound was characterized on commanded pulses and applied to inference untested. The mechanism chain survives (line 51 ties the operative bound to phase energies; line 164 embeds it in the \(h_i\)), so this is a caveat-placement loss rather than a replication loss — but the limitation now appears only in the Abstract, §7, and §10, never where the transport happens.

**SF-10 — H40 deletes the only gloss of the figure's "direction unresolved" outcome.** The replacement prose drops "the floor clears, but the interval does not settle direction, so no claim is made," while Figure 3 and its surviving caption still name the box: "the two downward 'no' arrows lead to not resolvable and direction unresolved." "Not resolvable" is glossed at line 195; "direction unresolved" is then glossed nowhere. (The deleted "detection floor as the largest apparent effect produced when nothing changed" is acceptable to lose — H05 owns it.)

**SF-11 (plan level) — §6's substituted sentences mix past and present tense.** Past: H12-A "was registered … were analyzed", H14-A "rendered", H15-A "used", U04-A "passed", U05-A "supported". Present: H18-A "The registered analysis **forms**", H19-A "the two raw p-values **are** ordered", H22-A "Each published floor cell **reports**", H23-A "**is**". Read consecutively, §6 will not sound like one voice.

**SF-12 — H46 deletes the only plain-word binding of the bare letters `F` and `B`.** Draft line 272 — "where F is the applicable cell floor and B is the contrast's claim-side bound" — is inside H46's replaced range. Bare `F` and `B` then survive at line 285 in U04-A ("`|estimate| > F`"), H26-A ("`C = F + B`"), and the Table 3 header. §4 line 200's "\(F_{\mathrm{cell}}+B_{\mathrm{claim}}\)" is close enough that a careful reader maps them, which is why this is not a blocker — but the mapping should not be homework.

**SF-13 — H45 puts an unglossed code identifier in a paper table.** "identify the token-generation arm as **`real_prompts_v1`**". Nothing in the paper defines it; the caption should name the prompt set in words.

**SF-14 — H46's "count floor" and the ladder ordering.** Same overload as SF-3; and the ladder paragraph explaining the 5-vs-3 split lands after H15 has already used the 5.

**SF-15 — H26's tense escape hatch.** "only the check of whether the measured magnitude exceeds the cell floor is reported **when its authenticated outcome issues**" leaves a future-conditional clause inside a retensed sentence.

---

## NITS

- **N-1** — H33 removes "the artifact calls it the detection floor" from §1, so a reader who skimmed the Abstract meets "same-cell operative floor" at line 88 with no bridge. One appositive in §1 would cost nothing.
- **N-2** — H37 removes an honest self-caveat sitting next to the Hähnel and Dauner comparisons; §8 is where a PC reader most rewards it.
- **N-3** — "usable records" is used throughout the plan as an undeclared synonym for the draft's defined term "*admitted bundle*" (line 86). Tie them once.
- **N-4** — Plan hygiene: the orphan line "“Under the same refusal” is four words." appears in the Notes of H20, H21, U03, and U04. It is editorial residue and means nothing to a substituting operator.
- **N-5** — §6 will carry "50 Qwen2.5 1.5B prompt-processing phases" (line 247, diagnostic-era) beside Qwen3-1.7B (demonstration) with no distinguishing clause. One phrase prevents a reader conflating 1.5B and 1.7B.
- **N-6** — H42 coins "the paired-comparison floor" as a new name for \(F_{\mathrm{cell}}\) inside a 70-word sentence. Its arithmetic checks out against the fixture at line 210 (1.5×1.6656 = 2.4984, +0.4 = 2.8984; 1.5×1.7656 = 2.6484, +0.4 = 3.0484; max 3.0484).
- **N-7** — Item 60: "not tamper-proof against anyone" parses awkwardly; "not tamper-proof against a determined attacker" or similar.

---

## PASS

H05, H08, H09, H10, H11, H12, H13, H16, H17, H18, H19, H24, H25, H30, H33, H36, H37, H38, H42, H47, U01, U02, U03, U04, U05, U06, U07, U08, Item 60 (29 blocks).

Worth naming as models for the rest: **H30** withdraws the 95/95 label while stating exactly what the number still is and why the premise fails; **U01** glosses the uncertainty interval inline ("the range after known measurement uncertainties were included") without renaming it; **H08** turns both gates into plain questions before their formal names arrive; **U07** states the transfer limitation without the word "transport"; **Item 60** glosses tamper-evident against tamper-proof in the same breath and keeps "These" honestly plural.

---

## Overall verdict

**NOT USABLE FOR SUBSTITUTION.** Seventeen blockers: R1 (unbuilt ≥2 threshold contradicting surviving draft lines 21/185/356), R2 (shared-error ratio decides the result with no mechanism in the paper), BL-3 (Item 10's bare ratio), BL-4 (H39 strands A/B/B/A and deletes the sign convention), BL-5 (H21's "requested maximum"/"generator estimate"), BL-6 (H14's "thinking disabled"/"chat template"), BL-7 (H02 unsubstitutable meta-prose), BL-8 (H48's unsupplied Methods disclosure), BL-9 (256-token survivors at draft lines 198 and 260), BL-10 (`_v4`/`_v5` split at draft lines 294, 314, 358) — counted per affected block, that is 15 hazard blocks plus 2 plan-level gaps.

The two roots are worth stating plainly, because they are the same failure the two earlier rounds died of, moved one level out: last time the plan used vocabulary the draft had not built *before* the insertion point; this time it uses a criterion and a quantity the draft does not build *at all*, and leaves the superseded criterion standing on the page beside the new one. The lint cannot see either, because neither is about token order — one is about what the unreplaced draft still says, the other about mechanism the paper never contains.
