# BYTES stage 1 §3.8 rerun with the fixed twin (RUN_STATE item 267)

Magistrate activation ed3461e5 (Opus 5.5, headless), 2026-11-11.

## Result

- **rc 7, verdict `PREDICTIONS_WRITTEN_STAGE1_DISAGREEMENT`.** Exits: a-blinded 0,
  t-blinded 0, a-fit-nokeys 1, t-1-nokeys 1 (the intended no-key refusals), a-fit 0, t-1 0.
- **Blinded agreement:** 2,531 compared; 2,421 equal, 110 under the bar, **0 above**
  (as in the first run).
- **Stage-1 agreement:** 59,068 compared; 53,858 equal, 5,138 under the bar,
  **72 above**. All 72 are the field `flags`, all at stage `fit`:
  - 4 in each of the 18 fit cells (3 models × 2 passes × {rails, rest, dc_input});
    by kind: dc_input 24, rails 24, rest 24.
  - **No `B_j`, `lower_j`, `upper_j`, `attribution_floor_j`,
    `rails_attribution_floor_j`, `B_kind:anchor` or fit-commit `w` is above the bar.**
    The first run had 318 such rows; the twin fix removes all of them.
  - The 72 `(group, key, stage)` triples are exactly the first run's 72 above-bar
    `flags` triples (set equality checked). Item 267's "about 69" is the probe's
    count of differing flag rows (RUN_STATE 266); the agreement file counts 72 fields.
- **Predictions sha256** `a6cb172c58462b76609be5ec532f1a9bcfbe474ea64d7e004e948b3ffaeb5f19`,
  **equal** to the uncommitted first-run file; `cmp` of the two `predictions.json`
  files reports them byte-identical. **Not committed.**
- `stage1-summary.json`: producing commit `a0d5b19c4f324f8df2ce743d2ae11599f3964cc7`,
  `producing_tree_dirty` false, `bytes_analysis_sha256` `18582818…0a71` (the pin),
  manifest sha256 `3cd3956e…1725` (unchanged).

Field names and counts only are recorded here (`above-bar-names.txt`, produced by
`names.py`, which never prints `a`, `t`, `abs` or `bar`). No value or sign was read.

## Steps (item 267)

1. `$W=/Users/edr/code/jw-wt/bytes-stage1` fetched `fix/2026-11-11-bytes-twin-anchor`
   and detached at `a0d5b19c4`. Diff from `df4c73e55`: `scripts/bytes_twin.py`, twin
   and agreement tests, fixtures, reports; `joulewise/` untouched.
2. `shasum -a 256 $W/joulewise/bytes_analysis.py` = `18582818c7e0…dffc0a71`. Pass.
3. `tests.test_bytes_twin tests.test_bytes_stage1`: 132 tests OK (103 s). Nothing else run.
4. §3.8 from the same `$S1` export and manifest into the new
   `--out $S1/run-twinfix` (`run.zsh` here; it refuses if the directory exists).
   11:21-12:07 PST. `$S1/run` was not touched.
5. Result above matches item 267's expectation.

## Not done (item 267)

No commitment, no records branch, no held-out key, row or store opened. The flags
question waits for the research lead's ruling (RL-80's flags branch).

## Host

Nothing armed. Only `com.joulewise.magistrate` loaded. Network time stays OFF. The
canonical root is untouched (item 263's hold). `$W` stays detached at `a0d5b19c4`;
`$S1/run` and `$S1/run-twinfix` are both kept.
