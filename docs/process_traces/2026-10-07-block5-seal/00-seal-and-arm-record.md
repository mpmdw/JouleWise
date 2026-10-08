# Measurement block 5: the seal and hand-off record (2026-10-07 21:21 PDT to 2026-10-08)

Written on 2026-10-08 by an Opus 5.5 seat for the orchestrator of interactive session e4fc0437, from the
session's running record (`/Users/edr/night-archive/gate-prune/wave-1007b/WAVE.md`, from its entry of 21:21), the
ruling files that record names, and the notes of the seat that built the clones
(`/Users/edr/night-archive/gate-prune/wave-1007b/landing/NOTES.md`). Paths that begin with `gates/`, `premortem/`
or `bench/`, and file names in capitals, are in this directory.

## 1. What this record is, and the words it uses

This is the account of one night's work: what was decided and done between the moment the session resumed on the evening of 2026-10-07, which
the session record labels 21:21 PDT, and the moment the rules of measurement block 5 were sealed, with each check that was
made, what it found and where its record is. It is written for a reader who was not there.

- **Measurement block 5** is three unattended measurement runs on one Mac. Each run is a **window**. Each window
  runs one **pack**, a fixed, committed set of experiment inputs; the packs are called ALPHA, BETA and GAMMA.
  Block 5 is the first block whose numbers are meant to carry claims in a paper.
- The **registration**, the **analysis plan** and the **flag catalog** are the three documents that fix the rules
  before any data exists: what is measured and which recorded conditions remove data; how the numbers are
  computed; and what each recorded condition (a **flag**, named by a code) does. They are in
  `configs/campaigns/v5_claim_25g83/`.
- A **seal** is a list of SHA-256 digests, each of a named file at a named commit, written after an independent
  gate has judged those files. The list is `SEAL_RECORD.md`.
- A **window input** is a tracked file a window can read: every file under `joulewise/`, `scripts/` and
  `configs/`, and the one document `docs/phase_2/window_runbook.md`. **H_claim** is the commit that holds the
  final bytes of every window input. The **seal commit** is its only child on the integration branch and changes
  only three files (the **seal documents**: the registration, the plan, and the **sealed inventory**, which lists
  the SHA-256 of every code and pack file at H_claim). The **record commit** follows the seal commit and adds this
  directory.
- A **seat** is one model session working to a written brief. The **orchestrator** is the interactive Opus 5.5
  session that leads the work. The **magistrate** is the headless Opus 5.5 session that a scheduled job, the
  **watchdog**, starts on the Mac whenever no window is in progress; from the hand-off on it arms and harvests the
  windows alone. While a remote branch named `ops/stop*` exists (the **stop ref**), the watchdog starts nothing.
