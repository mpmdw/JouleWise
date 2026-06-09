# Agent Implementation Plan

This repository implements JouleWise, an extensible energy-characterization
benchmark for LLM inference across heterogeneous local hardware. The name is a
nod to JouleSort and Splitwise: energy measurement as the spine, split inference
as the first research application that validates the harness.

## Ground Rules For Agents

- At the start of every substantial run, read `RUN_STATE.md` first.
- At the end of every substantial run, update `RUN_STATE.md` and add or update a
  detailed report in `docs/run_reports/`.
- Do not modify `Energy_Benchmark_Architecture.docx` unless the user asks.
- Keep run artifacts self-contained and reproducible.
- Prefer small vertical slices that produce complete run bundles.
- Treat unsupported hardware/model combinations as structured outcomes, not
  crashes.
- Keep runtime adapters separate from telemetry adapters.
- Make every result traceable to a config, raw power trace, event log, and
  reducer output.

## Canonical Architecture

```text
typed config
  -> controller
    -> transport adapter: local or ssh
    -> runtime adapter: mlx, vllm, llama.cpp, hailo-if-viable
    -> telemetry adapter: powermetrics, nvidia-smi, jetson rails, wall meter
  -> run bundle
    -> reducers
    -> dashboard / notebooks / report figures
```

## Phase Checklist

### Phase 1: Approval, Feasibility, And Measurement Design

Status: in progress.

- [x] Create repo-local agent plan.
- [x] Define draft typed benchmark config contract.
- [x] Define draft standardized run output contract.
- [x] Define runtime/telemetry/transport adapter interfaces.
- [x] Define run-bundle layout.
- [x] Add example configs for Mac-local and mock-local runs.
- [x] Add schema/interface tests.
- [x] Add Phase 1 CLI helpers for config validation and schema printing.
- [ ] Confirm supervisor expectations and final proposal scope.
- [ ] Complete Hailo feasibility investigation.
- [ ] Confirm wall-meter availability.
- [ ] Confirm local network plan for interconnect sweep.
- [ ] Confirm telemetry permissions on each physical target.

Acceptance criteria:

- Example configs validate.
- Mock adapter tests pass.
- Measurement methodology is documented.
- Every hardware target is classified as supported, pending, or intentionally
  unsupported.
- Phase 2 can start with a clear Mac MLX + powermetrics vertical slice.

### Phase 2: Harness, Mac Vertical Slice, And Homogeneous Baselines

Status: planned.

- [ ] Implement controller lifecycle:
  `prepare -> idle -> warmup -> measured_run -> cleanup -> reduce`.
- [ ] Implement run-bundle writer.
- [ ] Implement Mac MLX runtime adapter.
- [ ] Implement powermetrics telemetry adapter.
- [ ] Implement summary reducer.
- [ ] Implement dashboard v1 as a read-only run browser.
- [ ] Add NVIDIA/vLLM + nvidia-smi adapter.
- [ ] Add Orin adapter.
- [ ] Run homogeneous baselines.
- [ ] Reproduce prefill/decode qualitative power behavior.

Acceptance criteria:

- One command creates a complete Mac run bundle.
- Dashboard displays the run trace and summary metrics.
- Repeated runs report variance.
- Unsupported combos fail with structured failure reasons.

### Phase 3: Disaggregation, Offline KV Replay, And Interconnect Sweep

Status: planned.

- [ ] Implement split-run orchestration.
- [ ] Build offline decode replay path before live KV transfer.
- [ ] Measure serialization, payload size, transfer time, and transfer energy.
- [ ] Run GPU-to-Apple experiments.
- [ ] Run GPU-to-GPU experiments during 3080 Ti borrow window.
- [ ] Run Orin-to-Orin and Orin-to-Apple experiments.
- [ ] Run 1GbE, 2.5GbE, and optional 10GbE sweep.

Acceptance criteria:

- Split runs decompose prefill, transfer, and decode energy.
- Offline replay produces valid decode-energy measurements.
- Interconnect data supports a crossover curve.

### Phase 4: Core Characterization And Analysis

Status: planned.

- [ ] Aggregate homogeneous and split runs.
- [ ] Compute uncertainty intervals from repeated runs.
- [ ] Generate energy/token and energy/request figures.
- [ ] Generate interconnect crossover figures.
- [ ] Generate energy-latency Pareto frontier.
- [ ] Draft results and limitations.

Acceptance criteria:

- Claims trace back to raw run bundles.
- Figures regenerate from repository scripts.
- Results identify where splitting wins, loses, and why.

### Phase 5: Presentation, Repository Polish, And Final Submission

Status: planned.

- [ ] Write runnable README quickstart.
- [ ] Write backend-extension guide.
- [ ] Publish sample run bundle.
- [ ] Validate final dataset bundles against schemas.
- [ ] Prepare colloquium slides.
- [ ] Prepare final report.

Acceptance criteria:

- A new user can run one local benchmark from the README.
- A new developer can add a backend from the adapter guide.
- Final figures regenerate from published data.

## Current Verification Command

```bash
python3 -m unittest discover -s tests
```

Useful Phase 1 commands:

```bash
python3 -m joulewise validate-config configs/examples/mock_local.json
python3 -m joulewise print-config-schema
python3 -m joulewise print-output-schema
```

## Run Report Protocol

Every big run must leave a human-readable handoff note. The report should cover:

- What changed.
- What commands were run.
- What passed or failed.
- What local workspace state needs care.
- What the next agent should do first.

The root `RUN_STATE.md` is the current handoff. Dated reports live in
`docs/run_reports/`.
