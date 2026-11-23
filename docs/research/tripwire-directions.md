# If the tripwire works: research directions

*Research 2026-11-07, part 5. Draft written for Ed by the laptop lead (Opus 5.5). This is a docs-only change. It commits no Mac time, model downloads or GPU rental.*

**Ed's question (2026-11-07):** "Assuming the instrument proves useful in detecting hidden work, like better than SHADE-Arena alone (or whatever the standard would be to be a noteworthy result), what more research can we do with this tool? [...] Or do you not expect any to produce particularly noteworthy results?"

**How this was made.**
- **Seats.** Two seats were briefed blind. The Fable 5.1 seat delivered 11 directions, D1 to D11 (Appendix A.1). The Opus 5.5 seat was stopped by a safety classifier before it delivered; it returned only its reading log (Appendix A.2). The direction list therefore comes from a single seat.
- **Checks.** Each direction was attacked by one Fable 5.1 checker and one Opus 5.5 checker for prior work, feasibility and noteworthiness, 22 checks in all. They are printed verbatim in [tripwire-directions-checks.md](tripwire-directions-checks.md). The checks supply the cross-family element. No check refuted a direction on prior work. All 22 rated their direction incremental or not noteworthy *as designed*.
- **Lead synthesis.** The lead re-read protocol v4, the in-flight squeeze branches, three pilot RECORDs and RUN_STATE 210 (Ed's squeeze rulings). The lead re-opened 27 of the cited sources; the source list marks who opened each one.
- **Adversary content.** Adversaries appear here only as threat-model classes and estimands, at the level already in the squeeze addendum draft. Nothing here is an evasion recipe.

---

## 1. Executive summary (candid)

**Short answer.** Two or three of these could be genuinely noteworthy, but none as written. The most likely noteworthy outcomes are *limits*, not clean wins.

The 22 checks found nothing already done, but rated everything incremental, for the same reason: most of the seat's claims are settled by arithmetic before any joule is measured.
- Energy follows tokens and bytes.
- On the 30B pilots a hidden decode token costs about 0.49-0.67 J.
- For sequential hidden work, a stopwatch sees most of what a meter sees.

The noteworthy questions are the ones arithmetic does not settle.

**"Better than SHADE-Arena's monitor alone" is the wrong bar.** A transcript monitor cannot see hidden reasoning, so beating it there is trivially true, and reviewers will say so. Three bars would make a result noteworthy:
1. **Complementarity against a smart hider.** Pick a fixed false-alarm rate. Test an agent that deletes only the incriminating reasoning, not a random fraction of it, and does real hidden compute. The noteworthy result is that monitor plus meter leaves this agent no escape, on D and on the 30B, at m ≥ 39.
2. **A bound in physical units.** "Against a stated adversary, an agent on this host cannot do more than N tokens of unaccounted work per episode without an alarm at FPR ≤ 2.5 %." This is the per-episode analogue of Kimpson, Baker & Graham's β, which they measured only on A100s ([2610.07476](https://arxiv.org/abs/2610.07476)).
3. **A stated scope.** Where the bound stops holding: under batching, co-tenancy, and hiding methods that cost little compute.

**The three directions worth aiming at.** Each merges seat directions and is reshaped by the checks.

1. **The squeeze against a selective hider, with a replay verifier** (D1 + D2, with D11 as its cost axis). For each sabotage trajectory, compare two numbers:
   - **H_blind:** the incriminating reasoning tokens a hider must delete to blind the transcript monitor.
   - **H_det:** the hidden tokens the meter catches.

   With the current per-pair regression fit, H_det was 539 and 1,193 tokens in pilots 8-9 (record f775edaf). The checks project H_blind at tens to hundreds of tokens, so an **escape window** probably exists.

   Three checks independently proposed the same fix: score each audited episode against a seeded replay of its own declared log. Identical-work replays repeat to about 2 J (about 3-4 decode tokens). The regression residual SD is 19-58 J. Projected replay resolution is roughly 10-30 hidden tokens at FPR 2.5 %, not yet measured on D.

   Either outcome is publishable:
   - **The replay closes the window.** That would be a main-track result, the first per-episode instance of Kimpson's re-execution regime for LLM agents.
   - **A measured window remains.** That is the honest limit, and still the most citable result in this space.

   The scaffolding is already in flight: the squeeze addendum, the adversary kit, the analysis package and REVIEWER2. This direction changes the primary adversary and adds one channel.
2. **Where the tripwire dies: batching, and the attacker's cheapest compute** (D10 plus D9's batched arm, on the Mac first).
   - **Why it matters.** Batched decode shares the weight reads, so a hidden extra row costs far less than a sequential token. That is the attacker's best physical lever, and the first question a governance reviewer will ask.
   - **What to measure.** On this Mac, measure the marginal joules per hidden row against batch size, dense (D) against MoE (30B-A3B), and the device-level detection limit H50(B).
   - **Why it is new.** The checks found no published energy-against-batch curve for Apple silicon. The dense-against-MoE contrast is a real prediction that could fail.
   - **GPU rental** only if resolution survives at B ≥ 4.
