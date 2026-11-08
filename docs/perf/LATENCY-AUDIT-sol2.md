# JouleWise latency audit — independent Sol 2 seat

Prepared 2026-11-07 for task `latency-audit-sol2`, branch
`perf/2026-11-08-latency-audit-sol2`. Snapshot: `4e7e878a151d919faf56bb9131af1fcca4b7be75`.
Some source records are dated November 8; their dates are preserved, not treated
as observations made by this audit. No other latency-audit seat's branch was read.

The largest defensible immediate wins are moving the approximately 100-minute
desk off the measurement Mac and removing the BYTES test's serial critical
path. R0 retry handling has already been changed in the audited ALIGN lane;
count that as an existing improvement, not a new saving. R1's approximately
16-hour figure is an all-caps planning calculation, not a measured runtime.
There is no evidence here that a valid v4 measurement can be reduced to 1–5
hours without changing its design.

## Evidence and interpretation

**MEASURED** means an elapsed observation already recorded in the repository
(including a recorded approximate observation). **ESTIMATED** means a design
budget, arithmetic projection, target, or explicitly unmeasured cost. Every
proposed duration below is ESTIMATED until timed. A historical observation is
not a benchmark of today's tree. No sealed value or outcome is reproduced.

Time classes:

- **PHYSICS-BOUND (F):** decode throughput, thermal recovery, or required
  capture/idle observation under the current registered design. Optimize the
  surrounding implementation; preserve the observation and release conditions.
- **DESIGN-BOUND (D):** shortening this changes the roster, exposure, estimator,
  treatment, physical configuration, or a scientific gate. Lead/registration
  action is required; these are not implementation recommendations.
- **PROCESS-BOUND (P):** software work, serialization, retries caused by tooling,
  redundant verification, scheduling, polling, and unnecessary idle gaps.

Rows describing whole workflows are parents of component rows, not additive
costs. A cap is never counted as a sleep. Moving work to another machine saves
measurement-Mac availability, not necessarily total compute hours. Estimates
without a timing record are identified as budgets, and excluded from the firm
weekly ranking unless an explicit scenario is supplied.

| Source | Exact evidence / authority |
|---|---|
| S1 | [RUN_STATE.md](../../RUN_STATE.md), items 202 (R1 bounds), 206–211 (R0 contention/display), 213 (turnaround and off-Mac work), 187–188 (SSD), 196 (r3 duration), 169/172 (pilot desk), 154 (BYTES CI). Item numbers are more durable than line numbers. |
| S2 | [FINAL-DESIGN](../align/council-2026-11-05/FINAL-DESIGN.md) §§2.6, 2.8, 3.1; [Amendment 1](../align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md) §§A1–A3; [Amendment 2](../align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-2.md). Amendment 1 removes N and the 122B screen. The original 19-member/two-model plan is superseded. |
| S3 | ALIGN source at `9c40e4e5d9fa453cce3c70984e11fa382b7d4591` (`origin/lane/2026-11-05-align-pilot10-benign`): `joulewise/align/r0{,_runner,_mlx}.py`, `configs/align/v4/r0_desk.json`, `docs/align/r0/R0-L3-contention-rule.md`, `docs/run_reports/2026-11-05-align-v4-wp4b-r0-wall-time.md`. Read with `git show <commit>:<path>`; these files are absent from this pruned main tree. |
| S4 | Eleven R0 `report.json` records, original through rerun 10, on `origin/records/2026-11-{06,07}-align-r0-v4*`. Exact commits, paths, UTC boundaries and `check_seconds` are in [the evidence ledger](latency-audit-sol2-evidence.json). Only code/records Git objects were read. |
| S5 | R1 source at `e901eb2a480d51377a494be9d797733dfcd0220b` (`origin/lane/2026-11-06-v4-r1-integrated`): `scripts/align_r1_rehearsal.py` (`phase_plan`, `segment_bounds`, `night_worst_case_s`), `configs/align/v4/r1_runtime.json`, `docs/align/r1_runtime_contract.md`, `scripts/align_v4_kit.py`. |
| S6 | S3's `docs/align/v4/SSD-ALWAYS-ATTACHED-STUDY.md` §6 and `joulewise/align/apple/ssd_qualification.py:plan`; S1 item 187 corrects the default to 125 segments. This is a qualification design, not a completed hardware run. |
| S7 | CI map/report at `87d9b445c9b3b5e9fb7f76a07230e3399821b3fb` (`origin/lane/2026-11-06-ci-timings-main`): `scripts/test_timings.json`, annotations `_hosted_observations_2026_11_06_cross_lane`, `split_modules`, and `docs/run_reports/2026-11-06-ci-timings-pr-body.md`. Hosted runs and statistic definitions are recorded there. |
| S8 | [Under-90 report](../run_reports/2026-11-06-b5-under-90.md) §§3, 5, [full-chain synthetic report](../run_reports/2026-11-07-b5-robust-fullchain.md), [resume report](../run_reports/2026-11-06-b5-robust.md). Timing and synthetic equality evidence only. |
| S9 | [Decision log](../decision_log.md), D-188/D-189 and D-186; [orchestration](../orchestration.md), “What the prune keeps” and “Cold gates, councils and round limits.” Result equivalence preserves every registered number and decision, including refusal order. |
| S10 | [CI workflow](../../.github/workflows/ci.yml), [sharder](../../scripts/shard_tests.py), [timing map](../../scripts/test_timings.json), [quick tier](../../scripts/quick_suite.py). Current main and S7 are different timing populations. |
| S11 | S3's `tests/test_bytes_analysis.py:CampaignWordRates`, `tests/fixtures/bytes/campaign.py:archive_campaign`, `tests/align/test_moe_calibration.py:calibration`, `joulewise/bytes_analysis.py`, `scripts/align_v4_kit.py`. Source inspection, no execution. |
| S12 | [Publication smoke](../../scripts/release_check.py), [pack construction/verification](../../scripts/package_bundle_pack.py), [record landing](../../scripts/land_window_records.py), [watchdog](../../scripts/magistrate_watchdog.py), [watchdog installer](../../scripts/install_magistrate_watchdog.sh). |
| S13 | [Pilot-8 build/review record](../process_traces/2026-11-04-magistrate-cf1baad2/RECORD.md): build about 9 min, executing review about 7 min, calibration build 6 min. These are whole seat observations, not generator-only timings. |

