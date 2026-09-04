# Capstone Research-Question Coverage at the Live `_v5` State

**Date:** 2026-09-04

This map applies the fresh audit’s “now / one more collection chain / cut”
test to every canonical identifier in `docs/research_question_registry.md`
and every bank-only identifier carried by the previous coverage map. It does
not change any question’s registry status or claim ceiling.

The source audit is §2 of
`docs/process_traces/2026-09-02-fresh-fable-audit/03-audit-paper-rq.md` at Git
object `d6805473bf868eb076a92a2d4e8fe40ec8c150e6` on
`origin/fix/2026-09-02-decode-identity-set`. D-164 through D-171 provide the
live campaign and process rulings in `docs/decision_log.md`.

## Terms and eligibility

**On disk, diagnostic only** means retained bytes answer the narrow row or
subquestion, but those bytes are not eligible for a production claim. Every
retained measurement corpus predates the current production evidence
generation. A **collection chain** is the ordered desk work, diagnostic runs,
and production windows needed for a governed answer; it may span more than
one evening. **Cut** means the identifier stays in the research program but
is outside the capstone paper.

Prefill is the stage that processes the prompt. Decode is the stage that
emits output tokens. A floor window measures the cell-specific resolution
bound—the largest false energy difference allowed by the fixed measurement
calculation for one model, phase, and energy component. A contrast window
compares the two fixed models. `_v5` is the governed campaign generation for
the pinned Qwen3 1.7B and Qwen3 8B models. The ratio `R` compares the
boundary-widened resolution term with its point-boundary counterpart;
`R_cm` repeats the comparative calculation with timing error shared across a
block.

## Row-by-row map

The evidence column names the on-disk answer, the next data that would answer
the row, or the reason the row is cut. No “on disk” row below is
claim-eligible.

