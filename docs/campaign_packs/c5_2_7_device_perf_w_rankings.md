# C5-2.7 Pack: Device Perf/W Rankings With Runtime Revision Held Constant

Status: pre-hardware DRAFT. This pack is methodologically preparable, but
execution waits on P1-006 target access and the 3080 Ti borrow window.

Runtime-constant wording is conditional: the runtime revision and build family
are held constant, build flags are recorded, and backend kernels differ by
platform and are named. Same-binary execution is not required across ISA.

## Pinned Now

- Finite device/runtime/model/quant/workload selection scope.
- Same llama.cpp revision/build family, same model artifact, quantization,
  tokenizer, sampler, and output policy wherever the platform supports them.
- Request energy is primary; perf/W and token metrics are companions with
  runtime-observed denominators.
- Rank gaps must clear the active MDE/floor gate. Otherwise the verdict is
  `unresolved tie`.
- Cross-device ranking is per measurement boundary unless a calibration bridge
  exists.

## DRAFT AP Row

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-C5-2.7 / C5-2.7 device perf/W rankings with runtime held constant. DRAFT until registry freeze. |
| family_id | FAM-C5-27-DEVICE-RANKS |
| claim_role | primary |
| selection_scope | Frozen candidate set of devices `<<P1-006.DEVICE_SET>>`, optional borrowed `<<P1-006.3080TI_TARGET_OR_OMIT>>`, one llama.cpp revision/build family `<<P1-006.LLAMACPP_REVISION>>`, named backend kernels per platform, one model artifact, one quantization, one tokenizer, one sampler/output policy, workload shapes `{1024/256,4096/256,1024/512}` or a narrower frozen subset, and one boundary label family per rank table. Countable contrasts are all pairwise rank gaps within each frozen boundary x workload x metric family. |
| multiplicity_rule | Holm within FAM-C5-27-DEVICE-RANKS for predeclared within-boundary device rank gaps by workload and metric. Any cross-boundary rank, added device, added workload, or backend-kernel subset not frozen before execution is exploratory. |
| Metric + exact window class | Primary: request energy `energy_request_j` and `gross_energy_j` on idle-subtracted and gross request windows under a named boundary. Companions: runtime-observed output tokens/s, request latency, throughput/W, and J/output-token with tokenizer scope. |
| Unit of analysis + dependence structure | Bundle repetition within device x workload x boundary x runtime-build cell. Workloads within a session are blocked by device and order; repeated bundles, not token windows, are replicates. |
| Estimator/formula | Within each boundary x workload x metric family, estimate device pair gap `delta = metric(device_b) - metric(device_a)` using block/session covariates when frozen. Rank order is declared only when every adjacent rank gap clears `max(floor_abs_j, floor_cmp_j)` and the predeclared comparison MDE; otherwise adjacent devices are reported as `unresolved tie`. Perf/W uses measured work divided by request energy and is companion-only. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only. Include only cells with stack-identity table, llama.cpp revision, build family, build flags, backend kernel name, model artifact hash, quantization, tokenizer identity, sampler/output policy, runtime-observed token denominators, and boundary label. D-014 quality waivers must be named before registry freeze. |
| Order/blocking/covariates | Counterbalance workload order per device with start/end `short_short_sentinel` bundles bracketing each hardware session. Include device session, order position, ambient/cooldown flags, and backend-kernel label as recorded covariates when frozen. |
| Floor gate | pending-P2-015: consume `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, `DF-RQ-GROSS-LONG-PROMPT`, `DF-RQ-IDLE-LONG-PROMPT`, `DF-RQ-GROSS-LONG-DECODE`, `DF-RQ-IDLE-LONG-DECODE`, and `DF-CMP-ABBA-RQ` for matching request-window metrics. Any rank metric/window without a matching P2-015 row is capped at L1/descriptive until a floor row or accepted AP-specific bound exists. |
| MDE/n sizing + predeclared top-up rule | Preserve n>=5 per headline device x workload cell. Sizing authority: D-062 + `configs/analysis_registry/<<C527_ANALYSIS_REGISTRY>>.json` (frozen n; no outcome-based top-ups without demotion). |
| Denominator provenance requirement | Runtime-observed output tokens, stop reason, request latency, llama.cpp revision, build family, build flags, backend kernel name, model artifact hash, quantization, tokenizer identity, sampler/output policy, batching policy, boundary label, telemetry backend, and per-device environment capture. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L2 within boundary; L4 with second unit/calibration`. Forbidden upgrade: `no generic hardware ranking from heterogeneous boundaries`. |
| Disqualifiers + not-resolvable conditions | Rank gap <= comparison MDE, missing P2-015 floor row for the metric/window class, boundary mismatch without calibration, unrecorded backend kernel, runtime revision/build-family drift, model artifact drift, missing runtime-observed denominators for token companions, or single-unit evidence used for hardware-class wording. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## Manifest/Config Templates

