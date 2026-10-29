claude-opus-5-5
VERDICT: ACCEPT_WITH_FIXES

# KB-V2 round 5 delta review (Opus, executing): known-bytes reading rule, probe receipt, two CI causes

**Delta and checkout**
- Delta: `977a5d2df..6847502b8b6adec1d232bbfce10cb2a2c729498b` on mpmdw/JouleWise `codex/2026-10-28-kb-v2`, draft PR #593.
- Code checkout: `/tmp/jw`, detached at `6847502b8`, read-only.
- Scripts are in this directory and take the checkout as their first argument. Logs are in `logs/`.

**Summary**
- Every round-4 repro passes, from both reports. G2, G4, G5 and R-G3 are implemented as ruled.
- G1's accessor covers every read- and scan-path leaf I could reach. My own walk ran 44,816 mutations over all eight records, the scan object and gap rows, and found **no lost record, no lost call, and no shrunk bound from a missing, null, wrong-typed, non-finite or wrong-length leaf**.
- Three residual defects remain (findings 1–3). Each sits outside the five fault modes the builder's 945-case test generates:
  1. integers beyond binary64 make the accessor itself raise;
  2. time order inside one native row or one receipt is not checked;
  3. an invalid disclosure-only leaf vetoes all four classes.
- None changes a number on well-formed input. The worked values are unchanged.
- I could not read PR #593's CI: this session's GitHub access is scoped to mpmdw/JouleWise-data only (see Executed). Locally, the four jobs red in round 4 now pass at `6847502b8`.

## Findings

### 1. MINOR (G1): the one accessor raises `OverflowError` on integers too large for binary64, in both `read` and `scan`; the record is lost

**Where**
- `scripts/bytes_stream_test.py:210`: `valid = type(value) in (int, float) and math.isfinite(value)`.
- `math.isfinite(10**400)` raises `OverflowError: int too large to convert to float`. `json.loads` accepts such an integer as valid JSON.
- `knee_scan` (`:316`) and `read_known_bytes` catch only `KeyError`, `TypeError` and `ValueError`.
- A finite input whose arithmetic overflows raises the same way, at `idle_statistics` `math.fsum` (`:416`).

**Effect:** a traceback with no output. This breaks G1's "never a traceback, never a lost record".

**Repro**
- `python3.13 -B probes.py /tmp/jw KBDIR` (`logs/probes.log`); KBDIR is the output of `r4repro/r3/e2e.py`.
```
[huge_int_start_ns_rec0] CLI rc=1 TRACEBACK: OverflowError: int too large to convert to float
[huge_int_idle_stamp] CLI rc=1 TRACEBACK: OverflowError: int too large to convert to float
[huge_int_scan_K] CLI rc=1 TRACEBACK: OverflowError: int too large to convert to float
[huge_int_scan_receipt] 1 OverflowError: int too large to convert to float
[huge_int_scan_repeats] 1 OverflowError: int too large to convert to float
[power_1e308_idle_rails] CLI rc=1 TRACEBACK: OverflowError: intermediate overflow in fsum
```
- Leaf walk (`logs/leafwalk.log`): `crashes 980`. All 980 are `huge_int OverflowError ... @ bytes_stream_test.py:210`, one for every numeric leaf the reader reads, in every record and in `scan.K`/`B`/`Bc*`.

**Fix:** in `input_value`, treat a value that cannot convert to a finite float as invalid, for example by catching `OverflowError` around the finiteness test. Route it through the existing reason path. No new bar is needed.

### 2. MINOR (G1, sign or order the physics fixes): time order inside a native row or a receipt is unchecked; it raises, drops a sample silently, or moves every contrast while all classes stay RESOLVED

The accessor checks each stamp's type and sign, not that intervals are ordered.

**(a) A rails or GPU idle row with `end_ns < start_ns`**
- If the reversed row overlaps the span, it reaches `estimate_newey_west_bartlett` with a negative duration and raises (`joulewise/idle_dependence.py:89`).
- If it falls outside, the `:400` filter drops it silently. Support changes with no reason given, and a per-call bound can shrink.
- Repro (`logs/probes.log`, real CLI, full-size data):
```
[idle_rails_row_end_before_start] CLI rc=1 TRACEBACK: ValueError: idle durations must match samples and be finite and > 0
[idle_rails_last_row_end_ns_0] rc=0 ... all RESOLVED; pre rails sample_count 575 baseline 576   (no reason printed)
```
- Leaf walk, thinned data, `records.0.harvest.idle.pre.rails.11.end_ns` = 0: `baseline_bound_j 1.0077466676906661 < 1.00886451744611` and `bound_j(rails) 1.546546667690666 < 1.5476645174461099`; classes all RESOLVED, no reason.
- The walk shows the same pattern (bound below baseline, no reason) for `start_ns` = 0 on a rails or GPU row (an overlapping interval) and `stamp_ns` = 0 on meter rows.

