# Instrumentation And Permission Checklist

Status: pending physical-device confirmation.

## MacBook Pro M3 Max

- Runtime target: MLX.
- Telemetry target: powermetrics.
- Transport: local.
- Phase 1 status: partially checked on current controller.
- Observed:
  - Current machine architecture: `arm64`.
  - `powermetrics` binary found at `/usr/bin/powermetrics`.
- Checks:
  - [ ] MLX install path known.
  - [x] `powermetrics` binary present.
  - [ ] Required sudo/password workflow documented.
  - [ ] Thermal fields available.

## NVIDIA 3050

- Runtime target: vLLM.
- Telemetry target: nvidia-smi, optional wall meter.
- Transport: ssh.
- Phase 1 status: pending device access.
- Current controller note: `nvidia-smi` is not present locally, which is
  expected on the Mac controller and must be checked on the remote NVIDIA node.
- Checks:
  - [ ] SSH access.
  - [ ] CUDA runtime.
  - [ ] vLLM install path.
  - [ ] `nvidia-smi` power sampling available.
  - [ ] Wall-meter comparison path.

## NVIDIA 3080 Ti

- Runtime target: vLLM.
- Telemetry target: nvidia-smi, optional wall meter.
- Transport: ssh.
- Phase 1 status: pending borrow window.
- Checks:
  - [ ] Borrow window confirmed.
  - [ ] Memory limit documented.
  - [ ] Same checks as NVIDIA 3050.

## Jetson Orin Nano Super

- Runtime target: local inference stack, TBD.
- Telemetry target: Jetson rails or wall meter.
- Transport: ssh.
- Phase 1 status: pending device access.
- Checks:
  - [ ] SSH access.
  - [ ] Runtime path selected.
  - [ ] Board-rail telemetry accessible.
  - [ ] Wall-meter fallback available.

## Raspberry Pi 5 + Hailo-8L

- Runtime target: Hailo if viable.
- Telemetry target: wall meter.
- Transport: ssh.
- Phase 1 status: pending Hailo feasibility verdict.
- Checks:
  - [ ] Hailo toolchain installed.
  - [ ] LLM-shaped workload feasibility tested.
  - [ ] Verdict documented in `docs/phase_1/hailo_feasibility.md`.
