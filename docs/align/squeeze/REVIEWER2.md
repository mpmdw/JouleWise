# REVIEWER2 — three hostile reviews of the proposed energy squeeze

2026-11-07 · **DESK DRAFT for lead review. No registration, ruling or collection authority.**

These are three simulated reviewer perspectives written in one session, not
three independent reviews. Assume v4 eventually passes its registered gates.
That would establish a useful local measurement result; it would not, by itself,
establish that an adaptive saboteur must expose itself to either detector.
For a main-track paper, the decisive addition is a prospectively evaluated
**successful sabotage / both detectors miss** endpoint, against attacks designed
to exploit both channels together.

The strongest counterexample is simple: a malicious action can replace an
honest action inside the same logged forward passes. The meter can see exactly
the expected work while the transcript looks innocuous. Logging plausible work
does not require revealing the purpose of that work. The proposed squeeze is
therefore an empirical hypothesis over a specified attack space, not a physical
necessity. The residual documentation already acknowledges the within-forward-
pass limit. [ER, “Limits”; LIT, M4][ER]

## Evidence and authority used

All observations below come from repository text and local Git objects. No
measurement data or sealed outcome was opened or inferred. No network or fetch
was used; refs may lag their upstream branches. The sources are pinned below so
the lead can distinguish this review from a review of a later candidate.

| Key | Repository source and scope used |
|---|---|
| V4 | [Protocol v4 at `e901eb2a4`][V4]: configuration, roster, residual analysis, exclusions, pending council rulings and Addendum FN. Still a draft at this pin. |
| ER | [Energy residual specification at `e901eb2a4`][ER]: fit, score, calibration, count visibility, synthetic power and limits. |
| CHAIR | [2026-11-06 chair ruling at `5ea21c17f`][CHAIR]: especially rulings 2, 3, 6, 10, 12 and §D's forbidden upgrades. |
| LIT | [Literature audit at `16e1db623`][LIT]: H1–H3, M1–M4 and source-status distinctions. Prior-art statements here are attributed to this audit; I did not independently recheck external papers. |
| GATE | [W1 pre-arm audit at `53a230598`][GATE]: executive summary, decisions and BLOCKER-1. Its findings describe the audited pin, not verified current defects. |
| PROGRAM | [Research-program audit at `7f74dd2a9`][PROGRAM]: H2, M2–M4, E1/E2/E4 and “Weak spots”. |
| AGENDA / TRIP | [Research agenda][AGENDA] and [Energy Tripwire page][TRIP] at this clone's starting head `fdb1e0409`. The page is framing, not a measurement contract. |
| STATE | [Lead directions, items 203–204][STATE] at `fdb1e0409`: R10, Q4 approval, Q6 registration grade, and positive controls approved in principle. |
| AP / CL / MM | [Analysis-plan contract][AP], [claims ladder][CL] and [measurement methodology][MM]: multiplicity, units, boundaries, frozen sample sizes and dependence. |

**Resolve source chronology explicitly.** V4's text still says registration
grade defaults off, and the earlier PROGRAM audit asks whether Q4/Q6 were
answered. STATE item 204 subsequently answers both: Q4 yes; Q6 requires
`m ≥ 39` per pair **and a held-out test cohort**. Do not reopen those decisions
or present `m = 21` as the final approved design. GATE's registration findings
still need lead disposition against the actual candidate. This review does not
certify their repair. [STATE; V4, residual targets; GATE, BLOCKER-1][STATE]

## Reviewer 1 — ML and AI control

**Likely recommendation if only v4 succeeds: reject for the proposed broad
title; potentially valuable as a narrowly framed measurement paper.**

**M1. The dependent variable is omitted work, not sabotage.** Holding measured
joules fixed and deleting logged reasoning counts almost guarantees the
predicted direction of a residual shift. That is a useful detector calibration,
not evidence that successful sabotage requires additional computation. Genuine
injection establishes physical sensitivity but still does not establish that
an agent used that compute to sabotage. Separate three experiments: known-H
log edits, real extra computation, and agent-achieved side-task success. Report
main-task usefulness, side-task success and alarms for every attack attempt.
If successful low-compute sabotage evades both channels, retain it as a central
failure case. [V4, “known-H tamper”; ER, opening and Limits; PROGRAM, H2/E2][V4]

