# Suite next-layer specs

Status: draft specs only. No implementation is authorized by this packet.
Date: 2026-07-08.

These specs cover the next layer around the shipped JouleWise suite substrate:

- `checkpoint_metrics_spec.md`: suite checkpoint and envelope-gate metrics.
- `prompt_sequencing_spec.md`: prompt/workload sequencing, sidecars, and
  campaign order policy.
- `next_observer_spec.md`: observer/observatory surfaces for suite evidence.
- `instruction_tuning_spec.md`: instruction-style behavior suite extensions.
- `decision_review_log.md`: draft decisions, rationale, review notes, and
  counter-review prompts for future models.

The suite substrate itself is already implemented and merged as of the
2026-07-08 suite build session. This packet therefore does not re-specify
`run_suite`, marker vocabulary, `suite_manifest.json`, or
`outputs/suite_items.jsonl` from scratch. It defines how later work should use
those surfaces.

## Ground rules

- Specs are documentation and planning artifacts only.
- The active queue still has `RESUME-CP5` as a P0 safety row. These specs must
  not be read as permission to skip that checkpoint sequence.
- Private chain-of-thought is not recorded here. The auditable substitute is
  explicit rationale: options considered, chosen direction, rejected
  alternatives, evidence pointers, and revisit triggers.
- Public/generated observer surfaces must not quote raw deliberation,
  reviewer rationale, or agent reasoning text from process logs. They may parse
  structured status fields and link to source records.
- Draft choices in this packet are not canonical `D-NNN` decisions until a
  later session promotes them into `docs/decision_log.md` or a contract doc.
- New suite work must preserve the generic suite mechanism: no bespoke
  marker/window plumbing for individual workloads.

## Existing anchors

- Suite build report: `docs/run_reports/2026-07-08-suite-build.md`.
- Suite science expansion: `docs/run_reports/2026-07-08-suite-science-expansion.md`.
- Run-bundle contract: `docs/contracts/run_bundle_layout.md`.
- Adapter contract: `docs/contracts/adapter_contracts.md`.
- Analysis plans: `docs/contracts/analysis_plans.md`.
- Claims ladder: `docs/contracts/claims_ladder.md`.
- Queue and current pause: `TASK_QUEUE.md`, `RUN_STATE.md`.

## How later agents should use this packet

1. Read `RUN_STATE.md` and `TASK_QUEUE.md` first.
2. If `RESUME-CP5` is still active, finish it before implementing from these
   specs.
3. For any implementation, promote only the relevant draft decisions into the
   canonical decision log or contract docs.
4. Before campaign execution, run a fresh counter-review over the specific
   promoted decisions and the exact code diffs.
5. Keep bundle validation, floor gates, and analysis-plan claim ceilings ahead
   of any reader-facing claims.
