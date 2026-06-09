# Network And Interconnect Plan

Status: partially checked on current controller; pending physical topology and
remote-node confirmation.

This file defines the evidence needed before the interconnect sweep is
implemented. It should be completed during Phase 1 and used again before Phase
3 experiments.

## Target Links

- 1GbE: baseline commodity Ethernet.
- 2.5GbE: planned switch/adapter path.
- 10GbE: optional extension if adapters are available.

## Planned Topology

Pending physical hardware confirmation.

Record:

- Controller node.
- Prefill node.
- Decode node.
- Switch model.
- Adapter models.
- Cable type/length.
- Whether the benchmark link is isolated from general traffic.

Current controller evidence from 2026-06-09:

- `ifconfig` is available and shows an active `en0` interface with
  `media: autoselect`.
- `networksetup -listallhardwareports` failed in this execution context with
  `AuthorizationCreate() failed: -60008`.
- `iperf3` is not installed on the current controller.

Do not treat the current Wi-Fi/home-network interface as the benchmark
interconnect. The benchmark interconnect still needs a dedicated physical
topology for 1GbE / 2.5GbE / optional 10GbE.

## Link Verification

For each participating node, record the command used to verify negotiated link
speed.

Candidate commands:

- macOS: `networksetup -listallhardwareports`
- macOS: `ifconfig <interface>`
- Linux: `ethtool <interface>`

Current command status:

- macOS `ifconfig`: works in current environment.
- macOS `networksetup -listallhardwareports`: authorization failure in current
  environment; retry in a normal terminal if needed.
- Linux `ethtool`: pending Linux node access.

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

Current tool status:

- `iperf3`: not installed on current controller.
- Fallback fixed-size file transfer remains available in principle but has not
  been tested against a remote node.

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

## Phase 1 Open Items

- Choose or confirm the 2.5GbE switch/adapters.
- Decide whether 10GbE is in scope.
- Identify controller, prefill, and decode nodes for each split experiment.
- Decide whether the benchmark network can be isolated from general traffic.
- Install or avoid `iperf3`; if avoiding it, define the fixed-size transfer
  procedure.
