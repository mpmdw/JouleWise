# Node Worker Protocol (cross-cutting contract)

Status: wire format v1 pinned 2026-07-07 during Slice 2K - PROVISIONAL
pending first live hardware validation. Do not implement remote execution
against any other model.

## The idea

Remote execution is a project-wide protocol, not an SSH or vLLM detail:

```text
controller ──(transport)──► node worker
   sends: one JSON task file (what to run: runtime workload, telemetry
          action, or transfer action; plus config subset + timing markers)
   node:  executes with only its local environment (the joulewise
          package is NOT installed remotely)
   returns: an artifacts directory — events JSON, outputs, raw telemetry,
          worker log, exit/status code — collected back into the bundle
```

The transport (SSH today; anything later) only moves files and starts
processes. The protocol — task shape, artifact layout, status codes,
clock-marker discipline (D-003) — is transport-independent and shared by:

- Slice 2K (NVIDIA/vLLM + nvidia-smi over SSH) — first implementer;
  pinned specifics live in the hardware guide §2K and get promoted here
  as they stabilize.
- Slice 2L (Orin) — same protocol, different runtime/telemetry payloads.
- Phase 3 Stage 3.1+ (transfer microbenchmark, split runs) — adds
  transfer tasks (send/receive payload with both-end timing/energy) and
  `node_role` (prefill/decode; carried by D-024's RunContext), feeding
  composite bundles per the run-bundle layout's composite block.

For SSH transport targets, `hardware_target.host` is an opaque OpenSSH
destination string. It is passed verbatim to `ssh`/`scp`; user, port, key,
and identity details come from OpenSSH config rather than JouleWise schema
fields. The SSH argv terminator is placed before the destination:
`ssh <opts> -- <destination> <remote argv...>`. SCP uses the same rule:
`scp <opts> -- <src> <dst>`.

The remote node does not import or install `joulewise`. The shipped worker
mirrors D-012 `FailureReason` string values in its own file and must not
import the package.

## Task JSON v1

One task is one JSON object passed by file path to the worker. The artifacts
directory is an argv value, not a JSON field. Controller timestamps are not
embedded in the task because they are stale by remote dispatch time.

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `protocol_version` | yes | integer | Must be `1`. Strings such as `"1"` are invalid. |
| `task_id` | yes | string | Identifies this worker invocation in collected artifacts. |
| `run_id` | yes | string | Identifies the parent run. |
| `task_type` | yes | string | Open enum: `runtime`, `telemetry`, `transfer-send`, `transfer-receive`. |
| `operation` | yes | string | Scoped by task type. Runtime: `prepare`, `warmup`, `run_workload`, `cleanup`. Telemetry: `measure_idle`, `start_sampling`, `stop_sampling`. |
| `node_role` | yes | string or null | Phase 3 role such as `prefill`/`decode`; null for single-node Slice 2K tasks. |
| `timeout_s` | yes | number | Controller-supplied task timeout. vLLM readiness honors this value; if omitted by a legacy client, the worker defaults readiness to 300 s. |
| `paths.state_dir` | yes | string | Remote persistent working directory for pidfiles, ports, and run-scoped state shared across tasks. The controller derives it from each task's `run_id` as `<remote_work_root>/<run_id>/state`; the worker creates it if needed. |
| `runtime` | task-specific | object | Exactly one task-specific block is present. Used for runtime `prepare`, `warmup`, and `cleanup`; contains `model`, `quantization`, and backend `options`. |
| `workload` | task-specific | object | Used for runtime `run_workload`; contains prompt/output token targets and deterministic `sampling_params`. |
| `telemetry` | task-specific | object | Used for telemetry operations; contains backend, interval, query fields, and rail manifest. |

Runtime example for a realistic RTX 3050 target:

```json
{
  "protocol_version": 1,
  "task_id": "task-runtime-prepare-3050-001",
  "run_id": "run-3050-smoke-001",
  "task_type": "runtime",
  "operation": "prepare",
  "node_role": null,
  "timeout_s": 900.0,
  "paths": {
    "state_dir": "/tmp/joulewise/run-3050-smoke-001/state"
  },
  "runtime": {
    "backend": "vllm",
    "model": {
      "name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
      "revision": "main",
      "weight_format": "safetensors"
    },
    "quantization": {
      "name": "none"
    },
    "options": {
      "tensor_parallel_size": 1,
      "gpu_memory_utilization": 0.82,
      "served_model_name": "jw-3050-smoke"
    }
  }
}
```

Telemetry example for the same target:

```json
{
  "protocol_version": 1,
  "task_id": "task-telemetry-start-3050-001",
  "run_id": "run-3050-smoke-001",
  "task_type": "telemetry",
  "operation": "start_sampling",
  "node_role": null,
  "timeout_s": 30.0,
  "paths": {
    "state_dir": "/tmp/joulewise/run-3050-smoke-001/state"
  },
  "telemetry": {
    "backend": "nvidia_smi",
    "interval_ms": 100,
    "query_fields": [
      "timestamp",
      "power.draw",
      "temperature.gpu"
    ],
    "rail_manifest": [
      "gpu_board"
    ]
  }
}
```

## Artifacts Directory

The worker creates the artifacts directory before parsing the task file. It
always attempts to write these protocol-owned files:

- `worker.log`: plain text, one timestamped line per record.
- `status.json`: authoritative structured result, written through a temporary
  file followed by atomic replace.

Operation handlers may add flat files in the same directory. Pinned names for
later 2K units are `events.jsonl`, `response.txt`, `tokens.jsonl`,
`nvidia_smi.csv`, and `nvidia_smi_idle.csv`. The controller collects the
entire flat directory. Bundle mapping is: response/tokens under `outputs/`,
CSV under `raw/` verbatim per D-002, worker log under `logs/`, and events
merged into the run's runtime result.

`status.json` contains exactly:

| Field | Type | Notes |
| --- | --- | --- |
| `protocol_version` | integer | `1`. |
| `task_id` | string or null | Null when unknown because parsing failed before identity was available. |
| `task_type` | string or null | Null when unknown. |
| `operation` | string or null | Null when unknown. |
| `node_role` | string or null | Mirrors the task value when known. |
| `status` | string | One of `succeeded`, `failed`, `unsupported`. |
| `failure_reason` | string or null | D-012 string value mirrored by the worker, or null on success. |
| `message` | string | Human-readable summary. |
| `started_at_s` | number | Node `time.time()` at worker start. |
| `ended_at_s` | number | Node `time.time()` at worker end. |
| `monotonic_started_s` | number | Node `time.monotonic()` at worker start. |
| `monotonic_ended_s` | number | Node `time.monotonic()` at worker end. |
| `artifacts` | object | Map from logical artifact name to relative filename actually written. |
| `metadata` | object | Open metadata dictionary. For remote stages, adapter metadata persists worker metadata from `status.json.metadata` under bundle `metadata.json` as `metadata.adapters.<runtime|telemetry>.worker_metadata`, and also persists the corresponding controller-side `clock_alignment` records under `metadata.adapters.<runtime|telemetry>.clock_alignments[]`. |

Worker exit code is secondary crash evidence: `0` iff `status == "succeeded"`,
`1` otherwise, and `2` only when the worker cannot even create or write the
artifacts path.

For vLLM `runtime.run_workload`, the worker calls the same server's
`POST /tokenize` endpoint before streaming `POST /v1/completions`. On
success, `status.json.metadata.prompt_token_ids` records the realized prompt
token IDs and `prompt_token_count` records their count. If `/tokenize` is
unavailable or does not expose token IDs, the workload may still stream, but
metadata records `prompt_token_ids_unavailable_reason` with `source`,
`endpoint`, `error_class`, and `message`; adapters must not synthesize token
IDs for the D-033 v1 prompt-token hash.

## Failure Taxonomy

The controller remains the only `FailureReason` to run-status mapper. Remote
worker and transport code report the following D-012 strings:

| Condition | `status` | `failure_reason` |
| --- | --- | --- |
| Unreachable host, missing `ssh`/`scp`, SSH auth or name-resolution failure, artifact collection failure | `failed` | `transport_unavailable` |
| Missing `nvidia-smi` or unsupported `nvidia-smi` query | `unsupported` | `telemetry_unavailable` |
| vLLM launcher missing, `ModuleNotFoundError`, or `ImportError` during readiness | `unsupported` | `runtime_unavailable` |
| CUDA/vLLM out of memory while loading or running | `unsupported` | `did_not_fit` |
| Runner crash, malformed or missing `status.json`, malformed task JSON, invalid protocol version, missing required field | `failed` | `unknown_error` |
| Task type or operation not known to this worker build | `unsupported` | `unsupported_workload` |

SSH authentication details stay in message/metadata, for example
`ssh_error_class`; they are not recast as `permission_denied`. That reason is
reserved for on-node privilege semantics.

## Clock Markers

The transport takes pre/post no-op markers around every remote stage by
running the worker's clock echo mode:

```sh
python3 node_worker.py --clock-echo
```

The command prints one JSON line:

```json
{"node_time_s": 1783460000.125, "monotonic_s": 84321.5}
```

For each marker, the controller records:

```text
c_before = controller clock before ssh
node_time = echoed node_time_s
c_after = controller clock after ssh
offset_estimate = node_time - (c_before + c_after) / 2
rtt_bound = (c_after - c_before) / 2
```

For a stage with pre and post markers:

```text
offset_bound =
  max(pre.rtt_bound, post.rtt_bound)
  + abs(post.offset_estimate - pre.offset_estimate)
```

Adapter metadata records `clock_alignment` with the stage name, method name,
pre/post marker records, `offset_estimate_s`, and `offset_bound_s`.
Worker `status.json.metadata` records such as `node_utc_offset_s` are persisted
under the corresponding adapter's `worker_metadata` block so raw node-local
wall-clock artifacts can be re-parsed without relying on the reducer process's
local timezone.
`metadata.json` persists every remote runtime stage alignment
(`prepare`, `warmup`, `run_workload`, `cleanup`) and every remote telemetry
stage alignment (`measure_idle`, `start_sampling`, `stop_sampling`) under
`metadata.adapters.<runtime|telemetry>.clock_alignments[]`. Node-stamped
derived data is converted to the controller clock domain by subtracting
`offset_estimate_s` before creating `PowerSample`, `RuntimeEvent`, or other
derived artifacts. Raw files remain verbatim in the node clock domain per
D-002 so the conversion can be re-derived. Phase 3 reducers add bounds from
both nodes and flag cross-node intervals shorter than that uncertainty.

## Remote Path Layout

The controller ships one worker script per `NodeWorkerClient` to:

```text
<remote_work_root>/node_worker.py
```

Each task's `run_id` derives isolated per-run directories:

```text
<remote_work_root>/<run_id>/tasks/<task_id>.json
<remote_work_root>/<run_id>/artifacts/<task_id>/
<remote_work_root>/<run_id>/state/
```

There is no `pending-run-id` fallback. The bundle-created run id carried in
task JSON is authoritative.

## nvidia-smi Timestamp And CSV Rules

The worker records the node timezone at sampling start and idle capture in
metadata and `nvidia_smi.pid`:

```json
{"node_utc_offset_s": 0.0, "node_tzname": "UTC"}
```

The controller parses naive `YYYY/MM/DD HH:MM:SS.mmm` CSV timestamps with
that node UTC offset before applying the B-5 clock alignment. Legacy artifacts
without `node_utc_offset_s` fall back to the controller/parser local timezone
and record a provenance warning in parse diagnostics.

The parser skips a malformed final unterminated CSV row and records the
diagnostic count. Malformed interior rows remain hard parse errors.

## Pidfile Safety

Before signaling a PID from `vllm.pid` or `nvidia_smi.pid`, the worker verifies
that the live process command line matches the pidfile command. On Linux it
also compares `/proc/<pid>/stat` start time with `node_started_at_s`; when
`/proc` is unavailable it falls back to `ps -p <pid> -o args=` command-line
matching. A mismatch is a stale pidfile: runtime cleanup succeeds with a
stale-pidfile note and removes the pidfile; telemetry `stop_sampling` fails
structurally without producing a CSV and removes the pidfile.

## Worker Invocation

Normal task execution:

```sh
python3 node_worker.py --task /path/to/task.json --artifacts /path/to/artifacts
```

Clock marker execution:

```sh
python3 node_worker.py --clock-echo
```

The worker is importable for local tests but guarded with `if __name__ ==
"__main__"` for script execution.

## Requirements the wire format must satisfy (checklist for 2K)

- One task = one JSON file; schema documented here when pinned; versioned
  field from day one.
- Worker depends only on the remote environment (stdlib + the runtime
  under test); single self-contained script shipped per task.
- Every task returns a complete artifacts dir even on failure —
  structured status/failure_reason mirroring D-012, never a bare crash.
- Clock markers before/after each remote stage bound node clock offset
  (D-003); the bound travels back in the artifacts.
- Raw telemetry produced remotely lands verbatim in the collected
  artifacts and then under the bundle's `raw/` (D-002).
- Phase 3 headroom: task types are an open enum (runtime / telemetry /
  transfer-send / transfer-receive); a task may name the node's role.

## Non-goals

- No persistent JouleWise remote daemon; workers are per-task processes.
  A worker task may start long-lived backend child processes on the node,
  such as the `nvidia-smi` sampler or a `vllm serve` process, recorded under
  `paths.state_dir` with pidfiles/ports and stopped by later worker tasks.
- No remote joulewise install; the protocol is the interface.
- No live streaming in v1 (Phase 3 Stage 3.3 is stretch and revisits).
