# C5-2.3 Pack: Predicted-Vs-Measured KV Economics

Status: pre-hardware DRAFT. This pack remains useful even if live split fails:
it validates the analytic KV payload and transfer-economics terms that feed
the split model.

## DRAFT AP Row

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-C5-2.3 / C5-2.3 predicted-vs-measured KV economics. DRAFT until registry freeze. |
| family_id | FAM-C5-23-KV-ECONOMICS |
| claim_role | primary |
| selection_scope | Frozen runtime/model set `<<MODEL_SET>>`, prompt lengths `{512,2048,8192}`, decode length `256`, links `<<LINK_MBPS_SET>>`, device pair `<<DEVICE_PAIR>>`, runtime cache format, and transfer method. Includes analytic KV-size prediction, serialized payload size, transfer time/energy, deserialize/load time/energy, and measured split or replay evidence where available. |
| multiplicity_rule | Holm within FAM-C5-23-KV-ECONOMICS across predeclared prediction-error contrasts for payload bytes, transfer energy/GiB, transfer time/GiB, and deserialize energy/time for each frozen runtime x model x link family. Broad payload sweeps beyond the frozen set are Benjamini-Hochberg q=0.10 or exploratory as recorded at registry freeze. |
| Metric + exact window class | Payload bytes and prediction percent error; transfer energy J/GiB and transfer time s/GiB on transfer windows; deserialize/cache-load energy J and time s on phase windows; optional composite request total for split/replay validation. |
| Unit of analysis + dependence structure | Payload/replay bundle repetition. Sender/receiver transfer components and deserialize stage are dependent components of the same composite or replay cell. |
| Estimator/formula | Analytic KV bytes per token: `2 * n_layers * n_kv_heads * head_dim * dtype_bytes`, multiplied by prompt tokens and adjusted only by predeclared runtime cache dtype/layout metadata. Prediction error: `measured_payload_bytes - predicted_payload_bytes` and percent error. Transfer economics: `transfer_energy_j / payload_gib`, `transfer_time_s / payload_gib`; deserialize economics: `deserialize_energy_j` and `deserialize_time_s` per payload. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid transfer/replay/composite bundles only; include only cells with actual payload size, payload SHA-256, runtime cache format/version, link measurement, and cache-load markers. Exclude cells where cache is not portable unless the row is explicitly scoped to same-machine replay. Waivers must be named before registry freeze. |
| Order/blocking/covariates | Counterbalanced payload/link order by model and prompt length. Use ABBA duplicate-payload blocks for transfer repeatability where possible. Record block/session/link-position covariates and cooldown notes. |
| Floor gate | pending-P2-015: same-node request companions consume `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, `DF-RQ-GROSS-LONG-PROMPT`, `DF-RQ-IDLE-LONG-PROMPT`, and `DF-CMP-ABBA-RQ` for request windows. The 2048/256 request cells consume the ambiguity-rule maximum of the MID and LONG-PROMPT rows; 8192/256 request cells are capped until P2-015 adds matching-or-harder >=8192 prompt / 256 decode rows or the frozen AP names an accepted AP-specific bound. Any 2048/2048 request cell is likewise capped until P2-015 adds a matching-or-harder cell or the frozen AP names a bound. Optional composite request validation has no exact P2-015 composite row and is capped until P2-015 adds a composite row or the frozen AP names an accepted combination rule. Decode-stage companions consume `DF-PH-DECODE` and `DF-CMP-ABBA-PH`; prefill descriptors consume `DF-PH-PREFILL`. No exact P2-015 rows currently exist for `transfer` or `deserialize`; C5-2.3 L2 claims about those terms require P2-015 to add transfer/deserialize rows or this AP to freeze an accepted AP-specific bound. |
| MDE/n sizing + predeclared top-up rule | Preserve n>=3 per payload/link cell and n>=5 for headline runtime/model/link cells. Sizing authority: D-062 + `configs/analysis_registry/<<C523_ANALYSIS_REGISTRY>>.json` (frozen n; no outcome-based top-ups without demotion). |
| Denominator provenance requirement | Model config fields `n_layers`, `n_kv_heads`, `head_dim`, dtype bytes, prompt tokens, runtime cache format/version, serialized payload bytes, payload SHA-256, link throughput, transfer duration, deserialize/load markers, output tokens/stop reason for split validation companions. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L2`. Forbidden upgrade: `no KV economics claim without measured payload/link/deserialization terms`. |
| Disqualifiers + not-resolvable conditions | Missing measured payload bytes; nominal link speed without measured throughput; no deserialize/cache-load markers; transfer/deserialize floor row missing for a standalone L2 stage claim; clock-offset bound too large; runtime cache format not pinned; or cache portability failure hidden instead of scoped. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## Manifest/Config Templates

