# JouleWise latency audit — independent Sol seat 1

Audit date: 2026-11-08 UTC. Task: `latency-audit-sol1`. Base:
`4e7e878a151d919faf56bb9131af1fcca4b7be75`. This is a source and historical-record
audit, not a measurement campaign or an implementation. No Block-5 outcomes,
real measurement files, other latency-audit seat's branch, model weights, or
network services were accessed. Absolute data paths in source documents were
treated as text. Coordination state is lead-owned and unchanged.

The largest recurring software opportunities are **CI's indivisible simulation
tests and the roughly 100-minute terminal desk/harvest**. R0's repeated failures
also consumed substantial calendar time, but several remedies already exist.
There is no evidence that a valid 16.5-hour measurement window can generally be
reduced to five hours by software work. In particular, **R1's roughly 16 hours
is a worst-case budget, not an observed duration**, and the SSD's 6.83 hours is
a planned schedule. Treating either as a measured bottleneck would misrank work.

## Evidence and interpretation

- **MEASURED** means a reported elapsed duration or recorded test timing, with
  its source below. It does not mean this seat re-ran it. Rounded narrative
  timings and hosted medians retain that qualification.
- **ESTIMATED** covers schedule arithmetic, caps, forecasts, historical guidance
  without a timing log, and proposed targets. An unmeasured component is marked
  explicitly; its planning allowance is not evidence of time actually spent.
- **PHYSICS-BOUND** covers decode, thermal recovery and acquisition time required
  by the current experiment. **DESIGN-BOUND** covers registered counts, fixed
  schedules, ordering and acceptance rules whose reduction requires a prospective
  ruling. **PROCESS-BOUND** covers parsing, hashing, compression, repeated
  derivation, scheduling, software polling and engineering workflow. A row can
  contain more than one class; its components are distinguished.
- Window maxima, programmed chain time, desk time, CPU-seconds and elapsed time
  are different quantities. Parent totals and their child phases must not be
  added together. CI module medians from different runs are scheduling weights,
  not a measured whole-suite wall time. Synthetic timings never establish live
  performance or hardware validity.

The companion [evidence file](LATENCY-AUDIT-sol1-evidence.json) contains fixed
source revisions, extracted timing weights, pure R1 schedule arithmetic, the SSD
decomposition and CI packing projections. The probe compiled only selected pure
scheduling functions from Git source, with literal configuration values; it did
not import the R1 runtime, tests, MLX or data readers.

## Inventory: measurement and turnaround

