# Cold-gate packet 71 — NIGHT-GATE-QUIET-ADMISSION-01: after four same-signature supervision findings, continue, stop, or split (assembled mechanically by interactive session 5c919872, 2026-09-17 23:3x PDT)

Convened under rule 11 of the project's operating doctrine: the decision whether
to spend a fourth fix round on one seam, to stop, or to split the lane is not
the loop-immersed magistrate's to make alone, and the standing escalation
trigger — two consecutive rounds failing with the same signature — has now
fired twice on this seam. The charter's own §9 states the rule independently.

Nothing is armed and no window is waiting on this gate: the 2026-09-17 night
agents were uninstalled and the magistrate watchdog is parked. That is the
assembler's statement of operating context, not evidence, and no question
below depends on it; the judge is asked to verify nothing about it.

The lane's subject is the unattended night gate's admission test. Cold-gate
ruling 70 (exhibit F) affirmed the design: admission may wait inside a sealed
bind window and re-sample, with the cutoff value itself REFUSED pending an
evidence campaign. Implementation since then has run: seat delivery, fix round
1, two refuters, fix round 2, a delta re-audit, an external design consult, a
round-3 redesign implementing that consult, and a delta re-audit of round 3.
Exhibit A is that chain, each step in the reviewing session's own words.

## What was found (from the exhibits; the judge verifies)

- Four reviews in a row have found the driver's bind loop blockable. Round 1:
  `ready()` calls `join()` (exhibit A §A1). Round 2's delta: `ready()` proves
  pipe readability, then `result()` performs an unbounded `recv()` on the
  supervisor thread (§A2). Round 3's delta, on the redesign: four BLOCKERs —
  `Queue.put_nowait` takes a mutex shared with a service thread (F1);
  `Thread.start` uses `_active_limbo_lock` and `Event.wait` after the deadline
  is established (F2); finalization requires `launch_done` even with no PID
  (F3); and result/reap waits, deadline resets and swallowed journal errors
  survive their named tests (F4) — plus two should-fix (§A5).
- The round-3 audit's own same-signature field states the recurrence in its own
  words: "Blocking paths outside tests recur F1-F4" (§A5). Round 2's delta had
  said "YES, structural" (§A2). Neither partition was drawn before the failure
  it explains; exhibit E §E3 records the project's prior-record test for that.
- The first three findings of §A5 are about in-process threading primitives
  reachable from the ticker (a queue mutex, thread startup, a completion flag).
  The defect that forced the redesign was a blocking read on a pipe. Whether
  these are one signature or two is a question the judge may need to answer to
  rule Q1 and Q2; the packet takes no position.
- The same audit killed 19 of 26 mutants, including the whole-file control
  ("no-op supervisor: KILLED: 20 failures/18 tests"), and ACCEPTed eleven of
  the fourteen rows of its own operation table (§A5). Seven mutants survived:
  join-in-result, deadline reset on chunks, swallowed writer exceptions,
  blocking `waitpid`, and the three fault-ACK deletions.
- The consult that designed round 3 set one acceptance bar (§A3, "Same-signature
  rule"), and the round-3 brief restated it (§A4). The brief's wording adds
  "a lock held by another thread" to the consult's list; the audit holds the
  code against the brief's wording (its `against` fields cite `brief:18`).
- The code at `73cdbbc4` states the invariant in two comments only
  (`run_night.py:1995-1996` and `:2049`) and attaches a bounded-work comment to
  most ticker operations; the audit's operation table accepts those comments
  except at startup, where it records "No bounded-start comment" (exhibit B,
  exhibit A §A5).
- The round-3 change is essentially one region of one file: `git diff 5c5a3323
  73cdbbc4 -- scripts/run_night.py` is a single hunk `@@ -1991,262 +1992,669 @@`
  plus one import and two parser lines (exhibit D §D3).
- The rest of the lane has no open finding. The contract refuter traced all
  eleven review items; items 1, 2, 5, 6, 7, 8 and 9 came back "traced, no
  finding", and the three that did not (items 3-with-F2, 10-with-F1,
  11-with-F3) were checked as landed by the next delta's disposition table,
  whose only non-clean row is E-F6 — the supervision row (exhibit C §C4).
- Test totals: the seat reports 341 tests OK at `73cdbbc4` (exhibit C §C1); the
  audit re-ran the same six modules and got `Ran 341 tests in 171.428s / FAILED
  (failures=2, skipped=9)`, flagged as a shared Python-path environment problem
  with "canonical interpreter passes 2/2" (§A5, flag G1). The full-repository
  replay of 6402 tests with 0 failures is on the PRIOR head `5c5a3323`; the file
  that would hold a replay of `73cdbbc4` exists and is 0 bytes (§C2).
- The live sampler has been run natively at fix-round-1 head `536fd4db` with
  full output recorded (§C3). The only record of a native run at `73cdbbc4` is
  a clause inside the brief the lead wrote for the audit; the audit recorded it
  as "Lead smoke PASS supplied, not reproduced" (§C3, §A5).
