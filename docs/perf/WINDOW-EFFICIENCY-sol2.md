# Window efficiency: independent Sol2 seat

Task `window-efficiency-sol2`; branch `perf/2026-11-08-window-efficiency-sol2`.
Design analysis, **PROVISIONAL**. No measurement, registration, or change to
the armed R1 job. Source snapshot: main `4e7e878a151d919faf56bb9131af1fcca4b7be75`;
W1/R1 kit `d600baba029f70592bb8e792098338e4cd6811d3`
(`origin/lane/2026-11-07-w1-kit-r10`). Sources were read through local Git
objects and repository documents, without network access, weights, real
restricted data, or another window-efficiency seat's branch.

**Recommendation:** adopt event-driven turnaround and off-Mac desk work now;
keep v4's physics until R1 establishes what the gates actually cost. A defensible
large throughput improvement needs a different thermal estimand, shorter native
member overhead, and a new calibration. Calling those changes merely an
optimization of v4 would conceal a change in the science.

The arithmetic does **not** establish a 22-fold measurement speedup comparable
to the Block-5 software rewrite. The 16.53-hour v4 ceiling includes several
hours that are allowances, not compulsory waits. The 66-episode v5 proposal
also assumes a faster model and a different episode/thermal policy. My
conditional aggressive design reaches **2.39 fresh episodes per collection
hour**, versus **1.42** for unchanged v4 at its planning costs: about **1.68×**.
There is no live D evidence here establishing the aggressive timing target.

## 1. Evidence and authority

References below are reproducible with `git show <commit>:<path>`. External
paths appearing inside these documents were treated as text, never followed.
Numbers attributed to pilots/R0 are published repository summaries, not my
reanalysis of their raw data. **No completed R1 timing/energy record was
available in this read set.** Synthetic tests establish code behavior only.

| Key | Source and relevant sections |
|---|---|
| P4 | Kit commit above, `docs/align/pilot_protocol_v4.md`: Configuration; W1 roster; Gate semantics; U1–U6; Residual analysis; Sizing. The document explicitly lists rulings still awaiting integration. |
| TG | Same commit, `docs/align/thermal_gates.md`: Runtime behavior; Attribution and desk; WP14(b) supersession. The supersession and later rulings govern older example policies. |
| KIT | Same commit, `scripts/align_v4_kit.py`: `ROSTER`, `ruling_1f_fit`, `l1_t_dead`, `fit_roster`, `derive_sizing`, `sizing_preview`. |
| R1 | Same commit, `scripts/align_r1_rehearsal.py`: `phase_plan`, `segment_bounds`, `night_worst_case_s`, `_segment`, `wait_outside_os_batch`; `joulewise/align/apple/r1_runtime.py`: `episode_phases`, `derive_step_d_slots`, `k_step`, `observe_recovery`; `docs/align/r1_runtime_contract.md`. |
| L1/L2 | Same commit, `docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-1.md` and `LEAD-RULINGS-2.md`, especially L1/L2, R5–R8, D8-3, R10 and its review dispositions. |
| P3/S3 | Same commit, `docs/align/pilot_protocol_v3.md`; `configs/campaigns/align_pilot_v3/registration/{sizing_b5,sizing_evidence}.json`; `scripts/align_pilot_kit.py`. |
| ER | Same commit, `docs/align/energy_residual.md`, Model and training; Limits; counts-logged pilot convention. P4's sequence design supersedes the older context-only attention products. |
| RS | Main snapshot above, `RUN_STATE.md` items 160–213. In particular 162–166, 168–175 (pilots), 195–196 (thermometry), 202–204 (R1/R10/Q6), 207–213 (proportionality, meter and cadence). |
| R11 | `4526de7d587a412073cf792c959090401e8d4797`, `docs/align/squeeze/AGREEMENT-FINAL.md`, Track 1 R06/R07/R13/R14, adopted as specified in RS 212. |
| RR | Kit commit, `docs/run_reports/2026-11-05-align-{thermal-gates,v4-wp16-kit,v4-wp20-protocol,v4-wp4b-r0-wall-time}.md`, `2026-11-06-align-v4-{r1-integration,r1-round5-infra,w1-blockers}.md`; these describe implementation and synthetic checks, not completed R1 performance. |
| V5 | `docs/align/squeeze/v5-design/*.md` on the explicitly requested cached `origin/align/2026-11-08-v5design-*` refs; relevant thermal, cost and judgment sections are compared below. |

Q4 permits the **59,520 s** two-pair D-window maximum; Q6 requires **m ≥ 39
eligible benign trajectories per pair plus a locked test cohort** (RS 204).
RS 212/R11 preserves GPU energy as v4's primary residual and makes DC-in
secondary. R11 also requires whole-window-loss margin; it does not authorize
promoting a library U3 constant into a scientific bar. RS 213 authorizes
back-to-back operation with a 30–45 minute turnaround target. D-186 permits
proportionate refinement; D-188's software equivalence ruling is not a waiver
of measurement validity. Nothing here installs a ruling or changes those files.

## 2. One v4 window: what the clock is buying

### 2.1 Disjoint top-level accounting

W1 is **18** science members: four 30B anchors, eight 30B contrasts, six D
members. It contains no held-out calibration. Ordinals 5 and 17 are the D
original/replay; 18 is the development alternate, dropped first if sizing
requires it. Midpoint follows ordinal 9. The X/Y arm positions balance linear
ordinal drift and each arm/template has a D and a 30B predecessor. [P4, KIT]

A default D window is **22**, not 20, science members:
`4 anchors + 2 D sentinels + 14 fresh benign + 2 fresh sabotage`.
Thus **18 D members**, of which **16 are fresh**. The repeated sentinels and
anchors cannot be credited toward m. [P4; RS 204; V5 cost audits]

The following is a **planning/reservation budget**, not observed W1/D runtime.
Shares use the calculated maxima 44,640/58,260 s. Rows are disjoint; the
subphases in §2.2 are already inside the member rows.

