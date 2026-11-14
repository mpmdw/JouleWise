# RL-145 close §8 Part C smoke: Check by magistrate 3b6187a1 (2026-11-13 23:27 PST, RUN_STATE item 316)

Item 315's "Check" block, run after the desk fence was gone. The magistrate reports; it decides nothing. Nothing is re-run. Nothing from OUT is committed.

- OUT: `/Users/edr/code/jw-wt/r1-followup-smoke/.desk/r1-partc-smoke-20261114T052520Z` (smoke commit `f006b7aa665280253db10d7a167599ff385fcec4`).
- Span: launch 21:26:16 PST (epoch 1794633976); `runner_receipt.json` written 23:25:17 PST; the watchdog left FENCED at 23:27:20. **00:00 did not fall inside the span.**
- Agent census during the run: 237 `pgrep [c]odex|[c]laude` censuses in `censuses.jsonl`, all exit 1 (no agent).

## Receipt

```
{"error": "StepFailed: 1", "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 1}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 1), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 decfc428c1f119e5bad4ffd9487207cf6de4ecc2df1549d71ea33ab1d88a78bb
part-C 1 StepFailed: 1
RECEIPT OK
```

Receipt rc 1 with an `evaluation` present: a completed run (item 315's expected shape). Every feed proven stopped and hash-checked; one `close-volumes`.

part-C stderr ends: `ValueError: Part C failed (start_state_failed): Start state fails: the no-hold design fails in Automatic. It is not re-run. It goes to the research lead with the table.`

## Soak

rc 0; `soak_reference.json` sha256 `decfc428c1f119e5bad4ffd9487207cf6de4ecc2df1549d71ea33ab1d88a78bb`; window 1,200 s, 1,200 reads each.

| Sensor | mean °C | detrended sd °C | slope °C/min | settled |
|---|---|---|---|---|
| TV0h (s_fast) | 34.25713315010071 | 0.012371831672167422 | -0.007252826623453225 | true |
| TV1h (s_slow) | 34.25713315010071 | 0.012371831672167422 | -0.007252826623453225 | true |

The two bands are identical to every printed digit (for the lead's close §5 TV1h ≠ TV0h check; step-D's `over_reference_c` is also identical, fast 0.27482 = slow 0.27482).

## smoke_part_c.json (blinded print only: evaluation, N_chunk, T_dead)

- `verdict`: `start_state_failed`; `pass`: false; `slots_entered`: false; schema `joulewise.align.r1_part_c.v1`; authority "RL-145 step 3; RL-145 addendum section 6".
- `disposition` as printed: "Start state fails: the no-hold design fails in Automatic. It is not re-run. It goes to the research lead with the table." **This text is superseded** (item 315): it predates the close; the result goes to the research lead with the lead's desk table, and the verdict decides nothing.
- **N_chunk** 4,096. **T_dead** 983.1011242875009 s.
- Lines:
  - `step_d`: pass true; G0 wait 209.020538292 s; slope -0.15938308102583387 °C/min; over reference fast 0.27482032775878906 °C, slow 0.27482032775878906 °C; reasons [].
  - `d_bank_mechanics`: pass false.
    - `admitted_turns`: value 2, need 3, pass false.
    - `gate_time`: gates + holds 210.594729394 s, limit 393.24044971500035 s, share of T_dead 0.21421471727705307, pass true.
    - `h_records`: pass true (turn 0: 103 decode tokens, expected [] = actual []; turn 1: 4,096 decode tokens, [] = []).
    - `no_g1_timeout`: pass true (no turns). `no_x7`: pass true (x7 false).
  - `d_bank_start_state`: pass false, reasons []. Four samples, each `ok` false with `os_level` null and `pm_state` null: "G0 release", "G1 release (turn 1)", "first reading after turn 0 start", "first reading after turn 1 start".
  - `x_g`: pass true; no G1 timeout turns; x7 false. **X_G ran.**
- `log`: [] (empty).
- `printed_not_judged`:
  - predicted (as printed): "D_bank turn 1 (11,211 prefill tokens and a long decode): OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98. Printed beside the measurement; no verdict reads it."
  - Turn 0: 103 decode tokens; start state os_level 0 / pm Nominal; decode os level share {0: 1.0}; pm share {Nominal: 1.0}; readings os 9, pm 71; base clock 1,315.31 MHz; one partial block clock ratio 0.99435; last-512 ratios null; first_off null; token basis `uniform_estimate`.
  - Turn 1: 4,096 decode tokens; start state os_level 0 / pm Nominal; decode os level share {0: 0.2982, 1: 0.0702, 2: 0.6316}; pm share {Nominal: 0.2985, Moderate: 0.0700, Heavy: 0.6315}; readings os 342, pm 2,985; base clock 1,380.0 MHz; clock ratio by 256-token block ≥ 0.9999 through token 2,048, then 0.99696, 0.98438, 0.95273, 0.93057, 0.91103, 0.89538, 0.87652, 0.87373; **last-512 clock ratio 0.8751257385725489**; token-rate ratio last-512 null; first_off: pm Moderate (os_level null) at token 1,223, 102.07 s after first token, 162.67 s after turn start, not in prefill; token basis `uniform_estimate`.

## For the lead (observations, not rulings)

1. The `start_state_failed` verdict rests on four samples whose `os_level` and `pm_state` are both null, with an empty `reasons` list, while `printed_not_judged` records each turn's start state as os_level 0 / Nominal. The null samples may be the sampler's lookup or the 2 s stamp rule rather than an observed non-Automatic state; the journals decide.
2. TV0h and TV1h read identically through the soak and at step-D (close §5 trigger; rows 1-3's alias-pair confirmation).
3. Beside the research lead's close §8 predictions (no bar): step-D G0 released in 209.0 s (predicted 100-220 s); D_bank turn 1 left Nominal at token 1,223 (predicted before 2,048); last-512 clock ratio 0.875 (predicted 0.83-0.93); gates + holds 210.6 s (prediction named > 398.3 s or a deadman stop as the mechanics failure; neither happened, but 2 of 3 turns were admitted); X_G passed (predicted).

## Restore lines (read 23:3x PST, item 316)

- Desk fence gone; `com.joulewise.align-r0` agents loaded: 0; launch plist `r0-launches/ed97ee345ac44ed496b24ffc2c0549fd` `ProcessType => Interactive`.
- AC power, battery 100% charged; `powermode 0`.
- Network Time: Off.
- Kernel frequency word (`joulewise.hazards.clock.read_frequency`, ntp_adjtime modes 0): `raw_word 0`, 0.0 ppm, status 8321 (0x2081).
- No stray monitor; no root powermetrics; no High Power marker.

No unread mail from Ed; directives are the standing #587, #422, #421, #417, #416, #408, #405. No Codex child started. Nothing armed.
