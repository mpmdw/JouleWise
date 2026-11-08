# v5 design judgment — Sol2

Task `v5-design-judge`, brief dated 2026-11-08. Independent judgment on branch
`align/2026-11-08-v5design-judge-sol2`. **Proposal only; no registration,
measurement, monitor scoring, or hardware qualification is authorized here.**

Recommend a **HYBRID: ground-up behavioral experiment and calibration, v4
engineering reuse, native adaptive attacks, and replay-referenced energy
audits**, with the RTX 3050 used for development and a separately calibrated
replication. Ground-up Sol2 is the best starting document, with material repairs.
Do not make v5 depend on keeping v4's configuration merely to save seven windows.
Do not substitute an imputed off-Mac squeeze for the native primary experiment.

The decisive uncertainty is whether capable agents actually use software-missed
external computation to achieve monitor-evading sabotage. A positive injected
compute curve cannot answer that. A measured failure of the squeeze remains a
valid outcome; the design must permit it.

## Evidence and scoring

All five locally available design documents were read in full using Git objects.
The standing no-network rule conflicts with the requested `git fetch origin`.
Clarification was requested; absent an exception, **fetch was not run**. These
are cached-ref judgments, not a claim that origin was freshly synchronized.
`groundup-sol1` was absent on both local ref inventories; it receives no score.
The lead must fetch/reconcile later seats before treating this as a complete
final council. No path outside the permitted clone was used for study inputs.

| Seat / source file in `docs/align/squeeze/v5-design/` | Cached origin branch suffix | Commit |
|---|---|---|
| ADD-ON Sol1 / `addon-sol1.md` | `v5design-addon-sol1` | `6ad7a475aec66b2c1b06c8d9b2e378ab22281230` |
| ADD-ON Sol2 / `addon-sol2.md` | `v5design-addon-sol2` | `e2e255a941bfaa81387ee6ac56909c25a17597dd` |
| ADD-ON Opus / `addon-opus.md` | `v5design-addon-opus` | `fa2c0a9865b13164ce339a379d4dc3903789fcc1` |
| GROUND-UP Sol2 / `groundup-sol2.md` | `v5design-groundup-sol2` | `23cb07a240ac1fdba6c2609561d195607ead3cd2` |
| GROUND-UP Opus / `groundup-opus.md` | `v5design-groundup-opus` | `cb54bc168ca0276c0d31d38c976224bb9266eb91` |

