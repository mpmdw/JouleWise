# Counter-review — `prop-mvp-icpe-upgrade.md`
### "From Software Counter to Scientific Instrument: Phase-Resolved LLM Energy Measurement with Calibrated Refusal"

**VERDICT: WEAK** — sound core, fatal flaw in the thing that makes it an *upgrade*.

| Axis | Score |
|---|---|
| Novelty | **4 / 10** |
| Feasibility | **4 / 10** |
| MVP leverage | **8 / 10** |
| Venue fit | **5 / 10** |
| Original goals | **3 / 10** |

Contributions 1–3 *are* the MVP paper. The proposal's own thesis is that C4 (held-out
workload prediction, "Q4") and C5 (WT310E wall validation) lift it to ICPE full track.
Reviewed on that thesis: C4 cannot be claim-bearing under standing repo doctrine, C5 is
an Apple-silicon replication of a paper the MVP draft already cites, and the night budget
is understated by ~30%. The fallback the proposal itself names — metrology core, workshop
or ICPE Emerging — is the honest version and is genuinely strong.

---

## Numbers audit (the proposal's best feature)

Verified exact against the checkout at `89b929c`:

| Cited | Repo source | Status |
|---|---|---|
| 141.29 J decode contrast | `CLAIMS_STATUS.md:63` (`phase_energy_j.decode`, 7B−1.5B, frozen v3 manifest) | ✅ exact, correctly labelled diagnostic/pre-genesis |
| 14.0 J 7B comparative floor | `CLAIMS_STATUS.md:62` — 13.998036715259254 J | ✅ |
| 5.81 J 128-tok prefill delta; interval to ~4.0 J | `2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:173,204` — mean 5.809930 J; composed interval **4.001878–7.617982 J** | ✅ exact, and correctly used to *exclude* the arm |
| 3.14 / 3.24 / 2.80 h budgets | `d117-plan-freeze/DESIGN-MEMO.md:327` | ✅ |
| 59-pulse bookends | `docs/contracts/powermetrics_fiducial.md:27` (v3) | ✅ |
| 1.5B decode ≈ 0.09–0.10 J/token | derivable: 7B absolute-cell mean 192.386 J @512 out, minus 141.29 J ⇒ 51.1 J / 512 = **0.0998 J/tok** | ✅ independently reconstructs |
| "long-prompt effects reach tens of joules" | 1.5B prefill 51.07 J @4096 vs 1.712889 J @128 | ✅ understated, if anything |
| **"150-config metrology suite"** | `configs/campaigns/metrology_v1/` holds **191** JSON configs; no "150" anywhere in the repo | ❌ unsourced |
| **"two or three windows"** for the metrology suite | `configs/campaigns/metrology_v1/README.md` §Window packing packs **three** windows (A ~2.76 h, B ~3.09 h "TIGHT", C spillover) | ❌ contradicts the plan it cites |

Arithmetic discipline is above the bar for this factory. That makes the structural
failures below more damning, not less — they are not sloppiness, they are unexamined
inheritance from a superseded measurement regime.

---

## FATAL FLAWS

**F1 — Q4's held-out prediction is a cross-window effect estimate, which standing doctrine
demotes to "preliminary observation."** This kills contribution 4 as specified.

The proposal needs 4 prompt × 3 decode × 2 models × 5 reps = **120 members minimum**, and
concedes it spans "two or three windows." But the repo's sanctioned cross-window mechanism
is *floor transport* — D-082 cl.2 defines a component-scoped cross-window **floor artifact**
schema, where each component keeps its own window basis and allowance, composed by max.
There is no sanctioned path for pooling **point estimates** from different windows into one
estimator. The precedent is explicit and magistrate-set: `docs/run_reports/2026-07-30-mint-merge-coldgate.md:86`
records the 142 J cross-window effect being *relabelled down* to "a strong preliminary
observation — floors bound within-session error; the pre-registered head-to-head is what
upgrades it." `CONSULT-RESPONSE.md` likewise files its cross-window prefill subtraction as
"Corroborating diagnostic only," and D-113 cl.7 forbids mixing window members into a claim
basis at all. A categorical additive fit whose cells were collected on three different nights
is precisely the structure the magistrate has already refused once. The proposal calls the
missing capability "multi-session campaign packing" — a scheduling problem. It is a
claim-custody problem, and nothing in D-082/D-113/D-117 authorises it.