| ID / recurring step | Duration and evidence | Time class | Concrete opportunity / limit |
|---|---|---|---|
| M01 R0 complete desk qualification | **ESTIMATED 3–4 h**, current launch allowance [S01, items 205/208/211]. The original 5–6 h multi-model estimate [S02 §2.8] is superseded by Amendment 1's D-only roster. No successful complete R0 elapsed record was found in the inspected refs. | PHYSICS-BOUND model work; DESIGN-BOUND checks; PROCESS-BOUND repeated work | Instrument each check before promising a new clean-run wall. Target **ESTIMATED 2–3 h** only if non-decode overhead proves material; use the retry-specific target in fix 3. |
| M02 R0 launch/display preparation | **ESTIMATED fixed 300 s** dwell after display sleep, plus unmeasured launch/exit latency [S01 items 209/211; S03]. | DESIGN-BOUND required dwell; PROCESS-BOUND launch | Already installed by #700. A production dwell below 300 s is explicitly inadmissible. Keep it; do not mistake a test-only override for an optimisation. |
| M03 R0 SMC enumeration/step | **ESTIMATED 1,800–2,700 s capture**: idle 300 up to 1,200, load 900, recovery 600. Execution budget adds 600 s, hence **3,300 s** maximum [S04 config; `r0_host.step_budget`]. | PHYSICS-BOUND thermal identification; DESIGN-BOUND profile | Amendment 2 replaced the old 60 s load because it cannot identify a slow time constant up to 300 s. Adaptive idle settling already exists. Reclassification of an authenticated existing journal is offline work, not a new capture [S01 item 196]. |
| M04 R0 host, pins, disk and model load | **MEASURED 20.8 s** early launcher failure (item 178); **75.5 s** early coherence failure (item 180), both partial runs [S01]. Component wall otherwise unmeasured; **ESTIMATED 1–10 min** allowance for local checks/hashes, excluding model acquisition. | PROCESS-BOUND, with model-load I/O | Fix interpreter/symlink errors before hardware reservation; hash independent files with bounded concurrency. Neither partial-run wall is the healthy-path duration. No downloads are proposed here. |
| M05 R0 coherence, template, generated rewrite and peak-memory checks | Individual wall unmeasured; **ESTIMATED 5–20 min** allowance, excluding ladder/long decode. Re-run 6 had **MEASURED 949.8 s** outside its 1,520 s SMC failure; that residual includes other checks/overhead, not a profile [S05]. | PHYSICS-BOUND inference; PROCESS-BOUND repeated loading/checks; DESIGN-BOUND bars | Runner already retains a loaded backend across checks [S04 `r0_runner.execute`]. Reuse immutable authenticated check results only under an explicit same-stack/config rule, preserving each bar. |
| M06 R0 effort ladder | **ESTIMATED count-derived budget**: up to 3 rungs × 2 task pairs × at most 6 turns × 4,096 decode tokens; actual wall not recorded separately [S04 `r0.ladder`, `screen_episode`]. | PHYSICS-BOUND decode; DESIGN-BOUND pair/rung/cap policy | Early exit after the first passing rung already exists. Reducing pairs, turns or changing rung order is a design change. Profile per rung and retain failed-rung evidence. |
| M07 R0 long-decode/native cache qualification | Individual wall unmeasured; part of M01. **ESTIMATED one probe, at most one metadata-evaluation retry** [S04 `r0.long_decode`]. | PHYSICS-BOUND decode; DESIGN-BOUND native exactness; PROCESS-BOUND avoidable reruns | Retry only the failed probe, as already coded. Cache exactness evidence must bind the native stack/model/implementation; a synthetic pass is insufficient. |
| M08 R0 failure/relaunch/review cycle | **MEASURED failed walls 2,469.8 s, 92 s, 987 s** for re-runs 6/9/10 [S05]; **sum 59.15 min**, not the total eleven-attempt cost. Scheduling/review gaps add calendar time but are not all active work. | PROCESS-BOUND orchestration/repetition; DESIGN-BOUND refusal policy | #692 moved SMC ahead of disk hashes/model work; #699/#700 add R0-L3 contention recording, one redo and display sleep. These are existing changes, not new savings. Do not reintroduce retired clean-gap scheduling [S01 items 205/208/209]. |
| M09 R1 whole rehearsal | **ESTIMATED 56,206.96 s = 15.61 h** no-redo all-caps bound; **61,606.96 s = 17.11 h** with one batch wait; **90,662.94 s = 25.18 h** with the listed G0 retries and wait [S06; reproduced]. Calibration brackets and harvest are **excluded**; quiet-load redos can add more. Earlier Amendment 1's 2.5–3 h is not the integrated bound. No live completed R1 wall found. | PHYSICS-BOUND decode/recovery; DESIGN-BOUND phase table; PROCESS-BOUND startup/custody | Record actual phase occupancy before optimising the bound. **ESTIMATED 4–8 h** is an investigation target for an ordinary no-retry run, not a supported forecast. Never shrink the reservation to this target. |
| M10 R1 pre/post calibration brackets | Wall **unmeasured**; **ESTIMATED 10–30 min combined planning allowance**, low confidence. The bound function gives them zero specifically because it does not bound them [S06]. | PHYSICS-BOUND acquisition; DESIGN-BOUND bracketing; PROCESS-BOUND derivation | Time capture and derivation separately; memo only authenticated deterministic computation. Do not remove either bracket. |
| M11 R1 idle soak | **ESTIMATED fixed 1,800 s**, with final 1,200 s defining R; slope/load retries may repeat it [S06]. | PHYSICS-BOUND settling; DESIGN-BOUND SD/reference sample | Keep the registered 30 minutes. An adaptive shorter SD/reference estimator needs a prospective design, so no banked saving. |
| M12 R1 30B/D planning steps | **ESTIMATED bounds 5,164 s / 5,764 s**, each includes re-armed member allowance, G0, quiet and recovery, not just decode [S06; evidence file]. Step deadman 1,580 s; prefill 10k + 4,096 seeded decode. | PHYSICS-BOUND decode/recovery; DESIGN-BOUND stimulus | Maintain full planning workload. Break out startup, G0, prefill, decode, recovery and close. The fixed **600 s recovery** supplies classifier evidence; it is not an arbitrary sleep. |
| M13 R1 High Power A–B–A | **ESTIMATED 3 × 4,328.995 s = 3.61 h all-caps**; each leg includes a 665 s release bound and conservative member allowance [S06]. | PHYSICS-BOUND thermal response; DESIGN-BOUND lever comparison | The cooler/High Power lever requires ≥25% longer decline time; do not collapse A–B–A or change modes mid-series. The upper allowance uses I_D = 1,750 s before D's I_D is known; it is not a measured startup cost. |
| M14 R1 precools, post-D cooldown, designed R+4/+2/+0 starts | **ESTIMATED four cool-to-band caps × 1,500 s = 1.67 h**; **3 × 5,763.995 s = 4.80 h** designed-start bounds [S06]. Additional preheat up to 900 s is inside each designed-start bound. | PHYSICS-BOUND recovery; DESIGN-BOUND start states | Cool-to-band is already adaptive. Preserve the common R, warmest-first order and bounded retry. Do not add an extra cool-to-band between gated D members: that would destroy the W1 predecessor-heat test. |
| M15 R1 gated bank, spam replay pair, X-G; optional 4-bit | **ESTIMATED 4 × 1,800 s = 2 h** bounds for the mandatory members; optional 4-bit adds **1,800 s** to this bound model [S06]. | PHYSICS-BOUND inference; DESIGN-BOUND pair/duty/identity checks | Preserve bank-before-replay order and W1's configured idle. A 4-bit model or different prompt is not an equivalent speed optimisation; it needs its own qualification/ruling. |
| M16 R1 OS batch waits and redos | **ESTIMATED up to 5,400 s** for one 11:45–13:15 wait; rejected heavy segments add release + segment (up to two load redos), and calibration G0 retries add **29,055.98 s** in aggregate [S06]. | PROCESS-BOUND admission scheduling; DESIGN-BOUND load/redo rule | Schedule using phase-specific bounds and journal actual wait. A shorter proof of remaining segment work can reduce conservative scheduling slack only if approved; retain load observations and all rejected attempts. R0-L3 does not authorise weakening R1's rule. |
| M17 v4 window W1 / D-series | **ESTIMATED W1 chain 26,927 s (7.48 h), max 44,640 s (12.4 h)** after Amendment 1; D chain **40,527 s (11.26 h), max 58,260 s (16.18 h)** in original §2.7, under allowed **59,520 s (16.53 h)** ceiling [S02, S01 item 204]. R1/R10 and registration-grade scope still supersede planning inputs. | PHYSICS-BOUND inference; DESIGN-BOUND roster/replication/window span | Distinguish productive chain from contingency reservation. Three long D windows instead of six shorter ones already halves arm count; do not count it again. Confirmatory replication remains owed. |
| M18 observed predecessor pilot/B6/BYTES chain | **MEASURED pilot 4 23,567 s (6.55 h); pilot 10 6 h 31 m 41 s** [S07]. **MEASURED B6 chain 313 min** and BYTES 388/316 min [S01 items 49/75/76]. | PHYSICS-BOUND inference; DESIGN-BOUND prior rosters | Useful cadence evidence, not a v4-D speed prediction: models, rosters, gates and power policy differ. |
| M19 per-member process start, model load, idle, warmup | **ESTIMATED member law 516.575 + 1.13544 × episode_s**, scaffold 4,995 s [S02 §1.0]; **300 s configured idle/member** is explicit [S08]. W1's 18 planned ALIGN members alone contain **5,400 s (1.5 h)** configured idle, not all scaffold members. Warmup/load wall separately unmeasured. | PROCESS-BOUND start/load; PHYSICS-BOUND recovery; DESIGN-BOUND fixed idle/neutral warmup/fresh process | Profile I_D. Keep fresh-process and identical neutral-warmup semantics. Replacing idle with G0, keeping models resident across members, or removing warmup needs design review; no automatic 1.5 h saving. |
| M20 G0/G1 and in-turn holds | **ESTIMATED caps**: original W1 G0 600 s (R1 G0 1,200 s); G1/H min(300 s, 3×R1 p95 recovery), five consecutive 1 Hz releases [S02 §2.6; S06]. D's W1 cap is subsequently budget-sized by R10 [S01 item 203]. Actual wait distribution unavailable. | PHYSICS-BOUND cooling; DESIGN-BOUND release/reference/timeout rules | They already release adaptively. S6's predeclared median ≤90 s tuning, capped at δ_slow ≤2°C in the integrated fallback, is the authorised route. Do not replace failure with proceed or ratchet the reference. |
| M21 episode token budget/deadman, timeout cleanup | **ESTIMATED member cap 1,800 s** after wait budget spent, 3,300 s while unspent; T_dead derived from I_D, tail and 1.13544 factor [S02; S04 kit]. Cleanup has bounded grace/census intervals, not hours. | PHYSICS-BOUND decode; DESIGN-BOUND budget; PROCESS-BOUND cleanup | A cap is not a sleep. Reducing tokens, truncating the final turn, changing model precision or raising a deadline changes the qualified design. Preserve stop, custody and host-power restore semantics. |
| M22 record finalise, file census, hash, pin, compression | Individual **unmeasured**. **ESTIMATED 5–20 min** planning allowance, excluding harvest and transfer, low confidence. Serial per-file hashes exist in `b5.driver.checkout_snapshot`; R0 offload inventory streams 8 MiB chunks [S09/S04]. | PROCESS-BOUND | Immutable per-file digests, bounded file parallelism, deterministic ordered manifests and compression workers; hash final closed bytes. Instrument before claiming a saving. Online counting/journal processing already exists; do not infer all finalisation is deferred. |
| M23 terminal desk/harvest/inspection | **MEASURED ALIGN pilot 4 103 min; pilot 10 98 min** [S07]. **MEASURED prior B6 harvest 88 min; BYTES harvest 89–109 min**, with recorded desk totals **114/117 min** on two sessions [S01 items 49/75/76/105/123]. Totals overlap; do not add harvest to desk again. | PROCESS-BOUND derivation, validation, compression and orchestration | `align_pilot_session.desk` extracts member summaries serially, then invokes harvest; v4 delegates to it [S10]. Target **ESTIMATED 30–45 min**, conditional on a stage profile and ordered-output equivalence; strongest recurring turnaround investigation. |
| M24 custody/offload and destination verification | Standalone transfer/hash wall **unmeasured**. **ESTIMATED 10–60 min** desk allowance, highly storage-dependent. W1 planning footprint **18.71 GB/copy**, D **26.45 GB/copy** [S02/S04]. | PROCESS-BOUND I/O/hashing; DESIGN-BOUND custody/evidence rules | Parallel file hashes or incremental manifests may help; APFS/cache or CPU contention may make them worse. Keep destination re-read before deletion. `backup_runs.sh` is rsync plus a log, not a cryptographic verification receipt [S09]. |
| M25 between-window cooling, battery float, pre-arm checks and quiet dwell | Actual individual walls **unmeasured**; **ESTIMATED 10–60+ min** recovery/prepare allowance. Existing driver routes require **600 s continuous clean dwell**; a qualification route budgets **2,700 s** to obtain it [S11]. Applies by plan class, not to every workflow universally. | PHYSICS-BOUND thermal/battery recovery; DESIGN-BOUND dwell/admission; PROCESS-BOUND duplicate checks | Recover with lid open on the specified stand; optional cooler only under §3.1's qualification. Prepare static materials off-host/in advance. Finish CPU/disk work, eject drives and clear agents before counting clean dwell. |
| M26 post-window scheduling/calendar gap | **ESTIMATED** cadence in item 213: 1.2–1.3 windows/day instead of one; v4 programme 11–13 vs 14–16 days [S01]. This is a schedule forecast, not a measured optimisation. | PROCESS-BOUND scheduling; PHYSICS-BOUND recovery | Back-to-back windows are already policy [S12]. Overlap desk-side paperwork with recovery; overlapping on-Mac hashing/offload with acquisition or qualifying dwell remains disallowed. |
| M27 SSD qualification | **ESTIMATED 125 segments / 24,600 s = 6.833 h**: five 600 s settles, 60×120 s idle, 60×120 s decode guesses, 120×60 s gaps [S13; reproduced]. Fixed-work decode and plug/unplug response can extend it. | PHYSICS-BOUND capture/recovery; DESIGN-BOUND five-block paired design; PROCESS-BOUND operator handoffs | Two hours of 60 s gaps is an investigation target, not two hours of waste. A–D–A–D–A gives residual df for presence/drift; the old three-block/4.7 h plan is inadequate. Ed present; no overlap with R0/R1/windows. |

