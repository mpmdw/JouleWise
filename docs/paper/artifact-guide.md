# JouleWise artifact and repository guide

This is the maintainer-facing companion to the capstone paper. The paper points here for repository vocabulary, path conventions, generated-state checks, freeze receipts, custody operations, and release workflow. Scientific re-derivation—from raw trace through clock anchor, pulse bound, phase energy, floor, and verdict—stays in Appendix A.

## 1. Sources of truth and path conventions

The repository holds code, contracts, plans, and small issued artifacts. Measured run data are deliberately not tracked: `.gitignore` excludes `runs/`, `ci-runs/`, `/runs_window_*`, `/runs_recal*`, and `/runs_char_*`. Never infer that a missing run directory means evidence never existed; custody and release storage are separate from Git.

Use these owners rather than copying their contents into a new document:

- `docs/contracts/run_bundle_layout.md` owns the bundle directory shape, completion marker, immutable raw-artifact rule, calibration custody subtree, and strict-reduction semantics.
- `docs/contracts/characterization_result_schema_v1.md` owns the characterization specification, issued report, evidence bindings, and refusal vocabulary.
- `docs/contracts/powermetrics_fiducial.md` owns the commanded-pulse calibration artifact.
- `docs/contracts/analysis_plans.md` and `docs/contracts/claims_ladder.md` own the fixed-analysis and claim gates.
- `docs/phase_2/window_runbook.md` owns live window operation. Do not extract a second runnable campaign recipe from paper prose.
- `configs/campaign_policies/quiet_mac_p2_production.json` owns the production admission limits.
- `docs/process/state_kernel.json` owns live work-selection state; `RUN_STATE.md` and `TASK_QUEUE.md` contain generated projections of it.
- `docs/paper/results-fill-registry.md` owns every result or release placeholder in the draft.
- `docs/contracts/publication_privacy.md` owns the transformation and authorization boundary for public bundles.

Paths stored inside artifacts must follow the owning schema. Do not rewrite an absolute collection path to look portable, and do not invent a relative substitute: the stored path is evidence of where collection actually ran. Commands that produce replay outputs must write outside immutable input bundles.

## 2. Freeze before collection

Before measured collection, freeze the exact run identifiers, membership, stage order, comparison definitions, calibration retry count, numeric acceptance limits, extraction specification, source revision, and permitted exceptions. Prospective sizing also belongs here: if expected clearance is inadequate, increase independent evidence, change the workload, or narrow the claim before claim data exist. A workload change changes the population being estimated and requires a new plan.

The freeze exists because an earlier criterion was changed on the same day as the data it judged, and no machine-readable record could establish which criterion was prior. Limits therefore live in fingerprinted specifications rather than paper prose or analysis-result files. Editing remains possible, but it creates a successor freeze instead of rewriting the predecessor.

Campaign packs live under `configs/campaigns/`. For example, `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/` contains `plan_tree.json`, `calibration_plan.json`, `order_manifest.json`, condition-family declarations, `analysis_manifest_v3.json`, arm-readiness evidence, and the freeze receipt at `arm_readiness.freeze.receipts/freeze-0003.json`. Extraction specifications live under `configs/floor_mint/`.

Two sidecar names are in use and must be preserved:

- Plan files replace `.json` with `.sha256`, such as `plan_tree.json` and `plan_tree.sha256`.
- Most receipt files append `.sha256`, such as `freeze-0003.json` and `freeze-0003.json.sha256`.

The sidecar body names the file it authenticates, so use the body rather than deriving the subject from the sidecar name. A local check for the example pack is:

```sh
cd configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3
shasum -a 256 -c plan_tree.sha256 calibration_plan.sha256
```

A freeze receipt is append-only. Its evidence rows bind paths, fingerprints, and outcomes; its predecessor block binds the prior receipt and evidence set. A later calibration or plan does not edit an earlier receipt. It issues a successor linked to the predecessor. Never repair a broken historical locator by guessing another path.

## 3. Characterization specification and issuance

The matched schemas `joulewise.characterization_result_spec.v1` and `joulewise.characterization_result.v1` are defined by `docs/contracts/characterization_result_schema_v1.md`. The sole report writer recomputes the specification, contract, predecessor, and evidence fingerprints; a mismatch is a refusal, never a correction. It also rejects any result input that tries to select its own estimator or limit.

The writer applies two ordering gates before evaluating a criterion. The criteria freeze must issue strictly before every admitted member capture, and a borrowed limit must come from a supplier with an earlier freeze ordinal than the freeze that borrows it. Failure of either gate is protocol failure and emits no report. Evidence that built an allowance cannot also be the held-out evidence used to test that allowance.

Specifications and reports use canonical JSON: UTF-8, sorted object keys, two-space indentation, one trailing newline, duplicate keys refused, and no non-finite numbers. Preserve the canonical bytes because their fingerprint is the artifact identity; do not parse and reserialize a historical artifact with local defaults.

## 4. Calibration editions and capture eras

Calibration-acceptance editions are retained side by side under `configs/calibration/`:

- `calibration_acceptance_d079_v2.json`
- `calibration_acceptance_d079_v2_r2.json`
- `calibration_acceptance_d079_v2_n17_r3.json`
- `calibration_acceptance_d079_v2_n17_r4.json`
- `calibration_acceptance_d079_v2_n17_r5.json`
- `calibration_acceptance_d079_v2_n17_r6.json`

`joulewise/calibration_bracketing.py` registers each edition's operative bracket screen and never-zero allowance. An unknown edition or a supplied value that disagrees with the registry refuses. A source-byte change requires a successor edition. If the change is declared science-neutral, replay the entire governed corpus and reproduce every bound, decision, and evaluation count before recording that conclusion.

