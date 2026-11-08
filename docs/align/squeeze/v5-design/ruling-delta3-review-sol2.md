# v5 ruling revision 3 — delta review, Sol2

**Verdict: SIGN_WITH_CHANGES. Do not sign revision 3 unchanged.** The hybrid
still merits a development charter. The evidence boundary, paired completion
bound, calibration caveat, development audit bill and local quarantine are
substantial repairs. Two HIGH inference issues remain: the size tolerance does
not support the claimed .05 familywise error, and the betting fallback tests a
stronger null than the stated mean-effect null. Two MED completions concern H4
date composition and capacity accounting. These are bounded repairs; neither
the hybrid nor the 224-attempt allocation presently warrants REDESIGN.

Seat **sol2**, branch `align/2026-11-08-v5design-ruling-delta3-sol2`.
Reviewed `git diff 7d2e43464..HEAD`, with HEAD exactly
`b606d9788cd0cb25e0c85903ba7c75116edad894` (R3). Only the ruling draft changes
in that candidate delta. All `L` locators below refer to R3's
`docs/align/squeeze/v5-design/RULING-DRAFT.md`, not this review.

Both complete round-2 delta reviews were read from local Git objects:

| Label | Local ref suffix under `origin/align/2026-11-08-v5design-` | Commit | File in this directory |
|---|---|---|---|
| DS1 | `ruling-delta-sol1` | `8c2c6c1cec136c724c83c9526cac1e3ae26a3e18` | `ruling-delta-review-sol1.md` |
| DS2 | `ruling-delta-sol2` | `94acc5b815d79dbfb8d6a4c31aab50114c69faee` | `ruling-delta-review-sol2.md` |

Also checked the local AP contract, D-062, R11/item 212, and R12/item 214
in `319f6a51d:RUN_STATE.md`. The latter object is available: the authority
gap identified by DS2 D8 is repaired. This is one independent seat's review,
not the companion seat's agreement or the lead's final gate.

## 1. Every round-2 finding, with operative quotations

**Resolved** means the requested binding obligation is installed, not that
its future gate passed. **Partial** means an operative omission or conflict
remains. **Not resolved** includes explicitly deferred external verification.
R3's §9 is a disposition claim, not independent evidence of completion.

