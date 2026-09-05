```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Six queued phase-2 rows were traced: two remain physical executions and four should retire rather than create or duplicate machinery.",
  "workspace": {"base_requested":null,"base_mode":null,"head_start":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","head_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","upstream_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","branch":"feat/2026-09-04-fan-p2-rows"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/p2-rows/01-sol-report.md"],
  "unowned_dirty": [],
  "verdict": {"implementation":"no_change","acceptance":"ready"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"python3 -m unittest tests.test_envelope_gate tests.test_load_transition_alignment","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 37 tests in 17.809s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 37 tests in .*s\\n\\nOK"}},
    {"id":"V2","kind":"test","cmd":"python3 -m unittest tests.test_controller.SamplingWindowTests.test_marker_events_bracket_the_runtime_events tests.test_controller.SamplingWindowTests.test_stop_marker_is_stamped_before_alignment_capture tests.test_controller.SamplingWindowTests.test_post_window_dwell_changes_tail_support_without_moving_marker","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 1.288s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 3 tests in .*s\\n\\nOK"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest tests.test_run_campaign.RunCampaignTests.test_current_era_claim_eligibility_only_never_becomes_ready tests.test_run_campaign.RunCampaignTests.test_axi_restart_after_quarantined_attempt_cannot_reuse_first_run_exemption tests.test_run_campaign.RunCampaignTests.test_fresh_cooldown_raw_provenance_is_reverified_at_verdict_time tests.test_run_campaign.RunCampaignTests.test_all_members_cannot_claim_one_session_first_run_exemption tests.test_analysis_claims.InputSeamTests.test_cooldown_disposition_matches_controller_over_boolean_grid tests.test_analysis_integration.AnalysisIntegrationTests.test_unregistered_matching_topup_demotes_but_preserves_fixed_n_analysis","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 6 tests in 11.582s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 6 tests in .*s\\n\\nOK"}},
    {"id":"V4","kind":"test","cmd":"python3 -m unittest tests.test_publication_privacy tests.test_package_bundle_pack","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 26 tests in 4.242s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 26 tests in .*s\\n\\nOK"}}
  ],
  "flags": [
    {"id":"F1","kind":"lead_ruling","level":"nonblocking","text":"The retirement recommendations require the magistrate to amend the protected task registry; this session did not edit that registry.","needs":"Adjudicate P2-027, P2-035, P2-047A, and P2-050, then update docs/process/state_kernel.json and regenerate its projections."},
    {"id":"F2","kind":"environment","level":"nonblocking","text":"P2-010 and P2-046B require quiet-machine physical execution, which an active agent session may not perform.","needs":"Schedule each in a clean, lead-controlled quiet-machine window if retained."}
  ]
}
```

## Change

No production or test code changed. The review found no unsettled mechanical
gap that could be implemented without either duplicating later code or choosing
new scientific semantics. The disposition table is the requested harvest
artifact.

An **ABBA design** runs conditions in the order A, B, B, A so that gradual
machine drift is less likely to imitate a condition difference. A **measured
interval** is the time span whose sampled power is integrated into energy.

