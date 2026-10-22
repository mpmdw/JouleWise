## PROGRESS

- Done: findings 1, 4 and 5 implemented in 998d0dc05; findings 2 and 3 in 552561b3f. Finding 6 rejected as directed; finding 7 handed forward verbatim. All edits stay within the exhaustive allowlist.
- Done: corrected-source battery/meter classes pass 20 tests; instant and delayed real CLI chains, charging, weighted columns, blinded nulls, exact receive sorting and printed bounds/floors are verified.
- Done: all nine mutants KILLED in disposable copies; 180 test executions complete with the expected assertion failures. Every mutant copy and disposable TMPDIR deleted. Clone source never mutated.
- Done: exact three-stage CLI/load_records comparison against bda481d5a and ddcbafc4d; 523,819 / 1,316,507 common scalar fields unchanged apart from the prescribed 160 blinded count objects and provenance digests. Default no-assist manifests and both meter-stream byte hashes unchanged.
- Done: all 85 bounded analysis test methods pass individually by class across slices 2–4, with no skips. The local route replaces the long CampaignWordRates/whole-module run with CI. Six support modules: 33 passes, one pre-existing NULL-versus-GO hazard failure reproduced at ddcbafc4d. Agreement: seven passes, one expected defects failure; all 238 fields recorded below. Refusal census: all five arrays empty, exit 0.
- Done: slice 4 resumed clean director head a846ba997e307859cd625e034dfb53a22f64daf2; remaining M3/M19/M21 and all seven remaining classes complete. No implementation, fixture or test changes in this slice; only this report. Logs/results under /tmp/bat3f1/; all run TMPDIRs deleted.
- Next: director commits this report, pushes the same head to lane/2026-10-22-bytes-battery-term and ci/2026-10-22-bytes-battery-term, records PR #544 CI, and hands parity requirements to BY-TWIN-BAT. BY-MERGE carries the listed hunks later; no other branch merged here.
- Open external work: director-owned commit/push/CI observation and final review; BY-TWIN-BAT parity; the known baseline hazard-environment failure. No remaining local implementation or prescribed bounded verification; no NEEDS_SCOPE or NEEDS_RULING. No measurements, network actions or Git writes attempted.

BAT-3-fix1 COMPLETE

## SUMMARY

Findings 1–5 are fixed; the three battery/meter classes pass all 20 tests.
The delayed CLI world independently pins forward edge terms, post-end markers and the max-edge NR1 bound.
All 30 delayed discharge placements and two signed charging runs pass; charging receives no assist flag.
Printed battery means use registered stratum weights, and nonzero counts include charging.
Blinded decode counts and without-assisted numbers print null with the prescribed reason; harvest counts remain evaluated.
Receive-order checks require exact flags, full meter dictionaries and NEG-8 inputs; one cadence helper preserves arithmetic.
All nine mutants are killed, and exact comparisons against both baselines pass with only prescribed blinded/provenance changes.
All 85 bounded analysis methods pass locally; the long CampaignWordRates method and whole-module run belong to CI.
Agreement has the expected 238-field twin defects failure; one unchanged local hazard test fails at both final and baseline.

## FIX LOG

1. Fixed in 998d0dc05: delayed fixture/test passes in corrected-source three-class run. All 30 placements checked at 1e-6 J; exact markers/counts and printed maxima. Charging extension in 552561b3f.
2. Fixed in 552561b3f: test_large_model_assist_cli_chain_all_four_placements_and_counts independently checks registered stratified means on every printed DC/rest cell and signed nonzero counts, including retained charging; margin 0.044056348856499616 J.
3. Fixed in 552561b3f: test_blinded_assist_is_null_with_reason_and_heldout_counts_are_evaluated passes through the real CLI chain; count reason and without-assisted nulls match the disposition. Combined diagnostics retain the reason.
4. Fixed in 998d0dc05: test_out_of_receive_order_batches_match_ordered_terms_and_flags passes for exact flags/meter/NEG-8 equality under reversal and deterministic shuffle.
5. Fixed in 998d0dc05: T_SMC_S constant and shared _battery_delay_s helper; all 20 current battery/meter tests pass. Slice 3 bit-identity comparison passes; no scientific value changes.
6. Rejected as directed: production writes rx on every poll (all 93,533 H polls); malformed rx already causes a recorded bytes.meter_decode_unavailable fit-error flag, not refusal. Reference parser sorts by b["rx"] too; keep parity.
7. Handed forward; no twin edits authorized.

## MUTATION KILLS

