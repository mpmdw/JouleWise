# Window efficiency — independent Sol1 seat

Task `window-efficiency-sol1`, brief dated 2026-11-08. Design and documentary
audit only; **PROVISIONAL, no registration or measurement authorization**.

There is room to save Mac time, but the evidence does not support a 22-fold
physical speedup of v4. Its dense 8-bit model needs about 14.4 minutes just to
decode the protected 10,240-token allowance. The strongest immediate saving is
calendar utilization: finish and turn around promptly, move analysis off the
Mac, and avoid losing otherwise useful windows to an uninformative contrast.
Dropping thermal control can buy more throughput, but changes the experiment.

I recommend **A, v4-lean, for the present series**. Preserve the reference-state
estimand and native gates; use R1 to decide whether further physical savings
are justified. **B, v4-max, is a prospective new cohort**, with an ungated,
development-trained GPU-energy score. It is a useful costed alternative if
the lead is willing to change the claim. It cannot inherit v4 calibration.

| Quantity | Existing v4 planning basis | A: v4-lean | B: v4-max target |
|---|---:|---:|---:|
| Recurring collection span | 11.258 h; maximum allowed 16.533 h | Same 11.258 h | 13.721 h |
| Episode members / fresh working members | 22 / 16 | 22 / 16 | 37 / 33 |
| All episode members per collection hour | 1.954; 1.331 per maximum reserved hour | 1.954 | 2.697 |
| Fresh working members per collection hour | 1.421; 0.968 per maximum reserved hour | 1.421 | 2.405 |
| Calibration / test physical windows in the costed plan | Not fully specified by the draft | 8 / 6 | 4 / 3, plus 3 fit and 1 qualification window |
| Common-scope Mac occupancy, including R1 and W1 | 11.21 days if every maximum slot is occupied | 8.13 days at programmed spans | 7.79 days if the new 1,200 s member qualifies |

The last row is **scenario arithmetic, not an observed saving**. A already has
the same collection span as v4; existing machinery may already return early.
Do not count unused deadline allowance as CPU time removed. B's apparent
1.69-fold fresh-member throughput gain over A becomes only about a 4% saving
on this complete, small campaign after paying for its new fit and qualification.
Larger follow-on cohorts amortize those costs. All-member rates include
anchors/sentinels; they are not rates of independent calibration observations.
These are known-cost subtotals: add the unmeasured R1 scaffold/harvest term
defined as C_R below, plus any retries. The plans meet the same calibration
count requirement but buy different test counts; this is not a power-matched
comparison.

## 1. Evidence, pins, and authority

Only repository code, protocols, configuration receipts, and unblinded pilot
summaries were read. No measurement roots, model artifacts, other window-
efficiency seat branch, network service, or Block-5 outcome was inspected.
Absolute paths in source records were treated as text. R1 is already armed
according to the brief; **no R1 result is assumed available here**.

Sources below can be recovered with `git show <pin>:<path>`. Line references
refer to these pinned blobs, not a possibly different checkout.

| Key | Pin and source | What it supplies |
|---|---|---|
| P4 | `d600baba0`, `docs/align/pilot_protocol_v4.md`, §§W1 roster, Gate semantics, Instrument checks, Sizing | W1/D rosters, thermal estimand, provisional costs and registration gaps |
| K | `d600baba0`, `scripts/align_v4_kit.py`, lines 56–83, 398–644, 1022–1053, 1255–1281, 1483–1492 | Exact roster, fit law, R10 receipt paths and preview |
| RP | `d600baba0`, `scripts/align_r1_rehearsal.py`, lines 45–175, 495–539, 1301–1382 | R1 phase order, caps, duty bar, `night_worst_case_s` |
| RT | `d600baba0`, `joulewise/align/apple/r1_runtime.py`, lines 675–697, 767–836; `docs/align/r1_runtime_contract.md` | Phase derivation, intercept, native-record fields and continuous step tests |
| TG | `d600baba0`, `docs/align/thermal_gates.md`, §§Runtime behavior, Attribution and desk | Waits, ownership, sensors and qualifications still owed |
| L1 | `d600baba0`, `docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-1.md`, L1–L2 | Tail-aware deadman; U5 constant |
| L2 | `d600baba0`, same directory, `LEAD-RULINGS-2.md`, R5–R10 and final cold-review dispositions | Current R1 sizing, removed duplicate cooldown, R10 corrections |
| C | `d600baba0`, same directory, `CHAIR.md`, rulings 1–28 and §D | Confounds, uncertainty, required scientific qualifications |
| P3 | `d600baba0`, `docs/align/pilot_protocol_v3.md`, lines 12–32, 77–132, 173–214 | Observed idle, replay design, 30B timing and legacy scope |
| SE | `d600baba0`, `configs/campaigns/align_pilot_v3/registration/{sizing_b5.json,sizing_evidence.json,derive_sizing.py}` | Pilot-3 OLS law, aggregate scaffold, tool allowances and their derivation |
| ER | `d600baba0`, `docs/align/energy_residual.md`, §§Model and training, Episode scores, Limits | Energy accounting, five-term API, why duration can absorb hidden work |
| RS | `4e7e878a1`, `RUN_STATE.md`, items 160–213 | Unblinded pilot results, R0 observations, R10/R11 and turnaround direction |
| AF | `4526de7d5`, `docs/align/squeeze/AGREEMENT-FINAL.md`, R03–R15, V05/V08, A04/A06 | Adopted gaps, separate fit/calibration/test roles and dependence limitations |

Timing/validity sections of all eight cached v5 seat/judge documents were
consulted, under `docs/align/squeeze/v5-design/`:

| Pin | File | Relevant implication |
|---|---|---|
| `cb54bc168` | `groundup-opus.md`, §§3–4, 8–9 | Source of 66/14 h; 720 s Flash-Next members, different endpoint, thermal covariates, new calibration |
| `23cb07a24` | `groundup-sol2.md`, §§Model, Energy score, Mac hours | 900 s native envelope is a qualification target; replay has its own bill |
| `f63ca1aa5` | `groundup-sol1.md`, §§2, 7, 9 | Gated alternative; 1,200 s members and independent fit/calibration/test costs |
| `fa2c0a986` | `addon-opus.md`, §§5, 8, 11 | Borrowed v4 slots and imputed/replayed attacks are not free new evidence |
| `6ad7a475a` | `addon-sol1.md`, §§2, 6, 8 | Conditional reuse, six-member fit supports, complete calendar bill |
| `e2e255a94` | `addon-sol2.md`, §§Calibration, Window roster | Corrects D count to 18; one-pair tests amortize session fit supports |
| `3fbcf3da4` | `sol1-sol1.md`, §§Evidence, Exact hybrid | New thermal populations require fresh calibration; observed thermal load must not explain away attack work |
| `0867a29a4` | `sol2-sol2.md`, §§Evidence, Recommended hybrid | Covariate adjustment is not proof gates are dispensable; clusters and native replay matter |

