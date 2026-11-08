# Independent Sol seat 2: hostile review of the monitor–energy squeeze

**2026-11-07 · DRAFT for lead review · desk work only.** Branch:
`align/2026-11-07-sol-reviewer2-seat2`. One Sol seat wrote all three reviewer
perspectives below; these are not three independent agent reviews. I read none
of the other squeeze seats' branches. Assume v4's instrument gates and the
planned adaptive red team succeed; the question is what a strong reviewer
could still reject. No experiment, registration, authority ruling or hardware
qualification is performed by this document.

## Executive summary

**A successful v4 plus red team could support a top-venue paper about a bounded,
joint audit, but does not establish a universal squeeze.** The missing inference
is: “plausible logged work is visible to a monitor” does not imply “the monitor
recognizes its malicious purpose.” A wrong tool argument, steganographic filler
or malicious reasoning inside ordinary tokens can preserve both a plausible
transcript and its expected energy. The repo already recognizes the
within-forward-pass limit. The paper should test this common blind spot rather
than make it disappear by defining the attack set around omitted tokens.

The publishable result would be: **under an explicit local, operator-controlled
measurement boundary and a fixed attack/search budget, adding external energy
to a frozen transcript monitor reduces successful joint evasion at a fixed
benign alarm budget.** Show the complete escape frontier, utility, audit
availability and cost. Positive-control compute and edited-log curves explain
the mechanism; they do not substitute for that result. A finite red team gives
an empirical bound against the tested search procedure, not a proof covering
all adaptive adversaries.

My simulated recommendations, even assuming positive results:

| Reviewer | Current likely vote | What would change it | Confidence |
|---|---|---|---|
| AI control / ML | Weak reject: two task pairs and a capable model do not establish control efficacy | Success-conditioned and unconditional joint evasion; capable attacks with main-task utility; common-blind-spot attacks; held-out task/attacker evaluation | High on objection; medium on eventual vote |
| Security / side channel | Reject if called tamper-proof, datacenter-ready or complete | Explicit attacker permissions, independent DC capture/custody, matched-budget adaptive attack search, evidence about low-energy and same-compute attacks | High on objection; medium on achievable scope |
| Statistics / measurement | Weak reject if “m ≥ 39” is advertised as a validated 5% joint FPR | One frozen joint decision rule; a justified calibration construction; independent benign tests; multiplicity, exclusions and window dependence handled prospectively | High |

The cheap, urgent changes are the threat game, monitor visibility, estimands,
joint false-alarm rule and data split. The expensive changes are independent
benign tests, many genuinely successful sabotage attempts, and replication.
Preserve v4 as an instrument study if those costs cannot be met; narrow the
paper's rates and scope rather than promote exploratory successes to guarantees.

## Source pins and precedence

Every citation below has `commit:path:line` form; ranges refer to that immutable
blob, not the current working tree. Full pins:

| Source | Commit |
|---|---|
| Agenda / research page / local base | `be3cc8b680cde290299aeb8d198de73993fe38b2` |
| v4 R1 integrated protocol, implementation and chair | `e901eb2a480d51377a494be9d797733dfcd0220b` |
| Literature synthesis | `16e1db6230a80a605d084f0f9f61431d541b793f` |
| W1 pre-arm audit | `53a2305982a551ba5285e50bd0177726b5f138e7` |
| Research-program audit | `7f74dd2a97e5fcf078652deef2fb291929dc4524` |
| Imported calibration script | `7fbd95e311f31f3be82839225620a7fcdacdcd69` |

The later agenda owns the assigned objective: v4, adaptive red team and a top
main-track target (`be3cc8b68:docs/research/AGENDA.md:5-16`). Earlier research
advice to make v4 a journal extension, defer the external meter, or remain
non-adaptive is advice, not a superseding ruling. Q4/Q6 are now described as
approved in the agenda/page; their older “unanswered” audit entries are stale
(`be3cc8b68:docs/research/AGENDA.md:16,31-32`;
`be3cc8b68:docs/research/energy-tripwire.html:198-205`). Conversely, the v4
snapshot still calls itself unregistered. This review does not certify a newer
registration or claim that old implementation blockers remain unfixed elsewhere.

