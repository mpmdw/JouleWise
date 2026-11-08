# FIX-416-A implementation and executed evidence

Changes remain uncommitted at c84bb34c2cbbb03fada07fad61d48f0f328dfcad on `fix/2026-10-24-416-analysis`. The lead applies the registration sentences below and reviews/commits. No registration text, flag catalog, pack flag effects, hazard/clock policy, identity runtime fields, or blinding/resolution code was changed. Real archives were read-only inputs. No measurement, model load, system-state command, shared-index write or whole-repository suite was run. All retained campaign evidence is synthetic.

All commands below run from `/Users/edr/code/jw-wt/fix416-analysis`. `E` expands exactly to:

```sh
env TMPDIR=/private/tmp/fix416a/round2 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B
```

The before evidence in `.scratch-416A/` was executed in round 1 under the equivalent `/private/tmp/fix416a/run` TMPDIR. Final evidence is under `.scratch-416A/round2/`.

## Decisions I made

1. Whole request means tokenize `phase_start` through decode `phase_end`, including every gap. Neither the measured-run stage, sampling marker window, nor a sum of phase durations is substituted.
2. The existing export's `gross_energy_j` and `idle_subtracted_energy_j` cover sampling_started through sampling_stopped. They are not exact request integrals. Add independent exact request columns, leaving those existing summary columns intact. All stages and both implementations use the new columns for reference rails energy and duration; released DC/battery/rest references use that same request span. Missing exact columns do not silently fall back to a different span: old exports need re-export from their immutable archives.
3. Missing `test7_passed` retains the registered false default; any explicit value other than boolean false is refused. No session may opt into an unestablished pass-1 test-7 regime.
4. Authenticate the canonical registered manifest's bytes against §4's pinned digest, then compare each supplied numeric predictor by registered model identity. Session locations and public configuration keys are fixture metadata, not predictor overrides. Arithmetic-only fixture subsets retain their prior supported use.
5. Flagged-inclusive restores valid records with any catalog/NUMBER exclusion. Exactly the seven §6 invalid-energy conditions remain invalid; no prefix-wide veto survives.
6. Apply F2 exactly: adjacent samples union samples within inclusive ±r_max; multiply by r_max + Δt. The expanded residual window also survives the analysis's filtered reader.
7. Detect device-counter drops before the BYTES energy join. The generic mean-times-duration integrator has no counter and also serves irregular battery polls, so it remains unchanged. A failed DC value removes the whole affected DC/rest sampling unit; rails stays eligible. Gaps are checked at the half-open energy span, including missing samples at its first/last edges.
8. Apply the supplied bars directly in each printed field's unit, without relative defaults or formula propagation. F3 diagnostics have difference counts and no acceptance tolerance; their effects still pass through h, B, intervals and coefficients.
9. No decode-envelope anchor column exists in the export; item 9's optional change and M12 kill are not applicable. The existing whole-window bound is not relabelled as a decode envelope.
10. Reissue through the existing plan-tree generator and BY-INTEGRATE/BY-P6-B3 hash issuer operations, restricted to authorized generated trees/estimator versions, tree hashes, and their downstream source-container bindings. Draft gates and all other identity fields stay intact.

## Per item

### 1. Reference spans and exact export columns

[joulewise/bytes_analysis.py:479](/Users/edr/code/jw-wt/fix416-analysis/joulewise/bytes_analysis.py:479), [joulewise/bytes_analysis.py:831](/Users/edr/code/jw-wt/fix416-analysis/joulewise/bytes_analysis.py:831), [joulewise/b6/export_runs.py:98](/Users/edr/code/jw-wt/fix416-analysis/joulewise/b6/export_runs.py:98), [scripts/bytes_twin.py:555](/Users/edr/code/jw-wt/fix416-analysis/scripts/bytes_twin.py:555), and [scripts/bytes_twin.py:986](/Users/edr/code/jw-wt/fix416-analysis/scripts/bytes_twin.py:986) implement the common span. The exporter reconstructs the native interval-supported rails curve with the reducer's existing primary-evidence anchor verification and integrates its exact request endpoints; idle subtraction uses that run's idle power times the same duration. Verified calibration physics is cached per export, under the reducer's existing digest-keyed cache contract.

Before: `E /Users/edr/night-archive/seats-7209/probes/opus/a1-meter/neg8_quant.py /Users/edr/code/jw-wt/fix416-analysis /Users/edr/night-bytes/h2-20261023T144711Z/archive /Users/edr/night-bytes/h2-20261023T144711Z/export/bytes-mac-check/bytes-h2-20261023T144711843389Z-calibration.runs.csv .scratch-416A/opus-meter.before.json` retained `.scratch-416A/neg8.before.json`: old stage T_ref 8.707850422 s versus request 1.3108093057142856 s; DC E_ref 183.332605120919 J versus 97.97737850596059 J; A_DC 5.360522467577084 J versus 1.8825979913835909 J. The old blinded sum of phase durations was 1.3107811042240687 s and omitted gaps.

