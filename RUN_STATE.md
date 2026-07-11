# JouleWise Run State

Last updated: 2026-07-11 (P2-041 vetted rebuild complete and uncommitted on
`impl/p2041-vetted`; focused 398 OK/1 skipped, canonical 1062 OK/13 skipped.
Earlier: PR #49's main-side P2-038 rail-only CI flake
root-caused to the fake powermetrics child's SIGTERM/right-edge-bracket race;
fixture-only fix is uncommitted, exact test 100/100 green, focused 5 OK,
canonical 1041 OK/13 skipped. Earlier: P2-040 reducer-version review blocker fixed
without commit on `impl/p2040-remainder`: reducer 0.3.1 plus frozen-0.3.0
absence projection; focused tests green, canonical rerun exposed one unrelated
pre-existing node-worker timing failure. Earlier:
C-027 whole-project council review with
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

Status: **ACTIVE (2026-07-10 late, C-028 checkpoint #3 — fresh-thread
handoff; the prior thread's context filled).** This card is the ONLY
resume authority. Read it plus `docs/reviews/2026-07-10-hardening-adjudication.md`
before anything else.

**MERGED to main (C-028 total): PRs #41-#48.** #46 P2-042 analysis
manifest (review + fix round), #47 P2-040 remainder (reducer 0.3.1 +
ADDED_SINCE_0_3_0 discipline), #48 P2-038 production uncertainty
(metrology review: unknown-contamination fail-open closed; cross-
contract idle_drift_guard). Plus same-day: P0-003 CLOSED (iCloud
Drive backup, restore test strict-valid + byte-identical), D-060
RATIFIED by Ed, hardening proposal adjudicated (9 new queue rows
P2-043..P2-048/CI-002/REPRO-002/RPT-002; record + conflicts table in
docs/reviews/2026-07-10-hardening-adjudication.md).

**CHECKPOINT #4 (2026-07-11, Ed-directed pause; supersedes the item
list below where they conflict). State at pause:**

- MERGED today: PR #49 (NV-GATE-2 code-now, 1b0f1f6) and PR #54
  (P2-041 vetted rebuild + full review stack + fix rounds, 69a3393).
  Both historic flake classes dead; NV-5 localhost lead gate CLOSED.
- OPEN PRs, all lead-gated, HELD for the integration-review window:
  #50 P2-046A, #51 CI-002 (acceptance CI 4/4 green), #52 REPRO-002,
  #53 RPT-002 (all seven sources primary-verified), #55 P2-044
  (idle ESS per adjudicated design docs/reviews/2026-07-11-p2044-
  design-consult.md; lead gates + corpus 6/6 done; metrology review
  lens IN FLIGHT at pause).
- impl/p2037 worktree: contrast/claim engine implemented by an ultra
  session that exited transport-OK with NO REPORT (RED-round
  signature) — work itself lead-verified green (focused 89 OK,
  canonical OK); an independent xhigh AUDIT (implemented-vs-spec map,
  scope audit of cli.py/claims_lint.py hunks, fail-open hunts) was IN
  FLIGHT at pause; its report lands in the session scratchpad
  (sol-p2037-audit.md). UNCOMMITTED — do not discard. Acceptance
  gated on P2-044 (#55) landing + audit dispositions.
- Scope-restraint + adapter infrastructure (global, outside repo):
  claude-codex-report/v1 adopted (~/.claude/skills/codex-delegation/
  ADAPTER.md); codex-run-v3 + codex-usage INSTALLED (~/.local/bin);
  fail-on-diff scope backstop build IN FLIGHT at pause
  (sol-scope-backstop.md); AGENTS.md now carries delegated-session
  WRITE_SCOPE precedence + NEEDS_RULING early-return (9ca89cc,
  31b3f5e). Consult records: docs/reviews/2026-07-11-scope-restraint-
  consult.md, -p2044-design-consult.md, -p2041-red-tranche-triage.md,
  -hardening-row-scheduling-scout.md.
- Usage state: one ultra ≈ 11 xhigh sessions (35.3M vs ~3.1M tokens);
  5h window was 26% remaining, resets ~11:03Z; usage-pressure mode
  ACTIVE per Ed — after this pause, NO ultra launches (exception:
  P2-037 resume if its audit demands completion, Ed-authorized);
  prefer high/xhigh consultancy + spec design in break mode. Check
  `codex-usage <manifests>` before any ultra.
- RESUME ORDER: (1) consume the three in-flight reports
  (sol-p2044-review.md, sol-p2037-audit.md, sol-scope-backstop.md;
  scratchpad path in D-064 manifests; iCloud backup at
  JouleWise-agent-logs/2026-07-11/); (2) P2-044 review dispositions →
  merge #55; (3) P2-037 audit dispositions → fix/complete → PR; (4)
  P2-043 + P2-045 launch decisions (scout: they needed p2041 landed —
  satisfied — plus P2-037 CLI/vocabulary frozen); (5) DOC-008 kernel
  (LAST), cross-stream integration review over final main, merge held
  PRs #50-#53/#55 per its verdicts; (6) C-028 BOOKKEEPING ARC (item 5
  below, unchanged; D-064 must also ratify manifest v3 + adapter;
  P2-044 10s-bandwidth methodology freeze flagged for Ed veto) → THEN
  clear this card.

