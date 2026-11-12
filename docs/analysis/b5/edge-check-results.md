# Block 5 cross-instrument edge check: results

**Exploratory, derived after release.** Not registered; mints no claim; changes no registered number or sentence.
Run 2026-11-12 on the Air by an Opus 5.5 seat, following `docs/analysis/b5/edge-check-reading-rule.md` literally.

| Item | Value |
|---|---|
| Rule | `docs/analysis/b5/edge-check-reading-rule.md`, rule commit `7e1d4278c` (file SHA-256 `c9afe7bf…08b47`) |
| Script, pre-run commit | `56cf90719` (committed before any run on real data; only the synthetic selftest had run) |
| Script, reported run | `7d3724b70` (fix 1, label only; `DEVIATION-LOG.md` DLE-11) |
| Seed; resamples | 20261112; 2,000 |
| Data | `night-archive/harvest-v5-b5-{alpha-a1-20261009T2312Z, beta-a6-20261011T2011Z, gamma-a1-20261012T0420Z}` (kept runs, their calibration capture, `derived/{exclusions,roster}.json`, `withheld/bracket-evaluation.json`, the meter `stream-001.jsonl`); b and the kept-unit cross-check from `jw-b5-custody/release-check-final-20261108T0942Z/recompute.json` (RC). Nothing else opened. |
| Per-edge output | `edges.json`, SHA-256 `8dc61055975331e54c04362c5c78fb2aa3acbca5bf52b654513a5c14347cb07f` (identical in both runs; kept outside the repo at `/Volumes/JW-EXT/tmp/b5-edge-check/run2/`) |
| Script wall time | 11.5 s (run 2), 11.9 s (run 1). Whole task, rule read to PR: about 15 minutes. |

Reproduce: `python3.13 scripts/b5_edge_check.py --out "$TMPDIR/b5-edge-check"` (selftest only: `--selftest`).

## Outcome sentence (rule §1, chosen by the wording logic, interpretation I11)

> An exploratory cross-instrument check on released data found no pulse-to-inference difference in edge placement
> larger than the timing bound (T = +1.8 ms, 95% interval [-3.0, +14.8] ms, for rises, -5.6 ms, 95% interval
> [-7.5, -1.9] ms, for falls).

> Standing caveat: the meter reads whole-machine DC input, whose lag behind rail power may depend on step size and
> shape, so T mixes sampler placement with that path difference. The meter is not ground truth.

Per the rule: the first row does not validate the bound (b limits each edge, T compares typical placement). §9 keeps
the limitation, with "untested" becoming "not tested by a registered experiment".

**Read the intervals with this in mind (consequence of I2, not a choice made after looking).** Every kept run in a
session carries the same, byte-identical calibration capture. Resampling whole runs therefore always brings the same
59 pulses, so the pulse median is fixed in every resample. The 95% intervals carry the inference-edge sampling
variability only, not the uncertainty of the pulse median.

## Assumption checks flagged by the rule's author

- **(a) Long flat 2,048-token prefill: fails for Qwen3-1.7B.** The 1.7B prefill lasts 607–635 ms (ALPHA, n 41; GAMMA
  1.7B arm, n 10), shorter than the +800 ms window, so the prefill-to-decode transition is a stamped edge inside each
  request start's window. The Qwen3-8B prefill lasts 2,663–2,690 ms (BETA n 33; GAMMA 8B arm n 10), as assumed.
  What the rule's exclusion logic did: all 41 ALPHA and the 10 GAMMA 1.7B primary request-start edges are excluded
  (`neighbour_edge`); ALPHA has no rise T. The pooled rise T rests on 43 Qwen3-8B request starts (BETA 33, GAMMA
  10). The secondary transition edge is likewise excluded in those runs (the request start is inside its −700 ms
  side), so ALPHA has no transition row.
- **(b) Pulse gaps above about 700 ms: holds.** OFF to next ON is at least 1,507 ms (warmups included) and pulses last
  1,000–1,011 ms in all three captures; no pulse edge was excluded for any reason.

## Printed output (run 2, verbatim)

