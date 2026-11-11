# Block 5 results: the two registered GAMMA contrasts (Qwen3-8B minus Qwen3-1.7B)

Written 2026-11-08 by an Opus 5.5 seat for the Block-5 lead (interactive session 1544c617). It was written after Ed's
unseal OK for Block 5 (`RUN_STATE.md` item 231, recorded before any outcome was read) and after the release check
agreed (item 229).

**What this seat read.** Only these restricted Block-5 files were opened, read-only:

- the dry-run custody `/Users/edr/jw-b5-custody/dry-m/dry-run/`;
- the release-check output `/Users/edr/jw-b5-custody/release-check-final-20261108T0942Z/`.

No BYTES, ALIGN v4, Block 6 or `night-*` path was opened. Paths that appear inside the artifacts, such as the archive
roots the recompute names, were not followed.

**Arithmetic.** No new statistic was computed. Every number below is copied from a registered output, except numbers
marked **(derived)**. Those are simple ratios or counts of registered outputs, and each one shows how it was formed.

---

## 0. Sources and how to trace a number

Each number cites a file alias and a JSON key path. Paths are relative to the custody root named in the table. The
files under `outputs/`, `finalized/` and `disclosures/` are named by their own SHA-256, and this seat re-hashed each one
and found it equal to its name.

| Alias | File | SHA-256 |
|---|---|---|
| FILL | `dry-m/dry-run/restricted/outputs/a29c6cf2…-results-fill-input.json` (validated step-11 fill input) | `a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4` |
| CV | `dry-m/dry-run/restricted/outputs/67d8c231…-claim-verdicts.json` (claim gate, step 9) | `67d8c231eeb5df2e1240cd3d0b965555ab39755042a2b9676f939f1543716f27` |
| EXC | `dry-m/dry-run/restricted/finalized/analysed-attempt-exclusions-a9954365….json` (GAMMA exclusion function) | `a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46` |
| DISC | `dry-m/dry-run/restricted/disclosures/77be1a3e….json` (registered disclosure lines, §8) | `77be1a3ed3a851206a0762334cbdeaab5b40e83e3d9fcdbcf404da5e4d871f6a` |
| SENS | `dry-m/dry-run/restricted/outputs/4a7c4315….json` (Erratum-3 bracket sensitivity) | `4a7c4315327d29b214e79961d6f991af13dcabc24898368564007ac2e356ff28` |
| STEP | `dry-m/dry-run/restricted/outputs/b0f80f72….json` (stored-verdict step results) | `b0f80f7265cf84203ded237245ae25cf87adfd987c2265a92b52c96efb1ea5b5` |
| PROJ-A, PROJ-B | `dry-m/dry-run/restricted/outputs/{ed3cadb1…-projection-alpha, db6d5251…-projection-beta}.json` | `ed3cadb1f0ac…`, `db6d525129f9…` |
| REC | `dry-m/dry-run/B5-BLIND-DRY-RUN-RECORD.json` (only its header and step rows were read) | `66adc66e89f1a621009dd2ca98bc7c41b202d5c43a26a82af8a633a54c34aa03` |
| RC | `release-check-final-20261108T0942Z/recompute.json` (independent recompute; program SHA-256 `d49103e8…`) | `c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc` |
| CMP | `release-check-final-20261108T0942Z/comparison.json` (comparator) | `b12b7e1b32b27159be894221dcde7e334784061314fe91a39166faa36f72f4c9` |
| VER | `release-check-final-20261108T0942Z/verdict.json` (release verdict) | not re-hashed |

**Pins.**

- **Analysis.** The commit is `ab1e0098dbd0ab839c8f278088221aa8aa4de8d2`, tag `b5/analysis-r4` (`REC.analysis_commit`;
  `VER.pinned_commit`).
- **Release check.** It ran from main `02ef89f5c` (`VER.release_checkout.commit`) and its verdict is `agree`, exit 0.
- **Windows analysed.** One attempt per pack (`FILL.campaigns`; `DISC.block_lines[attempt_history]`):
  - ALPHA `v5-b5-alpha-a1-20261009T2312Z` (Qwen3-1.7B floors);
  - BETA `v5-b5-beta-a6-20261011T2011Z` (Qwen3-8B floors);
  - GAMMA `v5-b5-gamma-a1-20261012T0420Z`, which runs both models in A/B/B/A quads. Both contrasts come from GAMMA.

**Stack and boundary** (registration §0.5, §0.19 and §1; `CV.bundle_audit[*].token_provenance`):

- **Hardware and software.** An Apple M3 Max laptop on macOS build 25G83, running MLX. The models are
  `mlx-community/Qwen3-1.7B-4bit` (revision `3b1b1768…`) and `mlx-community/Qwen3-8B-4bit` (revision `545dc425…`).
- **Generation.** Greedy decoding with exactly 512 runtime-observed output tokens (`fixed_budget_exact`, stop reason
  `requested_tokens_emitted`).
- **Prompts.** One fixed 42-token decode prompt (`real_prompts_v1` item 0) and one fixed 2048-token prefill prompt.
- **Boundary.** `M3 Max / MLX / powermetrics SoC rails`. This is the gross CPU + GPU + ANE package-rail energy over a
  phase. It is not wall energy and not whole-machine energy.

---

## 1. Headline results (primary Holm family, m = 2, α = 0.05)

The family is `fam-d117-gamma-decode-prefill-p2048-primary-holm-v5` (`CV.families[0]`). `structural_status` is
`complete`, `missing_test_ids` is empty, and Holm rejects both contrasts.

