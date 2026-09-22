# Exhibit C — executed evidence (generator output, verbatim)

Generated 2026-09-22 06:57:28 PDT at main `ecbc0fac` over `/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night` (read-only).

## C1 — registration digest and fields
```
sha256 f59804a9a28b2145f7bb8e91a8f0fe11b21ae6728cee70d8e943fe52a46da6f6 configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json
envelope_s = 600
envelopes = 12
settle_s = 600
window_max_s = 9000
interior_offset_s = 60
interior_s = 480
start_drift_max_s = 10
minimum_retained = 8
minimum_adjacent_pairs = 4
cadence_exclusion = "start_drift: absolute collector start drift greater than 10 s from the frozen schedule"
exclusions = ["census_not_clean_or_unknown", "ac_not_AC_Power_or_probe_error", "CPU_Speed_Limit_below_100_or_thermal_probe_error", "clock_anchor_unresolved", "incomplete_interior_support", "collect_error", "cleanup_unproven", "start_drift"]
chain_source_sha256 = "568a2771b28da9d805cd23ff4059bbbc27d6dfad1f8d9603331a412e3751b7ea"
ruling = "cold gate 10 Q1/Q2 (2026-09-19); adjudication 10a; sizing ruling 46b"
slot_pitch_s present: False
window arithmetic: settle + 12*600 = 7800 ; settle + 11*620 + 600 = 8020 ; window_max_s = 9000
```

## C2 — per-envelope serial tail from the archive stamps (monotonic seconds)
```
evidence_envelopes.jsonl sha256 9c5a9c12d23d42bfe3181e9ba57f2d156041cce14f9c9b20f8abfd858120df3e
env chain_drift sess_drift stop-sched postparse-stop end-postparse nextpre-end groups  anchor_status  excluded(summary)
summary.json sha256 9121f080c97e4b2f8f01261d0a2f9f407840dea9a6c8ca4468406617403d6f04
  1       0.160      0.318    600.150          4.983         0.011       2.869    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support']
  2       7.892      8.014    600.150          4.936         2.122        3.02    113  bounded       []
  3      10.112     10.228    600.082          4.881         0.074       2.777    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support', 'start_drift']
  4       7.698      7.814    600.150          4.847         0.106        2.79    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support']
  5       7.777      7.893    600.142          4.971          2.13       2.934    113  bounded       ['incomplete_interior_support']
  6      10.061     10.177    600.150          4.893         1.552       2.939    113  bounded       ['incomplete_interior_support', 'start_drift']
  7       9.419      9.534    600.150          4.913         0.011       2.673    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support']
  8       7.632      7.747    600.150          5.010         2.291       2.612    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support']
  9       9.946     10.063    600.150          5.072         1.338       2.676    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support', 'start_drift']
 10       9.120      9.236    600.150          4.896         0.011       2.789    113  unknown       ['clock_anchor_unresolved', 'incomplete_interior_support']
 11       7.730      7.846    600.150          4.904         1.697       2.853    113  bounded       ['incomplete_interior_support']
 12       9.488      9.603    600.150          5.018         1.702                113  bounded       []
session.json sha256 per envelope:
  01 11f999b0f8c4992e271967933625e02acf85854170e2b7a50c7709182f7a08c6
  02 bbeb51b8091304c22a0f021a49d0352d3dd808d66a4fee4310b0e91658bd6ba3
  03 15fd5e92d23fe2d263daae9e266baa1c28000d35ec11489ff0b12e8913f2f9e9
  04 30b8c392495b7ae51a37114414f997b45114c11d25da57ff4327b0b7004c5487
  05 e10d95183894371bb8970bb1423bddd3f5d3f56e95ccd53abeb2144fd2721663
  06 66239a264f86202a75280396ab68251a9bd57b27c1b348ae934ffce85305d3fc
  07 7f45379557cb8e34dc66b3229f0be57410fe0840d53716180124cca040f0397a
  08 cd56a38e581837ec82431950b05823a57cc0a8d2d85db15bad41eca612d92b99
  09 7fb73b249c3ea4bd74fe23d4aedc08bc1eed1bde76d429080cc90f28bea38cd0
  10 6c16f672ff53b4d32ecc7bdc266e4128fe175eef209e0f50023996bde28b1f96
  11 f9dea9108a5708cc9f8edb543fed64188fe0b095a9119f06f657bd10bd121e1f
  12 e42ae3fcdbe2b7c727a77e42f7bad69896bed940a4daf897da5ca9395471eb84
```

## C3 — summary.json exclusion facts
```
1 excluded= ['clock_anchor_unresolved', 'incomplete_interior_support'] start_drift_s= 0.16
2 excluded= [] start_drift_s= 7.892
3 excluded= ['clock_anchor_unresolved', 'incomplete_interior_support', 'start_drift'] start_drift_s= 10.112
4 excluded= ['clock_anchor_unresolved', 'incomplete_interior_support'] start_drift_s= 7.698
5 excluded= ['incomplete_interior_support'] start_drift_s= 7.777
6 excluded= ['incomplete_interior_support', 'start_drift'] start_drift_s= 10.061
7 excluded= ['clock_anchor_unresolved', 'incomplete_interior_support'] start_drift_s= 9.419
8 excluded= ['clock_anchor_unresolved', 'incomplete_interior_support'] start_drift_s= 7.632
9 excluded= ['clock_anchor_unresolved', 'incomplete_interior_support', 'start_drift'] start_drift_s= 9.946
10 excluded= ['clock_anchor_unresolved', 'incomplete_interior_support'] start_drift_s= 9.12
11 excluded= ['incomplete_interior_support'] start_drift_s= 7.73
12 excluded= [] start_drift_s= 9.488
start_drift-excluded: [3, 6, 9] ; excluded for start_drift ALONE: []
retained 2 retained_pairs 0 status INCONCLUSIVE
```

## C4 — attestation query cost (executed twice; `/usr/bin/log show --info --debug --style syslog --predicate 'process == "timed"' --start '2026-09-22 03:00:00' --end '2026-09-22 03:10:01'`)
```
run 1: rc=0 lines=46 wall=0.704s
run 2: rc=0 lines=46 wall=0.836s
```

## C5 — group-census cost (executed: `/usr/bin/pgrep -lf -g <pgid> .` for one dead pgid, 20 runs; and one batched `pgrep -g <list>` over 113 dead pgids)
```
single pgrep: median 10.9 ms, max 12.5 ms; x113 at median = 1.23 s
batched pgrep over 113 pgids: 13.8 ms
groups journaled per envelope (evidence_envelopes.jsonl cleanup.groups): [113, 113, 113, 113, 113, 113, 113, 113, 113, 113, 113, 113]
```

## C6 — plist parse + derive cost at the bench (envelope 02 raw plist via the tracked collector's parse_frames; executed once)
```
plist /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence/envelope-02/raw/powermetrics-idle-2.plist bytes 132917113 sha256 d88f88215e53d570b36d9ced75bbfed2f8dc2d128ff48184bbc77b54f1c9cb77
parse_frames: 5.32s, frames=2
```

