# Counter-review: "Drift Is Never Zero: Temporal Metrology for LLM Energy Experiments on Consumer Silicon"

Reviewer: Opus 5, adversarial lens. Ground truth read at `desk` @ `89b929c`.

## Verdict: **WEAK**

Not a KILL — the underlying material is real, cheap, and honestly described, and the
proposal is unusually disciplined about its own limits (accurate arithmetic, correct
citation of the diagnostics, explicit refusal semantics, explicit concession on Ed's
original goals). But it is not a standalone paper. It is (i) §4 of the MVP draft, (ii)
one row of the MVP's own characterization table, and (iii) a methods appendix — bundled
and given a title. Its central quantity is, by its own cited evidence, *below the
instrument's resolution*, and the one quantity that would clear a floor (recovery-tail
energy) is a new metric family with no minted floor, no calibration basis, no
pre-registered extraction spec, and a confound the D-117 design cannot break.

## Scores (1–10)

| Axis | Score | One-line justification |
|---|---:|---|
| Novelty | **3** | Steady-state/thermal-state protocol discipline is a 15-year-old norm; only the never-zero allowance *construction* is fresh, and it is ~1.5 pages. |
| Feasibility | **6** | Reference cells and 5 s-resolution cooldown traces are genuinely banked; but the recovery-energy claim needs a new floor family and reopens a ratified freeze. |
| MVP leverage | **4** | Leverage is so high it inverts into double-publication risk: >70% of this paper is verbatim MVP §§3–5. |
| Venue fit | **4** | Already a capstone chapter (it is literally in `draft-v1.md`). Standalone ICPE: no. Workshop: marginal. |
| Original goals | **2** | Proposal concedes it serves none. Correct concession; the score follows. |

---

## Fatal flaws

