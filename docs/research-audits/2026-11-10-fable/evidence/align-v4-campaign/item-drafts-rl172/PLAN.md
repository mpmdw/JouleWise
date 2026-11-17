# MBP chain under RL-171 and RL-172, Sun 15 Nov 00:20 to Wed 18 Nov

Repair note, 2026-11-16: these older unissued templates also received the recorded `ended.epoch_s` census fix. Use the RL-173/current 1115 forms for any issuance; this older chain and its captured tests are historical. New regression results are recorded with the F2 fix report. Historical plans, mock bundles and test captures remain unchanged.

Items builder. First draft Sat 14 Nov 23:51 to Sun 15 Nov 00:21 PST; revised for RL-172 and the Sol items review Sun 15 Nov 00:40-00:50 PST (from `date`). Nothing was issued, committed or pushed, there was no SSH, and RUN_STATE was not touched. No energy, power, meter-sample, powermetrics, transcript, slot or custody file was opened; plans and mocks are synthetic. The RL-172 revision is listed in `CHANGES-RL172.md`.

**The rules this chain applies.**
- **Retired (RL-171 §2):** the 01:30-02:40 quiet; fence end by 01:50 and worst case by 01:30; the fixed 02:40 starts; every "none between X and 02:40" line. A span arms as soon as its gates hold, at any hour.
- **The batch-window argument (RL-171 §3, corrected by RL-172 §0), one rule on every campaign pin:** `02:00-02:35` wherever the pin's own `plan` admits the t0, otherwise `13:14-13:15`. Each item's `pick_arg` holds its bands, every band end checked with the pinned `plan` (`plans/bands/verify-*.txt`).
- **Close interval (RL-171 §6.1; confirmed by RL-172 §0 and (d)):** 300 s after a campaign close; 1,200 s after F0, F2 or any other close (the restart included). A campaign arm also waits for the lead's journal-copy marker of the latest campaign close (Sol items-rl171 P1).
- **Day law (RL-172 (a)):** a day is the local date of a span's t0. At most 12 mixed-size development legs and at most 24 development legs per t0-date; qualification dates disjoint from development dates; hp-01, F0, F2 and v4 sessions outside the count; a span that misses its date is re-dated by the lead, never doubled up. Each item's window admits only its date, and `day_gate` counts the legs already launched that date from the receipts. **Dates: dev-01-s04 Sun; dev-02-s02 Sun; dev-02-s03 Mon; dev-03 Mon; dev-04 Tue; dev-05 Wed.** Legs per date: Sat 7, Sun 11, Mon 18 (12 mixed), Tue 12 (12 mixed), Wed 12 (12 mixed).
- **v4 sessions (RL-172 (f)):** from the lead's READY record nothing lower arms and the session takes the next clean close; RL-165 §7's worst-case reservation is retired.
- **The restart (RL-172 (h)):** Sun 14:08 (± 15 min) once dev-02-s02 has closed; no F0 after 12:00 until it is recorded done. Every arm record prints the next OS batch time from `kern.boottime` (boot + 12 h + 48 s).
- **Kept:** hp-01's worst-case end by 00:30; what the pinned bytes refuse; every other gate (host gate, line 2, line 7, line 9 desk-final, blinding).

## 1. What the pinned bytes still refuse (run on the Air; README §1 has the evidence)

