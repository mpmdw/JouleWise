FINAL PASS: MERGE

PR #438 `docs/2026-09-27-d528efb2` -> `main`, merge candidate `591e4574` (== origin branch tip, confirmed by `git ls-remote`). Cold Fable 5.1 final pass, 2026-09-29, detached worktree `/Users/edr/code/JouleWise-wt-438final-ff50b201`.

## Check 1 -- merge and tests
- `git merge-tree --write-tree origin/main 591e4574` -> exit 0, tree `fa2d1927`, which equals `591e4574^{tree}`; merge-base `e3baaf2d`; `git diff --stat 591e4574 fa2d1927` empty. The merged result IS the branch tree, so everything below was run on the exact tree that lands.
- `python3 -B -m unittest tests.test_docs_freshness tests.test_gen_state` -> `Ran 75 tests ... OK`.
- `python3 scripts/gen_state.py --check` -> exit 0, no output.
- `git diff --stat 016f03a4 591e4574 -- ':!docs' ':!RUN_STATE.md' ':!TASK_QUEUE.md'` -> empty: every commit after the row-9 head touches only records/RUN_STATE/TASK_QUEUE. Whole PR outside `docs/`: `RUN_STATE.md`, `TASK_QUEUE.md`, `tests/test_gen_state.py` (count 281 -> 288, matching `TASK_QUEUE.md:671` and the kernel).

## Check 2 -- overstatement
- `git ls-remote origin`: all 17 branch heads named in RUN_STATE/record match (main `9eab16f8`; A `c3137f46`; L `478f5709`; H3 `cdfb27ce`; B `d4345946`; N1 `36e8ba6e`; D-138 `b953f4b0`; fence `069df719`; A130 `a3d0a4f4`; calexits `5c447604`; small-lanes `0f242228`; one-use `b53725b3`; wallclock `1dceb172`; inventory `05fca1af`; wip A `b0474eaa`; wip L `c1589d94`). This closes delta-3 flag F4 (remote checks the DNS-blocked audit could not run).
- Record items 128-160 swept for "merged/ratified/MERGE": item 133 says "#438 opened, not merged"; the only "merged" claims are historical PRs (#165, #276, #285) and the lane-sweep stack (item 129). Row-1 verdict `AUDIT: FAIL` (item 130) matches `61-bkpr2/01-audit-report.md:1`; item 139 header `DELTA: FINDINGS`; item 144's 268 modules / 7,549 tests / 0 / 0 / 109 skips matches `61-bkpr2/row9-tail.txt` `WORKERS SUMMARY ... result=PASS exit=0`.
- RUN_STATE top three blocks: RESUMED line (13) declares the PAUSED block history; PAUSED table heads match origin; the `SUCCESSOR'S NEXT EXACT ACTION` header (72) is marked SUPERSEDED. Item 160's "44 logs + 5 probe logs" = 49 added; "232 KB" is `du` of the 44 (bytes 110,377; `du -kc` of all 49 = 256 KB), consistent. "50 `.log` already tracked as precedent" verified (`git ls-tree origin/main`: 50).

## Check 3 -- delta-3 F1-F3 at 591e4574 (`git diff 0d26929b 591e4574`)
- F1 CLOSED: `RUN_STATE.md:48` struck through and marked "DONE or superseded 09-29, item 160"; line 30 now reads `478f5709 on origin (parent 76711800)`, agreeing with lines 40/44; line 72 header supersedes the stale seat lines 73/81/87.
- F2 CLOSED: record line 583 now cites "item 153's follow-on seat for A120" with an erratum naming the prior "item 150".
- F3 CLOSED: `RUN_STATE.md:53` quote is byte-identical to record line 612 (item 159) including "tokenm" and "fixec"; the label is now "exact words in record item 159", not "verbatim".
- Surviving stale lines, none misleading given the RESUMED banner (non-blocking, for the successor branch since this branch is frozen at item 160): line 41 "D-138 still stopped, waiting for Ed's choice" (Ed chose (a), line 52); line 45 "F5 ... are Fable's" and line 54 "Fable does them first" (done by the orchestrator, item 160); line 54's "44" (49 actual, explained in item 160).

## Check 4 -- the 49 force-added `.log` files
- `git diff --name-only --diff-filter=A 9eab16f8 591e4574 -- '*.log'` -> 49 files, 116,807 bytes, all under `docs/process_traces/2026-09-27-activation-d528efb2/` (30-s1-repair 10, 50-d138-issuance-seat 22, 71-ntp-design 17): unittest/probe/replay output.
- grep for keys/tokens/private keys/Bearer/api_key/password/emails (`passmail`, `glaring610`, `copper531`, gmail/proton)/Authorization/URLs -> 0 hits. Only PII-adjacent content is `/Users/edr` home paths (18 hits), already present 3,434 times in tracked `docs/` on main. Public-safe.

## Check 5 -- ledger rows 11 and 12
- Row 11: CI run 36618913843 on `591e4574` -> `completed success`, 14/14 jobs (build, changes, fences, installed-wheel, quick, test x6, calibration-exits-exclusive, calibration-writer-crash-matrix-exclusive x2). The separate `gate-ledger` check (run 36618913578) fails only because rows 11-12 still read PENDING in the PR body. Post-merge cross-unit integration review: the merge result is the branch tree itself (check 1), so the integration tree reviewed here is the merged tree; the three non-docs files are consistent with each other and the kernel (`--check` exit 0). Row 11 evidence text: `CI run 36618913578/36618913843 on 591e4574: 14/14 jobs success; merged tree == branch tree fa2d1927; cross-unit review by Fable final pass (this ruling).`
- Row 12: this ruling, cold Fable 5.1 on the exact merge candidate `591e4574`, all five checks executed as listed; verdict MERGE. Row 12 evidence text: `Cold Fable 5.1 final pass on 591e4574: MERGE (scratchpad/438final/ruling.md; copy into the successor record).`

## Blocking findings
None.

## Merge-time steps for the merger (not done here; no edits made)
1. Edit the PR body: replace rows 11 and 12 `PENDING ...` with the evidence text above so the `gate-ledger` check reruns green.
2. Merge `591e4574` exactly (no further commits to this frozen branch); copy this ruling into `docs/process_traces/2026-09-29-interactive-ff50b201/` on the successor branch together with the three RUN_STATE nits in check 3.