| Component | W1 seconds | W1 share | Default D seconds | D share | Basis |
|---|---:|---:|---:|---:|---|
| Four unchanged 30B anchors | 3,131.27 | 7.014% | 3,131.27 | 5.375% | S3 member law, KIT preview; 782.8175 s each rounded |
| Four original D condition/pair cells | 7,200 | 16.129% | — | — | 4 × 1,800 planning allowance |
| D replay of ordinal 5 | 1,800 | 4.032% | — | — | KIT ordinal 17 |
| D development alternate | 1,800 | 4.032% | — | — | KIT ordinal 18, selection only |
| Four S contrast members | 3,400 | 7.616% | 0 | 0% | 4 × 850, P4 planning guess |
| Four G contrast members | 4,600 | 10.305% | 0 | 0% | 4 × 1,150, P4 planning guess |
| Fourteen fresh benign D | — | — | 25,200 | 43.254% | 14 × 1,800 |
| Two fresh sabotage D | — | — | 3,600 | 6.179% | 2 × 1,800 |
| Two early/late D sentinels | — | — | 3,600 | 6.179% | 2 × 1,800 |
| Calibrated scaffold, once | 4,995 | 11.190% | 4,995 | 8.574% | S3 measured aggregate; components below |
| t0/stage allowance | 3,300 | 7.392% | 3,300 | 5.664% | Plan maximum formula, not a required sleep |
| Session idle-admission wait allowance | 7,200 | 16.129% | 7,200 | 12.358% | Plan `session_wait_budget_s`; actual waits may be zero |
| Pause allowance | 7,200 | 16.129% | 7,200 | 12.358% | Plan `pause_limit_s`; actual pauses may be zero |
| Ceiling/whole-minute rounding | 13.73 | 0.031% | 33.73 | 0.058% | Difference from unrounded sum |
| **Calculated maximum** | **44,640** | **100%** | **58,260** | **100%** | 12.400 / 16.183 h |

Arithmetic:

```text
W1 science = 3,131.27 + 6×1,800 + 4×850 + 4×1,150 = 21,931.27 s
W1 programmed span = ceil(21,931.27 + 4,995) = 26,927 s
D science = 3,131.27 + 18×1,800 = 35,531.27 s
D programmed span = ceil(35,531.27 + 4,995) = 40,527 s
maximum = 60×ceil((programmed span + 3,300 + 7,200 + 7,200)/60)
```

Unrounded collection planning costs are **7.4795 h W1** and **11.2573 h D**.
The allowed 59,520 s D ceiling adds **1,260 s** above the calculated maximum
(2.117% of that ceiling). A 22-member/16.53-hour statement is a reservation
rate, **1.331 members/h**, or **0.968 fresh members/h**; it is not the measured
rate at which the Mac performs useful episodes. At the unrounded collection
plan the corresponding rates are **1.954** and **1.421**. Merely lowering a
deadline does not make a member finish earlier.

### 2.2 Every internal phase: known allocations and missing measurements

For an executed member, build a disjoint wall timeline from controller stages,
model phase markers, tool intervals and gate/hold boundaries. Attribute model
work that drains before a hold to decode; do not count it as cooling. Distinguish
pre-episode G0 from G1/H, and integration energy from wall time. R1's `tail`
is the portion after a deadline and can overlap its other phase entries: **do
not sum tail into those phases again**. Render/dispatch/cleanup gaps also need
their own residual wall row; the seven reported labels need not exhaust wall.
[TG; R1 `episode_phases`; workload turn/tool stamps]

| Phase | Number or calculation | Share of a D window / evidence limitation |
|---|---|---|
| Prepare/process/model load | Fresh process per member; included in intercept I_D, not separately timed in the available D evidence | **Unknown**. Do not transfer a 30B load cost to 28.58 GB D weights. |
| Pre-member idle baseline/admission | 300 s configured on all 22 science members: **6,600 s** | **11.328% of 58,260**, or 16.286% of collection plan, as the configured allocation. P3 observed **389–393 s** with that setting; no D transfer is established. Retries/admission waits belong to their separate actual-wait ledger. |
| Warm-up generation | One runtime warm-up per member; D and contrast use a neutral benign prompt, followed by task reset/reseed/cache reconciliation | **Unknown seconds/share**. One warm-up is not a five-second generation. |
| Post-warm-up settling | `sampling.warmup_seconds=5`, all 22 members | **110 s = 0.189%**, already within member overhead. |
| R capture | Last **60 s** of the first thermal member's idle before warm-up, ≥54 successful slots; later members consume that one record | **0 additional seconds** if covered by existing idle. It is not a second 60-second baseline on every member. |
| G0 | One per D; 18 in a default D window. W1 has 14 thermal members (6 D + 8 contrasts), anchors unchanged | Actual ΣG0 **unknown**. Ten consecutive 1 Hz qualifying samples, 60 s slope history, slow slope ≤0.2 °C/min, both upper bands, OS 0 and fresh Nominal PM. This is an adaptive release, not a fixed 600-second sleep. |
| G0 caps | Without receipt: R1-derived clamp(ceil(1.25×max wait), 600, 1,200). With R10-2(a): separate, proven sub-600 D cap and contrast-role cap | Caps are **nested in T_dead**, not additive member phases. W1 R10 deviation has censoring and full-last-turn safeguards. |
| G1 waits | Before admitted turns after turn 0: Σ(n_i−1) possible waits | Five qualifying samples relative to the episode's fixed G0 reference; cap min(300, 3×R1 recovery). Actual ΣG1 **unknown**. |
| In-decode H holds | D only; fixed chunks, no hold after final token/per-turn cap | Rough count per turn floor((decoded−1)/N_chunk), subject to termination; actual ΣH **unknown**. N_chunk=max(256,256×floor(0.6×t_decline×r/256)), or 2,048 on no observed decline. Same reference/cap as G1. |
| Decode | R0-reported D **11.85–11.95 tok/s**; use 11.9 only for scenario arithmetic | At floor B_D=6,144, full-last-turn proof charges up to **10,240/11.9=860.504 s** per D; 18 such debits =15,489.08 s (**26.586%**). This is a budget debit for a fully used episode, **not a lower bound on every realized episode**; early task completion can be much shorter. |
| Prefill/cache reconciliation | Native fed-token phase, including any rebuild/refeed; R1 planning turn uses 10k fed tokens | D seconds **unknown**, measured rate required. P3's maximum fed-prefill was **16.84169 s** (9,683 tokens), minimum observed decode **41.95547 tok/s**, 138 turns. These only support the 30B transfer law. |
| Tools/state observation | Tool intervals plus state-observation/dispatch work | D seconds **unknown**. S3 historical planning allowance is **0.0831743 s/turn** =0.0215468 tool +0.0616275 observation, observed at most one tool/turn. It is not evidence for D XML multi-call tools. Include owned tool joules in turn energy. |
| Post-run idle sentinel/teardown/reduction | Controller `idle_drift_sentinel`, cleanup, file finalization and reducer | D seconds **unknown**, included in end-to-end wall/intercept. Do not replace it with zero or call a synchronous finalize free. |
| Deadman headroom/tail | T_dead=min((1750−I_D)/1.13544,(1800−I_D−max_tail−10)/1.13544) | Bound: I_D+1.13544T_dead+max_tail+10≤1,800. Headroom is not necessarily consumed. Tail is an overlapping deadline diagnostic. |
| Arm/close/quiet dwell | RS 213 target **30–45 min between windows**, including recovery, record/hash, preflight and display dwell | At 45 min, add **2,700 s** outside collection, **6.25% of a 43,226.27 s D cycle**. No measured decomposition into arm and close is available. Include the required network-time OFF lead time in the overlapping pre-arm schedule, not as an invented extra wait every member. |
| Batch-window wait | R1 quiet segments avoid **11:45–13:15 Pacific**; recorded `os_batch_wait_s` | See §2.4: 5,400 s describes the blackout's width, not a correct universal wait cap. No evidence that every W1/D member is subjected to R1's segment scheduler. |

