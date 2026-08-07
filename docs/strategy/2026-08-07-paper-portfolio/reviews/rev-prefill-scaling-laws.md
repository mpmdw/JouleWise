# Counter-review: "Detectability-Aware Prefill Energy Scaling on Apple Silicon"

Reviewer: Opus 5 counter-reviewer (adversarial charge: try to kill it).
Ground truth: desk checkout at `89f28bf`; D-117 (end of `docs/decision_log.md`);
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`;
`docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md`;
`docs/paper/draft-v1.md`; `CLAIMS_STATUS.md`; `docs/research_question_registry.md`.

**VERDICT: WEAK.** The underlying physics is the most favourable in the portfolio —
prefill length contrasts have effect/magnitude ≈ 1, so they clear the bar by ~10×
rather than by ~1.5×. Everything built on top of that physics is wrong: the cost is
understated by 2–4×, the floor-transport rule is anti-conservative on its dominant
component, three of the four length points have no admissible floor of any kind, the
headline falsifiable test is constructed so it cannot fail, and three of five
contributions already belong to the MVP paper. Kill it *as framed*; it survives only
as a one-night rider on the D-117 fourth-window option.

---

## 1. Feasibility vs the bar and the two claim gates

### 1.1 What is right (and it matters)

The effect sizing is the proposal's one genuine strength and I could not break it.
D-078 cl.11's attribution term is ~duration-independent (~30 ms edge × ~33 W), while
prefill energy is ~linear in prompt tokens. The SYNTHESIS diagnostic (1.5B prefill
predicts 128→4096 within ~3.3%) supports ~0.0125 J/prompt-token for 1.5B. So
128→1024 ≈ 11 J and 128→4096 ≈ 49 J against a ~5 J practical bar. Critically, a
prompt-length contrast is a contrast between two *magnitudes*, not a perturbation on
a shared baseline: the effect is nearly the whole of the larger arm. Under any floor
model — absolute or proportional — effect/floor is roughly 10–13×. This is the only
proposal I have reviewed where gate 1 (floor clearance) is not in doubt.

That is also why it is not a paper. See §3.

### 1.2 Fatal flaw A — the floor-transport rule is anti-conservative on repeatability

The proposal's transport rule is: "maximum of both 128-token floors, long-end null
behavior, all observed member attribution widths, and window drift allowances."

Draft §4 composes the floor as `F_cell = max(F_abs, F_cmp)`, where

- `F_abs = max(max_i |r_i|, t·s_r·sqrt(1+1/n))` — **repeatability, scales with the
  magnitude of the measured quantity**;
- the corner-widened attribution term — **~duration-independent** (this is the whole
  content of the attribution-limited finding);
- `A_drift` — measured per window, explicitly **no duration-scaling law applied**.

The proposal's transport rule silently assumes all three components are
duration-independent. Two are; the first is not. Prefill energy at 4096 tokens is
~32× that at 128 tokens (1.5B). If the coefficient of variation is even roughly
stable, `s_r` in absolute joules grows by the same factor. Taking `max(128-token
floors)` as the absolute component at 4096 is therefore anti-conservative by
something like an order of magnitude. This is not a nit: it is the exact failure
mode draft §8 says the project refuses ("Root-sum-square composition would be
anti-conservative for a systematic edge-placement bound" — same epistemic error,
opposite direction).

The DESIGN-MEMO forbids exactly this shape of reasoning twice:

- §"Prefill floor claim eligibility": "For each metric, the operative floor is the
  maximum of independently evaluated absolute and comparative components. … Never
  sum components and **never borrow a decode floor for prefill**."
- §"Optional 256-token prefill contrast": "The floor riders here use the prefill
  phase of the 128-prompt decode workload. They **do not automatically transport to
  a prospectively defined 256-token contrast**. The fourth plan needs either exact
  matching prefill floor cells or a separately predeclared and justified transport
  rule."

If a 128→**256** transport is not automatic, a 128→**4096** transport built on a
component that provably grows with magnitude is not defensible at all.

### 1.3 Fatal flaw B — three of four length points have no floor evidence whatsoever

Count what the plan actually collects. S1 = 256 and 1024 tokens, five cross-model
ABBA blocks per length = 40 members total, **zero absolute members, zero A=A null
blocks**. S2 = five cross-model ABBA blocks at 4096 (20 members) + five 4096-token
A=A null blocks per model (40 members) = 60.

So:

| Length | Absolute floor component | Comparative floor component |
|---|---|---|
| 256 | none | none |
| 1024 | none | none |
| 4096 | none | 5 blocks/model (half the D-117 design) |

D-117 gamma's floor rule is `cross_stack_armwise_max.v1`: independently resolve the
1.5B and 7B cells and take their maximum. A cross-model contrast at length L
therefore needs *two* floor cells at length L. The plan supplies zero at two of
three new lengths and a half-strength comparative-only cell at the third. Every
claim in Contributions 2 and 3 rests entirely on the unratified transport rule of
§1.2. If the metrology review rejects it — and the memo's own language says it
should — **both extension nights produce nothing claim-bearing.**

### 1.4 Fatal flaw C — the design under-powers precisely the cells it calls refusals

The proposal drops from D-117's ten ABBA blocks (n=10) to **five** (n=5) for every
contrast. Gate 2 is interval-supported direction, and the interval half-width scales
as ~1/sqrt(n): the SYNTHESIS's composed contrast half-width of ~1.81 J at n=10
becomes ~2.6 J at n=5. The repo's own D-062 rule (visible in the seeded AP-1/AP-2
plan rows) is "n=10 for near-floor cells/contrasts, n=5 elsewhere."

The proposal then designates 128→256 within 1.5B (~1.6 J projected — definitionally
near-floor) as a *deliberate refusal* and gives it **n=5**. A refusal produced by a
design the project's own sizing rule says was under-powered is not evidence about
the instrument; it is evidence about the manifest. Contribution 5 ("published
refusal boundaries … distinguishing measurement incapacity from equality") is
directly undermined: you cannot distinguish incapacity from under-powering when you
chose the under-powering.

### 1.5 Fatal flaw D — the headline falsifiable test cannot fail

Contribution 2 is the paper's flagship: fit a pre-registered linear-in-length model
and predict a held-out cell. The proposal states "The linear model is trained on
128, 256, and 4096; 1024 is held out."

- Three training points, two free parameters → **1 degree of freedom**.
- 1024 lies *between* 256 and 4096 → this is **interpolation**, not extrapolation.
- The prediction envelope is "guarded" by floors, i.e. widened by the same
  conservative machinery that makes floors large.

A 1-df linear interpolation to a mid-range point, judged against a
deliberately-conservative envelope, passes essentially by construction. The registry
already says so: seeded plan AP-1's "Holdout cells (L3 only)" row reads "both factor
levels occur in the training grid, so neither is statistical extrapolation. **No
extrapolation claim is available from this grid.**"

### 1.6 True cost — understated by 2–4×

Reconstruct the window budget from the DESIGN-MEMO's own alpha column. Fixed
per-window operational overhead: pre-cal 8 + 12 NEG8 members 22 + bound eval 1 +
start refs 8 + midpoint 5 + end refs 8 + post-cal 8 + untouched idle 10 = **70 min**
before any science. Science rates: ~1.9 min/member (absolute stage), ~1.7 min/member
(ABBA stage) for 1.5B; ~1.8–2.0 for 7B. The 4 h ceiling with the mandatory 20%
margin gives base occupancy ≤ 200 min → science ≤ ~130 min → **≈ 65–75 science
members per window**, before long-prompt prefill inflates per-member time.

Now price the plan honestly:

- **Minimum defensible version** (one long-endpoint floor pair per model, transported
  downward under a ratified monotone envelope): 1.5B floor window (10 abs + 40 null
  = 50 members) + 7B floor window (50) + contrast window(s) (40–60). **4 extra
  nights**, not 2.
- **Fully compliant version** (own floor cells per length per model, as the memo's
  "exact matching prefill floor cells" branch requires): 3 new lengths × 2 models ×
  50 members = 300 members ≈ 5 nights of floors alone, plus ~2.5 nights of contrasts.
  **≈ 7–8 extra nights.**

The proposal says two. Its own contingency clause ("fund a third extension night
with ten-block long-prompt floors") already concedes the direction of the error but
under-counts it, because a ten-block long-prompt floor is needed *per model*.

### 1.7 Cost error shared with the whole portfolio: the MVP is not 3 nights

The proposal asserts "the complete paper therefore costs **five quiet windows from
today**: the three already authorized plus two." That is false on the repo's own
draft. `docs/paper/draft-v1.md` §6 (contribution C-iv, "full instrument
characterization") has **all six rows marked `[PENDING WINDOW C]`** — linearity, null
response across magnitudes, empirical floor verification, phase-attribution causal
consistency, drift/settling, between-session stability. D-117 cl.4 explicitly places
the MET-WINDOW-C-01 campaign *after* the three-window closure. The MVP paper as
drafted is 3 nights **plus Window C**. Every "N + 2" arithmetic in this proposal
inherits that omission.

---

## 2. Existing-material compliance

Mostly compliant in spirit, with two hard violations.

- **Compliant:** owned hardware only, no wall-meter dependency, single-request
  boundary intact, all new harness work is manifest/generator/extraction plumbing.
  The correct statement that "a WT310E cannot validate prefill/decode attribution"
  matches draft §8 exactly.
- **Diagnostic reuse — what is genuinely reusable.** Per D-078/D-110 and
  `CLAIMS_STATUS.md` §1 ("pre-genesis windows CANNOT be claim-consumed — their role
  is diagnostic and rule-establishing only"), the historical corpora are void for
  claims. Reusable: (a) *sizing* projections (0.0125 J/prompt-token; the 5.81 J
  128-token cross-model delta; the ~3.3% linearity agreement), (b) runtime/memory
  budgeting, (c) design templates. **Not reusable:** any floor literal (the memo
  bans `7.377086` by name), any effect size as a result, and — the one the proposal
  gets wrong — the diagnostic linearity *as a fitted model*. The proposal is right to
  re-fit prospectively; it is wrong to then call the re-fit a validation of anything,
  since the prospective grid is the same shape as the diagnostic that motivated it.
- **Violation 1 — forbidden upgrade in the title.** AP-1's registry row: "Ceiling
  L3. **Forbidden upgrade: no curvature, universal scaling law**, or
  architecture-wide conclusion from this grid." The paper is titled "Prefill Energy
  **Scaling** … " with Contribution 2 named "empirical scaling curves." The body
  disclaims it ("not a universal scaling law"), but a title that a reviewer, an
  advisor, or a future citation will read as the forbidden upgrade is a governance
  problem, not a wording preference.
- **Violation 2 — gratuitous incompatibility with the seeded grid.** AP-1 freezes
  prompt levels {128, 512, 2048, 4096}. The proposal picks {128, 256, 1024, 4096}.
  There is no stated reason. Choosing non-overlapping interior levels forfeits reuse
  of AP-1's frozen design, estimator, multiplicity rule, and holdout logic, and
  guarantees that neither dataset can ever be pooled with the other.

---

## 3. Novelty — the real problem

Prefill energy is approximately linear in prompt length because prefill is
compute-bound over tokens. This is not in dispute anywhere in the literature; the
proposal's own related work will have to cite TokenPowerBench (which already
"groups results by context length", draft §8) and Fernandez et al. ACL 2025. The
scientific finding is a figure, not a paper.

So the novelty must be carried entirely by the metrology wrapper — and the metrology
wrapper *is the MVP paper*. Score the five contributions against `draft-v1.md`:

| # | Contribution | Already MVP? |
|---|---|---|
| 1 | Two claim-bearing prefill floors | **Yes.** These are D-117's alpha/beta prefill riders, already funded, already the MVP's C-v material. Not a contribution of this paper. |
| 2 | Model-specific scaling curves + held-out prediction | New — but see §1.5, it cannot fail. |
| 3 | Model-size × length interaction | New — but needs floors at every length it spans (§1.3). |
| 4 | Prospective workload sizing as methodology | **Substantially MVP.** Draft §8 already writes the PairedMDE one-way-ratchet doctrine; the SYNTHESIS records it is "consumed by the MVP paper draft §7 'Prospective workload sizing'." |
| 5 | Published refusal boundaries | **Yes.** This is C-iii, the fail-closed protocol and refusal log, already the MVP's third contribution. |

Two of five are new, and one of those two is unfalsifiable as designed.

## 4. Dedup against the D-117 fourth-window option

This is the decisive comparison for funding. D-117 cl.3 leaves open "a prospectively
frozen ≥256-token prefill contrast arm" at "+~110 core minutes, likely its own
window." That option buys the one thing the project actually lacks: a *prefill
contrast that clears the bar* (SYNTHESIS projects ~11.6 J at 256, ~2.3× the bar,
against a 128-token contrast whose interval lower edge sits ~4.0 J, below it).

The proposal's S1 arm at 256 tokens is a **strictly worse version of that option**:
same length, half the blocks (n=5 vs the fourth window's presumed n=10), and no
dedicated floor cell where the fourth window would carry its own. The proposal then
adds two further lengths whose claim status depends on an unratified transport rule.

Dedup value is therefore **low and negative**: funding this proposal would consume
the fourth-window option and replace it with an under-powered instance of itself.

## 5. Venue fit

Broadly honest — capstone chapter, EuroMLSys/HotCarbon or ICPE emerging-research,
ICPE full only conditionally. But the honesty is undercut by the title, and the
stated ICPE-full condition ("if the held-out prediction … succeed[s]") is
circular given §1.5. Against Rivoire's bar specifically, a JouleSort co-author will
ask the repeatability-scaling question in §1.2 within one reading.

## 6. Original-goals service

Accurate and appropriately modest. Serves the workload/length axis of the modular
harness and the "energy as a third metric" goal; serves none of speculative decode,
MTP, MoE, KV variants, or split. Its claim that long workloads are "foundational"
for those mechanisms is true and is the best argument for it — but the same argument
is served more cheaply by the fourth window plus a decode-length rider.

## 7. Non-findings (things I tried and could not break)

- "Identical nested token prefixes cannot be proven across tokenizers" is listed as a
  kill criterion. It is a non-risk: Qwen2.5-1.5B and Qwen2.5-7B share the same
  tokenizer, so nested prefixes are trivially identical. Listing it inflates the
  apparent rigour of the kill list.
- The single-request boundary claim is correct. Nothing here batches, reuses cache
  across requests, or introduces a server.
- The 4096-token memory-headroom concern is real but small: 1.5B/7B 4-bit KV at 4096
  tokens is ~112 MiB / ~224 MiB on a 128 GB machine. This will not be the kill.

---

## Scores

| Axis | Score | One-line justification |
|---|---:|---|
| Novelty | **3** | Prefill ∝ prompt length is known; the metrology wrapper is the MVP's; title claims a forbidden upgrade. |
| Feasibility | **4** | Effect sizing is excellent (~10× the bar); the *plan* is not feasible — no floors at 3 of 4 lengths, anti-conservative transport, n=5 on near-floor cells. |
| MVP leverage | **4** | Reuses §§3–5 cleanly, but 3 of 5 contributions are re-labelled MVP contributions; incompatible with the seeded AP-1 grid. |
| Venue fit | **5** | Honest ladder, but the ICPE-full condition is circular and the title is a referee magnet. |
| Original goals | **4** | Workload axis only, honestly stated; no mechanism axis. |

## Three strengthening moves

1. **Shrink to the fourth window plus one long-endpoint rider, and make each window
   self-flooring.** Drop 256 and 1024 as claim points. Fund, per model, one window
   of: 10 ABBA blocks of the 128-vs-L prefill contrast (40 members) + 5 A=A null
   blocks at L (20 members, the in-window comparative floor for the new condition
   family) = 60 science members, ~3.6–3.9 h with long prefills — rehearse against the
   4 h ceiling before freezing. Pick L = 1024 (≈11 J projected, comfortably clearing,
   and short enough to keep the window inside budget). This converts an
   unclaimable-by-default 2-night plan into a claim-bearing 2-night plan and removes
   the transport dependency entirely. Take the absolute component by transport only —
   it is the non-binding one (historically 6.29 vs 14.0 J for 7B).
2. **Run the repeatability-scaling desk check before funding anything — it is free
   and it is a kill criterion.** From the existing (void-for-claims, fine-for-sizing)
   1.5B corpora, compute the CV of prefill energy at 128 and at 4096 tokens and the
   corner-widened `F_abs` at each. If CV is roughly constant, the floor grows ~linearly
   with length, effect/floor is roughly *flat* across the ladder, and the entire
   "length is the free lever" premise fails beyond the attribution-dominated regime.
   The minted diagnostics already hint at proportionality: 1.5B decode ~51 J with
   absolute/comparative floors 3.82/3.59 J (~7%), 7B decode ~192 J with 6.29/14.0 J
   (~3–7%). Two points, same ratio band. Settle this at the desk, today, before a
   night is spent.
3. **Replace the unfalsifiable held-out fit with a real prospective test, and fix the
   title.** Either (a) pre-register a point prediction with a *pre-stated* tolerance
   in joules (not a floor-guarded envelope) and a stated interval that would falsify
   linearity, or (b) drop Contribution 2 and reframe the paper around the one thing
   that is genuinely novel and genuinely at risk: *the sizing rule itself* — "we
   pre-registered which contrasts would clear, and here is the pre-registration
   against the outcome," with the 128-token marginality as the registered near-miss.
   Retitle to something the AP-1 forbidden-upgrade clause permits, e.g. "Prospective
   Workload Sizing for Phase-Resolved Prefill Energy," and align interior levels to
   AP-1's {128, 512, 2048, 4096} so the data can ever be pooled.
