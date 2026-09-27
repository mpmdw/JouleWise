ADDENDUM: FINAL STATEMENT ISSUED

# Cold addendum REV5-REFUSAL-BRANCH-01-A1: the refuter's amendments, and the final statement

Judge: Fable 5.1, one non-interactive session, 2026-09-27, 12:24 to about 12:45 PDT.
No subagents, no background tasks, every command in the foreground. Scratch files are only under `/tmp/cg-refusal-a1-77b1bee2/`. That directory also holds `judge.out`, which no command of mine created; I take it to be the launcher's capture of this session and left it alone.

**Result in four sentences.**
- The refuter's main finding (SF-1) is true: I ran the issuing tool's own path function and it refuses on both windows' paths. With the tool as it stands, no calibration file can be written from W1 and W2.
- All seven of the refuter's points are adopted, five of them with changed wording (§4).
- The final statement is in §5. It supersedes §5 of the earlier ruling.
- The tool must be repaired before the issuance step runs. The repair's design goes to the four-model council, and a fresh cold gate rules on the final change. The owner's approval is not required (§6).

## 0. Contamination disclosure

- **Injected before my first turn, not by my choice:** the session harness placed four texts in my context: the owner's global instruction file, this repository's `CLAUDE.md`, the one-line index of the memory store, and a git status summary. The index carries one-line summaries of past rulings and checkpoints, including lines saying that W1 and W2 were armed. It states no measured value of W1 or W2. I opened no memory file behind it. The global instruction file contains a writing standard (define every term before use); I followed it as a matter of form.
- **Not read:** `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, any `CLAUDE*.md` file on disk, any memory file, any skill file, the activation record, the final-pass ruling, any email.
- **The charge file on disk** (`30-addendum/20-addendum-charge.md`): I printed its first three lines only, to confirm it is the charge I was given.
- **Measured values of W1 and W2:** I opened none. (The measured value is called B in this ruling: each capture's stored bound, in seconds, on how far its clock alignment can be off, held in the field `b_fiducial_s`.)
- **What I did do to W1 and W2 material, and why it shows no value:**
  - My script `locators.py` read the W2 measurement root's ledger as raw text and matched one field by pattern: the recorded directory path of each capture (`custody_locator`). It printed two path prefixes with the last path component replaced by `<attempt>`, and three counts. It parsed no row and printed no other field.
  - I computed sha256 digests of six files in the W2 measurement root. A digest shows nothing of a file's content.
  - I ran no part of the issuance step and opened no evidence file.
- **Values I did see, and why they do not bear on the outcome:**
  - The eleven B values of the 2026-09-19 captures. They are printed in the registration (Revision 5, "Disclosed design inputs") and in the decision log. They are not W1 or W2 values.
  - The registration's table of frame lengths and the battery capacity figures in amendment A-R5b. They are registration text.
  - W2's frame-cadence figures (median 128.5 ms, worst 141.4 ms), which the earlier ruling's own disclosure repeats. The registration allows that figure to be reported before any B value is read.
  - The path shapes (not the values) of the seventeen members of the July calibration file r7, to see how earlier calibrations recorded member locations.
- **Read as charged material, not trusted:** the original charge, the earlier ruling and the refuter's report. Every fact this addendum relies on was re-checked in this session and is listed in §1.

## 1. Executed evidence (this session)

| # | Check | How | Result |
|---|---|---|---|
| A1 | Working tree | `git rev-parse HEAD`, `git status --short` | `670756f3fbb366d9c40a7a128766c9afc5d331cf`, clean, before and after. |
| A2 | Registration digest | `shasum -a 256` | `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1` in my tree and in the W2 measurement root. |
| A3 | Issuing tool digest | `shasum -a 256` | `ceaf3807b2fde7d50374c4781e1c0eff3fb8fea38344b37950cf67fa8e757105` in my tree and in the W2 measurement root: the same file. |
| A4 | W2 measurement root | `git rev-parse HEAD`, `git status --short` | `722f7bd161f1a1d0ae2ef624f7f29aac3e347d82`, clean, before and after. It is a detached checkout: `722f7bd1` sits one commit above `a71a5e79` and is **not** an ancestor of `origin/main` `670756f3` (`git merge-base --is-ancestor`). |
| A5 | Recorded paths of W1 and W2 | `locators.py` on the ledger, masked | Two prefixes, 48 path strings each, all absolute: `/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/<attempt>` and the same with `w2`. |
| A6 | Is the custody tree under version control? | `git -C <dir> rev-parse --show-toplevel` on both window directories, on `/Users/edr/night-custody`, `/Users/edr`, `/Users` and `/` | "not a git repository" for all six. Neither window directory nor any parent is a symlink. |
| A7 | **SF-1: the tool's own function** | `sf1.py`: imported the issuing tool from my tree and called `_repo_relative_custody(<prefix>/MASKED-ATTEMPT, "MASKED-ATTEMPT", <root>)` for W1 and W2 against five roots | Against the W2 measurement root, the W1 measurement root and my working tree: `PrepareRefusal: member MASKED-ATTEMPT: custody … lies outside the repository, so no repo-relative source_directory exists`, six times out of six. Against `/Users/edr/night-custody` and `/`: a relative path is returned (see A8 for why that does not help). |
| A8 | Can an argument route around it? | `argcure.py`: called the ledger loader's `_committed_pin_bytes` and the battery module's `_git` with root `/Users/edr/night-custody` | Committed ledger pin: `None`. `git rev-parse HEAD`: `None`. The same two calls with the W2 measurement root as root succeed. So a root that contains the custody tree fails the tool's earlier checks. |
| A9 | Order of the tool's work | read the issuing tool :1025–1092, :1195–1428, :1650–1899, :2398–2488 | The custody refusal is raised inside the member loop (:1244, reached from :1827). It comes after the first valid capture's evidence is read and its stored B text is compared for equality with the ledger row (:1220–1242). It comes before the check for outside captures (:1844), the 0.075 s count (:1851), the 0.25 s check (:1852–1855), the floor check (:1856) and every statistic (:1862 on). |
| A10 | The two verifiers of an issued file | read `tests/verify_calibration_acceptance_corpus.py` :73–95 and `scripts/reissue_calibration_acceptance.py` :140–185 | Both join a root directory to each member's recorded relative path, require the result to stay inside that root, and check the files there. |
| A11 | The issued file's member format | read `joulewise/calibration_bracketing.py` :868–892 | Each member has exactly five fields: `member_id`, `source_directory`, `b_fiducial_s`, `manifest_sha256`, `instrument_evidence_sha256`. |
| A12 | The four estimator-code files | read `joulewise/calibration_bracketing.py` :206–211 | `joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`. None is the issuing tool, the validator or a verifier. |
| A13 | SF-2 facts | read :1667, :2046, :2131, :2398, :2412, :2468–2478; `calibration_bracketing.py` :515–523; decision log :12201–12203 | The reference string for the screen rule is checked only for being non-empty, and is written into the candidate file. The predecessor defaults to the active calibration, and Revision 5 refuses any predecessor but r7 (:1732). The decision-log heading and its "§5 R5(i) and R9" match the refuter's string. `--out` has no default. |
| A14 | SF-3 facts | read :1203–1257 and :1364–1376 | The check for outside captures skips every session the run names (`not in excluded_owners`). The member loop never consults the disposition registry. |
| A15 | N-a, N-d facts | read :1839–1850; `joulewise/battery_float.py` :514 | The tool's comment on an outside capture reads "Either way it is Ed's call, not the issuer's". Battery authentication reads each slot's `instrument_evidence.json` bytes, and it runs at :1752, before the member loop. |
| A16 | N-b, N-c facts | read :974–990; `gh issue view 416` | The issued file carries five named re-derivation triggers. Directive #416, clause 3, reads: "If the audit finds a defect in the calibration derivation path, W1/W2 are re-run before any headline run." |
| A17 | Texts quoted | read the registration :598–664 and :465–470; decision log :12170–12223; runbook :2568–2578 | Quotations in §3 to §6 are from these reads. |
| A18 | Digests of the run's inputs | `shasum -a 256` in the W2 measurement root | Listed in §5, item 2. The ledger is 641,850 bytes. |

**NOT EXECUTED**
- `prepare-candidate`: not run. A judge must not run it.
- The count-only dry run: not re-run. I rely on the earlier ruling's E6 for "12 valid, none excluded, no outside capture", and say so where it matters.
- Any read of a W1 or W2 ledger row's fields other than the recorded path; any read of an evidence or custody file.
- The test suite.
- Any design of the repair. §6 sets constraints only.
- A check of the owner's inbox.
- A paired refuter for this addendum. My protocol forbids subagents.
- The path and version of the project's own Python interpreter. My scratch runs used the shell's `python3`.

## 2. Terms used in this ruling

Each term is given here before it is used. Terms already defined in the earlier ruling keep their meaning; the ones this addendum leans on are repeated.

- **The issuing tool.** The script `scripts/issue_calibration_acceptance_generation.py`.
- **The issuance step.** The tool's command `prepare-candidate`. It either writes one candidate calibration file, marked not issued, or prints `REFUSED: <reason>`, writes nothing and exits with code 3.
- **Capture, window, valid, retained, member, B.** As in the earlier ruling: a capture is one 59-pulse calibration measurement; a window is one scheduled run of 12 captures; W1 and W2 are the two windows; a valid capture passed every protocol check; a retained capture (a member) is valid and its stored clock alignment resolves on read-back; B is defined in §0.
- **Ledger.** The append-only file in which each capture has rows recording its identity, its file digests and where its files are. Here: `runs/calibration_observation_ledger.jsonl` in the W2 measurement root.
- **Custody directory.** The directory holding one capture's files. Its ledger row records it as an absolute path, in the field `custody_locator`.
- **The custody tree.** The two directories `/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927` and `/Users/edr/night-custody/d079-epoch-25g83-derivation-w2-20260927`, which hold every custody directory of W1 and W2.
- **Git checkout.** A directory whose files are under version control by git. The tool asks git, in the directory it is told is its root, for the committed copy of two kinds of record.
- **Measurement root.** The git checkout a window was run from. The W2 measurement root holds the ledger with both windows' rows.
- **Root argument.** The tool's `--repo-root`. It defaults to the checkout the tool's own file sits in.
- **The custody fault.** The defect verified in §3: the tool can record a member's custody directory only as a path relative to its root, and W1's and W2's custody directories lie outside every checkout.
- **Curable, terminal, held.** The three classes of refusal fixed by the earlier ruling: corrected and re-run; ends the epoch under Revision 5; stopped until a second party rules.
- **Outside capture.** A valid capture of this epoch that belongs to neither W1 nor W2 and has not been set aside in the disposition registry.
- **Disposition registry.** The file `configs/calibration/observation_dispositions.json`, which lists captures set aside as diagnostics. The tool pins its digest.
- **The council.** The four-model review body of decision D-184. **The owner.** Ed. **The operator.** The session that runs the issuance step.

## 3. Ruling 1: SF-1 verified

### 3.1 What the tool does, and where W1 and W2 fall

**The forcing problem the tool's check solves.** An issued calibration file lists its members, and a later reader must be able to find each member's files and check them. If the file stored an absolute path such as `/Users/edr/…`, the check would work on this machine and on no other, without any warning. So the tool stores each member's directory relative to the checkout, and refuses if it cannot. The code comment says so (:899–903).

**Why that fails here.** Calibrations up to r7 kept their captures inside the checkout (r7's seventeen members are all under `runs_window_…/instrument_validation/`). W1 and W2 keep theirs in the custody tree, which is outside every checkout (A5, A6). The relative path the tool needs does not exist.

**Worked example (A7).** For the path `/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/MASKED-ATTEMPT` and the root `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2`, the tool's function computes "the first path relative to the second". The first does not start with the second, so the function raises the refusal quoted in A7. The same happens for W2's prefix, and for every checkout I tried.

### 3.2 Is the refusal certain?

**Yes, in this exact sense: with the tool at digest `ceaf3807…7105`, the issuance step cannot write a candidate from W1 and W2. Every run ends in a refusal. The refusal printed is the custody one unless an earlier cause refuses first.**

The order of the tool's work (A9), with every step named:

```
issuance step
 1. arguments, registration digest ................ refusals here are curable (item 5a)
 2. ledger load, committed ledger pin ............. curable (5c)
 3. predecessor file r7 ........................... curable (5c)
 4. battery records, recomputed from raw bytes .... curable by exact restore (5b), else terminal (4vi)
 5. window count, order, slot count, epoch ........ curable (5a) or terminal (4v)
 6. member loop, one valid capture at a time, in ledger order:
      a. read its files, check their digests ...... curable (5b)
      b. did its clock alignment resolve? ......... terminal if unregistered reason (4iii)
      c. stored B text equals the ledger row's? ... terminal (4iv)
      d. path relative to the root ................ THE CUSTODY FAULT: refuses here, on the
                                                    first capture that passes a, b and c
 7. outside captures .............................. never reached
 8. B against 0.075 s and 0.25 s .................. never reached
 9. floor of 12, statistics, S and C .............. never reached
