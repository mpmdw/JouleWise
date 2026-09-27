VERDICT: MERGE
ITEM 6(c): TOOL REPAIR

# Cold gate CUSTODY-REPAIR-FINAL-01: ruling on the final diff of the issuer custody repair

Judge: Fable 5.1, fresh session, 2026-09-27, 13:45 to 14:05 PDT. Candidate: commit `f783a3fd` against base `b69c39eb`.
This one ruling serves as the council's closing ruling on the repair and as the ruling that item 6(c) of statement REV5-REFUSAL-BRANCH-01 requires (addendum §6.1).

The verdict carries four conditions (§7, S1 to S4). None of them blocks the merge. All four bind before the issuance step runs.

## 0. Contamination disclosure

1. **What I did not write or design.** I took no part in designing, writing or reviewing this repair before this session.
2. **What the harness loaded without my asking.** Before my first action, the session had already placed three texts in my context: the owner's global instruction file, this worktree's `CLAUDE.md` (bridge and delegation rules), and a one-line-per-entry index of the owner's memory notes. The index includes the line "W2 admitted (#434 b69c39eb); issuance blocked on custody repair (design C)". None of the three holds a measured value. I opened none of the memory files, no skill file, and neither `RUN_STATE.md`, `TASK_QUEUE.md` nor `AGENTS.md`.
3. **What I read.** The statement; addendum §6 and §7; the council synthesis; Fable consult §3 to §5; the four lens and seat reports named in the charge; the fix brief; the delta brief; the two verify tails; the diff; and the code it touches.
4. **Measured values.** I opened no B value (B is a capture's stored timing bound in seconds, the field `b_fiducial_s`) of W1 or W2. I opened no `manifest.json` or `instrument_evidence.json` under `/Users/edr/night-custody`. The naming function I ran on the real paths calls `lstat` on those two files, which asks the filesystem whether each exists and is a regular file. It reads no byte of them.
5. **One step beyond the letter of the charge.** The charge named three ledger fields to project: `custody_locator`, `attempt_id`, `session_id`. I also projected each row's `disposition` string (the words `valid` or `ordinary-invalid`), to count the valid rows and to check for duplicate capture ids among them. I also projected each session's `plan_id`, which is an id. Neither is a B value or a statistic. The 12-and-12 split is printed in the statement itself. My probe printed which capture ids are valid; that list is in `/tmp/cg-custody-final-77b1bee2/r8_probe.log` and is not repeated here.
6. **Files changed.** None in any repository or custody directory. `git status` on the candidate worktree was empty after every run. Scratch is under `/tmp/cg-custody-final-77b1bee2/`.

## 1. Words used

- **The issuing tool:** `scripts/issue_calibration_acceptance_generation.py`. **The issuance step:** its command `prepare-candidate`, which writes one candidate calibration file or prints `REFUSED: <reason>` and writes nothing.
- **Capture:** one measurement attempt. Its files live in one directory, the **capture directory**.
- **Ledger:** the append-only file with one row per capture. Each row records the capture's id, the digests of its files, and the absolute path of its capture directory (the field `custody_locator`).
- **Member:** a capture that the issued calibration's statistics are computed from.
- **Primary files:** the two files in a capture directory whose sha256 digests a member entry stores: `manifest.json` and `instrument_evidence.json`.
- **Custody parent:** the directory that holds one directory per session. Here it is `/Users/edr/night-custody`.
- **Run checkout:** the git working directory the issuance step runs from, `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2`. It holds the ledger, the ledger head pin and the battery records.
- **Stored path:** the string a member entry keeps in `source_directory`. It must be relative, so that the file works on another machine.
- **Naming function:** the function that turns a ledger row's absolute path into the stored path. The old one is `_repo_relative_custody`; the new one is `_corpus_relative_custody`.
- **Canonical path:** a path spelled with no `.` or `..` part, no doubled or trailing `/`, and no symlink on the way, so that one directory has exactly one spelling.
- **Value-blind:** decided from path strings, ids and file existence only, with no measured value read.

## 2. What the repair does

**The fault.** The old naming function subtracts the run checkout's path from the capture directory's path. The W1 and W2 capture directories are not inside the run checkout, so the subtraction is impossible and the tool refuses every member. I reproduced this on the real path strings: the old function refused 24 of 24.

**The mechanism.** The new function subtracts the custody parent instead. Worked example, real strings:

```
ledger row records   /Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d04
custody parent       /Users/edr/night-custody                      (given as --corpus-root, never stored)
stored path          d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d04
                     └ part 1: session id ──────────────────┘ └ parts 2, 3: fixed ────┘ └ part 4: capture id ──────────────────────┘
```

The function accepts a stored path only if it has exactly these four parts: part 1 equals the row's session id, parts 2 and 3 are the literal names `runs` and `instrument_validation`, and part 4 equals the row's capture id. Because parts 1 and 4 come from the ledger row, only one custody parent can satisfy the rule. The operator confirms a fact the ledger already fixes; the operator does not choose it.

**What else the diff adds.**
- A pass over every valid row's path that runs before any member's files are opened, so a path fault refuses the whole run before any value is parsed.
- A read-only command, `verify-members --artifact <file> --corpus-root <dir>`, that joins each stored path to a directory the reader names and compares the two primary files' digests with the member entry.
- A fixed-text note, `derivation_notes.member_custody`, saying what the stored paths are relative to and naming that command.
- A test fixture option and 15 tests.

**What it does not touch.** `git diff --name-only b69c39eb f783a3fd` lists three files: the issuing tool, `tests/fixtures/epoch_bootstrap/build.py`, `tests/test_issuer_corpus_root.py`. Nothing under `configs/` or `joulewise/` changed, nor the verifier or the reissue tool.

## 3. Executed evidence (this session, `/opt/homebrew/bin/python3`, Python 3.14.7)

| # | Check | Result |
|---|---|---|
| E1 | `tests.test_issuer_corpus_root` | `Ran 15 tests in 18.771s`, `OK` |
| E2 | `tests.test_reissue_calibration_acceptance` + `tests.test_calibration_bracketing` | `Ran 99 tests in 0.644s`, `OK (skipped=1)` |
| E3 | `tests.test_issue_calibration_acceptance_generation` | `Ran 156 tests in 298.199s`, `OK`, exit 0. The live operating-system probe that failed in three sandboxed seats passes here. |
| E4 | Total | 15 + 99 + 156 = 270, which matches the lead's tail `63-fix1-lead-verify-tail.txt`. |
| E5 | The four estimator-code files, base against candidate | Equal digests: `powermetrics_fiducial.py` `386e8254…`, `uncertainty_evidence.py` `b583f35a…`, `adapters/powermetrics.py` `70f47086…`, `reduce.py` `7b9c0d28…`. They match the seat report's. |
| E6 | Base issuing tool digest | `ceaf3807…7105`, the digest the statement cites. Candidate: `21b2eea8c64e5fe1ca41474927e2b15471ceb11f2bd7e5f31b89445d3f53060c`. |
| E7 | Old naming function, base against candidate | Byte-identical. |
| E8 | The 15 new tests on the unrepaired tool (base tree plus the new test file and fixture builder) | `FAILED (errors=21)`: `--corpus-root` is an unrecognized argument and `_corpus_relative_custody` does not exist. |
| E9 | Three mutation cuts of my own, each on a scratch copy | Exact-four-part check removed: 3 failures, 1 error. Custody parent leaked into the ledger load: 10 failures. Digest comparison removed from `verify-members`: 1 failure. Every cut is caught. |
| E10 | Real paths (§4) | 24 of 24 accepted under `/Users/edr/night-custody`; every wrong directory refuses 24 of 24. |
| E11 | Adversarial probes of my own, synthetic captures only (§5) | 47 probes, 0 unexpected results. |
| E12 | Where the custody parent argument flows | `args.corpus_root` appears at two places in `_prepare_candidate`: the call into member selection (`:1894`) and the note's presence test (`:2164`). The ledger load, head pin, battery check and git lookups all keep `args.repo_root`. |
| E13 | Registration file digest in the candidate tree | `81b65f08…ddf1`, as the statement names it. |
| E14 | `git diff --check b69c39eb f783a3fd` | Clean. |

**NOT EXECUTED.**
- The issuance step on W1 and W2. It must not run before this ruling and the merge.
- `tests/verify_calibration_acceptance_corpus.py` against the historical capture archive.
- The repository-wide test discovery suite. I ran the four suites the charge names.
- The suites at the intermediate commit `c84b1dc2` (the 263-test tail). That commit is superseded by `f783a3fd`.
- Any check of the issuing transaction (the reviewed commit that turns a candidate into an issued file).
- Whether `/opt/homebrew/bin/python3` is the interpreter the harvest dry run used (statement item 2(a)).

## 4. R8: the repaired naming function on the real path strings

Source: the run checkout's `runs/calibration_observation_ledger.jsonl`. Script: `/tmp/cg-custody-final-77b1bee2/r8_probe.py`. Numbers were discarded at parse time (`parse_float` and `parse_int` return `None`).

| Directory given as the custody parent | Accepted | Refused | Reason printed |
|---|---|---|---|
| `/Users/edr/night-custody` (intended) | 24 | 0 | none |
| `/Users/edr` (one level too high) | 0 | 24 | "custody path must have exactly four parts" |
| `/` | 0 | 24 | same |
| the W1 session directory (one level too low) | 0 | 24 | 12 "exactly four parts", 12 "lies outside the declared corpus root" |
| the W2 session directory | 0 | 24 | same split |
| the run checkout | 0 | 24 | "lies outside the declared corpus root" |

- 24 rows, 24 distinct; 12 `valid`, 12 `ordinary-invalid`; 0 duplicate capture ids among the valid rows.
- All 24 stored paths have the four-part shape and none begins with `/`.
- Every part of every recorded path is spelled byte-for-byte as the directory is named on disk (24 of 24). This matters because the disk's filesystem ignores letter case (finding N1).
- Each session's `runs/instrument_validation` holds 12 entries and no symlink.

## 5. Adversarial probes

Script: `/tmp/cg-custody-final-77b1bee2/adversarial.py`; log beside it. Selected results:

| # | Input | Result |
|---|---|---|
| N2 | Middle parts spelled `Runs/Instrument_Validation` | Refused |
| N3c | Path in one Unicode spelling of `é`, capture id in the other | Refused |
| N4 | Path with a NUL byte; path with a trailing newline | Refused |
| N6b | Path spelled through a symlink to the custody parent | Refused |
| N8 | A primary file that is a named pipe | Refused, without hanging |
| N9 | Session id `plan-w1/runs`; session id `None`; empty capture id | Refused |
| N10 | A session directory that is a symlink to another session | Refused |
| N12 | One capture directory missing | The whole run refuses; no file is written; no member is dropped |
| V1–V3 | Member entry with a digest that is a list or an integer, or an id that is a dictionary | That member FAILS, exit 3, no crash |
| V5, V6 | Member 0 claims member 1's directory, digests and value, with and without a forged prior row | FAIL |
| V11 | The member's prior row duplicated | FAIL |
| V15, V16 | `verify-members` given a directory one level too low or too high | 20 of 20 FAIL |
| V18, V19 | A relocated copy with one byte flipped in one evidence file; then restored | 19 PASS and 1 FAIL; then 20 PASS |
| V22 | Digest of the whole synthetic custody tree before and after `prepare-candidate` plus `verify-members` | Equal |

Accepted inputs, each examined:
- A custody parent given as a relative path or through a symlink (N5, N6). The stored path is the same string, and the parent is never stored. Harmless.
- A path and ids that differ from the disk's spelling only by letter case or Unicode form, consistently (N1, N3b). See finding N1.
- A primary file that is a hard link to a file elsewhere (N7). The digest still binds the bytes. No action.
- An extra, unlisted file in a capture directory (V20). Already registered as lane CORPUS-RAW-REPLAY-01.

## 6. Rulings

### 6.1 Item 6(c): this is a tool repair

The statement's test has three parts.

1. **It changes none of the registered rules.** The diff touches no constant, formula or quantile. Membership is decided by the same loop as before. The new pass only adds refusals of the whole run, and it never drops or adds a capture. Test `test_same_ledger_flag_equivalence` runs one ledger with and without the new argument and finds the same member ids in the same order, the same `derivation_input_sha256` (the digest over the inputs of the arithmetic) and the same ledger cutoff. After removing the three intended differences (stored paths, the note, the whole-file digest), the two files are equal.
2. **The four estimator-code files are byte-identical** (E5).
3. **It lands through the ordinary pull-request gate.** This is a condition of the merge, not a fact yet.

The fault was in the tool: it could name a capture only relative to its own checkout. The repair changes where the tool looks for a name. It does not change which captures count or any limit.

**Recorded as made before values were seen.** The held refusal's text carries a path and a capture id and no value. I read no value.

### 6.2 R1 to R9 against the diff

| | Constraint | Finding | Basis |
|---|---|---|---|
| R1 | Blind | **Holds on the evidence available.** | The tests build made-up captures and use the issued r6 and r7 files and the registration's text. Every seat report I read states that no W1 or W2 value was opened, and I found none in those reports. I cannot prove what another session read. |
| R2 | No rule moves | **Holds.** | §6.1; E5. |
| R3 | Evidence stays put | **Holds for the diff.** | The diff has no write into a custody directory or the ledger. V22 shows a synthetic tree byte-identical across both commands. The real tree's before-and-after digests belong to the prepare step (§8, item 8). |
| R4 | Members stay verifiable | **Holds for members. One open point outside the diff (S1).** | The command is `verify-members`. It passes on a made-up calibration whose captures lie outside the checkout (E1, V19) and fails on one flipped byte (E1, V18, and the third cut of E9). Member paths are relative (N0b, N0d). |
| R5 | Still refuses | **Holds.** | Tests for outside-root, `..` and symlinks; my N6b, N10, V15, V16. |
| R6 | History unchanged | **Holds.** | No file under `configs/` changed. No file that reads r2 to r7 changed, so checking them cannot give a different result. E2 passes. The archive-side verifier run is NOT EXECUTED. |
| R7 | Smallest change | **Holds.** | The naming function and its argument remove the refusal. `verify-members` is what R4 demands. The note was ruled in by the council. The remaining lines are refusals the lenses asked for. E8 is the fail-before, pass-after test. The pull request must report the diff. |
| R8 | Proven on the real paths | **Holds today** (§4). | It must be run again at the merged commit and recorded (§8, item 7). |
| R9 | Disclosed | **Not a property of the diff.** | It binds the prepare record and any provenance text (S3). |

### 6.3 The lead's ruling on Sol's finding F1 (the exact four-part shape)

**The finding.** Fable consult §5.1 wrote the rule as "at least two parts; first equals the session id; last equals the capture id". The Sol lens built a capture at `P/s/s/runs/instrument_validation/s-d01`. Under that rule both `P` and `P/s` are accepted as the custody parent and give two different stored paths for one capture.

**Is the ruling within design C? Yes.** The design's stated purpose is that the rule "leaves exactly one custody parent that works", and its diagram names the middle as the "fixed middle part". The literal two-part rule did not deliver that purpose. The four-part rule does. It only adds refusals. My first cut in E9 confirms the test goes red when the check is removed.

**Could it refuse a legitimate future layout in a way that matters?** Three cases.

| Case | What happens | Does it matter? |
|---|---|---|
| A relocated archive that keeps `<session id>/runs/instrument_validation/<capture id>` under any directory `P` | `verify-members` passes (E1 relocation test, V17, V19). | No. |
| An archive laid out under another first name, or flattened | Every member FAILS until the reader renames the directories into the four-part shape. No byte needs to change. | It costs the reader time and never admits a wrong file. See S2: the lane's wording would cause exactly this. |
| A future capture harness that writes a different middle part | The issuance step refuses value-blind, before any evidence is opened. It would be a held refusal needing its own repair. | It costs time, not science. The loose alternative reopens the two-parent ambiguity. Accepted. |

### 6.4 The argument the issuance step is given

Statement item 2(c) says the added argument "is given as the repair's ruling fixes it, and is the only addition". I fix it as:

`--corpus-root /Users/edr/night-custody`

appended to the command of item 2(a). `--repo-root` stays omitted.

## 7. Findings

### BLOCKER
None.

### SHOULD-FIX (conditions; all bind before the issuance step runs)

- **S1. With the statement's command, the candidate will store one absolute path, in a note.** This is not in the diff; the line is unchanged from base.
  - *Mechanism.* Item 2(c) forbids `--predecessor-acceptance`, so the tool uses its default. The default is built from the tool's own location, so it is absolute. Line `:2184` stores `str(Path(args.predecessor_acceptance))` in `derivation_notes.predecessor.relative_path`.
  - *Executed.* Parsing the statement's arguments in the candidate tree gave `'/Users/edr/code/JouleWise-wt-corpus-fp-77b1bee2/configs/calibration/calibration_acceptance_d079_v2_n17_r7.json'`. From the run checkout it will begin `/Users/edr/night-custody/measurement/…`. In my synthetic candidate that key held the absolute string I had passed. The issued r6 and r7 hold relative strings there.
  - *Why it needs a ruling now.* R4 says "The issued file stores no absolute path." The sentence sits in the paragraph about members, and the note also stores the predecessor's sha256, so nothing is unverifiable. But once a candidate exists, item 7 governs and a repair can no longer be ruled blind. Today the matter is value-blind.
  - *Options.* (a) Record that R4's sentence is read as governing member paths, and disclose the absolute note. (b) The owner permits, under item 10, adding `--predecessor-acceptance configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`, which names the same bytes as the default. (c) A second tool repair.
  - *Recommendation.* (b). It changes no number, and the file ends with no absolute path.
  - *NOT EXECUTED.* Whether the issuing transaction rewrites this field.
- **S2. The archive lane names the wrong first part.** The synthesis's lane ISSUANCE-ARCHIVE-PACKET-01 says the archive keeps `<plan_id>/runs/instrument_validation/<id>`. The first stored part is the **session id**. For W1 and W2 the two differ: both sessions carry the one plan id `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3`. An archive laid out by plan id would fail `verify-members` on every member. Correct the lane to `<session id>/runs/instrument_validation/<capture id>` before any offload.
- **S3. The pull request and the prepare record carry the disclosures.** The pull request reports the diff (R7) and states three things: `verify-members` reimplements the member check instead of calling the reissue tool's; the new pass refuses the whole run on a bad path in any valid row, including a row the later replay would have excluded; and `verify-members` applies only to files that carry the `member_custody` note. The prepare record and any provenance text state that the tool was repaired after capture and before any B value was read, and cite the pull request, the council synthesis and this ruling (R9).
- **S4. The run checkout is not yet ready.** It sits at `722f7bd1` with the unrepaired tool, and its working tree is clean. After the merge it must be advanced to the main branch's commit that holds the repair. Then record its commit and the tool's sha256 (item 2(e)), and check the four digests of item 2(d) again. The ledger file is not under version control, so advancing the checkout must leave it untouched.

### NIT

- **N1.** The disk ignores letter case and Unicode form. The naming function accepts a path spelled differently from the directory's name when the row's ids are spelled the same way. The digests still bind the bytes, and all 24 real paths match the disk exactly (§4). Optional hardening: compare each part with the name the directory listing returns.
- **N2.** `verify-members` fails r2 to r7 by construction: their stored paths have three parts and their prior rows carry no session id. Its help text says "candidate or acceptance JSON file". Say which files it applies to.
- **N3.** Read from the code, NOT EXECUTED: if a member entry and its evidence file both lack `b_fiducial_s`, the comparison is `None` against `None` and passes. The validator's exact key set prevents such a member from being issued.
- **N4.** The new pass checks each path; the member reader then opens the files through the ledger's absolute path. Only the operator could change a directory between the two, and the digest check against the ledger row still runs on the bytes read. No action.

## 8. What the prepare step must still check

Every item is value-blind.

1. Finding S1 is ruled.
2. The repair is merged through the pull-request gate; the run checkout is advanced; commit and tool sha256 are recorded (S4).
3. The four digests of item 2(d) are checked and recorded immediately before the run.
4. The ledger head pin is committed in the run checkout. The tool asks git for it.
5. The interpreter's path and version are recorded, and it is the one the harvest dry run used.
6. The disposition registry's digest equals the one pinned in the tool at the run's commit.
7. The R8 probe is run again at the merged commit on the 12 valid captures, and its output is recorded.
8. A digest list of every file in the two custody directories is taken before the run and again after it, and the two are equal (R3).
9. `--out` names a new file outside `configs/` and outside `/Users/edr/night-custody` altogether, so the custody parent is never written to.
10. The count-only dry run is repeated and recorded (addendum S5), and the owner's replies are checked (addendum S4).
11. If a candidate is written: record its sha256 at once; run `verify-members --artifact <path> --corpus-root /Users/edr/night-custody` and expect 12 PASS lines and exit 0; search the file for any string beginning with `/`.

**Refusals the step could still print, all value-blind:** a wrong or missing argument (curable, item 5(a)); a custody file that is missing or changed since this probe (curable by exact restore, item 5(b)); a committed input that is not the registered one (curable, item 5(c)); a capture outside W1 and W2 (held, item 6(e)). I found no remaining path fault on the real strings.

## 9. Plain summary

1. The change is a repair of the tool and nothing else: it teaches the tool to name capture folders that sit outside the code repository, and it changes no rule, no limit and no capture. It may merge.
2. I re-ran all 270 tests, ran the repaired naming on the 24 real folder paths without reading any measured value (24 of 24 pass; every wrong folder is refused), and tried 47 hostile inputs; nothing broke.
3. Before the calibration step runs, four things need doing: decide how to handle one absolute path the statement's exact command would leave in a note (S1), correct the archive lane's folder naming (S2), carry the disclosures (S3), and update the run checkout to the repaired tool (S4).
