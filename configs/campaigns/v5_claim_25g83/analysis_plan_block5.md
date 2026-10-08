# Analysis plan V5-CLAIM-25G83-B5: what is computed from the claim windows, and how

Status: **Revision 12, 2026-10-07.** This file has its sealed bytes in the seal commit: the commit that follows the final head of the code (H_claim, registration §0.18) and carries the final text of this file and of the registration together with the filled `sealed_inventory.json` (registration §11). It is sealed when the seal record of registration §12, the document that lists the SHA-256 of every sealed file, exists and pins this file's SHA-256. (Revision 3 is commit `71c91d74`, revision 4 ends at commit
`7261a585`, revision 5 at `9d63b4df`, revision 6 at `c6843537`, revision 7 at `dc046d4d`, revision 8 at `30d92227`,
revision 9 at `bc8ad4ae`, revision 10 at `1d97f0a60`, revision 11 at `7c19c9c79`; the changes of revisions 4 to 12 are listed in §14.) Companion to
`registration_block5.md` (the **registration**) and `flag_catalog.json` (the **flag catalog**) in the same directory;
they are sealed together and none binds alone. Terms are those built in registration §0; terms that first appear here
are built where they first appear. Every rule is fixed before any claim byte exists. Most estimators below are already
frozen in committed bytes (the D-179 contract, the floor packs' `extraction_spec.json`, GAMMA's
`analysis_manifest_v3.json`); this plan ties those bytes, states the arithmetic so that it can be recomputed by hand,
and fixes what they leave open: inputs, exclusions, the estimator when units are removed, order of operations,
disclosures and what is printed from which artifact. Numbers in worked examples are **synthetic** and labelled so;
they are not measurements.

**What changed from revision 2.** Revision 2 analysed the one attempt per pack whose verdict was PASS, and a PASS
window had every member valid, so no member was ever excluded after collection. Under Ed's 2026-10-05 ruling a
member that fails a check costs only its own unit. This revision therefore registers: the analysed window is each
pack's first claim-usable attempt (§1, §2.1); the exclusion function's output is the only source of exclusions
(§2.2); the reported-cell estimator, the floors and the contrasts are computed over the kept units, with at least 5
of 10 per stratum (§4, §5, §7; 8 in revisions 3 to 9, set to 5 by the seal gate); and the exclusions are disclosed beside every number (§8). This amends D-179 ruling 1
and D-078's no-reduced-mean text (registration §10 item 4). Revision 2's disposition of three blind critiques is in
commit `bfd1ee8c`, §14 of this file there.

**Terms first used here.**

- **Kept unit.** A unit (a repeat or a quad, registration §0.8) none of whose members the exclusion function removed.
  n_r and n_b are the numbers of kept repeats and kept quads of a cell.
- **Analysed attempt.** For each pack, its first claim-usable attempt in arm order (registration §7.2).
- **Prospective manifest.** GAMMA's `analysis_manifest_v3.json`: the contrasts, their estimator, **multiplicity family** (the set of contrasts whose p-values are corrected together, here both contrasts under the Holm correction of §7.1)
  and floor rules, frozen before any collection. Its **frozen-semantics hash** is the SHA-256 of its
  analysis-relevant fields, so any later change to them is detectable.
- **Finalization.** The step that ties the identities of the collected bundles, the whole-window verdict, the bracket
  binding, the ledger, the aggregate floor, the dominance replay sidecar and the analysed attempt's exclusions to the
  prospective manifest without reading any effect estimate; its output is the **finalized manifest**.
- **Claim gate.** The program (`python -m joulewise analyze-claims`) that, from the finalized manifest, computes each
  contrast and decides its outcome and its **claim ceiling**: the highest level of the claims ladder (registration §0.19) that a sentence about the contrast may reach, here L2 or only L1 (§7.2).
- **Sidecar.** A separately hash-tied file emitted beside the mint: here the dominance replay inputs.
- **Pinset.** The list of content hashes the mint may consume. **v2 input manifest.** The mint's list of which
  extraction-report cells feed which floor role (decode, prefill).
- **Close-out.** The artifact that records every dominance ratio and decides branch A or B (§6).
- **Placement.** A registered site in the paper where an issued value may be rendered. **D-173 custody** is the only
  route by which a paper supplier may read evidence: the supplier names a **role** and a runs root, and a **supply
  map** returns every path and digest, so no caller-chosen path enters a number.
- **Issuer.** The production program that writes the D-179 reported-energy projection (§4).
- **Placement states.** `MEASURED`: copied or conservatively rounded from an issued field. `DERIVE`: computed by a
  formula named in this plan. `PROPOSED_STOP_FILL`: a proposed site whose fill is blocked until adopted.
  `RETIRED_FALLBACK`: a site retired by the D-174 fallback, printable only after a new ruling.
- **Blind dry run.** Steps 1–11 of §3 run on the real bytes before the release event, with every output kept in
  restricted custody and only structure serialized (§3.2).

## 1. When the analysis runs, and on what

1. The analysis runs once, after the measurement block closes (every pack has an analysed attempt, or END STATE,
   registration §7), after the blind dry run has completed (§3.2), and after the release event (registration §8), at a
   commit whose analysis programs are pinned by an addendum to the seal record (§11).
2. It reads exactly one attempt per pack: the pack's **first claim-usable attempt** in arm order, by the rule that
   `joulewise.flags.exclusions.first_claim_usable`, a function of the sealed exclusion module, states in code (at `9b0c680ed` only tests call that function; the analysis code of §11 must apply it). An attempt that is claim-usable but
   carries an UNCLASSIFIED code is undecided until that code is classified blind (registration §7.2); the analysis
   does not start while any analysed attempt is undecided. A pack is never armed again after a claim-usable attempt
   (a scheduling rule of registration §7.2 that no program enforces: the lead session that arms the next window, the magistrate of registration §5.7, applies it from the harvest verdicts), so there is exactly one analysed attempt per pack.
3. It reads evidence only through authenticated routes (for paper suppliers, D-173's
   `open_paper_input(role, runs_root)`); no caller-supplied path, digest or value enters a number.
4. Everything it emits is retained in analysis custody `FILL[B5-ANALYSIS-CUSTODY-ROOT]` and handed to the results
   cold gate before any paper sentence is filled.

## 2. Inclusion and exclusion

### 2.1 Attempts and superseded windows

Attempts other than the analysed one (NULL, not claim-usable, HARVEST_FAULT before its cure, or later than the first
claim-usable one) are never inputs to any number. They are listed with their verdicts, cause keys and flag counts in
the attempt history (§8). Windows of a measurement block that was superseded under registration §7.5 are retained and
disclosed structurally; their energies are never analysed, in this plan or as a secondary analysis.

### 2.2 Members and units

The analysed attempt's `derived/exclusions.json` (schema `joulewise.exclusions.v1`, written by the harvest from the
sealed catalog) is the only source of exclusions. Its SHA-256 is pinned by finalization (§3 step 8) and by the
reported-energy projection (§3 step 10); its `catalog_sha256` must equal the sealed catalog's digest in the seal
record, and its recorded harvest commit must be the one the §11 item 4 addendum pins, or the step goes to R3. (That §11 is the registration's. Its item 4 requires an addendum to the seal record, written before ALPHA-1's harvest, that names the harvest program's files, their SHA-256s and the commit of the desk checkout, which is the checkout, other than the measurement checkout, that the harvest runs from. The harvest writes that commit into `exclusions.json` once the change to the harvest program that the same item describes, the harvest lane, has landed.)

- A member it removes is removed from every cell it feeds. A removed repeat member removes that repeat; a removed quad member removes its whole quad, so the quad's drift cancellation is kept.
- Every target cell has at least 5 kept units in each stratum: this is part of `claim_usable`, so it holds on every
  analysed attempt. If an analysis program finds fewer, the program and the exclusion function disagree: the
  analysis stops and the step goes to R3.
- Nothing else excludes a member after collection. The floor extractor's same-slot exclusion of a cooldown-cap member
  and the claim gate's member-level codes (`paired_block_incomplete`, `fixed_n_plan_incomplete`,
  `window_evidence_precheck_missing`, `campaign_cooldown_evidence_missing`, `idle_window_suspect`) must not fire on a
  unit the exclusion function kept, and must not be raised merely because the exclusion function removed a unit. If
  one fires on a kept unit, the registration's member rules and the code disagree: the analysis stops and the step
  goes to R3.
- **p42.** The p42 phase is expected to overlap fewer than 3 records and fail its precheck on every member
  (registration §0.5). Its outcomes are recorded and block nothing: the p42 reported cells refuse with their D-179
  codes, and the p42 floor cells are non-extractable (§3 step 4). The expectation is checked at ALPHA-1's harvest by
  the s1-structural diagnostic (p42 precheck counts, registration §3).

### 2.3 END STATE after one or both floor packs were claim-usable

Fixed now: an analysed floor window is analysed for its L1 outputs only: its reported cells (§4) and the floor cells
of its extraction (§3 step 4), with the separate-window and END STATE disclosures of §8. Contrasts (§7), dominance
ratios (§6) and the aggregate mint need all three packs and are never computed from a partial block. The one
exception: if a cold gate rules, before any release, that the cause of the END STATE invalidates the analysed
windows, they are not analysed. The END STATE design record cannot choose otherwise.

### 2.4 A lost midpoint reference: `neg8.midpoint_lost`