## Inventory: measurement and turnaround

Targets in the last column refer to the fix list below. A target that depends
on a design decision is explicitly marked D.

| Recurring step | Duration and evidence | Time class | Concrete opportunity / expected duration |
|---|---|---|---|
| R0 complete pass | **ESTIMATED 3–4 h** all-pass target; worst token budget **7.27 h before setup/prefill/hash** (S3 WP4b report). No complete successful R0 in the eleven records inspected. | F for fixed inference/capture; P for retries and setup; D to reduce tests/tokens. | Keep hardware tests serial. F4 can avoid repeating already authenticated checks; no demonstrated 1–2 h whole-run target. |
| R0 repeated attempts and between-attempt work | **MEASURED 10,787.358 s = 3.00 h active**, **34.63 h** first start to rerun-10 end; **31.63 h** between records (S4). Gaps include repairs, reviews, overnight scheduling and owner waits. | P, with owner/review dependencies. | Already delivered R0-L3 flags ordinary contention and allows one sustained-load redo; stop counting full restarts as unavoidable physics. Do not claim all 31.63 h recoverable. |
| R0 cheap host/identity checks | **MEASURED about 0.3–0.43 s each** (S4). | P. | Leave them; moving them before expensive work costs under 1 s. |
| R0 model-file inventory/hash | **MEASURED disk check 18.47–19.78 s** (S4); includes more than hash alone. | P. | Immutable manifest keyed by revision/content, bounded parallel file hashing if profiled. F3 target **10–20 s**, low priority: seconds, not hours. |
| R0 MLX load and NLL/reference check | **MEASURED load about 13.5–13.7 s**, successful NLL checks **82–87.4 s** (S4). | P setup; F device-specific numerical work; D to remove the hardware check. | Prequalify tokenizer/reference/config off-Mac; retain exact pinned-stack hardware comparison. F4 target unchanged **about 2 min** for this pair on a fresh qualifying run. |
| R0 template/generated-tool/checkpoint checks | **MEASURED template 0.52–0.65 s**, generated successful check **43.8–51.0 s**, checkpoint receipt **0.49–0.63 s** (S4). | P parsing/receipt; F generation; D to change prompts, seeds or pass criteria. | Do source/template checks ahead of Mac time. Reuse only exact, authenticated configuration evidence; F4 saves seconds/minutes, not a long decode. |
| R0 memory stress | **MEASURED 731.9–746.6 s** for the 40,960-position/6,144-decode test (S4). | F fixed device work; D to shorten the stress. | Preserve peak/swap test. Avoid repeating it after an unrelated SMC-only fix, if the lead admits exact evidence composition (F4). |
| R0 SMC enumeration/step | **MEASURED rerun-7 check 1,845.600 s**, ended inconclusive; partial failures **61.664–1,520.052 s** (S4). Current config: **ESTIMATED 300–1,200 s adaptive idle + 900 s load + 600 s recovery**, plus enumeration (S3). | F observations/settling; D to shorten profile; P whole-run retry amplification. | SMC first is already installed; one affected-capture redo/flag under R0-L3. Preserve the 900 s step: Amendment 2 explains why 60 s cannot classify slow sensors. |
| R0 effort ladder | **ESTIMATED variable**, two task pairs per rung, xhigh → medium → low; first passing rung stops further work (S3 `ladder`). Part of the 3–4 h target. | F decode; D rung/seed/budget; P only redundant recomputation. | Lower rungs are already skipped after success. Do not start at low to manufacture a speedup. Time the retained phase receipts. |
| R0 long-decode/#1632 check | **ESTIMATED 38,912 decoded tokens per attempt**, one normal attempt plus one conditional metadata attempt; success stops immediately (S3). At a hypothetical 10 tok/s: **64.9 min/attempt**, before prefill. | F throughput; D token count/required mitigation check. | Not two unconditional runs. Do not remove the second attempt from a failing-verdict path without a ruling. |
| R0 launch/display dwell | **ESTIMATED fixed 300 s** after display sleep; source constant/required production receipt (S1 items 209/211). | F current quiet transition; D shorter dwell; P earlier setup failures. | Prepare off-Mac and include dwell in deadline; no shortening. |
| R1 whole rehearsal | **ESTIMATED 56,206.962 s = 15.61 h** all-caps no-redo subtotal; **61,606.962 s = 17.11 h** with one batch wait; **90,662.942 s = 25.18 h** with specified G0 retries plus batch wait. Calibration/harvest and contention redos are extra (S5). | F + D dominant; P startup and recovery from tooling failure. | Instrument actual phase time first (F8). The older **4–4.5 h** estimate in FINAL-DESIGN is superseded by the integrated phase bounds. Do not promise 16 → 4 h from caps. |
| R1 idle soak / slope admission | **ESTIMATED fixed 1,800 s**, last **1,200 s** supplies reference/noise; slope failure can repeat it (S5). | F observation; D soak/slope requirements. | No adaptive truncation of the registered noise observation. Record failed-soak cost separately. |
| R1 planning steps and recovery | **ESTIMATED caps 5,163.995 s (30B), 5,763.995 s (D)**; each includes G0, 300 s quiet, rearmed member bound, 600 s recovery (S5). | F fixed work/settle; D exposure and cap policy; P load/close overhead. | The separate 600 s cooldown after 30B was already removed by R6-6 because recovery supplied it. Do not claim another 10-minute saving. |
| R1 High Power A-B-A | **ESTIMATED 3 × 4,328.995 s = 3.61 h** bound, including each release; actual legs are not measured here (S5). | F ordered physical comparison; D remove/reorder legs. | Keep order and mode read-back. High Power adoption remains the predeclared ≥25% rule, not a performance setting this audit can choose. |
| R1 precools and designed start states | **ESTIMATED four precools capped at 1,500 s each = 100 min**; three planning states capped at **3 × 5,763.995 s = 4.80 h**; one extra precool+attempt permitted per G0-inconclusive segment (S5). | F recovery/heating; D state design; P repeated failed setup. | Precools already release adaptively at the band. Preserve warmest-first states and measured release temperatures. Their caps are not fixed waits to delete. |
| R1 gated D × 3 and X-G | **ESTIMATED 4 × 1,800 s = 2 h** bounds; 300 s configured idle and gates lie inside the relevant member schedule (S5). | F + D. | Keep D_bank → D_spam a → D_spam b → X-G and matched predecessors. Extra cooldowns would change the duty-bar experiment. |
| R1 scheduled-batch avoidance / contention redo | **ESTIMATED up to 5,400 s** per one batch wait; up to two contention redos per quiet segment, each with release as applicable (S5). | P scheduling; D any change to avoidance/redo rule. | Plan expected placement from actual segment timings, while retaining conservative admission bounds; do not reduce bounds to force a start. No guaranteed saving without a clean schedule. |
| v4 W1 / D-window chains | **ESTIMATED W1 span 26,927 s (7.48 h), max 44,640 s (12.40 h)**; D span **40,527 s (11.26 h), computed max 58,260 s (16.18 h), ceiling 59,520 s (16.53 h)** (S2 Amendment 1). Pending R1 leaves in S5 confirm these are planning values. | F work; D roster/observation; P unused reservation/scheduling. | Release on authenticated terminal completion rather than sleeping until the window cap, with existing lifecycle proof. Do not count unused maximum as measured wasted runtime. |
| Per-member configured idle | **ESTIMATED fixed 300 s/member**; 18 W1 members would total **90 min**, 22 D-window members **110 min**, if all retain that setting (S2/S5). Already included in member-law planning. | F current baseline; D change idle. | Keep. The 450 s after-D fallback increases idle under a prospective decision; this is not a free adaptive-wait opportunity. |
| Warmup / load / controller scaffold | **ESTIMATED member law 516.575 + 1.13544 × episode_s**, scaffold **4,995 s/window** (S2). These aggregates are not measured warmup durations. | F warmup/load heat; P Python/session/bundle work; D changing warmup. | F8: separate load, warmup, baseline, finalization. Do not label the full 516.575 s intercept as removable Python overhead. |
| G0, G1 and decode holds | **ESTIMATED caps:** original G0 600 s; integrated R1 calibration G0 1,200 s, W1 cap derived from R1 waits; G1/H ≤300 s. G0 uses 10 samples plus 60 s slope, G1/H 5 release samples (S2/S5). | F recovery; D bands, timeouts, duty fraction and hold schedule. | Already condition-based. Preserve episode-start reference, lookahead evaluation and unowned attribution. Cooler/setup may improve actual recovery under the existing adoption rules; no asserted gain. |
| Member deadman / window reserve | **ESTIMATED 1,800 s member cap**; 3,300 s t0-stage + 7,200 s wait budget + 7,200 s pause allowance in window sizing (S2/S5). | D safety/design bounds; P only an implementation that needlessly waits them out. | A maximum is not an elapsed phase. Keep salvage/tail margin. Never shorten token-admitted work by lowering deadman to hit a wall target. |
| Opening/closing calibration, corpus, bound derivation and reference members | **ESTIMATED current v4/R1 elapsed unmeasured**. Historical timing observations: opening calibration **MEASURED about 6 min**, 18-member corpus **45 min**, bound derivation **12 min**, three references **7 min** (S1 item 29). These describe a historical chain, not interchangeable v4 costs. | F fixed capture/reference work; P fitting/serialization; D removing brackets or changing reference allocation. | Retain every required bracket and reference. Profile derivation separately from capture; include current scaffold once. R1's phase-cap sum assigns calibration brackets zero only because it does not bound them, not because they take zero time. |
| Finalize, record hashes, record landing | **ESTIMATED unmeasured 2–10 min budget** within the 30–45 min turnaround target (S1/S12); R0 per-check disk timing is not a window-finalization measurement. | P. | F3 target **2–5 min**, bounded hash workers, canonical sorted manifests, immutable close then commit. Need bytes/files/CPU/I/O timing before claiming a gain. |
| Offload, compression, copy verification | **ESTIMATED unmeasured**; volume **37.4–52.9 GB/two copies** from S2. Physical transfer floor at hypothetical 0.25–1 GB/s is **0.6–3.5 min/pass**, excluding compression, small files and cloud confirmation. | P throughput/redundant passes; D custody or external-device rule changes. | F3 planning budget **10–30 min**, target **5–15 min** only after device benchmark. Incremental immutable manifests; independently verify destination and server receipt before deletion. |
| Between-window thermal cooldown | **ESTIMATED 15–25 min** in S1 item 213; no time-series measurement inspected. | F, physical-setup changes D. | Keep lid open and ≥5 cm clearance per S2 §3.1. Optional cooler is adopted through R1 for the whole series; never toggle it between members or silently change a frozen setup. Target remains **15–25 min** until measured. |
| Pre-arm checks / quiet dwell | **ESTIMATED 2 min** for historical bracket helper (S1 item 26); **300 s** R0 display dwell; some older night paths require **600 s** clean dwell (S1/S12). These are distinct paths, not three waits to add to every v4 arm. | P static preparation; F current quiet admission; D changing dwell. | F6 precompute static checks off-Mac, retain fresh disk/power/census/meter checks at arm. Record which dwell the actual plan consumes; no universal 5-minute assumption. |
| Whole turnaround / per-window desk | **ESTIMATED 30–45 min target** and **about 100 min desk** (S1 items 213, 169/172); original design budgets desks about 2 h. Not observed new turnaround. | P desk/review; F cooldown/dwell. | F1: desk/review/kit on laptop while next window measures. **0 min desk on measurement-Mac critical path**, same complete desk elsewhere; fresh evidence needed to show **30–45 min** turnaround. |
| SSD qualification | **ESTIMATED 24,600 s = 6.83 h**, 125 segments, A-D-A-D-A, Ed unplug/replug twice (S6). Decode lasts fixed work, so 6.83 h is not a hard runtime bound. | F capture/settle; D block/pair count; P operator readiness only. | Preflight everything before Ed's slot. No three-block shortcut: zero residual df was the reason the 4.7 h plan was rejected. No qualification executed. |
| SSD qualification components | **ESTIMATED 5 × 600 s = 50 min settle; 120 × 120 s = 4 h segments; 120 × 60 s = 2 h gaps** (S6); bursts occupy gaps and fixed decode can overrun the 120 s guess. | F observations and write-recovery; D shorten/gap overlap. | Preserve block order and power/control comparison. Faster extraction afterward is P, but unmeasured. Current external-volume prohibition remains. |
| Historical quiet kit / machine-test gate | **ESTIMATED 11.3 h kit +10 agent-free min**, **28.6 h deadline** (S1 item 41); 40-minute machine test was planned in item 39. | F prescribed validation; D omit captures; P tooling failures/retries. | Prequalify chain/courier/config off-Mac. Item 41 records **MEASURED approximately 34 min** lost to four courier-stub retries: test real terminal delivery before reserving a quiet slot. Historical, not added to v4 recurrence. |

