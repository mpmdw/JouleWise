# The JouleWise Instrument, Explained From Zero

*A guide for someone new to the project. It assumes you know what an LLM is
and roughly what "energy" means, and nothing else. It is deliberately more
thorough than the paper's methodology section: the paper argues; this
document teaches. Every mechanism is presented with the problem that forced
it into existence, because almost nothing in this instrument was designed
speculatively — nearly every gate exists because a specific failure
happened, or was demonstrated to be about to happen.*

*Status note: revised 2026-08-19. Since the first draft the instrument has
changed in one deep way and one broad way. The deep change: the estimator that
ties the sampler's clock to the workload's clock had its central assumption
measured and found false, and was replaced (section 5). The broad change: every
stored measurement now carries a machine-readable record of which capture
pipeline produced it, and only the current one may support a claim (section 6).
Every calibration number quoted below has been re-checked against the artifact
now in force, `d079_calibration_acceptance_v2_n17_r6`.*

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
measured, on this machine, under the same conditions as the claim. The
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

## 2. The measurement primitive, and why it cannot be trusted blindly

Everything starts with `powermetrics`, Apple's built-in telemetry sampler.
Run with root privileges, it reports power draw for named "rails" of the
processor package — the CPU cluster, the GPU, and the ANE (Apple Neural
Engine) — as a series of samples, each an average over its sampling
interval. JouleWise integrates those three rails between operation
boundaries: energy = sum of (average power × interval duration), with the
boundary intervals clipped at the operation's start and stop events.

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
wrong operation. The total is right; the split is wrong. For whole-run
measurements this barely matters. For *phase-resolved* measurements — the
project's whole point — it dominates: a decode phase might last a few
seconds, and a misplaced boundary sample carries a meaningful fraction of
a small phase's energy.

The origin story that made attribution the obsession: an earlier
generation of the pipeline carried a **time-anchor defect** — the mapping
between the sampler's timestamps and the workload's timestamps was
subtly wrong — and when it was found, the project voided *every*
claim-eligible corpus collected under it and rebuilt the anchoring
machinery from scratch. That decision (repair, then re-collect, rather
than patch and excuse) set the tone for everything after: attribution
errors are silent, so the machinery that bounds them must be loud. It
happened a second time, smaller and far more instructive, on 2026-08-18 —
section 5 is that story, and it is the best single illustration of how this
project treats being wrong.

**Resolution error: a difference that isn't there, or a real one you
can't see.** Even with perfect attribution, the machine's background
activity, thermal state, and the sampler's quantization put a floor under
what can be distinguished. If two identical workloads, measured minutes
apart under the best possible conditions, differ by up to X joules, then
no claim of a difference smaller than X is honest — no matter what the
point estimates say.

Attribution is bounded by **calibration** (sections 4 and 5). Resolution
is bounded by **floors** (section 8). The composed claim carries both.

## 4. The fiducial calibration: the instrument measuring itself

The calibration answers a concrete question: *if software commands a load
pulse at a known time, how far from the commanded edges can that pulse
appear in the sampled power trace?* The answer is a per-capture timing
bound called **b_fiducial** ("fiducial" as in a reference mark whose true
position is known).

**The protocol (version 3, frozen):** the workload drives 59 one-second
GPU pulses — each a 4096×4096 half-precision matrix multiplication loop on
the GPU — after 3 warmup pulses, with the sampler running at a 100 ms
cadence. The quiet gaps between pulses follow a deterministic
low-discrepancy schedule (deliberately irregular spacing) so the pulse
train cannot accidentally phase-lock with the sampler's own cadence. Every
capture records the raw sampler trace, the workload's event log, and a
clock anchor binding the two timelines.

**Detection:** an estimator searches the trace for the 59 pulses, jointly
fitting each pulse's start-edge and stop-edge displacement against the
commanded times. The accepted evidence is conservatively collapsed to one
symmetric worst-edge scalar per capture: the capture's b_fiducial is
driven by the *worst* pulse, not the average, because a phase boundary in
a real measurement gets no averaging — it lands where it lands. Across the
17-member corpus that grounds the current acceptance artifact, b_fiducial
ranges from 0.0232 s to 0.0329 s.

**Why pulses:** you cannot bound attribution error by measuring an unknown
workload — you need a signal whose ground truth you control. A commanded
square pulse is the simplest possible known signal: its true edges are in
the event log, its observed edges are in the trace, and the difference *is*
the attribution error, measured rather than assumed.

