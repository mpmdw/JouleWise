# Suite next decision and review log

Status: draft audit log for this spec packet. These are not canonical
`D-NNN` decisions until promoted.

## Draft decisions

### SN-001: Checkpoint metrics are derived analysis artifacts

Decision: suite checkpoint verdicts should be separate deterministic analysis
artifacts, not reducer fields and not prose-only run-report claims.

Options considered:

1. Add workload-specific checkpoint fields directly to `summary_metrics.json`.
2. Put checkpoint verdicts only in run reports.
3. Emit deterministic checkpoint JSON derived from strict-valid bundles.

Chosen: option 3.

Rationale: checkpoint logic is workload-specific, while the reducer is generic.
Machine-readable JSON gives future tools and reviewers a stable surface without
making run bundles carry every downstream analysis.

Revisit when: post-hoc analysis artifacts need an official bundle layout.

### SN-002: Manifest order is the execution truth until a real policy lands

Decision: specs must say `manifest_order` unless item reordering is implemented
through per-repetition manifests, campaign-level config ordering, or a real
runtime execution policy.

Options considered:

1. Let `order_seed` imply runtime reordering.
2. Generate per-repetition manifests or use campaign-level order manifests.
3. Implement a new runtime order policy.

Chosen: option 2 for near-term work; option 3 remains possible later.

Rationale: the current adapters execute manifest order. Treating a recorded
seed as operational would make reports false in a way that is hard to catch
after data collection.

Revisit when: suite adapters implement a non-`manifest_order` policy.

### SN-003: Sidecars carry generator truth until schema promotion

Decision: generator annotations, expected answers, tokenizer audit rows, and
deterministic scorer inputs stay in sidecars unless a manifest schema change is
explicitly reviewed.

Options considered:

1. Add every generator-specific field to suite manifests.
2. Keep manifests closed and use sidecars for profile-specific truth.

Chosen: option 2.

Rationale: closed manifests protect run identity and validation. Sidecars let
profile-specific information exist without pretending the generic substrate
understands it.

Revisit when: an analysis plan requires a field to be part of run identity.

### SN-004: The observer remains source-derived

Decision: suite observer pages should parse source docs and machine-readable
artifacts; they should not maintain separate hand-written status state.

Options considered:

1. Hand-maintained dashboard state.
2. Generated observer from repo truth.

Chosen: option 2.

Rationale: source-derived pages have already caught stale status. A second
manual state layer would create the same drift that the observatory was built
to prevent.

Revisit when: an external publication system requires a formal export schema.

### SN-005: Instruction-tuning suite means inference behavior only

Decision: instruction-tuning-related suite profiles should measure inference
behavior of named stacks, not training energy or general model quality.

Options considered:

1. Broaden into train-time energy and quality evaluation.
2. Stay on inference energy/behavior, with deterministic annotations only.

Chosen: option 2.

Rationale: JouleWise currently has an inference measurement harness. Training
energy, judge scoring, and leaderboard metrics require separate contracts and
would blur the project's strongest evidence lane.

Revisit when: train-time capture is explicitly scoped.

## Explorer inputs

Four read-only explorer passes informed this packet:

- Checkpoint metrics / measurement outputs.
- Prompt sequencing / workload generation.
- Next-observer / observatory surfaces.
- Instruction-tuning behavior extensions.

Material findings incorporated:

- `summary_metrics.suite_metrics` is optional for historical compatibility,
  but new suite analysis should expect it.
- Existing suite execution is manifest-order today.
- Text-path expected-vs-realized token hash checking remains a pre-campaign
  guardrail.
- Site/observer state should remain source-derived and fail-closed.
- Chat-template support is the largest unresolved instruction-tuning question.

## 5.5 high counter-review dispositions

Reviewer: `gpt-5.5`, high reasoning, read-only counter-review.

- Accepted: public observer leakage guard for stream logs. Applied in
  `README.md` and `next_observer_spec.md`.
- Accepted: deterministic checkpoint artifact wording must account for
  `generated_at`. Applied in `checkpoint_metrics_spec.md`.
- Accepted: sample checkpoint status counts were inconsistent. Fixed the
  example to show fixed-budget success with `capped_count: 0`.
- Accepted: strict-valid bundle alone is not checkpoint-ready because
  `suite_metrics` is optional for historical compatibility. Applied in
  `checkpoint_metrics_spec.md`.
- Accepted: `reasoning_mode_ladder_v1` needed a no-hidden-chain-of-thought
  prompt guard. Applied in `instruction_tuning_spec.md`.

## Counter-review prompts

Future counter-reviewers should answer these questions before implementation:

1. Which draft decisions should be promoted to `docs/decision_log.md`, and
   which should remain local to a spec?
2. Does any spec accidentally authorize skipping `RESUME-CP5`?
3. Are any checkpoint fields impossible to compute from current bundle
   evidence?
4. Does the prompt sequencing spec overstate byte-identical regeneration or
   exact-shape guarantees for any profile?
5. Does the observer spec risk introducing a second source of truth?
6. Does the instruction-tuning spec drift into quality claims, train-time
   claims, or benchmark leaderboard territory?
7. Are all floor-dependent claims blocked until P2-015 artifacts exist?
8. Are text-path hash-domain distinctions clear enough to prevent comparing
   text hashes to token-ID hashes?

## Known open questions

- Where should official checkpoint JSON live: campaign output directory,
  `docs/analysis/`, or a new run-bundle-adjacent analysis directory?
- Should checkpoint artifacts be immutable once written, or may they be
  regenerated like `summary_metrics.json` under D-028-style rules?
- How should per-repetition suite manifests be named if order rotation is
  generated rather than runtime-driven?
- What is the minimum template identity contract for chat-template delivery?
- Should the site render checkpoint JSON before or after the first quiet-window
  campaign, or wait for enough artifacts to avoid premature dashboard weight?