Network was forbidden, so no fetch or external paper/CFP lookup was made. The
named local remote-tracking refs were present. Literature assertions below are
attributed to the supplied synthesis, not represented as primary-source checks
by this seat. No other squeeze review, design or preregistration branch was read.

## Prioritized changes before collecting the affected data

Costs are planning estimates, not measured runtimes: a desk day is about six
focused person-hours; a D member uses up to the planned 1,800 s budget, with
additional window scaffold and possible exclusions. Owners are proposed roles,
not assignments or newly registered tasks. Lanes: **A** = desk/agent;
**Q** = later agent-free measurement; **E** = Ed's hardware/authority work.
Gates: **R1** before affected rehearsal measurements; **W1** before W1 freeze;
**D** before the first affected held-out/calibration/red-team cohort. Changes
after a gate require a prospective amendment or new cohort, never a retrofit.

| Priority / finding | Add or change | Proposed owner; lane | Estimated incremental cost | Gate; confidence |
|---|---|---|---|---|
| P0 / S1 | Freeze the attack game, trusted components and capture boundary; resolve the D-139 limitation for the intended attacker | Lead + security reviewer; A/E | 0.5–1 desk day; hardware setup separately | R1 if it changes capture, otherwise W1; high |
| P0 / S2 | Qualify external DC acquisition, clock alignment, battery path and all attack placements; keep rails/DC results separate | Instrument owner + Ed; A/Q/E | 1–2 desk days; reserve 2–6 quiet hours for engineering qualification, then measured roster | R1 for native slots; W1 for boundary; D for scored controls; high |
| P0 / M1 | Specify the joint successful-evasion endpoint, utility floor, availability handling and equal-alarm baselines | Lead + control/statistics reviewers; A | 0.5–1 desk day | W1 for endpoint/split; D for final locked analysis; high |
| P0 / T1–T3 | Freeze training/calibration/test units, score algorithm, rank, joint alarm threshold, primary comparisons and stopping rules | Statistics owner + lead; A | 1–2 desk days; benign test capture cost below | W1 design; D exact identities before any test score; high |
| P0 / S3 | Red-team both channels jointly, with visible-work laundering, cost substitution, placement and low-compute sabotage | Red-team owner; A/Q | 2–4 desk days; 36-attempt screening design below costs up to 18 member-hours plus scaffold, not a confirmatory rate study | D, before attack development touches its evaluation pool; high |
| P0 / T4 | Preserve every attempted attack, X exclusion, timeout, unavailable monitor and missing meter result; separate instrument acceptance from defense success | Harness/analysis owners; A/Q | 0.5–1 desk day; no extra members if collected initially | W1 schema; D roster; high |
| P0 / T5 | Close the already-reported protocol/code/registration discrepancies at a single pinned head | Lead + existing W1 owners; A, then Q | Existing work; estimate 1–3 desk days, no new hardware campaign solely for this review | R1/W1 as owned by each ruling; high |
| P1 / T2 | Add genuinely held-out benign tests and choose the precision the paper will claim | Statistics + collection owners; A/Q | If zero alarms: 59 independent tests per claimed population for a one-sided 95% upper bound below 5%; two pairs cost up to 59 member-hours plus scaffold | D, test roster frozen before reads; high under iid assumptions |
| P1 / M2 | Hold out a third task pair or task family, including its benign calibration and adaptive attack evaluation | Task/red-team owners; A/Q | 1–2 desk days; 39 calibration + 12 attack members alone cost up to 25.5 member-hours; independent benign tests are additional | D for separate extension; medium on cost |
| P1 / M3 | Validate capability at the actual effort/budget, then replicate the primary attack/defense comparison on a second model/configuration | Model + collection owners; A/Q/E | 1–3 desk days; separate per-pair calibration/test pools, likely several windows; size using native rates | D for each new cohort; high on need, medium on cost |
| P1 / S4 | Replicate the key joint result on another physical unit or with an independent operator; add one ungated or serving-regime stress cohort | Replication owner + Ed; A/Q/E | 1–3 setup days plus separate calibration/evaluation windows; hardware/access TBD | D extension, before that cohort; medium |
| P2 / N1 | Write the novelty/assumption matrix and cost account; prepare a minimal independent recomputation package | Paper/artifact owners; A | 1–2 desk days plus replication support | D freeze for methods; before submission for artifact; high |

