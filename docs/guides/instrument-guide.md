# The JouleWise Instrument, Explained From Zero

*A guide for someone new to the project. It assumes you know what an LLM is,
what power and energy are, and roughly how a computer is put together —
nothing else. It is deliberately more thorough than the paper's methodology
section: the paper argues; this document teaches. Every mechanism is
presented with the problem that forced it into existence, because almost
nothing in this instrument was designed speculatively — nearly every gate
exists because a specific failure happened, or was demonstrated to be about
to happen.*

*How to read it: every term of art is built or glossed where it first
appears, in the body, in order. The glossary at the end is a reminder for
someone coming back to the document, not the place definitions live. If you
meet a word here that has not yet been explained, that is a defect in this
guide, not something you were supposed to already know.*

*Status note: revised 2026-08-19. Since the first draft the instrument has
changed in one deep way and one broad way. The deep change: the estimator that
ties the sampler's clock to the workload's clock had its central assumption
measured and found false, and was replaced (section 5). The broad change: every
stored measurement now carries a machine-readable record of which capture
pipeline produced it, and only the current one may support a claim (section 6).
Section 4 has also been rebuilt to walk the whole detection procedure end to
end, because its central idea — what it means for the detector to "converge" —
was previously asserted rather than explained. Every calibration number quoted
below has been re-checked against the artifact now in force,
`d079_calibration_acceptance_v2_n17_r6`.*

---

## 1. What this instrument is for

JouleWise measures the energy cost of large-language-model inference
operations — "how many joules does it cost this Mac to generate one token,"
"how much energy does processing a 256-token prompt take," "is the 7-billion-
parameter model's decode energy distinguishable from the 1.5-billion one's"
— on Apple Silicon, using only the machine's own telemetry.

The defining commitment is that every number ships with a demonstrated
error bound. Not an assumed bound, not a vendor specification, not a
statistical formula applied on faith: a bound the instrument itself
measured, on this machine, under the same conditions as the **claim** — a
claim being any statement the project publishes as true of the world, the
thing all the machinery below exists to permit or refuse. The
project's one-line philosophy: **a measurement without a demonstrated error
bound is an anecdote.** Most published LLM-energy numbers on consumer
hardware are, by that standard, anecdotes — the related-work section of the
paper documents peer-reviewed studies that integrate the same telemetry
this project uses, with no calibration and no uncertainty treatment at all.

That commitment has an unusual consequence: the *primary product* of the
instrument is not the joule numbers. It is the **detection floor** — the
smallest energy difference the whole measurement system can honestly claim
to distinguish — plus the machinery that proves the floor is real. The
model-comparison numbers are then demonstrations of what a characterized
instrument can resolve.

### 1.1 What actually gets measured: operations and phases

An **operation** is one unit of work with a start event and a stop event that
the workload itself logs: "prefill of a 256-token prompt, begin … end,"
"decode of 128 tokens, begin … end." The energy of an operation is whatever
the machine drew between those two events. Everything downstream depends on
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
- **Member** — one measured execution of one configuration during a science
  run: "1.5-billion-parameter model, decode 128 tokens, repetition 3 of 4."
  Members are what a published number is eventually computed from.
- **Bundle** — the directory a capture or a member leaves on disk: the raw
  sampler output, the event log, the derived energy numbers, a metadata
  record describing exactly how it was produced, and cryptographic
  fingerprints of all of it. The bundle is the unit that gets stored,
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
- **Rail coverage is not enumerated.** Some hardware is simply outside the
  measured rails. A small example the project verified directly: the
  keyboard backlight's LED power does not appear on the CPU, GPU, or ANE
  rails (established by code inspection of the power-management stack and
  supported by a documentation-grade probe that toggled the backlight
  between maximum and off under the sampler). The measurement boundary is
  therefore always named explicitly: *these three rails, nothing else* —
  not "the machine's power."

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
moves from one phase's total to the other's — and, as section 8 will show,
the smallest difference this instrument is willing to claim is about 1 J.
One misplaced sample is therefore larger than the entire quantity being
claimed. (Those wattages are illustrative; the sample width and the floor
are real.) For a whole-run measurement, the same error cancels out
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
apart under the best possible conditions, differ by up to X joules, then
no claim of a difference smaller than X is honest — no matter what the
point estimates say.

Attribution is bounded by **calibration** (sections 4 and 5). Resolution
is bounded by **floors** (section 8). The composed claim carries both.

