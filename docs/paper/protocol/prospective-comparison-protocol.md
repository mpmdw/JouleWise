# Prospective comparison protocol

Status: PROSPECTIVE / UNPERFORMED. Extracted from the methods/diagnostic
article on 2026-09-05 under the paper-M magistrate ruling. This document
specifies future work and labelled synthetic illustrations; it supplies no
comparison result. Read the article’s Sections 1, 2, and 4 for the energy
allocation, pulse calibration, and sensitivity formulas. References to those
sections refer to `../draft-v2-skeleton.md`; local P.* sections are below.

## P.1 Prospective campaign identities and ratio census

Before either ratio is compared with 2, **authentication** matches every input
to its named source-file contents. **Evaluation** then requires a nonzero
point-only value, making the ratio evaluable. In the prospective design,
the twelve required ratios are
one independent-edge ratio for each of the eight floor components (two models,
two phases, and for each of those the same-model repeat and same-model null
A/B/B/A sources) and one comparative \(R_{cm}\) diagnostic for each of the four
same-model null components. Any of the twelve below 2 falsifies the claim;
equality passes. A ratio of at least 2 means that moving
the edge adds at least one entire point-only value to the bound—the
**twofold boundary contribution** defined by the method. This submission
reports the method and its worked arithmetic; it does not evaluate that
twelve-ratio empirical hypothesis.

That ratio result does not by itself choose between models. The
**decision rule**, fixed before collection, reports a direction only when the
measured difference clears its cell floor and the full lowest-to-highest range
after known errors stays on the direction fixed before collection.

