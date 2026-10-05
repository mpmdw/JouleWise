# Analysis plan V5-CLAIM-25G83-B5: what is computed from the claim windows, and how

Status: **DRAFT UNSEALED, 2026-10-05.** Companion to
`configs/campaigns/v5_claim_25g83/registration_block5_draft.md` (the **registration**); the two are sealed
together and neither binds alone. Terms are those built in registration §0; terms that first appear
here are built where they first appear. Every rule is fixed before any claim byte exists. Most
estimators below are already frozen in committed bytes (the D-179 contract, the floor packs'
`extraction_spec.json`, GAMMA's `analysis_manifest_v3.json`); this plan binds those bytes, states the
arithmetic in full so it can be recomputed by hand, and fixes everything they leave open: inputs,
order of operations, exclusions, disclosures and what is printed from which artifact. Numbers in
worked examples are **synthetic** and labelled so; they are not measurements.

**Terms first used here.** **Finalization** binds the identities of the collected bundles, the
whole-window verdict, the bracket and the floor to GAMMA's frozen prospective manifest without reading
any effect estimate; its output is the finalized manifest. The **claim gate** is the program that,
from the finalized manifest, computes each contrast and decides its outcome and claim ceiling. A
**sidecar** is a separately hash-bound file emitted beside the mint (the dominance replay inputs). A
**pinset** is the list of content hashes the mint may consume. The **close-out** is the artifact that
records every dominance ratio and decides branch A or B. A **placement** is a registered site in the
paper where an issued value may be rendered; **D-173 custody** is the only route by which a paper
supplier may read evidence (it names a role and a runs root; the supply map supplies every path and
digest).

## 1. When the analysis runs, and on what

1. It runs once, after the block closes (GAMMA PASS, registration §7) and after the release event
   (registration §9.4), at a commit whose analysis programs are pinned in the seal record (§11).
2. It reads exactly one attempt per pack: the attempt whose harvest verdict is PASS. The fixed order
   (registration §3.1) means no pack has two PASS attempts.
3. It reads evidence only through the authenticated routes named in §3 (for paper suppliers, D-173's
   `open_paper_input(role, runs_root)`); no caller-supplied path, digest or value enters a number.
4. Everything it emits is retained in analysis custody `FILL[B5-ANALYSIS-CUSTODY-ROOT]` and handed to
   the results cold gate (registration §10.3) before any paper sentence is filled.

## 2. Inclusion and exclusion

### 2.1 Attempts

Non-PASS attempts (NULL, RECOVER, REFUSED) are never inputs to any number. They are listed with their
cause codes and classes in the attempt history (§8). Superseded blocks (registration §7.4) are handled
by their own design record.

### 2.2 Members

No member is excluded after collection. A PASS window has, by construction, every member valid
(registration §6). The rules for a valid member whose *phase* cannot be resolved (fewer than 3 power
records overlap the phase, reducer outcome `not_resolvable_sample_count`) are:

- **Reported cell:** the cell refuses (`missing_or_invalid_member: refuse_reported_mean`); no 49-member
  mean is ever computed (D-179 ruling 1). The refusal and its member are printed.
- **Contrast:** the block containing that member is incomplete; the claim gate records
  `paired_block_incomplete` and `fixed_n_plan_incomplete`, so the outcome is `not_resolvable` (or
  `not_estimable`, if the engine also records a reason of that class; §7). No block is replaced.

The environmental diagnostic (registration §8) never excludes a member; it is disclosed (§8).

### 2.3 Partial blocks

If the block ends in END STATE after ALPHA and/or BETA passed, no analysis runs by default. The END STATE
design record decides whether the passed windows' L1 reported cells (§4) are analysed alone; contrasts
(§7) and dominance ratios (§6) need all three windows and are never computed from a partial block.

## 3. Order of operations

Each step runs on the bytes of the step before it; each output is content-addressed (SHA-256) and the
next step authenticates it. Commands are those of `docs/process/v5-artifact-flow.md` at the pinned head.

| # | Step | Program | Output |
|---|---|---|---|
| 1 | Strict validation of every bundle of the three PASS windows | `python -m joulewise validate-bundle --strict` | exit 0 per bundle |
| 2 | Re-reduction into restricted custody (never inside a bundle) | `python -m joulewise reduce … --output …rereduced.json` | summary schema 0.1 per bundle |
| 3 | L10-B rehearsal: floor extraction and mint on a scratch copy (already run between BETA and GAMMA, registration §3.3) | `scripts/extract_detection_floors.py`, `scripts/mint_floor_artifact_generalized.py` | `L10_B_FLOOR_PRODUCER` record |
| 4 | Floor extraction, ALPHA and BETA separately, each with its pack's `extraction_spec.json` | `scripts/extract_detection_floors.py … --hash-bundles` | `joulewise.detection_floor_extraction.v1` ×2 |
| 5 | Production mint of the aggregate floor and its dominance replay sidecar | `scripts/mint_floor_artifact_generalized.py` with `FILL[V5-FINAL-PINSET]`, `FILL[V5-V2-INPUT-MANIFEST]` | `joulewise.detection_floor_artifact.v2`; `joulewise.d165_dominance_replay.v1` |
| 6 | Dominance close-out | adapter `FILL[MINT-TO-CLOSEOUT-ADAPTER]`, then `scripts/build_d165_dominance_closeout.py` | `joulewise.d165_dominance_closeout.v1` |
| 7 | L10-C rehearsal of steps 8, 9 and 11 on a scratch copy | `docs/process/v5-l10-rehearsal-phase.md` §L10-C | `L10_C_FULL_EDGE` record |
| 8 | Finalization of GAMMA's prospective manifest with its five attachments (whole-window verdict, bracket binding, ledger, aggregate floor, dominance replay sidecar) | `scripts/finalize_analysis_manifest.py` | `am-3283e9d3….finalized.json` |
| 9 | Claim gate | `python -m joulewise analyze-claims --analysis-manifest … --runs-root … --evidence-root evidence-d117-floor-qwen3-1p7b-v5=… --evidence-root evidence-d117-floor-qwen3-8b-v5=… --floor-artifact …` | `joulewise.claim_verdicts.v1` |
| 10 | Reported-energy projection, three cells per model | production issuance of `joulewise.paper_reported_energy_projection.v1` through D-173 custody, `FILL[REPORTED-ENERGY-ISSUER]` | one projection per model |
| 11 | Results fills for adopted placements only | adapter `FILL[CLAIM-VERDICT-TO-FILL-ADAPTER]`, then `scripts/render_results_fills.py` and `--validate-rendered` | validated Markdown |
| 12 | Results cold gate: re-derive every printed number from the artifacts of steps 4–10 | judge + refuter | gate record |

A refusal at any step stops the steps after it. A tooling refusal goes to R3 and the step re-runs on
identical bytes; a refusal that is a registered scientific outcome (for example a not-resolvable
contrast) is the result and is printed as such.

## 4. Estimator 1: reported phase energy per model and phase (D-179)

**What it is.** For each model and each of decode, prefill-p42 and prefill-p2048, one gross phase
energy averaged over the cell's 50 ordered members, with an interval that respects the 20 independence
units. Normative home: `docs/contracts/paper_reported_energy.md`; registration digests in each floor
pack's `extraction_spec.json` (`reported_energy_registration.registration_sha256`: qwen3-1p7b at
L = 2048 `5560857668f053c99d0369161d4735015f4678a160b7a8423c7a7f357a50f5ea`, qwen3-8b at L = 2048
`04657a74de839a48ebf6bf55fe66f299fdd2e6401353c76d87d4d6ae843dae79`).

