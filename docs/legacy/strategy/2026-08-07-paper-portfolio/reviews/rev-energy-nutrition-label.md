# Counter-review — `prop-energy-nutrition-label.md`

**Reviewer:** Opus 5 counter-reviewer (adversarial charge: kill it)
**Target:** "Before Joules Become Rankings: A Metrology-Complete Energy Label for Consumer LLM Inference"
**Ground truth:** desk checkout at `.../scratchpad/desk` (main), D-117, DESIGN-MEMO, `docs/paper/draft-v1.md`, `CLAIMS_STATUS.md`, `docs/research_question_registry.md`, `docs/research_question_bank.md`

---

## VERDICT: **WEAK**

Precisely: **KILL as a standalone paper in its proposed four-contribution form; WEAK-but-keep as an MVP section + released artifact, with one narrow re-cut worth a workshop/Emerging-track submission.**

It is the only direction in the fan-out that hits Ed's leaderboard/reporting axis head-on at zero marginal quiet-night cost, and it is scrupulously compliant with the existing-material constraint — that is why it does not get a flat KILL. But it is not a second paper. Stripped of ceremony, its four contributions reduce to: a schema whose every field is *already mandated in the MVP draft* and ~70% covered externally by MLPerf Power / SPECpower / AI Energy Score; a comparability rule ~65% covered by AI Energy Score's own same-hardware/same-task/same-size-class procedure; a re-rendering of the MVP's own D-117 results; and a 40-row audit dominated ~19× in scale by a June-2025 754-model audit, whose conclusion is known before it runs. A May-2026 position paper already occupies the genre. What genuinely survives is **one field and one rule** — the detection floor and the claim gate that refuses directional language below it.

### Scores (1–10)

| Axis | Score | One-line |
|---|---|---|
| Novelty | **2** | Every schema field is already in MVP draft §§1,3–6, and externally the label is ~70% covered by MLPerf Power + SPECpower + AI Energy Score, the comparability procedure ~65% covered, and the audit dominated 19× in scale by an existing 754-model audit. A May-2026 position paper already occupies the genre. Survivor: one field and one rule. |
| Feasibility | **6** | Zero extra nights is real and good. But the cost is misstated by the repo's own sizing, the two-coder audit is unstaffed, and the whole paper is a hostage to all three D-117 windows passing. |
| MVP leverage | **6** | Maximum possible reuse — which is precisely the problem: total reuse with near-zero incremental yield is a duplicate-publication hazard, not leverage. |
| Venue fit | **3** | Self-assessment is commendably honest in tone, but contradicts the project's own venue table: CSCSU's 5-pages-including-references budget makes the "§§2–6 reused nearly intact" plan physically impossible, no workshop is named (EuroMLSys/HotCarbon are already identified in-repo), the invented ICPE-full criteria do not match the roadmap's, and the dual-submission collision with the MVP paper is never mentioned. |
| Original goals | **7** | Best-in-class on the reporting axis — but delivers only the prohibitive half of the critique ("you may not compare") with no constructive bridge, and serves no mechanism axis. |

---

## FATAL FLAWS

### F1 — Contribution 1 is a table of contents for the MVP paper. (decisive)

The proposal's headline contribution is "a falsifiable minimum reporting schema" binding: *boundary, gross-J/request estimand, workload, phase, physical unit, OS/runtime/model/quantization/tokenizer identity, calibration bracket and status, floor decomposition, claim interval, gate verdict, custody digest.*

Every single one is already mandatory in `docs/paper/draft-v1.md`:

| Proposed "new" field | Already mandated at |
|---|---|
| measurement boundary | §3 "Measurement model and boundary"; §6 final para |
| gross-J/request estimand | §1: "Gross joules per request are the primary energy metric" |
| workload / phase | §3 (runtime-emitted phase events) |
| physical unit, OS build, runtime/library versions, model artifact hash, quantization, tokenizer identity, sampler policy, telemetry backend | §6 final para — verbatim list, with "Silent omission is not permitted" |
| calibration bracket + status | §3 "The pre- and post-window calibrations form a bracket…"; freshness/authentication rules |
| floor decomposition | §4 + the **LABELLED** publication path (corner-widened value, `floor_source`, decomposition required) |
| claim interval + gate verdict | §4 "effective clearable effect = F_cell + B_claim"; "reported as *not resolvable*" |
| custody digest | §5 "Cryptographic hashes bind those files to the campaign manifest" |

