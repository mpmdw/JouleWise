# Extension-axes roadmap synthesis (Sol xhigh, 2026-07-17; re-run after placeholder defect — prior stub superseded)

## Findings

### F1 — §1–§2. Ranking and earliest realistic phase

Ranking discounts duplication and confounding, not merely implementation time. Phase key: **PF** post-floors exploratory; **NV** NVIDIA leg; **NS** needs new subsystem; **PC** post-capstone.

| # | Candidate | Phase | Research return / cost |
|---:|---|---|---|
| 1 | [C5-2.5c](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:123) | PF | Direct Q4 break-even; reuses AXI-SA. |
| 2 | [C5-2.11](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:43) | PF | Mac-runnable KV stress; transfer gates removed. |
| 3 | [RQ-AXI-HYBRID-PAIR](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:173) | PF | Distinct mixer stress; feasible named pair. |
| 4 | [C5-2.5b](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:117) | PF | Realized proposal work enters Q4. |
| 5 | [C5-2.12](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:49) | PF | Runnable marginal-slope test. |
| 6 | [C5-2.13](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:55) | PF | Promotes an existing L1 replay result. |
| 7 | [C5-2.14](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:61) | PF | Thesis-direct coefficient rider. |
| 8 | [C5-2.5d](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:129) | PF | Cheap, necessary contamination control. |
| 9 | [C5-2.5a](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:111) | NS | Valuable, but needs prospective cross-method design. |
| 10 | [RQ-AXI-ATTN-CONTEXT-SLOPE](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:179) | PF | Cheap; largely duplicates context/KV rows. |
| 11 | [C5-3.3 provenance rider](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:95) | PC | Capture provenance now; AMD science later. |
| 12 | [RQ-KV-POOL-OBSERVABLES](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:67) | PF | Runnable, but correlation-only/expected-null. |
| 13 | [C5-SF.3](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:21) | PF | Runnable null, not sparse execution. |
| 14 | [C5-2.5/MECHANISM](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:148) | NS | Strong mechanism question; no runtime. |
| 15 | [C5-SF.4](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:27) | NS | Identifiability guard, not empirical enrichment. |
| 16 | [C5-2.7 kernel rider](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:83) | NV | Existing row; boundary/device confounded. |
| 17 | [C5-1.13/C5-1.8 rider](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:89) | NV | Existing stack comparison; adapter burden. |
| 18 | [RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:191) | NS | Existing cadence guard already suffices. |
| 19 | [C5-SF.1](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:9) | NV | Stack-confounded; PowerInfer support **NEEDS-WEB**. |
| 20 | [C5-2.5/MTP-MAC](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:142) | NS | Pinned MLX strips heads; newer path **NEEDS-WEB**. |
| 21 | [RQ-AXI-ATTN-KERNEL-AB](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:185) | NS | Kernel, not mechanism; llama.cpp adapter absent. |
| 22 | [C5-SF.2](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:15) | NS | Counter existence **NEEDS-WEB** and unverifiable. |
| 23 | [C5-2.5/MTP-DEPTH](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:154) | NS | No runtime; counting semantics also missing. |

“PF” does not mean claim-ready: the published corpus remains claim-evidence-flagged and P2-037 adjudication is pending. Effects must clear the applicable request/phase floor before L2 wording. [Current floor posture](/Users/edr/code/JouleWise/PROJECT_STATUS.md:31).

### F2 — §3. Fold-in plan

D-055 makes the bank deliberative and the registry the canonical live index; D-070 specifically locates C5 deliberation in the bank and RQ/C-023 state in the registry. [D-055](/Users/edr/code/JouleWise/docs/decision_log.md:2884), [D-070](/Users/edr/code/JouleWise/docs/decision_log.md:3712).

- `docs/research_question_bank.md`:

  - Amend existing `C5-2.5` with `C5-2.5c` as primary Q4 rider, `C5-2.5b` as its proposal-work secondary, and `C5-2.5d` as a mandatory control—not a separate question.
  - Mint `C5-2.11` for on-device quantized-KV energy. Attach it to existing `C5-2.4`, `C5-1.12`, and `C-023-QUALITY-EQUIV-QUANT`.
  - Record `C5-2.12` under `C5-1.2`/`RQ-KV-GROWTH`, `C5-2.13` under `RQ-CACHE-PREFIX`/`RQ-MLX-KV-REPLAY`, and `C5-2.14` under `Q4/AP-1`; do not mint three more independent theses.
  - Add provenance-only amendments to `C5-1.8`, `C5-2.7`, and `C5-3.3`.

- `docs/research_question_registry.md`:

  - Add one new canonical row: `RQ-AXI-HYBRID-PAIR`, candidate, L2 named-pair ceiling, floor-gated.
  - Index new `C5-2.11`; add `C5-2.5b/c` as aliases/riders on existing `C5-2.5`, with `C-023-OUTPUT-IDENTITY` as a binding gate.
  - Update notes/aliases on `C5-1.2`, `RQ-KV-GROWTH`, `RQ-CACHE-PREFIX`, `RQ-MLX-KV-REPLAY`, `Q4`, `C5-1.8`, `C5-2.7`, and `C5-3.3`.
  - Attach the module-attribution nonclaim to `RQ-SHORT-PREFILL-RESOLVABILITY`/`RQ-METHOD-FLOOR`; do not create another methodology row.

Proposed one-line intake entry:

`| D-075 | Extension-axis intake: admit C5-2.5 break-even/proposal-K riders, C5-2.11 on-device KV quantization, and RQ-AXI-HYBRID-PAIR; attach cache/kernel/cadence refinements to existing rows; defer runtime-unsupported or duplicate candidates | proposed — Ed ruling required |`

### F3 — §4. Highest-value additions and do-not-fold list

Top three:

1. `C5-2.5c`: the cleanest directly runnable test of whether drafter fixed cost and acceptance-dependent work explain speculative-decoding energy.
2. `C5-2.11`: a presently runnable Mac question that converts existing KV machinery into a narrow Q4 marginal-work stress test.
3. `RQ-AXI-HYBRID-PAIR`: the only addition that broadens architectural science beyond the already-committed MoE axis without demanding module-level attribution.

Not worth folding as standalone rows:

- `C5-SF.1–.4`: no Mac sparse kernel, NVIDIA feasibility **NEEDS-WEB**, and dynamic counters lack a harness-verifiable conservation rule.
- All three native-MTP suggestions: the pinned runtime cannot execute the heads, while existing `C5-2.5` and native-MTP AP surfaces already preserve the future question.
- `RQ-KV-POOL-OBSERVABLES`: correlation cannot support the proposed allocator-design inference.
- `RQ-AXI-ATTN-KERNEL-AB`: duplicates runtime attribution and first requires another adapter.
- `RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM`: preserve as an existing-row guard.
- `C5-2.5a`: defer until a separate prospective cross-mechanism contrast is affordable.
- Kernel-provenance candidates and `C5-2.12–.14`: retain as amendments/riders, not independent questions.

## Residual risk

The evaluation’s **NEEDS-WEB** items remain open: DFlash on Ampere, DSpark/vLLM status, maintained PowerInfer support, newer MLX/native-MTP execution, sparse-attention execution, controlled hybrid-pair availability, and CUDA model-fit details. None should become a capstone commitment until its named feasibility gate is resolved.