- A **lane** is a branch for one piece of work, in its own checkout. The **integration branch** is
  `integrate/2026-10-07-int5` (pull request #489); the **design branch**, on which the three documents were
  drafted, is `design/2026-10-05-v5-claim-block-draft`.
- A **gate** is a check by a seat that did not write what it checks. An **independent executing review** runs the
  code on inputs of its own. A **cold pass** is a last reading by a Fable 5.1 session that took no part in the
  work and starts with no knowledge of it; a **cold gate** is a judgment made the same way. A **refuter** is a
  seat whose brief is to show a rule or the code giving a wrong outcome.
- The **harvest** is the program that runs at the desk after a window has ended: it checks the window's bytes and
  writes which measurements are kept. The **measurement clone** is the one checkout the windows run from; the
  **desk clone** is the separate checkout the harvest runs from.
- A **reference** is one run of a small fixed workload placed at the start, the middle and the end of a window;
  the **drift screen** compares the references' energies to decide whether the instrument drifted.

## 2. Where things stood at 21:21 PDT

The session had started at 15:30 on 2026-10-07 and had stopped at 16:45, when the account reached its usage
limit; every seat stopped with it. It resumed on the owner's word (section 6), at the entry the session record
labels 21:21. At that moment:

- Nothing was armed. The magistrate was held by the stop ref `ops/stop-pause`.
- The integration branch was at `9b0c680ed`. The registration and the plan were at revision 9, a draft.
- The seal gate had been dispatched at 16:15 as stage 1 of two (section 5, ruling 1). Its refuter had finished
  (`REFUTER_STAGE1.md`); its judge had been cut off with a partial ruling.
- A sweep of the registration's text against the code had finished at 16:13: 2,011 statements checked, 73
  mismatches confirmed (`gates/56-fidelity-sweep.md`). The orchestrator had ruled on them at 16:20
  (`gates/52-fidelity-rulings.md`): each sentence that misdescribed the code is corrected to the fact, no code
  changes before the seal, and two items go to the judge.
- The seal-landing lane (`lane/2026-10-07-seal-landing`), which makes the harvest treat the seal's own commits as
  no change to the code, was written; its review had been cut off.
- The owner had decided at about 16:05 that the first window is armed as soon as the seal path completes, with
  no wait for desk work (section 6).

## 3. What was done, in order

The rows are in the order of the session record, and the first column is the label the record gives each entry.
Those labels are not clock readings throughout: the record itself says that its labels after the resume were
estimates that ran ahead of the machine's clock, and that it read the clock from 22:55 on. The commits' own times
show how far a label can be off: the merge the record labels 21:38 was committed at 21:24, the merge it labels
23:15 at 22:23, and the seal commit, which it labels 01:30, at 01:15. So wherever a row names a commit, the third
column gives the time stored in the commit, and wherever a seat's own record gives its times, those are given
too. Those are the times to rely on. All times are Pacific Daylight Time.

| Label in the session record | What was done | Result, with the time a commit or a seat's own record gives |
|---|---|---|
| 21:21 | The session resumed, on the critical path only, with few seats at once. A test email was sent from the session. | The send succeeded. |
| 21:25 | The orchestrator read the refuter's record: five breaks (RF-1 to RF-5). It wrote its proposed dispositions as positions for the judge to rule on. | Section 5, ruling 2. |
| 21:30 | Started: the stage-1 judge again from the beginning; the independent executing review of the seal-landing lane; the two regions of registration revision 11 that had been cut off; the refuter of the attribution-floor investigation. | The judge's record gives its session as 21:24 to 21:54, and the review's record gives 21:24 to 22:40. |
| 21:38 | The orchestrator accepted the seal-landing procedure and merged the lane into the integration branch. | `9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a`, committed 21:24; section 5, ruling 3. |
| 21:42 | Started at that merge: Fable delta cold pass 5; the nine generator and pin checks, the refusal census and the whole test suite. | The cold pass's record gives its start as 21:25. Sections 4.2 and 4.3. |
| 21:55 | The pre-mortem of the first window resumed: its four unfinished lenses, verifiers for the findings that would lose a window, and the synthesis. | Section 4.5. |
| 21:58 | Pull request #489 was opened as a draft, from the integration branch into main, so that CI would run. | GitHub gives its creation as 21:29. |
| 22:05 | The orchestrator ruled on the attribution floor. | Section 5, ruling 4. |
| 22:10 | Cold pass 5 returned. | PASS WITH NOTES; section 4.2. |
| 22:20 | CI on the draft failed on Linux in its job `quick`, with two tests, so the jobs that run the full suite were skipped: the branch had never had a full Linux run. A lane for the Linux failures was started. | Section 5, ruling 5. |
| 22:30 | Stage 1 of the seal gate returned its ruling. | `STAGE 1: RULINGS COMPLETE`; the judge's session ended at 21:54. Section 4.1. |
| 22:32 | The seal-rulings lane was started: the catalog change and the three allowlist changes the judge required, with their tests. | Its last commit, `a0920cb8c`, is timed 22:08. |
| 22:50 | The review of the seal-landing lane returned. The orchestrator ruled on its findings. | Section 4.4; section 5, ruling 6. |
| 22:58 | Revision 11 of the registration was merged on the design branch. Revision 12 was started: five writers, a merger, two reviewers and one reviser. | `7c19c9c79`, committed 21:52. |
| 23:02 | The harvest lane was started: an author, then an independent executing review and a cold Fable pass. | Section 4.8. |
| 23:15 | The seal-rulings lane was merged into the integration branch. | `cc0b3446d`, committed 22:23; no file under `joulewise/` or `scripts/` changed. |
| 22:55, read from the clock | The pre-mortem was complete. The orchestrator decided its eleven questions. The scratch directories of the rehearsals under `/private/tmp` were deleted to free disk. | Section 5, ruling 7. |
| 23:17 | The owner answered the question of which account the Mac stays logged in to. | Section 6; the release no longer waits on it. |
| 23:17, about an event at about 23:05 | Three seats had been stopped when the owner sent a message: the suite run, the CI lane and the writers of the hand-off documents. The state each had left on disk was read, and the CI lane and the hand-off documents were started again. | The suite had finished at 22:41; section 4.3. |
| 23:10 | A seat of an unrelated paper lane was found to have put the owner's mail address into requests to scholarly sites. A rule was added for every seat: the owner's address, name and account identifiers go into no network request. | |
| 23:35 | Revision 12 was written, merged, reviewed and revised on the design branch. The orchestrator ruled on the reviser's two open cures. | `f7c643457`, committed 23:28; section 4.7; section 5, ruling 8. |
| 23:46 | The harvest lane was done. | `c10257418a9d7d2173bec306c0b1deb38e144343`, whose last commit is timed 22:47; both of its gates PASS WITH NOTES; section 4.8. |
| 23:48 | The final text was on the design branch. Stage 2 of the seal gate, part A, was started on it. | `c7408819c`, committed 23:45; section 5, ruling 9. |
| 23:55 | The hand-off drafts were done. The orchestrator wrote nine decisions on them. The documents the magistrate and the window read at run time were merged into the integration branch. An independent executing review of the seal-rulings lane was started. | `4394ca891`, committed 23:49; section 5, ruling 10. |
| 00:01 | The review of the seal-rulings lane returned. | PASS WITH NOTES; section 4.6. |
| 00:05 | Part A of stage 2 returned. Its four required changes were applied word for word. | `STAGE 2A: TEXT ADMITTED WITH REQUIRED CHANGES`; design branch `9864f7163`, committed 00:06; integration branch `1704059cc`, committed 00:07; section 4.9. |
| 00:55 | The CI lane was done: every Linux job passed on its head. The orchestrator ruled on the lane's two open items. | `3ff380b74`, committed 00:42; GitHub gives the run as 00:42 to 01:09. Section 4.10; section 5, ruling 11. |
| 01:10 | H_claim was fixed by merging the CI lane into the integration branch. The runbook's first two steps passed. | `a64000884ef5bb4b76415835f02f39803f6eb620`, committed 01:10; section 7. |
| 01:15 to 01:25 | A seat filled the places in the registration and the plan that waited for H_claim: its name, and eight digests computed at it. The orchestrator corrected one sentence of the registration's section 0.18 that misstated which revision of the two texts H_claim's tree holds. | Final text: design branch `cf92f73ec207634d5b2b3a76cae41d3e626befee`, committed 01:15. |
| 01:30 | The seal commit was made. | `ab7b21e576a2d74f0b25d9a26b463d6934588368`, committed 01:15; section 7. |
| 01:30, read from the clock | Part B of stage 2 returned. | `SEAL: ADMIT`, subject to five conditions; the judge's session ended at 01:26. Section 4.11. |

What followed the seal commit is in section 7.

## 4. The gates, each with its result and its record

### 4.1 The seal gate, stage 1

A Fable 5.1 judge and an Opus 5.5 refuter, on revision 9 of the three documents and the code at `9b0c680ed`.
Records: `RULING_STAGE1.md` and `REFUTER_STAGE1.md`, byte copies of the gate's own files.

The refuter reported five breaks. The judge accepted four with a cure and confirmed the fifth rule with its stated
reason corrected (`SEAL_RECORD.md`, section 3, has one line for each). The ruling's first line is
`STAGE 1: RULINGS COMPLETE`. It required:

- one change to the catalog: the smallest number of kept units a reported quantity may have, of its 10 planned,
  goes from 8 to 5. The judge's reason: discarding a window because a quantity kept 7 units is a preference for
  precision, and only a wrong or unattributable number or a measured physical hazard may remove data; 5 is the
  point below which the registered estimator cannot compute its result.
- 48 changes to the text of the registration and the plan, each written out word for word (T-1 to T-48);
- seven changes to code or to records in the code tree (K-1 to K-7). Three are entries of the refusal allowlist,
  the file that lists every place where code may stop collection or remove data. Four are changes to the harvest.

It required no change to code that runs during a window. It left one question, the table of pinned digests, to
stage 2.

### 4.2 Fable delta cold pass 5

A Fable 5.1 cold session on the code merged since the previous cold pass, `fe28e5a0c..9395cecfb`. Record:
`gates/40-cold-pass-5.md`. Result: **PASS WITH NOTES**. It found sound the rule by which a window detects agent
processes and the seal-landing change (fourteen cases, each run through the harvest and through the window's own
collector on a real git repository), and the four estimator files that may never be edited are unchanged. It
found one defect and itself classed it as a flag and not a reason to refuse: a commit after H_claim that changes only
another pack's directory removes a window that never read that directory. That cannot arise when the registered
procedure is followed, and it errs toward removing data. It went to the harvest lane as item H-12. Three notes
were carried forward: a stale note in the catalog, which was rewritten before H_claim; a window started from a
second checkout is recorded with no flag, which was first put as a question for stage 2 and, once the
seal-landing review had found the same gap, became item H-8; and a stale clause in a comment of the harvest,
which became item H-13.

### 4.3 The whole test suite at `9395cecfb`

Record: `gates/22-whole-suite-9395cecfb.md`. 9,842 tests. Five failures in three modules, each of which passes
when its module is run alone. The seat that ran the suite showed that four of the five are caused by the way the
run feeds its runner program on standard input and say nothing about the code; the fifth is a timing test. The
nine generator and pin checks and the refusal census passed at the same commit.

### 4.4 The independent executing review of the seal-landing lane

An Opus 5.5 seat that wrote none of the lane, at `2737ef88c`. Record: `gates/10-seal-landing-review.md`; the
procedure it reviewed is `gates/12-seal-landing-procedure.md`. What the lane was asked to change behaves as it
says: in sixteen cases a changed window input still removed the window, and no permitted commit did. The review
made nine findings, F1 to F9: one MAJOR gap that predates the lane (F1: a window started from a second checkout
with different code raises no flag), two MINOR ones (F2, F3) and six notes, all in checks the harvest makes after
a window. The orchestrator's ruling on
each is `gates/50-seal-landing-dispositions.md` (section 5, ruling 6).

### 4.5 The pre-mortem of the first window

Eight lenses, each asked to assume that the first window had been armed from the runbook and had failed, and to
find the cause beforehand; verifiers for every finding whose effect would stop or remove a window; one synthesis.
Record: `premortem/PREMORTEM.md`. Fifty-five findings; twenty-five were sent to a verifier and all were confirmed;
none was refuted. Nothing in the code path was found likely to lose the first window. What would have lost it was
the hand-off around the code, and each such finding is now a step of the runbook or a sentence of the magistrate's
brief: the orchestrator's own session is an agent process and a window refuses to start while one is alive; a
window must not be harvested before the harvest program is pinned; and a shell variable does not survive from
one command of a headless session to the next. The orchestrator's decisions on the pre-mortem's eleven questions
are `premortem/ORCHESTRATOR_DECISIONS.md` (section 5, ruling 7).

### 4.6 The independent executing review of the seal-rulings lane

An Opus 5.5 seat that wrote none of the lane, at `a0920cb8c`. Record: `gates/11-seal-rulings-review.md`. Result:
**PASS WITH NOTES**. The minimum of 5 decides through the real exclusion path on all three real packs (5 kept
units: usable; 4: the window is removed); the code's older default of 8 is never consulted with the sealed
catalog; every deliberate fault the reviewer put into the code was caught by a test. Four notes, all about
wording (a stale "8" in three code comments), were left for after the seal.

### 4.7 The review round of registration revision 12

Two Opus 5.5 reviewers and one reviser, on the merged text at `7e5eaa6c9` of the design branch. Record:
`gates/60-revision-12-review-round.md`. The verbatim reviewer checked that each of the judge's 48 changes stands
exactly as written: no blocker, one MAJOR finding, four MINOR and five notes. The pedagogy reviewer checked that
every term is built before its first use: five MAJOR findings, fifteen MINOR and four notes. The reviser applied
all of them (`f7c643457`) and left two cures for the orchestrator's ruling (section 5, ruling 8).

### 4.8 The harvest lane's two gates

The lane `lane/2026-10-07-harvest-lane` carries ten changes to the harvest, one commit each: K-4 to K-7 from the
judge, and H-8 to H-13 from the seal-landing review and cold pass 5 (`gates/15-harvest-lane-worklist.md`; the
author's report is `gates/17-harvest-lane-author-return.md`). It changes only `joulewise/b5/harvest.py`,
`joulewise/whole_window.py`, `scripts/harvest_b5_window.py` and tests, adds no flag code and changes no catalog
entry. Both gates judged the head `c10257418`:

- the independent executing review, by an Opus 5.5 seat: **PASS WITH NOTES**, three MINOR findings and four notes
  (`gates/13-harvest-lane-executing-review.md`);
- the cold pass, by a Fable 5.1 session: **PASS WITH NOTES**, two MINOR findings and five notes
  (`gates/14-harvest-lane-cold-pass.md`). It ran the drift screen with the registration's own numbers and got
  the ruled outcome in every case, and found that a lost reference's energy reaches no deciding comparison.

No fix round was needed. Each record ends with a table of what was done with each finding. The lane is not part
of pull request #489: it reaches only the desk clone (section 7, step 7).

### 4.9 The seal gate, stage 2, part A

A new Fable 5.1 session on the final text at `c7408819c` of the design branch. Record: `RULING_STAGE2.md`, under
"Part A". Result: `STAGE 2A: TEXT ADMITTED WITH REQUIRED CHANGES`. All 48 stage-1 changes are present; the
orchestrator's four later rulings are confirmed; every changed number was recomputed and agrees; the catalog is
admitted unchanged. It required three changes to the registration's text and one sentence of the refusal
allowlist. All four were applied word for word before H_claim.

### 4.10 CI on the tree of H_claim

Record: `gates/70-ci-linux-run-at-h-claim-tree.md`. Run 37745108000 passed every one of its 20 jobs on
`3ff380b74`, the head of the lane `lane/2026-10-07-ci-linux-fixes`. H_claim is the merge of that lane into the
integration branch, and the two commits hold identical files. The lane's fixes are confined to seven files under
`tests/`.

### 4.11 The seal gate, stage 2, part B

Another new Fable 5.1 session, held once the seal commit existed. Record: `RULING_STAGE2.md`, under "Part B".
Result: **`SEAL: ADMIT`, subject to five conditions**. Every check that can be made at the seal commit was made
by running it, and passed (`SEAL_RECORD.md`, section 3, says which). The five conditions are in `SEAL_RECORD.md`,
section 6.

### 4.12 Gates on earlier ranges of the branch

These were run before this night and are copied here because the pull request's ledger and the registration cite
them: the blind audit of the whole system at `a434e363d` by three seats, a Fable, an Astra and an Opus one
(`gates/30-triple-audit-fable.md`, `gates/31-triple-audit-astra.md`; the Opus seat's report was not found as a
file, only its probe outputs, so it is not copied); two delta audits by a Sol seat
(`gates/33-sol-delta-audit-1.md`, `gates/34-sol-delta-audit-2.md`); Fable cold passes 1 to 4
(`gates/35-cold-pass-1.md` to `gates/38-cold-pass-4.md`); and the record of the frozen head `fe28e5a0c`
(`gates/21-frozen-head-4.md`).

### 4.13 Gates still open when this record was written

- The whole test suite at the seal commit (run 9) finished at 02:29 PDT with 9,853 tests and five failures inside the shards, each passing when its module is run alone and when the runner is saved as a file (record `gates/20-whole-suite.md`). It finished after this record's first draft, so it is no longer open.
- CI at the record commit, which is the head of pull request #489. It had not run when this record was
  written. A commit cannot hold the result of the checks that run on it, so that result is recorded in the pull
  request's ledger, whose row 3 names the head at which CI passed.

## 5. The orchestrator's rulings, each with its reason

1. **The seal gate runs in two stages** (16:15, before the resume). Stage 1 rules on every question while the
   code head is still open; stage 2 judges the final text and writes the seal line. *Reason:* a ruling that needs
   a code change is cheap only while the head is open; once it is fixed, a code change costs a new run of the
   whole suite and a new cold pass. At 23:48 the orchestrator split stage 2 into two parts: part A reads the
   final text at once, and part B checks the digests and the seal's commits once they exist.
2. **Dispositions proposed to the judge for the refuter's five breaks** (21:25;
   `/Users/edr/night-archive/gate-prune/wave-1007b/seal-gate/STAGE1_ADDENDUM.md`). No change to code that runs
   during a window before the seal; the cures on the harvest's side go into a harvest lane that is pinned before
   the first harvest; the catalog's minimum of kept units is the judge's number to set. The judge adopted the
   harvest-side cures and set the minimum at 5.
3. **The seal-landing procedure is accepted as the lane wrote it** (21:38): H_claim holds the last change to a
   window input; the seal commit is its only child and carries the filled inventory and the final registration
   and plan; the seal record is a documents-only commit after it; the measurement clone is checked out at the
   seal commit. The lane's wider scope for what still counts as a change (all of `configs/`, and the window
   runbook) is accepted with it. *Reason:* a file cannot name the commit that contains it, and the inventory
   names H_claim; without the procedure the seal's own commit would have removed every window.
