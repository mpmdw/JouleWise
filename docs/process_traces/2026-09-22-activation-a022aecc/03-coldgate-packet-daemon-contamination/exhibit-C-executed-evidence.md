# Exhibit C — executed evidence (generator output, verbatim)

Generated 2026-09-22 23:55:38 PDT at main `91f80870` by `exhibit-C-generator.py`.

Archive roots, both read-only:

- TONIGHT = `/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night`
- PRIOR   = `/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night`  (archive copy present; preferred)

```
sha256(this generator) = f0db29e9ee2f56d8db8cc87ed9d8fb51db5a8dd8ae457e8372e30cae629a26e8
```

## C1 — registration digest check and the fields that govern this night

```
command: git show 91f80870:configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json | shasum -a 256
sha256(registration at 91f80870)              = 2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1
night_gate.QPE01_PILOT_REGISTRATION_SHA256 = 2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1
MATCH = True

busy_cores_role = "covariate_only"
exclusions = [
  "census_not_clean_or_unknown",
  "ac_not_AC_Power_or_probe_error",
  "CPU_Speed_Limit_below_100_or_thermal_probe_error",
  "clock_anchor_unresolved",
  "incomplete_interior_support",
  "collect_error",
  "cleanup_unproven",
  "start_drift",
  "network_time_slew_attested",
  "network_time_unattested"
]
load_generator = false
stop_branches = {
  "block_two_upper_bound_above_1_J": "no cutoff qualifies",
  "observer_floor_above_smallest_holdable_share": "no cutoff qualifies",
  "sized_pairs_above_24": "no cutoff qualifies"
}
sizing = {
  "assumption": "independent normally distributed disjoint pair differences",
  "chi_square_lower_tail_probability": 0.1,
  "confidence": 0.9,
  "delta_j": 1,
  "formula": "max(3, ceil(8 * s_upper**2 / delta_j**2))",
  "maximum_pairs": 24,
  "minimum_pairs": 3,
  "multiplier": 8,
  "reference_factors": {
    "n_4": 2.266,
    "n_6": 1.762
  },
  "s_pair": "sample SD of retained disjoint differences, df = n - 1",
  "s_upper": "s_pair * sqrt((n - 1) / chi_square_quantile(0.10, n - 1))"
}
block_two = {
  "authored_after_pilot": true,
  "contrast": "idle-load-idle bracket",
  "levels": [
    0,
    0.05
  ],
  "one_profile": true,
  "one_qos": true,
  "smallest_holdable_share": 0.05,
  "upper_bound": "one-sided 95% paired-contrast upper bound"
}
cadence_exclusion = "start_drift: absolute collector start drift greater than 10 s from the frozen schedule"
envelope_s = 600
envelopes = 12
interior_s = 480
minimum_retained = 8
minimum_adjacent_pairs = 4
pairing_rule = "disjoint_original_adjacent_pairs_both_retained_no_bridging"
```

## C2 — TONIGHT per-envelope table and headline summary fields

Sources: `/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/summary.json`, `/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-NN/session.json`, `/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence_envelopes.jsonl`.