**The detection budget — and the night it proved itself.** Recall what
the detector is actually being asked. A pulse was *commanded* at a known
time with a known duration, and the trace shows power stepping up and
back down somewhere near those times. The calibration question is: how
far from the commanded times could the pulse's start and stop edges
really have landed, as far as the recorded samples can tell? The
detector answers by trial. Take one candidate answer — say, "the start
edge was really 3 ms late and the stop edge 1 ms early" — work out what
every power sample *would* have read if that were true, and compare
against what the samples actually read. Some candidates fit well; most
fit terribly.

If the detector kept only the single best-fitting candidate, it would be
pretending the samples pin the edges to a point. They do not: each
sample is an average over roughly a tenth of a second, so a whole
neighbourhood of nearby candidates fits the data essentially as well as
the best one, and any of them could be the truth. The honest output is
therefore the *entire set* of candidates the samples cannot rule out —
and the pulse's timing bound is the worst edge displacement found
anywhere in that set. Which creates an obligation: the set must be found
*without gaps*, because a missed pocket of acceptable candidates could
hide the very displacement that should have set the bound, and the bound
would come out too small.

That obligation is what the rectangles are for. The candidates form a
two-dimensional plane — one axis for how far the start edge shifted, one
for the stop edge. You cannot try infinitely many points, and trying a
grid of points would leave the space *between* grid points untested. So
the detector takes a whole rectangle of the plane at once and computes a
guarantee of the form "nothing anywhere inside this rectangle can fit
the data better than X." If even that best case X is worse than the
acceptance threshold, the entire rectangle — infinitely many candidates
— is ruled out in one step. A rectangle that cannot be ruled out is cut
in half and each half examined again, down to a tenth of a millisecond,
at which point the survivor's whole extent is counted into the set.
Every point of the plane ends up either provably ruled out or counted
in. **"Converging on a pulse" means finishing that job** — the map of
what the data allows is complete, with no unexamined territory.

Why put a limit on that work at all? Two reasons. First, without one,
a bad trace can make the search grind on and on: how long it takes —
and whether the operator gives up and re-runs — would then depend on
how fast the machine happens to be and how patient the human happens to
feel, which means two people with the same data could reach different
verdicts. A fixed allowance makes the outcome a property of the *data*:
the same trace always costs the same number of rectangle evaluations
and always gets the same verdict, on any machine, forever. Second, the
amount of work the map needs is itself a diagnosis. A clean pulse train
has crisp steps, so most of the plane is ruled out cheaply — every
healthy capture on this machine finishes all 59 maps in roughly 115,000
to 138,000 evaluations, and the allowance is set at 165,000, that
maximum plus about 20% headroom. When a capture needs far more than
that, it is not a slow search; it is the data telling you the pulse
edges are genuinely smeared or ambiguous — something on the machine
blurred the steps the map is trying to trace.

Both reasons have already been exercised for real. One capture — whose
clock anchoring and custody all checked out fine — needed 1,282,827
evaluations, nine times more than any healthy capture ever has. Without
the budget, that would have been several minutes of grinding ending in
a bound of dubious meaning; with it, the capture was refused on the
spot, with the effort count recorded as the reason. And when a capture
does exceed the allowance, it is **refused as non-convergent** — never
accepted with whatever partial map existed when the money ran out, for
exactly the reason above: the unexplored territory might hide the very
edge placement that should have set the bound. On the night of
2026-08-17→18, the very first live capture under the pulse detector then in
force hit that budget and was refused. The diagnosis that followed is the best short
course on this project's method:

1. *Don't retry.* Rerunning until a capture passes is selection on the
   outcome — the cardinal sin. The refused capture's artifacts were
   preserved and studied instead.
2. *Discriminate instrument from environment.* Issued corpus captures —
   known-good traces — were replayed through the same detector. They hit
   the same budget. The previous detector generation, and the new one with
   a raised cap, both converged on all of them. Conclusion: the trace was
   fine (its pulse signal-to-noise matched the corpus); the budget had
   been set below the real workload's demand, a fact no repository test
   could expose because raw calibration traces are too large to live in
   the repository.
3. *Correct from the complete evidence, not until it passes.* Every
   retained raw trace on the machine was swept — 40 unique captures, of
   which 34 converged fully and 6 refused before fitting; the maximum
   observed demand was 137,189 evaluations; the budget was reset to
   165,000, about 20% above the maximum, with the margin exceeding the
   entire observed spread.
4. *Then, and only then, re-derive.* The refused capture, re-evaluated
   under the corrected budget, converged on all 59 pulses and yielded
   b_fiducial = 0.0309 s under the anchor estimator then in force. (That
   number moved when the estimator was replaced the next day — section 5.)