### Existing KV-Size Prediction Command

The analytic prediction is generated from current CLI:

```sh
python3 -m joulewise kv-size /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit/config.json --prompt-tokens 512,2048,8192
```

Live-verified for the named Qwen2.5-1.5B-Instruct-4bit config:
`bytes_per_token=28672` (28 KiB/token), so prompt totals are 14,680,064 bytes
(14 MiB) at 512 tokens, 58,720,256 bytes (56 MiB) at 2048 tokens, and
234,881,024 bytes (224 MiB) at 8192 tokens.

### PLANNED Transfer/Deserialize Template

Owner: Phase 3 Stage 3.1/3.2. No current CLI validates `run_kind:
transfer_bench` or `split_offline`. The `<<DEVICE_PAIR.*>>` placeholders are
the only hardware/device-pair slots; `<<LINK_*>>` placeholders are the only
link slots.

```json
{
  "schema_version": "0.2",
  "run_kind": "transfer_bench",
  "run_id": "c5-2-3-kv-<<DEVICE_PAIR>>-<<LINK_MBPS>>mbps-qwen25-15b-p2048",
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
  "transfer_bench": {
    "device_pair": "<<DEVICE_PAIR>>",
    "sender_target": "<<DEVICE_PAIR.SENDER_TARGET_ID>>",
    "receiver_target": "<<DEVICE_PAIR.RECEIVER_TARGET_ID>>",
    "link_label": "<<LINK_LABEL>>",
    "link_speed_mbps": "<<LINK_MBPS>>",
    "payload_sets": [
      {
        "payload_kind": "synthetic",
        "payload_sizes_mib": [16, 64, 256, 1024, 2048],
        "stage": "Stage 3.1 microbench bytes independent of any LLM runtime"
      },
      {
        "payload_kind": "kv_cache",
        "prompt_tokens": [512, 2048, 8192],
        "analytic_payload_sizes_mib": [14, 56, 224],
        "analytic_payload_sizes_bytes": [14680064, 58720256, 234881024]
      }
    ],
    "decode_tokens": 256,
    "method": "tcp_payload",
    "deserialize_probe": "load_prompt_cache_fresh_process",
    "repetitions": 5
  },
  "hardware_targets": [
    {
      "role": "sender",
      "id": "<<DEVICE_PAIR.SENDER_TARGET_ID>>",
      "transport": "<<DEVICE_PAIR.SENDER_TRANSPORT>>",
      "host": "<<DEVICE_PAIR.SENDER_SSH_HOST_OR_OMIT>>",
      "runtime_backend": "<<DEVICE_PAIR.RUNTIME_BACKEND>>",
      "telemetry_backend": "<<DEVICE_PAIR.SENDER_TELEMETRY_BACKEND>>",
      "device_kind": "<<DEVICE_PAIR.SENDER_DEVICE_KIND>>"
    },
    {
      "role": "receiver",
      "id": "<<DEVICE_PAIR.RECEIVER_TARGET_ID>>",
      "transport": "<<DEVICE_PAIR.RECEIVER_TRANSPORT>>",
      "host": "<<DEVICE_PAIR.RECEIVER_SSH_HOST_OR_OMIT>>",
      "runtime_backend": "<<DEVICE_PAIR.RUNTIME_BACKEND>>",
      "telemetry_backend": "<<DEVICE_PAIR.RECEIVER_TELEMETRY_BACKEND>>",
      "device_kind": "<<DEVICE_PAIR.RECEIVER_DEVICE_KIND>>"
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
    "tags": ["c5-2.3", "kv-economics", "transfer", "deserialize"]
  }
}
```

