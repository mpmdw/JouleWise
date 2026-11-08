# R12 adversarial review — Sol2

Seat: `perf/2026-11-08-r12-review-sol2`. Review of main
`3809bdd14da5882659f17dc292200d4afbbd1579`, especially `RUN_STATE.md:1045`
(item 214). **Recommendation: KEEP B1; CHANGE the R1 bound, B2 and B3 before
W1 registration.** The cadence proposal is useful, but count-only stopping
does not establish the exchangeability required by R14. This report supplies
advice, not a new ruling or registration.

## Evidence and scope

All sources are local repository text or Git blobs. No network, weights,
measurement data, real restricted directory, measurement process or external
user directory was accessed. Absolute data paths in source were text only.
Pilot timings quoted below are other seats' repository summaries, not fresh
measurements. No native MLX or hardware claim is made.

References use `key:path:line`; recover absent files with
`git show <commit>:<path>`. Line numbers refer to the pinned blob, not an
installed measurement checkout.

| Key | Commit | Source |
|---|---|---|
| H | `3809bdd14` | This clone's main snapshot; `RUN_STATE.md` and current shared runner |
| K | `d600baba029f70592bb8e792098338e4cd6811d3` | `origin/lane/2026-11-07-w1-kit-r10`, v4 kit/runtime/protocol |
| R | `e901eb2a480d51377a494be9d797733dfcd0220b` | R1 integration snapshot cited by the synthesis |
| S | `55029b860adc775fc2ef10a8f9aff19f30af05d2` | `docs/perf/2026-11-08-latency-synthesis.md` |
| L1 | `d9f443db67794a74b4e51c0535d2e1fd51f995ad` | `docs/perf/LATENCY-AUDIT-sol1.md` |
| L2 | `80ba796621ca369126f6a92b9b5f7034c9c65a1c` | `docs/perf/LATENCY-AUDIT-sol2.md` |
| W1 | `05aec5b13856f73e04d532fc25b5f79e79076517` | `docs/perf/WINDOW-EFFICIENCY-sol1.md` |
| W2 | `8dc931d1813714c134df6add4716e28c5bdb9d57` | `docs/perf/WINDOW-EFFICIENCY-sol2.md` |
| AF | `4526de7d587a412073cf792c959090401e8d4797` | `docs/align/squeeze/AGREEMENT-FINAL.md`, adopted by item 212 |

M0 intake found no active stop card. The explicit review brief selects this
docs-only work over the historical queue. Coordination state is unchanged,
as instructed. `CANONICAL.md:36` explicitly places the integrated R1 runner
off main; absence from the working tree is not evidence that it does not
exist. `/usr/bin/grep` found no `wait_outside_os_batch` under working-tree
`scripts/` or `joulewise/`; it found the definition and caller in temporary
copies of K's corresponding directories.

## Verdicts

| Item | Verdict | Severity | Reason |
|---|---|---|---|
| R1 printed bound | **CHANGE**; keep the synthesis's bug finding | **HIGH** | A single step-D admission can wait almost 11,164 s. Manual plan-sizing instructions consume the stale 61,607 s figure, and the shared runner enforces the resulting plan deadline. |
| B1 terminal-completion windows | **KEEP**, with qualified forecasts | **LOW** | The span/ceiling arithmetic is correct. Existing runner/chain code already returns on completion; no compulsory sleep to the ceiling was found in those paths. |
| B2 triage-only arm gate | **CHANGE** | **HIGH** | Moving the desk is sound. Removing every desk-derived next-arm prerequisite conflicts with the existing escalation/pool rules unless explicitly superseded. Final eligibility cannot simply be assumed available in five minutes. |
| B3 count stop, minimum 6/cap 8 | **CHANGE** | **HIGH** | It can remain blinded, but needs a prospective ordered rule, final eligibility and a defensible score/selection law. It does not settle R13's fit/calibration/test allocation or R14's dependence problem. |
| B3 completion/savings arithmetic | **CHANGE** | **MED** | 6.87 expected windows is benign-only. Adding the illustrative six-sabotage target gives 7.247 and a 7.47% shortfall at cap under the same iid assumptions. |
| Unadopted B4/B5 | **KEEP** R12's decision to defer | **LOW** | No new equivalence evidence. B4's stated saving also counts four anchors that its own text leaves unchanged. |

## 1. R1: verified scheduler defect and a real deadline dependency