*Forcing problem.* Each window's whole-window drift allowance (registration §0.12) is the larger of the NEG-8 bound
and the **spread**: the largest minus the smallest of the start-triplet mean, the midpoint reference's energy and the
end-triplet mean. Each member carries half of it as `E_whole_window_drift_allowance_j`, which enters a reported cell's
recorded timing bounds B (§4 step 4) and a contrast's deterministic bound total D (§7.1 step 5). The midpoint is the
only NEG-8 reference inside the window (GAMMA's two diagnostic interior references enter neither the screen nor the
allowance, registration §0.12). Of the references that run between the start and end triplets it is the only one the spread reads: GAMMA's two diagnostic interior references run one in the middle of its decode stages and one in the middle of its prefill stages, and their role is not a NEG-8 role. If the midpoint is lost (registration §0.12: failed and not restored by its spare, or
contaminated), the spread falls back to |end mean − start mean|, so an excursion that rises in the middle of the window and reverts by its end is no longer measured, and the allowance can only shrink. The midpoint sits at the
boundary between the decode and prefill arms (the window's decode stages and its prefill stages), after fifty decode members (forty in GAMMA), the one place where such
an excursion is physically expected, and no block has yet measured how large these excursions are.

*Rule* (NEG-8 cold ruling of 2026-10-07, decision 2, made operational by orchestrator ruling Q11 of 2026-10-07,
which the seal gate confirms; registration §7.2, §14 Q11). The flag catalog keeps `neg8.midpoint_lost` DISCLOSE.

- **On GAMMA** the flag removes the attempt from the claims: the sealed exclusion function adds the window reason
  `neg8.midpoint_lost_primary` (`joulewise.flags.exclusions.PACK_SCOPED_WINDOW_REASONS`), so the attempt is not
  claim-usable. It is therefore never GAMMA's analysed attempt (§1 item 2); GAMMA is re-armed, and the attempt, like
  every attempt that is not analysed, is an input to no number and is listed in the attempt history with its cause
  (§2.1, §8). The rule reads only the roster's pack id and the flag's code, never an energy, so the choice of
  GAMMA's analysed window cannot depend on its contrasts.
- **On ALPHA and BETA** the window keeps its screen result, its allowance and its numbers, and stays claim-usable;
  the flag is disclosed beside its reported cells and floors (§8.1).

*Scope.* The rule removes only GAMMA attempts. A lost midpoint on ALPHA or BETA can understate that window's
allowance, and so the bound B of its four reported cells, by an amount nothing measured; it is nevertheless only
disclosed (the fixed sentence of §8.1), because no decision rests on B: the reported cells are L1 instrument results
whose interval is printed, not tested. On GAMMA the allowance enters D, on which the decision
`deterministic_bound_obscures_direction` rests, so an understated D could let a direction claim through. (A floor's
value does not use the drift allowance, §5; the floor extraction only records each window's allowance beside the floor,
and refuses a cell when it is absent, §3.1 step 4.)

*Check in the claim gate.* By the rule above, GAMMA's analysed attempt never carries `neg8.midpoint_lost`. If the
claim gate finds the flag on it, the exclusion function and the code disagree: the analysis stops and the step goes to R3, as in §2.2.

*Worked example (synthetic).* GAMMA-1's arm-boundary midpoint reference fails idle admission, and its spare
overlaps a competing process, which the harvest finds, so the window carries `neg8.midpoint_lost`. Its
`exclusions.json` reads `claim_usable` false with `reasons` [`neg8.midpoint_lost_primary`]. GAMMA-2 is armed; it
keeps its midpoint and is claim-usable, so GAMMA-2 is the analysed attempt and its decode contrast (dbar = 3.0 J,
§7.2's example) can reach L2. GAMMA-1's contrasts are never computed. Had ALPHA-1 carried the flag, it would have
stayed claim-usable, and its reported cells would print as L1 with the flag disclosed.

*What would change it.* Nothing within block 5. A block's midpoint record (each window's spread with and without the midpoint, computed from reference energies and so read only after that block's release event) may show that the midpoint never moved the spread beyond the bound; a cold erratum may then downgrade the flag to disclose-only on GAMMA for a later block.
It cannot reinstate a block-5 attempt that was re-armed: when the record is read GAMMA's attempts are over, and reinstating one would choose the analysed window after its energies were seen (registration §0.12, §10; seal gate, stage 1).

## 3. Order of operations

### 3.1 The steps

The steps run in the order of their numbers, with one exception: step 6, the close-out, runs after step 8, finalization, because its program takes the finalized manifest as an input and rejects a manifest that is not finalized or that lacks the replay-sidecar attachment finalization writes. Each step runs on bytes that earlier steps wrote; each output is content-addressed (SHA-256) and the step that reads it
authenticates it. Every step reads the kept units from §2.2 and nothing else. Full command lines are those of
`docs/process/v5-artifact-flow.md` at the pinned commit (rows "Floor extraction", "Mint", "Finalization", "Claim gate"
and "Results fills").

| # | Step | Program | Output |
|---|---|---|---|
| 1 | Strict validation of every kept bundle of the three analysed attempts | `python -m joulewise validate-bundle --strict <bundle>` | exit 0 per bundle |
| 2 | Re-reduction into restricted custody (never inside a bundle) | `python -m joulewise reduce <bundle> --output <custody>/<bundle_id>.rereduced.json` | summary per bundle |
| 3 | Read the exclusions of each analysed attempt and fix each cell's kept units | lane L9 consumer of `exclusions.json` | kept-unit list per cell, hash-tied |
| 4 | Floor extraction, ALPHA and BETA separately, each with its pack's `extraction_spec.json`, over kept units, given the window's harvest archive so that the drift allowance is the one the harvest's NEG-8 screen left standing (registration §0.12) | `scripts/extract_detection_floors.py … --hash-bundles`, with the archive argument that lane L9-NEG8 adds (§11) | `joulewise.detection_floor_extraction.v1` ×2 |
| 5 | Production mint of the aggregate floor and its dominance replay sidecar; the v2 input manifest feeds only the decode and prefill-p2048 cells | `scripts/mint_floor_artifact_generalized.py` with `FILL[V5-FINAL-PINSET]` and `FILL[V5-V2-INPUT-MANIFEST]` | `joulewise.detection_floor_artifact.v2`; `joulewise.d165_dominance_replay.v1` |
| 6 | Dominance close-out; it runs after step 8, whose finalized manifest it reads (`--finalized-manifest`) together with the aggregate floor and the replay sidecar of step 5 | adapter `FILL[MINT-TO-CLOSEOUT-ADAPTER]`, then `scripts/build_d165_dominance_closeout.py` | `joulewise.d165_dominance_closeout.v1` |
| 7 | (removed: revision 2's L10-C rehearsal; the blind dry run of §3.2 runs these steps on the real bytes) | | |
| 8 | Finalization of GAMMA's prospective manifest with its attachments (whole-window verdict, bracket binding, ledger, aggregate floor, dominance replay sidecar, GAMMA's exclusions) | `scripts/finalize_analysis_manifest.py` | finalized manifest |
| 9 | Claim gate, one `--evidence-root` per floor pack, given the harvest archive of each window whose drift allowance it reads (GAMMA's for the contrasts' D; lane L9-NEG8 makes every claim consumer take it, §11) | `python -m joulewise analyze-claims … --neg8-harvest-archive <archive>` | `joulewise.claim_verdicts.v1` |
| 10 | Reported-energy projection, each cell independently, so a refusing cell (p42) leaves the others issued | production issuance of `joulewise.paper_reported_energy_projection.v1` through D-173 custody, `FILL[REPORTED-ENERGY-ISSUER]` | one projection record per cell |
| 11 | Descriptive estimates, disclosures and results fills for adopted placements | §7.3 and §8 by `FILL[DISCLOSURE-PRODUCER]`; adapter `FILL[CLAIM-VERDICT-TO-FILL-ADAPTER]`, then `scripts/render_results_fills.py` and `--validate-rendered` | issued values; validated Markdown |
| 12 | Results cold gate: re-derive every printed number from the artifacts of steps 3–11 | judge + refuter | gate record |

**Refusals.** A refusal at any step stops the steps after it, with one registered exception: if step 4 exits 1 and
its refused cells are only the p42 floor cells and no kept member was omitted from the spec, the report it wrote is
the input to step 5 and the exit is recorded as the registered p42 outcome. A tooling refusal goes to R3 and the step
re-runs on identical bytes; a refusal that is a registered scientific outcome (for example a not-resolvable contrast)
is the result and is printed as such.

**Early floor rehearsal (optional, never blocking).** Once ALPHA and BETA both have analysed attempts and the L9 code
has landed, steps 3–5 may be run on scratch copies of their bytes, serializing only structure, to find floor-path
defects before GAMMA's harvest. It never holds GAMMA's arm (revision 2's blocking L10-B step is withdrawn).

### 3.2 Blind dry run, and repairs after the release

The issuer, pinset, input manifest, adapters, the exclusions consumer and the disclosure producer are written blind
(§11). A repair written after the energies are visible would be a choice made with the outcome in view. Therefore:

1. **Before the release event**, steps 1–11 run end to end on the real bytes, outputs in restricted custody. Only
   structure is serialized: each step's exit status, schema validity, output digest and refusal codes, with any code
   that encodes a numeric comparison of a science quantity released only as "outcome-class refusal at step N". Every
   tooling refusal is cured by R3, blind, and the dry run repeats until it completes with no tooling refusal
   (`FILL[B5-BLIND-DRY-RUN-RECORD]`).
2. **After the release**, the analysis re-runs steps 1–11 from identical bytes at the pinned commit; every output
   digest must equal the dry run's. A mismatch stops the analysis and goes to R3 as a determinism defect.
3. **A repair needed after the release** is allowed only if it is written and reviewed by seats that have read no
   released number, adds a synthetic fixture reproducing the failure, and leaves every other registered synthetic
   fixture's output byte-identical. Any other change goes to a cold gate before it runs, and its outputs are labelled
   as produced after unblinding.

## 4. Estimator 1: reported phase energy per model and phase (D-179, amended for kept units)

**What it is.** For each model and each of decode, prefill-p42 and prefill-p2048, one gross phase energy averaged
over the cell's kept units, with an interval that respects the units. Normative home:
`docs/contracts/paper_reported_energy.md`. **Registration digests** (`REPORTED-ENERGY-REGISTRATION-DIGESTS`, filled
from committed bytes at `f8164893`, re-tied at seal, that is, recomputed from the bytes at the final head of the code (registration §2 item 1) and written here again; where a digest still waits for that, a FILL mark named `B5-FINAL-HASHES` stands in its place, §13): each floor pack's `extraction_spec.json` names the reported-energy
registration it implements in `reported_energy_registration.registration_sha256`:

- ALPHA: `5560857668f053c99d0369161d4735015f4678a160b7a8423c7a7f357a50f5ea`, in
  `configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json` (file SHA-256 at the final head of the code:
  `FILL[B5-FINAL-HASHES]`; revisions 4 to 11 printed `8b7969851c576032a89ebd00c5d3a4396e1eba264d4d1e6a4603420fecd15c5c`, the file's digest at `f8164893`, which went stale when commit `f4cf90472` regenerated the file);
- BETA: `04657a74de839a48ebf6bf55fe66f299fdd2e6401353c76d87d4d6ae843dae79`, in
  `configs/campaigns/d117_floor_qwen3-8b_v5/extraction_spec.json` (file SHA-256 at the final head of the code:
  `FILL[B5-FINAL-HASHES]`; revisions 4 to 11 printed `53e71b38ab9c9851744ee84e792263e081c78156f941e9ab782f924a132809c7`, the file's digest at `f8164893`, stale for the same reason).

Both specs are `procedure_only` and carry no post-collection numeric value. At `9b0c680ed` each spec still names the registration digest written above; only the two file digests have moved.

**Members.** Ordinals 1–10 are the absolute repeats; 11–50 are the ten null quads in A1, B1, B2, A2 order. Decode and
prefill-p42 read the decode stages' 50 bundles; prefill-p2048 reads the p2048 stages' 50.

**Arithmetic, in order.** Let r be the gross phase energies of the n_r kept repeats (`phase_energy_j.decode` or
`phase_energy_j.prefill`), and b the means of the four members of each of the n_b kept quads.

1. **Mean.** When all 20 units are kept: `m = statistics.fmean(E1…E50)`, the canonical value as issued today. When any
   unit was removed: `m = 0.2 × fmean(r) + 0.8 × fmean(b)`. The two agree in exact arithmetic at full n, because 10 of
   the 50 members are repeats and 40 are quad members. The weights 0.2 and 0.8 are fixed by design, not by what was
   kept: a plain mean over the kept members would shift weight between the strata whenever n_r ≠ n_b.
2. **Variance** of m from the two strata: `V = 0.04 × s_r² / n_r + 0.64 × s_b² / n_b`, with s_r and s_b the sample standard deviations (`statistics.stdev`, divisor n − 1) of the kept repeats and of the kept quad means.
3. **Half-width:** `h = t(0.975, min(n_r, n_b) − 1) × √V`, with exact quantiles t(0.975, 9) = 2.262157162798205,
   t(0.975, 8) = 2.306004135204166, t(0.975, 7) = 2.364624251592785, t(0.975, 6) = 2.446911851, t(0.975, 5) =
   2.570581836, t(0.975, 4) = 2.776445105 (the last three to nine places; L9 pins them exactly). Using the smaller stratum's degrees of freedom is
   the conservative choice; a Welch–Satterthwaite combination would give more.
4. **Recorded timing bounds.** Every member records three non-negative energy bounds: `E_clock_anchor_shift_bound_j`
   (the largest change in the energy assigned to the member's phase when each of the phase's two edges is displaced, on its own, by up to the **edge bound** g, while the whole power trace is shifted by up to ± the member's effective clock bound m, registration §0.14; g = b + s, where b is the window's **operative fiducial bound**, that is, the calibration bracket's recorded `b_fiducial_s`, the larger of its pre and post captures' fiducial bounds plus the bracket's own allowance, in seconds, for drift between those two captures, registration §0.11, and s is the change in wall minus monotonic time over the member's sampler stream, registration §0.14;
   the exact rule and a worked example close this step), `E_interpolation_joint_edge_bound_j` (identically 0 for interval-support traces, as all
   48 block-3 phase windows recorded), and `E_whole_window_drift_allowance_j` (half the window's gross-family NEG-8
   allowance, registration §0.12; the NEG-8 check is run on two families of reference energies, the gross energies and the idle-subtracted energies, each with its own allowance, and this is the gross one). The allowance is the one the harvest's `derived/neg8-allowance.json` names: the
   verdict row's own **NEG-8 bracket** (a second meaning of the word: not the pre and post calibration pair of registration §0.11, but the NEG-8 screen's record inside the whole-window verdict, `idle_admission_core.neg8_bracket`, which holds the screen's result and each family's allowance) when the harvest found no new loss (`stored_verdict`), or, when the harvest re-ran the
   screen on the surviving references and it passed, the bracket in `withheld/neg8-rescreen-bracket.json`
   (`survivor_rescreen`), never the verdict row's, which may still include a reference the harvest found
   contaminated (cold pass 2 N4; Sol delta audit A1). It is read through
   `whole_window.harvest_neg8_allowance_bracket`, which authenticates the record and recomputes a re-screened
   allowance; with no record, or one that does not authenticate, there is no allowance and the cell refuses
   (`whole_window_drift_allowance_unrecorded`). The same holds for D in §7.1. For each kind, its stratified average is 0.2 × (mean over the kept repeats) + 0.8 ×
   (mean over the members of the kept quads); at full n this equals the 50-member average. The three averages are
   summed with `math.fsum` into B. A missing kind refuses the cell; it is never zero by default. *The first kind, exactly* (orchestrator's ruling of 2026-10-07 on registration §14 Q5). The reducer assigns to a phase each power record's power times the length of that record's overlap with the phase (the overlap rule, registration §0.4). Where the records lie against the phase's two edges is known only within the timing bounds named at the head of this step: b, s and m, with g = b + s. Write E(x, y) for the energy the overlap rule assigns to the stretch from x to y, and t_on, t_off for the phase's recorded edges. The member's bound is the largest |E(t_on + e_on + d, t_off + e_off + d) − E(t_on, t_off)| over every e_on and every e_off between −g and +g, each chosen on its own, and every d between −m and +m, the one shift applied to both edges. Power is never negative, so the assigned energy cannot rise as the start edge moves later and cannot fall as the end edge moves later; the extremes over e_on and e_off therefore lie at the four corners e_on = ±g, e_off = ±g, and the reducer evaluates those four, each over every d. The result is the field `max_abs_delta_j` of the member's **anchor-shift energy envelope** for the phase: the record, in the member's `summary_metrics.json`, of the smallest and the largest energy over these movements (§5 describes the record; method `common_trace_shift_plus_independent_edge_corners_v3`, `joulewise/reduce.py` `_corner_composed_anchor_shift_envelope`). The summary stored in the bundle was reduced under the pre capture's fiducial bound alone, so the bound is not read from it: it is read from the member's summary as reduced again, in memory, under b, which is the summary the floor extraction (§5) and the claim gate (§7) read. *Worked example (synthetic).* b = 45.6 ms and s = 0.4 ms, so g = 46 ms; m = 2 ms; the record that holds the start edge averages 40 W, the record that holds the end edge averages 10 W, and every displaced edge stays inside its record. The largest change has the start edge 46 ms early and the end edge 46 ms late, which adds 0.046 × (40 + 10) = 2.30 J, and then both edges a further 2 ms early, which adds 0.002 × (40 − 10) = 0.06 J: the bound is 2.36 J. In that case, and only in it, the bound equals g × (P_on + P_off) + m × |P_off − P_on|, with P_on and P_off the average powers of the two records. When a displaced edge crosses into a neighbouring record that expression is only an approximation (on recomputed members of earlier windows it missed the exact bound by between −63% and +20%); the registered quantity is the exact maximum.
5. **Endpoints:** `lower = m − h − B`, `upper = m + h + B`, in that order, not clamped at zero.
6. **Per-token value:** 0.2 × (ΣE ÷ ΣT over the kept repeats) + 0.8 × (ΣE ÷ ΣT over the members of the kept quads), a
   ratio of totals within each stratum. For decode, T is the runtime-observed output token count (512 per member, of
   which the decode phase produced the last 511); the printed name is "decode-phase energy per output token (512
   output tokens, 511 of them generated in the decode phase)". For prefill, T is the runtime-observed prompt token
   count (2048), and the four prompt-count surfaces must agree. Every kept member's realized counts equal the
   registered counts (a mismatch removes the member), so this value equals m ÷ T; at full n it equals D-179's ΣE ÷ ΣT
   over the 50 members. A bad denominator refuses the per-token value only, not the mean.
7. **Attribution floor** (`binding.attribution_floor_j`; a formula is registered and no number is bound, by the orchestrator's ruling of 2026-10-07 on registration §14 Q5). *Forcing problem:* the first kind of step 4 says how far phase-edge timing alone could move the energy assigned to one member's phase, and its stratified average is inside the interval, as part of B. But every member of a window is reduced under that window's one operative fiducial bound: if the sampler's edges sit late, they sit late in every member, so this part of the bound does not shrink when members are averaged. A reader therefore needs the largest single-member value beside the cell. Earlier rulings named a constant for it, D-078's "about 1 J", which was one member's bound in a window of 2026-07-25 under another macOS build, model and calibration (registration §0.10); block 5 computes each cell's own value instead.
   *Rule:* the attribution floor of a cell is the largest first-kind bound (`E_clock_anchor_shift_bound_j`, step 4) over the cell's kept members. The issuer computes it at step 10 of §3.1 from the window's own members and bracket, and records with it the member that attains it and the smallest value over the kept members; the stratified average of the same bound is already recorded, as the first entry of the output field `interval.kind_averages_j` (Outputs per cell, below). The attribution floor is printed beside the cell and is not added to its interval (the output field `attribution_floor_composed` stays false). It is an energy of a claim window, so it is restricted until the release event. *Worked example (synthetic).* The kept members' bounds run from 1.95 J to 2.36 J (the member of step 4's example) and their stratified average is 2.12 J: 2.12 J is inside B, and the cell prints an attribution floor of 2.36 J. (The two cell examples below keep the small synthetic kind averages of earlier revisions, 0.010 J for this kind; they show the arithmetic, not the size.)
   *Fixed sentence*, with X the attribution floor: "Phase-edge timing alone could move the energy assigned to this phase of a single request by up to X J. The average of that bound over the kept members is already inside the interval, as part of B; X itself is not added. The bound says how far the assigned energy moves when power is taken as constant within each sampler record; it is not a bound on the physical energy of the phase."

**Worked example, all units kept (synthetic).** Repeats r = 10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8, 10.1, 10.0, 9.6 J
(mean 10.0, s_r = 0.2); quad means b = 10.4, 10.1, 10.3, 10.2, 10.5, 10.0, 10.2, 10.3, 10.1, 9.9 J (mean 10.2,
s_b = 0.18257). m = 0.2 × 10.0 + 0.8 × 10.2 = 10.16 J. V = 0.04 × 0.04 / 10 + 0.64 × 0.033333 / 10 = 0.0022933;
√V = 0.047889; h = 2.262157 × 0.047889 = 0.10833 J. With kind averages 0.010, 0.000 and 0.050 J, B = 0.060 J and the
interval is [9.9917, 10.3283] J. Decode per token: 10.16 / 512 = 0.019844 J/token.

**Worked example, units removed (synthetic, same data).** The exclusion function removed repeat 6 (10.3 J) and quads 5
(10.5 J) and 9 (10.1 J): n_r = 9, n_b = 8. Kept means: fmean(r) = 9.96667 J, fmean(b) = 10.175 J, so
m = 0.2 × 9.96667 + 0.8 × 10.175 = 10.13333 J. (A plain mean over the 41 kept members would give 10.12927 J, because it
weights the strata 9/41 and 32/41; that is why the stratified form is registered.) s_r = 0.18028, s_b = 0.16690;
V = 0.04 × 0.032500 / 9 + 0.64 × 0.027857 / 8 = 0.00014444 + 0.00222857 = 0.0023730; √V = 0.048714; degrees of freedom
min(9, 8) − 1 = 7; h = 2.364624 × 0.048714 = 0.11519 J, 6.3% wider than with all units. With B = 0.060 J the interval
is [9.9581, 10.3085] J. Decode per token: 10.13333 / 512 = 0.019792 J/token.

**Outputs per cell** (closed schema `joulewise.paper_reported_energy_projection.v1`, extended by L9): `mean_j`,
`lower_j`, `upper_j`, `per_token.j_per_token`, `n_bundles` (the kept members), plus the recomputation record
`interval {method, n_r, n_b, df, s_r, s_b, variance, h_j, kind_averages_j, B_j}`, the kept and removed unit ids, and
the SHA-256 of the exclusions document.

**What the interval covers.** Repeat-to-repeat and quad-to-quad variation inside one window over the kept units, plus
the recorded timing bounds. It does not cover variation between windows, nor any bias from which units were removed;
§8 discloses both.

## 5. Estimator 2: detection floors

**What a floor is, physically.** In a null quad both sides run the identical workload, so any A-versus-B difference is
produced by the instrument and the machine: sampler timing, where a phase edge falls inside a record, drift. The floor
of a cell is the largest such false difference the registered estimator allows; hence the smallest real difference it
can resolve.

**Binding.** Each floor pack's `extraction_spec.json` defines six floor cells per model (decode, prefill-p42 and
prefill-p2048, each in an **absolute** form over the kept repeats and a **comparative** form over the kept null-quad
differences), re-tied at seal (the two file digests of §4). The code is `joulewise/detection_floor.py` (`absolute_false_effect_floor`,
`comparative_false_effect_floor`) driven by `joulewise/floor_extraction.py`. The p42 cells are expected to be
non-extractable (§2.2).

**The D-054 point floor**, for the n kept values v_1…v_n (n = n_r for the absolute form, n_b for the comparative):

- absolute form: v are the kept repeat energies; deviations r_i = v_i − mean(v); prediction = t × s × √(1 + 1/n);
- comparative form: v are the kept null-quad differences d_k = (B1 + B2 − A1 − A2)/2; deviations are the d_k
  themselves (not re-centred); prediction = |mean(d)| + t × s × √(1 + 1/n);
- s is the sample standard deviation of the deviations; t = `student_t_critical_95(n − 1)` from the code's table (2.262 for 9 degrees of freedom, 2.306 for 8, 2.365 for 7, 2.447 for 6, 2.571 for 5, 2.776 for 4);
- point floor = max(max |deviation|, prediction);
- **guard**: g(n) = 1 for n ≥ 10 and √(9/(n − 1)) for 5 ≤ n < 10 (`small_sample_guard_factor`): g(9) = 1.0607,
  g(8) = 1.1339, g(7) = 1.2247, g(6) = 1.3416, g(5) = 1.5; the function is undefined below 5, which is why the
  cell minimum is 5 (registration §6.6). Guarded floor = g × unguarded floor.

**Corner widening.** Each value may lie anywhere within ± its admissible half-width w_i (its timing uncertainty in
joules). The corner-widened floor is the largest point floor over every corner of that box (2ⁿ corners, exact
enumeration, capped at n = 16), and at least the largest linear deviation the box admits. The **operative** unguarded
floor, operative meaning the value that every later step uses, is max(point floor, corner-widened floor). Absolute form: w_i comes from the member's **anchor-shift energy envelope**. That is the record, in the member's `summary_metrics.json` (field `energy_anchor_shift_envelopes`, written by the pinned reducer, `joulewise/reduce.py`, with one entry for each energy of the member; the entry for the cell's phase energy is the one used), of the range that phase energy can take when the power trace is moved in time against the phase's two edges within the member's three timing bounds: its effective clock bound and the change in wall minus monotonic time over its stream (both registration §0.14), and the fiducial bound of the calibration it was reduced under (registration §0.11); the reducer version the member was reduced with fixes how the three are combined. The record holds the energy with no movement (`point_j`), the smallest and largest energy over those movements (`lower_j`, `upper_j`) and the largest absolute change, the larger of point − lower and upper − point (`max_abs_delta_j`). w_i is the largest of point − lower, upper − point and `max_abs_delta_j`, plus the member's `E_interpolation_joint_edge_bound_j` (§4 step 4).
Comparative form (D-124, `d124_two_shared_edge_common_mode.v1`, parameter digest
`dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38`): within one quad, the phase onset and the phase
offset are each treated as one shared edge that may move by a common amount within the calibration bracket's operative fiducial
bound b (the bracket's recorded `b_fiducial_s`, in seconds: the larger of its pre and post captures' fiducial bounds plus the bracket's drift allowance, registration §0.11; `registered_common_mode_operative_bound` refuses unless the bracket passed and b equals that sum); the quad difference is re-evaluated as the shared onset sweeps [−b, b] and as the shared offset sweeps
[−b, b]; with z the difference at zero shift, the shared width is max(|min onset − z + min offset − z|,
|max onset − z + max offset − z|) + |z − d_k|; the local width is half the sum of the four members' own residual
half-widths (a member's residual half-width is the `max_abs_delta_j` that the reducer's envelope function, `_corner_composed_anchor_shift_envelope`, returns for that member's trace and phase window when it is given the member's effective clock bound, the change in wall minus monotonic time over its stream (both in registration §0.14) and a fiducial bound of zero; the fiducial part is carried once, by the shared edges); w_k = shared + local. The same treatment is applied once and identically on the floor cells and on the
consuming contrast.

**Worked examples (synthetic, computed with the repository functions at `a0a4f5a7`).**
- Absolute, all ten repeats of §4 (mean 10.0, s = 0.2, max |deviation| 0.4): prediction = 2.262 × 0.2 × √1.1 =
  0.4745 J; with w_i = 0.05 J on every member the operative floor is 0.5730 J; g = 1.
- Absolute, repeat 6 removed (n = 9, mean 9.96667, s = 0.18028, max |deviation| 0.36667): prediction = 2.306 ×
  0.18028 × √(10/9) = 0.4382 J; operative unguarded floor 0.5435 J; guarded 1.0607 × 0.5435 = 0.5765 J.
- Comparative, d = 0.10, −0.05, 0.20, 0.00, −0.10, 0.05, 0.15, −0.05, 0.10, 0.00 J (mean 0.04, s = 0.0966):
  prediction = 0.04 + 2.262 × 0.0966 × √1.1 = 0.2692 J; with w_k = 0.30 J on every quad the operative floor is
  1.0349 J.
- Comparative, quads 5 and 9 removed (n = 8, mean 0.05, s = 0.09258): prediction = 0.05 + 2.365 × 0.09258 × √(9/8) =
  0.2822 J; operative unguarded floor 1.0896 J; guarded 1.1339 × 1.0896 = 1.2354 J.

**How GAMMA uses them.** For each contrast, each side's floor comes only from its own model's cells for the same
phase and length (`exact_stack_only.v1`), taken worst case over that model's absolute and comparative cells
(`same_stack_componentwise_worst_case.v1`); the contrast's `floor_gate_j` is the larger of the two sides' floors
(`cross_stack_armwise_max.v1`). GAMMA's quads were measured in a different window from the floors; the transfer rests
on the registered assumption `d124_block_timescale_shared_edges_stationarity_transfer_v1` ("the shared onset and
offset edge treatment calibrated on floor blocks transfers unchanged to the consuming contrast at the same block
timescale"), whose own evidentiary limit is "the historical corpus records bounds, not realized member-level boundary
errors". Both are disclosed (§8).

## 6. Estimator 3: dominance ratios (D-165, D-168)

**The forcing question.** Is timing attribution the part of the floor that limits the measurement? For each model,
phase (decode, prefill-p2048) and form (absolute, comparative), over the kept units:

R = `corner_widened_unguarded_floor_j` ÷ `point_unguarded_floor_j` (`attribution_dominance_ratio.v1`)

R ≥ 2 (equality passes) means letting each value move within its timing box at least doubles the floor. From the
first and third §5 examples: absolute R = 0.5730 / 0.4745 = 1.21 (fails); comparative R = 1.0349 / 0.2692 = 3.84
(passes). Both numerator and denominator are unguarded floors, so the guard g(n) does not enter R.

- The eight R values (2 models × 2 phases × 2 forms) are D-165's "independent" ratios: "independent" names the
  independent-corner box above, not statistical independence; the eight share members and are correlated.
- The four R_cm values (2 models × 2 phases, comparative only) replay the comparative floor with an additive energy
  change of one shared sign across all kept quads and every combination of independent local signs
  (`joulewise/dominance_closeout.py`). R_cm passing licenses no physical-common-time robustness claim (D-165
  addendum 2026-09-04).
- A zero denominator refuses (`dominance_ratio_zero_denominator`); Infinity and NaN are never emitted.
- **Branch A** (every one of the eight R ≥ 2 and every required R_cm ≥ 2) licenses the dominance sentence and the
  contingent subtitle; otherwise **branch B** reports each failed component with null framing.
- Every ratio is printed with its numerator and denominator in joules, its n, and the label "point diagnostic; no
  interval".

## 7. Estimator 4: the two GAMMA contrasts

### 7.1 Frozen inputs and arithmetic

Frozen in GAMMA's `analysis_manifest_v3.json`
(`configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/analysis_manifest_v3.json`; re-tied at seal: file SHA-256 at
the final head of the code `FILL[B5-FINAL-HASHES]`). Lane L10 changed GAMMA's interior references
(registration §2), not this manifest.

| Contrast id | Metric | Sides (A, B) | Planned quads |
|---|---|---|---|
| `ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b` | `phase_energy_j.decode` | 1.7B, 8B | 10 |
| `ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b` | `phase_energy_j.prefill` | 1.7B, 8B | 10 |

Both are primary and two-sided, with registered direction positive (8B uses more phase energy than 1.7B), in one Holm
family (`d117-gamma-decode-prefill-p2048-primary-holm-v5`, m = 2, α = 0.05), zero replacements, `mde: null`. The
quad order is fixed and **not randomized**: A1 = 1.7B, B1 = 8B, B2 = 8B, A2 = 1.7B in every quad. The inference rests
on the model that the quad differences are independent draws once linear drift has cancelled.

**Amendment.** The manifest's fixed n = 10 is the planned n. The analysed n of a contrast is its kept quads, at least
5 (registration §6.6); a quad with any removed member is dropped. The claim gate does not raise
`fixed_n_plan_incomplete` or `paired_block_incomplete` for a quad the exclusion function removed (§2.2), and
finalization records GAMMA's exclusions digest so the manifest's frozen semantics stay unchanged and the analysed n is
traceable. `FILL[GAMMA-MANIFEST-EXCLUSIONS-BINDING]` names how L9 binds them.

**Arithmetic** over the n kept quads (`abba_block_arm_mean_difference_t_v1`; `joulewise/analysis_engine`):

1. Per kept quad k: `d_k = (B1 + B2)/2 − (A1 + A2)/2`.
2. `dbar = mean(d_k)`; `s_d` = sample standard deviation; `se_rep = s_d / √n`.
3. Metrology term: the engine reads governed random-error variances only for the metric `energy_request_j`; for
   the two phase metrics of block 5 none is recorded, so `se_met = 0` and `se_total = se_rep`. Each member's
   run-to-run error is already inside s_d (the d_k are observed with it), so a term added in quadrature would count it
   twice: in simulation the plain t interval covers 95.0% and the doubled one 99.8% (seal gate, stage 1). Errors that
   are not random from run to run (a calibration timing bias common to all members) are carried by D (step 5) and by
   the attribution floor (§4 step 7), never by this interval.
   (Terms of this step. The *metrology term* `se_met` is a standard error that the engine adds in quadrature to
   `se_rep` when a metric has one: `se_total = √(se_rep² + se_met²)`. It is built from *random-error variances*:
   variances, in J², that a member's summary records for a named source of run-to-run error. *Governed* means that
   the engine reads such a variance only when the summary's reducer version and idle-estimation method are a pair
   the code lists. The one such variance is `E_idle_mean_j2`, the variance of the member's idle-baseline mean taken as an
   energy; the engine reads it for `energy_request_j` and for no other metric.)
4. `t* = round(t(0.975, n − 1), 3)` (the engine rounds to three places: 2.262, 2.306 and 2.365 for n = 10, 9 and 8;
   2.447, 2.571 and 2.776 for n = 7, 6 and 5). The **metrology
   interval** (the engine's name, `metrology_aware_ci95`, for the 95% interval of dbar from its standard error alone,
   before the deterministic bounds of step 5 are added) is `dbar ± t* × se_total`.
5. Deterministic bound total D: for each recorded deterministic kind, a quad's bound is the A-side mean of its two
   members' bounds plus the B-side mean of its two; D is the sum over kinds of the mean over kept quads. The
   **decision interval** is the metrology interval widened by D on both sides.
6. Test: `t = dbar / se_total`, two-sided Student-t p-value with n − 1 degrees of freedom. Holm with m = 2: with
   p(1) ≤ p(2), adjusted p~(1) = min(1, 2 p(1)) and p~(2) = min(1, max(2 p(1), p(2))); a contrast is rejected when its
   adjusted p ≤ 0.05. A contrast that is not estimable keeps m = 2.

### 7.2 Outcome and ceiling

The claim gate (`joulewise/analysis_engine/claims.py:evaluate_claim`) collects reason codes, then decides in this
precedence:

1. **`not_estimable`** if any code in the not-estimable set: `analysis_manifest_invalid`,
   `analysis_manifest_not_frozen`, `order_manifest_hash_mismatch`, `floor_artifact_invalid`,
   `metric_missing_or_nonfinite`, `insufficient_complete_blocks`, `runtime_token_denominator_required`,
   `stop_reason_required`, `output_policy_required`, `tokenizer_identity_mismatch`.
2. **`not_resolvable`** if there is no floor, or any code in the not-resolvable set: member and window codes (none
   reachable on a kept unit of an analysed attempt, §2.2), floor codes (`floor_row_missing`, `floor_row_ambiguous`,
   `floor_row_stale`, `floor_transport_inapplicable`, `floor_abs_missing`, `floor_cmp_missing`,
   `required_error_term_unknown`, `required_covariance_unknown`, `ratio_floor_conversion_undefined`,
   `equivalence_margin_not_above_floor`), and the effect codes `interpolation_bound_exceeds_floor`,
   `interpolation_bound_exceeds_half_effect` (that bound is identically 0 for interval-support traces, so these trip
   only if the floor or dbar is exactly 0), `effect_not_above_floor` (|dbar| ≤ `floor_gate_j`) and
   `deterministic_bound_obscures_direction` (the decision interval contains 0 while the metrology interval does not).
3. **`unresolved`** if the metrology interval contains 0, or Holm does not reject.
4. **`direction_supported`** otherwise; the direction is the sign of dbar.

**Leave-one-quad-out**, over the kept quads: for each kept quad the contrast is recomputed without it (n − 1 quads).
It is **verdict-influential**, and blocks L2 with `loo_verdict_influential`, if dropping some quad changes the sign of
the estimate, whether it is above the floor, the Holm rejection, or the outcome. It raises the non-blocking concern
`loo_magnitude_influential` if dropping some quad moves the estimate by more than 0.25 × the floor. (Today's engine
runs it only on complete contrasts; L9 makes it run on the kept quads.)

**Randomization check.** Not run: the manifest's `deterministic_rotation` / `exchangeability: none` returns
`not_required`. The unrandomized order is disclosed (§8).

**L2 ceiling.** `claim_ready_for_l2_l3` is true, and the ceiling is `L2`, only when all hold:

- the outcome is `direction_supported`;
- `claim_role` is primary or secondary (the code accepts either; both block-5 contrasts are primary, so no outcome
  differs);
- `confirmatory_status` is `confirmatory`. The engine sets that value unless a top-up touches any registered entry
  of the manifest (the manifest's entries are its registered members, one bundle expected for each; for a manifest
  of GAMMA's kind the engine does not narrow this to the contrast's own entries, so one top-up demotes both
  contrasts). A replacement is a bundle collected in place of a registered one that failed, tagged with the entry
  it replaces and with a reason the manifest allows. A top-up is either a bundle in the runs root beyond the
  registered ones whose scientific configuration (its configuration with the run id and any replacement tags left
  out) equals a registered entry's and which is not a valid replacement, or a second successful replacement of
  one entry. On a top-up the engine sets `demoted_exploratory`, with the reason `outcome_dependent_top_up`.
  Block 5 registers no top-up and no replacement (§10), and GAMMA's manifest allows no replacement reason
  (`allowed_replacement_reasons` is empty);
- the evidence class is not legacy: the gate's `evidence_class` is `current`. It is `legacy_l1` only when the claim
  gate is run with its `--legacy-l1-mechanics` option, which step 9 of §3.1 does not use;
- there is no `loo_verdict_influential`;
- the direction equals the registered direction (positive).

Otherwise the ceiling is L1 wording. Two further parts of the code's condition cannot arise in block 5 and are
written here so that the condition can be rebuilt whole: the outcome `equivalent` also passes, but it needs a
registered equivalence margin (a half-width inside which the two sides would be declared equal) and both contrasts
register none (`equivalence: null`); and two reason codes of the randomization check block the ceiling
(`randomization_sensitivity_disagrees`, `randomization_check_insufficient_blocks`), but that check is not run
(above). (A GAMMA attempt carrying `neg8.midpoint_lost` is not claim-usable and is never analysed, §2.4.) The
registration's §1 table cites this definition.

**Worked example (synthetic).** d_k = 3.1, 2.9, 3.3, 3.0, 2.8, 3.2, 3.1, 2.9, 3.0, 2.7 J, with quad 4 removed: n = 9,
dbar = 3.0 J, s_d = 0.19365, se_rep = 0.064550; se_met = 0 for the phase metrics, so se_total = 0.064550. t* = 2.306;
the metrology interval is 3.0 ± 2.306 × 0.064550 = [2.8511, 3.1489] J; with D = 0.05 J the decision interval is
[2.8011, 3.1989] J. t = 46.5, so p is far below 0.025. With a floor of 1.2 J, |dbar| exceeds the floor, neither
interval contains 0, Holm rejects, dbar > 0 matches the registered direction, and leaving out any one kept quad moves
dbar by at most 0.0375 J (< 0.25 × 1.2): outcome `direction_supported`, ceiling L2.

### 7.3 Registered magnitude estimates (descriptive, from the same kept quads)

Computed by the disclosure producer, never gating anything, printed beside the contrast as "registered descriptive
estimates":

1. **Ratio of phase energies, 8B to 1.7B.** Per kept quad, ρ_k = ln[((B1 + B2)/2) / ((A1 + A2)/2)]; ρ̄ = mean(ρ_k),
   s_ρ their sample standard deviation; ratio = exp(ρ̄) with interval exp(ρ̄ ± t(0.975, n − 1) × s_ρ / √n) (exact
   quantiles of §4 step 3). Recorded timing bounds are not propagated into it (stated in the wording).
2. **Per-token difference.** dbar / 512 J per output token (decode) and dbar / 2048 J per prompt token
   (prefill-p2048), with both intervals of §7.1 divided by the same constant.
3. **Gross-energy sentence.** "Phase energy is gross: it includes the machine's baseline power over the phase, and the
   8B phase lasts longer, so part of the difference is baseline power times the extra duration."

## 8. Disclosures computed beside the claims

### 8.1 Disclosures

All are computed by code from structural or non-science evidence, except the cross-window check and the two
sensitivity lines (which use the released energies by rules fixed here), and printed with the results.

- **Kept units:** beside every reported cell, floor and contrast: n_r and n_b (or the kept quads), the removed units
  with the catalog families of the codes that removed them, and their positions in the window (stage and ordinal),
  so a reader can see whether removals clustered. A unit removed by a RESTRICTED code is shown as "removed (restricted
  code)" until the release event; the disclosure producer performs that redaction when it reads `derived/exclusions.json`,
  `derived/flags.jsonl` and `derived/window_flags.json`, which stay in restricted custody until then (registration §8).
- **Attempt history and conditionality:** every attempt of every pack with its verdict, cause key, flag counts by
  family and yield status with "collected X of Y planned members" (registration §5.7), printed as "attempts of this
  pack: N (causes …)". Fixed sentence: "These numbers are conditional on a window
  that passed the registered physical-hazard checks at arm and kept at least 5 of 10 units per stratum after the
  registered exclusions; the kept units of each cell are printed beside it."
  *A hazard not read at the arm.* *Forcing problem:* since audit finding A3 (registration §9.1; the rule is in
  registration §0.15 and §4.1) the arm refuses on an unread probe only for the instrument. When the arm's probe of
  the clock, battery, thermal, contention or disk hazard returns no reading (UNMEASURED), the arm records the flag
  `<module>.arm_unmeasured` (DISCLOSE) and the window starts, because the monitor measures that hazard during the
  window. For such a window the fixed sentence would say that it passed a check that never gave a reading. *Rule:*
  for an analysed attempt that carries any `<module>.arm_unmeasured` flag, the fixed sentence is followed by a
  second one that names the modules of those flags: "At this window's arm the [clock, battery, thermal, contention,
  disk] check returned no reading and did not refuse; the monitor measured it during the window." The flag changes
  no number and removes nothing. *Worked example (synthetic):* during BETA-1's arm the contention dwell (the stretch
  in which the arm watches for competing processes, registration §4.2) could take no process snapshot, so it ran to
  its 2,700 s cap and recorded `contention.arm_unmeasured` (registration §4.1), and the window was claim-usable.
  BETA's cells print the fixed sentence followed by "At this window's arm the contention check returned no reading
  and did not refuse; the monitor measured it during the window."
- **Sensitivity line (ADOPTED AS AMENDED by the seal gate, stage 1, 2026-10-07; registration §14 Q6).** *Forcing
  problem:* thermal pressure and contention plausibly correlate with load, most of all on 8B prefill-p2048 members, so
  removing the members they touched could bias a cell's mean downward. (Battery assist, the case that first raised
  this, is no longer an exclusion; it has its own registered line below.) *Rule:* when any unit of a cell or contrast
  was removed by one of the three load-correlated codes `thermal.os_level_nonzero`,
  `thermal.powermetrics_pressure_elevated` and `contention.request_overlap`, the same estimator is recomputed over
  the units that would be kept if those three codes were ignored (a unit removed by any other code, including the
  other eight PHYSICS_IN_SPAN codes, stays removed: those describe an energy that is wrong or unmeasured, not a hazard
  that follows load), and printed beside the primary value as "sensitivity: load-correlated physics exclusions
  (thermal pressure, contention) not applied (n_r = …, n_b = …)" (for a contrast, "(n = …)"). The test is on the
  codes of each removed unit in `exclusions.json`. It never replaces the primary value, never gates anything and
  licenses no claim. *Worked example (synthetic, the §4 data):* repeat 6 removed by `thermal.os_level_nonzero`, quads
  5 and 9 by `member.admission_aborted`: primary 10.13333 J (n_r = 9, n_b = 8); the line restores repeat 6 only:
  0.2 × 10.0 + 0.8 × 10.175 = 10.14 J (n_r = 10, n_b = 8), half-width 0.11557 J. Had repeat 6 been removed by
  `clock.step_overlap`, no line is printed for that cell.
- **Battery-assist sensitivity line (REGISTERED; ruling of 2026-10-06, registration §9.2).** *Forcing problem:*
  battery assist (the battery helping the adapter, registration §6.4) is disclosed, not excluded, because excluding
  it would select members by load. A reader still needs to see whether the members it touched move the number.
  *Rule:* an **assist member** is a kept member that carries the flag `battery.assist`. The harvest gives that flag
  only when the member's measured request was assisted: at least one SMC battery-current read below 0 mA held into
  the request (any negative read; −200 mA is only the threshold the flag's report counts against), or, when the SMC
  reads did not cover the member, a negative registry current or a discharge accumulator beyond its limit in the
  request. Assist seen only before or after the request (`battery.assist_outside_request`) does not make an assist
  member. For every reported cell (§4) the same estimator is computed twice: over the kept units (the primary value),
  and over the kept units with every unit that contains an assist member removed (a quad with one assist member is
  removed whole, as in §2.2). Both are printed, side by side, as "with assisted members" and "without assisted
  members (n_r = …, n_b = …)", with the count of assist members per stratum. Neither value is chosen after the fact;
  the first is the reported cell. If removing assisted units leaves fewer than 5 units in a stratum, the second value
  is still printed, with its n and the words "below the registered minimum of 5 units", and it decides nothing.
  *Worked example (synthetic, the §4 data).* If repeat 3 (9.9 J) and quad 7 (mean 10.2 J) contain assist members, the
  second value uses n_r = 9, n_b = 9: fmean(r) = 10.01111 J, fmean(b) = 10.2 J, m = 0.2 × 10.01111 + 0.8 × 10.2 =
  10.16222 J, printed beside the primary 10.16 J.
  *GAMMA's contrasts* (adopted, registration §14 Q9): each contrast is also computed without every kept quad that
  holds an assist member, by §7.1 steps 1–4 (dbar and its metrology interval), and printed beside the primary
  estimate as "without quads holding assisted members (n = …)", with the count of such quads. It has no Holm test, no
  floor decision and no outcome; it decides nothing, and below 5 quads it carries the words "below the registered
  minimum of 5 quads". *Worked example (synthetic, the §7.1 data).* If quad 3 (d = 3.3 J) holds an 8B assist member,
  the line uses the other 8 kept quads: dbar = 2.9625 J, s_d = 0.16850, se_rep = 0.059574 = se_total (no metrology
  term for the phase metrics, §7.1 step 3); t* = 2.365, so the interval is 2.9625 ± 0.1409 = [2.8216, 3.1034] J,
  printed beside the primary 3.0 J and [2.8511, 3.1489] J. (The data are the d_k of the worked example in §7.2.)
- **Monitor cost:** the hazard monitor's own CPU time per window and the number of its probes that fell inside target
  phases (registration §0.17), and the meter reader's CPU time (registration §5.8), with the fixed sentence "The
  hazard monitor ran on efficiency cores at background priority during collection, and the whole-machine meter's
  reader at ordinary priority; their CPU share is disclosed and was not subtracted."
- **Single window:** "The units of this cell were measured in one window; the interval covers variation within that
  window, not between days or windows. The repeats and quads are modelled as independent units; that is an
  assumption (D-179 dependence caveat)."
- **Cross-window consistency check** (registered rule; never changes a number). For each model and phase: G = the mean
  over GAMMA's kept quads of that model's side mean, h_G = t(0.975, n − 1) × s(side means) / √n; F = the model's
  reported cell mean and h_F its half-width h (without B). Δ = G − F. If |Δ| ≤ √(h_G² + h_F²): "GAMMA's and the floor
  window's estimates agree within their within-window intervals (difference Δ J)." Otherwise: "GAMMA's and the floor
  window's estimates differ by Δ J, more than their within-window intervals cover; the reported intervals understate
  between-window variation, which includes different interleaving and thermal history."
- **Floor transfer:** the assumption and evidentiary limit quoted in §5, verbatim.
- **Decision interval against the floor:** for each contrast, whether the decision interval's lower end (upper end,
  for a negative estimate) is beyond the floor. If it is not: "The estimate exceeds the floor, but its decision
  interval reaches below the floor."
- **Leave-one-quad-out magnitude concern**, if raised: "Leaving out quad k moves the estimate by X J, more than a
  quarter of the floor; the direction, the floor status and the multiplicity decision are unchanged."
- **Order:** "Every quad ran 1.7B, 8B, 8B, 1.7B in that fixed order; the order was not randomized, and the p-value
  assumes the quad differences are independent."
- **Contrast interval:** the rounded t* (2.306 for 2.306004); no metrology term is added for the phase metrics
  (§7.1 step 3), and errors common to all members are carried by D and the attribution floor.
- **Battery, thermal, contention, clock:** per window, the hazard measurements at arm (each hazard whose probe
  there returned no reading is named, `<module>.arm_unmeasured`, as above), the counts of each
  physics-in-span code, the count of members with anchor status `bounded` and the largest effective bound, and the
  host's total busy CPU during requests (journaled by the monitor; `kernel_task` cannot be named by an unprivileged
  `ps`, registration §6.8). For battery assist: per window, the number of members with `battery.assist` and with
  `battery.assist_outside_request`, and of calibration captures with `calibration.capture_battery_assist`; and per
  phase (registration §6.4: before the measured request, the request, after it), the number of negative SMC reads,
  the number below −200 mA, the minimum B0AC (the battery current read from the SMC, registration §4.2) and the total
  held time below −200 mA. The discharged energies (`withheld/battery-assist.json`) are released with the other
  energies after the release event. Per window, the count of members whose current was judged on the registry
  because the SMC did not cover them (`battery.smc_unavailable`), and of #421 pairs disclosed as discharge
  (`battery.capture_pair_assist`, `calibration.capture_battery_pair_assist`).
- **Reference drift:** each window's NEG-8 screen result, allowance and corpus size (10, 11 or 12). For a corpus of 10
  or 11, also disclose that the bound was validated against the collected members and that the harvest's re-screen,
  not the stored verdict, decided the screen (registration §5.3; `derived/neg8-bound.json`, `derived/neg8-screen.json`).
  Also, from the flags and `derived/neg8-screen.json` (registration §0.12, §5.3): the realised reference counts
  (start, midpoint, end) against the planned (3, 1, 3), the bound's formula at those counts, each lost reference with
  its slot and reason (`neg8.reference_lost`), each spare measured with its slot (`member.retried`) and whether it
  succeeded, a lost midpoint (`neg8.midpoint_lost`) with the fixed sentence "The midpoint reference was lost, so drift
  inside this window that reverted by its end was not measured; the drift allowance uses the start and end references
  only", and each corpus member dropped for physics with its code (`neg8.corpus_member_dropped`, source
  `harvest_physics`). The bound's two terms (envelope and repeatability) at the realised counts are energies and are
  printed with the other energies after the release event.
