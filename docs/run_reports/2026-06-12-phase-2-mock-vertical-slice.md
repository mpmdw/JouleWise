# Run Report: Phase 2 Mock Vertical Slice (Slices 2A-2F + 2J)

Date: 2026-06-12
Author: agent run (multi-agent workflow + central reconciliation)
Branch: `main` (uncommitted at time of writing; see "Workspace state")

## Planning reflection performed at the start

Read `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENT_PLAN.md`, the Phase 2 plan and
exit checklist, the contracts (`measurement_methodology.md`,
`run_bundle_layout.md`, `adapter_contracts.md`), the decision log, and the
schemas/interfaces. Confirmed the mock vertical slice (2A-2F, 2J) is
hardware-independent and was the top implementable queue work (P2-001,
P2-002). The hardware slices (2G-2M) remain gated on Phase 1 evidence
(P1-002 privileged sample, P1-006 remote access) and D-016 (model
selection), so they were specified as a handoff guide, not implemented.

## What changed

### Phase 2 mock vertical slice — implemented, tested, runnable

The harness now runs end-to-end from the CLI and produces complete,
schema-valid, correctly-reduced run bundles. New modules under `joulewise/`:

- `clock.py` (Slice 2B seam, D-019): `Clock` protocol, `SystemClock`,
  `FakeClock`. The only place the package reads wall-clock time.
- `bundle.py` (2A): `RunBundleWriter` with the documented layout, run-ID
  scheme (D-010), write-order + immutability invariants (D-011), config
  hashing (D-001), experiment-manifest helper (D-005).
- `adapters/` (2B): registry (`resolve_runtime`/`resolve_telemetry`/
  `resolve_transport`) plus deterministic `mock_runtime`, `mock_telemetry`,
  and `local_transport`. Unimplemented backends return structured failures
  (D-009/D-012); never raise.
- `controller.py` (2C, 2D wiring, 2F experiment loop): `run_benchmark` (one
  measured run) and `run_experiment` (repetitions + manifest + cooldown
  gate). Full lifecycle, D-012 status mapping, D-011 completeness invariant,
  D-013 quiescent measured window, deferred logging.
- `reduce.py` (2D): `reduce_bundle` — pure post-hoc reduction over on-disk
  artifacts (D-002). Trapezoidal energy with boundary interpolation, D-018
  rail summation, idle subtraction, per-phase attribution, measurement
  quality. Closed-form-tested.
- `report.py` (2J): `generate_report` — static HTML run browser (D-006),
  matplotlib behind the `[analysis]` extra with graceful structured failure
  when absent.
- `cli.py` (2E, 2F, 2J): new verbs `run`, `validate-bundle`, `report`;
  `run` dispatches to the experiment runner when `repetitions > 1`.
- `schemas.py`: two additive output fields only (R-015): `phase_energy_j`,
  `cooldown_cap_hit`. Config schema unchanged.
- `pyproject.toml`: `[analysis]` and `[mac]` extras; phase bumped to 2.
- `.github/workflows/ci.yml`: added the mock end-to-end `run` +
  `validate-bundle` step (D-017).

### Phase 1 gate closures (independent of the slice work)

- **P1-007 Phase 2 readiness review**: recorded in the Phase 1 exit
  checklist; verdict "mock-first Phase 2 may begin".
- **P1-005 Hailo feasibility**: verdict `unsupported_workload` from
  official-source desk research (no autoregressive-LLM path on the
  Hailo-8L; the GenAI path is Hailo-10H-only). Recorded in the Phase 1 exit
  checklist Hailo section with sources; optional local reproduction noted.

### Decisions recorded

- **D-020**: CLI binds `FakeClock` for all-mock runs, `SystemClock`
  otherwise.
- **D-021**: controller flushes `events.jsonl` before the reduce stage so
  the reducer stays pure over on-disk artifacts (a real sequencing hazard
  flagged by the 2C author and fixed in 2D).
- **D-022**: auto-generated run-ID suffix is the first 4 hex of the config
  hash, not `secrets.token_hex(2)` — restores the Slice 2B determinism
  criterion (refines D-010).

### Handoff doc for the gated work

- `docs/phase_2/hardware_slice_implementation_guide.md`: code-level pinned
  APIs, test lists, lazy-import patterns, and smoke procedures for the
  gated slices 2G (MLX), 2H (powermetrics), 2I (Mac integration), 2K
  (vLLM/nvidia-smi/ssh), 2L (Orin), 2M (baselines), plus the D-016 closure
  checklist. Written so the next agent (with hardware) can implement
  against locked contracts without re-deriving the design.

