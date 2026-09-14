# Counter-review — `prop-open-explore-contrarian.md`

**Reviewer:** Opus 5 counter-reviewer (independent). Ground truth: `desk` @ main.
**Proposal:** "Contrarian recommendation: three defensible course changes"

## Verdict: **WEAK**

Unusually accurate on facts — I found essentially no factual error worth calling a
defect — and almost entirely empty as a course-change argument. All three "course
changes" are already-ratified items in `docs/strategy/2026-08-06-impressiveness-roadmap.md`
(ranks 1, 2 and 7), and Idea 1's thesis is verbatim the existing thesis of `draft-v1.md`
§2. One genuinely load-bearing finding is buried inside Idea 1 as a subordinate clause,
and it *should* go to Ed — but as a scope ruling, not as a change of course.

| Axis | Score | One-line justification |
|---|---:|---|
| novelty | **2** | Nothing here is absent from the ratified roadmap or the draft's own framing. It re-types rank 1, rank 2 and rank 7 and calls them departures. |
| feasibility | **7** | Idea 1 is trivially feasible because it *is* the current plan; Idea 2 is feasible only on an unsecured loan; Idea 3's feasibility is better than it claims but its stack swap breaks floor transport. |
| mvp_leverage | **6** | Idea 1 helps by pruning, and the §6 / C-iv gap it half-surfaces is the single most useful thing in the file. Ideas 2 and 3 both spend before the MVP lands. |
| venue_fit | **5** | Idea 1's ladder matches the roadmap. Idea 2's "best chance of an ICPE full metrology paper" contradicts the repo's own criteria. |
| original_goals | **5** | Idea 3 really serves the mechanism axis — then picks the second-best mechanism and silently discards the best-scoring one. |

---

## Part 1 — Fact-check against the repo (this is the proposal's strongest section)

| Claim | Status | Evidence |
|---|---|---|
| "complete methods-paper structure but **no citable scientific number**" | **VERIFIED** | `CLAIMS_STATUS.md` §1: "**NONE at this checkpoint**"; "pre-genesis windows CANNOT be claim-consumed — their role is diagnostic and rule-establishing only." |
| D-110/D-117 made earlier passed windows diagnostic | **PARTLY** — right conclusion, loose mechanism | It attributes this to windows "predating the issued calibration regime". The actual ground (D-117 cl.1) is that the issued ledger holds only **import-marked** receipts, candidate discovery excludes imports *by design*, and future live receipts cannot causally bracket past windows — structurally unsatisfiable, not a date rule. D-110's separate ground (RT-1: a never-zero allowance of ZERO where D-102 pin 3 mandates `max(drift, 0.010818)`) is a different defect. Also worth noting the verdicts themselves are **untainted** (RT-5); it is *consumption* that is closed. |
| 3.14 / 3.24 / 2.80 h occupancies | **VERIFIED exactly** | DESIGN-MEMO budget table (188.4 / 194.4 / 168.0 min with 20% margin). |
| 10 absolute + 40 null-ABBA per floor window; "140 science members" | **VERIFIED** | Alpha/beta stage tables (absolute 10, null halves 20+20 → 50); gamma 40. 50+50+40 = 140. |
| Prefill riders ride the same bundles at no extra capture cost | **VERIFIED** | "The prefill rider adds no member and no runtime"; 100 cell-member references over exactly 50 unique bundles. |
| "141.29 J" historical decode contrast; "~28× the 5 J bar" | **VERIFIED**, correctly labelled diagnostic | `docs/run_reports/2026-08-03-16h-runway.md:67`: "registered claim metric `phase_energy_j.decode` 141.29 J vs the 146.73 J idle-subtracted diagnostic." 141.29/5 = 28.3. |
| 128-token prefill contrast 5.81 J, lower interval edge ~4 J, should remain unclaimed | **VERIFIED exactly** | prefill-feasibility SYNTHESIS: 5.809930 J point, composed half-width ~1.81 J, lower edge ~4.0 J, corroborated at 5.903 J; magistrate CONCUR on decode-only. |
| Desk blocker list (two-slot bracket, D-102 successor, prefill-capable four-cell mint, three-window regression, campaign packs, operator/readiness) | **VERIFIED** | Maps 1:1 onto DESIGN-MEMO F1/F2/F3 and units U4–U8. Omits U9/U10 (bookkeeping, postcollection pins) — immaterial. |
| C8 wall meter ratified as future work; borrowable | **VERIFIED but understated** | D-092 (`decision_log.md:117`, Rivoire-answered) ratified the wall meter *for the paper* as claim C8. Roadmap ranks it **#2** and already parks "borrow versus buy… and a cutoff date" as an open Ed decision. |
| Spec-decode 80–230 J, "~6–16× the older conservative 14 J floor" | **VERIFIED verbatim**, correctly flagged uncertain | `docs/run_reports/2026-07-30-sweep-mechanisms.md`, rank-2 row. |
| "pinned `mlx-lm` lacks proposal-count and step-boundary observability" | **VERIFIED — and the proposal understates its own case** | Roadmap F2 confirms it for pinned `mlx-lm`. But `RUN_STATE.md:1979` records "**DSpark/DFlash MLX feasibility CONFIRMED w/ per-round observability**" (2026-07-17), and `joulewise/adapters/mock_spec_runtime.py` plus the frozen AXI-SA bundle contract (`AxiCancelledProposalCounters`) already exist. Part of the gate it wants 2–3 weeks for is already discharged. |