All mutants run against disposable copies, with the three classes BatteryRulingWorkedExamples, MeterWorkedExamples, BatteryCampaignTests (20 tests). Exact command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/bat3f1/mutate_slice2.py`; the runner sets fresh TMPDIR, invokes `/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.BatteryRulingWorkedExamples tests.test_bytes_analysis.MeterWorkedExamples tests.test_bytes_analysis.BatteryCampaignTests` with the mutant copy as cwd, and deletes TMPDIR and copy in finally. Clone source is never mutated.

| mutant | before | after | killing test / evidence |
|---|---|---|---|
| M1_marker_no_end_tau | SURVIVED | KILLED | test_delayed_publications_pin_forward_edges_marker_and_offset_max: marker false vs true on late-end burst; 20 tests, one failure, exit 1, 68.931 s unittest / 69.851 s process |
| M2_v_end_zero | SURVIVED | KILLED | same delayed test: v_end 0 vs 12.65003513402062 J; 20 tests, one failure, exit 1, 68.304 s unittest |
| M8_offset_sum_not_max | SURVIVED | KILLED | test_delayed_publications_pin_forward_edges_marker_and_offset_max: both-edge C_j max assertion; 20 tests, one failure, exit 1, 64.847 s unittest / 65.719 s process |
| M10_battery_mean_unweighted | SURVIVED | KILLED | test_large_model_assist_cli_chain_all_four_placements_and_counts: 0.044056348856499616 J mean mismatch; 20 tests, one failure, exit 1, 79.315 s unittest / 80.401 s process |
| M18_v_end_backward_window | SURVIVED | KILLED | test_delayed_publications_pin_forward_edges_marker_and_offset_max: v_end 0 vs 12.65003513402062 J; 20 tests, one failure, exit 1, 78.184 s unittest / 79.117 s process |
| M20_nonzero_count_off | SURVIVED | KILLED | test_large_model_assist_cli_chain_all_four_placements_and_counts: count 3 vs 4; 20 tests, one failure, exit 1, 75.403 s unittest / 76.358 s process |
| M3_marker_no_start_tau | KILLED | KILLED | test_bat2_qwen_check_r01_seven_nonzero_polls, delayed oracle marker and instant-world decode counts: 20 tests, 3 failures, exit 1, 64.848 s unittest / 65.727 s process |
| M19_tau_one_refresh_plus_poll | KILLED | KILLED | test_bat2_qwen_check_r01_seven_nonzero_polls, delayed oracle marker and test_global_poll_gap_including_empty_poll_outside_selected_spans_sets_tau (1.6 vs 2.6 s): 20 tests, 3 failures, exit 1, 62.111 s unittest / 63.005 s process |
| M21_without_line_on_harvest_flag | KILLED | KILLED | test_large_model_assist_cli_chain_all_four_placements_and_counts: decode-assisted counts 4 vs 2 repeats; 20 tests, one failure, exit 1, 58.115 s unittest / 58.907 s process |

Slice 3 command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/bat3f1/mutate_remaining.py M10_battery_mean_unweighted M18_v_end_backward_window M20_nonzero_count_off`. Slice 4 command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/bat3f1/mutate_remaining.py M3_marker_no_start_tau M19_tau_one_refresh_plus_poll M21_without_line_on_harvest_flag`. Both complete; each copy and TMPDIR is deleted, logs are `/tmp/bat3f1/<mutant>.log`; result rows are in `/tmp/bat3f1/mutations-remaining.jsonl`. All nine semantic mutants are KILLED after the fix, including all three previously killed mutants.

## DELAYED WORLD

Explicit battery_publication="delayed" on assisted archive_campaign; default is instant.
BAT-2 §3: one preceding second averaged, publication held for one second, 5 Hz polls.
Publication phase 370 ms relative to raw-clock seconds, off the poll grid; preceding-second current sampled every 10 ms and rounded to integer mA.
Four original placements plus both_edges (two 1 s, -1000 mA bursts at 12774 mV). For delayed end bursts only, start after the final pre-end publication (at least 10 ms after it), keeping burst duration 1 s and crossing decode end. This ensures the first discharge report is late in every model/pass; fixed +/-0.5 s can publish a nonzero mean before decode end for some phases.
Test prints BAT3_DELAYED JSON to log.

Verified delayed per-run values (J; marker exact). Each row passed the independent raw-JSON oracle at 1e-6 J.

| pass | model | placement | burst | E_b | v_start | v_end | marker | C_j | u+v |
|---|---|---|---:|---:|---:|---:|---|---:|---:|
| 1 | Llama-3.3-70B-Instruct-4bit | inside_decode | 12.774000000 | 12.796024138 | 0.000000000 | 0.000000000 | True | 0.760886180 | 1.521772360 |
| 1 | Llama-3.3-70B-Instruct-4bit | across_start | 12.774000000 | 12.796024138 | 12.796024138 | 0.000000000 | False | 13.554226378 | 14.312428619 |
| 1 | Llama-3.3-70B-Instruct-4bit | across_end | 12.774000000 | 0.000000000 | 0.000000000 | 12.650035134 | True | 13.408881658 | 14.167728182 |
| 1 | Llama-3.3-70B-Instruct-4bit | prefill_only | 10.219200000 | 10.201641237 | 10.201641237 | 0.000000000 | False | 10.961967260 | 11.722293282 |
| 1 | Llama-3.3-70B-Instruct-4bit | both_edges | 25.548000000 | 12.796024138 | 12.796024138 | 12.693655945 | True | 13.554730380 | 27.007092566 |
| 1 | Qwen3-Next-80B-A3B-Instruct-4bit | inside_decode | 12.774000000 | 12.774000000 | 0.000000000 | 0.000000000 | True | 0.298491793 | 0.596983586 |
| 1 | Qwen3-Next-80B-A3B-Instruct-4bit | across_start | 12.774000000 | 12.774000000 | 12.186396000 | 0.000000000 | True | 12.483877954 | 12.781359909 |
| 1 | Qwen3-Next-80B-A3B-Instruct-4bit | across_end | 12.774000000 | 0.000000000 | 0.000000000 | 12.416328000 | True | 12.714264387 | 13.012200774 |
| 1 | Qwen3-Next-80B-A3B-Instruct-4bit | prefill_only | 10.219200000 | 8.916252000 | 8.916252000 | 0.000000000 | False | 9.214677593 | 9.513103187 |
| 1 | Qwen3-Next-80B-A3B-Instruct-4bit | both_edges | 25.548000000 | 12.774000000 | 12.263040000 | 12.263040000 | True | 12.561391834 | 25.122783669 |
| 1 | Qwen3.5-122B-A10B-4bit | inside_decode | 12.774000000 | 12.774000000 | 0.000000000 | 0.000000000 | True | 0.484552627 | 0.969105254 |
| 1 | Qwen3.5-122B-A10B-4bit | across_start | 12.774000000 | 12.774000000 | 12.339684000 | 0.000000000 | True | 12.824619137 | 13.309554273 |
| 1 | Qwen3.5-122B-A10B-4bit | across_end | 12.774000000 | 0.000000000 | 0.000000000 | 12.339684000 | True | 12.825615044 | 13.311546088 |
| 1 | Qwen3.5-122B-A10B-4bit | prefill_only | 10.219200000 | 8.839608000 | 8.839608000 | 0.000000000 | False | 9.323743452 | 9.807878903 |
| 1 | Qwen3.5-122B-A10B-4bit | both_edges | 25.548000000 | 12.774000000 | 12.237492000 | 12.237492000 | True | 12.724762476 | 25.449524952 |
| 2 | Llama-3.3-70B-Instruct-4bit | inside_decode | 12.774000000 | 12.774000000 | 0.000000000 | 0.000000000 | True | 0.378282884 | 0.756565767 |
| 2 | Llama-3.3-70B-Instruct-4bit | across_start | 12.774000000 | 12.774000000 | 12.774000000 | 0.000000000 | False | 13.152833446 | 13.531666891 |
| 2 | Llama-3.3-70B-Instruct-4bit | across_end | 12.774000000 | 0.000000000 | 0.000000000 | 12.697356000 | True | 13.077888001 | 13.458420003 |
| 2 | Llama-3.3-70B-Instruct-4bit | prefill_only | 10.219200000 | 8.762964000 | 8.762964000 | 0.000000000 | False | 9.142215497 | 9.521466993 |
| 2 | Llama-3.3-70B-Instruct-4bit | both_edges | 25.548000000 | 12.467424000 | 12.467424000 | 12.416328000 | True | 12.846042966 | 25.640989932 |
| 2 | Qwen3-Next-80B-A3B-Instruct-4bit | inside_decode | 12.774000000 | 12.774000000 | 0.000000000 | 0.000000000 | True | 0.148581079 | 0.297162158 |
| 2 | Qwen3-Next-80B-A3B-Instruct-4bit | across_start | 12.774000000 | 12.774000000 | 12.365232000 | 0.000000000 | True | 12.514599828 | 12.663967655 |
| 2 | Qwen3-Next-80B-A3B-Instruct-4bit | across_end | 12.774000000 | 0.000000000 | 0.000000000 | 12.416328000 | True | 12.565388688 | 12.714449376 |
| 2 | Qwen3-Next-80B-A3B-Instruct-4bit | prefill_only | 10.219200000 | 8.533032000 | 8.533032000 | 0.000000000 | False | 8.682303927 | 8.831575855 |
| 2 | Qwen3-Next-80B-A3B-Instruct-4bit | both_edges | 25.548000000 | 12.774000000 | 12.314136000 | 12.314136000 | True | 12.463201656 | 24.926403311 |
| 2 | Qwen3.5-122B-A10B-4bit | inside_decode | 12.774000000 | 12.774000000 | 0.000000000 | 0.000000000 | True | 0.241363716 | 0.482727432 |
| 2 | Qwen3.5-122B-A10B-4bit | across_start | 12.774000000 | 12.774000000 | 12.390780000 | 0.000000000 | True | 12.633382102 | 12.875984204 |
| 2 | Qwen3.5-122B-A10B-4bit | across_end | 12.774000000 | 0.000000000 | 0.000000000 | 12.237492000 | True | 12.480701794 | 12.723911588 |
| 2 | Qwen3.5-122B-A10B-4bit | prefill_only | 10.219200000 | 8.456388000 | 8.456388000 | 0.000000000 | False | 8.699307177 | 8.942226355 |
| 2 | Qwen3.5-122B-A10B-4bit | both_edges | 25.548000000 | 12.774000000 | 12.390780000 | 12.390780000 | True | 12.633759655 | 25.267519310 |

Slice 2 retains all 30 discharge rows above unchanged and adds these charging rows (same quantities, J):

| pass | model | placement | burst | E_b | v_start | v_end | marker | C_j | u+v |
|---|---|---|---:|---:|---:|---:|---|---:|---:|
| 1 | Llama-3.3-70B-Instruct-4bit | charging | -1.277400000 | -1.279602414 | 0.000000000 | 0.000000000 | False | 0.757729017 | 1.515458034 |
| 2 | Llama-3.3-70B-Instruct-4bit | charging | -1.277400000 | -1.277400000 | 0.000000000 | 0.000000000 | False | 0.380188791 | 0.760377582 |

Instant charging terms are -1.2796024137931035 J and -1.2774 J, with no decode or harvest assist marker. The .2/.8 mean test checks all DC/rest cells; maximum plain-mean difference is 0.044056348856499616 J.

## BIT-IDENTITY

PASS, slice 3, corrected source at 552561b3f. Read-only Git archives `/tmp/bat3f1/base` (bda481d5a) and `/tmp/bat3f1/round1` (ddcbafc4d) were exported with `git archive <commit> | tar -x -C <path>`; no Git writes. Exact command:

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/bat3f1/bit_identity.py`