```
idx     joules excluded               net_time_attest chain_drift_s sess_drift_s anchor    interior   native  bc_med  bc_max obs_cpu_s
  1    649.690 -                      authenticated         0.1912       0.3554 bounded   complete     2156  2.7280  3.0976    31.928
  2    306.799 -                      authenticated         0.1501       0.3154 bounded   complete     2151  1.2112  1.3552    31.311
  3    302.604 -                      authenticated         0.1501       0.3142 bounded   complete     2163  1.2160  1.2912    31.613
  4    304.637 -                      authenticated         0.1501       0.3123 bounded   complete     2178  1.2152  1.3344    31.659
  5    308.478 -                      authenticated         0.1501       0.3156 bounded   complete     2170  1.2192  1.4048    31.547
  6    304.993 -                      authenticated         0.1501       0.2805 bounded   complete     2179  1.2144  1.3296    31.634
  7    302.217 -                      authenticated         0.1501       0.3156 bounded   complete     2140  1.2064  1.2848    31.649
  8    309.634 -                      authenticated         0.1501       0.3111 bounded   complete     2189  1.2496  1.3328    31.551
  9    312.640 -                      authenticated         0.1501       0.3141 bounded   complete     2174  1.2272  1.5040    31.635
 10    303.291 -                      authenticated         0.1501       0.3130 bounded   complete     2201  1.2224  1.3520    31.618
 11    305.775 -                      authenticated         0.1501       0.3106 bounded   complete     2158  1.2112  1.3088    31.597
 12    347.863 -                      authenticated         0.1501       0.3151 bounded   complete     2156  1.2176  1.5744    31.610

session.json sha256 per envelope:
  01 c680b1366913544f3b90b6ff26668ce9543161a7ad29f596feabf6f4c5c01ebe
  02 0600c621900c6ed906b7869c1ceb8b59109497c608310ce04869673ff1830460
  03 4e644dd93645cd6bf1553698ccec94cb8e4ef2feaa8d34fd6dc2f25bb3dccac7
  04 1fccef43b9499660af0f6f3004c6e18d0d4e214041a121701133c4313f5dd6c8
  05 de062966fdd4578904582939cf41479982c4ecc26c49cd18ac6a1618cc15929a
  06 b8ad49cd24ffa61ae6f83a3f84a42d921069d88bf35569812c5c1eeef6654a1b
  07 27fe178256ae398fa39f62ba90b41f85f3e321391080df640c36fc111a07e2f9
  08 7ba61bde367eb8e1aafefe41581f8fb695cdaf18e379dc54e6a7dbfbaf99ad75
  09 5af8cfa6b894c0294c1e4ab107e69d9d00c08d1e38ce99626bf2a62efcc3d02d
  10 fbf1e04cc21e6e26c9624766b631354c33df823a2b5eafad75fff95679753d55
  11 0e48a9bc5aefb2040b46ee2fc5bf9f83f3ee370c6e395d0b91de4aec9576ec8b
  12 99fb3a70dfd2a354d57c5783b8ff754b20386c072f4d38c3ea0d5d554c1e0af4

summary headline fields:
  status = "SPREAD_RECORDED"
  evidence_status = "PROVISIONAL"
  retained = 12
  retained_pairs = 6
  pair_sd_j = 144.2791108429115
  pair_df = 5
  s_upper = 254.23420803393725
  s_upper_factor = 1.7620999086329474
  s_upper_reason = "one-sided upper 90% chi-square bound; independent normal pair differences assumed"
  block_two_pairs = 517081
  block_two_pairs_reason = "ruling 46b: max(3, ceil(8 * s_upper**2 / delta_j**2)); delta_j=1; stop above 24 pairs"
  block_two_stop = {"causes": ["sized_pairs_above_24", "observer_floor_above_smallest_holdable_share"], "outcome": "no cutoff qualifies", "pairs": 517081}
  cutoff_authority = false
  busy_cores = {"max": 3.0976, "min": 1.1647999999999996, "p10": 1.1987199999999993, "p50": 1.2207999999999988, "p90": 1.3321599999999993}
  clean_machine_busy_cores = {"max": 3.0976, "min": 1.1647999999999996, "p10": 1.1987199999999993, "p50": 1.2207999999999988, "p90": 1.3321599999999993}
  observer_floor_cores = 0.05282276792404742
  observer_support_s = 7181.620632706385
  single_envelope_sd_j = 98.86580418386548
  unfiltered_single_envelope_sd_j = 98.86580418386548
  first_to_last_retained_drift_j = -301.8268101329849
  max_abs_delta_j = 342.8903855583943
  adjacent_pair_sd_j = 105.48810110894335
  top_up = false
  busy_cores_role = "covariate_only; never excluded"
  busy_cores_source = "evidence_busy_cores.jsonl"

sizing_pairs (the six disjoint registered pairs; all deltas):
  pair (1,2)  delta_j = -342.890386  retained=True
  pair (3,4)  delta_j = +2.032680  retained=True
  pair (5,6)  delta_j = -3.484811  retained=True
  pair (7,8)  delta_j = +7.417157  retained=True
  pair (9,10)  delta_j = -9.348957  retained=True
  pair (11,12)  delta_j = +42.087744  retained=True
sizing_pairs delta_j list = [-342.890386, 2.03268, -3.484811, 7.417157, -9.348957, 42.087744]

adjacent_pairs (overlapping; diagnostic only per the summary):
  pair (1,2)  delta_j = -342.890386  retained=True
  pair (2,3)  delta_j = -4.195247  retained=True
  pair (3,4)  delta_j = +2.032680  retained=True
  pair (4,5)  delta_j = +3.841467  retained=True
  pair (5,6)  delta_j = -3.484811  retained=True
  pair (6,7)  delta_j = -2.776523  retained=True
  pair (7,8)  delta_j = +7.417157  retained=True
  pair (8,9)  delta_j = +3.006196  retained=True
  pair (9,10)  delta_j = -9.348957  retained=True
  pair (10,11)  delta_j = +2.483870  retained=True
  pair (11,12)  delta_j = +42.087744  retained=True
```