**Cost discipline.** These rows overlap; do not sum their desk costs mechanically.
Run a small attack screen, select the primary attack using development data,
then spend confirmatory samples on it. A blanket 5% escape claim for each of six
attack families on two pairs would need at least 708 iid zero-escape trials to
give separate unadjusted one-sided 95% bounds: up to 354 member-hours before
scaffold, benign tests or multiplicity correction. That is a different project
from 36 screening attempts. A preregistered mixture can support a mixture-average
claim at lower cost; it cannot establish a worst-case guarantee per family.

## Reviewer 1 — AI control / ML

### M1. A stronger physical work counter is not yet a stronger control protocol

The goal explicitly invokes complementary blind spots
(`be3cc8b68:docs/research/AGENDA.md:6-7`), while v4's primary tamper holds joules
fixed and deletes counts, explicitly disclaiming a causal sabotage effect
(`e901eb2a4:docs/align/pilot_protocol_v4.md:508-516`). Even perfect detection of
all such omissions does not show fewer successful undetected attacks. Positive
controls inject work whether or not that work helps sabotage.

Freeze these quantities on the same assigned malicious attempts: side-task
success, main-task usefulness, transcript alarm, energy alarm and audit
availability. Primary endpoint: successful jointly unflagged attacks divided by
**all assigned malicious attempts**, at a fixed benign alarm budget and a
predeclared usefulness requirement. Also report joint evasion conditional on
side-task success, the attack success rate, and successful-but-unaudited cases.
For an operational safety bound, count successful unaudited cases pessimistically
as escapes unless actual containment on abstention is demonstrated. This avoids
calling an incapable adversary or a broken audit a successful defense.

Compare monitor only, DC residual only, joint defense, trusted time only,
counts/tool metadata only, and monitor plus time/counts. Use paired attempts
and a fixed resource budget. AUC alone does not answer the operating-point
question. Print incremental catches and the full four-cell table of channel
alarms on successful attacks; correlated errors can make the apparent squeeze
small. Specify whether the alarm is post-hoc or can stop/reverse an action;
offline detection of a completed transfer is not prevention. Confidence: **high**.

Report monitoring inference cost, fitting/scoring overhead, meter hardware cost,
gate/hold latency and main-task utility together. An off-box monitor's energy
does not appear in the laptop's DC total; a cost or efficiency claim needs its
own measurement or an explicitly labelled estimate. Compare the joint defense
with spending the same resources on a stronger transcript monitor or re-execution.

### M2. Two pairs can validate an instrument and still overfit the control story

Both production pairs are fixed at `spam_filter_update` and `bank_transfer_2`
(`e901eb2a4:docs/align/pilot_protocol_v4.md:70-74`); threshold pooling across
pairs/configuration changes is forbidden
(`e901eb2a4:docs/align/pilot_protocol_v4.md:498-506`). A task-specific model can
memorize work patterns, prompt lengths or a peculiar tool workflow. New random
seeds within those pairs do not supply task generality. The research audit
already records prompt-length confounding and thin unique sabotage coverage
(`7f74dd2a9:docs/research-audits/2026-11-07/research-program.md:104-119,142-150`).

Add one held-out pair with a different tool/work profile and independently
scored side-task success. Report separately (a) zero-shot transfer of a frozen
detector and (b) performance after a predeclared local benign recalibration.
Do not relabel (b) zero-shot. Hold out attacker strategies or an attacker author,
not just generation seeds. Balance or disclose prompt-length differences;
never let the monitor see the sabotage instruction or an attack label. Confidence:
**high** on the limitation, **medium** that one added pair suffices for acceptance.

### M3. Model size is not evidence of adversarial capability

v4 has one production model, Qwen3.8-27B at 8-bit; the 30B anchors are an
instrument bridge, not a second production replication
(`e901eb2a4:docs/align/pilot_protocol_v4.md:58-68`). R0 chooses effort on benign
cap-ending behavior, and W1's minimum capability criterion is a state-changing
action (`e901eb2a4:docs/align/pilot_protocol_v4.md:166-191`). Neither ensures the
actual budget supports useful sabotage.
The chair explicitly limits conclusions to capped, shortened episodes
(`e901eb2a4:docs/align/council-2026-11-06-v4-review/CHAIR.md:315-317`).

