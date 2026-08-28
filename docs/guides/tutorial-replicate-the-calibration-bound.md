# Replicate the paper’s worked calibration-capture bound

The paper uses two related bounds, so begin by separating them. A **capture
bound** is a time uncertainty, in seconds: the greatest displacement between a
commanded graphics-processor pulse edge and the edge reported by the **power
trace** — a sequence of power readings over time — plus the uncertainty in
placing that trace on ordinary date-and-time clock readings. The instrument
guide and the paper's appendix call this quantity **b_fiducial**, and the
replay prints it under that name.

The capture bound is not itself the smallest energy difference a measurement
window can resolve. That energy quantity is the **detection floor** (the
paper's Section 2 calls the same quantity the *cell resolution bound*, where a
*cell* is one small rectangle in the edge-shift search explained below): the
largest energy difference this measurement system can report between two runs
that were in fact identical. The later energy calculation converts
boundary-time uncertainty into energy by multiplying it by the power change
across the boundary, then combines that result with run-to-run variation. This
tutorial reproduces the paper's **diagnostic** capture bound: a value used to
test the measuring mechanism, not to support a scientific claim.

Physically, the calibration asks the graphics processor to switch on and off
at recorded times, observes where those switches appear in interval-averaged
power records — each record is one average over one time slice — and keeps the
largest edge-placement error that the data still permit.

## The retained artifact

The retained artifact is one diagnostic calibration recording identified by `20260722T145535-e941c821`. On the author’s machine it is under:

```text
/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/
```

That directory contains five files:

- `manifest.json` names the recording and pulse protocol — the rules and
  schedule for commanding pulses — and records the SHA-256 digest of each of
  the other four retained files. A SHA-256 digest is a fingerprint used to
  make byte changes practically detectable.
- `events.jsonl` is the event log, with one structured event per line, including the independently timed commands that turned each calibration pulse on and off.
- `instrument_evidence.json` contains the recorded clock readings and the digests that the replay uses. Its stored pulse rows and stored bound come from an older clock calculation, so the replay deliberately does not use them as answers.
- `raw/powermetrics.plist` is an Apple property-list file containing the native interval-averaged power records from Apple’s `powermetrics` instrument.
- `power_trace.csv` is a comma-separated table made from those native records.
  The replay does not use this convenience copy: it recomputes from the native
  record so that a disagreement in the derived table cannot replace the source
  measurement. The manifest fingerprints both files.