The 30B member law is
`516.5751274713 + 1.13544437035×episode_s`, residual SD 2.31795 s
(12 pilot-3 A observations). For four anchors, its intercept contributes
2,066.301 s and its planned episode-dependent term 1,064.969 s. Both already
contain the relevant idle/warm-up/overhead costs. **Neither I_D nor its
subphase breakdown is filled by that regression.** A table of invented exact
G0/prefill/load shares would be less useful than these explicit unknowns.

### 2.3 Scaffold and recurring versus one-time costs

The kit reuses the 25-member scaffold: **18 reference-corpus candidates**
(stop after 12 valid), **3 start references + 1 midpoint + 3 end references**.
There are additionally bracket reservation, pre/post calibration captures,
bound derivation, whole-window verdict and two backups. They are not 25
scored SHADE episodes. The 4,995 s came from pilot-3's chain journal:
`last_end − first_start − (8,182 + 7,026) = 4,995 s`. [S3 evidence]

**No per-scaffold-stage timing decomposition is present in that published
sizing evidence.** Each named stage's individual time/share is therefore
unknown; their combined recurring share is 8.574% of the D reservation.
The stage graph supplies counts, not timings. Obtain stage durations from
R1/next-window records before deciding that reusing a corpus saves most of
those 83.25 minutes. Calibration bracket, bound validity, local drift
references, copying/hashing and backup time cannot all be called idle.

Four 30B anchors and two D sentinels cost **6,731.27 s/window** at planning
values: **16.61% of collection**, leaving 16 fresh D episodes. W1's contrast
costs **8,000 s**, **29.71% of its collection plan**, once, not every D window.
Repeating W1's eight contrasts in every D-window estimate would be an error.
Similarly, R0 and R1 are selection/qualification costs, not per-window taxes.

### 2.4 R1 phase table, and a scheduler discrepancy

The source's default no-redo table is reproducible without hardware. Let
`M=1750+1.13544×1580+120=3663.9952 s`; this deliberately uses the largest
admitted intercept and startup/tail margin, not an observed average.

| R1 phase | Count × bound | Seconds | Share of 56,206.9616 |
|---|---:|---:|---:|
| Idle soak | 1 × 1,800 | 1,800 | 3.20% |
| 30B planning step, quiet/G0/recovery | M+600+300+600 | 5,163.9952 | 9.19% |
| High Power A1/B/A2, each with release | 3 × (665+M) | 12,986.9856 | 23.11% |
| Pre-step-D precool, post-D cooldown, two later-state precools | 4 × 1,500 | 6,000 | 10.67% |
| D planning step | M+1,200+300+600 | 5,763.9952 | 10.25% |
| Designed states R+4, R+2, R+0 | 3 × (M+900+1,200) | 17,291.9856 | 30.76% |
| Gated D bank, D spam a, D spam b, then X-G | 4 × 1,800 | 7,200 | 12.81% |
| **Sum** | | **56,206.9616 = 15.613 h** | **100%** |

The 665 s release bound is 65 s preroll +600 s G0. Step recovery is 600 s.
Preheat is capped at 900 s, calibration precool at 1,500 s, R1 gated/step-D
G0 at 1,200 s. The gated block uses only each next member's own configured
idle, **no extra precool**: both spam replays follow D, X-G follows D spam b.
That predecessor control is essential for interpreting their differences.
[R1; L2 R6-1/R7-1/R8-4/D8-3]

This sum **omits calibration-bracket and harvest wall**, as the function's
docstring says. Add one R6-2 retry for each of four relevant segments:
`4×(1500+5763.9952)=29,055.9808 s`. Optional 4-bit adds its own 1,800 s
table allowance; contention redos add release + repeated segment (up to two
redos per quiet segment). These are not all captured by one replacement
window. L2 also notes the unresolved additional 1,200 s if the four gated
members' configured idle lies outside their quoted bounds.

**New code-only finding:** `night_worst_case_s` labels **5,400 s** as the
maximum batch wait. `_segment` actually calls `wait_outside_os_batch(bound)`
before a quiet segment, which waits until 13:15 whenever its predicted finish
would overlap the blackout. A synthetic invocation of the **actual two pure
scheduler functions**, with no sleeping or collection, gives:

```text
now = 2026-11-08 10:30 PST; segment bound = 5,763.9952 s
predicted finish overlaps 11:45; actual wait = 9,900 s (165 minutes)
resume = 13:15 PST
```