`K:scripts/align_r1_rehearsal.py:980` computes the predicted segment finish
and waits to the blackout's **end** whenever `t < end` and
`t + expected_s > start`. `_segment` calls it before invoking each quiet
attempt (`:1064–1082`). Thus the admission wait includes the interval before
11:45 during which the segment cannot safely finish, as well as the
11:45–13:15 blackout. The same relevant code is present at R; K's later
changes to this file concern X-G evidence, not scheduling or this table.

For the default step-D bound, from `segment_bounds` (`:138–156`):

```text
rearmed member = 1750 + 1.13544*1580 + 120 = 3663.9952 s
step D        = member + 1200 + 300 + 600 = 5763.9952 s
one wait      < step D + 5400             = 11163.9952 s
```

This is a supremum under an ideal advancing clock/sleep; exact finish at
11:45 is admitted because the comparison is strict. A fake-clock execution
of the actual two scheduler functions gave **9,900 s at 10:30**. Starting
at 10:08:56.004801 gave **11,163.995199 s**. No real sleep or runtime import
was involved.

The helper nevertheless assigns only the blackout width to
`batch_window_wait_max_s` (`K:scripts/align_r1_rehearsal.py:1314–1354`):

```text
phase-table sum                         56206.9616 s
old sum + 5400                          61606.9616 s
sum + one step-D admission-wait limit   67370.9568 s  -> ceil 67371 (18.714 h)
```

**67,371 s is the corrected one-encounter, no-redo phase-table allowance,
not a complete end-to-end bound.** Brackets/harvest are explicitly omitted
by the helper; R6-2 retries add 29,055.9808 s, contention redos are extra,
and a longer execution may encounter another daily blackout. The existing
unresolved four-member idle accounting caveat is another possible 1,200 s
(`K:docs/align/r1_runtime_contract.md:95`; W2 §2.4). None is fixed merely by
replacing one printed number.

The dependency question has two different answers:

* **No direct production caller of the helper was found** in K's `scripts/`
  and `joulewise/`; the R1 CLI has no overall deadline argument
  (`K:scripts/align_r1_rehearsal.py:1920`). Its shell wrapper also supplies
  none (`K:scripts/night_chains/align_r1_rehearsal.zsh:49–53`). Tests reproduce
  the stale totals (`K:tests/align/test_r1_round7_science.py:132–143`), so
  green arithmetic tests would not establish a valid scheduler bound.
* **Manual scheduling and an enforced deadline do depend on it.**
  `H:RUN_STATE.md:1222` tells the operator to set R1 `window_max_s` from
  56,207/61,607/90,663; `:1265` repeats this. The runtime contract above
  explicitly says the R1 plan is sized from the table. The shared runner
  derives its termination instant from `t0 + window_max_s + 300 s`
  (`H:scripts/run_night.py:85,1093`; also
  `K:scripts/run_night.py:1157`). The 300 s shutdown grace does not cover
  the missing 5,763.9952 s. The shared completion/dead-man scheduling also
  derives from this field (`H:scripts/run_night.py:2105–2113,2212–2213`).

**Required lead action:** correct the sizing guidance/helper/tests and
audit the actual R1 launch packet's `window_max_s`, enclosing deadlines and
cut policy before relying on them. This review did not inspect an installed
plan or any live job and cannot certify its current limit. Do not substitute
67,371 s as an unconditional guarantee or change R1's avoidance rule as a
side effect of fixing the accounting. Keep R1 versus W1/D scheduling
policies separate until the owner rules their intended behavior.

## 2. B1: correct arithmetic, conditional calendar

The default D roster is exactly **4 anchors + 2 sentinels + 14 fresh benign
+ 2 fresh sabotage = 22**, hence **18 D members and 16 fresh**
(`K:docs/align/pilot_protocol_v4.md:139–145`). Anchors, repeated sentinels
and W1 selection members do not add to m. Seven fresh benign/pair/window
is only available if none of those slots is reassigned to fitting.

```text
D span  = ceil(3131.27 + 18*1800 + 4995)                 = 40527 s
D max   = 60*ceil((40527 + 3300 + 7200 + 7200)/60)       = 58260 s
Q4 permitted ceiling                                   = 59520 s
W1 span = ceil(3131.27 + 4*1150 + 4*850 + 6*1800 + 4995) = 26927 s
W1 max                                                  = 44640 s
```

These agree with K's protocol (`:671–678`), kit `SCAFFOLD_S`/planning preview
(`scripts/align_v4_kit.py:56–58,1487–1488`), and validator's formula
(`scripts/validate_align_v4_w1_plan.py:208–230`). K's
`joulewise/b5/plan.py:59–67,922` supplies the allowances. The 59,520 minus
40,527 difference is **18,993 s**, including minute rounding and **1,260 s
above the calculated maximum**, not solely the three named allowances.

