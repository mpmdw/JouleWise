# Cold Fable final pass (gate-ledger row 7) — PR #423, A-R5b v1.1 append

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, single foreground session, worktree `JouleWise-wt-ed17a643-ar5b-fp` at HEAD `ad7565a7a9dae213c62ab701df164d672915fdda` = PR #423 head (`gh pr view 423`: OPEN, base `main`, head `feat/2026-09-25-a-r5b@ad7565a7`). Base `e9ed7a98` (merge of #418). Session 2026-09-25 ≈17:15–17:25 PDT. No background tasks, subagents, Codex calls, `sudo`, `launchctl`, `powermetrics`, installer or model inference. Only this file was written. Scratch copies of the two registration versions and the ruling were placed under `/tmp` (prefix `ed17a643_`) for byte comparison.

## 0. Contamination disclosure

Loaded by the harness without my choosing: the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers, including loop-context titles and checkpoint names). A system reminder supplied the git status and five recent commit subjects. I opened no memory file, no `RUN_STATE.md`, no `TASK_QUEUE.md`, no council log, no run report, and no `docs/process_traces` file other than the ones named below.

Loaded by me, all read-only: at HEAD, `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (headings; lines 150–200 Revision 1 Membership/Exclusions/Stopping/Blindness; lines 600–665 Revision 5 in full plus the amendment), `docs/decision_log.md` (lines 12196–12218; D-182 heading line 11959), `tests/test_preregistration_chain_digest.py` (grep), `joulewise/night_gate.py` (grep for `"C3"`), and greps of `joulewise`, `scripts`, `tests`, `docs`, `configs` for the identifiers the amendment relies on. From `origin/docs/2026-09-25-152c9255` via `git show`: the addendum ruling `…/30-addendum/21-coldgate-fable-bfg-addendum-ruling.md` (§0–§2, §5.3, §5.7, §5.8, §6, §7) and the file list of the packet directory. From GitHub: issues #422 (body and one comment) and #421 (body), PR #423 (metadata, files, body). Tests run: the three named modules.

## 1. Verification before the merits

| # | Check | Executed evidence | Result |
|---|---|---|---|
| V1 | Diff scope | `git diff --stat e9ed7a98 HEAD`: exactly two files, 24 insertions, 0 deletions: the registration (+18) and `docs/decision_log.md` (+6). `git status` clean. | PASS |
| V2 | PR head = merge candidate | `gh pr view 423 --json headRefOid` = `ad7565a7a9dae…`; `git rev-parse HEAD` identical. Files listed by GitHub = the same two. | PASS |
| V3 | Ed's approval | Issue #422 (author `mpmdw`, 2026-09-25T22:17Z) approves appending "exactly the §5.8 text" of the named addendum ruling on branch `docs/2026-09-25-152c9255` below sealed Revision 5, **after PR #418 merges**, plus the decision-log entry; scope "only that file, and only that append". #418 merged as `e9ed7a98`, which is this PR's base. | PASS |

## 2. The six charged checks

### (1) Prefix byte-identity and appended block = §5.8 — PASS

- `git show e9ed7a98:<reg>` = 47 804 bytes, sha256 `497847c4adcae3d8a9bfef99148c602579cca2b4adec1893c1980e7b366fd191`. `git show HEAD:<reg>` = 53 391 bytes, sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`.
- `head -c 47804 <HEAD file> | cmp - <base file>` → no output (identical). The base file's last byte is `\n` (`od -c`).
- Appended tail (bytes 47 805–53 391, 5 587 bytes) versus §5.8 of the ruling (lines 154–170 of the addendum ruling, every line beginning `>`; `sed 's/^> \{0,1\}//'` strips the marker; 5 586 bytes): `printf '\n' | cat - <stripped 5.8> | cmp - <appended>` → no output. **The appended block is one blank separator line followed by the §5.8 text, byte for byte** (the Unicode em dash, `≤`, `−` and `–` all carried; `cat -v` shows the same byte sequences on both sides).
- The whole-file digest `81b65f08…` equals the digest the magistrate posted on #422 and in the PR body, so the W1 notice pin named there refers to this exact file.

### (2) No sealed Revision 5 word changed — PASS

Follows from (1): the first 47 804 bytes are byte-identical to the merged seal, and the diff shows zero deletions. Independently: `grep -c '^# Revision 5 (2026-09-25; sealed 2026-09-25 at PR-L merge 9b750bf3)$'` = 1; seal placeholder grep (`<PR-L-MERGE[-]SHA>|<TEMPLATE[-]SHA256:`) = 0; the A-R5b heading occurs exactly once; Revision 3's chain-digest line is untouched (the chain-digest test below passes).

### (3) Consistency with Revision 5 and Revision 1; W1 runnable and unambiguous — PASS, with one carry note (M1)