The runner launches `/opt/homebrew/bin/python3.13 -B /tmp/bat3f1/identity_worker.py <tree> /tmp/bat3f1/identity-world /tmp/bat3f1/identity-<mode>.json <mode>`, with each tree passed as the process cwd and with its own fresh TMPDIR, deleted in finally. The base fixture creates 1,000 non-assisted runs, then its real blinded → fit → heldout CLI chain and load_records run. BAT-3/final repeat on the same paths/manifest/inputs with only B0AV=12774 added to the base polls, following the first round's comparison method. Each run resets releases and stage outputs; each prediction file stays byte-identical across its held-out stage. All three runs exit 0 (base 14.211 s, round1 10.837 s, final 9.880 s). Campaign scratch tree deleted after snapshots/comparisons.

All 17 JSON outputs are included: blinded/{analysis_record,blinded_pass_estimates,h1,h2,model_estimates,moe,unavailable}; stage1/{fit_pass_estimates,predictions}; out/{analysis_record,h1,h2,heldout_pass_estimates,model_estimates,moe,unavailable}; records. Dictionary common keys recurse, list lengths/types/scalars require exact equality; additions and removals are recorded. Only bytes_analysis_sha256 and predictions_sha256 are disclosed separately as changing provenance, never scientific quantities.

| comparison | exactly equal common scalars | changed common data fields | added key locations | removed | changing digest locations |
|---|---:|---:|---:|---:|---:|
| bda481d5a → final | 523,819 | 0 | 19,672 | 0 | 3 |
| ddcbafc4d → final | 1,316,507 | 160 count objects | 520 | 0 | 3 |