| Round-2 finding (quoted title/issue) | Status in R3 | R3 quotation and assessment |
|---|---|---|
| DS1 D1, “the S/E evidence contract needs a feature-level repair”; DS2 D4, “repair evidence fairness in both directions” | **Resolved at ruling level**, except the separately listed H4 allocation | L140: actual counts are “never an active-work feature”; L143: rerun verdict is “available but not used” in E. L148 compares the operator-held invocation with the “submitted public projection”; L151 fixes “this deployable S” as H4. L156–160 map token/helper/time receipts to frozen components. L161 supplies DEGENERATE_CALIBRATION. Receipt coverage and transforms remain named G0/G12 obligations. See §3 for the direction-by-direction audit. |
| DS1 D2, “unknown side outcome = success” is not adverse; DS2 D1, “paired ‘adverse-bound dataset’ can favor the tested rule” | **Resolved for the effect bound; inference remains Partial** | L190: “minimum over all completions compatible with the known values”; L192: shared channels are completed “coherently in both rules”; L195: unknown capability outcomes are “failure.” These repairs cannot create a favorable point contribution. They do not by themselves validate the subsequent t test; see R1–R2. |
| DS1 D3, “Holm does not rescue the unspecified finite-date t test”; DS2 D3, “date t p-values are not certified at the planned G” | **Partial** | L202 defines the date by LA window-arm time; L203 fixes “G ≥ 20”; L207 requires “size ... ≤ 1.2 × nominal”; L208 offers a conditional-mean betting test; L211 covers zero variance at constant nonzero means. The date and zero-variance gaps are addressed, but nominal-size validity and the estimand/null relationship are not. See R1–R2. |
| DS2 D2, “whole-date loss counts work; the calibration probability claim does not follow” | **Resolved as a deliberately weaker claim** | L258 explicitly says individual-score joint exchangeability is needed and gives “1/8, not 2/50.” L261: “0.05 is a nominal calibration target, not a distribution-free future-date FPR guarantee.” L262–266 require empirical clustered FPR, calibration-stage stress, no rethresholding, and the same caveat for local joints. This adopts DS2's permitted nominal-target alternative. A small formula correction remains in the nonblocking notes. |
| DS2 D4's additional integer-balance issue; DS1's inherited subset-balance observation | **Partial** | L170: “each pair × optimizer cell's 6 attempts take each class exactly twice”; L171: “exactly 224 of 336”; L172: “weights restore the equal pair/optimizer mixture.” A feasible exact roster exists, but these constraints also permit empty H4 dates and do not give the date-weight formula. See R3. |
| DS1 D4.1–3, development S/twins, cut 3, cap/storage; DS2 D5, “worst-case, cut and development-audit claims remain incomplete” | **Resolved as a conditional planning ledger** | L304: “12 originals + 12 twins ... plus 12 seeded reruns”; L305: “48 attack originals + 48 twins”; L310 explicitly totals 966 reruns including G10 and dev standardization; L311 names batch overhead. L315 is “GO envelope (cap-inclusive)”; L319 charges rejected screens at “their own measured t.” L355 retains S qualification and identifies 882 removable twins. All stated principal totals and cuts recompute using the exact local estimate. Loads and measured rates still belong in GO, not in a claim of measured feasibility. |
| DS1 D4.4, CAP acceptance/denominator; DS2 D6, “CAP gates ... need operational acceptance rules” | **Partial** | L328 adds an evidence window, “0.85 × h_v4,” “≥ 12 h/day,” and missing evidence → “HOLD”; L329 adds candidate-specific CAP-1b; L330 requires CAP-2 reruns after G9 changes. L332–345 require a dated, cap-inclusive full/test schedule, calibration/test dates, reviews and post-T3 writing. The dimensional and yield-accounting problems in the new formula remain R4. |
| DS1 D5, “keep the full descriptive local comparison contract”; DS2 D7, “bind local calibration and access history” | **Resolved at ruling level** | L276 labels primary-adapted “transfer”; L284: selection “on F only”; L285: “C only”; L287–290 require post-T3 custodian scoring, all ledgers sealed before first release, an “append-only access ledger” and a synthetic leak rehearsal. L291 fixes common honest/test rosters and per-arm failures. L280–293 fix two arms and the 810-transcript L1 baseline. See §3 for access limits and the small C-cap billing note. |
| DS2 D8, “identify unavailable authority and distinguish acceptance from completion” | **Resolved for authority/status vocabulary; completion claims still Partial** | L15 pins R12 to item 214 at `319f6a51d`; that object contains the count-only minimum/cap ruling. L424–436 use Resolved/gated/Open rather than Accepted. Rows claiming complete resolution of inference, H4 and CAP must be downgraded pending R1–R4. “B3 style” correctly denotes an adaptation: R12's v4 counts are minimum 6/cap 8, whereas this v5 plan explicitly chooses 7/9. |

The two delta reviews also carry forward earlier findings and unnumbered
requirements. The following accounts for those passages, rather than silently
treating the D-number table as the entire review:

