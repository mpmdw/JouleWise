# The JouleWise Instrument, Explained From Zero

*A guide for someone new to the project. It assumes you know what an LLM is,
what power and energy are, and roughly how a computer is put together —
nothing else. It is deliberately more thorough than the paper's methodology
section: the paper argues; this document teaches. Every mechanism is
presented with the problem that forced it into existence. The guide presents
refusal checks together with the recorded failures or executed counterexamples
that motivated them where that provenance is available.*

*How to read it: every term of art is built or glossed where it first
appears, in the body, in order. The glossary at the end is a reminder for
someone coming back to the document, not the place definitions live. If you
meet a word here that has not yet been explained, that is a defect in this
guide, not something you were supposed to already know.*

---

## 1. What this instrument is for

JouleWise measures the energy cost of large-language-model inference
work — "how many joules does it cost this Mac to generate one token,"
"how much energy does processing a 256-token prompt take," "is the 7-billion-
parameter model's decode energy distinguishable from the 1.5-billion one's"
— on Apple Silicon, using only the machine's own telemetry: measurements that
the operating system reports about the hardware while it runs.

JouleWise attaches a measured error bound where its calibration applies. The
current paper explicitly treats transfer from light commanded GPU pulses to
sustained inference as an untested assumption; the prospective campaign will
not test that transfer. A **claim** is any statement the project publishes as
true of the world, the thing all the machinery below exists to permit or
refuse. The
project's one-line philosophy: **a measurement without a demonstrated error
bound is an anecdote.** Most published LLM-energy numbers on consumer
hardware are, by that standard, anecdotes — the related-work section of the
paper documents peer-reviewed studies that integrate the same telemetry
this project uses, with no calibration and no uncertainty treatment at all.

That commitment has an unusual consequence: the *primary product* of the
instrument is not the joule numbers. It is the **detection floor** (the
paper's Section 2 calls the same quantity the *cell resolution bound*, where a
*cell* is one small rectangle in the timing search built in §4.4) — the
largest energy difference the measurement system can report between two runs
that were in fact identical — plus the machinery that proves the floor is
real. The
model-comparison numbers are then demonstrations of what a characterized
instrument can resolve.

### 1.1 What actually gets measured: operations and phases

An **operation** is one unit of work with a start event and a stop event that
the workload itself logs: "prefill of a 256-token prompt, begin … end,"
"decode of 128 tokens, begin … end." The reported operation energy is the
energy assigned between those events from three processor power channels —
CPU, GPU, and Neural Engine; display, storage, fans, charging, conversion loss,
and other loads are outside the sum. Everything downstream depends on
those two timestamps being trustworthy, which is why sections 4 and 5 are as
long as they are.

Inference has two physically different **phases**, and they must be measured
separately because they stress the hardware in different ways:

- **Prefill** — the model reads the entire prompt in one go. All the prompt's
  tokens can be processed together, so this is a dense burst of arithmetic
  that saturates the GPU's compute units. Short and hot.
- **Decode** — the model then emits tokens one at a time, each new token
  depending on the one before it. There is little to parallelise, so the GPU
  spends most of its time moving weights from memory rather than multiplying.
  Longer, and limited by memory bandwidth rather than arithmetic.

"**Phase-resolved**" measurement means reporting energy for prefill and decode
separately instead of one number for the whole run. It is the project's whole
point, and it is also what makes the timing problems in section 3 dangerous:
a single number for a whole run tolerates a sloppy boundary, but a number per
phase does not.

### 1.2 The nouns this document runs on

Six words appear on nearly every page below. They are built here, once, from
what physically happens, so that no later sentence has to lean on a word you
have not been given.

- **Capture** — one run of the calibration protocol of section 4. The
  privileged sampler starts, the GPU is driven through a known pattern of
  load pulses, the sampler stops: about 197 seconds of wall-clock time.
  What it leaves behind is three things — the sampler's raw output, the
  workload's event log (one line per commanded pulse edge, timestamped), and
  the evidence tying those two timelines together. Everything in sections 4
  and 5 happens inside a single capture.
- **Member** — one measured execution of one configuration during a **science
  run**, meaning the part of an uninterrupted measurement sitting that
  measures the models themselves
  rather than the instrument: "1.5-billion-parameter model, decode 128 tokens,
  repetition 3 of 4." Everything else in that sitting — calibration pulses
  and reference workloads — measures the instrument. Members are what a published
  number is eventually computed from.
- **Bundle** — the directory a capture or a member leaves on disk: the raw
  sampler output, the event log, the derived energy numbers, a metadata
  record describing exactly how it was produced, and cryptographic
  **fingerprints** of all of it — fixed-length values computed from exact file
  bytes to make byte changes practically detectable (§7). The bundle is the unit that gets stored,
  re-checked, and either allowed to support a published number or refused.
- **Window** — one uninterrupted sitting at the machine: quiet conditions
  established, network time disabled, a calibration capture, then the science
  members in a pre-fixed order, then a second calibration capture, then
  everything restored. In practice, a night.
- **Pack** — the committed directory that specifies, *before the window
  runs*, every configuration the window will execute and in what order.
- **Corpus** — a named, fixed set of captures used to derive a number. When
  you read "the 17-member corpus" below, it means exactly those seventeen
  captures, identified by fingerprint, and no others.

Two more words carry the project's whole attitude. A **claim** is a statement
JouleWise publishes as true of the world — "model A's decode costs E joules
more than model B's, on this exact software stack, with this bound," where a
**stack** is the whole named set of software the measurement ran on: model
file, runtime, tokenizer, operating-system build. A **refusal** is a recorded
decision that some piece of evidence may *not* be used, together with the
reason. Refusals are produced by **gates** — automated checks with the
authority to stop the pipeline, no human veto in the loop — and they are
outputs, not errors: the instrument publishes them, counts them, and treats a
night that produced only refusals as a successful night.

*Status note: revised 2026-08-27. This revision makes the measured boundary,
the before-and-after known-workload timing calibration, the detection floor,
the ordered collection window, the two claim gates, and a recorded **verdict**
— the final pass-or-refuse decision — reproducible from the text. It also records three changes in the current
checkout: code now builds and checks a record binding a window's fixed pack,
its two timing calibrations, its run directory, and its verdict, although the
current pack does not yet pass that record into the verdict stage; short desk
tests now exercise refusal paths through the ordered pipeline; and the operator
**threat model** — the set of operator failures the design promises to handle —
now protects against plausible mistakes rather than a deliberately dishonest
operator. A proposed pre-start check for the complete two-comparison statistical
plan is not yet connected to the code that makes plan bytes final, and the
planned clean end-to-end window check has not yet been run. Every calibration
number below was re-checked against the current **calibration acceptance
artifact** — the issued file that pins which calibration recordings,
numerical pass-or-refuse limits, and versions of the code that calculates each
bound these numbers come from — named
`d079_calibration_acceptance_v2_n17_r6` and built in §7.*

## 2. The measurement primitive, and why it cannot be trusted blindly

Everything starts with `powermetrics`, Apple's built-in telemetry sampler.
Run with root privileges, it reports power draw for named **rails** of the
processor package — a rail being a named power channel the chip's own
power-management hardware reports separately: the CPU cluster, the GPU, and
the ANE (Apple Neural Engine). The sampler emits a series of **samples**,
each one an *average* power over its own sampling interval, not an
instantaneous reading. The whole series a run produces is its **trace** — the
raw record everything downstream is computed from. JouleWise integrates the
three rails between operation boundaries: energy = sum of (average power ×
interval duration).

The samples that straddle a boundary are **clipped** — a sample whose
interval is half inside the operation contributes half its energy to that
operation and half to whatever came before or after. Clipping is the
smallest, most obviously correct thing to do, and it is also exactly where
the danger in section 3 enters: clipping is only right if you know where the
boundary falls inside the sample, and knowing that requires the two clocks
to agree.

One warning about a second overloaded word. Everywhere above, a **boundary**
is a moment in time — the instant a phase starts or stops. The next paragraph
uses the word in an unrelated sense: the **measurement boundary** is a question
of scope, meaning which physical quantities are inside the joule total at all.
Each use below says which meaning it carries.

This is the exact **measurement boundary**, meaning the physical quantities
that enter the reported joule total. For each overlapping interval, the
**sampler adapter** — the code that parses `powermetrics` output into
timestamped samples — reads the sampler's CPU, GPU, and Apple Neural Engine
processor-rail power values, converts milliwatts to watts, and adds them. The
**reducer** — the code that turns those parsed samples into a joule number for
one operation — treats the sum as a rectangular interval average and
multiplies it by the interval's positive overlap with the operation window. It
does not interpolate `powermetrics` endpoints. The sampler's
thermal reading is retained as machine-state evidence but is not added to
energy. Display, storage, fans, battery charging, power-conversion loss, and
every other load not present in those three named processor rails are outside
the numerical sum. JouleWise therefore reports **processor-rail energy**, not
whole-computer or wall-outlet energy; measuring the latter requires an
external power meter.

[Figure 1: boundary and energy assignment](../paper/figures/fig1_boundary_attribution.svg)
draws this calculation. Its title says that boundary placement decides which
phase is charged, and its subtitle says the drawing is schematic and all
values are illustrative. The white drawing area has a horizontal time axis
from 0.0 to 1.0 seconds in 0.2-second steps and a vertical power axis from 0
to 50 watts in 10-watt steps, over a pale grid. Gray step-shaped rectangles are the
sampler's interval-average powers; a dashed dark line is an idealized workload
power trace. A solid black vertical line is the runtime's logged operation
boundary. A translucent blue vertical band, bounded by two dashed blue lines,
is the interval in which calibration says that boundary may physically fall.
The blue hatched sliver between the black line and one band edge is energy that
could move from one phase to its neighbour. A vertical double-headed arrow
names the illustrative 33-watt power step; a horizontal double-headed arrow
names the illustrative 112-millisecond sampler interval; and a blue callout
arrow points to the movable-energy sliver and writes its illustrative
`0.030 s × 33 W ≈ 1 J` calculation. Gray
bars beneath the plot name the prefill and decode phases. The legend repeats
the five plotted marks — interval power, idealized power, runtime boundary,
timing band, and movable sliver. Four notes say that prompt processing draws
high power while saturating compute units, token generation draws less while
waiting on memory, the boundary interval is one blended average, and moving
the boundary transfers energy between phases without changing request-total
energy. The drawn
widths and heights explain the geometry; they are not measured data.