| id | type | capstone disposition | evidence on disk, next data, or cut reason |
|---|---|---|---|
| Q1 | research question | cut | No capstone split-inference collection is assigned. |
| Q2 | research question | cut | No capstone measured-link collection is assigned. |
| Q3 | research question | cut | No capstone split energy-and-latency collection is assigned. |
| Q4 | research question | cut | The predictive shape grid and held-out requests are not in `_v5`. |
| Q5 | research question | cut | The workload-by-model ranking grid is not in `_v5`. |
| Q6 | research question | cut | The current instrument has no whole-system wall-power channel. |
| RQ-METHOD-FLOOR | methodology artifact | on disk, diagnostic only | The retained calibration corpus plus `docs/paper/round7/anchor-correction-quantified.*` and `docs/paper/round7/excursion-decomposition.*` answer how the mechanism behaves. They do not populate a claim-bearing `_v5` cell. |
| C5-1.11 | research question | on disk, partial and diagnostic only | Retained telemetry answers only the observed Apple Neural Engine dark-state subquestion summarized in the bank, not general rail utilization. |
| C5-1.3 | research question | cut | The separate phase-accounting characterization is not in `_v5`. |
| RQ-KV-GROWTH | research question | cut | No capstone chunked key-value-cache growth window is assigned. |
| C5-1.5 | research question | on disk, partial and diagnostic only | Retained recovery tails and cap-hit outcomes answer only the observed cases summarized in the bank; they do not form a recovery curve. |
| C5-1.10 | research question | on disk, partial and diagnostic only | Retained structured failure and refusal outcomes answer only observed frontier cases, not a population frontier. |
| C5-1.7 | research question | cut | No capstone load-versus-resident measurement is assigned. |
| C5-1.9 | research question | cut | Its scored workload belongs to the post-fiducial `_v6` leg, which the fresh audit cuts from this paper. |
| C5-2.5 | research question | cut | No capstone speculative-decoding collection is assigned. |
| RQ-POWER-MODE | research question | cut | No capstone operating-system power-mode collection is assigned. |
| RQ-INTELLIGENCE-PER-JOULE | research question | cut | The question remains killed; the required general-intelligence denominator and correctness policy do not exist. |
| RQ-AUDITABLE-EVIDENCE | capability claim | on disk, diagnostic only | Strict-valid bundles and their evidence chain support the limited capability recorded in `docs/run_reports/2026-07-06-slice-2i-first-real-energy.md`; independent public re-reduction remains open. |
| RQ-QWEN25-SMOKE | capability claim | on disk, diagnostic only | `docs/run_reports/2026-07-06-slice-2i-first-real-energy.md` answers only the named Qwen2.5 stack and workload. |
| RQ-QWEN35-SMOKE | capability claim | on disk, diagnostic only | `docs/run_reports/2026-07-07-flagship-qwen35-122b.md` answers only the named Qwen3.5 stack and workload. |
| RQ-TWO-MODEL-ACTIVE-NONCLAIM | capability claim | on disk, diagnostic only | The two smoke reports answer the row negatively: the observations are confounded and cannot establish active-parameter scaling. |
| RQ-SHORT-PREFILL-RESOLVABILITY | methodology artifact | on disk, diagnostic only | `docs/process_traces/2026-08-09-prefill-phase-proof/` supplies DG-067, DG-068, DG-069, DG-076, and DG-077; `docs/paper/round7/dg071-dg075-statistics.*` issues the record-timing inputs. Together they support the printed `not resolvable` result. |
| RQ-MLX-KV-REPLAY | capability claim | on disk, diagnostic only | `docs/run_reports/2026-07-07-resume-merge-session.md` supports replay feasibility only for the named machine and software stack. |
| RQ-MAC-BASELINES | capability claim | cut | No capstone multi-profile baseline collection is assigned. |
| RQ-SHAPE-ENERGY | research question | cut | The required prompt-and-output shape grid is not in `_v5`. |
| C5-1.1 | research question | next collection chain | The governed `_v5` floor and contrast transaction would answer only the fixed Qwen3 8B-versus-1.7B pairwise demonstration. It would not answer the unresolved D-163 ladder extension. |
| C5-1.2 | research question | cut | No capstone context-length ladder is assigned. |
| C5-1.4 | research question | cut | No capstone frequency-residency warning-rule collection is assigned. |
| C5-1.6 | research question | cut | The post-floor shortlist names this option but assigns no capstone window. |
| C5-1.8 | research question | cut | The post-floor shortlist names this option but assigns no capstone window. |
| C5-1.12 | research question | cut | The post-floor shortlist names this option but assigns no capstone window. |
| C5-W.1 | research question | cut | No capstone category-at-fixed-shape collection is assigned. |
| C5-W.2 | research question | cut | No capstone reasoning-mode collection is assigned. |
| C5-W.3 | research question | cut | No capstone workload-category ranking grid is assigned. |
| C5-I.3 | research question | cut | No capstone multilingual fertility collection is assigned. |
| C5-I.1 | research question | cut | Its scored benchmark evidence belongs to the post-fiducial `_v6` leg. |
| C5-I.2 | research question | cut | No capstone published-difficulty collection is assigned. |
| C5-I.4 | methodology artifact | cut | No capstone external-runner overhead collection is assigned. |
| C5-I.5 | research question | cut | No capstone prompt-template comparison is assigned. |
| RQ-CONTENT-SENTINEL | research question | cut | No capstone fixed-shape content-sentinel collection is assigned. |
| RQ-ENERGY-VARIANCE | research question | cut | No capstone repeated stochastic-sampling collection is assigned. |
| RQ-SESSION-SHAPE | research question | cut | No capstone realistic-session composition collection is assigned. |
| RQ-ORDER-POSITION | methodology artifact | cut | The dedicated position-effect analysis remains proposed. |
| RQ-ATTRIBUTION-DOMINANCE | research question | next collection chain | The `_v5` alpha and beta floor windows plus gamma contrast, followed by the D-168 close-out, would answer the primary question. G2-a, the desk day, and G2-b precede the claim-bearing transaction. No `_v5` result is on disk. |
| RQ-CACHE-PREFIX | research question | cut | No capstone cache-policy and prompt-length collection is assigned. |
| RQ-AXI-HYBRID-PAIR | research question | cut | No capstone controlled hybrid-versus-transformer pair is assigned. |
| RQ-EXTERNAL-MARKED-RUNNER | capability claim | cut | No capstone marked-runner implementation and local collection is assigned. |
| RQ-HUMANEVAL-IMPORT-SMOKE | capability claim | cut | No capstone frozen HumanEval import smoke is assigned. |
| C5-2.1 | research question | cut | No capstone cross-stack quantization collection is assigned. |
| C5-2.2 | research question | cut | No capstone batch-size collection is assigned. |
| C5-2.3 | research question | cut | No capstone two-endpoint key-value-cache transfer collection is assigned. |
| C5-2.4 | research question | cut | No capstone end-to-end quantized-cache transfer collection is assigned. |
| C5-2.11 | research question | cut | No capstone on-device quantized-cache collection is assigned. |
| C5-2.6 | research question | cut | No capstone request-coalescing collection is assigned. |
| C5-2.7 | research question | cut | No capstone cross-device ranking collection is assigned. |
| C5-2.8 | research question | cut | No capstone split-placement validation is assigned. |
| C5-2.9 | research question | cut | No capstone wall-and-transfer crossover study is assigned. |
| C5-3.1 | research question | cut | A second comparable machine is outside the capstone. |
| C5-3.2 | research question | cut | Battery-path instrumentation is outside the capstone. |
| C5-3.3 | research question | cut | Cross-platform adapter and device work is outside the capstone. |
| C5-3.4 | capability claim | cut | Phone-class feasibility work is outside the capstone. |
| C5-3.5 | methodology artifact | cut | Cross-laboratory replication is outside the capstone. |
| C-023-TELEMETRY-PERTURBATION | methodology artifact | cut | No capstone telemetry-on/off comparison is assigned. |
| C-023-VERSION-DRIFT | research question | cut | No capstone pinned before-and-after version collection is assigned. |
| C-023-MARKER-JITTER | methodology artifact | cut | No capstone marker-and-sampler-phase sensitivity study is assigned. |
| C-023-OUTPUT-IDENTITY | methodology artifact | cut | This remains a binding gate for future comparisons, not a capstone question. |
| C-023-IDLE-STATIONARITY | methodology artifact | cut | This remains a future sensitivity check; gross energy stays primary. |
| C-023-QUALITY-EQUIV-QUANT | research question | cut | This remains a future quantization-comparison gate. |
| C-023-COEFF-TRANSPORT | research question | cut | No capstone realistic-workload holdout study is assigned. |
| APP-PROMPT-PROFILER | application idea | cut | Application idea, not a capstone research question. |
| APP-BUNDLE-POWER-BUG | application idea | cut | Application idea, not a capstone research question. |
| APP-CI-ENERGY-GATES | application idea | cut | Application idea, not a capstone research question. |
| APP-VENDOR-PRESS-AUDIT | application idea | cut | Application idea, not a capstone research question. |
| APP-MODEL-CARDS | application idea | cut | Application idea, not a capstone research question. |
| APP-TEACHING-INSTRUMENT | application idea | cut | Application idea, not a capstone research question. |
| APP-STANDARDS-CONTRIBUTION | application idea | cut | Application idea, not a capstone research question. |
| APP-CARBON-LABELS | application idea | cut | Application idea and remains killed. |
| APP-BATTERY-RUNTIME | application idea | cut | Application idea and remains killed. |
| APP-LOCAL-CLOUD-ROUTING | application idea | cut | Application idea and remains killed. |
| C5-1.13 | research question; bank-only rider absorbed by C5-1.8 | cut | No capstone same-silicon runtime-and-kernel comparison is assigned. |
| C5-2.10 | research question; bank-only rider absorbed by Q6 | cut | The current instrument has no whole-system wall-power channel. |
| C5-2.12 | research question; bank-only rider absorbed by RQ-KV-GROWTH and C5-1.2 | cut | No capstone bounded-versus-unbounded cache-policy collection is assigned. |
| C5-2.13 | research question; bank-only rider absorbed by RQ-CACHE-PREFIX and RQ-MLX-KV-REPLAY | cut | No capstone save-load-recompute energy crossover is assigned. |
| C5-2.14 | research question; bank-only rider absorbed by Q4 | cut | No capstone cache-policy coefficient stress test is assigned. |
| C5-2.5a | research question; bank-only rider absorbed by C5-2.5 | cut | No capstone cross-method speculative-decoding comparison is assigned. |
| C5-2.5b | research question; bank-only rider absorbed by C5-2.5 | cut | No capstone proposal-length collection is assigned. |
| C5-2.5c | research question; bank-only rider absorbed by C5-2.5 | cut | No capstone speculative-decoding break-even collection is assigned. |
| C5-2.5d | research question; bank-only rider absorbed by C5-2.5 | cut | No capstone lookup-contamination comparison is assigned. |
| C5-W.4 | research question; bank-only rider absorbed by C5-I.3 | cut | No capstone semantically matched multilingual collection is assigned. |

