# Block 5, second seal, BETA attempt 3: arm record

Magistrate activation 4c4ed4b2 (Opus 5.5, headless), 2026-10-10. Procedure: brief section 5 with items 1
to 17 of the RUN_STATE top blocks. The previous window is in `seal2-beta-a2-window.md`, and why this arm is
unchanged in `seal2-beta-a2-consult.md`.

- Plan `v5-b5-beta-a3-20261010T2151Z`, pack BETA, attempt 3, schema `joulewise.night_plan.v5`,
  `HAZARD_PACK`. t0 14:51 PDT (epoch 1791669060); `window_max_s` 112620; G10 `false`.
- Plan sha256 `0e8480329c69fbe5b28ba207050c2f7b46a8a49ca7246bf88473df4238f50415`; plan inputs sha256
  `f192e9781742bc38045863401d44676d5dff5afb3fc7b816489f27b1c8377a41`.
- Clone `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18` at
  `c97389f2f3be4c846459d18c4c0500bb942325c9` (the pin commit of attempt 2's close), clean; its diff against
  H_claim lists the three seal documents and the ledger pin.
- 5.1: agent check: no foreign agent, no seat alive (both times, and again before the install). No
  agent application open. Firefox open (pid 25671; E-2a is NO, so it stays, and the notice says so).
  Ledger `[] []`. Clock check passes (bound 4.69 ms against 5.0). Free disk 214 GiB (91 needed). Build
  25G83. Battery: adapter connected, not charging, 0 mA. Model pins equal to the sealed pins (nine units).
- 5.3: desk identity `WRITTEN`; plan writer `STAGED`, no threshold differs from the defaults, no pack
  digest error; `chain.zsh` hash OK; chain check rc=0; preflight ok; desk seal check `no flag`, rc=0.
- Settle: the display was woken at 13:28:09 PDT and the last keyboard event was at 13:42:45; the display
  was put to sleep at 13:49:27. t0 is 62 minutes after that. `/private/tmp` holds 3.7 million entries
  (113 GiB), so the 00:00 rule applies; a six-hour chain from 14:51 ends about 21:00. Today's daily batch
  ran at 12:53:29 (item 17).
- 5.4: arm notice sent, Gmail message id `1a127b0c7a05d282`. It also reports what stopped attempt 2 and the
  daily-batch finding. No unread mail from the owner before or after it.
- 5.5: install rc=0 at 14:21 PDT; labels `com.joulewise.night` and `com.joulewise.night.deadman` loaded,
  both `ProcessType` `Interactive`; the job runs `run_night.py run --plan` with this plan. Dead-man
  calendar: hour 23, minute 13.
- Files under `/Users/edr/night-plan-staging/v5-b5-beta-a3-20261010T2151Z`: `arm-env.zsh`,
  `chain-check.json`, `desk-seal-check/`, `identity-epoch.json`, `inputs-summary.json`, `install.out`,
  `plan-inputs.json`, `plan-record.json`, `schedule.json`, `t1-bindings.json`.

Checks that ran this activation and what each caught that touched a number: the harvest (removed attempt 2
from the claims: no closing calibration); the consult (found the 12:53 daily batch, three or four members
of one stage); the pre-arm checks, the desk seal check and the END STATE count caught nothing.

Next activation: brief section 3. While this window is armed or running, case 1. After it ends, section 4
with RUN_STATE item 10.
