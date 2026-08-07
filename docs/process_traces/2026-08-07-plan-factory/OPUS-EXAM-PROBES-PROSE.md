# Opus 5 examination — DRAFT-PROBES.md and DRAFT-RESULTS_PROSE.md

Examiner: Opus 5. Date: 2026-08-07. Tree: `scratchpad/desk` @ `3b5a794` (main).
Method: read the final assistant block of each trace; independently verified every
`mlx_lm` API claim against the installed venv at `/Users/edr/code/JouleWise/.venv`;
independently resolved every cited line anchor; checked both drafts against
`docs/paper/draft-v1.md`, D-117, and `docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md`.

---

# DRAFT 1 — DRAFT-PROBES.md

## Verdict: **ACCEPT-WITH-AMENDMENTS**

Deliverable present (final block, lines 3565–3878; lines 3249–3560 are a duplicate
emission of the same block — harmless but worth noting for whoever extracts it).

### What independently verified TRUE (credit where due)

- **Every cited CLI flag exists.** `--draft-model`, `--num-draft-tokens`, `--temp`,
  `--top-p`, `--min-p`, `--top-k`, `--xtc-probability`, `--seed`, `--verbose`,
  `--max-tokens`, `--prompt -` are all present in the installed
  `mlx_lm.generate` argparse. Confirmed by running `--help`.
- **Versions match the freeze.** `mlx-lm 0.31.3`, `mlx 0.31.2` installed, exactly as
  the draft pins.
- **All three model directories exist** at the exact cited paths
  (`/Users/edr/jw_models/mlx-community/Qwen2.5-{0.5B,1.5B,7B}-Instruct-4bit`).
- **The byte-identity check is sound and guaranteed, not hoped for.**
  `speculative_generate_step` accepts a draft token only on exact match
  (`if tn != dtn: break`, `generate.py:621`) against the target's own sampled token,
  and with `--temp 0` `make_sampler` returns `lambda x: mx.argmax(x, axis=-1)` before
  any top-p/min-p/top-k/XTC stage is consulted. Greedy output is therefore provably
  identical between arms; an output mismatch really is a feasibility failure, as the
  draft says.
- **"Emit exactly N tokens" is enforceable.** `speculative_generate_step` clamps
  `num_draft = min(max_tokens - ntoks, num_draft_tokens)` and breaks at `ntoks ==
  max_tokens`; `stream_generate` breaks at `(n+1) == max_tokens`. The `Generation: N
  tokens` line is a real acceptance check.
- **Probe B's gate framing is honest in substance** — `[ED-EXTERNAL]`, "without
  access, Probe B remains open; fixture or Mac evidence cannot substitute" is the
  right posture, and the "does not close Phase-7 items 1–3 or 5–8, does not make
  NVIDIA claim-bearing" scoping is exactly right.
- **The 100 ms PASS threshold is faithful to its source** (`rev-split-inference-metrology.md:140`
  disposition, verified verbatim).

### Amendments — Probe A

**A1 (executability, blocking-as-written).** `$OUT` is referenced in all four command
blocks but never assigned in the setup block (only `MLXGEN`, `DRAFT`, `PROMPT_FILE`,
`N`). Pasted as given under zsh this errors on the redirect. Add a deterministic
assignment (`OUT="${CUSTODY}/${TARGET}_${MODE}_n${N}_run${i}.log"`) and wrap the
runner in `set -euo pipefail`. This is the only literal executability defect found.

**A2 (the decision rule can fire on contradictory evidence).** CLOSE is defined as
"for **either** 7B workload, all five valid ratios are below 1.0". As written, a
negative at N=128 fires CLOSE even if N=512 shows a clean win — and N=128 is the
less representative cell (fixed per-round draft overhead is amortized over fewer
tokens). Replace with: CLOSE iff all five ratios < 1.0 at **7B/512** (the governing
cell) **and** the 7B/128 median is also < 1.0; a split between lengths is
INCONCLUSIVE by construction.

