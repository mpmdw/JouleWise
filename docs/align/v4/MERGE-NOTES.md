# v4 line: notes for the merge to main

2026-11-08. Read with `docs/analysis/v4/MERGE-ORDER.md` (on `engine-r23j`): the v4 line lands on `main` first
and wins every arm-stack conflict.

## Air-offload: duplicated additions (resolve as identical)

`ops/2026-11-08-air-offload-merged` @ `b5af05e12` is based on pruned main (`dcfa4c593`). It was not merged into
this line. Commit `5cce0c677` applies the lane's own change set instead (`git diff dcfa4c593..b5af05e12`, 13
files, all additions; the 14th path of that diff, a `CANONICAL.md` row, is excluded):

- `configs/ops/air_offload_rates.json`
- `docs/ops/AIR-OFFLOAD.md`, `docs/ops/AIR-OFFLOAD-AGREEMENT.md`
- `scripts/offload_bench.py`, `scripts/offload_setup_air.sh`, `scripts/offload_setup_mbp.sh`, `scripts/offload_window.py`
- `tests/test_offload_bench.py`, `tests/test_offload_delta2_sol1.py`, `tests/test_offload_delta2_sol2.py`,
  `tests/test_offload_delta_fixes.py`, `tests/test_offload_review_fixes.py`, `tests/test_offload_window.py`

When the lane (or this line) is merged into `main`, these 13 files are byte-identical on both sides and must be
resolved as identical (add/add with the same content). If git reports any difference in them, stop: the line or the
lane changed one of them after `5cce0c677`.

## Harvest-off

`align/2026-11-08-harvest-off-fix` @ `d5dc1198c` is a real merge (`c84df94bf`). It moves the pin of
`joulewise/b5/harvest.py` to `42cad8dec4295eef530b71374a8e4d0158a17028f5418c1507a56678ac49ab47` in
`tests/align/test_measurement_core_boundary.py` and `tests/align/test_thermal_sidecar.py`. The merge to `main`
also needs a cited `repin` for the sealed packs that pin `joulewise/adapters/powermetrics.py`
(`document_memo`); `python3 scripts/repin.py --check` is stale for them until then.

## Timing receipts: chain settle text changed (STRICT re-registration needed)

The Opus cold review of the timing-receipts fix delta (`docs/align/reviews/2026-11-08-timing-receipts-opus-cold-review.md`)
led to a change of the generated chain text: `settle()` in `joulewise/b5/chain.py` is now an unconditional
`/bin/sleep "$SETTLE_S"` with two marker writes around it from an inline stdlib-only helper
(`B5_SETTLE_MARK_PY`, from `SETTLE_MARK_HELPER`), replacing the earlier `B5_SETTLE_PY` package-importing helper.
`joulewise/b5/chain.py`, `scripts/run_night.py`, `scripts/align_v4_session.py` and `joulewise/hazards/arm.py` are
all in the registered closure, so their bytes changed under the registration: the STRICT re-registration (the
receipt over the artifact set, with the regenerated chain/night plan text) must be redone from this commit
before any window arms. Nothing was re-registered here.

## Merge c84df94bf: R17 finality and R22-1 disclosure-only records

The Sol review of the harvest-off merge (`docs/align/v4/MERGE-C84-REVIEW-sol.md`, branch
`align/2026-11-08-merge-c84-sol` @ `71a18a46b`) held on one defect: R17 finality
(`light_triage.final_adjudication_error`, shared by `cmd_final` and `WindowRecord`) compared the desk's
`members_excluded` with `exclusions.json` directly, so a valid contention-only desk (`members_excluded: []`,
`members_disclosure_only` set) could never be final. The comparison is now one function,
`v4_contention.recorded_exclusion_map` / `records_agree_with_harvest`, used by both finality and
`effective_desk`: the desk's and PILOT's `members_excluded` union `members_disclosure_only` must equal the
harvest's exclusions (same members, same codes). Real exclusions still have to agree exactly. The witness module
`tests/align/test_merge_c84_sol.py` is in unmodified and green; `tests/align/test_final_disclosure_agreement.py`
adds the mixed and real-exclusion controls.

## Dynamic closure trace

The trace was regenerated with the `timing_receipts_delta` scenario restored (Opus LOW-5). Executed paths grew by
`joulewise/align/apple/light_triage.py` and `joulewise/session_structure.py`, which the harvest-off lane already
added to the registered closure. `joulewise/align/apple/harvest_offload.py` and `scripts/align_v4_harvest_off.py`
(post-window pack tooling the lane deliberately kept out of `EXECUTED_CLOSURE`) are imported by
`tests/align/test_v4_next_arm_packet.py` only to assert equal constants, so the trace script now lists them in
`EXCLUDED_FILES` rather than reporting them executed-but-unbound. The closure itself is unchanged.

## Deviation: the LOW-2 spill file (lead ruling, accepted)

`scripts/run_night.py:_timing_journal` now creates `night/timing-receipts.jsonl` when a run has no `night.log`
(arm-only invocations). This departs from SPEED-TOOLBOX's "create no new files" and is ACCEPTED: losing those
markers is worse, and the file is written after the operation closes, never during a window or a dwell. A run
with a `night.log` appends to it as before. Recorded in `docs/align/v4/DEVIATIONS.md` (TR-spill-LOW-2).
