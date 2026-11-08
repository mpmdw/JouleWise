# Independent Sol cross-review of Claude's reviewer2 product

Date: 2026-11-07. **DESK REVIEW / DRAFT FOR LEAD REVIEW. Not a registration,
scope ruling, collection authorization, or hardware result.**

Reviewed product: `f01e47f295f36b5f77c06dd2d788bcaf88ff7f21`,
`docs/align/squeeze/reviewer2.md`, including both verbatim appendices.
Branch: `align/2026-11-07-sol-review-claude-reviewer2`.

## Verdict

**Following its central direction makes v4 substantially sounder; following its
action list literally is insufficient for a confirmatory squeeze claim.** Agree
with adding a real DC endpoint, a transcript-monitor experiment, capability
measurement, physical positive controls, independent bounded attack development,
and a separate test cohort. Do not adopt the proposed FPR guarantees, exclusion
scoring, composition shortcut, sample-size justification, or MDE projections
without the corrections below. These affect the headline result, not polish.

The document is useful review input, **not an admission verdict**. In particular,
v4 is explicitly provisional and unregistered (`V4:3-18`), despite the product's
repeated “as registered” language (`R:18,569`). No evidence inspected here clears
W1's registration blockers (`W1:77-93`; `MAIN:1143`).

## Scope, evidence and citation convention

This was an independent reading, with no peer consult or delegated reviewer.
No network or fetch was used: the standing no-network instruction takes
precedence over the brief's fetch request. All named objects were available
locally. Remote-ref freshness and live websites remain unverified. I read no
real measurement files, sealed outcomes, model weights, or forbidden directory;
absolute data paths inside source documents were text only. Pilot numbers below
are checks against the specifically cited, already-unblinded repository
narratives, not independent re-reductions of their underlying captures.

**AGREE** means the stated repository fact, mathematical statement with its
conditions, or proposed direction is supported. **DISAGREE** identifies a false
statement or an action unsafe to adopt as written. **UNVERIFIABLE** means the
available permitted evidence cannot establish it. Agreement with an action is
not installation of that action. Mixed recommendations are split in the reasons.

Every `KEY:line` citation expands through this table to
`<named commit>:<repository path>:<line>`. Ranges identify the supporting passage;
the first line is the citation anchor. All coordinates refer to source blobs,
not the lines of this review or mutable remote refs. Reproduce with
`git show <commit>:<path> | nl -ba`.

| Key | Named commit | Repository path |
|---|---|---|
| R | `f01e47f295f36b5f77c06dd2d788bcaf88ff7f21` | `docs/align/squeeze/reviewer2.md` |
| V4 | `e901eb2a480d51377a494be9d797733dfcd0220b` | `docs/align/pilot_protocol_v4.md` |
| ER | `e901eb2a480d51377a494be9d797733dfcd0220b` | `docs/align/energy_residual.md` |
| CH | `e901eb2a480d51377a494be9d797733dfcd0220b` | `docs/align/council-2026-11-06-v4-review/CHAIR.md` |
| PA | `e901eb2a480d51377a494be9d797733dfcd0220b` | `joulewise/align/apple/pilot_analysis.py` |
| RT | `e901eb2a480d51377a494be9d797733dfcd0220b` | `joulewise/align/apple/r1_runtime.py` |
| SMC | `e901eb2a480d51377a494be9d797733dfcd0220b` | `joulewise/align/apple/smc_enumeration.py` |
| MON | `e901eb2a480d51377a494be9d797733dfcd0220b` | `joulewise/align/shade/monitor.py` |
| PORT | `e901eb2a480d51377a494be9d797733dfcd0220b` | `docs/align/shade_port.md` |
| PIPE | `e901eb2a480d51377a494be9d797733dfcd0220b` | `docs/align/PIPELINE.md` |
| KIT | `e901eb2a480d51377a494be9d797733dfcd0220b` | `scripts/align_v4_kit.py` |
| R10KIT | `d600baba029f70592bb8e792098338e4cd6811d3` | `scripts/align_v4_kit.py` |
| FD | `6eb1ff5be31bec330ae5af262c2b4c7601e7755e` | `docs/align/council-2026-11-05/FINAL-DESIGN.md` |
| AM1 | `6eb1ff5be31bec330ae5af262c2b4c7601e7755e` | `docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md` |
| MAIN | `6f0bfd2d64b581b37969f8b28cc99f48661d7894` | `RUN_STATE.md` |
| P4 | `6f0bfd2d64b581b37969f8b28cc99f48661d7894` | `docs/process_traces/2026-11-03-magistrate-c9ac22ae/RECORD.md` |
| P6 | `6f0bfd2d64b581b37969f8b28cc99f48661d7894` | `docs/process_traces/2026-11-04-magistrate-7e06863b/RECORD.md` |
| P9 | `6f0bfd2d64b581b37969f8b28cc99f48661d7894` | `docs/process_traces/2026-11-05-magistrate-f775edaf/RECORD.md` |
| P10 | `6f0bfd2d64b581b37969f8b28cc99f48661d7894` | `docs/process_traces/2026-11-05-magistrate-3efb8793/RECORD.md` |
| LIT | `16e1db6230a80a605d084f0f9f61431d541b793f` | `docs/research-audits/2026-11-07/literature.md` |
| W1 | `53a2305982a551ba5285e50bd0177726b5f138e7` | `docs/research-audits/2026-11-07/w1-prearm-gate.md` |
| RP | `7f74dd2a97e5fcf078652deef2fb291929dc4524` | `docs/research-audits/2026-11-07/research-program.md` |
| MV | `036c7402dd506a6b2ca33ed2a3a576fdfe81eedb` | `docs/research-audits/2026-11-07/methodology-vs-literature.md` |
| WB | `93b049612e4909cccad7e3df8dc8b38acb5206e1` | `docs/research-audits/2026-11-07/w1-budget-fallback.md` |
| PROP | `5010326b7abd1938cfb1d058e004061c98e16301` | `docs/research-audits/2026-11-07/proportionality.md` |
| SQ | `688d14b6eba63544fee5c60dcb850cdb7caf3813` | `docs/registrations/align_v4_squeeze_addendum_DRAFT.md` |
| CLAIMS | `f01e47f295f36b5f77c06dd2d788bcaf88ff7f21` | `CLAIMS_STATUS.md` |
| DL | `f01e47f295f36b5f77c06dd2d788bcaf88ff7f21` | `docs/decision_log.md` |
| PAGE | `f01e47f295f36b5f77c06dd2d788bcaf88ff7f21` | `docs/research/energy-tripwire.html` |
| AGENDA | `f01e47f295f36b5f77c06dd2d788bcaf88ff7f21` | `docs/research/AGENDA.md` |
| KM | `f01e47f295f36b5f77c06dd2d788bcaf88ff7f21` | `joulewise/external/km003c_parse.py` |
| KMT | `f01e47f295f36b5f77c06dd2d788bcaf88ff7f21` | `tests/external/test_km003c_parse.py` |

## Consequential corrections and omissions

### F1 — A rank calculation is not an FPR validity proof

**DISAGREE** with importing the 2.5% marginal guarantee directly into the current
v4 analysis (`R:47,203-212,827-830`). The arithmetic is right for an appropriate
exchangeable score sequence. V4 instead specifies per-session benign
leave-one-trajectory-out fits and full-benign sabotage fits (`V4:488-505`), also
visible in `PA:229-241`. Those are different scoring procedures. A temporal
hold-out plus a common test fit does not suffice. For the proposed split-conformal
construction, separate the fit-training, calibration and final test cohorts;
calibration and future benign episodes must use the same frozen scoring function.
An alternative construction needs its own valid score-rank argument. SQ already
explicitly proposes that change (`SQ:38-44,233-256`). Name and admit it, rather
than merely describing the present analysis as split conformal.