**A3 (highest-value scientific amendment).** The suggested prompt — "numbered list 1
to 1000, each line the integer, a colon, and the word measurement" — is a degenerate,
near-zero-entropy sequence on which a 0.5B draft will achieve near-ceiling acceptance.
It measures speculative decoding's **best case**, not its operating case. Consequence:
(i) the CLOSE branch, which is the entire justification for the probe ("negative result
closes the question at zero night cost"), becomes very unlikely to fire; (ii) a SURVIVES
verdict on this prompt carries almost no information about realistic workloads. Add one
frozen, hashed free-prose instruction as the **governing** workload at the same two
lengths, and keep the list prompt as an explicitly labelled best-case upper-bound cell.
Pay for it with A6.

**A4 (the inference gap the parent asked about — throughput does NOT settle energy
without a stated assumption).** Energy per token is `E = P̄ · t`. A throughput ratio
`R = tps_on/tps_off < 1` gives `t_on/t_off = 1/R > 1`, so
`E_on/E_off = (P̄_on/P̄_off)·(1/R)`. The CLOSE-negative conclusion is licensed **only
under `P̄_on ≥ R·P̄_off`** — i.e. spec-on average package power must not fall below
spec-off by more than the throughput deficit. The draft never writes this down. It is
almost certainly true (spec-on performs K draft forwards plus one (K+1)-position target
forward per round, versus one target forward per token — strictly more model work per
emitted token, on a bandwidth-bound decode), but "almost certainly true" is exactly
what this project pre-registers rather than assumes. Add: (a) the assumption stated as
an assumption, (b) its one-sentence physical warrant, (c) a named falsifier — a
~10-minute quiet-window package-power spot check on one 7B/512 pair, run only if the
CLOSE verdict is contested. Also add the converse sentence explicitly: **a throughput
win does not imply an energy win** (spec decode can be faster and more energy-hungry per
token). The SURVIVES branch gestures at this; it should say it outright.

**A5 (K-scope inconsistency).** The CLOSE branch kills "the K-manipulation/runtime-fork/
floor/AP program", but the probe tests exactly one K (`num_draft_tokens=3`), and the
closure's own scope sentence lists "pinned runtime, target/draft pair, batch 1, prompt,
and lengths" — **K is omitted from the scope list while the branch kills the K program.**
Throughput is not monotone in K. Fix by either sweeping K ∈ {2, 3, 5} at the governing
cell (~+20 min) or narrowing the CLOSE branch to "no benefit at K=3 on this pair" and
adding K to the scope list.

**A6 (half the invocations feed no decision).** The 1.5B target consumes 20 of the 40
scored invocations and appears in no branch of the decision rule. Either give it a
pre-registered role — recommended: negative control, since the smaller target/draft
compute gap should yield a ratio no greater than the 7B ratio, a design-consistency
check rather than a decision input — or drop it and spend the time on A3's prose cells,
keeping the probe at ~2 h.

**A7 (environment contamination — this box runs the orchestration).** Forbid concurrent
agent/Codex/CI sessions, indexing, and backups during scored runs; this is the same Mac
the delegation loop runs on and any of those will corrupt tok/s far beyond the effect
size. Require AC power. Record `pmset -g`, thermal pressure, and pre/post load average
per invocation. Add a fixed inter-invocation idle (≥60 s) and require the two members of
a pair to be temporally adjacent, so the ABBA-style pairing actually cancels thermal
drift across 40 back-to-back 7B runs.

**A8 (known metric bias, direction matters).** `generation_tps` is
`(n+1)/(elapsed since the first yielded token)` (`generate.py:735, 750`). Under
speculation, the remaining tokens of the first accepted block are emitted at
near-zero elapsed time after the timer reset, inflating spec-on tok/s by roughly K/N
(~2% at N=128, ~0.5% at N=512). Record it and state the direction: **conservative for
CLOSE, anti-conservative for SURVIVES.**

**A9 (optional stopping).** "If desired, extend prospectively to `n=10`" *after* an
INCONCLUSIVE result is outcome-dependent stopping, and sits awkwardly beside the
draft's own "pre-registered operational meaning" language. Either pre-register the
n=10 extension unconditionally or delete the sentence.

**A10 (freeze the templating decision).** The chat template is applied by default; the
plan neither freezes nor mentions it. State that `--ignore-chat-template` is not
passed, record the realized templated prompt-token count as part of the identity check,
and specify the extraction boundary for the generated-text hash (the text between the
two `==========` delimiter lines) so the byte-identity check is reproducible by a third
party.

**A11 (inert flags).** With `--temp 0`, `make_sampler` short-circuits to argmax before
top-p/min-p/top-k/XTC are consulted. Keep the flags for the record but label them
no-ops, so no reader believes those sampler paths were exercised.

**A12 (citation drift).** `generate.py:657` is the `def stream_generate` line, not the
speculative dispatch (dispatch is at ~709–713; `speculative_generate_step` is defined
at 473). `:784` is the `for response in stream_generate(...)` line; the tok/s prints are
at ~790–797. Re-anchor.

### Amendments — Probe B

**B1 (the gate citation points at the wrong device, and omits a precondition).**
`phase_1_exit_checklist.md:329` is inside the **NVIDIA 3050** section. The
**3080 Ti (borrow)** section begins at line **345** and carries two unticked boxes:
"Borrow window confirmed and entered in `docs/milestones.md` (**R-006: schedule only
after Stage 3.0 verdicts + rehearsed runbook**)" and "Memory limit documented".
So the gate is *not* merely "does Ed have physical or SSH access" — R-006 imposes a
scheduling precondition the draft never names. Whether a non-claim characterization
sits inside or outside R-006 is a rule-11 cold-gate question, not the plan's to assume.
Also reconcile the vocabulary: the checklist says *borrow*, the plan says "the 3080 Ti
rig" as though owned.

