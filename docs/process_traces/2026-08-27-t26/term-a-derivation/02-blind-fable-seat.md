# Blind-seat report — item 26(i)/(ii): TERM A / TERM B derivation and self-consistency proof

Custodied verbatim as delivered by the blind Fable seat. It ran with no sight of the
Sol seat's derivation.

Repo read only: `/Users/edr/code/JouleWise-wt-r2` (nothing written there).

## 1. TERM A identity (per component, from UNCONDITIONAL fields)

For a floor component record `R` = `cells[].absolute` or `cells[].comparative` of a
`joulewise.detection_floor_artifact.v2` artifact:

```
A_unguarded = max( R.max_abs_residual_j [absolute] | R.max_abs_delta_j [comparative],
                   R.prediction_component_j )
A_guarded   = R.guard_factor * A_unguarded      (None when guard_factor is null, i.e. n < 5)
```

- Definition of the diagnostic: `_point_floor_diagnostic`,
  `joulewise/detection_floor.py:795-811` — `max(estimate.max_abs_deviation_j,
  estimate.prediction_component_j)`, times `guard_factor`.
- Those FloorEstimate attributes are carried unchanged through corner widening
  (`_apply_admissible_set_guard`, `:749-784`, which only rewrites
  `unguarded_floor_j` / `guarded_floor_j` / corner fields) and are serialized
  unconditionally as `max_abs_residual_j` / `max_abs_delta_j`,
  `prediction_component_j`, `guard_factor` (`build_absolute_record` `:1453-1468`;
  `build_comparative_record` `:1493-1508`).
- Inputs are themselves recomputable from the emitted samples:
  `prediction_component_j = extra + t_critical * s * sqrt(1 + 1/n)` with
  `s = sqrt(fsum((d - mean(d))^2)/(n-1))`, `t = student_t_critical_95(n-1)`,
  `extra = 0` (absolute) or `|mean_delta_j|` (comparative) (`_floor_estimate`
  `:689-716`; the `abs(mean)` extra at `:958`); `max_abs = max|residuals_j|` (`:696`);
  `guard_factor = sqrt(9/(n-1))` for 5 <= n < 10, else 1.0 (`:663-671`).
- Conditionality: `_add_attribution_limit_metadata` `:847-857` attaches
  `point_floor_diagnostic` ONLY when `admissible_set_uncertainty_dominates_point_floor`
  is true; the validator `_validate_attribution_limit_metadata` `:3289-3312` FORBIDS the
  container when the predicate is false (`:3307-3311`: "attribution-limit metadata is
  forbidden when uncertainty does not dominate"). The cell-level
  `point_floor_diagnostics` (`:1653-1666`) inherits the same conditionality. So a
  negative falsifier outcome can never be read off an artifact; hence the desk derivation.

## 2. Aggregation of the two components to ONE per-cell TERM A: NOT SPECIFIED ANYWHERE

Searched `joulewise/`, `docs/contracts/`, `docs/phase_2/detection_floor.md`,
`docs/decision_log.md`, `docs/paper/results-fill-registry.md`, and
`docs/paper/RQ-ATTRIBUTION-DOMINANCE-registry-row-draft.md` for "TERM A",
"repeatability term", "point-only floor", `point_floor_diagnostic(s)`. No code or
contract combines the absolute and comparative point diagnostics into one number; the
code keeps them as a two-key mapping (`point_floor_diagnostics: {absolute, comparative}`).

Candidates:

- (a) `max(A_abs_guarded, A_cmp_guarded)` — mirrors
  `floor_gate_j = max(floor_abs_j, floor_cmp_j)` (`:1628-1631`, validator `:3871`).
  Evidence: structural symmetry with the gate only.
- (b) Two per-component comparisons, no aggregation — mirrors the code's own predicate,
  which is evaluated per component (`:847-848`; `floor_extraction.py:2294-2300,
  2753-2759`), and the item-8 falsifier ("timing term exceeds repeatability term"),
  which is well-defined component-wise. Evidence: this is the only comparison the code
  actually performs.
- (c) Use only the component matching the claim's use (absolute for absolute claims,
  comparative for ABBA contrasts). Evidence: `single_count_discipline` / D-078 cl.11
  treat the floor role per contrast type, but nothing names this selection.

NEEDS-RULING (magistrate).

## 3. TERM B — the DOMINANCE term vs the gate

The code's dominance predicate (`:814-846`) compares `uncertainty_max > A_guarded` where:

```
absolute:    umax = max_i ( |residuals_j[i]| + w_i*(n-1)/n + (sum(w) - w_i)/n ),
             w = admissible_half_widths_j                                   (:829-838)
comparative: umax = max_i ( |block_deltas_j[i]| + w_i )              (:840-843, :735-745)
```

`umax` is NOT emitted anywhere; it is the exact linear corner maximum. The EMITTED
`corner_widened_unguarded_floor_j = max(unguarded_point, umax, full-corner enumeration
of the whole D-054 floor)` (`:936-946`, `:962-969`, `:761`) is >= `umax`, and strictly
larger in the mint cell (absolute: 2.940 vs 2.155; comparative: 6.796 vs 2.779). Then
`drift_widened_*_j = corner_widened_*_j + whole_window_drift_allowance.allowance_j`
(`:1336-1339`, validator `:3239-3258`), and
`floor_gate_j = max(abs.drift_widened_guarded, cmp.drift_widened_guarded)` (`:1621-1631`).