## Inventory: analysis, release and engineering

| ID / recurring step | Duration and evidence | Time class | Concrete opportunity / limit |
|---|---|---|---|
| A01 heavy blind dry run / reference run | **MEASURED narrative ~37 h r1 → 1 h 40 min r3** [S01 item 197]. Intermediate **27.1 h** attempt E and **1 h 46 min** dry-h candidate have different load and failure patterns [S01 item 165]. | PROCESS-BOUND | Already achieved under D-188. Do not credit 35 h again as future weekly saving. No run of this pipeline is authorised in this seat. |
| A02 dry-run stages 0/1/2/3/3b/4/5/8/6/9/9b/10/11 | **MEASURED r2 dry-j seconds**: 85/901/13/0/1,658/842/1,426/537/296/720/0/936/1,731 = **9,145 s** [S14 §5]. Order is the driver's dependency order. | PROCESS-BOUND census, validation, parse, brackets, mint, analysis, claims, sidecar, reported pass and sensitivity/disclosure | Zero means rounded/no observed work on that path, not guaranteed free. Repeated authentication and refits were demonstrated hotspots; preserve ordered refusal identity/position and frozen numerical semantics. These r2 stages are not r3's measured stage profile. |
| A03 synthetic full-chain equivalence/profile loop | **MEASURED 903 s r2 → 401 s fix**, 10 workers on M4 Air; profiled robust run 964 s [S15]. Wrong prefetch refitted 153 candidates vs 12 needed; corrected 3b **408.7 → 37.3 s**. | PROCESS-BOUND | Reuse this style of full-chain comparison. Microbenchmarks missed the bad prefetch. Do not extrapolate tiny synthetic traces as real-data throughput. |
| A04 release check, stage (a) digest verification | Standalone live wall **unmeasured**. **ESTIMATED tens of seconds–several minutes**, conditional on bytes/storage. Already thread-pooled for input census; output digest loop serial [S16]. | PROCESS-BOUND | Parallel hashing is partly implemented. Benchmark worker counts against actual storage later; preserve no-follow checks, canonical failure order and required complete re-read. No mtime-only trust cache. |
| A05 release stage (b) independent recompute | **MEASURED synthetic ~9 s** and fixture parse **5.78 MB / 0.549 CPU-s** in care audit. **ESTIMATED live 5–8 min** at ten workers, explicitly a projection [S17 §2.3]. | PROCESS-BOUND parsing/integration | Ten-process member pool already exists [S16]. Stream/parse once per authenticated trace; no estimator weakening. Validating agreement remains mandatory. |
| A06 release stage (c) comparator / release decision | Standalone wall **unmeasured; ESTIMATED <1–5 min** allowance. Comparator reports match/hold and structural counts only [S16]. | PROCESS-BOUND computation; DESIGN-BOUND release and unsealing authority | Keep independent implementations and bars fixed. A fast `hold` is not a successful release. Unsealing is a separate Ed decision. |
| A07 public software release smoke (`release_check.py`) | **Unmeasured; ESTIMATED 1–5 min**, low confidence [S18]. Includes clean tracked snapshot, mock bundle, validation/reduction, pack/site/capsule seams. Distinct from A04–A06. | PROCESS-BOUND | Cache deterministic build inputs, not a previous pass verdict; retain a fresh smoke. Script not executed in this audit. |
| A08 BYTES stage-1 preparation/export | **ESTIMATED 5 min** checkout/self-test, **5–20 min × 12 sessions = 1–4 h exports**, thermal lines **~10 min**, from runbook estimates [S19 §§3.1/3.4/3.6]. Synthetic driver self-test **MEASURED ~1 min /16 tests** there. | PROCESS-BOUND archive restore, auth, export, line generation | Profile and split read/auth preparation from ordered publication. The twelve-session loop is serial; exporter shares key/withheld stores, so naive concurrent exporters are unsafe. Avoid duplicate restore/parse without changing export semantics. |
| A09 BYTES blinded agreement → no-key refusal controls → fit release → dual fit → comparison → prediction commitment | **ESTIMATED one to a few hours** for run command, not measured live; code uses serial subprocesses [S19 §§1/3.8; S20]. Export time above may make the whole operator visit longer than the narrative overall estimate. | PROCESS-BOUND computation; DESIGN-BOUND blinding/commit barriers | Main/twin can be profiled separately and potentially computed ahead on identical authorised inputs; consume/check in registered order. Never release held-out rows/keys, pre-commit clocks or stage 2 early. Estimator digest and run branch remain pinned. |
| A10 BYTES held-out agreement and stage 2 | **ESTIMATED agreement similar to stage-1 run**; stage-2 wall **unmeasured** [S19 §4]. | PROCESS-BOUND computation; DESIGN-BOUND release sequence | Only after prediction commitment and the required agreement. No part was run here; no assumed stage-1 speedup licenses earlier release. |
| E01 hosted CI full code-change matrix | **MEASURED BYTES module 9,121.794 s (2.534 h) median**, complete module observations 9,130.964/9,112.624 s on named hosted runs [S21]. This dominates a shard; it is not a measured aggregate for today's main. CI is 12 ordinary shards plus exclusive jobs [S22]. | PROCESS-BOUND fixtures, simulation and packing | Pending timing lane lowers the largest declared unit to **5,741.949 s (95.7 min)**. More shards cannot beat it. Split/reuse fixtures and independent campaigns without dropping cases. Target **ESTIMATED 55–65 min** on the larger lane tree, subject to new timings. |
| E02 `tests.test_bytes_analysis` campaign method / remainder | **MEASURED 5,741.949 s method + 3,379.853 s remainder**, hosted medians [S21]. Method runs **60 full synthetic campaigns** (20/world × 3), not a sleep. User brief's ~7,500 s is an older approximation; inspected completed runs support ~9,122 s. | PROCESS-BOUND serial campaigns/repeated construction; DESIGN-BOUND empirical test coverage | Make independently seeded campaigns schedulable, aggregate all 20/world before rate assertions. Keep class-shared fixture consumers together or persist deterministic read-only fixtures. Full-module seconds are not saved runner-seconds just by splitting. |
| E03 `tests.align.test_moe_calibration` | **MEASURED 1,376.959 s** hosted weight in timing lane; integrated R1 lane has **1,451.183 s** weight [S21/S04 maps]. Brief's ~3,400 s could not be substantiated from inspected records. | PROCESS-BOUND synthetic statistics; DESIGN-BOUND 120 worlds × 200 bootstrap budget | Four test methods each run 120 worlds [S23]. Split independent worlds/seeds or reuse deterministic generated logs; preserve all worlds, resamples, seed mapping and final binomial assertions. **ESTIMATED 6–12 min** module critical-path target with four units; runner work may not fall. |
| E04 `tests.test_run_night` | **MEASURED 108.804 s** historical hosted weight, not a current re-run [S21]. Source includes child/grandchild sleeping fixtures and actual subprocess timeout tests [S24]. | PROCESS-BOUND real-clock fixture time | Inject fake clocks into logic tests; retain a small real process/signal/timeout sentinel. **ESTIMATED 30–60 s** target, unprofiled. Two `sleep(60)` lines do not prove two minutes are paid: correct timeout tests kill those children. |
| E05 other slow test families | **MEASURED hosted weights**: `b6.test_cold_pass_fixes` 4,032.784 s (already split in pending lane), `test_bytes_coverage_map` 2,787.918 s, `test_bytes_h_session` 1,601.667 s, `test_bytes_agreement` 1,132.724 s; exclusive calibration exits 820.019 s and crash-matrix sum 700.346 s [S21]. | PROCESS-BOUND fixtures and replay | Profile these after BYTES' dominant method. Source-replay alone **MEASURED 2,665.339 s** in one synthetic shard report [S25]; differing host/tree invalidates direct hosted comparisons. Keep crash/kill sentinels and all discovery coverage. |
| E06 full local suite | **ESTIMATED historical guidance ~3.2 h sequential**, AGENTS.md; no current comparable local full-suite wall found or run. CI-weight projection for R1 lane is **36,030.4 ordinary runner-seconds**, not a local runtime observation [S26]. | PROCESS-BOUND test work/contention | Use sanctioned shards in a later host-controlled session. Local 8-worker packing estimate with pending split **95.7 min**, before host contention/setup; 12-way also **95.7 min** because one method dominates. Avoid competing with live analysis/measurement. |
| E07 targeted/quick feedback and isolation repair | This audit **MEASURED 3 shard-runner tests in 0.005 s**, not suite coverage. Earlier synthetic report runs range from milliseconds to tens of minutes [S25]. | PROCESS-BOUND selection/isolation | Focused tests first, full required candidate verification once when ready. Keep final merged-tree requirements. Repair MLX test contamination rather than re-running an entire slow suite for an import-order defect [S01 item 176]. |
| E08 kit regeneration / `--check` / readiness | Wall **unmeasured; ESTIMATED 1–10 min** generation/check allowance, low confidence. Generator rebuilds `build_files`, then writes or compares every output [S04 `align_v4_kit.generate`]. | PROCESS-BOUND generation; DESIGN-BOUND readiness | Cache canonical generated bytes by complete input/source digest, avoid unchanged writes; still execute readiness and verify committed outputs. R1-filled leaves and pending/native gates invalidate the relevant cache. **ESTIMATED <1–2 min** target; likely smaller than review/CI waits. |
| E09 magistrate activation/intake/launch/pin | **MEASURED 95 min calendar** from activation 39a55bff 06:30 to R0 launch ~08:05 [S01 items 176/177], including preparation; not 95 min of interpreter startup. Pilot-4 activation **12:34 → prepare 14:46:28 (~132.5 min)** included its 103 min desk and review [S07]. | PROCESS-BOUND orchestration; DESIGN-BOUND notices/admission | Build immutable arm packets ahead of host handoff; no-op relaunches already exit without a new record/commit [S12]. Keep final host-local power, disk, lineage, quiet and arm checks fresh. |
| E10 independent executing review, fixes, delta review, cold gate, final lead diff | **MEASURED one bounded Sol fix 4.7 min; one Sol consult 14.2 min** in pilot-4 record [S07]. Whole workflow wall **unmeasured; ESTIMATED 0.5–3 h/candidate** excluding CI/desk, low confidence. | PROCESS-BOUND scheduling/repeated context; DESIGN-BOUND retained authority/gates | Run independent reviews/checks concurrently on the same immutable candidate where policy permits; delta scope after fixes; lead adjudicates. Pre-arm triple audit is once per frozen code/protocol change, not once per window [S12]. No gate deletion implied. |

