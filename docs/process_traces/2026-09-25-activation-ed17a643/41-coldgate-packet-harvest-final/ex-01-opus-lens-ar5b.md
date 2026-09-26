# Opus 5.5 contract lens: PR #423 (A-R5b v1.1), gate-ledger rows 1, 2, 6, 8

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), single foreground session, no subagents and no background tasks. Session ran 2026-09-25, about 17:15–17:30 PDT.
Worktree: `JouleWise-wt-ed17a643-ar5b-lens`, HEAD `ad7565a7`, base main `e9ed7a98`.
Ruled source: `origin/docs/2026-09-25-152c9255` @ `9fbc33be`, file `docs/process_traces/2026-09-25-activation-ed17a643/10-coldgate-packet-bfg/30-addendum/21-coldgate-fable-bfg-addendum-ruling.md`, sha256 `1047af22a32ba70544eabac0f85ee470957312a27204f79a538a39d9063b3add`, §5.8.

**Verdict: MERGE.** No findings are BLOCKERs. One MATERIAL finding (M1) is carried forward. It must be ruled before W1's harvest and implemented in BFG-D before any issuance. It does not require editing the text this PR installs.

## 0. Contamination disclosure

- **Loaded by the harness, not my choice:** global `~/.claude/CLAUDE.md`, project `CLAUDE.md`, and the auto-memory index `MEMORY.md`. The index is one-line pointers only; I opened no memory file. The harness also supplied the git status and five recent commit subjects.
- **Not opened:** `RUN_STATE.md`, `TASK_QUEUE.md`, any memory file, any council log, and `/tmp/ed17a643/ar5b/20-fable-final-pass-ar5b.md`. I saw the Fable final-pass file's name in a directory listing but did not read it.
  - One `git grep -c WALL-METER-GAIN-01` returned a match count for `TASK_QUEUE.md` among other files. I read no content from it.
- **Opened, read-only:**
  - The ruled addendum file in full.
  - Issues #421 and #422, including comments, via `gh`.
  - PR #423 metadata.
  - The registration file: Revision 1 lines 100–180, Revision 3 lines 514–560, and Revision 5 lines 600–646.
  - Code at `e9ed7a98`: `issue_calibration_acceptance_generation.py`, `validate_powermetrics_fiducial.py`, `night_gate.py`, `evidence_night.py`, `calibration_bracketing.py`, and `gen_derivation_night.py` (targeted line ranges and greps).
  - The BFG-D branch diff: issuer, writer, `battery_float.py`, and two docs.
- **Write-scope deviation (disclosed):** I created a scratch directory `/tmp/ed17a643/ar5b/lens-scratch/` for the byte comparison (four files). I deleted it before writing this report (`rm -r`; listing shown before removal).
  - I ran the canonical checkout's interpreter `../JouleWise/.venv/bin/python` for pytest and one in-memory Python probe, with `PYTHONDONTWRITEBYTECODE=1 -p no:cacheprovider`. `git status --porcelain` afterwards showed 0 lines.

## 1. Executed evidence