**Members.** Ordinals 1–10 are the absolute repeats; 11–50 are the ten null blocks in A1, B1, B2, A2
order. Decode and prefill-p42 read the same 50 bundles (the decode stages); prefill-p2048 reads the 50
bundles of the p2048 stages.

**Arithmetic, in the order the code performs it.** Let E1…E50 be the members' gross phase energies
(`phase_energy_j.decode` or `phase_energy_j.prefill`), r the first ten, and b_j the mean of block j's
four members.

1. Mean: `m = statistics.fmean(E1…E50)`. In exact arithmetic m = 0.2 × mean(r) + 0.8 × mean(b),
   because 10 of the 50 members are repeats and 40 are block members; the code uses the fifty-member
   mean.
2. Variance of m from the two strata: `V = 0.2² × s_r² / 10 + 0.8² × s_b² / 10`, with s_r and s_b the
   sample standard deviations (`statistics.stdev`, divisor n − 1) of the ten repeats and of the ten block
   means. Pooling all 20 units into one s/√20 is rejected: it weights the units equally in the variance
   but not in the mean.
3. Half-width: `h = t(0.975, 9) × √V` with `t(0.975, 9) = 2.262157162798205` (9 degrees of freedom, the
   conservative reference).
4. Recorded timing bounds: every member records three non-negative energy bounds,
   `E_clock_anchor_shift_bound_j`, `E_interpolation_joint_edge_bound_j` and
   `E_whole_window_drift_allowance_j` (how far its phase energy could move if the clock anchor, the
   phase edges inside their power records, or the whole-window drift sat at their registered limits).
   Average each kind over the 50 members; `B = math.fsum` of the three averages. A missing kind refuses
   the cell; it is never zero by default.
