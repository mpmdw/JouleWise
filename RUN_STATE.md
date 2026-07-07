# JouleWise Run State

Last updated: 2026-07-06

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
7. Call out any dirty working-tree state that should not be accidentally
   committed.

## Current Project Status

Phase 1 is in its final stretch (remaining gates need external/user
input; per-item status in `docs/phase_1/phase_1_exit_checklist.md` —
the MLX-runtime row closed 2026-07-06). Phase 2 now has its **first real
adapter**: Slice 2G (MLX runtime) is complete with a succeeded
real-generation bundle on the M3 Max (real MLX + mock telemetry
pairing; TTFT 81.5 ms, 265.8 tok/s). 2A-2F, 2J, 2N remain complete.
Still gated: 2H (privileged powermetrics sample, P1-002), 2I (2H),
2K/2L (P1-006), 2M (2I). D-016 has a provisional small-model pick
(Qwen2.5-1.5B-Instruct-4bit, local mirror) that opens 2G only; full
closure needs P1-001. P0-002 backup protocol closed with an INTERIM
same-disk destination (follow-up P0-003). The Stage 4.6 related-work
draft (P3-001) is done. Suite: 230 tests.

## What The Latest Run Did (2026-07-06, autonomous build-out)

Full detail: `docs/run_reports/2026-07-06-autonomous-buildout.md`.
User-directed maximal build-out on a NEW machine (M3 Max, 128 GB; fresh
clone at `~/code/JouleWise`), with implementation delegated to the local
Codex CLI through the new repo bridge (`scripts/codex-bridge`, commit
`10a570d`) and reviewed/live-verified by Claude. Landed, in order:
**P0-002** (`5b12332`) backup script + real restore test, interim
destination `~/JouleWise-backup`, R-016 updated; **P3-001** (`c31ffac`)
related-work draft — 11 sources, verified citations, positioning claims
honestly narrowed (claims 1-2) with claim 3 standing; **D-016
provisional** (decision log) Qwen2.5-1.5B-Instruct-4bit @ `8b40312`
mirrored to `~/jw_models/`, KV row verified (28,672 B/token);
**Slice 2G** (`3eb0acd`) MLX runtime adapter per the pinned guide, suite
226→230 green under both system python3 and the `[mac]` venv
(`transformers<5.13` pin — 5.13 breaks mlx_lm import), live smoke
succeeded + `--strict` + `reduce` green. The first live smoke failed
usefully and exposed a mock-telemetry × SystemClock composition edge
(samples stamped outside the D-026 window) — worked around at 20 Hz in
the bring-up config, hardening queued as **P2-008**.

## Previous Run (2026-07-06, status-review intake + fixes)

Full detail: `docs/run_reports/2026-07-06-status-review-fixes.md`. An
independent project status review
(`docs/run_reports/2026-07-06-project-status-review.md`) was examined at
the user's direction; all three findings were verified by reproduction
and fixed same-session, in the reviewer's suggested order: **P1**
(`0803d1f`) — `BundleReader.events()` centrally validates `timestamp_s`
as a finite number, so corrupt event timestamps become structured FAILED
summaries / `invalid:` problems instead of raw
`ValueError`/`TypeError`; **P3** (same commit) — new
`joulewise.bundle.write_raw_artifact(context, name, data)` gives
adapters the validated no-overwrite raw-evidence write (mock converted;
contract updated); **P2** (`80c3d49`, **D-030**) — new
`validate-bundle --strict` requires succeeded bundles to be
reducer-consumable and their summary to equal a fresh re-reduction
(both reviewer reproductions pinned as tests; Phase 4 inclusion rule and
Phase 5 Stage 5.2 now specify `--strict`). Suite 216 -> 226, green.
The review's remaining precondition for real measurement — P0-002
backup protocol — stays open at the top of the queue.

## Previous Run (2026-07-06, Slice 2N implementation)

Full detail: `docs/run_reports/2026-07-06-slice-2n-pre-hardware-hardening.md`.
Preflight per playbook M0 plus a user-requested filesystem health check
(repo at canonical path, git synced, suite green; deleted the verified
stale `~/Desktop/CapstoneRivoire` remnant; `~/jw_pending_edits/` was
already gone). Then executed Mission M1 end-to-end: all nine Slice 2N
items landed as the three planned commits — the adapter seam
(2N.1 RunContext + raw evidence, 2N.2 sampling-window markers, D-026),
the read layer (2N.8 shared `BundleReader` per D-025, 2N.4 rail
alignment contract D-027, 2N.7 report/reducer alignment, 2N.6 `reduce`
verb + D-028), and schema + metrics (2N.5 nullable-optionals schema +
pinned config hashes D-029, 2N.3 observed-token fallback with
`token_count_source`, 2N.9 v0.2 compatibility note — one flag for
Stage 3.1: put the composite event node tag inside event `metadata`,
not a sixth key). Suite grew 169 -> 216, green after every item; the
exit-checklist 2N row is closed; queue P2-007 done. All commits pushed
same-session at the user's request; CI green (run #11).

## Previous Run (2026-07-06, architecture review intake)

