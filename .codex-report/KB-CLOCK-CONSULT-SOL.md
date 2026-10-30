gpt-6.1-sol
RECOMMENDATION: (a) retain the 4629.6 s gate for the pinned implementation; it protects the active adapter's capture-wide 5 ms clock-evidence contract, and refuses all three 2.718 ppm arms. Do not shorten the span merely to obtain an arm.

Evidence (source commit a6c68c408; blind consult, high effort)

1. Clock domains and where rate matters

The measured rate is d(REALTIME - RAW)/dRAW, not a measurement of powermetrics elapsed-clock error. `joulewise/clock_reference.py:120` samples RAW/REALTIME/RAW; `joulewise/hazards/clock.py:5` defines the anchor and `:257` fits its slope. The kernel frequency word is diagnostic (`clock.py:24`). Network time OFF does not make REALTIME tick at RAW's rate.

`joulewise/bytes_stream_capture.py:55-69` supplies RAW brackets around time.time() (REALTIME), and `:98`, `:115`, `:148` supplies RAW nanoseconds to the probe. The eight receipts, idle spans, durations, and payload rates therefore use RAW. `scripts/bytes_stream_test.py:301-321` checks RAW identity and budgets endpoint resolution. Sleep/scheduling clocks are not substituted into those receipts.

The adapter is NOT reconstructing every endpoint by subtracting a fixed offset from its wall date. `joulewise/adapters/powermetrics.py:1766-1785` starts current-era record 0 at first_record_endpoint_s, then adds elapsed_ns for records 1..i. `:2012-2013` gives each interval support [endpoint-elapsed, endpoint). Rich telemetry follows the same accumulation (`:1885-1891`). The plist dates remain anchor evidence (`:1820-1825`, `:1849-1857`).

Harvest repeats this construction explicitly: `scripts/bytes_stream_harvest.py:29-39` converts the fitted first endpoint to RAW using capture_stop.start_stamp; `:42-53` adds integer elapsed_ns thereafter. Rails sums CPU/GPU/ANE, GPU uses GPU alone. `:62-73` passes native interval support and RAW receipt edges to the existing integrator. `joulewise/reduce.py:171-179` integrates power times interval overlap. No arm rate_ppm is multiplied into those powers, durations or joules.

Whose elapsed clock? The repository's estimator models elapsed_ns as monotonic duration and the native wall dates as an affine function of it: `joulewise/uncertainty_evidence.py:891-920`. The vendor executable's internal clock_gettime/mach call is not in this Python repository. I cannot certify its precise clock API from this seat. In particular, treating 2.718 ppm of REALTIME-versus-RAW slope as a measured 2.718 ppm error in elapsed_ns would be an unsupported inference. The stream code assumes native durations are usable as RAW durations; the synthetic fixtures satisfy that assumption by construction. No hardware evidence was collected to strengthen it.

There IS a number-bearing wall-clock dependency. The adapter invokes ACTIVE_CAPTURE_ANCHOR_METHOD (`powermetrics.py:542-546`), which is V3 (`uncertainty_evidence.py:1460`). Its affine feasible set uses native dates, accumulated elapsed durations, and wall/RAW stamp brackets (`:1065-1068`, `:1160-1207`, `:1223-1232`); it projects an epoch first endpoint (`:1269-1271`, `:1331-1351`). Thus changing the observed wall rate changes the constraints and potentially that endpoint, even though no explicit arm slope is passed to harvest. Harvest then uses a unit-slope start-offset conversion, rather than projecting the endpoint directly onto RAW through the fitted affine clock.

More decisively, V3 refuses wall-minus-monotonic span above 0.005 s (`uncertainty_evidence.py:40`, `:1090-1125`), adds that span to placement uncertainty (`:1317-1328`), and refuses an effective bound above 0.005 s (`:46`, `:1374-1381`). At a constant 2.718 ppm, 4629.6 s produces 0.0125832528 s of offset movement before read uncertainties: the actual adapter would refuse the resolved anchor even if the arm gate were removed. The synthetic Capture seam (`tests/test_bytes_stream_capture.py:58-85`) supplies an anchor directly; its successful long capture does not exercise this production limitation.

