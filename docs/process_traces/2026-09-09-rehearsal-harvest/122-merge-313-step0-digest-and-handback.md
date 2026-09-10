# 122 — PR #313 merge record, canonical fast-forward, step-0 digest check, and interactive hand-back (2026-09-10 ~04:10 PDT)

Interactive magistrate (session `01MrRehZWopqKNDv5Uy466AC`), bench = canonical `/Users/edr/code/JouleWise`.

## Merge

PR #313 merged at `4681e522` (`gh pr merge --merge`) after: refuters 116/117 at b746d966, fix round 1 e9df549a, delta 118 clean,
residual nit at 7d1354d5, terminal review 119, replay 120 (7d1354d5 alone, 5654 tests rc 0), gate ledger on the PR body (row 12 = the
PR head, as `scripts/check_gate_ledger.py` requires; `gate-ledger` job pass at 11:0x UTC after the row-12 correction).

Honesty note on CI at merge time: the CI run on 7d1354d5 completed success at 10:17 UTC (run 34465286275, all jobs). Editing the PR body
for the ledger re-triggered the `ci` workflow, and that duplicate run on the same sha was still in progress when the merge was issued;
the merge did not wait for it. The post-merge CI on main at 4681e522 is the run to cite for row 11's "post-merge" half.

## Canonical fast-forward and MAGISTRATE_WATCHDOG.md step 0 (five-file digest check)

Executed verbatim from the document in `/Users/edr/code/JouleWise` on `main` at `4681e522` (a merge commit, two parents):

```
e146083ad899059e6fd94353c5bfe5000b94b763ac927804dd64cd696d0a9dac  4681e5221302ac4790b387166f6cfa28b5a21049:scripts/magistrate_watchdog.py
e146083ad899059e6fd94353c5bfe5000b94b763ac927804dd64cd696d0a9dac  scripts/magistrate_watchdog.py
511e7cf8e25309e26a74e9b3dbac6ed1a6e7d5c1fa1f440e9a934052b80245cf  4681e5221302ac4790b387166f6cfa28b5a21049:scripts/install_magistrate_watchdog.sh
511e7cf8e25309e26a74e9b3dbac6ed1a6e7d5c1fa1f440e9a934052b80245cf  scripts/install_magistrate_watchdog.sh
d27016694b67ebe93bfc60edc20bc480a8b10be49eae979460610ac824b954d9  4681e5221302ac4790b387166f6cfa28b5a21049:docs/process/MAGISTRATE_WATCHDOG.md
d27016694b67ebe93bfc60edc20bc480a8b10be49eae979460610ac824b954d9  docs/process/MAGISTRATE_WATCHDOG.md
e2f836d5103ce6bf3b53fe7fd5d93fded2995273d6a1a4b1c0e4198b1f56ae0e  4681e5221302ac4790b387166f6cfa28b5a21049:docs/process/MAGISTRATE_RELAUNCH_PROMPT.md
e2f836d5103ce6bf3b53fe7fd5d93fded2995273d6a1a4b1c0e4198b1f56ae0e  docs/process/MAGISTRATE_RELAUNCH_PROMPT.md
6b70b924949f57eb2c2e6f230aa10be25802b12d49d92d79415653af6082cc73  4681e5221302ac4790b387166f6cfa28b5a21049:docs/process/NIGHT_HANDBACK.md
6b70b924949f57eb2c2e6f230aa10be25802b12d49d92d79415653af6082cc73  docs/process/NIGHT_HANDBACK.md
STEP0_OK
```

The live watchdog (`com.joulewise.magistrate`, StartInterval 300 s) renders the relaunch prompt from this canonical checkout, so every
activation spawned after this point carries prompt line 24 (the directive channel). Activation 7ce7af2a (spawned 20:52 PDT 09-09) keeps
the 23-line prompt until it exits.

## Hand-back

Ed's instruction (verbatim, ~03:30 PDT): "KILL as long as you can keep experimenting and have all the tools to keep running windows until
you have a paper". After this record and the T38g checkpoint are on main, the interactive magistrate terminates the two interactive
`claude` process groups (pid 16371, Terminal session of 20:13 PDT 09-09, with its codex mcp-server pair; and pid 17047, this session,
with its codex mcp-server pair and the harness's transient caffeinate), so the resident activation's runbook-67 census can pass and the
arm of rehearsal-20260911 can proceed inside the 09-10 03:00–06:30 window. No process of the resident activation is signalled.
