# JouleWise Run State

Last updated: 2026-07-07 PM (multi-stream checkpoint + C-009
meta-review consensus; RUN_STATE slimmed to intake-pointer shape per
that consensus)

## Start Here For Every Big Run

Before starting substantial work:

1. Read this file.
2. Read `TASK_QUEUE.md`.
3. Read `AGENT_PLAN.md` (phase index) and the active phase's plan doc under
   `docs/phase_N/`; per-item status lives in the phase exit checklist
   (D-023).
4. Read `docs/planning_reflection_protocol.md`.
5. Check `docs/decision_log.md` before re-deciding anything; check
   `docs/risk_register.md` if starting a phase or a hardware-dependent task.
6. Check the last 2-3 commits with `git log --oneline --decorate -3`.
7. Check `git status --short --branch`.
8. Run `python3 -m unittest discover -s tests` unless the task is docs-only.
9. Do not commit local deletions or unrelated changes unless the user asks.
10. Heartbeat rule (`docs/milestones.md`): if >14 days passed with no run
    report and no recorded break, start with a milestones + risk review.

At the end of substantial work:

1. Update this file with what changed.
2. Update `TASK_QUEUE.md` with completed, added, or re-ranked tasks.
3. Add or update a detailed report in `docs/run_reports/`.
4. Record tests, commands, blockers, and the next best task.
5. Record new decision-log entries and any risk-register status changes.
6. Refresh `PROJECT_STATUS.md` if advisor-visible state changed.
7. Push green commits promptly (small doc/bookkeeping commits straight
   to main; multi-commit code series as branch + PR per D-031). Do not
   accumulate unpushed local state — the remote and the high-level docs
   (README, PROJECT_STATUS) are the user's and advisor's view.
8. Run a docs-consistency sweep before the final bookkeeping commit
   (delegate to a fast subagent): stale test counts, gate-state
   contradictions between prose summaries and checklist matrix rows,
   numbers cited in multiple places. Adopted 2026-07-07 (council log
   C-002) after a sweep caught drift in 6 files; prose status summaries
   must carry an as-of date and defer to matrix rows (D-023 extension).
9. Call out any dirty working-tree state that should not be accidentally
   committed.

## Current Project Status

**The instrument is CAMPAIGN-READY (2026-07-07).** Five parallel
streams landed in one session (PRs #2-#6 + two integration fixes):
D-014 cross-repetition uncertainty (per-metric Student-t CIs,
byte-identically re-derivable from bundles), rich DVFS/GPU telemetry +
idle-contamination gate (first live true positive) + environment
capture, mock-telemetry SystemClock hardening (live-verified at 1 Hz),
the 2M campaign tooling (deterministic matrix generator + resumable
sequential runner), and the kv-size helper. C-005 research agenda
(31 tiered questions + jw_mixed_v1 workload suite) appended to the
question bank. Still gated: 2K/2L (P1-006). D-016 provisional pick
stands. Suite: 415 tests (369 + the Stream F audit tests; 31 `expectedFailure`
pins await the P2-013 fixes). Stream F LANDED as PR #7 (merged; queue
item P2-013 created from its findings). A whole-project design council
(C-007) then settled the P2-013 fix design, re-ranked the queue
(P2-013 → P2-014 → 2M), and adopted machine-state lanes + the
two-claim-track framing — see the latest-run section below.

## What The Latest Run Did (2026-07-07 PM, MULTI-STREAM SESSION — CHECKPOINTED MID-FLIGHT)

User-directed checkpoint stop. Four worktree streams ran (Opus
orchestrators directing Codex 5.5, Fable apex): **A** P2-013/P2-014
integrity fixes — groups 1–4 committed, 19/31 pins flipped, suite
423/10/12 in-worktree, corpus validates clean under the tightened
validator; **B** 2K NVIDIA fixture-first — wire protocol v1 +
worker/transport/client landed (438 tests, zero shared-file edits, all
pins PROVISIONAL pending live hardware); **C** Stage 3.0.1 mlx-lm
prompt-cache spike — **DONE, verdict `replay_supported`** (fresh-process
token-identical resume; cache size matches kv-size prediction to
+0.018%) pending one lead re-verification command; **D** DOC-007
docs/framing — DONE + lead-reviewed, merges after A with one
reconciliation pass. Slice 2O (workload program) landed on main
(`aa665e1`). ALL FOUR STREAM BRANCHES PUSHED; every stream ledger ends
with a `*-CHECKPOINT` entry naming its exact resume action.

