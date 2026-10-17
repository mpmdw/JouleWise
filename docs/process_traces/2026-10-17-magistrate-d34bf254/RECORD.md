# Magistrate activation d34bf254 (Opus 5.5, headless), 2026-10-17 from 11:47 PDT

Internal record; plain, no pedagogy pass.

## Launch
- Heartbeat written first. Pending notices: four `yield.stage_low` alerts (ordinals 3-6) from the machine-test smoke
  `SMOKE-d117_floor_qwen3-1p7b_v5-20261017T1735Z`. The smoke runs one member per collection stage, while the alerts count
  against the full plan, so they are expected. Ordinal 4's 0 of 1 is the member the test pushed over the idle cap on purpose.
- Gmail `from:claude2.glaring610@passmail.net is:unread`: none (and none read in the last day). No answer from Ed yet on
  Spotify / pid 43816. Both are still running (pids 917 and 43816, checked 11:5x).
- Directive issues: only the old open ones (#405, #408, #416, #417, #421, #422); nothing new.
- Email to Ed with all four notices, the machine-test outcome and the Spotify question: Gmail `1a14b36841cd2927`.
  `notice.ack` written after Gmail accepted it.
- Canonical root fast-forwarded `ad31062e9` -> `a7617f2ec` (docs only). No `com.joulewise.night*` label was loaded and no
  such plist was on disk. The watchdog script did not change, so the resident supervisor is not stale.

## Machine test MT-20261017T1735Z (pin P = 33816e4aa): ended, NOT passed
`report --uninstall` rc 0; the test's night jobs are uninstalled.
- Observed: agent pause, agent census, runner pause, fresh idle admission, idle cap, sampler restarts, sampler startup
  readings, sampler clean termination, keep-awake, per-run sleep readings, chain exit, smoke errors absent, harvest exit.
  "Meter present: not exercised" is expected.
- Not observed: "collection ran" and "smoke desk" (status `fail`).

Root cause: Sol 6.1 xhigh read-only seat, `/Users/edr/night-archive/b6-mt2-rootcause/sol-rootcause.md`. The lead
re-checked the cited code (`environment_admission.py` ~558, `controller.py` ~2114) and the governing texts. All three
defects are on the desk side; there is no collection fault and no wrong energy integration.
1. `environment_admission_refusals` still applies block 5's CPU busy-fraction veto (`cpu.admitted is not True`). The
   block-6 controller admits busy-only runs (`busy_fraction_admitted=true`, raw CPU result kept) by threshold-council Q3
   ("Adopt as a flag. 13 of 53 quiet rehearsal baselines fail it ..."). As a result the two succeeded members
   (prefill-p2048-abs-r01, busy p95 0.873, processor power p95 0.41 W against 1.0 W; and neg8-window-end-r1, busy p95
   0.872, 0.42 W) got `environment_admission_failed`. That reached `member.target_phase_precheck_failed` (reduce.py
   phase precheck) and `member.whole_window_member_failure` (the verdict writer in run_campaign.py), so both were excluded.
   In round 1 this would silently drop every busy-only run and reference, which changes the survivor set and the drift
   bound.
2. `acceptance.py` ~179 reads any `member.bytes_missing` as "the stage left no records". It called the deliberate
   cap-skipped stage `structure.missing_stage_bundles`.
3. `smoke.classify` returns `fail` on any nonzero stage rc. The cap-skipped stage exits rc 1, so a chance cap skip in a
   real pack smoke would hold the loop.

Observation for the record: the busy fraction came from `mediaanalysisd` (pid 812) at about 1.9 CPU-s/s during both
runs (`contention.request_overlap`). That is about 19 CPU-s per 10 s interval, far above c_q 0.54. Under S-8 as gated,
outside-processor CPU stays a flag for round 1, printed as a labelled alternative. mediaanalysisd cannot be booted out
(SIP), so round-1 runs will carry these flags.

## Decisions I made
- Fix on a branch from the lane (`fix/2026-10-17-b6-mt2-fixes`, worktree `JouleWise-wt-b6-mt2fix`), then re-run the
  machine test live at the new pin rather than build a desk-replay tool. The replay would need new code that
  re-reduces and re-verdicts (more number-bearing code to review). A live re-run costs about 1 h 10 min of machine time,
  which is idle anyway: round 1 cannot arm while Spotify and pid 43816 run.
- The environment-admission fix changes which data count. It therefore gets one executing review plus the two blind
  cold passes (Fable 5.1, Opus 5.5) before it merges into the lane, as the earlier MT fixes did.

## Seats
- Root cause: Sol 6.1 xhigh, codex-run-v3, `/Users/edr/night-archive/b6-mt2-rootcause/` (done 12:01).
- Fix: Sol 6.1 xhigh, codex-run-v3, brief `/Users/edr/night-archive/b6-mt2-fix/BRIEF.md`, report
  `/Users/edr/night-archive/b6-mt2-fix/sol-fix.md` and `.codex-report/b6-mt2-fixes.md` in the worktree (running from 12:05).