Read against Revision 5 §Sample, stops and blindness (lines 610–614) and Revision 1 Membership/Exclusions/Stopping/Blindness (lines 156–186):

- **"No B-based exclusion or outcome-driven top-up is permitted" (Rev 5)** vs the amendment's exclusion and replacement. Not a contradiction: the amendment's verdict is computed "from its raw bytes alone" before the cadence report, before the dry run and before any B value is read; the replacement is licensed only by that verdict. Rev 1's Exclusions paragraph already frames exclusions as "mechanism-named, outcome-independent, decided before capture", and the amendment's opening sentence claims exactly that class. Rev 1's "the ONLY exclusion mechanism registered at this step" is scoped to Revision 1's step; a later labelled amendment adding a mechanism is the ordinary revision path this file already uses (Revisions 2, 3, 5 each amend earlier text).
- **"Every valid resolved member is retained" (Rev 5) and Rev 1 Membership ("every observation … whose ledger disposition is valid and whose STORED anchor-v3 outcome … resolves")** vs "None of its slots is a member". The amendment governs for confounded windows because it is the later text and says so ("the rules that follow from it"); Rev 1's rule that "a valid same-epoch observation outside this registration refuses issuance rather than being absorbed" (the A-7 path) is reconciled explicitly: the issuer computes the confounded set itself, the operator names it separately, and issuance refuses unless the sets are equal. So a confounded window's valid rows neither absorb silently nor trip A-7 by accident. Unambiguous.
- **Stops.** Rev 5's two W1 stops (median native frame > 150 ms; fewer than 6 valid of 12) are named by the amendment and suspended only for a window with a verdict; the replacement "faces that window's stops afresh". The 6 h spacing is carried. W3's trigger ("fewer than 12 valid" after W2) is named. The n ≥ 12 floor is unchanged. Coherent.
- **Blindness.** Rev 1 says no member value is examined before the terminal session; the amendment reads only raw `ioreg` bytes, never B. Coherent, and it strengthens the fence (B values of a confounded window are "not read before issuance is decided").
- **Admission at t0 "inside the night gate's C3 row".** `joulewise/night_gate.py:301` defines `_CONDITION_IDS = ("C1", …, "C5")` and `:1355` appends to `rows["C3"].evidence`; the row exists. The refusal codes `night_refused_battery_float` and the file names `raw/battery_float.{pre,post}.ioreg` do not exist in code at HEAD (`git grep night_refused_` over `joulewise` lists eight codes, none for battery; `battery_float` appears only in the registration). `night_probe_error`, `window_exhausted`, `instrument_evidence.json`, `D-182` (decision log line 11959) and `addendum A-7` all resolve.
- **W1 runnability (M1, carry note, not a contradiction).** Once this merges, every derivation slot must carry pre/post observations, or the window is `battery_float_evidence_missing` and consumes the single replacement. The code that writes them is BFG-D, not yet on main. The registration text does not itself say "BFG-D before W1"; the decision-log record does ("PR BFG-D (derivation windows; required before W1)"), as does the ruling's §5.7 item 2. This is the intended ordering, and W1 is runnable and unambiguous once BFG-D lands. The arm notice must not issue before BFG-D is on main, or W1 is guaranteed confounded by construction.

### (4) Decision-log record accurate to its sources; no authority claimed that it lacks — PASS, with one MATERIAL (M2) and one NIT (N1)

Checked clause by clause against §5.8, §5.3, §5.7, #421 and #422:

- Predicate at arm, publication and t0; per-slot observations outside the clock-anchor stamps; whole-window verdict from raw bytes before any B value; exclusion with disclosure; at most one replacement per epoch: each matches the amendment's Admission, Per-slot evidence, Window verdict, Consequences and Replacement paragraphs.
- "appended below the sealed Revision 5 text, and no sealed word is edited": verified in (1)–(2).
- "The W1 notice and arm material pin the whole-file digest after the append": matches §5.7 item 3 and #422's binding text.
- "Directive: Ed's issue #421 (the battery-float gate for every window; anything germane to the verity of the science is mandatory)": matches #421's title and §2.
- "Approval to install: Ed's issue #422": matches.
- "Implementation: lane BATTERY-FLOAT-GATE-01, PR BFG-D (derivation windows; required before W1) and PR BFG-S (every other window kind; required before any such window)": matches §5.3 and §5.7; #421 §1 names BATTERY-FLOAT-GATE-01 as the code-level lane.
- Authority: the record is headed as an ACCEPTANCE-25G83-02 amendment in the same form as A-R5a-1 and claims only the cold ruling, the refuter, the addendum and Ed's two issues. It does not claim council ratification, and none is asserted. No authority beyond what exists is claimed.
- **M2 (MATERIAL, carry).** The three cited ruling paths under `docs/process_traces/2026-09-25-activation-ed17a643/10-coldgate-packet-bfg/` exist only on `origin/docs/2026-09-25-152c9255`; `git cat-file -e` at `e9ed7a98` and at HEAD returns NO for all three. By contrast, the A-R5a-1 record's two cited paths resolve on main. After this PR merges, a reader of main cannot open the text this amendment claims to copy until the docs branch lands. Not a blocker (the decision log is bookkeeping, not the registration, and the docs branch is the activation's normal landing vehicle), but the docs branch (at least that packet directory) must merge to main before the W1 arm notice cites this record, so the authority chain is verifiable from main. Alternative cure if the docs branch is delayed: one added clause naming the branch, in the decision log only (the registration needs no change, and #422 forbids any other registration edit).
- **N1 (NIT).** "amended by the paired Opus contract refuter (`21-opus-contract-refuter.md`) and the cold Fable addendum" reads as if the refuter amended the ruling. Per the addendum's §3 and §6, the refuter raised findings; the cold Fable addendum affirmed them and issued the amended texts. The parenthetical "§5.8, the installed text" removes any doubt about which text governs, so no reader can install the wrong text. Wording only.

### (5) Tests — PASS

```
$ python3 -m unittest tests.test_acc_25g83_rev5 tests.test_preregistration_chain_digest tests.test_docs_freshness
................................................
----------------------------------------------------------------------
Ran 48 tests in 10.194s

OK
```

The chain-digest test binds the Revision 3 "Chain digest in force" line to the tracked chain script and requires the sealed digest to remain unique; the append changed neither. `test_acc_25g83_rev5` reads the registration file and passes with the new heading present.

### (6) Anything a merge should not carry — nothing found

- No code, config, test or generated file changes; no `settings.local.json` in the diff (it is untracked and per-machine, as #422 says; its removal is #422's own follow-up, not this PR's).
- No stray bytes: the appended block starts with exactly one blank separator line and ends with the ruling's trailing newline. No trailing whitespace introduced (`cat -v` shows none).
- The old whole-file digest `497847c4…` appears only in the #418 seal-review traces, where it is historically correct ("new sha256" at that seal). Nothing on main pins it as the digest in force; Revision 5's own STATUS text says the digest pinned in the arm material is "this whole text's digest", which after the append is `81b65f08…`, as §5.7 item 3 and #422 require.
- The PR body's gate-ledger rows all read NOT-RUN with a note that Codex returned 401 and the gate runs on an Opus contract lens plus this cold pass. That is the truthful state at PR creation; the magistrate fills the rows before merge. Not a finding against the diff.

## 3. Findings, tiered

| ID | Tier | Finding | Action |
|---|---|---|---|
| M1 | MATERIAL (carry; ordering, not text) | With A-R5b on main, any derivation window armed before BFG-D lands is `battery_float_evidence_missing` by construction and would consume the epoch's single replacement. The registration text does not state the ordering; the decision-log record and ruling §5.7 do. | No change to this PR. The W1 arm notice must not issue until BFG-D is on main; the magistrate's arm checklist should carry this as an explicit precondition. |
| M2 | MATERIAL (carry) | The decision-log record's three cited ruling paths are absent from main (present only on `origin/docs/2026-09-25-152c9255`). | Merge that docs branch (or its packet directory) to main before the W1 notice cites this record. If it cannot land in time, add the branch name to the decision-log record only. |
| N1 | NIT | "amended by the paired Opus contract refuter" misattributes the amending act; the refuter raised findings, the addendum amended. | Optional wording fix at the next bookkeeping touch of the decision log. |

No BLOCKER.

## 4. Ruling

**MERGE** `ad7565a7`, as is. The registration prefix is byte-identical to the sealed Revision 5 on main; the appended block is the ruled §5.8 text byte for byte after one blank separator line; the whole-file digest is `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`, matching the digest the magistrate posted on #422 for the W1 notice pin; the amendment coheres with Revision 5's stops, blindness and no-outcome-driven-top-up rule and with Revision 1's membership and A-7 refusal path; the decision-log record is accurate to its sources and claims no authority it lacks; the three named test modules pass (48 OK); Ed's approval on #422 is followed to its letter (after #418, only that file, only that append, plus the log entry). Carry M1 and M2 as arm-notice preconditions; N1 is optional.

## 5. Plain summary for Ed (5 lines)

1. The battery rule you approved on #422 is in the registration file exactly as the cold ruling wrote it, and nothing in the sealed Revision 5 above it changed by a single byte.
2. The file's new fingerprint is the one the magistrate already posted; the W1 notice will pin that fingerprint.
3. The rule does not fight the sealed text: it excludes a window from instrument readings taken before any result is looked at, and allows one replacement window per epoch.
4. Two things must happen before W1 arms: the code that takes the per-slot battery readings (BFG-D) must land on main, and the ruling documents this record points at must land on main too.
5. Verdict: merge.
