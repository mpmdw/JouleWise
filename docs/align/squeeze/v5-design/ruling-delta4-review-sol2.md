# v5 ruling revision 4 — delta review, Sol2

**Verdict: SIGN_WITH_CHANGES.** Both seats' R1–R4 are resolved at ruling
level. The specified H1–H4 betting test is valid for its newly restricted
conditional-mean null; the H4 rotation and all requested accounting figures
reproduce. One material issue changes my signature: the current 20–28-date
test is very weak for modest escape reductions. Resolve power feasibility
now, before committing to the expensive development/confirmatory roster.
This calls for a bounded inference/roster decision, not abandonment of the
native hybrid or a REDESIGN verdict for the whole study.

Seat **sol2**, branch `align/2026-11-08-v5design-ruling-delta4-sol2`.
Candidate **`52e976dc928c30bb73bcb722ea5cca9dc37bae2c`**. Read the complete
`git diff b606d9788..HEAD`: only `RULING-DRAFT.md`, 96 additions / 44
deletions. Section references below address that candidate. This report does
not edit the ruling, install policy, or authorize collection or scoring.

Prior reports were read from existing local Git objects, without fetching:

| Seat | Ref under `origin/align/2026-11-08-v5design-` | Commit | File in this directory |
|---|---|---|---|
| E1 | `ruling-delta3-sol1` | `570ccd7131c9452746ca2d99a1cc4a3a630fde72` | `ruling-delta3-review-sol1.md` |
| E2 | `ruling-delta3-sol2` | `4e17eb873b85e1238a2733b5ced5cc6bf0a5e81d` | `ruling-delta3-review-sol2.md` |

## 1. Disposition of R1–R4 from both seats

**Resolved** means the operative draft installs the requested obligation;
it does not mean G0–G12 or any native gate passed. E1/E2 swap R1 and R2.
There is no wholly unaddressed R1–R4 finding.

| Prior finding | Status | Operative quotation and assessment |
|---|---|---|
| E1 R1 / E2 R2: betting null versus marginal effect | **Resolved at ruling level** | §4b registers “E[d_g \| 𝓕_{g−1}] ≤ 0 for every g” and explicitly says it is “not a test of the marginal average effect” under unrestricted dependence. F/C, thresholds, policies, roster and prior dates belong to the filtration. The shared-shock example and descriptive, independent-dates qualification for Δ are explicit. This is a substantive narrowing of the claim, not proof of marginal inference. Honest-FPR wording also switches to conditional-rate scope; the actual bound needs the G12 specification discussed below. |
| E1 R2 / E2 R1: 1.2× size tolerance and procedure switching | **Resolved** | §4b: “The 1.2 × nominal certification is dropped”; “There is no data-dependent switch”; “Holm ... is applied to the four valid p-values.” Betting is primary for every sample, t is sensitivity only, and an infinite-cutoff H4 remains with “p_4 = 1.” Simulation is explicitly a code regression test rather than the validity proof. G12 now includes Monte Carlo upper bounds, frozen replication/seed, implementation and full-family power. The remaining power concern is new finding P1, not a recurrence of invalid familywise control. |
| E1 R3 / E2 R3: H4 date support and estimator | **Resolved** | §4a requires “8 H4 attempts and 4 cover-only” and “at least one H4 attempt in every cell.” §4b defines “d_g = (1/6) Σ_s mean(δ_i : i in date g, cell s).” The phased cycle, sealed final-window phase and 37/38 cell totals ensure every assigned date supports all six cells; §4b retains missing attempts through adverse completions. Equal-date/equal-cell estimation is now explicit. |
| E1 R4 / E2 R4: CAP units and double yield | **Resolved** | §5: “h_v4 = 24 × Σ_all windows ... ÷ elapsed calendar hours”; “All windows count, accepted, rejected or redone.” The multiplier is “1.25 if a ≥ 0.80, otherwise 1/a,” charged once against gross capacity. The .85 transfer margin is separate. CAP-1b now needs “≥ 5 ... windows spanning ≥ 7 calendar days.” Actual timestamp/rate evidence remains a future gate. |