| Quantity | Decode (`ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b`) | Prefill p2048 (`ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b`) | Key (under `FILL.gamma.contrasts[i]`, i = 0 decode, 1 prefill) |
|---|---|---|---|
| Orientation | 8B minus 1.7B (`condition_b_minus_condition_a`) | same | `.conditions.difference_orientation` |
| Metric | `phase_energy_j.decode`, J per request | `phase_energy_j.prefill`, J per request | `.metric.name` |
| Kept quads / planned | 6 / 10 | 5 / 10 | `.sampling.kept_n`, `.sampling.planned_n` |
| Estimate d̄ | **146.62940 J** | **101.80943 J** | `.estimate` |
| s_d, se, df, t* | 0.18010 J; 0.073524 J; 5; 2.571 | 0.29710 J; 0.132867 J; 4; 2.776 | `CV.contrasts[i].estimator.{s_d,SE_total}`, `.df`, `.t_critical_95` |
| Metrology 95% interval (within-window statistical only) | [146.44037, 146.81843] J | [101.44060, 102.17827] J | `.interval.{lower,upper}` (= `CV…estimator.metrology_aware_CI95`) |
| Deterministic bound D (clock anchor + interpolation + drift allowance) | 5.08409 J (4.11056 + 0 + 0.97352) | 5.63310 J (4.65958 + 0 + 0.97352) | `.deterministic_widening_total`; `CV.contrasts[i].deterministic_bounds.terms` |
| **Decision interval** (metrology interval widened by D) | **[141.35628, 151.90252] J** | **[95.80749, 107.81138] J** | `.decision_interval.{lower,upper}` |
| Active detection floor (armwise max) | **10.17807 J** (1.7B arm 5.76593; 8B arm 10.17807) | **8.83026 J** (1.7B arm 8.21484; 8B arm 8.83026) | `.floor.active_floor_j`; `.floor.arm_gates[*].floor_gate_j` |
| Floor class | `attribution_limited`, source `E_clock_anchor_shift_bound_j` | same | `.claim_evaluation.floor_limit.{floor_limit_class,floor_source}` |
| Raw p | 6.0165e-16 | 1.7404e-11 | `.multiplicity.raw_p` |
| Holm-adjusted p | **1.2033e-15** (rejected) | **1.7404e-11** (rejected) | `.multiplicity.{adjusted_p,rejected}`; `CV.families[0].adjusted_p_values` |
| Outcome / direction | `direction_supported` / positive (registered: positive) | `direction_supported` / positive | `.claim_evaluation.{outcome,direction}`; `.hypothesized_direction` |
| Claim ceiling | **L2** (`claim_ready_for_l2_l3` true; reason codes none) | **L2** (same) | `.claim_evaluation.{claim_level_ceiling,claim_ready_for_l2_l3,reason_codes}` |
| Leave-one-quad-out | complete; 6 rows, each `direction_supported`, `above_floor`, no influence trigger; estimates 146.570–146.667 J | complete; 5 rows (n = 4 each), each `direction_supported`, `above_floor`, no trigger; estimates 101.683–101.865 J | `.loo.{status,rows[*]}` |
| Randomization check | `not_required` (fixed order, registered) | same | `CV.contrasts[i].randomization_check.status` |
| Sensitivity status | `clean` | `clean` | `CV.contrasts[i].sensitivity_status` |
| Confirmatory status; top-up; replacements | `confirmatory`; none; none | same | `.sampling.confirmatory_status`; `CV.sampling_audit.{top_up_detected,valid_replacements}` |

Two things in this table need care.

- **There are two intervals.** The lead's headline "CI95 146.44–146.82" is the **metrology interval**. That interval
  covers only quad-to-quad scatter within one window. The registered decision rule also uses the **decision
  interval**, which adds the deterministic timing bounds D (analysis plan §7.1 step 5). The paper should print the
  decision interval as the result and the metrology interval as its statistical part.
- **"Sensitivity clean" means the Erratum-3 bracket sensitivity only.** With the sensitivity bound in place, every
  floor, D and outcome equals the primary (`SENS.contrasts[*].{outcome_equals_primary,bound_independent_values_equal_primary}`).
  It is not the registered load-correlated sensitivity line, which L9 could not compute (§7, concern 2).

**Per-quad differences** (d_k, kept quads in id order; `RC.contrasts[cid].d_k`; checked through the d̄ and s_d rows
of the comparator):

- decode: 146.637, 146.443, 146.646, 146.439, 146.685, 146.926 J (b02, b03, b04, b07, b08, b10);
- prefill: 101.588, 101.737, 101.604, 101.802, 102.316 J (b02, b03, b05, b07, b08).

**Derived margins (derived; from the rows above).**

| | Decode | Prefill |
|---|---|---|
| d̄ ÷ active floor | 146.629 / 10.178 = 14.4 | 101.809 / 8.830 = 11.5 |
| Decision-interval lower end ÷ floor | 141.356 / 10.178 = 13.9 | 95.807 / 8.830 = 10.9 |
| Decision half-width ÷ d̄ | 5.273 / 146.629 = 3.6% | 6.002 / 101.809 = 5.9% |
| D ÷ decision half-width (share of the width that is the deterministic timing bound, not scatter) | 5.084 / 5.273 = 96% | 5.633 / 6.002 = 94% |
| Clock-anchor term ÷ D | 4.111 / 5.084 = 81% | 4.660 / 5.633 = 83% |

### 1.1 Registered descriptive magnitudes (analysis plan §7.3; never gating)

From `DISC.contrasts[label=magnitude_ratio|magnitude_per_token]`. They are compared by the comparator families
`descriptive_ratio` (6 rows) and `per_token_j` (10 rows), all AGREE (`CMP.comparisons[family=…]`).

| | Decode | Prefill p2048 |
|---|---|---|
| Ratio of phase energies, 8B to 1.7B (geometric mean over kept quads; **timing bounds not propagated**) | 3.8577 [3.8499, 3.8655] | 4.8840 [4.8580, 4.9100] |
| Difference per token | **0.286386 J per output token** (÷ 512) | **0.049712 J per prompt token** (÷ 2048) |
| — metrology interval | [0.286016, 0.286755] | [0.049532, 0.049892] |
| — decision interval | [0.276086, 0.296685] | [0.046781, 0.052642] |

### 1.2 The four L1 reported cells (side by side only; NOT a comparison)

ALPHA and BETA were collected in separate windows, in a fixed order. The registration (§1; fixed sentence
`separate_windows`) puts their side-by-side reading at L1, and analysis plan §12 forbids treating the ALPHA-versus-BETA
difference as a comparison. The values come from `SENS.reported_cells[*].primary` and `PROJ-A|B.cells[*].per_token`
(comparator family `reported_cell_j`, 144 rows, AGREE).