```

Steps 1 to 5 passed in the count-only dry run the earlier ruling executed, which mirrors them. The dry run reported 12 valid and none excluded, so at least one capture passes 6a to 6c, and step 6d then refuses. Steps 7 to 9 cannot be reached by any run.

**One correction to the refuter's wording.** The refuter says the refusal comes "before any B value is compared". That is not exact. Step 6c compares the first capture's stored B text with the ledger row's text, for equality, before step 6d. What is never reached is any comparison of B with a limit, and any statistic. The refusal's message carries a path and a capture id. It carries no value. The conclusion stands: the refusal is value-blind.

### 3.3 Is it held, and not curable, under the statement?

**Yes. It is held.**

- The statement's item 6 holds "any refusal that could be removed only by changing code". This is one.
- No argument removes it. The only roots that contain the custody tree are `/Users/edr/night-custody` and its parents. None is a git checkout (A6), and the tool needs git at its root for the committed ledger pin and the battery records. Under such a root both come back empty (A8), so the run would refuse at step 2 or step 4.
- No restore removes it. The files are present and are where the ledger says they are.
- The remaining "cures" all change the evidence's location or fake a repository: moving or copying the custody tree, a symlink, or `git init` above it. The runbook already forbids the first: "The custody root of an unissued epoch is never moved, relocated or offloaded." A repository created above the tree would also have to contain commits of the ledger pin and battery records that satisfy the rule "exactly one commit in `HEAD`'s history touches its path" (binding reading A-R5b-1). That is manufacturing a record, not curing a command.

**The refuter's concern about item 5(a) is sound.** Item 5(a) lists "a wrong checkout, interpreter or file path" as curable. The custody refusal is worded in terms of a path. An operator could misfile it. The final statement closes this in two places: item 5(a) now says it covers paths typed on the command line only, and item 6(d) names this refusal and its class.

**The refuter's concern about the silent default is sound.** Item 6 said: "If the ruling is no, or if no ruling is given, the refusal is terminal". With no time bound, a fault in software could end the epoch because nobody acted. The earlier ruling's own reason for the held class was that this must not happen. A held refusal permits nothing (no re-run, no capture, no issuance), so leaving it held costs no safety.

## 4. Ruling 2: each amendment

| Point | Ruling | Reason |
|---|---|---|
| **SF-1** custody fault is certain; name it; repair before the first run; no silent default | **ADOPTED, AMENDED** | Verified (§3). Four changes to the refuter's text. (1) "before any B value is compared" becomes "before any B is compared with a limit" (§3.2). (2) The list of things that are never a cure gains symlinks, rewriting a ledger row's path, and pointing the root argument elsewhere. (3) Who rules on the repair is split into design and final change (§6). (4) A run that ends in exactly this refusal does not end the period in which the owner's override is outcome-blind, because it shows no value (item 10). |
| **SF-2** fix the run's inputs | **ADOPTED, AMENDED** | The reference string is written into the candidate file and checked only for being non-empty (A13), so leaving it open leaves a choice to be made after the outcome. The refuter's checkout condition cannot be met as worded: commit `722f7bd1` is not on the main branch (A4), and the repaired tool will arrive from the main branch. So the run's inputs are pinned by digest, not by commit (item 2). |
| **SF-3** the tool does not enforce (b) against a successor that names W1 or W2 | **ADOPTED** | Verified (A14). The earlier ruling's sentence "The tool already enforces (b)" is corrected to: the tool refuses a successor that leaves W1 and W2 unnamed, and nothing in code stops one that names them. The code guard is added to item 4(d). It is a new refusal, so it restricts and permits nothing. It is built with the change item 4(d) already requires, not before the run: adding code that is not needed for the run is not the smallest change. |
| **N-a** an outside capture should be held, not terminal | **ADOPTED, AMENDED** | The fault is not W1's or W2's, it is found without reading any value, and it can be removed only by a reviewed change to the pinned registry, which is the definition of held. The registration says such a capture "refuses issuance rather than being absorbed"; it does not say the epoch ends. My amendment fixes the only ruling open: set the capture aside as a non-member. Absorbing it stays forbidden. It is moot today if the dry run still reports none. |
| **N-b** "no value is a ground … to write a new registration" is too broad | **ADOPTED, AMENDED** | The registration itself attaches a consequence to the `excursion_limited` mark, and the issued file carries five re-derivation triggers (A16). The sentence was meant to stop anyone replacing this calibration because they dislike its numbers. The final text forbids "a successor registration for this epoch" on that ground, and says that the registration's own consequences and the issued file's triggers are untouched. |
| **N-c** cite directive #416 as the reason for item 7(b) | **ADOPTED, AMENDED** | Clause 3 verified (A16). I add the second reason, which is the principled one: once a candidate exists its values are known, so a repair can no longer be ruled blind. Item 6 can repair a tool because the refusal came first. I also fix which rule governs when 7(a) and 7(b) both seem to apply: 7(b). |
| **N-d** battery authentication reads evidence bytes before line 1827 | **ADOPTED** | Verified (A15). The earlier ruling's sentence is corrected to: "members' evidence is first read for its content in the member loop; battery authentication reads the same files' bytes earlier, to check digests and battery records, and prints nothing from them." The conclusion is unchanged: a refusal reveals only its reason text. No statement text changes. |

**Two amendments of my own, forced by SF-1.**
- **J-1 (item 10).** The earlier text made the owner's override outcome-blind "before the issuance step first runs". A run that ends in the custody refusal, or in a mistyped argument, shows no value. The final text ties the boundary to the first result that depends on a measured value, and lists the results that do not.
- **J-2 (directive #416).** Clause 3 orders W1 and W2 re-run if the audit finds a defect in the derivation path. The custody fault is not that case: it was found before issuance, it blocks issuance loudly, and its repair changes no capture and no number. Recapturing would cure nothing, because the capture files and their digests were fixed at capture. Item 9 says so. This reads the owner's own directive, so the owner may overrule it.

## 5. Ruling 3: the final statement

Paste the block below verbatim into the prepare record. It supersedes §5 of `21-coldgate-fable-ruling.md`.

> **Statement REV5-REFUSAL-BRANCH-01, final text.** Fixed before the issuance step first runs on W1 and W2. Ratified by cold gate ruling `40-refusal-branch/21-coldgate-fable-ruling.md` and amended by cold addendum `40-refusal-branch/30-addendum/21-addendum-ruling.md`, both 2026-09-27. This text supersedes the ten-item text of the first ruling.
>
> Words used.
> **The registration** is `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` at sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`; Revision 5 and amendment A-R5b are the parts in force.
> **W1** is session `d079-epoch-25g83-derivation-w1-20260927` and **W2** is session `d079-epoch-25g83-derivation-w2-20260927`; together they hold 24 captures, 12 valid and 12 ordinary-invalid.
> **The issuing tool** is `scripts/issue_calibration_acceptance_generation.py`. **The issuance step** is its command `prepare-candidate`. It either writes one candidate calibration file, marked not issued, or prints `REFUSED: <reason>` and writes nothing.
> **B** is a capture's stored timing bound in seconds (`b_fiducial_s`). **Retained** means valid in the ledger and resolved on read-back. A **member** is a retained capture.
> **The ledger** is the append-only file that records each capture's identity, file digests and file location.
> A **custody directory** is the directory that holds one capture's files; its ledger row records it as an absolute path. **The custody tree** is the two directories `/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927` and `/Users/edr/night-custody/d079-epoch-25g83-derivation-w2-20260927`.
> A **git checkout** is a directory under version control by git. **The run checkout** is the W2 measurement root, `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2`.
> **The disposition registry** is `configs/calibration/observation_dispositions.json`, the list of captures set aside as diagnostics.
> **The council** is the four-model review body of decision D-184. **The owner** is Ed. **The operator** is the session that runs the issuance step.
>
> 1. **Scope.** This statement grants nothing the registration does not grant. It fixes what follows each possible result of the issuance step, before any B value of W1 or W2 has been read by anyone. Its sha256 is committed and sent to the owner by email before the issuance step first runs.
>
> 2. **How the step is run.**
>    (a) The command is exactly this, run from the run checkout with the project's own Python interpreter (the one the harvest dry run was made with), whose path and version are recorded:
>    `scripts/issue_calibration_acceptance_generation.py prepare-candidate --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md --preregistration-sha256 81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1 --registration-session-id d079-epoch-25g83-derivation-w1-20260927 --registration-session-id d079-epoch-25g83-derivation-w2-20260927 --d125-ruling "docs/decision_log.md, D-125 addendum (2026-09-25): Revision 5 screen and ceiling for epoch 25G83/v3 (ACCEPTANCE-25G83-02 §5 R5(i), R9)" --out <path>`
>    (b) `<path>` names a new file outside `configs/` and outside the custody tree.
>    (c) No other argument is given. In particular the step is not given `--nights-ruling`, `--slot-count-ruling`, `--ed-ruling`, `--battery-confounded-session-id`, `--predecessor-acceptance`, `--epoch-catalog-id`, `--acceptance-id`, `--ledger`, `--head-pin` or `--repo-root`. `--minimum-corpus-size` is omitted or is 12. If the repair of item 6(d) adds an argument that names the custody tree's parent directory, that argument is given as the repair's ruling fixes it, and is the only addition.
>    (d) Before the run, four files in the run checkout have these sha256 digests, which are their digests at commit `722f7bd161f1a1d0ae2ef624f7f29aac3e347d82`:
>    the ledger `runs/calibration_observation_ledger.jsonl`, `23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d`;
>    the ledger head pin `configs/calibration/calibration_ledger_head.json`, `5dbac530fbaebecfcd730acf1e49f9e2dff315da282382b5e6b5812fcd04aad5`;
>    W1's battery record `configs/calibration/battery_float_verdicts/d079-epoch-25g83-derivation-w1-20260927.json`, `07bcc13b6f476c72280a74e21bfc2499b9085f5bf380cf891afa7f341fa535a2`;
>    W2's battery record `configs/calibration/battery_float_verdicts/d079-epoch-25g83-derivation-w2-20260927.json`, `51f4961828a440cbab5c7cf504d7e4536b25243414441dab5fedfb6f28f946ec`.
>    The four digests are checked and recorded immediately before the run. If one differs, the step is not run and the difference is a held matter under item 6.
>    (e) The run checkout's commit and the issuing tool's sha256 at run time are recorded. The checkout differs from commit `722f7bd1` only by changes that reached the main branch through the ordinary pull-request gate.
>    (f) Every run is recorded verbatim in the prepare record, refused runs included: the command, the commit it ran at, the exit code, the full output and the time. No run is left out.
>
> 3. **If a candidate is written.** Issuance proceeds to the cold science gate and the issuing transaction. This holds whether or not the candidate carries either mark the registration defines: `excursion_limited` (two or more retained B above 0.075 s) or `zero_headroom` (the ceiling C equals the screen S). Each mark is recorded and travels with the calibration, with the consequence the registration states for it. No mark, no diagnostic and no value is a ground to withhold issuance, to exclude a capture, to capture again under Revision 5, or to write a successor registration for this epoch. This sentence does not limit what the registration itself prescribes for a mark, nor the re-derivation triggers the issued calibration carries.
>
> 4. **Terminal refusal.** A refusal is terminal when its cause is any of these:
>    (i) a member's B is above 0.25 s (`PLATEAU_INSET_S`);
>    (ii) fewer than 12 captures are retained;
>    (iii) a valid capture's stored clock alignment did not resolve for a reason other than `affine_clock_fit_empty`, or was recorded under a method other than anchor-v3;
>    (iv) a member's stored B text differs from its ledger row's;
>    (v) the registration is void (the rows' OS build or sampler digest differs from the registered one), or the rows disagree on the epoch;
>    (vi) a battery record and its recomputation still disagree after the exact restore of item 5(b).
>    On a terminal refusal, all of the following hold:
>    (a) Derivation under Revision 5 ends for this epoch. There is no further capture under it: no third window, no battery replacement window, no retry and no top-up.
>    (b) Nothing issues from W1 and W2. No capture is dropped, no threshold is moved and no flag is used to make them issue.
>    (c) All 24 captures of W1 and W2 become disclosed diagnostics. None is ever a member of a later registration's corpus, alone or alongside new captures. Their ledger rows and custody bytes are kept unmodified. Their B values may be read after the refusal, to find the cause, and each such read is recorded.
>    (d) The setting-aside is recorded in a new decision-log entry. The entry names its own reason: "member of registration Revision 5, which ended in a terminal refusal; disposed as diagnostic, never a member". It says whether it was written before or after any W1 or W2 value was read. The 12 valid captures' content ids are added to the disposition registry through the ordinary pull-request gate before any successor's issuance step runs. The same reviewed change makes the issuing tool refuse any registration that names a session owning a capture set aside in the registry. Until that change lands, rule (c) is enforced by this statement and by review, not by code: the tool's existing check for outside captures skips every session a run names.
>
> 5. **Curable refusal.** A refusal is curable only when its cause is on this list, and only by the cure named:
>    (a) a wrong or missing argument, sessions named out of order, a wrong interpreter, or a wrong checkout or file path typed on the command line. Cure: correct the command to the one in item 2 and run again. A path recorded in a ledger row is not a command path, and a refusal about one is never curable under (a);
>    (b) a custody file that is missing, unreadable or does not match the digest its ledger row recorded at capture. Cure: restore the bytes exactly from the harvest archive, to the place the ledger row records, so that they hash to the recorded digest, and run again;
>    (c) a committed input that is not the registered one: the ledger head pin, the predecessor calibration file, a battery record or the disposition registry. Cure: run from a checkout that holds the committed file. No file is edited.
>    A cure never changes the ledger, the registration, a capture's evidence, the issuing tool, or the four estimator-code files (`joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`). A cure never includes a capture.
>
> 6. **Held refusal.**
>    (a) **What is held.** Any refusal on neither list; any crash; any refusal that could be removed only by changing code; the two named cases in (d) and (e).
>    (b) **What holding means.** Work stops: no re-run, no capture and no issuance. The output is kept verbatim. A held refusal stays held until it is ruled. Silence never makes it terminal and never makes it curable.
>    (c) **Who rules, and on what.** The owner, or a fresh cold gate shown the refusal text and the proposed change and no B value, rules whether the change is a tool repair. A tool repair changes none of the registered rules (membership, the floor of 12, the 0.075 s and 0.25 s limits, the formulas for S and C, the quantile bounds), leaves the four estimator-code files byte-identical, and lands through the ordinary pull-request gate. If the ruling is that the change is not a tool repair, the refusal is terminal and item 4 applies. If the held output showed any B value or statistic, the ruling is recorded as made after values were seen.
>    (d) **The custody fault, known before the first run.** Verified on 2026-09-27 by running the issuing tool's own path function on path strings, with no B value read: every W1 and W2 ledger row records its custody directory as an absolute path inside the custody tree, and the custody tree lies inside no git checkout. The issuing tool can record a member's custody directory only as a path relative to the checkout it runs from. It therefore refuses: `REFUSED: member <id>: custody <path> lies outside the repository, so no repo-relative source_directory exists`. With the tool at sha256 `ceaf3807b2fde7d50374c4781e1c0eff3fb8fea38344b37950cf67fa8e757105`, no candidate can be written from W1 and W2, and this is the refusal printed unless an earlier cause refuses first. The tool reaches it after reading the first valid capture's files and checking that its stored B text equals the ledger row's, and before any B is compared with a limit and before any statistic. The message carries a path and a capture id and no value.
>    This refusal is held. It is not curable under item 5. None of the following is ever a cure: moving, copying, re-rooting or symlinking the custody tree or any custody directory; creating a git repository at or above `/Users/edr/night-custody`; rewriting the path a ledger row records; giving the tool a root directory other than the run checkout.
>    The repair is designed, ruled and merged before the issuance step runs. Its design is ruled by the council under decision D-184, and its final change is ruled a tool repair under (c) by a fresh cold gate that neither designed nor wrote it. The operator cannot rule on it alone. The owner receives a summary by email and may overrule. The repair satisfies all of these:
>    R1. **Blind.** It is designed, reviewed, tested and merged by people and models that have read no B value of W1 or W2 and have not run the issuance step on them. Its tests use made-up captures or already issued calibrations. Path strings and file digests of W1 and W2 may be used.
>    R2. **No rule moves.** It meets the definition of a tool repair in (c). The four estimator-code files' sha256 digests are recorded before and after and are equal.
>    R3. **Evidence stays put.** The custody tree, every file in it and every ledger row are byte-identical before and after.
>    R4. **Members stay verifiable.** A reader who holds the issued calibration file and the custody tree can check every member: the reader names the directory the members' paths are relative to, the check joins each member's recorded path to it, confirms the result lies inside that directory, and compares the manifest and evidence files there with the two digests the member's entry carries. The issued file stores no absolute path. The repair says which command performs this check, and shows it passing on a made-up calibration whose captures lie outside the checkout, and failing when one byte of a capture file is changed.
>    R5. **Still refuses.** The repaired tool refuses a custody directory that lies outside every directory it was told to accept, and refuses a recorded path that leaves its directory through `..` or a symlink. A test shows each.
>    R6. **History unchanged.** The issued calibration files r2 to r7 are byte-identical, and checking them gives the same result as before the repair.
>    R7. **Smallest change.** It is the smallest change that removes the refusal, and its diff is reported in the pull request. One test fails on the unrepaired tool and passes on the repaired one.
>    R8. **Proven on the real paths.** Before the issuance step runs, the repaired path function is run on the recorded paths of the 12 valid captures, as path strings only, and returns a relative path for each. The output is recorded.
>    R9. **Disclosed.** The prepare record, and any text that reports the resulting calibration's provenance, says that the issuing tool was repaired after capture and before any B value was read, and cites the pull request and both rulings.
>    If the issuance step was run before the repair and ended in exactly this refusal, the run is recorded under item 2(f) and nothing else follows from it.
>    (e) **A capture outside W1 and W2.** If the tool refuses `valid same-epoch observations outside this registration: …`, the refusal is held. The only ruling open is to set the named capture aside in the disposition registry as a diagnostic that is never a member, by a new decision-log entry and a reviewed change. The owner makes that ruling, or the council with a cold-gate ruling on its final text. The capture is never absorbed into the corpus, and no W1 or W2 capture is affected.
>
> 7. **Candidate written, then rejected.** When the candidate is written, its sha256 is recorded at once. If the cold science gate or the issuing transaction rejects it:
>    (a) for a reason whose fix leaves the member list, the statistics and the three operative numbers (S, C and the level screen) unchanged, such as an incomplete packet or a wrong identifier, the fix is made and the candidate is resubmitted. A re-prepared candidate must match the first in those fields character for character;
>    (b) for any reason whose fix would change one of those fields, or for a defect found in the code that derives them, item 4's consequences (a) to (d) apply. Two reasons make this stricter than item 6. Once a candidate exists its values are known, so a repair can no longer be ruled blind. And the owner's directive #416, clause 3, already answers a defect in the derivation path with recapture. Where (a) and (b) both seem to apply, (b) governs unless the owner rules otherwise in writing.
>
> 8. **Successor registration.** Any further calibration capture for this epoch happens only under a successor registration. A successor is authorized by the owner's written ruling, or by the council under decision D-184's addendum with a cold-gate ruling on its final text, as Revision 5 was. The operator cannot authorize one alone. The successor's text is sealed, and its digest is pinned in the arm material, before its first capture. The text states that it was written after Revision 5 ended, names the refusal reason, and lists as disclosed design inputs every W1 and W2 value its authors had seen. The owner receives a summary by email before its first arm notice.
>
> 9. **Directive #416, clause 3.** "W1/W2 are re-run" is read as: captured again under a successor registration, per item 8. No window is added to Revision 5 for an audit finding. The custody fault of item 6(d) is not a finding under clause 3: it was found before issuance, it blocks issuance and cannot pass silently, and its repair changes no capture and no number.
>
> 10. **Override.** The owner may overrule any item in writing. A ruling given before the issuance step first ends in a result that depends on a measured value is outcome-blind and simply replaces the item. The results that do not depend on a measured value are the refusals of items 5, 6(d) and 6(e), and no others. A ruling given after that point is recorded as made after the outcome was known, and any text that reports the resulting calibration says so.

## 6. Ruling 4: the custody fault's repair

### 6.1 Who rules

| Question | Who | Why |
|---|---|---|
| The repair's **design** (what the issued file records for each member, and how a reader finds the files) | The council, under decision D-184 | D-184's binding reading names "merge of claim-bearing code" among the major changes that convene all four model families "when usage allows". The issuing tool produces the calibration every later measurement is accepted against, and the design outlasts this epoch: every future calibration captured outside a checkout will use it. A seat is dropped only for a usage limit, and the record says which. |
| Whether the **final change** is a tool repair (item 6(c)) | A fresh cold gate, shown the diff, the test results, path strings and no B value | The statement already requires this ruling. A seat that designed or wrote the repair does not judge it. One cold-gate ruling on the final diff serves as both the council's closing ruling and item 6(c)'s ruling; two are not needed. |
| The owner | Not required. Receives a summary by email; may overrule | The D-184 addendum keeps for the owner "Only hardware, sudo, a notice NO, and publishing claims". The repair is none of these. |
| The operator alone | Cannot rule | The operator runs the step the repair unblocks. |
| This judge | Sets constraints only | I did not design the repair (NOT EXECUTED), so that the judge of the statement is not the author of the change it governs. |

**One thing does need the owner.** Any design that needs the custody tree moved, copied or put under a new repository, or a ledger row rewritten. The statement forbids these outright. Only the owner's written override under item 10 could allow one, and I advise against it: the evidence's location is part of its record.

### 6.2 The minimum constraints

They are R1 to R9 in item 6(d) of the statement, and they bind as part of it. The reason for each:

| Constraint | Forcing problem |
|---|---|
| R1 blind | A repair shaped by someone who has seen values can lean on them. Today nobody has; the repair must be finished while that is still true. |
| R2 no rule moves | The repair is about where files are, not about which captures count or what the limits are. |
| R3 evidence stays put | The ledger row's digests and path were fixed at capture. Changing either changes the record the calibration rests on. |
| R4 members stay verifiable | This is the purpose of the check that now refuses. Deleting the check would remove the refusal and the protection together. |
| R5 still refuses | Without it, the repaired tool would accept a directory anywhere on the disk. |
| R6 history unchanged | Six issued calibrations (r2 to r7) rely on the present behaviour. |
| R7 smallest change | The registration's own precedent for a blocking refusal in code: "the smallest change that removes it goes through the ordinary pull-request gate with its diff reported" (Revision 2, "On PASS", consequence 4). That sentence governs a different refusal; I use it as precedent, not as binding text. |
| R8 proven on the real paths | The count-only dry run does not exercise member custody (its own documentation lists it as "not mirrored"), which is how this fault reached today unseen. The check I ran in A7 takes seconds and reads no value. |
| R9 disclosed | A reader of the calibration should know the tool changed between capture and issuance, and that it changed blind. |

**A practical note for the operator (not a constraint).** The W2 harvest commit `722f7bd1` is not yet on the main branch (A4). The run checkout needs both that commit's records and the repaired tool. Item 2(d) and 2(e) are written so that this is checked by digest whichever way the two are brought together.

## 7. Findings

### BLOCKER
- **B1. The issuance step must not be run until the custody fault is repaired under item 6(d).** Running it sooner cannot produce a candidate. It is not harmful to the science (the refusal shows no value), but it spends a recorded run for nothing.

### SHOULD-FIX (conditions of this addendum)
- **S1.** Record the §5 block verbatim, commit it, and send its sha256 to the owner by email, before the issuance step runs. If the earlier ten-item text was already recorded or sent, say that this text replaces it.
- **S2.** Tell the owner in plain words what changed: the tool needs a repair before any calibration file can be written; the repair is ruled blind; two causes moved from "ends the epoch" or "unclassified" to "held"; silence no longer ends the epoch. The earlier summary line "Nothing needs you today" remains true, but the owner should know a code change now precedes the step.
- **S3.** If the issuance step has already been run in this activation, record that run under item 2(f) now, with its full output.
- **S4.** Check the owner's replies immediately before the issuance step runs. A reply that overrules any item governs.
- **S5.** Re-run the count-only dry run immediately before the issuance step and record it, so that "12 valid, none excluded, no outside capture" is confirmed at the run's own commit.

### NIT
- **N1.** The refuter's phrase "before any B value is compared" is inexact (§3.2). The statement uses the exact wording.
- **N2.** The earlier ruling's two sentences corrected by SF-3 and N-d (§4) should carry a pointer to this addendum where that ruling is cited.
- **N3.** The count-only dry run should gain a value-blind check of member custody paths, so that the next fault of this kind is found at harvest. This is a suggestion for the repair's authors and is not required by R1 to R9.
- **N4.** I did not determine the project interpreter's path (NOT EXECUTED). Item 2(a) requires it to be recorded.

## 8. Plain summary for the owner

1. The checking tool that writes the calibration file cannot do so today: the two windows' capture files are stored outside the code repository, and the tool only knows how to record locations inside it. I confirmed this without reading any measured value, and it means a small code repair must come before the issuance step.
2. That repair will be designed by the four-model council and approved by a fresh reviewer who sees no measured values; the capture files are never moved, no rule or threshold changes, and every sample member must stay checkable afterwards. You do not need to act, and you can overrule.
3. The final statement in §5 replaces the earlier one: all seven of the second reviewer's points are adopted, a stalled software fault can no longer end the epoch by silence, and your right to change any rule stays outcome-blind until the step first produces a result that depends on a measured value.