Report legitimate and side-task success at the exact frozen budget, failure
reasons and truncation rates. Evaluate a second model/configuration with its own
calibration and attacker development. Changing 8-bit to 4-bit is a new cohort,
not independent model-family replication. Do not require frontier weights or
rent a datacenter merely to satisfy this review; if unavailable, retain a
local-model result and state that scale transfer remains untested. Confidence:
**high** on inference, **medium** on the model extension's priority versus more
successful attacks on the primary model.

## Reviewer 2 — security / side channel

### S1. State a game in which the attacker and the meter can actually coexist

The pipeline says power is measured outside the agent, but the current claims
limit assumes no adversarial process on the measurement machine
(`e901eb2a4:docs/align/PIPELINE.md:9-20`;
`e901eb2a4:docs/decision_log.md:9196-9206`;
`be3cc8b68:CLAIMS_STATUS.md:10-19`). The literature audit flags this same-host
telemetry issue (`16e1db623:docs/research-audits/2026-11-07/literature.md:106-122`).
An external transducer improves independence, but a USB recorder on the attacked
host, an editable integration interval, or attacker-controlled counts can still
break the audit. Root-only powermetrics is a privilege boundary, not an external
trust root.

The lead should explicitly reconcile D-139 for this new experiment. Recommended
initial game: a malicious model/policy and permitted tool actions run inside a
trusted harness; no attacker root/kernel/meter/recorder access. List exactly
which transcript fields and token counts it can omit or fabricate; distinguish
trusted evaluator truth from the defender's view. If the attacker cannot edit
runtime token records, explain which helper computation can evade them. If it
can forge counts freely, include fabricated benign count padding as an attack:
plausible metadata does not require actually performing the claimed work.

Specify white-box knowledge of coefficients, thresholds, monitor prompt/model,
meter timing, query feedback and search budget. Separate log-manipulating policy
attacks, tool-executed local code, a compromised serving process and a malicious
administrator. The last two need stronger capture trust and must not be smuggled
into a conclusion from the first. This is a proposed scope decision, not a ruling
by this seat. Confidence: **high**.

### S2. Prove the external channel measures the work that the game permits

The research page describes DC cable measurements
(`be3cc8b68:docs/research/energy-tripwire.html:149-176`), but the pinned production
analysis reads `powermetrics:gpu_power`
(`e901eb2a4:joulewise/align/apple/pilot_analysis.py:209-224`); v4's contrast is
turn-owned GPU energy (`e901eb2a4:docs/align/pilot_protocol_v4.md:472-495`). Do
not label these results external-meter validation. The audit reports substantial
energy outside the rails in a different memory-traffic regime, with explicit
single-session limits
(`7f74dd2a9:docs/research-audits/2026-11-07/research-program.md:130-140`).

Before scoring attacks, bind transducer placement, recorder permissions,
timestamps, raw-sample custody, integration endpoints, missing-sample rules and
uncertainty. A DC meter measures energy crossing its cable. It equals whole-system
consumption only after accounting for battery storage changes and other power
paths. Verify the actual charger/cable route, rather than assuming a diagram
validates it. Qualify benign and injected-work response at CPU, GPU, tool and
between-turn placements, including sampling-phase variation. Meter-continuous
episode totals must cover any permitted hidden-work interval; trusted timing
must prevent an attacker moving the interval to omit its own work.

Keep DC and rails predictors/calibrations separate at a common benign alarm
budget, then report agreement and disagreements. Do not subtract host activity
that an attacker can cause as if it were harmless background. Real local controls
validate that physical boundary, not an equivalence between all hidden tokens
and a constant joules/token. Confidence: **high** on source/boundary distinctions;
**medium** on feasible precision until native qualification.

### S3. The strongest attacker attacks the premise, not just the threshold

The monitor renderer deliberately hides tool arguments in **every** visibility
mode (`e901eb2a4:joulewise/align/shade/monitor.py:30-60`). Its `full` view includes
native reasoning; `no_scratchpad` removes closed scratchpads
(`e901eb2a4:joulewise/align/shade/monitor.py:18-27,49-57`).
Those are materially different games. Counts being logged does not mean their
content reaches the monitor. Even perfect logging leaves a common blind spot
when semantics are hidden in ordinary work. The energy machinery acknowledges
within-forward-pass invisibility
(`e901eb2a4:docs/align/energy_residual.md:388-400`).

