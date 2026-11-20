# R1 (align-r1-20261111T0208Z) step_30b G0 timeout: magistrate diagnosis

Magistrate activation 5515349e (Opus 5.5, headless), 2026-11-10 19:20 PST.
Answers RUN_STATE item 253 (1). Read only thermal and structural records; no
R1 calibration value was read or used.

Custody `S=/Users/edr/night-align/r1-20261111T014106Z`; measurement root
`M=/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2`
at `20e9edbc4`. Step run dir
`R=$S/night/align-r1/step_30b/runs/align-v4-r1-step-30b`.

## What the gate requires (M `joulewise/align/apple/thermal_gates.py` `wait`, G0)

Ten consecutive 1 Hz samples with all of:
- fast sensor TV0h <= reference.fast_c + delta_fast_c (34.011 + 1.0 = 35.011 C);
- slow sensor Tf08 <= reference.slow_c + delta_slow_c (25.489 + 1.0 = 26.489 C);
- |slow slope| <= 0.2 C/min; os_level 0; pm_state Nominal, observed within 2 s.
Cap: 600 s (`g0_cap_s` default). Reference = `$S/night/align-r1/soak_reference.json`,
the mean of the last 1200 s of the chain's `idle_soak` segment (18:26:52-18:46:52).

## What happened (from `$R/outputs/align_thermal.jsonl`, `$R/events.jsonl`)

| time (PST) | phase | TV0h C | Tf08 C |
|---|---|---|---|
| 18:16-18:46 | idle_soak (no runtime process, no powermetrics) | 34.00-34.04 | 25.39-25.67, mean 25.489 |
| 18:46:54 | step starts (validate, prepare 10.7 s) | 33.79 | 26.40 |
| 18:47:18 | after prepare | 34.33 | 27.64 |
| 18:48:30-18:53:15 | step idle_baseline (model resident, powermetrics running) | 34.10-34.14 | mean 26.603, min 26.34, max 27.05 (286 samples) |
| 18:53:40-18:54:08 | warmup (one 5 s run) | up to 50.9 | up to 58.3 |
| 18:54:10-19:04:10 | G0 wait, 600 s, timeout | 34.28 at end (passes) | 28.42 at end (fails by 1.93) |

- TV0h passed throughout the tail. Tf08 is the only failing condition; slope and
  status conditions were met at the end (exit slope -0.039 C/min, Nominal).
- Single-exponential fit to the last 310 s of the G0 tail (18:59:00-19:04:10):
  asymptote 27.34 C, tau 312 s, rmse 0.078 C. The fitted asymptote is above the
  26.489 C limit, so on this fit a longer cap would not have released either.
- **Before any model work**, the step's own idle state already read Tf08 0.11 C
  above the limit on average (mean 26.603 vs 26.489), and above it for most samples.

## Diagnosis

Structural, not operational. The G0 reference comes from a soak that has no
runtime process, no resident 30B model and no powermetrics capture (writing
`raw/powermetrics.plist` at about 250 KB/s; 255 MB over 17 min). The member's own
idle state sits about 1.1 C warmer on Tf08 than that reference, which is already
past the +1.0 C allowance. No external load, residual heat or ambient change is
visible: the soak was flat (slope 0.0043 C/min, detrended sd 0.078 C).
Hypothesis, not proven: Tf08 may be near storage, and capture writes keep it warm.

A plain re-arm would very likely time out the same way. Any remedy changes the
G0 reference, its allowance or its cap, or the soak conditions: a design change
under item 253 (3), routed to the Fable 5.2 research lead before any re-arm.
