# SEAL-R5-01 — Opus 5.5 CONTRACT lens (gate rows 6/8/10)

Reviewer: Opus 5.5, fresh non-author subagent, contract lens. Checkout: `/Users/edr/code/JouleWise-wt-817355d2-solens`, HEAD `23dd9909e1f34610681b8616f573dee1a944cc3a` (detached), working tree clean before and after (`git status --short` empty both times). Read-only; the only file written is this report. No background tasks.

**Verdict: MERGE.** No BLOCKER. One MATERIAL follow-up that predates this diff and is not caused by it (the registered template digests are not checked at arm time; S4). Two NITs.

---

## S1. Values — PASS

```
$ gh pr view 412 --json mergeCommit,state,mergedAt,baseRefName
{"baseRefName":"main","mergeCommit":{"oid":"9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87"},"mergedAt":"2026-09-25T20:44:15Z","state":"MERGED"}

$ for f in com.joulewise.night.plist.template com.joulewise.night-probe.plist.template; do
    git show 9b750bf3:configs/launchd/$f | shasum -a 256; git show 23dd9909:configs/launchd/$f | shasum -a 256; shasum -a 256 < configs/launchd/$f; done
com.joulewise.night.plist.template:       e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8  (at 9b750bf3, at 23dd9909, worktree: identical)
com.joulewise.night-probe.plist.template: 1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd  (at 9b750bf3, at 23dd9909, worktree: identical)

$ git log --oneline 9b750bf3..23dd9909 -- configs/launchd/     -> (empty: no template change since PR-L)
$ git merge-base --is-ancestor 9b750bf3 23dd9909               -> 9b750bf3 is ancestor of 23dd9909
$ git log -1 --format='%H %P %s' 9b750bf3
9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87 4e48c159... dc210094... Merge pull request #412 from mpmdw/feat/2026-09-25-acc-launch-context
```

The sealed sentence reads `template at commit 9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87, template digests e62a461b…e5c8 and 1570b745…c1fd`. The commit is the full 40-hex SHA. The night digest comes first and the probe digest second, which matches the text's own definition ("The first digest is the sha256 of …night.plist.template … and the second of …night-probe.plist.template").

## S2. Procedure conformance — PASS (byte-exact)

`git diff --stat c6814dd8 23dd9909` shows one file changed, 2 insertions and 2 deletions: the header line (600) and the operating-condition line (608).

I rebuilt the expected sealed file from the parent by doing exactly the prescribed substitutions and nothing else, then compared bytes:

```
old counts: <PR-L-MERGE-SHA>=1 <TEMPLATE-SHA256:night>=1 <TEMPLATE-SHA256:probe>=1 'sealing pending PR-L pins'=2
old header occurrences of '(2026-09-25; sealing pending PR-L pins)': 1
expected == actual: True
old sha256: 977e3c9bac6de2fb4c8b462701a17b5b6d280240572d1e708997a19deb76d2f4
new sha256: 497847c4adcae3d8a9bfef99148c602579cca2b4adec1893c1980e7b366fd191
new still contains 'sealing pending PR-L pins': 1   (the quoted instruction inside the procedure sentence; correct to keep)
backtick-wrapped sealed values? False False False
CRLF in new: False  trailing newline: True

$ grep -c -E '<PR-L-MERGE[-]SHA>|<TEMPLATE[-]SHA256:' configs/calibration/preregistration_d079_epoch_25g83_rev1.md
0      (exit 1)
$ git show c6814dd8:<same file> | grep -c -E '…same pattern…'
1      (parent: all three placeholders were on one line)
```

- The literal tokens were replaced, with no backticks: yes.
- The header parenthetical follows the prescribed form "sealed <YYYY-MM-DD> at PR-L merge <first 8 hex>": it reads `sealed 2026-09-25 at PR-L merge 9b750bf3`. The first 8 hex match the commit. The date is correct: PR-L merged at 13:44 PDT on 2026-09-25 and the seal was committed at 13:55 PDT the same day.
- Nothing else changed. The STATUS paragraph and the procedure sentence (which still quotes the old parenthetical and `<that commit>`/`<template path>`/`<YYYY-MM-DD>` as instructions) are left as written. That is correct: the procedure says to replace "these three literals" and the parenthetical, and nothing more. None of the remaining angle-bracket instruction tokens match the placeholder grep.
- Amendment A-R5a-1 in `docs/decision_log.md` (line 12207) pins "the commit at which PR #412 (PR-L) landed on main and the sha256 of the two launchd templates … at that commit". It also says rendered-plist digests stay out of the text. The sealed sentence matches this: template digests only, no rendered digests. The header-parenthetical form is set by the prereg procedure sentence, not by the decision-log entry, and the diff follows it.
- Overbuilt: nothing. Missing from this diff: nothing. The remaining Revision 5 precondition, "this whole text's digest is pinned in the arm material", is a later arm step and is correctly not part of this diff. **The digest the arm notice must carry is `497847c4adcae3d8a9bfef99148c602579cca2b4adec1893c1980e7b366fd191`.**

## S3. Consumers — PASS

**The issuer** (`scripts/issue_calibration_acceptance_generation.py` lines 1281–1289). I ran its exact regexes against the sealed file:

```
'# Revision 5 (' present: True
placeholder match: None
commit matches: ['template at commit 9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87']
digest matches: ['template digests e62a461b…e5c8 and 1570b745…c1fd']
```
The issuer accepts the text: the Revision 5 guard raises neither "unsealed placeholders" nor "malformed".

