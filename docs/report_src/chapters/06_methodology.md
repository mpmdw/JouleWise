# Methodology

Each run's lifecycle is: idle-baseline sampling, model prepare, warmup,
marked measured window around the request, cooldown. The measured window is
defined by explicit start/end markers in the event log, and all energy
metrics integrate power samples strictly inside that window.

Two energy bases are always distinguished: **gross** energy is the raw
integral of package power over the measured window; **idle-subtracted**
energy removes the run's own measured idle baseline. Gross per-request energy
is the headline basis. Idle-subtracted energy is reported separately as a
within-device secondary view and is not used to rank devices or configurations.

The measurement boundary is named on every artifact. For the retained
historical corpus — **VOIDED permanently for claim use** under the
[root README void disposition](../../../README.md#current-state) — the recorded
boundary is Apple SoC CPU + GPU + ANE package power via powermetrics. Wall
power, memory, and peripherals are outside this boundary and no claim extends
past it.

Repetitions run sequentially per stack with cooldown gates between them;
cooldown-cap hits are recorded as quality flags and carried visibly into
tables and claims rows, never silently dropped. Strict validation guarantees
structural and provenance integrity of a bundle — required files, hashes,
marker pairing, trace consistency. It is not physical calibration and is
never presented as such.

Claims are routed through the claims ladder (D-037): L1 stack-specific
instrument observations need no contrast machinery; L2+ comparative claims
require frozen contrasts and verdict artifacts and are out of scope for the
legacy slice in this document.