**B2 (the PASS criterion rests on an unidentifiable fit).** The measured edge response
is the convolution of the card's real DVFS/clock-boost transient with the telemetry
filter. NVML alone cannot separate them, so "fits causal boxcar and first-order
averaging models … emits a conservative `B_GPU`" is not identifiable as stated — the
draft uses the word *conservative* without saying why it is entitled to it. Fix by
(a) declaring `B_GPU` an explicit **upper** bound that deliberately conflates device
transient and sensor filter, which is conservative in the admission direction, and
saying so; and (b) offering a locked-clock arm (`nvidia-smi -lgc`) as an optional
secondary — noting that this requires relaxing the plan's own blanket "never change
clocks" rule and therefore an Ed decision.

**B3 (a better instrument is listed and then unused).** `nvmlDeviceGetTotalEnergyConsumption`
(mJ monotone counter, Volta+, so available on GA102 — verify in inventory) appears only
as an inventory checkbox. Promote it to a primary instrument: it independently reveals
the fresh-value cadence and supplies the energy-area reference. As written, "integrated
area recovery against the long-plateau reference" derives its reference from the same
sample stream under test — partly circular.

**B4 (GPU mis-binding risk).** The scripts "select the GPU by UUID" but the pinned CLI
uses `--id=0`. On a rig that may also carry the 3050 this binds the wrong device. Use
`--id=<UUID>` everywhere and record the UUID in the manifest.

**B5 (the two streams are not clock-comparable).** The NVML sampler stamps monotonic
time before and after each call; the CLI sampler is specified to keep `nvidia-smi`'s own
`timestamp` field (coarse wall-clock). Require the CLI wrapper to stamp
`CLOCK_MONOTONIC_RAW` on each line **as read**, and treat `nvidia-smi`'s field as
diagnostic only — otherwise "delivered cadence" cannot be compared between streams,
which is the probe's headline quantity.

**B6 (time is under-priced by roughly a factor of 1.5).** Per train:
45 s opening plateau + 44.25 s of ON time (5 × Σ{0.05,0.1,0.2,0.5,1,2,5} s) + ~105 s of
inter-pulse idle (35 × 3 s) + ~30 s tail ≈ **3.7 min**; × 3 trains × 6 requested intervals
≈ **67 min**. That matches the stated 60–90 min *only if thermal re-admission is free* —
but the plan requires returning to within 2 °C of the frozen band between trains after
~44 s of high-utilization GEMM, plausibly 3–5 min each, i.e. another **55–90 min**
unaccounted, plus the 5 min initial idle. Re-price to **≈3.5–4.5 h**, or cut to four
requested intervals ({25, 100, 250, 1000} ms) to genuinely fit one evening.

