# Cold-gate Fable ruling — paper S3 (claim_side_bound_j)

**Contamination disclosure:** the harness auto-injected the global `~/.claude/CLAUDE.md` and the memory index `MEMORY.md` into my context before I read anything. I did not open RUN_STATE.md, repo CLAUDE.md, AGENTS.md, or any memory file. Packet sha256 verified equal to the stated digest; checkout e241e0b7.

**Ruling: A+B combined (scalar adopted, components required); C holds until the clause-to-test map below lands.**

## 1. Adopted quantity, formula, authoritative producer

`claim_side_bound_j` denotes the estimator's **complete deterministic-bound total B**, in joules, per contrast: for each named deterministic kind, the block-wise paired bound (`contrast_bound` if recorded, else `bound_a + bound_b`, `estimators.py:414-419`), averaged across blocks, then summed across kinds (`estimators.py:422-447`). Protocol text matches exactly (`prospective-comparison-protocol.md:359-364`). Authoritative producer = `estimate_paired_blocks` writing `PairedEstimate.deterministic_bound_total` (`estimators.py:479-486`, `:508`), serialized as `claim_verdicts.json contrasts[].deterministic_bounds.total`. The sidecar producer **copies** that field; it never recomputes.

The floor module's `claim_side_bound_source = "E_clock_anchor_shift_bound_j"` (`detection_floor.py:125`, `:391-392`) is ruled to name the **required propagation channel**, not the magnitude: the anchor term must be present in the deterministic list or the contrast refuses (`analysis_engine/__init__.py:980-986`), so B always contains it. The registry warning (`results-fill-registry.md:1128-1130`, `:422`) is resolved by this statement: DS-29 displays B, not the anchor term alone. Anchor-only display is forbidden.

## 2. Relationship to the stochastic interval and the already-applied widening

`metrology_aware_CI95` = estimate ± t·SE_total (stochastic layer). `decision_interval` = that interval extended once by B on each end (`estimators.py:483-486`). The claim decision consumes the decision interval directly (`claims.py:285`, `:369-375`). B is therefore **already applied**; the sidecar displays it, and nothing downstream may add it again. F+B (`floor_j + claim_side_bound_j`) is planning-only and non-gating (`paper_comparison_rendering.md:106-109`, protocol `:386-392`); where rendered (DS-28) it uses the same B, never a second widening. DS-26 endpoints are `deterministic_bounds.decision_interval` verbatim (`results-fill-registry.md:418-419`), never CI ± B recomputed by a renderer.

## 3. Contrast → ordered source-cell registration authority

The scaffold reads `finalized_manifest.contrasts[].source_cell_ids` (`claim_side_bound.py:51`). **No such key exists** in the prospective contrast schema (`analysis_manifest_v3.py:1072-1085`); executed probe: a real-shaped manifest always yields `claim_side_bound_cell_mismatch`. Adding the key would modify the frozen manifest, which this packet forbids.

Ruled authority chain: manifest `floor_estimator_registration` (prospective, `:1082`, `:3384-3385`) → `claim_verdicts contrasts[].floor.resolutions[].source_cell_ids`, validated unique, exact resolutions naming exactly one cell, usable resolutions naming at least one (`artifact.py:2271-2336`; engine `__init__.py:241-247`) → floor artifact `cells[].cell_id`. The sidecar's `source_cell_ids` = the ordered concatenation of `resolutions[].source_cell_ids` in resolution order, elements in recorded order, no dedup or sort. The scaffold's line 51 must be re-pointed to this join and additionally require every resolution status ∈ {exact, transported}. Ordering is bound because the scaffold rejects reordering (executed probe: swapped cells → `cell_mismatch`).

## 4. Serialization, version, tolerances

Schema id stays `joulewise.claim_side_bound.v1` (never issued; no consumer). Row keys become: `contrast_id`, `source_cell_ids`, `floor_artifact_id`, `claim_side_bound_j`, `deterministic_terms` (list of `{name, bound}` copied from verdicts `deterministic_bounds.terms`), `metrology_aware_CI95`, `decision_interval`. Digest binding to `claim_verdicts_sha256` retained.

Tolerance: **exact equality**, not `isclose`. Executed probe: a 1e-13 drift passes the scaffold (`claim_side_bound.py:62-63`) but the custody gate's `!=` refuses (`paper_custody.py:626-628`). The gate rule wins; the scaffold's 1e-12 comparisons are downgraded to diagnostics and the producer must emit the verdicts' JSON numerals byte-for-byte. Term-sum equality remains the verdicts validator's job (`artifact.py:2191-2195`, abs_tol 1e-12) and is not re-derived in the sidecar.

## 5. Required bindings

- **Floor:** `floor_artifact_id` equal to the floor artifact's `artifact_id` (`:55-56`) and embedded-floor byte equality (`paper_custody.py:608-614`); floor acceptance `PASS` (`paper_supply_custody.md:326-336`).
- **Reader:** `claim_verdicts_sha256` over the exact bytes the gate reads (`paper_custody.py:606`).
- **Manifest:** finalized v3 validator passes (`:602-604`); contrast ids ⊆ registered.
- **Acceptance/gate:** `claim-evidence.v1` registered in `_ISSUANCE_GATES` only after this producer exists (`:653-657`); gate re-runs `evaluate_claim` from verdicts fields (`:634-645`), never from the sidecar, so the sidecar is display-only provenance.
- **Anchor term:** gate refuses if `deterministic_terms` lacks `E_clock_anchor_shift_bound_j`.

## 6. Mutation cases (each must kill)

1. Omit one term from `deterministic_terms` while keeping the scalar → refuse (term sum ≠ total). Executed probe shows the current scaffold accepts `bound=0` with an unwidened interval, so this check is new and mandatory.
2. Scalar = anchor term only (< B) → refuse at `paper_custody.py:626`.
3. Decision interval widened by 2B → refuse (`claim_side_bound.py:62-63`; executed probe confirms).
4. Renderer recomputes CI ± B for DS-26 → mismatch versus verdicts `decision_interval` byte comparison.
5. Sidecar cells reordered, deduplicated, or drawn from a `refused` resolution → refuse.
6. Scalar drifted 1e-13 → refuse (exact equality).
7. Sidecar decision interval edited with matching scalar → refuse at `:627`.

## 7. Approved implementation scope and clause-to-test map

Scope: producer in `joulewise/analysis_engine/claim_side_bound.py` (copy-only from verdicts + floor), re-pointed join (decision 3), exact-equality validator, `claim-evidence.v1` registration, renderer projection of DS-26/DS-28/DS-29 from gate-authenticated verdicts. No manifest schema change. Tests: decisions 1–2 → `tests/test_paper_custody.py` gate mutations (extend `:913-917`); decision 3 → new join test against a v3-shaped manifest fixture (current fixture at `:888` invents the missing key and must be replaced); decision 4 → drift test; decision 6 → one test per case. Existing gate test executed: 1 passed.

**Failure-mode test:** under this ruling a displayed side-bound cannot differ from the decision-used quantity (single producer, exact byte equality, gate re-evaluates from verdicts), and cannot be widened twice (decision interval is copied, never recomputed; case 3 and 4 kill). NOT EXECUTED: full test suite; renderer code (not yet written).

**Verdict: A+B adopted — scalar B with named components, exact equality, join re-pointed to verdict floor resolutions; C (stop) remains in force until the seven mutation cases are green.**