- **Battery temperature across each stage** (registration §0.6; timing ruling of 2026-10-06): beside the NEG-8
  result, for each stage, its battery-thermistor readings, its rise (last reading minus first, in K) and whether
  its last three readings plateau (within 0.5 K), with every stage flagged `thermal.stage_battery_rise` (rise above
  3 K, no plateau) or `thermal.battery_temperature_unmeasured` named. The campaign runner
  (`scripts/run_campaign.py`) takes one reading before every member of a stage, the first included: after the
  member's cooldown wait is released (the first member of a stage has no wait) and before the member's sampler
  starts. A stage of N members therefore has N readings, and a one-member stage has one. The rise and the plateau
  are judged on the readings that could be read: the rise needs at least two of them, and a plateau needs three, so
  a stage with two readable readings, the second more than 3 K above the first, is flagged.
  Fixed sentence for a flagged stage: "Stage S warmed by X K without levelling off; the window's NEG-8 screen
  [passed/failed], and the reported numbers rest on that screen, not on this reading." It changes no number and
  removes nothing. A stage with no reading (the logging code is at `a434e363d`; a failed read is
  `thermal.battery_temperature_unmeasured`) reads "battery temperature not recorded for this stage".
- **G10:** its result and the redraw cycles that followed (registration §3).
- **p42:** "The 42-token prefill of the decode workload is shorter than one power record and could not be resolved;
  as registered, no p42 value is reported."
