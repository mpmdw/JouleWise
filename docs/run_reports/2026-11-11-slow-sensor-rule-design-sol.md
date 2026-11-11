# Slow-sensor rule: independent Sol design seat (RL-75)

2026-11-11. Branch `design/2026-11-11-slow-sensor-rule-sol`, based on W1
`b4a6c217f0285a20aff33a8407160dd77af2a8a6`. **Design and offline thermal replay
only. Nothing built for, armed on, or run on the measurement Mac.** Fable closes
the round. I have not read the other seat's plan or requested a peer consult.

## Recommendation and the decision it requires

The slow role should represent the long thermal tail, rather than acquire that
name solely by crossing the 60 s class boundary. My preferred scientific policy
is option 2 below: preserve both a fast gate and a separately responsive slow
gate, amend **only the slow role's return ceiling to the fixed 1,200 s R1/G0
ceiling**, and keep the existing 300 s G1/H ceiling and duty bar as independent
admission tests. Select by the amended classifier, not by naming Tf08 manually.
This does **not** establish that this policy is operationally feasible.

In fact, the existing thermal replays warn strongly against signing it yet:
the Tf08 G0 waits exceed even the most generous possible G0 share of W1's
current duty budget. A classifier amendment cannot repair that. If the native
D smoke and subsequent W1-schedule rehearsal cannot meet the unchanged duty
bar, use the registered fallback process and return to the lead; do not quietly
reclassify a fast-family sensor as equivalent deep-mass control.

Option 3A (two fast-family gates, Tf08 recorded) is a coherent, narrower
alternative if the lead deliberately chooses proximal thermal control plus
observation of the long tail. It needs a prospective claim/selection deviation
and a way to record the extra key. The present policy cannot express that extra
record-only channel. Option 1 alone is the least attractive: it can satisfy the
letter of the class rule without controlling or even recording the long tail.

## Authority, intake, and exposure limits

Read: RL-72, RL-74 and RL-75 in full from audit ref `5bb224eced70…`; the adopted
follow-up plan, replay, tests and manifest from `a12fd0e381bf…`; **only** W1
protocol lines 223–254 (WP14(a)); the specified runtime/gate/classifier/kit code;
and the sanctioned E1 print and copied thermal journals. RL-75 narrows RL-74(2):
an R0-fast winner requires Fable's ruling, even if its R1 slow class is stable.
R0 classified all six named keys, so the prior-inventory naming fence is met.
TV0h/TV1h are aliases; they cannot fill two roles. E1 also reports TV0s/TV1s as
aliases on that record, so treat them as one candidate there, not replication.

M0: no active stop card or global gate; workspace initially clean on the exact
requested branch/base. The generated queue and known-workspace prose are older
than this explicit brief; this brief selects the design-only AGENT work. Read
the targeted intake, playbook, orchestration and D-009/D-050/D-063 authority.
Per the brief, no coordination-state files or kernel tasks were changed.

**Exposure incident for the lead:** my first audit command printed the whole
decision document instead of extracting the requested headings. The tool
returned truncated but unrelated Block 5 policy/outcome prose. A later RL-59
range also extended into the following decision-request introduction. This
included aggregate ledger/check counts, not just thermal material. I therefore
cannot attest strict non-exposure to Block 5 prose under the task's narrower
sealed-Block-5 instruction. No Block 5 result file, real measurement dataset,
or forbidden external directory was opened. The design calculations below use
only thermal inputs and code constants, but the research lead must adjudicate
this seat's blinding acceptability before adoption. Subsequent audit reads
were restricted. This is an exposure disclosure, not an asserted waiver.

No network, SSH, weights, model execution, energy/power/token/performance
analysis, decode/turn-duration extraction, v4 outputs, real restricted data,
Block 6 or BYTES data were used. External data reads were confined to the two
paths authorized by the brief; absolute custody paths in source documents were
treated as text. The initial released-Block-5 standing rule was not used to
override the task's later, stricter blinding rule.

## What the registered rule and the current implementation do