4. **The attribution floor is registered as a formula, and no number is bound**
   (22:05; `gates/53-attribution-floor-ruling.md`, from the investigation `gates/54-attribution-floor-report.md`
   and its refutation `gates/55-attribution-floor-refutation.json`). The attribution floor is a bound on how
   exactly an energy can be assigned to one phase of a run. *Reason:* the number is not a constant of the
   instrument; every input to it changed for block 5; nothing in block 5 is decided by it; and binding the older
   value of about 1 J would print a floor the instrument does not have.
5. **The rule given to the CI lane** (22:20): fix a test where the defect is in the test; a change to a window
   input is a labelled candidate that the orchestrator rules on before the head is frozen. CI passing on the
   final head, the merge of #489 and the fast-forward of the canonical checkout all come before the stop ref is
   deleted.
6. **The findings of the seal-landing review** (22:50; `gates/50-seal-landing-dispositions.md`). None changes a
   window input before the head is frozen; each goes to the harvest lane (items H-8 to H-13). *Reason:* every
   one of those checks lives in the harvest, which runs after a window from the desk clone, and the judge had
   already ruled that a harvest lane lands there after the seal. One exception is a change before H_claim: the
   catalog's note about its own status was rewritten to a sentence that is true before and after the seal,
   because the catalog is a window input and its bytes freeze at H_claim.
