# Post-Block-5 prune: execution plan

**Authority.** Ed approved the post-release prune ("sounds good on all 3", RUN_STATE 231). The procedure is
[PRUNE-PLAN](PRUNE-PLAN.md) with the fixes from the Opus cold review
(`origin/ops/2026-11-08-prune-plan-opus-review:docs/ops/prune-plan-opus-review.md`), as applied by Sol on
`ops/2026-11-08-prune-fixes` @ `526d11168`. Lead rulings R17 to R19 and the W1 integration list in item 228 apply.
Every branch named in item 228 is unmerged, so it is HOLD by construction. This document puts the steps in order.
**Nothing irreversible happens before a verified backup exists in two places.**

Prepared 2026-11-08 on the Air (Opus 5.5). Steps a and b are partly done; the status of each is given below. Nothing
destructive has run: no branch, tag, clone, worktree or file was deleted.

## 0. Status at a glance

| Step | What | Status | Who | Reversible |
|---|---|---|---|---|
| a1 | Fresh GitHub mirror, PR heads, Air-only refs, `bundle --all`, isolated restore test | **DONE** on the Air | lead (this run) | additive |
| a2 | Off-machine copy (Dropbox) and a check from a different session | **PENDING**: the auto-mode classifier refused the upload | lead, after Ed allows it | additive |
| b | 34 named anchors, plus 2 recovered-object tags, pushed and checked with ls-remote | **DONE** | lead (this run) | yes until c; after c only an admin can undo |
| c | GitHub tag ruleset | **PENDING** | lead runs the `gh` call (Ed approved) | admin can disable it |
| d | Delete merged branches only, in 7 gated batches | **PENDING**; needs a2 and c first | lead | yes: restore from bundle, tag or PR ref |
| e | Air disk cleanup (5.1 GiB of proven-safe items) | **PENDING**; needs a2 | lead or Ed | yes: re-clone or `worktree add` |
| f | MBP checklist | **PENDING**; magistrate only, after R1 closes | magistrate | per item |

## 1. Delta check against the Opus review