| Registry row | Disposition | Evidence and reason | Magistrate action |
|---|---|---|---|
| `P2-010` | **Implement in the quiet-machine lane; software already exists.** | The registry asks for the remaining affine-ladder smoke campaign and the envelope-gate verdict. The generator and analyzer are already present in `joulewise/workloads.py` and `joulewise/envelope_gate.py`; AP-5 still requires the envelope-validation smoke gate before a scored campaign (`docs/contracts/analysis_plans.md`, AP-5 inclusion rule). This is a physical collection, not an agent-lane code task. | Retain only if the scored affine-ladder result remains a paper consumer; schedule the registered smoke bundles and apply the existing envelope gate. Otherwise retire it together with that consumer. |
| `P2-027` | **Recommend retirement.** | Later authority makes publication and uninvolved-party re-reduction optional owner-directed evidence handoff rather than a completion gate (`TASK_QUEUE.md`, supersession note before the live queue). The public-pack contract also says the privacy projection omits private raw evidence and therefore cannot support the old strict re-reduction claim (`docs/contracts/publication_privacy.md`, Publication boundary). Keeping the row as a normal queued task conflates optional dissemination with reproducibility. | Retire the row. If Ed later elects to publish, open a new release-specific row whose acceptance distinguishes privacy verification from external re-reduction of complete raw evidence. |
| `P2-035` | **Recommend retirement, not implementation.** | The research-question registry still labels sampling-induced energy variance a candidate. Its own design lists five missing supports, including seeded sampling, forced-token execution, a replay manifest, equivalence checking, and floor consumption (`docs/specs/rq_energy_variance_design.md`, Harness support today). The document identifies forced-token execution as the load-bearing missing instrument operation. Implementing it now would require a council promotion and a choice between forcing model outputs and measuring an equivalent scoring path; no ruling chooses that measurement semantics. | Retire the queued implementation row. Reopen only through the registry promotion procedure if this research question acquires a named paper consumer; the promotion must choose the forced-path measurement semantics before code work. |
| `P2-046B` | **Implement in the quiet-machine lane; no agent-lane change is due.** | The frozen Part-A contract explicitly says Part B has not run and that fixture results do not alter the physical interval-support bound (`docs/contracts/load_transition_alignment.md`, status paragraph). Current production still consumes the P2-038 interval-support evidence family in `joulewise/uncertainty_evidence.py` and `scripts/run_campaign.py`, so this row is not already done elsewhere. | If the diagnostic value still justifies a quiet window, execute the frozen manifest and adjudicate whether the existing bound is retained, widened, or replaced. Do not treat this report as physical validation. |
| `P2-047A` | **Recommend retirement.** | The proposed contrast was standard controller capture versus a buffered or minimal-marker path. The current controller already buffers every event and log in memory, writes nothing to disk inside the marker-bounded measured interval, and limits in-window controller work to two marker appends (`joulewise/controller.py`, module contract). A second “buffered” arm therefore has no distinct treatment. A minimal-marker arm would instead change recorded evidence and would require a new contract, not a mechanical implementation of the old row. | Retire P2-047A and its dependent physical-execution row. Any future controller-cost study should begin with a newly adjudicated estimand rather than subtracting an unsupported overhead estimate. |
| `P2-050` | **Recommend retirement after recording the absorbed dispositions.** | Later fail-closed work absorbed most of the umbrella: legacy `claim_eligibility` cannot make a current-era bundle eligible (`joulewise/analysis_engine/inputs.py`, `window_evidence_precheck`); cooldown outcomes are re-derived from authenticated raw terminal rows (`joulewise/cooldown.py` and `scripts/run_campaign.py`); first-run exemption is unique to the physical session and cannot be reused on restart (`scripts/run_campaign.py`); and the analysis engine scans the complete run root for unregistered matching bundles, records top-ups, and demotes affected contrasts (`joulewise/analysis_engine/inputs.py`, `_scan_replacements_and_topups`). Focused regressions cover those paths. The stronger cooldown-trace proposal—full row-shape, adjacency, timestamp, and rolling-decision replay—was explicitly left as an unadjudicated candidate in `docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`; current semantic verification checks the authenticated terminal decision but does not implement that larger design. | Close the umbrella row: record the landed items as already done, the once-per-analysis-manifest alternative as superseded by the physical-session rule, and retire the unadjudicated trace expansion unless a concrete failure creates a new, narrowly specified row. |

The protected live-state files need the dispositions above applied by the
magistrate. This session deliberately did not edit
`docs/process/state_kernel.json`, `TASK_QUEUE.md`, `RUN_STATE.md`, or
`docs/decision_log.md`.

## Verification notes

The repository-wide test suite was intentionally not run. Verification was
limited to the named row mechanisms and the later implementations cited for
the already-satisfied disposition.

## Residual risk

Retiring P2-035 closes a possible future research extension, not an existing
paper result. Retiring P2-047A rests on the present marker-bounded controller
contract; a later controller architecture that performs work inside the
measured interval would justify a newly specified diagnostic. P2-010 and
P2-046B remain unmeasured until a lead-controlled quiet-machine run supplies
physical artifacts.