| Pin | Used by | `02:00-02:35` admits | `13:14-13:15` admits | 10:50-13:15 |
|---|---|---|---|---|
| `b4b6aeb19` (v1) | dev-01-s04, dev-02 | 02:35 to 02:00 − W (5 legs 19:52:30; 6 legs 19:07:30; 12 legs 14:37:30) | 13:15 to 13:14 − W (5 legs 07:06:30; 6 legs 06:21:30; 12 legs 01:51:30) | not refused by `plan`; the soak path waits out 11:45-13:15 unbudgeted. Kept as no-launch |
| `dd206025a` (v1 launcher; no fence check) | hp-01 | 3 legs 21:22:30; 4 legs 20:37:30; 5 legs 19:52:30 | 3 legs 08:36:30; 4 legs 07:51:30; 5 legs 07:06:30 | as `b4b6aeb19` |
| `2d347f721` (v1.1) | dev-03, dev-04, dev-05, F2 | 02:35 to 01:50 − W − 1,460 (3 legs 20:48:10; 6 legs 18:33:10; 9 legs 16:18:10) | 13:15 to 13:04 − W − 1,460 (3 legs 08:02:10; 6 legs 05:47:10; 9 legs 03:32:10) | **refused by `fence_problems` under either argument** (10:50:00 admitted, 10:50:01 refused) |
| `c3f4bacd8` | F0 (standing) | soak_child refuses a soak start in (22:50:40, 02:35:00): launch 02:35:00-22:40:00 | n/a | no midday window at this pin |

## 2. The chain (expected case; `plans/chain.py`, every t0 planned with the pinned `plan` and the argument the item picks)

Gaps: 300 s after a campaign close, 1,200 s after F0, F2 or the restart; 20 min for the lead's hand-reads (hp-01 smoke, dev-03 pilot). F0: c3f4bacd8 window 02:35-22:40, t0 4 h apart, at most three a day. hp-01's worst cases end by Sun 13:45.

