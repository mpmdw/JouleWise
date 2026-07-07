# Run Report — 2026-07-07: Whole-Project Design Council (C-007)

## What this session was

User-directed: "examine this repo/project and have Fable and Codex go
back and forth about the design, architecture, high-level docs, and
planning; Fable is final judge but the council should all have input."
No implementation — a design/planning council only.

## Planning reflection

Intake per M0 (run state, queue, git log, audit doc). "This task"
initially read as queue-top work: rank 1 (P2-006) requires a quiet
machine, which a council session precludes; rank 2 (P2-013) is the
design-bearing task — the P2-013 sub-council started there before Ed
clarified the scope was the whole project, and both tracks ran in
parallel.

## Shape

Council skill shape B (ideation/strategy). Fable wrote position briefs
FIRST (9 P2-013 positions, 7 project positions), then 7 parallel
read-only Codex gpt-5.5 lenses argued against them (P2-013: design /
examiner / planning; project: architect / strategist / project-examiner
/ docs), Fable adjudicated a synthesis, a fresh Codex attack session
reviewed the synthesis (verdict: ratify-with-changes), Fable ratified
with all six required changes. Mechanics: `codex-run` backgrounded
sessions, one out-file each, per the codex-delegation skill; lens
outputs live in the session scratchpad (ephemeral); everything that
survived is recorded in council log C-007.

## Outcome

Full record with deliberation traces, per-layer catch attribution, and
dissents: `docs/council_log.md` C-007. Headlines:

- **P2-013 fix design settled** (resolutions 1–9), including the
  council's biggest catch: `--strict` never re-derives
  `power_trace.csv` from `raw/powermetrics.plist` — a raw-to-trace
  strict sub-check joins the P2-013 stream, and D-030's "raw artifacts"
  wording gets corrected.
- **Queue restructured:** P2-013 (rank 1, scope grown) → P2-014 (new:
  pre-2M contract amendments) → P2-006 2M campaign; machine-state lanes
  [QUIET-MAC]/[AGENT]/[ED-EXTERNAL] adopted; Do-Not-Do-Yet Phase-3
  wording fixed (desk spikes open, data collection gated); DOC-007
  docs + framing package queued.
- **Project framing:** two claim tracks adopted — auditable local
  measurement (harness + Apple-Silicon characterization) is the
  guaranteed capstone; split inference remains the validating study.
- **Detection floor** confirmed unowned → becomes an
  implementation-backed Phase 4 acceptance gate (spec queued in
  DOC-007).
- **Architecture:** five seams confirmed to break for Phase 3
  composites — deliberately deferred to Stage 3.1; the cheap pre-2M
  protections are exactly P2-014.

## What changed on disk

- `docs/council_log.md`: C-007 entry + index rows for C-005/C-006
  (index drift found and fixed).
- `TASK_QUEUE.md`: lanes section, ranks 1–13 restructure, P2-014 +
  DOC-007 added, Do-Not-Do-Yet wording fix.
- `RUN_STATE.md`: stale Stream F in-flight narrative cleared (PR #7 had
  landed), latest-run section for this council, next-steps rewritten.
- This report + the sweep's count fixes (README, PROJECT_STATUS,
  playbook M0, phase-2 checklist). No code changes; the consistency
  sweep ran the suite for ground truth: `Ran 415 tests, OK (skipped=10,
  expected failures=31)`.

## Commands / verification

Corpus fact-checks used by the council (lead-side): all 6 real bundles
carry `metadata.config_sha256`; all have finite headline energy fields;
raw plists present; 7 `test_audit_*` files. Attack round spot-checked
six synthesis code claims against source — all confirmed, one wording
overclaim (D-030) corrected.

## Workspace state

Clean tree before this session's doc edits. The consistency sweep's
ground-truth check found `../jw-test-audit` already removed (Stream F
landed as PR #7) while RUN_STATE still claimed it existed — fixed, along
with six stale 369-test counts across live docs (real count: 415 / 10
skipped / 31 expected failures). Scratchpad lens files are
session-ephemeral by design.

## Next agent should

Run the P2-013 stream per C-007 resolutions 1–9 (queue rank 1): Codex-led,
one worktree, 7 invariant-shaped commit groups, P2-014 riding along;
post-landing gate = 415 tests / 0 expected failures + `--strict` green
over the 6-bundle corpus without rewriting it.

## Decisions / risks

No decision-log entries written this session by design: D-011/D-027/
D-030 amendments and the `phase_energy_j`/provenance entries land WITH
the P2-013/P2-014 implementation (the council pinned their content;
C-007 is the interim record). Machine-state lanes recorded in
TASK_QUEUE + C-007. No risk-register changes (explicitly considered:
the council's findings change no risk posture — R-016's open backup
destination was re-flagged to Ed instead).
