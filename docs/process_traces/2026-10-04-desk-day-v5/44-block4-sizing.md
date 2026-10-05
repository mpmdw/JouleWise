# Record 44: block-4 sizing (how long `s1` may run, and the control deadlines)

2026-10-05, desk-day seat 2 (Opus 5.5), from the Sol sizing seat's derivation (brief 79) and the committed allowance
file `configs/campaigns/v5_qualification_25g83/sizing_allowances.json` on branch
`feat/2026-10-05-v5-qualification-code`. These are prospective protocol inputs for the plan writer, not measured
results. No `s1` byte is used. Durations come only from timing fields in block-1 to block-3 archives (permitted as
diagnostics after block 3) and from committed configs; no energy or power value is read or printed.

## What `s1` runs

The rendered one-block G2-b chain (`scripts/gen_g2_phase_d.py` after #474) runs, in order: reservation and start
authentication; pre settle; pre bracket and screen; the NEG-8 bound corpus (12 members); bound derivation; the start
reference triplet (3); the first science block, A/B/B/A (4 members: decode stage
`01_decode_contrast_blocks_01_05`, prompt 0, forced 512 output tokens); one midpoint reference; the end reference
triplet (3); the post bracket; the ratified physical-ahead STOP. That is 23 captured members and two calibration
captures, five campaign invocations and six 600-second settles. The science stage stops itself with rc 3
(`max_blocks_reached`); the chain checks that code and ends with rc 0. The full GAMMA graph's arm-boundary and
prefill-midpoint references are not dispatched, so they are not sized (addendum A).

The four science members (A1, B1, B2, A2) are the `b01` decode-contrast configs of the committed GAMMA pack:

| Position | Run id | Config SHA-256 |
|---|---|---|
| A1 | `d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-a1` | `7669e8e87e896529af2ba6f5cd01c7fcf911b4168180a3dc2a7343afc2e29558` |
| B1 | `d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-b1` | `07bc2083236fff5a7a6cfc62490d4c840c8c20c5d12216954882e03ace9b654c` |
| B2 | `d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-b2` | `0b9544fca27d382341e5978a07a7a3de90138dac8305a200846007ec9dabc868` |
| A2 | `d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-a2` | `82b7b8370e1ec402e393dbfb4fadd68c970a98e520095e1c8b91b27379b7c8cf` |

## The allowances

Each allowance in the committed file is `{seconds, source:{path, sha256}, source_pointer}`. Three kinds appear:
an observed maximum with a stated margin, a value derived from a committed config, or a config-derived proxy.

| Component | Seconds | How it is derived |
|---|---:|---|
| `T_pack_t0` | 360 | Three 120 s units for author, verify and consuming start (config-derived). Excludes the OFF dwell. |
| `T_fixed_settles` | 3700 | Six 600 s settles and five 20 s campaign countdowns (config). |
| `T_pre_post_calibration` | 770 | Two brackets of 240 s capture (observed maximum 196.8 s plus margin), 20 s countdown, 5 s pause and 120 s screen and allocation. |
| `T_bound_and_references` | 11365 | 19 auxiliary members at 595 s each plus 60 s bound derivation. **Proxy:** the auxiliaries run Qwen2.5-1.5B (1024 in, 256 out), and the archives hold no direct timing for it, so each is budgeted at the small science member's full envelope. |
| `E_small` | 595 | load 3, warmup 10, prefill 2, forced decode 5, cooldown 300, idle admission 275. |
| `E_large` | 619 | load 6, warmup 16, prefill 9, forced decode 13, cooldown 300, idle admission 275. |
| `T_stage_custody` | 2835 | Stage overhead, 23 reductions at 45 s (observed maximum 28.1 s plus margin), bracket writer custody, reservation. |
| `T_terminal_shutdown` | 300 | Reserve for the physical-ahead STOP and shell exit. |

Member terms: load, warmup, prefill and decode are observed stage maxima times 1.5, rounded up. Cooldown is the
production cap of 300 s. Idle admission is two 110 s attempts (observed maximum 103.6 s), three 15 s guards and a
10 s drift sentinel. Production retry backoff is 0 s; block 3's 300 s backoff is not imported. The post-STOP desk
step (two backups, close-out, OFF stand-down) is budgeted separately at 420 s and is not part of the quiet span.

## The arithmetic

```text
E_ABBA                      = 2·595 + 2·619                                   = 2428 s
NIGHT_PROGRAMMED_SPAN_S_s1  = 360 + 3700 + 770 + 11365 + 2428 + 2835 + 300    = 21758 s  (about 6 h 3 min)
WINDOW_MAX_S_s1             = 60·ceil((21758 + 2700)/60)                     = 24480 s  (6 h 48 min)
latest chain start          = t0 + 24480 − 21758                              = t0 + 2722 s
```

The 2700 s clean-dwell cap is added once, outside the programmed span; the dwell's 600 s minimum sits inside that
cap. From the driver's constants (`scripts/run_night.py`): emergency shutdown at `t0 + 24780`, courier deadline at
`t0 + 25080`, dead-man at the next whole minute after `t0 + 28380`.

## Clock design check (addendum A)

The binding rule is unchanged: every member's effective clock-anchor bound must be at most 5 ms at harvest. The
design check asks whether streams of this length plausibly meet it. On this machine, models and OS build, block 3's
SELECT re-harvest holds 50 anchor records, all `bounded`, the largest 4.02 ms. That passes, with a thin margin.

For transparency, the stacked worst case is 8.5 ms. It takes the largest observed anchor half-width (3.60 ms), the
largest drift rate seen in calibration captures (8 ppm, rounded up), and a 613 s stream that also counts the
cooldown, which actually runs on its own sampler. Those three worst cases never occur in one stream, so this number
is reported, not gated. If `s1`'s anchors come out unbounded, the registration's majority trigger ends the block.

## Control deadlines (`a1`, `a2`)

All from the controls' own receipts and boot, never a guessed delay (registration §4):

- ARM deadline: the earlier of 300 s after evaluation and every evidence deadline. The expiry check runs at the
  ARM deadline plus 1 ns and must see `readiness_record_expired`.
- Perishable evidence: volatile T-0 evidence lives 1200 s from its origin. The next occurrence's first T-0 capture
  starts after the latest of the control's ARM, GO and volatile-evidence deadlines.
- Caps after that point: absence check by +120 s, shutdown by +420 s, courier by +720 s, dead-man at the next whole
  minute after +4020 s.

Each control therefore costs its T-0 authoring time plus at most about 20 minutes, not the six-hour nonvolatile
horizon.