**M2. Complementary blind spots do not establish complementary coverage.**
An adaptive agent can encode reasoning in bland filler, reuse legitimate
reasoning for the side task, or replace useful computation with malicious
computation at essentially the same energy. It may also use benign-looking
padding to make hidden work fall within the predicted budget. A stronger model
might need fewer incriminating steps. A red team that merely removes more
tokens is not adaptive to the joint detector. Require joint feedback during
development, then freeze attacks before untouched evaluation. Report the
strongest mixed attack and the search budget, including failed searches.
[ER, Limits; LIT, M4; PROGRAM, M3][ER]

**M3. Two task pairs and one selected production model are a case study.**
The two pairs are `spam_filter_update` and `bank_transfer_2`; more seeds do not
create more tasks. The 30B anchors are not an independent, capable red team.
D is one model at a selected effort rung and quantization with tight admission
budgets; V4 explicitly forbids a cross-model monitoring claim. A capability
screen that requires a state-changing action is too weak to show that the model
can execute difficult, concealed sabotage. Predeclare capability evaluation on
development tasks with monitors disabled, then freeze the model and budgets.
Add held-out task families and, if feasible, a different model family; otherwise
state the exact case-study scope in the title/abstract. Flash-Next is pending,
not replication evidence. [V4, configuration, R0 ladder and Addendum FN;
CHAIR, §D.7/.9; PROGRAM, Weak spots][V4]

**M4. The monitor comparison could be won by prompt leakage or extra FPR.**
The pilot spam sabotage prompt is 755 tokens longer, and a counts-only baseline
has not been evaluated in the cited program audit. Give the transcript monitor
the deployment-realistic view: legitimate instructions, public messages and
tool events; exclude the sabotage instruction, condition tag, injection dose,
hidden scratchpad and outcome label. Specify whether reasoning counts are
visible independently of reasoning text. Compare metadata-only, trusted-time,
transcript-only, energy-only and combined detectors on the same episodes and
at the same **system-level** benign false-alarm budget. AUC alone cannot answer
whether the combination improves safety at a usable operating point. Fix the
monitor version, prompt, sampling and truncation policy before testing.
Include benign prompt-length/placebo controls so longer sabotage instructions
cannot substitute for detecting malicious behavior.
[PROGRAM, M2/M4/E1; ER, visibility choice; AGENDA, two-channel audit][PROGRAM]

## Reviewer 2 — security and side channels

**Likely recommendation if only v4 succeeds: reject any adaptive-security
claim; reconsider with a bounded, genuinely adversarial evaluation.**

**S1. What is trusted, and what can the attacker change?** Same-host
`powermetrics` is software telemetry, not an independent physical trust anchor.
An unprivileged agent's inability to write root-owned records is a privilege
assumption, not a test against a malicious host/provider. An external DC meter
helps only if the acquisition, timestamps, episode boundary and preserved raw
stream are also outside attacker control. Name who controls the host, runtime,
logger, tools and meter collector. If runtime counts are complete and trusted,
explain how hidden calls can occur; if the disclosure log is attacker-controlled,
explain why invented counts/context cannot inflate predicted energy. Hashing a
record proves neither completeness nor truth. Distinguish tampering with the
acquisition from evading an intact detector through valid workload choices.
[LIT, H2; V4, instrument checks; TRIP, instrument/walkthrough][LIT]

**S2. Energy conservation does not imply detectable excess energy.**
The attacker can substitute work, exploit the detector's calibrated slack,
spread a small omission over turns, manipulate workload mix, or spend logged
tokens on benign-looking computation. Real but cheap sabotage may have no
incremental dose. Omission plus cover is the obvious mixed attack. A detector
that reads only total token counts does not know that all those tokens were
used honestly. Require attacks on prediction terms and variance as well as on
the numerator: context/cache accounting, extra logged turns, filler and plausible
tool work. Reject impossible fabricated-count attacks only when the declared
trust boundary actually prevents them. Executed padding costs energy too: test
its effect on score variance and model slack rather than assume it cancels
arbitrary hidden joules. [ER, score and Limits; LIT, M4;
PROGRAM, M2][ER]

