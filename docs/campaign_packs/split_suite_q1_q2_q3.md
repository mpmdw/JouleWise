# Split Inference Suite Pack: Q1, Q2, Q3

Status: pre-hardware DRAFT. The AP rows are seeded rows, not frozen registry
entries. Freeze them only after device/link placeholders are filled and before
any split hardware execution.

Packaging decision: Q1/Q2/Q3 are one split-suite pack because all three consume
the same device-pair/link matrix, composite split bundles, split-stage windows,
transfer-boundary labels, and monolithic references. Keeping one pack prevents
three diverging manifest templates for the same hardware campaign while still
leaving one DRAFT AP row per question.

## DRAFT AP Row: Q1

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-SPLIT-Q1 / Q1 split reduces energy. DRAFT until registry freeze. |
| family_id | FAM-SPLIT-Q1-ENERGY-CROSSOVER |
| claim_role | primary |
| selection_scope | Frozen split matrix for `<<DEVICE_PAIR>>`, `<<MODEL_SET>>` resolved at registry freeze to either `{Qwen2.5-1.5B}` or `{Qwen2.5-1.5B, Qwen2.5-7B}`, prompt lengths `{512,2048,8192}`, decode length `256`, links `<<LINK_MBPS_SET>>`, split mode `offline_replay` unless explicitly frozen as analytical composition, and both monolithic references for the same model/runtime/artifact where available. Dropping the 7B cells requires named `DROP-FEASIBILITY-P1-004-P1-006-MODEL-7B` evidence before any campaign bundle exists. |
| multiplicity_rule | Holm within FAM-SPLIT-Q1-ENERGY-CROSSOVER across the predeclared split-vs-better-monolithic contrasts for each frozen model x prompt x link x pairing cell. Any unplanned model, prompt, link, runtime, or boundary subset is exploratory. |
| Metric + exact window class | Primary: `split_total_energy_j = prefill + serialize + transfer + deserialize + decode` reported as composite gross request energy and, where both ends have idle baselines, composite idle-subtracted request energy. Stage descriptors use gross phase windows: `phase_energy_j.prefill`, `phase_energy_j.serialize`, `phase_energy_j.transfer`, `phase_energy_j.deserialize`, and `phase_energy_j.decode`. |
| Unit of analysis + dependence structure | Composite bundle repetition; stage energies are nested within a composite split bundle and are not independent replicates. Monolithic references are bundle-level repetitions matched by model/runtime/artifact/version and blocked by session/link where possible. |
| Estimator/formula | For each frozen cell, estimate `delta_j = split_total_energy_j - min(monolithic_prefill_node_j, monolithic_decode_node_j)` with paired/block contrast when monolithic reruns are in the same campaign block; otherwise use predeclared unpaired contrast with session covariate. D-048 prediction validation also estimates prediction error `measured_split_total_j - predicted_split_total_j`, where prediction uses AP-1 Q4 coefficients + measured link-transfer energy + idle floors before any split hardware run. Crossover exists only where the split-total contrast is below zero and clears the floor gate. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid composite bundles and strict-valid monolithic reference bundles only. Exclude any composite missing payload manifest, clock-offset bound, per-node metadata, stage marker pair, model/artifact hash, or greedy output-equivalence check. D-014 quality waivers must be named in the frozen registry and report text; unwaived suspect flags stay in sensitivity tables but do not support L2 wording. |
| Order/blocking/covariates | Counterbalanced round-robin order by model x prompt x link x split/monolithic condition where model reload cost permits, following D-014/C-011 conventions. If operational blocks are forced, record executed order in the experiment manifest and include session/block/link-position drift terms. Start/end drift sentinels bracket each hardware session. |
| Floor gate | pending-P2-015: use `max(floor_abs_j, floor_cmp_j)` for the same backend, metric, and window class. Existing request rows can gate same-node request companions, not the composite split-total metric: `DF-RQ-GROSS-MID` (`gross_energy_j`, gross request), `DF-RQ-IDLE-MID` (`energy_request_j`, `idle_subtracted_energy_j`, idle-sub request), `DF-RQ-GROSS-LONG-PROMPT` (`gross_energy_j`, gross request), `DF-RQ-IDLE-LONG-PROMPT` (`energy_request_j`, `idle_subtracted_energy_j`, idle-sub request), and `DF-CMP-ABBA-RQ` (`gross_energy_j`, `energy_request_j`, request windows). The 2048/256 request cells consume the ambiguity-rule maximum of `DF-RQ-*-MID` and `DF-RQ-*-LONG-PROMPT`; 8192/256 request cells are capped until P2-015 adds matching-or-harder >=8192 prompt / 256 decode rows or the frozen AP names an accepted AP-specific bound. Any 2048/2048 request cell is likewise capped until P2-015 adds a matching-or-harder cell or the frozen AP names a bound. Stage descriptors consume `DF-PH-PREFILL` (`phase_energy_j.prefill`, phase window), `DF-PH-DECODE` (`phase_energy_j.decode`, phase window), and `DF-CMP-ABBA-PH` (`phase_energy_j.prefill`, `phase_energy_j.decode`, phase windows). No exact P2-015 row currently exists for composite `split_total_energy_j`, `serialize`, `transfer`, or `deserialize`; standalone L2/L3 claims for those terms are capped until P2-015 adds rows, adds a composite row, or this AP freezes an accepted AP-specific bound or combination rule. |
| MDE/n sizing + predeclared top-up rule | n>=5 for headline pairing cells; n>=3 minimum for non-headline cells. Top up to n=10 before Q1 L2 wording when the split-vs-better-monolithic CI touches the active floor gate, when a crossover verdict changes under leave-one-out, or when D-048 prediction error is near the floor. |
| Denominator provenance requirement | Runtime-observed output tokens, stop reasons, output policy, model artifact hashes, serialized payload bytes, payload SHA-256, effective link throughput, and per-node idle baselines. Config-token fallback cannot support per-token or latency-normalized L2 claims. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L2 boundary-labeled; stronger only with calibration`. Forbidden upgrade: `no uncalibrated cross-boundary total-energy winner`. |
| Disqualifiers + not-resolvable conditions | Below-floor contrast; missing P2-015 floor row for the claim window; transfer-stage boundary mismatch without D-049 label; cross-boundary quantitative winner without D-018 calibration bridge; clock-offset bound longer than the attributed interval; non-identical greedy output without scoped explanation; incomplete payload manifest; short windows under 3 samples; or monolithic reference version drift. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

### Q1 D-048 Pre-Registered Prediction Obligation

Before any split hardware run, generate predicted split-energy curves per
pairing/link and record them in the seeded AP row/frozen registry. The model is
model-first:

```text
predicted_split_total_j(prompt, link, pair)
  = AP-1 predicted_prefill_j(prefill_node, prompt)
  + measured_or_predicted_serialize_j(prefill_node, prompt)
  + measured_link_transfer_j(payload_bytes, link, pair)
  + measured_or_predicted_deserialize_j(decode_node, payload_bytes)
  + AP-1 predicted_decode_j(decode_node, decode_tokens)
  + idle_floor_terms_j
