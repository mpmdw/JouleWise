# Exhibit C — executed evidence (verbatim command output captured 2026-09-22 by activation d9990b3c; the magistrate wrote only the headings and the commands)

## C1 — per-envelope fields read from the harvest archive session records

Command: `python3 exhibit-C-generator.py` (the generator file is in this directory; sha256 7dd2c3cc941e7d83cc282bed635ed244a5cebc7e0deb2db574eeb87816184efa). It reads only `night/evidence/envelope-NN/session.json` and `night/evidence/summary.json` under the archive; the archive was verified byte-exact against the live custody root by the harvesting activation (`SHA256SUMS-check-against-live-root.txt`, 15801 OK).

```
archive: /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence
envelope | anchor status/detail | offset(pre_spawn) s | offset(sampling_stopped) s | offset change ms | span ms (max-min over 5 stamps) | baseline s (stopped-pre_spawn, monotonic) | equiv rate ppm (change/baseline) | anchor-only H ms | effective bound ms | interior status | span_mismatch | coverage-480 s | native samples | rail_sum_w W | error_bound_j | net_time_prov
01 | unknown/wall_minus_monotonic_span_exceeded | 1789778438.320378 | 1789778438.312345 | -8.033 | 8.039 | 599.8 | -13.39 |  |  | partial | None |  | 0 |  | None | None
02 | bounded/bounded | 1789778438.312340 | 1789778438.311934 | -0.406 | 0.411 | 592.1 | -0.69 | 0.704 | 1.123 | complete | False | 9.5367431640625e-07 | 2056 | 0.3227 | 1.7411453059492488 | None
03 | unknown/affine_clock_fit_empty | 1789778438.311927 | 1789778438.307485 | -4.442 | 4.535 | 589.9 | -7.53 |  |  | partial | None |  | 0 |  | None | None
04 | unknown/affine_clock_fit_empty | 1789778438.307349 | 1789778438.306015 | -1.334 | 1.344 | 592.3 | -2.25 |  |  | partial | None |  | 0 |  | None | None
05 | bounded/bounded | 1789778438.305999 | 1789778438.304818 | -1.181 | 1.191 | 592.2 | -1.99 | 1.786 | 2.980 | partial | True | -1.1920928955078125e-06 | 2038 | 0.3170 | None | None
06 | bounded/bounded | 1789778438.304799 | 1789778438.303656 | -1.143 | 1.153 | 590.0 | -1.94 | 1.008 | 2.164 | partial | True | 2.6226043701171875e-06 | 2038 | 0.3164 | 3.279594193879359 | None
07 | unknown/wall_minus_monotonic_span_exceeded | 1789778438.303637 | 1789778438.281315 | -22.322 | 22.360 | 590.6 | -37.79 |  |  | partial | None |  | 0 |  | None | None
08 | unknown/effective_clock_anchor_bound_exceeded | 1789778438.281258 | 1789778438.276754 | -4.503 | 4.541 | 592.4 | -7.60 | 0.532 | 5.077 | partial | None |  | 0 |  | None | None
09 | unknown/effective_clock_anchor_bound_exceeded | 1789778438.276679 | 1789778438.272193 | -4.485 | 4.524 | 590.1 | -7.60 | 0.821 | 5.348 | partial | None |  | 0 |  | None | None
10 | unknown/wall_minus_monotonic_span_exceeded | 1789778438.272125 | 1789778438.285164 | +13.039 | 13.047 | 590.9 | +22.07 |  |  | partial | None |  | 0 |  | None | None
11 | bounded/bounded | 1789778438.285143 | 1789778438.283636 | -1.507 | 1.520 | 592.3 | -2.54 | 2.492 | 4.015 | partial | True | -4.0531158447265625e-06 | 2039 | 0.3183 | None | None
12 | bounded/bounded | 1789778438.283612 | 1789778438.282118 | -1.494 | 1.508 | 590.5 | -2.53 | 0.429 | 1.939 | complete | False | 0.0 | 2070 | 0.3146 | 3.0554235977478688 | None

sha256 of each session.json read above:
11f999b0f8c4992e271967933625e02acf85854170e2b7a50c7709182f7a08c6  envelope-01/session.json
bbeb51b8091304c22a0f021a49d0352d3dd808d66a4fee4310b0e91658bd6ba3  envelope-02/session.json
15fd5e92d23fe2d263daae9e266baa1c28000d35ec11489ff0b12e8913f2f9e9  envelope-03/session.json
30b8c392495b7ae51a37114414f997b45114c11d25da57ff4327b0b7004c5487  envelope-04/session.json
e10d95183894371bb8970bb1423bddd3f5d3f56e95ccd53abeb2144fd2721663  envelope-05/session.json
66239a264f86202a75280396ab68251a9bd57b27c1b348ae934ffce85305d3fc  envelope-06/session.json
7f45379557cb8e34dc66b3229f0be57410fe0840d53716180124cca040f0397a  envelope-07/session.json
cd56a38e581837ec82431950b05823a57cc0a8d2d85db15bad41eca612d92b99  envelope-08/session.json
7fb73b249c3ea4bd74fe23d4aedc08bc1eed1bde76d429080cc90f28bea38cd0  envelope-09/session.json
6c16f672ff53b4d32ecc7bdc266e4128fe175eef209e0f50023996bde28b1f96  envelope-10/session.json
f9dea9108a5708cc9f8edb543fed64188fe0b095a9119f06f657bd10bd121e1f  envelope-11/session.json
e42ae3fcdbe2b7c727a77e42f7bad69896bed940a4daf897da5ca9395471eb84  envelope-12/session.json

float64 ulp at epoch scale: 2.384185791015625e-07 s ; at 480 s: 5.684341886080802e-14
per-envelope start drift s: [None, None, None, None, None, None, None, None, None, None, None, None]
summary.json: retained 2 status INCONCLUSIVE block_two_stop {'causes': ['observer_floor_above_smallest_holdable_share'], 'outcome': 'no cutoff qualifies', 'pairs': None, 'pairs_reason': 'not available in source evidence'} unfiltered_single_envelope_sd_j 1.4542732582500855 single_envelope_sd_j 2.726835932508704
per-envelope excluded reasons: [(1, ['clock_anchor_unresolved', 'incomplete_interior_support']), (2, []), (3, ['clock_anchor_unresolved', 'incomplete_interior_support', 'start_drift']), (4, ['clock_anchor_unresolved', 'incomplete_interior_support']), (5, ['incomplete_interior_support']), (6, ['incomplete_interior_support', 'start_drift']), (7, ['clock_anchor_unresolved', 'incomplete_interior_support']), (8, ['clock_anchor_unresolved', 'incomplete_interior_support']), (9, ['clock_anchor_unresolved', 'incomplete_interior_support', 'start_drift']), (10, ['clock_anchor_unresolved', 'incomplete_interior_support']), (11, ['incomplete_interior_support']), (12, [])]
per-envelope collector_start_drift_s: [(1, 0.32), (2, 8.01), (3, 10.23), (4, 7.81), (5, 7.89), (6, 10.18), (7, 9.53), (8, 7.75), (9, 10.06), (10, 9.24), (11, 7.85), (12, 9.6)]
network_time_provenance_reason (envelope 01): not established by this desk harness
```

