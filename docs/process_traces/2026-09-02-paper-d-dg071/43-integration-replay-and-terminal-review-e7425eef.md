# File 43 — integration replay for PR #276 at the final head `e7425eef`, 2026-09-02

Operation-loop §5 rows 9 and 12 evidence. The integration tree is a
scratch merge commit (never pushed) `f79d193b` = `e7425eef` (this PR's head,
which already contains main `31de700a` via `9ab5838a`) + `7488a3c0` (the
t26-b branch head at the time; `tests/test_gen_state.py` count reconciled to
128). Both commands below were run by the magistrate at the bench and are
pasted from the terminal log; nothing is transcribed.

## Full canonical suite on the integration tree (unpiped, `wt-integ2`, `TMPDIR=<scratchpad>/tmpinteg3`)

```
$ cd /Users/edr/code/JouleWise-wt-integ2 && git log --format='%h %p' -1
f79d193b e7425eef 7488a3c0
$ python3 -m unittest discover -s tests      # log: <scratchpad>/out/integ3-fullsuite-f79d193b.log
----------------------------------------------------------------------
Ran 4847 tests in 4334.878s

OK (skipped=125)
rc=0
```

The 125 skips are the standing hardware/quiet-window skips (same count as
the previous integration replay in file 36's series).

## Re-issue of the DG-071/DG-075 artifact at the PR head (`wt-paper-d` @ `e7425eef`, clean tree)

```
$ git rev-parse --short HEAD && git status --short | wc -l
e7425eef
       0
$ python3 scripts/issue_dg071_dg075_statistics.py --repository-root . --out <scratchpad>/reissue-k/dg071-dg075-statistics.json 2>&1 | tail -3
wrote <scratchpad>/reissue-k/dg071-dg075-statistics.md
DG-071 median_ms=120.9186 iqr_ms=5.9508
DG-075 median_ms=120.9224 iqr_ms=5.8949
$ shasum -a 256 <scratchpad>/reissue-k/*
9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7  <scratchpad>/reissue-k/dg071-dg075-statistics.json
041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b  <scratchpad>/reissue-k/dg071-dg075-statistics.md
$ cmp <scratchpad>/reissue-k/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.json && cmp <scratchpad>/reissue-k/dg071-dg075-statistics.md docs/paper/round7/dg071-dg075-statistics.md && echo BYTE-IDENTICAL-AT-$(git rev-parse --short HEAD)
BYTE-IDENTICAL-AT-e7425eef
```

Same digests as the reissue recorded in file 36 (`reissue-h`/`reissue-i` at
`6b6deb2f`): the committed artifact is reproducible at the merge candidate.

## Magistrate terminal review (row 12) of `e7425eef`

The merge candidate's post-review commits since the last fresh pass (terra
254, file 37) are custody and bookkeeping only: files 38–42 (cold-gate
packet, Sol 255 consult, cold Fable ruling, Opus refutation, synthesis), the
kernel row `DG071-PROVENANCE-TEST-01` with its `test_gen_state` literal, and
the merge of main. No producer, test-module, or paper-artifact bytes changed
after `2eea71fe`; the replay above and the byte-identical reissue at the
head are the evidence. Merge proceeds under D-072 with `--merge`.
