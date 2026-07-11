# Hardening-Proposal Adjudication (C-028, 2026-07-10)

Lead adjudication of `docs/JouleWise_Hardening_Proposal.md` (independent
Codex review commissioned by Ed), based on the gap analysis below
(gpt-5.6-sol xhigh advisory session) which the lead reviewed and accepts
in full — including its disagreements with the proposal.

**Lead rulings:**
1. The proposal's individual findings are ADOPTED per section (C) below;
   its parallel G0-G7 lifecycle is NOT adopted (existing gates/queue/
   D-060 govern; the gap analysis argues this correctly in (D)).
2. All section (B) conflict reconciliations are ACCEPTED as written.
3. Section (C) rows 1-9 enter the queue now (correctness/gate/report
   work permitted under ratified D-060); rows 10-11 are SHELF post-G6.
4. Same-day actions at adjudication: P0-003 CLOSED (Ed chose iCloud
   Drive; fresh restore test passed) and D-060 RATIFIED by Ed — the
   proposal's Phase-0 gate and freeze are thereby live.
5. The §11 research agenda is preserved as a paper roadmap (no registry
   intake now, per (B) row 12 and D-055); revisit after G6-equivalent.

---

I read the full proposal and inspected the requested branches/worktrees. One provenance wrinkle: the proposal names `d9389cd` as its baseline, but that commit is itself the post-PR-#41–#45 checkpoint. Substantively, however, the proposal analyzes the earlier state and misses much of those PRs’ content.

## (A) Already-landed map

“Main” below means `main @ d9389cd`; pushed branches are not yet landed; the P2-038 and NV-GATE-2 worktrees are uncommitted.

