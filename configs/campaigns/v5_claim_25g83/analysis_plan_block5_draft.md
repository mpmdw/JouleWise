# Analysis plan V5-CLAIM-25G83-B5: what is computed from the claim windows, and how

Status: **DRAFT UNSEALED, revision 2, 2026-10-05.** Companion to
`configs/campaigns/v5_claim_25g83/registration_block5_draft.md` (the **registration**); the two are sealed together
and neither binds alone. Terms are those built in registration §0; terms that first appear here are built where they
first appear. Every rule is fixed before any claim byte exists. Most estimators below are already frozen in
committed bytes (the D-179 contract, the floor packs' `extraction_spec.json`, GAMMA's `analysis_manifest_v3.json`);
this plan ties those bytes, states the arithmetic so that it can be recomputed by hand, and fixes everything they
leave open: inputs, order of operations, exclusions, disclosures and what is printed from which artifact. Numbers
in worked examples are **synthetic** and labelled so; they are not measurements. The packs named here are the
regenerated packs of registration §2.0; their estimator registrations are re-issued by that regeneration and
re-tied at seal (`FILL[V5-PACK-REGEN-RECORD]`). Section 14 records the disposition of the three draft critiques.

**Terms first used here.**

- **Prospective manifest.** GAMMA's `analysis_manifest_v3.json`: the contrasts, their estimator, multiplicity
  family and floor rules, frozen before any collection. Its **frozen-semantics hash** is the SHA-256 of its
  analysis-relevant fields, so any later change to them is detectable.
- **Finalization.** The step that ties the identities of the collected bundles, the whole-window verdict, the
  bracket binding, the ledger, the aggregate floor and the dominance replay sidecar to the prospective manifest
  without reading any effect estimate; its output is the **finalized manifest**.
- **Claim gate.** The program (`python -m joulewise analyze-claims`) that, from the finalized manifest, computes
  each contrast and decides its outcome and claim ceiling.
- **Sidecar.** A separately hash-tied file emitted beside the mint: here the dominance replay inputs.
- **Pinset.** The list of content hashes the mint may consume. **v2 input manifest.** The mint's list of which
  extraction-report cells feed which floor role (decode, prefill).
- **Close-out.** The artifact that records every dominance ratio and decides branch A or B (§6).
- **Placement.** A registered site in the paper where an issued value may be rendered. **D-173 custody** is the only
  route by which a paper supplier may read evidence: the supplier names a **role** (which evidence it needs) and a
  runs root, and a **supply map** returns every path and digest, so no caller-chosen path enters a number.
- **Issuer.** The production program that writes the D-179 reported-energy projection (§4).
- **Placement states.** `MEASURED`: copied or conservatively rounded from an issued field. `DERIVE`: computed by a
  formula named in this plan. `PROPOSED_STOP_FILL`: a proposed site whose fill is blocked until adopted.
  `RETIRED_FALLBACK`: a site retired by the D-174 fallback, printable only after a new ruling.
- **Blind dry run.** Steps 1–11 of §3 run on the real bytes before the release event, with every output kept in
  restricted custody and only structure serialized (§3.2).

## 1. When the analysis runs, and on what

1. The analysis runs once, after the measurement block closes (GAMMA PASS, registration §7), after the blind dry run
   has passed (§3.2), and after the release event (registration §9.4), at a commit whose analysis programs are
   pinned in the seal record (§11).
2. It reads exactly one attempt per pack: the attempt whose harvest verdict is PASS, from the measurement block that
   completed under the governing registration. A pack is never armed again after its PASS (registration §3.1), so
   there is exactly one such attempt.
3. It reads evidence only through the authenticated routes named in §3 (for paper suppliers, D-173's
   `open_paper_input(role, runs_root)`); no caller-supplied path, digest or value enters a number.
4. Everything it emits is retained in analysis custody `FILL[B5-ANALYSIS-CUSTODY-ROOT]` and handed to the results
   cold gate (registration §10.3) before any paper sentence is filled.

## 2. Inclusion and exclusion

### 2.1 Attempts and superseded windows

Non-PASS attempts (NULL, RECOVER, REFUSED) are never inputs to any number. They are listed with their cause codes and
classes in the attempt history (§8). PASS windows of a measurement block that was superseded under registration §7.4
are retained and disclosed structurally (verdicts, causes, counts); their energies are never analysed, in this plan
or as a secondary analysis.

### 2.2 Members

No member is excluded after collection. A PASS window has every member valid in the sense of registration §6, which
includes the target-phase precheck, the cooldown, the cooldown evidence and `idle_window_suspect`. Consequences:

- **Target phases (decode; prefill-p2048).** On a PASS window no member can produce the floor extractor's same-slot
  exclusion (cooldown cap hit) or a member-level claim-gate code such as `paired_block_incomplete`,
  `window_evidence_precheck_missing`, `campaign_cooldown_evidence_missing` or `idle_window_suspect`. If any is
  produced, or if a reported cell refuses with `missing_or_invalid_member: refuse_reported_mean`, it is a defect
  (the registration's validity and the code disagree): the analysis stops and the step goes to R3. No 49-member mean
  and no top-up are ever computed (D-179 ruling 1).
- **p42.** The p42 phase is expected to overlap fewer than 3 records and fail its precheck on every member
  (registration §0.5). Its outcomes are recorded and block nothing: the p42 reported cells refuse with their D-179
  codes; the p42 floor cells are non-extractable (§3 step 4). The expectation is verified before seal on `s1`'s
  structural precheck counts (in-window record counts and reason codes of the four `s1` members' p42 phases),
  `FILL[P42-S1-STRUCTURAL-CHECK]`.

The environmental diagnostic (registration §8) never excludes a member; it is disclosed (§8).

### 2.3 END STATE after one or both floor windows passed

Fixed now: the passed floor windows are analysed for their L1 outputs only: the reported cells (§4) and the floor
cells of the extraction (§3 step 4), with the separate-window and END STATE disclosures of §8. Contrasts (§7),
dominance ratios (§6) and the aggregate mint need all three windows and are never computed from a partial measurement
block. The one exception: if a cold gate rules, before any release, that the cause of the END STATE invalidates the
passed windows, they are not analysed. The END STATE design record cannot choose otherwise.

## 3. Order of operations

### 3.1 The steps

Each step runs on the bytes of the step before it; each output is content-addressed (SHA-256) and the next step
authenticates it. Full command lines are those of `docs/process/v5-artifact-flow.md` at the pinned commit (table
rows "Floor extraction", "Mint", "Finalization", "Claim gate" and "Results fills"; lines 19–24 at `c88565c4`).

| # | Step | Program | Output |
|---|---|---|---|
| 1 | Strict validation of every bundle of the three PASS windows | `python -m joulewise validate-bundle --strict <bundle>` | exit 0 per bundle |
| 2 | Re-reduction into restricted custody (never inside a bundle) | `python -m joulewise reduce <bundle> --output <custody>/<bundle_id>.rereduced.json` | summary schema 0.1 per bundle |
| 3 | L10-B rehearsal: floor extraction and mint on a scratch copy (already run between BETA and GAMMA, registration §3.3) | `scripts/extract_detection_floors.py`, `scripts/mint_floor_artifact_generalized.py` | `L10_B_FLOOR_PRODUCER` record |
| 4 | Floor extraction, ALPHA and BETA separately, each with its pack's `extraction_spec.json` | `scripts/extract_detection_floors.py … --hash-bundles` (artifact-flow "Floor extraction") | `joulewise.detection_floor_extraction.v1` ×2 |
| 5 | Production mint of the aggregate floor and its dominance replay sidecar | `scripts/mint_floor_artifact_generalized.py` (artifact-flow "Mint") with `FILL[V5-FINAL-PINSET]` and `FILL[V5-V2-INPUT-MANIFEST]`; the v2 input manifest feeds only the decode and prefill-p2048 cells (the mint requires exactly the roles decode and prefill, `mint_floor_artifact_generalized.py:3749`) | `joulewise.detection_floor_artifact.v2`; `joulewise.d165_dominance_replay.v1` |
| 6 | Dominance close-out | adapter `FILL[MINT-TO-CLOSEOUT-ADAPTER]`, then `scripts/build_d165_dominance_closeout.py` | `joulewise.d165_dominance_closeout.v1` |
| 7 | L10-C rehearsal of steps 8, 9 and 11 on a scratch copy | `docs/process/v5-l10-rehearsal-phase.md` §L10-C | `L10_C_FULL_EDGE` record |
| 8 | Finalization of GAMMA's prospective manifest with its attachments (whole-window verdict, bracket binding, ledger, aggregate floor, dominance replay sidecar) | `scripts/finalize_analysis_manifest.py` (artifact-flow "Finalization") | `am-3283e9d37ffe36895c77b6168e2688793061b5b8edc48690211fb72b8811e128.finalized.json` (manifest id re-tied after the regeneration) |
| 9 | Claim gate | `python -m joulewise analyze-claims` (artifact-flow "Claim gate"), with one `--evidence-root` per floor pack | `joulewise.claim_verdicts.v1` |
| 10 | Reported-energy projection | production issuance of `joulewise.paper_reported_energy_projection.v1` through D-173 custody, `FILL[REPORTED-ENERGY-ISSUER]`; it projects **each cell independently**, so a refusing cell (p42) leaves the others issued | one projection record per cell |
| 11 | Descriptive estimates, disclosures and results fills for adopted placements | §7.3 and §8 by `FILL[DISCLOSURE-PRODUCER]`; adapter `FILL[CLAIM-VERDICT-TO-FILL-ADAPTER]`, then `scripts/render_results_fills.py` and `--validate-rendered` | issued values; validated Markdown |
| 12 | Results cold gate: re-derive every printed number from the artifacts of steps 4–11 | judge + refuter | gate record |

**Refusals.** A refusal at any step stops the steps after it, with one registered exception: if step 4 exits 1 and
its refused cells are only the p42 floor cells (`d117-df-ph-prefill-p42-<model>-absolute` and
`d117-df-cmp-abba-ph-prefill-p42-<model>`) and no member was omitted from the spec, the report it wrote is the
input to step 5 and the exit is recorded as the registered p42 outcome. A tooling refusal goes to R3 and the step
re-runs on identical bytes; a refusal that is a registered scientific outcome (for example a not-resolvable contrast)
is the result and is printed as such.

### 3.2 Blind dry run, and repairs after the release

The issuer, pinset, input manifest, adapters, disclosure producer and environmental-diagnostic producer do not exist
yet (§11). A repair written after the energies are visible would be a choice made with the outcome in view.
Therefore:

1. **Before the release event**, steps 1–11 run end to end on the real bytes, outputs in restricted custody. Only
   structure is serialized: each step's exit status, schema validity, output digest, and its refusal codes, with any
   code that encodes a numeric comparison of a science quantity released only as "outcome-class refusal at step N"
   (registration §9.2). Every tooling refusal is cured by R3, blind, and the dry run repeats until it completes with
   no tooling refusal (`FILL[B5-BLIND-DRY-RUN-RECORD]`).
2. **After the release**, the analysis re-runs steps 1–11 from identical bytes at the pinned commit; every output
   digest must equal the dry run's. A mismatch stops the analysis and goes to R3 as a determinism defect.
3. **A repair needed after the release** is allowed only if it is written and reviewed by seats that have read no
   released number, adds a synthetic fixture reproducing the failure, and leaves every other registered synthetic
   fixture's output byte-identical. Any other change goes to a cold gate before it runs, and its outputs are
   labelled as produced after unblinding.

## 4. Estimator 1: reported phase energy per model and phase (D-179)

**What it is.** For each model and each of decode, prefill-p42 and prefill-p2048, one gross phase energy averaged
over the cell's 50 ordered members, with an interval that respects the 20 independence units. Normative home:
`docs/contracts/paper_reported_energy.md`; registration digests in each floor pack's `extraction_spec.json`
(`reported_energy_registration.registration_sha256`), re-tied after the regeneration
(`FILL[REPORTED-ENERGY-REGISTRATION-DIGESTS]`; the merged packs carried qwen3-1p7b
`5560857668f053c99d0369161d4735015f4678a160b7a8423c7a7f357a50f5ea` and qwen3-8b
`04657a74de839a48ebf6bf55fe66f299fdd2e6401353c76d87d4d6ae843dae79`).

**Members.** Ordinals 1–10 are the absolute repeats; 11–50 are the ten null quads in A1, B1, B2, A2 order. Decode and
prefill-p42 read the same 50 bundles (the decode stages); prefill-p2048 reads the 50 bundles of the p2048 stages.

**Arithmetic, in the order the code performs it.** Let E1…E50 be the members' gross phase energies
(`phase_energy_j.decode` or `phase_energy_j.prefill`), r the first ten, and b_j the mean of quad j's four members.

1. Mean: `m = statistics.fmean(E1…E50)`. In exact arithmetic m = 0.2 × mean(r) + 0.8 × mean(b), because 10 of the 50
   members are repeats and 40 are quad members; the canonical value is the fifty-member mean.
2. Variance of m from the two strata: `V = 0.2² × s_r² / 10 + 0.8² × s_b² / 10`, with s_r and s_b the sample standard
   deviations (`statistics.stdev`, divisor n − 1) of the ten repeats and of the ten quad means. Pooling all 20 units
   into one s/√20 is rejected: it weights the units equally in the variance but not in the mean.
3. Half-width: `h = t(0.975, 9) × √V` with `t(0.975, 9) = 2.262157162798205`. Nine degrees of freedom is each
   stratum's own (10 − 1); a Welch–Satterthwaite combination would give between 9 and 18, so 9 is the conservative
   choice the contract fixes.
4. Recorded timing bounds. Every member records three non-negative energy bounds; each is averaged over the 50
   members and the three averages are summed with `math.fsum` into B. A missing kind refuses the cell; it is never
   zero by default.
   - `E_clock_anchor_shift_bound_j`: the largest change in the member's phase energy when the whole power trace is
     shifted by any common amount within ± its effective clock bound (registration §0.14), evaluated exactly at
     every breakpoint (`reduce.py` `_anchor_shift_envelope`).
   - `E_interpolation_joint_edge_bound_j`: the largest change when the phase start and end move independently by ±
     half their local record gaps (`reduce.py` `_interpolation_joint_edge_bound_j`). For interval-support traces,
     where the reducer already splits edge records by exact overlap, the function returns 0; all 48 block-3 phase
     windows recorded 0 (registration §16).
   - `E_whole_window_drift_allowance_j`: half the window's gross-family NEG-8 allowance (registration §0.12), the
     same value on every member of the window. The issuer must preserve this allocation (D-179 contract);
     `FILL[REPORTED-ENERGY-ISSUER]` cites the code line where it does.
5. Endpoints: `lower = m − h − B`, `upper = m + h + B`, evaluated in that order and not clamped at zero.
6. Per-token value: ΣE / ΣT over the same 50 members (a ratio of totals, never a mean of ratios). For decode, T is
   the runtime-observed output token count (512 per member, of which the decode phase produced the last 511;
   registration §0.5); the printed name is "decode-phase energy per output token (512 output tokens, 511 of them
   generated in the decode phase)". For prefill, T is the runtime-observed prompt token count (2048), and the four
   prompt-count surfaces (`prompt_realized`, `tokenize_end`, `prefill_start`, `total − output`) must agree, else
   `paper_reported_energy_prompt_surfaces_disagree`; decode is exempt from that check. A bad denominator refuses the
   per-token value only, not the mean.
7. The D-078 attribution floor (`binding.attribution_floor_j`, value and source `FILL[ATTRIBUTION-FLOOR-BINDING]`)
   is printed beside the cell and never added into its interval. Beside a mean it says: phase-edge timing alone could
   move this cell's energy by up to about that many joules, which the interval does not include.

**Worked example (synthetic).** Repeats r = 10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8, 10.1, 10.0, 9.6 J (mean 10.0,
s_r = 0.2); quad means b = 10.4, 10.1, 10.3, 10.2, 10.5, 10.0, 10.2, 10.3, 10.1, 9.9 J (mean 10.2, s_b = 0.18257).
m = 0.2 × 10.0 + 0.8 × 10.2 = 10.16 J. V = 0.04 × 0.04 / 10 + 0.64 × 0.033333 / 10 = 0.0022933; √V = 0.047889;
h = 2.262157 × 0.047889 = 0.10833 J. With kind averages 0.010, 0.000 and 0.050 J, B = 0.060 J, and the interval is
[9.9917, 10.3283] J. For decode with 512 output tokens per member, ΣE / ΣT = 508.0 J / 25,600 tokens =
0.019844 J/token.

**Outputs per cell** (closed schema `joulewise.paper_reported_energy_projection.v1`): `mean_j`, `lower_j`, `upper_j`,
`per_token.j_per_token`, `n_bundles` (= 50), plus the recomputation record
`interval {method, n_r, n_b, df, s_r, s_b, variance, h_j, kind_averages_j, B_j}`. The four paper cells are decode and
prefill-p2048 for each model; the two p42 cells are attempted, expected to refuse, and never printed.

**What the interval covers.** It covers repeat-to-repeat and quad-to-quad variation inside one window, plus the
recorded timing bounds. It does not cover variation between windows (ambient temperature, thermal history,
background state on another day): each model's cells come from one window. That conditioning and the D-179
dependence caveat are disclosed with every cell, and §8 registers a check of between-window variation.

## 5. Estimator 2: detection floors

**What a floor is, physically.** In a null quad both sides run the identical workload, so any A-versus-B difference
is produced by the instrument and the machine: sampler timing, where a phase edge falls inside a record, drift. The
floor of a cell is the largest such false difference the registered estimator allows, computed from that cell's
absolute repeats or null quads; hence the smallest real difference it can resolve.

**Binding.** Each floor pack's `extraction_spec.json` defines six floor cells per model (decode, prefill-p42 and
prefill-p2048, each in an **absolute** form over the 10 repeats and a **comparative** form over the 10 null-quad
differences; for example `d117-df-ph-decode-qwen3-1p7b-absolute` and `d117-df-cmp-abba-ph-decode-qwen3-1p7b`). The
merged specs were ALPHA `03fe7be896c50a21b97d38c914b813988d1fa6ac645df773b69e238c220b28af` and BETA
`8c984e6b82dce443f7dcc1cf57ea8ec890e5c77e216a365569762c45340ae811`; the regenerated digests are re-tied at seal. The
code is `joulewise/detection_floor.py` (`absolute_false_effect_floor`, `comparative_false_effect_floor`,
`two_shared_edge_common_mode_floor`) driven by `joulewise/floor_extraction.py` (`extract_absolute_cell`,
`extract_comparative_cell`). The p42 cells are expected to be non-extractable (§2.2).

