# Paper portfolio — magistrate adjudication (2026-08-07)

**Process:** 24 paper directions (20 directed + 4 open-ended) each developed
by a Sol high/fast session with full repo context (BRIEF.md), each
adversarially counter-reviewed by an Opus 5 referee (reviews/), then two
opposing-prior Sol xhigh syntheses (SYNTHESIS-*.md). This file is the
magistrate's binding synthesis of the syntheses. Ed's rulings section at
the end supersedes anything here once he answers.

## The adopted arc

1. **P1 — the MVP capstone paper (in flight, draft COMPLETE on main as of
   PR #110).** Data: the three D-117 windows **plus Window C as night 4**
   (both syntheses' top recommendation — §6's six characterization rows
   are the paper's own contribution 4 and currently have no scheduled
   evidence; shipping them empty or descoping is Ed's ruling #1).
2. **P2 — second paper: QUANTIZATION, shrunk to BF16/Q4/Q8** (the
   pragmatics-first pick; referee verdict VIABLE — the only unconditional
   one in the corpus). Three extension nights + 4-8 desk weeks; consumes
   the D-117 Q4 floors DIRECTLY as a rung; BF16-Q4 anchors (guaranteed
   resolvable), Q4-Q8 adjudicates a real open question; an honest refusal
   on adjacent rungs is itself publishable under the project's thesis.
   Kill gates: 2-hour pinned-version conversion smoke BEFORE any D-016
   amendment; off-window Q4-Q8 projection within a week of alpha's floor.
3. **Stretch — MoE re-anchored** (the impact-first pick): Qwen3-30B-A3B
   vs its matched-active dense partner Qwen3-4B (already local) — the
   rank-3 campaign the repo's own mechanism sweep recommended, with the
   novel batch-1 bandwidth-sublinearity thesis. Strictly gated behind the
   seven-desk-gate schedule in SYNTHESIS-IMPACT-FIRST; no night until all
   clear. Spec decode gets ONLY its 2-hour daytime pilot (the repo's own
   smoke predicts spec-on never repays energy — the pilot is nearly free
   and decisive); MTP stays closed (dated AXI-SC verdict); split gets
   only the one-evening GPU-cadence probe.

## Riders into the MVP (night-cheap or free; fund by default)

- **Price-of-never-zero subsection** (desk-only): per-cell floors with and
  without the 0.010818 s bound; does any verdict flip. (rev-drift-thermal)
- **Contamination desk-study** over the ~203 in-custody idle captures:
  P(asymmetric burst > 1 J / > 5 J) over real member durations — feeds §10's
  operational-constraints paragraph with a real number. (rev-contamination)
- **20x time-anchor cautionary figure**: 0.081 J vs 1.649 J on identical
  workloads, pre/post D-078 — free, vivid, on-thesis. (rev-open-explore)
- **Refusal census + denominator** (one desk day) — makes §5's refusal-log
  claims quantitative. (rev-refusal)
- **Single-window KV-context-scaling contrast** (128 vs 4096 context at
  fixed decode; ~2.9x floor on 1.5B): THE candidate for the roadmap's "one
  designed extension" slot if Ed funds a fifth night — cures the
  cross-window custody problem, uses length as the lever, serves the
  original KV/attention goal. Decision rides the scheduling ruling.
  (rev-mvp-icpe move 1 + rev-kv-context strengthening)
- **Interior-chunk noise-limited estimand** (desk + reduction design): the
  project's first noise-limited quantity; methodological extension of the
  attribution-limited finding. (rev-long-generation)
- **Negative-label 3080 Ti demonstration** (zero nights): render the
  deliberately incomplete label for an nvidia-smi measurement — the
  sharpest figure for any reporting/limitations discussion.
  (rev-energy-nutrition move 3)

## Dispositions of the remaining directions (one line each; full arguments in reviews/)

KILLED as papers, salvage noted: mvp-icpe-upgrade (WEAK — its C4/C5 fail
doctrine; its KV move adopted above); wall-meter-validation (WEAK —
unidentifiable on a sealed laptop; re-scoped to an AC-boundary transfer
function IF the loan ever lands; never gates a submission); split-inference
(WEAK/KILL — no cross-device fiducial; cadence probe only);
mtp (KILL — runtime closed by dated verdict; dominated by spec decode);
spec-decode (WEAK — pilot only, K-manipulation rescope if it survives);
attention-variants (WEAK — no admitted checkpoint has the toggle;
context-slope study supersedes); floor-methodology-general (WEAK —
resolvability reframe + held-out floor-validation ladder absorbed into
MVP/Window C); batch-concurrency (WEAK/KILL — headline unfalsifiable;
A4 adapter stays queued desk work); param-scaling (WEAK — denominator
artifact ~29% of its trend); cross-runtime (WEAK — artifact-mismatch
identifiability; afternoon pilot only); drift-thermal (WEAK — is the MVP's
own §4; never-zero subsection adopted); tokenizer-honesty (WEAK — Petrov/
Ahia prior art; M1 ranking-flip night deferred; validator = artifact-track
candidate); prefill-scaling (WEAK — anti-conservative floor transport;
self-flooring 1024 endpoint deferred); kv-context (WEAK as 5-night version;
single-window core adopted above); long-generation (WEAK — comparative
floor unconstructible; interior-chunk estimand adopted);
contamination (WEAK — desk-study adopted, window version dead);
refusal-as-result (WEAK — census + plumbing adopted, paper dead);
energy-nutrition-label (WEAK — schema is the MVP's §6; negative-label demo
adopted); open-explore-registry/repo/contrarian/advisor (their unique
survivals: prefix-reuse boundary reframe kept as a cold idea; §6/Window-C
scope ruling surfaced; everything else duplicated the directed pool).

## Night-budget table (honest, cost-corrected)

| Item | Nights | Status |
|---|---|---|
| D-117 alpha/beta/gamma (MVP claims) | 3 | Ed-adopted; blocked on U1-U3 toolchain |
| Window C (MVP §6 characterization) | 1 | ED RULING #1 |
| Optional: KV-context designed extension | 1 | ED RULING (with #1) |
| Optional: 256-tok prefill contrast | 1 | recommend NO for capstone (both syntheses) |
| P2 quantization BF16/Q4/Q8 | **4** (was 3) | after MVP; kill gates first — see CORRECTION below |
| Stretch MoE | **4** (was 2-3) | desk gates first; Spring-class — see CORRECTION below |

**CORRECTION (2026-08-07, from the Opus re-examination of both gate plans;
full record in `docs/process_traces/2026-08-07-plan-factory/`):** both
second-paper night counts were understated in this adjudication. Quantization
needs a FOURTH conversion arm (the existing Q4 artifact cannot be byte-matched
by construction — it stores non-quantized parameters as F16 and carries no
"mode" key), taking it to 4 nights. MoE needs independent floors for THREE
arms (k=8, k=4, dense) = 150 members, arithmetically unreachable in two
nights, so 4. Both corrections are ED-FACING because night counts are the
budget he rules on. Two binding portfolio rules were also adopted: no
second-paper work touches the mint/pinset/detection_floor file set until U10
closes, and every kill threshold is a multiple of a PROJECTED floor (never a
joule literal, never 1x).

## Ed's rulings (ranked; both syntheses' merged list)

1. **§6/Window C**: fund night 4, or rewrite abstract+contributions+§6 as
   declared future work. RECOMMEND: fund.
2. **Reported-energy cells in alpha/beta**: pre-register reader-facing
   phase-energy means alongside floor cells (no added members) — must be
   decided BEFORE campaign-pack hashes freeze (time-critical, U5/U6).
   RECOMMEND: yes, pending a no-semantics-change check at the pack gate.
3. **Reason-code plumbing before night one** (member_id→reason_code +
   16 shadow codes under the ratified spec). RECOMMEND: yes (urgent).
4. **256-tok prefill arm**: RECOMMEND no for the capstone; the marginality
   is published as prospective sizing evidence.
5. **P2 commitment**: authorize the shrunk quantization posture
   (BF16/Q4/Q8, no Q5/Q6, no internal quality verdict) conditional on the
   conversion smoke; MoE reserves the stretch slot.
6. **Calendar**: capstone/advisor/venue evidence-by dates — needed to
   convert "Fall/Spring" into last-arm dates (six post-data weeks + one
   rerun slot reserved first).
7. **Public-artifact scope** (what evidence may be archived) and the
   wall-meter/second-unit external-coordination choice (RECOMMEND: second
   Apple unit over WT310E if only one; neither gates anything).