Typed-config shaped templates are placeholders until P1-006 supplies target
evidence. Each `<<P1-006.*>>` slot must be filled or explicitly omitted before
registry freeze.

```json
{
  "schema_version": "0.1",
  "run_id": "c5-2-7-<<P1-006.DEVICE_ID>>-llamacpp-<<P1-006.LLAMACPP_REVISION>>-p1024-d256",
  "model": {
    "name": "<<P1-006.MODEL_NAME>>",
    "family": "<<P1-006.MODEL_FAMILY>>",
    "source": "<<P1-006.MODEL_PATH>>",
    "revision": "<<P1-006.MODEL_REVISION_OR_HASH>>",
    "weight_format": "gguf",
    "context_window": "<<P1-006.CONTEXT_WINDOW>>"
  },
  "quantization": {
    "name": "<<P1-006.QUANT_NAME>>",
    "bits": "<<P1-006.QUANT_BITS>>"
  },
  "hardware_target": {
    "id": "<<P1-006.DEVICE_ID>>",
    "transport": "<<P1-006.TRANSPORT>>",
    "host": "<<P1-006.SSH_HOST_OR_OMIT_FOR_LOCAL>>",
    "runtime_backend": "llama.cpp",
    "telemetry_backend": "<<P1-006.TELEMETRY_BACKEND>>",
    "device_kind": "<<P1-006.DEVICE_KIND>>",
    "notes": "C5-2.7 runtime revision held constant; backend kernels named in stack_identity."
  },
  "runtime": {
    "name": "llama.cpp",
    "revision": "<<P1-006.LLAMACPP_REVISION>>",
    "build_family": "<<P1-006.LLAMACPP_BUILD_FAMILY>>",
    "build_flags": "<<P1-006.LLAMACPP_BUILD_FLAGS>>",
    "backend_kernel": "<<P1-006.BACKEND_KERNEL_NAME>>"
  },
  "workload_profile": {
    "name": "device_rank_p1024_d256",
    "prompt_tokens": 1024,
    "output_tokens": 256,
    "repetitions": 5,
    "warmup_runs": 1
  },
  "sampling": {
    "power_hz": 10.0,
    "idle_seconds": 30.0,
    "warmup_seconds": 5.0
  },
  "run_metadata": {
    "project": "capstone-joulewise",
    "operator": "ed",
    "tags": ["c5-2.7", "device-rank", "llamacpp-runtime-held-constant"]
  }
}
```

`order_manifest.json` must enumerate device x workload cells, start/end
sentinels, boundary labels, and the exact rank families. The stack-identity
table records OS, runtime revision/build family, build flags, backend kernel,
model artifact hash, quantization, tokenizer, sampler/output policy,
batching/concurrency policy, measurement boundary, and telemetry backend.

## Expected Artifacts

