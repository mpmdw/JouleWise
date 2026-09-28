PEDAGOGY: FIX

Pedagogy pass (first-use test, why-chain, no unpaid words) on:
(1) docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance/00-issuing-record.md ("IR"), and
(2) docs/decision_log.md: the `## D-185:` entry ("D185"), its index row, and the dated note in the `D-126-disposition-25G83-v3-2026-09-25` entry ("NOTE").
Worktree read: /Users/edr/code/JouleWise-wt-d138-final-d528efb2 (read-only; nothing modified). Verbatim texts D1–D8, H1–H7, B1–B4 and quoted rulings were not judged internally; where they use a term the surrounding prose never builds, the fix goes into the surrounding "How to read them" prose.

Severity: MAJOR = a reader cannot replicate the mechanism or is misled; MINOR = order or gloss defect that a careful reader can recover from.

---------------------------------------------------------------------
## A. Issuing record (IR)
---------------------------------------------------------------------

### A1 (MAJOR). IR title and header: "D-138" and "a D-138 transaction" never explained
- Location: title line; header bullet 2 ("What this record must hold"); §4.2, §7.1 (B4 "D-138's inheritance corollary").
- Fails: D-138 is the authority for the whole transaction, but the record never says what it requires. D-185 glosses it; the record does not. "Inheritance corollary" (inside B4, exempt) is also never glossed in surrounding prose.
- Replacement: add as the first sentence of the "Words about the process" bullet (see A2 for moving that bullet up):
  "**D-138** is the project decision that any change to the four estimator files (the code that turns a calibration capture into its number B, §1) may land only inside one atomic transaction that also re-issues the calibration file those files produced; issuing a calibration for a new epoch goes through the same transaction. Its **inheritance corollary**, cited in B4, says that later changes to those files ride that same transaction branch rather than landing separately."

### A2 (MAJOR). IR header: "seat", "lead", "cold" used before they are defined
- Location: header bullet 1 ("the lead (Opus 5.5 magistrate, activation d528efb2) ... dictated-fills seat") and bullet 2 ("cold design ruling") precede bullet 3, which defines seat, lead and cold.
- Fails: first-use order. "magistrate" and "activation" are never defined anywhere in the record, and "activation item N" / "activation record" recur in §3, §8, §9.
- Replacement: move the "Words about the process" bullet to be the first bullet, and extend it to read:
  "- **Words about the process:** a **seat** is one delegated model session, and the **lead** is the session that runs this transaction. The lead here is the **magistrate**: the Opus 5.5 session that directs the project's unattended work loop. One run of that loop is an **activation**, named by an id (here d528efb2); its numbered log of actions is the **activation record**, and "activation item 17" is entry 17 of it. A **cold** ruling or pass is written by a judge in a fresh session with none of the working context; the **cold final pass** is the cold review of the finished transaction that must approve it before it merges. A **refuter** is a seat whose only task is to try to show a finding or a change wrong. **Sol** and **Astra** are OpenAI models; **Fable** and **Opus** are Anthropic models. ..." (rest unchanged).
  And change bullet 1's opening from "**Owner of this record:**" to "**Author of this record:**" (see A3).

### A3 (MINOR). IR header vs §3: "owner" used in two senses
- Location: header "Owner of this record: the lead"; §3 "The owner's approval of the name", D2 "The owner may overrule".
- Fails: "owner" means the lead in the header and the project's human principal everywhere else; the second sense is never glossed.
- Replacement: header "**Author of this record:** the lead ..."; §3 first sentence: "The **owner** is the project's human principal, who alone approves published names and claims. The approval is recorded as item 17 of ..."

### A4 (MINOR). IR header bullet 2: "the old-epoch replay" and "D1 to D8" arrive only in §5/§8
- Location: "That section asks for D1 to D8 in full; H1 to H7; bindings B1 to B4 ...; and the old-epoch replay of its §10 item 2."
- Fails: label list with forward pointers only; "old-epoch replay" is a mechanism name whose meaning arrives in §8.
- Replacement: "That section asks for: the disclosures D1 to D8 in full (facts the science ruling requires to be stated wherever the calibration is used); the holds H1 to H7 (conditions on later windows); bindings B1 to B4 (conditions on this transaction itself), with digests measured before the issue and after the merge; the owner's approval of the name; digest X; and the old-epoch replay of its §10 item 2 (a check that a measurement recorded under the old macOS build is not given a different number once the default calibration changes). Each has its own section below."

