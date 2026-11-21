# Related-work literature review: synthesis of two seats (2026-11-07)

**Track:** related-work literature review (audit track, 2026-11-07).
**Synthesizer:** Opus 5.5 (`claude-opus-5-5`), working from two independent seat reports. Seat 1 is Fable 5.1; its longer committed copy is `docs/reviews/2026-11-07-related-work-review-fable.md` on `origin/audit/2026-11-07-related-work-review-fable` at `891b8856c`. Seat 2 is Opus 5.5 and was not committed. Both reports appear verbatim in the appendix.

**Status.** This is an audit deliverable. It is not a paper section, a registration or a claim. Nothing here is a measurement or a Block-5 value. No restricted path (`/Users/edr/jw-b5-*`, `night-*`, custody, archive, `restricted/`) was opened, and nothing here was inferred from Block 5.

**Repo pins.**
- `origin/main` = `bd7a3efcd`.
- ALIGN integrated lane `origin/lane/2026-11-06-v4-r1-integrated` = `e901eb2a4`.
- Latest `docs/align/pilot_protocol_v4.md` = `543c9565d`, which is on that lane and not on `main`.
- Protocol v3 = `83e2dac59`.
- Pilot v0 = `cbfb9b0a5`, on `desk/2026-11-01-align-pilot-v0`.

**How I checked the seats.** I settled every disagreement against the repo or the source, and I re-opened every source that a headline finding rests on. In the source list (§6), **RV** marks a source I re-opened on 2026-11-07 with the specific claim checked. **S1**, **S2** and **S1+S2** mark sources opened only by the named seat(s) and not re-opened by me. **META** means only metadata was verified. **UNVERIFIED** means no one could open the primary source.

---

## 1. Executive summary

- **ALIGN's core question is unoccupied, and the literature on both sides is now mapped.** No source uses measured energy to audit an agent's logged token counts.
  - Hidden-token auditing (CoIn, PALACE, Token Inflation) is entirely software-based.
  - Physical side-channel verification (Gargiulo & Kulp; Kimpson, Baker & Graham; de Almeida) works at workload-class or aggregate-compute scale.
  - Monitoring and control papers price oversight in dollars or task performance, never joules.
  - Agent-energy papers measure joules but never ask a monitoring question.

  The strongest framing is to present ALIGN's H50/H90 known-omission curve as a per-episode, token-level analogue of Kimpson et al.'s β.
- **The seats agree that published Apple-silicon LLM energy work uses `powermetrics` as if it were a meter.** Examples are AgentStop, GreenBench and Hübner et al. Apple's own man page says the values "are estimated and may be inaccurate" and "should not be used for any comparison between devices". Neither seat found an LLM energy study that gates on thermal state.
- **The literature raises two design threats that ALIGN's docs do not yet address. Both were found by seat 2; I verified both.**
  - *Tamper-evidence boundary.* `powermetrics` is software on the same host, and NVML-style telemetry "can be spoofed or replayed". The claim is limited to a non-adaptive adversary.
  - *Possible misspecification.* The five-term residual design assumes full attention, but model D has a hybrid, non-trimmable cache.

  A search of PIPELINE, v3, v4 and `energy_residual.md` finds no text on either threat.
- **The disagreements resolve mostly in favour of the repo.**
  - Seat 1 said `pilot_protocol_v4.md` does not exist. It does exist, on the v4 lane.
  - All four bibliography concerns seat 2 raised against `draft-v1.md` are resolved in the draft's favour by full-text checks: [19] Ruf & Detyniecki exists (HotCarbon '26, paper 17); [20] and [26] support the sentences that cite them; [23]'s "severe underestimate" is in the PDF.
  - Only venue updates remain.