Coverage is 13/13. Contribution 1 contributes **zero novel fields**. What actually remains is serialization + a validator — engineering, not a scientific contribution. A referee who reads both documents will say this in one sentence and it will end the paper.

### F2 — Salami slicing / duplicate submission, unaddressed.

The proposal states it "reuses the MVP draft's Sections 2–6 nearly intact" and consumes the identical D-117 dataset. Relative to the MVP paper it therefore has **no new measurements, no new method, and no new data** — only a new output format for the same numbers. Two papers sharing §§2–6 near-verbatim and one dataset, submitted to a capstone and then ICPE, is a live ACM prior/concurrent-publication problem. The proposal never names the risk, never proposes a partition of contributions, and its "what is new" list (schema, comparability rules, mutation evaluation, audit) is exactly the list F1 just dissolved.

### F2b — Novelty against external prior art, using the project's own related-work section.

I do not need an outside literature search to establish this; the MVP draft convicts the proposal. Draft §2 and §8 state that **MLPerf Power and SPEC already require** "a qualified analyzer, uncertainty evaluated at the observed load, fixed measurement ranges, synchronized clocks, sufficiently long intervals, invalid-sample accounting, and explicit treatment of battery-backed systems," and that their governing principle is precisely *reject-on-missing-evidence per run*. Map that onto contribution 1:

| Label field | Covered by MLPerf Power / SPEC? |
|---|---|
| measurement boundary (SUT definition) | **yes** |
| calibration/qualification state | **yes** (qualified analyzer, fixed ranges) |
| uncertainty interval | **yes** (uncertainty at observed load) |
| stack/system identity | **yes** (submission descriptor) |
| workload identity | **yes** |
| invalid-sample / validity accounting | **yes** |
| phase (prefill/decode) identity | no — but this is the MVP's contribution, not the label's |
| detection-floor decomposition | **no** |
| explicit gate verdict / refusal of direction | **no** |
| custody digest | partial (submission bundles) |

So on the repo's own related-work text, the genuine novelty of the schema is **three fields**, two of which (floor decomposition, gate verdict) are the MVP paper's own C-ii and one of which (custody digest) is its C-iii. The label contributes the *serialization*, not the *fields*.

### F2c — External prior-art survey: worse than F2b. (novelty 3 → 2)

A dedicated literature sweep confirms and deepens this. Coverage of the proposed fields:

| Proposed label field | External coverage |
|---|---|
| measurement boundary | **~90%** — MLPerf `power_measurement.adoc` (SUT = everything LoadGen sensitizes, measured AC-side at the wall); SPECpower run/reporting rules; **ISO/IEC 21031:2024 (Software Carbon Intensity)** mandates a declared boundary + functional unit; AI Energy Score declares GPU-only |
| stack identity | **~95%** — SPECpower's rules are *strictly more exhaustive* (CPU/mem/storage/NIC/PSU, OS+JVM versions and flags, firmware, every power-management setting, non-default tuning with justification); MLPerf `system_desc` + `power_settings`; Model Cards |
| calibration state | **~75%** — SPECpower requires **annual NIST-traceable calibration**, an accepted-analyzer list, crest factor ≥3 |
| uncertainty interval | **~55%** — SPECpower (**2008**) mandates ≤1% average uncertainty and **no more than 5% of samples above 1%** |
| claim verdict | **~25%** — SPECpower gates *run validity* (invalid runs cannot be published); MLPerf and AI Energy Score gate *comparability by configuration partition* |
| custody digest | **~50%** — MLPerf's compliance checker computes client/server source and results checksums and validates the full PTD transcript; AI Energy Score requires an unaltered-logs attestation |
| **detection floor** | **~5% — this, and only this, is the contribution** |

Three specific threats the proposal must survive and never mentions:

1. **AI Energy Score** (Hugging Face + Salesforce + Cohere + CMU; launched at the Paris AI Action Summit, 10 Feb 2025). A *literal energy label with a literal label generator*: model, Wh/1,000 queries, task, scoring date, benchmarking hardware, 1–5 stars, verification link — **plus an explicit comparability decision procedure** (same hardware/H100, same task, text generation only within size class; alternative hardware permitted but ineligible for the leaderboard) **plus a custody attestation**. It lands on contributions 1 *and* 2. The "energy nutrition label for AI" framing is occupied.
2. **"Position: LLM Inference Should Be Evaluated as Energy-to-Token Production"** (arXiv:2605.11733, **May 2026**) — a position paper prescribing mandatory reporting fields for LLM inference energy. Nearest competitor in genre *and* recency; three months old. Must be cited and differentiated in the abstract or the paper is dead on arrival.
3. **Papadopoulos et al., "Methodological Principles for Reproducible Performance Evaluation in Cloud Computing"** (SPEC-RG-2019-04 / IEEE TSE 2021, ICSE 2020 Journal-First) — eight principles, a decision procedure, and an audit of an existing benchmark against them, from **SPEC's own research group**. The exact structural analogue of this entire proposal. Cite it or be caught. (Adjacent: Raasveldt et al., "Fair Benchmarking Considered Difficult", DBTEST@SIGMOD 2018 — a pitfalls-and-detection paper with no new system.)

Contribution 2 survives **only** if its gating predicate is the floor/uncertainty rather than configuration equivalence. That distinction is the paper's whole spine and the proposal never states it.

*Favourable finding, and it cuts against this paper:* the sweep found **no peer-reviewed validation of Apple `powermetrics` accuracy** — only Apple's own "estimated and may be inaccurate" man page, the ml-energy/zeus RFC #159 thread, community IOReport findings (1 mJ resolution; sub-10 ms windows dominated by quantization noise), and "Apple vs. Oranges" (arXiv:2502.05317) using it while flagging its imprecision. That void is real and citable — but it is **the MVP paper's** novelty, not the label paper's. Which is F1 again.

### F2d — Contribution 4 is dominated ~19× in scale by an existing audit.

- **Luccioni, Gamazaychikov, Alves da Costa, Strubell, "Misinformation by Omission"** (arXiv:2506.15572, June 2025): **754 models, 2010–Q1 2025**, three-level Direct/Indirect/No-Disclosure taxonomy, OpenRouter usage-weighted (84% of token traffic served by No-Disclosure models).
- **Luccioni & Hernandez-Garcia, "Counting Carbon"** (arXiv:2302.08476): **95 models**.
- **BetterBench** (NeurIPS 2024 D&B): AI benchmarks scored against **46 criteria**.

"Approximately 40 rows" is a pilot, not a study. Defensible *only* if reframed so the **instrument** — scoring against fields nobody else checks (floor, calibration bracket, custody) — is the contribution and n=40 is a stated limitation, not a headline. Two flagged unknowns that could make this worse and need a targeted read before funding: **AI-CARE** (arXiv:2602.16042, Feb 2026, "carbon-aware reporting evaluation metric") could not be characterized past its abstract and may collide head-on; and the **NREL "Beginner's Guide to Power and Energy Measurement and Estimation for Computing and ML"** (arXiv:2412.17830, Dec 2024) already covers at-the-wall vs. on-device boundaries, sampling strategy, and common error sources, closing with a call for "measurement methods and standards for facilitating robust comparisons" — i.e. it published this proposal's motivation twenty months ago.

### F3 — The audit cannot fail, and its sample is rigged.

Contribution 4's stated falsification condition: *"the critique fails if prevailing reporting already supplies the proposed mandatory evidence reliably."* Nobody publishes a corner-widened detection floor with a two-gate claim verdict and a custody digest, because nobody built JouleWise. The disconfirming outcome is foreknown to be impossible. Two coders and a κ statistic applied to a foregone conclusion is bookkeeping dressed as an experiment.

Worse, the sample is drawn from "the four nearest reporting systems discussed in the MVP draft" — i.e. TokenPowerBench, ML.ENERGY, Silicon Showdown, Intelligence-per-Watt: the four the MVP already criticizes for exactly these omissions (draft §2.3, §8.1). Auditing only your own straw men and excluding the strongest-practice reporters (MLPerf Power inference-power submissions, SPECpower results, HuggingFace/Salesforce AI Energy Score) is selection on the outcome — the precise sin §5 of the MVP draft forbids in collection. The paper preaches pre-registration and then proposes "approximately 40 result rows" with no frozen sample, no frozen selection rule, and no named second coder.