| Proposal item | Current repo evidence | Residue |
|---|---|---|
| Immutable, re-reducible evidence kernel; strict artifact validation | Already core architecture on main: bundle reader, raw powermetrics lineage, reducer/version dispatch, strict validation, pack-and-verify tooling. PR #43 added P2-040 correctness/version handling; PR #45 added the floor artifact. | Physical sensor truth remains deliberately outside strict validation, as D-030 requires. |
| Phase 0 scope freeze | Substantially expressed by proposed D-060 and the current queue/do-not-do list. | D-060 is still **PROPOSED awaiting Ed**; it is not binding yet. P0-003 off-machine backup is still open. |
| Replace campaign `publishable` | Implemented on `origin/impl/p2041`: collection `usable/partial/blocked/invalid`; readiness `ready_for_analysis/not_ready_for_analysis/not_assessed`; one-bundle case fixed. | Branch needs integration after P2-042. P2-037 still owns actual claim outcomes. No publication-approval state should be added to this layer. |
| Unknown-key safety | `origin/impl/p2040-remainder` emits structured `ConfigKeyWarning`, records `metadata.config_warnings`, and preserves normalized hashes. | It implements adjudicated warn-and-ignore, not proposal-level rejection or acknowledgement-aware preflight. A doctor/campaign preflight can add the latter without changing schema-0.1 parsing. |
| `warmup_seconds` | Fully implemented on `origin/impl/p2040-remainder` as post-active-warmup settling outside sampling/measured windows, with injected-clock tests. | Merge/review only. |
| Cleanup contamination | Local cleanup success/failure is surfaced as `measurement_quality.runtime_cleanup_ok` on `origin/impl/p2040-remainder`. NV-GATE-2’s dirty worktree detects surviving vLLM/sampler processes, demotes them, records remote cleanup failures, and removes remote artifacts. | P2-041 does not appear to consume `runtime_cleanup_ok=false` to stop a following local member. That integration residue should be adjudicated. |
| Metric naming and denominator provenance | Main already distinguishes total-token and output-token energy; D-058 makes runtime-observed output tokens authoritative. PR #43 fixed config-vs-runtime denominator precedence. | Throughput remains `N/(t_last-t_first)` and needs the convention decision below. |
| Frozen analysis manifest | Implemented and pushed on `origin/impl/p2042`: deterministic `analysis_manifest.json`, semantic IDs, frozen contrast enumeration, hash linkage, atomic emission, validator, and lint mode. | Draft PR #46 review/integration remains. |
| Claim engine | P2-039 floor producer/resolver is on main; P2-042 manifest and P2-041 readiness consumer are pending. | P2-037—paired contrasts, governed intervals, LOO, randomization, Holm/BH, floor outcomes—is genuinely absent. |
| Production uncertainty path | The uncommitted `impl/p2038` worktree supplies clock brackets, marker/sample support bounds, pre/post idle evidence, post-run sentinel, strict re-derivation, and a production shakedown gate. | Still needs lead review, integration, and the quiet-machine live closure. It does not estimate autocorrelation/effective sample size. |
| Detection-floor artifact | Landed in PR #45: versioned artifact, guarded and unguarded floors, ABBA deltas, exact identities, transport refusal, provenance validation. | Real calibration bundles and automatic consumption by an eligible real claim remain unexecuted. |
| Wall/PD bridge design | Already designed under D-054, [detection_floor.md](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md), Q6/C5-2.10, D-018, and registry Q6/C5-3.2. It already specifies paired deltas, slope/intercept bridge fitting, residual gates, synchronization, and boundary-specific claim ceilings. | P1-003 meter decision, external-meter importer/CLI, and live campaign remain. Do not create another design document. |
| Narrow reference campaign | Existing 2M/AP-2 machinery, P2-042 frozen manifests, order provenance, and floor/claim stack cover much of the design. | No new, complete, floor-governed real reference campaign exists. The proposal’s “five blocks” is below the adjudicated minimum. |
| Report vertical slice | PR #44 landed RPT-001: permanent `docs/report_src/`, legacy bundle→artifact→table/figure→claims-index→report path, claims lint, atomic build. | The background chapter remains an assembly stub; final claim-oriented comparison pages and new real campaign content remain. |
| Public reproducibility | Pack/verify tooling landed in PR #25; REPRO-001 specifies three bundles, environment locks, release provenance, and external re-reduction. | Actual publication and external attestation are Ed-facing and undone. |
| Publication privacy | Not delivered. Current pack tooling copies strict-valid bundles verbatim and has no privacy classifier or transformation ledger. | Genuinely new and required before publication. |
| CI/package hardening | Main has Linux 3.11/3.14 tests and a non-strict mock E2E. Some branches ran `compileall` locally. | CI does not install/build the package, does not run strict mock validation, has no console script, macOS job, Ruff, or coverage reporting. |
| `joulewise doctor` | Individual capabilities already exist: config validation, environment snapshotting, powermetrics capability probe, thermal-pressure capture, and shakedown assertions. | No consolidated read-only preflight command or machine-readable acknowledgement policy exists. |
| NVIDIA hardening | The uncommitted NV-GATE-2 worktree implements include-usage fallback, stream-chunk demotion, process-survival handling, remote cleanup reporting, strict nvidia-smi lineage, cooldown correction, and a real worker subprocess test. | Still uncommitted/unreviewed and fixture-first; live hardware promotion remains gated. |
| Governance simplification | D-063/DOC-008 already specifies a machine-readable state kernel, generated live queue/restart blocks, PROJECT_STATUS history archive, and retirement of the standalone reflection protocol. | Broad relocation of councils/run reports is neither implemented nor part of DOC-008 Stage 1. |
| Research agenda | Nearly every §11 question already has a canonical equivalent in the D-055 registry: HET-PD→Q1/Q2/Q3; MODEL→Q4/C5-2.8; QNT→C5-1.12/C5-2.1; XFER→Q2/C5-2.3; KVQ→C5-2.4; SPEC→C5-2.5; CACHE→RQ-CACHE-PREFIX; GEN→C5-3.1/C5-3.5. | No new registry rows are justified now. |
| Appendix C literature | None of the proposed arXiv IDs appears outside the untracked proposal. | These additions belong in the existing related-work source, bibliography, source map, and RPT chapter—not in a new track. |

## (B) Conflicts with adjudicated rulings