**RESTART HERE:** read
`docs/run_reports/2026-07-07-checkpoint-multistream-session.md` (stream
table, merge order A→D→C→B, process learnings — esp. the SUBAGENT WAKE
GAP), then resume streams from their ledgers. After all merges +
integration review: the quiet-machine 2M campaign (P2-006).

## Session History (pointers only — run reports own the narrative)

Per the C-009 meta-review consensus, RUN_STATE no longer stacks
previous-run narratives. Recent sessions, newest first:

- 2026-07-07 PM checkpoint (multi-stream, C-008/C-009 + consensus):
  `docs/run_reports/2026-07-07-checkpoint-multistream-session.md`
- 2026-07-07 whole-project design council (C-007):
  `docs/run_reports/2026-07-07-whole-project-design-council.md`
- 2026-07-07 five-stream parallel session (C-005/C-006):
  `docs/run_reports/2026-07-07-parallel-streams-session.md`
- 2026-07-07 flagship benchmark:
  `docs/run_reports/2026-07-07-flagship-qwen35-122b.md`
- Older: see `docs/run_reports/` (dated files).

## Current Verification

- `python3 -m unittest discover -s tests` → `Ran 415 tests, OK
  (skipped=10, expected failures=31)` (as of 2026-07-07, after PRs
  #2-#7; the 31 expected failures are Stream F audit pins that flip to
  passing as P2-013 lands).
- CI: mock e2e + suite on both matrix legs.
- Latest live evidence: real n=3 MLX experiment with populated
  `aggregate` block, byte-identically re-derivable (run report
  2026-07-07-parallel-streams-session.md).

## Known Workspace State

- `main` is pushed and current (through the C-009 consensus commit).
- FOUR worktrees exist deliberately (checkpointed streams; branches all
  pushed): `../jw-p2013`, `../jw-2k`, `../jw-spike301`, `../jw-doc007`.
  Remove each only after its PR lands.
- `/tmp/jw-lead-verify/` holds disposable lead-verification artifacts.

## What Is Next

Follow `TASK_QUEUE.md` (lane-annotated); the checkpoint run report's
"How to restart" section is the authoritative sequence. In order:

1. **Resume + land the four checkpointed streams** [AGENT]: A P2-013
   groups 5–8 + P2-014 → merge; D reconciliation pass → merge; C verdict
   re-verify → merge; B U3–U5 + review pipeline → rebase → merge; then
   the cross-stream integration review. Per-stream resume points live in
   the stream ledgers (`docs/stream_logs/` on each branch). Topology per
   the C-009 consensus (lead-driven pipelines / foreground-wait
   orchestrators; heartbeat as backstop).
2. **P2-006: the 2M two-model baseline campaign** [QUIET-MAC] — after
   the merges; no-agent quiet lock per C-009 T5; corpus born under the
   fixed validator with prompt provenance (P2-014e).
3. **P2-010 → P2-012 workload program** [AGENT] per Slice 2O gates.
4. **Ed's external one-pass** [ED-EXTERNAL]: calendar, device access,
   borrow window, wall meter, backup destination (P0-003).
5. **Small task queued by C-009**: patch `~/.local/bin/codex-run`
   (mkdir -p out-dir; forward -C/-s on --resume; thin-output warning).

Hardware-gated (unchanged): 2K/2L (P1-006), wall meter (P1-003),
topology (P1-004), calendar mapping (P1-008).

## Open Decisions And Blockers

- Supervisor approval and scope pending (P1-001, R-001 — trigger fired
  2026-06-12, mitigation holding); gates FULL D-016 closure (a
  provisional small-model pick opened 2G on 2026-07-06).
- Real backup destination pending (P0-003; interim same-disk location
  active, R-016 mitigated-interim).
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Git author identity on this machine auto-selected as
  `Ed R <edr@Eds-MacBook-Pro.local>`. Amend future commits if a
  different identity is needed.