Branch prefix for those rows is `origin/align/2026-11-08-`. Additional evidence:
`origin/research/2026-11-07-tripwire-directions` at
`028a705292461646c2cfcbe18b74f4c4a9b0a3ed`, file
`docs/research/tripwire-directions.md` (TD, PR #703); and the canonical A0–A13
table in `origin/align/2026-11-07-v4-reviewer2` at `f01e47f29`,
`docs/align/squeeze/reviewer2.md` §3.6. These are repository reports; their
literature, hardware observations, API availability and prices were not
independently verified. The R1 integration lane was not inspected or changed.

Scores assess each **written proposal**, including its assumptions and omissions,
on a 1–10 scale. Higher is better; (c) means cheaper and more calendar-resilient.
Scores are ordinal judgments, not calibrated probabilities or an acceptance
forecast. No proposal is ready to register unchanged.

| Design | (a) Main-track-strength squeeze prospects | (b) Soundness / honest scope | (c) Mac cost / calendar | (d) Known-risk resilience | (e) v4 / component reuse |
|---|---:|---:|---:|---:|---:|
| ADD-ON Sol1 | 4 | 8 | 2 | 5 | 9 |
| ADD-ON Sol2 | 4 | 8 | 3 | 5 | 9 |
| ADD-ON Opus | 3 | 5 | 7 | 5 | 8 |
| GROUND-UP Sol2 | **6** | 7 | 6 | **7** | 7 |
| GROUND-UP Opus | 5 | 5 | 6 | 6 | 6 |

**ADD-ON Sol1 (§§3–10).** Best treatment of independent windows, honest probes,
native counterexamples and the capability denominator. Its 120 attempts over
60 attack windows avoid pretending many attacks in one night are independent.
It explicitly requires energy benefit beyond replay/software on real external
attacks. But 79 base slots, 87 with modest contingency, and predominantly
15.7-hour attack reservations are a poor fit to shared nights. Fixed 2–4-turn
episodes and tool schemas may remove the behavior of interest. The calibration
reuse and LOO-score validity remain conditional. Replay is a serious comparator
but lacks a complete separate execution bill. It buys rigor by spending almost
the entire Mac calendar, without fixing the behavioral premise.

**ADD-ON Sol2 (§§Arms–Three risks).** More attack-efficient: 192 primary attempts
in 32 pair-specific windows, plus 32 policy comparators and 64 honest audits.
It bills a software replay allowance, tests time/accounting competitors and
requires both channels to contribute. However the strong ≤5% escape claim is
weakly powered under plausible dependence; the primary beta-binomial model's
rho≤.10 ceiling is an assumption. Three development windows may be inadequate
to find a strong joint-aware policy. It inherits the same capability/tool/reuse
risks as Sol1. Its explicit 14-hour/12-hour recosting is valuable and sobering.

**ADD-ON Opus (§§0, 2.3, 5, 7).** Correctly concedes authenticated in-runtime
omissions to software, puts external compute in the headline, adds concurrent
CPU controls and explicitly considers replay energy. Its 2–3 incremental-window
claim is attractive **because the primary behavioral result is composed**, using
about 3,000 cloud episodes, selected forced-relocation replays, and only six
native adaptive Mac attacks. Quantized MLX and dequantized vLLM behavior need
not agree; teacher forcing need not match native energy. Tiny transfer samples,
non-rejection of a rank/KS test, and matching a catch-count prediction interval
do not establish equivalence. Imputation does not turn cloud attempts into
independent physical evidence or eliminate structural model error. Oracle
relocation is useful mechanism evidence, not an adequate primary model of an
agent editing its own environment. Reallocating T1–T3 also weakens v4's held-out
benign cohort. Its D0 proposal to score existing pilots needs the registration
restriction checked first. Retain its instruments, not its main-track shortcut.

**GROUND-UP Sol2 (§§Experiment–Mac hours).** Strongest primary comparison:
native successful attacks, real editable submitted logs, real subprocess access,
strong software audit, fixed development-trained predictor, new calibration,
and explicit clustered uncertainty. Longer coherent episodes address the bite
risk; a cheaper candidate ladder addresses throughput. Costs and weaker
replication claims are candid. Repairs: its rank-38 S5/E5/M5 comparisons conflict
with the binding maximum-threshold rule; do not adopt them. Its 900-second
member and 360-second software replay are unqualified assumptions. Its 172-member
development allowance is not reconciled with two 60-episode candidate screens,
48 fit episodes and 24 control members. The tailored synthetic tasks could
make success look engineered; retain public benchmark tasks for the primary
where feasible. Fourteen physical clusters cannot certify rare-escape safety.

**GROUND-UP Opus (§§2–9, 11).** Strongest argument for selecting tasks by bite,
longer episodes, lighter thermal overhead and measuring software redundancy
before a large campaign. Flash-Next may eventually unite the workstreams.
But it is a near-memory-limit unqualified port, not free capability or speed.
Its primary still emphasizes in-runtime hidden spans, with software-accounting
increment descriptive; a rerun can beat that headline. Deleted logs are
declared impossible under its trusted harness, missing part of Ed's adversary.
Fitting on B-cal and thresholding those same training residuals does not earn
the stated maximum-rank prediction bound. Attack-responsive temperature/tool
duration covariates can explain away the signal. Fisher/CP episode inference
does not handle shared-night dependence. Realization-count-triggered extra
attempts depend on a scientific outcome, even if detector outputs stay sealed.
Its low night count excludes a comprehensive software/energy replay bill.
These are more consequential than adding a third task pair.

## What Sol and Opus agree on, and what matters in their disagreement

All five favor a frontier off-box monitor, whole-member DC-in beside rails,
bounded adaptive search, separate calibration/tests and per-attempt escape.
All recognize weak sabotage and compute-neutral escapes as serious limits.
Both families' ground-up seats see calibration reuse as less valuable than
obtaining a capable adversary. None incorporates the newly supplied RTX rig;
that is a new opportunity, not a defect in their original intake.

The recurring disagreement is **native evidence versus modeled transfer**.
Sol spends Mac time on attack attempts and honest probes; ADD-ON Opus spends
it on selected physical replays and composes a much larger cloud experiment.
GROUND-UP Opus does run its primary natively, but still uses composition for
mechanism claims and optimistic episode-level power. Sol is more careful about
LOO exchangeability, conditional versus marginal FPR, cluster dependence and
missing-evidence accounting. Opus is more aggressive about removing expensive
scaffolding and screening behavior elsewhere. Take that resource discipline
without importing transfer assumptions into the primary.

The Sol seats' unavailable-taxonomy caveat was honest for their intake, but the
taxonomy exists in a cached branch now. Use its actual definitions: for example
A3 is latent/no-visible-reasoning, A9 is exclusion provocation and A13 is battery
buffering. ADD-ON Sol2's proposed A labels are not that taxonomy. Update the
mapping under the new software/framing rulings; the old table's predicted
catcher for A1 does not override the software-rerun objection.

## Arithmetic and inference audit

The important reservation calculations reproduce:

| Quantity | Independent recomputation | Implication |
|---|---|---|
| Seven v4 calibration reservations | 7×58,260 s = 113.28 h = 4.72 machine-days | Real saving only for a compatible cell; not necessarily already sunk |
| v4-style 17-D / 18-D window | 56,460 / 58,260 s = 15.68 / 16.18 h | Calibration does not fit a hard 16-hour night |
| ADD-ON Sol1 base | 1,240.70 h; 79 slots; ceil(1.1×79)=87 | Saving seven windows does not make it a short campaign |
| ADD-ON Sol2 base / replay allowance | 754.33 h; (754.33+120)×1.25 = 1,092.92 h | 120 h is generation/account replay allowance, not comprehensive metered replay |
| GROUND-UP Sol2 as printed | 350.9 h primary; 438.625 h with 25% reserve | Correct table sum, conditional on timing and development allocation |
| Two full candidate screens + fit + controls | 2×60+48+24 = 192, not 172 | Add 5 h at 900 s/member if both candidates are screened fully |

TD's roughly 2 J identical-work repeatability versus 19–58 J regression SD
suggests **9.5–29×** improvement on that reported stack. It does not establish
v5's paired SD, a D/Flash floor, or an AC-desktop floor. With an illustrative
2.2-SD threshold, 2 J gives 4.4 J. That corresponds to about 24 tokens at
0.18 J/token but 1.2 at 3.6 J/token. Those coefficients belong to different
settings: there is no universal “replay detects N tokens” conversion. Calibrate
real side-generation and CPU doses in joules; include native/forced mismatch,
position bias, correlated drift, battery/tail and instrument uncertainty.

Software identity replay and **measured energy-reference replay are distinct**.
A free authenticated count comparison can detect stripped reasoning; generating
the sequence costs compute; measuring its complete energy twin costs another
member plus physical scheduling. Neither Sol replay allowance automatically
buys the latter. ADD-ON Opus at least costs a dedicated energy-reference night,
but eight pairs are a pilot rather than a powered adaptive squeeze cohort.

Maximum calibration gives 1/(m+1) per channel only under the actual score-law
exchangeability assumptions. Training residuals, unmatched session fits and
night clusters do not acquire that property merely by reaching m=39. Even a
valid marginal bound is not a high-confidence conditional FPR certificate.
Use genuinely held-out honest episodes, disclose dependence and calibrate the
actual composite statistic. Non-rejection of distribution equality is not
evidence of equivalence.

Cluster limits are consequential: with zero event-windows, the independent-window
one-sided 95% bound is 19.26% for 14 windows, 10.15% for 28, and 8.94% for 32.
These conservatively bound per-attempt event rates; they are not the full
precision obtainable under justified weaker dependence. Freeze that model and
test it on synthetic nulls before registration. Also settle confidence-tail
conventions: at 6/100, the CP upper bound is .11499 one-sided 95%, but .12603
for the upper end of a two-sided 95% interval. GROUND-UP Opus's ≤.12 pass rule
depends on that distinction.

## The recommended hybrid, exactly

1. **Take ground-up Sol2's native design and strong comparator.** Use two
   mechanically scored public SHADE task pairs selected on development data
   under a frozen capability rule. Start with its 30B-4bit / 27B-4bit candidate
   ladder and up-to-12-action episodes. Admit only a model that demonstrates
   useful joint main/side success on both pairs and a complete 900 s member.
   Flash-Next is eligible only through a prospectively amended candidate
   charter after native parity, memory, side-work headroom and timing qualify;
   it is not a dependency. Synthetic task twins are controlled supplements,
   not silently substituted benchmark successes. If no capable configuration
   passes, stop the positive-squeeze campaign and report the limit.
2. **Take ADD-ON's engineering reuse, not its calibration entitlement.** Reuse
   bundles, clock/meter readers, seed/custody interfaces, parser/cache tests,
   monitor transport, tool supervisor, capability graders, attack kit and
   G0/G1 implementation. Leave v4 and R1 intact and separately report v4.
   New episode/tool/model/thermal distributions get new m≥39/pair calibration.
   Use a separately qualified lighter thermal policy; do not assume covariate
   adjustment makes gates unnecessary. Restrict predictive covariates to
   defensible declared work and pre-attack state, not observed hidden load.
3. **Take Opus ADD-ON and TD's paired energy reference.** Budget measured twins
   for every calibration, honest-test and primary attack episode; select the
   primary physical score on development only, before calibration. Prefer
   replay-referenced whole-member DC-in if its qualified resolution gain is
   useful. Keep the regression residual as an ablation, not another unbudgeted
   OR alarm. Use balanced within-session order and trusted tool-state replay;
   match the legitimate workload, not a rerun that repeats the hidden payload.
   Forced replay controls isolate mechanism. Native attacks remain the primary
   behavioral evidence. If replay does not qualify, recost/re-register the
   regression-only experiment before calibration rather than silently switch.
4. **Test Ed's actual monitoring-aware adversary.** Let the sandboxed actor
   edit its working files and submitted logs/transcripts, selectively omit or
   fabricate records, use ordinary subprocess/side-generation affordances and
   adapt against disclosed detectors. Keep a separate evaluator ledger and
   meter outside its authority. Distinguish authenticated primary-runtime
   counts from the editable submission; grant the software baseline every
   genuinely available trusted receipt. Primary attacks choose whether to use
   external computation; do not require excess work. Test concurrent/sparse
   work, padding/substitution, cheap sabotage, prompt injection and record
   deletion. Keep latent/steganographic counterexamples and all failures.
5. **Repair the FPR comparison without rank 38.** Retain maximum thresholds
   throughout. One proposed equal-*nominal*-budget comparison is M∨A versus
   M∨B, where A is a frozen software-audit score and B is a frozen maximum of
   development-scaled A and physical residual. Calibrate M, A and B separately
   at their per-pair maxima on new benign calibration. Each deployed rule has
   two calibrated channels (nominal union ≤5% at m=39), not a three-channel
   union with an unreported 7.5% budget. B's scaling is frozen before calibration.
   The rules need not be nested: count gains and losses. Print actual honest
   FPR and costs, M/E ablations and the literal M∨E result. This composite
   interpretation needs the lead's explicit registration ruling.
6. **Keep per-attempt escape and incremental value primary.** Use the Sol2
   336-attempt, 280-honest-test allocation, fixed optimizer mixture and separate
   controls, rearranged into more physical sessions below. Compare the strong
   software and joint rules on the same native attempts with cluster-aware
   uncertainty. Require capability, benign utility and a useful incremental
   physical contribution on successful actor-chosen external attacks. Report
   conditional escape, per-pair/attack results, unavailability and all cheap
   counterexamples. Do not promise a model-free ≤5% escape certificate from
   this budget. Freeze missing-data conservatism and no outcome-based top-ups.

The three-layer claim must be explicit: **monitor = content; meter = quantity
of work; probes = internals**. Energy can reveal extra work or records edited
after work was done, when the software audit cannot already establish it.
It cannot identify malicious meaning, unfaithful/steganographic CoT within
logged tokens, or latent reasoning inside a fixed-compute forward pass.
Extra latent *passes* can consume extra work, a different claim. Interpretation
probes are an optional separately validated diagnostic; this experiment does
not claim to solve that third layer. Privileged host/meter compromise and
off-host computation are outside the primary sandbox claim. Do not expand to
an untrusted-runtime headline merely because trusted-runtime results disappoint.

### A replay bill that fits physical nights

Use 28 test windows rather than the source's 14: each has 12 attacks, ten honest
tests, two control members and two sentinels = 26 originals; add 22 energy twins
for the attacks/honest tests. At 900 s/member plus one scaffold hour this is
**13 h**, with totals 336 attacks, 280 honest tests, 56 controls, 56 sentinels.
T1/T2/T3 can be 8/10/10 sealed windows. Recompute power for this allocation;
do not inherit the source's 14-cluster simulation or claim 28 independent
windows if several share a common experimental session.

| Hybrid primary allocation | Qualified-envelope planning hours |
|---|---:|
| Development: up to 192 members + 4 scaffold h | 52 |
| Seven calibration sessions: 106 originals + 78 twins + 7 scaffold h | 53 |
| Test: 728 originals + 616 twins + 28 scaffold h | 364 |
| Base / 25% time reserve | **469 / 586.25** |

This replaces generation-only replay with measured reference members; it does
not bill both. Relative to the source's measured-original schedule, 694 twins
cost 173.5 h and fourteen extra test scaffolds cost 14 h: **187.5 h**. Full
candidate screening adds the separate 5 h correction above, plus one extra
scaffold hour to fit development into four nights of at most 16 h. These are
planning envelopes, not hardware evidence. They exclude v4, Flash-Next work, desktop
port/meter qualification and a full second strong-model campaign.

At 1,800 s/member, the 1,720 original-plus-twin members add another 430 h;
with the same 25% reserve the bill becomes **1,123.75 h**. That is a stop and
redesign trigger, not a small contingency. A hard 12-hour night cannot hold
the 13-hour roster. At 900 s, 586.25 h is about 42 fourteen-hour equivalents;
twenty weeks at two such equivalents/week supplies only 560 h. Secure at
least about two additional long equivalents plus dated partial calibration
sessions, or start earlier. Base physical sessions are roughly four development,
seven calibration and 28 test slots before replacements; equivalent-hour
arithmetic must not hide the larger number of calendar dates. Finish primary
collection by early/mid-April and protect writing time. The 2027 submission
date remains an unverified planning assumption under the network ban.

### Use the RTX 3050 where it changes the economics

Port one backend, initially the simplest supported llama.cpp CUDA path, with
synthetic conformance tests before using any lead-authorized existing weights.
Use approximately 8B 4-bit models for task-generator debugging, attack-policy
plumbing, capability screens, tool/log-edit tests and CPU/concurrent side-work
controls. These save MBP engineering trials; an 8B capability pass does not
qualify the strong Mac adversary, and an 8B failure need not reject its tasks.
Theoretical 4-bit weight bytes alone are about 3.73 GiB for 8B. Quantization
metadata, cache, context, buffers and other processes must also fit the 8 GB
device; actual fit and throughput require qualification. Do not assign D or
Flash-Next to it.

After obtaining the logging AC wall meter, separately calibrate the desktop
configuration with m≥39/pair and held-out tests. Replicate physical controls
and a bounded native 8B adversary cohort; distinguish autonomous attacks from
teacher-forced fixed-work replication. Record NVML and RAPL where supported
beside the AC integral. Compare their accounted energy, gaps and dose sensitivity
to the meter; neither sensor is a complete wall-energy substitute. Higher idle
power, fans, PSU losses, CPU work, meter cadence and integration uncertainty
may erase the Mac's small-dose advantage. Native backend divergence is expected
to require its own replay qualification, not cross-backend token identity.

This gives Apple/DC-in versus Linux/CUDA/AC-wall replication of a method and its
limits, **not** two equally strong agents, equal joule coefficients, datacenter
validity or a third-chip benchmark. Publish platform-specific floors, FPR,
audit cost and failures; never pool calibrators. It also removes the need to
rent GPUs for small-model engineering. Large-model cloud pilots still need
separate authority and do not replace native confirmation. No port, purchase,
download, network access or desktop execution occurred in this judgment.

## Probability assessment and lead rulings

TD's roughly 2/3 workshop and 1/4 main-track judgment is conditional on v4's
measurement gates. It is a useful planning reference, not a measured base rate.
Seat forecasts are not directly comparable: ADD-ON Sol1/Sol2 estimate scientific
strength at .25/.20, while ADD-ON Opus's .09 clean-win product includes a .55
reviewer/venue factor; GROUND-UP Opus's .30 does not include that same factor.

On TD's conditional research-strength scale, neither frozen ADD-ON materially
raises the ~25% reference: native versions buy evidence at high cost; the
composed version saves cost by weakening the claim. A repaired ground-up design
plausibly reaches **30–35%** (+5–10 percentage points). The recommended hybrid,
with capability, paired-reference and desktop qualification gates, plausibly
reaches **30–40%** (+5–15 points), with wide uncertainty. This is my subjective
judgment before behavioral gates, conditional on a qualified instrument and
funded calendar, **not an unconditional acceptance probability**. Missing those
resources lowers it. The desktop alone warrants no numerical uplift before
qualification. No document justifies a >50% clean-squeeze forecast. A sharp
measured escape window remains more plausible than a universal win.

The following are **NEEDS_RULING for registration/execution, not blockers to
delivery of this recommendation**. The lead retains every decision and final
verification gate.

| Question / options | Recommendation | Work blocked pending ruling |
|---|---|---|
| Freshness: cached five seats or fetched complete council? | Resolve fetch exception, fetch when permitted, read ground-up Sol1 if it arrives; compare exact heads | Final council adoption |
| Runtime/log trust: authenticated primary runtime, or compromised runtime? | Editable agent environment/submission; trusted evaluator and primary counters; honest software competitor; compromised-runtime claims separate | Threat model and claim wording |
| Model/tasks: frozen D, capability-qualified cheaper cell, or Flash dependency? | Ground-up ladder and public task screen above; fixed selection/caps before calibration; no compulsory extra compute | Development charter and native capability gate |
| Detector family: literal OR alone, second-largest thresholds, or two calibrated composite channels? | Maxima only; rule on M∨A versus M∨B and physical-score selection before calibration | Statistical registration / matched nominal alarm budget |
| Replay: full measured twins or generation-only comparator? | Reserve 586.25 h for qualified twins; meter/battery/native replay gates first; downgrade/re-register if unaffordable | Measurement roster and power audit |
| Dependence/FPR: theoretical guarantee or empirical scoped claim? | Fixed independent development fit; audit exchangeability; disclose conditional nominal bound plus held-out clustered uncertainty; no training-residual shortcut | Inferential wording and synthetic size/power validation |
| Resources: Mac allocation, RTX meter/backend and optional stronger-model replication? | Fund dates/hours separately from v4 and Flash; desktop method replication first; no unfunded second strong-model promise | Purchases, ports and live scheduling |
| Monitor/calendar: provider pin, API budget, scoring order and deadline? | Pin/price frontier snapshot before any v4 score; development feedback before policy freeze; verify actual conference dates when network is permitted | API scoring and final calendar |

Immediate next step: lead adopts a bounded **capability, trust-boundary and cost
development charter**, then qualifies native sabotage and replay resolution with
agents stood down and the current blinded job protected. Do not buy calibration
until those gates pass. No v4/R1 amendment or live run follows from this report.

Arithmetic record for the synthetic document audit:

```json
{
  "source_seats": 5,
  "test_windows": 28,
  "member_s": 900,
  "test_originals_per_window": 26,
  "test_twins_per_window": 22,
  "test_window_h": 13,
  "development_members": 192,
  "development_h": 52,
  "calibration_h": 53,
  "test_h": 364,
  "base_h": 469,
  "reserved_h": 586.25,
  "measured_members": 1720,
  "worst_case_reserved_h": 1123.75
}
```