### A5 (MAJOR). §1 table rows S and C: "passes without comment" and "may be budgeted" do unpaid work; C's definition is incomplete until the paragraph below
- Location: rows **S** and **C**; then "The rule in force for this registration ... takes C as the largest of R7's C ..., this bound, and S."
- Fails: (i) "passes without comment" and "budgeted" are technical verbs whose meaning (the allowance rule, max(drift, S)) arrives only in "What S and C do to a measurement". (ii) The C row defines C as the prediction bound alone; the full definition (largest of three numbers) arrives two paragraphs later — a term whose meaning arrives in later text. (iii) "t(0.995, n − 1)" is not named as a Student-t quantile.
- Replacement for row S: "| **S** (bracket screen) | The spread of the members' B values (largest minus smallest), rounded to 1 µs. The **drift** of a measurement is the change in B between the calibration capture taken just before it and the one taken just after it. Every measurement is charged a drift **allowance** of at least S: the allowance is the larger of the drift and S (worked example below). |"
- Replacement for row C: "| **C** (maximum budgetable drift) | The largest drift that may be charged at all: a measurement whose drift exceeds C is refused. Under the rule in force for this registration (the D-125 addendum of 2026-09-25), C is the largest of three numbers: R7's C; S; and a 99 % prediction bound for the difference between two independent draws of B, t(0.995, n − 1) × s × √2, where t(0.995, n − 1) is the 0.995 quantile of Student's t distribution with n − 1 degrees of freedom and s is the members' sample standard deviation. |"
- Then in the worked paragraph, replace "The rule in force for this registration (the D-125 addendum of 2026-09-25) takes C as the largest of R7's C (0.010164834757777545 s), this bound, and S. The bound is the largest." with "Of the three candidates for C, R7's C is 0.010164834757777545 s and S is 0.013701 s, so the bound is the largest."

### A6 (MINOR). §1 "What S and C do": "timing bound" is never tied to what it bounds
- Location: "the measurement's timing bound is 0.036 + 0.013701 = 0.049701 s".
- Fails: the reader is not told what this number is used for, so the why-chain from B to the measurement stops one step short.
- Replacement: "... so the allowance is S and the measurement's **operative bound** (the timing uncertainty, in seconds, attached to the measurement when power frames are assigned to it) is max(0.030, 0.036) + 0.013701 = 0.049701 s."

### A7 (MINOR). §1 table: "window", "estimator", "cap", "invalid", "ledger" used in rows above the rows that define them
- Location: row **Level screen** ("stops a window"), row **Bracket** ("If the capture before it is invalid"), row **Epoch** ("estimator revision"), row **Seal** ("ledger cutoff"), row **Prior set** ("stopped by the cap").
- Fails: first-use order inside a table that promises "Every term below is used only in the sense given here".
- Replacement: move the rows **Estimator and the cap**, **Window, claim-bearing, arming, pack** and **Ledger** to directly after row **B**; move the definition of valid/invalid (see A9) into the **Ledger** row. No wording change needed beyond A8/A9.

### A8 (MAJOR). §1 row "Estimator and the cap": "cell" is "one unit of the estimator's search work" — not replicable, and the cap has no forcing problem or numbers
- Location: "A **cell** is one unit of the estimator's search work. **The cap** is the limit of 165,000 cells per capture".
- Fails: "search work" does not say what is searched; the reader cannot connect cell counts to frame length (D2, D7 rely on it) or see why 165,000.
- Replacement: "The **estimator** is the code that turns a capture's raw bytes into B. It lives in four files (§7). To find each pulse edge it searches over candidate edge times, subdividing the candidate range down to 0.1 ms; each region it evaluates is one **cell**. Longer sampler frames leave each edge less sharply located, so the search evaluates more cells. **The cap** is the limit of 165,000 cells per capture (`DETECTION_PROJECTION_CELL_BUDGET`). It was set on 2026-08-18 from 34 complete captures at frames of about 120 ms, which needed 112,205 to 137,189 cells; 165,000 cleared that maximum by 20.3 %. A capture that needs more is stopped and yields no B. At this epoch's 128–130 ms frames captures need 144,037 to 170,965 cells (D2)."
  (Source: comment above `DETECTION_PROJECTION_CELL_BUDGET`, joulewise/powermetrics_fiducial.py:77-88, and D2.)

