# Block 5 lean analysis specification (SPEC v1)

**Status.** Lead-finalized 2026-11-06 on branch `lane/2026-11-06-b5-lean` from a Sol 6.1 xhigh extraction draft (local run, events audited clean). The draft was checked by the lead against the plan, the L9 cold-judge rulings and the code; the lead's changes are: §0 (scope tiers and deliverables), the authority list below, the tightened kernel permissions of §2 and §5 (floors, the D-124 sweep and split, and the R_cm replay are now implemented from this text, not called), the exact corner functional in §3.2, and §6 Q1/Q6 resolved by the L9 rulings J5/J6.

## 0. Scope tiers and deliverables (lead)

**Tier 1 (required).** Everything a reader of the paper gets a number from: §3.1 reported cells (incl. p42 refusal, per-token, attribution floor); §3.2 floors (both forms, both target phases, both floor packs; p42 floor components refused); §3.3 aggregate floor and per-contrast floor gate; §3.4 eight R and four R_cm with branch; §3.5 both contrasts with Holm, outcome, ceiling and the family LOO; §3.6 claim-side bound copy (D-189) and the §7.3 descriptive magnitudes; §3.7 numeric disclosure lines (battery-assist cells/contrasts, load-correlated cells/contrasts, cross-window, decision-vs-floor, LOO magnitude, floor composition, attribution floor).

**Tier 2 (after Tier 1 passes its tests).** §3.7 "production step-11 supplementary calibration sensitivity" (b_sens, registered by trigger-erratum E3 item 14 as read by L9 ruling J6) and §3.8 whole-machine cross-check (absent on S10; unit tests only).

**Out of scope.** Custody, authentication, digests of outputs, caches, deadlines, strict bundle validation (step 1), the ordinary step-2 re-reduction, re-evaluation of the calibration bracket and the NEG-8 bracket from the ledger/reference traces (the lean reads the harvest-recorded values; production checks them equal, §1.5), structural disclosure text. The lean pipeline is a numerical pipeline: it trusts the harvest's exclusions and recorded brackets and reproduces every reported number from them.

**Deliverables.** `joulewise/b5_lean/` (package), `scripts/run_b5_lean.py` (CLI writing one `results.json`, schema §4), `tests/b5_lean/` (unit tests incl. every worked example of PLAN §4-§8), all standard library plus the allowed kernels of §2.