The large raw recording is not in this documentation checkout. [Appendix A.6](../../paper/draft-v1.md#a6-release-locators) also says that the public archive locator has not yet been issued. A second reader therefore needs to obtain the retained corpus—the collection of retained recordings—from the project owner until that locator is published. The `--corpus-root` command-line option names the directory that contains `runs_window_a_20260722/`. Without it here, the program searches this documentation checkout, reports that `instrument_evidence.json` is absent, and exits with code `3`, the number the program returns for unavailable primary files; absence cannot look like success.

## What the replay fence checks

`scripts/check_paper_replay_fence.py` is an automated replay **fence**: a check
that stands between a stored number and its use, and refuses rather than warns.
It reads the printed values from Section 2 of the paper, verifies the event log
and raw power-record fingerprints against `instrument_evidence.json`, and then
works from the original file bytes. It recomputes the **clock-placement bound**
— the upper limit on how far the two clocks' alignment may be wrong — while
allowing the ordinary clock and the machine's always-advancing clock to run at
slightly different rates. It also recomputes every **pulse fit** — the
calculation that finds the on-and-off shifts whose predicted power trace best
matches the observed trace — and compares the results with the paper.

Two different results come out of that calculation, and this tutorial uses the
second. The **best-fit lags** are the single on/off shift pair that explains the
trace most closely. The **allowed interval** is the full range of shifts the
trace cannot rule out — wider, because each power record averages roughly a
tenth of a second and cannot pin an edge to a point. The bound comes from the
widest end of the allowed interval, never from the best fit; the instrument
guide's §§4.2–4.4 build the search that produces it.

The comparison is exact for counts and for numbers represented in Python’s standard 64-bit floating-point format. Only the two signed best-fit lags—the on-and-off time shifts producing the closest fit—use the paper’s stated three-decimal rounding. The script also checks the paper’s displayed subtraction with exact decimal arithmetic, meaning base-ten subtraction without a binary approximation.

The reported “43 of 43” means that all 43 comparison rows matched. The rows are two counts, thirteen exact floating-point values, two rounded best-fit lags, one pulse name, and five fields for each of five clock readings: \(2+13+2+1+(5\times5)=43\). It does not mean that 43 recordings were tested.

`cell_count` is the number of search steps the edge-fitting calculation took
for this recording. The instrument guide calls one such step an
**evaluation**; a healthy recording takes roughly 115,000–138,000 evaluations,
and a fixed cap of 165,000 refuses any recording that takes more. The replayed
count, 122,859, is therefore ordinary for a healthy recording.

The replay’s data flow is shown below. **Onset** means a switch-on edge; **offset** means a switch-off edge.

```text
[instrument_evidence.json: clock readings and file fingerprints]
    -- supplies --> [fingerprint check]
[events.jsonl: commanded pulse edges]
    -- supplies --> [fingerprint check]
[raw/powermetrics.plist: native power intervals]
    -- supplies --> [fingerprint check]

[fingerprint check]
    -- authenticates --> [recomputation of clock placement and pulse fits]
[recomputation of clock placement and pulse fits]
    -- produces --> [allowed onset and offset intervals]
    -- produces --> [clock-placement bound]
[allowed onset and offset intervals]
    -- reduce to --> [largest absolute edge displacement]
[largest absolute edge displacement] + [clock-placement bound]
    -- add once --> [final capture bound]
[final capture bound]
    -- compare exactly --> [paper’s printed bound]
```

Square brackets enclose the name of every input, operation, or computed value. Each labelled arrow states how one named element feeds the next; the plus sign names the single addition performed near the end.

## Run the replay

First inspect the verified interface:

```console
python3 scripts/check_paper_replay_fence.py --help
```

Then run against the retained corpus:

```console
python3 scripts/check_paper_replay_fence.py --corpus-root /path/to/corpus
```

Here `/path/to/corpus` is the directory that contains
`runs_window_a_20260722/`, not the recording directory itself.

The run printed one `ok` row per match: `draft` is the value read from the paper and `derived` is the value recomputed from the retained files. Its exact output was:

Some rows show the two columns in different notation — for example,
`0.0000010000000000000002` and `1.0000000000000002e-06`. The `draft` column
reproduces the paper's printed decimal rendering; the comparison is made on
the parsed 64-bit values, which are identical.

```text
ok   pulse_count: draft=59 derived=59
ok   cell_count: draft=122859 derived=122859
ok   anchor_bound_s: draft=0.0011349971959968978 derived=0.0011349971959968978
ok   b_fiducial_s: draft=0.030067931757111657 derived=0.030067931757111657
ok   planned_on_offset_s: draft=26.625 derived=26.625
ok   planned_off_offset_s: draft=27.625 derived=27.625
ok   command_on_epoch_s: draft=1784757381.2856488 derived=1784757381.2856488
ok   command_off_epoch_s: draft=1784757382.293089 derived=1784757382.293089
ok   onset_residual_lower_s: draft=0.02544938965763524 derived=0.02544938965763524
ok   onset_residual_upper_s: draft=0.02893293456111476 derived=0.02893293456111476
ok   offset_residual_lower_s: draft=-0.008607394549133255 derived=-0.008607394549133255
ok   offset_residual_upper_s: draft=-0.005308621075866744 derived=-0.005308621075866744
ok   retained_residual_bound_s: draft=0.02893293456111476 derived=0.02893293456111476
ok   wall_resolution_s: draft=1.0000000000000002e-6 derived=1.0000000000000002e-06
ok   monotonic_resolution_s: draft=4.166666666666666e-8 derived=4.166666666666666e-08
ok   best_fit_delta_on_s: draft=+0.027 derived=0.027000000000000003
ok   best_fit_delta_off_s: draft=-0.007 derived=-0.007
ok   pulse_ordinal_word: draft=tenth derived='tenth'
ok   clock_stamps[0].stamp: draft=pre_spawn derived='pre_spawn'
ok   clock_stamps[0].epoch_s: draft=1784757335.502742 derived=1784757335.502742
ok   clock_stamps[0].monotonic_before_s: draft=458736.4081875 derived=458736.4081875
ok   clock_stamps[0].monotonic_after_s: draft=458736.408188666 derived=458736.408188666
ok   clock_stamps[0].resolution_s: draft=0.0000010000000000000002 derived=1.0000000000000002e-06
ok   clock_stamps[1].stamp: draft=first_parse derived='first_parse'
ok   clock_stamps[1].epoch_s: draft=1784757336.604396 derived=1784757336.604396
ok   clock_stamps[1].monotonic_before_s: draft=458737.509839458 derived=458737.509839458
ok   clock_stamps[1].monotonic_after_s: draft=458737.509840291 derived=458737.509840291
ok   clock_stamps[1].resolution_s: draft=0.0000010000000000000002 derived=1.0000000000000002e-06
ok   clock_stamps[2].stamp: draft=sampling_started derived='sampling_started'
ok   clock_stamps[2].epoch_s: draft=1784757337.0900722 derived=1784757337.0900722
ok   clock_stamps[2].monotonic_before_s: draft=458737.995513416 derived=458737.995513416
ok   clock_stamps[2].monotonic_after_s: draft=458737.995514666 derived=458737.995514666
ok   clock_stamps[2].resolution_s: draft=0.0000010000000000000002 derived=1.0000000000000002e-06
ok   clock_stamps[3].stamp: draft=sampling_stopped derived='sampling_stopped'
ok   clock_stamps[3].epoch_s: draft=1784757533.877846 derived=1784757533.877846
ok   clock_stamps[3].monotonic_before_s: draft=458934.782846541 derived=458934.782846541
ok   clock_stamps[3].monotonic_after_s: draft=458934.782848041 derived=458934.782848041
ok   clock_stamps[3].resolution_s: draft=0.0000010000000000000002 derived=1.0000000000000002e-06
ok   clock_stamps[4].stamp: draft=post_parse derived='post_parse'
ok   clock_stamps[4].epoch_s: draft=1784757533.8891652 derived=1784757533.8891652
ok   clock_stamps[4].monotonic_before_s: draft=458934.794166 derived=458934.794166
ok   clock_stamps[4].monotonic_after_s: draft=458934.7941665 derived=458934.7941665
ok   clock_stamps[4].resolution_s: draft=0.0000010000000000000002 derived=1.0000000000000002e-06
MEMBER 20260722T145535-e941c821
COMPARED 43
MISMATCHES 0
```

Thus the current result is 43 matches out of 43 comparisons, with no mismatch.

## Reproduce the arithmetic by hand

The event log supplies the commanded pulse edges. The clock readings and expected file fingerprints come from `instrument_evidence.json`. The native power intervals come from `raw/powermetrics.plist`. From those inputs, the current code recomputes all pulse fits rather than copying the older derived rows in the evidence file.

The recomputation finds that the tenth commanded pulse carries the largest
allowed displacement of the 59. Its allowed onset interval runs from
`0.02544938965763524` to `0.02893293456111476` seconds after the commanded
onset. Its allowed offset interval runs from `-0.008607394549133255` to
`-0.005308621075866744` seconds relative to the commanded offset; a negative
value means the observed offset may be earlier.

Take the largest absolute endpoint for each edge:

```text
onset worst case = max(|0.02544938965763524|, |0.02893293456111476|)
                 = 0.02893293456111476 s

offset worst case = max(|-0.008607394549133255|, |-0.005308621075866744|)
                  = 0.008607394549133255 s
```

The onset value is larger. The replay checks every onset and offset from all 59 detected pulses—118 edge values—and confirms that this onset is the unique maximum.

The second number is the **clock-placement bound**: the power record and pulse
commands are stamped by two different clocks, and this scalar limits how far
their alignment may be wrong. The instrument guide's §5
derives it. The recomputed value is `0.0011349971959968978` seconds. It is
added rather than combined in quadrature because it is a bound, not a standard
deviation: the pulse-edge and clock-placement errors may both take their
worst-case values at the same time. A sum smaller than that legal combination
would not be a bound. Add it once to the maximum edge displacement, using the
same 64-bit floating-point arithmetic as the implementation:

```text
0.02893293456111476 s
+ 0.0011349971959968978 s
= 0.030067931757111657 s
```

That is the capture bound. It exactly matches the value in [Section 2, “One diagnostic reconstruction”](../../paper/draft-v1.md#one-diagnostic-reconstruction) and [Appendix A.3.6](../../paper/draft-v1.md#a36-the-calibration-bound-b_fiducial-and-validity). The match establishes faithful replay of this diagnostic calibration recording; the paper explicitly does not use it as evidence for a scientific claim.

## What you should now be able to do

- Distinguish the time-valued capture bound from the energy-valued detection floor.
- Locate the five retained files and explain which three primary inputs the replay reads.
- Use `--corpus-root` when the retained corpus is outside the documentation checkout.
- Explain what each stage in the replay diagram computes.
- Recalculate the maximum edge displacement and add the independent clock-placement bound.
- Interpret 43 matches as checked paper values, not recordings.
