# R1 follow-up native smoke: not started (magistrate aa8a5a95, 2026-11-11 15:19-15:50 PST)

RUN_STATE item 270 asked the magistrate to run smoke Part A, then Part B, at
`ops/2026-11-11-r1-followup-kit` @ `6a9805190`. **Neither part was started. No
capture ran and no host setting was changed.**

## Why not

1. **No agent may be alive during the capture.** The kit's own contract says
   (`docs/align/r1_runtime_contract.md` @ `6a9805190`, line 272): "Run under the
   ordinary clean-host/DC-in custody procedure; the script is not authority to
   run while an agent is active." The kit report says "agent-free session"
   (next steps item 2). Ed's standing rule is that no measurement runs while an
   agent is alive. Item 270 has the magistrate start the smoke and stay alive
   without making tool calls. That leaves a live Claude process on the
   measurement Mac during the capture, so it does not satisfy the rule.
2. **Without a plan, nothing supplies the feeds item 270 checks.** On a night,
   the KM003C wall meter, the agent census and the volume census come from
   `run_night` and the HAZARD_PACK driver (`joulewise/b5/driver.py`, meter journal
   `METER_JOURNAL`). The bare
   `scripts/align_r1_followup_kit.py smoke` call starts none of them. Running
   it under `run_night` would need a night plan and an install, which is arming,
   and item 270 forbids that.
3. **No agent-free launcher exists for this smoke.** R0 used
   `scripts/launch_align_r0.py`. It writes a desk fence, bootstraps a one-shot
   LaunchAgent, waits for the magistrate to exit, sleeps the display and dwells
   300 s, and only then runs the runner. Its `launch` step is hard-wired to
   `scripts/align_r0_checks.py`. The watchdog honours any valid desk fence
   (`magistrate_watchdog.desk_fence_active`). The missing pieces are an R1 smoke
   runner spec and the feeds from point 2.

A smoke run with an agent alive and the feeds missing would only be partial,
and item 270 says a partial smoke "is not a pass and is never extended". So
I stopped before the capture rather than after it.

**Item 271 (lead, 15:21 PST) has since put item 270 on hold** until the merged
pre-signing commit is named. Points 1 to 3 hold for whatever commit item 272
names, so item 272 needs to pick how the smoke runs agent-free and where its
feeds come from.

## Read-only preflight (all passed)

- Condition 13: `reg.verify_r1_executed_sources` at `6a9805190` passed
  (executed_commit `6a9805190483ddcb40b89969c7ed4ae00adbe7c7`).
  `thermal_gates.py` is byte-identical to `82c14c9ea`.
- Nothing armed. `launchctl list` shows only `com.joulewise.magistrate`, and
  `~/Library/LaunchAgents` holds no `com.joulewise.night*` plist.
- Host at 15:45 PST:
  - AC power, 100 %, charged; `IsCharging` No; `InstantAmperage` 0.
  - `pmset -g custom` powermode 0 on both profiles.
  - Network Time Off.
  - No external volume.
  - 106 GiB free on `/System/Volumes/Data`.
- Soak reference: `/Users/edr/night-align/r1-20261111T043229Z/night/align-r1/soak_reference.json`.
  Item 270 calls this file `r1_soak_reference.json`; no file of that name exists.
- Kit worktree, detached at `6a9805190` (superseded by item 272's commit): `/Users/edr/code/jw-wt/r1-followup-smoke`.
  It is clean and nothing was run in it except the condition-13 check.

## What would unblock it (lead's choice)

- **(a) Agent-free handoff.** Generalise `launch_align_r0.py` to accept an R1
  smoke runner. The runner would:
  1. start `scripts/km003c_monitor.py` and the agent and volume census journals;
  2. read back powermode;
  3. run `smoke --part A`, then `smoke --part B` into new directories;
  4. restore Automatic and stop the meter.

  The magistrate then exits, and the next activation harvests and commits the
  results. This is new orchestration code, so it needs one executing review
  before use. About 1 to 2 h to build and review; the two parts take at most
  about 1 h (Part A within 1,800 s; Part B up to 1,800 s more).
- **(b) Lead-run.** The lead runs both parts from a session that is not on the
  measurement Mac, with the magistrate held off by a desk fence.
- **(c) Partial run.** The lead accepts a smoke with an agent alive and the
  feeds missing. That would contradict the contract line above and Ed's rule,
  so it is not recommended.