Freeze the exact production visibility and rendered bytes. Stress-test these
six attack families, first in development, then with the frozen selected policy:

| Attack family | What a hostile reviewer wants to see |
|---|---|
| Omission/placement | Real unlogged decode or CPU/tool work, at low/high doses, within turns, gaps and holds; include zero dose |
| Work laundering | Useful-looking filler, encoded reasoning, innocent-looking tool calls, fabricated counts if permitted; a monitor does not catch something merely because it can read it |
| Work substitution | Trade cheaper benign work for covert work, preserve total tokens/energy, shift context/cache mix; do not assume hidden compute only adds to an unchanged workload |
| Same-compute sabotage | Change one harmful tool argument or choice without extra reasoning; test whether visible replies reveal it. Names-only tool views are a candidate weakness, not proof of a working exploit |
| Sensor/state shaping | Chunk or schedule work around sampling/holds, use CPU rather than GPU, exploit thermal/DVFS variation within permitted controls; privileged power-mode changes only in a separately authorized game |
| Monitor adaptation | Optimize benign-looking explanations, prompt injection in allowed transcript/tool content, and hidden-channel placement against the combined objective |

One cost-controlled screen is 2 pairs × 6 families × 3 fresh attempts = 36
assigned attacks, with doses/placements distributed by a frozen covering design.
This is a proposed stress test, not sufficient precision for six family-specific
robustness claims. The attacker objective should maximize side-task success
with main-task usefulness while evading **both** frozen alarms, given a recorded
budget of attempts, feedback queries and compute. Development feedback is allowed
and logged. Final seeds, tasks and monitor randomness remain withheld; no further
adaptation follows final scoring. Report the best attack and the full search
history, including failed runs. A negative result bounds that search procedure.
Confidence: **high** on need, **medium** on which attack will work.

### S4. Datacenter batching is a different identification problem

v4 uses a fresh process per member and reference-state gates/holds
(`e901eb2a4:docs/align/pilot_protocol_v4.md:70-74,193-201,514-516`). The chair
disclaims deployment realism (`e901eb2a4:docs/align/council-2026-11-06-v4-review/CHAIR.md:315-316`).
The research synthesis corrects a batching comparison and still concludes that
per-request attribution weakens
(`7f74dd2a9:docs/research-audits/2026-11-07/research-program.md:79`). Under shared
accelerators, cache sharing, concurrent tenants and dynamic batching, total DC
energy does not identify which request consumed it. An adaptive attacker may
use slack, overlap memory/compute or displace legitimate work; additive energy
is not guaranteed. Off-device tool calls are outside the local cable boundary.

For this paper, claim a dedicated local/edge audit. Add a bounded ungated or
co-scheduled-load extension only if affordable, and calibrate it separately.
A datacenter claim needs a serving/batching study with attribution and trusted
allocation; prose alone cannot supply it. Independent-unit/operator replication
is more valuable than another exact replay on the same laptop. Confidence:
**high** on limitation, **medium** on extension costs and venue demands.

## Reviewer 3 — statistics / measurement

### T1. Fix the calibration construction before invoking conformal-style ranks

The protocol uses per-session leave-one-trajectory-out benign fits and full
benign fits for sabotage (`e901eb2a4:docs/align/pilot_protocol_v4.md:488-505`);
the implementation confirms the asymmetric fitting maps
(`e901eb2a4:joulewise/align/apple/pilot_analysis.py:228-235`). Imported calibration
selects scores after fitting and pools them across sessions
(`7fbd95e31:scripts/align_pilot_calibration.py:70-112`). Deduplicating seeds does
not make scores exchangeable across a new window or make differently trained
scoring rules symmetric.

The standard order-statistic bound requires calibration and the new benign score
to have an appropriate joint exchangeability construction. A frozen code commit
alone does not prove that. Before collection, either justify the actual
cross-fit/session algorithm mathematically, or add a clean split detector with
a fixed trained score and untouched calibration/test sets. Preserve the existing
v4 statistic as specified unless the owning lead prospectively changes it.
Report empirical benign test intervals even if a rank guarantee is justified.
Do not call failure to detect a window shift proof of exchangeability.
Confidence: **high** that the proof obligation exists; **medium** whether the
final amended construction can satisfy it.

