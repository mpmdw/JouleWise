# Q6 / C5-2.10 Pack: Rail-Vs-Wall Boundary Sensitivity

Status: pre-hardware DRAFT. The AP row is not frozen until the boundary-pair
hardware and calibration manifest are known.

## DRAFT AP Row

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-Q6-C5-2.10 / Q6 boundary sensitivity; C5-2.10 boundary-directional bias quantification. DRAFT until registry freeze. |
| family_id | FAM-Q6-RAIL-WALL-BOUNDARY |
| claim_role | primary |
| selection_scope | Frozen paired boundary campaign for `<<TARGET_DEVICE>>`, platform telemetry backend `<<RAIL_BACKEND>>`, external boundary `wall_meter` or `USB-C PD/DC`, workload profiles `{mid_mid, long_prompt if feasible, long_decode if feasible}`, one model artifact, one runtime, and matched platform-vs-external windows. |
| multiplicity_rule | Holm within FAM-Q6-RAIL-WALL-BOUNDARY across predeclared workload-profile boundary deltas and conclusion-flip tests. Any post-hoc workload, boundary, or backend subset is exploratory. |
| Metric + exact window class | Primary: workload-induced delta energy by boundary on gross request windows and idle-subtracted request windows: `delta_external_j`, `delta_platform_j`, `external_minus_platform_j`, and sign/direction of any conclusion flip. Calibration descriptors may include session-window idle and sustained blocks. |
| Unit of analysis + dependence structure | Paired block: the same workload execution or matched active block with simultaneous platform telemetry and external meter trace. Platform and external readings in a block are dependent paired measurements. |
| Estimator/formula | Fit or summarize paired boundary difference `external_minus_platform_j = delta_external_j - delta_platform_j` by workload family. If at least three active load levels exist, fit the detection-floor runbook bridge `delta_external_j = alpha + beta * delta_platform_j + residual_j`; quantitative bridge accepted only when held-out or cross-validated residuals satisfy the P2-015 threshold. A conclusion-flip test is predeclared as whether a same-condition ordering changes sign between boundary estimates. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid JouleWise bundles plus external meter artifact required. Exclude blocks without synchronization evidence, meter calibration/status, meter cadence, platform rail manifest, shared marker plan/manual sync note, or matched window definitions. Waivers must be named in the frozen registry and cannot turn missing external evidence into a calibrated claim. |
| Order/blocking/covariates | ABBA or paired step-load blocks where feasible: idle, active A, active B, idle, then reversed order. For repeated LLM workloads, counterbalance profile order per D-014/C-011 conventions and record cooldown cap hits. Include block/session and meter-cadence covariates only if frozen. |
| Floor gate | pending-P2-015: consume `DF-RQ-GROSS-MID` (`gross_energy_j`, gross request), `DF-RQ-IDLE-MID` (`energy_request_j`, `idle_subtracted_energy_j`, idle-sub request), optional `DF-RQ-GROSS-LONG-PROMPT` / `DF-RQ-IDLE-LONG-PROMPT` for long-prompt claims, optional `DF-RQ-GROSS-LONG-DECODE` / `DF-RQ-IDLE-LONG-DECODE` for long-decode claims, and `DF-CMP-ABBA-RQ` (`gross_energy_j`, `energy_request_j`, request windows). Phase-window boundary claims additionally consume `DF-PH-PREFILL`, `DF-PH-DECODE`, and `DF-CMP-ABBA-PH` only if cadence and clock thresholds clear. |
| MDE/n sizing + predeclared top-up rule | n>=5 paired blocks per primary workload family; top up to n=10 if the boundary-delta CI crosses the floor gate, if the bridge residual threshold is near-failing, or if a conclusion-flip verdict changes under leave-one-out. |
| Denominator provenance requirement | Runtime-observed output tokens, stop reason, output policy, platform rail manifest, external meter make/model/calibration/status, meter resolution/cadence/logging mode, synchronization method, and matched window IDs. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L2; L4 only with replication`. Forbidden upgrade: `no wall/rail conclusion flip claim without paired boundary plan`. |
| Disqualifiers + not-resolvable conditions | No external meter trace; unmatched platform/external windows; missing rail manifest; missing meter calibration/status; clock/sync bound too large; floor missing for the metric/window class; bridge residual above threshold; or single-unit evidence used for vendor/hardware-class wording. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## Manifest/Config Template

The JouleWise workload half is current v0.1. External-meter capture/import is
PLANNED under P1-003 wall-meter evidence and P2-015 calibration runbooks. The
`<<BOUNDARY_PAIR.*>>` placeholders are the only target/boundary slots.

```json
{
  "schema_version": "0.1",
  "run_id": "q6-boundary-<<BOUNDARY_PAIR.TARGET_DEVICE>>-mid-mid-r1",
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
    "id": "<<BOUNDARY_PAIR.TARGET_DEVICE>>",
    "transport": "<<BOUNDARY_PAIR.TRANSPORT>>",
    "host": "<<BOUNDARY_PAIR.SSH_HOST_OR_OMIT_FOR_LOCAL>>",
    "runtime_backend": "<<BOUNDARY_PAIR.RUNTIME_BACKEND>>",
    "telemetry_backend": "<<BOUNDARY_PAIR.RAIL_BACKEND>>",
    "device_kind": "<<BOUNDARY_PAIR.DEVICE_KIND>>",
    "notes": "Q6 paired rail-vs-wall boundary campaign; external meter trace is paired outside current v0.1 config."
  },
  "workload_profile": {
    "name": "boundary_mid_mid",
    "prompt_tokens": 512,
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
    "tags": ["q6", "c5-2.10", "boundary", "rail-vs-wall"]
  }
}
```

Order policy: execute repeated profiles in ABBA-like paired order where A and B
are identical JouleWise workload labels under simultaneous external metering.
For step-load calibration, alternate idle and sustained active blocks with at
least three transitions and reverse the active-load order across blocks.

## Expected Artifacts

Standard run bundles must contain `config.json`, `metadata.json`,
`events.jsonl`, `power_trace.csv`, raw telemetry under `raw/`, logs, outputs,
and `summary_metrics.json`, per `docs/contracts/run_bundle_layout.md`.

Additional expected external-meter artifacts:

```text
runs/<run_id>/
  external_meter/
    meter_metadata.json
    trace.csv
    sync_notes.json