| Cell (window) | Mean phase energy | Interval | h | B (timing term) | Attribution floor | Kept units (n_r, n_b) | J per token (runtime-observed) |
|---|---|---|---|---|---|---|---|
| Qwen3-1.7B decode (ALPHA) | 51.20643 J | [48.92960, 53.48326] | 0.09802 | 2.17881 | 2.12935 | 10, 8 | 0.100013 per output token |
| Qwen3-1.7B prefill p2048 (ALPHA) | 26.25391 J | [23.32742, 29.18040] | 0.13223 | 2.79425 | 2.72478 | 9, 8 | 0.0128193 per prompt token |
| Qwen3-8B decode (BETA) | 198.36172 J | [195.23985, 201.48359] | 0.15284 | 2.96903 | 2.85109 | 7, 7 | 0.387425 per output token |
| Qwen3-8B prefill p2048 (BETA) | 128.28329 J | [125.19070, 131.37588] | 0.10233 | 2.99026 | 2.84206 | 9, 6 | 0.0626383 per prompt token |
| p42 cells, both models | refused `paper_reported_energy_record_invalid`; registered `expected_unresolvable` | — | — | — | — | — | — |

**Cross-window check** (`DISC.cells[label=cross_window]`). This compares the reported cells with GAMMA's per-arm
estimates of the same quantity.

- 1.7B decode: +0.10423 J, agrees.
- 1.7B prefill: −0.04107 J, agrees.
- 8B prefill: −0.26101 J, agrees.
- **8B decode: −0.42167 J, which is "more than their within-window intervals cover; the reported intervals understate
  between-window variation"** (the registered sentence).

---

## 2. Exclusions

### 2.1 What was removed, and by which registered rule

**The rule chain.**

1. The harvest writes flags.
2. The flag catalog (`configs/campaigns/v5_claim_25g83/flag_catalog.json`, SHA-256 `5d77c725…`) gives each code its
   effect. Every code below has effect `EXCLUDE_MEMBER`.
3. Registration §6.6 then removes the whole quad: "A removed quad member removes its whole quad, so the A, B, B, A drift
   cancellation is kept. In GAMMA a quad with any removed member is dropped from its contrast."

So 9 quads × 4 bundles = **36 bundles** were removed. They are the 36 `bundle_audit` rows with reason
`unit_removed_by_exclusion_function` (`CV.bundle_audit`): decode 8 + 8, prefill 10 + 10.

**The exclusion function's inputs.** Its inputs are the harvest's stored flags for each member (code, family, member
position) and the cell minimum (`EXC.cells[*].minimum.quad` = 5). Its output is `EXC.cells[*].{dropped_units,kept_units}`
and `EXC.members_excluded`. The observed contention magnitudes and the anchor statistics behind each flag are in the
GAMMA harvest archive (`derived/flags.jsonl`). That archive is outside this seat's read scope, so they are not quoted
here.

**Codes and their registered meaning.** The texts are the catalog notes and registration §6.3–6.4.

- `contention.request_overlap` (PHYSICS_IN_SPAN): "an outside process (not `kernel_task`) exceeds 0.05 CPU-s/s in a 10 s
  interval that overlaps that span" (registration §6.4). The span is the request span, or the whole member span when
  the request span is missing.
- `member.admission_aborted` (MEMBER_VALIDITY): "Idle admission refused the member after its one immediate retry"
  (§6.3). Its companions are `member.span_unknown`, `member.target_phase_precheck_failed` and sometimes
  `member.strict_validation_failed`. Those follow because an aborted member has no placeable span and no valid target
  phase.
- `member.anchor_not_bounded` (MEMBER_VALIDITY): the member's clock anchor is not `bounded` under registration §0.14.
  `bounded` requires an effective bound ≤ 5 ms, ≥ 60 s of sampler record, ≥ 2 rollovers, rate within 50 ppm and first
  parse lag 0–0.25 s. Here it comes with `member.whole_window_member_failure`; the stored whole-window verdict lists
  this member under `environment_admission_missing` (`STEP.windows.gamma.member_reasons`).

**Removed quads.** The member suffix gives the side and the position within the quad: a1 = A1 (1.7B), b1 = B1 (8B),
b2 = B2 (8B), a2 = A2 (1.7B). The data are `EXC.cells[*].dropped_units` and `EXC.members_excluded`; the stage names are
`DISC.contrasts[label=removed unit].stage_ids`.

| Contrast | Quad | Stage | Triggering member(s) | Side | Codes that fired | Registered rule |
|---|---|---|---|---|---|---|
| decode | b01 | science-01 (decode quads 01–05) | b01-b1 | 8B (B1) | `contention.request_overlap` | §6.4 contention → §6.6 |
| decode | b05 | science-01 | b05-b1 | 8B (B1) | `contention.request_overlap` | §6.4 → §6.6 |
| decode | b06 | science-02 (decode quads 06–10) | b06-b2 | 8B (B2) | `member.anchor_not_bounded`, `member.target_phase_precheck_failed`, `member.whole_window_member_failure` | §6.3 validity → §6.6 |
| decode | b09 | science-02 | b09-b2 | 8B (B2) | `member.admission_aborted`, `member.span_unknown`, `member.strict_validation_failed`, `member.target_phase_precheck_failed` | §6.3 → §6.6 |
| prefill | b01 | science-03 (prefill quads 01–05) | b01-b1 and b01-a2 | 8B (B1) and 1.7B (A2) | both: `member.admission_aborted`, `member.span_unknown`, `member.target_phase_precheck_failed` | §6.3 → §6.6 |
| prefill | b04 | science-03 | b04-a1 | 1.7B (A1) | `contention.request_overlap` | §6.4 → §6.6 |
| prefill | b06 | science-04 (prefill quads 06–10) | b06-b2 | 8B (B2) | `contention.request_overlap` | §6.4 → §6.6 |
| prefill | b09 | science-04 | b09-b1; b09-a2 | 8B (B1); 1.7B (A2) | b1: `contention.request_overlap`; a2: `member.admission_aborted`, `member.span_unknown`, `member.target_phase_precheck_failed` | §6.4 and §6.3 → §6.6 |
| prefill | b10 | science-04 | b10-b1 | 8B (B1) | `contention.request_overlap` | §6.4 → §6.6 |

**Kept quads.** Decode keeps b02, b03, b04, b07, b08 and b10, which is 6 against a minimum of 5. Prefill keeps b02, b03,
b05, b07 and b08, which is 5, **exactly the minimum** (`EXC.cells[*].{kept_units,n_kept,minimum}`). One more prefill
loss would have removed the GAMMA window (`cell.below_minimum`, §6.6).

The same codes also removed four GAMMA reference or corpus members, which are not contrast members (`EXC.members_excluded`):