At 30/45 min turnaround the D cycles are 11.7575/12.0075 h, yielding
2.0413/1.9988 windows, 44.9075/43.9725 total members and 32.6600/31.9800
fresh members/day. S's rounded figures are right **under those premises**.

The shared runner polls until the child ends, cancels its deadline watchdog
and proceeds immediately (`H:scripts/run_night.py:1168,1313–1319`; equivalent
K lines `1234,1379–1385`). The generated HAZARD_PACK chain ends with
`chain_end` and exit (`K:joulewise/b5/chain.py:1228`). This resolves S §5 D10
for these inspected paths: no deliberate wait to the ceiling. It does not
prove every installed wrapper, successful window or physical turnaround
will match the planning span.

Retain every planned stage, reference/bracket, terminal process cleanup,
custody requirement and quiet-start predicate; “terminal completion” must
not mean stopping when the last scored member finishes. A terminal failed
chain does not become valid because it ended early. Faster cadence also
changes the distribution of wall-clock starts: it is no independent proof
that window states or scores are exchangeable.

S §3's **143.2–146.2 h** bill for R1+W1+7C+3T still uses the old R1 wait.
Replacing only that allowance gives **144.7689–147.7689 h**, before the
explicitly unbudgeted R1 costs, failures, blackout policy for D, additional
fit support, or the unresolved test roster. The roughly six-day bill remains
a conditional scenario, not registration-grade capacity evidence.

## 3. B2: preserve arm prerequisites and distinguish final from provisional counts

**Keep the off-MBP desk placement.** The 98–103 min historical desk summaries
are supported by L1 row M23; they do not measure today's v4 desk or the
proposed five-minute triage. L2 F1 explicitly says never to arm across an
unresolved gate that depends on the desk (`L2:docs/perf/LATENCY-AUDIT-sol2.md:170`).
S table 1 row 2's characterization as “implied by all” is stronger than the
seats' support for removing those gates.

“Power-mode restored” also needs the intended state named: W1/D arm checks
verify the **frozen series mode**, which may be adopted High Power; stale R1
markers trigger an Automatic restore first
(`K:scripts/align_v4_session.py:161–176`). A generic Automatic-only triage
would not implement that contract.

The protocol requires **U1–U3 failure to block held-out pool entry and an
escalation before the next window**, and U4/U5 inconclusive can change the
remaining sentinel roster (`K:docs/align/pilot_protocol_v4.md:479–495`).
These include token identity, coverage, exclusions and energy-based checks,
not just meter presence. AF A03/A06 retain the exact-candidate/eligibility
obligations. The W1 and changed-code desk exceptions in R12 are necessary
but do not specify how these later-window prerequisites are satisfied.

**Change B2's wording:** name which checks must finish before the next arm,
even when computed on the laptop; defer report preparation and genuinely
non-gating analysis. If R12 intentionally supersedes the before-next-window
rule, register the exact supersession, treatment of an already-running
window, cohort separation after a policy change, and unavailable-member
accounting. “Accepted risk of one wasted window” is not enough to establish
these semantics, and an unbounded desk backlog could affect more than one
window. No hashing, exporting or magistrate activity moves into the next
measurement window on the MBP (L2 §Overlap).

For B3, a triage count must be labelled **provisional** until all registered
eligibility checks finish. Freeze a decision boundary/snapshot and an
in-flight-window policy. A window already launched as calibration cannot
silently become test, or be discarded after convenient counts arrive. All
its eligible calibration members count if the prospective rule includes it.
The eight-window cap must count attempted windows, including failures and
in-flight ones, rather than authorize eight successful windows plus retries.

## 4. B3: count-only can preserve blinding without guaranteeing calibration validity

### What is valid, and what is still missing

Under the illustrative seven-benign/pair roster, six windows supply 42/pair;
one whole-window loss leaves **35**, below 39. Seven supply 49, or 42 after
one loss; eight supply 56, or 49 after one loss and
`floor(.8*49)=39` under W1's additional 20% attrition premise. Those margins
are correct, conditional on the specified losses and no fit-slot deduction.

Counts alone can be a permitted blinded information view. **Correlation
between eligibility and score does not automatically invalidate an inverse
count design:** with iid trajectory-level `(eligibility, score)`, identical
predeclared eligibility for C and test, and a fixed common scoring law,
accepted scores can remain iid from the eligible population. That yields a
claim about eligible trajectories, not all assigned attempts.