5. Endpoints: `lower = m − h − B`, `upper = m + h + B`, evaluated in that order and not clamped at zero.
6. Per-token value: `ΣE / ΣT` over the same 50 members (a ratio of totals, never a mean of ratios), with
   T the runtime-observed output tokens for decode and the runtime-observed prompt tokens for prefill
   (the four prompt-count surfaces must agree, else `paper_reported_energy_prompt_surfaces_disagree`).
   A bad denominator refuses the per-token value only, not the mean.
7. The D-078 attribution floor (about 1 J) is printed beside the cell and never added into its interval.

**Worked example (synthetic).** Repeats r = 10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8, 10.1, 10.0, 9.6 J
(mean 10.0, s_r = 0.2); block means b = 10.4, 10.1, 10.3, 10.2, 10.5, 10.0, 10.2, 10.3, 10.1, 9.9 J
(mean 10.2, s_b = 0.18257). m = 0.2 × 10.0 + 0.8 × 10.2 = 10.16 J. V = 0.04 × 0.04 / 10 + 0.64 ×
0.033333 / 10 = 0.0022933; √V = 0.047889; h = 2.262157 × 0.047889 = 0.10833 J. With kind averages
0.010, 0.020 and 0.030 J, B = 0.060 J, and the interval is [9.9917, 10.3283] J. For decode with 512
output tokens per member, ΣE / ΣT = 508.0 J / 25,600 tokens = 0.019844 J/token.

**Outputs per cell** (closed schema `joulewise.paper_reported_energy_projection.v1`): `mean_j`,
`lower_j`, `upper_j`, `per_token.j_per_token`, `n_bundles` (= 50), plus the recomputation record
`interval {method, n_r, n_b, df, s_r, s_b, variance, h_j, kind_averages_j, B_j}`. The four paper cells
are decode and prefill-p2048 for each model; the two p42 cells are computed and retained, not printed.

## 5. Estimator 2: floors

**What a floor is, physically.** In a null block both arms run the identical workload, so any A-versus-B
difference is produced by the instrument and the machine: sampler timing, where a phase edge falls
inside a 100 ms record, drift. The floor of a cell is the largest such false difference the registered
estimator allows, computed from that cell's absolute repeats and null blocks. A real contrast smaller
than its floor cannot be told apart from instrument error.

**Binding.** Each floor pack's `extraction_spec.json` defines six floor cells per model (decode,
prefill-p42 and prefill-p2048, each in an absolute and a comparative null-block form, for example
`d117-df-ph-decode-qwen3-1p7b-absolute` and `d117-df-cmp-abba-ph-decode-qwen3-1p7b`; ALPHA spec
`03fe7be896c50a21b97d38c914b813988d1fa6ac645df773b69e238c220b28af`, BETA spec
`8c984e6b82dce443f7dcc1cf57ea8ec890e5c77e216a365569762c45340ae811`). The comparative cells use the D-124
two-shared-edge common-mode estimator (`d124_two_shared_edge_common_mode.v1`, parameter digest
`dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38`): the block's phase onset and offset
may each move by one shared amount within the registered timing domain, the bundle-specific residuals
are taken at their adversarial extremes, and the worst apparent difference is the width; the allowance
is applied exactly once and identically on the floor cells and on the consuming contrast. The normative
arithmetic is the extraction and mint code at the sealed head; this plan adds no alternative floor.

**How GAMMA uses them.** For each contrast, each arm's floor comes only from its own model's cells for
the same phase and length (`exact_stack_only.v1`; no cross-length transport), taken worst-case over that
stack's components; the contrast's gate `floor_gate_j` is the larger of the two arms' floors
(`cross_stack_armwise_max.v1`).

## 6. Estimator 3: dominance ratios (D-165, D-168)

