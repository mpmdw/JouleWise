## Positions

1. No D-066..D-070 outcome contradicts standing authority outside D-066’s scoped override. D-060, D-053, D-058, and the reducer freeze are all preserved or expressly overridden within scope; the audit gate, Window A order, quiet-machine ownership, legacy arms, and claim ceilings remain intact.

2. D-067 satisfies all four Ed amendments:

   - reporting-not-recording and mandatory dual-basis capture;
   - accurate attribution of Rivoire’s energy-proportionality argument;
   - revisit at P1-003/Q6 boundary sensitivity;
   - concrete Lakebed/status wording task with every number basis-labeled.

3. D-070’s mappings to the five architectural axes are substantively accurate. Its request-scoped schema does not inherently conflict with D-058 or require re-dispatching existing bundles if it applies only to a new schema/reducer version and places `request_id` inside event `metadata`.

4. D-032 reinforces D-067: `phase_energy_j` is already gross-only. D-067 should explicitly say dual-basis capture refers to request-level metrics; it does not introduce idle-subtracted phase maps.

5. Remaining tracked deploy/regeneration instructions:

- `docs/orchestration.md`
- `docs/reviews/2026-07-13-comprehensive-audit/CHECKPOINT.md`
- `docs/run_reports/2026-07-13-bridge-v11.md`
- `docs/specs/advisor_status_site_analysis.md`
- `docs/specs/suite_next/next_observer_spec.md`
- `docs/site/run_state.html`
- `docs/site/orchestration.html`
- `site_capsule/AGENTS.md`
- `site_capsule/CLAUDE.md`
- `site_capsule/README.md`

## Disagreements

- D-067 reverses `docs/contracts/token_normalization.md`’s binding “Primary Metric” clause, which still defines headline request energy as idle-subtracted. This reversal is authorized by D-066, but D-067 should explicitly supersede that clause and assign its contract alignment separately from S-0. Otherwise D-069’s statement that S-0 “touches no contract” is inaccurate.

- “Dual-basis capture stays mandatory in every bundle” is stronger than current contract language:

  - `measurement_methodology.md`: report both “when possible.”
  - `run_bundle_layout.md`: `idle_subtracted_energy_j` may be null for successful bundles and metrics are optional/nullable for failed or unsupported bundles.

  Ed’s outcome stands, but the applicable bundle states or exceptions need definition and contract reconciliation.

- The deployment convention is misattributed. C-012 records the site-observatory/image-review stream; C-013 records deployment and folding regen+redeploy into the end-of-work loop.

- D-070 mixes two source homes. The C5 rows are in `docs/research_question_bank.md`, while `C-023-*` and `RQ-*` canonical rows are in `docs/research_question_registry.md` under D-055. The axis mappings themselves are accurate.

- `C-023-IDLE-STATIONARITY` does not contain an open headline-basis question; it imposes idle-model sensitivity on idle-subtracted conclusions. D-067 closes headline-basis selection while leaving that constraint active.

- D-066 accurately cites D-053 as the analysis-registry predeclaration freeze, but D-053 is not a general contract freeze.

- D-064 index hygiene:

  - The new top index row omits “per-session” and “canonical” from the entry title.
  - The old inline `## Index row` now duplicates the top index.
  - D-067 has only a punctuation-level title mismatch (`:` versus `—`).
  - Other titles and accepted statuses match.

- No C-033 entry currently exists outside these drafts. “C-033 coherence-reviewed” is therefore premature until this review is adjudicated and recorded.

## Open questions

- D-070 should pin `request_id` to `events.jsonl.metadata.request_id`. A sixth top-level key would contradict the exact five-key event contract.

- The new reducer version must group lifecycle and phase windows by `request_id`; the current reader pairs phase windows globally by phase name. This is additive work, not a legacy-bundle migration.

- The lead should define whether “every bundle” means every successfully measured, idle-eligible bundle or literally failed/unsupported bundles as well.

## Recommendation

Accept the five Ed-directed outcomes, but correct the provenance and contract-coherence defects before treating C-033 as closed:

1. Name D-032 and preserve gross-only phase semantics in D-067.
2. Explicitly supersede the D-058 Primary Metric clause and reconcile nullable dual-basis rules.
3. Attribute the deploy convention to C-013.
4. Correct the registry source homes.
5. Pin `request_id` to metadata and new-version dispatch.
6. Clean D-064’s duplicate/mismatched index row and defer the C-033 completion claim until recorded.

Verification was read-only: targeted authority/contract/registry searches, deploy-reference sweep, workspace-status confirmation, and `git diff --check` passed. No files were changed.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Coherence review complete: outcomes are authorized, with contract-alignment, citation, deploy-pointer, schema-location, and index-hygiene corrections identified before C-033 closure.","pathspec":[],"verification":["git status --short: expected three dirty paths only","targeted decision/contract/registry/deploy-reference review: complete","git diff --check: PASS"],"flags":["no_edits"]}