## C3 — TONIGHT load journal `evidence_busy_cores.jsonl`

```
file: /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence_busy_cores.jsonl
sha256 = 4ad71d0be4f6af605871b8531db44e305a3ed3e157c91e9c6bfa4e21a392f86c
row count = 245
rows without observation.metrics = 2
  monotonic_start=362600.556583708 error="CPU counter regressed for the same process identity"
  monotonic_start=365578.575872958 error="Command '('/usr/bin/top', '-l', '2', '-s', '30', '-n', '0')' died with <Signals.SIGTERM: 15>."

top_consumers aggregation over 243 rows with metrics, by command basename, sorted by total busy-core-seconds share (sum of per-sample busy_cores); top 10:
command                       rows      total      mean       max  observer_flag
fseventsd                      243   242.4495    0.9977    1.0003  [False]
powermetrics                   234    22.0635    0.0943    0.1176  [False]
mediaanalysisd                  20    17.4756    0.8738    1.7894  [False]
Python                         311     2.5615    0.0082    0.2703  [False]
launchd                        242     2.3480    0.0097    0.0178  [False]
WindowServer                   185     1.5761    0.0085    0.0662  [False]
corespotlightd                  14     0.8073    0.0577    0.1038  [False]
ControlCenter                   38     0.7390    0.0194    0.0389  [False]
top                            204     0.7385    0.0036    0.0036  [False]
contactsd                      185     0.5752    0.0031    0.0115  [False]

(full basename list, 73 distinct: AddressBookSourceSync, BiomeAgent, ControlCenter, IMDPersistenceAgent, IMTranscoderAgent, IMTransferAgent, ImageIOXPCService, IntelligencePlatformComputeService, ManagedClient, MessagesAirlockService, NotificationCenter, PerfPowerServices, PhotosReliveWidget, Python, Raycast, ServiceExtension, UsageTrackingAgent, WeatherWidget, WindowServer, XprotectService, ZoomUpdater, airportd, apsd, audioaccessoryd, audioclocksyncd, biomesyncd, cfprefsd, cloudd, com.apple.DriverKit-AppleBCMWLAN, com.apple.Safari.SafeBrowsing.Service, configd, contactsd, coreaudiod, corebrightnessd, corecaptured, corespotlightd, dasd, deleted_helper, duetexpertd, filevaultd, findmybeaconingd, frauddefensed, fseventsd, homed, homeenergyd, identityservicesd, imagent, launchd, linkd, locationd, logd, mDNSResponder, mdmclient, mds, mds_stores, mdworker_shared, mediaanalysisd, mobileassetd, networkserviceproxy, notifyd, nsurlsessiond, opendirectoryd, parsec-fbf, peopled, powermetrics, runningboardd, spotlightknowledged, spotlightknowledged.updater, sysmond, syspolicyd, top, trustd, usernotificationsd)

per-envelope join: a journal row belongs to envelope i when its monotonic_start lies in
[scheduled_mono_s, scheduled_mono_s + 600) of summary envelopes[i].
idx  rows  fseventsd>=0.9  mediaanalysisd rows  median total busy_cores
  1    20              20                   11                   2.4760
  2    20              20                    0                   1.2136
  3    20              20                    0                   1.2184
  4    19              19                    2                   1.2176
  5    20              20                    2                   1.2216
  6    19              19                    0                   1.2144
  7    20              20                    0                   1.2088
  8    19              19                    0                   1.2512
  9    19              19                    0                   1.2288
 10    20              20                    4                   1.2248
 11    19              19                    0                   1.2112
 12    19              19                    0                   1.2176
rows not inside any scheduled envelope window = 9

first 25 rows (offset_s from the first journal row's monotonic_start):
 offset_s  busy_cores  top 3 consumers (basename=busy_cores)
      0.0      1.1904  fseventsd=0.9995  powermetrics=0.1140  launchd=0.0082
     30.4      1.2128  fseventsd=0.9966  powermetrics=0.0909  launchd=0.0092
     60.8      1.2528  fseventsd=0.9983  powermetrics=0.0929  WindowServer=0.0234
     91.2      1.3232  fseventsd=0.9990  powermetrics=0.0932  corespotlightd=0.0689
    121.6      1.3344  fseventsd=0.9948  powermetrics=0.0936  corespotlightd=0.0349
    152.0      1.2512  fseventsd=0.9983  powermetrics=0.0923  WindowServer=0.0191
    182.4      1.2112  fseventsd=0.9997  powermetrics=0.0909  launchd=0.0092
    212.8      1.1984  fseventsd=0.9977  powermetrics=0.0906  launchd=0.0089
    243.2      2.8992  mediaanalysisd=1.4433  fseventsd=0.9972  powermetrics=0.1084
    273.6      3.0592  mediaanalysisd=1.7521  fseventsd=0.9996  powermetrics=0.1065
    304.0      3.0784  mediaanalysisd=1.7336  fseventsd=0.9946  powermetrics=0.1117
    334.4      3.0608  mediaanalysisd=1.7591  fseventsd=0.9992  powermetrics=0.1107
    364.8      3.0624  mediaanalysisd=1.7571  fseventsd=0.9994  powermetrics=0.1097
    395.2      2.9840  mediaanalysisd=1.6726  fseventsd=0.9997  powermetrics=0.1104
    425.6      2.7840  mediaanalysisd=1.4518  fseventsd=0.9960  powermetrics=0.1117
    456.0      2.7280  mediaanalysisd=1.3177  fseventsd=0.9978  powermetrics=0.1064
    486.4      3.0976  mediaanalysisd=1.7824  fseventsd=0.9996  powermetrics=0.1104
    516.8      3.0688  mediaanalysisd=1.7894  fseventsd=0.9976  powermetrics=0.1100
    547.2      2.2240  fseventsd=0.9989  mediaanalysisd=0.9416  powermetrics=0.1025
    577.6      1.3840  fseventsd=0.9996  Python=0.2703  launchd=0.0083
    607.9      1.2256  fseventsd=0.9922  powermetrics=0.0814  launchd=0.0128
    638.3      1.2048  fseventsd=0.9999  powermetrics=0.0899  launchd=0.0089
    668.7      1.2048  fseventsd=0.9997  powermetrics=0.0929  launchd=0.0089
    699.1      1.2096  fseventsd=0.9971  powermetrics=0.0929  launchd=0.0109
    729.5      1.2976  fseventsd=0.9940  powermetrics=0.0952  WindowServer=0.0372
```