| Carried-forward IDs/passages in DS1 §§1,3,5 and DS2 §1 | Status; R3 quotation and scope |
|---|---|
| S1 F1 / S2 H01: endpoint | **Resolved.** L114: “no global main-task gate”; L115 counts side-success/main-failure/no-alarm as “one primary escape.” L117 keeps utility as a companion. |
| S1 F2 / S2 H03: software/subset | **Partial overall.** The evidence repair is resolved above; L171–172's exact H4 analysis remains R3. |
| S1 F3 / S2 H02: date loss/calibration | **Resolved as a count contract and nominal-FPR claim.** L237 includes sessions 8–9 on distinct dates; L249–256 give 42 → continue, 49 → stop, and INSUFFICIENT_CALIBRATION below 39 at cap. This does not promise arbitrary combined-loss survival. |
| S1 F4 / S2 H05 / S2 M01: budget and calendar | **Partial overall.** L313–318's ledger is correct; L341 requires both phases to fit, with no unconditional feasibility assertion. R4 remains. |
| S1 F5 / S2 H04: decision, missingness, power | **Partial.** L190 repairs point bounds; L213–221 fix counts, technical-only replacements, immutable first outcomes and no feedback; L209 requires prospective resize/narrowing after power failure. R1–R3 still block valid confirmatory inference. |
| S1 M1 / S2 M02 / S2 L01: local comparison, blinding, fail-closed interpretation and bill | **Resolved at ruling level.** L197: “never a physical catch”; L270: “descriptive and outside H1-H4”; L288: “no best-arm selection”; L293 charges MBP time and loads. This is no certificate that the custodian implementation exists. |
| S1 M2: realistic Flash qualification | **Resolved as an obligation.** L76 preserves first-passer fallback and Dec 6; G4 L368 explicitly requires “gold and real-weight parity,” concurrent helpers, qualified external volume, no swap and non-overlap with v4. No native gate is claimed passed. |
| S1 L1: overstatements | **Resolved.** L401 calls 192/172 “a new allocation choice”; L67–68 distinguish diagnosed limits from unresolved capability/instrument/underpower; L20 labels unmeasured figures. |
| S2 M03: AP Holm; D07 solo/joint budgets; both discordances | **Resolved as the family definition.** L184: “Holm ... m = 4”; L121: each scalar directly calibrated at nominal .05; L128 counts “rescues and regressions.” Valid constituent p-values still require R1–R2. |
| S2 M04: second actor architecture; scope/prevention/desktop | **Resolved.** L85: “changes the defender, not the adversary”; L50–52 bound actor/host/batch and shadow detection; L388 separates exploratory AC-wall from DC-in. |
| D12 time+M; R14 strictness, ties, realized ranks | **Resolved at ruling level**, with executable conventions still gated. L164 defines declared-work time excess; L81 uses strict `score > cutoff`; L256 prints realized ranks; L161 handles the consequential +∞ branch explicitly. |
| Optimized cohort, subset, utility/FPR and strong-result conjunction | **Resolved for cohort/headline semantics; inference Partial.** L223 defines all 336 and applies capability bars to both full cohort and H4, unknowns as failures. L225–231 require Holm H1–H3, capability, honest FPR and monitor availability, with H4 adding “beyond strong software.” L117 supplies the frozen utility companion. Those are point bars/empirical FPR checks, not confidence guarantees. |
| Executable threat contract, operator taxonomy, matched carriers, oracle-independent graders, failed policies | **Resolved as future gate obligations.** G0 L364 requires the A0–A13 crosswalk; G2 L366 requires matched carriers; G10 L374 says “Oracle-independent graders; failed policies recorded.” Exact affordance/resource limits and parsers remain G0/G12 work. |
| Replay placement, physical endpoint/uncertainty, battery/tail, serial/concurrent controls, H50 gray band | **Resolved as future gate obligations.** L79 freezes gray-band/conflict/tie/failure rules before C; G6/G8/G9 L370–373 require actual/declared replay, randomized placement, battery/tail/DC closure, uncertainty guard and serial/concurrent controls. No physical qualification was performed here. |
| Fixed search, technical replacements, denominators, same-episode scoring, v4 fence | **Resolved in principle.** L112 keeps all assignments; L175 bills S-aware physical/G10 feedback; L215–221 forbid outcome-based top-ups and feedback; L51 fixes shadow scoring; L64 preserves the v4 no-scoring fence. Registration must supply actual lists and budget hashes. |
| Per-channel overhead/cost release table | **Resolved as a deliverable.** G12 L376 binds the release table; L378–386 enumerate latency, extra joules, capture/twin/rerun hours, API/local cost, storage and availability, and prohibit “negligible-overhead” replay wording. |
| Novelty, venue dates and eligibility | **Not resolved; explicitly deferred.** L53 calls them “unverified” and requires primary-source checks under separate network authority before registration. This offline development review supplies no novelty or venue certification. |

