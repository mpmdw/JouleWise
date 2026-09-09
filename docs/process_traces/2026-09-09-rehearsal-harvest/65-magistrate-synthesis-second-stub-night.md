# Magistrate synthesis — second stub night (cold gate 61 + Opus refuter 62), activation 2145630c, 2026-09-09 ~09:20 PDT

Both seats rule (c): a second REHEARSAL_STUB night is REQUIRED, combined so that it also closes 21i acceptance item 5 (agents installed
before 07:00 on the calendar day BEFORE t0, so the pre-night 07:00 dead-man firing is observed standing down with one night.log line
and no writes into night/). The ground is item 5 and the un-exercised class-independent gate rows (refuter 62: the 09-09 gate returned
at the C5 chain read, so C1/C4 and the tail of C3 never ran live), not the cure's own branch (judge 61: a real night never takes the
stub branch). Adopted as the magistrate's decision; dissent: none material. Refuter caveats adopted: an agent-present refusal on the
second night closes item 5 only, not item 6; packet O-1 (stale diffstat excerpt: the merged change is 5 files 225+/100−, not 6 files)
and O-2 (item 3 PARTIAL omitted) are recorded here; O-4: a green stub's receipt verdict is exactly `REHEARSAL_ONLY`.

## Pins for rehearsal-20260911 (REHEARSAL_STUB; combined night)

- plan_id `rehearsal-20260911`; receipt_class REHEARSAL_STUB (driver's built-in stub `sleep 2; echo REHEARSAL`; no pack, no model, no
  measurement, no sudo). New plan_id, fresh custody root, fresh checkout path (61 N3; 21i's plan is never re-armed).
- t0 = 2026-09-11 02:56:00 PDT = epoch 1789120560; window_max_s 900; courier deadline t0 + 900 + 300 = 1789121760 (03:16:00 PDT);
  arming-session exit boundary t0 − 25 min = 1789119060 (02:31:00 PDT 09-11); relaunch belt 02:45–03:30 PDT 09-11.
- repo_head = measurement_head = H, the main commit that rewrites docs/process/NIGHT_HANDBACK.md for this night (H is a descendant of
  the cure merge a52810c9; 61 N1, 62 Q2). measurement_root `/private/tmp/joulewise-rehearsal-20260911-checkout` (disposable detached
  checkout at H, used only by this stub, removed with the plan root after harvest; never reused by a real plan — D-175).
- custody_root `/Users/edr/night-custody/rehearsal-20260911`; results branch `night-results/20260911` if the driver's push succeeds.
- INSTALL WINDOW (61 N2, both bounds): 2026-09-10 between 03:00 and 06:30 PDT — strictly after that day's 02:56 has passed (so the night
  agent's first daily firing IS t0 on 09-11, never a day early) and strictly before 07:00 (so the dead-man's first firing, 07:00 on
  09-10 = epoch 1789048800, precedes t0 and must stand down). Install both agents FROM the disposable checkout at H with
  `install_night_agent.sh --hour 2 --minute 56` after `--render-only` validation from that checkout; census of no other agent session
  immediately before; plan authored with `write_night_plan` to a staging path outside the watchdog's `*/night_plan.json` glob, validated,
  then `os.replace`d into place (D-175 eight conditions).
- Record at arm time (61 N4): `pmset -g batt` source and `pmset -g custom` powermode; the timer probe; state that a green stub says nothing
  about the capture-timeout seam. Powermode is recorded, not gated, for a stub.
- Harvest acceptance (61 N5, 62): `receipt.json` verdict `REHEARSAL_ONLY` (not REFUSED; `night_refused_agent_present` acceptable but then
  item 5 only, not item 6), C5 measured `chain_stub: built_in_stub_by_design` with null digests; `night.log` carries the dead-man
  stand-down line (~07:00 09-10) before the `night gate verdict=` line, and night/ holds nothing from that firing; the stub's launchd exit
  status 3 is unconditional for the stub class and is NOT a refusal signal (61 Q4.3). Any other refusal is a finding to cure first.
- Email-then-arm: the consolidated NIGHT_HANDBACK notice with these pins is sent AFTER commit H and BEFORE the move (D-175 condition 1 as
  applied on 09-08); Ed's NO on the thread stands the night down. Item 1 (cold_start.json derivation) is desk work, not this night's.

## Who arms

Whichever headless activation is alive in the 09-10 03:00–06:30 PDT window (this activation if still resident; else its successor from
the durable pointer), after re-reading the thread for a NO is impossible headless — the NO reaches the magistrate through the next
activation's prompt or an interactive session, as before. The arming activation exits after the arm record (the night is 20 h away, so
no t0 − 25 min pressure at install; the 09-11 stand-down is the watchdog's).