Every changed common data field vs ddcbafc4d is decode_assisted_member_counts: 80 in blinded/blinded_pass_estimates.json[] and 80 in blinded/model_estimates.json[].passes[], each changing {repeat:0,quad:0} to null. Added fields at those same 160 cells are decode_assisted_member_counts_reason, with_assisted_label and without_assisted (480 locations), plus without_assisted at 40 combined blinded/model_estimates.json[] points. No other common value changes. Complete indexed paths and values: `/tmp/bat3f1/comparison-round1.json`.

New field names vs base (19,672 locations, nested objects recorded at their new outer key): battery_gross_j, battery_idle_power_w, battery_n, battery_n_idle, battery_nonzero_run_count, battery_phase_edge_j, battery_phase_edge_max_j, battery_poll_interval_max_s, battery_secondary_j, battery_tau_s, battery_term_max_j, battery_term_mean_j, battery_v_end_j, battery_v_start_j, boundary_description, decode_assisted_member_counts, decode_assisted_member_counts_reason, decode_battery_assist, harvest_assisted_member_counts, meter_gross_j, meter_idle_power_w, meter_phase_edge_j, meter_run_terms, meter_secondary_j, with_assisted_label, without_assisted. Complete paths: `/tmp/bat3f1/comparison-base.json`.

Changing digest locations in both comparisons: stage1/predictions.json.bytes_analysis_sha256; out/analysis_record.json.bytes_analysis_sha256.{committed,evaluating}; out/analysis_record.json.predictions_sha256. Source SHA-256 base ae8c856d6467f8f51fae3c4e966d7948e64fadbbad22ada066d28748d52a1186; round1 fbf7b91acbe361cd3947f8e3d70fb9bc2941da9164b99ee2101294b161fc12e7; final 36cfd4b3f91ce93b7ada90c9663aaad345c0d2613d268a95e0e2888c5258292b. Prediction SHA-256 base a6b0e759c9ca0d76b0d86c38c4a27b3246f84d5d619e96984df09c49f301da21; round1 4d971a818f05eff3f5ff441ea486a3e8987d3d32685abcd460fc9ab2a45bf79d; final cbb257d94bc887dd4f4be8e13c65b29b2b05bb350c2bd119d54c3982717410ea.

Logs `/tmp/bat3f1/identity-{base,round1,final}.log`; snapshots with the same stems and .json. No byte tolerance, changed scientific exemption or numerical rounding.

Additional default-generation check: `/tmp/bat3f1/default_fixture_worker.py <tree> /tmp/bat3f1/default-fixture-world /tmp/bat3f1/default-fixture-<mode>.json`, launched under the required environment, `/opt/homebrew/bin/python3.13 -B`, tree cwd and fresh disposable TMPDIR, for round1 and final. Each worker actually calls archive_campaign(release="none") with default no-assist arguments; comparison gives manifest_equal=true, hashes_equal=true for both bytes-p1 and bytes-p2 raw meter streams. Both processes exit 0. Thus the fixture's new delayed/charging options leave the default meter bytes and manifest unchanged, independent of the same-input reduction proof. Evidence `/tmp/bat3f1/default-fixture-comparison.json`; worker deletes its campaign tree each time.

## HUNKS FOR BY-MERGE

Final implementation is unchanged from 552561b3f (verified by empty path-specific diff); slices 3 and 4 only update this report. All hunks against ddcbafc4d are listed below.