**Authorities in addition to PLAN/REG** (all at this commit): `docs/process_traces/2026-10-block5/l9-rulings/RULING.md` (the Fable 5.1 cold-judge ruling of 2026-10-12 on lane L9; cited as RULING Jn), in particular **J5** (the floor a contrast is tested against is the guarded operative floor plus the floor window's whole gross drift allowance; PLAN L133-L135 is corrected by addendum), **J6** (scope of the b_sens sensitivity), **J8** (LOO rows when the other contrast lost that quad) and **Z item 2** (LOO magnitude threshold is 0.25 x the floor); `docs/process_traces/2026-10-block5/trigger-erratum/ERRATUM.md` (E3; item 14 defines b_sens).

Source checkout: `929fc65c9ce3ff82f0311d28acf76a682edd466f` (`b5/analysis-r2` reference). This is a specification for an independent numerical implementation, not a production custody implementation. All fixture observations below are **SYNTHETIC S10**, not hardware validation. No production output or real window was read. No tests, floor corner enumeration, calibration refitting, or end-to-end analysis were run while drafting.

`PLAN Lnnn` means a line in `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` at this commit; `REG Lnnn` means a line in its companion `registration_block5.md`. The additional normative contracts are `docs/contracts/paper_reported_energy.md` (D-179, including “Kept units”), `docs/contracts/paper_claim_side_bound.md` (D-178, including the D-189 section), and D-189 in `docs/decision_log.md` at L12251 onward. D-189 is an issuance rule, not a different estimator. Section 6 below records apparent disagreements instead of resolving them.

The comparison target is the production numbers at this commit. Where a discrepancy is identified, implement the explicitly labelled production behavior for the comparison and retain the discrepancy in the handoff. This draft grants no permission to change the preregistration, production code, or scientific interpretation.

## 1. Inputs and the numerical boundary

### 1.1 Blinding and scope

Binding instruction, reproduced verbatim:

> BLINDING: never read/list/open /Users/edr/jw-b5-*, /Users/edr/night-*, night-custody, night-archive, or any restricted/ dir. Synthetic data only. The one exception: you may test for existence of the file /Users/edr/jw-b5-staging/dryrun-k/exit and existence of dirs /Users/edr/jw-b5-staging/release-* (names only).

The lead expressly permits the synthetic directory named `archive/sources/night-custody/` inside the committed S10 fixtures or their extraction at `/Users/edr/code/CapstoneProject/jw-wt/b5-lean-data/`. All reads for this work must stay inside that data root or this checkout. Do not follow historical absolute paths embedded in fixture JSON, ledger locators, model provenance, or harvest records. They are data strings, not input locators. In particular, do not open a production `restricted/` directory to discover output fields; the production locations in this document were obtained from code only.

The three inputs are the committed `tests/fixtures/b5_analysis/s10/{alpha,beta,gamma}/archive.tar.xz`, already extracted to `/Users/edr/code/CapstoneProject/jw-wt/b5-lean-data/{alpha,beta,gamma}/archive/`. Do not extract them again for the numerical implementation. All input paths below are relative to each pack's `archive/`.

| Pack | Pack id / archived config directory `P` | Model role |
|---|---|---|
| `alpha` | `d117_floor_qwen3-1p7b_v5` | Qwen3-1.7B-4bit; model key `qwen3-1p7b` |
| `beta` | `d117_floor_qwen3-8b_v5` | Qwen3-8B-4bit; model key `qwen3-8b` |
| `gamma` | `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` | A = 1.7B, B = 8B |

Exactly one analysed attempt per pack is used, selected before looking at effects (PLAN L53-L62). For this fixture comparison, selection is already represented by these three archives; do not search for other attempts. ALPHA's archived attempt is 1, BETA's 3, GAMMA's 1. The first quad is removed in both GAMMA phases. These facts are not filters to hard-code: read the exclusion documents.

### 1.2 Archive layout and fields

The numerical reader needs the following finite inventory, not a recursive search outside the archive.

| Relative input | Use and exact fields |
|---|---|
| `harvest.json` | `pack_id`, `plan_id`, `attempt`, `claim_usable`, `outputs` mapping relative filenames to SHA-256. This is the harvest record, not a source of phase energy. Its historical `archive_root` must not be used as a path. |
| `derived/exclusions.json` | `cells[]`, keyed by `cell_id`; `kept_units.repeat` and/or `kept_units.quad` contain unit ids; `n_kept`, `n_repeats`, `n_quads` are consistency checks. `dropped_units[]` records `stratum`, `unit_id`, `run_ids`, `positions`, `codes`. It is the sole primary exclusion authority (PLAN L77-L91). |
| `derived/roster.json` | `members[]`: `run_id`, `kind`, `stage_id`, `units[] {cell_id,stratum,unit_id}`. Join each member's unit memberships to exclusion ids. `cells[] {cell_id,strata,target}` identifies target/non-target cells. Persisted roster rows do **not** supply A1/B1/B2/A2 labels. |
| `derived/flags.jsonl` | One JSON object per line. Read `code`, `scope.level`, `scope.run_id` for member flags, and the scope/stage fields for disclosures. An assist member has the exact code `battery.assist` at member scope. |
| `derived/window_flags.json` | Window-level flags/hazard and yield information. Production disclosure collection joins flags from this record with the JSONL stream, validates their catalog classification, and deduplicates identical flag objects. Do not infer exclusions from flags a second time. |
| `derived/neg8-allowance.json` | `source`, `verdict`, `bound_used`, `bound_artifact_sha256`, `survivor_bracket`, `clean_bound`. This selects the allowance source; it does not itself contain the allowance number. |
| `withheld/neg8-rescreen-bracket.json` | Wrapper `.bracket`; in S10 all packs select this source. Gross allowance is `.bracket.claim_families.gross_energy.drift_allowance_j`, also recorded at `.bracket.drift_allowances.gross_energy.allowance_j`. |
| `withheld/neg8-clean-bound.json`, `derived/neg8-clean-corpus.json` | Parents of the rescreened allowance; named by the allowance record. Needed to audit the recorded allowance, not to compute floor scatter. |
| `derived/neg8-screen.json`, `derived/neg8-bound.json`, `derived/neg8-corpus-physics.json` | Reference-count, survivor, bound, and omission disclosures; not additional sources of science-member exclusions. |
| `withheld/bracket-evaluation.json` | `.assessment`: `status`, `b_fiducial_s`, `endpoint_max_b_fiducial_s`, `calibration_drift_allowance_s`, `pre`, `post`, `acceptance`. This is the harvest's recorded calibration assessment, distinct from the NEG-8 bracket. |
| `derived/bracket-binding.json`, `derived/terminal-pin.json` | Calibration identity bindings and terminal ledger sequence. Do not confuse the binding's digest with a numerical bound. |
| `sources/inputs/acceptance.json` | Issued acceptance, including `derivation_corpus.members[].b_fiducial_s`, `identity_epoch`, `ledger_cutoff`. Required for the supplementary block-maximum sensitivity. |
| `sources/ledger/calibration_observation_ledger.jsonl` | Ledger copy, used only through the archive's terminal pin. Never open `custody_locator` or `runs_root` values. |
| `sources/repo/configs/campaigns/P/extraction_spec.json` | ALPHA/BETA only. `reported_energy_cells[]` gives the 50 ordered members per reported cell. `cells[]` gives floor forms and exact repeat/quad membership. |
| `sources/repo/configs/campaigns/P/producer_contract.json` | Maps floor component ids to aggregate artifact cell ids via `roles[]`. The selected roles are `decode` and `prefill_p2048`; the latter becomes the mint's `prefill` role. |
| `sources/repo/configs/campaigns/P/analysis_manifest_v3.json` | GAMMA only. `contrasts[]` gives `contrast_id`, `metric`, `block_ids`, `members[] {run_id,block_id,block_number,position,arm,order_index}`, floor dependencies, direction and family. The archived prospective manifest has `contrasts[].members`; do not assume it has top-level `entries`. |
| `sources/repo/configs/campaigns/P/{plan_tree,calibration_plan,order_manifest}.json` and named stage order/config files | Structural joins, original order, and model/workload identity. Read only explicitly named relative config paths under `sources/repo/`. |
| `sources/repo/configs/campaigns/P/prefill_pin/{selection,prefill_prompt_pin}.json` | ALPHA/BETA's registered prompt/selection parents. No post-collection numerical estimate is taken from them. |
| `sources/night-custody/runs_claim/<run_id>/summary_metrics.json` | Stored point phase energy: `.phase_energy_j.decode` or `.phase_energy_j.prefill`; stored prechecks and envelopes for audit only. The scalar `.energy_bound_terms_j.E_clock_anchor_shift_bound_j` is request-level, **not** the phase bound. |
| Same bundle: `metadata.json`, `config.json`, `events.jsonl`, `power_trace.csv` | Runtime tokens, identity, timing, phase windows, and interval-support power trace. See below. |
| Same bundle: `raw/powermetrics.plist`, `instrument_calibration/…` | Only if using the full frozen re-reduction seam. Direct envelope evaluation on the already recorded trace avoids refitting/authentication. Never resolve embedded original absolute locators. |
| `withheld/meter.json`, if present | `.members[run_id]` is the whole-machine diagnostic row; see §3.8. It is absent in all three S10 packs. |
| `sources/SHA256SUMS` | Source-byte census if an implementer chooses to check fixture integrity. It is not a numerical estimator. |

Read neither `runs_bound` nor reference traces to estimate science effects. They are needed only if independently auditing NEG-8 instead of using its recorded, checked allowance. Other harvest monitoring files are outside the primary numerical dependency set; §3.7 identifies the structural disclosure boundary.

### 1.3 Unit reconstruction and order

Use each exclusion cell's kept ids, intersected with registered membership; do not select members by success status, readable files, energy, or a new validation pass. A missing member of a **kept** unit is an input error. Missing files in a removed unit are expected and must not be opened. A removed quad removes all four members (PLAN L82-L91; REG L784-L810).

For ALPHA/BETA, exclusion cell ids are `df-ph-{decode,prefill-p42,prefill-p2048}-<model>`. Reported ids are `d117-reported-mean-ph-<phase>-<model>`. A reported cell's `members[]` is ordered by `ordinal` 1–50. Ordinals 1–10 are repeats; 11–14 are quad 1, 15–18 quad 2, etc., with positions **A1, B1, B2, A2**. Use the floor spec's comparative `blocks[].members` map to join unit ids to these positions. Do not sort the exclusion `dropped_units[].run_ids`: that list is lexically sorted in the persisted exclusion record and would give A1,A2,B1,B2. Roster order/membership plus the registered spec restores the scientific order. Exclusion `positions` refer to roster positions, not reported-cell ordinals.

Floor ids are:

- Absolute: `d117-df-ph-<phase>-<model>-absolute`.
- Comparative: `d117-df-cmp-abba-ph-<phase>-<model>`.

For GAMMA, preserve each contrast's manifest `block_ids` order, then use the explicitly recorded `members[].position`. The exclusion cell id equals the contrast id. A1/A2 are 1.7B; B1/B2 are 8B (PLAN L373-L379; REG L794-L795). No randomization or swapping of sides is permitted. The two contrast ids are `ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b` and `ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b`.

S10 membership checkpoints, obtained by reading exclusion documents:

| Pack / phase | Kept repeats | Kept quads | Removed units |
|---|---:|---:|---|
| ALPHA decode, p42 | 9 | 9 | repeat r01 and quad b01 |
| BETA decode, p42 | 9 | 9 | repeat r01 and quad b01 |
| ALPHA/BETA prefill-p2048 | 10 | 10 | none |
| GAMMA decode | — | 9 | b01 |
| GAMMA prefill-p2048 | — | 9 | b01 |

Target counts below 5 in either required stratum are a refusal, not a new estimate (PLAN L83-L91). p42 shares decode's kept units but remains a non-target phase with its own refusal.

### 1.4 Energy, trace, tokens, and per-member bounds

All energy numerators here are **gross processor-rail phase energy**, in J, not `energy_request_j` or idle-subtracted energy (PLAN L201-L204, L221-L222; REG L630-L644). Read the stored phase point values. Changing only the fiducial bound changes envelopes and prechecks, not integration windows or point energy. Production step 2 performs an ordinary reduction and requires stored/refit-dependent fields to agree; later consumers separately reduce in memory under the operative window bound. Step 2's output is **not** the later bracket-widened summary.

For trace computations, `power_trace.csv` has `timestamp_s,power_w,source,rail,interval_start_s,interval_end_s`. Sum only `metadata.device.rail_manifest` at each common timestamp, then sort by timestamp. S10 has `cpu_power,gpu_power,ane_power`; do not add an already combined rail. Missing declared rails/support disagreement is an error. Treat each power as constant over its interval. For a window [x,y], energy is `fsum(P_j * max(0, min(y,end_j)-max(x,start_j)))`. Use `BundleReader.summed_curve()` and `phase_windows()` from the restricted kernel allowance in §2 to avoid inventing marker pairing. The `phase_start`/`phase_end` markers give one window for each relevant S10 phase.

Metadata fields are:

- `uncertainty_evidence.clock_anchor.effective_clock_anchor_bound_s` = member-local common shift bound m.
- `uncertainty_evidence.clock_anchor.wall_minus_monotonic_span_s` = independent edge span s.
- `workload_observed.output_token_count` = output T (512); `workload_observed.token_count` = total prompt + output.
- `workload_provenance.prompt.realized_token_count` = prompt count.
- `events.jsonl`: `phase_end` of `tokenize` and `phase_start` of `prefill`, each event's `metadata.prompt_tokens`, are the two additional prompt surfaces. All elements of each event-surface sequence must agree with the scalar prompt count and `total-output`. Prefill needs all four surfaces, positive integer denominators. Decode needs only runtime output count. Missing prompt surfaces do not invalidate a decode denominator.
- Tokenizer identity is `workload_provenance.tokenizer`. Frozen policy identity consists of policy `name`, `requested_tokens`, and `workload_provenance.sampler`. Production hashes these with sorted compact JSON. Neither realized emitted count nor stop condition is part of the policy hash. The token source is checked as runtime-observed via summary measurement quality; production's normalized record labels it `runtime_observed`.

Counts must be non-boolean integers, not configured counts or token timestamp fallbacks. Output-policy and tokenizer identities must be constant over the reported cell. For S10, target prefill counts are 2048; decode divides by **512**, despite only the last 511 outputs being generated in the decode phase (PLAN L248-L254).

The three gross-phase deterministic kinds, in this order, are:

1. `E_clock_anchor_shift_bound_j`: the phase envelope's `max_abs_delta_j` evaluated under **this window's b**, not the stored request scalar or pre-capture-only envelope.
2. `E_interpolation_joint_edge_bound_j`: sum of the phase precheck windows' `interpolation_joint_edge_bound_j`; explicitly 0 for these interval-support fixtures.
3. `E_whole_window_drift_allowance_j`: **half** the selected gross-family window allowance A.

All must exist and be finite/nonnegative. Missing never means zero. The floor's absolute width uses the max of the envelope's three equivalent excursions, plus interpolation; the reported/claim deterministic anchor term uses the envelope's recorded `max_abs_delta_j` (PLAN L233-L246, L309). Do not substitute the maximum member width for an average bound.

### 1.5 Calibration bracket b and NEG-8 allowance A

These are two different brackets. The calibration bracket supplies seconds b; the NEG-8 bracket supplies joules A.

Production **re-evaluates** each calibration bracket at step 3b using the archived ledger/inputs: `b = endpoint_max + max(observed_drift, bracket_screen)`. The comparison and acceptance arithmetic use Decimal lexemes; the reducer receives the recorded binary64 projection. The screen is 0.014531 s (REG L947-L960). The primary analysis does not replace per-window b with a block maximum. `evaluate_window_bracket` in `joulewise/b5_analysis/bracket.py:L421-L505` constructs the assessment; all primary consumers receive its b through an archive context.

For governed erratum-3 windows, the re-evaluated fields and selected acceptance subrecords must equal `withheld/bracket-evaluation.json.assessment`, or production refuses `window_bracket_differs_from_harvest`. The fixtures' BETA and GAMMA are governed pin4 shapes (`INDEX_ENTRY.json` has T0=1791738001, beyond the erratum cutoff 1791738000); ALPHA is an older pin2 shape for which this direct harvest-equality check is not made. Do not claim an executed replay of the brackets: none was run in drafting. Their recorded endpoint/allowance arithmetic gives the same b below; the code's deterministic formula and unchanged fixture inputs justify reading that recorded number in the lean numerical comparison. This shortcut drops authentication, not a numerical term. If a later fixture disagrees, expose the disagreement rather than choosing one silently.

| Pack | Recorded endpoint max (s) | Calibration allowance (s) | b (binary64 s) |
|---|---:|---:|---:|
| ALPHA | 0.02371598449914623 | 0.014531 | 0.03824698449914623 |
| BETA | 0.024723064620926976 | 0.014531 | 0.039254064620926975 |
| GAMMA | 0.022708904464676976 | 0.014531 | 0.037239904464676975 |

`derived/neg8-allowance.json.source` controls A (PLAN L237-L244):

- `stored_verdict`: read `sources/night-custody/runs_claim/whole-window-verdict.json`, the verdict row itself, at `idle_admission_core.neg8_bracket`, checking the allowance record's verdict row/basis binding. There is no `rows[]` wrapper in this S10 JSON file. Do not use the verdict's top-level status to reselect units.
- `survivor_rescreen`: read `withheld/neg8-rescreen-bracket.json.bracket`; require `decision == "passed"`, empty `conditions`, and consistent parents. Never fall back to the stored verdict bracket.
- Any other source or missing allowance: no allowance; refuse, never use 0.

Production's `whole_window.harvest_neg8_allowance_bracket` (L8969-L9127) authenticates the record, checks the bound/corpus, recomputes each family's excursion, count-adjusted bound, and allowance, and requires exact equality with the three recorded fields. Thus reading a **successfully checked** recorded A is numerically identical; no re-reduction of references is needed in lean. The formula is `A=max(trajectory_excursion_max_j,derived_repeatability_bound_j)`, not half that maximum. Only allocation to a science member divides by 2.

All S10 packs record `source=survivor_rescreen`, `bound_used=corpus_physics_clean`, reference counts start=2, midpoint=1, end=3, excursion=0.4546465258437422 J, derived gross bound=1.0440031334189257 J, and therefore **A=1.0440031334189257 J; A/2=0.5220015667094628 J**. The midpoint is present. GAMMA's diagnostic interior references enter neither screen nor allowance (REG L1004-L1009). GAMMA with `neg8.midpoint_lost` cannot be an analysed attempt; ALPHA/BETA disclose that loss without recomputing a different primary selection (PLAN L117-L138).

Recorded phase energies can be reused; recorded pre-capture envelopes cannot. A small direct kernel check on GAMMA decode b02 A1 gave the same point 97.58580408325196 J but stored anchor width 0.4773862379695828 J versus operative width 0.8191478630960631 J. The checks in §3.6 used the permitted envelope kernel on the 72 kept GAMMA members; every kernel point equalled its stored phase point exactly. No full reducer/custody call was made.

## 2. Frozen kernels the independent implementers may read or call

**Lead permission summary (binding; supersedes any wider wording in §2.1-§2.4).**

- MAY call (and read): `joulewise/bundle_read.py` (`BundleReader` and its trace/metadata/event/phase accessors, `TracePoint`, `Window`); `joulewise/reduce.py` only `_integrate` and `_corner_composed_anchor_shift_envelope` (and whatever they call); `joulewise/aggregate.py` only `student_t_critical_95` / `_T_CRITICAL_95` (or copy the literals of §2.3); `joulewise/analysis_engine/distributions.py` only `student_t_quantile`, `two_sided_student_t_p_value`, `student_t_cdf` and their helpers.
- MUST NOT read or call: `joulewise/detection_floor.py`, `joulewise/floor_extraction.py`, `joulewise/dominance_closeout.py`. The D-054 point floor, the corner enumeration, the linear extreme, the guard, the D-124 sweep and its width split, the drift widening and the R/R_cm replay are implemented from the formulas of §2.2, §2.4, §3.2 and §3.4, which transcribe those files exactly. (The plan names those files as the definition; the transcription is what the comparison with production checks.) Where §2.2-§2.4 below say a function "may be used", read it as "this is the production function your code must reproduce".
- NOT used: `_rederive_summary_for_authenticated_fiducial_bound` (full reducer under b; ~30 s refit per instrument calibration). The direct envelope route gives the identical numbers: lead check on ALPHA `d117fq31p7-df-ph-decode-abs-r02` decode under b = 0.03824698449914623 s, full re-derivation `max_abs_delta_j` = 0.6169095327593794 and direct `_corner_composed_anchor_shift_envelope(curve, [window], m, b, s)` = 0.6169095327593794, identical `point/lower/upper`.

Everything outside this section's numerical/trace seams is to be implemented from the formulas in §3. Permission to read a file here is limited to the named functions, their numerical constants/types, and the helpers they invoke for this computation. It is not permission to study its custody, mint, validation, driver, or other analysis implementation. Imports may load dependencies, but do not use that to inspect production glue. Standard-library `math`, `statistics`, `decimal`, JSON and CSV handling are unrestricted.

### 2.1 Trace and reducer envelope

Allowed files: `joulewise/bundle_read.py` for `TracePoint`, `Window`, `BundleReader`'s trace/metadata/event/phase accessors and their parsing/pairing helpers; `joulewise/reduce.py` for the following trace numerical seams. PLAN L246 and L309-L316 define these as the exact estimator, rather than an edge-power approximation.

- `BundleReader(path: Path)`; `.summed_curve() -> list[TracePoint]`, `.phase_windows() -> dict[str,list[Window]]`, `.metadata() -> dict`, `.events() -> list`, `.raw_summary() -> dict|None`. `TracePoint(t,power_w,support_start_s=None,support_end_s=None)` and `Window(start_s,end_s)` carry seconds/W. These accessors read only that bundle. They supply the overlap support and marker pairing; do not invoke strict-validation or corpus/custody discovery methods.
- `_integrate(curve: list[TracePoint], start_s: float, end_s: float) -> float`: interval overlap integral, returning 0 when end <= start. Used by the common-mode sweep.
- `_corner_composed_anchor_shift_envelope(contributions: list[tuple[list[TracePoint],list[Window]]], bundle_bound_s: float|None, fiducial_bound_s: float|None, wall_minus_monotonic_span_s: float=0.0) -> dict|None`. Call with one `(curve,[phase_window])`, `m`, `b`, `s`. For residual widths call identically with fiducial **0.0**. Returns `method`, `point_j`, `lower_j`, `upper_j`, `max_abs_delta_j`, `anchor_bound_s`, `wall_minus_monotonic_independent_edge_span_s`, `independent_edge_shift_bound_j`. None is a refusal, never width 0.
- Its `_anchor_shift_envelope`, `_anchor_shift_breakpoints`, `_shift_energy_j`, and interpolation helpers may be used as dependencies. The outer function subtracts a common epoch before displacement arithmetic; preserve that operation. It evaluates four independent edge corners with edge bound `b+s`, then the exact common-shift breakpoint extrema over ±m. m is the metadata effective bound as recorded; do not subtract s out of m or add b a second time.
- `_rederive_summary_for_authenticated_fiducial_bound(path: Path, *, authenticated_fiducial_bound_s: float, _instrument_calibration_physics_cache: dict[str,float]|None=None) -> dict`: allowed as the full frozen reducer alternative. Production's authenticated consumption session calls it with the selected per-window b and keeps the result in memory. It dispatches using the stored reducer identity; callers may not choose another version. It is unnecessary for lean's direct trace-envelope route. It must never be used in a way that follows an embedded locator outside the permitted synthetic roots.

### 2.2 D-124 shared-edge sweep

Allowed numerical seams in `joulewise/floor_extraction.py` (PLAN L310-L317):

- `_common_mode_block_inputs_from_evidence(members: Sequence[MemberReport], *, runs_root: Path, metric: str, shared_edge_bound_s: float) -> _CommonModeBlockInputs`. Supply four minimal member records having `.bundle_id` and `.position`, with positions A1,B1,B2,A2; runs_root is the permitted synthetic `sources/night-custody/runs_claim`; metric is `phase_energy_j.decode` or `phase_energy_j.prefill`; shared bound is that floor pack's b. No extraction driver is needed. Production step 4 and the step-5 mint recomputation both call this seam.
- `_CommonModeBlockInputs` contains `onset_values_j`, `offset_values_j`, `zero_point_contrast_j`, four `bundle_residual_half_widths_j`, four `member_window_bounds_s`, and `member_envelope_integral_sum_j`.
- `_common_mode_block_input_from_contrast(*, contrast, onset_shifts_s, offset_shifts_s, bundle_residual_half_widths_j, member_window_bounds_s, member_envelope_integral_sum_j)` is the pure alternative when parsing is implemented independently.
- `_common_mode_floor_from_block_inputs(block_deltas_j, block_inputs, *, calibration_bracket, shared_edge_bound_s) -> FloorEstimate`, with bracket equal to the recorded **assessment object**, not its wrapper. This includes the exact width composition, domain checks, and calls the comparative floor kernel. `_common_mode_floor_from_extracted_inputs`/`_common_mode_floor_core`, `_common_mode_block_half_width`, grid/finite/window helpers are dependencies. For the supplementary wider-bound sensitivity only, use `_sensitivity_common_mode_floor_from_block_inputs` with b_sens; the primary seam requires equality to b rather than merely a larger bound.

The grid is **not** a regular mesh. For each member, subtract its first curve timestamp from all supports and both phase edges. Each grid starts with `{-b,+0.0,+b}` and adds every `support_start_s-window_edge` and `support_end_s-window_edge` lying inclusively inside [-b,b], for all four members. Sort the unique onset and offset grids separately. The zero-shift contrast z is computed once and reused at the grid's zero entries. (Lead clarification, exact production form: `onset_sweep_j[i] = z if e_on == 0.0 else contrast(e_on, 0.0)` over the sorted onset grid, and `offset_sweep_j[i] = z if e_off == 0.0 else contrast(0.0, e_off)` over the sorted offset grid; the two sweeps are separate one-dimensional sweeps, never a 2-D product. Each member's residual half-width is `_corner_composed_anchor_shift_envelope([(relative_curve, [relative_window])], m, 0.0, s)['max_abs_delta_j']` on the origin-subtracted curve and window, positions in A1,B1,B2,A2 order; `None` refuses. `delta_j` in the split is the floor delta `(B1+B2-A1-A2)/2.0` of the stored phase energies. The comparative width is w_k = `out4(fsum((shared, local)), +inf)` from the split of §2.4.) At each sweep point compute `fsum(c_p * integrate(curve_p,on_p+e_on,off_p+e_off))` in A1,B1,B2,A2 order with coefficients (-0.5,+0.5,+0.5,-0.5). This z can differ from a stored-energy ABBA delta by rounding; the difference is explicitly budgeted. The padding scale input `member_envelope_integral_sum_j` is `fsum(abs(c_p)*integrate(curve_p,on_p-b,off_p+b))` in that same position order; it is not the sum of the four envelope half-widths.

