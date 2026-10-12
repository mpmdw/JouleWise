# Block 5, second seal, GAMMA attempt 1: window record, and the close of collection

Magistrate activation 76a41dde (Opus 5.5, headless), launched 2026-10-12 02:19 PDT.

**Outcome: GAMMA attempt 1 is claim-usable. All three packs have a claim-usable window. Block 5 collection is
closed (brief section 7) and nothing further is armed.**

- Plan `v5-b5-gamma-a1-20261012T0420Z`, governed by Erratum 3. From `night/hazard_result.json`: verdict `GO`,
  `stage_reached` `chain`, no refusal, fault reasons none, every stage's yield status `OK`, window yield
  status `PARTIAL`; chain exit code 0; 107 planned, 107 bundles present, 4 failed by the driver's count.
  Driver start 21:20 PDT on 2026-10-11, chain 21:23 to 02:14 PDT. Courier email Gmail `1a12f666f4e1716c`.
- RUN_STATE item 19's clock check: (RAW minus Python monotonic) at `ended` minus the same at `started` is
  2,499 ns. The Mac did not sleep. The keep-awake job `local.jwbench.keepawake` was loaded throughout
  (pid 30553).
- 4.2: no open session. 4.3: pin `ADVANCED` 488 to 498, operator identity `magistrate-20261012T0920Z`, clone
  commit `4cb222a19cba8b60b936941e9ed3997121471359`; the clone differs from the seal commit only in the pin
  file. 4.4: uninstall rc=0, no night label or job file left; the dead-man calendar was hour 1, minute 56,
  and the job fired once inside the window at 01:56:01 PDT and stood down (brief 4.1: not a fault). By the
  stage times that instant is inside `gamma-science-04-prefill-p2048-contrast-blocks-06-10` (01:13 to
  02:02 PDT).
- 4.5: pin test `HARVEST_PINNED`, desk root `b039c0257d1b1d407ee9598222db3f78f6ad7beb` (the pin that governs
  this attempt, RUN_STATE item 25). Harvest 02:21 to 03:03 PDT, rc=0, archive
  `/Users/edr/night-archive/harvest-v5-b5-gamma-a1-20261012T0420Z` (18 GiB): `verdict` `COLLECTED`,
  `claim_usable` `true`, `exclude_window_reasons` `[]`, `faults` `[]`. Yield: planned 107, present 107,
  raw-valid 107, succeeded 103 (`gamma-science-02-decode-contrast-blocks-06-10` 19 of 20,
  `gamma-science-03-prefill-p2048-contrast-blocks-01-05` 18 of 20,
  `gamma-science-04-prefill-p2048-contrast-blocks-06-10` 19 of 20; the corpus 18 of 18, every reference
  stage whole, the reference `gamma-reference-arm-boundary` 1 of 1). `harvest.json` sha256
  `4bb49435f33d481b8404c9e5540ea515a4ba2910cc98316e34467d2424a8d1c7`. `harvest_checkout.head` equals the desk
  root, `status_clean` true. The claim runs root holds its verdict file (tested for existence, not opened).
- `calibration_bracket` in `harvest.json`: `evaluated` true, `status` `passed`, `freshness` `fresh`,
  `reasons` none, `erratum_3_governed` true, `trigger_scope` `window_evidence`, `recorded_only_triggers`
  `new_systematic_failure_challenges_preflight_screen`, doubling count 45 of 48, sequences of other sessions'
  systematic captures `[456]`. There is no window code, so no reason to open.
- Clock-status count (brief section 6 rule 3): this attempt recorded 105, not bounded 1; block total recorded
  995, not bounded 10: `continue`.
- Midnight (RUN_STATE item 29): 00:00 PDT fell inside `gamma-science-02-decode-contrast-blocks-06-10`
  (23:25:55 to 00:13:49 PDT), 14 minutes before that stage ended. The reference
  `gamma-reference-arm-boundary` ran 00:14:49 to 00:16:58 PDT, so it started 15 minutes after midnight, not
  the 20 minutes or more the arm's prediction aimed at; it succeeded (1 of 1). The stage midnight fell in
  lost 1 of 20; whether the walk cost that member is not read here (the member-level records are
  restricted).