A safety gate refusing on first contact with reality, the refusal
diagnosed rather than overridden, and the fix grounded in the full corpus:
that is the intended shape of every failure this instrument will ever have.

**The budget was re-earned, not inherited.** When the anchor estimator was
replaced (section 5), the sweep that justified 165,000 became invalid — it had
been run under the old anchors — so it was redone. The budget stayed at
165,000, now standing on the claim-bearing population's own numbers: the 17
corpus survivors demand between 115,449 and 137,535 evaluations, median
122,097, and 165,000 is that maximum plus about 20%. One later validation-only
capture resolves its clock anchor cleanly and then demands 1,282,827
evaluations, 9.2× the next highest demand of any v3-resolvable capture (a set
wider than the 17 survivors); it is recorded as refused rather than
admitted. Raising the cap to swallow it was considered and rejected, because a
ninefold increase driven by one outlier would make a wall-clock deadline the
real limit and the failure mode dependent on how fast the host machine happens
to be. A budget is a safety gate only if the population it protects sets it,
not the worst thing it ever saw.

**Clock discipline.** The anchor between the two timelines is only valid
if neither clock moves during a capture. The system clock's network-time
synchronization can *slew* the clock mid-window — silently stretching or
compressing the timeline and moving energy between operations. So during
measurement windows, network time is disabled and re-enabled through two
narrowly authorized administrator commands (the only two privileged clock
operations the measurement account can run without a password; the
authorization was installed and exercised as part of operator
qualification). The anchoring machinery itself carries a 5 ms ceiling —
an anchor that cannot be established to better than 5 ms refuses the
capture. How that anchor is computed, and what happened when its model
turned out to be wrong, is section 5.

**Bracketing and drift.** A single calibration is a snapshot. Real windows
are bracketed: a calibration before and after the science members, with
the timing allowance taken as the full disagreement between the brackets
(never less than the *bracket screen* of 9.724 ms — sections 5 and 7 explain
its provenance — derived from the historical range of 17 same-epoch bounds). If the brackets disagree by
more than 10.165 ms, the entire window is refused — that much drift means
the instrument was not the same instrument at both ends of the night.

## 5. The clock anchor, and the day its model was falsified

**What an anchor is.** Two clocks are involved in every capture and neither
knows about the other. The sampler labels its rows with the system's
wall-clock time, but measures how long each row lasted on its own **monotonic**
timeline — a counter that only ever advances and is never adjusted by network
synchronization — and the workload stamps its pulse commands in wall-clock
time. To integrate energy between event boundaries you must know how those two
timelines line up, and nothing in the operating system tells you. The **clock
anchor** is the measured relationship between them — and because it is
measured, it is reported as an *interval*, never a point. Its half-width is
part of every bound the instrument publishes.

**How the evidence arrives.** Each time the wall clock rolls over a whole
second, the sampler prints that whole-second wall-clock label on the row whose
averaging interval just ended, and every row also reports how long it covered
in the monotonic timeline. Each row therefore says: *the very first sample
ended somewhere in this one-second-wide window of wall time, shifted back by
the elapsed time accumulated since*. A 197-second capture yields about 197
such statements, and five system timestamps taken around the capture (spawn, first parse, sampling start, stop, final
parse) bracket the same quantity causally. The anchor is whatever survives all
of that evidence at once.

**The old method, and its hidden assumption.** The previous estimator (the
censored-intersection method) intersected those windows with the causal
bracket: if what remained had positive width, its midpoint became the anchor
and its half-width the bound; if what remained was empty, the capture was
refused. The method is sound *given* one assumption that was never stated as
an assumption — that one second of wall time is exactly one second of the
sampler's elapsed timeline. Rate = 1.

**The falsification.** On this machine the wall clock runs about **7 parts per
million** fast against the monotonic timeline — seven microseconds per second.
Over a 197-second capture that accumulates roughly 1.4 ms of stretch, and the
machine's own
records agree: the wall-versus-monotonic spans logged during the diagnostic
probe were 1.442–1.447 ms. The intersection windows, after the causal
bracket, are only about a millisecond wide. A systematic stretch the same size
as the thing you are intersecting does not perturb the answer; it destroys it.
Six back-to-back captures under identical conditions made it visible: two
resolved, with intersection widths of +780 µs and +1.039 ms, and four came
back empty, at −4 µs, −159 µs, −210 µs and −313 µs. Same machine, same
protocol, same sitting — a coin flip.

