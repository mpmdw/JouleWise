# Pull request #492: gate record

Magistrate activation 1aed44f9 (Opus 5.5, headless), 2026-10-09. Structure only. The change is the window
side of the block 5 corpus erratum; its specification is the cold ruling `RULING.md` and the corrected
`ERRATUM.md` in this directory on branch `records/2026-10-block5`. The seats' full reports are in
`/Users/edr/night-archive/b5-consults/corpus18-build/` on the measurement Mac.

## Who did what

- Built by a Sol 6.1 seat at effort xhigh (`sol-window-side.md`), from the ruling's section D. The lead
  regenerated `identity_pins.json` and the pin registry, because the writer reads reference bundles the
  seat was not allowed to open.
- Reviewed and executed at `985d0722d` by a second Sol 6.1 seat at effort high that did not write the
  change (`sol-window-review.md`): `PASS-WITH-FINDINGS`.
- Cold final pass at `985d0722d` by Fable 5.1 in a new session (`FABLE-window-pass.md`):
  `FABLE PASS: PASS-WITH-FINDINGS`.
- The three commits after `985d0722d` change files under `tests/` only (`git diff --stat
  985d0722d..a5ae00c46 -- . ':!tests' ':!docs'` is empty), so the two passes stand for the head.

## What the review and the cold pass established by executing

- No file under `joulewise/` or `scripts/` changed. In each pack directory only the generator,
  `plan_tree.json` and `plan_tree.sha256` changed; the contrast generator's twin changed in one literal.
  The 280 science configurations, the 16 science order manifests, the three calibration plans, the
  reference and spare directories, the flag catalog, the campaign policy and the historical corpus are
  byte-identical to main.
- The six new members are byte copies of the first member with their own run id (1,319 bytes each, one
  differing line). Both manifests have 18 rows; the first 12 are the old rows.
- Every generator's check mode, the spares check, the sizer's check and the identity-pin check exit 0.
  The pin registry is reproduced byte for byte by the census program.
- In each plan tree the corpus stage's `expected_count` is 18 and the 18 member files and both manifests
  are pinned with digests equal to the files' SHA-256. Each rendered chain passes `zsh -n` and its corpus
  stage carries `--max-failures 18` (`DRY-RENDER.md`).
- No live logic in the chain, the driver or the runner assumes 12. Spans grow by 8,064 s (2 x 6 members
  x 672 s); `window_max_s` is 110,220 s, 112,620 s and 99,060 s; an arm needs 90.4 GiB free for ALPHA and
  BETA and 80.8 GiB for GAMMA.
- The identity pins differ from the file on main in the three plan-tree digests only.

## Findings and dispositions

| # | From | Finding | Disposition |
|---|---|---|---|
| 1 | cold pass 1, review F1 | A blinding assertion in `tests/test_harvest_b5_window.py` was narrowed to object members only | Fixed in `94a60fff4`: a boundary match that still covers arrays and strings |
| 2 | CI quick tier | `tests.test_gen_g2_phase_d` counts the corpus the prospective G2-b chain reads (23, now 29) | Fixed in `8c6e95029` (test only) |
| 3 | whole suite | `tests.test_v5_block4_replay` pins the GAMMA pack's bytes at its source commit | Fixed in `94a60fff4`: the file list is unchanged and every byte outside the erratum's three files is unchanged |
| 4 | whole suite | Four tests of `tests.test_neg8_survivors` build windows from the committed corpus and expected 12-member bounds | Fixed in `a5ae00c46` by a Sol 6.1 seat: expected values computed from the 18-member fixture with the registered formula; no assertion removed or loosened; no production defect |
| 5 | cold pass 2 | `tests/test_harvest_b5_window.py` gained an environment override for one archive path | Flag, no fix: it only decides whether two archive-gated tests skip |
| 6 | cold pass 3 | The pin registry's diff is larger than the corpus files | Flag: the committed registry was stale against the unchanged census program; no window program reads it |
| 7 | cold pass 4 | Comment strings in the chain and the sizer still say 12 | Flag: registered as deviation 9 by the ruling; the files stay byte-identical |
| 8 | cold pass 5 | The disk module's default planned bytes is the 119-member figure | Flag: the plan supplies its own figure from the plan tree |
| 9 | cold pass 6 | The recorded collection-deadline margin is more negative | Flag: a record; nothing refuses on it |
| 10 | cold pass 7, review F2 | Every window's in-window bound now takes the harvest's second route; the seal landing test still authenticates the old seal | As ruled (J2); the new seal commit follows this merge |
| 11 | review F3 | Moving t0 moves the dead-man job by the same amount, so its firing time inside a chain is fixed relative to the stages | Deferred to the desk check before GAMMA that the ruling orders (minor finding 15) |
| 12 | review F4 | Ignored `.pyc` files appeared in the review worktree during the review | Flag: the worktree's tracked and untracked state is unchanged |

## Whole suite

`pr492-suite-summary.txt` beside this file: head `a5ae00c46`, six shards and the two exclusive modules.
Three modules failed inside the parallel run and pass when run alone; they are wall-clock tests
(`tests.test_sample_quiet_predicate_evidence`, `tests.test_v5_s1_qualification`, one worker-pool test of
`tests.test_harvest_b5_window`). Every other module passed.