## C4 — PRIOR night (qpe01-pilot-n1-20260922-0217), same aggregation

```
file: /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence_busy_cores.jsonl
sha256 = 39224eb543f582d62ee2d8fdb1d93e6d83ebab7188d3740a55057a1fd84313db
summary.json sha256 = 9121f080c97e4b2f8f01261d0a2f9f407840dea9a6c8ca4468406617403d6f04
row count = 238; rows with metrics = 236
command                       rows      total      mean       max
powermetrics                   229    25.6055    0.1118    0.1338
launchd                        236     2.1830    0.0093    0.0188
Python                         340     2.1706    0.0064    0.2762
WindowServer                   204     1.8359    0.0090    0.0435
ControlCenter                   43     0.8801    0.0205    0.0297
contactsd                      225     0.7356    0.0033    0.0040

PRIOR summary busy_cores quantiles = {"max": 0.7392000000000003, "min": 0.19200000000000017, "p10": 0.22240000000000038, "p50": 0.24160000000000004, "p90": 0.32431999999999983}
PRIOR status = "INCONCLUSIVE" ; evidence_status = "PROVISIONAL" ; retained = 2 ; retained_pairs = 0
PRIOR retained envelopes (excluded == []):
  envelope 02  joules = 154.881681
  envelope 12  joules = 151.025353
PRIOR all envelopes (index, joules, excluded, busy_cores median):
  01       None clock_anchor_unresolved,incomplete_interior_support            0.23680000000000057
  02    154.882 -                                                              0.24319999999999986
  03       None clock_anchor_unresolved,incomplete_interior_support,start_drift 0.2400000000000002
  04       None clock_anchor_unresolved,incomplete_interior_support            0.23083811664849757
  05    152.148 incomplete_interior_support                                    0.2591999999999999
  06    151.864 incomplete_interior_support,start_drift                        0.24960000000000093
  07       None clock_anchor_unresolved,incomplete_interior_support            0.23359999999999914
  08       None clock_anchor_unresolved,incomplete_interior_support            0.24239999999999995
  09       None clock_anchor_unresolved,incomplete_interior_support,start_drift 0.2528000000000006
  10       None clock_anchor_unresolved,incomplete_interior_support            0.24799999999999933
  11    152.807 incomplete_interior_support                                    0.2480000000000011
  12    151.025 -                                                              0.23999999999999932
```

