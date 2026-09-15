# lt-03 — Fix round 1 and the FIX-5 ruling

## The FIX contract (lead-written, dictated closure shapes)

`/tmp/magistrate-d6888966/brief-04-fix-round-1.md`, 15 233 bytes. Every refuter
finding was dispositioned explicitly — none was silently applied and none was
silently dropped. Each item carried its closure SHAPE plus a defect-shaped
regression naming the counterfactual input and the production call site, and the
brief required the seat to confirm each new test was RED before the fix and
GREEN after. Items the seat disagreed with were to return `NEEDS_RULING` rather
than be redesigned in the seat.

| Item | Source finding | Disposition |
|---|---|---|
| FIX-1 | C1 / E1 / reconcile F1 — blocker | FIX |
| FIX-2 | E2 | FIX |
| FIX-3 | E3 | FIX |
| FIX-4 | E4 | FIX |
| FIX-5 | C3 / E5 | FIX — returned NEEDS_RULING, ruled below |
| FIX-6 | C2 / E6 | FIX |
| FIX-7 | 15 surviving mutations | FIX (test strength; acceptance clause (e)) |
| FIX-8 | C4 | FIX (docs) |
| FIX-9 | C5 | FIX (docs) |
| FIX-10 | consequential | FIX (document every new refusal literal) |
| §3 pre-registration | seat D F2 / contract §8 | NOT FIXED — escalated to the cold gate; declared untouchable in every brief |

Two ruled-out designs were named as forbidden in the brief so the seat could not
drift into them: no maximum-window ceiling constant (the adjudication rules it
out explicitly, and E3's oversized-window case invites exactly that mistake),
and no per-span timers / per-plan labels / arming declaration file.

## Round 1 seat

Astra `xhigh`, workspace-write, detached pid 68616, launched 07:31:17, returned
07:44 (clock reads). Output `/tmp/magistrate-d6888966/lt-04-fix-round-1.md`.
Envelope `status: blocked`, `completion: partial` — correct, because FIX-5 was
withheld. `unowned_dirty: []`. Landed as **`ffc3cafc`** (pushed), 8 files,
+342 / −37, all inside `WRITE_SCOPE`.

FIX-1..4 and FIX-6..10 closed, each with its regression confirmed RED-before /
GREEN-after by the seat. Seat-run modules: `test_install_night_agent` 38 OK,
`test_run_night` 96 OK, `test_magistrate_watchdog` 93 OK,
`test_gen_derivation_night` 40 OK, `test_night_gate` 59 OK,
`test_docs_freshness` 31 OK; `git diff --check` and `zsh -n` clean; its own
mutation replay reported ALL 16 MUTANTS RED. The lead replays independently at
the final head — no seat's green is accepted as sufficient (rule 1).

The FIX-1 regression is worth naming: it advances a controlled clock from 12:00
to 12:01:01 during bootout **with a second span immediately following**, so an
implementation that re-derived "today's spans" at bootstrap time instead of
carrying the SELECTED span's close would still be caught.

## The NEEDS_RULING, and the lead's ruling

The seat returned F1 (`lead_ruling`, blocking) and implemented nothing for
FIX-5: **the dictated shape contradicted itself.** It required refusing any `t0`
whose local wall-clock minute is ambiguous under a DST fold, while also
requiring a control at the FIRST 2026-11-01 01:30 occurrence to SUCCEED — but
both occurrences share that one ambiguous minute. The defect is the lead's, in
the brief; the seat was right to stop rather than pick an interpretation. This
is the NEEDS_RULING protocol working as designed.

**Ruled by the lieutenant (07:46): reject BOTH occurrences — every `t0` whose
local minute is ambiguous is refused, regardless of fold.** Reasons recorded at
the time of the ruling:

1. The contract refuter established from the installed manual
   (`/usr/share/man/man5/launchd.plist.5:448-482`) only that calendar intervals
   recur and omitted fields are wildcards; it could NOT establish real launchd
   behaviour on a repeated minute. Permitting fold=0 would rest on unverified
   dispatch behaviour.
2. A wrong dispatch is not retryable: the gate refuses `night_window_expired`
   and the write-once record at `run_night.py:1507-1510` then CONSUMES a
   pre-registered plan. That is evidence-bearing, which is exactly where D-161
   leaves fail-closed intact.
3. The cost is one local hour, once a year.

The seat itself recommended this option.

### Flagged to the magistrate — a narrowing of acceptance clause (c)

Kernel acceptance says "the plan's `t0` may be any clock time". After FIX-5 that
reads, precisely: **any whole minute that occurs exactly once in local time.**
The lieutenant's position is that this makes the physical granularity of
`StartCalendarInterval` explicit — launchd carries no seconds, and a repeated
minute is genuinely two instants for one label — rather than adding a timing
rule, which D-181 cl.1 would forbid. It is fail-closed, it is one refusal
literal, and it is trivially reversible. **The magistrate or the cold gate may
overrule it**; nothing downstream depends on the narrowing, and the alternative
(permit fold=0, refuse fold=1) is a one-line change to the same predicate.

The lieutenant judged this a code-mechanism choice, not a process rule, and so
inside its remit under rule 11's enumerated forbidden list. It is surfaced here
and in the handback rather than being left implicit.

### Not an escalation trigger

FIX-5 was never attempted and then failed; it was withheld pending a ruling. The
standing trigger is two consecutive rounds failing with the SAME SIGNATURE.
Round 1 closed nine of ten items green on first attempt. No trigger fired.

## FIX-5 completion seat

Astra `high`, workspace-write, detached pid 12372, launched 07:46:32 on a CLEAN
tree at `ffc3cafc`. Brief `/tmp/magistrate-d6888966/brief-05-fix5-ruling.md`
carries the ruling verbatim, the two literals `plan_t0_not_minute_aligned` and
`plan_t0_ambiguous_local_time`, five counterfactuals (seconds=17; fold=0;
fold=1; an ordinary control; and a SPRING-transition control at 2026-03-08
04:30, because the spring gap creates MISSING minutes, not ambiguous ones, and
must not be swept up by the fold predicate), and an explicit instruction to
confirm the FIX-1..FIX-10 regressions still pass — a fix round breaking the
previous fix round is the documented failure mode this step exists to catch.
