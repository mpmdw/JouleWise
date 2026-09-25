# A292 scored reducer: all 54 acceptance tests pass, nothing needs a ruling

The reducer is written in `joulewise/scored_reduce.py`, the only file I changed. Nothing is committed. I did not open `tests/scored_reduce_checker.py`, and no test depends on the specific inputs it uses.

## (1) `tests.test_scored_reduce`, all 54 tests

```
Ran 54 tests in 1243.208s

OK
```
The run took about 21 minutes. Nearly all of that is the 200-night differential test building its cases, at about 2 s per night. The reducer itself takes about 0.3 s per night. The other 53 tests also pass on their own in about 46 s.

## (2) Packer suites
```
tests.test_scored_packer:        Ran 41 tests in 11.624s — OK
tests.test_scored_packer_fuzz:   Ran 6 tests in 51.496s — OK
  FUZZ cases=4 submissions=1798 census={'inv_02': 808, 'inv_03': 99, 'inv_11': 447, 'inv_12': 41, 'inv_38': 372, 'inv_39': 8, 'inv_52': 23}
```

## (3) NEEDS_RULING
None. No test contradicted E2. Four places where E2 left a choice open, so you can check them:
- **Check order within a phase:** each window, then each row, goes through that phase's whole ordered list of checks before the next one starts. The completeness phase checks missing windows in placement order, then null anchors in window input order, then missing rows in placement order.
- **Which envelope index the window binding uses:** the in-force digest is computed from the placement's envelope index, not the index written on the window. Otherwise a window with a wrong index would fail as `window_binding` instead of `window_envelope`.
- **Where `k` and `claim_ready` come from:** E2 does not define `k`. I took "`k` = number of counted windows" from the Opus design seat (07/03-seat-opus:87). I took `mode` from the registration and `claim_ready` from the roster, as ex-20:147 has them; E2 did not change either. This means I read beyond E2 for these field meanings only, not for any rule.
- **`retry_stage_counts`:** only stages that actually occur get a key. The oracle agrees.

## (4) E2 clause → function in `scored_reduce.py`

| E2 clause | Where |
|---|---|
| ENTRY: five positional parameters, verifier call first, pure, `import joulewise.scored_registration as sr` | `reduce` (first statement `verify_executed_roster(registration, roster, predicted_decode_s)`); outputs are fresh values or deep copies |
| `STOP_REASONS`, `REDUCTION_CODES` (22 codes), `ReductionRefusal(.code, .detail)` | module constants and `ReductionRefusal` |
| `in_force(k)` | `_in_force` |
| CLASSIFICATION live / terminal / voided, plus each key's observation | `_classify` |
| Phase 2 `reduce_input` | `reduce`, second statement |
| Phase 3 window checks: keys → domain (including anchor shape) → unknown → binding (in-force) → duplicate → envelope → unstarted | `_check_window` |
| Phase 4 row checks on all rows: keys → domain and coherence → stop_reason_unknown → scorer → unknown → binding (final digest) → duplicate → unstarted → tokens_over_cap → cap_disagreement | `_check_row` |
| Phase 5 completeness: `missing_live_window` (detail is `repr(key)`), then `anchor_energy_envelope_unrecorded`, then `row_missing` | `reduce`, the three loops after the row checks |
| Phase 6 `executed_status(..., frozenset(live keys))`, output copied unchanged | `reduce` (the `status = ...` line) |
| Phase 7 `internal_disagreement`: recount fully counted parents and distinct envelopes, compare with `spread_exceeded` | `reduce`, the loop over cells after they are built |
| CAP: `capped` / `correct` (K3), `malformed`, `cap_tokens_arm` (the name `cap` is never used) | `_derived`; `malformed` and `cap_tokens_arm` in `reduce` |
| `cap_bound` over paired items, division form, reads `sr.CAP_BOUND_FRACTION` when called | `reduce`, cell construction |
| K24 pairing: `paired`, `n_counted`, `k24_dropped`, `unpaired_item_ids` | `reduce`: item construction (`paired`), parent and cell construction |
| `attempt_divergence` | `reduce`, item construction (compares against superseded rows) |
| Parents: `g_j` summed with `fsum` once per counted window, `k`, `fully_counted`, item-weighted `position` | `reduce`, parent loop |
| Cells, levels (`max_gap = registration.max_gap`) | `reduce`, cell and level construction |
| `counted_windows` in placement order; `uncounted_windows` in input order with reason | `reduce` |
| M1 `terminal_refusals`: the roster's 7 keys plus `window_key` plus `gross_j` (ceiling violation gets the window's value or null; unattributed overrun is always null) | `reduce`, the terminal-refusal loop |
| `superseded_rows` unchanged in input order; `sha256` of canonical JSON | `reduce` output block and `_canon` |

Still for you to do before merge: the M8 mutation sweeps and the cold gate. Mutants I checked by reasoning are killed by specific tests:
- `>=` changed to `>` in `capped`: killed by `test_cap_boundary_cap_minus_one_and_cap`.
- Deleting the `row_tokens_over_cap` guard: the input then refuses as `row_cap_disagreement` instead, so the test still fails.
- Replacing `sr.CAP_BOUND_FRACTION` with a literal: killed by the 0.30 patch test.

Two things outside my scope: the claude.ai Anthropic Economic Index connector needs authorizing in claude.ai connector settings before it can be used; this task didn't need it. Also, `MEMORY.md` is over its size limit (25.7 KB against 24.4 KB), so its last 7 lines are being cut off when it loads.
