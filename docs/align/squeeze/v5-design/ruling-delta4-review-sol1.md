# v5 ruling revision 4 — delta review, Sol1

**Verdict: SIGN_WITH_CHANGES, for one material power-planning change.** All
R1–R4 findings from both prior seats are **Resolved at ruling level**. The
primary betting test is valid for its newly restricted conditional-mean null;
the H4 roster, capacity convention and revised ledger reproduce. The
remaining concern is substantive: the allowed betting family has very low
power for modest escape reductions at 20–28 dates, even in favorable synthetic
laws. Set the intended effect size and joint-power target and address sizing
early, rather than discovering this after substantial physical development.
This does not call for abandoning the native hybrid or reopening the repaired
validity objections. No actual G12 certification is claimed.

Seat **sol1**, branch `align/2026-11-08-v5design-ruling-delta4-sol1`.
Candidate **`52e976dc928c30bb73bcb722ea5cca9dc37bae2c`**. Reviewed the complete
`git diff b606d9788..HEAD`: only `RULING-DRAFT.md`, 96 additions / 44 deletions.
Section references below refer to that candidate. The ruling is unchanged.

Both complete delta3 reviews were read from existing local Git objects:

| Key | Ref suffix under `origin/align/2026-11-08-` | Object | File in this directory |
|---|---|---|---|
| E1 | `v5design-ruling-delta3-sol1` | `570ccd7131c9452746ca2d99a1cc4a3a630fde72` | `ruling-delta3-review-sol1.md` |
| E2 | `v5design-ruling-delta3-sol2` | `4e17eb873b85e1238a2733b5ced5cc6bf0a5e81d` | `ruling-delta3-review-sol2.md` |

Also checked the repository intake, AP contract, D-062 and orchestration
instructions. This is one independent seat; no companion verdict or final
authority decision was delegated. Novelty, venue eligibility/dates, actual
capability, host capacity and measurement outcomes remain unverified.

## 1. Both seats' R1–R4 dispositions

**Resolved** here means the requested binding specification is installed,
not that its future implementation or qualification passed. None of these
eight findings remains Partial or Not resolved as a ruling-level obligation.

| Prior finding | Status | Operative revision-4 quotation and assessment |
|---|---|---|
| **E1 R1:** betting null versus marginal effect null | **Resolved** | §4b registers “E[d_g \| 𝓕_{g−1}] ≤ 0 for every g” and explicitly says it is “not a test of the marginal average effect” under unrestricted dependence. The shared-shock example and descriptive-only Δ reporting close the null/claim mismatch. |
| **E1 R2:** size tolerance and switched test | **Resolved** | §4b: “The 1.2 × nominal certification is dropped”; “There is no data-dependent switch between procedures”; “Holm ... is applied to the four valid p-values.” Exact validity now comes from the capital argument, with simulation only a code regression check. |
| **E1 R3:** H4 date support and estimator | **Resolved** | §4a: “8 H4 attempts and 4 cover-only” with “at least one H4 attempt in every cell.” §4b defines d_g as “the equal average of the six pair × optimizer cell means.” The empty-date/cell counterexample is excluded. |
| **E1 R4:** CAP units and duplicate yield | **Resolved** | §5: “h_v4 = 24 × Σ_all windows ... ÷ elapsed calendar hours, in h/day”; “Yield is charged once.” Gross capacity is paired with the reserved bill, so accepted-window losses are no longer subtracted twice. |
| **E2 R1:** nominal family control | **Resolved** | §4b makes betting primary “for every H1-H4,” with “t test” under “Sensitivity only.” H4 degeneration “stays in the family with p_4 = 1.” The family remains four and no variance-dependent selection survives. |
| **E2 R2:** conditional theorem versus registered null | **Resolved** | §4b freezes “the date order and the filtration,” uses “0 ≤ λ_g ≤ 1,” and states “p_k = min(1, 1/K_G).” Its dependence claim is expressly conditional on the per-date conditional-mean null, not a theorem about arbitrary marginal-null dependence. |
| **E2 R3:** exact subset allocation and mixture | **Resolved** | §4a fixes the phased “{cover, external} → {cover, unrestricted} → {external, unrestricted}” cycle, two cells per phase, and seals window 28/per-cell totals. Equal cell/date weights are explicit; unequal raw counts do not silently change the estimand. |
| **E2 R4:** capacity accounting and observation span | **Resolved** | §5 includes “All windows ... accepted, rejected or redone,” measures a separately, retains the distinct 0.85 transfer margin and requires CAP-1b's “≥ 5 ... windows spanning ≥ 7 calendar days.” The same convention updates both bill and capacity. |

