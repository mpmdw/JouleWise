# delta 8 — final fresh-eyes review, `bookkeeping/2026-09-09-rehearsal-arm` @ 0fdb4011 (READ-ONLY)

Executed this session in /Users/edr/code/JouleWise-wt-magistrate-1ef89702 (PD-1): `git log/diff/show`
c6d64665..0fdb4011; the consult's Q3 extraction over added lines and whole-file over 21b; greps into
process-census-0055.txt, pass3-{standdown-census,census-classified,step4-bench}.txt and
21-activation-*/{events.jsonl,state.json,magistrate.lock.json}; a fence extractor diffing step-4's PY.

## 1. Q3 mechanical check
**Added lines, 21b + 21c + 00-DURABLE (operative prose): CLEAN.** After the 83953/48645 allowlist the
only tokens are 58633, 71666, 71687, 71607, 71596, 71682 — each on a line naming an artifact basename
that contains it (all five 716xx in `21-activation-1ef89702/process-census-0055.txt`; 58633 at
`pass3-standdown-census.txt:17`).

**Added lines, whole range: 27 further tokens**, all inside the custodied review files 21e7/21f, which
quote the deleted prose to condemn it — out of class, but the check as the consult wrote it (whole
range) fires on them, so a successor cannot run it without a carve-out written down nowhere.

**Whole-file over 21b: 2 violations, uncured, absent from the consult's §1.1 list.**
- `21b:348` "Activation 1ef89702 (pid 84232) … (events.jsonl seq 5, …)" — 84232 is **not in**
  `21-activation-1ef89702/events.jsonl`; it is in that activation's state.json/heartbeat.json/
  magistrate.lock.json/process-census-0055.txt.
- `21b:353` "lock pid 83086, supervisor 83075", same events.jsonl locus — neither pid is in either
  events.jsonl; both are in `21-activation-784a764e/state.json` and `magistrate.lock.json`.
Pids true, locus wrong; should-fix, but it confirms the consult — delta 8 cured the same three lines
reviewers had named and two unlisted sites survive. Non-violations: 2460/3600 (21b:173,251); 4000
(`[:4000]`, 21b:288, outside the allowlist); 1200 (21b:134; 1788947760+1200 = 1788948960 ✓).

## 2. Three residual sites + classifier identity
- `21b:311` — 71666/71687/71607 in process-census-0055.txt ✓; "gone" per pass3-standdown-census.txt,
  whose `daemon/spare/pty-host/resume` section is `(end)`, empty ✓ (collective absence is all the line
  claims); its "handoff-daemons rc 0" is joulewise-53's, and the artifact's own `rc=1` is explained two
  lines later as the wrong-cwd attempt ✓. `21b:366` — all five pids in process-census-0055.txt ✓.
- `00-DURABLE:593` — "since 09-04" deleted, 58633 present in the cited census ✓. **Predicate still
  uncorroborated:** the cited argv is `/opt/homebrew/Cellar/python@3.14/…/Python.app/Content` (truncated)
  and no artifact records 58633's argv containing `vllm` or a temp path; the only "vllm" in the bench dir
  is `pass3-step4-bench.txt:3`, a **mocked** fake vllm.
- **Step-4 classifier: byte-identical.** Exactly one fence matches (pgrep ∧ sessions) in each revision;
  equal at 5637 bytes. No hunk in the range falls inside a fence.

## 3. R1 on 21f2 — one blocker
- **BLOCKER, 21f2:3.** "content head reviewed: `734dadec` plus this file and **21g2** (replay tail) on
  top." (a) There is no 21g2 — tracked and on disk there is only `21g-full-replay.md` and `21g-replays/`.
  (b) That head **excludes three of the four files in 21f2's own commit**: the 21b:311/366 citations, the
  00-DURABLE edits and the custodied consult all landed in 0fdb4011, not 734dadec. The terminal review
  does not cover the head it terminates. Signature A in the review channel — instance five.
- **Should-fix, 21f2:29.** "from here every message claims only 'edits as specified'" — broken by the
  commit that ships it: 0fdb4011's message makes content claims, names three items against four changed
  files (00-DURABLE unmentioned), and credits to 21b a cured sentence that is in 00-DURABLE.
- **Should-fix, 21f2:27-29** paraphrases the consult as ruling "deletion under R2 closes the class"; it
  said "*for the operative prose of 21b/21c*, yes" and named three unmechanised channels. Both mechanism
  asks (R3 over `git log -1 --format=%B`; the outbound-message rule) are stated intent, installed
  nowhere — ruled-not-installed.
- Traceable ✓: regex at 21f2:8 byte-equal to `21b:270`; "nine mocked tables" = 9 PASS cases in
  pass3-step4-bench.txt; pass3-census-classified.txt classifies as described; all three Gmail ids appear
  in 21b/00-DURABLE on thread `1a0800cdb282c3f1`; every 21e7 blocker (renderer, crashpad, 7631–7644,
  7901) is gone from 21b/21c and the orphan bench citation landed at 21b:337.
- **Cross-doc, should-fix:** D6-2's floor (quit after 1788945300) is in 21b:323 and 00-DURABLE:591 only;
  `21c:242`, the *ruling of record*, still reads "quit … before … 1788947100" with no floor, so it still
  authorises the exact early-quit orphan D6-2 was raised to prevent.

## 4. Commit messages vs their diffs
- `ebf90cd6` — **over-claims**: asserts "no pid narration in 21b/21c … pass3-step4-bench.txt cited";
  diff is one file, +45, the custodied 21e7. Confirmed independently here.
- `734dadec` accurate, corrects ebf90cd6 in its trailer. `0fdb4011` no over-claim — every claim is in its
  diff — but omits 00-DURABLE and misattributes one cure.

## 5. Same-signature statement
- "prose contradicts its cited artifact": **SURVIVES** — 21f2:3 (nonexistent 21g2, head understated);
  weakly 00-DURABLE:593 and 21b:348/353. Fifth consecutive delta carrying it.
- "commit message contradicts its diff": **SURVIVES** at `ebf90cd6` — corrected in the next commit's
  prose, not in the artifact; and the anti-recurrence rule at 21f2:29 is already broken by 0fdb4011.

Both recurring is rule 11's standing escalation trigger: the next spend is a consult or an accepted-
with-limits landing, not a fifth prose reformulation, and under no circumstances a classifier edit.

VERDICT: NOT LANDABLE — blocker: 21f2:3 (terminal review cites a nonexistent 21g2 and states a reviewed
head excluding three of the four files in its own commit; it does not review the head it terminates).
Cure is one corrected line in 21f2. Should-fix if landing anyway: 21b:348/353 loci, 00-DURABLE:593's
uncorroborated vllm/temp-path predicate, 21c:242's missing D6-2 floor.