**B7 (make the PASS threshold's consequence explicit — it strengthens the "don't fund"
disposition).** `B_GPU ≤ 100 ms` is faithful to the review. But combined with the
plan's own `B_composite < 0.25 × shortest_claimed_interval`, a PASS *at* the 100 ms
boundary already forbids any stage shorter than ~400 ms — before the other two terms
are added at all. Prefill stages at this project's workloads are plausibly shorter than
that. Say so: the probe's honest headline may be "how much of the split direction
cadence alone already kills", and a boundary PASS may be operationally useless.

**B8 (add a named FAIL sub-mode).** If the driver exposes neither `power.draw.instant`
nor a distinct averaging field, that is itself a clean publishable negative
characterization — pre-register it as its own named sub-mode rather than folding it
into the generic "required power fields are unsupported".

**B9 (custody orphaning).** Both probes write to `~/JouleWise-probe-custody/`, outside
the repo and outside the project's existing evidence-root conventions. Name which
convention this follows and bind `SHA256SUMS` into the repo record on the authorized
follow-up turn, or the evidence has no chain.

**B10 (citation drift).** Phase-7 item 4 is at `docs/JouleWise_Hardening_Proposal.md:453`;
line 444 is the `### Phase 7` heading.

### Three highest-risk items — Draft 1

1. **The CLOSE branch cannot realistically fire on the chosen prompt (A3).** The probe's
   entire economic justification is a cheap negative closure, and the workload is chosen
   to be maximally favourable to the thing it is meant to kill. Most likely outcome as
   written: two hours spent, SURVIVES or INCONCLUSIVE returned, nothing closed, and the
   K/fork/floor program still on the table with a misleading tailwind.
2. **The throughput→energy inference is asserted, not stated (A4).** A CLOSE verdict
   would be published as closing "the energy question", but the document never records
   the power-monotonicity assumption that licenses the step. On a project whose entire
   thesis is that unstated inferential steps are where energy claims go wrong, shipping
   this gap is the self-inflicted wound.
3. **Probe B's PASS emits a bound its method cannot identify (B2), against a gate whose
   real precondition is unstated (B1).** The fitted `B_GPU` conflates the card's physical
   DVFS ramp with the sensor's filter; and the access gate is R-006-conditioned, not
   merely Ed-availability-conditioned. Either alone would make a "PASS" overstate what
   the evening bought.