WP14(a), W1 protocol `:223–254`, pins `smc_enumeration.RULE` verbatim. Both roles
need the existing quality/coverage, resolving-rise, noise, clamp and heat-order
checks and `t1 = tau * ln(rise / 1 C) <= 300 s`. Fast has `tau <= 60 s`, noise
`<= 1/3 C`, and largest rise; slow has `60 < tau <= 300 s`, noise `<= .15 C`,
and longest t1, with lexical ties. Each phase needs at least 99% one-second
cells, under 1% read errors and no consecutive empty cells. R1 D is final;
30B is record-only; a null role is not a manual-substitution licence.

These are **model-free crossings**, not fitted exponential constants:
`smc_enumeration.py:470–475, :640–668`. The baseline is the final idle-minute
median, rise is the final load-tenth median minus that baseline, and class tau
is the first recovery read's excess/e crossing timed from that read.
`select_keys` at `:894–899` chooses the largest-rise die key and longest-t1
heatsink key. Aliases are diagnosed in `rank :712–724` and
`r1_runtime.py:448–466`; the kit refuses aliased roles at
`scripts/align_v4_kit.py:248–269`. A name prefix establishes no anatomy.

The operational gates differ:

| feature | G0 | G1/H |
|---|---|---|
| reference | captured/consumed pre-warmup idle median | **actual G0 release** temperatures |
| release | 10 consecutive samples in both upper bands | 5 consecutive samples in both upper bands |
| slow slope | absolute 60 s OLS slope <= .2 C/min | no slope bar |
| status | fresh os_level 0 and PM Nominal | no corresponding status test in release predicate |
| cap | R1 1,200 s; W1 derived, at most 1,200 s | at most 300 s per wait |

All require observed valid, fresh, continuous samples. These are one-sided
upper bands, not absolute-distance bands. See `thermal_gates.py:541–596`;
G0's release alone sets `episode_reference` at `:631–635`. H is dispatched
after a configured heavy-cell chunk (`endpoint.py:310–325`); G1 before later
turns (`workload.py:539–543`). A G1/H timeout stops further work. An unreleased
G0 has no episode reference and W1 ends the member (`workload.py:444–455`);
RL-72's follow-up timeout dispatch exception applies only to step kinds.

Gate-policy data can select two keys, two bands and caps; it cannot select
different key pairs by gate kind. `thermal_gates.py:101–108, :150–164` rejects
unknown options and turn caps above 300. Sensor policy has exactly fast, slow,
fan keys and R0 digest (`thermal.py:22–40`); `keys :43–44` samples those two
temperatures and F?Ac fans. There is no third-temperature record-only field.
Putting a T key in `fan_keys`, duplicating a thermometer, or using a huge band
does not implement an independent record-only role: validity/coverage still
involve the purportedly inactive key.

The kit also requires a passing D classification, matching classification
digest, keys in the matching class lists, **equality to the selected picks**,
and lead verification of changed-pick S6/S7 (`align_v4_kit.py:231–280`). Editing
only a JSON sensor name cannot bypass these obligations.

## Thermal evidence and arithmetic

### The 30B inventory print: narrow class, sampler failure, candidate gates

E1's real classification returned null/null before class arithmetic: recovery
coverage .7617, 55 consecutive empty cells and .075 read-error fraction despite
zero key-read errors. Its gates-bypassed arithmetic is diagnostic, not a pass.
TV0h: tau 40.2 s, rise 57.52 C; Tf08: tau 140.4 s, rise 55.84 C, t1 564.9 s.
Including long sweeps changes Tf08 to 143.8 s and t1 578.6 s, still failing.
Tf08 remains 3.81 C above its classifier baseline at recovery's last read.

At rise 55.84 C, `300 / ln(55.84) = 74.58 s`. Thus the nominal slow interval
is effectively `(60, 74.58] s`, only 14.58 s wide. TV0m changes from tau 60.2 s
(slow, t1 236.5 s) to 58.0 s (fast) when long sweeps are retained; TV0s/TV1s
then appear slow at 66.6 s, t1 267.1 s. None is a demonstrated native-D winner.

