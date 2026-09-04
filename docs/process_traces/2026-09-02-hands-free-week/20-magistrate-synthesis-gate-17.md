# Magistrate synthesis of cold gate 17 (cold Fable file 19, Opus refuter file 18), 2026-09-04 03:20 PDT

Both seats: the packet was defective (Q2 pinned the superseded watchdog revision; the file-15 "dated amendments" were adopted post hoc instead of proposed; Q1/Q3 compound) and the OBJECT has one integration blocker and several material gaps. No re-convening until the cures below land; the next packet (21) carries the two glob/latency amendments as PROPOSED addenda 4 and 5 in 17j, the Opus-amended R-6/R-7/R-9 texts (file 18 Q6, with the D-171 item-7 supersession stated and routed to Ed), the cold seat's additions (file 19 Q6), a Q2 pinned to the round-4 head, and integration-tree evidence.

Cures owed before packet 21:
| # | Finding | Cure | Owner |
|---|---|---|---|
| B-1 | On the merged tree the watchdog's plan glob reads the two retired v1 custody plans → HOLD_UNSAFE every tick; its fixtures are v1 (12 errors) | Round 4 on the INTEGRATED base (plan-pin merged into the watchdog branch): v2 fixtures and doc plans; retired-v1 plans are recorded once as `plan_retired_v1` and IGNORED by the fence (never a hold); a test on the merged tree | Sol round 4 |
| Q1 (18) | Installer accepts stale / future-dated plans the gate refuses | plan-pin round 3 (running): installer applies the gate's age/future checks | Sol |
| Q2 (18) | No test pins `SUPERVISOR_POLL_S = 10`; poll 600 survives | watchdog round 3 (running): literal assertion + deadline-hit regression | Sol |
| Q5 (18, 19) | Relaunch prompt fences only the dev checkout; nothing bars ratifying process rules; R-9(3) absent | watchdog round 3 (running) | Sol |
| M-1 (19) | No launchd-spawned `-p` proof before the twin kill | Bench: a throwaway LaunchAgent `com.joulewise.magistrate.rehearsal` that runs the file 17g spawn command once from launchd (no TTY); custody the receipt; uninstall | magistrate bench |
| M-2/M-3 (19) | Orphans outside the session tree (`claude --bg-pty-host` at ppid 1; shell-snapshot children at ppid 1) escape the tree walk → census hit at t0 | Handoff procedure (doc §install handoff): before the first stand-down the magistrate stops every background task, records the explicit pid list of the Terminal-hosted tree + daemon + spares + orphans, kills them, and verifies the census empty; the watchdog never kills unowned pids | Sol round 4 (doc) + magistrate at handoff |
| Q4 (19) | Ordering must move the v1 custody roots out of the glob and install the night agents from the measurement checkout | Handoff procedure: rename `~/night-custody/rehearsal-2026090{2,3}` → `~/night-custody/retired-v1/…` before install; NIGHT_HANDBACK + prompt say night agents install from the measurement checkout | magistrate at handoff; Sol round 4 (doc) |
| Q3 (18) | R-9 addendum must cite D-171 item 7 and record the supersession of Ed's 5-minute figure by the 15-minute physics margin | 17j text (file 18 Q6 R-9) + email to Ed (default: physics margin stands) | magistrate |
| Q7 (18/19) | Packet hygiene: proposals not adoptions; correct pins; integration evidence; no compound questions | packet 21 | magistrate |
