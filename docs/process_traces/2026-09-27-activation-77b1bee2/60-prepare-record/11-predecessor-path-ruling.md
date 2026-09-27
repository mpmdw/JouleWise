RULING: (b)

# Cold gate PREDECESSOR-PATH-01: ruling on how the prepare step names the predecessor calibration file

Judge: Fable 5.1, fresh session, 2026-09-27, ending 16:17 PDT. Tree read: `/Users/edr/code/JouleWise-wt-corpus-fp-77b1bee2`, detached at `f783a3fd348df984e3278e25842dc396059443a4`, issuing tool sha256 `21b2eea8c64e5fe1ca41474927e2b15471ceb11f2bd7e5f31b89445d3f53060c`.

The ruling is option (b), as **an amendment to item 2(c) of statement REV5-REFUSAL-BRANCH-01**, not as a reading of it. It carries six conditions (§6). The owner's written reply, if it arrives before the prepare step runs, replaces this ruling.

## 0. Contamination disclosure

1. **What the harness loaded without my asking.** Before my first action the session had placed three texts in my context: the owner's global instruction file, the worktree's `CLAUDE.md` (bridge and delegation rules), and a one-line-per-entry index of the owner's memory notes. The index includes the line "W2 admitted (#434 b69c39eb); issuance blocked on custody repair (design C)" and a line saying the owner dislikes work being queued on him when an agent could do it. None of the three holds a measured value. I opened no memory file, no skill file, and neither `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md` nor any `CLAUDE*.md`.
2. **What I did not lean on.** The authority question in §4 is decided from the statement and its two ratifying rulings alone. The index line about queuing work on the owner is not used as a ground.
3. **What I read.** The charge (`10-predecessor-path-charge.md`); the statement in full; ruling `71-coldgate-final-diff-ruling.md` in full; §4.6 of `40-refusal-branch/21-coldgate-fable-ruling.md` and the amendment table (§4) of `40-refusal-branch/30-addendum/21-addendum-ruling.md`; the issuing tool's predecessor code; the loader in `joulewise/calibration_bracketing.py`; `joulewise/authentication_io.py` `:547–556`; the first 182 lines of `tests/test_issuer_corpus_root.py`.
4. **Measured values.** I opened no ledger, no capture file and no file under the custody tree. In the run checkout I did three things only: asked git for its commit and status, hashed two files (the issuing tool and the r7 calibration file), and listed the r7 file's directory entry. The r7 and r6 calibration files are issued calibrations of an earlier epoch; from each I printed three strings of the predecessor note (an id, a path, a digest) and no number.
5. **Owner's mail.** I did not open the owner's mailbox. Whether a reply has arrived is the operator's check (condition C5).
6. **Files changed.** None in any repository. `git status --porcelain` printed nothing for the candidate tree, the record tree and the run checkout after my last command. Scratch is under `/tmp/cg-pred-77b1bee2/` (`probe.py` sha256 `47c1cbfa…fd48`, `probe.log` sha256 `829e58df…13cb`).

## 1. Words used

- **The statement:** REV5-REFUSAL-BRANCH-01, file sha256 `8717e33c27f069e3889d8f3d6095d76adbdd6ad9b012482e0cad3a936bb339a6` (hashed this session; it matches the charge).
- **The issuing tool:** `scripts/issue_calibration_acceptance_generation.py`. **The prepare step:** its command `prepare-candidate`, which writes one candidate calibration file or prints `REFUSED: <reason>` and writes nothing.
- **Predecessor:** the previously issued calibration file whose two numbers the new calibration inherits: its ceiling (the largest timing drift it allows) and its level screen. For this epoch the predecessor is **r7**, the file `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`.
- **Registry pin:** a table written in code (`ISSUED_ACCEPTANCE_REGISTRY`) that lists, for each issued calibration's id, the sha256 its file must have. For r7 the pin is `9c3a29f61a6f72bbe5efdfb0eddd1caa14557595522b2abb093b414380b9fe16`.
- **Authenticate:** read a file's bytes, hash them, and accept the file only if the hash equals the registry pin listed under the id the file itself states.
- **Absolute path:** a path that begins with `/` and so names a place on one machine. **Relative path:** a path that does not, and is joined to a directory the reader chooses.
- **Run checkout:** the git working directory the prepare step runs from, `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2`.
- **The note:** the entry `derivation_notes.predecessor` in the candidate file. It records the predecessor's id, a path string under the key `relative_path`, and the predecessor file's sha256.
- **Value-blind:** decided from path strings, ids, digests and code, with no measured value read.
- **B:** a capture's stored timing bound in seconds.