Changing only the 1 C return target to the gate's present band does **not**
solve Tf08's admission problem:

- `140.4 * ln(55.84/1.5) = 507.8 s > 300 s`;
- even at the tuning ceiling 2 C: `140.4 * ln(55.84/2) = 467.4 s > 300 s`;
- a 300 s return would require `delta >= 55.84*exp(-300/140.4) = 6.59 C`.

That last band is outside the adopted 2 C tuning ceiling. Against the fixed
1,200 s G0 ceiling, the original 1 C t1 of about 565 s fits. These predictions
are not observed G0 waits and do not include slope, dwell or reference drift.

The appended **“RL-74: step-30b G0 replayed on the candidate keys”** section was
read. Its inventory own-reference capture has only .797 coverage and 47 valid
reads; its early G0 also latches unobserved. The following candidate releases
waive those faults and omit unavailable status. They are threshold diagnostics:

| slow slot, TV0h fast | own-reference G0 at 1.0 C | at 1.5 C | deciding condition at 1.0 / 1.5 C |
|---|---:|---:|---|
| TV0m | 429.82 s | 342.83 s | band / slope |
| TV0s or TV1s | 671.83 s | 477.84 s | band / slope |
| Tf08 | censored before real load | 738.83 s | band / band |

TV0h-as-single-thermometer diagnostic: 182.85 s at either band; **not a valid
two-role policy**. The sound sidecar/status control gives Tf08 714.95 s at
1.5 C and 1,006.95 s at 1.0 C against exact R_op. A .026 C lower thinned
inventory median delays the 1.5 C release by 24 s. Thus the diagnostics do not
justify carrying S6=1.5 to a new V-family winner; RL-74 requires its own default
`max(1 C, 3*soak SD)` and its own tuning evidence.

### D members: observed warmup cooldowns, not completed D steps

The unchanged replay's self-check reproduces all 13 recorded G0 outcomes and
R_op bit for bit; released waits agree within the stipulated 2 s. The five D
members timed out against cold R_op; RL-59 confirms no D turn was run in them.
Their G0 cooldowns are useful data, but cannot supply D's post-turn tau or a
D-after-D duty result. The following common-reference replay uses the historical
step-D retry's own median, **34.307 C fast, 28.586 C slow**. It is not the new
follow-up's R_D after the prescribed 30B predecessor.

| member | Tf08 G0 joint, 1.5 C | band-only, 1.5 C | slope-only | joint, 1.0 C |
|---|---:|---:|---:|---:|
| A1 | 728.41 | 702.42 | 723.43 | 835.42 |
| B | 877.65 | 715.65 | 577.65 | 877.65 |
| A2 | 716.55 | 660.55 | 716.55 | 862.54 |
| step-D first | 753.16 | 728.16 | 721.16 | 1,055.16 |
| step-D retry | 815.21 | 801.21 | 693.21 | 932.21 |

Times are seconds from G0 entry. Intermittent band/slope excursions explain why
the joint wait can exceed both first single-condition release times; do not
estimate it by their maximum. At 1.5 C the common-reference release margins are
.058, .777, .194, .126 and .205 C, respectively, not the much larger at-cap
margins. Own-reference joint waits are 728.41, 877.65, 862.54, 753.16, 815.21 s.
The planning streams, which had a heater, are only threshold tests under a
changed reference: common-reference 1.5 C releases are 462, 694, 889 and 866 s.

The new desk diagnostic stops each counterfactual at its recorded G0 end.
It reports per-key first return, ten-sample band hold, slope and joint checks,
plus role reversal.

The following per-key times use **each member's own** reference, unlike
the common-reference table above. The first band entry need not persist;
the ten-sample column applies the dwell/status/continuity tests. The
single-key rows are virtual diagnostics, not valid two-role policies.

