# Project Status History

Historical snapshots; non-operative; current status lives in
`PROJECT_STATUS.md`; dated evidence lives in run reports.

## Update Ledger

| date | what changed |
|---|---|
| 2026-09-01 | The live work selector was reconciled to the Qwen3 `_v5` chain; the results-fill registry was regenerated; a fresh-model whole-repository review launched the paper skeleton, dependence, timing-marker, close-out, and probe-configuration follow-ups. |
| 2026-08-30/31 | The Qwen3 plan preparation completed adversarial review; exact model and tokenizer identities, the two-times dominance rule, and the four-rung checked selector were pinned. |
| 2026-08-28 | Ed selected Qwen3-1.7B-4bit and Qwen3-8B-4bit; three blind reviewers prompted the pre-data tightening of the paper's pass/fail rule. |
| 2026-08-20 | The predecessor campaign preparation passed its review gates and merged; its model family was later superseded, while the repaired instrument and frozen-design discipline remained. |
| 2026-08-15/16 | A readiness review refused measurement, converted every finding into repair work, and the mergeable repair program then landed. |
| 2026-08-13 | The predecessor three-pack campaign froze successfully; those packs are retained as process evidence but are not the current Qwen3 campaign. |
| 2026-07-30/31 | The first floor artifact and a passed head-to-head diagnostic demonstrated the governed path; later decisions made both non-claim-bearing and required prospective replacement. |
| 2026-07-25/26 | The repaired screening and uncertainty-budget rules merged, and the first post-repair windows passed. |
| 2026-07-22 | The defective trace-time anchor was repaired and verified end to end. |
| 2026-07-19 | The soundness audit voided all pre-repair energy values and defined the repair. |
| 2026-07-17/18 | The environment guard and exploratory runtime evidence landed; their pre-repair energy values are historical and void. |
| 2026-07-09 | A whole-project review found reader-facing claim drift and analysis gaps; the advisor status view remained repository-backed. |
| 2026-07-07/08 | Source-identity tracking, statistical uncertainty, contamination detection, telemetry, campaign automation, the mock-first NVIDIA stack, and a cache-replay feasibility result landed through reviewed streams. |
| 2026-07-06 | The MLX plus `powermetrics` Mac path first produced strict-valid hardware bundles; its pre-repair energy values were later voided. |
| 2026-06-12 | The mock vertical slice proved the typed-config-to-auditable-bundle path before hardware measurement. |

## Evolution From The Original Architecture Sketch

| original sketch | current position | reason |
|---|---|---|
| YAML or JSON configuration | normalized, sorted-key JSON; YAML deferred | stable hashing with a zero-dependency core |
| likely Pydantic schemas | standard-library data classes with the same contract | the core runs without optional packages |
| implement Mac first | deterministic mock vertical slice first, then Mac | prove controller and arithmetic before real telemetry can confound them |
| file-backed dashboard, perhaps a database later | static HTML and analysis files; no database planned | smallest tool that supports inspection and progress reporting |
| offline cache replay before live splitting | three-stage ladder: synthetic transfer, then offline replay, then an optional live split | cache representations are not generally portable across runtime engines |
| schedule cross-device pairs directly | require feasibility evidence before borrowed-hardware scheduling | bounds the largest execution risk and preserves a synthetic fallback |
| measurement boundaries mostly implicit | boundaries, clock discipline, uncertainty, and controller effects explicit | required for defensible physical energy comparisons |

The original controller-and-adapter architecture remains coherent. The changes
above strengthen evidence and bound feasibility risk rather than changing the
capstone into a different system.

## Process Note

Historical snapshot. `docs/orchestration.md` owns the current procedure.

The project is developed by a human researcher directing a reviewed,
multi-model engineering workflow. Ed owns research direction, physical machine
operation, external access, and final authorization of claim-bearing
collection. A designated lead owns decomposition, design rulings, final diff
review, verification, and integration. Separate implementers and reviewers use
distinct perspectives so that an assumption shared by code and its first test
does not become unchallenged evidence.

Consequential changes—measurement physics, pre-registration, evidence
identity, and paper-claim rules—receive deeper independent review than routine
bookkeeping. Raw evidence is immutable, review findings receive explicit
dispositions, and no agent performs final live-hardware verification on behalf
of the human operator. The 2026-09-01 fresh-model review is an example: it
found a stale live-work selector, missing close-out ownership, a frozen draft
that names the retired campaign, and dependence wording that needed a dedicated
sensitivity analysis. The work selector and ownership question are now decided
and recorded, while the follow-up code and paper work remain visibly in flight.
The earlier review by three independent reviewers on 2026-08-28 separately
found and repaired the nearly unfalsifiable headline rule before data existed.

Each fact has one owning artifact: decisions in `docs/decision_log.md`, live
work state in `docs/process/state_kernel.json`, deliberation in
`docs/council_log.md`, session evidence in `docs/run_reports/`, and raw
scientific evidence in immutable bundles. The complete operating model is in
`docs/orchestration.md`.

**Where to look.** Start with `RUN_STATE.md` for live status, this document for
the advisor view, `docs/process/v5-artifact-flow.md` for the current mechanism,
and `docs/decision_log.md` for binding choices. Front-facing changes update
`docs/site/DRIFT.md`; Ed deploys the status site manually.