A note on one overloaded word before it starts working. **Floor** always
means "a limit below which something cannot go," but this document uses it
of several different things: the *detection floor* (the smallest claimable
energy difference), the *0.1 ms floor* on how finely the detector subdivides
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

**The protocol (version 3, frozen).** The workload drives 59 one-second GPU
pulses — each a 4096×4096 half-precision matrix multiplication loop, chosen
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

Two gates use that score.

**The first asks whether there is a pulse at all.** Compute the score of the
flat "nothing happened here — it was baseline the whole time" explanation,
then compare it with the best guess's score. The best guess must come in
below **half** the flat explanation's score, or the pulse is declared not
detected and the capture is refused. This is a significance test in the
plainest possible form: the pulse hypothesis must explain the data at least
twice as well as no pulse at all. With a real pulse the margin is not close:
a flat explanation has to absorb the entire step — every plateau sample
counted as a large miss — so it accumulates penalty on a different scale
entirely. That is precisely why failing this gate means something went badly
wrong rather than "the fit was mediocre."

**The second defines the surviving patch,** and its threshold is *not* an
absolute number. It is set relative to the best guess found:

```
limit = best score + max( 1.0 , 5% of best score )
```

A guess survives if its score is at or below that limit. In words: a guess
survives if it explains the samples essentially as well as the best guess
does — within one sample's worth of ordinary noise, or within 5% of the
total score once the total is large.

Both branches matter, so work them. If the best score is 38.0, then 5% of
it is 1.9, which beats the 1.0 floor, and the limit is 39.9: with 38
noise-widths of unexplained miss already on the table, a guess that adds
another 1.9 is not meaningfully worse. If instead the best score is 4.0 —
an unusually clean pulse — then 5% is 0.2, the floor of 1.0 wins, and the
limit is 5.0. That floor is what keeps the patch honest when the fit is
nearly perfect: a guess whose penalty is within a single noise-width of the
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
behaviour, the detector can compute *exactly*, in closed form, the best
score any guess anywhere inside the block could possibly achieve — a
guaranteed floor under the block. It does not sample the block; it bounds
it. That single computation is one **evaluation**, and it is the unit in
which all search effort below is counted. Each evaluation licenses one of
three moves:

- **Reject the block.** If even the best score achievable inside it sits
  above the waterline, then every guess inside it is ruled out — infinitely
  many guesses eliminated by one evaluation. This is the move that makes an
  infinite search finite: one evaluation can kill a quarter of the plane.
- **Split the block.** If the block cannot be rejected, some guess inside it
  might survive, so cut it in half and evaluate each half. Blocks that
  straddle the patch's boundary can be neither rejected (part of them fits)
  nor accepted (part of them does not), so they keep splitting, closing in
  on the true edge of the patch from outside.
- **Accept the block.** Once a surviving block is down to 0.1 ms on a side,
  stop splitting and count its *entire extent* into the patch. This is the
  conservative move: nothing inside it has been ruled out, so all of it is
  counted in, which can only make the final bound larger, never smaller.

Run to completion, every point of the plane ends up either provably ruled
out or counted in, with nothing unexamined. **That completed map is what
"converging on a pulse" means** — not "the search found a good answer," but
"the map of what this data permits is finished, with no unexplored
territory." The word is used in that exact sense everywhere below.

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

Across the 17-member corpus that grounds the current acceptance artifact,
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
property a measurement is allowed to have. A fixed allowance makes the
outcome a property of the *data*: the same trace costs the same number of
evaluations and earns the same verdict, on any machine, forever.

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
**custody** check (custody being the unbroken, hash-linked record of where
each file came from and that nothing has altered it since; section 9
builds it out), and then demands **1,282,827** evaluations: 9.2× the next
highest demand of any capture the current anchor method can resolve at all
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
The anchoring machinery itself carries a 5 ms ceiling: an anchor that cannot
be established to better than 5 ms refuses the capture outright. How that
anchor is computed, and what happened when its model turned out to be wrong,
is section 5.

### 4.8 Bracketing and drift

A single calibration is a snapshot, and a window lasts hours. Over hours the
instrument can **drift** — its timing behaviour changing slowly as the
machine warms, as background state settles, as anything else moves — so a
bound measured at 9 p.m. is not automatically a bound that describes 3 a.m.
Real windows are therefore **bracketed**: one calibration capture before the
science members and another after, pinning the night's timing behaviour
between two measured values. The timing **allowance** applied to the night's data — the
uncertainty attached to every phase edge — is then taken as the full
disagreement between the two brackets, not their average. If the instrument
behaved differently at the two ends of the night, the claim inherits the
whole difference.