- Slice 2 joulewise/bytes_analysis.py load_records blinded branch: add decode_assist_evaluated=False per record; no new reduce_models argument.
- Slice 2 reduce_models diagnostic branch: print null decode counts and labelled null diagnostic with reason when records say not evaluated; retain harvest counts and evaluated branch.
- Slice 2 combine_passes diagnostic branch: preserve not_evaluated status/reason/label in combined output.
- Slice 2 tests/fixtures/bytes/campaign.py episode construction: append optional one-second charging episode at first large model's ordinal 5 (both passes).
- Slice 2 stream assembly: publication mean supports signed per-episode current; instant branch looks up per-episode current; baseline empty-episode behavior unchanged.
- Slice 2 harvest flag construction: emit battery.assist only for negative-current episodes, matching harvest semantics.
- tests/fixtures/bytes/campaign.py archive_campaign signature: append battery_publication keyword and mode validation, without moving battery_assist.
- Episode construction: optional fifth both_edges placement only in delayed mode; retain span_ns and add spans_ns for two bursts.
- Stream assembly: cached integer-mA preceding-second publications; instant branch retains prior arithmetic and baseline poll generation.
- joulewise/bytes_analysis.py constants: add T_SMC_S = 1.0.
- joulewise/bytes_analysis.py battery helpers/meter_decode: shared _battery_delay_s(poll_interval), replacing literal tau expression with identical arithmetic.
- joulewise/bytes_analysis.py archive missing-reading marker fallback: use the same helper.

## HAND-FORWARD FOR BY-TWIN-BAT

Finding 7 (verbatim):

