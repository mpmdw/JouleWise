# Built-terms lexicon

The base table was generated mechanically from `docs/paper/draft-v1.md` by
`scripts/paper_terms_lint.py`. The successor-draft additions below record terms
built or glossed while curing the first-use ledger; ruled terms absent from
either draft remain lint vocabulary.

## Successor-draft first-use additions

| term | first-use home | build or gloss |
|---|---|---|
| Apple M3 Max / 128 GB unified memory | §1 | Names the single measured machine and its memory capacity. |
| MLX | §1 | Apple's on-device inference framework used to run the models. |
| resolution bound / detection floor / cell floor | §1 | One largest allowed false phase-energy difference: “detection floor” is another name for it, and “cell floor” is the artifact term for its final value after the Section 4 safeguards. |
| \(U_{\rm point}\) / \(U_{\rm corner}\) | §1 | Bound at recorded edges versus the counterpart after all allowed lower-or-upper choices are evaluated jointly. |
| member / A/B/B/A block | §1 | One run; four such runs ordered A, B, B, A. |
| timing-error sign / shared sign / local sign | §1 | Direction in which allowed error moves energy; one shared choice spans all blocks and one local choice is made per block. |
| reasoning disabled | §1 | Qwen3's optional chain-of-thought output is switched off. |
| declared machine state | §2 | Hardware and operating conditions recorded before collection. |
| frozen | §2 | Fixed and fingerprinted before collection. |
| signal, fit, range, trace-coverage, and completeness checks | §2 | The first use points to the complete pulse-fit definitions in Appendix A.3.5. |
| shared search-work limits | §2 | The first use points to the complete work-budget definition in Appendix A.3.7. |
| first-record endpoint | §2 | Wall-clock time assigned to the end of the first native power record. |
| clock-anchor allowances | §2 | Endpoint half-range, observed wall-versus-monotonic span, largest clock resolution, and numeric-rounding pad. |
| calibration-acceptance rule | §2 | Pre-collection rule deciding whether two capture bounds may bracket one window. |
| entry check | §2 | The admission gate of Section 5. |
| reference runs | §2 | Fixed workloads repeated at window opening, midpoint, and close to track drift. |
| gross energy | §2 | Processor energy recorded during a run. |
| idle-subtracted energy | §2 | Gross energy minus mean idle power multiplied by run duration. |
| null-test blocks | §3 | Identical-condition blocks whose allowed differences should contain zero. |
| package power | §3 | Summed CPU, GPU, and neural-engine power. |
| retired calculation | §3 | The former equal-rate anchor and guarded yes/no rule, superseded by the rate-aware anchor and corner-to-point ratio. |
| close-out artifact | §4 | Post-campaign artifact that checks every required ratio. |
| energy terms | §4 | Gross request, idle-subtracted request, gross prompt-processing, and gross token-generation energy. |
| deterministic-bound kinds | §4 | Joint interpolation-edge movement, idle-power drift, clock-anchor movement, and whole-window drift allowance. |
| Figure 3 | §4 | Figure reference whose following prose names the evidence, gate, and outcome paths. |

## Draft-v1 generated base