**The D-054 point floor** (method `d054_false_effect_guard.v1`), for n values v_1…v_n:

- absolute form: v are the ten repeat energies; deviations r_i = v_i − mean(v); prediction = t × s × √(1 + 1/n);
- comparative form: v are the ten null-quad differences d_k = (B1 + B2 − A1 − A2)/2; deviations are the d_k
  themselves (not re-centred); prediction = |mean(d)| + t × s × √(1 + 1/n);
- s is the sample standard deviation of the deviations, t = 2.262 (`student_t_critical_95(9)`);
- **point floor** = max(max |deviation|, prediction). The √(1 + 1/n) factor is a prediction interval for one new
  value; it belongs to the floor and is excluded by name only from the reported-cell interval (§4, §12);
- **guard**: g(n) = 1 for n ≥ 10, √(9/(n − 1)) for 5 ≤ n < 10 (`small_sample_guard_factor`); guarded floor = g ×
  unguarded floor. With n = 10 on a PASS window, g = 1.

**Corner widening.** Each value may lie anywhere within ± its admissible half-width w_i (its timing uncertainty in
joules). The **corner-widened floor** is the largest point floor over every corner of that box (each v_i set to
v_i + w_i or v_i − w_i; 2¹⁰ = 1024 corners, exact enumeration, capped at n = 16), and at least the largest linear
deviation the box admits. The operative unguarded floor is max(point floor, corner-widened floor).