**Re-priced honest cost after amendments:** Probe A ≈ 2–2.5 h (2 h if A6 trades the 1.5B
target for A3's prose cells); Probe B ≈ 3.5–4.5 h, or one genuine evening at four
requested intervals.

---

# DRAFT 2 — DRAFT-RESULTS_PROSE.md

## Verdict: **REWORK — there is no deliverable in this file.**

### The finding

`DRAFT-RESULTS_PROSE.md` is a **truncated trace**. The session ended mid-tool-call and
never emitted a final assistant message. Evidence, all mechanically checkable:

- The string `[VALUE]` — which the brief mandates as the placeholder token — appears
  **exactly once in the entire 5,451-line file**, on line 14, inside the *user prompt*.
  It appears zero times in any assistant output.
- The last `^codex$` assistant marker is at line **2927**; the last tool marker
  (`exec` / ` succeeded in`) is at line **5367**. The file ends at line 5908 (numbered)
  with `nl`-style output of `docs/decision_log.md` §D-096, i.e. raw exec output.
- The only assistant narration after line 2927 is a single scene-setting sentence
  ("The governing design separates the three D-117 windows…"), followed by tool calls
  to the end, the last of which errors (`rg: joulewise/analysis_engine.py: No such file`).

There is no results prose, no three variants, no §6 shell, and no `[VALUE]` placeholders
to examine. I cannot flag sentences that would become false under landed values, because
no sentences exist. Any downstream document asserting these drafts were custodied is
wrong on this file.

### Batch-level signal (cheap, and the parent should have it)

Applying the same last-assistant-marker-vs-last-tool-marker test across the whole
plan-factory batch:

| File | lines | last `codex` | last tool marker | deliverable? |
|---|---|---|---|---|
| DRAFT-NEVERZERO.md | 10583 | 10131 | 10055 | **yes** |
| DRAFT-PROBES.md | 3878 | 3248 | 3195 | **yes** |
| DRAFT-MOE_GATES.md | 4100 | 3339 | 3794 | **no** |
| DRAFT-QUANT_GATES.md | 21285 | 16063 | 20698 | **no** |
| DRAFT-REASONCODE.md | 11428 | 5737 | 11070 | **no** |
| DRAFT-RESULTS_PROSE.md | 5451 | 2927 | 5367 | **no** |
| DRAFT-U4.md | 8764 | 986 | 8597 | **no** |
| DRAFT-U8.md | 10692 | 9241 | 10448 | **no** |

**Six of eight** custodied "drafts" in commit `3b5a794` end in tool output rather than a
final message. Only PROBES and NEVERZERO carry a deliverable. This is a same-signature
failure across a batch — per the standing escalation trigger, the next spend should be a
consult on *why the batch truncated* (quota exhaustion? per-session output cap? wrapper
harvest bug?), not eight re-runs. Recommend a custody-time postcondition on the wrapper:
refuse to file a `DRAFT-*.md` whose last assistant marker precedes its last tool marker.

### The acceptance contract for the re-run (doctrine-derived; this is the deliverable I
can give)

The parent's real question — *which sentences become false depending on which values
land* — is answerable in the abstract, and pre-writing the failure classes is worth more
than reviewing prose that does not exist. Any re-run brief should forbid these by name.

**P1 — Summed-threshold leakage (the single most likely doctrinal failure, and it lives
in Variant A).** §4 is explicit: `practical joint-clearance size = F_cell + B_claim` is
a *disclosure* quantity, "not a single summed acceptance threshold, and the decision
interval is not compared with the sum." Any sentence of the form "the effect of [VALUE] J
exceeded the joint-clearance bar of [VALUE] J", or "cleared floor plus claim bound", or
"passed the combined threshold", is doctrinally false regardless of what lands. Required
shape: floor-gate outcome stated first and alone, direction-gate outcome stated second
and separately, and the joint-clearance size mentioned only in a sizing sentence
carrying its own explicit "this is not a threshold" clause.

**P2 — Magnitude adjectives that flip with the values.** "Comfortably clears",
"substantially above", "by a wide margin", "an order of magnitude", "marginally" are all
value-contingent and all become false or overclaiming at some landed value. Pre-drafted
prose must contain **no** unbound magnitude adjective — only `[VALUE]`-bound numerals,
or a pre-registered adjective ladder keyed to explicit bands.

**P3 — The attribution-limited label is doubly conditional and will be asserted
unconditionally.** §4 licenses it only when (a) attribution dominance is the *sole*
otherwise-refusing condition **and** (b) an exact corner-widened floor exists. Every
occurrence in pre-drafted prose must be written as an explicit conditional branch with
its own alternate text, never as flat assertion.

**P4 — Dominance is itself a landed fact.** The paper's ≈1 J from ≈30 ms × ≈33 W is a
prior-calibration result. A fresh window could land drift- or repeatability-dominated.
"Attribution again dominated" is a value-contingent claim and must be placeholdered.

**P5 — "not resolvable" is not "no difference".** §4 and §8 both forbid it. Ban by name:
"did not differ", "no measurable difference", "equivalent", "on par", "came out flat",
"null result", "failed to reach significance", "trend toward". Required forms: *"not
resolvable at the stated floor under the recorded conditions"* (floor-gate failure) and
*"unresolved; no directional claim"* (direction-gate failure). Variant B is where this
will creep in, and Variant B is the on-thesis outcome.

