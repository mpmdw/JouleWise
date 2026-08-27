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

### Pulse-projection deadline

Run one complete multi-pulse accepted-region projection—the search that encloses every pulse-edge lag pair permitted by the fit's loss limit—with the frozen default work limits. The primary reproducible limit is 165,000 evaluated cells (`joulewise/powermetrics_fiducial.py:77-88`). The code calls the second limit the “FROZEN supplementary host-safety deadline” and fixes it at 120.0 s; it “only catches unexpected per-cell cost or host pathologies that a cell count cannot bound” (`joulewise/powermetrics_fiducial.py:89-92`). One cell counter and one monotonic-clock deadline are shared across every pulse in the detection attempt. Before evaluating another cell, the detector checks the cell limit first and then the 120 s deadline (`joulewise/powermetrics_fiducial.py:524-550`). If either limit is exhausted, discard every partial pulse fit and issue invalid evidence with `detection_nonconvergent`, no fitted pulses, and no `b_fiducial_s`; never retain a truncated accepted region as a calibration result (`joulewise/powermetrics_fiducial.py:976-1010`).

### Reference repeatability and whole-window drift allowance

Build the reference-repeatability bound separately for gross request energy and idle-subtracted request energy. Start from a settled, same-condition reference corpus with at least ten members; the mint rejects an unsettled manifest, too few members, unsafe or duplicate paths, non-current reductions, and mixed scientific configurations (`joulewise/whole_window.py:3373-3454`). The code fixes the corpus minimum at \(n_c=10\), the replicated endpoint count at three, and the freshness horizon at 86,400 s (`joulewise/whole_window.py:90-104`). For one claim family, sort the corpus point energies as \(C_{(1)}\leq\cdots\leq C_{(n_c)}\), compute their sample standard deviation \(s_c\), and let \(t_{0.975,n_c-1}\) be the Student-\(t\) critical value used by the implementation. Then compute

\[
R_c=\max\!\left(
\frac{C_{(n_c)}+C_{(n_c-1)}+C_{(n_c-2)}}{3}
-\frac{C_{(1)}+C_{(2)}+C_{(3)}}{3},
\ t_{0.975,n_c-1}s_c\sqrt{2/3}
\right).
\]

This is the code's `replicated_endpoint_bound_j`: the larger of the mean of the largest three minus the mean of the smallest three and the two-endpoint-means prediction term (`joulewise/whole_window.py:1430-1477`). The artifact builder evaluates that construction independently for the gross and idle-subtracted families (`joulewise/whole_window.py:1480-1492`). A current window must supply exactly three start references, one midpoint reference, and three end references for both families (`joulewise/whole_window.py:1859-1888`).

For each family, let \(S\) be the mean of its three start points, \(M\) its midpoint point, and \(E\) the mean of its three end points. Compute the endpoint screen statistic \(|E-S|\), the trajectory excursion

\[
X=\max(S,M,E)-\min(S,M,E),
\]

and the never-zero whole-window allowance

\[
A_{\mathrm{drift}}=\max(X,R_c).
\]

The endpoint screen passes only when \(|E-S|\leq R_c\), while the allowance uses the larger three-point excursion \(X\), so the midpoint can expose an interior excursion hidden by similar endpoints (`joulewise/whole_window.py:1752-1803`). Perform the complete calculation separately for the gross and idle-subtracted families (`joulewise/whole_window.py:1921-1938`). Apply no duration multiplier: the implementation records `not_applied_no_governed_time_law` (`joulewise/whole_window.py:1797-1803`). Refuse a claim-time use when the bound is older than 86,400 s or when the observed operating-system build, power-supply identity, or calibration identity differs from the artifact bindings (`joulewise/whole_window.py:1245-1344`).

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

The paper's Table 3 claim-side bound has NO supplier yet; the registry holds that column unresolved and it renders only after the prospective campaign. Do not bind it to `deterministic_bounds.total`: that quantity widens the decision interval, but the registry's own rule forbids assuming it is identical to the template's clock-anchor claim-side term, and `scripts/render_results_fills.py:977` enforces that. `E_clock_anchor_shift_bound_j` is one term inside `deterministic_bounds.terms[]` and is likewise not the column.

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