| Conflict | Reconciliation | Winner |
|---|---|---|
| Proposal: reject unknown configuration keys by default. C-027/P2-040: schema 0.1 must deterministically warn-and-ignore for compatibility. | Keep parsing warn-first. Make `doctor` and campaign preflight fail when machine-readable warnings exist unless the operator supplies a recorded acknowledgement. This realizes the proposal’s compromise without changing config bytes or old-bundle readability. | C-027/P2-040 parsing policy wins; proposal wins at the execution-preflight layer. |
| Proposal vocabulary: `collection_complete`, `strict_valid`, `analysis_ready`, `claim_ready`, `publication_approved`. Implemented/adjudicated vocabulary separates collection verdicts, readiness, P2-037 outcomes, and publication acts. | Treat completeness and strict validity as facts; retain P2-041’s collection/readiness enums; retain P2-037’s exact outcomes; represent publication as a signed release/review act, not another campaign verdict. | Analysis-trio/P2-041 vocabulary wins. |
| Proposal suggests renaming `publishable` to `publication_approved`. | Do not perform a one-for-one rename. The old term incorrectly conflated collection and interpretation. P2-041’s multi-layer split is stronger. | P2-041 wins. |
| Proposal outcome examples: “directional, unresolved, not resolvable, equivalence-qualified, invalid.” | Use the closed engine vocabulary: `not_estimable`, `not_resolvable`, `unresolved`, `direction_supported`, `equivalent`; collection `invalid` belongs to another layer. | D-053/D-057 and the engine-trio spec win. |
| Reference campaign says at least five exchangeable blocks. | D-053 requires at least six for randomization checks; D-062 says near-floor confirmatory work should generally be nearer ten, with frozen `n`. | D-053/D-062 win. |
| Proposal’s CI package/console/macOS expansion versus D-017 core-only CI and C-011’s explicit rejection of a console script before 2M. | Amend D-017 only for cheap built-package installation, strict mock E2E, and `compileall`. Defer console entry point and broad macOS/dev-tool expansion until after 2M/reference evidence. | Existing sequencing wins now. |
| Proposal’s “one current status source” versus D-023 and D-063. | Preserve one authority **per fact**: exit checklists for phase completion, state kernel for work selection, PROJECT_STATUS as derived advisor prose. A single global status document would reintroduce mixed semantics. | D-023/D-063 win. |
| Broad archive hierarchy could hide binding decisions and acceptance evidence. | DOC-008 may archive derived status history. Do not move binding decision-log entries, cited run reports, or acceptance evidence merely to exclude them from searches. A later link-integrity/archive audit can consider non-authoritative narrative. | D-050/D-063 and provenance requirements win. |
| Proposal prefers a root-owned powermetrics wrapper if the sudo rule is broad. D-004 explicitly chose the Apple-owned binary plus scoped sudoers and rejected a wrapper. | Keep D-004 unless its revisit trigger fires—macOS privilege behavior changes or the machine owner rejects the current rule. `doctor` should inspect, never edit, sudoers. | D-004 wins. |
| Proposal says cleanup failures should block the next run. Adjudication distinguishes process survival from file/directory cleanup failure. | Surviving runtime/sampler process must demote/block. File/directory removal failure remains a visible quality/forensics signal. Local `runtime_cleanup_ok=false` needs explicit campaign consumption because it implies possible survival. | NV-4’s distinction wins. |
| Gate G7 forbids any claim-bearing backend until it independently satisfies G3–G6. | Allow D-054’s L0/L1 capability and descriptive observations with provisional labels and unknown terms. Require full backend-specific gates for L2/L3 comparisons. | D-054/claims ladder wins. |
| Immediate §11 registry intake versus the agenda’s own “post-hardening” framing and proposed D-060. | Add no new live rows now. Preserve a non-authoritative alias crosswalk; after G6, promote only distinct questions that survive scope review. | D-055 and the depth-before-breadth stop line win. |

## (C) Genuinely new items worth adopting

These ranks are value-per-effort, but none should interrupt the active stop-card integration chain.