7. **The pre-mortem's eleven questions** (22:55; `premortem/ORCHESTRATOR_DECISIONS.md`). H_claim waits for the
   full Linux CI run. Two optional changes to the watchdog do not land before the freeze. The documents a
   headless session reads at run time are rewritten before H_claim, so the measurement clone holds them. The
   harvest lane is to be pinned before the arm; if it has not passed when everything else is ready, the arm does
   not wait and the first window alone is held for it. The first window is itself the measurement of this
   machine's contention. The desk clone is its own clone at the harvest lane's head. The magistrate opens only a
   short list of a window's outputs before the measured values are released. The owner's two standing directive
   issues stay open. The rehearsals' scratch directories are deleted. No GAMMA rehearsal precedes the seal, and
   the risk is recorded. The permission settings for headless sessions are not edited on a seat's report; the
   question goes to the owner.
8. **The reviser's two open cures in revision 12** (23:35; `gates/60-revision-12-review-round.md`, part 3). The
   rule that decides whether two failed attempts of a pack share a cause is built only from records that may be
   opened during the block. The registration's question on the limits of the rule that detects agent processes
   is closed on the evidence of cold pass 5 and is not left to stage 2. Part A of stage 2 confirmed both.
9. **The order of the seal's commits** (23:48): the seal commit is made before part B writes the seal line, so
   that part B can check it, and the record commit is made after the line.