These are proposals and judgments, not measured throughput. The judges did not
have groundup-sol1 locally; it is present in this clone. I did not inherit
their missing-source claim.

Authority order matters:

* P4 is explicitly unregistered and contains stale/pending sections. RS 203
  installs R10; RS 204 approves 59,520 s windows and registration grade
  **m >= 39 per pair plus separate test**. Those are settled choices.
* RS 212/R11 adopts AF, keeps the v4 primary residual on **GPU energy**, and
  makes a predeclared INCONCLUSIVE contrast non-veto through an explicit R10
  supersession. K at `d600baba0` still contains the earlier receipt-path
  contrast refusal. A prospective kit must reconcile that; this report does
  not treat old code as overriding the later ruling.
* R11 also requires window-loss margin and a defensible U3 derivation. Neither
  a fixed U3 multiplier nor an unqualified thermal-control pass is installed
  here. W1 is still a selection/slot-filling pass, not calibration.
* D-078's **2026-09-04 dated addendum** in `docs/decision_log.md` governs
  interval-overlap allocation and withdraws the unrestricted clause-11
  guarantees. The old Current Project Status paragraph must not be used to
  promise physical-error coverage or an effective clearable-effect floor.
  Neither redesign deletes timing uncertainty or required metrology roles.

## 2. One v4 window: disjoint budget first

There are three different objects: R1 qualification, W1 selection, and the
recurring D calibration/test frame. Calling all of them a “16.5 h window”
obscures both the arithmetic and what can be amortized.

### 2.1 W1 selection

The exact K roster is 4 unchanged 30B anchors, 8 contrast members (two per
X/Y × G/S cell), and 6 D members. D ordinal 17 replays 5; ordinal 18 is bank
development seed 93. Five D originals plus one replay are six executions,
not six held-out observations. **W1 contributes zero to m.**

K/P4 preview: `4*782.8175 + 4*1150 + 4*850 + 6*1800 + 4995`.
The preview uses 3,131.27 s for all four anchors; its extra digits are a
rounded transfer from SE, not new precision.

| Disjoint W1 component | Seconds | Share of 44,640 s maximum | Source / status |
|---|---:|---:|---|
| Four anchors, including their own setup/idle/warmup/episode/close | 3,131.27 | 7.01% | SE/P4 transferred 30B planning cost |
| Four G contrast members | 4,600 | 10.30% | P4/K guess, 1,150 each |
| Four S contrast members | 3,400 | 7.62% | P4/K guess, 850 each |
| Five D originals/development members | 9,000 | 20.16% | K, 1,800 each; includes both conditions |
| D late replay | 1,800 | 4.03% | Same member allowance |
| Shared scaffold | 4,995 | 11.19% | SE observed aggregate transferred to W1 |
| T0 stage allowance | 3,300 | 7.39% | P4 maximum formula; allowance, not mandatory sleep |
| Session member-wait allowance | 7,200 | 16.13% | P4/SE runner allowance |
| Chain pause allowance | 7,200 | 16.13% | P4 maximum formula |
| Ceiling/rounding remainder | 13.73 | 0.03% | Arithmetic |
| **Total maximum** | **44,640 = 12.400 h** | **100%** | `60*ceil((ceil(26926.27)+17700)/60)` |

The programmed span is **26,927 s = 7.480 h**, only 13 s below the 26,940 s
span limit. R1 must replace the guesses. K first drops **18**, then lowers
B_D by 1,024 to 6,144, then returns to the lead. Its `fit_roster` docstring's
“17 first” is stale; the executable loop and P4 drop 18. Cutting 17 would
destroy the required 5/17 replay.

### 2.2 Recurring two-pair D frame

P4: 4 anchors + 2 early/late D sentinels + 14 fresh benign + 2 fresh sabotage
= **22 executions, 18 D, 16 fresh working members**. Seven benign per pair
enter the eligible calibration count; anchors/sentinels do not. Contrast
members occur in W1, not every subsequent window.

| Disjoint D-window component | Seconds | Share of authorized 59,520 s cap | Source / status |
|---|---:|---:|---|
| Four 30B anchors | 3,131.27 | 5.26% | SE/P4 |
| Two D sentinels/replays | 3,600 | 6.05% | P4, 2 × 1,800 |
| Fourteen fresh benign | 25,200 | 42.34% | P4, 14 × 1,800 |
| Two fresh sabotage | 3,600 | 6.05% | P4, 2 × 1,800 |
| Shared scaffold | 4,995 | 8.39% | SE |
| T0 / session-wait / pause allowances | 3,300 / 7,200 / 7,200 | 5.54% / 12.10% / 12.10% | Same maximum formula |
| Integer/minute ceiling | 33.73 | 0.06% | Arithmetic |
| Extra room between planning maximum and authorized maximum | 1,260 | 2.12% | 59,520 − 58,260 |
| **Authorized maximum** | **59,520 = 16.533 h** | **100%** | RS 204/Q4 |

`span = ceil(3131.27 + 18*1800 + 4995) = 40527 s = 11.258 h`.
`planning maximum = 60*ceil((40527+17700)/60) = 58260 s = 16.183 h`.
The inherited amendment's “16 × 1,800” label is wrong for this roster; the
correct multiplier is **18**, as addon-Sol2 also identifies. Do not subtract
two D members from a total that already includes both sentinels.

### 2.3 Inside a member: what is known and what is not

These rows are **nested inside** the preceding tables. They are not extra
items to add to the 1,800 s allowance. Actual phase shares require R1 records.
An invented numerical partition would conceal the very uncertainty R1 exists
to resolve.