For a single such encounter, the wait can approach **5,763.9952+5,400 =
11,163.9952 s**, and the illustrative no-redo sum becomes **67,370.9568 s =
18.714 h**, before brackets/harvest. The source's printed **61,606.9616 s**
is a phase sum plus one 90-minute blackout, **not a proved total bound**.
The analogous printed retries-plus-one-blackout total is 90,662.9424 s;
multi-day/retry execution can encounter more than one daily blackout.
This report makes **no change to R1**; the lead should compare actual waits
with the allowance after it closes. Releasing when a short task can finish
before 11:45 is sensible, but the full conservative segment bound determines
today's admission and can create additional idle time.

## 3. What each overhead controls, and cheaper substitutes

“No evidence” below means no quantified causal benefit of that particular
duration/rule in the inspected unblinded records. It does not mean the
confound is imaginary. Pilot estimates are on 30B, not proof for dense D.

| Overhead | Confound and evidence of benefit | Cheaper alternative and validity condition |
|---|---|---|
| 300 s baseline plus idle admission | Separates busy background work/idle drift and provides recovery and a reference. P3 observed 389–393 s total idle stage. **No evidence** comparing 60/120/300 s on matched D work. | Preserve live admission but use a rolling 60 s quiet/stationary baseline after a minimum reset; share only truly adjacent idle samples. Must show equivalent baseline means/drift bounds and no state-conditioned exclusions. Keep the window R stable across members. |
| Neutral warm-up and 5 s settle | Compiles/initializes runtime and prevents sabotage-specific warm-up heat; reseed protects measured RNG. **No evidence** for the marginal value of 5 s, or that warm-up can be removed on D. | Warm once per loaded-model block, then reset task/KV/RNG exactly; retain neutral work. Native equivalence, first-turn latency and residual checks required. Compiler/model caches can persist; task/hidden state cannot leak. |
| Fresh process/model load | Isolates runtime state, failures, caches and memory leakage. Token-identical 30B repeats support repeatability under the existing path, not a causal fresh-process advantage. **No evidence** quantifying per-member reload benefit. | Resident model with clean per-episode task/KV/sampler contexts, bounded worker restart cadence and memory telemetry. Qualification must include same-seed identity across positions, cleanup faults and long continuous runs. Do not parallelize episodes on the measuring GPU. |
| G0 | Controls slow heat-soak and initial state, which OS level alone misses. Pilot 6 anchors shifted −3.5 to −14.7 J, K=3 σ_w=5.08 J; no temperatures then. RS 195 observed an unsettled SMC baseline (34.0→30.6 °C) and placeholder sensors; physical control is needed. **No evidence** that 600 s is the right universal cap. | G0 already releases adaptively by settledness. Use R10's measured role-specific cap where admissible; do not add a fixed cooldown before the same test. A larger cap changes availability, not a released member's temperature criterion. A shorter cap can induce informative missingness. |
| G1 and heavy decode holds | Control within-episode DVFS/thermal history while excluding pauses from turn-owned energy. P3 clock drops preceded positive OS level by ~20 s; later bank residual/clock correlations were +0.79 to +0.92 (print-only). **No evidence yet** of matched D energy variance with versus without G1/H, or the optimal chunk size. | Joint band tuning capped at δ_slow≤2 °C is already a ruled fallback. Adaptive chunk spacing needs a qualified controller and matched injected-work checks; fewer holds must not simply censor the hottest/longest honest episodes. Dropping gates in favor of covariates changes the estimand (§5). |
| 30B four-anchor bridge | Separates common session shifts from trajectory effects and preserves the historical crossed-anchor diagnostic. Pilot 4↔5 matched SD=2.97 J, common shift −0.43 J (SE .61); K=7 σ_w=4.67 J, interaction residual SD=1.93 J. | For **v4-lean retain all four**: dropping them invalidates the existing crossed-anchor U4 claim. A new D-only early/mid/late bridge is cheaper and more relevant to D, but estimates a different drift diagnostic; cannot retroactively call it the same σ_w. |
| D sentinels/replays | Distinguish work variation from state variation; bind actual D across sessions. Repeated seeds are not independent calibration. Historical replay differences 1.3–10.1 J; same-position measurement noise ~2.10 J. D scale remains **unknown**. | Pair/interleave sentinels with matched predecessors and predeclared positions. More than one trajectory avoids blind spots; fewer than early+late loses local drift information. Replaying every episode roughly doubles active work; it is not free validation. |
| Eight W1 contrasts | Identifies whether legacy 30B G1 changes energy at identical work, and supports the pilot-state interpretation. **No evidence yet** of the treatment effect from this planned experiment. It does not authorize removing D holds. | One dedicated contrast window could simplify D scheduling. Moving all G to one window and S to another confounds treatment with window; retain within-window randomized/balanced pairs, temperature-delivery and token identity. Extra window scaffold/arm costs must be charged. |
| Decode and fed prefill | These are the workload, not removable overhead. Prefix caching materially reduced identical C sabotage work: 14,451→2,232 J and 20,563→1,380 J (RS 162); those are energy findings, not measured timing ratios. Sequence attention design reduced fit residuals ~3×; this is analysis repair, not a clock saving. | Keep episode-prefix reuse and exact accounting, checkpoints off as ruled. Rebuild counts/refed tokens must enter the model. Changing model, quantization, token cap, final-turn truncation or task affordance requires a new/frozen cohort and capability evidence. |
| Tools, state observation and logging | Owns external work and preserves prompt/action semantics. ER's synthetic omitted-tool examples show residual bias; **no D live timing evidence**. | Cache immutable assets, batch durable writes outside stamped intervals, precompute token/template checks off-Mac. Keep tool order/results and timestamps; measure logger/sampler perturbation. Moving model-affecting work across the energy boundary is invalid. |
| Scaffold/corpus/brackets | Calibrates instrument/clock alignment and contemporaneous drift. The published aggregate costs 4,995 s; **no align-specific ablation** of 18 corpus candidates or 3/1/3 references was found. | Reuse authenticated corpus derivations only while their instrument/config/age domain remains valid; retain fresh pre/post brackets and local drift references. A reduced reference design needs predictive false-fail/drift coverage, not just a small mean change. Per-stage timing comes first. |
| Deadman factor, tail and kill slack | Prevents lost bundles/incomplete work exceeding the runner cap. 1.135444 is a pilot-3 member-law slope, not a physical law; R1 rearming required later bound corrections (D8-3 alone adds 1,864 s to step-30B). | Size from end-to-end R1 wall and phase-tail evidence with conservative margins. Do not replace a worst-case proof with one observed maximum; three gated D runs cannot estimate a reliable p99. Tightening unused deadlines saves no ordinary runtime and can increase exclusions. |
| Batch wait/contention redos | Avoids scheduled exogenous load. R0 records prove actual contention and display effects, but **no measured D energy reduction** from a 90-minute blackout was found. R0's former 0.05-core refusal wasted repeated attempts on routine daemons (RS 207–211). | Preserve R1 unchanged. Later: schedule calibration/quiet phases around the blackout, do desk work off-Mac in that gap, use actual per-member bounds instead of a huge segment envelope where contracts permit. Short contaminating intervals can be flagged/retained only under a prospectively qualified rule, not outcome-based deletion. |
| Arm/close, display dwell, battery float | Prevents agent load/display activity and charging from entering the measured boundary. Display-off testing cut WindowServer/ControlCenter intervals below .02 core over 15 min; pilot 10 lost 3 members during a 21–31 W top-up and one to thermal level 1. These are real hazards. | Automate mechanical close/preflight, keep display asleep, use the 30–45 min turnaround and parallel off-Mac analysis. Do not bypass charge/top-up or quiet-start requirements. A long Mac reservation should not include 100 min of laptop-capable desk analysis. |