```
b5_edge_check: script commit 7d3724b701955eaaa9ae1ef2e9abe05384d16577, script sha256 a0eb6af989c87842049c5f4db6ead1ba9efade261d9848012f60833daf11dc4e
rule: docs/analysis/b5/edge-check-reading-rule.md sha256 c9afe7bf2e0ebc406a52cea22c5d3f4b7d27f15fa5f439e53321f052c5708b47
seed 20261112, bootstrap resamples 2000
selftest: 200 synthetic steps (100 rise, 100 fall), true time uniform in -80..+120 ms of the stamp
  meter   (20 ms samples):  error mean +0.66 ms, |error| median 6.18 ms, max 21.77 ms (one-sample quantisation, I6 convention)
  sampler (~130 ms records): error mean +0.07 ms, |error| median 0.78 ms, max 4.11 ms
  dropout / missing-record / small-step paths: ok
ALPHA: 83 kept runs, 1 distinct calibration capture(s) (carried by [83] runs), b = 44.637 ms, meter stream sha256 200a9245c61f9bfb...
BETA: 68 kept runs, 1 distinct calibration capture(s) (carried by [68] runs), b = 49.144 ms, meter stream sha256 dc2c8b7ed77f760a...
GAMMA: 44 kept runs, 1 distinct calibration capture(s) (carried by [44] runs), b = 47.972 ms, meter stream sha256 69968fe59532f970...

## Assumption checks (from stamps only)
(a) ALPHA Qwen3-1.7B-4bit 2,048-token prefill duration: n 41, min 607 ms, median 622 ms, max 635 ms (NOT longer than the +800 ms window end)
(b) ALPHA pulse gaps (OFF to next ON, incl. warmups): min 1510 ms, max 6521 ms; pulse widths (ON to OFF): min 1000 ms; pulses per capture: 59 (+3 warmup)
(a) BETA Qwen3-8B-4bit 2,048-token prefill duration: n 33, min 2663 ms, median 2676 ms, max 2690 ms (longer than the +800 ms window end)
(b) BETA pulse gaps (OFF to next ON, incl. warmups): min 1510 ms, max 6518 ms; pulse widths (ON to OFF): min 1000 ms; pulses per capture: 59 (+3 warmup)
(a) GAMMA Qwen3-1.7B-4bit 2,048-token prefill duration: n 10, min 609 ms, median 621 ms, max 634 ms (NOT longer than the +800 ms window end)
(a) GAMMA Qwen3-8B-4bit 2,048-token prefill duration: n 10, min 2669 ms, median 2679 ms, max 2689 ms (longer than the +800 ms window end)
(b) GAMMA pulse gaps (OFF to next ON, incl. warmups): min 1507 ms, max 6516 ms; pulse widths (ON to OFF): min 1000 ms; pulses per capture: 59 (+3 warmup)
```


## Exclusions by reason (an edge may carry more than one reason)
| Session | Edge class | Stamped | neighbour_edge | meter_dropout | sampler_missing | small_step_meter | small_step_sampler | level_sd_undefined | Excluded | Kept |
|---|---|---|---|---|---|---|---|---|---|---|
| ALPHA | pulse_on | 59 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 59 |
| ALPHA | pulse_off | 59 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 59 |
| ALPHA | request_start_p2048 | 41 | 41 | 0 | 0 | 0 | 37 | 0 | 41 | 0 |
| ALPHA | decode_end | 83 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 83 |
| ALPHA | request_start_short | 42 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 42 |
| ALPHA | transition_p2048 | 41 | 41 | 0 | 0 | 41 | 39 | 0 | 41 | 0 |
| BETA | pulse_on | 59 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 59 |
| BETA | pulse_off | 59 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 59 |
| BETA | request_start_p2048 | 33 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 33 |
| BETA | decode_end | 68 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 68 |
| BETA | request_start_short | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 35 |
| BETA | transition_p2048 | 33 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 33 |
| GAMMA | pulse_on | 59 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 59 |
| GAMMA | pulse_off | 59 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 59 |
| GAMMA | request_start_p2048 | 20 | 10 | 0 | 0 | 0 | 9 | 0 | 10 | 10 |
| GAMMA | decode_end | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 44 |
| GAMMA | request_start_short | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 24 |
| GAMMA | transition_p2048 | 20 | 10 | 0 | 0 | 10 | 9 | 0 | 10 | 10 |

## Per session and direction (primary edges; Delta = sampler minus meter, ms)
| Session | b (ms) | Direction | Pulse n | Pulse median | Pulse IQR | Inference n | Inference median | Inference IQR | T (ms) | 95% interval | Undefined resamples | Reading |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALPHA | 44.6 | rise | 59 | -23.0 | [-34.8, -10.0] | 0 | n/a | [n/a, n/a] | n/a | [n/a, n/a] | 2000 | n/a |
| ALPHA | 44.6 | fall | 59 | -22.6 | [-32.2, -14.6] | 83 | -30.3 | [-37.2, -18.1] | -7.7 | [-9.6, -2.3] | 0 | inside |
| BETA | 49.1 | rise | 59 | -32.0 | [-40.3, -9.3] | 33 | -25.5 | [-31.7, -11.2] | +6.5 | [+1.5, +19.4] | 0 | inside |
| BETA | 49.1 | fall | 59 | -25.6 | [-35.9, -15.1] | 68 | -23.4 | [-31.6, -18.0] | +2.3 | [-0.7, +5.0] | 0 | inside |
| GAMMA | 48.0 | rise | 59 | -27.9 | [-34.7, -5.1] | 10 | -24.0 | [-32.6, -2.0] | +3.9 | [-7.5, +27.4] | 0 | inside |
| GAMMA | 48.0 | fall | 59 | -18.5 | [-32.3, -11.8] | 44 | -29.9 | [-37.6, -21.9] | -11.4 | [-15.3, -7.9] | 0 | inside |
| POOLED | 44.6/49.1/48.0 | rise | 177 | -27.4 | [-36.0, -7.1] | 43 | -25.5 | [-31.8, -10.2] | +1.8 | [-3.0, +14.8] | 0 | inside |
| POOLED | 44.6/49.1/48.0 | fall | 177 | -22.8 | [-33.5, -13.0] | 195 | -28.4 | [-35.2, -18.8] | -5.6 | [-7.5, -1.9] | 0 | inside |

