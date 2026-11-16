# PR #804: iCloud span offload

Owner direction (2026-11-15 17:46 PST): "use icloud, no? why would you not use icloud".
Authority: RL-173 A at `f35483d41`, RUN_STATE items 347 and 350 on origin/main, and the
builder request for this branch. This is software work with synthetic bytes only. No MBP contact,
real iCloud operation, custody or energy file access, measurement, or merge occurred.

## Change

The default backend is iCloud Drive, using the existing macOS sign-in. Artifacts are atomically
renamed into the item-350 destination. A positive CloudDocs status is followed by observed
SF_DATALESS eviction, download, and sha256/size readback for every artifact. Confirmations record
`icloud evict+redownload sha256 match` and upload/eviction/verification times. Failed/unobserved
readback produces only `.ok.unconfirmed`; upload/status timeout or wrong bytes produces no marker.
The optional tested rclone backend remains. The byte-only archive, encryption configuration,
control-file guards, plan lock, original retention and no-clobber marker are preserved.

Runbook installation now needs no rclone or new credential, includes bird/cloudd/fileproviderd
on the maintenance line, and retains PROVISIONAL macOS 26 qualification and the research-lead
question: is iCloud with evict+redownload readback the permanent tool under A.3?

## Workspace incident

Initial Git access failed because this worktree's .git pointed under the OS-denied air-home root.
No protected root was accessed or its permissions changed. An accessible repository replica supplied
independent metadata at `/Volumes/JW-EXT/scratch/sol-offload-icloud/git-metadata/.git`; the original
pointer is saved as `original-worktree-git.txt` in that scratch directory. Before editing, this
worktree was verified clean at b9d688207 using the independent index. Its .git now points to that
metadata. Source changes stay in the requested worktree/branch.

## Verification and dispositions

- Baseline: 89 focused tests passed (58 offload + docs freshness).
- Current focused suite: 98 tests passed (67 offload + docs freshness); synthetic fake brctl on PATH,
  real LibreSSL. Tests cover pending/unknown statuses, subprocess and poll deadlines, failed/no-op
  eviction, failed download, unavailable flag observation, hash mismatch, partial confirmation,
  immutable retry, atomic copy cleanup, link/hardlink/FIFO/ancestor/repository guards and Air pull.
- The existing head's CI failed the Git-fixture maintenance guard: six direct git-init sites in this
  PR's original tests. All existing and new fixture initializations now use `init_git_fixture`;
  the six-test maintenance module passes.
- Final pre-seat focused run: 104 tests passed (offload, docs freshness, Git fixture maintenance).
- Quick tier: 282 modules, 20 module failures in 148.334 s; this OS-blinded seat denies every
  `/restricted/` path, including those in synthetic fixtures (PermissionError / tooling_refusal).
  Log: `/Volumes/JW-EXT/scratch/sol-offload-icloud/quick.log`. This is not claimed green.
  Some legacy modules also attempt OS-denied canonical custody paths; none was opened.
  The final-head PR gate ledger records GitHub CI evidence when complete. Full suite belongs in GitHub Actions on this analysis Mac per
  CANONICAL; no sequential discover run is used. The CI workflow runs the sharded canonical suite.
- Cold executing Sol seat: **ADMIT at da02b7fde**, 104 focused tests and 21 independent probes
  passed; zero BLOCKING, one SHOULD-FIX, two NOTEs. Immutable report:
  `docs/run_reports/2026-11-15-span-offload-icloud-sol.md`. The retry SHOULD-FIX is repaired:
  an existing unconfirmed iCloud record now remains exit 8, unchanged, instead of exit 3.
  A new actual-CLI regression covers this; the repaired focused run passed 105 tests.
  **Delta ADMIT at 27e4070c4:** 105 focused tests and 26 independent probes passed; no new
  software findings. Report: `docs/run_reports/2026-11-15-span-offload-icloud-sol-delta.md`.
  The subsequent archive commit changes records only; the lead verifies software/runbook identity
  to this admitted head. Final CI evidence is in the PR gate ledger.
- The exact requested `sol_seat.sh` launcher was run; nested `sandbox-exec` failed before Sol started
  (`sandbox_apply: Operation not permitted`). A fresh `gpt-6.1-sol`, xhigh, no-history agent inherited
  the existing OS blinding and executed the cold review. No sandbox was removed or bypassed.
  One failed wrapper launch and two executing review invocations used one cold seat.
  Per-invocation receipts/dispositions:
  `docs/process_traces/2026-11-15-span-offload-icloud/review-invocations.jsonl`; archived brief beside it.
  Review evidence is synthetic, not live qualification. No number-bearing defect has been claimed
  or fixed by these checks.

## Handoff

Lead: after admission/green CI and an eventual separately authorized merge, follow
`docs/ops/SPAN-OFFLOAD.md` Install, including the production-key synthetic MBP-to-iCloud-to-Air
round trip between spans. Keep all operational gates closed on exit 5 or 8. Ask the research lead
the A.3 permanence question; retain the daemon maintenance line meanwhile. Interim offload.key's
second-copy duty from RL-173 A.1 remains external and was not inspected here.