- **Attribution floor:** the §4 step 7 sentence beside each reported cell.
- **Separate windows:** the 1.7B and 8B reported cells were collected in separate windows in a fixed order; their
  difference is not a comparison (claims ladder: forced order stays below L2).
- **Dominance:** "R is a point diagnostic with no interval; 'independent' names the independent-corner component."
- **D-177:** phase attribution is reported without a measured instrument phase-accounting check.
- **Fixed prompt:** the decode contrast uses one fixed prompt; no prompt-population generality is claimed.

### 8.2 Whole-machine cross-check (registered descriptive analysis; never a claim number)

*Forcing problem.* Every claim is a processor-rail energy. Whether the rail estimate moves with the machine's own
energy from member to member is a question the rails cannot answer; the whole-machine meter of registration §5.8 can.
This section fixes, before any byte exists, exactly what is computed from it, so that nothing about it is chosen
after the numbers are seen.

*Inputs.* For each kept or removed member of each analysed attempt (the meter describes every collected member), over
its measured request (the harvest's request span; at `a434e363d` the harvest computes no phase-level figures,
registration §5.8), the harvest's restricted record `withheld/meter.json` (one file per window, one row per member)
gives three numbers, defined in registration §5.8: **ΔE_rail**, the processor-rail energy above the member's idle
baseline; **ΔE_machine**, the energy entering the machine (the meter's DC input plus the battery's discharge, −B0AC ×
B0AV) above the same baseline; and **ρ** = ΔE_rail ÷ ΔE_machine, the rails' share. The row also says whether the
battery term was available. The member's and the window's `meter.*` flags are read from the harvest's flags
(`derived/flags.jsonl`).

