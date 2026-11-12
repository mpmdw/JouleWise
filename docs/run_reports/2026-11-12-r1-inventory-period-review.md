# R1 inventory sampler period (RUN_STATE 280): cold executing review

- **Reviewer:** Fable 5.2, cold and executing (RL-74(a) gate). Did not write the change.
- **Target:** `fix/2026-11-12-r1-inventory-period` @ `22138c5b5220144bed3f31267c34f980a17d953a`, parent `8f5a1a0f9`.
- **Date:** 2026-11-12, about 02:10 to 02:35 PST. Run on the Air; no host-changing command, no MBP access.
- **Blind status:** blind. Fake-clock tests and source reading only; no v4, Block 6 or BYTES outcome and no energy or power value was read.

## Verdict: ADMIT

The schedule rule is correct, it is the same rule as the thermal sidecar's loop, and it changes nothing on a
night except the inventory journal's cadence. Nothing blocks the fifth smoke or a real night. Two test gaps
and one pre-existing ticker behaviour are noted below; none needs to be closed before the smoke.

## Checks

| # | Check | Result |
|---|---|---|
| 1a | Period with sweeps under one tick | Pass. Sample k starts at grid + wake latency of tick k. Gap = 1 s + (latency k+1 - latency k); nothing accumulates. Real loop, 45,000 ticks, 0.128 s sweep, start at 30 days of uptime: total drift 0 ns, largest gap error 0 ns. With latency random in 0-50 ms over 5,000 ticks, every start stayed within the latency band of the grid. |
| 1b | Sweeps of one tick or more | Pass. Constant sweeps 1.0-1.5 s give 2 s gaps, 2.0-2.5 s give 3 s, 3.8 s gives 4 s. Single stalls of 1.0, 1.2, 1.5, 1.99, 2.5, 10 and 3,600 s: one long gap, then exactly 1 s gaps on the original grid; smallest gap 1.0 s, so no burst. |
| 1c | Floating point over a night | Pass. `due += 1.0` and `due += n` (n a whole float) are exact except when `due` crosses a power of two, where the error is at most half an ulp. 50,000 ticks from bases of 1,000 s, 30 days and 400 days: error exactly 0. Across 2^23 s: 9.3e-10 s, once, not growing. The skip form is no worse than repeated `+= 1.0`. |
| 1d | Edge cases | `now - due == 1.0` exactly: the tick at `now` is skipped (gap 2 s), as in `thermal.py` (`due <= now`). Zero sweep: 1 s gaps. Negative `now - due` (an early wake): the guard is false, nothing is added. The boundary between the two regimes is sweep + wake latency = 1 s, not sweep = 1 s (0.994 s sweep with 6 ms latency already alternates ticks); that is the intended rule. |
| 1e | Timestamps | Pass. `InventoryJournal.sample` stamps `started` and `finished` from the clock around the read. `due` is never written. A skipped tick writes no row. |
| 1f | Same rule as the sidecar | Pass, by algebra: both give next due = old due + floor(now - old due) + 1 whenever a tick was overrun. `thermal.py:170-173` and `smc_enumeration.py:427-429` read as the author says. |
| 2 | Night-path impact | Pass. Only the cadence of `inventory/inventory_journal.jsonl` changes, on the segments that call `start_inventory` (step-30b, step-d). See "Consumers". |
| 3 | Same-bug survey | `ProductionBackend.ticker` bursts after a stall. Low severity; see finding F3. |
| 4 | Fail-first | Pass. At `8f5a1a0f9` the new module fails 3 assertions: median period 1.126 s and 1.206 s, stall coverage 0.884. At head, 2 tests pass. The test calls the real `rt._inventory_process` with `time.monotonic` patched. |
| 5 | Mutants | The five requested: four killed, one survives (`>` for `>=`, equivalent in practice). One extra non-equivalent mutant survives; see F1. |
| 6 | Tests | All 13 modules pass. `test_r1_runtime`: 7 failures and 2 errors, the same nine test names at head and at `8f5a1a0f9`. |
| 7 | Binding | Bug fix. No pin or plan_tree regeneration needed. |

## Consumers of the inventory journal

All were read; all work in time, on the 1 s cell grid, and were written for a 1 Hz journal.

- `classify_step` -> `smc_enumeration.rank`: phases are assigned by stamp; coverage is `thermal.Coverage` with a
  half-period tolerance on a grid anchored at the phase's first sample, so the sampler's phase relative to a
  phase boundary cannot empty cells. Fits use actual stamps. The row-count conditions are minimums (at least 5
  valid samples per phase, at least 5 load samples at 50-60 s) and ratios (mode and clamp fractions); a 1.00 s
  period gives more rows than 1.12 s, never fewer.
- `kit.phase_coverage` (smoke Part B): same `Coverage`, 99% of cells and fewer than 2 consecutive empty cells.
  This is the check that failed; it needs 1 Hz.
- `s7_for_picks` / `quiet_baseline`: time windows, minimum of 5 samples in the last 60 s.
- `replay.candidate_replays`: actual stamps through the W1 replay session, which requires 1 Hz coverage (it
  returned `unobserved` at 1.12 s).
