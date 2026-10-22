# align-apple lane report

## SUMMARY
Work in progress: this is the initial, remote inspection checkpoint.
The Apple lane was absent and was created from spine 4d47c4362352ccd8d4d904134a79f0d8260b21b5.
The pipeline plan, shared records and cross-lane protocols have been read.
The named workload, suite, generator, MLX and powermetrics files have been inspected.
Existing MLX workloads execute in process through MlxRuntimeAdapter.
Powermetrics stop_sampling_with_evidence owns the current rate-aware anchor.
The selected cloud workspace has not yet become usable; no local commands can execute.
No hardware measurement, installation, arming or loading has occurred.

## FILES
- .codex-report/align-apple.md: initial inspection and execution blocker checkpoint.

## PUBLIC API
None implemented at this checkpoint.

## TESTS RUN
None: exec_command reports "No usable execution environment is available."
No extras installed.

## END-TO-END
Not yet run; blocked on workspace startup.

## DECISIONS I MADE
- Preserve records.py, interfaces.py and PIPELINE.md unchanged.
- Reuse PowermetricsTelemetryAdapter.stop_sampling_with_evidence and its returned clock evidence; do not duplicate parsing or invent a spawn-midpoint anchor.
- Prefer the existing in-process MLX path because current workloads already use it; complete adapter design after local inspection.
- Treat benchmark wall seconds and alignment monotonic integer nanoseconds as distinct domains, with a lane-local conversion and explicit uncertainty.
- Use only the authorized lane branch. This checkpoint uses the GitHub connector because the local executor is unavailable.

## CONTRACT-CHANGE
None at this checkpoint.

## OPEN ISSUES
- Workspace startup prevents checkout, local inspection, implementation and test execution.
- Sampler, endpoint, workload, synthetic campaign integration and Apple path document remain to be built.

## NEEDS_RULING
None at this checkpoint.