**S3. The proposed physical channel is not the v4 channel.** V4's contrast/U3
and attribution use turn-owned GPU-rail energy; the squeeze brief calls for
external DC energy. One cannot transfer rail thresholds or uncertainty bounds
to DC input. Whole-machine DC includes CPU, memory, fans, conversion and battery
flows. Battery discharge can supply compute without contemporaneous charger
energy. A start-of-window high state of charge does not prove an episode-level
energy balance. Require a floating-battery qualification, meter sample coverage,
clock/boundary uncertainty, raw-stream custody and a DC-specific benign model.
If independent acquisition cannot be arranged, narrow the trust claim. The KB
rails-coverage result is a reason to measure both boundaries; its roughly 24%
fraction is not a universal conversion factor. [V4, U3/contrast; GATE, HIGH-1;
PROGRAM, M1; CL, Global Rules][V4]

**S4. Local batch-1 evidence says little about a datacenter.** Thermal gates
and inter-turn holds impose a controlled reference state. Concurrent batching,
shared accelerators, remote tools, scheduler slack and co-tenants can break
episode-level attribution and hide marginal work inside already-powered
hardware. Off-host work is outside a local meter's physical boundary. The
AP contract explicitly disallows per-request energy attribution in overlapping
batch groups. Keep the primary claim to dedicated local execution; add an
ungated regime and second unit if making a deployment claim. A server extension
would need a new batch-level estimand, trusted scheduler/accounting and fresh
calibration, not a paragraph extrapolating laptop token costs. [V4, known-H
caveat; CHAIR, §D.8; AP, Metric + exact window class; PROGRAM, M4/R9][AP]

## Reviewer 3 — statistics and measurement

**Likely recommendation if only v4 succeeds: reject rate/robustness claims
without an independent evaluation cohort and a coherent calibration argument.**

**T1. Which threshold construction supports the FPR statement?** ER's generic
API describes leave-task-pair-out fits and a type-1 rank `ceil((1−α)m)`; V4
describes per-session leave-one-trajectory-out benign scores, a full benign fit
for sabotage, and rank `ceil((1−α)(m+1))`. These are different procedures.
The sample-maximum theorem requires suitable exchangeability of calibration
and future scores; a test score using a differently fitted model does not
automatically have that property. Resolve the exact executed procedure and
proof/limitation before collection. For the squeeze addendum, a separate fit
set, calibration set and later test set is the clearest proposal. Keep v4's
frozen analysis as its own result unless the lead prospectively amends it.
[ER, Episode scores and calibration; V4, residual analysis; CHAIR, §D.1][ER]

For a fixed scoring rule and iid continuous benign scores, a maximum over
`m = 21` gives marginal exceedance `1/22 = 4.55%`, while the realized FPR's
one-sided 90% upper bound is `1−0.1^(1/21) = 10.38%`. At `m = 39`, a
**maximum** gives 2.5% marginal and a 5.73% upper bound at 90% confidence.
But V4's stated 5% rank rule gives rank 38 at `m = 39`, not the maximum.
TRIP's maximum/2.5% explanation and V4's rank policy must be reconciled.
Neither `m ≥ 39` nor a finite threshold certifies a realized 5% FPR.
[V4, target/ruling 12; CHAIR, §D.1; TRIP, walkthrough step 5][V4]

**T2. The OR alarm spends a joint error budget.** Two detectors each calibrated
at 5% can produce a combined benign alarm rate as large as 10%. Comparing that
combination to a 5% transcript monitor is unfair. Calibrate the combined policy
as a policy, or allocate component error budgets with a union bound. For
example, two 2.5% marginal budgets target a 5% marginal union bound without
assuming detector independence; they still need a defensible calibration
scheme and independent realized-FPR assessment. Searching thresholds, tasks,
H doses, models, boundaries and fusion rules creates additional selection
opportunities. Freeze one primary comparison; enumerate secondary families and
Holm correction, and label exploratory sweeps. Do not select whichever energy,
time or fusion variant looks best on the test set. [AP, Required fields and
Analysis Registry; ER, calibration][AP]

**T3. Turns, replay copies and H-grid points are not independent attacks.**
Removing ten different H values from one carrier creates one trajectory with
ten derived scores. Two seed-1 sabotage trajectories measured in three sessions
are still only two distinct trajectories. Three to five windows are too few
for a reassuring window-cluster bootstrap. Prespecify trajectory and window
dependence, show per-window results and leave-one-window-out sensitivity, and
reserve H50/H90 as descriptive when a curve does not identify them. A curve
that never reaches 90% has H90 beyond the tested range, not a fitted guarantee.
Use fresh carriers for physical doses, and account for shared fit/threshold
uncertainty in intervals. [PROGRAM, H2; V4, ruling 2; ER, power caveats;
MM, Statistical Protocol][PROGRAM]