## How it was built

A multi-agent workflow implemented the seven slices in dependency order
(2A ∥ 2B → 2C → 2D → 2E → 2F → 2J), each agent gated on a green full suite,
followed by six parallel adversarial contract reviewers (bundle layout,
reducer math, lifecycle/failure semantics, clock/determinism, CLI/CI,
schema/test-adequacy) with per-finding skeptic verification.

Note: the first workflow run aborted at Slice 2D when the session model
became temporarily unavailable mid-run; 2A/2B/2C had completed cleanly and
left no partial files. The run was resumed from cached 2A/2B/2C results,
with the 2D prompt amended to pin the events-flush fix (D-021).

## Review findings (adversarial pass)

Zero critical or major findings. Eight confirmed **minor** findings (four
small code issues, four test-coverage gaps); two findings were correctly
refuted (per-member config-hash divergence is intended per D-005; TTFT
file-order reliance is safe because `events.jsonl` is contractually
timestamp-sorted). All eight confirmed findings were fixed:

1. metadata.json now carries `model` + `quantization` (contract
   enumerates "model"); controller `_write_metadata`.
2. zero-length measured window no longer zeroes real per-phase energy; the
   real summed curve is threaded into `_zero_window_summary`.
3. D-011 completeness hardened: `bundle.write_metadata` serializes with
   `default=str` and the controller normalizes adapter metadata through
   `_jsonable`, so a third-party adapter returning non-serializable
   metadata can no longer leave an unfinalized bundle.
4. deterministic run-ID suffix (D-022); a run-benchmark-level determinism
   regression test pins byte-identical events for identical config+clock.
5-8. added the missing failing-path tests: validate-bundle JSON-parse /
   re-validation, validate-bundle events.jsonl record checks, run-verb
   exit-2 on schema-invalid config, and the cooldown rolling-window
   high-to-low recovery transition.

## Commands run / results

```bash
python3 -m unittest discover -s tests      # Ran 169 tests, OK (skipped=8)
python3 -m joulewise run configs/examples/mock_local.json --runs-dir <tmp>
python3 -m joulewise validate-bundle <tmp>/example-mock-local   # valid
```

The 8 skips are the matplotlib `[analysis]`-extra chart tests in
`test_report.py`; they skip cleanly where the extra is absent (CI and a
bare checkout) and run where it is installed.

Closed-form e2e check on `mock_local.json` (prompt 32, output 8, 2 Hz,
idle 1 s): measured window 0.112 s, gross 0.84 J, idle-subtracted 0.28 J,
phase split prefill 0.24 J / decode 0.60 J, ttft 0.042 s, throughput
114.3 tok/s — all matching the mock constants exactly.

Determinism (no `run_id`): two runs of the same config produce byte-
identical run IDs and byte-identical `events.jsonl`.

CI e2e step (the exact workflow shell block) simulated locally: exit 0.

## Workspace state — needs care

- All slice modules and tests are **untracked** (`joulewise/*.py`,
  `tests/test_*.py`); the doc and config changes are modifications. Nothing
  is committed yet at the time this report was written; the run's commit
  follows.
- `.gitignore` now excludes `ci-runs/`, `report/`, and
  `.claude/settings.local.json` in addition to `runs/`.
- One plan reconciliation: Slice 2A's design notes wrote
  `create(runs_root, config)`; the implemented (and correct) API is
  `create(runs_root, config, clock)` per the D-003/D-019 clock rule. The
  Phase 2 plan's Slice 2A note is updated to match.

## What the next agent should do first

1. Push and confirm CI is green on `main` (3.11 + 3.14 matrix + mock e2e).
2. Phase 2's remaining work is all gated:
   - **D-016 model selection** (decision step; needs P1-001 supervisor
     scope or explicit user go-ahead + a disk-space check) — unblocks
     2G/2K install targets.
   - **2G/2H/2I** (Mac MLX + powermetrics + integration) — gated on
     P1-002 (privileged powermetrics sample + sudoers) and D-016.
   - **2K/2L** (remote NVIDIA/Orin) — gated on P1-006 access evidence.
   - **2M** baselines — after 2I + at least one remote target.
   Use `docs/phase_2/hardware_slice_implementation_guide.md` as the
   code-level spec for all of these.
3. Remaining Phase 1 external gates (supervisor scope, calendar, wall
   meter, network topology, NVIDIA/Orin access) still need user/hardware
   input — see the Phase 1 exit checklist.