| # | Item | Span | Gate (short) | Forecast t0 (local / epoch) | Argument | Exp end | Worst end | Fence end |
|---|---|---|---|---|---|---|---|---|
| 0 | item 331 (issued) | dev-01-s04 (item 331) | issued; t0 00:20 forecast by the lead | Sun 00:20:00 / 1794730800 | `13:14-13:15` | Sun 02:56:45 | Sun 06:27:30 | Sun 06:51:50 |
| 1 | ITEM-hp01-s01 | hp-01-s01 smoke | s04 closed + Check; RL-155 §5.2; line 2; line 9 s03 desk | Sun 03:01:45 / 1794740505 | `02:00-02:35` | Sun 04:56:48 | Sun 07:39:15 | Sun 08:03:35 |
| 2 | (remainder item, not drafted) | hp-01-s02 | smoke hand-read + R9; s04 desk final; CI base+0 | Sun 05:16:48 / 1794748608 | `02:00-02:35` | Sun 07:32:42 | Sun 10:39:18 | Sun 11:03:38 |
| 3 | (remainder item, not drafted) | hp-01-s03 | s02 closed clean; smoke desk final | Sun 07:37:42 / 1794757062 | `02:00-02:35` | Sun 10:14:27 | Sun 13:45:12 | Sun 14:09:32 |
| 4 | ITEM-dev02-s02 | dev-02-s02 | append committed; RL-155 §3.3; line 9 hp-01-s02 desk; Sunday | Sun 10:19:27 / 1794766767 | `02:00-02:35` | Sun 13:17:03 | Sun 17:11:57 | Sun 17:36:17 |
| - | (host event) | RL-172 (h) restart at 14:08 (± 15 min), then the readback; no F0 after 12:00 until done | dev-02-s02 closed; lead's remote proof of a clean return | Sun 14:08:00 / 1794780480 | - | Sun 14:28:00 (assumed 20 min) | - | - |
| 5 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Sun 14:48:00 / 1794782880 | `(c3f4)` | Sun 16:46:54 | Sun 18:11:00 | dl t0 + 14,400 s |
| 6 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Sun 18:48:00 / 1794797280 | `(c3f4)` | Sun 20:46:54 | Sun 22:11:00 | dl t0 + 14,400 s |
| 7 | ITEM-dev02-s03 | dev-02-s03 | s02 checked; line 9 hp-01-s03 desk; Monday | Mon 00:00:00 / 1794816000 | `13:14-13:15` | Mon 02:57:36 | Mon 06:52:30 | Mon 07:16:50 |
| 8 | ITEM-dev03-pilot | dev-03-s01 pilot | READY+staged; dev-02 closed; line 9 dev-02-s02 desk; dated Monday | Mon 03:02:36 / 1794826956 | `02:00-02:35` | Mon 04:59:40 | Mon 07:40:06 | Mon 08:04:26 |
| 9 | ITEM-dev03-rest | dev-03-s02 rest (nine) | hand-read R9 + L002 released; append; line 9 dev-02-s03 desk; dated Monday | Mon 05:19:40 / 1794835180 | `02:00-02:35` | Mon 09:32:23 | Mon 14:27:10 | Mon 14:51:30 |
| 10 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Mon 09:37:23 / 1794850643 | `(c3f4)` | Mon 11:36:17 | Mon 13:00:23 | dl t0 + 14,400 s |
| 11 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Mon 13:37:23 / 1794865043 | `(c3f4)` | Mon 15:36:17 | Mon 17:00:23 | dl t0 + 14,400 s |
| 12 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Mon 17:37:23 / 1794879443 | `(c3f4)` | Mon 19:36:17 | Mon 21:00:23 | dl t0 + 14,400 s |
| 13 | ITEM-dev04-s01 | dev-04-s01 | delta ADMIT; Q6; line 9 dev-03 pilot desk; dated Tuesday | Tue 00:00:00 / 1794902400 | `13:14-13:15` | Tue 02:55:07 | Tue 06:52:30 | Tue 07:16:50 |
| 14 | ITEM-dev04-s02 | dev-04-s02 | L005 released or >=4 of dev-03's 5 consumers; line 9 dev-03 rest desk; Tuesday | Tue 03:00:07 / 1794913207 | `02:00-02:35` | Tue 06:21:18 | Tue 09:52:37 | Tue 10:16:57 |
| 15 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Tue 06:26:18 / 1794925578 | `(c3f4)` | Tue 08:25:12 | Tue 09:49:18 | dl t0 + 14,400 s |
| 16 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Tue 10:26:18 / 1794939978 | `(c3f4)` | Tue 12:25:12 | Tue 13:49:18 | dl t0 + 14,400 s |
| 17 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Tue 14:26:18 / 1794954378 | `(c3f4)` | Tue 16:25:12 | Tue 17:49:18 | dl t0 + 14,400 s |
| 18 | ITEM-dev05-s01 | dev-05-s01 | delta ADMIT; Q6; line 9 dev-04-s01 desk; dated Wednesday | Wed 00:00:00 / 1794988800 | `13:14-13:15` | Wed 03:14:40 | Wed 06:52:30 | Wed 07:16:50 |
| 19 | ITEM-dev05-s02 | dev-05-s02 | line 9 dev-04-s02 desk; Wednesday | Wed 03:19:40 / 1795000780 | `02:00-02:35` | Wed 06:21:18 | Wed 10:12:10 | Wed 10:36:30 |
| 20 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Wed 06:26:18 / 1795011978 | `(c3f4)` | Wed 08:25:12 | Wed 09:49:18 | dl t0 + 14,400 s |
| 21 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Wed 10:26:18 / 1795026378 | `(c3f4)` | Wed 12:25:12 | Wed 13:49:18 | dl t0 + 14,400 s |
| 22 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Wed 14:26:18 / 1795040778 | `(c3f4)` | Wed 16:25:12 | Wed 17:49:18 | dl t0 + 14,400 s |

**Development is complete at Wed 06:21:18** (RL-165 chain: Tue 09:16:18; RL-171 with no day law: Mon 23:02:29). RL-172 (a) accepts the extra day.

**Campaign-span numbering for line 9 (unchanged order):** 1 pilot, 2 dev-01-s03, 3 dev-01-s04, 4-6 hp-01, 7 dev-02-s02, 8 dev-02-s03, 9 dev-03 pilot, 10 dev-03 rest, 11-12 dev-04, 13-14 dev-05.