**The forcing question.** Is timing attribution actually the part of the floor that limits the
measurement? For each model, phase and form, `R = corner_widened_unguarded_floor_j /
point_unguarded_floor_j` compares the floor with phase edges free to move inside the timing domain
against the floor with edges fixed at their point estimates; R ≥ 2 (equality passes) means edge
movement at least doubles the floor. There are exactly eight independent ratios (2 models × 2 phases ×
absolute and comparative) and four comparative common-mode ratios R_cm (shared-sign/local-corner
replay). A zero denominator refuses; Infinity and NaN are never emitted. **Branch A** (every independent
R ≥ 2 and every required R_cm ≥ 2) licenses the dominance sentence and the contingent subtitle;
otherwise **branch B** reports each failed component with null framing. R_cm passing licenses no
physical-common-time robustness claim (D-165 addendum 2026-09-04). Output: the close-out artifact's
eight plus four records and its recomputed global flags.

## 7. Estimator 4: the two GAMMA contrasts

Frozen in GAMMA's `analysis_manifest_v3.json` (manifest id
`am-3283e9d37ffe36895c77b6168e2688793061b5b8edc48690211fb72b8811e128`, frozen semantics
`dfe508c2be5da02118bcb0d923f31a06a2bc686bd470fb7bbfa6cff2d391111e`, file SHA-256 per GAMMA's plan tree
`c3fd5405dd7e126431d56723a059abee67e7cb3b8471aab92fd9c63896ae835c`).

| Contrast id | Metric | Arms (A, B) | Blocks |
|---|---|---|---|
| `ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b` | `phase_energy_j.decode` | 1.7B, 8B | 10 |
| `ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b` | `phase_energy_j.prefill` | 1.7B, 8B | 10 |

Both are primary and two-sided, with registered direction positive (8B uses more phase energy than
1.7B), in one Holm family (`d117-gamma-decode-prefill-p2048-primary-holm-v5`, m = 2, α = 0.05), fixed
n = 10 blocks, zero replacements.

**Arithmetic** (`abba_block_arm_mean_difference_t_v1`; block construction in
`joulewise/analysis_engine/__init__.py`, estimate in `estimators.py:estimate_paired_blocks`):

1. Per block k: `d_k = (B1 + B2)/2 − (A1 + A2)/2`.
2. `dbar = mean(d_k)`; `s_d` = sample standard deviation; `se_rep = s_d / √10`.
3. Metrology term: each member records governed random-error variances (the reducer's estimates of
   random measurement error in its phase energy; the gross-repetition term is left out because
   block-to-block repetition is already in se_rep). For each such term, the block's paired variance is
   `(var_A1 + var_A2)/4 + (var_B1 + var_B2)/4` (members independent); summed over blocks and divided by
   n² it is that term's squared standard error; `se_met` is the root of their sum.
   `se_total = √(se_rep² + se_met²)`.
4. `t* = round(t(0.975, 9), 3) = 2.262`; metrology-aware 95% interval `dbar ± t* × se_total`.
5. Deterministic bound total D: for each recorded deterministic kind, a block's bound is the A-arm mean
   of its two members' bounds plus the B-arm mean of its two; D is the sum over kinds of the mean over
   blocks. No cancellation across arms is assumed. The decision interval is the metrology interval
   widened by D on both sides.
6. Test: `t = dbar / se_total`, two-sided Student-t p-value with 9 degrees of freedom. Holm (the
   correction that keeps the chance of any false positive across the family at α) with m = 2:
   with p(1) ≤ p(2), adjusted p~(1) = min(1, 2 p(1)) and p~(2) = min(1, max(2 p(1), p(2))); a contrast
   is rejected when its adjusted p ≤ 0.05. A contrast that is not estimable keeps m = 2.

**Outcome, in this precedence** (`joulewise/analysis_engine/claims.py:evaluate_claim`):

1. `not_estimable`: manifest, floor-artifact, metric or token-identity failure, or fewer than 2
   complete blocks.
2. `not_resolvable`: no floor, any incomplete or invalid block, a whole-window or admission failure,
   `|dbar| ≤ floor_gate_j` (`effect_not_above_floor`), or the decision interval contains 0 while the
   metrology interval does not (`deterministic_bound_obscures_direction`).
3. `unresolved`: the metrology interval contains 0, or Holm does not reject.
4. `direction_supported`: otherwise; the direction is the sign of dbar.

The claim ceiling is L2 only when the outcome is `direction_supported`, the direction equals the
registered positive direction, the contrast is primary and confirmatory, and no sensitivity flag
(randomization check, leave-one-block-out) is raised; otherwise L1 wording.