| # | What | Result |
|---|---|---|
| E1 | Unquote §5.8 (lines 154–170): `"> "` removed, `">"` becomes an empty line. `cmp` against the PR's added lines, minus the leading blank separator line. | **BYTE-IDENTICAL.** 17 lines, no stray non-quote lines. |
| E2 | `git diff --numstat e9ed7a98 ad7565a7` | Registration file 18 insertions, 0 deletions. `decision_log.md` 6 insertions, 0 deletions. No other file changed. |
| E3 | Sealed prefix: sha256 of the first 47804 bytes of the new file vs `git show e9ed7a98:<file>` | Both `497847c4adcae3d8a9bfef99148c602579cca2b4adec1893c1980e7b366fd191`. The base ends in `\n`. The new whole file is `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`, which equals the digest the magistrate posted on #422. |
| E4 | #422 scope: "only that file, and only that append", plus the decision-log entry | Matches E2 exactly. |
| E5 | `pytest` at HEAD (7 files: `test_acc_25g83_rev5`, `test_preregistration_chain_digest`, `test_docs_freshness`, `test_d078_reason_registry`, `test_identity_pins`, `test_claims_lint`, `test_whole_window_selection`) | **191 passed, 703 subtests passed.** |
| E6 | What the chain digest covers (Revision 3, lines 544–545) | sha256 of `scripts/night_chains/calibration_derivation_only.zsh` only. BFG-D does not touch `scripts/night_chains/` (diff stat). `ESTIMATOR_CODE_PATHS` (`calibration_bracketing.py:206-211`) does not include the writer. So the sentence "chain digest … estimator-code pins … unchanged" can stay true after BFG-D. |
| E7 | Writer anchors at `e9ed7a98` (`grep -n clock.stamp()` etc.) | `:2229` AFTER_CUSTODY_DIRECTORY_CREATION. The first `clock.stamp()` is `:2296` (`pre_spawn`) and the last is `:2453` (`post_parse`). `:2454` is `active_sampler = None`; `:2456` is `if logical_driver`. `git diff --stat c6814dd8 e9ed7a98 -- joulewise scripts tests` is empty, so the ruling's line numbers hold at main. BFG-D places the pre-observation right after `:2229` and the post-observation after the `with` block. |
| E8 | Battery code on main: `git grep -i 'battery_float\|AppleSmartBattery' e9ed7a98 -- joulewise scripts` | Only `joulewise/environment.py:370,513` (informational `ioreg -d 1`). **No A-R5b sentence is implemented at main.** All implementation sits on `origin/feat/2026-09-25-bfg-d`: 6 commits on `c6814dd8`, all labelled UNVERIFIED/WIP, round 3 pending. |
| E9 | Issuer at main: custody handling for members | `_read_member_evidence` (`:900-935`) and the native-frame read (`:1151-1156`) **refuse** issuance on unreadable or mismatched custody. There is no guard against re-preparation (grep `already\|re-prepar\|exists()`: none). The candidate carries each member's `b_fiducial_s` (`:1556`). |
| E10 | BFG-D `battery_float.validate_window`, loaded from `git show` into memory and run on a session whose custody path does not exist | `battery_float_evidence_missing ["evidence missing or unauthenticated: FileNotFoundError: …instrument_evidence.json"]`. In BFG-D's issuer (diff), the computed non-pass sessions are removed from `session_ids` *before* `_registration_observations` and member reads. |
| E11 | BFG-D issuer: which sessions get a computed verdict | `candidates = session_ids ∪ named_confounded ∪ {owners of valid, same-epoch, non-registry rows}`. `len(computed_confounded) > 1` refuses. |
| E12 | 6 h spacing enforcement: grep `21600\|6 h\|spacing` in the issuer, `gen_derivation_night.py`, `night_gate.py`, `evidence_night.py` | No hits. Spacing is procedural, both at main and on BFG-D. |
| E13 | Cited rulings present on main (`git cat-file -e`) | The three BATTERY-FLOAT-01 files cited by the new decision-log entry: **absent at `e9ed7a98`**, present on the docs branch. The two older ACCEPTANCE rulings cited by A-R5a-1 are present on main. The docs branch has no PR (`gh pr list --head`: `[]`) and does not contain `e9ed7a98`. |
| E14 | ID collision: `git grep A-R5b e9ed7a98` | No prior use. |

## 2. Findings

### M1: MATERIAL. A window that passed at harvest can later flip to `battery_float_evidence_missing`, which gives a route to drop a clean window after B has been seen.

- **Text.** "Window verdict" says the check runs before the cadence report, the dry run and any B read. "Either verdict is final" covers only the two non-pass verdicts; the text never says a *pass* at harvest is final. "Consequences" has the issuer compute the verdict "itself from raw bytes" at issuance time. Any missing or unauthenticated observation then makes the window `evidence_missing`: excluded, with one replacement allowed.
- **Failure scenario** (E9, E10, E11):
  1. W1 and W2 pass at harvest.
  2. `prepare-candidate` emits a candidate carrying all members' `b_fiducial_s`. There is no re-preparation guard.
  3. The caller dislikes the result, for example one B > 0.25 s refusing under `PLATEAU_INSET_S`, or `excursion_limited`.
  4. The caller deletes or alters one `raw/battery_float.post.ioreg` in a W2 slot. Honest custody loss does the same.
  5. The issuer now computes W2 = `evidence_missing`, requires `--battery-confounded-session-id W2`, and accepts W1 + W2′ after the one permitted replacement.
- **Why that breaks the rules.** It is an exclusion driven by B plus an outcome-driven top-up, which Revision 5 forbids ("No B-based exclusion or outcome-driven top-up is permitted"). It also falsifies the text's own justification for replacement: "decided … before any B value or disposition is read, so it cannot select on outcome."
- **The asymmetry is new.** At main, the same custody loss on a member **refuses** issuance (E9). Under A-R5b as implemented on BFG-D, it **excludes** the window, and the check runs before member reads (E10).
- **Why this does not hold #423.** The text supports a reading that closes the route. "Window verdict" anchors the verdict in time (at harvest, before the dry run), and nothing in the text forbids an extra issuer refusal.
- **Cure, no text edit needed:**
  - (a) The magistrate records a binding reading in the decision log: "the window verdict is the one computed at harvest; a harvest pass that the issuer cannot re-establish from raw bytes is a custody failure and refuses issuance; it is never an exclusion."
  - (b) BFG-D commits each session's harvest verdict durably, in the harvest record or pin commit, before the count-only dry run. The issuer refuses when its computed status disagrees with the recorded one.
  - (c) Add a test: harvest pass, then a deleted raw file, must refuse rather than exclude.
- **Timing.** (a) and (b) must be in force before W1's harvest dry run. (c) must be in place before any issuance.

### N1: NIT. The "at most one replacement per epoch" stop is not enforced for a failing window with zero valid rows.