## 3. Saturation: MBP idle hours per day (Sun 00:00 to Thu 00:00, expected case, busy = t0 to expected close)

| Day | RL-165 chain | This plan (RL-171 + RL-172) | of which idle for day balance | of which the restart | Saved vs RL-165 | This plan + F2 if READY | of which idle for day balance |
|---|---|---|---|---|---|---|---|
| Sun | 10.34 | **7.67** | 5.24 | 1.52 | 2.67 | 5.60 | 3.17 |
| Mon | 9.29 | **8.93** | 8.43 | 0 | 0.36 | 4.80 | 4.30 |
| Tue | 14.45 | **11.78** | 11.62 | 0 | 2.67 | 9.72 | 9.55 |
| Wed | 18.05 | **11.78** | 0 | 0 | 6.27 | 11.78 | 0 |
| Total | 52.13 | **40.16** | 25.29 | 1.52 | **11.97** | 31.90 | 17.02 |

- **Idle for day balance** is idle inside a window where a READY counted span was held for its t0-date: Sun 14:48-24:00 (dev-02-s03 is dated Monday), Mon 09:37-24:00 (dev-04 is dated Tuesday) and Tue 06:26-24:00 (dev-05 is dated Wednesday). F0 fills part of each; its 4-h spacing and three-a-day cap stop it filling more; F2 fills more if READY.
- **The restart** (Sun 13:17-14:48: no F0 after 12:00, 14:08 restart, 20 min readback, 20 min after a non-campaign close) is 1.52 h, counted in Sunday's idle but not as day balance.
- Same READY set in all columns (counted spans, hp-01, standing F0). RL-171 with no day law would idle 51.3 h in total but end development Monday night with 42 development legs on Monday (`plans/chain-new-nodaybal.txt`), which RL-172 (a) rules out.
- Before development ends this plan idles 28.5 h of 78.4 h (25.3 h of it for day balance); with F2 20.2 h.
- F2 rows use the draft kit `f2-inst-01.v1.1` at `2d347f721` (expected 7,442 s, worst 11,250 s per 3-leg piece), with 1,200 s after every F0 or F2 close (Sol items-rl171 P2). F2 has no item in this set; READY is the lead's call.
- Sources: `plans/old-idle.txt`, `plans/chain-new*.txt` and `.json`.

## 4. Remaining idle gaps (this plan) and their causes

| Gap | Hours | Cause |
|---|---|---|
| Sun 00:00-00:20 | 0.33 | item 331 issue time (s04 at 00:20) |
| Sun 04:56-05:16 | 0.33 | the lead's desk: hp-01 smoke hand-read, s04 desk final, mirror append, CI base+0 |
| Sun 13:17-14:48 | 1.52 | **the RL-172 (h) restart**: no F0 after 12:00 until it is done, then 20 min after a non-campaign close |
| Sun 16:46-18:48 | 2.02 | **day balance** (dev-02-s03 dated Monday) with F0's 4-h spacing |
| Sun 20:46-Mon 00:00 | 3.22 | **day balance**; F0 cannot launch after 22:40 (c3f4 soak_child) |
| Mon 04:59-05:19 | 0.33 | the lead's desk: dev-03 pilot hand-read (R9 + smoke line, L002), append, dev-02-s03 desk final |
| Mon 11:36-13:37, 15:36-17:37 | 2 × 2.02 | **day balance** (dev-04 dated Tuesday) with F0's spacing |
| Mon 19:36-Tue 00:00 | 4.40 | **day balance**; F0's three-a-day cap |
| Tue 08:25-10:26, 12:25-14:26 | 2 × 2.02 | **day balance** (dev-05 dated Wednesday) with F0's spacing |
| Tue 16:25-Wed 00:00 | 7.58 | **day balance**; F0's cap |
| Wed 08:25-10:26, 12:25-14:26 | 2 × 2.02 | no READY counted kit; F0's spacing |
| Wed 16:25-Thu 00:00 | 7.58 | no READY kit: F0's cap; freeze 2, the look manifest, qualification kits (#794), ctl-01, the slot session and W1 are not READY (RL-172 (i) row 1: READY work is the limit) |