Each member needs exactly one nonnegative interval-support phase window. The strict domain is `nextafter(start+b,+inf) < nextafter(end-b,-inf)`; a collapsed/touching window refuses `common_mode_nonseparable_window_domain`. Do not replace a refused shared-edge computation with an independent-member approximation. Record both sweeps and residuals for audit.

### 2.3 Floors and numerical tables

Allowed file `joulewise/detection_floor.py`, only:

- `absolute_false_effect_floor(values_j: Sequence[float], *, admissible_half_widths_j: Sequence[float]) -> FloorEstimate`.
- `comparative_false_effect_floor(block_deltas_j: Sequence[float], *, admissible_half_widths_j: Sequence[float]) -> FloorEstimate`.
- `_floor_estimate`, `_corner_maximized_unguarded_floor`, `_linear_corner_widened_max`, `_apply_admissible_set_guard`, admissible-value helpers and `FloorEstimate` as dependencies. `MAX_EXACT_ADMISSIBLE_CORNER_N=16`.
- `abba_delta(a1_j,b1_j,b2_j,a2_j) -> float` is the **floor** delta, evaluated `(b1+b2-a1-a2)/2.0` left to right.
- `small_sample_guard_factor(n: int) -> float`; `registered_common_mode_operative_bound(calibration_bracket) -> float`; `common_mode_zero_points_agree(a,b,summed_joule_terms) -> bool`; their numerical helpers/constants.

The floor kernel is explicitly named by PLAN L289-L309. It does not implement reported-cell CIs or claim tests. `FloorEstimate` has point diagnostic fields (`mean_j,deviations_j,sample_stddev_j,max_abs_deviation_j,t_critical,prediction_component_j`) but its `unguarded_floor_j`/`guarded_floor_j` are already widened operative values; do not mislabel the former as the point floor.

Allowed file `joulewise/aggregate.py`, only `_T_CRITICAL_95` and `student_t_critical_95(df:int)->float`. At df=1…9 the floor literals are `12.706,4.303,3.182,2.776,2.571,2.447,2.365,2.306,2.262`. Other listed df use their table entry; an unlisted positive df uses the largest listed df below it. The required primary floor df are 8 and 9. Do not use an exact quantile here (PLAN L300).

Allowed file `joulewise/analysis_engine/distributions.py`, only `student_t_quantile(probability:float,df:int)->float`, `two_sided_student_t_p_value(statistic:float,df:int)->float`, `student_t_cdf` and their incomplete-beta helpers. Production uses `round(student_t_quantile(0.975,n-1),3)` for contrasts, but unrounded CDF tails for p-values. Use this dependency-free numerical CDF if exact production rounding is desired; a different library can differ in the last bits. No permutation functions are needed.

The exact reported/descriptive T975 table is reproduced in §3.1; it requires no permission to read the reported-energy implementation.

### 2.4 D-165 width split and replay

Allowed file `joulewise/dominance_closeout.py`, only the numerical functions below and their finite/outward helpers. The replay is explicitly code-defined by PLAN L351-L355.

- `split_common_mode_block_width(*, delta_j, onset_sweep_j, offset_sweep_j, zero_point_contrast_j, bundle_residual_half_widths_j, member_envelope_integral_sum_j) -> {shared_width_j,local_width_j}`. These are the D-124 block inputs above. Production extraction calls this when making w_k; the replay uses the same split.
- `replay_common_mode_dominance(blocks: Sequence[Mapping], *, calibration_bracket:object, shared_edge_bound_s:float) -> dict`. Each raw block must contain `delta_j,onset_sweep_j,offset_sweep_j,zero_point_contrast_j,bundle_residual_half_widths_j,member_window_bounds_s,member_envelope_integral_sum_j`; windows must be four JSON-style two-element lists. It returns `rule_id,point_unguarded_floor_j,common_mode_corner_widened_unguarded_floor_j,ratio,threshold,comparison,passes`. Production step 5 records these inputs/results; step 6 replays them.
- `dominance_ratio(*,corner_widened_unguarded_floor_j,point_unguarded_floor_j)->dict` returns ratio and the >=2 predicate; zero denominator refuses.

For exact outward arithmetic define `out4(x,d)` as four successive `math.nextafter(x,d)` calls. In the split, set `S=max(member_envelope_integral_sum_j,1,abs(delta),abs(z),abs(each onset/offset value))`; pad = `64*(ulp(1.0)/2)*S`. Set `l=out4(fsum(min(onset),-z,min(offset),-z,-pad),-inf)` and `u=out4(fsum(max(onset),-z,max(offset),-z,+pad),+inf)`, preserving the code's two-stage fsum association: first the four excursion terms, then the pad. Shared = `out4(fsum(out4(max(abs(l),abs(u)),+inf),abs(z-delta)),+inf)`. Local = `fsum(four residual widths)/2.0`. The extraction width is **`out4(fsum(shared,local),+inf)`**. These pads and outward steps resolve the plan's real-arithmetic formula; do not drop them.

Zero-point agreement is `isclose(z,delta,rel_tol=0,abs_tol=max(1e-6,1e6*2**-53*scale))`, with scale the largest absolute contributing joule term. A zero point must also be an exact member of each sweep. A D-124 registered bracket must pass, contain a positive once-embedded `max(observed_drift_s,bracket_screen_s)` allowance, and satisfy b=endpoint+allowance within absolute 1e-12; the kernel checks this. Shared b is not b plus another calibration allowance.

## 3. Estimators and production records

### 3.0 Numeric conventions and production filename notation

Use finite IEEE binary64 floats for energy arithmetic, except the explicitly named Decimal comparisons and formatting. Preserve sequence order. `sum` means Python's built-in sum at the production interpreter; `fsum` means `math.fsum`; `fmean` and `stdev` mean `statistics.fmean` and `statistics.stdev`, including their actual summation behavior. These are not interchangeable. Target semantic float agreement, not equality of custody digests, absolute paths, or source-file formatting. Use `PYTHONDONTWRITEBYTECODE=1` for read-only Python audits and run work at background priority.