### Why the R1 headline is misleading

The reproduced 15.61-hour sum is a sum of conservative phase bounds, not a
list of sleeps. For clarity, the exact phase rows are in
the evidence file: 1,800 s soak; 5,164 s 30B; 12,987 s A–B–A; 6,000 s
precool/cooldown; 5,764 s D; 17,292 s designed states; 7,200 s gated/X-G.
These add to **56,206.96 s** before display/launch overhead and the exclusions below.

Calibration brackets and terminal harvest are excluded from that sum, not free.
A plan sized to 16 hours is therefore not a guaranteed complete end-to-end
reservation. Conversely, unused cap time is not a software saving. The first
R1 record should supply phase start/end, released/timed-out G0/G1/H, load/redos,
preheat, actual cool-to-band wait, model/session startup, bytes and close time.
Only then can the lead distinguish a normal 4–8 h run from an overlong one.

## Ranked fixes: hours saved per week × ease

No measured weekly execution census exists in the inspected evidence. The
ranking therefore uses an explicit **ESTIMATED planning scenario**: 5 CI code
candidates/week; 6 terminal desks and custody turnarounds/week; 2 R0 retries/week
during bring-up; 5 review packets/week; 10 kit checks/week; 1 BYTES campaign/week;
one R1 per four weeks. Ease is 1 (new scientific design) to 5 (existing reviewed
change ready to integrate). Scores are opportunity-ranking heuristics, not
measured saved hours. Re-rank with actual cadence; R0/R1 benefit falls sharply
after commissioning. CI is counted once per candidate, not once per parallel
job or interpreter. Proposed target times below are **ESTIMATED**.