After: `E .scratch-416A/round2/reference_real.py` → `reference-real-both-final.log` and per-session `*.references.json`, using only status-succeeded/nonexcluded references, as the analysis does. H's excluded unresolved start reference and failed end references remain excluded. H cannot supply the complete NEG-8 endpoint set; BY-H2 provides the complete comparison. Exact request columns and both implementations' reference energy/duration/allowance agree within the registered bars; the largest allowance difference is 5.02e-8 J, versus its 0.0005 J printed-precision bar. The export tests deliberately use separated phases whose 8 s total phase duration spans a 14 s request: exact gross 140 J, secondary 98 J, duration 14 s, while existing summary gross stays 40 J. New J columns round-trip through existing blinding; durations are not scaled. BY-H2 final means are rails E_ref 37.121008004357314 J / A_gross 0.8725818631964231 J; DC-input E_ref 97.97737850624749 J / A_gross 1.8825979661437486 J; rest E_ref 60.856370501890176 J / A_gross 1.7503635685036656 J, all at T_ref 1.3108093057142856 s. For refcorpus r01 the old sampling-window rails gross is 37.142127465977815 J and the exact request integral is 37.13965434460142 J; r02 changes 37.03314485823969 J to 37.02732989881257 J. No proportional rescaling is used. The original Opus neg8_quant.py was also rerun using the scratch-only CSV with these exact new columns (`round2/neg8-after.json`); its request-labelled branch is the corrected branch, while its deliberately retained measured_run branch is the old-rule counterexample.

### 2. Production-shaped synthetic campaigns

[tests/fixtures/bytes/campaign.py:13](/Users/edr/code/jw-wt/fix416-analysis/tests/fixtures/bytes/campaign.py:13) and [tests/fixtures/bytes/twin_synth.py:92](/Users/edr/code/jw-wt/fix416-analysis/tests/fixtures/bytes/twin_synth.py:92) supply 50 SPS, rate_idx 2, 20 ms counters, five polls/s, a synthetic 0.35 s sampler-spawn interval, a 1.0 s post-window dwell and 6.0 s stop wind-down. The full campaign includes explicit interphase gaps. Defect planting follows parsed sample positions rather than a 100 ms assumption. These are synthetic timing choices, not new hardware observations.

Before/after mutation: `E .scratch-416A/agreement_span_probe.py old` restores only the old analysis measured_run span in CLI subprocesses: 3549 above-bar fields of 262311; tail `PASS old measured_run reference-span mutant detected above the bar`. `E .scratch-416A/agreement_span_probe.py request` gives 0 above of 262311; tail `PASS request-span agreement: zero above the bar`. Both full stage chains and artifacts are retained under `round2/span-probe-*`. `E .scratch-416A/fixture_shape.py` verifies header/counters and controller timing; round-2 final fixtures are independently inspected by the campaign and twin tests.

### 3. test7_passed

[joulewise/bytes_analysis.py:427](/Users/edr/code/jw-wt/fix416-analysis/joulewise/bytes_analysis.py:427) checks both validation and direct reduction ingress; [scripts/bytes_twin.py:657](/Users/edr/code/jw-wt/fix416-analysis/scripts/bytes_twin.py:657) independently refuses non-false values. `E .scratch-416A/test7_before.py` loads the old functions from the actual base commit and executes both versions: `BEFORE both readers accept test7_passed=true`; `AFTER both readers refuse test7_passed=true`. Final assertions also cover false-like integer/string/null values in the analysis.

### 4. Registered predictors

[joulewise/bytes_analysis.py:408](/Users/edr/code/jw-wt/fix416-analysis/joulewise/bytes_analysis.py:408), [joulewise/bytes_analysis.py:415](/Users/edr/code/jw-wt/fix416-analysis/joulewise/bytes_analysis.py:415), and the twin's independent manifest ingress authenticate digest `76452108c1a10b1f63b48fc95b306b6c4aa936a0d2e94244be65dc067c356264` before comparing W/KV/R and any b/GB projections. Both fixture manifests now use the exact registered numeric bytes.

Astra before: `E .scratch-416A/probe.py /Users/edr/night-archive/seats-7209/probes/astra/manifest_probe.py before` admitted doubled W and changed BW from 266.206264 to 475.327520 GB/s. Same probe after (`... round2`, log `astra-manifest.log`) exits 1 at `AnalysisError: model predictors differ from registered manifest: Qwen3-1.7B-4bit`, the expected refusal. `E .scratch-416A/manifest_after.py` checks both readers independently; tail `PASS both readers refuse all four numeric-predictor mutations and test7_passed=true`.

### 5. Twin invalid record set

[scripts/bytes_twin.py:87](/Users/edr/code/jw-wt/fix416-analysis/scripts/bytes_twin.py:87) independently spells §6's seven codes; no analysis import is shared. Tests cover every code and restore valid roster/model/NUMBER exclusions. `E .scratch-416A/round2/validity_probe.py` executes the actual base and final restorers: roster.not_in_plan, model.identity_mismatch and member.reduction_mismatch are false before and true after; member.anchor_not_bounded remains false. The earlier prefix veto is gone. Full twin/native/export run: 117 tests, OK, after correcting the old compressed fixture to include its required tokenize start.

### 6. Meter edge power

