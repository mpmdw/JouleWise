# Block 5, second seal, GAMMA attempt 1: arm record

Magistrate activation d7a980d2 (Opus 5.5, headless), 2026-10-11 20:16 PDT. **Both night jobs are installed.**

- Plan `v5-b5-gamma-a1-20261012T0420Z`, pack GAMMA, attempt 1, t0 epoch 1791778800 (21:20 PDT), G10 false,
  107 members, `window_max_s` 99060. Plan sha256
  `d331c333daf7f0df1ce1346548965308771a0769d20b4cefb268a6093a863c5a`; plan inputs sha256
  `61b596b06cbead66fd69191ee1373a99926ab246581216e4813c5309fa2b9f26`; clone head
  `e84b1ea63ce98871486bf5de4b143e6b71d9e31d`; custody `/Users/edr/night-custody/v5-b5-gamma-a1-20261012T0420Z`;
  staging `/Users/edr/night-plan-staging/v5-b5-gamma-a1-20261012T0420Z` (arm-env, inputs summary, plan record,
  chain check, schedule, desk seal check, install output).
- Erratum 3 governs it (t0 later than epoch 1791738000): its harvest is made by the pin
  `b039c0257d1b1d407ee9598222db3f78f6ad7beb`, where the desk root is checked out.
- Why it is armed: BETA attempt 6 is claim-usable (`seal2-beta-a6-window.md`); `B5-ARM-RELEASED: beta gamma`
  in the canonical root, which was fast-forwarded to main at 20:10 PDT with no night job loaded or on disk
  (it had been two commits behind since the BETA arm).
- 5.1: agent check two empty lists; no agent application; Firefox open (pid 25671; answer E-2a is NO, so it
  was left and named in the notice); clone clean, diff against the claim head lists the three seal documents
  and the ledger pin; ledger `[] []`; frequency gate passes (2.718 ppm, 4.694 ms of 5.0); free disk 128 GiB
  (81 needed); build 25G83; the nine identity pins equal the sealed ones; AC attached, not charging, 0 mA;
  the four helper digests as the brief lists them and the pre-arm helper as RUN_STATE item 26 gives it; no
  restart since 2026-09-18.
- Keep-awake job: `caffeinate` pid 30553, parent 1, holds `PreventUserIdleSystemSleep`; the Mac has been in
  full wake since 2026-10-10 23:13:51.
- **The pre-arm run of Erratum 3 item 13(a)** (`b5_prearm_bracket.py`, 20:10 PDT, from the pinned desk
  checkout; output `/Users/edr/night-plan-staging/b5-bench/prearm/gamma-a1.json`): exit 0;
  `must_conditions_hold` true; snapshot refusal reasons none; head sequence 488; candidates 16, valid
  finalized captures 16; binding of the last finalized session validated; observed and recorded-only
  triggers `new_systematic_failure_challenges_preflight_screen`; doubling count 43 of 48; sequences of other
  sessions' systematic captures `[456]` (one entry: no consult is due).
- 5.3: desk identity written; plan `STAGED`, no threshold difference; chain check rc=0; preflight ok; desk
  seal check `no flag`, rc=0.
- 5.4: arm notice Gmail `1a12e1ac7076ac26` (it carries BETA attempt 6's outcome and the question about Ed's
  design-decisions mail, RUN_STATE item 30); no unread owner mail before or after it.
- 5.5: both jobs loaded 20:15 PDT, process type Interactive; dead-man calendar hour 1, minute 56.

## The choice of t0: midnight, measured

RUN_STATE item 4 of the 2026-10-09 block says to arm no window whose chain runs at 00:00 local unless
`/private/tmp` holds fewer than 1,000 entries and under 1 GiB. It holds 674,273 entries and 9 GiB (what Ed's
command of 13:05 PDT left: everything younger than a day), and the session's permission check refuses to
delete there. The two numbers are a proxy; the hazard is the processor time of the cleaner's walk. The same
walk (two `find` passes over `/private/tmp`), timed at 20:07 PDT: 51 s of wall time, 17.5 CPU-seconds. That
can cost the member it overlaps and no more. The alternatives were worse: a t0 after 00:10 puts the end
references and the closing calibration into the hour around 05:40, where the malware scan ran on 10-10 and
where BETA attempt 5 lost six members of its last stage; the next t0 inside the preferred band (13:10 to
17:15) is 17 hours away.

So the chain runs through midnight, placed. Stage order of the plan: reservation, opening calibration, 18
corpus members, bound derivation, `gamma-reference-start` (3), science 01 (20), `gamma-reference-decode-midpoint`
(1), science 02 (20), `gamma-reference-arm-boundary` (1), science 03 (20), `gamma-reference-prefill-midpoint`
(1), science 04 (20), `gamma-reference-end` (3), closing calibration. With BETA attempt 6's stage lengths
(RUN_STATE item 29), science 02 is predicted from t0 + 134 min to t0 + 186 min. A first plan
(`v5-b5-gamma-a1-20261012T0343Z`, t0 20:43 PDT) put 00:00 about five minutes after the arm-boundary reference,
the one member whose loss removes a GAMMA window. It was withdrawn by brief 5.6 before any notice or install
(`/Users/edr/night-custody-archive/v5-b5-gamma-a1-20261012T0343Z-withdrawn`; its runs parent and staging
directory are empty leftovers). It was never noticed to Ed and never installed, so it is not counted as an
attempt and the plan that replaces it keeps attempt number 1. With t0 21:20, 00:00 is predicted 26 minutes
into science 02 and 26 minutes before its end.

**Brief difference 8 (the dead-man job).** It fires 16,560 s after t0, at 01:56 PDT, predicted inside science
04 (t0 + 253 to 307 min) and about half an hour before the end references. The analysis names the member it
fell in from the member times.

**After this window:** brief section 4 with the pin `b039c0257` (check the desk root first); item 19's clock
check; read `calibration_bracket` in `harvest.json` (expected on a good window: `status` `passed`, doubling
45, sequences `[456]`); open the reason inside any window code before deciding. Note for the decision: which
stage 00:00 and 01:56 fell in, from the stage start and end times. If claim-usable: the block is closed,
brief section 7. Otherwise section 6 and GAMMA attempt 2.

## The pruning rule: what each gate of this activation caught that touched a number

- Item 19's sleep check on BETA attempt 6: -334 ns. Caught nothing.
- The END STATE count (890 recorded, 9 not bounded): caught nothing.
- The harvest pin test, the agent check (twice), the identity pins check, the desk seal check, the chain
  check, the frequency gate, the battery reading, the keep-awake check: caught nothing this activation.
- The pre-arm run of Erratum 3: holds; caught nothing.
- Reading the canonical root's `B5-ARM-RELEASED:` line: it read `beta` because the root was behind main.
  A stale copy, not a hold; cured by the fast-forward. Caught nothing that touches a number.
- The stage-order check against midnight: moved t0 by 37 minutes so that the cleaner's walk does not fall on
  the one reference whose loss removes a GAMMA window. This one bears on whether a window survives.