**F2 — Q4's replication counts are sized by a noise-limited formula the project retired.**
The proposal says "normally five repetitions per cell and ten only where prospectively
identified as near-floor." That is AP-1/D-062 sizing, whose arithmetic is
`MDE95 ≈ 1.46 × CV` off a Window-A CV anchor of ~0.3% (`docs/contracts/analysis_plans.md:71-75`)
— a √n-scaling, repeatability-based model. D-078 cl.11 ratified that this instrument is
**attribution-limited (~1 J), not noise-limited (~0.3 J)**, and floors compose repeatability
**plus** a worst-case attribution bound **plus** never-zero drift. A bound does not divide by
√n. The evidence is in the proposal's own citation: the prefill delta has SD 0.121 J over
n=10 blocks, yet a composed half-width of **1.808 J**. Going 5 → 10 reps buys essentially
nothing against the binding term, so the mitigation the plan reserves for near-floor cells is
inert. Per the project's own doctrine, workload **length** is the only free lever — which the
proposal knows (it uses it correctly for micro-deltas) and then forgets for Q4.

**F3 — the ICPE venue gate is hung on hardware that is neither owned nor doctrinally load-bearing.**
"Wall-meter dependency: **yes** for this proposed ICPE-full version" directly contradicts
D-092, which ratified C8 while ruling that "**every claim except C8 must stand on the internal
instrument characterization; C8 stays conditional in the outline and is not assumed**." The
proposal inverts a ratified conditional into a submission blocker. Compounding: D-092 assumed
*purchase*; the borrow path adds an advisor-lab calendar dependency the proposal never dates.
The kill list names "battery-charge neutralization" but supplies no protocol — an M3 Max MBP
on AC with a charging battery makes wall power a function of state-of-charge, and this is the
single most likely way the whole C5 arm produces uninterpretable data. A "safe inline fixture"
is also mains work by an undergraduate, unscoped and unscheduled.

---

## Should-fix

**S1 — night budget understated ~30%.** Claimed 9–10 (3 D-117 + 6–7). Reconstructed:
D-117 **3**; metrology suite **3** (the README packs A/B/C, not "two or three"); Q4 **3–4**
(at ~2.6 min/member from the proven ten-absolute set's 25–28 min, 120 members ≈ 5.5–6 h
science before references, NEG-8 corpus, and 20% margin — and P2-019 additionally requires an
8192-prompt anchor that the proposal silently drops); wall pilot + confirmatory **2**;
contingency **1**. Total **12–13 nights**. One contingency night against a project whose
recorded history includes Window B failing outright (D-113 claim-retired) and 43/50
su-calibration bundles contaminated by a screensaver is not a reserve, it is optimism.

**S2 — "already-designed metrology suite" overstates readiness.** `metrology_v1/README.md`:
"The five draft plans … **must be magistrate-ratified before measurement**,"
`freeze_status: draft_pending_magistrate_ratification`, `micro_delta/k0064` is "only a
DRAFT-PENDING-SLOPE placeholder," and three open ratification questions remain. Also, the
suite "**does not gate a scientific claim, introduce a model, or mint a detection floor**"
and its runnable members are **1.5B only** — so three of the six-to-seven extra nights buy
characterisation, not claims, and say nothing about the 7B stack that carries the headline
contrast. Worth funding; not worth mislabelling.

**S3 — pre-arm blockers omitted from the critical path.** DESIGN-MEMO F1–F3 (two-slot bracket
session; prefill-capable multi-cell mint; D-102 live-prefix successor path) are open blockers
before *any* D-117 arm, and `89b929c` adds live ones (path-doubling in verdict R6; bracket
borrowing; scalar-only preflight). The proposal lists these as desk work without acknowledging
they gate night one.

---

## Novelty

Weakest axis, and the diagnosis is uncomfortable: **the two contributions that constitute the
"upgrade" are the two least novel things in the proposal.**

