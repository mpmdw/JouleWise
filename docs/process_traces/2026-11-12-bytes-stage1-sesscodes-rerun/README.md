# BYTES stage 1 §3.8 rerun with the session-codes twin (RUN_STATE item 283)

Magistrate activation 5fe31705 (Opus 5.5, headless), 2026-11-12.

## Result

- **rc 0, verdict `READY_TO_COMMIT`.** Exits: a-blinded 0, t-blinded 0,
  a-fit-nokeys 1, t-1-nokeys 1 (the intended no-key refusals), a-fit 0, t-1 0.
- **Blinded agreement:** 2,531 compared; 2,421 equal, 110 under the bar, **0 above**
  (as in both earlier runs).
- **Stage-1 agreement:** 59,068 compared; 53,930 equal, 5,138 under the bar,
  **0 above**. Item 268's 72 above-bar `flags` rows (4 in each of the 18 fit cells)
  now agree: the equal count rose by exactly 72 (53,858 to 53,930) and the
  under-bar count is unchanged at 5,138.
- **Above-bar field names and counts by cell kind:** none (`above-bar-names.txt`,
  produced by `names.py`, which never prints `a`, `t`, `abs` or `bar`).
- **Predictions sha256**
  `a6cb172c58462b76609be5ec532f1a9bcfbe474ea64d7e004e948b3ffaeb5f19`, **equal** to
  the `run` and `run-twinfix` files; `cmp` of `run-twinfix/out/a-fit/predictions.json`
  against `run-sesscodes/out/a-fit/predictions.json` reports them byte-identical.
  **Not committed.**
- `stage1-summary.json`: producing commit `1e78224cdd5b49bd0c0fc5ada98d07f93cfb1e30`,
  `producing_tree_dirty` false, `bytes_analysis_sha256` `18582818…0a71` (the pin),
  manifest sha256 `3cd3956e…1725` (unchanged).

No value or sign was read.

## Steps (item 283)

1. `$W=/Users/edr/code/jw-wt/bytes-stage1` fetched `fix/2026-11-11-bytes-twin-sesscodes`
   and detached at `1e78224cd`. Diff from `a0d5b19c4`: `scripts/bytes_twin.py`, twin
   and agreement tests, a fixture, `scripts/test_timings.json`, reports;
   `joulewise/` untouched.
2. `shasum -a 256 $W/joulewise/bytes_analysis.py` = `18582818c7e0…dffc0a71`. Pass.
3. `tests.test_bytes_twin tests.test_bytes_stage1` from `$W`
   (`TMPDIR=/private/tmp/jwbytes-tmp`, `JW_B5_SYNTHETIC_ONLY=1`): 144 tests OK
   (117 s). Nothing else run. (A first invocation from the canonical root's cwd failed
   to import the modules, so 0 tests ran; nothing executed.)
4. §3.8 from the same `$S1` export and manifest into the new
   `--out $S1/run-sesscodes` (`run.zsh` here; it refuses if the directory exists).
   04:20:22-05:06:14 PST. `$S1/run` and `$S1/run-twinfix` were not touched.
5. The result matches item 283's expectation (rc 0, nothing above the bar).

## Not done (item 283)

No commitment, no records branch, no held-out key, row or store opened. The
commitment waits for the lead's item after the research lead confirms; held-out
waits for the research lead's blind ruling on P1.

## Host

Nothing armed. Only `com.joulewise.magistrate` loaded; no `com.joulewise.night*`
label or plist. Network time stays OFF. The canonical root was fast-forwarded once at
launch (`b4c7859bf` to `7d67c7aa4`, RUN_STATE only), after the no-night-agent check;
it was not touched otherwise. The R1 smoke worktree was untouched. `$W` stays
detached at `1e78224cd`; `$S1/run`, `$S1/run-twinfix` and `$S1/run-sesscodes` are kept.
