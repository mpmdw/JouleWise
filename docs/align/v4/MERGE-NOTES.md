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