**Worked example (synthetic).** d_k = 3.1, 2.9, 3.3, 3.0, 2.8, 3.2, 3.1, 2.9, 3.0, 2.7 J: dbar = 3.0 J,
s_d = 0.18257, se_rep = 0.057735. With a paired variance of 0.0100 J² in every block,
se_met = √(10 × 0.0100 / 100) = 0.031623 and se_total = √(0.0033333 + 0.0010000) = 0.065828. The
metrology interval is 3.0 ± 2.262 × 0.065828 = [2.8511, 3.1489] J; with D = 0.05 J the decision
interval is [2.8011, 3.1989] J. t = 45.6, so p is far below 0.025. With a floor of 1.2 J, |dbar| exceeds
the floor, neither interval contains 0, Holm rejects, and dbar > 0 matches the registered direction:
`direction_supported`, ceiling L2.

## 8. Disclosures computed beside the claims

All are computed by code from structural or non-science evidence and printed with the results:

- **Attempt history:** every attempt of every pack with its verdict, cause codes and class.
- **Battery:** each window's #421 verdict (computed before any energy was read).
- **Clock:** the number of members with anchor status `bounded` (all, in a PASS window) and the largest
  effective bound per window.
- **Reference drift:** each window's NEG-8 whole-window result.
- **Environment:** per cell and per window, the count of science members flagged by
  `FILL[ED-PREDICATE]`, and the idle-drift flags of registration §8 item 3. Wording if any member is
  flagged: "N of the 50 members of this cell showed background activity by the registered diagnostic;
  they are included, as registered." No re-estimate without them is computed.
- **Separate windows:** the 1.7B and 8B reported cells were collected in separate windows in a fixed
  order; their difference is not a comparison (claims ladder: forced order stays below L2).
- **D-177:** phase attribution is reported without a measured instrument phase-accounting check.
- **Fixed prompt:** the decode contrast uses one fixed prompt (D-166 addendum); no prompt-population
  generality is claimed.

## 9. What is printed, and from which artifact

Under the current D-174 fallback no row below has a placement; each becomes printable only through the
placement ruling of registration §15 Q5. Site ids are the proposed `CP-X…` sites of
`docs/contracts/paper_comparison_placements.md`.

| Printed quantity | Artifact (schema) | Field | Proposed site | Status now |
|---|---|---|---|---|
| Models, workload, L = 2048 | selection record; prompt pin; panel | `selected_prefill_tokens`; pinned identities | CP-X01-identity, CP-X01-length | PROPOSED_STOP_FILL |
| Reported energy: mean, interval, J/token, n (4 cells) | `joulewise.paper_reported_energy_projection.v1` | `mean_j`, `lower_j`, `upper_j`, `per_token.j_per_token`, `n_bundles` | CP-X05-* | RETIRED_FALLBACK (needs a ruling) |
| Attribution floor beside each cell | projection binding | `binding.attribution_floor_j` | CP-X05-* | RETIRED_FALLBACK |
| Floors (4 model/phase cells) | `joulewise.detection_floor_artifact.v2` | `floor_gate_j` and component census | CP-X04-* | PROPOSED_STOP_FILL |
| Dominance ratios; branch sentence; subtitle | `joulewise.d165_dominance_closeout.v1` | 8 R, 4 R_cm, `branch`, licensing flags | CP-X02-*, CP-X03-* | PROPOSED_STOP_FILL |
| Contrast tables (decode, prefill) | `joulewise.claim_verdicts.v1` + finalized manifest | `estimator`, `deterministic_bounds.decision_interval`, `floor`, `multiplicity`, `claim_evaluation` | CP-X06-table, CP-X07-table | PROPOSED_STOP_FILL |
| Verdict sentences (abstract, discussion, conclusion) | `joulewise.claim_verdicts.v1` | `claim_evaluation.outcome`, `direction`, `claim_level_ceiling` | CP-X08-* | PROPOSED_STOP_FILL |
| Before-comparison refusal (if any window or gate refuses) | campaign log, whole-window verdict | governing row and reason | CP-X09-* | PROPOSED_STOP_FILL |
| Disclosures of §8 | harvest records, whole-window verdicts, ED output | counts and verdicts | `FILL[DISCLOSURE-SITES]` | not proposed yet |

Every printed number is copied or conservatively rendered from these fields (`MEASURED`) or derived by
a formula named here (`DERIVE`); none is recalculated from prose.

## 10. Analysis-plan rows (`docs/contracts/analysis_plans.md` fields)