| Phase | W1 / D-frame quantity | Share of corresponding maximum, when identifiable | Number source / needed record |
|---|---|---|---|
| Configured idle baseline | 18 / 22 episode members × 300 s = 5,400 / 6,600 s | 12.10% / 11.09% | P3/P4 and generated configs; nested in member cost |
| Observed idle inflation | 30B pilot baseline **389–393 s**, not 300 | Extra 356–372 s for four anchors: 0.80–0.83% W1, 0.60–0.63% D cap; already in transferred law | P3 lines 17–19. **No D observation yet**; do not transfer 390 s to all D members |
| Model load, validation, process/session/telemetry start, serialization, cleanup | Unknown separately | Unknown | SE 30B intercept 516.575127 s includes idle and these costs; D intercept I_D must come from RT/R1 |
| Neutral warmup compute | One invocation/member, at most **4 generated tokens**, plus full warmup prompt prefill | Unknown time; 4/11.85 = 0.338 s is decode-only, not a warmup timing forecast | `joulewise/adapters/mlx_runtime.py:57,414–432`; ALIGN workload `warmup`, benign for both D conditions |
| Post-warmup fixed settle | 5 s/member = 90 / 110 s | 0.20% / 0.18% | Generated `sampling.warmup_seconds`; controller `_stage_warmup` |
| G0 start-state wait | 14 / 18 thermal members (anchors excluded) | `100*sum(G0_s)/maximum`; unknown until R1/W1 | TG/P4; ten qualifying 1 Hz samples, slow 60 s slope ±0.2 °C/min, bands, OS/PM predicates. Cap is not wait duration |
| G1 turn waits | D turns after turn 0, plus G contrast turns after turn 0; no S-arm G1 | `100*sum(G1_s)/maximum`, unknown | Five consecutive qualifying samples; G_turn = min(300 s, 3 × R1 recovery). Fixed episode release reference, no ratchet |
| H decode holds | Heavy D only; none on 30B contrasts | `100*sum(H_s)/maximum`, unknown | N_chunk = max(256, 256*floor(0.6*t_decline*r/256)); 2,048 if no decline. Same reference/cap as G1; evaluated lookahead drain belongs to model work |
| Active decode | Actual D tokens / active rate, with holds removed | Unknown total; **10,240/11.85 = 864.14 s** per protected floor-budget member, equivalent to 1.45% of D-window cap per member | RS 203 R0 rate 11.85–11.95 tok/s; R6-3 uses the slowest step/gated rate. B_D ≥6,144 plus full final-turn cap 4,096 |
| Fed prefill and cache rebuild/refeed | Actual uncached suffixes, including legitimately re-fed tokens | Unknown | Per-turn first-token/start stamps and cached/fed IDs. 30B SE maximum 16.842 s is **not D's rate or maximum** |
| Tool and state-observation work | Actual tool-call intervals; often small in historical pilot | Unknown for D | SE legacy allowance 0.021547 + 0.061627 = 0.083174 s/turn (max observed one call). Do not transfer to D multi-call/XML work |
| Deadman tail and unused slack | T_dead minus work/waits actually consumed; positive tail after expiry separately recorded | Unknown; unused slack is **not a sleep** | L1, RT `deadman.phases_s`; 10 s L1 margin, tail-dependent fit below |
| Sensor/census overhead | 1 Hz SMC and existing PM/status/load readers | Concurrent, not additive wall time | TG/RT. R0 full inventory read median 86 ms for 403 keys (RS 195), not the smaller production sidecar's measured cost |

For numerical phase shares, the custodian should supply `sum(phase_s)` by role,
divide by the actual window elapsed seconds, and also print the reservation
denominator. RT `episode_phases` derives G0/G1/H from thermal intervals, prefill
from start→first token, decode from first→end minus H, and tools from calls.
Its `tail` is an overrun diagnostic, **not an additional disjoint phase** to
add on top of work already counted. Reconcile timestamps and disclose remaining
setup/gaps before calling the table a full wall-time partition.

L1 freezes:

```text
T_dead = min((1750-I_D)/1.13544,
             (1800-I_D-max_R1_tail-10)/1.13544)
I_D + 1.13544*T_dead + max_R1_tail + 10 <= 1800
```

The 30B contrast intercept is 516.575127 s and its deadman is **1,086.30 s**.
That is not a measured D deadman. G0/G1/H consume the G0-entry deadline;
adding “600 s cooling” outside a full episode budget double counts capacity.
R1's calibration steps deliberately re-arm after their G0/quiet or preheat,
so their bounds are different.

Without R10's receipt, W1's shared G0 cap is
`clamp(ceil(1.25*max(D gated waits, X-G wait)),600,1200)`, with censored waits
counted at 1,200. Under a signed R10-2(a) receipt, D can use a smaller cap
derived from timing/counts; the three D G0s must be uncensored and it must
preserve the full final turn. Receipt/no-receipt paths differ (L2 final
MEDIUM-2 disposition), so simply replacing “600” everywhere is incorrect.

The structural 8-bit failure can be seen without energy or future R1 values:
I_D includes at least the configured 300 s idle, so even before tails
`T_dead <= (1750-300)/1.13544 = 1277.04 s`. At the fastest documented 11.95
tok/s, `600 + 10240/11.95 = 1456.90 s`, already 179.87 s too long before
G1/H, prefill, or tools. This is an admission-budget conflict, not measured
proof that every real trajectory would need its maximum tokens.

### 2.4 Shared scaffold, batch wait, arm and close

The **4,995 s** is an observed *aggregate*, not a per-stage estimate. SE
computes it from the pilot-3 chain journal as:
`1793699064 − 1793678861 − 8182 − 7026 = 4995`.
The v4 plan graph retains, in order:

1. bracket reservation and pre-calibration;
2. reference-corpus collection (18 planned bundles, stop after 12 valid), then
   drift-bound derivation;
3. three start references;
4. first episode stage, then one midpoint reference;
5. second episode stage, then three end references;
6. post-calibration, whole-window verdict, and two-root backup.

Thus there are **25 scaffold bundles: 18 corpus + 7 references**. The 4,995 s
also includes the non-episode stages and gaps inside the journal envelope.
Individual calibration, reference, corpus-idle/warmup, derivation, verdict,
and backup seconds are **not exposed by that aggregate receipt**. Their
shares are unknown individually; collectively they are 11.19% of W1's cap
and 8.39% of the D cap. R1/next chain journals can disaggregate them. It would
be false precision to apportion 4,995/25 to each bundle or to bill all 18
planned corpus runs when early stopping actually fires.

The R1 batch exclusion is **11:45–13:15 Pacific = 5,400 s**, not a routine
extra 90 minutes in every D window. RP admits quiet segments using their full
bound and can wait for that interval to end. W1/D still encounter background
jobs and their own guards; RS 213 says respect the batch schedule, but does
not establish a separate universal 5,400 s D-window sleep. Do not add this
wait to the D table on top of all existing wait allowances as if observed.

Outside collection, RS 213 targets **30–45 min turnaround**, including
record finalization/hash, return to quiet state (about 15–25 min), pre-arm,
and display/quiet dwell. The R0 launcher has a **300 s** dwell (RS 209/211);
RS 206 specifies at least five minutes before R1's first census segment.
These are not a new per-member wait. Individual arm/close/check/restore
durations have **no measured decomposition** here. Costing below charges
30 min once per physical window, including the last, with a 45 min
sensitivity. The historical **5,400 s harvest/desk allowance** (P3: 89–90 min
observed) moves off the measurement Mac under RS 183/213; final on-host custody
and mandatory close steps still finish there.

### 2.5 R1 is a separate, one-time bill

RP/R8-4/D8-3 give `member = 1750 + 1.13544*1580 + 120 = 3663.9952 s`.
Here 1,750 s is the largest admitted startup/close intercept, **not observed
setup time**; 1,580 s is the configured re-armed step deadman.