The associated small corrections also close: §4d scores C at its “actual
eligible roster,” bills up to 28 additional scores, and explicitly permits
F fitting before freeze while C/test scoring waits for T3. §4c now prints
the general rank-tail formula. §9's R1–R4 disposition is supported by the
operative clauses, rather than being accepted on its own authority.

## 2. Betting validity, including stopping and missingness

Let the sealed initial information be 𝓕₀, including the calibration and
roster. At each chronological date, d_g is measurable in 𝓕_g and bounded
in [−1,1]; λ_g is measurable in 𝓕_{g−1} and lies in [0,1]. Then

```text
1 + λ_g d_g ≥ 0
E[K_g | 𝓕_(g−1)]
  = K_(g−1) × (1 + λ_g E[d_g | 𝓕_(g−1)])
  ≤ K_(g−1)
K_0 = 1  ⇒  E[K_G | 𝓕_0] ≤ 1
P(p_k ≤ u | 𝓕_0) = P(K_G ≥ 1/u | 𝓕_0) ≤ u,  0 < u < 1.
```

K=0 is absorbing and produces p=1, as specified. A mixture is valid when
its frozen weights are nonnegative and sum to one; G12 should enforce that
normalization. Nonnegative averaging preserves the bounds and the pathwise
minimum over compatible missing-data completions cannot increase a
conditional mean. It must remain a lower bound for the same target/null;
it does not manufacture a marginal-null guarantee.

Holm's step-down thresholds are exactly `.05/4, .05/3, .05/2, .05`, with
all four hypotheses retained. No independence between their p-values is
needed. A +∞ calibration cutoff cannot shrink that family after the fact.

**No optional-stopping leak is specified.** G is the sealed date roster;
there is no early look, running-maximum selection or outcome-driven top-up.
Although a genuine nonnegative supermartingale can also support certain
stopped tests, that is not this registered procedure. Predictable stake
adaptation may be evaluated by an isolated custodian after sealing all data,
using chronological prefixes only; it must not give policies any feedback.
Selecting the stake rule, mixture weights, date exclusions or terminal date
after looking at test outcomes would violate the freeze. Assigned lost
dates/attempts stay represented by the adverse-bound rule rather than being
dropped until the result passes. These are implementation obligations, not
observed leaks.

The rejection concerns failure of the *all-dates conditional null*: at least
some conditional reductions are positive. It does not establish a positive
average population effect or positivity on every date. Revision 4 now says
this explicitly, including why a persistent shared shock is no counterexample
to the stated theorem.

**Honest-FPR qualification for G12:** §4b gives a direction and conditional
scope, not yet a complete interval algorithm. For date rate R_g∈[0,1],
`d_g(q)=q−R_g` supplies the same theorem under the pointwise null
`E[R_g|past]≥q` on *every* date. Rejecting that null says some conditional
rates are below q. Its inversion must not be advertised as an upper bound
on every date's rate or, automatically, on the average of heterogeneous
predictable rates. Register the target (a common conditional rate, or a
specified average) and a valid matching bound. A bounded martingale
concentration bound can handle the average, though it will be wide at this
G. This is a registration specification item; no numerical FPR interval is
certified by this documentary review, and it does not invalidate H1–H4.

## 3. P1 — material power feasibility; decide now

The stake cap has a substantial price. On any nonnegative date path,
λ=1 maximizes every capital factor over all permitted predictable rules;
a convex mixture cannot beat it. Jensen then gives

```text
K_G ≤ product_g(1+d_g) ≤ (1+mean(d))^G.
First Holm rejection requires K ≥ 80.
G=20: observed mean(d) must be ≥ 80^(1/20)−1 = .244957.
G=28: observed mean(d) must be ≥ 80^(1/28)−1 = .169412.
```

If a very strong H4 rejects first, the smallest H1–H3 p still needs K≥60:
the respective bounds are .227178 and .157458. These are evidence-crossing
bounds on nonnegative paths, not 80%-power sample-size calculations.
For a constant positive d=.05/.10/.15/.20, just reaching K=80 takes
90/46/32/25 dates. The current 28 windows supply at most 28 dates; treating
the 336 attempts as 336 independent dates is not a repair.