```

The feasible set must include at least one pairing/link cell where the model
predicts a crossover, if any exists after P1-004/P1-006 hardware facts are
known. If no feasible crossover is predicted, that no-crossover verdict is
publishable only as successful prediction or quantified overhead discovery,
not as a surprise negative. Every branch is a result: confirmed model,
quantified unmodeled overhead, or crossover located where predicted.

At registry freeze, designate one named same-boundary headline pairing where
both ends are under like measurement boundaries. That pairing is the D-048
L2-eligible calibration-free headline cell; cross-boundary pairings remain
secondary/descriptive unless a D-018 bridge is frozen and clears.

## DRAFT AP Row: Q2

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-SPLIT-Q2 / Q2 link bandwidth sensitivity. DRAFT until registry freeze. |
| family_id | FAM-SPLIT-Q2-LINK-SENSITIVITY |
| claim_role | primary |
| selection_scope | Frozen `<<DEVICE_PAIR>>` and model/prompt/decode set from the split suite, limited to links `<<LINK_MBPS_SET>>` with measured effective throughput and transfer energy. |
| multiplicity_rule | Holm within FAM-SPLIT-Q2-LINK-SENSITIVITY across predeclared link-speed contrasts within each model x prompt x device-pair cell. Exploratory for unplanned links or nominal-link-only comparisons. |
| Metric + exact window class | Primary: transfer time seconds, effective throughput MiB/s, transfer energy joules, and split total energy joules on composite request windows. Companion latency: end-to-end split latency seconds and stage latencies seconds. |
| Unit of analysis + dependence structure | Composite transfer/split bundle repetition, blocked by payload/link/session. Sender and receiver transfer windows inside one composite bundle are dependent components, not separate replicates. |
| Estimator/formula | Within-cell link contrast: `delta_link = metric(link_b) - metric(link_a)` using paired/block contrast when the same payload order is counterbalanced across links. Crossover movement is reported as change in the prompt-length crossing point only when both links have measured transfer energy and the Q1 contrast clears its floor. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid composite bundles only; payload byte count and SHA-256 required; link speed must be measured, not assumed. Exclude cells with missing receiver/sender marker bounds, payload mismatch, or transfer-boundary label mismatch for a like-boundary comparison. |
| Order/blocking/covariates | Counterbalance link order inside each payload/model block: e.g., `1GbE,2.5GbE,2.5GbE,1GbE` across ABBA blocks where hardware switching permits. Record forced order and include session/link-position covariate. |
| Floor gate | pending-P2-015: same-node request companions consume `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, `DF-RQ-GROSS-LONG-PROMPT`, `DF-RQ-IDLE-LONG-PROMPT`, and `DF-CMP-ABBA-RQ` for `gross_energy_j` / `energy_request_j` request windows. The 2048/256 request cells consume the ambiguity-rule maximum of the MID and LONG-PROMPT rows; 8192/256 request cells are capped until P2-015 adds matching-or-harder >=8192 prompt / 256 decode rows or the frozen AP names an accepted AP-specific bound. Any 2048/2048 request cell is likewise capped until P2-015 adds a matching-or-harder cell or the frozen AP names a bound. Request-level split-total link sensitivity has no exact composite P2-015 row; it is capped until P2-015 adds a composite row or the frozen AP names an accepted combination rule. Transfer-stage energy has no exact P2-015 transfer-window floor row yet; standalone transfer-energy L2 wording is capped until that row or AP-specific bound exists. |
| MDE/n sizing + predeclared top-up rule | n>=3 per payload x link cell, n>=5 for headline link contrast. Top up to n=10 when the link contrast CI crosses the active floor gate or when the nominal crossover position changes under leave-one-out. |
| Denominator provenance requirement | Payload bytes from `transfer/payload_manifest.json`, payload SHA-256, measured transfer duration, runtime-observed output tokens for total split companions, and recorded link evidence from P1-004. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L2`. Forbidden upgrade: `no nominal-link crossover without measured links`. |
| Disqualifiers + not-resolvable conditions | Nominal link speed without measured throughput; missing payload manifest; transfer window shorter than clock-offset bound; below-floor link effect; transfer-boundary label mismatch; or unplanned link searched after seeing results. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## DRAFT AP Row: Q3

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-SPLIT-Q3 / Q3 split energy-latency Pareto. DRAFT until registry freeze. |
| family_id | FAM-SPLIT-Q3-PARETO |
| claim_role | secondary |
| selection_scope | Frozen comparison set from Q1/Q2: monolithic references and split cells for `<<DEVICE_PAIR>>`, `<<MODEL_SET>>`, prompt lengths `{512,2048,8192}`, decode length `256`, links `<<LINK_MBPS_SET>>`, and a single frozen latency metric per figure. |
| multiplicity_rule | Holm within FAM-SPLIT-Q3-PARETO for predeclared pairwise dominance checks in the frozen comparison set; any expanded all-pairs sweep uses Benjamini-Hochberg at q=0.10 or is exploratory, as frozen in the registry. |
| Metric + exact window class | Energy axis: composite gross request energy and, where available, composite idle-subtracted request energy. Latency axis: one frozen metric per figure, default end-to-end request latency seconds; companion TTFT seconds and decode latency seconds are descriptive unless frozen as separate figures. |
| Unit of analysis + dependence structure | Bundle/composite-bundle repetition; Pareto membership is computed from condition-level estimates with raw points shown. Stage windows inside a split bundle are not independent. |
| Estimator/formula | A condition is Pareto-frontier only if no other frozen condition has both lower energy and lower frozen latency metric after floor and CI checks. Directional dominance uses contrast-level CI, not visual separation of marginal intervals. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only; every cell must carry boundary label, link label, output policy, and runtime-observed denominator evidence. Exclude cells with non-equivalent output policy or missing latency metric. |
| Order/blocking/covariates | Same counterbalanced order as Q1/Q2. Pareto analyses include session/block covariate only if frozen before execution; otherwise report stratified raw points and descriptive frontier only. |
| Floor gate | pending-P2-015: same-node request-energy companions consume `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, `DF-RQ-GROSS-LONG-PROMPT`, `DF-RQ-IDLE-LONG-PROMPT`, and `DF-CMP-ABBA-RQ` for request windows. The 2048/256 request cells consume the ambiguity-rule maximum of the MID and LONG-PROMPT rows; 8192/256 request cells are capped until P2-015 adds matching-or-harder >=8192 prompt / 256 decode rows or the frozen AP names an accepted AP-specific bound. Any 2048/2048 request cell is likewise capped until P2-015 adds a matching-or-harder cell or the frozen AP names a bound. Composite split-total Pareto energy has no exact P2-015 row; it is capped until P2-015 adds a composite row or the frozen AP names an accepted combination rule. Latency has no P2-015 energy floor; latency uncertainty follows D-014 contrast CI and run-bundle timing quality fields. Stage-energy captions consume `DF-PH-PREFILL`, `DF-PH-DECODE`, and `DF-CMP-ABBA-PH` only for prefill/decode descriptors. |
| MDE/n sizing + predeclared top-up rule | n follows Q1/Q2 source cells; top up before Pareto-frontier language when any dominance verdict changes under leave-one-out or when the energy contrast is near the active floor gate. |
| Denominator provenance requirement | Runtime-observed output tokens, stop reason, output policy, request latency, TTFT/decode latency when used, and payload/link evidence for split cells. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L2`. Forbidden upgrade: `no Pareto claim without frozen set and latency metric`. |
| Disqualifiers + not-resolvable conditions | Frozen comparison set changed post hoc; latency metric changed per figure; energy contrast below floor; output-policy mismatch; cross-boundary quantitative ranking without calibration; or missing raw points/uncertainty. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## Manifest/Config Templates

These templates are typed-config shaped. Current schema v0.1 validates
monolithic references; schema v0.2 split/transfer configs are PLANNED under
Phase 3 Stage 3.1. The `<<DEVICE_PAIR.*>>` placeholders are the only
hardware/device-pair slots; `<<LINK_*>>` placeholders are the only link slots.

### Existing Monolithic Reference Template

```json
{
  "schema_version": "0.1",
  "run_id": "split-ref-<<DEVICE_PAIR.PREFILL_TARGET_ID>>-qwen25-15b-p2048-d256",
  "model": {
    "name": "Qwen2.5-1.5B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
    "weight_format": "mlx",
    "context_window": 32768
  },
  "quantization": {
    "name": "int4",
    "bits": 4
  },
  "hardware_target": {
    "id": "<<DEVICE_PAIR.PREFILL_TARGET_ID>>",
    "transport": "<<DEVICE_PAIR.PREFILL_TRANSPORT>>",
    "host": "<<DEVICE_PAIR.PREFILL_SSH_HOST_OR_OMIT_FOR_LOCAL>>",
    "runtime_backend": "<<DEVICE_PAIR.PREFILL_RUNTIME_BACKEND>>",
    "telemetry_backend": "<<DEVICE_PAIR.PREFILL_TELEMETRY_BACKEND>>",
    "device_kind": "<<DEVICE_PAIR.PREFILL_DEVICE_KIND>>",
    "notes": "Split-suite monolithic reference for <<DEVICE_PAIR>>."
  },
  "workload_profile": {
    "name": "split_ref_p2048_d256",
    "prompt_tokens": 2048,
    "output_tokens": 256,
    "repetitions": 5,
    "warmup_runs": 1
  },
  "interconnect": {
    "name": "local"
  },
  "sampling": {
    "power_hz": 10.0,
    "idle_seconds": 30.0,
    "warmup_seconds": 5.0
  },
  "run_metadata": {
    "project": "capstone-joulewise",
    "operator": "ed",
    "tags": ["phase3", "split-suite", "monolithic-reference", "q1", "q2", "q3"]
  }
}
```

### PLANNED Split Offline Replay Template

Owner: Phase 3 Stage 3.1/3.2; no current CLI validates this schema yet.

```json
{
  "schema_version": "0.2",
  "run_kind": "split_offline",
  "run_id": "split-offline-<<DEVICE_PAIR>>-<<LINK_MBPS>>mbps-qwen25-15b-p2048-d256",
  "model": {
    "name": "Qwen2.5-1.5B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "<<DEVICE_PAIR.MODEL_PATH_ON_BOTH_NODES>>",
    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
    "weight_format": "<<DEVICE_PAIR.WEIGHT_FORMAT>>",
    "context_window": 32768
  },
  "quantization": {
    "name": "int4",
    "bits": 4
  },
  "split_plan": {
    "mode": "offline_replay",
    "prefill_target": "<<DEVICE_PAIR.PREFILL_TARGET_ID>>",
    "decode_target": "<<DEVICE_PAIR.DECODE_TARGET_ID>>",
    "runtime_backend": "<<DEVICE_PAIR.SAME_RUNTIME_ON_BOTH_ENDS>>",
    "prompt_tokens": 2048,
    "decode_tokens": 256,
    "transfer": {
      "method": "tcp_payload",
      "link_label": "<<LINK_LABEL>>",
      "link_speed_mbps": "<<LINK_MBPS>>",
      "staging_dir": "/tmp/joulewise-split-staging",
      "payload_kind": "kv_cache"
    },
    "stage_windows": ["prefill", "serialize", "transfer", "deserialize", "decode"],
    "decode_node_warm_state": "model_loaded_before_measured_window",
    "equivalence_check": "greedy_monolithic_token_identity"
  },
  "hardware_targets": [
    {
      "role": "prefill",
      "id": "<<DEVICE_PAIR.PREFILL_TARGET_ID>>",
      "transport": "<<DEVICE_PAIR.PREFILL_TRANSPORT>>",
      "host": "<<DEVICE_PAIR.PREFILL_SSH_HOST_OR_OMIT>>",
      "runtime_backend": "<<DEVICE_PAIR.SAME_RUNTIME_ON_BOTH_ENDS>>",
      "telemetry_backend": "<<DEVICE_PAIR.PREFILL_TELEMETRY_BACKEND>>",
      "device_kind": "<<DEVICE_PAIR.PREFILL_DEVICE_KIND>>"
    },
    {
      "role": "decode",
      "id": "<<DEVICE_PAIR.DECODE_TARGET_ID>>",
      "transport": "<<DEVICE_PAIR.DECODE_TRANSPORT>>",
      "host": "<<DEVICE_PAIR.DECODE_SSH_HOST_OR_OMIT>>",
      "runtime_backend": "<<DEVICE_PAIR.SAME_RUNTIME_ON_BOTH_ENDS>>",
      "telemetry_backend": "<<DEVICE_PAIR.DECODE_TELEMETRY_BACKEND>>",
      "device_kind": "<<DEVICE_PAIR.DECODE_DEVICE_KIND>>"
    }
  ],
  "sampling": {
    "power_hz": 10.0,
    "idle_seconds": 30.0,
    "warmup_seconds": 5.0
  },
  "run_metadata": {
    "project": "capstone-joulewise",
    "operator": "ed",
    "tags": ["phase3", "split-suite", "offline-replay", "q1", "q2", "q3"]
  }
}
```

Order policy: generate an experiment manifest that rotates model x prompt x
link x condition order. Within each block, execute monolithic prefill-node
reference, monolithic decode-node reference, and split cell in counterbalanced
round-robin order unless model reload makes this impossible; any forced block
order is recorded and analyzed as drift evidence.

For any config with `workload_profile.repetitions > 1`, the current runner
dispatches to the experiment runner: member bundles are written as
`runs/<base_run_id>__r1` ... `runs/<base_run_id>__rN`, and the experiment
manifest lands at `runs/experiments/<base_run_id>.json`. Validation,
reduction, and packaging paths must name member bundles, not the base
`run_id`.

## Expected Artifacts

Composite split bundles follow `docs/contracts/run_bundle_layout.md`:

```text
runs/<base_run_id>__rN/
  config.json
  metadata.json
  events.jsonl
  summary_metrics.json
  transfer/payload_manifest.json
  nodes/prefill/
  nodes/decode/