| R1 phase group, in execution order | Arithmetic / seconds | Share of 56,206.9616 s no-redo bound |
|---|---:|---:|
| Pre-calibration snapshot / physical bracket | 0 in helper; actual scaffold outside it | Unknown, not physically zero |
| Idle soak | 1,800; last 1,200 s detrended for bands | 3.20% |
| 30B step | member + 600 G0 + 300 quiet + 600 recovery = 5,163.9952 | 9.19% |
| A1–B–A2 power-mode legs | 3 × (member + 65 pre-roll + 600 release) = 12,986.9856 | 23.11% |
| D precool | 1,500 cap | 2.67% |
| D step | member + 1,200 G0 + 300 quiet + 600 recovery = 5,763.9952 | 10.25% |
| Post-D cooldown, also first designed state's precool | 1,500 cap | 2.67% |
| Designed states R+4, R+2, R+0 | 3 × (member + 900 preheat + 1,200 G0) = 17,291.9856 | 30.76% |
| Precools before second and third designed states | 2 × 1,500 = 3,000 | 5.34% |
| Gated bank, spam-a, spam-b | 3 × 1,800 = 5,400 | 9.61% |
| X-G after spam-b | 1,800 | 3.20% |
| Post-calibration / harvest / final close | 0 in helper; additional actual work | Unknown, not physically zero |
| **No redo, no retry subtotal** | **56,206.9616 = 15.613 h** | **100%** |

One batch wait gives **61,606.9616 s = 17.113 h**. R6-2 retries for step-D
and the three designed states add
`4*(1500+5763.9952) = 29055.9808 s`; with one batch wait, the helper returns
**90,662.9424 s = 25.184 h**. These exclude calibration/harvest and ordinary
quiet-segment redos. Each heavy redo adds its segment and a 665 s release;
the per-segment redo limit is two. The optional 4-bit segment adds 1,800 s
to this helper, before its own qualification implications.

The 25.184 h figure is specifically **with one batch wait**, not an absolute
all-failures bound: a >24 h schedule can meet another daily batch window.
Use actual start/segment bounds to count overlaps. The source also carries
an unresolved +1,200 s caveat if the four gated members' 300 s idle is outside
their assumed 1,800 s bound. Report both until wall stamps settle it. None
of this is a proposal to change tonight's armed R1.

## 3. What each overhead buys, and cheaper substitutes

The empirical base is informative but narrow. RS 163–175 report:

* Pilots 4 and 5 had 28/28 eligible, token-identical matched members. Across
  the 24 originals, window contrast −0.43 J (SE 0.61), pair-difference SD
  **2.97 J**. This supports repeatability under that 30B regime.
* Pilot 6's eight anchors shifted **−0.41%**, 3.5–14.7 J; K=3 moment sigma_w
  **5.08 J**, same-position noise 2.10 J. Pilot 7 stayed with pilot 6; the
  step was between pilots 5 and 6, not explained by time of day. **No
  temperature was recorded to attribute this step.** At K=7 the reported
  sigma_w was 4.67 J, residual SD 1.93 J.
* The attention-aware logged-work design reduced bank/spam residual SD from
  182.4/36.5 to 86.9/22.9 J in pilot 7, 250.8/45.4 to 58.3/19.0 J in pilot
  8, and 274.0/118.8 to 45.1/32.7 J in pilot 9. Bank residual-clock
  correlations reached +0.92, +0.87 and +0.79 across reports. Better logged-
  work prediction helps; this does **not** identify a causal thermal effect.
* Pilot 10 lost three members to **21–31 W battery charging** and one to
  thermal level 1. A roughly 5% pack sag was about 18 kJ; measured request
  assists explained only about 300 J. Power/battery checks have real yield.
* R0's post-load evidence (L2 Round 7) found G0 settledness only after
  **840–1,040 s**, G1-like release at **279 s**, and a late common cooling
  mode tau **430–510 s**. Those are a different load, but strong evidence
  against assuming 60–90 s always buys the same state.