**(b) A receipt `start_ns` earlier than `idle_pre_end_ns`**
- Only `start_ns`/`end_ns` positivity and the cross-record start order are checked (`:672`).
- Repro: `[rec0_start_ns_at_idle_pre_start]`, all RESOLVED.
  - Deltas: rails 0.066707 vs 0.066716, DC 0.192505 vs 0.192943, rest 0.125798 vs 0.126227 J/GB.
  - No reason is printed.
- In the walk, `records.0.receipt.start_ns` = 0 moves DC from 0.19294 to 0.18526 J/GB, still RESOLVED.

**Fix**
- Treat a rails/GPU row with `end_ns <= start_ns` as an invalid collection, as the accessor already does for a wrongly typed row.
- Require `idle_pre_start_ns <= idle_pre_end_ns <= start_ns < end_ns <= idle_post_start_ns <= idle_post_end_ns` in each receipt.
- Route both through `missing(...)`.

### 3. MINOR (G1 routing versus §2/§4): an invalid disclosure-only leaf invalidates its whole container and makes all four classes UNDETERMINED

**Where**
- `:594-595`: `r["stack"] = take(..., STACK_INPUTS, ..., names, ...)` and `h["capture_stack"] = take(..., CAPTURE_INPUTS, ...)`.
- One bad leaf, for example `python`, `packages.numpy`, `kernel_library` or `telemetry_backend`, replaces the container with `{}` and charges all four classes.
- §2 and §4 say these fields are disclosure: "They do not independently veto a class"; "Other differences change no class". G1 routes a failure to "the affected class", and a disclosure field affects none.

**Repro** (in-process with the leaf-walk base; commands in Executed):
```
python differs rec2               -> all RESOLVED
del receipt.stack.python rec2     -> all UNDETERMINED (records[2].receipt.stack.python missing or invalid)
del receipt.stack.packages.numpy  -> all UNDETERMINED
del capture telemetry_backend     -> rails/rest UNDETERMINED "measured rails boundary missing" (the recorded rail set was valid), gpu/dc UNDETERMINED
```

**Severity reasoning:** the error is conservative; it never shrinks a bound. But a missing disclosure value vetoes a class that a wrong value would leave alone, and the rails/rest reason is false.

**Fix:** validate leaf by leaf. Charge physical fields (OS, hardware unit, MLX/MLX-Metal, rail set) to the classes §2 names. Disclose the rest without vetoing, and keep a valid rail set when a sibling disclosure leaf is bad.

### 4. NIT (for the lead; builder decision): negative measured powers and integrals are accepted

**What happens**
- `NATIVE_INPUTS` and `energy_j` use `NUMBER`, which accepts any sign.
- Negative idle rails/GPU/meter `power_w`, or a negative `energy_j.rails`, change every central value.
- The walk lists 504 "silent" negative/zero power cases; only the negative ones are relevant. In each, classes are unchanged, the half-width widens and no reason is printed.
- Example: `energy_rails_negative` makes rails NOT RESOLVED.

**Context**
- The round report records this choice ("retain signed measured powers/integrals").
- Battery power is legitimately signed. Rails, GPU and adapter-meter power are not.
- G1 asks for sign "where the rule's physics fixes it". I did not rate it higher because no bound shrank in any case.

### Environmental (not a defect of this delta)

- `tests.test_bytes_stream_test.ReceiptTests.test_cli_end_to_end_with_fake_mlx_and_real_identity_sources` errors on this seat with `TypeError: 'NoneType' object is not callable`.
  - Cause: the test patches `time.sleep`, and `subprocess.wait` inside the runtime-identity probe calls it.
  - It fails identically at `977a5d2df` (checked in a throwaway worktree), so it predates round 5.
  - In round 4 it passed on another seat.
  - The other 48 tests pass (`logs/ut_stream.tail`).