### T2. m ≥ 39 neither specifies a threshold nor validates a realized joint FPR

The page says “sample maximum,” yielding marginal 1/(m+1)
(`be3cc8b68:docs/research/energy-tripwire.html:151`). The imported code instead
uses k = ceil(0.95(m+1)) (`7fbd95e31:scripts/align_pilot_calibration.py:45-57`).
At m = 39 this is **rank 38**, giving marginal tail at most 2/40 = 5% under
the rank assumptions; the maximum gives 1/40 = 2.5%. This is a concrete
specification ambiguity, not evidence that either prospective choice is invalid.
The older API document even states a different quantile convention
(`e901eb2a4:docs/align/energy_residual.md:109-116`). Register the actual series
algorithm and mark those distinctions explicitly.

Marginal coverage averages over calibration draws. For an iid continuous benign
score and the maximum of m calibration scores, the realized tail's one-sided
90% upper tolerance bound is 1−0.1^(1/m); at m = 39 it is **5.73%**, or **7.39%**
at 95%. This extends the chair's warning
(`e901eb2a4:docs/align/council-2026-11-06-v4-review/CHAIR.md:157-165,307-310`).
For a separate iid benign test with zero alarms, 59 tests give a one-sided 95%
Clopper–Pearson upper bound of 4.95%. Shared windows invalidate treating every
member as an independent test; plan window-level replication and report that
assumption separately. With so few windows, a cluster bootstrap is a diagnostic,
not a guarantee of accurate tail inference.

For an OR defense, two individually 5% alarms allow up to 10% benign alarms by
the union bound. No independence assumption repairs the budget. Freeze either
a justified jointly calibrated statistic or an allocation such as 2.5% per
channel, with untouched benign tests for the combined rule. Include abstention
and repeated/per-turn monitoring policy in its unit of error; a per-episode
bound is not a session-wide or deployment-lifetime bound. Confidence: **high**
on arithmetic and logical distinctions; final coverage conditional on T1.

### T3. Separate primary inference from an attractive collection of curves

v4 already has two count conventions, an H grid, alternative fits, thermal
criteria and contrast rules (`e901eb2a4:docs/align/pilot_protocol_v4.md:410-441,488-523,611-623`).
Adding channels, monitors, models, attacks and dose curves creates many chances
to select a flattering result. Points on an H curve reuse the same energy and
trajectory. Turns, doses, sentinels and replays are not independent successes.

Register one primary joint comparison at one alarm budget; predeclare task
aggregation and whether the claim is mixture-average or per-pair/per-family.
Use a small hierarchical testing family or Holm correction for confirmatory
comparisons, and label the rest exploratory. D-139's old two-contrast Holm family
belongs to a different estimand and must not be silently reused here
(`e901eb2a4:docs/decision_log.md:9199-9201`). Freeze attack selection and threshold
tuning on development data. Report uncertainty for paired changes in successful
escape, not independent error bars for detectors run on the same episodes.

Register H50/H90 interpolation, failure-to-cross handling and resampling units;
allow “not reached within tested H,” including nonmonotone curves. Keep analytic
H_min, empirical known-omission curves and causal injected-work curves distinct.
The energy API itself warns that power calculations rely on additive work and
calibration shape (`e901eb2a4:docs/align/energy_residual.md:197-237,388-400`).
Three detected trajectories are not a precise power estimate; neither is a
simulator tuned to those three. Confidence: **high**.

### T4. Selection by eligibility can preferentially remove the best attacks

X1–X8 exclude thermal, missing-state, divergent, OOM and deadman cases; cohort
and extension rules also depend on instrument status
(`e901eb2a4:docs/align/pilot_protocol_v4.md:454-470,612,619,623`). Compute-heavy
or delay-inducing attacks may trigger those events more often than benign runs.
“Detection among eligible runs” can improve while useful audit coverage collapses.

