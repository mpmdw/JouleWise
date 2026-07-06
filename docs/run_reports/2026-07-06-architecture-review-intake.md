# 2026-07-06: External Architecture Review Intake (Codex)

## Context

The user ran an independent architecture review (Codex) over the
planning corpus and source, and asked for an agree/disagree assessment
with the agreed items implemented. The review's bottom line — keep the
current architecture — required no action; five improvement suggestions
and three operational risks were triaged. Docs/design-only run; no
production code changed (implementation stays in Slice 2N per plan).

## Triage Of The Review's Suggestions

Agreed and implemented (as design decisions + plan updates):

1. **`RunContext` before real adapters** → accepted as **D-024**
   (options recorded: piecemeal params / writer injection / context
   object; chosen: immutable context — data, not capability). Slice
   2N.1 rewritten to implement it; playbook M1 updated; the earlier
   open question in 2N.1 ("new param vs writer vs context") is now
   settled rather than deferred to the implementer.
2. **Shared bundle read layer** → accepted as **D-025**. New work item
   2N.8 (`BundleReader`; reducer/report/validate-bundle port onto it);
   2N.7's rail alignment must be implemented via it, not spot-fixed;
   Phase 4 Stage 4.1 now requires `aggregate` to be a reader consumer,
   not a fourth parser.
3. **Remote runner as a node-worker protocol** → accepted. New
   cross-cutting contract `docs/contracts/node_worker_protocol.md`
   (conceptual shape + wire-format requirements checklist; details
   pinned during 2K). Guide §2K and playbook M8 now point there;
   `AGENT_PLAN.md` source-of-truth map row added.
4. **v0.2 design spike during 2N (no implementation)** → accepted,
   scoped tightly as new item 2N.9: a design-only compatibility check
   of RunContext/BundleReader against D-008's `run_kind`/`split_plan`
   and the composite-bundle layout; deliverable is a findings note; NO
   schema change (R-015 stands).
5. **SQLite before DuckDB, later** → agreed with the posture (which
   matches the existing plan); recorded as one clause in Stage 4.1's
   design notes so the escalation path is written down.

Agreed, no action needed (already the plan): 2N is the right next move;
R-016 backup protocol is real work gated before 2I data.

Qualifications recorded (where the review was softened):

- `node_role` enters as an optional context field only — Phase 3
  concepts get a seam now, not machinery.
- The v0.2 spike is a documented check, not an implementation.
- The node-worker contract fixes the conceptual shape now but leaves
  wire-level pinning to 2K, to avoid speculating details the first
  implementer will learn.

## Operational Risk: Stale Desktop Workspace

The review flagged that the agent workspace still points at
`~/Desktop/CapstoneRivoire/Capstone`. Confirmed: the path contains only
a harness-recreated `.claude/settings.local.json` (this session's own
permission approvals, Desktop-scoped). The real repo settings exist at
the new path. Fix is user-operational: launch future agent sessions
from `~/code/CapstoneRivoire/Capstone`, then delete the Desktop
leftover. Until then, agents launched the old way must `cd` to the real
repo (playbook M0 step 1 reads `RUN_STATE.md`, which names the path).

## What Changed

- `docs/decision_log.md`: D-024, D-025 (+ index rows).
- `docs/phase_2/phase_2_plan.md`: Slice 2N items 1/7 rewritten, items
  8/9 added; acceptance criteria extended.
- `docs/phase_2/phase_2_exit_checklist.md`: 2N row evidence updated;
  (earlier same-day: CI row closed via Actions run #7).
- `docs/agent_playbook.md`: M1 sections 2N.1/2N.7 rewritten, 2N.8/2N.9
  added; M8 points at the node-worker contract.
- `docs/contracts/node_worker_protocol.md`: new.
- `AGENT_PLAN.md`: source-of-truth map row for the new contract.
- `docs/phase_4/phase_4_plan.md`: Stage 4.1 sqlite-before-DuckDB clause
  + aggregate-uses-reader requirement.

## Commands / Verification

```bash
python3 -m unittest discover -s tests   # 169, OK (skipped=8)
```

## Next Agent Should

Unchanged from the queue: M1 (Slice 2N — now nine items, with D-024/
D-025 pre-decided), M2 (backup protocol), M3 (related work). The user
should relaunch agent sessions from `~/code/CapstoneRivoire/Capstone`.

## Decision Log / Risk Register Deltas

- New: D-024 (RunContext), D-025 (shared bundle reader).
- Risk register: no status changes at intake time; see follow-up.

## Follow-Up (same day): second review pass, housekeeping fixes

The reviewer re-checked the live repo and endorsed the intake; its three
housekeeping catches were all valid and are fixed:

1. **Wording:** D-024/D-025 statuses now read "accepted; implementation
   pending / to be implemented in Slice 2N" — the earlier "implemented
   in Slice 2N" phrasing could mislead a future agent into assuming the
   seam/reader already exist. They do not.
2. **R-017 staleness:** the register still said the repo move was
   queued after `RUN_STATE.md`/`TASK_QUEUE.md` recorded it complete — a
   drift violation of our own rules. R-017 is now marked mitigated
   (2026-07-05 move), likelihood high→low, with the residual exposure
   (stale session launch paths; never placing repo or `runs/` under
   iCloud) kept live.
3. **2N sizing:** playbook M1 now prescribes landing 2N as three commit
   groups (A: RunContext/window seam; B: BundleReader + policies + CLI;
   C: schema/metrics/v0.2 note) with the suite green after every item,
   and names a completed group as the clean mid-slice handoff point.