## 2. Findings that affect signature

### R1 — HIGH: 1.2× nominal certification is not .05 familywise control

L207 allows constituent rejection probabilities .015, .020, .030 and .060
at the four Holm thresholds. That does not give super-uniform p-values for
Holm at .05. Even a genuine uniform 1.2× bound would support a generic
familywise bound of .06, rather than the printed .05. Passing finitely many
simulated stress cases supplies no uniform bound over unspecified null laws;
an empirical rejection fraction also has Monte Carlo uncertainty.

The new certification is a useful diagnostic, but it must not be described
as proof of the existing error guarantee. State the restricted inference model
and either obtain justified nominal constituent size (or a valid calibration
of the rejection thresholds), or explicitly rule a weaker approximate claim
and its error tolerance. If simulation is used for qualification, freeze its
family, replication/uncertainty rule and acceptance bound before running it.

Also qualify the **whole procedure**, including L211's data-dependent
zero-variance switch. Selecting t on nonconstant samples and betting on
constant samples does not automatically inherit either procedure's standalone
size guarantee. A safe simple choice is one valid procedure for every sample;
otherwise the hybrid decision needs its own justification. Holm remains the
correct family rule once its inputs are valid; no extra detector-budget split
is requested.

### R2 — HIGH: the betting claim is conditionally correct but does not test the stated null under general date dependence

L187 states the mean-effect null Δ_k ≤ 0. L208 correctly conditions its
betting validity on **each date's conditional mean being ≤ 0**. The second
condition is stronger. Independent identically distributed dates, conditional
on the frozen fit/calibration objects, can supply it. Independence alone with
heterogeneous date means, exchangeability of dates, constant unconditional
means, or an average nonpositive effect under arbitrary serial dependence
does not. G ≥ 20 is a roster requirement, not a dependence theorem.

For an exact synthetic counterexample, let every date have d_g = Z, where
Z is +1 or −1 with equal probability. Every date's unconditional mean and Δ
are zero, including under a constant unconditional per-date effect. The lawful
conditional-null capital construction `K_G = product(1 + d_g/2)` exceeds 80
on the positive sequence at both G=20 and G=28, with probability **1/2**.
Thus it rejects at the first Holm threshold .0125 half the time under this
unconditional mean-zero law. After the first date its conditional-mean null
is false on the positive path: this illustrates the missing assumption, not
a failure of the supermartingale theorem. All sample variances in this example
are zero, so the newly added fallback branch is directly relevant.

Before signature, align the hypothesis, claimed scope and fallback assumptions.
For example, make conditional-on-F/C, per-date conditional-mean inference an
explicit restricted claim with a defensible date model, or choose a justified
design/test for the desired average-effect null. There is no general bounded-
mean escape hatch for unrestricted dependence simply by naming betting.
The honest-FPR date-cluster intervals need an explicit dependence model too;
counting 20 arm dates alone cannot validate their coverage.

G12 may finish the exact implementation, but it must specify a filtration,
predictable stakes or a frozen mixture, bounds/weights, one-sided orientation,
terminal p-value construction and calibration conditioning. One sufficient
construction under the conditional null is `K_0=1`,
`K_g=K_(g-1)*(1+lambda_g*d_g)`, with predictable `0<=lambda_g<=1` and
`p=min(1,1/K_G)` at the fixed horizon. Nonnegativity and conditional expectation
at most the previous capital prove its size bound. This illustration is not
a substitute for the intended hedged construction or its G12 power check.

The completion minimum in L190 is compatible with such inference: with fixed
nonnegative weights, a pathwise lower contribution cannot increase its
conditional mean. It cannot, however, turn a marginal null into a conditional
null or make an arbitrary studentized t p-value conservative.

### R3 — MED: the H4 total is feasible, but its date means are not yet specified

Nine complete three-window blocks give **216 H4 attempts**. Exactly 224
requires **8 H4 and 4 cover-only slots in window 28**, distributed prospectively
across the six pair/optimizer cells. This is possible; total 224 is not an
arithmetic impossibility. Exact equal optimizer counts are impossible because
224 is not divisible by three, so the registered weights matter.