**Original item list (item 1 DONE; superseded where checkpoint #4
says otherwise):**

1. DONE 2026-07-11: PR #49 MERGED to main (1b0f1f6) after the full
   gate stack: lead conflict resolution (456772a), Sol merge review +
   P2-005-row repair (13f6c9e), the py3.14 CI red root-caused as a
   PRE-EXISTING main-side fixture SIGTERM race and fixed fixture-only
   (10e0ad2; flake test 0/30 fails lead-run), NV-5 localhost lead gate
   CLOSED (3/3 OK socket-capable), canonical 1041 OK (skipped=12)
   unpiped, CI green both versions, Ed-approved SHA-guarded merge.
   Both historic flake classes (fake-nvidia-smi idle deadline; P2-038
   rail-only right-edge bracket) are now dead on main.
   IN FLIGHT (Ed-directed fan-out): impl/p2041-vetted ULTRA
   composition per the triage recipe, and a NEW impl/p2037 stream
   (contrast/claim engine, ULTRA, from the banked adjudicated spec +
   frozen rulings; interface assumptions vs p2041 flagged for
   integration review). Original item (superseded): PR #49 had REAL
   code conflicts vs post-#48
   main: joulewise/cli.py + reduce.py + schemas.py + tests/test_cli_run.py
   (both sides extended MeasurementQuality, ADDED_SINCE_0_3_0, and the
   0.3.x dispatch) + the usual state-file unions. A clean merge was
   deliberately NOT rushed at checkpoint. Resolve with care (union of
   BOTH quality fields runtime_cleanup_ok + remote_cleanup_failed in
   schema, ADDED_SINCE, and dispatch tests; suite must stay green
   UNPIPED), or delegate to a Sol session in ../JouleWise-wt/nvgate2
   with this exact contract. Then CI → merge #49. NOTE: #49 contains
   the ROOT-CAUSE fix for the historic fake-nvidia-smi flake (worker
   idle deadline now starts at sampler readiness) — after it merges,
   that flake class is dead everywhere.
   ADDENDUM (2026-07-11): conflicts RESOLVED lead-side (456772a +
   P2-005-row repair 13f6c9e after a Sol merge-review catch; suite
   1041 OK unpiped). CI then went RED ONCE on py3.14 at 13f6c9e:
   FAIL test_rail_only_sentinels_withhold_drift_but_leave_gross_eligible
   (tests/test_p2038_production_path.py, MAIN-side PR #48 content,
   AssertionError eligible=False) — NOT the localhost subprocess test
   (an earlier same-day report misattributed it). Same code was green
   on 3.11 and on both versions at 456772a ⇒ nondeterministic,
   timing-suspect, possibly pre-existing on main independent of #49.
   Root-cause + deterministic fix required BEFORE merging #49; do not
   merge on a rerun-green alone, and any fix must preserve fail-closed
   gate semantics (metrology adjudication).
