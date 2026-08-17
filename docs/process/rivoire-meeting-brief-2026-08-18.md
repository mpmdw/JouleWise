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
The resulting repair program has now been executed: the night-of-measurement
capture contract was corrected, arming and launch were bound into one
authenticated step, and claim analysis was changed to accept only a complete,
authenticated, finalized result. Missing lineage, incomplete custody, stale
inputs, or an unproved derivation now produces a recorded refusal from
collection through claim analysis. The successor-pack re-freeze is in progress;
it precedes the focused re-audit and the next READY-candidate council.

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
