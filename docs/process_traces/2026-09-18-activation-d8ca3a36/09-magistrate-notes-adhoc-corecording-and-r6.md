# Magistrate notes — ad-hoc co-recording (record 08) and the r6 idle reference (record 07), 2026-09-18 18:2x PDT

Orientation data only; the lane 232 harness will re-record under the ruled protocol. Nothing here is a cutoff.

## Record 08: eight 30 s sampler rounds beside `sudo -n powermetrics --samplers cpu_power -i 30000 -n 8`

State: three Astra seats (records 05–07) running their reads and test scratch, Ed's interactive `claude` (pid 1505) idle, this activation (pid 3006). `sudo -n powermetrics` needs no password (`/etc/sudoers` grants `(root) NOPASSWD: /usr/bin/powermetrics`; `sudo -n -l` 18:28). The two clocks are not aligned to the second (the sampler started 18:20:44, powermetrics 18:21:14 and each covers ~30 s), so rows pair by overlap, not identity.

| sampler round (start) | busy_cores | powermetrics interval (start) | CPU mW | P1-cluster active % |
|---|---|---|---|---|
| 1 (18:20:44) | 0.270 | 18:21:14 | 261 | 0.81 |
| 2 (18:21:16) | 0.187 | 18:21:44 | 410 | 0.05 |
| 3 (18:21:48) | 0.989 | 18:22:15 | 4333 | 13.8 |
| 4 (18:22:20) | 1.445 | 18:22:45 | 7470 | 45.2 |
| 5 (18:22:52) | 1.072 | 18:23:15 | 5858 | 36.7 |
| 6 (18:23:24) | 0.197 | 18:23:45 | 1523 | 13.2 |
| 7 (18:23:56) | 0.166 | 18:24:15 | 378 | 0.0 |
| 8 (18:24:28) | 0.243 | 18:24:45 | 763 | 0.29 |

E-cluster and P0-cluster HW active residency read 100 % in every interval (the HW residency line is cluster-on time, not core busy time; the per-CPU lines carry the busy fraction). Observer cost per round: 1.67–1.80 cpu-s (whole-round, census included), consistent with record 30's 1.15 cpu-s desktop figure plus the seats' contention.

Two observations for the consult and the memo:

1. **Busy cores and energy are not proportional across states.** Rounds 1–2 and 6–8 sit at 0.17–0.27 busy cores for 0.26–1.5 W; rounds 3–5 at 1.0–1.45 busy cores for 4.3–7.5 W. The P1 cluster's active share tracks the power, so where the busy time lands (E-cluster near 1 GHz vs P-cluster near 4 GHz) decides the joules per slot as much as the busy-core count. A cutoff in busy cores alone therefore needs a stated worst-case placement or a companion residency predicate; the consult's Q3 asks exactly this.
2. **Attribution is blind to short-lived children.** In round 4 the aggregate is 1.445 busy cores but the top consumer is 0.014 (`claude`); the seats' CPU went into test interpreters and shell commands born and exited between snapshots, which the contract already states an observer cannot recover. The aggregate (host counters) is right; the top-consumers list is not evidence of who was busy. The memo must say so where it quotes attribution rows.

## Record 07: the r6 idle reference (Astra high, complete, V1 pass on all 17 manifest and evidence pins)

- The accepted-clean bundles' instrument IS macOS `powermetrics` (CPU rail, nominal 10 Hz, `raw/powermetrics.plist` frames per interval), on macOS 25F84, Mac15,9, AC high-power. So lane 232's co-recording is already in the instrument's units, and the judge's item 1 ("through the actual floor pipeline") differs from powermetrics co-recording only in the pipeline's reduction (ABBA pulse contrast, warmup trimming, GPU-rail baseline), not in the sensor.
- Initial idle (sampling start to first warmup, ~5.0 s): CPU 0.071–0.696 W across the 17 members (median ≈ 0.10 W); whole-capture CPU mean 0.121–0.359 W. Three a9 members lack the raw plist (F1, non-blocking for this lane: the CSV rail still carries the power).
- No process census, load or busy-core reading exists in any bundle; the "idle active core sum" the seat computed (0.24–2.64) is Σ(1 − idle − down) over the 16 CPUs from residency, NOT `cpu_interval_v1`, and includes powermetrics' own cost. It is not comparable to the sampler's `busy_cores` without a bridge measurement (both quantities in the same interval on today's build). The harness must record per-CPU residency so that bridge can be computed.
- Epoch caveat stands: 25F84 references do not on their face transfer to 25G83; the memo's reference must be a fresh census-clean idle on 25G83 with the r6 numbers as the consistency check.