- Absolute form: w_i is the member's anchor-shift energy envelope half-width.
- Comparative form (D-124, `d124_two_shared_edge_common_mode.v1`, parameter digest
  `dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38`): within one quad, the phase onset and the phase
  offset are each treated as one **shared edge** that may move by a common amount within the bracket's operative
  fiducial bound b (the acceptance's drift allowance embedded exactly once, `registered_common_mode_operative_bound`).
  The quad difference is re-evaluated as the shared onset sweeps across [−b, b] and as the shared offset sweeps across
  [−b, b]; with z the difference at zero shift, the shared width is max(|min onset − z + min offset − z|,
  |max onset − z + max offset − z|) + |z − d_k|; the local width is half the sum of the four members' own residual
  half-widths; w_k = shared + local (`_common_mode_block_half_width`). The same treatment is applied once and
  identically on the floor cells and on the consuming contrast.

**Worked example (synthetic, computed with the repository functions).** Absolute: the ten repeats of §4 (mean 10.0,
s = 0.2, max |deviation| 0.4): prediction = 2.262 × 0.2 × √1.1 = 0.4745 J; point floor 0.4745 J. With w_i = 0.05 J
on every member the corner-widened floor is 0.5730 J. Comparative: d = 0.10, −0.05, 0.20, 0.00, −0.10, 0.05, 0.15,
−0.05, 0.10, 0.00 J (mean 0.04, s = 0.0966): prediction = 0.04 + 2.262 × 0.0966 × √1.1 = 0.2692 J; point floor
0.2692 J; with w_k = 0.30 J on every quad the corner-widened floor is 1.0349 J.

**How GAMMA uses them.** For each contrast, each side's floor comes only from its own model's cells for the same
phase and length (`exact_stack_only.v1`; no cross-length transport), taken worst case over that model's absolute and
comparative cells (`same_stack_componentwise_worst_case.v1`); the contrast's `floor_gate_j` is the larger of the two
sides' floors (`cross_stack_armwise_max.v1`). GAMMA's quads were measured in a different window from the floors
(ALPHA and BETA); the transfer rests on the registered assumption
`d124_block_timescale_shared_edges_stationarity_transfer_v1` ("the shared onset and offset edge treatment calibrated
on floor blocks transfers unchanged to the consuming contrast at the same block timescale"), whose own evidentiary
limit is "the historical corpus records bounds, not realized member-level boundary errors". Both are disclosed (§8).

## 6. Estimator 3: dominance ratios (D-165, D-168)

**The forcing question.** Is timing attribution the part of the floor that limits the measurement? For each model,
phase (decode, prefill-p2048) and form (absolute, comparative):

R = `corner_widened_unguarded_floor_j` ÷ `point_unguarded_floor_j` (`attribution_dominance_ratio.v1`)

R ≥ 2 (equality passes) means letting each value move within its timing box at least doubles the floor. From the §5
examples: absolute R = 0.5730 / 0.4745 = 1.21 (fails); comparative R = 1.0349 / 0.2692 = 3.84 (passes).

- The eight R values (2 models × 2 phases × 2 forms) are D-165's "independent" ratios: "independent" names the
  **independent-corner** box above (each member's or quad's width at its own corner), not statistical independence;
  the eight share members and are correlated.
- The four **R_cm** values (2 models × 2 phases, comparative only; `attribution_dominance_ratio_common_mode.v1`)
  replay the comparative floor with an additive energy change of one shared sign across all ten quads and every
  combination of independent local signs (`joulewise/dominance_closeout.py`). The replay does not apply the same
  timing shift in every quad or prove that its limit covers such a shift. Absolute R_cm is not applicable.
- A zero denominator refuses (`dominance_ratio_zero_denominator`); Infinity and NaN are never emitted.
- **Branch A** (every one of the eight R ≥ 2 and every required R_cm ≥ 2) licenses the dominance sentence and the
  contingent subtitle; otherwise **branch B** reports each failed component with null framing (the sentence says the
  component did not show timing dominance, and nothing more). R_cm passing licenses no physical-common-time
  robustness claim (D-165 addendum 2026-09-04).
- Every ratio is printed with its numerator and denominator in joules and labelled "point diagnostic; no interval".
  The ratios rest on thresholds applied to point values whose denominators depend on the data; the subtitle wording
  must not suggest statistical confirmation (§8 wording).

Output: the close-out artifact's eight plus four records and its recomputed global flags.

## 7. Estimator 4: the two GAMMA contrasts

### 7.1 Frozen inputs and arithmetic

Frozen in GAMMA's `analysis_manifest_v3.json` (merged: manifest id
`am-3283e9d37ffe36895c77b6168e2688793061b5b8edc48690211fb72b8811e128`, frozen semantics
`dfe508c2be5da02118bcb0d923f31a06a2bc686bd470fb7bbfa6cff2d391111e`, file SHA-256
`c3fd5405dd7e126431d56723a059abee67e7cb3b8471aab92fd9c63896ae835c`; re-tied after the regeneration).

| Contrast id | Metric | Sides (A, B) | Quads |
|---|---|---|---|
| `ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b` | `phase_energy_j.decode` | 1.7B, 8B | 10 |
| `ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b` | `phase_energy_j.prefill` | 1.7B, 8B | 10 |

Both are primary (`claim_role: primary`) and two-sided, with registered direction positive
(`scientific_hypothesis_direction`: 8B uses more phase energy than 1.7B), in one Holm family
(`d117-gamma-decode-prefill-p2048-primary-holm-v5`, m = 2, α = 0.05), fixed n = 10 quads, zero replacements,
`mde: null`. The quad order is fixed and **not randomized**: A1 = 1.7B, B1 = 8B, B2 = 8B, A2 = 1.7B in every quad
(manifest `design.randomization`: `scheme: deterministic_rotation`, `exchangeability: none`). The design is
interleaved, which the claims ladder requires for L2; the inference rests on the model that the ten quad differences
are independent draws once linear drift has cancelled.

**Arithmetic** (`abba_block_arm_mean_difference_t_v1`; quad construction in `joulewise/analysis_engine/__init__.py`,
estimate in `estimators.py:estimate_paired_blocks`):

1. Per quad k: `d_k = (B1 + B2)/2 − (A1 + A2)/2`.
2. `dbar = mean(d_k)`; `s_d` = sample standard deviation; `se_rep = s_d / √10`.
3. Metrology term: each member records governed random-error variances (the reducer's estimates of random
   measurement error in its phase energy; the gross-repetition term is left out). For each such term, the quad's
   variance is `(var_A1 + var_A2)/4 + (var_B1 + var_B2)/4`; summed over quads and divided by n² it is that term's
   squared standard error; `se_met` is the root of their sum; `se_total = √(se_rep² + se_met²)`. **Disclosed
   conservatism:** each member's random error is already part of the observed spread s_d, so adding se_met counts it
   twice. The interval is deliberately wider than a nominal 95% interval and its coverage is above 95%; the df stays 9.
   The reported cells (§4) add no such term.
4. `t* = round(t(0.975, 9), 3) = 2.262` (the engine rounds to three places; §4 uses 2.262157162798205); metrology
   interval `dbar ± t* × se_total`.
5. Deterministic bound total D: for each recorded deterministic kind, a quad's bound is the A-side mean of its two
   members' bounds plus the B-side mean of its two; D is the sum over kinds of the mean over quads. No cancellation
   across sides is assumed. The **decision interval** is the metrology interval widened by D on both sides.
6. Test: `t = dbar / se_total`, two-sided Student-t p-value with 9 degrees of freedom. Holm with m = 2: with
   p(1) ≤ p(2), adjusted p~(1) = min(1, 2 p(1)) and p~(2) = min(1, max(2 p(1), p(2))); a contrast is rejected when its
   adjusted p ≤ 0.05. A contrast that is not estimable keeps m = 2.

### 7.2 Outcome and ceiling, in full

The claim gate (`joulewise/analysis_engine/claims.py:evaluate_claim`) collects reason codes, then decides in this
precedence:

1. **`not_estimable`** if any code in the not-estimable set: `analysis_manifest_invalid`,
   `analysis_manifest_not_frozen`, `order_manifest_hash_mismatch`, `floor_artifact_invalid`,
   `metric_missing_or_nonfinite`, `insufficient_complete_blocks` (fewer than 2 complete quads),
   `runtime_token_denominator_required`, `stop_reason_required`, `output_policy_required`,
   `tokenizer_identity_mismatch`.
2. **`not_resolvable`** if there is no floor, or any code in the not-resolvable set. Member and window codes (none
   reachable on a PASS window, §2.2): `config_hash_mismatch`, `bundle_missing`, `bundle_strict_invalid`,
   `bundle_status_not_succeeded`, `whole_window_neg8_verdict_missing`, `whole_window_neg8_verdict_failed`,
   `adapter_continuity_evidence_missing`, `adapter_continuity_failed`, `cpu_admission_core_missing`,
   `cpu_admission_core_failed`, `whole_window_verdict_coverage_incomplete`,
   `whole_window_verdict_provenance_invalid`, `whole_window_verdict_conflict`,
   `calibration_bracket_exceeds_minted_bound`, `capture_pipeline_absent`, `capture_pipeline_superseded`,
   `paired_block_incomplete`, `fixed_n_plan_incomplete`, `window_evidence_precheck_missing`,
   `campaign_cooldown_evidence_missing`, `idle_window_suspect`, `idle_window_suspect_unknown`, every reducer reason
   code and every refusal-taxonomy code. Floor codes: `floor_row_missing`, `floor_row_ambiguous`, `floor_row_stale`,
   `floor_transport_inapplicable`, `floor_abs_missing`, `floor_cmp_missing`, `required_error_term_unknown`,
   `required_covariance_unknown`, `ratio_floor_conversion_undefined`, `equivalence_margin_not_above_floor`.
   Effect codes:
   - `interpolation_bound_exceeds_floor` (the contrast's summed `E_interpolation_joint_edge_bound_j` ≥ the floor)
     and `interpolation_bound_exceeds_half_effect` (that bound ≥ ½ |dbar|) (`__init__.py` `_interpolation_reasons`).
     *Trip risk assessed:* that bound is identically 0 for interval-support traces (§4), so these can trip only if
     the floor or dbar is exactly 0;
   - `effect_not_above_floor`: |dbar| ≤ `floor_gate_j`;
   - `deterministic_bound_obscures_direction`: the decision interval contains 0 while the metrology interval does
     not.
3. **`unresolved`** if the metrology interval contains 0, or Holm does not reject (`multiplicity_not_rejected`).
4. **`direction_supported`** otherwise; the direction is the sign of dbar.

**Leave-one-quad-out** (`sensitivity.py`; runs because n = 10). For each quad k the contrast is recomputed without
quad k. It is **verdict-influential**, and blocks L2 with `loo_verdict_influential`, if dropping some quad changes
the sign of the estimate, whether it is above the floor, the Holm rejection, or the outcome. It raises the
non-blocking concern `loo_magnitude_influential` if dropping some quad moves the estimate by more than 0.25 × the
threshold, the threshold being the floor because `mde` is null. With a large model difference and a floor near 1 J
this concern is likely; its wording is registered in §8.

**Randomization check.** Not run: the manifest's `deterministic_rotation` / `exchangeability: none` returns
`not_required` (`sensitivity.py:57-65`), so `randomization_check_insufficient_blocks` and
`randomization_sensitivity_disagrees` cannot arise. The unrandomized order is disclosed (§8).

**L2 ceiling.** `claim_evaluation.claim_ready_for_l2_l3` is true, and `claim_level_ceiling` is `L2`, only when all
hold: outcome `direction_supported`; `claim_role` primary; the engine's `confirmatory_status` is `confirmatory`; the
evidence class is not legacy; no `loo_verdict_influential`, `randomization_sensitivity_disagrees` or
`randomization_check_insufficient_blocks`; and the direction equals `scientific_hypothesis_direction` (positive).
Otherwise the ceiling is L1 wording. The registration's §1 table cites this definition.

**Worked example (synthetic).** d_k = 3.1, 2.9, 3.3, 3.0, 2.8, 3.2, 3.1, 2.9, 3.0, 2.7 J: dbar = 3.0 J,
s_d = 0.18257, se_rep = 0.057735. With a quad variance of 0.0100 J² in every quad, se_met = √(10 × 0.0100 / 100) =
0.031623 and se_total = √(0.0033333 + 0.0010000) = 0.065828. The metrology interval is 3.0 ± 2.262 × 0.065828 =
[2.8511, 3.1489] J; with D = 0.05 J the decision interval is [2.8011, 3.1989] J. t = 45.6, so p is far below 0.025.
With a floor of 1.2 J, |dbar| exceeds the floor, neither interval contains 0, Holm rejects, dbar > 0 matches the
registered direction, and leaving out any one quad moves dbar by at most 0.033 J (< 0.25 × 1.2): outcome
`direction_supported`, ceiling L2. The decision interval's lower end (2.80 J) also exceeds the floor (§8).

### 7.3 Registered magnitude estimates (descriptive, computed from the same quads)

The direction of the contrast is expected; the magnitude is what a reader needs. Three quantities are registered
now, computed by the disclosure producer from the same 40 members per contrast, never gating anything, and printed
beside the contrast as "registered descriptive estimates":

1. **Ratio of phase energies, 8B to 1.7B.** Per quad, ρ_k = ln[ ((B1 + B2)/2) / ((A1 + A2)/2) ]; ρ̄ = mean(ρ_k), s_ρ
   their sample standard deviation; ratio = exp(ρ̄) with interval exp(ρ̄ ± 2.262157 × s_ρ / √10). Recorded timing
   bounds are not propagated into it (stated in the wording). *Synthetic example:* side means 10.0 and 13.0 J in
   every quad give ρ_k = 0.26236 and ratio 1.300.
2. **Per-token difference.** dbar / 512 J per output token (decode) and dbar / 2048 J per prompt token
   (prefill-p2048), with both intervals of §7.1 divided by the same constant. Valid because every member's
   runtime-observed token counts equal the registered counts (registration §6); otherwise this estimate refuses.
3. **Gross-energy sentence.** Fixed wording: "Phase energy is gross: it includes the machine's baseline power over
   the phase, and the 8B phase lasts longer, so part of the difference is baseline power times the extra duration."

## 8. Disclosures computed beside the claims

All are computed by code from structural or non-science evidence, except the cross-window check (which uses the
released energies by a rule fixed here), and printed with the results:

- **Attempt history and conditionality:** every attempt of every pack with its verdict, cause codes and class,
  printed beside each reported cell and contrast as "attempts of this pack: N (classes …)". Fixed sentence: "These
  numbers are conditional on a window that passed the registered quiet, timing and reference-drift checks."
- **Single window:** "All 50 members of this cell were measured in one window; the interval covers variation within
  that window, not between days or windows. The repeats and quads are modelled as independent units; that is an
  assumption (D-179 dependence caveat)."
- **Cross-window consistency check** (registered rule; never changes a number). For each model and phase: G = the
  mean over GAMMA's 10 quads of that model's side mean, h_G = 2.262157 × s(side means) / √10; F = the model's
  reported cell mean (ALPHA or BETA) and h_F its D-179 half-width h (without B). Δ = G − F. If |Δ| ≤ √(h_G² + h_F²):
  "GAMMA's and the floor window's estimates agree within their within-window intervals (difference Δ J)." Otherwise:
  "GAMMA's and the floor window's estimates differ by Δ J, more than their within-window intervals cover; the
  reported intervals understate between-window variation, which includes different interleaving and thermal
  history."
- **Floor transfer:** the assumption and evidentiary limit quoted in §5, verbatim.
- **Decision interval against the floor:** for each contrast, whether the decision interval's lower end (upper end,
  for a negative estimate) is beyond the floor. If it is not: "The estimate exceeds the floor, but its decision
  interval reaches below the floor."
- **Leave-one-quad-out magnitude concern**, if raised: "Leaving out quad k moves the estimate by X J, more than a
  quarter of the floor; the direction, the floor status and the multiplicity decision are unchanged."
- **Order:** "Every quad ran 1.7B, 8B, 8B, 1.7B in that fixed order; the order was not randomized, and the p-value
  assumes the ten quad differences are independent."
- **Conservative contrast interval:** the se_met double count of §7.1 step 3, and the rounded t*.
- **Battery:** each window's #421 verdict (computed before any energy was read).
- **Clock:** the number of members with anchor status `bounded` (all, in a PASS window) and the largest effective
  bound per window.
- **Reference drift:** each window's NEG-8 screen result and allowance.
- **Environment:** per cell and per window, the count of science members flagged by `FILL[ED-PREDICATE]`, and the
  idle-drift and pre/post idle-window flags of registration §8 item 3. Waiver wording for the latter (claims ladder
  L1): "The pre- and post-request idle-window GPU diagnostics flagged N members; they describe the idle slices around
  the request, not the measured phase, and are waived for L1 as registered." No reduced mean is computed (D-179).
- **p42:** "The 42-token prefill of the decode workload is shorter than one power record and could not be resolved;
  as registered, no p42 value is reported."
- **Attribution floor:** the §4 step 7 sentence beside each reported cell.
- **Separate windows:** the 1.7B and 8B reported cells were collected in separate windows in a fixed order; their
  difference is not a comparison (claims ladder: forced order stays below L2).
- **Dominance:** "R is a point diagnostic with no interval; 'independent' names the independent-corner component."
- **D-177:** phase attribution is reported without a measured instrument phase-accounting check.
- **Fixed prompt:** the decode contrast uses one fixed prompt (D-166 addendum); no prompt-population generality is
  claimed.

## 9. What is printed, and from which artifact

Under the current D-174 fallback no row below has a placement; each becomes printable only through the placement
ruling of registration §15 Q5. Site ids are the proposed `CP-X…` sites of `docs/contracts/paper_comparison_placements.md`.

| Printed quantity | Artifact (schema) | Field | Proposed site | Status now |
|---|---|---|---|---|
| Models, workload, L = 2048 | selection record; prompt pin; panel | `selected_prefill_tokens`; pinned identities | CP-X01-identity, CP-X01-length | PROPOSED_STOP_FILL |
| Reported energy: mean, interval, J/token, n (4 cells) | `joulewise.paper_reported_energy_projection.v1` | `mean_j`, `lower_j`, `upper_j`, `per_token.j_per_token`, `n_bundles` | CP-X05-* | RETIRED_FALLBACK (needs a ruling) |
| Attribution floor beside each cell | projection binding | `binding.attribution_floor_j` | CP-X05-* | RETIRED_FALLBACK |
| Floors (4 model/phase cells) | `joulewise.detection_floor_artifact.v2` | `floor_gate_j` and component census | CP-X04-* | PROPOSED_STOP_FILL |
| Dominance ratios with numerators and denominators; branch sentence; subtitle | `joulewise.d165_dominance_closeout.v1` | 8 R, 4 R_cm, their floors, `branch`, licensing flags | CP-X02-*, CP-X03-* | PROPOSED_STOP_FILL |
| Contrast tables (decode, prefill) | `joulewise.claim_verdicts.v1` + finalized manifest | `estimator`, `deterministic_bounds.decision_interval`, `floor`, `multiplicity`, `claim_evaluation` | CP-X06-table, CP-X07-table | PROPOSED_STOP_FILL |
| Ratio and per-token difference (§7.3) | disclosure producer output | registered fields | `FILL[DISCLOSURE-SITES]` | not proposed yet |
| Verdict sentences (abstract, discussion, conclusion) | `joulewise.claim_verdicts.v1` | `claim_evaluation.outcome`, `direction`, `claim_level_ceiling` | CP-X08-* | PROPOSED_STOP_FILL |
| Before-comparison refusal (if any window or gate refuses) | campaign log, whole-window verdict | governing row and reason | CP-X09-* | PROPOSED_STOP_FILL |
| Disclosures of §8 | harvest records, whole-window verdicts, ED output, disclosure producer | counts, verdicts, registered sentences | `FILL[DISCLOSURE-SITES]` | not proposed yet |

Every printed number is `MEASURED` (copied or conservatively rounded from these fields) or `DERIVE` (computed by a
formula named in this plan); none is recalculated from prose.

## 10. Analysis-plan rows (`docs/contracts/analysis_plans.md` fields)

| Field | Decode contrast | Prefill-p2048 contrast | Reported cells (each) |
|---|---|---|---|
| Plan id / consumer | `B5-GAMMA-DECODE` / phase-energy paper | `B5-GAMMA-PREFILL-P2048` | `B5-REPORTED-<model>-<phase>` |
| family_id, role | `d117-gamma-decode-prefill-p2048-primary-holm-v5`, primary | same, primary | none (L1, no inference across cells) |
| Selection scope | decode, Qwen3 1.7B vs 8B, prompt 0, forced 512 | prefill at 2048 tokens, same pair | one model, one phase, its 50 members |
| Multiplicity | Holm, m = 2, α = 0.05 | same | none |
| Metric, window class | gross `phase_energy_j.decode`, phase window | gross `phase_energy_j.prefill`, phase window | gross phase energy, phase window |
| Unit, dependence | A/B/B/A quad side-mean difference, 10 quads, modelled independent | same | 10 repeats + 10 quads (20 units), modelled independent |
| Estimator | §7.1 | §7.1 | §4 |
| Inclusion, waivers | registration §6 validity; pre/post idle-window diagnostics waived as worded in §8 | same | same; any absent member refuses |
| Order, blocking, covariates | fixed unrandomized A/B/B/A interleaving cancels linear drift; no covariates | same | fixed member order |
| Floor gate | `floor_gate_j`, side-wise max (§5) | same | attribution floor printed beside, not a gate |
| n sizing, top-up | fixed n = 10 from the frozen manifest; no replacement, no top-up | same | fixed 50 |
| Denominator | none for the contrast; 512 output tokens for the §7.3 per-token difference | none; 2048 prompt tokens for §7.3 | runtime-observed tokens |
| Holdout | not applicable (L2) | not applicable | not applicable |
| Ceiling; forbidden upgrade | L2 per §7.2; no claim about other prompts, lengths, models or machines | L2; same | L1; no model comparison from these cells |
| Disqualifiers | §7.2 outcomes and sensitivity codes | same | D-179 refusal codes |
| Linked manifests | filled after execution from the finalized manifest and bundle hashes | same | projection bindings |

## 11. Analysis code that must exist (pinned in the seal record)

| Need | State at this writing | FILL |
|---|---|---|
| Production reported-energy issuance through D-173 custody, projecting each cell independently and preserving the whole-window allowance allocation | Absent ("No production dispatch exists", `joulewise/paper_reported_energy.py:457`; the fixture path projects three cells in one pass) | `REPORTED-ENERGY-ISSUER` |
| `_v5` final pinset and v2 input manifest for the mint (decode and prefill-p2048 cells only) | Absent (`docs/process/v5-artifact-flow.md`, "What does not exist yet") | `V5-FINAL-PINSET`, `V5-V2-INPUT-MANIFEST` |
| Mint-to-close-out adapter | Absent (same source) | `MINT-TO-CLOSEOUT-ADAPTER` |
| Claim verdicts to results-fill input (RENDERER-V5-SUCCESSOR-01) | Absent (same source) | `CLAIM-VERDICT-TO-FILL-ADAPTER` |
| Environmental diagnostic producer | Not designed (registration §8) | `ED-PREDICATE` |
| Disclosure producer for §7.3 and §8, including the step-4 p42 exit rule | Absent | `DISCLOSURE-PRODUCER` |

Preferred: each merged under the normal gates (with the measurement-code final pass) and pinned before `ALPHA-1`
arms. Permitted otherwise: written and merged before the release event by seats that have read no claim-window
energy, against this plan's text, pinned in a seal-record extension, and exercised by the blind dry run (§3.2)
before the release.

## 12. What the analysis never does

- Exclude, replace, reweight or re-collect a member after collection; compute a mean over fewer than the registered
  members; pool members across attempts or windows; analyse a superseded window's energies.
- Use the pooled s/√20 interval, a mean of per-member ratios, configured token counts, the `detection_floor.py`
  √(1 + 1/n) prediction term as a reported-cell interval or deterministic term, or any floor other than the minted
  one.
- Treat the ALPHA-versus-BETA difference of reported means as a comparison.
- Test one-sided, change α, m, the registered direction or the contrast set, or add a contrast.
- Read an energy before the release event, or let any energy value inform a recovery decision.
- Report any analysis not registered here except as clearly labelled exploratory.

## 13. FILLs specific to this plan

`B5-ANALYSIS-CUSTODY-ROOT`, `B5-BLIND-DRY-RUN-RECORD`, `P42-S1-STRUCTURAL-CHECK`,
`REPORTED-ENERGY-REGISTRATION-DIGESTS`, `V5-FINAL-PINSET`, `V5-V2-INPUT-MANIFEST`, `MINT-TO-CLOSEOUT-ADAPTER`,
`REPORTED-ENERGY-ISSUER`, `CLAIM-VERDICT-TO-FILL-ADAPTER`, `DISCLOSURE-PRODUCER`, `DISCLOSURE-SITES`, and, shared with
the registration, `ED-PREDICATE`, `ATTRIBUTION-FLOOR-BINDING` and `V5-PACK-REGEN-RECORD`. The open questions are
registration §15; Q5 (placement), Q10 (code timing) and Q16 (attribution floor) bear directly on this plan.

## 14. Disposition of draft critiques

Three blind critics (science, feasibility, replicability) reviewed revision 1 (`9900a047`). Every item was checked
against the code on `origin/main` at `c88565c4`. Items not listed as rejected or partly rejected were accepted and
fixed where shown. Section references are to revision 2 (R = registration, A = this plan).

**Science (S).** S1 p42 refusal: fixed (R §0.5; A §2.2, §3 step-4 rule, step 10 per-cell issuer). S2 PASS window
losing a cell: fixed by extending window validity (R §6, R §7.1 table; A §2.2); the extractor's exclusion is now
unreachable on a PASS window. S3 outcome rules: fixed (A §7.2); the interpolation trip-risk assessment needed no
synthetic study because the bound is identically 0 for interval-support traces (verified on all 48 block-3 phase
windows). S4 between-window variation: fixed (A §4 last paragraph, §8 cross-window check and floor transfer; R
§0.8). S5 window choice after supersession or END STATE: fixed (A §2.1, §2.3). S6 post-release repairs: fixed (A
§3.2). S7 magnitude: **partly accepted**: a quad-level log-ratio estimate, the per-token difference and the
gross-energy sentence are registered as descriptive estimates (A §7.3); a Fieller interval and the alternative of
forbidding any printed ratio were not adopted, because the log-ratio is simpler to replicate and the ratio is the
number a reader needs. S8 "reads no energy value": fixed (R §0.12, §7.2; A §8); **one detail rejected**: the
`neg8_bracket` numbers the critic cited (0.05 J, 0.25) do not gate (`whole_window.py`: "neither numeric tolerance
gates this amended estimand"); the gate is the derived NEG-8 bound. S9 floor judged on the point estimate: fixed as a
registered disclosure (A §8). S10 environmental diagnostic: **partly rejected**: the report-only sensitivity figure
(mean and contrast without flagged members) is a reduced mean that D-179 forbids ("no post-collection admission
filter and no 49-member mean"); instead the window-level trigger with a binomial threshold is recommended (R §8). S11
dominance ratios: fixed (A §6, §8). S12 se_met double count and t* rounding: fixed as disclosures (A §7.1, §8). S13
floor definition: fixed, one definition (R §0.10, A §5). S14 attribution floor source: fixed as
`FILL[ATTRIBUTION-FLOOR-BINDING]` plus R §15 Q16 and the meaning sentence (A §4 step 7). S15 decode J/token
denominator: fixed (R §0.5, A §4 step 6). S16 blinding leaks: fixed (R §9.2).

**Feasibility (F).** F1 30 s idle voids every anchor: fixed (R §2.0 a, §5.3, §15 Q14); confirmed in code
(`MIN_RATE_FIT_BASELINE_S = 60.0`) and on block-3 data (about 54 s at observed cadence). F2 GAMMA's duplicated
interior reference: fixed (R §2.0 b, §6 distinct-reference assertion). F3 in-chain verdict without bracket binding:
fixed by the desk route (R §2.0 c, §3.3 step 2, §5.1); the alternative of adding a binding stage to the packs was not
chosen, to match block 4 and the runbook. F4 missing OFF, dwell and start-budget admission for `TRANSACTION_PACK`:
fixed (R §12.2). F5 clock convention: fixed (R §5.3; ρ = 8 ppm, stream definition, calibration streams, worst case
enforced); the stream ceiling is now about 175 s, which leaves no room for a retry wait at 55 s idle (R §15 Q1). F6
8B cycles and cooldown cap: fixed (R §5.2 cap sizing and the `s1` cooldown observations; a cap hit is RECOVER-E, R
§6, §7.1). F7 disk model: fixed (R §4 item 8); APFS clones are preferred to hardlinks. F8 duration: fixed (R §3.3
step 1, §3.4, §15 Q15). F9 attempt history, quiescence and Spotlight: fixed (R §3.4, §4 item 11); **one detail not
adopted**: the `.metadata_never_index` marker is not prescribed, because its effect on 25G83 is unverified; the
mechanism is a FILL that must be verified. F10 re-freeze after each pin advance: fixed (R §0.21, §3.3 step 4); **one
detail rejected**: `db41703c` is now on main (PR #477 merged as `c88565c4`). F11 GAMMA-only stages first run in
GAMMA-1: fixed (R §12.3 dry render; R §7.4 narrowed supersession, still a cold-gate question, Q9). F12 deadline stop
without a class: fixed (R §5.2, §7.1: class T with a registered resizing rule). F13 authority literal: fixed (R
§0.17, §2.1 item 9). F14 G3 fit for floor windows: fixed (R §0.20, §6, `FILL[G3-CLAIM-ARGS]`). F15 untracked sizing
source: fixed (R §5.2: block 4's committed adapter binds; this draft's scratch is a design estimate only). F16
GAMMA schema: fixed (R §2.0 d, §12.2). F17 wrong clock facts: fixed (R §5.3: T 111.8–128.5 s, ρ 3.248–3.279 ppm,
about 58 s shorter at 30 s idle).

**Replicability and pedagogy (P).** P1 floor and dominance arithmetic: fixed (A §5, §6, with worked examples
computed by the repository functions). P2 phase-energy rule: fixed (R §0.4). P3 511 versus 512: fixed (R §0.5, A
§4). P4 clock-anchor feasible set: fixed (R §0.14). P5 pulse calibration and acceptance numbers: fixed (R §0.11),
including that the policy's 0.01 s drift field is not a comparator. P6 NEG-8: fixed (R §0.12); the label's origin is
stated as an inherited name. P7 timing bounds and allocation: fixed (A §4 step 4). P8 sensitivity flags: fixed (A
§7.2). P9 two L2 predicates: fixed, one definition (A §7.2), cited by R §1. P10 guard items and CPU criteria: fixed
(R §0.13). P11 member timeline: fixed (R §0.3). P12 dwell predicate: fixed (R §0.18). P13 G3: fixed (R §0.20). P14
`pgrep` argv: made a FILL copied from the driver's census code (R §4 item 1) rather than typed from memory. P15 floor
definition: fixed (as S13). P16 unreachable §7.3 trigger: fixed by counting across attempts (R §7.3) and
`FILL[ANCHOR-RUNTIME-EFFECT]` (R §0.14). P17 one event-to-verdict table: fixed (R §7.1). P18 two record thresholds
and p42: fixed (R §0.5; A §2.2). P19 "no pack has two PASS attempts": fixed (R §3.1; A §1). P20 df 9 and the rounded
t*: fixed (A §4 step 3, §7.1 step 4). P21–P29 overloaded words: fixed by building "measurement block", "quad",
"side", "workload-switch reference", "tie" versus "bound", the plan senses, "commit" versus "ledger tip", the two
floors and the admission terms; the diagram's square brackets became boxes in prose and "refuted" became "challenged
by a refuter seat". Code identifiers keep their names in backticks. P30–P31 terms before first use: fixed by
restructuring R §0 into §0.1–§0.22 and this plan's terms list. P32 suspect quality flags: fixed (R §6, §8 item 3; A
§8 waiver wording). P33 sizing columns: fixed (all columns emitted in the hashed `sizing_v2.json`; formulas in R
§5.2). P34–P35 unsourced figures: fixed with hashed scratch records or code citations (R §0.3, §4 item 8, §8, §16).
P36 "a third of every cycle": replaced with the burst-length argument and both burst counts (R §15 Q1). P37
truncated hashes and elided commands: full digests given, and commands cited to `v5-artifact-flow.md` rows. P38
42-token source: fixed (R §0.5). P39 duration arithmetic and "own boot": recomputed (R §3.4); "own boot" withdrawn
(R §4 item 7). P40 diagram markers: redrawn (R §3.2). P41 drift-cancellation example: added (R §0.8).