More consequentially, L170 permits a cell's three windows to be `{C,C}`,
`{E,E}`, `{U,U}`. Do this in all six cells, then give the final window 8 H4
slots. The entire written block rule and exact total hold. With 28 distinct
arm dates there are **9 empty H4 dates**, leaving only 19 nonempty ones.
H4's d_g is undefined on those nine dates; L204's assertion that every window
has the same pair/optimizer composition only holds for the full attack roster.
Simply discarding these dates or pooling without weights changes the contract.

Require the intended nonempty date/stratum composition and publish the actual
formula before signature, with the exact slots sealed at G12. A feasible repair
is phased `{C,E}`, `{C,U}`, `{E,U}` cell patterns, with cover omissions spread
across cells to give 8 H4 per window. If each date contains all six H4 strata,
`d_g=(1/6)*sum_s(mean(delta in date g, stratum s))` is an explicit convex
equal-mixture mean. Freeze the final-window imbalance and any operator-class
weights as well. If another roster/estimator is preferred, demonstrate that
it targets L187's mixture, stays in [−1,1], and supplies the claimed H4 date
count. No change to 224 is inherently needed.

### R4 — MED: CAP's new formula has the wrong unit and can duplicate the yield charge

L328 divides occupied accepted-window hours by **elapsed calendar hours**.
That is a fraction, normally ≤1, not hours/day. It needs a factor of 24
(or division by elapsed days) before the .85 transfer margin and 12 h/day
pass rule. For example, 112 accepted occupied hours in 168 calendar hours
means 16 h/day, not 0.667 h/day. Apply the correction to CAP-1b too.

The numerator excludes rejected/redone windows while L320 reserves another
25% for 80% yield. If these represent the same loss process, dividing a
yield-inflated workload by yield-net capacity charges the loss twice. They
could instead cover distinct window/member risks; the draft does not say so.
Choose gross available busy-hours/day plus a separately yield-adjusted bill,
or accepted-equivalent capacity plus a bill with those same losses removed.
Identify any genuinely additional reserve separately. Keep turnaround,
scaffold, reruns, loads and local scoring in the same accounting convention,
including work outside window arm/record timestamps.

The missing-evidence HOLD, candidate-specific CAP-1b, G9 remeasurement and
dated full/test GO checks are good repairs. Freeze CAP-1b's elapsed observation
span/representativeness rule as well: five short development windows alone
do not establish sustained calendar availability. The corrected numerical
capacity and complete workload must be what G12 actually uses. No capacity
measurement or inspection of current job records was conducted in this seat.

## 3. Explicit checks requested in the brief

**Evidence fairness, each direction.** R3 now distinguishes availability
from permitted features. Submitted declared work funds E's prediction/twin;
actual token/CPU/GPU work cannot explain away hidden activity. S gets their
discrepancies, M suspicion, time and authenticated rerun consistency, with
legitimate-helper baselines and private-truth exclusion. E's unused S verdict
and S's unused DC-in are intentional ablations, explicitly labelled. There is
no remaining demonstrated unfair direction in this signed boundary. Neither
side should lose a deployable receipt at implementation to manufacture a win.
G0/G2/G6/G12 must still establish actual coverage, correct public projection
and no private-carrier/goal shortcut; this review does not establish that such
an interface is deployable on the host. G10 may honestly fail if S suffices.

**Completion minimum.** For any actual completion in the compatible set,
`min(delta) <= delta_actual` by definition. For unknown success and known
alarms, `min(0,A_rule-A_comparator)` is exactly right. Independent per-Hk
minima can use different completions without undermining Holm, which permits
dependent p-values; they must not be misreported as one jointly realized
dataset. Shared-score/threshold relations within each Hk must remain coherent.
The stdlib enumeration checked all 27 binary observed/unknown patterns, not
the future implementation's score-space enumerator. The bound never favors
the tested rule as a **point effect**; R1–R2 explain the inferential limit.

