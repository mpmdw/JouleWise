PEDAGOGY: FIX

Second pedagogy pass (first-use test, why-chain, no unpaid words) at commit f3c1bb64 in /Users/edr/code/JouleWise-wt-d138-impl-d528efb2 (read-only; nothing modified), on:
(1) docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance/00-issuing-record.md ("IR");
(2) docs/decision_log.md: `## D-185:` (lines 12228-12276, "D185"), its index row (line 231), and the dated note after "The issuer's A-7 check is the sole new registry consumer." (line 12200, "NOTE").
Verbatim D1-D8, H1-H7, B1-B4 and quoted rulings were not judged internally; where they use a term the surrounding prose does not build, the fix goes into the surrounding prose.

Severity: MAJOR = a reader cannot replicate the mechanism or is misled; MINOR = order or gloss defect a careful reader can recover from. The verdict is FIX because of items 1-5 (MAJOR); the MINOR items should be applied in the same revision.

---------------------------------------------------------------------
## 0. First-pass reconciliation
---------------------------------------------------------------------

All 37 actionable first-pass items (A1-A25, B1-B10, C1-C2; B11 was a PASS note) are either applied in the text or listed in CHANGES.md with a reason. The CHANGES.md deviations (A8, A10, A18 A267 and "the writer", A20, A23, A24, A17/B3, B8) are justified and the resulting text is sound. A7 (table order) is applied only in part: the rows it named moved, but "epoch", "pin", "R7" and "hold H1" are still used rows before the rows that define them (item 6 below).

