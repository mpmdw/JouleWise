# Release-day prune plan

**PLAN ONLY — no operation is authorized by this document today.** Revised for
Opus's `ADMIT_WITH_FIXES` cold review on
`origin/ops/2026-11-08-prune-plan-opus-review:docs/ops/prune-plan-opus-review.md`.
Source identities: [PIN-INVENTORY](PIN-INVENTORY.md). Future driver contract:
[TAG-PINNING](TAG-PINNING.md). No network, cleanup, tag creation or publication
was performed while preparing this revision. All commands below belong to a
later owner-controlled session after the gates have passed.

Keep main's history intact. Use **one GitHub tag ruleset**, about 30 named
anchors (33 in the present TSV), existing `b5/*`, `b6/collection` and
`bytes/collection-n*` tags, a fresh self-contained mirror and `bundle --all` in
two durable places. Batch 1 deletes **merged branches only**. Later unmerged
retirements preserve the **whole tip** at `archive/branch/<branch-name>` first.
The citation census checks coverage; it does not manufacture per-citation tags.
No filter-repo, main rewrite, reflog expiry, aggressive GC or alternate-store
pruning is proposed. Frozen B5 driver/registration semantics remain unchanged.

## Entry gates and branch disposition

1. The lead accepts the B5 release receipt and independent recompute/comparison
   gates; the running eight-worker analysis has ended. Supply five full commit
   identities from the receipt: **analysis, equivalence oracle (including the
   D-189 reference), independent comparator checkout, recompute checkout, and
   release checkout (`release_checkout.commit`)**. Record tree IDs, receipt
   digest and the existing or new exact retaining tag for each. Do not assume
   these are the same commit, r4, or the current branch tip. The #704 comparator
   `bea480f296e5c7bc77ad1684936f2b257801f597` must be retained if used off main.
2. The magistrate recovers **B5 final ledger head `4cb222a19` from the MBP** to
   server branch `records/b5-ledger-final` and annotated tag `pin/b5-ledger-final`;
   the recorded full SHA must start with `4cb222a19`. Verify both server targets
   with `ls-remote`, include them in the mirror/bundle, and prove recovery before
   **any MBP checkout cleanup**. This is an owner/magistrate step, never a license
   for this blinded worker to open its checkout or ledger. Do not substitute the
   collection tag for this descendant.
3. Fetch remote branches **and PR heads** before refreshing or declaring an
   object unavailable. `498ad1d0` exists on GitHub per Opus; it is an **unfetched
   server object**, not a missing-history finding. Resolve its full SHA after
   fetching PR heads. `050aaad13`, `6bcd90a3`, `9a6f8880` need recovery or explicit
   owner disposition; unresolved scientific pins cannot be waived as narrative.
4. Refresh the census and review its diff. [BRANCH-TRIAGE.tsv](BRANCH-TRIAGE.tsv)
   records exact tips; new/moved refs default HOLD. Main plus **every HOLD tip**
   is scanned for eligible source text, including docs, tools, code/config/tests
   and registrations (fixture data payloads and sealed paths are excluded).
   Unchanged HOLD blobs inherit main's scan; changed/new regular blobs are read
   at each tip. Sealed path components are excluded, never followed. Unresolved
   hex strings include dates, synthetic values and model revisions: disposition
   actual Git citations explicitly. No local census proves server freshness.
5. Land the separate equivalence-test fix before batch 1. It requires
   `b5/analysis-r1-9bfix-ref^{commit}`; absence is a failure. Run the committed
   name-consumer grep on main and HOLD tips. For **every candidate hit**, record
   source location, exact tip, owner, disposition (runtime migration, narrative
   only with reason, or KEEP). Unresolved hits keep that branch on HOLD.
6. Complete tag publication/protection, PR/check evidence, two-copy recovery,
   worktree/alternates and model-cache gates below. B6, BYTES, ALIGN, qwen4_exp,
   Flash-Next and x86 remain independent live lanes. B5 release does not retire
   them or change lead-owned coordination state.

| Branch set | Disposition |
|---|---|
| Refreshed `MERGED-CANDIDATE`, unchanged tip ancestor of freshly fetched protected main | Batch 1 eligible only after name-consumer dispositions, clean/idle worktrees and retention proof |
| Every unmerged branch, including historical harvest 2/3, B6/BYTES records, ALIGN, ports, research, #701 and #704 | HOLD in batch 1; later owner retirement must tag the entire exact tip as `archive/branch/<name>`, publish/protect/verify it and refresh both bundles first |
| Main, symbolic HEAD, active ops/delivery/evidence lanes | KEEP; a Git ancestry result cannot retire a live interface |
| Existing `archive/pre-prune-2026-11-06` branch **and** tag | KEEP both unchanged; existing archive promise persists |

