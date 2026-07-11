# Hardening-row scheduling scout (gpt-5.6-sol xhigh, 2026-07-11)

> Commissioned by the C-028 lead after PR #49 merged, with impl/p2041-vetted and
> impl/p2037 in flight. Verdicts on which adjudicated hardening rows start now.

Launch four parallel implementation streams now: **REPRO-002, CI-002, P2-046A, and RPT-002**. Hold their branches out of main until either:

- they land before the final DOC-008 refresh and are included in the final-main integration review, or
- C-028 bookkeeping closes.

Do not merge anything after that integration review without rerunning the final-head review.

The critical scheduling catch is **P2-044**: P2-037 may continue implementation, but it cannot be accepted as complete or claim-capable until P2-044 supplies and propagates the corrected idle variance/ESS term. This hard dependency in [TASK_QUEUE.md](/Users/edr/code/JouleWise/TASK_QUEUE.md:127) predates today’s P2-037 launch.

## Verdict matrix

| Row | Verdict | Reason |
|---|---|---|
| P2-043 doctor | **AFTER-P2041-LANDS** | Direct collision in `joulewise/cli.py`, `scripts/run_campaign.py`, campaign tests, and the readiness/acknowledgement wire; also wait for P2-037’s CLI hunk. |
| REPRO-002 privacy | **START-NOW** | Publication tooling and privacy contract are disjoint from both active implementations. |
| P2-044 idle ESS | **AFTER-P2041-LANDS** | Must replace the reducer’s current raw-sample `s²/n` term and then be consumed by P2-037; direct collision with both streams. |
| CI-002 packaging | **START-NOW** | Confine to packaging/workflow files; no production CLI/reducer edits are required. |
| P2-045 throughput | **AFTER-P2041-LANDS** | Direct reducer/schema/strict-dispatch collision; versioning must start from P2-041’s final reducer `0.4.0` contract. |
| P2-046 alignment | **START-NOW — A only** | Fixture-driven harness/analysis can be added in new files; B remains `[QUIET-MAC]` and cannot run under agent load. |
| P2-047 overhead | **AFTER-BOOKKEEPING** | Explicitly gated “after floors”; real P2-015 floor evidence does not exist, and its capture-path work would touch campaign/controller surfaces. |
| RPT-002 literature | **START-NOW** | Report-source-only footprint, provided it does not modify `scripts/claims_lint.py`. |
| P2-048 meter bridge | **AFTER-BOOKKEEPING** | Still conditional on unresolved P1-003, and its CLI/schema/floor integration overlaps the active streams. |

This follows the active chain in [RUN_STATE.md](/Users/edr/code/JouleWise/RUN_STATE.md:64), the adjudicated rows in [2026-07-10-hardening-adjudication.md](/Users/edr/code/JouleWise/docs/reviews/2026-07-10-hardening-adjudication.md:77), and the P2-041 collision map in [2026-07-11-p2041-red-tranche-triage.md](/Users/edr/code/JouleWise/docs/reviews/2026-07-11-p2041-red-tranche-triage.md:18).

## Per-row scope and collision assessment

### P2-043 — read-only `joulewise doctor`

1. **Scope/files:** new `joulewise/doctor.py`; modify `joulewise/cli.py`, `joulewise/environment.py`, `scripts/run_campaign.py`; add `tests/test_doctor.py`; modify `tests/test_cli.py` and `tests/test_run_campaign.py`; add `docs/contracts/doctor_preflight.md`, with narrow references from `docs/contracts/measurement_methodology.md`.
2. **Collisions:** direct with p2041 in CLI, campaign runner, campaign tests; direct with p2037’s required CLI subcommand work. No substantive DOC-008 collision; routine queue/state bookkeeping only.
3. **Unlanded dependency:** final P2-041 `claim_readiness` and campaign-log acknowledgement representation. Existing config warnings and powermetrics probes are already landed.
4. **Verdict:** **AFTER-P2041-LANDS**, and after P2-037’s CLI hunk is frozen or landed.