| Field | Decode contrast | Prefill-p2048 contrast | Reported cells (each) |
|---|---|---|---|
| Plan id / consumer | `B5-GAMMA-DECODE` / phase-energy paper | `B5-GAMMA-PREFILL-P2048` | `B5-REPORTED-<model>-<phase>` |
| family_id, role | `d117-gamma-decode-prefill-p2048-primary-holm-v5`, primary | same, primary | none (L1, no inference across cells) |
| Selection scope | decode, Qwen3 1.7B vs 8B, prompt 0, forced 512 | prefill at 2048 tokens, same pair | one model, one phase, its 50 members |
| Multiplicity | Holm, m = 2, α = 0.05 | same | none |
| Metric, window class | gross `phase_energy_j.decode`, phase window | gross `phase_energy_j.prefill`, phase window | gross phase energy, phase window |
| Unit, dependence | A/B/B/A block arm-mean difference, 10 blocks | same | 10 repeats + 10 blocks (20 units) |
| Estimator | §7 | §7 | §4 |
| Inclusion, waivers | strict-valid, anchor bounded; no waivers | same | same; any absent member refuses |
| Order, blocking, covariates | ABBA order cancels linear drift; no covariates | same | fixed member order |
| Floor gate | `floor_gate_j`, armwise max (§5) | same | attribution floor printed beside, not a gate |
| n sizing, top-up | fixed n = 10 from the frozen manifest; no replacement, no top-up | same | fixed 50 |
| Denominator | none (J per phase) | none | runtime-observed tokens |
| Holdout | not applicable (L2) | not applicable | not applicable |
| Ceiling; forbidden upgrade | L2; no claim about other prompts, lengths, models or machines | L2; same | L1; no model comparison from these cells |
| Disqualifiers | §7 outcomes 1–3; sensitivity flags | same | D-179 refusal codes |
| Linked manifests | filled after execution from the finalized manifest and bundle hashes | same | projection bindings |

## 11. Analysis code that must exist (pinned in the seal record)

| Need | State at this writing | FILL |
|---|---|---|
| Production reported-energy issuance through D-173 custody | Absent ("No production dispatch exists", `joulewise/paper_reported_energy.py:457`) | `REPORTED-ENERGY-ISSUER` |
| `_v5` final pinset and v2 input manifest for the mint | Absent (`docs/process/v5-artifact-flow.md`, "What does not exist yet") | `V5-FINAL-PINSET`, `V5-V2-INPUT-MANIFEST` |
| Mint-to-close-out adapter | Absent (same source) | `MINT-TO-CLOSEOUT-ADAPTER` |
| Claim verdicts to results-fill input (RENDERER-V5-SUCCESSOR-01) | Absent (same source) | `CLAIM-VERDICT-TO-FILL-ADAPTER` |
| Environmental diagnostic producer | Not designed (registration §8) | `ED-PREDICATE` |
| Disclosure producer for §8 | Absent | `DISCLOSURE-PRODUCER` |

Preferred: each merged under the normal gates (with the measurement-code final pass) and pinned before
`ALPHA-1` arms. Permitted otherwise: written and merged before the release event by seats that have read
no claim-window energy, against this plan's text, and pinned in a seal-record extension before the
analysis runs.

## 12. What the analysis never does

- Exclude, replace, reweight or re-collect a member after collection; compute a mean over fewer than
  the registered members; pool members across attempts or windows.
- Use the pooled s/√20 interval, a mean of per-member ratios, configured token counts, the
  `detection_floor.py` √(1 + 1/n) prediction term, or any floor other than the minted one.
- Treat the ALPHA-versus-BETA difference of reported means as a comparison.
- Test one-sided, change α, m, the registered direction or the contrast set, or add a contrast.
- Read an energy before the release event, or let any energy value inform a recovery decision.
- Report any analysis not registered here except as clearly labelled exploratory.

## 13. FILLs specific to this plan

`B5-ANALYSIS-CUSTODY-ROOT`, `V5-FINAL-PINSET`, `V5-V2-INPUT-MANIFEST`, `MINT-TO-CLOSEOUT-ADAPTER`,
`REPORTED-ENERGY-ISSUER`, `CLAIM-VERDICT-TO-FILL-ADAPTER`, `DISCLOSURE-PRODUCER`, `DISCLOSURE-SITES`,
and `ED-PREDICATE` (shared with the registration). The open questions are registration §15; Q5
(placement) and Q10 (code timing) bear directly on this plan.
