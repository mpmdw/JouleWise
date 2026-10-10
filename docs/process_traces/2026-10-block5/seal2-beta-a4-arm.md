# Block 5, second seal, BETA attempt 4: arm record

Magistrate activation 20773813 (Opus 5.5, headless), 2026-10-10. Procedure: brief section 5 with items 1 to
17 of the RUN_STATE top blocks. The previous window and why this arm is unchanged: `seal2-beta-a3-window.md`.

- Plan `v5-b5-beta-a4-20261010T2237Z`, pack BETA, attempt 4, schema `joulewise.night_plan.v5`,
  `HAZARD_PACK`. t0 15:37 PDT (epoch 1791671820); `window_max_s` 112620; G10 `false`.
- Plan sha256 `372d8a46fece7b776ec03fcbab03143de953ea12bece7c6fab74ed1e4ad1f29b`; plan inputs sha256
  `53f0420b2152d4328a7eba5054591ad1200c74015078d9a801626c87139668ff`.
- Clone `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18` at
  `9bd5317340a5512928f96c60c607bc4bf38ce305` (the pin commit of attempt 3's close), clean; its diff against
  H_claim lists the three seal documents and the ledger pin.
- 5.1: agent check: no foreign agent, no seat alive (before the plan and again before the install). No agent
  application open. Firefox open (pid 25671; E-2a is NO, so it stays, and the notice says so). Ledger `[] []`.
  Clock check passes (bound 4.69 ms against 5.0). Free disk 214 GiB (91 needed). Build 25G83. Battery:
  adapter connected, not charging. Model pins equal to the sealed pins (nine units).
- 5.3: desk identity `WRITTEN`; plan writer `STAGED`, no threshold differs from the defaults, no pack digest
  error; `chain.zsh` hash OK; chain check rc=0; preflight ok; desk seal check `no flag`, rc=0.
- Settle: the display has been asleep since 13:49:27 PDT and nobody has touched the machine since; t0 is
  108 minutes after that. `/private/tmp` was not counted again (3.7 million entries at the last arm), so the
  00:00 rule applies: a six-hour chain from about 15:45 ends about 21:45. t0 is inside item 17's range.
- 5.4: arm notice sent, Gmail message id `1a127daa7413df79`. It reports attempt 3's outcome and cause. Its
  count "14 of 15 captures valid" is wrong; the count is 13 of 14 (`seal2-beta-a3-window.md`). No unread mail
  from the owner before or after it.
- 5.5: install rc=0 at 15:06 PDT; labels `com.joulewise.night` and `com.joulewise.night.deadman` loaded, both
  `ProcessType` `Interactive`; the job runs `run_night.py run --plan` with this plan. Dead-man calendar:
  hour 23, minute 59.
- Files under `/Users/edr/night-plan-staging/v5-b5-beta-a4-20261010T2237Z`: `arm-env.zsh`,
  `chain-check.json`, `desk-seal-check/`, `identity-epoch.json`, `inputs-summary.json`, `install.out`,
  `plan-inputs.json`, `plan-record.json`, `schedule.json`, `t1-bindings.json`.

Checks that ran this activation and what each caught that touched a number: the window's own calibration
screen (stopped attempt 3 before any member ran); the harvest (recorded attempt 3 as not claim-usable); the
contention read, the pre-arm checks, the desk seal check and the END STATE count caught nothing.

Next activation: brief section 3. While this window is armed or running, case 1. After it ends, section 4
with RUN_STATE item 10. One rule added by this activation: if this attempt's chain stops with
`pre_calibration_capture_failed` and the ledger again shows `systematic-invalid` for its `pre` slot, convene
the two-seat consult before any attempt 5 (same cause twice).