## C5 — TONIGHT t0 receipt and result

```
receipt.json sha256 = 64ed9c4d79066502b7d77af6123f595c5c69271de1dfb720dad76d478ca85f22
result.json  sha256 = ea1b5565911762c06dfa9bcbb5bd1bfdd7a46521b619a174c8e8790c8dc78d26
conditions[2].condition_id = C3  status = PASS
  load_1m = 1.03
  load_average_raw = "{ 1.03 1.14 1.20 }\n"
  agent_census_exit_code = 1
  agent_census_stdout = ""
  cpu_speed_limit = null
  ac_power_raw = "Now drawing from 'AC Power'\n -InternalBattery-0 (id=23003235)\t80%; AC attached; not charging present: true\n"
  hid_idle_raw = "0\n"
  thermal_raw = "Note: No thermal warning level has been recorded\nNote: No performance warning level has been recorded\nNote: No CPU power status has been recorded\n"
  detail = "agent, HID, AC, display, load, and thermal predicates passed"

walk of the whole receipt for keys named top_consumers_at_decision or quiet_admission:
  hits = NONE — neither key appears anywhere in the receipt
  receipt top-level keys = ['authored_monotonic_ns', 'conditions', 'plan_id', 'receipt_class', 'refusal', 'schema', 'verdict']
  receipt_class = "DIAGNOSTIC_NO_PACK" ; verdict = "GO" ; refusal = null
  condition statuses = {'C1': 'PASS', 'C2': 'NOT_APPLICABLE', 'C3': 'PASS', 'C4': 'PASS', 'C5': 'PASS'}

result.json: census_count = 267 ; census_hits = [] ; verdict = "GO" ; chain_exit_code = 0 ; aborted_reason = null
```

## C6 — machine-state probes executed now (unified log, `ps`, `mount`)