Every bundle also carries a schema version and clock-anchor method. `joulewise/uncertainty_evidence.py` maps registered methods to schema eras and distinguishes two failures: `capture_pipeline_absent` for missing current presentation and `capture_pipeline_superseded` for a recorded retired method. Strict replay uses the method named by the bundle, preserving old evidence as auditable. Claim admission is narrower and requires a method in `CLAIM_BEARING_ANCHOR_METHODS`. Never migrate an old bundle by editing its method label.

## 5. Bundle custody, failures, and replacements

The bundle at `<runs root>/<run id>/` is written once. `summary_metrics.json` is the completion marker; an absent or invalid marker means incomplete collection, not a successful member with missing results. Native artifacts under `raw/` are the source of truth. For powermetrics, preserve `raw/powermetrics.plist` even when derived `power_trace.csv` and rich telemetry exist.

If `metadata.instrument_calibration` is present, preserve the complete `instrument_calibration/` subtree: `manifest.json`, `instrument_evidence.json`, `events.jsonl`, and `raw/powermetrics.plist`. It is custody, not a reconstructable cache.

A failed or interrupted occurrence is never deleted or overwritten. For a governed retry:

1. Stop at the first member failure and retain the occupied directory.
2. Move that occurrence to the window's declared quarantine root outside the active runs root.
3. Record supersession before using the replacement as current:

```sh
python3 scripts/run_campaign.py --runs-dir <runs root> \
  --record-supersession <bundle id> \
  --quarantine-path <quarantined bundle path> --reason <recorded reason>
```

4. Write the retry into a new active slot.

The recorder requires both `--quarantine-path` and `--reason`. Two present bundles claiming the same occurrence are a refusal, never an invitation to choose one. After a stage's third failure from the same cause, close the window under D-087; do not interpret the rule as closing only that stage. Preserve the salvage corpus and its refusal.

The whole-window verdict appends to `<runs root>/campaign_log.jsonl` or to the explicit external `--log`. It binds the declared membership, source manifests, replacements, exclusions, calibration bracket, policy, drift evidence, and evaluation basis. Re-evaluation appends a new row and never overwrites the earlier verdict.

## 6. Extraction, issuance, and claim consumption

Use `scripts/extract_detection_floors.py` with the frozen extraction specification and complete whole-window binding. Exit `0` means every cell extracted; exit `1` means the report was written with recorded refusals; exit `2` means process input was invalid and no report was written. Do not turn exit `1` into a generic CI failure without preserving its scientific meaning.

A floor or claim result is not self-authorizing. The full chain is:

```text
frozen plan and policy
  -> immutable bundles and calibration custody
  -> whole-window verdict and evaluation basis
  -> detection-floor extraction report
  -> issued floor artifact
  -> analysis manifest and claim verdict
```

At claim consumption, check the registered `FLOOR-BIND-01` row in `docs/process/state_kernel.json`. While its claim-side limitation remains open, do not describe a standalone floor artifact as independently authenticating complete extraction evidence. The paper's Appendix A therefore conditions claim replay on closure of that row.

The claim-side bound printed in the paper is `deterministic_bounds.total`. `E_clock_anchor_shift_bound_j` is only one term. Do not substitute it into tables, templates, or release metadata.

## 7. Repository checks moved out of the paper

These checks maintain repository consistency; they do not re-derive a scientific number and therefore belong here.

**Generated state.** Edit `docs/process/state_kernel.json`, then render its projections:

```sh
python3 scripts/gen_state.py
python3 scripts/gen_state.py --check
```

Do not hand-edit text between generated markers in `RUN_STATE.md` or `TASK_QUEUE.md`. CI runs the `--check` form in `.github/workflows/ci.yml`; exit `0` is exact agreement, `1` is drift, and `2` is an invalid source or missing marker.

**Freeze-receipt history.** Verify published receipt chains from local Git objects:

```sh
python3 scripts/verify_receipt_histsem.py \
  --repository-root . --require-published
```

This requires full Git history. CI runs this command. A depth-limited clone may fail because it lacks the pinned source objects, not because a scientific artifact changed.

**Assembled RPT-001 report.** When changing that report's inputs, verify its generated page, inclusions, and artifact fingerprints without network access:

```sh
python3 scripts/build_capstone.py --profile rpt001 --offline --check
```

This check concerns assembled-report state; it is not a substitute for replaying measured evidence.

**Canonical tests.** For code changes, run:

```sh
python3 -m unittest discover -s tests
```

Tests are development verification. They are not part of the scientist's evidence replay in Appendix A.

## 8. Release workflow and current availability

`docs/paper/results-fill-registry.md` row DS-34 is the single release-locator hold. Its status is `STOP_FILL` / `SUPPLIER_UNKNOWN` until the release checklist issues the repository revision, archive locator, and published digest manifest. Do not add a second placeholder or fill DS-34 from an internal path.

Before publication, follow `docs/contracts/publication_privacy.md`: a private strict-valid bundle is not copied verbatim into a public pack, and the privacy projection does not itself authorize upload, tagging, release, or external messaging. The release manifest must pair every public path with its fingerprint and must provide every concrete argument used by Appendix A's evidence-dependent commands. Missing consumption semantics, custody-store paths, membership bindings, evaluation-basis fingerprints, floor artifacts, or manifests are release blockers; they are never repaired by selecting a nearby repository file.

Until DS-34 issues and `FLOOR-BIND-01` closes on the claim side, describe the demonstration chain as designed for independent reanalysis, not as presently open and independently re-reducible. Release does not close the separate scientific limitation that pulse-derived timing bounds are transported to sustained mixed inference load without a workload-shaped transfer test.