Verdict on Part 1: **near-zero factual error, and the two imprecisions run against the
proposal's own interest.** Credit where due — this is a well-grounded document.

## Part 2 — Are these course changes? No.

**Idea 1 is not a course change; it is the ratified plan plus a label.** Its thesis — "make
the attribution-limited instrument and its calibrated refusals the scientific result" — is
already `draft-v1.md` §2, closing paragraph: *"JouleWise fills that gap by making instrument
characterization and refusal behavior the primary result; model comparisons are
demonstrations of what the characterized instrument can and cannot resolve."* Its experiment
plan is exactly D-117, unmodified. Roadmap rank **1** is "Complete C1–C7 cleanly." Nothing
is being changed. Presenting the status quo as a departure spends the proposal's credibility
on a no-op, and it is the reason the document reads as contrarian in posture only.

**...but one real finding is hiding inside it,** in a subordinate clause: *"replace the
oversized pending characterization table in §6 with the prospective floor/contrast
evaluation."* That points at a live, unrecorded scope contradiction:

> Draft §6 — contribution **C-iv, "full instrument characterization"** (linearity, null
> response across magnitudes, empirical floor verification, phase-attribution causal
> consistency, drift/settling, between-session stability) — has **all six rows marked
> `[PENDING WINDOW C]`**. D-117 funds three windows, none of which is a Window C, and
> D-117 cl.4 explicitly places the broader MET-WINDOW-C-01 C2/C4/C5 campaign *after* the
> three-window closure. So when all three D-117 nights land, §4 gets its floors and §7 gets
> its demonstration — **and §6 stays entirely empty. One of the paper's six advertised
> contributions will have zero evidence.**

Either C-iv is descoped for the MVP (contribution list, abstract and §6 rewritten as
declared future work, with the limitation stated) or the MVP needs a fourth night. I can
find no decision entry recording that choice. **This is the one item worth surfacing to
Ed.** The proposal earns partial credit for reaching it and a mark down for not naming it
as *the* finding — it is buried under a rhetorical frame that invites dismissal.

**Idea 2 is not a course change and its payoff is overstated.** D-092 already ratified the
wall meter for the paper as C8; the roadmap ranks it #2 and already lists borrow-vs-buy and
a cutoff date as Ed decisions. Its headline claim — "best chance of an ICPE full metrology
paper" — contradicts the repo directly: the roadmap says wall validation "validates totals
only—not phase allocation," and ICPE full requires "C1–C8, cross-day stability,
artifact-ready release, **and at least one deeper contribution**." Wall validation is one of
four prerequisites, and the only one gated on an instrument Ed does not own and a loan that
is not secured. Against the paper-first stack (P1 = capstone MVP), funding the
importer / clock-sync / held-out-regression desk stack *before* the MVP lands trades P1 time
for a P2 benefit contingent on someone else's lab calendar. Its own kill criteria concede
the dependency. The roadmap's sequencing — after the MVP, in parallel with the artifact
release, with a hard cutoff — is better and already ratified.

**Idea 3 is the only real course change — and it is the wrong pick, for a reason in the file
it cites.** Three problems:

1. **It selects against the repo's own effect/floor arithmetic.** The
   `2026-07-30-sweep-mechanisms.md` table it quotes ranks spec decode **second**
   (80–230 J, ~6–16× floor). **Rank one in the same table is weight quantization 4b vs 8b:
   ~450–700 J, ~35–50× floor** — a larger, better-understood effect needing no new stack,
   no new observability, no event-schema extension, no custody/admission re-integration,
   with quality screening runnable outside quiet windows (roadmap #5, "1–2 nights"). The
   proposal drops quantization in a list ("Drop wall validation, Q4, broad C1–C5
   characterization, quantization, MoE, MTP, and split") **without ever arguing against
   it**. Choosing ~1/4 the effect/floor ratio at ~10× the engineering risk, while silently
   discarding the dominant alternative, is the document's worst reasoning failure.
2. **Its stack swap voids the D-117 floors it claims to build on.** Draft §1 scopes a
   measurement to "one physical unit, operating-system build, **runtime and library stack**,
   model artifact, quantization, tokenizer, sampling policy…". A separately pinned
   DSpark/DFlash MLX stack is a new condition family; the design memo's transport rule
   (which forbids even a 128-prompt prefill rider from transporting to a 256-token contrast
   without exact matching cells) binds here too. So "use D-117 as the calibration
   foundation" is precisely what a new runtime pin forbids. Its "five nights total including
   D-117" is right in *count* and wrong in *kind*: it buys the MVP plus a separate island
   study sharing §§3–5 methods and none of its floors.
3. **Output identity is the fragile part and gets one sentence.**
   `C-023-OUTPUT-IDENTITY` binds every C5-2.5 rider ("Fixed output-token count is not fixed
   decoded work"). "Deterministic on/off outputs match exactly in dry trials" is the right
   gate, but spec decode against a different drafter is exactly where it breaks, and the
   proposal budgets nothing for the failure branch.

**Funding order:** its own ordering (1 safest, 2 if the loan lands, 3 highest upside) is the
roadmap's ordering with the numbers re-typed. No new information.

---

## Fatal flaws

1. **Not contrarian.** All three proposals are already-ranked items in the ratified roadmap
   (ranks 1, 2, 7 — and rank 7 even names *external-draft speculative decode* as the
   recommended first mechanism choice behind a 2–3 week feasibility gate, which is Idea 3
   almost word for word). Idea 1's thesis is the draft's existing §2 thesis. A proposal
   whose assignment was to challenge ratified direction instead ratifies it while claiming
   otherwise; that mislabelling is itself an evidence failure and it obscures the one thing
   in the file that *is* new.
2. **Idea 3 discards the higher-scoring mechanism without argument** (quantization
   450–700 J / 35–50× floor / existing stack, vs spec decode 80–230 J / 6–16× / new stack).
3. **Idea 3's new stack pin breaks the very floor transport it claims to inherit**, so its
   five-night plan does not produce one paper.
4. **Idea 2's headline payoff contradicts the repo's own assessment** of what a wall meter
   can validate (totals, not phase allocation) and of what ICPE full requires, while being
   the only idea gated on unowned apparatus.

## Three strengthening moves

1. **Lead with the one real finding and drop the other two.** Rewrite the whole document as
   a single scope ruling for Ed: *the three D-117 windows do not produce §6.* Quantify it —
   six `[PENDING WINDOW C]` rows, one of six advertised contributions, zero D-117 members
   addressing them — and present the binary: descope C-iv from the MVP (rewriting the
   contribution list, abstract and §6 as declared future work, with the limitation stated in
   the paper) or fund a fourth characterization night. That is a genuine, decidable,
   currently-unrecorded decision; the "three course changes" framing is what buries it.
2. **Re-run Idea 3's selection against the repo's own table, then defend the pick or switch.**
   The honest comparison is spec decode (80–230 J, new stack, new events, floors don't
   transport, output identity fragile) versus the quantization ladder (450–700 J, existing
   stack, existing floors transport, off-window quality screening). Either argue the novelty
   premium explicitly — it may well win, spec decode is the more interesting result — or
   take the quantization ladder for the capstone and hold the mechanism ambition for ICPE.
   Also update the feasibility claim: `RUN_STATE.md` already records DSpark/DFlash per-round
   observability CONFIRMED, so the 2–3 week gate is partly pre-paid.
3. **Re-scope Idea 2 to what is actually decidable now.** Not "spend two nights on the wall
   meter" but "set a loan-secured-by date and a cutoff after which C8 is cleanly removed" —
   literally the open decision the roadmap already parks with Ed. Correct the payoff claim to
   the repo's own wording (totals only, not phase allocation) and state the residual plainly:
   the wall meter cannot validate the paper's central contribution.

## Should the magistrate surface anything to Ed?

**Yes — exactly one item, and it is none of the three ideas as framed:** the §6 / C-iv gap.
Recommend surfacing it as a **scope ruling** ("does the MVP still claim C-iv?"), not as a
course change, and not attributed to this proposal's contrarian framing, which will invite
the wrong kind of dismissal. Nothing else in this document meets the bar for reopening
D-117 or the paper-first stack.
