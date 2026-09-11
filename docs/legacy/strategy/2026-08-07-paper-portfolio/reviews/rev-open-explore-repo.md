# Counter-review — `prop-open-explore-repo.md` (open-ended, repo-asset-sourced)

Reviewer: Opus 5, adversarial counter-review lens (contract + feasibility + novelty).
Ground truth: `scratchpad/desk` @ main; D-117; `2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`;
`2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md`; `2026-08-06-impressiveness-roadmap.md`;
`docs/paper/draft-v1.md`; `docs/advisor_briefs/2026-07-30-advisor-brief.md`;
`TASK_QUEUE.md`; `docs/research_question_bank.md`.

Proposal reviewed: final block, lines 6886–6941 (identical earlier copy at 6828–6885 is
streaming duplication and was ignored).

---

## Meta-finding: the brief was answered backwards

The assignment: *"examine the repository itself — instrument code capabilities, banked
non-claim data, custody machinery, existing diagnostics — and propose 3 papers that the
CURRENT assets make **uniquely cheap or uniquely strong**."*

What came back:

- **#1** = the MVP paper that is already written and already funded. Its "assets" are the
  three D-117 windows that have not been collected yet. Nothing about it is *newly*
  cheap; it is the baseline against which cheapness is measured.
- **#2** = registry row **Q4** / analysis plan **AP-1**, roadmap rank **4**.
- **#3** = registry row **Q6**, roadmap rank **2**, gated on hardware the project does
  not have.

So a session asked "what do your assets uniquely enable" answered with the paper it is
writing plus the top of the strategy backlog. **Zero of the three is asset-discovered.**
The sibling session (`prop-open-explore-registry.md`), which was *not* asked to mine
assets, is the one that surfaced an actual idle asset — the July KV replay spike.

The genuinely un-mined claim-grade assets sitting in this repo, none of which this
proposal mentions: the **refusal-log corpus** as a dataset; the **contamination event
record** (43/50 screensaver-contaminated su-calibration bundles; two live contamination
catches inside the 7B floor window, both recovered per written playbook); the
**pulse-train calibration corpus** itself as a counter-timing dataset independent of
LLMs; the **bracket-drift corpus** and the ~10.82 ms bracket-drift limit; the
**pre-D-078 time-anchor-defective corpora** as a documented instance of a measurement
error class (0.081 J vs 1.649 J for the *same* 128-token prefill workload — a 20× error
caused purely by a time-anchor defect, which is a striking, publishable cautionary
figure that costs zero nights).

**Positive counterweight — factual accuracy is high, and in places better than the
sibling's.** Everything I spot-checked reproduces:

| Proposal claim | Repo source | Verdict |
|---|---|---|
| windows 3.14 / 3.24 / 2.80 h, ≈9.2 h total | DESIGN-MEMO `:327` (sum 9.18) | ✅ exact |
| 50 science bundles per floor window, 40 contrast | Alpha: abs 10 + 10 ABBA blocks ×4 = 50; Gamma: 40 | ✅ exact |
| decode contrast ≈140 J | registered metric `phase_energy_j.decode` 7B−1.5B = 141.29 J | ✅ |
| 7B comparative floor 14.0 J | advisor brief 2026-07-30 | ✅ exact |
| prefill contrast 5.81 J, half-width ≈1.81 J | 5.809930 J; composed half-width 1.808052 J | ✅ exact |
| decode 64→512 ≈45 J (1.5B) / 165–170 J (7B) | 0.098 J/tok ×448 = 43.9; 0.376 ×448 = 168.4 | ✅ best-in-portfolio |
| "no scientific number is presently claim-bearing" | CLAIMS_STATUS + D-117 | ✅ |

One arithmetic understatement: prefill **128→2048 "roughly 19 J"**. From the measured
51.073 J @4096, proportional gives ~25.5 J @2048, minus the 1.65 J base ≈ **23.9 J**.
Flagged uncertain, and conservative in the safe direction, so a nit — but it is the only
number in either document that does not reproduce.

---

## Idea 1 — "When More Repetitions Do Not Help"

### What it is
The MVP paper. Exactly the three D-117 windows, four floor cells, the 7B−1.5B decode
contrast, the refusal machinery. Draft §§1–5 and §8 reused intact; §§6–7 placeholders
filled.

### Assessment
As a *paper*, this is correct, well-scoped, and the right thing to submit. The title is
good — "When More Repetitions Do Not Help" is a better one-line statement of the
attribution-limited finding than anything in `draft-v1.md`, and Ed should consider
stealing it. The kill criterion — *"None short of an unrepaired instrument defect.
Repeated prospective refusals narrow the paper to calibrated non-identifiability; they
do not justify relaxed gates"* — is the single most disciplined sentence in the entire
open-explore pair.

