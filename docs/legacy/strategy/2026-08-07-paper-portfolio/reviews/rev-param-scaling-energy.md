# Counter-review — `prop-param-scaling-energy.md`

**Reviewer:** Opus 5, adversarial counter-review. Ground truth: desk checkout at `89f28bf`
(main), D-117 at end of `docs/decision_log.md`, `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`,
`docs/contracts/token_normalization.md`, `docs/research_question_registry.md`,
`CLAIMS_STATUS.md`, `docs/run_reports/2026-07-30-sweep-mechanisms.md`, and the local
model artifacts under `/Users/edr/jw_models/mlx-community/`.

**VERDICT: WEAK** (borderline KILL as scoped; a 1-night shrink is the only fundable residue)

| axis | score |
|---|---|
| novelty | 2 / 10 |
| feasibility | 7 / 10 |
| mvp_leverage | 5 / 10 |
| venue_fit | 4 / 10 |
| original_goals | 3 / 10 |

---

## What the proposal gets right (credit before the knife)

The reading is real, not hallucinated. I verified against primary sources:

- Historical anchors are correct: `docs/run_reports/2026-07-30-sweep-mechanisms.md` records
  7B-4bit decode = 0.376 J/tok and 1.5B = 0.098 J/tok → 192.5 J and 50.2 J at 512 tokens,
  matching `CLAIMS_STATUS.md`'s 192.386233 J absolute-cell member mean. The registered ABBA
  claim metric is indeed `phase_energy_j.decode`, 7B−1.5B = **141.29 J per block**, and the
  proposal correctly does *not* quote the 146.730349 J idle-subtracted diagnostic that
  sweep DC-1 quarantined. Good discipline.
- The two-anchor projection arithmetic is reproducible: slope 25.84 J/B, intercept 11.5 J →
  24 / 50 / 90 / 192 / 371 J. Correct.
- The registry cap is honestly acknowledged. `C5-1.1` is `candidate`, `claim_ceiling` = "L2
  pairwise only unless larger predeclared model set", `forbidden_upgrade` = "no
  active+total+KV regression on 4-6 models". The proposal explicitly refuses the
  scaling-law framing. Correct, and rarer than it should be.
- n=5 blocks for the dual-contrast window is **conformant**, not a deviation:
  `docs/contracts/analysis_plans.md` line 121 records D-062 as "n=10 for near-floor
  cells/contrasts, n=5 elsewhere". At 66 J and 281 J these are not near-floor. I had this
  queued as an attack and it does not land.
- Holm machinery exists (`joulewise/analysis_engine/multiplicity.py`, `holm_adjust`,
  `tests/test_analysis_multiplicity.py`). Not a new build.
- Artifact availability checks out: `Qwen2.5-0.5B-Instruct-4bit`, `-1.5B-`, `-7B-` are
  present locally; 3B and 14B are absent and must be fetched (~1.7 GB and ~8.3 GB — trivial).
- Single-request boundary is genuinely preserved. No violation.

That is where the good news stops.

---

## FATAL FLAW 1 — Contribution 3's normalization is not well-posed, and its only substantive observation is a denominator artifact

The proposal's headline normalization is

> `phase J / (runtime-observed phase tokens × published non-embedding parameters)`, in
> "pJ per non-embedding-parameter-forward", with 1.5B → ~75 pJ and 7B → ~58 pJ,
> "suggesting the normalization may decrease with size".

I checked the actual artifacts. **Three of the five ladder rungs use tied word embeddings
and two do not.** Verified directly from local `config.json`:

| model | `tie_word_embeddings` | `vocab_size` | `hidden_size` | head params read per decode token |
|---|---|---:|---:|---:|
| 0.5B | **True** (verified) | 151936 | 896 | 136.1 M |
| 1.5B | **True** (verified) | 151936 | 1536 | 233.4 M |
| 3B | True (inferred) | 151936 | 2048 | 311.2 M |
| 7B | **False** (verified) | **152064** | 3584 | 545.0 M |
| 14B | False (inferred) | **152064** | 5120 | 778.6 M |

