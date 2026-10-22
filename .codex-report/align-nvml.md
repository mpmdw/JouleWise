# NVML lane implementation report

## SUMMARY

Implementation in progress; this first commit preserves the lane intake.
Read PIPELINE.md, records.py, interfaces.py and the existing nvidia_smi adapter.
The shared records and protocols will remain unchanged.
The managed execution environment is still starting; no hardware was exercised.
Planned work: ctypes NVML sampling, duty-window reconstruction, preflight and runbook.
A separate model is deriving an independent numerical twin for estimate_energy.
Only the exhaustive lane write scope is authorized.

## FILES

- `.codex-report/align-nvml.md`: this running implementation and verification report.

## PUBLIC API

Planned: NvmlSampler.start(), NvmlSampler.stop(), plan_offsets(period_ns, duty_fraction, repeats), estimate_energy(runs), and the preflight module CLI.

## TESTS RUN

None yet: no usable shell environment is available. No hardware validation claimed.

## END-TO-END

Pending implementation and execution.

## DECISIONS I MADE

- Keep independent legacy, instantaneous-field, averaged-field and energy-counter traces.
- Use structured JSON in PowerTrace.notes for lane-local timing and capability diagnostics.
- Preserve raw cumulative counter readings and flag discontinuities; do not invent continuity.
- Do not extrapolate a finite uncertainty over unobserved work without an explicit power bound.
- Cycle phase offsets after a minimal tiling to obtain within-phase replicas for repeatability.
- Preserve unsupported or unavailable measurement outcomes as recorded flags.
- The user brief selects this bounded synthetic-only lane over unrelated repository queue work.

## CONTRACT-CHANGE

Proposed: structured per-sample timing and sensor-window metadata in PowerTrace. NVIDIA's public NVML header documents one-second output averaging for H100 legacy power and the average field; those outputs need a multi-window description in addition to the supplied A100/H100 25-of-100 ms physical-sensor assumption. The implementation will adapt locally and flag the mismatch without editing shared contracts.

## OPEN ISSUES

Implementation and tests remain pending workspace startup.

## NEEDS_RULING

none
