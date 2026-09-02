# Cold gate D1 — magistrate ruling (2026-09-01)

**Trigger.** Luna 132 (delta re-audit of night-driver fix round 3,
`f07c85d5`) ruled FIX-ROUND on one blocker, D1: the round-3 cure for terra
F3 makes the dead-man read an empty `chain.started` as a failed launch, but
the O_EXCL claim creates that empty file BEFORE `Popen`, so a dead-man that
reads it in that window would courier over a chain that is actually
starting. F3 and D1 are both about what an incomplete `chain.started`
MEANS to the dead-man, so a fix round 4 is the second fix round on the same
defect. CLAUDE.local.md rule 11 makes the cold gate mandatory, and the
standing escalation trigger (same signature twice) makes the next spend a
consult, not round three. This gate is both.

**Packet.** `coldgate-d1-packet.md` (mechanically assembled: luna D1 and
terra F3 verbatim, ruling R-3/R-7/§8 d.3 text, line-numbered code at
`f07c85d5`, the launchd template, four questions). Three seats, three model
families, none with loop context:

| Seat | Model / lens | Output |
|---|---|---|
| Sol xhigh, design | `gpt-5.6-sol`, read-only codex seat | `133-sol-coldgate-d1.md` |
| Opus 5, contract lens | fresh subagent | `coldgate-d1-opus.md` |
| Cold Fable, execution reality | fresh subagent | `coldgate-d1-fable.md` |

## What the seats agreed on

1. **Q4 is the bigger defect, and it needs no race.** All three: a
   dead-man that fires at 07:00 BEFORE the night's `t0` (agents installed
   the morning of a 23:00 night; the installer even creates the empty
   night dir) finds no marker, censuses, may write a write-once
   `refusal.json`, pushes a results branch, launches the courier (an email
   for a night that has not happened), and writes write-once
   `courier.json`. The real `run` then dies at `_existing_record`
   (`run_night.py:1009-1012`) with a rerun refusal and no courier; the
   next morning's dead-man sees `courier.sent` and skips. The night is
   lost silently. (Opus §Q4, Fable §Q4, Sol §Q4 "F2 — blocker".)
2. **The cure for both D1 and Q4 is a temporal eligibility guard in
   `dead_man()`**, not a change to what the marker means. Fable: stand down
   while `now < t0 + window_max_s + COURIER_DEADLINE_S` (the completion
   epoch, the same arithmetic as `run_night.py:1039`). Sol: stand down
   until `now >= _next_deadman_epoch(t0)`. Opus: stand down while
   `now < t0`, plus schedule guards. The run path already guarantees
   `completion < _next_deadman_epoch(t0)` (`:1040`), so for every plan the
   driver will admit, Fable's and Sol's bounds select the same 07:00
   occurrence; Fable's is the tighter statement of the invariant (the
   dead-man may act only after the night can no longer be in progress) and
   also refuses a manual `dead-man` invoked during the window.
3. **Round 3's marker semantics are correct once the guard exists.**
   Fable's state table (absent / empty / partial / null-pgid / pgid, each ×
   `chain.exited` absent/present) records every branch as correct when
   evaluated after the completion epoch. Opus and Sol both retain the
   null-pgid branch. No seat wanted (b) (mtime grace) or (c) (drop the
   null branch — reopens F3 in its crash form).
4. **D1's reachability is confined to schedules the driver should refuse.**
   Opus and Fable: only when the armed hour coincides with 07:00 (or a t0
   ≥ 07:00 plan meets a coalesced wake); the coalesced-wake case for a
   t0 < 07:00 plan is closed by `night_gate.py:556` before any claim. Sol
   counts more schedules reachable because `dead_man()` has no temporal
   check at all — which is Q4 restated.

## Where they split, and the ruling