## Inventory: analysis, release and engineering

| Recurring step | Duration and evidence | Time class | Concrete opportunity / expected duration |
|---|---|---|---|
| Block-5 blind dry run | **MEASURED approximately 37 h r1 → 1 h 40 min r3**, S1 item 196. r2 dry-j **9,145 s (152 min)**, S8. Different load/worker conditions; not all speedup is code. | P. | Already achieved precedent. Preserve D-188 comparator and blinding. F6/F7 seek additional minutes, not another 35 h credit. No analysis executed here. |
| Analysis source census, kept-unit validation and manifest | **MEASURED r2 steps 0/2/3: 85 / 13 / approximately 0 s** at reported precision (S8). | P authentication/traversal. | Ordered bulk hashing/census is already implemented. Preserve every authenticated input and refusal; target approximately **1–2 min total**, not a major remaining r3 saving. |
| Dry-run strict validation / bracket / extraction | **MEASURED r2 steps 1/3b/4/5: 901 / 1,658 / 842 / 1,426 s** (S8). | P arithmetic/authentication implementation; D removing required checks. | Same-output memoization/parallel authenticated work. S8 synthetic full chain **903 → 401 s**, with exact registered output equality; **not live timing**. Prefetch only discovery-eligible candidates (153 refits → 12 synthetic), preventing wasted pool work. |
| Dry-run late consumers / disclosure | **MEASURED r2 steps 8/6/9/9b/10/11: 537 /296 /720 /0 /936 /1,731 s** (S8). | P; D changes to science/release policy. | F7 profile r3, preserve ordered consumption/refusal and both sensitivity bounds. Old r2 costs are not the remaining r3 savings. |
| Analysis checkpoint/resume | **ESTIMATED about 15 min reconstruction** on old dry-j basis (S8 resume report), plus unfinished step onward. | P. | Already built. Resume authenticated checkpoints after crashes; never accept stale code/input keys. Avoid a fresh 100-minute run for a transient failure when current contract permits resume. |
| B5 release verification/replay | **ESTIMATED approximately one additional heavy run** if the pinned release still replays the dry-run path; current duration not separately measured here. Independent recompute/comparator has no timed whole-run record in this audit. | P implementation; D dropping/replacing registered release replay. | F7 optimize equal work. A “digest-only release” or lean 5–8 min replacement is a policy proposal in the earlier care audit, **not adopted authority** here; excluded from savings. Keep D5/other release gates. |
| Generic `release_check.py --dry-run` | **ESTIMATED unmeasured**, provisional **1–5 min budget**, S12. Source snapshot + Git commit + capstone check + mock run + pack/verify + site/capsule. It is separate from B5 release. | P. | F6 instrument each subprocess; cache immutable source/build inputs while retaining fresh smoke/pack verification. Target **1–3 min**, low-confidence and unranked. No private-corpus regeneration implied. |
| BYTES stage 1 | **ESTIMATED unmeasured**; S1 schedules it for Nov 12, no elapsed production record located. Test fixture campaign cost **about 95.7 s/campaign** (S7) is not a production duration. | P extraction/read/fit; D stage-1 commitment/release split. | F8 time export authentication, meter parse, `load_records`, `reduce_models`, prediction freeze and commitment separately. Reuse pure authenticated parse results across boundaries; preserve held-out-key withholding and commitment. **No defensible whole-stage speed target yet.** |
| Harvest / thermal-line preparation | **MEASURED historical BYTES s4-p1 harvest 101 min**, chain 388 min (S1 item 75). v4 desk estimate about 100 min is distinct. | P harvest/software; F chain; D removing validity screens. | F1 off-Mac harvest when the owning gate allows the next arm; F7 parse once across consumers. Target **0 Mac-blocking desk min**, total compute time initially unchanged. |
| CI whole run, slow shard | **MEASURED old BYTES module 8,973 s**, S1 item 154; S7 newer medians **9,121.794 s = 2.53 h**. That module floors a module-atomic shard; setup/other tests add time. | P. | F2: merge/use hosted weights and splits, then split the heavy method. Static full-ALIGN projection below: **2.53 h → 95.7 min → 56.3 min**, before fixture improvements. |
| `tests.test_bytes_analysis` heavy test | **MEASURED 5,741.949 s heavy method +3,379.853 s remainder** (S7), 60 synthetic campaigns. | P fixture generation/CLI/repeated I/O. | F2 retain all worlds/seeds/assertions; make each world a method, then profile shared fixture construction vs arithmetic. Target **about 32 min/world**, still leaves **56.3 min** remainder floor. |
| Other BYTES/B6 test floors | **MEASURED cold_pass_fixes 4,032.784 s**, coverage_map **2,787.918 s**, h_session **1,601.667 s**, agreement **1,132.724 s** (S7). | P. | Respect shared setup/memo ownership; split independent class/method units only. Cold-pass five-method split already present in S7, largest **1,365.954 s**. Coverage-map **46.5 min** is the next indivisible floor after BYTES remainder. |
| `tests.align.test_moe_calibration` | **MEASURED 1,376.959 s** hosted S7. Brief's approximately 3,400 s is **ESTIMATED/unverified historical context**, not a reproduced observation. Four worlds × 120 seeded simulations × 200 bootstrap budget in S11. | P. | F5 distribute the four independent methods (ideal **5.74 min/method**, before unequal cost); cache invariant router structures, profile inner statistics. Keep all seeds/worlds/bootstrap draws/rate bars. |
| `tests.test_run_night` | **MEASURED 108.804 s** hosted map S7/main; no current local probe. Source has intentional real sleeping children for teardown tests and injected clocks for long-dwell tests. | P. | F5 profile methods; use readiness pipes instead of gratuitous startup sleeps, preserve real process-group/kill/timeout checks. Target **60–100 s**, tentative; not an hours-scale first priority. |
| Calibration/reducer/provenance test jobs | **MEASURED exits 820.019 s; crash-matrix 700.346 s summed split-unit medians; controller attachment 874.571 s; receipt_histsem 464.792 s** (S7). Crash sum is not a serial observation. | P with process-local witness ownership. | Keep calibration-exits exclusive; scattering its consumers repeats the full witness corpus. Existing K= 2 crash split is enough for its indivisible method. Disable detached Git maintenance in disposable fixtures (already in S7), retain provenance failures. |
| Full local suite | **ESTIMATED historical about 3.2 h** in AGENTS.md, no fresh local full run; current main map sum **16,558.178 s = 4.60 h** over 456 named weights, some absent. Full ALIGN projection **9.84 ordinary worker-hours**, before exclusive jobs and setup (ledger). Neither sum is a measured local wall. | P. | F2 use measured split map and focused loops during edits; full required merged-tree run remains. Static eight-worker floor **95.7 min** with S7 splits; local hardware can differ greatly from hosted weights. Never run full suite alongside this job. |
| Quick/touched loops | **ESTIMATED unmeasured wall**; `quick_suite.py` selects modules weighted <5 s, excluding exclusive/split modules (S10). This is a selection policy, not a 5 s whole-tier promise. | P. | F5 fast local feedback; fresh complete verification on final code candidate. Cache fixture templates, not test verdicts. No bypass of number-bearing checks. |
| Kit regeneration / pins / fixtures | **MEASURED historical whole seat build about 9 min, review about 7 min** (S13); **ESTIMATED generator-only unmeasured**. S3 generator reads frozen Git blobs and inputs, never model directories. | P; D changes to seeds/rosters/identity. | F6 cache `git show` blobs by commit/path, render deterministically, write changed bytes only; rerun `--check`. Target **<1 min generator +<2 min check**, budget only; do not claim 9-minute generator baseline. |
| Clone/venv/config correctness / native gates | **ESTIMATED unmeasured** setup and native parity wall. Historical R0 first run failed after **MEASURED 20.8 s** because interpreter-path resolution lost its venv (S4). | P; F native execution for parity. | Ahead-of-time exact invocation/import/identity preflight, offline locked environment reuse, no model downloads. Metal tests stay lead-owned outside sandbox; fixtures cannot certify native state. |
| Magistrate activation / wakeup | **ESTIMATED poll delay 0–300 s**, mean 150 s only for uniform completion phase; 300 s watchdog interval and backoff in S12. Activation/coordination wall has no aggregate observation. | P. | F9 event-trigger one short finalization/arm checklist after terminal proof, retain watchdog fallback and every fence. Target **0–30 s wake latency**, not continuous agent presence during measurement. |
| Review workflows / re-gating | **MEASURED example 7 min kit executing review**, S13; **ESTIMATED end-to-end queue/review wall unmeasured**. Review cost is not a fixed round count. | P scheduling; D science/irreversible cold gate requirements. | F1/F6 review off-Mac; assemble exact-commit packet once, run independent lenses concurrently elsewhere, one disposition record. Preserve final lead verification and required cold science gate. No weekly credit for deleting gates. |
| Optional Flash-Next provisioning/parity | **ESTIMATED 7–20 h after download begins**, S1 item 198; no measured inventory in this audit. Separate future phase under Amendment 1. | P conversion/provisioning; F fixed numerical reference work; D stack/model choice. | Prequalify tooling/configs off-Mac. No weights downloaded, no port/parity run, and no benefit counted in the v4 ranking. |