```

`metadata.json` must include the platform rail manifest required by D-018.
`external_meter/meter_metadata.json` records make/model, calibration
date/status, stated accuracy, resolution, sampling cadence, logging mode, and
synchronization method. The marker/clock-offset expectations follow D-003:
shared marker plan or manual synchronization notes are recorded, and any
window shorter than the recorded clock/sync bound is not used for attribution.

Comparisons are like-window and like-workload only: platform request window
against external request window, platform idle block against external idle
block. Cross-boundary ranking language is not allowed unless the paired bridge
clears its predeclared residual threshold.

## Figure Skeletons

F-Q6-BOUNDARY-SCATTER: external vs platform workload-induced energy.

- x-axis: platform rail/model energy delta (J), boundary label
  `<<RAIL_BACKEND>>`.
- y-axis: external meter energy delta (J), boundary label `wall_meter full
  system AC` or `USB-C PD/DC input`.
- Caption template: `Measurements in this figure characterize one physical unit of [target hardware] running [OS/version], [runtime/library], [model artifact], [quantization], [tokenizer], [sampler/output policy], and [measurement boundary]. They support stack-specific claims under the stated boundary and do not establish hardware-class, vendor-class, or unit-general results without independent replication or calibration evidence.`

F-Q6-BOUNDARY-RESIDUALS: bridge residual by workload family.

- x-axis: workload family/block.
- y-axis: `external_minus_platform_j` residual (J).
- Caption adds: `Boundary labels differ across cells, so absolute energy values are descriptive rather than a calibrated cross-target ranking.` when residual threshold has not cleared.

F-Q6-CONCLUSION-FLIP: direction by boundary.

- x-axis: frozen workload contrast.
- y-axis: paired contrast energy (J), with separate rail and wall/PD points.
- Caption states whether the flip test was predeclared and whether it cleared
  the floor gate.

## Hardware Prerequisites

- P1-003 wall meter or PD/DC analyzer decision, including export/logging
  method.
- P2-015 calibration artifact with the exact request-window floor rows named
  in the AP row.
- Platform telemetry backend and rail manifest for `<<TARGET_DEVICE>>`.
- Synchronization method that satisfies D-003 and P2-015 clock-bound gates.

## Plug-In-Day Runbook

Existing commands:

```sh
python3 -m joulewise validate-config configs/campaign_packs/<<Q6_CONFIG>>.json
python3 -m joulewise run configs/campaign_packs/<<Q6_CONFIG>>.json --runs-dir runs
python3 -m joulewise validate-bundle --strict runs/<<RUN_ID>>
python3 -m joulewise reduce runs/<<RUN_ID>>
python3 scripts/package_bundle_pack.py --output runs/bundle_packs/<<PACK_ID>> runs/<<RUN_ID_1>> runs/<<RUN_ID_2>>
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<PACK_ID>>
```

PLANNED commands:

```sh
# PLANNED, owner: P1-003 wall-meter evidence plus P2-015 calibration runbook.
python3 -m joulewise import-external-meter --bundle runs/<<RUN_ID>> --trace <<METER_TRACE_CSV>> --metadata <<METER_METADATA_JSON>>

# PLANNED, owner: P2-015 floor/calibration implementation.
python3 -m joulewise boundary-calibrate runs/<<RUN_ID_1>> runs/<<RUN_ID_2>> --output runs/analysis/<<Q6_RESULTS>>.json
```

Operator sequence:

1. Record meter make/model/calibration/export method before the first workload.
2. Fill config placeholders and freeze the AP row with complete contrast IDs.
3. Start external meter logging, run JouleWise workload bundles, and preserve
   meter traces with synchronization notes.
4. Strict-validate and reduce JouleWise bundles.
5. Import/pair external traces once the planned importer exists; otherwise
   keep external artifacts adjacent to bundles and cap claims at L1/descriptive.