| Overhead | Confound or failure controlled | Evidence of reduction in noise/bias | Cheaper alternative and condition for equal validity |
|---|---|---|---|
| Per-member idle | Baseline power, quiet admission, cooldown and reference R | Eligible nominal pilots show the combined regime works; **no evidence** isolates 300 versus 120/60 s, or the extra 89–93 observed seconds | First audit capture/admission latency. For a later qualified cohort, use last-60-s reference and adaptive settledness rather than fixed padding. Preserve PM/OS/battery predicates and baseline precision; cannot assume net saved seconds equal idle removed because G0 may grow |
| Warmup plus 5 s settle | Compilation, first-call/kernel/cache initialization, condition-dependent heat | **No evidence** quantifies benefit of four warmup tokens or five seconds alone. Neutral prompt removes a design asymmetry | Merge redundant *within-process* warmups only after exact prompt/cache/RNG/native timing checks. Fresh processes still need their own initialization. One night-level warmup cannot warm all later fresh processes |
| Fresh process/load/close | Cross-member KV/RNG/task/allocator carryover and leaked workers | Synthetic/native identity gates establish behavior; **no evidence** measures persistent-process bias | Persistent model worker with hard task/cache/RNG reset and process census; qualify identical tokens and timing/energy first. Not part of A |
| G0 | Different start heat soak, slope, OS/PM state | R0 long recovery proves thermal debt; v3 shifts are compatible with several causes. **No evidence** yet measures D residual-SD reduction from G0 | Adaptive release is **already implemented**: it waits for state, not for the cap. Shorten only redundant pre-gate idle; use R10 cap for bounded exclusion. A start-temperature predictor can replace the intervention only in B with fresh calibration |
| G1 | Heat accumulation across turns; avoids a moving reference | R0 replay's 279 s recovery supports a long wait can be real. **No evidence** of D bias removed per G1 | Tune S6 jointly with holds within ruled 2 °C limit, using U5 and duty evidence. Paired/interleaved order balances slow drift but does not restore within-turn clocks. No fixed shorter wait claimed equivalent |
| Decode H holds / drain | Clock decline inside long dense decode; avoids charging asynchronous work to cooling | Continuous R1 steps can observe decline; native resume/lookahead qualification remains owed. **No evidence** yet quantifies D noise reduction or resume-transient cost | Larger qualified N_chunk or no holds only if decline/energy-equivalence evidence supports it. B accepts a new continuous-serving estimand; clock or post-load temperature regression could otherwise absorb hidden work |
| Four 30B anchors | Historical instrument bridge and between-window drift | K-session offsets and 1.93–2.10 J residual repeat noise are measured; new setup changes comparability | Keep all four in A. Two D trajectory pairs replace historical anchors in B; disclose loss of the 30B bridge. Old sigma_w formula divides by four and cannot be kept after halving anchors |
| Two D sentinels | In-window/cross-window drift, exact-work identity and U4 | D evidence absent before R1; v3 replays demonstrated the need to observe drift | Keep early/late identity-bearing pairs. They cost time but cannot become fresh m. Inconclusive U4 can require more sentinels, so the nominal two-sentinel budget is not guaranteed |
| Eight W1 contrasts | Separates 30B G1 treatment from template/time/stage and verifies delivery | **No D evidence**; 30B same-work differences supply scale, not a measured treatment effect | R11 non-veto INCONCLUSIVE avoids holding D for an uninformative contrast. Four runs would remove within-cell replication and change uncertainty. Separate contrast window is viable for scope, not a free speedup; see below |
| Three-state temperature study | Bounds sensitivity to release-temperature band (U5) | No D estimate yet; L1 uses c=1, replay floor 2.97 J. Three points give only one residual df | Run once in qualification, not every D window. Analyze existing temperatures/energies; broad CI is imprecision, not evidence of no bias. Cannot replace with a significance test against zero |
| Soak, precools, recovery and A-B-A | Reference noise; sensor selection/cooling; power-mode comparison | R0 placeholder/unsettled-sensor catches were real (RS 195); no measured gain from longer soak or A-B-A yet | Already amortized in R1. Duplicate 600 s post-30B cooldown was **removed by R6-6**; do not save it twice. An unobserved recovery tail remains censored; do not fit an invented short tau |
| Seven short references and calibration brackets | Timing alignment, drift and scale/stability over window | P3 I1–I4 passes support complete instrument stack, **no evidence** isolates marginal benefit per extra reference | Keep current scaffold in A/B costing. Share a boundary reference across adjacent windows only after a custody/temporal-support ruling. Midpoint losses and drift can be nonlinear; endpoints alone are not an established substitute |
| Eighteen planned corpus members / bound derivation | Current-window drift-bound estimation, minimum valid support | Reused machinery, **no evidence** here shows 12 valid versus a smaller corpus has same coverage | Honor existing stop-after-12-valid. A cached bound could save work but needs stability/coverage across setups and time plus prospective registration. Derive/check on other hardware only if no live chain consumer needs the result first |
| Prefill / cache rebuild | Actual legitimate model work and state history | Large cache savings documented, but pilot 2→3 also changed thermal/cache regime; cannot attribute all 14,451→2,232 J or 20,563→1,380 J changes to caching alone | Prefix caching already on. Avoid repeated render/tokenization without changing template or fed-token accounting; checkpoints remain explicitly off. New cache/checkpoint policy needs identity and energy qualification |
| Tools and state snapshots | Actual task actions, correct grading, per-turn work accounting | Historical 0.083174 s/turn is small; D multi-call cost unknown | Offload scoring and postprocessing; retain executing tools on actor path. Do not replace real tool work by mocks or omit its energy; no plausible multi-hour saving established |
| Sidecar, PM, battery and census | State observability, attribution, contention and charging | R0 100 ms coverage tolerance rejected real reads; low census thresholds repeatedly stopped R0. Display-off removed UI bursts. None proves current sidecar is free | Reuse existing streams/readers and analyze offline. R11 forbids a second KM003C reader. No new live logger tonight. Quantify overhead before lowering cadence/coverage |
| Deadman / runner slack | Bounded stalls, complete final turns, salvage and safe cleanup | 30B OLS SD 2.318 s, max absolute residual 3.728 s, n=12; **not a D-tail quantile**. R1 tails pending | Measure phase closure and max tail, keep 1.13544 until qualified. Unused allowance costs no elapsed time in an early-finishing chain. Do not shorten T_dead to increase episodes/hour while silently truncating the estimand |
| Batch/contamination waits | Shared CPU/power disturbance | R0 failures show real daemon activity, but 0.05-core aborts mostly guarded selection records rather than energy effects; R0-L3 already replaces that behavior | Keep display asleep, fixed-cadence existing census, prospective per-member disposition and count-only extensions. R1's 0.5 core/60 s redo rule stays tonight; removing all guards is not justified by calling macOS “quiet” |
| Arm, close, backup, desk | Power-mode restoration, immutable evidence, recoverability, informed next arm | P3 desk 89–90 min is measured; RS 213 turnaround is a target, not a trace | Finalize/hash/close on Mac; analysis/reviews/kit work off Mac concurrently with next capture. Copy/backup must not create load during measurement. Precompute immutable inputs; no simultaneous agent on measurement Mac |

**Contrast-only windows.** Moving the eight contrast members out of W1
saves 8,000 planned W1 seconds, but adds another scaffold of 4,995 s and
another turnaround, plus any D predecessor heaters needed to reproduce the
original heat ordering. Without those extra heaters, it is a different
contrast. Idealized separate contrast span is `8000+4995 = 12995 s`, so the
series is already **6,795 s = 1.888 h longer** including a 30 min extra
turnaround, before caps/heaters. It can reduce W1's admission fragility and
simplify interpretation; it does not reduce total Mac time under this ledger.
Within-window balanced/interleaved G/S is preferable if the original contrast
is retained, with delivery/stage/predecessor terms frozen before collection.

## 4. Redesign A — v4-lean

### Changes and preserved claim

Keep the selected 27B quantization, stack, prompt/cache/seed rules, episode
budget and full final turn, GPU-energy endpoint, neutral warmup, 300 s idle,
G0/G1/H, all four anchors, two D sentinels, scaffold, and exclusion/accounting
rules. Freeze final slots before D1. R10/R11 reconciliation, U3 derivation,
completed-turn duty semantics, battery rules, and registration cold gates are
prerequisites, not claimed complete by this design.

Make the **operational** window end at actual terminal completion; hand its
sealed record to the off-Mac desk and perform only the 30–45 min physical
turnaround on the MBP. The 59,520 s safety maximum remains available. Batch
and member-wait allowances remain safety allowances; no successful member
loses a turn to manufacture a shorter schedule. Apply R11's non-veto contrast
disposition prospectively; an INCONCLUSIVE contrast still cannot claim a
thermal explanation. A does not depend on guessing a shorter idle or G1.

This is safe for v4's estimand because it changes scheduling and placement of
desk work, not what a measured trajectory does. It largely implements RS 213,
so it may be an execution improvement rather than a new code optimization.

### Full allocation and arithmetic

* **W1:** one selection window, zero m. Keep 5/17 and the eight contrasts;
  allowed ordinal-18 drop remains prospective if sizing requires it.
* **C1–C8:** eight calibration windows with the 22-member roster. Each gives
  7 fresh benign/pair, hence **56/pair** nominal. Lose one whole window and
  20% of remaining benign members: `floor(7*7*.8) = 39/pair`. This is a
  deterministic allowance conditional on that loss bound, not a probability
  forecast. Fixed cap eight; below 39 for either pair at cap means insufficient
  calibration, not selection of the quietest 39 or an automatic retry.
