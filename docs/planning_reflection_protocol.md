# Planning Reflection Protocol

Every phase and substantial run must begin with a planning audit before new
implementation work starts. The goal is to keep plans decision-ready, not merely
aspirational.

## When To Use This

Use this protocol at the start of:

- A new phase.
- A major feature inside a phase.
- Any run that changes experiment methodology, schemas, adapters, metrics, or
  data layout.
- Any run that depends on physical hardware, borrowed devices, or external
  approvals.

## Start-Of-Run Planning Audit

Before implementing, answer these questions in the run report or current phase
doc:

1. What is the exact goal of this run?
2. What prior state did I inspect?
3. What assumptions am I inheriting?
4. Which checklist items become closer to done?
5. What evidence will prove each item is done?
6. What commands, files, measurements, or written approvals will be captured?
7. What can fail without blocking the project, and how will that failure be
   recorded?
8. What should not be changed during this run?

For random or newly discovered user tasks, also update or consult
`TASK_QUEUE.md` before implementation. The task should be ranked against current
phase gates, recent commits, recent run reports, and workspace safety.

## Step Planning Quality Bar

Each non-trivial step in a phase plan should include:

- **Objective**: what the step accomplishes.
- **Inputs**: files, hardware, approvals, configs, or prior artifacts needed.
- **Actions**: concrete work to perform.
- **Evidence**: artifact, command output, test, measurement, or written decision
  that proves completion.
- **Acceptance criteria**: the pass/fail condition.
- **Fallback**: what to do if the preferred path fails.

If a step lacks evidence and acceptance criteria, it is not ready to execute.

## End-Of-Run Reflection

At the end of every substantial run, update `RUN_STATE.md` and a dated
`docs/run_reports/` report with:

- What changed.
- How the work was ranked in `TASK_QUEUE.md`.
- What was verified.
- What failed or remained uncertain.
- Whether the plan was accurate.
- What planning gaps were discovered.
- The next exact step and its evidence requirement.

## Phase Exit Rule

A phase is not complete until its exit checklist has evidence for every required
item. Evidence can be one of:

- Passing tests.
- Captured command output.
- A committed artifact.
- A raw measurement bundle.
- A written decision or approval.
- A documented unsupported/failure verdict.

Do not mark a phase complete because the next phase is tempting. That way lies
beautiful chaos, and also bad benchmarking.