### F4 — "Base paper cost is exactly the three D-117 windows" is false by the repo's own numbers.

`docs/research_question_bank.md:1087` sizes the nearest existing item — **"Bundle contract as a standards contribution — the run-bundle layout + boundary table + strict validator packaged as a proposed artifact format for edge-LLM energy (MLPerf-Power-adjacent)" — at ~15–30 person-days**, and that is the *export* alone. The proposal additionally requires: machine-readable + human-readable renderer, completeness validator, comparability validator, a mutation-test suite with four named refusal classes, byte-linked artifact→label provenance, and a two-coder 40-row audit. Claiming zero marginal cost because no new night is needed conflates the scarce resource (nights) with the actually-binding one (Ed's desk hours), which the DESIGN-MEMO already shows is the critical path: gates U1–U7 (ledger session/binding, successor builder, pinset v2, multi-cell mint, prefill metric support, three-window regression, campaign packs) must all land *before* alpha runs.

Compounding this: "no hand-copied scientific numbers and byte-linked provenance" implies the renderer hooks the governed mint chain — `scripts/mint_floor_artifact_generalized.py` / `joulewise/detection_floor.py`, i.e. **U3, on the D-117 critical path**. The proposal never specifies whether the label layer is upstream (critical-path-perturbing) or a downstream read-only consumer of minted artifacts. That ambiguity is the difference between "free" and "delays the three windows."

### F5 — Governance-fence collision, unacknowledged.

The registry already carries this direction: **`APP-STANDARDS-CONTRIBUTION`** — status *candidate*, claim ceiling *"methodology artifact proposal"*, explicit fence: **"no claim to be the standard."** The proposal cites neither the row nor the fence, and titles itself *"A **Metrology-Complete** Energy Label"* with contribution 1 phrased as "A result is complete **only if** it binds…". That is a claim to *be* the standard, in the title and the first contribution.

Adjacent fences it also walks past: **`APP-MODEL-CARDS`** — "internal only until L4 replication… public version is killed until cross-lab replication"; and **C5-3.5** (`docs/research_question_bank.md:1050`), which the bank states "**gates every public-facing application (leaderboard, standard, audit service)**." A proposal whose whole selling point is existing-material compliance should have found the two registry rows that fence it.

### F6 — A standard nobody else can satisfy is a description of an instrument, not a standard.

The mandatory fields include an in-window bracketed pulse-train calibration status, a corner-widened attribution-limited detection floor, and a custody digest. On an nvidia-smi or RAPL setup, three of the twelve fields are not merely *absent* — they are **unproducible**. The paper proposes a universal reporting minimum derived from n=1 lab, n=1 machine, n=1 stack, and never tests whether the schema degrades gracefully anywhere else. The audit measures whether published rows *have* the fields; it never measures whether they *could*. External validity is the load-bearing question for any standards paper and this one does not ask it.

### F7 — Correlated single point of failure with the MVP.

All four label cells (1.5B/7B × prefill/decode) and the contrast verdict depend on alpha, beta, **and** gamma all passing. The same failure kills the MVP paper's §7. There is no degraded-mode plan: no "what the paper is if gamma refuses," no fallback to labels-over-refusals. Ironically, a refusal-rendered label would be the most interesting artifact the paper could produce, and it is not planned for.

### F8 — Precision failures inside a paper about precision.

- "**Five real label cells** plus a contrast verdict" — D-117 yields **four** cells (DESIGN-MEMO §"four-cell artifact", rows at lines 147–149) plus one contrast. The paper miscounts its own results in its contribution list.
- "approximately 40 result rows" — an unfrozen n in a paper whose thesis is pre-registration.
- The 141.29 J figure and the 5.81 J / ~4.0 J-lower-edge prefill numbers are correctly sourced and correctly labelled diagnostic (`CLAIMS_STATUS.md:63`; prefill SYNTHESIS). Credit where due — the factual base is clean. The 3.14/3.24/2.80 h budgets, 10+40 schedule, and 50-unique-bundle shape all reconcile with DESIGN-MEMO lines 259–271, 327.

### F9 — Venue analysis contradicts the project's own venue table, and the page budget makes the reuse plan physically impossible.

`docs/strategy/2026-08-06-impressiveness-roadmap.md` §"Venue ambition" already fixes the ladder with cited page limits:

- **CSCSU: 5 pages *including references*.** The proposal's core mechanism — "reuses the MVP draft's Sections 2–6 nearly intact" — cannot be executed twice inside 5-page budgets. At the capstone venue there is room for one paper, and §§2–6 are already spoken for. The reuse plan is not merely redundant; it does not fit.
- The roadmap names **EuroMLSys (6 pp excl. refs) and HotCarbon (5 pp excl. refs)** as "the natural near-term research target," and notes HotCarbon "needs a stronger sustainability-metrics argument" — which is arguably what a reporting-standards paper *is*. The proposal says "credible performance- or sustainable-systems workshop paper" and names **no venue at all**, missing the one the project already identified as its best fit.
- **ICPE full track**: the roadmap enumerates the qualifying deeper contributions — "held-out Q4 prediction, second-unit replication, or a successful mechanism study" — on top of C1–C8, cross-day stability, and artifact-ready release, at 28% acceptance. **A reporting label is not on that list.** The proposal invents its own ICPE-full criteria ("executable validator, reporting audit, artifact-quality release, and preferably external adoption") and then gates on external adoption, which is unreachable in a capstone timeline and is in any case fenced by C5-3.5.
- Roadmap **rank 3, "Artifact-evaluation-quality release" (4–6 weeks, 0 measurement nights)**, already covers the validator/renderer/reproducible-provenance work, and ICPE runs a dedicated artifact-evaluation track aligned to it. The proposal re-derives a large part of rank 3 as a novel paper contribution without citing it.

**Partial correction in the proposal's favour, which it did not claim for itself.** On the charge's question (a) — *can a standards paper without new measurements carry weight at the target venue?* — the answer is **yes, but only in the right track**. ICPE's **Emerging Research track** explicitly solicits "new ideas and vision papers on emerging research challenges" and states that some aspects may "remain open, possibly with limited or no evaluation" (it was formerly the Work-in-Progress and Vision track). **HotCarbon** explicitly solicits "research **and position** papers"; **LOCO** welcomes "new ideas and visions." So the genre is admissible — at Emerging/WIP and workshop tier, which is exactly where the roadmap already placed it and where the proposal declined to look. Two caveats: the **ICPE 2026 cycle has closed** (4–8 May 2026, Florence; research abstracts were due 3 Nov 2025), so the real target is ICPE 2027; and the sweep **could not find a single named ICPE paper that is purely a reporting standard with zero new measurements** — permitted by track scope, but unevidenced by precedent. Do not let that be asserted unsupported.

### F10 — It serves only the prohibitive half of Ed's goal.

Ed wants an *energy-honest leaderboard*. This paper's comparability procedure is a list of refusals: no boundary substitution, no tokenizer-blind J/token ranking, no cross-boundary ranking. It explicitly disclaims public cross-device leaderboards and declares the WT310E "**not a dependency**." Cost-honest, but it leaves the reader with "you may almost never compare" and no constructive bridge to what a *valid* comparison would look like. That reads as nihilism to a systems referee, and it under-serves the very goal the proposal claims to serve best.

---

## STRENGTHENING MOVES (if kept)

**1. Dissolve contribution 1; re-cut the standalone around the floor-gated refusal, not around a label.**
Fold the schema into MVP §6 — where its every field already lives — and release the validator as an MVP artifact. If a standalone is still wanted, build it on the one thing the sweep found genuinely uncovered (~95%): **no existing ML-energy reporting regime states a detection floor or gates a directional claim on it, and the software-counter regimes the entire ML literature runs on (CodeCarbon, RAPL, `powermetrics`) are precisely the ones with no calibration story.** That is **one** contribution, not four. Its comparability rule must be gated on floor/uncertainty, explicitly contrasted with AI Energy Score's configuration-equivalence partition and MLPerf's Closed/Open × Available/Preview/RDI divisions. Title it around refusal ("When Two Energy Numbers May Not Be Compared"), never "nutrition label" — that framing is occupied by a funded four-institution initiative. And import SPECpower's ≤1%-uncertainty / NIST-traceable-calibration rules and the RAPL-validation literature **as the standard you are carrying into a new regime**, not as a gap you discovered. Non-negotiable: cite and differentiate arXiv:2605.11733 (May 2026) and Papadopoulos et al. (SPEC-RG/TSE 2021) in the abstract. This also cures F2 — MVP contributes measurements, this contributes a decision procedure, and the overlap becomes a citation instead of duplicated §§2–6.

**2. Make the audit capable of failing, staff it, and stop pretending n=40 is a study.**
Freeze sample size, source list, and selection rule *before* coding, in the repo, under the project's own pre-registration discipline. Include the strongest-practice reporters (MLPerf Power submissions, SPECpower results, AI Energy Score, MLCommons result JSON) alongside the four weak ones — an audit that excludes best practice is not evidence. Change the scored question from *"is the field present in the row?"* (foregone) to **"is the field *recoverable* from the artifacts the publisher released?"** — recoverability produces a real bifurcation instead of a uniform zero. Position n=40 as an **instrument demonstration** with the sample size stated as a limitation, and cite Misinformation by Omission (754), Counting Carbon (95), and BetterBench (46 criteria) as the scale precedent you are deliberately not competing with — otherwise a referee will do it for you. Read AI-CARE (arXiv:2602.16042) and the NREL Beginner's Guide (arXiv:2412.17830) in full before committing; either could pre-empt this contribution outright. On staffing: name the second coder now; if there isn't one, drop κ, run single-coder, and publish rubric plus full coding sheet so others can re-code — cheaper and more honest than an unstaffed inter-rater claim.

**2b. Pick the venue the project already picked, and the track the genre actually fits.** Target **HotCarbon** (5 pp excl. refs; explicitly solicits position papers; explicitly wants a stronger sustainability-metrics argument — a refusal calculus for energy comparisons is exactly that) or **EuroMLSys** (6 pp). For ICPE, target the **Emerging Research track at ICPE 2027** — it takes vision papers with limited or no evaluation by construction; the 2026 cycle is closed and the full research track's qualifying deeper contributions (held-out Q4 prediction, second-unit replication, mechanism study) do not include this. Send the validator to **ICPE's artifact-evaluation track** as roadmap rank 3, not as a research-paper contribution. Verify ICPE 2027 page limits directly — the sweep could not confirm them.

**3. Buy external validity with hardware that is already idle — the negative-label demonstration.**
The proposal declares the RTX 3080 Ti "irrelevant." That is the missed opportunity. Render a **deliberately incomplete label** for an nvidia-smi measurement on the owned 3080 Ti, showing exactly which mandatory fields cannot be produced on that instrument, and what the comparability gate then refuses when asked to rank it against the M3 Max. This requires no quiet night, no calibration bracket, no floor, no claim — it is a *negative* demonstration, which is the project's native genre. It converts F6 from a fatal objection into the paper's sharpest figure, gives the audit a live worked case, and partially answers F9 by showing concretely what a bridge would have to supply. Failing that, retitle away from "metrology-complete" and adopt the registry's own ceiling language ("a proposed metrology disclosure schema; not a claim to be the standard") to clear F5.

---

## KILL CRITERIA I WOULD ADD

- If a side-by-side of contribution 1's field list against MVP draft §§1,3–6 does not surface **at least three fields the MVP does not already mandate**, the standalone paper is dead on arrival — do not spend desk hours on it. (On my read: zero.)
- If the label serialization touches `mint_floor_artifact_generalized.py` / `detection_floor.py` rather than consuming minted artifacts read-only, kill it until after the three D-117 windows land. Nothing goes on the critical path for a formatting layer.
- If a pilot coding of 8 rows across the four proposed sources yields uniform zeros on the metrology fields, the audit is confirmed unfalsifiable as designed — re-scope to recoverability (move 2) or drop contribution 4.
- **Read arXiv:2605.11733 (Energy-to-Token position paper, May 2026) and arXiv:2602.16042 (AI-CARE, Feb 2026) before any desk hour is spent.** If either already prescribes a mandatory-field set for LLM inference energy reporting with a completeness evaluation, this direction is pre-empted and should collapse to an MVP section immediately.
