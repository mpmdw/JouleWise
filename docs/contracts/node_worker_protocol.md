# Node Worker Protocol (cross-cutting contract)

Status: conceptual shape fixed (2026-07-06, from the external
architecture review); wire-level details are pinned into this document
during Slice 2K implementation. Do not implement remote execution
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

- No persistent remote daemon; workers are per-task processes.
- No remote joulewise install; the protocol is the interface.
- No live streaming in v1 (Phase 3 Stage 3.3 is stretch and revisits).
