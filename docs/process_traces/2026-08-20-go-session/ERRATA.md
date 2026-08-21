# Errata — 2026-08-20 go-session custody

Corrections to custodied verbatim reports. The originals are records of what
the tool emitted and are not edited; this file is the correction channel.

## E-1: `rh-impl-report.md` workspace branch field is wrong

`rh-impl-report.md:14` records `"branch": "impl/d144-followups-prewindow"`
with `head_start = head_end = 42bd318`. The RECEIPT-HISTSEM-01 implementation
that report describes lives on branch **`impl/receipt-histsem` @ `60ba2e9`**
(pushed, labelled do-not-merge). The report's pathspec and verification
records are internally consistent; only the branch metadata is stale (the
session inherited the field from the prior lane). Anyone harvesting by branch
name must use `impl/receipt-histsem`.

Filed 2026-08-20 by the T19 successor session (lead), caught by the T18/T19
run-report drafter's evidence pass; verified against the custodied file
before filing.

## E-2: aedf530 commit message — UTC mislabeled as PDT and a false bisect

Commit aedf530's message states the calexits 3.11 shard was "red on every
main run since 2026-08-20 13:22 PDT" and that the breaking window contained
"no code change." Corrections of record: (a) 13:22 is UTC (06:22 PDT) — the
cold-gate packet propagated GitHub's UTC timestamps under a PDT label;
(b) the "no code change in the breaking window" bisect framing is FALSE as
an exoneration — the identical failure signature had already occurred on
main at 2026-08-19T23:08Z, before the two green runs; the defect is an
intermittent that happened to pass twice, not a clean environment break.
The fix itself stands on the terra root-cause session's local 3.11
reproduction, which does not depend on the bisect. Caught by the Opus
contract-lens refuter (cold-pair session, 2026-08-20 night).

## E-3: deviation note — PRs #163/#164/#165 merged over a red required check

The standing registered rule TASK_QUEUE.md:288-295 ("shard-4 CI failures in
this module are re-run-once-then-investigate, never waved through silently",
registered 2026-08-11) was BREACHED at the merges of #163, #164, and #165:
calibration-exits-exclusive (3.11) was red on each PR's checks (on #164 the
3.14 variant was also red), and no re-run, investigation, or disposition was
recorded at merge time. Compensating evidence: each merged behind a green
full local canonical at its own head (the recorded operative gate). No
rollback or re-verification is ordered (cold-pair ruling + synthesis,
2026-08-20 night). Corrective convention, binding: ANY merge over ANY red
required check requires an explicit recorded disposition at merge time.

## E-4: aedf530 landed direct-to-main without independent pre-landing review

The calexits assertion-widening (a claim-bearing witness test) followed the
46d710f direct-to-main precedent but exceeded it: no independent refuter
before landing. Compensating evidence, recorded: the terra root-cause
session's local 3.11 reproduction and discriminating-power demonstration,
plus the Opus refuter's post-hoc executed probes (the widened assertion
opens no RACE_EXERCISED escape hatch; the ENOENT causal account matches the
3.11-only failure). A light independent retro-review rides the
CALEXITS-CLEANUP-RACE-CI311 row's closure.

## E-5: a 39MB local custody tarball transited git history (6649736..1d6824c)

The consistency-sweep commit 6649736 used `git add -A` and swept in
`.decisive-replay/d117_v2_production_custody_store.tar.zst` (39MB, local
decisive-replay custody, deliberately untracked all session). Corrected
one commit later (1d6824c: removed from the tree, path gitignored). The
blob remains reachable in pushed history; expunging it requires a history
rewrite, which is an irreversible action reserved to Ed (decide whether
repo-size hygiene warrants it; no secret material is involved — the
tarball is measurement custody whose ruled home is outside the repo).
Root cause: `git add -A` in a bookkeeping commit; corrective convention:
bookkeeping commits stage by explicit pathspec, never -A.
