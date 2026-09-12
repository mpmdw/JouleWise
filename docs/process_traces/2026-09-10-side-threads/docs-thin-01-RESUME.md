# DOCS-THIN-01 — resume note (durable pause, 2026-09-10 ~23:0x PDT)

Side thread run by the Opus 5 lieutenant under magistrate Fable, on Ed's ask:
"reviewing the entire project from top to bottom and investigating redundancies
in documentation... there are way too many documents, I think, that are
redundant in old directives. Basically, clean things up and thin things out to
just the necessary data. Maybe make a separate legacy folder if you must keep
some things."

## Phase reached

**Phase B is COMPLETE and committed on branch `chore/2026-09-10-docs-thin`.**
Not started: the draft PR. A Fable 5.1 review seat was in flight when the
session was closed for the measurement window; its verdict was never received.

| Commit | What |
|---|---|
| `f6aed467` | 309 git renames: 309 historical files (83,121,775 bytes) into `docs/legacy/`, plus the two-line `tests/test_docs_freshness.py` scan exclusion |
| `32c6d0b3` | `docs/legacy/README.md` (the archive's front door) and six link repairs in live documents |
| this commit | seat reports, this note, the pin list |

Verified branch census against `origin/main...HEAD` at `29dbc537`: 309 renames,
7 additions, and 5 modifications (321 files changed).

Active documentation surface, `docs/` excluding `docs/legacy/`:
**3809 files / 145.8 MB -> 3504 files / 62.7 MB.** Nothing was deleted.

## Exact next step for whoever resumes

1. `cd /Users/edr/code/JouleWise-wt-docs-thin` (NEVER the canonical checkout
   while a headless magistrate session is live there).
2. Confirm the branch still applies over current `origin/main`; the archival
   moves touch no excluded path, so a rebase should be mechanical.
3. Re-run the verification (there is no pytest on this `python3`):
   `python3 scripts/gen_state.py --check`  and
   `python3 -m unittest discover -s tests -q`.
   The full-suite run was launched but its result was never captured. The
   twelve documentation-pinning modules were green: `Ran 529 tests, OK
   (skipped=74)`, and `gen_state --check` rc 0.
4. Spawn the independent read-only review seat that did not finish: check that
   nothing live was moved, that every moved-file link resolves, that no
   excluded path changed, that the tests pass when the reviewer runs them, and
   whether the thinning went far enough.
5. `git push -u origin chore/2026-09-10-docs-thin` and open a **DRAFT** PR
   titled `DOCS-THIN-01 (draft): ...`. **Never merge** — Ed and Fable decide
   what lands.

## What was archived, and the rule

The destination rule is mechanical and exception-free, which is why no
historical document had to be edited: `docs/X` -> `docs/legacy/X`, and a
repository-root file `Y.md` -> `docs/legacy/root/Y.md`. `docs/legacy/README.md`
carries the full move table and the table of what deliberately stayed put.

- 41 `docs/process_traces/` directories dated before 2026-08-15 (240 files,
  55.1 MB) — the full list is in `docs-thin-01-archived-trace-dirs.txt`, minus
  the five restored in step "findings" below
- 5 loose `process_traces/` records (retired RESUME banners, a manifest, a sweep)
- `docs/strategy/2026-08-07-paper-portfolio/` (52 files, 27.8 MB)
- `docs/advisor/`, `docs/evidence/`, and four dated loose documents under `docs/`
- root `STATUS.md`, `FREEZE-FCM01.md`, `STOPPED-FCM01.md`

## Findings worth keeping

1. **The multi-megabyte "documents" are raw session transcripts.** The top
   fourteen largest files in `docs/` were 2-4.5 MB each and are the verbatim
   stdout of past automated sessions — Codex session headers, echoed file
   diffs, 24,000 lines apiece. `DRAFT-QUANT_GATES.md` opens with
   `OpenAI Codex v0.146.1 / workdir: ... / session id: ...`. This is the
   2026-08-07 mid-write custody incident recorded in the codex-delegation
   skill. They carry audit value and were moved, never deleted, but they are
   not documents anyone reads.
2. **`docs/process/state_kernel.json` validates its pointer targets.** Moving a
   trace directory it cites makes `scripts/gen_state.py --check` exit 2. Five
   items had to be restored to their original locations after the first move
   wave: `2026-08-03-q1-remint-bytecompare`, `2026-08-03-t3-doctrine-gate`,
   `2026-08-05-cgv-f3-consult`, `2026-08-14-readiness-charter-consult`,
   `RESUME-2026-07-26.md`, plus the whole of `docs/stream_logs/` (the kernel
   names `docs/stream_logs/2026-07-08-affine-ladder.md`). Markdown links in
   excluded files are cosmetic; kernel pointers are NOT.
3. **The freshness test's glob is a silent-coverage trap.**
   `tests/test_docs_freshness.py::_decision_reference_documents` globs
   `docs/**/*.md` and skips `docs/process_traces/`. Archiving traces to
   `docs/legacy/process_traces/` would have swept historical transcripts
   INTO the scan — the suite might still pass while checking a different set of
   documents. The fix skips `docs/legacy/`: main scans 459 documents and the
   branch scans 402. The 57 dropped documents are archived `.md` files that
   were never under `process_traces/`, including 52 now in
   `docs/legacy/strategy/2026-08-07-paper-portfolio/`; no live document leaves the scan
   and no new document enters it. This is intended: archived history leaves
   the live reference scan, and Ed may veto.
4. **A linked worktree cannot run `git mv` from a sandboxed seat.** The real
   `.git` is outside the sandbox and `index.lock` gives EACCES; the Phase B
   Astra seat returned `blocked` with zero moves. The lead did the 309 renames
   at the bench and re-delegated only the prose and link work.
5. **No deletion candidate survived scrutiny.** The read-only survey found
   byte-identical pairs (capsule instruction files, font faces, duplicate
   review exhibits) but each pair has both names referenced, or the duplication
   is itself part of the audit record. Deletions: zero, by design.
6. **Overlapping status surfaces remain at the repository root** and are the
   obvious next thinning target, but they need Ed: `AGENT_PLAN.md`,
   `CLAIMS_STATUS.md`, `PROJECT_STATUS.md`, `README.md`, `WINDOW_STATUS.md`
   (whose 2026-08-24 `_v4` narrative is superseded by D-164/D-167), plus the
   excluded `RUN_STATE.md` and `TASK_QUEUE.md`. `STATUS.md` was a finished
   per-stream handoff and has been archived. The survey's recommendation:
   `RUN_STATE.md` stays THE operational entry point, and the others keep their
   distinct owners because D-023/D-063 deliberately split phase evidence, work
   selection, restart projection and the advisor summary.

## Excluded paths (never touched on this branch; verified empty in the diff)

`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/decision_log.md`, `docs/council_log.md`,
`docs/process/**`, `docs/process_traces/2026-09-10-activation-96bfeca7/**`,
`docs/process_traces/2026-09-02-hands-free-week/**`,
`docs/process_traces/2026-09-09-rehearsal-harvest/**`,
`docs/phase_2/derivation_night_runbook.md`, `configs/**`, `scripts/**`,
`paper/**` and `docs/paper/**`, `.github/**`.

Check command, which must print nothing:

    git diff --name-only origin/main | grep -E '^(RUN_STATE|TASK_QUEUE|docs/decision_log|docs/council_log|docs/process/|configs/|paper/|\.github/|docs/paper/)'

## Proposed changes to excluded files (for Ed or the magistrate — NOT applied)

- `docs/process/state_kernel.json` carries authority/evidence pointers into six
  archival locations. Repointing them through the normal generation workflow
  would let those six move to `docs/legacy/` too.
- `scripts/build_site.py`, `scripts/pack_capsule.py`, `scripts/claims_lint.py`
  hold literal documentation paths; updating them together with an approved
  move would free `docs/run_reports/`, `docs/advisor_briefs/` and
  `docs/project_critique_review.html`.
- `docs/decision_log.md` and `docs/council_log.md` cite ~34 archived trace
  directories by their old paths. Do NOT rewrite them; the destination rule in
  `docs/legacy/README.md` resolves those citations by lookup.
- `configs/campaigns/.../plan_tree.json` and `analysis_manifest_v3.json` are
  frozen before-measurement records and must keep their literal source paths;
  that is why `docs/strategy/2026-08-09-pack-freeze-plan.md` and
  `docs/process_traces/2026-08-07-plan-factory/` stayed put.

## Documentation paths pinned by `tests/` or `scripts/` (115 that exist, of 144 matched)

A literal-path pin breaks on a move. This list was the primary move-safety
filter; the full raw match set is in `docs-thin-01-test-pinned-paths.txt`.

```
docs/advisor_briefs/2026-07-17-window-a-brief.html
docs/advisor_briefs/expected.html
docs/agent_playbook.md
docs/axi-handoff.md
docs/campaign_packs
docs/campaign_packs/
docs/campaign_packs/d117_contrast_v5.md
docs/captions
docs/captions/F2.md
docs/contracts
docs/contracts/
docs/contracts/adapter_contracts.md
docs/contracts/analysis_plans.md
docs/contracts/bridge_protocol.md
docs/contracts/claims_ladder.md
docs/contracts/d078_reason_registry_amendment.md
docs/contracts/d165_dominance_closeout.md
docs/contracts/evidence_handoff.md
docs/contracts/measurement_methodology.md
docs/contracts/other_contract.md
docs/contracts/paper_comparison_placements.md
docs/contracts/paper_reported_energy.md
docs/contracts/paper_supply_custody.md
docs/contracts/powermetrics_fiducial.md
docs/contracts/quiet_guard.md
docs/contracts/receipt_histsem_verifier.md
docs/contracts/run_bundle_layout.md
docs/council_log.md
docs/decision_log.md
docs/decision_log.md D-166
docs/does_not_exist.md
docs/JouleWise_Hardening_Proposal.md
docs/milestones.md
docs/orchestration.md
docs/paper
docs/paper/
docs/paper/draft-v1.md
docs/paper/draft-v2-skeleton.md
docs/paper/example.md
docs/paper/figures/build_mechanism_figures.py
docs/paper/figures/fig1_boundary_attribution.svg
docs/paper/figures/fig3_decision_gates.svg
docs/paper/figures/fig4_edge_excursions.svg
docs/paper/figures/figA_partial_record_enclosure
docs/paper/figures/figA_partial_record_enclosure.json
docs/paper/figures/figA_partial_record_enclosure.svg
docs/paper/figures/figA6_pulse_fit.svg
docs/paper/figures/reproduce_worked_examples.py
docs/paper/figures/worked-examples.json
docs/paper/fill-rehearsal
docs/paper/fill-rehearsal/dominance-reproduced-alpha-extraction.json
docs/paper/fill-rehearsal/dominance-reproduced-alpha-floor.json
docs/paper/fill-rehearsal/dominance-reproduced-beta-extraction.json
docs/paper/fill-rehearsal/dominance-reproduced-beta-floor.json
docs/paper/fill-rehearsal/new_supplier.py
docs/paper/fill-rehearsal/select_outcome_branches.py
docs/paper/protocol/first-use-audit-ledger.md
docs/paper/protocol/prospective-comparison-protocol.md
docs/paper/results-fill-registry.md
docs/paper/round7/anchor-correction-quantified.json
docs/paper/round7/dg071-dg075-statistics.json
docs/paper/round7/excursion-decomposition.json
docs/paper/round7/excursion-decomposition.json --svg 
docs/paper/round7/retensing-plan.md
docs/paper/round7/structural-edits.md
docs/paper/round7/successor-migration-inventory.md
docs/phase_2/alpha_arm_readiness.md
docs/phase_2/beta_arm_readiness.md
docs/phase_2/detection_floor.md
docs/phase_2/gamma_arm_readiness.md
docs/phase_2/phase_2_exit_checklist.md
docs/phase_2/window_runbook.md
docs/phase_4/claims_index.md
docs/planning_reflection_protocol.md
docs/process_traces
docs/process_traces/
docs/process_traces/2026-07-15-axi-xhigh-consult/response.md
docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json
docs/process_traces/2026-07-24-diagnostic-extraction/
docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md 
docs/process_traces/2026-08-09-prefill-phase-proof/results.json
docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md
docs/process_traces/2026-08-28-live-smoke/preflight.sh
docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md
docs/process_traces/2026-08-30-prefill-margin-coldgate/
docs/process_traces/2026-08-30-prefill-margin-coldgate/ and the 
docs/process_traces/2026-08-30-t28-estate11/estate-12-anchor-spec.json
docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md
docs/process_traces/2026-09-02-process-rules/
docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md
docs/process_traces/2026-09-04-paper-custody/11-round-5-design-spec-astra.md
docs/process_traces/2026-09-04-peer-audit/
docs/process_traces/2026-09-05-d166-prompt0/01-dependency-census.md
docs/process_traces/2026-09-08-handoff-redo/
docs/process_traces/2026-09-09-probe/NEEDS-RULING-x.md
docs/process_traces/2026-09-09-probe/X-RULING-probe.md
docs/process_traces/archive/2026-09-09-probe/X-RULING-archive.md
docs/process_traces/older.md
docs/process-fetch.md
docs/process/coldgate_charter_registry.md
docs/process/coldgate_charter_v3_candidate.md
docs/process/coldgate_charter.md
docs/process/coldgate_consult_brief_template.md
docs/process/MAGISTRATE_RELAUNCH_PROMPT.md
docs/process/MAGISTRATE_WATCHDOG.md
docs/process/NIGHT_HANDBACK.md
docs/process/state_kernel.json
docs/process/state_kernel.schema.json
docs/project_status_history.md
docs/report_src
docs/report_src/appendices/A_reproducibility.md
docs/report_src/chapters/07_results.md
docs/report_src/generated/rpt001_vertical_slice.md
docs/report_src/README.md
docs/report_src/report.md
docs/research_question_registry.md
docs/reviews/2026-07-13-comprehensive-audit/CHECKPOINT.md
docs/risk_register.md
docs/run_reports/
docs/run_reports/...md or docs/process_traces/...md
docs/run_reports/2026-07-09-advisor-status-site.md
docs/run_reports/2026-07-13-history.md
docs/run_reports/example.md
docs/run_reports/latest.md
docs/run_reports/unused.md
docs/site
docs/site contains no HTML pages
docs/site_src/index.html
docs/site_src/research.html
docs/site_src/results.html
docs/site_src/site_sections.css
docs/site/build_manifest.json
docs/site/DRIFT.md
docs/site/style.css
docs/site/task_queue.html
docs/slides
docs/slides/backup.md
docs/specs/axi/sb_static_batch_verdict.md
docs/specs/c027/doc-008_state_kernel.md
docs/specs/c027/rpt-001_report_vertical_slice.md
docs/stop_cards/
docs/stop_cards/fixture-active.md
docs/tables
docs/tables/T2.md
```
