# Block 5, second seal, BETA attempt 6: window record

Magistrate activation d7a980d2 (Opus 5.5, headless), launched 2026-10-11 19:14 PDT.

**Outcome: BETA attempt 6 is claim-usable. BETA is done and is never armed again. GAMMA attempt 1 is next.**

- Plan `v5-b5-beta-a6-20261011T2011Z`, the first attempt Erratum 3 governs. From `night/hazard_result.json`:
  verdict `GO`, `stage_reached` `chain`, no refusal, fault reasons none, every stage's yield status `OK`;
  chain exit code 0; 125 planned, 125 bundles present, 4 failed by the driver's count. Driver start 13:11 PDT,
  chain 13:16 to 19:11 PDT. Courier email Gmail `1a12de2704561fe4`.
- Item 19's clock check: (RAW minus Python monotonic) at `ended` minus the same at `started` is -334 ns.
  The Mac did not sleep. The keep-awake job `local.jwbench.keepawake` was loaded throughout (pid 30553).
- 4.2: no open session. 4.3: pin `ADVANCED` 478 to 488, operator identity `magistrate-20261012T0215Z`, clone
  commit `e84b1ea63ce98871486bf5de4b143e6b71d9e31d`; the clone differs from the seal commit only in the pin
  file. 4.4: uninstall rc=0, no night label or job file left; the dead-man calendar was hour 21, minute 33
  (removed before it fired).
- 4.5: pin test `HARVEST_PINNED`, desk root `b039c0257d1b1d407ee9598222db3f78f6ad7beb` (the pin that governs
  this attempt, RUN_STATE item 25). Harvest 19:16 to 20:05 PDT, rc=0, archive
  `/Users/edr/night-archive/harvest-v5-b5-beta-a6-20261011T2011Z` (22 GiB): `verdict` `COLLECTED`,
  `claim_usable` `true`, `exclude_window_reasons` `[]`, `faults` `[]`. Yield: planned 125, present 125,
  raw-valid 125, succeeded 122 (`02_phase_decode_abba_blocks_01_05` 19 of 20,
  `04_phase_prefill_p2048_absolute` 9 of 10, `neg8_bound` 17 of 18; every other stage whole). `harvest.json`
  sha256 `80398a5deb1d55f19c13f8e4057debd296b8dbb30dfa4de914cacc11aa8a97fe`. `harvest_checkout.head` equals
  the desk root, `status_clean` true.
- `calibration_bracket` in `harvest.json`, as the arm record expected: `evaluated` true, `status` `passed`,
  `freshness` `fresh`, `reasons` none, `erratum_3_governed` true, `trigger_scope` `window_evidence`,
  `recorded_only_triggers` `new_systematic_failure_challenges_preflight_screen`, doubling count 43 of 48,
  sequences of other sessions' systematic captures `[456]`. There is no window code, so no reason to open.
- Clock-status count (brief section 6 rule 3): attempt 6 recorded 124, not bounded 1; block total recorded
  890, not bounded 9: `continue`.
- Beyond the brief's list of files, this session printed `night/chain-stages.jsonl` of this window once
  (stage names, return codes, start and end times; no member, no energy), to see how long each stage took.
- A query-only reading of two time servers at 19:15 PDT (`sntp`, nothing set; RUN_STATE item 22(d)): the
  Mac's clock is 0.838 s from both (`time.apple.com` and `time.cloudflare.com` agree to 0.2 ms).
- Free disk after the harvest: 128 GiB by `df -g`. Ed ran the `/private/tmp` command at about 13:05 PDT;
  `/private/tmp` now holds 674,273 entries and 9 GiB (what is left was younger than a day then).
- Owner mail: no unread mail from Ed at launch. Ed told the interactive session at 13:07 PDT that the
  magistrate should "check the emailed design decisions i sent, about network time and physics numbers etc".
  A search by sender over five days finds one such mail, his of 2026-10-10 20:04 PDT (Gmail
  `1a128ebb107987ab`: the word "window", network time, proportion of the limits, why 100 runs, power traces),
  which activation 21c2e498 answered on 2026-10-11 (Gmail `1a129c14f0c1407a`) and whose follow-up lanes are
  RUN_STATE item 22. No later mail from him exists in the mailbox. The arm notice asks him whether he sent
  another.