2. impl/p2041-vetted — VETTED REBUILD COMPLETE, UNCOMMITTED (2026-07-11):
   manually composed from the requested post-#49 `1b0f1f6` base using the
   triage recipe; no raw WIP diff or generated site files were applied.
   HEAD itself is the #49 merge; item 1's pre-merge narrative is inherited
   anchor text and is superseded, but later main bookkeeping was not imported.
   `claim_readiness`, per-physical-session exemption, adjudicated v2/top-up
   shape, P2-038/P2-040/P2-042 behavior, and both post-#49 cleanup fields are
   retained. Final focused 398 OK/1 skipped; canonical 1062 OK/13 skipped;
   mechanical gates clean. Report:
   `docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`. Lead owns final diff
   review and pathspec commit, including explicit adjudication of the three
   assertion-only pure-B exceptions and the frozen stored-field mapper gap.
3. DOC-008 kernel (LAST, per adjudication): refresh at final
   integrated head + NOT-AUTHORITATIVE header, targeted review, PR.
4. Cross-stream integration review (Sol) over final main: interaction
   defects only, esp. P2-038 evidence x P2-040 gates x P2-041
   readiness x P2-042 manifest x NV-GATE quality fields.
5. C-028 BOOKKEEPING ARC: consume scratchpad/bookkeeping-drafts.md;
   D-064 decision entry (adjudicated H4: tracked per-session JSONL,
   one row per invocation; a partial exists at
   scratchpad/c028-invocations.jsonl); C-028 council entry (this arc
   had ~35 Sol sessions incl. 7-lens review, 40-ruling adjudication,
   per-stream review stacks, 2 capacity-killed+resumed sessions, the
   hardening adjudication, bridge v2); run report; queue-row updates
   (P2-040 FULLY done, P2-038/P2-042 done pending integration review,
   RETRO-001 done pending verification-head advance at next site
   regen+diff); RPT-001+P2-039 exit-checklist rows per DOC-009 rule;
   consistency sweep; site regen + deploy; THEN clear this card.

**Environment/tooling facts for the fresh thread:**
- codex = gpt-5.6-sol (Ed's term); reviews at --effort xhigh (config
  default), BIG implementations at --effort ultra (spawn_agent-capable).
  Invoke via ~/.local/bin/codex-run-v2 (adds -m/--effort, capacity
  retry-with-resume, --manifest D-064 rows; 37/37 tests) — v1 exists
  but v2 is now proven across ~10 runs.
- Worktrees under ../JouleWise-wt/ — do NOT remove until merged.
- Git identity: repo-local user.name/email were set (hostname changed);
  worktree commits work.
- LESSON (bit three times): never pipe the suite when its exit code
  gates a push — run unpiped to a file, check, then push separately.
- Sol sandboxes cannot bind localhost sockets and cannot write shared
  worktree git metadata: socket tests are lead-run 3x; merges are
  lead-recreated (sessions may pre-union content).
- The fake-nvidia-smi flake fires near-deterministically under Sol
  load on THIS machine but never in CI — until #49 merges, judge that
  one failure accordingly.

**Ed-decision list remaining:** two-model floor economics; full-corpus
CI commitment; renderer (P1-008); REPRO pack publication acts.

## Superseded stop card (CP-5)## Superseded stop card (CP-5)

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

**P2-041 VETTED REBUILD COMPLETE in `impl/p2041-vetted` (2026-07-11;
uncommitted for lead pathspec review).** The 4 clean-A files were copied
blob-exact and the 15 mixed files were manually re-derived from post-#49 main.
The landing keeps `claim_readiness`, a per-physical-session first-run
exemption, the adjudicated campaign-verdict-v2/top-up surface, authoritative
P2-042 manifest validation, P2-038 shakedown behavior, and both
`runtime_cleanup_ok` and `remote_cleanup_failed` under reducer 0.4.0. Focused
398 OK/1 skipped; canonical 1062 OK/13 skipped. Report:
`docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`.

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

- 2026-07-11 P2-041 vetted rebuild (uncommitted; lead pathspec review and
  commit pending): `docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`

- 2026-07-10 NV-GATE-2 idle-capture regression debug/fix (uncommitted;
  localhost re-verification remains lead-gated):
  `docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md`
- 2026-07-10 NV-GATE-2 CODE-NOW implementation (NV-1/NV-3/NV-4/NV-5;
  live promotion evidence still gated):
  `docs/run_reports/2026-07-10-nvgate2-codenow.md`