* **T1–T3:** three test tranches, **two physical windows each**, one per pair.
  Each window has 4 anchors + 2 sentinels + **6 fresh benign fit-support** +
  **4 untouched benign tests** + **6 sabotage tests** = 22. Fit support is
  paid and separate from both m and honest tests. Per pair: 18 fit members,
  12 honest tests, 18 sabotage attempts across three physical test windows.
  Scoring/LOTO/full-fit comparability and rank law must be frozen and audited;
  matching six-member training cardinality to calibration folds alone does
  not prove exchangeability. These are v4 signature/omission tests, not a
  funded adaptive-squeeze or rare-escape certificate.

This is a **proposal to size the currently missing full Q6 roster**, not an
assertion that D8 or six test windows were already authorized by R11. Both
pairs and a fixed failure-at-cap consequence must be in the series plan.
Keeping only three two-pair test windows would spend twelve support members
per window and leave only four genuine test slots; those supports cannot
also count as untouched honest tests.

Keep the existing one-sided GPU-score rank construction, with strict `>` and
conservative ties: `k = ceil(.95*(m+1))`, using the actual eligible m. At
m=39, k=38 gives a conditional marginal bound of 5%; it is not the maximum's
2.5% bound (R11). This does not cure the separate LOTO/full-fit and
between-window exchangeability questions. No monitor fusion rule is added.

For each of 14 recurring windows:

```text
collection span     = ceil(4*782.8175 + 18*1800 + 4995) = 40527 s
                    = 11.2575 h
cycle, 30 min turn  = 11.7575 h
members/hour        = 22/11.2575 = 1.9543 collection; 1.8711 cycle
fresh/hour          = 16/11.2575 = 1.4213 collection
calibrators/hour C  = 14/11.2575 = 1.2436 collection
```

Common-scope bill, starting with the already-armed R1:

```text
R1, one batch wait       = 61606.9616/3600 + .5 = 17.6130 h + C_R
W1, charge full maximum  = 44640/3600 + .5      = 12.9000 h
C1-C8 + six T windows    = 14*11.7575          = 164.6050 h
total                   = 195.1180 h          = 8.1299 Mac days + C_R/24
```

`C_R` is R1 physical calibration/scaffold/harvest time **outside** the helper's
bound, excluding the already charged turnaround. Its duration is unknown;
it remains an explicit additive term in every total. R1 retry/redo costs are
also additional. With 45 min turnaround add **4.00 h = 0.167 day** (16
physical windows). A 25% capacity contingency on the known subtotal is
**243.8976 h = 10.1624 days**, plus the separately budgeted unknown/retry
terms. Capacity reserve does not authorize replacements.

If all 14 recurring windows occupy the full 59,520 s allowance instead,
the same calculation is **268.9797 h = 11.2075 days + C_R/24**. Ratio 1.379.
That is the upper scheduling opportunity, **not a prediction of a 27.5%
physical runtime reduction**. Existing early return makes the corresponding
reservation-only saving zero. One-window-per-night scheduling is not assumed;
RS 213 explicitly dedicates the Mac around the clock.

### Risks and R1 discrimination

The main risks are **yield**, not a new measurement bias: G0 timeouts, holds
consuming the full-turn budget, charging, U3 instability, and incomplete
turns masquerading as useful admissions. R1 can refute the 1,800 s fit or show
R10's short G0 is unachievable. Then A's calendar is not admissible; use the
ruled fallback or screen-only outcome, not optimistic averages.

No further physical idle/hold reduction is included in A's headline. A
same-estimand follow-up may shorten idle only after native selection data
show unchanged released-state distribution, token identity, clock/energy
repeatability, baseline uncertainty, and acceptable completion yield. R1
journals can identify redundant dwell, but cannot alone replay a different
warmup/idle sequence counterfactually.

## 5. Redesign B — v4-max

### Most aggressive defensible boundary

Retain **the same D 8-bit model**, two task pairs, sampler, cached-prefix
accounting and full-turn admission policy, to isolate an efficiency design
from the separate Flash-Next/model change. Use continuous native decode and
no G0/G1/H intervention. Keep OS/PM/battery/collector observations, bounded
processes, exact evidence custody, metrology uncertainty, per-attempt failures
and fixed physical setup. Replace the four historical 30B anchors and two D
sentinels by **four D sentinels**: two fixed benign trajectories, one per
pair, each early/late. Lose the historical anchor bridge openly.

Use a 60 s reset/reference observation, one neutral per-process warmup, and
a qualified **1,200 s whole-member envelope**. Keep the shared 4,995 s
scaffold in the bill; no savings from unqualified bound/reference deletion.
Continuous collectors and immutable-input precomputation may reduce process
overhead, but each member retains a fresh actor/task state. A persistent
model process is optional only after reset/identity qualification.

The target is physically possible, not demonstrated:

```text
protected decode at documented slow rate     10240/11.85 = 864.135 s
reset/reference observation                                   60 s
proposed warmup/load/session/cleanup aggregate                 145 s
proposed fed-prefill and tools aggregate                        90 s
remaining contingency                                      40.865 s
whole member                                               1200 s
```

The last three allocations are **targets with no D timing evidence**, not
measured components. Bank/sabotage prefill may exceed them; R1 has only a
bank/benign gated case. At higher frozen B_D the decode term is larger; this
particular bill therefore assumes **B_D = 6,144**, frozen during development,
full 4,096-token last turn, and a native tail-safe member budget. If the
member envelope needs 1,500 or 1,800 s, use the sensitivity table below.
Do not shorten coherent action trajectories after reading calibration/test.

Train a small, **fixed per-pair GPU-energy predictor on independent F data**,
including logged-work terms and, if development supports them, only
pre-episode thermal/ambient state. Use later temperature, fan and clock
histories diagnostically. Neither active duration nor attack-produced heat
may earn predicted legitimate joules: doing so could explain away hidden
compute. No post-hoc residual refit on C or T, and no unseen window-specific
random effect estimated from the scored attack. Freeze transforms/scales,
strict rank/tie rules and missingness before C.

Define the new scalar score as `(whole-episode GPU energy - frozen predicted
legitimate energy) / frozen predictive SD`, composing the measured integral's
uncertainty as in ER and including a development-estimated fixed episode/gap
term over that same scored span. It is one-sided for excess unexplained work.
Use `k = ceil(.95*(m+1))` on held-out C scores disjoint from F, strict `>` and
conservative ties; at nominal m=66, k=64 has marginal exceedance bound 3/67 = 4.48% under
exchangeability. Estimator/uncertainty details must be frozen before C; no
post-test choice between this score and a temperature-conditioned variant.

This preserves a scientifically meaningful question about detection of
omitted logged work under continuous serving. It **does not preserve v4's
reference-state energy, U2/U4 control claim, historical bridge, or original
per-session estimator**. It needs a separate registration and fresh F/C/T.
The primary remains GPU energy here; making DC-in primary would require an
additional endpoint/battery/tail contract. R11's secondary meter stream is
retained without pretending it already qualifies that new endpoint.

