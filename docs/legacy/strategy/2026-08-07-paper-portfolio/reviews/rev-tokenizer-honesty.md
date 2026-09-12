# Counter-review: "A Token Is Not a Unit: Tokenizer-Honest Energy Reporting for Local LLM Inference"

Reviewer: Opus 5, counter-review lens (contract + prior-art + existing-material).
Target: `scratchpad/portfolio/prop-tokenizer-honesty.md`
Ground truth: repo at `scratchpad/desk`, HEAD `89f28bf`; D-117 at `docs/decision_log.md:7507`;
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`.

**VERDICT: WEAK.** Not a kill on honesty — the proposal is unusually careful about what it
refuses to claim, and every load-bearing feasibility assertion I checked is *true*. It is a kill
on **paper-hood**. This is a correct, cheap, ~1.5-page section of the MVP paper that has been
inflated into a standalone paper by borrowing the MVP paper's three windows wholesale and
attaching a desk exercise whose headline result was published at 100× the scale in 2023.

**Scores** — novelty 2, feasibility 9, mvp_leverage 5, venue_fit 3, original_goals 5.

---

## What I verified (the proposal's factual base is mostly sound)

Credit where due. I checked the proposal's concrete assertions rather than taking them:

| Assertion | Verdict |
|---|---|
| Qwen2.5-1.5B and 7B tokenizer artifacts are byte-identical | **TRUE.** Both `tokenizer.json` sha256 `a8506e7111b80c6d8635951a02eab0f4e1a8e4e5772da83846579e97b16f61bf` (`~/jw_models/mlx-community/`) |
| Qwen2.5, Qwen3, OLMo tokenizer artifacts "already present locally" | **TRUE.** `~/jw_models/` holds Qwen2.5-{0.5,1.5,7}B, Qwen3-4B, Qwen3.5-122B, OLMo-1B-0724-hf, OLMoE-1B-7B-0924 |
| 141 J historical decode contrast, non-claim | **TRUE.** `CLAIMS_STATUS.md:63` — `phase_energy_j.decode` 7B−1.5B = 141.29 J, re-scoped DIAGNOSTIC by D-117 |
| 128-token prefill contrast ≈ 5.81 J, marginal | **TRUE.** Ten block deltas 5.645–6.008 J, `docs/process_traces/2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:173` |
| D-117 budgets 3.14 / 3.24 / 2.80 h | **TRUE.** DESIGN-MEMO:327 |
| Prefill rider adds no member, no runtime | **TRUE.** DESIGN-MEMO:261 |
| Outputs retained for cross-tokenization | **TRUE.** `response_text` is a bundle field, `docs/contracts/run_bundle_layout.md:401` |
| No frozen-boundary violation | **TRUE.** All three new capabilities are desk reducers; inference execution untouched |

So the proposal is not fantasy. That makes the following objections harder, not easier — they are
objections to what the work *is*, not to whether it can be done.

---

## FATAL FLAWS

### F1. It is not an energy paper. The proposal itself proves this.
The charge asked whether the paper needs *any* new windows. The proposal answers, in bold:
"This paper needs **no additional quiet night beyond those three**." Those three are the MVP
paper's windows. Subtract the MVP paper and what remains is: token counts on parallel text,
computed at a desk, in an afternoon, with zero joules.

The tell is Contribution 2. Strip the LaTeX and it reads: for any positive reals,
`((E_A/T_A)/(E_B/T_B)) / (E_A/E_B) = T_B/T_A`. That is an identity. It holds for every E and
every T. It cannot be falsified by any experiment, on any instrument, on any hardware. Listing an
algebraic tautology as a numbered falsifiable contribution is a category error, and a metrology
advisor who co-authored JouleSort will name it in the first paragraph of her feedback.

The paper's whole causal step — from "token counts differ" to "reported *energy* comparisons
distort" — is made by that identity, never by measurement. Everything downstream is arithmetic on
someone else's joules.

### F2. Direct-hit prior art, entirely unacknowledged.
Contribution 1 is "a measured denominator-distortion distribution": ~200 FLORES parallel sentences
× 6–8 languages × 3 tokenizers. This is a strict *subset* of published work:

- **Petrov, La Malfa, Torr, Bibi, "Language Model Tokenizers Introduce Unfairness Between
  Languages," NeurIPS 2023** — tokenization lengths over **2000 FLORES-200 sentences**, ~17
  tokenizers, disparities **up to 15×**, framed explicitly as cost, latency, and context
  unfairness. They ship `tokenization_lengths.csv` publicly. The proposal's entire Contribution 1
  is a row-and-column slice of a released dataset.
- **Ahia, Kumar, Gonen, Kasai, Mortensen, Smith, Tsvetkov, "Do All Languages Cost the Same?
  Tokenization in the Era of Commercial Language Models," EMNLP 2023** — FLORES-based, up to 5×
  token inflation, and the *identical* argumentative move: the token is a billing denominator, so
  denominator disparity distorts the reported cost of the same content.

The proposal contains **zero** related-work positioning against tokenizer-fertility literature.
Not a hedge, not a citation, not a "we differ in that…". For a paper whose entire headline is that
literature's flagship result, this is not an omission — it is the review.

The only available differentiator is substituting **joules for dollars**. Per F1, the proposal
never measures that substitution. So the delta over Petrov 2023 is: a unit relabel, asserted.

### F3. The project's own contrast is a negative control *by construction* — the proposal admits it and moves on.
Contribution 3 offers gamma (1.5B vs 7B decode) as "a calibrated same-tokenizer control." I
verified the tokenizers are byte-identical. Correct — and devastating. The paper's **only**
calibrated energy evidence is, by design, evidence in which the pitfall it is about **cannot
occur**. A paper about a hazard whose measured content is guaranteed hazard-free is a paper whose
measured content is decorative.

Worse: gamma is already the MVP paper's headline result. Contribution 3 is the MVP paper's
demonstration study, relabelled as a control.

### F4. The tokenizer roster is inflated 3→2. I measured it.
The proposal names "three exact artifacts already present locally—Qwen2.5, Qwen3, and OLMo."
Byte-distinct, yes. Behaviorally distinct, no. I loaded all four local `tokenizer.json` files and
tokenized ten matched parallel sentences (nine scripts), same semantic content:

```
lang    chars  bytes  Qwen2.5  Qwen3   OLMo  OLMoE   OLMo/Q2.5  Q3/Q2.5
eng       168    168       28     28     28     28        1.00     1.00
spa       183    193       45     45     54     54        1.20     1.00
deu       174    176       47     47     58     58        1.23     1.00
zho        41    123       23     23     59     59        2.57     1.00
jpn        69    207       44     44     75     75        1.70     1.00
ara       133    244       46     46     90     90        1.96     1.00
hin       131    339      121    121    130    130        1.07     1.00
kor        67    167       45     45    116    116        2.58     1.00
rus       165    303       54     54     82     82        1.52     1.00
tha       118    352       52     52    131    131        2.52     1.00
```

Vocab: Qwen2.5 151665, Qwen3 151669 (four added specials), OLMo/OLMoE 50280.

**Qwen3/Qwen2.5 = 1.00 on every language, every script.** Same merges. And OLMo-1B ≡ OLMoE-1B-7B
(`tokenizer.json` sha256 `a094266ac6c4982efba277bc251349a5a6d6ad37efb39a2a90f53d8be2a40a40` for
both). The proposal's three-tokenizer audit is an **N=2** comparison — Qwen-family vs
GPT-NeoX-family — dressed as three. Contribution 1's "distribution" is one ratio with two
endpoints. A reviewer who runs the check I just ran (fifteen minutes, no hardware) finds this.

### F5. On the paper's own measured corpus the effect is exactly zero.
The proposal's second desk leg is "cross-tokenize the exact prompts and retained outputs from the
three D-117 windows." I pulled the actual window config
(`configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/…-b04-a1.json`):
workload profile `df_ph_decode`, `prompt_tokens: 128`, `output_tokens: 512` — synthetic English.
Row 1 of my table: **OLMo/Qwen2.5 = 1.00 on English.** Cross-tokenizing the D-117 corpus is
guaranteed to produce nothing. The one place the paper touches its own measured data with its own
new method, the method returns the null by construction.

### F6. The kill criteria cannot fire; they are pre-registration theatre.
Stated kill: "less than 5% distortion throughout." Already falsified by the table above (1.07–2.58,
i.e. +7% to +158%) before a single FLORES sentence is downloaded. Stated headline threshold:
"median absolute distortion ≥10% in two scripts or 95th percentile >20%." Guaranteed to pass —
Petrov published up to 15×.

This project's whole moral authority rests on gates that can actually refuse (D-117, the two claim
gates, the refusal log as evidence). Importing that vocabulary onto a threshold whose answer is
already public inverts it. This is the single most damaging thing in the proposal *for the
project*, because it teaches the reader that JouleWise pre-registration is decorative.

### F7. The one quantitative diagnostic offered is uncorroborated and computed on a caricature.
"Across eight existing 512-Qwen-token multilingual controls, OLMo produces 4,540 tokens versus
Qwen2.5's 4,096, or +10.8%. The widest item is 722 versus 512 (+41.0%), while another is 459 versus
512 (−10.4%)." I grepped the repo for `4,540` / `4540` / these ratios: **nothing**. The numbers
have no tracked provenance.

They are also computed on `jw.multiling` synthetic sentinel text
(`joulewise/gensuite/__init__.py:1059,1250`) — programmatically generated function-word blocks with
script-appropriate punctuation. That is a caricature of language. Two consequences: (a) +10.8% is
about an order of magnitude below real matched-text dispersion (my measured 1.07–2.58); (b) the
reported **−10.4% sign reversal** (OLMo producing *fewer* tokens than Qwen) is an artifact of
repeated function words hitting NeoX merges, and does not occur on any of my ten real sentences.
The proposal's "ranking hazard" framing leans on exactly that sign reversal. Its only support is a
generator artifact.

### F8. FLORES is not acquired. The proposal writes as if a session that hasn't happened, has.
`docs/campaign_packs/c5_i_3_flores_fertility.md` header: **"Status: pre-source-session DRAFT."**
Unresolved placeholders: `FLORES_REVISION`, `FLORES_LICENSE`, `ARCHIVE_SHA256`, `SUBSET_ID`,
`LANGUAGE_IDS`, `PAIR_IDS`, `TOKEN_MATCHED_METHOD`, and the 6-vs-8 language count **deferred by
D-046/B6**. The proposal says "the source session's prospectively chosen six or eight FLORES
languages/scripts" — there is no such choice on record. It is a named prerequisite session, unrun,
that the proposal has quietly converted into a completed input.

### F9. Salami-slice risk against P2 (ICPE), which the proposal concedes and then ignores.
It states it reuses draft-v1 §§3–5 "almost intact," reuses the same three windows' results, and is
"not, by itself, enough for an ICPE full-track claim." Under Ed's paper-first stack (P1 MVP, P2
ICPE), that is a P1-schedule desk cost with no P2 payoff, plus a live dual-publication hazard: two
papers, shared method sections, identical results tables. An ICPE PC checks for exactly this.

Also, §§3–5 are **not currently clean for reuse**: the paper-fidelity audit at HEAD
(`docs/process_traces/2026-08-07-night-hardening/AUDIT-PAPER-FIDELITY.md`) found draft-v1 §3 claims
trapezoidal integration while the reducer performs overlap-weighted interval averaging (HEAD commit
message: "paper needs interval-average (not trapezoidal) correction … before advisor review").
Minor, but "reuse §§3–5 intact" is currently false.

---

## Non-fatal: what is already project doctrine, presented as new

Contribution 4 ("a mechanically checkable reporting rule") is largely **ratified JouleWise contract
since 2026-07-09**. `docs/contracts/token_normalization.md` already binds: gross request energy is
PRIMARY; J/token is "tokenizer-scoped companion" and "never a tokenizer-blind work unit";
runtime-observed denominators; tokenizer name/revision/class/vocab named wherever a per-token
number appears; co-display at equal-or-greater salience (D-033/D-037/D-052/D-053). The FLORES pack
already **pins now**: "Required companion denominators: J/char, J/byte, and semantic-pair IDs" and
the ceiling "no tokenizer efficiency ranking without semantic and token-matched legs."

And `docs/paper/draft-v1.md:11` — the MVP paper's *scope statement* — already reads: "Joules per
prompt or output token are tokenizer-scoped companion metrics and are never treated as
tokenizer-independent work units."

The paper's central normative claim is already in the MVP paper. The proposal's own token-matched
control leg is a pack requirement, presented as a design choice. What is genuinely new in
Contribution 4 is only *mechanical enforcement* — which is a tool, not a finding.

---

## Scores, with reasoning

**Novelty — 2/10.** Contribution 1 is a subset of Petrov 2023's released dataset. Contribution 2 is
an identity. Contribution 3 is the MVP paper's result relabelled. Contribution 4 is the project's
own 2026-07-09 contract plus a linter. The two points are for the linter and for the honesty of the
"forbid the causal sentence" fence, which is genuinely good discipline.

**Feasibility — 9/10.** The highest score in this portfolio, and deservedly. Zero incremental
nights. Tokenizer artifacts verified present. `response_text` retained. No frozen-boundary
violation. Only real risk is F8 (FLORES acquisition), and Petrov's published length tables are a
fallback. Docked one point because the desk stream (auditor + reducer + validator) lands squarely
on the P1 critical path, which is currently the D-117 desk freeze — window plans, generalized mint
pinsets, extraction specs, synthetic integration regression. Not free.

**MVP leverage — 5/10.** Bimodal. As **§7 of the MVP paper**: 8 — it costs nothing, it sharpens the
existing scope statement into a measured one, and it makes the shared-tokenizer gamma contrast look
deliberate rather than lucky. As a **separate paper**: 3 — it leverages the MVP by *duplicating*
it, and creates F9. Averaged, 5. The proposal itself writes "Section 7 becomes a tokenizer-honesty
evaluation," which is the correct instinct pointing at the wrong deliverable.

**Venue fit — 3/10.** Capstone chapter: fine. EuroMLSys / HotCarbon / ICPE-WiP: the Petrov+Ahia
collision is disqualifying for the headline as written; the first reviewer question is "what is new
beyond Petrov 2023?" and the honest answer is "we relabel dollars as joules but do not measure it."
HotCarbon additionally wants a carbon argument this does not make. ICPE full track: disclaimed by
the proposal.

**Original goals — 5/10.** Genuinely serves the **energy-honest leaderboard/reporting critique**,
which is a real Ed axis, and the normalization discipline is a true prerequisite for later
mechanism work. Serves **zero** mechanism axes — no spec decode, no MTP, no MoE routing, no
KV/attention, no split inference. The proposal says so plainly, which earns it points for honesty
and costs it points on the axis.

---

## Three strengthening moves, if kept

### M1 — Buy the paper an actual measurement: the ranking flip, on one added night.
This is the move that converts a tokenization note into an energy paper, and it is available on
**owned hardware with already-proven harness support**.

Add a fourth window: matched-content decode contrast, **Qwen2.5-1.5B vs OLMo-1B / OLMoE-1B-7B**, on
a frozen non-Latin-script prompt set (Korean, Chinese, Thai — my table shows 2.5×+ OLMo inflation
there), budgeted by **characters or bytes, not tokens**, with gross J/request primary. Then show,
with real joules and both claim gates, that **J/output-token ranks the two stacks in one direction
while J/request-for-identical-semantic-content ranks them in the other.** That is a measured
ranking flip. It is the thing Petrov could not do and Ahia approximated with API prices.

Feasibility is not speculative: OLMoE-1B-7B has already run on this harness
(`docs/process_traces/2026-07-17-exploratory-block/results.md`, three reps, 229.028 ± 2.445 J), and
the exploratory OLMoE-vs-Qwen3-4B gross gap was **133.720 J — 5.43× the guard then, ~27× the 5 J
bar**. Effects are enormous; sizing is not the risk.

The confound is real and must be owned in the title, not buried: OLMoE is BF16, Qwen is INT4;
architectures differ. So the estimand is **"as-shipped stacks," not "tokenizer holding model
fixed"** — which is precisely the unit a leaderboard reports, and therefore precisely the unit whose
distortion matters. State that the study identifies *reporting* distortion between deployable
stacks and explicitly does not decompose tokenizer from architecture. Now the kill criterion is
real: if no script exhibits a flip region, the paper refuses, and the refusal is a result.

Cost: one added quiet night (~2.5–3 h) + a matched-content-budget workload generator. Verify first
whether an INT4 OLMo conversion is available to reduce the quantization confound.

### M2 — Fix the roster, retire the synthetic corpus, drop the D-117 cross-tokenization leg.
(a) Three artifacts is two tokenizers — Qwen3 ≡ Qwen2.5 (measured 1.00 across nine scripts) and
OLMo-1B ≡ OLMoE. Either add genuinely distinct locally-obtainable tokenizers (Llama-3 128k,
Gemma 256k, Mistral 32k, plus a byte-level control) or state N=2 and shrink the claim accordingly.
(b) Delete the `jw.multiling` synthetic diagnostic from the evidence base. It understates real
dispersion by ~an order of magnitude and manufactures the −10.4% sign reversal the "ranking hazard"
framing leans on. Replace with real matched text.
(c) Drop the "cross-tokenize the D-117 prompts and outputs" leg entirely. English, ratio 1.00,
guaranteed null. Spending desk time on it and reporting the null as a finding would be worse than
not doing it.
(d) Add the related-work paragraph the proposal has no version of, leading with Petrov NeurIPS 2023
and Ahia EMNLP 2023, and stating the delta in one sentence you are willing to defend.

### M3 — If M1 is not funded, demote to §7 + ship the validator as the artifact.
Do not write this as a standalone paper. Land it as MVP §7 (~1.5 pages: the identity as a
one-line remark, my table's real-text dispersion as one figure, the shared-tokenizer note that
makes gamma's design legible) and put the *new* contribution where it is actually new: a released,
mechanically enforcing **report validator** that refuses any cross-stack J/token comparison lacking
gross J/request at equal salience, tokenizer artifact digest, runtime-observed denominator
provenance, and J/byte + J/char — i.e. `docs/contracts/token_normalization.md` compiled into a
checker.

Then add the one thing nobody has done: **run it over published LLM-energy leaderboards and
benchmarks** (ML.ENERGY, Silicon Showdown, TokenPowerBench, Intelligence-per-Watt) and report which
of their comparisons it refuses and why. That is an artifact/tool contribution with a real,
falsifiable empirical result attached, it costs zero nights, it does not collide with Petrov, and
it is exactly Ed's energy-honest-reporting axis. It is also a much better fit for an ICPE artifact
or tool track than the current framing is for anything.

---

## Bottom line

The proposal's greatest virtue — it needs no new measurement — is also the proof of its central
defect. A paper about energy reporting that measures no energy attributable to its own thesis, on a
project whose only contrast is tokenizer-identical by construction, is a tokenization note with the
MVP paper's method sections stapled to the front. Fund **M1** and it becomes a real, modest,
defensible energy paper with a measured ranking flip. Fund **M3** and it becomes a good section
plus a genuinely useful tool. Fund it as written and Ed spends P1 desk time reproducing a 2023
NeurIPS result at 1% scale, with a pre-registered threshold whose answer he already knows.