| member/key | first in band 1.0 / 1.5 C | ten-sample band 1.0 / 1.5 C | slope-only | joint at 1.5 C |
|---|---:|---:|---:|---:|
| A1 TV0h | 105.41 / 66.41 | 114.43 / 75.42 | 206.43 | 206.43 |
| A1 Tf08 | 773.41 / 655.41 | 873.42 / 702.42 | 723.43 | 728.41 |
| B TV0h | 104.64 / 64.64 | 113.65 / 73.65 | 200.65 | 200.65 |
| B Tf08 | 881.64 / 754.64 | 937.65 / 798.65 | 577.65 | 877.65 |
| A2 TV0h | 106.54 / 66.53 | 115.55 / 75.55 | 202.55 | 202.55 |
| A2 Tf08 | 881.54 / 702.54 | 971.55 / 791.55 | 716.55 | 862.54 |
| step-D first TV0h | 105.16 / 66.16 | 114.16 / 75.16 | 205.16 | 205.16 |
| step-D first Tf08 | 930.16 / 668.16 | 1049.16 / 728.16 | 721.16 | 753.16 |
| step-D retry TV0h | 102.20 / 67.20 | 120.21 / 76.21 | 208.21 | 208.21 |
| step-D retry Tf08 | 873.20 / 759.20 | 932.21 / 801.21 | 693.21 | 815.21 |

Reversing the existing pair, **Tf08 fast / TV0h slow**, while preserving
the 1 C fast band and the common step-D reference gives G0 releases
835.42, 827.66, 810.54, 1,055.16 and 932.21 s, respectively (either slow
band). Moving the slope test to TV0h does not eliminate the Tf08 wait;
its tightened fast-slot band decides. There are no D journals for TV0m,
TV0s or TV1s here. TV0h-only diagnostics cannot substitute for those
unobserved candidate gates.

To check the single-exponential assumption, fit `log(T-B)=a+b*t`,
`tau_fit=-1/b`, where B is that member's own pre-warmup median. Intervals below
are fixed relative to G0 entry, using valid bracketed readings with >=.9
coverage and no gaps over 2 s; no baseline/asymptote is fitted. These are
**warmup-cooldown fits, not WP14(a) class tau**:

| member | TV0h tau fit: 0–60 / 60–300 / 300–600 s | Tf08 tau fit: same intervals |
|---|---|---|
| A1 | 18.2 / 214.4 / 341.7 | 53.1 / 263.2 / 328.9 |
| B | 18.1 / 213.5 / 384.8 | 52.5 / 266.7 / 411.8 |
| A2 | 18.1 / 211.8 / 372.0 | 52.8 / 254.3 / 362.3 |
| step-D first | 18.1 / 210.8 / 321.1 | 51.7 / 263.0 / 343.3 |
| step-D retry | 17.9 / 214.6 / 362.6 | 52.6 / 266.9 / 382.5 |

All entries are seconds. Log-fit R² ranges .952–.988 for TV0h and .966–.998 for
Tf08. High within-interval R² does not validate one tau for the whole cooldown:
the fitted constants change several-fold across intervals. At 600 s, Tf08 is
still about 1.88–2.41 C above its own pre-warmup median, while TV0h is about .17–.23 C
above its own. This establishes different observed responses, not anatomical
identification of the sensors or proof of independent thermal masses.

### Duty and cap consequences before choosing an option

The bar is no X7, at least three admitted turns, and
`G0 + sum(G1) + sum(H) <= .40*T_eff`
(`align_r1_rehearsal.py:82–89, :768–800`). `T_eff` is the lesser of the armed
deadman and L1, not the step member's re-armed post-G0 allowance (`:1512–1535`).
From `align_v4_kit.py:1080–1084`, for any nonnegative I_D:

`T_eff <= 1750/1.13544 = 1541.25 s`, so **all gate/hold time <=616.50 s**, even
before subtracting the actual member intercept or tail constraint. This uses
code constants only, no observed turn duration.

Every D warmup-cooldown G0 in the common-reference table already exceeds
616.50 s. A representative
877.65 s G0 alone would need `T_eff >=877.65/.4=2194.13 s`, exceeding that upper
bound. The new warmer R_D and native D schedule may change the waits, so this
is **a conditional impossibility if these waits recur**, not a measured duty
failure of a future window. It is a reason to withhold feasibility claims.