The new §4.5 "Design change before merge" is replicable in its main line: forcing problem, a route table with every column named, the doubling defect with real numbers (23 against a threshold of 24; the judge's prototype bound 0.0384310413330314 s), the three options, and the chosen cure. It has three defects (items 3, 9 and 10 below).

---------------------------------------------------------------------
## 1. MAJOR defects
---------------------------------------------------------------------

### 1 (MAJOR). IR §4.2, "Added by design addendum A1": the sentence says the opposite of the mechanism
- Location: IR §4.2, second paragraph: "it hashes the file at that path and refuses unless the digests are equal or if the file is missing."
- Why it fails: read literally, this says "refuses unless (equal, or missing)", which means a missing file is accepted. Addendum A1 §5 S2 says "refuses unless equal; a missing file refuses." A reader who rebuilds the tool from this sentence gets it wrong.
- Replacement: "it hashes the file at that path, and refuses if the file is missing or if its sha256 differs from the digest the text cites."

### 2 (MAJOR). IR §4.4 "What is not closed by code" and D185 Considerations "What code does not close": "ordinary capture" is never built
- Location: IR §4.4: "a bracket needs two valid ordinary captures, and at 25G83 every ordinary capture refuses at preflight while the default is R7." D185: "every ordinary capture at 25G83 refuses at preflight while the default is R7".
- Why it fails: this is the whole argument that no result can come out of a manual campaign, and it rests on a word that is never defined. "Ordinary" also collides with the defined term "ordinary-invalid" (IR §1, Ledger). The intended sense, from addendum A1 E12 ("this is an ORDINARY night"), is a calibration capture taken in a window that is not a derivation night. That matters because derivation-night captures skip the default's epoch check but are never bracket endpoints.
- Replacement (IR §4.4): "It cannot produce a result through the code routes tested: a result needs a passed bracket; a bracket needs two valid calibration captures taken outside a derivation night, because captures of a derivation night are never bracket endpoints (§1, Derivation night); and at 25G83 every calibration capture outside a derivation night refuses at capture preflight while the default is R7."
- Replacement (D185): "It cannot produce a result through the code routes tested: a result needs a passed bracket, a bracket's two calibration captures must come from a window that is not a derivation night (derivation-night captures are never bracket endpoints), and at 25G83 every such capture refuses at capture preflight while the default is R7 (addendum A1 R-7)."

### 3 (MAJOR). IR §4.5 "The cure" and D185 Options: "would close that night" / "both close the derivation night" do unpaid work
- Location: IR §4.5: "The first two would close that night, so every non-claim capture would be screened by the held file's level screen." D185 Options, last bullet: "both close the derivation night at 25G83".
- Why it fails: the reader is not told why keeping the default on the new file shuts the derivation night. The chain in addendum A1 E12 is that the derivation-night input writer runs only when the default does not cover the machine's epoch. With the default covering 25G83, the writer refuses ("this is an ORDINARY night"), so non-claim captures must go through ordinary capture preflight, which returns the default's level screen. Without that chain, "close" is a verb doing the technical work.
- Replacement (IR): "The first two keep the new file as the default. The derivation night's input writer runs only when the default does not cover the machine's epoch; with the default covering 25G83 it refuses at a 25G83 machine (addendum A1 E12). Every non-claim capture at 25G83 would then go through capture preflight, which returns the default's level screen, so each would be screened by the held file's level screen."
- Replacement (D185): "rejected by addendum A1: both keep the new file as the default, and the derivation night's input writer runs only when the default does not cover the machine's epoch. At 25G83 it would then refuse, and every non-claim capture, including those the cap question needs, would pass capture preflight against the held file's level screen. The second option also leaves a manual campaign open."

### 4 (MAJOR). D185 Terms and Decision 3: the validator's forcing problem cannot be replicated from the entry
- Location: D185 Terms, the loader bullet: "... which checks the file's internal rules, among them that every valid capture of the registered sessions is a member or a named exclusion". Decision 3: "The loader's validator skips, in the prior set ..., exactly the eleven rows". Why: "those rows had been set aside by a written decision the validator did not know about."
- Why it fails: the rule the entry states covers only captures of the registered sessions. The eleven rows come from other sessions, so under the rule as stated nothing would refuse them. The rule that actually refused them, "any valid row at the file's epoch from a session outside the registration is refused" (IR §4.1), is not in the entry. "Skips" also names no check, which is the defect C1 fixed in NOTE but not here. The entry says it "can be applied without that record", and on this point it cannot.
- Replacement (Terms, loader bullet, the validator clause): "... and its content passes the **validator** (`_valid_acceptance_bound`), which checks the file's internal rules. Among them is the **completeness check**: every valid capture of the file's registered sessions must be a member or a **named exclusion** (a valid capture listed with a registered reason), and a valid capture at the file's epoch from a session outside the registration is refused. Otherwise members could be chosen after their values were seen."
- Replacement (Decision 3, first sentence): "The loader's validator leaves out of its completeness check exactly the eleven rows of the prior set (the file's copy of the ledger of all captures) that decision `D-126-disposition-25G83-v3-2026-09-25` set aside, matched by content identifier (a digest derived from each capture's evidence files). It does so only when the file declares that decision in `prior_observation_set.disposing_decision_ids`."

### 5 (MAJOR). IR header "State" bullet and D185 Status: key terms used before any definition
- Location: IR line 7: "the new file is issued and registered, but R7 stays the default calibration while hold H1 stands." D185 Status: "any change to the four estimator files ...", "which kept R7 as the default while the hold stands", "disclosures, holds, bindings, measurements and the old-epoch replay". The D185 Terms block comes after Status.
- Why it fails: R7, "hold H1", "the default" and "registered" (used here in the code-registry sense, not the §1 "Registration" sense) reach the reader of IR before §1 builds them. In D185, the whole Status paragraph is read before the Terms that build it.
- Replacement (IR line 7): "**State:** the transaction is built and **not merged**. On 2026-09-28 the design changed before merge (§4.5): the new file is issued and entered in the code's table of issued files, but **R7** (the calibration file in force today, which covers only the old macOS build 25F84; §1) stays the **default** (the file used when no file is named; §1) while **hold H1** stands (H1 keeps claim-bearing windows off the new file until a written ruling settles whether the cell cap biases which measurements survive; §4.4, §6). Open items are listed in §10. The after-merge measurements (§7.3) are placeholders until the merge."
- Replacement (D185): move the whole "**Terms, so the entry can be applied without that record.**" block to directly below the `## D-185:` heading, above "**Status:**". Add one Terms bullet: "The **old-epoch replay** evaluates one recorded 25F84 measurement at main and at the transaction's head and compares the outputs (design ruling §10 item 2)."

---------------------------------------------------------------------
## 2. MINOR defects: issuing record
---------------------------------------------------------------------

### 6 (MINOR). IR §1 table: first-use order (residual of A7)
- Location: "epoch" is first used in the Estimator row ("At this epoch's 128 to 130 ms frames") and in Capture preflight, but the Epoch row comes 10 rows later. "pins" is used in the Window row and "committed pin" in the Ledger row, before the Pin row. "R7's C" is used in the C row, before the Generation row. "hold H1" is used in the Default and Candidate rows, before the Hold row.
- Replacement: move the **Epoch** row and the **Pin** row to directly after the **Estimator and the cap** row. In the C row, change "C is the largest of three numbers: R7's C; S; ..." to "C is the largest of three numbers: the C of **R7** (the generation in force, below); S; ...". In the Default row, change "(§4.3)" to "(§4.3), while **hold H1** stands (below, Hold; §4.4)". Alternatively, move the **Hold** row to directly after the **Default** row.

### 7 (MINOR). IR §1 and §4.3: "register" in two senses
- Location: the Registration row defines "registration" as the sealed pre-capture document. The Candidate row ("registering it"), §4.3 title and first paragraph ("registered in `ISSUED_ACCEPTANCE_REGISTRY` and `_D102_GENERATION_DERIVATIONS`") and the header use "register" to mean entering the file in the code's tables. The table promises that "Every term below is used only in the sense given here."
- Replacement (Candidate row): "**Issuing** means turning the candidate into issued form, entering it in the code's tables of issued files (`ISSUED_ACCEPTANCE_REGISTRY`, `_D102_GENERATION_DERIVATIONS`; this is not the Registration document below), and pinning the new file's digest in the loader." In §4.3, change the title to "The default stays R7; the new file is entered, pinned and held" and change "registered in" to "entered in".

### 8 (MINOR). IR §2 opening paragraph: four terms before they are built
- Location: "The fix seat regenerates the issued bytes with the promotion tool (§4.2), because design addendum A1 changed three sentences of the issuance text (§4.2). Fields protected by test P2 (...)".
- Why it fails: "promotion tool", "issuance text" and "test P2" are first used here and built only in §4.2 and §7.2. The present tense "regenerates" also contradicts the finished digest in the table.
- Replacement: "The issued bytes were regenerated by the **promotion tool** (`scripts/promote_calibration_candidate.py`, §4.2), which writes the issued file from the candidate and the **issuance text** (`10-issuance-text.json`, the lead-written notes, disclosures and holds that the file carries). They were regenerated because design addendum A1 changed three sentences of that text (§4.2). The tool's test P2 (§7.2) requires that the regeneration leave these fields unchanged: identifier, epoch, n, S, C, level screen, cutoff, predecessor, member values and prior set. Only the file's digest and its whole-file seal change."

### 9 (MINOR). IR §4.5, doubling-fix bullet: "which is at most six brackets" has no derivation
- Location: "the file goes stale at the twelfth new valid capture at 25G83 (12 + 12 = 24), which is at most six brackets."
- Why it fails: the number depends on whether consecutive brackets share a capture, and the text does not say. It is a number without its working.
- Replacement: delete ", which is at most six brackets". If the count is kept, state its assumption: "which is six brackets if each bracket uses two new captures of its own".

### 10 (MINOR). IR §4.5: status stated as done, and "the judge" at first use
- Location: (a) "Each new test of the hold ... and the doubling tests DT-1 and DT-2 are run against `325d9f77` and shown to fail, then against `8458f797…` and shown to pass". §10 lists this as open. (b) "the judge confirmed by execution" is the first use of "the judge" in §4.5.
- Replacement: (a) "Each new test of the hold ... and the doubling tests DT-1 and DT-2 must be shown failing at `325d9f77` and passing at `8458f797…` (addendum A1 §8.1 step 3; open, §10)." (b) "the cold judge of design addendum A1 confirmed by execution".

### 11 (MINOR). IR §4.1 Mechanism: two opaque sentences
- Location: (a) "a caller that supplies another digest (tests do) gets a parse without it and must not treat the result as authority". (b) "The last rule is implied by the completeness equality and is kept as a second guard (addendum A1 N1; test L10 shows the second rule can be observed)."
- Why it fails: (a) "authority" does unpaid work. (b) "the second rule" can be read as "the second guard" in the same sentence, and the text does not say what L10 does.
- Replacement (a): "a caller that supplies another digest (tests do, to feed altered files) gets the file's rows without that check, and no code may use such rows to decide which rows the validator skips."
- Replacement (b): "The last rule is implied by the completeness equality and is kept as a second guard (addendum A1 N1). Test L10 adds to the code table a second decision that disposes one row of the prior set; the file does not declare that decision, so the load must refuse. This shows that the second rule in the list (the declaration must equal the disposing decisions) acts on its own."

### 12 (MINOR). IR §4.2: "preserved log" and "asserted a gate"
- Location: "It recomputes the preserved log's digest the way the block states it." Also "because the first bytes asserted a gate that was still open ... `required_verification` now says the merge gate is recorded in this record".
- Replacement: "It recomputes the digest of the **preserved log** (the saved copy of the time daemon's log, D8) the way the block states it." And: "because the first bytes stated that the merge checks of design ruling §9 (the **merge gate**: the checks this transaction must pass before it merges, §10) were complete when they were still open, and they omitted science addendum A3".

### 13 (MINOR). IR §4.4: three unbuilt phrases
- Location: (a) Forcing problem: "a hold that existed only as a sentence would be weakest at the moment of merge". (b) Place 2: "the floor mint's allowance projection" (the floor mint is built only later, in §4.3's third paragraph, and "allowance projection" never is), and "When bracket evaluation is handed a held file ...". (c) Release: "the cap council's plan" (the council is glossed only in §7.1).
- Replacement (a): "Windows are armed by an unattended loop that reads code, not prose. A hold written only as a sentence would stop nothing at the moment of merge, which is when the new file first becomes loadable."
- Replacement (b): "the floor mint's **allowance projection** (the step of the floor mint, §4.3, that computes a measurement's drift allowance, max(drift, S), from the calibration file)". And: "When bracket evaluation asks for a held file and the loader returns `None`, its freshness result reads status `stale` with reason `acceptance_artifact_claim_held` and the hold's name, instead of the `acceptance_artifact_missing_or_invalid` it gives for an unreadable file. Its refusal code stays `calibration_acceptance_bound_stale`."
- Replacement (c): "Under the plan of the cap council (the project's four-model review council sitting on the cap question as CAP-COUNCIL-25G83-01; §7.1), the file that becomes the default then will be a successor, not this one."

### 14 (MINOR). IR header: "science ruling", "design ruling", "new epoch", "digest X"
- Location: header lines 3 and 5.
- Why it fails: the reader is never told what the science ruling or the design ruling judged. "New epoch" and "digest X" arrive before §1.
- Replacement (append to the "What this record must hold" bullet): "The **science ruling** SCI-25G83-CANDIDATE-01 (with its addenda A1 to A3) is the cold ruling on whether the candidate's captures and numbers are sound enough to issue; its verdict was to proceed. The **design ruling** D138-25G83-DESIGN-01 is the cold ruling on how this transaction is built." In line 3, change "issuing a calibration for a new epoch" to "issuing a calibration for a new **epoch** (a new machine state, here a new macOS build; §1)". In line 5, change "digest X;" to "digest X (the sha256 of the issued file; §1);".

### 15 (MINOR). IR §5 "How to read them": D3's "structural reading" not built
- Location: D3 (exempt) says "under the structural reading ruled in §2.4". The surrounding prose glosses "the writer" but not this term.
- Replacement (append to the §5 gloss paragraph): "The **structural reading** in D3 is the first science ruling's reading (§2.4) of the registration's clock-alignment exclusion clause. The clause applies at the issuing step, to captures the writer recorded as valid. A capture the writer had already recorded `ordinary-invalid` never reaches that step, and is excluded as ordinary-invalid rather than under the registered class."

### 16 (MINOR). IR §7.2 and §10: "identity", "independent replay", "mutation evidence"
- Location: §7.2 second table, "at a 25G83 identity" / "25F84 identity"; §7.2 lead-in, "the re-hash and an independent replay are repeated"; §10, "the mutation evidence of design ruling §9 step 5".
- Replacement: "for a measurement whose epoch is 25G83" (and likewise for 25F84). In the lead-in: "the re-hash and an **independent replay** (the checks of design ruling §9 steps 1 and 2, re-run on the real ledger read-only; its last three rows below) are repeated by a seat that did not write them". In §10: "the **mutation evidence** (runs in which a named piece of the new code is deliberately broken, each of which a test must then catch) of design ruling §9 step 5".

### 17 (MINOR). IR §8: "candidate discovery" collides with the defined term "Candidate", and three phrases are unbuilt
- Location: Attempt 2, "(**candidate discovery**)". §1's Candidate row defines "candidate" as an unissued calibration file. Also: Attempt 1, "the W2 measurement checkout" and "R7 authenticated as fresh"; Attempt 2, "the whole-window verdict". The first mention is in §1's Derivation night row (`discover_calibration_candidates`), with no gloss.
- Replacement: "... the evaluator first finds the calibration captures taken just before and just after it (**bracket-capture discovery**; the code calls it candidate discovery, `discover_calibration_candidates`, a different sense from §1's Candidate)", and use "bracket-capture discovery" thereafter. In Attempt 1: "with the 276-row ledger in the working copy that ran window W2, whose ledger head equals the committed pin. At main `e7c8bcc6`, the loader accepted R7 and judged it fresh". In Attempt 2: "the whole-window verdict (the step that decides whether the window as a whole passed; lead to confirm the gloss)". In the §1 Derivation night row: "(the skip in bracket-capture discovery, `discover_calibration_candidates`, §8; ...)".

### 18 (MINOR). IR §1 worked paragraph: "binary64"
- Replacement: "evaluated in binary64 (IEEE 754 double-precision) floating point as the file's rule states".

### 19 (MINOR). IR §2 table: `claim_eligible: true` appears with no pointer
- Replacement (row "Role and issuance block", column 2): append "(what `claim_eligible` means: §4.6)".

---------------------------------------------------------------------
## 3. MINOR defects: D-185 entry
---------------------------------------------------------------------

### 20 (MINOR). D185 Terms: "cells" and "charged" left half-built
- Location: the estimator bullet ("165,000 evaluated regions (**cells**)") and the calibration-file bullet ("the smallest drift allowance any measurement is charged").
- Why it fails: Decision 5 says "the cap stops more captures when the sampler's frames are longer", but the entry never says why frame length drives cell count. The entry also never says what the allowance is added to.
- Replacement (estimator bullet, second sentence): "To locate each pulse's start and end it splits the range of candidate edge times into ever smaller regions, down to 0.1 ms, discarding regions that cannot fit; each region it evaluates is a **cell**. Longer sampler frames locate edges less sharply, so more cells are needed. The search is limited to 165,000 cells per capture (**the cap**); a capture that needs more is stopped and yields no B."
- Replacement (after the S sentence): "The measurement's timing uncertainty (its **operative bound**) is the larger of the two captures' B plus the allowance."

### 21 (MINOR). D185 Terms: "registration" and "R7's C" before their gloss
- Location: the calibration-file bullet ("the captures the registration selected"; "the largest of R7's C"). The registration is glossed only in Why, and R7 only in the next bullet.
- Replacement: "... of its **members** (the captures that the **registration**, a sealed document written before the captures, `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, selected) ...". Change "the largest of R7's C" to "the largest of the C of R7 (the old-epoch file, below)".

### 22 (MINOR). D185: unglossed actors and tools
- Location: Terms, "the preparation tool" (no path). Decision 2, "lead-written" and "the merge gate". Decision 4, "floor-mint pin files", then Options, "pinset schema" (a term shift, with the floor mint never built). Decision 5, "The arm admission list". Why, "the loader repair". Options, "`candidate_not_issued`", "code echoes that block" and "the arm-time authorisation record".
- Replacement:
  - Terms: "A **candidate** is a file the preparation tool (`scripts/issue_calibration_acceptance_generation.py`) wrote, marked "not issued" (key `candidate_not_issued`) ..."
  - Decision 2: "written by the lead (the Opus 5.5 session running this transaction)". Also: "that the **merge gate** (the checks this transaction must pass before it merges, recorded in the issuing record) is not asserted by the bytes".
  - Decision 4: "The **floor mint** computes a window's detection floors (the smallest energies it can resolve) from pin files called **pinsets**; the pinset schema (`scripts/floor_mint_pinsets/schema_v2.json`) now forces ...". Use "pinset" in Options unchanged.
  - Decision 5: "(3) The **arm admission list** (`_issued_d079` in `joulewise/arm_readiness.py`, the calibration identifiers a pack may name) refuses ..."
  - Why: "exercises the loader repair (item 3) ..."
  - Options: "code echoes that block" becomes "code copies that block into its outputs" (lead to confirm). "the arm-time authorisation record" becomes "the record written when a window is armed".

### 23 (MINOR). D185 Decision 6: "alone it would let the new file pass brackets as the default"
- Why it fails: under this entry the new file is not the default, so the reason reads as contradictory unless the reader knows it refers to the first build.
- Replacement: "The fix lands in the same commit as items 4 and 5, because in any commit where the new file is the default and the loader gate is absent (as in the first build), the fix alone would let the new file pass brackets."

### 24 (MINOR). D185 Revisit triggers: "That failure is closed" is glossed one sentence after use
- Replacement: "... of either epoch. The file then stops loading: the validator refuses it, because its declared decisions no longer match those that dispose its rows, and it is never accepted with an out-of-date declaration. Only a re-issue cures it." Delete the bracketed "("Closed": ...)" sentence. If the N3 text must stay verbatim, put it in quotation marks and keep the gloss as surrounding prose.

### 25 (MINOR). D185 Status: "science gate" is named but what it judged is not said
- Replacement: "the cold science gate SCI-25G83-CANDIDATE-01 (the ruling on whether the candidate's captures and numbers are sound enough to issue; "cold": written by a judge in a fresh session with none of the working context) ..."

---------------------------------------------------------------------
## 4. Index row and dated note
---------------------------------------------------------------------

- **Index row (line 231): PASS.** It is a summary pointer. Its terms are built in the entry once items 4, 5 and 21-22 land. "The loader skips exactly the eleven D-126-disposed rows" will read correctly once Decision 3 says "leaves out of its completeness check" (item 4). Optional: mirror that wording in the row.
- **Dated note (line 12200): PASS.** C1 and C2 are applied. "Completeness check" is built by the following sentence, "corpus-doubling trigger" is glossed at use, and the tool, test and table are named by path. No defect found.
