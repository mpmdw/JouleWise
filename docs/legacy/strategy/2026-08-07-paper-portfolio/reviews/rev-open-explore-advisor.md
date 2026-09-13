# Counter-review: `prop-open-explore-advisor.md` (advisor-lens open exploration)

**Reviewer:** Opus 5, counter-review lens (contract + resourcing + dedup).
**Ground truth checked against:** `desk@89f28bf` — `docs/decision_log.md` D-117,
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`,
`docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md`,
`docs/paper/draft-v1.md` §§6–8, `CLAIMS_STATUS.md`.
**Pool members compared:** `prop-mvp-icpe-upgrade`, `prop-wall-meter-validation`,
`prop-prefill-scaling-laws`, `prop-drift-thermal-science`,
`prop-long-generation-dynamics`, `prop-floor-methodology-general`.

---

## Headline

**Every factual number in this proposal checks out** — the most accurate submission
I have audited in this pool. And it does not matter, because **all three papers are
dominated by other pool members.** Paper 1 is the plan of record with a title on it.
Paper 2 is `draft-v1.md` §6, which already exists in the repo as six
`[PENDING WINDOW C]` rows, and is also contribution 2 of `prop-mvp-icpe-upgrade`.
Paper 3 is `prop-wall-meter-validation` with the acceptance rule, the held-out
design, the battery control and the primary-source meter citations removed.

Net unique portfolio contribution: **approximately zero.** Its residual value is as a
*convergence signal* (an independent lens ranked the same three things in the same
order) and as the surfacing of one real gap in the MVP scope (§6 ships empty), which
argues for a merge that a different proposal already proposes.

---

## (a) Is the advisor modeling credible, or a caricature?

**CREDIBLE, but shallow and under-exploited. Not a caricature — and that is the
problem.** It invents no advisor opinions that contradict the record; it also never
reaches the two artifacts that a JouleSort/Mantis author would most obviously want.

What it gets genuinely right:

- **Full-system boundary as the deepest objection.** JouleSort's defining move was
  measuring the *whole system at the wall* under a fixed workload with published
  entry rules. The proposal correctly identifies that `powermetrics`' modeled SoC
  boundary is *not* the full system, and makes closing that gap a whole paper. That
  is the highest-signal advisor prediction available and it is correctly made.
- **Refusal-as-evidence maps to benchmark-entry validation.** JouleSort disqualified
  invalid entries; JouleWise retains refusals as evidence. The proposal connects
  these, correctly.
- **Correct instinct that a metrology referee prefers instrument depth over
  premature mechanism breadth.** Consistent with the repo's own advisor-feedback
  record. It also correctly refuses to smuggle mechanism work in.
- **It does not overclaim what a wall meter can validate** ("agreement validates
  totals, not the prefill/decode split"). That is the right epistemic line and it is
  drawn explicitly as a *contribution*, which is good taste.

Where the modeling is thin — and these are misses, not stylistic quibbles:

1. **It never proposes an efficiency metric or benchmark rule set.** JouleSort's
   actual contribution was `sorted records per joule` plus divisions, entry rules and
   a validator. The JouleWise-shaped analogue — a defined tokens-per-joule with a
   named boundary, an honest denominator, and the fail-closed protocol as the entry
   rule set — is the single most JouleSort-lineage artifact this material can yield,
   and the session dedicated to the advisor lens does not mention it once. (It lives
   in `prop-energy-nutrition-label` / `prop-tokenizer-honesty` instead.)
2. **It never names Mantis / the counter→wall-model lineage.** Rivoire's other
   principal line of work is full-system power *models* from OS counters validated
   against a wall meter across load families. That is *exactly* Paper 3's shape, and
   framing it that way would materially strengthen the positioning. Worse:
   `draft-v1.md` §8 cites RAPL-in-Action, Jay & Ostapenco, MLPerf Power and SPEC —
   **and cites neither JouleSort nor Mantis.** The one session tasked with the
   advisor's perspective failed to catch that the paper does not cite its own
   advisor's foundational work. This is a real, actionable finding the session was
   uniquely positioned to make and did not.
3. **It ignores the standing plain-language requirement.** Advisor-facing surfaces
   get plain language and defined terms (standing, from actual professor feedback).
   A session modeling this advisor should have flagged the reader-facing prose bar.
   It modeled the advisor's *technical taste* and not her *communication bar*.
4. **One unevidenced disposition claim carries the whole ranking** ("a metrology
   reviewer would value these above premature mechanism breadth"). Probably true;
   asserted, not argued.

**Verdict on (a): credible lineage instincts, executed at half depth. Do not use this
document as the portfolio's model of the advisor — it is missing the benchmark-design
half of the lens entirely.**

---

## (b)+(c) Per-idea audit

### Paper 1 — "Calibration Before Comparison: Detection Floors for Phase-Resolved LLM Energy"

**Verdict: VIABLE (redundant — it is the funded plan, not a proposal).**

| axis | score |
|---|---:|
| novelty | **2** |
| feasibility | **10** |
| mvp_leverage | **10** |
| venue_fit | **6** |
| original_goals | **1** |

**Fact-check: clean.** Every number verified against ground truth — 3.14 / 3.24 /
2.80 h budgets (DESIGN-MEMO §Runtime evidence and budgets, all Pass in the 2–4 h
envelope); 50 science bundles as 10 absolute + 40 null-ABBA (memo §alpha, and the
extraction spec's "100 cell-member references but exactly 50 unique bundles"); 40
ABBA contrast members; prefill riders as a new condition family over the same
bundles at zero added runtime; 141.29 J as the *registered* claim metric (correctly
distinguished from the 146.73 J whole-request diagnostic, which it does not quote);
141.29 / 5 = 28×; prefill exclusion at 5.809930 J point with ~4.0 J interval lower
edge. It also correctly states that a contrast failure would mean changed stack
behavior or invalid transfer — **not** license to select another run. That is the
exact discipline D-110/D-117 demand.

**Fatal flaw (as a *direction*, not as work):** it proposes nothing. "Exactly the
three D-117 nights; no extra members" is the decision already adopted today. A
portfolio direction that recommends executing the current plan carries zero decision
information. Its correct role is baseline, and the baseline is already funded.

**Second flaw — the one substantive thing it hides:** Paper 1 says it reuses "the
draft's introduction, calibration, floor, protocol, and limitations sections." It
never mentions **§6, Instrument characterization** — whose six rows are *all*
`[PENDING WINDOW C]`. So Paper 1 ships a metrology paper whose entire
instrument-characterization section is empty, publishing detection floors with no
operating-characteristic evidence that those floors mean anything. That is precisely
the first question a measurement referee — and this advisor specifically — will ask.
The advisor lens should have caught this and merged Papers 1 and 2. It instead split
them and stayed silent about the seam.

**Contribution 1 is not new:** "attribution width exceeds ordinary repeatability" is
already RATIFIED (D-078 cl.11) as a standing project finding. Publishing it is
right; listing it as a falsifiable contribution of these three nights is padding.

**Venue:** capstone yes. "Credible ICPE emerging/workshop" — I'll grant workshop; not
ICPE full, and the proposal does not claim otherwise. Fair.

**OVERLAP FLAG — SUBSET of `prop-mvp-icpe-upgrade`.** That proposal contains Paper 1
verbatim as its stage 1 (same budgets, same 10+40, same 141.29 J / 5.81 J reasoning)
and then adds the ICPE delta. Paper 1 is strictly contained. **Dedup value: nil.**

---

### Paper 2 — "Does the Detection Floor Behave Like a Detection Floor?"

**Verdict: VIABLE as *content*, WEAK as a *standalone paper*. Merge, do not fund
separately.**

| axis | score |
|---|---:|
| novelty | **6** |
| feasibility | **4** |
| mvp_leverage | **9** |
| venue_fit | **5** |
| original_goals | **2** |

The science is the right science — a published operating characteristic for a
software energy counter is a genuinely uncommon artifact and is what makes the floor
claim credible. Four specific problems.

**1. Night budget understated ~2×. Its own kill criterion fires.** Using the memo's
own runtime evidence (1.5B decode member 92.7 s; ABBA blocks 1–5 = 20 members in a
34 min allowance, i.e. ~10% overhead; fixed per-window cost = 8+8 calibration + 22
NEG8 + 21 references + 10 untouched idle ≈ 69 min; 20% margin):

- *Linearity window* (5 length levels 128→2048, n=5): ~52 min raw member time →
  ~2.7 h. **Feasible in one window. Correctly sized.**
- *Micro-delta window* at the project's standard n=10 block basis: 4 levels × 40
  members = 160 members at ~100 s ≈ 267 min raw → (294 + 69) × 1.2 ≈ **7.3 h.**
- Even degraded to n=5 blocks (80 members): (147 + 69) × 1.2 ≈ **4.3 h** — still over
  the proposal's own stated kill line of four hours, and now with a halved block
  basis for the very interval gate under test.

Realistic total is **1 linearity + 3 micro-delta nights ≈ 4 additional windows**, not
"two." And the proposal's kill criterion — "kill if the frozen design exceeds four
hours" — self-executes on its own arithmetic. `prop-mvp-icpe-upgrade` budgets the
same experiment across a metrology window A, a window B *and* a short third window;
that is the honest number.

**2. Slope estimate is biased in the wrong direction.** The proposal derives
"~47 J / 512 tokens ≈ 0.09 J/token" from a *whole-request* diagnostic. Whole-request
energy includes prefill and fixed per-request overhead, so this is an **average**,
not a **marginal** slope, and the true marginal slope is *lower*. Consequently the
quoted 27 / 54 / 81 / 163-token deltas are **too small** to hit 0.5×/1×/1.5×/3× the
floor — longer members, worse budget, in the same direction as flaw 1. The proposal
does hedge ("crude, design-only, must be frozen from a desk pilot"), which is why
this is a should-fix and not a blocker; but the hedge does not rescue the budget.

**3. Circular ground truth — the design's real blocker.** The "known" injected effect
magnitude is *predicted from the fitted slope*. So the operating-characteristic test
measures (slope-model error + detection performance) jointly and cannot separate
them. At the 0.5× arm the slope's prediction uncertainty is of the same order as the
injected effect, so "the instrument correctly refused a sub-floor effect" is
observationally identical to "the injection missed its target." The pass/fail rule
must be stated against a *propagated prediction interval* on the injected effect,
with per-member runtime-observed token counts, or the whole contribution is
unfalsifiable. Not addressed anywhere.

**4. Two physical confounds silently assumed away.**
   (i) **Unequal-duration ABBA.** Injecting effects via output-length deltas makes A
   and B members different lengths, breaking the duration symmetry the null-ABBA
   design and the measured drift allowance were established under; A and B stop being
   exchangeable within a block. This is exactly the coupling `prop-drift-thermal-science`
   exists to characterize.
   (ii) **The floor is treated as one scalar across 128–2048 tokens.** Repeatability
   plausibly scales with total energy while attribution does not, so there is likely a
   *per-magnitude* floor — which multiplies windows again. Draft §6 knows this (it has
   a separate "Null response across magnitudes" row); the proposal does not.

**Venue:** I contest "the strongest owned-hardware route toward an ICPE full paper."
An operating-characteristic study alone is a methods/measurement workshop paper.
`prop-mvp-icpe-upgrade`'s argument — that ICPE full needs characterization *plus* a
held-out prediction study — is the more persuasive read of that track.

**OVERLAP FLAGS (three):**
- **`prop-mvp-icpe-upgrade` contribution 2** is this experiment, stated more
  precisely (nulls at 128/512/2048; slope 0.09–0.10 J/token; 64-token delta ≈
  5.8–6.4 J) and honestly multi-window budgeted. **Dominated.**
- **`docs/paper/draft-v1.md` §6** already specifies this program in-repo as
  `[PENDING WINDOW C]` — linearity, null response across magnitudes, empirical floor
  verification via 0.5/1/1.5/3× micro-deltas in both directions. This is not a new
  paper idea; it is an unexecuted section of the existing draft. The proposal
  half-admits this ("adds the currently pending draft §6 rows") without drawing the
  conclusion.
- **`prop-long-generation-dynamics`** owns the 128→2048 decode ramp as its subject.
  Partial overlap on the linearity window.

---

### Paper 3 — "From SoC Estimate to Wall Energy: Validating the Measurement Boundary"

**Verdict: KILL as a distinct direction. Strictly dominated by
`prop-wall-meter-validation`; subsume.**

| axis | score |
|---|---:|
| novelty | **3** |
| feasibility | **3** |
| mvp_leverage | **6** |
| venue_fit | **6** |
| original_goals | **3** |

Same thesis, same borrowed WT310E, same 1.5B/7B levels, same "one pilot + one
confirmatory window," same correct "totals not the split" conclusion as
`prop-wall-meter-validation` — and worse on every axis where they differ:

| | advisor Paper 3 | `prop-wall-meter-validation` |
|---|---|---|
| acceptance rule | none stated | `ΔE_wall = α + βΔE_pm`, held-out residual ≤ `max(floor, 5% ΔE_wall)` |
| design | "paired workloads at ~512 and 2048" | 4 levels × 6 paired blocks, 4 fit / 2 held-out, counterbalanced |
| load-dependence | not tested | explicit falsifier across idle / GPU-pulse / LLM families |
| battery control | one clause inside *kill criteria* | designed control with recorded battery observations |
| meter sourcing | marketing product page | user manual + communication manual, 100 ms update, fixed-range warning |
| planning energies | 47 J / 192 J | 51 J / 192 J **with a 5–30% discrepancy band → 2.5–15 J and 10–58 J**, i.e. it actually shows the short cell may not clear the bar |

Flaws that are Paper 3's own, beyond being dominated:

1. **Unbudgeted extra window.** It requires "a wall-specific null/repeatability
   floor" — i.e. a whole floor-minting program with its own members and calibration —
   and then budgets one pilot plus one confirmatory window. Minting a wall floor is
   at minimum another night. Under-budgeted by ≥1 window.
2. **Contribution 2 has no acceptance rule.** "Test whether the 1.5B-vs-7B direction
   survives the boundary change" needs a wall-side interval, which needs the floor in
   (1). Circular as written.
3. **Meter suitability asserted, not computed.** It quotes "0.1% of reading + 0.05%
   of range" from a product page and then says suitability "must be calculated at the
   observed load" — without calculating it. At a ~5–75 W laptop load on coarse power
   ranges the *range* term likely dominates; that arithmetic is the feasibility
   question and it is deferred. Also: the accuracy figure itself needs verification
   against the WT310E manual before it goes anywhere near a paper.
4. **It never derives its own central claim.** The crisp argument for "wall cannot
   validate the split" is a sampling-rate argument: 100 ms meter updates are ~3×
   *coarser* than the ~30 ms edge uncertainty that defines the attribution limit. The
   proposal states the conclusion as an assertion instead of deriving it from the
   instrument, which is a wasted opportunity in the one section where this lens
   should be strongest.
5. **Prior art unengaged.** Counter-vs-wall validation with load-dependent error is
   ~2006-era Mantis territory and the Jay & Ostapenco line already cited in the
   draft's §8. Neither is engaged; novelty rests on "on a Mac, for LLM phases."
6. **External dependency.** Gated entirely on a loan Ed does not control. The
   proposal is right to make "no loan means no paper" a kill criterion and right to
   refuse a smart-plug substitute.

**OVERLAP FLAG — NEAR-TOTAL DUPLICATE of `prop-wall-meter-validation`**, and also
overlaps `prop-mvp-icpe-upgrade` contribution 5. **Dedup value: nil. Discard this
version; keep the sibling.**

---

## Synthesis guidance

1. **Do not allocate a portfolio slot to this session.** All three papers are
   dominated. Use it as corroboration that the pool's center of gravity
   (floors → characterization → wall boundary) is correctly ranked, which is real but
   cheap information.
2. **Harvest exactly two things.** (i) The observation that the MVP as scoped by
   D-117 ships with `draft-v1.md` §6 entirely `[PENDING]` — which is an argument for
   folding characterization into the MVP/ICPE scope, i.e. for
   `prop-mvp-icpe-upgrade` over a Papers-1-and-2 split. (ii) Paper 1's fact-checked
   restatement of the D-117 spine, which is accurate enough to reuse verbatim as the
   shared project-brief paragraph across the portfolio.
3. **Log the advisor-lens gap as a task, not a paper.** `draft-v1.md` §8 cites
   neither JouleSort nor Mantis. The paper does not cite its advisor's foundational
   work, and the advisor-lens session did not notice. Fix in the draft; it costs desk
   minutes and it is the kind of omission that colors a first read.
4. **If Paper 2's content is funded** (inside the ICPE upgrade, where it belongs),
   the three blockers above — circular injected-effect ground truth, unequal-duration
   ABBA exchangeability, per-magnitude floors — must be resolved at the desk *before*
   any night is armed. Each is cheap on paper and expensive in wasted windows.
