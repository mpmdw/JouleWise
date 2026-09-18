# Live sampler smoke (V5, native) and two bench fixes — NIGHT-GATE-QUIET-ADMISSION-01, 2026-09-17 20:15–20:40 PDT

The seat's sandbox denies `sysctl` and `top`, so the lead ran the sampler natively in `/Users/edr/code/JouleWise-wt-gate-quiet`. Machine state: Ed's interactive session active (the census would refuse a night), Spotlight store rebuild finished at ~20:0x, load 1.5–2.1. These lines characterise the sampler on a busy desktop, not a quiet machine; they are evidence for lane QUIET-PREDICATE-EVIDENCE-01's observer-cost item, not for any cutoff.

## Run 1 — head `6bcd90a3` (D1–D7 as delivered), 20:15:24 PDT

```
subprocess.CalledProcessError: Command '('/usr/bin/top', '-l', '2', '-s', '30.0', '-n', '0')' returned non-zero exit status 1.
```

Defect: the `-s` argument was built from the float `30.0`; `top` accepts integers only (`top -l 2 -s 1.0 -n 0` exits 1, `-s 1` prints two samples). The injected-sampler regressions could not see it. Cured in fix round 1 (brief 08 item 7: integer argv, integer validation of `sample_interval_s`, exact-tuple argv tests; the float mutant fails the argv test, seat report V4).

## Run 2 — head `a2671902` (fix round 1), 20:38:27 PDT

```
ValueError: top CPU percentages do not sum to 100
```

Defect: `second_top_idle_fraction` required user + sys + idle to sum to 100 within 0.1, but `top` rounds the three independently; observed live lines: `9.36% user, 3.6% sys, 87.3% idle` (sum 100.26) and `1.53% user, 7.17% sys, 91.28% idle` (99.98). Bench fix by the lead (commit `536fd4db`: tolerance 1.0 with the observed lines in a comment) plus regression `test_second_top_idle_fraction_tolerates_top_rounding_but_not_gaps` (commit `649eefd2`), proven to kill the strict `> 0.1` mutant (the mutant raises `ValueError: top CPU percentages do not sum to 100` under the test). Same signature as run 1 (a live-parse defect invisible to injected fixtures); the standing escalation rule was considered and the bench fix chosen because the fix is one constant and one test, smaller than any delegation contract. Both defects go to the delta re-audit as new surface.

## Run 3 — head `536fd4db`, 20:39:36 PDT — PASS

```
{"busy_cores": 0.608, "host_busy_cores": 0.608, "load_avg_diagnostic": {"raw": "{ 2.09 1.94 1.92 }"},
 "observer_cpu_s": 0.2475,
 "top_consumers": [{"busy_cores": 0.0864, "command": ".../WindowServer", "observer": false, "pid": 417},
                   {"busy_cores": 0.0794, "command": "claude", "observer": false, "pid": 2490},
                   {"busy_cores": 0.0781, "command": ".../Terminal", "observer": false, "pid": 2461}]}
```

Reading: `busy_cores` 0.61 on a desktop with an interactive session, WindowServer and Terminal active; the host and process figures agree (max of the two is 0.608). Observer cost 0.2475 cpu-s per 30 s round including one census probe, i.e. 0.0082 core-equivalents per interval (the cold judge measured 0.0072 without the census; the census adds ~0.03 cpu-s). Load average 2.09 while the interval-CPU reading was 0.61 core: the same disagreement the packet reported, in the direction that matters (load overstates).

Note: the sampler's `top_consumers` shows the observer's own `claude` process as `observer: false` because the observer pid is the Python interpreter, not the interactive Claude session; the sampler's own interpreter did not reach the top three. The execution refuter's mutant 11 covers observer labelling.