## What the cheap scheduling probe establishes

The [evidence ledger](latency-audit-sol2-evidence.json) was generated by reading
Git objects and JSON only. No test module, measurement backend, model, custody
root, or analysis driver was imported. Probe wall: **MEASURED 0.295 s**. `nice -n
10` was requested; the sandbox reported `setpriority: Operation not permitted`
but executed the subsecond probe. No successful priority change is claimed.

The projection discovers test filenames/packages in S3's tracked Git tree,
uses S7 hosted weights, removes its two exclusive modules, and greedily assigns
units in descending weight to the lightest of twelve bins. Unknown modules get
26.98 s each. Four modules lack observations: external-volume, two new R0
load-reference modules, and SSD qualification. Their cost is uncertain.

| Static schedule, same 571-module tree | ESTIMATED slowest ordinary shard | Interpretation |
|---|---:|---|
| Module-atomic | 9,121.794 s (152.0 min)| BYTES whole module dominates. |
| S7 declared splits | 5,741.949 s (95.7 min)| Heavy BYTES method dominates. |
| Also split that method into three equal-cost world methods | 3,379.853 s (56.3 min)| BYTES remainder dominates; equal world cost is an assumption. |

Total ordinary weight is **35,409.860 s**, so even perfect twelve-way packing
cannot beat **49.18 min** without reducing actual work or increasing runners.
The 23.4-minute main-only projection in S7's report does not apply to the full
ALIGN/BYTES tree. Setup, queue delays, fixture duplication, memory/I/O contention,
exclusive jobs, failures and newly measured modules can increase all projections.
Python 3.11 and 3.13 must retain the intended checks; current workflow uses 3.13
for ordinary shards and 3.11 for fences. No interpreter coverage is removed.