```

The composite summary must decompose total split energy into `prefill`,
`serialize`, `transfer`, `deserialize`, and `decode` components. Per
`docs/contracts/measurement_methodology.md`, serialize is the cache-persist
window on the prefill node, transfer is the byte-movement window, deserialize
is the cache-load window on the decode node, and decode is first-token to
last-token. Cache load is not decode energy.

D-049 boundary labels are required per transfer cell:

- `host-inclusive transfer energy`: wall/PD/SoC/module boundary includes the
  host or NIC path for the transfer leg.
- `board-only lower-bound transfer energy`: discrete-GPU board telemetry
  excludes host CPU/NIC/DRAM transfer work; the value is a lower bound.

Transfer-energy comparisons are like-boundary only unless a D-018 calibration
bridge exists. Each composite bundle records D-003 clock-offset marker bounds:
per-process monotonic-vs-wall offsets, NTP state where determinable, remote
marker no-op timestamps before/after each remote stage, and a composite
metadata offset bound. Any cross-node interval shorter than the offset bound
is not eligible for energy attribution claims.

## Figure Skeletons

F-SPLIT-Q1-CURVES: total energy vs prompt length.

- x-axis: prompt length (tokens).
- y-axis: split total energy and monolithic reference energy (J).
- Facets: `<<DEVICE_PAIR>>` x `<<LINK_LABEL>>`.
- Caption template: `Measurements in this figure characterize one physical unit of [target hardware] running [OS/version], [runtime/library], [model artifact], [quantization], [tokenizer], [sampler/output policy], and [measurement boundary]. They support stack-specific claims under the stated boundary and do not establish hardware-class, vendor-class, or unit-general results without independent replication or calibration evidence.` Boundary labels: `[per-cell host-inclusive transfer energy]` or `[per-cell board-only lower-bound transfer energy]`. For cross-boundary cells: `Boundary labels differ across cells, so absolute energy values are descriptive rather than a calibrated cross-target ranking.`

F-SPLIT-Q2-LINK: transfer energy/time vs link.

- x-axis: measured effective throughput (MiB/s) and nominal link label.
- y-axis left: transfer energy (J); y-axis right: transfer time (s).
- Caption includes the same single-unit language and the D-049 per-cell
  transfer-boundary label.

F-SPLIT-Q3-PARETO: energy-latency frontier.

- x-axis: frozen latency metric (s), default end-to-end request latency.
- y-axis: composite request energy (J).
- Marks: raw bundle points plus condition estimate/CI.
- Caption includes the same single-unit language and names the frozen latency
  metric; no Pareto claim is made outside the frozen comparison set.

F-SPLIT-PREDICTION: predicted vs measured split total.

- x-axis: predicted split total energy (J).
- y-axis: measured split total energy (J).
- Reference: y=x line; annotate residual (J) and boundary labels.
- Caption frames acceptance as D-048 prediction validation.

## Hardware Prerequisites

- P1-004 link evidence: measured topology/link speeds for `<<LINK_MBPS_SET>>`.
- P1-006 device evidence: remote target access and telemetry backend viability.
- Same pinned runtime and identical model artifact on both split ends for real
  KV replay; cross-runtime KV portability is out of scope.
- P2-015 floor artifact for the exact backend x metric x window classes named
  in the AP rows.
- AP-1 Q4 coefficients and monolithic references for the same model/runtime
  family before D-048 split prediction curves are frozen.
- D-049 transfer-boundary classification for every transfer cell.

## Plug-In-Day Runbook

Existing commands:

```sh
python3 -m joulewise kv-size /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit/config.json --prompt-tokens 512,2048,8192
python3 scripts/spike_mlx_prompt_cache.py run --model /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit --prompt-len 1024 --decode 64 --workdir runs/spikes/<<DEVICE_PAIR>>-mlx-cache --keep
python3 -m joulewise validate-config configs/campaign_packs/<<MONOLITHIC_CONFIG>>.json
python3 scripts/run_campaign.py configs/campaign_packs/<<MONOLITHIC_CONFIG_DIR>> --runs-dir runs --log runs/experiments/<<EXPERIMENT_ID>>.jsonl --backup
python3 -m joulewise validate-bundle --strict runs/<<BASE_RUN_ID>>__r1
python3 -m joulewise reduce runs/<<BASE_RUN_ID>>__r1
python3 scripts/package_bundle_pack.py --output runs/bundle_packs/<<PACK_ID>> runs/<<BASE_RUN_ID_A>>__r1 runs/<<BASE_RUN_ID_B>>__r1
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<PACK_ID>>
```

PLANNED commands:

```sh
# PLANNED, owner: Phase 3 Stage 3.1 in docs/phase_3/phase_3_plan.md; no current TASK_QUEUE row.
python3 -m joulewise transfer-bench configs/campaign_packs/<<TRANSFER_BENCH_CONFIG>>.json --runs-dir runs