Those premises are not established by R12. Whole-window failures, thermal
carryover and session fits couple eligibility and score across trajectories.
U3 itself uses energy differences. Selecting/ending windows by those counts
or statuses can change the represented state mixture despite hiding alarms.
AF R13/R14 explicitly retain these problems
(`AF:docs/align/squeeze/AGREEMENT-FINAL.md:49–50,124`; W2 §5 scientific
conditions). More available trajectories do not create more independent
windows. Report all assigned attempts and unavailable outcomes as well as
the valid-only analysis; exclusion is not detection (AF V06).

### Exact synthetic counterexample to “counts alone suffice”

This is a mathematical example, **not a claim about actual v4 scores**.
Windows are iid. With probability .9 a window supplies seven eligible
benign/pair, each with score 0; otherwise it supplies three eligible/pair,
each with score 1. Both pairs share the state. A future test window has the
same law and eligibility; its first eligible trajectory is the prespecified
test unit. All scores within a window share its state. The example concerns
that future-window test unit, not a uniformly sampled row from a pooled
collection of future windows.

Apply the proposed minimum-6/cap-8, both-pairs m≥39 rule and
`k=ceil(.95*(m+1))`, strict `score > calibration[k]`:

* Six score-0 windows meet the target (m=42, k=41); threshold=0.
* Any successful calibration containing a score-1 window has at least
  three scores of 1, so its threshold=1 at these possible m values.
* Therefore the probability of successful calibration **and** a false
  alarm on a future eligible test trajectory is
  `.9**6 * .1 = .0531441`, already **above .05**. Exact enumeration gives
  success probability .99956835 and FPR conditional on success .05316705.
  Fixed eight-window collection in this same example gives .04306531
  conditional on success. Fixed eight is not a general cure for clustering;
  here it exposes the effect of the stopping choice.

Thus even iid **windows**, matching eligibility and fully hidden scores
are insufficient for a trajectory-level exchangeable-rank guarantee.
Count stopping can matter when window yield reveals its score distribution.

### Required prospective specification

Before W1 registration, freeze:

1. The ordered window/seed/role list, both-pair targets, minimum and total
   attempt cap. Decide explicitly whether ≥6 sabotage/pair is a stop target;
   it is not implicit in Q6. No reordering toward high-yield states, optional
   repeat windows, “best 39,” or post-count fit/calibration/test reassignment.
2. The final eligibility/exclusion and whole-window-failure rules, who sees
   which fields, the asynchronous decision boundary, and treatment of
   pending counts/in-flight windows. Include all eligible members selected
   by the rule, not a convenient subset. At cap, unresolved/insufficient
   calibration, with no unregistered ninth attempt.
3. Fit/calibration/test roles and a common defensible score law; condition
   the statistical claim on its actual unit of exchangeability. Freeze
   window-state scheduling/holdout treatment and account for cluster and
   informative-missingness sensitivity. A synthetic null audit can expose
   failures; neither fresh seeds nor a non-significant drift check proves
   transport to a live future window.
4. Actual rank, alpha, strictness/ties and the claim to print. At m=39,
   rank 38 supports ≤5% and the maximum supports ≤2.5% **only with valid
   exchangeable scores**. Stopping at a random m does not waive that
   condition or repair per-session LOTO-benign/full-fit-sabotage asymmetry.

If those conditions cannot be justified, use a prospectively fixed collection
plan and restrict the inference to what its score/dependence analysis supports;
do not retain a distribution-free claim merely because the count target passes.

### Probability and roster omissions in the synthesis

For S's **assumed**, unmeasured 10% independent member exclusion, let
`b_n=P(Bin(7n,.9)≥39)` and `s_n=P(Bin(n,.9)≥6)`. Joint completion for
both pairs is `b_n²` benign-only or `(b_n*s_n)²` with sabotage. Recomputed:

| Target | By 6 windows | By 7 | By 8 | Expected attempts, cap 8 | Insufficient at cap |
|---|---:|---:|---:|---:|---:|
| Benign only | .147184 | .984054 | .999990 | 6.868762 | .00000991 |
| Benign + ≥6 sabotage/pair | .041569 | .711490 | .925258 | 7.246940 | .074742 |

`E[N]=8-P(complete by 6)-P(complete by 7)`, including cap failures. The
approximately 13.30 h saving relative to fixed eight (30 min turnaround)
is benign-only; with sabotage it is **8.85 h**, under these assumptions.
The probabilities in S are right; using 6.87 as an undifferentiated B3
benefit mixes targets. Neither table models whole-window loss or correlated
attrition. S §5 D3's suggestion to settle the rule from the first two
calibration windows must instead be frozen before collection, or governed
by a fully prospective adaptation rule.