## Checks requested

| # | Check | Result |
|---|---|---|
| 1 | Round-4 repros at `6847502b8` | **All pass**, details below. |
| 2 | G1 accessor | Read and scan paths take every receipt, harvest and CLI value through `input_value`, directly or via `take`. That includes nested lists (rails label, native rows, edges), per-call dicts in records 1–7, `scan.K`/`B`/`Bc*`, null containers, scan receipts with their clock fields, and both arms of the GPU-source rule (harvest rail set and reference rail set). Independent walk: no lost record, no lost call, and no shrunk bound under deleted, null, wrong-type, NaN, ±inf, empty, short or long mutations. Residuals: findings 1–3. |
| 3 | G2 | **Pass.** `g2_lost_calls.py`: 8 positions × 6 loss modes (popped, `{}`, receipt null, repeats null, harvest null, rails integral null) = 48 cases, **0 mismatches**. Only the lost call's arm loses `x`/`dx`, and only for the boundaries that need it (rails-integral loss touches rails/rest only). The other arms are bit-identical to the baseline. `raw_stream_j_per_byte` is kept unless S is lost. |
| 4 | G4, R-G3, CI | See the CI paragraph below this table. |
| 5 | G5 | Rule §2 (`docs/registrations/bytes_known_bytes_reading_rule_DRAFT.md:220-222`) and §4 (`:369-370`) carry the reason, and the program has it at `:662-666`. Repro `[rails_label_no_gpu_rec7]`: GPU UNDETERMINED (`gpu_power missing from recorded rail set ...`), DC RESOLVED. Opus 6: `cache_reference.above=True`, matching its pair. Opus 7: `5 ± 150` prints `0 ± 150` with upper limit `160`, both at the tens place. |
| 6 | Numbers | Bars: 4.5e-7 GB/s at `tests/test_bytes_stream_test.py:924-926` (1% of 0.000045 GB/s), and 5.7e-6 J/GB at `:488-514`. Both are used as given, with derivations beside them; no new tolerance. New round-5 assertions use exact equality only where bit-identity is the property (an arm unaffected by a lost call; a `cache_reference` copy equal to its `pairs` entry) and exact `>=` for "no bound below baseline". Worked values are unchanged (`logs/e2e_r3.log`): rails 0.06672 ± 0.00057, DC 0.1929 ± 0.0025, rest 0.1262 ± 0.0024, f 0.3458 ± 0.0075. Program minus independent ≤ 2.81e-6 J/GB, inside the 5.7e-6 bar. |

**Check 4 detail: G4, R-G3 and CI**
- `tests.test_bytes_h_session`: 36 tests, OK.
- `tests.test_repin`: 37 tests, OK.
- `repin.py --check`: `PASS 16 pin families current`. `bytes_mac_kit.py --check`: `verified non-claim Mac kit`.
- Registry diff against `977a5d2df`: one file entry, exactly four rows (`/stage_graph/{2,4,18,24}/input/sha256`). Only the target index changed, now pointing at `bytes-s1-p1-{bound-collection,reference-start,reference-midpoint,reference-end}/order_manifest.json` (targets 162, 172, 168, 166). The `targets` list is identical and no other key changed.
- `013a8e99d` is a real `git revert` of `2153f1333`.
- **CI not read** (scope). Local stand-ins all pass: the fences steps (`gen_state --check`, `repin --check`, `tests.test_docs_freshness` 31 OK, histsem `PASS`) and both modules that were red in round 4.

### Round-4 repros at `6847502b8`

