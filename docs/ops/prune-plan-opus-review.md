# Prune plan: cold review (Opus 5.5, cross-family)

**Reviewed:** `origin/ops/2026-11-08-prune-plan` at `7cce18c15` (Sol 6.1 build):
PRUNE-PLAN.md, PIN-INVENTORY.md, TAG-PINNING.md, the five TSVs, and the run report.
**Repository state checked against:** `origin/main` `c07b388e9`, the plan's snapshot
`4e7e878a1`, the GitHub server (rulesets, branch protection, open PRs, commit
lookups), and the Air's `jw-wt` clone layout. This was a read-only review. Nothing
was deleted, moved, tagged or pushed except this review branch. No restricted path,
`jw-b5-*`, `night-*` or custody directory was opened. One path below,
`/Users/edr/jw-b5-analysis`, is named only because it appears as text in
`objects/info/alternates` files under `jw-wt/`.

## Verdict: ADMIT_WITH_FIXES

The plan is careful and conservative where it counts. It keeps main's history,
uses no `filter-repo`, force-push to main, reflog expiry or aggressive GC, puts
tags and a bundle before deletion, uses `--force-with-lease` deletes, keeps every
unmerged branch on HOLD, and leaves disk deletion to Ed. I found no step that
would lose Block 5 release objects as written. Server-side, main is protected
(no force-push, no deletion), and every `MERGED-CANDIDATE` tip is an ancestor of
main, so the first branch batch cannot lose commits on GitHub.

The fixes below are required **before any execution step** (tag creation, any
branch deletion, any disk cleanup). The largest risks are in the disk checklists
and in parts of the procedure that exist only as prose, not in the Git retention
logic.

## Findings, ranked

### HIGH-1: The Air checklist ignores the alternates graph. Removing one stale-looking clone breaks dozens of others, including the B5 release-check worktrees and the qwen4_exp port lanes.

What I found: most directories under `jw-wt/` are standalone clones that borrow
objects through `objects/info/alternates`, not worktrees. Some borrow in chains:

- `jw-wt/council-pr` (last commit 2026-11-06; looks stale) owns the objects that
  `handoff`, `align-v4-assembly`, `ci-rootcause-b6` and `cloud-fixgold` borrow.
- `handoff` is the main repository for the `b5-r3-run`, `b5-r4-run`,
  `b5-release-check`, `b5-lean*` and other worktrees. About 70 `sol-*` clones
  borrow from `handoff`, which borrows from `council-pr`.
- `/Users/edr/jw-b5-analysis/.git/objects` is the alternate store for about 15
  clones: `opus-port-evals`, `opus-port-perf`, `opus-port-upstream`,
  `opus-flashnext-twin`, `sol-flashnext-engine`, `sol-flashnext-port`,
  `sol-release-ready`, `sol-v4-plan`, `sol-v4-wp5`, `cmp-dryij`, `council-align9`,
  and others.

The plan says only that tags in an alternate-backed clone do not stop GC in the
shared store. It does not map the graph or name `council-pr` or the B5 analysis
checkout as stores other clones depend on.

Failure scenario: after release, Ed or an agent removes `jw-wt/council-pr` as an
old council PR clone, or archives and removes the B5 analysis checkout once the
receipt is accepted. The Air checklist treats both as normal retirement steps.
Every dependent clone then reports "unable to read object". That includes the
`b5-release-check` and `b5-r4-run` worktrees used to re-verify the release, and
the qwen4_exp port clones (a standing major goal). `sol/u90-item3` and
`sol/u90-item5` hold one unpushed commit each, which would be lost outright.
Running `git gc` or `git fetch` (which can trigger auto-gc) inside an owner store
after its branches are deleted causes the same failure, more slowly.

Fix: add a precondition to the Air checklist. Enumerate every `objects/info/alternates`
under `jw-wt/` and `$HOME`. For each clone that will survive, either dissociate
it (`git repack -a -d`, then remove the alternates file) or delete it first.
Until that is done, set `gc.auto=0` in every owner store. List each owner store
as KEEP. Before removing any clone, also check for unpushed commits with
`git rev-list --branches --not --remotes`.

### HIGH-2: Deleting the "local copy" inside a sync folder deletes the cloud copy too (iCloud Drive, Dropbox).

The MBP rule ("external SSD plus server-confirmed iCloud") and the Air jwgold
rule ("copied to Dropbox and verified") both end with "Ed deletes only the
redundant local copy". The plan never says that the local copy must sit
**outside** the synced tree. If the archive lives in iCloud Drive (including
Desktop and Documents sync) or in the Dropbox folder, deleting it locally
propagates. It deletes the cloud copy, leaving only the 30-day "Recently
Deleted" or "Deleted files" window.