Full detail: `docs/run_reports/2026-07-06-architecture-review-intake.md`.
An external architecture review (Codex) was triaged; agreed items landed
as design decisions and plan updates: **D-024** (adapters receive an
immutable `RunContext` — settles 2N.1's open seam question), **D-025**
(shared `BundleReader` for reducer/report/validate/aggregate — new item
2N.8; 2N.7 must build on it), a new cross-cutting contract
`docs/contracts/node_worker_protocol.md` (remote execution shape, pinned
during 2K, reused by 2L + Phase 3), item 2N.9 (design-only v0.2
compatibility check), and a sqlite-before-DuckDB clause in Stage 4.1.
Operational note: agent sessions should be launched from
`~/code/CapstoneRivoire/Capstone`; the old Desktop path holds only a
harness-recreated `.claude/settings.local.json` and can be deleted after
relaunch. A same-day second review pass confirmed the intake and drove
three housekeeping fixes (D-024/D-025 "pending" wording, R-017 marked
mitigated, 2N three-commit grouping in playbook M1).

## Older Run (2026-07-05, docs/meta-layer cleanup + repo move)

Full detail: `docs/run_reports/2026-07-05-docs-meta-cleanup.md`. Summary:

- External audit (code review + planning review) on return from the
  break; suite verified green (169) before any changes.
- D-023: per-item status consolidated into the exit checklists; plan
  headers now point there; `phase_2_plan.md` vs hardware-guide
  duplication cut to a what/how split.
- Drift fixed: phase 1 plan step statuses, stale 2026-06-10 auth-session
  references everywhere, D-019→D-022 range, 2M gate wording (Mac-only
  floor allowed), `PROJECT_STATUS.md` stale test count.
- New: Slice 2N (pre-hardware hardening, from the code review's seam
  findings); Phase 4 Stage 4.6 (background/related-work draft —
  previously unowned); R-016 (corpus backup); R-017 (iCloud lock);
  milestones heartbeat rule; queue tasks P0-002, P2-007, P3-001.
- The iCloud EPERM lock recurred mid-run (R-017); the user moved the
  repo off iCloud in response (P0-001, done — see below).
- Advisor doc (`PROJECT_STATUS.md`) refreshed for 2026-07-05.

## Current Verification

```bash
python3 -m unittest discover -s tests           # 230 tests, OK (skipped=10)
.venv/bin/python -m unittest discover -s tests  # 230 tests, OK (skipped=10)
```

Result (2026-07-06, after Slice 2G): green under BOTH the system
python3 (CI-equivalent, no mlx) and the `[mac]` venv. Also verified:
mock e2e; the 2G live bundle (`example-mac-mlx-mock-telemetry`)
succeeded with `validate-bundle --strict` green and `reduce`
re-derivation green; backup restore test green.

## Known Workspace State

- **New machine (2026-07-06):** MacBook Pro M3 Max / 128 GB. Canonical
  path here: `~/code/JouleWise` (fresh clone; the previous machine's
  `~/code/CapstoneRivoire/Capstone` notes are historical).
- Remote: `https://github.com/mpmdw/JouleWise`; branch `main`. FIVE
  local commits NOT pushed (awaiting user): `10a570d` Codex bridge,
  `5b12332` backup script, `c31ffac` related-work draft, `3eb0acd`
  Slice 2G, plus the bookkeeping commit for this session.
- Git author auto-selected as `Ed R <edr@Eds-MacBook-Pro.local>` on this
  machine (previous machine used `Edr <edr@Edrs-MacBook-Air.local>`).
- Machine-local, intentionally uncommitted (`.gitignore`): `.venv/`
  (mlx_lm 0.31.3 / mlx 0.31.2 / transformers 5.12.1), `.claude/`
  (Codex agent/command/skill files), `.codex-bridge/` logs.
- Model mirror (R-014): `~/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit`
  (839 MB, rev `8b40312`). Interim backup destination: `~/JouleWise-backup`.
- Codex CLI 0.142.5 at `/Applications/Codex.app/Contents/Resources/codex`,
  symlinked to `~/.local/bin/codex`.

## What Is Next

Follow `TASK_QUEUE.md`; execute via the mission guides in
`docs/agent_playbook.md` (start every session with its Mission M0). In
order:

1. P1-002 (user): privileged powermetrics sample + D-004 sudoers — the
   ONLY blocker for 2H (playbook M6), then 2I (playbook M7) = first
   real energy numbers. The MLX half of P1-002 closed 2026-07-06.
2. P1-001 (user): supervisor scope → full D-016 closure (playbook M4
   remainder: mid model, CUDA load evidence, GGUF paths).
3. P0-003 (user): real external/cloud backup destination.
4. Implementable now without user input: P2-008 (mock telemetry ×
   SystemClock hardening), Phase 3 Stage 3.0.0 (kv-size helper), and
   Stage 3.0.1 (mlx-lm prompt-cache spike — its inputs, 2G + chosen
   small model, are satisfied).

Done 2026-07-06 (this session): P0-002 interim, P3-001, D-016
provisional, Slice 2G with live real-generation evidence, Codex bridge.

## Open Decisions And Blockers

- Supervisor approval and scope pending (P1-001, R-001 — trigger fired
  2026-06-12, mitigation holding); gates FULL D-016 closure (a
  provisional small-model pick opened 2G on 2026-07-06).
- Mac privileged powermetrics sample pending (P1-002, R-002; the sole
  gate for 2H; auth session to be rescheduled).
- Real backup destination pending (P0-003; interim same-disk location
  active, R-016 mitigated-interim).
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Git author identity on this machine auto-selected as
  `Ed R <edr@Eds-MacBook-Pro.local>`. Amend future commits if a
  different identity is needed.