For comparison, E1's V-family diagnostics at 1 C leave at most 186.68 s
(TV0m), or **minus** 55.33 s (TV0s), for every G1/H combined, even under this
optimistic 616.50 s bound. At 1.5 C they leave 273.67 and 138.66 s. The
single-TV0h diagnostic leaves 433.65 s. None proves three turns fit.

`w1_g0_cap` (`align_r1_rehearsal.py:1411–1444`) uses the three actual gated D
runs and X-G, not these legs, planning turns, or hypothetical gates:
`clamp(ceil(1.25*max(wait)),600,1200)`, with censored inputs conservatively
charged 1,200. If the 877.65 s proxy maximum recurred in those runs, the cap
would be 1,098 s; at 1 C, `ceil(1.25*1055.16)=1319`, clamped to 1,200. A
429.82 s candidate proxy would still produce the 600 s floor, whereas
671.83 s would suggest 840 s. These are illustrations, **not earned W1 slots**.
A large cap neither consumes time automatically nor relaxes the 40% bar.

## The three prospective options

| option | G0 | G1/H and duty | band and cap | meaning of W1 thermal control | policy data alone? |
|---|---|---|---|---|---|
| **1. Unchanged classifier; fast-family slow winner** | both selected V keys gate; the slow slot's slope can still require hundreds of seconds | same two keys, five samples, 300 s cap; new W1-schedule duty required | new slow key starts at max(1,3 SD), not Tf08's S6 receipt; derive cap anew | two response rates within the fast family; no demonstrated control of Tf08's long tail | gates: **yes**, after valid classification and approval; third-key recording: **no** |
| **2. Amend slow return ceiling; keep dual gates** | fast plus classifier-selected slower key; Tf08-like waits of 716–878 s are plausible on these traces | return ceiling no longer certifies the 300 s per-turn recovery; keep actual duty/fallback bar; current waits would exhaust it | retain Tf08's 1.5 C receipt only if Tf08 wins; another winner starts at default; cap <=1,200 | both a rapid response and the observed long tail bounded at gate boundaries; no guarantee of continuous isothermality | classifier/RULE amendment: **no**; resulting gate behavior/bands/caps: **yes**, unchanged gate module |
| **3A. Fast-family pair gates; long-tail key recorded** | exactly option 1's gates | duty is on the actual fast-family pair; record-only temperature cannot veto/admit a member after the fact | pair's own bands and re-derived cap; no gate band/cap for the recorded key | proximal thermal control with long-tail observation; deeper state remains potentially variable | pair gates: **yes**; extra recording: **no** in current policy |
| **3B. Long-tail dual gate; fast-family candidate recorded** | exactly option 2's TV0h + amended slow pair | same long-wait and duty risk as option 2 | same as option 2 | dual-timescale control, with an additional proximal response on record | gate behavior: **yes**; selection amendment and third record key: **no** |

The literal single-gating-key versions of option 3 are **not expressible** by
the current policy either. Both keys participate in every gate's band/validity
checks; moving Tf08 to the fast slot only removes its slope check and applies
the fast band's tighter threshold to it. It is not record-only. Per-kind
“Tf08 only at G0, V key at G1/H” also needs gate logic and is outside condition
13. Setting `per_turn=False` or `heavy=False` would remove required controls
and is not an equivalent implementation of any option here.

For 3A/3B a builder could propose an additional bound collector outside
`thermal_gates.py`, with prospective policy/schema support, independent
readability flags, source digests and native sampling checks. That is a
**further approval/design requirement**, not an available policy knob or work
done by this seat. RL-74's policy-data-only preference is not silently waived.
If it cannot be done within the lead's interpretation, disclose unavailable
extra recording and return for a ruling; do not pretend a third key was saved.

For every option, the follow-up and W1 must execute identical
`thermal_gates.py` bytes under RL-61 condition 13. There is **no gate-module
edit** in this branch. Option 2 changes classification before signing, outside
the gate module. Every changed executed source, manifest/digest and kit check
still requires the lead's cold review and affected smoke repeat under RL-72.