**Output-location notation:** all locations in this section are **names from code**, relative to the custody root's `dry-run/restricted/`; no such directory was read. `H` means the full 64-character SHA-256 of that particular file's bytes, not a literal filename and not one shared hash. `dry_run.StepState.register` renames most named outputs to `H-basename`; `write(addressed=True)` replaces the basename with `H.json`. Resolve the actual file using the public dry-run record's `steps[].outputs[] {name,sha256}`, not by guessing H. Distinct addressed files in the same directory have distinct hashes and roles.

| Alias | Step | Actual production location |
|---|---|---|
| `ER(pack)` | 4 | `mint/H-extraction-<pack>.json` |
| `AF` | 5 | `mint/H-aggregate-floor.json` |
| `DR` | 5 | `mint/H-dominance-replay.json` |
| `PIN` | 5 | `mint/floor-mint-pinset.json` |
| `CLOSE` | 6, after 8 | `finalized/outputs/closeout.json` |
| `RT` | 6 | `finalized/outputs/closeout.ratio-table.json` |
| `CV` | 9 | `outputs/H-claim-verdicts.json` |
| `CSB` | 9b, if issuable | `custody/H.json`, role `claim_side_bound`; nominal request was `custody/claim-side-bound.json` |
| `PROJ(pack)` | 10 | `outputs/H-projection-<pack>.json` |
| `SENS` | 11 | `outputs/H.json`, role `sensitivity`; nominal request `outputs/sensitivity.json` |
| `DISC` | 11 | `disclosures/H.json`, role `disclosure_record`; released/unreleased text have their own hashes and suffixes |
| `BR(pack)` | 3b | `brackets/H-<pack>.json` |
| `BMAX` | 3b | `brackets/H-block.json` |

Ordinary step-2 summaries retain `rereduced/<pack>/<run_id>.rereduced.json`. Kept counts are also recorded in step 3 at `kept-units/H-<pack>.json`. The finalization copies of AF/DR live at `finalized/mint/H-aggregate-floor.json` and `finalized/mint/H-dominance-replay.json`; the finalized manifest is `finalized/<manifest_id>.finalized.json` (`analysis_manifest_v3.FINALIZED_BASENAME_SUFFIX`). The numeric mappings below do not depend on its basename.

### 3.1 (a) Reported cells: PLAN §4 / D-179

Authority: PLAN L221-L256 and `paper_reported_energy.md` “Kept units”; membership REG L803-L810. Let r be the kept repeat energies, q the ordered member energies of kept quads, and b_k=`fmean` of the four energies in quad k. r precedes q in the reported ordinal order. Let nr=len(r), nb=len(b).

Evaluate in this order:

1. If nr=nb=10, m=`fmean(all 50 energies in ordinal order)`. Otherwise m=`0.2*fmean(r)+0.8*fmean(b)`.
2. sr=`statistics.stdev(r)`; sb=`statistics.stdev(b)` (divisor n−1; do not substitute a hand-written residual sum).
3. V=`0.2**2 * sr**2 / nr + 0.8**2 * sb**2 / nb`. Use these exponentiated literals, not 0.04/0.64, to preserve the final binary digit.
4. df=`min(nr,nb)-1`; h=`T975[df]*sqrt(V)`.
5. For each deterministic kind, at full counts its average is `fmean(50 member bounds)`. Otherwise K=`0.2*fmean(repeat bounds)+0.8*fmean(quad-member bounds)`. The second mean is over **4nb members**, not just a selected side. B=`fsum(K values)` in the three-kind order in §1.4.
6. lower=`m-h-B`; upper=`m+h+B`, left associated, without clamping.
7. Full counts per-token=`fsum(all energies)/sum(all T)`. Reduced counts per-token=`0.2*(fsum(r)/sum(T_r))+0.8*(fsum(q)/sum(T_q))`. Retain the energy/token totals for both strata and all members. Even when every T is the same, do not simplify the canonical float expression to m/T.
8. Attribution floor=`max(member phase anchor bounds)`, min=`min(...)`, argmax=first attaining bundle in original ordinal order. `attribution_floor_composed=false`. This maximum is displayed, not added to B or h.

Exact `T975` literals (also used by §3.6 ratio and cross-window estimates):

| df | T975 |
|---:|---:|
| 1 | 12.706204736174705 |
| 2 | 4.302652729749464 |
| 3 | 3.1824463052837095 |
| 4 | 2.7764451051977943 |
| 5 | 2.5705818356363155 |
| 6 | 2.44691185114497 |
| 7 | 2.364624251592785 |
| 8 | 2.306004135204166 |
| 9 | 2.262157162798205 |

Primary cells require nr,nb>=5 and complete ordered rows for every kept unit. A per-token denominator/scope problem refuses only that sibling. Its `status="refused"`, value/tokens null, and reason is retained; the energy mean still exists. A missing deterministic kind refuses the energy cell. Production's normalized strict/precheck failure becomes `paper_reported_energy_record_invalid` through `_project_kept_cell`; do not replace a bad kept member by another bundle.

**p42:** keep a refused cell with no energy estimate. The S10 stored prefill-p42 precheck has `cadence_ratio_unrecorded` and `insufficient_in_window_samples`; the wider envelope may add `anchor_energy_envelope_exceeds_quarter_metric`. The production reported projection refuses it with `paper_reported_energy_record_invalid`, leaving target decode/p2048 issued. Do not report the available point prefill scalar as an issued p42 value (PLAN L92-L95, L637-L638).

**Production record:** `PROJ(pack).cells[cell_id]`: `mean_j,lower_j,upper_j,n_bundles,independence_units,interval.{n_r,n_b,df,s_r,s_b,variance,h_j,kind_averages_j,B_j},per_token.{status,reason,energy_sum_j,observed_token_sum,j_per_token,strata},attribution_floor.{value_j,attained_by,minimum_j},binding.attribution_floor_j,attribution_floor_composed,kept_units,removed_units`. Select list rows by id, not index. p42 is in `refused_cells[] {cell_id,code,target,plan_code}`. Do not expect a `status` field on successful production cell rows.

Arithmetic-only S10 checkpoints (stored energies; no full reducer or issuer run):

| Pack / phase | m | sr | sb | V | h |
|---|---:|---:|---:|---:|---:|
| ALPHA decode | 99.03179576104058 | 15.64079141448331 | 6.949439049782262 | 4.521553803455967 | 4.9034746368635 |
| ALPHA p2048 | 105.48237820861756 | 23.39165673456546 | 13.05947182421114 | 13.103865896102306 | 8.188842045452539 |
| BETA decode | 103.80356829774307 | 26.52025214256461 | 11.601422352063208 | 12.69694125849081 | 8.216930940244701 |
| BETA p2048 | 111.72658072246566 | 23.908442185779645 | 10.257148926445163 | 9.019837093356685 | 6.793946475521171 |

### 3.2 (b) Floors per pack × phase × form

Authority: PLAN L289-L317. Compute six components per floor pack, preserving p42 refusals; only decode/p2048 enter the mint.

For absolute values v=repeat energies: mean=`sum(v)/n`, deviations u_i=`v_i-mean`, prediction extra=0. For comparative values v_k=`(B1+B2-A1-A2)/2.0` in that evaluation order: mean=`sum(v)/n`, deviations u=v **without re-centering**, prediction extra=`abs(mean)`. In both cases, the floor kernel evaluates `u_mean=sum(u)/n`, s=`sqrt(fsum((u_i-u_mean)**2)/(n-1))`, t=`student_t_critical_95(n-1)`, prediction=`extra+t*s*sqrt(1.0+1.0/n)`, maxdev=`max(abs(u))`, point P=`max(maxdev,prediction)`. Notice the second centering of absolute residuals for the standard deviation and its use of built-in sum; replacing this by `statistics.stdev(v)` can move the last bits.

Absolute admissible widths w_i are the operative member envelope max excursion plus the phase interpolation bound. Comparative widths w_k come from the D-124 sweep/split in §2.2–2.4. They are not half the sum of four full fiducial member bounds; only the residual widths use fiducial zero.

Enumerate masks 0 through `2**n-1` in input order, corner value i=`v_i+(w_i if mask&(1<<i) else -w_i)`. Recompute the **whole point-floor functional** at each corner, including its mean, s and prediction; take maximum C0 (start the running maximum at 0.0). Exactly, for corner c (a list of n floats): `cm=sum(c)/n`; absolute: `u=[c_i-cm]`, extra=0.0; comparative: `u=c` (not re-centred), extra=`abs(cm)`; then `um=sum(u)/n`, `s=sqrt(fsum((u_i-um)**2)/(n-1))`, `pred=extra+t*s*sqrt(1.0+1.0/n)` with t=`student_t_critical_95(n-1)`, value=`max(max(abs(u_i)),pred)`. If all widths are zero, use the point functional directly. Exact enumeration is capped at n=16 for nonzero widths; no Monte Carlo/grid approximation is admissible.

Also compute the exact linear extremum L. For comparative L=`max(abs(v_i)+w_i)`. For absolute, W=`fsum(w)`; residual width i=`w_i*(n-1)/n+(W-w_i)/n`; L=`max(abs(u_i)+residual_width_i)`. Corner cover C=`max(C0,L)`; operative unguarded U=`max(P,C)`. Production stores **U** in both `corner_widened_unguarded_floor_j` and `unguarded_floor_j`; it does not serialize C0 separately. Keep C0 as a lean audit intermediate with no direct production-field comparison.

Guard g=1.0 if n>=10, otherwise `sqrt(9/(n-1))` for n>=5. Guarded G=`g*U`. S10 decode uses n=9/g=sqrt(9/8); p2048 n=10/g=1. P42 has no floor and n_admitted=0 on refusal, even though the exclusion census still has 9 kept units per stratum.

**Production behavior requiring an explicit discrepancy marker:** the extraction report and mint then add the **full** gross window allowance A, after the guard: drift-unguarded=`U+A`, drift-guarded=`G+A`. `operative_floor_j=G+A`. Do not compute `g*(U+A)` or add A/2. This follows `floor_extraction.CellReport.as_row` and `detection_floor._add_whole_window_drift_allowance`; it disagrees with PLAN L134-L135 as recorded in §6.

Other numerical refusal rules: fewer than two values cannot define scatter; below five no primary guarded floor; width count must equal n and widths must be finite/nonnegative. A kept member's envelope must match its point (production `isclose`, relative 1e-9/absolute 1e-12), and its total half-width may not exceed 0.25*abs(metric), with zero metric/nonzero width refusing. D-124 requires the strict window domain and zero-point checks in §2. A sole cell condition `admissible_set_uncertainty_dominates_point_floor` labels an attribution-limited floor while retaining the widened numeric result; it is not permission to publish the point diagnostic. p42's fatal prechecks leave `floor=null,extractable=false`; they do not stop other components (PLAN L174-L178).

**Production record:** `ER(pack).cells[floor_cell_id]` has `kind,metric,n_planned,n_admitted,extractable,refusal_reasons,operative_floor_j,whole_window_drift_allowance,anchor_shift_bound_max_j,members[]`. `.floor` has `n,mean_j,deviations_j,sample_stddev_j,max_abs_deviation_j,t_critical,prediction_component_j,unguarded_floor_j,guard_factor,guarded_floor_j,admissible_half_widths_j,corner_widened_unguarded_floor_j,corner_widened_guarded_floor_j,whole_window_drift_allowance_j,drift_widened_unguarded_floor_j,drift_widened_guarded_floor_j`. Point P is `max(floor.max_abs_deviation_j,floor.prediction_component_j)`, or `point_floor_diagnostic.unguarded_floor_j` when that optional label exists. A `.members[]` row records `bundle_id,position,block_id,metric_value_j,anchor_shift_bound_j,operative_anchor_envelope`; phase-widened summaries themselves are not persisted as step-2 files.

### 3.3 (c) Aggregate floor and per-contrast gate

Authority: PLAN L330-L337. There are four aggregate cells, artifact id `d117-qwen3-phase-floor-set-v5`:

- `d117-qwen3-1p7b-decode-floor-v5`, `d117-qwen3-1p7b-prefill-p2048-floor-v5`;
- `d117-qwen3-8b-decode-floor-v5`, `d117-qwen3-8b-prefill-p2048-floor-v5`.

For a model/phase, Fabs=`absolute.G+A`, Fcmp=`comparative.G+A`, Fgate=`max(Fabs,Fcmp)`. No pooling across models, phases, or forms. Transport group `tg-d117-<model>-<decode|prefill-p2048>-v5` takes the componentwise maximum over eligible source cells, which is just its one cell in S10. For a GAMMA phase, resolve the A and B models separately under `exact_stack_only.v1`, then aggregate Fabs=max(side Fabs), Fcmp=max(side Fcmp), active F=max(side Fgate). The policy is `same_stack_componentwise_worst_case.v1` followed by `cross_stack_armwise_max.v1`, never a sum.

Production uses the full binary64 floors for AF and the claim gate. PIN also records Decimal(str(float)) full-precision strings and six-decimal **ROUND_HALF_EVEN** diagnostic literals. Do not feed those six-decimal strings back into the gate. `mint_floor_artifact_generalized.py:L2776-L2922` recomputes both forms, requires report-width/floor equality using Decimal strings, then makes the pin projection. `detection_floor.build_floor_cell` puts the drift-guarded numeric components into `floor_abs_j,floor_cmp_j,floor_gate_j`.

If either model resolution is unusable, combined `floor.status="refused"`, `floor_abs_j,floor_cmp_j,active_floor_j=null`. Never use the other model's floor alone or null as zero. Resolution may be labelled `transported` despite exact-stack-only model matching: that rule names eligibility, not necessarily the wire status `exact`. The actual exact/transported resolution and source ids must be preserved.

**Production record:** `AF.cells[aggregate_cell_id].{floor_abs_j,floor_cmp_j,floor_gate_j,absolute,comparative}`; transport groups' `composed_floor_*_j`; `CV.contrasts[contrast_id].floor.{status,floor_abs_j,floor_cmp_j,active_floor_j,transport_verdict,resolutions,arm_gates}`. Each `arm_gates[]` row has `arm_id,condition_family_id,status,floor_gate_j`. The per-side projection from `_decorate_v3_floor` uses the condition-family/transport binding; select sides by their condition ids. Refusal/source-provenance mismatches are input failures, not numerical fallback modes.

### 3.4 (d) Eight R and four R_cm dominance ratios

Authority: PLAN L339-L360. For each aggregate cell's absolute and comparative component, R=`U/P`, with numerator the corner-widened **unguarded** floor and denominator the point **unguarded** floor. Neither g nor A enters either operand. Threshold is 2.0, equality passes.

For each comparative component, split every block width into shared S_k and local L_k by §2.4. Enumerate one shared sign s in (-1,+1) and every independent local mask. Perturbed delta k is evaluated left-to-right as `d_k+s*S_k+(L_k if mask&(1<<k) else -L_k)`. Compute its comparative point floor by calling the floor kernel with **all widths zero**. The maximum is Ncm; denominator is the original comparative point floor P, also computed with zero widths. Rcm=`Ncm/P`. Use the split widths, not the already outward-summed w_k; they cannot be losslessly recovered by subtraction.

This is `d165_shared_sign_local_corner_replay.v2`, an energy-sign sensitivity diagnostic, not a physical common-time worst case. Absolute Rcm is `not_applicable` (PLAN L351-L355). Record each ratio's n, operands, threshold and pass flag, labelled “point diagnostic; no interval”.

Any P=0 refuses `dominance_ratio_zero_denominator`; no Infinity/NaN. If every 8 R and every 4 required Rcm passes, branch A, `dominance_sentence_licensed=true,subtitle_licensed=true`; otherwise branch B and both false. A malformed/refused ratio makes production branch null and licenses false; it is not a numerical branch-B ratio of zero.

**Production record:** `CLOSE.independent_ratios[]` keyed by `(cell_id,component)` has `point_unguarded_floor_j,corner_widened_unguarded_floor_j,ratio,threshold,comparison,passes,status,refusal_reason`. `CLOSE.comparative_common_mode_ratios[]` substitutes `common_mode_corner_widened_unguarded_floor_j`. Global fields include `all_independent_pass,all_required_common_mode_pass,branch,dominance_sentence_licensed,subtitle_licensed`. `RT.ratios[]` records explicit `numerator_j,denominator_j,n,ratio,status,label` for all twelve. `DR.cells[].comparative.common_mode_replay.inputs` records `calibration_bracket,shared_edge_bound_s,blocks[]`; `.result` records replay operands and ratio. Do not read a production replay sidecar as a lean input; it is a comparison output.

### 3.5 (e) GAMMA contrasts, intervals, tests, decisions, LOO

Authority: PLAN L364-L477. Both contrasts are primary, two-sided, positive registered direction, fixed planned 10 blocks, m=2 Holm, alpha=0.05, no replacements/top-ups or equivalence/MDE. Kept n is 9 in S10. The manifest family's instance id is `fam-d117-gamma-decode-prefill-p2048-primary-holm-v5`.

For each kept quad compute a_k=`(A1+A2)/2.0`, b_k=`(B1+B2)/2.0`, then **d_k=b_k-a_k**. Do not use the floor's algebraically equivalent `(B1+B2-A1-A2)/2` evaluation here. m=`fsum(d)/n`; sd=`sqrt(fsum((d-m)*(d-m))/(n-1))`; se_rep=`sd/sqrt(n)`, se_met=0.0 for these phase metrics, se_total=`hypot(se_rep,se_met)`. Metrology variance is not added from the request's idle-baseline fields (PLAN L389-L403).

Critical t*=`round(student_t_quantile(0.975,n-1),3)`. Set half=`t*se_total`; metrology interval I=`{lower:m-half,upper:m+half}`. Repeat-point CI is identical here. There is no prediction factor sqrt(1+1/n).

For each of the three deterministic kinds c, a quad's bound is `((c_A1+c_A2)/2.0)+((c_B1+c_B2)/2.0)`. D_c=`fsum(quad bounds)/n`; deterministic names are sorted lexically in production, yielding anchor, interpolation, whole-window drift here. D=`fsum(D_c)`. Decision interval is `{lower:I.lower-D,upper:I.upper+D}`. The drift contribution D_drift equals the **full GAMMA A**, since each member carries A/2. No ABBA cancellation is inferred for deterministic bounds. Production's claim path uses the independent sum of operative member envelopes, not the floor's D-124 shared width; see the explicit ambiguity in §6.

Test statistic t=m/se_total; p=`two_sided_student_t_p_value(t,n-1)`, without rounding t or p. If se_total=0, finite JSON t is null and p=0 for nonzero m, p=1 for m=0. Production does not serialize t; it is a lean diagnostic reconstructed from estimator fields. Non-estimable hypotheses retain their slot in m=2 and get null p. For both finite p, sort by `(p,contrast_id)`; adjusted first=`min(1,2*p1)`; adjusted second=`min(1,max(2*p1,p2))`. Rejection iff adjusted p<=0.05. If only one p exists it still receives factor 2. No outcome/floor filtering before Holm.

Refusal and outcome rules, in priority order (PLAN L417-L434):

1. Non-estimable input/metric conditions produce `not_estimable`: invalid/nonfrozen manifest, order hash mismatch, invalid floor artifact, missing/nonfinite metric, fewer than two complete blocks, or required token/stop/policy/tokenizer failures. Null estimate, CIs and D remain null.
2. Unusable floor or member/window/error-term provenance reasons produce `not_resolvable`. These include missing/ambiguous/stale/inapplicable floor, missing absolute/comparative component, required bound/covariance unknown, or a kept-member precheck failure. Removed quads must **not** add `fixed_n_plan_incomplete`/`paired_block_incomplete`; the kept plan is the expected count. If such a code fires on a kept unit, stop as a tooling disagreement rather than drop the unit.
3. With usable inputs, `abs(m)<=F` adds `effect_not_above_floor` and gives `not_resolvable`. Interpolation total >=F or >=0.5*abs(m) adds the corresponding interpolation reason; its value is 0 here, so equality matters at zero effect/floor.
4. If I contains zero inclusively, outcome `unresolved`. If I excludes zero but the decision interval contains zero inclusively, `not_resolvable` with `deterministic_bound_obscures_direction`. Otherwise a nonrejected Holm test gives `unresolved`/`multiplicity_not_rejected`; otherwise `direction_supported` with sign of m.

The L2 ceiling requires direction_supported, primary/secondary role, confirmatory status, current evidence, direction matching positive, and no verdict-influential LOO or blocking randomization sensitivity. Otherwise ceiling L1. Magnitude-only LOO concerns do not lower the ceiling. Both S10 p-values are large; Holm adjusted p is 1.0 for both. Large floor diagnostics also exceed these small effects, so the numerical rules predict `not_resolvable`/L1 for both; this is an inference from fixture arithmetic, not an observed production run.

LOO is a **family** recomputation (PLAN L436-L440), not two unrelated one-contrast loops. Match block number 1…10 across phases. For each number retained by at least one complete contrast, remove that numbered block from **each** contrast where it is kept. Recompute its estimator/D/CI/p; leave the other unchanged if it had already lost that number. Reapply Holm to both p-values with m=2. Re-resolve the floor against the retained member identities; the same registered source cells and numeric floor apply on S10 (do not recompute floor-pack samples). Emit a row for a contrast only if that number was in its kept quads. Thus S10 has 9 LOO rows per contrast, each with n=8, df=7 and t*=2.365. If the primary n is 5, LOO's n=4 is still a sensitivity estimator; do not impose a new primary-minimum refusal on it.

For each LOO row compare against the full estimate/evaluation: sign (negative/zero/positive), above-floor status `abs(estimate)>F`, adjusted rejection, and outcome. Changed values produce triggers, in that order: `estimate_sign,floor_status,adjusted_rejection,outcome`. Movement strictly greater than 0.25*F adds `estimate_magnitude`. Any first-four trigger adds `loo_verdict_influential`; magnitude adds the nonblocking `loo_magnitude_influential` only when no verdict trigger occurs anywhere. The primary point outcome is not overwritten by a ceiling reduction. `deterministic_rotation/exchangeability:none` gives randomization status `not_required`, with null exact p/rejection; do not run a sign-flip test.

**Production record:** `CV.contrasts[id]`: `sampling.{planned_n,observed_complete_n,kept_n,removed_block_ids,confirmatory_status}`, `bundle_blocks.{planned_block_ids,included_bundle_ids,blocks}`, `estimator.{name,n,df,estimate,s_d,SE_repeat,SE_metrology,SE_total,t_critical_95,repeat_point_CI95,metrology_aware_CI95,raw_p}`, `deterministic_bounds.{terms,total,decision_interval}`, `multiplicity.{raw_p,adjusted_p,rejected}`, `floor` as §3.3, `claim_evaluation.{outcome,direction,reason_codes,claim_ready_for_l2_l3,claim_level_ceiling}`, `randomization_check`, `loo.{status,rows}`, `sensitivity_status`. LOO rows use **lowercase** `metrology_aware_ci95`, plus `omitted_block_id,n_blocks,df,estimate,decision_interval,floor_status,raw_p,adjusted_p,outcome,influence_triggers`.

The per-quad a_k,b_k,d_k and t statistic are not serialized in the primary verdict. Production constructs d_k in memory (`analysis_engine.__init__._prepare_contrast_v3`/`estimators.estimate_paired_blocks`) and disclosure observation rows copy it; the lean document must retain them to make comparison auditable. Do not invent a production JSON field for them.

### 3.6 (f) Step 9b claim-side bound, and (g) descriptive magnitudes

**Claim-side bound.** Authority is PLAN L408-L410 plus `paper_claim_side_bound.md`, D-178 and D-189. This is a **copy of D and its components and both intervals**, not another bound calculation and not D plus the floor. Production `analysis_engine/claim_side_bound.py:_project` copies each contrast to schema `joulewise.claim_side_bound.v2`:

`contrast_id,source_cell_ids,floor_artifact_id,deterministic_widening_total,unit,estimator_id,ratio_estimand,deterministic_terms,metrology_aware_CI95,decision_interval`.

Unit is `J`, ratio_estimand is null, estimator id `abba_block_arm_mean_difference_t_v1`. `source_cell_ids` is the ordered concatenation of each `CV.floor.resolutions[].source_cell_ids`; preserve repeats across resolutions, never deduplicate. For these exact-stack phase groups it identifies the two model-specific aggregate cells. The ordered `(ratio form,source-cell list)` join must be injective across contrasts.

Copied JSON numerals retain **their original lexical tokens**, including exponent, trailing zeros and signed zero. Production parses numbers as opaque token records; Decimal is used for finite/nonnegative/ordered-value validation, not to recompute D or intervals. If implementing only numerical comparison, store the numeric values and additionally their source-token strings so a copy check can distinguish `4`, `4.0` and `4e0`.

D-189 non-issuance occurs if the first failed producer condition is a resolution status outside exact/transported, a null metrology or decision interval, empty deterministic terms, or absent anchor term. Emit no sidecar; represent status `not_issuable`, code `claim_side_bound_not_issuable`, and continue reported cells/disclosures. A mere outcome label `not_resolvable` does **not** imply non-issuance: an effect below a valid floor can still have complete numeric D/I/decision fields. Earlier malformed identities, joins, units, shapes or provenance remain tooling errors under `paper_claim_side_bound_*`. No default bound is manufactured (D-190 preserves legitimate nulls in step 11).

**Production record:** `CSB.contrasts[id].deterministic_widening_total` copies `CV...deterministic_bounds.total`; `.deterministic_terms` copies `.terms`; `.metrology_aware_CI95` and `.decision_interval` copy the corresponding CV objects. Step 9b's non-issuable state is recorded structurally in the dry-run record, with no CSB output.

The following are arithmetic-only **S10 checkpoints**, obtained from stored phase points and direct permitted envelope calls, not from a production sidecar. They provide a concrete target for D-189's copied numbers. Each n=9, df=8, t*=2.306, interpolation term=0, drift term=1.0440031334189257 J. Ordinary binary64 rounding applies.

| Quantity | GAMMA decode | GAMMA prefill-p2048 |
|---|---:|---:|
| dbar J | -1.0844937583414678 | 4.336251745727861 |
| sd J | 16.02153721926087 | 30.464868906699763 |
| se J | 5.340512406420291 | 10.154956302233254 |
| t statistic | -0.2030692330267231 | 0.42700841014689966 |
| raw p | 0.8441507365183523 | 0.6806329375903751 |
| anchor D component J | 1.7202261542629798 | 1.802156582333815 |
| total D J | 2.7642292876819052 | 2.8461597157527407 |
| I lower J | -13.399715367546658 | -19.08107748722202 |
| I upper J | 11.230727850863722 | 27.753580978677743 |
| decision lower J | -16.163944655228562 | -21.927237202974762 |
| decision upper J | 13.994957138545628 | 30.599740694430484 |

**Descriptive magnitudes.** Authority PLAN L479-L490. For the same kept GAMMA quads, log ratio rho_k=`log(b_k/a_k)` requires positive side means. rho=`statistics.fmean(rho_k)`, srho=`statistics.stdev(rho_k)`, half=`T975[n-1]*srho/sqrt(n)`. Ratio=`exp(rho)` and limits=`exp(rho-half),exp(rho+half)`. No timing bounds enter this descriptive interval. Nonpositive side mean or n<2 gives not-computable, not a guessed ratio.

Per-token descriptive difference is dbar/512 for decode or dbar/2048 for prefill; divide **both** I and the decision interval by the same constant. It is separate from the reported-cell ratio-of-totals. Preserve the gross-energy interpretation: energy includes baseline power over the phase, and a longer phase can account for part of the difference. It licenses no new test or claim.

**Production record:** `DISC.contrasts[]` rows identified by `(line,contrast_id)`: `magnitude_ratio` has `log_mean,log_sd,ratio,lower,upper`; `magnitude_per_token` has `value_j,denominator,metrology.{lower,upper},decision.{lower,upper}`. `gross_energy` is a fixed sentence. No mean-of-ratios replacement of the reported-cell estimand is permitted.

### 3.7 (h) Numeric disclosures and the supplementary b sensitivity

Authority PLAN L499-L644, especially L526-L565 and L573-L588. These are descriptive outputs; none replaces a primary estimate.

**Load-correlated exclusions.** LOAD is exactly `{thermal.os_level_nonzero,thermal.powermetrics_pressure_elevated,contention.request_overlap}`. Trigger a line when any dropped unit's codes intersect LOAD. Restore a dropped unit only if its nonempty complete code set is a subset of LOAD; any other removal reason keeps it dropped. Recompute reported cells with §3.1 and primary minimum 5. On GAMMA, production recomputes dbar, sd,se,t*,I only, by §3.5 steps through I; no Holm, D or outcome is emitted for this line. A typed refusal in a restored-member calculation becomes that line's `status="refused",code`, not a failure of all disclosures. A trigger with no restorable unit emits “no unit restored” and an empty values object. The fixture has no LOAD flags, so no such production lines; represent the lean line as `status="not_triggered"`, not a zero-valued sensitivity.

Production mapping: `DISC.cells[line=load_correlated_cell,cell_id]` has `restored_counts,families,values.{status,mean_j,h_j,B_j,lower_j,upper_j}` when computed; `DISC.contrasts[line=load_correlated_contrast,contrast_id]` has `restored_count,families,values.{status,n,mean_j,s_d,se,t_star,lower_j,upper_j}`. The latter's scope relative to the plan is a question in §6.

**Battery-assist cells.** Count kept member ids carrying `battery.assist` separately in repeat and quad strata. `battery.assist_outside_request` never counts. Remove every kept unit containing at least one assist member, including the entire quad. Recompute the same reported estimator with no primary minimum constraint: >=2 units in each stratum uses the table in §3.1, even below 5; one remaining unit in a stratum gives only `0.2*fmean(repeats)+0.8*fmean(quad means)` with no interval; zero in either gives not-computable. Do not fill an undefined sd or CI with zero. Print both primary and without-assist values, n and counts; a below-5 result is explicitly labelled and decides nothing.

Production mapping: `DISC.cells[line=battery_assist_cell,cell_id]`: `primary`, `without`, `n_r,n_b,assist_members.{repeat,quad},removed_unit_ids`. Computed primary/without value objects have `status,mean_j,h_j,B_j,lower_j,upper_j`. S10 has zero assist members, empty removed ids, and without equals primary exactly.

**Battery-assist contrasts.** Remove kept quads holding any assist member. Apply §3.5 through I only (no D, floor, Holm or outcome). n>=2: compute mean/sd/se/rounded t*/I; n=1: mean only/status `one_quad`; n=0: status `not_computable`. Explicitly label below 5. Production mapping: `DISC.contrasts[line=battery_assist_contrast,contrast_id]` has `status,n,mean_j,s_d,se,t_star,lower_j,upper_j,assist_quads,assist_members`. S10 has no assist quads, n=9, same dbar and I as primary.

**Cross-window consistency.** For each model/target phase, use that model's GAMMA side means a_k or b_k. G=`fmean(side means)`, hG=`T975[n-1]*stdev(side means)/sqrt(n)`. F is the floor-pack reported **mean**, hF its h **without B**. Delta=`G-F`; agree iff `abs(Delta)<=hypot(hG,hF)`, equality included. Do not pool windows or compare the two floor-pack means to make a contrast. Production mapping: `DISC.cells[line=cross_window,pack,cell_id]` has `G_j,h_G_j,F_j,h_F_j,delta_j,agree`.

**Decision interval against floor.** Near endpoint=`decision.lower` for estimate>=0, otherwise `-decision.upper`. “Beyond floor” iff near>F. Production emits the concern text only if `abs(estimate)>F` and near<=F. Mapping: `DISC.contrasts[line=decision_floor,contrast_id]` has `decision_interval,floor_j,estimate_j`; near/beyond/concern are derived from those fields and text, not serialized numeric fields. Null floor/interval remains null and prints its registered state.

**LOO magnitude.** For each primary LOO row having `estimate_magnitude`, movement=`abs(loo.estimate-primary.estimate)`. Sort by numeric block number for display. Production mapping: `DISC.contrasts[line=loo_magnitude,contrast_id].rows[] {block_number,movement_j}`; `loo_counts` has `count,exclusive_block_numbers`. The fixed prose says direction/floor/multiplicity are unchanged; see §6 for a qualification when verdict and magnitude triggers coexist.

**Floor composition and attribution.** Map `DISC.floors[line=floor_composition,cell_id]` to `guarded_j,allowance_j,source,drift_widened_j,minted_j`. `guarded_j+allowance_j==drift_widened_j` is checked exactly. `DISC.cells[line=attribution_floor,cell_id]` has `value_j,attained_by,minimum_j`. These use the primary values, not sensitivity replacements. Decision and dominance diagnostics retain the “point diagnostic; no interval” label.

**Other numeric/structural §8.1 disclosures.** Retain kept/removed unit ids, stage positions and removal codes/families from the input records alongside each estimate; the normative code-family catalog is `configs/campaigns/v5_claim_25g83/flag_catalog.json`. Attempt history, arm/hazard readings, monitor CPU time/probe counts, clock-bound maxima, NEG-8 reference omissions/counts and battery-stage temperatures are structural/monitoring disclosures, not new phase-energy estimators. If included in results.json, copy the available input readings under `disclosures.structure` with their units and source path/field; never compute a “correction” from them. Do not fetch other attempts or external journals. This specification's key-by-key numeric comparison scope is the §8.1 estimator lines explicitly defined above, with original input structural records retained for audit.

**Production step-11 supplementary calibration sensitivity.** Although not named in PLAN §§4–8, `b5_analysis/sensitivity.py` also emits `joulewise.b5_bracket_sensitivity.v1`; retain it for complete numerical comparison. Derive T=max(terminal ledger sequence)=424 on S10; require archive ledger copies to agree on their shared prefixes. Start Bmax at the maximum Decimal bound over the 24 issued acceptance members. Consider ledger **observation** rows (not append-intent control envelopes) with 376<sequence<=T, the same `identity_epoch`, disposition `valid` or `systematic-invalid`; take the maximum of `exact_bound_lexeme_s` in Decimal. On ties retain the earlier attaining observation according to ledger order; when the maximum is an acceptance member, locate its matching <=376 observation if present. Convert the chosen maximum to float once. Do not open historical capture files.

S10 Bmax is 0.06271744938655198 s, attained at sequence 412, T=424; acceptance-only maximum is 0.03646286164497997 s. Terminal archive sequences are 392,408,424. For each window b_sens=`max(b_op,Bmax)` (Decimal comparison, float output), so all three S10 windows use 0.06271744938655198 s in the sensitivity pass. Do **not** add 0.014531 again to Bmax. Keep primary b unchanged.

Recompute envelopes, D-124 widths, floors and reported bounds under each b_sens, keeping energies, units, A, mean, h, sd, se and p unchanged. Recompute GAMMA D under its wider bound and evaluate decisions using the corresponding wider model floors. Recompute family decisions/LOO as in §3.5. Primary source-floor eligibility remains the registered one. For null/refused primary states, null stays null. This pass issues no new primary projection, mint or claim.

