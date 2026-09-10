# Exhibit A — the two contract paragraphs at 58d4696b (docs/contracts/measurement_methodology.md)

## A1 admission paragraph (lines 66–80)
```text
both attempts preserve distinct raw artifacts and provenance. A persistent
failure either aborts (production) or records the exploratory-only,
unwaivable `environment_admission_failed` claim barrier (`on_fail: flag`).
There is no skip disposition in a fixed-n campaign. A lightweight post-run
display/screensaver/HID observation makes within-member transitions visible.
Each admission attempt records its start and end times. The admitted
baseline's duration must not exceed the attempt's span, and the baseline's
capture interval must lie inside the attempt's start-to-end interval. Both
comparisons are between epoch timestamps that were rounded on different
arithmetic paths (a sum of sampler intervals against a difference of stored
endpoints), so each allows at most 1 μs of discrepancy — four representable
steps of an epoch-seconds binary64 value, where one step is 0.238 μs at epoch
1.789e9 — and never credits unobserved time: a baseline longer than the
attempt by 10 μs, or a capture endpoint one sample interval (100 ms) outside
it, still refuses.
```

## A2 cooldown bullet (lines 295–312)
```text
- Between live repetitions, cooldown v2 holds until the retained evidence has
  both a complete 30-second wall-clock span and at least
  `coverage_fraction * sustained_window_s` of captured coverage
  (`coverage_fraction = 0.8` by default), and its duration-weighted idle-power
  mean satisfies the one-sided rule
  `rolling_mean <= reference * (1 + tolerance)` (10% by the production
  policy), while thermal pressure is Nominal. A below-reference mean therefore
  counts as recovery. Span and coverage are tested with a small allowance
  for floating-point rounding, never for unobserved time: the span test
  allows 1 μs; the coverage test allows the larger of 1 μs and a summed
  rounding term, where that term adds, for every retained reading that
  overlaps the window, one representable step (one unit in the last place,
  ULP) of the reading's evidence end and one ULP of its clipped start, plus
  one ULP of the coverage sum itself. A 10 μs deficit in span or coverage
  still refuses. An optional calibrated absolute ceiling is an
  additional upper cap and never an OR escape. The wait has a 5-minute cap;
  the cap is evaluated before release on every iteration, so recovery criteria
  first met at or after the deadline remain a `cap_hit` (with the late criteria
```