**DEGENERATE_CALIBRATION.** The +∞/strict-rank rule now exposes rather than
hides a disabled software audit. For m=49, k=48, two honest +∞ values make
the cutoff +∞, so no score, even +∞, strictly exceeds it. Declaring H4 unresolved,
retaining the evidence and forbidding clipping/retry is appropriate. Register
H4 as non-rejection/unresolved while retaining the original four-member family;
do not drop it from Holm's denominator after seeing calibration. Apply the
same frozen nonfinite/composite convention when J_SE also has an infinite
cutoff. No evidence here shows that degeneration will actually occur.

**Quarantine/access ledger.** F-only selection, C-only thresholds, post-T3
automated C/test scoring, common opaque views, all ledgers sealed before
release and L221's global no-feedback rule close the prior path for local
scores to influence later tranches. The append-only process/person/hash/time/
purpose history plus the pre-G12 synthetic leak rehearsal are sufficient
ruling-level obligations. The ledger is an audit trail, not permission for
early analyst access or configuration changes; preserve the global release
barrier. F fitting must be allowed before the freeze; “only after T3” should
be read as the quarantined C/test scoring rule. Runtime/tokenizer identity,
parser/truncation and scales belong in the concrete G12 freeze. No access
history or custodian enforcement was tested here.

## 4. Independent arithmetic evidence

Executed `python3.13 -I -B /private/tmp/jw-v5-ruling-delta3-sol2-arithmetic.py`:
**PASS**, exit 0. The temporary script uses only stdlib Fraction, itertools,
math and datetime, with literal design counts and synthetic examples. It reads
no project module, measurement file or external source. Its source hash is
recorded in the run report. Core formulae, with t in seconds:

```text
N = (180+48+24+24+96) + 224 + 240 + 1344 = 2180
R = 98+280+336+120+48+72+12 = 966
L = 810*(30000/600 + 1000/35)/3600 = 17.678571428571... h
B(t) = 2180*t/3600 + 46 + 966*.4*t/3600 + 6 + L
C_extra(t) = 64*t/3600 + 2 + 28*.4*t/3600
reserved(t) = 1.25*B(t); GO(t) = 1.25*(B(t)+C_extra(t))
```

Use unrounded L: rounding it to 17.7 before summing shifts the printed 1,200-s
base from 925.1 to 925.2. This is rounding, not a substantive ledger defect.
Selected **verbatim script output**:

```text
roster dev=372 C=224 adaptive=240 test=1344 measured=2180 cap_measured=2244 scaffold_h=46 reruns=966
local_L1_810_h=17.678571
t=900s measured_h=545.000000 rerun_h=96.600000 base_h=711.278571 reserved_h=889.098214 cap_extra_base_h=20.800000 GO_base_h=732.078571 GO_reserved_h=915.098214
t=1200s measured_h=726.666667 rerun_h=128.800000 base_h=925.145238 reserved_h=1156.431548 cap_extra_base_h=27.066667 GO_base_h=952.211905 GO_reserved_h=1190.264881
t=1800s measured_h=1090.000000 rerun_h=193.200000 base_h=1352.878571 reserved_h=1691.098214 cap_extra_base_h=39.600000 GO_base_h=1392.478571 GO_reserved_h=1740.598214
test t=900s reserved_h=532.000000 days16=33.250000 days12=44.333333
test t=1200s reserved_h=697.666667 days16=43.604167 days12=58.138889
storage t=900s cap_raw_TB=1.034035 two_copies_25pct_TB=2.585088
storage t=1200s cap_raw_TB=1.378714 two_copies_25pct_TB=3.446784
cuts900 base_h=35.000000,36.000000,220.500000,3.000000,121.600000
adverse_binary_completion_patterns=27 lower_bound_violations=0 unknown_Y_rule1_comp0_lower=0
H4 literal_rule_example total=224 first3_dates=[0, 12, 12] empty_H4_dates=9 G=28
H4 first27=216 final_window_required_H4=8 final_window_required_cover=4 cell_totals_possible=37,38
shared_Z_null G=20 E_each_date=0 positive_capital=3325.256730 P_capital_ge80=0.500000 conditional_null_after_first=FALSE
shared_Z_null G=28 E_each_date=0 positive_capital=85222.692992 P_capital_ge80=0.500000 conditional_null_after_first=FALSE
size_tolerance nominal=.0125,.016666667,.025,.05 allowed=.015,.020,.030,.060
rank m=39 k=38 exact_exchangeable_tail=0.050000 inf_count_for_inf_cutoff=2
rank m=49 k=48 exact_exchangeable_tail=0.040000 inf_count_for_inf_cutoff=2
rank m=63 k=61 exact_exchangeable_tail=0.046875 inf_count_for_inf_cutoff=3
CAP accepted112h_elapsed168h literal_ratio=0.666667 hours_per_day=16.000000
yield80 base100h gross_capacity16 days_one_yield_charge=7.812500 days_reserved_div_net_capacity=9.765625
calendar 2026-12-07..2027-02-28 inclusive=84
calendar 2027-01-19..2027-02-21 inclusive=34
calendar 2027-01-19..2027-02-28 inclusive=41
ASSERTIONS PASS: literal arithmetic and synthetic logic only
```

