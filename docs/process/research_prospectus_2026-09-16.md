# JouleWise research prospectus — the landscape, the questions worth asking, and whether the tool deserves a public life (v2)

**Date:** 2026-09-16. **Author:** Fable writer seat (v1) and Fable editor seat
(v2), read-only, at `main dc119f7d` (checkout
`/Users/edr/code/JouleWise-wt-horizon`). **Reader:** Ed, who wants to learn the
landscape before ranking work by CV value (what goes on his résumé) per
hour of his own time. A *seat* is one delegated agent session that does a
bounded piece of work; Fable (Claude) and Astra (GPT) are the two model
families whose seats wrote the inputs, and the *magistrate* is the lead
session that rules on process and science questions between Ed's own
decisions.
**Inputs, cited by path throughout:** the Apple-only plan
(`docs/process/research_plan_2026-09-16.md`, "the plan"), two horizon drafts
to reconcile (Fable: the session scratchpad’s Fable horizon draft (reconciled into `docs/process/research_plan_horizon_2026-09-16.md`), "the Fable
draft"; Astra: the session scratchpad’s Astra horizon consult (same reconciliation), "the Astra
draft"), the literature record
(`docs/process_traces/2026-09-15-interactive-b0ae8462/21-rq-literature-and-best-practices-fable.md`,
"record 21"), the Astra exploration report
(`…/22-rq-exploration-astra-report.md`), the question bank
(`docs/research_question_bank.md`, "the bank"), the coverage map
(`docs/research_question_coverage-2026-09-04.md`), `CLAIMS_STATUS.md`, the
paper draft (`docs/paper/draft-v1.md`, "the paper" or "draft §n"), and the
tool-viability report (the session scratchpad’s tool-viability report (its fetched facts are reproduced in Part IV), "the
viability seat", whose external facts were fetched on 2026-09-16). Citations
[1]–[31] are the numbered sources in record 21 §4 and the Fable draft
§Sources; [32]–[57] are the viability seat's fetched pages. Nothing else was
fetched.

**How to read this.** Part 0 is the whole argument on one page; stop there if
you only want the verdicts. Parts I–III build the landscape and rank the
questions; Part IV is the tool-release decision with the tool comparison;
Part V is the day-by-day sequence and what Ed must do with his own hands.
Every term of art is defined in plain words the first time it appears, and
every mechanism comes with the problem that forces it and a worked example
with real numbers; if a later section uses a word you do not recognise, the
definition is earlier in the document, never later.

**Two labels used throughout.** **NEEDS-WEB** marks a fact no seat verified
against a primary page; it is a prerequisite to acting, never an assumption.
**ASSUMED** marks a planning estimate (hours, dollars, byte sizes computed
from parameter counts) that is not a measurement.

**Identifiers used throughout, glossed once.** *D-nnn* is a numbered entry in
the project's decision log (`docs/decision_log.md`), a ruling that binds later
work. *A-nnn / E-nnn* is a registered work lane in `TASK_QUEUE.md` (the same
lane appears under both prefixes). *RQ-…* and *Q-n* in backticks are row
identifiers in the question bank; *C5-…* are claim identifiers in the coverage
map; *AP-n* are the bank's numbered analysis-plan rules (for example AP-1, the
rule that held-out shapes or models are named before any collection); *PC-n*
are the bank's numbered planning facts assumed for Paper C (for example PC-4,
decode power is near-flat). *Paper A* is the merged methods paper; *Paper B*
is the phase-energy capstone paper (data-complete day 3 of the plan); *Paper
C* is the mechanism paper on the bank's first tier of questions (day 10);
*Paper D* is the post-C scaling and mechanism-law paper (core day 17, full
day 23) — all from the plan §Terms and §Days to each paper. *Papers E and F*
are proposed post-plan papers sketched in Part III (E: which device class
should run which request; F: the instrument). *`_v5`* is the fifth frozen generation of the
campaign plan for the pinned Qwen3 1.7B and 8B model pair — the one whose
collection windows (defined in Part II) produce the first *claim-bearing*
numbers, meaning numbers the paper
may state as findings, as opposed to *diagnostic* numbers, which show the
instrument working but may not be quoted as results.

---

## Part 0 — One page

**What the tool is.** JouleWise measures how much energy a laptop spends
answering a language-model request, and — the part nobody else does — says
how much of that energy it can honestly assign to each of the request's two
stages. A request has a *prefill* stage (the model reads the prompt) and a
*decode* stage (it emits output tokens one at a time); the paper calls a
stage a *phase*. Energy is power accumulated over time, so the energy charged
to each phase depends on where the phase boundary falls on the power trace.
Apple's `powermetrics` reports the processor's average power every 100 ms;
the model runtime records when each phase started and stopped on a different
clock. JouleWise places both on one timeline by firing 59 one-second GPU
pulses of known timing before and after every measurement session and
fitting where the power trace *saw* them; the fit's residual is the timing
uncertainty of every phase boundary in that session (draft §2). From that it
computes, for every group of like-for-like runs (a *cell*: one model, one
prompt shape, one phase, one machine state), a *resolution bound* — "the
largest false difference this measurement system can manufacture when
nothing has changed" — and it refuses to state a direction between two
conditions unless two gates pass (draft §4): the *magnitude gate* (the
observed difference exceeds the bound) and the *direction gate* (the
difference's own uncertainty interval lies entirely on one side of zero,
tightened by Holm's step-down correction when several contrasts are tested
at once, so that the chance of a false direction anywhere in the family stays
at the stated level). Everything is *pre-registered*: the plan, the models,
the prompts and the decision rule are frozen and fingerprinted with SHA-256
hashes before any data exists, and every refusal is a printed result with a
reason (draft §5).

**What it can and cannot resolve today.** The timing uncertainty is a few
tens of milliseconds (one retained *capture* — one recorded calibration, the pulse train and the
power trace that saw it — gave 30.07 ms, draft §2). Where the
boundary sits on a steep power step — prefill runs the GPU hard, decode runs
it lighter — the misplaced time times the power step is about a joule:
30 ms × 35 W ≈ 1 J. That is the **≈1 J attribution scale**, and no amount of
repetition removes it, because it is applied to every run the same way.
Run-to-run scatter, by contrast, is small: three diagnostic-era cells had
point scatter floors of 0.29, 0.49 and 0.31 J against timing-widened floors
of 3.15, 2.92 and 2.18 J (draft §3; the artifact's name for the resolution
bound is the *detection floor*, and "floor" below always means that). The
**≈5 J effective bar** is the labelled floor plus the *claim-side bound* — the
extra margin a difference must show because the difference itself is
measured with scatter and must clear the floor by its own uncertainty, not
merely touch it (`CLAIMS_STATUS.md` §1, D-078 clause 11 — D-078 is the
2026-07-19 soundness ruling that voided every pre-repair corpus and fixed this
framing). Over a 512-token decode that is 5 J ÷ 512 ≈ 10 mJ per token; over
2048 tokens ≈ 2.4 mJ. Anything smaller prints `not resolvable` — which means
*this instrument cannot see it*, never *these are equal*. Nothing is
claim-bearing on disk today: every number in `CLAIMS_STATUS.md` is
diagnostic, and the first claim-bearing cells come from the `_v5` windows on
day 3 of the plan.

**The three highest-value questions on Mac + meter** (value defined in
Part II): (1) the **bytes law** — is decode energy per token one linear
function of bytes read per token across model sizes and quantizations
(weights stored in fewer bits), with a *held-out* model (one whose energy is
predicted before it is measured)? It answers Ed's "why does each method cost
more" directly. (2) **Same-query variance as a first-class result** — how much
does the same request's energy vary on repeat, what drives the spread
(thermal state, position in the window, sampling length), and how does it
compare with the timing bound? Nobody publishes this for Apple silicon. (3)
The **meter mapping** — one number with an uncertainty interval that ties
`powermetrics`' units to a physical instrument on the laptop's power cable,
the field's first question and 15 minutes of Ed.