```
command: /usr/bin/log show --last 30h --predicate 'process == "fseventsd" AND eventMessage CONTAINS "scan_old"' --style compact
rc = 0; wall = 1.7 s; total stdout lines = 807
timestamped lines = 806
first: 2026-09-22 04:49:03.306 E  fseventsd[341:279f72a] [com.apple.fsevents:daemon] scan_old: bailing out because device mounted @ [<private>]<private> has dls 0x0 and dls->fci 0x0
last:  2026-09-22 23:54:47.828 E  fseventsd[341:2eef0bf] [com.apple.fsevents:daemon] scan_old: bailing out because device mounted @ [<private>]<private> has dls 0x0 and dls->fci 0x0

hourly histogram (cut -c1-13 | sort | uniq -c):
        9 2026-09-22 04
       45 2026-09-22 05
       46 2026-09-22 06
       47 2026-09-22 07
       44 2026-09-22 08
       45 2026-09-22 09
       45 2026-09-22 10
       45 2026-09-22 11
       44 2026-09-22 12
       43 2026-09-22 13
       43 2026-09-22 14
       41 2026-09-22 15
       39 2026-09-22 16
       39 2026-09-22 17
       39 2026-09-22 18
       40 2026-09-22 19
       38 2026-09-22 20
       39 2026-09-22 21
       39 2026-09-22 22
       36 2026-09-22 23

command: ps -axo pid,pcpu,time,etime,rss,command | grep '[f]seventsd'   (wall clock 2026-09-22 23:55:39 PDT)
  341 100.0 1285:07.69 04-06:14:22  29136 /System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/FSEvents.framework/Versions/A/Support/fseventsd

command: mount | grep -v devfs
/dev/disk3s1s1 on / (apfs, sealed, local, read-only, journaled)
/dev/disk3s6 on /System/Volumes/VM (apfs, local, noexec, journaled, noatime, nobrowse)
/dev/disk3s2 on /System/Volumes/Preboot (apfs, local, journaled, nobrowse)
/dev/disk3s4 on /System/Volumes/Update (apfs, local, journaled, nobrowse)
/dev/disk1s2 on /System/Volumes/xarts (apfs, local, noexec, journaled, noatime, nobrowse)
/dev/disk1s1 on /System/Volumes/iSCPreboot (apfs, local, journaled, nobrowse)
/dev/disk1s3 on /System/Volumes/Hardware (apfs, local, journaled, nobrowse)
/dev/disk3s5 on /System/Volumes/Data (apfs, local, journaled, nobrowse, protect, root data)
map auto_home on /System/Volumes/Data/home (autofs, automounted, nobrowse)
```

## C7 — counterfactual sizing (DIAGNOSTIC ONLY — not a re-verdict, not registered)

The registration fixes the six disjoint pairs and the sizing rule; dropping a pair after seeing the data is NOT admissible sizing. The (ii) row exists only to show how much of the sizing outcome rides on pair (1,2).

```
formula (registration `sizing`, ruling 46b):
  s_pair   = sample SD of the pair deltas (n-1 denominator)
  s_upper  = s_pair * sqrt((n-1) / chi2_0.10(n-1))     [one-sided upper 90% chi-square bound]
  pairs    = max(3, ceil(8 * s_upper**2 / 1**2)); stop above 24 pairs
  chi2_0.10 computed by the stdlib lower-gamma inversion of joulewise.quiet_predicate_campaign.chi_square_lower_decile (scipy not importable here: ModuleNotFoundError)

  chi2_0.10(df=3) = 0.584374374   factor sqrt(df/chi2) = 2.265765949
  chi2_0.10(df=4) = 1.063623217   factor sqrt(df/chi2) = 1.939260231
  chi2_0.10(df=5) = 1.610307987   factor sqrt(df/chi2) = 1.762099909
  cross-check: summary.s_upper_factor = 1.762099909 (df = 5) -> agreement True

registered pair deltas (J): [-342.890386, 2.03268, -3.484811, 7.417157, -9.348957, 42.087744]

(i) all six pairs as registered [AUTHORITATIVE — this is what the summary reports]:
    n = 6; df = 5; mean delta = -50.697762 J
    s_pair  = 144.279111 J
    chi2_0.10(5) = 1.610307987; factor = 1.762099909
    s_upper = 254.234208 J
    pairs   = max(3, ceil(8 * 254.234208**2 / 1**2)) = 517081
    stop (pairs > 24)? True
    summary agreement: pair_sd_j = 144.279111 -> True; s_upper = 254.234208 -> True; block_two_pairs = 517081 -> True

(ii) pairs 2-6 only, dropping pair (1,2) [COUNTERFACTUAL, NOT ADMISSIBLE SIZING]:
    n = 5; df = 4; mean delta = +7.740763 J
    s_pair  = 20.189565 J
    chi2_0.10(4) = 1.063623217; factor = 1.939260231
    s_upper = 39.152820 J
    pairs   = max(3, ceil(8 * 39.152820**2 / 1**2)) = 12264
    stop (pairs > 24)? True

(iii) PRIOR night: retained_pairs = 0 -> 0 pairs; no pair SD, no s_upper and no block-two sizing were computable from it.
      PRIOR summary pair_sd_j = null ; s_upper = null ; block_two_pairs = null
```

