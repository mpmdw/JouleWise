# BLIND SEAT A — `characterization_result_schema.v1` design (P06)

## 0. The finding that reframes the problem

Before the design: three facts I verified that change what this schema is for.

**(a) The characterization pack already exists and is already frozen — it is just not bound to the paper.** `configs/campaigns/metrology_v1/` is the characterization campaign: five sub-campaigns whose READMEs name paper claims C1–C5 (`configs/campaigns/metrology_v1/README.md:1-8`). They map 1:1 onto Table 1's first five rows, and four of five already carry `freeze_status: "frozen_before_measurement"` (e.g. `configs/campaigns/metrology_v1/linearity_ramp/calibration_plan.json:5`). Their sample counts — Table 1's `TODO-EVIDENCE[...]` cells at `docs/paper/draft-v1.md:335-339` — are **already registered numbers**:

| Table 1 row | metrology_v1 sub-campaign | Registered design | Cite |
|---|---|---|---|
| Workload response | `linearity_ramp` | 5 output levels (128/256/512/1024/2048), n=8 each, 40 bundles | `linearity_ramp/calibration_plan.json` cells; `fixed_n: 8` |
| Identical-condition null | `null_ladder` | 3 magnitudes (128/512/2048), 5 ABBA blocks each, 60 bundles | `null_ladder/README.md:11-12` |
| Small-difference challenge | `micro_delta` | ΔE at **0.5× / 1× / 1.5× / 3×** the published floor, 5 blocks/slot | `micro_delta/calibration_plan.json:5-7` |
| Phase accounting | `additivity_shapes` | 3 shapes (2048/128, 512/512, 128/2048), n=8, 9 cells | `additivity_shapes/README.md:10-13` |
| Drift and recovery | `long_holds` + `window_references` | decode-o4096 n=3; extended idle 120/300/600 s; 3+1+3 references | `long_holds/`; `configs/campaigns/window_references/README.md:1-8` |

So **twelve of the paper's `TODO-EVIDENCE` cells are not all unknowable — several are already-registered numbers that no artifact binds to the draft.** Any design that treats all twelve as "needs Ed input" is wrong. The schema's first job is to make the binding mechanical.

**(b) The retained characterization the abstract cites has no artifact, no schema, and no criterion.** The abstract's `25.6–31.1 ms` (`docs/paper/draft-v1.md:7`, repeated `:215`, `:219`, `:267`, `:400`) exists in **no file**. It is a min/max recomputed on 2026-08-15 by one audit seat reading 30 separate `summary_metrics.json` files — `energy_anchor_shift_envelopes["<metric>"].anchor_bound_s` across `runs_window_a10_20260725/` — and written down only as prose at `docs/process_traces/2026-08-15-readiness-council/seat-reports/L11-retained-characterization-basis-report.md:37`. Three further defects in that same number:
- ~80–97% of every one of those 30 bounds is **one shared session fiducial constant** (`b_fiducial_s = 0.024879192`). Quoting a 30-run min–max presents a shared constant as 30 independent draws.
- All 30 members carry `clock_bound_exceeds_quarter_window`, a **genuinely pre-registered numeric criterion** at `joulewise/reduce.py:996-998` (`clock_bound_s > 0.25 * window.duration_s`). The paper mentions this at none of its six citation sites.
- The one criterion these runs *did* face — `admissible_set_uncertainty_dominates_point_floor`, pre-registered 2026-07-20 (`docs/decision_log.md:4238-4241`, commit `ca6861b`) — refused all three cells, and was **converted from a hard refusal to a labelled claim path on the same day the data were collected** (commit `ffee598`, 2026-07-25; D-078 cl.11 at `docs/decision_log.md:4730-4740`).

That last item is the type specimen. It is not misconduct — the decision log is candid that it was the only remaining path (`docs/decision_log.md:4715-4718`) — but it is exactly the failure mode P06 rules against, and it happened because **`configs/floor_mint/a10_extraction_spec.json` has keys `['schema_version', 'cells']` only**: the spec pinned *membership* and nothing else. The pass criterion lived in `joulewise/reduce.py` and the decision log, both mutable, and both were mutated.

**The one-line statement of what this schema must fix: the house already freezes WHO is measured; it has never frozen WHAT COUNTS AS PASSING.**

**(c) The characterization has already been run and refused.** `runs_window_metrologyA_20260731` / `metrologyB_20260801` collected null rungs 1–2 and 23/24 additivity members; **"Both metrology verdicts FAILED and stand as issued"** (`WINDOW_STATUS.md:91`). Publishable-as-refusal is not hypothetical here — it is the current state.

---

## 1. Architecture: instantiate the house spec/result pair, do not invent one

The house already has the exact pattern: a **pre-registered spec** and an **issued result** with paired schema names — `configs/floor_mint/a10_extraction_spec.json` (`joulewise.detection_floor_extraction_spec.v1`) → `detection-floor-extraction.json` (`joulewise.detection_floor_extraction.v1`). I instantiate it rather than inventing:

| Artifact | Schema id | When | Contents |
|---|---|---|---|
| `configs/characterization/characterization_row_registry_v1.json` | `joulewise.characterization_result_spec.v1` | **Frozen before collection** | Row set, criteria, estimators, limits (numbers or derivation rules), outcome map, token bindings, per-criterion pre-registered consequence |
| `<runs_root>/characterization-report.json` | `joulewise.characterization_result.v1` | Issued after | Per-row/per-criterion realized values, outcomes, refusals, evidence digests |
| `docs/contracts/characterization_result_schema.md` | prose, `characterization-result-schema/v1` | Normative | Exact-key schema + closed refusal vocabulary. **Carries no number.** |