- Free disk after the harvest: 120 GiB by `df -g`.
- Beyond the brief's list of files, this session printed, of this window: `night.log` (six driver lines:
  start, the dead-man line, the verdict word, two pushes, the courier attempt), `night/result.json`,
  `night/chain-stages.jsonl`, `night/stage_yield.jsonl` and the last lines of `night/launchd.night.out` (the
  courier's closing text). Brief 4.1 says not to open `night.log`; it was opened before the brief was read.
  None of these holds a member's energy or a data value, and nothing read there entered a decision.
- The watchdog's pending notice at launch: `transition-2775-hold_census`, 02:14:49 PDT, "production census
  non-empty inside plan span". The watchdog's own census event of that second names the one process it saw:
  pid 19488, the night courier of this plan (the `claude -p` session the driver starts after the chain to
  email the result). The chain had exited at 02:14:39 and no member was running. The hold cleared at
  02:19:50 when the courier had gone. No measurement was touched.
- Owner mail: no unread mail from Ed at launch or before the closing email. Open directive issues: #405,
  #408, #416, #417, #421, #422, all standing since September; none new.

## The block, attempt by attempt

Verdict, `claim_usable`, window reasons and the SHA-256 of `harvest.json`, read from each archive root.

First seal (corpus of 12; kept, disclosed, never analysed):

| Plan id | Verdict | Usable | Window reasons | `harvest.json` sha256 |
|---|---|---|---|---|
| `v5-b5-alpha-a1-20261008T2201Z` | COLLECTED | no | `cell.below_minimum`, `neg8.bound_not_derived` | `c15f85f21b4d6b8a82cefaf0176291deafb4d009efbea37093c5806bf6eadc91` |
| `v5-b5-alpha-a2-20261009T0515Z` | NULL | no | `window.null` | `4564ea599b682c1e922dc090a42c01dd436f4c9e6bcb2c38e2271842ab4bd8a1` |
| `v5-b5-alpha-a3-20261009T0644Z` | COLLECTED | no | `neg8.bound_not_derived`, `neg8.screen_failed` | `e668781583da51efce7a7e7ef57fef8cbfab68b427acd40401dafc1529d4267e` |

Second seal (corpus of 18):

| Plan id | Verdict | Usable | Window reasons | `harvest.json` sha256 |
|---|---|---|---|---|
| `v5-b5-alpha-a1-20261009T2312Z` | COLLECTED | **yes** | none | `baf397d620845bbd92e6efa69646daafa5c731d552e568e7a4be6b72ac797ab5` |
| `v5-b5-beta-a1-20261010T0742Z` | COLLECTED | no | `neg8.screen_failed` | `f0d72323b67d075db29a5c136d087222284a6d4651d130549f9dbd5a82d6ec7d` |
| `v5-b5-beta-a2-20261010T1756Z` | COLLECTED | no | `calibration.no_bracket`, `cell.below_minimum`, `whole_window.verdict_absent` | `143ec4d5969f541d6829781c9076441412c21246dad67bcab54671150c77526f` |
| `v5-b5-beta-a3-20261010T2151Z` | NO_COLLECTION | no | `calibration.no_bracket`, `cell.below_minimum`, `neg8.bound_not_derived`, `roster.no_science_bundles`, `whole_window.verdict_absent` | `a95540c91cec31d47b8dff62956c3020b1901801b9d111e2ec4155231c45e0c1` |
| `v5-b5-beta-a4-20261010T2237Z` (re-harvest `-r2`) | COLLECTED | no | `calibration.bracket_acceptance_failed` | `b4aa474b1ebc4eefc0a8b5f4b9d6975544578113583d0da10fa410a9f139d5b6` |
| `v5-b5-beta-a5-20261011T0739Z` | COLLECTED | no | `calibration.bracket_acceptance_failed` | `8e69f3ef88b932a4b5e0f6a56816e2c1e45d5a64d19595bebf88c02f9a76170d` |
| `v5-b5-beta-a6-20261011T2011Z` | COLLECTED | **yes** | none | `80398a5deb1d55f19c13f8e4057debd296b8dbb30dfa4de914cacc11aa8a97fe` |
| `v5-b5-gamma-a1-20261012T0420Z` | COLLECTED | **yes** | none | `4bb49435f33d481b8404c9e5540ea515a4ba2910cc98316e34467d2424a8d1c7` |

The analysed windows: ALPHA `v5-b5-alpha-a1-20261009T2312Z`, BETA `v5-b5-beta-a6-20261011T2011Z`, GAMMA
`v5-b5-gamma-a1-20261012T0420Z`. Attempts: ALPHA 4 (three under the first seal, one under the second), BETA
6, GAMMA 1; eleven in all, eight not claim-usable. The plan `v5-b5-gamma-a1-20261012T0343Z` was withdrawn
before any notice or install and is not an attempt.

## Gates that ran this activation, and what each caught that touched a number

- The harvest (pinned program, 42 minutes): decided the window; removed 4 of 107 members from the succeeded
  count. Caught nothing that removes the window.
- RUN_STATE item 19's sleep check: 2,499 ns, nothing caught (third window in a row with nothing: BETA 5,
  BETA 6, GAMMA 1; it stays, since the one sleep it exists for was real and no registered check sees one).
- The harvest pin test and the desk-root commit check: passed, nothing caught.
- The END STATE count: `continue`, nothing caught.

## Next

Desk work only, in the order RUN_STATE gives: the analysis lanes (L9, L9-NEG8) and L9-BRACKET (item 27),
written blind before any release event; then item 22's lanes (b), (c), (d) and (a). No release event is
taken by a headless activation without the cold gate the registration names.