### Proposed option-2 selection test, fixed before looking at D

Keep all D1–D6 quality checks, model-free baselines/crossings, fast eligibility
and fast ranking unchanged. For **slow only**, replace `t1<=300` with
`t1<=1200`, retaining `60<tau<=300`, noise <=.15 C and the resolving-rise
tests. Preserve the longest-t1 ranking and lexical tie. Fix 1,200 as a
pre-signature constant; do not substitute the subsequently estimated W1 cap,
which would make selection depend on a slot derived from the selected gate.
Continue printing the original 300 s pass/fail beside the amended verdict.

This avoids selecting a band after seeing which value admits Tf08. It also
leaves the legacy fast D4/D1(d) reference pool unchanged. A changed slow winner
may be another key, not Tf08; no manual fallback to Tf08 is allowed. Under
RL-75, if the winner is still R0-fast, or the quality/sensitivity table is
unstable, bring it to Fable. The “separate response” interpretation has not
been met just by relaxing a ceiling.

Before freeze, repeat the classification on the night's native D under the
adopted series mode, match the smoke-approved keys or apply the registered
pick-change procedure, recompute S6/S7 for the actual picks, and earn the duty
and cap receipts on those keys. S7's quiet-baseline rule for changed picks
(`align_r1_rehearsal.py:845–851`) does not replace the pre-warmup G0 reference.

## What smoke Part B must place before Fable

Part B runs only later, natively, in a clean agent-free session under the
lead's authority. This seat runs no smoke. The D classification table must
show, for **all candidates**, not just a selected row:

1. Key, temperature unit/quantum, R0 class and eligibility, alias group; D mode
   and the classification/source digests. Confirm TV0h/TV1h count once and
   test the D record's aliases rather than assume E1's groups persist.
2. Each phase's one-second coverage, read-error fraction and longest empty
   run: >=.99, <.01, and at most one. The sampler fix must pass those bars;
   invalid coverage cannot be waived to produce the authoritative picks.
3. Baseline/noise/floor, rise, positive rise60, jump, tau, t1, original class
   and rejection reason; heat-order reference, censoring/clamp flags and
   exclusions. Print distance to 60 s and to the return ceiling, not just a
   rounded “60”. Preserve the classification digest and full thermal record.
4. Unchanged-rule picks plus diagnostics with/without the pre-specified
   borderline-read treatment (bracket/coverage rules remain authoritative).
   Stable non-null picks require the same key/alias representative, class and
   valid heat-order reference in both views. Gaps that make a crossing
   unresolvable mean inconclusive, not permission to interpolate a winner.
5. For option 2, the parallel, explicitly labelled amended D5 table with
   `t1<=1200`, original 300 s verdict retained, and the deterministic winning
   slow key. For any proposed band-based alternative, print the actual band
   and `tau*ln(rise/band)` too; do not assume 1.5 C suffices.
6. Per selected key and proposed record key, the valid own pre-warmup capture
   and its coverage; G0 replay at default and prospective tuned band against
   both its own capture and the accepted R_D, with first-band, dwell,
   slope-only and joint times, margins and censor limits. Unlike E1, the
   authoritative native test may not waive a .797 capture. Part A's capture
   and status checks and <=1,200 s release remain required.

**Decision tree:** an unchanged stable non-R0-fast slow winner allows the
remaining RL-74(2) process, not an automatic signature. A stable R0-fast
winner supports option 1/3A only after Fable explicitly accepts its narrower
meaning and resolves extra recording. A stable amended, non-fast-response
winner supports testing option 2/3B, conditional on the full duty rehearsal.
Nulls, borderline switches, aliases or unresolved crossings hold the arm.
If no sufficiently observed qualifying slow candidate exists, this round
does not invent one.