## C2 — the sudoers slice as installed on this machine (D-127), and whether the toggle runs without a password

Command: `sudo -n -l` (list only; no command executed).

```
Matching Defaults entries for edr on mac:
    env_reset, env_keep+=BLOCKSIZE, env_keep+="COLORFGBG COLORTERM",
    env_keep+=__CF_USER_TEXT_ENCODING, env_keep+="CHARSET LANG LANGUAGE LC_ALL
    LC_COLLATE LC_CTYPE", env_keep+="LC_MESSAGES LC_MONETARY LC_NUMERIC
    LC_TIME", env_keep+="LINES COLUMNS", env_keep+=LSCOLORS,
    env_keep+=SSH_AUTH_SOCK, env_keep+=TZ, env_keep+="DISPLAY XAUTHORIZATION
    XAUTHORITY", env_keep+="EDITOR VISUAL", env_keep+="HOME MAIL",
    lecture_file=/etc/sudo_lecture, !log_allowed

Runas and Command-specific defaults for edr:
    Defaults!/usr/sbin/systemsetup -setusingnetworktime off,
    /usr/sbin/systemsetup -setusingnetworktime on !requiretty

User edr may run the following commands on mac:
    (ALL) ALL
    (root) NOPASSWD: /usr/sbin/systemsetup -setusingnetworktime off,
        /usr/sbin/systemsetup -setusingnetworktime on
    (root) NOPASSWD: /usr/bin/powermetrics
```

Command: `sudo -n /usr/sbin/systemsetup -getusingnetworktime` (the READ form is NOT in the slice; expected to require a password; nothing was changed):

```
sudo: a password is required
rc=1
```

The SET forms (`-setusingnetworktime off` / `on`) were NOT executed by this activation: the machine is not in a window and toggling is a state change reserved for the ruled entry-point step.

## C3 — night LaunchAgent state at packet assembly

```
-	0	com.joulewise.magistrate
com.joulewise.magistrate.plist
```

## C4 — unified log for the time daemon over the pilot window (raw file: `exhibit-D-timed-log-0210-0435.txt`)

Command: `/usr/bin/log show --predicate 'process == "timed"' --start '2026-09-22 02:10:00' --end '2026-09-22 04:35:00' --style compact` (191 lines; sha256 70218c4a41b0ee87e20f032790e442451f36d713df49933ccbaba907395797b6). The `cmd,apply,src,adjtime` lines, with `adjust` in seconds and the preceding `ntp_adjtime` line's `freq_scaled` (units of 2^-16 ppm; divide by 65536 for ppm):