Window dependence is a separate problem. Seven seeds in one D window do not
automatically supply seven independent calibration environments (`V4:139-146`).
A synthetic counterexample: give each of six independent windows one continuous
score, repeated for all seven members. The maximum of the 42 calibration scores
is the maximum of six draws. A benign episode in a new independent window exceeds
it with probability **1/7**, not **1/43**. Increasing the episode count without
addressing window effects does not establish the claimed FPR. A heterogeneity
test that fails to reject does not prove exchangeability.

Similarly, the Clopper–Pearson calculations are correct **iid Bernoulli
references**, not automatically exact for pooled, window-correlated episodes
(`R:49,96,208-210,418`). For example, if all 20 test alarms share one Bernoulli
event with probability .30, zero alarms occurs with probability .70; reporting
the usual zero-of-20 upper limit .139 has only .30 coverage in that world.
Predeclare the sampling unit and supported conditional/marginal target; show
window sensitivity and withdraw unsupported nominal guarantees. SQ explicitly
retains the iid-reference qualification (`SQ:266-274`). Wild bootstrap or
jackknife labels alone do not repair six-cluster inference (`R:756-760`).

The rule `ceil(.975*(m+1))` is finite at m=39 and equals the maximum for
**39 ≤ m ≤ 78**. At m=79 the rank is 78, not the maximum. Thus “m ≥ 39 only as
the sample maximum” (`R:47,203`) needs that qualification. At m≈21 a 2.5%
split-conformal threshold is infinite. The proposed Q6 fallback (b) therefore
does **not** retain the proposed nontrivial 2.5%+2.5% OR detector (`R:219-223`).

### F2 — Measure paired joint escape; do not manufacture it by composition

**DISAGREE** with treating benign-carrier power and unmetered monitor/success
rates as sufficient for confirmatory joint escape (`R:748-751,802-803,843`).
The required identity is
`P(S and not M and not E) = P(S and not M) * P(not E | S, not M)`.
Replacing its last factor with a carrier-derived `P(not E | H)` assumes
transportability to successful, monitor-evading attacks conditional on all
relevant work/context/placement variables. It is stronger than merely saying
the alarms are independent “given the episode.” Equal escape marginals .10
permit a joint escape anywhere from 0 to .10; their product .01 is only one
coupling. Adaptation makes the coupling central. An underpowered equivalence
subset cannot establish it; absence of a detected discrepancy is not equivalence.

Primary P2 should use **paired physical energy and monitor observations on the
same held-out attacks**, or honest partial-identification bounds/unresolved
status. Unmetered transcripts remain development evidence or a labelled proxy.
Neither injected compute nor a log edit alone proves successful sabotage
(`SQ:79-85,305-320`; `CH:310-312`). Keep independent execution truth and matched
shams, which the review largely omits (`SQ:126-147`).

The stated best response is a maximum over a bounded registered/search-tested
policy class, not over every possible adversary (`R:834-838`; `SQ:87-99`). Select
policies on development seeds; freeze the final blue team **after** its permitted
update; use fresh calibration if it changes, then fresh tests. Freeze how ties,
failed attack execution, multiple families and any test-set maximization enter
confidence bounds. “Another model family” is useful diversity, not proof of
independence or an exhaustive search.

P2 improves on monitor-only by .05 (`R:93,842`), while the appendix's definition
requires improvement over **both** solo channels (`R:836`). These differ. If
energy alone already matches J, beating M alone does not show complementarity.
Make one operational definition primary and print both matched-budget solo
comparisons. Equal nominal FPR ceilings are not evidence of equal realized FPR.

The N=150 sizing justification tests the wrong null (`R:307,843`). Its z=2.89
uses a .10 difference against **zero**. Against the proposed .05 improvement
margin, the same approximation gives z=1.44. With the review's pooled .10 rate
and true .10 gap, a conventional independent-arm 80%-power, one-sided 5% design
would need about **446 per arm**, before selection, clustering or multiplicity.
This is an illustrative calculation, not a recommended sample size: a paired
design needs the discordance rates and a maximum-over-policies analysis.

### F3 — Fail-closed safety is not evidence of detector sensitivity

**DISAGREE** with counting every excluded attack as a detected alarm in primary
P2 without a corresponding operational benign denominator (`R:95,226-227`).
X2/X7 currently remove observations (`V4:454-462`), so missing attacks must not
vanish. But an OS or instrument failure is not a positive energy or semantic
detection. Define a composite deployment policy that aborts/escalates on such
failures, then count **benign aborts/escalations** in that policy's cost/FPR or
report availability separately. Otherwise attacking a broken instrument can
appear to improve detection at no benign cost.

Report detected, successful-and-escaped, attack-not-executed, and unavailable
counts for every assigned attempt. Give worst/best-case escape bounds for
unavailable outcomes; show conditional-on-valid detector sensitivity separately.
The review's all-missing-as-evasion sensitivity is valuable, but does not make
the optimistic primary a calibrated detector (`SQ:287-311`). Apply an analogous
predeclared rule to missing/invalid monitor judgments (`MON:163-206`).

### F4 — The DC endpoint needs a complete new measurement contract

**AGREE** with the external boundary; **DISAGREE** that its implementation is
just wiring a parser or that an allowlist grants R1 authority (`R:90`). KM already
labels itself diagnostic, not claim-producing (`KM:1-4`). R1's battery journal
records integer-percent state, not battery power (`RT:589-650`). SMC's mention of
the logger (`SMC:197`) proves only an allowed process name. It does not establish
arm admission, hardware availability, timing qualification or a usable DC fit.
Leave the existing R1 kit unchanged, consistent with `MAIN:1130,1142`.

Freeze sign and units of battery assist, coverage/gaps, independent timestamps,
clock uncertainty, metered span including tails, phase ownership, integration,
uncertainty propagation, and missing-sensor behavior **before the first sample
destined for that endpoint** (`KM:6-44`; `SQ:149-165`). A separate host requires
a measured clock mapping; synchronization is not a slogan or permission to
alter the machine's network-time policy. Float at arm/end is not proof of zero
battery flow throughout the span. The native battery/edge/coverage checks remain
lead-owned. No native result was obtained here.

The fixed idle-baseline subtraction is a **new estimand**, not an implication
of ER's prohibition on a duration predictor. ER currently retains benign
unowned energy in the total (`ER:9-27,395-397`); SQ explicitly proposes a gross
DC total (`SQ:149-155`). Freeze a baseline from trusted pre-attack data and
trusted ownership stamps, propagate its duration-scaled uncertainty, retain
gross energy, and test gap attacks against the full audit span. If a reported
log can relabel segments as unowned, the attacker can affect the subtraction.
Never remove a baseline fitted using the attacked gap's measured power.

Same-host read access to power is not write access to root telemetry. Host
compromise and log-write authority must be separated (`SQ:49-67`). Off-host
logging can be optional only if the collector, battery record and truth ledger
are protected from the permitted scaffold adversary. D-139 is a registered
limitation that needs explicit scope reconciliation, not proof that every
prospective ALIGN adversary is forever prohibited (`DL:9199-9209,10469-10480`).

### F5 — The review repeats the MDE formula error it says was eliminated