*What is reported, per pack and model:*

1. per member: ΔE_rail, ΔE_machine and ρ;
2. per model: the median of ρ, its minimum and maximum, and its interquartile range (the 25th and 75th percentiles,
   linear interpolation between order statistics, as `km003c_parse.percentile`);
3. **hard plausibility band:** a member window is plausible when 0 < ρ ≤ 1 and ΔE_machine − ΔE_rail ≥ 0 (the rails
   are part of the machine, so their extra energy can be neither negative nor larger than the machine's). Every member
   window outside it is listed individually with the meter flags that apply to it (its own
   `meter.battery_activity`, if it carries one, and the `meter.*` flags of its window); it is reported, never
   removed;
4. **within-model spread:** (max ρ − min ρ) ÷ median ρ over the model's plausible member windows, reported; a spread
   of at most 0.2 is described as "consistent". It is reported only and excludes nothing;
5. **central band:** set from the first clean window. A window is clean when it carries no window-level meter flag
   and none of its members carries `meter.battery_activity`. Every `meter.*` code but that one is written for the
   window as a whole (`meter.absent`, `meter.drops_excess`, `meter.duplicates`, `meter.clock_fit_residual`,
   `meter.pdtr_gain_out_of_band`, `meter.vbus_out_of_contract`, `meter.supervision_fault`); `meter.battery_activity`
   is the one written per member, when a B0AC read inside the member's measured request is not zero. The band is
   the first clean analysed window's per-model minimum-to-maximum range of ρ over its plausible member windows. It
   is disclosed with that window's identifier before any later window is described against it.
   Later windows are described against it ("k of n member windows inside the first clean window's band"), never
   filtered by it. If no window is clean, no central band is set and the line says so.

*Worked example (synthetic).* A model's ten repeats give ρ = 0.78, 0.80, 0.81, 0.79, 0.82, 0.80, 0.77, 0.81, 0.80,
0.83. Median 0.80; range 0.77–0.83; interquartile range 0.7925–0.81; all inside the hard band; spread
(0.83 − 0.77) ÷ 0.80 = 0.075, at most 0.2, so "consistent". A member window with ΔE_machine = 600 J and
ΔE_rail = 640 J has ρ = 1.07: outside the hard band, listed with the meter flags that apply to it (for example its
own `meter.battery_activity`), and kept in every claim it feeds.

*What it never does.* It never refuses a window, never excludes a member, never enters a claim-bearing number, never
replaces the rail estimate, and is never pooled into a cell. Its energies are restricted until the release event,
like every other energy. The boundary is stated with it every time it is printed: "whole-machine DC input plus the
battery term, measured at the USB-C input; the adapter's AC-to-DC loss is not included."

## 9. What is printed, and from which artifact

Under the current D-174 fallback no row below has a placement; each becomes printable only through the placement
ruling of registration §14 Q4. Site ids are the proposed `CP-X…` sites of
`docs/contracts/paper_comparison_placements.md`.

| Printed quantity | Artifact (schema) | Field | Proposed site | Status now |
|---|---|---|---|---|
| Models, workload, L = 2048 | selection record; prompt pin; panel | `selected_prefill_tokens`; pinned identities | CP-X01-identity, CP-X01-length | PROPOSED_STOP_FILL |
| Reported energy: mean, interval, J/token, kept units (4 cells) | `joulewise.paper_reported_energy_projection.v1` | `mean_j`, `lower_j`, `upper_j`, `per_token.j_per_token`, `n_bundles`, `interval.n_r`, `interval.n_b` | CP-X05-* | RETIRED_FALLBACK (needs a ruling) |
| Attribution floor beside each cell | projection binding | `binding.attribution_floor_j` | CP-X05-* | RETIRED_FALLBACK |
| Floors (4 model/phase cells) | `joulewise.detection_floor_artifact.v2` | `floor_gate_j`, n and component census | CP-X04-* | PROPOSED_STOP_FILL |
| Dominance ratios with numerators and denominators; branch sentence; subtitle | `joulewise.d165_dominance_closeout.v1` | 8 R, 4 R_cm, their floors, `branch`, licensing flags | CP-X02-*, CP-X03-* | PROPOSED_STOP_FILL |
| Contrast tables (decode, prefill) | `joulewise.claim_verdicts.v1` + finalized manifest | `estimator`, `deterministic_bounds.decision_interval`, `floor`, `multiplicity`, `claim_evaluation`, kept quads | CP-X06-table, CP-X07-table | PROPOSED_STOP_FILL |
| Ratio and per-token difference (§7.3) | disclosure producer output | registered fields | `FILL[DISCLOSURE-SITES]` | not proposed yet |
| Verdict sentences | `joulewise.claim_verdicts.v1` | `claim_evaluation.outcome`, `direction`, `claim_level_ceiling` | CP-X08-* | PROPOSED_STOP_FILL |
| Disclosures of §8 | harvest records, exclusions, disclosure producer | counts, verdicts, registered sentences | `FILL[DISCLOSURE-SITES]` | not proposed yet |

Every printed number is `MEASURED` or `DERIVE`; none is recalculated from prose.

## 10. Analysis-plan rows (`docs/contracts/analysis_plans.md` fields)

| Field | Decode contrast | Prefill-p2048 contrast | Reported cells (each) |
|---|---|---|---|
| Plan id / consumer | `B5-GAMMA-DECODE` / phase-energy paper | `B5-GAMMA-PREFILL-P2048` | `B5-REPORTED-<model>-<phase>` |
| family_id, role | `d117-gamma-decode-prefill-p2048-primary-holm-v5`, primary | same, primary | none (L1, no inference across cells) |
| Selection scope | decode, Qwen3 1.7B vs 8B, prompt 0, forced 512 | prefill at 2048 tokens, same pair | one model, one phase, its kept units |
| Multiplicity | Holm, m = 2, α = 0.05 | same | none |
| Metric, window class | gross `phase_energy_j.decode`, phase window | gross `phase_energy_j.prefill`, phase window | gross phase energy, phase window |
| Unit, dependence | quad side-mean difference, kept quads (≥ 5 of 10), modelled independent | same | kept repeats + kept quads (≥ 5 of 10 each), modelled independent |
| Estimator | §7.1 | §7.1 | §4 |
| Inclusion, exclusions | the analysed attempt's `exclusions.json` under the sealed catalog | same | same |
| Order, blocking, covariates | fixed unrandomized A/B/B/A interleaving cancels linear drift; no covariates | same | fixed member order |
| Floor gate | `floor_gate_j`, side-wise max (§5) | same | attribution floor printed beside, not a gate |
| n sizing, top-up | planned 10; analysed = kept quads, at least 5; no replacement, no top-up | same | planned 10 + 10; analysed = kept, at least 5 per stratum |
| Denominator | none for the contrast; 512 output tokens for the §7.3 per-token difference | none; 2048 prompt tokens | runtime-observed tokens |
| Holdout | not applicable | not applicable | not applicable |
| Ceiling; forbidden upgrade | L2 per §7.2; no claim about other prompts, lengths, models or machines | L2; same | L1; no model comparison from these cells |
| Disqualifiers | §7.2 outcomes and sensitivity codes; a GAMMA attempt carrying `neg8.midpoint_lost` is not claim-usable and never analysed (§2.4) | same | D-179 refusal codes |
| Linked manifests | the finalized manifest, bundle hashes and the exclusions digest | same | projection bindings and the exclusions digest |

## 11. Analysis code (lane L9), written blind

| Need | State at this writing | FILL |
|---|---|---|
| Consume `exclusions.json` (`joulewise/analysis_engine/inputs.py`): kept units per cell, removed units excluded everywhere; the two checks of §2.2 (its `catalog_sha256` against the sealed catalog's digest in the seal record, its recorded harvest commit against the harvest addendum) | Absent | `EXCLUSIONS-CONSUMER` |
| D-179 issuer implementing §4 (stratified mean, variance, df, B, per-token over kept units; n_r, n_b in the record), projecting each cell independently and preserving the whole-window allowance allocation, reading the re-screened allowance when the harvest re-screened (§4 step 4), reading each member's first-kind bound from its summary as re-derived under the window's operative fiducial bound (§4 step 4), computing the attribution floor from its own per-member rows (§4 step 7) and refusing a binding whose `attribution_floor_j` differs from that maximum (the existing refusal `paper_reported_energy_binding_mismatch`), with a synthetic test on a cell that has one removed member | Absent ("No production dispatch exists", `joulewise/paper_reported_energy.py`). The projection function that exists, `_project_cell`, takes exactly 50 member rows and the quantile for 9 degrees of freedom, and checks only that `attribution_floor_j` is a finite number that is not negative; the kept-units arithmetic of §4 and the check of the floor against the computed maximum belong to the issuer | `REPORTED-ENERGY-ISSUER` |
| Floor extraction over kept units with g(n) (`joulewise/floor_extraction.py`) | The extractor assumes full n | `FLOOR-EXTRACTION-KEPT-UNITS` |
| Claim gate over kept quads: no `fixed_n_plan_incomplete` for removed quads; leave-one-quad-out over kept quads; finalization binds the exclusions digest | Absent | `GAMMA-MANIFEST-EXCLUSIONS-BINDING` |
| **Lane L9-NEG8: one NEG-8 survivor logic for every claim consumer** (registration §0.12, §9.1, §14 Q13). It runs after the seal and before any claim, as a gated fix to code that does not run during collection (registration §11 item 1 (ii)), pinned before the release event (§11 item 4), with one design round by Sol and Fable before code. It must: (a) use one strict-invalid predicate in the verdict writer, the replay and the harvest, moving the replay and the harvest to the writer's predicate (structural check, custody triangle, config binding) plus full strict validation, so all three drop exactly the same references, and leaving the writer's bytes unchanged (Fable cold pass 4 N-3); (b) pass the harvest archive through floor extraction (`floor_extraction.extract_cells`), the mint (`scripts/mint_floor_artifact.py`, `mint_floor_artifact_generalized.py`) and `scripts/extract_detection_floors.py`, so a block-5 floor cell gets the allowance the harvest's screen left standing (Sol re-verification R2; cold pass 4 D1); (c) make claim validation authenticate the harvest's survivor screen before the stored-failure veto, so a window whose stored screen failed and whose survivor re-screen passed gets the re-screened allowance, while the membership, provenance and physics checks stay independent (Sol R3); (d) have every claim consumer read the allowance from `derived/neg8-allowance.json` (registration §0.12), never from the stored bracket. Each with a test on a synthetic HAZARD root (the code's name for a runs root of a block-5 window, that is, a directory under which the window's member bundles are written, recognised by the launch-lineage locator file the driver publishes into it) with and without its archive. | At the int5 head `fe28e5a0c`, and unchanged at `9b0c680ed`: the record, its consumer and `analyze-claims --neg8-harvest-archive` exist; (b), (c) and the shared predicate (a) do not. Until the lane lands, every block-5 floor cell refuses (`whole_window_drift_allowance_unrecorded`) and a contrast resting on a recorded survivor re-screen refuses (`whole_window_neg8_verdict_failed`): a floor or contrast computed from HAZARD roots whose window has a recorded re-screen has no allowance and is not claimable. Both refuse; neither prints a wrong number. | `L9-NEG8` |
| Claim gate reads GAMMA's flags: `neg8.midpoint_lost` on the analysed attempt stops the analysis (the exclusion function should have made the attempt not claim-usable, §2.4) | Absent | (part of L9) |
| `_v5` final pinset and v2 input manifest for the mint; two-producer aggregate floor binding in the claim gate (memo 4.1; in this row and the three below, "memo" is the lane memo of 2026-10-05 that holds the block-4 pre-mortem and the analysis-path dry run, `/Users/edr/night-archive/ia-0a40/MEMO.md`, registration §16, cited by its section number). The aggregate floor has two producers, the ALPHA and BETA floor packs, and each pack carries its own `calibration_plan.json` | The issued pinset and input manifest: absent. They are written from each floor window's runs root, extraction report (the output of step 4 of §3.1) and bracket binding and from the calibration ledger, so they cannot exist before collection; the program that writes them is present at `9b0c680ed` (`scripts/emit_floor_mint_pinset.py`, commit `8c6dd2c2b`). The two-producer binding: present at `9b0c680ed` (commit `2d3329e0d`: the claim gate's input loader, `joulewise/analysis_engine/inputs.py`, binds each cell of the aggregate floor to the `calibration_plan.json` of the pack that produced it; before that commit it could bind one such file only, so a floor made from two packs could not be bound). Revision 10 wrote "Absent" for the whole row | `V5-FINAL-PINSET`, `V5-V2-INPUT-MANIFEST` |
| Mint-to-close-out adapter; dominance sidecar wiring (memo 4.3) | The adapter: absent. The sidecar wiring: present at `9b0c680ed` (commit `8c6dd2c2b`): the mint writes the sidecar (`--d165-replay-out`), and finalization takes it (`--dominance-replay-sidecar`) and copies it unchanged into its custody root. Revision 10 wrote "Absent" for the whole row | `MINT-TO-CLOSEOUT-ADAPTER` |
| Bracket replay in finalization with the ledger-cutoff baseline (memo 3.3). Finalization evaluates the calibration bracket again from the ledger (the replay). That evaluation refuses (`calibration_ledger_baseline_missing`) unless the ledger snapshot it is given carries, as its baseline, the acceptance's cutoff: the ledger sequence and head digest up to which the acceptance was derived (registration §0.11) | Present at `9b0c680ed`: `joulewise/analysis_manifest_v3.py` loads the snapshot with the cutoff's sequence and head digest as its baseline (commit `f8ad16514`). Revision 10 still wrote "Defect known" here | none |
| Claim gate re-runs `analyze_claims` and requires byte equality; the `evidence_class` read is fixed (memo 3.7) | Defect known | (part of L9) |
| Claim verdicts to results-fill input | Absent | `CLAIM-VERDICT-TO-FILL-ADAPTER` |
| Disclosure producer for §7.3 and §8, including the battery-assist line (§8.1), the load-correlated physics sensitivity line (§8.1), the whole-machine cross-check (§8.2, reading `withheld/meter.json`), the reference-drift line's survivor counts, lost references, spares and lost midpoint (§8.1), the second sentence for a hazard not read at the arm (§8.1), the redaction of a unit removed by a RESTRICTED code (§8.1), the attribution-floor sentence beside each reported cell (§4 step 7; no program prints the attribution floor today), and the step-4 p42 exit rule | Absent | `DISCLOSURE-PRODUCER` |

Each is written and merged before the release event by seats that have read no claim-window energy, against this
plan's text, tested on synthetic fixtures (including: one removed repeat gives n_r = 9, the stratified mean and t with
8 degrees of freedom; one removed quad member drops its quad; six of ten quads removed gives `cell.below_minimum` and five removed does not;
floors at n = 8 use g = 1.134 and floors at n = 5 use g = 1.5; an 8B-tagged bundle under a 1.7B cell is refused), pinned by an addendum to the seal
record, and exercised by the blind dry run (§3.2) before the release.