## 9. Calibration algorithm operator detail

Appendix A of the paper carries the calibration mechanism a scientist needs to rebuild a number.
This section carries the operator and maintainer detail that would not help that rebuild: the exact
refusal vocabulary, the admission enumeration, grid point counts and tie-breaks, the branch-and-bound
traversal order, work-budget constants and exhaustion behaviour, record shapes, and event-pairing
mechanics. The paper points here rather than carrying it. Repository vocabulary is used freely below.

**Inputs and their admission checks (each failure returns `clock_anchor_unresolved` with the detail named in parentheses).** All five stamps must be present (`clock_stamp_unavailable`); each must be finite with *mb* ≤ *ma* and non-negative resolutions, and their *mb* values must be non-decreasing in the order S_pre, S_parse, S_start, S_stop, S_post (`clock_stamp_invalid`). Records must exist (`native_records_unavailable`), each with integer *e_i* > 0 and integer *n_i* (`native_exact_inputs_unavailable`), *n_i* a whole second (`native_label_not_whole_second`), positive finite elapsed and finite label (`native_record_malformed`), `is_delta` true (`native_record_not_delta_aggregate`), finite energy (`native_energy_counter_unavailable`), and the *p_i*/*E_i* agreement of A.3.1 (`native_energy_power_inconsistent`). Labels must be non-decreasing (`native_timestamps_non_monotone`); a label jump between consecutive records of more than the *later* record's *e_i* + 1 s is a gap (`native_rollover_anomalous`); at least two label increases must occur (`no_native_second_rollover` if none, `native_rollover_anomalous` if one). Let *q_last* be the cumulative elapsed time *q_i* of the final record, i.e. the instrument's own count of the whole capture after record 0. It must be at least 60 s (`clock_fit_span_insufficient`), and the controller's own coverage *ma*(S_post) − *mb*(S_pre) must be at least *q_last* (same detail).

**Step 7 of the A.3.3 solver sequence — diagnostic only.** Bisect *δ* over [0, 250 µs] for 24 steps to find the smallest allowance at which the full set is still feasible; report the upper end as `min_l_infinity_residual_upper_bound_s` (1.49·10⁻¹¹ s on the example: the labels fit the affine model essentially exactly). This value does not enter the bound.

**Reading the pulses.** `events.jsonl` is scanned for the four command event types: `warmup_command_on`, `warmup_command_off`, `pulse_command_on`, and `pulse_command_off`. An `_on` event opens a pending pulse of its kind (warm-up or measured); the following `_off` event of the same kind closes it, and its wall time must be strictly later than the on-stamp's. The pulse is stored as (*on*, *off*, *u_on*, *u_off*) from the two stamps as defined in A.3.1. Unpaired, ambiguous, or missing stamps are refused. There must be exactly 3 warm-ups and exactly 59 measured pulses.

   For the coarse step *N* = 150, so before clipping the grid has 301 points spanning *c* ± 0.75 s; for the fine step *N* = 1500 and 3001 points. The clip to |*d*| ≤ 0.75 s is applied after generation, so a grid centred away from zero is one-sided at the clipped end. Worked example: at the start, G(0, 0.005) = {−0.750, −0.745, …, −0.005, 0, 0.005, …, 0.745, 0.750} (301 values). If the onset search then lands at *d_on* = 0.015, the next onset grid is G(0.015, 0.005) = {0.015 + 0.005*k* : *k* = −150 … 150} = {−0.735, −0.730, …, 0.760, 0.765} clipped to {−0.735, …, 0.745, 0.750} (298 values). The fine grid around the same centre is G(0.015, 0.0005) = {0.015 + 0.0005*k* : *k* = −1500 … 1500}, likewise clipped at +0.750 (2971 values, from −0.735 to 0.750).

   Eight one-dimensional searches in all (onset, offset, onset, offset at the coarse step; the same four at the fine step). Ties in the argmin resolve to the smallest (most negative) candidate, because candidates are evaluated in increasing order and the first minimum is kept. Let *Loss** = Loss(*d_on*, *d_off*) at the end. Example (pulse 0, same earlier anchor as above): *d_on* = 0.016 s, *d_off* = −0.011 s.

The pulse's record is then (*j*, detected = true, reasons = none, *a*, SNR, *d_on*, *d_off*, on_lo, on_hi, off_lo, off_hi). A pulse rejected at any step above is recorded as (*j*, detected = false, the rejection reasons — one or two, since the amplitude and SNR tests are evaluated together and both can fire) with no region limits; *a* and SNR are included when they were computed before the rejection, and *d_on*, *d_off* only for a shift-limit rejection.

The branch-and-bound of A.3.5 must terminate on a flat loss surface without exploring hundreds of millions of cells. One **shared budget** governs all 59 pulses of a detection: at most 165 000 evaluated cells (`DETECTION_PROJECTION_CELL_BUDGET`; the example capture used 122 859), and at most 120 s of wall time (`DETECTION_PROJECTION_WALL_BUDGET_S`). Each cell popped from the stack consumes one unit *before* its lower bound is evaluated, and the cell check is made before the wall check so that an input reaching the exact cell limit always receives the same disposition. The 120 s limit is a *pre-cell deadline*: it is tested only at the moment a cell is popped, so the last cell evaluated may run past the 120 s mark; it is not a continuously enforced cap.

If either limit is reached, every partial fit is discarded and the detection is recorded as `detection_nonconvergent` with no bound: exhausted work is one invalid detection, never a truncated region. A wall-clock stop is host-dependent, so its trigger and cell count are recorded as non-reproducible diagnostics; a cell-count stop is reproducible.

The traversal order does not change the retained region on a completed run, but it determines which cells have been evaluated when the shared work budget of A.3.7 is reached, and it is what makes the evaluated-cell count reproducible.

## 10. Evidence index for the appendix calibration material

Every equation, constant and rule in the paper's Appendix A section A.3 was derived from the code by a
seat that did not read the prose it replaced. This is that derivation's evidence index, kept in the
repository rather than in the paper. `pf` abbreviates `joulewise/powermetrics_fiducial.py` and `ue`
abbreviates `joulewise/uncertainty_evidence.py`.

### 10.1 Evidence index

Paths are relative to the repository root. `pf` = `joulewise/powermetrics_fiducial.py`; `ue` = `joulewise/uncertainty_evidence.py`; `pm` = `joulewise/adapters/powermetrics.py`; `vs` = `scripts/validate_powermetrics_fiducial.py`; `clk` = `joulewise/clock.py`.

A.3.1 objects
- Samplers string and rail manifest: pm:57–58. Sampling interval 100 ms: pf:66.
- Record fields `elapsed_ns`, `timestamp`, processor powers (mW → W by /1000), energy counters (int mJ), `is_delta`: pm:1775, 1791–1799, 1820–1830.
- Whole-second label semantics (labels END of window; quantised): ue:78–85; whole-second refusal: ue:909–912.
- Combined power p_i = sum of the three per-rail watts: pm:1805 (`sum(rail_power_w.values())`), projected as `power_w` at pm:1853.
- Record energy E_i = fsum of three mJ counters / 1000: pm:1845–1848.
- Energy/power consistency check and tolerances 0.002 J abs, 0.001 rel: ue:65–66, 933–940.
- Worked-example record 0 values (e_0 = 111242541 ns, powers, counters): parsed from the retained capture `/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/raw/powermetrics.plist` (sha256 b55f3471…9ef, recorded in `docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json`).
- Cumulative elapsed q_0 = 0, q_i = Σ_{1..i} e: ue:972–975.
- ClockStamp fields and how a stamp is taken (monotonic, wall, monotonic): clk:19–27, 58–72. Resolution r = max(wall, monotonic): pf:1074–1076; ue:1032–1034.
- Half-width u(S) = (ma − mb)/2 + r: pf:1067–1081 (strict path, pf:1189–1191).
- Stamp resolution values on the example capture: `instrument_evidence.json` of the retained capture, `clock_anchor.clock_stamps`.
- Trace interval [t_i − e_i/1e9, t_i) with gpu_power: pf:1253–1260; vs:2088–2092. Primary rail `gpu_power`: pf:69.
- CommandedPulse (on, off, u_on, u_off): pf:457–464; construction from stamps pf:1233–1240; vs:2024–2031.

A.3.2 capture procedure
- Protocol id v3: pf:45. Pulse count 59, warm-ups 3, duration 1.0, gap base 1.5, baseline 5.0: pf:61–65.
- Stamp sequence pre_spawn → spawn → first_parse → rollover wait → sampling_started → 5 s → warm-ups (1 s work, 1.5 s rest, stamped and logged) → 5 s → pulse loop → 5 s → sampling_stopped → terminate → post_parse: vs:1883–2040. Rollover gate: vs:1051–1079 (adapter equivalent pm:1585–1661).
- Pulse loop origin is a monotonic reading after the second 5 s rest, not sampling_started: vs:1981–1989, 2002–2005.
- Schedule: pf:381–398 (on_0 = start, off = on + 1.0, next on = off + gap(index), index from 1); gap = 1.5 + vdC_2(index): pf:370–378; van der Corput: pf:355–367. Rationale (no phase lock): pf:373–375.
- Workload 4096×4096 float16 fenced matmul on preallocated buffers: pf:67–68, 1554–1585.
- Event types and stamps in `events.jsonl`: vs:1947–1949, 1960–1962, 2007–2009, 2020–2022. Stamp name set: ue:67–73; assembled at vs:2049–2057.
- Primary bytes hashed (SHA-256 computed over the raw bytes): vs:629–630, 1132–1140; digest-format requirement on the evidence: pf:1419–1424; re-derivation from primary bytes, stored values not inputs: pf:1104–1110.

A.3.3 clock anchor
- Method identity: ue:20; claim-bearing: ue:1298–1299; active capture method: vs:633–637.
- Exact rational arithmetic and outward rounding: ue:682–701, 1223.
- Model condition (affine; 250 µs charged in full; network-time-off admission): ue:826–844; constant ue:37.
- Admission checks and detail strings in order: ue:871–970 (stamps 876–885; records 886–900; whole second 909; health 916–940; monotone 942–948; anomalous 949–955; rollovers 956–970), baseline ≥ 60 s ue:39, 972–982; controller coverage ue:984–995.
- Span definition and 5 ms limit: ue:310–329 (definition), ue:35, 997–1006 (limit). Worked span 0.00044608116149902344: recomputed from the five stamps of the retained capture; equals `wall_minus_monotonic_span_s` in r4-derivation.json.
- Numeric-padding check, 1e-6, 4 ulps, derivation note: ue:42–60, 1008–1025.
- m_0 = mb(S_pre)·1e9: ue:1028. Stamp constraints h_j, g_j: ue:1031–1044.
- Native constraints n − δ ≤ A + βq ≤ n + 1 s + δ: ue:721–737 (rows), ue:1077, 1091–1093.
- k_pre and k_parse definitions: ue:1046–1066; k_pre > k_parse refusal: ue:1067–1068, 782–783. Causal inequality α + βk_pre ≤ A ≤ α + βk_parse: ue:794–811 (rows). k_pre = e_0 − r_pre follows algebraically from ue:1028 and ue:1056–1061 (m_0 cancels); worked values recomputed from the retained stamps and e_0.
- Fourier–Motzkin elimination of α: ue:774–811.
- Box: ue:61, 1078–1090. Solver (exact incremental 2-D LP, fixed seed): ue:622–679; only optimal values are returned: ue:632–634.
- Two rollovers required (MIN_NATIVE_ROLLOVERS = 2): ue:40, 965–970; capture waits for one: pm:1585–1638, vs:1051–1079.
- Gap rule uses the later record's elapsed: ue:949–955 (`exact_elapsed_ns[index]`, index of the later record).
- Refusal sequence: native ue:1094–1097; +stamp ue:1098–1100; joint with 1 s relaxation ue:1101–1112; β range/box/50 ppm ue:38, 1114–1135; A range ue:1137–1139; first-parse lag ue:36, 1141–1161 (envelope LP ue:740–771); residual bisection 24 steps ue:1163–1177, 1205–1207.
- Bound composition H + span + r_max + 1e-6, roundup; point anchor = midpoint via ordinary `float()` (round-to-nearest), limits via outward rounding: ue:41, 1179–1196, 1225–1234; H uses exact rational endpoints (ue:1179–1180) before the endpoints are rounded (ue:1192–1193); printed-endpoint recomputation 0.0006871223449707031 done in this session. Term-by-term pricing: ue:846–862.
- Worked four-term values, A_lo/A_hi, point, rate window, rollovers, records, lag: `docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json` (`anchor_v3` block). Exact decimal sum 0.0011349971959968977402 and roundup to 0.0011349971959968978 verified with `decimal` in this session; the same check appears in `docs/process_traces/2026-08-20-go-session/t19-envelopes/paper-delta.md:73`.

A.3.4 anchoring, trimming, authentication
- Anchored parse: record 0 end = anchor; later records add e_i/1e9 cumulatively in float: pm:1770–1785; pf:1249–1252. Rate-1 forward mapping rationale: ue:851–855.
- Event pairing rules (on opens, off closes, off > on, unpaired/ambiguous refused; exactly 3 + 59): pf:1199–1247.
- Trimming: intervals with start ≥ last warm-up off survive: pf:1084–1092 (`trim_trace_after_pulses`), called with warm-ups pf:1261 and vs:1082–1096, 2094. Warm-ups' rationale and the surviving rests: vs:1085–1093.
- Schedule authentication: durations [0.8, 1.2], gap error ≤ 0.25 vs 1.5 + vdC_2(k), k from 1, 4.5 s quiet before/after: pf:97–100, 401–441; invoked pf:1262–1263.

A.3.5 pulse fit
- Margin 0.75 and overlap test; baseline set O; ≥ 3 intervals: pf:103, 712–729. b = median, σ = max(1.4826·MAD, 1e-3): pf:730–734.
- Spurious plateau: threshold b + max(0.5·10 W, 5σ), runs ≥ 2 (SPURIOUS_MIN_CONSECUTIVE): pf:104, 891–907; invalidates: pf:1011–1017.
- Local set L: pf:745–750. Interior with 0.25 inset: pf:102, 751–756; rejection pf:757–762.
- Amplitude = median(interior) − b; SNR; thresholds 10 W, 10: pf:71–72, 763–779. Amplitude pinned: pf:806–807.
- Edge coverage: pf:780–794.
- Model ŷ = b + a·overlap fraction: pf:5–8 (docstring), 560–566, 569–587. Huber δ = 1.345: pf:101, 553–557.
- Grid G(c, s): pf:707–709 (`count = ceil(half_range/step)`, offsets −count..count), clip |d| ≤ 0.75: pf:812–816, 820–824. N = 150 / 1500 recomputed (0.75/0.005 = 150.0, 0.75/0.0005 = 1500.0).
- Search: steps (0.005, 0.0005), 2 rounds each, onset then offset, argmin via `min` (first minimum wins): pf:73–75, 808–827.
- Significance Loss* < 0.5·Loss_flat: pf:828–839. Shift limit ≥ 0.5 rejects: pf:95, 840–852.
- Tolerance max(1.0, 0.05·Loss*), loss limit = Loss* + tolerance: pf:854–856, 869.
- Cell lower bound (monotonicity, corner predictions, distance, Huber sum): pf:590–633.
- Branch-and-bound: stack from [−0.75, 0.75]², consume cell, discard if LB > limit, retain if max side ≤ 1e-4, bisect wider side (onset on tie), bounding box of retained cells, empty → error: pf:76, 636–704.
- Widening by u_on/u_off: pf:872–875. Output record: pf:876–888.
- Worked pulse-0 numbers (amplitude, SNR, d_on, d_off, regions) and pulse-0 stamp bracket: retained capture `instrument_evidence.json` (`pulses[0]`, `clock_anchor.first_sample_end_point_epoch_s` = 1784757336.5528765 under v2 per `bindings.anchor_method_version`) and `events.jsonl` first `pulse_command_on`; u_on = 1.1250009518116714e-6 recomputed in binary64 from that stamp with pf:1071–1076.
- Traversal order (LIFO `stack.pop()`, lower half pushed then upper): pf:657, 667, 689–696.
- Rejected-pulse record shapes: pf:757–762, 772–779, 788–794, 833–839, 844–852.
- van der Corput general term (digit reversal in base 2): pf:355–367.

A.3.6 bound and validity
- Worst per edge max(|lo|,|hi|), 118 values, B = max + trace_anchor_bound: pf:1022–1043; anchor bound passed in: pf:1264–1271, vs:2093–2100. Median/p95 (ceil(0.95n) − 1 index): pf:1044–1048; diagnostic-only labels pf:1472–1473.
- Validity conjunction including binding fields (ten V2 fields): pf:106–120, 1407–1416, 1435–1445; bound still serialised when invalid: pf:1471; closed reason vocabulary pf:148–167.
- 95/95 statement: pf:11–14.
- Worked B_fiducial_v3 = 0.030067931757111657 and difference 0.0289329345611147592: r4-derivation.json (`b_fiducial_v3_s`) minus `effective_clock_anchor_bound_s`, verified with `decimal`.

A.3.7 budget
- Cell budget 165 000, recalibration note, wall budget 120 s: pf:77–92. Shared across pulses: pf:524–531, 976–979. Consume-before-evaluate and cell-check-before-wall: pf:533–550, 668.
- Pre-cell deadline semantics (checked in `consume_cell` only): pf:533–550.
- Clock origin = `time.monotonic()` at budget construction (pf:530), constructed at pf:976–979 after `_baseline_stats` (pf:975) and before the fit loop (pf:980–991).
- Exhaustion discards all fits, `detection_nonconvergent`: pf:992–1010; reproducibility labelling pf:1525–1545. Example evaluated count 122 859: r4-derivation.json.

### 10.2 Known gaps and caveats

None marked `[[NEEDS-VALUE:]]`. Every number and rule in the prose is traceable to the lines above. Two caveats the reviewer should know, both stated in the prose rather than hidden:

1. The pulse-0 fit values (amplitude 40.6667 W, d_on 0.016, d_off −0.011, the two regions) come from the retained capture's first-issued `instrument_evidence.json`, anchored with the earlier v2 estimator's point (1784757336.5528765). The v3 point used for the paper's bound is 1784757336.5526073, 0.27 ms earlier; the prose now says so in plain words. No refit was run; the four anchor terms and B_fiducial_v3 are taken from the recorded v3 re-derivation (`r4-derivation.json`).
2. The code fixes MIN_NATIVE_ROLLOVERS = 2 and MAX_FIRST_PARSE_LAG_S = 0.25 s without a recorded rationale for those particular numbers; the prose states what each gate tests and its value, and does not invent a justification for the magnitude.
3. The claim that "any exact LP solver returns the same optimal values" is a mathematical property of linear programmes (optimal value is unique), stated to make the estimator replicable without reproducing the Seidel implementation; it is not asserted anywhere in the code.

## 11. Executable verification order

Moved here from Appendix A.4 of the paper (round 6, ruling item 58); the paper keeps a pointer.


First obtain the release manifest. It must supply the repository revision, archive root, bundle identifiers, plan and policy files, drift-bound artifact, whole-window consumption semantics and any custody-store arguments, extraction specification, evaluation-basis fingerprint, floor artifact, and analysis manifest. Do not infer a missing value from a nearby file.

**1. Fix the code and plan bytes.** Check out the exact released revision with full history. Then verify every plan or policy sidecar named by the release, for example:

```sh
shasum -a 256 -c <plan sidecar> <calibration-plan sidecar>
```

A mismatch stops the replay. This establishes byte identity, not whether the scientific criteria passed.

**2. Rebuild each run's trace and phase energies.** Work on a copy of the archive and write the replay outside the immutable bundle:

```sh
python3 -m joulewise.cli validate-bundle --strict <runs root>/<run id>
python3 -m joulewise.cli reduce <runs root>/<run id> \
  --output <replay output>/<run id>.summary.json
```

Strict validation checks the stored `power_trace.csv` against the trace derived from `raw/powermetrics.plist`, then compares `summary_metrics.json` with a fresh reduction of the raw artifacts. The reducer reads the phase start and end times from `events.jsonl`. For interval-supported powermetrics samples it recomputes phase energy as the sum of `power_w` times the overlap duration between each sample interval and the phase interval; point traces instead use linear interpolation and trapezoidal integration. Multiple intervals with one phase name are summed. Compare the replay's `phase_energy_j` values with the released summary before continuing.

**3. Rebuild the trace anchor and pulse-edge bound.** For each bracketing calibration, run:

```sh
python3 -c "
import json, pathlib
from joulewise.powermetrics_fiducial import verify_stored_evidence_physics
d = pathlib.Path('<runs root>/<run id>/instrument_calibration')
e = json.loads((d / 'instrument_evidence.json').read_text())
b = verify_stored_evidence_physics(
    e,
    (d / 'raw' / 'powermetrics.plist').read_bytes(),
    (d / 'events.jsonl').read_bytes(),
)
print('verified effective pulse bound (s):', b)
print('stored pulse bound (s):', e['b_fiducial_s'])
"
```

This route ignores stored pulse fits while calculating: paired clock readings and native trace records rebuild the trace's time anchor; command stamps come from the calibration event log; every pulse is refitted; and the anchor bound is added to the largest fitted edge residual. The verifier checks that the refits lie within the stored pulse intervals and returns the wider of the fresh and stored effective bounds, so replay cannot narrow the publication. Repeat for both sides of the window. This proves the calibration-regime bound from raw bytes. It does **not** test transport of that bound from commanded GPU pulses to sustained mixed inference load; Section 7 retains that limitation.

**4. Reproduce the complete-window decision.** Use the exact consumption semantics and additional custody arguments recorded by the release; different semantics are not interchangeable. Run this against the archive copy because it appends to the replay log:

```sh
python3 scripts/run_campaign.py --whole-window-verdict \
  --runs-dir <runs root> --log <replay output>/campaign_log.jsonl \
  --campaign-policy <policy>.json --neg8-drift-bound <drift bound>.json \
  --consumption-semantics-id <release-recorded id> \
  <release-recorded custody and membership arguments>
```

The recomputation checks declared membership, replacements, admissions, calibration bracket, policy, and drift evidence. Its status and reason names must equal the released whole-window verdict. For `d078_minted_envelopes_v1`, include `--calibration-custody-store` when the release records one. For `salvage_dangler_exclusion_v1`, both `--window-membership-binding` and `--salvage-closure` are required. An archive that omits its required arguments is not sufficient for replay; do not guess them.

**5. Re-extract the largest false difference this measurement system can manufacture.** The result is the cell's resolution bound — the artifact calls it the detection floor:

```sh
python3 scripts/extract_detection_floors.py \
  --runs-root <runs root> --spec <extraction spec>.json \
  --out <replay output>/floors.json \
  --manifest-id <release-recorded manifest id> \
  --evaluation-basis-sha256 <released basis fingerprint> \
  --consumption-semantics-id <release-recorded id>
```

Compare each replayed cell's point repeatability term, corner-widened timing term, drift-widened gate, label, and refusal list with the release. Include `--hash-bundles` only if the released invocation did. If the code conditionally omits the point-only term, the release must supply its desk derivation from emitted per-cell repeatability statistics plus the replay-fenced self-consistency check against every cell where the code emitted the same diagnostic; absence of that derivation is a release blocker. Exit `0` means all cells extracted. Exit `1` means the report was written with one or more recorded cell refusals; it may be the correct reproduction. Exit `2` means the specification or path was invalid and no report was produced.

**6. Reproduce the contrast verdict.** This step becomes executable when the gamma analysis manifest is reissued: the manifest as currently generated is inadmissible, because it freezes the decode family at one member while the ratified family has two, and the reissue (tracked as W-10) gates the `_v4` transaction night. Until it lands, steps 1 through 5 replay in full and this step does not. Use the released floor artifact only after its extraction binding passes the L1 closure named above:

```sh
python3 -m joulewise.cli analyze-claims \
  --analysis-manifest <analysis manifest>.json --runs-root <runs root> \
  --floor-artifact <authenticated floor artifact>.json \
  --output <replay output>/claim_verdicts.json
```

Compare the point estimate, `deterministic_bounds.total`, full interval, Holm multiplicity with alpha = 0.05 and m = 2, floor gate, direction gate, outcome, and reason names. The clock-anchor shift bound is only one deterministic term, not the total.
