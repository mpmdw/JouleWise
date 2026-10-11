# Block 5, second seal, BETA attempt 5: window record

Magistrate activation bab1c330 (Opus 5.5, headless), launched 2026-10-11 06:33 PDT.

- Plan `v5-b5-beta-a5-20261011T0739Z`. From `night/hazard_result.json`: verdict `GO`, `stage_reached` `chain`,
  no refusal, fault reasons `["yield_low"]`; chain exit code 0; 125 planned, 125 bundles present, 8 failed by
  the driver's count. Driver start 00:39:05 PDT, chain exit 06:25 PDT. Courier email Gmail `1a12b26720aac233`.
- The driver's one `LOW` stage: `beta-science-prefill-p2048-abba-06-10`, 14 of 20 succeeded, minimum 16.
- Item 19's clock check: (RAW minus Python monotonic) at `ended` minus the same at `started` is -708 ns.
  The Mac did not sleep. The keep-awake job `local.jwbench.keepawake` was loaded throughout (pid 30553).
- 4.2: no open session. 4.3: pin `ADVANCED` 468 to 478, operator identity `magistrate-20261011T1334Z`, clone
  commit `a9b11f40c103de4aa2007b8220d90dbe9069c70d`. 4.4: uninstall rc=0, no night label or job file left;
  the dead-man calendar was hour 9, minute 1 (removed before it fired).
- 4.5: pin test `HARVEST_PINNED`, desk root `0699abbb0881ce64b39c46ba07de568cc3848260`. Harvest 06:36 to
  07:19 PDT, rc=0, archive `/Users/edr/night-archive/harvest-v5-b5-beta-a5-20261011T0739Z`: `verdict`
  `COLLECTED`, `claim_usable` `false`, `exclude_window_reasons` `["calibration.bracket_acceptance_failed"]`,
  `faults` `[]`. Yield: planned 125, present 125, raw-valid 125, succeeded 119 (stage
  `06_phase_prefill_p2048_abba_blocks_06_10` 14 of 20; every other stage whole). `harvest.json` sha256
  `8e69f3ef88b932a4b5e0f6a56816e2c1e45d5a64d19595bebf88c02f9a76170d`. `harvest_checkout.head` equals the desk
  root, `status_clean` true.
- Clock-status count (brief section 6 rule 3): attempt 5 recorded 121, not bounded 2; block total recorded
  766, not bounded 8: `continue`.
- Watchdog notices handed to this activation: the yield alert for the `LOW` stage above, and one
  `hold_census` at 06:28:31 PDT. The second is the window's own courier (pid 48779), seen by the watchdog three
  minutes after the chain's exit and before it released the plan; nothing ran beside the chain.
- Free disk after the harvest: 111 GiB by `df -g` (the archive is 21 GiB).

## The cause of attempts 4 and 5 (structure only), found 07:35 PDT

Attempt 5 has the same single window reason as attempt 4 and did not sleep, so the sleep was not attempt 4's
cause. A program that prints status words and reason codes only (numbers masked) read
`withheld/bracket-evaluation.json` of four archives:

| Attempt | assessment | reasons | acceptance freshness |
|---|---|---|---|
| ALPHA 1 (second seal) | passed | none | `fresh`, drift `passed_screen` |
| BETA 1 | passed | none | `fresh`, drift `passed_screen` |
| BETA 4 (`-r2`) | failed | `calibration_acceptance_bound_stale` | `stale`, `prospective_rederivation_required`, trigger `new_systematic_failure_challenges_preflight_screen` |
| BETA 5 | failed | `calibration_acceptance_bound_stale` | the same |

The calibration ledger's only block-5 capture with a disposition other than `valid` is sequence 456, the
`pre` slot of BETA attempt 3's session, `systematic-invalid` (the capture that stopped attempt 3). All four
captures of attempts 4 and 5 (sequences 464, 468, 474, 478) are `valid`, with alignment bounds of 27.6 to
31.9 ms against the 36.46 ms screen. So the reading is: that one capture is a registered trigger that makes
the calibration acceptance `d079_calibration_acceptance_v2_n24_25g83_r2` stale for every later harvest, and
the drift comparison is then never made. Attempts 4 and 5 were lost to it, and an unchanged arm of BETA or
GAMMA would be lost the same way.

**Correction of the 2026-10-10 record** (`seal2-beta-a4-window.md`): its decision took attempt 4's
`calibration.bracket_acceptance_failed` as the consequence of the sleep and armed attempt 5 unchanged. The
reason code was read and the reason inside it was not. The sleep was real and the keep-awake job stays; it
was not what removed attempt 4.

**Hold.** No pack is armed until this is cured. Brief section 6 rule 1 (same cause twice): two blind seats
were convened at 07:45 PDT, Sol 6.1 at effort high through `codex-run-v3` and an Opus 5.5 agent; brief
`/Users/edr/night-archive/b5-consults/beta-a5-stale/BRIEF.md`, reports `seat-sol.md` and `seat-opus.md`
beside it. Their questions: whether the reading is right; what the registered re-derivation needs and which
gate (desk work, a prospective cold erratum, a new seal); whether the trigger rule is proportionate; the
status of attempts 4 and 5; a desk check that would have shown the stale state before an arm.
