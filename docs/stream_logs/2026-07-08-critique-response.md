# Stream Decision Ledger - Critique Response CR-1 (2026-07-08)

Scope: JouleWise stream/critique-response implementation session CR-1, per
C-011 council adjudication. This file uses the convention-v2 ledger format:
typed entries, mandatory Evidence, and scope capped to code shape,
cross-stream contracts, acceptance criteria, or future process.

---

### CR-1 [codex CR-1] [type: code-shape] Campaign verdict taxonomy

- **Decision:** Campaign verdicts are recorded as one JSONL
  `campaign_verdict` row and printed as a human `VERDICT:` block.
  `publishable` means every evaluated member is usable. `partial` means at
  least one member is usable and all other non-missing members are explicitly
  waived. `blocked` means expected member bundles are missing. `invalid`
  means an unwaived invalid member exists, or no usable member exists.
- **Alternatives:** Plain-text verdict blocks inside JSONL; treating all-waived
  campaigns as partial.
- **Why:** Keeping JSONL parseable preserves existing tooling. Requiring at
  least one usable member for `partial` matches the adjudicated "some usable"
  wording.
- **Evidence:** `scripts/run_campaign.py` verdict helpers and
  `tests.test_run_campaign.RunCampaignTests.test_verdict_block_content_for_publishable_campaign`.
- **Confidence:** High.
- **Binds:** Campaign log consumers and publishability gate.

### CR-2 [codex CR-1] [type: cross-stream-contract] Waiver schema stays campaign-level

- **Decision:** `--waivers` reads a JSON list of objects with
  `bundle_id` or `config`, plus `reason`, `approver`, `timestamp`, and
  `scope`. Waivers are matched at campaign evaluation time and logged in the
  campaign log only; bundles are never mutated.
- **Alternatives:** Embedding waiver metadata in `summary_metrics.json` or
  `metadata.json`.
- **Why:** The adjudication explicitly forbids bundle-level waivers; keeping
  them outside evidence preserves bundle immutability and makes waiver scope
  visible in the campaign verdict.
- **Evidence:** `scripts/run_campaign.py::load_waivers` and
  `test_waiver_allows_invalid_existing_member_and_records_partial_verdict`.
- **Confidence:** High.
- **Binds:** Campaign operation and dataset publication review.

### CR-3 [codex CR-1] [type: code-shape] Order manifest shape

- **Decision:** `generate_matrix.py` emits per-repetition configs named
  `<model-tag>-r<rep>-<workload>.json` and an `order_manifest.json` with
  `schema_version`, `seed`, `rotation_scheme`, `imbalance_note`, and an
  `executed_order` list containing index, config, run_id, model_tag, rep, and
  workload.
- **Alternatives:** Encoding order only in filenames; one manifest per model
  tag.
- **Why:** `run_campaign.py` needs an explicit executed-order source to avoid
  silent sorted model blocks, and one combined manifest lets two model-tag
  generator invocations converge on the counterbalanced campaign order.
- **Evidence:** `scripts/generate_matrix.py`,
  `tests.test_generate_matrix.GenerateMatrixTests.test_order_manifest_records_counterbalanced_execution_order`,
  and `test_order_manifest_controls_execution_order_and_log_metadata`.
- **Confidence:** Medium-high.
- **Binds:** Pre-2M matrix generation and campaign execution order.

### CR-4 [codex CR-1] [type: code-shape] Phase identifiability field shape

- **Decision:** `measurement_quality.phase_identifiability` is a map from
  phase name to `"identifiable"` or `"not_resolvable_sample_count"`.
  Nonzero intervals require at least `MIN_PHASE_SAMPLES = 3` summed-curve
  samples with inclusive bounds; zero-length intervals are identifiable and
  keep their existing zero-energy behavior.
- **Alternatives:** Per-interval nested records; top-level phase summary field.
- **Why:** The adjudicated rule asks for phase status, while keeping
  `phase_energy_j` untouched and the addition inside measurement quality.
- **Evidence:** `joulewise/reduce.py`,
  `test_phase_identifiability_requires_three_samples_per_nonzero_interval`,
  and `test_summary_metrics_schema_has_idle_gpu_quality_fields`.
- **Confidence:** High.
- **Binds:** Reducer honesty flags and downstream report interpretation.

### CR-5 [codex CR-1] [type: code-shape] Output-token denominator source flag

- **Decision:** `measurement_quality.token_counts_source` records
  `"runtime_observed"` when token events provide the output-token
  denominator and `"config_fallback"` when the legacy config fallback would
  have been used; in the fallback case output-token-denominator metrics are
  nulled.
- **Alternatives:** Reusing `token_count_source`, which already describes the
  total-token denominator for `energy_token_j`.
- **Why:** A separate additive field avoids changing the meaning of the older
  total-token provenance field while making config fallback explicit.
- **Evidence:** `joulewise/reduce.py` and
  `test_config_output_token_fallback_is_flagged_and_output_metrics_null`.
- **Confidence:** High.
- **Binds:** Reducer output schema and strict validation of fresh summaries.

### CR-6 [codex fix] [type: cross-stream-contract] Waiver v2, new-era honesty gates, output-token discriminator

- **Decision:** Campaign waivers now use a typed exact-match target:
  exactly one of `bundle_id`, `config`, or `run_id`. `config` matches only
  config filenames/stems; duplicate targets fail closed. Waiver `scope`
  names the failure classes it neutralizes (`idle_window_suspect`,
  `strict_invalid`, `status_failed`, or `any`). Strict validation requires
  `measurement_quality.token_counts_source` and
  `measurement_quality.phase_identifiability` on new-era summaries carrying
  `summary_provenance`, while legacy summaries keep additive tolerance.
  Runtime output-token counts come only from decode-phase token events.
- **Alternatives:** Keep CR-2's untyped waiver namespace; require the new
  summary fields for every historical bundle; count all token events as
  output-token evidence.
- **Why:** The review found cross-namespace waiver collisions, overbroad
  waiver scope, silent new-era honesty-field omission, and prompt-token event
  leakage into output-token metrics. Each needed fail-closed behavior without
  invalidating the six legacy Mac bundles.
- **Evidence:** `scripts/run_campaign.py`, `joulewise/cli.py`,
  `joulewise/bundle_read.py`, `joulewise/reduce.py`,
  `tests/test_run_campaign.py`, `tests/test_cli_run.py`, and
  `tests/test_reduce.py`.
- **Confidence:** High.
- **Binds:** Supersedes CR-2's waiver schema details; campaign publication
  gates, strict validation, and reducer token provenance.