The prospective demonstration—the comparison fixed before collection—is
outside this submission's empirical scope. It
compares the small model `qwen3-1p7b`, revision
`3b1b1768f8f8cf8351c712464f906e86c2b8269e`, with the large model `qwen3-8b`,
revision `545dc4251c05440727734bcd94334791f6ab0192`. <!-- V5-ID-001; V5-ID-002 -->
Its token-generation contrast uses prompt 0 of the ordered eight-prompt
`real_prompts_v1` set for every block in both model arms. The prompt-set SHA-256
fingerprint—an identifier of exact file bytes—is
`20debdb41eb4983339a160176dcf4e475153b5d6f16b1ef3ada39447e99f3474`. <!-- V5-WL-001 -->
Both conditions use the same `tokenizer.json` SHA-256
`aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4` and the
same applied chat-template—the formatter that turns a prompt into model input—
whose SHA-256 is
`87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5`, with
reasoning disabled (Qwen3's optional chain-of-thought output is switched off).
<!-- V5-WL-002; V5-WL-003 --> Greedy generation—choosing
the highest-probability next token at every step—forces 512 output tokens for
one rendered prompt in each run. <!-- V5-WL-004 --> The prefill length-selection procedure remains prospective. No selected
length supplies this submission.
This fixed pair would demonstrate the decision rule; it is not a scaling experiment.
The comparison supports this fixed prompt and makes no prompt-population
generality claim. No result for that pair is reported here.

## P.2 Instrument characterization

<!-- Source: characterization_result_schema_v1; reviewer D3 and C5. -->

Instrument characterization asks four physical questions before any campaign
result may rely on the instrument. Does energy change with the amount of work
in the planned way? Under identical conditions, do repeated paired blocks stay
inside a comparator—an upper limit fixed from earlier, disjoint evidence? Do
the two phase energies account for their enclosing request without leaking dependence across the phase boundary, meaning without prompt-processing energy
changing with work performed after prompt processing ended? And do held-out
reference probes, kept out of the allowance calculation, remain inside the
drift allowance—the maximum within-window change assigned from its designated
references—while the machine recovers within the declared settling convention,
its fixed maximum recovery time? An admitted bundle is a run allowed into the
calculation because it passed its frozen entry and evidence checks.

The following are registered characterization methods, not issued empirical
results. A later campaign must collect their designated inputs and apply the
fixed calculations before claiming characterization. **Floor packs** are the
campaign plans that collect calibration data used to build a comparator floor;
a **contrast pack** is a plan collecting model-comparison data. Their planned
same-condition A/B/B/A blocks build floors and cannot also count as disjoint
characterization evidence. No such report is supplied in this submission.

For workload response, runs are the observations; admission does not establish
the independence the statistical model assumes. Sampler records within a run
are not independent workload observations. A workload-response slope is the fitted
change in energy per output token. A fitted residual is one observed energy
minus the straight-line value predicted for its output length. The residual
must fit both the bundle's allowed timing half-width and a floor issued earlier
for that same cell.

For one A/B/B/A block, let
\(\delta=(B_1+B_2-A_1-A_2)/2\). Each of the four member energies has its
recorded value at its phase boundaries and an edge-moved allowance
\([A_1^L,A_1^U]\), \([B_1^L,B_1^U]\), \([B_2^L,B_2^U]\), or
\([A_2^L,A_2^U]\). Evaluate \(\delta\) over the fixed set of allowed endpoint
combinations and retain the interval of allowed differences
\[
I_i=[\delta_i^-,\delta_i^+]
=\left[
\frac{B_1^L+B_2^L-A_1^U-A_2^U}{2},
\frac{B_1^U+B_2^U-A_1^L-A_2^L}{2}
\right].
\]
The mean interval over the five identical-condition null-test blocks—blocks in
which both conditions are the same—is
\(I_{\mathrm{mean}}=[\sum_i\delta_i^-/5,\sum_i\delta_i^+/5]\). Let
\(C=[-m,+m]\) be the earlier comparator, where \(m\) is its positive joule
endpoint, and define the largest absolute allowed block difference as
\[
M=\max_i\max(|\delta_i^-|,|\delta_i^+|).
\]
No issued null-ladder member endpoints are available, so this construction is
symbolic rather than measured. The forcing problem is that a point value can
hide an allowed nonzero difference, while a mean can hide blocks moving in
opposite directions. The containment test therefore requires every \(I_i\) to
contain zero, then requires \(I_{\mathrm{mean}}\subseteq C\) and \(M\le m\).

Here is a numeric illustration, not measured evidence: its comparator is
\([-3\ \mathrm{J},+3\ \mathrm{J}]\), and its five block intervals, all in
joules, are \([-2,+2]\), \([-1,+1]\), \([-0.5,+0.5]\),
\([-1.5,+1.5]\), and \([-1,+1]\). For this numeric illustration, the
lower endpoints sum to \(-6\) J and the upper endpoints to \(+6\) J, so
\(I_{\mathrm{mean}}=[-1.2\ \mathrm{J},+1.2\ \mathrm{J}]\) and \(M=2\) J.
Every displayed check passes. If, still only as an illustration, the fifth
interval were \([+0.5\ \mathrm{J},+2.5\ \mathrm{J}]\), it would remain
inside the comparator but exclude zero, so that block would fail the first
containment check even though its mean interval would be inside the comparator.

```text
comparator C       [-3 J==========================+3 J]
first block I_1    |    [-2 J----------------+2 J]    |
second block I_2   |      [-1 J------------+1 J]      |
third block I_3    |       [-0.5 J--------+0.5 J]      |
fourth block I_4   |     [-1.5 J----------+1.5 J]     |
fifth block I_5    |      [-1 J------------+1 J]      |
mean interval Ibar |     [-1.2 J----------+1.2 J]     |
```

Diagram legend: `C` is the earlier comparator band; `I_1` through `I_5` are the
five illustrative allowed-difference intervals; `Ibar` is their mean interval;
`|` marks the comparator band's left and right boundaries on each block row;
`=` spans the comparator; `-` is a schematic connector for a block or mean
interval and is not drawn to a numerical scale; and square brackets mark
included endpoints. The endpoint labels carry the numeric values. Five
measured blocks leave every unmeasured block and the population distribution
unknown, so a pass establishes only
measured-block containment, never population coverage.

For phase accounting, the residual
\(D=E_{\mathrm{prefill}}+E_{\mathrm{decode}}-E_{\mathrm{request}}\) is the signed energy left
after subtracting the enclosing request from the two phase energies. A positive
value is double-counted energy. A negative value may be energy in the unphased gap,
the recorded interval between the end of prefill and the start of decode;
its duration times its largest recorded **package power**—the summed CPU, GPU,
and neural-engine power—bounds what may be missing. A resolution band is the
symmetric allowed slope range made from one
admitted prefill half-width across the observed output span. A floor band is
the analogous range made from an independently issued prefill floor. The
shared session timing term is the one bracket-capture timing bound common to
all session members; member-local timing is each run's own local and edge-span
contribution. Timing flags mark a member whose clock bound exceeds a quarter
of its window. Sampling flags mark too few in-window sampler records or a
window whose sampling cadence cannot be recorded or does not stay above a
fixed multiple of the phase rate. The required multiples are the design
constants `SHORT_WINDOW_CADENCE_RATIO_MIN = 2.0` for a short phase window and
`REQUEST_WINDOW_CADENCE_RATIO_MIN = 4.0` for a request window. A missing ratio
records `cadence_ratio_unrecorded`; a ratio below its required multiple records
`cadence_ratio_below_threshold` in `joulewise/reduce.py`.

For drift and recovery, reference roles identify the allowance-building runs
at the window opening, midpoint, and close and distinguish the held-out probes
that cannot enter that allowance. A passing cooldown exit is the first gate
evaluation after a sustained workload whose complete thirty-second rolling
window has at least eighty-percent duration coverage, duration-weighted mean
power no greater than one-and-one-tenth times the clean reference, and nominal
thermal pressure; elapsed recovery time starts when the sustained workload
ends and stops at that first pass.

The registered minimum basis is forty admitted bundles over five output
lengths for workload response; five disjoint A/B/B/A test blocks at each
null-test magnitude; twenty-four admitted bundles and two bracket captures for
phase accounting; and six designated reference members, three held-out probes,
and three sustained-work/cooldown pairs for drift and recovery. A **workload level** is one output-token count fixed before collection, and a **workload magnitude** is one target size in the null test. Failure withdraws the relevant
**per-token conversion**, the fitted joules per output token, floor, or
phase-specific claim. These are design requirements, not counts collected
for this paper.

The workload-response slope has a special exact calculation because choosing a
lower or upper endpoint independently for forty energies appears to require
\(2^{40}\) joint combinations. Ordinary least-squares fitting chooses the
straight line whose squared vertical departures from the observed energies are
smallest. With fixed output levels, its slope is a fixed weighted sum,
\(\hat\beta=\sum_i w_iE_i\), of the forty energies. For output count x_i,
w_i=(x_i−mean(x))/sum_k(x_k−mean(x))², with units per token. Each energy has an allowed
lower endpoint \(L_i\) and upper endpoint \(U_i\). To obtain the smallest
allowed slope, use \(L_i\) wherever \(w_i>0\) and \(U_i\) wherever \(w_i<0\);
to obtain the largest, reverse those choices. A zero weight changes neither
result. Thus the positive-slope screen at its fixed zero threshold—the
numerical cutoff the slope must exceed—needs two endpoint vectors, not all
\(2^{40}\) combinations. <!-- C1.2/C1.3: fixed forty-bundle design and zero threshold; reviewer D3 -->

An illustrative three-term excerpt, not measured data, uses counts 1, 2, 3 tokens, mean 2, and squared-deviation sum 2, hence weights
\((-0.5,0,+0.5)\ \mathrm{token}^{-1}\) and allowed energy intervals
\([0,2]\), \([2,16]\), and \([16,24]\) J. The minimum chooses \(2\)
for the negative-weight term, either endpoint for the zero-weight term, and
\(16\) for the positive-weight term. For this numeric illustration, the
minimum is \(-0.5(2)+0.5(16)=7\) J per output token and the maximum, after
reversing those endpoint choices, is \(-0.5(0)+0.5(24)=12\) J per output
token. The forty-member calculation applies that same sign rule to every real
weight.

```text
allowed endpoint pair [L_i, U_i]
              | w_i < 0  --> minimum U_i; maximum L_i
weight w_i ---| w_i = 0  --> either endpoint; contribution unchanged
              | w_i > 0  --> minimum L_i; maximum U_i
```

Diagram legend: `[L_i, U_i]` is one energy's allowed endpoint pair; `w_i` is
its fixed least-squares weight; the three branches are negative, zero, and
positive weight signs; `-->` maps a sign to its endpoint choice; and “minimum”
and “maximum” name the two slope vectors being constructed.
This shortcut does not apply to the separate moved-edge-limit calculation: it
recalculates a mean and sample standard deviation at every joint endpoint
choice. Changing one endpoint changes both quantities and the largest
residual, so this nonlinear calculation refuses exact enumeration above sixteen
observations.

If issued, an identical-condition result would have a deliberately narrow
meaning: five contained measured blocks would establish only the containment
drawn above. It would neither estimate a percentage of a wider population nor
supply an independent coverage guarantee. <!-- reviewer C5: containment caveat -->

## P.3 Directional comparison and claim gates

Two directional comparisons—token generation and prompt processing, each with
its expected direction fixed before collection—share one two-sided Holm
step-down correction. We apply Holm at nominal family-wise level 0.05 to two
model-based tests; error control depends on their distributional and dependence
assumptions. For each block \(i\), first form its paired difference
\(d_i=B_i-A_i\), condition B's mean energy in that A/B/B/A block minus
condition A's mean energy. For the gross phase-energy contrasts used here, the
current builder supplies no additional stochastic metrology variance, so the
**repeat standard error** is the standard error of the block differences,
\(se_{\mathrm{repeat}}=s/\sqrt{n}\), where \(s\) is their sample standard
deviation. Timing and other deterministic allowances are propagated
separately. Divide the mean \(\bar d\) by \(se_{\mathrm{repeat}}\); with
\(n=10\), the Student-\(t\) reference has \(n-1=9\) degrees of freedom. The null
hypothesis is zero mean difference; “two-sided” counts equally extreme positive
and negative statistics. The resulting tail area is that comparison's **raw
probability** \(p\).

An illustrative, not campaign data, fixture uses ten block differences in
joules: \([5.0,7.6,5.5,4.2,4.7,6.8,5.5,3.6,3.9,3.2]\). Their mean is
\(5.0\) J, their squared deviations sum to
\(\sum_i(d_i-5.0)^2=17.64\ \mathrm{J}^2\), and therefore
\(s=\sqrt{17.64/9}=1.4\) J and
\(se_{\mathrm{repeat}}=1.4/\sqrt{10}=0.442719\) J. With no additional
stochastic metrology term on this phase path, \(t=5.0/0.442719=11.2938\) on 9
degrees of freedom, with two-sided \(p=1.29\times10^{-6}\). The separate
dependence-sensitivity sheet,
`docs/paper/round7/dependence-sensitivity.md`, works the same ten differences
under a stipulated effective-sample-size halving and an estimated AR(1) model,
which treats adjacent block errors as serially correlated. Those alternatives
are sensitivity scenarios, not estimates of independence for the campaign.

Order the two raw probabilities \(p_{(1)}\le p_{(2)}\). Compare the first with
0.025; only if it passes, compare the second with 0.05. Pairing that
\(1.29\times10^{-6}\) with a second illustrative raw probability of \(0.041\) for
the other comparison orders them as \(1.29\times10^{-6}<0.041\): the smaller
passes 0.025, then 0.041 passes 0.05, so both directional comparisons pass
Holm. If one contrast is missing, its slot remains: a sole value 0.041 is
compared with 0.025 and fails, while the missing contrast cannot pass. Holm is
one step; the decision-interval sign check (the direction gate) in the next
paragraph is the other. The sheet's \(\nu=9\) row adds a stipulated
0.2-J stochastic metrology standard error to these same deltas; its different
raw probability also passes Holm, but its decision interval fails the
direction gate. That composition example is not a campaign input.

A directional result then faces two different checks. The magnitude check
requires the absolute point estimate to exceed \(F_{\mathrm{cell}}\); failure
means **not resolvable**—the estimate does not clear the cell floor—not zero.
The direction check requires the measurement interval, formed from the repeat
standard error already defined for this gross phase-energy path, and the
decision interval, formed by extending both ends by the sum of the recorded
deterministic bounds. A deterministic bound is a
non-random maximum displacement carried in the authenticated block record.
A **reducer** is the program that turns a retained run bundle into phase energies.
For native interval-average records, the reducer integrates constant reported power
over the overlap duration; its interpolation-bound term is zero. Timing
uncertainty enters through separately recomputed boundary envelopes. An
**interpolation edge** is the point-sample fallback's phase-window start or end
between neighboring point samples. The named **deterministic-bound kinds** are
that fallback's joint interpolation-edge movement, idle-power drift for
idle-subtracted request energy, clock-anchor movement, and
the whole-window drift allowance. For each kind, use its recorded contrast bound when present, otherwise
add its A-side and B-side bounds; average that kind across the ten blocks, then
sum those kind averages. Both intervals must lie wholly on the direction fixed
before collection and the Holm-adjusted test must pass. In the synthetic
example, a 10.0-J point estimate exceeds the 3.0484-J floor. Its measurement
interval is [9.5, 10.5] J. If the authenticated deterministic-bound list for
that example contains 0.10 J and 0.15 J, its sum is 0.25 J and the decision
interval is [\(9.5-0.25\), \(10.5+0.25\)] = [9.25, 10.75] J. Both intervals remain positive and pass the sign check; Holm must pass
separately. No test data are assigned to this 10-J geometric example, so it
does not establish an adjusted-test pass or authorize a positive direction.
In general its measurement half-width is h=t_critical × SE; h=0.5 J could
be obtained with t_critical=2.262 and SE=0.2210433245 J. These are stipulated
geometry inputs, not the ten-delta test above (registry SYN-04).

A separate explicit synthetic test dataset can supply the 10-J geometry:
five block differences equal 10−c and five equal 10+c J, where
c=1.5/2.262 J. Their mean is 10 J, sample SD is c√(10/9), and
SE=c/3=0.5/2.262 J. Using the fixed critical 2.262 gives h=2.262×SE=0.5 J.
The zero-mean test statistic is 10/SE=45.24 on 9 degrees of freedom,
with two-sided p=6.300451137599192×10⁻¹². Pairing this actual synthetic
calculation with the earlier ten-delta p=1.28854294284577×10⁻⁶ passes
Holm’s 0.025 and 0.05 thresholds separately from the sign check. This
fully specified synthetic pair demonstrates the procedure; it is no model result.

The floor and decision interval remain separate mandatory gates. For a
symmetric measurement interval with half-width \(h\) and symmetric nonnegative
deterministic widening \(B\), their numerical conjunction is
\(|\mathrm{estimate}|>\max(F,h+B)\); asymmetric intervals use their actual
endpoints. \(F+B\) is only a non-gating planning diagnostic, neither necessary
nor sufficient for acceptance, and neither mandatory gate may be removed as
double counting.

The method's **signed clearance or shortfall** is the absolute point
estimate minus the cell floor. A positive value is the amount by which the
magnitude check clears; zero or a negative value is the shortfall and cannot
pass. The synthetic example prints \(10.0-3.0484=6.9516\) J. This difference
summarizes the magnitude check; it does not replace either uncertainty
interval used by the direction check.

### Evidence refusal and claim gates

The schematic describes the method's possible decisions; this paper reports
no new model-comparison verdict.

Figure 3 separates evidence refusal from the two claim gates. An admission
failure means the stage did not pass the entry check. **Custody** means that
each named input's fingerprint still matches its recorded bytes; a custody
failure means at least one does not. Missing, stale,
contaminated, duplicated, inconsistent, or unauthenticated evidence enters a
side path and is refused before either gate. Usable evidence carries a point
estimate and its complete uncertainty interval to the magnitude gate; a value
that clears the cell floor then reaches the direction gate. The four
possible outcomes are refusal, not resolvable, direction unresolved, and a
directional claim.

![Figure 3. Evidence refusal and two sequential claim gates.](../figures/fig3_decision_gates.svg)

*Figure 3. Decision-gate schematic; no measured data or numeric threshold is encoded by its layout. On the white background, the title and subtitle identify two gates and four outcomes. In the upper lane, a dashed box lists an admission or custody failure and the six evidence defects that can cause it; a right-pointing arrow labelled as a side entry that reaches no gate leads to the bordered “refused” box, which says that the evidence produces no authorized comparison result. A pale horizontal rule separates that refusal lane from the lower decision lane. The lower lane starts with a gray measured-contrast box containing the point estimate and composed uncertainty interval. A right-pointing arrow leads to the first white rounded box, Gate 1, which asks whether the estimate's magnitude exceeds the cell floor. Its “yes” arrow leads to the second white rounded box, Gate 2, which asks whether both intervals point the registered way and Holm passes; the next “yes” arrow leads to the blue directional-claim box, which states that both gates passed in the direction registered before collection. Gate 1's downward “no” arrow leads to the “not resolvable” box, which says the effect is smaller than this instrument can resolve and does not mean zero, equality, or no difference. Gate 2's downward “no” arrow leads to the “direction unresolved” box, which says the floor cleared but the interval or Holm did not settle direction, so no claim is made. The bottom notes define the cell floor as the registered operational resolution guard for assigned-energy differences, retain the separate floor and interval gates, and identify F+B—floor plus deterministic widening—as a non-gating planning diagnostic, neither necessary nor sufficient for acceptance.*

## P.4 Operational admission and refusal

If a required measurement is missing, malformed, outside its fixed limit, or inconsistent with another record, collection stops and records why; the program never substitutes a favorable value or silently skips the member. This behavior is *fail-closed*. The unit governed this way is a measurement window, including its calibrations, declared runs, cooldowns, and final verdict.

### Measured admission rules

To admit a stage—that is, to allow its first measured member—the program evaluates these recorded fields and limits immediately before measurement:

- After any operator or stage intervention, it waits \(180\) s with no experiment activity. The environment record must show `power_source = "AC Power"`, `power.external_connected = true`, `low_power_mode = false`, `display_power_state = "all_asleep"`, `screensaver_engaged = false`, and `thermal_pressure = "nominal"`. `power.adapter_watts` must be numeric and must match every other admission observation in the window; adapter description and power-source labels must also remain unchanged. Any mismatch or missing required field refuses admission.
- The pre-run idle baseline samples for \(30\) s at a requested \(10\) Hz and must yield at least \(30\) complete processor-state and power records. For each record, CPU busy ratio is the largest across cores of \(1-\text{idle ratio}-\text{powered-down ratio}\), clipped to \([0,1]\). The reported `cpu_busy_ratio_p95` and `processor_combined_power_w_p95` use nearest-rank p95: sort \(n\) values and select item \(\lceil0.95n\rceil\). Admission requires the former to be at most \(0.5\) and the latter at most \(1.0\) W.
- In those same idle records, fewer than \(40\%\) of raw `gpu.idle_ratio` values may fall below \(0.80\), and `gpu_freq_mhz_mean` must be at most \(800\) MHz. Missing or malformed CPU, GPU, or power telemetry refuses admission. One completely recorded idle-baseline retry is allowed; failure of the retry aborts that stage attempt.
- Between members, the cooldown rule must pass before \(300\) s. A cap hit refuses recovery. Runtime and power-source identities, clock-anchor status, power-record spacing, calibration age, and the post-run environment are also checked. An operator override is recorded but makes the member diagnostic only, never claim-bearing.

A stage attempt stops at its first member failure. If the same cause fails a window stage for the third time, the **window closes**; this rule does not merely close or restart the stage. All collected material remains preserved as diagnostic evidence.

### Counterbalanced order

Each comparison uses A, B, B, A order fixed before collection, with an admitted cooldown between members. Heating or other approximately linear drift over the hour can otherwise favor whichever condition runs later. If run midpoints are \(t_{A1},t_{B1},t_{B2},t_{A2}\), exact first-order balance is \(t_{A1}+t_{A2}=t_{B1}+t_{B2}\); the measured contrast is \((B_1+B_2-A_1-A_2)/2\). Unequal runtimes and cooldowns can break exact balance, while curvature and the separate whole-window drift allowance remain, so the retained midpoint times are part of the evidence rather than an assumed symmetry.

### Every input and every refusal remains visible

Every file the analysis reads is fingerprinted. Failed or interrupted attempts are never deleted or overwritten: an occupied retry slot moves to retained quarantine, the retry uses a new slot, and an append-only replacement record identifies both occurrences. Two present bundles claiming one occurrence cause a refusal. The final verdict binds the declared member set, preserved attempts, replacements, calibration bracket, policy, and drift evidence, preventing later selection of a favorable subset.

Invalid evidence is refused; usable evidence below the floor receives a different outcome. The refusal log preserves contaminated members, calibration outside the allowed condition family, stale drift evidence, unresolved clock anchors, and duplicate recorded occurrences. Below-floor effects are recorded as not resolvable, not invalid evidence. These are specified refusal behaviors; no missing campaign result is treated as an observed empirical refusal.

The repository is tamper-evident for the operator's own benefit—a way to catch mistakes—not tamper-proof against another program or person. It assumes a single trusted operator, so its gates defend against error and post-hoc choice rather than an adversary; they provide internal consistency, not third-party provenance (evidence that would convince someone who does not trust the operator).

The repository artifact guide holds the maintainer-facing path conventions,
**freeze receipts**—records that fix the plan bytes and the time those bytes
were frozen—generated-state checks, and reissue workflow; Appendix A retains
the scientific route from raw bytes to the reported verdict.

## P.5 Campaign dependence and custody limitations

Fourth, the prospective design's ten blocks in one measurement window would not automatically be ten
independent physical draws. Consecutive member runs inside a block share the same
local machine state, and blocks can share the calibration bracket, thermal
trajectory, background activity, neighbouring sampler behavior, and serial
change across the window; a deterministic allowance can widen an interval but
does not make those observations independent. Positive dependence would make
an independence-based repeat standard error and tail probability too small,
while its direction and size here are unquantified.

<!-- Source: docs/paper/round7/dependence-sensitivity.md; reviewer item D6; ranked item 15. -->
The sampling unit—the smallest observation treated as a separate draw—is one
complete A/B/B/A block, never one of its four member runs. For block \(i\),
\(d_i=(B_{i1}+B_{i2}-A_{i1}-A_{i2})/2\). For this path, the **total standard error** equals the modeled repeat
standard error, with no additional stochastic metrology variance. The
sensitivity calculation is

\[
\begin{aligned}
s&=\text{sample standard deviation of the complete block differences},\\
n&=\text{number of complete blocks},\\
V&=\text{variance multiplier supplied by the selected dependence model},\\
n_{\mathrm{eff}}&=n/V=\text{number of independent blocks with the same repeat standard error},\\
\nu&=\text{Student-}t\text{ degrees of freedom supplied by that model},\\
\mathrm{SE}_{\mathrm{repeat,model}}&=s\sqrt{V}/\sqrt{n}=s/\sqrt{n_{\mathrm{eff}}},\\
\mathrm{SE}_{\mathrm{total}}&=\mathrm{SE}_{\mathrm{repeat,model}}
\quad\text{for the gross phase-energy path used here}.
\end{aligned}
\]

The registered independent-block model supplies \(V=1\),
\(n_{\mathrm{eff}}=n\), and \(\nu=n-1\). The AR(1) estimated-adjacency model,
which relates each block to the immediately preceding block, supplies \(V\)
from its finite sum over the estimated correlation between successive block
differences and uses
\(\nu=\min(n-1,\lfloor n_{\mathrm{eff}}\rfloor-1)\). The named fixed effective-
sample-size halving case supplies \(V=2\), \(n_{\mathrm{eff}}=5\), and \(\nu=4\).
For these gross phase-energy contrasts the current builder supplies no
additional stochastic metrology variance, so \(SE_{\mathrm{metrology}}=0\) on
this path and each model's total stochastic standard error reduces to its
modeled repeat standard error. The dependence-sensitivity sheet's worked
example stipulates a nonzero \(se_{\mathrm{metrology}}\) and is an arithmetic
check of the composition, not a campaign input. Timing and other deterministic
allowances remain separate. <!-- Pre-registered design/model
constants: docs/paper/round7/dependence-sensitivity.md:28-52; builder treatment:
joulewise/analysis_engine/__init__.py:588-603 and
joulewise/analysis_engine/estimators.py:350-371; not measured values. -->
If any member is absent, invalid, or not admitted, its contrast cannot enter
the registered claim procedure: the analysis uses no shortened set, outcome-
driven replacement, or top-up, and it does not calculate the registered result
unless all ten complete blocks are present. The A/B/B/A order counterbalances
straight-line drift and cancels it exactly only when the A and B time-midpoint
sums match; unequal runtimes or cooldowns break that balance. <!-- Source:
docs/paper/round7/dependence-sensitivity.md:6; reviewer D9; ranked item 16. -->
\(A_k\) is one family-level allowance for remaining across-window curvature
and repeatability added once to the component floor, so it is not an additional
member or block charge. Within-arm variation—variation among runs of the same A
or B condition—can manufacture an apparent paired difference; ordering does not
remove it. <!-- Reviewer D9; ranked item 16. -->
The identical-condition null illustration covers only its five synthetic
intervals. Even a later measured pass would establish neither population
coverage nor equality. <!-- DS-03; KEY_FROZEN /
VALUE_UNISSUED. Five-block design: docs/contracts/analysis_plans.md:380-381;
reviewer D11; ranked item 16. -->
The exact closing check is to retain all blocks in collection order, rerun the
registered independent-block calculation and every pre-registered dependence
sensitivity model, and compare their total standard errors, degrees of freedom,
intervals, and direction gates without changing the member set.

Fifth, the generic floor consumer does not independently rederive every
uncertainty width from primary inputs. It binds configurations, membership,
identities and point metrics; its floor validator recomposes the result from
widths supplied by the floor artifact. The mint performs a stronger
source-based width comparison. Thus a coherently produced wrong-width artifact
is not independently caught at every consumption boundary. Byte seals catch
later substitution but do not close that production-error gap. This submission
publishes no new floor; the gap is a limit of the reusable method, not a
claim that an unissued floor was reproduced. Section 9 describes the separate
paper-input custody requirement and public reproduction limits.

Sixth, the provenance is trusted-operator rather than adversarial. The hashes
and refusal records can expose an accidental edit or inconsistent derived file,
but an operator who controls acquisition, hashing, and analysis could replace
the primary files and recompute the records consistently; the possible effect
on any reported value is therefore unquantified and could favor a claimed
contrast. A reader could close this limit only with independently held
acquisition evidence—for example, a separate operator or laboratory retaining
append-only, signed raw records and comparing them with the analysis archive—so
that the person producing the claim cannot rewrite the evidence and its
fingerprints alone.

## P.6 Prospective publication supply chain

Under D-173, the adopted paper-custody rule, a claim-bearing supplier must
obtain inputs through the typed custody-read interface `open_paper_input(ref)`:
a role name and runs root resolve through a clean-Git supply map to fixed
paths and expected digests, followed by fresh validator replay from disk.
The rule is an input requirement, not evidence that this draft has a released
production supply chain. It does not close the generic floor consumer's
uncertainty-width gap described in Section 7. Any later floor publication
requires a source-member and width census, bracket and basis identifiers,
estimator identity, and an independently reconstructed-versus-published floor
comparison. Correct points with coherently wrong widths cannot count as
source reproduction. No such prospective floor or model verdict is published
here. Hashes provide trusted-operator consistency, not third-party provenance.

## P.7 Future validation designs

The inserted-gap study remains possible future diagnostic work; it is not a
predicate for this submission and this paper has not run it. Its gap, run count,
estimator, and residual comparison are fixed before collection. It is a proposed
design, not yet a runnable protocol: its sleep
actuation, command-stamp method, and fitted-edge selection remain to be fixed.
Hold model identity, prompt, tokenizer, and
generation rules fixed at the values registered for the campaign. In each of
about ten otherwise identical real-workload runs, insert an approximately
500-ms commanded sleep during which the inference workload submits no GPU work.
Place it after the runtime stamps prefill completion and before it stamps decode
start. Retain both command stamps, the surrounding power records, the before-
and-after calibration bracket, and every refusal record. <!-- TRANSFER-FIDUCIAL-01 at
docs/process/state_kernel.json:/tasks/TRANSFER-FIDUCIAL-01; runtime events:
joulewise/adapters/mlx_runtime.py:795-809 emits phase_end/prefill, "mlx prefill
completed", and phase_start/decode, "mlx decode started". -->

Apply the detector that Section 2 defines for commanded pulse edges, without
modification, to the falling edge when the sleep begins and the rising edge
when decode resumes. For each edge
\(e\), define
\(r_e=t_{\mathrm{fit},e}-t_{\mathrm{command},e}\), where
\(t_{\mathrm{fit},e}\) is the detector's fitted edge time and
\(t_{\mathrm{command},e}\) is that edge's independently stamped command time.
Report every signed \(r_e\) and record its comparison with
\(B_{\mathrm{fiducial}}\), where
\(B_{\mathrm{fiducial}}=0.030067931757111657\) s is the retained diagnostic
capture's pulse-derived limit. <!-- DG-027; MEASURED / DIAGNOSTIC_ERA /
REPLAY_FENCED. --> The registered row does not prescribe an acceptance
threshold for that comparison, so this paper does not label a result a pass or
transfer failure. A reader can recompute both residuals from the retained
command stamps and power trace.

The external-meter study is a proposed design, not yet a runnable protocol: its
tested load settings—its workload levels—meter synchronization, and allowable range for \(g\) remain to
be fixed. This paper has not pre-registered it. Place the meter on the wall side of the
machine's power supply. At each workload level already registered for the
campaign, integrate the meter's power over the same request start and end stamps
that the counter uses, obtaining \(E_{\mathrm{meter}}\), and retain the counter's
whole-request energy \(E_{\mathrm{counter}}\) over that window. For each load,
calculate \(g=E_{\mathrm{counter}}/E_{\mathrm{meter}}\). Fix an allowable range
for \(g\) before collection, report every ratio, and pass a load only when its
ratio is inside that range. This tests whole-request gain, not the phase split.
A separate Apple Silicon machine can repeat the complete protocol; other
questions remain outside this capstone's scope.

## P.8 Comparison archive objects

3. The fixed campaign plan, its freeze receipt, calibration-acceptance file, policy, drift-bound artifact, extraction specification, and analysis manifest. The receipt issue time and fingerprints establish which membership, limits, estimator, and contrasts were fixed before the evidence they judge.
4. The append-only whole-window verdict, which binds admitted members, preserved failures and replacements, the calibration bracket, policy, and drift evidence. The floor extraction then binds each reported floor to its admitted cell. The claim verdict binds the contrast estimate, composed uncertainty, cell floor, and two decision gates to those authenticated inputs.

## P.9 Comparison refusal interpretation

A refused contrast does not show equality. It says the named instrument and evidence cannot adjudicate that difference: the effect may be absent or may lie below what the cell resolves. Failed and interrupted occurrences remain in the archive, while replacements are named separately; therefore extra directories are expected and must never be treated as admitted merely because they exist.

## P.10 Historical release-status note

### A.6 Release status

No public archive, release revision or fingerprint-manifest locator has issued.
Section 9 and registry DS-34 give the current availability statement; local
project custody paths are not public release locators. A complete public
historical replay remains unavailable, while Figure A1 can be regenerated
from the repository alone.

## P.11 Fresh collection prerequisites

Fresh collection additionally requires the configured Apple-silicon instrument, the exact model files named by the plan, the measurement environment recorded in `env/mac-measurement-lock.txt`, non-interactive permission to run `/usr/bin/powermetrics`, and the measured admission predicates in Section 5 (the pass/fail checks a machine's own calibration must satisfy before its runs are admitted). The retained configuration used the machine named in Section 1. This work does not establish that another Mac, operating-system build, model revision, or quantization shares its measured limits; that machine must characterize its own cells.

