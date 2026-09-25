# Cold Fable final pass — SEAL-R5-01 (gate-ledger row 7)

**Contamination disclosure.** Besides the charge, this session's harness loaded three things automatically before I read anything: the global `~/.claude/CLAUDE.md` (writing standard, skill list), the project `CLAUDE.md` (bridge policy), and the one-line index `MEMORY.md` of the memory directory (titles and hooks only; one hook reads "next = Rev5 seal PR then W1 arm"). I opened no memory file, no `RUN_STATE.md`, no `TASK_QUEUE.md`, and no activation record. Within the charge I read A-R5a-1 in `docs/decision_log.md`; a grep listed `docs/process_traces/2026-09-25-activation-152c9255/27-coldgate-packet-prr-r3/20-coldgate-fable-prr-r3-ruling.md` as containing the template digests, but I did not open it. Everything else is the repository at 23dd9909 and the commands below.

Judge: Claude Fable 5.1, single foreground session, no background tasks or subagents. Working tree: `/Users/edr/code/JouleWise-wt-817355d2-finalpass`, detached at `23dd9909e1f34610681b8616f573dee1a944cc3a`, clean.

## Verdict: MERGE

No BLOCKER. No finding requires a change to the diff. One MATERIAL finding (F1) is pre-existing in PR-L's design, not introduced by the seal, and is discharged by a check the W1 arm procedure must run by hand until code does it. Two NITs.

| ID | Class | Finding |
|----|-------|---------|
| F1 | MATERIAL (pre-existing, not in this diff) | No code consumes the registered template digests; the working-tree template that the installer renders is tied to the registration only through the plan's `repo_head` pin, and the driver checkout is not checked for uncommitted edits. See S4. |
| F2 | NIT | `tests/test_acc_25g83_rev5.py:96` string-replaces the unsealed header, which is now a no-op on the sealed file. The test is not vacuous; see S3. |
| F3 | NIT | The next issuance must pass the NEW file digest `497847c4adcae3d8a9bfef99148c602579cca2b4adec1893c1980e7b366fd191` as `--preregistration-sha256`; nothing in the repo records it yet (by design: the arm material carries it). Recorded here so the arm notice does not take the old digest `977e3c9b...` by mistake. |

## S1. Values — PASS

```
$ gh pr view 412 --json mergeCommit,title,mergedAt,baseRefName
{"baseRefName":"main","mergeCommit":{"oid":"9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87"},
 "mergedAt":"2026-09-25T20:44:15Z",
 "title":"PR-L: launch-context cure (ProcessType=Interactive, installer refusal, probe cadence phase, R16 custody root)"}

$ git log -1 --format='%H %P %s' 9b750bf3
9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87 4e48c159... dc210094... Merge pull request #412 from mpmdw/feat/2026-09-25-acc-launch-context

$ git show 9b750bf3:configs/launchd/com.joulewise.night.plist.template | shasum -a 256
e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8  -
$ git show 9b750bf3:configs/launchd/com.joulewise.night-probe.plist.template | shasum -a 256
1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd  -
```

Sealed sentence at 23dd9909 (word diff of the only content change):

```
template at commit [-<PR-L-MERGE-SHA>,-]{+9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87,+}
template digests [-<TEMPLATE-SHA256:night>-]{+e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8+}
and [-<TEMPLATE-SHA256:probe>.-]{+1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd.+}
```

Commit matches `mergeCommit` exactly (40 hex). Night digest is in the first slot, probe digest in the second, matching the sentence that follows ("The first digest is the sha256 of ...night.plist.template ... and the second of ...night-probe.plist.template"). Both templates carry `<key>ProcessType</key><string>Interactive</string>` at 9b750bf3 (night line 7, probe line 6). Templates are byte-identical at 23dd9909 (`git diff --stat 9b750bf3 23dd9909 -- configs/launchd/` is empty; `shasum` of the working-tree files reproduces both digests). `git merge-base --is-ancestor 9b750bf3 23dd9909` succeeds.