Failure scenario: the jwgold run directory sits under `~/Dropbox/...`. Ed deletes
it to free space, and the Dropbox copy that was "verified" goes with it. The same
happens for an MBP archive kept under iCloud-synced Documents.

Fix: before any deletion, require a recorded statement of the exact local path
and proof that it is not inside a synced root. Verify the cloud copy from a
**different** device or session: evict, re-download, then compare checksums
against the manifest. Treat sync services as a copy only when the deleted path
is outside them.

### HIGH-3: The borrowed SSD is counted as an "independent second copy".

The MBP checklist calls the external SSD "an independent second copy". Per
Ed's brief and the lead's records, the SN7100 is **borrowed** and attached by
day only. The `align/2026-11-08-ssd-permanent-*` branches are still drafts.

Failure scenario: Ed deletes MBP local archives after verifying SSD and iCloud.
The SSD then goes back to its owner, or is reformatted for the Flash-Next live
tests, and the only remaining copy is iCloud. That violates the two-copy rule
the plan itself cites, and it is invisible later because the verification
record says "two copies verified".

Fix: the SSD counts as a retention copy only after Ed records that it is owned
or permanently assigned, and that it is not used as Flash-Next or scratch
space. Otherwise the second copy must be the Air (once it is dissociated and
has disk), Dropbox (see HIGH-2) or a purchased drive.

### HIGH-4: Tags are never pushed or protected, and the server has no tag rules today.

Step 1 creates about 204 annotated tags **locally only**. No command pushes them,
and no command checks them with `git ls-remote --tags origin` against the TSV.
"Server rules should forbid tag update/deletion" is prose, and
`GET /repos/mpmdw/JouleWise/rulesets` returns `[]` right now. The existing
release identities (`b5/analysis-r3`, `b5/analysis-r4`, `b5/collection`,
`b6/collection`, `bytes/collection-n*`) can therefore be moved or deleted by
anyone with push access, including the allow-listed agent `gh` and `git push`
operations.

Failure scenario: a later agent mistakes `pin/*` tags for clutter and runs
`git push origin :refs/tags/...`, or retags `b5/analysis-r4` while "fixing" a
tag conflict. `release_b5.py --pinned-commit` still works, because it uses the
SHA. But retention of off-main pins then depends only on HOLD branches staying
undeleted, and the "tags replace branches" premise fails silently.

Fix: add explicit step 1b, run before any remote branch deletion and gated by Ed:
1. Create a GitHub tag ruleset on `refs/tags/**` that blocks update and deletion
   and restricts creation to admins.
2. `git push origin <explicit tag list>`.
3. Run `git ls-remote --tags origin`, peel each tag (`^{}`), and require it to
   equal the TSV commit for every row.
4. Record the ruleset JSON.

### HIGH-5: A merged-candidate branch is consumed by name, and deleting it silently weakens a B5 equivalence test.

`tests/b5_analysis/test_result_equivalence.py:1054` sets
`R1_FIX_BRANCH = 'origin/lane/b5-r1-9b-fix'`. Lines 1020–1022 run their
assertion only `if backport is not None`. `lane/b5-r1-9b-fix` is
`MERGED-CANDIDATE` in BRANCH-TRIAGE.tsv.

Failure scenario: batch 1 deletes the branch. In fresh clones the test then
skips the D-189 reference check and still passes. The equivalence guard gets
weaker with no visible failure. The same commit (`e7eb872d`) is already tagged
`b5/analysis-r1-9bfix-ref`.

Fix: before batch 1, change the constant to `b5/analysis-r1-9bfix-ref^{commit}`
and make a missing ref a hard failure. More generally, the "no-live-ref-name"
check should be a script, not an owner review. Run
`git grep -F -f <candidate-names>` over `joulewise scripts tools tests configs .github`
on main **and on every HOLD lane tip**. That scan finds 21 candidate names
referenced in code, config or registrations on main alone (`envelope-gate`,
`lane/2026-10-14-independent-recompute`, `lane/2026-10-07-seal-landing`, and
others). Most are narrative, but each one needs a disposition.

### HIGH-6: The census tooling is not committed, so the required release-day refresh cannot be reproduced.

The TSVs were generated by `/private/tmp/jw-prune-inventory.py` and checked by
`/private/tmp/jw-prune-verify.py`. Neither is committed. The plan's own Air
checklist proposes cleaning `/private/tmp`, and a reboot clears it too. Every
entry condition depends on refreshing the inventory against release-day main.
Main has already moved (`4e7e878a1` → `c07b388e9`, plus 18 new and 4 moved
branches).

Fix: commit both scripts under `scripts/ops/`, with the census scope fixes from
MED-1, and make the refresh one command whose output diff is reviewed.

### MED-1: Pin inventory scope gaps (the main answer to review question 1)

The census scanned the text of main's `joulewise/ scripts/ tests/ configs/`, 11
named documents, and two branches (`bytes-pass2-open`, `align-pilot10-benign`).
It did not scan:

- **`docs/**` beyond the named list.** 38 commits cited there are off-main and
  not covered by any proposed tag. They include two B5 seal-provenance commits:
  - `8ce450ad55`, the corpus-18 erratum TEXT-GATE, which lives only on `seal/2026-10-09-corpus18-text`.
  - `9271df94f0`, the CI run at the H_claim tree, in `00-seal-and-arm-record.md`, which lives only on `lane/2026-10-07-ci-lock-inode-candidate`.
- **Live HOLD lanes.** Commit citations not in the manifest:
  - ALIGN v4 R1 / R11 lanes: 11, including the R0 NLL reference config pin
    `62bc719f7` (`configs/align/v4/r0_nll_reference.json`, branch
    `lane/2026-11-06-r0-d-nll-diagnosis`).
  - qwen4_exp canonical and MBP-live lanes: 7, including the Sol port
    `28d153449` and the twin `ad56248a5`.
  - BYTES stage-1 (#701): 11.
  - #704 comparator lane: 3.
  - `research/2026-11-07-audit-burn`: 24.
- **`tools/`.** This is where the B5 comparator `tools/b5_equivalence/compare_b5_results.py`
  lives. It has no hex literals today, but it sits on the release path and the
  census cannot see it.
- **Release-receipt identities other than `analysis_commit`.** The B5 release
  runbook (`lane/2026-11-05-b5-release-runbook`) records:
  - the equivalence oracle commit;
  - an **independent comparator checkout commit**;
  - the recompute checkout;
  - `release_checkout.commit` from `release_b5.py`.

  The plan adds only `pin/b5-release-<id>` at the analysis commit. If the
  release runs with the #704 comparator before it merges (`bea480f29`, off
  main), that commit sits only on a HOLD branch with no tag.
- **Server-only objects.** The census used only locally recorded remote refs.
  `498ad1d0`, listed as one of the five "unavailable" commits, resolves on
  GitHub (`498ad1d0c0f9…`, "QUIET-PREDICATE-EVIDENCE-01 harness"), probably
  through `refs/pull/*/head` (655 PR heads on the server). The other four are
  not on GitHub. `4cb222a19`, the B5 final ledger head, exists only on the
  measurement side.
- **Undercounted ancestry and history consumers.** The inventory lists three
  sites. Main also has:
  - `paper_custody.py:565` and `paper_reported_energy.py:236–242`, which walk
    history with `git log -S` and `git show HEAD:<spec>`;
  - `evidence_night.py:517`, `refresh_receipt_histsem_pinset.py:212–220`,
    `build_v4_histsem_pinset.py:253`, `harvest_window.py:335`,
    `flags/collect.py:643`, `digest_pin_census.py:404`, `arm_readiness.py:4258`.

  None breaks while main's history is kept. File-prune PRs must still check
  their `HEAD:<path>` reads (the paper verifiers matter for the capstone paper).

None of these is lost today, because every affected branch is HOLD. They matter
when HOLD branches are later "owner-dispositioned" against a manifest that does
not list them. Fix: extend the scan to all tracked text on main plus every HOLD
lane tip. Add the release-receipt identity set (analysis, oracle, comparator,
recompute, release checkout) as required inputs to step 1. Fetch
`refs/pull/*/head` before declaring a commit unavailable.

### MED-2: The archive tag is pinned to the stale snapshot in the executable TSV.

The prose says the archive tag must target **release-day main** and must never
move. But `TAGS-TO-CREATE.tsv` row 1 has
`archive/process-traces-before-release-prune-2026-11-08 → 4e7e878a1`, and the
step-1 script creates tags straight from the TSV. Run as written, it would
permanently freeze the archive at the snapshot. Commits merged later would then
fail step 2's ancestry check, or the operator would be tempted to move the tag.
Fix: have the script take `ARCHIVE_COMMIT` (required to equal
`git rev-parse origin/main` after a fresh fetch) and refuse if the TSV row
differs. Better still, name the tag by release date at creation time.

### MED-3: TAG-PINNING keeps identity strength but loses the "reviewed and CI-gated" property that ancestor-of-main gave.

On identity, the design is sound. The registration's full SHA (and tree) is the
authority, a moved tag is caught by SHA equality, and there is no fallback to
main. But ancestry from protected main also meant that the commit came through
a PR with the required checks. An annotated tag on an off-main commit carries no
such evidence. "Authenticated ruling entry" (validator rule 3) is not defined,
and signed tags are optional.

Failure scenario: a lane commit that never passed CI is tagged
`pin/b6-analysis-r1`, registered by SHA, and validates cleanly.

Fix: require the registration to record **review evidence** for the commit:
- a PR number, plus the required check-run conclusions for that exact SHA from
  `gh api .../commits/<sha>/check-runs`, archived in the receipt; or