A useful scale check: historical ~2 J repeat noise is much smaller than the
**19–58 J** sequence-fit residual SD on fresh benign 30B work. The ~5 J
between-window component cannot explain all of that regression error. Thermal
gates may buy crucial reference-state comparability, but there is **no evidence
that they remove most of the misfit**, and those scales cannot be transferred
to D. Better feature/accounting models and better physical control answer
different questions.

Some isolated saving ceilings help prioritize qualification. Reducing configured
idle from 300 to 60 s on 22 members removes **5,280 s (1.467 h)** before any
extra G0 wait: at most 13.03% of the current collection plan. Removing all
four 30B anchors removes **3,131.27 s (0.870 h)** but loses their claim.
Replacing the existing four-anchor/two-sentinel bridge with four D sentinels
saves `6,731.27−4M` seconds at D member cost M: **1,931.27 s at M=1,200**,
but **costs another 468.73 s at M=1,800**. Thus even “fewer anchors” is not
automatically cheaper. These savings are **not additive** with the all-in
member reduction in B. No numerical gate-saving estimate is justified until
R1 supplies ΣG0/ΣG1/ΣH.

## 4. Redesign A — v4-lean: preserve v4's estimand and claims

**Change operations; preserve the measurement.** Keep the D model/precision,
sampler, admitted-turn law, reference-state GPU endpoint, five-term sequence
design, G0/G1/H, warm-up/reset, per-member 300 s idle, four anchors, two D
sentinels, calibrated scaffold and exact token checks. Keep W1's roster and
contrast in W1. Use the already ruled R10 procedure if admissible, including
its public receipt, censoring checks and separate contrast cap. No unruled
constant is installed here; R1 can still refute D admission entirely.

After a completed window, close/hash/preflight mechanically and cool to the
existing quiet start state. Run desks, reviews, kit preparation and static
checks on the laptop in parallel. Do not wait for a nominal night or until a
maximum deadline if the terminal record already exists. Retain the generous
deadline allowances unless separately qualified; schedule by **actual close**.
This implements RS 213 and does not turn reserved slack into claimed physical
savings. Code correctness and claim checks still gate use of their results.

### Roster, rate and campaign arithmetic

Use the default two-pair 22-member D frame for both calibration and the
comparison test cohort. Calibration windows supply 7 benign/pair and
1 sabotage/pair. Test windows use distinct locked seeds and are never added
to the calibration pool.

```text
D collection plan = 3,131.27 + 18×1,800 + 4,995 = 40,526.27 s
D cycle with 45 min turnaround = 43,226.27 s = 12.0073 h
all science / collection h = 22 / 11.2573 = 1.9543
fresh D / collection h      = 16 / 11.2573 = 1.4213
fresh D / cycle h           = 16 / 12.0073 = 1.3325
```

Minimum calibration: `ceil(39/7)=6` windows gives 42/pair. **Recommend seven**:
49/pair, leaving 42 after one entire lost window, then at most three more
individual losses/pair. This satisfies R11's requested whole-window margin
with the actual 7/pair roster; a 5/pair roster would need a different bill.
Propose an eighth calibration window as a count-only reserve, subject to the
lead's prospective adoption; never collect until an alarm looks good.

**Test:** three additional windows T1–T3, 21 fresh honest and 3 sabotage
trajectories **per pair** if all eligible. This is a clearly specified minimum
v4 test, not a powered adaptive-squeeze experiment. Three sabotage attempts per
pair provide very weak sensitivity precision. Fix a larger scientific test
size prospectively if that precision is inadequate; every extra default T
window costs another 12.0073 cycle-hours. No monitor/red-team work is silently
funded by this bill.

**Registration-grade qualification is still required.** The seven-window
bill counts all seven benign/pair under the published P4 roster. R11 R14
separately identifies the LOTO-benign/full-fit-sabotage score-law asymmetry;
fresh seeds and sufficient m do not repair it. R11 R13 also requires explicit
fit/calibration/test roles. If the registered remedy consumes, for example,
two of the seven benign slots/pair as independent fit support, only **five**
are calibration: eight windows reach 40/pair and **nine** leave 40 after
one whole-window loss. Then W1+nine C+three T costs
`12×11.2572972+7.4795194+13×.75 =152.3171 h =6.3465 days`.
This is a **sensitivity**, not a ruled two-support-episode fit; rank, prediction
precision and capability still need qualification. Additional development/fit
windows must likewise be added if the final scorer requires them. Do not
describe the 5.3459-day sample-count bill as a completed scientific gate.