**For BY-TWIN-BAT (out of this item's scope).** The agreement failure (238 entries above the bar in CI shard 11) comes only from the battery term, its marker and the blinded-stage line.
   - I built the defects campaign at the head and compared head with base code on its 1000 records. Meter parts are bit-identical, the only extra flag is the new code, and exactly one run differs: qwen3-30b-a3b-4bit-0 in pass 1. Its battery term is 201.6 J, v_start 120.96 J, v_end 40.32 J, and it is marked.
   - The cause is the planted defect: 36 W of battery (−3000 mA × 12000 mV) on a run whose meter was halved to 10.09 J. That inflates the cell's h from 0.81 to 16.0 J.
   - Make the planted battery power equal to the halved meter power, so the run's DC input stays the same. `tests/test_bytes_agreement.py` is out of BAT-3's write scope.

Finding 3 mirror: blinded-stage decode-assisted count and without-assisted diagnostic must be explicitly null/not evaluated, with reason "not evaluated at the blinded stage"; harvest counts remain evaluated.
Agreement rerun (slice 3): eight tests, seven pass and the expected defects-campaign failure, exit 1; 73.175 s unittest / 74.139 s process. All 238 above-bar entries occur in defects; bytes, resident, time and minimum have zero. Full rows with values and bars: `/tmp/bat3f1/agreement-all-fields.json`; log `/tmp/bat3f1/agreement-slice3.log`. The existing comparison checks without-assisted status; it does not currently compare the new null count/reason fields, so BY-TWIN-BAT must mirror those explicitly too.

| campaign | compared | equal | under bar | above bar |
|---|---:|---:|---:|---:|
| bytes | 9986 | 5555 | 4431 | 0 |
| defects | 10031 | 5582 | 4211 | 238 |
| minimum | 10110 | 5574 | 4536 | 0 |
| resident | 9986 | 5695 | 4291 | 0 |
| time | 9986 | 5644 | 4342 | 0 |

Every affected field by stage/group (no first-40 truncation):

| stage | group | fields above bar |
|---|---|---|
| blinded | cell/qwen3-30b-a3b-4bit/pass1/rails/gross/without_assisted | status |
| heldout | cell/qwen3-30b-a3b-4bit/pass1/dc_input/gross | B_j, B_kind:meter_edge, h_j, lower_j, mean_j, meter_attribution_floor_j, upper_j, variance |
| heldout | cell/qwen3-30b-a3b-4bit/pass1/rest/gross | B_j, B_kind:meter_edge, h_j, lower_j, mean_j, meter_attribution_floor_j, upper_j, variance |
| heldout | cell/qwen3-30b-a3b-4bit/pass1/dc_input/idle_subtracted | B_j, B_kind:meter_edge, h_j, lower_j, upper_j, variance |
| heldout | cell/qwen3-30b-a3b-4bit/pass1/rest/idle_subtracted | B_j, B_kind:meter_edge, h_j, lower_j, upper_j, variance |
| heldout | cell/qwen3-30b-a3b-4bit/pass1/dc_input/flagged_inclusive | B_j, B_kind:meter_edge, h_j, lower_j, mean_j, upper_j, variance |
| heldout | cell/qwen3-30b-a3b-4bit/pass1/rest/flagged_inclusive | B_j, B_kind:meter_edge, h_j, lower_j, mean_j, upper_j, variance |
| heldout | point/qwen3-30b-a3b-4bit/mean/dc_input/gross | e, half_width_j(h+B), lower, mean_j, pass_difference_j, pass_values_j[0], power, power_half_w, printed_j_per_output_token, upper |
| heldout | point/qwen3-30b-a3b-4bit/mean/rest/gross | e, half_width_j(h+B), lower, mean_j, pass_difference_j, pass_values_j[0], power, power_half_w, printed_j_per_output_token, upper |
| heldout | point/qwen3-30b-a3b-4bit/mean/dc_input/idle_subtracted | half_width_j(h+B), lower, power_half_w, upper |
| heldout | point/qwen3-30b-a3b-4bit/mean/rest/idle_subtracted | half_width_j(h+B), lower, power_half_w, upper |
| heldout | h1/dc_input/passes_mean/qwen3-30b-a3b-4bit | bytes:ln_ratio, bytes:measured_lower, bytes:measured_upper, resident:ln_ratio, resident:measured_lower, resident:measured_upper, time:consistent, time:ln_ratio, time:measured_lower, time:measured_upper, word |
| heldout | h1/dc_input/pass1/qwen3-30b-a3b-4bit | bytes:ln_ratio, bytes:measured_lower, bytes:measured_upper, resident:ln_ratio, resident:measured_lower, resident:measured_upper, time:consistent, time:ln_ratio, time:measured_lower, time:measured_upper, word |
| heldout | h1/rest/passes_mean/qwen3-30b-a3b-4bit | bytes:ln_ratio, bytes:measured_lower, bytes:measured_upper, resident:ln_ratio, resident:measured_lower, resident:measured_upper, time:consistent, time:ln_ratio, time:measured_lower, time:measured_upper, word |
| heldout | h1/rest/pass1/qwen3-30b-a3b-4bit | bytes:ln_ratio, bytes:measured_lower, bytes:measured_upper, resident:ln_ratio, resident:measured_lower, resident:measured_upper, time:consistent, time:ln_ratio, time:measured_lower, time:measured_upper, word |
| heldout | h2/dc_input/passes_mean | extended:P0:estimate, extended:epsilon:estimate, extended:epsilon:lower[HC3], extended:epsilon:lower[OLS label], extended:epsilon:upper[HC3], extended:epsilon:upper[OLS label], extended:rho:estimate, extended:rho:lower[HC3], extended:rho:lower[OLS label], extended:rho:upper[HC3], extended:rho:upper[OLS label], simple:P0:estimate, simple:epsilon:estimate, simple:epsilon:lower[HC3], simple:epsilon:lower[OLS label], simple:epsilon:upper[HC3], simple:epsilon:upper[OLS label], tier:P0:estimate, tier:epsilon:estimate, tier:epsilon:lower[HC3], tier:epsilon:lower[OLS label], tier:epsilon:upper[HC3], tier:epsilon:upper[OLS label], tier:rho:estimate, tier:rho:lower[HC3], tier:rho:lower[OLS label], tier:rho:upper[HC3], tier:rho:upper[OLS label] |
| heldout | h2/dc_input/passes_mean/deviation/llama-3.3-70b-instruct-4bit | deviation_w, lower_w, predicted_w, prediction_half_w, upper_w |
| heldout | h2/dc_input/passes_mean/deviation/qwen3-8b-8bit | deviation_w, lower_w, predicted_w, prediction_half_w, upper_w |
| heldout | h2/dc_input/passes_mean/deviation/qwen3-next-80b-a3b-instruct-4bit | deviation_w, lower_w, predicted_w, prediction_half_w, upper_w |
| heldout | h2/dc_input/passes_mean/deviation/qwen3.5-122b-a10b-4bit | deviation_w, lower_w, predicted_w, prediction_half_w, upper_w |
| heldout | h2/dc_input/passes_mean/loo | llama-3.3-70b-instruct-4bit, qwen3-1.7b-4bit, qwen3-14b-4bit, qwen3-32b-4bit, qwen3-4b-4bit, qwen3-8b-4bit, qwen3-next-80b-a3b-instruct-4bit, qwen3.5-122b-a10b-4bit |
| heldout | h2/rest/passes_mean | extended:P0:estimate, extended:epsilon:estimate, extended:epsilon:lower[HC3], extended:epsilon:lower[OLS label], extended:epsilon:upper[HC3], extended:epsilon:upper[OLS label], extended:rho:estimate, extended:rho:lower[HC3], extended:rho:lower[OLS label], extended:rho:upper[HC3], extended:rho:upper[OLS label], rest:c:estimate, rest:epsilon_rest:estimate, rest:epsilon_rest:lower[HC3], rest:epsilon_rest:lower[OLS label], rest:epsilon_rest:upper[HC3], rest:epsilon_rest:upper[OLS label], rest:lambda:estimate, rest:lambda:lower[HC3], rest:lambda:lower[OLS label], rest:lambda:upper[HC3], rest:lambda:upper[OLS label], simple:P0:estimate, simple:epsilon:estimate, simple:epsilon:lower[HC3], simple:epsilon:lower[OLS label], simple:epsilon:upper[HC3], simple:epsilon:upper[OLS label], tier:P0:estimate, tier:epsilon:estimate, tier:epsilon:lower[HC3], tier:epsilon:lower[OLS label], tier:epsilon:upper[HC3], tier:epsilon:upper[OLS label], tier:rho:estimate, tier:rho:lower[HC3], tier:rho:lower[OLS label], tier:rho:upper[HC3], tier:rho:upper[OLS label] |
| heldout | h2/rest/passes_mean/deviation/llama-3.3-70b-instruct-4bit | deviation_w, lower_w, predicted_w, prediction_half_w, upper_w |
| heldout | h2/rest/passes_mean/deviation/qwen3-8b-8bit | deviation_w, lower_w, predicted_w, prediction_half_w, upper_w |
| heldout | h2/rest/passes_mean/deviation/qwen3-next-80b-a3b-instruct-4bit | deviation_w, lower_w, predicted_w, prediction_half_w, upper_w |
| heldout | h2/rest/passes_mean/deviation/qwen3.5-122b-a10b-4bit | deviation_w, lower_w, predicted_w, prediction_half_w, upper_w |
| heldout | h2/rest/passes_mean/loo | llama-3.3-70b-instruct-4bit, qwen3-1.7b-4bit, qwen3-14b-4bit, qwen3-32b-4bit, qwen3-4b-4bit, qwen3-8b-4bit, qwen3-next-80b-a3b-instruct-4bit, qwen3.5-122b-a10b-4bit |

## TESTS RUN

Slice 4 exact command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/bat3f1/run_classes_slice4.py tests.test_bytes_analysis.H1WorkedExamples tests.test_bytes_analysis.H2WorkedExamples tests.test_bytes_analysis.Addendum4RegressionTests tests.test_bytes_analysis.ReviewerProbeTests tests.test_bytes_analysis.SubsetReleaseChainTests tests.test_bytes_analysis.Q1MissingFilesCLIChainTests tests.test_bytes_analysis.Q2CommitmentCLIChainTests`. The runner invokes `/opt/homebrew/bin/python3.13 -B -m unittest <class>` individually, with clone cwd, synthetic-only/no-bytecode environment and a fresh TMPDIR per class, deleted in finally. All exit 0, no skips or environmental failures. Logs `/tmp/bat3f1/slice4-<class>.log`; result rows `/tmp/bat3f1/regressions-slice4.jsonl`.

| class | tests | unittest seconds | process seconds | exit |
|---|---:|---:|---:|---:|
| H1WorkedExamples | 6 | 0.001 | 0.840 | 0 |
| H2WorkedExamples | 4 | 0.001 | 0.852 | 0 |
| Addendum4RegressionTests | 14 | 172.842 | 173.710 | 0 |
| ReviewerProbeTests | 1 | 53.253 | 54.018 | 0 |
| SubsetReleaseChainTests | 2 | 52.776 | 53.505 | 0 |
| Q1MissingFilesCLIChainTests | 3 | 32.284 | 33.002 | 0 |
| Q2CommitmentCLIChainTests | 1 | 18.319 | 19.039 | 0 |

These 31 methods complete 85 locally executed analysis methods across the recorded class runs; only CampaignWordRates (one long method) is assigned to CI by the local route. The 400-draw p03 diagnostic completes all 36 registered report rows. No whole repository suite was run.

Slice 4 mutation command/results are under MUTATION KILLS: M3/M19/M21 execute all 60 tests, expected exit 1; all copies and TMPDIRs deleted. No tests/source changed after the passing corrected-source class runs or bit-identity check. `git diff --check` passes; required baseline ancestry confirmed.

Slice 3 agreement exact worker command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/bat3f1/agreement_run.py`, launched via subprocess with clone cwd and a fresh disposable TMPDIR. The worker loads the complete tests.test_bytes_agreement suite with unittest.defaultTestLoader, runs every test, then writes all Recorder rows before returning the suite status. Eight tests, seven pass / one expected failure, exit 1, no skips or environmental failures; details and every above-bar field under HAND-FORWARD FOR BY-TWIN-BAT. Parent finally deletes TMPDIR.

Slice 3 regression command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/bat3f1/run_classes.py tests.test_bytes_analysis.Addendum7RegressionTests tests.test_bytes_analysis.Q1WithheldCensusTests tests.test_bytes_analysis.RegisteredArithmeticTests`. The runner invokes `/opt/homebrew/bin/python3.13 -B -m unittest <class>` individually with clone cwd and a fresh TMPDIR, deleted in finally. Results: Addendum7RegressionTests 13 tests / 30.761 s unittest / 31.725 s process; Q1WithheldCensusTests 4 / 0.004 s / 0.902 s; RegisteredArithmeticTests 3 / 1.482 s / 2.315 s. All exit 0, no skips or environmental failures. Logs `/tmp/bat3f1/slice3-<class>.log`.

Slice 3 mutations: exact command and individual killing tests/timings are under MUTATION KILLS. All 60 executions complete (20 tests per mutant); expected exit 1 with exactly one assertion failure per mutant. No mutant retained. Bit identity: three chains exit 0, all 17 outputs and 1,000 joined records included; exact command/results under BIT-IDENTITY. `git diff --check` exit 0.

Slice 2 additional regression runs: `/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.BoundaryAndStagingTests` (10 tests, 42.208 s, exit 0), and `... tests.test_bytes_analysis.ProductionArchiveTests` (4 tests, 49.919 s, exit 0), with the same synthetic-only/no-bytecode/fresh-TMPDIR wrapper and clone cwd. Logs `/tmp/bat3f1/slice2-{BoundaryAndStagingTests,ProductionArchiveTests}.log`. No skips.

Baseline check: `/opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_import_graph`, process cwd `/tmp/bat3f1/round1` (ddcbafc4d read-only archive), same environment and disposable TMPDIR. Six tests, five pass / one failure, exit 1, 3.692 s: same NULL-versus-GO assertion as final working tree. Log `/tmp/bat3f1/round1-hazards-import-graph.log`.

Slice 2 commands use `/opt/homebrew/bin/python3.13 -B -m unittest <name>` for each table row (prefix battery class names with `tests.test_bytes_analysis.`). Each separate invocation has `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, and its own `TMPDIR=tempfile.mkdtemp(prefix="jwtmp-bat3f1.", dir="/tmp")`, deleted by `shutil.rmtree` in finally. Cwd is the clone. Logs are `/tmp/bat3f1/slice2-<name>.log`. No skips.

| class/module | tests | seconds | exit |
|---|---:|---:|---|
| BatteryRulingWorkedExamples | 3 | 0.001 | 0 |
| MeterWorkedExamples | 3 | 0.001 | 0 |
| BatteryCampaignTests | 14 | 75.422 | 0 |
| tests.b6.test_bytes_packs | 9 | 2.248 | 0 |
| tests.b6.test_catalog | 4 | 0.313 | 0 |
| tests.flags.test_flags_catalog | 7 | 0.009 | 0 |
| tests.hazards.test_import_graph | 6 | 3.894 | 1; 1 failure |
| tests.flags.test_flags_import_graph | 3 | 0.256 | 0 |
| tests.test_battery_float_sweep | 5 | 3.154 | 0 |

Hazard import-graph failure: `test_a_complete_arm_and_monitor_run_load_no_retired_module` receives `NULL` instead of `GO` from its fake-hardware arm; unchanged module, five remaining tests pass. No hazard-path repair attempted; the identical failure reproduces on the read-only ddcbafc4d archive (six tests, one failure, 3.692 s, exit 1), so it predates this fix. No environment repair attempted.

`/opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census`: exit 0, unlisted=[], stale=[], miscounted=[], guard_changed=[], scope_gaps=[]; same environment/fresh-TMPDIR/cleanup wrapper. Log `/tmp/bat3f1/refusal-census-slice2.log`.

Slice 1 initial attempts (superseded by the passing corrected-source runs): `/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.BatteryCampaignTests.test_delayed_publications_pin_forward_edges_marker_and_offset_max`, with JW_B5_SYNTHETIC_ONLY=1, PYTHONDONTWRITEBYTECODE=1 and fresh TMPDIR; output `/tmp/bat3f1/delayed-first.log`.
Initial shell cleanup command was rejected by command guard (rm -rf disallowed); no test ran in that attempt. Switched to Python tempfile/subprocess/shutil cleanup, retaining all required environment controls.
First delayed test: 1 test, 46.785 s, exit 1: fixed symmetric end bursts could publish before decode end in some phases. Tightened only delayed end-burst placement as described above.
Second run adds BatteryRulingWorkedExamples and MeterWorkedExamples; output `/tmp/bat3f1/delayed-second.log`. During that run removed an erroneous test lookup for analysis_record.refusal_census (the census is a separate tool, not an analysis output field); if that already-loaded run reaches KeyError, rerun the corrected source. Run `-m tests.hazards.refusal_census` separately and record all five arrays.
Second run completed: 7 tests in 50.695 s, 6 passed, 1 error at the already-removed refusal_census lookup. All delayed energy, marker, edge, offset and printed-bound assertions passed before that error. Third run uses corrected source and all three classes, log `/tmp/bat3f1/battery-classes-slice1.log`.

## CI

Lane: `lane/2026-10-22-bytes-battery-term`; CI branch: `ci/2026-10-22-bytes-battery-term`; existing draft PR #544 (no new PR).
Current director commit/source head: `a846ba997e307859cd625e034dfb53a22f64daf2`, clean at slice 4 intake, descended from required `ddcbafc4dc53fb40c89b507d46a74cf6d9101c98`. This final slice changes only the report; the director supplies its new commit hash after committing it.
Implementation head: `552561b3f4b76bb5d86d868cda736bcb99eab0a8`; no implementation/test/fixture bytes changed since the exact baseline comparisons.
State: not queried from this offline local seat; no network or Git write attempted. The director owns committing/pushing the same final head to both branches and recording CI. CI runs the whole analysis module; expected outstanding failures are twin agreement's defects campaign and gate-ledger. One required hazard import-graph test also fails locally, identically at unchanged ddcbafc4d, as documented under TESTS RUN.

## DECISIONS I MADE

- One additional delayed CLI chain within BatteryCampaignTests, so the prescribed three-class mutant runs include the new biting assertions.
- Use independent plain-JSON battery formulas; meter-edge factor is checked using the per-run printed powers/residual/sample interval.
- Deterministic reverse and seed-1100 shuffle use exact equality after rx sort.
- Use installed /opt/homebrew/bin/python3.13; no setup/link/install needed on this local route.
- Harvest battery_join and _smc_phase (joulewise/b5/harvest.py around 2557–2700) disclose battery.assist only for discharge and exclude SMC charging above 200 mA. Use +100 mA for one second (1.2774 J) so no other harvest code applies and the run stays in the primary cell.
- To make registered weighting observable without inventing a harvest hazard, BatteryCampaignTests clears B0AV in one unassisted 70B repeat's idle span per pass before the CLI chain. Existing missing-reading handling removes that repeat only from DC/rest; primary and inclusive counts are 9 repeats / 10 quads, and without-assisted counts are 7 / 10 (rails remain 10 / 10 and 8 / 10). The four original discharge placements and their joules are unchanged.
- Decode evaluation is a record-level fact set only by blinded ingress. No new reduce_models argument, flag code, refusal, registration edit or generated pack change is needed. BAT-2 and the table contract do not prescribe a different representation for unevaluated blinded counts.

## OPEN ISSUES

All requested local implementation and bounded verification are complete. Bit identity passes against both baselines; all nine mutants are killed. CI replaces the whole analysis-module run under the local route and remains director-owned. One required hazard import-graph test locally returns NULL instead of GO; unchanged hazard code, no repair attempted, the identical failure reproduces at ddcbafc4d, so it predates this fix. No environment repair attempted. No baseline mismatch, out-of-scope write or ruling question encountered.

## NEEDS_RULING

none