**Quick simulation:** stdlib only, 10,000 repetitions per setting, seed
20261108 with deterministic setting offsets. It uses the actual 28-window
phased six-cell roster. G=20 has eight two-window dates and twelve single
dates; G=28 has one window per date. For each assigned attempt, δ is +1
with probability μ+r, −1 with probability r, and 0 otherwise, independently
across attempts. Thus the expected date reduction is μ. H1–H3 share the
same synthetic δ; H4 uses its assigned subset of those attempts. This
deliberately correlated family is allowed by Holm. It is an illustrative
law for paired differences, not a fitted detector/capability model.

All stakes equal 1. At r=0 this is an upper envelope for all allowed stake
rules/mixtures on these same data. At r=.05 it is one admissible strategy,
not such an envelope. No missingness, threshold randomness, capability-bar
failure, monitor failure, date shock or drift is simulated. Full Holm
rejection is tested; the strong-result conjunction is not. Selected **verbatim
output** (entries are probabilities, not percentages):

```text
G mu regression H1_first H4_first Holm_H1to3 Holm_all4
20 0.05 0.00 0.0000 0.0000 0.0000 0.0000
20 0.10 0.00 0.0000 0.0000 0.0000 0.0000
20 0.15 0.00 0.0000 0.0001 0.0000 0.0000
20 0.20 0.00 0.0189 0.0363 0.0334 0.0334
20 0.25 0.00 0.5033 0.4641 0.5806 0.5806
20 0.30 0.00 0.9729 0.9179 0.9805 0.9805
28 0.05 0.00 0.0000 0.0000 0.0000 0.0000
28 0.10 0.00 0.0001 0.0004 0.0001 0.0001
28 0.15 0.00 0.1062 0.1396 0.1512 0.1512
28 0.20 0.00 0.8833 0.7806 0.9069 0.9069
28 0.25 0.00 0.9993 0.9945 0.9995 0.9995
28 0.30 0.00 1.0000 1.0000 1.0000 1.0000
28 0.10 0.05 0.0010 0.0045 0.0014 0.0014
28 0.20 0.05 0.7798 0.6614 0.8108 0.8096
```

Maximum Monte Carlo standard error is .005 (roughly ±.01 for a 95% interval
near .5). Zero in 10,000 has a one-sided 95% binomial upper bound about
.00030; it is not literal zero population power. Source, complete output
and SHA-256 are preserved in the accompanying run report.

**Assessment:** G12 is unlikely to certify useful power for 5–15
percentage-point reductions in all required contrasts, particularly the
increment over strong software. At 28 dates it can plausibly pass for
roughly 20-point effects in this favorable law; at 20 dates it needs closer
to 30 points. These are all-attempt reductions, not catch conditional on
side success. At the .30 capability floor a .20 improvement already means
rescuing two thirds of successful escapes, before accounting for regressions.
That may happen, but the draft supplies no evidence that every required
contrast achieves it. Actual effects and the final stake rule are unknown.

**Required before signing the present roster:** specify a scientifically
useful effect vector and numerical power target (80% is an illustration
here, not an installed requirement), then demonstrate feasibility at a
sealed date schedule. If the intended MDE is about .10, revise now: more
genuine dates/attempts with a recosted roster, a justified narrower
dependence/null model with a valid more efficient procedure, or narrower
prospective claims. A different plug-in rule or mixture within the present
stake cap cannot fix the favorable nonnegative-path ceiling. Stakes above
1 lose nonnegativity at d=−1. Simulation-qualified t tests, relabelled
attempts or post-result top-ups are not valid substitutes. Even 46 dates
only crosses the constant-.10 evidence threshold; it does not certify
80% power and needs a new support/cost calculation.

The existing G12 instruction to resize/narrow if power fails is sound.
P1 asks to make that feasibility decision before spending through G4–G11,
rather than discovering an already visible limitation at registration.
It changes the scientific return and likely roster/calendar, which is why
it affects signature; it is not another demand for wording cleanup.

## 4. Independent roster and arithmetic checks

One legal phase-offset vector is `(0,0,1,1,2,2)`. Enumerating 28 windows
gives eight subset and four cover attempts in every window, 224 H4 and 112
cover in total. Each cell contributes four H4 attempts per complete
three-window block; after nine blocks it has 36. The final window adds
one to four cells and two to two cells: `(37,37,37,37,38,38)`.
All three classes total 112 each. Grouping windows into dates preserves
all six cells. Equal weighting of the six cell means and then dates is a
convex combination in [−1,1]; it need not equal the raw pooled-attempt mean
when date sizes differ. That distinction is now correctly frozen.