```text
runs/<base_run_id>__rN/
  config.json
  metadata.json
  events.jsonl
  power_trace.csv
  summary_metrics.json
  outputs/
    response.txt
    provenance.json
  raw/
    telemetry_backend_artifacts
runs/experiments/<base_run_id>.json
runs/analysis/c5-2-7/
  stack_identity_table.csv
  rank_family_registry.json
  boundary_rank_results.json
```

Every artifact set must retain the runtime build record, backend kernel name,
boundary label, and runtime-observed denominator evidence. Unlike-boundary
cells may be shown together only as descriptive, boundary-labeled rows unless
a calibration bridge is present.

## Figure Skeletons

F-C527-BOUNDARY-RANK-TABLE: boundary-labeled device rank table.

- Rows: frozen device cells.
- Columns: request energy, throughput, perf/W companion, rank verdict, MDE
  gap, and boundary label.
- Caption includes the capstone single-unit limitation language and the full
  token-normalization stack identity fields. It states that runtime revision is
  held constant while backend kernels differ by platform and are named.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

F-C527-ENERGY-THROUGHPUT: request energy vs throughput.

- x-axis: runtime-observed output tokens/s or request latency.
- y-axis: request energy under the named boundary.
- Caption co-displays request energy with any token companion and names the
  tokenizer identity. Cross-boundary points are descriptive unless calibrated.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

F-C527-WORKLOAD-STABILITY: workload-rank stability.

- x-axis: workload shape.
- y-axis: rank or rank gap with uncertainty.
- Caption says adjacent gaps that do not clear MDE/floor are `unresolved tie`.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

## Gates

- P1-006 device access, telemetry evidence, and 3080 Ti borrow window.
- Boundary comparability or explicit per-boundary rank tables only.
- P2-015 floors for each metric/window class.
- L4 wording requires second unit, calibration, and replication evidence, not
  this pack alone.

## Refusals

- Do not present cross-device ranks as generic hardware ranks across
  heterogeneous boundaries.
- Do not claim same binary or same kernel across ISA; claim only same runtime
  revision/build family with backend kernels named.
- Do not rank adjacent devices when the rank gap does not clear MDE/floor.

## Plug-In-Day Runbook

Existing commands:

```sh
python3 -m joulewise validate-config configs/campaign_packs/<<C527_CONFIG>>.json
python3 scripts/run_campaign.py configs/campaign_packs/<<C527_CONFIG_DIR>> --runs-dir runs --log runs/experiments/<<C527_EXPERIMENT_ID>>.jsonl --backup
python3 -m joulewise validate-bundle --strict runs/<<BASE_RUN_ID>>__r1
python3 -m joulewise reduce runs/<<BASE_RUN_ID>>__r1
python3 scripts/package_bundle_pack.py --output runs/bundle_packs/<<PACK_ID>> runs/<<BASE_RUN_ID_A>>__r1 runs/<<BASE_RUN_ID_B>>__r1
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<PACK_ID>>
```

PLANNED commands:

```sh
# PLANNED, owner: C5-2.7 reduction after P1-006 targets exist.
python3 -m joulewise rank-devices runs/bundle_packs/<<PACK_ID>> --output runs/analysis/c5-2-7/results.json
```

Operator sequence:

0. Acquire the no-agent quiet-machine lock (`[QUIET-MAC]`): stop all
   agent/Codex load for the whole measurement session and confirm machine-idle
   state before the first idle baseline.
1. Fill target configs from P1-006 evidence, record llama.cpp revision/build
   family, build flags, and backend kernel name for every platform.
2. Freeze AP row, rank families, order manifest, and boundary labels before
   any bundle executes.
3. Run device/workload campaign with sentinels bracketing each hardware
   session.
4. Strict-validate, reduce, package, and verify member bundles.
5. Apply rank rule. Any adjacent gap that fails the active floor/MDE gate is
   reported as `unresolved tie`.

Closing cooldown-gate note: the D-014 cooldown gate between repetitions is
runner-automated, but cooldown cap-hit flags must be checked in each member
bundle's measurement quality before analysis.