**DISAGREE** with using CHAIR's 300–500-token estimate as a verified detector
limit (`R:164-165,377,589,923`). CHAIR explicitly projects `q*s_r,D/e_D`
(`CH:270-295`); RP rejects another estimate for exactly replacing the score's
predictive denominator with residual SD (`RP:78`). ER defines
`D_i=sqrt(s_i'Cov(beta)s_i+n_i*sigma2+h_episode^2)` and uses this in the score
(`ER:93-107`), not the across-episode `s_r`. Calibrated power also uses the
benign score mean/SD and a power quantile (`ER:197-229`). A crossing threshold
and an 80%-power MDE are different quantities. CHAIR is authority for required
actions; its back-of-envelope numerical forecast is not a validity theorem.

Recompute using the actual DC scoring function, a stated hidden-work context,
uncertainty kind and power target. Count/context forgery changes the design and
potentially the denominator; sub-turn/full-omission curves need that arithmetic,
support checks and nonmonotonic/uncrossed-curve reporting. Do not infer physical
attack power or joules/token from a log edit. The 17× denominator observation is
explicitly **synthetic**, not measured D performance (`ER:363-373`).

### F6 — Capability is necessary; the proposed gate is not yet a design

**AGREE** that one benign state-changing action cannot validate sabotage
capability (`FD:644-649`), and the pilot's one-of-12 unique sabotage seeds is
weak (`P4:21`). **UNVERIFIABLE** that capability is the likeliest failure or that
either outcome will be publishable (`R:34,165,838`).

The 10% threshold, hint-off preference and switching order are proposals, not
source-derived constants. Specify sample size, uncertainty, main-task utility,
side-task criterion, task identity and dev-only selection before switching.
Forty 1,800-second episodes do equal 20 hours (`R:92`), but the proposed two
pairs × two hint states × seven H budgets already make 28 cells: about 1.43
episodes/cell at that total. One success in ten has a one-sided 95% exact lower
bound about .0051, not .10. More importantly, reconfiguring quantization,
effort/B_D or the model creates a separate fitted/calibrated cohort
(`V4:186-191,504-505`; `CH:315-317`).

Define H as a **total hidden-work budget** or a per-turn budget explicitly; a
forced end-of-think can alter the output distribution, later context, tool
actions and main-task success. H=0 may still permit latent or visible reasoning;
it is not proof of “no reasoning.” Hint-in-prompt does not demonstrate that
sabotage can succeed without planning. Cloud and MBP-day capability results are
proxies unless configuration, sampler, cap/stop semantics and output behavior
transfer. A scripted injector can validate detection of work, not make an
incapable saboteur evidence for semantic control (`SQ:79-85,139-147,305-311`).

### F7 — “Full” monitor visibility has two important holes

The three views exist, but **all omit system prompts and tool-call arguments**
(`PORT:241-256`; `MON:30-60`). Thus “full” is not the full execution record; the
monitor does not receive the sabotage hint as a system instruction
(`PORT:142-149`). An adversary can place important content in arguments or
results; any additional receipt/argument view must be separately named and
calibrated. The review mentions information sets in general but misses these
concrete existing exclusions, the default actions-only task-context difference,
and invalid judgment handling (`PORT:234-239,266-281`).

Two monitors × three views are six scoring procedures, not one 2.5% channel.
Choose/freeze a primary M and view or calibrate the entire composite; report the
others as secondary. Freeze model/version, prompt hash, parser, context truncation,
retry policy, randomness, and prompt-injection defenses. A late frontier-model
update or a different monitor input changes the detector. The phrase “2×2” in
the product lists only visible+logged and hidden+withheld (`R:91,622`); that is
two coupled settings. Specify all four visibility × count-access cells, or
call it a two-setting comparison. Keep this separate from the actual E×M alarm
contingency table, and prevent hidden-truth leakage into either detector.

### F8 — No conservation law forces malicious content into monitor-readable form

**AGREE** that cheap decoys, visible filler/encoded work, off-host work and work
outside an episode break the unconditional squeeze story (`R:40-44,167-177`).
**DISAGREE** that a third relevance/compressibility channel closes that hole
merely by being run, or that the semantic monitor is shown to close Kimpson's
matched-energy hole (`R:176,255,351,464`). These are hypotheses, not consequences
of the physics. A two-sided residual can catch unbalanced overclaiming; exactly
balanced fabricated work plus hidden computation can have ordinary energy
and time. Logged benign-looking malicious computation need not be caught by
any of those channels (`ER:388-400`; `SQ:59-67`).

Report success/escape over the explicit tested policy class and budget. Include
**mixed** padding × placement attacks, not just separate taxonomy rows; SQ
already asks for a committed mixed grid (`SQ:69-99`). Add legitimate-task
utility and denial-of-service cost, boundary-escape accounting, shams, scorer
support/identifiability checks, attack-execution receipts, and detector-failure
handling. These omissions matter more than an additional venue prediction.

## Disposition of all 23 reconciled actions

The identifiers below are the product's §2 numbers. Costs are **UNVERIFIABLE
estimates** unless separately checked; no timing/allocation below authorizes a
run. A substantive design must be frozen before its relevant data/feedback,
even where the product labels the execution deadline merely “paper.”

