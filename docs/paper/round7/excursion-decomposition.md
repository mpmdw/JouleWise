# What the 30 ms calibration bound is made of

Round-7 supporting analysis. Desk work over a retained capture; no new
measurement was taken, and nothing under `runs_window_a_20260722/` was written.

## Replay command

```sh
python3 scripts/paper_excursion_decomposition.py \
    --corpus-root /Users/edr/code/JouleWise \
    --out docs/paper/round7/excursion-decomposition.json \
    --svg docs/paper/figures/fig4_edge_excursions.svg
```

`--corpus-root` is the directory *containing* `runs_window_a_20260722/`, not the
capture directory itself. Every number in this document comes from the JSON file
that command writes, `docs/paper/round7/excursion-decomposition.json`. Where a
number is stated to fewer digits than the file carries, the file governs.

## Words used here

Three terms carry the whole analysis, so they are built before they are used.

A **commanded edge** is a moment the harness told the machine to start or stop a
burst of work: the switch-on moment is the **onset**, the switch-off moment is
the **offset**. The capture commands 59 such bursts, so it contains 118 edges.

A **best-fit lag** is the single time shift that makes the predicted power trace
line up as closely as possible with the observed one, for one edge. It is signed
in the sense *detected minus commanded*: a positive onset lag means the power
trace shows the burst starting **later** than it was ordered to start.

An **allowed interval** is wider than the best-fit lag, and it is the quantity
the published bound is actually built from. Each power record reports one average
over roughly a tenth of a second, so the trace cannot place an edge at a point —
it can only rule out shifts that would contradict the recorded averages. What
survives is a range. The bound takes the **worst excursion** of each edge's
allowed interval, meaning whichever end is furthest from zero, and then takes the
largest of those 118 values.

These two are different numbers for the same edge, and confusing them is the easy
mistake here. A statement about *which way the instrument is off* uses the
best-fit lag. A statement about *the size of the published bound* uses the
allowed interval.

## Reproduction statement

The pulse rows stored inside this capture's 2026-07-22 `instrument_evidence.json`
were produced by an earlier version of the clock-placement estimator and are not
read as values by this analysis. The detection is recomputed from the primary
bytes — the retained `raw/powermetrics.plist` and `events.jsonl`, both checked
against the fingerprints the evidence file records — under the current (v3)
estimator. The script refuses to write any output unless that recomputation
reproduces the two values the frozen draft prints for this capture. It did:

| Value | Draft `docs/paper/draft-v1.md` | Re-derived | Result |
|---|---|---|---|
| `b_fiducial_s` | `0.030067931757111657` | `0.030067931757111657` | identical double |
| `projection_evaluated_cell_count` | `122859` | `122859` | identical integer |

As an independent check that this is the same computation the repository already
fences, the re-derived row for pulse 9 matches every value
`scripts/check_paper_replay_fence.py` reports for that pulse: allowed onset
interval `0.02544938965763524` to `0.02893293456111476` s, allowed offset
interval `−0.008607394549133255` to `−0.005308621075866744` s, best-fit lags
`+0.027` and `−0.007` s.

## Summary of the 118 edges

Best-fit lags, in milliseconds, signed as *detected minus commanded*. "Late"
means positive; "early" means negative.

| | Onsets (59) | Offsets (59) |
|---|---|---|
| median | **+13.0** | **−5.5** |
| interquartile range | 5.0 | 7.0 |
| median absolute deviation | 2.5 | 4.0 |
| mean | +13.237288 | −6.050847 |
| minimum | +4.0 | −15.0 |
| maximum | +27.0 | +3.5 |
| count late (positive) | **59** | 8 |
| count early (negative) | 0 | **49** |
| count exactly zero | 0 | 2 |

The interquartile range is the width of the middle half of the sample: a quarter
of the values sit below it and a quarter above. The median absolute deviation is
the typical distance of a value from the median, and is used here because it is
not moved by the one or two extreme pulses.

Worst excursions of the allowed intervals — the quantity the bound is built from,
always positive because it is a distance from zero:

| | Onsets (59) | Offsets (59) | All 118 |
|---|---|---|---|
| median | 14.924429 | 8.241330 | 11.903439 |
| interquartile range | 5.126558 | 6.546343 | 7.599034 |
| minimum | 6.502036 | 1.191832 | 1.191832 |
| maximum | **28.932935** | 16.480784 | **28.932935** |

The single largest value, 28.932935 ms, is pulse 9's onset. Onsets carry the
larger excursion in 52 of the 59 pulses.

## How much of the bound is repeatable, and how much is scatter

The published bound decomposes into four terms that sum to it exactly:

| Term | Value (ms) | Share | What it is |
|---|---|---|---|
| repeatable onset bias | 13.000000 | 43.2 % | the median onset lag — the part present on every pulse |
| excess of the worst pulse | 14.000000 | 46.6 % | how much further pulse 9's onset lagged than the median pulse (+27.0 − +13.0) |
| reach of the allowed interval | 1.932935 | 6.4 % | how far pulse 9's allowed interval extends beyond its own best fit (28.932935 − 27.0) |
| clock-anchor term | 1.134997 | 3.8 % | the separate bound on placing the whole trace on the wall clock |
| **total** | **30.067932** | 100 % | `B_fiducial`, matching the draft digit for digit |