## File prune PRs and dependency gates

The 2026-11-06 prune already removed roughly 8,100 files. Do not regenerate its
deleted inventories or restore them just to delete them again. These are the
remaining retirement groups; paths are exact files or explicit scoped patterns,
not commands to run against external storage. Preserve all at the new archive
tag first. See [TRIM_REPORT §6](../process/TRIM_REPORT.md#6-needs-ed-one-line-recommendation-each)
and [previous prune §4–5](../run_reports/2026-11-06-repo-prune.md).

| Files/directories | Proposed action and reason | Dependency gate before deletion |
|---|---|---|
| `docs/process_traces/**`, remaining historical `docs/legacy/**`, `docs/reviews/**`, dated `docs/run_reports/**` | Archive historical records at archive tag; remove only superseded traces with no current reader | Keep seal record, errata, current runbooks, decision/registration authority and every live kernel pointer. Move citations/readers to immutable commit/tag paths where appropriate; lead owns state edits |
| Superseded campaign generations `configs/campaigns/d117_*qwen25*`, `d117_*_v1`, `_v2`, `_v3`, and historical `configs/p2_015_floors/**` | Retire whole unused generations and companion generators/tests; old pins should not indefinitely keep main's packs | Preserve old bundle readers. Live v5 references still pin `p2_015_floors/calibration_plan.json`; migrate those consumers or KEEP it. No glob deletion of all `d117_*` |
| `joulewise/arm_readiness.py`, `arm_readiness_evidence.py`, `arm_readiness_evidence_t0.py`, `t0_rehearsal.py`, `night_gate.py`, `v5_qualification.py`, `arm_retry.py`, `network_time_off.py`, `dwell.py`, `scheduler_gates.py` | Retire old CA-42 arm/T-0 chain as one coupled PR | Extract still-used physical probes into `joulewise/hazards/`/shared modules; remove `bundle.py`'s arm-readiness dependency; preserve active ALIGN/hazard callers and old-format readers. Coordinate with PR #668; do not duplicate its work |
| `scripts/capture_t0_step.py`, `launch_window.py`, `author_arm_*`, `generate_arm_readiness.py`, `produce_t0_rehearsal_bundle.py`, `rehearse_t0_unattended.py`, `v5_s1_desk_closeout.py`, `check_v5_arm_abort.py`, `restore_v5_null_reservation.py`, `assemble_v5_battery_boundaries.py`, `scripts/ed_session/**` | Remove retired chain entry points and their dedicated tests | Retire together with module group above, hazard-refusal allowlists, coverage builders and pack evidence. Do not remove a still-imported wrapper |
| `scripts/harvest_g2a_window.py` | Superseded G2-a collection helper | `joulewise/v5_qualification.py` imports it; retire that caller first or retain the helper |
| `joulewise/b5_analysis/**` and old per-step computation; `joulewise/whole_window.py` L9 mirror | Move B5-only reproduction to preserved analysis checkout; eventually remove superseded heavy computation from main | First prove released reproduction at its frozen tag with environment records. Preserve independent recompute, release verifier, comparator and old-data readers. Shared `whole_window.py` cannot be deleted wholesale; main's reducer must carry the ruled clamp before removing the mirror |
| `tests/b5_analysis/test_frozen_files.py` working-tree assertions; old computation-only tests | Replace with commit-scoped integrity tests; retain freeze enforcement at the actual reproducing checkout | No edits to frozen B5 source or original digest values. Assert original and ruled-rebound identities separately; introduce migration regression before removing current assertions |
| `scripts/axi_sb_static_batch_spike.py`, `axi_sc_spec_decode_spike.py`, `spike_mlx_prompt_cache.py`, `codex_usage_probe.py`, `measure_claude_cold_start.sh`, `gen_affine_smoke.py`, `gen_gsm8k_scored.py`, `gen_jw_mixed.py` if still present | Archive one-shot experiments with recorded verdicts; delete superseded entry points | Confirm absence from live imports, manifests, scanners and tests; retire their dedicated tests only. Presence must be rechecked because earlier prune already removed some |
| `joulewise/adapters/node_worker.py`, `node_client.py`, `ssh_transport.py`, `nvidia_smi.py`, `vllm_runtime.py` and dedicated tests | Candidate retirement of never-live remote stack | **DEFER**: old trim recommended after paper; fresh x86/CUDA work may adopt it. Obtain owning-lane decision before any removal |
| `scripts/build_site.py`, `pack_capsule.py`, `release_check.py`, `build_capstone.py`, `claims_lint.py`; `docs/site/**`, `docs/report_src/**`, `site_capsule/**` and RPT-only tests | Archive/delete as one unit if public site/report pipeline is no longer a deliverable | **DEFER** deliverable decision; `docs/paper/artifact-guide.md` still tells readers to run build_capstone |
| `joulewise/scored_{packer,reduce,registration}.py` and their tests | Retire dead lane as one unit | **DEFER** until lead closes A291–A296; this task cannot change kernel/state |
| `scripts/mint_floor_artifact.py`, `joulewise/analysis_manifest.py`, `joulewise/load_transition_alignment.py` | **KEEP** | Generalized mint loads v1 as core; issued manifest reader still needed; load-transition task remains live. “Old” does not imply removable |
| `configs/pins/registry.json`, `configs/gates/hazard_refusals.json`, number-coverage tables and test timing map | Update in each coupled prune PR, not standalone deletion | Regenerate registry only after reviewed retirement; never repin a protected number from changed bytes. Timing hints for deleted tests can be dropped |

Keep independent recompute, its comparator, equivalence comparator and independent
twins separate. Their independence is intentional. No raw evidence, issued
artifact, run bundle, model checkpoint, receipt, original registration or
calibration record is destroyed by a Git file-prune PR.

## CANONICAL.md changes in the eventual PR

Do not change the current tool map as though this plan had already run. Each
landed prune PR updates its rows with the replacement and retained tag:

1. Add this pin inventory, prune plan, immutable archive tag and tag-pinning
   policy under repository operations. Preserve the old archive retrieval guide.
2. Split B5 “reproduce released block” (receipt's frozen tag/commit and recorded
   environment) from production numbers for future blocks (independent recompute
   after its coverage gate). Keep release/comparison tools discoverable.
3. Replace CA-42 collection/T-0 entries only when their successor paths are
   installed and callers have moved. Keep current ALIGN lane pointers through
   integration; do not label the provisional registration as frozen/live-validated.
4. Remove kept-but-undecided rows only after the deliverable/task-owner rulings.
   Cite tags for retired computation and identify the retained format reader.
5. Add the pin integrity test and standalone-bundle recovery procedure. Keep CI's
   full suite on CI; this blinded machine must not run it.

## Later operator sequence — never run in this blinded task

### 1. Fresh census, receipt identities and review evidence

Use an idle, owner-chosen checkout; disable auto-GC in alternate object owners
until borrowers have been dissociated. Fetch does not count as dissociation.
In the **later connected session only**:

```sh
git -c gc.auto=0 fetch --prune origin
git -c gc.auto=0 fetch origin '+refs/pull/*/head:refs/remotes/pull/*/head'
ARCHIVE_COMMIT=$(git rev-parse refs/remotes/origin/main)
# Set RELEASE_DATE and CENSUS_DIR to reviewed values; output must be inside the
# owner-approved scratch area. Never reuse an already-created archive tag name.
python3.13 -B scripts/ops/prune_refresh.py --output "$CENSUS_DIR" \
  --archive-commit "$ARCHIVE_COMMIT" --archive-date "$RELEASE_DATE"
# Review output vs docs/ops; commit the refreshed tables and dispositions.
```

The four scripts in `scripts/ops/` never fetch, tag or delete. The refresh emits
all five original TSVs, `CENSUS-SCOPE.tsv`, `CENSUS.json` and
`BRANCH-NAME-CONSUMERS.tsv`. Name hits have disposition REVIEW. The standalone
`prune_branch_names.py` exits 1 when matches need review. `prune_verify.py`
refuses a stale archive row, changed scope tip or lost commit; normal snapshot
mode reports HOLD-only pins without calling them protected. Its
`--release-ready` mode refuses HOLD-only pins and requires local exact tags;
use it for a scoped unmerged-retirement manifest after adding its whole-tip
archive tag. The full census may still report unrelated HOLD-only pins, whose
branches must remain.
It is a local topology check, not an attestation of administrative gates.

[TAGS-TO-CREATE.tsv](TAGS-TO-CREATE.tsv) is now a **named-anchor manifest**:
existing names are verified/reused, not recreated. Add the five receipt roles
and recovered ledger to it at release time, reusing existing exact tags where
possible. The archive row must equal `ARCHIVE_COMMIT` from that fetch; the
refresh sets it, and the verifier refuses a different target. Date the archive
name at creation, never move an existing tag to refresh it.

For **each tag**, complete [TAG-REVIEW-EVIDENCE.tsv](TAG-REVIEW-EVIDENCE.tsv)
and archive an evidence row containing tag name, tag-object ID,
peeled full commit and tree, PR number, exact reviewed SHA, required check names
and conclusions, source JSON/digest and reviewer/time. Use PR/check evidence for
the exact SHA (not a green sibling or the latest run on the branch). If a
historical pin lacks a PR, retain it as historical evidence and record that
limitation; it cannot authorize a new tag-pinned run. A protected `block/*` line
with the same required checks can establish review provenance, but still record
its originating PR/check evidence per tag. Unknown or failing checks block use.

In the later connected owner session, collect (with pagination):

```sh
gh api --paginate --slurp "repos/mpmdw/JouleWise/commits/$commit/check-runs" > "$CHECKS_JSON"
gh api --paginate --slurp "repos/mpmdw/JouleWise/commits/$commit/pulls" > "$PRS_JSON"
```

Do not infer PR numbers/check results offline; the current evidence status is
**PENDING**, not PASS. Keep receipt/evidence JSON and their digests with both
backups. [TAG-PINNING](TAG-PINNING.md) defines review and ruling authentication.

### 1b. Ed's one ruleset; publish and verify exact tags

Ed creates **one active GitHub tag ruleset** covering **all `refs/tags/**`**
(including existing scientific names, `pin/**`, and archive names). Block updates
and deletion, restrict creation to repository admins; no agent bypass grant.
Record/export ruleset JSON, ID, active enforcement, patterns and bypass roles.
Verify those settings from the server; do not assume main protection covers tags.
Record any administrative bypass powers explicitly; an admin credential is not
mutation-proof. Registered commit/tag-object IDs and both backups remain checks
against an accidental administrative retag.
This gate precedes every remote branch deletion. New tags are annotated; verify
existing annotated identities unchanged. Signing is optional, never implied.

Create missing manifest tags locally using `git tag -a` at each full SHA only
after the manifest/evidence review; existing conflicts stop the process. Then
push **only the explicit reviewed ref list**, with no force or `--tags` wildcard:

```sh
git push origin "refs/tags/$reviewed_tag_1" "refs/tags/$reviewed_tag_2"
git ls-remote --tags origin > "$SERVER_TAGS"
```

For **every** manifest tag require both `refs/tags/<name>` (tag-object ID) and
`refs/tags/<name>^{}` (peeled commit) to match the local object and manifest.
Record the server listing and compare it to the evidence rows; missing,
lightweight, conflicting, deleted/recreated tag objects fail. This is a required
operator comparison, not just saving the listing. Also verify
`records/b5-ledger-final` against the recovered full SHA. No deletion can proceed
from local tags alone. Avoid force-updating any scientific tag.

### 1c. Mirror, bundle --all, two durable copies and isolated restore

After server publication, create a fresh mirror **from GitHub**, never a local
alternate-backed clone. Explicitly fetch PR heads: do not rely on clone defaults
for the hosting service's special refs. Preserve all branches, tags and PR heads.

```sh
git -c gc.auto=0 clone --mirror "$GITHUB_URL" "$MIRROR_REPO"
git -C "$MIRROR_REPO" -c gc.auto=0 fetch origin '+refs/pull/*/head:refs/pull/*/head'
git -C "$MIRROR_REPO" rev-parse --is-shallow-repository  # require false
# Require no objects/info/alternates or GIT_ALTERNATE_OBJECT_DIRECTORIES.
git -C "$MIRROR_REPO" fsck --full
git -C "$MIRROR_REPO" bundle create "$PRESERVATION_BUNDLE" --all
git -C "$MIRROR_REPO" bundle verify "$PRESERVATION_BUNDLE"
git -C "$MIRROR_REPO" bundle list-heads "$PRESERVATION_BUNDLE" > "$BUNDLE_REFS"
git clone --mirror "$PRESERVATION_BUNDLE" "$RECOVERY_REPO"
git -C "$RECOVERY_REPO" fsck --full
```

Require no bundle prerequisites and no recovery alternates. Compare **every
saved ref/object ID**, all anchor tag-object/peeled IDs, release identities,
recovered ledger and inventoried commit reachability against the recovery repo.
HOLD-only citations remain explicitly HOLD-only; before retiring one, its whole
tip must become a protected archive tag. Enumerate any UNRETAINED citation and
recover/retain it before deletion; a successful bundle cannot repair absent refs.
Keep the mirror plus complete bundle, manifest, scope, receipts, PR/check JSON,
server listing and rollback log in **two durable independent places** with
matching SHA-256 manifests and a recovery test from each. Record destinations,
volume/service identity, verifier and time. Two directories on one device or
one sync account are one failure domain. **The borrowed SSD never counts as an
independent copy**, even if it currently holds a correct bundle. Use owned
storage, a self-contained Air copy, or a verified independent cloud destination.

### 2. Merged branches only; freshness, lease and rollback record

Create a reviewed approved subset of `MERGED-CANDIDATE` rows. For each, bind the
name-consumer dispositions and worktree-idle evidence to that exact snapshot SHA.
Immediately before checking tips, **fetch first**, never trust stale tracking refs:

```sh
git -c gc.auto=0 fetch --prune origin
git rev-parse "refs/remotes/origin/$branch"  # must equal snapshot_commit
git merge-base --is-ancestor "$snapshot_commit" refs/remotes/origin/main
git merge-base --is-ancestor "$snapshot_commit" "refs/tags/$ARCHIVE_TAG^{commit}"
# Commit an INTENT rollback row before deletion, then perform the explicit lease:
git push --force-with-lease="refs/heads/$branch:$snapshot_commit" origin \
  ":refs/heads/$branch"
# Verify server absence; append CONFIRMED (or FAILED) to the committed log.
```

The rollback log is [PRUNE-ROLLBACK.tsv](PRUNE-ROLLBACK.tsv) (header only today;
no deletion occurred). Append timestamp, INTENT/CONFIRMED/FAILED, branch,
full SHA, archive tag/tag-object ID, bundle digest/location, operator and receipt.
Commit INTENT before the operation and outcome afterward; an interrupted push
leaves a recoverable intent. Abort on a moved tip, failed check or unexpected
server result. Delete local names only with `git branch -d -- "$branch"` after
checking local tip equality; it also rejects registered checked-out branches.

Restore an accidentally deleted name from a verified bundle/recovery repository,
protected tag, or saved PR ref:

```sh
git cat-file -e "$snapshot_commit^{commit}"
git push origin "$snapshot_commit:refs/heads/$branch"
```

Verify the restored server SHA. Do not force over a newly created branch.
Unmerged retirement is a **later** explicit owner decision: add annotated
`archive/branch/<name>` at the exact tip, with review/evidence status, push and
verify under the same ruleset, refresh both backups, repeat census/consumer
checks, then lease-delete. This replaces the old harvest exceptions.

### 3. Bounded file-prune PRs

Use the dependency table above. Preserve old-format readers and independent
tools. For every retired path review `git show HEAD:<path>` and `git log -S`
consumers, especially `paper_custody.py`, `paper_reported_energy.py`,
`evidence_night.py`, `refresh_receipt_histsem_pinset.py`,
`build_v4_histsem_pinset.py`, `harvest_window.py`, `flags/collect.py`,
`digest_pin_census.py`, `arm_readiness.py`, identity pins and generalized mint.
Main history alone does not preserve a path that a verifier reads at HEAD.
Migrate those consumers with meaningful regressions before removing files.
Use an explicit reviewed path list; update CANONICAL, registry and affected
callers in the same PR. Run affected unittest modules one at a time; full CI
belongs off this busy machine. Frozen-source and scientific digest identities
remain unchanged. Reproduction from sealed data is a lead gate outside agents.

## Disk cleanup — Ed/magistrate only, after jobs and retention gates

No machine inventory or copy verification is claimed here. No external paths
were inspected. Never use a blanket recursive deletion, age-based scratch prune,
cache purge or worktree prune as an implied follow-on operation.

### Gates shared by both machines

- For **every** copy to delete, record its exact local path and prove it is
  **outside every synced tree**, including Dropbox and iCloud Desktop/Documents.
  Local deletion in a synced tree propagates to cloud storage. Such a path is
  ineligible for this deletion procedure; cloud eviction is a separate explicit
  owner action. Verify the cloud copy from a different device/session by
  re-downloading and comparing all manifest checksums; Finder badges and local
  placeholders are insufficient. Retain two durable independent copies, excluding
  the borrowed SSD. Keep manifests/custody/verification receipts with them.
- Build a **model-weight KEEP inventory** from live registrations/identity pins:
  repository/model ID, upstream revision, format/conversion, exact owner-recorded
  local path, all shard/tokenizer/config digests, dependent lanes, second-copy
  destination and checksum/recovery receipt. Include ALIGN v4's pinned
  `Qwen/Qwen3.8-27B@8c0b3d30…`, B6/BYTES manifests, qwen4_exp/Flash-Next originals
  and MLX conversions, and x86 working sets. Treat paths as text here. KEEP all
  HF/MLX caches and conversion inputs until this inventory is complete; upstream
  re-downloadability is not retention. Remove a cache only after a digest-verified
  durable second copy is recorded and no live job depends on it. Never download
  or open weights in this planning task.
- Before any clone removal, record clean/dirty state, untracked/ignored files,
  branch/HEAD, worktree registry, active owner/process, and
  `git rev-list --branches --not --remotes` for **unpushed commits**. Preserve
  unique commits with pushed/verified retention refs and both bundles first.
  A clean working tree does not prove there is no unique work.

### Air: alternates graph before any clone or checkout removal

- Do not touch the long-running analysis job, its environments, custody or
  outputs. The current authoritative correction is: **handoff is now
  self-contained**. Do not repeat the review's stale handoff → council-pr edge.
  Surviving `sol-*` borrowers still need handoff's objects: KEEP handoff until
  every surviving borrower is dissociated or intentionally retired.
- `/Users/edr/jw-b5-analysis` **still backs about 14 clones**. This is a textual
  owner warning only: **never delete or GC it before all surviving borrowers
  have been repacked/dissociated**. Do not open it in this blinded session.
  Keep council-pr or any other object owner if the refreshed graph still names
  it. Counts and edges must be rechecked by Ed, never inferred from directory age.
- Ed obtains an authorized metadata-only alternates graph for approved clone
  roots (including approved home clones); do not blindly traverse `$HOME` or any
  sealed/restricted root. Record each clone, its actual Git/common directory,
  alternates edges (including chains), dependents, unpushed commits and worktrees.
  Mark **every object owner KEEP** and set `gc.auto=0` there before operations
  that might auto-GC. No agent permission to read protected paths follows.
- For each surviving borrower, while stores are intact and jobs idle, Ed runs
  `git repack -a -d` **without `--local`** so borrowed reachable objects copy in.
  Save its alternates metadata, detach that file, unset alternate environment
  paths, then run `git fsck --full` and required-ref/recovery checks isolated from
  owners. A failure means restore the metadata and KEEP the owner. Iterate chains
  until there are no surviving inbound dependencies. Repacking an owner alone
  does not dissociate its borrowers. Install refs for unique commits first.
- Distinguish standalone clones from registered worktrees. Remove only reviewed
  idle clean worktrees through Git; keep environments/locks through recovery.
  Scratch age alone is not proof of disposability. Preserve unique reports,
  sockets, process files and locks. The existing jwgold Dropbox receipt still
  needs the unsynced-source and independent-session recovery checks above.

### MBP: magistrate ledger recovery first

- **Before any checkout cleanup, the magistrate completes `4cb222a19` recovery,
  server branch/tag verification and both bundle restores in entry gate 2.**
  Preserve all other active collection, ledger and calibration dependencies.
- Apply the same alternates/unique-work checks before removing clones. Lock
  SSD-hosted worktrees with `git worktree lock --reason "removable volume"`
  while attached; a detached volume is not a stale worktree. Do not run
  `git worktree prune` while removable-volume worktrees are unavailable.
- The borrowed SN7100 is staging/scratch and **never an independent retention
  copy**. Draft permanent-SSD branches do not change that. Obtain owned storage,
  a verified self-contained Air copy, or an independent verified Dropbox copy
  alongside server-confirmed iCloud before deleting an eligible unsynced source.
- Check every file against both durable destination manifests, record volume and
  cloud identities/time/verifier, and test restore. Ed deletes only explicitly
  authorized redundant unsynced copies; failed/uncertain copies stay. No trash
  emptying or backup pruning follows implicitly. Preserve the model-cache KEEP
  inventory and exact release environment on both machines.