| Rank | Fix, old → target elapsed | Scenario saving h/week | Ease / score | Evidence, next implementation and acceptance |
|---|---|---:|---|---|
| 1 | **CI timing lane + finer BYTES campaign/fixture units**: measured 2.534 h module floor → **55–65 min candidate critical path** | **7.3–8.1**; midpoint 7.7 | 3 / **23.0** | [S21/S26]. First integrate reviewed timing changes, expiring `awaiting_lane` only when its module lands; then split the 60 independent campaigns with full aggregate assertions. Profile the 56-minute remainder and 46-minute coverage module. Verify every discovered test/campaign exactly once and unchanged outcomes; compare hosted walls on the same final tree. Existing split alone projects **95.7 min**, saving ~4.7 h/week versus whole-module packing; this is part of the row's saving, not additive. |
| 2 | **Parallel terminal desk preparation and eliminate duplicate parse/refit work**: measured 98–103 min → **30–45 min** | **5.3–7.3**; midpoint 6.0 | 3 / **18.0** | [S07/S10/S14]. Add stage timings first. Stage read-only per-member extraction in bounded workers, consume in roster order; share authenticated deterministic reads within the permitted run scope. Keep independent arithmetic check and raw-byte validation. Separate capture finalisation from analysis/publication. Full synthetic chain equivalence includes refusals, ordering and custody, then lead-controlled live timing; no pre-terminal harvest or mutable-file caching. |
| 3 | **R0 scoped retry/resume of unchanged successful checks**: **3.5 h → 1.25 h per representative retry** | **4.5**, bring-up only | 2 / **9.0** | [S04/S05]. Source supports `--checks` and incremental receipts, but `complete_r0` requires a full accepted set; define a lead-approved aggregate receipt binding model/stack/config/code/journal identity before reusing results. Keep physical admission fresh. This is an operational acceptance change, not authority this audit installs. A clean R0's decode will remain. #692/#699/#700 are prerequisites already built, not additional savings. |
| 4 | **Prepare once per candidate; parallel independent review/check work**: non-test/non-desk packet overhead **45 → 21 min** | **2.0**, low-confidence allowance | 4 / **8.0** | [S12]. Use one candidate manifest with exact SHA, contract deltas, timing/equality evidence and dispositions. Apply existing once-per-code/protocol audit rule; retain lead's final diff and cold gate. Do not count CI/desk time here. Measure packet-ready → reviewers-ready → final disposition; the 4.7/14.2 min examples show bounded calls, not the entire workflow cost. |
| 5 | **Bounded parallel hashing + incremental custody manifests**: unmeasured assumed **45 → 18 min/turnaround** | **2.7**, provisional | 2 / **5.4** | [S04/S09/S16]. Benchmark 1/2/4/8 file workers on synthetic closed files first. Preserve complete SHA-256, sorted manifests, no-follow/link/duplicate-path protections, ordered error reporting, file-close/fsync boundaries and destination re-read before deletion. Release input hashes are already parallel. Cache only proven immutable objects; final canonical inventory still authenticates all required bytes. This allowance is separate from desk computation and awaits a disjoint stage profile. |
| 6 | **Content-addressed kit generation/check inputs**: assumed **10 → 1 min/check** | **1.5**, provisional | 3 / **4.5** | [S04]. Cache by generator/source + complete input bytes, including pilot pins, R0/R1 slots and native qualification receipts. Publish atomically; unchanged bytes avoid writes. Always run required readiness and output identity checks. Synthetic cache invalidation and corrupted-output cases must miss/refuse correctly. This low-confidence allowance may disappear if profiling finds generation already seconds. |
| 7 | **BYTES export preparation in isolated read workers; ordered publication**: estimated **2.5 → 1.25 h exports** at midpoint of runbook range | **1.25** | 2 / **2.5** | [S19/S20]. Profile archive restoration, authentication and per-session export first. Shared withheld/key stores forbid blindly putting the shell loop in a pool. Parallelise only isolated read preparation; canonical writes/releases and commitment stay serial. Keep estimator digest, independent twin/comparer and no-key controls. Target applies to export only; fit/held-out stage targets remain unmeasured. |
| 8 | **R1 phase-aware schedule/startup work**: assumed ordinary **8 → 6 h** per commissioning run | **0.5** | 2 / **1.0** | [S06]. First measure actual phase occupancy. Prepare static input/pin checks ahead of the quiet job; avoid duplicated model setup only where the established fresh-member semantics permit. Consider a proven tighter scheduling bound without shortening actual acquisition or changing load rules. Savings exclude all fictitious unused-cap "recovery". |
| 9 | **MoE world units and night-driver clock fixtures**: measured 22.95 min MoE floor → **6–12 min**, night 108.8 s → **30–60 s** | **0 incremental candidate-wall saving banked** | 3 / **0** | [S23/S24]. Valuable feedback/runner-cost work, but both fit under rank 1's projected 55–65 min end-to-end bound. Preserve 120 worlds, 200 bootstraps, empirical rate checks, real process/signal sentinels. Their improvement must not be added to rank 1's CI saving. |