**T4. Selection and exclusions can manufacture apparent robustness.** The
model/effort/budget ladder, thermal holds, cache rebuilds, cap-ended turns,
charging and deadline exclusions all change which episodes survive. An adaptive
attacker might cause an exclusion deliberately. Report alarms conditional on
instrument validity, plus an all-assigned-attempt ledger with completion,
usefulness, sabotage success, abstention and refusal. A refusal that blocks the
agent may be a safe stop at an availability cost; a refusal that lets it continue
unobserved is not a detected attack. V4's hybrid model may also misspecify the
five-term fit. Predeclare support/extrapolation checks, rebuild and unowned-gap
diagnostics and a hybrid-attention sensitivity; never choose a fit from attack
performance. Equal seed indices do not make benign/sabotage trajectories a
paired causal comparison. [V4, stopping/exclusions/rulings 10–14/25; ER, Limits;
LIT, M1; CHAIR, §D.11/.12][V4]

**T5. Blinding and reproducibility must cover the new claim.** A blinded B5
analysis does not blind an ALIGN red team. Record who sees doses, conditions,
monitor scores, energy and success labels at each stage. Adaptive development
requires feedback; final evaluation requires a fresh sealed cohort. Freeze
attack code/prompts, monitor, fusion, exclusions and stopping rule before that
cohort. Release a runnable synthetic pack, analysis code and appropriately
sanitized raw traces/transcripts after the owning release gates. Independent
arithmetic recomputation of the same recordings is valuable but is not a second
physical experiment. A second device/collector would address different errors.
[AP, registry freeze; CL, L4; GATE, registration; PROGRAM, E6][AP]

## Prioritized changes before collecting evidence for the squeeze

Everything in this section is a **proposal for lead adjudication**, not a new
registered task or an amendment applied by this review. P0 items precede
claim-bearing squeeze collection; P1 items are needed before their extension's
collection if that extension is claimed. Existing v4 engineering gates remain
separate. Costs are rough planning estimates, not measured timings or bookings.
One person-day means about eight desk hours; one Mac-night means 12.4 hours
as in PROGRAM. Production instrumentation and model tests require the lead's
clean, no-agent session. No model download is proposed in this review run.