## 12. What the analysis never does

- Use a member or unit the exclusion function removed; exclude, replace, reweight or re-collect anything else after
  collection; compute a cell over fewer than 5 kept units in a stratum; pool members across attempts or windows; top
  up a cell from another attempt; analyse a superseded window's energies or any attempt other than a pack's first
  claim-usable one.
- Weight a reduced cell by its kept member counts instead of the fixed 0.2 / 0.8 strata (§4 step 1).
- Use the pooled s/√20 interval, a mean of per-member ratios, configured token counts, the √(1 + 1/n) prediction term
  as a reported-cell interval, or any floor other than the minted one.
- Treat the ALPHA-versus-BETA difference of reported means as a comparison.
- Test one-sided, change α, m, the registered direction or the contrast set, or add a contrast.
- Read an energy before the release event, or let any energy value inform a scheduling decision.
- Print the sensitivity line as the result, or report any analysis not registered here except as clearly labelled
  exploratory.

## 13. FILLs specific to this plan

Still open after the seal: `B5-ANALYSIS-CUSTODY-ROOT`, `B5-BLIND-DRY-RUN-RECORD`, `EXCLUSIONS-CONSUMER`, `L9-NEG8`,
`REPORTED-ENERGY-ISSUER`, `FLOOR-EXTRACTION-KEPT-UNITS`, `GAMMA-MANIFEST-EXCLUSIONS-BINDING`, `V5-FINAL-PINSET`,
`V5-V2-INPUT-MANIFEST`, `MINT-TO-CLOSEOUT-ADAPTER`, `CLAIM-VERDICT-TO-FILL-ADAPTER`, `DISCLOSURE-PRODUCER`,
`DISCLOSURE-SITES`. Each names code, a record or a ruling that does not exist yet. Where each is filled: the seal
commit fixes this file's bytes and the seal record pins their SHA-256, so a value that becomes known after the seal
goes into an addendum to the seal record (registration §12), not into this file. If this file is nevertheless
changed to carry one, the same addendum restates this file's SHA-256: no program reads this file, so nothing else
would bind the changed bytes.

