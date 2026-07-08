# JouleWise Run State

Last updated: 2026-07-08 (resume+merge session: checkpointed streams
completed and landed under the C-009 topology)

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

**P2-013 and P2-014 are COMPLETE and MERGED (2026-07-08).** The
checkpointed multi-stream session resumed under the C-009 topology and
landed: PR #8 (all 31 audit pins fixed; strict raw-to-trace gate +
legacy-additive compare; summary/workload provenance; D-032..D-034),
PR #10 (DOC-007 docs/framing + merge-time reconciliation), PR #9
(Stage 3.0.1 verdict **`replay_supported`**, lead-re-verified live —
Phase 3's central technical risk retired on current hardware), plus
D-035/D-036 (the ratified spike promotions). **PR #11 (2K NVIDIA
fixture-first stack, 545 tests, integration-reviewed, all pins
PROVISIONAL) is OPEN awaiting Ed's merge.** Suite on main: 462 OK
(skipped=10, ZERO expected failures); all 6 real corpus bundles pass
`--strict` read-only. The 2M campaign (P2-006) is fully unblocked and
is the next machine-state-compatible task.

**RESTART HERE:** read
`docs/run_reports/2026-07-07-resume-merge-session.md` (product
outcomes, review-pipeline yield table, restart steps). Short version:
Ed merges PR #11 → remove `../jw-2k` → quiet-machine 2M campaign
(P2-006) under the C-009 T5 no-agent lock.

## Session History (pointers only — run reports own the narrative)

Per the C-009 meta-review consensus, RUN_STATE no longer stacks
previous-run narratives. Recent sessions, newest first:

- 2026-07-07/08 resume+merge (C-009 topology first full run; PRs
  #8/#9/#10 merged, #11 open):
  `docs/run_reports/2026-07-07-resume-merge-session.md`
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

- Merged main: `python3 -m unittest discover -s tests` → `Ran 462
  tests, OK (skipped=10)` — ZERO expected failures (as of 2026-07-08,
  after PRs #8/#9/#10).
- `validate-bundle --strict` green over all 6 real corpus bundles,
  read-only, unrewritten (incl. the new raw-to-trace gate).
- CI: mock e2e + suite on both matrix legs, green on every PR head.
- PR #11 branch: 545 OK incl. fake-e2e strict validation of a
  provenance-carrying synthetic 2K bundle.

## Known Workspace State

- `main` is pushed and current (through this session's bookkeeping).
- ONE worktree remains deliberately: `../jw-2k` (PR #11 open). Remove
  after it lands. (`../jw-p2013`, `../jw-doc007`, `../jw-spike301`
  removed this session — branches merged.)
- `/tmp/jw-lead-verify/` holds disposable lead-verification artifacts.

## What Is Next

Follow `TASK_QUEUE.md` (lane-annotated). In order:

1. **Ed merges PR #11** [ED-EXTERNAL] (2K fixture-first; rebased,
   integration-reviewed, merges clean). Then remove `../jw-2k`.
2. **P2-006: the 2M two-model baseline campaign** [QUIET-MAC] — fully
   unblocked; no-agent quiet lock per C-009 T5 (stop all fleets/Codex
   load first); corpus born under the fixed validator with prompt
   provenance.
3. **P2-010 → P2-012 workload program** [AGENT] per Slice 2O gates
   (D-034).
4. **Ed's external one-pass** [ED-EXTERNAL]: calendar, device access,
   borrow window, wall meter, backup destination (P0-003).
5. **3.0.2 llama.cpp spike** [AGENT after R-003 approval]: reuses the
   3.0.1 harness shape (D-035/D-036) + its two deferred hardening fixes.

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