- `neg8-refcorpus-r05` and `-r16`, for contention;
- the references `neg8-window-end-r1` and `neg8-window-start-r2`, for contention.

The NEG-8 drift screen still passed on its survivors: 5 deciding references against 7 planned, with a clean corpus of
12 (`DISC.window_lines.gamma[neg8_screen, reference_counts, corpus_counts]`). Across GAMMA there were 10
`contention.request_overlap` flags and 4 `member.admission_aborted` flags. The four aborted members are the four of
107 planned members that were not collected (103 of 107; `DISC.block_lines[attempt_history]`).

### 2.2 Balance across sides and blocks

**At bundle level, balance is exact by construction.** Every removal takes a whole quad, so 18 bundles of each model
were removed (derived: 9 quads × 2 per side). The within-quad A/B/B/A cancellation is kept for every kept quad.

**The members that triggered removal are not balanced (derived count from `EXC.members_excluded`).**

- 8 of the 11 triggering contrast members are on the 8B side; 3 are on the 1.7B side.
- All 4 decode removals were triggered by an 8B member.
- Contention alone fired on 5 8B members and 1 1.7B member. Admission aborts were 2 and 2; the anchor failure was 1 on
  the 8B side.
- By position within the quad: B1 5, B2 3, A1 1, A2 2.

A plausible reading is exposure, but it is not established. An 8B request runs longer: its decode phase is about 3.3
times longer and its prefill phase about 4.3 times longer (derived: `RC.disclosures.scaled_allowance.contrasts[*].{T_b_s,T_a_s}`,
6.574 s / 1.990 s and 2.678 s / 0.620 s; a recompute field that is not compared). So a background process at a fixed
rate overlaps 8B requests more often. BETA, the 8B-only window, also had more contention flags (14) than ALPHA (4) or
GAMMA (10) (`DISC.window_lines.*[physics_counts]`).

**Across blocks and stages.** The removals are spread over all four collection stages: 2, 2, 2 and 3. Two patterns
stand out (derived observation, structure only):

- **The first quad listed in every stage was removed.** These are decode b01 and b06 and prefill b01 and b06, with four
  different causes: contention, anchor failure, admission abort and contention.
- **Quad number b09 was removed in both phases.**

BETA's decode quad b01 was also removed (`RC.reported_cells.df-ph-decode-qwen3-8b.removed_units`). If each stage runs
its quads in listed order (the order manifest; not re-checked here), the machine looks less settled right after a stage
starts. Because a removal takes both sides of a quad, this does not bias the within-quad contrast. It does mean the kept
quads under-represent the post-transition state.

**The exclusions are re-derived independently, but only from the stored flags.** The recompute re-runs the exclusion
function from the stored flags and the withheld roster and spans, and agrees for ALPHA, BETA and GAMMA
(`RC.exclusions_rederivation.*.differing_keys` empty; comparator family `exclusions_rederivation` 3/3 AGREE). It does
not re-detect contention, aborts or anchors from raw hazard data. `LEAN-COVERAGE-AUDIT.md` §4 says so explicitly.

### 2.3 Was the registered rule frozen before data?

Yes. These were checked against the repository on 2026-11-08.

- **The catalog.** Its last change is commit `1704059cc98334a9c402390ad041e1199e2c8936` (2026-10-08 00:07 PDT). It
  carries the catalog revision 12 and the allowlist sentence the seal gate required. The cell minimum of 5 came in at
  `059fafc55` (2026-10-07, seal-gate change C-1).
- **The first seal.** H_claim is `a64000884ef5bb4b76415835f02f39803f6eb620` and the seal commit is
  `ab7b21e576a2d74f0b25d9a26b463d6934588368` (2026-10-08 01:15 PDT). The seal record is
  `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md` §§2 and 4.
- **The second seal, which governs the analysed windows.** H_claim is `c27485347c9629b857df81665b5b1b8d10dcd36a` and the
  seal commit is `be6525e5a6511adf882282e404e163e14dbb738b` (2026-10-09 10:42 PDT); see SEAL_RECORD.md "Erratum 1". The
  catalog was unchanged at this seal. Between the two seals the registration's diff touches the NEG-8 corpus text and no
  member-exclusion rule of §6.3, §6.4 or §6.6.
- **The catalog bytes did not move.** This seat recomputed the catalog's SHA-256 at `1704059cc`, `a64000884`,
  `ab7b21e57`, `c27485347`, `be6525e5a`, GAMMA's harvest pin `b039c0257` and the analysis commit `ab1e0098d`. It is
  `5d77c725d4bf…` at every one, equal to `configs/analysis/b5/seal_pins.json` `sealed.catalog_sha256` and to
  `EXC.catalog_sha256`.
- **Data came later.** The first Block-5 attempt is `v5-b5-alpha-a1-20261008T2201Z` (planned start 2026-10-08T22:01Z),
  after the first seal. GAMMA's attempt started 2026-10-12T04:20Z.
- **The harvest program was changed, prospectively.** The program that emits the flags was re-pinned twice by
  prospective errata. Erratum 2 was admitted 2026-10-10T16:30Z, with pin `0699abbb0`. Erratum 3 was admitted
  2026-10-11T17:00Z, with pin `b039c0257`, committed 2026-10-11 10:19 PDT, before GAMMA armed (SEAL_RECORD.md Addenda 3
  and 4).
  - Each erratum says "No threshold, flag code, roster, blinding rule or window input changes."
  - Each was admitted by a cold Fable judge with an Opus refuter.
  - Each was written "by a seat that has read no claim-window energy".
  - GAMMA's exclusion record names harvest head `b039c0257` with a clean checkout (`EXC.harvest_checkout`).

---

## 3. What L2 permits, and what it does not

The sources are the ladder (`docs/contracts/claims_ladder.md`), registration §0.19 and §1, and the fixed sentences in
`DISC.fixed_sentences`.

**The registered condition for L2 was met.** Registration §1 sets L2 for GAMMA "if and only if the claim gate returns
`claim_ready_for_l2_l3` true" (analysis plan §7.2). It does, for both contrasts. That requires all of these:

- the direction is supported: |d̄| > floor, neither interval contains 0, and Holm rejects;
- the contrast is primary and confirmatory, from a frozen manifest, with no top-up;
- leave-one-quad-out is not verdict-influential;
- the direction is the registered one.

The ladder's L2 evidence is also present:

- n ≥ 5 per condition (5 or 6 quads, which is 10 or 12 bundles per model);
- strict-valid bundles;
- order recorded and interleaved (A/B/B/A within one window);
- intervals reported;
- the effect above the detection floor;
- one boundary label;
- runtime-observed token counts, stop reason and output-policy label for the per-token figures.

**L2 permits this sentence shape.** "Within the `M3 Max / MLX / powermetrics SoC rails` boundary, on this stack, under
this workload and output policy, condition B (Qwen3-8B) used more phase energy than condition A (Qwen3-1.7B): +146.6 J
per request in decode (decision interval 141.4–151.9 J) and +101.8 J in a 2048-token prefill (95.8–107.8 J), both above
the registered detection floors after Holm correction." The registered ratio and per-token difference may be printed
beside it, labelled "registered descriptive estimates", with "recorded timing bounds are not propagated" stated for the
ratio.

**L2 does not permit any of the following.**

- **L3 or L4.** No fitted model, no scaling law, no "energy scales with parameter count", no per-parameter energy, and no
  holdout prediction. Registration §1 says L3 and L4 are "out of reach". The ladder's downgrade example applies: two
  models that differ in size are hypothesis-generating, not an active-parameter scaling result.
- **Generalization** beyond this machine, OS build, runtime, quantization, sampler and policy. That includes other Macs,
  other chips, CUDA, other runtimes, other prompts (registered sentence `fixed_prompt`: "no prompt-population generality
  is claimed") and other prompt lengths (registration §1: nothing "about prompt lengths other than 2048").
- **Any whole-machine, wall or "device energy" claim.** The claim boundary is the SoC package rails. The whole-machine
  meter is a descriptive cross-check and "never a claim" (registration §1; analysis plan §8.2).
- **Cross-window claims.** No ALPHA-versus-BETA comparison of the reported cells (L1; `separate_windows`).
- **Between-day or between-session reproducibility.** Registered sentence `single_window`: "the interval covers
  variation within that window, not between days or windows". Registration §1 makes block 6 the replication test, and
  "replicated" needs the same outcome word and the same sign in every counting block-6 session (`RUN_STATE.md` item 37).
- **A phase-attribution accuracy claim.** Registered sentence `d177`: "phase attribution is reported without a measured
  instrument phase-accounting check."
- **The D-165 dominance sentence or the "attribution-limited" contingent subtitle.** These are not licensed:
  `DISC.block_lines[dominance_branch]` reads "D-165 branch B; dominance sentence licensed: no". Three of the four
  comparative R_cm values are below 2.0 (1.7046, 1.9997 and 1.7616; only 8B prefill passes, at 2.7704). The floor
  *label* `attribution_limited` in §1 is a different thing: it is the D-078 floor class (§4.2). It must not be written
  as the D-165 subtitle.
- **"Efficiency" or "cost" wording that implies causality beyond the measured quantity.** The quantity is gross: it
  "includes the machine's baseline power over the phase, and the 8B phase lasts longer, so part of the difference is
  baseline power times the extra duration" (registered sentence `gross_energy`).
- **Reading the p-values as a measure of effect size or of generality.** They assume independent quads in a fixed,
  unrandomized order (registered sentence `order`).
- **Forbidden ladder words**: universal, architecture-wide, cross-boundary winner, extrapolated crossover, proves, law.

---

## 4. Disclosures

### 4.1 The deviation log, one line each

Source: `docs/analysis/b5/DEVIATION-LOG.md`. Each entry is signed with "The release event has not happened. The lead
has seen no Block 5 energy or outcome value."

- **DLE-0** (adopted 2026-11-06; decided 2026-10-14): plan step 12, the results cold gate (judge plus refuter
  re-deriving every printed number), is replaced by the independent recompute agreeing with L9 within bars fixed
  blind. Estimands are unchanged. Coverage gaps are listed in LEAN-COVERAGE-AUDIT §2.
- **DLE-1** (2026-11-06): the release is (a) digest re-verification of the dry run, (b) the independent recompute and
  (c) the comparator under pinned bars, instead of re-running steps 1–11. Seven registered disclosure families are not
  independently recomputed; this is accepted for block 5 only.
- **DLE-2** (2026-11-06): from block 6 on, the lean recompute is the production path and heavy L9 becomes an
  off-critical-path audit. It does not change any block-5 number.
- **DLE-3** (2026-11-07, analysis r3):
  - D1 fixes a wrong key (`battery_term_available`) in the printed `machine_member` lines;
  - D5b relabels a floor-binding refusal as `floor_artifact_invalid`;
  - the D-188 speed engineering is result-equal;
  - D2–D4 and D6 fix the recompute and the comparator, not L9.
- **DLE-4** (2026-11-07, analysis r4): fixes L9's floor binder. It counted the campaign log's whole-window evaluation row
  as a second occurrence of every member, so it refused all four GAMMA floor cells. Without the fix both contrasts would
  have been `not_estimable`. The cause was found by a structure-only probe; the recompute shares neither the parse nor
  the defect.
- **DLE-5** (2026-11-07, release tooling): the comparator now maps and compares the attribution-floor metadata. These
  are 84 leaves that L9 printed for the first time once DLE-4 let the floors resolve. A limit decision inside its bar
  holds the release automatically. L9 and recompute outputs are unchanged.

### 4.2 The attribution-limited floors (DLE-5; D-078)

Every GAMMA floor cell is `attribution_limited`, with floor source `E_clock_anchor_shift_bound_j`
(`FILL.gamma.contrasts[*].floor.resolutions[*]`). This means the published claim floor is set by phase-edge timing
(clock-anchor) uncertainty, not by run-to-run repeatability.

- The repeatability-only point floors are printed as diagnostics with `published_claim_floor: false`. They are
  0.59–1.01 J (guarded), against published floors of 5.8–10.2 J (`.claim_evaluation.floor_limit.point_floor_diagnostics`).
- **How a floor is composed** (`DISC.floors[label=floor_composition]`): the guarded operative floor, plus the floor
  window's NEG-8 drift allowance, gives the minted floor. Two examples:
  - BETA decode absolute: 9.01530 + 1.16277 = 10.17807 J;
  - BETA prefill absolute: 7.66749 + 1.16277 = 8.83026 J.
- **The armwise maximum** is `cross_stack_armwise_max.v1`. The 8B (BETA) floor sets the active floor in both contrasts
  (`RC.contrasts[*].floor.attained_by` = BETA).
- **The comparator re-derived the D-078 limit rule** from the recompute's own terms and compared every printed
  diagnostic. There are 0 `within_bar_undetermined` rows (`VER.stages.comparator.limit_undetermined.count` = 0). So the
  fallback label "attribution limit not independently determined" is not needed for any cell.
- **The single-count discipline.** `attribution_floor_plus_claim_side_bound.v2` is a non-gating planning diagnostic. The
  implemented rule is |estimate| > F with both intervals excluding 0. The clock-anchor bound enters the claim once,
  through D, and the floor is a calibration false-effect bound (`.claim_evaluation.floor_limit.single_count_discipline`).

### 4.3 How the recompute and the comparator confirmed the results, and what they did not cover

**What was confirmed** (`VER`; `CMP`; `RC`):

- **(a) Digests verified.** 390 outputs and 78,389 input-census rows were re-hashed for all three windows.
- **(b) The independent recompute.** It is `scripts/independent_recompute_b5.py`, program SHA-256 `d49103e8…`. It uses
  the standard library only and imports nothing from `joulewise`. It read the raw power records of 249 runs, with 0 not
  compared and `comparison_stopped` false. It exited 0 with 6 workers.
- **(c) The comparator** (bar set `b5_release_recompute_coded_7e322b76`, bars SHA-256 `2f65bba2…`, fixed blind,
  `RUN_STATE.md` item 83 ruling 1):
  - every family is AGREE with 0 failing rows;
  - 0 unmapped step-11 leaves, 0 non-finite values, 0 absent sources;
  - 0 undetermined holds and 0 structure flags.
- **Row counts.** The families most relevant to the headline: `contrast_j` 87, `contrast_p` 30, `floor_gate_j` 72,
  `floor_j` 201, `kept_units` 26, `outcome_word` 579, `holm_order` 1, `per_token_j` 10, `descriptive_ratio` 6,
  `reported_cell_j` 144, `run_phase_energy_j` 585, `exclusions_rederivation` 3. Every L9 number in the §1 table has a
  compared row: d̄, s_d, se, t*, both intervals, D and its terms, the floors and arm gates, raw and adjusted p, Holm
  rejection, kept quads, outcome, direction, ceiling and every LOO row.
- **Largest difference found** (derived: the maximum of |difference| per family in `CMP.comparisons`):
  - `contrast_j` 5.7e-14 J;
  - `floor_gate_j` 9.8e-12 J;
  - `run_phase_energy_j` 2.3e-13 J;
  - `per_token_j` 5.6e-17 J;
  - `contrast_p` 1.5e-22.
  The joule bars are 1e-6 relative.

**What it does not show.**

- **"Agree across 24 families" is 23 that compared something.** The `window_edge_s` family has 0 rows (pass 0,
  fail 0).
- **Seven registered disclosure families are not independently recomputed** (DLE-1; LEAN-COVERAGE-AUDIT §2): monitor
  cost; arm and host hazards; battery; battery temperature; reference, corpus and NEG-8 history; attempt history and G10;
  selection. For these, `agree` shows integrity (stage (a)), not correctness. There are also 403 numeric leaves under
  named exemptions (`VER.stages.comparator.step11.uncovered_numeric`). Under item 83 ruling 3, any such leaf the paper
  prints must be hand-checked first.
- **Collection-time judgments are taken from storage, not re-derived** (LEAN-COVERAGE-AUDIT §4): the exclusion flags,
  the clock anchors (m, s), the calibration fits (b_pre, b_post), the NEG-8 clean-corpus choice and the screen
  decision. The heavy L9 dry run re-derived them under strict step 1; the recompute did not.
- **The p-value bar cannot separate p-values this small.** It is 1e-6 absolute, so it could not distinguish p-values of
  1e-11 to 1e-15. The actual agreement (1.5e-22) is far tighter, and t* and se are compared separately.

### 4.4 Other registered disclosures a reader needs

- **Order.** "Every quad ran 1.7B, 8B, 8B, 1.7B in that fixed order; the order was not randomized, and the p-value
  assumes the quad differences are independent." (`order`)
- **Conditionality.** "These numbers are conditional on a window that passed the registered physical-hazard checks at
  arm and kept at least 5 of 10 units per stratum after the registered exclusions." (`conditionality`)
- **p42.** The 42-token prefill is "shorter than one power record and could not be resolved; as registered, no p42 value
  is reported." (`p42`)
- **Battery.** There were no battery-assisted quads: the battery-assist lines equal the primary, assist quads 0
  (`DISC.contrasts[label=battery_assist_contrast]`). At arm the battery read amperage 0, PASS
  (`DISC.window_lines.gamma[arm_hazards]`).
- **Stored whole-window verdicts.** The in-run verdict was `failed` in all three analysed windows (`STEP.windows.*.stored_verdict`).
  As registered, "the stored verdict's status and NEG-8 bracket decided nothing; its membership, basis, provenance and
  physics checks were applied." Each stored condition is answered by a registered mechanism, and both tripwires are
  clear: `excluded_reference_in_screen` and `kept_member_outside_verdict_membership`.
- **Attempt history** (`DISC.block_lines`):
  - ALPHA and GAMMA are each the pack's first attempt under the second seal.
  - BETA is attempt 6. Attempts 1–5 were not claim-usable, for NEG8, CALIBRATION, ROSTER and `cell.below_minimum`
    causes; they are kept and disclosed and their energies were never analysed.
  - The three first-seal ALPHA attempts were superseded by Erratum 1 and never analysed.
- **Monitor cost** (not recomputed; DLE-1 family 1). GAMMA's hazard monitor used 209.46 CPU-s and the meter reader
  94.02 CPU-s, with 568 probes inside target phases. This load was not subtracted (`DISC.window_lines.gamma[monitor_cost, monitor_sentence]`).
- **The whole-machine (DC-in) channel was analysed, as registered and as Ed's KM003C rule requires.** It is
  descriptive, never a claim. The boundary is "whole-machine DC input plus the battery term, measured at the USB-C input;
  the adapter's AC-to-DC loss is not included."
  - The rails' share ρ of idle-subtracted request energy in GAMMA (`DISC.window_lines.gamma[machine_summary]`): 1.7B
    median 0.3606 (range 0.3532–0.3828), 8B median 0.3649 (0.3268–0.3842), the Qwen2.5 reference 0.3912. All are
    "consistent"; none is implausible (0 of 103).
  - No window is clean, so no central band is set.
  - Per-phase gross whole-machine energy (registered blind in `RUN_STATE.md` item 37; computed by the recompute only, not
    compared, ALPHA and BETA only, not GAMMA, from `RC.disclosures.whole_machine.windows.*.cells`):
    - 1.7B decode 149.65 J (h 0.17; edge-shift up to 9.07 J; rail share 0.34);
    - 8B decode 589.25 J (h 0.57; edge-shift up to 12.17 J; share 0.34);
    - 1.7B prefill 57.85 J (share 0.45);
    - 8B prefill 285.62 J (share 0.45).
  - These are L1, separate-window values and not a comparison. They need the item-83 hand check before they are printed.

### 4.5 Registered sensitivity lines computed only by the recompute (not compared; not for the paper without a hand check)

| Line (registration) | Decode | Prefill | Source |
|---|---|---|---|
| Load-correlated exclusions not applied (§8.1; the seal gate's narrowed form) | **L9: not computable** (`member_code_on_kept_unit`); recompute: 146.800 J, metrology interval [146.439, 147.161], n = 8 (2 quads restored) | **L9: not computable**; recompute: 101.657 J, [101.224, 102.089], n = 8 (3 restored) | `DISC.contrasts[label=load_correlated_contrast]`; `RC.disclosures.load_sensitivity` (exempt from comparison, LEAN-COVERAGE-AUDIT §3) |
| Drift allowance scaled by max(1, E/E_ref, T/T_ref) (`RUN_STATE.md` item 37, blind; "the registered result is unchanged") | D 9.345 J; decision [137.095, 156.164] J; floor gate 15.228 J; `direction_supported` | D 8.045 J; decision [93.395, 110.224] J; floor gate 11.685 J; `direction_supported` | `RC.disclosures.scaled_allowance.contrasts` |

---

## 5. Joules per token

The artifacts carry the token counts. Every included bundle has `output_tokens` 512 with `token_count_source`
`runtime_observed` (`CV.bundle_audit[*].token_provenance`). The fill's `j_per_token` field is null by design: the
contrast metric is per request. The per-token values are the registered descriptive estimates of analysis plan §7.3.

- **Decode.** 0.286386 J per output token for 8B minus 1.7B; decision interval [0.276086, 0.296685]. The denominator is
  all 512 runtime-observed output tokens. The decode phase covers the other 511 generation steps, because prefill
  produces the first token (registration §0.5, D-179).
- **Prefill p2048.** 0.049712 J per prompt token; decision interval [0.046781, 0.052642]; the denominator is 2048.
- **Per-model L1 cells** (separate windows; not a comparison): 1.7B 0.100013 and 8B 0.387425 J per output token
  (decode); 1.7B 0.0128193 and 8B 0.0626383 J per prompt token (prefill p2048) (`PROJ-A|B.cells[*].per_token.j_per_token`).

---

## 6. Paper-ready text (capstone talk and mid-December paper)

**Before any of this is printed, four gates apply. The repository does not show any of them as met.**

1. **The placement ruling.** Registration §14 Q4 and analysis plan §9 say every Block-5 row is printable "only through
   the placement ruling of registration §14 Q4". D-174's fallback places no `_v5` result. No adoption ruling was found
   in `RUN_STATE.md` or `docs/decision_log.md`.
2. **The paper plan excludes Block 5.** `docs/capstone/PAPER-PLAN-v2.md` currently excludes Block 5 from the capstone
   paper ("It is Paper 1 material, and sealed"). The "sealed" premise is now outdated, but changing the plan is the
   lead's call.
3. **The renderer obligation.** The seal record's declared deviation of 2026-10-20 requires any Block-5 results
   renderer to print every contrast row with its issued status, to select none, and to pass "the Results cold gate"
   before its numbers are used. This file prints both contrasts and selects nothing. Whether a hand-written page counts
   as a "renderer", and whether DLE-0 also stands in for that gate, should be ruled.
4. **The block-6 reporting rule.** `RUN_STATE.md` item 37 (blind, 2026-10-14) fixed this reporting rule: "the paper
   prints block 5 and block 6 side by side". Printing Block 5 alone should say that the replication block is registered
   and its results are sealed.

**Paragraph (conservative wording).**

> In a registered comparison on one Apple M3 Max laptop (macOS build 25G83; MLX; 4-bit Qwen3-1.7B and Qwen3-8B; greedy
> decoding with exactly 512 output tokens), the two models were interleaved within a single measurement session in
> fixed 1.7B–8B–8B–1.7B quads. Energy is the gross energy of the SoC CPU, GPU and ANE package rails reported by
> powermetrics, assigned to the prefill and decode phases of each request. It is neither wall-socket nor whole-machine
> energy. For one fixed 42-token prompt, the 8B model's decode phase used 146.6 J more per request than the 1.7B
> model's: decision interval 141.4 to 151.9 J, which adds the registered timing bounds to the 95% interval of 146.4 to
> 146.8 J, over 6 of 10 planned quads. For one fixed 2048-token prompt, its prefill phase used 101.8 J more (95.8 to
> 107.8 J; 5 of 10 quads). Both differences exceed the registered detection floors of 10.2 J and 8.8 J, survive Holm
> correction across the two registered contrasts (adjusted p ≤ 2 × 10⁻¹¹), and keep their verdict when any single quad
> is left out. They therefore meet our preregistered criteria for a comparative (L2) result. As registered descriptive
> estimates, the differences are 0.286 J per output token and 0.050 J per prompt token. The registered exclusion rules
> removed 9 of the 20 planned quads, most of them for background CPU activity overlapping a request, so the prefill
> comparison rests on the registered minimum of five quads. The intervals describe variation within one session; a
> replication block is registered and its results are not yet released. These are measurements of one stack at one
> measurement boundary, not a scaling law, a cross-device ranking, or a statement about whole-machine energy. The rails
> carried roughly a third of the machine's idle-subtracted request energy in the same session.

**Table (paper form; values rounded from §1, full precision and keys in §1).**

| Phase (fixed prompt) | Quads kept / planned | 8B − 1.7B phase energy (J) | 95% interval, within session (J) | Decision interval incl. timing bounds (J) | Detection floor (J) | Holm-adjusted p | Outcome (ceiling) | Per token, descriptive |
|---|---|---|---|---|---|---|---|---|
| Decode (42-token prompt, 512 output tokens) | 6 / 10 | +146.6 | 146.4 – 146.8 | 141.4 – 151.9 | 10.2 | 1.2 × 10⁻¹⁵ | direction supported (L2) | 0.286 J per output token |
| Prefill (2048-token prompt) | 5 / 10 | +101.8 | 101.4 – 102.2 | 95.8 – 107.8 | 8.8 | 1.7 × 10⁻¹¹ | direction supported (L2) | 0.050 J per prompt token |

**Caption.**

> Boundary: M3 Max / MLX / powermetrics SoC rails (gross phase energy). One session; quads in fixed, unrandomized
> order. Exclusions follow the frozen registered rules. Phase attribution was not checked against an instrument
> measurement. The ratio of phase energies, 8B to 1.7B, is 3.86 (decode) and 4.88 (prefill); it is descriptive and
> recorded timing bounds are not propagated into it.

**Talk slide, one line.** "Registered, blinded, independently recomputed: in one session on one Mac, the 8B model's
decode phase cost 146.6 J more per request than the 1.7B model's (141.4 to 151.9 J), and 2048-token prefill 101.8 J more
(95.8 to 107.8 J); both are above the instrument's detection floor. Rails only, one prompt, one session."

---

## 7. What a skeptical reviewer will raise

**Top three.**

1. **One session, so the intervals understate real-world uncertainty.**
   - The 95% intervals are ±0.19 J and ±0.37 J on effects of 147 J and 102 J (derived half-widths), and the p-values
     are 10⁻¹¹ to 10⁻¹⁵. These reflect quad-to-quad repeatability inside one window under a fixed, unrandomized
     order. They do not reflect between-day variation.
   - The registered cross-window check already shows the gap. GAMMA's 8B decode estimate and BETA's differ by 0.42 J,
     "more than their within-window intervals cover".
   - No replication result is released yet.
   - The decision interval, ±5.3 J and ±6.0 J, is the honest width. It is 94–96% deterministic timing bound (derived),
     not statistics.
   - The defensible claim is the direction and approximate magnitude, at L2, for this stack.
2. **Heavy and uneven data loss.**
   - 9 of 20 quads (45%) were removed: 11 of 80 contrast members, 13.75% (derived). Registration §6.6 planned on a
     member-loss rate of about 1/37 (2.7%), the only measured cause.
   - The prefill contrast sits exactly at the minimum of 5.
   - 8 of 11 triggering members were on the 8B side.
   - The first listed quad of every stage was lost.
   - Contention (an unidentified outside process above 0.05 CPU-s/s) was the leading cause, and it is pervasive across
     the block: 4, 14 and 10 flags in ALPHA, BETA and GAMMA.
   - The rules were frozen before data (§2.3), and whole-quad removal keeps the comparison symmetric. But the registered
     sensitivity line that restores the contention-removed quads was **not computable in L9**
     (`member_code_on_kept_unit`). The recompute's version (146.80 J and 101.66 J at n = 8 each, close to the primary)
     is uncompared and is not a registered L9 number.
   - The exclusion re-derivation re-applies the rule to stored flags; nobody independently re-detected the contention.
   - Reviewers will ask what the contending process was. The hazard records that would say are outside this read.
3. **What is being measured.**
   - The claim boundary is the SoC package rails. In the same session they carried only about 36% of the
     idle-subtracted whole-machine request energy, and about 34% (decode) and 45% (prefill) of gross whole-machine phase
     energy (recompute, descriptive).
   - The project's own known-bytes test found that the rails miss most of a memory-traffic contrast
     (`docs/capstone/PAPER-PLAN-v2.md`, about 76%).
   - Phase energy is gross. The 8B phases last about 3.3 times (decode) and 4.3 times (prefill) longer, so part of the
     difference is baseline power times duration.
   - Phase attribution has no instrument check (D-177).
   - The result itself, a larger model using more energy, is expected. Its value is that the registered, blinded,
     independently recomputed pipeline resolved it with stated floors. It should be framed as an instrument result, not
     as a discovery.

**Also likely to be raised.**

- **Process churn.**
  - BETA needed six attempts and ALPHA restarted after the first seal was superseded.
  - Three errata were admitted mid-block. They were prospective and blind to energies, but motivated by structural
    failures of earlier attempts.
  - The analysis went through four versions (r1–r4) and six deviation entries, DLE-0 to DLE-5, all signed blind.
  - The DLE-4 defect would have made both contrasts `not_estimable`. A reviewer may ask what else is latent. The answer
    is the independent recompute's agreement on the core arithmetic, with the coverage limits stated in §4.3.
- **The stored whole-window verdict failed in all three analysed windows.** Claim-usability rests on the harvest's
  registered re-screens and member exclusions, not on the in-run verdict.
- **The dominance diagnostic sits close to its threshold.** R_cm for 1.7B prefill is 1.9997, just under the threshold
  of 2. Branch B was selected and the subtitle is not licensed. Any "timing uncertainty dominates" sentence must not be
  written.
- **The prefill leave-one-out runs at n = 4,** below the cell minimum of 5. The recompute flags this as
  `loo_kept_n_equals_minimum` (STRUCTURE, non-stopping).
- **One fixed prompt per phase, and one prefill length.** The prefill length of 2048 was chosen in block 3 as the
  shortest length at which small-model prefill overlapped at least 5 power records.
- **A labelling inconsistency (minor; trace before the paper).** `CV.bundle_audit` lists `strict_status: valid` for the
  members the harvest flagged `member.strict_validation_failed` or `member.admission_aborted` (decode b09-b2, prefill
  b01-a2). These are probably different checks, since the engine does not re-validate removed units. The recompute's
  `kept_member_unusable` flags name only members of removed units, and none stopped the comparison.

---

## 8. Checks this file still needs before paper use

- The lead or Ed rules on §14 Q4 placement and on the PAPER-PLAN-v2 exclusion (§6, gates 1–2).
- A cold read of this file against the artifacts (the item-83 ruling-3 hand check for any uncovered leaf the paper
  prints: §4.4 and §4.5 values, the attempt history, the monitor cost).
- A structure-only trace of the contention source and of the stage-opening losses, from the GAMMA harvest's
  `derived/flags.jsonl`. This matters for block 6's interpretation, not for these verdicts.