| term | first line | how detected | line (first 80 chars) |
|---|---:|---|---|
| + max(1.0, 0.05 · Loss | 620 | emphasis | Λ = Loss* + max(1.0, 0.05 · Loss*). |
| 1.5B | 247 | curated seed | In a retained diagnostic-era population of 50 Qwen2.5 1.5B prompt-processing pha |
| 10⁻⁶ s | 547 | emphasis | 4. **10⁻⁶ s** prices *binary64 representation error* of the epoch-scale inputs t |
| 197-second capture | 460 | repeated hyphenated compound | 3. Waits until the whole-second `timestamp` label of a record advances at least  |
| 2 < 3 | 256 | emphasis | For a concrete case, retained bundle `p2015-df-ph-decode-abs-r03` supplies the t |
| 4-bit | 260 | curated seed | The prospective demonstration will compare 4-bit Qwen2.5 7B with 1.5B on the nam |
| 59 measured pulses | 464 | emphasis | 7. Drives the **59 measured pulses**. Pulse *j* (0-based) is commanded on at pla |
| 7B | 260 | curated seed | The prospective demonstration will compare 4-bit Qwen2.5 7B with 1.5B on the nam |
| _r6 | 164 | backticked identifier | not merely the excess above the 9.724-ms bracket screen introduced in Section 2; |
| _v4 | 2 | backticked identifier, curated seed | TITLE PAIR — HELD UNTIL `_v4` ISSUES; NEITHER TITLE IS TYPESET. |
| A | 471 | emphasis | The estimator's identity is `powermetrics_native_second_rate_aware_set_membershi |
| A_hi | 530 | emphasis | 5. *A_lo* = min *A*, *A_hi* = max *A* over the full set. |
| A_lo | 530 | emphasis | 5. *A_lo* = min *A*, *A_hi* = max *A* over the full set. |
| absolute component | 117 | curated seed, emphasis | The construction has two sources of false difference. The *absolute component* m |
| accepted region | 622 | emphasis | The **accepted region** is the set of all (*d_on*, *d_off*) in the square [−0.75 |
| accepted-region algorithm | 419 | repeated hyphenated compound | This appendix specifies the two calculations behind the calibration numbers in S |
| ACM CAIS '26 | 372 | emphasis | 11. D. Pham, K. Katevas, A. Shahin Shamsabadi, and H. Haddadi. “AgentStop: Termi |
| ACM SIGMETRICS Performance Evaluation Review | 390 | emphasis | 29. M. Hähnel, B. Döbel, M. Völp, and H. Härtig. “Measuring energy consumption f |
| admissible_interval_empty | 528 | backticked identifier | 3. All rows infeasible → the native rows are re-formed with *δ* = 1 s and recomb |
| admissible_set_uncertainty_dominates_point_floor | 96 | backticked identifier | \| **Phase accounting:** do the two phase energies close to request energy, stay  |
| admission | 55 | curated seed | Figure 2 maps that bracket onto one complete measurement window. The gray horizo |
| admitted | 86 | curated seed | These tests use workloads as known signals to characterize the measuring instrum |
| admitted bundle | 86 | emphasis | These tests use workloads as known signals to characterize the measuring instrum |
| affine_clock_fit_empty | 527 | backticked identifier | 2. Native + stamp rows infeasible → `affine_clock_fit_empty`. |
| affine_clock_residual_exceeded | 528 | backticked identifier | 3. All rows infeasible → the native rows are re-formed with *δ* = 1 s and recomb |
| all_asleep | 220 | backticked identifier | - After any operator or stage intervention, it waits \\(180\\) s with no experimen |
| alpha | 99 | curated seed | The two inferential properties—the null-mean containment and prefill-invariance  |
| Amplitude | 586 | emphasis | 3. **Amplitude** *a* = median{ *y_i* : interior } − *b*, and **robust SNR** = *a |
| analysis-lock.txt | 402 | backticked identifier | Re-derivation requires a full-history checkout at the released revision, Python  |
| anchor | 47 | curated seed, emphasis | For each commanded pulse, the detector estimates resting GPU power from samples  |
| anchor_method_version | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| Anchoring | 561 | emphasis | **Anchoring.** With the point anchor *A* (seconds), record *i*'s end time *t_i*  |
| and | 94 | emphasis | \| **Workload response:** do request and decode energy increase with realized out |
| ane_energy | 429 | backticked identifier | - three processor power fields, `cpu_power`, `gpu_power`, `ane_power`, each in m |
| ane_power | 425 | backticked identifier | **The instrument and its records.** The instrument is macOS `powermetrics`, run  |
| artifact's outcome | 88 | curated seed | The frozen P06 result specification contains the predicates below. D-152 supplie |
| artifact-guide md | 352 | repeated hyphenated compound | Repository governance details removed from Appendix A live in `docs/paper/artifa |
| artifact-guide.md | 352 | backticked identifier | Repository governance details removed from Appendix A live in `docs/paper/artifa |
| attribution-limited | 96 | curated seed, emphasis | \| **Phase accounting:** do the two phase energies close to request energy, stay  |
| attribution-limited label | 96 | repeated hyphenated compound | \| **Phase accounting:** do the two phase energies close to request energy, stay  |
| Authenticating the executed schedule | 567 | emphasis | **Authenticating the executed schedule.** From the pulse stamps and the trimmed  |
| b | 578 | emphasis | The median absolute deviation (MAD) is the median of the absolute distances from |
| B_2-A_1-A_2 2 | 57 | repeated hyphenated compound | The pale lower inset expands one A/B/B/A block. Its black vertical axis is measu |
| B_anchor | 540 | emphasis | where roundup is outward rounding to binary64 and 10⁻⁶ s is `NUMERIC_PADDING_S`. |
| B_decode_claim_J | 196 | backticked identifier | 2. **Direction and registered inference:** both the metrology-aware interval and |
| B_fiducial | 650 | emphasis | Worked example (capture `20260722T145535-e941c821`, re-derived under the anchor  |
| b_fiducial_s | 96 | backticked identifier | \| **Phase accounting:** do the two phase energies close to request energy, stay  |
| baseline set | 573 | emphasis | **Baseline set and robust scale.** Define the *margin window* of pulse *j* as [* |
| Baseline set and robust scale | 573 | emphasis | **Baseline set and robust scale.** Define the *margin window* of pulse *j* as [* |
| BASELINE_S | 461 | backticked identifier | 4. Takes stamp **S_start** (`sampling_started`), then rests 5 s (the pre-train q |
| binary64 representation error | 547 | emphasis | 4. **10⁻⁶ s** prices *binary64 representation error* of the epoch-scale inputs t |
| block difference | 148 | curated seed | 3. A point value hides timing uncertainty, so each independent energy or block d |
| bound | 471 | emphasis | The estimator's identity is `powermetrics_native_second_rate_aware_set_membershi |
| bracket | 49 | curated seed | The clock anchor uses five wall-clock readings, each bracketed by monotonic-cloc |
| bracket_screen_s | 164 | backticked identifier | not merely the excess above the 9.724-ms bracket screen introduced in Section 2; |
| by definition | 514 | emphasis | Because *m_0* is *by definition* *mb*(S_pre) · 10⁹, the first bracket collapses  |
| c | 600 | emphasis | 6. **The search (constrained coordinate descent).** The two shifts are searched  |
| calibration_acceptance_d079_v2_n17_r3 | 164 | backticked identifier | not merely the excess above the 9.724-ms bracket screen introduced in Section 2; |
| Castanet 2025 Workshop at CCGrid | 375 | emphasis | 14. N. Kocher, C. Wassermann, L. Hennig, J. Seng, H. Hoos, K. Kersting, M. Linda |
| cell | 11 | curated seed | Phase-energy measurements can repeat yet still charge energy to the wrong stage  |
| Cell lower bound | 624 | emphasis | - **Cell lower bound.** For a rectangle *C* = [on_lo, on_hi] × [off_lo, off_hi]  |
| cell-specific resolution | 30 | repeated hyphenated compound | 2. The second contribution is a cell-specific resolution bound and the prospecti |
| ch | 434 | emphasis | - the per-channel powers in watts, `rail_power_w[ch] = field_ch / 1000` for each |
| characterization | 84 | curated seed | ## 3. Instrument characterization |
| characterization_operative_floor_unavailable | 88 | backticked identifier | The frozen P06 result specification contains the predicates below. D-152 supplie |
| claim gate | 202 | curated seed | Figure 3 separates evidence refusal from the two claim gates. A thin horizontal  |
| claim-anchored limit | 88 | curated seed | The frozen P06 result specification contains the predicates below. D-152 supplie |
| claim-side bound | 196 | curated seed, repeated hyphenated compound | 2. **Direction and registered inference:** both the metrology-aware interval and |
| Clock stamps | 442 | emphasis | **Clock stamps.** The controller reads time with a *paired stamp*: it reads the  |
| clock-anchor bound | 47 | repeated hyphenated compound | For each commanded pulse, the detector estimates resting GPU power from samples  |
| clock-anchor estimator | 419 | emphasis, repeated hyphenated compound | This appendix specifies the two calculations behind the calibration numbers in S |
| clock-model error | 21 | repeated hyphenated compound | The primary research question is therefore plain: under the corrected clock mode |
| clock_anchor_unresolved | 482 | backticked identifier | **Inputs and their admission checks.** All five stamps must be present and well  |
| clock_fit_unbounded | 529 | backticked identifier | 4. *β_lo* = min *β*, *β_hi* = max *β* over the full set. If either equals its bo |
| clock_rate_limit_exceeded | 529 | backticked identifier | 4. *β_lo* = min *β*, *β_hi* = max *β* over the full set. If either equals its bo |
| clock_stamp_invalid | 514 | backticked identifier | Because *m_0* is *by definition* *mb*(S_pre) · 10⁹, the first bracket collapses  |
| combined power | 435 | emphasis | - the **combined power** *p_i* = Σ_ch `rail_power_w[ch]`, i.e. cpu + gpu + ane,  |
| Commanded pulses | 450 | emphasis | **Commanded pulses.** A commanded pulse *P* is a pair of stamps, one taken immed |
| comparative component | 117 | curated seed, emphasis | The construction has two sources of false difference. The *absolute component* m |
| Composing the bound | 534 | emphasis | **Composing the bound.** With *A_lo*, *A_hi* in ns: |
| config.json | 410 | backticked identifier | 1. A run bundle at `<runs root>/<run id>/`. `config.json` identifies the conditi |
| contrast | 99 | curated seed | The two inferential properties—the null-mean containment and prefill-invariance  |
| corner maximum | 150 | curated seed | 4. Apply the pre-fixed small-sample multiplier after the corner maximum: |
| corner-widened | 103 | curated seed | **Diagnostic-era evidence of the phenomenon, not a current instrument property.* |
| corner-widened guarded | 185 | repeated hyphenated compound | Each arrow means that the named value supplies the calculation to its right. The |
| corner_widened_guarded_floor_j | 185 | backticked identifier, curated seed | Each arrow means that the named value supplies the calculation to its right. The |
| corners | 148 | emphasis | 3. A point value hides timing uncertainty, so each independent energy or block d |
| cpu_busy_ratio_p95 | 221 | backticked identifier | - The pre-run idle baseline samples for \\(30\\) s at a requested \\(10\\) Hz and mu |
| cpu_energy | 429 | backticked identifier | - three processor power fields, `cpu_power`, `gpu_power`, `ane_power`, each in m |
| cpu_power | 425 | backticked identifier | **The instrument and its records.** The instrument is macOS `powermetrics`, run  |
| Cumulative elapsed time | 440 | emphasis | **Cumulative elapsed time.** Define *q_0* = 0 and *q_i* = *e_1* + *e_2* + … + *e |
| d_off | 588 | emphasis | 5. **The model and the objective.** For candidate edge shifts (*d_on*, *d_off*)  |
| d_on | 588 | emphasis | 5. **The model and the objective.** For candidate edge shifts (*d_on*, *d_off*)  |
| decision interval | 196 | curated seed | 2. **Direction and registered inference:** both the metrology-aware interval and |
| decode | 35 | emphasis | JouleWise assigns each *powermetrics* sampling interval to prompt processing (*p |
| detected | 644 | emphasis | A pulse is **detected** when it passes every check of A.3.5 and so carries two w |
| detection floor | 11 | curated seed | Phase-energy measurements can repeat yet still charge energy to the wrong stage  |
| deterministic_bounds.total | 196 | backticked identifier | 2. **Direction and registered inference:** both the metrology-aware interval and |
| Diagnostic-era evidence | 11 | repeated hyphenated compound | Phase-energy measurements can repeat yet still charge energy to the wrong stage  |
| DIAGNOSTIC-ERA VALUE | 256 | repeated hyphenated compound | For a concrete case, retained bundle `p2015-df-ph-decode-abs-r03` supplies the t |
| Direction and registered inference | 196 | emphasis | 2. **Direction and registered inference:** both the metrology-aware interval and |
| direction gate | 285 | curated seed | Table 3. Prospective contrast decisions. The point will be the mean of ten block |
| direction supported | 210 | emphasis | **End-to-end numeric example (synthetic regression fixture, not experimental evi |
| direction unresolved | 204 | emphasis | In the lower lane, the gray input box contains the measured contrast: its point  |
| directional claim | 204 | emphasis | In the lower lane, the gray input box contains the measured contrast: its point  |
| display_power_state | 220 | backticked identifier | - After any operator or stage intervention, it waits \\(180\\) s with no experimen |
| Double-headed arrows | 37 | repeated hyphenated compound | Figure 1 names the mechanism. Its horizontal time axis, vertical power axis, pal |
| drift | 55 | curated seed | Figure 2 maps that bracket onto one complete measurement window. The gray horizo |
| Drift and recovery | 97 | emphasis | \| **Drift and recovery:** does an allowance contain probes excluded from constru |
| e-Energy '10 | 377 | emphasis | 16. M. Poess, R. O. Nambiar, K. Vaid, J. M. Stephens, K. Huppler, and E. Haines. |
| e_0 | 438 | emphasis | *p_i* and *E_i* are used for only one thing: a health check that the record's po |
| e_1 | 440 | emphasis | **Cumulative elapsed time.** Define *q_0* = 0 and *q_i* = *e_1* + *e_2* + … + *e |
| e_2 | 440 | emphasis | **Cumulative elapsed time.** Define *q_0* = 0 and *q_i* = *e_1* + *e_2* + … + *e |
| E_clock_anchor_shift_bound_j | 196 | backticked identifier | 2. **Direction and registered inference:** both the metrology-aware interval and |
| e_i | 427 | emphasis | - `elapsed_ns`, written *e_i*: the length in nanoseconds of the averaging window |
| earlier | 514 | emphasis | Because *m_0* is *by definition* *mb*(S_pre) · 10⁹, the first bracket collapses  |
| Edge coverage | 587 | emphasis | 4. **Edge coverage**: the earliest start in *L* must be ≤ *on* − 0.75 and the la |
| edge_coverage_missing | 587 | backticked identifier | 4. **Edge coverage**: the earliest start in *L* must be ≤ *on* − 0.75 and the la |
| effective_clock_anchor_bound_exceeded | 540 | backticked identifier | where roundup is outward rounding to binary64 and 10⁻⁶ s is `NUMERIC_PADDING_S`. |
| elapsed_ns | 427 | backticked identifier | - `elapsed_ns`, written *e_i*: the length in nanoseconds of the averaging window |
| Eliminating α | 516 | emphasis | **Eliminating α.** *α* appears with coefficient 1 in every stamp and causal cons |
| enclosure | 622 | emphasis | The **accepted region** is the set of all (*d_on*, *d_off*) in the square [−0.75 |
| end | 428 | emphasis | - a `timestamp` date, written *n_i* once converted to Unix-epoch nanoseconds. Th |
| end of record 0 | 471 | emphasis | The estimator's identity is `powermetrics_native_second_rate_aware_set_membershi |
| energy-efficiency benchmark | 336 | repeated hyphenated compound | JouleSort established that an energy-efficiency benchmark needs a fixed workload |
| estimator_revision | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| events.jsonl | 410 | backticked identifier | 1. A run bundle at `<runs root>/<run id>/`. `config.json` identifies the conditi |
| extrapolation | 272 | emphasis | The planning disclosure was `C = F + B`, where F is the applicable cell floor an |
| fail-closed | 214 | emphasis | If a required measurement is missing, malformed, outside its fixed limit, or inc |
| fiducial | 80 | curated seed, emphasis | <!-- evidence: runs_window_a_20260722/instrument_validation/20260722T145535-e941 |
| field_ch | 434 | backticked identifier | - the per-channel powers in watts, `rail_power_w[ch] = field_ch / 1000` for each |
| fingerprint | 396 | emphasis | This appendix separates two tasks. *Re-derivation* recomputes reported values fr |
| first-record endpoint | 49 | repeated hyphenated compound | The clock anchor uses five wall-clock readings, each bracketed by monotonic-cloc |
| first_parse | 70 | backticked identifier | \| `first_parse` \| 1784757336.604396 \| 458737.509839458 \| 458737.509840291 \| 0.00 |
| first_parse_lag_exceeded | 531 | backticked identifier | 6. First-parse lag: the largest value over the feasible set of min_v (*h_v*(β) + |
| FIT_HALF_RANGE_S | 600 | backticked identifier | 6. **The search (constrained coordinate descent).** The two shifts are searched  |
| fitted_shift_exceeds_validation_limit | 616 | backticked identifier | 8. **Shift limit.** Require \|*d_on*\| < 0.5 s and \|*d_off*\| < 0.5 s (`MAX_VALIDAT |
| floor gate | 185 | curated seed | Each arrow means that the named value supplies the calculation to its right. The |
| floor-binding limitation | 350 | repeated hyphenated compound | The registered L1 floor-binding limitation prevents describing the present chain |
| floor_gate_j | 185 | backticked identifier, curated seed | Each arrow means that the named value supplies the calculation to its right. The |
| Fraction | 471 | backticked identifier | The estimator's identity is `powermetrics_native_second_rate_aware_set_membershi |
| Fresh collection | 396 | emphasis | This appendix separates two tasks. *Re-derivation* recomputes reported values fr |
| Full-System Power | 365 | repeated hyphenated compound | 4. D. Economou, S. Rivoire, C. Kozyrakis, and P. Ranganathan. “Full-System Power |
| g_v | 520 | emphasis | - for every stamp *v*: *A* ≥ *g_v*(β) + *β*·*k_pre* (5 rows). |
| g_v′ | 518 | emphasis | - for every ordered pair of stamps (*v*, *v′*), including *v* = *v′*: *g_v′*(β)  |
| gamma | 272 | curated seed | The planning disclosure was `C = F + B`, where F is the applicable cell floor an |
| Gate 1 | 204 | emphasis | In the lower lane, the gray input box contains the measured contrast: its point  |
| Gate 2 | 204 | emphasis | In the lower lane, the gray input box contains the measured contrast: its point  |
| generated-state checks | 237 | repeated hyphenated compound | The repository artifact guide holds the maintainer-facing path conventions, free |
| gpu.idle_ratio | 222 | backticked identifier | - In those same idle records, fewer than \\(40\\%\\) of raw `gpu.idle_ratio` values |
| gpu_energy | 429 | backticked identifier | - three processor power fields, `cpu_power`, `gpu_power`, `ane_power`, each in m |
| gpu_freq_mhz_mean | 222 | backticked identifier | - In those same idle records, fewer than \\(40\\%\\) of raw `gpu.idle_ratio` values |
| gpu_power | 425 | backticked identifier | **The instrument and its records.** The instrument is macOS `powermetrics`, run  |
| graphics-processor pulses | 19 | repeated hyphenated compound | For runs that share the same phase, workload, model, hardware, software, and pow |
| guard factor | 180 | curated seed | checked energy/block intervals -> point formulas -> every joint corner -> guard  |
| guarded | 156 | curated seed | Fewer than five independent units produce diagnostic components but no publishab |
| H | 544 | emphasis | 1. **H** prices *where record 0's end sits on the wall clock* — the half-width o |
| h_v | 518 | emphasis | - for every ordered pair of stamps (*v*, *v′*), including *v* = *v′*: *g_v′*(β)  |
| half-width | 442 | emphasis | **Clock stamps.** The controller reads time with a *paired stamp*: it reads the  |
| half-width of | 450 | repeated hyphenated compound | **Commanded pulses.** A commanded pulse *P* is a pair of stamps, one taken immed |
| hardware_model | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| held-out probes | 97 | repeated hyphenated compound | \| **Drift and recovery:** does an allowance contain probes excluded from constru |
| held-out reference | 88 | repeated hyphenated compound | The frozen P06 result specification contains the predicates below. D-152 supplie |
| Holm family | 99 | curated seed | The two inferential properties—the null-mean containment and prefill-invariance  |
| HotCarbon '26 | 380 | emphasis | 19. B. Ruf and M. Detyniecki. “The Cost of Context: Profiling the Energy Footpri |
| HotPower '08 | 379 | emphasis | 18. S. Rivoire, P. Ranganathan, and C. Kozyrakis. “A Comparison of High-Level Fu |
| i | 425 | emphasis | **The instrument and its records.** The instrument is macOS `powermetrics`, run  |
| I_i | 448 | emphasis | **Trace intervals.** After the trace is anchored (A.3.4), each record becomes a  |
| Identical-condition null | 95 | emphasis, repeated hyphenated compound | \| **Identical-condition null:** does an A/B/B/A comparison manufacture a differe |
| idle-subtracted request | 97 | repeated hyphenated compound | \| **Drift and recovery:** does an allowance contain probes excluded from constru |
| IEEE Computer | 376 | emphasis | 15. K.-D. Lange. “Identifying Shades of Green: The SPECpower Benchmarks.” *IEEE  |
| Inputs and their admission checks | 482 | emphasis | **Inputs and their admission checks.** All five stamps must be present and well  |
| instrument_calibration | 411 | backticked identifier | 2. The bundle's `instrument_calibration/` subtree. Its `raw/powermetrics.plist`  |
| instrument_evidence.json | 411 | backticked identifier | 2. The bundle's `instrument_calibration/` subtree. Its `raw/powermetrics.plist`  |
| Interior set | 585 | emphasis | 2. **Interior set**: intervals in *L* with start ≥ *on* + 0.25 and end ≤ *off* − |
| invalid | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| is_delta | 430 | backticked identifier | - an `is_delta` flag, which must be `true` (the record is an interval aggregate, |
| issued degrees of freedom | 264 | curated seed | The two contrasts will form one Holm family with alpha = 0.05 and m = 2, a diffe |
| j | 450 | emphasis | **Commanded pulses.** A commanded pulse *P* is a pair of stamps, one taken immed |
| k | 464 | emphasis | 7. Drives the **59 measured pulses**. Pulse *j* (0-based) is commanded on at pla |
| k_parse | 514 | emphasis | Because *m_0* is *by definition* *mb*(S_pre) · 10⁹, the first bracket collapses  |
| k_pre | 514 | emphasis | Because *m_0* is *by definition* *mb*(S_pre) · 10⁹, the first bracket collapses  |
| L | 584 | emphasis | 1. **Local set** *L*: all trace intervals overlapping the margin window [*on* −  |
| limit | 471 | emphasis | The estimator's identity is `powermetrics_native_second_rate_aware_set_membershi |
| load-regime transfer | 53 | repeated hyphenated compound | This calibrates edge placement under commanded GPU pulses and then transports th |
| Local set | 584 | emphasis | 1. **Local set** *L*: all trace intervals overlapping the margin window [*on* −  |
| LOCAL_MARGIN_S | 573 | backticked identifier | **Baseline set and robust scale.** Define the *margin window* of pulse *j* as [* |
| loss limit | 618 | emphasis | **The accepted region.** The fitted point is not the output. Define the **loss l |
| Loss_flat | 615 | emphasis | 7. **Significance.** Let *Loss_flat* = Σ_{I_i ∈ L} ρ((*y_i* − *b*)/σ), the loss  |
| low_power_mode | 220 | backticked identifier | - After any operator or stage intervention, it waits \\(180\\) s with no experimen |
| m | 478 | emphasis | The wall clock is assumed affine in monotonic time over the capture: wall(*m*) = |
| M3 | 21 | curated seed | The primary research question is therefore plain: under the corrected clock mode |
| m_0 | 476 | emphasis | - *α*, the wall time (ns) at the monotonic instant *m_0* = *mb*(S_pre) · 10⁹, i. |
| ma | 442 | emphasis | **Clock stamps.** The controller reads time with a *paired stamp*: it reads the  |
| ma_v | 484 | emphasis | **Wall-minus-monotonic span.** Index the five stamps by *v* (reserving *j* for p |
| mac-measurement-lock.txt | 404 | backticked identifier | Fresh collection additionally requires the configured Apple-silicon instrument,  |
| Magnitude | 195 | emphasis | 1. **Magnitude:** the strict inequality \\(\|\\hat\\Delta\|>F_{\\mathrm{cell}}\\) holds |
| margin window | 573 | emphasis | **Baseline set and robust scale.** Define the *margin window* of pulse *j* as [* |
| math.fsum | 421 | backticked identifier | Two conventions hold throughout. All times are in seconds unless marked "ns" (na |
| MAX_AFFINE_CLOCK_RESIDUAL_S | 480 | backticked identifier | **Model condition (stated because the containment claim depends on it).** The es |
| MAX_AUTHENTICATED_GAP_ERROR_S | 567 | backticked identifier | **Authenticating the executed schedule.** From the pulse stamps and the trimmed  |
| MAX_CLOCK_RATE_DEVIATION_PPM | 529 | backticked identifier | 4. *β_lo* = min *β*, *β_hi* = max *β* over the full set. If either equals its bo |
| MAX_FIRST_PARSE_LAG_S | 531 | backticked identifier | 6. First-parse lag: the largest value over the feasible set of min_v (*h_v*(β) + |
| MAX_VALIDATED_EDGE_SHIFT_S | 616 | backticked identifier | 8. **Shift limit.** Require \|*d_on*\| < 0.5 s and \|*d_off*\| < 0.5 s (`MAX_VALIDAT |
| mb | 442 | emphasis | **Clock stamps.** The controller reads time with a *paired stamp*: it reads the  |
| mb_v | 484 | emphasis | **Wall-minus-monotonic span.** Index the five stamps by *v* (reserving *j* for p |
| metadata.config_sha256 | 410 | backticked identifier | 1. A run bundle at `<runs root>/<run id>/`. `config.json` identifies the conditi |
| metrology-aware interval | 196 | repeated hyphenated compound | 2. **Direction and registered inference:** both the metrology-aware interval and |
| mlx_version | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| model-size comparison | 11 | repeated hyphenated compound | Phase-energy measurements can repeat yet still charge energy to the wrong stage  |
| model_fit_not_significant | 615 | backticked identifier | 7. **Significance.** Let *Loss_flat* = Σ_{I_i ∈ L} ρ((*y_i* − *b*)/σ), the loss  |
| mx.eval | 464 | backticked identifier | 7. Drives the **59 measured pulses**. Pulse *j* (0-based) is commanded on at pla |
| n_i | 428 | emphasis | - a `timestamp` date, written *n_i* once converted to Unix-epoch nanoseconds. Th |
| Native-label constraints | 499 | emphasis | **Native-label constraints.** For each record *i*, with *δ* = 250 µs = 250 000 n |
| never-adjusted counter | 65 | repeated hyphenated compound | The following table and arithmetic reconstruct one retained diagnostic capture f |
| never-zero allowance | 51 | repeated hyphenated compound | Finally, the pre-window and post-window capture bounds form a bracket. A differe |
| no | 204 | emphasis | In the lower lane, the gray input box contains the measured contrast: its point  |
| no_plateau_interior_intervals | 585 | backticked identifier | 2. **Interior set**: intervals in *L* with start ≥ *on* + 0.25 and end ≤ *off* − |
| not presently open to independent re-reduction | 398 | emphasis | The code repository is available to the project, but the claim-bearing evidence  |
| not resolvable | 204 | emphasis | In the lower lane, the gray input box contains the measured contrast: its point  |
| not_resolvable_sample_count | 254 | backticked identifier | A phase is resolvable only when at least three records count; fewer yields the n |
| null block | 187 | curated seed | Passing the identical-condition null block at the corner-widened resolution boun |
| Numeric-padding check | 490 | emphasis, repeated hyphenated compound | **Numeric-padding check.** Let *w_max* = the largest \|*w_v*\| over the five stamp |
| numeric_padding_insufficient | 490 | backticked identifier | **Numeric-padding check.** Let *w_max* = the largest \|*w_v*\| over the five stamp |
| NUMERIC_PADDING_S | 540 | backticked identifier | where roundup is outward rounding to binary64 and 10⁻⁶ s is `NUMERIC_PADDING_S`. |
| O | 573 | emphasis | **Baseline set and robust scale.** Define the *margin window* of pulse *j* as [* |
| off | 450 | emphasis | **Commanded pulses.** A commanded pulse *P* is a pair of stamps, one taken immed |
| off_j | 567 | emphasis | **Authenticating the executed schedule.** From the pulse stamps and the trimmed  |
| on | 450 | emphasis | **Commanded pulses.** A commanded pulse *P* is a pair of stamps, one taken immed |
| on_j | 573 | emphasis | **Baseline set and robust scale.** Define the *margin window* of pulse *j* as [* |
| on_{j+1} | 567 | emphasis | **Authenticating the executed schedule.** From the pulse stamps and the trimmed  |
| operating-system build | 304 | repeated hyphenated compound | The transferable lesson for other software counters is procedural: check how cou |
| operative floor | 94 | curated seed | \| **Workload response:** do request and decode energy increase with realized out |
| os_build | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| outward | 471 | emphasis | The estimator's identity is `powermetrics_native_second_rate_aware_set_membershi |
| P | 450 | emphasis | **Commanded pulses.** A commanded pulse *P* is a pair of stamps, one taken immed |
| p2015-df-ph-decode-abs-r03 | 256 | backticked identifier | For a concrete case, retained bundle `p2015-df-ph-decode-abs-r03` supplies the t |
| p256 | 198 | curated seed | The primary family uses two-sided Holm correction at \\(\\alpha=0.05\\) with \\(m=2\\ |
| p_0 | 438 | emphasis | *p_i* and *E_i* are used for only one thing: a health check that the record's po |
| p_i | 435 | emphasis | - the **combined power** *p_i* = Σ_ch `rail_power_w[ch]`, i.e. cpu + gpu + ane,  |
| paired stamp | 442 | emphasis | **Clock stamps.** The controller reads time with a *paired stamp*: it reads the  |
| Per-pulse fit | 582 | emphasis | **Per-pulse fit.** For pulse *j* with commanded (*on*, *off*, *u_on*, *u_off*): |
| phase | 113 | backticked identifier | The only window classes are `request` and `phase`. Gross and idle-subtracted ene |
| Phase accounting | 96 | emphasis | \| **Phase accounting:** do the two phase energies close to request energy, stay  |
| phase-aware placement | 344 | repeated hyphenated compound | Split and disaggregated inference remain a demanding application rather than thi |
| phase-boundary attribution | 21 | repeated hyphenated compound | The primary research question is therefore plain: under the corrected clock mode |
| phase-edge placement | 103 | repeated hyphenated compound | **Diagnostic-era evidence of the phenomenon, not a current instrument property.* |
| plateau_below_minimum | 586 | backticked identifier | 3. **Amplitude** *a* = median{ *y_i* : interior } − *b*, and **robust SNR** = *a |
| PLATEAU_INSET_S | 585 | backticked identifier | 2. **Interior set**: intervals in *L* with start ≥ *on* + 0.25 and end ≤ *off* − |
| point-only repeatability | 21 | curated seed, repeated hyphenated compound | The primary research question is therefore plain: under the corrected clock mode |
| point-only value | 185 | repeated hyphenated compound | Each arrow means that the named value supplies the calculation to its right. The |
| post-window calibration | 51 | repeated hyphenated compound | Finally, the pre-window and post-window capture bounds form a bracket. A differe |
| post_parse | 73 | backticked identifier | \| `post_parse` \| 1784757533.8891652 \| 458934.794166 \| 458934.7941665 \| 0.0000010 |
| Power and Performance Benchmark Methodology | 363 | emphasis | 2. Standard Performance Evaluation Corporation. *Power and Performance Benchmark |
| power.adapter_watts | 220 | backticked identifier | - After any operator or stage intervention, it waits \\(180\\) s with no experimen |
| power.external_connected | 220 | backticked identifier | - After any operator or stage intervention, it waits \\(180\\) s with no experimen |
| power_policy | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| power_source | 220 | backticked identifier | - After any operator or stage intervention, it waits \\(180\\) s with no experimen |
| power_trace.csv | 410 | backticked identifier | 1. A run bundle at `<runs root>/<run id>/`. `config.json` identifies the conditi |
| powermetrics | 17 | emphasis | This physical distinction, rather than a tour of the measurement system, is the  |
| powermetrics.plist | 410 | backticked identifier | 1. A run bundle at `<runs root>/<run id>/`. `config.json` identifies the conditi |
| powermetrics_native_second_rate_aware_set_membership_v1 | 471 | backticked identifier | The estimator's identity is `powermetrics_native_second_rate_aware_set_membershi |
| powermetrics_pulse_fiducial_v3 | 456 | backticked identifier | The capture is protocol `powermetrics_pulse_fiducial_v3`. (*Fiducial* here means |
| powermetrics_sha256 | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| pre-spawn stamp | 476 | repeated hyphenated compound | - *α*, the wall time (ns) at the monotonic instant *m_0* = *mb*(S_pre) · 10⁹, i. |
| pre-train quiet | 461 | repeated hyphenated compound | 4. Takes stamp **S_start** (`sampling_started`), then rests 5 s (the pre-train q |
| pre-window and | 51 | repeated hyphenated compound | Finally, the pre-window and post-window capture bounds form a bracket. A differe |
| pre_spawn | 69 | backticked identifier | \| `pre_spawn` \| 1784757335.502742 \| 458736.4081875 \| 458736.408188666 \| 0.000001 |
| prefill | 35 | emphasis | JouleWise assigns each *powermetrics* sampling interval to prompt processing (*p |
| Procedure | 625 | emphasis | - **Procedure.** Start with the single cell [−0.75, 0.75]² on a last-in-first-ou |
| processor_combined_power_w_p95 | 221 | backticked identifier | - The pre-run idle baseline samples for \\(30\\) s at a requested \\(10\\) Hz and mu |
| Projection | 626 | emphasis | - **Projection.** The region's enclosure is the bounding box of the retained cel |
| prompt-processing energy | 247 | repeated hyphenated compound | In a retained diagnostic-era population of 50 Qwen2.5 1.5B prompt-processing pha |
| protocol_sha256 | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| provided that | 480 | emphasis | **Model condition (stated because the containment claim depends on it).** The es |
| pulse train | 11 | curated seed | Phase-energy measurements can repeat yet still charge energy to the wrong stage  |
| pulse-derived bound | 53 | repeated hyphenated compound | This calibrates edge placement under commanded GPU pulses and then transports th |
| pulse-derived timing | 294 | repeated hyphenated compound | **Limitation 1 is an untested load-regime transfer.** The timing bound is charac |
| pulse-fit (accepted-region) algorithm | 419 | emphasis | This appendix specifies the two calculations behind the calibration numbers in S |
| pulse-fit accepted-region algorithm | 419 | repeated hyphenated compound | This appendix specifies the two calculations behind the calibration numbers in S |
| pulse_command_off | 464 | backticked identifier | 7. Drives the **59 measured pulses**. Pulse *j* (0-based) is commanded on at pla |
| pulse_command_on | 464 | backticked identifier | 7. Drives the **59 measured pulses**. Pulse *j* (0-based) is commanded on at pla |
| pulse_protocol_id | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| pyproject.toml | 402 | backticked identifier | Re-derivation requires a full-history checkout at the released revision, Python  |
| q | 440 | emphasis | **Cumulative elapsed time.** Define *q_0* = 0 and *q_i* = *e_1* + *e_2* + … + *e |
| q_0 | 440 | emphasis | **Cumulative elapsed time.** Define *q_0* = 0 and *q_i* = *e_1* + *e_2* + … + *e |
| q_i | 440 | emphasis | **Cumulative elapsed time.** Define *q_0* = 0 and *q_i* = *e_1* + *e_2* + … + *e |
| Qwen | 247 | curated seed | In a retained diagnostic-era population of 50 Qwen2.5 1.5B prompt-processing pha |
| Qwen2.5 | 247 | curated seed | In a retained diagnostic-era population of 50 Qwen2.5 1.5B prompt-processing pha |
| r | 442 | emphasis | **Clock stamps.** The controller reads time with a *paired stamp*: it reads the  |
| r_max | 546 | emphasis | 3. **r_max** prices the *reported resolution of the clocks* that produced the st |
| r_pre | 514 | emphasis | Because *m_0* is *by definition* *mb*(S_pre) · 10⁹, the first bracket collapses  |
| r_v | 492 | emphasis | **Stamp constraints.** For each stamp *v* (all quantities converted to ns by mul |
| rail_power_w | 434 | backticked identifier | - the per-channel powers in watts, `rail_power_w[ch] = field_ch / 1000` for each |
| RAPL in Action | 324 | emphasis | Khan et al.'s *RAPL in Action* and Jay et al. own the gain axis: how accurately  |
| rate_aware_native_set_empty | 526 | backticked identifier | 1. Native rows alone infeasible → `rate_aware_native_set_empty`. |
| Re-derivation | 396 | emphasis | This appendix separates two tasks. *Re-derivation* recomputes reported values fr |
| re-derivation check | 77 | repeated hyphenated compound | <!-- replay fence: scripts/check_paper_replay_fence.py is the mechanical re-deri |
| Reading the pulses | 563 | emphasis | **Reading the pulses.** The command event log is scanned for on/off events and p |
| record | 425 | emphasis | **The instrument and its records.** The instrument is macOS `powermetrics`, run  |
| record energy | 436 | emphasis | - the **record energy** *E_i* = (`cpu_energy` + `gpu_energy` + `ane_energy`) / 1 |
| record spacing | 256 | emphasis | For a concrete case, retained bundle `p2015-df-ph-decode-abs-r03` supplies the t |
| refusal | 11 | curated seed, emphasis | Phase-energy measurements can repeat yet still charge energy to the wrong stage  |
| refused | 47 | backticked identifier, curated seed, emphasis | For each commanded pulse, the detector estimates resting GPU power from samples  |
| REGION_COVERAGE_RESOLUTION_S | 625 | backticked identifier | - **Procedure.** Start with the single cell [−0.75, 0.75]² on a last-in-first-ou |
| reported resolution of the clocks | 546 | emphasis | 3. **r_max** prices the *reported resolution of the clocks* that produced the st |
| request | 113 | backticked identifier | The only window classes are `request` and `phase`. Gross and idle-subtracted ene |
| resolution bound | 11 | curated seed | Phase-energy measurements can repeat yet still charge energy to the wrong stage  |
| resolvability | 23 | curated seed | The planned model-size comparison will demonstrate how this measurement result g |
| resolvable | 23 | curated seed | The planned model-size comparison will demonstrate how this measurement result g |
| RESULT PENDING ISSUED ARTIFACTS | 189 | emphasis | The four prospective phase-cell values and their decompositions remain unavailab |
| retain the entire cell | 625 | emphasis | - **Procedure.** Start with the single cell [−0.75, 0.75]² on a last-in-first-ou |
| right-pointing arrow | 202 | repeated hyphenated compound | Figure 3 separates evidence refusal from the two claim gates. A thin horizontal  |
| robust SNR | 586 | emphasis | 3. **Amplitude** *a* = median{ *y_i* : interior } − *b*, and **robust SNR** = *a |
| robust_snr_below_minimum | 586 | backticked identifier | 3. **Amplitude** *a* = median{ *y_i* : interior } − *b*, and **robust SNR** = *a |
| rollover | 460 | emphasis | 3. Waits until the whole-second `timestamp` label of a record advances at least  |
| run-to-run scatter | 21 | repeated hyphenated compound | The primary research question is therefore plain: under the corrected clock mode |
| run-to-run variation | 11 | repeated hyphenated compound | Phase-energy measurements can repeat yet still charge energy to the wrong stage  |
| runtime-recorded boundary | 37 | repeated hyphenated compound | Figure 1 names the mechanism. Its horizontal time axis, vertical power axis, pal |
| S | 442 | emphasis | **Clock stamps.** The controller reads time with a *paired stamp*: it reads the  |
| s_coarse | 600 | emphasis | 6. **The search (constrained coordinate descent).** The two shifts are searched  |
| s_fine | 600 | emphasis | 6. **The search (constrained coordinate descent).** The two shifts are searched  |
| S_parse | 459 | emphasis | 2. Polls the output file until the first record parses, then takes stamp **S_par |
| S_post | 465 | emphasis | 8. Rests 5 s, takes stamp **S_stop** (`sampling_stopped`), terminates `powermetr |
| S_pre | 458 | emphasis | 1. Takes stamp **S_pre** (named `pre_spawn`), then spawns `powermetrics`. |
| S_start | 461 | emphasis | 4. Takes stamp **S_start** (`sampling_started`), then rests 5 s (the pre-train q |
| S_stop | 465 | emphasis | 8. Rests 5 s, takes stamp **S_stop** (`sampling_stopped`), terminates `powermetr |
| sampling record | 23 | curated seed | The planned model-size comparison will demonstrate how this measurement result g |
| sampling-record interval | 256 | repeated hyphenated compound | For a concrete case, retained bundle `p2015-df-ph-decode-abs-r03` supplies the t |
| sampling-record interval width | 256 | emphasis | For a concrete case, retained bundle `p2015-df-ph-decode-abs-r03` supplies the t |
| sampling_interval_ms | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| sampling_started | 71 | backticked identifier | \| `sampling_started` \| 1784757337.0900722 \| 458737.995513416 \| 458737.995514666  |
| sampling_stopped | 72 | backticked identifier | \| `sampling_stopped` \| 1784757533.877846 \| 458934.782846541 \| 458934.782848041 \| |
| screensaver_engaged | 220 | backticked identifier | - After any operator or stage intervention, it waits \\(180\\) s with no experimen |
| Section 1 | 13 | section heading | ## 1. Introduction |
| Section 10 | 354 | section heading | ## 10. Conclusion |
| Section 11 | 360 | section heading | ## 11. References |
| Section 2 | 33 | section heading | ## 2. In-window calibration method |
| Section 3 | 84 | section heading | ## 3. Instrument characterization |
| Section 4 | 109 | section heading | ## 4. The resolution bound and how it is composed |
| Section 5 | 212 | section heading | ## 5. Collection stops when required evidence fails |
| Section 6 | 239 | section heading | ## 6. Demonstration results |
| Section 7 | 292 | section heading | ## 7. Discussion and limitations |
| Section 8 | 320 | section heading | ## 8. Related work |
| Section 9 | 346 | section heading | ## 9. Evidence and code availability |
| set membership | 471 | emphasis | The estimator's identity is `powermetrics_native_second_rate_aware_set_membershi |
| Shift limit | 616 | emphasis | 8. **Shift limit.** Require \|*d_on*\| < 0.5 s and \|*d_off*\| < 0.5 s (`MAX_VALIDAT |
| short-prefill negative result | 356 | curated seed | The capstone’s central outcome is the registered attribution-dominance test. For |
| Significance | 615 | emphasis | 7. **Significance.** Let *Loss_flat* = Σ_{I_i ∈ L} ρ((*y_i* − *b*)/σ), the loss  |
| span | 484 | emphasis | **Wall-minus-monotonic span.** Index the five stamps by *v* (reserving *j* for p |
| Spurious-plateau check on the baseline set | 580 | emphasis | **Spurious-plateau check on the baseline set.** The check is evaluated once, aft |
| Stamp constraints | 492 | emphasis | **Stamp constraints.** For each stamp *v* (all quantities converted to ns by mul |
| summary_metrics.json | 410 | backticked identifier | 1. A run bundle at `<runs root>/<run id>/`. `config.json` identifies the conditi |
| support interval | 249 | curated seed | The rule is mechanical. A *powermetrics* record has a support interval. It count |
| t | 264 | emphasis | The two contrasts will form one Holm family with alpha = 0.05 and m = 2, a diffe |
| t_0 | 561 | emphasis | **Anchoring.** With the point anchor *A* (seconds), record *i*'s end time *t_i*  |
| t_i | 448 | emphasis | **Trace intervals.** After the trace is anchored (A.3.4), each record becomes a  |
| T_warm | 565 | emphasis | **Trimming warm-ups.** Let *T_warm* = the wall time of the last warm-up's off-st |
| The accepted region | 618 | emphasis | **The accepted region.** The fitted point is not the output. Define the **loss l |
| The feasible set and the solver | 522 | emphasis | **The feasible set and the solver.** The variables are boxed: *β* ∈ [1 − 10⁻³, 1 |
| The instrument and its records | 425 | emphasis | **The instrument and its records.** The instrument is macOS `powermetrics`, run  |
| The model | 473 | emphasis | **The model.** Two unknowns: |
| The model and the objective | 588 | emphasis | 5. **The model and the objective.** For candidate edge shifts (*d_on*, *d_off*)  |
| The rule is a count | 256 | emphasis | For a concrete case, retained bundle `p2015-df-ph-decode-abs-r03` supplies the t |
| The search (constrained coordinate descent | 600 | emphasis | 6. **The search (constrained coordinate descent).** The two shifts are searched  |
| thermal_pressure | 220 | backticked identifier | - After any operator or stage intervention, it waits \\(180\\) s with no experimen |
| time.monotonic | 421 | backticked identifier | Two conventions hold throughout. All times are in seconds unless marked "ns" (na |
| time.time | 421 | backticked identifier | Two conventions hold throughout. All times are in seconds unless marked "ns" (na |
| timestamp | 428 | backticked identifier | - a `timestamp` date, written *n_i* once converted to Unix-epoch nanoseconds. Th |
| timing-widened | 21 | curated seed | The primary research question is therefore plain: under the corrected clock mode |
| total standard error | 264 | curated seed | The two contrasts will form one Holm family with alpha = 0.05 and m = 2, a diffe |
| trace interval | 448 | emphasis | **Trace intervals.** After the trace is anchored (A.3.4), each record becomes a  |
| Trace intervals | 448 | emphasis | **Trace intervals.** After the trace is anchored (A.3.4), each record becomes a  |
| transfer | 11 | curated seed | Phase-energy measurements can repeat yet still charge energy to the wrong stage  |
| transport | 53 | curated seed | This calibrates edge placement under commanded GPU pulses and then transports th |
| Trimming warm-ups | 565 | emphasis | **Trimming warm-ups.** Let *T_warm* = the wall time of the last warm-up's off-st |
| true | 430 | backticked identifier | - an `is_delta` flag, which must be `true` (the record is an interval aggregate, |
| two | 460 | emphasis | 3. Waits until the whole-second `timestamp` label of a record advances at least  |
| u_off | 450 | emphasis | **Commanded pulses.** A commanded pulse *P* is a pair of stamps, one taken immed |
| u_on | 450 | emphasis | **Commanded pulses.** A commanded pulse *P* is a pair of stamps, one taken immed |
| v | 484 | emphasis | **Wall-minus-monotonic span.** Index the five stamps by *v* (reserving *j* for p |
| valid | 652 | backticked identifier | The evidence file is marked `valid` only if all of the following hold: every one |
| values | 522 | emphasis | **The feasible set and the solver.** The variables are boxed: *β* ∈ [1 − 10⁻³, 1 |
| v′ | 518 | emphasis | - for every ordered pair of stamps (*v*, *v′*), including *v* = *v′*: *g_v′*(β)  |
| w | 442 | emphasis | **Clock stamps.** The controller reads time with a *paired stamp*: it reads the  |
| w_max | 490 | emphasis | **Numeric-padding check.** Let *w_max* = the largest \|*w_v*\| over the five stamp |
| w_v | 484 | emphasis | **Wall-minus-monotonic span.** Index the five stamps by *v* (reserving *j* for p |
| wall-clock time | 448 | repeated hyphenated compound | **Trace intervals.** After the trace is anchored (A.3.4), each record becomes a  |
| Wall-minus-monotonic span | 484 | emphasis | **Wall-minus-monotonic span.** Index the five stamps by *v* (reserving *j* for p |
| wall_minus_monotonic_span_exceeded | 488 | backticked identifier | over the five stamps, in seconds. These two subtractions are the one place the e |
| warm-up pulses | 45 | repeated hyphenated compound | Immediately before and after each science window—one uninterrupted measurement s |
| warmup_command_off | 462 | backticked identifier | 5. Drives 3 **warm-up pulses**, each 1 s of GPU work followed by a 1.5 s rest. E |
| warmup_command_on | 462 | backticked identifier | 5. Drives 3 **warm-up pulses**, each 1 s of GPU work followed by a 1.5 s rest. E |
| whole set | 571 | emphasis | The forcing problem: a 1 s rectangular GPU pulse, sampled by an instrument avera |
| whole-second label | 49 | repeated hyphenated compound | The clock anchor uses five wall-clock readings, each bracketed by monotonic-cloc |
| whole-system totals | 294 | repeated hyphenated compound | **Limitation 1 is an untested load-regime transfer.** The timing bound is charac |
| whole-window | 57 | curated seed | The pale lower inset expands one A/B/B/A block. Its black vertical axis is measu |
| whole-window drift | 57 | repeated hyphenated compound | The pale lower inset expands one A/B/B/A block. Its black vertical axis is measu |
| whole-window verdict | 413 | repeated hyphenated compound | 4. The append-only whole-window verdict, which binds admitted members, preserved |
| Widening by stamp uncertainty | 633 | emphasis | **Widening by stamp uncertainty.** The commanded edges themselves are known only |
| window closes | 225 | emphasis | A stage attempt stops at its first member failure. If the same cause fails a win |
| within-capture wall-versus-elapsed drift | 545 | emphasis | 2. **span** prices *within-capture wall-versus-elapsed drift*. It is needed beca |
| Worked current-capture arithmetic | 79 | emphasis | **Worked current-capture arithmetic.** One retained current-estimator derivation |
| Workload response | 94 | emphasis | \| **Workload response:** do request and decode energy increase with realized out |
| worst excursion | 644 | emphasis | A pulse is **detected** when it passes every check of A.3.5 and so carries two w |
| y_i | 448 | emphasis | **Trace intervals.** After the trace is anchored (A.3.4), each record becomes a  |
| yes | 204 | emphasis | In the lower lane, the gray input box contains the measured contrast: its point  |
| z_i | 624 | emphasis | - **Cell lower bound.** For a rectangle *C* = [on_lo, on_hi] × [off_lo, off_hi]  |
| }\\) and \\(U_{\\mathrm{cmp} | 148 | emphasis | 3. A point value hides timing uncertainty, so each independent energy or block d |
| §1 | 13 | section heading | ## 1. Introduction |
| §10 | 354 | section heading | ## 10. Conclusion |
| §11 | 360 | section heading | ## 11. References |
| §2 | 33 | section heading | ## 2. In-window calibration method |
| §3 | 84 | section heading | ## 3. Instrument characterization |
| §4 | 109 | section heading | ## 4. The resolution bound and how it is composed |
| §5 | 212 | section heading | ## 5. Collection stops when required evidence fails |
| §6 | 239 | section heading | ## 6. Demonstration results |
| §7 | 292 | section heading | ## 7. Discussion and limitations |
| §8 | 320 | section heading | ## 8. Related work |
| §9 | 346 | section heading | ## 9. Evidence and code availability |
| α | 476 | emphasis | - *α*, the wall time (ns) at the monotonic instant *m_0* = *mb*(S_pre) · 10⁹, i. |
| β | 475 | emphasis | - *β*, the rate of the wall clock relative to the monotonic clock (dimensionless |
| β_hi | 529 | emphasis | 4. *β_lo* = min *β*, *β_hi* = max *β* over the full set. If either equals its bo |
| β_lo | 529 | emphasis | 4. *β_lo* = min *β*, *β_hi* = max *β* over the full set. If either equals its bo |
| δ | 499 | emphasis | **Native-label constraints.** For each record *i*, with *δ* = 250 µs = 250 000 n |
| τ_0 | 464 | emphasis | 7. Drives the **59 measured pulses**. Pulse *j* (0-based) is commanded on at pla |
| τ_j | 464 | emphasis | 7. Drives the **59 measured pulses**. Pulse *j* (0-based) is commanded on at pla |
| τ_{j+1} | 464 | emphasis | 7. Drives the **59 measured pulses**. Pulse *j* (0-based) is commanded on at pla |
| ẑ_hi | 624 | emphasis | - **Cell lower bound.** For a rectangle *C* = [on_lo, on_hi] × [off_lo, off_hi]  |
| ẑ_lo | 624 | emphasis | - **Cell lower bound.** For a rectangle *C* = [on_lo, on_hi] × [off_lo, off_hi]  |
