# Record 44: block-4 sizing (how long `s1` may run, and the control deadlines)

2026-10-05. First written by desk-day seat 2 (Opus 5.5) from the Sol sizing seat's derivation (brief 79).
Recomputed by seat 3 for idle 75 s and ruling 76 addendum E, from sizing round 2 (brief 124) and lane X10
(brief 127). These are prospective protocol inputs for the plan writer, not measured results.

Sources:
- Derivation: `configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json`. It names every
  block-1 to block-3 archive file it drew a duration from (67 timing sources), with path and SHA-256, and the 23
  regenerated configs.
- Allowances: `configs/campaigns/v5_qualification_25g83/sizing_allowances.json` (70 source-bound allowances).

Both files are on the block-4 code branch; their digests at H are in the sealed file inventory. Until round 2 every
allowance pointed at a test fixture; production allowances now point at the derivation. No `s1` byte is used. Only
timing fields were read from the archives (permitted as diagnostics after block 3); no energy or power value was
read or printed.

## What `s1` runs

At t0 the driver first runs the native six-step T-0 stage:
1. clock reference;
2. clock disable (the network-time OFF receipt);
3. quiet-Mac preparation;
4. the one clean dwell (at least 600 s, capped at 2700 s);
5. ledger readiness;
6. the ledger reservation.

