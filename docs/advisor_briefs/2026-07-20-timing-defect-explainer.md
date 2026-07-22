# What the timing bug was — a plain-language explainer

Audience: project advisor. No prior context needed beyond: JouleWise measures
how much energy (joules) a laptop uses while running AI workloads, by reading
Apple's built-in power meter (`powermetrics`) while the workload runs.

## First, the direct answer: nothing produced energy

No workload ever measured negative. Every power reading in every recording is
positive and physically ordinary. The bug was not in the *measurement* of
energy — it was in the *bookkeeping of time*.

There are two clocks involved:

1. The **workload's clock**: our code logs "inference started at 12:00:00.808,
   finished at 12:00:01.179" using the system clock.
2. The **power meter's clock**: the meter writes a stream of power samples on
   its own timeline.

To compute "energy used by the workload," we add up the meter's samples that
fall between the workload's start and finish times. That only works if the two
timelines are correctly aligned. Our alignment method was crude: it assumed
the meter's recording began at roughly the moment we launched the meter
process, an estimate that can be off by up to about one second.

For a long measurement (a 60-second run) a half-second misalignment at the
edges hardly matters proportionally. But one of our test workloads runs for
only 0.37 seconds. With the alignment off by ~0.6 seconds, the window we
integrated landed on a near-idle stretch of the recording (0.27 J) while the
actual burst of consumption — about 8 J — sat a fraction of a second away in
the same recording, outside the misplaced window.

The security-camera analogy: the camera's clock is 40 seconds fast. The event
is on tape, plainly visible. But if you pull footage strictly for
"12:00:00–12:00:30 according to the camera," you get an empty hallway. Nobody
concluded the hallway *un-happened*; the clocks just disagree. Same here: the
~8 J was always in the recording; we integrated the wrong slice of it. A
report that juxtaposed "0.27 J reported" with "8 J outside the window" was
badly phrased and read as if energy were negative — it is not, and we have
reworded it.

## Your bottom line is correct, and we accept it

> "If the bottom line is that you can't run very short workloads and collect
> reliable data, that's totally normal and fine."

Agreed, with no gymnastics: **sub-half-second workloads are below this
instrument's resolution and we will not make claims about them.** The meter
samples 10 times per second; a 0.37-second run contains only 3–4 samples, and
our own quality gates already reject that as too few regardless of the clock
fix. Those tiny runs exist in the protocol only as stress tests of the
instrument itself, and they did their job — one of them is what exposed the
clock bug.

The reason we still fixed the clocks rather than just dropping short runs:
the misalignment also affects *long* measurements, just more subtly. A
~60-second, ~148 J suite run with a half-second alignment error carries
roughly ±10 J of uncertainty at the window edges — and our statistical
method was trying to detect differences of about 1 J. So every energy number
now carries an explicit uncertainty range derived from how well the clocks
are known to align, and numbers whose range is too wide relative to their
value are automatically barred from claims.

## Translations of the jargon you flagged

- **"Loose pre-spawn bracket"** → the crude alignment estimate: we only knew
  the meter started somewhere between "just before we launched it" and "its
  first output," a window of about ±0.5 seconds.
- **"Carrying ±N J of anchor sensitivity"** → because the clock alignment is
  uncertain by up to X seconds, the computed energy can change by up to N
  joules depending on where the alignment truly lies. We now compute and
  report that range for every number instead of pretending it is zero.
- **"Conflated source provenance with metric eligibility"** → we mixed up two
  unrelated quality checks and reported the wrong one. Check 1: "the software
  that collected this data was clean, unmodified, and version-pinned" (this
  was true). Check 2: "this particular number meets the statistical quality
  bar to support a claim" (for most numbers this was false, and the system
  itself was saying so). Our status write-up advertised check 1 as if it
  implied check 2. That was an honesty bug in our reporting, now corrected.
- **"Cooldown cap-hit members"** → between measurements the protocol waits
  for the machine to settle back to idle, up to a 5-minute cap. Four
  measurements proceeded when the cap expired even though the machine had
  not fully settled. Those four don't count as clean repetitions.
- **"Suite-specific position confounding; the frozen floor absorbs it, no
  unfreezing"** → in our repeat-the-same-thing-four-times experiments,
  measurements later in each block came out slightly lower than earlier ones
  (about 0.2%, a warm-up/ordering effect). The statistically honest response
  is *not* to re-tune the analysis method after seeing the data; our
  pre-registered method is conservative enough to cover a bias of this size,
  so we keep it as-is, report the effect openly, and rotate positions in
  future experiment designs so ordering can't masquerade as a real
  difference.

## Where things stand

- The hardware and the meter are fine; the recordings are intact and
  arithmetically self-consistent to machine precision.
- Repeatability across nights is strong (long-run energies agree to ~0.3%),
  which is evidence the *instrument platform* is stable even though the old
  absolute numbers can't be trusted for claims.
- The clock-alignment fix is implemented and under adversarial review (two
  independent AI review tracks must both come back clean before we trust it).
- Before any new data collection, the full chain gets calibrated end-to-end
  with a known test pattern: the laptop fires 40 precisely-timed bursts of
  GPU work, and we measure how accurately the reconstructed timeline places
  them. That measured accuracy — not anyone's judgment — determines the
  shortest workload we are allowed to make claims about.
- No previously published energy number is being defended in the meantime;
  the affected tables are explicitly marked "under re-adjudication."

One process note: earlier status pages were written in the project's internal
shorthand, which is unreadable from outside — your feedback prompted a
standing rule that advisor-facing pages get plain language and defined terms.