Ranks 1–2 have the strongest recurring elapsed baselines, but their **new**
durations are still hypotheses. Ranks 4–8 use unmeasured component allowances.
The scores do not justify an additive total: profiles may show custody already
inside a desk interval, review packet time may overlap physical recovery, and
multiple improvements may leave the same critical path. The roughly **35.3 h
already removed from each heavy r1 analysis** is a demonstrated precedent, not
an additional opportunity in this ranking.

### Design/physics investigations for the lead — no banked weekly saving

1. **Cooling geometry and optional cooler.** FINAL-DESIGN §3.1 already requires
   lid open, a hard stand with ≥5 cm clearance, fixed room setting and direct
   MagSafe. Keep those conditions fixed. R1 can qualify the optional cooler by
   the ≥25% decline-time improvement rule, then use it for the whole series.
   Expected new G0/G1/recovery time is **unknown**; a target 20–30% reduction in
   measured cooling time is an experiment hypothesis, not a decode speedup.
   No cooler toggling just between selected scientific members.
2. **Fixed 300 s idle versus state-based admission.** W1's 18-member planned
   ALIGN roster spends 1.5 h on configured idle before other scaffold members.
   A hypothetical 300→120 s change could save 54 min on those 18 members, but
   changes baseline formation, predecessor heat and the thermal estimator's
   context. **DESIGN-BOUND; not proposed for current v4 or any sealed block.**
   G0/G1 are already adaptive. The permitted S6 tuning is distinct from
   inventing a new release rule.