Order policy: execute payload sizes in rotated log-spaced order per link and
reverse the order across blocks. If hardware switching forces link blocks,
record link-position and session covariates before registry freeze.

For any future transfer/replay config with `repetitions > 1`, member bundles
must follow the current experiment-runner convention:
`runs/<base_run_id>__r1` ... `runs/<base_run_id>__rN`, with the manifest at
`runs/experiments/<base_run_id>.json`. Validation, reduction, and packaging
paths must name member bundles, not the base `run_id`.

## Expected Artifacts

Transfer/composite bundles must include:

```text
runs/<base_run_id>__rN/
  config.json
  metadata.json
  events.jsonl
  summary_metrics.json
  transfer/payload_manifest.json
  nodes/prefill/ or nodes/sender/
  nodes/decode/ or nodes/receiver/
```

`transfer/payload_manifest.json` records payload bytes, payload SHA-256,
payload kind, predicted bytes, prediction formula inputs, transfer start/end,
and measured throughput. `events.jsonl` must carry `serialize`, `transfer`,
`deserialize`, and `decode` markers where applicable. `deserialize` is the
cache-load window on the decode node; cache load is not decode energy.

D-049 labels are required for every transfer cell:

- `host-inclusive transfer energy`
- `board-only lower-bound transfer energy`

Only like-boundary transfer-energy cells may be compared. D-003 metadata must
record wall-clock timestamps, monotonic-vs-wall offsets, NTP state when known,
remote marker-event offset bounds, and measurement-quality flags for intervals
shorter than the bound.

## Figure Skeletons

F-C523-KV-BYTES: predicted vs measured payload bytes.

- x-axis: predicted KV payload size (MiB or GiB).
- y-axis: measured serialized payload size (MiB or GiB).
- Caption template: `Measurements in this figure characterize one physical unit of [target hardware] running [OS/version], [runtime/library], [model artifact], [quantization], [tokenizer], [sampler/output policy], and [measurement boundary]. They support stack-specific claims under the stated boundary and do not establish hardware-class, vendor-class, or unit-general results without independent replication or calibration evidence.`

F-C523-TRANSFER-ECONOMICS: transfer energy/time per GiB.

- x-axis: measured effective throughput (MiB/s) or nominal link label.
- y-axis: transfer energy (J/GiB); companion panel transfer time (s/GiB).
- Caption embeds the same single-unit language and D-049 boundary label.
  For unlike boundaries, add: `Boundary labels differ across cells, so absolute energy values are descriptive rather than a calibrated cross-target ranking.`

F-C523-DESERIALIZE: cache-load cost vs payload.

- x-axis: measured payload size (MiB or GiB).
- y-axis: deserialize/cache-load energy (J) and time (s).
- Caption states that cache load is not decode energy.

F-C523-PREDICTION-ERROR: model residuals.

- x-axis: runtime x model x prompt length.
- y-axis: prediction error percent and joules where energy is modeled.
- Caption states whether the result is measured transfer/deserialize or
  analytical composition.

## Hardware Prerequisites

- P1-004 link topology and measured throughput evidence.
- P1-006 second-node/device telemetry and remote transport evidence.
- Runtime cache persistence verdict from `docs/phase_3/kv_feasibility.md`.
- P2-015 floors or AP-specific bounds for transfer/deserialize before L2
  stage-economics wording.