That alternation was the loud symptom: good captures refused for no physical
reason. The silent problem was worse. When the intersection *did* survive, its
midpoint sat off by roughly half the accumulated drift, in the same direction
every time. Every accepted anchor carried a bias nobody could see.

**The replacement: solve for the rate instead of assuming it.** The current
method — *rate-aware set membership* — asks which **(rate, offset)** pairs are
consistent with *every* constraint at once, and returns the entire feasible
set. That set is convex, and the search runs in exact rational arithmetic, so
no floating-point rounding can invent or destroy feasibility at the margin.
The anchor interval is the width of the set; the fitted rate falls out as a
by-product — on the afternoon diagnostic probe (the disciplined capture the
science review examined), a window from +7.243 to +7.285 ppm, 0.04 ppm wide,
which is why a mid-capture change of rate cannot hide inside it. If no rate reconciles the constraints, the capture is refused. The method
never picks the least-bad rate.

**What is frozen around it, so the fit cannot absorb anything it likes.**
Departure from a straight-line relation between the clocks is capped at
250 µs, a fitted rate beyond ±50 ppm *refuses* rather than being clipped to
the limit, and neither constant may be widened after a failure is observed
without declaring an entirely new method. The fit is also not a substitute for
turning network time off: the model assumes nothing is steering the clock
mid-capture, and the enforced network-time-OFF window is what makes that
assumption admissible. One further term is easy to mistake for redundancy. The
anchor's half-width says *where the timeline starts*; a separate term pays for
the two clocks drifting apart *during* the capture. Both are needed, because
the pulse detector walks forward through the trace from the anchor's midpoint
at the monotonic clock's own rate, while the pulse commands it is comparing
against are stamped in wall-clock time.

**Paying for the rate is what makes the bound honest.** Across the re-derived
corpus the anchor term rose by 0.311 ms on average, against per-capture bounds
in the 25–35 ms range. On the calibration fixture shared by the whole test
suite, the very same inputs now yield a bound 3.09 microseconds wider. That
figure already includes one numerical detail that was paid for rather than
deferred: the padding constant was raised from 1 nanosecond to 1 microsecond,
to cover the rounding error you get when a timestamp counted from 1970 is
stored as a double-precision number. Individual
b_fiducial values moved *both* ways, because the pulse detector re-fits the
trace under a shifted anchor: 6 of the 17 issued members tightened, including
the one that becomes the new corpus maximum. The padding raise by itself moved
every anchor-v3 bound outward by 1 µs minus 1 ns; under that change alone
nothing tightened and no capture changed status.

**Refusals of previously accepted captures are the correction working.** The
derivation corpus went from 19 members to **17**. Two captures the old model
had accepted now refuse, for a physical reason rather than a numerical one:
their timestamps admit *no single rate at all*. One is pinned to
[−1.1, +5.2] ppm by its early stamp pairs and to [−16.04, −15.99] ppm by its
long baselines — disjoint by more than 15 ppm — with its wall-versus-monotonic
offset moving −3.18 ms mid-capture; the smallest slack that would make it
feasible is 5.612 µs. The other runs at −9.2 ppm early and −2.27 ppm late;
1.873 µs. The mechanism is that the wall clock was being actively *steered*
during those captures, before clock discipline existed as a protocol step, and
the custody record agrees independently: the earliest clock-pin record on this
machine postdates both. For contrast, of the 43 replayed corpus-lineage
captures, 41 need exactly zero slack. The model fits an ordinary capture to sub-microsecond
consistency and refuses precisely the captures where something was moving the
clock.

**Which direction a correction moves your own thresholds is diagnostic.** One
of the two refused captures was the *corpus maximum* under the old model
(b_fiducial 0.033559 s), so removing it makes the instrument's screens
**stricter**: the maximum falls to 0.032898 s and the bracket screen tightens
from 0.010818 s to 0.009724 s. A correction that discards your most
contaminated data point and leaves you a harder bar to clear is the shape of
an honest one; be suspicious of the opposite. Likewise, 11 of the 32 captures
that survived re-derivation produced intervals that no longer contain the old method's
accepted point — exactly what removing a bias should do, not an anomaly to be
explained away.

**The lesson worth carrying away: replay is not validity.** Every stored
bundle from the old era still replays perfectly — feed the old bytes to the
old estimator and you get the old numbers, to the last digit, forever. What
died was not reproducibility but *claim-eligibility*, because faithfully
reproducing a computation whose model is false reproduces the error
faithfully. That has a concrete consequence: each corpus member's bound is the
new derivation itself, **not** the larger of the old and new values. Taking
the maximum would look conservative while smuggling the falsified model's
numbers back in wherever they happened to be bigger. A superseded model is
superseded, not demoted to a floor.