Three propositions, each a different test:

- **(T1)** `umax > A_guarded` — literally the code's predicate: "the largest
  anchor-admitted linear residual/contrast exceeds the guarded scatter floor". The
  ruling's phrase "the quantity the code's own dominance predicate compares" points
  here, but `umax` is not "the corner-widened floor".
- **(T2)** `corner_widened_guarded_floor_j > A_guarded` — "the published timing-widened
  floor exceeds the scatter floor". Implied by T1, and weaker as a falsifier, because
  the full-corner term adds scatter-at-corner content and so can exceed A even when T1
  fails.
- **(T3)** `floor_gate_j > A` — adds the drift allowance, which is a whole-window
  repeatability/drift term (`derived_repeatability_bound_j`, `:3193`), i.e. it
  contaminates a timing-vs-scatter test with a non-timing term. Correct to report only
  as the gate.

Which of T1/T2 the falsifier means is NEEDS-RULING.

## 4. Self-consistency proof (executed)

Values below are diagnostic-era instrument evidence, NOT paper results.

Artifacts where the code emits `point_floor_diagnostic`: only
`df-ph-decode-floor-mint1.json` (identical bytes in worktree and main checkout, sha256
prefix 559ab5ede19e; commit f1885626), one cell, both components. No other emitter
found — searched `/Users/edr/code/JouleWise/runs`, `docs/process_traces`, and
`tests/fixtures` for `point_floor_diagnostic` (`*.json`); other hits are a schema and
test fixtures without the container.

| record | n | gf | TERM_A_ung recomputed | emitted | EXACT | TERM_A_g recomputed | emitted | EXACT | umax | predicate | diag present | presence OK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mint1.df-ph-decode-floor.absolute | 10 | 1.0 | 0.49344826888709603 | 0.49344826888709603 | True | 0.49344826888709603 | 0.49344826888709603 | True | 2.1546708898450326 | True | True | True |
| mint1.df-ph-decode-floor.comparative | 10 | 1.0 | 0.6303242282254147 | 0.6303242282254147 | True | 0.6303242282254147 | 0.6303242282254147 | True | 2.779249999417285 | True | True | True |
| d117 fixture D117-GOLDEN-ABS | 5 | 1.5 | 0.4808173041811168 | (none) | – | 0.7212259562716752 | (none) | – | 0.216 | False | False | True |

PASS: 2/2 emitted diagnostics reproduced byte-for-value (Python float `==`);
presence/absence matches the recomputed predicate 3/3; corner-widened floors reproduced
24/24 records (including 18 rows of
`docs/process_traces/2026-07-24-diagnostic-extraction/diagnostic_details.json`); the gate
identity `floor_gate_j == max(abs, cmp)` holds; and every intermediate
(`prediction_component_j`, `max_abs`, `guard_factor`) recomputed from raw samples within
1e-12.

**Side finding.** `diagnostic_details.json`'s fields `point_unguarded_floor_j` /
`point_guarded_floor_j` are NOT point-only: the generating script
(`run_diagnostic_extraction.py:202,204`) serialises `estimate.unguarded_floor_j` AFTER
corner widening, so they equal `corner_widened_*` in 16/18 rows and coincide with TERM A
only where the predicate is false (A8-SU-ITEM, A8-SU-LEVEL). Nothing in that trace can
serve as a second proof source, and its labels are misleading if anyone cites them as
scatter floors.

## 5. Where this derivation could be wrong, and what settles each

1. A `_v4` kernel change to `_point_floor_diagnostic` or the predicate (item 26(iii)) —
   settled by re-running the script on the `_v4` artifact under the replay fence.
2. Float-summation order (`fsum` vs `sum`) across interpreters — pinned by the golden
   fixtures per the comment at `:692-694`; settled by CPython version pinning in the fence.
3. Aggregation across components (§2) — NEEDS-RULING.
4. Which quantity is "TERM B" (§3) — NEEDS-RULING.
5. The proof has n=1 cell (2 components); a second emitting artifact would strengthen
   it — settled when `_v4` issues its four cells.
6. `configs/campaigns/metrology_v1/characterization_result_schema_v1.json:1157` binds
   evidence at `$.floors[].point_floor_diagnostic`, while the actual artifact path is
   `cells[].{absolute,comparative}.point_floor_diagnostic` /
   `cells[].point_floor_diagnostics` — a path mismatch someone should confirm before the
   characterization consumer runs.

## NEEDS-RULING

- **NR-1:** aggregation operator for per-cell TERM A (max / per-component / claim-matched).
- **NR-2:** TERM B = `umax` (the code's literal comparand, unemitted but derivable) or
  `corner_widened_guarded_floor_j` (emitted, published); and guarded vs unguarded on both
  sides — note the code compares an UNGUARDED `umax` against a GUARDED point floor.
- **NR-3:** whether the mislabelled `point_*` fields in the 2026-07-24 trace need a
  correction note before anything cites them.

## Confidence

Settled by code and executed proof: the TERM A identity, its unconditional inputs, the
conditionality site, the predicate's exact comparand, the drift-vs-corner decomposition,
and the mint reproduction. Inferred and unsettled: the component aggregation and the
T1/T2 choice — those are the magistrate's.