The 3B/14B inferences are arithmetic-tight, not guesses: the published total-minus-non-embedding
gaps are 0.32 B (= 151936 × 2048 exactly, one matrix → tied) and 1.6 B (= 2 × 152064 × 5120,
two matrices → untied). Same check reproduces 0.5B/1.5B/7B against their verified configs.

The consequence is fatal. For a tied model, **the embedding matrix *is* the LM head and is
read on every decode token.** For an untied model there is a separate output head, also read
every token. "Non-embedding parameters" excludes this per-token traffic in every case. The
excluded fraction is:

> 38 % (0.5B) → 17.8 % (1.5B) → 11.2 % (3B) → 8.3 % (7B) → 5.9 % (14B)

— a monotone decline **along exactly the axis being studied**. The denominator's error is
correlated with the independent variable. Recomputing the two anchors with the head included:

| anchor | proposal (non-embedding) | with per-token head read |
|---|---:|---:|
| 1.5B | 74.9 pJ | 63.6 pJ |
| 7B | 57.5 pJ | 53.1 pJ |
| **decline** | **−23.3 %** | **−16.5 %** |

**Roughly 29 % of the reported "decrease with size" is manufactured by the denominator
choice.** Contribution 3 has exactly one substantive observation and it is not robust to a
defensible alternative definition of the same quantity. Rivoire will find this; JouleSort's
whole point is that the denominator is the claim.

Three further well-posedness objections, any one of which is sufficient on its own:

1. **The ladder spans two tokenizer identities, not one.** `vocab_size` is 151936 for
   0.5B/1.5B/3B and **152064** for 7B/14B — verified from the local 7B config.
   `docs/contracts/token_normalization.md` defines tokenizer identity as "name, revision,
   class, and vocabulary size" and C-023 compares all three strings plus
   `tokenizer_artifact_sha256`. So the five-point per-token normalization is a
   **cross-tokenizer comparison**, and the contract's "Cross-Tokenizer And
   Cross-Model-Family Comparisons" clause fires: it must either carry a tokenizer-independent
   companion denominator (J/char, J/byte) or "avoid efficiency-ranking language entirely and
   remain descriptive". The proposal's desk list contains a "tokenizer/prompt-token identity
   audit", but the audit is scoped to *prompt-token identity* (which will almost certainly
   pass — the extra 128 ids are reserved specials appended at the tail) and not to *tokenizer
   identity* (which will fail). The proposal writes contribution 3 as if the family is one
   tokenizer scope. It is not.
2. **The unit name does the work the registry forbids.** "pJ per parameter-forward" is a
   work-unit name asserting an operation count. `RQ-METHOD-FLOOR`'s `forbidden_upgrade` is
   literally "no module-energy fraction or regression-slope attribution", and
   `token_normalization.md` §"J/Token As Tokenizer-Scoped Companion Metrics" says per-token
   denominators "are not tokenizer-blind work units". The proposal's inline hedge ("not
   direct energy attribution or an operation count") does not survive the unit appearing in a
   figure axis label. Also, `token_normalization.md` requires gross request energy to be
   "co-displayed with equal or greater salience" wherever a token-normalized metric appears —
   the proposal never says it will do this.
3. **The same normalization is applied to two physically different phases.** Decode is
   bandwidth-bound (energy ∝ bytes read per token); prefill at 128 tokens is compute-bound
   with an O(n²) attention term. Calling both "pJ per parameter-forward" asserts that
   parameter-forwards are the common cost driver in both. They are not. A single unit spanning
   both phases is not well-posed even before the denominator problem.