With t in seconds, using exact rational arithmetic until display:

```text
L = 810*(30000/600 + 1000/35)/3600 = 17.678571428571... h
extra_local_C = 28*(30000/600 + 1000/35)/3600 = .611111111111... h
B(t) = (2180 + .4*966)*t/3600 + 46 + 6 + L
cap_extra(t) = (64 + .4*28)*t/3600 + 2 + extra_local_C
GO_base(t) = B(t) + cap_extra(t)
GO_reserved(t) = 1.25*GO_base(t), when a ≥ .80

ledger t=900 base=711.278571 reserved=889.098214 cap_extra=21.411111 GO_base=732.689683 GO_reserved=915.862103
ledger t=1200 base=925.145238 reserved=1156.431548 cap_extra=27.677778 GO_base=952.823016 GO_reserved=1191.028770
ledger t=1800 base=1352.878571 reserved=1691.098214 cap_extra=40.211111 GO_base=1393.089683 GO_reserved=1741.362103
```

Thus **732.7 / 915.9 h at 900 s**, **952.8 / 1,191.0 h at 1,200 s**,
and **1,393.1 / 1,741.4 h at 1,800 s** reproduce. The full 28 extra C
scores are a conservative attempted-roster allowance, not a claim that
126 eligible C items can survive the count-only stopping rule.

**CAP-1:** all busy durations in hours over elapsed hours, multiplied by
24, has units h/day. For 112 gross busy hours over 168 elapsed hours it
gives 16 h/day, or 13.6 after the .85 transfer margin. At a=.80, a
100-accepted-hour job takes `125/16 = 100/(.8*16) = 7.8125` days.
Dividing the reserved bill by accepted capacity would duplicate yield;
the revised gross denominator avoids that. At a=.70 the multiplier is
1/.70=1.428571, not 1.25 times 1/.70. Disjoint busy/turnaround intervals,
endpoint coverage, actual accepted fractions and loads still require
CAP evidence; none was measured here.

**Rank:** for k=ceil(.95(m+1)), a continuous jointly exchangeable future
score has strict exceedance probability `(m+1−k)/(m+1)`; ties make this
an upper bound. Results: m=39/k=38 → .050000; m=44/k=43 → .044444;
m=49/k=48 → .040000; m=63/k=61 → .046875. The formula is repaired;
exchangeable dates alone still do not prove this episode-level result,
as §4c explicitly warns.

## 5. Proportionate disposition and handoff

Keep the evidence boundary, deployable S, adverse completions, frozen
search/no-feedback rules, count-only calibration stop, local F/C quarantine,
and no-v4-credit provisions closed. No new defect in those clauses is
established by this delta. Native capability, physical closure, receipt
coverage, capacity and calibrated monitor behavior remain unexecuted gates.

**Cosmetic items:** none requiring correction. Review-round labels and
prose compression can be handled editorially; neither is a signature
condition.

**Next exact step:** the lead chooses and records P1's effect/power/date
decision, recosts any revision, and adjudicates this and the independent
companion seat on the resulting candidate. Complete the exact honest-rate
bound at G12. This is one seat's judgment, not the companion seat's
agreement or final lead verification. Novelty and NeurIPS 2027 requirements
remain explicitly unverified pending separate network authority.

Verification: the isolated stdlib script exited 0 with assertions passing;
`git diff --check` passed. No unit/full/sharded suite or compileall was
needed for Markdown-only changes. The review and dated run report are the
only repository edits; coordination state and the ruling remain unchanged.
No network, download, real measurement read, sealed analysis, process/job
inspection, native probe or external user-tree access was used.

**Lead-only native checks outside this sandbox:** no MLX code/tests were
added here. Once implementation exists, run the import-gated tiny-synthetic
MLX unittest modules for operator-held/public replay, forced declared-work
twins, history/cache/RNG identity, receipt partitioning, helper concurrency
and teardown, and tails, one module at a time at their integrated paths.
No native test is claimed passed and no weights are needed for those tests.
Actual capability, timing, capacity and DC-in closure require the later
lead-controlled clean-machine gates, with agents stopped for quiet captures.