| Allocation | Windows | Collection hours | Including 45 min turnaround/window |
|---|---:|---:|---:|
| W1, selection only | 1 | 7.4795 | 8.2295 |
| C1–C7 | 7 | 78.8011 | 84.0511 |
| T1–T3 | 3 | 33.7719 | 36.0219 |
| **From W1 onward** | **11** | **120.0525** | **128.3025 h = 5.3459 Mac-days** |
| One predeclared default-window replacement | +1 | +11.2573 | +12.0073 h; total **5.8462 days** |

Those are continuous occupied-Mac planning days at the quoted costs, **not
guaranteed calendar completion**. The existing deadline-only reservation for
W1 + ten D-shaped windows is `44,640+10×59,520=639,840 s =177.7333 h`
(7.4056 days), before turnarounds. Its unused difference from collection is
not newly saved compute. If R1 is charged rather than treated as already
armed/sunk, add its published one-blackout 17.1130 h: **6.0590 days total**,
plus brackets/harvest, actual excess waits, retry/redos and any other uncounted
qualification work. The scheduler finding alone permits another 1.6011 h
in a single encounter relative to that allowance.

**Risk/decision:** this is the low-risk recommendation before registration.
The uncertain claim is the *calendar target*, not the estimand: R1 must show
released gates, usable turns, tail fit, acceptable duty and valid instrumentation.
If the Mac still needs 17–18 h per completed D cycle, retain that measured
schedule. This design provides no basis to bypass admission to meet a date.

## 5. Redesign B — v4-max: change the thermal experiment explicitly

This is the aggressive scientifically defensible option, **conditional on a
new development qualification and prospective registration**. It keeps D
8-bit and both task pairs for a clean cost comparison; it does not depend on
downloading or selecting a faster model. It preserves known-H omission and
the active GPU endpoint, but **replaces v4's reference-state estimand with
an ordinary continuous-serving, state-conditioned estimand**. Thus it cannot
retain v4's U2/U4 crossed-anchor or “controlled reference-state energy” claims.
If those claims are essential, choose A; do not pool B with A's calibration.

Proposed implementation to qualify, not an R1 modification:

1. Keep a model resident within a block; reset task, KV cache and RNG for every
   episode. One neutral block warm-up, with a separately qualified cheap
   per-episode initialization. Use a 60 s reset/reference interval. Keep
   instrument admission and a minimum baseline; no G0/G1/H physics waits.
2. Record start thermal state, fans, ambient proxy, clock and battery state.
   Freeze a benign predictor with **pre-episode** nuisance state before
   calibration, or an explicitly prespecified state-stratified score. Fit and
   tune only on development, then use independent calibration scores. Do not
   regress on elapsed duration or temperature caused by current hidden work:
   that can explain away the signal being tested. Actual active clock and
   post-episode temperature are diagnostics. Make state-support failures
   visible as availability/limits outcomes, not selective deletion of hot
   attacks. Retain physical safety and genuine evidence-missing refusals.
3. Replace four historical 30B anchors plus two same-trajectory D sentinels
   with **four D sentinel members**: early/late on each pair. Rotate matched
   predecessors in registered balanced blocks; randomize fresh roles within
   blocks. This buys a new D-specific drift diagnostic, not the old U4.
4. Keep the 4,995 s scaffold in this bill until evidence justifies thinning it.
   Keep fresh bracketing, raw immutable records and exact boundary checks.
   Use the existing KM003C stream as an independent secondary, no new reader.
   Do not relabel DC-in as GPU energy or ignore battery storage/charging.
5. Cost actual end-to-end members, not just their decode. Keep task completion
   and whole-admitted-turn semantics; do not force shorter outcomes to satisfy
   the timing target. The worked capacity below uses B_D=6,144 and max_tokens
   4,096, so it is its own configuration if A selects a different budget.

### Timing target and how it could fail

**1,200 s all-in per member is a proposed qualification target, not a measured
D bound.** One explicit engineering budget is:

| Internal item | Proposed seconds | Status |
|---|---:|---|
| Full-last-turn decode debit, 10,240/11.9 | 860.5042 | R0 rate used as a planning premise; sustained ungated rate unmeasured |
| Fed prefill, nominal 10k/250 tok/s | 40 | **Assumption**, not a D R1 observation; multi-turn total can exceed 10k |
| Tools and state/dispatch | 10 | **Assumption**; must cover multi-call episodes |
| Reset/reference idle | 60 | Proposed replacement for 300 s baseline |
| Amortized warm-up/init/settle | 40 | **Assumption**, requires resident-worker parity |
| Amortized load/process work | 30 | **Assumption**, not the old fresh-process cost |
| Cleanup/post-idle/finalize | 30 | **Assumption**, must be measured end to end |
| Remaining timing margin | 129.4958 | Covers unmodelled gaps; not evidence of a safe tail bound |
| **Total** | **1,200** | Qualification must establish the complete roster under continuous load |

Temperature/clock decline, larger fed prefixes, slow tools or initialization
can defeat this target. R1's existing gated records can expose those costs,
but cannot prove an ungated, resident, 36-member design works. That needs new
native development after R1, outside this seat's sandbox. Never truncate an
admitted turn or filter long valid episodes to claim the target passed.

### Full capacity and sample arithmetic

Use **36 D members** per nominal 14 h collection window: four sentinels and
32 fresh trajectories, balanced 16/pair. The all-in allowance includes all
member phases in the preceding table; do not add another idle or warm-up to it.

```text
collection = 36×1,200 + 4,995 = 48,195 s = 13.3875 h
cycle      = 48,195 + 2,700 = 50,895 s = 14.1375 h
all members / collection h = 36/13.3875 = 2.6891
fresh / collection h      = 32/13.3875 = 2.3903
fresh / cycle h           = 32/14.1375 = 2.2635
```

Minimum calibration: **three** windows, `3×16=48/pair`. Recommend **four**,
64/pair, with 48 remaining after one whole-window loss; up to nine additional
individual losses/pair remain before m drops below 39. These calibration
windows use all 32 fresh slots for benign trajectories; sabotage moves to the
test cohort. Calibration replays/sentinels do not count toward m.