3. **SSD gap/settle design.** Its 60 s gaps alone sum to 2 h; reducing each to
   30 s would make the planning total **5.83 h**, conditional on unchanged
   recovery/power validity. That requires a prospective design/ruling. Reducing
   five blocks to three loses residual df and is not a valid optimisation.
   Qualification is mainly one-time setup: without repeated requalification
   there is no meaningful weekly saving to rank.
4. **Offload overlapping the next window.** **Not admissible now.** W1/R1 arm
   rules require no external volume, and same-Mac offload/hash/compression can
   perturb measured power, thermals and contention. SSD qualification may
   prospectively support a different policy; it is not permission to pipeline
   evidence traffic into collection. Consider copying an already-verified,
   closed archive from a separate non-measuring host only after custody,
   blinding and host-isolation authority is established. Expected wall saving
   is **unknown**. Desk paperwork can overlap recovery today; qualified clean
   dwell starts after interfering work ends.
5. **R1/roster simplification.** A–B–A legs, designed start states, the replay
   pair, acquisition durations and final-turn/token limits protect distinct
   questions. The measured D decode rate **11.85–11.95 tok/s** and theoretical
   bandwidth ceiling ~14 tok/s [S01 item 203] make a generic 3× software speedup
   implausible on this pinned workload. Dropping checks, reducing replicas,
   changing quantisation or trimming outputs requires the lead's prospective
   scientific decision. Registered estimators and Block-5 blinding stay fixed.

## Validation plan and unresolved measurements

This seat ran only source arithmetic and a three-test shard-runner subset
(0.005 s). No full/quick suite, measurement job, data pipeline, model import or
download ran. The sandbox rejected `nice`'s priority adjustment; both tiny
commands continued successfully. No native speed claim follows from this audit.

First implementation should be rank 1's timing/simulation-fixture work, followed
by rank 2's desk stage profile on synthetic bundles. For each, record wall,
CPU, peak RSS, bytes read/written, case count and cold/warm cache state; compare
same head/host and preserve an unmodified reference run. Use at least paired
repeat observations to distinguish a gain from host load. Do not profile the
active blinded job or start another heavy job on its host.

**Lead-only later gates:** native inference/cache work must run on a compatible
Mac outside this sandbox, with tests gated on `mlx` importability. Existing
modules include `tests.align.test_r0_mlx_native`,
`tests.align.test_cache_checkpoint_native`, `tests.align.test_thermal_mlx` and
`tests.align.test_smc_native` at S04's tree. Any actual R0/R1/window or SSD
qualification needs an agent-free controlled session and its own authority.
These gates were **not run**; this docs-only audit does not need them to land.

Missing evidence to collect later: successful full R0 phase wall; actual R1
phase occupancy; current full local-suite wall on a specified tree/host;
finalisation/offload/hash/kit standalone walls; release (a)/(b)/(c) walls;
BYTES export/fit/twin walls; measured weekly counts. The 7,500 s BYTES and
3,400 s MoE brief figures are not silently substituted for newer/different
hosted observations. No unresolved scientific ruling is required to accept this
inventory; the conditional changes above remain proposals for the lead.

## Source index (all local source/record text)

Git citations below mean `git show <revision>:<path>`; refs were read only from
this clone's allowed object store. Fixed SHAs make citations independent of
subsequent lane movement. No command in a cited operator runbook was executed.

