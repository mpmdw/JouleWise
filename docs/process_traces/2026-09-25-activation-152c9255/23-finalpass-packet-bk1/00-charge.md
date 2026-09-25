# Charge — cold Fable final pass BK1-FINALPASS-01: the docs/bookkeeping merge candidate of activation 152c9255

Assembled 2026-09-25 07:16 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## What you rule on

- **Merge candidate:** branch `docs/2026-09-25-152c9255-bk1`. Rule on the head named in the next line.
- **Diff:** vs `origin/main` `c034a56f`. About 193 files: `docs/process_traces/` for activations 278ebc9e and 152c9255, `docs/process/state_kernel.json`, `RUN_STATE.md`, `TASK_QUEUE.md` and `tests/test_gen_state.py`.
- **Purpose:**
  - land the predecessor's remaining records and this activation's records and cold rulings on main. PR-R needs the acceptance ruling file on main before it merges, because its sealed registration cites that file;
  - register the new lanes;
  - refresh the RUN_STATE resume pointer.

## Review history

The Opus fidelity lens on the prior head `b41ccd57` is `ex-22-fidelity-lens.md`: 0 BLOCKER, 3 SHOULD-FIX and 3 NIT, all applied by the magistrate at the bench in the commit after `b41ccd57` (record 00 item 52).

## Questions

- **V1.** Verify the lens's two hard checks yourself on the candidate head:
  - no MATH problem text anywhere in the diff (ids and hashes only; this is Ed's E1 answer);
  - only the allowed paths change.
- **V2.** Verify that every lens finding is closed as record 00 item 52 says, and that the post-lens commit introduced nothing else.
- **V3.** Run `python3 scripts/gen_state.py --check` and `python3 -m unittest tests.test_gen_state` in your worktree.
- **V4.** Spot-check at least 10 factual claims in the RUN_STATE top block against their cited primary files.
- **V5.** Rule MERGE, FIX-FIRST (with exact texts), or REFUSE.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root) or `/Users/edr/night-custody`.
- The discovery suite is not allowed, and neither are background tasks.
- Write only the ruling file.
- Do not read TASK_QUEUE.md's history, council logs or memory beyond what the checks need.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
b804919ac5ccbe92a447f5867ac9d7f5d834c46b87e6d47b9a2a8b6da8496456  ex-22-fidelity-lens.md
```