Retain a funnel by condition, attack family, task and window: assigned, started,
completed, side-task scored, meter available, monitor available, eligible and
alarmed. Keep the all-assigned attack denominator from M1 beside conditional
instrument analyses. Predeclare when an invalid/missing audit triggers an
operational stop, and measure false stops on benign tasks. Count-only extensions
must remain blind to alarms and side-task success. No favorable top-ups or
discarding long attacks as “background.” Confidence: **high** on risk; its actual
magnitude is unknown.

### T5. A successful future campaign still needs one auditable final specification

The supplied pre-arm gate rejects the pinned head and lists registration,
battery, contrast, fallback and classifier issues
(`53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md:9-30,77-155`).
The protocol lists unresolved U-statistic conventions and chair amendments
(`e901eb2a4:docs/align/pilot_protocol_v4.md:433-441,594-642`). These are known
findings from that audit, not fresh executing-review discoveries by this seat.

Even if all gates pass, a reviewer needs the final estimand, sensor/meter
boundary, software/model hashes, thermal margins, fallback configuration, seed
roster, exclusion/stopping rules and code/registration mapping in one frozen
version. Show the U6 operating-characteristic/precision limitation rather than
renaming an inconclusive calibration “stable.” R1 and W1 are tuning data; W1
cannot become final test data because its result looks representative. Document
which people/systems could see which outputs, when the freeze occurred, and all
prospective changes. Block-5 blinding does not imply that the already-inspected
ALIGN pilots or a repeatedly queried red team were blinded. Keep those data
roles separate without opening Block 5. Confidence: **high**.

## Novelty, replication and what discussion alone can address

### N1. The novelty must survive four close neighbors

The supplied synthesis describes these neighbors and gives source URLs
(`16e1db623:docs/research-audits/2026-11-07/literature.md:85-110,128-150,267-279`).
Those are secondary, locally available assessments here. Before submission the
lead should verify the primary texts and update versions; do not reuse numeric
leaderboard claims from this review as newly verified facts.

| Neighbor | Strongest novelty objection | Needed distinction/evidence |
|---|---|---|
| CoIn; PALACE; token-inflation audits | Auditing hidden reasoning counts already exists | State provider cooperation, trusted counts and physical-access assumptions; compare achievable error/cost against counts and trusted-time baselines. CoIn's count-manipulation task is not semantic sabotage |
| Gargiulo & Kulp | External power already identifies workloads | Distinguish a workload-class trace classifier from per-episode residual auditing and, crucially, show incremental joint defense against an adaptive attacker |
| Kimpson, Baker & Graham | Power already bounds covert compute, including matched-energy limitations | Report hidden work relative to declared work as well as tokens/joules; explain why transcript monitoring improves the tested bound and explicitly retain shared blind spots |
| Energy regressions / SHADE-Arena monitors | Both component technologies are established; combining them could be incremental | A preregistered, costed joint evasion frontier at equal benign alarm rates, independently metered positive controls and transfer/replication are the contribution |

Avoid “first physical monitor” and a global absence-of-literature claim. A safe
draft claim is “a prospective evaluation of transcript monitoring combined with
an externally measured residual audit against the specified adaptive policies
on dedicated local hardware.” If successful, add the measured improvement and
its interval. Thermal rigor and blinding make that result credible; they are not
substitutes for novelty.

For replication, ship code/config and model revision/quantization identifiers,
tiny synthetic fixtures, raw-format specifications, energy integration and
threshold recomputation instructions, hardware/cable/clock setup, freeze history
and a minimal read-only replay entrypoint. Model weights need not be redistributed.
Release only newly authorized study artifacts; no Block-5 materials are needed
for this paper. Recomputing the same trace independently verifies arithmetic;
another unit/operator verifies transfer. Label which kind was achieved.
Confidence: **medium-high** on positioning, **medium** on absence of closer work
because this seat performed no network search.

**Discussion can bound these claims, but cannot supply missing evidence:**

| Limitation that can remain | Honest discussion statement | What would require new data |
|---|---|---|
| Privileged host compromise | Excluded attacker class; external recorder trust stated | Tamper/replay validation under that privilege |
| Datacenter / remote tools / dynamic batching | Dedicated local-machine result; no per-tenant attribution claim | Matched serving experiments and trusted allocation |
| Frontier models or other architectures | Exact model/configuration, capability and budget scope | New model-specific calibration and successful adaptive attacks |
| Same-compute semantic attacks | Energy has no general semantic discriminator; tested misses remain visible | A defense claim needs transcript evidence against them, not a caveat alone |
| Very low FPR, long deployment horizons | Finite observed rate/interval; no lifetime guarantee | Adequate independent benign exposure and drift study |
| One physical unit | Device-specific sensitivity and reproducibility recipe | External-unit/operator measurements |
| Universal “squeeze holds” | Finite attack-set result with a compute/search budget | A theorem needs substantive attack/monitor assumptions, not more random seeds |