Naming follows house convention exactly: `joulewise.<thing>.vN` (`joulewise/arm_readiness.py:47-89`; `joulewise/detection_floor.py:201-205`).

**Why the prose contract carries no number:** if a limit lives in prose, an editing pass changes a pass criterion without a freeze receipt. Numbers live only in the spec JSON, which is hashed into a freeze receipt.

**Contract prose style** mirrors `docs/contracts/d117_step6_confirmation_table.md` — a `## Exact schema` section stating "Every object below is exact-key. Integers reject booleans. Digests are 64 lowercase hexadecimal characters," followed by one literal JSON document with placeholders (`:64-138`) — plus a `## Refusal vocabulary` two-column closed-enum table in the form of `docs/contracts/receipt_histsem_verifier.md:103-129`, and a **Domain-owners table binding every issued field to the code path that recomputes it**, copying `docs/phase_2/floor_mint_contract.md:180-192`. That last table is the strongest precedent in the repo for a result schema whose numbers must each name a recomputing authority.

**Register it as an analysis-plan family.** `docs/contracts/analysis_plans.md:15-36` already ratifies the per-plan required-field set (family_id, claim_role, selection_scope, multiplicity_rule, unit of analysis + dependence structure, estimator/formula, inclusion/exclusion, floor gate, MDE/n sizing, disqualifiers + not-resolvable conditions, claim ceiling + exact forbidden upgrade). Every characterization criterion is an instance of that table. Register rows as `AP-C1 … AP-C7` in the Analysis Registry, which is itself "FROZEN before each campaign's execution" (`analysis_plans.md:47-49`). This buys three things for free: **multiplicity discipline** (see §5), a ratified claim-ceiling field, and `scripts/claims_lint.py` as a mechanical checker.

---

## 2. The row set

**Keep the six template rows. They are frozen harder than the draft.** `docs/process_traces/2026-08-07-plan-factory/lint_results_prose_template.py:779-788` binds row ids to token tuples and mechanically enforces that each token occurs exactly once inside its own `diagnostic_<row>_present` branch. Renaming or splitting a row breaks the lint, the 91-token census, and the 133-row registry reconciliation (`docs/paper/results-fill-registry.md:381-392`). The six ids are `linearity, null, empirical_floor, phase_attribution, drift_settling, between_sessions`, and `docs/paper/results-fill-registry.md:304-309` (DS-02..DS-07) already binds each to its Table 1 content anchor.

**Get the split's benefit without breaking the freeze: rows report, criteria decide.** Each row carries ≥1 **criterion** — the unit of evaluation, with its own estimator, limit, evidence binding, and refusal label. The row outcome is the fail-closed aggregate over its criteria. `drift_settling` therefore adjudicates drift containment and recovery time *separately* (they have different evidence, and one is capability-blocked while the other is not) while still rendering as one row.

**Add one row: `attribution_bound` (R7).** Table 1 characterizes everything except the quantity the paper's title, abstract, §3 and §7 are all *about*. `25.6–31.1 ms` and the attribution-limited label rest entirely on retired-era, unrecorded, uncriterioned diagnostics (§0b). R7 makes the paper's headline property a prospectively pre-registered, criterioned result. Its quantities are already recorded in every bundle and need **no new capability**.

**Cost, stated plainly:** a new token family (`B_C_fiducial_bound_s`, `B_C_bundle_local_bound_max_s`, `PLAIN_LANGUAGE_RESULT_attribution`, `D_C_attribution_diagnostic_s`), a template-train amendment, a lint update, census 91→~95. **Precedent exists for exactly this:** `docs/paper/results-fill-registry.md:349-350` already records that "the lead-owned template train must add the guarded prompt token family" for the D-122 arm. The template was authored 2026-08-07, *before* the anchor correction (r6 / 13-r1, 2026-08-19) made attribution the headline. A frozen artifact that predates the finding it must report is the case successor editions exist for.

**Fallback if the magistrate refuses the amendment:** fold R7's criteria into `phase_attribution` as criteria C4.3–C4.5. Nothing in the schema breaks; only the paper's reporting granularity degrades. I prefer R7 standalone and expect this to be the debate's main contested point.

---

## 3. Outcome vocabulary (shared by all rows)

House naming: snake_case for outcome/reason codes (`joulewise/analysis_engine/claims.py:20-28` `CLAIM_OUTCOMES = not_estimable, not_resolvable, unresolved, direction_supported, equivalent`).