## S2. Procedure conformance — PASS

```
$ git diff c6814dd8 23dd9909 --stat
 configs/calibration/preregistration_d079_epoch_25g83_rev1.md | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```

Exactly two lines changed, both in the prescribed places:

- Header: `# Revision 5 (2026-09-25; sealing pending PR-L pins)` → `# Revision 5 (2026-09-25; sealed 2026-09-25 at PR-L merge 9b750bf3)`. Form matches A-R5a-1 and the in-file instruction: "sealed <YYYY-MM-DD> at PR-L merge <first 8 hex of the commit>". Date is correct: merge at 2026-09-25 13:44 PDT, seal commit authored 2026-09-25 13:55 PDT.
- Operating-condition sentence: three literals replaced, no backticks added around the values, trailing punctuation preserved (`,` after the commit, `.` after the probe digest), no other characters touched.

```
$ grep -c -E '<PR-L-MERGE[-]SHA>|<TEMPLATE[-]SHA256:' configs/calibration/preregistration_d079_epoch_25g83_rev1.md
0     (grep exit 1, as the test in S3 also expects)
```

The seal-procedure prose itself (still describing the placeholders in backticks inside the grep expression) is unchanged; that is correct, since the procedure text is part of the registration and the grep pattern text `<PR-L-MERGE[-]SHA>` with the bracketed hyphen does not match itself. The STATUS paragraph at line 602 still says "no W1 capture may be armed until the literal launch-context placeholders below are replaced"; that condition is now satisfied and the sentence remains true as a record. Nothing else in the file mentions "sealing pending".

## S3. Consumers — PASS

Issuer block (`scripts/issue_calibration_acceptance_generation.py:1281-1290`):

```python
if "# Revision 5 (" not in preregistration_text: raise PrepareRefusal(...)
if re.search(r"<PR-L-MERGE-SHA>|<TEMPLATE-SHA256:[^>]+>", preregistration_text): raise ... "unsealed placeholders"
if not re.search(r"template at commit [0-9a-f]{40}\b", ...) or not re.search(r"template digests [0-9a-f]{64} and [0-9a-f]{64}\b", ...): raise ... "malformed"
```

Against the sealed text: `# Revision 5 (` present; placeholder regex has no match; `template at commit 9b750bf3...c87,` matches the 40-hex pattern with `\b` satisfied by the comma; `template digests e62a...5c8 and 1570...1fd.` matches the 64/64 pattern with `\b` satisfied by the period. The issuer accepts.

Tests (all four modules requested; counts confirm both modules ran in each invocation):

```
$ python3 -m unittest tests.test_acc_25g83_rev5 tests.test_preregistration_chain_digest
Ran 17 tests in 10.698s   OK        (9 + 8 tests by grep -c 'def test_')
$ python3 -m unittest tests.test_issue_calibration_acceptance_generation tests.test_night_gate
Ran 217 tests in 65.626s  OK        (114 + 103)
```

**Digest pins.** Old file sha256 `977e3c9bac6de2fb4c8b462701a17b5b6d280240572d1e708997a19deb76d2f4`, new `497847c4adcae3d8a9bfef99148c602579cca2b4adec1893c1980e7b366fd191`. A repo-wide grep (excluding `.git`) finds neither digest anywhere. `night_gate.RULED_REGISTRATIONS` pins other protocol files (D-166, QPE-01), not this one. `tests/test_preregistration_chain_digest.py` reads the "Chain digest in force (revision 3)" line by regex and compares it to the tracked zsh chain; the seal does not touch that line. The issuer receives the file digest only via `--preregistration-sha256` at issuance time. So no test or production code pins this file's bytes in a way the seal breaks (F3 records the new digest for the arm material).