## 6. What a bundle remembers: capture eras and the claim barrier

The section above leaves an obvious question: hundreds of stored measurements
on this machine were taken under an estimator now known to be wrong. What
happens to them?

**Every bundle carries its own capture-pipeline identity.** A stored bundle
records the anchor method that produced it, paired inseparably with a schema
label — `p2-038.1`, `.2`, or `.3` for the three generations of capture
pipeline. One canonical table maps method to label, and the *method* is the
single key everything dispatches on. If a bundle's label and its method
disagree it is refused outright, rather than resolved in favour of either: the
record is lying about itself and there is no honest way to guess which half is
true. Where the capture machinery produced no such evidence at all, no era is
synthesised — the evidence is marked explicitly incomplete, because inventing a
plausible label is the one failure this design must never have.

**Two questions, deliberately kept apart:** *can this bundle be verified?* and
*may this bundle support a claim?*

- **Strict verification is era-faithful, forever.** Every stored bundle is
  re-derived under *its own* recorded method — `.1` bundles under the legacy
  replay, `.2` under the old censored-intersection derivation, `.3` under the
  current one — and crossing an era against another era's method refuses. The
  748 stored second-era bundles in the repository tree (off-repository mirrors
  hold more) therefore keep every bit of their audit value: they still authenticate, they still replay byte-exactly,
  and their custody chains remain checkable. Nothing was rewritten, relabelled,
  or deleted.
- **Claim admission is a separate, mechanical barrier.** Supporting a
  published number requires the *positive presentation* of the current
  claim-bearing method — one closed set with one member today. Absence is not
  permission. One shared test implements this, and the three places that admit
  evidence to a claim — the analysis, the floor extraction, and the
  whole-window check — all call that one test. None of them re-implements it or
  writes the method name into its own code, so the barrier cannot quietly decay
  in one place while still holding in another.

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
different version. So the instrument's identity is pinned cryptographically
by the **calibration acceptance artifact** — currently
`d079_calibration_acceptance_v2_n17_r6`, whose own file hash begins
`0227bca3` — which records:

- the 17-member derivation corpus (every member's b_fiducial, byte-exact),
- the decision thresholds derived from that corpus,
- and the SHA-256 hashes of the four estimator source files that computed
  them (the fiducial estimator, the uncertainty machinery, the sampler
  adapter, and the reducer).

Any change to any of those four files — even a one-line comment — makes
every downstream consumer refuse with a *staleness* error, on purpose. A
changed estimator is a different instrument, and a different instrument
does not inherit the old instrument's evidence. When an estimator change
is genuinely wanted (the detection budget above was one), the acceptance
is **reissued**: all 19 members of the replay set are re-authenticated from
their raw artifacts under the new code, every derived quantity is compared
against the predecessor's record with zero mismatches tolerated, and the new
artifact publishes a delta naming exactly which pins rotated and to what. The
reissue is "science-neutral by construction": if anything beyond the intended
code pins differs, it does not issue.

**The generation chain.** Because the pin rule has no exceptions, the artifact
has a lineage rather than a version number, and every link in it is a document
you can open:

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
hash, the before-and-after hash of every estimator source that changed, and the
record that the full 19-member replay reproduced every anchor bound,
disposition, projection cell count and b_fiducial value exactly. Predecessor
generations are kept byte-identical forever; a superseded generation is retired
as the *live* artifact, never edited.

**Policy constants are resolved, never copied.** A trap lives in that table:
the bracket screen was 0.010818 s under the 19-member generations and is
0.009724 s under the 17-member ones. If any consumer held that number as a
literal, historical replays would silently start judging old data by new
thresholds. So no such literal exists anywhere in the mint lane — a regression
test forbids both digits (the one home for the registered values is the
acceptance registry itself, which the guard deliberately exempts) — and every
consumer resolves the screen and the
allowance rule *from the generation the supplied artifact itself names*. An
unregistered identity refuses; an artifact whose stated screen disagrees with
the registered value for its identity refuses rather than a winner being
chosen. That is what lets the live instrument move while every historical
replay stays byte-exact: the past is judged by the rules of the past, by
machinery rather than by memory.

## 8. Floors: what the instrument may claim to distinguish

A **detection floor** is the empirically demonstrated smallest energy
difference the complete measurement system can distinguish for a given
operation family on this exact software stack. Not the sampler's noise
floor — the *system's* floor, including attribution error, drift, and
everything the protocol could not remove.

**How a floor is measured:** by running designed workload pairs whose true
difference is known — most importantly *identical* pairs, where the true
difference is exactly zero — and observing what the pipeline reports.
The observed spread of reported "differences" between identical workloads
is the false-difference scale; the floor is set above it.

**ABBA blocks.** The workhorse design: measure condition A, then B, then B,
then A. Any slow drift in the machine's state (thermal, background
services settling) affects the two A's and the two B's near-symmetrically
and cancels in the paired comparison. Simple alternation (ABAB) would
alias a linear drift straight into the A−B difference; ABBA cancels it to
first order. The floor packs use both absolute arms (single-condition
bundles, for level estimates) and ABBA comparison blocks (for difference
estimates): the current successor packs carry, per floor family, 10
absolute bundles plus 10 ABBA blocks of 4 members each — 100 science
configurations per floor pack, all frozen before any data is seen.