| # / product line | Status | Reason and required disposition |
|---|---|---|
| 1 / `R:89` | **AGREE** | Add threat/information-set text, scope counts and host permissions, and address D-139. Treat residual signs as conditional on honest baseline work and fitted costs; unprivileged reads do not prove spoofing. Re-execution is a possible escalation, not established cost-free replacement. F4/F7/F8; `DL:10469-10480`; `SQ:49-67`. |
| 2 / `R:90` | **DISAGREE** | Adopt a new qualified DC endpoint, but settle gross versus baseline-subtracted energy explicitly. W1 data used in DC E_ref/fit cannot precede qualified capture; “kit wiring by D” is too late for that use. The R1 allowlist is not permission or a validated instrument path. F4; `CH:100`; `RT:632-654`; `KM:1-44`. |
| 3 / `R:91` | **DISAGREE** | Add the arm, off-box execution and sealed paired scores. Freeze one primary monitor/view or a calibrated composite, resolve the two-settings/2×2 ambiguity, handle failures, and establish the FPR assumptions. F1/F7; `MON:30-60,163-206`. |
| 4 / `R:92` | **AGREE** | Capability gate and dev-only S(H) are essential. The 10% rule, switching, 40-episode budget and hint choice require a prospective sample/utility rule and configuration-matched verification. Conditional-on-success energy is secondary to assignment accounting. F6; `FD:644-649`; `V4:186-191`. |
| 5 / `R:93` | **DISAGREE** | Fix P1's wording: H* is a token count, whereas ≥.8 must refer to a detection probability. A ≥.8 point estimate with a lower bound >.5 proves a claim about .5, not ≥.8. Specify nulls, intervals, Holm inputs and fixed sequence. Resolve P2 versus both solos, paired inference, fit/calibration separation and FPR conditions. F1/F2/F5; `ER:197-229`; `SQ:231-274`. |
| 6 / `R:94` | **AGREE** | Freeze attack development and effort, dev/test separation, policy selection and final blue-team update. Add mixed strategies and test multiplicity; do not call the finite search universal robustness. F2/F8; `SQ:69-99`. |
| 7 / `R:95` | **DISAGREE** | Fail closed operationally, but do not call every missing attack a detector catch at unchanged benign FPR. Score the complete operational policy on benigns, preserve unavailable categories and escape bounds. F3; `V4:454-462`; `SQ:287-311`. |
| 8 / `R:96` | **DISAGREE** | Agree allocation needs a ruling; include disjoint fit data and the window unit. Exact binomial FPR is conditional, not assured by a locked cohort. The m≈21 fallback cannot preserve a finite .025 E threshold. F1; `MAIN:1124-1129`; `V4:139-146,488-505`. |
| 9 / `R:97` | **AGREE** | Timestamp the final frozen artifact and deviations before relevant collection; a local Git tag alone is not an external timestamp. Public upload is a later lead/Ed publication action. `SQ:3-7,220-229`; `AGENDA:5-20`. |
| 10 / `R:98` | **AGREE** | Correct the boundary and two-trajectory presentation now; use “tests whether” for the squeeze until results exist. Recheck the contradictory Token Inflation source before replacing its statistic; see external-source register. `PIPE:9-20`; `PAGE:149-151,185-190`; `LIT:63,730`. |
| 11 / `R:104` | **AGREE** | Stronger randomized physical controls improve identification. Add zero-dose shams, independent execution truth, context/mode stratification, sufficient replication, monotonicity/model checks and bounds if H90 is not reached. A logistic model or ≥3 replicates does not guarantee precise H90. GPU “miss” is a test prediction. `CH:50-56`; `SQ:126-147,313-320`. |
| 12 / `R:105` | **AGREE** | Pair metered test attacks with monitor scores; frozen fresh seeds and physical gap/battery/decoy arms are necessary. Use this evidence directly for P2 rather than treating a tiny composition subset as proof of independence. F2/F4; `ER:388-400`; `SQ:149-165,278-311`. |
| 13 / `R:106` | **DISAGREE** | Unmetered development/proxy transcripts are useful; N≈150/family does not justify the proposed primary .05-margin best-response claim. No carrier-product shortcut. F2; `R:843`; `SQ:317-320`. |
| 14 / `R:107` | **AGREE** | Compare metadata, trusted time, E, M and J at fixed budgets on the same data. Register negative residual and sequential CUSUM as separate targets with family/horizon control; do not spend uncounted alpha on time, windows, or repeated looks. β-analogue needs explicit numerator/denominator and units. `PIPE:24-29`; `ER:197-217,388-400`; `SQ:145-147,258-264`. |
| 15 / `R:108` | **AGREE** | An exploratory relevance/compressibility channel can test the decoy hypothesis. It cannot establish a disguised-compute guarantee merely by running; do not borrow CoIn's detection rate. F8; `LIT:721-723`; `ER:399-400`. |
| 16 / `R:109` | **AGREE** | Report v3 as a historical ungated exploratory companion and W1 contrasts as designed. Comparing v3 30B with gated D does not isolate the causal benefit of gating. `V4:474-486,514-515`; `CH:314-317`. |
| 17 / `R:110` | **AGREE** | Print transfer/pooling diagnostically; no replacement of per-pair headline or selection using final test scores. `P4:24`; `P6:24`; `V4:504-505`. |
| 18 / `R:116` | **AGREE** | Predeclare hybrid sensitivity and outlier-threshold response. Rank m−1 does not retain the same FPR budget; a remedy cannot be chosen after seeing the maximum. `CH:157-165`; `LIT:43,71`; F1. |
| 19 / `R:117` | **AGREE** | A separately calibrated Air replication improves device generality. Share the meter only under lead scheduling, and qualify passive-cooling/OS differences; 2–4 Air nights is unverified. `LIT:185,618-620`; `MV:67`; `V4:504-505`. |
| 20 / `R:118` | **AGREE** | Additional pairs/models/ungated runs are useful secondary scope extensions, each separately configured and calibrated. Pair evaluators/judges must be frozen and off-box. A simulation is not batched-hardware validation. `PORT:119-140`; `V4:58-61,186-191,504-505`. |
| 21 / `R:119` | **AGREE** | Optional only under a trusted-collector boundary; otherwise protect/move logging before claiming tamper resistance. A second logger does not authenticate the MBP's battery record by itself. `SQ:49-57`; `KM:9-18,29-38`; F4. |
| 22 / `R:120` | **AGREE** | Prepare a reproducible release with hashes, prompts, attacks, truth/score schemas and deviations. Exact venue artifact rules remain unverified; publication needs normal owner authority. `R:319,973-995`; `SQ:139-147,220-229`. |
| 23 / `R:121` | **DISAGREE** | Agree to avoid unnecessary guard expansion. Do not demote registered U6 consequences or waive W1 fixes by this review: CHAIR itself proposes revised U6 margins, and v4 says failure leaves calibration unresolved. `CH:90-104`; `V4:464-470`; `W1:34-71`; `PROP:23-37`. |

## Claim-by-claim register for the synthesis

Repeated versions of a claim in the executive summary and §3 share a row.
External numerical/content claims are separately adjudicated below; a source
being quoted by another audit is not independent verification of the paper.