### Full allocation and arithmetic

For a 14 h physical window with the old scaffold retained:

```text
floor((50400-4995)/1200)             = 37 total members
37*1200+4995                        = 49395 s = 13.720833 h
4 D sentinels + 33 fresh working    = 37
members/hour                        = 2.6966
fresh working/hour                  = 2.4051
cycle with 30 min turnaround         = 14.220833 h
```

* **Q:** one separately costed qualification window. Native reset/token
  identity, continuous-state repeatability, phase closure and long-tail
  checks happen before any C. Failure stops this option; Q is not m.
* **F1–F3:** 33 fresh benign each, alternating 17/16 between pairs, giving
  50/49 distinct-seed development members by pair, plus sentinels. Train and
  freeze the score; use leave-window-out development diagnostics to challenge
  thermal transfer. None is subsequently promoted into calibration.
* **C1–C4:** 33 fresh benign each, alternately 17/16 and 16/17 by pair:
  **66 calibrators/pair**. Lose one window with 17 members of a given pair:
  49 remain; `floor(.8*49)=39`. Use all eligible, not a selected 39. Below
  39 for either pair at the fixed cap is unresolved. Four windows meet the
  count requirement; four do not prove 66 independent thermal environments.
* **T1–T3:** each has 16 sabotage tests (8/pair) and 17 honest tests
  (alternating 9/8 by pair), plus four sentinels. Totals **24 sabotage
  attempts/pair and 26/25 honest tests** over three shared physical windows.
  A frozen F predictor means no twelve-member session-fit tax in T. These
  tests are held out from F/C and any attack selection.

Thus **4 calibration + 3 test windows**, with **3 fit + 1 qualification**
also paid: eleven new-policy physical windows. The larger episodes/hour
number does not come from counting F/sentinels as calibration or from
silently spending calibration members to fit the predictor.

The common-scope comparison also charges the already-armed R1 and the
original W1 selection maximum, so no savings are credited for abandoning
v4's remaining selection work:

```text
Q + 3F + 4C + 3T       = 11*14.220833 = 156.4292 h
common R1 and W1       =                30.5130 h + C_R
total                  =               186.9422 h = 7.7893 days + C_R/24
25% capacity reserve   =               233.6778 h = 9.7366 days, before unknown terms
```

With 45 min turnaround add **3.25 h = 0.135 day** (13 windows). This does
not fund a new model/quantization, a monitor/red team, an autonomous physical
hidden-compute positive-control campaign, or a full native software-replay
competitor; those are separate experiments, not free detector views.

Sensitivity of the 14 h frame, retaining four sentinels and 4,995 s scaffold:

| Qualified whole-member envelope | Total slots | Fresh slots | Programmed hours | Fresh members/hour |
|---|---:|---:|---:|---:|
| 1,200 s target | 37 | 33 | 13.721 | 2.405 |
| 1,500 s | 30 | 26 | 13.888 | 1.872 |
| 1,800 s | 25 | 21 | 13.888 | 1.512 |

The 1,200 s F/C/T roster must be **repacked and recosted**, not silently
retained, if either slower envelope is measured. R1 is not that qualification.
Neither the 1.13544 legacy law nor “no gates” proves a faster member.

### Validity risks and how to falsify the design

Thermal state can change both joules/token and the behavior/length of a
trajectory. Start-temperature adjustment does not repair within-episode
throttling or guarantee exchangeability. Calibration and testing should be
interleaved over time under sealed roles, with both tasks balanced in every
window, no test feedback, and window-clustered uncertainty. Three test
windows support only weak population statements; more windows are needed
for a precise low false-positive/escape-rate claim. A conformal rank bound
is conditional on the score law being exchangeable, not a consequence of
reaching m=39. Report empirical honest alerts and temporal drift separately.

R1's continuous 4,096-token steps can challenge this option cheaply if they
show large clock decline, poor temperature-band energy stability or long
tails. Compare irreducible load/warmup/prefill/tool/close costs with the
335.865 s left by decode, removing R1-only G0/quiet/preheat/recovery phases
and explicitly accounting for B's different reset. Excess costs refute the
assumed timing inputs for the same backend/shape; they do not disprove an
unimplemented optimization. A small beta_T interval and flat clocks would
encourage B, but **cannot establish** its
ungated multi-turn residual law: R1 begins steps from controlled states and
has only three gated development trajectories. Q/F must demonstrate native
thermal overlap, exact reset behavior, useful complete actions, honest
out-of-window score stability and sufficient detection resolution. If those
fail, publish the limitation or use A; do not regress on observed hidden-load
temperature/clock to force a positive result.

### Why 66/14 h does not transfer

Groundup-Opus explicitly budgets Flash-Next at about 35 tok/s, 15k decode
tokens, 42 s incremental prefill, 30 s tools, 60 s reset and 20 s teardown:
about 580 s, padded to 720. `50400/720 = 70` slots, minus four overhead slots
= 66 scored episodes. This is **4.714 scored/hour**, but it changes model,
scaffold, endpoint, task/episode distribution and fitting scheme. It also
depends on native qualification that has not happened here. The same seat's
27B-4bit fallback is 1,200 s and 38 scored/night under its different scaffold.

The v4 comparison's “22” includes six instrument checks, while “66” excludes
four overhead slots. Compare fresh/usable rates and complete campaign cost,
not just those labels. At D's documented rate the protected 10,240-token
decode alone exceeds a 720 s member. A faster model/precision is a plausible
larger saving, but has separate capability, runtime, metrology and fresh-
calibration obligations. No result-equivalence argument like Block-5 analysis
can make different physical trajectories the same observation.

## 6. Cheap answers from tonight's unchanged R1

**Do not attach instrumentation, start a probe, change caps/order/config, or
open an agent on the measuring Mac.** All requests below are post-terminal,
off-Mac analyses of already-produced R1 records, or operator annotations from
the existing arm/close records. No sealed Block-5 source is an input. Have
the authorized custodian export only these unblinded R1 summaries after close.
Analyze timing/counts first, before any detector-result-driven design choice.