Then ARM and the chain. The rendered one-block G2-b chain (`scripts/gen_g2_phase_d.py` after #474) runs, in
order:
- reservation and start authentication;
- the pre settle, then the pre bracket and screen;
- the NEG-8 bound corpus (12 members), then bound derivation;
- the start reference triplet (3);
- the first science block, A/B/B/A (4 members: decode stage `01_decode_contrast_blocks_01_05`, prompt 0, forced
  512 output tokens);
- one midpoint reference, then the end reference triplet (3);
- the post bracket;
- the ratified physical-ahead STOP.

That is 23 captured members and two calibration captures, five campaign invocations and six 600-second settles.
The science stage stops itself with rc 3 (`max_blocks_reached`); the chain checks that code and ends with rc 0.

The four science members are the `b01` decode-contrast configs of the GAMMA pack as regenerated at idle 75 s by
#481. Their run ids and config digests are in the derivation (`/members`) and in `FILL[S1-ROSTER]`.

## Two different durations: a member's envelope and a sampler stream

A member's **envelope** is everything the chain spends on it:
- model load (before the sampler starts);
- sampler start-up, idle admission (including the policy's one retry and its guards), warmup, prefill and forced
  decode;
- sampler wind-down;
- a cooldown of up to 300 s.

The cooldown runs on a separate sampler: the main sampler stops at `joulewise/controller.py:1607`, before cooldown
begins.

A **sampler stream** is one continuous powermetrics capture. Its length matters because the clock anchor is fitted
across it, and two limits apply:
- below 60 s the anchor fit refuses (`clock_fit_span_insufficient`, memo 1.8);
- the longer the stream, the further the clock drifts across it, and the frequency gate (below) bounds that drift.

So the envelope sizes the window, and the stream sizes the clock check.

## The allowances

| Component | Seconds | Derivation |
|---|---:|---|
| Load, small / large | 3 / 6 | Observed maximum × 1.5, rounded up |
| Warmup, small / large | 10 / 16 | Observed maximum × 1.5, rounded up |
| Prefill, small / large | 2 / 9 | Conservative proxy: the observed timing at a 4096-token prompt, at least as long as the issued prefill length |
| Forced decode, small / large | 5 / 13 | Observed 512-token maximum × 1.5, plus 1 s |
| Idle admission | 275 | Two attempts of 110 s (largest observed at idle 75 s: 103.6 s), three 15 s guards, a 10 s drift sentinel |
| Sampler start-up / wind-down | 15 / 17 | Production readiness timeout; stop, flush and sentinel |
| Cooldown | 300 | Production cap (separate sampler) |
| **`E_small`**, **`E_large`** (full envelope) | **627**, **651** | Sum of the rows above |
| Each auxiliary member (NEG-8, references) | 627 | Proxy: budgeted at the small member's envelope, because the archives hold no timing for the auxiliary model |
| `T_bound_and_references` | 11973 | 19 × 627 + 60 s bound derivation |
| `T_pack_t0` | 360 | Author, verification and consuming start after the T-0 stage |
| `T_fixed_settles` | 3700 | Six 600 s settles and five 20 s campaign countdowns |
| `T_pre_post_calibration` | 770 | Two brackets of 240 s capture (observed maximum 196.8 s plus margin), 20 s countdown, 5 s pause, 120 s screen and allocation |
| `T_stage_custody` | 2835 | Stage overhead, 23 reductions at 45 s (observed maximum 28.1 s plus margin), bracket writer custody, reservation |
| `T_terminal_shutdown` | 300 | The physical-ahead STOP and shell exit |
| **`T0_STAGE_CAP_S`** | **3300** | The 2700 s dwell cap plus 600 s for the other five steps and the OFF margin; the writer accepts 3180-3480 s |

The plan writer's file charges the 32 s of sampler start-up and wind-down per member through its custody field
(2835 + 23 × 32 = 3571 s) rather than per member. The two accounts give the same total; the 32 s is counted once.

The idle admission term did not change with regeneration. Record 44's first version already drew it from block 3,
which ran at idle 75 s. The regenerated configs request 750 records: in 40 comparable block-3 idle slices that took
97.7-100.3 s.

## The arithmetic

```text
E_ABBA                     = 2·627 + 2·651                                  = 2556 s
NIGHT_PROGRAMMED_SPAN_S_s1 = 360 + 3700 + 770 + 11973 + 2556 + 2835 + 300   = 22494 s   (6 h 15 min)
WINDOW_MAX_S_s1            = 60·ceil((22494 + 3300)/60)                     = 25800 s   (7 h 10 min)
latest chain start         = t0 + 25800 − 22494                             = t0 + 3306 s
emergency shutdown         = t0 + 26100 s
courier deadline           = t0 + 26400 s
dead-man                   = next whole minute after t0 + 29700 s
```

The T-0 stage sits outside the programmed span and is added once (addendum E). The earlier version counted a
360 s T-0 inside the span and added the 2700 s dwell cap outside it. That left the latest chain start at t0 + 2722 s,
earlier than a long dwell could finish. G4's 600-3600 s T-0 span holds by construction: R0 opens the stage, and
authoring follows within 3300 + 120 s.

## Stream lengths and the clock

| Stream | Seconds | Derivation |
|---|---:|---|
| Small science member, each auxiliary member | 314 | 15 + (275 − 10) + 10 + 2 + 5 + 17 |
| Large science member (**`T_stream_max`**) | 335 | 15 + (275 − 10) + 16 + 9 + 13 + 17 |
| Each bracket | 240 | Observed maximum 196.8 s plus margin |

Every anchor-bearing stream is at least 60 s by allowance, and the writer refuses a shorter one. Helper captures
that carry no anchor (cooldown subwindows, the post-run sentinel) are exempt.

**Frequency gate** (registration §4). With network time OFF the clock drifts at the kernel's stored frequency
correction `f`. The occurrence arms only if

```text
H_max + 0.10 ms + (|f| + 0.25 ppm) · T_stream_max ≤ 5 ms
3.60 ms + 0.10 ms + (3.17 + 0.25) ppm · 335 s = 3.70 ms + 1.146 ms = 4.846 ms ≤ 5 ms
```

That holds at today's −3.17 ppm, with 0.154 ms to spare. The largest |f| that passes is about 3.63 ppm. Under the
first version's 613 s stream, which wrongly counted the cooldown, the same gate failed (X3 finding F2).

**Clock design check (addendum A).** The binding rule is unchanged: every member's effective clock-anchor bound
must be at most 5 ms at harvest. On this machine, models and OS build, block 3's SELECT re-harvest holds 50 anchor
records from streams of comparable length (idle 75 s). All are `bounded`, and the largest is 4.02 ms. The margin is
thin and is disclosed to the cold gate. If `s1`'s anchors come out unbounded, the registration's majority trigger
ends the block.

## Control deadlines (`a1`, `a2`)

All deadlines come from the controls' own receipts and boot, never from a guessed delay (registration §4):

- **ARM deadline:** the earlier of 300 s after evaluation and every evidence deadline. The expiry check runs at
  the ARM deadline plus 1 ns and must see `readiness_record_expired`.
- **Perishable evidence:** volatile T-0 evidence lives 1200 s from its origin. The next occurrence's T-0 stage
  starts only after the latest of the control's ARM, GO and volatile-evidence deadlines.
- **Caps after that point:**
  - absence check by +120 s;
  - shutdown by +420 s;
  - courier by +720 s;
  - dead-man at the next whole minute after +4020 s.

So each control costs its T-0 stage plus at most about 20 minutes, not the six-hour nonvolatile horizon. G10 then
waits for its offset band: about two hours after `a1`'s resync at today's drift rate (registration §5).