The smaller carried findings also close: §4d scores C at its “actual eligible
roster,” §5 adds 28 local C scores; §4c uses the exact rank-tail formula;
§4d explicitly allows “F-fitting ... before the G12 freeze” while C/test
scoring waits for T3. §9's round-4 dispositions accurately describe those
repairs. “Resolved” must continue to be distinguished from gates passed.

## 2. Validity of the primary betting test

Let d_g be measurable when date g is processed, with −1 ≤ d_g ≤ 1. Under the
registered null, for every date, E[d_g | 𝓕_{g−1}] ≤ 0. With K_0=1 and
𝓕_{g−1}-measurable 0≤λ_g≤1,

```text
1 + λ_g*d_g ≥ 0
E[K_g | 𝓕_(g−1)]
  = K_(g−1) * (1 + λ_g*E[d_g | 𝓕_(g−1)]) ≤ K_(g−1).
```

Thus K is a nonnegative supermartingale with E[K_G]≤1. At the sealed,
fixed G, for 0<u<1,

```text
P(min(1, 1/K_G) ≤ u) = P(K_G ≥ 1/u) ≤ u.
```

The K_G=0 convention p=1 is correct, including a stake-1/date-return-−1
bankruptcy. A normalized nonnegative frozen mixture of capital processes
starting at 1 has the same guarantee; mixture weights must sum to 1. Holm
then controls FWER≤.05 without independence of its four inputs. Use the
exact thresholds .05/(4−j), not the rounded .0167 display value in code.

The adverse completion minimum is pathwise below the true δ. Fixed
nonnegative cell/date averaging preserves that order and hence the
conditional-mean inequality. This argument requires an adapted completion
rule and stake computation: no future date's observations may enter a date's
stake. A frozen algorithm may be replayed chronologically after the global
seal; predictability does not require releasing interim results to humans.

**No optional-stopping leak is specified.** Date identities/order/horizon are
sealed; technical replacements use the preassigned rule; calibration's
count-only stop occurs before test inference and is included in the F/C
conditioning. No running maximum, early result look, outcome-based top-up,
date deletion or reordering is authorized. G12 must test those actual
mechanics. The simulated-size upper-bound requirement is a conservative
regression gate, not a proof or a reason to change the test after results.

The guarantee is for the intersection of the per-date conditional nulls.
Rejection supplies controlled-error evidence against all of them being
nonpositive; it does not establish a positive marginal campaign mean under
arbitrary dependence. Revision 4 states that limitation candidly. Retain it
in the eventual headline and do not promote descriptive Δ intervals to
unconditional coverage.

One registration detail remains for the schematic honest-FPR sentence:
freeze the exact conditional-rate estimand and confidence-bound inversion.
For example, with honest alarm rate R_g and candidate target q, q−R_g has
the correct sign for testing E[R_g | past]≥q. Under heterogeneous rates,
rejecting that all-date null says some conditional rate is below q; it does
not upper-bound their marginal or average rate. A common conditional-rate
interpretation needs its corresponding model. This is not an additional
primary-test signature finding or a requirement that the reported upper
bound be ≤.05; the current strong label uses the honest FPR **point** bar.

## 3. P1 — material power risk; settle sizing early

The validity repair is expensive in power. With constant positive date
return μ, the best allowed stake is 1, K_G=(1+μ)^G. To clear the **first**
Holm threshold requires K_G≥80, hence μ≥80^(1/G)−1:

| Dates | Constant date return needed for K≥80 |
|---:|---:|
| 20 | .244957 |
| 28 | .169412 |
| 40 | .115777 |
| 60 | .075767 |

These are deterministic-path benchmarks, not universal minimum detectable
effects or 80% power calculations. At .10 the constant path needs 46 dates;
at .05 it needs 90. Jensen's inequality shows that variation in nonnegative
returns with the same realized average can only lower stake-1 capital.
More attempts on the same date improve precision but do not create more
capital factors. In particular, the current 20-date layout is not nearly
equivalent to using all 28 windows on distinct dates.

**Quick synthetic simulation:** Python 3.13 stdlib only, 12,000 independent
replications per row, seed 202611070401 plus the row index. Exactly 28
windows, 12 attacks/window, six cells and the phased 224-attempt H4 roster
are used. At G=20, eight dates hold two windows and twelve hold one; at G=28
each date holds one. For a successful attack, category A is caught by E but
missed by M, time+M and S; category B is caught by those software rules but
missed by E. The two joints are their OR in this special case. A and B have
unconditional probabilities μ_A and μ_B; residual successes are missed by
all detectors. Thus the true effect vector is (μ_A, μ_B, μ_A, μ_A).
The same per-attempt outcomes generate all four hypotheses, rather than
simulating independent, potentially incoherent effect arrays.

