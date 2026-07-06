# Phase 5 Plan: Presentation, Repository Polish, And Final Submission

Status: tracked in `docs/phase_5/phase_5_exit_checklist.md` (per-item
status authority, per D-023). Gated by the Phase 5 readiness section of
`docs/phase_4/phase_4_exit_checklist.md`. Calendar anchors live in
`docs/milestones.md` (dates TBD until P1-008 closes).

Companion docs:

- Exit gates: `docs/phase_5/phase_5_exit_checklist.md`

## Goal

Package the project so that three audiences succeed without help: a new
*user* runs a benchmark from the README; a new *developer* adds a backend
from the extension guide; the *committee* can trace every claim to data.
"Polish" here means verified usability, not cosmetics - every deliverable
below has an executable acceptance test.

## Stages

### Stage 5.0: README Quickstart (verified)

Objective: a fresh-clone quickstart that works.

Actions: rewrite README with two paths - (a) zero-dependency mock path:
clone -> `python3 -m joulewise run configs/examples/mock_local.json` ->
`report` -> open HTML, under five minutes; (b) Mac path with `[mac]` extra
and the D-004 sudoers note. State Python floor, extras table (D-009), and
the bundle-anatomy crash course (what's in `runs/<id>/`).

Evidence: the quickstart executed literally, command-by-command, in a fresh
clone in a temp directory (and by the CI mock step, which mirrors path a);
transcript in a run report.

Acceptance: a follow-the-text-only execution succeeds with no improvisation;
any deviation found is fixed in the README, not in the transcript.

Fallback: none needed.

### Stage 5.1: Backend-Extension Guide (verified by construction)

Objective: `docs/extending.md` - how to add runtime/telemetry/transport
adapters.

Design notes: the guide is written by *doing* - add a small real adapter
(`file_replay` telemetry: replays a recorded power-trace CSV as if live;
genuinely useful for demos and reducer debugging) and write the guide as
its faithful walkthrough: protocol to satisfy, registry entry, structured
failures, rail manifest (D-018), lazy-import pattern (D-009), tests to
copy. The tutorial adapter ships in the package with tests, so the guide
can never drift from a working example.

Evidence: the adapter + tests merged; guide cross-checked section-by-
section against the shipped code; ideally a fresh agent session executes
the guide to add a second trivial adapter and reports friction.

Acceptance: guide and shipped example agree exactly; the friction report
(if run) produced doc fixes, not workarounds.

Fallback: skip the fresh-session test if time-bound; the by-construction
property still holds.

### Stage 5.2: Sample Bundle Publication

Objective: real example data in the repo.

Actions: select one mock bundle and one real Mac bundle (small model, short
workload); apply the size policy - committed bundles <= ~2 MB each, with
oversized raw artifacts (e.g., big plists) truncated *by documented script*
(`scripts/trim_bundle.py`) that records what was removed in the bundle's
metadata; place under `examples/runs/`; wire `validate-bundle` over them
into CI.

Evidence: CI validating the samples on every push; README links them.

Acceptance: a reader can open a real bundle without running anything; CI
proves the samples stay schema-valid as schemas evolve.

Fallback: if no real bundle fits the size policy, publish the mock bundle
in-repo and the real bundle as a release asset, README pointing to both.

### Stage 5.3: Dataset Freeze And Release

Objective: the immutable artifact behind the report.

Actions: freeze the corpus (Phase 4 gate already requires it); write
`scripts/make_release_manifest.py` producing SHA-256 manifests for all
bundles + the analysis dataset; tag `v1.0-data`; verify figures regenerate
from the tagged tree + corpus; attach the corpus archive (or record its
storage location if too large for release assets - decision recorded with
size evidence).

Evidence: tag exists; manifest committed; regeneration-from-tag performed
once and logged.

Acceptance: report figures are reproducible from tag + manifest-verified
data, demonstrated not asserted.

Fallback: none needed.

### Stage 5.4: Colloquium Slides

Objective: the talk, built on frozen figures.

Design notes - narrative skeleton (adjust to the venue's time limit when
P1-008 fixes it): problem (energy is the constraint nobody measures well at
the edge) -> JouleWise design (config/adapters/bundles - one slide on
auditability) -> methodology highlights (idle subtraction, boundaries,
uncertainty - the credibility slide) -> homogeneous findings (F1/F3) ->
split story (F4/F5 crossover) -> energy-latency trade-off (F6) ->
applicability findings (incl. Hailo verdict and any portability findings -
negative results presented as findings) -> limitations -> future work.
Every number on a slide carries its claims-index ID in the speaker notes.

Actions: outline -> draft -> rehearse twice with timing -> revise; dry-run
with supervisor if schedulable.

Evidence: deck in repo (`docs/phase_5/colloquium/`); rehearsal timing notes.

Acceptance: deck fits the slot with >=2 min margin; every figure slide
regenerates from the pipeline; speaker notes carry claim IDs.

Fallback: none needed beyond ordinary iteration.

### Stage 5.5: Final Report Assembly

Objective: the written deliverable.

Actions: assemble from existing audited parts - background/related work
(4.6 draft), methodology (Phase 1 doc, updated), harness design (plan
docs distilled), results (4.4 draft), limitations (4.4), reproducibility
appendix (quickstart + regeneration commands + manifest), applicability
findings; final pass walking the claims index against the text (every
quantitative sentence has its row; every row's status caveat is honored).

Evidence: report source in repo; claims-index final-pass note.

Acceptance: supervisor-submission-ready by the P1-008 date with margin;
the index pass found zero untraceable claims (or they were fixed).

Fallback: scope prose, never data integrity - shorter honest report beats
longer unaudited one.

### Stage 5.6: Repository Final Pass

Objective: leave the repo as the durable artifact.

Actions: docstring/naming pass on public surfaces; prune dead docs
(superseded drafts marked or removed); LICENSE decision (user input -
academic context may have institutional norms; flagged in milestones);
final `RUN_STATE.md` written as a project-complete handoff (what exists,
how to regenerate everything, what future work would start with).

Evidence: final run report; clean `git status`; CI green on the final
commit.

Acceptance: the Phase 5 exit checklist is fully green.

Fallback: none needed.

## Exit

Governed by `docs/phase_5/phase_5_exit_checklist.md`. The capstone's
acceptance criteria from `AGENT_PLAN.md` map: README quickstart (5.0),
extension guide (5.1), sample bundle (5.2), validated dataset (5.3),
slides (5.4), report (5.5).
