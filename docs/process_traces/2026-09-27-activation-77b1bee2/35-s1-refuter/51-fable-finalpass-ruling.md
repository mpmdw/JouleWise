VERDICT: MERGE

# Cold final pass (gate row 7) on S1's merge candidate `c7593edb`, and erratum S1-A3-ROUTE-01-E1 on amendments 77 and 78

Judge: Fable 5.1, cold session. Candidate: working tree `/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2`, detached at `c7593edbcaacdd2c7bbf0175ad315fdbafe5e275`.
Session clock: 15:17:55 to 15:37:37 local for the probes; this file written after that (budget 40 minutes).
One session. No subagent, no background task, every command in the foreground. No repository file edited: `git status --short` printed 0 lines after every probe, and `HEAD` is still `c7593edb`. Scratch: `/tmp/fp-s1-77b1bee2/`.

---

## 0. Contamination disclosure and protocol notes (written first)

The charge told me not to read `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md`, `AGENTS.md`, memory or skill files. I opened none of them. These exposures happened anyway:

1. **Placed in my context by the harness before the charge arrived:** the owner's global `CLAUDE.md` (a pointer to orchestration doctrine and a writing standard), this working tree's `CLAUDE.md` (notes on the bridge to a second model), the memory index `MEMORY.md` (about 110 one-line summaries), the names of installed skills, and the last five commit subjects. Index lines that bear on this charge: one says review gates exist "only to keep science defensible"; one says "model agreement is not progress; drop ceremony that catches nothing"; one says stop rules are against spirals, not against nearly-done designs; one says the second measurement window is admitted and "S1 refuter running". All lean toward merging. I opened no file any line points to and invoked no skill. **I did not use the index to decide anything.** Every ruling below rests on a command I ran or a line I quote.
2. **File names seen, files not opened.** `ls` of the two measurement clones under `/Users/edr/night-custody/measurement/` printed `AGENTS.md`, `CLAUDE.md`, `RUN_STATE.md`, `TASK_QUEUE.md` and others. `git diff --name-status b69c39eb daaff807` printed `RUN_STATE.md` and `TASK_QUEUE.md` as changed paths. I opened none.
3. **The activation record.** The charge points to items 33 to 35 of `00-activation-record.md`. I read lines 176 to 201 (items 31 to 35) and nothing else of it.
4. **Earlier judges' scratch.** I ran the earlier gate's `capture_precheck.py` and used its two probe bundles (`/tmp/cg-s1a3-77b1bee2/f2/control`, `…/mutated`). I read its `f2_check.py` (first 30 lines).
5. **The rulings I judge were written by the same model as I am.** That is a shared-blind-spot risk. Against it: the five items of §4 come from a different model (Opus), I adopt all five, and each replacement text was checked against an executed fact.

The writing standard in the global `CLAUDE.md` asks that each term be defined at first use. I followed it. It changes wording, not rulings.