**Tool-release verdict, three sentences (Part IV has the rule in full).**
Ship *Release 0* now, as Paper B's artifact: the existing Apple path packaged
as a pip `joulewise` with `calibrate` and `measure` returning phase energies,
the floor and the refusal, plus a Zenodo DOI (a permanent identifier minted
by the Zenodo archive) and a citation file — two to
three weeks of mostly agent work and half an hour of Ed, earning the ACM
*Available* + *Functional* badges (code obtainable from a permanent
identifier, and documented, complete and exercisable) that a metrology
reviewer looks for. Start *Release 1* — the formal rewrite into a library
other labs can use (portable backends, one-call API, replication-bar docs,
7–16 seat-weeks depending on scope; a *backend* is the code that talks to
one power counter) — only after Paper D's core is data-complete (day 17),
only once the meter mapping has an interval, and only on a flip signal (an
NVIDIA pulse pilot yields a finite timing bound through the same code path,
or IOReport — Apple's no-root energy-counter interface, the one Zeus reads —
turns out to carry the same edge error, or an outside group asks); ship it only when a floor has actually been
re-derived on an NVIDIA card with at least one resolvable contrast and one
printed refusal. Stop at Release 0 if the `_v5` attribution-dominance test (the paper's
headline test of whether boundary attribution, not repeat scatter, dominates
each phase's floor) returns a *null* — finds no dominance — in both phases
*and* IOReport shows edge error well under the floor, or if six months after Release 0 there is zero external signal — until
one of those fires, the rewrite is a bet, not an investment.

---

## Part I — The landscape

### Who measures LLM inference energy, and how (record 21 §1)

The field splits into four groups, and each has a hole a metrologist sees
first. Instrument names used in the table: `powermetrics` is Apple's
software power counter; NVML is NVIDIA's management library, the software
counter for its GPUs; DCGM is NVIDIA's datacenter monitoring daemon over the
same sensors; RAPL is Intel's on-chip energy counter; Zeus and CodeCarbon are
libraries that read those counters; an external analyzer is a physical meter
on the mains cable; *cadence* is how often readings arrive; a *CI* is a
confidence interval on repeated runs. A *counter update period* is how often the hardware
counter actually refreshes its value, which may be slower than how often
software reads it; a *stale read* is a sample that repeats the previous value
because the counter has not updated; *load-dependent gain* is the ratio of a
physical meter's reading to the software counter's, which Jay et al. [5]
found changes with load.

| group | representative work | instrument and cadence | what they do, and what they do not |
|---|---|---|---|
| Benchmark suites | MLPerf Power [1]; ML.ENERGY [3]; HF (Hugging Face) AI Energy Score | external analyzer at 1 s (MLPerf); NVML via Zeus (ML.ENERGY); CodeCarbon (HF) | report totals and per-token means; ML.ENERGY: **no repetitions, no intervals**; HF: 10-run mean, no uncertainty |
| Phase-level studies | Splitwise [14], POLCA [15], Illusion of Power Capping [11], Ruf & Detyniecki [12], TokenPowerBench [13] | NVML/DCGM 50–100 ms; POLCA reads the boundary *visually* from a trace | report prefill vs decode power/energy; **nobody quantifies energy moved by boundary-placement error**; the two strongest ([11],[12]) avoid the boundary by running phases as separate operations |
| Apple-silicon studies | Silicon Showdown [17], AgentStop [18], GreenBench [19], Wilkins [e-Energy 2024], Intelligence-per-Watt | `powermetrics` at 2 s ([19]) to 50 ms; mean of 3 ([17]); 95% CI only in [18] | compare models on Macs; **no study states time anchoring between `powermetrics` and the workload, thermal control, or a resolution bound**; [19] reports 0.47 W package beside an 8–12 W system estimate |
| Counter-mechanics work | Hähnel [8], Khan [7], Jay [5], Cao [6], Dauner [9], Yang [10] | RAPL/NVML vs wall meters | characterise update periods, stale reads, load-dependent gain; Apple's counter is uncharacterized; Jay's 1.17–1.18 slope and Cao's 20% gap are NVIDIA/RAPL numbers |

### What nobody does, and where JouleWise sits

Four practices are absent from every row above and present in JouleWise
(draft §2–§5; record 21 §2):

1. **Boundary-placement error as a measured quantity.** A timing bound from
   in-session pulses, converted to joules per cell.
2. **A resolution bound per cell, with a refusal below it.** The literature's
   only uncertainty reports are confidence intervals on repeats, which
   cannot see a systematic boundary error.
3. **Pre-registration with frozen, hashed packs.** A *pack* is the set of
   files that define a campaign — models, prompts, shapes, run counts,
   decision rule — whose SHA-256 fingerprints are recorded before data
   exists, so nothing in it can change afterwards without detection. Unique
   in energy work (record 21 §2, last rows; the nearest analogue is Zhuang's
   paired minimum-detectable-effect design for accuracy benchmarks [20]).
4. **Custody**: the chain of fingerprints that proves which bytes produced
   which number — every input fingerprinted, every failed attempt retained,
   the verdict bound to the declared member set (a *member* is one run; the
   member set is the list of runs the verdict was declared over) so no
   favourable subset can be picked later (draft §5).

And one practice is absent from JouleWise and present in the standards:
**no external meter** (record 21 §2 row 1, scored *Not done*). SPEC [2] and
MLPerf [1] require an analyzer with ≤1% uncertainty, calibrated yearly,
*ranged* before the counted runs (a *ranging run* exercises the workload once
so the meter's measurement range can be fixed before any counted run; a range
change mid-run would change the meter's resolution). Every joule in Papers
B–D is in Apple's units until the meter leg (Part II §5) runs.

### What a JouleSort-lineage reviewer asks first

In this order, from record 21 §3 "reviewer questions we cannot yet answer":
(1) how far is `powermetrics` from a physical meter under *this* load
(gain)? (2) what is the counter's own update period — do your 100 ms
averages *alias* a slower internal counter, that is, read the same stale
value several times and mistake it for several independent samples
(Dauner's NVML finding [9] applied to Apple)? (3) why not isolate prefill
with generation length 1 and avoid the boundary altogether ([12],[11])? (4)
what does the sampler itself cost (NAACL 2025: trackers inflate time
15–50%)? (5) does the pulse-derived timing bound transfer to real inference
load (the paper's stated Limitation 1, draft §7: the bound is characterised
under commanded GPU pulses and transported to sustained mixed inference
load, and nothing in the frozen campaign tests that transport)? Questions 3
and 5 are already in the plan (Phase 0 — the plan's days 1–3 — windows
0.5–0.6 and Future Work #1); 1, 2 and 4 are the meter leg and the two
diagnostic windows in Part II.

---

## Part II — Mac hardware + wall meter only

### How value is scored here

Four factors, each 1–3, multiplied; the product is what the ranking sorts on.

- **Novelty** vs the literature above: 3 = no published measurement of the
  mechanism at all; 2 = published on GPUs but not with a resolution bound
  or not on Apple; 1 = published and JouleWise would add a citation-shaped
  replication.
- **Claim strength the instrument supports**, using the bank's ceiling
  ladder (`research_question_bank.md` §"Capability map"), four rungs: **L1**
  an association; **L2** a measured difference within the named boundary
  that clears the floor; **L3** a prediction validated on held-out cells
  frozen before collection (the AP-1 rule); **L4** replicated on another
  unit. 3 = L3 reachable; 2 = L2; 1 = L1 or a printed negative. (The
  ladder's "L1" is unrelated to the paper's "Limitation 1" above or to the
  paper's "L1 floor-binding limitation" — its §9 label for the fact that a
  third party cannot yet re-derive the link from a floor artifact to the
  claim that consumed it, met again in Part III; the three share a label,
  not a meaning.)
- **Why-content**: 3 = the answer names a physical mechanism (bytes moved,
  time at flat power, a counter's update period); 2 = it decomposes an
  effect; 1 = it ranks.
- **CV per Ed-hour**: 3 = zero Ed-hours (seats run it unattended) and it
  lands in a paper section; 2 = under an hour of Ed; 1 = Ed at a machine
  for hours or an unbuilt prerequisite.

Windows are the plan's unit: a *window* is one uninterrupted quiet-machine
collection session, ≈2.5 h wall, ≈2.25 h of capture, 4–5 per day; a
*refusal* — the unattended chain declining to capture because an
*admission gate* (a machine-state check a window must pass before capture:
load, the *census* that nothing else is running, clock) failed — costs
≈20 min (plan §Assumptions). A *rider* is an extra measurement taken inside
a window already scheduled for something else, so it costs no window of its
own. A *floor window*
repeats one condition to measure its scatter and *mint* its floor — compute
the cell's resolution bound and freeze it as a signed artifact that later
contrasts consume; a *contrast window* compares two conditions. *Desk* work
is analysis or writing that needs no window; a *desk arm* is a sub-experiment
done at the desk (an *arm* is any sub-experiment inside a window or a lane).

### The ranking

Terms in the table, glossed once: *quantization* stores each weight in fewer
bits; *sparse* or *MoE* (mixture-of-experts) models keep every expert's
weights resident but read only a routed subset per token; *held-out* means
predicted before measured; *p\*/d* is the prompt length at which prefill and
decode cost the same, in units of the decode length; *roofline* is the model
in which a computation is limited either by the chip's arithmetic rate or by
its memory bandwidth, whichever it reaches first. The *KV cache* is the per-token
key and value vectors the model stores for everything already in the
context, so *KV growth* is how decode energy rises as that store grows. A
*mixer* is the layer type that mixes information across tokens (standard
attention or one of its variants), so a *mixer signature* is the energy
fingerprint of that choice. *Prefill chunk* is the size of the pieces a long
prompt is processed in. "Fable draft Leg 2": the Fable draft is organised
in *Legs* — Leg 1 the meter, Leg 2 the Apple diagnostics and desk items,
Leg 3 the NVIDIA and cloud work — and that naming is kept here. The
*coefficient law*
(`RQ-NEXT-COEFF-LAW`, bank line ≈1748) is the companion of the bytes law: a
request's energy is modelled as E = fixed + a·p + b·d (p prompt tokens, d
decode tokens; the *coefficients* are fixed, a and b), and the law asks
whether those three coefficients follow one rule in (active bytes, KV bytes
per token, resident bytes) across models, predicting a held-out model's
held-out shape within the bar.

| rank | question (bank id) | Ed's axis | novelty | claim | why | CV/Ed-h | product | windows | paper |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Bytes-touched law + coefficient law (`RQ-NEXT-BYTES-LAW`, `RQ-NEXT-COEFF-LAW`; lifts `C5-1.1`) | same size × quant, "why" | 2 | 3 | 3 | 3 | 54 | 5 (+ floors inside) | D |
| 2 | Same-query variance as a result (`RQ-ENERGY-VARIANCE` + identical-condition null + `RQ-ORDER-POSITION` + `C5-1.5`) | variance | 3 | 2 | 2 | 3 | 36 | 2 (+ rides every floor window) | C (variance) |
| 3 | Meter mapping (`WALL-METER-GAIN-01`, lane A214; `Q6` reframed) | instrument | 3 | 2 | 2 | 2 | 24 | 4 + 1 reserve | B (instrument) |
| 4 | Quantization decomposition at one size (`C5-1.12`): watts vs time | same size × quant | 1 | 2 | 3 | 3 | 18 | 1 | C |
| 5 | Energy per correct answer vs MATH level (`RQ-NEXT-EPCA-LEVELS`, protocol from `RQ-D-A10`) | fixed-difficulty benchmark | 2 | 2 | 2 | 2 | 16 | 5 | D (applied) |
| 6 | Phase crossover p\*/d as a roofline constant (`RQ-NEXT-PHASE-CROSSOVER`, `RQ-NEXT-PREFILL-CHUNK`) | workload profile | 2 | 3 | 3 | 3 | 54† | 5 | D |
| 7 | Shape grid E = fixed + a·p + b·d with held-out shapes (`Q4`/`RQ-SHAPE-ENERGY`) | workload profile | 1 | 3 | 2 | 3 | 18 | 8 | C (coefficients) |
| 8 | Token-shape sufficiency: does content matter at fixed shape? (`RQ-CONTENT-SENTINEL`, `C5-W.1`) | workload profile | 2 | 2 | 1 | 3 | 12 | 2 | C (workloads) |
| 9 | Category ranking stability across models (`C5-W.3`/`Q5`) | workload profile | 1 | 2 | 1 | 3 | 6 | 3 | C |
| 10 | Counter update period + sampler overhead (record 21 §2 rows 3, 9; Fable draft Leg 2) | instrument | 3 | 1 | 3 | 3 | 27 | 2 | B, F |
| 11 | KV growth with context (`RQ-KV-GROWTH`, `C5-1.2`) | why | 2 | 2 | 3 | 3 | 36 | 3 | C (context) |
| 12 | Mixer signature at ≈3B active (`RQ-NEXT-MIXER-3B`) | why | 3 | 2 | 3 | 1 (NEEDS-WEB runtimes) | 18 | 5 | D (mechanism) |

† Rank 6 ties rank 1 on the product; it sits below because it consumes
rank 1's coefficients (the crossover prediction is derived from the fitted
prefill and decode slopes), so it cannot be first. Ranks 10–12 are placed by
product but listed after Ed's four axes are covered. The plan already runs
7, 8, 9 and 11 in Paper C's window order (plan Phase 1, days 4–10) and 1, 5, 6, 12 in
Paper D's (Phase 2, days 11–17, and Phase 2b, days 18–23); this ranking does not move them, it says which to protect if
windows are lost.

### Ed's axes, one at a time

#### Axis 1 — a benchmark of fixed difficulty, repeated (rank 5)

*Plain words.* Take problems from the MATH benchmark (a dataset of
competition problems) whose difficulty level (1–5) the dataset authors
assigned, hold the prompt and output budget fixed, let the model stop
naturally, and ask: does energy per *correct* answer rise with level, and is
the rise entirely explained by how many tokens the model emitted?

*Why it matters.* "Harder questions cost more energy" is the sentence every
practitioner wants; the honest version separates two mechanisms — the model
*thinks longer* (more decode tokens at near-flat power, so more time) versus
the model *does more work per token* (which, on a dense model at fixed shape,
it cannot, because the computation graph is the same for every token). The
bank's planning fact PC-4 (bank line ≈1608) is that decode power is nearly
flat, ≈23–28 W from 1.5B to 122B-A10B (the A-suffix is a sparse model's active
parameter count: 122 B stored, 10 B read per token), so decode energy
differences are decode *time*. If emitted tokens explain the whole rise, difficulty is a
length effect; a residual after length is the interesting result.

*What the answer looks like.* Five numbers (J per correct answer at each
level) with the binomial uncertainty of the denominator: at 32 items per
level, a 50% accuracy has ±17% on the count of correct answers
(`RQ-NEXT-EPCA-LEVELS`), which dominates the energy uncertainty because a
level window's energy is hundreds of joules against a 5 J bar. Worked case
from `RQ-D-A10`: 32 attempts, 16 correct, a 6 J aggregate difference is
6/16 = 0.375 J per correct answer; with 4 correct it is 1.5 J — the
denominator, not the instrument, sets the resolution.

*Windows, paper, prerequisites.* 5 windows (plan Phase 2b, windows 49–53),
Paper D applied section. Prerequisite: a **policy ruling** extending AP-5 —
the bank's rule that correctness is a quarantined annotation, never a
capability claim (C-004, the July council ruling that quarantines
correctness) — to the MATH source; without it only "energy beside external
scores" is licensed (D-041, the decision that permits scored workloads only
as annotation). Contamination (the model may have seen the problems in
training) means the claim is shape-only: "on this frozen subset, at this token
envelope (prompt and output budget)", never "harder problems cost more".

#### Axis 2 — same size, different quantizations, and *why* (ranks 1 and 4)

*Plain words.* Quantization stores each weight in fewer bits (16-bit → 8 →
4). For one model at one size, how much energy does each recipe save, and is
the saving because the chip draws less power or because it finishes sooner?
Then across sizes: is energy per decoded token simply proportional to the
bytes the chip must read per token?

*The mechanism, built from the numbers.* During decode every output token
requires reading all the model's active weights once from memory, plus the
per-token cache of everything already in the context (the *KV cache*: one
key vector and one value vector per layer per token). Qwen3-8B has 8.2 B
parameters (Astra draft §2, from the official card): 16.4 GB at 16-bit,
8.2 GB at 8-bit, ≈4.1–4.6 GB at 4-bit (Astra's 4.10 GB is the bare
parameter count at 4 bits; the Fable draft's ≈4.6 GB adds the scale-factor
overhead every 4-bit recipe stores; ASSUMED either way). Its KV cache is
2 × 36 layers × 8 heads × 128 × 2 bytes ≈ 147 KB per token, so a 4096-token
context is ≈0.6 GB read per token (Astra §2, from the config file: 603,979,776
bytes). Decode is memory-bandwidth-bound: at an ASSUMED ≈400 GB/s effective on
the M3 Max, reading 16.4 GB takes ≈41 ms per token; 4.6 GB takes ≈11 ms. At
the ≈25 W flat decode power that is ≈1.0 J/token at 16-bit against
≈0.29 J/token at 4-bit — a ≈3.5× saving that is *almost all time*, not watts.
The 4K-context (4096-token) cache adds ≈4% for 16-bit and ≈13% for 4-bit: the cheaper the
weights, the larger the cache's share. A *dequantization* cost (unpacking
4-bit weights into arithmetic-ready form) is the term that would make the law
non-linear; Arya & Simmhan found INT8 can cost *more* than FP16 on some
stacks (record 21 §1), which is exactly what a dequant term predicts.

*What the answer looks like.* Rank 4 (`C5-1.12`, one 8-bit 8B cell in
Paper C, plan window 11): a split — "of the X J saved per 512 tokens, Y J is
lower mean power and Z J is shorter time". Rank 1 (`RQ-NEXT-BYTES-LAW`):
one fitted line, E/token = P × bytes/BW_eff (P the flat decode power,
BW_eff the effective memory bandwidth), across Qwen3 1.7B/4B/8B/14B/32B
dense plus 30B-A3B and 122B-A10B sparse, with the 14B point held out and
predicted before it is measured. Resolution: 10% of a 47 J 512-token decode
≈ the 5 J bar, so at d = 2048 the law resolves ≈1.3% departures. The
*negative* is as publishable: a resident-but-inactive-bytes term (the whole
mixture-of-experts model, not just its active experts, costing energy) would
show as sparse points above the line — the mechanism ML.ENERGY v3's 3.56× [3]
versus Fernandez's +54% [16] disagree on.

*Windows, paper, prerequisites.* Rank 4: 1 window, Paper C, the 8-bit
artifact pinned. Rank 1: 5 windows with the new models' floors inside them
(plan Phase 2 windows 1–5), Paper D; Qwen3-Next-80B-A3B runtime support
NEEDS-WEB; quantization *group size* (how many weights share one scale
factor) must be held constant across sizes (the risk both seats name).

#### Axis 3 — workload-profile variation as the investigated axis (ranks 6–9)

*Plain words.* Hold the model fixed and vary what the request looks like —
prompt length, output length, content category, whether the prompt is
shared with the previous request — and ask which of those move energy, by
how much, and whether the answer is the same for every model.

*The mechanism.* Prefill is compute-bound (every prompt token is processed
in parallel; energy ∝ active parameters × prompt tokens at high power);
decode is bandwidth-bound (one token at a time at near-flat ≈25 W). So a
request's energy is E = fixed + a·p + b·d (`Q4`), and the *ratio* of the two
slopes has a physical meaning: p\*/d is the prompt length at which prefill
and decode cost the same, and if the roofline picture is right it is a
device constant that transports to a held-out model
(`RQ-NEXT-PHASE-CROSSOVER`). Content, by the same picture, should not matter
at fixed shape: the Token-Shape Sufficiency Null (bank §Workload expansion)
— a category effect that survives matched token counts is the surprise, and
its absence is a result.

*What the answers look like.* Rank 7: per-model coefficients (fixed, a, b)
with held-out shapes (512, 256) and (4096, 512) predicted within the floor
(bank line 509). Rank 6: a single number p\*/d per model, predicted for the
held-out model before it is measured (ladder rung L3). Rank 8: a null or a
category effect above the floor, on the five conditions of AP-6 (the content
sentinel's analysis plan: five synthetic content variants at one fixed
shape). Rank 9: an ordering (code vs long-context vs reasoning) per model
and whether it flips.

*Windows, paper.* Plan Phase 1 windows 3–10 (grid + validation), 20–24
(sentinel + categories); Phase 2 windows 8–12 (crossover + chunk).
Prerequisites: none beyond the held-out shapes being reserved before
collection (AP-1). The categories' natural-stop mode (`natural_eos`: EOS is
the end-of-sequence token, so natural stop means the model chose to emit it)
must report stop reasons so a cheap wrong answer is visible as a short one.

