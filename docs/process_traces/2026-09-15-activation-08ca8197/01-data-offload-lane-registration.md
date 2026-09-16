# 01 — Registration of DATA-OFFLOAD-ICLOUD-01 (2026-09-15 ~22:20 PDT, activation `08ca8197`)

## Source

At ~22:15 PDT the interactive session `b0ae8462` (Ed at the machine, remote
control) relayed over the cross-session channel an instruction from Ed, quoted
by that session as verbatim:

> "Also, keep in mind: consistently offload as much local data onto iCloud as
> possible."

The relay asked this activation to register it as a standing P2 lane,
bookkeeping only, with the shape recorded in the kernel row: at every
session-end bookkeeping, move CLOSED archives (`~/night-archive/*`, retired
measurement bundles whose custody digests are already recorded, old
codex-run-v3 scope data) into iCloud Drive, leave a local pointer plus a
SHA-256 manifest, verify the copy's digests before deleting any local
original, and never place live worktrees, the canonical repository,
`~/night-custody`, or active measurement roots under iCloud sync.

This is not a directive issue (`gh issue list --label directive` was empty at
22:14 and again before this slice). It is recorded here as relayed; the row's
first irreversible step (deleting local originals after a verified copy)
therefore waits for Ed's YES on the manifest, after which the lane is standing.

## What was registered

Kernel row `DATA-OFFLOAD-ICLOUD-01`, rank 209, `p2_next_slice`, lane `agent`,
status `queued`. Kernel 182 → 183 rows; `TASK_QUEUE.md` regenerated;
`tests/test_gen_state.py` expected-id set and count updated. Nothing was
copied, moved or deleted. No process beyond the generator and its unit test
was launched (Ed's prudence instruction stands; load about 3 at the time).

## Candidate archives seen by this activation (not measured for size)

- `~/night-archive/` — retired plan roots and `magistrate-tmp-20260915`
  (the `/tmp/magistrate-*` rsync the interactive session made before the
  restart, about 696 MB per its checkpoint).
- `$TMPDIR/codex-run-v3-scope*` — 3 directories at 20:12 PDT.
- Retired measurement bundles: to be enumerated by the lane against the
  custody digests recorded in the repository before anything moves.

## Never-sync list (fence for the lane)

Live worktrees under `/Users/edr/code`, the canonical repository
`/Users/edr/code/JouleWise`, `/Users/edr/night-custody`, every active or
plan-pinned measurement root (`/Users/edr/JouleWise-measurement-*`), and any
path a night plan names. The iCloud sync client adds file-system churn, which
is the class of load the restart was about; nothing that a window reads or
writes may be under it.