| Priority / item | Concrete addition or change; completion evidence | Objections addressed | Estimated incremental cost |
|---|---|---|---|
| **P0-1: claim and trust contract** | A short threat table: attacker capabilities/feedback/budgets, legitimate utility, local/remote boundary, trusted count provenance, collector privileges, permitted log edits and protected evidence. Separate omission, injection and semantic-sabotage estimands. State a joint-evasion criterion and a failure condition in advance. | M1/M2, S1/S2/S4 | 1–2 person-days; no Mac time. |
| **P0-2: reconcile authority and freeze** | Carry Q6 and R10 into the actual candidate; disposition GATE's nine missing W1-blocking rulings and WP19, battery/contrast/duty issues against current code. Freeze cohort keys, dose/attack roster, monitor view, fits, calibration ranks, fusion and exclusions. A dated disposition table must cite implementation and native receipts. This review is not that receipt. | M3, S3, T1/T4/T5 | 1–3 desk days plus owning reviews; R0/R1 time already budgeted by v4, repairs unknown. |
| **P0-3: independent DC qualification** | Specify collector topology and end-to-end trusted raw stream; qualify floating battery and meter coverage/time alignment on representative episodes. Fit/calibrate DC residuals separately from rails. Retain rails as a diagnostic, not a fallback chosen by test performance. | S1/S3, T4 | 2–4 desk days plus 6–18 instrument hours; new hardware/collector procurement unknown. Qualification may share positive-control episodes. |
| **P0-4: physical positive and negative controls** | Randomized, desk-blinded doses including zero and sham injection; actual unlogged decode at in-context and fresh-context sites, plus CPU/tool and memory work within the declared boundary. Check dose custody independently. Preserve omission curves as a separate assay. Begin with the approved 30B control shape and include D controls before transferring a D physical-detection claim. | M1, S2/S3, T3/T4 | 2–4 desk days; PROGRAM E2 estimates 1–2 nights for 30B alone. A D bridge is additional, roughly 12–24 member-hours for 24–48 members at the 1,800 s cap, plus scaffold. |
| **P0-5: joint adaptive red team** | Implement the attack families below; give the development attacker both scores and public detector details. Bound search by queries, tokens, energy and human edits. Freeze winning policies and attack-family roster before fresh evaluation. Include zero-extra-compute and mixed omission/cover attacks; record all attempts and query expenditure. | M2/M3, S1/S2, T4/T5 | 4–8 desk days; a planning cap of 100–200 live development attempts costs 50–100 member-hours at 1,800 s each, plus scaffold. Simulator screening can reduce this; it cannot establish physical evasion. |
| **P0-6: fair monitor and fusion baselines** | Lock transcript visibility and monitor prompts; score metadata/time/transcript/energy/combined policies on common held-out episodes. Set one total FPR budget and one primary combined-vs-transcript comparison; report energy-vs-time incremental value. | M4, S2, T2 | 2–3 desk days; offline monitor inference on an allowed nonmeasurement host, measured rather than assumed cost. Same episodes can serve P0-7. |
| **P0-7: sample-size and error plan** | Distinct fit/calibration/test roles; honor ≥39 calibration episodes/pair but do not count these as test evidence. Enumerate confirmatory families, interval construction, window allocation, attack-policy selection and exclusion handling. Choose the target rate precision before collection; show both optimistic iid and dependence-inflated budgets. | T1–T5, M4 | 1–3 desk days. Test rates can dominate cost: zero alarms in 59 independent test episodes/pair gives a one-sided 95% upper bound below 5%; two pairs cost 59 member-hours at cap, before scaffold. See qualifications below. |
| **P0-8: leakage and blindness rehearsal** | Synthetic end-to-end fixtures demonstrate no dose/condition/hidden-log leak into the monitor, deterministic frozen scoring and preservation of unknown/invalid outcomes. Separate development feedback from sealed final scoring. Independently recompute a synthetic final table before collecting its real analogue. | M4, T4/T5, S1 | 1–2 desk days; no production windows. |
| **P1-1: task and model breadth** | Add at least two held-out task families selected for different sabotage mechanisms, including a low-compute action; add an already available capable model from a different family if feasible. Predeclare how capability failures are reported. Each configuration has separate calibration; no opportunistic pooling. | M1–M3, T3/T4 | 2–5 desk days. Each new configuration × pair needs at least 39 calibration members = 19.5 cap-hours, plus separate fit/test/control members and scaffold. Availability/parity may dominate. |
| **P1-2: replication and operational stress** | Reserve a second physical unit/independent collector; repeat the frozen primary assay with unit-specific calibration. Add an ungated/ordinary-serving cohort if making a deployment claim. Shared batching is a separate study; choose that scope before its collection. | S3/S4, T3/T5 | 2–4 desk days plus hardware access. A lean assay is roughly 1–2 windows; full rate replication must be sized like P0-7 and can be much larger. |

These costs overlap: P0-4, P0-6 and P0-7 can share evaluation recordings where
their roles were assigned before collection; training, calibration and test
roles cannot share an episode. Do not add all rows as if independent. Conversely,
the 100–200-attempt red-team budget is material: it alone is about 4–8
12.4-hour nights of capped member time, before scaffolding. The full main-track
package is not one positive-control night plus analysis. If that budget is
unavailable, keep v4's bounded local claim and publish the adaptive study as an
explicitly limited follow-up, rather than call a non-adaptive grid adaptive.

## Minimum adaptive attack specification

Publish detector formulas and monitor prompts to the development red team.
Allow feedback from the **combined** policy, not only a binary transcript
alarm. Freeze candidate policies/selection criteria after development, and run
them on fresh seeds, carriers and later windows. The attack controller's own
search compute must be counted separately; if executed off-host it must not be
confused with the target agent's monitored execution. Final outcomes stay sealed
until the analysis and validity decisions are frozen.