**P6 — Variant B must be two variants, not one.** B1 (floor-gate failure) and B2
(direction-gate failure) require materially different sentences: B1 may not quote a
direction at all; B2 may quote the point estimate but must state that the composed
interval spans the registered direction's boundary. A single "contrast refused"
narrative will be false for whichever mode lands.

**P7 — Variant C is under-specified in the brief, and its obvious framing is false.**
With three windows (1.5B decode floor, 7B decode floor, decode contrast), a single
*floor*-window failure does not merely reduce coverage — it removes an arm the contrast's
gate depends on. Under D-095's `cross_stack_armwise_max.v1` (each arm's floor resolved
independently on its exact stack; the claim clears **both** arm gates, i.e.
`max(F_A, F_B)`, never the sum), a missing arm floor makes the contrast **not evaluable**,
not "partially claimable". Any Variant C prose that keeps the contrast alive on one
surviving floor is doctrinally false at landing. This is the most important single
instruction for the re-run.

**P8 — Prefill is floors-only.** D-117 cl.3 makes the registered contrast **decode-only**;
the paper's own Table 2 row reads "not registered under the adopted default … floors
only". Any narrated prompt-processing *difference* is an unregistered post-hoc claim.
Prefill prose may report floor cells and nothing comparative.

**P9 — Tokenizer-scoped companion metrics.** J/prompt-token and J/output-token are
companion metrics, never the headline contrast, and never compared across tokenizers.
Within Qwen2.5 the tokenizer is shared so intra-family use is admissible — the prose must
say *why* it is admissible rather than silently doing it, since the rule is the paper's
own contribution.

**P10 — Never-zero drift.** D-102 pin 3, binding under D-117 cl.1: `A_drift ≥ 0.010818 s`
always. "Drift was negligible/absent" is false by construction. Correct sentence: "the
drift screen passed; the allowance remains positive by construction."

**P11 — `n` means bundles.** The paper fixes it: "n counts independent valid run bundles,
not samples or items within a bundle." Ban "over [VALUE] measurements"; fix the noun
everywhere.

**P12 — The §6 shell presumes a night that is not funded.** Window C is **ED RULING #1,
open**; the six §6 rows are all `[PENDING WINDOW C]`, and the adjudication's stated
alternative is "rewrite abstract+contributions+§6 as declared future work". The §6 shell
must therefore be written with the *unfunded* branch as default and the populated branch
as conditional — not as past-tense characterization results.

**P13 — Register and tense.** (a) Plain advisor-facing language is a standing rule
(Rivoire): `F_cell`, `B_claim`, `ABBA`, "gamma window", "armwise-max", "cl.11", "D-117"
must not appear unglossed in paper prose. (b) The paper is today uniformly *future*
tense ("The planned demonstration will ask…"). Each past-tense variant must ship with
its own matching §7 lead-in rewrite, or the section lands half-future/half-past.

### Three highest-risk items — Draft 2

1. **The file is empty of deliverable, and the batch commit says otherwise.** Six of
   eight drafts in this batch are truncated traces. The immediate risk is not the missing
   prose — it is that a downstream turn treats `3b5a794` as having custodied eight
   drafts and schedules review, adjudication, or Fable time against artifacts that do not
   exist. Fix the custody postcondition before re-running anything.
2. **Pre-drafted results prose is a structurally dangerous artifact for this project.**
   Every one of P1–P12 is a way for a fluent, doctrinally-worded paragraph to survive
   review while being false at landing, precisely because the reviewer reads the prose
   and not the values. If the re-run happens, it must emit prose in which **every**
   value-contingent clause is syntactically marked as conditional, so a reader cannot
   accidentally read an assertion.
3. **Variant C's natural framing is false (P7) and Variant A's natural framing leaks a
   summed threshold (P1).** These are the two variants a writer will find easiest to
   write well and hardest to write correctly — and the summed-threshold error is exactly
   the one the paper spends a paragraph pre-empting, which means a reviewer skimming for
   doctrine-shaped language will read the error as compliance.