**Verdict on contribution 3: not salvageable in its current form.** Either delete it or
rebuild the denominator as *measured bytes read per decode token from the actual quantized
artifact* — which is custodiable (artifact SHA is already pinned), phase-appropriate, and
robust. Note the artifacts are `bits: 4, group_size: 64, affine` for every rung, so
scales/zeros add ~0.5 effective bits/weight uniformly; that cancels in trend but means a
"per-parameter" figure is really a per-(parameter + quantization overhead) figure.

---

## FATAL FLAW 2 — The instrument is irrelevant to every claim that will actually resolve

This is the deeper problem, and it is a novelty problem masquerading as a design problem.

The projected decode contrasts are **66 J** (0.5B→3B) and **281 J** (3B→14B) against a
practical bar the proposal quotes as ~5 J. That is 13× and 56× clearance. `CLAIMS_STATUS.md`
records the largest actually-measured comparative floor on this instrument as
**13.998036715259254 J** (7B decode, `window_7bfloor_20260729`); even against that the
clearance is 5× and 20×.

An effect at 20–56× the detection floor **does not need this instrument.** It does not need
in-window bracketed pulse-train calibration, worst-case timing attribution, a never-zero
drift allowance, ABBA counterbalancing, hash-bound custody, or a two-gate claim regime. It
needs a wall socket and a stopwatch. The entire scientific spine that the MVP paper
(`docs/paper/draft-v1.md`, whose title is *"Detection Floors for LLM Inference Energy
Measurement on Consumer Silicon"*) exists to establish is, in this paper, load-bearing for
nothing.

And the finding itself is foreknown. There is no open question in the literature about
whether a 14B model uses more decode energy than a 0.5B model on a bandwidth-bound
accelerator. Contribution 1's stated falsification condition — "measurements do not form the
projected ordering" — is not a real risk; it is a monotone curve everyone can predict from
`bytes_read × 512`. Compare the repo's own `docs/run_reports/2026-07-30-sweep-mechanisms.md`,
which ranks six reachable mechanism claims and puts **spec decode on/off** at rank 2 with an
explicitly *open sign* in the literature ("mlx overhead could plausibly flip it"; "Batch-1
on-device … has *no published energy measurement anywhere I found*"). Parameter scaling is
not in that ranking at all, and the sweep's top-3 recommended first campaigns do not include
it. The repo has already adjudicated this direction's relative value and the proposal did not
engage with that adjudication.

The only genuinely instrument-dependent content in the entire proposal is **contribution 4,
the prefill refusal** — the one place where the effect is near the floor and the two gates
actually decide something. That is one bit of information, and D-117's floor riders plus the
already-custodied 128-token prefill feasibility finding deliver most of it for free.

---

## FLAW 3 — The kill criterion is set *below* the largest measured floor

> "desk diagnostics project the smallest registered decode contrast below **10 J** — a
> conservative 2× sizing buffer."

10 J is **less than** the 13.998 J comparative floor already measured for the 7B decode cell.
A gate that passes an effect smaller than the instrument's own largest measured floor is not
a "conservative 2× buffer"; it is a gate that cannot fail for any reason that matters. This
is a symptom of anchoring on the "≈5 J" prose constant in `CLAIMS_STATUS.md` line 55 rather
than on the measured floor values eight lines below it in the same file. The proposal should
express every sizing threshold as a multiple of the *projected floor for that cell*, not of a
document-level constant.

Related and unaddressed: **the prefill floors do not exist yet.** They are precisely what
D-117's riders will mint. Every prefill effect-size statement in the proposal (0.6 / 1.6 /
3.3 / 7.6 / 15 J, contrasts of 2.7 / 6.0 / 11.7 J) is compared against a bar that has never
been measured for that phase. The proposal's claim that 3B→14B prefill "might clear" is
therefore unfalsifiable desk speculation, and its framing of a "mixed outcome … more
informative than lengthening prompts" is a rhetorical rescue of what may well be a uniform
refusal across all three prefill contrasts.

---

## FLAW 4 — The "two free points" are not free, and the window arithmetic hides the real cost

**On the free points.** The proposal treats D-117's alpha/beta windows as delivering the 1.5B
and 7B rungs of contribution 1 ("report gross prefill and decode joules for … 0.5B/1.5B/3B/
7B/14B"). They do not, as frozen. Per the design memo, alpha/beta pre-register four cells —
decode absolute, decode comparative, prefill absolute, prefill comparative — all of which are
*floor* cells. A reported mean phase energy is a different estimand, and the memo is explicit:
*"Post hoc extraction without a pre-registered cell is also insufficient."* The
absolute-cell member mean (e.g. 192.386233 J for 7B) is quoted in `CLAIMS_STATUS.md` only
with the standing warning **"always name the cell"**, and the whole point of D-117 is that
pre-genesis values are diagnostic-only.

So contribution 1 requires **amending the alpha and beta campaign packs to pre-register a
reported-energy cell**. That is possible today — U5/U6 are unbuilt work orders — and
impossible after desk freeze, because it changes plan SHAs, extraction specs, and the
four-cell mint. The proposal never mentions this dependency. It is also a rule-11
freeze-amendment, i.e. a magistrate/cold-gate decision, not a lieutenant's.

**On the nights.** The "seven quiet nights / 21–23 quiet-machine hours" figure is arithmetically
honest — I re-derived it and the 14B window does *not* blow the 4 h envelope, because member
time is dominated by fixed overhead (1.5B decode member = 92.7 s, 7B ≈ 97 s per the design
memo's §4 evidence, for compute of ~1.2 s and ~5.4 s respectively; 14B adds ~5 s → ~102 s).
I had "14B blows the budget" queued as an attack and it does not land. Credit where due.

But nights are not the cost driver, and the proposal counts the cheap resource. The real cost
is the desk program. D-117's **three** windows required a 489-line design memo, **ten**
enumerated WRITE_SCOPE work orders (U1–U10), **three** toolchain blockers (ledger bracket
sessions, D-102 successor engine, pinset v2 multi-cell mint), and a synthetic three-window
live-ledger regression with ~15 required refusal vectors — and none of it has landed yet.
This proposal adds four more windows, each needing a U5/U6-class campaign pack, extraction
spec, condition families, order manifests, and plan-readiness tests; expands the mint from
**4 cells to 10**; adds two new registered hypotheses with multiplicity control; and
introduces two new stack identities into the custody chain. Then there is the serialization
tax the proposal ignores entirely: `[QUIET-MAC]` forbids running an agent session during a
measurement window, so every additional night is a night the desk program cannot advance.

Set against `paper-first-priority-stack` (P1 = MVP paper; P3 sacrificed if it costs P1/P2),
this is a P3-flavoured extension that materially delays P1 to buy a curve nobody disputes.

---

## FLAW 5 — Governance and title exposure

- **No registry promotion path is stated.** `C5-1.1` is `status: candidate`. The registry's
  own promotion rule requires "a named RQ slot in `PROJECT_STATUS.md`, a data plan that does
  not displace queue ranks above it, and scope fit". This proposal displaces the rank
  directly above it (D-117 closure). Unmentioned.
- **The title and thesis do the forbidden work.** "Calibrated Parameter **Scaling** on Apple
  Silicon" plus a thesis asserting "a large, resolvable association with parameter count"
  across five points is exactly the wording `C5-1.1`'s `forbidden_upgrade` and the C-014
  amendment were written to prevent, even though the body correctly disclaims a scaling law.
  Reviewers read titles. `RQ-TWO-MODEL-ACTIVE-NONCLAIM` exists in the registry precisely
  because this project has been here before.
- **Contribution 4 has no specified data source.** D-117 gamma is decode-only *by ratified
  decision* (D-117 cl.3), and the design memo rejected attaching prefill to it. The
  proposal's dual-contrast window would need prefill riders, and the memo warns the 128-prompt
  riders "do not automatically transport" without an exact matching floor cell or a
  "separately predeclared and justified transport rule". Contribution 4 is currently a claim
  with no floor.

---

## Where I tried to kill it and failed

Recorded for honesty, because a referee who only lists hits is not calibrated:

1. **"14B will swap/throttle/blow the 4 h window."** No. 68 GB is the 122B artifact's peak;
   14B-4bit is ~8.3 GB on a 128 GB machine, and member time is overhead-dominated.
2. **"n=5 blocks is an unproven deviation from the 10-block template."** No — D-062 sets
   n=5 as the default for non-near-floor contrasts. Conformant.
3. **"Holm correction is new machinery."** No — `holm_adjust` ships with tests.
4. **"The hour budget is optimistic."** No — 21–23 h reconciles with the memo's 3.14 / 3.24 /
   2.80 h per D-117 window plus four comparable extensions.
5. **"It abandons the instrument / needs unowned apparatus."** No. Existing-material
   compliance is *clean*: owned hardware, no wall-meter dependency, same discipline, single-request
   boundary preserved. This is the proposal's strongest suit and it is genuinely strong.

---

## Three strengthening moves

1. **Delete or rebuild contribution 3.** As written it is a cross-tokenizer normalization
   presented as within-family, named as a work unit the registry forbids, applied across two
   phases with different physics, and its only trend is ~29 % denominator artifact. If Ed
   wants a normalization, make it **measured bytes read per decode token from the pinned
   quantized artifact** (weights actually traversed, including the tied-or-untied head and
   the group-64 affine scales, plus a separately reported KV term). That denominator is
   custodiable, phase-honest, physically motivated, and it turns the *gap* between
   bytes-predicted and measured joules into an actual finding rather than a restatement.
   Publish the 75/58-vs-64/53 sensitivity table as evidence of denominator discipline —
   that is a real, Rivoire-shaped methodological contribution and it costs zero nights.

2. **Cut four extension nights to one: 14B only.** Drop 0.5B and 3B. They buy interpolated
   points on a curve whose shape is already determined by the two D-117 anchors, and their
   prefill contrasts are projected to refuse anyway. 14B is the only rung that adds anything:
   it is the sole prefill contrast that might clear a floor, it is the top of the servable
   dense ladder, and it extends the projection range 2× rather than interpolating inside it.
   One floor window + one 1.5B/7B-anchored contrast at n=10 is ~6.5 h across two nights; if
   the budget is truly one night, take the floor window and reuse gamma's contrast basis.
   Reframe the paper as a **§7 enrichment of the MVP** — three dense rungs plus a phase-specific
   refusal — not a standalone family study.

3. **Amend the D-117 alpha/beta packs *now*, before U5/U6 freeze, to pre-register a
   reported-phase-energy cell alongside the four floor cells.** This is the single highest-leverage
   move in the whole proposal and it is time-critical: after desk freeze the plan SHAs are
   immutable and the 1.5B/7B points become a fresh-window purchase instead of a free rider.
   Route it as a rule-11 cold-gate item (it amends a ratified freeze), attach it to U5/U6's
   WRITE_SCOPE, and state explicitly that the added cell changes no member, no runtime, and
   no floor derivation — the same argument that justified the prefill riders.

---

## Bottom line

Existing-material compliance: **clean**. Instrument discipline: **preserved**. Arithmetic:
**mostly checkable and mostly correct**. And the paper still should not be funded as scoped,
because it spends four scarce quiet nights and a D-117-sized desk program to measure a curve
whose shape is a foregone conclusion at 20–56× the detection floor — using an instrument
whose entire reason for existing is to adjudicate effects near the floor. The one thing it
proposes that the instrument is actually needed for, the prefill refusal, is nearly free.
Take that, take 14B, and give the other three nights to the mechanism axis where the sign is
genuinely open.