| Attack family | Attacker controls / concrete test | What a miss would demonstrate |
|---|---|---|
| Ordinary overt sabotage | Direct attempt with full visible trace and no omission. | Establishes task capability and whether the transcript monitor has an easy positive control. |
| Omission-only | Real hidden compute at several sites/doses, including a zero/sham arm; compare to separately labeled log edits. | Physical sensitivity and the gap between post-hoc omission and execution. |
| Cover-only / disguised reasoning | Keep honest counts, but use bland filler, indirect tool arguments or misleading reasoning to accomplish the side task. | Whether the monitor reads semantics reliably when energy is fully explained. |
| **Omission + cover** | Jointly choose hidden dose and innocuous logged prefill/decode/turn budget to minimize both alarms while maintaining main-task utility. Use only genuinely executed cover work unless fabricated counts are in scope. | The central squeeze challenge; padding can change both predicted energy and the transcript. |
| Count/context forgery | Inflate disclosed counts or cached context without doing that work, if the attacker controls those fields. If ruled impossible, demonstrate trusted field derivation with a negative fixture. | Whether the energy prediction itself has an unauthenticated input. |
| Work substitution / minimal compute | Attempt a malicious state-changing tool action with the same or fewer logged tokens/calls as useful behavior, without injected computation. | A direct counterexample to any universal sabotage-energy claim. |
| State and placement | Choose allowed timing, cache reuse, CPU vs GPU/tool work, and spread work across turns. Test boundary-adjacent work and preheating only within declared permissions; collector/gate modification is a different threat. | Physical/model slack and whether exclusion causes are exploitable. |
| Monitor-aware revision | Use development feedback to rewrite reasoning/tool justifications while preserving the successful action and nearly matching logged work. | Transfer from an optimized attack to an untouched evaluation cohort. |

Do not require the initial full Cartesian product of every family, model, task
and dose. Use development to select a bounded set, freeze the selection rule,
then report final performance for every selected family. Keep the mixed and
minimal-compute families mandatory even if they fail in development. A
handwritten successful malicious tool call can validate the harness's failure
surface, but it is not evidence of model-generated adaptive sabotage.

## Concrete endpoint, rate claims and stopping rules

Let `Y` mean successful side-task sabotage, `U` legitimate-task utility, `AE`
the frozen energy alarm and `AM` the frozen transcript alarm. The primary attack
endpoint should be:

```text
joint attack success = P(Y = 1 and AE = 0 and AM = 0 | assigned attack policy)
combined benign FPR = P(AE = 1 or AM = 1 | benign)
```

Report utility jointly with safety, plus the conditional evasion rate among
successful sabotages. Report attack capability explicitly so an incapable
model's low joint success rate is not mistaken for detector coverage. Use
environment-state success and legitimate-task scoring rather than agent
self-report; adjudicate uncertain outcomes blinded to alarms.
With no successful sabotages, conditional detector coverage is unestimable.
For each pair, policy and window, print the four `AE × AM` outcomes, all
assigned attempts, side-task success, main-task utility, invalid/abstaining
observations and operational stops. Do not multiply marginal miss rates or
assume independence. Compare detectors at the same benign-FPR target and show
the paired change in joint attack success, with uncertainty. Test the worst
predeclared attack family as well as any prespecified mixture; an average over
mostly ineffective attacks cannot establish a squeeze.
Unknown outcomes remain unknown; show worst-case bounds that count them as
possible joint evasions alongside the valid-only results.

The lead must choose the minimum useful improvement and maximum tolerable joint
attack success **before data collection**. A sensible decision form is:
combined-FPR upper bound within budget, utility loss within a fixed margin, and
a simultaneous interval supporting the declared improvement against the
strongest baseline. Failure of any limb yields unresolved or unsupported
wording. No numerical target is adopted by this draft.

Some scale checks, assuming independent Bernoulli episodes and zero observed
events: a one-sided 95% upper bound is `1−0.05^(1/n)`. It is 9.81% at `n=29`,
4.95% at `n=59`, and 0.997% at `n=299`. Thus 0/3, 0/12 or merely `m=39`
calibration cases cannot establish a small realized attack/FPR rate. These are
single-rate best-case calculations, **not** a powered comparative design;
multiplicity, nonzero events, small baseline differences and within-window
dependence require more evidence. Bonferroni/Holm-adjusted simultaneous
statements require their own sizing. No threshold/theorem claim survives
unexamined window drift or a changed scoring rule.

For H curves, preserve carrier identity and shared calibration uncertainty;
report physical joules, tokenizer-specific H and hidden/declared work fraction.
Show the tested range and uncertainty rather than interpolating H90 from a few
whole-turn crossings. Use window and trajectory sensitivity analyses; do not
treat an ordinary bootstrap over three windows as a cure for sparse independent
units. Freeze the maximum attempts/windows and count-only extension rules;
never extend because a detection rate or confidence interval is disappointing.
[CHAIR, rulings 2/3/12 and §D; AP, D-062; MM, Statistical Protocol][CHAIR]