For R1, the ledger independently expands the source formulas with
`member = 1750 +1.13544*1580 +120 = 3663.9952 s`. The nine grouped phase rows sum
to 56,206.9616 s; adding 5,400 s and the 29,055.9808 s R6-2 retry allowance
reproduces S1 item 202's rounded 56,207 /61,607 /90,663 s. This establishes that
the large budget follows the phase table. It does **not** establish that all
caps are reached, or bound calibration, harvest, and every contention redo.

## Ranked fixes

Planning assumptions for comparison, **not observed weekly frequencies**:
six windows/desks, ten full CI candidates, three local full-suite candidates,
one R0 and one R1 per week during active development. Ease: 3 = small existing
tooling/operational change, 2 = bounded implementation with meaningful tests,
1 = wider work or hardware/design gate. Score = saved hours/week × ease.
Savings refer to the named resource; overlapping rows are not a portfolio sum.

| Rank / fix | Expected result, evidence and exact work | Hours/week × ease = score |
|---|---|---:|
| 1 **F1: remove desks/reviews from measurement-Mac turnaround** | About 100 min desk → **0 Mac-critical-path min**, initially unchanged compute elsewhere. Apply S1 item 213's already authorized split: terminal immutable record, local required checks, physical recovery/dwell; laptop does desk/review/kit. Target 30–45 min turnaround is an **estimate** awaiting timestamps. Never arm across an unresolved gate that actually depends on the desk. | 6 × 100/60 = **10.0 Mac h** × 3 = **30.0** |
| 2 **F2: measured CI map, then BYTES world split** | First use S7's existing five CI commits without landing unrelated B5 changes; resolve `awaiting_lane` only when its module arrives. Verify every test exactly once and isolated methods' fixture ownership. 9,121.794 → 5,741.949 s gives 56.33 min/run; three world methods project 3,379.853 s. Preserve the complete 60-campaign statistical aggregation and all per-world rate assertions. | First stage 10 × 3379.845/3600 = **9.39 CI h** × 3 = **28.17**; second stage adds **6.56 CI h** × 2 = **13.12**, dependent on stage 1, not counted twice. |
| 3 **F3: incremental custody + bounded hash/copy pipeline** | Scenario **30 → 10 min/turnaround**, not a measured baseline. Target 2–4 hash workers on immutable closed files, ordered manifests and bounded I/O; compress/copy each closed archive once, independently read/hash destination once. Keep server-confirmed cloud copy plus independent second copy before deletion (S1 item 170). Measure cold/hot hash, copy and final verification separately; parallel hashes on one SSD may lose. | Scenario 6 × 20/60 = **2.0 Mac h** × 2 = **4.0**; low confidence; overlaps F1's turnaround target. |
| 4 **F5: test fixture and simulation profiling** | Start BYTES coverage-map/remainder and MoE, then run-night. Target **20–30% less ordinary work** as a hypothesis: 9.84 worker-hours → 6.89–7.87, with all worlds/seeds/draws unchanged. Build immutable fixture templates once per owner, copy into private per-test roots, never share mutable outputs. MoE's four independent world methods can be separate units; keep ordered statistical aggregation. | Conditional after profiling: 10 × (49.18 min × 20–30%)/60 = **1.64–2.46 ideal CI h** × 2 = **3.28–4.92**; distinct from packing gain, not guaranteed wall reduction. |
| 5 **F6: deterministic kit/source-snapshot caching and ahead-of-time review packets** | Target generator <1 min + check <2 min; cache only exact commit/input/artifact digests, including generator and pinned inputs, flags and environment. `--check` regenerates/recompares canonical bytes; no cached GO, census, disk or live sensor state. For a hypothetical 10 min kit/check → 3 min, six cycles save 42 min; S13 does not measure that baseline. | Scenario **0.70 engineering h** × 2 = **1.40**, low confidence. |
| 6 **F9: terminal-event wakeup with mechanical activation** | 300 s poll → 0–30 s event wake; retain 300 s fallback, STOP/owner rules, terminal proof and admission census. No new polling agent runs during a window. Mean 150 → 15 s saving is a uniform-phase assumption. | 6 × 135/3600 = **0.225 Mac h** × 3 = **0.675** |
| 7 **F4: exact R0 evidence reuse after unrelated failures** | On older reruns 4–7, about 12.2 min memory stress plus about 2–3 min early checks preceded SMC each time (S4). SMC-first and R0-L3 already remove much of that amplification. For future source-only fixes, let the lead admit composition only when code/config/model/stack and evidence remain bound exactly; otherwise rerun. Target avoid **15–20 min** repeated work per such event, not a faster decode. | Assumed one avoidable event/week **0.25–0.33 Mac h** × 2 = **0.50–0.66**; **zero** if already prevented. |
| 8 **F7: next analysis/release optimization under D-188** | Profile r3, then deduplicate authenticated parsing/refits and parallel pure preparation with ordered consumption. S8's synthetic 401 s and measured 100 min r3 establish precedent; they do not establish a remaining factor. Planning target **100 → 80–90 min/run**, with exact comparator agreement, is unverified. For two analysis/release executions/week, conditional saving 20–40 min. | Scenario **0.33–0.67 analysis h** × 1 = **0.33–0.67**. No credit for removing registered replay or moving real data. |
| 9 **F8: phase receipts before promising R1/BYTES-stage 1 speedups** | Report load/warmup/decode/G0/G1/H/precool/serialize/hash/parse/fit separately, with CPU, bytes/files and retry reason. Use existing S5 phase fields and S8 timing patterns; expose structure-only public timing, numeric study values stay sealed. Target timing overhead<1%, to be verified on synthetic runs. No fabricated wall saving. | **0 credited h**, prerequisite to a defensible R1/stage 1 target. |

