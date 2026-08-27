# Sol seat — smoke corpus path (gpt-5.6-sol xhigh, read-only; relayed by the codex director). Verbatim.

Sol thread id: `01a0423e-a537-7940-b067-9126bc5b616b` (xhigh, read-only sandbox, no edits). Envelope validated: single final `BRIDGE_REPORT_V1` sentinel, well-formed JSON, status `DISCUSSION`. Sol's answer verbatim follows.

## Positions

(a) Claim consumption is a conjunction:

- Bundle: safe directory; valid `config.json`, `metadata.json`, `events.jsonl`, `summary_metrics.json`, trace/suite evidence; authenticated config hash; succeeded positive measured window with ≥2 samples; supported reducer; exact raw re-reduction; valid workload/output, uncertainty, raw-to-trace, and rich-telemetry evidence (`joulewise/bundle_read.py:741-800`; `joulewise/cli.py:392-412,488-584,1219-1425`). `RunBundleWriter`, controller, runtime/telemetry adapters, and reducer write these (`joulewise/bundle.py:925-965,1167-1195`; `joulewise/controller.py:1433-1444,1609-1625,2056-2163`).
- Custody/admission: launch lineage and source provenance authenticate; config typed identity, normalized bytes, realized runtime/telemetry/device/model identity, and manifest config all agree; telemetry config/metadata/summary triangle agrees; status succeeds; telemetry is non-mock (`joulewise/analysis_engine/inputs.py:2667-2755`; `joulewise/whole_window.py:973-1066`). Thus line 2753 excludes mock before estimation.
- Member/campaign: finite selected metric; current reducer wire; no environment, cleanup, capture-pipeline, anchor, or precheck refusal; `window_evidence_precheck.eligible=true` with empty reasons; verified cooldown is uniquely joined from authenticated campaign manifests/log and either first-run-exempt or raw-hash-verified recovered—not cap-hit (`scripts/run_campaign.py:5837-5935`; `joulewise/analysis_engine/inputs.py:2106-2121,2197-2234,2327-2368,3398-3479`). `run_campaign` writes those campaign/cooldown records.
- Global readiness: usable collection, exact fixed-N paired/ABBA completeness; whole-window environment/CPU admission, adapter continuity, NEG-8 bracket, and instrument-calibration bracket all pass (`scripts/run_campaign.py:5977-6074,6077-6113`).
- Floor/finalization: finalized manifest binds the exact valid floor bytes; declared evidence roots resolve; every floor member is strict, succeeded, non-mock, bounded-anchor; complete-bundle/config/metric/scientific/stack hashes and calibration plan/ABBA labels/order match (`joulewise/analysis_engine/inputs.py:827-927,1563-1613,1831-1938`). Floor extraction/mint tools write the artifact; finalizer attaches it.

(b) Tier-2 is the minimal honest direction, but it is not CLI-reachable: normal resolution hardcodes `PowermetricsTelemetryAdapter(clock)` (`joulewise/adapters/__init__.py:153-170`). The cited test actually uses a specialized registry, `CampaignPositiveTelemetryAdapter`, fixture clock, environment patch, and synthetic calibration—not merely the base adapter plus canned plist (`tests/test_p2038_production_path.py:258-330,402-452`). It proves strict validity, complete `uncertainty_evidence`, and a locally eligible gross-request bracket (`:474-580`), not cooldown, whole-window bracket, floor binding, or final `analyze_claims`.

(c) None. The closest real-writer test stops at that member proof. The synthetic analysis "end-to-end" patches authenticated consumption and disables strict validation (`tests/test_analysis_integration.py:528-539,565-584`).

## Disagreements

The forcing problem's shorthand overstates the existing replay seam. Generic fixture replay is not demonstrated claim-consumable; the positive test depends on additional specialized seams.

## Open questions

Only execution can establish exact smoke-pack hashes, cooldown joins, all bracket evidence, floor applicability, and a wholly DATA verdict. Also, `--bracket-binding` still lacks a producer (ruling addendum lines 129-132).

## Recommendation

No current path yields a claim-consumable synthetic bundle without production changes. Choose tier-2: add one authenticated-plan-tree, `generation_kind=pipeline_smoke`-only replay adapter option, hard-pinned to the fixture executable/prefix, plus BRACKET-BINDING-CLI-01; then run one real collector→finalizer→claim-edge test. Estimate: 2 Sol-days. Do not touch frozen packs or any `_v4` changed-set file. The strongest objection is that fixture clock/idle/environment specialization may create another replay-only success path unless every join above is asserted. Unit B's class refusal is correctly placed (`9b3dab83:joulewise/arm_readiness.py:3906-3915`).

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Recommend a fail-closed pipeline_smoke-only tier-2 replay seam plus the missing bracket-binding producer; no existing synthetic path satisfies every claim-admission predicate.","pathspec":[],"verification":["Confirmed HEAD e2d63571f19903f6f7b7cb13d43a107aa3b7d643 and clean main worktree","Inspected admission, validator, telemetry, cooldown, floor, finalization, CLI, tests, and main...9b3dab83 diff read-only"],"flags":["no_edits","tests_not_run_read_only_consult","production_change_required"]}