Three locked test windows each contain four sentinels plus **16 fresh honest
+16 sabotage** trajectories (8+8 per pair). Totals: **24 honest and 24
sabotage per pair** across T1–T3. The honest test cohort is not fit/calibration
data; no threshold recalibration after T1. This is still a small number of
independent windows and not a high-precision FPR/escape-rate certificate.

To expose all costs, retain the original W1 as a conservative one-window
selection/contrast allowance; its records never enter B calibration. Budget
**two additional 36-member development windows** for resident-worker,
ungated-state, predictive-null and injected-compute qualification. This is
a reservation for work, not an assertion that 72 members suffice to prove
every gate. Failure sends the design back to A or a revised prospective bill.

| Allocation | Windows | Cycle hours |
|---|---:|---:|
| W1/legacy bridge and deciding-contrast allowance | 1 | 8.2295 |
| New B calibration | 4 | 56.5500 |
| New B held-out test | 3 | 42.4125 |
| **Selection + registered collection** | **8** | **107.1920 h = 4.4663 days** |
| New native development qualification | +2 | +28.2750 |
| **Total from W1, including qualification** | **10** | **135.4670 h = 5.6445 days** |
| One additional count-only replacement | +1 | +14.1375 h; **6.2335 days** total |

Charge already-armed R1's documentary allowance as well and B becomes
**6.3575 days**, before the same R1 omissions/caveats as A. On a fresh
campaign, B is **slightly more expensive than A including qualification**, but
buys much more test sabotage evidence. If compatible development is already
paid, its collection-only advantage is real: 4.4663 versus 5.3459 cycle-days.
It is not honest to omit qualification and announce a guaranteed shorter
end-to-end study.

The inherited deadline formula would reserve
`60×ceil((48,195+17,700)/60)=65,940 s =18.3167 h`, despite 13.3875 h planned
collection. A smaller **50,040 s** terminal deadline (collection +1,800 s,
rounded up) is a *new proposal* requiring qualified failure/tail handling;
it is not necessary for event-driven turnover, and saves no ordinary compute.
Do not claim that a 14 h **hard reservation** is satisfied under the inherited
allowances. The cycle also exceeds 14 h once turnaround is included.

### Sensitivities and scientific conditions

If 1,200 s does not qualify, repack rather than silently overrunning:

| All-in D member | Balanced members/window | Sentinels + fresh | Collection h | Benign/pair/calibration window | Minimum / one-loss-margin calibration windows |
|---|---:|---|---:|---:|---|
| 1,200 s | 36 | 4+32 | 13.3875 | 16 | 3 / 4 |
| 1,500 s | 28 | 4+24 | 13.0542 | 12 | 4 / 5 |
| 1,800 s | 24 | 4+20 | 13.3875 | 10 | 4 / 5 |

Add three test windows and development for each. Do not treat the larger
rosters as independent windows. If a daily 90-minute blackout is imposed on
later continuous operation, its ideal duty-only cost is ×24/22.5=**1.0667**;
forward-overlap admission adds more. A 1,200 s member blocked before the
blackout can wait up to 6,600 s, giving a duty-only factor up to
`24/(24−6600/3600)=1.0827` for one such loss/day. The R1 longer-segment
scheduler can cost more (§2.4). These are scheduling sensitivities, not a new
mandate to apply an R1-only rule to every D window.

**Statistical conditions matter more than nominal m.** At m=39, rank
`ceil(.95×40)=38` gives marginal FPR ≤5%; the maximum gives ≤2.5%, only under
the actual score exchangeability conditions. Within-window correlation,
session-specific refits and thermal carryover do not disappear with fresh
seeds. Freeze training/calibration/test roles, use temporal holdout and
window-level diagnostics/uncertainty, and qualify the score law on synthetic
nulls before registration. Four calibration windows/three test windows are
weak support for general drift claims; more windows can be scientifically
necessary even if m is already large. Predeclare a balanced distribution of
states; do not trade seven temporal sessions for three without disclosing it.

R1 can refute the cheap timing premise or show a serious state effect; it
cannot confirm covariate sufficiency, persistent-worker parity, exchangeability
or ordinary-serving omission sensitivity from a few gated runs. In particular,
the three designed start states estimate a sparse slope, not the dynamic
ungated response over an entire long episode. Keep positive-control injected
work across the state range as a new qualification requirement. A covariate
scheme that improves null fit while absorbing known hidden work fails.

## 6. Why the 66-per-14-hour v5 headline is not a direct v4 forecast

Ground-up Opus §3/§8 assumes ~35 tok/s Flash-Next, ~15k decode tokens,
60 s reset, resident/lean serving, thermal covariates and a **720 s all-in
member** (1,000 pessimistic, 1,200 fallback). With four overhead members and
no additional scaffold debit, `floor(50,400/720)−4=66` scored slots. At 1,000
and 1,200 s it is **46/38**. Those are conditional capacities, not measured
native yields. Including this report's retained 4,995 s scaffold reduces the
720 s capacity to `floor((50,400−4,995)/720)−4=59` scored slots.

At D's measured ~11.9 tok/s, 15k decode alone takes **1,260.5 s**; even the
10,240-token full-last-turn debit is **860.5 s**, before prefill/tools/reset.
The 720 s scenario therefore does not transfer to full-budget 8-bit D. A
shorter realized episode can finish faster, but a capability-altering cap is
not a free optimization.

The other seats bound this claim usefully:

| Design source | Pertinent comparison |
|---|---|
| ADD-ON Opus §§5, 11 | Preserves 22-member frame and claims 7×7=49 benign/pair. Its own T1–T3 changes shrink v4's honest test cohort; that is a real inferential cost, not reuse for free. |
| ADD-ON Sol1 §8 | 17 D +4 anchors gives 56,460 s maximum; 18 D gives 58,260 s, beyond a hard 16 h. Its expensive adaptive study is not the minimum v4 m-plus-test campaign costed here. |
| ADD-ON Sol2, Window roster | One pair per test window saves duplicate fitting support; six fit members, two audits, attacks and sentinels are separately charged. Calibration retention does not make later full replays free. |
| GROUND-UP Sol1 §§2, 9 | Keeps qualified thermal control and a 1,200 s target, costs inherited scaffold and 17,700 s reserves. 24 members reserve 14.32 h. This demonstrates that gates/covariates are a substantive choice, not unanimous design evidence. |
| GROUND-UP Sol2, Mac hours | A separate **900 s** whole-member target and 3,600 s scaffold give 52 members/14 h. Qualification, seven calibration sessions, test clusters and software replays are charged. None of that timing is an R1 observation. |
| Both v5 judgments, Arithmetic audit | Warn against transferring 30B replay noise to D/DC-in, counting correlated episodes as independent clusters, omitting physical replay cost, or calling reserved time collection time. Opus's pessimistic/fallback qualification needs more than two nights. |

