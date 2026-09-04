# JouleWise: Project Status, Plan, And Architecture

Audience: capstone advisor. This is the compact current view. Historical
updates and retired process prose are preserved in
`docs/project_status_history.md`; live work selection remains in the generated
regions of `RUN_STATE.md` and `TASK_QUEUE.md`, sourced from
`docs/process/state_kernel.json`.

## Current Claim And Scope

JouleWise is an auditable instrument for measuring energy and latency during
local large-language-model inference on named hardware, runtime, model,
workload, and telemetry stacks. Its capstone contribution is the governed
measurement path: immutable run bundles, explicit physical boundaries,
read-only re-reduction, uncertainty and detection-floor rules, and mechanical
refusal when evidence cannot support a claim. The binding headline and minimum
viable stop line are in `docs/contracts/capstone_scope.md`.

The current prospective campaign compares
`mlx-community/Qwen3-1.7B-4bit` and `mlx-community/Qwen3-8B-4bit` with MLX on
one Apple M3 Max. It uses the internal label `_v5` and was fixed by D-164
through D-167. No claim-bearing `_v5` data exist yet, so this page makes no
energy or model-ranking claim from that campaign. The final paper may report a
positive, negative, unresolved, or refused result without weakening the
instrument contribution.

The paper is metrology-centered. It asks whether measurement boundaries are
placed correctly in time, repeat runs agree, and drift, linearity, additivity,
and detection limits are controlled well enough for a same-boundary model
comparison. Split inference and remote-device work remain optional,
feasibility-first extensions; they are not required for a defensible capstone.
Claims remain stack-specific unless independent replication and calibrated
boundary evidence justify broader language.

## Measured Evidence

The typed-config-to-run-bundle path has executed on deterministic mock adapters
and on the Apple M3 Max with MLX and `powermetrics`. Strict validation rebuilds
recorded power traces and summaries from raw bytes and refuses inconsistent
bundles. That proves artifact consistency; it is not, by itself, proof that a
physical measurement is correctly attributed.

Every energy value collected before the time-anchor repair is permanently
void for claim use. Those preserved corpora document a real defect: power
readings and workload events used different clocks, so the old join could
integrate the wrong part of a trace. The repair, its prospective controls, and
the no-revival fence are owned by D-078 and
`docs/reviews/2026-07-19-measurement-soundness-audit.md`.

Post-repair windows demonstrated that the screened, bracketed instrument path
can complete on real hardware, but predecessor results do not substitute for
the Qwen3 campaign. The repaired instrument is attribution-limited at roughly
1 joule: boundary-placement uncertainty of about 0.7–1.0 J per run exceeds
repeatability noise of about 0.29–0.49 J on roughly 50 J observations. The
floor and the claim-side interval each retain that attribution term, making the
effective clearable phase contrast roughly 5 J rather than the floor alone.
These quantities are instrument-characterization evidence under D-078 clause
11, not `_v5` model results.

Retained bundles and corpora are immutable. Failed or refused attempts remain
in custody; retries and supersession follow recorded rules rather than silently
replacing inconvenient evidence.

<!-- ADVISOR-PAGE-END -->

## Gate Matrix

This matrix states the scientific sequence, not an agent-ranked work list.
`RUN_STATE.md` and the state kernel decide whether a step is currently open.

| Gate | Required evidence | Effect of failure | Owner |
|---|---|---|---|
| Unattended infrastructure | A resident supervisor enforces stand-down and each night plan is pinned to the dedicated measurement checkout. | No real window is armed. | D-169, D-171; `docs/milestones.md` |
| G2-a diagnostic probe | A calibrated bracket; at least five small-model members at each of 512, 1,024, 2,048, and 4,096 prompt tokens; preserved selector input. | The probe is preserved and the registered prefill refusal applies; it never becomes claim evidence. | D-166; state-kernel `V5-G2A-PREFILL-PROBE-01` |
| Desk freeze | Checked rung selection, its evidence hash, three generated `_v5` packs, byte-stable regeneration, and fresh-checkout proof. | Packs do not advance to the machine. | D-162, D-167; `V5-DESK-DAY-01` |
| G2-b shakedown | One real-pack small/large/large/small block, complete bracket and verdict, desk check, and exactly the registered incomplete-campaign refusal. | Preserve the attempt and stop; do not retry into success. | D-162, D-167; `V5-G2B-SHAKEDOWN-01` |
| Transaction opening | Cold-gate-adjudicated readiness at the G2-b-proved head. D-171 delegates GO to the magistrate's gate, so Ed is not a per-window operator. | Claim-bearing collection remains closed. | D-171; `V5-TRANSACTION-01` |
| Nightly G3 | Each immutable campaign night passes the same read-only checker before another arm runs. | The next arm stays blocked pending governed disposition. | D-162, D-167; `V5-NIGHTLY-G3-01` |
| Issue and close out | Strict validation, authenticated per-cell floor inputs, mint, finalized manifest, eight ordinary dominance ratios, four comparative shared-shift ratios, and exact claim verdicts. | Missing, unauthenticated, or zero-denominator inputs license no paper branch. | D-165, D-168; `docs/contracts/d165_dominance_closeout.md` |
| Results fill | Only authenticated values and pre-written branch sentences requested by the 126-key successor registry. | No hand-filled numerical or dominance claim. | `docs/paper/results-fill-registry.md` |

