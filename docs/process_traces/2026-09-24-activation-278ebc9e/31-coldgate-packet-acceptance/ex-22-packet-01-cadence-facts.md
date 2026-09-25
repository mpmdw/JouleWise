# Cadence facts and causal limits

**Native interval** means a raw plist frame's `elapsed_ns`, not the time when a reader received it. **r6/r7** are the sixth/seventh issued 17-member D-079 artifacts. **Anchor** means the estimator mapping native sampler time to the capture's wall clock. [docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md:5-11,28]

## Identity and measurements

| Source | OS / sampler / requested interval | Measured interval and yield |
|---|---|---|
| r6 reference | 25F84; `/usr/bin/powermetrics` SHA-256 `d1dccad0d0a8016d38bd584bdae283566723096162f06ef663debb4a5762fe69`; 100 ms | Per-run median 119.628–121.085 ms in the 17-member reference; overall maximum 144.252 ms. [docs/process_traces/2026-09-15-activation-08ca8197/10-arm-evidence/30-stage-output-b.txt:7; docs/process_traces/2026-09-19-activation-b165c535/03-diagnostic-invalid-captures-astra.md:2 `reference`] |
| 19 Sep n1/n2 | 25G83; SHA-256 `b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5`; 100 ms | Each slot's raw frame count and min/median/p95/max are in the table below; 20,605 raw frames map one-to-one to each CSV rail, so no alternate-frame loss was found. [configs/calibration/preregistration_d079_epoch_25g83_rev1.md:132-136; docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md:5-28] |
| 20 Sep `qpe01` quiet-predicate pilot | 25G83 pilot, not D-079 corpus | Aborted after settle with zero completed envelopes: overlapping agent-census `pgrep` calls matched one another. Partial envelope 1 has zero usable native samples. [docs/process_traces/2026-09-20-activation-21752427/01-qpe01-pilot-n1-20260920-harvest-record.md:9-20] |
| 22 Sep 02:17 `qpe01` | 25G83 pilot, 100 ms setting | Envelope 2: 2,535 frames in 600 s, mean `elapsed_ns` about 237 ms. Pilot retained 2/12 envelopes; clock-anchor and support exclusions were separate from cadence. [docs/process_traces/2026-09-22-activation-22666c9f/01-qpe01-pilot-n1-20260922-0217-harvest-record.md:63-81,234-237] |
| 22 Sep 21:00 `qpe01` | 25G83 pilot | Twelve envelopes retained; each had about 2,140–2,201 native samples in its 480 s interior (roughly 218–224 ms per interior sample, a quotient rather than a measured interval distribution). A background daemon contaminated energy, not sample identity. [docs/process_traces/2026-09-22-activation-a022aecc/01-qpe01-pilot-n1-20260922-2100-harvest-record.md:177-196,249-264] |
| 23 Sep 07:00 `qpe01` | 25G83 pilot | Eleven of twelve 480 s interiors retained, native sample counts 2,038–2,071 (quotients about 232–236 ms); envelope 9 excluded for non-observer process load. The pilot's observer floor exceeded its planned 0.05-core block-two level. [docs/process_traces/2026-09-23-activation-5fe5a59b/01-qpe01-pilot-n1-20260923-0700-harvest-record.md:106-123,140-164,206-222] |

The cited identity checks identify the sampler by executable path and SHA-256, not a human-readable `powermetrics` release number; no release number is established here. Both epochs retain `sampling_interval_ms: 100` and `estimator_revision: joint_loss_sublevel_interval_branch_v2` in the six-field acceptance identity. [docs/process_traces/2026-09-15-activation-08ca8197/10-arm-evidence/30-stage-output-b.txt:7; configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:20-26; configs/calibration/preregistration_d079_epoch_25g83_rev1.md:132-136]

**19 Sep slot-level raw `elapsed_ns`:** each cell is frame count; median ms. This is *native interval*, not delivery-arrival jitter. [docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md:11-28]

| Slot | n1 | n2 | Slot | n1 | n2 |
|---|---:|---:|---|---:|---:|
| d01 | 871;244.3 | 862;247.6 | d07 | 855;249.7 | 862;247.3 |
| d02 | 850;248.8 | 860;247.5 | d08 | 860;248.9 | 865;246.6 |
| d03 | 851;249.2 | 874;245.0 | d09 | 862;247.1 | 843;250.5 |
| d04 | 862;245.5 | 880;244.0 | d10 | 856;246.9 | 845;254.3 |
| d05 | 855;247.7 | 860;249.9 | d11 | 862;248.1 | 846;251.5 |
| d06 | 869;245.8 | 863;249.1 | d12 | 855;248.6 | 837;251.6 |

## What is established, and what is not

- The six missed-pulse captures in n1 had no interval wholly inside the required plateau interior `[on+0.25 s, off-0.25 s]`; power excursions still appeared in the raw trace. Two other invalid n1 captures failed clock anchoring. This makes coarse phase sampling a supported mechanism for missed interiors, not proof that the binary caused the interval increase. [docs/process_traces/2026-09-19-activation-b165c535/03-diagnostic-invalid-captures-astra.md:2 `misses`, `detector`, `causes`]
- The r6 stored historical anchor label was `powermetrics_native_second_censored_intersection_v1`; the 25G83 observations stored `powermetrics_native_second_rate_aware_set_membership_v1`. r6's issued corpus was subsequently re-derived under anchor-v3, so comparing those stored method labels alone is not an estimator counterfactual. The r7 reissue changed one estimator-code pin but retained the 25F84 identity and the 17 statistics. [docs/process_traces/2026-09-19-activation-b165c535/03-diagnostic-invalid-captures-astra.md:2 `reference`; docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md:64-70; configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:495-505]
- Archived raw plist `elapsed_ns`, frame counts, native dates, CSV parity, and retrospective pilot distributions can be analyzed without a new run. The 19 Sep analysis found raw-to-CSV parity and longer native intervals; it could not measure frame arrival jitter or decide binary versus scheduler versus sampler work. [docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md:5-9,28,44-52]
- The proposed A243 diagnostic matrix is 15 matched 90 s runs, about 35 minutes with settles, varying 50/100/200 ms requests, sampler sets, hide flag, idle/busy load, file/stdout path and hooks. It invokes `sudo -n /usr/bin/powermetrics`; execution needs authorized sudo and an agent-free quiet window. An old compatible signed binary or alternate OS boot is a further counterfactual, not an available result. [docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md:30-50; docs/process_traces/2026-09-19-activation-a743be05/06-consult-artifacts/jw_cadence_bench.zsh:1-48]
- No later executed A243 binary/OS crossover is identified in the lane's live queue record; its 22 Sep note adds the 2,535-frame pilot datum. This is an inventory limit, not proof none exists elsewhere. [TASK_QUEUE.md:872]