[joulewise/bytes_analysis.py:508](/Users/edr/code/jw-wt/fix416-analysis/joulewise/bytes_analysis.py:508), the filtered reader and [scripts/bytes_twin.py:866](/Users/edr/code/jw-wt/fix416-analysis/scripts/bytes_twin.py:866) implement F2. Hand-worked tests use r_max > Δt and large nonadjacent powers, and prove the additional powers enter u; adjacent samples remain included when r_max < Δt.

The original brief's superseded ±(r_max+Δt) probe had changed 97/190 H and 60/146 BY-H2 edges (retained round-1 evidence). Final F2 proof: `E .scratch-416A/round2/edge_real.py` → `edge-real.log`: H 190 edges, 0 changed; BY-H2 146 edges, 0 changed; maximum Δu is 0 for both. This is real raw-stream input, read only.

### 7. Dropped meter samples

[joulewise/external/km003c_parse.py:384](/Users/edr/code/jw-wt/fix416-analysis/joulewise/external/km003c_parse.py:384), `meter_decode`, and [scripts/bytes_twin.py:850](/Users/edr/code/jw-wt/fix416-analysis/scripts/bytes_twin.py:850) inspect exact unwrapped integer device counters, independent of host jitter. Science and reference request paths emit `bytes.meter_gap`; DC/rest alone lose the affected unit. No catalog edit was made. The replayed_batch agreement campaign exercises an actual counter gap: in each pass Llama rails retains 10 repeats and 10 quads; DC/rest remove repeat 0, retaining 9 repeats and 10 quads.

Before: Opus `fit_sensitivity.py` rerun on H (round-1 `opus-H.json`/`opus-H.log`) reproduced a 28.009406447 s, 1401-sample dropout: native integrate returns 5916.114714557086 J instead of 6101.072861976976 J, error −184.95814741989034 J, without rejecting the gap. After: `E .scratch-416A/gap_real.py` mutates only an in-memory real-H copy, confirms the same old low-level result, then gets analysis `MeterGapError` and twin `meter_gap` / `bytes.meter_gap`; tail `PASS real H in-memory dropout is detected by both implementations; source stream unchanged`.

`E .scratch-416A/probe.py /Users/edr/night-archive/seats-7209/probes/fable/parser_agree.py round2` re-executes Fable's parser/join probe. `E .scratch-416A/round2/proof_compare.py` compares it to the executed pre-change JSON: H 935345 samples/95 joins and BY-H2 761159 samples/73 joins, zero dropped or irregular counters, identical prior join results, native/filtered/twin agreement. Extra retained filter context and wall execution time are representation differences only.

### 8. Agreement bars and F3 diagnostics