That allowance is never permitted to fall below the **bracket screen** of
9.724 ms. A screen, here and throughout, is a threshold a value must clear;
this one is a floor under the allowance, and it exists because two brackets
can agree closely by luck. Without the floor, a fortunate pair of captures
could buy a tighter bound than the instrument has ever demonstrated it
deserves. The 9.724 ms comes from the historical range of 17 bounds derived
under the same calibration generation — sections 5 and 7 explain where the
number comes from and why it changed.

And if the brackets disagree by more than 10.165 ms, the entire window is
refused. That much movement means the instrument was not the same
instrument at both ends of the night, and no single allowance honestly
describes both halves.

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

**The falsification.** On this machine the wall clock runs about **7 parts
per million** fast against the monotonic timeline. Parts per million is the
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

The anchor interval is the width of the set; the fitted rate falls out as a
by-product. On the afternoon diagnostic probe (the disciplined capture the
science review examined) the rate came out as a window from +7.243 to
+7.285 ppm — just 0.04 ppm wide, which is why a mid-capture change of rate
cannot hide inside it: any real rate change would have to be smaller than
four hundredths of a microsecond per second to go unnoticed. If no rate
reconciles the constraints, the capture is refused. The method never picks
the least-bad rate.

**What is frozen around it, so the fit cannot absorb anything it likes.**
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
per-capture bounds in the 25–35 ms range. On the calibration fixture shared
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
step. The custody record agrees independently: the earliest record on this
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
metadata record itself — `p2-038.1`, `.2`, or `.3` for the three generations.
One canonical table maps method to label, and the *method* is the single key
every piece of code chooses its behaviour from, so nothing anywhere decides
what to do by reading the label alone.

If a bundle's label and its method disagree it is refused outright, rather
than resolved in favour of either. The record is lying about itself, and
there is no honest way to guess which half is true — a bundle claiming
`.2` while carrying `.3`'s method might be a mislabelled good bundle or a
correctly labelled corrupted one, and those want opposite treatment. Where
the capture machinery produced no such evidence at all, no era is
synthesised: the evidence is marked explicitly incomplete, because inventing
a plausible label is the one failure this design must never have.

**Two questions, deliberately kept apart:** *can this bundle be verified?*
and *may this bundle support a claim?*

- **Strict verification is era-faithful, forever.** Every stored bundle is
  re-derived under *its own* recorded method — `.1` bundles under the legacy
  replay, `.2` under the old censored-intersection derivation, `.3` under the
  current one — and crossing an era against another era's method refuses. The
  748 stored second-era bundles in the repository tree (off-repository mirrors
  hold more) therefore keep every bit of their audit value: they still
  authenticate — meaning their stored fingerprints still match a fresh
  computation over their bytes — they still replay byte-exactly, and their
  custody chains remain checkable. Nothing was rewritten, relabelled,
  or deleted.
- **Claim admission is a separate, mechanical barrier.** "Admission" is the
  narrow question of whether a bundle may stand behind a published number.
  Supporting one requires the *positive presentation* of the current
  claim-bearing method: the bundle must actively show it, from a closed
  set — an explicitly enumerated list, one member long today. Absence is not
  permission; a bundle that says nothing about its era is refused exactly
  like one that names a retired era. One shared test implements this, and the
  three places that admit evidence to a claim — the analysis, the floor
  extraction, and the whole-window check — all call that one test. None of
  them re-implements it or writes the method name into its own code, so the
  barrier cannot quietly decay in one place while still holding in another.

**The problem that forced it into existence.** Before this, superseded
bundles were kept out of claims by per-window policy documents — that is, by a
human remembering to apply a rule. That works until the night it doesn't. A
policy document is not a gate.

**Why there are two refusal reasons and not one.** The barrier distinguishes
`capture_pipeline_superseded` — an authentically stored bundle whose method has
been retired — from `capture_pipeline_absent`, where there is no such evidence
at all. Collapsing them would have been simpler and also false: 745 of the 748
stored second-era bundles record that their anchor *did* resolve, so filing
them under "anchor unresolved" would contradict their own authenticated
metadata. Refusals are published results, so a refusal reason must be true
about the artifact it names, not merely convenient.

## 7. The calibration acceptance: pinning the instrument's identity