Part B alone cannot choose on duty: it is a single D step, not three admitted
turns with holds following a D predecessor. The follow-up's three gated D
runs and X-G, using the approved keys and reference, must show the actual
G0/G1/H wait ledger, medians (G1 and H each <=90 s if tuning is invoked), the
unchanged 40%/three-turn/no-X7 bar, L1 fit and G0-cap receipt. Follow the
ordered fallbacks (S6 through 2 C, D-predecessor idle 300 to 450 s, same-rung
4-bit, screen-only/return to council), not a longer unregistered turn cap.

## Draft prospective deviation rows for the lead

These are proposed text, **not adopted deviations or edits to closed texts**.
Use the applicable row; do not conflate these alternatives.

**SS-1 / WP14(a), unchanged classifier with R0-fast slow pick:**
“Before signature and before any v4 window, on temperature-only R1 evidence,
the lead approves the native smoke-D classifier's stable [fast, slow] picks
for the follow-up and W1, although [slow] was R0-fast. The model-free
classifier and its 300 s return test are unchanged. The two roles describe
different response rates in the fast family, not independently established
die/heatsink masses or control of Tf08's long tail. Aliases cannot fill both
roles. S6 starts at the new key's registered default; S6/S7, duty and cap
receipts are earned on these picks. The night's adopted-mode D selection
must reproduce them or invoke the registered pick-change procedure.”

**SS-2 / WP14(a), recommended amended slow return ceiling:**
“Before signature and before any v4 window, the slow D5 return-time ceiling
is prospectively changed from tau*ln(rise/1 C)<=300 s to <=1200 s, the fixed
R1/G0 observation ceiling. The fast D4 rule, slow 60<tau<=300 s and noise
limit, all other quality/heat-order/clamp/alias checks, longest-return ranking
and lexical ties remain unchanged. The unchanged-rule result is retained
beside the amended table and both rules/digests are pinned. The slow test
certifies start-gate recovery plausibility only; it no longer asserts 300 s
per-turn recovery. Actual G1/H retain their 300 s caps, and the W1-schedule
duty, S6/S7 and G0-cap bars remain independent prerequisites. A null, aliased,
unstable or R0-fast slow winner is referred to the research lead, never
manually replaced. Selection occurs in native smoke D before the follow-up,
is reproduced under the night's adopted mode, and is frozen before signing.”

**SS-3A / WP14(a), gating versus record-only roles (if authorized):**
“Before signature and before any v4 window, [V_fast,V_slow] are the only
gating temperature keys and [lag_key] is recorded for every member, including
its idle capture and release state, as a non-gating lag indicator. Its values
are not used to select, exclude, retry or retune a member after outcomes.
W1's thermal-control interpretation is restricted to the gating pair. The
recording mechanism, policy/source digests, sampling/error accounting and
disclosure-only handling of missing lag observations are approved before
smoke. Alias exclusion applies to the gating pair. S6/S7, duty and cap
receipts use that pair. The current policy has no extra-record key field;
this row is not implemented by relabelling a gate slot.”

For 3B replace the first sentence with the option-2 dual-gating pair and the
fast-family record-only key; retain SS-2's classifier amendment. A literal
single-key or different-pair-by-gate-kind design is a separate logic change
and is not represented by these rows or approved under condition 13.

## Changes, checks, limitations and exact handoff

Copied the adopted replay, its manifest and tests onto this branch. Extended
only the desk script with opt-in `--slow-role-diagnostics` and synthetic
regressions. It retains the temperature/status allow-list, requires the
legacy self-check before reporting new diagnostics, and censors all new
counterfactuals at recorded G0 end. New fixed-baseline fits refuse incomplete,
gappy, nonpositive-excess or noncooling intervals. Per-key virtual duplication
is labelled non-selectable. No classifier, gate, runtime, kit, config or
coordination state was changed.

Verification (targeted only; no full suite):

- Baseline adopted module: `python3.13 -B -m unittest
  tests.test_align_r1_thermal_replay` — 19 tests, PASS, 13.369 s.
- Extended module, same command — **24 tests, PASS, 20.819 s** (an intermediate
  23-test run also passed). Total targeted-test runtime stayed below a minute.
- `compile(source, filename, "exec")` on the two changed Python files — PASS;
  no `.pyc` output. No broad compile or discovery over data paths was used.