## Secondary inference edges (reported, not in T)
| Session | Edge class | n kept | Median Delta (ms) | IQR |
|---|---|---|---|---|
| ALPHA | request_start_short | 42 | -8.9 | [-17.0, -0.6] |
| ALPHA | transition_p2048 | 0 | n/a | [n/a, n/a] |
| BETA | request_start_short | 35 | -37.6 | [-44.4, -32.7] |
| BETA | transition_p2048 | 33 | -16.7 | [-33.6, -6.4] |
| GAMMA | request_start_short | 24 | -24.1 | [-38.6, -5.4] |
| GAMMA | transition_p2048 | 10 | -15.9 | [-25.5, -2.5] |



`Reading` is the rule §1 row for that interval against ±b: `inside` (row 1), `outside` (row 2), `other` (row 3).
For POOLED, "inside" means inside ±b for every session's b (I11). Δ is sampler minus meter on the meter's RAW axis:
a negative Δ means the sampler's step time is earlier than the meter's, which holds for pulse and inference edges alike.

## Interpretations (fixed in the script before the first run; printed in its docstring)

Where the rule was ambiguous or did not match the data, the most literal reading was taken:

- **I1 Kept runs.** The target cells' kept units in each session's `derived/exclusions.json`, mapped to runs by
  `derived/roster.json`: ALPHA and BETA, the decode and prefill-p2048 reported cells (quads and repeats; 83 and 68
  runs); GAMMA, the kept quads of the two contrasts (44 runs). The script stops if they differ from RC's kept lists;
  they agree. The p42 cells are refused in Paper 1 and use the decode runs anyway.
- **I2 Calibration capture.** "Each one's calibration capture" is the capture in the run's `instrument_calibration/`.
  All kept runs of a session carry the same byte-identical capture (the opening capture), so it is one capture:
  its pulses are counted once (n = 59 per session, 177 pooled), and the pulse median is fixed under resampling. The
  closing capture is not carried by any run and is not used.
- **I3 Pulse count.** The rule says "the 56 non-warmup pulses"; each capture has 59 `pulse_command_on/off` pairs plus
  3 separate `warmup_command_on/off` pairs. All 59 non-warmup pulses are used. Warmup edges count only as neighbours.
- **I4 Stamped edges.** Pulse and warmup command ON/OFF (`clock_stamp.epoch_s`); request start = `phase_start` of
  `tokenize` (the request's first phase event, 0.2 ms before prefill start); transition = `phase_end` of `prefill`;
  decode end = `phase_end` of `decode`. Neighbours are searched among the kept runs' and the capture's stamped edges
  only ("No other data"). For the secondary edges the same run's transition is not a neighbour.
- **I5 Sampler windows.** Level windows use the whole records lying inside them; A..B runs from the start of the
  record covering −250 ms to the end of the record covering +350 ms.
- **I6 Meter integral.** The shipped `km003c_parse.integrate` convention: mean of the samples in [A, B) times
  (B − A). The selftest shows this carries one-sample quantisation (error up to about ±20 ms per edge, mean +0.7 ms
  over 200 synthetic steps); it is the same for pulse and inference edges.
- **I7 Dropout and missing record.** Meter: a device-time gap other than 20 ms, or no sample within 20 ms of a
  window edge, in [−700, +800) ms. Sampler: a record without all three rails, a gap above 1 ms between records, or
  records not covering the window.
- **I8 Clock.** Per edge, ordinary least squares of poll `rx` on poll `rt` over the polls within ±30 s.
- **I9 Bootstrap.** Each iteration resamples every session's kept runs with replacement (all kept runs; both
  directions from one draw; sessions in fixed order); pooled T from the same draws. ALPHA rise is undefined in all
  2,000 resamples (no kept edges). Percentiles by `km003c_parse.percentile` (linear).
- **I10 Reference b.** `RESULTS.md` does not print b in ms. b is each session's operative timing bound as recorded
  in RC (`windows.<S>.b_op_s`), which `RESULTS.md` cites as its recompute source, and the script checks it equals
  `withheld/bracket-evaluation.json` `assessment.b_fiducial_s`: ALPHA 44.637 ms, BETA 49.144 ms, GAMMA 47.972 ms.
- **I11 Wording.** The sentence is chosen from the pooled T per direction. Pooled "inside" = inside ±b for every
  session's b; "wholly outside" = outside ±b for every session's b. Either direction wholly outside gives row 2;
  both inside gives row 1; otherwise row 3. Every per-session row is also `inside` (ALPHA rise has none).
- **I12 Step test.** Excluded if |L_post − L_pre| < 5 × max(SD_pre, SD_post) on either instrument; every reason is
  evaluated where computable, so the counts by reason overlap.

## Deviations

One bug fix after the first run (DLE-11): the model label in assumption check (a). Both outputs are in the log; no
Δ, T, interval, exclusion count or outcome changed, and the per-edge output has the same SHA-256. No other change
was made after any Δ was seen: no tuning, no second estimator, no extra slices.
