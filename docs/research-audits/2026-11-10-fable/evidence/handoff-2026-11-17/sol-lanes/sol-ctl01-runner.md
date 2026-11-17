Built and pushed draft [PR #808](https://github.com/mpmdw/JouleWise/pull/808) on `cadence/2026-11-16-ctl01-runner`, from `2d347f721`.

Commits: `ca551fabb`, `74780a38c`, both with the required trailer.

Produced:

- [Scripted runtime](/Volumes/JW-EXT/jw-wt/sol-ctl01-runner/joulewise/align/apple/cadence_ctl.py) and [kit schema](/Volumes/JW-EXT/jw-wt/sol-ctl01-runner/joulewise/cadence/ctl.py), integrated with the existing runner.
- [Unfrozen draft kit](/Volumes/JW-EXT/jw-wt/sol-ctl01-runner/docs/process/cadence/kits/cl-ctl-01.draft.json).
- [Synthetic tests](/Volumes/JW-EXT/jw-wt/sol-ctl01-runner/tests/cadence/test_ctl.py), [documentation](/Volumes/JW-EXT/jw-wt/sol-ctl01-runner/docs/process/cadence_ctl_runner.md), and [run report](/Volumes/JW-EXT/jw-wt/sol-ctl01-runner/docs/run_reports/2026-11-16-ctl01-runner.md).
- PR body at `/Volumes/JW-EXT/scratch/ctl01-runner-20261116/PR-BODY.md`; reread and matched after creation and update.

**193 focused tests passed.** Final-head CI remains running. Qualified canonical discovery remains running with signalling modules stubbed. The fixture census failed because `ps` is denied.

**No ADMIT yet:** the requested wrapper failed before starting Sol: `sandbox_apply: Operation not permitted`. The review packet is ready at `/Volumes/JW-EXT/scratch/mythos-sandbox/ctl01-runner-20261116/BRIEF.md`.

Open questions—none decided:

1. **Lead:** run the prepared wrapper externally, or authorize a fresh built-in Sol reviewer? Recommend external launch; ADMIT is blocked.
2. **Lead:** permit #794’s qualification integration if CI inherits v1.1’s existing failures, or preserve the exact baseline? Recommend integration for a green baseline.
3. **Lead/research lead:** does the requested Sol review satisfy RL-174’s named Mythos seat?
4. **Research lead:** after reading `lm-inst-01`, what doses and recovery duration should freeze?
5. **Research lead:** confirm visible caps, extra/CPU turn shapes, split gaps, and equal token counts versus literal sequence replay.
6. **Research lead:** accept the logged-envelope/physical-call audit contract for the controls print?
7. **Lead:** settle the phase pin, layout, seed, dates, consumer balance, pilot and native smoke.
8. **Lead:** assign and freeze the controls print/schema/manifest and disclosure amendment before energy access; obtain an external fixture census.

No measurement-Mac contact, hardware work, `RUN_STATE.md` edit, or merge.