10. **Nine decisions on the hand-off drafts** (23:55;
    `/Users/edr/night-archive/gate-prune/wave-1007b/handoff/ORCHESTRATOR_FIXUPS.md`). The seal record's directory
    and file names are the ones the registration prints. The harvest addendum is a section of the seal record.
    The harvest lane has its two reviews. The desk clone's commit is the harvest lane merged with H_claim. None
    of the owner's issues is closed. The magistrate may also open the arm record `hazards/arm.json`, because the
    registration's rule for shared causes names it. The CI lane's one candidate change to window-time code is not
    taken (ruling 11). The owner's answers stay at their defaults. The whole suite at the record commit is run by
    the same method as before, with the five known failures run again alone.
11. **The CI lane's two open items** (00:55). `tests/fixture_signatures.json`, a test-side file that the
    watchdog's informational record of orphaned processes reads, is accepted. The candidate change to
    `scripts/run_campaign.py` (commit `9271df94f`) is not taken for block 5. *Reason:* it hardens the reclaiming
    of a stale lock file against a file system that reuses inode numbers, which the Linux CI runner does and the
    Mac's volume does not; it is code that runs during a window, so taking it would need a review and a further
    cold pass for no effect on the measurement machine.
12. **H_claim is the merge of the CI lane** (01:10), `a64000884ef5bb4b76415835f02f39803f6eb620`. Its tree equals
    the tree of the lane's head on which CI passed. Since the head cold pass 5 judged, nothing under `joulewise/`
    or `scripts/` changed, and under `configs/` only the flag catalog and the refusal allowlist.

