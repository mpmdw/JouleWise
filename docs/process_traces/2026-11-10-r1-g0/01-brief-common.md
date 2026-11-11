# Brief (common): R1 step_30b G0 start-gate timeout — what change lets R1 measure?

Read first: `docs/process_traces/2026-11-10-r1-g0/00-diagnosis.md` (this branch),
RUN_STATE.md items 251-253 on main, and the code at the frozen measurement root
`M=/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2`
(head 20e9edbc4; READ ONLY, run no git command in M): `joulewise/align/apple/thermal_gates.py`
(`wait`, G0), `joulewise/align/apple/r1_runtime.py` (soak reference, G0_TIMEOUT_REASONS),
and the v4 protocol text that registers the thermal gates (find it under `docs/`;
grep `delta_slow_c`, `G0`, `soak_reference`). Custody data (READ ONLY):
`/Users/edr/night-align/r1-20261111T014106Z` (this refusal) and the earlier
`/Users/edr/night-align/` pilot-v7..v9 and r0-v4-* roots. Do not read any
calibration value or any workload result; thermal, status and structural records only.

## The question
R1 is the v4 hardware rehearsal. Its first model step refused because G0 never
released: Tf08 settled about 1.1 C above a reference taken from an idle soak with
no runtime process and no capture, against a +1.0 C allowance. What is the smallest
change, justified by physics, that lets G0 release on a machine that is genuinely
back at its own idle state, without letting a hot start through? Candidates
include (not exhaustive): take the G0 reference from the member's own pre-load
idle_baseline (or a soak run with capture and the runtime live); size delta_slow_c
from measured idle spread; lengthen g0_cap_s; change s_slow. Say which, and why
the others are worse.

## Required evidence (execute; do not only read)
1. Replay the candidate rule(s) over every thermal record on disk where G0 ran
   or could have run (this R1 step, pilots v7-v9, every r0-v4-* root that has
   thermal data). Report, per candidate: releases, timeouts, time-to-release, and
   how far above the member's own idle state the start was at release.
2. State the effect size in physical terms: the cooling tail after release and
   what residual heat at release would cost on the smallest printed energy
   quantity (attribution limit about 1 J per run).

## Numbers rule (binding)
Every tolerance, threshold or bar you propose carries its derivation beside it,
from the quantity's physics (sensor resolution, measured idle spread, sample
interval, attribution limit) or from printed precision. A number with no
derivation is not written. Exact equality only where bit-identity is the property.

## Decide
Decide everything the governing texts determine and list it under "decisions I
made". Mark NEEDS_RULING only for a choice that changes which data count or a
printed number.

## Output
Write ONLY your report file (path given in your seat prompt). No code edits, no
git operations except reading, no network, no change to any custody or M file.
Never start or touch a measurement; no launchctl, pmset, sudo, systemsetup.