- A separate stdlib harness loaded the adopted script directly from its Git
  blob and this script on the same synthetic desk fixture. Default serialized
  JSON and rendered text were **byte-identical** (SHA-256 `f319e6ed…60479`
  and `079c7481…5e24`). This is a synthetic default-output check, not a claim
  that two production measurement bundles were generated.
- `--scenarios` on the sanctioned copies — all 13 manifest journal hashes
  checked; all recorded G0 outcomes reproduced; exact R_op recomputation;
  released-time differences under 2 s; no self-check failures. The resulting
  JSON SHA-256 is `0ed56cbaa8c76c7ea1d5c5fece332d520a2888119d72bc3962500a1de19392bf`.
- After that self-check, the new `slow_role_diagnostics` desk function on those
  same hash-checked control/D journals produced **24 per-key rows and 48 role
  replays**. Only recorded G0 prefixes enter its calculations. The report
  tables above were taken from those outputs, not fitted by hand.
- W1 `thermal_gates.py` compares byte-for-byte to the base Git blob, SHA-256
  `c72937bd8bf7b5553c1ffd70e76018ffbf25f32578533c8749aa88419837918d`.
  The copied manifest also equals the adopted branch's bytes exactly.
- The E1 heading list was re-read near close: the appended candidate-key G0
  section at line 153 is present and used above; no additional appended
  section was found.

The baseline command actually run was:

```sh
python3.13 -B scripts/align_r1_thermal_replay.py \
  --manifest docs/run_reports/2026-11-11-r1-thermal-replay.manifest.json \
  --root /private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/41120c85-9f5f-48c9-aa4d-c3d83d4df41c/scratchpad/r1-journals \
  --scenarios --json /private/tmp/slow-sensor-sol-baseline.json
```

The new diagnostics were then called against that checked report with
`slow_role_diagnostics(report, journals, members)`, where journals came only
from `read_journal(path, manifest_sha256)` and members were the control and
five D members. For a fresh combined reproduction, add
`--slow-role-diagnostics` to the command above and choose a new `--json`
destination; inspect its `slow_roles` field. The combined reproduction is a
recipe, not an additional run claimed here. No thermal output is added to
normal stdout, and the legacy default result remains unchanged.

Unknown: native D's valid classification and full inventory; the actual
follow-up R_D; new-pick soak SD; D-after-D G1/H and duty; whether a distinctly
lagged amended winner exists; policy-only extra recording (unsupported in
the inspected code). The journals cannot determine power-mode adoption or
yield W1 settings. E1's 30B comparison cannot establish D's winner, and the
warmup fits cannot substitute for classifier crossings. No MLX/native tests
were run; the lead must run the approved smoke A/B and subsequent rehearsal
outside this sandbox, on an agent-free machine. All empirical gate/cap/duty
statements retain their diagnostic or conditional labels.

The next exact step is for the lead to rule on this seat's exposure and the
prospective option/return test, then bring the fixed-sampler native smoke D
table to Fable before any night is armed. State/kernel bookkeeping, review,
signing and arm decisions remain lead-owned. Local commits only; no push.

## Open questions for the research lead

- Is this seat's disclosed audit-prose exposure acceptable for this thermal
  design round, or is a fresh seat needed before adopting its recommendation?
- Should the slow role preserve long-tail control (SS-2, with real risk of
  screen-only fallback), or explicitly become an observed non-gating lag
  variable alongside a fast-family gating pair (SS-1 + SS-3A)?
- If SS-2 is adopted, is the fixed 1,200 s slow-only return ceiling accepted,
  with the original 300 s verdict printed and G1/H/duty unchanged?
- If option 3 is chosen, may the builder add a separately bound record-only
  collection path outside the gate module before smoke, or must the present
  policy-data-only limit hold and the missing third key return for a ruling?
- If native waits repeat the >616.50 s G0 proxy, confirm that the existing
  duty/fallback process controls the decision; a longer classifier ceiling or
  gate cap alone does not make W1 admissible.
