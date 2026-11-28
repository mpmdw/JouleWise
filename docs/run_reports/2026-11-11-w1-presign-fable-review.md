# Fable cold review: the W1 pre-signing branch (RL-58 restore, RL-61 move, RL-62 catalog binding, CI debt)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 06:15 PST. Branch `ops/2026-11-11-w1-presign`, base
the W1 line `b4a6c217f`. It integrates three branches and adds one commit set of my own.

**Verdict: ADMIT**, for the two Sol-built pieces (below). The integration commits are mine and want a second
reader before the line takes them; the orchestrator chooses who.

## What is on the branch

| Piece | Ruling | Built by | From |
|---|---|---|---|
| CI debt: orphan-census test, decision log from `main`, packet mutation count 488, driver measurement-core pin | orchestrator | lane lead | `ops/2026-11-11-w1-ci-debt` |
| Estimator file restored to the accepted bytes; parse memo moved into the harvest | RL-58 | Sol | `ops/2026-11-11-w1-est-restore` |
| R1 phase table moved to a wait-free module, bound strict | RL-61 | Sol | `ops/2026-11-11-w1-phase-table` |
| Block 6 flag catalog bound strict, with its test; receipt template lists the two new bindings; five deviation rows | RL-62, RL-63, RL-65, RL-67, RL-68 | lane lead | `c64049b66` |
| Dynamic closure trace regenerated | RL-53, RL-61 | lane lead | `f41ee4e7c` |

## Review of the estimator restore (RL-58): ADMIT

- `joulewise/adapters/powermetrics.py` is byte-identical to `main`: no diff, SHA-256 `70f47086…`.
- The memo is `document_memo()` in `joulewise/b5/harvest.py`. Against RL-58's conditions:
  scoped to one member's assessment and removed on exit, including on error (`try`/`finally` restores the
  original function object); keyed by the SHA-256 of the exact input bytes; a hit returns a fresh copy
  (`pickle.loads` of the stored bytes); a failed parse is never kept (the exception leaves before the store);
  with the scope closed the estimator module holds its original function. Outside a scope nothing differs, and
  another thread without the scope gets the original parser.
- New test: every file in `ESTIMATOR_CODE_PATHS` equals the acceptance's pin.
- On the Air, on the Sol branch: `repin.py --check` passes all 16 families; `g2_phase_d` passes;
  `tests.test_calibration_live_three_window` 23 tests OK; `tests.test_repin` 37 OK; the three harvest-off
  modules 49, 17 and 22 OK; the closure and registration modules 36 OK.
- `tests/align/test_measurement_core_boundary.py`: the `b5/harvest.py` pin moves, with the ruling cited.

## Review of the phase-table move (RL-61): ADMIT

- Checked mechanically against the W1 line: `phase_plan`'s source text is identical; the six constants it needs
  have identical values; the new module `joulewise/align/apple/r1_phase_table.py` imports nothing.
- The driver imports and re-exports the names; `scripts/run_night.py` changes one import line.
- W1's static closure, as the PREQUAL check computes it, lists the new module and no longer the rehearsal
  driver. The PREQUAL check is unchanged.
- `tests.align.test_r1_rehearsal` (76, with the pinned tables for both `include_4bit` values),
  `tests.align.test_w1_prequal.SizingTests` (2), `tests.test_w1_reliability` (11) and round 5 (7): OK.
- `thermal_gates.py`, `r1_runtime.py` and `r1_runtime.json` are untouched.

## Confirmations on the integrated head, on the Air

| Check | Result |
|---|---|
| `tests.align.test_v4_executed_closure`, `test_v4_dynamic_closure`, `test_v4_registration` | 38 tests, OK |
| `tests.test_calibration_live_three_window` | 23 tests, OK |
| `tests.test_repin` | 37 tests, OK |
| `python3.13 -B scripts/repin.py --check` | PASS, 16 pin families current |
| `python3.13 -B scripts/repin.py --check g2_phase_d` | PASS |
| `tests.align.test_measurement_core_boundary` | 6 tests, OK |
| `tests.test_docs_freshness` | 31 tests, OK |
| `tests.test_fixture_orphan_census` | 16 tests, OK |
| `tests.align.test_w1_prequal.SizingTests` | 2 tests, OK |
| `tests.align.test_r1_rehearsal` | 76 tests, OK |
| `tests.align.test_smoke_delta3_sol1` | 16 tests, OK |
| `tests.test_adapters_powermetrics` | 3 tests, OK |
| `tests.align.test_harvest_off_review_sol2` | 22 tests, OK |
| `python3.13 -B scripts/gen_state.py --check` | exit 0 |

The trace differs from the committed one only by the new module in `executed`, `child_process_paths` and
`by_event`; `not_bound` and `not_strict` are empty.

## Not done on this branch

- The remaining `tests.align.test_w1_prequal` failures: two are one harness fault, fixed on the arm-check
  branch; two meter cases wait for a quiet machine.
- The held-windows deviation row and the row for the acceptance-only codes (RL-65, RL-71): they go in with the
  RL-53 batch, which carries the checks they describe.
- The STRICT receipt is not signed here; the template still reads `PENDING_LEAD_REGISTRATION`.