There are no regressions, missing values, random calibration thresholds or
availability failures. H4 uses the actual equal-cell mean, and the full
four-p-value Holm step-down is applied. Honest FPR/availability gates are
assumed met, rather than simulated; these are **inference-conjunction** power
estimates, not probabilities of the entire strong-result label. Capability
is also checked and barely changes these estimates (q≥.40 here).

Every realized date return is nonnegative, so λ=1 **pathwise dominates
every allowed predictable stake and normalized frozen mixture in these
laws**. A better plug-in/hedge cannot fix their poor power within this family.
The binary detector law is an optimistic mathematical example, not evidence
that native S, E or a directly calibrated joint will attain it.

| Effect in each H (percentage points) | Side-success q | H1–H3 Holm power, G=20 | H1–H3 Holm power, G=28 |
|---:|---:|---:|---:|
| 5 | .40 | 0/12,000 | 0/12,000 |
| 10 | .40 | 0/12,000 | 0/12,000 |
| 15 | .40 | 0/12,000 | 15.67% |
| 20 | .50 | 3.20% | 96.64% |
| 25 | .60 | 71.58% | 99.99% |

Selected **verbatim output** (the run report archives the exact script):

```text
SIM G=28 effects=(0.10,0.10,0.10,0.10) q=0.40 any_first=0.000333 H1to3=0.000000 CI95=[0.000000,0.000320] all4=0.000000 capability_and_H1to3=0.000000 capability=0.998500
SIM G=28 effects=(0.15,0.15,0.15,0.15) q=0.40 any_first=0.271667 H1to3=0.156667 CI95=[0.150273,0.163280] all4=0.156667 capability_and_H1to3=0.156667 capability=0.998417
SIM G=20 effects=(0.20,0.20,0.20,0.20) q=0.50 any_first=0.070000 H1to3=0.032000 CI95=[0.028998,0.035302] all4=0.032000 capability_and_H1to3=0.032000 capability=1.000000
SIM G=28 effects=(0.20,0.20,0.20,0.20) q=0.50 any_first=0.995167 H1to3=0.966417 CI95=[0.963041,0.969494] all4=0.966333 capability_and_H1to3=0.966417 capability=1.000000
SIM G=28 effects=(0.06,0.18,0.06,0.06) q=0.40 any_first=0.605083 H1to3=0.000000 CI95=[0.000000,0.000320] all4=0.000000 capability_and_H1to3=0.000000 capability=0.998750
ASSERTIONS PASS: literal arithmetic and synthetic laws only; no repo/data imports
```

CI95 is a pointwise Wilson Monte Carlo interval for H1–H3 power; zero observed
rejections is not proof of zero power (upper bound about .032%). The
unequal-effect row shows that one strong channel does not establish the
conjunction. At a .30–.40 side-success rate, a .10 per-attempt reduction is
already a substantial conditional rescue fraction; the .20+ scenarios are
large effects. These are plausible planning scenarios, **not measured v5
effects or a full G12 stress certification**.

**Judgment:** G12 is likely to fail any conventional high-power requirement
for 5–15-point effects at the current counts, even before adding bound
missingness, threshold randomness and honest-gate losses. It can pass under
very large effects and 28 separate dates; the simulation does not justify an
unconditional forecast about the actual study. No numerical power target or
intended MDE is yet frozen, so an actual certification verdict is impossible.

**Requested change:** make the power/MDE decision an early design deliverable,
with a numerical target for the H1–H3 conjunction and separately for the H4
headline (e.g. 80% is a choice for the lead, not an assumed existing rule).
Prefer all 28 distinct dates if retaining 28 windows. If the intended MDE is
modest, prospectively fund more dates/windows or narrow the claim/family
before freezing it; recalculate CAP/calendar and the attack/calibration bill.
If retaining 20–28 dates, explicitly accept a large-effect design and show
conservative power at that MDE. G12's existing “re-sized or narrowed
prospectively” escape is sound, but deferring this readily visible sizing
issue until the final gate risks an expensive unresolved campaign. Do not
recover power by treating correlated episodes as independent or by silently
returning to the invalid marginal-null t test. The hybrid need not be
REDESIGN unless the desired effect/claim cannot fit the justified envelope.

## 4. Independent roster, capacity, rank and ledger arithmetic