`ATTRIBUTION-FLOOR-BINDING`, shared with the registration, is closed: revision 12 filled it with a formula and bound
no number (§4 step 7; registration §14 Q5).

`B5-FINAL-HASHES`, also shared with the registration, marks a digest and not a missing rule. Where the mark stands,
the SHA-256 of the named file's bytes at the final head of the code is written in its place before the seal commit
is made. In this plan it stands in three places: the two `extraction_spec.json` file digests of §4 and the digest of
GAMMA's manifest in §7.1. `REPORTED-ENERGY-REGISTRATION-DIGESTS` was filled in revision 4 (§4). Revision 2's
`ED-PREDICATE` (replaced by the contention member rule) and `P42-S1-STRUCTURAL-CHECK` (now the s1-structural
diagnostic at ALPHA-1's harvest) are withdrawn.

The open questions are registration §14. Of the three that bore directly on this plan, Q4 (placement) is still
open; Q5 (the attribution floor) was closed by the orchestrator's ruling of 2026-10-07, and Q6 (the sensitivity
line) by the seal gate at stage 1 (§8.1).

## 14. Changes from earlier revisions

**Revision 3 (2026-10-05), from revision 2.**

- §1 item 2: "the attempt whose verdict is PASS" became "the first claim-usable attempt".
- §2.2: "no member is excluded after collection" became the exclusion function's output, the unit rule and the
  8-of-10 minimum.
- §3: step 3 now fixes the kept units; the L10-B rehearsal is optional and non-blocking; the L10-C rehearsal is
  replaced by the blind dry run, which now covers the exclusions consumer.
- §4: the stratified estimator over kept units, exact t for 7 and 8 degrees of freedom, stratified B and per-token
  value, and a second worked example.
- §5: floors over kept units with g(n), with worked examples at n = 9 and n = 8.
- §7: contrasts over at least 8 kept quads; leave-one-quad-out over kept quads; a worked example at n = 9.
- §8: kept-unit and attempt disclosures, the proposed sensitivity line, the monitor's cost, G10, and the hazard
  measurements; the environmental-diagnostic counts and waiver wording of revision 2 are replaced by the contention
  member rule and its counts.
- §11: the L9 code list, written blind, with the dry run before release.

**Revision 4 (2026-10-06), synchronizing with the integrated code at `f8164893`.** No estimator, threshold or effect
used by this plan changed.

- §4: the two reported-energy registration digests are filled in from the floor packs' extraction specs.
- §8: for a NEG-8 corpus of 10 or 11 members, the reference-drift disclosure says the harvest's re-screen against the
  collected-subset bound decided the screen (registration §5.3).
- The registration now removes, through the exclusion function, each member the whole-window verdict fails
  (`member.whole_window_member_failure`, registration §6.3). This plan reads exclusions only from `exclusions.json`
  (§2.2), so it needs no other change.
- §8: a battery-temperature line beside the NEG-8 result, from the diagnostic the timing ruling of 2026-10-06 added
  (`/Users/edr/night-archive/gate-prune/timing/RULING_fable_cooldown_2026-10-06.md`; registration §0.6). It is
  disclosure only. The ruling's other changes (cooldown rule, 576-record idle baseline, 60 s settles) change how
  members are collected, not how this plan computes from them.

**Revision 5 (2026-10-06, the REG lane of gate-prune round 3).** No estimator, threshold or exclusion used by §4–§7
changed.

- §8 is split into §8.1 (the disclosures) and §8.2 (the whole-machine cross-check).
- §8.1: the battery-assist sensitivity line is registered, from the orchestrator's ruling of 2026-10-06
  (`/Users/edr/night-archive/wallmeter-probe/verify/RULING_battery_assist_2026-10-06.md`, registration §9.2): every
  reported cell printed with and without units holding an assisted member, neither chosen after the fact. Whether
  GAMMA's contrasts get it is registration §14 Q9. The physics-in-span sensitivity line no longer cites battery
  assist, which is disclosed and not an exclusion.
- §8.1: the battery disclosure gains the per-phase assist counts and the SMC fallback count; `kernel_task`'s share,
  which an unprivileged `ps` cannot measure, is replaced by the host's total busy CPU; the monitor-cost line adds the
  meter reader; the battery-temperature line no longer waits for its logging code (at `b9d02700a`); the attempt
  history adds each attempt's yield.
- §8.2: the pre-registered descriptive analysis of the whole-machine meter (registration §5.8): ΔE_rail, ΔE_machine
  and ρ per member and window; per model the median, range and interquartile range of ρ; the hard band
  0 < ρ ≤ 1 with ΔE_machine − ΔE_rail ≥ 0; the within-model spread, reported only; the central band from the first
  clean window, disclosed with its identifier. It never gates or enters a number.
- §11: the disclosure producer's scope grows by the two items above.

**Revision 6 (2026-10-07, the REG sync to the frozen head `a434e363d`).** No estimator, threshold or exclusion used by
§4–§7 changed.

- §8.1: an assist member is one carrying `battery.assist`, which the code gives for **any** negative SMC read in the
  measured request (−200 mA is only the report's threshold), not "at least one read below −200 mA"; the per-phase
  battery disclosure uses the code's phases (before the request, the request, after it) and adds the counts of
  `battery.assist_outside_request`, capture assist and the discharge-only #421 pairs.
- §8.1: the battery-assist line also covers GAMMA's contrasts (registration §14 Q9, adopted by the orchestrator's
  ruling of 2026-10-06), with a worked example on the §7.2 data.
- §8.2 and §11: the harvest's meter record is one file per window, `withheld/meter.json`, over each member's measured
  request only; the per-phase figures revision 5 named are not produced.
- §7.1: GAMMA's analysis manifest is unchanged by lane L10, which is in the frozen head.

**Revision 7 (2026-10-07, the REG sync to the audit fixes and the NEG-8 survivors ruling, int5 head `d3c107f2f`).** No
estimator, threshold or member exclusion used by §4–§7 changed.

- §2.4 (new): `neg8.midpoint_lost`, which the catalog keeps DISCLOSE, is claim-excluding for GAMMA's two primary
  contrasts, by the NEG-8 cold ruling of 2026-10-07 (decision 2): when GAMMA's analysed attempt carries it, the
  contrasts are computed and printed as "not a claim", with no L2 ceiling, until the block's midpoint record supports
  an erratum. A floor window carrying it keeps its L1 cells, with the flag disclosed. Whether such a GAMMA attempt
  should be re-armed is registration §14 Q11.