`SENS.b_max.{value_s,attained_by_sequence,T}`, `.windows[pack].{b_op_s,b_sens_s,widened}`, `.reported_cells[] {pack,cell_id,status,primary,sensitivity,...}`, `.floor_cells[] {pack,cell_id,primary,sensitivity,...}`, `.contrasts[] {contrast_id,floor_cell_ids,primary,sensitivity,...}` are the comparison fields. Reported value objects contain `mean_j,h_j,B_j,lower_j,upper_j,attribution_floor_j`; floor objects `floor_abs_j,floor_cmp_j,floor_gate_j,allowance_j`; contrast objects `floor_abs_j,floor_cmp_j,floor_gate_j,D_j,outcome`. Preserve `equals_primary`, `not_below_primary`, `mean_and_half_width_equal_primary`, `bound_independent_values_equal_primary`, `outcome_equals_primary` where applicable. Refused p42 rows contain `status,code` instead. The driver first runs a no-widening identity check using Bmax=0 but does not retain that separate trial as another output.

### 3.8 (h) Whole-machine §8.2 cross-check

Authority: PLAN L646-L693. Production computes it **only when `withheld/meter.json` exists**; all three S10 archives have `meter.absent` and no meter record. Output the state `absent` and the boundary text, not empty numerical means or an estimate derived from processor rails alone.

For a present record, read every `members[run_id]`, including removed science/reference members: `rail_delta_J`, `machine.delta_J`, `rho`, and `machine.battery_available`. These are request-span values, not phase estimates. Group by model using registered member configs, with GAMMA side membership only for its science quads. The reference model is a separate model group. A member is plausible iff finite rho, `0<rho<=1`, finite rail/machine deltas and `machine-rail>=0`. Report all outliers with its member-level and window-level meter flags; exclude none from claims.

For all finite rhos in a model/window, compute median, min, max, q25/q75. Quantile q uses sorted values and position `(N-1)*q/100`, with linear interpolation `v_low+(v_high-v_low)*(position-low)`; use q=25,75. For plausible rhos, spread=`(max-min)/median`; <=0.2 means consistent. In chronological window order, the first per-model clean window (no window meter flags and no member `meter.battery_activity`) with plausible members sets central [min plausible,max plausible]. Count later finite members inside it inclusively; never filter them by that band. If no clean window, central band remains null.

Production `DISC.window_lines[pack]` selects `line=machine_member` rows with `model,run_id,rho,rail_j,machine_j,removed,plausible,meter_flags,battery_term_available`; `line=machine_summary` has `model,median,minimum,maximum,q25,q75,spread,central_band.{pack,plan_id,attempt,lower,upper}` when computable. The later-window inside count is in rendered text, not a separate numeric JSON field. `machine_absent` and `machine_boundary` are text-only rows. Always retain: “whole-machine DC input plus the battery term, measured at the USB-C input; the adapter's AC-to-DC loss is not included.”

## 4. Proposed single-document output and comparison map

The lean program writes one `results.json`, schema `b5-lean.results.v1`. It does not emit a custody tree or fabricate hashes/receipts. Keys are stable; arrays from production are indexed by identities, not their position. All four primary target cells, four model/phase aggregate floors, twelve dominance ratios and two contrasts must be represented. Also represent both p42 reported cells and all four p42 floor components as refused. Preserve null and refusal states. Use sorted object keys when serializing; never round stored result floats for display.

This is a schema description, not example JSON with fabricated numeric values:

| Top-level key | Contents and required child keys |
|---|---|
| `schema_version` | Exact string `b5-lean.results.v1` |
| `source` | `code_commit`, `fixture="SYNTHETIC S10"`; relative archive identities; no production path |
| `windows[pack]` | `pack_id,plan_id,attempt,b_op_s,neg8_source,allowance_j,member_allowance_j,reference_counts`, and `units[cell_id].{kept_repeat_ids,kept_quad_ids,dropped_units}` |
| `members[pack][run_id][phase]` | `energy_j,output_tokens,prompt_tokens,anchor_j,interpolation_j,member_drift_j,envelope,residual_anchor_j` when required; never force a removed missing bundle to exist |
| `reported[pack][phase]` | phase keys `decode,prefill_p42,prefill_p2048`; `cell_id,status,refusal_codes`; successful rows additionally `mean_j,lower_j,upper_j,n_bundles,independence_units,interval,per_token,attribution_floor,attribution_floor_composed,kept_units,removed_units`. `interval` and `per_token` copy the field vocabulary in §3.1. |
| `floors[pack][phase][form]` | form `absolute,comparative`; `cell_id,status,refusal_codes,n,values_j,deviations_j,mean_j,sample_stddev_j,t_critical,prediction_component_j,max_abs_deviation_j,point_j,corner_enumeration_j,linear_extreme_j,corner_widened_j,unguarded_j,guard_factor,guarded_j,allowance_j,drift_unguarded_j,drift_guarded_j,widths_j`; null numerical result fields on refusal, with the exclusion kept count separate |
| `floor_blocks[pack][phase][block_id]` | `position_run_ids,delta_j,onset_sweep_j,offset_sweep_j,zero_point_contrast_j,bundle_residual_half_widths_j,member_window_bounds_s,member_envelope_integral_sum_j,shared_width_j,local_width_j,width_j`. Preserve sweep order. |
| `aggregate_floor` | `artifact_id,cells[aggregate_cell_id].{floor_abs_j,floor_cmp_j,floor_gate_j}`, `contrasts[contrast_id].{status,floor_abs_j,floor_cmp_j,floor_gate_j,resolutions}`, and optional six-decimal diagnostic strings separately |
| `dominance` | `independent[aggregate_cell_id][form]` and `common_mode[aggregate_cell_id]`, each `status,n,numerator_j,denominator_j,ratio,threshold,passes,refusal_code`; `all_independent_pass,all_required_common_mode_pass,branch,dominance_sentence_licensed,subtitle_licensed` |
| `contrasts[contrast_id]` | `sampling,observations[block_id].{position_run_ids,a_mean_j,b_mean_j,d_j},estimator,deterministic_bounds,floor,test.{t,raw_p,adjusted_p,rejected},claim_evaluation,randomization_check,loo.{status,rows[omitted_block_id]}`. Estimator/D/claim fields use the exact production vocabulary in §3.5. |
| `claim_side_bound` | `status,refusal_code,contrasts[contrast_id]` with the §3.6 fields, and `number_tokens[contrast_id]` for copied numerals; nonissuable has no fabricated contrast values |
| `descriptive[contrast_id]` | `ratio.{status,log_mean,log_sd,ratio,lower,upper}`, `per_token.{value_j,denominator,metrology,decision}` |
| `disclosures` | `battery_cells[pack][phase]`, `battery_contrasts[contrast_id]`, `load_cells[pack][phase]`, `load_contrasts[contrast_id]`, `cross_window[pack][phase]`, `decision_floor[contrast_id]`, `loo_magnitude[contrast_id]`, `floor_composition[component_id]`, and `structure` as defined in §3.7; explicit `not_triggered` for absent load lines |
| `machine[pack]` | `status`, `members[run_id]`, `models[model]`, `boundary`; status absent on S10, numerical collections empty/null |
| `bracket_sensitivity` | Same numeric shape as SENS in §3.7, using identity-keyed maps instead of lists |
| `spec_discrepancies` | The applicable §6 identifiers; these annotate results, never silently switch formulas |

Use status `computed`, `refused`, `not_computable`, `not_triggered`, `not_issuable`, or `absent` in their defined contexts. A refusal does not introduce zero placeholders. Derived audit fields without production serialization are still emitted but are labelled `derived` in the comparison adapter.

The production comparison adapter, implemented independently of lean arithmetic, uses this mapping. `row(id)` means select exactly one matching object, not a numerical array subscript. The aliases resolve to actual hashed filenames by §3.0.

| Lean key / suffix | Production file and field, or explicit derivation |
|---|---|
| `windows[p].b_op_s` | BR(p) `.evaluation.b_fiducial_s`; source shortcut `withheld/bracket-evaluation.json.assessment.b_fiducial_s` |
| `windows[p].allowance_j` / `member_allowance_j` | ER(p) cell `.whole_window_drift_allowance.allowance_j`; member value is that /2; source rescreen bracket path in §1.5 |
| `windows[p].units[c]` | Input exclusions `.cells.row(c).kept_units,dropped_units`; step-3 kept record supplies counts, not a new exclusion policy |
| `members[p][r][phase].energy_j` | ER(p) applicable cell `.members.row(bundle_id=r).metric_value_j`; for GAMMA derived from input phase point (CV serializes identities, not member energies) |
| `members…anchor_j,envelope` | ER(p) member `.operative_anchor_envelope.{max_abs_delta_j,…}`; GAMMA not separately serialized; included in CV deterministic averages |
| `members…interpolation_j,member_drift_j` | Derived from phase precheck and A/2; not standalone CV member fields |
| `reported[p][phase].mean_j,lower_j,upper_j,n_bundles,independence_units` | PROJ(p) `.cells.row(cell_id).same_field` |
| `reported…interval.*` | PROJ(p) `.cells.row(cell_id).interval.*`, including all eight census/scatter/width fields and named kind averages |
| `reported…per_token.*` | PROJ(p) `.cells.row(cell_id).per_token.*`, including strata totals |
| `reported…attribution_floor.*` | PROJ(p) `.cells.row(cell_id).attribution_floor.*`; max also `.binding.attribution_floor_j` |
| `reported…status/refusal_codes` | Presence in PROJ(p) `.cells` means computed; `.refused_cells.row(cell_id).code` means refused |
| `floors…n,mean_j,deviations_j,sample_stddev_j,t_critical,prediction_component_j,max_abs_deviation_j` | ER(p) `.cells.row(component_id).floor.same_field`; comparative mean is still `mean_j` in ER |
| `floors…widths_j` | ER(p) `.cells.row(component_id).floor.admissible_half_widths_j` |
| `floors…point_j` | max of ER `.floor.max_abs_deviation_j,prediction_component_j`; optional `.point_floor_diagnostic.unguarded_floor_j`; CLOSE denominator is an independent serialized comparison |
| `floors…corner_enumeration_j,linear_extreme_j` | Derived only by the §3.2 formulas; no distinct production fields |
| `floors…corner_widened_j,unguarded_j,guard_factor,guarded_j` | ER `.floor.corner_widened_unguarded_floor_j,unguarded_floor_j,guard_factor,guarded_floor_j` respectively |
| `floors…allowance_j,drift_unguarded_j,drift_guarded_j` | ER `.floor.whole_window_drift_allowance_j,drift_widened_unguarded_floor_j,drift_widened_guarded_floor_j` |
| `floors…status,refusal_codes` | ER `.extractable,.refusal_reasons`; `.floor_conditions` is a label, not a terminal refusal |
| `floor_blocks…` sweep/residual/window/integral inputs | DR `.cells.row(aggregate_cell_id).comparative.common_mode_replay.inputs.blocks.row(block_id)`; block identity/membership wrappers may add hashes, but raw field names are those in §2.4 |
| `floor_blocks…shared_width_j,local_width_j` | DR block `.derived_split.{shared_width_j,local_width_j}`; final w is ER `.floor.admissible_half_widths_j` at the matching kept block position |
| `aggregate_floor.cells[c].*` | AF `.cells.row(c).floor_abs_j,floor_cmp_j,floor_gate_j` |
| `aggregate_floor.contrasts[c].floor_gate_j` | CV `.contrasts.row(c).floor.active_floor_j`; same abs/cmp/status/resolutions map by name |
| `dominance.independent[c][form]` | CLOSE `.independent_ratios.row(cell_id=c,component=form)`; numerator `.corner_widened_unguarded_floor_j`, denominator `.point_unguarded_floor_j` |
| `dominance.common_mode[c]` | CLOSE `.comparative_common_mode_ratios.row(cell_id=c)`; numerator `.common_mode_corner_widened_unguarded_floor_j`, denominator `.point_unguarded_floor_j` |
| `dominance…n` | RT `.ratios.row(ratio_id,cell_id,component).n`; explicit operands also `.numerator_j,.denominator_j` |
| `dominance.branch,all_*,*_licensed` | CLOSE same top-level fields |
| `contrasts[c].sampling,estimator,deterministic_bounds,floor,claim_evaluation,randomization_check` | CV `.contrasts.row(c).same_object`; sd field is `.estimator.s_d`, not `sample_stddev` |
| `contrasts[c].test.raw_p,adjusted_p,rejected` | CV `.contrasts.row(c).multiplicity.same_field`; raw p also `.estimator.raw_p` |
| `contrasts[c].test.t` | Derived `.estimator.estimate/.estimator.SE_total`, with zero-SE rule; not serialized |
| `contrasts[c].observations` | Derived from registered kept member points/positions; not serialized as numeric block rows in CV |
| `contrasts[c].loo.rows[k].*` | CV `.contrasts.row(c).loo.rows.row(omitted_block_id=k).*` |
| `claim_side_bound.contrasts[c].*` | CSB `.contrasts.row(c).*`; total/terms/intervals are exact numeral copies of CV as §3.6 |
| `claim_side_bound.status/refusal_code` | CSB present = issued; otherwise dry-run record step 9b `status=outcome_class,refusal=claim_side_bound_not_issuable` means not issuable |
| `descriptive[c].ratio.*` | DISC `.contrasts.row(line=magnitude_ratio,contrast_id=c).*` |
| `descriptive[c].per_token.*` | DISC `.contrasts.row(line=magnitude_per_token,contrast_id=c).*` |
| `disclosures.battery_cells/load_cells/cross_window` | DISC `.cells` rows selected by `line=battery_assist_cell/load_correlated_cell/cross_window`, pack and cell id; child fields per §3.7 |
| `disclosures.battery_contrasts/load_contrasts/decision_floor/loo_magnitude` | DISC `.contrasts` rows selected by the corresponding line and contrast id, child fields per §3.7; near/beyond and absent-load status are derived |
| `disclosures.floor_composition` | DISC `.floors.row(line=floor_composition,cell_id)` |
| `machine[p].members/models` | DISC `.window_lines[p]` selected by `line=machine_member/machine_summary`; absent state by `machine_absent` |
| `bracket_sensitivity.*` | SENS same fields after converting lists to identity-keyed maps; also copied into DISC `.sensitivity` |

