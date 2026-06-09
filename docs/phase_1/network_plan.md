# Network And Interconnect Plan

Status: pending hardware/network confirmation.

This file defines the evidence needed before the interconnect sweep is
implemented. It should be completed during Phase 1 and used again before Phase
3 experiments.

## Target Links

- 1GbE: baseline commodity Ethernet.
- 2.5GbE: planned switch/adapter path.
- 10GbE: optional extension if adapters are available.

## Planned Topology

Pending.

Record:

- Controller node.
- Prefill node.
- Decode node.
- Switch model.
- Adapter models.
- Cable type/length.
- Whether the benchmark link is isolated from general traffic.

## Link Verification

For each participating node, record the command used to verify negotiated link
speed.

Candidate commands:

- macOS: `networksetup -listallhardwareports`
- macOS: `ifconfig <interface>`
- Linux: `ethtool <interface>`

Expected evidence:

```text
interface:
configured speed:
negotiated speed:
duplex:
date checked:
```

## Throughput Verification

Use a controlled transfer test before benchmark KV-transfer experiments.

Candidate tools:

- `iperf3` if available.
- A fixed-size file transfer if `iperf3` is unavailable.

Expected evidence:

```text
link target:
tool:
payload size:
measured throughput:
run count:
notes:
```

## Transfer Measurement Policy

Every split/disaggregated run should record:

- Payload size in bytes.
- Serialization start/end.
- Transfer start/end.
- Deserialization/load start/end, when applicable.
- Link speed label.
- Measured throughput.
- Transfer-stage energy method: measured, modeled, or unavailable.

## Acceptance Criteria

This plan is ready when:

- All intended link speeds have a concrete hardware path or are explicitly
  marked unavailable.
- The link-speed verification command is known for each node.
- The throughput verification method is selected.
- Transfer-stage event fields are aligned with the run-bundle layout.