#### Axis 4 — same query, repeated: the spread as a first-class result (rank 2)

*Plain words.* Run the identical request ten times under identical
declared conditions. How far apart are the energies, what makes them
differ, and how does that spread compare with the instrument's own timing
uncertainty?

*What is already known, diagnostically.* Repeat scatter is small. The
1.5B-vs-7B diagnostic contrast had σ = 0.241 J over n = 10 blocks (a
*block* is one ABBA group of four runs, the design defined just below) on a
≈146.7 J whole-request difference (`CLAIMS_STATUS.md` §2, labelled
diagnostic) — 0.16%. The three diagnostic-era cells' point floors (0.29,
0.49, 0.31 J) were 5.9–10.9× *smaller* than their timing-widened floors
(draft §3). The paper's primary finding is precisely this ratio:
attribution beats scatter. That makes "the variance" a two-part result: the
tiny repeat spread, and the fact that it is not the limiting term.

*What drives the spread, and how to test each.* The plan's contrasts run in
**ABBA** order — condition A, then B, then B, then A; one such group of four
runs is a *block* — so any steady drift across the block cancels in
(B₁+B₂−A₁−A₂)/2 (draft §5). An
*identical-condition null* is an ABBA block whose A and B are the *same*
condition, so the true difference is zero and anything the block reports is
the instrument's own manufacture. Each driver below is a one-arm design
inside floor windows the plan already runs, so 0 extra Ed-hours:

| driver | mechanism | test | what the plan already has |
|---|---|---|---|
| thermal state | a warmer chip runs at lower clocks for the same work → longer time at similar power | correlate member energy with the pre-member cooldown exit time and the thermal-pressure column (macOS's own reported thermal state); ABBA blocks cancel *linear* drift, the residual is curvature | cooldown gate ≤300 s to ≤1.10× reference power; `thermal_pressure = nominal` admission (draft §5) |
| position in window | slow drift (heating, background daemons) makes later members differ from earlier ones | the *reference runs* — one fixed, identical workload run three times at the window's opening, once at its midpoint and three times at its close — give the drift trajectory; `RQ-ORDER-POSITION` fits energy against slot index | reference runs in every window (paper Figure 2) |
| memory placement / page state | first run after load pays page faults and cache misses | the warm-up rule Leg 2 asks the paper to state: first member per model per window discarded, count printed | not yet stated explicitly (record 21 §2 warm-up row) |
| sampling (non-greedy: greedy decoding always emits the most likely token so repeats are identical; sampling draws, so output length varies) | different output length per repeat → different decode time | `RQ-ENERGY-VARIANCE`: repeat with recorded seeds, replay the token paths, split variance into length-explained vs residual | plan Phase 1 windows 15–16 |
| the instrument | timing bound applied to every member | the identical-condition null must contain zero within the floor | paper Table 1 row 2 (draft §3) |

*What the answer looks like.* A figure: per-cell repeat spread (J and %)
beside the timing-widened floor, with the drift trajectory and the
length-vs-residual split for the sampled arm. The sentence: "on this unit
the same request repeats within ≈0.3 J; the instrument's boundary
uncertainty is ≈1 J; sampling length explains X% of stochastic variance".
No Apple study has printed any of those three numbers (record 21 §1).

*Windows, paper.* 2 windows (Phase 1 windows 15–16) plus riders in every
floor window; Paper C variance section, with the null and drift parts
already Paper B obligations (coverage map "Non-registry paper obligations").

### The wall-meter question set (rank 3) and the disagreement about what it licenses

*What the meter is.* The ChargerLAB POWER-Z KM003C is a pass-through on the
USB-C cable between the power adapter and the laptop; it logs voltage and
current on that wire (Fable draft Leg 1; [31]). Retail pages say 1%
accuracy, up to 1000 samples/s — **NEEDS-WEB**: the manufacturer's page and
manual refused the fetch (HTTP 403, both drafts). It arrives ≈17:00 PDT
2026-09-17 (ASSUMED from the brief).

*What it measures, physically.* A *boundary* is the set of physical parts
whose power a reading includes. The meter's boundary is the direct-current
(DC) power delivered into the laptop: the processor, memory, display
backlight, SSD, fans and the charger circuit, minus nothing. It excludes the
adapter's own AC-to-DC conversion loss, so it is **not** wall (AC) power. The
counter's boundary is different: `powermetrics` reports the CPU, GPU and ANE
(Apple's neural engine) on the chip and nothing else. And the battery sits
between the cable and the chip: below full charge the meter reads chip power
*plus* charge current; when the chip draws more than the adapter supplies,
the battery makes up the difference and the meter reads *less* than the chip
drew.

*The question set, in order:*

1. **Logger host** — does logging over the meter's HID interface (a
   driverless USB device class) from the measured Mac itself add load above
   the idle floor? Measured, not assumed (lane A214 clause a).
2. **Battery participation bound** — the signed battery energy
   ∫V·I dt over each block *and* the unsigned ∫|V·I| dt (charging and
   discharging can cancel in the signed total while substantial buffering
   occurred; Astra §1 step 4). Proposed admission: participation below 1%
   of block energy and below 20% of the smallest difference the experiment
   intends to resolve (Astra's proposed budgets, not repository thresholds).
   The Fable draft's simpler rule is a *50 mA refusal*: any block during which
   battery current exceeds 50 mA is refused outright.
3. **Alignment** — the same 59 GPU pulses are visible on the meter as
   steps of tens of watts, so the meter's samples are placed on the wall
   clock by the same edge-fitting, not by the meter's own timestamps
   (Fable Leg 1 clause c; Astra step 7 adds 5/10/20 s plateaus with unequal
   gaps).
4. **The fit across a load ladder** — one ratio hides a slope (Jay et al.
   [5] found 1.17–1.18 and load-dependent). Fit E_DC = a·T + b·E_software
   per block (T the block duration, so a is a constant power outside the
   counter's boundary and b a scale factor on what the counter reports) with
   blocks ≥60 s (Astra §1 "What number comes out"), across idle, the 1.7B and
   8B decode cells, the 30B-A3B prefill cell, and GPU pulses at three duty
   levels (duty: the fraction of each second the pulse is on; Fable's rungs), ≥10 repeats in ABBA order. Worked illustration
   (Fable Leg 1, not data): idle 6.0 W meter vs 1.2 W counter; 8B decode
   38.0 W vs 31.5 W → a ≈ 4.7 W (backlight, SSD, charger), b ≈ 1.06.
   Curvature across rungs or a b whose interval excludes 1 is the
   load-dependent finding.
5. **Held-out day** — repeat the held-out blocks on a different day with a
   fresh alignment and battery qualification (Astra's milestone M4); the largest
   held-out prediction error is a reported number.

*The disagreement.* The registered lane A214 (`TASK_QUEUE.md` row E214) and
the Fable draft call the slope a **gain** — "the calibration of the
total-energy scale". Astra's draft numbers its requested rulings R-n, its
findings F-n and its verifications V-n; its row R1 (`needs_ruling`) objects:
the slope bundles four things — counter error, loads outside the reported
channels (backlight, SSD, memory), conversion and cable losses, and battery
flow — and cannot identify counter gain separately from them; a slope of
1.06 does not mean the counter under-reports the chip by 6%. Astra also
notes that `wall_meter` already means *AC wall power* in the repository's
boundary vocabulary (D-018, `docs/decision_log.md` line 1073: "wall_meter: AC
wall power (full system)"), so the DC reading needs its own boundary
identity in the *rail manifest* (the repository's list of named power
boundaries). Its proposed claim: "for this laptop, power configuration and
workload range, this relationship predicts measured USB-C input energy from
the named processor estimates, with this uncertainty and held-out error" — a
**workload-conditioned DC-boundary mapping** (a *mapping* is a fitted
relationship between two boundaries' readings; a *gain* would be a
correction factor applied to one of them).

*My reading: Astra is better argued on the claim, Fable on the mechanics.*
The physics is Astra's: the meter's boundary (DC into the whole laptop) is
not the counter's boundary (CPU + GPU + ANE on the chip), so a slope between
them is a mapping between boundaries, not a correction to one of them;
multiplying phase energies by it would be a category error, and the A214
acceptance text (b) as written invites that error. Fable's design — pulse
anchoring, the ABBA ladder, the ranging run, the 50 mA refusal — is the
better operational protocol and survives intact under Astra's wording;
Astra's battery *energy* integrals and held-out day are strict improvements
to it. **Ruling the magistrate must make before the desk arm starts:** (i)
A214's claim wording — "gain calibration of the total-energy scale" →
"workload-conditioned mapping from processor-counter energy to USB-C DC input
energy, with interval and held-out error"; (ii) a new boundary identity (for
example `usbc_dc_input`) distinct from `wall_meter` (AC) in the rail
manifest; (iii) which battery budget is adopted. What the paper can then say
is exactly what Fable's §"How we compare" already drafts: traceable to a
consumer meter's datasheet, at a different boundary, ranged, pulse-anchored,
phase attribution cross-checked not calibrated.

*Windows.* Both drafts: 4 windows + 1 reserve, plus ≈3 desk blocks; Astra
insists (rightly, and the plan agrees) that the desk arm rides Phase 0's
desk day, not day 24 — only the ladder windows are horizon work.

### Two cheap instrument windows nobody has run on Apple silicon (rank 10)

From the Fable draft Leg 2 table, both `DIAGNOSTIC_NO_PACK` (a window class
that leaves the frozen pack untouched): (a) **counter update period** — run
`powermetrics` at 10, 20, 50, 100, 200, 500 ms against the pulse train and
count consecutive identical records; read the IOReport cumulative counters
(IOReport is Apple's kernel reporting interface; its energy counters are
Zeus's Apple read path [4], 1 mJ resolution, no administrator privileges) at
1 kHz and record the step period; the finding is the shortest interval at
which records are independent. (b) **Sampler overhead** — the same request
set with the sampler at 100 ms, 1000 ms and off, ABBA; report tokens/s
inflation and the sampler's own CPU time. Together with the meter mapping and
the anchoring bound these are the four facts record 21 found no Apple study
states, and they are Paper F's core (Part III, Papers E and F).

---

## Part III — Everything else

### Heterogeneous placement across device classes (Ed's original interest)

*Plain words.* The same request can be served by a Mac, a consumer NVIDIA
card, or a rented datacenter card. *Placement* is the choice of which device
class should run which model size, phase mix and prompt length for the least
energy. The **whole-request** version gives one device the entire request;
the **split-request** version runs prefill on one device, ships the KV cache
to another, and decodes there.

*Whole-request first, and what it needs.* Each device gets its own floor
windows (a floor never transfers across platforms — Astra §3 "All
claim-bearing cells need per-platform floors"), then the same ABBA contrast
design. The result is a placement rule that prints `not resolvable` where
the floors do not permit a direction. Fable's worked illustration: 8B int8
decode at 0.55 J/token on the Mac vs 0.42 on the 3080 Ti with floors of 0.04
and 0.06 → the 0.13 J/token difference clears both, "decode 8B int8 on the
3080 Ti class", boundary-labelled; prefill at 4K, 1.9 vs 1.7 J with a 0.3 J
floor → `not resolvable`. The boundary label is not decoration:
`powermetrics` reports chip channels, NVML reports **board power** (the card
and its own memory, nothing on the host [26]) — the two are not the same
physical boundary, and Astra's R7 forbids turning them into an "Apple vs
NVIDIA efficiency" ratio. What *is* legitimate: within-platform placement
orderings, whether a mechanism's direction replicates inside each boundary,
and whether the same functional law fits each platform with its own
coefficients.

*The recipe problem both drafts flag and Astra makes concrete.* "4-bit MLX"
(MLX is Apple's machine-learning framework, the Mac's execution leg) and
"4-bit CUDA" are different numerical recipes (group size, scales, zero
points, excluded tensors), so a matched cross-vendor comparison needs one
recipe on both ends. Astra proposes BF16 (16-bit floating point, the
unquantized recipe) on both at 1.7B and 8B — which means **new Apple BF16
cells with their own floors** (the `_v5` 4-bit floors do not license them)
and, because 8B BF16 is 16.4 GB, the 8B point fits neither the 12 GB 3080 Ti
nor the 16 GB 5080 (Fable §3a table; Astra §2: 16.4 GB is 15.27 GiB, where a
GiB is 2^30 bytes, so a nominal 16 GB card has no room for cache or runtime).
Consequence: cross-vendor *matched* comparison at 8B lives on the 80 GB cloud
card; the owned card gives matched 1.7B plus within-platform 8B int8/4-bit
results.

*What fits where (weights only; both drafts agree, Fable's table §3a with
fetched file sizes [28]–[30]):* 1.7B at any precision everywhere; 8B int8
(8.2 GB) and 4-bit on the 12 GB and 16 GB cards, 8B BF16 only at 80 GB and
on the Mac; OLMoE-1B-7B (7B total, 1.3B active [30]) at int8/4-bit on the
consumer cards; DeepSeek-V2-Lite Q4_K_M (llama.cpp is a C++ inference runtime; Q4_K_M is
one of its 4-bit recipes) is 10.5 GB [28] — on the 12 GB card only at short prompts; Qwen3-30B-A3B Q4_K_M
18.6 GB [29] and anything larger need the 80 GB card or the Mac.

*The second instrument class.* NVML exposes `nvmlDeviceGetPowerUsage`
(milliwatts) and `nvmlDeviceGetTotalEnergyConsumption` (a cumulative
millijoule counter, on Volta — NVIDIA's 2017 generation — and newer)
[26],[27]. Two cautions Astra adds that Fable lacks: on Ampere (the 2020
generation) cards other than GA100 (its datacenter chip), and on newer
architectures, the generic power query returns a **one-second average**
(NVML documentation, Astra §2) — the 3080 Ti's chip is GA102, an Ampere
part that is not GA100, so its polled power cannot resolve a sub-second
phase no matter how fast it is polled (**NEEDS-WEB + live probe** on the
actual card, along with whether GeForce exposes the energy counter at all);
and the repository's existing NVIDIA path is **PROVISIONAL**:
`joulewise/adapters/nvidia_smi.py:40` requests generic `power.draw`, and
`joulewise/adapters/node_worker.py:341,476` place the phase boundary at the
*first received stream chunk*, a service-delivery event that includes
software delay, not a device-completion event (Astra F3, V2). Both must be
rebuilt before any NVIDIA *phase* claim; request totals and printed phase
refusals are the honest first NVIDIA result (Astra risk 3).

*What replaces the quiet-machine census.* The *census* is the process-list,
load and clock check that refuses a window if anything else is running on
the machine. On the owned rig: process list, load, `nvidia-smi
--query-compute-apps` empty, NTP state (NTP is the network time service that
nudges the system clock; an active correction would move the timeline under
the measurement), and NVML's die temperature — better than the Mac, which
exposes no die temperature (Fable Leg 2 thermal row). On cloud: the census
sees only our own virtual machine; noisy neighbours are *detected* by the
reference-run spread, never gated, and a spread above the floor prints `not
resolvable` (Fable §3a; Astra §3 step 2's provisional screens: host CPU <5%,
idle power within max(3 W, 5%), start temperature within 3 °C).

### Cloud vs owned rig vs friend's 5080

| | owned RTX 3080 Ti, 12 GB | friend's RTX 5080, 16 GB, Windows, remote | rented 80 GB H100/A100, Linux |
|---|---|---|---|
| models | 1.7B all; 8B int8/4-bit; OLMoE; DS-V2-Lite short prompts; 14B 4-bit (Astra) | same + full DS-V2-Lite cache; 20–24B 4-bit conditional | through 70B 4-bit, 32B BF16, 30B-A3B BF16 |
| instrument | NVML; 1 s-averaged generic power on GA102 (NEEDS-WEB); energy counter on GeForce NEEDS-WEB | same, plus Windows/WSL2 caveats (WSL2 is Linux running under Windows; NVML queries such as utilisation are missing there, Astra §2) | full NVML; best-supported |
| quiet control | full census port; dedicable | agreed no-use intervals only; remote desktop itself loads the GPU | own VM only; neighbours detected not gated |
| Ed-hours and dollars | Fable 2–3 h once / Astra 4–8 h setup + 0.5–1 h per session; ≈$0.25/window electricity (Fable, ASSUMED 350 W) or ≤$3.38 for 25 h (Astra, 0.45 kW × $0.30/kWh) | Fable 2–4 h per session / Astra 3–6 h + friend's 1–2 h; $0 | Fable 0.5 h / Astra 2–4 h; see arithmetic below |

*Dollar arithmetic, cited not recomputed.* Fable §3b: 12 windows at
$1.39–4.29 per GPU-hour [21],[22] → $3.5–11 per 2.5 h window → **$40–130**
per campaign. Astra §5: 12 windows × 2.5 h + 5 setup hours = 35 billed
hours at H100 PCIe $3.29 / SXM $4.29 [21] (PCIe and SXM are the card's two
form factors; SXM is the faster, pricier one) → **$115–150** (Astra line
397: $115.15–$150.15); the full 30-window NVIDIA plan, 80 billed hours →
**$263–343** (Astra line 405: $263.20–$343.20). Astra's is the
better-founded figure: it includes setup hours, uses the verified
single-H100 prices, and notes that a single A100 80 GB at $1.39–2/h is a
search snippet, not a fetched offer (Fable [22] says the same in its source
note). Take **≈$115–150 for a 12-window cloud tier** as the planning number.

*Primary platform: the drafts disagree.* Fable: owned 3080 Ti primary
(near-zero Ed-hours after one evening, exercises the port both others
reuse), cloud secondary for what the card cannot hold. Astra: rented H100
primary (memory headroom, native Linux which the existing
`node_worker`/`vllm_runtime` adapters target — vLLM is a Linux GPU inference
server — predictable access), 3080 Ti secondary for repeatable checks.
**Resolution:** Fable's order is right *on Ed's stated objective* (CV per
Ed-hour) — but only if the rig runs Linux and exposes the telemetry; Astra's
next-action ("read-only inventories of the owned rig and a candidate cloud
instance") decides it. If the rig is Windows, or GA102's 1 s averaging plus a
missing energy counter leave only request totals, Astra's order wins and the
rig becomes the third device-class point. Both agree the 5080 is never on
the critical path.

### The split-request transfer rider

Measurable: Mac-side prefill + serialise-and-send under `powermetrics`; rig-
side receive + deserialise + decode under NVML; and, if the Mac's Ethernet
adapter is a USB-C dongle, the KM003C between Mac and dongle logs the
dongle's own DC — a second use of the meter (Fable §3c). Not measurable: the
switch, the cable, the rig's NIC (network card; outside board power), and
whether the Mac's USB4 controller is even inside the package figure [25]
(NEEDS-WEB). Size: Qwen3-8B, 8192-token cache = 1,207,959,552 bytes (Astra
§4) → ideal wire time 9.66 s at 1 GbE (gigabit Ethernet), 3.87 s at 2.5 GbE, 0.97 s at 10 GbE,
before serialisation overhead; Fable's 2K-prompt case is ≈0.3 GB, ≈2.4 s at
1 GbE. Blocker both name: the cache format must be portable between runtimes
— MLX and CUDA do not share one; one runtime on both ends (llama.cpp on
Metal, Apple's GPU API, and on CUDA) is the ASSUMED route. Budget: 5
windows, ≈1 Ed-hour for adapter and cable, ≈$40 ASSUMED. Result: one figure
with a stated attribution limit — link energy bounded below by the dongle's
DC, unbounded above on the rig side. Astra's staging (fixed byte buffers → a
real saved cache → decode from it with output verified) is the right order
of proof.

### Interconnect questions — the straight answer

Fable says "mostly no"; Astra says "yes, some". They agree on every fact and
differ on emphasis. The straight answer:

| question | answerable? | on what | attribution limit |
|---|---|---|---|
| transfer *time* and bytes vs link rate (1/2.5/10 GbE) | **yes** | Mac ↔ rig, owned | timing and bytes only; NIC/switch energy invisible |
| host-to-GPU copy rate on the rig | yes | owned | board energy only |
| KV-cache transfer *energy* | **partially**: device-side deltas + dongle DC | owned | rig NIC unmeasured; link energy is a lower bound |
| NVLink vs PCIe tensor parallelism (splitting one model's layers across several cards in one box; NVLink is NVIDIA's card-to-card link, PCIe the ordinary bus) | only on rented multi-GPU (8×H100 SXM $31.92/h [21] → ≈$80/window) | cloud | sum of board energies at TP=2 vs TP=1; the NVSwitch fabric (the chip that connects the cards), host CPU and NIC are outside — the weakest attribution in the program |
| cross-node disaggregated prefill/decode (Splitwise [14], DistServe) | no, as an energy question | — | needs two nodes and a serving stack that ships the cache; device-side deltas only = the rider above |
| multi-Mac over Thunderbolt vs Ethernet | no | one Mac owned | — |
| joules in the NIC or fabric | **no** with any owned instrument | — | needs its own meter |

Neither consumer card has NVLink (Astra §4, product pages). Ranked last on
metrology fit by both drafts; the timing-and-bytes results are cheap and
honest, the energy results are not attributable.

### Literature practices not yet adopted (short table; costs from Fable Leg 2)

| practice | mechanism | cost | closes |
|---|---|---|---|
| counter update period / stale reads [9],[10] | cadence sweep vs pulses; IOReport step period | 1 window + 0.5 desk | "do 100 ms averages alias?" |
| sampler overhead [6], NAACL 2025 | 100 ms vs 1000 ms vs off, ABBA | 1 window | "does the instrument change what it measures?" |
| die temperature + ambient [2],[11] | `powermetrics`' `smc` sampler (the system-management-controller sensor set that reports temperatures on Intel Macs) is refused on Apple silicon (NEEDS-WEB on this build); log the thermal-pressure level per record; ambient needs a ≈$20 USB logger (ASSUMED) | 0.5 desk | "what was the chip's and the room's temperature?" — answered as a stated limitation |
| explicit inference warm-up rule (Cruz; [11]) | first member per model per window discarded, count printed | 0.25 desk | "was the first request cold?" |
| fixed n vs adaptive stopping (Wilkins) | one paragraph: adaptive n makes the resolution bound data-dependent | 0.25 desk | "why not repeat until the interval closes?" |
| ranging run before fixed ranges [1] | rides meter window 1 | 0 | "was the meter's range fixed first?" |
| Zenodo DOI + README with measured step times (ACM badging; ICPE AE) — this row *is* Release 0 in Part IV | package packs, bundles, reduction code; state the floor-binding limit (the open lane FLOOR-BIND-01: a floor artifact currently supplies its own timing widths and campaign membership, so a third party cannot independently re-derive the floor-to-claim link — the paper's §9 calls this "the L1 floor-binding limitation") | 1–2 desk-days for the badge alone; 2–3 seat-weeks for the pip package (Part IV); Ed 0.5 h | *Available* + *Functional* badges |

### Ranking Part III by the same value definition

| rank | item | novelty | claim | why | CV/Ed-h | product | Ed-hours | dollars |
|---|---|---|---|---|---|---|---|---|
| 1 | artifact package + DOI (Release 0) | 2 | — (badge) | 1 | 3 | — | 0.5 | 0 |
| 2 | whole-request placement on the owned card (+ method replication inside it) | 2 | 2 | 2 | 2 | 16 | 3–8 once | ≈$3 |
| 3 | cloud 80 GB tier: matched BF16 8B, 30B-A3B vs 32B, 70B if it fits (speculative) | 2 | 2 | 3 | 2 | 24 | 0.5–4 | $115–150 |
| 4 | cross-vendor bytes-law transport (`RQ-NEXT-ROOFLINE-DEVICE`, `RQ-D-A15`) | 3 | 3 | 3 | 1 | 27 | inside 2–3 | inside 2–3 |
| 5 | split-request rider | 2 | 1 | 2 | 1 | 4 | ≈1 | ≈$40 |
| 6 | friend's 5080 | 1 | 2 | 1 | 1 | 2 | 2–4/session | 0 |
| 7 | multi-GPU interconnect on cloud | 1 | 1 | 1 | 1 | 1 | 0.5 | ≈$80/window |

Row 4 outranks rows 2–3 on product but *depends* on them (it is the same
windows with a frozen equation and a held-out model), so it is listed
fourth; it is the reason to run 2–3 at all beyond a leaderboard.

### Week ladder from day 24, consolidated

| week | Fable draft §5 | Astra draft §5 | where they differ, and the consolidated line |
|---|---|---|---|
| H1, days 24–30 | meter ladder (4); two Apple diagnostics (2); Leg 2 desk items; rig port begins | meter (4+1); NVIDIA diagnostics (2+1); 3 meter + 6–9 NVIDIA desk blocks | Same week shape. Astra adds NVIDIA sensor characterisation *before* any rig floor and puts it here; Fable has the rig port as seat work only. **Consolidated:** meter ladder + Apple diagnostics + NVIDIA sensor characterisation on whichever platform the inventory picks. Ed: plug the meter (0.25 h) + rig inventory evening (2–4 h) or cloud account (0.5 h). |
| H2, days 31–37 | 3080 Ti floors + placement grid (12, back-to-back); artifact package + DOI | on **each** platform: 4 floors, 2 contrasts, 1 held-out validation, 2 reserve (9), matched 1.7B/8B BF16 | Differ on recipe: Fable reuses the Mac's minted 4-bit cells; Astra requires new matched BF16 Apple cells. **Astra is right for any cross-platform comparison**; Fable is right that within-platform placement needs no new Apple cells. **Consolidated:** owned-card placement grid at its native recipes (Fable) + one matched-BF16 1.7B pair on both (Astra, the 8B BF16 pair waits for cloud). The artifact package moves *earlier* than Fable's H2 — it is Release 0, shipped with Paper B (Part IV). |
| H3, days 38–44 | cloud tier (12) | scaling roster on each platform (10) + 3080 Ti request-total windows (5) | Fable's cloud tier and Astra's scaling roster are the same windows under different names. **Consolidated:** cloud 12 windows = 4 floors + BF16 8B match + 30B-A3B vs 32B + the scaling roster (the ladder of model sizes) with 14B held out. |
| H4, days 45–51 | split-request rider (5); optional 5080 | KV-cache mechanism on each platform (8); Paper F core | Different content. **Consolidated:** KV-cache surface on the cloud card (Astra's 8) if the bytes law stood in H3; the split rider only if the cabling is already done; 5080 never on the path. |
| H5+, days 52– | writing E and F | optional network feasibility (days 52–58) | **Consolidated:** writing; network timing-and-bytes only if a second endpoint exists. |

Ed's physical total: Fable ≈5.5 h + optional; Astra 12–19 h. The gap is
Astra's rig setup (4–8 h) and cloud provisioning (2–4 h) estimates versus
Fable's 2–3 and 0.5; both are ASSUMED. Plan on Astra's numbers and be
pleased if Fable's hold.

### Papers E and F — two sketches each, one recommendation

Fable: **E** = "Energy-first placement of LLM requests across device
classes: a pre-registered, floor-bounded, cross-vendor measurement" (the
placement rule as headline; NVML as the second instrument class inside it);
**F** = "What `powermetrics` measures: calibrated gain, counter granularity
and sampler overhead for Apple-silicon energy metrology" (workshop-length;
the four facts no Apple study states). Astra: **E** = "What carries across
counters? Phase-energy resolution on Apple silicon and NVIDIA GPUs" (which
phases resolve on which instrument; explicit negatives); **F** = "When bytes
predict inference energy: held-out scaling and cache tests across Apple
silicon and CUDA".

Recommendation: Fable's F, retitled per the meter ruling ("mapping", not
"gain"), is the cheapest CV line in the program — ≈8 windows, most already
inside H1–H2, a HotCarbon/e-Energy-workshop shape (two venues in Part IV's table),
squarely in the advisor's lineage. For E, merge the two: Astra's cross-counter resolution question is
the *method* contribution a metrology reviewer accepts, and Fable's
placement rule is the *application* that answers Ed's original interest;
Astra's bytes-law F becomes E's second results section once the law stands
on the Mac (Paper D) — it does not need its own paper.

---

## Part IV — Is the tool worth publishing or rewriting formally?

### What the repository is, by its own evidence

`joulewise/` is 100 `.py` files and ≈130 k lines of Python by `wc -l`
(129,593 at `dc119f7d`; the count includes generated schemas and long
tables), 231 test files with ≈6 000 test functions (5,971 `def test_`
definitions by grep at `dc119f7d`), ≈110 scripts, ≈3,600 Markdown files
(mostly process custody, not user docs), and a package layout that is one
tool's worth of mechanism and one project's worth of process:
`powermetrics_fiducial.py` (the pulse detector — a *fiducial* is a reference
mark of known timing, here the commanded GPU pulse), `clock.py` /
`clock_reference.py` (the rate-aware anchor: a fit that lets the sampler's
clock and the runtime's clock differ in *rate*, not only in offset),
`detection_floor.py` / `floor_mint_estimator.py` (the resolution bound),
`envelope_gate.py` / `idle_admission.py` / `environment_admission.py` (the
admission gates: machine-state checks a window must pass before capture),
`paper_custody.py` / `authentication_io.py` / `receipt_oracle.py` (custody),
`night_agent_install.py` / `night_gate.py` (the unattended chain), and
adapters `mlx_runtime`, `vllm_runtime`, `powermetrics`, `nvidia_smi`,
`node_worker` / `node_client` / `ssh_transport` (a second backend exists,
PROVISIONAL per Part III). Packaging today: `pyproject` 0.1.0, stdlib-only
core (it imports only Python's standard library), a `python -m joulewise`
CLI with 13 subcommands (`run`, `validate-config`, `kv-size`, …) that is
*governed* — every command runs under the custody rules; **not on PyPI, no
`CITATION.cff` (the machine-readable citation file GitHub and Zenodo
recognise), no Zenodo DOI, 0 GitHub stars, no software release** (the latest
tag is a git tag for test data, not a release, from 2026-08-09) — viability
seat Table 1b.

### What is unique, and what is Apple-shaped

| unique (no published tool has it) | Apple-specific today |
|---|---|
| in-session pulse-train calibration with a rate-aware clock anchor that retains a *set* of feasible alignments and refuses when network time correction is active (draft §2) | the pulse is a Metal/MLX GPU matrix multiply; the trace parser reads `powermetrics` plists; the clock model was fitted to `powermetrics`' whole-second labels |
| cell resolution bound by corner enumeration (each member's energy is an interval — its point value widened by the timing bound — every combination of interval ends is a corner, and the bound is the worst corner) with attribution-limited labelling (draft §4) | the *timing envelopes* (the per-record interval of possible energies the timing bound implies) assume a 100 ms interval-average sampler; NVML's 1 s-averaged power (Astra §2) needs a different envelope model |
| two-gate decision + printed refusal + resolvability rule (a phase must be covered by ≥3 records) | the admission gates read macOS fields (`thermal_pressure`, `display_power_state`, `low_power_mode`, adapter watts) |
| pre-registration: frozen packs, hashes, freeze receipts (a signed record that a pack was frozen at a given hash and time), held-out rules before collection | portable in principle; the pack format is repo-shaped |
| custody: fingerprinted inputs, retained failed attempts, verdict bound to the member set | portable; `paper_custody.py` is not an API |
| unattended window chain with census, refusal and dead-man behaviour (a scheduled check that stands the night down if the chain has not reported) | launchd-specific (macOS's service scheduler) |

### Comparison with existing tools (viability seat §1, fetched 2026-09-16)

Two tables because ten columns do not fit. Table 1a is what each tool
measures and how; Table 1b is how rigorous and how packaged it is. Star
counts, licences and release dates were read from the GitHub API on
2026-09-16 by the viability seat. A *backend* is the piece of code that
talks to one power source; *cadence* is how often readings arrive.

**Table 1a. Backends, sampling, phases, uncertainty, anchoring.**

| Tool | Platforms / backends | Sampling method and cadence | Per-phase (prefill/decode) energy | Any uncertainty / resolution bound | Time anchoring between samples and workload |
|---|---|---|---|---|---|
| **Zeus** (ml.energy) [32] | NVIDIA via NVML (cumulative energy counter on Volta+, power polling on older GPUs); AMD via AMDSMI (AMD's management library; ROCm is its GPU stack, 6.3+); Intel/AMD CPU via RAPL; Apple silicon via IOReport; Jetson (NVIDIA's embedded boards) on-chip | Counter delta between `begin_window` / `end_window`; background polling process where no counter exists; cadence not stated on the measure page | Only what you wrap: a window is any code block, so you can wrap prefill and decode yourself. No boundary calibration | None. `zeus.profile` picks a measurement and cool-down duration "to yield stable, low-variance energy readings" — variance reduction, not a bound | None beyond the counter read at window edges. The Apple RFC [33] (closed, opened 2025-03-09) chose IOReport *because* it samples "at arbitrary times", rejecting `powermetrics` for "fixed time intervals" and root |
| **zeus-apple-silicon** [34] | Apple silicon only; private IOReport "Energy Model" cumulative counters: CPU per core/cluster, GPU, GPU SRAM, ANE, DRAM; no sudo | Counter delta at window edges, 1 mJ resolution; values "believed to be model-based estimates derived from utilization, frequency, and voltage, rather than direct power sensor readings" | Same as Zeus (wrap it yourself) | None; warns that windows under ~10 ms show quantization noise | Counter read at edges; no clock model |
| **CodeCarbon** [35] | Linux RAPL via powercap (the kernel's RAPL interface); Windows 11 EMI (its energy-meter interface); Intel Mac via discontinued Power Gadget; Apple silicon via `sudo /usr/bin/powermetrics`; NVIDIA via `nvidia-ml-py`; TDP-times-load fallback when no counter (the chip's rated maximum power times its utilisation) | Default `measure_power_secs` = **15 s**, with a 1 s scheduler for devices lacking counters | No | None stated | None stated |
| **ML.ENERGY Benchmark / leaderboard** [3] (https://arxiv.org/abs/2505.06371) | NVIDIA via Zeus/NVML; H100-class servers | Steady-state saturated batching; energy/request = steady energy ÷ steady tokens × mean output tokens; cadence not stated | No (whole-request per-token) | No repetitions, no CI (record 21) | Not stated |
| **Optimum-Benchmark** (Hugging Face) [37] | Wraps CodeCarbon; CPU + RAM always, GPU **CUDA only** (`gpu_ids`); no MPS (PyTorch's Apple-GPU backend)/Apple | `POWER_CONSUMPTION_SAMPLING_RATE = 1` second | Per named task window (`track(task_name)`); the inference scenario names tasks such as prefill and decode (record 21). Boundary = `torch.cuda.synchronize()` before start and stop, no calibration | None | CUDA sync only |
| **MLPerf Power** [1] (https://arxiv.org/abs/2410.12032; benchmarks page [38]) | Whole system at the wall via an external analyzer driven by SPEC PTDaemon (the analyzer-driver software); a rule set, not a library | Analyzer at 1 s, ≥60 s collection, ranging run then fixed ranges | No (system power or energy per stream) | Analyzer uncertainty must be ≤1% (compliance checker) — an instrument spec, not a per-result bound | NTP; checker tolerates 800 ms timestamp skew |
| **Scaphandre** [39] | Linux RAPL via powercap (Windows driver exists); per-process share by CPU time; no GPU ("except when running GPU intensive workloads") | Periodic counter read; interval configurable; exporters Prometheus (a metrics server)/stdout/JSON | No | None | None |
| **pyJoules / pyRAPL** (PowerAPI) [40] | Intel RAPL package/DRAM/iGPU, NVIDIA via NVML; Linux only, no macOS | Counter delta at start/stop (decorator, context manager, `EnergyMeter`) | Wrap it yourself | None; warns the reading includes every other process | None |
| **nvidia-ml-py / pynvml** [41] | NVIDIA only; raw NVML bindings (power, and cumulative energy on Volta+) | Whatever you poll; NVML counters update no faster than ~100 ms, 95% underestimate at 0.5 ms polling (Dauner [9]); `nvidia-smi` samples cover ~25% of runtime (Yang [10]) | No | None | None |
| **TokenPowerBench** (AAAI 2026) [42] | "GPU-, node-, and system-level power without specialized power meters"; NVIDIA-class telemetry; abstract says it will be open-sourced, no repo link on the abstract page (NEEDS-WEB for the code) | Cadence not stated on the abstract; a secondary summary says 1 Hz default up to 10 Hz (NEEDS-WEB on the primary PDF) | **Yes** — "phase-aligned metrics pipeline that attributes energy to the prefill and decode stages of every request"; no error budget for the boundary (record 21) | None stated | Not stated |
| **macmon** [43] | Apple silicon M1–M5; private API "the same data `powermetrics` exposes", **no sudo**; CPU/GPU/ANE watts, temperatures, frequencies | Polling; `--interval` in ms, default 1000 ms; TUI (terminal display), `pipe` JSON, `serve` Prometheus; Rust library | No | None | None |
| **asitop** [44] | Apple silicon; `sudo powermetrics`; display only | Display refresh; no logging | No | None | None |
| **JouleWise** (this repo) | Apple silicon via `powermetrics` (`sudo -n`, samplers `cpu_power,gpu_power,ane_power,thermal`); an `nvidia_smi` polling adapter exists (539 lines) but only the Apple path is calibrated and claim-bearing; MLX and vLLM runtime adapters | Interval-average records at a commanded **100 ms**; phase energy = integral of CPU+GPU+ANE interval power inside runtime-emitted phase boundaries (draft §2, §A.2) | **Yes, with a calibrated boundary**: 59 one-second GPU pulses before and after each window fit the sampler's edge placement; the operative timing bound is the larger of the pre- and post-window capture bounds plus a never-zero drift allowance (for the clock drifting between the two calibrations; ≥9.724 ms, draft §2); a prefill covered by fewer than 3 records is printed "not resolvable" (draft §1–§2) | **Yes**: per-cell resolution bound from repeat scatter, identical-condition ABBA blocks, all 2^n interval corners, a small-n guard (with few repeats the scatter estimate is itself uncertain, so the floor is widened by a Student-t factor), and a drift allowance; two gates (magnitude, direction with Holm) and printed refusals (draft §4) | **Yes**: five wall/monotonic clock pairs plus native second labels fit a rate-aware clock line; refuses on active NTP correction (draft §2) |

**Table 1b. Meter validation, statistics, custody, licence/stars/release, packaging.**

| Tool | Validated against an external meter | Repetition / statistics support | Pre-registration or custody of evidence | Licence / stars / last release (fetched 2026-09-16) | Packaging |
|---|---|---|---|---|---|
| Zeus | Not stated on the measure page; Jay et al. [5] found software meters read 1.17–1.18× wall slope, load-dependent | `zeus.profile` chooses duration/cool-down; no CI output | None | Apache-2.0 / **374** stars / `zeus-v0.16.0` 2026-07-07, pushed 2026-09-08; PyTorch ecosystem project [45] | pip `zeus-ml`, library API, some CLI |
| zeus-apple-silicon | No | No | None | Apache-2.0 / **8** stars / v1.1.0 2026-03-29 | header-only C++ + pip |
| CodeCarbon | No (docs do not describe it); Cao et al. [6] found software estimates ~20% off a Watts Up plug meter | No | None | MIT / **1,915** stars / v3.3.1 2026-09-09 | pip, decorator, context manager, `codecarbon monitor` CLI, dashboard |
| ML.ENERGY | No | None (single steady-state run) | None | leaderboard repo: no licence field / 13 stars / v3.0 2025-12-01 | Benchmark scripts + hosted leaderboard |
| Optimum-Benchmark | No | Repeats via config; no CI | None | Apache-2.0 / **341** stars / v0.6.0 2025-08-19, pushed 2026-05-26 | pip, Hydra (a configuration framework) CLI, Python API |
| MLPerf Power | It *is* the meter (analyzer at the wall) | Rules on run length; no repeat rule | Compliance checker, submission audit | Apache-2.0 / 28 stars (power-dev) / no releases, pushed 2025-09-11 | Rule set + PTDaemon; needs a ~$1k+ analyzer |
| Scaphandre | No | No | None | Apache-2.0 / **1,973** stars / v1.0.3 2026-07-17 | Rust binary, agent, Prometheus exporter |
| pyJoules / pyRAPL | No | No | None | MIT / 94 and 116 stars / v0.5.2 **2021-10-05** and v0.2.3.1 **2019-12-19** | pip |
| nvidia-ml-py | n/a | n/a | n/a | BSD / official; 13.610.43 released 2026-06-01; pynvml mirror 274 stars | pip |
| TokenPowerBench | Not stated | Not stated (record 21) | None | NEEDS-WEB (no repo link on the abstract page) | Framework (paper) |
| macmon | No | No | None | MIT / **1,885** stars / v0.8.2 2026-08-04 | Homebrew binary, Rust library |
| asitop | No | No | None | MIT / **4,635** stars / no releases, last push 2024-04-18 | pip CLI |
| JouleWise | **No** — draft §7: "no independent gain check against wall power"; ML-side counter cross-check is future work (record 21 §3) | **Yes**: ABBA blocks, fixed-before-collection n, Holm family, Student-t guard, held-out drift probes (draft §3–§5) | **Yes**: frozen SHA-256 packs, freeze receipts, append-only retry records, verdict binds the member set; but the floor-binding limitation (FLOOR-BIND-01) means a third party cannot yet re-derive the floor→claim link (draft §9) | MIT / **0** stars / no software release; ≈130 k lines in `joulewise/`, ≈232 k lines under `tests/` incl. fixtures (viability seat's count), 231 test files, ≈3,600 Markdown files | `pyproject` 0.1.0, stdlib-only core, `python -m joulewise` CLI (13 subcommands); **not on PyPI, no CITATION.cff, no Zenodo DOI** |

Reading the tables in one sentence: the field's tools are counter readers
with a begin/end window; none of them tells the user how large a false
difference their setup can produce, none calibrates where a phase boundary
falls on the samples, and none refuses.

#### Worked numbers behind the table (viability seat §1.1)

The cadence column decides whether a tool can see a phase at all. Take the
shapes JouleWise registers (draft §3): prompt 2048 / output 128, prompt
512 / output 512, prompt 128 / output 2048. Prefill durations on the M3 Max
are not quoted in the draft; assume a 512-token prefill of order one second
and a 128-token prefill of a few hundred milliseconds (ASSUMED — the draft's
resolvability rule exists precisely because short prefills sometimes overlap
fewer than three 100 ms records, draft §1).

- CodeCarbon at its default 15 s: a 0.3 s prefill overlaps zero or one
  sample. The tool cannot report prefill energy; it reports the request
  average and calls it done.
- GreenBench's `powermetrics` at 2 s [19]: the same prefill sits inside one
  2 s interval together with the first ~1.5 s of decode. Mean power ×
  latency then charges decode power to prefill or the reverse; no error bar
  is possible because there is one sample.
- Optimum-Benchmark at 1 s with `torch.cuda.synchronize()`: the sync places
  the *workload* edge exactly, but CodeCarbon underneath still averages over
  1 s intervals, so a 0.3 s prefill is at best one partially covered
  interval. Nothing in the tracker reports how much of that interval belongs
  to prefill.
- JouleWise at 100 ms: a 0.3 s prefill overlaps three to four records; the
  rule prints "not resolvable" below three. A 1 s prefill overlaps ten. The
  calibrated edge bound of ≈30 ms (draft §2 worked capture: 0.0300679 s) is
  then a known fraction of one record, and the energy it can move is power
  step × 0.03 s — at a 40 W step, 1.2 J — which is the ≈1 J figure the
  paper's abstract names.
- NVML counters (Dauner [9]): update period ≈100 ms, the same order as
  `powermetrics`. A begin/end window in Zeus or pyJoules that straddles a
  40 W step therefore carries the same ≈1 J ambiguity per edge; Zeus's
  window API does not expose it because the counter looks continuous.

The comparison the field cares about is a difference between two
conditions. In the diagnostic-era cells (draft §3), repeat scatter alone
gave floors of 0.29–0.49 J, and the calibrated edges widened them to
2.2–3.2 J, ratios 5.9–10.9×. A tool that reports only scatter would call a
1 J phase difference significant; the widened floor says it is inside what
the boundary can manufacture. That single number is the reason a researcher
would install this and not the others.

**Star counts, for scale.** Total stars across the nine competing repos
fetched: 4,635 (asitop, dormant since 2024) + 1,973 (Scaphandre) + 1,915
(CodeCarbon) + 1,885 (macmon) + 374 (Zeus) + 341 (Optimum-Benchmark) + 274
(pynvml) + 116 + 94 (pyRAPL, pyJoules) + 28 (power-dev) + 8
(zeus-apple-silicon) = 11,643. The three most-starred are monitors that
report watts and stop; the only Apple energy-window library has 8. The
market for "rigorous" is small and unoccupied; the market for "easy" is
large and taken.

### Gap analysis in plain words (viability seat §2)

**What JouleWise has that none of the twelve has.**

1. *A calibrated phase boundary.* Every other per-phase tool
   (Optimum-Benchmark, TokenPowerBench, Zeus-wrapped windows) takes the
   runtime's phase timestamp as exact. JouleWise measures, in the same
   session, how far the sampler's reported edges sit from commanded edges
   (59 pulses, bound ≈25–31 ms in the diagnostic era, draft §3) and carries
   that into the phase energy. The physics is general: any sampler with a
   finite update period — `powermetrics` at 100 ms, NVML counters at
   ~100 ms (Dauner [9]) — has this error, and a steep power step times a
   ~30 ms edge error is ≈1 J (draft §2). Nobody else quantifies it.
2. *A resolution bound with refusal.* The two-gate rule and the printed
   refusal ("not resolvable", "direction unresolved") do not exist anywhere
   in Table 1. AgentStop [18] and Watt Counts report a CI; that is the
   closest (record 21 §2).
3. *Pre-registration and custody.* Frozen packs, fingerprints and receipts
   before data exist. Unique in energy tooling; the nearest analogue is the
   accuracy-benchmark paired-MDE paper (Zhuang et al. [20]), not a tool.
4. *Counterbalanced ABBA with a measured drift allowance* and an admission
   gate on machine state (AC power, display asleep, thermal nominal, idle
   p95 — the 95th-percentile sample — ≤1 W). No tool in the table gates on machine state at all.

**What they have that JouleWise lacks.**

1. *Portable backends.* Zeus covers NVIDIA, AMD, Intel/AMD CPU, Apple,
   Jetson. JouleWise's claim-bearing path is one backend on one machine.
2. *A one-line library API.* `with ZeusMonitor(): ...` or
   `@measure_energy`. JouleWise is driven by a config file and a governed
   CLI; there is no `import joulewise; joulewise.measure(fn)`.
3. *Packaging and community.* CodeCarbon 1,915 stars, monthly releases;
   Scaphandre 1,973; macmon 1,885; Zeus 374 and a PyTorch-ecosystem badge.
   JouleWise: 0 stars, not on PyPI.
4. *Docs at a beginner's bar.* Zeus's measure page explains windows in a
   paragraph. JouleWise's README opens with seven defined terms and a
   1,500-word status log; its ≈3,600 Markdown files are process custody,
   not user docs.
5. *No sudo.* zeus-apple-silicon and macmon read IOReport without root;
   JouleWise needs a passwordless `sudo -n powermetrics` line.
6. *External-meter validation.* Only MLPerf Power has it, but JouleWise
   shares that gap with everyone else in the software-counter row — until
   the meter mapping (Part II) lands.

**Would researchers adopt the unique parts, or only admire them?** Honest
split:

- *Adopt*: the floor and the refusal, **if** they come out of a single
  function call with sensible defaults. Every 2025–2026 measurement section
  in record 21 that lacks a CI would have one if the tool computed it for
  them. The CodeCarbon issue tracker already asks for exactly this: issue
  #1350 (open, 2026-08-12) proposes a `codecarbon doctor` "to report
  measurement quality" [46].
- *Admire but not adopt as-is*: the pulse-train calibration. It needs 2 ×
  ~3 minutes of commanded GPU load per session, quiet-machine conditions and
  a clock model. Researchers will run it once per machine if it is a
  one-command `joulewise calibrate` that caches a bound; they will not run
  it per experiment. Custody, packs, freeze receipts and night-window
  installers are what a *campaign* needs, not what a library user needs;
  they should be shippable but off by default.
- *Neither*: the ~130 k-line governance surface. Reviewers will not read it
  and users will not install it.

### Evidence of demand (viability seat §3)

**What recent measurement sections get wrong (all from record 21, each
verified there by fetch).**

- Cadence unstated: Splitwise [14], Silicon Showdown [17] (`powermetrics`
  interval not stated), TokenPowerBench [13], ML.ENERGY [3].
- No CI or repeats: ML.ENERGY (no repetitions), Ruf & Detyniecki [12]
  (single run), GreenBench [19] (one warm-up, no error bars), Silicon
  Showdown [17] (mean of 3, no CI), Fernandez et al. [16] (3-run means).
- Boundary handled by eye or by construction: POLCA [15] reads the boundary
  visually from DCGM traces; Illusion of Power Capping [11] and Ruf [12]
  avoid it by running phases as separate operations.
- Cadence too coarse for the phase: GreenBench samples `powermetrics` every
  **2 s** and multiplies mean power by latency; CodeCarbon's default is
  15 s [35].
- No meter validation: Cao et al. [6] (~20% off a Watts Up meter), Jay et
  al. [5] (slope 1.17–1.18 vs wall); tracker overhead inflates inference
  time 15–50% (NAACL 2025).
- Record 21's summary line: "No Apple-silicon study states time anchoring
  between `powermetrics` and the workload, thermal control, or a resolution
  bound."

**Live user pain on the Apple path, from the biggest tool's tracker (fetched
via `gh` by the viability seat).** 48 CodeCarbon issues mention
`powermetrics`. Open on 2026-08-12: #1306 "Empty powermetrics output yields
NaN (not-a-number) power, poisoning all downstream totals on Apple Silicon"
(https://github.com/mlco2/codecarbon/issues/1306); #1313
"`ApplePowermetrics._setup_cli` silently succeeds on Intel Macs"
(https://github.com/mlco2/codecarbon/issues/1313); #1345 "reject unsupported
Macs and report 0 W when no samples"
(https://github.com/mlco2/codecarbon/issues/1345); #1397 (closed
2026-08-19) timed out the subprocess. The most-used tool's Apple backend is,
as of last month, still *failing open* — reporting a number when it should
report nothing — the exact failure class JouleWise's admission gate refuses.

**The mainstream Apple path chose to sidestep the boundary, not solve it.**
Zeus RFC #159 [33] picked IOReport counters read "at arbitrary times" and
rejected `powermetrics`; the resulting library warns its values are
model-based estimates and has 8 stars. Nobody has published whether
IOReport's counter update period reintroduces the same edge error. That is
an open question a JouleWise release could answer (record 21's recommended
cross-check, and Part II rank 10's diagnostic window).

### What a researcher elsewhere would need

1. **Portable instrument backends** behind one interface: `powermetrics`
   (done), IOReport (the Zeus interface [4]; the Phase 0 cross-check arm
   builds a reader), NVML power + energy counter (rebuilt from the
   provisional adapter, with the 1 s-averaging envelope), later RAPL. Each
   with its own pulse generator and its own sensor-response
   characterisation (Astra §3 step 3).
2. **A library API instead of a repo of scripts**: `measure(request,
   backend) → bundle`, `floor(cells) → bound`, `contrast(a, b, floor) →
   verdict | refusal`, with the pack/freeze objects as data classes.
3. **Documentation at the replication bar** — the paper's Appendix A is
   already written to it; the artifact guide (`docs/paper/artifact-guide.md`)
   covers governance, not use.
4. **An artifact badge and a DOI** (Zenodo is the archive that mints the
   DOI; a `CITATION.cff` is the machine-readable citation file GitHub and
   Zenodo recognise).
5. **Tests that a third party can run in minutes**, which means separating
   the ≈6 000-function suite into a portable core and the project's
   process tests, keeping the *mutation* harness (tests that plant a
   deliberate defect and check a test fails — "kill-tested") for floors and
   refusals.

### The cost, from both seats

Two independent ASSUMED estimates, both in seat-weeks (agent work directed
by one student), with the difference explained rather than averaged.

*The prospectus's estimate (five items):* backend interface + NVML backend
2–3; library API over the existing floor/contrast/custody code 2–3; docs
and examples 1–2; test split 1; artifact submission 1 → **≈7–10
seat-weeks**, Ed's share (review, the DOI, the submission) 6–10 Ed-hours.

*The viability seat's estimate (twelve items, §4):*

| # | Item | What "done" means | Weeks | Drop or keep |
|---|---|---|---|---|
| 1 | Backend abstraction | One `PowerSource` interface with `start()`, `stop()`, `records()` yielding timestamped interval-average power. Implementations: `powermetrics` (exists, 2,278 lines, 100 ms); IOReport (new; wrap zeus-apple-silicon, Apache-2.0 is MIT-compatible; no sudo); NVML energy counter + power polling (the 539-line `nvidia_smi` adapter is a start); RAPL powercap (new, Linux) | 3–4 | Keep; Apple + NVML first, RAPL last |
| 2 | Portable fiducial calibration | `joulewise calibrate` runs the pulse train on whichever accelerator the backend names (a 4096² fp16 matmul pulse exists for MLX; needs a CUDA twin), fits edges, caches the bound per machine with a date and an expiry | 2–3 | Keep; this is the differentiator |
| 3 | Library API, one entry point | `result = joulewise.measure(request_fn, phases=("prefill","decode"), n=5, design="ABBA")` returning gross J, phase J, the cell floor, the two-gate decision, and a refusal reason or None. Floor construction (`detection_floor.py`, corner enumeration, guard) already exists and is stdlib-only | 2 | Keep |
| 4 | CLI | `joulewise calibrate`, `joulewise measure --config`, `joulewise report`; the 13-subcommand governed CLI becomes the campaign layer | 1 | Keep, thinned |
| 5 | Docs at the replication bar | A 20-page user guide: install, calibrate, measure, read a refusal; the draft §2/§4 mechanism text already meets the first-use test and can be reused; README rewritten from status log to quick-start | 2–3 | Keep |
| 6 | Tests and mutation harness | Carve the ≈232 k-line test tree to the library surface; keep the defect-shaped regressions and the `replay-mutations.sh` pattern from the process traces so floors and refusals stay kill-tested | 1–2 | Keep, reduced |
| 7 | Artifact packaging | PyPI release, `CITATION.cff`, Zenodo DOI per release, GitHub release notes (JOSS, the Journal of Open Source Software, needs six months of that history — the clock starts at the first real release, not at the 2026-06-09 first commit) | 0.5 | Keep |
| 8 | Example dataset | One retained window: raw `powermetrics` plist, `events.jsonl`, calibration captures, fingerprint manifest — the 2026-07-22 diagnostic capture reconstructed in draft §2 is the obvious candidate | 0.5 | Keep |
| 9 | Licence | Stay MIT (already); dependencies Apache-2.0/BSD are compatible | 0 | Keep |
| 10 | Custody / campaign layer | Packs, freeze receipts, verdict binding, admission gates, ABBA scheduling | 0 (exists) | Ship as `joulewise.campaign`, off by default |
| 11 | Night-window machinery | launchd installer, the relaunch watchdog, magistrate docs, and the project's own scheduling internals (kernel events, refusal fast-retry) | 0 | **Drop from the tool**; JouleWise-specific operations |
| 12 | External-meter cross-check | Not required for release; record it as the known gap the field shares | 0 | Defer |

Total for the formal rewrite: **≈12–16 seat-weeks**. Smallest useful
release (items 3, 4, 5-lite, 7, 8 on the existing Apple backend): **≈2–3
seat-weeks**.

*Reconciled range:* **7–16 seat-weeks for the formal rewrite** — 7–10 if the
calibration stays Apple-only and the test tree is split rather than carved
(prospectus), 12–16 if the pulse calibration is ported to CUDA, the mutation
harness is carried over and an example window is packaged (viability seat);
**2–3 seat-weeks for Release 0** (viability seat); **1–2 seat-days for the
badge alone** (Fable draft Leg 2); **Ed 0.5 h** for the DOI in every case,
6–10 h in total across a full rewrite. The risk is not the weeks; it is
doing them before knowing whether the floor machinery is a general method or
an Apple-specific fit.

### Candidate venues (both seats, merged)

| venue | fits | what it wants | fetched facts (viability seat) |
|---|---|---|---|
| ICPE artifact-evaluation track | **tool paper / artifact**: the library, the backends, the artifact | Tool and data artifacts, ≤4 pages ACM format; badges Available / Functional / Reusable; "available from a permanent URL or DOI with an archival plan, such as the Zenodo repository"; README with hardware/software specs and "time estimates for the complete replication process"; *Results Validated* not claimable at submission | [47]; ICPE 2027 lists an Artifact Evaluation Track and a Data Challenge Track [48]; dates May 24–28 2027, Gothenburg (secondary: [49]); deadlines NEEDS-WEB |
| HotCarbon (workshop) | **measurement/instrument paper** (Paper F) | 5 pages incl. figures, double-blind, favours papers that "stimulate reflection and discussion"; no tools track named; [9],[12] are HotCarbon 2026 papers — the venue already publishes counter-mechanics work | [50]; 2026 deadline was 2026-05-18, held July 16–17 at UW; 2027 "to be announced" [51] |
| CarbonMetrics @ SIGMETRICS 2026 | instrument validation paper (F) or the tool | Explicitly lists "monitoring and benchmarking tools" and "validation of measurement tools for reproducible carbon accounting" | [52]; dates/page limit not on the page |
| ACM e-Energy (+ workshops) | measurement paper with artifact (Paper E), or F at a workshop; Wilkins' `powermetrics` study is e-Energy 2024 — the venue knows the instrument | Notes track ≤4 pages; four submission tracks | search snippet only; CFP page returned 403 twice — NEEDS-WEB [53] |
| MLSys (+ workshop) | tool/benchmark paper; practitioners; the placement rule and the library | 10 pages; topics include "Machine learning benchmarks, datasets, and tooling"; voluntary artifact evaluation "following the ACM Artifact Review and Badging policy" | [54]; 2026 deadline was 2025-10-30 |
| JOSS (Journal of Open Source Software; a software paper) | the library, once it has a public life | OSI licence, "feature-complete", comprehensive docs and tests, evidence of research impact, "at least six months of public history prior to submission, with evidence of releases, public issues/pull requests"; rejects "minor utility" and thin wrappers; public GitHub review | [55] |

**What an ACM badge requires** (ACM page returned 403; text from the SIGIR
mirror [56]): *Artifacts Evaluated – Functional*: "documented, consistent,
complete, exercisable, and include appropriate evidence of verification and
validation." *Reusable*: additionally "very carefully documented and
well-structured to the extent that reuse and repurposing are facilitated."
*Available*: "permanently available for retrieval" (a DOI). *Results
Reproduced*: main results obtained by a team other than the authors using
the authors' artifacts. *Results Replicated*: without author artifacts.
Zenodo mints a DOI per GitHub release once the repo is public, licensed and
toggled on in Zenodo's GitHub settings [57]. JouleWise today would qualify
for Available (public, MIT) and plausibly Functional for the *code*; Results
Reproduced is blocked by the floor-binding limitation until FLOOR-BIND-01
closes. A tool paper without cross-vendor evidence is a Mac tool paper;
ICPE's track will ask what the second backend showed.

### The decision rule — one rule, both seats' conditions

**Release 0 — unconditional, now.** Ship a pip package `joulewise` that does
only what already works: the Apple `powermetrics` backend at 100 ms,
`calibrate` from the existing pulse train, `measure` returning gross + phase
energy + cell floor + refusal, with a Zenodo DOI, `CITATION.cff` and one
example window, published as Paper B's artifact at the ACM *Available* +
*Functional* level. Cost 2–3 seat-weeks of mostly agent work (1–2 seat-days
if only the badge is taken), Ed 0.5 h. It needs no new science, it converts
the existing code into an artifact reviewers can run, it is the badge a
metrology reviewer looks for, and it starts JOSS's six-month clock. The
seat work starts after day 3 so it never competes with Paper B's desk day.

**Release 1 — the formal rewrite — is gated twice.**

*Start* Release 1 only when **all** of the following hold:

- (a) **Paper D's core is data-complete** (day 17). The prospectus's
  condition was Paper C (day 10, so the Mac science is never delayed); the
  viability seat's was Paper D, because a rewrite before then competes
  with the only windows that can produce claim-bearing numbers. The later
  date subsumes the earlier one and is adopted; seat-side design work may
  begin at day 10.
- (b) **The meter mapping has an interval** (Part II rank 3), so the tool
  can state its scale's traceability.
- (c) **At least one flip signal toward "sooner" has fired:** (c1) the
  IOReport cross-check (record 21's top recommendation; Part II rank 10)
  shows IOReport counters carry the same ~100 ms edge error — then the
  pulse calibration is needed on the no-sudo path too and the tool has no
  substitute; (c2) an NVML pulse-train pilot on the 3080 Ti (or the cloud
  card, if the rig inventory sends the program there) reproduces a finite
  edge bound of ≥20 ms through the same pulse → anchor code path — then the
  method is demonstrably portable; (c3) any external group asks for the
  package after Release 0.
- (d) **Neither stop signal has fired:** (d1) the `_v5` attribution-dominance
  test returns a null in both phases (the floor is still useful, but the
  calibration is then a 6-minute ritual that changes no decision and the
  pitch shrinks to "floors and refusals") *and* (d2) IOReport at arbitrary
  instants shows edge error well under the floor (zeus-apple-silicon already
  sidesteps the boundary for free) — both together stop it; or (d3) six
  months after Release 0 there are zero external issues, forks or
  citations.

*Ship* Release 1 only when the cross-vendor floor re-derivation has actually
worked: a floor minted on an NVIDIA card by the same pulse → anchor →
corner-enumeration → two-gate path, with its own sensor characterisation,
producing at least one resolvable contrast and at least one printed refusal
(H2–H3 in the week ladder). If that fails — NVML's averaging leaves every
phase unresolved — the honest product is a **methods artifact** (the Mac
tool, badged, with the recipe for porting) and a Paper F, not a general
library. If it succeeds, the library is the Paper E artifact and the
rewrite pays for itself at submission. If the record is silent on (c) and
(d), wait for the six-month JOSS clock and decide on external signal alone.

**What Ed should tell the advisor in one breath:** the field's tools read
counters inside a window and hand back a number with no bound; JouleWise is
the only one that says how large a false difference the setup can
manufacture and refuses when the answer is "bigger than what you saw." That
part is portable and wanted; the night-window custody that surrounds it is
not, and should stay a campaign layer.

### Release 0, concretely (viability seat §5.1)

The smallest release that is still useful is the one a reviewer of Paper B
can run in fifteen minutes on their own Apple laptop. Its public surface is
four calls; everything else stays importable but undocumented.

```python
import joulewise as jw

cal = jw.calibrate()                 # ~6 min: 3 warm-up + 59 one-second GPU pulses, twice; caches the
                                     # edge bound (s) with a date; refuses on active NTP or a hot machine
res = jw.measure(run_request,        # any callable that emits jw.phase("prefill") / jw.phase("decode")
                 n=5, design="ABBA", calibration=cal)
print(res.gross_j, res.prefill_j, res.decode_j)   # point values with intervals
print(res.floor_j, res.decision)    # e.g. 3.05 J, "not resolvable: |Δ|=1.1 J < floor 3.05 J"
res.save("window-2026-09-19/")      # raw plist, events.jsonl, calibration captures, sha256 manifest
```

What ships with it: the `powermetrics` backend at 100 ms (existing),
`detection_floor.py` and the two gates (existing, stdlib-only), the pulse
train and clock anchor (existing, `powermetrics_fiducial.py`, `clock.py`), a
20-page guide reusing draft §2 and §4 prose, one retained example window,
`CITATION.cff`, a Zenodo DOI, PyPI 0.1.0. What it refuses: anything but
Apple silicon with passwordless `sudo -n powermetrics`; that limitation is
printed, not hidden.

What it deliberately does not ship: packs, freeze receipts, the ABBA night
scheduler, launchd agents, the watchdog, cold gates (reviews by a fresh
session with no loop context). Those become
`joulewise.campaign` in Release 1 or stay in this repository as the paper's
custody layer.

Risks worth naming before committing two weeks. First, the floor-binding
limitation (draft §9) means Release 0's floor is computed in-process from
the user's own window, not bound to a governed (custody-ruled) extraction; that is fine for
a library user and must be stated as such, or a reviewer will read the
paper's custody claims into the package. Second, `powermetrics` needs root,
and the CodeCarbon tracker shows that path failing open on other people's
Macs in August 2026; Release 0 must fail closed with a readable message on
Intel Macs, missing sudo, and empty output — the admission-gate code already
does this and just needs to be on the import path. Third, a 6-minute
calibration is a real adoption tax; caching per machine with an expiry is
the mitigation, and the IOReport cross-check decides whether a no-sudo path
can ever skip it.

---

## Part V — Recommended progression

One sequence, each step with its reason:

1. **Days 1–3, Paper B as planned** (plan Phase 0), with the meter desk arm
   on the day-2 desk day *after* the magistrate's A214 ruling (Part II
   rank 3). Reason: the grade; and the ruling costs nothing while the meter
   is in transit.
2. **Day 2 desk: the two Leg 2 desk items** (warm-up rule, fixed-n
   paragraph) into Paper B's protocol section. Reason: zero windows, two
   reviewer questions closed.
3. **Days 4–10, Paper C as planned**, protecting in this order if windows
   are lost: the 30B-A3B/122B floors → shape grid + held-out → variance
   windows 15–16 → the 8-bit cell → KV growth → sentinel → categories.
   Reason: the coefficients feed every Paper D law; the variance result is
   Ed's axis and costs two windows. **In parallel, seat work, zero windows:
   Release 0** (Part IV) — the pip package, example window, `CITATION.cff`;
   the DOI is minted when Paper B is submitted. Reason: it is agent work
   that competes with nothing, and it starts the JOSS clock.
4. **Days 11–17, Paper D core: bytes law first** (Phase 2 windows 1–5), then
   crossover + chunk, then mixers if the NEEDS-WEB runtimes check out.
   Reason: rank 1 in Part II; it is the "why" behind every other axis.
5. **Days 18–23, Paper D full set**, with EPCA (energy-per-correct-answer)
   levels last because it waits
   on the AP-5 policy ruling — file that ruling request now so it is not the
   blocker on day 18.
6. **Days 24–30 (H1): meter ladder + the two Apple instrument windows +
   NVIDIA sensor characterisation** on the platform the inventory picks.
   Reason: closes the field's first question and seeds Paper F; the NVIDIA
   characterisation (the pulse pilot, flip signal c2) and the IOReport
   cross-check (c1) are the go/no-go for Release 1.
7. **Days 31–37 (H2): whole-request placement on the owned card at native
   recipes; one matched-BF16 1.7B pair.** Reason: the placement study is
   Ed's original question on hardware he owns.
8. **Days 38–44 (H3): cloud 12-window tier, ≈$115–150.** Reason: the only
   place 8B BF16 matching, 30B-A3B vs 32B and the scaling roster's upper
   rungs exist.
9. **Days 45–51 (H4): KV-cache surface on the cloud card if the bytes law
   stood; split rider only if already cabled.** Then writing: F to a
   workshop, E to a venue; the Release 1 decision by the Part IV rule.

### What Ed must do physically, and when

| when | action | hours |
|---|---|---|
| ≈17:00 PDT Wed 2026-09-17 (ASSUMED arrival) | plug the KM003C between adapter and Mac; confirm the adapter out-rates the laptop's peak (140 W ASSUMED vs <100 W ASSUMED); turn optimized battery charging off (setting NEEDS-WEB on this build); leave the logger decision to the desk arm's measurement | 0.25 |
| at Paper B submission | Zenodo account; confirm the Release 0 DOI | 0.5 |
| before H1 (any evening) | rig inventory: OS, driver, `nvidia-smi -q` telemetry fields, whether the energy counter reads on this GeForce, SSH from the Mac — read-only | 1–2, up to 4–8 if it becomes the setup evening |
| H3 | cloud account and payment; pick a *dedicated single-GPU* instance (reject shared slices and MIG, NVIDIA's partitioning of one GPU into independently rented slices) | 0.5–4 |
| H4, optional | Ethernet adapter + cable for the split rider; the friend's 5080 session if one falls free | 1 + (0–4) |
| always | never run an interactive session on the measured Mac during a window (the census refuses; the Sept 13 and 15 refusals were exactly this) | 0 |

### What would change the order

1. **The equivalence night FAILs or is INCONCLUSIVE** (plan window 0.2: the
   night-one check of twelve timing captures against the last accepted
   calibration envelope, which decides whether the calibration is in force
   on this OS build): everything slides ≥1–2 days; nothing reorders.
2. **The IOReport cross-check disagrees with `powermetrics` by more than
   the cell floor**: Phase 1 stops; the instrument question becomes Paper
   B's limitation and Paper F's headline — and the meter ladder moves up
   to be the tie-breaker (a third read path).
3. **The A214 ruling adopts "gain"**: the meter still runs, but the paper
   sentence must not multiply phase energies by the slope; if the ruling
   goes Astra's way (recommended), nothing else changes.
4. **The rig inventory finds Windows, or GA102 gives only 1 s-averaged
   power with no energy counter**: cloud becomes primary (Astra's order),
   the rig a request-total-only third point, and the Release 1 ship gate
   is tested on the cloud card.
5. **The bytes law fails on the Mac** (sparse points off the line beyond
   the bar): that is a result — the resident-bytes term exists — and the
   cross-vendor transport (Part III rank 4) becomes *more* interesting, not
   less; the KV surface in H4 yields to a second bytes-law leg with router
   statistics (the MoE router's per-token expert choices).
6. **Ed's time shrinks**: drop in this order — 5080, split rider, cloud
   tier, rig. The meter, the desk items, Release 0 and every Apple window
   survive any cut, because they cost Ed almost nothing.
7. **A cloud reference spread exceeds the floor in two consecutive
   windows**: change instance type or provider before a third (the
   standing two-failures rule, Fable draft §"What would change" 4).

---

## Fidelity spot-check (editor seat, 2026-09-16, read-only at `dc119f7d`)

| number | where it is used | source found |
|---|---|---|
| σ = 0.241 J, n = 10, 146.730349 J | Part II Axis 4 | `CLAIMS_STATUS.md` line 117 (labelled DIAGNOSTIC there) |
| ≈1 J attribution scale, ≈5 J effective bar | Part 0 | `CLAIMS_STATUS.md` lines 106–110; D-078 clause 11 at `docs/decision_log.md` line 4745 ("±31 ms … ~33 W mis-attributes ~1 J") |
| 30.07 ms capture bound | Part 0, Part IV | `docs/paper/draft-v1.md` line 79 (0.030067931757111657 s) |
| 0.29 / 0.49 / 0.31 J vs 3.15 / 2.92 / 2.18 J | Part 0, Axis 4 | `draft-v1.md` line 103 (0.2888, 0.4934, 0.3113; 3.153, 2.922, 2.184; ratios 10.92, 5.92, 7.02) |
| 16.4 GB / 8.2 GB / 4.1 GB; ≈4.6 GB; 15.27 GiB | Axis 2, Part III | Astra draft line 213 (table) and 234; Fable draft lines 224–225 |
| $115–150 and $263–343 | Part III | Astra draft lines 397 ($115.15–$150.15) and 405 ($263.20–$343.20); Fable's $40–130 at lines 304–305 |
| day 3 / 10 / 17 / 23 | throughout | plan lines 97, 129, 160, 165–168 |
| 12 GB / 16 GB / 80 GB | Part III | Fable draft lines 211–213, 221; Astra draft lines 238 (NVIDIA product pages), 242–244 |
| star counts (4,635 … 8; sum 11,643) | Part IV | viability seat Table 1b and §1.1, GitHub API fetch 2026-09-16; not re-fetched here |
| test count | Part IV | **the brief's "6240" is UNSOURCED (ASSUMED)**: grep at `dc119f7d` counts 5,971 `def test_` functions in 231 `test_*.py` files (249 `.py` files under `tests/`); the prospectus's "≈6 000" is consistent with the grep, 6240 is not, and no pytest collection was run (no pytest in the read-only interpreter) |
| ≈130 k lines, 231 test files, ≈110 scripts, ≈3,600 `.md` | Part IV | `wc -l` 129,593 over 100 `.py` files in `joulewise/`; `find` 231 / 110 / 3,600 (v1's "113 scripts" and the viability seat's "503 `.py` files, 3,550 `.md`" were not reproduced and are replaced by today's counts) |
| 9.724 ms drift screen | Table 1a | `draft-v1.md` line 51 |
| 147 KB/token, 603,979,776 and 1,207,959,552 bytes | Axis 2, Part III | Astra draft line 232 (from the official `config.json`) |
| PC-4 ≈23–28 W | Axis 1 | bank line 1608 |
| 10 mJ and 2.4 mJ per token | Part 0 | arithmetic from the 5 J bar (5/512, 5/2048); v1 cited "bank line ≈1615", which carries different per-token figures, so the citation is replaced by the arithmetic |
| `wall_meter: AC wall power (full system)` | Part II | `docs/decision_log.md` line 1073 |
| lane A214 / row E214 wording | Part II | `TASK_QUEUE.md` line 670 |

---

**Magistrate note on the test count (added at landing).** The "6240 tests" figure is the runtime count of the 2026-09-16 integration replay (`docs/process_traces/2026-09-15-interactive-b0ae8462/26a-integration-replay-881a8d6b.txt`: 239 modules, 6240 tests, 0 failures), which includes dynamically generated cases; the 5,971 static `def test_` functions counted above are the source-level figure. Both are correct for what they count.

## Sources

[1]–[20] are record 21 §4
(`docs/process_traces/2026-09-15-interactive-b0ae8462/21-rq-literature-and-best-practices-fable.md`);
[21]–[31] are the Fable horizon draft's §Sources
(the session scratchpad’s Fable horizon draft (reconciled into `docs/process/research_plan_horizon_2026-09-16.md`)). Astra's additional primary
pages (NVML device queries, the Qwen3 model cards and `config.json`, the
NVIDIA WSL guide, vLLM installation, the ChargerLAB logging page, the RTX
3080 Ti / 5080 product pages, Lambda pricing) are linked inline in
the session scratchpad’s Astra horizon consult (same reconciliation) and are not renumbered here.

[32]–[57] were fetched by the viability seat on 2026-09-16
(the session scratchpad’s tool-viability report (its fetched facts are reproduced in Part IV) §Fetch log):

- [32] Zeus measure page — https://ml.energy/zeus/measure/
- [33] Zeus Apple-silicon RFC #159 — https://github.com/ml-energy/zeus/issues/159
- [34] zeus-apple-silicon — https://github.com/ml-energy/zeus-apple-silicon
- [35] CodeCarbon methodology — https://docs.codecarbon.io/latest/explanation/methodology
- [36] ML.ENERGY Benchmark (also [3]) — https://arxiv.org/abs/2505.06371
- [37] Optimum-Benchmark energy tracker source — https://raw.githubusercontent.com/huggingface/optimum-benchmark/main/optimum_benchmark/trackers/energy.py
- [38] MLPerf inference datacenter benchmarks (rules also [1], https://arxiv.org/abs/2410.12032) — https://mlcommons.org/benchmarks/inference-datacenter/
- [39] Scaphandre per-process power explanation — https://hubblo-org.github.io/scaphandre-documentation/explanations/how-scaph-computes-per-process-power-consumption.html
- [40] pyJoules documentation — https://pyjoules.readthedocs.io/en/latest/
- [41] nvidia-ml-py on PyPI — https://pypi.org/project/nvidia-ml-py/
- [42] TokenPowerBench (AAAI 2026) — https://arxiv.org/abs/2512.03024
- [43] macmon — https://github.com/vladkens/macmon
- [44] asitop — https://github.com/tlkh/asitop
- [45] Zeus in the PyTorch ecosystem — https://pytorch.org/blog/zeus/
- [46] CodeCarbon issue #1350, `codecarbon doctor` — https://github.com/mlco2/codecarbon/issues/1350 (issues #1306, #1313, #1345, #1397 are at the same tracker, fetched via `gh`)
- [47] ICPE 2026 artifact-evaluation track — https://icpe2026.spec.org/tracks-and-submissions/artifact-evaluation-track/
- [48] ICPE 2027 home — https://icpe2027.spec.org/
- [49] ICPE 2027 call (secondary) — https://callforpaper.org/cfp/call-for-papers-icpe-2027
- [50] HotCarbon CFP — https://hotcarbon.org/cfp
- [51] HotCarbon home — https://hotcarbon.org/
- [52] CarbonMetrics @ SIGMETRICS 2026 — https://noman-bashir.github.io/CarbonMetrics/
- [53] ACM e-Energy 2026 CFP (403 on fetch; NEEDS-WEB) — https://energy.acm.org/conferences/eenergy/2026/pages/cfp.php
- [54] MLSys 2026 call for papers — https://mlsys.org/Conferences/2026/CallForPapers
- [55] JOSS about — https://joss.theoj.org/about
- [56] ACM artifact badging text (SIGIR mirror; the ACM page returned 403) — https://sigir.org/general-information/acm-sigir-artifact-badging/
- [57] GitHub docs, referencing and citing content (Zenodo DOI per release) — https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content

Failed fetches recorded by the viability seat: `mlco2.github.io/codecarbon/methodology.html` (301 → `docs.codecarbon.io/methodology.html` 404; the `/latest/explanation/methodology` path worked), the ACM badging page (403; SIGIR mirror used), `hotcarbon.org/2026/` (404; `/cfp` used), e-Energy 2026 root and CFP (403 both; Notes ≤4 pages is from a search snippet), ICPE 2027 deadlines (not on the site). Nothing in this prospectus was fetched fresh by the editor seat; every unverified fact is marked NEEDS-WEB or ASSUMED at its use.