## 2. Rule-on 1: the finding is verified

### 2.1 Where the default is set and how it is stored (read from code)

| Step | Place | What it does |
|---|---|---|
| 1 | `joulewise/calibration_bracketing.py:58–60` | `_CALIBRATION_CONFIG_DIR` is built from the module's own location on disk, so it is absolute. |
| 2 | `:137–139`, `:199` | `DEFAULT_ACCEPTANCE_BOUND_PATH` is that directory joined to the r7 file name. |
| 3 | issuing tool `:2552–2555` | `--predecessor-acceptance` takes that value as its default. |
| 4 | issuing tool `:1768` | The file at the argument's path is authenticated (§2.2). |
| 5 | issuing tool `:2184` | The note stores `str(Path(args.predecessor_acceptance))`: the argument's own spelling, not a path computed from the file. |
| 6 | issuing tool `:2187–2189` | The note also stores the sha256 of the file's bytes. |

So with the flag omitted, the key named `relative_path` holds an absolute path. Ruling 71's finding S1 is correct. No code checks that string: the only part of the notes the production validator reads is `excluded_members` (`calibration_bracketing.py:991–992`).

### 2.2 How the predecessor is authenticated (read from code)

```
path given on the command line  ──►  bytes read from disk          (calibration_bracketing.py:1133)
                                       │
                                       ├─ parse; take the id the FILE states      (:1171–1175)
                                       ├─ look that id up in the registry pin     (:1175–1176)
                                       ├─ sha256(bytes) must equal the pin        (:1179)   else refuse
                                       └─ Revision 5: the id must be r7's         (issuing tool :1797–1801) else refuse
```

Every element: the **path** decides only where bytes are read from. The **id** comes from the file, never from the path. The **pin** comes from code. The **r7 requirement** comes from code and applies because the registration's epoch is the Revision 5 epoch.

Consequence: whatever path is given, the step continues only if the bytes hash to `9c3a29f6…fe16` and state r7's id. The path cannot choose different content. It can only choose which copy of those bytes is read, and what string the note stores.

### 2.3 Executed evidence (`/opt/homebrew/bin/python3`, Python 3.14.7; log `/tmp/cg-pred-77b1bee2/probe.log`)

The candidate tree stood in for the run checkout: the probe ran with it as the working directory. Captures were made up by the repair's own fixture builder (24 captures, two sessions, Revision 5 path).