- **Marker protocol.** Opus adopts (a) (`chain.claim` + complete
  `chain.started` via temp+rename); Sol proposes an `O_EXLOCK` on the
  marker held through launch publication, with the dead-man acquiring the
  same lock; Fable keeps the single marker unchanged. **Ruled: Fable.**
  With the eligibility guard the dead-man never reads a marker inside
  `[t0, completion)`, and the run path cannot legitimately hold the claim
  outside it (`night_window_expired` refuses before the claim once
  `now > t0 + window_max_s`; the claim-to-`Popen` interval is milliseconds
  against a 300 s deadline). (a) still couriers on the absent marker in
  the same-second case (Fable's objection stands), and the lock design
  trades an unreachable race for a dead-man that can block on a stuck
  launcher (Sol's own residual). Neither buys anything the guard does not.
  Recorded as dissent: Sol (lock), Opus ((a) + claim file).
- **Enabling configuration.** Opus asks the installer to refuse
  `--hour == DEADMAN_HOUR` and the plan to refuse a t0 within
  `COURIER_DEADLINE_S` of the dead-man boundary. **Ruled: adopt the
  installer refusal** (four lines, one test; it removes the only schedule
  under which D1 was reachable on an awake machine, and no real plan arms
  at 07:00). The plan-side boundary refusal is NOT adopted: with the
  guard in place a t0 ≥ 07:00 plan is merely a daytime plan whose dead-man
  is the next morning, which R-7 tolerates.
- **Q4 predicate.** Opus's `now < t0` is necessary but not sufficient
  (Sol: "checking only `now < t0` is insufficient when `t0 = 07:00`").
  **Ruled: the completion-epoch predicate**, which subsumes it.

## Ruled cures for fix round 4 (binding on the brief)

- **C1 (blocker; cures D1 and Q4).** Hoist
  `completion_epoch_s = t0 + window_max_s + COURIER_DEADLINE_S` into one
  helper used by BOTH `run` (`:1039`) and `dead_man`. In `dead_man()`,
  after the `courier.sent` check and before the courier-lock check: if
  `time.time() < completion_epoch_s`, append one `night.log` line
  ("dead-man fired before the night's completion deadline <epoch>;
  standing down") and return `EXIT_GO`, having written NOTHING else
  (no census, no write-once record, no push, no courier). `night.log` is
  append-only and outside the write-once set, so the stand-down leaves no
  state that a later run or dead-man can trip on.
- **C2 (should-fix; removes the enabling schedule).**
  `scripts/install_night_agent.sh` refuses `--hour == DEADMAN_HOUR`
  outright (the whole hour, not just the dead-man minute), with a
  usage-class exit and a message naming the dead-man hour. It already
  reads the constants at `:54-57`.
- **C3 (should-fix; Opus dissent, stale-night guard).** The installer
  already exits 3 on `chain.started` without `chain.exited`. Extend the
  same check to refuse when the night dir holds ANY write-once record
  (`result.json`, `receipt.json`, `refusal.json`, `courier.json`,
  `courier.sent`, `chain.started`, `chain.exited`): a plan is armed against
  a fresh custody root, never over a previous night's records.
- **Not in round 4.** No marker-protocol change; no `night_gate` schema
  change; no courier-prompt change; the dead-man's post-night behaviour
  (every branch in Fable's table) is unchanged.

## R-7 amendment (recorded here; the stage-1 ruling file is not edited)

R-7 gains the mirror bound all three seats found missing: *the dead-man may
act only after the night's completion epoch
(`t0 + window_max_s + COURIER_DEADLINE_S`); before it, the dead-man writes
nothing but a log line and exits GO.* Stage-2 acceptance
(NIGHT-REHEARSAL-01) gains one rehearsal case: agents installed the morning
BEFORE the armed night, so the pre-night 07:00 firing is observed standing
down. The morning ritual in `docs/process/NIGHT_HANDBACK.md` gains
`scripts/install_night_agent.sh --uninstall` after the handback is read
(Fable secondary; the dead-man otherwise fires every 07:00 forever, silenced
only by `courier.sent`).

## Dissent kept on record

- Sol: an `O_EXLOCK` marker transaction is the safety-first design; and
  R-7 should say "one active courier owner, bounded retries, stop after
  `courier.sent`" rather than "exactly one courier" (email plus a local
  marker cannot give literal exactly-once delivery). The second point is
  accepted as wording; R-7's property is ownership, not delivery count.
- Opus: the night dir should be night-scoped (`night/<YYYYMMDD>/`). Not
  adopted for stage 1: the plan's `custody_root` is per-night by the arming
  rule (C3 enforces it); a dated subdirectory is a stage-2 refinement.

## Gate composition for round 4

Fix seat: terra xhigh (Sol wrote rounds 2 and 3; rotate). Delta re-audit:
Sol xhigh or luna xhigh, with the executed pre-fix evidence standard of
round 3 and the mutant set: drop the guard; `<`→`<=`; `t0` instead of the
completion epoch; installer hour check removed; stale-record check removed.
A same-signature failure of round 4 is a structural signal — the next
spend is a design consult on the dead-man's contract, not round 5.