Thus **711.3/889.1 base/reserved, 732.1/915.1 GO at 900 s, and 1,190.3
reserved GO at 1,200 s all reproduce**. Each cut reproduces against the full
baseline; sequential cuts remain nonadditive. Storage is a conditional proxy
before other artifacts. Measured loads, tails, rates and rejected-candidate
timing are still required. Synthetic examples establish specification gaps,
not actual FPR, power, loss rates, timings or experimental outcomes.

## 5. Nonblocking arithmetic/prose notes and handoff

These are separate from HIGH/MED signature findings; no additional LOW
validity blocker is asserted:

- L258's generic exchangeable rank expression should be
  `(m+1-ceil(.95*(m+1)))/(m+1)`, not always `2/(m+1)`. At the permitted
  m=63, k=61 it is 3/64. The nominal/empirical downgrade makes this a formula
  correction, not a restored distribution-free claim.
- The fixed 810-transcript L1 bill uses 98 C items. The realized reserve-session
  roster can exceed 98 eligible C items across the two pairs; recost local C
  scoring at actual m under the frozen law. A conservative allowance for all
  28 extra attempted C items is another 0.6111 base MBP hours at the stated
  rate, much smaller than the unmeasured load allowance. Do not cap the local
  threshold population at 98 merely to preserve that bill.
- Clarify the F-fitting exception to the post-T3 scoring sentence and correct
  §9's completion labels for R1–R4. These are not evidence of an actual leak.

**Next exact step:** the lead dispositions R1–R4 and revises the binding
inference/null, H4 date-weight and CAP clauses, then obtains both independent
seats' agreement/disagreement on that exact candidate. Registration remains
blocked on G0–G12; no collection, scoring, purchase, calendar extension or
positive-result claim is authorized by this verdict. If the fair comparison
or a valid adequately powered test cannot meet the corrected capacity gates,
that is the point for REDESIGN.

Verification was documentary inspection, the temporary stdlib script and
docs diff/whitespace checks. No unit/full/sharded suite or compileall was
needed for this docs-only change. No network, model download, process/job
inspection, MLX execution, hardware probe, real measurement read or block-5
pipeline occurred. The ruling and coordination state are unchanged; handoff
details live in the accompanying dated run report.

**Lead-only checks outside this sandbox:** once implementation exists, run
the import-gated tiny-synthetic MLX unittest modules for actual/public replay,
forced twins, history/cache/RNG identity, receipt partitioning, helper
concurrency/teardown and tails, one module at a time using their integrated
paths. This review adds no native code/test module and claims none passed.
No weights should be downloaded for those tests. Native parity, timing,
capacity, physical closure and capability gates need the lead's later clean
machine lane, with agents stopped for quiet measurements. Novelty/venue
verification needs separate network authority. The companion seat's verdict,
future G12 size/power and actual host receipt coverage remain unknown here.