A bound measured by one version of the estimator code says nothing about a
different version. So the instrument's identity is **pinned** — recorded as a
cryptographic fingerprint, so that any later change is detectable — by the
**calibration acceptance artifact**, currently
`d079_calibration_acceptance_v2_n17_r6`, whose own file hash begins
`0227bca3`. (A hash, throughout this document, is a short fixed-length
fingerprint computed from a file's exact bytes: change one byte anywhere and
the fingerprint changes completely, and you cannot construct a different file
with the same fingerprint. It is how every "these are the same bytes" claim
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
its predecessor — rather than a version number, and every link in it is a
document you can open:

| Generation | What forced it | What moved |
|---|---|---|
| `…_v2_n19` | first issuance | — |
| `…_v2_n19_r2` | audited detection work, then the budget correction | one estimator pin, rotated twice; corpus still 19 |
| `…_v2_n17_r3` | the anchor replacement (section 5) | the science itself: corpus 19 → 17, screens tightened |
| `…_v2_n17_r4` | making the new anchor the live capture method | one estimator pin |
| `…_v2_n17_r5` | the production capture flip | three estimator pins |
| `…_v2_n17_r6` | capture-era presentation (section 6) | two estimator pins |

Only `r3` changed any science. `r4`, `r5` and `r6` are **proven-neutral
reissues** — forced by the pin rule, not by any new measurement — and each
carries its proof rather than an assertion: a named predecessor with its file
hash, the before-and-after hash of every estimator source that changed, and
the record that the full 19-member replay reproduced, exactly, every capture's
anchor bound, its **disposition** (whether it converged or was refused, and
why), the number of blocks its search had to evaluate — the same
evaluation count that section 4.6's budget caps — and its b_fiducial
value. Predecessor generations are kept byte-identical forever; a
superseded generation is retired as the *live* artifact, never edited.

**Policy constants are resolved, never copied.** A trap lives in that table:
the bracket screen was 0.010818 s under the 19-member generations and is
0.009724 s under the 17-member ones. If any consumer held that number as a
literal in its own source code, historical replays would silently start
judging old data by new thresholds — the past re-tried under rules that did
not exist when it happened. So no such literal exists anywhere in the mint lane — the code that
computes and validates floors: an automated **regression test** — a test
whose only job is to fail if a specific past mistake ever reappears — names
the three source files of that lane and forbids both digit strings from
appearing in any of them. (The acceptance registry itself is not scanned;
it is the one home where the registered values legitimately live.)
Every consumer instead *resolves* the screen and the allowance rule from the
generation that the supplied artifact itself names. An artifact whose
identity is not in the registry refuses; an artifact whose stated screen
disagrees with the registered value for its identity refuses too, rather
than a winner being chosen between them. That is what lets the live
instrument move while every historical replay stays byte-exact: the past is
judged by the rules of the past, by machinery rather than by memory.

## 8. Floors: what the instrument may claim to distinguish

A **detection floor** is the empirically demonstrated smallest energy
difference the complete measurement system can distinguish for a given
operation family on this exact software stack. Two of those words are load-
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
drift. (The 0.2 J is illustrative; note that it is a fifth of the working
floor below, which is exactly the scale at which a fabricated difference
would be dangerous rather than obvious.) ABBA cancels drift that grows
linearly with time exactly, and any smoothly varying drift approximately —
"to first order," in the usual phrasing.

The floor packs use both **absolute arms** — single-condition bundles, which
answer "how many joules does this cost," where drift cannot be cancelled
because there is nothing to pair against — and ABBA comparison blocks, which
answer "how much more does A cost than B" and where drift can. Each successor floor
pack carries three condition families — token generation, 128-token prompt
processing, and 256-token prompt processing — and every family gets both
arms: a 10-member absolute *cell* and a 10-block ABBA cell (a cell,
in experiment-design terms, is one named group of runs that produces one
number — one arm of one family). Only two of the
three families cost physical runs: the 128-token family is a *rider* — it
re-reads the prompt-processing phase of the decode family's own bundles
rather than commanding runs of its own — which is why the pack totals 100
science configurations rather than 150. The exact member inventory is not
something to reconstruct from this paragraph: the pack's own generator
re-derives and attests it on every check, which is the authority a
replicator should use.
All of it is frozen before any data is seen.

**The floors are attribution-limited, and labeled as such.** On this
instrument, the noise-limited component of the floor is around 0.3 J — that
is what the machine's variability alone would allow — but the attribution
term, b_fiducial applied at the phase boundaries as in section 3's worked
example, dominates and lifts the working floor to roughly 1 J for the
characterized phases. Saying a floor is "attribution-limited" therefore
means something specific and actionable: the binding constraint is clock
alignment, not electrical noise, so a better clock anchor — not a quieter
machine, not a longer run, not more repetitions — is the upgrade path. That
regime is an established finding of the project, published as a label on
every floor rather than hidden, precisely so a reader comparing instruments
can see which wall each one is against.

Claims built on the floors then carry additional **pre-registered**
claim-side margins — margins written down and committed before any data
exists, so they cannot be chosen after seeing which value would let a
result through — putting the effective bar for a claimed difference near
5 J. Numbers smaller than the labeled bar are not claimed, full stop: the
pipeline refuses to emit them as findings.

**Per-phase, per-stack.** Floors do not transfer across phases, prompt
lengths, or stacks. The 256-token prefill floor is its own separately
measured artifact precisely because transporting a floor from a different
prompt length would be an assumption wearing a measurement's clothes.

## 9. The quiet machine: protecting the signal

Everything above assumes the machine's background is stationary and small.
It is not, unless forced to be. Resident daemons index files, analyze
photos, check for updates; the display and its friends draw power; other
software (including this project's own AI tooling) burns CPU. None of it
is distinguishable from workload energy after the fact — the rails report a
total, not an attribution by process.

The defenses, each with its scar tissue:

- **The screensaver story.** In an early floor campaign, 43 of 50
  calibration bundles were contaminated because a video screensaver
  engaged during the windows — the six "anomalously low" bundles were the
  *clean* ones, and the contaminated majority looked normal precisely
  because it was the majority. The protocol now forces the display asleep
  (a transient display-sleep command, not a screensaver), verifies
  screensaver disengagement, and treats display state as a first-class
  fence — something checked and recorded before the window, not assumed.
- **The process census.** A **census** here means what it means anywhere:
  an enumeration of what is present, checked against what is allowed.
  Before quiet work, five process probes sweep the machine: a keep-awake
  census (no stray `caffeinate` holders — processes that ask macOS to stay
  awake and would defeat the display fence), an agent census (no AI-tooling
  sessions running), a browser census, a monitor census (no samplers or
  watchers already running, which would both draw power and contend for the
  telemetry interface), and a maintenance census (Spotlight indexing, photo
  analysis, software update, backups). The census patterns were themselves
  calibrated against reality: a qualification capture of the machine's true
  quiet state showed that several system daemons are permanently resident
  (seven Safari support agents with Safari closed; `watchdogd` matching a
  naive "watch" pattern), and the probe patterns are being corrected against
  that ground-truth fixture rather than against wishful assumptions.
- **Power and thermal fences.** AC power at full charge (a mid-window
  charge-termination is a step change in the power picture — this was
  observed directly during an operator qualification probe), thermal
  state nominal before starting, and at least ten minutes of untouched
  idle settling before any calibration.
- **The agent quiesce rule.** To *quiesce* a system is to bring it to a
  quiet, settled state and hold it there. The project is developed largely
  by AI agents — and an agent session is background load like any other. No
  measurement starts while any agent session is active. The overnight
  first-light window — the first real collection window run with the
  finished machinery — was run by a single fenced driver script with every
  agent fleet shut down, and the driver's own censuses are part of the
  capture's **custody record**: the unbroken, hash-linked account of where
  each file came from and what was true when it was written, which
  section 11 uses as a gate.

## 10. Frozen plans and the freeze ceremony

**Why freeze:** the most seductive way to corrupt a measurement campaign
is to adjust it after seeing data — drop the awkward bundle, tweak the
schedule, re-run the unlucky block. Each adjustment is individually
defensible and collectively fatal, because the plan ends up shaped by the
data it was supposed to judge. The defense is to make the plan physically
unchangeable before the first byte of data exists.

**What a pack is.** A campaign is compiled into a **pack**: a committed
directory containing every configuration the night will run (all 100
science configs for a floor pack), the **order manifests** fixing the exact
execution sequence, the calibration plan, the **condition-family
definitions** — the written-down specification of what makes condition A
condition A: which model artifact, which prompt length, which phase, which
runtime settings, so that "A" is a reproducible object rather than a label —
and a `plan_tree.json` that binds all the pieces together by hash.

Packs are generated by committed generator programs, so the entire pack is
reproducible byte-for-byte from its generator — and audited regressions
prove the generator cannot overwrite an earlier generation's committed
bytes (a defect class that was found, fought through seven rounds of
implementation and nine audits, and closed with generational proofs). That
property has since been exercised for real rather than only proved: the
version-2 packs have generated a version-3 family without altering a byte of
the version-1 or version-2 packs — see *Lineage in practice*, below.

**Identity-pin projection: naming is not enough.** A plan can only *name*
what it intends to run — "the 7-billion-parameter model" — and a name is not
bytes. The file behind the name can be re-downloaded, re-quantized, or
silently replaced between writing the plan and running it. So before
freezing, a projection tool reads the *actual* files the night will execute
(the real model weight files on disk, hashed; the real runtime identity) and
**pins** those fingerprints — records them, so any later difference is
detectable — into a **projection receipt**. This closes the gap between "the
plan says model X" and "the bytes on disk are model X," which is otherwise
checkable only after the fact, if at all.

**The freeze receipt.** Freezing a pack **mints** a **receipt** — "mint"
because the act creates a one-of-a-kind record at a specific moment that
cannot afterwards be made again for a different set of bytes. A receipt is a
small file that attests: *at this moment, these exact bytes existed at this
exact location, and these readiness checks passed.* It binds the plan's
bytes by hash (the SHA-256 of the calibration plan, which itself embeds the
hashes of everything else, so one fingerprint covers the whole tree) plus
the readiness evidence rows evaluated at freeze time. Two properties are
easy to miss and load-bearing:

- **The receipt *is* the frozen state.** The pack's descriptive text
  (README wording, status fields) is never rewritten after minting — an
  executed proof showed that any post-mint byte change to the pinned plan
  unconditionally invalidates the receipt at every later gate, with no
  re-mint path. So the committed receipt governs, and human-facing wording
  is written to be true both before and after freezing ("status governed
  by the freeze receipt") rather than flipped after the fact.
- **Receipts chain across generations.** A successor pack's receipt is
  numbered one past its predecessor's (`freeze-0002` chaining to the v1
  family's `freeze-0001`) and embeds an authenticated predecessor binding:
  the predecessor's pack digest, plan hash, receipt hash, and identity
  receipt, all verified before the successor may mint. ("Digest" is another
  word for hash.) Superseded packs remain valid *historical* records — their
  receipts still authenticate — but the lineage is explicit and
  machine-checked in both directions.

**Lineage in practice: how a frozen family gets a successor.** When section
5's anchor replacement moved the calibration artifact, the three frozen
campaign packs were left bound to a generation that can no longer bear claims.
The obvious repair — regenerate the packs in place against the new artifact —
is exactly what the freeze machinery exists to prevent: it would destroy the
historical attestation the receipts were minted to provide and leave a
directory claiming to be frozen while holding different bytes. So the family
grew a third generation instead. Each `_v2` pack's **unedited** generator was
run to emit a `_v3` tree, and only the emitted, not-yet-frozen drafts were
retargeted at the current calibration artifact. The frozen `_v2` packs were
not touched at all — including their generator programs, which are themselves
frozen pack content, hashed inside the very plan trees they produce; a
regression re-hashes the committed `_v2` trees to prove it.

Two details earn their weight. **Bind at birth, not by retargeting later:** a
pack records the *file hash* of the acceptance artifact it was built against,
and issuing a newer artifact leaves the older file untouched. So a pack built
against last week's generation and quietly pointed at this week's would still
carry a hash that verifies cleanly — the check would pass while the pack was
stale, which is the worst possible combination. The successor packs therefore
reached their would-be-frozen state already bound to the live generation: the
retarget happened in the unfrozen drafts, before any receipt existed, so no
frozen pack ever pointed at a stale generation.
**Freeze is deliberately the last step:** the successor family's readiness
evidence has been authored at the designated measurement checkout — eleven
evidence documents per pack, thirty-three in all, every one passing — and the
freeze receipts chaining each `_v3` pack to its `_v2` predecessor's
`freeze-0002` are the one step still outstanding. Nothing may be collected
under the successor family until they exist.

**A subtlety that cost a night's receipts:** freeze receipts authenticate
the *absolute path* of the pack they froze. Receipts minted in a temporary
working directory are worthless on the real measurement night, because the
path they attest to is not the path the night runs from. The project's
receipts are therefore minted in the designated measurement checkout — the
exact directory the measurement night will run from — and the first set,
minted in the wrong place, was reverted on the record and re-minted
correctly. (The revert commits are still in the history; honest history is
preferred over clean history throughout this project.)

## 11. Arming, the window, and the operator

A measurement night is a ceremony with a deliberately narrow shape.

**Readiness evidence with freshness horizons.** Before **arming** — the step
that authorizes a specific frozen plan to actually run — evidence rows are
authored proving the machine and pack are ready: clock state, quiet censuses,
pack authentication, regression-suite results, and so on. Each row has a
**freshness horizon**: a maximum age past which it stops counting as
evidence. Volatile evidence (anything about the machine's live state) expires
on a 20-minute horizon measured on the monotonic clock, so it cannot be
extended by moving the wall clock; procedural evidence lasts six hours.
Expired evidence refuses the arm. The horizons encode a simple truth: a
statement about a machine's state is only evidence while the state can't have
drifted.

**The single-use arm capability.** Arming mints a **capability** — a
one-shot authorization token, valid for exactly one launch — that the
launcher consumes *atomically*: the consumption and the launch are one
indivisible step, so there is no moment in which the capability has been
checked but not yet spent. The launch either happens under the armed plan or
the capability burns. There is no "launch, tweak, relaunch under the same
arm," which is the manoeuvre this prevents. The consumption is bound to the
arm-time attested inputs through a five-hop chain of hashes, so a
substituted manifest or foreign context is refused before any filesystem
effect occurs.

**The window chain.** The launched chain runs the pack's members in frozen
order, brackets them with the pre- and post-calibrations of §4.8, writes runs
into custody-controlled roots — directories whose contents are hash-recorded
as they are written, so a later edit is detectable — and refuses on any
deviation: a boot change (the machine restarted mid-window, which resets the
monotonic clock and voids every timing relationship established before it), a
clock event, a stage running out of the frozen order.

**The trusted-operator boundary — stated, not hidden.** The instrument
does *not* defend against a deliberately dishonest operator, and the
threat model explicitly excludes adversarial programs running inside the
measurement account. What the machinery guarantees is that an *honest*
operator cannot accidentally produce dishonest data: the gates catch stale
evidence, contaminated environments, plan deviations, byte drift, and clock
trouble. Fabrication by the single trusted human with root access is out of
scope — and the paper says so, because a limitation stated is a boundary,
while a limitation hidden is a landmine.

## 12. From samples to claims

The full pipeline, end to end:

1. **Plan** — packs generated, reviewed, committed.
2. **Freeze** — identity projected, evidence authored, receipts minted at
   the measurement checkout, everything pushed.
3. **Arm** — fresh readiness evidence within horizons; capability minted.
4. **Window** — quiet fences, clock discipline, bracket calibration,
   frozen-order members, bracket calibration, restore.
5. **Reduce** — *reduction* is the step that turns raw telemetry into
   physics: for each member, integrate the three rails between the
   event-logged operation boundaries under the anchored clock, clipping the
   boundary samples, and attach to every phase edge the timing allowance the
   night's brackets earned. Raw samples in, per-phase joules with bounds out.
6. **Gate** — the whole-window **verdict**, meaning the recorded pass-or-
   refuse decision for the window as a unit: acceptance artifact fresh and
   authenticated, every member presenting the current capture pipeline
   (section 6), brackets within drift allowance — screened against the
   generation the artifact itself names, never a copied constant —
   pre-flight screen passed (the section 4.8 admission check that a calibration's own bound must not exceed the corpus ceiling of 0.032898 s), custody complete, every member's lineage
   authenticated. Any failure refuses the window's evidence — recorded, not
   discarded.
7. **Claim** — only differences exceeding the labeled floor plus
   pre-registered margins, under the pre-registered statistical family, on
   the named stack, within the named boundary.

That last step needs its terms. A **contrast** is one planned A-versus-B
comparison; the first campaign has two of them, and they are judged as one
**family** — a set of tests considered together — because testing two things
at once raises the chance that at least one crosses the line by luck. The
**Holm correction** compensates for that: it tightens the per-test
thresholds so that the probability of *any* false claim in the family stays
at α = 0.05, i.e. one in twenty. **Two-sided** means a difference in either
direction would count, and **directions pre-registered** means the project
wrote down beforehand which way it expected each contrast to go, so a
surprise cannot be quietly recast as a prediction.

What a published claim finally says, in plain words: *on this exact
hardware, OS build, runtime, and model artifact, measured across these
three rails with attribution bounded by an in-window calibration, the
energy of operation A exceeded operation B by E joules, where E clears an
empirically demonstrated floor of F joules plus stated margins — and here
is the complete refusal log of everything the instrument declined to
claim along the way.*

## 13. The verification culture, briefly

Every mechanism above exists in code that is **fail-closed**: when a check
cannot be completed — evidence missing, a hash unreadable, a constraint
unsatisfiable — the default outcome is refusal, never acceptance. Nothing
passes by silence.

The project's process mirrors the instrument: implementations are audited
adversarially by independent reviewers, fixes are re-audited (fix rounds
have introduced defects often enough that the re-audit is mandatory),
consequential reversals are reviewed by people given the artifacts without
the authors' framing, and the operator is qualified through scripted
evidence-producing sessions. The project's own history is the argument:
essentially every failure class was caught by a *different* layer than the
one that produced it — the audits catch the implementations, the
fresh-eyes reviews catch the audits, the operator's live runs catch what no
sandbox could see, and the instrument's own refusal gates caught a mis-set
parameter on their first night of contact with reality. The run reports
under `docs/run_reports/` are the evidence trail, and they are written to be
read.

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
  authorization to launch a frozen plan.
- **Attribution error** (§3) — energy assigned to the wrong operation because
  of clock misalignment between workload and sampler.
- **b_fiducial** (§4.5) — a capture's measured worst-edge timing bound: how
  far a commanded pulse edge can appear displaced in the trace.
- **Block / rectangle** (§4.4) — a range of start-edge shifts crossed with a
  range of stop-edge shifts; the unit the detector rejects, splits, or
  accepts.
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
  stored bundle, recorded as an anchor method paired with a schema label
  (`p2-038.1/.2/.3`). Old eras are verified forever under their own method;
  only the current era may support a claim.
- **Census** (§9) — an enumeration of what is running, checked against what
  is allowed; five of them fence a quiet window.
- **Claim barrier** (§6) — the single shared test every claim-side consumer
  calls, admitting a bundle only on positive presentation of the current
  claim-bearing capture era.
- **Clock anchor** (§5) — the measured relationship between the system's wall
  clock, in which the sampler labels each row and the workload stamps its
  pulse commands, and the sampler's own monotonic timeline, in which each
  row's duration is reported; published as an interval. The current method
  solves for the two clocks' *rate* as well as their offset and refuses when
  no single rate fits.
- **Condition family** (§10) — the written specification of what makes a
  condition itself: model artifact, prompt length, phase, runtime settings.
- **Converged** (§4.4) — the map of surviving candidates for a pulse is
  complete: every point of the plane provably ruled out or counted in.
- **Custody record** (§9, §11) — the hash-linked account of where each file
  came from and what was true when it was written.
- **Detection budget** (§4.6) — the pre-registered cap of 165,000 evaluations
  on a capture's total search effort; exhaustion refuses the capture as
  non-convergent.
- **Detection floor** (§8) — the demonstrated smallest energy difference the
  complete system can distinguish for a named operation family and stack.
- **Evaluation** (§4.4) — one exact computation of the best score achievable
  anywhere inside one block; the unit of search effort.
- **Fail-closed** (§13) — when a check cannot be completed, the outcome is
  refusal, not acceptance.
- **Fiducial pulse train** (§4) — the 59-pulse known workload used to measure
  attribution error.
- **Freeze receipt** (§10) — the cryptographic attestation that a pack's bytes
  are final at a named path; the receipt is the frozen state.
- **Generation (of the acceptance artifact)** (§7) — one issued link in the
  artifact's lineage. Predecessors are kept byte-identical forever, and each
  consumer resolves its thresholds from the generation the supplied artifact
  names.
- **Hash / digest** (§7) — a short fingerprint of a file's exact bytes;
  change one byte and it changes completely.
- **Identity-pin projection** (§10) — the receipt pinning the actual model and
  runtime bytes a night will execute.
- **Monotonic clock** (§5) — a counter that only ever advances at a steady
  rate and is never adjusted by network synchronization.
- **Null pair** (§8) — a comparison whose true difference is known to be
  exactly zero; the basis of floor measurement.
- **Operation / phase** (§1.1) — one logged unit of work; prefill (dense,
  compute-bound prompt processing) and decode (token-at-a-time,
  memory-bound generation).
- **Pack** (§1.2, §10) — the committed, frozen directory of every
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