As a *portfolio proposal*, it contributes nothing. There is no decision for Ed to make:
these windows are already the adopted D-117 claim path. A 20-direction fan-out spends a
slot to be told to keep doing what is already funded. And it duplicates three directed
lanes simultaneously.

### Fatal-flaw candidates

**FF1 — no decision content.** Every proposal in this factory is supposed to help Ed
allocate nights and desk time. This one allocates the nights already allocated. Its
marginal information is the title.

**FF2 — contribution 1 is not falsifiable as written.** *"Show whether 59-pulse,
live-bookended calibration contains the observed phase-edge uncertainty in all three
prospective windows."* "Contains" has no threshold here. The repo does have one — the
~10.82 ms bracket-drift screen (`draft-v1.md:54`) — and the contribution should name it.
The brief demanded falsifiable contributions; contributions 2–4 are, 1 is not.

**FF3 — silent on the three D-117 blockers.** The DESIGN-MEMO opens with **F1** (the
ledger cannot reserve both bookend slots under one committed head), **F2** (the
generalized mint is decode-only and single-cell — it *cannot mint the two prefill
riders*), and **F3** (no D-102 successor path for a live-prefixed ledger). All three are
severity `blocker` and all three stand between today and window one. The shared brief
paragraph lists the desk work generically ("two-slot calibration-ledger session,
acceptance-successor machinery, four-cell mint…") but the idea's own "Needs and fit"
paragraph says only *"Owned M3 Max only; no wall meter"* — i.e. the honest answer to
"what does this cost" is **weeks of blocker-clearing desk work**, and the proposal reads
as though the nights are the cost. For the one idea whose entire value is honesty about
cost, that is a real defect.

**FF4 — venue claim drifts.** *"a credible ICPE-full foundation"* — the roadmap is
explicit that ICPE-full additionally needs **C8 (wall validation), cross-day stability,
an artifact-evaluation-quality release, and one deeper contribution**. Idea 1 is
CSCSU + workshop, full stop; the proposal says that too, then adds the ICPE gloss.

### Feasibility vs the bar and the two gates
Impeccable, because it is D-117 as written. Decode contrast ≈141 J against a 14.0 J
comparative floor is ~10×; the ~5 J bar is irrelevantly far away. Prefill riders are
floor cells, not contrasts — correctly, since the 128-token prefill *contrast* is
marginal (5.81 J point, 1.81 J composed half-width → interval 4.00–7.62 J, lower side
under the bar). The proposal explicitly declines that contrast. Correct call, matching
D-117.

### Overlap flags
- **mvp-icpe-upgrade** — SEVERE (this is its baseline; that lane owns the delta).
- **floor-methodology-general** — SEVERE (floors + attribution limit are its whole core).
- **refusal-as-result** — SEVERE (contribution 4 is verbatim that direction).
- **contamination-characterization** — MODERATE (the admission-gate catches).
- **drift-thermal-science** — MILD (drift allowance, bracket screen).

### Scores
novelty **2** · feasibility **9** · mvp_leverage **10** · venue_fit **7** ·
original_goals **2**

### Verdict: **WEAK** as a portfolio entry (excellent as the paper it already is)
Nothing to fund. Harvest the title and the kill-criterion sentence; discard the rest.

---

## Idea 2 — "From Measurements to Workload Energy Budgets"

### What it is
AP-1's `4×3` grid (prompt {128,512,2048,4096} × output {64,256,512}), holdouts
`(512,256)` and `(4096,512)`, n=5 (n=10 near floor), **one stack first, second stack
only if the first passes its holdouts**, ~2–3 additional nights.

### Head-to-head with the sibling proposal's Idea 1 (same idea)
Both sessions independently landed on registry Q4. They differ in exactly two places,
and the comparison is decisive:

| | repo #2 | registry #1 |
|---|---|---|
| Staging | **one stack first, gated on holdout pass** ✅ better | both stacks at once |
| Nights | 2–3 (one stack) — closer to the roadmap's 2–3 | 3 (both stacks) — under-booked |
| Floor transport across the grid | **named as a kill criterion, no mechanism** ❌ | **null/magnitude-ladder window** ✅ better |
| Magnitude estimates | 45 / 165–170 J — exact | ~40 / ~165 J — slightly loose |
| Overselling | "predict held-out single-request energy" | same error, plus in the title |

**The decisive gap is floor transport.** A detection floor here binds to *"one declared
condition family: the same telemetry backend, metric, window type, **workload profile**,
and stack identity"* (`draft-v1.md:60`). Read literally, 12 (prompt,output) cells = 12
condition families = 12 floor cells per stack. D-117 spends **9.2 quiet hours to mint
four**. Repo #2 names this ("if planned cells lack compatible floor transport") and then
proceeds as though 2–3 nights suffices. The sibling proposal has the answer — the
`draft-v1.md:148` **[PENDING WINDOW C]** "null response across magnitudes" ladder is the
empirical license to transport a comparative floor across the grid's magnitude range —
and this proposal does not. **Merge the sibling's ladder into this proposal's staging and
you have the best version of Q4 in the portfolio.**

### Fatal-flaw candidates

**FF1 (shared with the sibling) — "prediction" oversells a categorical additivity test.**
`E = fixed + prompt_level + decode_level` is categorical (per `research_question_bank.md:475`).
Holdouts are unmeasured *combinations of measured levels*. The study tests **absence of
interaction**; it does not predict any workload outside the grid, and cannot. The thesis
sentence — *"can predict held-out single-request energy on one named local-LLM stack"* —
will be read by a referee as a scaling law and then found not to be one. Retitle around
additivity. To its credit, contribution 3 ("identify which workload increments are
resolvable and where attribution prevents coefficient claims") is exactly right.

**FF2 — floor transport unsolved (above).** The blocker.

**FF3 — the desk cost of minting is unpriced.** D-117 blocker **F2**: the generalized
mint is *single-plan/single-cell*, and pinset v2 + a four-cell aggregate artifact is
being built *just for D-117's four cells*. A 12–24-cell grid needs the same machinery at
several times the cardinality, with prospectively frozen acceptance thresholds per cell
before data exists (the D-079 discipline: thresholds hash-sealed eight days before the
data). "New work is campaign-spec generation, AP-1 registry freeze, deterministic
holdout analysis, and figures" understates this by a wide margin.

**FF4 — one-stack staging weakens the paper it is trying to strengthen.** Gating the
second stack on the first's holdout pass is good risk management and bad science
communication: a single-stack additivity result on one 1.5B model is a much thinner ICPE
contribution than a two-stack result, and the roadmap's rank-4 entry assumes the full
designed matrix (*"Fund the full designed matrix or omit the predictive claim; do not
replace it with opportunistic workload breadth"*). The staging must therefore be framed
as *sequencing*, with both stacks committed — not as an option to stop at one.

### Feasibility vs the ~5 J bar and the two gates
Effect sizing is the best in the portfolio. Decode 64→512: 43.9 J (1.5B), 168 J (7B) —
both ≫ bar, both derived correctly from 0.098 / 0.376 J-per-token. Prefill 128→512 ≈
4–5 J, correctly flagged *may not clear*; 128→2048 ~24 J (proposal says 19 J,
understated but conservative), clears. The **residual/interaction** term is the one that
may sit under the floor, correctly handled: *"a holdout miss means the additive model is
rejected — not patched with an interaction after inspection."* That single sentence is
the pre-registration discipline this project exists to demonstrate, and it is the
strongest reason to fund some version of Q4.

Single-request boundary: preserved. No wall meter. No new hardware. Existing runtime,
suite, reducer, ABBA, custody, analysis-registry all reused — the "uniquely cheap"
argument is genuinely true *here*, if nowhere else in this document.

### Venue-fit honesty
*"Capstone second chapter, then ICPE full research"* — defensible and matches the
roadmap's rank-4 rationale, provided the C8/stability/artifact prerequisites are stated.
They are not. Same omission as the sibling.

### Overlap flags
- **prefill-scaling-laws** — SEVERE (prompt axis is that direction's core).
- **long-generation-dynamics** — MODERATE (output axis; different question — position
  effects vs cell totals).
- **mvp-icpe-upgrade** — SEVERE (roadmap names Q4 held-out as *the* ICPE upgrade).
- **param-scaling-energy** — MILD (two-stack factor).
- **`prop-open-explore-registry.md` #1** — **NEAR-TOTAL DUPLICATE**. Merge, do not fund
  twice.

### Scores
novelty **5** · feasibility **6** · mvp_leverage **9** · venue_fit **8** ·
original_goals **5**

### Verdict: **VIABLE** — the best-staged version of a well-known backlog item
Fund the *merged* Q4 (this proposal's staging + the sibling's null-magnitude ladder),
inside `mvp-icpe-upgrade` / `prefill-scaling-laws`, not as a standalone direction.

---

## Idea 3 — "Do SoC-Rail and Wall-Power Measurements Support the Same Conclusion?"

### Assessment
A duplicate of the directed **`wall-meter-validation`** proposal *and* of the sibling
session's Idea 3. Three slots in one factory spent on one axis. The directed lane, which
was briefed specifically on *"what it adds, what it can never validate (phase split)"*,
should own it.

Best line in the write-up, and a real contribution: contribution 4, *"empirically
separate total-scale validation from phase-attribution validation,"* with the thesis
stating up front that external AC measurement *"remain[s] explicitly unable to validate
the prefill/decode split."* That is precisely what `draft-v1.md:56` says the pulse
calibration validates and the wall meter cannot (*"only an external meter could
additionally validate the absolute whole-system scale"* — scale, not attribution). The
proposal gets this right where a careless version would claim the meter validates the
phase split. Transplant it.

### Fatal-flaw candidates

**FF1 (BLOCKER) — the instrument is not merely unowned, its acquisition decision is
unmade and Ed-blocked.** `TASK_QUEUE.md:327`: **P1-003**, status `READY [ED-EXTERNAL]` —
*"Record the wall-meter decision: meter make/model or unavailable verdict."* The
importer, `P2-048`, is `SHELVED — trigger: P1-003`. The kill criterion here is entirely
*post*-borrow (calibration status, cadence, uncertainty, clock bound, battery
neutralization) and never states the *first* gate: does the unit exist and is a loan
agreed. The roadmap prices the path at **4–8 weeks**; the proposal gives no calendar at
all. A proposal whose critical path runs through an unmade external decision must lead
with that, not bury it.

**FF2 — battery neutralization is named four times and solved zero times.** On a
MacBook the AC-side reading includes charging current, which can dwarf the residual
being measured. The repo has no mechanism. This is the single most likely cause of an
unusable first pilot, and it gets a noun.

**FF3 — sizing is inside-out.** *"The model-size effect should exceed 100 J … the
absolute wall-minus-SoC gap is probably tens of joules."* Both are true and both are
the easy parts. The scientifically interesting quantity is the **load-dependent
boundary bias** — whether the SoC-to-wall ratio changes between compute-heavy and
long-context conditions — and the proposal concedes that *"boundary-interaction effects
may be below 5 J."* So, as with the sibling's cache proposal, the headline question may
be unresolvable while the easy questions clear. It handles the refusal semantics
correctly (*"no flip resolvable, not boundary equivalence"*), but the design should be
**powered for the interaction**, not for the model-size effect that is already known to
be ~141 J. No power argument is offered.

**FF4 — two windows is optimistic for a first-contact instrument.** One pilot plus one
confirmatory, with a bespoke synchronization bridge, a new floor class, dual-stream
custody, and an inline AC fixture, all on hardware nobody in this project has used
before. The roadmap says the confirmatory run may share a later frozen campaign *"only
after the importer and protocol pass independently"* — i.e. more than two sessions.

### Feasibility vs the bar and the two gates
Correctly notes (as does the sibling) that the ~5 J phase-contrast bar does not govern an
external meter and a new paired meter/synchronization floor is required. Good. Refusal
semantics correct. Existing-material compliance: acceptable — the WT310E is explicitly
permitted by the brief and P2-048's bridge design already exists.

### Overlap flags
- **wall-meter-validation** — **TOTAL DUPLICATE**.
- **`prop-open-explore-registry.md` #3** — **TOTAL DUPLICATE**.
- **floor-methodology-general** — MILD (the new paired-meter floor class).

### Scores
novelty **4** · feasibility **3** · mvp_leverage **8** · venue_fit **7** ·
original_goals **3**

### Verdict: **WEAK** — redundant and blocked on an unmade external decision
Kill as a portfolio entry. Transplant contribution 4's scale-vs-attribution distinction
into the directed `wall-meter-validation` proposal.

---

## Cross-cutting

1. **Existing-material compliance: PASS on all three.** Nothing abandons the instrument;
   nothing invents apparatus without a path. The hard constraint was respected, and the
   shared brief paragraph is the most accurate project restatement in either document.
2. **Asset-mining: FAIL against the assignment.** The brief asked what the *current
   assets* uniquely enable. All three answers came from the strategy roadmap and the
   registry, not from the repository. The refusal log, the contamination record, the
   pulse-train corpus, the bracket-drift corpus, and the pre-D-078 time-anchor defect
   (0.081 J vs 1.649 J on identical workloads — a 20× error from a pure timing defect,
   available at zero night cost) were all left on the floor.
3. **Original-goals service: essentially nil.** All three write-ups concede they serve no
   mechanism axis. Idea 2 claims to serve "modular-harness, workload-swappability,
   split-budgeting" — of these only workload-swappability is real; nothing here builds
   toward spec-decode, MoE, MTP, KDA, or split inference.
4. **Numeric discipline: the best of the two open-explore sessions.** Every claim-bearing
   number reproduced from primary evidence except the 128→2048 prefill estimate (19 J vs
   ~24 J), and uncertain quantities carry explicit `[uncertain]` / `[linear estimates]`
   labels. Whatever else is wrong here, it is not fabrication.
