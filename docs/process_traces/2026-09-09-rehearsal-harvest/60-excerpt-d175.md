# D-175 excerpt (docs/decision_log.md lines 11138–11160 at 7ca2908f)
## D-175: headless magistrate arming authority — relaunch prompt line 19 amended (cold gate + Opus contract refuter, magistrate-synthesized, 2026-09-08; Ed may veto)

**Trigger (rule 11):** the interactive magistrate reinterpreted relaunch-prompt line 19 ("do not alter ... plans,
night records, or launchd configuration") so the watchdog-relaunched headless magistrate could arm the
post-watchdog REHEARSAL_STUB night through NIGHT_HANDBACK. An Astra scout had flagged the line-11/line-19
conflict as a lead-owned authority defect.

**Decision:** line 19 is replaced by the text in
`docs/process_traces/2026-09-08-handoff-redo/09-coldgate-packet-rehearsal-authority/13-magistrate-synthesis.md`
(watchdog-owned state and the magistrate launchd job stay barred; a plan the session authored under NIGHT_HANDBACK
may be re-armed or removed by that procedure; authoring a plan with `write_night_plan` and installing its two night
agents is arming, not alteration). Arming a REHEARSAL_STUB requires the eight conditions in that synthesis:
stage the plan outside the watchdog's `*/night_plan.json` glob, validate with `install_night_agent.sh
--render-only` from the pinned measurement checkout, `os.replace` into the plan directory, agents installed from
that checkout at t0's hour/minute, arm email with pins before the move, no OTHER agent session alive, pin
reachability preserved, exit by t0 − 25 min. A `/private/tmp` detached checkout is a valid REHEARSAL_STUB root
(MAGISTRATE_WATCHDOG.md line 258) and must never be reused by a real plan.

**Why:** both cold seats found the conflict textual, not structural (MAGISTRATE_WATCHDOG.md line 86 already names
the relaunched session as the arming party); the Opus refuter showed a malformed plan inside the watchdog's glob
would `HOLD_UNSAFE`, drain the resident and block every later launch (`scripts/magistrate_watchdog.py:1206-1210,
1729-1745`), which the staging + validation condition prevents; `plan_is_armed` is true from the authored epoch, so
an "already armed" carve-out would strip the session of the re-arm path the 09-03 rehearsal actually needed.