- `journal_rows` in the classification record is a count and will be about 12% higher. It is a recorded output,
  not compared against anything.

The G0 and per-turn gates, the reference capture, quiet admission and member selection read the thermal
sidecar journal (`align_thermal.jsonl`), not the inventory journal, and are untouched. Nothing depends on the
old ~1.12 s spacing.

One physical consequence, stated for the record: the inventory process now reads the SMC inventory at 1.00 Hz
where it read at about 0.89 Hz, so its read duty rises from about 11% to about 13% of one process during
step-30b and step-d. That is the ruled design (protocol v4 :243-251, R5-5), not a new load.

## Mutants (against `tests.align.test_r1_inventory_period`)

| Mutant | Result |
|---|---|
| M1 restore `due = max(due, time.monotonic() - 0.01)` | killed (3 failures) |
| M2a `due = now` when a tick was overrun | killed |
| M2b unconditional `due = now` | killed (3 failures) |
| M3 drop the skip (burst) | killed |
| M4 `>` for `>=` | **survives**; differs only when `now - due` is exactly 1.0 |
| M5 skip one tick too many | killed |
| M6 skip one too few | killed |
| M7 threshold 0.5 | survives; truly equivalent (floor is 0 below 1.0) |
| M8 threshold 2.0 | **survives; not equivalent** (F1) |
| M9 `due = max(due, now - 1.0)` | killed |
| M10 ceiling for floor | killed |

## Tests (one module at a time, `nice -n 10 python3.13 -B -m unittest`, 33 GB free throughout)

| Module | Result |
|---|---|
| tests.align.test_r1_inventory_period | 2 OK |
| tests.align.test_r1_inventory | 14 OK |
| tests.align.test_smc_classifier_v4 | 27 OK |
| tests.align.test_smc_quiet | 34 OK |
| tests.align.test_smc_selection | 10 OK |
| tests.align.test_r0_host | 59 OK (1 skipped) |
| tests.align.test_r1_smoke_launcher | 45 OK |
| tests.align.test_r1_followup | 12 OK |
| tests.align.test_r1_round7_science | 18 OK |
| tests.align.test_v4_registration | 24 OK |
| tests.align.test_v4_executed_closure | 6 OK |
| tests.align.test_v4_dynamic_closure | 10 OK |
| tests.hazards.test_refusal_allowlist | 24 OK (1 skipped) |
| tests.align.test_r1_runtime | 33 run, 7 failures + 2 errors; identical nine names at `8f5a1a0f9` |

## Findings

- **F1 (low, test gap, not blocking).** The stall test uses only a 2.5 s stall. A stall between 1 and 2 s is
  not covered: with the guard changed to `>= 2.0` the loop samples again immediately after such a stall and
  then catches up off-grid, and the module still passes. The head code handles 1.0-1.99 s stalls correctly
  (checked above). RL-74's recorded stalls were 1.6-3.8 s, so a 1.5 s case belongs in the test. Add it in the
  next change to this file; it does not need a new presign.
- **F2 (informational).** The exact-tie mutant (`>`) survives. It can only differ when `now - due` is exactly
  1.0, and either behaviour is acceptable there. No action.
- **F3 (low, pre-existing, no fix required).** `ProductionBackend.ticker` (`r1_runtime.py:1436-1445`) does
  `due += 1.0` with no skip, so after its thread is starved for N seconds it runs N callbacks back to back.
  On a night it drives (a) the load and battery journal: a burst writes several `ps` samples a few tens of
  milliseconds apart, each truthfully time-stamped (`cpu_busy_t_s`), and the battery poll counts ticks so it
  stays on its 30 s schedule; any statistic that weights load samples equally over-weights the moment after a
  stall, and the burst itself forks a few extra `ps`; (b) the planning-preheat heater control, where repeated
  `set_duty` calls are harmless. This loop ran on night `r1-20261111T043229Z` unchanged. It is the loop RL-76
  found starved by the main thread, so bursts do happen. Worth the same three-line rule in a later change; not
  a reason to hold the smoke.
- **F4 (informational).** The author's history claim holds. `_inventory_process` and the `- 0.01` line first
  appear in `a85ee8ec6` (2026-11-11 07:06 PST); night `r1-20261111T043229Z` started 2026-11-10 20:32 PST and
  used the in-thread ticker, whose period was 1 s. No recorded night ran the defective line.

## Binding

Bug fix that restores the ruled design: protocol v4 :243-251 and LEAD-RULINGS-2 R5-5 say every inventoried key
at 1 Hz; RL-74(a) and RL-76 set the 99% bar per phase; RL-84 keeps it per key. The 0.99 s + sweep period was
never ruled or registered. No registered or pinned artifact records the inventory period or a row count; the
registration, executed-closure, dynamic-closure and refusal-allowlist modules pass at head with no
regeneration. Magistrate caps and DEADLINE are untouched by the diff (three files: the runtime, its contract
doc, the new test). The smoke's `verify_r1_executed_sources` check binds to the executed commit, so the fifth
smoke must name a commit that contains `22138c5b5`.