- §7.2: the L2 ceiling gains that condition. §10 and §11: the disqualifier and the claim-gate need.
- §8.1: the reference-drift disclosure adds the realised reference counts, lost references with their reasons, spares
  measured, a lost midpoint with its fixed sentence, and corpus members dropped for physics (registration §0.12, §5.3).
- Two audit fixes need no text here: the exclusion function now resolves member flags scoped by bundle id
  (registration §0.16), and a malformed flag line now carries a conservative exclusion instead of blocking the
  release event (registration §6.2). This plan reads exclusions only from `exclusions.json` (§2.2).

**Revision 8 (2026-10-07, the REG final pass to the candidate H_claim `43ac12d0c`).** No estimator, threshold or
member exclusion used by §4–§7 changed.

- §2.4: orchestrator ruling Q11 (registration §14 Q11, closed). A GAMMA attempt carrying `neg8.midpoint_lost` is not
  claim-usable (window reason `neg8.midpoint_lost_primary`), so GAMMA is re-armed and such an attempt is never
  analysed. Revision 7's "computed and printed as not a claim" path is withdrawn; the claim gate instead stops if it
  ever finds the flag on GAMMA's analysed attempt. The worked example follows the new rule.
- §7.2: the L2 condition on `neg8.midpoint_lost` is withdrawn, because no analysed GAMMA attempt can carry it. §10 and
  §11 follow.
- §4 step 4 and §11: after a harvest re-screen, the issuer reads the drift allowance from
  `withheld/neg8-rescreen-bracket.json`, never the verdict row's (Fable cold pass 2, note N4).

**Revision 9 (2026-10-07, the REG sync to the int5 head `fe28e5a0c`).** No estimator, threshold or member exclusion
used by §4–§7 changed.

- §4 step 4 (and D in §7.1): the drift allowance is the one `derived/neg8-allowance.json` names, read through
  `whole_window.harvest_neg8_allowance_bracket`; with no authenticated record there is no allowance and the cell
  refuses (Sol delta audit A1, fixed in the harvest at `6fd863645`).
- §3.1 steps 4 and 9: floor extraction and the claim gate are given the window's harvest archive; the claim gate's
  argument exists (`--neg8-harvest-archive`), floor extraction's comes with lane L9-NEG8.
- §11: lane L9-NEG8 (registration §9.1, §14 Q13): one strict-invalid predicate, the archive through floor extraction
  and the mint, survivor-screen authentication ahead of the stored-failure veto, and every claim consumer reading the
  allowance record. Until it lands, no block-5 floor and no contrast resting on a recorded survivor re-screen is
  claimable; both refuse, in the safe direction.
- §2.4: the floors' relation to the allowance is stated exactly (the value does not use it; the extraction records it
  and refuses without it).

**Revision 10 (2026-10-07, the REG preparation pass at the int5 head `9b0c680ed`).** No estimator, threshold or
exclusion used by §4–§7 changed.

- §8.1: a window whose arm could not read one of the clock, battery, thermal, contention or disk hazards starts with
  the flag `<module>.arm_unmeasured` (registration §0.15, §4.1; audit finding A3, in the code since revision 7). The
  fixed conditionality sentence says the window "passed the registered physical-hazard checks at arm", which is not
  true of a check that gave no reading, so a second fixed sentence now follows it for such a window and names the
  hazards. The hazards line names them too. Found by checking the integration's list of required text changes
  against this plan (registration, revision 10 item 2); the seal gate adopts or rewords the sentence.
- §11: the disclosure producer's scope grows by that sentence. The state of lane L9-NEG8 is unchanged at `9b0c680ed`:
  nothing merged since `fe28e5a0c` touches floor extraction, the mint or the claim validator.
- The registration's revision 10 restates the census's rule for JavaScript runtimes from the merged code
  (registration §4.5). The census decides whether a window starts or stops; it enters no computation here.
- Every line above §6's sentence on R_cm keeps its line number, because a test in the integration tree names that
  sentence by its line (registration §13, revision 10 sync record).

**Revision 11 (2026-10-07, corrections of fact after the comparison of the documents with the code).** Every statement
of the registration, this plan and the flag catalog that can be checked against the code was compared with the code
at the int5 head `9b0c680ed`: 2,011 statements checked, 73 mismatches of fact confirmed by a second reader, and 70
further reports of sentences that are hard to read correctly or terms used without being built (registration,
"What changed in revision 11"). This revision corrects this plan's text to what the code does. No estimator,
threshold or exclusion used by §4–§7 changed, and no code changed.

- §1 item 2: the rule that a pack is never armed again after a claim-usable attempt is applied by the lead session
  that arms the next window, from the harvest verdicts; no program enforces it (registration §7.2). At `9b0c680ed`
  only tests call the function that picks a pack's first claim-usable attempt, so the analysis code of §11 must
  apply it.
- §2.4: "the only reference inside the window" is narrowed to the only NEG-8 reference between the start and end
  triplets that the spread reads; GAMMA's two diagnostic references are inside the window too and are not read.
- §3.1: the close-out (step 6) runs after finalization (step 8); the step numbers are kept and the order is stated.
- §4, §5, §7.1: the two `extraction_spec.json` digests and the three phrases "re-tied at seal" are marked
  with the FILL mark `B5-FINAL-HASHES`. The two digests are stale and are not recomputed here; the final pass recomputes them at
  the final head.
- §7.2: of the three reason codes that can block L2 after the sensitivity lines, `loo_verdict_influential` can
  arise in block 5, because the leave-one-quad-out line runs; the two randomization codes cannot. For GAMMA's
  kind of manifest a top-up on any entry demotes both contrasts, not only the one it touches.
- §8.2: seven meter codes are written for the window, not six (`meter.supervision_fault`, written by the driver, is
  the seventh).
- §11: three rows are brought to the code at `9b0c680ed`. The bracket replay with the ledger-cutoff baseline is
  present. The two-producer floor binding and the wiring of the dominance sidecar are present; the issued pinset,
  the input manifest and the mint-to-close-out adapter are still listed as absent.
- §14: "the §7.1 data" is corrected to the §7.2 worked example; the same phrase in §8.1 stands inside a passage
  that is not touched (below).
- Terms: each of the terms the readers reported (U51 to U60 of the comparison's list) is built before its first
  use or glossed at it, except two terms that occur only in §7.1 step 3.
- Not touched, waiting for the seal gate's judge: §7.1 step 3, the §7.2 worked example and the two §8.1 passages on
  the metrology term (question SG-13: the code adds no metrology term for the two phase metrics, so se_met is 0
  there and the registered interval would narrow); and the §8.1 sentence on a unit removed by a RESTRICTED code
  (question SG-12).
- Every line above §6's sentence on R_cm keeps its line number, as in revision 10. Corrections above it were made
  inside existing lines, so 23 of those lines are longer than the file's usual width.

**Revision 12 (2026-10-07, the text of the seal).** Three sources changed this plan. First, stage 1 of the seal
gate (the gate ran in two stages, registration §12): the gate's judge read the registration, this plan and the flag catalog as they stood at revision 9 and ordered
48 changes of text, numbered T-1 to T-48, and one change to the catalog, C-1 (ruling file
`/Users/edr/night-archive/gate-prune/seal-gate/RULING_STAGE1.md`; its rulings are cited below by their names in that
file, SG-1 to SG-13). The 22 changes that fall in this plan are applied word for word. One of them, T-24 in §2.4,
met a passage that revision 11 had already corrected; the judge's words are written there, followed by the facts
revision 11 had added. Second, the orchestrator's ruling of 2026-10-07 on registration §14 Q5, the attribution floor
(`/Users/edr/night-archive/gate-prune/wave-1007b/q5-attribution-floor/RULING.md`). Third, the procedure by which the
seal is committed (registration §11, §12). Rules that bear on numbers changed in three places: the minimum of kept
units and the metrology term of the contrasts, both by the judge's rulings, and the attribution floor, with the
summaries from which the first kind of B is read, by the orchestrator's ruling.

- **The minimum of kept units per stratum is 5, not 8** (SG-1; T-7 to T-18; in the catalog,
  `rules.cell_unit_minimum`, C-1). It is changed in the opening summary, §2.2, §7.1, §8.1 (the fixed sentence, which
  now also says that the kept units are printed beside each cell, and the two battery-assist lines), §10, §11 and
  §12. The judge's ground: with 5 to 9 kept units the registered estimators still give a correct number with a wider
  interval, and a wider interval is not a reason to discard a window; below 5 the floor guard g(n) of §5 is
  undefined, so a floor cell has no floor. §4 step 3 now prints the quantiles for 6, 5 and 4 degrees of freedom, and
  §5 the guard for n = 7, 6 and 5.
- **No metrology term for the two phase metrics** (SG-13; T-45 to T-48): §7.1 step 3, the §7.2 worked example, the
  worked example of GAMMA's battery-assist line in §8.1 and the "Contrast interval" disclosure of §8.1. The engine
  reads a random-error variance only for the metric `energy_request_j`, so for both contrasts se_total = se_rep.
  The two worked intervals narrow, from [2.8325, 3.1675] J to [2.8511, 3.1489] J and from [2.7987, 3.1263] J to
  [2.8216, 3.1034] J; no worked outcome changes. Revision 11 had left these passages for this ruling.
- **§8.1, the sensitivity line is adopted as amended** (SG-4; T-35, T-38): it ignores three load-correlated codes,
  not the whole PHYSICS_IN_SPAN family, and it has a worked example.
- **§8.1, a unit removed by a RESTRICTED code** (SG-12; T-33): the disclosure producer performs the redaction, and
  the three `derived/` files that name such a code stay in restricted custody until the release event.
- **§2.4, a lost midpoint** (SG-5; T-24, T-25): the midpoint is the only NEG-8 reference inside the window, and the
  scope paragraph now says why a lost midpoint is only disclosed on ALPHA and BETA although it can understate their
  bound B. The paragraph "What would change it" is rewritten to agree with registration §0.12 as the judge amended
  it (T-22, an item of the registration): an erratum can relax the rule only for a later block.
- **§2.2** (SG-11; T-44): the analysis checks the catalog digest and the harvest commit that `exclusions.json`
  records.
- **§4 steps 4 and 7, the attribution floor** (the orchestrator's ruling on Q5): a formula is registered and no
  number is bound. Step 4 now states the first kind of recorded timing bound as the code computes it: revisions up
  to 11 named only the shift of the whole trace, and the bound also displaces each phase edge by the edge bound,
  which is the larger part. Step 7 defines the attribution floor of a cell as the largest of that bound over the
  cell's kept members. Its earlier sentence, that the interval "does not include" the bound, was false: the average
  of the same bound is inside the interval, as part of B. Step 4 also says which summaries the bound is read from,
  those re-derived under the window's operative fiducial bound, which earlier revisions left unsaid; that choice
  sets the size of the first kind of B. §11's issuer row and §13 follow.
- **The status line, §13 and the digests.** The status line says how this file is sealed. §13 says where a FILL
  that is still open is filled after the seal. The FILL mark `B5-FINAL-HASHES` now stands in its bracketed form only
  where a digest is written in its place (§4 twice, §7.1 once), so that filling it is the substitution of one value;
  where the mark is only spoken of (§4's introduction, §13, and revision 11's entry above) it is named without the
  brackets. The two `extraction_spec.json` digests that revisions 4 to 11 printed are kept, labelled as the digests
  at `f8164893`.
- **Sentences this revision's writer added beside the judge's words.** Each follows from a ruling above and changes
  no rule: the sentences after T-44 that say which §11 is meant and what its addendum names (§2.2); the terms of
  §7.1 step 3, built after the judge's text; the code's tabulated and rounded t values for 6, 5 and 4 degrees of
  freedom (§5; §7.1 step 4); the sentence after T-47 that says where its data come from (§8.1); the guard at n = 5
  among §11's fixtures; and additions to three rows of §11's table (the two checks of §2.2, the attribution floor in
  the issuer, the redaction and the attribution-floor sentence in the disclosure producer).
- Every line above §6's sentence on R_cm keeps its line number, as in revisions 10 and 11. The judge's text adds
  seven lines above it (T-44 one, T-24 one, T-25 three, T-8 one, T-9 one); each is made up by joining two
  neighbouring lines of older text into one (in §2.2, §2.4 at two places, §4 step 2 and §5), and the paragraph
  "What would change it" of §2.4 is two lines shorter. The judge's lines keep the line breaks of the ruling file.