What Apple does **not** provide: a calibration certificate, timing
guarantees for when a sample's window actually began and ended, or
documentation of exactly which physical loads appear on which rail. Three
concrete consequences shaped the whole project:

- **Attribution is not guaranteed.** The sampler has its own clock and its
  own buffering; the workload has another clock. Nothing promises that
  "the sample stamped 12:00:00.100" aligns with "the token generated at
  12:00:00.100" to better than some unknown error.
- **Resolution is not stated.** Nothing says how small an energy
  difference is distinguishable from the sampler's own noise and the
  machine's background variation.
- **Rail coverage is not enumerated by physical device.** The adapter can
  name the three reported processor rails, but that does not turn them into
  a wall-power measurement. The boundary must therefore travel with every
  result: *these three rails, nothing else*.

Because none of these properties comes from the vendor, the instrument's
job is to *measure its own measurement system*. Sections 4–8 are that
self-measurement; everything else is protecting it from contamination.

## 3. The two families of error

Every defense in this project targets one of two error families. Keeping
them separate is the single most clarifying idea in the methodology.

**Attribution error: the right energy, assigned to the wrong thing.**
If the clock alignment between workload and sampler is off by even a few
milliseconds, samples near an operation boundary get integrated into the
wrong operation. The total is right; the split is wrong.

Put numbers on it. Suppose a decode phase runs for 3 seconds and the GPU
rail averages 12 watts through it: 36 joules for the phase. Each sample
covers roughly 0.112 s — the sampler is asked for 100 ms intervals but
delivers about 112 ms in practice, as section 4.1 details — so one sample
carries about 1.3 J. If the boundary
between prefill and decode is misplaced by a single sample's width, 1.3 J
moves from one phase's total to the other's. Section 8 reconstructs a real
diagnostic timing bound whose attribution contribution is about 0.99 J for
the paper's representative power step, showing that a one-sample displacement
is large on the scale being characterized. (The power in this paragraph is
illustrative; the later timing bound comes from retained evidence.) For a
whole-run measurement, the same error cancels out
completely — the energy stays inside the run either way. That is exactly
why phase-resolved measurement is the hard case and why this project is
obsessed with clocks.

The origin story that made attribution the obsession: an earlier
generation of the pipeline carried a **time-anchor defect** — the mapping
between the sampler's timestamps and the workload's timestamps was
subtly wrong — and when it was found, the project voided *every*
corpus that had been eligible to support a claim, and rebuilt the anchoring
machinery from scratch. That decision (repair, then re-collect, rather
than patch and excuse) set the tone for everything after: attribution
errors are silent, so the machinery that bounds them must be loud. It
happened a second time, smaller and far more instructive, on 2026-08-18 —
section 5 is that story, and it is the best single illustration of how this
project treats being wrong.

**Resolution error: a difference that isn't there, or a real one you
can't see.** Even with perfect attribution, three things put a floor under
what can be distinguished: the machine's background activity, its thermal
state, and the sampler's **quantization** — the fact that it reports power
in discrete steps, so two genuinely different power draws can come back as
the same printed number. If two identical workloads, measured minutes
apart under the best possible conditions, differ by some spread — call that
spread *X* joules — then no claim of a difference smaller than *X* is honest — no matter what the
point estimates say.

Attribution is bounded by **calibration** (sections 4 and 5). Resolution
is bounded by **floors** (section 8). The composed claim carries both.

A note on one overloaded word before it starts working. **Floor** always
means "a limit below which something cannot go," but this document uses it
of several different things: the *detection floor* (the largest false energy
difference reported between identical runs), the *0.1 ms floor* on how finely the detector subdivides
its search, and the *floor* under the timing allowance of section 4.8. Each
use below names what it is a floor of. The same goes for **bracket**, which always means
"pin a quantity between two known values on either side of it" — used in
section 4 for a calibration capture before and after the science members,
and in section 5 for two system timestamps taken either side of an event.

## 4. The fiducial calibration: the instrument measuring itself

The calibration answers a concrete question: *if software commands a load
pulse at a known time, how far from the commanded edges can that pulse
appear in the sampled power trace?* The answer is a per-capture timing
bound called **b_fiducial**. "Fiducial" is the metrology term for a
reference mark whose true position is known independently — a survey
benchmark, a registration cross on a printing plate. Here the fiducial is a
burst of GPU load whose true start and stop times the software itself chose,
so any displacement seen in the trace is instrument error and nothing else.

The code that computes b_fiducial from a capture is the *fiducial estimator*.
"Estimator," throughout this document, means a specific piece of code that
computes a quantity from raw evidence — and section 7 explains why replacing
one, even trivially, is treated as building a different instrument.

**Why a commanded pulse, and not the real workload.** You cannot bound
attribution error by measuring something whose true timing you don't know:
if the trace disagrees with your expectation, you cannot tell whether the
instrument is late or the workload was. So the calibration measures a signal
whose ground truth is under your control. A commanded square pulse is the
simplest such signal: its true edges are in the event log because software
put them there, its apparent edges are in the power trace, and the
difference between the two *is* the attribution error — measured rather
than assumed.

**The protocol (version 3, fixed before use).** The workload drives 59
one-second GPU pulses — each a 4096×4096 half-precision matrix multiplication loop, chosen
because it takes the GPU rail from near-idle to near-saturation in well
under a sample's width, giving the sharpest edge the hardware can produce —
after 3 warmup pulses that are discarded, with the sampler asked for a
100 ms cadence. Every capture records the raw sampler trace, the workload's
event log, and a **clock anchor**: the measured relationship between the
sampler's timeline and the workload's timeline. Section 5 builds the anchor
in full; for now, treat it as "the number that says where in the sampler's
trace the workload's t = 0 actually falls, with its own error bar."

The quiet gaps between pulses follow a deterministic **low-discrepancy
schedule** — a fixed, deliberately irregular set of gap lengths, spread as
evenly as possible over the range rather than drawn at random or held
constant. The problem it solves is worth seeing concretely. Suppose instead
that every gap were exactly 1.000 s and the sampler ticked exactly every
0.100 s. Then every pulse would begin at the same position *within* a
sampling interval — say, 30 ms after a sample boundary, every single time.
Any systematic error that depends on that position would then repeat
identically 59 times, and 59 pulses agreeing to the microsecond would look
like superb precision while actually being one measurement performed 59
times. Irregular gaps scatter the pulses across all positions within the
sampling interval, so the spread you measure is a real spread. Determinism
matters too: the schedule is fixed in advance and identical on every
capture, so two captures are comparable and neither was tuned after seeing
its own result.

### 4.1 One pulse, end to end

The rest of this section follows a single pulse — call it pulse 23 of the 59
— from raw samples to a bound, then multiplies up. Everything the detector
knows about that pulse is in the samples covering it, so start there.

**What the samples actually say.** The sampler does not see edges. It
reports one *average* power per interval, and in practice each interval
covers about 112 ms (the 100 ms cadence is a request, not a guarantee).
Line up those intervals against the commanded pulse and they fall into
three groups:

- samples lying wholly *inside* the pulse, which read the plateau — the
  loaded power level;
- samples lying wholly *outside* it, which read the baseline — the idle
  level;
- and, at each edge, one or two samples that **straddle** it: the pulse
  covers only part of their interval, so they report a blend of plateau and
  baseline, in proportion to how much of the interval the pulse covered.

That last group is the entire evidence base. A plateau sample says only
"the pulse was on for all of this interval" — it says nothing about *where*
the edge fell, because it would read exactly the same if the edge had been
20 ms earlier. Same for the baseline samples. Only the straddling samples
carry positional information, and they carry it as a height: the fraction
of the interval the pulse covered.

Worked, with illustrative power levels: baseline 2 W, plateau 40 W, a
straddling sample 112 ms wide whose interval the pulse overlaps for 30 ms.
Its reported average is 2 + (30/112) × 38 = 12.18 W. Nothing else about
that sample is informative; that one number, 12.18 W, is what the edge
placement has to explain.

### 4.2 Two unknowns make a plane of guesses

A pulse has exactly two unknowns: how far its **start edge** really was from
the commanded start time, and how far its **stop edge** really was from the
commanded stop time. So a complete guess about the pulse is a pair of
numbers. *"Started 3.2 ms late, stopped 1.1 ms early"* is one guess.
*"Started 40 ms late, stopped 40 ms late"* is another.

Put start-shift on a horizontal axis and stop-shift on a vertical axis, and
every possible guess becomes one point on a plane, the same way every
possible (voltage, current) operating point of a device is one point on an
I–V plane. That is all "the plane" means here: **each point of it is one
hypothesis about where the two edges really were,** and the origin is the
hypothesis that the pulse landed exactly where it was commanded.

Any guess can be tested, because a guess predicts the samples. Take the
(+40 ms, +40 ms) guess against the straddling sample above. If the whole
pulse really sat 40 ms later than commanded, that sample's 30 ms of overlap
would not exist at all — the predicted reading is the bare baseline, 2 W,
against a recording of 12.18 W. A 10 W miss is enormously larger than
sample-to-sample noise, so that guess is **ruled out**: the recorded data
contradicts it.

Now take (+0.3 ms, −0.2 ms). Shifting the start edge 0.3 ms later cuts the
overlap from 30 ms to 29.7 ms, so the predicted reading moves from 12.18 W
to 12.08 W — a change of about 0.1 W, well under one percent, and smaller
than the ordinary wobble between consecutive samples. The data cannot tell
that guess apart from the perfect one. It **survives**.