| Rank | Proposed queue row | Lane / priority | Acceptance |
|---:|---|---|---|
| 1 | **P2-043 — Read-only `joulewise doctor`** | `[AGENT]`, P1 pre-Window-A | Machine-readable and human output covering config warnings, versions, architecture, model/tokenizer identity, powermetrics presence/`sudo -n`, sampler fields, thermal pressure, destination/free space, and quiet-machine warnings; non-mutating; deterministic fixture tests; campaign mode fails on unacknowledged config warnings. |
| 2 | **REPRO-002 — Publication privacy audit** | `[AGENT]`, P1 pre-publication | Enumerate prompts, responses, paths, user/host identifiers, logs and environment fields; fail closed on unreviewed fields; distinguish immutable private bundle from transformed public pack; record transformation manifest and hashes; never claim byte identity after transformation. |
| 3 | **P2-044 — Idle dependence and effective sample size** | `[AGENT]`, P0 before P2-037 claim integration | From retained idle traces, compute a predeclared block-mean or autocorrelation-adjusted variance/ESS; never use raw adjacent sample count as independent `n`; propagate the governed variance; closed-form and highly correlated fixtures; P2-037 consumes the corrected term. |
| 4 | **CI-002 — Core packaging/strictness hardening** | `[AGENT]`, P1 | Build wheel/sdist, install into a clean environment, run `python -m joulewise`, `compileall`, canonical tests, and strict mock run→validate→reduce→strict. Preserve zero-dependency core. No console script or macOS hardware claim in this row. |
| 5 | **P2-045 — Throughput convention versioning** | `[AGENT]`, P2 before throughput enters a governed figure | The reducer currently implements `N/(t_last-t_first)`. Because the span contains only `N-1` inter-token intervals, steady-state decode throughput is `(N-1)/span`; current code overstates by `N/(N-1)`—14.3% at eight tokens, about 0.2% at 512. Add/version an unambiguous inter-token metric or explicitly rename the legacy convention; preserve old-bundle dispatch and update tests/contracts. |
| 6 | **P2-046A/B — Load-transition alignment characterization** | A `[AGENT]`, B `[QUIET-MAC]`, P1 | A: frozen marker/load harness and analysis producing offset/residual/bound artifacts. B: execute counterbalanced transitions on the real Mac and determine whether P2-038’s conservative interval-support bound is validated or must widen. This is not already covered by P2-038. |
| 7 | **P2-047A/B — Controller capture-overhead ABBA** | A `[AGENT]`, B `[QUIET-MAC]`, P2 after floors | A: standard event path versus buffered/minimal-marker path, identical output policy and output hashes, frozen ABBA manifest. B: real floor-governed execution. Default disposition is scope-to-instrumented-stack; subtraction requires a separately justified model. |
| 8 | **RPT-002 — 2026 related-work refresh** | `[AGENT]`, P1 report | Independently verify the three Appendix C sources—and preferably the other four §11 anchors—from primary papers; update `related_work_draft.md`, CSL bibliography, source map, and chapter; revise novelty language so JouleWise does not claim origin of energy-aware disaggregation. |
| 9 | **P2-048 — External-meter importer and bridge CLI** | `[AGENT]`, P2 conditional on P1-003 | Implement the already-designed Q6 artifact/import format and `boundary-calibrate`; bind meter metadata, synchronization, paired windows, slope/intercept, residuals, held-out gate, floor identity, and refusal reasons. The design itself should not be duplicated. |
| 10 | **CI-003 — Post-reference developer polish** | `[AGENT]`, P3/post-G6 | Add console entry point, macOS install/import job if it proves useful, Ruff, and measured coverage reporting. Adopt thresholds only after observing the baseline. |
| 11 | **DOC-010 — Post-DOC-008 archive audit** | `[AGENT]`, P4/post-G6 | Identify only non-authoritative historical material eligible for relocation; preserve paths or redirects, citations, decision authority, and link integrity. No broad archive migration before DOC-008 proves the state kernel. |

For §11 specifically: no new canonical registry rows belong **now**. Its IDs are mostly aliases or elaborations of existing questions. After G6, LOAD-1 may merit a distinct row if it cannot be cleanly represented by C5-1.7/C5-2.6; the rest should first be mapped to existing owners rather than duplicated.

## (D) Disagreements

- The proposal is too willing to turn good observations into another G0–G7 management system. JouleWise already has adjudicated gates, a queue, stop cards, checklists, and DOC-008. Adopt individual findings, not the proposal’s parallel lifecycle.

- Five blocks is not enough for the project’s own intended inference. Six is the floor; near-floor confirmatory work should target closer to ten.

- `N/(t_last-t_first)` is not the natural decode-throughput estimator when timestamps mark completed tokens. It is defensible only as a specially named legacy ratio, not as generic token throughput.

- A broad G2 CI/tooling campaign before Window A is poor capstone sequencing. Strict mock CI and clean package installation are cheap and worthwhile; console scripts, Ruff, coverage targets, and macOS CI are polish unless an observed defect justifies them.

- A full `doctor` laundry list should not become a brittle “supported macOS” certification system. It should report evidence, fail on known hard requirements, and use warnings/recorded acknowledgements for ambient load, free-space preference, and uncalibrated thermal heuristics.

- Controller-overhead subtraction is too ambitious. Measuring it is useful; subtracting it risks replacing observed evidence with a fragile correction model. The honest default is to scope results to the instrumented stack.

- The proposed broad historical archive is premature and potentially harmful. Run reports and council records are often cited evidence, not clutter. DOC-008’s narrow generated-state fix addresses the demonstrated failure without moving the evidentiary substrate.

- Requiring wall/PD calibration before a complete capstone would be overcautious. The proposal correctly says not to do that; same-boundary, rail-labeled L2 work can be defensible under D-054.

- The §11 agenda is far beyond capstone scope. It is useful as a paper roadmap, not as backlog. Importing its rows now would directly repeat the breadth problem the proposal diagnoses.

- Public release of verbatim bundles without a privacy audit is the proposal’s strongest genuinely new warning. Existing pack tooling is integrity-focused, not publication-safety-focused.

<<<<<<< HEAD
If only one thing can be done this week: **close P0-003 by choosing an off-machine destination and passing a fresh restore test**. That is the only action that unlocks irreplaceable quiet-machine evidence without weakening any scientific gate.
=======
If only one thing can be done this week: **close P0-003 by choosing an off-machine destination and passing a fresh restore test**. That is the only action that unlocks irreplaceable quiet-machine evidence without weakening any scientific gate.
>>>>>>> origin/main
