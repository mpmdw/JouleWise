# Run Reports

This directory stores detailed "what I did and what is next" reports for major
JouleWise work sessions.

Before starting a big run:

1. Read `RUN_STATE.md`.
2. If `RUN_STATE.md` has an ACTIVE `ACTIVE_STOP_CARD`, follow that card
   first. It may point to a stream log or checkpoint artifact that is newer
   than the latest run report.
3. Read the latest report in this directory unless the stop card names a
   different resume authority.
4. Check the working tree.
5. Confirm the next task against `TASK_QUEUE.md` and `AGENT_PLAN.md`.

After finishing a big run:

1. Update `RUN_STATE.md`.
2. Add a new dated report here, or update the current report if the run is a
   continuation of the same task.
3. Include tests, commands, blockers, and concrete next steps.
4. If the run used delegation, tools, skills, councils, or worktrees, include
   the lightweight process trace below.

## Required Process Trace

Use this block for substantial runs. It is intentionally small; the goal is
to make the run auditable without committing raw scratch logs.

```text
## Process Trace

- Active stop card at start: none | RUN_STATE.md#ACTIVE_STOP_CARD
- Skills/playbooks used:
- Subagents / delegated sessions:
  - role/lens:
  - model:
  - prompt path or hash:
  - output path:
  - disposition:
- Worktrees / branches / PRs:
- Invocation manifest path, if any:
- Ephemeral artifacts:
  - path:
  - sha256 or stable id:
  - promoted_to:
  - not_promoted_reason:
- Council/debate scorecard, if any:
  - unique catches by severity:
  - accepted/rejected/false-positive counts:
  - lead triage/rework time:
  - decision IDs / queue rows created:
- Stop state at end:
```

For large delegated runs, add or reference an `invocation_manifest.jsonl`
with one row per substantial invocation:

```text
run_id parent_report role_or_lens model wrapper session_id prompt_sha256
prompt_path output_path status consumed_by disposition commit_or_pr
```

Report names should use:

```text
YYYY-MM-DD-short-topic.md
```
