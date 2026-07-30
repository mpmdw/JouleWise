# Related-work sweep — CV / publication paths for the capstone (2026-07-30)

**Origin:** delegated literature/landscape sweep, 2026-07-30 — Fable subagent
under the magistrate's 7B-floor-window session
(`abec37a6-31cd-4c56-a8a8-9448acaf12be`), agent `ac7d981331ebbfa4d`. This file is the
agent's final deliverable message, extracted verbatim from the session
transcript; the raw JSONL transcript and the intermediate raw related-work
capture are session-scoped scratch and are deliberately NOT committed.

**Status:** desk research, not project evidence. Nothing here is a JouleWise
measurement, a claim, or a ratified decision. Adopted items become queue rows
or decision-log entries in their own right; see `TASK_QUEUE.md` intake batch
2026-07-30.

---

All questions answered with data. Here is the deliverable.

---

# CV-building paths for the JouleWise capstone: evidence-grounded assessment

## Ground truth gathered (per question)

**1. Workshop venues — do they accept work like this?** Yes, demonstrably.

- **HotCarbon** (co-located w/ major systems conf, papers published archivally in ACM SIGEnergy Energy Informatics Review): 5-page limit, double-blind, explicitly favors papers that "stimulate reflection and discussion" and open lines of inquiry — position papers welcome ([CFP](https://hotcarbon.org/cfp)). The [2025 accepted list](https://hotcarbon.org/2025) (19 papers) includes directly comparable scope and team shapes: *"Energy Efficient or Exhaustive? Benchmarking Power Consumption of LLM Inference Engines"* (4 authors, Texas Tech + LBNL) and *"LLMCO2: Carbon Footprint Prediction for LLM Inferences"* (5 authors, Indiana + Purdue). Small university teams are the norm, not the exception. Acceptance rate is unpublished (flagged: hot-topics workshops of this kind typically land roughly 40–60% — that's a guess). **HotCarbon '26 already happened (July 16–17, 2026; deadline was May 18)** — the target is HotCarbon '27, deadline ~May 2027 (guess from pattern; not yet announced).
- **EuroMLSys** (co-located with EuroSys): 6 pages, single-blind. The [2026 accepted list](https://euromlsys.eu/) includes *"Balancing Compute in LLM Inference: Model Selection, Quantization, and Test-Time Scaling"* — a **single-institution University of Trieste paper reporting energy per output token** — plus edge-inference papers on Raspberry Pi Zero 2W (Keio) and Jetson (FORTH/Crete). JouleWise is squarely in scope and *better instrumented* than several accepted papers. EuroMLSys 2026 deadline was Feb 24, 2026; EuroSys 2027 is **April 19–23, 2027, Rabat** ([2027.eurosys.org](https://2027.eurosys.org/)), so expect a ~Feb 2027 workshop deadline (guess from prior pattern).
- **ICPE** ([2027: May 24–28, Gothenburg](https://icpe2027.spec.org/)): the most metrology-sympathetic venue — it has nine tracks including an **Emerging Research Track** (early-stage, ideal for undergrad-led work) and a dedicated **Artifact Evaluation Track**. All 2027 dates currently TBA (verified on the [important-dates page](https://icpe2027.spec.org/important-dates/)); prior pattern puts research-track deadlines ~Oct–Nov 2026 and emerging-track ~Jan 2027 (guess).
- **CCGrid** ([2027, Dallas-Fort Worth](https://hpcclab.org/ccgrid27/)): full 10-page IEEE papers, **abstract Nov 24 / paper Dec 1, 2026**. Highest bar, most datacenter-flavored — weakest topical fit for consumer-Mac metrology. Lowest priority.

**Signal value:** For **MS/PhD admissions**, a workshop paper is a concrete, verifiable artifact ("you wrote something, submitted it, someone accepted it, you can point to a PDF") that beats "ongoing research" with no output — but should be framed as the opening line, not the headline ([practitioner discussion](https://dev.to/ericwoooo_kr/do-workshop-papers-at-neuripsicml-actually-help-your-phd-application-heres-what-admissions-9dj)). Flagged inference: the advisor's recommendation letter (JouleSort first author, SIGMOD '07) is almost certainly worth more than the venue itself; the paper's job is to give that letter something concrete to point at. For **industry hiring**, a workshop paper alone is a weak-to-moderate signal for SWE roles but a real differentiator for the specific perf/power niche (see Q6).

**2. Artifact badges vs. a good repo.** ACM's [badge system](https://www.acm.org/publications/policies/artifact-review-and-badging-current) (Available / Evaluated / Reproduced) is visible **within the research community** — badges print on the paper's first page and matter to program committees and grad admissions readers who know the system. They are near-invisible to industry recruiters. A solo, well-documented, hash-bound reproducible repo is a *comparable or better* industry signal and a *weaker* academic one (a badge is third-party verification; a repo is self-attestation). Best move: ICPE's artifact track converts the existing repro discipline into a badge nearly for free — the marginal cost over what JouleWise already has (hash-bound repro, pre-registered claims) is packaging, not new work.

**3. Open-source niche — genuinely open, with honest caveats.** The traction landscape:

| Tool | Stars | Notes |
|---|---|---|
| [tlkh/asitop](https://github.com/tlkh/asitop) | ~4.6k | simple TUI powermetrics wrapper — broad dev appeal, zero rigor |
| [CodeCarbon](https://github.com/mlco2/codecarbon) | ~1.7k+ (approx.) | estimates, not measurement; backed by a nonprofit + Mila/BCG volunteers |
| [vladkens/macmon](https://github.com/vladkens/macmon) | ~1.4k | sudoless private-API metrics |
| [ml-energy/zeus](https://github.com/ml-energy/zeus) | **371** | despite an NSDI '23 paper, PyTorch-ecosystem status, Mozilla Fund award |
| [ml-energy/zeus-apple-silicon](https://github.com/ml-energy/zeus-apple-silicon) | **8** | reads IOReport; README *explicitly disclaims* accuracy ("model-based estimates… may be inaccurate"), no calibration, no error bars, tests use mocked data |

The niche check is decisive: **the only existing Apple Silicon ML-energy library openly states it is unvalidated — exactly the gap JouleWise's error budgets and detection floors fill.** No published equivalent of "validated instrument + error budget on consumer Apple Silicon" exists in tool form. Honest calibration on the ceiling, though: Zeus at 371 stars shows that *rigorous* energy tooling has a niche audience; asitop at 4.6k shows the mass audience wants a pretty TUI, not metrology. Realistic outcome for a polished pip/brew "measure your local LLM's J/token, with error bars" tool + strong launch post: a few hundred to ~2k stars if it lands on HN (local-LLM energy is a recurring HN topic — see [threads](https://news.ycombinator.com/item?id=44714213) and posts like [Muxup's per-query energy piece](https://muxup.com/2026q1/per-query-energy-consumption-of-llms)); tens of stars if it doesn't. Star count is a lottery; the *durable* value is a linkable, installable artifact recruiters can run in 5 minutes.

**4. Leaderboard/site path.** The [ML.ENERGY leaderboard](https://ml.energy/) is the proof that such artifacts get cited (it became a **NeurIPS 2025 Datasets & Benchmarks spotlight paper**, is cited by follow-on benchmarking papers, and anchored a NeurIPS tutorial with NVIDIA/Google/Meta). But it is a *funded multi-person lab initiative* (Mozilla Technology Fund, Laude Institute support). A solo undergrad running a continuously-updated leaderboard is a maintenance trap: every new model release creates silent obligation, and a stale leaderboard is a negative signal. The cheap variant that keeps ~80% of the value: a **static results page with error bars** ("J/token for N local models on M-series, with detection floors"), versioned, dated, and linked from the tool README — a snapshot, not a service.

**5. Timing (verified where possible).** Semester calendar vs. deadlines:

- **Now–Nov 2026:** no workshop deadline pressure. Tool release + blog post window.
- **Nov 24 / Dec 1, 2026:** CCGrid 2027 abstract/paper ([source](https://hpcclab.org/ccgrid27/)) — stretch option only.
- **~Oct 2026–Jan 2027 (TBA, guess):** ICPE 2027 research / emerging-research / artifact deadlines.
- **~Feb 2027 (guess from 2026's Feb 24):** EuroMLSys 2027 deadline; workshop late April 2027, Rabat.
- **~May 2027 (guess from pattern):** HotCarbon 2027 deadline; workshop ~July 2027.

Grad-application relevance: for Fall 2027 PhD applications (due ~Dec 2026), only "submitted/under review" status is achievable; for Fall 2028 applications, everything above lands as "published."

**6. What hirers in this niche value — real postings.** This skillset maps onto actual new-grad requisitions, which is unusual and worth exploiting:

- NVIDIA **[AI Inference Performance Engineer — New College Grad 2026](https://jobs.nvidia.com/careers/job/893393884394)** (benchmarking GenAI inference; TensorRT-LLM/vLLM/SGLang).
- NVIDIA **[Power Methodology and Modeling Engineer — New College Grad 2026](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Power-Methodology-and-Modeling-Engineer---New-College-Grad-2026_JR2017486-1)** — "energy modeling techniques for next-gen GPUs, CPUs and Tegra SoCs… energy usage in AI workloads." This is almost literally the capstone as a job description.
- Apple **[Apple Neural Engine Performance and Power Engineer](https://jobs.apple.com/en-us/details/200617651-3956/apple-neural-engine-performance-and-power-engineer)** and **[On-Device ML Performance Infrastructure Engineer](https://jobs.apple.com/en-us/details/200605950/on-device-ml-performance-infrastructure-engineer)** — on-device efficiency on Apple Silicon specifically.
- [EnCharge AI LLM Inference Deployment Engineer](https://builtin.com/job/llm-inference-deployment-engineer/4620026) — inference on energy-efficient accelerators.

Flagged as inference: Anthropic/OpenAI inference teams don't post "energy" in job titles; their postings emphasize inference performance/efficiency generally — the measurement-discipline signal transfers but isn't a keyword match there.

---

## Ranked effort-vs-payoff table

| # | Path | Effort | Industry signal | Grad-school signal | Risks | Calendar anchor |
|---|---|---|---|---|---|---|
| 1 | **Workshop paper: HotCarbon '27 or EuroMLSys '27** (5–6 pp distillation of existing results) | **Low-medium** — results exist; writing + advisor iteration, ~3–6 wks part-time | Moderate; strong for perf/power roles specifically | **Strong** — concrete refereed artifact + anchors the JouleSort-author letter | Unpublished acceptance rates; deadline dates for '27 still guesses; 9–12 mo latency to the workshop | EuroMLSys ~Feb 2027 (guess); HotCarbon ~May 2027 (guess) |
| 2 | **Tool release** (pip/brew `joulewise`, validated, error-bar output) + launch blog post | **Medium** — packaging, API cleanup, docs, launch post; ~4–8 wks; ongoing issue triage | **Strong** — installable, demo-able, fills a verified gap (zeus-apple-silicon: 8 stars, explicitly unvalidated) | Moderate (repo ≠ peer review) | HN launch is a lottery (Zeus: 371 stars *with* an NSDI paper); support burden; macOS API churn across releases | Anytime; ideal Sep–Nov 2026, before paper deadlines |
| 3 | **ICPE 2027 emerging-research + artifact-evaluation combo** | Low-medium (paper) + low (artifact — repro discipline already exists) | Weak-moderate | **Strong** — badge = third-party verification of the repro claims, rare for an undergrad | All 2027 dates TBA; conference-track bar higher than workshops | Deadlines likely Oct 2026–Jan 2027 (guess) — watch [icpe2027.spec.org](https://icpe2027.spec.org/) |
| 4 | **Blog series** (methodology, error budgets, "why powermetrics lies to you") | **Low** — 2–4 posts | Moderate — interview fodder, HN-able, recruiter-legible | Weak alone | None material; low ceiling alone | Rolling; sequence with #2 |
| 5 | **Static results page w/ error bars** (snapshot, not service) | Low (on top of #2) | Moderate — the linkable demo | Weak-moderate | Goes stale gracefully if dated/versioned | With #2 launch |
| 6 | Live maintained leaderboard | **High, unbounded** | Moderate if fresh, **negative if stale** | Weak unless it becomes a paper (ML.ENERGY needed a funded lab to get there) | Perpetual maintenance; solo undergrad vs. funded Michigan lab | — |
| 7 | CCGrid 2027 full paper | High (10-pp IEEE bar) | Weak-moderate | Moderate | Topical mismatch (datacenter focus); earliest hard deadline | Dec 1, 2026 |

## Recommended portfolio: #2 → #1 → #3, in that order

**Ship the tool + blog post first (fall 2026), submit the workshop paper second (winter/spring 2027), convert repro discipline into an ICPE artifact badge if the dates cooperate.** These three compound: the tool release makes the workshop paper *stronger* (reviewers can install what the paper describes — rare and disarming), the paper makes the tool *credible* (the validation story becomes citable), and the badge or well-documented repo covers whichever audience the other two miss. The niche is verifiably open — the only existing Apple Silicon ML-energy library has 8 stars and a README disclaiming its own accuracy — and the exact skillset appears verbatim in current NVIDIA and Apple new-grad/perf-power postings, which is the strongest industry-side evidence found. Skip the live leaderboard (funded-lab economics, solo-maintenance trap) in favor of a dated static results page; skip CCGrid (wrong audience, highest bar, earliest deadline). One deliberate gap to accept: nothing lands as "published" before Dec 2026 grad deadlines, so if Fall 2027 PhD entry matters, the EuroMLSys/ICPE submission should be timed to be "under review" by application season — otherwise the calendar is comfortable.

Sources: [HotCarbon CFP](https://hotcarbon.org/cfp) · [HotCarbon 2025 papers](https://hotcarbon.org/2025) · [EuroMLSys](https://euromlsys.eu/) · [EuroSys 2027](https://2027.eurosys.org/) · [ICPE 2027](https://icpe2027.spec.org/) · [CCGrid 2027](https://hpcclab.org/ccgrid27/) · [ml-energy/zeus](https://github.com/ml-energy/zeus) · [zeus-apple-silicon](https://github.com/ml-energy/zeus-apple-silicon) · [asitop](https://github.com/tlkh/asitop) · [macmon](https://awesome.ecosyste.ms/projects/github.com/vladkens/macmon) · [CodeCarbon](https://github.com/mlco2/codecarbon) · [ML.ENERGY](https://ml.energy/) · [ML.ENERGY Benchmark (NeurIPS D&B)](https://arxiv.org/abs/2505.06371) · [ACM badging policy](https://www.acm.org/publications/policies/artifact-review-and-badging-current) · [workshop-papers-for-PhD discussion](https://dev.to/ericwoooo_kr/do-workshop-papers-at-neuripsicml-actually-help-your-phd-application-heres-what-admissions-9dj) · [NVIDIA inference perf NCG](https://jobs.nvidia.com/careers/job/893393884394) · [NVIDIA power methodology NCG](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Power-Methodology-and-Modeling-Engineer---New-College-Grad-2026_JR2017486-1) · [Apple ANE perf/power](https://jobs.apple.com/en-us/details/200617651-3956/apple-neural-engine-performance-and-power-engineer) · [Apple on-device ML infra](https://jobs.apple.com/en-us/details/200605950/on-device-ml-performance-infrastructure-engineer)