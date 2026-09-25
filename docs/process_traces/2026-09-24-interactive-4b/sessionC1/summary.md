# OSCTX diagnostic summary

Diagnostic only; not claim-bearing.

## C1

| Block | Arm | E J/token | R token/s | Flags |
|---|---|---:|---:|---|
| C1-01 | SH | 0.389921 | 83.801 |  |
| C1-01 | I | 0.388484 | 84.314 |  |
| C1-02 | SH | 0.388635 | 83.864 |  |
| C1-02 | I | 0.389548 | 84.308 | census_cpu |
| C1-03 | SH | 0.390560 | 83.819 | census_cpu |
| C1-03 | I | 0.391442 | 84.068 | census_cpu |
| C1-04 | I | 0.389026 | 84.321 | census_cpu |
| C1-04 | SH | 0.388390 | 83.836 | census_cpu |
| C1-05 | I | 0.388342 | 84.144 | census_cpu |
| C1-05 | SH | 0.388765 | 83.782 |  |
| C1-06 | I | 0.388672 | 84.347 |  |
| C1-06 | SH | 0.389018 | 83.726 | census_cpu |

| Block | Arm | Bundle status | Idle-request precheck reasons | Gross J | Idle W mean / SD | Idle cadence s | Energy bound terms J |
|---|---|---|---|---:|---|---:|---|
| C1-01 | SH | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 200.68249742888116 | 0.16315584810914352 / 0.35143500969290353 | 0.1212425415 | {"E_clock_anchor_shift_bound_j": 0.08003566331893808, "E_drift_bound_j": 23.894805468324396, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-01 | I | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 199.52479612480593 | 0.09730940599480874 / 0.2132761323990717 | 0.131997104 | {"E_clock_anchor_shift_bound_j": 0.05428264551585471, "E_drift_bound_j": 10.644171644686393, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-02 | SH | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 199.90332321689178 | 0.14459015252820187 / 0.24060562714095404 | 0.12111693700000001 | {"E_clock_anchor_shift_bound_j": 0.027502569609396232, "E_drift_bound_j": 11.096143706739527, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-02 | I | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 200.1335130167606 | 0.10767987800937165 / 0.25506615031921226 | 0.1318150205 | {"E_clock_anchor_shift_bound_j": 0.007132453510905634, "E_drift_bound_j": 11.960698455620761, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-03 | SH | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 200.82231541610003 | 0.13374216363940344 / 0.2475075349686399 | 0.121109229 | {"E_clock_anchor_shift_bound_j": 0.052240948003316134, "E_drift_bound_j": 12.50914991694932, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-03 | I | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 201.05388884441805 | 0.09938015977867297 / 0.2594351231302731 | 0.131934812 | {"E_clock_anchor_shift_bound_j": 0.0007568640699560092, "E_drift_bound_j": 11.368322549084672, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-04 | I | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 199.86226213682914 | 0.10703967745727222 / 0.2646633456870049 | 0.131879791 | {"E_clock_anchor_shift_bound_j": 0.0041711827395261025, "E_drift_bound_j": 10.825083070963732, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-04 | SH | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 200.17732471481085 | 0.20709294689251173 / 0.3438598036155077 | 0.1213411875 | {"E_clock_anchor_shift_bound_j": 0.015975233618462426, "E_drift_bound_j": 15.25088507935431, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-05 | I | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 199.7940833805375 | 0.1504575310406475 / 0.3254841151290154 | 0.1317406865 | {"E_clock_anchor_shift_bound_j": 0.04775575471822435, "E_drift_bound_j": 11.20838965968848, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-05 | SH | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 200.06159741317964 | 0.1584810009995424 / 0.28968029551072966 | 0.1228794995 | {"E_clock_anchor_shift_bound_j": 0.05204268970695125, "E_drift_bound_j": 12.513455518803482, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-06 | I | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 199.6134360131707 | 0.09624269196997569 / 0.2614097422108937 | 0.13167302 | {"E_clock_anchor_shift_bound_j": 0.02578569731792868, "E_drift_bound_j": 11.975215904273847, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |
| C1-06 | SH | succeeded | environment_admission_failed, environment_admission_missing, instrument_calibration_missing | 200.1747999648316 | 0.1558970132378245 / 0.32263067088502734 | 0.1220451665 | {"E_clock_anchor_shift_bound_j": 0.05534868059331188, "E_drift_bound_j": 17.474978260739167, "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0} |

| Arm | Invalid cells | Mean idle W | Mean edge J/token | Max drift ratio |
|---|---:|---:|---:|---:|
| I | 0 | 0.10968489070845813 | 0.000537214181295693 | 0.060176889167341964 |
| SH | 0 | 0.16049318756777126 | 0.0011529305921938904 | 0.11968981411952402 |

| Contrast | Verdict | Ratio 99.375% interval | Widened E interval | Absolute J/token contrast 99.375% interval | Approx. 80% MDE ratio |
|---|---|---|---|---|---:|
| SH/I:E | EQUIVALENT | 0.99991 [0.99548, 1.00435] | [0.86145, 1.16062] | -3.7244061867678736e-05 [-0.0017641431279740159, 0.0016896550042386582] | 1.03551 |
| SH/I:R | EQUIVALENT | 0.99471 [0.99192, 0.99751] | n/a |   | 1.03349 |

Contemporary SH/I equivalence on E and R: True.

SH/I:E: widened interval crosses δ: yes; v2.3 C3 outcome: INCONCLUSIVE-by-attribution.
Original I median idle cadence ≤ 130 ms: not met (131.84740575 ms).
Purpose-based cure test (all I runs valid; median ≤ 150 ms): met.
Production margin: 300 × median cadence = 39.554221725000005 s against 55 s.

| Cell | Arm | E drift bound / net energy |
|---|---|---:|
| C1-01 | SH | 0.11968981411952402 |
| C1-01 | I | 0.0535141322643005 |
| C1-02 | SH | 0.05576481261538283 |
| C1-02 | I | 0.059968909970797665 |
| C1-03 | SH | 0.0625561365528655 |
| C1-03 | I | 0.05672304770153055 |
| C1-04 | I | 0.0543478657689378 |
| C1-04 | SH | 0.07669314070227125 |
| C1-05 | I | 0.05637146968288369 |
| C1-05 | SH | 0.06286658476512565 |
| C1-06 | I | 0.060176889167341964 |
| C1-06 | SH | 0.08773575578203453 |

## P

| Block | Arm | E J/token | R token/s | Flags |
|---|---|---:|---:|---|
| P-01 | D | n/a | n/a |  |
| P-02 | B | n/a | n/a |  |
| P-03 | D | n/a | n/a |  |
| P-04 | B | n/a | n/a |  |

| Block | Arm | Bundle status | Idle-request precheck reasons | Gross J | Idle W mean / SD | Idle cadence s | Energy bound terms J |
|---|---|---|---|---:|---|---:|---|
| P-01 | D | probe-only |  | None | None / None | None | null |
| P-02 | B | probe-only |  | None | None / None | None | null |
| P-03 | D | probe-only |  | None | None / None | None | null |
| P-04 | B | probe-only |  | None | None / None | None | null |

| Arm | Invalid cells | Mean idle W | Mean edge J/token | Max drift ratio |
|---|---:|---:|---:|---:|
| B | 0 | None | None | None |
| D | 0 | None | None | None |

## CPU probe (descriptive, outside inference)

| Context | Median CPU-probe seconds | Ratio to I |
|---|---:|---:|
| I | 7.694059812522028 | 1.0 |
| SH | 7.6139142290339805 | 0.989583446783503 |
| D | 7.556131312507205 | 0.9820733782455986 |
| B | 57.273547416960355 | 7.443865633036549 |

## Flags

- /Users/edr/osctx-mvp-01/sessionC1/C1/C1-02.2.I.a1: census_cpu
- /Users/edr/osctx-mvp-01/sessionC1/C1/C1-03.1.SH.a1: census_cpu
- /Users/edr/osctx-mvp-01/sessionC1/C1/C1-03.2.I.a1: census_cpu
- /Users/edr/osctx-mvp-01/sessionC1/C1/C1-04.1.I.a1: census_cpu
- /Users/edr/osctx-mvp-01/sessionC1/C1/C1-04.2.SH.a1: census_cpu
- /Users/edr/osctx-mvp-01/sessionC1/C1/C1-05.1.I.a1: census_cpu
- /Users/edr/osctx-mvp-01/sessionC1/C1/C1-06.2.SH.a1: census_cpu

## Discarded attempts

- /Users/edr/osctx-mvp-01/sessionC1/C1/C1-warmup.1.I.a1: preregistered discard