## 6. The owner's words that the session record holds

These are the owner's own words as the session record quotes them, each with the time the record gives.

- About 16:05, on arming the first window: "ok go ahead with the window, ping me when to /exit this interactive
  session so you can have a quiet machine".
- 21:21, on resuming after the usage limit reset: "ok keep working".
- 21:25, on the mail connector: "i think i fixed the block on gmail".
- 23:17, on which account the Mac stays logged in to: "oh ill probably keep both for one more month so no worries
  about that, dont trip about which account leave that to me".

## 7. After the seal commit: the runbook's steps as they were run

The runbook is `30-post-seal-runbook.md`. Steps 0 to 2 were run by the orchestrator; steps 3 to 7 by a separate
Opus 5.5 seat, whose notes are `/Users/edr/night-archive/gate-prune/wave-1007b/landing/NOTES.md`.

| Step | What it printed |
|---|---|
| 0. The values file and the state at the start | The stop ref was present, no window job was loaded, and no block-5 plan existed. |
| 1. H_claim | Every check passed at `a64000884`: the catalog's digest `5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d`, the minimum 5, the sizing output `89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa`, the inventory still its stub, and the landing test 9 tests, OK. |
| 2. The seal commit | `ab7b21e576a2d74f0b25d9a26b463d6934588368`: one parent, H_claim; its difference from H_claim is exactly the three seal documents; the inventory `57ee5d4a8ce632dfca7858f8f834d75dce463276b35fffc4edad91af2d76312a` lists 682 files and names H_claim; the landing test 9 tests, OK; a map generated again equals the committed one; `gen_state.py --check` and `repin.py --check` pass. The registration is `4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841` and the plan `1172a4501e2311a98508e6102420de657daa88c8c455603717b8ff7b2a1e1b8a`. The commit was pushed first to the branch `seal/2026-10-08-block5-seal-candidate`; the integration branch on the remote stayed at H_claim until the seal line, and pull request #489 showed the seal commit as its head when this record was written. |
| 3. The measurement clone | `/Users/edr/night-custody/measurement/JouleWise-measurement-20261008T0817Z-b5`, a full clone at the seal commit, clean; its difference from H_claim is the three seal documents. |
| 4. The environment | `brew pin python@3.13` is set. The environment equals the committed lock (37 packages); its digest is the sealed one, `9033a69906aab1f0ff5724b5a6c2f3efd623512ee49a7048713e2410e701c794`; the identity pins generated again equal the sealed ones for all nine units. |
| 5. The ledger seed | Block 3's final calibration ledger (402 rows, `6ee89e5a1b83c88d865a65cca71177d19a4b23b47d6af2979f92a6840857530e`) is installed; it reads back at row 402, equal to the committed pin, with no refusal. |
| 6. The bench | The four helpers are installed with the expected digests. A scratch plan for each pack was accepted by the plan writer, the chain check and the installer's render mode, and the identity checks a window makes at its start, run with H_claim as the reference, raised no flag. Members 119, 119 and 101. The six digests are in `SEAL_RECORD.md`, section "Plans written after the seal". |
| 7. The desk clone | The harvest lane was merged with H_claim: `7e6158d669cbb6fb35761aee18abf363f07c5d36`. Its difference from H_claim lists the three harvest program files and three test files; the three program files are byte-identical to the reviewed head's. Tests at that head: 204, OK, and 204, OK. The desk clone `/Users/edr/night-custody/desk/b5-harvest` is at that commit, clean. A rehearsal of the harvest's identity steps from the desk clone against the measurement clone raised no flag for any pack. `SEAL_RECORD.md`, Addendum 1, pins that commit. |
| 8. The record commit | Prepared on the branch `lane/2026-10-08-seal-record`: this directory, one test change and the new top block of `RUN_STATE.md`. The test change: `tests.test_docs_freshness` requires a section of executed evidence in every dated ruling file; the copy of the stage-1 ruling is a byte copy whose digest the gate pins, so that one path is exempted, with the reason in the test. Landing it on the integration branch is the orchestrator's step. |
| 9 to 15 | Not run when this record was written: the suite and CI at the record commit, the pull request's ledger, the merge, the canonical checkout, the readings before the release, stopping every agent, the email to the owner, and deleting the stop ref. |

