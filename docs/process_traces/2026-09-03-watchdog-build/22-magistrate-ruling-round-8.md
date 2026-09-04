# Magistrate ruling: round 8 contract (after the Opus counter-review, trace 21, and the apex read A-1)

Date: 2026-09-04. Verdict adopted: NOT LANDABLE. The watchdog half's untested surfaces were the installer, the plist, and the checklist — the same "tests restate the implementation" signature relocated (Opus), which the magistrate accepts: the R-2 cure was applied to the watchdog and not to its sibling installer. Round 8 is the LAST fix round before the cold gate; any residual blocker after its delta re-audit goes to the cold gate as an open question rather than a round 9.

## Clauses (all mandatory; each with a red-then-green test)

C-1 (B-1 = A-1) **Drain ladder is clamped to the plan deadline.** `_enforce_drain` takes the earliest active parseable plan (if any) and every stage is `min(cooperative time, t0 − LEAD)`: REQUEST no later than t0−25 min, TERM no later than t0−16, KILL no later than t0−15; `step()` evaluates `relevant_standdown_plan`/`standdown_phase` on EVERY poll even while a drain is latched. Replacement ticks (no supervisor) under hold with an active plan in TERM/KILL phase signal that phase immediately. Tests: latch at t0−22 → KILL by t0−15; latch at t0−10 → KILL on the first poll; sibling plan with future `authored_epoch_s` arriving at t0−20 with a live resident → KILL by t0−15; replacement tick at t0−12 → TERM now.

C-2 (B-2) **The plist pins the canonical checkout.** The installer refuses to install from any checkout other than `CANONICAL_REPO` (`/Users/edr/code/JouleWise`, resolved; `git rev-parse --show-toplevel` must equal it) and renders that literal into `ProgramArguments`/`WorkingDirectory`; the checklist step says `cd /Users/edr/code/JouleWise` first. Test (behavioural, see C-4): installing from a temp copy exits non-zero with the named reason; the rendered plist from the canonical path contains the literal.

C-3 (B-3) **Backoff survives reboot correctly.** Persist `next_eligible` as a wall-clock epoch plus the boot identifier (`sysctl kern.boottime` or `time.monotonic()` vs uptime) — on a boot-id change any stored backoff is discarded with an event `backoff_reset_after_reboot`. Test: state written with a foreign boot id and a far-future monotonic → LAUNCHING (not BACKOFF).

C-4 (B-4) **The installer gets a behavioural test** in `tests/test_install_magistrate_watchdog.py`: run the real script in a temp HOME with a stubbed `launchctl` on PATH recording its argv; assert the plist bytes, the lock seed, the refusal on a non-canonical checkout, and that a failed lock seed removes the plist it wrote (S-2). No `assertIn` over the script's source.

C-5 (S-1) Replacement-tick granularity: a tick under hold computes the stage from wall time, not from tick count (covered by C-1's "signal that phase immediately").

C-6 (S-3) Document, in MAGISTRATE_WATCHDOG.md, that LaunchAgents do not load before login; the unattended-reboot case is an accepted limitation for this week (Ed's machine stays logged in) with the liveness threshold: no `state.json` write for > 15 min = watchdog dead → the courier email at the next window says so. No code.

C-7 (S-4) The documented rehearsal example plans must not share `measurement_root` with a real plan at a different head: examples use a clearly fake root under `/private/tmp/...` and the doc says so; `plan_conflict` semantics unchanged.

C-8 (S-5) The plist pins the interpreter: `/usr/bin/python3` is NOT acceptable (no repo deps); use the absolute path of the python that runs the tests today (`sys.executable` at install time, recorded in the plist and asserted by C-4).

C-9 (S-6) The courier/Gmail send is out of this round (it is the night driver's contract, not the watchdog's); recorded here as an open item for the packet.

Round 8 scope: scripts/magistrate_watchdog.py, scripts/install_magistrate_watchdog.sh, tests/test_magistrate_watchdog.py, tests/test_magistrate_watchdog_cli.py, tests/test_install_magistrate_watchdog.py (new), docs/process/MAGISTRATE_WATCHDOG.md, docs/process/MAGISTRATE_RELAUNCH_PROMPT.md, trace 23, addendum to 01.