- 2026-07-10 NV-GATE-2 accepted-findings fix round (uncommitted; merge
  metadata recreation and lead gate pending):
  `docs/run_reports/2026-07-10-nvgate2-fix-round.md`
- 2026-07-10 P2-038 accepted-findings fix round (all FIX-1..FIX-6 green;
  content-merged `origin/main`, Git merge metadata sandbox-blocked):
  `docs/run_reports/2026-07-10-p2038-fix-round.md`
- 2026-07-10 P2-038 production uncertainty software path (live quiet-machine
  closure still open):
  `docs/run_reports/2026-07-10-p2038-production-uncertainty.md`
- 2026-07-10 P2-040 reducer-version compatibility review fix (uncommitted):
  `docs/run_reports/2026-07-10-p2040-versioning-fix.md`
- 2026-07-10 P2-040 remainder implementation (uncommitted, pending lead
  pathspec commit/corpus gate):
  `docs/run_reports/2026-07-10-p2040-remainder.md`
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

- P2-041 vetted rebuild: baseline canonical `Ran 1041 tests in 67.995s`,
  `OK (skipped=13)`; final focused recipe modules `Ran 398 tests in 54.964s`,
  `OK (skipped=1)`; final canonical `Ran 1062 tests in 76.436s`, `OK
  (skipped=13)`; `git diff --check` and the dead-private-helper search clean.
  The retained corpus and localhost socket gates skipped loudly; no live or
  quiet-Mac validation was claimed. Report:
  `docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`.

- PR #49 P2-038 rail-only flake: pre-fix exact-test loop failed 4/100;
  retained failure emitted `cadence_ratio_unrecorded` plus
  `interpolation_bound_unrecorded` because the final trace sample preceded the
  stop marker. Archived `origin/main` reproduced on iteration 6. The
  fixture-only terminal-sample handshake fix passed the exact test 100/100,
  focused module `Ran 5 tests in 30.480s`, `OK`, and canonical suite
  `Ran 1041 tests in 66.509s`, `OK (skipped=13)`. Report:
  `docs/run_reports/2026-07-10-pr49-p2038-flake-root-cause.md`.
- NV-GATE-2 idle-capture regression fix: historic fake-sampler plus new
  delayed-readiness regression passed together in 3 consecutive fresh
  processes; canonical suite `Ran 1023 tests in 35.164s`, `OK (skipped=13)`;
  `py_compile` and `git diff --check` clean. The exact localhost contract was
  attempted 3 times but loudly skipped before worker execution because this
  sandbox denied socket bind; lead socket-capable 3x rerun remains required.
  Report: `docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md`.
- NV-GATE-2 accepted-findings fix round: focused node-worker/subprocess,
  controller, reducer, strict-dispatch, and schema surface `Ran 229 tests in
  4.995s`, `OK (skipped=2)`; the historic fake-sampler test passed three
  consecutive fresh-process runs; canonical suite `Ran 1022 tests in 34.406s`,
  `OK (skipped=13)`; targeted `py_compile` and `git diff --check` clean. The
  0.3.1 dispatch came from `origin/impl/p2040-remainder` because post-main did
  not contain it. Report: `docs/run_reports/2026-07-10-nvgate2-fix-round.md`.
- NV-GATE-2 CODE-NOW worktree: baseline `Ran 910 tests in 32.549s`,
  `OK (skipped=12)`; final canonical suite `Ran 922 tests in 33.551s`,
  `OK (skipped=13)`; focused NV-1/NV-3/NV-4/NV-5 surface `Ran 232 tests
  in 6.085s`, `OK (skipped=2)`; `git diff --check` and targeted
  `py_compile` clean. The added skip is loud and specific: this managed
  sandbox denied localhost socket bind for NV-5. No live NVIDIA evidence or
  de-provisionalization was claimed.
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
- P2-040 reducer-version review fix: focused strict/reducer run
  `Ran 84 tests in 1.908s`, `OK`; extended strict/reducer/schema run
  `Ran 104 tests in 1.997s`, `OK (skipped=1)`. Canonical run reached
  `Ran 926 tests in 33.732s`, `FAILED (failures=1, skipped=12)` solely at
  pre-existing `test_telemetry_measure_idle_with_fake_nvidia_smi`; isolated
  reruns reproduce its 0.2-second fake-process timing failure. All
  reducer/version tests pass; no out-of-scope node-worker change was made.
