# Consult ISSUANCE-CUSTODY-OUTSIDE-REPO-01 — cold seat, Fable 5.1

Session: one non-interactive session, 2026-09-27, 12:35 to about 12:55 PDT. No subagent, no background task, no call to another model. Working tree `/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2` at `670756f3`, clean before and after.

## 0. Contamination disclosure

What reached me before or during the work, stated so a reader can judge how blind this seat was.

1. **Injected by the harness, not opened by me.** My context arrived already holding the project `CLAUDE.md`, a global `CLAUDE.md`, and the index page of a memory store (one-line titles of past checkpoints and owner directives). I did not open any of these with a tool, but I cannot un-see them. They hold process doctrine and the facts that W1 and W2 were armed and harvested. They hold no timing value and no statistic of W1 or W2.
2. **Other seats.** A directory listing showed me that a file named `13-opus-consult.md` (19 209 bytes) exists. I did not open it. No `12-*` file and no other `14-*` file existed at the listing. I did not open `01-scout-brief.txt` or `20-consult-charge.md`.
3. **Read in full:** the scout report `11-sol-scout-report.md` and the statement `00-refusal-branch-final-statement.md`. The scout report carries count-only harvest facts (6 valid captures per window, none excluded). The statement carries counts and limits, no measured value.
4. **Measured values of W1 and W2: none opened.** I did not run `prepare-candidate` or `check`. I opened no `manifest.json` and no `instrument_evidence.json` under the custody tree; my probes only asked whether each capture directory exists. From the ledger I extracted three fields by text pattern (`custody_locator`, `attempt_id`, `session_id`) and the names of keys containing "session", "attempt", "custody" or "locator". The ledger rows were never parsed as JSON and no other field was printed. The whole file passed through process memory, as any read of it must.
5. **Historical values seen in source code.** `tests/verify_calibration_acceptance_corpus.py:25-47` holds the stored statistics of the earlier corpora (the 19-member and 17-member generations). I read that file as source. Those are values of already issued calibrations from an earlier machine state, not of W1 or W2.
6. **Already issued calibration files r2 to r7** were loaded by my probes. The probes printed path strings, key names, file digests and true/false results only.
7. **Not read:** `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, any skill file, any memory file body.

## 1. Constraints I bound myself to

R1 to R9 of statement item 6(d). For this seat that meant: no B value read (R1); nothing written to any repository except this answer file; custody tree, ledger and r2 to r7 untouched (R3, R6), confirmed by digest at the end (§9, probe P6). Everything I did not run is marked NOT EXECUTED.

## 2. Words used

Each term is defined here, before its first use below.

- **Capture**: one measurement run. Its files live in one directory, the **capture directory**. Its name is the **capture id** (the ledger calls it `attempt_id`), for example `d079-epoch-25g83-derivation-w1-20260927-d01`.
- **Session**: one window of captures. Its name is the **session id**, for example `d079-epoch-25g83-derivation-w1-20260927`.
- **Night directory**: the directory that holds one session's captures. It is named by the session id.
- **Custody parent**: the directory that holds the night directories. On the capture machine it is `/Users/edr/night-custody`.
- **Run checkout**: the git working copy the issuance step runs from, `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2`.
- **Ledger**: the append-only file with one row per capture event. A row records the capture id, the session id, the sha256 digests of the capture's files, and the capture directory as an absolute path (`custody_locator`).
- **Member**: a capture that enters the calibration. The calibration file lists each member with five fields: its id, its stored timing value, the digests of its two primary files (`manifest.json` and `instrument_evidence.json`), and `source_directory`, a path string that says where those two files are.
- **Issuer**: `scripts/issue_calibration_acceptance_generation.py`. Its command `prepare-candidate` writes a calibration file marked "not issued", called the **candidate**.
- **Validator** and **loader**: the functions `_valid_acceptance_bound` and `load_calibration_acceptance_bound` in `joulewise/calibration_bracketing.py`. The validator checks a calibration file's structure and arithmetic. The loader accepts a file only when its whole bytes hash to a digest registered in code.
- **Verifier**: `tests/verify_calibration_acceptance_corpus.py`. **Reissue tool**: `scripts/reissue_calibration_acceptance.py`. Both re-open member files and compare digests.
- **Contained**: a path is contained in a directory when, after every symlink and every `..` in it is followed, the result still lies inside that directory.
- **Canonical path**: a path that is already its own fully followed form, with no symlink and no `..` in it.

## 3. Answer in short

**Design C**, which is design A with three things removed and two added.

Removed: the artifact-level `source_root` descriptor, every change to the validator and loader, and every change to the verifier and the reissue tool. None of them is needed to remove the refusal, and my probes show why (§4).

Added: a rule that ties each stored path to the capture's own session and capture id, so the custody parent is fixed by the ledger and is not a free choice; and one new read-only command, because no existing command can perform the member check that R4 demands on a made-up calibration.

The code change is confined to one file, the issuer, plus tests and the test fixture builder.

## 4. Question 1 — which design, and the consumer map

### 4.1 The mechanism, with the real strings

**Forcing problem.** The ledger row of a W1 capture records this capture directory:

```
/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d01
```

The issuer must store a path that works on another machine, so it must not store that absolute string. Today it can only subtract the run checkout's path, and this capture directory is not inside the run checkout, so it refuses.

**Mechanism.** Subtract the custody parent instead. With `--custody-root /Users/edr/night-custody` the stored string is:

```
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d01
```

Its first part is the session id. Its last part is the capture id. Both are already in the ledger row. The rule "first part equals the row's session id, last part equals the row's capture id" therefore leaves exactly one custody parent that works. The argument confirms a fact the ledger fixes. It does not choose one.

**Diagram.** Every element is named.

```
/Users/edr/night-custody/                      custody parent: named by --custody-root, never stored
├── d079-epoch-25g83-derivation-w1-20260927/   night directory = session id = FIRST stored part
│   └── runs/instrument_validation/            fixed middle part
│       └── d079-…-w1-20260927-d01/            capture directory = capture id = LAST stored part
│           ├── manifest.json                  primary file 1, digest stored in the member entry
│           └── instrument_evidence.json       primary file 2, digest stored in the member entry
├── d079-epoch-25g83-derivation-w2-20260927/   second night directory, same shape
├── d079-epoch-25g83-derivation-n1-20260919/   another session's night directory: never nameable
├── d079-epoch-25g83-derivation-n2-20260919/   another session's night directory: never nameable
└── measurement/JouleWise-measurement-…-w2/    run checkout (git): holds the ledger and the tools
```

**Reading it back.** A reader who has the two night directories under any directory `P` names `P`. The check joins `P` with each stored string, confirms the result is contained in `P`, and hashes the two primary files there. `P` may be the original custody parent, an external disk, or a restored archive.

### 4.2 Why not A as the scout wrote it

1. **A's descriptor is unenforced unless the validator changes, and the validator should not change.** Probe P3: the validator admits an added key at the top level and inside `derivation_corpus` without any code change. So the descriptor would be decoration the loader never checks. Making the loader check it means editing `joulewise/calibration_bracketing.py` in a repair whose rule is "smallest change" (R7), for no gain in removing the refusal.
2. **A's containment check alone is too weak for this custody parent.** Probe P1 found that the custody parent holds at least four night directories of the same machine state (two from 2026-09-19, two from 2026-09-27) and the run checkout. "Inside the custody parent" would accept a capture directory that sits in another session's night directory. The session rule in C closes that.
3. **A leaves the custody parent a free argument.** `/Users/edr`, `/Users` and `/` all contain the captures. Each would give a different stored string and different file bytes for the same science. Under C only one value is accepted (probe P4, "too high" and "too low" both refuse).

### 4.3 Why not B

Probe P3: a member entry with one added key makes the validator return false. The member key set is compared for exact equality at `joulewise/calibration_bracketing.py:876-883`. B therefore needs a validator change keyed by generation so that r2 to r7 keep passing. That is the largest change of the three and the only one that touches the code path the production loader runs. What B offers, a per-session binding, C gets from fields the file already has: the first part of the stored path is the session id, and each prior-set row of a live generation already carries `session_id` (`joulewise/calibration_bracketing.py:820-821`).

### 4.4 The scout's consumer map, checked

| Consumer | Scout's claim | My finding | Evidence |
|---|---|---|---|
| Issuer | Stores a path relative to its checkout; refusal at `:896`, call at `:1244`. | **Correct.** Added detail: the issuer reads member bytes through the ledger's absolute path (`:1041`, `:1508`), so reading is unaffected. The naming function is the only site where the refusal arises. | `scripts/issue_calibration_acceptance_generation.py:896-912, 1041, 1244-1247, 1508` |
| Verifier | Needs a change to "select that logical root from a caller-supplied archive location, while preserving repo-root resolution for r6/r7". | **Wrong premise.** The verifier already takes its root from the caller (`--repo-root`, required, no default) and joins it with the stored string. No r2 to r7 member directory exists in the checkout (probe P2: 0 present in every file), so history is already verified from an archive location, never from the repository. No mechanical change is needed. | `tests/verify_calibration_acceptance_corpus.py:73-89, 165-170` |
| Verifier, second point | Stored expectations cover ids through r7. | **Correct, and it has a consequence the scout missed.** The verifier refuses any calibration id it has no stored statistics for (`:76-78`), so it cannot run on a made-up calibration or on a candidate. It cannot be the command R4 asks for. | same file, `:25-66, 76-78` |
| Reissue tool | One root, `--corpus-root`. | **Correct.** Added detail: its command line accepts only a file the production loader authenticates (`:579-582`), so it also cannot run on a made-up calibration or a candidate. Its function `authenticate_derivation_corpus` can, and it already checks containment, directory name equals member id, both digests and the prior-set link. | `scripts/reissue_calibration_acceptance.py:127-238, 560-567, 579-582` |
| Validator and loader | "A path-contract change needs a validator change." | **Wrong for A and C, right for B.** The validator asks only that `source_directory` be a string (`:885`). It admits the new night-relative string, and also an absolute string and a `..` string (probe P3). A new registered digest is needed for any new calibration regardless of design. | `joulewise/calibration_bracketing.py:873-889, 1127-1138` |
| D-138 transaction (the single reviewed commit that turns a candidate into an issued file and registers its digest) | Installs the file and pins; the cold packet has no member-directory resolver. | **Not verified.** I did not read `docs/decision_log.md:10361` or the runbook's packet section. NOT EXECUTED. I confirmed only that the issuer's own text and tests describe the transaction this way (`issuer:2162-2180`, `tests/test_issue_calibration_acceptance_generation.py:1237-1274`). | — |
| Anything else | — | **None found.** A search for `source_directory` outside process traces finds the four consumers above, their tests, the issued files, and three unrelated local variables in `tests/test_arm_readiness_*.py`. | search recorded in §9, P7 |

## 5. Question 2 — the minimum change set

### 5.1 Sites

All in `scripts/issue_calibration_acceptance_generation.py` unless stated.

1. **New function beside `:896`.** `_repo_relative_custody` stays byte-identical. A new function takes the recorded path, the capture id, the session id and the custody parent, and returns the stored string or refuses. Its steps, in order:
   1. The custody parent must exist and be a directory. Follow its symlinks once to get its canonical form.
   2. The recorded path must be absolute.
   3. The recorded path must exist and must be canonical. A recorded path that reaches its directory through a symlink or `..` refuses.
   4. The recorded path must be contained in the custody parent.
   5. The remainder after subtracting the custody parent must have at least two parts, and its first part must equal the session id.
   6. Its last part must equal the capture id.
   7. Return the remainder with `/` separators.

   The exact code I ran is in §9, probe P4. Step 3 has one consequence that a reader can check by eye: the ledger's recorded path always equals the custody parent, then `/`, then the stored string.
2. **`_select_members`, `:1203-1257`.** Add a parameter `custody_root: Path | None = None`. At `:1244`, call the old function when it is `None` and the new one otherwise. No fallback from one to the other: with a custody parent given, every member must pass the new function.
3. **Call site `:1828`.** Pass `args.custody_root`.
4. **Parser, after `:2392`.** Add `--custody-root`, type path, default `None`. With the flag absent the tool behaves exactly as today.
5. **New read-only command `verify-members --artifact <file> --custody-root <directory>`.** It loads the file as plain JSON, claims no authority for it, first refuses any member whose stored string is absolute, contains `..`, or is not in normal form, then calls the existing `authenticate_derivation_corpus` from the reissue tool, prints one PASS or FAIL line per member with no value, and exits 0 only when every member passes. This is the command R4 asks the repair to name.
6. **Optional, for the council to rule: one note.** `derivation_notes["member_custody"]`, written only when `--custody-root` is given, holding fixed text: that stored paths are relative to the directory holding one directory per session, and the command of site 5. The validator admits it unchanged (probe P3; the validator reads only `excluded_members` from the notes, `joulewise/calibration_bracketing.py:991-994`). It holds no absolute path. I recommend it, because R4 has the reader name a directory and the file should say which one. If the council reads R7 strictly, drop it and let the decision log carry the sentence.
7. **Test fixture builder, `tests/fixtures/epoch_bootstrap/build.py:152-225` and `:326-410`.** Add an optional `custody_parent`. When given, each session's captures are written under `custody_parent/<session id>/runs/instrument_validation/` and not under the fixture checkout's `runs/`. `_write_session` already takes the runs directory as a separate argument (`:328`), so the change is small.
8. **Tests**, §7.

**Not changed:** `joulewise/calibration_bracketing.py`, `tests/verify_calibration_acceptance_corpus.py`, `scripts/reissue_calibration_acceptance.py`, the four estimator-code files, every file under `configs/`.

**One guard the implementer must hold.** `--custody-root` flows to the naming function and to nothing else. Every other use of the repository root (the ledger, the ledger head pin at `:1589`, the battery records, the git commit lookup at `:1621`) stays on the run checkout. The statement forbids "giving the tool a root directory other than the run checkout", and permits one added argument that "names the custody tree's parent directory" (items 6(d) and 2(c)). C fits both only if this guard holds.

### 5.2 Artifact schema delta

| Field | Before | After |
|---|---|---|
| Member key set | 5 keys | the same 5 keys |
| `source_directory` | string relative to the checkout | string relative to the custody parent, shaped `<session id>/…/<capture id>` |
| `derivation_notes.member_custody` | absent | optional fixed-text note (site 6) |
| Every other key | — | unchanged |

`derivation_input_sha256`, the digest over the inputs of the arithmetic, does not include paths (`issuer:2258-2296`; it takes member ids and values only). So the naming change cannot move it. `derivation_sha256`, the digest over the whole file, does move, as it does for every new file.

### 5.3 How r6 and r7 stay valid unchanged

No file that reads them changes. Their bytes are untouched. Probe P2 shows every stored path in r2 to r7 is already relative, in normal form, and ends in its member id, with a first part that names a window directory (`runs_window_a2_20260722`, and so on). The new calibration follows the same shape with a night directory in that position. Probe P6 records the seven files' digests for the before-and-after comparison R6 requires.

### 5.4 What a future reader can re-verify, and how

The reader has the repository and the archived night directories.

| Link | Check | Command |
|---|---|---|
| Issued file is the registered one | whole-file sha256 equals the digest registered in code | the loader, `load_calibration_acceptance_bound` |
| Member files are the captured ones | the two primary files hash to the two digests in the member entry | `verify-members --artifact <file> --custody-root <P>` |
| Member belongs to the recorded capture | the hash of the two digests equals a prior-set row's `content_id`, and that row has the same capture id, a session id equal to the first part of the stored path, and disposition valid | same command (the prior-set link is part of `authenticate_derivation_corpus`, `reissue:207-224`) |
| Statistics follow from the member values | recompute minimum, maximum, mean, standard deviation | the verifier, once the issuing transaction adds this calibration's stored statistics to `:25-66` |
| Prior set equals the ledger up to the cut-off | replay the ledger and compare with `ledger_cutoff.head_digest` | needs the ledger file; see finding F3 |
| Raw sampler output matches the evidence file | depends on whether `manifest.json` lists raw file digests | NOT VERIFIED: I opened no manifest |

## 6. Question 3 — science and custody risks

**Can any design let a choice depend on measured values?**
- The stored string is a function of three ledger fields: recorded path, session id, capture id. None is a measured value. Membership is decided at `issuer:1218-1236` before the naming function runs and does not consult it.
- One ordering fact to disclose: the naming function runs per member, after that member's stored timing value has been read and compared with the ledger row's text (`:1237-1242`). A refusal from the naming function therefore comes after one value was read by the program. The refusal message carries no value. The statement already records this for the present refusal (item 6(d)).
- Under A the custody parent is a free argument with several accepted values. Under C one value is accepted. Under B the mapping of sessions to directories is free in the same way as A unless B adds the same session rule.
- The repair must be merged before the first run, as the statement requires. A repair written after a candidate exists could not be called blind.

**Does the evidential chain stay intact?** Yes. The chain is: ledger row, which holds the two digests; then the two primary files, which must hash to them; then whatever the manifest binds. The issuer still authenticates bytes against the ledger row at `:1033-1053`, through the ledger's own recorded path. The repair changes only the name written into the calibration file. No ledger row and no custody byte is written (R3).

**iCloud offload and archive plans after issuance.**
- Stored paths are relative, so moving the archive does not break the member check. Probe P5 passes on a relocated copy.
- The archive must keep each night directory's name and inner layout. A renamed night directory fails the join.
- The ledger rows keep the absolute path of the capture machine. Any tool that reads bytes through the ledger (the issuer itself, and ledger loading with custody verification on) stops working for these rows once the night directories leave `/Users/edr/night-custody`. That is already true of the 38 oldest rows, whose recorded paths are absolute iCloud paths (runbook `:363`). So: offload only after the issuing transaction is complete, and never before (runbook `:2573-2574` says the same for an unissued calibration).
- iCloud can replace a local file with a placeholder whose content downloads on first read. The runbook records an 11-hour wait for 3.33 GB of such files (`:2136`). Before deleting any local copy, run `verify-members` against the archive copy and keep its output.

## 7. Question 4 — defect-shaped tests

Each test asserts the refusal's reason text, not only the exit code, following the file's own rule at `tests/test_issue_calibration_acceptance_generation.py:902-909`. All use made-up captures (R1). macOS note: temporary directories sit behind a symlink (`/tmp` is `/private/tmp`), so fixtures must record canonical paths, or step 3 of the new function refuses them.

| # | Test | Before repair | After repair |
|---|---|---|---|
| T1 | Two made-up sessions with captures under `custody_parent/<session id>/…`, beside the fixture checkout. `prepare-candidate --custody-root custody_parent` exits 0; every stored path is relative, starts with its session id, ends with its capture id. | RED (the flag does not exist; without it the tool refuses "lies outside the repository") | GREEN |
| T2 | The same made-up values prepared once in the old layout and once in the new. `derivation_input_sha256`, member values, statistics and thresholds are equal; only stored paths and the note differ. This is R2 in executable form. | cannot run | GREEN |
| T3 | The two existing tests at `:1518` and `:1539` pass unmodified. | GREEN | GREEN |
| T4a | Capture directory under a directory that was not declared. | — | refuses "lies outside the declared custody root" |
| T4b | Recorded path containing `..`. | — | refuses |
| T4c | Recorded path that is a symlink leading out of the custody parent. | — | refuses |
| T4d | Recorded path that is relative. | — | refuses |
| T4e | Capture directory whose name is not the capture id. | — | refuses |
| T4f | Capture directory inside another session's night directory. | — | refuses |
| T4g | Custody parent one level too high; one level too low; missing. | — | each refuses |
| T5a | `verify-members` on T1's candidate, naming the custody parent. | cannot run | exit 0, all PASS |
| T5b | Same, naming a copy of the custody parent made elsewhere. | — | exit 0 |
| T5c | Same, after flipping one bit of one `instrument_evidence.json`. | — | non-zero; that member FAIL; the others PASS |
| T5d | Same, naming the checkout. | — | non-zero |
| T5e | A file whose stored path is absolute, has `..`, or passes through a symlink leading out. | — | each non-zero |
| T6 | sha256 of r2 to r7 equals the values in §9 P6; the loader loads each registered one. | GREEN | GREEN |
| T7 | The candidate's text does not contain the custody parent's absolute path anywhere. | — | GREEN |
| T8 | Removal check: deleting any single step of the new function turns exactly one of T4a to T4g red. | — | required |

R8 is separate from these: before the issuance step, the operator runs the repaired function on the 12 valid captures' recorded paths and records the output. My probe P4 ran a stand-in of the function on all 24 recorded paths, which include those 12.

## 8. Question 5 — reasons to prefer not changing code

1. **An existing mechanism the scout missed, on the reading side.** The contract "stored path is relative to a directory the caller names" already exists. The reissue tool calls it `--corpus-root` (`:560-567`), and r2 to r7 can only be verified that way, since none of their capture directories is in the checkout. This is why C changes no reader.
2. **No existing mechanism on the writing side.** I found no flag, constant or map in the issuer that names a directory outside the checkout. Pointing `--repo-root` at the custody parent is forbidden by the statement and would also break the head-pin and commit lookups. Editing the candidate's paths by hand is not a sanctioned route and would be worse than a reviewed code change. So the code must change, or nothing issues.
3. **The cost of changing.** The issuer's digest `ceaf3807…` is written into the statement. The repaired tool has a new digest, to be recorded at run time under item 2(e) and disclosed under R9.

## 9. Findings

**BLOCKER**

- **F1. No existing command can perform R4's member check on a made-up calibration or on a candidate.** The verifier refuses ids it has no stored statistics for (`tests/verify_calibration_acceptance_corpus.py:76-78`). The reissue tool's command line accepts only loader-authenticated files (`scripts/reissue_calibration_acceptance.py:579-582`). Designs A and B as written name these two as the checking route, so neither satisfies R4 as it stands. Cure: site 5.
- **F2. The guard of §5.1.** If `--custody-root` reaches any use of the repository root, the repair becomes the forbidden cure. A test should run T1 and assert the candidate's ledger cut-off and battery-record notes equal those of the old-layout run in T2.

**SHOULD-FIX**

- **F3. The ledger is not in the repository.** `.gitignore:8` ignores `runs/`, and `git ls-files` lists no production ledger in either checkout. Only its head pin is committed. The statement's item 2(d) describes the ledger's digest as "at commit `722f7bd1`"; more exactly, it is the digest of an untracked file whose head the committed pin binds. A reader with "only the repository plus the archived night roots" cannot replay the ledger. Cure: archive the ledger file (sha256 `23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d`) with the night directories. No code change.
- **F4. Containment alone is too weak** for a custody parent that holds other sessions. Cure: the session rule (step 5).
- **F5. The custody parent should not be a free choice.** Cure: the same rule.
- **F6. Existing readers accept an absolute stored path that lies inside the named directory**, and a non-normal path that stays contained (probe P5b). The issuer is today the only guard of "the issued file stores no absolute path". Cure inside the repair: the refusal at the start of `verify-members`, and T7. Changing the two existing readers is a separate, later change.
- **F7. The scout's validator change should be dropped.** It is not needed (probe P3) and it enlarges the repair.
- **F8. The run checkout and the main branch have diverged.** `722f7bd1` is not an ancestor of `670756f3`, nor the reverse. The repaired tool must reach the run checkout by changes that passed the pull-request gate (item 2(e)), with the four files of item 2(d) byte-identical afterwards. Procedural, for the operator.

**NIT**

- **F9.** The verifier's flag is named `--repo-root` though it never needs to be a repository. An alias `--corpus-root`, as the reissue tool has, would help. Not in this repair.
- **F10.** The verifier does not check that the directory name equals the member id; the reissue tool does (`:175-178`). Not in this repair.
- **F11.** The help text of `--repo-root` (`issuer:2388-2391`) says member paths are recorded relative to it. Add "unless `--custody-root` is given".
- **F12.** The old naming function follows symlinks without requiring the path to exist (`:907`). Leave it; the new function is strict.

## 10. Executed probes

Scripts and outputs are in `/tmp/custody-consult-fable-77b1bee2/` (scratch, not in any repository).

**P1. Recorded paths, as strings** (`probe_locators.py`, `probe_rows.py`).
```
unique locators 86   external 48   kinds {'absolute': 86}
W rows 52   unique locators 24
basename == attempt_id: 52 of 52
first component == session_id: 52 of 52
every W path: depth 4 | middle runs/instrument_validation | exists True | resolve_same True | is_symlink False
/Users/edr/night-custody: not a symlink; not inside any git repository
```

**P2. Stored paths in r2 to r7** (`probe_history.py`). For all seven files: relative, normal form, last part equals member id: True. Present in the checkout: 0. Keys of `derivation_corpus`: `members`, `n`, `selection`.

**P3. Validator on r7 with one change at a time, digest recomputed** (`probe_validator.py`).
```
baseline r7 structural validator: True
extra key in derivation_corpus: True
extra top-level key: True
night-relative source_directory: True
ABSOLUTE source_directory: True
dot-dot source_directory: True
extra MEMBER key (design B): False
production loader on r7 file: True
```

**P4. Proposed function** (`probe_design_c.py`, parts 1 and 2).
```
unrepaired function refused 24 of 24; proposed function returned a relative path for 24 of 24
root = /Users/edr (too high): REFUSED      root = the night directory (too low): REFUSED
root = the run checkout: REFUSED
made-up tree: own session ACCEPTED; undeclared root, '..', symlink escape, relative path,
wrong basename, another session's directory, missing directory, missing root: each REFUSED
```

**P5. Round trip through the existing reissue function, made-up captures outside the checkout** (part 3).
```
reader names the custody parent: all_authenticated=True 4/4
reader names a RELOCATED copy: True 4/4
reader names the checkout: False 0/4        reader names the undeclared parent: False 0/4
after a one-byte mutation: False 3/4
stored path leaving through '..': False 3/4  through a symlink leading out: False 3/4
```
**P5b.** (`probe_absolute.py`) Stored path absolute but inside the named directory: accepted. Non-normal but contained: accepted. This is finding F6.

**P6. Digests, identical before and after my probes.** Issuer `ceaf3807b2fde7d50374c4781e1c0eff3fb8fea38344b37950cf67fa8e757105`. Estimator files: `powermetrics_fiducial.py` `386e8254…4216bab92`, `uncertainty_evidence.py` `b583f35a…9cd94ae8`, `adapters/powermetrics.py` `70f47086…5116e5e4`, `reduce.py` `7b9c0d28…9ff9fcc`. Issued files: v2 `31611396…`, r2 `3c92dd66…`, r3 `73f02263…`, r4 `dcb3d3ed…`, r5 `92b9c060…`, r6 `0227bca3…`, r7 `9c3a29f6…` (full values in `digests_after.out`). Ledger `23f72c37…`, equal to the statement's. The run checkout's issuer, reissue tool, verifier and validator are byte-identical to the working tree's. Both checkouts clean.

**P7. Existing tests.** `tests.test_reissue_calibration_acceptance` plus the two issuer tests at `:1518` and `:1539`: 8 tests, OK, 8.6 s.

**NOT EXECUTED**
- `prepare-candidate` or `check` on any input, real or made-up.
- Any end-to-end run of a repaired issuer. I changed no code; P4 runs a stand-in function written in the probe.
- The full issuer test file and the full validator test file.
- The verifier on r2 to r7 against their archived capture directories (not present on this checkout).
- Reading `docs/decision_log.md` D-138 and the runbook's cold-packet section.
- Any check of what `manifest.json` binds.
- Which 12 of the 24 captures are the valid ones (I did not read dispositions).

RECOMMEND: C
