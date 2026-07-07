# JouleWise Run State

Last updated: 2026-07-07 (parallel-streams session)

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
stands. Suite: 369 tests. Stream F (repo-wide Codex test audit) in
flight — its PR + a final integration review are the only open threads.

## What The Latest Run Did (2026-07-07, FIVE-STREAM PARALLEL SESSION)

Six worktree streams (Fable orchestrators driving Codex 5.5-high per the
new operation-loop skill), two councils, ~6-7M Codex tokens of
implementation/review offloaded. Merged: PRs #2 (kv-size), #3 (2M
campaign tooling), #4 (P2-009 rich telemetry), #5 (P2-008 mock
hardening), #6 (P2-011/D-014 uncertainty) + INT-001/INT-002 integration
fixes. Lead-verified on real hardware: n=3 experiment aggregate
99.19 ± 1.36 mJ/output-token re-derived byte-identically; idle gate
caught real contamination; 1 Hz mock regression proof. Councils: C-005
(hardware-tiered research agenda, jw_mixed_v1 suite → P2-012), C-006
(orchestration trace v2, process meta-review; global skills
deduplicated; operation-loop installed). Suite 254 → 369. Full detail:
`docs/run_reports/2026-07-07-parallel-streams-session.md`; process
trace: council log C-006.

## Previous Run (2026-07-07, FLAGSHIP MODEL BENCHMARKED)

Qwen3.5-122B-A10B-4bit (65 GB mirror, rev `e9c67b0`) selected by
web-verified research, mirrored, and benchmarked through the unmodified
harness: 3/3 strict-valid reps, ~304 J / 512 tokens (583 mJ/token,
46 tok/s, TTFT ~270 ms, CV 0.3%). First Q4 data point: mJ/token scales
~linearly with ACTIVE params (6.7×) while decode power is nearly flat.
Full detail: `docs/run_reports/2026-07-07-flagship-qwen35-122b.md`.
Config `mac_mlx_qwen35_122b.json` (hash-pinned). Corpus backed up.

## Previous Run (2026-07-07, merge + research councils + flagship model)

PR #1 (the 11-commit vertical-slice series) merged to main after C-002
review; CI green on both matrix legs. Research councils C-003/C-004 ran
(see `docs/council_log.md`): Q4-Q6 promoted, `docs/research_question_bank.md`
created, new queue items P2-009/P2-010/P2-011. User-directed flagship
model selected by web-verified research: `mlx-community/Qwen3.5-122B-A10B-4bit`
(69.6 GB, 122B MoE/10B active, rev `e9c67b0`) — mirror download in
progress; the flagship benchmark run on it is the immediate next action.
Standing loop addition: push green commits promptly; refresh high-level
docs each session (steps 7-8 above).

## Previous Run (2026-07-06 night, Slice 2I — FIRST REAL ENERGY NUMBERS)

Full detail: `docs/run_reports/2026-07-06-slice-2i-first-real-energy.md`.
The user installed the D-004 sudoers line (P1-002 now fully complete).
First flagship attempt failed instructively (powermetrics ~1 s startup
latency vs a 0.32 s measured window → 0-byte capture); fix (`b4d4173`,
Codex from parent diagnosis): start_sampling readiness wait (first
parseable plist doc, 15 s bound), `-b 0` unbuffered, flagship workload
64→512 tokens at 10 Hz. Then **3/3 reps succeeded, all --strict valid**:
gross 46.6-48.0 J (CV 1.4%), 77-88 mJ/output-token, prefill 0.03 J vs
decode ~47 J, TTFT 92.8-94.9 ms, 257 tok/s, 8.8-8.9 Hz observed (in
band). Methodological finding: rep 1's idle baseline (3.5 W vs 0.2-0.3 W)
shows post-model-load settling contamination → Stage 4.0 protocol note.
Corpus backed up per R-016. **Slices 2H and 2I are COMPLETE; the Mac
vertical slice (P2-003) is done; 2M and Phase 3 Stage 3.0 are unblocked.**
Suite: 254.

## Previous Run (2026-07-06 evening, P1-002 + Slice 2H)

Full detail: `docs/run_reports/2026-07-06-slice-2h-powermetrics.md`. The
user captured the privileged powermetrics sample (P1-002 → framing +
field names pinned in the Phase 1 checklist; fixture committed). Slice
2H then landed (`26dca41`) through a review/counterreview loop: Codex
implemented; a 22-agent adversarial review confirmed 10 findings (1
blocker: measure_idle fabricated a 0.0 W baseline and delayed failure
past warmup); Codex counterreviewed, accepted all 10, and contributed
the AdapterFailure design (structured exception → controller maps the
true FailureReason). Suite 251 green both interpreters. Live-verified:
mlx+powermetrics fails at idle_baseline with permission_denied, no
warmup, no fabricated baseline. User re-prioritized: P1-001 and P0-003
→ meta/deferred. Remaining before first real energy numbers: the D-004
sudoers line, then one `mac_mlx_local.json` run (= 2H smoke + 2I).

## Previous Run (2026-07-06, autonomous build-out)

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

- `python3 -m unittest discover -s tests` → `Ran 369 tests, OK
  (skipped=10)` (as of 2026-07-07, after PRs #2-#6 + integration fixes
  INT-001/INT-002).
- CI: mock e2e + suite on both matrix legs.
- Latest live evidence: real n=3 MLX experiment with populated
  `aggregate` block, byte-identically re-derivable (run report
  2026-07-07-parallel-streams-session.md).

## Known Workspace State

- `main` is pushed and current: PRs #2-#6 merged + INT-001/INT-002 +
  bookkeeping commits; no unpushed local state.
- SIX worktrees exist (`../jw-uncertainty`, `../jw-campaign`,
  `../jw-mock-hardening`, `../jw-rich-telemetry`, `../jw-kv-size`,
  `../jw-test-audit`) — five have merged branches awaiting
  `git worktree remove` (archive `.codex-bridge/` logs to the R-016
  backup area first, per C-006); `jw-test-audit` (stream F) is STILL IN
  FLIGHT — do not remove it.
- `/tmp/jw-lead-verify/` holds disposable lead-verification artifacts.

## What Is Next

Follow `TASK_QUEUE.md`; execute via the mission guides in
`docs/agent_playbook.md` (start every session with its Mission M0). In
order:

1. **Land Stream F** (repo-wide Codex test audit, worktree
   `jw-test-audit`, branch `stream/test-audit`) — findings re-check
   against merged main was in flight at session close; then the final
   post-merge integration review over the complete composite.
2. **P2-006: the 2M two-model baseline campaign** (queue rank 1, fully
   tooled). REQUIRES A QUIET MACHINE — no agent fleet, no Codex load
   (the idle gate will flag contamination). Command sequence in PR #3;
   run under `.venv` (`.venv/bin/python3 scripts/run_campaign.py ...`).
   Then `docs/phase_2/baseline_results.md` consuming the D-014
   aggregates.
3. **P2-010 scored workload suite** (`affine_mod_ladder_v1`), then
   **P2-012 `jw_mixed_v1`** per the C-005 spec in the question bank.
4. Phase 3 Stage 3.0.1 (mlx-lm prompt-cache spike) — 3.0.0 (kv-size)
   done, PR #2.
5. Small follow-ups queued from stream reports: `aggregate` CLI verb,
   methodology-doc amendment (manifest-level aggregate + t-table floor
   policy), idle-gate threshold corpus, `dvfm_states` slimming option.
6. Worktree cleanup after F lands (`git worktree remove` × 6; archive
   `.codex-bridge` logs to the R-016 backup area first, per the C-006
   preservation rule).

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