The full-local-suite effect of F2 is also useful but not independently added to
the score: S7 split weights project 95.7 min on eight workers before setup;
splitting the heavy BYTES method removes that floor, but local throughput and
fixture contention must be timed. Do not use hosted sums to claim a measured
local saving.

## Overlap and design boundaries

**Safe overlap:** while a window measures on the dedicated Mac, other machines
can review code/records, regenerate kits from frozen inputs, and analyze copies
already authorized and transferred under custody. No background Mac hashing,
compression, offload daemon, suite or magistrate is added to that window.

**Offload overlap is conditional.** The measurement Mac still has to read and
transmit bytes, and the current rule prohibits mounted external volumes during
measurement. Complete local transfer/eject before the next dwell. A remote
machine may independently verify a complete copy while the next window runs
only if local retained copies/free space satisfy the arm gate and no required
verification/release decision is pending. Do not delete local evidence until
all existing custody requirements pass. Even a qualified always-attached SSD
would permit option B's sleeping presence, not background writes. S1 item 212's
KM003C/DC-in direction makes the older SSD GPU-only argument insufficient;
lead must reconcile the measurement boundary before adopting any amendment.

**Thermal improvement is physical configuration work.** Lid open, stand,
clearance and fixed room setpoint are already specified. The optional cooler
starts off and R1 decides use for the whole series. An ad hoc cooler, changing
power mode, or shortening post-D idle changes predecessor state and can change
the measured number. Faster settling may improve throughput only after the
same band/slope/sample conditions and the owning setup rule are met.