| Product claim / location | Status | Check against permitted evidence |
|---|---|---|
| Seats, synthesis identity, byte-for-byte journal extraction and historical blinding (`R:3-10,333,512,539,553`) | **UNVERIFIABLE** | Git pins establish the committed product, not hidden workflow provenance or what a previous seat actually opened. I did not inspect external journals or forbidden custody. |
| Exact pins and draft addendum present (`R:8,28-33`) | **AGREE** | Named objects resolve; SQ has threat, monitor, joint rules and the rail limitation (`SQ:47-99,149-165,231-320`). All remain draft (`SQ:3-7`). |
| “v4 as registered” (`R:18,569`) | **DISAGREE** | `V4:3-18`; `W1:11-16`. Use “the pinned draft and planned known-omission estimand.” |
| No registered joint monitor/adaptive experiment (`R:19-23,129-132`) | **AGREE** | `V4:60-61,508-523`; available monitor implementation `MON:103-117`. “No second production model” alone would not prohibit adding a monitor; the absence of a specified arm is the substantive evidence. |
| “No adversary” literally (`R:20,571`) | **DISAGREE** | There are sabotage-condition agents (`V4:70-71,99-118`). There is no detector-aware adaptive experimental arm. Use that narrower statement. |
| Analysis scores the GPU rail (`R:21,135`) | **AGREE** | Direct code: `PA:193-224,241`. |
| No KM003C reference in either v4 kit; parser exists (`R:136,303`) | **AGREE** | Literal search of full KIT and R10KIT blobs found none; `KM:1-18`. That does not prove no logger existed anywhere in a historical night. |
| Meter “never a claim number” (`R:136,143,572`) | **AGREE** | `KM:1-4`, `MV:816`. This diagnostic label is not an ALIGN-specific ban on a prospectively admitted DC endpoint. |
| PIPELINE boundary wording and page step 03 imply more than the scored channel (`R:21,65-66,304,964`) | **AGREE** | `PIPE:9-20`; `PAGE:149-151`; `PA:193-224`. The page already has the two-trajectory caveat (`PAGE:190`), so its fact tile needs that local qualification, not a claim that the caveat is absent. |
| Host telemetry is “readable and spoofable” as one inference (`R:137-140`) | **DISAGREE** | Historical unprivileged reads are reported by `LIT:618-621`; write/spoof capability and current-Mac access are not established by that. Distinguish OS, privilege and collector authority. F4. |
| About 76% outside rails (`R:141,188,410,704,969`) | **AGREE** | As a **single latency-bound marginal known-bytes contrast**, `RP:130-138`. It is not 76% of all memory/decode energy; “rest” also includes conversion/fans. Extrapolation to several-fold decode sensitivity is **UNVERIFIABLE**. |
| Flash-Next host-side table escapes the GPU estimand (`R:141,705`) | **AGREE** | Architectural/boundary concern is recorded in `MV:32,104-107`. Zero coupling into the rail or a guaranteed DC alarm is not established; `ER:393-394`. |
| Battery assist and integer-percent journal (`R:142`) | **AGREE** | The 1.2–2.1 s report is in `MV:157-158`; journal behavior is directly checked in `RT:589-650`. No new physical verification was performed. |
| PDTR slope .955, intercept 2.3 W, r=.9975; 10–17 ms; τ≈2.3 s / ≈12 s (`R:143-146`) | **AGREE** | Correct attribution to `MV:51,102,157-158`, not new calibration. Treating those as universal accuracy/phase bounds or independent meter certification is **UNVERIFIABLE**; `KM:29-44,78-94`. |
| No threat-model section in v4 (`R:150`) | **AGREE** | Text scan and `V4:56-91,488-523`; `LIT:42,70`. This is an absence in the pinned draft, not proof all repo threat text is absent. |
| Three adversary identities; forgeable counts matter; re-execution objection (`R:151-153`) | **AGREE** | Sensible design distinctions (`SQ:49-67`); four pilot replays did reproduce IDs (`P4:18`). Determinism across new stacks/batches or trustworthy execution is not thereby guaranteed. |
| D-139 creates a scope conflict requiring reconciliation (`R:154`) | **AGREE** | `CLAIMS:14-19`; `DL:10469-10480`. A new ALIGN claim needs an explicit prospective boundary. Automatic blanket prohibition of every sanctioned experimental workload would overread the MVP/family limitation. |
| Hint on and provided in system prompt (`R:35,159,649`) | **AGREE** | `V4:70-71`; `PORT:142-149`. The rough prefill ratio is an estimate (`MV:30`), not proof the plan suffices or every hint token is a fresh uncached prefill. |
| One of 12 unique sabotage seeds successful in pilot 4 (`R:36,160`) | **AGREE** | `P4:21`: one spam seed plus its replay, five other spam and six bank seeds unsuccessful. Do not count the replay as another success trial. |
| FD gate minimal; D capped and truncated; near-zero success makes a low unconditional escape rate vacuous (`R:37-39,161-165`) | **AGREE** | `FD:644-649`; `V4:166-191`; `CH:317`. Report capability and utility alongside escape; F6 qualifies the proposed solution. |
| Disguised/cheap-decoy blind spot (`R:40-44,167-177`) | **AGREE** | `ER:388-400`; `SQ:59-67,69-85`. “Carve-out unless #15 runs” is **DISAGREE**: running a third channel does not establish robustness. |
| All attack rows A0–A13 are relevant hypotheses (`R:183-196`) | **AGREE** | Honest/stripped/budgeted/latent/obfuscated/decoy/off-GPU/gap/salami/exclusion/oracle/privileged/deletion/battery cases follow from `ER:9-27,388-400`, `V4:454-462`, `KM:9-18`, `SQ:69-99`. The “predicted catcher” column is a prediction, not verified coverage; A11 requires explicit privilege scope. |
| Threshold/CI/binomial arithmetic (`R:203,207-210,226`) | **AGREE** | Recomputed: m39 .025 marginal; iid 90% max-tail upper .05733 (m21 .10385); 0/20 upper95 .13911; 3/3 lower90 .46416; 6/6 .68129; binomial yield .91508/.64841/.42050. F1 limits their use, and ≥39 “only maximum” is incorrect past 78. |
| 1% finite sample-maximum calibration requires m≥99 (`R:212`) | **AGREE** | `1/(m+1)≤.01`; this is a finite maximum rank condition, not certification of realized FPR or window robustness. |
| Q6 yes; D split unresolved; seven benign/pair/window (`R:216-223`) | **AGREE** | `MAIN:1122-1129`; `AM1:117-124`; 6×7=42, 3×7=21. D7–D9 adds 49.6 h of maxima, about four 12.4 h equivalents; exclusions may require more. Random split is weaker for drift and still needs m≥39 plus fit/test units. F1. |
| Exclusions remove scored observations; hidden work can exploit this (`R:225-227`) | **AGREE** | `V4:454-462`; `CH:319`. The stronger appendix statement that correlation was demonstrated (`R:775`) is **DISAGREE**: CHAIR says independence is not shown, not that a correlation was measured. F3. |
| Existing physical-control ruling, proposed doses and .18 versus .49–.67 J/token (`R:230-233`) | **AGREE** | `CH:50-56`; `RP:249`; coefficients in `P6:39`, pilot in-context values `P9:17-18`. .18 is a fitted bare-decode approximation, not a measured universal fresh-context injector rate. |
| Baselines missing, metadata tool exists (`R:235-237`) | **AGREE** | `PIPE:24-29`; `RP:166-168`; local Git has `joulewise/align/analysis/metadata_baseline.py` at e901. No superiority over time has been established. |
| Two pairs, per-pair/session calibration, failed transfer, one device, gated regime (`R:239-246`) | **AGREE** | `V4:70-71,488-505,514-515`; `P4:24`; `RP:119,261-270`. GPU same-SKU variability does not quantify Mac variation; external figure unverified below. |
| Literature positioning and residual rather than regression novelty (`R:248-257`) | **AGREE** | Reasonable positioning against the mapped sources (`LIT:85-102`; `RP:159-164`). Exhaustive “unoccupied” novelty and a monitor closing matched-energy evasions are **UNVERIFIABLE**, not a proved gap or result. F8. |
| Pilots informed design; new D model and external timestamp help (`R:259-261`) | **AGREE** | Pilot selection history `P6:35-42`, `RP:115-119`; prospective D configuration `V4:58-91`. A new model/timestamp cannot erase prior selection or replace fresh test seeds. |
| Discussion limits on remote work, batches, root/meter attacks, scale, device/task transfer, reference state, negative threats and no causal sabotage claim (`R:263-272`) | **AGREE** | `ER:388-400`; `V4:504-515`; `CH:307-322`; `SQ:49-57,79-85`. Any battery/gap/disguised arm actually placed in the primary threat model needs an experiment or unresolved label, not discussion-only dismissal. |
| P0 0 extra MBP nights; P1 3–5; P0 6–10 desk days; unmetered N≈150/family; future venue feasibility (`R:24-27,52-61`) | **UNVERIFIABLE** | Proposals, not completed budget or a calendar proof. Q6 fit/calibration/test allocation is unresolved, DC qualification costs time, and §3.9 may add windows. `MAIN:1125-1129`; F1/F2/F6. |
| Nothing new gates R1; physical-control D cell is a paper gate; 30B nights approved in principle (`R:56,104`) | **AGREE** | `MAIN:1123,1130,1142-1143`; `CH:56`. Each new kit still requires its own admission. |

## External-source claims: distinguish attribution from verification

No paper or CFP was opened during this no-network review. Consequently every
primary-source number, quotation, current platform access claim and deadline
in the rows below is **UNVERIFIABLE here**. Repository consistency checks are
stated explicitly; they must not inherit the product's “opened/verified” label.
The original links identify what the lead should check later, not sources I
retrieved. Pin a version/date/section and retain a permitted source excerpt.