**F1 — It is already published. Double-publication is not a risk here, it is the
baseline state.** `docs/paper/draft-v1.md` line 86–95 is a section titled *"Measured,
never-zero drift allowance"* that states the exact `A_drift = max(observed excursion,
derived reference-repeatability bound)` rule, the 3/1/3 reference design, the midpoint-
curvature rationale, and the "a passing drift screen never means zero drift" claim. That
is Contribution 2's entire descriptive content, already written. Line 151 is the
characterization table's **"Drift and settling"** row, whose method column reads: *"Place
long controlled holds and fixed reference workloads through the window, including start,
midpoint, and end references. After operator or stage activity, repeat the reference
while recording the time required for thermal and admission observables to stabilize;
compare it with the 180 s operating convention."* That is Contributions 1, 3 and 4. Line
158 is a paragraph already distinguishing slow drift from thermal settling. A referee
handed both manuscripts will ask which one is the extended version of the other, and with
Rivoire — who sets a metrology bar and will read both — the salami question is asked out
loud. The proposal never once acknowledges that the MVP contains this content; it says
only that the MVP "treats it as one characterization row," which understates it by a
section and a half.

**F2 — The D-117 windows do not schedule the experiment the MVP's own drift row
specifies, and the proposal substitutes weaker data without saying so.** The frozen
per-window schedule (DESIGN-MEMO §schedule, identical for alpha/beta/gamma) is: *pre
calibration → 12 NEG8 → 3 start refs → absolutes/ABBA → 1 midpoint ref → ABBA → 3 end
refs → post calibration*. There are **no long controlled holds** and **no
post-transition reference repeats**. The 180 s post-admin settle appears exactly once per
window, inside the pre-calibration allowance, and is followed by 22 minutes of NEG8
members before the first reference — so nothing measures residual settling against the
180 s convention. Contribution 4's settle-sensitivity item and the MVP row's "compare it
with the 180 s operating convention" test are therefore **unobservable** from D-117 data.
The proposal's desk-work list includes "sensitivity to the 180-second operator settle" as
if it were reduction work. It is not; it is an experiment that was never scheduled.

**F3 — The central quantity is below the instrument's own resolution, and the proposal
knows it.** Its own best clean estimate is 0.006718 J of point drift over 2.96 h on
~38.5 J references (decision_log line 4519) — 0.017%, roughly **150× below the ~1 J
attribution limit** and ~750× below the ~5 J practical bar. The other two cited numbers
are worse as evidence, not better: 0.778 J is the signature of a **stale end reference
measured ~2 h post-collection** (decision_log line 4508, run report a5) — i.e. a protocol
violation, not in-window drift; and 0.70 J is an ABBA-mitigated 0.47% cross-block trend
on a ~148 J workload. So the honest prospective statement is: *in-window drift on this
stack in a quiet window is not measurable with this instrument.* The proposal correctly
refuses to claim "no drift" and reports containment instead — but a paper whose principal
object is unresolvable by its own instrument yields six binary pass/fail cells. That is a
table, not a results section.

**F4 — Contribution 2 validates the wrong never-zero rule, or two of them at once.**
There are two distinct never-zero constructs in this project and the proposal conflates
them. The one it writes down is the **energy** allowance `A_drift` from draft §4. The one
that actually carries a reportable number is D-102 pin 3 / D-117 cl.1: `A_s =
max(observed_drift_s, 0.010818)` — a **timing** allowance in seconds, worth **~+43% on
the a10 anchor bound** (`CLAIMS_STATUS.md` lines 34, 140). The proposal's stated formula
is the energy one; the constant a reader will expect (0.010818) is the timing one. As
written the contribution is not evaluable. Worse: the interesting version — "does the
never-zero timing floor change a mint decision?" — is a **desk replay of existing
material requiring zero nights**, which means the strongest single result in this paper
does not need any of the three windows.

**F5 — The recovery-tail contrast is (a) unfloored, (b) confounded, (c) informatively
censored, and (d) n=1 at the stated replication unit.**
- *(a) Unfloored.* "Excess-energy area above baseline" is a new metric family. Under this
  project's own regime a claim-bearing metric needs a minted floor (repeatability +
  attribution + drift), a calibration basis, and a pre-registered extraction spec. The
  pulse-train bracket calibrates **phase-edge timing**; it says nothing about
  free-running integration of 5 s idle means over a 100–300 s window. The proposal
  applies "the applicable approximately 5 J bar" without deriving any applicable floor.
  Under D-117's gate discipline that claim cannot be published. The claim "no extra
  base-case night" quietly assumes a floor family that does not exist.
- *(b) Confounded.* 1.5B and 7B decode arms differ in *both* power and duration, so
  "workload-conditioned recovery" is total-delivered-energy-conditioned recovery. Model
  identity is not separable from thermal load without an intensity ladder — which the
  proposal itself defers to an optional fourth window. The headline hypothesis is
  unidentified in the base design, and the proposal lists it as a falsifiable
  contribution anyway.
- *(c) Informatively censored.* `cooldown_gate` (controller.py ~2408–2540, policy
  `subwindow_s=5.0, sustained_window_s=30.0, tolerance_fraction=0.10, cap_s=300.0`)
  terminates the observation at the moment the 30 s rolling mean falls to ≤110% of the
  frozen reference. The tail is right-censored *by the threshold that defines the
  outcome*, and censored at 300 s by the cap — and cap-hit members are additionally
  stamped `{"cooldown_cap_hit": True}` against the **following** repetition, i.e. the
  longest-tail observations are simultaneously admission-affecting events elsewhere in
  the protocol. The proposal lists "cap-hit frequency" as a metric and never addresses
  that the censoring is informative and entangled with science-cell admission.
- *(d) n=1.* The proposal declares "window, not individual cooldown subwindows, is the
  independent replication unit." Only gamma has paired 1.5B/7B arms. Therefore the
  recovery contrast has **one** independent replication unit. Under the project's own
  two-gate rule (floor clearance *and* interval-supported direction), an interval over
  n=1 is not constructible. Either the sentence is wrong or Contribution 3 is dead; the
  proposal does not notice the contradiction.

**F6 — It proposes to reopen a magistrate-ratified freeze, and prices the risk at
zero.** "Before freezing those plans, add a prospective temporal-analysis specification"
— but D-117 plan-freeze is already ratified (`de9e879`, gates 1–8 adopted, U1–U10 work
orders, three toolchain blockers), with U1/U2 confirmed live blockers in the
night-hardening triage register (`89b929c`). There is no U11 for a temporal spec. Adding
one is a new work order into an already-blocked queue, and DESIGN-MEMO's extraction
semantics are explicitly fatal-on-anomaly ("missing prefill phases, fallback values, or
member discovery outside the list are fatal"). A mis-specified temporal extraction that
refuses would jeopardize **the floor mint the P1 capstone paper depends on**. Under Ed's
paper-first priority stack this is the decisive argument: a secondary paper is proposing
to add refusal surface to the primary deliverable's critical path. The proposal's risk
section does not mention this at all.

## On the charge questions, directly

**(b) How many additional windows does it truly need?** The proposal says **0** (+1
optional). Honest accounting is **2 minimum** plus a new floor family:
1. A **long-hold / post-transition reference window** — the experiment the MVP's own
   drift row specifies and D-117 does not schedule (F2). Without it there is no settling
   science, only a drift screen.
2. An **intensity-ladder window** to de-confound thermal load from model identity (F5b).
   The proposal makes this conditional on gamma showing "a repeatable recovery effect
   that is censored or underidentified" — but it is underidentified *a priori*, by
   design, so the condition is already met before collection.
3. Plus desk + likely a repeatability corpus to mint a floor for recovery-tail excess
   energy (F5a).
The three D-117 windows give you: six containment cells (three nights × two families),
~39 cooldown traces per window at 5 s resolution, and a 3-night between-day containment
replication. That supports one table and one figure. It does not support a paper.

**(c) Effect sizes vs floors.** Drift half: 0.0067–0.78 J against a ~1 J attribution
limit and ~5 J bar — structurally sub-floor, guaranteed null. Recovery half: probably
*large* (a ~0.3–2 W elevation over 100–300 s is tens to hundreds of joules, so it will
clear any bar) — but a large effect that "the heavier model heats the chip more and it
cools slower" is thermodynamically obligatory, not a finding. The proposal's stated
"1–20 J, highly uncertain" range looks low to me by roughly an order of magnitude given
the release rule (10% tolerance on a small idle reference); I flag this as my estimate,
not a repo number. Either way the paper faces a bind: the resolvable effect is trivial
and the interesting effect is unresolvable.

**(d) Novelty.** Thin. "Fixed cooldowns and visually stable endpoints are insufficient
evidence of temporal stability" is the founding premise of SPECpower's calibration and
steady-state run rules, of sustained-performance-state methodology in mobile SoC
benchmarking, and of the rigorous-benchmarking literature on measurement bias and
warm-up (Mytkowicz et al.; Blackburn et al.). "Energy tail after a burst of work" is the
tail-energy concept from mobile radio energy work (TailEnder-lineage). Rivoire's own
JouleSort run rules encode the same discipline. *Cited from general knowledge — verify
before use.* What is actually new is narrow and worth stating narrowly: a never-zero
allowance with a **derived, hash-sealed positive lower bound** that is propagated into a
published detection floor, plus its measured arithmetic consequence (+43% on an anchor
bound). That is a contribution. It is one contribution, and it fits in the MVP.

**(e) Existing-material compliance.** Formally compliant — owned hardware only, WT310E
correctly declared a non-dependency, no abandonment of the instrument, no fabricated
apparatus. Substantively non-compliant on one point: it presents a new claim-bearing
metric family (recovery-tail excess energy) as free reduction of banked evidence when it
requires a floor mint the project has not designed (F5a).

**(f) Original-goals service.** Near-zero, and the proposal says so plainly — credit for
that. Its offered defense ("prevents temporal history from being misreported as the
energy effect of those mechanisms") is a hygiene argument that D-014 already implements.
It does not advance spec decode, MTP, MoE, KV/attention, or split inference by one step.

## What the proposal gets right (so this is not a hatchet job)

Its arithmetic reconciles exactly with the DESIGN-MEMO (140 = 50+50+40 science, 36 bound,
21 references = 7×3, 6 bookends). Its diagnostic citations are accurate to the source
lines. Its refusal framing is correct and it explicitly forbids the tempting bad claim
("the result is containment or refusal, not 'no drift'"). Its kill criteria are real,
including the `thermal_pressure`-is-categorical concession — which is correct: the trace
field is a string in `{nominal, normal}`, so "thermal dynamics" is unsupportable
vocabulary. And it correctly refuses to invoke the wall meter. This is a well-executed
proposal for a paper that should not exist separately.

## Three strengthening moves, if kept

1. **Demote it into the MVP and promote the one real result.** Do not write a second
   paper. Write **one subsection** of the MVP — "the price of never-zero" — that reports
   the D-102 pin-3 lower bound's *decision-changing* arithmetic: for each of the four
   minted cells, the operative floor with and without the 0.010818 s floor, and whether
   any claim verdict flips. This is desk-only, needs zero nights, uses the windows Ed is
   already funding, is genuinely novel against the literature, and is exactly the kind of
   result Rivoire will respect. Everything else in this proposal is either the MVP's own
   text or a null.
2. **Make the temporal extraction structurally incapable of harming the floor mint.**
   If any temporal spec is added, it must be a *separate, read-only, non-blocking*
   artifact with its own evidence root that cannot refuse or gate the D-117 extraction —
   explicitly outside the fatal-on-anomaly path, and added as a post-hoc reduction of
   already-collected bundles rather than a pre-freeze plan amendment. Otherwise the
   proposal is trading P1 risk for P3 content. If that separation is not achievable
   without a plan amendment, drop the temporal spec entirely and reduce the cooldown
   traces after collection with no pre-registration claim attached (report as
   characterization, not claim).
3. **If the recovery science is wanted, fund the identifying design and say the price
   out loud.** One intensity-ladder window (fixed model, three delivered-energy levels)
   plus a long-hold/post-transition window, plus a minted floor for recovery-tail excess
   energy with its own repeatability corpus and a defined baseline and integration
   boundary. State the censoring model explicitly (right-censored at release and at the
   300 s cap, with cap-hits informative) and pre-register a survival-style analysis of
   time-to-release rather than an energy contrast. That is a **real** two-extra-night
   paper — and then it should be honestly compared against the other 19 directions on
   two nights of Ed's scarcest resource, where I do not expect it to win.

## Bottom line for the portfolio decision

Fund the **desk-only** never-zero-arithmetic subsection inside the MVP. Do not fund a
standalone drift/thermal paper, and do not amend the D-117 freeze for it. If Ed wants a
metrology-flavored second paper, the never-zero construction is a better *seed* for the
general floor-methodology direction than it is a paper of its own.