# PLANNED, owner: Phase 3 Stage 3.2/3.4 in docs/phase_3/phase_3_plan.md; no current TASK_QUEUE row.
python3 -m joulewise run configs/campaign_packs/<<SPLIT_OFFLINE_CONFIG>>.json --runs-dir runs

# PLANNED, owner: Phase 3 composite reader/reducer work; no current TASK_QUEUE row.
python3 -m joulewise validate-bundle --strict runs/<<COMPOSITE_SPLIT_BASE_RUN_ID>>__r1
python3 -m joulewise reduce runs/<<COMPOSITE_SPLIT_BASE_RUN_ID>>__r1
```

Operator sequence:

0. Acquire the no-agent quiet-machine lock (`[QUIET-MAC]`; see
   `docs/orchestration.md`): stop all agent/Codex load for the whole
   measurement session and confirm machine-idle state before the first idle
   baseline.
1. Create `configs/campaign_packs/` if needed, copy each filled template JSON
   into that directory, and freeze DRAFT AP rows into the analysis registry
   with complete `contrast_id` enumeration, manifest hash, and a named
   same-boundary headline pairing for the Q1 D-048 L2-eligible
   calibration-free cell; cross-boundary pairings stay secondary/descriptive
   without a D-018 bridge.
2. Resolve all selection-scope alternatives to included/excluded verdicts
   before any campaign bundle exists, using named evidence such as
   `DROP-FEASIBILITY-P1-004-P1-006-MODEL-7B` for excluded cells.
3. Generate or hand-author `configs/campaign_packs/<<MONOLITHIC_CONFIG_DIR>>/order_manifest.json`
   with schema `joulewise.order_manifest.v1`, including rotated
   model x prompt x link x condition order and start/end
   `short_short_sentinel` entries that must execute as the first and last
   measured bundles bracketing each hardware session. Extending
   `scripts/generate_matrix.py` for split-suite matrices is a PLANNED
   prerequisite owned by Phase 3 Stage 3.1 if the manifest is not hand-authored.
4. Run `kv-size` and the prompt-cache spike; record feasibility verdicts in
   `docs/phase_3/kv_feasibility.md`.
5. Validate monolithic configs, run monolithic references, strict-validate and
   reduce each member bundle (`runs/<base_run_id>__rN`) and retain
   `runs/experiments/<base_run_id>.json`.
6. Execute transfer bench and split offline runs once planned commands exist.
7. Package strict-valid member bundles and verify the pack before analysis.

Closing cooldown-gate note: the D-014 cooldown gate between repetitions is
runner-automated, but cooldown cap-hit flags must be checked in each member
bundle's measurement quality before analysis.