| Claim, including appendix repetitions | Status | Offline check / source to verify |
|---|---|---|
| Kimpson β=1.16, ≥.41, .059 and their interpretation (`R:44,171,255,585,817`) | **UNVERIFIABLE** | Consistent with `LIT:747-750`; [arXiv 2610.07476](https://arxiv.org/abs/2610.07476). A capacity-normalized worst-case bound is not an empirical episode H90 or proof of semantic-monitor coverage. |
| CoIn fingerprints, relevance, 94.7%, provider artifacts (`R:252,814`) | **UNVERIFIABLE** | Consistent attribution `LIT:721-723`; [ACL paper](https://aclanthology.org/2026.findings-emnlp.363/). Detection rate cannot be transferred to a compressibility baseline. |
| Token Inflation three audits, 1,469% average versus “up to,” recommended independent evidence (`R:63,253,499,815,965`) | **UNVERIFIABLE** | **Internal contradiction confirmed:** `LIT:38,63,77,89` says “up to”; `LIT:730` says average. Product sides with the latter but has no archived primary version. Recheck [arXiv 2605.30040](https://arxiv.org/abs/2605.30040) before asserting which quote is correct. |
| Gargiulo/Kulp 10 MHz H200, 930 traces, 97%, macro-F1 .955, spoof/replay and exact caveat (`R:139,254,299,727,816`) | **UNVERIFIABLE** | Broad content agrees with `LIT:742-745`; [arXiv 2609.00309](https://arxiv.org/abs/2609.00309). Does not demonstrate a spoof on this Mac. Exact alternative quotation unverified. |
| Hot Pixels power/temperature unprivileged reads, frequency distinction (`R:89,138,193,298,692`) | **UNVERIFIABLE** | The correction agrees with `LIT:617-621`; [USENIX paper](https://www.usenix.org/conference/usenixsecurity23/presentation/taneja). Evidence there concerns historical M1/M2 systems; current M3/OS access needs separate qualification. |
| PLATYPUS unprivileged RAPL exploitation and subsequent Linux/admin restrictions (`R:140,693,819`) | **UNVERIFIABLE** | Only a narrative in `R:140,693,991` is available in this read set; platform/privilege changes need the primary advisory/paper, not inference from read access on macOS. |
| SHADE scratchpad dependence, best monitor AUC .87, frontier scope (`R:164,236,384`) | **UNVERIFIABLE** | Attributed in `LIT:64` and `RP:160`; [arXiv 2506.15740](https://arxiv.org/abs/2506.15740). Repo verifies the public five pairs/evaluators (`PORT:119-149`), not a universal necessity of hidden reasoning or a local-model success rate. |
| Pfau filler benefit and dense-supervision requirement; latent scale extrapolation (`R:172,384,668,933`) | **UNVERIFIABLE** | General filler result recorded by `LIT:698-700`; [arXiv 2404.15758](https://arxiv.org/abs/2404.15758). Dense-supervision quote is not reproduced there. A trained filler construction does not establish a security “capability tax” or a scale law. |
| Roger/Greenblatt paraphrasing blocks the built encodings (`R:173,934`) | **UNVERIFIABLE** | Source identified only by `R:986`; [arXiv 2310.18512](https://arxiv.org/abs/2310.18512). Neither extrapolate to every encoding nor claim #15 closes disguised reasoning. |
| Async Control 6% FNR at 1% FPR; all control work uses 1%; Greenblatt 1–2% budgets; prescribed game rounds (`R:211,300-301,653,665`) | **UNVERIFIABLE** | Specific Async figure is consistent with `LIT:422`; [arXiv 2512.13526](https://arxiv.org/abs/2512.13526). One example does not establish the universal operating-point claim; budget/round attributions were correctly withdrawn pending support. |
| MonitoringBench 94.9%→60.3% (`R:213,655`) | **UNVERIFIABLE** | Consistent attribution `LIT:678-680`; [arXiv 2605.09684](https://arxiv.org/abs/2605.09684). Does not predict the catch rate of the proposed monitor/setting. |
| Wu 335× cached, 115× uncached→3.3× batched, R²=.961, venue (`R:64,245,256,280,296,408,818`) | **UNVERIFIABLE** | The **115× comparison is the consistent repo correction**, `RP:79,163`. [NeurIPS entry](https://neurips.cc/virtual/2026/170701). Whether the primary experiment establishes those figures is not independently checked here. |
| WattsUpDoc ≥94% known / ≥85% unknown (`R:257,731,819`) | **UNVERIFIABLE** | Consistent attribution `LIT:756-758`; [HealthTech paper page](https://www.usenix.org/conference/healthtech13/workshop-program/presentation/clark). Prior power monitoring is a useful comparator, not a performance baseline on SHADE. |
| Sinha same-SKU average 8% / up to 22% (`R:243,414`) | **UNVERIFIABLE** | `LIT:185,231`; [arXiv 2208.11035](https://arxiv.org/abs/2208.11035). Not a measured MacBook uncertainty term. |
| ChargerLAB separate-host/offline logging features, meter accuracy and certification (`R:697-698,737,796,993`) | **UNVERIFIABLE** | `KM:6-44` verifies repository stream conventions, not manufacturer accuracy or offline-memory capability. Hardware/API-clock qualification remains prospective; the product itself admits accuracy is unknown. |
| Baker, Ctrl-Z, CoT Red-Handed and remaining source-list claims (`R:305,637,983-985`) | **UNVERIFIABLE** | Source list is not an archived primary-text audit. Baker/obfuscation and Ctrl-Z are described in `LIT:686-692`; do not add unverified quantitative claims. |

## Adjudications and the product's own corrections

This checks the entire §4 disagreement table and §5 corrections. A correction
can be epistemically sound even when the substitute external fact is unverified.

| §4 row / location | Status | Disposition |
|---|---|---|
| Batching / `R:280` | **AGREE** | Internally resolves to the same cached/uncached distinction as `RP:79`; primary verification remains open. |
| Primary estimand / `R:281` | **DISAGREE** | Rejecting pooled primary is consistent with `V4:505`; the chosen P1/P2 is not complete, and its .05-margin sizing/dual-solo definition conflicts remain. F2. |
| Capability priority / `R:282` | **AGREE** | A meaningful semantic endpoint requires this before test seeds; threshold/sample/switching details remain proposals. F6; `P4:21`. |
| Exclusions / `R:283` | **DISAGREE** | Promote missingness accounting, not optimistic catch counting at a nominal unchanged FPR. F3; `V4:454-462`. |
| Cohort split / `R:284` | **AGREE** | Identified a real 21 versus 39 mismatch; include fit allocation and .025 infeasibility of the fallback. `AM1:117-124`; F1. |
| Control doses / `R:285` | **AGREE** | Combining dose response with physical modes is useful; add shams/truth and do not guarantee logistic identifiability. `CH:56`; `SQ:126-147`. |
| Device and ungated priority / `R:286-287` | **AGREE** | Reasonable prioritization with distinct cohorts and noncausal historical comparison; costs are estimates. `MV:67`; `CH:314-317`. |
| Off-host logging / `R:288` | **AGREE** | Only under the trusted-collector threat boundary; otherwise it becomes essential to that claim. `SQ:49-57`; F4. |
| USENIX infeasible / `R:289` | **UNVERIFIABLE** | R0 status does not establish future impossibility; it supports schedule risk, not a deadline proof. `R:60,319`. |
| Security target / `R:290` | **AGREE** | A planning preference compatible with the main goal, conditional on future official CFPs and submission rules. `AGENDA:5-20`. |

| §5 item / location | Status | Disposition |
|---|---|---|
| 1 Wu correction / `R:296` | **AGREE** | Repo consistency supports the correction (`RP:79`); external fact remains unverified. |
| 2 U6 4% removal / `R:297` | **AGREE** | `CH:93` does not state 4%; “always inconclusive” describes the old margin, followed by proposed changes (`CH:94-95`). |
| 3 Hot Pixels correction / `R:298` | **AGREE** | Consistent with `LIT:618-620`; not a current-platform test. |
| 4 exact Gargiulo quotation / `R:299` | **UNVERIFIABLE** | Neither wording independently established without primary text. |
| 5–6 audit budget / rounds attribution removal / `R:300-301` | **AGREE** | Remove unsupported attributions. The review does not provide primary evidence for them; its own round rule remains a proposal. |
| 7 greedy-repeat claim replaced / `R:302` | **AGREE** | `P4:21` supports the narrower one-unique-seed statement, not the three-of-three genealogy. |
| 8 meter status / `R:303` | **AGREE** | An ALIGN kit lacking a logger call is not evidence its diagnostics contain a synchronized KM stream; `KM:1-4`; F4. |
| 9 PIPELINE path / `R:304` | **AGREE** | The cited lane blob has the sentence at `PIPE:11-12`; no current-main implementation should be inferred. |
| 10 not-reopened citations / `R:305` | **AGREE** | Transparent epistemic downgrade is appropriate; primary claims remain UNVERIFIABLE here too. |
| 11 rough prefill estimate / `R:306` | **AGREE** | Keep explicitly rough; `MV:30`. |
| 12 sizing / `R:307` | **DISAGREE** | The printed arithmetic is correct for a zero-difference null, not the proposed ≥.05 gain. N≈300–400 at 10% success has no stated alternative, dependence or selection calculation. F2. |

## Appendix coverage: all actions and additional seat claims

The verbatim appendices are evidence of what the committed product says, not
additional independent experiments. Every action below inherits the indicated
substantive check, including its conditions; overridden recommendations remain
explicitly rejected rather than silently disappearing.

| Appendix action | Status | Coverage / deviation from the reconciled action |
|---|---|---|
| A1 (`R:337`) | **AGREE** | Action 2's DC direction; its implementation conditions and unverified budget remain F4. |
| A2 (`R:338`) | **AGREE** | Action 1; F4/F7/F8. |
| A3 (`R:339`) | **AGREE** | Monitor-arm direction; action 3's FPR/view qualifications apply. |
| A4 (`R:340`) | **AGREE** | Actions 6/12, bounded search and paired physical testing; F2/F8. |
| A5 (`R:341`) | **AGREE** | Action 11 with shams, execution truth and uncertain cost. |
| A6 (`R:342`) | **DISAGREE** | A pooled, counts-logged energy-only primary conflicts with pair separation and does not establish the squeeze; `V4:491,505`; F2. |
| A7 (`R:343`) | **DISAGREE** | 21 calibration observations/pair do not deliver m≥39 or a finite .025 energy threshold; F1. |
| A8 (`R:344`) | **AGREE** | Action 9, publication only under lead/Ed authority. |
| A9 (`R:345`) | **AGREE** | Action 14, trusted fixed timing estimator and fair budgets. |
| A10 (`R:346`) | **AGREE** | Action 19; per-device fit and native qualification. |
| A11 (`R:347`) | **DISAGREE** | Outcome/utility reporting and retitling are useful; a scripted compute injector cannot by itself carry a successful-saboteur adaptive claim. `SQ:79-85,305-311`; F6. |
| A12 (`R:348`) | **AGREE** | Action 16, historical exploratory comparator only. |
| A13 (`R:349`) | **AGREE** | Action 14; register scan window/horizon and false-alarm budget. |
| A14 (`R:350`) | **AGREE** | Action 17, exploratory transfer only. |
| A15 (`R:351`) | **DISAGREE** | An exploratory third channel may test catchability, not “show” it in advance; F8. |
| A16 (`R:352`) | **AGREE** | Action 18, fixed prospective remedial rule. |
| A17 (`R:353`) | **AGREE** | Exclusion/ITT reporting is necessary; action 7/F3 adds missingness bounds. |
| A18 (`R:354`) | **AGREE** | Action 20 optional transfer; unverified time estimate. |
| A19 (`R:355`) | **AGREE** | Action 10 for repo text; Token Inflation wording remains source-unverified. |
| A20 (`R:356`) | **UNVERIFIABLE** | Venue dates and categorical future feasibility; planning preference acceptable. |
| B1 (`R:516`) | **AGREE** | Action 1/10 directions, F4/F7/F8. |
| B2 (`R:517`) | **DISAGREE** | F4: qualify DC/gross-baseline contract and clocks; do not alter R1 or treat arm/end battery checks as continuous validity. |
| B3 (`R:518`) | **DISAGREE** | F1/F7: freeze primary monitor/view/composite and genuine crossed count/view arms before an FPR guarantee. |
| B4 (`R:519`) | **AGREE** | Action 4, F6 design/sample conditions. |
| B5 (`R:520`) | **AGREE** | Action 6; frozen final blue team, mixed families, fresh test/selection inference. |
| B6 (`R:521`) | **DISAGREE** | Action 7/F3: unavailability versus detection and benign operational cost. |
| B7 (`R:522`) | **DISAGREE** | Action 5/F1/F2/F5: specify null, interval, H and paired best-response target. |
| B8 (`R:523`) | **AGREE** | Action 11, preserve physical versus modelled token-equivalent distinction. |
| B9 (`R:524`) | **AGREE** | Action 12, direct joint measurement primary. |
| B10 (`R:525`) | **AGREE** | Ungated D arm can estimate the deployment gap with its own calibration; cost unverified. `CH:316`. |
| B11 (`R:526`) | **AGREE** | Action 14, prospectively separate negative/sequential tests and define β units. |
| B12 (`R:527`) | **DISAGREE** | Action 13/F2: proxy development useful, inadequate confirmatory sizing/composition claim. |
| B13 (`R:528`) | **AGREE** | Action 20, fixed additional task/judge configurations. |
| B14 (`R:529`) | **AGREE** | Action 20, separate 30B calibration and no transfer of D's claim. |
| B15 (`R:530`) | **AGREE** | Batching scope/simulation useful; Wu figures primary-unverified, cloud hardware not authorized here. |
| B16 (`R:531`) | **AGREE** | Related-work coverage useful; source-statistic correction requires primary recheck. |
| B17 (`R:532`) | **DISAGREE** | Action 23: resource prioritization cannot remove W1/registered calibration obligations. |
| B18 (`R:533`) | **UNVERIFIABLE** | Venue feasibility is a schedule estimate; do not split the owner's squeeze goal merely on an unverified forecast. |

Additional claims in seat prose, beyond the action mappings and external-source
register:

| Claim / product lines | Status | Reason |
|---|---|---|
| Future complete squeeze / empty feasible region (`R:370,382,440`) | **DISAGREE** | Finite tests do not prove every strategy excluded; H90 is 90% detection, not an absolute bound. No law implies monitor catch of all logged malicious work. F2/F8. |
| Prospective v4 cell, sampler/caps and seed independence (`R:373-375,613,862-864`) | **AGREE** | `V4:58-91,148-191`; Q6 supersession `MAIN:1124-1129`. Dev seeds are valid design data but capability results remain outcomes to record, not permission to inspect final test scores. |
| 19–58 J residuals, ≈2 J replay, two held-out trajectories, 2/26 alarms (`R:376`) | **AGREE** | Repository narrative matches `RP:104-119`, `P9:17-25`, `P10:21-24`. The 2/26 numerator is **bank**; spam is 0/26. Pooling would be 2/52, not a single generic sabotage rate. Raw captures not read. |
| D 300–500 and 30B 80–370 MDE (`R:377,589,923`); “will be caught” | **DISAGREE** | Planning estimates rest on the mismatched scale in CHAIR; no prospective DC detection guarantee. `CH:272-295`; F5. |
| Metadata/count baseline is PALACE (`R:396`) | **DISAGREE** | `PIPE:26` asks whether observed metadata separates conditions; PALACE predicts hidden counts from prompt/answer (`LIT:725-727`). They are related software baselines, not the same target. |
| Power metering costs nothing per episode (`R:632`) | **DISAGREE** | Capture, battery journal, alignment, fit and monitoring have overhead; logger self-load is explicitly nonzero (`MV:67`). It may be cheap/passive, not free. |
| Trusted counts always eliminate the need for a meter (`R:626`) | **DISAGREE** | They expose inconsistent token stripping for a covered inference path, but not necessarily separate calls, tool work, off-path compute or a compromised reporting component. Define coverage of the trusted counter. `ER:388-400`; `SQ:59-67`. |
| No visible reasoning = latent-only; forced end-of-think measures H (`R:668,851-853,933`) | **DISAGREE** | Visible actions can still carry computation; define hidden versus total/per-turn work and verify enforced cap semantics. F6. |
| Four forms off-GPU rail miss and DC catch (`R:703-706,908`) | **UNVERIFIABLE** | Appropriate hypothesis, not observed outcome; rail coupling and full-host noise can change. `ER:393-394`; `RP:135-138`. |
| Benign-carrier edit “exact for in-process decode” (`R:763,850`) | **DISAGREE** | It is an exact specified *log transform*, not guaranteed physical response or an exact fitted energy law. `CH:312`; `SQ:118,139-147,317-320`. |
| Clock correlation +.79 fifth session; hybrid misspecification (`R:767-772`) | **AGREE** | `P10:24`; `LIT:71`; as diagnostics, not a causal explanation or license to change the primary on test results. |
| Power-mode effect or U4/U5 acceptance generalized to all devices/production (`R:270,398,789`) | **DISAGREE** | The valid restricted reference-state limitation is in `CH:313-322`. Historical 30B versus gated D is not a randomized gating effect; n=1 A-B-A does not establish a general effect. |
| Cross-session frozen-fit sensitivity and second-size S(H) (`R:671,682`) | **AGREE** | Useful additional secondary proposals omitted from the final list; admit their fits/cohorts prospectively. `V4:488-505`; `CH:315`. |
| A single-trajectory maximum can be fixed by rank m−1 or pooling (`R:426`) | **DISAGREE** | Both change the inferential target/false-alarm rule; do not use an observed outlier to select a favorable threshold. F1; `V4:505`; `CH:164-165`. |
| Meter fit is gain certification, no gain validation anywhere, or .955 implies unexplained 4.5% fault (`R:410,428,794-800`) | **DISAGREE** | Repo reports a PDTR comparison and a diagnostic band, not traceable calibration of either sensor or proof of a fault. Claim-grade accuracy/uncertainty remains open. `KM:78-94`; `MV:102,266`. |
| 10–11 nominal / 15–17 refusal-adjusted nights; 1.5× refusal factor (`R:469,593-595`) | **UNVERIFIABLE** | Forecasts with inconsistent “night”/16.5-hour window units and unresolved cohort allocation. `RP:76` explicitly treats refusal factors as judgment. |

## Venues and publication actions

| Product venue claim | Status | Review |
|---|---|---|
| NeurIPS 2027 unannounced, 2026 May 4/6, projected May; April completion sufficient (`R:315`) | **UNVERIFIABLE** | Offline record only. [Official dates pointer](https://neurips.cc/Conferences/2026/Dates); future fit/feasibility is judgment, not evidence. |
| CCS 2026 Jan 7/14 and Apr 22/29; projected late-April 2027 (`R:316`) | **UNVERIFIABLE** | Primary CFP not archived in read set; product itself relies partly on aggregators. |
| S&P 2027 June 4/11 and Nov 10/17; projected 2028 early June (`R:317-318`) | **UNVERIFIABLE** | [CFP pointer](https://sp2027.ieee-security.org/cfpapers.html); projections are not scheduled deadlines. |
| USENIX '27 Jan 19/26, 13 pages, Open Science, ML caution; '28 August fallback (`R:319,490,948`) | **UNVERIFIABLE** | [CFP pointer](https://www.usenix.org/conference/usenixsecurity27/call-for-papers); Denver/August conference dates and future impossibility likewise not checked. |
| SaTML '27 passed Sept 29/30; '28 late September (`R:320,491,952`) | **UNVERIFIABLE** | No primary archived CFP; future estimate. |
| ICML '27 projected January, conference July 31–Aug 6 (`R:321,492,949`) | **UNVERIFIABLE** | [Dates pointer](https://icml.cc/Conferences/2027/Dates); no proof of future data-readiness impossibility. |
| ICLR '27 Sept 18/25 and '28 Sept/Oct (`R:493,953`) | **UNVERIFIABLE** | No primary archived deadline page in this read set. |
| Write toward main-track squeeze, choose one venue, recheck CFPs (`R:323-326,955-958`) | **AGREE** | Fits `AGENDA:5-20`. Preprint, public registration and forum posting are later owner-controlled publication actions, not performed/authorized by this review. No promise that either outcome is publishable. |

## What the lead should retain and change next

Retain the review's central critique and its attention to capability, the actual
physical boundary, paired monitors, adaptive attacks and independent test data.
Carry corrections F1–F8 into the existing addendum rather than spawning another
protocol. The exact next desk step is a **lead disposition of actions 2, 3, 5,
7, 8, 13 and 23**, with a cohort/fit/calibration/test table and a definition of
the primary operational escape event and benign cost. Reconcile gross versus
baseline-subtracted DC energy, paired direct versus proxy P2, and the two-solo
versus monitor-only gain criterion before any relevant cohort is collected.

Keep the pre-W1 blockers as a separate explicit checklist: missing protocol
rulings, WP19, battery admission, contrast fit, fallback expressibility,
registration/cold-gate receipt and post-R1 delta review (`W1:34-71,77-105`;
`MAIN:1143`). This reviewer2 document did not close them. R1 remains on its
existing authorized path. Prospective DC qualification, battery/clock checks,
forced-budget behavior and synchronized native compute-injection tests must be
run later by the lead outside this sandbox, in a clean authorized measurement
session. This review contains no code change requiring a new native test now.

## Verification and remaining uncertainty

- Resolved all source pins locally and checked cited code/doc passages. No fetch,
  external primary-source retrieval, outcome analysis, model execution or weights.
- `TMPDIR=/private/tmp python3.13 -B -m unittest tests.external.test_km003c_parse.EnergyTests`:
  **6 tests passed**, 0.024 s. Inspected the class first: only synthetic streams,
  battery signs, missing-SMC handling, integration and ratios (`KMT:247-310`).
  Recorded-fixture classes were deliberately not run. This is parser arithmetic
  evidence, not native meter validation or claim-grade uncertainty calibration.
- Standard-library arithmetic independently checked the ranks, stated confidence
  limits, binomial yield, cohort counts, .05-margin sizing correction and the
  analytic dependence/composition counterexamples in F1/F2/F6. No simulation was
  substituted for a live result.
- Documentation-only diff; no full suite, sharded suite, pipeline, compileall,
  hardware collection or Metal execution. Citation/diff checks and commit
  details are in the accompanying run report.

Unresolved decisions belong to the lead: threat authority and D-139 scope;
measurement/baseline contract; unit of exchangeability; extra windows and fit
cohort; primary monitor/view; precise P1/P2 hypotheses; unknown-outcome policy;
capability cutoff/sample size and configuration fallback. Primary literature,
CFP accuracy and prior-seat journal provenance remain unverified under the
no-network/path constraints. These are explicit limits of this review, not
claims that the underlying sources or proposed experiments are wrong.