| Source | Exact location / interpretation |
|---|---|
| S01 | [RUN_STATE.md](../../RUN_STATE.md), at audit base: items 49, 75–76, 105/123 timing lines (lines 444/574), 165/197 analysis timings, 176–180 launcher/intake, 194–211 R0/R1 and 213 cadence. Highest numbered ruling supersedes earlier estimates. |
| S02 | [FINAL-DESIGN](../align/council-2026-11-05/FINAL-DESIGN.md) §§1.0, 2.6–2.8, 3.1, plus [Amendment 1](../align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md) §§A1/A3/A5 and [Amendment 2](../align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-2.md). Planning numbers, not measured v4 elapsed. |
| S03 | `scripts/launch_align_r0.py` at audit base; RUN_STATE items 209/211 define admissible 300 s display dwell and R0-L3. |
| S04 | `e901eb2a480d51377a494be9d797733dfcd0220b` (`origin/lane/2026-11-06-v4-r1-integrated`): `configs/align/v4/r0_desk.json`; `joulewise/align/r0.py` (`ladder`, `long_decode`), `r0_runner.py:108`, `r0_host.py:40,318,389,417`; `scripts/align_v4_kit.py:1239`. An integration snapshot; later RUN_STATE rulings take precedence. |
| S05 | `origin/records/2026-11-07-align-r0-v4-rerun6` (`744d17a51`), `...rerun9` (`954a93b11`), `...rerun10` (`ac801585ee512d796d80e1f54e9b3ff8358c8797`): `docs/align/r0/2026-11-07-rerun{6,9,10}/NOTE.md`, opening elapsed lines. No sensor journal/report JSON read. |
| S06 | S04 revision: `scripts/align_r1_rehearsal.py:35–170,495–538,1113–1133,1301–1355`; `configs/align/v4/r1_runtime.json`; `joulewise/align/apple/r1_runtime_contract.py:25,77`; `docs/align/r1_runtime_contract.md`. Pure schedule probe reproduces rounded item-202 bounds. |
| S07 | `20799f8c743d9d6eca3e1a37ffdf716870623f33` (`origin/records/2026-11-03-magistrate-c9ac22ae`), `docs/process_traces/2026-11-03-magistrate-c9ac22ae/RECORD.md` §§Launch/Desk/Next-window design consult/ARM; `106ecad40c04de8de2f44389d602212bbdb5d8da` (`origin/records/2026-11-05-3efb8793`), `docs/process_traces/2026-11-05-magistrate-3efb8793/RECORD.md` §§Pilot 10 terminal/Desk. Text timing records only. |
| S08 | S04 revision, `docs/align/pilot_protocol_v4.md:72` and §§thermal gates/physical setup. Registered per-member schedule and fresh process. |
| S09 | [b5/driver.py](../../joulewise/b5/driver.py), `StageJournal.final`/`checkout_snapshot`; [backup_runs.sh](../../scripts/backup_runs.sh). Serial hash loops are code evidence, not elapsed profiles. |
| S10 | S04 revision, `scripts/align_pilot_session.py:269–317`; `scripts/align_v4_session.py:113`. Read-only member extraction precedes harvest, which may compress the runs. |
| S11 | [run_night.py](../../scripts/run_night.py): clean-dwell record construction (600 s) and qualification route (2,700 s timeout); chain census interval 30 s. Plan-class qualifications matter. |
| S12 | [orchestration.md](../orchestration.md) §§Cold gates, What the prune keeps, Records, The loop; [decision_log.md](../decision_log.md), D-186 and D-188–D-190. Final verification/authority stays with lead. |
| S13 | S04 revision, `joulewise/align/apple/ssd_qualification.py:44–124`, `scripts/align_ssd_qualification.py` header/defaults; RUN_STATE items 187/188. Five blocks × paired idle/decode with 120 s planning segments, 60 s gaps. |
| S14 | [2026-11-06-b5-under-90.md](../run_reports/2026-11-06-b5-under-90.md) §§3–5: dry-j walls, synthetic profiles, repeated authentication/refits and explicitly qualified projections. |
| S15 | [2026-11-07-b5-robust-fullchain.md](../run_reports/2026-11-07-b5-robust-fullchain.md): 903/964/401 s synthetic equality runs, candidate-prefetch defect and 76–124 min projected live wall. Later measured 100 min is S01, not a result of this audit. |
| S16 | [release_b5.py](../../scripts/release_b5.py): threaded input digests, serial output digests, ten-worker recompute and comparator; [RELEASE-RUNBOOK-lean.md](../analysis/b5/RELEASE-RUNBOOK-lean.md) stages (a)–(c). |
| S17 | [2026-11-06-b5-care-audit.md](../run_reports/2026-11-06-b5-care-audit.md) §2.3: synthetic parse measurement and live 5–8 min projection; not a verified successful live release. |
| S18 | [release_check.py](../../scripts/release_check.py), clean-source snapshot and `execute_smoke`. No live pipeline invoked. |
| S19 | `e091c0881e4a059f9deac1e2f9ab507b2c33ff0c` (`origin/lane/2026-11-07-bytes-stage1-run`): `docs/run_reports/2026-11-07-bytes-stage1-plan.md` §§1,3,4,5. Estimates and constraints only. |
| S20 | S19 revision, `scripts/bytes_stage1.py:251–327`. Serial run order, pinned estimator and pre-commit blinding barrier. |
| S21 | `87d9b445c9b3b5e9fb7f76a07230e3399821b3fb` (`origin/lane/2026-11-06-ci-timings-main`): `scripts/test_timings.json` `_hosted_observations_2026_11_06_cross_lane`, `seconds_by_module`, `split_modules`; `docs/run_reports/2026-11-06-ci-timings-pr-body.md`. Hosted runs include 42022192283, 42025676611, 42185282133, 42193220561; local estimates and hosted times differ. This lane is a proposal at this snapshot, not a claim of merged/green status. |
| S22 | [.github/workflows/ci.yml](../../.github/workflows/ci.yml), current 12-way ordinary packing plus exclusive jobs; [shard_tests.py](../../scripts/shard_tests.py), LPT packing, opt-in split/remainder and coverage checks. Actual production test interpreter is 3.13 in this file; 3.11 remains in the structural job. |
| S23 | S04 revision, `tests/align/test_moe_calibration.py:88–165`: 4 methods ×120 worlds, 200 resamples; preserve empirical coverage. |
| S24 | [tests/test_run_night.py](../../tests/test_run_night.py), subprocess/sleep and timeout fixtures; duration from S21 only. |
| S25 | [SHARD0.md](../run_reports/2026-11-06-b5-under-90/suite/SHARD0.md) (274 s partial module batch, Python 3.12.13); [SHARD6.md](../run_reports/2026-11-06-b5-under-90/suite/SHARD6.md) (source replay 2,665.339 s). These are partial synthetic shard reports, not a passing full-suite baseline. |
| S26 | [AGENTS.md](../../AGENTS.md) full-suite guidance; companion evidence file's source-only LPT projection using S21 weights on S04's tracked test inventory: 594 modules, 592 ordinary, **27 untimed** conservatively assigned 26.98 s. Discovery/import/addressability not executed by the probe; sum and maxima are scheduling estimates. |