That second case is the whole problem. It is not one lucky guess that
survives; it is an entire connected patch of the plane — every guess close
enough that the straddling samples cannot testify against it. Keeping only
the single best-scoring guess would amount to pretending the samples pin the
edges to a point, when each sample is an average over more than a tenth of
a second. The honest output is the *whole surviving patch*, and the pulse's
timing bound is the **worst edge displacement found anywhere in it** — the
most the edges could have moved without the recording noticing.

Which creates an obligation that drives everything in the next two
subsections: the patch must be found *without gaps*. A missed pocket of
surviving guesses could contain exactly the displacement that should have
set the bound, and the bound would come out too small — an error in the
flattering direction, which is the only kind this project treats as fatal.

### 4.3 What "fits well enough" means: the score and the waterline

"Ruled out" and "survives" have been doing work above; here is the actual
test, so neither word carries a hidden meaning.

Every guess gets a **score**, and lower is better. For each sample: take the
**miss** — the recorded height minus the height this guess predicts — and
divide it by the machine's ordinary sample-to-sample scatter — measured
once per capture, from the quiet stretches between pulses — so the units
become "how many noise-widths off." Then pass that through a penalty function and add the
penalties up over all the samples covering the pulse.

The penalty function is deliberately two-part: it grows with the *square* of
the miss while the miss is small, and only *linearly* once the miss is
large. The reason is a specific failure mode. If the penalty stayed
quadratic everywhere, a single glitchy sample — a stray interrupt, a
scheduling hiccup, one interval that read absurdly high — would contribute a
gigantic penalty and drag the best-fitting guess toward explaining that one
sample at the expense of all the others. Going linear for large misses caps
how much any one bad sample can distort the fit, without ignoring it.
A guess that explains every sample perfectly scores near zero; a guess whose
straddling-sample predictions are badly wrong piles up penalty fast.

Concretely, the code uses the **Huber penalty** with crossover *k* = 1.345.
For a miss of *m* noise-widths, the penalty is `m²/2` while `|m| ≤ k`, and
`k × (|m| − k/2)` beyond it. A miss of 0.5 noise-width costs 0.125. A miss
of 6 noise-widths costs 7.1654875 rather than the 18 that a square penalty
would charge. The linear branch is what stops one stray interval from buying
the fit.

Two gates use that score.

**The first asks whether there is a pulse at all.** Compute the score of the
flat "nothing happened here — it was baseline the whole time" explanation,
then compare it with the best guess's score. The best guess must come in
below **half** the flat explanation's score, or the pulse is declared not
detected and the capture is refused. This is a deterministic model-fit gate,
not a calibrated statistical significance test: the pulse model's loss must
be less than half the flat model's loss. With a real pulse the margin is not close:
a flat explanation has to absorb the entire step — every plateau sample
counted as a large miss — so it accumulates penalty on a different scale
entirely. That is precisely why failing this gate means something went badly
wrong rather than "the fit was mediocre."

**The second defines the surviving patch,** and its threshold is *not* an
absolute number. It is set relative to the best guess found:

```
limit = best score + max( 1.0 , 5% of best score )
```

A guess survives if its summed Huber loss is no more than
`max(1.0, 5% of best score)` above the best score. The `1.0` is one unit of
total loss; it is not one sample or one noise-width. One normalized
one-noise-width residual contributes 0.5 unit, for example.

Both branches matter, so work them. If the best score is 38.0, then 5% of
it is 1.9, which beats the 1.0 floor, and the limit is 39.9: with 38
noise-widths of unexplained miss already on the table, a guess that adds
another 1.9 is not meaningfully worse. If instead the best score is 4.0 —
an unusually clean pulse — then 5% is 0.2, the floor of 1.0 wins, and the
limit is 5.0. That floor is what keeps the patch honest when the fit is
nearly perfect: a guess whose total penalty is within one loss unit of the
best cannot be told apart from it *by this data*, and pretending otherwise
would manufacture precision out of a good night.

A useful picture: think of the score across the plane as a landscape with a
valley, the valley's bottom being the best guess. The limit is a
**waterline** just above the bottom; flood the valley to that line, and the
flooded region is exactly the surviving patch. One consequence to state
plainly rather than have someone discover it as a gotcha: the waterline is
defined in terms of the best score, so the detector must find the bottom of
the valley first and flood afterwards.

### 4.4 Mapping the patch in blocks: what "converged" means

The patch has to be found, and there are infinitely many guesses in the
plane. Testing them one at a time is impossible. Testing a finite grid of
them is worse than it looks: whatever spacing you choose, everything
*between* your grid points goes untested, and the patch's true extent can
poke out between two grid points that both passed. That is the gap the
obligation in §4.2 forbids.

So the detector tests guesses **in blocks**. A block — a rectangle of the
plane — is nothing mysterious: it is a range of start-shifts crossed with a
range of stop-shifts. *"Every guess in which the start edge was between
−500 ms and −250 ms off, and the stop edge between +250 ms and +500 ms
off"* is one block, and it contains infinitely many individual guesses.

The reason blocks work is a property of the fit itself. Sliding an edge
changes a straddling sample's predicted height **monotonically** — in one
direction only, never doubling back: push the start edge later and that
sample's predicted average only ever falls. Because of that one-directional
behaviour, the detector can compute a rigorous lower bound on the score of
every guess in a block. It does not sample the block; it bounds it. For each
recorded interval, the two opposite corners of the block give the smallest
and largest predicted power. If the recorded power lies between those
predictions, that interval's minimum possible miss is zero. Otherwise the
minimum miss is the distance to the nearer prediction. The detector converts
each minimum miss to noise-widths, applies the Huber penalty above, and sums
the per-interval minima. This sum can be loose because different intervals'
minima may require different guesses, but no single guess in the block can
score below it.

Work the straddling sample from §4.1. Its baseline is 2 W, plateau is 40 W,
interval width is 112 ms, recorded average is 12.18 W, and the commanded
overlap is 30 ms. Over a block of start shifts from −10 ms to +10 ms and
stop shifts from −10 ms to +10 ms, the stop edge remains beyond this
start-edge sample, so its possible overlap ranges from 40 ms down to 20 ms.
Its predicted average
therefore ranges from `2 + (20/112) × 38 = 8.79 W` to
`2 + (40/112) × 38 = 15.57 W`. The recorded 12.18 W lies inside that range,
so this interval contributes a zero lower-bound penalty for the block. For a
block of start shifts from +30 ms to +60 ms and stop shifts from −10 ms to
+10 ms, its possible overlap is zero and the only prediction is 2 W; its
smallest possible miss is therefore 10.18 W.
The implementation divides that miss by the capture's measured scatter before
applying the penalty, exactly as the score definition requires.

That complete lower-bound computation for one rectangle is one
**evaluation**, and it is the unit in
which all search effort below is counted. Each evaluation licenses one of
three moves:

- **Reject the block.** If even the best score achievable inside it sits
  above the waterline, then every guess inside it is ruled out — infinitely
  many guesses eliminated by one evaluation. This is the move that makes an
  infinite search finite: one evaluation can kill a quarter of the plane.
- **Split the block.** If the block cannot be rejected, some guess inside it
  might survive, so cut it in half and evaluate each half. Blocks that
  straddle the patch's boundary cannot yet be rejected, so they keep splitting, closing in
  on the true edge of the patch from outside.
- **Retain the unresolved block.** Once a block whose lower bound does not
  exceed the waterline is down to 0.1 ms on a side, stop splitting and count
  its *entire extent* into the enclosure. The block is unresolved, not proved
  to survive point by point. Retaining all of it can only make the final bound
  larger, never smaller.

Run to completion, every point in the configured `[-0.75 s, +0.75 s]²`
search square ends up either provably ruled out or enclosed by a retained
cell; the detector does not search an unbounded plane. **That completed map is what
"converging on a pulse" means** — not "the search found a good answer," but
"the configured search square has been completely classified without a gap."
The word is used in that exact sense everywhere below.

The following schematic names the spatial search. It is not measured data;
the irregular patch and block locations only show the algorithm's roles.

```text
                  stop-edge shift (seconds)
                           +0.75
                             ^
        configured square    |  R = block rejected in one evaluation
       +---------------------+---------------------+
       | RRRRRR              |              RRRRRR |
       | RRRRRR        +-----S-----+         RRRRRR |
       |               | ......... |                |
       |               S . u u u . S                |
       |               | . u x u . |                |
 -0.75 +---------------|-. u u u .-|---------------> +0.75
       |               S ......... S       start-edge shift (seconds)
       |               +-----S-----+                |
       |                    <----->                  |
       |               worst-edge scalar            |
       | RRRRRR              |              RRRRRR |
       +---------------------+---------------------+
                             v
                           -0.75
```

Figure 4, the plane of edge hypotheses:

- The horizontal arrow is start-edge shift; the vertical arrow is stop-edge
  shift, both spanning the configured −0.75-second to +0.75-second square.
- The axes' crossing is the origin: both edges at their commanded positions.
- `x` is the lowest-score edge pair found before the enclosure search.
- Dots form the surviving patch: point hypotheses whose score is at or below
  the waterline.
- `R` marks a large block rejected because its lower bound exceeds the
  waterline.
- `S` marks a block that overlaps the patch's edge and must be split.
- `u` marks a retained unresolved cell at the 0.1-millisecond resolution;
  its full area is included even though not every point was proved to survive.
- The solid box around the dots and `u` cells is the final rectangular
  enclosure of all retained cells.
- The double-headed arrow from the enclosure toward the origin represents the
  worst-edge scalar before the clock-anchor term is added.

### 4.5 From one pulse to one capture's b_fiducial

Three steps turn 59 completed maps into the single number that everything
downstream inherits.

**First, widen for the command stamps.** The map bounds what the *samples*
can say about the edges. But the commanded times themselves were written by
software and carry their own small uncertainty, so the patch is widened once
more by the recorded uncertainty of the pulse's own command timestamps.

**Second, collapse to a worst-edge scalar.** A pulse's map gives a range for
the start edge and a range for the stop edge, and neither is necessarily
symmetric — a pulse might permit start shifts from −4 ms to +9 ms. The
**worst-edge scalar** is the single largest displacement magnitude over both
ends of both ranges: 9 ms, in that example. Take the largest such value over
all 59 pulses, and that is the capture's b_fiducial, applied symmetrically
as ±b_fiducial.