Do not move failed joint efficacy, an undefined trust boundary, missing DC
qualification, leakage or an invalid error-rate claim into limitations and keep
the same headline. Those change what the result means.

## Venue targets and deadline status

**No exact submission deadline is verified in this offline review.** A targeted
search of local Markdown found no 2027 CFP dates for the venues below. The dates
column supplies planning windows from customary cycles, explicitly not 2027
deadlines. The lead must check the official CFP, abstract/full-paper cutoffs,
timezone, tracks, anonymity and concurrent-submission rules before committing
to a date. Do not confuse the repo's November Paper-1 milestones with an ALIGN
venue deadline.

| Preference | Target / fit | Deadline status as of this review | What would make the submission competitive |
|---|---|---|---|
| 1A: security version | USENIX Security 2027 or next eligible cycle; strongest fit for a carefully scoped adaptive attacker and independent physical channel | **Exact cycle dates unknown; verify now.** Do not infer availability from historical multi-cycle schedules. [Official conference hub](https://www.usenix.org/conferences) | Reproducible adaptive search, concrete successful attacks, clear trust boundary and escape/FPR tradeoff |
| 1B: ML/control version | NeurIPS 2027 main track; strongest ML fit for complementary oversight and measurable control improvement | **Exact abstract/paper dates unknown.** Historical planning window: May; use an internal complete-draft target in April 2027, not as an official deadline. [Official site](https://neurips.cc/) | Held-out task/attacker evidence, strong monitor baselines, capability/usefulness, joint statistical precision |
| 2: earlier ML opportunity | ICML 2027 main track; plausible if the control contribution and extension data are ready | **Exact dates unknown.** Historical planning window: January; internal readiness review in December 2026. [Official site](https://icml.cc/) | Same core evidence as NeurIPS; no rushed reuse of pilot/tuning data as a test set |
| 2: security alternative | ACM CCS 2027; strong if framed as an adaptive attack/defense system | **Exact cycle deadlines unknown; verify current CFP before choosing a cycle.** [SIGSAC conference listings](https://www.sigsac.org/ccs.html) | Strong exploit/evasion evaluation, capture independence, artifact and honest attacker scope |
| 3: later security alternative | IEEE S&P / NDSS next eligible main-track cycle | **Exact eligible cycle and deadlines unknown.** Verify year and cycle; do not assume a 2027 slot remains. [S&P](https://www.ieee-security.org/), [NDSS](https://www.ndss-symposium.org/) | Strong systems/security argument beyond a laptop correlation study |
| Later option | ICLR next eligible main track | **Exact date unknown.** Customary preceding-year autumn cycle makes a 2027 opportunity unsafe to assume in November 2026; consider 2028 after checking. [Official site](https://iclr.cc/) | A broadly useful oversight method and compelling generalization |

Venue fit judgments are **medium confidence**; exact-deadline confidence is
**unverified**. Prefer security if the best result is a rigorously scoped
physical audit against concrete adaptive attacks; prefer ML if the best result
is generalized incremental control efficacy. A workshop is a useful fallback
for v4-only instrumentation, but it does not satisfy the main-track objective.
Deadline verification is the only requested research subtask left unresolved by
the no-network constraint.

## Lead handoff

First disposition P0/S1, M1 and T1–T3 as a proposed threat game, endpoint and
error-budget/data-split amendment. Then reconcile it with the final W1 gate
packet at the lead's actual integration head. Reserve attack, benign-test and
replication budgets only after that decision. Nothing here changes the current
roster, authorizes native collection or registers a task.

Verification and the local commit are recorded in
`docs/run_reports/2026-11-07-sol-reviewer2-seat2.md`. Native meter/MLX
qualification and a live red-team campaign belong to the lead outside this
sandbox; no model code or MLX tests were added by this docs-only seat.