- **The seats overlap on about 30 sources, and the union has 104.** The consolidated list (§6) keeps every source that either seat opened. Three seat claims were corrected (Token Inflation's 1,469% is "up to", not an average; the SHADE-Arena quote; the IPW accelerator list). One source remains UNVERIFIED and is dropped from all findings.

## 2. Decisions needed from the lead

1. **ALIGN threat-model text before the registration cold gate (high).** Should v4 and the ALIGN paper (a) state the privilege boundary (the agent is unprivileged, and `powermetrics` runs as root under the harness), and (b) confine the claim to a *non-adaptive* adversary, as known log omission with joules held fixed? *Recommendation:* adopt both now as wording, and defer an external DC or wall meter. v4's estimand is already non-adaptive by construction (`543c9565d:docs/align/pilot_protocol_v4.md:508-516`), so this changes text, not design. See finding H2.
2. **Hybrid-attention diagnostic (medium).** Should registration add a *print-only* residual variant for D? It would restrict the context-quadratic terms to D's full-attention layers, or use a context-linear form, and report the change in s_r. *Recommendation:* yes, print-only, with no change to the primary fit. See finding M1.
3. **Kimpson-β units (medium).** Should the known-H curve also be printed as hidden work as a fraction of declared work, so reviewers can compare it with Kimpson et al. directly? *Recommendation:* yes, as a print beside H50/H90 (ruling 2, `pilot_protocol_v4.md:611`).
4. **Khiani provenance.** "Blinding the AI Co-Scientist" (NeurIPS 2026 workshop poster, Rohan Khiani) describes hash-frozen registration, structural blindness, two-seat review and an admission gate that refused its own headline analysis twice. That closely matches JouleWise's governance. `git grep` on `origin/main` and a search of commit messages on all branches find no reference to Khiani. Is it independent prior art (cite as a neighbour and differentiate) or connected to this project (cite as source, with disclosure)? Only the lead can answer.
5. **Body edits to `draft-v1.md` §8.** The 2026-08-27 bibliography audit records a frozen body and ten uncited §11 entries pending a magistrate ruling (`bd7a3efcd:docs/paper/bibliography-audit-2026-08-27.md:3-16`). This review gives body uses to three of them: [9] Hübner, [11] AgentStop and [21] Silicon Showdown. Citing them by their existing numbers needs no renumbering. May §8 now take the additions in §5 of this document (a few sentences, plus venue updates for [20] and [22])? *Recommendation:* yes for the venue updates and the three orphans. Other additions should wait for the next paper round.
6. **ALIGN related-work section.** The ALIGN lane has no related-work text; `git ls-tree` on `e901eb2a4` shows no related or literature file under `docs/align`. Should one be started now from §3 and §4 of this document? *Recommendation:* yes, as a lane doc before the registration cold gate reads v4. Point 1's threat text should go in the same doc.
7. **GreenBench critique.** Should the critique of GreenBench's 0.47 W "package" figure rest only on the paper's internal inconsistency, or on a controlled `powermetrics` check on the analysis Air (seat 1's suggestion)? *Recommendation:* internal inconsistency only. The critique needs no new measurement (proportionate care), and the Air must not load weights for this.
8. **Sidedness (lead-owned prereg ruling; confirm "no change").** Seat 1 asked whether the residual test should be two-sided, because sandbagging predicts a negative residual. For v4's registered estimand the answer is no: known-H omission strips logged counts while holding joules fixed, so the residual shift is non-negative by construction, and "H=0 is never a detection" (`pilot_protocol_v4.md:508-514`). The sign question applies only to a future *causal* sabotage estimand or to RQ-ALIGN-METADATA-BASELINE. *Recommendation:* no change to v4. The paper should state the predicted sign for each threat model, and any causal estimand must preregister its sign or be two-sided.
9. **ControlArena (deferred).** Should a later ALIGN block adopt ControlArena settings? Its Inspect sandbox conflicts with the rule that native gates "require no agent session on the measurement Mac" (`pilot_protocol_v4.md:692-693`). *Recommendation:* defer. Nothing in v4 needs it.

## 3. Reconciliation: where the seats disagreed or were wrong, and what I decided

| Item | Seat 1 | Seat 2 | What I checked | Decision |
|---|---|---|---|---|
| `pilot_protocol_v4.md` exists? | Absent from every fetched branch; used v0 | On the v4 lane only, marked DRAFT SKELETON | `git log --all -- docs/align/pilot_protocol_v4.md` finds `543c9565d` on `origin/lane/2026-11-06-v4-r1-integrated`. Header: "DRAFT SKELETON — PROVISIONAL; not registered or authorized to arm" (`:3`). Not on `main` | **Seat 2 is right.** Seat 1's ALIGN notes describe v0: Qwen3-8B-4bit, 12 episodes, and thinking on/off as an open choice. v4 supersedes v0 with D = `mlx-community/Qwen3.8-27B-8bit`, thinking on, Qwen3-30B-A3B anchors, a 1 Hz SMC sidecar and G0/G1/holds (`:64-73`, `:195-201`). Seat 1's gap 7 claim that thinking on/off is an open choice is stale and is dropped |
| [19] Ruf & Detyniecki | Treated as cited, no issue | UNVERIFIED; proposed swapping in Delavande 2601.22362 | The HotCarbon 2026 page (https://hotcarbon.org/2026) lists "The Cost of Context: Profiling the Energy Footprint of Input Tokens in Large Language Models", Boris Ruf and Marcin Detyniecki (AXA), at `/assets/2026/paper-17.pdf`. Text extracted from the PDF: "we isolate the prefill phase by setting the generation length to exactly 1 token"; "each context length is measured in a single run" | **Verified.** The sentence at `draft-v1.md:332` stands, and no swap is needed. Delavande remains a useful extra cite, since it uses the same one-token method with 10 runs after 5 warm-ups |
| [20] NVML cross-check | Already cited, no change | The v2 abstract omits the cross-check that `draft-v1.md:330` relies on | v2 HTML §3.1 (https://arxiv.org/html/2605.11999v2): "The counter updates at about 10 Hz, so every run we report lasts at least two seconds"; "over decode runs, the integrated power samples agree with the counter to within 2%" | **Sentence stands.** The check covers decode runs only, which fits "sufficiently long". Update the venue to PPAM 2026 (v2, 29 Oct 2026) |
| [26] "raise but not lower" | Already cited | Not in the abstract; soften or check | Full text §8 item 5 (https://arxiv.org/html/2605.28873): "recompute δ∗ at ρdeff = max(ρdprior, U95(ρd))… otherwise the pre-registered MDE remains binding" | **Sentence stands.** The max() makes the rule one-way. Optionally cite §8 item 5 |
| [23] Dauner et al. | Possible name collision with Dauner & Socher | Metadata verified; "severe underestimate" needs the PDF | Text extracted from https://hotcarbon.org/assets/2026/paper-46.pdf: on the RTX 4090 the cumulative counter "underestimates integrated NVML power by 95.4% at 0.5ms, 75.6% at 10ms, and 13.3% at 100ms, recovering to within 1.6% only at 1s" | **Verified, and no collision.** The two Dauner papers are distinct works (HotCarbon '26 with Steinberg et al.; *Frontiers in Communication* 2025 with Socher) that share first author Maximilian Dauner (Munich UAS HM). Suggested wording fix at `:326`: it is the *cumulative-energy counter* that diverges from integrated power at short intervals, not polling as such |
| AgentStop, Hübner "new" | Hübner listed as new (S3) | AgentStop recommended as a new citation | `draft-v1.md:370` lists [9] Hübner and `:372` lists [11] AgentStop; neither is cited anywhere in the body (my count over `draft-v1.md` outside §11) | **Both seats missed this.** These are existing orphan entries, so the action is to cite them in the body, not add them (decision 5) |
| GreenBench 0.47 W | "Internally implausible" | "Boundary ambiguity" | Abstract (RV): the M4 Pro "draws only 0.47 W of CPU+GPU package power during sustained inference" and "total system power of 8-12 W" | **Report it as an unreconciled internal inconsistency (17-25×).** Do not assert the true value. Both framings support naming the boundary |
| Token Inflation figure | n/a | "1,469% on average" | Abstract (RV): "up to 1,469%" for hidden reasoning "in the most permissive setting"; 50.85% tokenization over-reporting | **Corrected to "up to"** |
| SHADE-Arena quote | Paraphrase | "depends heavily on a hidden scratchpad" | Abstract (RV): "success on the side task relies heavily on having access to a hidden scratchpad that is not visible to the monitor" | **Use the exact quote** |
| IPW and M4 Max | n/a | "8 accelerators including the Apple M4 Max" | Abstract (RV) names the M4 Max as an *example* local accelerator; v7 comment says NeurIPS 2026 | **Softened**; venue update confirmed |
| AgentStop setup | n/a | M1 Max, 100 ms, trapezoid, ~95 °C, Jetson via tegrastats | The abstract has none of these. HTML §5.3 (RV): M1 Max, macOS 15.6.1, `powermetrics` "every 100 milliseconds", trapezoidal rule, CPU baseline subtracted only in non-GPU phases, no GPU subtraction. Intro: "nearly 95°C, with sustained operation above 90°C". Appendix B lists a Jetson AGX Orin and tegrastats | **Confirmed** except Jetson energy, which is softened to "lists" |
| Søgaard et al. | UNVERIFIED | n/a | arXiv 2302.10086 (RV): EACL 2023 | **Verified** |
| Argerich & Patiño-Martínez | UNVERIFIED | n/a | Crossref 10.1109/ACCESS.2024.3409745 (RV): IEEE Access 12:80194-80207, 2024 | **META** (content not opened) |
| Residual sign / sidedness | Asks for a two-sided test | n/a | `pilot_protocol_v4.md:508-516` | **One-sided is correct for v4's estimand** (decision 8) |
| Threat model (only seat 2 raised it) | n/a | `PIPELINE.md:10-12` claims a measurement outside the agent's reach; on a Mac it is host software | `e901eb2a4:docs/align/PIPELINE.md:9-12`: "Logs, transcripts and monitors are software the agent may be able to reach. The power draw is measured outside it." `/usr/bin/grep -i` for adaptive, privilege, root, external meter, wall meter and spoof over PIPELINE, v3, v4 and `energy_residual.md`: no relevant hits (the only matches are "runs root" as a directory name, v4:262 and :296). Gargiulo & Kulp abstract (RV): NVML "can be spoofed or replayed". Hot Pixels (RV): Apple "allows unprivileged access" to power and temperature through IOReport | **Kept, high** (H2) |
| Hybrid-cache misspecification (only seat 2 raised it) | n/a | Five-term design assumes full attention | `bd7a3efcd:docs/align/council-2026-11-05/FINAL-DESIGN.md:12` ("D's non-trimmable hybrid cache"); `pilot_protocol_v4.md:488-489` design; no architecture-specific term in v4 or `energy_residual.md`. Chkir abstract (RV): "attention mechanism is the primary factor governing how decode energy scales with context length". Ma v2 abstract (RV): "the recurrent architectures pay no prefill penalty" | **Kept, medium** (M1). Fitted coefficients absorb part of the error; the cost is a larger s_r |
| Khiani (only seat 1 found it) | Nearest governance neighbour; provenance? | n/a | NeurIPS virtual page (RV): title, author Rohan Khiani, AI-Native Academia workshop, all four mechanisms confirmed, no energy content. No repo reference | **Kept**; provenance goes to the lead (decision 4) |

**Dropped or downgraded.**
1. Preprints.org 202605.0855: a 403 for seat 1 and for me. Every content claim attributed to it is dropped. It is listed UNVERIFIED in §6.
2. Seat 1's v0-specific relevance notes: thinking on/off as an open choice, Qwen3-8B-4bit and 12 episodes. v4 supersedes them.
3. Seat 2's "on average" for Token Inflation (corrected to "up to").
4. MacCoun & Perlmutter content. Neither seat opened the Nature text: seat 1 read Berkeley News, seat 2 had Crossref metadata. It may be cited as a pointer, but no specific content claim is made from it.
5. Venues that seat 2 says came from its own memory or a search listing rather than an opened page: Splitwise ISCA 2024 (seat 1 gives it with pages 118-132 but did not say where), Weiss et al. USENIX Security '24, TAPAS ASPLOS '25, and Solovyeva & Castor EASE 2026. These are carried as "venue unconfirmed". I confirmed that the Solovyeva arXiv page shows no venue.

## 4. Findings

### High

**H1. ALIGN's energy-as-audit question is unoccupied. Two adjacent literatures bracket it, and the novelty claim should be phrased against both.**
- **Hidden-token auditing is all software.**
  - CoIn (Findings of EMNLP 2026, RV) uses a hash tree over embedding fingerprints and detects up to 94.7% of count manipulation.
  - PALACE (S2) predicts hidden counts.
  - Token Inflation (RV) defeats three audit frameworks, with up to 1,469% inflation going undetected. It recommends "evidence the provider does not control": TEE attestation, proofs of inference, or third-party re-execution.
  - Velasco et al. and "Invisible Tokens" (S2) give the incentive and a taxonomy of audits. That taxonomy has no physical class.
- **Physical verification works at the wrong grain.**
  - Gargiulo & Kulp (RV) separate workload classes from 10 MHz H200 traces with 97% accuracy and macro-F1 0.955.
  - Kimpson, Baker & Graham (RV) define β, the hidden compute a power trace cannot rule out: 1.16 worst case on A100, at least 0.41 against a matched-energy adversary, 0.059 with re-execution.
  - de Almeida (ICML 2026 TAIGR workshop, RV) recognises a training signature.
- **Monitoring and control papers report no compute or energy cost of the monitor.**
  - The TRACE and Async Control abstracts (RV) report none.
  - Control Tax (RV) defines "the operational and financial cost" and does not mention energy.
  - Ctrl-Z and Hua et al. (S1+S2, S2) report cost as performance or budget.
- **Agent-energy papers measure joules without a monitoring question.** Energy per Successful Goal (RV) and Where Does the Energy Go? (RV) are examples.
- **Side channels on LLMs use packets and timing, not power.** Whisper Leak (RV) classifies prompt topics at above 98% AUPRC across 28 models.

*Safe claim, as worded by seat 2 (endorsed):* "a pre-registered test of whether measured energy detects known omissions of reasoning tokens from an LLM agent's log, on local hardware, reported as a detection curve over hidden tokens (H)". It is a per-episode, token-level analogue of Kimpson's β. The identical-work replays (U3, `pilot_protocol_v4.md:419`) and the frozen benign fit play the role of the verifier's re-execution.

*Do not claim:* detection of sabotage as such, robustness to an adaptive adversary, or semantic monitoring.

**H2. Tamper evidence is asserted, but its boundary is not stated.**
- `PIPELINE.md:9-12` presents power as measured "outside" the agent's reach. On a Mac, the counter is host software.
- Gargiulo & Kulp argue that on-chip telemetry can be spoofed or replayed.
- Hot Pixels shows unprivileged *read* access to Apple power and temperature through IOReport. JouleWise uses `powermetrics`, which needs root.
- Kimpson's matched-energy result (β ≥ 0.41) shows that an adaptive adversary who pads logged work elsewhere is outside any trace-only estimand. v4's estimand is explicitly "known log omission, not a causal sabotage effect" (`:513-514`), so it is non-adaptive by construction, but no ALIGN doc says so in threat-model terms.

*Action:* decision 1.

**H3. Apple-silicon LLM energy work uses `powermetrics` as a meter, and no LLM energy study was found that gates on thermal state.**
- The man page (RV) says the values "are estimated and may be inaccurate" and "should not be used for any comparison between devices". The default interval is 5000 ms, and the thermal sampler reports the current pressure, not an integral.
- AgentStop (RV) runs at about 95 °C, with no GPU baseline.
- GreenBench (RV) reports an inconsistent package and system pair (see §3).
- Hübner et al. (S1+S2) show no external validation.
- Hot Pixels (RV) shows that on actively cooled MacBook Pros, temperature and power, not frequency, co-vary with the workload. That is the MBP's regime, so thermal state is an energy confound.
- MELT (S1+S2) and Tummalapalli et al. (RV: the iPhone 16 Pro loses nearly half its throughput within two iterations) show thermal and power policy moving the operating point within seconds.

This supports JouleWise's within-device gross basis (`bd7a3efcd:README.md:63-70`), the floating-battery rule (`README.md:23`) and v4's G0/G1/holds. *Do not claim* that the gates transfer to other devices, or that `powermetrics` has gain accuracy: there is no external meter.

### Medium

**M1. The five-term residual design may be misspecified for D's hybrid architecture.** The design `[1, P, D, (C+P)D + D²/2, CP + P²/2]` (`pilot_protocol_v4.md:488-489`) has context-quadratic terms that assume full attention in every layer. D has a hybrid, non-trimmable cache (`FINAL-DESIGN.md:12`). Chkir et al. (RV) show that attention type governs how decode energy scales with context. Ma et al. (RV) show that recurrent layers pay no prefill penalty. Misspecification inflates s_r and lowers detection power. *Action:* decision 2. This is print-only and leaves the registered primary fit unchanged.

**M2. The energy regression has prior art. The novelty is using a frozen fit's residual as a monitoring statistic over multi-turn, cached-prefix episodes.**
- Wilkins, Keshav & Mortier (HotCarbon 2024, RV) fit energy in input and output tokens with an interaction term, at R² > 0.96.
- Vellaisamy et al. (IISWC 2026, RV) use a fixed-plus-marginal decomposition. For Llama-3.2-1B on an H200, token energy falls from 7.46 to 0.72 J/token while window energy rises from 1.19 to 5.93 kJ, so per-token normalisation misleads. This supports printing gross episode energy beside turn-owned energy (`pilot_protocol_v4.md:199-200`).
- Husom et al., *The Price of Prompting* (S1), regress on response length.
- Fortuna et al. (S1) use a two-rate prefill and decode model.

**M3. The phases are not energetically separable, and agent energy per token far exceeds serving benchmarks.**
- Solovyeva & Castor (RV): higher prefill cost amplifies per-token decode energy by 1.3–51.8%, depending on the model.
- Luo et al. (RV): GPU-only telemetry misses 41–45% of system energy, and a sequential agent uses 63× more system energy per output token than saturated serving.

Turn-owned attribution should say that cross-phase coupling is absorbed into the fitted coefficients, not removed. These results also support the `(C+P)D` and `CP` terms and the gross headline basis.

**M4. The case for an energy channel is motivated by text-monitor failure modes, and its limit is formally sourced.**
- SHADE-Arena (RV) shows side-task success relying on a hidden scratchpad. Its best saboteur reaches 27% (Claude 3.7 Sonnet under a Claude 3.6 Sonnet monitor), and its best monitor reaches AUC 0.87.
- Chen et al. (S2) show that CoTs often omit what mattered.
- Baker et al. (S1+S2) show that optimising against a CoT monitor yields obfuscation.
- Korbak et al. (S1+S2) describe CoT monitorability as fragile.
- Kale et al. (RV) show that agent awareness of being monitored degrades monitors.
- MonitoringBench (RV) shows refined attacks cutting an Opus-4.5 monitor's catch rate from 94.9% to 60.3%.

Pfau et al. (RV) show computation hidden inside meaningless filler tokens. That is the formal source for ALIGN's stated limit: computation inside logged tokens costs what the log predicts (`PIPELINE.md:19-20`). Two framing rules follow, one from each seat:
- Energy detects *removed* reasoning, not *disguised* reasoning (seat 2).
- Once a monitor is known, it becomes an optimisation target, so any energy monitor inherits Baker's warning (seat 1).

**M5. Reasoning-token energy has not been measured on Apple silicon.**
- Dauner & Socher (*Frontiers in Communication* 2025, RV) measured an A100 with Perun across 14 models from 7B to 72B. Reasoning variants used 543.5 thinking tokens on average against 37.7 response tokens per multiple-choice item, and showed a 4–6× increase in emissions in free response.
- Zähl et al. (RV) found anomalous per-prompt energy for a thinking-mode model on an RTX 4060 Ti read at 2 Hz.
- Jin, Wei & Brooks (S1+S2) analyse test-time compute in energy terms.

None of these works on Apple silicon or ties energy to chat-template hidden-token accounting.

**M6. Monitoring cost in joules is open territory.** Ctrl-Z reports a 58%→7% attack reduction at about 5% usefulness cost (S1+S2). Hua et al. (S2) present a cost-constrained monitor framework that accepts any cost unit. Baker's "monitorability tax" (S1+S2) and Control Tax (RV) also express cost without energy. RQ-ALIGN-EFFICIENCY-MONITORABILITY (`PIPELINE.md:29`) is uncontested.

**M7. The governance practice has an established lineage, and one close neighbour.**
- Blind analysis comes from physics: Klein & Roodman 2005 (S1+S2, Crossref abstract) and Roodman 2003 (S2).
- Preregistration: Nosek et al. 2018 (S1+S2).
- ML preregistration: Hofman et al. 2023 (S1+S2), Søgaard et al. (EACL 2023, RV) and the NeurIPS 2021 pre-registration workshop, PMLR vol. 181 (S2).
- Systems metrology: Hoefler & Belli SC15 (S1+S2), van der Kouwe et al.'s "Benchmarking Crimes" (S2) and Kalibera & Jones (S2).
- Neither seat found an LLM-energy paper that preregisters or blinds; seat 2 checked more than 20.
- Khiani (RV) is the nearest published description of JouleWise-style mechanical pre-commitment (decision 4).

*Framing:* present this proportionately, as method hygiene with precedent, not as the contribution.

### Low (bibliography and framing)

**L1. Bibliography status for `draft-v1.md` §11** (row numbers as at `bd7a3efcd:docs/paper/draft-v1.md:361-391`):

| Entry | Status change | Action |
|---|---|---|
| [13] Benazir & Lin | Crossref (RV) confirms POMACS 9(3):1-26, Dec 2025 | Mark VERIFIED-ONLINE. The arXiv title differs (2508.08531). The `:332` sentence already says "without energy measurement" |
| [19] Ruf & Detyniecki | HotCarbon '26 paper-17 (RV) | Mark VERIFIED-ONLINE. Optionally add the PDF URL |
| [20] Ma et al. | v2, PPAM 2026 (RV) | Update the venue. The cross-check is confirmed for decode runs |
| [22] IPW | v7 says NeurIPS 2026 (RV) | Update the venue |
| [23] Dauner et al. | paper-46 PDF text (RV) | Mark VERIFIED-ONLINE. Tighten `:326` to name the cumulative counter |
| [26] Paired-MDE | §8 item 5 (RV) | No change. Optionally cite the section |
| [9], [11], [21] | Existing orphans | Cite in the body (decision 5) |

**L2. Generality and reference state.** Same-SKU GPUs vary by 8% on average and up to 22% (Sinha et al. SC22, S2), so results from a single MBP are device-specific. Gated energy is reference-state energy, not production energy; v4 already says so (`:514-515`). Keep both points in the paper.

**L3. Measurement-practice lineage on NVIDIA that has no Apple counterpart.** Burtscher et al. (2014, tool page only, S2) document sensor ramp and lag. Yang et al. (SC24, S1+S2) show sensors sampling only about 25% of runtime, with error cut by 35% on average. Dauner et al. (RV) document stale NVML reads below 100 ms. `powermetrics` has no equivalent literature. JouleWise's phase-edge calibration and prefill probe (`README.md:21`) fill that gap, on time rather than gain.

## 5. Gaps JouleWise fills (merged), and where to cite

| Gap | Evidence it is open | Claim boundary | Placement |
|---|---|---|---|
| G1. A physical audit of an agent's logged work at token level | H1 | Known, non-adaptive omission only; local hardware | New ALIGN related-work section (decision 6) |
| G2. LLM energy on Apple silicon with registered thermal gates and a floating battery | H3 | First found, not first proven; does not transfer across devices | `draft-v1.md` §8 "LLM energy measurement"; ALIGN paper |
| G3. Validating `powermetrics` on the time axis (phase-edge calibration, sampler-coverage gate) | L3, H3 | No gain claim without an external meter | §8 "counter gain to counter time": add the man page, Yang SC24 and optionally Burtscher beside Hähnel [29] and Dauner [23] |
| G4. Per-turn, per-tool attribution on a laptop SoC with half-widths and a tiling check | M2, M3; Energy per Successful Goal attributes per layer on servers | Turn-owned GPU energy within a named boundary | ALIGN paper |
| G5. Monitoring cost in measured joules | M6 | Frontier measured on one device | ALIGN paper (RQ-ALIGN-EFFICIENCY-MONITORABILITY) |
| G6. An energy model for multi-turn, cached-prefix episodes | M2, with the M1 caveat | Subject to the hybrid-architecture diagnostic | ALIGN paper; v4 analysis section |
| G7. Blind, preregistered energy measurement in ML systems | M7 | Hygiene with precedent; cite Khiani as a neighbour pending decision 4 | §8 "metrology lineage": add Nosek, Klein & Roodman and Hoefler & Belli |
| G8. Reasoning-token energy on device, tied to hidden-token accounting | M5 | D and anchor cells only | ALIGN paper |

## 6. Consolidated source list

This is the union of both seats, deduplicated. Each row gives the short citation, year and venue, URL, status, and its use for JouleWise. Full annotations, with authors and 2–4 sentences each, are in the seat reports in the appendix. The seat IDs (S# for seat 1; A#, B#, V#, E#, M# or table rows for seat 2) map each row back to the appendix.

### 6.1 Apple and edge measurement; sensor timing; thermal state

| # | Source | Year, venue | URL | Status | Use |
|---|---|---|---|---|---|
| 1 | Apple, `powermetrics(1)` man page (S1, A1) | n/a | https://keith.github.io/xcode-man-pages/powermetrics.1.html ; https://ss64.com/mac/powermetrics.html | RV | Vendor disclaimer; within-device basis |
| 2 | Oakley, "What does Activity Monitor measure?" (S2) | 2026, Eclectic Light Co. | https://eclecticlight.co/2026/06/29/what-does-activity-monitor-measure/ | S1 | Macs expose no wall power; meters weak below ~5 W |
| 3 | Taneja et al., Hot Pixels (A2) | 2023, USENIX Security | https://www.usenix.org/conference/usenixsecurity23/presentation/taneja | RV (ar5iv) | Thermal–power coupling on MBP; unprivileged IOReport |
| 4 | Pham et al., AgentStop [11] (A3) | 2026, ACM CAIS | https://arxiv.org/abs/2605.15206 | RV | Closest Apple `powermetrics` agent study; hot regime |
| 5 | Kannan et al., GreenBench (S4, A4) | 2026, IEEE ICCUBEA | https://arxiv.org/abs/2608.28667 | RV | Boundary inconsistency example |
| 6 | Benazir & Lin [13] (A5) | 2025, POMACS 9(3) | https://api.crossref.org/works/10.1145/3771563 ; https://arxiv.org/abs/2508.08531 | RV (Crossref) | No energy measured; low-bit not always faster |
| 7 | Hübner et al., Apple vs. Oranges [9] (S3) | 2025, IPDPSW | https://arxiv.org/abs/2502.05317 | S1+S2 | `powermetrics` used as a meter |
| 8 | Saad-Falcon et al., Intelligence per Watt [22] (A6) | 2025/2026, NeurIPS 2026 | https://arxiv.org/abs/2511.07885 | RV | Local-energy appetite; venue update |
| 9 | Rajesh et al., Apple runtime comparison (S5) | 2025, arXiv | https://arxiv.org/abs/2511.05502 | S1 | Throughput reported without joules |
| 10 | Laskaridis et al., MELTing point (S9, A7) | 2024, MobiCom | https://arxiv.org/abs/2403.12844 | S1+S2 | Thermal limits on-device LLMs |
| 11 | Tummalapalli et al., edge under sustained load (S10) | 2026, arXiv | https://arxiv.org/abs/2603.23640 | RV | iPhone 16 Pro throughput halves; tool not named |
| 12 | Islam et al., SLM energy on edges (S11) | 2025, IEEE MASS | https://arxiv.org/abs/2511.11624 | S1 | No error budget |
| 13 | Zähl et al., consumer GPU benchmark (S12) | 2026, arXiv | https://arxiv.org/abs/2608.00008 | RV | 2 Hz sampling; thinking-mode anomaly |
| 14 | Husom et al., The Price of Prompting (S13) | 2024, arXiv | https://arxiv.org/abs/2407.16893 | S1 | Response length predicts energy |
| 15 | Husom et al., Sustainable LLM Inference for Edge AI (seat 2 table) | 2025, arXiv | https://arxiv.org/abs/2504.03360 | S2 | Pi 4 with a hardware meter |
| 16 | Javat & Kazakov, Silicon Showdown [21] (seat 2 table) | 2026, arXiv | https://arxiv.org/abs/2605.00519 | S2 | Unmatched boundaries; orphan to cite |
| 17 | Zhang et al., SiliconBench (seat 2 table) | 2026, NeurIPS poster | https://neurips.cc/virtual/2026/poster/139658 | S2 | Apple stacks, no energy |
| 18 | Yang, Adámek & Armour, Part-time Power Measurements (S8, A8) | 2023/2024, SC24 | https://arxiv.org/abs/2312.02741 | S1+S2 | Sampler coverage, about 25% |
| 19 | Burtscher, Zecena & Zong, K20 sensor (A9) | 2014, GPGPU-7 | https://userweb.cs.txstate.edu/~burtscher/research/K20power/ | S2 (tool page only) | Sensor lag and ramp |
| 20 | Dauner et al., measurement frequency [23] (A10) | 2026, HotCarbon | https://hotcarbon.org/assets/2026/paper-46.pdf | RV (PDF text) | Stale NVML; 95.4% underestimate at 0.5 ms |
| 21 | Khan et al., RAPL in Action [5] (S7) | 2018, TOMPECS | DOI 10.1145/3177754 | already cited | Gain-validity anchor |
| 22 | Sinha et al., Not All GPUs Are Created Equal (seat 2 table) | 2022, SC22 | https://arxiv.org/abs/2208.11035 | S2 | Single-unit generality |
| 23 | Stojkovic et al., TAPAS (seat 2 table) | 2025 (ASPLOS unconfirmed) | https://arxiv.org/abs/2501.02600 | S2 | Thermal profiles differ by phase |
| 24 | Nunez-Yanez et al., run-time power modelling (seat 2 table) | 2020, arXiv | https://arxiv.org/abs/2006.12176 | S2 | Temperature term in power models |
| 25 | NVIDIA CUTLASS measurement guidelines (seat 2 table) | n/a | https://docs.nvidia.com/cutlass/latest/media/docs/cpp/gemm_performance_measurement_methodology_guidelines.html | S2 | Warm-up and cool-down practice |
| 26 | Preprint on Apple-silicon LLM energy, preprints.org 202605.0855 (S6) | 2026 | https://www.preprints.org/manuscript/202605.0855/v1 | **UNVERIFIED** (403 twice) | Dropped from all findings |

### 6.2 Agents, monitoring and control; agent energy

| # | Source | Year, venue | URL | Status | Use |
|---|---|---|---|---|---|
| 27 | Kutasov et al., SHADE-Arena (S14, B1) | 2025, arXiv | https://arxiv.org/abs/2506.15740 | RV | Task source; hidden scratchpad |
| 28 | Benton et al., Sabotage Evaluations (S15) | 2024, arXiv | https://arxiv.org/abs/2410.21514 | S1+S2 | Threat models; small-to-large extrapolation |
| 29 | Kale et al., Weak-to-Strong Monitoring / CUA-SHADE-Arena (B2) | 2025, arXiv | https://arxiv.org/abs/2508.19461 | RV | Monitor degradation under agent awareness |
| 30 | Jotautaitė et al., MonitoringBench (B3) | 2026, arXiv | https://arxiv.org/abs/2605.09684 | RV | LLM-monitor ceiling |
| 31 | Mittapalli et al., TRACE (S16) | 2026, arXiv | https://arxiv.org/abs/2606.07054 | RV | SHADE monitor; no cost reported |
| 32 | Ward et al., CTRL-ALT-DECEIT (S17) | 2025, NeurIPS spotlight | https://arxiv.org/abs/2511.09904 | S1 | Sandbagging sign (decision 8) |
| 33 | Debenedetti et al., AgentDojo (S18) | 2024, arXiv | https://arxiv.org/abs/2406.13352 | S1 | Alternative tasks |
| 34 | Greenblatt et al., AI Control (S19, B4) | 2023/2024, ICML | https://arxiv.org/abs/2312.06942 | S1+S2 | Vocabulary for the estimand |
| 35 | Bhatt et al., Ctrl-Z (S20, B5) | 2025, arXiv | https://arxiv.org/abs/2504.10374 | S1+S2 | Cost expressed as performance |
| 36 | UK AISI, ControlArena (S21) | 2025, blog | https://www.aisi.gov.uk/blog/introducing-controlarena-a-library-for-running-ai-control-experiments | S1 | Future harness (decision 9) |
| 37 | Cooper Stickland et al., Async Control (S22) | 2025, arXiv | https://arxiv.org/abs/2512.13526 | RV | Post-hoc monitoring; no compute cost |
| 38 | Terekhov et al., Control Tax (S23) | 2025/2026, arXiv | https://arxiv.org/abs/2506.05296 | RV | Financial cost, no energy |
| 39 | Korbak et al., CoT Monitorability (S24, B9) | 2025, arXiv | https://arxiv.org/abs/2507.11473 | S1+S2 | Fragility framing |
| 40 | Baker et al., Monitoring Reasoning Models (S25, B6) | 2025, arXiv | https://arxiv.org/abs/2503.11926 | S1+S2 | Obfuscation; monitorability tax |
| 41 | Chen et al., Reasoning Models Don't Always Say What They Think (B7) | 2025, arXiv | https://arxiv.org/abs/2505.05410 | S2 | Unfaithful CoT |
| 42 | Pfau, Merrill & Bowman, Let's Think Dot by Dot (B8) | 2024, arXiv | https://arxiv.org/abs/2404.15758 | RV | Formal source for the stated limit |
| 43 | Arnav et al., CoT Red-Handed (S26) | 2025, NeurIPS | https://proceedings.neurips.cc/paper_files/paper/2025/hash/468a018d4eb4ef57a2a5715d16658b24-Abstract-Conference.html | S1 | Template for a hybrid monitor at fixed FPR |
| 44 | Hua et al., Cost-Constrained Runtime Monitors (B10) | 2025, arXiv | https://arxiv.org/abs/2507.15886 | S2 | Framework that accepts joules |
| 45 | Kumar et al., OverThink (B12) | 2025, arXiv | https://arxiv.org/abs/2502.02542 | S2 | Billed hidden-token inflation; a different threat |
| 46 | Zhang et al., When LLM Defenses Backfire (seat 2 table) | 2026, arXiv | https://arxiv.org/abs/2607.24392 | S2 | Runtime cost, not joules |
| 47 | Panigrahy et al., Energy per Successful Goal (S27, B11) | 2026, arXiv v2 | https://arxiv.org/abs/2605.22883 | RV | Closest agent-attribution sibling |
| 48 | Luo et al., Where Does the Energy Go? (S28) | 2026, arXiv | https://arxiv.org/abs/2609.29707 | RV | 41–45% non-GPU; 63× per token |
| 49 | Fortuna et al., Where Should Agents Live? (S29) | 2026, arXiv | https://arxiv.org/abs/2609.18283 | S1 | Two-rate model; edge modelled only |
| 50 | Tripathy et al., SWEnergy (S30) | 2026, AGENT@ICSE | https://arxiv.org/abs/2512.09543 | S1 | SLM agents may not attempt the task |
| 51 | Krupp et al., Towards Sustainable Web Agents (S31) | 2025, arXiv | https://arxiv.org/abs/2502.17903 | S1 | Motivation only |

### 6.3 Hidden-work audit and side channels

| # | Source | Year, venue | URL | Status | Use |
|---|---|---|---|---|---|
| 52 | Sun et al., CoIn (V1) | 2026, Findings of EMNLP pp. 7594–7620 | https://aclanthology.org/2026.findings-emnlp.363/ | RV | Software count audit |
| 53 | Wang et al., PALACE (V2) | 2025, arXiv | https://arxiv.org/abs/2508.00912 | S2 | Statistical counterpart of the metadata baseline |
| 54 | Hoque et al., Token Inflation (V3) | 2026, arXiv | https://arxiv.org/abs/2605.30040 | RV | Need for evidence the provider does not control |
| 55 | Velasco et al., Is Your LLM Overcharging You? (V4) | 2025/2026, ICML oral (per seat) | https://arxiv.org/abs/2505.21627 | S2 | Misreporting incentive |
| 56 | Sun et al., Invisible Tokens, Visible Bills (V5) | 2025, arXiv | https://arxiv.org/abs/2505.18471 | S2 | Audit taxonomy without a physical class |
| 57 | Gargiulo & Kulp, Workload Identification (V6) | 2026, arXiv | https://arxiv.org/abs/2609.00309 | RV | Telemetry can be spoofed; class-level only |
| 58 | Kimpson, Baker & Graham, Can Power Draw Constrain Covert Compute? (V7) | 2026, arXiv | https://arxiv.org/abs/2610.07476 | RV | β framing; adaptive-adversary limit |
| 59 | de Almeida, GPU telemetry verifies training (V8) | 2026, ICML TAIGR workshop | https://icml.cc/virtual/2026/78576 | RV | Power carries workload structure |
| 60 | Clark et al., WattsUpDoc (V9) | 2013, USENIX HealthTech | https://www.usenix.org/conference/healthtech13/workshop-program/presentation/clark | S2 | Power as an external monitor |
| 61 | McDonald & Bar Or, Whisper Leak (S32) | 2025, arXiv | https://arxiv.org/abs/2511.03675 | RV | Packet and timing side channel, not power |
| 62 | Weiss et al., What Was Your Prompt? (seat 2 table) | 2024 (USENIX Security unconfirmed) | https://arxiv.org/abs/2403.09751 | S2 | Token-length leakage |
| 63 | Shumailov et al., Sponge Examples (seat 2 table) | 2021, EuroS&P | https://arxiv.org/abs/2006.03463 | S2 | Energy as a security quantity |
| 64 | Cai et al., Auditing Model Substitution (seat 2 table) | 2025, arXiv | https://arxiv.org/abs/2504.04715 | S2 | Software-only audits unreliable |
| 65 | Ong et al., TOPLOC (seat 2 table) | 2025, arXiv | https://arxiv.org/abs/2501.16007 | S2 | Cryptographic alternative |
| 66 | Shavit, What Does It Take to Catch a Chinchilla? (seat 2 table) | 2023, arXiv | https://arxiv.org/abs/2303.11341 | S2 | Hardware-rooted verification |

### 6.4 Energy per token, model size and quantization, prefill versus decode

| # | Source | Year, venue | URL | Status | Use |
|---|---|---|---|---|---|
| 67 | Patel et al., Splitwise (S41, E1) | 2023/2024 (ISCA unconfirmed on page) | https://arxiv.org/abs/2311.18677 | S1+S2 | Phase-split mechanism |
| 68 | Wilkins, Keshav & Mortier (E2) | 2024, HotCarbon | https://arxiv.org/abs/2407.04014 | RV | Regression prior art |
| 69 | Vellaisamy et al. (E3) | 2026, IISWC | https://arxiv.org/abs/2608.28044 | RV | Fixed plus marginal; per-token normalisation misleads |
| 70 | Chkir et al., energy scaling across attention architectures (E4) | 2026, arXiv | https://arxiv.org/abs/2608.25096 | RV | Hybrid-attention caveat |
| 71 | Ma et al., The Illusion of Power Capping [20] (S37, E5) | 2026, PPAM | https://arxiv.org/abs/2605.11999 | RV (v2 HTML) | Cross-check confirmed; recurrent layers pay no prefill penalty |
| 72 | Solovyeva & Castor, Towards Green AI (S38, E6) | 2026, arXiv (venue none on page) | https://arxiv.org/abs/2602.05712 | RV | Phase coupling 1.3–51.8% |
| 73 | Chung et al., Where Do the Joules Go? (E7) | 2026, arXiv | https://arxiv.org/abs/2601.22076 | S2 | Task type changes energy ~25× |
| 74 | Delavande, Pierrard & Luccioni, Understanding Efficiency (S36, E8) | 2026, arXiv | https://arxiv.org/abs/2601.22362 | RV (HTML) | One-token prefill; 10 runs; quantization regime |
| 75 | Jin, Wei & Brooks, The Energy Cost of Reasoning (S43, E9) | 2025, arXiv | https://arxiv.org/abs/2505.14733 | S1+S2 | Test-time compute in energy terms |
| 76 | Dauner & Socher, Energy costs of communicating with AI (S42) | 2025, Frontiers in Communication 10 | https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2025.1572947/full | RV | Thinking tokens dominate |
| 77 | Ruf & Detyniecki, The Cost of Context [19] | 2026, HotCarbon | https://hotcarbon.org/assets/2026/paper-17.pdf | RV (PDF text) | One-token prefill; single run per length |
| 78 | Samsi et al., From Words to Watts (S33) | 2023, arXiv | https://arxiv.org/abs/2310.03003 | S1+S2 | Datacenter baseline |
| 79 | Luccioni, Jernite & Strubell, Power Hungry Processing (S34) | 2024, FAccT | https://arxiv.org/abs/2311.16863 | S1+S2 | Parameter count insufficient |
| 80 | Fernandez et al., Energy Considerations (S39) | 2025, ACL | https://arxiv.org/abs/2504.17674 | S1+S2 | FLOP estimates underestimate |
| 81 | Chung et al., ML.ENERGY [8] (S40) | 2025, NeurIPS D&B | https://arxiv.org/abs/2505.06371 | already cited | Datacenter scope |
| 82 | Niu et al., TokenPowerBench [7] (S35) | 2025/2026, AAAI | https://arxiv.org/abs/2512.03024 | already cited | Phase attribution without meters |
| 83 | Wilhelm et al., Energy-per-Token advocacy (S44) | 2025, EuroMLSys | https://arxiv.org/abs/2603.20224 | S1 | Metric advocacy |
| 84 | Oviedo et al., Energy Use of AI Inference (S45) | 2025, arXiv / Joule 2026 | https://arxiv.org/abs/2509.20241 | S1 | Modelled; contrast only |
| 85 | Elsworth et al., Google-scale impact (S46) | 2025, arXiv | https://arxiv.org/abs/2508.15734 | S1 | Boundary choice moves the number |
| 86 | Jegham et al., How Hungry is AI? (S47) | 2025, arXiv | https://arxiv.org/abs/2505.09598 | S1 | Estimated; contrast only |
| 87 | Argerich & Patiño-Martínez (S48) | 2024, IEEE Access 12 | DOI 10.1109/ACCESS.2024.3409745 | META | Batch and quantization tuning; content unread |

### 6.5 Methodology, preregistration and blinding

| # | Source | Year, venue | URL | Status | Use |
|---|---|---|---|---|---|
| 88 | Nosek et al., The Preregistration Revolution (S49, M2) | 2018, PNAS | https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500 | S1+S2 | Prediction vs postdiction; deviation log |
| 89 | Hofman et al., Pre-registration for Predictive Modeling (S50, M3) | 2023, arXiv | https://arxiv.org/abs/2311.18807 | S1+S2 | ML preregistration targets modelling |
| 90 | Søgaard, Hershcovich & de Lhoneux (S51) | 2023, EACL | https://arxiv.org/abs/2302.10086 | RV | Two-sided preregistration debate |
| 91 | Khiani, Blinding the AI Co-Scientist (S52) | 2026, NeurIPS AI-Native Academia workshop | https://neurips.cc/virtual/2026/166242 | RV | Nearest governance neighbour (decision 4) |
| 92 | MacCoun & Perlmutter, Blind analysis (S53) | 2015, Nature 526 | https://www.nature.com/articles/526187a | META (content unread by both seats) | Pointer only |
| 93 | Klein & Roodman, Blind Analysis in Nuclear and Particle Physics (S54, M1) | 2005, Annu. Rev. Nucl. Part. Sci. 55 | https://api.crossref.org/works/10.1146/annurev.nucl.55.090704.151521 | S1+S2 (abstract) | Hidden-signal-box design |
| 94 | Roodman, Blind Analysis in Particle Physics (seat 2 table) | 2003, PhyStat | https://arxiv.org/abs/physics/0312102 | S2 | Companion to row 93 |
| 95 | Hoefler & Belli, Twelve Ways (S55, M4) | 2015, SC15 | https://htor.inf.ethz.ch/publications/index.php?pub=222 | S1+S2 | Results in the noise |
| 96 | van der Kouwe et al., Benchmarking Crimes (M5) | 2018, arXiv | https://arxiv.org/abs/1801.02381 | S2 | Pre-submission self-audit checklist |
| 97 | NeurIPS 2021 Pre-registration workshop (seat 2 table) | 2021, PMLR 181 | https://proceedings.mlr.press/v181/ | S2 | ML preregistration precedent |
| 98 | Kapoor & Narayanan, Leakage (seat 2 table) | 2022, arXiv | https://arxiv.org/abs/2207.07048 | S2 | Reproducibility |
| 99 | Bouthillier et al., Accounting for Variance (seat 2 table) | 2021, arXiv | https://arxiv.org/abs/2103.03098 | S2 | Sources of variance |
| 100 | Agarwal et al., Statistical Precipice (seat 2 table) | 2021, NeurIPS | https://arxiv.org/abs/2108.13264 | S2 | Interval estimates with few runs |
| 101 | Kalibera & Jones, Rigorous Benchmarking (seat 2 table) | 2013, ISMM | https://kar.kent.ac.uk/33611/ | S2 | Repetition planning |
| 102 | Henderson et al., Systematic Reporting (seat 2 table) | 2020, JMLR | https://arxiv.org/abs/2002.05651 | S2 | Energy-reporting appendices |
| 103 | Mytkowicz et al. [31] (S56) | 2009, ASPLOS | DOI 10.1145/1508244.1508275 | already cited | Measurement bias |
| 104 | Zhuang, Li & Fan, Paired-MDE [26] | 2026, arXiv | https://arxiv.org/abs/2605.28873 | RV (full text §8) | One-way MDE revision |

**Count:** 104 rows. 35 were re-opened by me (RV, including the PDF-text checks), 4 are already cited and unchanged, 2 are META and 1 is UNVERIFIED. The other 62 were opened by the seats and not re-opened by me: 17 by both seats, 15 by seat 1 only and 30 by seat 2 only.

## 7. Process note

- **Sources.** Re-checks used WebFetch on arXiv abstract and HTML pages, the NeurIPS and ICML virtual pages, ACL Anthology, Crossref, the HotCarbon 2026 page and retit.de. I fetched two HotCarbon PDFs (papers 17 and 46) into an isolated scratch directory. A zlib-only text extractor ran on each with `python3 -I`, because neither poppler nor pypdf is installed on the Air.
- **Repo checks.** Repo checks used `git show`, `git grep` and `git log` at the pins above.
- **Not touched.** No restricted path, rehearsal fixture or Block-5 artifact was opened. The measurement MBP was not touched.
- **Unresolved.** Two items stay open: whether the Khiani work is connected to this project (decision 4), and the content of the preprints.org paper (UNVERIFIED).

---

## Appendix A. Seat 1 report (Fable 5.1), verbatim as relayed to the synthesizer

The longer committed version is at `891b8856c:docs/reviews/2026-11-07-related-work-review-fable.md`.

~~~~text
TOP: ["Saved durably: docs/reviews/2026-11-07-related-work-review-fable.md on branch audit/2026-11-07-related-work-review-fable (commit 891b8856c, pushed to mpmdw/JouleWise; no PR; worktree removed). 56 sources, 47 OPENED, 4 PARTIAL, 4 UNVERIFIED, plus one repo-only cite.","Apple's own powermetrics man page says power values 'are estimated and may be inaccurate' and 'should not be used for any comparison between devices'; the only two Apple-silicon LLM/HPC energy papers found (Hübner 2502.05317; GreenBench 2608.28667) use the tool with no timing calibration, repeats, idle baseline, thermal gating or cross-check. GreenBench's 0.47 W 'package' figure during 7B decode vs 8-12 W system is internally implausible: a concrete published example of why JouleWise's channel naming, calibration and detection floor are needed.","No source anywhere asks whether energy beyond what logged tokens predict flags hidden or deleted agent work, or reports a joule-per-catch monitoring frontier: monitoring papers (SHADE-Arena, TRACE, CoT Red-Handed, Async Control) report no compute cost; Control Tax prices oversight in dollars; agent-energy papers (Energy per Successful Goal, Where Does the Energy Go) measure joules on NVIDIA/x86 with no monitoring question; side-channel work (Whisper Leak) uses timing/packets, not power. RQ-ALIGN-ENERGY-RESIDUAL and RQ-ALIGN-EFFICIENCY-MONITORABILITY are unoccupied.","Khiani, 'Blinding the AI Co-Scientist' (NeurIPS 2026 workshop) describes hash-frozen registration, structural blindness and two-seat review that closely match JouleWise's sealed-rules/desk-blind/independent-reviewer practice; it is the nearest published pattern and must be cited and differentiated. Provenance should be checked.","Independent support for the residual design's terms: Solovyeva & Castor (prefill cost amplifies decode energy 1.3-51.8%), Luo et al. (non-GPU energy 41-45%; sequential agent 63x energy/token vs serving), Zähl et al. and Dauner & Socher (hidden thinking tokens dominate per-answer energy). Sandbagging (CTRL-ALT-DECEIT) predicts a negative residual, so the preregistered test may need to be two-sided.","docs/align/pilot_protocol_v4.md named in the brief does not exist on any fetched branch; v0 on desk/2026-11-01-align-pilot-v0 (cbfb9b0a5) was used.","Bibliography hygiene: draft-v1.md [23] 'Dauner et al.' (counter-update behaviour) and Dauner & Socher 2025 (Frontiers, reasoning-token energy) are different works; confirm [23]'s record before adding the second."]
OPEN: ["Where is docs/align/pilot_protocol_v4.md (measurement Mac only? unpushed branch?); the review should be re-checked against its task list and budgets.","Is Khiani (NeurIPS 2026 workshop, 'Blinding the AI Co-Scientist') independent prior art or connected to this project? Determines whether it is cited as neighbour or source.","Should a controlled check on the analysis Air (never the measurement Mac) establish what powermetrics reports as 'package' vs gpu_power under MLX decode, to ground the GreenBench critique?","Should RQ-ALIGN-ENERGY-RESIDUAL's preregistered test be two-sided, given sandbagging predicts a negative residual while hidden work predicts positive?","Should a later ALIGN block adopt ControlArena settings despite its Inspect sandbox conflicting with the no-agent-process-on-the-Mac rule?","Four sources remain UNVERIFIED/PARTIAL (preprints.org 202605.0855; Argerich IEEE Access 2024; Søgaard et al. 2023; Nature/Klein-Roodman full texts); who re-opens them before the bibliography is frozen?"]
# Related-work literature review (Fable seat), 2026-11-07

**Durable copy:** committed as `docs/reviews/2026-11-07-related-work-review-fable.md` on branch `audit/2026-11-07-related-work-review-fable` of `mpmdw/JouleWise`, commit `891b8856c`, pushed to origin (no PR opened; worktree removed). Base: `origin/main` at `9406e49a2`.

Status: audit-track deliverable, not a paper section. A second model audits the same brief independently. Nothing here is a measurement, a Block-5 value, or a claim; Block 5 stays sealed and nothing here was derived from it.

Repo evidence is cited as `path:line` at `main` commit `9406e49a2` or at `desk/2026-11-01-align-pilot-v0` commit `cbfb9b0a5` for the ALIGN docs (not on `main`). The brief named `docs/align/pilot_protocol_v4.md`; that file does not exist on any fetched branch (only `pilot_protocol_v0.md` on the desk branch and `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v{1,2,3}.json` on `main`). v0 was used instead; see Open questions.

Source status labels: **OPENED** (primary page fetched, fields read from it); **PARTIAL** (primary fetched but returned only metadata/binary; summary from an opened secondary); **UNVERIFIED** (no primary could be opened; fields from search index, re-check before citing).

## 0. What JouleWise measures (for the relevance notes)

- One instrument: `powermetrics` on Apple silicon at 10 Hz, integrated only inside runtime-emitted phase boundaries, with a per-macOS-build timing calibration judged by a cold reviewer (`README.md:21`, `:23`; `docs/paper/draft-v1.md:324-330`).
- Gross energy within a named boundary as headline; idle-subtracted only as a within-device secondary view (`README.md:63-70`).
- Battery full and floating during every measurement because charging heats the chip; keep-awake job; an agent session at the keyboard voids a session (`README.md:19`, `:23`).
- Rules sealed by an independent reviewer before data exist; a desk program reads counts and checks, never an energy; opening energies needs reviewer approval; eight removed/refused attempts kept and disclosed (`README.md:19`).
- Detection floor: largest false difference the admitted system can produce; contrasts below it are refused (`README.md:11-13`; `draft-v1.md:342`).
- Prefill probe: shortest prompt length at which five small-model runs show at least five power readings overlapping prefill (`README.md:21`).
- ALIGN pilot v0: SHADE-Arena `spam_filter_update` and `bank_transfer_2` on Qwen3-8B-4bit/MLX, benign vs sabotage prompts, 12 episodes ABBA inside the unchanged Block-6 scaffold; per-turn prefill/decode/hidden token counts, tool-call timestamps, per-segment attributed energy; no monitor during the session (`docs/align/pilot_protocol_v0.md:23-60` at `cbfb9b0a5`).
- RQs: RQ-ALIGN-METADATA-BASELINE, RQ-ALIGN-ENERGY-RESIDUAL, RQ-ALIGN-EFFICIENCY-MONITORABILITY (`docs/align/PIPELINE.md:26-30`). Residual design `[1, prefill, decode, context*decode, context*prefill]`, trained on benign episodes only; "Power can count work omitted from a log; it cannot tell what reasoning occurs inside the same forward passes" (`docs/align/energy_residual.md:1-30`).

Already cited in `draft-v1.md:320-392`: Khan (RAPL in Action), Jay, Hähnel, Ma (Illusion of Power Capping), TokenPowerBench, Ruf & Detyniecki, ML.ENERGY, JouleSort, SPECpower, MLPerf Power, Georges et al., Mytkowicz, Paired-MDE, disaggregation papers, SplitZip. This review adds what the draft lacks: Apple-specific telemetry validity, agent monitoring/control, agent energy, reasoning-token energy, preregistration/blinding lineage.

## 1. Energy/power measurement of LLM inference on Apple silicon and edge devices

**S1. `powermetrics(1)` man page (Apple; mirror).** OPENED. https://keith.github.io/xcode-man-pages/powermetrics.1.html — "Average power values reported by powermetrics are estimated and may be inaccurate" and "should not be used for any comparison between devices"; cpu_power energy-model data "generally not comparable across machine models"; thermal sampler is an instantaneous end-of-window value; default interval 5000 ms. *Relevance:* vendor's own validity caveat for JouleWise's sole instrument; supports within-device paired design and refusal to rank devices; the thermal flag is a snapshot, not an integral, which the paper should state.

**S2. Oakley, H. "What does Activity Monitor measure?" Eclectic Light Co., 2026-06-29.** OPENED. https://eclecticlight.co/2026/06/29/what-does-activity-monitor-measure/ — Energy Impact tracks CPU only, non-linear (173x implied vs ~11x measured); neither tool estimates memory/SSD power; Macs expose no wall power; consumer wattmeters unreliable below ~5 W. *Relevance:* why JouleWise integrates named channels, and why an external-meter cross-check at laptop idle is itself hard; for the limitations section (`draft-v1.md:330`).

**S3. Hübner, Hu, Peng, Markidis. "Apple vs. Oranges: Evaluating the Apple Silicon M-Series SoCs for HPC Performance and Efficiency." arXiv 2502.05317, 2025.** OPENED. https://arxiv.org/abs/2502.05317 — powermetrics on M1-M4, a few W to 10-20 W, >200 GFLOPS/W; no meter, no tool validation. *Relevance:* representative of using the tool as if it were a meter; JouleWise's calibration and floor are the missing layer.

**S4. Kannan, Firke, Bengle, Deshmukh. "GreenBench: Benchmarking Energy Efficiency and Carbon Footprint of Open-Source LLM Inference on Apple Silicon." arXiv 2608.28667, 2026 (IEEE ICCUBEA 2026).** OPENED. https://arxiv.org/abs/2608.28667 — M4 Pro, Ollama, five 3-9B models; "CPU+GPU package power" ~0.47 W during sustained inference vs 8-12 W system; energy per token = power x latency; 30-40x over datacenter GPUs. *Relevance:* closest published neighbour and a cautionary example: 0.47 W package during 7B decode is implausible and inconsistent with its own system figure; no idle baseline, thermal handling or repeat protocol. Cite as nearest neighbour and as why channel naming, calibration and a floor precede any Mac per-token number.

**S5. Rajesh et al. "Production-Grade Local LLM Inference on Apple Silicon: A Comparative Study of MLX, MLC-LLM, Ollama, llama.cpp, and PyTorch MPS." arXiv 2511.05502, 2025.** OPENED. https://arxiv.org/abs/2511.05502 — M2 Ultra; MLX highest sustained throughput; energy not measured. *Relevance:* Apple-runtime comparisons report tok/s without joules; JouleWise adds the energy axis for the same runtime.

**S6. Preprint on LLM inference energy on Apple Silicon, preprints.org 202605.0855 v1, 2026.** UNVERIFIED (403). https://www.preprints.org/manuscript/202605.0855/v1 — snippets: claims no prior validated energy-estimation method for Apple-silicon LLM inference; uses top/vm_stat/ioreg/ps at 1.5 s, not powermetrics. *Relevance:* if accurate, concedes the gap from a weaker instrument. Re-open before citing.

**S7. Khan, Hirki, Niemi, Nurminen, Ou. "RAPL in Action." ACM TOMPECS 3(2), 2018. DOI 10.1145/3177754.** PARTIAL (PDF binary; record confirmed; already `draft-v1.md:366`). Regression vs plug power; high correlation; jittery ~1 ms updates. *Relevance:* keep as gain-validity anchor.

**S8. Yang, Adámek, Armour. "Part-time Power Measurements: nvidia-smi's Lack of Attention." arXiv 2312.02741, 2023 (SC'24 DOI 10.1109/SC41406.2024.00028).** OPENED. https://arxiv.org/abs/2312.02741 — only ~25% of runtime sampled on A100/H100; corrected practice cuts error 35% avg, 65% max vs external meter. *Relevance:* GPU analogue of sampler coverage; the prefill probe is JouleWise's response to the same hazard. Cite beside Hähnel.

**S9. Laskaridis, Katevas, Minto, Haddadi. "MELTing point: Mobile Evaluation of Language Transformers." MobiCom 2024, pp. 890-907; arXiv 2403.12844.** OPENED. https://arxiv.org/abs/2403.12844 — Android/iOS/Jetson; memory-bound; quantization viable at accuracy cost; continuous execution "elusive" from energy and heat. *Relevance:* peer-reviewed statement that thermal behaviour limits sustained on-device inference; motivates JouleWise's thermal flag and charging ban.

**S10. Tummalapalli, Arayakandy, Pal, Kundan. "LLM Inference at the Edge: Mobile, NPU, and GPU Performance Efficiency Trade-offs Under Sustained Load." arXiv 2603.23640, 2026.** OPENED. https://arxiv.org/abs/2603.23640 — Qwen2.5-1.5B 4-bit; iPhone 16 Pro loses nearly half its throughput within two iterations; S24 hits an OS GPU-frequency floor; RTX 4050 battery-limited at 34.1 W / 131.7 tok/s. *Relevance:* quantifies how fast thermal/battery policy moves the operating point on Apple mobile silicon; supports bracketed references and the drift bound. Tooling not in abstract.

**S11. Islam et al. "Characterizing and Understanding Energy Footprint and Efficiency of Small Language Model on Edges." arXiv 2511.11624, 2025 (IEEE MASS 2025).** OPENED. https://arxiv.org/abs/2511.11624 — Pi 5, Jetson Nano/Orin Nano; rankings without method, per-token numbers, thermal or idle handling in abstract. *Relevance:* typical edge-energy paper without an error budget.

**S12. Zähl, Dalipaj, Hennig, Bayer. "Energy Efficiency of Locally Deployed LLMs: A Preliminary Quantitative GPU Power Benchmark on Consumer Hardware." arXiv 2608.00008, 2026.** OPENED. https://arxiv.org/abs/2608.00008 — RTX 4060 Ti, Ollama, 18 models, nvidia-smi 2 Hz; 0.27 J/tok to 8.6x; thinking-mode model anomalously high per-prompt energy, authors argue generation modes must be distinguished. *Relevance:* independent evidence hidden reasoning dominates per-prompt energy (premise of RQ-ALIGN-ENERGY-RESIDUAL); 2 Hz plus S8 shows why 10 Hz and the coverage probe matter.

**S13. Husom, Goknil, Shar, Sen. "The Price of Prompting: Profiling Energy Use in LLM Inference." arXiv 2407.16893, 2024 (v2 2026).** OPENED (full HTML). https://arxiv.org/abs/2407.16893 — MELODI (Scaphandre + nvidia-smi); server, workstation, two laptops; response length strongest predictor (r~0.77), prompt features weak (~0.13); regression on response length, model, hardware R^2 0.996. *Relevance:* coarse whole-request ancestor of the energy-residual regression; JouleWise's per-turn attribution with half-widths is the finer instrument.

## 2. Energy and cost of LLM agents and of agent monitoring

**S14. Kutasov et al. "SHADE-Arena: Evaluating Sabotage and Monitoring in LLM Agents." arXiv 2506.15740, 2025.** OPENED. https://arxiv.org/abs/2506.15740 — 17 task pairs; best sabotage 27% (Claude 3.7 Sonnet) under Claude 3.6 monitor; best monitor Gemini 2.5 Pro AUC 0.87; side-task success relies on a hidden scratchpad; no monitoring cost reported. *Relevance:* source of ALIGN tasks (pinned `6614e771`, `docs/align/shade_port.md`); hidden scratchpad is the mechanistic reason an energy residual could carry signal; no energy, timing or monitor cost reported — the opening.

**S15. Benton et al. "Sabotage Evaluations for Frontier Models." arXiv 2410.21514, 2024.** OPENED. https://arxiv.org/abs/2410.21514 — threat models for covert sabotage of evaluation/monitoring/deployment; minimal mitigations currently sufficient; simulate large deployments from small-scale statistics. *Relevance:* same inferential move as JouleWise's pilot sizing via `sigma_pair` (`apple_path.md:306-373`).

**S16. Mittapalli et al. "TRACE: Trajectory Reasoning through Adaptive Cross-Step Evidence Aggregation for LLM Agents." arXiv 2606.07054, 2026.** OPENED. https://arxiv.org/abs/2606.07054 — on ten SHADE-Arena domains F1 0.713, recall 0.844; no cost reported. *Relevance:* SHADE-Arena is the standard monitor testbed; monitor papers do not report their own compute; joule-per-catch axis unoccupied.

**S17. Ward et al. "CTRL-ALT-DECEIT: Sabotage Evaluations for Automated AI R&D." arXiv 2511.09904, 2025 (NeurIPS 2025 spotlight).** OPENED. https://arxiv.org/abs/2511.09904 — MLE-Bench in Inspect; backdoors, generalisation failures, sandbagging; monitors fair on code sabotage, weak on sandbagging. *Relevance:* sandbagging reduces work, so an energy residual would go negative; the ALIGN design should state the predicted sign per threat model.

**S18. Debenedetti et al. "AgentDojo." arXiv 2406.13352, 2024.** OPENED. https://arxiv.org/abs/2406.13352 — 97 tasks, 629 security cases. *Relevance:* alternative task source only.

**S19. Greenblatt, Shlegeris, Sachan, Roger. "AI Control: Improving Safety Despite Intentional Subversion." arXiv 2312.06942, 2023 (ICML 2024).** OPENED. https://arxiv.org/abs/2312.06942 — trusted/untrusted protocols, control evaluation. *Relevance:* vocabulary ALIGN borrows; budgets human audits but not joules.

**S20. Bhatt et al. "Ctrl-Z: Controlling AI Agents via Resampling." arXiv 2504.10374, 2025.** OPENED. https://arxiv.org/abs/2504.10374 — BashBench 257 tasks; attacks 58% to 7% at 5% usefulness cost. *Relevance:* resampling multiplies inference work; protocol energy is a measurable design variable no control paper reports.

**S21. UK AISI. "Introducing ControlArena." 2025-10-22.** OPENED. https://www.aisi.gov.uk/blog/introducing-controlarena-a-library-for-running-ai-control-experiments — settings, policies, monitors, micro/macro-protocols on Inspect. *Relevance:* standard harness if ALIGN grows; Inspect sandboxing conflicts with "no agent process on the Mac".

**S22. Cooper Stickland et al. (UK AISI). "Async Control: Stress-testing Asynchronous Control Measures for LLM Agents." arXiv 2512.13526, 2025.** OPENED. https://arxiv.org/abs/2512.13526 — post-hoc monitoring of Claude 4.1 Opus SWE agent; 6% FNR at 1% FPR; FNR-to-deployment extrapolation. *Relevance:* JouleWise's protocol is asynchronous by construction (`pilot_protocol_v0.md:114`); monitor not priced.

**S23. Terekhov, Liu, Gulcehre, Albanie. "Control Tax: The Price of Keeping AI in Check." arXiv 2506.05296, 2025 (v3 2026).** OPENED. https://arxiv.org/abs/2506.05296 — control tax as operational/financial cost; dollar costs per monitor under an audit budget; no energy unit. *Relevance:* nearest prior art to RQ-ALIGN-EFFICIENCY-MONITORABILITY; proves the axis is priced in dollars, not joules.

**S24. Korbak et al. (41 authors). "Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety." arXiv 2507.11473, 2025.** OPENED. https://arxiv.org/abs/2507.11473 — CoT monitoring imperfect but promising; fragile. *Relevance:* hidden tokens are the monitorable surface; JouleWise asks whether a physical trace survives when text is removed (tamper transforms).

**S25. Baker et al. (OpenAI). "Monitoring Reasoning Models for Misbehavior and the Risks of Promoting Obfuscation." arXiv 2503.11926, 2025.** OPENED. https://arxiv.org/abs/2503.11926 — CoT monitoring far better than action-only; GPT-4o monitors o3-mini; training against the monitor yields obfuscated reward hacking; "monitorability tax". *Relevance:* obfuscation hides intent in text but not compute spent; energy residual is a candidate monitor text-pressure cannot directly erase (hypothesis, not finding).

**S26. Arnav et al. "CoT Red-Handed: Stress Testing Chain-of-Thought Monitoring." NeurIPS 2025.** OPENED. https://proceedings.neurips.cc/paper_files/paper/2025/hash/468a018d4eb4ef57a2a5715d16658b24-Abstract-Conference.html — hybrid reasoning+action score about doubles detection on subtle cases. *Relevance:* natural evaluation template: add an energy channel to a text monitor at fixed FPR.

**S27. Panigrahy, Tyagi, Abkin, Houngninou, Mahapatra. "Energy per Successful Goal: Goal-Level Energy Accounting for Agentic AI Systems." arXiv 2605.22883, 2026.** OPENED. https://arxiv.org/abs/2605.22883 — A-LEMS (RAPL; SPBM/DCGM on GB10), temporal boundary model, five-layer attribution; OOI 0.35-11x CPU-only, 0.4-26x with GPU; GPU 83.8% of agentic energy; overhead from extra calls. *Relevance:* closest methodological sibling to ALIGN attribution, on NVIDIA/x86 without a floor or preregistration; supports turn/tool counts as covariates.

**S28. Luo, Li, Wang, Chen. "Where Does the Energy Go? Profiling LLM Agent Inference on Blackwell GPUs." arXiv 2609.29707, 2026.** OPENED. https://arxiv.org/abs/2609.29707 — NVML+RAPL+IPMI; GPU-only misses 41-45% of system energy; sequential agent 63x more system energy per output token than saturated serving. *Relevance:* supports gross boundary and the `context*decode` term; strongest number for why single-stream agent energy per token exceeds serving benchmarks.

**S29. Fortuna, Hanžel, Strnad, Bertalanič. "Where Should Agents Live? Energy-Memory Characterization of Agentic AI for the Edge-Cloud Continuum." arXiv 2609.18283, 2026.** OPENED. https://arxiv.org/abs/2609.18283 — two-rate prefill/decode closed-form model; transport ~0.25% of workflow energy. *Relevance:* same functional form as JouleWise's per-turn fit; edge modelled, not measured.

**S30. Tripathy, Harshit, Vaidhyanathan. "SWEnergy." AGENT 2026 (ICSE workshop) pp. 104-111; arXiv 2512.09543.** OPENED. https://arxiv.org/abs/2512.09543 — Gemma-3 4B and Qwen3 1.7B agents; 9.4x framework spread; near-zero resolution. *Relevance:* an SLM agent may not attempt the task; pilot v0 records scores for this reason (`pilot_protocol_v0.md:87-88`).

**S31. Krupp, Geißler, Lukowicz, Karolus. "Towards Sustainable Web Agents." arXiv 2502.17903, 2025.** OPENED. https://arxiv.org/abs/2502.17903 — position paper. *Relevance:* motivational only.

**S32. McDonald, Bar Or. "Whisper Leak: a side-channel attack on Large Language Models." arXiv 2511.03675, 2025.** OPENED. https://arxiv.org/abs/2511.03675 — packet size/timing classify prompt topic >98% AUPRC across 28 models. *Relevance:* side-channel literature infers token counts/topics from timing and packets; no source found infers hidden computation from power. The nearest-relative citation for the gap.

## 3. Energy per token vs model size/quantization; prefill vs decode

**S33. Samsi et al. "From Words to Watts." arXiv 2310.03003, 2023.** OPENED. https://arxiv.org/abs/2310.03003 — LLaMA on V100/A100 up to 32 GPUs. Datacenter only.

**S34. Luccioni, Jernite, Strubell. "Power Hungry Processing." FAccT 2024 pp. 85-99; arXiv 2311.16863.** OPENED. https://arxiv.org/abs/2311.16863 — multi-purpose generative models orders of magnitude costlier at matched parameters. *Relevance:* parameter count insufficient predictor; contrasts between named configurations.

**S35. Niu et al. "TokenPowerBench." arXiv 2512.03024, 2025 (AAAI 2026).** OPENED (already cited). https://arxiv.org/abs/2512.03024 — phase-aligned prefill/decode attribution without meters. Draft's critique stands.

**S36. Delavande, Pierrard, Luccioni. "Understanding Efficiency: Quantization, Batching, and Serving Strategies in LLM Energy Use." arXiv 2601.22362, 2026.** OPENED. https://arxiv.org/abs/2601.22362 — H100/TGI; low precision saves energy only in compute-bound regimes; arrival shaping up to 100x. *Relevance:* a 4-bit vs 8-bit contrast on memory-bound single-stream Mac decode may be small or sign-ambiguous; needs a floor and preregistered direction.

**S37. Ma, Afzal, Eitzinger, Wellein. "The Illusion of Power Capping in LLM Decode." arXiv 2605.11999, 2026 (PPAM 2026).** OPENED (already `draft-v1.md:381`). https://arxiv.org/abs/2605.11999 — decode under half rated power; clock locking recovers up to 32%. No change.

**S38. Solovyeva, Castor. "Towards Green AI: Decoding the Energy of LLM Inference in Software Development." arXiv 2602.05712, 2026.** OPENED. https://arxiv.org/abs/2602.05712 — prefill cost amplifies per-token decode energy 1.3-51.8%; babbling suppression saves 44-89%. *Relevance:* evidence for the `context*decode` interaction and output-length as dominant lever.

**S39. Fernandez, Na, Tiwari, Bisk, Luccioni, Strubell. "Energy Considerations of LLM Inference and Efficiency Optimizations." ACL 2025 pp. 32556-32569; arXiv 2504.17674.** OPENED. https://arxiv.org/abs/2504.17674 — up to 73% savings; FLOP-based estimates substantially underestimate. *Relevance:* peer-reviewed warning against modelled energy; supports measured-only stance.

**S40. Chung et al. "The ML.ENERGY Benchmark." arXiv 2505.06371, 2025 (NeurIPS 2025 D&B spotlight).** OPENED (already cited). https://arxiv.org/abs/2505.06371 — datacenter GPU scope.

**S41. Patel et al. "Splitwise." ISCA 2024 pp. 118-132; arXiv 2311.18677.** OPENED. https://arxiv.org/abs/2311.18677 — prefill compute-bound, decode memory-bound with distinct power profiles. *Relevance:* canonical phase-split characterisation for why prefill and decode are reported separately.

**S42. Dauner, Socher. "Energy costs of communicating with AI." Frontiers in Communication 10, 2025. DOI 10.3389/fcomm.2025.1572947.** OPENED (full text). https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2025.1572947/full — A100, Perun, 14 models 7-72B; ~543 thinking tokens vs 38 response tokens per MC item; reasoning 4-6x emissions in free response. *Relevance:* measured baseline for "hidden thinking dominates energy" with Qwen/DeepSeek variants. Note: a different "Dauner" is cited at `draft-v1.md:326` [23]; check for name collision.

**S43. Jin, Wei, Brooks. "The Energy Cost of Reasoning." arXiv 2505.14733, 2025.** OPENED. https://arxiv.org/abs/2505.14733 — test-time compute beats model scaling on accuracy/energy; interaction with output length. *Relevance:* frames the inference-time-budget axis in energy terms.

**S44. Wilhelm, Wittkopp, Kao. "Beyond Test-Time Compute Strategies: Advocating Energy-per-Token in LLM Inference." EuroMLSys 2025; arXiv 2603.20224.** OPENED. https://arxiv.org/abs/2603.20224 — metric advocacy. *Relevance:* JouleWise's per-phase denominators are the concrete form.

**S45. Oviedo et al. (Microsoft). "Energy Use of AI Inference, Efficiency Pathways, and Test-Time Scaling." arXiv 2509.20241, 2025; Joule 2026.** OPENED. https://arxiv.org/abs/2509.20241 — modelled 0.31 Wh median; 15x longer queries ~13x energy. *Relevance:* modelled; contrast only.

**S46. Elsworth et al. (Google). "Measuring the environmental impact of delivering AI at Google Scale." arXiv 2508.15734, 2025.** OPENED. https://arxiv.org/abs/2508.15734 — boundary includes host, idle capacity, overhead; median 0.24 Wh. *Relevance:* industrial statement that boundary choice moves the number >2x; supports gross headline and named boundary.

**S47. Jegham et al. "How Hungry is AI?" arXiv 2505.09598, 2025.** OPENED. https://arxiv.org/abs/2505.09598 — estimated from API latency and multipliers. Contrast only.

**S48. Argerich, Patiño-Martínez. "Measuring and Improving the Energy Efficiency of LLM Inference." IEEE Access 12, pp. 80194-80207, 2024. DOI 10.1109/ACCESS.2024.3409745.** UNVERIFIED (403/loading stub). Batch size and quantization tuning. Re-open.

## 4. Methodology, preregistration and blinding

**S49. Nosek, Ebersole, DeHaven, Mellor. "The preregistration revolution." PNAS 115(11) 2600-2606, 2018.** OPENED (PMC). https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500 — prediction vs postdiction; indirect exposure to results biases; deviations OK if transparent; blinding the dataset, decision trees, SOPs. *Relevance:* canonical cite for sealed rules and the deviation log; "indirect exposure" is why the desk program never reads an energy.

**S50. Hofman, Chatzimparmpas, Sharma, Watts, Hullman. "Pre-registration for Predictive Modeling." arXiv 2311.18807, 2023.** OPENED. https://arxiv.org/abs/2311.18807 — template and practitioner study. *Relevance:* ML preregistration targets model evaluation; systems-measurement preregistration is unoccupied.

**S51. Søgaard, Hershcovich, de Lhoneux. "A Two-Sided Discussion of Preregistration of NLP Research." arXiv 2302.10086, 2023.** UNVERIFIED (search only). *Relevance:* supports explicit exploratory/claim split.

**S52. Khiani, R. "Blinding the AI Co-Scientist: Mechanical Pre-Commitment for AI-Assisted Empirical Research." NeurIPS 2026 Workshop on AI-Native Academia (poster).** OPENED. https://neurips.cc/virtual/2026/166242 — hash-frozen registration with append-only amendments; structural blindness (estimator cannot load real data); two-seat review; admission gate refused the headline analysis twice; "checks on outward-facing claims should run from the reader's vantage". *Relevance:* nearest published description of JouleWise's governance pattern and the only one framed for AI-assisted research; cite as neighbour and differentiate (physical measurement, detection floor, cold reviewer per build). See Open questions on provenance.

**S53. MacCoun, Perlmutter. "Blind analysis: Hide results to seek the truth." Nature 526, 187-189, 2015.** PARTIAL (login wall; Berkeley News coverage opened). https://www.nature.com/articles/526187a ; https://news.berkeley.edu/2015/10/08/blind-analysis-could-reduce-bias-in-social-science-research/ — hide or shift values until analysis is debugged; randomise labels. *Relevance:* general anchor for "analysis code reviewed before energies are opened".

**S54. Klein, Roodman. "Blind Analysis in Nuclear and Particle Physics." Annu. Rev. Nucl. Part. Sci. 55, 141-163, 2005.** PARTIAL (PDF fetched, text layer not extractable here). https://www.gwern.net/doc/statistics/bias/2005-klein.pdf — hidden signal box, hidden offset, prescription. *Relevance:* "nobody has looked at a measured energy yet" is a hidden-signal-box design.

**S55. Hoefler, Belli. "Scientific Benchmarking of Parallel Computing Systems: Twelve Ways..." SC15. DOI 10.1145/2807591.2807644.** OPENED (abstract record). https://evaluate.inf.usi.ch/node/366 — often unclear whether improvements are in the noise. *Relevance:* the detection floor operationalises "does the difference clear the noise".

**S56. Mytkowicz et al. ASPLOS 2009.** Already `draft-v1.md:392`. No change.

## 5. Gaps JouleWise fills

1. **Validated, phase-resolved powermetrics energy on Apple silicon.** Apple calls the numbers estimates (S1); the Apple-silicon energy papers (S3, S4) use the tool without timing calibration, repeats, idle baseline, thermal gating or cross-check, and S4's package figure looks internally inconsistent. No source characterises where the sampler places energy in time. Boundary: JouleWise still lacks an independent counter cross-check (S37 has one), and the vendor caveat forbids cross-device ranking.
2. **Sampler coverage as a gate (prefill probe).** Under-sampled phases produce wrong energy (S8); consumer/edge papers sample at 2 Hz or do not say (S10-S12). No source sets a minimum workload length from measured sampler overlap.
3. **Battery and thermal state as admission criteria.** S9, S10 show policy moves the operating point within seconds; no LLM-energy paper makes battery-floating and a per-member thermal flag a precondition with refusal.
4. **Energy as an agent-monitoring signal.** Monitoring literature measures text (S14, S16, S17, S24-S26) and prices oversight in dollars (S23) or usefulness (S19, S20, S22); agent-energy papers measure joules on NVIDIA/x86 with no monitoring question (S27-S30); side channels use timing/packets, not power (S32). RQ-ALIGN-ENERGY-RESIDUAL and RQ-ALIGN-EFFICIENCY-MONITORABILITY are unoccupied. Boundary: pilot is a non-claim instrument check (`pilot_protocol_v0.md:3-5`); S25 implies any known energy monitor becomes an optimisation target.
5. **Per-turn, per-tool attribution on a laptop SoC with uncertainty.** S27 attributes per layer on servers; S13 regresses whole requests; S28's 41-45% non-GPU share argues for the gross boundary on an SoC. No source attributes per turn on Apple silicon with half-widths and a tiling check (I3, `pilot_protocol_v0.md:72`).
6. **Preregistration and blinding applied to systems measurement.** ML preregistration targets predictive modelling (S50, S51); blind analysis is physics practice (S53, S54); mechanical precommitment is described for econometrics (S52). No LLM-energy paper seals removal rules before data, discloses refused sessions, or blinds its desk program. S52 is the pattern to cite and differentiate from.
7. **Reasoning-token energy on-device.** S42, S43, S12 measure hidden thinking's dominance on A100 or a consumer GPU; none on Apple silicon or tied to chat-template hidden-token accounting (`apple_path.md:91-109`). The "thinking on/off" open choice (`pilot_protocol_v0.md:137`) is also a literature gap.

## 6. Suggested placement in the paper

- `draft-v1.md` §8 "counter gain to counter time": add S1, S8 beside Hähnel.
- §8 "LLM energy measurement": add S4 (with caveat), S36, S38, S46.
- New Paper-2 paragraph: S14, S19, S23, S25, S26, S27, S28, S32, ending on gap 4.
- §8 "metrology lineage": add S49, S52, S53/S54, S55.
- Bibliography hygiene: resolve the two "Dauner" records.

## 7. Could not open / verify

S6 (403); S48 (403/stub); S51 (search only); S53 Nature full text (login); S54 PDF text layer (no poppler/pypdf on host); Hoefler-Belli author site (TLS mismatch; USI record used); `docs/align/pilot_protocol_v4.md` absent from every fetched branch.

## 8. Open questions

1. Where is `pilot_protocol_v4.md`? Review used v0 at `cbfb9b0a5`; re-check against v4's task list and budgets.
2. S52 (Khiani, NeurIPS 2026 workshop) matches JouleWise's governance closely. Independent prior art, or connected to this project? Decides whether to cite as neighbour or source.
3. S4's 0.47 W package figure: one controlled check on the analysis Air of what powermetrics reports as "package" vs `gpu_power` under MLX decode would ground the critique.
4. S17's sandbagging predicts a negative residual; the design frames hidden work as positive. Should the preregistered residual test be two-sided?
5. Adopt ControlArena (S21) settings for a later block, given the Inspect-sandbox conflict with the no-agent-process rule?
~~~~

## Appendix B. Seat 2 report (Opus 5.5), verbatim as relayed to the synthesizer

~~~~text
TOP: ["No prior work uses measured energy to audit an LLM agent's logged token counts. ALIGN sits between two literatures. Hidden-token auditing (CoIn, Findings of EMNLP 2026; PALACE; Token Inflation 2605.30040, which beats three audit frameworks with 1,469% undetected inflation and calls for evidence the provider does not control) is all software-based. Physical side-channel verification (Gargiulo & Kulp 2609.00309; Kimpson, Baker & Graham 2610.07476; de Almeida, ICML'26 workshop) works at workload-class or aggregate-compute scale. ALIGN's H50/H90 curve is a per-episode, token-level analogue of Kimpson's beta.","SHADE-Arena's abstract says sabotage success 'depends heavily on a hidden scratchpad' the monitor cannot see. Together with CoT unfaithfulness (Chen et al. 2025), obfuscation under optimization (Baker et al. 2025) and monitorability fragility (Korbak et al. 2025), this is the best motivation for an energy channel that bounds hidden reasoning size without reading it. Pfau et al.'s filler-token hidden computation is the formal source for the stated blind spot at PIPELINE.md:19-20 (e901eb2a4).","Apple-silicon LLM energy papers (AgentStop: M1 Max, powermetrics at 100 ms, GPU near 95 C; GreenBench; Hubner et al.; IPW) use powermetrics at face value. Apple's man page says average power values 'are estimated and may be inaccurate'. Hot Pixels (USENIX Sec'23) shows power and temperature co-vary with the workload on actively cooled Apple Macs. I found no LLM energy study that gates on thermal state, so ALIGN's G0/G1/holds look new. NVIDIA has a sensor-timing literature (Burtscher 2014; Yang et al. SC24, ~25% sampling coverage; Dauner HotCarbon'26); powermetrics has none.","Possible model misspecification. Chkir et al. 2026 show attention type governs how decode energy scales with context, and Ma et al. (PPAM 2026) show Gated DeltaNet and Mamba2 lack the quadratic prefill penalty. D has a hybrid, non-trimmable cache, yet the five-term design's (C+P)D + D^2/2 and CP + P^2/2 terms (pilot_protocol_v4.md:488-489 @543c9565d) assume full attention throughout. A print-only diagnostic is advised, because misspecification inflates s_r and lowers detection power.","Prior art to cite for the energy regression: Wilkins, Keshav & Mortier (HotCarbon'24) fit e = a0*tin + a1*tout + a2*tin*tout (R^2 > 0.96); Vellaisamy et al. (IISWC'26) use a fixed-plus-marginal decomposition. ALIGN's novelty is using a frozen fit's residual as a monitoring statistic over multi-turn, cached-prefix episodes, not the regression itself.","Threat-model gap: PIPELINE.md:10-12 says power is measured outside the agent's reach, but on a Mac powermetrics is software on the same host. Gargiulo & Kulp argue on-chip telemetry can be spoofed or replayed, and Kimpson et al. show matched-energy adversaries can hide at least 41% of capacity. The ALIGN paper should state the privilege boundary, confine the claim to non-adaptive known omission, or add an external meter cross-check.","Bibliography fixes for draft-v1.md: [13] verified via Crossref (arXiv title differs); [19] Ruf & Detyniecki still UNVERIFIED, while Delavande et al. 2601.22362 verifiably uses the one-token prefill method (but runs 10 reps, so the 'one run, no error bars' critique would not transfer); [20] now PPAM 2026, and its v2 abstract omits the NVML cross-check the draft relies on; [22] now NeurIPS 2026; [23] metadata verified; [26]'s abstract does not mention the 'raise-only' ratchet attributed at draft-v1.md:342.","No LLM-energy paper reviewed preregisters or blinds. JouleWise's sealed Block 5 with an energy-blind desk is blind analysis (Klein & Roodman 2005), with preregistration precedent in ML (Hofman et al. 2023; NeurIPS'21 PMLR vol. 181). Monitoring cost in joules is also open: Ctrl-Z, Hua et al. and Baker et al. report cost as performance or budget, so RQ-ALIGN-EFFICIENCY-MONITORABILITY is uncontested."]
OPEN: ["Should ALIGN report its known-H detection curve in units comparable to Kimpson et al.'s beta (hidden work as a fraction of declared work), and cite the identical-work replays (U3) plus frozen benign fit as the analogue of verifier re-execution?","Is the five-term residual design adequate for D's hybrid-attention, non-trimmable-cache architecture? Should registration add a print-only variant that restricts the context-quadratic terms to D's full-attention layers?","Should the ALIGN paper's claim be explicitly limited to a non-adaptive adversary (known log omission with joules fixed)? Should a print-only matched-energy mimicry variant be added so reviewers see the boundary?","Does tamper-evidence need an external DC or wall meter cross-check on episode totals, or is a stated privilege boundary (agent unprivileged, powermetrics as root via the harness) enough for the intended venue?","Can [19] Ruf & Detyniecki be located? If not, should draft-v1.md:332 be rewritten around the verifiable Delavande et al. 2026 source, accepting that the 'one run, no error bars' critique then falls away?","Does the v2 full text of Ma et al. (PPAM 2026) still contain the independent NVML energy-counter cross-check that draft-v1.md:330 relies on? And does the Paired-MDE full text support the 'raise but not lower' claim at draft-v1.md:342?","Should the ALIGN lane gain a related-work section now (it has none), using §2.2–2.3 of this review as the skeleton, before the blind registration cold gate reads protocol v4?"]
## JouleWise related-work review (Opus seat), 2026-11-07

**Track:** related-work literature review. Model: Opus 5.5 (`claude-opus-5-5`). I worked on my own; another model is auditing the same brief separately.

**Blinding and safety.** I did not open, list or read any restricted path (`/Users/edr/jw-b5-*`, `night-*`, custody, archive or `restricted/`). I did not open the `docs/paper/fill-rehearsal/*` JSONs. I made no attempt to infer any Block-5 value. I did not touch the measurement MBP. I made no commits, PRs, GitHub comments or worktrees, and wrote no files apart from one downloaded PDF, which went to an isolated scratchpad directory.

**Repo pins used for evidence**
- `origin/main` = `bd7a3efcd`.
- ALIGN integrated lane `origin/lane/2026-11-06-v4-r1-integrated` = `e901eb2a4`.
- Latest protocol v4 = `543c9565d`.
- Protocol v3 = `83e2dac59`.
- `docs/align/pilot_protocol_v4.md` is **not on main**. It exists only on that lane, and its own header says "DRAFT SKELETON — PROVISIONAL; not registered" (`543c9565d:docs/align/pilot_protocol_v4.md:3`).

---

## 0. What JouleWise measures (what this review is matched against)

**Paper 1 / instrument**
- The headline is gross energy inside a named measurement boundary on an Apple M3 Max MBP. Idle-subtracted energy is a separate, within-device view (`bd7a3efcd:README.md:63-70`).
- `powermetrics` gives one power reading every 100 ms (`README.md:21`).
- The battery must be full and not charging during every measurement (`README.md:23`).
- Block 5 is sealed. Its desk program never reads an energy (`README.md:19`).
- The instrument is attribution-limited, not noise-limited. The related-work section frames this as a "counter time vs counter gain" problem (`bd7a3efcd:docs/paper/draft-v1.md:320-346`).

**ALIGN**
- The question: "Can the electrical energy an inference machine draws serve as a record of an agent's work that the agent cannot edit?" Power "can count work: generated tokens a log omits, tool calls a log omits", and it "is blind to reasoning that fits inside one forward pass" (`e901eb2a4:docs/align/PIPELINE.md:7-20`).
- Related candidate questions: RQ-ALIGN-ENERGY-RESIDUAL and RQ-ALIGN-EFFICIENCY-MONITORABILITY (`PIPELINE.md:27,29`).

**Protocol v4**
- Model: Qwen3.8-27B 8-bit.
- Tasks: two SHADE-Arena task pairs, each run under a benign and a sabotage condition (`pilot_protocol_v4.md:70-73`).
- Thermal control: a 1 Hz SMC thermal sidecar, a start gate (G0), per-turn gates (G1) and decode holds (`:195-201`, `:350-390`).
- Acceptance criteria U1–U6 (`:413-422`). The quantity is turn-owned GPU energy.
- Analysis: a five-term residual design `[1, P, D, (C+P)D + D²/2, CP + P²/2]` (`:488-489`).
- Monitoring estimand: the known-H omission tamper curve. It is explicitly "known log omission, not a causal sabotage effect" (`:508-516`; `83e2dac59:docs/align/pilot_protocol_v3.md:155-163`).
- The lane has **no related-work text yet**. The only external references in `docs/align` are to the SHADE-Arena upstream repository.

---

## 1. Top findings (summary; detail in §§2–6)

1. **No prior work uses measured energy to audit an LLM agent's logged token counts.** ALIGN sits in the gap between two literatures, and neither closes it:
   - **Hidden-token auditing** (CoIn, PALACE, Token Inflation, Velasco et al.) is entirely software, statistical or cryptographic. Token Inflation shows that audits relying on provider artifacts can be beaten (1,469% undetected inflation of hidden reasoning). It calls for evidence the provider does not control.
   - **Physical side-channel compute verification** (Gargiulo & Kulp 2026; Kimpson, Baker & Graham 2026; de Almeida 2026) classifies workload type or bounds aggregate covert compute at GPU or datacenter scale. None of it works at token level or per episode.

   ALIGN's H50/H90 detection curve is in effect a **per-episode, token-level analogue of Kimpson et al.'s β**. This is the strongest novelty framing available and should anchor the ALIGN related-work section.
2. **SHADE-Arena's own abstract says side-task success "depends heavily on a hidden scratchpad" the monitor cannot see.** Combined with CoT unfaithfulness (Chen et al. 2025), obfuscation under optimization (Baker et al. 2025) and fragile monitorability (Korbak et al. 2025), this is the best external motivation for a channel that bounds the *size* of hidden reasoning without reading it. The limit has a formal source: Pfau et al.'s filler-token hidden computation spends exactly the energy the log predicts. That matches `PIPELINE.md:19-20`.
3. **Published LLM-on-Apple energy work takes `powermetrics` at face value.**
   - AgentStop (M1 Max, 100 ms, trapezoid integration, GPU near 95 °C), GreenBench, Hübner et al. and IPW do this.
   - Apple's own man page says average power values "are estimated and may be inaccurate" and advises against comparing devices.
   - Hot Pixels (USENIX Sec '23) shows that on actively cooled Apple machines, frequency is pinned and power and temperature co-vary with the workload. That is the MBP's regime.
   - I found **no LLM energy study that gates on thermal state**. ALIGN's G0/G1/holds and its model-free SMC sensor classifier appear new.
   - NVIDIA has a published literature on the sensor time axis (Burtscher 2014; Yang et al. SC24, ~25% sampling coverage; Dauner et al. HotCarbon '26, stale NVML reads under 100 ms). `powermetrics` has nothing equivalent, and JouleWise's phase-edge calibration fills that gap.
4. **The five-term residual design may be misspecified for D.**
   - Chkir et al. 2026: attention type governs how decode energy scales with context. MHA is steep; GQA with sliding-window attention is nearly flat.
   - Ma et al. 2026: Gated DeltaNet and Mamba2 have no quadratic prefill penalty.
   - D (`qwen3_5` family) has a hybrid, non-trimmable cache (`bd7a3efcd:docs/align/council-2026-11-05/FINAL-DESIGN.md:12`). The terms `(C+P)D + D²/2` and `CP + P²/2` assume full attention in every layer.

   Fitted coefficients will absorb some of this, but misspecification inflates s_r and so lowers detection power. A print-only diagnostic is cheap.
5. **Prior art for the energy regression exists, and ALIGN should cite it.** Wilkins, Keshav & Mortier (HotCarbon '24) fit `e = α0·τin + α1·τout + α2·τin·τout` (R² > 0.96). Vellaisamy et al. (IISWC '26) use a fixed-plus-marginal decomposition. What is new in ALIGN is using a *frozen* fit's residual as a monitoring statistic over multi-turn, cached-prefix episodes, not the regression itself.
6. **Threat-model gap.** `PIPELINE.md:10-12` says the power draw "is measured outside" the agent's reach. On a Mac, though, the counter is software on the same host. Gargiulo & Kulp argue that on-chip telemetry can be spoofed or replayed, and Kimpson et al. show matched-energy adversaries can hide at least 41% of capacity. The paper must state the privilege boundary (powermetrics needs root; Hot Pixels shows unprivileged *read* access to IOReport), restrict the claim to a non-adaptive adversary, or add an external DC/wall meter cross-check.
7. **I found no preregistration or blinding in any LLM-energy paper I reviewed** (more than 20 checked). The sealed Block 5 with an energy-blind desk is blind analysis in the Klein & Roodman sense, transplanted to ML-systems measurement. This is citable, established practice, not idiosyncrasy.
8. **Bibliography fixes for `draft-v1.md`** (detail in §5):
   - [13] verified via Crossref; the arXiv title differs.
   - [19] Ruf & Detyniecki is still UNVERIFIED after targeted searches. Delavande et al. 2026 is a verifiable source for the one-token prefill-isolation method.
   - [20] is now PPAM 2026, and its v2 abstract does not mention the NVML cross-check the draft leans on.
   - [22] is now NeurIPS 2026.
   - [23] metadata is verified.
   - [26]'s abstract does not mention the "raise-only ratchet" that `draft-v1.md:342` attributes to it.

---

## 2. Annotated core sources (45; all opened unless marked)

Format: **Title**. Authors. Year. Venue. URL. Then why it matters for JouleWise.

### 2.1 Measurement validity on Apple silicon and edge devices; sensor time behaviour; thermal state

**A1. powermetrics(1) manual page.** Apple (man page, read via the ss64 mirror). https://ss64.com/mac/powermetrics.html
- Default sample interval is 5000 ms; `-i` sets it; the thermal sampler reports pressure at the end of each window.
- Average power values "are estimated and may be inaccurate", and the page advises against using them to compare devices.
- This is the primary disclaimer for the instrument. It directly supports JouleWise's within-device gross-energy basis and its refusal to rank devices (`README.md:63-70`).
- Apple does not document the windowing semantics at 100 ms. That is the gap JouleWise's phase-edge calibration fills.
- Caveat: I read a mirror, not apple.com.

**A2. Hot Pixels: Frequency, Power, and Temperature Attacks on GPUs and Arm SoCs.** H. Taneja, J. Kim, J. J. Xu, S. van Schaik, D. Genkin, Y. Yarom. 2023. USENIX Security '23, pp. 6275–6292. https://www.usenix.org/conference/usenixsecurity23/presentation/taneja (details via https://ar5iv.labs.arxiv.org/html/2305.12784)
- The authors read Apple M1/M2 power, temperature and frequency through IOReport (via SocPowerBuddy). Apple allows power and temperature reads without privileges. They sampled every 10 ms.
- Readings depend on both the instructions and the data.
- Actively cooled M1 MacBook Pro and Mac mini hold the top P-state and leak "via temperature and power". The passively cooled Air leaks via frequency and power.
- For JouleWise, this is independent evidence that on the MBP's cooling regime, temperature and power co-vary with the workload. Thermal state is therefore an energy confound, which justifies G0/G1/holds. It also documents unprivileged read access, which is relevant to the tamper-evidence threat model.

**A3. AgentStop: Terminating Local AI Agents Early to Save Energy in Consumer Devices.** D. Pham, K. Katevas, A. Shahin Shamsabadi, H. Haddadi. 2026. ACM CAIS '26. https://arxiv.org/abs/2605.15206
- This is the closest neighbour on both hardware and method. Local agents run on an M1 Max (macOS 15.6.1); `powermetrics` logs at 100 ms, energy comes from trapezoidal integration, and a CPU baseline is subtracted only during non-GPU phases, with no GPU baseline. A Jetson AGX Orin is measured through tegrastats.
- Agentic runs raise GPU power, temperature (near 95 °C, sustained above 90 °C) and battery drain. Early termination saves 15–20% of wasted energy at under 5% utility loss.
- JouleWise differs in thermal-state control, the floating-battery rule, time attribution and preregistration. AgentStop's sustained-hot regime is exactly what ALIGN's gates exclude.
- Cite it in both the Apple-measurement and agent-energy paragraphs.

**A4. GreenBench: Benchmarking Energy Efficiency and Carbon Footprint of Open-Source LLM Inference on Apple Silicon.** R. Kannan, R. Firke, S. Bengle, S. Deshmukh. 2026. Accepted at IEEE ICCUBEA 2026 (per arXiv). https://arxiv.org/abs/2608.28667
- Uses an M4 Pro with `powermetrics` and Ollama timing. Package-level CPU+GPU is about 0.47 W during sustained inference, while system power is given as 8–12 W.
- Reports that 3–3.8B models use up to 62% less energy per token than 7–9B models.
- It is a cautionary example of boundary ambiguity: package and system figures differ by roughly 20×, with the system figure partly assumed. It supports JouleWise's rule of naming the boundary.

**A5. Benchmarking and Characterization of Large Language Model Inference on Apple Silicon.** A. Benazir, F. X. Lin. 2025. Proc. ACM Meas. Anal. Comput. Syst. (POMACS) 9(3):1–26, DOI 10.1145/3771563.
- Metadata verified via Crossref: https://api.crossref.org/works/10.1145/3771563. The ACM DL page returned 403.
- The arXiv version is titled "Profiling Large Language Model Inference on Apple Silicon: A Quantization Perspective": https://arxiv.org/abs/2508.08531
- Covers M2 Ultra, M2 Max and M4 Pro against RTX A6000 configurations, models from 8B to 405B, and 14 quantization schemes. Lower-bit quantization does not reliably speed up inference, because of dequantization overhead.
- It measures **no energy**, so `draft-v1.md:332` now describes it correctly.
- Relevant to v4's 4-bit contingency (`pilot_protocol_v4.md:186`): a lower bit width is not guaranteed to be cheaper on Apple.

**A6. Intelligence per Watt: Measuring Intelligence Efficiency of Local AI.** J. Saad-Falcon, A. Narayan, et al. (15 authors). 2025, v7 October 2026. NeurIPS 2026 (per arXiv comment). https://arxiv.org/abs/2511.07885
- Defines IPW as accuracy per unit of power. Covers 20+ local models, 8 accelerators including the Apple M4 Max, and 1M queries. Local accelerators show at least 1.4× lower IPW than cloud ones.
- Shows how much appetite there is for local-device energy as a headline figure. JouleWise is the measurement-validity complement.
- [22]'s venue should be updated.

**A7. MELTing point: Mobile Evaluation of Language Transformers.** S. Laskaridis, K. Katevas, L. Minto, H. Haddadi. 2024. MobiCom 2024. https://arxiv.org/abs/2403.12844
- Headless on-device LLM benchmarking on Android, iOS and Jetson, with energy and thermal tracing.
- Thermal behaviour and energy make sustained on-device LLM execution hard. Inference is memory-bound. Quantization costs accuracy.
- Early evidence that thermal state is first-order on edge devices. JouleWise moves from characterizing it to gating on it.

**A8. Part-time Power Measurements: nvidia-smi's Lack of Attention.** Z. Yang, K. Adamek, W. Armour. 2023, rev. 2024. SC24 (DOI 10.1109/SC41406.2024.00028 listed on the arXiv page). https://arxiv.org/abs/2312.02741
- On A100 and H100, the built-in sensor samples only about 25% of runtime. More than 70 GPUs were tested. The authors' good practices cut energy error by 35% on average (up to 65%) against an external meter.
- This is the strongest demonstration that a vendor counter's *time* behaviour, not its gain, dominates error for short phases. It is the NVIDIA analogue of JouleWise's powermetrics attribution limit.
- Add it to the "counter time" lineage in `draft-v1.md` §8 (currently Hähnel [29] and Dauner [23]).

**A9. Measuring GPU Power with the K20 Built-in Sensor.** M. Burtscher, I. Zecena, Z. Zong. 2014. GPGPU-7. https://userweb.cs.txstate.edu/~burtscher/research/K20power/ (I opened the authors' tool page; the paper PDF is linked there.)
- The K20Power tool corrects for the sensor's slow ramp-up and ramp-down and for variable sampling frequency.
- A GPU precedent, alongside Hähnel [29], for lag and ramp in a built-in sensor, which is the phenomenon JouleWise calibrates at phase edges.

**A10. Evaluating the Influence of Measurement Frequency on Energy Readings Using Intel RAPL and NVIDIA NVML.** M. Dauner, M. Steinberg, A. Brunnert, B. Schicker, B. Zönnchen. 2026. HotCarbon '26 (Seattle, 16–17 July 2026).
- PDF: https://hotcarbon.org/assets/2026/paper-46.pdf. It downloaded, but I could not extract its text.
- Metadata and findings come from a co-author organisation's page: https://www.retit.de/paper-measurement-frequency-energy-readings-intel-rapl-nvidia-nvml-hotcarbon-2026/
- NVML cumulative energy counters often return stale reads below 100 ms, and this varies by platform. RAPL is stable at 10 ms or coarser. The authors recommend integrating power rather than trusting unvalidated counters.
- This resolves the repo's UNVERIFIED-OFFLINE status for [23] at metadata level. The specific "severe underestimate on one GPU" sentence (`draft-v1.md:326`) still needs a PDF check.

### 2.2 Agents, monitoring, control evaluations, and their cost or energy

**B1. SHADE-Arena: Evaluating Sabotage and Monitoring in LLM Agents.** J. Kutasov, Y. Sun, P. Colognese, T. van der Weij, L. Petrini, C. B. C. Zhang, J. Hughes, X. Deng, H. Sleight, T. Tracy, B. Shlegeris, J. Benton. 2025. arXiv (no venue listed). https://arxiv.org/abs/2506.15740
- Benign main tasks are paired with harmful side tasks. The best saboteurs succeed 27% of the time (Claude 3.7 Sonnet) and 15% (Gemini 2.5 Pro) under a Claude 3.6 Sonnet monitor. The top monitor reaches AUC 0.87.
- Side-task success "depends heavily on a hidden scratchpad" the monitor cannot see.
- ALIGN runs two of its pairs locally (`pilot_protocol_v4.md:70-73`). The hidden-scratchpad dependence is the best single motivation for an energy channel that bounds hidden reasoning without reading it.

**B2. Reliable Weak-to-Strong Monitoring of LLM Agents.** N. Kale, C. B. C. Zhang, K. Zhu, A. Aich, P. Rodriguez, Scale Red Team, C. Q. Knight, Z. Wang. 2025. arXiv. https://arxiv.org/abs/2508.19461
- Introduces monitor red teaming and CUA-SHADE-Arena, a computer-use extension built on TheAgentCompany and the main SHADE-Arena successor.
- An agent's awareness of being monitored degrades monitor reliability, and giving the monitor more awareness helps less than expected. A hybrid hierarchical-sequential scaffold enables weak-to-strong monitoring. Escalating pre-flagged cases to humans adds about 15% TPR at 1% FPR.
- An energy residual cannot be talked out of its verdict by prompt injection, which is the failure mode this paper documents. An aware agent can still change how much work it does.

**B3. MonitoringBench: Semi-Automated Red-Teaming for Agent Monitoring.** M. Jotautaitė, M. A. Martinez, O. Matthews, T. Tracy. 2026. arXiv. https://arxiv.org/abs/2605.09684
- 2,644 attack trajectories in BashArena. Refined attacks cut an Opus-4.5 monitor's catch rate from 94.9% to 60.3%. Monitors often flag suspicious actions but are then persuaded or miscalibrated.
- Evidence of the ceiling on LLM monitors under adversarial pressure. It supports positioning energy as a non-semantic, non-persuadable *complement*, not a replacement.

**B4. AI Control: Improving Safety Despite Intentional Subversion.** R. Greenblatt, B. Shlegeris, K. Sachan, F. Roger. 2023, rev. 2024. ICML 2024 (OpenReview link on the arXiv page). https://arxiv.org/abs/2312.06942
- Defines control protocols such as trusted editing and untrusted monitoring, evaluated against a deliberately subversive model.
- This is the frame ALIGN's estimand should be written in: a red-team policy (log omission), a blue-team monitor (energy residual) and an FPR budget. It also provides the vocabulary for saying the policy is *known and non-adaptive*.

**B5. Ctrl-Z: Controlling AI Agents via Resampling.** A. Bhatt, C. Rushing, A. Kaufman, T. Tracy, V. Georgiev, D. Matolcsi, A. Khan, B. Shlegeris. 2025. arXiv. https://arxiv.org/abs/2504.10374
- The first agent control evaluation: BashBench, 257 tasks. Resample protocols cut attack success from 58% to 7% at about 5% cost to benign performance.
- The cost of control is reported as performance, never in joules. That is the opening for RQ-ALIGN-EFFICIENCY-MONITORABILITY (`PIPELINE.md:29`).

**B6. Monitoring Reasoning Models for Misbehavior and the Risks of Promoting Obfuscation.** B. Baker, J. Huizinga, L. Gao, Z. Dou, M. Y. Guan, A. Madry, W. Zaremba, J. Pachocki, D. Farhi. 2025. arXiv. https://arxiv.org/abs/2503.11926
- A GPT-4o CoT monitor beats action-only monitoring of o3-mini for reward hacking. Optimizing against the monitor produces obfuscated reward hacking. The authors propose a "monitorability tax".
- Obfuscation changes CoT *content*, not necessarily its length. ALIGN should say plainly that energy detects removed reasoning, not disguised reasoning.

**B7. Reasoning Models Don't Always Say What They Think.** Y. Chen, J. Benton, A. Radhakrishnan, J. Uesato, C. Denison, J. Schulman, A. Somani, P. Hase, M. Wagner, F. Roger, V. Mikulik, S. R. Bowman, J. Leike, J. Kaplan, E. Perez. 2025. arXiv. https://arxiv.org/abs/2505.05410
- CoTs mention hint use often less than 20% of the time it matters. Outcome RL improves this only up to a plateau. Reward hacking goes unverbalized.
- Establishes that visible reasoning is incomplete evidence. ALIGN targets a different kind of incompleteness (missing tokens) and must not claim to fix unfaithfulness.

**B8. Let's Think Dot by Dot: Hidden Computation in Transformer Language Models.** J. Pfau, W. Merrill, S. R. Bowman. 2024. arXiv. https://arxiv.org/abs/2404.15758
- Meaningless filler tokens can carry hidden computation on some tasks.
- This is the formal source for ALIGN's stated limit. Computation hidden inside *logged* tokens costs exactly the energy the log predicts, so energy is blind to it (`PIPELINE.md:19-20`).

**B9. Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety.** T. Korbak, M. Balesni, E. Barnes, Y. Bengio, J. Benton, et al. (41 authors). 2025. arXiv position paper. https://arxiv.org/abs/2507.11473
- CoT monitoring is promising but fragile, and developers should protect monitorability.
- A framing citation for why signals that do not depend on CoT matter.

**B10. Combining Cost-Constrained Runtime Monitors for AI Safety.** T. T. Hua, J. Baskerville, H. Lemoine, M. Hopman, A. Bhatt, T. Tracy. 2025. arXiv. https://arxiv.org/abs/2507.15886
- Decides which monitors to call under an average-cost budget, using exhaustive search plus Neyman–Pearson allocation. More than doubles recall over a naive baseline in code review.
- An energy residual is a monitor with near-zero marginal cost, because the energy is measured anyway. It slots into this framework, and costs can be stated in measured joules.

**B11. Energy per Successful Goal: Goal-Level Energy Accounting for Agentic AI Systems (A-LEMS).** D. Panigrahy, A. Tyagi, S. Abkin, D. K. Houngninou, R. Mahapatra. 2026 (v2 October 2026). arXiv. https://arxiv.org/abs/2605.22883
- Introduces goal-level accounting and a temporal boundary model, using RAPL on x86 and SPBM/DCGM on a GB10.
- The Orchestration Overhead Index (OOI) is 0.35–11.07× when only CPU energy is counted, and 0.4–26.48× once GPU dynamic energy is included. GPU dynamic energy is 83.8% of agentic energy per successful goal in local inference. The overhead comes from the structure of the orchestration (more calls), not from costlier calls.
- The closest "energy of agents" framework. It supports counting work, but it has no thermal control and no monitoring use.

**B12. OverThink: Slowdown Attacks on Reasoning LLMs.** A. Kumar, J. Roh, A. Naseh, M. Karpinska, M. Iyyer, A. Houmansadr, E. Bagdasarian. 2025. arXiv. https://arxiv.org/abs/2502.02542
- Decoys placed in external context inflate hidden reasoning tokens 12–46× (up to 17× in coding agents) while answers stay correct.
- A real attack that produces unexpected hidden reasoning. It argues that energy-anomaly monitoring has security value beyond sabotage. In this attack the extra tokens are billed, so this is a different threat from log omission.

### 2.3 Auditing hidden work: token-count audits and physical side-channel verification (the bridge ALIGN occupies)

**V1. CoIn: Counting the Invisible Reasoning Tokens in Commercial Opaque LLM APIs.** G. Sun, Z. Wang, B. Tian, M. Liu, Z. Shen, S. He, Y. He, W. Ye, Y. Wang, A. Li. 2026. Findings of EMNLP 2026, pp. 7594–7620, DOI 10.18653/2026.findings-emnlp.363. https://aclanthology.org/2026.findings-emnlp.363/ ; https://arxiv.org/abs/2505.13778
- Builds a hash tree over token-embedding fingerprints and adds relevance matching. Detects count inflation up to 94.7% of the time when run as a trusted third-party auditor.
- Defines the hidden-reasoning-count audit problem that ALIGN attacks physically. CoIn depends on artifacts the provider supplies.

**V2. Predictive Auditing of Hidden Tokens in LLM APIs via Reasoning Length Estimation (PALACE).** Z. Wang, G. Sun, Y. He, Z. Shen, B. Tian, A. Li. 2025. arXiv. https://arxiv.org/abs/2508.00912
- A user-side model predicts hidden reasoning-token counts from prompt–answer pairs.
- The statistical counterpart of ALIGN's RQ-ALIGN-METADATA-BASELINE (`PIPELINE.md:26`): how much can be predicted without a physical channel.

**V3. Token Inflation: How Dishonest Providers Can Overcharge for Large Language Model Usage.** S. Hoque, J. Zhang, J. Sun, F. Suya. 2026. arXiv. https://arxiv.org/abs/2605.30040
- Defeats three token-auditing frameworks. Hidden reasoning is inflated by 1,469% on average without detection, and tokenization ambiguity allows 50.85% over-reporting even when the reasoning is visible.
- Names a "trust paradox" and recommends evidence the provider does not control (TEEs, proofs, re-execution).
- The strongest external argument for a physical record. Measured energy is such evidence whenever the party measuring is not the party reporting.

**V4. Is Your LLM Overcharging You? Tokenization, Transparency, and Incentives.** A. A. Velasco, S. Tsirtsis, N. Okati, M. Gomez-Rodriguez. 2025 (v4 May 2026). ICML 2026 oral (per arXiv comment). https://arxiv.org/abs/2505.21627
- Per-token pricing creates an incentive to misreport; the authors propose per-character pricing.
- The economic reason logged counts may be untrustworthy.

**V5. Invisible Tokens, Visible Bills: The Urgent Need to Audit Hidden Operations in Opaque LLM Services.** G. Sun, Z. Wang, X. Zhao, B. Tian, Z. Shen, Y. He, J. Xing, A. Li. 2025. arXiv position paper. https://arxiv.org/abs/2505.18471
- Distinguishes quantity inflation from quality downgrade. Lists commitment-, prediction-, behaviour-, signature- and TEE-based audits.
- Physical or energy-based audit is absent from this list. JouleWise can claim to instantiate that missing class on local hardware.

**V6. Workload Identification with Physical Side Channels for AI Governance.** S. Gargiulo, G. Kulp. 2026. arXiv. https://arxiv.org/abs/2609.00309
- H200 power sampled at about 10 MHz across 930 traces separates training, inference and non-AI work with 97% accuracy (macro-F1 0.955) on unseen model families. Most adversarial evasions are caught.
- Argues that on-chip telemetry (NVML) can be spoofed or replayed.
- The closest physical side-channel neighbour. It identifies workload class, not token counts, and it directly challenges software counters, which is a threat-model point ALIGN must answer for `powermetrics`.

**V7. Can Power Draw Constrain Covert Compute? Limits of Analogue Verification for AI Governance.** T. Kimpson, M. Baker, E. Graham. 2026 (submitted 5 October 2026). arXiv. https://arxiv.org/abs/2610.07476
- Defines β as the largest hidden compute a power trace cannot rule out, as a fraction of declared capacity. Worst-case β is 1.16 on A100s. Matched-energy adversaries hide at least β = 0.41. If the verifier can re-execute the declared work at an observed operating point, β falls to 0.059.
- **The most important new neighbour.** ALIGN's H50/H90 curve (ruling 2, `pilot_protocol_v4.md:611`) is a token-level, per-episode β. ALIGN's identical-work replays (U3) and frozen benign fit play the role of verifier re-execution.
- It is also the strongest critique: an adaptive matched-energy adversary lies outside ALIGN's estimand.

**V8. Can GPU Telemetry Verify LLM Training? Evidence from Temporal Structure in a Black-Box Setting.** A. G. de Almeida. 2026. ICML 2026 Second Workshop on Technical AI Governance Research (poster). https://icml.cc/virtual/2026/78576
- A one-class verifier trained on power telemetry recognizes the temporal signature of autoregressive LLM training across model families.
- More evidence that power carries workload structure. Not token-level.

**V9. WattsUpDoc: Power Side Channels to Nonintrusively Discover Untargeted Malware on Embedded Medical Devices.** S. S. Clark, B. Ransford, A. Rahmati, S. Guineau, J. Sorber, K. Fu, W. Xu. 2013. USENIX HealthTech '13. https://www.usenix.org/conference/healthtech13/workshop-program/presentation/clark
- Whole-system power detects known malware at 94% or better and unknown malware at 85% or better, with no change to the device.
- The canonical precedent for power as an external monitor of unexpected computation. ALIGN is "WattsUpDoc for agent logs", with a calibrated physical model in place of a classifier.

### 2.4 Energy per token versus model size and quantization; prefill versus decode; energy models

**E1. Splitwise: Efficient Generative LLM Inference Using Phase Splitting.** P. Patel, E. Choukse, C. Zhang, A. Shah, Í. Goiri, S. Maleki, R. Bianchini. 2023, rev. 2024. https://arxiv.org/abs/2311.18677
- The arXiv page lists no venue; ISCA 2024 is from my own knowledge and is not confirmed on the page.
- Prompt computation is compute-intensive and token generation memory-intensive, each with its own power profile.
- The canonical mechanism citation for phase-separated energy.

**E2. Offline Energy-Optimal LLM Serving: Workload-Based Energy Models for LLM Inference on Heterogeneous Systems.** G. Wilkins, S. Keshav, R. Mortier. 2024. HotCarbon 2024. https://arxiv.org/abs/2407.04014 (Eq. 6 read from https://arxiv.org/html/2407.04014)
- The model is `e_K(τin, τout) = α0·τin + α1·τout + α2·τin·τout`, fit by OLS for each model and system pair, with R² > 0.96. Hardware is A100s measured through PyJoules/NVML, with CPUs through AMD μProf.
- This is the direct prior art for ALIGN's energy-in-token-counts regression. ALIGN's design (`pilot_protocol_v4.md:488-489`) adds an intercept and cumulative-context quadratic terms suited to multi-turn, cached-prefix episodes.
- The novelty to claim is using a frozen fit's residual as the monitoring statistic.

**E3. Characterization of Request and Token Energy Costs for LLM Inference Workloads on GPU Platforms.** P. Vellaisamy, V. Lam, S. Blanton, J. P. Shen. 2026. IISWC 2026. https://arxiv.org/abs/2608.28044
- Decomposes energy into a fixed prefill/setup cost plus a marginal cost per output token.
- For Llama-3.2-1B on an H200, token energy falls from 7.46 to 0.72 J/token while request energy rises from 1.19 to 5.93 kJ.
- Per-token normalization misleads. This supports JouleWise printing gross episode energy beside turn-owned energy.

**E4. Understanding the Energy Scaling of Large Language Model Inference Across Context Lengths and Attention Architectures.** M. Chkir, S. M. Danish, J. Höll, A. Asad. 2026. arXiv. https://arxiv.org/abs/2608.25096
- Attention type governs how decode energy scales with context: MHA is steep, GQA shallower, and GQA with sliding-window attention nearly flat.
- Implication: ALIGN's context-quadratic terms assume full attention, but D has a hybrid cache. See finding 4 and open question 1.

**E5. The Illusion of Power Capping in LLM Decode: A Phase-Aware Energy Characterisation Across Attention Architectures.** B. Ma, A. Afzal, J. Eitzinger, G. Wellein. 2026 (v2 29 October 2026). PPAM 2026. https://arxiv.org/abs/2605.11999
- Decode is memory-bound and the GPU idles between kernel launches, so power caps rarely engage. Locking the SM clock recovers up to 32% of decode energy.
- Gated DeltaNet and Mamba2 show no prefill penalty without prefix caching.
- Already cited as [20]. The venue needs updating, and it supports E4's caveat about hybrid architectures.

**E6. Towards Green AI: Decoding the Energy of LLM Inference in Software Development.** L. Solovyeva, F. Castor. 2026. arXiv (an EASE 2026 listing appeared in search; not confirmed). https://arxiv.org/abs/2602.05712
- Higher prefill cost raises the energy of each decoded token by 1.3–51.8%, depending on the model. Decode dominates overall.
- Shows the phases are not energetically independent. This bears on JouleWise's phase attribution and on ALIGN's `CP` and `(C+P)D` interaction terms.

**E7. Where Do the Joules Go? Diagnosing Inference Energy Consumption.** J.-W. Chung, R. Wu, J. J. Ma, M. Chowdhury. 2026. arXiv. https://arxiv.org/abs/2601.22076
- 46 models, 7 tasks and 1,858 configurations on H100 and B200. Task type alone changes LLM energy about 25×.
- Large-scale backing for "decode dominates" (per the search summary). The point that lower precision is not always more efficient also comes from the search summary, not the abstract I read.

**E8. Understanding Efficiency: Quantization, Batching, and Serving Strategies in LLM Energy Use.** J. Delavande, R. Pierrard, S. Luccioni. 2026. arXiv. https://arxiv.org/abs/2601.22362 (method read from the HTML version)
- Quantization saves energy only in compute-bound regimes.
- "We isolate prefill by generating a single token", then obtain decode by subtraction. Energy comes from CodeCarbon (NVML plus pyRAPL), with 10 runs after 5 warm-ups.
- A *verifiable* citation for the one-token prefill-isolation method that the paper currently attributes to an unverified source ([19]).

**E9. The Energy Cost of Reasoning: Analyzing Energy Usage in LLMs with Test-time Compute.** Y. Jin, G.-Y. Wei, D. Brooks. 2025. arXiv. https://arxiv.org/abs/2505.14733
- Test-time compute can beat model scaling on accuracy per unit of energy for complex reasoning, and output length interacts with that.
- Ties reasoning-token count to energy, which is the physical link ALIGN exploits. It also frames v4's effort ladder as an energy choice.

### 2.5 Measurement methodology, preregistration and blinding

**M1. Blind Analysis in Nuclear and Particle Physics.** J. R. Klein, A. Roodman. 2005. Annu. Rev. Nucl. Part. Sci. 55:141–163, DOI 10.1146/annurev.nucl.55.090704.151521.
- Metadata and abstract read via Crossref: https://api.crossref.org/works/10.1146/annurev.nucl.55.090704.151521 (the publisher page returned 403).
- Blinding keeps experimenters from seeing the result until the analysis is fixed.
- The sealed Block 5, with a desk program that reads no energy (`README.md:19`), is blind analysis in exactly this sense. Cite it to present the practice as established metrology.

**M2. The Preregistration Revolution.** B. A. Nosek, C. R. Ebersole, A. C. DeHaven, D. T. Mellor. 2018. PNAS 115(11):2600–2606, DOI 10.1073/pnas.1708274114. https://api.crossref.org/works/10.1073/pnas.1708274114 (the PNAS page returned 403)
- Preregistration separates prediction from postdiction and handles preexisting data and deviations.
- Supports the public deviation log and the lead-ruling process.

**M3. Pre-registration for Predictive Modeling.** J. M. Hofman, A. Chatzimparmpas, A. Sharma, D. J. Watts, J. Hullman. 2023. arXiv. https://arxiv.org/abs/2311.18807
- A lightweight preregistration template for ML, with a qualitative study of researchers.
- The closest ML-specific proposal. JouleWise extends the idea to *measurement systems*, adding seals and refusal records.

**M4. Scientific Benchmarking of Parallel Computing Systems: Twelve Ways to Tell the Masses when Reporting Performance Results.** T. Hoefler, R. Belli. 2015. SC15, pp. 73:1–73:12. https://htor.inf.ethz.ch/publications/index.php?pub=222
- A review of 120 HPC papers found reporting insufficient: many never show that improvements exceed noise.
- Gives systems reviewers a familiar anchor for JouleWise's detection floors.

**M5. Benchmarking Crimes: An Emerging Threat in Systems Security.** E. van der Kouwe, D. Andriesse, H. Bos, C. Giuffrida, G. Heiser. 2018. arXiv. https://arxiv.org/abs/1801.02381
- Catalogues 22 benchmarking crimes and finds about 5 per paper across 50 top-venue defenses.
- A checklist JouleWise can self-audit against before submission.

---

## 3. Supporting sources (opened; one line each)

| Source | URL | Use |
|---|---|---|
| Shumailov et al., *Sponge Examples: Energy-Latency Attacks on Neural Networks*, EuroS&P 2021 | https://arxiv.org/abs/2006.03463 | Adversarial inputs raise energy 10–200×; energy as a security quantity. The authors call for worst-case, not average-case, energy analysis |
| Benton et al., *Sabotage Evaluations for Frontier Models*, 2024 | https://arxiv.org/abs/2410.21514 | Threat models for sabotaging evaluation and oversight; background to SHADE-Arena |
| Mittapalli et al., *TRACE*, 2026 | https://arxiv.org/abs/2606.07054 | SHADE-Arena successor monitor that links evidence across steps; F1 0.713, recall 0.844 on 10 SHADE domains |
| Zhang, Li, Chen, Peng, *When LLM Defenses Backfire*, 2026 | https://arxiv.org/abs/2607.24392 | Multi-round defenses carry the largest runtime overhead; cost is reported in runtime, not joules |
| Cai, Shi, Zhao, Song, *Auditing Model Substitution in LLM APIs*, 2025 | https://arxiv.org/abs/2504.04715 | Software-only verification is "fundamentally unreliable"; proposes TEEs |
| Ong et al., *TOPLOC*, 2025 | https://arxiv.org/abs/2501.16007 | Activation-hash proofs of inference; a cryptographic alternative to physical audit |
| Shavit, *What Does It Take to Catch a Chinchilla?*, 2023 | https://arxiv.org/abs/2303.11341 | Compute-monitoring governance via on-chip logging; frames hardware-rooted verification |
| Weiss, Ayzenshteyn, Amit, Mirsky, *What Was Your Prompt?*, 2024 (USENIX Security '24 per my knowledge; arXiv page lists preprint) | https://arxiv.org/abs/2403.09751 | A token-length side channel reveals response content; token counts leak physically and through the network |
| Samsi et al., *From Words to Watts*, 2023 | https://arxiv.org/abs/2310.03003 | Early LLaMA inference energy on V100/A100 |
| Luccioni, Jernite, Strubell, *Power Hungry Processing*, FAccT 2024 | https://arxiv.org/abs/2311.16863 | General-purpose models cost orders of magnitude more per inference than task-specific ones |
| Fernandez et al., *Energy Considerations of LLM Inference and Efficiency Optimizations*, 2025 | https://arxiv.org/abs/2504.17674 | FLOP- or utilization-based estimates "significantly underestimate" real energy; optimizations save up to 73% |
| Chung et al., *The ML.ENERGY Benchmark*, NeurIPS D&B 2025 | https://arxiv.org/abs/2505.06371 | Leaderboard covering 40 architectures; already cited as [8] |
| Niu et al., *TokenPowerBench*, AAAI 2026 | https://arxiv.org/abs/2512.03024 | Prefill/decode attribution without meters; already cited as [7] |
| Husom et al., *Sustainable LLM Inference for Edge AI*, 2025 | https://arxiv.org/abs/2504.03360 | Raspberry Pi 4 with a hardware meter; trade-offs across quantization levels |
| Javat, Kazakov, *Silicon Showdown*, 2026 | https://arxiv.org/abs/2605.00519 | Up to 23× tokens per joule for Apple. The abstract does not name the energy method (the repo's earlier notes say NVIDIA board power vs Apple whole-SoC `powermetrics`) |
| Hübner, Hu, Peng, Markidis, *Apple vs. Oranges*, 2025 | https://arxiv.org/abs/2502.05317 | M1–M4 HPC benchmarks with power measured by `powermetrics`; no external validation visible |
| Zhang et al., *SiliconBench*, NeurIPS 2026 poster | https://neurips.cc/virtual/2026/poster/139658 | Ten Apple-silicon inference stacks compared on speed, memory and fidelity; no energy |
| Sinha et al., *Not All GPUs Are Created Equal*, SC22 | https://arxiv.org/abs/2208.11035 | Same-SKU GPUs vary 8% on average (up to 22%); limits generalizing from a single machine |
| Stojkovic et al., *TAPAS*, 2025 (ASPLOS '25 per search; not shown on the arXiv page) | https://arxiv.org/abs/2501.02600 | LLM inference phases have distinct thermal and power profiles |
| Nunez-Yanez et al., *Run-Time Power Modelling in Embedded GPUs with DVFS*, 2020 | https://arxiv.org/abs/2006.12176 | Tegra TX1 model that captures temperature effects on power |
| NVIDIA, *GEMM Performance Measurement Methodology Guidelines* (CUTLASS docs) | https://docs.nvidia.com/cutlass/latest/media/docs/cpp/gemm_performance_measurement_methodology_guidelines.html | Warm up until power stabilizes; cool down to idle; "power and thermal controllers may induce clock variability" |
| Roodman, *Blind Analysis in Particle Physics*, PhyStat2003 | https://arxiv.org/abs/physics/0312102 | Short companion to M1 |
| MacCoun, Perlmutter, *Blind analysis: Hide results to seek the truth*, Nature 526:187–189 (2015) | https://api.crossref.org/works/10.1038/526187a | **Content UNVERIFIED** (Nature redirected to login; metadata only via Crossref) |
| *NeurIPS 2021 Workshop on Pre-registration in ML*, PMLR vol. 181 | https://proceedings.mlr.press/v181/ | ML has run a preregistration review track |
| Kapoor, Narayanan, *Leakage and the Reproducibility Crisis in ML-based Science*, 2022 | https://arxiv.org/abs/2207.07048 | 329 papers affected by leakage; "model info sheets" |
| Bouthillier et al., *Accounting for Variance in ML Benchmarks*, 2021 | https://arxiv.org/abs/2103.03098 | Randomize more sources of variation; rates of false detection |
| Agarwal et al., *Deep RL at the Edge of the Statistical Precipice*, NeurIPS 2021 | https://arxiv.org/abs/2108.13264 | Interval estimates and robust aggregates for few runs |
| Kalibera, Jones, *Rigorous Benchmarking in Reasonable Time*, ISMM 2013 | https://kar.kent.ac.uk/33611/ | Plans repetitions at the levels with most variance; reports effect-size CIs |
| Mytkowicz et al., *Producing Wrong Data…*, ASPLOS '09 | https://api.crossref.org/works/10.1145/1508244.1508275 | Already cited as [31]; re-verified |
| Henderson et al., *Systematic Reporting of the Energy and Carbon Footprints of ML*, JMLR 21 (2020) | https://arxiv.org/abs/2002.05651 | Standardized energy-reporting appendices |
| Zhuang, Li, Fan, *Pre-Registering the Detectable Effect (Paired-MDE)*, 2026 | https://arxiv.org/abs/2605.28873 | Already cited as [26]; see §5 for a cite-to-claim concern |

---

## 4. Gaps JouleWise fills (positioning, with claim boundaries)

**G1. A token-level physical audit of an agent's logged work.**
- Neither hidden-token auditing (V1–V5) nor physical compute verification (V6–V8) fits a calibrated energy-from-logged-tokens model and uses its residual to flag omitted reasoning in multi-turn agent episodes.
- *Safe claim:* "a pre-registered test of whether measured energy detects known omissions of reasoning tokens from an LLM agent's log, on local hardware, reported as a detection curve over hidden tokens (H)".
- *Do not claim:* detecting sabotage as such, robustness to adaptive adversaries, or semantic monitoring.
- *Frame the result as* a per-episode, token-level analogue of Kimpson et al.'s β.

**G2. LLM energy measurement on Apple silicon that controls thermal state.**
- AgentStop, GreenBench, Hübner et al., IPW, MELT and Silicon Showdown do not gate on die or heatsink temperature. Hot Pixels shows why that matters on actively cooled Apple machines.
- *Safe claim:* "to our knowledge, the first LLM energy protocol with registered thermal start and per-turn gates on Apple silicon".
- *Do not claim* that the gates transfer to other devices.

**G3. Validation of `powermetrics` on the time axis.**
- NVIDIA sensors have a timing literature (A8–A10). Apple publishes only an "estimated and may be inaccurate" disclaimer (A1).
- JouleWise's phase-edge attribution bound at 100 ms is new.
- *Do not claim gain accuracy:* there is no external meter.

**G4. Blind, preregistered energy measurement in ML systems.**
- None of the energy papers reviewed preregister or blind.
- JouleWise transplants blind analysis (M1) and preregistration (M2, M3), adding refusal records.
- Frame this proportionately, as method hygiene with precedent, not as the contribution.

**G5. Monitoring cost in joules.**
- Control and monitoring papers report cost as performance or abstract budget (B5, B6, B10). Agent-energy papers (A3, B11) do not measure monitor catch rates.
- RQ-ALIGN-EFFICIENCY-MONITORABILITY is open territory, and B10's framework accepts joules as its cost input directly.

**G6. An energy model for multi-turn, cached-prefix episodes.**
- Wilkins (E2) and Vellaisamy (E3) model single requests. ALIGN's cumulative-context design is new for agent episodes, subject to the hybrid-architecture caveat (E4, E5).

---

## 5. Concrete bibliography actions for `draft-v1.md` §11

Rows are cited by number in `bd7a3efcd:docs/paper/bibliography-audit-2026-08-27.md:99-112` and `draft-v1.md:374-387`.

- **[13] Benazir & Lin.** Crossref confirms the POMACS 9(3):1–26 (Dec 2025) metadata, so the status can move to VERIFIED-ONLINE. The arXiv preprint has a different title (2508.08531). The body sentence at `draft-v1.md:332` now correctly says "without energy measurement".
- **[19] Ruf & Detyniecki (HotCarbon '26).** Still **UNVERIFIED**. Three targeted searches found no record. Delavande, Pierrard & Luccioni (arXiv 2601.22362) verifiably uses the one-token prefill isolation with decode by subtraction. It runs 10 repetitions, though, so the critique "one run per context length without error bars" (`draft-v1.md:332`) would **not** transfer if the citation is swapped; the sentence would need rewording.
- **[20] Illusion of Power Capping.** v2 is dated 29 October 2026 and the paper is accepted to PPAM 2026, so update the entry. The v2 abstract does not mention the independent NVML energy-counter cross-check that `draft-v1.md:330` relies on. Re-check the v2 full text before keeping that sentence.
- **[22] IPW.** The arXiv v7 comment says NeurIPS 2026; update the venue.
- **[23] Dauner et al.** Metadata and the PDF URL are verified (HotCarbon '26, paper-46). The finding about stale NVML reads under 100 ms is confirmed at summary level. The "severe underestimate on one GPU" detail still needs the PDF text.
- **[26] Paired-MDE.** The abstract describes a conservative, pre-committed MDE budget and a five-line template, but **not** the "raise but not lower" threshold behaviour that `draft-v1.md:342` attributes to it. Check the full text or soften the sentence.
- **New citations recommended for `draft-v1.md` §8:**
  - Yang et al. SC24 (A8) and Burtscher et al. 2014 (A9), for the counter-time lineage.
  - The `powermetrics` man page (A1), for the estimate disclaimer.
  - Hot Pixels (A2), for thermal/power coupling on Apple.
  - AgentStop (A3), the closest Apple `powermetrics` LLM study.

---

## 6. Threats the literature raises for ALIGN (for the registration cold gate and the paper)

- **T1. Tamper-evidence boundary (V6, A2).** The record is a host-software counter.
  - Option (a): state the privilege boundary (the agent runs unprivileged; powermetrics runs as root via the harness).
  - Option (b): add an external DC or wall meter as a cross-check on episode totals. JouleSort-style wall metering validates totals only, as the paper already notes.
- **T2. Adaptive adversary (V7, B2).** The estimand holds measured joules fixed and strips logged counts (`pilot_protocol_v3.md:155-163`; `v4:508-516`). That is a non-adaptive omission. A matched-energy mimic, one that pads logged counts elsewhere to cover hidden ones, is out of scope and must be named as such.
- **T3. Model misspecification for hybrid attention (E4, E5).** Add a print-only fit with the context-quadratic terms restricted to D's full-attention fraction of layers, or a context-linear variant, and report the change in s_r.
- **T4. Phases are not separable (E6).** Prefill state changes the cost of each decoded token. Turn-owned attribution should say that cross-phase coupling is absorbed into the fitted coefficients, not removed.
- **T5. Thermal coupling (A2, A7, CUTLASS, Nunez-Yanez).** These support the gates, but they also mean gated energy is reference-state energy, not production energy. v4 already says this (`:514-516`); keep it in the paper.
- **T6. Generalizing from one unit (Sinha et al.).** Same-SKU variability (8% average, up to 22%) means single-MBP results should be framed as device-specific.

---

## 7. UNVERIFIED or partially verified items

- **Ruf & Detyniecki, "The Cost of Context" (HotCarbon '26):** not found anywhere. UNVERIFIED.
- **MacCoun & Perlmutter, Nature 2015:** Crossref metadata only; content UNVERIFIED.
- **Dauner et al.:** the PDF downloaded but could not be text-extracted (no poppler on the Air). Findings come from a co-author organisation's page, so they are verified at metadata and summary level only.
- **Burtscher et al. 2014:** I opened the authors' tool page, not the paper text.
- **Venues taken from my own knowledge, not from the pages I opened:** Splitwise (ISCA 2024), Weiss et al. (USENIX Security 2024), Samsi et al. (HPEC 2023), TAPAS (ASPLOS '25; the search shows it, the arXiv page does not), Solovyeva & Castor (EASE 2026; a search listing only).
- **Abstract-level only:** these papers' details come from abstracts, plus HTML for Wilkins, AgentStop, Hot Pixels and Delavande. Every quantitative claim above is from an abstract or an HTML page I opened. Nothing is from memory.

---

## 8. Process note

Sources were opened with WebFetch, mostly arXiv abstract pages, plus ACL Anthology, USENIX, Crossref, ICML and NeurIPS virtual pages, and authors' pages. No Block-5 artifact, restricted path or rehearsal fixture was read. Nothing was committed or merged. This report is the deliverable for the collector to store.
~~~~