| Finding | Verdict | Evidence |
|---|---|---|
| HIGH-1 alternates | **FIXED in the plan; the graph is re-measured here.** The plan has the owner/borrower checklist, `gc.auto=0`, repack without `--local`, and an isolated fsck. Measured today (metadata only, [AIR-ALTERNATES-GRAPH](execution-2026-11-08/AIR-ALTERNATES-GRAPH.tsv)): `handoff` **is self-contained** (it has no alternates file). It owns 21 clones and 31 worktrees. `council-pr` still owns 3 clones (`align-v4-assembly`, `ci-rootcause-b6`, `cloud-fixgold`). `/Users/edr/jw-b5-analysis` owns **9 visible** borrowers: 8 under `jw-wt/` (`cmp-dryij`, `council-align9`, `opus-flashnext-twin`, `opus-port-{evals,perf,upstream}`, `sol-v4-plan`, `sol-v4-wp5`) and `/private/tmp/jw-b5-postrelease-20261105.git`. The "about 14" figure may include roots that cannot be inspected; treat it as a lower bound and never delete or GC that store. Two `/private/tmp` clones already point at missing stores (`jw-wt/sol-w1bm-sol1`, `jw-wt/sol-optin-audit`), so they are broken now. **Done in this run:** `gc.auto=0` and `gc.autoDetach=false` are set in `handoff` and `council-pr`. Every local branch, HEAD and stash in all 37 Air clones was checked against the fresh mirror. The 5 Air-only commits are now kept in the backup under `refs/air-local/*` ([list](execution-2026-11-08/AIR-ONLY-REFS-IN-BACKUP.tsv)). |
| HIGH-2 sync folders | **FIXED.** The plan requires the exact path, proof that it is outside every synced tree, and a check from another device. Measured: Dropbox is `~/Library/CloudStorage/Dropbox` (`~/Dropbox` is a symlink to it). iCloud Desktop/Documents sync is **off** (`FXICloudDriveDesktop=0`). `~/code` is not synced. Time Machine has no destination. The Air backup lives at `/Users/edr/code/CapstoneProject/jw-archive/git-backup-2026-11-08/`, outside every synced tree. |
| HIGH-3 borrowed SSD | **FIXED.** The plan says the SSD never counts. This plan does not use it either (see a2 and f). |
| HIGH-4 tags pushed and verified | **FIXED and EXECUTED.** All 36 tags were pushed by explicit refspec. Each tag object and peeled commit was compared through `git ls-remote` ([proof](execution-2026-11-08/TAG-LS-REMOTE-PROOF.tsv): 36/36 OK). The ruleset (step c) is still pending. Rulesets returned `[]` today. |
| HIGH-5 branch read by name | **FIXED on the branch, not yet on main.** `dcaf2ca2c` changes the test to read `b5/analysis-r1-9bfix-ref^{commit}` and fail hard if the tag is missing. Main still reads `origin/lane/b5-r1-9b-fix` (3 hits in the fresh scan), so that branch is refused by the batch gate (name-consumer-hit) until the fix merges. |
| HIGH-6 census scripts | **FIXED.** Four scripts are committed under `scripts/ops/`, with synthetic tests. This run adds `prune_batch_gate.py` and fixes a design bug: the verifier required the archive tag to *equal* current main, which can never hold once main moves past an immutable tag. It now requires *ancestry* (there is a regression test). It also adds a stable census clone, because live `handoff` refs moved in the middle of a run twice today (see §2). |
| MED-1 missed pins | **FIXED.** Scope is now main plus every HOLD tip. The six highlighted objects are resolved and present in the bundle. `pin/b5-corpus18-text-gate` and `pin/b5-hclaim-ci` are anchors. `498ad1d0` **was** on GitHub, but only as an unreferenced object that GitHub GC could drop. It is now fetched by SHA and tagged `archive/recovered/498ad1d0-qpe01-harness`. The fresh census found one more UNRETAINED commit, `e55ac391a` (a scratch merge that lived only in the Air `handoff` store). It is now tagged `archive/recovered/e55ac391a-cw-impl-scratch-merge`. Two citations that exist only in PR heads (`36dcdd76f` in #206, `7d586a691` in #186) are PR-BUNDLE-ONLY, retained by `refs/pull`. Still open: `050aaad13` exists **only** in the `jw-b5-analysis` object store, which 8 Air borrowers can see. It was deliberately not copied and not pushed (see §6). `6bcd90a3` and `9a6f8880` are on neither GitHub nor any Air clone; they need an owner disposition. |
| MED-2 stale archive TSV | **FIXED.** The archive tag was created at release-day main `901d7580d` (RUN_STATE 231), and the verifier refuses any row that differs. |
| MED-3 per-tag PR and checks | **FIXED and EXECUTED.** [TAG-REVIEW-EVIDENCE](TAG-REVIEW-EVIDENCE.tsv) now holds the real tag-object IDs, trees, PRs and the 18 required checks of main protection at the exact SHA. Raw JSON is in the backup's `evidence/`. Only `b5/analysis-r1` has all 18 checks passing at its SHA. Every other anchor is `*_HISTORICAL_ONLY`: it keeps its identity, but **cannot authorize a new tag-pinned run** (TAG-PINNING rule). Note for the lead: `pin/b5-release-checkout` = `02ef89f5c` (the #704 merge on main, where the release check ran) has `quick=failure` and `test (3.13, 2)=failure` on its push CI at that exact SHA. |
| MED-4 model weights | **FIXED in the plan.** It has a KEEP inventory gate. Measured: the Air has no model caches beyond `~/.cache/huggingface` (84 KB, faster-whisper only). The weights are on the MBP or SSD, so §f applies. |
| MED-5 ledger `4cb222a19` | **OPEN, magistrate step** (§f1). Confirmed absent from GitHub (API 422) and from every Air clone. |
| LOW-1 rollback log | **FIXED.** [PRUNE-ROLLBACK.tsv](PRUNE-ROLLBACK.tsv) gets an INTENT row (committed and pushed) before each batch and an outcome row after it (§d). |
| LOW-2 fetch first | **FIXED.** Every batch begins with `fetch --prune` and a fresh census in the stable clone. |
| LOW-3 removable volumes | **FIXED in the plan.** §f4. |

**Delta verdict: every HIGH and MED finding is fixed, except two that are open by design.** MED-5 (`4cb222a19`) is a
magistrate step. The off-machine half of the two-copy rule (a2) still has to be performed. Neither blocks the
additive steps already done. Both block step d.

## 2. Census dry run on the Air (read-only), with outputs

A stable census clone, `/Users/edr/code/CapstoneProject/jw-wt/prune-census`, was cloned from the fresh mirror. It has
`gc.auto=0`, origin set to GitHub, and all remote branches, tags and PR heads (`refs/remotes/pull/*/head`, 656 PRs).
Other agents fetch into `handoff` and move its tracking refs. That broke two runs today, with `stale census scope:
refs/remotes/origin/main`. The census clone moves only when the operator fetches into it.

```
python3.13 -B scripts/ops/prune_refresh.py --repo /Users/edr/code/CapstoneProject/jw-wt/prune-census \
  --output <scratch>/census-20261108b --archive-commit 901d7580def7862127ad2f4acb33011286d7e688 --archive-date 2026-11-08
name scan: 12112 source blobs; 209 positives
PASS snapshot topology: 9150 anchor/main ancestors; 1603 HOLD-only pins
Branch-name hits require dispositions: True        (exit 0; wall 2 min 22 s)
```

- Census main is `d2e7e8a39`; it covers 907 scope tips and 25,891 unique blobs.
- Pin coverage: 4,395 MAIN, 778 TAG, 1,601 HOLD-BUNDLE-ONLY, 2 PR-BUNDLE-ONLY, **0 UNRETAINED**. 19,176 unresolved text
  strings remain review aids only.
- Triage: **681 MERGED-CANDIDATE**, 908 HOLD.
- Name consumers: 18,938 hit rows across 40 candidate names. 66 of the rows are on main, across 26 names (`envelope-gate`
  ×11, `integrate/2026-10-07-int5` ×6, `lane/b5-r1-9b-fix` ×3, …).
- The refreshed tables are committed in `docs/ops/` and replace the `c07b388e9` snapshot.

Batch gate, `scripts/ops/prune_batch_gate.py`, run over all 681 candidates:

```
approved=640 refused=41
  40 name-consumer-hit
   2 open-pr-head-or-base   (lane/2026-10-07-l9-analysis = base of #566; lane/2026-11-05-align-window-council = base of #679)
```

Outputs: [BATCH1-APPROVED.tsv](execution-2026-11-08/BATCH1-APPROVED.tsv) (640 branch and tip pairs) and
[BATCH1-REFUSED.tsv](execution-2026-11-08/BATCH1-REFUSED.tsv). Every approved tip is an ancestor of protected main and
of the archive tag. Deleting them therefore loses **zero commits** on GitHub. The 41 refused names stay until an
owner records a disposition and a later gate passes.

## a. Backup: mirror and `bundle --all`, two places

**a1, done (the Air, outside any synced folder).** `/Users/edr/code/CapstoneProject/jw-archive/git-backup-2026-11-08/`
(919 MB) contains:

| Item | Content |
|---|---|
| `JouleWise.git` | Fresh `git clone --mirror` from GitHub, with `gc.auto=0`, no alternates and not shallow. It holds 1,584 heads, 743 `refs/pull` refs, every tag, and `refs/air-local/*` (5 Air-only commits). `fsck --full` is clean. |
| `JouleWise-all-20261108.bundle` | **The final bundle.** 317,201,502 bytes, sha256 `f6f566e6e461f7be0c3506f6022ede456ec4d9cac1ffb5651896bb154d16b96d`. 2,370 refs, including all 36 tags; 0 prerequisites. |
| `JouleWise-all-pretag-20261108.bundle` | Pre-tag bundle, taken before step b. 317,332,281 bytes, sha256 `fec4d13e846a08071caa24ec78b66fc65efb8d0b3ebcf74b0b9dfe9415aa4536`. |
| `refs-final.txt`, `refs-pretag.txt`, `SHA256SUMS`, `evidence/` | Ref lists, digests, and per-commit PR and check-run JSON. |

Restore test for each bundle: an isolated `git clone --mirror <bundle>` with no alternates, `fsck --full` clean, and
the ref list byte-identical to the bundle's heads. For the final bundle, every anchor's tag object and peeled commit
matched the server. The release identities (`02ef89f5c`, `bea480f29`, `ab1e0098d`) and `62bc719f7`, `28d153449`,
`ad56248a5`, `e55ac391a`, `d48ab1f77` are all present.

**a2, pending (off-machine).** The off-machine place that exists is **Dropbox**, in the folder
`/JouleWise-offload/` that the offload workflow already uses (`2026-11-03-synthetic`, `2026-11-06-air` and
`2026-11-07-air` are there). The Dropbox MCP connector can reach it to check from a different session. The borrowed
SSD does not count, nor does iCloud on the same Air account, nor GitHub (the thing being pruned). Commands
(the auto-mode classifier refused them in this run, so the lead or Ed has to allow them):

```sh
B=/Users/edr/code/CapstoneProject/jw-archive/git-backup-2026-11-08
D=/Users/edr/Library/CloudStorage/Dropbox/JouleWise-offload/2026-11-08-git-backup
mkdir -p "$D" && cp "$B/JouleWise-all-20261108.bundle" "$B/refs-final.txt" "$B/SHA256SUMS" "$D/"
cp -R "$B/evidence" "$D/evidence"
```

Check it from a different session, not from the local file. Wait until Dropbox shows the files as synced. Then get a
temporary download link for `/JouleWise-offload/2026-11-08-git-backup/JouleWise-all-20261108.bundle` (Dropbox MCP
`download_link`), download it to a fresh scratch directory, and require sha256 `f6f566e6…16b96d`. Then run
`git clone --mirror <download>` and `fsck --full`. Record the path, the Dropbox rev, the time and the verifier in the
rollback log header row. Ed can also check from his phone or the web. **Step d does not start until this is recorded.**
The Air copy never gets deleted as "redundant": it is the second copy.

## b. Tags (done): 34 named anchors plus 2 recovered objects

The 12 existing tags were reused unchanged: `b5/analysis`, `b5/analysis-r1`, `b5/analysis-r1-9bfix-ref`, `-r2`,
`-r3`, `-r4`, `b5/collection`, `b6/collection`, and `bytes/collection-n1` to `n4`. Their server tag objects equal the
pre-run listing.

**Created and pushed** (annotated, tagger mpmdw, explicit refspecs, no `--tags`): 22 manifest anchors and 2
recovered-object tags. Each message names its role and cites this plan.

```
archive/process-traces-before-release-prune-2026-11-08 -> 901d7580d  (release-day main, RUN_STATE 231)
pin/align-v4-measurement-snapshot 9c40e4e5d   pin/align-v4-r1-integration-snapshot e901eb2a4
pin/b5-accepted-analysis b13a510dc   pin/b5-harvest-1..4 7e6158d66 224a264c5 0699abbb0 b039c0257
pin/b5-seal1-claim a64000884   pin/b5-seal1-record ab7b21e57   pin/b5-seal2-record be6525e5a
pin/b5-corpus18-text-gate 8ce450ad5   pin/b5-hclaim-ci 9271df94f   pin/b5-release-checkout 02ef89f5c
pin/b6-registration 2a4e5149c   pin/b6-machine-test 6849cb7e3   pin/b6-acceptance 5ffbe15c4
pin/b6-kit 1c1bc3204   pin/b6-ledger-final 20c881075
pin/bytes-registration 7b622eb95   pin/bytes-pass2-lane ee4ce93fc   pin/bytes-ledger-final 1aca17e27
archive/recovered/498ad1d0-qpe01-harness 498ad1d0c   archive/recovered/e55ac391a-cw-impl-scratch-merge e55ac391a
```

ls-remote proof: [TAG-LS-REMOTE-PROOF.tsv](execution-2026-11-08/TAG-LS-REMOTE-PROOF.tsv). For all 36 tags, the
`refs/tags/<t>` value equals the local tag object, and `refs/tags/<t>^{}` equals the manifest commit.

- `pin/b5-release-checkout` comes from RUN_STATE 229/231: the check "ran on main `02ef89f5c`". `release_b5.py` runs
  the recompute and the comparator from that same checkout, so one tag covers three receipt roles. The lead should
  confirm `release_checkout.commit` in the structure-only `verdict.json`; this run did not open the custody directory.
- `analysis` = `b5/analysis-r4`. The oracle is `b5/analysis-r1` plus `b5/analysis-r1-9bfix-ref`.
- `pin/b5-ledger-final` is reserved for the magistrate (§f1).

**Rollback for b.** Before step c, `git push origin :refs/tags/<t>` removes a tag. After c, an admin must disable the
ruleset first, which is Ed's call. No scientific tag should ever be moved.

## c. Tag ruleset (Ed approved; the lead runs the call)

```sh
gh api --method POST repos/mpmdw/JouleWise/rulesets \
  --input docs/ops/execution-2026-11-08/tag-ruleset.json \
  > /Users/edr/code/CapstoneProject/jw-archive/git-backup-2026-11-08/evidence/ruleset-created.json
gh api repos/mpmdw/JouleWise/rulesets          # must list it with enforcement "active"
gh api repos/mpmdw/JouleWise/rulesets/<id>     # save it next to the evidence; check target, include patterns, rules, bypass_actors []
```

The payload, [tag-ruleset.json](execution-2026-11-08/tag-ruleset.json), has target `tag`, enforcement `active`, **no
bypass actors**, and the rules `deletion`, `update` and `non_fast_forward`. It covers `refs/tags/b5/**`,
`refs/tags/b6/**`, `refs/tags/bytes/**`, `refs/tags/pin/**` and `refs/tags/archive/**`. New tags under those patterns
can still be created, which `pin/b5-ledger-final` and the later `archive/branch/<name>` tags need. The
`fixture-d117-v2-production-v1` tag is not covered.

Optional, [tag-creation-ruleset.json](execution-2026-11-08/tag-creation-ruleset.json): `creation` is restricted
with an admin (RepositoryRole 5) bypass. On this single-account repository every credential, including the agents'
`gh`, is the admin, so this rule changes nothing in practice. Install it only if collaborators are added.

**Probe** (safe whichever way it goes): create `pin/ruleset-probe-2026-11-08` at main, push it, then run
`git push origin :refs/tags/pin/ruleset-probe-2026-11-08`. The push **must be rejected** with a rule violation. The
probe tag then stays as a permanent marker. Never probe with a real anchor.

**What needs Ed.** Creating the ruleset needs only repository admin. The `gh` token (`repo` scope, admin on this
user-owned repository) is enough, and Ed has approved it, so the lead runs it. If the API returns 403, Ed creates the
ruleset in Settings → Rules → Rulesets → New tag ruleset with the same fields. Ed is also the only one who may later
**disable or edit** the ruleset, for example to correct a tag. An admin credential can always do that, and the
registered SHAs plus the two backups detect it.

## d. Delete merged branches only (after a2 and c)

The approved set is 640 merged branches in **7 batches of at most 100**, taken in order from `BATCH1-APPROVED.tsv`.
**Each batch** starts from a fresh fetch and a **fresh rerun of the branch-name consumer scan**. `prune_refresh.py`
runs `prune_branch_names.py`, then the gate. Any refusal removes that branch from the batch; the batch does not
proceed with it.

```sh
R=/Users/edr/code/CapstoneProject/jw-wt/prune-census; W=<clean checkout of ops/2026-11-08-prune-execution>
A=archive/process-traces-before-release-prune-2026-11-08; AC=901d7580def7862127ad2f4acb33011286d7e688
OUT=<new scratch dir per batch>; N=<batch number 1..7>
git -C "$R" -c gc.auto=0 fetch --prune origin '+refs/heads/*:refs/remotes/origin/*' '+refs/tags/*:refs/tags/*' \
  '+refs/pull/*/head:refs/remotes/pull/*/head'
(cd "$W" && python3.13 -B scripts/ops/prune_refresh.py --repo "$R" --output "$OUT/census" \
  --archive-commit "$AC" --archive-date 2026-11-08)                    # must end in "PASS snapshot topology", exit 0
gh pr list -R mpmdw/JouleWise --state open --limit 300 --json number,headRefName,baseRefName \
  --jq '.[] | "\(.number)\t\(.headRefName)\t\(.baseRefName)"' > "$OUT/open-prs.tsv"
tail -n +2 "$W/docs/ops/execution-2026-11-08/BATCH1-APPROVED.tsv" | cut -f1 | sed -n "$(( (N-1)*100+1 )),$(( N*100 ))p" > "$OUT/batch.txt"
(cd "$W" && python3.13 -B scripts/ops/prune_batch_gate.py --repo "$R" --census "$OUT/census" --batch "$OUT/batch.txt" \
  --open-prs "$OUT/open-prs.tsv" --archive-tag "$A" --approved "$OUT/approved.tsv")   # refused rows go to stderr
# INTENT: append one row per approved branch to docs/ops/PRUNE-ROLLBACK.tsv, then commit and push BEFORE deleting:
#   <utc>  INTENT  <branch>  <sha>  $A  <tag object>  f6f566e6…  jw-archive + Dropbox  <operator>  batch-$N
tail -n +2 "$OUT/approved.tsv" | while IFS=$'\t' read b c; do
  git -C "$R" push --force-with-lease="refs/heads/$b:$c" origin ":refs/heads/$b" && echo "CONFIRMED	$b	$c" || echo "FAILED	$b	$c"
done | tee "$OUT/outcome.tsv"
git ls-remote --heads origin > "$OUT/heads-after.txt"   # every CONFIRMED name must be absent; every FAILED name unchanged
# Append the outcome rows to PRUNE-ROLLBACK.tsv; commit and push.
```

- **Size and reversibility.** Each deletion removes one ref. The tip is an ancestor of protected main and of the
  immutable archive tag, so no commit becomes unreachable. To restore a branch:
  `git push origin <sha>:refs/heads/<branch>`, using the sha from the rollback log. The objects are on main, in both
  bundles, and in `refs/pull/*`.
- **Hard exclusions.** These are enforced by the gate and repeated here:
  - main, `archive/*` and `records/*`;
  - every item-228 lane, and all `align/2026-11-08-*` integration branches (they are unmerged, so HOLD);
  - `lane/b5-r1-9b-fix`, until `dcaf2ca2c` is on main;
  - the 40 consumed names;
  - the bases of #566 and #679;
  - any branch whose tip has moved.
- **Unmerged branches** are not touched in this prune. Retiring one later works like this: create an annotated
  `archive/branch/<name>` tag at the exact tip, push it, check it with ls-remote (the ruleset covers `archive/**`),
  refresh the mirror and both bundle copies, then lease-delete.
- **Local names.** After the remote deletes, `git branch -d -- <name>` in `handoff`, only where the local tip equals
  the deleted tip. Optional; it frees nothing that matters.

## e. Air disk cleanup: only items the checklist proves safe (after a2)

Each item listed here passed every one of these checks:
- no inbound alternates;
- not a worktree parent;
- `git status --porcelain --untracked-files=all` is empty;
- no ignored files;
- no stash of its own;
- every local branch, tag and HEAD is in the fresh mirror;
- no process has it open;
- it belongs to a finished lane.

Paths are under `/Users/edr/code/CapstoneProject/jw-wt/`. None is in a synced tree.

| Path | Size | Kind | Why it is safe | Restorable |
|---|---|---|---|---|
| `b5-robust-rev-sol` | 679M | standalone clone | B5 robust review (released). Clean, all refs in mirror, no borrowers | yes: re-clone, then `git checkout 9eb90c6c5` |
| `b5-robust-rev` | 681M | standalone clone | same; HEAD `4b0781b04` | yes |
| `sol-u90-item3` | 390M | clone (borrows handoff) | B5 u90 lane. Its once-unpushed `72de487f0` is on GitHub (in mirror) | yes |
| `sol-u90-item5` | 390M | clone (borrows handoff) | same; `fc39a2499` is on GitHub | yes |
| `cmp-dryij` | 399M | clone (borrows jw-b5-analysis) | B5 dry-run comparison, finished. It is a borrower, not an owner. Removing it lowers the store's borrower count | yes |
| `sol-prune-fixes` | 208M | clone (borrows handoff) | Prune-fixes Sol seat. Its work is `526d11168`, on GitHub | yes |
| `runstate-176`, `runstate-196` | 386M, 193M | handoff worktrees (detached) | old RUN_STATE edit worktrees; clean | yes: `git worktree add <path> 28fe66141` / `87682bfbd` |
| `capmerge` | 193M | handoff worktree | clean, detached `f48741f15` | yes |
| `u90-item3-int`, `u90-item5-int` | 389M, 389M | handoff worktrees | B5 u90 integration; clean; their branches stay in handoff | yes |
| `b5-under-90`, `b5-robust-fc`, `b5-care-audit` | 389M, 390M, 386M | handoff worktrees | B5 speed and audit lanes, finished; clean | yes |

That totals **5.1 GiB**. Commands:
- clones: `rm -rf -- /Users/edr/code/CapstoneProject/jw-wt/<name>`, one literal path at a time;
- worktrees: `git -C /Users/edr/code/CapstoneProject/jw-wt/handoff worktree remove <path>`. Git refuses if the
  worktree is dirty, and never use `--force`.

Run the eligibility row again ([AIR-CLONE-STATE.tsv](execution-2026-11-08/AIR-CLONE-STATE.tsv)) right before each
removal, and skip the item if anything changed.

**KEEP. These are not proven safe, or are needed:**
- Object owners:
  - `handoff`: 21 clones and 31 worktrees, plus `gc.auto=0`.
  - `council-pr`: 3 clones. It shows 10,519 "unpushed" only because it has no remote-tracking refs; all its branch tips
    are on GitHub.
  - `/Users/edr/jw-b5-analysis`: 9 or more borrowers. Never delete or GC it until every borrower is repacked or
    retired. It also holds `050aaad13`.
- B5 re-verification worktrees: `b5-release-check`, `b5-release-final`, `b5-r4-run`, `b5-r3-run`, `b5-r4`,
  `b5-r3-assembly`, and `b5-results` (the write-up is in progress).
- Live lanes:
  - qwen4_exp / Flash-Next: `opus-port-*`, `opus-flashnext-twin`, `opus-realparity`, `rec-l3ref`;
  - ALIGN v4: `sol-v4-*`, `r0-*`, `align-v4-assembly`;
  - every `sol-*` clone dated 11-08 (review rounds still in progress).
- Active now: `d5`, `w1-smoke-merged`, and the `/private/tmp/jwsol` job.
- Dirty trees: `b5-lean*`, `b5-robust`, `b5-u90-r2`, `ci-rootcause-b6*`, `p10-review`, `wp7-review`, `wp8-cold`,
  `sol-v4-plan`, `sol-v4-wp5`.
- Non-git directories whose content was not inspected (blinding): `b5-lean-data` 1.2G, `prune-work` 422M (the
  11-06 inventories, which may be the only copy), `align-v4-assembly-tmp` 275M, `ci-rootcause-b6-tmp` 161M, and the
  Sol `*.events.jsonl` audit logs.
- Model caches (none on the Air), the backup directory itself, and `prune-census`.

**Owner review, not proven safe:** the broken `/private/tmp` clones (`jw-w1bm-sol1-baseline-35dccf241`,
`jw-optin-audit/*`) and the `/private/tmp/jw-smoke-*` candidates.

## f. MBP checklist: magistrate only, in a gap AFTER R1 closes

R1 is **armed now** (item 227: t0 Sun 01:17 PST; latest end **Mon 11-09 06:39 PST**). Nothing here runs while any
plan is armed or a window is measuring. Each step starts by confirming no arm is loaded. None of this is
hardware-bound except f1, so do as little as possible on the MBP (offload rule).

1. **Recover the B5 final ledger, `4cb222a19`.** From the MBP ledger repository, push the full SHA to
   `records/b5-ledger-final`. Create the annotated tag `pin/b5-ledger-final` at the same SHA and push it explicitly.
   Check both with `git ls-remote origin refs/heads/records/b5-ledger-final 'refs/tags/pin/b5-ledger-final*'`; the
   full SHA must start with `4cb222a19`. Tell the lead. The lead fetches it into the Air mirror (plain fetch, never
   `--prune`, because `refs/air-local` must survive), re-bundles, and refreshes both copies. No MBP checkout cleanup
   happens before that.
2. **Model weights KEEP inventory.** For each cache (HF, MLX conversions, SSD-hosted), record: repo or model id,
   pinned revision (ALIGN v4 `Qwen/Qwen3.8-27B@8c0b3d30…`, the B6/BYTES manifests, the Flash-Next originals and
   conversions), path, and per-shard digests. Delete nothing unless a digest-verified second copy is recorded
   **and** no live lane uses it. Being re-downloadable does not count as retention.
3. **Alternates and unique work.** Use the same metadata-only graph as on the Air. For every clone, check
   `rev-list --branches --not --remotes`, stashes and dirty state before removing anything. Set `gc.auto=0` in owner
   stores.
4. **Removable volumes.** Run `git worktree lock --reason "removable volume"` on SSD-hosted worktrees while the SSD
   is attached. Never run `git worktree prune` with the SSD detached.
5. **The SSD is never a retention copy.** It is borrowed and attached by day only. A second copy of an MBP archive
   must be the Air (outside sync), Dropbox (checked from another session), or owned storage. Check every deleted path
   against both manifests and confirm it is outside iCloud and Dropbox before Ed deletes it.

## g. What remains and who does it

| # | Step | Size | Reversible | Gate |
|---|---|---|---|---|
| 1 | a2: Dropbox copy and remote check | +317 MB upload | additive | allow the upload (classifier) |
| 2 | c: tag ruleset POST and probe | none | admin can disable | none; Ed approved |
| 3 | Merge `dcaf2ca2c`, the test fix, to main | none | normal PR | CI |
| 4 | d: 7 batches, 640 merged branch refs | 640 refs, 0 commits lost | yes: push sha back from log, bundle or PR ref | 1 and 2 done; fresh census PASS and gate per batch |
| 5 | e: 14 Air items | 5.1 GiB | yes: re-clone or `worktree add` | 1 done; recheck each row |
| 6 | f1: `4cb222a19` to server, then the Air re-bundles | none | additive | R1 closed (after Mon 06:39 PST); magistrate |
| 7 | f2 to f5: MBP cleanup | per inventory | per item | 6 done; never while armed |
| 8 | Dispositions for 41 refused names, `050aaad13`, `6bcd90a3`, `9a6f8880` | none | n/a | owner or lead |