| # | Check | Result |
|---|---|---|
| E1 | Default value parsed with the flag omitted | `'/Users/edr/code/JouleWise-wt-corpus-fp-77b1bee2/configs/calibration/calibration_acceptance_d079_v2_n17_r7.json'`; absolute. |
| E2 | Value parsed with `--predecessor-acceptance configs/calibration/calibration_acceptance_d079_v2_n17_r7.json` | `'configs/calibration/calibration_acceptance_d079_v2_n17_r7.json'`; relative. |
| E3 | sha256 of the bytes reached each way | Both `9c3a29f6…fe16`, equal to the registry pin. Both paths reach one file (same inode); it is a regular file, not a symlink. |
| E4 | `_authenticated_predecessor` on each path | The two returned documents are equal; id `d079_calibration_acceptance_v2_n17_r7`. |
| E5 | The same r7 file in the **run checkout** (at commit `722f7bd1`, working tree clean) | sha256 `9c3a29f6…fe16`; regular file; git blob `7dcd186e…`, the same blob as in the candidate tree. |
| E6 | Synthetic run A, flag omitted | exit 0. Note stores the absolute string of E1. |
| E7 | Synthetic run B, flag given as in E2 | exit 0. Note stores `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`; `file_sha256` `9c3a29f6…fe16`. |
| E8 | Every key that differs between files A and B | Two: `derivation_notes.predecessor.relative_path`, and `derivation_sha256` (the digest of the whole file, which closes over the note). |
| E9 | Fields equal between A and B | `derivation_input_sha256` (the digest of the arithmetic's inputs), `decimal_derivation`, `derivation_corpus`, `registered_generation_row`, `prior_observation_set`, `ledger_cutoff`, `identity_epoch`, `acceptance_id`. |
| E10 | Strings beginning with `/` in file B | One, and it is an artefact of my probe: the registration's path, which I gave as an absolute scratch path. The statement's command gives it as a relative path, and the tool stores the spelling given (`:2222`). The ledger, head pin, checkout root, custody parent and output file were all given as absolute paths and none was stored. |
| E11 | Negative C: a copy of r7 with one space added (same values, valid JSON), named by path | `REFUSED: predecessor: … is not an authenticated issued acceptance`; exit 3; no file written. |
| E12 | Negative D: r6 named by its repository path | `REFUSED: registration Revision 5 requires r7 predecessor d079_calibration_acceptance_v2_n17_r7`; exit 3; no file written. |
| E13 | Negative E: a path that does not exist | `REFUSED: predecessor: configs/calibration/no_such_file.json is not an authenticated issued acceptance`; exit 3; no file written. |
| E14 | Other spellings of the same file | `./configs/…` is stored without the `./`. A spelling with `..` in it is accepted and stored **verbatim**, `..` included. The spelling therefore has to be fixed exactly (§5). |
| E15 | How r6 and r7 themselves stored this note | r7: `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`. r6: `configs/calibration/calibration_acceptance_d079_v2_n17_r5.json`. Both repository-relative: the form option (b) produces. |

### 2.4 Answers

| Question | Answer |
|---|---|
| Where is the default set? | `joulewise/calibration_bracketing.py:199`, built absolute at `:58–60`; taken as the argument default at issuing tool `:2553`. |
| How is it stored? | Verbatim, as the argument's spelling, at `:2184`. |
| Does the relative argument name byte-identical content? | Yes (E3, E5). It could not do otherwise and still pass (§2.2, E11, E12). |
| Is it authenticated the same way, against the registry pin? | Yes. The same function, the same pin, the same r7 requirement (E4). |
| Is `relative_path` then relative? | Yes (E7). |

**One real difference, stated plainly.** The default is resolved against the place the tool's code lives. A relative argument is resolved against the directory the command is run from. Item 2(a) already fixes that directory as the run checkout, so both name the same file. If the command were run from elsewhere, the step would refuse (E13) or would read another copy that must still hash to the pin. No wrong content can enter.

**NOT EXECUTED.**
- The prepare step on W1 and W2.
- Anything in the run checkout beyond E5. It still holds the unrepaired tool, so E5 must be repeated after it is advanced (condition C3).
- Whether the issuing transaction (the reviewed commit that turns a candidate into an issued file) rewrites the note. Ruling 71 left this open and so do I; option (b) makes the answer immaterial, because the string is already relative.
- The test suites. This ruling changes no code.

## 3. Rule-on 2, first half: is option (b) an escape flag?

**What the word meant.** The first ratifying ruling (§4.6) used "escape flags" for three arguments: `--nights-ruling`, `--slot-count-ruling` and `--ed-ruling`. Each lets a run depart from a registered rule by naming a written ruling. `--predecessor-acceptance` was not among them.

**Why `--predecessor-acceptance` is on the list in item 2(c).** The cold addendum added it, with six others, under its amendment SF-2, "fix the run's inputs". Its stated reason: leaving an input open "leaves a choice to be made after the outcome".

**Test of option (b) against each purpose.**

| Purpose | Does option (b) defeat it? | Basis |
|---|---|---|
| No registered rule is departed from | No. | The predecessor is r7 either way; the ceiling and level screen inherited are the same strings (E9). |
| No input is left to be chosen after the outcome | No. | The input is fixed by code to r7's exact bytes (§2.2). The argument's spelling is fixed by this ruling, before any B is read (§5). |
| The operator has no freedom | No, provided the spelling is exactly the one in §5. | E14 shows other spellings would be stored verbatim, so the spelling is not left open. |

**Finding.** In function, option (b) is not an escape: it chooses how an unchanged input is named in a note, and nothing else. **In letter, it is forbidden:** item 2(c) says "the step is not given … `--predecessor-acceptance`", and says the custody argument "is the only addition". Giving the flag is a departure from the text. I rule it as an amendment and do not present it as a reading.

## 4. Rule-on 2, second half: who can permit it?

**The statement contains a conflict that its authors did not see.** Item 2(c) forbids the flag. Item 6(d) R4 says "The issued file stores no absolute path." With the tool as it is, obeying 2(c) puts an absolute path in the file. Both sentences entered the text in the same cold addendum. One of three things must give:

| Option | What gives | Cost |
|---|---|---|
| (a) | R4's sentence is read as covering member paths only. | The file carries `/Users/edr/night-custody/measurement/…` in a note. The sentence in R4 is unqualified, so this too changes the statement's meaning. If the path is later judged a defect, the fix comes after a candidate exists, when values are known. |
| (b) | Item 2(c)'s list loses one entry, for one fixed spelling. | A departure from the letter of the fixed command. No number, member or rule changes (E8, E9). |
| (c) | Neither sentence; the tool is changed again. | New code in the issuing tool, a new council design ruling and a new final-diff cold gate, for a string no code reads. Item 6(c) defines a tool repair as the answer to a held refusal, and this is not a refusal, so (c) stretches the statement as well. |

**Can a cold gate permit (b)? Yes, within limits, and I state the limits.**

1. *The text's own authority.* The statement was "ratified by cold gate ruling" and "amended by cold addendum". The ban on this flag was written by a cold gate. A fresh cold gate, value-blind, resolving a conflict between two sentences of that text is the same kind of act as the addendum, which corrected the first ruling's sentences.
2. *Timing is what protects the science.* Item 10 treats a ruling as outcome-blind when it is given "before the issuance step first ends in a result that depends on a measured value". That has not happened: the step has not run, and I read no value.
3. *What a cold gate cannot do.* Item 10 gives the power to **overrule** an item to the owner alone. I therefore do not overrule item 2(c) in general. I amend one entry of its list for one exact argument text whose effect I have shown to be nil on every number. I could not permit any other listed flag on this reasoning, and I could not permit this flag with any other value.
4. *The owner's place.* The owner was asked and may overrule. This ruling does not make his silence into consent; it stands on points 1 to 3. His written reply in either direction replaces it (condition C5).

**Where I am uncertain.** The statement gives no procedure for amending itself. Point 1 is my reading of how the text came to exist, not a clause of the text. A reader who holds that only the owner may touch item 2 would require option (a) or the owner's reply. I judge that reading too strict, because it would force a known defect into the file (a) or a post-outcome fix, both worse for the record than a disclosed, value-blind amendment. The operator should put this paragraph in front of the owner (condition C4).

## 5. Rule-on 3: the choice and the exact text

**Option (b).**

**The argument, exactly:**

`--predecessor-acceptance configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`

No leading `./`, no `..`, no absolute form, no trailing space.

**The full command for the prepare record** is item 2(a)'s command, then the custody argument fixed by ruling 71 §6.4, then this argument:

`scripts/issue_calibration_acceptance_generation.py prepare-candidate --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md --preregistration-sha256 81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1 --registration-session-id d079-epoch-25g83-derivation-w1-20260927 --registration-session-id d079-epoch-25g83-derivation-w2-20260927 --d125-ruling "docs/decision_log.md, D-125 addendum (2026-09-25): Revision 5 screen and ceiling for epoch 25G83/v3 (ACCEPTANCE-25G83-02 §5 R5(i), R9)" --out <path> --corpus-root /Users/edr/night-custody --predecessor-acceptance configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`

`<path>` is as item 2(b) and ruling 71 §8 item 9 fix it. Every other flag listed in item 2(c) stays forbidden.

**Item 2(c), as amended by this ruling (text for the prepare record):**

> Amendment PREDECESSOR-PATH-01 (cold gate, 2026-09-27, before any B value of W1 or W2 was read and before the issuance step ran). In item 2(c), `--predecessor-acceptance` is given, with exactly the value `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`, and with no other value. Reason: the tool's default names the same file by an absolute path and stores that spelling in the candidate's note `derivation_notes.predecessor.relative_path`, which item 6(d) R4 forbids. The argument names the same bytes (sha256 `9c3a29f61a6f72bbe5efdfb0eddd1caa14557595522b2abb093b414380b9fe16`), authenticated against the same registry pin, and changes no member, statistic or operative number. The statement's file is not edited; this amendment is recorded beside it. The owner may overrule it under item 10.

## 6. Conditions (all value-blind; all bind before or at the run)

- **C1. Exact text.** The argument is given character for character as in §5.
- **C2. Working directory.** The command is run from the run checkout, as item 2(a) requires. The output of `pwd` is recorded immediately before the run.
- **C3. The file is checked immediately before the run,** in the run checkout after it has been advanced to the merged repair: `shasum -a 256 configs/calibration/calibration_acceptance_d079_v2_n17_r7.json` prints `9c3a29f6…fe16`; the file is a regular file and not a symlink; `git status --porcelain -- configs/calibration/calibration_acceptance_d079_v2_n17_r7.json` prints nothing. A mismatch is a committed input that is not the registered one: item 5(c) applies, and no file is edited.
- **C4. The owner is told before the run,** in the thread where he was asked: the amended text of §5, this file's sha256, and the uncertainty paragraph of §4.
- **C5. The owner's reply is looked for immediately before the run.** A written reply replaces this ruling: if he chooses (a), the flag is omitted and the absolute note is disclosed; if he chooses (c), the step waits for the second repair.
- **C6. After a candidate is written:** its `derivation_notes.predecessor.relative_path` equals the string of §5 and its `file_sha256` equals the pin; the search of ruling 71 §8 item 11 for any string beginning with `/` finds none. The prepare record and any text that reports the calibration's provenance state that the fixed command was amended by one argument, before any value was read, and cite this ruling.

**If the step refuses because of this argument** (message beginning `REFUSED: predecessor:`), the cause is a mistyped path or a wrong working directory, or a changed file. The first two are curable under item 5(a); the third under item 5(c). None shows a value.

## 7. Findings outside the charge

- **N1. The key's name promises what the code does not enforce.** `relative_path` stores whatever spelling was given (E1, E14). A later, ordinary change could store the path relative to the checkout, or refuse an absolute one. It is not needed for this run and must not be bundled into the pending repair, which has its final-diff ruling.
- **N2. The same holds for the registration's note** (`derivation_notes.preregistration.relative_path`, issuing tool `:2222`). The statement's command gives that path in relative form, so the real run stores a relative string. C6's search covers it.

## 8. Plain summary

1. The check confirms the problem and the fix: left alone, the tool writes a machine-specific folder path into the new calibration file; naming the earlier calibration file by its short in-repository path makes the tool read exactly the same bytes, verified against the same fixed fingerprint, and store the short path instead.
2. Nothing else changes: in a made-up trial the two resulting files differed only in that path string and the whole-file fingerprint that covers it, and every attempt to slip in different content was refused.
3. Adding the argument departs from the letter of the fixed command, so it is recorded as a disclosed amendment made before any measurement was read; Ed's written reply, whichever way it goes, takes precedence.