**The floors are attribution-limited, and labeled as such.** On this
instrument, the noise-limited component of the floor is around 0.3 J, but
the attribution term — b_fiducial applied at the phase boundaries —
dominates and lifts the working floor to roughly 1 J for the characterized
phases. That regime is a *ratified finding*, published as a label on every
floor rather than hidden: this project's floors say "attribution-limited,"
and a reader comparing instruments should understand that a better clock
anchor, not a quieter machine, is the upgrade path. Claims built on the
floors then carry additional pre-registered claim-side margins, putting
the effective bar for a claimed difference near 5 J. Numbers smaller than
the labeled bar are not claimed, full stop — the pipeline refuses to emit
them as findings.

**Per-phase, per-stack.** A floor is measured for a named operation family
(decode; prefill at a fixed 256-token prompt) on a named stack (exact
model artifact hash, runtime version, quantization, tokenizer, OS build).
Floors do not transfer across phases, prompt lengths, or stacks; the
256-token prefill floor is its own measured artifact precisely because
transporting a floor from a different prompt length would be an assumption
wearing a measurement's clothes.

## 9. The quiet machine: protecting the signal

Everything above assumes the machine's background is stationary and small.
It is not, unless forced to be. Resident daemons index files, analyze
photos, check for updates; the display and its friends draw power; other
software (including this project's own AI tooling) burns CPU. None of it
is distinguishable from workload energy after the fact.

The defenses, each with its scar tissue:

- **The screensaver story.** In an early floor campaign, 43 of 50
  calibration bundles were contaminated because a video screensaver
  engaged during the windows — the six "anomalously low" bundles were the
  *clean* ones. The protocol now forces the display asleep (a transient
  display-sleep command, not a screensaver), verifies screensaver
  disengagement, and treats display state as a first-class fence.
- **The process census.** Before quiet work, five process probes sweep the
  machine: a keep-awake census (no stray `caffeinate` holders), an
  agent census (no AI-tooling sessions), a browser census, a monitor
  census (no samplers or watchers already running), and a maintenance
  census (Spotlight indexing, photo analysis, software update, backups).
  The census patterns were themselves calibrated against reality: a
  qualification capture of the machine's true quiet state showed that
  several system daemons are permanently resident (seven Safari support
  agents with Safari closed; `watchdogd` matching a naive "watch"
  pattern), and the probe patterns are being corrected against that
  ground-truth fixture rather than against wishful assumptions.
- **Power and thermal fences.** AC power at full charge (a mid-window
  charge-termination is a step change in the power picture — this was
  observed directly during an operator qualification probe), thermal
  state nominal before starting, and at least ten minutes of untouched
  idle settling before any calibration.
- **The agent quiesce rule.** The project is developed largely by AI
  agents — and an agent session is background load like any other. No
  measurement starts while any agent session is active. The overnight
  first-light window was run by a single fenced driver script with every
  fleet shut down, and the driver's own censuses are part of the capture's
  custody record.

## 10. Frozen plans and the freeze ceremony

**Why freeze:** the most seductive way to corrupt a measurement campaign
is to adjust it after seeing data — drop the awkward bundle, tweak the
schedule, re-run the unlucky block. The defense is to make the plan
physically unchangeable before the first byte of data exists.

**What a pack is.** A campaign is compiled into a **pack**: a committed
directory containing every configuration the night will run (all 100
science configs for a floor pack), the order manifests fixing the
execution sequence, the calibration plan, condition-family definitions,
and a `plan_tree.json` that binds the pieces together with hashes. Packs
are generated by committed generator programs, so the entire pack is
reproducible byte-for-byte from its generator — and audited regressions
prove the generator cannot overwrite an earlier generation's committed
bytes (a defect class that was found, fought through seven rounds of
implementation and nine audits, and closed with generational proofs). That
property has since been exercised for real rather than only proved: the
version-2 packs have generated a version-3 family without altering a byte of
the version-1 or version-2 packs — see *Lineage in practice*, below.

**The freeze receipt.** Freezing a pack mints a receipt: a cryptographic
attestation binding the plan's exact bytes (via SHA-256 of the calibration
plan, which itself embeds the hashes of everything else) plus the
readiness evidence rows evaluated at freeze time. Two properties are
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
  receipt, verified before the successor may mint. Superseded packs remain
  valid *historical* records — their receipts still authenticate — but the
  lineage is explicit and machine-checked in both directions.

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
carry a hash that verifies cleanly, and nothing would reveal that it is out of
date. The successor
packs therefore reached their would-be-frozen state already bound to the
live generation: the retarget happened in the unfrozen drafts, before any
receipt existed, so no frozen pack ever pointed at a stale generation.
**Freeze is deliberately the last step:** the successor family's readiness
evidence has been authored at the designated measurement checkout — eleven
evidence documents per pack, thirty-three in all, every one passing — and the
freeze receipts chaining each `_v3` pack to its `_v2` predecessor's
`freeze-0002` are the one step still outstanding. Nothing may be collected
under the successor family until they exist.