- Ruling 70 in force: Q4 REFUSE — no cutoff value may be activated, and the
  mechanism may land only with the value as plan data and no admitting default;
  Q10 named four items exceeding mechanism, and listed "sampler supervision"
  among the magistrate's mechanism discretion (exhibit F §F1, §F2).
- On Q5's premise: at `73cdbbc4`, `--observation` requires `--job-id` and
  `--result-fd` and writes a framed envelope to a descriptor rather than
  printing, and the flagless printing mode imports `smoke_observation_round`
  from `scripts.run_night` — the module Q3 would exclude from PR 1 (§C6).

## The questions

Five propositions. Each takes exactly one verdict: AFFIRM, REJECT or REFUSE,
with the deciding exhibit or an executed observation, a severity tier
BLOCKER / MATERIAL / NIT, and for REFUSE the exact defect and the minimum cure.

### Q1

> The round-3 invariant as written — "no operation on the deadline-owning path
> may wait for worker progress, EOF, filesystem completion, a lock held by
> another thread, or child exit" — is the right acceptance bar for the bind
> loop, and a contended in-process mutex held only for bounded work by a
> sibling thread is a violation of it.

If REJECT: state the bar that replaces it, in one sentence, in the instrument's
terms — what the census cadence and the bind deadline must tolerate.

### Q2

> A fourth fix round on the supervision seam, scoped to delta-23 findings F1-F6
> under the Q1 bar, may proceed, with a fifth round forbidden: a surviving
> BLOCKER after round 4 stops the lane.

### Q3

> The lane may be split. PR 1 is the gate-side mechanism — plan v4, the
> `quiet_admission` policy module, receipt v3, the generator flag and its
> invariants, the retry successor route under D-182, and the contract documents,
> with every v4 plan unarmable until a cutoff has authority — merged under the
> project's twelve-row gate now, with the driver's v4 bind loop excluded. PR 2
> is the supervision seam alone, gated on its own audit.

### Q4

> If the lane is split, the exclusion must be enforced by code — a v4 plan is
> refused by the driver at PR 1's head, fail-closed — and proven by a
> regression, not by process.

### Q5

> The evidence campaign QUIET-PREDICATE-EVIDENCE-01 (kernel 232) may run its
> sampling with the merged gate-side sampler CLI
> (`python -m joulewise.quiet_admission --observation`) before PR 2 lands,
> since it arms nothing.

## Constraints on the judge

Rule only Q1 through Q5. Amend no rule, decision-log entry, skill doctrine,
contract or pre-registration file, and write no file other than your ruling.
Cite exhibits by name. Cite code by `file:line` only if you personally read that
line at `73cdbbc4` in the branch worktree
`/Users/edr/code/JouleWise-wt-gate-quiet` (read-only, with `git -C` and
`sed -n`/`nl -ba`; never edit, stage, commit, stash or check out there) or at
`80dbcb4c` in `/Users/edr/code/JouleWise`.

Execute one probe of your own if the budget allows. Running the six-module set
is NOT permitted — it takes minutes and the packet does not need it. Running
`TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest
tests.test_quiet_admission` in the branch worktree IS permitted. Report whatever
it shows, labelled as your own observation with the time, including if it
contradicts the packet.

Do not arm anything. Do not run `launchctl` or any bootstrap. Do not touch
`~/night-custody` or `~/Library/LaunchAgents`. Do not read narrative process or
state documents; exhibit E states, for each of its excerpts, why it is offered
and where the non-narrative authority sits instead.

Perform the packet-hygiene check the charter requires and say where this packet
is incomplete or non-neutral. Keep the ruling under 14 KB and write it to
`docs/process_traces/2026-09-17-interactive-5c919872/71-coldgate-packet-supervision-stop-or-split/10-coldgate-fable-ruling.md`.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin
in the convening prompt.

## Exhibit manifest

```
a5cf7d31b2771ec0c6a77ca491aa103a3e700c1b0f4ca66cd6ef6b713c727991  exhibit-A-review-history.md
2491edd5dcd842b0d74d9b66d28cca4a82e0a91da4b399f3aef6ace701078235  exhibit-B-ticker-code-at-73cdbbc4.md
1b47dc0960d6d579bb3421098c4eb6620f09ce487d42318c2af15580ba6e2fae  exhibit-C-what-is-green.md
309894f5588fb83b7291bed9fa3e325850910c491c5931c2d65baf4165a629ad  exhibit-D-diff-shape.md
78eb147280853dce3ec9e51ba0986da8c3fd9d96402806229abe7a7ea20ed288  exhibit-E-doctrine.md
1ee64b7c38d6b3e0d94c13796f94ad9eb9a3d9c702eece2322fa8c9a185ee0c5  exhibit-F-ruling-70-scope.md
```
