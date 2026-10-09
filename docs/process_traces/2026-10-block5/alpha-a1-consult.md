# Block 5, ALPHA attempt 1: consult, cold ruling and decision

Magistrate activation d2ddcd8e (Opus 5.5, headless), 2026-10-08. Structure only. This record follows
`alpha-a1-window.md`. The papers are in `alpha-a1-consult/` beside this file: `BRIEF-body.md` (the brief
both seats had), `sol-consult.md`, `opus-consult.md`, `JUDGE-CHARGE.md`, `RULING.md`.

## Why a consult

The harvest gave ALPHA attempt 1 the window reasons `cell.below_minimum` and `neg8.bound_not_derived`.
Brief section 6 sends either code to two blind seats at once, on the first occurrence, before the same
pack is armed again.

## The two seats (about 21:24 to 21:31 PDT)

- **Sol 6.1**, effort high, through `codex-run-v3`, read-only scope. Recommendation: arm ALPHA attempt 2
  unchanged; contention is established but not shown to be what removed the units. The launcher exited
  rc=65 (`run_status=ACCEPTANCE_FAILED`: it could not parse the report's JSON header). The report body
  is complete and was read as a consult answer; the parse failure is recorded here as a protocol failure
  of the envelope, and nothing was consumed through the launcher's acceptance path.
- **Opus 5.5** agent, read-only. Recommendation: remove the contending daemons first, then arm from the
  same clone. It found that `com.apple.mediaanalysisd` and `com.apple.photoanalysisd` are listed as
  disabled for the login session and are nevertheless loaded and running.

What both found, and the judge recounted: the monitor's contention journal has 1,975 ten-second
intervals; 183 of them have an outside process above the registered limit of 0.05 CPU-seconds per second.
Intervals that contain each process: `mediaanalysisd` 77 (alone in 72), `corespotlightd` 51 (alone in
43), `fseventsd` 14, `PerfPowerService` 13, `runningboardd` 10, `mobileassetd` 10, `deleted` 9, `mds` 7.
The arm's own dwell before the chain was clean. Neither seat found a harvest defect. Both asked for a
count by exclusion code from `derived/exclusions.json`, a file brief section 6 closes.

## Cold ruling (Fable 5.1, new session, 21:33 to 21:42 PDT)

The seats disagreed, so the question went to a cold judge. Last line: `RULING: CURE-STEP-1-THEN-ARM`.

- Q1: boot out the two agents that are already disabled, then arm ALPHA attempt 2 from the same clone. No
  erratum is needed: nothing a window reads changes, and the registration already has a contending
  process removed before a re-arm. A new persistent disable of `corespotlightd` is not authorized; it is
  a question for Ed that does not hold the arm. If the bootout is refused: no reboot and no logout,
  record the refusal, arm unchanged, and send Ed the question with the exact error.
- Q2: neither seat's program may run. One narrower program, printed in the ruling, may run once; it
  prints family names and integers only, with no cell, stratum or member, and its output may go into the
  record and the arm notice.
- Q3: no error in either seat that changes the arm. The file-existence argument shows that the corpus
  bound was derived and then lost a member to a physics-in-span code, leaving fewer than the 10 the
  bound needs (10 of 12 had been kept, so there was no margin).

## The family count (the ruling's program, run once at 21:43 PDT, output verbatim)

```
excluded_members_total 19
excluded_members_by_family MEMBER_VALIDITY 6
excluded_members_by_family PHYSICS_IN_SPAN 18
dropped_target_units_total 14
dropped_target_units_by_family MEMBER_VALIDITY 4
dropped_target_units_by_family PHYSICS_IN_SPAN 13
target_cells_below_minimum 1
```

`PHYSICS_IN_SPAN` leads the dropped target units, so the ruling's main branch applies. Cause key of ALPHA
attempt 1 (registration 7.3): `cell.below_minimum` with families `PHYSICS_IN_SPAN` and
`MEMBER_VALIDITY`; `neg8.bound_not_derived` with family `PHYSICS_IN_SPAN`.

## The cure was refused by the operating system (21:43 PDT)

Before: `com.apple.mediaanalysisd` running as pid 98055, `com.apple.photoanalysisd` running as pid 81746;
`launchctl print-disabled gui/501` lists both as disabled.

- `launchctl bootout gui/501/com.apple.mediaanalysisd`: rc=150,
  `Boot-out failed: 150: Operation not permitted while System Integrity Protection is engaged`
- `launchctl bootout gui/501/com.apple.photoanalysisd`: rc=150, the same message.

After: both still running with the same pids, both still listed as disabled. Machine state is unchanged
between ALPHA attempt 1 and attempt 2.

## Decision

By the ruling's fallback: ALPHA attempt 2 is armed unchanged, from the same sealed clone. No reboot and no
logout. Ed is asked two questions in the arm notice, neither of which holds the arm: whether the Mac may
be restarted between windows so that the two existing disables take effect, and whether `corespotlightd`
may be disabled. If attempt 2 is lost to the same cause family, registration 7.3 sends it to a consult,
not to a third arm.

After each remaining harvest the journal tally (intervals over the limit, by process name) is written
beside the attempt, as the ruling asks, so the machine condition of each window is on record.