Meter and battery are different. `joulewise/external/km003c_parse.py:252-259` fits unwrapped device milliseconds against host RAW receive stamps; `:264-294` fits one lower-arrival-envelope intercept AND slope; `:350-356` maps the whole stream once. Its clock_rate_ppm is device-versus-RAW, not the hazard's REALTIME-versus-RAW rate. Battery uses poll receive RAW stamps (`:328-336`). Harvest rejects multiple streams and uses RAW spans without a second controller offset (`scripts/bytes_stream_harvest.py:81-103`, `:217-220`). Meter integration is selected-sample mean power times RAW receipt duration (`km003c_parse.py:406-420`). The hazard's slope creates no accumulating meter timing error.

Pass-1 does not use t_stream_max_s as an energy multiplier. The night driver feeds it into the clock hazard (`joulewise/b5/driver.py:577-585`). `joulewise/bytes_analysis.py:587-617` consumes B6's own-session operative bound and rederives the energy envelope; `joulewise/b6/calibration.py:94-102` constructs max(pre,post)+max(abs(pre-post),bracket_screen). The 5 ms contract protects the wall/native alignment model used by the fiducial detector: `uncertainty_evidence.py:911-924` expressly explains that accumulated elapsed support is compared to WALL-epoch pulse commands. It is not a universal 5 ms requirement imposed by the reader's printed precision.

2. Executed timing and energy arithmetic

For a hypothetical unit-slope mapping of a clock with fractional rate error r onto RAW, endpoint displacement at elapsed t is d(t)=r*t. At 2.718 ppm, r=2.718e-6; the stress case is 3r=8.154e-6. These are conditional displacement calculations, NOT observed receipt or meter errors.

The planned schedule follows `bytes_stream_capture.py:26-37`: scan allowance 22*(3*2+4*10+2)=1056 s; each measured call adds 10 s preparation, three 3 s settles, two 57.6 s idles, and 250 or 500 s work. First work starts at 1056+10+3+57.6+3=1129.6 s. Subsequent call starts advance by prior work+134.2 s. Executed Python 3.13 arithmetic:

| Call | Work start/end s | d start/end ms, 2.718 ppm | d start/end ms, 8.154 ppm | 160 W absolute edge bound J, 2.718 ppm |
|---|---:|---:|---:|---:|
| S1 | 1129.6 / 1629.6 | 3.070253 / 4.429253 | 9.210758 / 13.287758 | 1.199921 |
| C1a | 1763.8 / 2013.8 | 4.794008 / 5.473508 | 14.382025 / 16.420525 | 1.642803 |
| C3a | 2148 / 2398 | 5.838264 / 6.517764 | 17.514792 / 19.553292 | 1.976964 |
| C2a | 2532.2 / 2782.2 | 6.882520 / 7.562020 | 20.647559 / 22.686059 | 2.311126 |
| C2b | 2916.4 / 3166.4 | 7.926775 / 8.606275 | 23.780326 / 25.818826 | 2.645288 |
| C3b | 3300.6 / 3550.6 | 8.971031 / 9.650531 | 26.913092 / 28.951592 | 2.979450 |
| C1b | 3684.8 / 3934.8 | 10.015286 / 10.694786 | 30.045859 / 32.084359 | 3.313612 |
| S2 | 4069 / 4569 | 11.059542 / 12.418542 | 33.178626 / 37.255626 | 3.756493 |

The final column is Pmax*(|d_start|+|d_end|), a conservative bound on swapped boundary strips for a nonnegative trace bounded by Pmax. At 40 W divide by four; at 3r multiply by three. Thus those conditional bounds range from 0.299980 to 3.756493 J at the supplied 40-160 W range, or 0.899941 to 11.269480 J at 3r. They are not meter error estimates: the actual meter is on RAW, nor is meter power automatically a certified bound on reported rails. Constant power across all boundaries produces zero window displacement error; a load step depends on the power difference across the displaced edge. A clock-scale error can also stretch a finite pulse by roughly P_excess*r*T (1.359 ms of duration at 500 s, 0.6795 ms at 250 s; triple at 3r). No universal exact joule error follows from watts alone.