Why the worst rather than the average, when averaging 59 measurements is the
usual way to get a better number? Because b_fiducial is not an estimate of a
typical error; it is a bound on the error at *one* boundary. A phase
boundary in a real measurement happens once and gets no averaging — it lands
where it lands, and the honest question is how badly a single boundary can
be misplaced. Averaging would answer a question nobody asked.

**Third, add the anchor.** The capture's clock-anchor bound (section 5) is
added on top, because everything above was measured relative to a timeline
whose own alignment is known only to within that bound.

Across the 17-member corpus that grounds the current **acceptance artifact** —
the issued machine-readable record of the accepted captures, thresholds, and
estimator fingerprints —
b_fiducial ranges from 0.0232 s to 0.0329 s.

### 4.6 The detection budget: paying for the map, and what the price reveals

The **detection budget** is a cap on the *total* number of evaluations the
detector may spend across all 59 maps in a capture. It is currently 165,000.
Exceed it and the capture is refused.

For scale: a healthy pulse's map finishes in roughly two thousand
evaluations, and every healthy capture in the current 17-member corpus
lands between 115,449 and 137,535 — call it 115,000 to 138,000, or about
2,000–2,300 per pulse.

**Why cap the work at all?** Two reasons, and neither is "to save time."

*Reproducibility.* Without a cap, a bad trace makes the search grind on and
on, and how long it grinds — and whether the operator loses patience and
re-runs it — depends on how fast the machine happens to be and how patient
the human happens to feel. Two people with the same bytes could then reach
different **verdicts** — a verdict being the recorded accept-or-refuse
decision, the thing the instrument actually publishes — which is not a
property a measurement is allowed to have. The 165,000-evaluation cap makes
the primary work count deterministic. A separate 120-second monotonic wall
deadline can also refuse a trace, so sufficiently slow or pathological hosts
are not guaranteed the same verdict.

*Effort as diagnosis.* How much work the map needs is itself a measurement
of trace quality. A clean pulse train has crisp steps, so most of the plane
sits far from the waterline and dies in a handful of evaluations. When a
capture needs far more work than any healthy capture ever has, that is not a
slow computer; it is the data reporting that the pulse edges are genuinely
smeared or ambiguous — something on the machine blurred the very steps the
map is trying to trace. The budget converts that into a refusal instead of
leaving it as a footnote nobody reads.

**Why refusal is total, never partial.** When the budget runs out
mid-search, the tempting move is to keep whatever map exists at that moment
and publish the worst displacement found so far. That would be exactly
backwards. The unexplored blocks are the ones that could not be cheaply
ruled out — the most suspicious territory on the plane — and any of them
might contain the displacement that should have set the bound. A bound taken
from an unfinished map can therefore only err in one direction: too small,
i.e. claiming better timing than was demonstrated. So the capture is refused
as **non-convergent**, whole, and the refusal is recorded rather than
discarded.

**The night the budget proved itself.** On 2026-08-17→18, the very first
live capture under the pulse detector then in force hit the budget and was
refused. The diagnosis that followed is the best short course on this
project's method:

1. *Don't retry.* Rerunning until a capture passes is selection on the
   outcome — the cardinal sin. The refused capture's artifacts were
   preserved and studied instead.
2. *Discriminate instrument from environment.* Issued corpus captures —
   captures already published as part of the acceptance artifact, and so
   known-good — were replayed through the same detector. They hit the same
   budget. The previous detector generation, and the new one with a raised
   cap, both converged on all of them. Conclusion: the trace was fine (its
   pulse signal-to-noise matched the corpus); the budget had been set below
   the real workload's demand, a fact no repository test could expose
   because raw calibration traces are too large to live in the repository.
3. *Correct from the complete evidence, not until it passes.* Every retained
   raw trace on the machine was swept — 40 unique captures, of which 34
   converged fully and 6 refused before fitting; the maximum observed demand
   was 137,189 evaluations (under the anchor estimator then in force); the
   budget was reset to 165,000, about 20% above that maximum, with the
   margin exceeding the entire observed spread.
4. *Then, and only then, re-derive.* The refused capture, re-evaluated under
   the corrected budget, converged on all 59 pulses and yielded
   b_fiducial = 0.0309 s under the anchor estimator then in force. (That
   number moved when the estimator was replaced the next day — section 5.)

A safety gate refusing on first contact with reality, the refusal
diagnosed rather than overridden, and the fix grounded in the full corpus:
that is the intended shape of every failure this instrument will ever have.

**The budget was re-earned, not inherited.** When the anchor estimator was
replaced (section 5), the sweep that justified 165,000 became invalid — it
had been run under the old anchors, and the detector walks the trace from
the anchor, so different anchors mean different searches — so it was redone.
The budget stayed at 165,000, now standing on the claim-bearing population's
own numbers: the 17 corpus survivors demand between 115,449 and 137,535
evaluations, median 122,097, and 165,000 is that maximum plus about 20%.

**And then a capture that genuinely deserved refusing.** One later
validation-only capture — one collected to exercise the machinery rather
than to support a number — resolves its clock anchor cleanly, passes every
retained-artifact check (the hash-linked record of where each file came from
and whether its bytes later changed), and then demands **1,282,827**
evaluations: 9.2× the next highest demand of any capture the current anchor
method can resolve at all
(a set wider than the 17 survivors). It is recorded as refused rather than
admitted to any claim-bearing use. Without the budget, that would have been several minutes of
grinding ending in a bound of dubious meaning; with it, the capture was
refused on the spot, with the effort count recorded as the reason.

Raising the cap to swallow it was considered and rejected. A ninefold
increase would make a wall-clock deadline the real limit and the failure
mode dependent on how fast the host machine happens to be — precisely the
reproducibility property the budget exists to provide. A budget is a safety
gate only if the population it protects sets it, not the worst thing it ever
saw.

### 4.7 Clock discipline

The anchor between the two timelines is only valid if neither clock moves
during a capture. The system clock's network-time synchronization can
*slew* the clock mid-window — smoothly speeding it up or slowing it down to
walk it toward a time server's idea of now — which silently stretches or
compresses the timeline and moves energy between operations. So during
measurement windows, network time is disabled and re-enabled through two
narrowly authorized administrator commands (the only two privileged clock
operations the measurement account can run without a password; the
authorization was installed and exercised as part of operator
qualification — the scripted sessions in which the human running the
instrument demonstrates each privileged step and leaves evidence of it).
The anchoring machinery itself carries a 5 ms ceiling: an effective anchor
bound greater than 5 ms refuses; exactly 5 ms is allowed. How that
anchor is computed, and what happened when its model turned out to be wrong,
is section 5.

### 4.8 Bracketing and drift

A single calibration is a snapshot, and a window lasts hours. Over hours the
instrument can **drift** — its timing behaviour changing slowly as the
machine warms, as background state settles, as anything else moves — so a
bound measured at 9 p.m. is not automatically a bound that describes 3 a.m.
Real windows are therefore **bracketed**: one calibration capture before the
science members and another after, pinning the night's timing behaviour
between two measured values. The timing **allowance** applied to the night's
data — the uncertainty attached to every phase edge — is not their average.
It is the larger of the two measured bounds, plus the larger of their observed
difference and the historical **bracket screen** — a threshold used here as a
minimum allowance. In symbols, if the
two bounds are *b*pre and *b*post, the allowance is
`max(bpre, bpost) + max(|bpre - bpost|, bracket screen)`. The first term pays
for the worse endpoint; the second pays for movement across the window, while
preventing accidental close agreement from buying an unjustifiably small
allowance.

Worked with the two endpoint bounds read later in §12:
`b_pre = 0.028145704403191807 s` and
`b_post = 0.029425288011457773 s`. Their difference is
`0.001279583608265966 s`, below the `0.009724 s` screen, so the screen wins.
The allowance is therefore
`0.029425288011457773 + 0.009724 = 0.039149288011457773 s`, about 39 ms of
permitted displacement at every phase edge for that historical window.

That allowance is never permitted to fall below the bracket screen of
9.724 ms. This screen is a floor under the allowance, and it exists because two brackets
can agree closely by luck. Without the floor, a fortunate pair of captures
could buy a tighter bound than the instrument has ever demonstrated it
deserves. The 9.724 ms comes from the historical range of 17 bounds derived
under the same calibration generation — sections 5 and 7 explain where the
number comes from and why it changed.

And if the brackets disagree by more than 10.164835 ms, the entire window is
refused. The exact registered value is `0.010164834757777545 s`, the 99%
two-draw prediction limit derived for the 17-capture acceptance corpus and
stored in the issued acceptance artifact rather than copied into each
consumer. That much movement means the instrument was not the same
instrument at both ends of the night, and no single allowance honestly
describes both halves.

The current checkout contains a **bracket-binding record** builder and its
checks. This record fingerprints the fixed plan, the finalized calibration
ledger containing both endpoint captures, the exact run directory, and the
**evidence-root identity** — the fingerprint at the top of the retained-record
chain for this window, which prevents a binding from being satisfied by a
different night's evidence tree. When supplied, the whole-window verdict consumes that
record, and analysis finalization compares the record evaluated into the
verdict byte-for-byte with the supplied binding. This closes a whole-window
substitution gap: individually valid plan, calibration, run, and verdict files
cannot be borrowed from different windows and assembled into one apparently
valid result. The reusable mechanism is implemented, but the current locked
comparison pack's verdict command does not pass the binding argument; its plan
only reserves an empty post-collection fingerprint slot. Treat the complete
pack-to-verdict lifecycle as planned until a successor pack wires that input.

## 5. The clock anchor, and the day its model was falsified

**What an anchor is.** Two clocks are involved in every capture and neither
knows about the other. The sampler labels its rows with the system's
wall-clock time — the ordinary time-of-day clock, the one network
synchronization adjusts — but measures how long each row lasted on its own
**monotonic** timeline: a counter that only ever advances, at a steady rate,
and is never adjusted by anything. The workload, meanwhile, stamps its pulse
commands in wall-clock time. To integrate energy between event boundaries
you must know how those two timelines line up, and nothing in the operating
system tells you. The **clock anchor** is the measured relationship between
them — and because it is measured, it is reported as an *interval*, never a
point. Its **half-width** — half the width of that interval, the "±" you
would quote — is part of every bound the instrument publishes.