More seriously, **R13 is not settled by “cap 8.”** W2 explicitly budgets a
sensitivity in which two benign slots/pair/window are spent on independent
fit support: then only five count toward m; eight windows give 40/pair and
one loss leaves **35**, requiring nine for that loss margin
(`W2:docs/perf/WINDOW-EFFICIENCY-sol2.md:317–329`). S reduces the remaining
roster issue to three versus six *test* windows (§5 D4), omitting this
potential **calibration** capacity conflict. W1's six-support-member test
proposal likewise says matched cardinality does not prove exchangeability
(`W1:docs/perf/WINDOW-EFFICIENCY-sol1.md:389–416`). Resolve the scorer and
full F/C/T bill together before calling the 6–8 plan sufficient. Neither
this seat nor R12's capacity arithmetic can choose those semantics for the
lead/statistics owner.

## 5. Other synthesis corrections and decisions to retain

* **B4 arithmetic — LOW, CHANGE if ever revisited.** S §3 says D idle is
  shortened while the four anchors stay at 300 s, but charges `22*180`.
  The correct saving is **18*180=3,240 s**; span becomes **37,287 s =
  10.3575 h**, before any offsetting G0 change. With the speculative 2,700 s
  B5 saving it would be 9.6075 h, not 9.41. R12 did not adopt either, so
  this does not change the present lean trajectory.
* **Decode wording — LOW, CHANGE.** S §0's 860.5 s is a full-budget debit
  for D at the protected floor plus last-turn allowance. It is not the
  compulsory duration of each of the 22 members: four are anchors, and
  episodes can finish early. W2 §2.2 explicitly makes this distinction.
  Keep the conclusion that no measured five-hour D window is established.
* **R1 budget consistency — MED, CHANGE.** S finds the batch error but
  continues to use 17.11 h in its series totals and D1. Propagate the
  one-encounter correction, retaining bracket/harvest/retry terms rather
  than hiding them in a rounded day estimate.
* **Source attribution — LOW, CHANGE.** S table 1 row 23 labels L2 a
  scheduler-code finding source. L2's inventory and probe actually repeat
  the 5,400 s allowance (`L2:docs/perf/LATENCY-AUDIT-sol2.md:81,152–157`).
  The demonstrated forward-overlap discrepancy is W2 §2.4's finding;
  S §5 D2 attributes that correctly.
* **KEEP** the separation of measured historical timings, planning costs
  and unqualified targets; same-output software work off the MBP; anchors
  and W1 contrasts; fixed cooler/setup policy; and deferral of resident/
  ungated v4-max, scaffold reuse and shorter idle. Neither software result
  equivalence nor unchanged token identity alone proves measurement
  equivalence after a thermal intervention. L1's rankings also warn that
  proposed savings overlap; do not add them into a bankable weekly total.

## Verification and handoff

`python3.13 -B /private/tmp/jw-r12-sol2-4x9tr2hf/check_r12.py` passed in
under one second. The stdlib-only script AST-isolates only
`_batch_windows`/`wait_outside_os_batch`, injects fake time, checks five
boundary/start cases and the long-wait counterexample, reproduces phase/span/
cycle arithmetic, computes exact binomial tails, and enumerates all 256
eight-window state tapes with rational probabilities for the stopping
counterexample. It imports no repository runtime, tests, MLX or data reader.
Its SHA-256 is
`34089b27fa9baaa92d30ababdb2ca89db394a5c0eda83467d204274e447a2020`.
`git diff --cached --check` passed as the document whitespace check. No full
suite or measurement pipeline was run; no production/test code changed.

Native tests required by **this docs-only change:** none. For a later
implementation, the lead must run focused scheduler/deadline regressions,
and validate actual R1/W1 terminal timing, final eligibility and native
gates outside this active sandbox in a lead-controlled quiet session.
Existing stale-total unit assertions need correction as part of that code
change. This report does not certify the installed plan, score law, empirical
attrition, or the proposed turnaround.

Next exact step: the lead compares both independent r12 seats, dispositions
the HIGH findings, audits the R1 launch deadlines, and freezes the reconciled
B2 gate contract plus ordered B3/F-C-T/rank rules before W1 registration.
The open questions are the sabotage target, valid scorer/fit-support bill,
pending-eligibility policy and actual launch-packet limits. No coordination
file was edited and no new authority was assumed.