Executed synthetic replay:

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m tests.test_bytes_stream_capture --synthetic /tmp/kb-clock-sol-archive`

Completed: 8 records, knee found, rails/GPU/DC/rest RESOLVED. Printed rails and GPU contrasts were 7.000 +/- 0.014 J/GB. Synthetic power is 4 W rails baseline, 2 W GPU baseline, 8 W meter baseline, plus N*(0.05+per_byte*size)/T; per_byte=8e-9 above the synthetic knee and 1e-9 below, doubled for meter (`tests/test_bytes_stream_capture.py:76-80`, `:89-99`). Actual rails work powers were 82.293503, 9.099510, 9.198812, 9.396795 W for S,C1,C3,C2; GPU is 2 W less. Synthetic timing differs from the conservative planned allowances; its capture origin is RAW 1000 s.

I separately executed an in-memory sensitivity experiment: native_trace supplied rows; each support edge x was replaced by origin+round((x-origin)*(1+r)); powers, RAW receipts and meter were held fixed. rail_energy recomputed native overlaps; idle rows were reselected over the unchanged RAW spans; the unchanged read_known_bytes recomputed contrasts. This deliberately injects an elapsed-clock scale mismatch, not the measured wall-rate mechanism. Positive dilation was tested, not asserted as the sign of the Mac's drift.

| Call | Synthetic d start/end ms at r | Payload GB | Comparison bar J | rails/GPU change J at r | change J at 3r |
|---|---:|---:|---:|---:|---:|
| S1 | 0.631777 / 1.989983 | 4883.377816 | 0.027835254 | +0.057886650 | +0.173659910 |
| C1a | 2.327585 / 3.007063 | 26.186088 | 0.000149261 | +0.000372165 | +0.001116496 |
| C3a | 3.344666 / 4.024148 | 52.317651 | 0.000298211 | -0.001203602 | -0.003610803 |
| C2a | 4.361750 / 5.041235 | 104.417198 | 0.000595178 | -0.004041355 | -0.012124069 |
| C2b | 5.378838 / 6.058322 | 104.417198 | 0.000595178 | -0.007935610 | -0.023806829 |
| C3b | 6.395925 / 7.075406 | 52.317651 | 0.000298211 | -0.011910854 | -0.035732560 |
| C1b | 7.413009 / 8.092487 | 26.186088 | 0.000149261 | -0.015710886 | -0.047132661 |
| S2 | 8.431257 / 9.789463 | 4883.377816 | 0.027835254 | +0.542252936 | -0.403242274 |

Triple the displacement column for 3r. Bars are exactly 5.7e-6*(bytes_per_read*N/1e9), the rule used at `tests/test_bytes_stream_harvest.py:25`; 5.7e-6 is already 1% of the smallest printed half-width, not a value to divide by 100 again. For example S1's bar is 0.0278352535486464 J. All eight hypothetical integral changes exceed their bars. S2's sign reversal is plausible: displacement crosses native interval boundaries, so sensitivity is not globally linear.

The reader's rails/GPU delta changed by +4.03661108e-5 J/GB at r and -8.67497127e-5 J/GB at 3r; DC changed by zero, rest by the negative rails change. Both exceed the 5.7e-6 J/GB comparison bar. `scripts/bytes_stream_test.py:649-666` explains the propagation: arm excess is pooled over repeats; cache slope and intercept feed DRAM-minus-cache delta. The palindrome does not guarantee cancellation of nonlinear edge selection or unequal per-dispatch timing. These shifts remain much smaller than this fixture's printed 0.014 J/GB contrast half-width, but that does not excuse exceeding the independent comparison bar.

Does the reader already bound it? Only in part. Harvest supplies one common-shift envelope evaluated over the calibration operative bound (`bytes_stream_harvest.py:200-202`, `:270-281`). `reduce.py:2069-2076` guarantees a common translation envelope, not a dilation; the optional independent-edge term exists but harvest does not pass it. `bytes_stream_test.py:913-926` charges anchor_shift_j to rails/GPU; `:952-954` merely reports operative_timing_bound_s. B6 calibration does not add rate*continuous_capture_age.

In this fixture the operative bound was 0.03242827162932592 s and anchor_shift_j values were [0.219311404, 0.018243249, 0.027191969, 0.041254020, 0.056000003, 0.066423564, 0.073549461, 1.951962011] J. They numerically exceed the individual injected integral changes in this experiment, including 3r. That is empirical coverage here, not a containment proof for arbitrary affine distortion, idle-baseline displacement, or actual Mac powers. The production capture's effective clock bound is also not explicitly maximized into the harvest's operative bound. Therefore “already bounded” is not an adequate justification for silently removing the gate.

3. Gate choice and replay

For the pinned code I choose (a), with its present derivation rather than a newly invented tolerance. h_ms=3.7 is the existing 3.60 ms h_max plus 0.10 ms placement margin; frequency_margin_ppm=0.25 and limit_ms=5 are existing contract values (`hazards/clock.py:73-80`). `:263-271` evaluates h+(abs(rate)+margin)*T/1000. Executed calls to measured_rate_bound(Fraction('2.718'), thresholds):

| T s | Bound ms | Maximum abs rate ppm | Pass |
|---:|---:|---:|---|
| 96.39069404196925 | 3.986087580 | 13.236779122 | yes |
| 335 | 4.694280000 | 3.630597015 | yes |
| 500 | 5.184000000 | 2.350000000 | no |
| 4629.6 | 17.440652800 | 0.030801797 | no |

Each maximum is (5-3.7)*1000/T-0.25. At 3r the continuous bound is 3.7+(8.154+0.25)*4629.6/1000=42.6071584 ms. At r the physical wall offset movement alone is 12.5832528 ms; at 3r it is 37.7497584 ms. The discrepancy with the arm bound is placement and the registered rate margin.

Three recorded 2.718 ppm arms: `docs/process_traces/2026-10-block5/seal2-beta-a5-arm.md:13`, `seal2-beta-a6-arm.md:15`, `seal2-gamma-a1-arm.md:19`. Replaying the recommended gate refuses 3/3; the 500 s alternative also refuses 3/3; the old 335 s and pass-1 spans refuse 0/3. Claim usability under the shorter old contract is consistent with refusing a much longer new capture. It does not prove the Mac is unusable or that these hypothetical joule errors occurred.

This recommendation is an implementation-consistency hold, not a claim that RAW energy physics demands 0.0308 ppm. A useful future change would derive and carry a RAW first-endpoint feasible interval directly from the affine anchor set, retain native elapsed support in RAW, and make a test-specific admission contract whose energy bounds consume that uncertainty. It would also have to address the production adapter's V3 caps and the harvest's bound join. Simply re-anchoring at receipt time or stdout receive time is unsound: neither identifies the native sample endpoint without latency bounds. Switching to V3.1 alone is insufficiently justified here: its 15 ms backstop was derived for 25 ppm*600 s (`uncertainty_evidence.py:63-67`), not this hour, and 3r here exceeds it. I have not assigned an unsupported new threshold or claimed this is a one-line change.

The planned 4629.6 s includes allowances, not an enforced upper limit on all allocation/scheduling delays. Any future live attempt must check the actual capture span against its chosen clock contract; an arm forecast cannot guarantee a longer actual capture's bound.

Verification and custody

Python 3.13.5; JW_B5_SYNTHETIC_ONLY=1 and PYTHONDONTWRITEBYTECODE=1 for all Python executions. No hardware, MLX workload, live ledger, real measurement streams, or blinding keys. Only source arm-report prose was read for the recorded rates. Full synthetic replay above passed; `python3.13 -B -m unittest tests.test_bytes_stream_harvest` passed 21 tests in 8.193 s. Executed arithmetic used the production gate and production native integrator/reader. No full suite: this is a report-only change. Existing branches and implementation files are untouched; the report branch is cut directly from a6c68c408.

Decisions I made

- Preserve the user-requested report-only scope rather than update repository bookkeeping or implementation.
- Recommend the strict existing gate for this exact code, explicitly accepting 3/3 refusals instead of calling an incompatible arm usable.
- Distinguish measured REALTIME-versus-RAW drift, native-duration clock error, and device-meter rate. Do not turn one into another without evidence.
- Use conservative planned timing and the executed synthetic receipts separately; label every injected dilation as conditional.
- Treat printed-precision comparison bars and scientific uncertainty envelopes as different tests. Numerical coverage in one fixture is not a general proof.
- Leave policy changes and any new RAW-native anchor identity to the lead's ruling; no implementation or hardware validation is claimed.