A feasible phase-offset vector is `(0,1,2,1,2,0)`. In every window, four
cells contribute one H4 attempt and two contribute two: total 8, with all
six cells nonempty. Each three-window cell cycle has two C, two E and two U
attempts. The first 27 windows give 216 H4 attempts and window 28 gives 8;
per-cell totals are `(37,37,38,37,38,37)`, summing to 224. This example also
gives 112 H4 attempts per pair. Equal-weight cell means remain defined after
pooling either one or two windows on a date and stay in [−1,1]. The actual
offsets and roster still need the stated G12 seal.

CAP-1 now computes gross h/day: 112 busy hours over 168 elapsed hours give
24×112/168=16 h/day, then the distinct v4→v5 stress gives 13.6 h/day. With
accepted fraction a, the workload multiplier is max(1.25,1/a). A 100-accepted-h
job with a=.8 and gross 24 h/day takes 125/24=5.208333 days, equal to
100/(.8×24); no second yield factor is applied to capacity. At a=.7 the
multiplier becomes 1.428571. Actual timestamp intervals must use the same
observation span and count turnaround only once; no records were inspected.

For strict score>cutoff and jointly exchangeable individual scores, the tail
bound is `(m+1−ceil(.95*(m+1)))/(m+1)`: m=39→k=38/.050000;
m=44→43/.044444; m=49→48/.040000; m=63→61/.046875. Ties can make it
conservative. Exchangeable dates alone still do not establish this bound;
the nominal/empirical claim limitation remains necessary.

Using exact rational arithmetic, in hours, with t in seconds:

```text
L = 810*(30000/600 + 1000/35)/3600 = 17.678571428571...
B(t) = (2180 + .4*966)*t/3600 + 46 + 6 + L
C_extra(t) = (64 + .4*28)*t/3600 + 2
             + 28*(30000/600 + 1000/35)/3600
GO_base = B + C_extra; GO_reserved = 1.25*GO_base
```

Verbatim arithmetic output:

```text
ledger t=900 local810=17.678571429 extra_local28=0.611111111 base=711.278571429 reserved=889.098214286 cap_extra=21.411111111 GO=732.689682540 GO_reserved=915.862103175
ledger t=1200 local810=17.678571429 extra_local28=0.611111111 base=925.145238095 reserved=1156.431547619 cap_extra=27.677777778 GO=952.823015873 GO_reserved=1191.028769841
ledger t=1800 local810=17.678571429 extra_local28=0.611111111 base=1352.878571429 reserved=1691.098214286 cap_extra=40.211111111 GO=1393.089682540 GO_reserved=1741.362103175
```

Thus **732.7 / 915.9 h at 900 s**, **952.8 / 1,191.0 h at 1,200 s**, and
**1,393.1 / 1,741.4 h at 1,800 s** reproduce. The cap includes the extra
local bill once. 838 transcripts is a conservative scheduled-roster upper
bill, not a claim that all 126 calibrators can be eligible at the count-only
stop. Rates, loads, quiet return and capacity remain planning assumptions.

## 5. Cosmetics, verification and handoff

**Cosmetic items:** none affecting signature. Round naming or prose
compression can wait; no additional cosmetic edit is requested.

Changed files: this review and
`docs/run_reports/2026-11-07-v5-ruling-delta4-sol1.md`. Verification:
`python3.13 -I -B /private/tmp/jw-v5-delta4-sol1-check.py` **PASS**, exit 0;
the separate constant-path sizing calculation **PASS**; Markdown/diff checks
are recorded in the run report. No unit/full/sharded suite or compileall was
needed for two Markdown files. No network, real measurement/data access,
model download, MLX execution, process/job inspection, pipeline, hardware
probe, coordination-state update or push occurred.

**Next exact step:** lead adjudicates P1 alongside the independently produced
Sol2 review, sets the intended MDE/joint-power target and early sizing route,
and retains the closed R1–R4 repairs. Then freeze and implement G12 on that
prospective design. Actual capability/effect distributions, full G12 power,
deployment receipt coverage and the companion verdict are unknown here.

**Native checks for the lead outside this sandbox:** no native test was
added. After implementation, run the import-gated tiny-synthetic MLX unittest
modules for operator/public replay, forced twins, history/cache/RNG identity,
receipt partitioning, helper concurrency/teardown and tails, one module at a
time using their then-existing paths; download no weights for those tests.
Native parity, capability, timing, CAP and DC-in/battery/tail resolution
remain later lead-controlled gates. Quiet measurements require the clean
machine lane with agents stopped; none is authorized by this review.
