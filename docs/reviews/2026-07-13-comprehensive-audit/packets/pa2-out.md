```json
[
  {
    "work_order": "WO-001",
    "collides_with": [
      "docs/contracts/node_worker_protocol.md §Remote Path Layout",
      "docs/specs/c027/nv-gate-2_live_promotion.md §NV-4: remote temp-artifact cleanup surfacing"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "Both surfaces currently permit final cleanup to remove remote artifacts immediately. Custody-before-cleanup and the persistent retention manifest replace that timing rule; D-011 completion semantics are extended, not replaced."
  },
  {
    "work_order": "WO-002",
    "collides_with": [
      "docs/contracts/run_bundle_layout.md §Summary Metrics Minimum Fields",
      "docs/decision_log.md §D-011 amendment (2026-07-07 shared succeeded-summary validator)"
    ],
    "kind": "contradicts",
    "required_supersession_line": true,
    "note": "The current contract requires finite energy_request_j for succeeded summaries. The register delegates this to packets/ed-rulings.json R3, but that file contains no R3. Adoption is unsafe until R3 is materialized; if R3 permits null, both losing surfaces require dated amendment."
  },
  {
    "work_order": "WO-003",
    "collides_with": [
      "docs/contracts/adapter_contracts.md §Suite Runtime Adapter",
      "docs/contracts/run_bundle_layout.md §Suite Bundle Additions",
      "docs/decision_log.md §D-035 and §D-036"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "It enforces existing realized-output and computed-verdict principles for single runs and spikes while preserving sealed suite per-item outcomes."
  },
  {
    "work_order": "WO-004",
    "collides_with": [
      "docs/specs/c027/p2-039_floor_artifact.md §5.3 Bundle and artifact hashes and §7.3 P2-037 interface boundary",
      "docs/specs/c027/analysis_engine_trio.md §B3 P2-039 floor-artifact consumer interface"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "The specifications already require byte-bound floor evidence; this order closes an implementation/admission gap without changing the estimator."
  },
  {
    "work_order": "WO-005",
    "collides_with": [
      "docs/decision_log.md §D-030 amendment (2026-07-11 P2-044 idle dependence)",
      "docs/phase_2/detection_floor.md §P2-044 idle-dependence predeclaration",
      "docs/contracts/run_bundle_layout.md §Idle-mean dependence contract (P2-044)",
      "docs/specs/c027/p2-040_reducer_gate_correctness.md §No-scope-creep fences",
      "docs/phase_2/phase_2_exit_checklist.md §Evidence Matrix row P2-040 reducer/gate correctness"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "Duration-weighted idle means and support-overlap/counter integration directly replace the frozen arithmetic-mean and trapezoidal-point-estimand rules. The WO scope omits the decision log, detection-floor spec, P2-040 spec, and checklist, so it cannot satisfy D-043 as written."
  },
  {
    "work_order": "WO-006",
    "collides_with": [
      "docs/contracts/run_bundle_layout.md §Event Log Minimum Fields",
      "docs/contracts/measurement_methodology.md §Phase Labels"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "It defines validation for the already-documented phase pairs and makes node identity part of the pairing domain."
  },
  {
    "work_order": "WO-007",
    "collides_with": [
      "docs/contracts/run_bundle_layout.md §Required Artifacts frequency-unit note",
      "docs/contracts/run_bundle_layout.md §Summary Metrics Minimum Fields"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "The additive MHz field and deprecated legacy alias preserve old bytes; rich powermetrics records remain verbatim."
  },
  {
    "work_order": "WO-008",
    "collides_with": [
      "docs/decision_log.md §D-045 Suite substrate execution semantics",
      "docs/contracts/adapter_contracts.md §Suite Runtime Adapter"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "This changes ownership of shared bookkeeping, not the pinned runtime-facing suite semantics; independent backend outcomes remain required."
  },
  {
    "work_order": "WO-009",
    "collides_with": [
      "docs/decision_log.md §D-044 Suite config identity",
      "docs/decision_log.md §D-045 Suite substrate execution semantics",
      "docs/decision_log.md §D-056 Suite order policies",
      "docs/specs/suite_next/decision_review_log.md §SN-003 Sidecars carry generator truth until schema promotion"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "The exact losing surfaces depend on the still-unmade per-field ruling. Any removal or reinterpretation of within_bundle_repeats, cooldown_policy, cache_policy, warmup_policy, or item status_policy must amend D-044 identity/default rules and preserve a versioned migration."
  },
  {
    "work_order": "WO-010",
    "collides_with": [
      "docs/contracts/node_worker_protocol.md §Task JSON v1",
      "docs/contracts/node_worker_protocol.md §Artifacts Directory",
      "docs/contracts/node_worker_protocol.md §Remote Path Layout",
      "docs/phase_1/2k_live_verification_checklist.md §§1-5"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "Correlation tokens and safe-component identifiers alter the pinned wire shape and response identity. The lead must first choose a dated provisional-v1 amendment or protocol-version bump."
  },
  {
    "work_order": "WO-011",
    "collides_with": [
      "docs/specs/suite_next/prompt_sequencing_spec.md §Manifest and sidecar rules and §Text-path hash guard",
      "docs/specs/suite_next/decision_review_log.md §SN-003"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "It implements the already-required P2-025 text-path guard; an authoritative manifest-policy exemption would require explicit schema promotion under SN-003."
  },
  {
    "work_order": "WO-012",
    "collides_with": [
      "TASK_QUEUE.md §Current Queue row P2-019 and generated row Q4",
      "docs/specs/rq_energy_variance_design.md analysis-plan row 'MDE/n sizing + predeclared top-up rule'",
      "docs/campaign_packs/c5_2_3_kv_economics.md corresponding MDE/n row",
      "docs/campaign_packs/c5_2_7_device_perf_w_rankings.md corresponding MDE/n row",
      "docs/campaign_packs/c5_2_8_placement_optimality.md corresponding MDE/n row",
      "docs/campaign_packs/c5_3_1_3_5_replication.md corresponding MDE/n rows",
      "docs/campaign_packs/c5_i_1_i_2_i_5_import_family.md corresponding MDE/n rows",
      "docs/campaign_packs/c5_i_3_flores_fertility.md corresponding MDE/n row",
      "docs/campaign_packs/c5_i_4_harness_overhead_floor.md corresponding MDE/n row",
      "docs/campaign_packs/q6_c5_2_10_rail_vs_wall.md corresponding MDE/n row"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "These losing rows authorize outcome-dependent growth contrary to D-062. Each needs a dated replacement/reference to the frozen registry authority; merely changing the generator is insufficient."
  },
  {
    "work_order": "WO-013",
    "collides_with": [
      "docs/specs/c027/analysis_engine_trio.md §B15 claims_lint and Phase-4 claims-index consumption",
      "docs/specs/c027/rpt-001_report_vertical_slice.md §5.3 claims_lint --mode phase4"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "The two specifications pin incompatible mode names and row dialects. The unified version-aware entry point should back-annotate both while preserving D-059's single-linter decision."
  },
  {
    "work_order": "WO-014",
    "collides_with": [
      "docs/specs/c027/rpt-001_report_vertical_slice.md §§3.1, 4.1, 5.2, 5.3, 6.1 and 9.5 rpt001-v1 default references"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "Making rpt001-v2 canonical changes the spec's default paths and commands. The spec is absent from WO-014 bounded_scope, so a lead-owned same-session amendment is required for D-043 closure."
  },
  {
    "work_order": "WO-015",
    "collides_with": [
      "docs/specs/c027/rpt-001_report_vertical_slice.md §3.1 Pinned input manifest",
      "docs/specs/c027/rpt-001_report_vertical_slice.md §4.1 Versioned outputs"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "Section 3.1 says v1 uses package-packer identity semantics, but sealed v1 actually uses the tab-delimited algorithm. The spec must label that legacy algorithm and point canonical identity to v2."
  },
  {
    "work_order": "WO-016",
    "collides_with": [
      "docs/contracts/measurement_methodology.md §Run Lifecycle and §Measurement Quality Fields",
      "docs/specs/c027/p2-039_floor_artifact.md §5.2 clean-project-commit invariant",
      "docs/specs/c027/doc-009_repro-001_authority_and_repro.md §Fences"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "It adds capture-time and end-state provenance while preserving the existing rule that dirty evidence may complete but cannot support claims or publication."
  },
  {
    "work_order": "WO-017",
    "collides_with": [
      "docs/specs/c027/doc-009_repro-001_authority_and_repro.md §REPRO-2 and §REPRO-3",
      "TASK_QUEUE.md §Current Queue P2-027 and generated E2",
      "docs/phase_5/phase_5_exit_checklist.md §Definition Of Done",
      "AGENT_PLAN.md §Phase 5 acceptance criteria",
      "docs/contracts/publication_privacy.md §Publication boundary"
    ],
    "kind": "contradicts",
    "required_supersession_line": true,
    "note": "The existing authority requires publication plus one external re-reduction; WO-017 makes full re-reducibility controlled/internal by default and external handoff opt-in. Adoption needs the Ed privacy ruling and either dated descope of REPRO-2/P2-027/Phase-5 wording or retention of those obligations. A raw-evidence handoff also requires an explicit privacy-contract exception."
  },
  {
    "work_order": "WO-018",
    "collides_with": [
      "docs/decision_log.md §D-051 Advisor status site",
      "docs/specs/advisor_status_site_analysis.md §Production facts observed and §Phase D"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "Pinning renderer/tool versions and recording artifact identity strengthens the existing source-derived, fail-soft site architecture."
  },
  {
    "work_order": "WO-019",
    "collides_with": [
      "docs/decision_log.md §D-017 CI scope",
      "docs/phase_5/phase_5_exit_checklist.md §Evidence Matrix items 5.0-5.3"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "Wiring capstone, site, capsule, and bundle-pack construction into CI exceeds D-017's settled core-only CI scope. WO-019 does not name D-017; that decision and index row need a dated amendment."
  },
  {
    "work_order": "WO-020",
    "collides_with": [
      "docs/decision_log.md §D-065 clause 2",
      "docs/contracts/bridge_protocol.md §10 Implementation and consumption pointers"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "It implements the already-ratified one-home/pointer rule while retaining D-065's enforcement-boundary exemptions."
  },
  {
    "work_order": "WO-021",
    "collides_with": [
      "docs/specs/c027/doc-008_state_kernel.md §3.1 Top-level object, §3.6 Cross-record invariants and §4 Generator and generated regions",
      "RUN_STATE.md §Known Workspace State",
      "AGENT_PLAN.md §Single Source Of Truth Map",
      "docs/decision_log.md §D-063 Process architecture v2"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "Schema v3 and AUTHORITATIVE_WORK_SELECTION_STATE replace the explicit schema-v2/NOT_AUTHORITATIVE_DERIVED_VIEW rule and the prose-owned work-selection model. D-063 and its index should record the authority upgrade; phase completion remains with exit checklists."
  },
  {
    "work_order": "WO-022",
    "collides_with": [
      "docs/decision_log.md §D-060 Depth-before-breadth stop line",
      "docs/decision_log.md §D-061 Review-layer evaluation rule",
      "docs/orchestration.md §Council discipline"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "The numeric bands and spend tripwire add procedural teeth without replacing D-060 or permitting automatic deletion of D-061-protected layers."
  },
  {
    "work_order": "WO-023",
    "collides_with": [
      "docs/contracts/run_bundle_layout.md §Required Artifacts",
      "docs/contracts/publication_privacy.md §Path and field classification"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "A new top-level quarantine-diagnostics field would require additive contract documentation and privacy classification; run_bundle_layout.md is currently absent from the bounded scope."
  },
  {
    "work_order": "WO-024",
    "collides_with": [],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "The landed deletion removes dead preflight work without changing the publication transform, hash manifest, or REPRO-2 pack contract."
  },
  {
    "work_order": "WO-025",
    "collides_with": [
      "docs/specs/c027/p2-038_production_uncertainty_evidence.md §7.2 Derivation record"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "The landed reason is an additive member of the spec's local provenance vocabulary, not D-057's claim-reason vocabulary."
  },
  {
    "work_order": "WO-026",
    "collides_with": [],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "Test-only re-homing enforces existing public safeguards and changes no authority."
  },
  {
    "work_order": "WO-027",
    "collides_with": [
      "docs/decision_log.md §D-064 recovery-substrate clause"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "Deletion is compatible only after the unique live-visibility recipe is retained elsewhere; D-064's supported status/manifest recovery surfaces remain untouched."
  },
  {
    "work_order": "WO-028",
    "collides_with": [
      "docs/decision_log.md §D-005",
      "docs/contracts/run_bundle_layout.md §Experiment Manifests"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "The landed ordering strengthens member discoverability. If aggregate_error remains a manifest field, the additive field still needs contract documentation."
  },
  {
    "work_order": "WO-029",
    "collides_with": [
      "docs/decision_log.md §D-006 Dashboard v1",
      "docs/contracts/token_normalization.md §Primary Metric and §J/Token companion metrics"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "The report remains a diagnostic static browser; provenance co-display prevents governed token metrics from looking claim-ready."
  },
  {
    "work_order": "WO-030",
    "collides_with": [
      "docs/decision_log.md §D-009 Dependency policy"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "The landed editable-extra documentation and bounded matplotlib requirement implement D-009's optional-analysis-extra policy."
  },
  {
    "work_order": "WO-031",
    "collides_with": [
      "docs/decision_log.md §D-023",
      "docs/decision_log.md §D-051",
      "AGENT_PLAN.md §Single Source Of Truth Map"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "It adds a freshness owner while preserving exit-checklist status authority and source-derived advisor views."
  },
  {
    "work_order": "WO-032",
    "collides_with": [
      "docs/phase_2/suite_implementation_research.md threshold-sensitivity paragraph",
      "docs/contracts/analysis_plans.md §AP-5"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "D-047 already invalidated the 40-80-item pseudo-replication premise. The stale paragraph needs a dated D-047 supersession line; AP-5 only needs an additive authority pointer."
  },
  {
    "work_order": "WO-033",
    "collides_with": [
      "TASK_QUEUE.md §Current Queue P2-016(a) post-2M controller split",
      "TASK_QUEUE.md §Current Do-Not-Do-Yet List Phase-3 data fence",
      "docs/decision_log.md §D-060"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "Keep this shelved until campaign-scale or multi-node edits actually touch run_campaign.py. Its boundary must be distinguished from P2-016(a), and it must not become selectable before the post-2M/D-060 gates."
  },
  {
    "work_order": "WO-034",
    "collides_with": [
      "TASK_QUEUE.md §Current Queue P3-001b",
      "TASK_QUEUE.md §Current Queue SPLIT-AP",
      "TASK_QUEUE.md §Current Queue P2-016(f)",
      "TASK_QUEUE.md §Current Do-Not-Do-Yet List schema-v0.2 and live-split fences",
      "docs/phase_3/phase_3_exit_checklist.md rows Schema v0.2, Transfer microbenchmark and Offline split decomposition"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "New command-owner rows should be children/dependencies of the existing split-prep and Phase-3 rows, not parallel owners. Preserve the Stage-3.1 and offline-before-live fences."
  },
  {
    "work_order": "WO-035",
    "collides_with": [
      "docs/contracts/node_worker_protocol.md §Task JSON v1",
      "docs/phase_3/phase_3_plan.md §Stage 3.1 Schema v0.2 + Transfer Microbenchmark",
      "TASK_QUEUE.md §Current Do-Not-Do-Yet List schema-v0.2 fence"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "A discriminated transfer payload replaces the current nominally open task_type plus closed runtime/workload/telemetry payload shape. Amend/version the protocol only when Stage 3.1 is scheduled."
  },
  {
    "work_order": "WO-036",
    "collides_with": [
      "TASK_QUEUE.md §Current Queue P2-005",
      "TASK_QUEUE.md §Current Queue P2-016(b)",
      "TASK_QUEUE.md §Current Do-Not-Do-Yet List Phase-3 data and live-split fences",
      "docs/contracts/node_worker_protocol.md §Task JSON v1 and §Remote Path Layout"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "Keep shelved until retries or concurrent campaigns are introduced. If the ownership primitive changes the wire shape, promote it through the same protocol-version closure as WO-035."
  },
  {
    "work_order": "WO-037",
    "collides_with": [
      "TASK_QUEUE.md §Current Queue P2-005 and generated A23",
      "TASK_QUEUE.md §Current Queue P1-006 and generated E6",
      "docs/specs/c027/nv-gate-2_live_promotion.md §Definition of live promotion and §8 acceptance",
      "docs/phase_1/2k_live_verification_checklist.md §7 De-Provisionalization Notes",
      "docs/phase_2/phase_2_exit_checklist.md row 2K NVIDIA/vLLM/ssh",
      "docs/decision_log.md §D-057 stable reason vocabulary"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "This is a pre-live-promotion gate, not ordinary deferred-roadmap work: fold it into P2-005 before the first claim-bearing NVIDIA run. Its new governed exclusion reason requires a versioned D-057 amendment, which the current scope omits."
  },
  {
    "work_order": "WO-038",
    "collides_with": [
      "docs/contracts/adapter_contracts.md §Transport Adapter",
      "TASK_QUEUE.md §Current Queue P2-016(b)",
      "TASK_QUEUE.md §Current Queue P2-005",
      "TASK_QUEUE.md §Current Do-Not-Do-Yet List Phase-3 data/live-split fences"
    ],
    "kind": "supersedes",
    "required_supersession_line": true,
    "note": "Deletion or deprecation of run_command/collect_artifact changes the public transport contract. Keep shelved until the multi-node decision, re-baseline after WO-001/WO-010, and back-annotate the adapter contract."
  },
  {
    "work_order": "WO-039",
    "collides_with": [
      "docs/decision_log.md §D-051",
      "docs/specs/advisor_status_site_analysis.md §Gap 3 Advisor ask, §Gap 4 Evidence ranking, §Gap 5 Claims/gates and §Gap 6 Campaign readiness",
      "TASK_QUEUE.md §Current Queue SITE-02",
      "docs/decision_log.md §D-060"
    ],
    "kind": "contradicts",
    "required_supersession_line": true,
    "note": "Removing queue, quiet-window, external-ask, risk, and doc-state payloads re-decides D-051's intended live advisor view even if the current browser does not consume them. It must follow SITE-02 and requires a dated D-051 amendment or a retained compatibility endpoint."
  },
  {
    "work_order": "WO-040",
    "collides_with": [
      "docs/specs/c027/rpt-001_report_vertical_slice.md §3.1 absolute-path prohibition and §6.1 Commands"
    ],
    "kind": "extends",
    "required_supersession_line": false,
    "note": "It mechanically enforces existing repository-relative and source-only check requirements; no publication or privacy authority changes."
  }
]
```
BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Mapped all 40 accepted work orders at HEAD 3b507c795a520266046dd4956349d70e73a3e7ab. Adoption blockers are the missing R3 authority for WO-002, incomplete D-043 closure scope for WO-005/WO-014, unresolved publication descope in WO-017, unnamed D-017/D-063/D-057/D-051 re-decisions in WO-019/WO-021/WO-037/WO-039, and deferred WO-037 being incorrectly sequenced after the live-promotion gate it must protect.","pathspec":[],"verification":["Parsed all 40 row_type=work_order records with jq: 28 planned, 7 deferred-roadmap, 4 landed, 1 landed-with-residual","Inspected TASK_QUEUE Current Queue, generated lane rows, Do-Not-Do-Yet fences, AGENT_PLAN authority map, relevant contracts/specs/checklists, and D-005/D-006/D-009/D-011/D-017/D-023/D-030/D-043-D-065 decision entries","Confirmed packets/ed-rulings.json contains no R3 despite WO-002 citing it","git status/read-only inspection: pre-existing untracked docs/reviews/2026-07-13-comprehensive-audit/packets/fable-court-holdings.json; no edits made"],"flags":["no_edits","adoption_blockers","missing_R3","supersession_closure_required"]}