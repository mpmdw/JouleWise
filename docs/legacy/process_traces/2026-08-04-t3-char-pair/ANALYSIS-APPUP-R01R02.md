# T3-CHAR-PAIR-01 — app-UP arm desk analysis (r01 + r02) — NON-CLAIM

Analyzed 2026-08-07 per PROTOCOL.md §Analysis. **NON-CLAIM, permanently**
(protocol limitation 3). n=2 of the planned n=3 (r03 died mid-capture and
was never re-run; between-capture agreement below makes the pair already
informative). Analysis script: `analysis_appup_r01r02.py` (this directory);
input: `rich_telemetry_idle.jsonl` (3000 frames each, ~10 Hz, ~360 s).

## Per-capture package power (processor_combined_power_w)

| capture | n | duration | mean | p95 | SD | min | max |
|---|---|---|---|---|---|---|---|
| r01 (~01:59) | 3000 | 362.3 s | 0.1929 W | 0.484 W | 0.383 W | 0.046 W | 7.47 W |
| r02 (~06:1x) | 3000 | 360.3 s | 0.1917 W | 0.463 W | 0.376 W | 0.046 W | 6.74 W |

Arm A (app-UP) mean of capture means: **0.1923 W**; between-capture SD
**0.0008 W** (the two captures, hours apart, agree to ~0.4%). GPU is fully
idle in both (idle ratio ≥0.997, ~0.6–0.8 mW). Distribution is heavily
right-skewed (SD ≈ 2× mean): the floor is a low base with sparse multi-watt
bursts (max 6.7–7.5 W single frames) even with everything dormant.

**Cross-check:** the pipeline's own `idle_baseline` block computed
independently at capture time agrees (r01 0.1925 W / r02 0.1903 W;
`idle_window_suspect: false` both; the ≤1% delta vs this script is
sample-weighting). `rail_sum_power_w` matches package power to ≤9.3 µW.

## What this answers (and what it cannot)

Ed's live question (2026-08-06 checkpoint): what does the resident-but-
dormant t3 stack actually cost a measurement window?

- **Upper bound on the dormant stack's steady cost:** the ENTIRE machine
  floor with t3 resident+dormant (+ an idle agent session, limitation 1)
  is ~0.19 W. The dormant t3 stack's steady contribution is strictly less
  than that. Over a 300 s member that is ≤ ~58 J gross — large against the
  ~5 J effective bar (D-078 cl.11) as a gross number, but the steady part
  is exactly what idle subtraction cancels.
- **The non-cancelling part is the bursts:** p95−mean ≈ 0.27–0.29 W, with
  single-frame excursions to ~7.5 W. Against a ~5 J effective bar, an
  asymmetric burst budget of only ~18 s at the p95−mean band (or ~0.7 s at
  the max burst rate) inside one member consumes the whole margin. Burst
  asymmetry between measure and baseline phases is precisely what the
  null-member screen exists to catch — and this floor's burstiness is
  present even fully dormant.
- **The t3 DELTA remains unmeasured.** Arm B (app-DOWN) was deliberately
  never collected (needs Ed present). This pair bounds the app-UP floor
  and proves its night-scale reproducibility (0.0008 W); it cannot
  attribute any of it to t3 vs the OS baseline.
- **An ACTIVE agent session is a different regime entirely:** D-099 puts
  an idle-waiting agent session at 12–18% CPU of agent load; active
  streaming is watts, not tenths — hundreds of joules per member, ~two
  orders of magnitude over the effective bar, and bursty (non-cancelling).
  The zero-agent rule for CLAIM windows is doing real work; the cheap
  concession this data supports is at most "resident-and-dormant", and
  even that awaits the arm-B delta plus a gate (protocol limitation 4).

## Status

Arm A analysis banked (this file). Remaining if the pair is ever completed:
r03 re-capture (config `configs/characterization/char-t3appup-r03.json`),
arm B with Ed present, between-arm difference + CI per the protocol.
