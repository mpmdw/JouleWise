# Alignment attribution lane

## SUMMARY
- Attribution lane created from spine 4d47c4362352ccd8d4d904134a79f0d8260b21b5.
- Governing pipeline, records and protocols read before writes; those files remain unchanged.
- Existing reducer and phase-share integration conventions inspected.
- Implementation and synthetic validation are in progress.
- Managed execution environment is pending/offline; no local commands or tests have run.
- This initial checkpoint was committed through the connected GitHub tool while workspace startup is unavailable.

## FILES
- `.codex-report/align-attribution.md`: lane checkpoint and eventual handoff.

## PUBLIC API
Pending implementation of the exact A4 signatures in the build brief.

## TESTS RUN
None yet: the execution tool reports "No usable execution environment is available."

## END-TO-END
Pending synthetic sensor worlds and twenty-turn episodes.

## DECISIONS I MADE
- Explicit user lane instructions select this bounded AGENT task; no hardware or paid services are used.
- WRITE_SCOPE overrides repository instructions to update global planning or run-report files.
- TASK_QUEUE.md is empty on the spine; RUN_STATE.md has no active stop card.
- No sensor_sim.py exists in joulewise/align on the starting spine; use a test-local generator.
- Reuse joulewise.reduce._integrate through a lane-local adapter; preserve nanosecond precision by subtracting an integer origin before conversion.

## CONTRACT-CHANGE
none

## OPEN ISSUES
- Managed execution environment startup has not completed; required shell setup and validation are pending.
- Independent twin comparison belongs to the integration gate; this seat must not claim to be its own independent twin.

## NEEDS_RULING
none
