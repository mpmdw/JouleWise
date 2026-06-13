# JouleWise Run State

Last updated: 2026-06-12

## Start Here For Every Big Run

Before starting substantial work:

1. Read this file.
2. Read `TASK_QUEUE.md`.
3. Read `AGENT_PLAN.md` (phase index) and the active phase's plan doc under
   `docs/phase_N/`.
4. Read `docs/planning_reflection_protocol.md`.
5. Check `docs/decision_log.md` before re-deciding anything; check
   `docs/risk_register.md` if starting a phase or a hardware-dependent task.
6. Check the last 2-3 commits with `git log --oneline --decorate -3`.
7. Check `git status --short --branch`.
8. Run `python3 -m unittest discover -s tests` unless the task is docs-only.
9. Do not commit local deletions or unrelated changes unless the user asks.

At the end of substantial work:

1. Update this file with what changed.
2. Update `TASK_QUEUE.md` with completed, added, or re-ranked tasks.
3. Add or update a detailed report in `docs/run_reports/`.
4. Record tests, commands, blockers, and the next best task.
5. Record new decision-log entries and any risk-register status changes.
6. Refresh `PROJECT_STATUS.md` if advisor-visible state changed.
7. Call out any dirty working-tree state that should not be accidentally
   committed.

## Current Project Status

Phase 1 is in its final stretch (most design/feasibility items closed; the
remaining gates need external/hardware input). **Phase 2's
hardware-independent core is complete and runnable**: one command produces a
complete, schema-valid, correctly-reduced run bundle from deterministic mock
adapters. The remaining Phase 2 slices are hardware-gated.

Every phase follows one documentation scheme:
`docs/phase_N/phase_N_plan.md` + `docs/phase_N/phase_N_exit_checklist.md`.
Cross-phase contracts live in `docs/contracts/`; registries in `docs/`
(decision log, risk register, milestones). Code-level specs for the gated
Phase 2 slices live in `docs/phase_2/hardware_slice_implementation_guide.md`.

## What This Run Did (2026-06-12, Phase 2 mock vertical slice + Phase 1 closures)

Implemented and tested the Phase 2 mock vertical slice (slices 2A-2F + 2J),
closed two Phase 1 gates, and recorded the supporting decisions. Full detail:
`docs/run_reports/2026-06-12-phase-2-mock-vertical-slice.md`.

New `joulewise/` modules:

- `clock.py` (D-019): `Clock` protocol, `SystemClock`, `FakeClock` — the only
  place the package reads wall-clock time.
- `bundle.py` (2A): `RunBundleWriter` — bundle layout, run-ID scheme (D-010,
  refined by D-022), write-order/immutability invariants (D-011), config
  hashing (D-001), experiment-manifest helper (D-005).
- `adapters/` (2B): registry + deterministic mock runtime/telemetry + local
  transport; unimplemented backends return structured failures (D-009/D-012).
- `controller.py` (2C/2D/2F): `run_benchmark` + `run_experiment`; full
  lifecycle, D-012 status mapping, D-011 completeness invariant, D-013
  quiescent measured window, events flushed before reduce (D-021).
- `reduce.py` (2D): `reduce_bundle` — pure post-hoc reduction over on-disk
  artifacts (D-002); trapezoidal energy, D-018 rail summation, idle
  subtraction, per-phase attribution; closed-form-tested.
- `report.py` (2J): static HTML run browser (D-006); matplotlib behind the
  `[analysis]` extra with graceful structured failure when absent.
- `cli.py`: new verbs `run`, `validate-bundle`, `report`; `run` dispatches to
  the experiment runner when `repetitions > 1`.
- `schemas.py`: two additive output fields only (R-015): `phase_energy_j`,
  `cooldown_cap_hit`.
- `pyproject.toml`: `[analysis]`/`[mac]` extras; phase bumped to 2.
- `.github/workflows/ci.yml`: mock end-to-end `run` + `validate-bundle` step.

Built by a multi-agent workflow (2A∥2B→2C→2D→2E→2F→2J), each slice gated on a
green suite, then an adversarial contract-review pass: zero critical/major
findings, eight confirmed minor findings (four code, four test-gaps) all
fixed, two findings correctly refuted. Decisions D-020 (CLI clock selection),
D-021 (events flushed before reduce), D-022 (config-hash run-ID suffix) added.

Phase 1 closures:

- P1-005 Hailo feasibility: verdict `unsupported_workload` (official-source
  desk research; Hailo-8L has no autoregressive-LLM path, GenAI is
  Hailo-10H-only). Recorded in the Phase 1 exit checklist Hailo section.
- P1-007 Phase 2 readiness review: recorded; verdict "mock-first Phase 2 may
  begin".

Also added `docs/phase_2/hardware_slice_implementation_guide.md` (code-level
specs for the gated slices 2G-2M).

## Current Verification

```bash
python3 -m unittest discover -s tests
```

Result (2026-06-12):

```text
Ran 169 tests
OK (skipped=8)
```

The 8 skips are the matplotlib `[analysis]`-extra chart tests in
`test_report.py`; they skip cleanly where the extra is absent (CI, bare
checkout) and run where it is installed. End-to-end verified:
`python3 -m joulewise run configs/examples/mock_local.json` → complete
bundle → `validate-bundle` green; reducer values match the closed-form mock
constants exactly; identical config + clock ⇒ byte-identical events.

## Known Workspace State

- Remote: `git@github.com:mpmdw/JouleWise.git`; branch `main`.
- **2026-06-12 environment incident:** while finishing the docs/commit, the
  repo-root directory became OS-locked (read/readdir EPERM; git "Unable to
  read current working directory"), spreading across subtrees over time, with
  the iCloud Drive file provider (`bird`) active. The repo lives under
  `~/Desktop/`, which is iCloud "Desktop & Documents"-synced. The code and
  `docs/` changes all landed and the suite was green (169) before the lock;
  iCloud eviction makes files cloud-only, not lost. The lock cleared on its
  own and this run's work was committed normally; the suite was re-run green
  (169) afterward to confirm no eviction corruption. **Durable fix to avoid a
  recurrence: move this git repo off the iCloud-synced Desktop** (e.g.
  `mv ~/Desktop/CapstoneRivoire ~/code/`); a work tree under iCloud "Optimize
  Mac Storage" will intermittently EPERM-lock the root.

## What Is Next

Follow `TASK_QUEUE.md`. The top items are all gated:

1. P2-004: close D-016 model selection (decision step; needs P1-001
   supervisor scope or explicit user go-ahead + disk-space check) — unblocks
   2G/2K install targets.
2. P2-003: Mac MLX + powermetrics vertical slice (2G/2H/2I) — gated on P1-002
   (privileged powermetrics sample + D-004 sudoers) and D-016. Spec:
   `docs/phase_2/hardware_slice_implementation_guide.md`.
3. P2-005: remote targets (2K NVIDIA/vLLM/ssh, 2L Orin) — gated on P1-006.
4. P2-006: homogeneous baselines (2M) — after 2I + ≥1 remote target.

Remaining Phase 1 external gates: supervisor scope (P1-001), calendar
(P1-008), wall meter (P1-003), network topology (P1-004), NVIDIA/Orin access
(P1-006).

## Open Decisions And Blockers

- Supervisor approval and scope pending (P1-001, R-001); also gates D-016.
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Mac privileged powermetrics sample pending (P1-002, R-002; gates 2H).
- D-016 model selection open (criteria fixed; needs P1-001 + install
  evidence).
- Git author identity was auto-selected as
  `Edr <edr@Edrs-MacBook-Air.local>` for the first commit. Amend future
  commits if a different identity is needed.