### REPRO-002 — publication privacy audit

1. **Scope/files:** new `joulewise/publication_privacy.py`; extend `scripts/package_bundle_pack.py`; add `tests/test_publication_privacy.py`; extend `tests/test_package_bundle_pack.py`; add `docs/contracts/publication_privacy.md`; update `docs/report_src/appendices/A_reproducibility.md`.
2. **Collisions:** none with p2041 or p2037. No DOC-008 surface. Bookkeeping collision is limited to `RUN_STATE.md`/`TASK_QUEUE.md`, which should be deferred to the lead.
3. **Unlanded dependency:** none. REPRO-001 publication remains gated on this row, but its existing packer is the correct substrate.
4. **Verdict:** **START-NOW** — isolated publication tooling with no active-stream API dependency.

### P2-044 — idle dependence and ESS

1. **Scope/files:** new `joulewise/idle_dependence.py`; modify `joulewise/reduce.py`, `joulewise/schemas.py`, likely `joulewise/aggregate.py` and `joulewise/bundle_read.py`; add `tests/test_idle_dependence.py`; modify `tests/test_uncertainty_p2029.py`, `tests/test_reduce.py`, and P2-037 analysis-engine tests; update `docs/contracts/run_bundle_layout.md`, `docs/phase_2/detection_floor.md`, and `docs/specs/c027/analysis_engine_trio.md`.
2. **Collisions:** direct p2041 collision in reducer/schema/uncertainty tests/contracts; direct semantic and test collision with p2037 estimators and metrology-aware intervals. No DOC-008 substantive overlap.
3. **Unlanded dependency:** P2-041’s final reducer version and P2-037’s consumer interface. Conversely, P2-037 acceptance depends on this row.
4. **Verdict:** **AFTER-P2041-LANDS** — implement immediately after the `0.4.0` reducer settles, then rebase/integrate P2-037 before accepting it.

### CI-002 — packaging and strictness

1. **Scope/files:** `.github/workflows/ci.yml`, `pyproject.toml`, optionally new `tests/test_ci_contract.py`. No production module changes.
2. **Collisions:** none with p2041 or p2037. DOC-008 does not own these files. Only mechanical state/report bookkeeping.
3. **Unlanded dependency:** none; setuptools discovery will automatically include p2037’s future package.
4. **Verdict:** **START-NOW** — workflow and packaging metadata are disjoint.

### P2-045 — throughput convention versioning

1. **Scope/files:** `joulewise/reduce.py`, `schemas.py`, `bundle_read.py`, `aggregate.py`, and `cli.py` strict-version dispatch; tests in `test_reduce.py`, `test_schemas.py`, `test_bundle_read.py`, `test_aggregate.py`, and `test_cli_run.py`; contracts in `run_bundle_layout.md`, `phase_2_plan.md`, and `analysis_plans.md`.
2. **Collisions:** heavy direct collision with p2041’s reducer/schema/CLI migration and p2037’s metric ingestion.
3. **Unlanded dependency:** final reducer `0.4.0` and final P2-037 metric-name expectations. The add-new-metric versus rename-legacy decision also needs to be frozen.
4. **Verdict:** **AFTER-P2041-LANDS**, additionally waiting until P2-037’s input vocabulary is stable.

### P2-046A/B — load-transition alignment

1. **Scope/files for A:** new `joulewise/load_transition_alignment.py`, `scripts/characterize_load_transition.py`, `configs/calibration/p2_046_load_transition/manifest.json`, `tests/test_load_transition_alignment.py`, fixture data under `tests/fixtures/p2046/`, and `docs/contracts/load_transition_alignment.md`. Do not edit the existing fake-powermetrics fixture.
2. **Collisions:** none with p2041 or p2037 when kept to those files. It consumes P2-038 evidence but does not change its production path. No DOC-008 overlap.
3. **Unlanded dependency:** none for A; P2-038 and the fixed bracketing fixture are on main. B requires a lead-controlled quiet Mac.
4. **Verdict:** **START-NOW for A only** — deterministic prep is independent; B remains gated.