**In one sentence: a repeatable bias accounts for 13.0 ms of the 30.07 ms bound
(43 %), and pulse-to-pulse scatter for a slightly larger 14.0 ms (47 %), so the
bias is the largest single term but does not by itself dominate the bound.**

The distinction that matters is between the typical edge and the bound. For a
typical onset the bias is nearly the whole story: it is 13.0 ms of the 14.924429 ms
median onset excursion, or 87 %. But the bound is a maximum, not a typical value,
and a maximum is set precisely where the scatter is largest. Removing a
well-characterised 13 ms bias would therefore shrink the typical edge error by
roughly seven-eighths while shrinking the bound by well under half.

The reviewers' stated expectation entering this analysis was a bias of about
+16 ms on onsets and −11 ms on offsets. Those two figures are the values stored
for pulse 0 under the *earlier* estimator, not the distribution medians under the
current one. Re-derived under the current estimator across all 59 pulses, the
medians are **+13.0 ms and −5.5 ms**. The direction of both expectations holds;
the offset magnitude is about half what was expected.

## Independence: what the pulse-index behaviour shows

The paper's "95/95" label treats the 59 pulses as independent draws from one
distribution. The numbers below are what the capture shows about that. They are
**descriptive only** — no significance test, model, or confidence statement is
attached to any of them, and none is offered as proof of independence. They are
reported so a reader can see the pattern rather than take the assumption on
trust.

**Trend across the capture.** If the instrument were drifting, warming, or
settling as the 59 pulses fired, the excursions would trend with pulse index.
Spearman's rank correlation, which runs from −1 to +1 and reports whether one
quantity tends to rise as the other does, and the slope of a straight line fitted
by least squares:

| Series against pulse index | Spearman rank correlation | Straight-line slope | Change across the whole capture |
|---|---|---|---|
| onset best-fit lag | −0.229191 | −0.051899 ms per pulse | −3.010 ms over 58 pulse gaps |
| offset best-fit lag | +0.068914 | +0.013735 ms per pulse | +0.797 ms over 58 pulse gaps |
| onset worst excursion | −0.200526 | −0.044685 ms per pulse | −2.592 ms over 58 pulse gaps |
| offset worst excursion | −0.017797 | −0.001296 ms per pulse | −0.075 ms over 58 pulse gaps |

The offset series shows essentially no trend. The onset series shows a weak
downward one, and it should be stated plainly rather than waved past: the fitted
line falls 3.010 ms across the capture, which is larger than the 2.5 ms median
absolute deviation of the same series. That is a real feature of these 59 numbers,
not a rounding artefact. It is small next to the 13.0 ms bias and next to the
23 ms full spread of the onset lags, and a rank correlation of −0.23 on 59 points
is weak, but the capture does not show onsets as perfectly exchangeable in firing
order. A single capture cannot settle whether this is drift, an artefact of the
pulse schedule, or chance.

**Correlation between the two edges of the same pulse.** If a pulse that started
late also ended late, the pulse's two edges would not be separate draws:

| Pair | Pearson correlation | Spearman rank correlation |
|---|---|---|
| onset lag against offset lag, same pulse | −0.111746 | −0.109346 |
| onset worst excursion against offset worst excursion, same pulse | +0.175409 | +0.173030 |

Both are weak. The signed lags are slightly *anti*-correlated, meaning a
later-starting pulse tends very slightly toward an earlier-ending one — the
direction that would be expected if the fit were trading one edge against the
other to preserve the plateau width, though the size here is too small to rest
anything on.

**What this does and does not support.** The pulses do not partition into
obviously distinct groups, no edge pair moves together strongly, and the offset
series shows no trend in firing order. That is consistent with the independence
the "95/95" label assumes. It is not a demonstration of it, and the weak onset
trend is a caveat that belongs with the label rather than in a footnote below it.

## A physical explanation — labelled as interpretation

**The following paragraph is interpretation, not measurement. Nothing in this
capture tests it, and no claim in the paper rests on it.**

The onset bias and the offset bias differ in both size and consistency: every
onset is late by a typical 13 ms, whereas offsets are early by a typical 5.5 ms
with ten of the 59 not early at all. A plausible reading is that starting and
stopping a large matrix multiplication on the GPU are not mirror images of each
other. Starting one requires the work to be dispatched to the GPU, the kernel to
be scheduled, and the clocks and power delivery to climb to the level the work
demands; the power draw therefore ramps over some milliseconds after the command,
and a detector looking for the moment power rises will place that moment late by
about the ramp time — repeatably, because the same dispatch and ramp happen every
time. Stopping is the decay of an already-running state: the last kernel drains
and the power falls back, a process that need not take the same time as the climb
and that can begin before the commanded stop if the final work completes early.
That asymmetry would produce exactly what is seen — a large, tight, one-signed
onset bias and a smaller, looser, mostly-one-signed offset bias. Confirming it
would need a separate experiment varying the burst size and observing whether the
onset bias tracks the dispatch and ramp time; that experiment has not been run.

## Files

| File | What it is |
|---|---|
| `scripts/paper_excursion_decomposition.py` | the analysis; re-derives the capture and writes both outputs below |
| `docs/paper/round7/excursion-decomposition.json` | per-pulse values and every summary statistic quoted here |
| `docs/paper/figures/fig4_edge_excursions.svg` | the figure, generated by the same script from the same values |
| `docs/paper/figures/png/fig4.png` | 2400-pixel raster of the figure |
| `docs/paper/figures/fig4-verification.md` | element-by-element check of the figure against the data file |