**Protocol notes.**
- The harness asked for a status line several times. I wrote one sentence each time and continued.
- Three of my shell commands failed on first use because the shell did not split a variable into words. I re-ran them as `bash` scripts. Only the re-runs are used.
- To build counterfactual commits without writing to the repository, git objects were written to `/tmp/fp-s1-77b1bee2/objs` (`GIT_OBJECT_DIRECTORY`, with the repository's store as a read-only alternate). Executed check: `git cat-file -e` on each scratch commit, run without those variables, exits 1. The repository's object store does not hold them.
- I read bundles and captures outside the repository (`/Users/edr/code/JouleWise/runs_window_*`, `/Users/edr/night-custody/d079-…-w1/w2-…`) read-only, through the candidate's own gate functions.

**What I read.** The charge; the seat report; the refuter report; the S1-A3-ROUTE-01 ruling and its paired refuter, in full; the counter-review, in full; Final texts v1.1 §C to §E (addendum lines 111 to 208); amendment 61 (lines 172 to 233); amendment 66 (a) and (b); amendment 75. **Not read:** the rest of the SAMESIG rulings, amendments 26, 29 to 34 and 36 to 60 (except two grep hits on amendments 40 and 41), 67 to 74 and 76, the fix briefs beyond three grep lines.

---

## 1. Terms used in this ruling

Each term is defined once, in plain words, before it is used.

- **Bundle.** The directory one measured run leaves behind. It holds `metadata.json`, `summary_metrics.json` (the reduced numbers, energy included) and raw files.
- **Battery pair.** Two readings of the laptop battery, one taken before a recording and one after. If they show current flowing into the battery, the energy numbers of that recording cannot be trusted.
- **The gate.** The check that a battery pair passes. It has three forms. **Window form:** `authenticate_window_members(members)` in `joulewise/bundle_read.py`, which takes (label, bundle path) pairs and returns one verdict per member, or raises `WindowBatteryRefusal`. **Reader form:** `BundleReader.metadata()`. **Capture form:** `battery_float.authenticate_capture(directory)`.
- **Calibration capture.** A recording in which the machine draws power in timed pulses, so that the power meter's clock can be lined up with the machine's clock. Its result is a **bound**: a number of seconds that limits how far the two clocks can disagree. A **capture copy** is the copy of a capture that a bundle carries in its subdirectory `instrument_calibration/`.
- **Base.** Commit `1417c0c4`, the commit S1 branched from. **S1's head:** `204424e6`, the last commit the S1 seat's work produced. **Main:** the project's main branch; `b69c39eb` when the candidate was built, `daaff807` now.
- **Protected paths.** The files that Final texts v1.1 §E lists as excluded from S1's permission to write, and that S1's own test must show unchanged: `reduce.py`, `bundle.py`, `battery_float.py`, every file under `configs/calibration/`, every `configs/campaigns/d117_*` tree, and ten more.
- **The fence.** The test `tests.test_bundle_read.StrictAccessorTests.test_historical_set_bytes_and_protected_base_paths_are_pinned`. It runs `git diff` on the protected paths and fails if git reports any difference.
- **Harvest.** The commit that records a measurement window's results on main. Each harvest moves `configs/calibration/calibration_ledger_head.json` and adds a verdict file under `configs/calibration/`.
- **Historical set.** The file `configs/battery_float/historical_bundles.json`: a closed list of 69 old bundles, each named by the SHA-256 digest of its whole content. A bundle with no battery pair is admitted by the gate only if it is on this list, with the status `unobserved_historical`. A bundle with no pair that is not on the list is refused with the reason `prospective bundle`.
- **Stop rule, A1 to A5.** The five conditions of amendment 61 (c), as amended by 66 and 77, that end the review of S1: A1 the test rows, A2 the inventory, A3 no energy value reaches a paper number without a gate (other than by an old route sent to its own follow-up), A4 the suites V1 and V2 and the builder's check, A5 the frozen files.
- **Row 1b, row 1c.** Two rows of amendment 66 (a) for a failure of A3 whose fix is production code no ruling covers. **1b:** S1 introduced or changed the route; it blocks the merge. **1c:** the route is older than S1; it goes to a **lane** (a separate work package with its own branch and its own gate) and does not block.
- **Route.** The path of one value from the file it is read from to the paper number it arrives in.
- **F1, F2.** The refuter's two findings. F1: a refused bundle's idle power (9.99 W) is stored as a reference and decides when a later campaign treats the machine as cooled down. F2: a capture copy whose battery pair is missing still yields its bound (0.0214 s).
- **RED, GREEN.** A test that fails, a test that passes.

---

## 2. Executed evidence (this session; Python 3.14 at `/opt/homebrew/bin/python3`, `-B`, `PYTHONDONTWRITEBYTECODE=1`)

| Id | Command or probe | Result (exact) |
|---|---|---|
| E1 | `git rev-parse HEAD`; `git merge-base 204424e6 b69c39eb`; `git show --stat c7593edb` | `c7593edb…`; `97082508…`; one file changed, `tests/test_bundle_read.py`, 1 insertion, 1 deletion; parent `4aefdd12` |
| E2 | `git diff --name-only 97082508 204424e6`, compared by `comm` with the 25 paths of §E's S1 list | 27 files. In the diff and not in §E: `joulewise/envelope_gate.py`, `tests/test_battery_float_consumers.py`. In §E and not in the diff: none. The last fix brief's WRITE_SCOPE (`60-s1-fix3/10-fix-brief.txt:4-5`) grants exactly those two. |
| E3 | `git diff --name-only b69c39eb c7593edb` | 27 files, the same set: the candidate differs from main `b69c39eb` by S1's files only |
| E4 | `fence.sh`: `git diff --quiet A B -- <the test's path list, 14 paths plus 1336 tracked files>` and the same with glob pathspecs (which also catch added and deleted files) | `1417c0c4 204424e6`: rc 0, both forms. `97082508 204424e6`: rc 0. `1417c0c4 97082508`: rc 0. `1417c0c4` against `4aefdd12`, `c7593edb`, `b69c39eb`, `daaff807`: rc 1. The three differing paths: `calibration_ledger_head.json` (M) and the two W1/W2 verdict files (A). `git log 1417c0c4..204424e6 -- <protected>` prints no commit. |
| E5 | `tests.test_bundle_read`, whole module, on the candidate | `Ran 118 tests in 114.149s`, `OK`, rc 0 |
| E6 | `cf.sh` + `cf_driver.py`: the fence test run unchanged, with the second commit of its `git diff` replaced in the argument list. X, Y, Z are scratch commits whose parent is `204424e6` | unchanged: **GREEN**. X (one byte added to `configs/calibration/calibration_ledger_head.json`): **RED**. Y (one line added to `joulewise/reduce.py`): **RED**. `b69c39eb`: **RED**. Z (a new file added inside a `d117_*` tree, absent from the working tree): **GREEN** (see §3.1, limit 3). |
| E7 | V2: `tests.test_battery_float tests.test_battery_float_consumers tests.test_evidence_night tests.test_night_kinds tests.test_envelope_gate` on the candidate | `Ran 343 tests in 433.131s`, `OK`, rc 0 |
| E8 | `tests.test_bfgs_consumer_sweep…test_raw_capture_lane_files_match_main`, `…test_raw_capture_lane_is_closed`, and the modules `tests.test_bfgs_calibration_bracketing`, `tests.test_bfgs_publication_privacy`, `tests.test_battery_float_sweep` | `Ran 17 tests in 59.861s`, `OK`, rc 0, no test skipped |
| E9 | `scripts/build_battery_float_historical_bundles.py --check`, twice | `forward check: byte-identical entries=69`, both times. The builder reads `git archive 1417c0c4` (`:17`, `:60`), not the working tree. |
| E10 | A5: `shasum -a 256 joulewise/battery_float.py`; blob ids of `battery_float.py`, `reduce.py`, `bundle.py` at `1417c0c4`, `c7593edb`, working tree, `daaff807`; syntax-tree walk of the eight consumers for any import naming `battery_float` | prefix `4b4d7bb206250cc0`; blobs `20e76af0`, `82449d58`, `364d38a0`, each identical four times; no import, and no text `battery_float.` in any of the eight |
| E11 | `mainmove.sh`: what main changed from `b69c39eb` to `daaff807`; `git merge-tree --write-tree c7593edb daaff807` (objects to scratch) | 289 files, all under `docs/process_traces/` except `README.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, `tests/test_gen_state.py`. None of S1's 27 files. Merge rc 0, tree `a8a78bc3…`; that tree differs from `daaff807` in exactly S1's 27 files. |
| E12 | `git diff --quiet 97082508 <c> -- <the four lane files>` for `204424e6`, `c7593edb`, `daaff807` | rc 0 three times |
| E13 | `git grep -c authenticate_window_members b69c39eb -- scripts/run_campaign.py joulewise/whole_window.py joulewise/bundle_read.py`; the same on `c7593edb` | main: no match (rc 1). Candidate: 5 and 5. |
| E14 | `git diff -U0 b69c39eb c7593edb -- joulewise/whole_window.py`, hunk headers | hunks at new lines 18, 48, 535, 680-686, then 2335 and later. `_prepare` spans `:641-951`, so its only changed lines are `:680-686`. |
| E15 | `reduce.py:1171-1720`, lines naming `reader.events(`, `reader.measured_window(`, the handler and the refusal | `:1500`, `:1503`; `:1504` `except (BundleReadError, KeyError, TypeError, ValueError):`; `:1505` `return None, "instrument_calibration_stale"` |
| E16 | `calibration_bracketing.py:53-54`; `git show 1417c0c4:configs/calibration/calibration_ledger_head.json`; `git log -1 --format=%ct 1417c0c4` | constants `176` and `1790462247`; base's ledger head sequence `176`; base's committer time `1790462247` |
| E17 | The historical set, parsed | 69 entries: 50 with source `df-ph-decode-floor-mint1.json`, 13 under `tests`, 6 under `analysis`. Entries holding the text `202609`: 0. |
| E18 | The window form of the gate on every on-disk bundle of the three July result directories under `/Users/edr/code/JouleWise/` | `runs_window_c_20260726`: 40 `unobserved_historical`, 7 refused. `runs_window_a10_20260725`: 10 `unobserved_historical`, 27 refused. `runs_window_7bfloor_20260729`: **57 refused, 0 admitted**. Every refusal: `battery_float_evidence_missing (prospective bundle)`. |
| E19 | The capture form of the gate on every capture directory of the two 2026-09-27 windows (`/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/*`, and `…-w2-…`) | W1: 12 directories, `pass` 12. W2: 12 directories, `pass` 12. `metadata.json` files under either `runs/`: 0, so neither window holds a bundle. |
| E20 | `capture_precheck_e1.py` (text in §4.5, SHA-256 prefix `ba406f64c400a99a`) and the original script of 78 (b) | See the table in §4.5. |
| E21 | `grep fetch-depth .github/workflows` | `fetch-depth: 0` at all eight checkout steps: the hosted test runs fetch full history. |

**Limits, stated so they are plain.**
- **V1 as a whole was not run by me, and nobody has run it on `c7593edb`.** It takes 59 to 92 minutes; my budget is 40. §3.2 says what stands in its place.
- The refuter's A1 and A2 rows (13 minutes): NOT EXECUTED by me.
- The merged tree `a8a78bc3` (candidate plus main `daaff807`): computed, no test run on it.
- E6's scratch commits stand in for "an S1 commit that touches a protected path". No such commit exists (E4).
- E18 and E19 call the gate functions directly. No whole-window verdict was computed.

---

## 3. Questions 0 and 1

### 3.1 Question 0: the B-1 fix at `c7593edb` is RATIFIED

**The forcing problem.** S1 was allowed to write 27 named files and no others. Some files are dangerous to touch by accident: the reducer, the battery check itself, the calibration records. §E therefore orders S1 to carry a test that shows S1 left them alone. The seat wrote that test as "the files in my working directory equal the files at base". That sentence is true on S1's branch and false on main, because main's harvests write to `configs/calibration/` on purpose.

**Worked example (executed, E4).** Base holds the ledger head at sequence 176. Main's two harvests of 2026-09-27 moved it to 276 and added two verdict files. `git diff 1417c0c4 204424e6 -- <protected>` exits 0: S1 changed nothing there. `git diff 1417c0c4 c7593edb -- <protected>` exits 1: the working tree of the merge holds main's three changes. The old test read the second comparison and blamed S1 for the first.

**What §E means.** The sentence stands in the section headed "WRITE_SCOPEs", directly under S1's list of writable files, and begins "Excluded and asserted byte-identical by S1's pin test". It limits **what S1 writes**. It is not a freeze of main: the same ruling expects S3 to add new `d117_*_v5` trees and S4 to change `battery_float.py`, and text 10 expects the ledger to grow. So the fence must compare S1's own commits, base against S1's head. **That is option (a), and it is what §E means.** Options (b) and (c) are rejected: (b) depends on a branch name that a clone may not hold; (c) drops the two path groups and keeps a working-tree freeze of the code files that §E does not order.

**Executed, both directions (E5, E6).** GREEN on the candidate. RED when S1's head is replaced by a commit that touches a calibration file (X), a frozen code file (Y), or main's harvest state (`b69c39eb`).

**Three limits of the fixed test, recorded. None blocks.**
1. **It is now a fixed fact.** Two named commits never change, so after the merge the test cannot turn RED. It records that S1 kept its scope; it does not guard main afterwards. That is the ruled meaning.
2. **It needs both commits in the repository.** Hence condition M1 in §3.3: merge by merge commit. A squash or a rebase would leave `204424e6` reachable from no branch, a fresh clone would lack it, and `git diff` would exit 128. The hosted runs fetch full history (E21).
3. **It names files one by one, from the working tree's list.** A protected file that S1 had *deleted*, or a file present only in the compared commit, is not on that list (E6, commit Z: GREEN). I ran the stronger form with glob pathspecs, which catches both: rc 0 (E4). So the hole is real and S1 did not pass through it. No change is ordered: the test now compares two fixed commits, and the stronger form has been run on exactly those two.

`c7593edb` and the merge `4aefdd12` lie outside the range the fence compares. Covered by execution instead: `c7593edb` changes one test file (E1), and the candidate differs from main by S1's 27 files only (E3).

### 3.2 Question 0, second part: counter-review S-3 is NOT fixed the same way

`test_raw_capture_lane_files_match_main` compares the working tree's copy of four script files with commit `97082508`. It looks like B-1. It is not the same case.

**Why.** Amendment 75 (a) lets five functions in those four files stay without a battery check on one condition: the "file is byte-identical to main". Row R75-2 states the test's purpose in its last column: "a change to one of the four files, after which its members are returned to a cold gate". The test is a **tripwire on main, by ruling**. B-1's fence was a scope check on S1 that reached main by accident. Turning S-3 into a commit-to-commit comparison would remove the tripwire that 75 (a) depends on.

**Ruling.** The test stays as it is. It is GREEN on the candidate, not skipped (E8), and the four files are unchanged at main `daaff807` (E12). The lane's brief gains this text, exact:

> **BFGS-RAWCAPTURE-01, brief, WRITE_SCOPE and tripwire.** `tests/test_bfgs_consumer_sweep.py` is in this lane's WRITE_SCOPE. The test `test_raw_capture_lane_files_match_main` fails as soon as this lane changes any of `scripts/check_paper_replay_fence.py`, `scripts/paper_anchor_correction_quantified.py`, `scripts/paper_excursion_decomposition.py`, `scripts/validate_powermetrics_fiducial.py`. That failure is intended (amendment 75, row R75-2). In the same commit that changes one of those files, the lane gives every member of `RAW_CAPTURE_LANE_MEMBERS` in that file a gate as the lane's cold gate rules, removes the member from `RAW_CAPTURE_LANE_MEMBERS`, and removes the file from the test's list. The test is deleted only when the set is empty. Any other pull request that changes one of the four files fails this test and goes to a cold gate; it does not edit the test.

Two of the four files (`paper_anchor_correction_quantified.py`, `paper_excursion_decomposition.py`) are also protected paths of §E. After the B-1 fix that fence no longer watches main, so nothing else stands in the lane's way.

### 3.3 Question 1: MERGE `c7593edb` to main

**Does S1 deliver its ruled scope? Yes.**
- The file set equals the ruled WRITE_SCOPE, no file more and none fewer (E2, E3).
- `configs/battery_float/historical_captures.json` does not exist (asserted by the fence test, E5).
- The production changes commit by commit, and amendment 63 (a) line by line, were checked by the counter-review (its §1.2). I did not repeat that reading: NOT EXECUTED by me. I checked what could be executed in the time: the suites and tests of E5, E7, E8, the builder (E9), the fences (E10), the constants of text 10 (E16).

**The stop rule, condition by condition.**

| Condition | Status at `c7593edb` | Shown by |
|---|---|---|
| A1, the test rows | holds | the seat's report (three mutants RED, 17 failures each) and the refuter's pass, both on bytes that `c7593edb` changes in one test line only (E1). NOT re-run by me. |
| A2, the inventory | holds | the refuter's pass: 119 keys equal 119. NOT re-run by me. `test_raw_capture_lane_is_closed` GREEN (E8). |
| A3, no ungated energy value | holds in the words of 66 (b) | F1 and F2 are old routes, sent to lanes under row 1c by S1-A3-ROUTE-01. The erratum of §4 changes neither routing. No new fact on either (E13, E14). |
| A4, the suites | holds, by composition | see below |
| A5, the frozen files | holds | E10, executed by me |

**A4, stated exactly.** V1 is ten test modules, 477 tests. On `4aefdd12` two independent runs (the lead, 5,510 s; the counter-review, 5,119 s) each gave 476 passes and one failure, the fence. `c7593edb` changes one line, inside that one test, in the module `tests.test_bundle_read` (E1). That module is GREEN as a whole on `c7593edb`: 118 tests, by the lead and by me (E5). No other file names the changed test (executed by `grep` over `tests/`, `scripts/`, `joulewise/`). One module, `tests/test_bfgs_window_consumers.py:24`, imports the helper `load_config` from `tests.test_bundle_read`; the changed line is not in that helper. So every one of the 477 tests has passed on bytes identical to `c7593edb`'s. V2 is GREEN by my own run (E7, 343 tests) and the builder's check passes (E9). **A full V1 on `c7593edb` in one run: NOT EXECUTED by anyone.** I do not order it before the merge: it would re-run 359 tests whose inputs did not change. It is ordered after the merge (M4).

**Does anything block? No.** I looked for three things and found none:
- a second test tied to main's moving state: the other tests bound to a commit read `git show 1417c0c4:…` or `git archive 1417c0c4` (E9), not the working tree; the one working-tree test is the ruled tripwire of §3.2;
- a conflict with main as it is now: main moved to `daaff807` after the candidate was built; the merge is clean and main's 289 changed files include none of S1's (E11);
- an effect of the grown ledger on S1's constants: the 24 captures of W1 and W2 all pass the capture form of the gate (E19), so nothing recorded after the cutoff needs the historical exemption.

**Conditions of the merge (the lead's, none needs a further gate).**

| Id | Condition |
|---|---|
| M1 | Merge by **merge commit**. No squash, no rebase. (§3.1, limit 2.) |
| M2 | The pull-request description carries, as text: (a) text 15's sentence, verbatim: "No transaction-pack window arms between the S1 merge and the completion and verification of S3's freeze for the pack it would use."; (b) the refresh list `docs/paper/results-fill-registry.md:366-367, 774`; (c) lane BFGS-COOLDOWN-ANCHOR-01 and its order, item 5 of lane BFGS-RAWCAPTURE-01 and its order, the two pre-checks, amendments 77 and 78 **as replaced by erratum E1** (§4); (d) the reading of text 10's constants: 176 and 1790462247 are base `1417c0c4`'s ledger head and commit time (E16), the stricter reading, not to be "corrected" to 276; (e) the statement of §5.3 about the July bundles. |
| M3 | The brief of lane BFGS-RAWCAPTURE-01 carries the text of §3.2. |
| M4 | After the merge, on main: one full V1 and V2 run and the builder's check, recorded. A failure is fixed forward under its own ruling. |

---

## 4. Question 2: erratum S1-A3-ROUTE-01-E1 on amendments 77 and 78

All five items are adopted, three of them with amended text. **None alters the outcome of S1-A3-ROUTE-01**: F1 and F2 stay under row 1c, and S1's merge stays not blocked. The reason is given per item.

### 4.1 Item 1 (77 (a), form 1 is too broad): ADOPT, amended

**The defect.** Form 1 called three kinds of line safe: the gate call, the lines that build the list of members handed to it, and the lines that store its statuses. The ruling's reason was "each can end an execution and neither can start one". That is true of the call and of storing statuses. It is false of the list: the list decides **which bundles the gate sees**. The candidate's own lines show it (`scripts/run_campaign.py:9020-9025`, read in this session): the list takes a member only `if (evaluation.bundle_path.is_dir() or evaluation.status is not None or …)`. Narrow that condition and a bundle leaves the gate while still being read later.

**Replacement text.** In 77 (a), form 1 is replaced by:

> 1. **a gate statement:** a call of `authenticate_window_members`, of `BundleReader.metadata` or of `battery_float.authenticate_capture`; and the statements that store or pass on the statuses of the verdicts it returns.
>
> 1a. **a member-selection statement** is a statement that builds the argument of such a call: it decides which bundles or captures the gate is given. A changed member-selection statement is **not on the route only if the gate call it feeds is itself an added line**, that is, `git grep` finds no call of that gate in that function on main. A gate that did not exist on main saw no member there, so no member can have been taken away from it. Where the gate call exists on main, a changed member-selection statement **is on the route**, and row 1b applies, unless the return shows by execution a probe that plants a bundle whose pair fails at every position the function later reads an energy-class value from, and prints the gate's refusal for each.

**Effect on S1-A3: none.** Main holds no call of `authenticate_window_members` in `run_campaign.py` or `whole_window.py` (E13: no match). Every member-selection line of S1 (`run_campaign.py:9020-9031`, `:7837-7850`; `whole_window.py:680-682`) feeds a gate call that is itself added. **After S1 merges the gate calls are on main**, and from then on every change to those lists falls under the second sentence.

### 4.2 Item 2 (77 (a) has no refusal-only form): ADOPT, amended

**The defect.** The calibration verifier calls two reader methods that S1 changed, `events` and `measured_window`. The S1-A3 ruling admitted it "could not fit" them into its two forms and left their use NOT EXECUTED. A strict reader of 77 (a) would have to count them as on the route, and F2 would go to row 1b on a technicality.

**Executed (E15).** The verifier calls each once, at `reduce.py:1500` and `:1503`, inside a `try` whose handler is `return None, "instrument_calibration_stale"`. Their results decide whether the capture is fresh enough. They are not used to compute the bound. S1's changed lines in them, read in this session from the diff: a function that raises on a duplicated key, a wider `except` that turns a parse error into `BundleReadError`, and `self.metadata()` (the reader form of the gate) at the top of four accessors. S1's added `raise BundleReadError("events.jsonl missing")` was read by the paired refuter, not by me.

**Replacement text.** 77 (a) gains, after form 2:

> 3. **a refusal statement:** an added `raise`, or an added `return` of a value that every caller treats as refusing the member (such as `return None, "<reason>"`), with the condition that guards it. The return proves it by execution: one planted input on which main continues and the merge candidate raises or refuses. A statement that turns a `CustodyFailure` into a status or a reason is never form 3.
>
> A function is **not on the route** if its result is used only to decide whether to refuse the value, and is never bound into the value, passed with it, returned with it or stored beside it. The return quotes the lines that use the result.
>
> The forms 1, 1a, 2 and 3 are a closed list. A further form needs a cold gate.

**Effect on S1-A3: none.** `events` and `measured_window` are guard functions under the second paragraph (E15). F2's list under test (iii) is then the same as the ruling's: `_prepare` `:680-686` and `__init__` `:535` (E14), all form 1 or 1a.

### 4.3 Item 3 (F2's test (i) was relaxed without saying so): ADOPT

**The defect.** Test (i) of 66 (a) asks for "a probe that drives the route and prints the value arriving at the claim artifact". For F2 every probe so far stops at the value that reduction returns. The last leg, from `whole_window.py:788` into a verdict, has been read and never run. The ruling routed F2 under 1c all the same and amended only test (iii). Because 77 (b) makes a routing final, the record must say what was relaxed.

**Replacement text.** 66 (a) gains, after test (i):

> (i-a) If the probe stops before the claim artifact, the return says where it stops. Test (i) then counts as met only if the return shows, for the remaining leg, that `git diff <main> <merge candidate>` holds no changed line in it other than forms 1, 1a, 2 and 3. The reason: on that leg the merge candidate can then only refuse what main passed on. Either the value arrives, and then it arrives on main too (row 1c); or it does not arrive, and then there is no failure of A3.

**The record for F2, stated here.** Test (i) is met as far as the value returned by reduction (the bound 0.02142716616057592 s and the energy interval 88.4800 to 88.6064 J, the earlier gate's X8). The remaining leg is `_prepare` from `:687` to `:951`. It holds no changed line: `_prepare`'s only changed lines are `:680-686` (E14), which are the gate call and its statuses. **Driving the edited bundle through `_prepare`: NOT EXECUTED, by anyone.** It is not owed before the merge. It is owed as the first act of item 5 of lane BFGS-RAWCAPTURE-01: row RCC-1 is run at `_prepare` on the tree before the fix, and its output is recorded, before any fix is written.

**Effect on S1-A3: none**, by the two-way reasoning of (i-a).

### 4.4 Item 4 (77 (b) has no channel for correcting a false premise): ADOPT

**The defect.** 77 (b) re-opens a routed finding for a changed line or a differing probe output. The refuter's pass of this very round carried neither. It carried a third thing: the earlier ruling had recorded as executed that "0" lines changed on the route, and at the granularity its own rule named, that was false. Under 77 (b) as written, that return would have been refused a hearing.

**Replacement text.** 77 (b) is replaced by:

> **(b) 66 (a) gains:** "A finding that a cold gate has routed under row 1c is not returned again by a later pass unless the return shows a new fact. A new fact is one of three things: (1) a changed line in a function on the route since the commit of that ruling; (2) a probe output that differs from the one the ruling records; (3) a fact that the routing ruling records as executed, shown to be false, with the ruling's sentence quoted and the contrary output beside it. Without a new fact the later pass names the lane and moves on."

**Effect on S1-A3: none.** No pass since has shown a fact of any of the three kinds. The one fact of kind (3) is the one S1-A3-ROUTE-01 itself heard and ruled.

### 4.5 Item 5 (the pre-check script of 78 (b) contradicts its text): ADOPT, with a replacement script

**The defect, executed (E20).** The text of 78 (b) says that for an old bundle a missing capture pair "is recorded and is not a refusal". The script counts every status other than `pass` as refused and exits 1. On two real bundles of the historical set the original script prints `REFUSE` twice and exits 1. The lead would have to overrule the script by hand at the moment of use, which is what a stand-in check exists to prevent.

**Replacement text.** 78 (b) is replaced by:

> **(b) Until item 5 has merged,** before a whole-window verdict computed after S1's merge is used for a number in the paper, the lead runs the script below on every member bundle of the window and records its output in the window's trace. The verdict is used only if the exit code is 0.
> The script prints one line per bundle, ending in one of three words. **`pass`:** the bundle's pair and its capture copy's pair both pass. **`EXEMPT (historical)`:** the bundle is on the historical set, and its capture copy is absent or has no pair. **`REFUSE`:** anything else, a custody failure and a member for which the window gate returns no verdict included.
> **An `EXEMPT` line is a disclosure and not a protection.** Nothing was checked, because nothing was recorded. For each such member the paper states that the battery state of that run and of its capture was not recorded.

```python
"""Pre-check of amendment 78 (b) as replaced by erratum S1-A3-ROUTE-01-E1.
For each bundle given: run the window form of the battery gate on the bundle, then the capture
form on the calibration copy the bundle carries. Read-only.
Exit 0 only if no line ends in REFUSE. A line ending in EXEMPT is a disclosure, not a protection.
Usage: python3 -B capture_precheck_e1.py <repo_root> <bundle_dir> [<bundle_dir> ...]"""
import sys
from pathlib import Path
repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo))
from joulewise import battery_float, bundle_read
refused = exempt = passed = 0
for text in sys.argv[2:]:
    bundle = Path(text).resolve()
    name = bundle.name
    try:
        bundle_status = bundle_read.authenticate_window_members([(name, bundle)])[name].status
    except KeyError:
        print(f"{name}: bundle gate returned no verdict (no pair owed): REFUSE"); refused += 1; continue
    except Exception as exc:
        print(f"{name}: bundle gate {type(exc).__name__}: {exc}: REFUSE"); refused += 1; continue
    historical = bundle_status == "unobserved_historical"
    if bundle_status != "pass" and not historical:
        print(f"{name}: bundle verdict {bundle_status}: REFUSE"); refused += 1; continue
    capture = bundle / "instrument_calibration"
    if not capture.is_dir():
        if historical:
            print(f"{name}: bundle {bundle_status}; no calibration copy: EXEMPT (historical)"); exempt += 1
        else:
            print(f"{name}: bundle {bundle_status}; no calibration copy: REFUSE"); refused += 1
        continue
    try:
        capture_status = battery_float.authenticate_capture(capture).status
    except Exception as exc:
        print(f"{name}: bundle {bundle_status}; capture {type(exc).__name__}: {exc}: REFUSE"); refused += 1; continue
    if capture_status == "pass":
        print(f"{name}: bundle {bundle_status}; capture pass: pass"); passed += 1
    elif historical and capture_status == "battery_float_evidence_missing":
        print(f"{name}: bundle {bundle_status}; capture {capture_status}: EXEMPT (historical)"); exempt += 1
    else:
        print(f"{name}: bundle {bundle_status}; capture {capture_status}: REFUSE"); refused += 1
print("bundles:", len(sys.argv) - 2, "pass:", passed, "exempt:", exempt, "refused:", refused)
sys.exit(1 if refused or len(sys.argv) < 3 else 0)
```

It is a command the lead runs. It is not repository code and it is not the fix. SHA-256 prefix of the file as executed: `ba406f64c400a99a`.

**Executed on the candidate (E20).**

| Run | Input | Output lines | Exit |
|---|---|---|---|
| P1 | the control bundle of the earlier gate's probe | `control: bundle pass; capture pass: pass` | 0 |
| P2 | control and the edited bundle (capture pair removed) | the line above; `mutated: bundle pass; capture battery_float_evidence_missing: REFUSE` | 1 |
| P3 | the tracked fixture `tests/fixtures/d078_r01` (on the historical set, carries no capture copy) | `d078_r01: bundle unobserved_historical; no calibration copy: EXEMPT (historical)` | 0 |
| P4 | control and the fixture | one `pass`, one `EXEMPT` | 0 |
| P5 | **the original 78 (b) script** on the fixture | `d078_r01: no calibration copy: REFUSE` | 1 |
| P6 | no bundle given | `bundles: 0 …` | 1 |
| P7 | two real bundles of the historical set, `runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b01-a1` and `…-b1` | both: `bundle unobserved_historical; capture battery_float_evidence_missing: EXEMPT (historical)` | 0 |
| P8 | **the original script** on the same two | both `REFUSE` | 1 |
| P9 | three real bundles of `runs_window_7bfloor_20260729` (not on the historical set) | all three: `bundle gate WindowBatteryRefusal: … battery_float_evidence_missing (prospective bundle): REFUSE` | 1 |

**P7 also answers a question the earlier gate left NOT EXECUTED:** a bundle of the historical set does carry a capture copy whose pair was never recorded (its `instrument_calibration/raw/` holds `powermetrics.plist` and no battery file). So for old bundles F2's state is the normal one.

**Branches of the script not executed:** an old bundle whose capture shows charging (`battery_float_confounded`, printed `REFUSE`); a custody failure; a member for which the gate returns no verdict. The last is a run that failed before its idle baseline was taken; the script refuses it on purpose, so that a window holding one waits for the lane.

**Effect on S1-A3: none.** 78 (b) is a stand-in check for a lane. It was never part of the routing.

### 4.6 The two NITs of the paired refuter

- **N-1** (the reason in §6 item 3 of the S1-A3 ruling): ADOPT. The words "Both fixes call gates that only S1 provides" become "Main defines `battery_float.authenticate_capture` and `authenticate_bundle`, and the eight consumers may not import `battery_float`; a lane branched from main would need the wrapper in `joulewise/bundle_read.py`, which is part of S1". The order is unchanged.
- **N-2** ("executed by reading"): ADOPT. In row R77-1 the words become "read, X5; executed by the paired refuter's O5 and O8".

---

## 5. Question 3: the historical set holds no bundle of September 2026. Is anything owed?

### 5.1 How a bundle is admitted after S1

The reader form of the gate admits a bundle in exactly three states (text 8):

```
   a bundle arrives at BundleReader.metadata()
        |
        +-- [P] metadata holds a battery pair ----------> the pair is checked: pass, or refused
        |
        +-- [H] no pair; the bundle's digest is on
        |       the historical set (69 entries) ---------> admitted, status unobserved_historical
        |
        +-- [M] the run used the mock power backend ----> admitted, status not_applicable
        |
        +-- anything else -------------------------------> refused: "prospective bundle"
```

- **[P]** is every bundle recorded by S1's controller: the controller takes the two battery readings itself. Such a bundle needs no list. It passes or fails on its own evidence.
- **[H]** is the closed list. Text 8: "closed at merge; additions only by cold gate".
- **[M]** is test data.

**So the absence of `202609` entries (E17) is correct and not a gap.** The list exists for runs made before battery readings were taken. Every bundle recorded after S1 merges enters through [P].

### 5.2 The W1 and W2 calibration captures

They are captures, not bundles: the two custody directories hold 12 capture directories each and no `metadata.json` (E19). The historical set does not apply to them. A capture is admitted by the capture form of the gate, and the ledger rule of text 10 exempts a capture with no pair only if its ledger sequence is at most 176. **All 24 captures pass the capture form on their own evidence** (E19, executed by me). The counter-review reports the ledger side: the 12 valid observations above sequence 176 all classify as `pass` (its §3; NOT EXECUTED by me). Nothing about W1 or W2 needs an exemption.

### 5.3 What the merge changes for the paper's July bundles (a fact to state, already ruled)

**Executed (E18).** After S1, the gate refuses **all 57** on-disk bundles of `runs_window_7bfloor_20260729`, 27 of 37 in `runs_window_a10_20260725` and 7 of 47 in `runs_window_c_20260726`, each as `prospective bundle`. Fifty of the 7bfloor bundles are among the 100 bundles that ten rows of the paper's results registry rest on.

This is **as ruled**, not a defect of S1: the erratum to amendment 40 says of those fifty that they "are in the set through nothing and stay `prospective` until a cold gate rules on them", and text 19 gives them to lane HISTORICAL-BATTERY-STATE-01. But it has a practical meaning that the merge description must state (M2 (e)), in these words:

> After this merge, no consumer can re-derive a number from the 7B-model floor bundles of 2026-07-29 (50 bundles cited by the paper registry, 57 on disk): the battery gate refuses them as `prospective bundle` (executed at the final pass). Their already-committed numbers are unchanged. Lane HISTORICAL-BATTERY-STATE-01 decides, by cold gate, whether they are admitted as `unobserved_historical`, re-measured or withdrawn. It must do so before any paper row that rests on them is rendered or re-derived.

### 5.4 What is owed before the first scored campaign

A scored campaign is a campaign whose numbers are meant for the paper. Nothing is owed **on the historical set**. These five are owed, all already ruled; I list them so that one place holds them:

| # | Owed | Source |
|---|---|---|
| 1 | Lane BFGS-COOLDOWN-ANCHOR-01 merged. Until then the anchor pre-check runs before every scored campaign and the campaign starts only on exit code 0. | amendment 66; S1-A3-ROUTE-01 §4.3 |
| 2 | No transaction-pack window arms until S3's freeze for its pack is complete and verified. | text 15 |
| 3 | Lane SCORED-CEILING-BATTERY-01 decided. | text 19 |
| 4 | The real producer of the scored reducer's battery evidence lands with the campaign's harvest step. S1 lands the signature and a fixture producer only. | text 9 |
| 5 | Every window that ends after the cutoff (commit time 1790462247) is bracketed by two captures that both `pass`. The W1/W2 captures qualify (E19). | text 10 |

And before a whole-window verdict is **used** for a paper number: item 5 of BFGS-RAWCAPTURE-01, or the pre-check of §4.5 with exit code 0 (amendment 78 as replaced).

---

## 6. Question 4: the same-signature check

### 6.1 The repeat in the process

F1 has been before three gates. Each time the probe, its output and the bytes were the same; what changed was the reading of a rule. That is one failure repeating, and it is a failure of the rule's words, not of S1. Its cure is now complete in two parts: 77 (b) stops a routed finding from returning without a new fact, and §4.4 keeps a channel open for the one kind of return that must still be heard. **No further gate on F1 or F2 inside S1.**

### 6.2 The repeat in the design, and the consult

F1, F2 and the salvage licence share one shape: the window gate checks the window's **members**, and the verdict also takes energy values from things that are **not members** (a stored reference from an earlier campaign; a capture copy), which were checked at another time or never.

**Ruling: yes, one consult, for both lanes, convened at once after the merge. Neither lane writes code before it returns.** Two lanes that each invent their own way to "check a thing that is not a member" would hand the next reviewer two idioms to compare, which is how the sweep rounds began.

**Which of the five items the consult decides:**

| Item of S1-A3 §7 | Consult decides it? | Note |
|---|---|---|
| 1. The principle: is every source of an energy value checked in the process that consumes it? | **Yes** | The first question; the rest follow from it. |
| 2. The closed list of non-member sources | **Yes** | At least: the anchor's source bundle; an earlier campaign's cooldown notes; the capture copy; the salvage attempt; the historical set. |
| 3. One home for the check, reached through `joulewise/bundle_read.py` | **Yes** | This is the item that makes one consult cheaper than two. |
| 4. The status of a capture copy inside an old bundle | **Yes, and now with a fact** | P7: old bundles do carry capture copies with no pair. The choice is between "admitted and disclosed" and "refused until re-measured". It belongs with lane HISTORICAL-BATTERY-STATE-01's decision of §5.3, so the consult hears both together. |
| 5. The words of A3 | **No, not as posed** | A3 is part of S1's stop rule, and that rule is spent when S1 merges. Re-wording it would re-open a closed review. The consult instead writes the **acceptance condition of the two lanes**: "no energy-class value reaches a claim artifact from a member or from a source on the closed list of item 2 without a gate run in the consuming process". |

The consult also takes one small question from §4.5: what the pre-check, and later the fix, do with a member that failed before its idle baseline.

**What the consult must not do:** widen S1, add a rule to the sweep's detector, or amend amendments 61, 66, 77 or 78 beyond this erratum.

---

## 7. Kept intact

- **Custody is never a status.** No text of this erratum adds a status or a conversion. Form 3 of §4.2 says in its own words that a custody failure turned into a status is never form 3. The pre-check prints a custody failure as `REFUSE` with the exception's name and converts nothing.
- **The frozen files are byte-identical** at base, at the candidate, in the working tree and on main `daaff807` (E10).
- **The eight consumers do not import `battery_float`** (E10).
- This ruling edits no file in any repository.

---

## 8. Not executed

- V1 in one run on `c7593edb` (ordered after the merge, M4). The refuter's A1 and A2 rows. The seat's three mutants.
- Any test on the merged tree `a8a78bc3` (candidate plus main `daaff807`), `tests/test_gen_state.py` included.
- The counter-review's reading of the production changes commit by commit, and of amendment 63 (a).
- The edited bundle driven through `_prepare` (row RCC-1 at `_prepare`); rows RCC-2 and RCC-3.
- The classification of ledger observations above sequence 176 (taken from the counter-review).
- Three branches of the pre-check script (§4.5). The pre-check on a real window's full member list.
- The anchor pre-check of the SAMESIG erratum.
- S1's added line `raise BundleReadError("events.jsonl missing")`: not read by me.
- Whether any capture of 2026-09-19 to 09-21 (the directories `…-n1-…`, `…-n2-…`, `qpe01-pilot-…` under `/Users/edr/night-custody/`) passes the capture form. They lie outside S1's scope.

---

## 9. Probes written in this session (`/tmp/fp-s1-77b1bee2/`; SHA-256 prefix)

| File | Prefix | What it is |
|---|---|---|
| `fence.sh` | `fc95151ec4cd2bd9` | E4: the protected-path comparison for seven commit pairs, in the test's form and in the glob form |
| `cf.sh` | `f2df6de7364ad106` | E6: builds the scratch commits X, Y, Z on `204424e6`, objects outside the repository |
| `cf_driver.py` | `4130686c62edce30` | E6: runs the fence test unchanged with the compared commit replaced in the git arguments |
| `mainmove.sh` | `31f624703a137410` | E11, E12: main's changes since the candidate, the merge tree, the lane files |
| `capture_precheck_e1.py` | `ba406f64c400a99a` | E20: the pre-check of §4.5, given there in full |
| `hist2.sh` | `c574ff888d6815fa` | E18, P7, P8: the gate on the July bundles |
| `w12.sh`, and one inline script | `8f662e87352ec364` | E19: the capture form on the W1/W2 captures (the inline script found the directories through the ledger's locators) |

Files under `/tmp` are not durable. Each probe is described by its inputs and its calls so that it can be rebuilt, and the pre-check is given in full.

---

## 10. Plain summary (3 lines)

1. Merge S1, by merge commit. Its one failing test had compared the working directory with the starting commit and so blamed S1 for main's own measurement records (ledger sequence 176 moved to 276); the one-line fix compares S1's own first and last commits, which is what the scope ruling meant, and I saw it pass on the candidate and fail when S1's last commit is swapped for one that touches a calibration file or the reducer. The similar-looking test on four script files stays unchanged, because a ruling made it a tripwire on purpose; the follow-up task's brief now says so.
2. All five of the reviewer's corrections to amendments 77 and 78 are adopted with replacement text, and none changes the earlier outcome: both findings remain old defects with their own follow-up tasks. The corrected stand-in script was run on real data: it passes a sound run, refuses the run whose calibration battery readings were removed, and marks old runs as "exempt, not checked" where the original script wrongly refused them.
3. Nothing about the list of 69 old runs is owed before the first scored campaign: new runs carry their own battery readings, and all 24 calibration recordings of 2026-09-27 pass on their own evidence. One consequence must be written into the merge description: after the merge the battery check refuses every one of the 57 stored 7B-model runs of 2026-07-29 until their own follow-up task rules on them. Not run by me: the full 477-test suite in one go (every test has passed on identical bytes; one full run is ordered after the merge).
