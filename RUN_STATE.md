# JouleWise Run State

Last updated: 2026-07-09 (C-027 whole-project council review with
gpt-5.6-sol: claim-surface corrections in README/PROJECT_STATUS/this
file, 14 new queue rows plus NV-GATE-2 additions to P2-005, D-060 proposed +
D-061..D-063 accepted; record in
`docs/reviews/2026-07-09-c027-whole-project-review.md`. Earlier same
day: Codex MCP bridge hardening; P2-034/C-026, C-025 wave 2, C-024
wave 1, C-023 rigor review, C-022 CP-5 clearance; suite 877)

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

Status: **ACTIVE (2026-07-10, C-028 checkpoint #2 — Ed away).** This
card is the resume authority. The C-028 session adjudicated all ten
C-027 specs (docs/specs/c027/ADJUDICATION.md — 40 rulings, 2-round Sol
advisory), then landed the integration through per-tranche review
stacks.

**MERGED to main this session:** PR #41 (spec wave incl. ADJUDICATION),
PR #42 (docs tranche: governance addenda + per-invocation
recoverability audit + AP/SPLIT amendments + env locks), PR #43
(P2-040 tranche + version dispatch + NV-2 cooldown fix; lead gates:
corpus 6/6 strict, mock e2e, suites green), PR #44 (RPT-001 report
skeleton + gated vertical slice; lead re-ran the full build), PR #45
(P2-039 floor calculator, validator hardened after a BLOCKED review).
RETRO-001 ran (2 SHOULD-FIX, both fixed in #43); Current Verification
may advance past 36d5641 after the NEXT session's fresh site
regen+diff (RETRO-1's remaining condition).

**OPEN work, exact states:**

- PR #46 DRAFT (impl/p2042 frozen analysis manifest): implementation
  complete, main merged in (one manual-merge splice defect was
  introduced and fixed — 8a1c9f-era note in the PR), suite green.
  NEEDS: targeted Sol review (spec: engine trio §A + adjudication) →
  fix round if any → un-draft → CI → merge.
- impl/p2041 (pushed, NO PR): campaign verdict split + H3 fail-closed
  campaign-cooldown gate, complete per its run report in the branch;
  intentionally behind main. NEEDS: merge main in (run_campaign.py
  will conflict with #46's sidecar exclusion — land #46 first),
  targeted review, PR, gates, merge.
- impl/p2040-remainder (pushed, NO PR): FIX-7a/7b/FIX-8 complete; lead
  corpus gate + full suite ALREADY GREEN. NEEDS: targeted review
  (cheap), PR, CI, merge.
- impl/nvgate2-codenow: session died at capacity twice; a codex-run-v2
  RESUME with --retries 3 was IN FLIGHT at checkpoint (out-file
  scratchpad/nvgate2-impl2.md). If it completed: commit by pathspec in
  ../JouleWise-wt/nvgate2, review, PR. If it died with the session:
  the worktree holds partial state — resume again via
  `codex-run-v2 <out> --resume ...` in that worktree.
- impl/p2038 (production uncertainty evidence, stacked on the merged
  P2-040): Sol session was IN FLIGHT at checkpoint (out-file
  scratchpad/p2038-impl.md). Same recovery pattern as nvgate2.
  P2-038 stays a HARD pre-Window-A gate.
- DOC-008 kernel: adjudicated to land LAST — refresh the kernel at the
  final integrated head + NOT-AUTHORITATIVE header, targeted review,
  PR. Not started (deliberately).
- Cross-stream integration review (Sol) over merged main AFTER the
  remaining branches land; then C-028 BOOKKEEPING: consume
  scratchpad/bookkeeping-drafts.md (16 KB: D-064 draft, C-028 council
  entry draft, run-report skeleton, clearance template) — lead owns
  final wording; per-invocation JSONL per D-064 (a start exists at
  scratchpad/c028-invocations.jsonl via codex-run-v2 --manifest);
  queue-row status updates; consistency sweep; site regen + deploy;
  THEN clear this stop card.

**Session scratchpad** (survives on disk):
`/private/tmp/claude-501/-Users-edr-code-JouleWise/e48cf22e-209a-4355-bb28-9b6a37636b34/scratchpad/`
— all review packets (rev-*.md, p2040-lens*.md, retro001.md), fix
reports, the advisory thread record (resume-plan.md; MCP thread id in
ADJUDICATION.md), bookkeeping drafts.

**Tooling delta:** `~/.local/bin/codex-run-v2` installed (37/37 tests;
per-call -m/--effort, capacity-aware retry-with-resume, D-064
--manifest/--role/--parent rows). v1 untouched; promote v2 to default
after a few more clean runs. Ed's division-of-labor directive (Sol =
implementer + advisor, Fable = architect/director) is in effect and
recorded in memory.

**Ed-decision list** (updated 2026-07-10: P0-003 DONE — iCloud Drive +
restore test; D-060 RATIFIED): remaining — two-model floor economics;
full-corpus CI; renderer (P1-008); REPRO pack publication.

## Superseded stop card (CP-5)

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

**RPT-001 targeted review fix round COMPLETE in worktree (2026-07-10;
awaiting lead pathspec commit).** FIX-1..FIX-9 are implemented: Phase-4
claims lint/projection, adjudicated 1P5B identity and regenerated artifacts,
full/offline atomic build with hash verification, real pipeline regressions,
D-058 T1 scope, expanded claim-language tripwires, boundary-honest prose,
LF byte stability, and evidence-bootstrap gating. Real-corpus regeneration
used `/Users/edr/code/JouleWise/runs`; focused 37 OK and canonical 890 OK
(skipped=10). Report: `docs/run_reports/2026-07-10-rpt001-fix-round.md`.

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
Window A is GO in the CP-5 software sense — C-027 additionally
conditions execution on P0-003 backup, P2-038, P2-039, and
P2-015-SMOKE.** Seven PRs merged
(#22..#28): D-033 strict legacy-bypass close, envelope-gate script,
campaign-runner prompt-hash check, bundle-pack tooling, tokenizer
identity widening + manifest regen, capture hardening (output token IDs,
fail-closed sampler pin, model weight hashing, hash-domain
realized-vs-manifest closure), advisor status site + suite_next draft
specs (D-051). Suite 822 OK. Ed's four-part answer + Window-A go/no-go:
`docs/run_reports/2026-07-09-cp5-resume.md`.

**P2-038 SOFTWARE SIDE COMPLETE on `impl/p2038` (2026-07-10; uncommitted
for lead pathspec review); LIVE CLOSURE REMAINS OPEN.** Current-era real
powermetrics runs now derive and record paired-clock anchor/phase evidence,
the interim pre/post idle envelope, and a separate idle-drift guard handoff;
the post sentinel is outside the measured window. A production-shaped real
adapter/child-process path passes the P2-029/P2-040 request gate with no
synthetic metadata and exercises all three required fail-closed reasons.
Campaign shakedown mode now enforces strict → reduce → strict → assertion →
backup. True MLX + `/usr/bin/powermetrics` execution and approved backup remain
lead-owned `[QUIET-MAC]` work. Report:
`docs/run_reports/2026-07-10-p2038-production-uncertainty.md`.

**RESTART HERE (next agent) — this is the ONLY next-action block; the
queue owns ordering (C-027):**
1. Read `docs/reviews/2026-07-09-c027-whole-project-review.md` (latest —
   whole-project council review, adjudicated follow-ups) and
   `docs/run_reports/2026-07-09-cp5-resume.md` (Window-A go/no-go).
2. Lane state after C-027:
   - [ED-EXTERNAL] P0-003 external backup destination is a HARD GATE
     before any new irreplaceable Window-A evidence is retained; plus
     P1-008 rubric/calendar (provisional-contract fallback per proposed
     D-060).
   - [AGENT]: the C-027 correctness rows, in queue order — finish lead review
     and landing of P2-038's completed software diff, then P2-039 (frozen floor artifact +
     guard factor), then RPT-001 (report skeleton + vertical slice),
     P2-042 (frozen analysis manifest), P2-041 (campaign verdict
     split), and only then P2-037 (contrast/claim engine, which
     consumes the manifest — required before any P2-006
     interpretation). P2-022/P2-023 remain BLOCKED post-2M per D-041 —
     do not start them.
   - [QUIET-MAC] Window A (C-019 shakedown → P2-015-SMOKE → P2-015
     floors → P2-006) proceeds only after P2-040 + P2-038 + P2-039
     land and the P0-003 backup gate is satisfied (P2-040 is
     pre-Window-A: strict must reject zero-length windows before any
     collection).
3. Rotation (D-056), uncertainty gates (D-057), and the campaign packs
   are live for Window-A execution once the above gates clear.

## Session History (pointers only — run reports own the narrative)

- 2026-07-10 P2-038 accepted-findings fix round (all FIX-1..FIX-6 green;
  content-merged `origin/main`, Git merge metadata sandbox-blocked):
  `docs/run_reports/2026-07-10-p2038-fix-round.md`
- 2026-07-10 P2-038 production uncertainty software path (live quiet-machine
  closure still open):
  `docs/run_reports/2026-07-10-p2038-production-uncertainty.md`
- 2026-07-10 P2-040 / RETRO-001 fix round (committed on c027-int-p2040
  after lead review): `docs/run_reports/2026-07-10-p2040-fix-round.md`
- 2026-07-09 C-027 whole-project council review (7 gpt-5.6-sol lenses +
  counterreview + independent final examiner):
  `docs/reviews/2026-07-09-c027-whole-project-review.md` (compact run
  report: `docs/run_reports/2026-07-09-c027-council-review.md`)
- 2026-07-09 Claude Code → Codex MCP bridge hardening and live smoke:
  `docs/run_reports/2026-07-09-claude-codex-mcp-bridge.md`
- 2026-07-09 P2-034 broad campaign packs (C-026; PR #39):
  `docs/run_reports/2026-07-09-p2034-broad-packs.md`
- 2026-07-09 spec-fleshing wave 2, ultracode (C-025; PRs #33..#38;
  D-056..D-059): `docs/run_reports/2026-07-09-spec-fleshing-wave2.md`
- 2026-07-09 spec-fleshing wave 1 (C-024; PRs #29..#32; D-052..D-055):
  `docs/run_reports/2026-07-09-spec-fleshing-wave1.md`
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

- P2-038 accepted-findings fix round: all FIX-1..FIX-6 complete; focused
  `Ran 70 tests in 41.211s`, `OK`; canonical `Ran 992 tests in 68.140s`,
  `OK (skipped=12)`; `git diff --check` clean. The real-child rail-only path
  now withholds drift on unknown contamination while gross remains eligible;
  P2-039's pending guard validator accepts the emitted block; backup launch
  failure, extreme-sentinel exclusion, child invocation, and literal phase
  constants are regression-tested. The absent worktree `runs/` corpus produced
  the loud six-bundle acceptance-gate skip. Git merge metadata remains absent
  because the managed sandbox cannot write the external worktree admin dir;
  the exact clean three-way `origin/main` content snapshot is applied.
- P2-042 emitter branch `impl/p2042` (lead-committed base; draft PR #46;
  targeted-review fix round complete in the worktree, no fix-round commit):
  FIX-1 fail-closed typed identity/linkage validation, FIX-2 semantic
  `run_id` derivation, and FIX-3 raw-byte AP hashing/LF config emission are
  implemented. Focused manifest/generator/campaign checks: `Ran 82 tests in
  12.317s, OK`; final canonical suite: `Ran 989 tests in 33.405s, OK
  (skipped=12)`. Review regressions cover `run_id=[]`, one malformed identity
  at each manifest object layer, a fully rehashed coherent rename, and a CRLF
  AP fixture. Report:
  `docs/run_reports/2026-07-10-p2042-analysis-manifest.md`.
- P2-040 / RETRO-001 fix-round worktree: canonical suite `Ran 908 tests in
  32.723s`, `OK (skipped=11)`; focused 211 tests OK; claims lint exit 0 with
  no errors; `git diff --check` clean. The absent `runs/` corpus produced the
  required loud six-bundle acceptance-gate skip; the lead corpus gate then
  PASSED (6/6 strict via corpus symlink), plus mock e2e run+strict+reduce
  and the post-merge full suite (OK, skipped=12).
- Claude Code 2.1.205 approved the project `codex` MCP server; Codex CLI
  0.144.0 protocol handshake exposed `codex` + `codex-reply` with the
  expected full-session controls. A real Claude → Codex read-only call
  read `AGENTS.md`/`RUN_STATE.md`, and the same thread continued through
  `codex-reply` (`JOULEWISE_CODEX_MCP_OK` /
  `JOULEWISE_CODEX_REPLY_OK`). `scripts/check-codex-mcp.mjs` passes;
  canonical suite `Ran 877 tests, OK (skipped=10)`.
- Last code-bearing verified head c095c83 (post PR #39; note: 36d5641
  later changed `scripts/build_site.py` on main without a recorded
  verification — flagged by C-027, covered by RETRO-001): suite `OK (skipped=10)` and
  repo lint errors=0, lead-run; pack lint errors=0 warnings=0.
- Prior: main after wave-2 integration fixes: `python3 -m unittest discover -s
  tests` → `Ran 877 tests, OK (skipped=10)`, lead-run; repo lint
  errors=0; CI green on all six PR heads (#33..#38); combined-ref
  pre-merge suite check green; live rotated mock campaign strict-valid
  with order provenance (lead-validated); mock e2e emits uncertainty
  fields per D-057.
- Prior: series head f75134d (post PRs #29..#32; docs-only) lead-verified;
  integration-fix commit 7156295 is also docs-only (no test surface):
  `python3 -m unittest discover -s tests` → `Ran 822 tests, OK
  (skipped=10)`, lead-run; CI green on all four PR heads (py3.11+py3.14);
  integration reviewer independently re-ran the suite and recomputed the
  detection-floor campaign arithmetic.
- Prior verification (7666652, post PRs #22..#28): `Ran 822 tests, OK
  (skipped=10)`, lead-run.
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

- `impl/p2038` is intentionally dirty with the uncommitted P2-038 software,
  accepted-findings fixes, tests, contracts, config, run reports, and the clean
  three-way content merge of `origin/main`. The lead owns pathspec review and
  the real Git merge/commit; the sandbox could not write `ORIG_HEAD`/merge
  metadata in the external worktree admin directory. No retained run bundle
  was modified.
- `main` and `origin/main` contain the user-directed Claude Code → Codex
  bridge hardening from commit `1d7c415` (pushed direct as a bounded
  tooling change, closeout `ef34cc9`). Branch `c027-council-review`
  (PR #40) carries the C-027 review record, claim-surface corrections,
  and sweep fixes, and has merged main back in; the worktree is
  otherwise clean.
- Codex's own worktree `/Users/edr/.codex/worktrees/7fe2/JouleWise`
  still holds the ORIGINAL advisor-site commits (bf9ffc5..e6cf431);
  their content landed via PR #28 (D-051 renumber applied). Safe to
  leave or remove; do not re-land.
- `/tmp/jw-lead-verify/` and the session scratchpad hold disposable
  lead-verification artifacts (live-runs bundles are not corpus).

## What Is Next

See **RESTART HERE** above — that block and `TASK_QUEUE.md` are the only
next-action authorities. (C-027 removed the duplicated ranking that
previously lived here after it drifted stale against the queue.)

Hardware-gated (unchanged): 2K/2L (P1-006; NV-GATE-2 additions from
C-027 apply at live promotion), wall meter (P1-003), topology (P1-004),
calendar mapping (P1-008).

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