## C8 — energy comparison, TONIGHT vs PRIOR

```
TONIGHT joules per envelope (over the registered 480 s interior):
  01     649.6897
  02     306.7994
  03     302.6041
  04     304.6368
  05     308.4783
  06     304.9934
  07     302.2169
  08     309.6341
  09     312.6403
  10     303.2913
  11     305.7752
  12     347.8629
PRIOR retained joules: [154.8817, 151.0254] (envelopes [2, 12], read from /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence/summary.json)
TONIGHT median joules = 306.2873 over 12 envelopes
PRIOR   median joules = 152.9535 over 2 retained envelopes
ratio of medians TONIGHT/PRIOR = 2.0025
delta J (median) = +153.3338 J
implied extra mean power over the 480 s interior = (306.2873 - 152.9535) / 480 = +0.3194 W
TONIGHT minimum envelope = 302.2169 J -> extra mean power vs PRIOR median = +0.3110 W
TONIGHT envelope 01 (the outlier pair's left member) = 649.6897 J -> extra mean power vs PRIOR median = +1.0349 W
```

## C9 — file digests read by this generator (self-anchoring)

```
9121f080c97e4b2f8f01261d0a2f9f407840dea9a6c8ca4468406617403d6f04  /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence/summary.json
39224eb543f582d62ee2d8fdb1d93e6d83ebab7188d3740a55057a1fd84313db  /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence_busy_cores.jsonl
c680b1366913544f3b90b6ff26668ce9543161a7ad29f596feabf6f4c5c01ebe  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-01/session.json
0600c621900c6ed906b7869c1ceb8b59109497c608310ce04869673ff1830460  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-02/session.json
4e644dd93645cd6bf1553698ccec94cb8e4ef2feaa8d34fd6dc2f25bb3dccac7  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-03/session.json
1fccef43b9499660af0f6f3004c6e18d0d4e214041a121701133c4313f5dd6c8  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-04/session.json
de062966fdd4578904582939cf41479982c4ecc26c49cd18ac6a1618cc15929a  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-05/session.json
b8ad49cd24ffa61ae6f83a3f84a42d921069d88bf35569812c5c1eeef6654a1b  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-06/session.json
27fe178256ae398fa39f62ba90b41f85f3e321391080df640c36fc111a07e2f9  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-07/session.json
7ba61bde367eb8e1aafefe41581f8fb695cdaf18e379dc54e6a7dbfbaf99ad75  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-08/session.json
5af8cfa6b894c0294c1e4ab107e69d9d00c08d1e38ce99626bf2a62efcc3d02d  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-09/session.json
fbf1e04cc21e6e26c9624766b631354c33df823a2b5eafad75fff95679753d55  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-10/session.json
0e48a9bc5aefb2040b46ee2fc5bf9f83f3ee370c6e395d0b91de4aec9576ec8b  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-11/session.json
99fb3a70dfd2a354d57c5783b8ff754b20386c072f4d38c3ea0d5d554c1e0af4  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-12/session.json
84bfcafb84cb08ddb6b4c1e2fe707ac2b74a1e5b055ecba204a3740c58fe2bc2  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/summary.json
4ad71d0be4f6af605871b8531db44e305a3ed3e157c91e9c6bfa4e21a392f86c  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence_busy_cores.jsonl
bf5a2d7ecec2d87ad9754024cc8f1f1fc4c9a0cd9f9ef839fa87c06e05344af5  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence_envelopes.jsonl
64ed9c4d79066502b7d77af6123f595c5c69271de1dfb720dad76d478ca85f22  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/receipt.json
ea1b5565911762c06dfa9bcbb5bd1bfdd7a46521b619a174c8e8790c8dc78d26  /Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/result.json

sha256(this generator) = f0db29e9ee2f56d8db8cc87ed9d8fb51db5a8dd8ae457e8372e30cae629a26e8
```