| `row_outcome` | Renders as (template's closed phrase set, `DRAFT-RESULTS_PROSE.md:259-263`) | Meaning |
|---|---|---|
| `supported` | "supported the registered behavior" | every criterion met its limit |
| `indeterminate` | "did not support a conclusion under the registered criterion" | evidence authentic and complete, decision not reachable (n below registered minimum; interval straddles the limit; probe mis-sized) |
| `contradicted` | "showed that the registered expected behavior did not hold" | criterion evaluated and **failed**. This is a published result |
| `pending_eligibility` | "remains pending because fewer than three eligible sessions are available" | **`between_sessions` only** — the template restricts this phrase |
| `protocol_incomplete` | *no phrase exists* | **unreachable after freeze** |

**`protocol_incomplete` is the point of the whole exercise.** `docs/paper/draft-v1.md:331` says the rows' "only permitted outcome is 'protocol incomplete'" *because no schema exists*. Freezing the schema retires that outcome. The writer must **refuse to issue a report** rather than emit it — a `protocol_incomplete` in an issued report is a schema violation, not a result.

**Aggregation precedence (fail-closed):** `contradicted` > `indeterminate` > `supported`. A known failure must never hide behind an unreached decision. `between_sessions` short-circuits to `pending_eligibility` when eligible sessions < 3.

**Refusal prefix family.** A closed `characterization_*` enum, **deliberately disjoint** from `readiness_*` / `histsem_*` / `CELL_REFUSAL_CODES`, exactly as `docs/contracts/receipt_histsem_verifier.md:129-131` requires of `histsem_*` ("no coincidental downstream `readiness_*` refusal substitutes for a required histsem refusal"). Members named per row below.

---

## 4. The rows

Fields per criterion follow `docs/contracts/analysis_plans.md:15-36`: `criterion_id, quantity, units, estimator, sample_unit, minimum_n, decision_rule, limit, limit_basis, evidence_binding, consequence_if_contradicted, claim_ceiling`.

`limit_basis` is a closed enum: **`ruled`** (a number already fixed by a ratified decision or committed code), **`derived`** (a formula over authenticated prior artifacts, resolving to a number at freeze time), **`ed_input_required`** (no basis exists; freeze blocks).

### R1 `linearity` — Workload response

*Forcing problem, in plain words:* if measured energy does not grow in a fixed straight-line way with the amount of work done, then any energy difference between two conditions can be an artifact of the conditions doing different amounts of work rather than of the thing being compared. R1 also **supplies** R3: the token→joule conversion.

| | |
|---|---|
| **C1.1 / C1.2** | Fit `E = a + bT` by ordinary least squares over admitted bundles, `T` = **realized** output tokens (`draft-v1.md:335`), separately for `energy_request_j` and `phase_energy_j.decode`. One admitted bundle = one point. Emits `[S_C_linearity_request_J_per_token]`, `[S_C_linearity_decode_J_per_token]`. |
| **C1.3 estimator** | **Maximum level-mean residual (MLMR)**, joules: `max over levels of |mean residual at that level|`. Emits the limit as `[R_C_linearity_limit_J]`. |
| *Why MLMR and not an F-test for lack of fit* | An F-test's p-value scales with within-level scatter, which on this instrument is dominated by attribution error (D-078 cl.11); a low-scatter level would fail it for physically negligible curvature. MLMR is in joules, directly comparable to the floor — the quantity the paper decides with. |
| **C1.3 limit** | `MLMR ≤ F_operative` of the matching **already-issued** alpha/beta cell. *Plain statement:* a departure from the straight line smaller than the largest difference the instrument can manufacture with nothing changed is not evidence of curvature. `limit_basis: derived`. |
| **Circularity guard** | The floor used **must** come from a prior frozen window (alpha/beta), never from the characterization window's own data — otherwise a bad window inflates its own limit. Enforced by the supplier-ordering gate (§6). If no alpha/beta floor is issued at freeze time, `limit_basis` degrades to `ed_input_required` and an absolute joule limit must be ratified instead. **This is the design's single largest open dependency and I flag it as such.** |
| **n** | 5 levels × 8 bundles = 40, **already registered** (`linearity_ramp/calibration_plan.json`, `fixed_n: 8`). Above the ruled ≥5-independent-unit minimum (`draft-v1.md:186`) but below `g(n)=1` at n≥10 (`draft-v1.md:187`). |
| **Degraded** | `characterization_level_absent` (any registered level missing → `indeterminate`; the draft requires "every level is present", `:335`); `characterization_level_membership_insufficient`; `characterization_estimator_undefined`. |
| **Evidence** | Per-bundle `summary_metrics.json` energy fields + realized token counts from the runtime event stream; each bundle fingerprinted in the campaign record (`draft-v1.md:315`), report recomputes. |
| **`consequence_if_contradicted`** | "The token-generation slope is not usable to size effects; `micro_delta`'s k slots cannot be ratified, and R3 returns `indeterminate` rather than being re-derived from post-hoc data." |

### R2 `null` — Identical-condition null response

*Forcing problem:* an ABBA comparison whose A and B are the same condition must come out at zero; any nonzero block difference is false by construction (`draft-v1.md:307`).

| | |
|---|---|
| **C2.1 estimator** | Per block `δᵢ = (B₁+B₂−A₁−A₂)/2` (J); report `max|δᵢ|` → `[D_C_null_max_abs_J]`, plus `δ̄` and its composed interval. |
| **C2.1 decision rule** | **Containment, not a significance test.** The whole composed interval for `δ̄` must lie inside `[−m, +m]`, and `max|δᵢ| ≤ m`. The draft is explicit that "failure to reject zero is not sufficient" (`:336`). |
| **C2.1 limit `m`** | `m = F_operative` of the matching **already-issued** alpha/beta cell. `limit_basis: derived`. |
| *Why this is the strongest criterion in the schema* | The floor is defined as the largest difference the instrument can manufacture with nothing changed (`draft-v1.md:165`). A null block **is** nothing changed. So a null block exceeding the floor **falsifies the paper's own floor.** R2 becomes a live falsification test of §3, not a decoration. |
| **Non-circularity, and why the dedicated arm is needed** | The alpha/beta packs' own ABBA stages *construct* `F_cmp` (`joulewise/detection_floor.py` via `draft-v1.md:180`), so testing those blocks against that floor is circular. `null_ladder`'s blocks are held **outside** the floor derivation, which is why the dedicated arm earns its window minutes. |
| **n** | 3 magnitudes × 5 blocks = 15 blocks, **already registered** (`null_ladder/README.md:11-12`). ≥5 per magnitude satisfies `draft-v1.md:186`; `g(n)>1` applies. |
| **Degraded** | `characterization_magnitude_absent` → `indeterminate` (never `contradicted`). |
| **`consequence_if_contradicted`** | "The affected cell's issued floor is withdrawn from claim use and every contrast consuming it returns `not_resolvable` pending a re-derived floor." A pre-committed consequence with real cost. |

### R3 `empirical_floor` — Deliberate small-difference challenge

*Forcing problem:* gates that never see a near-threshold case are untested.

| | |
|---|---|
| **Estimator** | Per registered level: predicted `Δ̂ = b̂·ΔT` using the **externally fixed** slope from R1's supplier artifact; observed `Δ` from that level's ABBA blocks; ratio `ρ = |Δ| / F_operative`. Emits `[R_C_micro_min_x_floor]`, `[R_C_micro_max_x_floor]` (min/max of ρ across levels). |
| **Criterion** | **Gate-outcome conformance.** Every registered level's realized gate outcome equals its prewritten expected outcome (`draft-v1.md:337`). |
| **Levels — ALREADY RULED** | `configs/campaigns/micro_delta/calibration_plan.json:5` registers ΔE at **0.5× / 1× / 1.5× / 3×** the published floor. `limit_basis: ruled`. The 3× super-floor level is independently corroborated by D-078 cl.11's "~3x the widened floor". **I do not invent multipliers; the pack has them.** |
| **The 1× slot is registered without a pass expectation** | At exactly the gate boundary the expected outcome is genuinely undetermined; registering an expectation there registers a coin flip. The 1× slot is registered as `expectation: none` and contributes a diagnostic value only. This is a deliberate, attackable choice. |
| **Bidirectionality** | The template requires super-floor effects "resolved … in both directions" (`DRAFT-RESULTS_PROSE.md:2452`), so 3× must be registered at both signs. `difference_orientation: "condition_b_minus_condition_a"` already exists (`micro_delta/calibration_plan.json:78`). |
| **Mis-sizing guard (important)** | Levels are set in **tokens**; the token→joule conversion uses `b̂`. If `b̂` is wrong the probes land in the wrong place and R3 tests `b̂`, not the gates. The spec therefore records `predicted_delta_j` per level at freeze and `realized_delta_j` at report; if `|realized/predicted − 1|` exceeds a registered factor, the row returns `indeterminate` with `characterization_effect_sizing_missed` — **never `contradicted`.** Failing to build the test is not the test failing. |
| **Capability** | **PARTIAL.** Only 1 of 3 k slots is generated and the pack is `freeze_status: "draft_pending_slope"` (`micro_delta/calibration_plan.json:5`). Blocked on R1's fit + magistrate ratification of the slots. This is a *sequencing* prerequisite, not a missing instrument. |
| **`consequence_if_contradicted`** | Direction-dependent, both pre-registered: a sub-floor level that *resolves* → "the floor understates the instrument's false-effect rate; §3's floor construction is reported as falsified for that cell." A super-floor level that *fails to resolve* → "the two-gate path is reported as less sensitive than the floor predicts; §6's clearance sizing is re-derived upward." |

### R4 `phase_attribution` — Phase accounting

| | |
|---|---|
| **C4.1a `additivity_no_overcount`** | `Dᵢ = E_prompt + E_generation − E_request` per bundle (J). Criterion: `max Dᵢ ≤ τ`. A **positive** `D` means the phases double-counted boundary sample energy — a hard instrument defect. `τ` has a **ruled numeric basis**: `draft-v1.md:426` records that independent reintegration reproduced every stored phase energy with **0.0 J discrepancy**, so `τ` is a floating-point tolerance (proposed `1e-9 J`), not a physical allowance. `limit_basis: ruled`. |
| **C4.1b `additivity_gap_bounded`** | `|Dᵢ| ≤ (registered maximum un-phased gap duration) × (maximum recorded package power over that gap)`. Derived per bundle from retained trace data; no invented number. Emits `max|D|` as `[D_C_additivity_J]` (max, **not** mean — a mean `D` can be zero while individual bundles leak in opposite directions, and per-run attribution is the paper's concern). |
| **C4.2 `prompt_invariance`** | Fit prompt-processing energy against **later** output tokens with prompt tokens held fixed → `[S_C_prompt_invariance_J_per_token]`. Prompt processing finishes before generation starts, so how many tokens are generated afterwards cannot change the energy prompt processing used. A nonzero slope means energy is leaking across the boundary. |
| **C4.2 limit `β`** | Pass iff the whole composed slope interval lies in `[−β, +β]`, with `β = 1 J / ΔT_max`. *Derivation:* over the registered output-token span, a slope `β` shifts energy by `β·ΔT_max`; setting that shift equal to the ruled ~1 J attribution scale (D-078 cl.11) gives `β`. With `additivity_shapes`' 2048-token maximum, `β ≈ 0.00049 J/token`. `limit_basis: derived`. Emits as `[B_C_prompt_invariance_J_per_token]`. |
| **Registry note** | `[B_C_prompt_invariance_J_per_token]` exists in `results-fill-registry.md:261` but is **absent from lint's Variant-B row tuple** (`lint_results_prose_template.py:784-785`) — it renders only in Variant A. Flagged as a template-train inconsistency to resolve at the same time as R7's tokens. |
| **n** | 3 shapes × 8 = 24 members, 9 cells, **already registered**; 23/24 already collected once (`WINDOW_STATUS.md:78-79`). |
| **`consequence_if_contradicted`** | **Already written in the draft** — `docs/paper/draft-v1.md:328`: "A nonzero prompt-processing slope under a fixed prompt would narrow the phase-specific claim rather than be explained away." The spec binds that sentence verbatim. |

### R5 `drift_settling` — Drift and recovery (**two criteria, deliberately separate**)

| | |
|---|---|
| **C5.1 `drift_containment`** | `X = max(S,M,E) − min(S,M,E)` from the fixed 3+1+3 reference schedule (`draft-v1.md:236-244`) → `[D_C_reference_excursion_J]`. **The criterion cannot be `X ≤ A_drift`** — that is self-satisfying, since `A_drift = max(X, R_c)`. The draft says so in its own words (`:244`): "The start, midpoint, and end points … document the allowance but cannot validate it; containment must be evaluated on held-out probes or later sessions." **Criterion:** register held-out reference probes excluded from the allowance derivation; every held-out probe's deviation from the window's reference mean must be `≤ A_drift`. |
| Capability | **EXISTS** — held-out probes are ordinary reference members (`configs/campaigns/window_references/`, executed in `runs_window_metrologyA_20260731/campaign_log.jsonl`). New spec field required: `reference_role ∈ {allowance_constructing, held_out}`, frozen at pack generation so the allowance derivation mechanically excludes them. |
| Held-out count | `ed_input_required` (window-budget bound). Proposed floor of ≥3, one per window third, so a single outlier is not the whole result. |
| **C5.2 `recovery_time`** | "the first elapsed time at which the complete admission predicate and cooldown exit criterion both pass" after a disturbance (`draft-v1.md:339`) → `[T_C_recovery_s]`. **Criterion: `T_recovery ≤ 180 s`**, which the draft explicitly asks this row to adjudicate (`:339` "recovery comparison that adjudicates the 180-s convention"). `limit_basis: ruled` — `docs/phase_2/window_runbook.md:214` `SETTLE_S=180`, `:135` "Stage settle | 180 seconds". |
| **Capability: ABSENT, and worse — structurally censored** | No disturbance injector exists anywhere (grep for `stress-ng|inject.*load|recovery_time|time_to_recover` over `joulewise/`, `scripts/`, `configs/` → zero). And the runbook executes a **blind fixed sleep**: `docs/phase_2/window_runbook.md:1299` `/bin/sleep "$SETTLE_S"`, *then* attempts admission. So the first passing admission is at 180 s **by construction**: you can only learn "≤180 or failed," never a value. Reporting that as a point estimate would be a lie. |
| **My proposal, two tiers** | **(i) Minimal, no new instrument:** poll the existing admission predicate at a registered cadence *during* the settle and log every attempt's outcome. The predicate already exists (`joulewise/environment_admission.py`, `joulewise/idle_admission.py`); recording its result during a wait is a **logging change, not a new measurement capability**. This uncensors C5.2. **(ii) If (i) does not land before freeze:** register C5.2 as **censored** — `censored: true`, outcome restricted to `supported` (recovered by 180 s) or `contradicted` (did not), and `[T_C_recovery_s]` binds to the **censoring bound**, never a point estimate. The `censored` flag is mandatory in the schema and the renderer must not drop it. |
| Fence acknowledged | `configs/campaigns/metrology_v1/long_holds/README.md:12-24` + `joulewise/schemas.py:816` forbid zero-token members and harness edits. Neither tier violates it: (i) adds logging inside the existing settle; (ii) adds nothing. |
| **`consequence_if_contradicted`** | "The settling interval is raised to the observed maximum recovery time plus the registered margin in a successor policy edition, and every window collected under the 180-s convention is re-examined for admission validity." |

### R6 `between_sessions` — Between-session stability

| | |
|---|---|
| **Scope** | `cross_window`. It is the reason Variant A is unavailable until ≥3 sessions (`DRAFT-RESULTS_PROSE.md:250-253`). |
| **Eligibility predicate (exact)** | A session is eligible iff (i) its whole-window verdict is **issued** and PASSED; (ii) every stack-identity field at `draft-v1.md:333` matches the reference session exactly; (iii) its capture-method era is a current claim-bearing anchor method (`draft-v1.md:326`; registry F2, `results-fill-registry.md:43-47`). |
| **Selection discipline** | The eligible set is **defined by predicate, never enumerated.** An enumerated list invites cherry-picking; a predicate cannot. `sessions_excluded[]` with per-session reasons is mandatory so exclusions are visible. |
| **Criterion** | For each of {calibration bound (s), each operative floor (J), null result (J)}: the **range across eligible sessions ≤ the largest single-session declared bound for that quantity**. *Plain statement:* session-to-session variation must not exceed the uncertainty a single session already declares — otherwise the single-session bound understates what the instrument does. `limit_basis: derived`, non-circular, no new number. |
| **n** | **≥3 — the one Table 1 cell already filled** (`draft-v1.md:340`). Below 3 → `pending_eligibility`. Emits `[N_C_eligible_sessions]`. |
| **Gap flagged** | No pack supplies R6; it is an index over windows. Its evidence binding is a cross-window session index that must itself be frozen (predicate, not list). |

### R7 `attribution_bound` — Timing-attribution realization (**proposed addition**)

*Forcing problem:* the paper's title, abstract, §3, and §7 all rest on the claim that phase-edge placement, not run scatter, limits this instrument — and §5 characterizes everything except that.

| | |
|---|---|
| **C7.1 decomposed reporting** | Report the **shared session fiducial term** `b_fiducial_s` (one per bracket capture, 2 per window) and the **per-bundle local + edge-span term** (genuinely per-run) as **separate fields**, never as one min–max range. This directly repairs the defect in the abstract's current `25.6–31.1 ms` (§0b). |
| **C7.2 `bracket_bound_within_issued_band`** | Both bracket captures' bounds must fall inside the issued acceptance edition's registered corpus band. **Ruled and already operational** — the paper does exactly this comparison at `draft-v1.md:335` (0.0309 s inside `[0.0227, 0.0336]` s). The spec binds the **edition id**, not the number (`draft-v1.md:325`). |
| **C7.3 `quarter_window_eligibility_rate`** | Realized rate of `clock_bound_exceeds_quarter_window` across admitted members. **Ruled and committed**: `joulewise/reduce.py:996-998`. Criterion: rate = 0 among claim-bearing members. **This flag fired on 30/30 of the retained corpus and the paper reports it nowhere.** |
| **C7.4 `cadence_and_sample_fidelity`** | Realized rates of `cadence_ratio_below_threshold` and `insufficient_in_window_samples`. Ruled constants: `joulewise/reduce.py:117-118` (2.0 / 4.0) and `MIN_PHASE_SAMPLES` (≥3 overlaps, `draft-v1.md:426`). |
| **C7.5 `attribution_dominance_realized`** | Consumes the **existing** computed condition `admissible_set_uncertainty_dominates_point_floor` (`joulewise/floor_extraction.py:170-214`). Pass = the timing term exceeds the point repeatability term. **Needs no new number at all.** |
| **`consequence_if_contradicted` (C7.5)** | "The attribution-limited label is not applied to this window's floors, and §7's 'Attribution-limited resolution' paragraph is re-scoped to the retired-era corpus only." A pre-registration that can force a paper rewrite is the only kind worth having. |
| **Evidence binding (exact field paths)** | `<bundle>/summary_metrics.json` → `energy_anchor_shift_envelopes["<metric>"].anchor_bound_s`, `.max_abs_delta_j`, `.independent_edge_shift_bound_j`, `.method`; `energy_bound_terms_j.E_clock_anchor_shift_bound_j`. Bracket captures → `instrument_evidence.json` `b_fiducial_s`. Flags from `campaign_log.jsonl` `claim_evidence_flags`. |
| **Capability** | **EXISTS today.** Every field above is already written by the current harness. |

---

## 5. Multiplicity — a hole the row-by-row framing hides

Seven rows × ~15 criteria is a family of tests, and `docs/contracts/analysis_plans.md:57-62` requires a named `multiplicity_rule` for any family. §6's demonstration already Holm-corrects its two tests (`draft-v1.md:361`); the characterization currently corrects nothing.

**Proposal:** most criteria are **deterministic bound comparisons** (containment against a fixed limit), which carry no false-positive rate and need no correction. Only two are inferential — R2's null equivalence interval and R4.2's slope interval. Register the family with `claim_role: exploratory`, `multiplicity_rule: "explicitly exploratory; no confirmatory inference"` — allowed verbatim (`analysis_plans.md:58-60`) — and apply **Holm within the two-member inferential subfamily** (`m=2`). Every row's `claim_ceiling` is instrument-result language, `exact_forbidden_upgrade` = "no characterization row may be quoted as a scientific finding about models, hardware, or workloads."

---

## 6. Freeze mechanics

**No new machinery. One new receipt kind.**

Freeze receipts already exist per pack at `<pack>/arm_readiness.freeze.receipts/freeze-000N.json` (+`.sha256`), schema `joulewise.arm_readiness_freeze_receipt.v2` (`joulewise/arm_readiness.py:397-425`), with `evidence[]` entries of shape `{evidence_id, namespace, path, receipt_kind, schema_version, sha256, status}` and eleven existing kinds (`ACCEPTANCE_OWNER, DOCTRINE_PIN, ESTIMATOR_IDENTITY, MINT_TRUST, MULTICELL_MINT, PACK_AUTHENTICATION, PACK_FAMILY, REASON_CODE_COVERAGE, RECEIPT_ORACLE, RECOVERY_LEDGER_TEST, THREE_WINDOW_REGRESSION`).

1. **Add receipt kind `CHARACTERIZATION_CRITERIA`**, path `arm_readiness.evidence/evidence-characterization-criteria.json`, `sha256` over the frozen spec. That is the entire freeze mechanic.
2. **The `rows[]` shape is already right.** `freeze-0003.json` rows are `{row_id, predicate_id, applicability, evaluation_phase, evidence_ids[], verdict}` — reuse with `evaluation_phase: "POST_COLLECTION"` (new member of `EVALUATION_PHASES`, currently `{FREEZE_AND_ARM, ARM_ONLY}` at `joulewise/arm_readiness.py:246-253`) and `criterion_id` for `predicate_id`.
3. **Two mechanical ordering gates** (the enforcement, not the promise; `draft-v1.md:291`):
   - **`characterization_criteria_not_prior`** — refuse unless the freeze receipt's `issued_at_utc` precedes every admitted member's capture timestamp.
   - **`characterization_limit_supplier_not_prior`** — refuse unless every `derived` limit's supplier artifact carries a **strictly earlier freeze ordinal**. This gate would have caught the 2026-07-25 same-day criterion change.
4. **One writer.** `joulewise/characterization_report.py` issues the report, recomputes every fingerprint itself, and rejects any input field attempting to select its own estimator *or its own limit* — extending `draft-v1.md:324`.
5. **Edition discipline.** `predecessor`-linked, append-only, `estimator_code_sha256` with `triggers: ["protocol_or_estimator_byte_change"]`, as the calibration-acceptance editions do (`draft-v1.md:325`).

**Blocking prerequisite, stated plainly:** `configs/campaigns/metrology_v1/` currently has **no** `arm_readiness.evidence/`, **no** `arm_readiness.freeze.receipts/`, **no** `plan_tree.json`, **no** `producer_contract.json`, **no** `identity_pin_projection.receipts/`, and its generators carry **no** `SUCCESSOR_ACCEPTANCE_ID` (unlike `d117_floor_qwen25_1p5b_v3/generate_configs.py:155`). It also has no profile entry in `configs/arm_readiness/d117_row_registry_v2.json`. **It cannot be frozen under house machinery until those five namespaces land.** That is the real work order behind this schema, and it is larger than the schema itself.

**Scoping correction:** the `_v4` transaction (`TASK_QUEUE.md:630`, `V4-TRANSACTION-01`) mints `freeze-0004` ×3 for the **alpha/beta/gamma** packs only (`docs/contracts/d117_step6_confirmation_table.md:83-101`). `metrology_v1` is not in it and needs its own freeze lane (`freeze-0001`, `predecessor: null`), sequenced against — not inside — the `_v4` transaction.

**Naming hazard:** "Window C" means two different things. `results-fill-registry.md:100-101` warns the characterization campaign is "not any historical window called C"; D-113 uses "Window C" for the fresh claim-bearing window (`docs/decision_log.md:7452-7455`); `metrology_v1/README.md:45-46` and `docs/phase_2/window_c_operator_checklist.md:141-147` give two *different* splits. Resolve before freeze.

---

## 7. How Table 1 consumes it

**Table 1 is currently being asked to be both the pre-registration and the result. Split it.**

- **Table 1 (specification), stays where it is.** All twelve `TODO-EVIDENCE` cells replaced by frozen values or derivation rules, cited by `edition_id` + sha. Complete and replicable **before any collection**. DS-02..DS-07 stay bound to their content anchors; their fill rule changes from `STOP_FILL` to `MEASURED`-from-the-criteria-file — answering the registry's own complaint that "specification row is not a fillable result cell" (`results-fill-registry.md:304-309`) by no longer trying to make it one.
- **Table 1b (results), new.** Per-row `row_outcome` + that row's value tokens, filled only from an issued report through the ordinary `MEASURED / DERIVE / STOP_FILL` machinery (`results-fill-registry.md:32-36`). Six (or seven) new registry rows bind Table 1b's cells to report fields.
- **Renderer wiring is already built.** Variant A/B/C selection guards (`DRAFT-RESULTS_PROSE.md:2410, 2433, 2478, 2554`), six `ROW_RENDER` blocks with `diagnostic_<row>_present` branches, fixed-order `PRESENT_DIAGNOSTICS_RENDER`. The schema supplies `whole_window_verdict`, per-row `row_outcome`, per-row `diagnostic_present` booleans, `outcome_drift_supported`, and the named value fields. Nothing new renderer-side except R7's tokens.

---

## 8. Failure honesty

**A three-level ladder, all of it already modelled by the template:**

1. **Row `contradicted` under a PASSED window → published as a result.** Variant B renders it and already carries the honesty language (`DRAFT-RESULTS_PROSE.md:2545`). **Schema addition:** every `contradicted` row must render its **pre-registered `consequence_if_contradicted`**, frozen before collection. *A failed characterization row that does not name what it narrows is decorative, not honest.* Fail-closed doctrine extended from data to interpretation.
2. **Row `indeterminate`** → "did not support a conclusion under the registered criterion." No value promoted; absence is never zero (`DRAFT-RESULTS_PROSE.md:2604`).
3. **Window REFUSED → Variant C.** No row promoted; only authenticated diagnostics render in fixed order `linearity, null, empirical_floor, phase_attribution, drift_settling`, with absent rows explicitly listed. `between_sessions` is correctly absent — cross-window, no in-window diagnostic.

**Two schema-level additions:**
- **`protocol_incomplete` is unreachable post-freeze.** If the writer would emit it, it refuses to issue the report — the mechanical retirement of `draft-v1.md:331`.
- **Anti-selection rule on re-collection.** A successor characterization window must carry an explicit `predecessor` link and **both results publish**; the paper reports the sequence, never the best one. **Carefully scoped:** a *window-verdict* failure legitimately re-collects (the current state — both metrology verdicts FAILED, `WINDOW_STATUS.md:91`), but a **`contradicted` row under a PASSED window does not license re-collection to flip it.** The abandon-after-three rule (`draft-v1.md:318`) covers environmental interruption and does not reach this case.
- A report where every row is `supported` **must still publish its refusal log** (`draft-v1.md:326`).

---

## 9. Pedagogy compliance (P06 closure)

P06's demand (`docs/paper/draft-v1-review-round4-pedagogy.md:89`): "For every table row, state the statistic, frozen threshold, sample unit/count, and accept/refuse rule, with **one numeric worked example per mechanism**."

- **Statistic / threshold / unit / count / rule:** §4 supplies all four per row. No adjective criteria survive: "good fit," "stabilize," "test containment" are replaced by MLMR ≤ F, held-out deviation ≤ A_drift, and interval-inside-`[−m,m]`.
- **First-use test — every term glossed at first use in §5:** *criterion*; *row outcome*; *held-out probe* (a reference measured but excluded from building the allowance it will be tested against); *censored* (a time we can only bound, because the protocol stops looking before it happens); *containment* (the whole interval lies inside the limit, not merely fails to exclude zero); *equivalence margin*; *eligible session*; *consequence-if-contradicted*.
- **The worked-example clause is closeable NOW, before collection.** Use retained **diagnostic** numbers, explicitly labelled non-claim-bearing — the paper already does this twice (`draft-v1.md:78`, `:426`). Available today: R7 from `anchor_bound_s = 0.0310738 = 24.879 + 6.195 ms` on `p2015-df-ph-prefill-abs-r01` with the 1.016 J envelope and 32.7 W quotient; R4 from the 0.0 J reintegration discrepancy and 37/50 two-overlap population (`:426`); R5.1 from the re-derived 0.5094 J excursion against the 0.652 J allowance (`:255`). **§5 therefore stops being the weakest section without waiting for the window.**
- **§5 rewrite shape, per row:** forcing problem → what the row measures physically → exact estimator → the limit and *where its number came from* → what a failure would mean and what it costs → worked example with real numbers.

---

## 10. Ruled vs derived vs needs-input — the honest ledger

| Limit | Basis | Source |
|---|---|---|
| R3 level multipliers 0.5×/1×/1.5×/3× | **ruled** | `micro_delta/calibration_plan.json:5`; corroborated D-078 cl.11 "~3x" |
| R5.2 recovery ≤ 180 s | **ruled** | `window_runbook.md:214, :135` |
| R7 quarter-window bound | **ruled** | `joulewise/reduce.py:996-998` |
| R7 cadence ratios 2.0 / 4.0, ≥3 overlaps | **ruled** | `joulewise/reduce.py:117-118`; `draft-v1.md:426` |
| R7 bracket band | **ruled** | issued acceptance edition (bind edition id) |
| R7 dominance | **ruled** | existing `admissible_set_uncertainty_dominates_point_floor` |
| R4.1a τ (float tolerance) | **ruled** | 0.0 J reintegration discrepancy, `draft-v1.md:426` |
| R6 n ≥ 3 | **ruled** | `draft-v1.md:340` |
| R1/R2/R3 sample counts | **ruled** | metrology_v1 plans, already frozen |
| R1 MLMR limit; R2 margin `m` | **derived** | issued alpha/beta `F_operative` — **blocked until alpha/beta issue floors** |
| R4.1b gap bound | **derived** | registered gap duration × observed gap power |
| R4.2 β | **derived** | 1 J ÷ registered ΔT_max (D-078 cl.11 scale) |
| R6 cross-session rule | **derived** | largest single-session declared bound |
| R5.1 held-out probe count | **ed_input_required** | window budget; proposed floor ≥3 |
| R3 sizing-miss tolerance factor | **ed_input_required** | no basis exists |
| R1/R2 fallback absolute limits if no alpha/beta floor at freeze | **ed_input_required** | the schema's largest single dependency |

---

## 11. Written to be attacked — where I expect to lose

1. **R7 as a seventh row.** Costs a template amendment, lint change, census re-run. "Fold it into R4" is coherent; I hold R7 standalone because the paper's headline property deserves its own printed outcome, and D-122 set the precedent.
2. **R1/R2 limits derived from alpha/beta floors.** If alpha/beta have not issued floors when the characterization window is funded, two of seven rows fall to `ed_input_required` and the freeze blocks. A seat arguing for absolute pre-registered joule limits has a real schedule-risk point; my counter is that an absolute limit is exactly the invented number the constraint forbids.
3. **The 1× micro slot registered without an expectation.** Attackable as ducking the hardest case. I hold it: registering an expectation at the gate boundary registers a coin flip.
4. **Contradicted-outranks-indeterminate precedence.** Arguable both ways; chosen so a known failure cannot hide behind an unreached decision.
5. **R5.2's polling proposal** touches the settle path in a runbook that says "DO NOT MODIFY HARNESS CODE" (`long_holds/README.md:12-24`). I read the fence as covering the workload schema, not admission logging, but that reading is contestable — hence the censored fallback.
6. **The metrology_v1 freeze-namespace gap is bigger than the schema.** A seat arguing the schema is premature until those five namespaces land has a sequencing point I would probably concede — but the spec can be authored and ratified in parallel, and authoring it is what unblocks the freeze work order.