For reproducibility, the six design heads used were addon-opus `fa2c0a986`,
addon-sol1 `6ad7a475a`, addon-sol2 `e2e255a94`, groundup-opus `cb54bc168`,
groundup-sol1 `f63ca1aa5`, groundup-sol2 `23cb07a24`; judge-sol1 `3fbcf3da4`
and judge-sol2 `0867a29a4`. Full pins are in the run report. No source
recommends treating this throughput arithmetic as native validation.

Running contrast members in their own window is attractive only if it reduces
failed D→30B transitions enough to repay **4,995 s scaffold + turnaround**,
plus whatever anchors/sentinels the new window needs. An eight-member
contrast window retaining all four anchors would cost
`8,000+3,131.27+4,995=16,126.27 s` before extra drift roles and turnaround.
Removing those contrasts from W1 saves only 8,000 s; naive splitting adds
8,126.27 s collection overhead. It is an availability/interpretability trade,
not an automatic time saving. Preserve D-predecessor treatment delivery if
retaining the original contrast question; R11 permits a disclosed non-veto
INCONCLUSIVE result rather than forcing W1 to succeed by changing that heat.

## 7. What tonight's R1 records can settle cheaply

**Leave the armed program, instruments, constants and ordering unchanged.**
No new sampler, observer, model run or interactive process during R1. The
following are add-on **offline analyses of the records it already makes**, on
the laptop after closure/export. Preserve originals; write derived tables in
a new analysis directory. If a requested field was not captured, report
missingness and defer the corresponding qualification to a later window.

| Priority / analysis | Existing records and calculation | Decision it informs |
|---|---|---|
| 1. Complete wall ledger | Chain phase started/ended stamps; controller prepare/idle/warm-up/measured/post-idle/cleanup/reduce; token/tool/gate boundaries. Partition disjoint intervals, reconcile their union with wall, report unknown gaps and deadline-tail overlaps. | Replaces guessed D shares and locates actual removable work. Print seconds and fractions by member/phase, not only deadman fraction. |
| 2. R10 admission and lost work | Decode counts/rates, all G0 outcomes (including censored waits), G1/H medians and sums, prefill/tool, tail, full-last-turn proof. Compute the ruled procedure blind to energy. | Can D run valid useful work at all? Does sub-600 G0 admit, is duty ≤40% with ≥3 turns, are censored waits forcing fallback? No energy-conditioned cap tuning. |
| 3. Baseline/settledness sufficiency | Soak last 20 min detrended noise, slow slope, 60/120/300 s subwindows; post-load and pre-warm-up idle records on each model member. Recompute baseline means, uncertainty, drift bounds and earliest eligible release. | Estimates baseline precision and thermal delay separately. A short-baseline offline replay does **not** establish the counterfactual heat after actually shortening idle. |
| 4. Thermal dynamics and bias | Three designed start-state energies, matched spam replay pair, active clock, release temperatures, fan state and predecessor gaps. Apply predeclared L2 c=1 U5 form with σ_pair=max(observed,2.97 J), retain broad intervals. | Can refute “heat irrelevant”; cannot prove covariate equivalence from three states/one replay difference. Do not confuse a non-significant slope with a small-effect bound. |
| 5. Gate redundancy | Reconstruct every G0/G1/H's threshold-crossing time, qualifying consecutive samples, slow slope, PM freshness and native-stream drain. Plot wait by prior work/ordinal and decode-token count; simulate alternative bands/caps as diagnostics only. | Do long waits buy extra settledness, or mostly wait for an already-recovered state? Counterfactual energy under removed holds remains **unobserved**. |
| 6. Model/turn economics | Actual cached/fed/rebuilt tokens, step versus multi-turn prefill, tool-call counts/times, warm-up tokens, per-member load/hash/close costs, sustained decode rate versus temperature and High Power A-B-A adoption. | Tests the 1,200 s budget and identifies work suitable for resident reuse. No parity claim until a separate resident-worker native experiment. |
| 7. Scheduler/redo cost | `os_batch_wait_s`, intended bound and timestamps for every attempt; release, precool/retry and rejected-attempt durations. Replay scheduler offline with actual start times and the 10:30 synthetic case. | Quantifies blackout versus forward-overlap wait, incorrect +5,400 s maximum, conservative bound tax and redo tax. No changes to tonight's plan. |
| 8. Scaffold and close | Actual pre/post bracket, corpus/reference, derivation, verdict/backup/harvest stage records where present; count what R1 actually executes versus the full W1 scaffold. | Determines how much of 4,995 s is repeated work; **R1 may not execute every W1 scaffold stage**, so missing rows are not zero. Final record/pre-arm turnaround needs a later completed close/next-arm pair. |
| 9. Meter/battery/background | Existing KM003C custody/clock coverage, rail trace, SMC battery flow/SoC, charging onset and per-second CPU journal; inspect timestamps around top-ups and daemon bursts. | Confirms the physical channel exists and identifies loss risk. Do not infer system energy from charger energy alone or launch a second meter process. |

Make one compact R1 results sheet: per member **useful turns/tokens, idle,
warm-up, G0, G1, H, prefill, decode, tools, other gaps, tail, total wall,
eligible status**, plus phase/attempt totals and a separate unavailable-field
column. Print observed, cap and unused headroom separately. This is more
decision-useful than another speculative timing law.

The exact next step for the lead is to run those **record-only** analyses
after R1 closes, decide D admission under R10, and choose A or a separately
qualified B before W1 registration. Keep genuinely necessary instrument,
battery and replay controls. The available evidence supports thinning
operational delay immediately; it does not yet support removing the thermal
experiment while retaining its claims.