**Vacuity check (F2).** `tests/test_acc_25g83_rev5.py:30-41` builds every fixture from the live file by substituting the launch sentence with `LAUNCH_CONDITION = re.compile(r"template at commit \S+, template digests \S+ and \S+\.")`, which matches the sealed hex values as well as the old placeholders, and it asserts exactly one match. The a/b/c fixture and the `not-a-commit` fixture therefore still exercise accept and refuse paths against text derived from the sealed registration; the "unsealed placeholders" refusal is exercised by `test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids`, which injects the placeholders itself. The only no-op is the header `.replace(...)` at lines 95-98, which was already cosmetic: the issuer checks only that `# Revision 5 (` is present, never the parenthetical. Science consequence: none. Optional cleanup: drop the replace or assert `"sealed 2026-09-25 at PR-L merge 9b750bf3" in PREREG.read_text()` so the test pins the seal form. Not required for merge.

## S4. Science — one MATERIAL gap, pre-existing, not caused by the seal (F1)

What the seal describes: captures launched by launchd agents rendered from templates whose bytes at 9b750bf3 hash to the two registered digests, with `ProcessType=Interactive`.

What the installer actually does (`joulewise/night_agent_install.py`):

- Reads the night template from the **driver checkout working tree**, `repo / "configs/launchd/com.joulewise.night.plist.template"` (line 1170), and the probe template likewise (line 1031). It never reads them at a commit and never computes or compares a template sha256.
- Renders night and dead-man from the same night template (lines 636-660), enforces `ProcessType == Interactive` on every rendered payload (lines 588, 656, 1041), and records `rendered_plist_sha256` per label in the arm evidence and probe receipt (lines 590-591, 1148-1151), re-checking those digests at install (line 493). This matches the registration's own description of the per-window record.
- Pins `plan.repo_head` to the driver checkout HEAD and `plan.measurement_head` to the measurement checkout HEAD (lines 1187-1195); refuses on mismatch.
- `night_gate` C5 (lines 1314-1345) refuses if the **measurement** checkout has tracked edits or untracked files. No equivalent porcelain check exists for the **driver** checkout (`grep -n porcelain joulewise/night_agent_install.py` returns only the comment at 665).

The gap: the registered template digests are a text-only pin. Nothing at arm time verifies `git show <repo_head>:<template> | shasum -a 256` equals the registered value, and nothing verifies the driver checkout's template file is clean. Two ways a W1 window could run under a launch context other than the registered one without any refusal:

1. A future commit on main changes either template; a plan authored at that HEAD passes the `repo_head` check, renders the new template, and the registration then misdescribes the launch context. Today this cannot happen (templates are unchanged from 9b750bf3 through 23dd9909), but the pin does not defend itself.
2. An uncommitted edit to the template in the driver checkout (when the driver checkout is not the same path as the measurement checkout that C5 inspects) renders a plist from bytes that match no commit. The rendered digest is recorded, so an auditor could detect it post hoc only by re-rendering from the registered template with the same plan values, which is laborious and not currently scripted.

Neither path is opened or widened by this diff; both are properties of PR-L as ratified under A-R5a-1, which chose template digests over rendered-plist digests precisely because the rendered ones are plan-specific. The seal is the correct literal act. The scientific defence until code closes it is procedural: before W1's arm notice, record in the arm material (a) `plan.repo_head`, (b) `git show <repo_head>:configs/launchd/com.joulewise.night.plist.template | shasum -a 256` and the probe equivalent, both equal to the registered digests, and (c) `git -C <driver checkout> status --porcelain -- configs/launchd/` empty. A one-line follow-up in the installer (compute the two template digests from the working tree at `validate_install` and refuse if the plan or registration pins differ) would make it mechanical; I recommend it as a separate light-gate change, not as a condition on this merge.

Ancillary observation, not a finding: the registration says the night template is "shared by the night and dead-man labels". Confirmed in code: the dead-man render is the same `self.template` with the Month and Day calendar keys stripped (lines 645-647), so its rendered digest differs from the night label's but its template digest is the registered night digest.

## What was NOT EXECUTED

Nothing in the charge was skipped. I did not run full test discovery, as instructed. I did not open the PRR-R3 cold-gate ruling that a grep showed also contains the two template digests.