### P2-047A/B — controller capture-overhead ABBA

1. **Scope/files:** likely `joulewise/controller.py`, `joulewise/bundle.py`, `scripts/run_campaign.py`, new capture/ABBA analysis module, frozen manifest under `configs/calibration/`, `tests/test_controller_capture_overhead.py`, and amendments to `detection_floor.md`.
2. **Collisions:** campaign-runner collision with p2041; semantic floor/claim collision with p2037. It may also overlap existing controller tests touched by #49-related surfaces.
3. **Unlanded dependency:** real P2-015 floors, plus a settled instrumented-stack definition. B is `[QUIET-MAC]`.
4. **Verdict:** **AFTER-BOOKKEEPING** — its explicit “after floors” gate is unsatisfied.

### RPT-002 — 2026 related-work refresh

1. **Scope/files:** update `docs/phase_4/related_work_draft.md`; create `docs/report_src/references.csl.json` and `source_map.json`; replace the stub in `docs/report_src/chapters/03_background_and_related_work.md`; update `docs/report_src/README.md`; extend `scripts/build_capstone.py` and `tests/test_rpt001_report_slice.py` only as needed; add `tests/test_rpt002_related_work.py`.
2. **Collisions:** none with active streams if `scripts/claims_lint.py` is read-only. No DOC-008 surface. Avoid `PROJECT_STATUS.md` and generated site files until bookkeeping.
3. **Unlanded dependency:** none. Primary-paper verification is desk work and explicitly ungated.
4. **Verdict:** **START-NOW** — isolated report-source stream.

### P2-048 — external-meter importer and bridge CLI

1. **Scope/files:** new `joulewise/external_meter.py` and `joulewise/boundary_calibration.py`; modify `joulewise/cli.py`, `schemas.py`, and `detection_floor.py`; add `tests/test_external_meter.py` and `tests/test_boundary_calibration.py`; update `docs/campaign_packs/q6_c5_2_10_rail_vs_wall.md` and the existing detection-floor bridge contract.
2. **Collisions:** direct CLI collision with both active streams; likely schema and claim/floor integration collision with p2037. No DOC-008 substantive overlap.
3. **Unlanded dependency:** unresolved P1-003 meter choice/export format and cadence capabilities.
4. **Verdict:** **AFTER-BOOKKEEPING** — hardware/interface decision absent, so implementation now would guess the importer boundary.

## Ready delegation contracts for START-NOW rows

### REPRO-002

1. **Task:** Implement the fail-closed publication privacy audit and transformed-public-pack path without mutating private bundles.
2. **Inputs:** main `73489a9`; hardening C2; `scripts/package_bundle_pack.py`; `tests/test_package_bundle_pack.py`; `docs/specs/c027/doc-009_repro-001_authority_and_repro.md`; `docs/contracts/run_bundle_layout.md`; PR #49 quality/log fields.
3. **Deliverables:** `joulewise/publication_privacy.py`; packer integration; privacy and packer tests; `docs/contracts/publication_privacy.md`; reproducibility-appendix amendment. Every field/path class must be classified; unknown fields fail closed; transformation manifest records source hash, operation, output hash, and non-byte-identity.
4. **Verification:** focused privacy/packer tests; synthetic secret-bearing bundle covering prompts, responses, absolute paths, user/host IDs, logs, environment and worker fields; audit-refusal mutation tests; transformed-pack tamper test; canonical suite.
5. **Constraints:** no edits under `runs/`; no release/publication; no private data copied into fixtures; include `remote_cleanup_failed`, `runtime_cleanup_ok`, node-worker logs/environment; do not edit CLI, reducer, schemas, shared state, or generated site.
6. **Report:** `docs/run_reports/2026-07-11-repro002-publication-privacy.md`.

### CI-002