Free disk read 203 GiB after step 7.

## 8. What was deferred, and to which lane

| What | Where it goes | Source |
|---|---|---|
| The harvest changes K-4 to K-7 and H-8 to H-13 | The harvest lane, done and pinned by Addendum 1 of the seal record before the first harvest | `RULING_STAGE1.md`; `gates/50-seal-landing-dispositions.md` |
| A reference that the verdict writer reads but the harvest's fresh reduction cannot read still removes the window | Lane L9-NEG8 (one rule, for every program, for which references survive), after the block and before any claim | `gates/13-harvest-lane-executing-review.md` R-1; `gates/14-harvest-lane-cold-pass.md` HC-5 |
| Folding the harvest's three replay settings into one rule; a fixture written by the real verdict writer and harvested by the real harvest | Lane L9-NEG8, its first stages | `gates/14-harvest-lane-cold-pass.md` HC-0; `gates/13-harvest-lane-executing-review.md` R-7 |
| Treating the corpus members whose physics was not measured as the references are now treated | To be considered in lane L9-NEG8's design before the first GAMMA window | `RULING_STAGE1.md`, finding 11; `gates/15-harvest-lane-worklist.md` |
| The harvest's wider class of window inputs also catches a change to the environment lock file, which no block-5 program reads | The harvest lane after block 5, as a flag and not a removal | `RULING_STAGE2.md`, part A, section C.2 |
| The analysis code (lane L9) and lane L9-NEG8 | After the block closes and before any measured value is opened; written blind; pinned by a second addendum to the seal record | `RUN_STATE.md`, the block-5 block |
| Four notes of the seal-rulings review (a stale "8" in three code comments) | After the seal | `gates/11-seal-rulings-review.md` |
| The candidate change to the stale-lock reclaim (`9271df94f`) | Parked until after block 5 | Section 5, ruling 11 |
| Two optional watchdog changes (the release of a window whose result email failed; a plan that never started) | The first desk session after the first window, on main | `premortem/ORCHESTRATOR_DECISIONS.md` O-2 |
| The GAMMA diagnostic references' own yield minimum; judging a clock series on the samples that did read; redaction of restricted codes in three of the harvest's files | The list for after block 5; the last one in lane L9 before any release | `gates/52-fidelity-rulings.md` |
| A rehearsal of GAMMA's verdict writer on real bundles | Not done before the seal; if the first two windows show a defect in the writer, the cure and a re-issued seal come before GAMMA | `premortem/ORCHESTRATOR_DECISIONS.md` O-10 |
| Whether the permission settings for headless sessions cover the block-5 programs | The owner; the settings change only on his own word in the session | `premortem/ORCHESTRATOR_DECISIONS.md` O-11 |
| The five questions put to the owner at the hand-off (whether the magistrate may quit an application or end a session it finds; whether an issue opened from the Mac notifies him; the lead between the arm notice and the window; a manual release command) | The owner; each has a default that is in force until he answers | `40-magistrate-brief.md`, section 2 |
| Why one timing test's child process outlives its signal inside the suite's third shard | Not concluded; the test passes alone | `gates/22-whole-suite-9395cecfb.md` |

Two notes of the harvest lane's gates have no ruling in the session record and no lane yet: the cold pass's HC-3
(a reference whose files vanish after its verdict) and the optional code change of the review's R-4 (recording
the digest of every module the harvest imports). Neither asked for a change before the lane is pinned.

## 9. What was still open when this record was written

- The whole suite at the seal commit: finished, see section 4.13.
- CI at the record commit, which the pull request's ledger records (section 4.13).
- `RUN_STATE.md`: part B's first condition lets the record commit change only paths under `docs/` and
  `tests/`, and `RUN_STATE.md` is at the repository's root; the orchestrator ruled on 2026-10-08 that its new block is committed to the main branch as a documents-only commit directly after the pull request's merge and before the stop ref is deleted (registration section 11 item 1, class iii).
- The runbook's steps 9 to 15.