| Finding | Result |
|---|---|
| Opus-r4 1a (registry) / Sol 3 | Pass: `repin --check` PASS; Sol `ci_diagnose.py` reports `current stale rows 0`. |
| Opus-r4 1b (session KeyError) / Sol 4 | Pass: `test_bytes_h_session` OK. `ci_diagnose`'s path lookup still prints MISSING; that is expected, because the fix keys by `manifest_id`. |
| Opus-r4 2 (short edge lists) / Sol 1 | Pass: empty or one-value `meter_edge_w` → DC UNDETERMINED with the leaf reason; `edge_bound_j` absent, not 0. |
| Opus-r4 3 (scalar edges, string anchor, non-object gap row, string adapter) | Pass: all exit 0 with the leaf reason. |
| Opus-r4 4 (negative adapter rating) | Pass: `adapter rating missing`; `bound_j` None. |
| Opus-r4 5 / Sol 2 (empty record suppresses arms) | Pass: arms S, C1, C3 kept, C2 marked not defined. |
| Opus-r4 6, 7, 8 | Pass (G5 row in the table above). |
| Sol 1 (null `idle.pre`, null receipt, `[None, 86]` edges) | Pass: `reader_edges.py`, all EXIT 0, eight calls kept. |
| Sol `read_cases.py` | Pass: baseline all RESOLVED with the worked contrasts; each prerequisite case shows a reason. |
| Round-3 chain via `run_with_clock` (`scan_cases`, `knee_noise_diag`, `tick_quant`, `dram_noise`, `refusals`, `e2e`) | Pass, with the same outcomes as round 4 (`logs/r3_*.log`). |
| `e2e4.py` | Pass: run through `r4repro/e2e4.py`. The only change to the copy is that a display field that is now correctly absent prints `<absent>`; the original stops with a `KeyError` in its own print line. Part 1 scan results are as in round 4. |

## Executed

- `bash tools/cloud/seat_setup.sh /tmp/jw` → ok; Python 3.13.17; `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`.
- `python3.13 -B -m unittest tests.test_bytes_stream_test tests.test_bytes_mac_kit` → 49 tests, 1 error (the environmental case). Includes the builder's 945-case CLI walk.
- `tests.test_bytes_h_session` → 36 OK (1312 s). `tests.test_repin` → 37 OK. `repin.py --check` → PASS. `bytes_mac_kit.py --check` → verified.
- Fences steps → all pass (`logs/fences.log`).
- `r4repro/r3/run_with_clock.py /tmp/jw r3/e2e.py KB`, then the five other round-3 scripts; `r4repro/e2e4.py /tmp/jw KB OUT`.
- Sol scripts (`reader_edges.py`, `read_cases.py`, `ci_diagnose.py`), run from a symlinked root because they resolve `parents[2]`.
- `probes.py /tmp/jw KB`: real `read`/`scan` CLI subprocesses on full-size real-`stream()` records.
- `leafwalk.py /tmp/jw KB OUT.json --cli-every 97`:
  - Base: the same eight records (receipts from the real `stream()` with a fake array module, written and reloaded by round-3 `e2e.py`).
  - Idle rows thinned to 12 per stream at 4.8 s; `battery_samples` keeps every 50th row.
  - 44,816 in-process cases. Every 97th case (450) was re-run through the real `read` CLI subprocess: 450/450 rc 0, same classes.
  - Results: `crashes 980` (all finding 1), `lost_calls 0`. `shrunk 292`: findings 2a and 2b plus artefacts that are not defects (my index-wise comparison after deleting a whole record; deleting or duplicating an idle row; valid zero values such as `settle_s`, `r_max_s`, `anchor_shift_j`, `meter_edge_w`). `silent 1135`: findings 2 and 4, plus valid zero values.
- `g2_lost_calls.py` → 0 mismatches.
- Finding-3 cases: in-process, via the leaf-walk base (the commands are in this review's shell history, summarised in the finding).
- **Not run:**
  - **PR #593 CI.** GitHub access for this session is limited to mpmdw/JouleWise-data, so I did not query mpmdw/JouleWise's Actions. Every job state is UNREAD here, not green.
  - Quick tier, the whole suite, MLX, Metal and hardware.

## Decisions I made

- **Severities:**
  - Findings 1–2 are MINOR. They break G1's "never a traceback" and "never a smaller bound", but only for inputs no production writer emits: integers above 1e308, time-reversed rows, a start before the idle end.
  - Finding 3 is MINOR. It is conservative, but contradicts §2/§4.
  - Finding 4 is a NIT, deferred to the lead because the builder documented the choice.
- **Thinned harvest:** I thinned native idle rows for the exhaustive walk only, as the builder did, but with a different shape (12 rows, a modulated power). I repeated the decisive cases on full-size data through the CLI.
- **Reading the walk:** I counted "shrunk" or "silent" as a defect only where the mutated value is malformed (time order). Where the change is a legitimate different measurement (a valid zero, an extra or missing native sample), I did not.
- **CI:** I did not work around the repository scope. I reproduced the previously red jobs' commands locally instead.