## Non-registry paper obligations

These are in the fresh audit’s “one more window” table but are not additional
registry rows, so they do not change the row count above.

| obligation | next evidence | capstone status |
|---|---|---|
| Pulse-to-inference transfer assumption | `TRANSFER-FIDUCIAL-01`: a known gap inserted into real inference work, with both edges fitted by the existing estimator and the residual compared with the pulse-derived bound. | Diagnostic only; post-campaign; cannot support a claim. |
| Workload response characterization | A separate characterization collection using the registered `metrology_v1` shape. | Retained in paper §3; outside `_v5`; uncollected. |
| Identical-condition null characterization | A bounded null folded into the floor windows or a separate characterization collection. | Retained in paper §3; outside `_v5`; uncollected. |
| Phase-accounting characterization | A separate characterization collection using the registered `metrology_v1` shape. | Retained in paper §3; outside `_v5`; uncollected. |
| Drift-and-recovery characterization | A separate characterization collection using the registered `metrology_v1` shape. | Retained in paper §3; outside `_v5`; uncollected. |

The magistrate ruling keeps all four characterizations in paper §3. Their
status is therefore explicit rather than optional: none is part of `_v5`, and
none has been collected. The bounded identical-condition null may share a
floor window or use a separate characterization collection without changing
that paper obligation.

## Totals and reading rule

The map contains 89 identifier rows: 79 canonical registry rows and 10
bank-only riders. Ten rows have diagnostic or partial answers on disk, two
rows require the next governed `_v5` collection chain, and seventy-seven are
cut from the capstone. These are table counts, not scientific observations.

The two retained capstone questions are deliberately narrow.
`RQ-ATTRIBUTION-DOMINANCE` asks whether the registered boundary-widening
ratios meet the D-165 rule in every required `_v5` cell. `C5-1.1` asks only
for the fixed pairwise Qwen3 demonstration. Neither is answered today. The
post-campaign transfer fiducial can test whether the calibration bound carries
from pulses to inference, but D-167 keeps it diagnostic and non-claim-bearing.

D-169 and D-171 permit an unattended operating path once its gates are met;
they do not make a window collected. D-170’s executed-evidence duty means a
future state change must point to an execution record or code-path proof,
rather than inferring that an artifact exists. Until those records exist,
this map keeps the two `_v5` rows in the next-collection category.