```
24:2026-09-22 02:28:08.335 Df timed[381:2788754] [com.apple.timed:data] cmd,ntp_adjtime:out,modes,2017,offset_us,-7764578,freq_scaled,-45002,maxerror_us,17386
25:2026-09-22 02:28:08.335 Df timed[381:2788754] [com.apple.timed:data] cmd,apply,src,adjtime,rtc_s,14598637.789071666,rtc_unc_s,0.000500005,t_s,811762088.322831392,unc_s,0.017386546,mach,6980400242946,adjust,-0.007764578,success,
49:2026-09-22 02:56:19.109 Df timed[381:2788754] [com.apple.timed:data] cmd,ntp_adjtime:out,modes,2017,offset_us,-4294276,freq_scaled,-127056,maxerror_us,16714
50:2026-09-22 02:56:19.109 Df timed[381:2788754] [com.apple.timed:data] cmd,apply,src,adjtime,rtc_s,14600328.576196916,rtc_unc_s,0.000500007,t_s,811763779.104481697,unc_s,0.016714522,mach,7020979133393,adjust,-0.004294276,success,
64:2026-09-22 03:09:28.304 Df timed[381:2788754] [com.apple.timed:data] cmd,ntp_adjtime:out,modes,2017,offset_us,5484,freq_scaled,-127056,maxerror_us,21348
65:2026-09-22 03:09:28.304 Df timed[381:2788754] [com.apple.timed:data] cmd,apply,src,adjtime,rtc_s,14601117.770467540,rtc_unc_s,0.000500008,t_s,811764568.297222495,unc_s,0.021348167,mach,7039919795711,adjust,0.000005484,success,1
79:2026-09-22 03:09:28.350 Df timed[381:2788754] [com.apple.timed:data] cmd,ntp_adjtime:out,modes,2017,offset_us,-19789,freq_scaled,-127056,maxerror_us,21348
80:2026-09-22 03:09:28.350 Df timed[381:2788754] [com.apple.timed:data] cmd,apply,src,adjtime,rtc_s,14601117.816235334,rtc_unc_s,0.000500008,t_s,811764568.342990160,unc_s,0.021348474,mach,7039920894764,adjust,-0.000019789,success,
94:2026-09-22 03:09:28.408 Df timed[381:2788754] [com.apple.timed:data] cmd,ntp_adjtime:out,modes,2017,offset_us,-33259,freq_scaled,-127056,maxerror_us,21348
95:2026-09-22 03:09:28.408 Df timed[381:2788754] [com.apple.timed:data] cmd,apply,src,adjtime,rtc_s,14601117.875053043,rtc_unc_s,0.000500008,t_s,811764568.401807785,unc_s,0.021348870,mach,7039922306709,adjust,-0.000033259,success,
119:2026-09-22 03:34:21.014 Df timed[381:2793b70] [com.apple.timed:data] cmd,ntp_adjtime:out,modes,2017,offset_us,-20277977,freq_scaled,-498151,maxerror_us,15704
120:2026-09-22 03:34:21.014 Df timed[381:2793b70] [com.apple.timed:data] cmd,apply,src,adjtime,rtc_s,14602610.481062166,rtc_unc_s,0.000500005,t_s,811766060.984621048,unc_s,0.015704614,mach,7075744850303,adjust,-0.020277977,success
144:2026-09-22 04:03:55.705 Df timed[381:2798a6b] [com.apple.timed:data] cmd,ntp_adjtime:out,modes,2017,offset_us,16596198,freq_scaled,-165813,maxerror_us,16317
145:2026-09-22 04:03:55.705 Df timed[381:2798a6b] [com.apple.timed:data] cmd,apply,src,adjtime,rtc_s,14604385.204332333,rtc_unc_s,0.000500005,t_s,811767835.711004257,unc_s,0.016317371,mach,7118338208822,adjust,0.016596198,success,
159:2026-09-22 04:07:36.808 Df timed[381:2799601] [com.apple.timed:data] cmd,ntp_adjtime:out,modes,2017,offset_us,15736,freq_scaled,-165813,maxerror_us,17485
160:2026-09-22 04:07:36.808 Df timed[381:2799601] [com.apple.timed:data] cmd,apply,src,adjtime,rtc_s,14604606.308164041,rtc_unc_s,0.000500007,t_s,811768056.814276695,unc_s,0.017485074,mach,7123644700536,adjust,0.000015736,success,
174:2026-09-22 04:07:36.854 Df timed[381:2799601] [com.apple.timed:data] cmd,ntp_adjtime:out,modes,2017,offset_us,10371,freq_scaled,-165813,maxerror_us,17485
175:2026-09-22 04:07:36.854 Df timed[381:2799601] [com.apple.timed:data] cmd,apply,src,adjtime,rtc_s,14604606.354114000,rtc_unc_s,0.000500007,t_s,811768056.860226393,unc_s,0.017485327,mach,7123645803447,adjust,0.000010371,success,
189:2026-09-22 04:07:36.909 Df timed[381:2799601] [com.apple.timed:data] cmd,ntp_adjtime:out,modes,2017,offset_us,-8941,freq_scaled,-165813,maxerror_us,17485
190:2026-09-22 04:07:36.909 Df timed[381:2799601] [com.apple.timed:data] cmd,apply,src,adjtime,rtc_s,14604606.409287833,rtc_unc_s,0.000500008,t_s,811768056.915400028,unc_s,0.017485633,mach,7123647128081,adjust,-0.000008941,success
```

Count of `settimeofday` or `step` lines in the window:

```
0
```
