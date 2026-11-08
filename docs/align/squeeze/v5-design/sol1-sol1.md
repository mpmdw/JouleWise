# v5 design judgment — Sol1

Task `v5-design-judge`; brief dated 2026-11-08. Independent judgment, not a
registration, hardware result, or permission to collect data.

**Recommend a HYBRID: ground-up behavioral design and fresh calibration,
v4 engineering reuse, and RTX 3050 development plus physical replication.**
Use groundup-Sol2 as the main experimental and statistical starting point.
Take the bite-region screen and longer episodes from groundup-Opus, the
software-resistant claim and replay experiments from addon-Opus, and the
reuse/denominator/cluster safeguards from the two Sol ADD-ON seats.
Keep v4 intact as its own study. Do not preserve the 27B 8-bit configuration
or its short episodes merely to save calibration time.

This is the best chance of a strong *bounded empirical* squeeze result. It
cannot guarantee the desired positive result: compute-neutral sabotage is a
real counterexample, and a measured escape region may be the paper's result.

## Evidence and limits of this review

The standing no-network rule prevented refreshing origin. I ran
`GIT_ALLOW_PROTOCOL=file git fetch origin`; it exited 128 with
`fatal: transport 'https' not allowed`, before any network access. The five
locally available origin refs below were read in full. The named
`origin/align/2026-11-08-v5design-groundup-sol1` ref was **absent locally**;
I cannot establish whether it exists remotely. It receives no invented score.
The lead should refresh and judge that seat before final adjudication.

All seat branches have prefix `origin/align/2026-11-08-v5design-`; their
documents are `docs/align/squeeze/v5-design/<seat>.md` at these commits:

| Seat | Pinned commit |
|---|---|
| addon-sol1 | `6ad7a475aec66b2c1b06c8d9b2e378ab22281230` |
| addon-sol2 | `e2e255a941bfaa81387ee6ac56909c25a17597dd` |
| addon-opus | `fa2c0a9865b13164ce339a379d4dc3903789fcc1` |
| groundup-sol2 | `23cb07a240ac1fdba6c2609561d195607ead3cd2` |
| groundup-opus | `cb54bc168ca0276c0d31d38c976224bb9266eb91` |