- P2-040 remainder worktree: pre-change baseline `Ran 910 tests in 34.584s`,
  `OK (skipped=12)`; post-change focused affected modules `Ran 256 tests in
  3.744s`, `OK (skipped=1)`; canonical `Ran 924 tests in 32.812s`, `OK
  (skipped=12)`; compileall and `git diff --check` clean. The unchanged
  six-corpus test produced its required loud skip because `runs/` is absent;
  lead 6/6 strict read-only rerun remains the landing gate.
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
- P2-040 reducer-version review fix: focused strict/reducer run
  `Ran 84 tests in 1.908s`, `OK`; extended strict/reducer/schema run
  `Ran 104 tests in 1.997s`, `OK (skipped=1)`. Canonical run reached
  `Ran 926 tests in 33.732s`, `FAILED (failures=1, skipped=12)` solely at
  pre-existing `test_telemetry_measure_idle_with_fake_nvidia_smi`; isolated
  reruns reproduce its 0.2-second fake-process timing failure. All
  reducer/version tests pass; no out-of-scope node-worker change was made.
- P2-040 remainder worktree: pre-change baseline `Ran 910 tests in 34.584s`,
  `OK (skipped=12)`; post-change focused affected modules `Ran 256 tests in
  3.744s`, `OK (skipped=1)`; canonical `Ran 924 tests in 32.812s`, `OK
  (skipped=12)`; compileall and `git diff --check` clean. The unchanged
  six-corpus test produced its required loud skip because `runs/` is absent;
  lead 6/6 strict read-only rerun remains the landing gate.
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

- Worktree `/Users/edr/code/JouleWise-wt/p2041-vetted` on
  `impl/p2041-vetted` is intentionally dirty only with the uncommitted P2-041
  vetted rebuild and its bookkeeping/report. It remains anchored at the
  user-specified post-#49 `1b0f1f6`; `origin/main` advanced during the run and
  was not merged. No `docs/site/*` file was regenerated. Lead owns final diff
  review and pathspec commit; do not commit or discard the tree wholesale.

- Worktree `/Users/edr/code/JouleWise-wt/nvgate2` on
  `impl/nvgate2-codenow` has the idle-readiness fix, regression test, and
  handoff bookkeeping COMMITTED (cd6e2cb) and the lead-resolved merge of
  post-#48 `origin/main` (union of remote_cleanup_failed +
  runtime_cleanup_ok in schema/ADDED_SINCE/dispatch tests). The pre-existing
  main-side P2-038 rail-only flake has an uncommitted fixture-only SIGTERM
  handshake fix plus handoff report/state updates. The localhost 3x lead gate
  PASSED (lead-run 2026-07-11: 3/3 OK socket-capable; flake test 0/30
  failures; canonical 1041 OK skipped=12 unpiped, socket test exercised).
- `impl/p2038` is intentionally dirty with the uncommitted P2-038 software,
  accepted-findings fixes, tests, contracts, config, run reports, and the clean
  three-way content merge of `origin/main`. The lead owns pathspec review and
  the real Git merge/commit; the sandbox could not write `ORIG_HEAD`/merge
  metadata in the external worktree admin directory. No retained run bundle
  was modified.
- Worktree `/Users/edr/code/JouleWise-wt/p2040rem` on
  `impl/p2040-remainder` contains the committed remainder implementation and
  is intentionally dirty only with the uncommitted reducer-version review
  fix, tests, D-030 amendment, and handoff bookkeeping. Do not commit or
  discard these changes wholesale.
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

Lead-review the uncommitted P2-041 vetted rebuild against its triage recipe,
explicitly adjudicate the three post-#49 assertion-only pure-B exceptions and
the frozen stored-field mapper gap, then commit only approved pathspecs. The
cross-stream P2-038/P2-040/P2-041/P2-042/NV integration review remains the next
stop-card action after landing. `TASK_QUEUE.md` remains the ordering authority.

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
