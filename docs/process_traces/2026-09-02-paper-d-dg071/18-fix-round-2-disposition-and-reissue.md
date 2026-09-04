# Fix round 2 — magistrate disposition and artifact re-issue (2026-09-02)

Seat: Sol xhigh (`17-sol-247-fix-round-2.md`), brief `16-fix-round-2-brief.md`,
WRITE_SCOPE `scripts/issue_dg071_dg075_statistics.py` +
`tests/test_issue_dg071_dg075_statistics.py`. Wrapper status:
`semantic_status=clean completion=complete run_status=OK scope_action=passed
rc=0`; envelope 4251 bytes; closures C1–C7 all `done`, no deviations.

## Magistrate review of the diff (read in full at the bench)

- C1 population: `_read_records` groups contiguous rows by `timestamp_s`
  literal; `_record_from_group` refuses `record_rail_set_mismatch` unless the
  group is exactly one row per rail in `{cpu_power, gpu_power, ane_power}`
  with byte-identical endpoint literals; a timestamp literal that returns after
  another group began refuses `records_not_contiguous` (checked before the
  monotone check, so interleaving is named as interleaving). One width per
  record. JSON carries `sampler_record_count`, `rail_row_count`, `rails`; the
  "duplicate timestamps" fields are gone.
- C2 arithmetic: endpoints parsed with `Decimal(literal)` after the
  emptiness check, `is_finite()` refusal kept; `_quantile` computes
  h = (n−1)·p exactly and interpolates exactly; seconds emitted as
  `format(d, "f")` strings; `_ms` renderings quantized to
  `MS_RENDER_QUANTUM = Decimal("0.0001")` ROUND_HALF_EVEN, also strings;
  `SCHEMA_VERSION` → `…v2`; `MS_DECIMALS` and `import statistics`/`math`
  removed.
- C3 disclosure: `method` object in the JSON (population, arithmetic,
  quantile, median, iqr, millisecond_rendering, float64_replication,
  dg075_dependence) and a `## Method` section in the Markdown with the
  addendum's float64 sentence verbatim and the worked example. Sol added one
  sentence the brief did not dictate — "A separately rendered IQR can differ
  from the difference of rendered quartiles by one unit in the last place" —
  which is true of this bundle (122.9227 − 116.9720 = 5.9507 vs rendered IQR
  5.9508) and is accepted as a replication-bar improvement.
- C4 tiling: `_verify_tiling` refuses `records_do_not_tile` on any
  `interval_end_s` literal ≠ `timestamp_s` literal or any boundary gap
  > `Decimal("0.000001")`; JSON reports `max_tiling_gap_s` (`"0.0000004"`) and
  `tiling_gap_nonzero_boundaries` (100), matching the bench census in the
  addendum (`14a-dg071-bench.py`).
- C5 refusals: 16 refusal names, 16 through-`main` tests (table in file 17);
  both dictated mutants killed by exactly their named test (`Ran 22 … FAILED
  (failures=1)` each). The dropped `statistic_sample_empty` refusal is
  unreachable (records ≥ 2 ⇒ widths ≥ 2, spacings ≥ 1) — accepted.
- C6 precision: fixture at epoch magnitude with middle widths whose exact mean
  renders `120.9186` and whose float64 mean renders `120.9185`; both asserted.
- C7 replay: two pre-landing runs byte-identical; renderings match the
  addendum's expected values exactly.
- Docstring: cites the addendum path; "R-167-1" no longer appears in the
  producer (Opus N-1 closed).

Carried to the delta re-audit as a NIT, not a fix: two distinct
`timestamp_s` literals that are numerically equal (e.g. `…1` vs `…10`) would
pass `timestamps_non_monotone` (strict `<`) and form two records with a zero
DG-075 spacing. The retained bundle has none (406 literals, 406 distinct
values); the refuter decides whether it is worth a refusal.

Disposition: LANDED as commit `29181d6c` (magistrate commit; seat cannot
commit in a linked worktree). Artifact re-issued at the bench (below).

## Executed evidence

```
$ cd /Users/edr/code/JouleWise-wt-paper-d
$ TMPDIR=<scratchpad>/tmpbench /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics
Ran 22 tests in 0.149s

OK
exit=0
$ git commit … → 29181d6c
$ for r in a b; do TMPDIR=<scratchpad>/tmpbench PYTHONDONTWRITEBYTECODE=1 \
    /Users/edr/code/JouleWise/.venv/bin/python scripts/issue_dg071_dg075_statistics.py \
    --out <scratchpad>/reissue-$r/dg071-dg075-statistics.json; echo "exit=$?"; done
wrote <scratchpad>/reissue-a/dg071-dg075-statistics.json
wrote <scratchpad>/reissue-a/dg071-dg075-statistics.md
DG-071 median_ms=120.9186 iqr_ms=5.9508
DG-075 median_ms=120.9224 iqr_ms=5.8949
exit=0
wrote <scratchpad>/reissue-b/dg071-dg075-statistics.json
wrote <scratchpad>/reissue-b/dg071-dg075-statistics.md
DG-071 median_ms=120.9186 iqr_ms=5.9508
DG-075 median_ms=120.9224 iqr_ms=5.8949
exit=0
$ shasum -a 256 <scratchpad>/reissue-*/dg071-dg075-statistics.*
5d96505f7940a9306e9e03c574329bcce6fa5c3d179a5fb76f8ea9b44a693b0d  reissue-a/dg071-dg075-statistics.json
357410c69e6a32b210979aedc7782a3c5319c598957bd4aabef0b4ae7363969d  reissue-a/dg071-dg075-statistics.md
5d96505f7940a9306e9e03c574329bcce6fa5c3d179a5fb76f8ea9b44a693b0d  reissue-b/dg071-dg075-statistics.json
357410c69e6a32b210979aedc7782a3c5319c598957bd4aabef0b4ae7363969d  reissue-b/dg071-dg075-statistics.md
$ cmp reissue-a/…json reissue-b/…json && cmp reissue-a/…md reissue-b/…md && echo BYTE-IDENTICAL
BYTE-IDENTICAL
exit=0
$ grep -n '"git_commit"\|sampler_record_count\|rail_row_count\|max_tiling\|nonzero' reissue-a/dg071-dg075-statistics.json
14:  "max_tiling_gap_s": "0.0000004",
26:    "git_commit": "29181d6cdf7bcea89540c52eba39965363f5446f",
30:  "rail_row_count": 1218,
40:  "sampler_record_count": 406,
68:  "tiling_gap_nonzero_boundaries": 100
```

The re-issued pair replaces `docs/paper/round7/dg071-dg075-statistics.{json,md}`
(the a3dadadd issue withdrawn by the addendum). The producer's SHA-256s at
`29181d6c` differ from Sol's pre-landing replay (`198fe3b8…`/`03126994…`)
only through the embedded `git_commit`, as Sol's report predicted.

Owed next: execution-lens delta re-audit of the re-issue by a different
model (file 19/20), Opus counter-review, fresh pass, PR.