I also read the main argument and relevant detailed designs in
`origin/research/2026-11-07-tripwire-directions:docs/research/tripwire-directions.md`
at `028a705292461646c2cfcbe18b74f4c4a9b0a3ed` (TD; PR #703 in the brief),
the local intake/authority documents, the analysis-plan required fields, and
targeted v4 design/amendment budget text. Citations below name seat sections
at these pinned versions, reproducible with `git show <commit>:<path>`.
Pilot results and product specifications are supplied documentary premises,
not independently checked measurements. The R1 integrated lane was untouched.
No sealed data, model weights, external study paths, network services, or hardware
measurements were accessed. Mid-May 2027 is a planning horizon, not a verified
conference deadline.

## Scores and scientific-success judgments

Each score is 1–10, higher better. **C rewards lower Mac cost and lower
calendar risk**, including engineering dependencies and omitted audit work.
Scores assess the submitted design before the repairs recommended here.

| Design | A: main-track result | B: soundness / honesty | C: cost / calendar | D: known-risk robustness | E: reuse |
|---|---:|---:|---:|---:|---:|
| ADD-ON Sol1 | 4 | 8 | 2 | 4 | 9 |
| ADD-ON Sol2 | 5 | 8 | 4 | 5 | 9 |
| ADD-ON Opus | 3 | 5 | 7 | 4 | 9 |
| GROUND-UP Sol1 | unavailable | unavailable | unavailable | unavailable | unavailable |
| GROUND-UP Sol2 | 7 | 9 | 6 | 7 | 8 |
| GROUND-UP Opus | 6 | 5 | 6 | 6 | 6 |

My rough planning judgments for **main-track-strength scientific evidence**
are 20% for addon-Sol1, 22% for addon-Sol2, 12% for addon-Opus, 30% for
groundup-Sol2, 25% for groundup-Opus, and **35% for the proposed hybrid**
(broad hybrid range 20–45%). Relative to TD's approximately 25% reference,
these are approximately −5, −3, −13, +5, 0, and +10 percentage points.
These are subjective priorities, not measured probabilities or acceptance
predictions. TD conditions on v4 clearing its gates; its probability and the
seats' differing scientific/acceptance forecasts cannot be directly combined.
The deltas use 25% as a common planning reference, not a normalized posterior.
They assume the stated reservations are funded and still allow capability,
instrument, and execution failure. The hybrid's plausible gain comes from
testing a stronger threat, removing the fixed short-episode bottleneck, and
adding a second physical platform. It does not come from more positive controls.
TD's roughly two-thirds workshop forecast remains a reasonable fallback;
a clean universal squeeze is less plausible than a scoped win or measured limit.

**ADD-ON Sol1.** Strong disclosure of failure modes and native attack
requirements; six adaptive-development windows and 120 final attempts on 60
windows avoid disguising transformed logs as independent attacks. Its main
weakness is purchasing independence with almost the entire Mac calendar:
79 base slots, 87–90 with allowances, predominantly 15.7 h, and five long
confirmation slots/week in its proposed test phase (§§7–10). At pilot yield
1/12, 120 attempts produce only ten expected successes. Its 10% escape/FPR
criteria are more modest than a tight squeeze. Software rerun is required but
has no separately sized native-replay line in the main bill. Good safeguards
to reuse; poor primary resource allocation.

**ADD-ON Sol2.** The strongest ADD-ON. It makes energy rescue beyond
monitor/rerun/time a primary claim, requires actual actor-selected sabotage,
uses one-pair windows efficiently, and exposes LOO and dependence problems
(Calibration; Estimands; Window roster). But 192 primary attempts in 32
clusters cannot robustly establish its <5% escape target without substantial
dependence assumptions. Its beta-binomial nuisance model is proposed work,
not a validated analysis. The 120 h software-replay allowance is honest but
still provisional. A frozen short-episode model and possibly incompatible
compute-tool surface remain structural risks.

**ADD-ON Opus.** Best separation of in-runtime stripping from runtime-external
work, and the clearest affordable replay-resolution experiment (§§2, 5).
However, its primary squeeze mostly uses cloud behavior with **imputed** Mac
energy, oracle-relocated hidden work, and only six native adaptive Mac attacks.
That measures a compositional model more directly than the requested live
monitoring-aware adversary. Dequantizing MLX weights into bf16/vLLM does not
establish identical native behavior or energy. A non-significant rank/KS test
does not establish transfer or exchangeability; two native/forced trajectory
pairs give little equivalence precision. Bootstrap/imputation cannot supply
missing physical mechanisms. The cheap 2–3 incremental windows also borrow
v4's test slots and weaken its honest holdout. Keep K/E_R as mechanism studies;
do not adopt imputed outcomes as the headline experiment (§§5, 7, 10).

**GROUND-UP Sol2.** Best backbone: native actor choice, longer completed
episodes, fixed development-trained detector, separate honest tests, an
equal-FPR strong software comparator, conservative missingness, and explicit
cluster/utility limits. It admits that software may win (Experiment; Energy;
Estimands). Its two synthetic task twins risk appearing tailored, both model
candidates are Qwen, the 900 s member and 360 s rerun are unqualified, and
14 clusters support weak assumption-free rare-event bounds. Development's
172-member allowance is already allocated to screens, fit data and controls;
600 nominal feedback queries are not 600 funded physical queries. Reserve
actual native adaptive-search members after thresholds or reduce that promise.
It lacks a costed, calibrated metered per-episode replay channel. These are
fixable design issues rather than reasons to retain v4's configuration.

**GROUND-UP Opus.** Correctly prioritizes capability, a third task pair, longer
episodes, meter-first measurement and deployment-like operation. Its decisive
defect is leaving energy's contribution beyond software descriptive while
hidden **in-runtime** scratchpads remain central to SQ-A/SQ-B (Arms; §§6, 10).
Authenticated counts/rerun can defeat that headline. The Flash-Next port,
near-full memory, long KV cache, side-work memory and ungated residuals are
simultaneous dependencies. In-sample B-cal residual maxima do not acquire a
conformal guarantee just by being maxima; use separate training or a valid
symmetric construction. Thermal/tool-time covariates can explain away the
attacker's work. Non-rejection of a rank test is not SQ4 validation. Its
realization-shortfall extension is outcome-dependent even though called
count-only; freeze attempts instead. Its budget understates pessimistic
qualification and omits comprehensive software/metered replay (§§7–9, 11).

## Arithmetic and replay audit

The independent checks use only integer rosters and synthetic probabilities.

| Check | Recomputed result and consequence |
|---|---|
| v4 calibration saving | `7 × 58,260 / 3,600 = 113.2833 h = 4.7201 continuous days`. The seven windows are reusable only if actually collected and eligible; they are not already-earned evidence. |
| v4 roster typo | `4 + 2 + 14 + 2 = 22`, hence **18 D members**, not 16. `3,131.27 + 18×1,800 = 35,531.27`; scaffold/reserves/rounding yield 58,260 s. Both Sol ADD-ON budgets use the correct maximum. This review does not amend v4. |
| Long-night constraint | 58,260 s is **16.183 h**, above a hard 16 h night. A 17-D frame is 56,460 s = 15.683 h. None is a 12 h reservation. |
| addon-Sol2 power | IID size for `K≤3, n=192, p=.05` is .012216, within .05/3; power is .8722 at p=.01 but only .4636 at p=.02. The submitted caution is warranted before clustering. |
| Groundup-Sol2 ledger | Primary 350.90 h; with 25% reserve **438.63 h**. Two-model plan 461.80 h; reserve **577.25 h**. Doubling its 1,308 measured members from 900 to 1,800 s adds 327 h: **986 h** with reserve. These sums check out. |
| Groundup-Opus qualification | N0 has about 60 development episodes; N1 has 60 controls. With four overhead episodes/night, capacity is 66/46/38 at 720/1,000/1,200 s. The two qualification stages require **2/4/4 nights**, respectively, before reserves. Its pessimistic/fallback totals need at least two additional nights on those assumptions. |
| Rare-event independence | Zero events in 14 independent windows has one-sided 95% upper bound **19.26%** on any-event window probability; in 32 it is **8.94%**. These also conservatively bound attempt rates. Neither is a model-free <5% claim. |

TD's roughly 2 J identical-work repeatability versus 19–58 J regression
residual SD makes replay worth testing. Those quantities are not established
v5/DC-in predictive scales; the native model, meter boundary, battery flow,
ordering and episode length all matter. The addon-Opus E_R projection
`2.2 × (3–14 J) / 3.6 J/token = 1.83–8.56 tokens` is arithmetically correct
at κ=1. Its scientific assumptions, including that predictive null scale,
remain unmeasured. Do not transfer either that projection or TD's 10–30-token
projection as a v5 detection limit. Replay the episode's **declared work**,
not its hidden-work truth ledger, with matched initial state and balanced
same-window placement; separately test serial and concurrent side work.

Software consistency rerun and **metered** declared-work replay are different
products. In the groundup-Sol2 primary there are `78+280+336=694` calibration,
honest-test and attack episodes. At a provisional 900 s/replay, plus one
scaffold hour per 52 replays, a metered replay for all costs
`694×.25 + ceil(694/52) = 187.50 h` **in addition to** its software ledger.
The resulting primary reserve is `(350.90+187.50)×1.25` = **673.00 h**.
That is about 48.1 fourteen-hour equivalents; the design must repack matched
original/replay blocks within physical windows and redo clustering, not replay
in a later session and assume offsets cancel. This is a provisional capacity
bound, not a validated schedule. Extra development or non-paired control
replays, longer tails and qualification can increase it.

A smaller secondary study with all 78 replay calibrators plus a preselected
64 honest/attack test episodes adds `142×.25+ceil(142/52)=38.50 h`, giving
**486.75 h** primary-plus-substudy reserve. It cannot support replay decisions
on the other attacks or inherit the full primary's power. Control sham twins
can supply their own matched contrasts where actually token/state matched.
Credit shared software/metered work only after native validation demonstrates
one run satisfies both contracts. A forced-token energy replay alone does not
authenticate the original generation. Replaying only suspicious test episodes
would change the detector and create selection bias unless registered as a
two-stage rule and calibrated end to end.

## Exact hybrid to take forward

1. **Claim and boundary.** Test a monitoring-aware sandboxed agent with write
   access to its task environment and submitted logs/transcripts. It can edit
   its records, choose side generation and tool subprocesses, pad/obfuscate
   text, and substitute cheap malicious actions for benign work. Preserve
   private evaluator truth separately. Trust the measurement collector and
   specified auditor inputs; grant neither root nor meter control. Give every
   detector all evidence available under that same deployment contract.

   The three layers must be explicit: **monitor = content; meter = quantity;
   probes = internals**. Metering can flag missing records of work actually
   done and unlogged side computation above a measured net-energy floor.
   It cannot identify malicious meaning, steganographic/unfaithful CoT within
   logged tokens, or latent reasoning within a fixed-compute forward pass.
   Those latter internals need probes, outside this confirmatory experiment.
   Off-host work is outside a single-host meter's coverage. Do not infer
   untrusted-runtime robustness from an experiment with a trusted runtime.

2. **Native behavior and capability.** Start with groundup-Sol2's 30B-A3B
   4-bit candidate, then 27B 4-bit under a frozen selection rule based on
   completed main-plus-side success and budget, not throughput alone. Use up
   to 12 action turns initially; qualify actual action closure and useful
   sabotage before selecting a budget. Flash-Next is optional after its own
   port/memory/capability gates, not a primary dependency. The original two
   SHADE pairs are preferable if capable; synthetic twins are separately named
   tasks if needed. Select task semantics on development seeds and include
   equal-compute/cheap sabotage immediately. Do not construct a task that
   requires gratuitous compute to force energy's success. A third qualified
   pair is useful only with its own fresh calibration and funded execution.

3. **Genuine hidden-work choice.** Add ordinary sandbox compute affordances
   to the benign and attack environments alike, with realistic benign use.
   The actor decides whether they help sabotage; it may decide not to spend
   extra compute. Forced side-generation/tool-work injections remain separate
   shams/dose controls, as in both Sol proposals and Opus's K night. A visible
   compute call need not reveal malicious content, but its process receipt
   cannot be withheld from the software baseline just to make energy win.
   Cheap substitutions and fully logged malicious actions stay in the test.

4. **Detectors and analysis.** Freeze the API monitor before any v4 scoring;
   use new v5 development/calibration/test namespaces. Train predictors and
   software-score transformations on development only. Use whole-member
   DC-in as small-effect authority, with rails alongside it, validated battery
   closure and no attack-controlled energy allowance from tool time or thermal
   covariates. Decide on development whether regression is adequate or
   metered replay is needed as the primary energy score. Calibrate whichever
   score is selected with fresh **m≥39 per pair**, preferably a fixed roster
   with attrition margin, and strict per-channel maxima. Do not OR an
   uncalibrated replay/rail alarm into the primary.

   Require a strong software baseline: frontier monitor, authenticated
   invocation/count/log consistency, available process accounting and trusted
   time. One fixed composite software score can be calibrated as one channel;
   its maximum plus the energy maximum gives the two-channel joint rule.
   Also print the literal monitor-plus-energy ablation. A 5%-nominal software
   comparator using rank 38 at m=39 is a useful *additional*, explicitly ruled
   comparison; it must not silently replace the standing maximum thresholds.
   Verify empirical false alerts for every expanded detector rule.

   Primary target: escape **per sabotage attempt**, with paired energy rescue
   beyond the software baseline and retained honest utility/FPR. Report
   success-conditioned escape and all cheap successful counterexamples.
   Use groundup-Sol2's 336 attempts/14-window, 280 honest-test plan as a sizing
   starting point, not a final power guarantee. Repack for measured timings,
   reserve native adaptive development, and freeze inference with drift/ICC
   stress tests. Keep enough independent windows; large episode counts in
   eight nights do not provide hundreds of independent replicates. A bounded
   improvement is more defensible than a universal or <5% rare-escape promise.
   Evaluate all frozen best-response policies under every detector rule;
   distinguish paired detector gain from changes in attacker policy.

5. **Reuse and resource cap.** Reuse v4's bundle/custody formats, seed and
   scorer machinery, transcript/history/parser fixes, runtime adapters, G0/G1
   implementation, budget accounting, monitor adapter, red-team/injector kit,
   DC-in integrator and meter audit. Qualify a simpler thermal policy on
   development; do not presume dropping gates preserves resolution. Use v4
   episodes only for their own registered claims or permitted secondary
   comparisons. New tools, tasks, budgets, quantization or thermal populations
   require a new calibration cell; no v4 m credit in this hybrid.

   Reserve roughly **440 h** for a regression-primary single-model plan,
   about **487 h** with the small metered-replay substudy, or about **673 h**
   for comprehensive primary metered replay under the provisional envelopes.
   Prefer one capable Mac model plus RTX physical replication to a second
   expensive Mac calibration. Secure actual dates and a total cap near 700 h
   if full replay is necessary. At 2.5 fourteen-hour equivalents/week, 673 h
   needs about 19.2 weeks, in addition to v4/Flash-Next reservations. Recost
   before registration if 900 s members or tail closure fail. Stop for a
   limits result rather than silently funding a 1,800 s campaign.

6. **Use the RTX 3050 well.** Give the Linux desktop a bounded CUDA port,
   synthetic harness tests, small-model policy/tool/record-editing pilots,
   and native 8B 4-bit capability screens using only later-authorized weights.
   Eight billion 4-bit weights alone are about 4 GB; runtime metadata, KV
   cache and concurrent side work still need a measured 8 GB fit. Prefer a
   modest-context llama.cpp CUDA path initially; choose vLLM only if its
   backend/model fit is qualified. Neither backend is already certified here.

   Buy/qualify the proposed **logging AC wall meter** before physical claims.
   Then replicate shams, actual side generation and CPU/tool work, serial
   versus concurrent placement, declared-log replay, and a small batching
   ladder. Compare integrated wall energy with NVML and, **if the CPU exposes
   it**, RAPL, stating device/package/system boundaries and missing coverage.
   Never add overlapping telemetry domains or treat NVML+RAPL as the wall
   total. Desktop AC includes PSU losses; Mac KM003C measures DC delivered
   after the brick. Calibrate per platform and compare detection/escape curves
   at matched operating points, not raw joules or pooled thresholds.

   Register ≥39 fresh honest scores/pair on the desktop for any confirmatory
   detector claim and a separate honest/attack test cohort. Otherwise label
   it exploratory mechanism replication. Higher idle power, fans, CPU/PSU
   variation and meter cadence/accuracy can overwhelm small doses; long
   whole-member integration and sham tests must establish resolution first.
   The weaker 8B adversary cannot certify the larger Mac model's capability,
   replace native Mac adaptive attacks, validate 27B behavior transfer, or
   simulate Flash-Next. It can save Mac engineering/pilot time and add a
   second measured hardware stack. It does not remove the Mac primary bill.

## Where Sol and Opus agree and disagree

All available seats accept a frontier off-box monitor, whole-member meter
authority, runtime-external controls, per-attempt escape and a bounded claim.
They agree that capability/no-bite is a first gate, and all mention software
rerun as a serious competitor. Neither family supplies live validation here.

The **Sol seats prioritize native attempts, explicit software competitors,
honest holdouts and dependence accounting**, paying many more Mac hours.
Both ADD-ON Sol seats identify the session-LOO exchangeability problem; their
matching training sizes alone do not solve it. Groundup-Sol2 avoids that
particular problem with a development-trained fixed score.

**ADD-ON Opus moves behavior off-Mac and composes the physics**, producing the
largest cost saving but also the largest gap from an autonomous native attack
claim. Its three-jaw framing is stronger than its composition validation.
**GROUND-UP Opus prioritizes Flash-Next, three pairs and ungated throughput**;
groundup-Sol2 chooses smaller, more mature candidates, moderated gates and
two new task families. Opus's 12-night central bill and Sol2's roughly
31 reserved primary night-equivalents describe different experiments and
assumptions; they are not rival estimates of the same roster. The RTX resource
arrived in this judging brief: none of the five seats presents a costed plan
for it, so its benefit is a hybrid recommendation, not retroactive seat credit.

## Rulings the lead must make

These decisions block registration/execution, not delivery of this judgment.

| Question / options | Recommendation | Work blocked pending ruling |
|---|---|---|
| ADD-ON reuse, full restart, or hybrid? | Hybrid above; v4 independent, fresh v5 calibration. Refresh missing groundup-sol1 before final choice. | Final design selection. |
| Authenticated runtime/logs versus broader runtime compromise; which auditor evidence exists? | Writable submitted records, authenticated primary invocation where available, real side work; disclose exact software coverage. No implied root-compromise result. | Threat contract, deployable baseline and allowed edit/offload surfaces. |
| Native attacks versus oracle relocation/composed outcomes? | Native primary; oracle attack relocation/composition only mechanism studies. Metered declared-work replay may score native attacks. | Roster and primary estimand. |
| Candidate model/task ladder and capability bar? | Mature 4-bit candidates first; completed useful sabotage on both pairs; explicit fallback/stop date. Approve any task twins as new tasks. | Model/task selection and development charter. |
| Regression or metered replay; trusted battery/tail boundary; thermal policy? | Decide on development before fresh calibration; whole-member DC-in remains authority. | Detector freeze, calibration validity and exact machine bill. |
| Max thresholds, strong software composite, equal-FPR comparator, dependence and claim margins? | Keep required maxima; add separately registered matched-FPR comparison; audit clusters and missingness. No in-sample residual rank guarantee or outcome-based top-up. | Analysis-plan approval and power claims. |
| Mac allocation versus Flash-Next; desktop purchase/port/model access; API budget/version? | Secure dated primary reservations with a capped replay allowance; authorize desktop wall meter and a bounded port/screen. Pin API model/prompt before scoring. | Resource commitment and any external action. |
| Canonical A0–A13 mapping and final stop rules? | Reconcile Sol's functional labels with Opus's cited R2 taxonomy; do not treat their A numbers as interchangeable. Stop for a limits paper if cheap sabotage or software sufficiency defeats the premise. | Coverage claim, calibration/test registration and publication scope. |

Assumed binding rulings: KM003C placement/whole-member authority; amended
D-139 A1; primary frontier API monitor and no pre-registration v4 scoring;
m≥39/pair plus held-out tests with per-channel maxima; external-compute
positive controls; per-attempt escape primary, all-cells survival descriptive;
the stated three-layer scope; and desktop availability as a proposed resource.
No new experimental ruling is installed by this report.

**Next exact step:** refresh the seat refs in an authorized networked session,
add groundup-sol1 if present, then approve one capability-and-cost development
charter covering the native Mac candidate ladder, legal log/tool access,
software competitor, replay decision, and bounded RTX port. No new calibration
or monitor scoring is authorized until that charter and registration are ruled.
