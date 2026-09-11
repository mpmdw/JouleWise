SUBJECT: JouleWise NIGHT_HANDBACK notice — rehearsal-20260912 (REHEARSAL_STUB) t0 2026-09-12 00:30 PDT; installing now; reply NO to stand it down

Ed,

This is the NIGHT_HANDBACK email-then-arm notice for tonight's dry run. Launch needs no action from you unless you reply NO on this thread. Silence means the plan goes ahead. A NO at any time before 00:30 stands the night down; the agents are already installed by the time you read this, so a NO means I (or the next activation) uninstall them.

The one thing only you could do is done: the orphaned Claude daemon 83102 is gone (verified gone at 11:46 by this activation and again by Block A's census at 11:50:00 PDT; a final census runs immediately before publication). Thank you.

PLAN
- plan_id / class: rehearsal-20260912 / REHEARSAL_STUB (the driver's built-in `sleep 2; echo REHEARSAL`: no pack, no model, no measurement, no sudo)
- repo_head = measurement_head = H′ = a7d1eb88aaf9f70f430d95da69f39c4190299a80 (main; the merge of PR #323, the NIGHT_HANDBACK rewrite for this night; it carries PR #321 NIGHT-INTERPRETER-PIN-01, PR #322 NIGHT-C1-REGISTRATION-DOCS-01 and PR #320 EPOCH-CONTINUATION-01)
- measurement root (disposable): /private/tmp/joulewise-rehearsal-20260912-checkout, with a .venv whose bin/python is Python 3.13.1 — the interpreter both LaunchAgents name by absolute path
- custody root: /Users/edr/night-custody/rehearsal-20260912
- t0: 2026-09-12 00:30:00 PDT = 2026-09-12 07:30:00 UTC = epoch 1789198200; window 900 s (closes 00:45:00 PDT, epoch 1789199100)
- courier deadline: 00:50:00 PDT, epoch 1789199400
- arming-activation exit boundary: 00:05:00 PDT, epoch 1789196700 (the watchdog's stand-down request lands here; TERM 00:14, KILL 00:15). This activation exits right after recording the arm; any later activation the watchdog launches today is told the frozen triple and exits by 00:05.
- results branch: night-results/20260912 (does not exist on origin; verified with ls-remote --exit-code, rc 2)
- install: 12:02 (about ten minutes after this notice is sent) PDT today, from the stub checkout, --hour 0 --minute 30 (cold-gate C-5 allows any time after 07:00 PDT on 09-11)
- dead-man: the 07:00 dead-man never fires because both agents are uninstalled at harvest before 07:00 on 09-12; if that slips past 07:00 it takes the `courier already sent` branch and is harmless
- registration_path: configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json (the D-166 literal that night-gate row C1 hashes; digest proven at the desk against the compiled constant: dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265)

AUTHORITY
Cold-gate ruling docs/process_traces/2026-09-11-activation-58a3bcfc/06-coldgate-ruling-item6.md §4(c), reading R1, conditions C-1…C-9, with (a) as the automatic fallback; D-175 (email-then-arm) and D-180. Your non-veto of reading R1 on this thread is part of the evidence. The ruling's paragraph for you, verbatim:

> Ed — one decision, one word if you like. Last night's dry run of the measurement machinery never started: macOS's job scheduler (launchd) started our night driver with the wrong Python (an old 3.9 build the scheduler finds first on its path), and the driver crashed on its first import. We are fixing that so the job file names the exact Python it must use and the installer test-imports everything under that Python before it installs. Before the real "equivalence night" (the one measurement night that checks whether the OS update moved the instrument), the rules on file still require one more dry run through the scheduler: the driver's machine checks (idle, power, load, thermal, boot clock, pre-registration hash) have never run live from the scheduler since the last fix, and last night they never ran at all. The fastest honest way to do that is a dry run tonight at about 00:30 Saturday morning (Sept 12), installed this evening, harvested and removed before 03:00, so the real night can be installed Saturday morning and fire at 02:56 on Sunday Sept 13. The only thing you must do for any of this: kill the orphaned Claude background process (pid 83102 and its children) — every night check refuses while it is alive. If you prefer the usual timetable (dry run Sunday 02:56, real night Monday 02:56), reply NO and we do that instead. Silence means tonight's plan goes ahead.

(The install is happening in the daytime rather than "this evening": ruling 06 C-5's bound is any wall-clock time after 07:00 PDT on 09-11, and arming as soon as H′ exists removes the risk that a usage-limited activation is not alive this evening to do it. Nothing else in the plan changes.)

WHAT HAPPENS AFTER
The next activation (launched by the watchdog after the courier sends, earliest 00:50) harvests, judges item 6 against C-7, and retires the plan (uninstall from the stub checkout, remove the checkout and plan root) before 02:30. Then the equivalence night is installed in the 03:00–06:30 span on 09-12 for t0 2026-09-13 02:56 PDT. Fallback (a) — stub 09-13 02:56, equivalence 09-14 — applies without any further gate if any of C-1…C-8 is missing by 02:30 or if you say NO.

LIMITATION, stated as one: a headless activation cannot re-read this thread after sending. I rechecked owner-authored open directive issues immediately before publication; beyond that I cannot certify that no unseen reply exists.

CANCELLATION
Reply NO on this thread, or open a directive issue on mpmdw/JouleWise saying NO. A NO stands the night down; a veto of reading R1 specifically routes to fallback (a).

— magistrate 1944317a (headless activation 1944317a-0e0f-46d7-8ae4-9e16e6a8df13)