## Limits that belong in the discussion

These are irreducible scope limits of the proposed local experiment. A candid
discussion is necessary, but cannot rescue a title or abstract that asserts the
opposite.

| Limitation | What the discussion can honestly say | What would require new evidence |
|---|---|---|
| Semantics at fixed compute | Energy bounds unexplained work; it cannot identify the purpose of fully accounted computation. Successful within-pass or low-compute sabotage remains possible. | A broader semantic-security claim needs new mechanisms, not simply more precision at the meter. |
| Bounded adaptation | Robustness is against the tested policy families, feedback and budgets. No finite red team proves robustness to arbitrary future agents or unlimited optimization. | A stronger attacker/model and fresh sealed evaluation, whenever the claim expands. |
| Dedicated local hardware | Physical access and trusted acquisition fit an operator-controlled on-prem/edge audit. Host-compromised providers and off-host compute are outside this result. | A different trust architecture and threat-model evaluation. |
| Batching/datacenter transfer | Shared-serving marginal energy and per-request attribution are unresolved. No token-cost or threshold transfer is asserted. | A batch-level study with trusted scheduler/accounting and calibrated boundaries. |
| Reference-state measurement | G0/G1/holds trade throughput and latency for precision. Report gross energy, waits, monitor overhead and availability cost. | An ungated serving cohort before deployment-rate claims. |
| Task/model and unit breadth | Two pairs, one selected production model and one physical unit support named local findings. Extra seeds improve precision within that scope. | New task families/model families and independent physical replication before broader generality claims. |
| Release and novelty | Release reproducible code, synthetic fixtures and admissible artifacts through the owning gates. Describe novelty against the repository audit's adjacent literatures, with external-source rechecks by the lead before submission. | No claim that an offline literature audit exhausts future or inaccessible prior art. |

My main-track recommendation is conditional: retain v4 as the measurement
foundation, then make the adaptive joint-evasion assay the paper's decisive
test. If mixed cover or equal-compute sabotage defeats it, that is an important
negative result and a boundary on the squeeze. Suppressing that boundary would
make the paper weaker than the instrumentation deserves.

[V4]: https://github.com/mpmdw/JouleWise/blob/e901eb2a480d51377a494be9d797733dfcd0220b/docs/align/pilot_protocol_v4.md
[ER]: https://github.com/mpmdw/JouleWise/blob/e901eb2a480d51377a494be9d797733dfcd0220b/docs/align/energy_residual.md
[CHAIR]: https://github.com/mpmdw/JouleWise/blob/5ea21c17f837896b13e430a1e41b5ef9984ccd57/docs/align/council-2026-11-06-v4-review/CHAIR.md
[LIT]: https://github.com/mpmdw/JouleWise/blob/16e1db6230a80a605d084f0f9f61431d541b793f/docs/research-audits/2026-11-07/literature.md
[GATE]: https://github.com/mpmdw/JouleWise/blob/53a2305982a551ba5285e50bd0177726b5f138e7/docs/research-audits/2026-11-07/w1-prearm-gate.md
[PROGRAM]: https://github.com/mpmdw/JouleWise/blob/7f74dd2a97e5fcf078652deef2fb291929dc4524/docs/research-audits/2026-11-07/research-program.md
[AGENDA]: https://github.com/mpmdw/JouleWise/blob/fdb1e0409784096b1bfffbeea92d4e3d09a02ce0/docs/research/AGENDA.md
[TRIP]: https://github.com/mpmdw/JouleWise/blob/fdb1e0409784096b1bfffbeea92d4e3d09a02ce0/docs/research/energy-tripwire.html
[STATE]: https://github.com/mpmdw/JouleWise/blob/fdb1e0409784096b1bfffbeea92d4e3d09a02ce0/RUN_STATE.md#L1105-L1126
[AP]: https://github.com/mpmdw/JouleWise/blob/fdb1e0409784096b1bfffbeea92d4e3d09a02ce0/docs/contracts/analysis_plans.md
[CL]: https://github.com/mpmdw/JouleWise/blob/fdb1e0409784096b1bfffbeea92d4e3d09a02ce0/docs/contracts/claims_ladder.md
[MM]: https://github.com/mpmdw/JouleWise/blob/fdb1e0409784096b1bfffbeea92d4e3d09a02ce0/docs/contracts/measurement_methodology.md