**Tests:**
```
$ python3 -m unittest tests.test_acc_25g83_rev5 tests.test_preregistration_chain_digest
Ran 17 tests in 11.070s   OK
$ python3 -m unittest tests.test_issue_calibration_acceptance_generation tests.test_night_gate
Ran 217 tests in 63.817s  OK
```

**Byte and digest pins.** Neither the old digest (`977e3c9b…`) nor the new one (`497847c4…`) appears anywhere in the tree outside `.git`. The sealed values (`9b750bf3`, `e62a461b9f`, `1570b745870`) appear only in the registration file itself. Other consumers of the file:
- `tests/test_preregistration_chain_digest.py` reads the chain-digest and timing sentences, which this diff does not touch.
- `tests/test_night_gate.py` lines 286 and 327 check path usage and that C1 refuses the scientific prereg. Neither depends on the header or the operating condition.
- `docs/process/state_kernel.json` holds prose references to line 143 only.

No consumer breaks.

**Vacuity.**
- `tests/test_acc_25g83_rev5.py` lines 95–98 run `.replace("# Revision 5 (2026-09-25; sealing pending PR-L pins)", "… sealed … aaaaaaaa)")`. On the sealed file this replacement now does nothing (confirmed: `header replace no-op: True`). The fixture header therefore reads `9b750bf3` while its fixture commit is `"a"*40`. Consequence: none for correctness. The issuer never reads the header parenthetical, and no code checks that the header and the commit agree. The test's real assertions (grep count 0 with exit 1, sealed text accepted, malformed text refused) still exercise the live pin sentence. → **NIT**, no science impact.
- The fixtures that swap in the pin sentence (`registration_with_launch_pins`, via `LAUNCH_CONDITION`) still find exactly one match in the sealed file (`LAUNCH_CONDITION count: 1`). So the unsealed-refusal, malformed-refusal and superseded-refusal cases in `test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids` are still built from the real file and still run their checks. None of them became vacuous.

## S4. Science — seal correct; one pre-existing enforcement gap

What the seal records matches the truth. The templates at `9b750bf3` hash to the sealed values, and they are byte-identical at `23dd9909`.

**The gap (MATERIAL, pre-existing, not introduced by this diff).** No code compares the templates the installer actually uses against the registered digests:
- `joulewise/night_agent_install.py` line 1170 (night/dead-man) and line 1031 (probe) read templates from the installer's own working checkout (`repo = Path(__file__).resolve().parents[1]`, line 1367), whatever that checkout's HEAD is.
- It enforces only `ProcessType == "Interactive"` on the rendered bytes (lines 585–593 and 656), and it records the per-window `rendered_plist_sha256`.
- `grep -rn "template digests|template at commit|night.plist.template|night-probe.plist.template"` across the `.py/.sh/.zsh` files finds no check that the template sha256 at arm time equals `e62a461b…`/`1570b745…`. The issuer checks only that the pins are well-formed hex. It does not check them against git.

So if any later commit changes either template, W1 would still install and run. Examples: `Nice`, `LowPriorityIO`, `EnvironmentVariables`, `ProgramArguments`, or anything else that changes the launch context while leaving `ProcessType=Interactive`. That run would happen under a launch context different from the registered one, with nothing refusing it. The mismatch would show up only if someone later compared the recorded rendered digests against a re-render from `9b750bf3`.

Today the gap is closed only by fact: no template has changed between `9b750bf3` and `23dd9909`.

Recommended follow-up, not a condition for this merge: add a bench step to the W1 arm checklist, at minimum `git show HEAD:configs/launchd/<each template> | shasum -a 256` in the arm checkout, compared against the two registered digests and recorded in the arm evidence. Better, add an installer or night-gate guard that refuses when the template digests differ from those parsed out of the registration.

A second, smaller point on wording: "template digest at the merge commit" pins the template, not what gets loaded. The rendered plist adds per-window values (plan path, custody root, receipt path, calendar). The registration already says this explicitly, as A-R5a-1 intends, and the installer records the rendered digest per window. So nothing is misdescribed.

## Findings

| # | Severity | Finding |
|---|----------|---------|
| F1 | MATERIAL (follow-up; pre-existing; not a merge condition) | Registered template digests are not checked at arm or install time. The installer renders from its own checkout and enforces only `ProcessType=Interactive`. A post-seal template edit would run W1 under an unregistered launch context without any refusal. Fix: an arm-checklist digest comparison now, and a code guard later. |
| F2 | NIT | `tests/test_acc_25g83_rev5.py:95-98`: the header `.replace` now does nothing on the sealed file, so the fixture header (`9b750bf3`) disagrees with the fixture commit (`aaaa…`). Nothing consumes the header, so there is no science impact. Optional cleanup: stop relying on the replace, or assert the header form directly. |
| F3 | NIT | The issuer's Revision 5 guard is format-only (40/64 hex). It would accept wrong-but-well-formed values. This lens verified the values independently (S1). |

**Verdict: MERGE** `23dd9909`, as is. No replacement text is needed. Carry `497847c4adcae3d8a9bfef99148c602579cca2b4adec1893c1980e7b366fd191` as the registration digest in the W1 arm material, and put F1's template-digest comparison on the W1 arm checklist.
