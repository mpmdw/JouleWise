# 08k — Round 8 landed (`d5ec18bb`) and the LIVE launchctl smoke PASSED (magistrate b0ae8462, 2026-09-15 23:52 PDT)

Round 8 (report 08l): the record-and-poll design from packet 13 is on the branch — `Shield` records the first signal
only; polls at every state boundary and before every write_plist/bootstrap/print; the commit latch is the last poll
after the clock predicate; teardown never polls; INT/TERM/HUP ignored from teardown to process death; handlers
installed before argparse; `grep -c pthread_sigmask` = 0; 54 + 2 mutation pairs RED→GREEN under Python 3.14.7 and
3.9.6; both modules OK. Lead diff read: matches the adopted design line for line.

Live smoke (Ed-approved; script and README in 08m, tee log 08m-…-PASS.log; engine sha in the log header): REAL
launchd, throwaway labels `com.joulewise.smoke.night` / `.deadman`, throwaway launch_dir and custody root under the
session scratchpad, plists rendered from the real template with `/usr/bin/true`. Sequence observed: baseline
`print` rc 113 with the exact absence line ×2 → `bootstrap` rc 0 ×2 → `print` rc 0 ×2 (service dumps show the
calendar triggers) → engine install rc 0, state trace VALIDATED → … → VERIFIED → SUCCESS → `bootout` rc 0 ×2 →
`print` rc 113 + exact line ×2 → uninstall rc 0 → plists and sidecars gone → final liveness rc 113 ×2 →
`SMOKE VERDICT exit=0: PASS`. The D2 wire signature (`rc 113` + `Could not find service "<label>" in domain for
user gui: 501`) is pinned on macOS 25G83 twice (before load and after a real bootout). The fake-vs-real gap named as
the top first-shot risk is closed.

In flight on `d5ec18bb`: delta re-audit of round 8 (seat `delta8-astra`), execution lens 2 with real signals under
both interpreters (seat `exec2-astra`), and the lead's full-suite replay (12 workers).