**How the evidence arrives.** Each time the wall clock rolls over a whole
second, the sampler prints that whole-second wall-clock label on the row
whose averaging interval just ended, and every row also reports how long it
covered in the monotonic timeline. Each row therefore says: *the very first
sample ended somewhere in this one-second-wide window of wall time, shifted
back by the elapsed time accumulated since*. A 197-second capture yields
about 197 such statements. In addition, five system timestamps taken around
the capture (spawn, first parse, sampling start, stop, final parse) bracket
the same quantity causally — they are events that provably happened before
or after the sampling, so they fence the answer from both sides. The anchor
is whatever survives all of that evidence at once.

**The old method, and its hidden assumption.** The previous estimator — the
*censored-intersection* method, so called because each row's statement is a
one-second window that has been cut down ("censored") by what the other
evidence allows — intersected those windows with the causal bracket: if what
remained had positive width, its midpoint became the anchor and its
half-width the bound; if what remained was empty, the capture was refused.
The method is sound *given* one assumption that was never stated as an
assumption — that one second of wall time is exactly one second of the
sampler's elapsed timeline. Rate = 1.

**The falsification.** In that six-capture diagnostic sitting, the wall clock
ran about **7 parts per million** fast against the monotonic timeline. Parts per million is the
natural unit for a difference in clock *rate*: 1 ppm is one microsecond per
second, so 7 ppm is seven microseconds gained every second. Over a
197-second capture that accumulates roughly 1.4 ms of stretch, and the
machine's own records agree: the wall-versus-monotonic spans logged during
the diagnostic probe were 1.442–1.447 ms. The intersection windows, after
the causal bracket, are only about a millisecond wide. A systematic stretch
the same size as the thing you are intersecting does not perturb the answer;
it destroys it. Six back-to-back captures under identical conditions made it
visible: two resolved, with intersection widths of +780 µs and +1.039 ms,
and four came back empty, at −4 µs, −159 µs, −210 µs and −313 µs (a negative
width meaning the constraints had crossed past each other — no time at all
satisfied them). Same machine, same protocol, same sitting — a coin flip.

That alternation was the loud symptom: good captures refused for no physical
reason. The silent problem was worse. When the intersection *did* survive, its
midpoint sat off by roughly half the accumulated drift, in the same direction
every time. Every accepted anchor carried a bias nobody could see.

**The replacement: solve for the rate instead of assuming it.** The current
method — *rate-aware set membership* — treats the answer as a pair, **(rate,
offset)**: how fast the wall clock runs relative to the monotonic one, and
where the two timelines coincide. It asks which such pairs are consistent
with *every* constraint at once, and returns the entire **feasible set** —
the complete collection of pairs that violate nothing. That set is
**convex**, which here has a practical payoff rather than a decorative one:
a convex set has no holes and no separate islands, so finding its extreme
edges genuinely finds all of it, and no candidate can be hiding in a pocket
the search never visited. The search runs in exact rational arithmetic —
fractions of whole numbers, carried exactly, never rounded to a
floating-point approximation — so no rounding error can invent or destroy
feasibility at the margin.

The anchor interval is the projection of the two-dimensional feasible
`(rate, offset)` set onto anchor position; the fitted-rate interval is a
separate projection. On the afternoon diagnostic probe (the disciplined
capture the science review examined), the fitted constant-rate interval was
+7.243 to +7.285 ppm. Its width does not by itself bound arbitrary mid-capture
rate changes; the model separately allows up to 250 µs of non-affine departure
and relies on authenticated network-time-off evidence. If no rate
reconciles the constraints, the capture is refused. The method never picks
the least-bad rate.

**What is fixed around it, so the fit cannot absorb anything it likes.**
A model with more free parameters can explain more — including things it
should be refusing. Three constraints stop that. Departure from a
straight-line relation between the clocks is capped at 250 µs, so the fit
cannot quietly become a curve that bends around bad data. A fitted rate
beyond ±50 ppm *refuses* rather than being clipped to the limit, because a
clipped value would silently present an absurd fit as a marginal one. And
neither constant may be widened after a failure is observed without
declaring an entirely new method — otherwise the limits would drift outward
one refusal at a time until they constrained nothing.

The fit is also not a substitute for turning network time off: the model
assumes nothing is steering the clock mid-capture, and the enforced
network-time-OFF window of §4.7 is what makes that assumption
**admissible** — permitted to be relied on, because something independent
enforces it, rather than merely hoped for.

One further term is easy to mistake for redundancy. The anchor's half-width
says *where the timeline starts*; a separate term pays for the two clocks
drifting apart *during* the capture. Both are needed, because the pulse
detector walks forward through the trace from the anchor's midpoint at the
monotonic clock's own rate, while the pulse commands it is comparing against
are stamped in wall-clock time — so an error in the starting point and an
error that accumulates with elapsed time are two different quantities.

**Paying for the rate is what makes the bound honest.** Across the
re-derived corpus the anchor term rose by 0.311 ms on average, against
per-capture bounds in the 23–33 ms range (§4.5). On the calibration fixture shared
by the whole test suite — a small stored input used by every test so they
all judge the same bytes — the very same inputs now yield a bound 3.09
microseconds wider. That figure already includes one numerical detail that
was paid for rather than deferred: the padding constant was raised from
1 nanosecond to 1 microsecond, to cover the rounding error you get when a
timestamp counted from 1970 is stored as a double-precision number.

Individual b_fiducial values moved *both* ways, because the pulse detector
re-fits the trace under a shifted anchor: 6 of the 17 issued members
tightened, including the one that becomes the new corpus maximum. The
padding raise by itself moved every bound computed under the new anchor
method — "anchor-v3" in the artifacts — outward by 1 µs minus 1 ns; under
that change alone nothing tightened and no capture changed status.

**Refusals of previously accepted captures are the correction working.** The
derivation corpus went from 19 members to **17**. Two captures the old model
had accepted now refuse, for a physical reason rather than a numerical one:
their timestamps admit *no single rate at all*. One is constrained to
[−1.1, +5.2] ppm by its early stamp pairs and to [−16.04, −15.99] ppm by its
long baselines — two demands that do not overlap, disjoint by more than
15 ppm — with its wall-versus-monotonic offset moving −3.18 ms mid-capture.
The **slack** needed to make it feasible — the smallest amount by which the
constraints would have to be loosened before any rate satisfied them all —
is 5.612 µs. The other runs at −9.2 ppm early and −2.27 ppm late; 1.873 µs.

The mechanism is that the wall clock was being actively *steered* during
those captures — network time synchronization walking it toward a server's
time while the capture ran — before clock discipline existed as a protocol
step. The retained-artifact record agrees independently: the earliest record on this
machine of the clock being pinned — network time disabled and that fact
written down as evidence — postdates both captures. For contrast, of
the 43 captures in this lineage that were replayed, 41 need exactly zero
slack. The
model fits an ordinary capture to sub-microsecond consistency and refuses
precisely the captures where something was moving the clock.

**Which direction a correction moves your own thresholds is diagnostic.**
One of the two refused captures was the *corpus maximum* under the old model
(b_fiducial 0.033559 s), so removing it makes the instrument's screens
**stricter**: the maximum falls to 0.032898 s and the bracket screen tightens
from 0.010818 s to 0.009724 s. A correction that discards your most
contaminated data point and leaves you a harder bar to clear is the shape of
an honest one; be suspicious of the opposite — a correction that
conveniently loosens every threshold it touches deserves an auditor.
Likewise, 11 of the 32 captures that survived re-derivation produced
intervals that no longer contain the old method's accepted point — exactly
what removing a bias should do, not an anomaly to be explained away.

**The lesson worth carrying away: replay is not validity.** Every stored
bundle from the old era — "era" meaning the generation of capture pipeline
that produced it, built properly in section 6 — still replays perfectly:
feed the old bytes to the old estimator and you get the old numbers, to the
last digit, forever. What died was not reproducibility but
*claim-eligibility*, because faithfully reproducing a computation whose
model is false reproduces the error faithfully. That has a concrete
consequence: each corpus member's bound is the new derivation itself,
**not** the larger of the old and new values. Taking the maximum would look
conservative while smuggling the falsified model's numbers back in wherever
they happened to be bigger. A superseded model is superseded, not demoted to
a floor.

## 6. What a bundle remembers: capture eras and the claim barrier

The section above leaves an obvious question: hundreds of stored measurements
on this machine were taken under an estimator now known to be wrong. What
happens to them?

**Every bundle carries its own capture-pipeline identity.** A **capture era**
is one generation of the capture pipeline — the particular combination of
sampler handling and anchor method in force when the bytes were recorded. A
stored bundle records its era in two inseparable halves: the anchor method
that produced it, paired with a **schema label** naming the shape of the
metadata record itself. One canonical table — `SCHEMA_FOR_ANCHOR_METHOD` in
`joulewise/uncertainty_evidence.py` — has one row per generation, pairing an
anchor-method name with the schema label emitted beside it. The *method* is the single key
every piece of code chooses its behaviour from, so nothing anywhere decides
what to do by reading the label alone.

If a bundle's label and its method disagree it is refused outright, rather
than resolved in favour of either. The record is lying about itself, and
there is no honest way to guess which half is true — a bundle carrying one
generation's label and another generation's method might be a mislabelled
good bundle or a correctly labelled corrupted one, and those want opposite
treatment. Where
the capture machinery produced no such evidence at all, no era is
synthesised: the evidence is marked explicitly incomplete, because inventing
a plausible label is the one failure this design must never have.

**Two questions, deliberately kept apart:** *can this bundle be verified?*
and *may this bundle support a claim?*