**Adaptive waits mostly already exist.** R0 adaptive idle, R1 precool-to-band,
G0/G1/H release conditions and conditional long-decode retry are installed.
Fixed 300 s baselines, 1,800 s soak, 900/600 s sensor profile and SSD blocks/gaps
are observation/design requirements. Removing them, widening bands beyond
predeclared tuning, altering seeds/rosters/token budgets, reducing bootstrap
draws, changing the estimator or skipping independent verification is D work.
No such change is proposed as an engineering saving.

**Review remains independent.** D-186 and orchestration already say pre-arm
triple audit runs per frozen code/protocol change, not per unchanged window;
ordinary harvest is raw-byte validation plus independent arithmetic. Reusing
that approved gate placement and moving reviews off-Mac is a process saving.
This audit does not authorize fewer science gates, self-review as independence,
or cached final verification on a different commit.

## Handoff and unresolved measurements

Delivered documentation and a source-metadata ledger only. No production code,
study data, model weights, coordination state or running job changed; no
network, full suite, B5 pipeline, native MLX or quiet capture was run. No
scientific gate is closed by this report.

Next exact work: lead selects F1/F2, records actual recurring frequencies, and
obtains per-stage timings at the next already authorized boundary. F2's test
change needs isolated-method coverage and unchanged campaign aggregate
assertions on Python 3.11/3.13, then hosted final-head timing. F3 needs synthetic
destination corruption/interruption tests before any real custody use. Lead
owns all final checks and prospective design decisions.

Outside this sandbox, after the current job ends and under an appropriate
lead-controlled session, retain the relevant native gates:
`tests.align.test_r0_mlx_native`, `tests.align.test_thermal_mlx`, and
`tests.align.test_cache_checkpoint_native` on the exact pinned Metal stack;
native suites must skip when MLX is unavailable. No new MLX code/tests were
written here. A fixture pass does not validate hardware, holds or token parity.

Missing evidence: complete successful latest R0, actual integrated R1 phase
times, completed v4 chain/turnaround, hash/compress/copy throughput, production
BYTES-stage 1 and independent release-check wall, generator-only time, current
full-local-suite wall, and end-to-end review queue time. The brief's 7,500 s
BYTES / 3,400 s MoE figures are not substituted for sourced observations.
Ranking uses the conservative end of projected ranges and is conditional on
frequency/resource assumptions; targets are not measured
speedups. Source revisions are frozen in the ledger so later branch movement
does not silently change this audit.