Compare identity/count/status/boolean fields exactly. Compare unrounded numerical values at binary64 rounding tolerance, recording both absolute and relative difference; for an initial portable comparator use `rel_tol=1e-12,abs_tol=1e-12`, with no tolerance for null versus number, missing versus zero, or different outcome/ceiling. D-124 outward padding is part of the value even when it falls below that comparison tolerance. A stricter same-interpreter comparison may use `.hex()` equality. Check CSB numeral-token copy equality separately. A disagreement near any decision boundary requires examining operands, not widening the tolerance. Never compare rounded text as the numeric authority.

## 5. Independence fence for the implementers

The implementers receive this specification and the synthetic inputs. They may read the normative plan, registration, the two named paper contracts, data JSON/CSV/JSONL, and the **numerical functions/files scoped in §2 only**. They may implement all §2 formulas themselves. They must implement the reported estimator, claim estimator, Holm, outcome/ceiling logic, disclosures and output composition independently from this document.

Do **not** read or call these production glue/estimator sources while implementing (in addition: `joulewise/detection_floor.py`, `joulewise/floor_extraction.py`, `joulewise/dominance_closeout.py`, per the lead permission summary of §2; `scripts/independent_recompute_b5.py`, `scripts/compare_b5_recompute.py`, `scripts/b5_e2e_synthetic.py`, `tests/b5_analysis/`, `tests/independent_recompute/`, `docs/run_reports/`, `docs/process_traces/` other than the two authority files named in §0):

- `scripts/run_b5_analysis.py`; all `joulewise/b5_analysis/*` (including `dry_run.py,bracket.py,context.py,kept_units.py,windows.py,archive.py,steps.py,runner.py,parallel.py,disclosures.py,sensitivity.py`, whether or not every basename exists at this commit).
- `joulewise/analysis_engine/{__init__,inputs,estimators,claims,multiplicity,sensitivity,artifact,registry,ratio,claim_side_bound}.py`. The distribution primitives alone are allowed by §2.3. The D-189 copier must be rebuilt from §3.6, not reused.
- `joulewise/paper_reported_energy.py`, `joulewise/paper_reported_energy_issuer.py`, `joulewise/paper_custody.py`, other paper custody/supply/rendering adapters, `joulewise/floor_mint_estimator.py`, and the mint's original-core/wrapper implementations.
- `joulewise/whole_window.py`, calibration bracketing/ledger discovery, authentication I/O/session code, archive/source stores, `joulewise/analysis_verified_store.py`, deadline wrappers, and store/cache worker plumbing. §2's permitted functions may import dependencies; do not inspect or invoke these as analysis entry points. Recorded b/A are the lean input boundary.
- Program wrappers `scripts/{extract_detection_floors,emit_floor_mint_pinset,mint_floor_artifact_generalized,finalize_analysis_manifest,run_d165_closeout_from_custody,build_d165_dominance_closeout,issue_reported_energy,produce_b5_disclosures,build_results_fill_input,render_results_fills}.py`, `joulewise/cli.py`, the `python -m joulewise analyze-claims` entry point, and production test expected outputs or existing implementations of a lean pipeline.

For clarity, §2 (as narrowed by the lead permission summary) permits only these repository code files, within their stated numerical scope: `joulewise/bundle_read.py`, `joulewise/reduce.py` (`_integrate`, `_corner_composed_anchor_shift_envelope`), `joulewise/aggregate.py` (`student_t_critical_95`), `joulewise/analysis_engine/distributions.py`. Referencing a forbidden file's code location in this specification documents the provenance of a rule; it does not authorize the implementer to open that file. No custody/authentication result from lean is a production issuance claim.

## 6. Open questions and possible production/plan disagreements

These are questions for the lead/results cold gate. No correction is authorized or made here. The comparison behavior specified above remains explicit.

1. **Q1 — NEG-8 allowance enters the floor. RESOLVED by RULING J5 (lead):** the cold judge ruled that the minted floor is `drift_widened_guarded_floor_j` = guarded operative floor + the floor window's whole gross allowance, that PLAN L133-L135 is wrong and is corrected by addendum (corrected sentence at RULING J5(d)), and that the dominance ratios and the attribution floor do not carry the allowance. Production follows the ruling; this is not a discrepancy. Original draft text kept for the record:  PLAN L134-L135 says a floor's value does not use the drift allowance; PLAN L295-L317 defines point/corner/guard without adding it. Production `floor_extraction.py:CellReport.as_row` (L1459-L1533), `detection_floor.py:_add_whole_window_drift_allowance` (L1496-L1538), `build_floor_cell` (L1818-L1836), and `emit_floor_mint_pinset.py:_postcollection` (L57-L84) add full A after guarding and use that number in the mint. The step-11 disclosure even states each contrast's floor carries the floor window's allowance, while its decision interval carries GAMMA's (`disclosures.py:_energy_lines`). Is that a deliberate later amendment, or a production estimator divergence? It materially changes the floor and floor gate; lean must retain both G and G+A for adjudication.

2. **Q2 — “identically” applied D-124 treatment on the consuming contrast.** PLAN L316-L317 and L334-L336 say shared-edge treatment transfers identically to the contrast; the prospective manifest records `consuming_contrast_treatment=two_shared_edges_plus_bundle_specific_adversarial_terms`. Yet `analysis_engine/__init__.py:L675-L721` forms D by adding the full operative member bounds on the two sides, and `inputs.py:deterministic_bounds` takes phase `max_abs_delta_j`; it does not invoke the D-124 sweep for GAMMA's deterministic claim bound. This agrees with the explicit conservative sum in PLAN L408-L410. Does “identically” refer only to floor eligibility/transfer rather than claim-side D, or is there an unresolved policy/code conflict? Lean comparison uses the conservative sum and keeps the distinction visible.

3. **Q3 — Load-correlated contrast sensitivity's extent.** PLAN L530-L535 asks for the same estimator over the units that would be kept, with no explicit restriction to steps 1–4. Production `disclosures.py:_energy_lines` (load-correlated contrast branch, around L520-L544) emits `_paired_values` only: mean/scatter/SE/rounded-t metrology interval, with no deterministic D/decision interval or Holm/outcome. The battery-assist contrast line is expressly restricted to steps 1–4 by PLAN L558-L561, but the load line is not. Confirm the intended disclosure scope. S10 has no LOAD-coded removals, so this does not change its numbers.

4. **Q4 — Unqualified LOO magnitude sentence.** PLAN L583-L584's fixed sentence says direction, floor status and multiplicity are unchanged. Production `disclosures.py:L586-L605` prints that sentence for every row containing `estimate_magnitude`, even when the same row also contains a verdict trigger; `analysis_engine/sensitivity.py:influence_triggers` permits both. Should the prose be conditional on absence of verdict triggers? Numerical triggers/movement must remain as computed. This is a wording issue unless such a row exists.

5. **Q5 — Equality evidence for the older harvest bracket shape.** PLAN L234/L313 names the bracket's recorded b; production `b5_analysis/bracket.py:evaluate_window_bracket` re-evaluates all shapes but only enforces exact comparison to harvested assessment for governed erratum-3 windows. S10 ALPHA is the older shape. Its recorded endpoint/allowance arithmetic agrees with the formula, and BETA/GAMMA have the explicit equality gate, but no full replay was executed during this specification task. The lean shortcut is justified numerically at the recorded boundary, not claimed as independent authentication of the old harvest. A later isolated comparison should confirm ALPHA's b against production's BR output without exposing real data.

6. **Q6 — Supplementary block-maximum sensitivity authority. RESOLVED (lead):** b_sens is registered by trigger-erratum E3 item 14 and its scope is fixed by RULING J6 (each window under its own b_sens(W); both floor forms recomposed into `floor_gate_j` with the same allowance; GAMMA's D re-derived under b_sens(GAMMA); one sensitivity outcome word per contrast). Original draft text kept for the record:  Production step 3b/11 computes Bmax and b_sens, including same-epoch systematic-invalid observations, and emits the additional SENS numbers. There is no `B_max`/`b_sens` estimator in the cited PLAN §§4–8; the primary plan instead specifies each window's own b (PLAN L234,L313). This draft treats SENS as a separate production comparison output, never a replacement of primary estimates. The lead should supply the owning later erratum/ruling if it is to be presented as preregistered rather than supplementary.

Two resolved numerical clarifications are **not** bugs: PLAN L228's decimal 0.04/0.64 is algebraic prose while the D-179 contract explicitly pins `0.2**2`/`0.8**2`; PLAN L229-L232 abbreviates some exact t literals and delegates the frozen values to L9. Similarly the floor delta and claim delta have different canonical evaluation orders by PLAN L298 and L389. Preserve these distinctions rather than “fixing” them.

## 7. Verification record and next comparison

Drafting checks were limited to low-priority reads and tiny arithmetic snippets. HEAD was verified as `929fc65c9`; the checkout initially had no changes. Reads stayed in the checkout and permitted synthetic extraction. No production restricted tree, external custody, real window, test suite, full reducer, or end-to-end pipeline was opened/run. The process was already at niceness 20; `nice -n 19` reported a denied priority reset but commands remained at the lower scheduling priority. Python imports used `PYTHONDONTWRITEBYTECODE=1`.

Direct evidence: parsed each archive's exclusions/roster/allowance/bracket records; inspected representative trace/metadata/event/spec membership; confirmed all three meter records absent and no assist/LOAD flags; recomputed the four reported m/s/V/h checkpoints from stored phase energies; evaluated only the permitted envelope kernel for kept GAMMA phase members and computed the §3.6 D/CI/p checkpoints; read ledger scalar bounds to establish Bmax/T. Floor enumeration, R/Rcm and complete output equivalence remain **unexecuted**, not “passed”.

Next exact step: give this file and synthetic input roots to each independent implementer, have each write the specified `results.json`, then perform a separate lead-controlled numerical comparison against the production output roles/fields in §4. Resolve Q1/Q2 before interpreting any scientific floor/claim sentence. Retain every discrepancy and every null/refusal as a comparison result; do not repair production in the lean implementation.