- **C4** — that inference energy ≈ fixed + prompt term + decode term is the working assumption
  of essentially every LLM-energy paper (Samsi et al.; Fernandez et al.; Husom et al.;
  Stojkovic et al.; LLMCarbon; ML.ENERGY/Zeus). Confirming additivity is not a finding. Its
  only novel element is pre-registered refusal semantics — which is C2's contribution, reused.
- **C5** — Jay & Ostapenco (CCGRID 2023) already established load-dependent software-vs-wall
  divergence, and `docs/paper/draft-v1.md:30` **already cites it** while arguing a wall meter
  observes only a total and cannot validate phase attribution. C5 is therefore a
  substrate-swapped replication of prior work the draft itself frames as the less interesting
  axis, purchased with a borrowed instrument and two nights.
- **C1–C3** are the real novelty, and they are the MVP. The measurement space is now populated
  — *Silicon Showdown* (arXiv 2605.00519, May 2026) uses powermetrics for Apple-silicon LLM
  tokens/joule; TokenPowerBench (arXiv 2512.03024) decomposes prefill/decode phase power;
  ML.ENERGY has published Mac profiling. What none of them do is quantify what their counter
  **cannot** resolve. Targeted search returns nothing on detection floors, attribution limits,
  or refusal reporting for software power counters. That gap is real and it is already banked.

## Venue-fit honesty

Partly creditable, partly evasive. Creditable: it names the workshop/Emerging-track fallback
and reuses the MVP's single-stack limitations rather than hiding them. Evasive: **no calendar**
— the impressiveness roadmap flagged "Venue and calendar ambition remain unbound" as an open
finding (F3) and this proposal reproduces the blindness while proposing 6–7 extra nights plus
a hardware loan. And the generalisability objection an ICPE full-track referee will actually
raise (n=1 machine, one model family, one framework, one quantisation) is not addressed by
either upgrade; a single borrowed meter on the same single machine does not touch it.

## Original goals

Honestly declared as unserved — credit for refusing to smuggle. But the proposal *misses that
it is holding the mechanism axis in its hand.* The (4096, 512) cell is a KV-cache/attention
scaling experiment: decode cost per token rises with context because attention reads a growing
cache. Sizing it (Qwen2.5 configs, from memory — **verify against the pinned `config.json`**):
1.5B ≈ 28 layers × 2 KV heads × 128 dim × 2 × 2 B ≈ 28 KB/token ⇒ ~117 MB at 4096 ctx against
~0.77 GB of 4-bit weights ⇒ **~14% decode-energy rise ≈ +7 J** over 512 tokens; 7B ≈ 57 KB/token
⇒ ~235 MB against ~3.8 GB ⇒ ~6% ⇒ **≈ +12 J**. Both clear the ~5 J bar. The proposal predicts
additivity *holds*; the interesting, publishable, mechanism-level result is the measurable
deviation — and it is exactly the KV/attention axis Ed wants.

---

## Three strengthening moves

1. **Replace C4 with a single-window KV-context-scaling contrast.** Fix decode length,
   vary prompt context (128 vs 4096), collect both arms **inside one window** as an ABBA
   pair — which cures F1 (no cross-window estimator), cures F2 (length is the lever, not
   reps), converts the least-novel contribution into the most-novel one, and serves the
   original KV/attention goal. Freeze the tolerance as a number before collection.
2. **Re-cost to 12–13 nights, and label each night's yield.** Separate claim-bearing nights
   from characterisation nights (the metrology suite mints nothing), scale contingency to the
   project's demonstrated window-failure rate rather than to one reserve night, and put the
   DESIGN-MEMO F1–F3 blockers and the `89b929c` U1/U2 findings on the critical path ahead of
   night one.
3. **Demote C5 to a conditional appendix and unhook it from the venue.** Restore D-092's
   posture: C8 conditional, not assumed. Submit on the metrology core; add the wall arm only
   if the loan, an in-calibration certificate, a named battery-neutralisation protocol, and a
   qualified fixture all land by a dated deadline — and set that deadline, since the repo has
   flagged its absence twice.