The dominance sentence has a pre-registered falsifier: the timing-aware floor
divided by the naive floor must be at least two in all eight ordinary cases,
and all four comparative shared-shift replays must also clear two. A failed
shared-shift replay withdraws the sentence; it does not invite a revised
threshold (D-165 and D-168).

## Artifact State

| Artifact | Current state | Remaining evidence |
|---|---|---|
| Instrument and run-bundle contract | Runnable on mock and Mac; strict validation, reduction, and structured refusal exist. | Remote NVIDIA and Jetson promotion requires live device evidence. |
| Measurement method | Repaired time anchor, bracketed screening, uncertainty propagation, immutable evidence, and gross-energy headline basis are specified. | Observe the registered rules on the complete `_v5` campaign. |
| Qwen3 `_v5` plan | Model identities, tokenizer relationship, thinking-off decode policy, forced 512-token output, four-rung prefill selector, and dominance criterion are fixed. | Measured rung selection, final packs, and fresh-checkout proof. |
| Machine-to-paper chain | Probe, desk, shakedown, transaction, nightly checking, floor, close-out, and fill interfaces are mapped in `docs/process/v5-artifact-flow.md`. | Complete the open implementation gates before their first production use. |
| Paper | The first draft is a frozen historical baseline; the successor fill registry defines permitted values and branch sentences. | Prospective campaign artifacts, final prose, figures, limitations, and claims audit. |
| Optional extensions | Synthetic transfer and offline cache replay have a feasibility-first route. | Live split or remote-hardware evidence only if schedule and gates permit. |

The architecture remains one typed controller composed with transport, runtime,
and telemetry adapters. Each run writes a self-contained bundle of normalized
configuration, environment and stack identity, lifecycle events, raw telemetry,
model output, and derived summaries. Detailed design belongs in
`docs/contracts/`, the phase plans, and the implementation—not in this status
page.

## Advisor Decisions And Risks

The repository does not record the final-report deadline or colloquium date.
Those are the only calendar inputs this page asks the advisor or program to
supply; internal cut dates must be derived after they are known. The
metrology-centered scope and minimum viable artifact are already governed by
D-091 and `docs/contracts/capstone_scope.md`. The current calendar record is
`docs/milestones.md`.

| Risk | Current posture |
|---|---|
| No claim-bearing Qwen3 data yet | Preserve the fixed sequence and write no result before authenticated artifacts exist. |
| Probe overlap is insufficient | Keep every probe and issue the registered refusal instead of lowering the count floor. |
| A night is contaminated or a gate fails | Fail closed, preserve evidence, and require a governed disposition; no silent retry. |
| Timing attribution does not dominate repeatability by two | Use the pre-written non-dominance branch; the instrument result remains reportable. |
| Dependence changes the ten-block direction inference | Complete the registered sensitivity analysis and narrow wording if required. |
| Remote access or cache replay fails | Use synthetic-transfer evidence or omit split inference; neither blocks the core capstone. |
| Calendar input arrives late | Protect the Mac instrument, authenticated campaign chain, claim audit, report, and presentation before optional breadth. |

The minimum viable outcome is a trustworthy, reproducible measurement
instrument plus a governed Apple-Silicon characterization with honest positive,
negative, unresolved, or refused results. A single physical unit supports only
claims about its named stack.

## Next Milestone

The next scientific milestone is the G2-a prompt-length record, but it is not
simply “one instrumented evening waiting on Ed.” The unattended supervisor and
measurement-checkout plan pin precede it. Once those live gates open, the
driver may run the bracketed diagnostic without Ed at the keyboard, while all
agent processes stand down for the quiet interval. The result selects the
shortest qualifying prefill length; it cannot support a model-energy claim.

After G2-a, the desk day freezes the selection into the three campaign packs,
then G2-b proves the real-pack path. The magistrate's cold-gate readiness
decision opens the transaction under D-171. Collection proceeds through
nightly G3 checks, followed by floor issuance, finalization, dominance and
claim close-out, and controlled results filling. This document promises that
sequence, not dates. Live status is in `RUN_STATE.md`.

## Evidence Links

| Question | Owning evidence |
|---|---|
| What claim is permitted? | `docs/contracts/capstone_scope.md`; `docs/contracts/claims_ladder.md` |
| Which work may run now? | `RUN_STATE.md`; `docs/process/state_kernel.json`; generated Current Queue in `TASK_QUEUE.md` |
| Why are old energy values void? | D-078 in `docs/decision_log.md`; `docs/reviews/2026-07-19-measurement-soundness-audit.md` |
| What exactly will the Qwen3 campaign do? | D-164 through D-168; `docs/process/v5-artifact-flow.md`; `configs/campaigns/d117_contrast_v5/` |
| How are measurements and claims governed? | `docs/contracts/measurement_methodology.md`; `docs/contracts/analysis_plans.md`; `docs/paper/results-fill-registry.md` |
| What remains risky or externally constrained? | `docs/risk_register.md`; `docs/milestones.md` |
| Where is historical status prose? | `docs/project_status_history.md`; dated files under `docs/run_reports/` |

Update this page only when an advisor-visible gate, verdict, campaign step, or
claim boundary changes. Keep volatile ranks, dates, and test state in their
owners. Under D-136 the site lane is retired from routine sessions: agents do
not refresh, regenerate, or deploy it. `docs/site/DRIFT.md` is retained only as
a reference for an Ed-chosen manual workflow dispatch; Ed deploys any resulting
snapshot.