1. **Task:** Add built-package and strict-mock CI hardening while preserving the zero-dependency core.
2. **Inputs:** main `73489a9`; hardening C4; `.github/workflows/ci.yml`; `pyproject.toml`; existing mock config and CLI flow.
3. **Deliverables:** wheel and sdist build; clean-venv wheel install; installed-package `python -m joulewise` smoke; `compileall`; canonical tests; strict mock `run → strict validate → reduce → strict validate`.
4. **Verification:** `python3 -m build`; install wheel into a disposable venv and invoke from outside the repository; run the exact strict mock chain; canonical suite; `git diff --check`.
5. **Constraints:** allowed production footprint is only `.github/workflows/ci.yml` and `pyproject.toml`; no console script, macOS job, Ruff, coverage threshold, optional extras, CLI behavior change, or retry masking of the two fixed flakes.
6. **Report:** `docs/run_reports/2026-07-11-ci002-packaging-strictness.md`.

### P2-046A

1. **Task:** Build the frozen fixture-driven load-transition marker/sample alignment harness and analysis artifact; do not execute the real-Mac phase.
2. **Inputs:** main `73489a9`; hardening C6; P2-038 production uncertainty spec; `joulewise/uncertainty_evidence.py`; fixed `tests/fixtures/fake_powermetrics_process.py` as read-only reference.
3. **Deliverables:** new analysis module and driver script; frozen calibration manifest; offset/residual/conservative-bound artifact schema; deterministic fixtures/tests; operator runbook for B.
4. **Verification:** closed-form offset/residual/bound fixtures; malformed/missing-transition refusal tests; two identical fixture runs produce byte-identical artifacts; focused tests; canonical suite.
5. **Constraints:** `[AGENT]` A only—no `/usr/bin/powermetrics`, load generation, quiet-window capture, or physical-bound conclusion; do not edit the existing fake-powermetrics fixture, controller, reducer, CLI, or P2-038 production code; retain PROVISIONAL language.
6. **Report:** `docs/run_reports/2026-07-11-p2046-load-transition-prep.md`.

### RPT-002

1. **Task:** Verify and integrate the seven 2026 positioning sources from primary papers, including all three Appendix C items and four remaining §11 anchors.
2. **Inputs:** main `73489a9`; hardening C8; Appendix C and §11 of `docs/JouleWise_Hardening_Proposal.md`; existing related-work draft; report-source profile and chapter stub.
3. **Deliverables:** corrected related-work draft; canonical CSL JSON; source map with stable identifiers, primary URLs, retrieval dates and evidence locations; assembled chapter; novelty wording explicitly disclaiming origination of energy-aware disaggregation; bibliography validation tests.
4. **Verification:** independently cross-check titles/authors/version/venue and each substantive claim against primary papers; JSON parse/schema checks; report build/check; focused report tests; `claims_lint` existing modes clean; canonical suite.
5. **Constraints:** primary papers and official proceedings only; no unverified proposal prose promoted as fact; do not touch `scripts/claims_lint.py`, claims-engine files, `PROJECT_STATUS.md`, shared state, or generated site; preserve narrower boundary-honest consumer/edge positioning.
6. **Report:** `docs/run_reports/2026-07-11-rpt002-related-work-refresh.md`.

## Staleness after today’s landings

- **REPRO-002 needs a baseline amendment:** its inventory must explicitly cover PR #49’s `measurement_quality.remote_cleanup_failed`, the retained `runtime_cleanup_ok` union, remote worker logs/paths/environment, and cleanup-failure strings. The row remains valid, but an audit based on the pre-#49 field inventory would be incomplete.
- **CI-002 is not stale:** today’s fixture fixes removed two flakes, but did not add package build/install, `compileall`, or strict mock CI. Do not add reruns or exceptions for those now-dead flakes.
- **P2-046 is not stale:** the fake-powermetrics SIGTERM fix guarantees a right-edge bracket; it does not characterize real load-transition offset/residual behavior.
- **P2-044’s scope is not stale, but its schedule is:** P2-037 is already in flight despite P2-044 being its adjudicated pre-integration dependency.

Read-only scout completed on clean `main @ 73489a9`; no files changed and no tests were run.