- **Evidence:** E11. A failing session whose finalized rows are all ordinary-invalid is never in `candidates` unless the caller names it. The caller can leave it out, so `len(computed_confounded) > 1` never fires.
- **Scope.** No B value can be chosen through such a window, because it has none. So the effect is limited to evading the stop on a second replacement. The sentence "any further window with either verdict stops the epoch" is then held only by the harvest record.
- **Cure, BFG-D:** compute `validate_window` for every terminal derivation-kind session that has any finalized row in the target epoch, regardless of disposition. This stays inside the text ("sessions it is asked to consider" is a floor, not a ceiling).

### N2: NIT. Unclear whether a replacement's 6 h "neighbours" include the failed window it replaces, and no code enforces the spacing.

- "The replacement takes the replaced window's place … keeps … at least 6 h to its neighbours." One reading counts the failed W1 as W1′'s neighbour; another does not, since it has left the sequence. Arm, window and harvest can fit inside 6 h, so the question can arise in practice.
- There is no scientific way to cherry-pick through this, since the verdict does not depend on outcomes. Spacing is procedural (E12), as it already was for Revision 5.
- **Cure:** one line in the magistrate's harvest procedure. Recommended: measure ≥ 6 h from the failed window as well, which is conservative.

### N3: NIT. The decision-log record: provenance and wording (lines 12215–12217).

- (a) The three cited BATTERY-FLOAT-01 paths do not exist on main after merge (E13). A-R5a-1's citations do resolve on main. **Cure:** land the docs branch before the W1 notice cites this entry, or add "(branch `docs/2026-09-25-152c9255`)". #422 itself names the branch.
- (b) "amended by the paired Opus contract refuter" credits a refuter with amending power. The addendum treats refuter output as "argument" (§1), and it was the addendum that affirmed and amended. **Suggested wording:** "with findings of the paired Opus contract refuter affirmed by the cold Fable addendum."
- (c) "The W1 notice and arm material pin the whole-file digest after the append" states a future obligation as present fact. "must pin" is accurate.
- None of these overclaims the science. The summary of A-R5b's content in the record is accurate against §5.8, sentence by sentence.

### N4: NIT (information). Between #423's merge and BFG-D's merge, main carries a registration it cannot enforce.

- E8: no gate at main implements the predicate, the per-slot observations, the verdict or the issuer rules. Ruling §5.7 orders BFG-D before W1, and procedural gate C9 covers the interval. Nothing mechanical stops a W1 from arming against the new digest before BFG-D.
- **Cure:** keep §5.7's order as a stated condition of the W1 arm checklist. No code change is needed in #423.

## 3. Checked, no finding

- **Byte fidelity:** E1 and E3. The appended block is §5.8 byte for byte. Not one sealed byte moved. The separator is a single blank line.
- **Conflicts with the sealed Revision 5 and Revision 1:**
  - **Membership:** "None of its slots is a member" is a later, specific rule. Revision 5's "Every valid resolved member is retained" therefore does not reach these slots.
  - **Exclusions:** Revision 1's "ONLY exclusion mechanism" is expressly supplemented ("adds one … exclusion"). Revision 1's "every exclusion is recorded with its named mechanism and its ledger row retained" is met at window level (retained; mechanism named).
  - **Stops:** the verdict runs before the 150 ms stop and the 6-of-12 stop. The replacement faces those stops afresh. The issuer's W1 ≥ 6 check and W3 check run on the post-exclusion `session_ids` (BFG-D), so W1′ becomes `session_ids[0]`.
  - **W3 trigger:** failing windows do not count toward it.
  - **Top-ups:** "No other top-up" matches Revision 5's ban on B-based top-ups, apart from M1.
  - **Blindness:** B values stay unread until issuance is decided.
  - **Harvest order:** unambiguous: verdict, then cadence, then dry run.
- **Admission and D-182:** a zero-capture refusal is not a window. It does not use up the one replacement, and cannot select on outcome.
- **Implementability:** every per-slot and admission sentence maps to a site in ruling §5.3/§5.5, and the ruled line anchors exist at `e9ed7a98` (E7). There is one line of drift: `evidence_night` publish is at `:1777`, not `:1776`, and the text anchor still identifies it.
  - Sentences no implementation plan covers are all procedural: the 6 h spacing (N2); "the harvest record … and the next arm notice name the window …" (BFG-D's runbook and handback diffs add only the refusal-code row); the paper-level limitation disclosure; and "diagnostics afterwards", which is a permission. None needs code in #423.
- **Overbuild:** none. There are two files, and the decision-log entry is three short paragraphs that mirror A-R5a-1's form.

## 4. Tier summary

| ID | Tier | Holds #423? | Must land by |
|---|---|---|---|
| M1 | MATERIAL | No (text admits the cure) | Reading + recorded harvest verdict before W1 harvest; refusing issuer and test before any issuance |
| N1 | NIT | No | BFG-D |
| N2 | NIT | No | Harvest procedure before any replacement |
| N3 | NIT | No | Before the W1 notice cites the entry |
| N4 | NIT | No | W1 arm checklist |

**Verdict: MERGE.**