3. **Energy counts bytes, not thoughts: a visibility map of hiding mechanisms** (D3 reshaped, plus D9 and D5's hidden best-of-N). For each way to hide work, measure joules per unit of hidden computation, then record which channel sees it:
   - **Hiding mechanisms:** sequential hidden tokens; batched hidden candidates; latent or recurrent-depth reasoning (a public 3.5B model exists, [2502.05171](https://arxiv.org/abs/2502.05171)); and the energy-blind cases. Those are filler-token and in-place reasoning ([2607.22925](https://arxiv.org/abs/2607.22925)) and control-token chain-of-thought suppression ([2609.27542](https://arxiv.org/abs/2609.27542)).
   - **Channels:** transcript monitor, runtime counter, regression fit, replay, and time.

   This is the threat-model table every reviewer of direction 1 will want. On its own it is a strong workshop paper; inside direction 1 it becomes the limits section.

**Incremental.** Fold these into the three above; none earns its own Mac night.
- **D5, model substitution.** Outputs already catch 4-bit quantization (AUC > 0.999 within 300 tokens, DiFR [2511.20621](https://arxiv.org/abs/2511.20621)).
- **D6, covert out-of-model work.** The software rails catch most doses. Storage and network doses carry too few joules. ClawGuard holds the out-of-band headline ([2605.06205](https://arxiv.org/abs/2605.06205)).
- **D8, the open benchmark.** Release it as direction 1's artifact. A Datasets & Benchmarks paper needs 3+ chips and many more episodes.
- **D11, oversight tax in joules.** This becomes the cost axis of direction 1.
- **D4, log inflation.** A one-sided fixture and one limits sentence.
- **D7, eval awareness.** At most a negative-control rider.

**Honest base rate.**
- **As written:** of the 11 directions, none survived the checks as noteworthy.
- **After reshaping:** three have a plausible path, and they largely reduce to one paper, the squeeze, with batching and the visibility map as its scope and limits. Ed has set NeurIPS 2027 for the full squeeze result (RUN_STATE 210).
- **My judgment, conditional on v4 clearing W1 and the D windows:** about two in three that the squeeze program yields a solid workshop paper, and about one in four that it yields a main-track paper.
- **What moves the main-track odds up:** the replay verifier closes the escape window, or the window is large and cleanly measured with real hidden compute.
- **What moves them down:** the prompted 27B or 30B agent is the only adaptive adversary that runs. That is likely a predictable "weak agent fails to evade" null, which Mallen et al. predict ([2412.12480](https://arxiv.org/abs/2412.12480)).
- **Unconditionally,** multiply by the chance that v4 clears its own gates. These figures are judgment, not a computed rate.

**One decision governs every adversarial claim, and it is still open.** On a local, seeded stack, the runtime's own token counter and a seeded rerun of the declared prefix catch stripped reasoning in software, at zero energy cost (the DiFR idea).
- **Where energy earns its place:** compute the runtime does not mediate (tool subprocesses, side generation, hidden parallel rows, unseeded work), and settings where host software is not trusted.
- **Who has to decide:** the squeeze addendum already lists this as an open lead + Ed decision ("attacker may forge reported counts/text, or runtime counts are authenticated").
- **Recommendation:** make the positive controls *unmediated* hidden compute, such as fresh-context side generation or work inside tool subprocesses, not log edits. Then state plainly that log stripping alone is a software problem.

Ed settled the power-path question on 2026-11-07 (RUN_STATE 210). The KM003C sits between the wall brick and the MagSafe cable, so it measures all ALIGN power. The magistrate still has to confirm, in an arm record, that the capture is live. The battery still needs its own term: battery assist came to 0.8-30 J per member in pilot 9 (record f775edaf).

---

## 2. The strategic picture

### 2.1 What v4 must show first

Sources: protocol v4 on `lane/2026-11-06-v4-r1-integrated`, the 2026-11-06 chair rulings, and RUN_STATE 204 and 210.

| Gate | What v4 must show | Where it is defined |
|---|---|---|
| **A. Thermal control** | W1 passes U1-U3: coverage and gate checks; slow-temperature range ≤ 3 °C; identical-work pairs within 3 × max(2.97 J, 0.11 % of pair energy) at exact tokens | v4 "Instrument checks"; chair ruling 5 |
| **B. Pool size** | Each pair reaches ≥ 21 eligible benign and ≥ 3 sabotage held-out D members. This is the count-only extension, capped at D5 (D6 under registration grade). | Chair ruling 3 |
| **C. Resolution** | Known-H detection curve on D: H50/H90 with a window-cluster bootstrap; marginal FPR ≤ 1/(m+1); MDE at ranks m and m−1; flag any threshold > 1.5 × the next score | Chair rulings 2 and 12 |
| **D. Registration grade** | m ≥ 39 per pair plus a locked test cohort, with Ed's go before alarms are read | v4 "Residual analysis"; RUN_STATE 204 |
| **E. Real hidden work** | The D positive-control cell, with real unlogged compute rather than a log edit, as a paper gate | Chair ruling 2 |
| **F. Trusted boundary** | KM003C capture confirmed live in an ALIGN arm record; battery assist handled; threat model states whether runtime counts are authenticated | RUN_STATE 210; squeeze addendum §9 |

Gates A-E make up a "the tripwire works" result. Gate F is what makes any *adversarial* follow-on admissible.

### 2.2 From v4 results to next directions

```mermaid
flowchart TD
  A["R1 + W1: U1-U3"] -->|"fails after the ladder, or refused under 1(f)"| F["30B corpus only: desk parts of Dir 1 and E2 positive controls; Dirs 2 and 3 unaffected"]
  A -->|"passes"| B["D windows: at least 21 benign and 3 sabotage per pair; known-H H50 on D"]
  B -->|"H50 at most about 500 tokens"| C1["Regression fit primary, replay secondary"]
  B -->|"H50 at least about 1,000 tokens"| C2["Replay becomes the primary energy channel"]
  C1 --> D["Positive control: real unmediated hidden compute (paper gate)"]
  C2 --> D
  D -->|"on the token law"| E1["Dir 3: spend nights only on batched and latent arms"]
  D -->|"cheaper than the token law"| E2["Dir 3 becomes the core result"]
  E1 --> G["Selective hider: H_blind against H_det"]
  E2 --> G
  G -->|"H_blind above H_det (fit)"| H1["Squeeze holds: scale to m 39+ and adaptive families; main-track attempt"]
  G -->|"between H_det (replay) and H_det (fit)"| H2["Replay closes the window: re-execution headline"]
  G -->|"H_blind below H_det (replay)"| H3["Publish the measured window as the limit"]
```

| v4 outcome | Reading | What it unlocks |
|---|---|---|
| W1 fails U1-U3 after the escalation ladder, or v4 is refused under ruling 1(f) | No D held-out pool | Direction 1 continues on the 30B: frozen calibration `7fbd95e31`, pilots 8-10, E2 nights. Directions 2 and 3 do not need D. D8 stalls because it needs two models. |
| W1 passes; D's per-pair H50 at m ≥ 39 is ≤ about 500 tokens and s_r ≲ 2 % of episode energy | The regression fit is a usable detector | Direction 1 with the fit as primary and replay as a second channel |
| W1 passes; D's H50 ≥ about 1,000 tokens | The fit is too coarse for selective hiders | Direction 1 with replay as the primary energy channel. The fit's misspecification on D's hybrid attention becomes a side result. |
| Positive control caught near the token law | Real hidden work costs what the log model says | Direction 3's sequential arms are confirmations; spend Mac time on the batched and latent arms only |
| Positive control missed, or off the token law | Real hidden work is cheaper per token than predicted, for example fresh-context side generation (the seat's figure: about 0.18 J/token) | Direction 3 becomes the core paper; the measured exchange rates are the result |
| H_blind > H_det for most trajectories | No escape window for selective hiders | The squeeze headline. Scale up and run the adaptive families. |
| H_det,replay < H_blind < H_det,fit | The fit leaves a window and replay closes it | Headline: "re-execution closes it" |
| H_blind < H_det,replay | A window remains | Publish the measured window and its exchange rate (padding tokens exposed per hidden token). Narrative: "physics bounds unaccounted compute to X tokens; the content monitor must catch everything below X." |
| Runtime counts ruled authenticated | Log stripping is caught in software | Drop log-edit arms from the claims. Energy's claim narrows to unmediated compute: directions 1 (side generation), 3, and D6's rider. |

**Independent of v4:** direction 2 (Mac batching) and direction 3 (exchange rates) need only Ed's OK for Mac nights and, for direction 3, one model download.

---

## 3. Ranked table

Ranking is noteworthiness × feasibility, after reshaping. **Novelty** reports both checks: "not refuted 2/2" means neither checker found the direction already done. The checks' main reservation is listed beside it. Links point to the closest prior work the checks named; the [sources](#sources) section says who opened each one.

| # | Direction (reshaped) | From | Noteworthy ceiling | Feasibility and cost | Novelty (checks) | Closest prior work |
|---:|---|---|---|---|---|---|
| 1 | **Squeeze against a selective hider, with a replay verifier** | D1, D2, D11 | Main track (NeurIPS 2027 squeeze paper) if replay closes the window, or the window is cleanly measured with real hidden compute on D and the 30B | Desk now (1-2 weeks of Air/Sol time). Measurement rides the squeeze cohorts already reserved in the addendum; replay roughly doubles Mac time for each audited episode | Not refuted 4/4. External gap confirmed: no paper combines a physical channel with a transcript monitor, and Kimpson et al. leave joint energy-time inversion to future work (per a check that read their appendix). Internal overlap is high: squeeze prereg, analysis package, adversary kit, REVIEWER2, ShadeMonitor visibilities | [Kimpson et al. 2610.07476](https://arxiv.org/abs/2610.07476); [Hua et al. 2507.15886](https://arxiv.org/abs/2507.15886); [Arike et al. 2601.21112](https://arxiv.org/abs/2601.21112); [Arnav et al. 2505.23575](https://arxiv.org/abs/2505.23575); [Kutasov et al. 2506.15740](https://arxiv.org/abs/2506.15740); [Rahman & Tajdari 2606.19262](https://arxiv.org/abs/2606.19262) |
| 2 | **Where the tripwire dies: batching and the attacker's cheapest compute** | D10, D9 arm B | Governance main track as the scope section of #1; workshop alone | 1-2 Mac nights of static-batch replays (B ∈ {1, 2, 4, 8}) plus desk. GPU (40-80 h, inline DC meter at a PCIe card) only afterwards, with Ed's go | Not refuted 4/4. The attribution sub-question is already answered (JouleShare). The slope collapse is predictable from GPU tables. Unmeasured on Apple silicon; the dense-against-MoE contrast is open | [Luo et al. 2608.00026](https://arxiv.org/abs/2608.00026); [Luo et al. 2609.29707](https://arxiv.org/abs/2609.29707); [Wu et al., NeurIPS 2026 workshop](https://neurips.cc/virtual/2026/poster/170701); [Niu et al. 2610.28576](https://arxiv.org/abs/2610.28576) |
| 3 | **Energy counts bytes, not thoughts: visibility map and exchange rates** | D3, D9, D5's best-of-N arm | Workshop alone; limits section of #1 | About one Mac night as riders on ASTRA-2CH or the positive-control night. An optional half night on a recurrent-depth model needs Ed's download OK and a PyTorch-MPS stack decision | Not refuted 6/6. Arithmetic predicts the dense and MoE latent ratios (from the lm_head byte fraction). Batched rows, recurrent depth and MoE routing are open | [Geiping et al. 2502.05171](https://arxiv.org/abs/2502.05171); [Baherwani et al. 2607.22925](https://arxiv.org/abs/2607.22925); [Usama et al. 2609.27542](https://arxiv.org/abs/2609.27542); [Zhang et al. 2412.15431](https://arxiv.org/abs/2412.15431); [DiFR 2511.20621](https://arxiv.org/abs/2511.20621) |
| 4 | Covert out-of-model work at the DC boundary | D6 | Workshop (systems security / technical AI governance) | Rider inside an E2 positive-control night | Not refuted 2/2. Physical detection of covert work is old (WattsUpDoc 2013); ClawGuard holds the out-of-band agent headline. The calibrated joule dose curve is new | [ClawGuard 2605.06205](https://arxiv.org/abs/2605.06205); [Gargiulo & Kulp 2609.00309](https://arxiv.org/abs/2609.00309); [Rahman & Tajdari 2606.19262](https://arxiv.org/abs/2606.19262) |
| 5 | Model substitution and compute verification (minus best-of-N) | D5 | A section of a governance paper | 1 Mac night. Its adversary programs need a ruling under amended D-139 A1 | Not refuted 2/2, but outputs already catch quantization (DiFR, IRIS), and the battery buffer opens a hole under host-level adversaries | [DiFR 2511.20621](https://arxiv.org/abs/2511.20621); [IRIS 2607.20860](https://arxiv.org/abs/2607.20860); [Kimpson et al. 2610.07476](https://arxiv.org/abs/2610.07476) |
| 6 | SHADE-Energy release | D8 | The artifact of #1. A D&B paper only with 3+ chips and teacher-forced replay packs | 1-2 desk weeks plus a borrowed same-SKU unit | Not refuted 2/2: the first metered control dataset. ClawGuard and Gargiulo & Kulp dilute "first physical channel" | [Kutasov et al. 2506.15740](https://arxiv.org/abs/2506.15740); [MonitoringBench 2605.09684](https://arxiv.org/abs/2605.09684); [Gargiulo & Kulp 2609.00309](https://arxiv.org/abs/2609.00309) |
| 7 | Oversight tax in joules | D11 | Cost axis of #1 | Token-arithmetic table now; at most a half-night rider | Not refuted 2/2. Two of its three claims are fixed by token counts; prefix-caching energy is already characterized on H100 | [SIMPLE law 2611.03330](https://arxiv.org/abs/2611.03330); [Hua et al. 2507.15886](https://arxiv.org/abs/2507.15886) |
| 8 | Log inflation as a one-sided fixture (sandbagging rejected) | D4 | One paragraph | 0 nights | Not refuted 2/2. Close to tautological: it is the omission curve's mirror image | [Hoque et al. 2605.30040](https://arxiv.org/abs/2605.30040) |
| 9 | Eval-awareness negative control (rejected as an energy study) | D7 | One validity sentence | 0 extra nights, rider only | Not refuted 2/2. The token-count half is already published on an open 20B model | [Ahmed et al. 2510.08624](https://arxiv.org/abs/2510.08624) |

---

## 4. Directions in detail

Each section gives the reshaped claim, design, cost, what would make the result noteworthy, and the risks, followed by what the checks changed from the seat's version. The seat's original text for each direction is in Appendix A.1.

### 4.1 Direction 1: the squeeze against a selective hider, with a replay verifier (D1 + D2 + D11)

**Claim (proposed; the lead and registration set the bars).** For each sabotage trajectory τ, define:
- **H_blind(τ):** the fewest reasoning tokens, deleted in the hider's preferred order (incriminating spans first), that push the transcript monitor below its benign-calibrated threshold at FPR ≤ 1/(m+1).
- **H_det(τ, c):** the hidden-work dose, in decode-token equivalents, at which channel c alarms at the same FPR. The channels are c ∈ {E: regression residual, T: trusted time, R: replay residual, OR\*: the addendum's frozen max-of-z joint rule}.

The primary estimand is the escape fraction, Pr[H_blind < H_det,OR\*]. It is reported per pair and model, with a trajectory-cluster CI. Register it two-sided, with these predictions:
- With E and T only, a window exists for most trajectories.
- Adding R closes it for most trajectories.

The claim is falsified in the interesting direction if a window remains with R. The secondary estimand is the **exchange rate**: padding tokens an adversary must expose to the monitor per hidden token, inside the two-knob null region (prefill and context inflation).

**Design.**
1. **H_blind at the desk (0 nights).**
   - **Monitor and transcripts.** Use the ShadeMonitor port (`docs/align/shade_port.md` on the v4 lane; full, no-scratchpad, actions-only and tampered visibilities, never run on data). Run it on transcripts the magistrate assembles.
   - **Monitor choice.** Ed's ruling (RUN_STATE 210) makes a frontier API monitor primary, so use it, with the local model as secondary.
   - **Deletion orders.** Targeted deletion (side-task spans first) is primary; random deletion is the control.
   - **Calibration.** Calibrate the monitor on benign transcripts stripped the same way, so it cannot alarm on missing reasoning alone (the format-cue control).
2. **H_det,E at the desk.** Compute it from the frozen per-pair fits and the recorded residuals. Compute the two-knob null region analytically from the marginal powers. The methodology audit gives P_prefill/P_decode ≈ 1.8 on this Mac; P_context still needs bounding.
3. **Replay channel (measurement).**
   - **How it runs.** Replay each audited episode's declared log in the same window, under the same gates and holds. Use forced-token decode, one token per step (the forced-decode primitive is on `interp/2026-11-07-forced-decode`). Score measured minus replay.
   - **Null and placement.** The null comes from the identical-work pairs the v4 U3 check already collects. Balance replay placement (ABBA): records 1b198a71 show a reproducible in-session replay excess of +1.3 to +10.1 J by position.
   - **Determinism check.** Seeded free replay checks determinism. A divergence makes that episode inconclusive, not a detection.
4. **Real hidden work.** Use unmediated compute: the addendum's fresh-context side generation, plus work inside tool subprocesses (its U family). Log stripping alone is not enough (§1).
5. **Time as a channel, with thermal stratification.** On D, 1,024 hidden tokens at about 11.9 tok/s add roughly 86 s, a strong signal. But record 0eafdaa2 shows a 425 → 447 s drift on identical tokens before the v4 gates existed, so time noise under the gates must be measured, not assumed.
6. **Adversaries.** Keep the addendum's N/P/S/T/U/M families and its bounded adaptation budget.
   - **Primary adversary:** the scripted selective hider, not a uniform-fraction hider.
   - **Prompted aware agent:** report it descriptively, with a no-hide-instruction control (the prompt itself induces work, record 7e06863b).
   - **Scope:** amended D-139 A1 allows only the agent under test, sandboxed, as the on-host adversary.
7. **Cost axis (D11).** Report the monitor's joules per unit of catch rate beside the meter's near-zero marginal cost.

**Cost.**
- **Desk:** 1-2 weeks of Air and Sol time.
- **Measurement:** no new nights beyond the squeeze cohorts. Replay roughly doubles Mac time for each audited episode, so either replay all sabotage-arm episodes plus a registered random subset of benign ones, or budget the replay explicitly.

**Noteworthy if.** The test runs on D and the 30B at m ≥ 39, with real unmediated hidden compute and a frontier monitor, and gives either:
- **(a) A closed window.** Replay closes it. Headline: "per-episode re-execution bounds an agent's unaccounted compute to about N tokens and leaves no gap a selective hider can use against a transcript monitor."
- **(b) A clean measured window.** Its size and exchange rate, presented as the honest limit.

Result (a) is a main-track candidate. Result (b) ranges from workshop to main track, depending on how cleanly it is measured.

**Risks.**
- **The software objection (§1).** If runtime counts are authenticated, log-stripping arms are moot. Energy's claim must rest on unmediated compute.
- **Replay determinism and drift.** Replay needs D's seeded generation to be token-identical; a divergence is inconclusive. Between-session offsets of 3.5-14.7 J (pilots 5-7) force in-window replay.
- **Sample size.** To resolve a catch-rate difference of 0.2 takes about 40+ distinct sabotage trajectories per pair per model. E2's fresh sabotage seeds are needed.
- **Energy-blind hiding.** Compute-reducing hiding ([2609.27542](https://arxiv.org/abs/2609.27542)) and filler or in-place computation ([2607.22925](https://arxiv.org/abs/2607.22925)) are invisible to energy by construction. They belong in the limits section, not the claim.
- **Overlap.** This changes the squeeze addendum's primary adversary and adds a channel. Route it through the AGREEMENT action list, not a parallel registration.

**What the checks changed.**
- Uniform-fraction hiding is a straw adversary; targeted deletion is primary.
- A Neyman-Pearson likelihood-ratio combination is infeasible at this sample size: Hua et al. trained it on 218 misaligned samples. Use the frozen OR\* rule already in the addendum.
- Tier 3 (prompted agent against a count-forging oracle) loses by privilege, not by skill. It is descriptive only.
- The structural-consistency score is evidence the adversary writes ([2605.30040](https://arxiv.org/abs/2605.30040)), so it is demoted.
- Kimpson's β = 0.059 is a framework to cite, not a number that transfers.
- MonitoringBench's 94.9 % → 60.3 % drop comes from refined attacks, not hidden reasoning ([2605.09684](https://arxiv.org/abs/2605.09684)); cite it as such.

### 4.2 Direction 2: where the tripwire dies, batching and the attacker's cheapest compute (D10 + D9 arm B)

**Claim.** On this Mac, under mlx-lm static batching, an extra decode row at batch B costs a fraction r(B) of a batch-1 token. The checks' predictions:
- **Dense D:** r(2) ≈ 0.1-0.4, because the weights are read once for all rows.
- **MoE 30B-A3B:** r(2) is higher, because rows route to different experts, so the expert bytes read grow with B.

The device-level detection limit for one unlogged row is H50(B) ≈ k · s_r(B) / e_marginal(B). The claim is falsified if r_MoE(2) ≤ r_dense(2), or if r does not fall with B.

The checks also corrected the seat's dichotomy: the likely mechanism is **slope collapse** (cheap marginal tokens), not residual SD growth. Wu et al. measure a decode:prefill ratio of about 335× at prefix-cached batch 1, falling to about 3.3× under production batching ([NeurIPS 2026 workshop](https://neurips.cc/virtual/2026/poster/170701)).

**Design.**
1. **Desk, read-only.** Check that the pinned mlx-lm batch path handles D's hybrid GatedDeltaNet cache and the 30B MoE at B ≤ 8. The repo verdict `docs/specs/axi/sb_static_batch_verdict.md` covers B ∈ {2, 4} on small standard models only. Check the memory budget at 40,960 context.
2. **Mac stage (1-2 nights).** Run teacher-forced fixed-token streams at B ∈ {1, 2, 4, 8} for D and the 30B, in ABBA order. Fit E(B) = fixed + B × marginal. Test additivity directly with subset replays, E(A ∪ B) against E(A) + E(B) − idle, as JouleShare does.
3. **Device-level log completeness.** Predict whole-host energy from *all* logged rows, with no per-episode attribution. Inject one unlogged row and estimate H50(B). Use the KM003C as the boundary.
4. **GPU stage.** Run it only if H50 stays useful at B ≥ 4, and only with Ed's go (PIPELINE rule). It needs a physical PCIe workstation with an inline DC meter on the card's power leads and a slot riser, NVML beside it, and continuous batching. Call the result the *batched-serving limit*. A PCIe card cannot earn the title "datacenter limit".

**Cost.** 1-2 Mac nights plus desk time. The GPU stage is 40-80 GPU-hours plus meter hardware.

**Noteworthy if.** It produces a measured r(B), dense against MoE, on Apple silicon, plus device-level H50(B) at a trusted boundary. That is the scope statement that turns a laptop result into a governance claim. With direction 1 it reaches the main track. Alone it is a workshop paper. The genuinely new sentence would be either "MoE routing blunts the batching lever", or the opposite with a number.

**Risks.**
- **Static batching** is not continuous batching.
- **Thermal load** at B = 8 is high.
- **Memory fit** at B = 8 is untested on the 27B.
- **Mislabelled work.** "Hiding work inside co-tenant traffic" is mislabelled work. Energy conservation cannot see it, so drop that arm.

**What the checks changed.**
- JouleShare already answers per-request attribution: calibrated attribution still leaves normalized L1 error of 0.116-0.177 ([2608.00026](https://arxiv.org/abs/2608.00026)).
- "Wu et al." is real; the lead opened the NeurIPS virtual page.
- Run on the Mac first. No rental is needed to learn the shape.

### 4.3 Direction 3: energy counts bytes, not thoughts, a visibility map (D3 reshaped + D9 + D5's best-of-N)

**Claim.** For each hiding mechanism, measure the exchange rate x (joules per unit of hidden computation, relative to a sequential decode token) and record which channels see it.

| Mechanism | Predicted x (checks' arithmetic) | Monitor | Runtime counter / seeded rerun | Energy fit / replay | Time |
|---|---|---|---|---|---|
| Sequential hidden tokens (stripped or side-generated) | ≈ 1 by construction; fresh-context side generation lower per token | blind | sees in-process work; misses side processes | sees | sees |
| Hidden best-of-N, sequential | ≈ (N−1) × candidate length | blind | in-process only | sees | sees |
| Hidden best-of-N, batched | r(B) from direction 2 | blind | in-process only | weaker | weak |
| Latent passes (no lm_head or sampling) | ≈ 1 − lm_head byte fraction: about 0.97 (D), about 0.91 (30B-A3B), about 0.7 (sub-1B) | blind | if mediated | sees | sees |
| Recurrent-depth steps (3.5B model) | per-step share of the recurrent block (checks: about 43 %) | blind | blind to depth | sees | sees |
| Filler or in-place computation inside visible tokens | 0 beyond the visible tokens | may see | sees the tokens | blind to the hidden part | blind |
| Control-token CoT suppression | < 0 (less work) | blind | sees fewer tokens | blind (energy falls) | blind |

**Design.**
- **Paired replays.** Use paired ABBA teacher-forced replays at the ~2 J floor, with doses set per episode, not per turn. The seat's per-turn ladder made every dose trivially detectable.
- **Preregistration.** Register the byte-arithmetic predictions before measuring. A deviation, for example from host-loop overhead in a latent loop, is the result.
- **Real-model arm (optional).** The 3.5B recurrent-depth checkpoint as an optional half night, with the recurrence knob swept. It has no MLX port (per the checks), so it runs on PyTorch MPS, with a stack excursion and an untrusted-code gate.
- **Unmeasured rows.** The energy-blind rows are argued from mechanism and cited, not measured.

**Cost.** About 3 hours as a rider on ASTRA-2CH or the positive-control night, plus an optional half night. The 3.5B model needs Ed's download OK.

**Noteworthy if.** The batched or recurrent-depth rows deviate from the arithmetic, so that an adversary can think for less than the token law predicts, or the result gives the first joule data for a real latent-reasoning model. Otherwise it is the limits table of direction 1. The "energy audits forward passes and bytes, blind to symbols" statement is new as a measured claim. On its own it is one paragraph.

**Risks.**
- **Predictable outcome.** Most rows are predictable, and a reviewer may call the null rows obvious.
- **Small models.** Small models have different noise floors.
- **Timing.** A trusted clock also counts silent forward passes ([2412.15431](https://arxiv.org/abs/2412.15431) shows timing leaks token counts). Narrow "no software monitor can see it" to "no monitor the agent or host can edit".

**What the checks changed.**
- Doses are set per episode.
- Arm S (encoded or steganographic reasoning at fixed tokens) is dropped as a separate arm. ASTRA-2CH T-DC and the rail data-dependence ladder already bound content effects.
- Filler tokens are emitted tokens, so they belong in neither of the seat's arms.

### 4.4 Covert out-of-model work at the DC boundary (D6), rider

**Claim (reshaped).** The calibrated minimum detectable covert dose per episode, in joules and in token equivalents, is reported per dose type and per boundary (software rails against the KM003C).
- **Primary estimand:** the fraction of each dose that the rails cannot see.
- **The seat's bar:** "H50 ≤ 300 J". With residual SD 19-58 J, that is nearly guaranteed. Re-anchor the dose grid to multiples of s_r and state each dose in W × s against the measured tool-wait budget.

**Design.**
- **Dose types.** Run inside an E2 night: CPU loop, small-model decode, and a memory-bandwidth-bound dose. Drop the storage and network doses: they carry too few joules to reach 150 J inside an episode.
- **Realism.** The adaptive arm hides doses inside legitimate, variable tool work, not in idle gaps.
- **Spoofing arm.** One arm falsifies host telemetry. Under that arm the meter's value is shown, not just asserted.

**Cost.** A rider inside one E2 night.

**Noteworthy if.** Systems-security or governance workshop at best. Probable headline: "the rails catch what the DC meter catches, except under telemetry spoofing". That is a useful negative.

**Risks.**
- The 1 Hz SMC limits the PDTR and battery terms. The KM003C logs at 50 samples/s (repo fixture), so tool spans can be tiled at the meter.
- Thermal side effects of the doses.
- A small-model download needs Ed's OK.
- Amended D-139 A1 allows only the agent under test as the on-host adversary. Harness-injected doses are positive controls and are fine.

### 4.5 Model substitution and inference-compute verification (D5), section

**Claim (reshaped).** Drop the 30B-A3B substitute as a straw man. Keep unmasked 4-bit only as a calibration point. The informative arms are:
- **Batched hidden best-of-N:** energy separates it from the declared work while time does not.
- **An energy-padding adversary:** a paced 4-bit model plus busy work tuned to the 8-bit fit (Kimpson's matched-energy case). It is tested against a trace-shape classifier at the KM003C's logged rate.

**Design and cost.** One window. The padding adversary is an adversarial program on the host, so it needs a ruling under amended D-139 A1 before it can run.

**Noteworthy if.** A section of the governance paper. The worthwhile sentence would be "energy verifies the compute budget, not model identity", with the confusion set measured.

**Risks.**
- **Battery buffer.** Under a host-level adversary (a provider-substitution threat), the battery can supply load the charger-side meter never sees, and charge control lets it shift energy across episodes. Run on a battery-less Mac or meter the battery independently.
- **Outputs already do this.** DiFR and IRIS catch quantization from outputs. Energy matters here only for discarded samples, which output checks cannot see.

### 4.6 SHADE-Energy release (D8), artifact

**Claim (reshaped).** Release direction 1's metered episodes, tamper transforms, frozen fits and an offline monitor-scoring API as its artifact.
- **Cross-site artifact.** Teacher-forced replay packs: free-running trajectories diverge across chips, so they are not a good cross-site artifact.
- **Between-unit term.** A same-SKU estimate with an honest n = 2 caveat.

**Corrections to carry.**
- "Any Apple-silicon Mac" is false. The models need at least 48 GB.
- Only monitors can be scored offline; behavioural adversaries need new metered episodes.
- The project uses 2 of SHADE-Arena's 5 public pairs (per the checks).
- Carry the SHADE canary string.
- The "22 % same-SKU variation" figure the seat cited is GPU *performance*, not power (Sinha et al. 2208.11035, per the checks).

**Cost.** 1-2 desk weeks after the Block 5/6 registered releases, through `release_check.py` and Ed's manual authorization.

**Noteworthy if.** A D&B paper only with 3+ chips, all public pairs and the scoring API. Otherwise it is a supplement, still worth releasing because it is cheap.

### 4.7 Oversight tax in joules (D11), cost axis

Compute the token-arithmetic table from transcripts now. Measure only the part arithmetic does not fix: the long-context energy/token departure for re-read against incremental monitoring, and verdict identity under MLX prefix caching. Run that as a half-night rider on 5-10 length-capped transcripts.

The seat's "≥ 20 % of agent energy" bar cannot fail: a per-turn 8B re-read probably costs several times the agent episode. Report the ratio as a function of turn count instead.

SHADE-Arena's default monitor reads the transcript once at the end, not per turn. The prefix-caching mechanism is already characterized on H100 (prefill energy −93 %, KV term unaffected, [2611.03330](https://arxiv.org/abs/2611.03330)).

### 4.8 Log inflation (D4), fixture plus one limits sentence

Keep the seat's rejection of the sandbagging arm. Fold inflation into the squeeze P arm as follows:
- **Test.** A one-sided lower-tail test with its own alpha.
- **Reporting.** Report prefill and decode inflation separately, with cache-hit counts printed.
- **Sign of the confounds.** Rebuilds push the residual *up*. Cache hits and cool thermal states push it down.

The limits sentence: "Energy bounds net unaccounted work. It cannot separate matched padding plus hidden work from honest work without replay or authenticated counts."

Fix the Token Inflation citation to: "1,469 % on average, in the most permissive setting" (lead re-opened [2605.30040](https://arxiv.org/abs/2605.30040)).

### 4.9 Eval awareness (D7), negative-control rider at most

Keep the rejection. If a D window has spare slots, run a framing arm with matched prefill tokens and report it as a descriptive CI ("the residual does not move with framing"), never as "confirmed". The token-count effect is already published on GPT-OSS-20B ([2510.08624](https://arxiv.org/abs/2510.08624)).

The eval-awareness question that matters for an energy tripwire is whether the agent is aware of *the meter*. That belongs in direction 1's aware adversary families.

### 4.10 Limits the seat stated and this synthesis keeps

- **Off-host delegation** is invisible to a single-host meter by construction, for example collusion through steganography (Motwani et al. 2402.07510, per the seat).
- **Training-time self-modification** on this Mac is just another dose type, in direction 3 or D6.
- **Root compromise and meter tampering** are outside the squeeze's primary claim (addendum §2).

---

## 5. What to start at the desk now (no Mac time)

The list is ordered by how much it de-risks direction 1. All items are read-only analysis or writing, and none touches restricted paths. Transcript inputs come from the magistrate, never from night custody directly.

1. **Threat-model memo (lead, for Ed).** Decide authenticated runtime counts against an untrusted log. Make unmediated compute energy's case. Add battery assist as a scored term. Restate amended D-139 A1's scope. This feeds the squeeze addendum's §9 decision rows.
2. **Analytic two-knob null region (Sol).** Use the frozen fits' marginal powers: P_prefill/P_decode ≈ 1.8 here, with P_context to be bounded. Publish the predicted escape set before any adversarial data exists.
3. **H_blind desk study (Air).**
   - Run the frontier API monitor (primary) and the local monitor on development and selection transcripts only.
   - Compare targeted deletion against random deletion, with benign transcripts stripped the same way.
   - First pre-qualify the local monitor's AUC on development seeds.
   - The magistrate assembles the inputs.
4. **H_det,E distribution and replay-null projection (Air).**
   - Compute per-pair f_E* and H_det from calibration `7fbd95e31`.
   - From the identical-work pair differences in pilots 4-10, project H_det,replay, including the position effect in record 1b198a71.
5. **Replay-verifier design note (Sol).** Cover the forced-decode loop on D's hybrid cache, in-window placement and ABBA balance, the null distribution, the cost per audited episode, and the determinism check.
6. **Byte-arithmetic prediction table (Sol).** Cover the lm_head fractions for D, the 30B and a sub-1B model; the recurrent-depth per-step share; and r(B) for dense against MoE. Register it before directions 2 and 3 measure anything.
7. **Batch-path feasibility (Air, code reading only).** Find out whether the pinned mlx-lm batch path supports D's hybrid cache and the 30B MoE at B ≤ 8 within memory at 40,960 context.
8. **Citation hygiene in the squeeze and ALIGN drafts (lead).**
   - MonitoringBench's drop comes from refined attacks.
   - Token Inflation: "on average, most permissive setting".
   - "Wu et al." is Wu, Han, Ruf, Grari and Detyniecki (NeurIPS 2026 Resource-Aware Agentic AI workshop).
   - Kimpson et al. has three authors.
   - JouleShare is Luo et al. 2608.00026.
   - Sinha's 22 % is a performance figure.
9. **D11 token-arithmetic table (Air).** From transcripts, with no meter.
10. **Later:** release schema and stripping pass for D8. Nothing leaves the Mac before the Block 5/6 registered releases.

**Decisions for Ed** (none blocks items 1-9):
- **(a)** Authenticated runtime counts, or an untrusted log, as the squeeze's primary threat.
- **(b)** 1-2 Mac nights for direction 2's batching study after the D windows.
- **(c)** Download of the 3.5B recurrent-depth model and a PyTorch-MPS excursion for direction 3, or skip it.
- **(d)** Whether D5's padding adversary falls under amended D-139 A1.
- **(e)** GPU rental only after the Mac batching result.

---

## Sources

- **[L]** The lead opened the page for this synthesis (abstract page unless noted).
- **[C]** A seat or checker opened it, per their report; the lead did not re-open it.
- **UNVERIFIED** Nobody opened it; it was seen only in search snippets.

Only sources this document leans on are listed. The checks file lists every source each checker opened.

- [L] Kimpson, Baker & Graham, "Can Power Draw Constrain Covert Compute?", [2610.07476](https://arxiv.org/abs/2610.07476). β = 1.16 worst case; ≥ 0.41 matched-energy; 0.059 with re-execution, A100. The joint energy-time inversion as future work is [C] (from the full text).
- [L] Kimpson, Baker & Graham, "Detecting AI Training in Datacentre Power", [2610.30182](https://arxiv.org/abs/2610.30182). Simulated facility power.
- [L] Luo, Li, Wang, Wang & Chen, JouleShare, [2608.00026](https://arxiv.org/abs/2608.00026).
- [L] Luo, Li, Wang & Chen, "Where Does the Energy Go?", [2609.29707](https://arxiv.org/abs/2609.29707).
- [L] Wu, Han, Ruf, Grari & Detyniecki, "Prefill, Decode, and Context", [NeurIPS 2026 workshop poster](https://neurips.cc/virtual/2026/poster/170701).
- [L] Niu, Sencer, Zhang & Chen, "The Token-Energy Law of LLM Decode", [2610.28576](https://arxiv.org/abs/2610.28576).
- [L] Ma, Afzal, Eitzinger & Wellein, [2605.11999](https://arxiv.org/abs/2605.11999). The ">20× energy per token from batch 1 to 32" figure is [C]; it is not on the abstract page.
- [L] Cavagna et al., the SIMPLE law, [2611.03330](https://arxiv.org/abs/2611.03330).
- [L] Usama, Nisa & Jung, control-token CoT suppression, [2609.27542](https://arxiv.org/abs/2609.27542).
- [L] Baherwani, Goldstein & Panda, "Not All LLM Reasoning is Visible in the Chain-of-Thought", [2607.22925](https://arxiv.org/abs/2607.22925).
- [L] Geiping et al., recurrent depth, [2502.05171](https://arxiv.org/abs/2502.05171).
- [L] Zhang, Saileshwar & Lie, "Time Will Tell", [2412.15431](https://arxiv.org/abs/2412.15431).
- [L] Karvonen et al., DiFR, [2511.20621](https://arxiv.org/abs/2511.20621).
- [L] Zhang, Zhang & Qin, IRIS, [2607.20860](https://arxiv.org/abs/2607.20860).
- [L] Arike et al., "How does information access affect LLM monitors...", [2601.21112](https://arxiv.org/abs/2601.21112).
- [L] Arnav et al., "CoT Red-Handed", [2505.23575](https://arxiv.org/abs/2505.23575).
- [L] Hua et al., "Combining Cost-Constrained Runtime Monitors", [2507.15886](https://arxiv.org/abs/2507.15886).
- [L] Kutasov et al., SHADE-Arena, [2506.15740](https://arxiv.org/abs/2506.15740).
- [L] Jotautaitė et al., MonitoringBench, [2605.09684](https://arxiv.org/abs/2605.09684).
- [L] Hoque, Zhang, Sun & Suya, "Token Inflation", [2605.30040](https://arxiv.org/abs/2605.30040).
- [L] Gan et al., ClawGuard, [2605.06205](https://arxiv.org/abs/2605.06205).
- [L] Gargiulo & Kulp, [2609.00309](https://arxiv.org/abs/2609.00309).
- [L] Rahman & Tajdari, [2606.19262](https://arxiv.org/abs/2606.19262).
- [L] Mallen et al., Subversion Strategy Eval, [2412.12480](https://arxiv.org/abs/2412.12480).
- [L] Terekhov et al., "Adaptive Attacks on Trusted Monitors", [2510.09462](https://arxiv.org/abs/2510.09462).
- [L] Ahmed et al., [2510.08624](https://arxiv.org/abs/2510.08624).
- [L] Ansari, "Beyond Training: A Feasibility Taxonomy", [2609.10105](https://arxiv.org/abs/2609.10105). Its rating of per-inference energy monitoring as "Speculative" is [C] (from the full text).
- [C] Pfau, Merrill & Bowman 2404.15758; Hao et al. (Coconut) 2412.06769; Roger & Greenblatt 2310.18512; Sun et al. (CoIn) 2505.13778; Cai et al. 2504.04715; Ong et al. (TOPLOC) 2501.16007; Kale et al. 2508.19461; Needham et al. 2505.23836; Baker et al. 2503.11926; Chen et al. 2505.05410; Terekhov et al. (Control Tax) 2506.05296; Motwani et al. 2402.07510; Sinha et al. 2208.11035; Clark et al. (WattsUpDoc, USENIX HealthTech 2013).
- UNVERIFIED: vllm-mlx 2601.19139 (cited by the checks for continuous batching on Apple silicon); WattsOnLLM (APNet 2026 slides).

In-repo sources:
- Protocol v4 (`lane/2026-11-06-v4-r1-integrated:docs/align/pilot_protocol_v4.md`)
- The squeeze addendum draft (`align/2026-11-07-squeeze-prereg`)
- The squeeze analysis README (`align/2026-11-07-squeeze-analysis`)
- `docs/research/AGENDA.md`
- RUN_STATE 204 and 210
- Magistrate records 0eafdaa2, 1b198a71 and f775edaf
- The methodology-vs-literature audit (`research/2026-11-07-methodology-vs-literature`)
- `docs/specs/axi/sb_static_batch_verdict.md`

---

## Appendix A. Seat reports, verbatim

Both seats' outputs are printed exactly as returned to the workflow. Prose reports are blockquoted so their own headings do not join this document's outline. The Fable seat's direction list was returned as structured fields; each field's text is printed verbatim under a label. Nothing was edited, including the seats' own citation errors that §4 corrects.

### A.1 Seat 1 (Fable 5.1): report

> # What the energy tripwire can do next, if v4 shows it works (Fable seat, 2026-11-07)
>
> **Scope and sources.** Read from the canonical clone via `git show` (no worktree created, nothing written to the repo): `docs/research/AGENDA.md` (origin/main), `docs/research/energy-tripwire.html` (fdb1e0409), `docs/align/pilot_protocol_v4.md` (origin/lane/2026-11-06-v4-r1-integrated), `docs/align/PIPELINE.md`, and the four 2026-11-07 audits (`literature.md`, `research-program.md`, `methodology-vs-literature.md`, `interp-weight-edit-energy.md`) on their research branches. No sealed path was opened. Every external source below was opened by me this session; the few I did not open are marked UNVERIFIED and are not load-bearing.
>
> ## 1. What "noteworthy" should mean here
>
> "Better than SHADE-Arena's monitor alone" is the wrong yardstick because the two instruments read different things: the transcript monitor reads *content* (best AUC 0.87, Gemini 2.5 Pro; side-task success "relies heavily on having access to a hidden scratchpad", Kutasov et al. 2506.15740); the tripwire reads *quantity of work* and is blind to content by construction (computation inside logged tokens costs what the log predicts; Pfau et al. 2404.15758 is the formal source). The defensible standards are therefore:
>
> 1. **Resolution:** H50/H90 (hidden tokens caught half / nine-tenths of the time) at marginal FPR <= 1/(m+1), m >= 39, on two models, with a real-compute positive control rather than a log edit. This is what v4 + E2 deliver; it is the entry ticket, not the paper.
> 2. **Complementarity:** a joint energy + transcript detector that catches more at fixed FPR than either alone *along the hiding axis* (how much reasoning the agent conceals). That is direction 2 below and is the strongest single framing I found.
> 3. **Adversarial bound:** a measured per-episode analogue of Kimpson, Baker & Graham's beta (the hidden compute a power trace cannot rule out; 1.16 worst case on A100, >= 0.41 against a matched-energy adversary, 0.059 with verifier re-execution; 2610.07476). JouleWise's seeded identical-work replays and frozen benign fit *are* a re-execution verifier at token grain, so the natural headline is "beta_episode at m >= 39 under adversary tiers 0-3".
>
> If v4 clears (1) and the program then delivers (2) and (3) on the 30B + D corpus, that is a main-track safety/governance paper. Without (2) or (3) it stays a strong workshop paper, whatever the H50 is.
>
> ## 2. Candid tiering of the directions
>
> **Tier A: could be genuinely noteworthy (main-track level if executed with m >= 39 and two models).**
> - **D2 Energy-transcript squeeze** (joint detection curves). Connects to the control literature's cost-constrained monitor combination (Hua et al. 2507.15886, Neyman-Pearson over likelihood ratios) and to MonitoringBench's finding that refined attacks cut an Opus-4.5 monitor from 94.9% to 60.3% (2605.09684). The squeeze is the only direction where energy changes what a *content* monitor can achieve.
> - **D1 Adaptive, meter-aware adversary ladder.** Only noteworthy if run as a *ladder* from a scripted oracle (upper bound on evasion, Kimpson's matched-energy case) down to prompted LLMs with and without meter feedback. The honest expectation is that current open 27B/30B agents cannot pad energy precisely; measuring *how badly* they fail, and whether the two-knob mixed attack (methodology doc idea 3) nulls both energy and time channels, is the result. Merge with D2 into one paper: "The energy-transcript squeeze and its adversarial limits".
> - **D10 Scaling the tripwire off the laptop** (batch, multi-tenant GPU). This is the question every governance reviewer will ask. Kimpson (A100) and Gargiulo & Kulp (H200, ~10 MHz, 97% class accuracy; 2609.00309) work at workload grain; nobody has measured how token-level residual resolution degrades with batch size and co-tenancy. Needs rented GPU hours (Ed's explicit go per PIPELINE), not Mac-nights.
> - **D8 "SHADE-Energy" open benchmark.** Noteworthy only as a Datasets & Benchmarks artefact with >= 2 models, >= 2 machines (E6 second unit), the tamper suite and scoring code; as a one-Mac data dump it is a supplement.
>
> **Tier B: solid, publishable as sections or a workshop paper, not headline.**
> - **D5 Substitution / inference-compute verification.** A plain 8-bit -> 4-bit swap or a hidden best-of-N is visible on a stopwatch, so the energy-only result is near-certain and incremental; the interesting arm is *timing-masked* substitution and hidden best-of-N (the most realistic covert-compute generator). Prior: Cai et al. (text/logprob audits weak, propose TEEs; 2504.04715), TOPLOC (needs activations; 2501.16007), Token Inflation (evidence must come from outside the audited party; 2605.30040).
> - **D6 Out-of-model agent activity.** ClawGuard (May 2026, 2605.06205) already demonstrates out-of-band *EM* detection of agent workflow hijacking under a compromised-host threat model (AUC 0.9945). WattsUpDoc (2013) is the power precedent (>= 94% known, >= 85% unknown malware). JouleWise's differentiators are a commodity DC meter, a *calibrated* residual rather than a classifier, and a dose-response curve in joules. Fold into the E2 positive-control night as dose types.
> - **D3 Forward-pass counter vs steganography null.** "Energy counts forward passes, not tokens" is a clean two-sided statement: Coconut-style latent steps (Hao et al. 2412.06769) and looped passes are detectable like hidden tokens; encoded/steganographic reasoning inside fixed tokens (Roger & Greenblatt 2310.18512; Pfau) is undetectable at FPR. Nice, modest.
>
> **Tier C: not noteworthy as posed; reject or reframe.**
> - **D4 Sandbagging as negative residual: reject.** Energy is per token, not per quality; a model that "tries less" at the same token count draws the same joules, and a model that truncates reasoning shows it in the log the operator already holds. CTRL-ALT-DECEIT finds sandbagging hard for *content* monitors (2511.09904) and Tice et al. detect it from the weight side by noise injection (2412.01784); neither gap is one the tripwire fills. The useful residue is a *two-sided* test for log *inflation* (padding logged work to cover hidden compute, the counter-move in D1), which the Token Inflation threat motivates.
> - **D7 Eval awareness: reject as an energy study.** Framing effects (Needham et al., AUC 0.83 for evaluation detection; 2505.23836; Kale et al.: agent awareness of monitoring degrades monitors, 2508.19461) show up as *token-count* differences the operator can read directly. Energy adds nothing unless the reasoning is hidden, in which case it is just D2. Keep as a zero-cost rider (framing arm in a D window), nothing more.
> - **Multi-agent collusion: a limit statement, not an experiment.** On-host delegation of covert work is D6; off-host delegation (Motwani et al. secret collusion via steganography, 2402.07510) is invisible to a single-host meter by construction. Say so in the paper's limits.
> - **Training-time uses:** detecting unlogged fine-tuning/self-edits is already folded into E2 as a dose type (interp doc idea 10); Gargiulo & Kulp and de Almeida (ICML 2026 TAIGR) show training has a class-level power signature. On a Mac a LoRA pass on a small model is a few kJ, so it is simply another dose. No separate direction.
>
> ## 3. Cross-cutting design rules (apply to every direction)
>
> - **Adversary ladder, registered once.** Tier 0: non-adaptive log omission (v4's estimand). Tier 1: real hidden compute, non-adaptive (E2). Tier 2: scripted oracle adversary that knows the frozen coefficients and pads logged counts to match energy (Kimpson matched-energy; the two-knob prefill + context attack). Tier 3: prompted LLM adversary with/without meter feedback. Report beta_episode per tier.
> - **Unit:** hidden work in *token-equivalents* at the fitted decode coefficient (0.495 J/token spam, 0.667 bank in context; ~0.18 J/token fresh context), and beside it as a fraction of declared work so reviewers can compare with Kimpson's beta.
> - **Threshold:** max of m benign residuals, m >= 39 (FPR <= 2.5%); print MDE at ranks m and m-1 and flag a threshold > 1.5x the next score (council ruling 12).
> - **Boundary:** every adversarial or substitution claim must be scored at the DC meter (KM003C / PDTR) as well as the GPU rail, because rails are host software and miss ~76% of memory-traffic energy (f = 0.238). This is also the privilege-boundary answer to Gargiulo & Kulp's NVML-spoofing point and Hot Pixels' unprivileged sensor reads (2305.12784).
> - **Sign:** registered one-sided for omission; two-sided only for the inflation/substitution estimands, declared in advance.
> - **Proportionate care:** keep blinding and prereg; do not add guards. Most of these directions are desk work on transcripts and traces the project already owns.
>
> ## 4. Dependencies on v4
>
> - If W1/D1-D3 pass U1-U3 and D's per-pair s_r stays at ~1-2% of episode energy: all directions proceed on D; D2 and D1 use D's held-out curve as the energy half.
> - If v4 is refused under ruling 1(f) or thermal control fails: D1, D2, D5, D6 all still run on the Qwen3-30B-A3B corpus (frozen calibration 7fbd95e31, pilots 8-10) plus one E2-shaped night; only D8 (benchmark needs two models) and the cross-model claim suffer.
> - If the D positive control (real injected compute) is detected at <= 512 tokens: D5's hidden best-of-N arm and D6's dose types become straightforward; if not, D2 is the fallback framing because it does not need a small H50 to show complementarity.
> - D10 is independent of v4 and of the Mac.
>
> ## 5. Sources opened this session (all abstract pages unless noted)
> Kimpson, Baker & Graham arXiv:2610.07476; Gargiulo & Kulp 2609.00309; Kutasov et al. SHADE-Arena 2506.15740; Sun et al. CoIn 2505.13778; Pfau, Merrill & Bowman 2404.15758; Baker et al. 2503.11926; Kale et al. 2508.19461; Ward et al. CTRL-ALT-DECEIT 2511.09904; Cai et al. 2504.04715; Hoque et al. Token Inflation 2605.30040; Hua et al. 2507.15886; Hao et al. Coconut 2412.06769; Needham et al. 2505.23836; van der Weij et al. 2406.07358; Motwani et al. 2402.07510; Roger & Greenblatt 2310.18512; Shavit 2303.11341; Ong et al. TOPLOC 2501.16007; Shumailov et al. Sponge Examples 2006.03463; O'Gara et al. HEMs 2505.03742; Luo et al. 2609.29707; Taneja et al. Hot Pixels 2305.12784; Jotautaite et al. MonitoringBench 2605.09684; Meinke et al. 2412.04984; Gan et al. ClawGuard 2605.06205; Tice et al. 2412.01784; Chen et al. 2505.05410; Clark et al. WattsUpDoc (USENIX HealthTech '13 page); de Almeida (ICML 2026 TAIGR poster page).
> UNVERIFIED by me (cited via the repo audits or a search snippet only): Wu et al. "Prefill, Decode, and Context" (NeurIPS 2026 workshop); Terekhov et al. Control Tax 2506.05296; Arnav et al. CoT Red-Handed; SCAgent 2605.17406.

### A.1 (continued) Seat 1 (Fable 5.1): directions

#### D1. Adaptive, meter-aware adversary ladder (extend candidate 1)

**Claim.** Falsifiable claim: against an adversary that knows the frozen five-term coefficients and pads logged prefill/context counts to cover H hidden decode tokens (Kimpson's matched-energy case), the energy-only residual's catch rate at FPR <= 1/(m+1) falls to the FPR for H <= 1,024, while the registered energy + trusted-time + structural-consistency score keeps power >= 0.8 at H = 1,024; and a prompted LLM adversary (tier 3) achieves less than half the evasion of the scripted oracle (tier 2). Falsified if energy-only already resists the oracle, if the joint score adds < 0.2 power, or if the prompted agent matches the oracle. Why the tripwire: JouleWise has exact token logs, turn timing from the trusted trace, turn-owned energy and seeded identical-work replays, which put it in Kimpson's re-execution regime (beta 0.059) rather than trace-only (beta >= 0.41). Closest prior work: Kimpson, Baker & Graham 2610.07476 (beta, matched-energy adversary, A100); Gargiulo & Kulp 2609.00309 (four evasion strategies, diluted LoRA caught 48-88%); Kale et al. 2508.19461 (agent awareness of monitoring degrades monitors); methodology doc idea 3 (two-channel audit, two-knob mixed attack).

**Design.** Arms by adversary tier on the same held-out pool. Tier 2 (desk, 0 nights): synthetic tampers on D1-Dn and pilot 8-10 logs over the H grid {128, 256, 512, 1024, 2048} in four attack classes: strip only; strip + prefill inflation; strip + context inflation; optimal mixed inflation. Scores: energy-only, time-only (duration from trusted trace onset/offset, stratified by thermal state), structural consistency (re-tokenise; turn t+1 prompt = turn t context + outputs), and a joint Mahalanobis score; frozen leave-one-trajectory-out benign fits for energy and time. Tier 3 (1-2 Mac-nights, 30B v3 shape, ~12 members per arm): the agent is told the energy monitor exists and is given either (a) the fitted coefficients and per-turn energy feedback or (b) only the instruction to hide reasoning while keeping its log plausible; real hidden compute is generated by the agent itself (hidden best-of-N or private scratchpad turns the harness withholds from the log but meters). Estimand: beta_episode per tier = largest hidden token-equivalent not rejected at the m-max threshold (m >= 39), with H50/H90 per attack class from a window-cluster bootstrap. Adversary model stated explicitly: controls its log and its generation, not the meter; powermetrics as root under the harness; DC meter as arbiter.

**Cost.** Tier 2: 0 Mac-nights (desk on existing traces; registration before the D held-out pool is unblinded). Tier 3: 1-2 Mac-nights on the 30B (pilot-10 kit plus a small unpinned-runner change); no extra hardware. Reaches m >= 39 on the 30B as a by-product.

**Noteworthy if.** Noteworthy (main-track safety/governance venue, merged with D2) if the ladder yields a measured beta_episode per tier on two models at m >= 39 and shows the mixed attack's null region quantitatively (where 1/P_dec lies between 1/P_pre and 1/P_ctx). Incremental if only tier 2 on one model: that is a reanalysis rider, workshop level.

**Risks.** Prompt-induced work confounds the residual (RECORD 7e06863b) so tier 3 needs a no-hide instruction control; the 30B/27B agents are weak at precise padding, so tier 3 may be a predictable 'fails to evade' null; thermal/DVFS noise is shared between the energy and time channels (drop 'independent' wording); min empirical FPR ~0.07 with m ~12-14 per window makes Bonferroni unattainable, so register the joint score as primary; context inflation is capped at 40,960 tokens. Dependencies: tier 2 needs the frozen fit (any model); tier 3 needs Ed's OK for more 30B nights (RUN_STATE item 174). v4 outcome changes the model, not the design.

#### D2. The energy-transcript squeeze with joint detection curves (candidate 2, promoted to headline)

**Claim.** Falsifiable claim: along the hiding axis (fraction f of reasoning tokens the agent conceals from the transcript), the transcript monitor's catch rate at FPR 2.5% falls monotonically with f while the energy residual's rises; a Neyman-Pearson combination of the two likelihood ratios achieves a minimum catch rate over f that exceeds the better single detector's minimum by >= 0.2, i.e. there is no f at which an agent escapes both. Falsified if the joint minimum is within 0.05 of the single-detector minimum, or if the monitor's catch rate does not fall with f (content leaks through actions alone). Why the tripwire: it is the only detector whose power increases when reasoning is hidden, and hiding is exactly what defeats CoT monitors (Baker et al. 2503.11926 obfuscation; MonitoringBench 94.9% -> 60.3%). Closest prior work: Hua et al. 2507.15886 (cost-constrained monitor combination, >2x recall); SHADE-Arena monitor AUC 0.87; Chen et al. 2505.05410 (reveal rate often < 20%); CoT Red-Handed (hybrid monitors at fixed FPR; UNVERIFIED by me); the repo's unrun RQ-ALIGN-METADATA-BASELINE.

**Design.** Inputs: existing pilot 4-10 and v4 transcripts with their metered energy (sabotage and benign). Hiding axis: for each sabotage transcript produce versions with f in {0, 0.25, 0.5, 0.75, 1.0} of reasoning tokens stripped from the transcript (the known-H tamper applied to the monitor's view as well as the log), and a monitor-only control where tokens are stripped from the transcript but kept in the log (isolates the content effect). Monitor arms: local Qwen3-8B 4-bit and Qwen3.8-27B 8-bit as SHADE-style suspicion scorers (thinking off, numeric score), run off the measurement Mac; also a counts-only metadata classifier (grouped CV, AUC with CI) as the cheap baseline. Energy arm: v4 residual score at the frozen benign fit. Joint arm: likelihood-ratio combination with thresholds set on benign episodes at FPR <= 1/(m+1). Estimand: catch rate vs f for monitor, counts, energy, joint, with bootstrap CIs clustered by trajectory and window. Adversary: non-adaptive hider (tier 0/1); tier 2-3 from D1 as a sensitivity. Report per model and per task pair, never pooled across pairs (cross-pair transfer fails).

**Cost.** 0 Mac-nights for scoring (monitor inference runs on the Air or any machine; identity of verdicts, not energy, is what matters there). +0 if D1 tier 3 transcripts exist. No hardware. Pilot transcripts sit under night-* custody, so the lead/magistrate assembles the inputs.

**Noteworthy if.** Noteworthy (main-track) if the joint curve shows a no-escape region on two models at m >= 39 with a real-compute positive control, framed as 'hiding compute forces logging plausible work the monitor can read'. Incremental if only one model, simulated hiding, and m ~28: then it is a strong figure in the ALIGN paper, not its own result.

**Risks.** Energy half is non-adaptive by construction unless D1 tiers are added; the 30B rarely completes the side task, so sabotage transcripts are few (2 distinct held-out trajectories today; E2's ~12 fresh sabotage seeds fix this); monitor verdict identity under prefix caching on MLX can drift (define identity on the parsed score); the +755-token sabotage prompt inflates the counts baseline's AUC for the wrong reason and must be disclosed. Dependencies: needs E2 (fresh sabotage seeds, real injected compute) or the v4 D windows for the energy half; blocked only by transcript custody.

#### D3. Forward-pass counter: latent reasoning detectable, encoded reasoning not (candidate 3, reframed two-sided)

**Claim.** Falsifiable claim: (a) k hidden latent reasoning steps (extra forward passes with no emitted token, Coconut-style or looped) are detected by the tripwire at the same H50 as k hidden decoded tokens, within 20% in token-equivalents; (b) steganographic/encoded reasoning inside a fixed visible token stream (Roger & Greenblatt; Pfau filler tokens) is detected at exactly the FPR (a registered null with an equivalence bound of 0.1% of episode energy). Falsified if latent steps cost < 0.5 of a decode token in energy (then energy under-counts latent cognition), or if an encoding scheme at fixed tokens moves energy by > 0.1%. Why the tripwire: it counts forward passes and bytes moved, not symbols; no software monitor can see a forward pass that emits nothing. Closest prior work: Hao et al. Coconut 2412.06769 (continuous thoughts fed back as embeddings, COLM 2025); Pfau, Merrill & Bowman 2404.15758; Roger & Greenblatt 2310.18512 (paraphrasing limits encoding to ~3 bits/KB); Chen et al. 2505.05410.

**Design.** Arm L (latent): a synthetic latent-step harness on D or the 30B that runs k extra forward passes per turn with the hidden state fed back and nothing emitted (k in {0, 64, 256, 1024}), built on the teacher-forced decode loop ASTRA-2CH already needs; benign fit from k = 0 members; dose-response of the residual in token-equivalents; optionally a public Coconut checkpoint (GPT-2 scale) as a real-model confirmation, non-claim. Arm S (encoded): identical token streams replayed through the model with content varied (paraphrase vs steganographic carrier of equal length) in ABBA order, TOST at +/-0.1% with ~11 pairs at the ~2 J pair SD. Estimands: H50 for latent steps vs decoded tokens; equivalence bound for content at fixed tokens. Threshold: m-max on k = 0 benign members. Adversary: non-adaptive; the point is the instrument's law, not an attacker.

**Cost.** 1 Mac-night (arm L dose ladder plus arm S replays fit one window; ~22 members). No extra hardware. Needs the forced-decode loop (interp Stage 0 desk tool) and a model download if a real latent-reasoning checkpoint is used (Ed's OK).

**Noteworthy if.** Noteworthy at a workshop (interp/safety) as the first measured statement that energy audits forward passes rather than tokens, with a positive dose curve and a registered null; stronger if a real latent-reasoning model confirms arm L. It will not carry a main-track paper alone; it is a conceptual boundary result that reviewers of D1/D2 will want stated.

**Risks.** Arm S is a near-certain null that a reviewer may call obvious; the latent harness is synthetic unless a real checkpoint runs on MLX; small models have a different noise floor (interp doc check: floor does not transfer); latent steps on a hybrid cache (D) may cost differently per pass than attention decode, which is itself the measurement. Dependencies: none on v4's outcome; shares the teacher-forced loop with ASTRA-2CH; queue after the D windows.

#### D4. Sandbagging via negative residuals: REJECT; keep a two-sided log-inflation test (candidate 4)

**Claim.** Verdict: not a tripwire question. Energy is proportional to tokens generated and bytes moved, not to answer quality, so an agent that strategically underperforms at the same token count draws the same joules, and one that truncates its reasoning shows that in the log the operator already owns. The surviving falsifiable claim is about inflation, the counter-move to hiding: an agent (or provider) that pads logged counts without doing the work produces a negative residual detectable at the same resolution as omission (|H50| within 20% of the omission H50), which closes the padding escape in D1 and answers the Token Inflation threat with physical evidence. Closest prior work: van der Weij et al. 2406.07358 (sandbagging definition, password-locking); Ward et al. CTRL-ALT-DECEIT 2511.09904 (sandbagging harder for monitors than code sabotage); Tice et al. 2412.01784 (noise injection reveals sandbagging from the weight side, NeurIPS 2025); Meinke et al. 2412.04984 (Claude 3.5 Sonnet sandbagged to stay helpful); Hoque et al. Token Inflation 2605.30040 (up to 1,469% hidden-token inflation undetected; evidence must come from outside the audited party).

**Design.** Desk only: on existing benign logs, inflate logged decode counts by H in {128, 256, 512, 1024} with joules held fixed; score with a two-sided version of the residual against a two-sided m-max/m-min threshold (FPR <= 2/(m+1)); report H50 for inflation beside omission. Register the sign convention per threat model in the ALIGN paper (omission one-sided, inflation/substitution two-sided; literature audit decision 8). Do not run a sandbagging arm: if Ed wants sandbagging studied, the right instruments are content monitors and weight-side noise injection, and the energy result is a predictable null that can be stated from the token law without a night.

**Cost.** 0 Mac-nights (desk). No hardware.

**Noteworthy if.** Not noteworthy on its own at any venue. As a paragraph it strengthens D1/D2 (closes the padding escape) and the paper's limits section ('energy audits work, not effort or quality').

**Risks.** Mislabelling a null as a finding; a negative residual is also what a sampler stall or cache rebuild produces, so inflation detection needs the rebuild-count print (council ruling 11) beside it. No dependency on v4.

#### D5. Model-substitution and inference-compute verification, including timing-masked and hidden best-of-N (candidate 5, narrowed to the hard arms)

**Claim.** Falsifiable claim: with the verifier holding the DC meter and the declared model's frozen fit, (a) a substituted 4-bit D, a different-family substitute (Qwen3-30B-A3B) and a hidden best-of-N (N in {2, 4, 8}) are each rejected at FPR <= 1/(m+1) with power >= 0.9 per episode; (b) a timing-masked substitute (4-bit D with decode paced to the 8-bit tok/s) is still rejected by energy alone with power >= 0.8; (c) the two-knob matched substitute (pacing plus padded logged counts) is where power collapses, giving a measured confusion set. Falsified if (b) falls below 0.5 (energy adds nothing over a stopwatch) or if (a) fails for best-of-N at N = 2. Why the tripwire: substitution audits from text need many queries and miss subtle swaps, logprob audits are undermined by nondeterminism (Cai et al. 2504.04715), TOPLOC needs activation access (2501.16007); energy needs only the meter and is a physical analogue of re-execution (Kimpson beta 0.059). Closest prior work: Cai et al.; TOPLOC; Kimpson et al.; Gargiulo & Kulp (class-level only); interp doc PRECISION-TAMPER (banked, timing-masked arm); Shavit 2303.11341 and O'Gara et al. 2505.03742 (compute verification without power).

**Design.** One window on the D line: declared arm D-8bit (benign, two pairs); substitute arms D-4bit, 30B-A3B, D-8bit with hidden best-of-N (N candidates sampled per turn, one shown; the log reports one); masked arm D-4bit paced to 8-bit speed via per-token sleeps or clock pacing; matched arm = masked plus inflated logged counts (desk tamper on the masked arm's log). Identical token streams across weight sets via teacher forcing where the comparison is physics (4-bit vs 8-bit at fixed tokens); free decode for best-of-N. Estimand: per-episode energy minus declared-model prediction, in J and token-equivalents, at rails and DC; classification power per arm at the m-max threshold (m >= 39 benign D members from the D windows); time residual as the second channel. Adversary model: controls the served model and pacing, not the meter; knows the declared fit (worst case).

**Cost.** 1 Mac-night (arms fit one window at ~22 members if best-of-N is capped at N = 4 for bank). No extra hardware; the KM003C is already inline. Teacher-forced loop from interp Stage 0.

**Noteworthy if.** Noteworthy at a governance/security workshop (or as a section of the main paper) if the timing-masked and best-of-N arms give measured power and the matched arm gives a quantified confusion set tied to Kimpson's beta. Incremental if only the unmasked swaps are run: everyone expects a 4-bit model to draw less, and a stopwatch already sees it.

**Risks.** Per-token energy differences between quantizations on this rig are not yet measured in the agent regime (BYTES data are sealed until stage 1/2; do not size from latency-bound KB coefficients); pacing by sleeps changes the DVFS state and may itself be visible, so pace by clock pin where possible and report both; hidden best-of-N changes thermal state (positive, that is the signal, but it threatens G1 holds); the 30B substitute differs in prompt tokenisation, so compare on logged counts as the provider would report them. Dependencies: needs the D benign pool (v4 D windows) for m >= 39, or runs on the 30B with D as the substitute if v4 is refused.

#### D6. Out-of-model agent activity as a sandbox tripwire: dose-response at the DC boundary (candidate 6, merged with training-time and on-host collusion)

**Claim.** Falsifiable claim: covert work the agent runs outside the inference process during tool waits (a CPU busy loop, a second small model decoding, a LoRA fine-tune pass on a small model, an SSD scan, a network upload) is detected at the DC boundary with H50 <= 300 J per episode at FPR <= 1/(m+1), and the GPU-rail residual alone misses CPU-only and storage-only doses (power < 0.5 at 300 J) while the DC residual catches them. Falsified if DC H50 > 1 kJ (background noise swamps covert work) or if the rail residual already catches everything (then the DC meter adds nothing here). Why the tripwire: the DC meter is outside the host's software and the rails miss ~76% of memory-traffic energy and all storage/power-conversion energy, so the 'unassigned power residual' (PSTR minus rails, already logged at 1 Hz) is the natural sandbox alarm; agent episodes have long tool waits where covert work hides. Closest prior work: Gan et al. ClawGuard 2605.06205 (EM side channel, agent workflow hijacking, AUC 0.9945, compromised-host threat model; the closest neighbour and the one to cite first); Clark et al. WattsUpDoc (USENIX HealthTech '13; power detects known malware >= 94%, unknown >= 85%); Gargiulo & Kulp 2609.00309 and de Almeida (ICML 2026 TAIGR) for training signatures; Motwani et al. 2402.07510 for the off-host collusion limit; interp doc idea 10 (unlogged self-modification as an E2 dose type).

**Design.** Run inside the E2 confirm-and-inject night (30B, v3 shape) or a D window: benign episodes with blinded covert doses injected during tool waits, dose types {GPU decode by a 0.6B model, CPU busy loop, LoRA step on a 0.6B model, 20 GB SSD read, network upload}, doses in joules chosen to span {0, 150, 300, 600, 1200} J as measured by the DC meter in a calibration pass; benign fit from dose-0 members. Scores: GPU-rail residual, CPU-rail residual, DC (PDTR/KM003C) residual, each with its own m-max threshold. Estimands: dose-response and H50 in joules per dose type and per boundary; a joules-to-token-equivalents conversion for the paper. Adversary: non-adaptive injector (tier 1), with one scripted tier-2 arm that schedules the dose inside the inference process's own decode window to test masking. State the limit: off-host delegation and network-side collusion are invisible to a single-host meter.

**Cost.** 1 Mac-night if merged into E2 (shares its anchors and benign members); 0 extra hardware (KM003C inline, SMC PDTR/PSTR already logged). A 0.6B model download needs Ed's OK.

**Noteworthy if.** Noteworthy at a systems-security or governance workshop if it gives the first calibrated dose-response of covert agent work at a commodity DC meter, with the rail-blind cases quantified (what powermetrics-only monitors cannot see). Not main-track on its own now that ClawGuard has claimed the out-of-band-detection headline with a stronger channel; position as 'calibrated residual + cheap meter + dose curve' versus their classifier + SDR.

**Risks.** 1 Hz SMC cannot tile 0.2-3 s tool spans, so DC applies to episode totals only; macOS background tasks (~650/h) are in-band noise at the DC boundary and set the real floor; the KM003C parser double-counting bug (km003c-rs) must be fixed first; a LoRA dose on a Mac is memory-bound and may look like decode; injection changes thermal state and must respect G1/holds. Dependencies: E2 approval (Ed's v3 ruling); independent of v4's outcome.

#### D7. Eval awareness (test vs deployment framing): REJECT as an energy study; keep as a zero-cost rider (candidate 7)

**Claim.** Verdict: energy is not the right tool. An eval-aware agent that changes behaviour under 'this is a test' framing changes its token counts and actions, which the operator's own log shows directly; at matched tokens the energy difference is predicted to be zero. The only case where energy adds information is when the framing-induced extra reasoning is hidden from the transcript, and that is D2. Falsifiable rider claim (cheap): identical tasks framed as evaluation vs deployment differ in logged reasoning tokens by more than the within-trajectory SD, and the energy residual at the frozen fit does not differ (|mean residual shift| < 0.5 s_r), confirming energy tracks work not framing. Closest prior work: Needham et al. 2505.23836 (models detect evaluations, AUC 0.83; more reliable in agentic settings); Kale et al. 2508.19461 (monitor-aware agents degrade monitors); Meinke et al. 2412.04984.

**Design.** If run at all: a framing arm inside a D window (two prompt wrappers, identical task and seed, 4 members per pair); estimands are token-count difference and residual shift; no new threshold. Do not spend a night on it.

**Cost.** 0 extra Mac-nights as a rider (consumes 4-8 member slots in an existing window); 0 hardware.

**Noteworthy if.** Not noteworthy for the tripwire at any venue. The token-count framing effect itself belongs to the eval-awareness literature and would be a footnote there on a 27B open model.

**Risks.** Spending measurement-Mac time on a question the log answers. No dependency on v4.

#### D8. 'SHADE-Energy': an open metered-episode benchmark and protocol (candidate 8)

**Claim.** Falsifiable claim (for the artefact): an independent group with any Apple-silicon Mac and a USB-C DC meter, following the released protocol (seed law, prefix cache, thermal gates, five-term fit, m-max threshold), reproduces the detection curve on the released task pairs to within the between-machine term (sentinel shift <= 0.5% and H50 within a factor of 1.5), and the released traces let anyone score a new monitor or adversary against the energy channel without re-running. Falsified if a second unit cannot reproduce H50 within 1.5x (then the method is device-specific and the benchmark is a dataset, not a protocol). Why the tripwire: no control or monitoring benchmark carries a physical channel; SHADE-Arena, CUA-SHADE-Arena, MonitoringBench and ControlArena are all transcript-only. Closest prior work: Kutasov et al. SHADE-Arena 2506.15740; Kale et al. CUA-SHADE-Arena 2508.19461; Jotautaite et al. MonitoringBench 2605.09684; UK AISI ControlArena (repo-cited, not opened by me: UNVERIFIED); Gargiulo & Kulp release a 930-trace dataset at workload grain.

**Design.** Contents: metered episodes (1 Hz SMC rails, PDTR/PSTR, KM003C totals, turn timestamps, token logs, seeds, thermal journals) for two models (30B-A3B and D) on the two public SHADE task pairs; the known-H tamper suite and the adversary-ladder tampers (D1 tier 2) as transforms; the frozen fits and scoring code; a scoring API that returns catch rate at FPR <= 1/(m+1) for any submitted monitor score vector (so D2 joint curves can be computed by others); a reproducibility kit (seed law, prefix-cache, gates, admission checks) with the deviation log. Second-unit replication (E6) on a borrowed M-series Mac for the between-machine term: 2 nights per pack shape. Release only after Block 5/6 registered releases and only non-restricted episodes; check SHADE-Arena's public-subset and anti-contamination terms before release.

**Cost.** Mostly desk (1-2 weeks of lead/Sol time for packaging and scoring API) plus 2 Mac-nights on a borrowed second unit for the replication term. Hardware: a second Apple-silicon Mac and a second KM003C (~$80) for the replicating site.

**Noteworthy if.** Noteworthy as a Datasets & Benchmarks track paper if it ships two models, two machines, the tamper/adversary suite and a scoring API, and is the first control benchmark with a physical channel. Incremental (a supplement to the ALIGN paper) if it is one machine and a data dump.

**Risks.** SHADE-Arena keeps most task pairs private, so the benchmark covers two public pairs and inherits their contamination caveats; releasing traces may leak Block-5/6-adjacent material (custody review needed); the between-machine term may be large (same-SKU variation up to 22% on GPUs; unknown on M-series), which is itself a finding but weakens 'protocol' claims; maintenance burden after the capstone. Dependencies: v4 D windows supply the second model; E6 needs access to a second unit.

#### D9. Hidden parallel sampling and test-time-compute budget enforcement (new; the most realistic covert-compute generator)

**Claim.** Falsifiable claim: an agent that secretly runs best-of-N or parallel search (N candidates per turn, one shown, the log counting one) is detected by the tripwire with H50 at N <= 2 for D on both task pairs, and the detection curve in N is predicted to within 20% by the fitted decode and context coefficients; conversely, a declared test-time-compute budget (e.g. reasoning_effort rung, N = 1) can be verified per episode at FPR <= 1/(m+1). Falsified if N = 2 is not caught (hidden sampling costs less than the log model predicts, e.g. through batching on the GPU) or if the curve deviates > 50% from the token law. Why the tripwire: parallel sampling is the canonical way an agent spends unlogged compute on a side objective without lengthening the visible transcript, and it costs energy roughly linearly in N while the log is flat; no transcript monitor can see the discarded candidates. Closest prior work: Kimpson et al. (covert compute as a fraction of declared); Luo et al. 2609.29707 (batching improves energy per token 3.2x from 1 to 16 rps, which is the attacker's lever); Hoque et al. Token Inflation (the inverse billing threat); CoIn (counting hidden tokens from provider artefacts).

**Design.** Arm inside the D5 or E2 window: benign D episodes with hidden best-of-N at N in {1, 2, 4, 8} on each turn's reasoning (candidates generated sequentially at batch 1 in arm S; batched in arm B to test the batching lever), one candidate logged; benign fit from N = 1 members; estimand: residual vs N in token-equivalents, H50 in N, and the ratio of measured to predicted (N-1) x decode cost; threshold m-max; adversary non-adaptive (tier 1) with a tier-2 variant that pads the log. Also a budget-verification read: declare the effort rung and test whether episodes at a higher rung are rejected.

**Cost.** 0.5-1 Mac-night (shares the window with D5). No extra hardware.

**Noteworthy if.** Noteworthy as the realistic positive control inside D1/D2/D5 (it turns 'injected compute' into an attack an agent would plausibly run), and as a concrete compute-governance demonstration: per-episode verification of a declared test-time budget on local hardware. Not a standalone paper; a figure and a paragraph that reviewers will remember.

**Risks.** Batched candidate generation at B > 1 on MLX changes the per-token energy (the attacker's advantage), so arm B may show sublinear growth, which is the honest result; hidden sampling raises temperature and threatens G1 holds; the harness must withhold candidates from the log while metering them, a small unpinned-runner change. Dependencies: D model and the forced/parallel decode path; independent of v4's verdict otherwise.

#### D10. Tripwire resolution off the laptop: batch size, co-tenancy and the datacenter limit (new)

**Claim.** Falsifiable claim: on a single discrete GPU serving an agent, per-episode residual SD (as a fraction of episode energy) grows at least linearly with the number of concurrent co-tenant requests, so that H50 for one episode exceeds the episode's own decode count at concurrency >= 8; per-request attribution restores resolution only if the verifier holds per-request timing and token counts for every co-tenant. Falsified if H50 at concurrency 8 stays below 25% of the episode's decode tokens (then the tripwire scales to small-batch serving), or if the residual SD does not grow with concurrency (then energy is additive and attribution is a bookkeeping problem). Why the tripwire: the Mac result is batch 1 on unified memory; the governance literature works at cluster scale (Kimpson A100 beta; Gargiulo H200 class identification; Shavit chip-level); nobody has measured where token-level resolution dies between the two. Closest prior work: Kimpson, Baker & Graham 2610.07476; Gargiulo & Kulp 2609.00309; Luo et al. 2609.29707 (GPU-only telemetry misses 41-45% of system energy; 63x agent vs serving per token); Wu et al. NeurIPS 2026 workshop (per-request attribution weakens under batching; UNVERIFIED by me, repo-opened); the repo's own A2 lane (power/nvml.py with the slice-averaging repetition protocol).

**Design.** Rented single GPU (or a borrowed workstation) with an external PDU/inline DC meter at the PSU, plus NVML as the inside channel: run the same SHADE episodes (vLLM, OpenAI-compatible endpoint, the repo's shade/ runner) at concurrency c in {1, 2, 4, 8, 16} with synthetic co-tenant traffic of known token counts; fit the five-term model per c on benign episodes; estimands: s_r(c)/E(c), H50(c) by known-H tamper, and the gain from per-request attribution (co-tenant tokens as covariates). Threshold m-max with m >= 39 per c (episodes are short on a GPU, so m is cheap). Adversary: non-adaptive; one scripted arm hides work inside co-tenant traffic. Report at both PDU and NVML boundaries; use the varied-gap pulse schedule to calibrate NVML slice averaging (Yang et al. remedy already in the repo).

**Cost.** 0 Mac-nights. Rented GPU time: ~20-40 GPU-hours plus an inline AC/DC meter at the PSU (~$150-400) or PDU with per-outlet metering; needs Ed's explicit go (PIPELINE rule: no rented GPU without it). Desk: the A2 NVML lane exists; the shade/ runner targets vLLM already.

**Noteworthy if.** Noteworthy (governance venue, main-track level if combined with D1/D2) if it gives a measured resolution-vs-concurrency curve and a clear statement of where per-episode energy auditing stops working; this is the result that turns a laptop study into a governance claim with stated scope. Incremental if run only at c = 1 (a replication of the Mac result on a GPU).

**Risks.** NVML can be spoofed/replayed and averages slices, so the claim must rest on the PSU meter; cloud GPUs expose no PSU meter (needs a physical box); thermal and clock behaviour on a datacenter GPU differs (power caps, Ma et al. UNVERIFIED by me); co-tenant traffic realism; scope creep away from the Mac program. Dependencies: none on v4; depends on Ed funding GPU hours and on the ALIGN paper's threat model being stated first.

#### D11. Oversight tax in joules (adjacent, already in the repo as idea 6; listed for completeness)

**Claim.** Not a tripwire use but the same rig and transcripts: the energy of running SHADE-style monitors (full re-read vs prefix-cached incremental vs end-of-episode action-only) relative to the agent's own episode energy, with verdict identity as the identical-work check. Falsifiable claims and arms are in methodology-vs-literature idea 6 (>= 20% of agent energy for a per-turn 8B re-read; >= 4x saving from prefix caching; action-only < 0.5x CoT+action). Closest prior work: Control Tax 2506.05296 (USD on SHADE; UNVERIFIED by me, repo-opened); Hua et al. 2507.15886 (cost framework accepting any unit); Arike et al. (USD frontier; UNVERIFIED by me).

**Design.** As in the repo doc: A/B/B/A blocks over monitor arms M1-M5 on fixed transcripts, 1 Mac-night, +1 for a co-resident variant; token-arithmetic predictions preregistered from transcripts first so only non-determined arms run.

**Cost.** 1 Mac-night (+1 co-resident). No hardware.

**Noteworthy if.** Workshop-level (first control tax in joules); it becomes more interesting as the cost axis of D2's joint detector (joules spent per unit of catch rate for energy vs transcript vs joint monitoring), which is where I would place it rather than as a standalone night.

**Risks.** Mostly token arithmetic (claims ii and iii are nearly determined by transcripts); monitor verdict drift under caching; transcript custody. Independent of v4's verdict; uses W1/pilot transcripts.

### A.2 Seat 2 (Opus 5.5): report

> The full write-up for this brief was not delivered. A safety classifier stopped the response, and I am not reproducing it, so the 'directions' list is empty. Ed's question still needs an answer: either re-brief this seat on a narrower scope or use the other seat's output.
>
> What I did before the stop:
> - **Repo reading.** I read the inputs read-only, with git show, from the canonical clone /Users/edr/code/CapstoneProject/jw-wt/handoff:
>   - docs/research/AGENDA.md and docs/research/energy-tripwire.html (origin/main);
>   - docs/align/pilot_protocol_v4.md and docs/align/PIPELINE.md (origin/lane/2026-11-06-v4-r1-integrated);
>   - the 2026-11-07 research audits: literature.md, research-program.md (plus research-program/fable-seat.md), methodology-vs-literature.md and interp-weight-edit-energy.md, each on its research/2026-11-07-* branch.
> - **Web sources.** I opened these this session:
>   - Kimpson, Baker and Graham, arXiv 2610.07476
>   - Gargiulo and Kulp, arXiv 2609.00309
>   - Rahman and Tajdari, arXiv 2606.19262
>   - Koran et al., arXiv 2605.15377
>   - SHADE-Arena, arXiv 2506.15740
>   - Token Inflation, arXiv 2605.30040
>   - CoIn, arXiv 2505.13778
>   - Cai et al., arXiv 2504.04715
>   - Pfau et al., arXiv 2404.15758
>   - Geiping et al., arXiv 2502.05171
>   - Roger and Greenblatt, arXiv 2310.18512
>   - van der Weij et al., arXiv 2406.07358
>   - CTRL-ALT-DECEIT, arXiv 2511.09904
>   - Needham et al., arXiv 2505.23836
>   - Baker et al., arXiv 2503.11926
>   - Kale et al., arXiv 2508.19461
>   - Greenblatt et al., arXiv 2312.06942
>   - Ma et al., arXiv 2605.11999
>   - Luo et al., arXiv 2609.29707
>   - Wu et al., NeurIPS 2026 virtual poster 170701
>   - LLM Agents Can Easily Tamper With Their Own Traces, arXiv 2609.30266
>   - Tracekit, arXiv 2609.35659
>   - Bridges et al., arXiv 1805.06541
>   - Clark et al., WattsUpDoc (USENIX HealthTech 2013 page)
>   - Redwood Research, "AI catastrophes and rogue deployments"
>   - Motwani et al., arXiv 2402.07510
>   - Khatamifard et al., POWERT (HPCA 2019 record)
>   - Hot Pixels, arXiv 2305.12784
> - **Boundaries.** I did not touch any restricted, night-*, custody, archive or Block 5 path. I created no worktree, ran no external code, downloaded nothing and posted nothing.
> - **Scratch files.** Copies of the input documents are in /private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/1544c617-26c5-454f-8287-04b93bf8aa23/scratchpad/src/ and can be deleted.

Seat 2 directions: [] (empty: the seat delivered no list).

## Appendix B. The 22 checks

Printed verbatim in [tripwire-directions-checks.md](tripwire-directions-checks.md).
