# Rivoire Meeting Brief: JouleWise Instrument Readiness

## What the instrument is

JouleWise treats Apple's *powermetrics* processor-package counter as a
scientific instrument rather than a logging convenience. It calibrates phase
timing inside each uninterrupted measurement window, measures repeatability
and drift, and preserves the raw power trace, runtime boundaries, and complete
derivation chain. It publishes a detection floor—the largest false difference
the admitted measurement system can produce—and refuses a result when the
evidence cannot support it.

## Retained a9/a10 characterization

The retained conclusion is attribution-limited, not noise-limited. Across
a10's 30 phase-absolute members, composed boundary bounds span 25.6–31.1 ms;
phase-envelope-to-bound quotients span 21–58 W; and ordinary-prefill envelopes
span 0.98–1.47 J. These quotients are derived from each member's envelope and
bound, not measured power steps. The a9 window supplies reference and bracket
context but contains no phase-absolute members. The familiar illustration is
pinned to member `p2015-df-ph-prefill-abs-r01`: its 31.07 ms bound and 1.016 J
prefill envelope give a derived quotient of 32.7 W. Repetition can refine the
smaller repeatability term, but it cannot average away the uncertainty caused
by placing samples at the phase boundary.

## What changed in the last two weeks

The readiness audit returned NOT-READY, so no measurement window was spent.
The repair program's code wave has been executed and merged (the program
itself closes only with the re-freeze, re-audit, and READY-candidate council
below): the night-of-measurement
capture contract was corrected, arming and launch were bound into one
authenticated step, and claim analysis was changed to accept only a complete,
authenticated, finalized result. Missing lineage, incomplete custody, stale
inputs, or an unproved derivation now produces a recorded refusal from
collection through claim analysis. Preparation for the successor-pack
re-freeze is underway — its inputs are built and under adversarial review —
and the atomic re-freeze executes next, before the focused re-audit and the
READY-candidate council.

## Overnight update (2026-08-18, morning of the meeting)

The successor-pack re-freeze executed overnight, through its confirmation
point (publication awaits an explicit final sign-off). And the
shakedown-first sequence produced its first results:

- **Quiet-state baseline:** a ten-minute idle capture on the fenced quiet
  machine; GPU rail essentially silent (mean 0.34 mW, 95.8% of samples
  exactly zero), thermal state nominal throughout — the machine's quiet
  state is as quiet as the protocol assumes.
- **First calibration capture, and a safety mechanism proving itself:**
  the fixed-work pulse calibration ran overnight. The capture itself was
  strong (pulse signal-to-noise at the same level as the issued
  calibration corpus). The newly added detection-budget check — a cap on
  how much search the pulse detector may spend before declaring itself
  unable to converge — refused the capture: the cap had been set below
  what real traces need, something no repository test could reveal
  because the raw calibration traces live outside the repository. The
  cause was isolated with a discriminating experiment (issued corpus
  members hit the same cap; the previous detector and a raised cap both
  converge on the same data), the cap was recalibrated from a complete
  sweep of all 34 retained raw calibration traces (maximum observed
  demand 137,189 search cells; cap set to 165,000, ~20% above the
  maximum — derived from the corpus, not tuned until the night passed),
  and the same overnight capture then re-derived cleanly:
  **timing-attribution bound b_fiducial = 0.0309 s, inside the issued
  corpus band [0.0227, 0.0336]**.

The instrument is verified on real overnight data, and the episode is the
methodology working as designed: a conservative gate refused first, the
refusal was diagnosed rather than retried, and the correction came from
the complete evidence base.

## What the first campaign answers and how it runs

The first claim campaign asks whether the named stack can resolve the difference
between the two model sizes in token generation and in prompt processing under
a fixed synthetic 256-token prompt. The sequence is shakedown-first: a
quiet-state baseline and calibration-only instrument check must show that the
signal is not polluted before any claim window begins. The alpha, beta, and
gamma windows then collect the small-model floor, the large-model floor, and
the model-size contrasts under their frozen packs. The two prospective
contrasts are one pre-registered Holm family (\(\alpha=0.05\), \(m=2\)); the
tests are two-sided, and their scientific directions were pre-registered. The
256-token prompt-processing floor is a dedicated measured artifact whose floor
cells are pre-registered in the frozen packs, not a value transported from a
different prompt length.

## Questions for Dr. Rivoire's judgment

- Is one Holm family for the token-generation and 256-token prompt-processing
  contrasts the right familywise-error choice, given that both are planned
  demonstrations of the same instrument and both remain separately
  floor-gated?
- Is the stated transfer assumption defensible: calibration pulses are
  graphics-processor matrix multiplications under light central-processor load,
  while the science workload is sustained mixed-load inference?
- Is *attribution-limited* the right publication label when boundary placement
  dominates repeatability, provided that the exact corner-widened floor is
  published and the label never overrides any other refusal?
