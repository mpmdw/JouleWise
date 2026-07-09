# JouleWise Run State

Last updated: 2026-07-09 (scientific-rigor review C-023: verdict strong
provisional → advisor-defensible once the named all-software artifact
list lands; docs-only session. Prior same day: CP-5 CLEARED, PRs
#22..#28 merged, Window-A GO behind P2-015 design doc + C-019 shakedown;
suite 822; C-022; D-051)

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
11. Live MLX gates use the repo venv: `.venv/bin/python -m joulewise ...`
    (system python3 lacks mlx → `runtime_unavailable`).
12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
    "restart", "next", queue, and mission pointer until explicitly cleared.

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
   numbers cited in multiple places (C-002; D-023 extension).
   After any session that changed front-facing docs, REGENERATE and
   REDEPLOY the site so the public snapshot tracks the repo (C-012):
   `python3 scripts/build_site.py && python3 scripts/pack_capsule.py &&
   (cd site_capsule && npx lakebed deploy)`.
9. Call out any dirty working-tree state that should not be accidentally
   committed.

## ACTIVE_STOP_CARD

Status: **CLEARED 2026-07-09** by the CP-5 resume session. Every
clearance criterion was met: all three worktree diffs lead-gated
(envgate live-gated against the real affine mock bundle) and merged as
PRs #23/#24/#25; PR #22 merged after a fresh final-head pass; the
methodology synthesis and suite_next specs packet adjudicated (CP-6 in
the stream log); all accepted pre-campaign changes landed and merged
(PRs #26/#27/#28); both post-merge integration reviews CLEAN; queue
rank 0 closed. Full record:
`docs/run_reports/2026-07-09-cp5-resume.md`. No stop card is active.

## Current Project Status

**Suite BUILD session COMPLETE and MERGED (2026-07-08; C-017;
D-044..D-047).** The workload suite is now CODE, not contracts: P2-010a
generic substrate (PR #17: suite.py, run_suite protocol, mock+MLX
execution, BundleReader suite validation, reducer suite_metrics, strict
rollup provenance), P2-010b affine core + smoke manifest (PR #18,
promoted via #20 after a base-retarget slip), P2-012 phase-1 + P2-020
generator engine (PR #19: gensuite, six categories + five ids-native
sentinels). All 37 research-doc amendments adjudicated first (recorded
dispositions). Live-verified on real MLX at three code states; three
live-only defects caught and fixed at the lead gate. Post-merge
integration review: zero cross-stream defects.

**CP-5 RESUMED AND CLEARED (2026-07-09): pre-campaign review COMPLETE;
Window A is GO behind two queued campaign-time steps.** Seven PRs merged
(#22..#28): D-033 strict legacy-bypass close, envelope-gate script,
campaign-runner prompt-hash check, bundle-pack tooling, tokenizer
identity widening + manifest regen, capture hardening (output token IDs,
fail-closed sampler pin, model weight hashing, hash-domain
realized-vs-manifest closure), advisor status site + suite_next draft
specs (D-051). Suite 822 OK. Ed's four-part answer + Window-A go/no-go:
`docs/run_reports/2026-07-09-cp5-resume.md`.

**RESTART HERE (next agent):**
1. Read `docs/run_reports/2026-07-09-cp5-resume.md` for this session's
   record and the Window-A go/no-go checklist.
2. Next work per `TASK_QUEUE.md`: P2-015 design-doc prep [AGENT], then
   quiet Window A (P2-015 floors + C-019 shakedown first, then P2-006).

## Session History (pointers only — run reports own the narrative)

- 2026-07-09 scientific-rigor review of suite/benchmark/question bank
  (C-023; review-only; full record in
  `docs/reviews/2026-07-09-scientific-rigor-review.md`):
  `docs/run_reports/2026-07-09-scientific-rigor-review.md`
- 2026-07-09 CP-5 resume: pre-campaign review completed, stop card
  cleared, PRs #22..#28 merged, Window-A GO
  (C-022): `docs/run_reports/2026-07-09-cp5-resume.md`
- 2026-07-09 meta-process stop-card + codex-bridge audit cleanup
  (D-050; CP-5 preserved untouched):
  `docs/run_reports/2026-07-09-meta-process-stop-card-cleanup.md`
- 2026-07-09 advisor status-site live-depth refresh (D-051/C-021;
  subordinate to the then-active CP-5 stop card):
  `docs/run_reports/2026-07-09-advisor-status-site.md`
- 2026-07-08 suite build (C-017; adjudication + PRs #17/#18/#20/#19;
  D-044..D-047): `docs/run_reports/2026-07-08-suite-build.md`
- 2026-07-08 suite-science + expansion (C-014/C-015; PRs #14/#15/#16;
  D-038..D-042): `docs/run_reports/2026-07-08-suite-science-expansion.md`
- 2026-07-08 Lakebed deploy (C-013):
  `docs/run_reports/2026-07-08-lakebed-deploy.md`
- 2026-07-08 site observatory (PR #13):
  `docs/run_reports/2026-07-08-site-observatory.md`
- 2026-07-08 critique second-pass + councils+critique (C-011 → PR #12):
  `docs/run_reports/2026-07-08-councils-critique-session.md`
- 2026-07-07/08 resume+merge (C-009 first full run; PRs #8..#11):
  `docs/run_reports/2026-07-07-resume-merge-session.md`
- Older: see `docs/run_reports/` (dated files).

## Current Verification

- Final merged main (7666652, post PRs #22..#28): `python3 -m unittest
  discover -s tests` → `Ran 822 tests, OK (skipped=10)`, lead-run.
- Live lead gates this session (real MLX, Qwen2.5-1.5B via `.venv`, mock
  telemetry): single-prompt + TWO full 48-item jw_mixed suite runs
  (pre-merge old manifests, then final merged main with the REGENERATED
  manifests) — all strict-valid; 48/48 hash-domain closures on the
  real tokenizer; output token ids, model artifact hash, pinned sampler,
  and package versions verified present in the bundles.
- Envelope gate live: honest `envelope_failed[E1]` on the mock affine
  bundle; refusals for wrong-profile/malformed/mixed inputs; exit codes
  0/2/3.
- Bundle pack live: pack → verify(0) → tamper → verify(2).
- Manifest regen: byte-identical double-regen; all realized counts 512;
  new effective shas 855be4e5 (mixed) / 0316283d (sentinel).
- CI green on every merged head (PR #27's first merge-ref run failed on
  a cross-branch fixture interaction; fixed test-side, then green).
- Post-merge integration reviews (both waves): CLEAN, incl. an
  end-to-end mock campaign → strict → envelope-gate → pack → verify flow
  and a D-033 legacy-identity spoof probe that failed closed.
- `validate-bundle --strict` green over all 6 real corpus bundles under
  the new era rule (PR #22 live gate: 6/6 valid, tamper fails named).

## Known Workspace State

- `main` pushed and current through this session's bookkeeping. No open
  PRs; no stream worktrees remain (all seven merged and removed).
- Codex's own worktree `/Users/edr/.codex/worktrees/7fe2/JouleWise`
  still holds the ORIGINAL advisor-site commits (bf9ffc5..e6cf431);
  their content landed via PR #28 (D-051 renumber applied). Safe to
  leave or remove; do not re-land.
- `/tmp/jw-lead-verify/` and the session scratchpad hold disposable
  lead-verification artifacts (live-runs bundles are not corpus).

## What Is Next

Follow `TASK_QUEUE.md` (lane-annotated). In order:

1. **P2-015 design-doc prep** [AGENT]: cell list, n, UCB floor rule,
   Window-B-start revalidation cell (accepted synthesis condition; the
   only remaining pre-window agent work). Before drafting, read C-023's
   recommended scope expansion (combined floor + calibration runbooks +
   telemetry-trust hierarchy + error budget) in
   `docs/reviews/2026-07-09-scientific-rigor-review.md` — adoption is
   the next planning session's call.
2. **Quiet Window A** [QUIET-MAC]: C-019 shakedown first, then P2-015
   floors, then P2-006 2M baselines; AP-6 sentinel pilot may ride the
   window tail (manifests are ready).
3. **Ed's external one-pass** [ED-EXTERNAL]: calendar, device access,
   borrow window, wall meter, backup destination (P0-003); plus P2-027
   external re-reduction party selection.
4. **3.0.2 llama.cpp spike** [AGENT after R-003 approval].

Hardware-gated (unchanged): 2K/2L (P1-006), wall meter (P1-003),
topology (P1-004), calendar mapping (P1-008).

## Open Decisions And Blockers

- Supervisor approval and scope pending (P1-001, R-001 — mitigation
  holding); gates FULL D-016 closure.
- Real backup destination pending (P0-003; interim same-disk active).
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Git author identity on this machine auto-selected as
  `Ed R <edr@Eds-MacBook-Pro.local>`. Amend future commits if a
  different identity is needed.
