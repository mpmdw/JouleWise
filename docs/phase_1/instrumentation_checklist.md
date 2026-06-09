# Instrumentation And Permission Checklist

Status: pending physical-device confirmation.

## Apple Silicon / Mac Target

- Runtime target: MLX.
- Telemetry target: powermetrics.
- Transport: local.
- Phase 1 status: partially checked on current Apple Silicon controller; repeat
  on the final M3 Max measurement target before claiming full support.
- Observed:
  - Current machine architecture: `arm64`.
  - `powermetrics` binary found at `/usr/bin/powermetrics`.
  - Current user id is non-root (`501`).
  - `powermetrics --help` lists machine-readable `plist` output and samplers:
    `thermal`, `cpu_power`, `gpu_power`, and `ane_power`.
  - A direct sample attempt with
    `powermetrics -n 1 -i 100 --samplers thermal,cpu_power,gpu_power,ane_power`
    failed with: `powermetrics must be invoked as the superuser`.
  - Python import checks show `mlx` and `mlx_lm` are not installed in the
    current Python environment.
- Checks:
  - [ ] MLX install path known.
  - [ ] MLX/MLX-LM installed or installation procedure documented.
  - [x] `powermetrics` binary present.
  - [x] Required superuser workflow identified.
  - [ ] Required sudo/password workflow approved for benchmark runs.
  - [ ] `powermetrics` sample fields captured from a privileged run.
  - [ ] Thermal fields available in captured samples.
  - [ ] Output parser target selected: text or `plist`.

Evidence commands run on 2026-06-09:

```bash
which powermetrics
powermetrics --help
powermetrics -n 1 -i 100 --samplers thermal,cpu_power,gpu_power,ane_power
python3 -c "import importlib.util; print(importlib.util.find_spec('mlx') is not None)"
uname -m
id -u
```

Current verdict:

- Telemetry binary: present.
- Telemetry permission: permission-blocked until a sudo workflow is approved.
- Runtime: pending install or environment selection for MLX/MLX-LM.

Next owner/action:

- User will handle local-machine auth on 2026-06-10. After that, capture one
  privileged `powermetrics` sample and record the available power/thermal fields
  here.

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