### A9 (MAJOR, and a FACTUAL flag for the factual lane). §1 row "Prior set": "systematic-invalid" never built, and the gloss given is wrong for it
- Location: "86 rows here (53 valid, 31 ordinary-invalid, 2 systematic-invalid). Both invalid kinds are captures that yield no B."
- Fails: "systematic-invalid" is never defined; the sentence given ("yield no B") is untrue of it. The two systematic-invalid rows are 25F84 attempts `20260726T000039-491995f3` and `20260801T064830-c76f5d1c`, which yielded B values 0.035435840879704805 s and 0.0350400833260715 s above the level screen then in force (decision_log.md ≈ line 8000, "Disposition inventory (B1 lead-ruled)"; the rows are in the issued file's `prior_observation_set.observations`).
- Replacement: "| **Prior set** | The calibration file's own copy of the ledger rows that existed when it was derived: 86 rows here (53 valid, 31 ordinary-invalid, 2 systematic-invalid). A **valid** row yielded a B that passed every check. An **ordinary-invalid** row yielded no B: the capture was stopped by the cap or by a clock check. A **systematic-invalid** row yielded a B above the level screen in force when it was taken, which counts as a sign that the machine state itself had failed; the two here are 25F84 captures of 2026-07-26 and 2026-08-01. |"

### A10 (MINOR). §1 row "Seal": four undefined phrases inside the definition
- Location: "the ledger cutoff, ..., the quantile proof, the operative numbers and four fields of the registered row".
- Fails: "quantile proof", "operative numbers" and "registered row" are never defined; "ledger cutoff" precedes "Ledger".
- Replacement: "... covers only the inputs of the arithmetic: the identifier, the epoch, the ledger cutoff (the ledger row the derivation stopped at), the 12 member values, the statistics, the rounding rule, the stored check of the t quantile used for C, the three resulting numbers S, C and level screen, and four fields of the file's generation row (`registered_generation_row`, the entry that names its predecessor and registration). ..."

### A11 (MAJOR). "content identifier" used in §1 and §4.1 but never defined in IR
- Location: row **Disposed row** (implicitly), §4.1 worked example "the row's content identifier is in the decision's list", §4.1 Mechanism "eleven content identifiers".
- Fails: the skip mechanism keys on this identifier; D-185 glosses it, the record does not.
- Replacement: append to the **Disposed row** row: "Each ledger row is named by its **content identifier**: a sha256 digest computed from the digests of the capture's two evidence files (`manifest.json` and `instrument_evidence.json`, function `content_id_from_artifact_hashes`), so the name changes if either file changes."

### A12 (MAJOR). §4.1 worked example: an unresolved contradiction is left for the reader
- Location: "The file names no exclusion among valid rows (`derivation_notes.excluded_members` is empty). Design ruling §4.1 says one valid row is a named exclusion. The counts here are read from the issued file at drafting."
- Fails: the reader is handed two incompatible counts with no statement of which the mechanism uses or whether it matters; the sentence does unpaid work. Also "named exclusion" is never defined before first use in §4.1 Forcing problem.
- Replacement (Forcing problem, at first use): "... each must be a member or a **named exclusion** (a valid capture that the file lists in `derivation_notes.excluded_members` with a registered reason) ..."
- Replacement (worked example): "The file names no exclusion among valid rows (`derivation_notes.excluded_members` is empty), and 30 + 12 + 11 = 53 accounts for every valid row. The worked example in design ruling §4.1 counted one valid new-epoch row as a named exclusion; the issued file does not bear that out, and the check below uses the file's counts."

### A13 (MINOR). §4.1 Mechanism: "the exact mechanism sentence" and "a different prior-set mode"
- Location: "decision id → the exact mechanism sentence and the frozen set of eleven content identifiers"; "The seven older generations use a different prior-set mode and never reach this code".
- Fails: neither phrase is defined; a replicator cannot tell what text is compared or what distinguishes the modes.
- Replacement: "... decision id → the decision's sentence stating why the rows were set aside ("captured under the default-ProcessType launch context ...", copied exactly from the disposition file) and the frozen set of eleven content identifiers." and "The seven older generations were derived only from the 38-row import of historical captures at ledger sequence 76, with no captures of their own registered sessions, so their prior sets never enter the completeness check that this code sits in (design ruling §4.4 test L9 ...)."

### A14 (MINOR). §4.2: "`backfill_candidate`" appears without gloss
- Location: "marks `backfill_candidate` issued".
- Replacement: "sets the file's `backfill_candidate` block (the record of the preparation run's inventory and required checks) to status `issued`".

### A15 (MINOR). "the preparation tool" is never named by path
- Location: §1 row **Candidate**, §4.1, §4.3, D5 gloss.
- Fails: a replicator cannot find it. (Name not verified by this pass; the scripts/ directory holds `issue_calibration_acceptance_generation.py`, whose tests include `test_issuer_corpus_root`.)
- Replacement for row **Candidate**: "A calibration file written by the preparation tool (`scripts/<name>.py`) and marked "not issued". ..." — lead fills the exact path.

### A16 (MAJOR). §4.3: "pinset schema", "screen value" undefined
- Location: "The pinset schema `scripts/floor_mint_pinsets/schema_v2.json` gains a list for the new identifier that forces its screen value to `0.013701`. Before this change, an identifier in no list had an unchecked screen value."
- Fails: neither "pinset", "floor mint" nor "screen value" is built; the reader cannot see why an unchecked value matters.
- Replacement: "The **floor mint** is the step that computes a window's detection floors (the smallest energies it can resolve) from its evidence; each run reads a **pinset**, a JSON file of the identifiers and values it must use, and `scripts/floor_mint_pinsets/schema_v2.json` checks each pinset. The schema now has a list for the new identifier that forces the pinset's bracket screen to equal this file's S, `0.013701`. Before this change a calibration identifier in no list had its bracket screen unchecked, so a pinset could carry a wrong S without refusal."

### A17 (MAJOR). §4.4: "cap question" used before it is defined; "readiness-evidence row" undefined
- Location: §4.4 Release: "the written ruling that closes the cap question by route R or route M (H2, H3)"; Mechanism: "Such a pack cannot arm without a readiness-evidence row".
- Fails: "cap question" first appears here; its meaning arrives only in D2/D7 and H1 (§5, §6). Routes R and M are pointer-only.
- Replacement (add as the first sentence of §4.4 Forcing problem): "The **cap question** is whether the 165,000-cell cap, which stops captures that need more search work and so stops more of them when the sampler delivers longer frames, filters which measurements survive by machine state (D2, D7). Until it is settled, results at 25G83 may be biased toward the short-frame state."
- Replacement (Release): "... cites the written ruling that closes the cap question by **route R** (re-size the cap by a rule written before the new value is computed, then show that 24 captures under it stop none; H2) or **route M** (keep the cap and measure, in a registered plan, how brackets it abandons differ in energy and frame length from those it keeps; H3)."
- Replacement (Mechanism): "Such a pack cannot arm without a **readiness-evidence row** (a record, written by the arming code, that each named calibration identifier is admitted), and the code that writes that row always refuses ..."

### A18 (MAJOR). §5 "How to read them": several terms used in D1–D8 left unbuilt
- Location: §5 intro paragraph.
- Fails: the paragraph glosses many terms but omits: **statement** and its items ("statement item 7(b)", "item 4", "item 10" in D2; "statement item 6(d) R9" in D5); **F1** (D2); § signs in **D2** (the intro says only D3 and D4 carry § signs of the first ruling); **the writer** (D3); **the clock method** (D8, H5); **custody** ("nights in custody", D8 — defined only later in §6); **capture chain** (D8, and §6 intro); **ruling A267** (D8).
- Replacement: append to the §5 intro paragraph:
  "The **statement** cited in D2 and D5 is the refusal-branch statement `docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/00-refusal-branch-final-statement.md`, the pre-written list of what the science gate could decide and what each outcome forces; "item 7(b)" is its item 7(b). **F1** in D2 is the first science ruling's finding that the cap is mis-sized; the § signs in D2 also cite that ruling. **The writer** in D3 is the code that recorded each capture's outcome in the ledger. **The clock method** is the part of the estimator that places a capture on the wall clock by fitting a straight line through paired clock readings; it adds a fixed 250 µs allowance to every capture's B. **Custody** is the directory where a window's raw evidence is kept. A **capture chain** is the set of scripts that takes a window's captures; the calibration chain and the chain that takes idle measurements are separate. **Ruling A267** is the 2026-09-22 ruling that first diagnosed network-time corrections as a cause of clock movement."
  (The lead should verify the one-line gloss of A267 and "the writer" against their sources; this pass did not open them.)

### A19 (MINOR). §6 intro: "capture chain" and "custody" order
- Location: §6 intro defines Custody (needed earlier, in D8) and uses "capture chain" without gloss.
- Replacement: once A18 is applied, delete the §6 intro sentence "**Custody**, in H5, is the directory where a window's raw evidence is kept." (now built in §5).

### A20 (MINOR). §7.1: "council" inside B4 not glossed in surrounding prose
- Location: B4 (exempt) "the council rules in writing".
- Replacement: add before B1 in §7.1: "The **council** in B4 is the project's four-model review council (Fable 5.1, Opus 5.5, Sol 6.0, Astra 6; decision D-184). The inheritance corollary is glossed in the header (A1)."

### A21 (MINOR). §7.2: "test P2" unexplained
- Location: "yes (the file-level check is test P2)".
- Replacement: "yes (test P2, `tests/test_promote_calibration_candidate.py::test_p2_protected_paths_unchanged`, repeats the check on the written file)".

### A22 (MAJOR). §8 Attempt 1: "member" collides with the defined term; "decode-floor window", "canonical checkout" undefined
- Location: "The seat chose recorded member `sw7bfloor-df-ph-decode-abs-r01` of the passed claim-bearing 25F84 decode-floor window"; "(the one in the canonical checkout)".
- Fails: §1 promises every term is used only in its §1 sense; "member" there is a calibration capture, here it is a workload measurement. "decode-floor window" and "canonical checkout" are internal shorthand.
- Replacement: "The seat chose recorded measurement `sw7bfloor-df-ph-decode-abs-r01` of the passed claim-bearing 25F84 window of 2026-07-29 that measured detection floors for the decode (token-generation) phase of Qwen2.5 7B." and "(the one in the project's main working copy)".

### A23 (MAJOR). §8 Attempt 2: "absolute floor", "comparative floor", "historical imports", "candidate discovery", "floor mint ... input manifest" unbuilt
- Location: "records 6.294380135190098 J (absolute floor) and 13.998036715259254 J (comparative floor)"; "Both are historical imports (`historical-import-v1-finalization`), and current candidate discovery excludes historical imports".
- Fails: the whole STOP argument rests on "historical import" and "candidate discovery", neither built; the floors are numbers with no meaning attached.
- Replacement: "... records 6.294380135190098 J (absolute floor: the smallest energy a single measurement can resolve) and 13.998036715259254 J (comparative floor: the smallest difference between two measured conditions it can resolve)." and "**Why main produces no number:** to evaluate a measurement, the evaluator first finds the calibration captures taken just before and just after it (**candidate discovery**). For the July measurement these are ledger rows 58 and 60. Both are **historical imports** (`historical-import-v1-finalization`): captures taken before the ledger existed and entered into it afterwards, whose evidence was not produced by the current capture chain. Current candidate discovery skips historical imports (...)." For "generalized floor mint reads an acceptance path from its input manifest": "the generalized floor mint (§4.3) takes the calibration file's path from the list of inputs it is given".
  (Glosses of the two floors should be checked against the floor definitions by the factual lane.)

### A24 (MINOR). §8, §10, D185: "lane" is internal shorthand
- Location: IR §8 "Until a lane gives old-epoch results a route ..." and "That lane is to be opened by the lead"; §10 bullet 3; D185 Considerations "A lane is to give old-epoch results a route that names R7."
- Replacement: "lane" → "a separate tracked work item" at first use in each document, then "that work item".

### A25 (MINOR). §9: "write scope", "at the bench", "delegation wrapper", "repository-root preflight tests"
- Location: §9 opening and item 2.
- Replacement: "The ruling fixed the implementation seat's **write scope** (the exhaustive list of files it may change; the wrapper that runs it refuses any other edit) ..."; "the lead made that two-line change at the bench" → "the lead made that two-line change itself"; "two repository-root preflight tests" → "two tests in the same module that run the pre-window checks against the repository's own configuration".

---------------------------------------------------------------------
## B. D-185 entry (D185)
---------------------------------------------------------------------

### B1 (MAJOR). Terms bullet 2: S and C built with "passes without comment" and "may be budgeted"; C has no rule
- Location: "**S** ... is the largest change in B between the captures before and after a measurement that passes without comment. **C** is the largest such change that may be budgeted; above it the measurement is refused."
- Fails: same as A5; the entry claims it "can be applied without that record", but C cannot be recomputed from it.
- Replacement: "A **calibration file** holds the B values of its **members** (the captures the registration selected) and three numbers derived from them. The **drift** of a measurement is the change in B between the calibration captures just before and just after it. **S**, the spread of member B rounded to 1 µs, is the smallest drift allowance any measurement is charged (allowance = max(drift, S)). **C** is the largest drift that may be charged; above it the measurement is refused. Here C is the largest of R7's C, S, and t(0.995, n − 1) × s × √2 (Student's t quantile; s the members' sample standard deviation). The **level screen**, the largest member B, is the largest B a calibration capture at the start of a window may have; a larger one stops the window."
  (Also move the "claim-bearing window / arming / pack / hold" bullet before this one, or accept "window" as plain English — MINOR.)

### B2 (MAJOR). "estimator" / "the four estimator files" never defined in D185
- Location: Status ("any change to the four estimator files"); "What this does not change".
- Replacement: add a Terms bullet first: "The **estimator** is the code that turns a capture's raw bytes into B; it lives in four files (`joulewise/powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, `reduce.py`). Its search for pulse edges is limited to 165,000 evaluated regions (**cells**) per capture (**the cap**); a capture that needs more is stopped and yields no B."

### B3 (MAJOR). Decision 5: "the cap question" used before the cap is defined, and the question is never stated
- Location: "cites the written ruling that closes the cap question by route R or route M. Route R re-sizes the cap (the limit of 165,000 units ...)".
- Fails: first-use order; the question itself is never stated (route M's clause only hints at it).
- Replacement (with B2 in place): "... The hold is released only by a reviewed change that deletes the entry and cites the written ruling that closes the **cap question**: the cap stops more captures when the sampler's frames are longer (8 of the 24 captures here), and since a stopped calibration capture abandons its measurement, the surviving measurements may over-represent the short-frame machine state. Route R re-sizes the cap by a rule written before the new value is computed, then shows in at least 24 captures of windows without a claim that none stops on it. Route M keeps the cap and measures, in a registered plan, whether abandoned and completed measurements differ in energy and frame length."

### B4 (MINOR). Terms bullet 4: "validator" undefined
- Location: "its content passes the validator"; Decision 3 "The loader's validator skips".
- Replacement: "... and its content passes the **validator** (`_valid_acceptance_bound`), which checks the file's internal rules, among them that every valid capture of the registered sessions is a member or a **named exclusion** (a valid capture listed with a registered reason)."

### B5 (MINOR). "generation", "disclosures", "bindings" undefined in D185
- Location: Status ("disclosures, holds, bindings"); "What this does not change" ("binding B1", "the six older generations"); Options ("Disclosures inside the issuance block").
- Replacement: add to the Terms bullet on candidates/R7: "Each issued calibration file is a **generation** and names its predecessor; R7 is the seventh." Add a Terms bullet: "The science gate attached **disclosures** D1–D8 (facts to be stated wherever the calibration is used), **holds** H1–H7 (conditions on later windows) and **bindings** B1–B4 (conditions on this transaction: B1 fixes the estimator files' digests, B2 forbids changing them, B3 forbids curing a failure by re-preparing the candidate, B4 makes any later cap change a re-issue)."

### B6 (MINOR). Decision 1: "Whole-file seal" and "digest X" unglossed
- Location: "File sha256 (digest X, pinned in the loader)... Whole-file seal: `8477d8ce…`".
- Replacement: "File sha256 (called digest X in the issuing record; pinned in the loader) ... Whole-file seal (the digest the file stores over all its other keys): `8477d8ce…`."

### B7 (MINOR). Decision 4: "pinset schema" and "screen value" undefined
- Location: "The pinset schema forces the new file's screen value to `0.013701`."
- Replacement: "The schema that checks the floor-mint pin files (`scripts/floor_mint_pinsets/schema_v2.json`) now forces a pin file naming the new identifier to carry its S, `0.013701`; before, an identifier in no list had its S unchecked."

### B8 (MINOR). Why: "no claim-bearing window could be screened at it"
- Location: "No calibration file covered that epoch, so no claim-bearing window could be screened at it."
- Fails: "screened" is a technical verb with no built sense (the entry built "level screen", not "screened").
- Replacement: "No calibration file covered that epoch, so every measurement at 25G83 would be refused as stale and no claim-bearing window could run."

### B9 (MINOR). Considerations "Old-epoch results": "historical imports" and "candidate discovery" unbuilt
- Location: "because the July 2026-07-29 calibration rows are historical imports that current candidate discovery excludes".
- Replacement: "because the calibration captures taken just before and just after the July 2026-07-29 measurement were entered into the ledger after the fact as historical imports, and the current step that finds a measurement's before-and-after captures skips historical imports."

### B10 (MINOR). Considerations "Network time": term unglossed in D185
- Location: "The members were captured with network time ON (disclosure D8)."
- Replacement: "The members were captured with network time ON (the macOS setting "set time automatically", under which the time daemon `timed` corrects the wall clock during captures; disclosure D8)."

### B11 (PASS, note). Index row
- The index row is a summary pointing to the entry; its terms (input seal, hold H1, disclosures) are built in the entry once B1–B6 land. No change required.

---------------------------------------------------------------------
## C. Dated note on the D-126 disposition entry (NOTE)
---------------------------------------------------------------------

### C1 (MINOR). "skips exactly these eleven content ids": skips from what is not said
- Location: "When an issued calibration file declares `D-126-disposition-25G83-v3-2026-09-25` in `prior_observation_set.disposing_decision_ids`, the validator skips exactly these eleven content ids."
- Fails: "skips" names no check. A reader of the D-126 entry has no context that the validator refuses valid rows from unregistered sessions.
- Replacement: "When an issued calibration file declares `D-126-disposition-25G83-v3-2026-09-25` in `prior_observation_set.disposing_decision_ids`, the validator leaves these eleven rows of the file's prior set out of its completeness check. That check otherwise refuses any valid 25G83 row from a session outside the file's registration, and these rows come from the 2026-09-19 n1 and n2 sessions."

### C2 (MINOR). "the issuer" undefined in the note
- Location: "an equality check that the issuer and `tests/test_calibration_dispositions.py` both run".
- Replacement: "an equality check (`parse_disposition_registry`) that the calibration preparation tool runs each time it reads the registry file, and that `tests/test_calibration_dispositions.py` runs on every suite run."

---------------------------------------------------------------------
## Out of scope for this pass, passed to the factual lane
- A9: the IR claim "Both invalid kinds are captures that yield no B" is false for the two systematic-invalid rows (they carry B values above the level screen then in force).
- A12: the design ruling §4.1 and the issued file disagree on the number of named exclusions (1 against 0).
- IR header "head at drafting: `e14e00bb…`": the worktree HEAD is now `325d9f77` (a merge of origin/main). This is noted only, not judged.