- **Strict verification is era-faithful, forever.** Every stored bundle is
  re-derived under *its own* recorded method — legacy bundles under the
  legacy replay and current bundles under the current derivation — and
  crossing an era against another era's method refuses. The historical
  bundles therefore keep their audit value: they still
  authenticate — meaning their stored fingerprints still match a fresh
  computation over their bytes — they still replay byte-exactly, and their
  retained-artifact chains remain checkable. Nothing was rewritten, relabelled,
  or deleted.
- **Claim admission is a separate, mechanical barrier.** "Admission" is the
  narrow question of whether a bundle may stand behind a published number.
  Supporting one requires the *positive presentation* of the current
  claim-bearing method: the bundle must actively show it, from a closed
  set — an explicitly enumerated list, one member long today. Absence is not
  permission; a bundle that says nothing about its era is refused exactly
  like one that names a retired era. One shared test implements this, and the
  claim-side consumers — including analysis, floor extraction, and the
  whole-window check — all call that one test. None of
  them re-implements it or writes the method name into its own code, so the
  barrier cannot quietly decay in one place while still holding in another.

**The problem that forced it into existence.** Before this, superseded
bundles were kept out of claims by per-window policy documents — that is, by a
human remembering to apply a rule. That works until the night it doesn't. A
policy document is not a gate.

**Why there are two refusal reasons and not one.** The barrier distinguishes
`capture_pipeline_superseded` — an authentically stored bundle whose method has
been retired — from `capture_pipeline_absent`, where there is no such evidence
at all. Collapsing them would have been simpler and also false: a superseded
bundle may record that its anchor resolved under its own historical method, so
filing it under "anchor unresolved" would contradict its authenticated
metadata. Refusals are published results, so a refusal reason must be true
about the artifact it names, not merely convenient.

## 7. The calibration acceptance: pinning the instrument's identity

A bound measured by one version of the estimator code says nothing about a
different version. So the instrument's identity is **pinned** — recorded as a
cryptographic fingerprint, so that any later change is detectable — by the
**calibration acceptance artifact**, currently
`d079_calibration_acceptance_v2_n17_r6`, whose own file hash begins
`0227bca3`. (A hash, throughout this document, is a short fixed-length
fingerprint computed from a file's exact bytes: changing one byte normally
produces an unrelated-looking fingerprint. Finding a different file with the same
SHA-256 is considered computationally infeasible with current methods; it is
not mathematically impossible. It is how every "these are the same bytes" claim
below is checked.) The artifact records:

- the 17-member derivation corpus (every member's b_fiducial, byte-exact),
- the decision thresholds derived from that corpus,
- and the SHA-256 hashes of the four estimator source files that computed
  them: the fiducial estimator of section 4, the uncertainty machinery, the
  *sampler adapter* (the code that parses `powermetrics` output into samples),
  and the **reducer** — the code that turns raw samples into per-operation
  energy numbers, described in section 12 step 5.

Any change to any of those four files — even a one-line comment — makes
every downstream consumer refuse with a *staleness* error: a refusal meaning
"the code that produced this artifact is not the code now on disk, so the
artifact's numbers are not this instrument's numbers." That is on purpose. A
changed estimator is a different instrument, and a different instrument does
not inherit the old instrument's evidence.

When an estimator change is genuinely wanted (the detection budget of §4.6
was one), the acceptance is **reissued**. The reissue replays all 19 members of the
*replay set* — the predecessor generation's complete corpus. It is kept
whole on purpose: it includes the two captures the corrected anchor
refuses, so every reissue must reproduce not only the 17 surviving values
but the two refusals *as refusals*. Each member is re-authenticated from
their raw artifacts under the new code, every derived quantity is compared
against the predecessor's record with zero mismatches tolerated, and the new
artifact publishes a **delta**: an explicit list of exactly which pins
*rotated* — that is, which recorded fingerprints were replaced — and what
they were before and after. The reissue is "science-neutral by construction":
if anything beyond the intended code pins differs, it does not issue at all.

**The generation chain.** Because the pin rule has no exceptions, the
artifact has a **lineage** — a chain of issued **generations**, each naming
its predecessor — and every link is a document that can be opened and
fingerprinted. The anchor replacement in section 5 is the link that changed
the scientific corpus and tightened its screens. Later links changed governed
code fingerprints without changing the derived science. Each such neutral
reissue carries a named predecessor, the before-and-after fingerprint of every
source file that changed, and a complete replay showing that every anchor
bound, evaluation count, final pulse bound, and **disposition** — whether a
capture converged or was refused, and why — stayed identical. Predecessor
generations remain byte-identical; a superseded generation is retired as the
live artifact, never edited.

**Policy constants are resolved, never copied.** A trap lives in that table:
the bracket screen was 0.010818 s under the 19-member generations and is
0.009724 s under the 17-member ones. If any consumer held that number as a
literal in its own source code, historical replays would silently start
judging old data by new thresholds — the past re-tried under rules that did
not exist when it happened. So no such literal exists anywhere in the code that
computes and validates floors: an automated **regression test** — a test
whose only job is to fail if a specific past mistake ever reappears — names
the three source files of that lane and forbids both digit strings from
appearing in any of them. (One table in
`joulewise/calibration_bracketing.py`, the **acceptance registry**, lists every
issued acceptance generation and its exact file fingerprint. A companion table
in the same file maps each generation to the bracket screen and allowance rule
it registered. This file is the one place those digits legitimately appear, so
the scan deliberately skips it.)
Every consumer instead *resolves* the screen and the allowance rule from the
generation that the supplied artifact itself names. An artifact whose
identity is not in the registry refuses; an artifact whose stated screen
disagrees with the registered value for its identity refuses too, rather
than a winner being chosen between them. That is what lets the live
instrument move while every historical replay stays byte-exact: the past is
judged by the rules of the past, by machinery rather than by memory.

## 8. Floors: what the instrument may claim to distinguish

A **detection floor** is the empirically demonstrated largest false energy
difference the complete measurement system reports between identical runs for
a given operation family on this exact software stack. Two of those words are load-
bearing. An **operation family** is a named kind of measured work — "decode,"
or "prefill at a 256-token prompt" — not an individual run. A **stack**, as
in section 1.2, is the full named set of software the measurement ran on,
and for a floor it is named exhaustively: exact model artifact hash, runtime
version, weight quantization (the numeric precision the model's weights are
stored at — a different sense of the word from the sampler's quantization in
section 3), tokenizer, OS build. A floor belongs to one family on one stack
and nowhere else.

Note also what the floor is *not*: it is not the sampler's noise floor. It
is the *system's* floor, including attribution error, drift, and everything
the protocol could not remove.

Build that limit from the physical error before using it as a decision rule.
If a phase boundary may be displaced by *b* seconds and the power changes by
ΔP watts across that boundary, then as much as `b × |ΔP|` joules can move
between the neighbouring phases: watts multiplied by seconds are joules. The
paper's retained diagnostic reconstruction supplies a real timing value from
one calibration capture: `b_fiducial = 0.030067931757111657 s`. Using the
paper's representative phase-edge power step of `33 W` gives
`0.030067931757111657 s × 33 W = 0.992241747985 J`, or about `0.99 J`, at
that edge. This is not a universal floor and not a new result; it is a worked
reconstruction of the attribution contribution for that recorded capture and
illustrative power step. A claim-specific floor must still be measured from
the named operation family and software stack, then combined with the timing
allowance earned by that window.

**How a floor is measured:** by running designed workload pairs whose true
difference is known — most importantly *identical* pairs, called **null
pairs** because the true answer is exactly zero — and observing what the
pipeline reports anyway. Whatever spread of non-zero "differences" the
pipeline reports between workloads that were in fact the same is the
false-difference scale, measured rather than assumed. The floor is set above
it. This is the only honest way to answer "how small a difference can you
see": show what the instrument says when there is nothing to see.

**ABBA blocks.** The workhorse design: measure condition A, then B, then B,
then A, back to back — a **condition** being one of the two things being
compared, specified exactly (section 10 shows how). The problem it solves is
drift — the machine slowly
warming, background services settling, anything that makes later measurements
systematically differ from earlier ones regardless of condition.

Work it with numbers. Suppose A and B are genuinely identical (a null pair,
true difference 0 J), and the machine drifts steadily upward by 0.2 J per
slot, so the four slots carry drifts of 0.0, 0.2, 0.4 and 0.6 J on top of a
true 100.0 J.

- Simple alternation, **ABAB**: A reads 100.0 and 100.4 (mean 100.2); B reads
  100.2 and 100.6 (mean 100.4). Reported difference: **−0.2 J** — a
  difference invented out of pure drift, equal to exactly one slot of it.
- **ABBA**: A reads 100.0 and 100.6 (mean 100.3); B reads 100.2 and 100.4
  (mean 100.3). Reported difference: **0.0 J** — correct.

The trick is that ABBA gives each condition one early slot and one late slot,
symmetrically placed about the block's midpoint, so a steadily increasing
drift adds the same amount to both means and cancels in the subtraction.
ABAB does not: A always precedes B, so B always carries one extra slot of
drift. The 0.2 J is illustrative; its purpose is to make the invented
difference visible in the arithmetic. ABBA cancels drift that grows
linearly with time exactly, and any smoothly varying drift approximately —
"to first order," in the usual phrasing.

Floor measurements use both **absolute arms** — single-condition bundles,
which answer "how many joules does this cost," where there is nothing to pair
against — and ABBA comparison blocks, which answer "how much more does A cost
than B" while cancelling steady drift. The exact inventory is generated and
fingerprinted in its pack; an operator must execute that inventory rather than
reconstructing a run count from prose. The decision rules are written and
committed before data exists, so a threshold cannot be chosen after seeing
which value would permit a claim.

When the attribution term dominates the measured null-pair spread, the floor
is **attribution-limited**: clock alignment, not merely electrical noise, is
the binding constraint. That label is actionable. Improving the anchor or
edge calibration can lower such a floor; adding repetitions without changing
the timing bound cannot make the boundary uncertainty disappear.

**Per-phase, per-stack.** Floors do not transfer across phases, prompt
lengths, or stacks. The plan requires a 256-token prefill floor dependency,
but no 256-token floor artifact or transport rule is currently ratified; the
committed fields remain `EMPTY`.

## 9. The quiet machine: protecting the signal

Everything above assumes the machine's background is stationary and small.
It is not, unless forced to be. Resident daemons index files, analyze
photos, check for updates; the display and its friends draw power; other
software (including this project's own AI tooling) burns CPU. None of it
is distinguishable from workload energy after the fact — the rails report a
total, not an attribution by process.

The defenses, each aimed at a plausible operating mistake:

- **The screensaver story.** An early floor campaign showed that a video
  screensaver can contaminate calibration while making the contaminated
  majority look normal. The protocol now forces the display asleep
  (a transient display-sleep command, not a screensaver), verifies
  screensaver disengagement, and treats display state as a first-class
  fence — something checked and recorded before the window, not assumed.
- **The process census.** A **census** here means what it means anywhere:
  an enumeration of what is present, checked against what is allowed.
  Before quiet work, process probes look for keep-awake holders that could
  defeat the display fence, development agents, browsers, samplers or
  watchers, and maintenance services such as indexing, photo analysis,
  software update, and backup. The allowlists are tested against a recorded
  quiet-machine fixture so that a permanently resident system process is not
  mistaken for contamination merely because its name matches a broad pattern.
- **Power and thermal fences.** AC power at full charge (a mid-window
  charge-termination is a step change in the power picture — this was
  observed directly during an operator qualification probe), thermal
  state nominal before starting, followed by the plan's required untouched
  idle-settling period before calibration.
- **The agent quiesce rule.** To *quiesce* a system is to bring it to a
  quiet, settled state and hold it there. The project is developed largely
  by AI agents — and an agent session is background load like any other. No
  measurement starts while any agent session is active. An overnight
  non-claim first-light calibration **shakedown** — a deliberately small run
  used to expose faults rather than produce a research number — ran under a fenced driver with
  every development agent shut down. It did not exercise the full
  author-to-arm-to-verify-to-consume lifecycle; the dress rehearsal remains
  open. The driver's own censuses enter the
  **retained-artifact record**: the hash-linked account of where each file
  came from, what was true when it was written, and whether its bytes later
  changed. Section 11 uses that record as a gate input.

## 10. Fixed plans and the locking ceremony

**Why lock a plan:** the most seductive way to corrupt a campaign is to
adjust it after seeing data — drop an awkward run, alter the order, or repeat
an unlucky block. Each edit may sound defensible, but together they make the
plan a product of the evidence it was supposed to judge. The repository calls
the act of making the plan bytes final **freezing**, and calls its output a
**freeze receipt**. In plain words, the receipt is an authenticated fingerprint
of the exact plan bytes, their exact directory, and the readiness checks that
passed before collection. Change a byte or move to a different directory and
the receipt no longer authenticates that plan.

The campaign **pack** introduced in section 1.2 contains the configuration
files, their execution order, the calibration plan, definitions of conditions
A and B, and a tree of file fingerprints. Before the receipt is made, an
**identity projection** reads the actual model and runtime files that will be
executed and records their fingerprints. This solves a physical identity
problem: a filename can stay unchanged while the bytes behind it are replaced.
The projection lets a later gate compare intended bytes with executed bytes.

Receipts form a lineage rather than overwriting history. A successor pack
contains the predecessor's pack, plan, receipt, and identity fingerprints;
older packs remain checkable as historical records. The three current
successor packs each pin `freeze-0003.json`, and those receipt files and their
fingerprint sidecars exist in this checkout. That corrects the earlier status
that described the receipts as still outstanding.

**The statistical-plan gap in this checkout.** The intended model comparison
has two planned contrasts. Because testing more than one contrast increases
the chance that at least one looks positive by luck, the analysis proposal
puts both in one **multiple-comparison family** — a set judged together — and
uses the **Holm correction**. A **p-value** is the probability, under the
no-effect model the test assumes, of seeing a result at least as extreme as the
observed one. Holm sorts the two p-values smallest first, multiplies the
smaller by 2, leaves the larger as it is, then walks the list raising any value
to the largest adjustment seen so far. It declares an effect only where the
adjusted value is at or below 0.05. Worked: p = 0.02 and 0.04 become 0.04 and
0.04, and both clear 0.05; p = 0.03 and 0.04 become 0.06 and 0.06, and neither
does. That design is documented, but it is not yet an installed
pre-start guarantee here: the current **analysis manifest** — the
machine-readable file meant to name the analysis rule before collection —
still has incomplete family fields, and the plan-locking implementation does not invoke the
manifest validator. The campaign launcher has its own pre-run validation, but
that is later than the receipt and does not make the receipt attest the rule.
Therefore a current receipt proves the plan bytes and existing readiness rows,
not that this complete statistical rule is present. Collection must remain
blocked until a successor implementation makes that check part of locking and
a new receipt authenticates the corrected plan.

## 11. Arming, the window, and the operator

**Arming** is the final authorization to launch one already locked plan. Its
readiness rows must still be fresh when checked; a row about live machine state
cannot be borrowed indefinitely after the machine may have changed. A
successful arm produces a **capability**, a one-use launch token. The launcher
consumes it in the same indivisible operation that starts the run, so the
operator cannot check a token, change an input, and reuse the token.

A **window** is the uninterrupted physical interval in which the instrument
establishes quiet conditions, measures its timing before the workload, runs
the pre-ordered references and comparisons, measures timing again, and judges
the complete record. The software records the window as an ordered list of
stages and reserves the identity of the calibration pair before either
calibration runs, so neither endpoint can later be swapped for a capture from
another night. Grouped by what the operator is physically doing, the current
comparison window runs in this order:

1. **Pre-calibration.** Run the pulse train from section 4 and derive its
   timing bound under the clock anchor from section 5.
2. **Admission gate.** Authenticate that calibration and compare its own
   bound with the current acceptance limit. A missing, stale, malformed, or
   over-limit calibration refuses the window before science work begins.
3. **Opening references.** Run the fixed reference workloads that establish
   the starting level under the same machine state.
4. **Token-generation comparison.** Execute the first half of its A/B/B/A
   blocks, repeat the midpoint reference, then execute the second half.
5. **Comparison-boundary reference.** Repeat a fixed reference between the
   token-generation and prompt-processing comparisons.
6. **Prompt-processing comparison.** Execute the first half of its A/B/B/A
   blocks, repeat the midpoint reference, then execute the second half.
7. **Closing references.** Repeat the fixed reference workloads after the
   comparisons.
8. **Post-calibration.** Run the same pulse train again. Derive the bracket
   allowance from both endpoint bounds and refuse excessive movement.
9. **Whole-window verdict and retention.** Bind the fixed plan, finalized
   calibration ledger, exact run directory, and evidence-root identity;
   evaluate the window; then retain the authenticated record and backup.

[Figure 2: one measurement window](../paper/figures/fig2_window_timeline.svg)
shows that order. Its title names the calibration bracket, admission gate,
reference runs, and counterbalanced science stages; its subtitle says stage
widths are illustrative, not to scale, and contain no measured data. On its
white background, a horizontal session-time arrow
runs above blue-outlined pre-calibration and post-calibration boxes, a gray
admission box, an opening-reference box containing three narrow bars, a first
science box containing eight alternating light and blue bars — light for
condition A and blue for condition B, in the A/B/B/A order the inset expands —
followed by a one-bar
midpoint-reference box, a second eight-bar science box, and a closing-reference
box containing three bars. A blue bracket line spans from the pre-calibration
to the post-calibration, with two lines of text explaining that the pair bounds
timing drift and that science evidence remains conditional until the closing
calibration passes. Notes below say the order is fixed before data, references
track drift, and the widths are schematic rather than elapsed-time data. The
admission note names quiet state, power policy, thermal pressure, clock
anchoring, and calibration freshness, and says that a failed check refuses the
stage rather than allowing its evidence to support a claim.

The lower pale inset, titled "One A/B/B/A block, expanded," explains one such
block. Its horizontal
axis names four slots and its vertical axis names measured value. A rising
dashed gray line represents steady drift, with a short leader identifying it;
a dashed vertical blue line marks the two conditions' common average position
in time.
Four circles mark, from left to right, a white A, a blue B, a blue B, and a
white A. Two blue averaging brackets join the two A circles and the two B
circles. The surrounding notes explain that giving each condition one early
and one late slot cancels linear drift exactly, while curvature within a block
can leave a residual. They also write the block difference as
`(B1 + B2 − A1 − A2) / 2`, say that a positive value means B used more energy,
and say counterbalancing does not replace the measured whole-window allowance.
The circles, line, and box widths illustrate the method; they are not
observations from a campaign.

**What the operator model does and does not promise.** The working protections
target plausible mistakes: stale evidence, an unexpected process, a changed
file, the wrong stage order, a reboot, a clock event, or mismatched records.
The project is removing defenses whose only purpose is to resist a deliberately
dishonest operator with full control of the measurement account. Some such
code remains until that cleanup is implemented, so this is the operative
threat-model boundary rather than a claim that every older check has already
been deleted.

## 12. From samples to claims

After the window, **reduction** turns telemetry into physics: it integrates the
three processor rails between anchored operation boundaries, clips boundary
intervals, and attaches the bracket-earned timing allowance. Claim evaluation
then uses two gates. They answer different questions and must not be collapsed
into one significance test.

**Gate 1 — large enough for this instrument.** Take the absolute A-minus-B
energy estimate and compare it with the registered detection floor. The
estimate must be strictly larger. Equality fails. A smaller or equal estimate
produces a recorded `not_resolvable` refusal: the observed difference may be
real, but this instrument cannot separate it from its demonstrated limit.

**Gate 2 — direction established after uncertainty and multiplicity.** First,
both the metrology interval — the estimate widened for measurement error — and
the decision interval — the interval used by the registered analysis — must
lie wholly on the same predeclared side of zero. Second, the statistical test
must survive its installed multiple-comparison correction. An interval touching
or crossing zero refuses a direction claim. A test that does not survive the
correction also refuses it. Passing the first gate therefore never licenses the
words "A uses more" or "B uses more" by itself.

[Figure 3: decision gates](../paper/figures/fig3_decision_gates.svg) names the
whole decision. Its title names two gates and four possible outcomes; its
subtitle says the drawing contains no data and its spacing implies no numeric
threshold. In the upper part of the white drawing area, a dashed evidence-
failure box lists missing, stale, contaminated, duplicated, inconsistent, or
unauthenticated evidence. A right-pointing side-inlet arrow, labelled as
reaching no gate, leads to a solid refusal box whose smaller text says that no
result is reported from that evidence. A horizontal separator divides that
evidence route from the lower claim route. Below it, a gray measured-contrast
box names the point estimate and composed uncertainty interval, then points to
the first rounded gate box, which asks whether the absolute estimate is greater
than the detection floor. Its downward "no" arrow ends at a `not_resolvable`
box whose text says this is not zero, equality, or no difference. Its rightward
"yes" arrow reaches the second rounded gate box, which asks whether the whole
uncertainty interval points one way. That box's downward "no" arrow ends at a
direction-unresolved box whose text says the floor cleared but direction did
not; its rightward "yes" arrow ends at a blue directional-claim box whose text
says both gates passed in the direction registered before collection. Three
lines at the bottom define the floor as the largest apparent effect when
nothing changed, keep the floor and interval as separate checks, and say their
sum is only a sizing disclosure rather than a single threshold. The boxes and
arrows are a decision flow, not measured data.

**How to read one real verdict.** A historical whole-window record stamped
`2026-07-27T12:22:34.799230Z` reports schema
`joulewise.idle_admission_whole_window_verdict.v1`, record type
`idle_admission_whole_window_verdict`, and status `passed`. Read its fields in
this order:

- `schema_version` and `record_type` tell software how to interpret the file;
  they are not the scientific conclusion.
- `status` is the gate conclusion, while `claim_licensing: true` says the
  record could license its contemporary downstream use if every later gate
  also passed. It does not make this old record eligible under today's capture
  generation.
- `bundle_ids` names the exact included set — 47 bundles in this record — so
  a directory listing cannot silently add evidence. `excluded_bundles`,
  `waived_bundles`, and `occurrence_supersessions` explain records that did not
  enter that set.
- `campaign_policy` identifies the rules applied. `row_provenance` fingerprints
  the evidence rows, and `source_campaign_manifests` identifies the manifests
  from which those rows came.
- `evaluation_scope` states what the gate evaluated. `evaluation_basis` binds
  five things whose change would change the verdict: a fingerprint per included
  measurement, a fingerprint of the policy applied, a fingerprint of the
  membership list itself, the rule stating how many times one measurement may
  be consumed, and the identities of the two calibration captures bracketing
  the night. In this record the pre-bound
  is
  `0.028145704403191807 s` and the post-bound is
  `0.029425288011457773 s`; those are inputs to the verdict, not a claim that
  every later window shares them.
- `idle_admission_core` contains the detailed per-rule outcome, and `runs_dir`
  names the run root that was examined. A replicator verifies the fingerprints
  before trusting either human-readable name.

When the bracket-binding input is supplied, it strengthens this shape: a
finalizer compares the binding supplied beside the verdict with the binding
recorded inside it. A passed verdict copied from another run therefore cannot
finalize the current window merely because its top-level status says `passed`.
As section 4.8 notes, the reusable checks exist but the current locked pack has
not yet wired the complete lifecycle.

## 13. Verification without overstating it

The implemented gates described here are designed to **fail closed**: when one
of those gates sees missing or invalid evidence, it refuses rather than
accepting by silence. The current short pipeline checks exercise that property
at a desk in minutes: they cover refusal-tail behavior, reason-code separation,
launcher arguments, and the window environment allowlist. They do not create a
clean live measurement window and therefore do not prove that the full physical
pipeline succeeds end to end. That clean quiet-machine run remains planned and
must be performed with development agents stopped; fixture-based tests must not
be presented as hardware validation.

## 14. Glossary

*A reminder for a returning reader, not the place these terms are defined.
Every entry here is built where it first appears in the body; the section
number points there.*

- **ABBA block** (§8) — a measure-A, B, B, A schedule that cancels
  steadily-growing drift in paired comparisons by giving each condition one
  early and one late slot.
- **Acceptance artifact** (§7) — the issued document pinning the
  calibration corpus, thresholds, and estimator code hashes; the
  instrument's identity card.
- **Admission** (§6) — the narrow question of whether a bundle may stand
  behind a published number, decided by one shared test.
- **ANE** (§2) — Apple Neural Engine, one of the three measured rails.
- **Arm / arm capability** (§11) — the single-use, atomically consumed
  authorization to launch a locked plan.
- **Attribution error** (§3) — energy assigned to the wrong operation because
  of clock misalignment between workload and sampler.
- **b_fiducial** (§4.5) — a capture's measured worst-edge timing bound: how
  far a commanded pulse edge can appear displaced in the trace.
- **Block / rectangle** (§4.4) — a range of start-edge shifts crossed with a
  range of stop-edge shifts; the unit the detector rejects, splits, or
  retains unresolved.
- **Bracket** (§4.8, §5) — to pin a quantity between two known values either
  side of it: calibration captures before and after a window; system
  timestamps before and after an event.
- **Bracket screen** (§4.8) — the floor under a window's timing allowance,
  currently 9.724 ms, so lucky bracket agreement cannot buy an undeserved
  bound.
- **Bundle** (§1.2) — the stored directory a capture or member leaves behind,
  including raw output, derived numbers, metadata and hashes.
- **Capture** (§1.2, §4) — one run of the calibration protocol, about 197 s.
- **Capture era** (§6) — the generation of capture pipeline that produced a
  stored bundle, recorded as an anchor method paired with a schema label.
  Old eras are verified forever under their own method; only the current era
  may support a claim.
- **Census** (§9) — an enumeration of what is running, checked against what
  is allowed before a quiet window.
- **Claim barrier** (§6) — the single shared test every claim-side consumer
  calls, admitting a bundle only on positive presentation of the current
  claim-bearing capture era.
- **Clock anchor** (§5) — the measured relationship between the system's wall
  clock, in which the sampler labels each row and the workload stamps its
  pulse commands, and the sampler's own monotonic timeline, in which each
  row's duration is reported; published as an interval. The current method
  solves for the two clocks' *rate* as well as their offset and refuses when
  no single rate fits.
- **Condition definition** (§10, §8) — the written specification of what makes
  condition A or B itself: model artifact, prompt length, phase, runtime
  settings.
- **Converged** (§4.4) — the map of surviving candidates for a pulse is
  complete: every point in the configured search square is provably ruled out
  or enclosed by a retained unresolved cell.
- **Detection budget** (§4.6) — the pre-registered cap of 165,000 evaluations
  on a capture's total search effort; exhaustion refuses the capture as
  non-convergent.
- **Detection floor** (§8) — the largest false energy difference the complete
  system reports between identical runs for a named operation family and stack.
- **Evaluation** (§4.4) — one computation of a rigorous, possibly loose lower
  score bound for one block; the unit of search effort.
- **Fail-closed** (§13) — when a check cannot be completed, the outcome is
  refusal, not acceptance.
- **Fiducial pulse train** (§4) — the 59-pulse known workload used to measure
  attribution error.
- **Freeze receipt** (§10) — the authenticated fingerprint of a pack's exact
  bytes at a named path, made before collection.
- **Generation (of the acceptance artifact)** (§7) — one issued link in the
  artifact's lineage. Predecessors are kept byte-identical forever, and each
  consumer resolves its thresholds from the generation the supplied artifact
  names.
- **Hash / digest** (§7) — a short fingerprint of a file's exact bytes;
  a byte change normally produces an unrelated-looking value.
- **Identity-pin projection** (§10) — the receipt pinning the actual model and
  runtime bytes a night will execute.
- **Monotonic clock** (§5) — a counter that only ever advances at a steady
  rate and is never adjusted by network synchronization.
- **Null pair** (§8) — a comparison whose true difference is known to be
  exactly zero; the basis of floor measurement.
- **Operation / phase** (§1.1) — one logged unit of work; prefill (dense,
  compute-bound prompt processing) and decode (token-at-a-time,
  memory-bound generation).
- **Pack** (§1.2, §10) — the committed, locked directory of every
  configuration a measurement night will run.
- **powermetrics** (§2) — Apple's telemetry sampler; the measurement
  primitive.
- **ppm (parts per million)** (§5) — the unit for clock-rate differences;
  1 ppm is one microsecond per second, so 7 ppm accumulates about 1.4 ms
  over a 200-second capture.
- **Pre-registration** (§8, §12) — writing a decision rule down and
  committing it before the data exists, so it cannot be chosen afterwards.
- **Rail** (§2) — a named power channel (CPU, GPU, ANE); the measurement
  boundary is exactly these three.
- **Reduction** (§12) — turning raw samples into per-operation, per-phase
  energy numbers with bounds.
- **Refusal** (§1.2) — a recorded decision not to admit evidence when a gate
  fails; the instrument's most common and most important output.
- **Retained-artifact record** (§9, §11) — the hash-linked account of where
  each file came from, what was true when it was written, and whether its
  bytes later changed.
- **Reissue (science-neutral)** (§7) — a new acceptance generation forced by
  an estimator byte change alone, whose neutrality is proven by replaying the
  whole corpus and diffing every derived quantity, not asserted.
- **Score** (§4.3) — the summed, noise-scaled, quadratic-then-linear penalty
  measuring how badly one candidate edge placement explains the samples.
- **Straddling sample** (§4.1) — a sample whose interval contains a pulse
  edge, so its height reports what fraction of the interval the pulse
  covered; the only edge evidence there is.
- **Waterline** (§4.3) — the survival threshold, best score + max(1.0, 5% of
  best score); candidates scoring at or below it cannot be told apart from
  the best by this data.
- **Window** (§1.2) — one uninterrupted, calibrated, quiet collection session.
- **Worst-edge scalar** (§4.5) — the single largest edge displacement over
  both edges of all 59 pulses, applied symmetrically as ±b_fiducial.
