# Changes: D-185 texts revised per the pedagogy pass and design addendum D138-25G83-DESIGN-01-A1

Sources: the pedagogy pass (`50-d138-issuance-seat/refuters/pedagogy-pass.md`, sha256 `bcf56c26…87be`); design addendum A1 (`11-d138-design/31-addendum-ruling.md`, sha256 `4ddcd14b…d0b`, records branch). Nothing was written under /Users/edr/code/.

## Before you run gen.py

- **Unfilled placeholders break it.** gen.py's last `assert '{' not in s…` fails on any unfilled placeholder. Fill them in `prose.md` first, then point gen.py at the revised prose (it reads `/tmp/d185gen/prose.md`). I tested this in scratch with dummy values (`_gen_test.py`, which writes to `/tmp/d185rev/_render.md`): the render completes, all D/H verbatim asserts pass, and the output is 359 lines.
- **Placeholders you asked for:** `{HEAD}`, `{NEW_DIGEST_X}` (digest X = the loader pin) and `{NEW_WHOLE_SEAL}`.
- **Placeholders I added:**
  - `{ISSUANCE_TEXT_SHA256}`: `10-issuance-text.json` changed at `6ed6c1d5`. Its current sha256 is `fea3454620a18467b248eea2dbd427c1d95c5a894577fed3999dbe572f70908c`, but I left a placeholder in case you edit the file again.
  - `{MAIN_AT_REPLAY}`, `{OLDEPOCH_MAIN_SHA256}`, `{OLDEPOCH_HEAD_SHA256}` and `{OLDEPOCH3_PATH}`: the old-epoch re-run of addendum §6 item 1.
- **Cells to fill after gen:** the cells marked "*to be filled*" in the second table of §7.2 (pre-issue checks repeated at `{HEAD}`) and in §7.3. They are plain text, not placeholders.
- **Revised prose is not yet in the record.** The committed record has a closing section, "Re-issue before review", that is not in `/tmp/d185gen/prose.md` (it was added to the record directly). The revised prose now includes it, renamed "Re-issues before review" and with a 2026-09-28 entry added.

## Issuing record (`prose.md`): changes by section

- **Header.**
  - The "Words about the process" bullet moves to the top (A2). It is extended with D-138 and the inheritance corollary (A1), and with magistrate, activation, activation record, cold final pass and refuter (A2). I also added **fix seat**, a new term.
  - "Owner" becomes "Author" (A3).
  - The "must hold" bullet gains the A4 glosses. It also cites design addendum A1 by path and digest, lists that addendum's §7.1 additions, and tells it apart from science addendum A1.
  - The head is now `{HEAD}`, and the first-build and first-draft heads are kept as history. The state bullet is rewritten, and a revision line was added.
- **§1 table.**
  - Rows are reordered (A7): B, then Estimator/cap, then Window, then the rest. The Ledger row comes after Level screen, not directly after B, because the systematic-invalid definition uses "level screen".
  - Rows rewritten: S and C (A5), Estimator/cap (A8), Ledger with dispositions (A7/A9), Seal (A10), Prior set (A9), Disposed row plus content identifier (A11), Candidate plus tool path (A15).
  - Rows rewritten because R7 stays the default: Default, Generation and Loader (Loader also adds the validator gloss).
  - New rows: Bracket evaluation (inside Bracket), Capture preflight, Hold/**held file**, **Derivation night** and **Doubling trigger**. Addendum §7.2 requires that these new terms be built.
  - Worked C paragraph (A5) and operative-bound paragraph (A6).
- **§2.**
  - Digest X, the whole-file seal and the issuance-text digest are now placeholders.
  - A new paragraph says which fields test P2 protects through the regeneration.
  - The network-time block's built keys are stated, and I say that they follow science addendum A3 (N6).
- **§3.** Adds the "owner" gloss (A3).
- **§4.1.**
  - "Named exclusion" is glossed at first use (A12).
  - The worked-example contradiction is resolved with 30 + 12 + 11 = 53 (A12 and addendum §5 flag ii).
  - The decision sentence and the older generations' prior-set mode are glossed (A13, checked: 38 rows, R7 cutoff 76).
  - Adds the comment on the N4 table-equality check and the second guard on rule (f) (N1, L10).
  - L9 is now the renamed `test_l9_all_files_load_without_registry_io`, which covers the new file as well as the old ones (N5).
- **§4.2.** `backfill_candidate` is glossed (A14). A new paragraph covers S2 (the tool checks cited digests, P6) and S3 (three issuance-text fields changed; the bytes are regenerated).
- **§4.3.** Rewritten as "The default stays R7; the new file is registered, pinned and held" (R-1), and the loader behaviour is stated. It keeps the three R7 freezes (addendum §3.4) and adds the floor-mint and pinset glosses (A16).
- **§4.4.** Rewritten as "Hold H1 is enforced in code, at three places" (§7.1 row "Issuing record §4.4"):
  - It has a cap-question forcing problem (A17), then the three places (R-1, R-2/R-3/R-4, the admission list) with the readiness-evidence gloss (A17). It also covers R-5's diagnostic wording.
  - Release gains the route R/M glosses (A17), the import-check consequence and a note that the successor becomes the default (R-6).
  - Known cost uses the addendum §7.1 "Hold cost" text, in the record's own words.
  - "What is not closed by code" (R-7) is new.
- **§4.5 (new).** "Design change before merge (2026-09-28)" (task item e and addendum §7.1 row "new §4.5"):
  - It covers the forcing problem, then both refuters' routes, cited by path and digest, in a route table in which every column is named.
  - It explains the doubling defect and why it hid both routes (E9 to E11).
  - It explains the judge's choice among the three options and why (addendum §3.2), and states the doubling fix with numbers, the one-commit rule, and the RED/GREEN requirement.
  - It closes with the sentence "What is shown": no result can be produced through the code routes tested.
- **§4.6** (was §4.5). Adds one sentence: while the file is held, `claim_eligible` has no effect.
- **§5.**
  - "§ in D2" is merged into the existing sentence.
  - The A18 glosses are appended: statement, F1, the writer, clock method, custody, capture chain and A267. They carry corrections (see below), and a line saying they were checked at revision (addendum §7.2 note 3).
- **§6.** The custody sentence is deleted (A19). The text now says "three places".
- **§7.1.** Adds the council gloss (A20) and a pointer to the cap council addendum.
- **§7.2.** Test P2 is named (A21). A second table, "Repeated on the final head `{HEAD}`", follows addendum §8.1 step 4 and includes the new item (vi) expectations.
- **§7.3.** Rows rewritten per addendum §8.1 step 13: loader with no argument returns R7; the new path returns `None` without the keyword and the file with it; capture preflight refuses at 25G83.
- **§8 (old-epoch replay).**
  - Attempts 1 and 2 are kept, with the A22 and A23 glosses; the floor glosses gain their construction from the paper draft.
  - The lead's reading and the "Against the ruling's three outcomes" paragraph are replaced by "How the attempts stand": addendum §6 item 2 ruled STOP the correct reading, and the lead's reading was not adopted.
  - New subsections:
    - "The ruling for this transaction": met by identity, byte-identical re-run required (§6 item 1).
    - "Attempt 3": placeholders.
    - The restated condition for the later default-moving transaction, quoted verbatim (§6 item 3).
  - The Consequence paragraph is rewritten (this transaction removes no ability main has). "Lane" becomes "separate tracked work item" (A24), and a gloss is added after the verbatim ruling quote, which contains "lane".
- **§9.** Adds the write-scope gloss (A25), "at the bench" becomes "itself", and the preflight tests are glossed. A new paragraph, "Superseded by design addendum A1", says the re-pointed tests are restored to main's expectation, with no assertion weakened, and that the contract refuter checks this.
- **§10.** Rewritten from addendum §8.1:
  - the RED record, with its stop condition;
  - the re-hash at `{HEAD}`;
  - the old-epoch re-run;
  - the suite and mutations;
  - the two refuters' charges;
  - the pedagogy pass 2 and the cold final pass;
  - §7.3;
  - the explicit-R7 work item;
  - H5/H6;
  - the H1 release.
- **Closing section.** Renamed "Re-issues before review". The 2026-09-27 entry is kept as history, including the old digests `9e5c735b…` and `80c23036…`, which are history, not placeholders. A 2026-09-28 entry was added (S3 text change at `6ed6c1d5`, regenerated digests as placeholders).

## D-185 section, index row, dated note

- **D-185 section.**
  - Status now cites design addendum A1 by path and digest, plus `{HEAD}`.
  - Terms: new estimator bullet first (B2). The claim-bearing bullet moves before the calibration-file bullet and gains "derivation night". Also B1, B4 (validator, named exclusion), B5 (generation, disclosures, holds, bindings), and a new bullet for held file and non-claim purpose. The loader bullet adds capture preflight and bracket evaluation.
  - Decisions:
    - 1: placeholders and B6.
    - 2: S2 and S3 added.
    - 4: replaced ("the default does not move") plus B7.
    - 5: the addendum §7.1 exact text, with B3's cap-question text fitted after it, and "release is the only change that can move the default".
    - 6 (new): the doubling fix and the one-commit rule.
    - 7: the old item 6.
  - Why: B8 fitted (see below), plus why issue now (§7.1 "Likely re-issue" wording).
  - Options: two options added (the first design, and options a/b of addendum §3.2). The H1-as-sentence option no longer claims the admission list alone was chosen.
  - Considerations:
    - Hold cost and Likely re-issue: the addendum §7.1 exact texts.
    - Doubling trigger (new): the exact text.
    - What code does not close (new, R-7).
    - Old-epoch results: rewritten per §6, with B9 folded in.
    - Network time: B10 applied.
  - Revisit triggers: N3's exact text, followed by one added gloss sentence for "closed". The cold-final-pass trigger becomes the byte-identical re-run trigger, and the cap-ruling trigger notes that only the release may move the default.
  - The heading is left unchanged so the anchor stays stable; you may want to add "design addendum D138-25G83-DESIGN-01-A1".
- **Index row.** Digest placeholder; "the default moves" becomes "the default stays R7 while H1 stands"; the three enforcement points; the doubling fix. The status column cites the addendum and the old-epoch outcome. B11 said no change was needed, but addendum §7.1 required these.
- **D-126 dated note.** C1 and C2 applied. The note now names **two** new consumers: the validator and bracket evaluation's doubling count (addendum §4 adds a second read of this decision via `disposed_content_ids_for`). It cites addendum §4 and is marked "revised 2026-09-28".

## Pedagogy items not applied, or applied with changes

- **Not applied anywhere:** none of the 37.
- **A18, ruling A267: gloss corrected.** A267 is a work-queue item (QPE01-CLOCK-DISCIPLINE-ANCHOR-01); its cold gate ruled on 2026-09-22. The gloss now says what the queue records: timed corrections caused the clock movement, and the network-time-OFF control covered the idle-measurement chain only. The pass's "first diagnosed" was not verified.
- **A18, "the writer": gloss corrected.** It is the capture writer, the pinned code that writes each capture's disposition at capture time, before any B (science ruling §1 and §2.4). This is more precise than the pass's "recorded each capture's outcome".
- **A10: fields corrected.** The pass's "four fields … the entry that names its predecessor and registration" was inexact. From `derivation_input_sha256` the four fields are the screen rule, the predecessor id, the predecessor's C and the D-125 ruling. The sealed inputs also include `two_draw_prediction_derivation` and C − S among the operatives.
- **A8: mechanism and numbers adjusted.**
  - The mechanism is taken from the code (`_accepted_region_projection`): bisect the (start, end) square of ±0.75 s down to 0.1 ms, discarding pieces that cannot fit, with cells summed over the 59 pulses. The pass said only "subdividing the candidate range".
  - "Cleared by 20.3 %" is now "by 27,811 cells, 20.3 %".
  - The ≈120 ms frame length is attributed to D2, because the code comment does not state it.
- **A20: extended.** Also names CAP-COUNCIL-25G83-01 and the path of its addendum.
- **A23: glosses extended.** The floors now carry how each is built (repeat scatter; same-model A/B/B/A blocks), from `docs/paper/draft-v2-skeleton.md`.
- **A24: kept inside the verbatim ruling quote.** "Lane" inside the quoted design ruling §10 item 2 is verbatim and was kept; a gloss sentence follows the quote.
- **A17 Mechanism and B3: fitted to addendum §7.1** (addendum §7.2 note 1). The admission-list-only framing is gone.
- **B8: fitted.**
  - Present tense, as addendum §7.2 note 1 asks.
  - "Through the default" was added, because R7 stays the default and a held file can still be loaded by path with the keyword.
  - "No claim-bearing window could run" was dropped, because addendum §7.1 bars any statement that a claim at 25G83 is impossible.
  - For the same reason, one sentence in §4.5 was reworded to "kept any measurement … from becoming a result through the code".
- **B1: optional MINOR applied.** The claim-bearing bullet was moved before the calibration-file bullet.

## Facts checked at revision (read-only, in the impl worktree at `6ed6c1d5` plus the fix seat's uncommitted edits, and on the records branch)

- **Estimator and ledger:**
  - The cap comment (powermetrics_fiducial.py:77-88) and the bisection code (:646-699).
  - `content_id_from_artifact_hashes` and `CONTENT_ID_ARTIFACTS` (calibration_ledger.py).
  - The disposition file's mechanism sentence.
- **The issued file:**
  - Its prior set: 86 rows = 53/31/2; the two systematic-invalid attempts are 2026-07-26 and 2026-08-01; `excluded_members` = [].
  - Its keys, and the fields of `registered_generation_row` and `decimal_derivation`.
  - The older files have 38-row prior sets, and R7's cutoff is 76.
- **Tests and tools:**
  - The P2 test body.
  - L9's current name. It comes from the fix seat's in-progress tree, so re-check it at `{HEAD}`.
  - The preparation tool's path.
- **Issuance text:** the new `hold_enforcement`, `transaction` and `required_verification`, and the network-time block's keys.
- **Glosses and citations:**
  - H2/H3/B4 texts.
  - D-138's inheritance corollary.
  - D-184.
  - The A267 queue entry.
  - The science ruling's "valid" and "writer".
  - The paper's floor definitions.
  - `discover_calibration_candidates` skips historical imports (:1894-1925).
- **Digests:**
  - The design addendum's digest: `4ddcd14b…`, equal on the records branch and the bk worktree; not on origin/main yet.
  - The refuter reports' digests.

## For you to confirm at `{HEAD}` before landing

- **What I stated as fact is design as ruled, not yet verified at `{HEAD}`.** These statements rely on the fix seat implementing R-1 to R-5 exactly as ruled:
  - the keyword `allow_claim_held`;
  - the table `CLAIM_HELD_ACCEPTANCE_IDS` in calibration_bracketing.py;
  - the import refusal;
  - the diagnostic `acceptance_artifact_claim_held`;
  - the test ids HR-1 to HR-8, DT-1 to DT-5, L10, P6 and P7;
  - `tests/test_claim_hold_routes.py`.
- **§4.4 place 2's "no file under joulewise/ or scripts/ passes the keyword" is HR-6's claim; confirm it at `{HEAD}`.**
- **Addendum §8.1 step 9 requires a second pedagogy pass** on these revised texts.