| Question / output | Existing record and cheap calculation | Decision it informs; what it cannot establish |
|---|---|---|
| Where did the wall time go? | Driver invocation start/end, bundle `events.jsonl`, episode/turn stamps, chain stage journal: disjoint load/idle/warmup/G0/episode/close/backup timeline, then phase shares and closure remainder | Replaces every unknown in §2. Profile hashes/reduction and redundant serialization off Mac. No per-stage record means “unmeasured,” not zero |
| Is the 300 s inter-member schedule actually 300 s? | Last decode/end of R+0 planning turn → next process start, model prepare, idle start/end, warmup, G0; repeat for bank→spam-a→spam-b→X-G | Settles RS 202(5) and +1,200 s bound caveat. Separate thermal rest from model work; cannot equate wall gap with cooling |
| Does D fit at all? | `r1_slots.deadman_budget`, `budget_fit_inputs`, duty bar, tokens, turn/stop flags; independently derive L1/R10 with min(step/gated rate), full final-turn cap, projected holds and pair-specific prefill/tool allowances | G0*/X2 exposure, max fitting B_D, completed useful turns. An admitted unfinished turn is not a useful action. No energy fields needed for the budget procedure |
| Is cooling buying useful time or consuming the episode? | Per-gate `gate_waits_s`, released/censored outcomes, G0/G1/H fractions; first eligible release on fixed reference, temperature/slope/clock histories; waits vs ordinal/predecessor | R10 feasibility and S6 tuning within current rules. Include all failed waits. Three D runs give no stable p95 or tail guarantee; R1 D-after-D is not W1 D-after-30B |
| Could an adaptive/shorter baseline suffice? | Re-evaluate settledness/coverage on 60/120/180/300 s subwindows of existing idle/soak, compare detrended baseline uncertainty and reference medians | Finds padding and sensitivity without measuring again. It cannot reproduce changed warmup timing, thermal trajectory or baseline admission; native selection qualification still required |
| What noise is controlled by start state? | Three designed-state measured release temperatures/energies, exact token identity, beta_T with full one-df uncertainty, replay-pair noise, clocks and task/context labels | Tests U5 and possible covariate scale. No non-significance-as-equivalence, no temperature-free v3 “thermal refit,” no extrapolation from one long step to all D turns |
| Are H holds placed before real decline? | Continuous step PM clock vs token count and elapsed time; gate/hold dispatch stamps and first post-resume clock samples in gated runs | Falsifies over-frequent holds or harmful resume transients; identifies a candidate larger N_chunk for a prospective selection test. No absent no-hold trajectory may be imputed as measured |
| Can deadman/startup margins shrink? | Step/gated `member_wall_s`, I_D, G0-entry origin, every expiry/tail, close/watchdog outcome; compare modeled vs actual wall and largest positive residual | Identifies overbounds. A maximum of a few observations is not a high-quantile safety certificate; keep salvage/kill/restore guarantees and inspect unclassified time |
| Is the batch policy avoiding or merely reserving time? | Existing quiet CPU journal, recorded waits/redos, segment start/duration and local-time overlap; simulate scheduling with recorded bounds | Quantifies actual 5,400 s wait and repeated daily overlaps. Record daemon source/episode loss. No deliberate contention injection or changed R1 disposition |
| What does fixed scaffold cost? | Existing chain stage start/end for pre/post bracket, corpus, derivation, start/mid/end references, verdict, both backups; number of corpus members actually executed | Separates recurring metrology from expensive postprocessing. Does not justify smaller reference n or cached drift bounds without uncertainty analysis |
| Is charging the real yield bottleneck? | Existing 30 s battery journal, charger/SoC/flow records, episode spans and the **existing** KM003C stream; verify clock coverage and custody | Drain slope, charge-resume SoC, projected top-up time, unavailable members. DC-in is secondary in v4. Do not start a second reader or call an empty stream live capture |
| What really occupies the 30–45 min turnaround? | Existing terminal/hash/restore/uninstall/pre-arm/display timestamps and operator arm annotation, collected after close | Separates unavoidable cool-down from laptop-able desk work; permits back-to-back scheduling without placing hash/copy/agents inside the next measurement |

The next exact step is for the lead/custodian to produce that **timing-only
R1 timeline and admission worksheet**, complete the R10/R11 registration
reconciliation, and choose A or charter B before any new held-out member is
spent. R1 cannot establish the causal benefit of gates without an appropriate
future comparison. No additional live run is requested tonight.

## 7. Reproducible arithmetic audit

This standard-library block uses only documentary constants and proposal
inputs. It reads no files, imports no runtime/model package, and performs no
measurement. Its assertions check arithmetic, not scientific validity.

```python
# WINDOW_EFFICIENCY_AUDIT
import math

anchor4, scaffold, reserves = 3131.27, 4995, 3300 + 7200 + 7200
w1 = math.ceil(anchor4 + 4*1150 + 4*850 + 6*1800 + scaffold)
d = math.ceil(anchor4 + 18*1800 + scaffold)
assert w1 == 26927 and d == 40527
assert 60*math.ceil((w1+reserves)/60) == 44640
assert 60*math.ceil((d+reserves)/60) == 58260
assert 59520 - 58260 == 1260

f = 1.13544
rearmed = 1750 + f*1580 + 120
step30 = rearmed + 600 + 300 + 600
stepd = rearmed + 1200 + 300 + 600
designed = rearmed + 900 + 1200
aba = rearmed + 65 + 600
r1 = 1800 + step30 + 3*aba + 4*1500 + stepd + 3*designed + 4*1800
retry = 4*(1500 + stepd)
assert math.isclose(r1, 56206.9616)
assert math.isclose(retry, 29055.9808)
assert math.isclose(r1+5400, 61606.9616)
assert math.isclose(r1+5400+retry, 90662.9424)
assert math.isclose((1750-300)/f, 1277.0379764672725)
assert 600 + 10240/11.95 > (1750-300)/f

# Both-pair count margins, with the stated loss bounds only.
assert 8*7 == 56 and math.floor((8-1)*7*.8) == 39
cal_windows = [(17,16), (16,17), (17,16), (16,17)]
assert [sum(w[p] for w in cal_windows) for p in (0,1)] == [66,66]
for lost in range(4):
    for pair in (0,1):
        assert math.floor(sum(w[pair] for i,w in enumerate(cal_windows)
                              if i != lost)*.8) >= 39
assert 4+2+6+4+6 == 22  # A: anchors, sentinels, fit, honest test, sabotage
assert 37-4 == 33       # B: total minus sentinels
assert 17+16 == 33      # B: honest and sabotage tests per window
assert math.floor((50400-scaffold)/1200) == 37

turn = .5
common = (r1+5400)/3600 + turn + 44640/3600 + turn
a = 14*(d/3600 + turn) + common
baseline = 14*(59520/3600 + turn) + common
bspan = 37*1200 + scaffold
b = 11*(bspan/3600 + turn) + common
assert bspan == 49395
assert math.isclose(a, 195.1180448888889)
assert math.isclose(baseline, 268.9797115555556)
assert math.isclose(b, 186.94221155555557)
for label, hours in (("baseline",baseline), ("v4-lean",a), ("v4-max",b)):
    print(label, "known hours", round(hours,6), "Mac days", round(hours/24,6),
          "days with 25% capacity reserve", round(hours*1.25/24,6))
for member in (1200,1500,1800):
    slots = math.floor((50400-scaffold)/member)
    span = slots*member + scaffold
    print("B sensitivity", member, slots, slots-4, round(span/3600,6),
          round((slots-4)/(span/3600),6))
print("PASS: documentary arithmetic; C_R and retries remain additional")
```