- Same runtime and pinned cache format on both ends for real replay.

## Plug-In-Day Runbook

Existing commands:

`kv-size` prints an analytic size calculation only. The prompt-cache spike
writes a spike report under `--workdir`, not a standard run bundle.
`validate-bundle`, `reduce`, and `package_bundle_pack.py` apply only after a
bundle-producing step has run: the PLANNED transfer-bench/split-replay commands
below, or v0.1 monolithic reference runs borrowed from the split-suite pack.

```sh
python3 -m joulewise kv-size /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit/config.json --prompt-tokens 512,2048,8192
python3 scripts/spike_mlx_prompt_cache.py run --model /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit --prompt-len 1024 --decode 64 --workdir runs/spikes/c5-2-3-mlx-cache --keep
python3 scripts/run_campaign.py configs/campaign_packs/<<C523_REFERENCE_CONFIG_DIR>> --runs-dir runs --log runs/experiments/<<C523_EXPERIMENT_ID>>.jsonl --backup
python3 -m joulewise validate-bundle --strict runs/<<BASE_RUN_ID>>__r1
python3 -m joulewise reduce runs/<<BASE_RUN_ID>>__r1
python3 scripts/package_bundle_pack.py --output runs/bundle_packs/<<PACK_ID>> runs/<<BASE_RUN_ID_A>>__r1 runs/<<BASE_RUN_ID_B>>__r1
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<PACK_ID>>
```

PLANNED commands:

```sh
# PLANNED, owner: Phase 3 Stage 3.1 in docs/phase_3/phase_3_plan.md; no current TASK_QUEUE row.
python3 -m joulewise transfer-bench configs/campaign_packs/<<C523_TRANSFER_CONFIG>>.json --runs-dir runs

# PLANNED, owner: Phase 3 Stage 3.2 in docs/phase_3/phase_3_plan.md; no current TASK_QUEUE row.
python3 -m joulewise run configs/campaign_packs/<<C523_SPLIT_REPLAY_CONFIG>>.json --runs-dir runs

# PLANNED, owner: Phase 4 analysis implementation; no current TASK_QUEUE row.
python3 -m joulewise kv-economics-reduce runs/bundle_packs/<<PACK_ID>> --output runs/analysis/<<C523_RESULTS>>.json
```

Operator sequence:

0. Acquire the no-agent quiet-machine lock (`[QUIET-MAC]`; see
   `docs/orchestration.md`): stop all agent/Codex load for the whole
   measurement session and confirm machine-idle state before the first idle
   baseline.
1. Create `configs/campaign_packs/` if needed, copy the filled template JSON
   into that directory, generate analytic KV-size predictions, and record
   model-config hashes.
2. Run cache persistence spike for the target runtime and record verdict.
3. Freeze AP row and manifest with exact runtime/model/link/payload cells,
   explicitly separating synthetic payload ladder cells from prompt-derived
   KV-cache cells.
4. Generate or hand-author `configs/campaign_packs/<<C523_CONFIG_DIR>>/order_manifest.json`
   with schema `joulewise.order_manifest.v1`, including rotated
   runtime/model/link/payload order and start/end `short_short_sentinel`
   entries that must execute as the first and last measured bundles bracketing
   each hardware session. See `docs/campaign_packs/README.md` for the
   campaign-order versus intra-suite-order distinction. Extending
   `scripts/generate_matrix.py` for C5-2.3 transfer matrices is a PLANNED
   prerequisite owned by Phase 3 Stage 3.1 if the manifest is not hand-authored.
5. Execute transfer/deserialization campaign once planned commands exist.
6. Strict-validate, reduce, package, verify member bundles
   (`runs/<base_run_id>__rN`), then compare measured payload, transfer, and
   deserialize terms against the frozen predictions.

Closing cooldown-gate note: the D-014 cooldown gate between repetitions is
runner-automated, but cooldown cap-hit flags must be checked in each member
bundle's measurement quality before analysis.
