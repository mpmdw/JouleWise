# Counter-review — `prop-open-explore-registry.md` (open-ended, registry-sourced)

Reviewer: Opus 5, adversarial counter-review lens (contract + feasibility + novelty).
Ground truth: `scratchpad/desk` @ main; D-117 at end of `docs/decision_log.md`;
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`;
`docs/process_traces/2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md`;
`docs/strategy/2026-08-06-impressiveness-roadmap.md`; `docs/paper/draft-v1.md`;
`docs/research_question_bank.md` / `_registry.md`.

Proposal reviewed: final block, lines 6314–6368 (an earlier identical copy at 6257–6313
is streaming duplication and was ignored).

---

## Meta-finding: the brief was not answered

The assignment said, verbatim: *"propose the TOP 3 paper ideas YOU judge most promising
(**yours may be original — not on any list**)."* What came back is three rows lifted
off existing lists:

- Idea 1 = registry row **Q4** (`docs/research_question_registry.md:42`), analysis plan
  **AP-1**, suite element `q4_l3_shape_grid_v1`, with the holdout cells `(512,256)` and
  `(4096,512)` copied verbatim from `research_question_bank.md:475`.
- Idea 3 = registry row **Q6** (`:44`), plus its C5-2.10 elaboration.
- Both are already **ranked** in the repo's own strategy doc: the impressiveness
  roadmap puts wall-meter at **rank 2** and Q4-held-out at **rank 4**.

Only Idea 2 (prefix-reuse crossover) is a construction rather than a transcription, and
even it sits adjacent to banked riders C5-2.12/C5-2.14. A session invited to originate
returned the repo's own ranked backlog. That is a compliance failure against the
*framing* of the brief, not against the hard existing-material constraint — the work is
honestly grounded, it is just not new information for a 20-direction fan-out.

**Positive counterweight:** the numeric grounding is unusually good. Every diagnostic I
spot-checked reproduces:

| Proposal claim | Repo source | Verdict |
|---|---|---|
| 1.5B prefill 1.65 J @128 | 1.649076 J, `runs_window_a10_20260725/...short-prefill-abs` | ✅ exact |
| 1.5B prefill 51.07 J @4096 | 51.072749 J, a10 prefill-abs, n=10 clean | ✅ exact |
| "49 J diagnostic difference" | 51.073 − 1.649 = 49.42 J | ✅ |
| 12.8 / 25.5 / 51.1 J avoidable prefill @1k/2k/4k | proportional from 51.07 | ✅ arithmetic sound |
| cache load ~0.4 ms | `cacheload_s` 0.000426 s (1024) / 0.000455 s (2048) | ✅ exact |
| save 14–28 ms | `save_s` 0.0136 s (1024) / 0.0276 s (2048) | ✅ exact |
| cache-size prediction within 0.02% | `cache_bytes_pct` 0.0182% (1024), 0.0091% (2048) | ✅ exact |
| exact 64/64 token identity | `tokens_identical: true`, `verdict: replay_supported` | ✅ |
| historical energies 47–200 J | 1.5B decode 50.26 J, 7B 192.39 J (advisor brief) | ✅ |

No fabricated numbers found. Contrast this with the framing looseness below.

---

## Idea 1 — "JouleWise-Q4: Predicting Request Energy from Prompt and Output Shape"

### What is actually being proposed
Freeze AP-1's `4×3` grid (prompt {128,512,2048,4096} × output {64,256,512}), hold out
`(512,256)` and `(4096,512)`, collect **one magnitude/null-ladder window + one grid
window per model = 3 additional quiet windows**, ~120–160 science bundles, fit the
additive categorical model on training cells, evaluate holdouts once.

### The one genuinely good idea in this document
The **magnitude/null-ladder window** is the sharpest thing either open-explore session
produced, and the proposal does not seem to know why. A detection floor in this project
is bound to *"one declared condition family: the same telemetry backend, metric, window
type, **workload profile**, and stack identity"* (`draft-v1.md:60`). Taken literally,
each of 12 (prompt,output) cells per model is a distinct condition family → **24 floor
cells**. D-117 spends **three full windows and ~9.2 h to mint four**. At that exchange
rate a floor-per-cell grid is ~18 windows, and both Q4 proposals in this portfolio are
dead on arrival.

The escape hatch is exactly the null ladder: `draft-v1.md:148` already specifies
*"Null response across magnitudes — identical A=B ABBA blocks at short, medium and long
output magnitudes"* as instrument characterization, currently **[PENDING WINDOW C]**.
That is the empirical license to transport one comparative floor across the grid's
magnitude range. Proposing it as window 1 of the campaign is correct engineering and
folds an unfunded draft placeholder into a funded campaign. **Credit where due.**

### Fatal-flaw candidates

**FF1 — "Prediction" is the wrong word and the title inherits the error.**
The bank's model is **categorical**: `E = fixed + prompt_level + decode_level`. The
holdouts `(512,256)` and `(4096,512)` are unmeasured *combinations of measured levels*.
The study therefore tests **additivity / absence of interaction**, and predicts nothing
outside the grid. "Predicting Request Energy from Prompt and Output Shape" promises a
scaling law it cannot deliver; a referee will call this out in the first paragraph.
Contribution 4 ("labels predictions outside the measured grid unsupported") shows the
author knows — which makes the title a choice, not a slip. **Retitle around additivity.**

**FF2 — Window budget is optimistic against the only calibrated evidence.**
D-117's own budget table (memo §Runtime evidence, `:327`) gets **50 science bundles into
3.14 h** using 1.5B 128-prompt/512-output members at 92.7 s and 7B at ~97 s. The grid's
heavy cells (4096 prompt × 512 output, 7B) are strictly longer than every member those
budgets were built from, and the proposal wants **60 grid bundles per window**. The
proposal's own kill criterion ("dry-run timing cannot fit 60 bundles plus operations and
20% margin") is the right guard, but it is stated as a risk rather than priced — and the
realistic answer is 4–5 windows, not 3. Both Q4 proposals under-book nights; this one
under-books harder because it insists on two models.

**FF3 — Mint machinery is scoped for four cells, not twenty-four.**
D-117 blocker **F2** says the generalized mint is *"decode-only and single-plan/
single-cell"* and needs **pinset v2 + a four-cell aggregate artifact** just to serve
D-117. The Q4 grid needs the same machinery at ~6× the cardinality plus prospectively
frozen acceptance thresholds for every cell before data exists. That desk cost is
invisible in this proposal. It is not fatal, but "three additional quiet windows" is not
the true cost — the true cost is dominated by desk, and the proposal's own
"HARDWARE/VENUE/RISKS" paragraph never says so.

**FF4 — Ambiguity on where model size enters.** 24 cells is 12 per model × 2 models, but
the model is written as `fixed + prompt_level + decode_level` with no model factor. Fit
per-stack (as the repo-sourced sibling proposal does) or add a factor — unspecified, and
it changes both the df budget (10 training cells, 6 parameters, 4 residual df is already
thin) and the floor story.

### Feasibility vs the ~5 J bar and the two gates
Magnitudes are not the problem and are correctly sized. Decode 64→512 at
0.098 J/token (1.5B) → 43.9 J and 0.376 J/token (7B) → 168 J: both ≫ 5 J. The proposal's
"~40 J / ~165 J" is slightly conservative and flagged uncertain — acceptable. Prefill
128→512 ≈ 5 J is genuinely marginal and 128→2048 ≈ 24 J clears. The **residual /
interaction** term is the quantity that may sit under the floor, and the proposal handles
that correctly ("additive at this instrument's resolution, not mathematical exactness").
Gate discipline is honest throughout. **This is a competent instrument-aware design.**

### Venue-fit honesty
Overstated by omission. The roadmap's ICPE-full row requires *"C1–C8, cross-day
stability, artifact-ready release, **and at least one** deeper contribution: held-out Q4
prediction, second-unit replication, or a successful mechanism study."* Q4 is one of
three alternatives for the *last* item, not the ticket. Calling it "the strongest ICPE
full-paper direction" without stating the C8/stability/artifact prerequisites is the
kind of half-truth that gets a proposal funded and then stranded.

### Overlap flags
- **prefill-scaling-laws** — SEVERE. The prompt axis {128…4096} × prefill energy *is*
  that direction's core, and both draw on the same 2026-08-07 sizing desk check.
- **long-generation-dynamics** — MODERATE. Shares the output axis {64,256,512}, though
  that direction is within-request position effects, not cell-level totals.
- **mvp-icpe-upgrade** — SEVERE. The roadmap names Q4 held-out as *the* ICPE upgrade;
  that directed proposal will almost certainly propose this same grid.
- **param-scaling-energy** — MILD. Two-model factor overlaps its 0.5B–14B ladder.
- **kv-context** — MILD, via the 4096-prompt cells.

### Scores
novelty **5** · feasibility **6** · mvp_leverage **9** · venue_fit **8** ·
original_goals **5**

### Verdict: **VIABLE** (strong design, unoriginal selection, under-booked)
Fund the *design* — specifically the null-magnitude-ladder window, which should be
extracted and funded regardless of what happens to Q4, because it discharges
`draft-v1.md`'s [PENDING WINDOW C] rows. Do not fund this as a separate portfolio
direction; it belongs inside `mvp-icpe-upgrade` / `prefill-scaling-laws`.

---

## Idea 2 — "Cache Once, Pay Once? A Calibrated Prefix-Reuse Crossover"

### What is actually being proposed
Promote the July KV spike 3.0.1 (`docs/stream_logs/2026-07-07-kv-spike-301/`,
`verdict: replay_supported`) into claim-grade energy science: cold-prefill vs
cache-assisted request at 1024/2048/4096 prompt tokens, 64 greedy output tokens,
~135 members across 2 windows, solving `E_build+save + k·E_cached < k·E_cold`.

This is the only idea in either open-explore proposal that is not a transcription, and
it mines a real, verified, otherwise-idle repo asset. That earns it a serious read.

### Fatal-flaw candidates

**FF1 (BLOCKER) — the headline crossover is arithmetic, not measurement.**
`E_build` is not a small extra cost; **`E_build` is the prefill itself**. Substituting
`E_build ≈ E_prefill`, `E_save ≈ 0`, `E_cold ≈ E_prefill + E_decode`,
`E_cached ≈ E_decode`, the inequality collapses to
`E_prefill + k·E_decode < k·E_prefill + k·E_decode` → `k > 1`.
The crossover is at **k = 2 by construction**, on any hardware, with no measurement.
The only way the experiment moves that number is if cache load or altered execution
costs something — and the proposal's own evidence says those cost **0.4 ms load and
14–28 ms save**, i.e. ≲0.9 J at ~33 W, an order of magnitude **below the ~1 J
attribution limit** and two below the ~5 J bar. So the single empirically interesting
parameter in the paper is provably unresolvable by this instrument *before collection*.
The proposal half-admits this ("tiny subcomponents may be reported unresolved") without
noticing it has just conceded the thesis. What survives is a real but thin finding:
*"prefix reuse recovers essentially the whole prefill; the overhead is below our
detection floor."* That is one figure and a paragraph, not a paper — unless it is
reframed as a **null/refusal result about cache-overhead invisibility**, which would
actually be publishable in this project's idiom.

**FF2 (BLOCKER, unflagged anywhere) — the cached arm's real cost falls partly OUTSIDE
the named measurement boundary.**
The spike's cache is **58.7 MB** (`cache_bytes_measured: 58725623`). Putting cache load
inside the measured request boundary — which the proposal explicitly requires — means the
cached arm performs a ~59 MB NVMe read that the instrument attributes to the request.
But `draft-v1.md:11` fixes the boundary as *"internal to the named `powermetrics`
system-on-chip boundary"*: SSD controller and NAND energy is **not on the SoC rails**.
The contrast therefore has a **systematic bias in favour of caching** whose size the
instrument cannot see, on a project whose entire thesis is naming your boundary
honestly. Nobody in this proposal, or in its sibling, flags it. This is not
unfixable — it is a limitations paragraph, a `dd`-style desk estimate, or exactly the
case where the borrowed WT310E earns its keep — but shipping it unflagged would be the
worst kind of own-goal for a paper about measurement honesty.

**FF3 — magnitude at the anchor length is marginal, and the proposal's own bar is
wrong.** The kill criterion is "less than ~8 J at 1,024 tokens". But the effective bar
in this project is `floor + claim-side bound` (`draft-v1.md:109–115`), and the *minted*
1.5B decode floor is **7.38 J** (advisor brief). A gross-request floor for a new
condition family will be of that order or larger. 12.8 J projected at 1024 tokens is
~1.7× a 7.4 J floor before the claim-side bound is added — the same marginality profile
as the 128-token prefill contrast that D-117 flagged as marginal at 5.81 J. **The 1024
arm should be presumed unresolvable and the design anchored at 2048/4096** (25.5 / 51.1 J),
which are comfortable. Anchoring the "crossover" story at the length where the
instrument is weakest is the design error.

**FF4 — stack-pin risk.** The spike ran `mlx_lm 0.31.3` / `mlx 0.31.2` on 2026-07-07.
Prompt-cache file format is not a stability-guaranteed surface; a version change between
spike and campaign can silently break replay or, worse, change cache contents while
`tokens_identical` still passes. The proposal's kill criterion covers token identity but
not cache-format identity across the pinned stack. Add a cache-bytes/hash reproduction
check to the desk gate.

### Feasibility, cost, gates
Two windows / ~135 members is plausible at 64-token outputs (cheap members), and this is
the *least* window-hungry idea in either document. Desk cost is real but bounded: new
condition family, cached workload profile, manifest, custody for the cache artifact.
Single-request boundary is genuinely preserved — one request per bundle, no concurrency.
Good discipline.

### Venue-fit honesty
The most honest venue paragraph in either proposal: capstone chapter → ICPE
Emerging/EuroMLSys, "full ICPE becomes plausible". Correctly humble.

### Novelty
Prefix/prompt-cache reuse is thoroughly known in the serving literature (vLLM prefix
caching, SGLang RadixAttention); the novel wrapper is *energy*, *on-device*, *phase-
resolved*, *with a published floor and a refusal for the sub-floor overhead*. That is a
genuine delta, and no directed pool member covers it: `kv-context-energy` is assigned
"decode energy per token as a function of resident context length" — a growth-of-KV
question, not a reuse-economics question. **This is the only genuinely new idea in
either open-explore proposal.**

### Overlap flags
- **kv-context-energy** — PARTIAL (shared KV/cache subject matter, different question).
- **prefill-scaling-laws** — MILD (uses the same 1024/2048/4096 prefill ladder as its
  magnitude source).
- Otherwise clear of the directed pool.

### Scores
novelty **6** · feasibility **6** · mvp_leverage **7** · venue_fit **6** ·
original_goals **7**

### Verdict: **VIABLE** — keep alive, but only after a desk resolution of FF1+FF2
The idea survives only if reframed away from "where is the crossover" (arithmetic)
toward "what does prefix reuse cost that the instrument cannot see" (a boundary and
refusal result), with the off-SoC I/O flaw stated up front and the anchor moved to
2048/4096. In that form it is a legitimate short paper and the closest thing in this
portfolio to Ed's original KV/mechanism axis.

---

## Idea 3 — "Two Boundaries, One Verdict: Validating `powermetrics` Against Wall Power"

### Assessment
Technically the most competent of the three write-ups and the least useful to this
portfolio, because it is a **direct duplicate of the directed
`wall-meter-validation` proposal**, which was commissioned with a sharper brief
("what it adds, what it can never validate"). Funding both is waste; the directed one
should own the axis.

**Genuinely good technical point (worth transplanting into the directed proposal):**
*"The existing ~5 J phase-contrast sizing bar does not automatically govern the external
meter; a new paired meter/synchronization floor does."* Correct, non-obvious, and
exactly the kind of thing a careless version of this paper would get wrong by reusing
the 5 J number out of context. Likewise the discipline that a sub-floor residual licenses
only *"no boundary difference resolved,"* never equivalence.

### Fatal-flaw candidates

**FF1 — the instrument does not exist and its acquisition is not a task anyone owns.**
`TASK_QUEUE.md:327` still lists **P1-003** as `READY [ED-EXTERNAL]` — *record the
wall-meter decision: meter make/model or unavailable verdict*. Not "borrowed", not
"pending": **undecided, and blocked on Ed**. The importer (`P2-048`) is **SHELVED**,
trigger = P1-003. So the whole idea is downstream of a decision that has sat unmade, and
the proposal presents it as a scheduling matter. Its kill criteria are all
*post*-borrow (calibration status, cadence, fixture, sync bound); the *actual* first
kill gate is "does Ed have the unit at all." The roadmap prices this honestly at
**4–8 weeks**; this proposal does not price it at all.

**FF2 — HotCarbon fit is overstated.** The roadmap says plainly: *"HotCarbon needs a
stronger sustainability-metrics argument."* A rail-vs-wall agreement study is a metrology
paper; citing the HotCarbon CFP scope does not make it a sustainability contribution.
EuroMLSys or ICPE is the honest read, which the proposal also gives — so this is
padding, not deception, but a referee notices padding.

**FF3 — the held-out design is under-specified where it matters.** "Reserve one workload
family as the held-out bridge test" across only **four active levels** leaves three
training levels to fit a paired regression with a held-out check. That is not a
regression; it is three points and a hope. Either widen the level set or drop the
held-out framing and call it a paired-agreement study with a stated residual bound.

**FF4 — battery neutralization is named but not solved.** On a MacBook the AC-side
measurement includes charging current. "Battery-charge neutralization" appears as a
requirement in both the kill criteria and the capability list, but the repo has no
mechanism for it, and it is the single most likely reason a first pilot produces
unusable data. It deserved a paragraph, not a noun.

### Feasibility vs the bar
Workload magnitudes (47–200 J) are comfortable. The scientific target — the wall-minus-SoC
residual and any boundary-dependent contrast flip — is explicitly acknowledged as
possibly sub-floor, with correct refusal semantics. Honest.

### Overlap flags
- **wall-meter-validation** — **TOTAL DUPLICATE**. Do not double-fund.
- **floor-methodology-general** — MILD (the new paired-meter floor is a floor-composition
  contribution).

### Scores
novelty **4** · feasibility **3** · mvp_leverage **8** · venue_fit **7** ·
original_goals **3**

### Verdict: **WEAK** — redundant and hardware-blocked
Kill as a portfolio entry; transplant the "new paired floor, not the 5 J bar" point and
the equivalence-refusal language into the directed `wall-meter-validation` proposal.

---

## Cross-cutting

1. **Existing-material compliance: PASS on all three.** Nothing here abandons the
   instrument or invents apparatus without a path. The hard constraint was respected.
2. **Original-goals service: weak overall.** Idea 2 touches the KV/cache axis; Ideas 1
   and 3 admit they serve no mechanism. Nothing here advances spec-decode, MoE, MTP, or
   split inference.
3. **The unmined assets.** For a session told to originate, the repo's most under-used
   claim-grade assets went untouched: the **refusal log** as a corpus, the
   **contamination events** (the 43/50 screensaver-contaminated bundles; the two live
   contamination catches in the 7B window), the **drift/bracket corpus**, and the
   **pulse-train calibration corpus** itself. Idea 2 is the one asset-mining move and it
   is the best thing in the document.
4. **Duplication with the sibling open-explore session.** Ideas 1 and 3 are the same
   ideas as `prop-open-explore-repo.md` #2 and #3. Two independent open-ended sessions
   converging on the repo's own ranked roadmap is informative about the roadmap's
   quality and uninformative about the design space.