## 5. Slipped branches (RL-172 (a): a missed date is re-dated by the lead, never doubled up)

- **No Sunday pull** (dev-02-s02 misses Sunday): Monday runs `dev-02-s01` (twelve legs, not mixed) by ITEM-dev02-s03 with RAN=none: 12 + dev-03's 12 = 24 development legs, 12 mixed, inside both caps. Bands: `13:14-13:15` to 01:51:30, none 01:51:31-02:34:59, `02:00-02:35` 02:35-10:50 and 13:15-14:37:30, `13:14-13:15` after.
- **dev-03's remainder misses Monday:** the lead re-dates it. It cannot share Tuesday with dev-04 (9 + 12 mixed > 12), so dev-04 and dev-05 each move one date; `day_gate` refuses any doubled-up arm.
- **dev-04-s02 misses Tuesday:** re-dated; dev-05 moves with it if the two would share a date over 12 mixed legs.
- **L002 times out:** nothing span-shaped arms until the research lead rules (RL-165 §4).
- **dev-04's L005 times out:** dev-04-s02 arms only if dev-03 released at least four of its five consumers (RL-165 §4; RL-167); else dev-04's L007-L012 and dev-05 run own-shaped (new kits).
- **v4 session READY (RL-172 (f)):** it takes the next clean close; later blocks are re-dated, never doubled up.
- **The restart cannot be proven remotely:** it waits and goes to the research lead (RL-172 (h)); the chain then gains 1.5 h on Sunday.

## 6. Lead workload the chain assumes

| Time | What | If late |
|---|---|---|
| Before each campaign arm | Copy the latest campaign close's journals to the Air, hash-verify, then write `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok` (manifest sha256 + `date`) | the next campaign arm WAITs |
| Sun before 02:57 | Issue/stage ITEM-hp01-s01 (pmset sudo pre-read; alarm at t0 + 16,650 s) | the smoke waits |
| Sun 04:57-05:17 | Smoke hand-read; s04 desk final; hp-01 mirror append; CI base+0; issue hp-01-s02 | hp-01-s02 slides; after 10:50 it waits to 13:15 |
| Sun before 10:19 | dev-02 6 + 6 append committed; hp-01-s02 desk final; ITEM-dev02-s02 staged | the pull slides inside Sunday |
| Sun 13:17-14:28 | Remote proof of a clean return, the 14:08 restart, the readback (RL-172 (h)); record the host event | F0 stays held |
| Sun before 23:59 | dev-03 READY and staged; dev-04/05 queues committed | the pilot waits |
| Mon 05:00-05:20 | Pilot hand-read; dev-02-s03 desk final; dev-03 append; issue the rest | the rest slides |
| Each block close | Print the t0-date by cell by G0-role table (RL-172 (a)) | - |

## 7. Files

`STANDING-F0.md`, `ITEM-hp01-s01.md`, `ITEM-dev02-s02.md`, `ITEM-dev02-s03.md`, `ITEM-dev03-pilot.md`, `ITEM-dev03-rest.md`, `ITEM-dev04-s01.md`, `ITEM-dev04-s02.md`, `ITEM-dev05-s01.md`, `ITEM-dev05-s02.md`; `CHANGES-RL172.md`; `queue/`; `plans/` (chain, bands, plans); `probe/`; `mock/`; `tools/` (build: `build_hp01.py`, `build_dev02.py`, `build_dev03.py`, `build_dev0405.py`, `apply.py` + `edits_f0.py`, then `rl172.py`; `lint.py`).