[tests/test_bytes_agreement.py:210](/Users/edr/code/jw-wt/fix416-analysis/tests/test_bytes_agreement.py:210), [tests/test_bytes_agreement.py:260](/Users/edr/code/jw-wt/fix416-analysis/tests/test_bytes_agreement.py:260), and the per-table comparisons implement §12/§14: energy 1%(h+B), power 1%(h+B)/T, H2 coefficients and interval endpoints 1% HC3 half-width, durations 1 ms, VIF identical rendering to 2 significant figures; remaining printed fields have half a last-place unit (BW/b/R 0.0005, τ/drift/H1 coefficients 0.0000005, correlation 5e-10, log ratios/t quantiles 0.00005; H2 errors/C use the row's half-width decimal place). No formula-derived fallback or generic relative bar remains. The legacy fixture assertion that every individual offset bound must exceed its own cell bar is replaced by an explicit whole-column-zero mutation using the same per-row bars; it must produce an above-bar difference in each campaign, without adding a selection rule or changing any bar. Raw variance/covariance/MSE/derivatives and unprinted power/sensitivity terms are counted in separate diagnostics without tolerance or gating, including within copied output structures.

`E .scratch-416A/bar_probe.py` executes the base and final comparers: BW +0.05 GB/s and drift scale +0.00005 are under the old bars and both above the final bars (0.0005 and 5e-7). Tail `PASS Astra BW +0.05 GB/s and drift-scale +0.00005 mutations: admitted before, both above bar after`. A regression proves arbitrarily large raw diagnostic differences cannot gate while a printed mean mutation does. The retained-output coverage audit also mutates every one of the 1608 remaining declared compared fields; all are detected. Numeric and word/census regressions run in the full agreement module. The existing output-field coverage fixture moves 77 unprinted field paths into a named F3 exemption; its read-only mutation check verifies they do not gate while printed mean/coefficient mutations still do.

### 9. Optional blinded anchor column

The export carries `bound_E_clock_anchor_shift_bound_j`, which is the whole sampling-window bound, and does not carry the decode-envelope anchor term. Under the explicit conditional instruction, the blinded anchor path is unchanged and no claim that M12 is killed is made.

### 10. Rebind, regenerate, reissue and rerun

All 19 final campaigns below have zero above-bar fields before the generator binding changes. The actual final estimator SHA-256 is `76c44759c4c674100303be718ce9c4db0723d3b7ffb9549f0ad4607285b0176a`. Only `AGREED_ESTIMATOR_VERSION` changes in `scripts/bytes_plan_trees.py`; its issuer regenerates six pass-1 estimator bindings and all twelve fixed trees (the generator self-digest also changes pass-2 trees), leaving pass-2 estimator versions null and every pack draft. `.scratch-416A/round2/rebind.py` applies the existing BY-INTEGRATE/BY-P6-B3 identity issuer operations with a strict changed-path and estimator-only pack check, updates the twelve source and consumer tree hashes and only their derived source-container bindings, then loads the consumer artifact. No identity runtime/model fields change. `scripts/repin.py --write registry` refreshes the downstream registry where needed.

Full test/CLI commands and stable tails are recorded below. The full-analysis module includes the separate 60 native synthetic campaigns (20 per world), in addition to the conditional 400-draw ensemble and 19 independent-comparer campaigns.

## Nineteen-campaign table

| Campaign | Compared | Equal | Under bar | Above bar | Diagnostics | Different diagnostics |
|---|---:|---:|---:|---:|---:|---:|
| bytes | 314763 | 307505 | 7258 | 0 | 102274 | 625 |
| resident | 262311 | 256825 | 5486 | 0 | 84106 | 582 |
| time | 262311 | 256946 | 5365 | 0 | 84106 | 582 |
| defects | 269207 | 263544 | 5663 | 0 | 86430 | 586 |
| minimum | 254892 | 249072 | 5820 | 0 | 81108 | 767 |
| edge_locked | 262311 | 256944 | 5367 | 0 | 84106 | 562 |
| withheld | 218372 | 213559 | 4813 | 0 | 68146 | 678 |
| invalid_anchor | 261959 | 256399 | 5560 | 0 | 83978 | 588 |
| marker_incomplete | 20238 | 18064 | 2174 | 0 | 302 | 266 |
| late_start | 169829 | 164277 | 5552 | 0 | 51394 | 514 |
| polls_only | 20146 | 17943 | 2203 | 0 | 302 | 264 |
| header_closed | 20146 | 17846 | 2300 | 0 | 302 | 285 |
| empty_payload_n | 314763 | 307497 | 7266 | 0 | 102274 | 628 |
| replayed_batch | 314411 | 307110 | 7301 | 0 | 102146 | 643 |
| replayed_tail | 314763 | 307464 | 7299 | 0 | 102274 | 624 |
| first_batch_tail_replayed | 314763 | 307534 | 7229 | 0 | 102274 | 628 |
| compressed | 262311 | 256649 | 5662 | 0 | 84106 | 575 |
| battery_instant | 315115 | 308512 | 6603 | 0 | 102402 | 662 |
| battery_delayed | 314763 | 307784 | 6979 | 0 | 102274 | 664 |

Diagnostic differences do not gate. Their count is reported separately from printed-field agreement, as F3 requires. Disk was checked before campaigns; free space was 79–80 GiB, above the 60 GiB floor.

## Coverage: counts of 400

Command: `E tests/fixtures/bytes/coverage.py .scratch-416A/round2/campaigns/bytes 400` (stdout retained as `round2/coverage.json`). The unchanged conditional ensemble produces 36 method rows (3 worlds × 3 boundaries × 2 fits × 2 methods), each using 400 draws per world. The independent standalone run and the full analysis module agree on all coverage fractions. Minimum HC3 plain-95% coverage is **379/400 (0.9475)**; no 0.93 floor fails. Full precision, offset alternatives and SE diagnostics remain in `round2/coverage-final.json`; the final post-binding run is byte-identical to the initial independent rerun in `round2/coverage.json`.

| World | Boundary | Fit | HC3 95% | OLS 95% | HC3 ruled-k | OLS ruled-k | k |
|---|---|---|---:|---:|---:|---:|---:|
| bytes | rails | simple | 388/400 (0.9700) | 389/400 (0.9725) | 397/400 (0.9925) | 395/400 (0.9875) | 9 |
| bytes | rails | extended | 393/400 (0.9825) | 397/400 (0.9925) | 400/400 (1.0000) | 399/400 (0.9975) | 9 |
| bytes | DC input | simple | 388/400 (0.9700) | 389/400 (0.9725) | 397/400 (0.9925) | 395/400 (0.9875) | 9 |
| bytes | DC input | extended | 393/400 (0.9825) | 397/400 (0.9925) | 400/400 (1.0000) | 399/400 (0.9975) | 9 |
| bytes | rest | simple | 388/400 (0.9700) | 389/400 (0.9725) | 397/400 (0.9925) | 396/400 (0.9900) | 11 |
| bytes | rest | extended | 393/400 (0.9825) | 397/400 (0.9925) | 400/400 (1.0000) | 399/400 (0.9975) | 11 |
| time | rails | simple | 379/400 (0.9475) | 380/400 (0.9500) | 397/400 (0.9925) | 396/400 (0.9900) | 9 |
| time | rails | extended | 388/400 (0.9700) | 380/400 (0.9500) | 398/400 (0.9950) | 398/400 (0.9950) | 9 |
| time | DC input | simple | 379/400 (0.9475) | 380/400 (0.9500) | 397/400 (0.9925) | 396/400 (0.9900) | 9 |
| time | DC input | extended | 388/400 (0.9700) | 380/400 (0.9500) | 398/400 (0.9950) | 398/400 (0.9950) | 9 |
| time | rest | simple | 379/400 (0.9475) | 380/400 (0.9500) | 397/400 (0.9925) | 397/400 (0.9925) | 11 |
| time | rest | extended | 388/400 (0.9700) | 380/400 (0.9500) | 399/400 (0.9975) | 399/400 (0.9975) | 11 |
| resident | rails | simple | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 9 |
| resident | rails | extended | 398/400 (0.9950) | 318/400 (0.7950) | 400/400 (1.0000) | 394/400 (0.9850) | 9 |
| resident | DC input | simple | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 9 |
| resident | DC input | extended | 398/400 (0.9950) | 318/400 (0.7950) | 400/400 (1.0000) | 394/400 (0.9850) | 9 |
| resident | rest | simple | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 11 |
| resident | rest | extended | 398/400 (0.9950) | 318/400 (0.7950) | 400/400 (1.0000) | 398/400 (0.9950) | 11 |

## Exact registration text for the lead (do not apply automatically)

### Section 7

Replace only the sentence beginning "Per run, u =" in the meter-edge definition with:

> Per run, u = (P_start + P_end) × (r_max + Δt), where each edge power is the largest power among the two samples adjacent to that edge together with every sample whose mapped time lies within ±r_max of the edge, r_max is the largest absolute recorded excess latency of the clock fit, and Δt is the header's device-sample interval (20 ms at the recorded 50 SPS rate).

Add to the NEG-8 definition:

> Every reference's whole request runs from tokenize phase_start to decode phase_end in events.jsonl, including all gaps between phases; this same span defines T_ref and the rails, DC-input, battery and rest reference energies in every stage.

> The BYTES export carries reference_request_gross_j, reference_request_idle_subtracted_j and reference_request_duration_s, integrated on that request span; the existing gross_energy_j and idle_subtracted_energy_j retain their sampling_started-to-sampling_stopped meaning and are not reference request inputs.

Add after the unavailable-meter rule:

> A dropped device sample is an exact gap in the device's integer counter sequence, without tolerance; if a missing sample's mapped time lies in a run's half-open decode span or a reference's half-open request span, that run is flagged bytes.meter_gap and has no DC-input or rest value, with the affected DC-input/rest sampling unit removed as for bytes.meter_decode_unavailable while its rails record remains eligible.

> Every pass-1 session has test7_passed false (omission defaults to false): no regime has established a test-7 pass under P0 ruling 3, and both analysis implementations refuse any explicitly supplied session value other than boolean false.

### Section 9

Replace the coverage reproduction/minimum sentences with:

> The conditional member-redraw coverage ensemble was rerun at the FIX-416-A agreeing joulewise/bytes_analysis.py SHA-256 76c44759c4c674100303be718ce9c4db0723d3b7ffb9549f0ad4607285b0176a, using 400 draws per world and the unchanged tests/fixtures/bytes/coverage.py harness; the independent run and the full-analysis module give the same coverage counts.

> Minimum HC3 plain-95% coverage is 379/400 (0.9475), above the registered 0.93 floor; the 60 native offset campaigns remain separate evidence.

Replace all eighteen table rows with the exact coverage table above. Retain the registered formula and floor; do not silently retain the former 377/400 sentence or old table counts.

### Section 12

Clarify the final numeric-bar bullet:

> Every other printed quantity without a half-width agrees when its absolute difference is at most half a unit in the last decimal place §14 prints for that quantity; these bars are applied directly in that field's unit and are not propagated through formulas.

Add:

> Quantities for which §14 gives no printed precision, including raw variance, covariance, MSE and d_beta_d_delta_per_ms, are diagnostics rather than agreement fields: their unequal values are counted per campaign without a tolerance or acceptance gate, and their effects are checked through the printed h, B, intervals and coefficients.

Replace the production-shaped fixture parenthesis with:

> Production-shaped synthetic campaigns have full-size modules, 50 runs per model per pass, start/midpoint/end references, controller sampler-spawn latency, the 1.0 s post-window dwell and stop wind-down, gaps between request phases, and a continuous 50 SPS meter stream with rate_idx 2 and 20 ms device counters; they traverse the real harvest export and every CLI stage.

### Section 13

Add:

> Both implementations authenticate the canonical registered manifest's SHA-256 from §4 and refuse numeric W/KV/R/b overrides in analysis manifests.

Replace the old agreeing-digest / pending-propagation sentences with:

> At the FIX-416-A agreeing tree, the SHA-256 of joulewise/bytes_analysis.py is 76c44759c4c674100303be718ce9c4db0723d3b7ffb9549f0ad4607285b0176a; all nineteen synthetic agreement campaigns have zero printed fields above §12's bars, and the 400-draw-per-world coverage ensemble has been rerun at these source bytes.

> scripts/bytes_plan_trees.py binds that digest to every estimator version in the six pass-1 registrations; pass-2 estimator versions remain null, all twelve generated trees and their identity-pin tree hashes have been reissued, and every pack remains draft.

The two §18 slot-summary cells must carry the same updated facts (cross-references, not new rules):

> The coverage slot is filled by the FIX-416-A execution: §9 contains all eighteen count/fraction rows, and minimum HC3 plain-95% coverage is 379/400 (0.9475).

> The estimator slot is filled at SHA-256 76c44759c4c674100303be718ce9c4db0723d3b7ffb9549f0ad4607285b0176a, bound through the generator to all six pass-1 registrations; pass-2 versions remain null and all packs remain draft.

Retain the existing post-stage-1 module-change policy. These are exact proposed sentences; the lead owns registration edits and citations.

## Executed verification commands and tails

`E -m unittest tests.test_bytes_analysis` → `analysis-tests.log`

```text
AssertionError: 1 != 0 : BYTES analysis refused: [Errno 2] No such file or directory: '/private/tmp/fix416a/round2/tmpkwlcqro8/fit-line/configs/bytes/bytes_manifest.json'
----------------------------------------------------------------------
Ran 111 tests in 5049.425s
FAILED (failures=4)
```

`E -m unittest tests.test_bytes_analysis.Addendum7RegressionTests.test_a7_12_generated_signed_clock_latency_uses_largest_absolute_extreme` → `analysis-rate-rerun.log`

```text
.
----------------------------------------------------------------------
Ran 1 test in 86.200s
OK
```

`E -m unittest tests.test_bytes_analysis.BatteryCampaignTests.test_neg8_request_battery_correction_reaches_dc_and_rest_references` → `analysis-reference-rerun.log`

```text
.
----------------------------------------------------------------------
Ran 1 test in 68.569s
OK
```

`E -m unittest tests.test_bytes_analysis.Q2CommitmentCLIChainTests` → `q2-final.log`

```text
.
----------------------------------------------------------------------
Ran 1 test in 94.055s
OK
```

`E -m unittest tests.test_bytes_twin tests.test_km003c_parse tests.b6.test_export_runs` → `twin-native-export-final.log`

```text
.....................................................................................................................
----------------------------------------------------------------------
Ran 117 tests in 91.759s
OK
```

`E -m unittest tests.external.test_km003c_parse tests.b6.test_export_runs` → `native-export-final.log`

```text
........................................................
----------------------------------------------------------------------
Ran 56 tests in 0.566s
OK
```

`E .scratch-416A/round2/run_agreement.py` → `agreement.log`

```text
+ ok
----------------------------------------------------------------------
Ran 48 tests in 118.990s
FAILED (failures=13, errors=3)
```

`E .scratch-416A/round2/final_compare.py` → `agreement-final-pass.log`

```text
.......................
----------------------------------------------------------------------
Ran 48 tests in 95.326s
OK
```

`E .scratch-416A/round2/final_compare.py --compare-only` → `agreement-final-replay.log`

```text
compressed {"above_bar": 0, "compared": 262311, "diagnostic_compared": 84106, "diagnostic_different": 575, "equal": 256649, "under_bar": 5662}
battery_instant {"above_bar": 0, "compared": 315115, "diagnostic_compared": 102402, "diagnostic_different": 662, "equal": 308512, "under_bar": 6603}
battery_delayed {"above_bar": 0, "compared": 314763, "diagnostic_compared": 102274, "diagnostic_different": 664, "equal": 307784, "under_bar": 6979}
PASS: final comparer, all 19 campaigns, zero above the bar
```

`E .scratch-416A/round2/coverage_check.py` → `coverage-summary.log`

```text
PASS 36 method rows; 400 draws per world; independent and full-module coverage counts identical
PASS minimum HC3 plain-95% coverage: 379/400 (0.9475); registered 0.93 floor holds
PASS post-binding final coverage is byte-identical to the initial independent rerun
```

`E .scratch-416A/round2/coverage_map_check.py` → `coverage-map.log`

```text
PASS exhaustive output inventory: 1836 field paths; no missing or stale declarations
PASS F3: 77 diagnostic-only field mutations do not gate; printed mean and coefficient mutations still gate
```

`E .scratch-416A/round2/coverage_map_full_check.py` → `coverage-map-full.log`

```text
checked 1400 compared-field mutations; 0 undetected
checked 1500 compared-field mutations; 0 undetected
checked 1600 compared-field mutations; 0 undetected
PASS all 1608 declared compared-field mutations are detected under the registered bars
```

`E .scratch-416A/round2/scope_audit.py` → `scope-audit.log`

```text
configs/bytes/identity_pins.json : 12 authorized derived-hash fields; all other identity/runtime fields equal base
configs/b6/registration/identity_pins.json : 24 authorized derived-hash fields; all other identity/runtime fields equal base
PASS exhaustive tracked write scope; pack changes are estimator bindings only; identity changes are tree hashes and required source bindings only
```

`E .scratch-416A/round2/rebind.py` → `rebind.log`

```text
Regenerated authorized estimator bindings and trees: 18
PASS: source/consumer tree hashes and derived source bindings re-issued; other identity fields preserved
```

`E scripts/repin.py --write registry` → `repin-write.log`

```text
  P recorded_evidence: 143
  P sealed_registration: 171
  follow-up L10: tests/test_d117_contrast_v5_pack.py (synthetic_literal)
  follow-up L2: joulewise/night_gate.py (RULED_REGISTRATIONS)
```

`E scripts/repin.py --check` → `repin-final.log`

```text
  scripts/run_night.py
  scripts/test_timings.json
  scripts/validate_powermetrics_fiducial.py
PASS 16 pin families current
```

`E scripts/bytes_plan_trees.py --check` → `trees-final.log`

```text
verified 12 BYTES draft registrations and 12 fixed pass trees
```

`E -m unittest tests.test_bytes_plan_trees tests.b6.test_bytes_launch tests.b6.test_bytes_packs` → `plan-tests.log`

```text
bytes-s6-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s6-p2 {'absolute_repeat': 10, 'comparative_abba_member': 40, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen35-122b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s6-p2 lost members 1 ACCEPT True ()
bytes-s6-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
```

## Verification deviations and interpretation

The first full agreement-module assertion run exposed old marker fixtures with implicit counter gaps and a hard-coded 100 ms flip-probability interval, as well as the obsolete requirement that every offset-bound value clear its own cell bar; the marker fixtures now supply continuous 50 SPS samples while retaining their original poll/last-sample fit clocks, the dropped-edge cases require DC refusal when the mapped missing sample is in decode, and the flip test reads its actual header interval. The final module tests actual whole-column omission mutations under the unchanged registered bars. The first twin/native/export run failed only the legacy compressed-fixture assumption that decode start could stand in for a missing tokenize start. Its input now carries a genuine tokenize event; the focused rerun and full 117-test rerun pass. The analysis module initially exposed a legacy signed-latency test with a hard-coded 100 ms meter interval; its assertion now checks the generated 20 ms interval and the corrected test passes. The reference-battery test likewise used measured_run in its oracle; it now uses tokenize through decode end and passes its rerun. An extra real-reference proof initially used an unjustified 1e-8 J assertion, which rejected a 5.02e-8 J allowance difference; the final proof applies §14's 0.0005 J bar. The first real reference proof included an already excluded unresolved H start reference; the final proof follows the unchanged succeeded/nonexcluded ingress and preserves H's unavailable endpoint set. The old raw Astra manifest probe now exits 1 by design at the predictor refusal; the complementary final script asserts both readers' refusals. Round-1 unresolved scope/edge/diagnostic questions were answered by F1–F3 and are not outstanding blockers.

The initial full-analysis invocation executed all 111 test cases, with four failure records affecting three cases: the two stale oracles above, and both subcases of the isolated Q2 checkout lacking the newly required canonical manifest. The Q2 fixture now copies that digest-authenticated input alongside its isolated code; both comment-only and fit-line mutation subcases pass. All three affected current test definitions pass focused reruns; the other 108 cases, including the 60-campaign ensemble, pass in the full invocation. All 111 final test definitions are therefore covered without repeating the already completed 60-campaign ensemble for test-only assertion changes. Some scratch-file formatting and log-inspection snippets used the default Python 3.14 without the requested safety prefix. All repository tests and real-data probes used the mandated Python 3.13 -B and environment. A final scan finds zero Python 3.14 bytecode files under joulewise, scripts or tests; the default-interpreter resolution and verification environment are recorded in round2/python-helper-audit.log. No whole-repository suite or live hardware validation is claimed; the user explicitly reserved those for CI/the lead. All changed tests and relevant native parser tests were run as focused modules. Registration prose is deliberately unchanged and must be applied by the lead. The original scratch report is retained as `REPORT-round1.md` for provenance; this report supersedes its partial status.

## Final SHA-256 values

- `configs/b6/packs/bytes-s1-p1/registration.json`: `e43c2baeba1b4f6539ca37198c2519f81d8548090ed6012bf00efef6298f6ea5`
- `configs/b6/packs/bytes-s2-p1/registration.json`: `41ce7b9ea17e837d302334643db043128c7ffdc2ae35a4f58d57b69cc1646f8a`
- `configs/b6/packs/bytes-s3-p1/registration.json`: `63b2d69607775f73ca2f35fef3bb5413582aad45763515f02a108c27fc1a4ca3`
- `configs/b6/packs/bytes-s4-p1/registration.json`: `7778868c99e94fc0314ab35706fea53bae776890cd461a0c625478b7c8260351`
- `configs/b6/packs/bytes-s5-p1/registration.json`: `bd1b815b5248b53f33fc9bc29c9ec1cbc236c381995975037093c293d57361b6`
- `configs/b6/packs/bytes-s6-p1/registration.json`: `33d0f0b928b22ed7c1cfeb96787817b163cb522a41baff59e7d28e76877dd87c`
- `configs/b6/registration/identity_pins.json`: `00237a41170a48f8def36e9afe285a97f8fdc37005488c6d5b7d33067129caf9`
- `configs/bytes/identity_pins.json`: `782fd6ec19293042aa3e7297bac02eab6657626e9e67e25abef479c7fd0b4c26`
- `configs/campaigns/bytes-s1-p1/plan_tree.json`: `a9bdcaa0c0f44cb1e41f5d02804c041a1c7a926fbbbe8fbfcb315086153db845`
- `configs/campaigns/bytes-s1-p2/plan_tree.json`: `b1d08d3a063ba30439bb5eab87122d50c95e58b69e72edeb56c93d48ab0f97c3`
- `configs/campaigns/bytes-s2-p1/plan_tree.json`: `78209b00bef6fdc58b4ea6ef1a416b988d39ef770ba269e1deeceb3952ddd41d`
- `configs/campaigns/bytes-s2-p2/plan_tree.json`: `a9e451e0ba4dc74f9ab00edfa07c708c56ed3377c3e035082c0644995f197f9f`
- `configs/campaigns/bytes-s3-p1/plan_tree.json`: `993b1158c135cdf55dd1a03ab592306bd24ed61b94e9972fe8c5dd078f4b329f`
- `configs/campaigns/bytes-s3-p2/plan_tree.json`: `5a3d11d816b3ffb5be53f80be96ade15720108db7b3332a06470bbc1afd41573`
- `configs/campaigns/bytes-s4-p1/plan_tree.json`: `934e482d929e4b4db3c6fedf4e60596acaff2d16bb29d9ad0f403286c17f14b7`
- `configs/campaigns/bytes-s4-p2/plan_tree.json`: `a28aeedc4597196bd2de7635c0b3a13dc382be0dd98ce1c2c0884b7f4483b65c`
- `configs/campaigns/bytes-s5-p1/plan_tree.json`: `ef1b3161f90a5c54b7da5fb642dd0f466f045be0f18db7ae3193a850f456d532`
- `configs/campaigns/bytes-s5-p2/plan_tree.json`: `5c6d798eabfdb585d9eba9ac03395d9614392fc83fa84d70f335a7e2da9cfacc`
- `configs/campaigns/bytes-s6-p1/plan_tree.json`: `cb2e2d24755ac718bbac808b9556e6e3df8a6730795f5fdd31a53a1c9d1d3ebb`
- `configs/campaigns/bytes-s6-p2/plan_tree.json`: `c7dad2e8b53606f178f51133da61582479bde733db8c4fab30684190d5b0892f`
- `configs/pins/registry.json`: `4cc05a007dd15e98f630ae3d1cbc184b7b4f7731044b24c2a6eca70117696805`
- `joulewise/b6/export_runs.py`: `61a58df84395fd4e78322eb49455558e15c917b6697686fc82064eedc0d36fba`
- `joulewise/bytes_analysis.py`: `76c44759c4c674100303be718ce9c4db0723d3b7ffb9549f0ad4607285b0176a`
- `joulewise/external/km003c_parse.py`: `aaab58733db866957b0f6684401ecd6309f7b3275019e6f8ddf641a6e01288f2`
- `scripts/bytes_plan_trees.py`: `181c35f4512ef38b6dac7f1f02a350c3ca908fcd677d6000b48bb4e6b6961830`
- `scripts/bytes_twin.py`: `1f0791a66ffdedbdb0d7b48f3e30839b5993a7a3332df05ba0e999c0aecc2172`
- `tests/b6/test_bytes_launch.py`: `7dc41f9edae939dbdeb63f2e16a16afd6dd628cc0be6808f4f4d573be0138b41`
- `tests/b6/test_bytes_packs.py`: `9242923bacd47fd8879d23320811209f7973c0668e784b3cbecba9264165bb9f`
- `tests/b6/test_export_runs.py`: `f04a2a9a0d0a90c2bf481a185900b56a73977809782bd66e48df2ef3b9f953b2`
- `tests/fixtures/bytes/campaign.py`: `f1a6475f1ef96c59e011f918562c0ba1c39777e7ed15dd821f60b556c1804adc`
- `tests/fixtures/bytes/campaign_design.json`: `0834cdfcf7520c607f0b7198f3c9a61db74a62847d72e659d912fb8f42a91766`
- `tests/fixtures/bytes/output_coverage.json`: `4404a69bb9ce9d665768046b588ea98f1797bad31fd55bedbeaeea5f9b52e6ee`
- `tests/fixtures/bytes/twin_synth.py`: `273acfee117c4ffaf795d6fd99c18f5c33f23e7ce4c1477ddef2a9d30cad02e4`
- `tests/test_bytes_agreement.py`: `b2ebacd3f227a3c61c7ac45bdeff1bd9b03fdd12c235183a271f1797b1324596`
- `tests/test_bytes_analysis.py`: `66424f26c40ffdec0bc82eb64e11aa9ca09f0a360dbd2cf283945ec5af308eae`
- `tests/test_bytes_plan_trees.py`: `ed8000bf45ccb757151d78549e52c297b03a9b05cbc7f3ed13c74a901de52cb6`
- `tests/test_bytes_twin.py`: `2207b543c6965f29d462abe6e36b1ee9e680324edb8d7bf8937c99387271c5be`
- `tests/test_km003c_parse.py`: `269e764a5fda9146e0ab6ca739f85988ba6be67ffd260790c9950d3a09504f71`
- `configs/bytes/bytes_manifest.json`: `76452108c1a10b1f63b48fc95b306b6c4aa936a0d2e94244be65dc067c356264`

HEAD did not move; the estimator digest identifies the uncommitted reviewed file bytes, which the lead commits.