**Identity-pin projection.** Before freezing, a projection tool reads the
*actual* model files and runtime the night will execute (the real
safetensors on disk, hashed; the real runtime identity) and pins them into
a projection receipt. This closes the gap between "the plan says model X"
and "the bytes on disk are model X."

**A subtlety that cost a night's receipts:** freeze receipts authenticate
the *absolute path* of the pack they froze. Receipts minted in a temporary
working directory are worthless on the real measurement night. The
project's receipts are therefore minted in the designated measurement
checkout — the exact directory the arm night will run from — and the first
set, minted in the wrong place, was reverted on the record and re-minted
correctly. (The revert commits are still in the history; honest history is
preferred over clean history throughout this project.)

## 11. Arming, the window, and the operator

A measurement night is a ceremony with a deliberately narrow shape.

**Readiness evidence with freshness horizons.** Before arming, evidence
rows are authored proving the machine and pack are ready — clock state,
quiet censuses, pack authentication, regression-suite results, and so on.
Volatile evidence (anything about the machine's live state) expires on a
20-minute monotonic horizon; procedural evidence lasts six hours. Expired
evidence refuses the arm. The horizons encode a simple truth: a statement
about a machine's state is only evidence while the state can't have
drifted.

**The single-use arm capability.** Arming mints a capability that the
launcher consumes *atomically, exactly once*. The launch either happens
under the armed plan or the capability burns — there is no
"launch, tweak, relaunch under the same arm." The consumption is bound to
the arm-time attested inputs through a five-hop digest chain, so a
substituted manifest or foreign context is refused before any filesystem
effect.

**The window chain.** The launched chain runs the pack's members in frozen
order, brackets them with the pre/post calibrations, writes runs into
custody-controlled roots, and refuses on any deviation — a boot change, a
clock event, an out-of-order stage.

**The trusted-operator boundary — stated, not hidden.** The instrument
does *not* defend against a deliberately dishonest operator, and the
threat model was explicitly ratified to exclude adversarial programs
running inside the measurement account. What the machinery guarantees is
that an *honest* operator cannot accidentally produce dishonest data: the
gates catch stale evidence, contaminated environments, plan deviations,
byte drift, and clock trouble. Fabrication by the single trusted human
with root access is out of scope — and the papers says so, because a
limitation stated is a boundary, while a limitation hidden is a landmine.

## 12. From samples to claims

The full pipeline, end to end:

1. **Plan** — packs generated, reviewed, committed.
2. **Freeze** — identity projected, evidence authored, receipts minted at
   the measurement checkout, everything pushed.
3. **Arm** — fresh readiness evidence within horizons; capability minted.
4. **Window** — quiet fences, clock discipline, bracket calibration,
   frozen-order members, bracket calibration, restore.
5. **Reduce** — for each member, integrate the three rails between the
   event-logged operation boundaries under the anchored clock; apply the
   bracket-derived timing allowance to every phase edge.
6. **Gate** — the whole-window verdict: acceptance artifact fresh and
   authenticated, every member presenting the current capture pipeline
   (section 6), brackets within drift allowance — screened against the
   generation the artifact itself names, never a copied constant —
   pre-flight screen passed, custody complete, every member's lineage
   authenticated. Any failure refuses the window's evidence — recorded, not
   discarded.
7. **Claim** — only differences exceeding the labeled floor plus
   pre-registered margins, under the pre-registered statistical family
   (the first campaign's two contrasts form one Holm-corrected family at
   α = 0.05, two-sided, directions pre-registered), on the named stack,
   within the named boundary.

What a published claim finally says, in plain words: *on this exact
hardware, OS build, runtime, and model artifact, measured across these
three rails with attribution bounded by an in-window calibration, the
energy of operation A exceeded operation B by E joules, where E clears an
empirically demonstrated floor of F joules plus stated margins — and here
is the complete refusal log of everything the instrument declined to
claim along the way.*

## 13. The verification culture, briefly

Every mechanism above exists in code with fail-closed refusals, and the
project's process mirrors the instrument: implementations are audited
adversarially by independent reviewers, fixes are re-audited (fix rounds
have introduced defects often enough that the re-audit is mandatory),
consequential reversals go to cold reviews performed without the authors'
framing, and the operator is qualified through scripted evidence-producing
sessions. The project's own history is the argument: essentially every
failure class was caught by a *different* layer than the one that produced
it — the audits catch the implementations, the cold reviews catch the
audits, the operator's live runs catch what no sandbox could see, and the
instrument's own refusal gates caught a mis-set parameter on their first
night of contact with reality. The run reports under `docs/run_reports/`
are the evidence trail, and they are written to be read.

## 14. Glossary

- **ABBA block** — a measure-A, B, B, A schedule that cancels slow drift
  to first order in paired comparisons.
- **Acceptance artifact (D-079)** — the issued document pinning the
  calibration corpus, thresholds, and estimator code hashes; the
  instrument's identity card.
- **ANE** — Apple Neural Engine, one of the three measured rails.
- **Arm / arm capability** — the single-use, atomically consumed
  authorization to launch a frozen plan.
- **Attribution error** — energy assigned to the wrong operation because
  of clock misalignment between workload and sampler.
- **b_fiducial** — a capture's measured worst-edge timing bound: how far a
  commanded pulse edge can appear displaced in the trace.
- **Capture era** — the generation of capture pipeline that produced a
  stored bundle, recorded inside it as an anchor method paired with a schema
  label (`p2-038.1/.2/.3`). Old eras are verified forever under their own
  method; only the current era may support a claim.
- **Census** — the pre-window process sweeps proving the machine quiet.
- **Claim barrier** — the single shared test every claim-side consumer calls,
  admitting a bundle only on positive presentation of the current
  claim-bearing capture era.
- **Clock anchor** — the measured relationship between the system's wall
  clock, in which the sampler labels each row and the workload stamps its
  pulse commands, and the sampler's own monotonic timeline, in which each
  row's duration is reported; it is published as an interval. The current
  method solves for the two clocks' *rate* as well as their offset and
  refuses when no single rate fits (section 5).
- **Detection budget** — the preregistered cap on the pulse detector's
  search effort; exhaustion refuses the capture as non-convergent.
- **Detection floor** — the demonstrated smallest energy difference the
  complete system can distinguish for a named operation family and stack.
- **Fiducial pulse train** — the 59-pulse known workload used to measure
  attribution error.
- **Freeze receipt** — the cryptographic attestation that a pack's bytes
  are final; the receipt is the frozen state.
- **Generation (of the acceptance artifact)** — one issued link in the
  artifact's lineage. Predecessors are kept byte-identical forever, and each
  consumer resolves its thresholds from the generation the supplied artifact
  names.
- **Identity-pin projection** — the receipt pinning the actual model and
  runtime bytes a night will execute.
- **Pack** — the committed, frozen directory of every configuration a
  measurement night will run.
- **powermetrics** — Apple's telemetry sampler; the measurement primitive.
- **ppm (parts per million)** — the unit for clock-rate differences; 1 ppm
  is one microsecond per second, so 7 ppm accumulates about 1.4 ms over a
  200-second capture.
- **Rail** — a named power channel (CPU, GPU, ANE); the measurement
  boundary is exactly these three.
- **Refusal** — a recorded decision not to admit evidence when a gate
  fails; the instrument's most common and most important output.
- **Reissue (science-neutral)** — a new acceptance generation forced by an
  estimator byte change alone, whose neutrality is proven by replaying the
  whole corpus and diffing every derived quantity, not asserted.
- **Window** — one uninterrupted, calibrated, quiet collection session.
