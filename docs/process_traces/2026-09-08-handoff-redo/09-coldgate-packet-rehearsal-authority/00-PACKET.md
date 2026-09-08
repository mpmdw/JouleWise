# Cold-gate packet: may the WATCHDOG-OWNED headless magistrate arm a REHEARSAL_STUB night?

Assembled mechanically by the interactive magistrate (session 018PXMANyqqMtpXYryP26pEm) at 2026-09-08 ~01:20 PDT.
Rule-11 trigger: a reinterpretation of a standing instruction (relaunch prompt line 19) by the magistrate.

## Question
The headless magistrate's relaunch prompt (exhibit A) says at line 11 "Never arm or re-arm a night except through
the documented NIGHT_HANDBACK email-then-arm procedure; Ed's NO always overrides", at line 13 "The first real
window may be armed only under a v2 plan after both night agents are installed from that plan's measurement_root
at its measurement_head", and at line 19 "Do not alter watchdog state, locks, requests, events, plans, night
records, or launchd configuration except for the explicit heartbeat and notice acknowledgment interfaces."
Arming a night = writing a night plan under the custody root + installing two night LaunchAgents
(launchd configuration). Lines 11/13 presuppose the headless magistrate arms; line 19 forbids the writes arming
requires. Exhibit E (an Astra scout, fresh eyes) flagged this as a lead-owned authority conflict.

## The interactive magistrate's proposed ruling (to be upheld, amended, or overturned)
Line 19 protects watchdog-owned state (state.json, locks, requests, events) and plans/night records that are
ALREADY ARMED; it does not bar the documented NIGHT_HANDBACK email-then-arm of a REHEARSAL_STUB night after Ed's
arm email has gone out and no NO has arrived, provided: (1) NIGHT_HANDBACK.md is re-dated with the real pins of
the plan's checkout before the arm email (done: exhibit C at ae8f074f); (2) both night agents install FROM that
checkout at its pinned head; (3) the arm email names t0, measurement_root, measurement_head, receipt_class
REHEARSAL_STUB and the courier deadline; (4) no arming while any other agent session is alive on the machine.

## Facts the judge may rely on (verified by the interactive magistrate this session)
- Watchdog launched headless activation 1ef89702 at 2026-09-08 00:51:55 PDT (events seq 3-4); lock names pid 84232.
- The headless magistrate proposes plan rehearsal-20260909, t0 epoch 1788947760 (2026-09-09 02:56 PDT), receipt
  class REHEARSAL_STUB, measurement_root /private/tmp/joulewise-rehearsal-20260909-checkout = a detached
  checkout of ae8f074f created only at arm time; courier deadline 03:16 PDT; arm email sent (Gmail
  1a0800cdb282c3f1) with the pins as a follow-up on the same thread; it arms nothing until the interactive
  magistrate stands down.
- D-169 fences (exhibit D): the arming email precedes arming; Ed's standing NO overrides; REHEARSAL_STUB can
  never carry verdict GO; zero-agent census is the driver's first act.
- MAGISTRATE_WATCHDOG.md (exhibit B end): "Rehearsal stubs may follow watchdog installation ... their documented
  /private/tmp/... measurement roots are deliberately fake and must never be reused by a real plan."

## Charge to the cold judge
Rule: UPHOLD / AMEND (give exact replacement text for line 19 or the conditions) / OVERTURN (state who may arm the
rehearsal instead and what the headless magistrate must do). Test the ruling against the failure the design exists
to prevent: a headless session moving the watchdog's own state or an armed plan out from under the watchdog.
Also answer: does a /private/tmp measurement root for a REHEARSAL_STUB violate any fence in exhibits B or D?

## Exhibits
A relaunch prompt; B watchdog safety model + first-window paragraph; C NIGHT_HANDBACK.md at ae8f074f; D D-169
fences from the state kernel; E scout finding R2; F decision-log pointers (read those decision_log.md lines only).