- reachability from a protected `block/*` branch that has the same required
  checks.

Restrict `pin/**` tag creation to admins through the ruleset in HIGH-4. If
signing is used, define "authenticated" as `git verify-tag` against a committed
`allowed_signers` file. Also record the tag-object ID, not just the peeled
commit, so a deleted-and-recreated tag is detectable.

### MED-4: The model weights that live lanes depend on are not protected in the disk checklists.

The checklists never mention model caches (HF, MLX conversions). For a
disk-pressure cleanup these are the largest and most tempting targets. Live
pins name upstream revisions: for example, ALIGN v4 `Qwen/Qwen3.8-27B@8c0b3d30…`
in `r0_nll_reference.json`, the BYTES manifest, the B6 identity pins, and the
Flash-Next port weights. An uploader can delete or rewrite an upstream HF
revision, so re-downloading later may not reproduce the pinned identity.
Fix: add a KEEP list to each machine section. Generate it from the identity
pins of live registrations (repo, revision, local path and digest), plus the
Flash-Next and x86 working sets. Allow a cache to be removed only after its
digest-verified second copy is recorded.

### MED-5: The B5 final ledger head `4cb222a19` is MBP-only, and the MBP checklist does not name it.

The inventory correctly lists it as unavailable and on hold, but the MBP section
speaks only of "ledger roots". Fix: make recovery an entry gate. Push it from
the MBP ledger repo to a `records/b5-ledger-final` branch and tag, then verify
on the server, before any MBP cleanup of old checkouts.

### LOW-1: There is no explicit rollback record.

Fix: have step 2 append each deleted `(branch, sha)` pair to a committed ops log.
Restore is `git push origin <sha>:refs/heads/<branch>` from the bundle, tags or
`refs/pull`. State it.

### LOW-2: The step-2 freshness check relies on remote-tracking refs.

The check compares `refs/remotes/origin/<name>` against the snapshot. Add
`git fetch --prune origin` immediately before it. The lease already protects the
server side.

### LOW-3: `git worktree prune` can drop worktrees on removable volumes.

On the MBP, it drops metadata for worktrees on the SSD while the SSD is detached.
Use `git worktree lock` for SSD-hosted worktrees.

## Proportionality: what could be simpler

The retention machinery (1,131-row manifest, 173 `pin/*-cited-<hex>` tags, five
TSVs, about 4,400 lines) is heavier than the risk it addresses. It still misses
whole tips of unmerged branches, which the plan admits. A leaner design that is
also **stronger**:

1. Add one GitHub ruleset that protects `refs/tags/**` (HIGH-4). Main is
   already protected.
2. Tag only the named scientific anchors, about 30. **Reuse** the existing
   `b5/analysis-r*`, `b5/collection`, `b6/collection` and `bytes/collection-n*`
   tags instead of adding duplicate `pin/b5-analysis-r3`-style names. Two names
   for one identity invite drift, and the release runbook cites the `b5/*` names.
3. Back up with `git clone --mirror` from GitHub (no alternates, includes
   `refs/pull/*`), then `git bundle create --all`. Keep two copies (see HIGH-3).
   This replaces the tags-only bundle and covers HOLD branches too.
4. Batch 1 deletes merged branches only. This is safe by construction (tip
   ancestor of protected main, lease delete), after the name-consumer scan.
5. For later unmerged-branch retirements, tag the whole tip as
   `archive/branch/<name>` at deletion time. This needs no per-citation tags and
   preserves all of the work, not just the cited commits.

The per-citation census then becomes a **check** (every cited commit is reachable
from some protected ref) rather than a tag factory.

Keep the blinding rules and the prereg fidelity exactly as they are. The rest
(manual owner reviews per branch, the separate dry-run block) can collapse into
the scripted checks above.

## Disposition summary

| # | Severity | Fix needed before |
|---|---|---|
| HIGH-1 alternates graph | HIGH | any Air or MBP clone or checkout removal |
| HIGH-2 sync-folder deletion | HIGH | any local data deletion |
| HIGH-3 borrowed SSD | HIGH | any MBP archive deletion |
| HIGH-4 tag push and protection | HIGH | any remote branch deletion |
| HIGH-5 `R1_FIX_BRANCH` and name consumers | HIGH | branch batch 1 |
| HIGH-6 census scripts uncommitted | HIGH | release-day refresh |
| MED-1 census scope | MED | any HOLD-branch disposition; release pin set |
| MED-2 archive tag target | MED | step 1 |
| MED-3 review evidence in TAG-PINNING | MED | first tag-pinned registration |
| MED-4 model-weight KEEP list | MED | disk cleanup |
| MED-5 `4cb222a19` recovery | MED | MBP cleanup |
| LOW-1..3 | LOW | opportunistic |
