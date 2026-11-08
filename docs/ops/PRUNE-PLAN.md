# Release-day prune plan

**Prepared only. Do not run before the Block-5 release.** Baseline and full pin
tables: [PIN-INVENTORY](PIN-INVENTORY.md). This task creates documentation and a
local commit only. It neither releases B5 nor authorizes a measurement, offload,
branch deletion, tag publication or disk cleanup today.

Keep main's history intact. Delete old working-tree files through ordinary PRs;
preserve scientific commits through immutable annotated tags and a standalone
backup. Tags are enough to preserve branch history, but cannot bypass the
ancestry checks in an already frozen driver. Future drivers follow
[TAG-PINNING](TAG-PINNING.md).

## Entry conditions

The release lead records that the B5 release receipt is accepted, independent
recompute/comparison gates have passed, and the current blinded job has ended.
The lead supplies the receipt's full analysis commit and adds it to the pin
manifest. Never infer it from the newest tag or a running process. Preserve all
earlier analysis tags, their oracle/refutation records and sealed inputs.

Refresh this inventory against the release-day repository. A moved branch,
additional pin, unresolved commit reference or new caller changes the deletion
set. In particular, recover the five unavailable commit citations in the
inventory (the final B5 ledger head is a provenance pin), or obtain an explicit
owner disposition for historical non-scientific references. A proof covering
only the locally resolvable set is not complete pin preservation. Keep affected
records/branches on hold until that work is done. Set the **not-yet-created**
archive tag's manifest target to release-day pre-prune main so it also covers
new process records; once created, never move it. B6, BYTES, ALIGN v4/v5, the MLX port and x86 work remain independent live
lanes. B5 release alone does not retire them. Coordination state and its pointer
targets remain lead-owned; this plan does not register or close kernel tasks.

## Branch disposition

[BRANCH-TRIAGE.tsv](BRANCH-TRIAGE.tsv) enumerates every locally recorded origin
branch with its full tip. At the baseline: **687 merged candidates**, **190 held
refs**, **605 held unmerged refs**. “Candidate” means safe for retention once the
tag/bundle, unchanged-tip, idle-worktree and no-live-ref-name checks pass; it does
not establish those operational checks. No remote freshness was queried.

| Branch set | Why it can be deleted / why held | Release-day condition |
|---|---|---|
| All `MERGED-CANDIDATE` rows (the exact list is the TSV) | Entire tips are ancestors of baseline; proposed archive tag retains all their commits | Recheck tip and archive ancestry; owner confirms branch name is not an active delivery or receipt interface; clean, idle worktrees only |
| `lane/2026-10-09-harvest-corpus-cap` at `224a264c5faaae90cdf56118df37e773a932700b` | Frozen historical harvest, whole tip retained by `pin/b5-harvest-2` | Candidate after release and ref-name consumers move to tag/SHA |
| `lane/2026-10-10-harvest-screen-sources` at `0699abbb0881ce64b39c46ba07de568cc3848260` | Frozen historical harvest, whole tip retained by `pin/b5-harvest-3` | Same; never re-harvest earlier excluded attempts |
| `lane/2026-10-11-harvest-trigger-scope` | Pin4 is `b039c0257`; branch tip is later `b517626d8` | HOLD until its entire tip is explicitly archived and its later changes dispositioned; pin4 alone does not preserve them |
| `records/b6-pin-heads` at `20c881075…`; `records/bytes-pass2-heads` at `1aca17e27…` | Whole ledger chains retained by proposed final-head tags | HOLD by default; eligible for a later owner-directed retirement after B6/BYTES consumers use tags. Their blocks remain live |
| `lane/2026-10-28-bytes-pass2-open`, `lane/2026-10-17-b6-packs-registered` and B6/BYTES analysis/stage lanes | Registration/measurement code still used off main | HOLD; preserve tags now, retire only after owners replace delivery pointers |
| ALIGN measurement/R1 integration, `align/*`, `port/*`, x86, current research and record branches | Ongoing science, porting, pending reviews or authoritative records | HOLD even if Git calls them merged |
| `archive/pre-prune-2026-11-06` branch and tag | Existing archive promise says neither ref will be moved/deleted | KEEP both; do not “deduplicate” the branch into the tag |
| `main`, origin's symbolic HEAD, current ops branch, `night*` refs | Primary/current refs or potentially sealed evidence | KEEP; no evidence-branch content census in this task |
| Every other `HOLD-UNMERGED` row | Unmerged is not synonymous with superseded; tags for individual pins cannot establish that all useful work is retained | KEEP pending explicit owner disposition; no wildcard deletion |

The two named historical-harvest candidates are additions to, not overrides of,
the TSV's conservative HOLD classification. No other unmerged ref is approved
for the first deletion batch. An ancestor test proves storage, not that an
operational consumer has stopped using a branch name.

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

## Commands, in order — for the later operator

These blocks are a runbook, not execution evidence. Run from a clean, owner-chosen
repository after the entry conditions, not a running analysis/measurement
checkout. All Git source inspection is offline. Set `RELEASE_COMMIT` to the full
40-hex receipt commit, `RELEASE_ID` to its reviewed identifier, and
`PRESERVATION_BUNDLE` to a new owner-selected bundle filename on independent
storage. These values cannot be filled from this blinded task.

### 1. Preflight, tag creation, then retention dry run

```sh
git status --short --branch
git rev-parse --is-shallow-repository       # must be false
git rev-parse HEAD refs/remotes/origin/main
# Compare branch tips and pin changes with the TSV snapshot; refresh if changed.
# Require clean worktree, completed jobs and the release receipt before continuing.
export RELEASE_COMMIT RELEASE_ID PRESERVATION_BUNDLE
python3 -B - <<'PY'
import csv, os, re, subprocess
def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()
assert not git('status', '--porcelain'), 'dirty tree'
assert git('rev-parse', '--is-shallow-repository') == 'false'
release = os.environ['RELEASE_COMMIT']
rid = os.environ['RELEASE_ID']
assert re.fullmatch(r'[0-9a-f]{40}', release)
assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', rid)
rows = list(csv.DictReader(open('docs/ops/TAGS-TO-CREATE.tsv'), delimiter='\t'))
rows.append({'tag': 'pin/b5-release-' + rid, 'commit': release})
for row in rows:
    tag, commit = row['tag'], row['commit']
    assert git('rev-parse', commit + '^{commit}') == commit
    ref = 'refs/tags/' + tag
    exists = subprocess.run(['git', 'show-ref', '--verify', '--quiet', ref]).returncode
    if exists == 0:
        assert git('cat-file', '-t', ref) == 'tag', 'expected annotated tag'
        assert git('rev-parse', ref + '^{commit}') == commit, 'tag conflict'
    else:
        assert exists == 1, 'cannot inspect tag'
        subprocess.run(['git', 'tag', '-a', tag, commit, '-m',
                        'Release-day retention; source: docs/ops/PIN-INVENTORY.md'], check=True)
PY

# DRY RUN: tags now exist, but no branch/file has been removed.
python3 -B - <<'PY'
import csv, os, subprocess
def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()
for row in csv.DictReader(open('docs/ops/TAGS-TO-CREATE.tsv'), delimiter='\t'):
    assert git('rev-parse', 'refs/tags/' + row['tag'] + '^{commit}') == row['commit']
for row in csv.DictReader(open('docs/ops/PIN-COMMITS.tsv'), delimiter='\t'):
    # One explicit merge-base check for EVERY inventoried commit, not just tips.
    subprocess.run(['git', 'merge-base', '--is-ancestor', row['commit'],
                    'refs/tags/' + row['preserving_tag'] + '^{commit}'], check=True)
assert git('rev-parse', 'refs/tags/pin/b5-release-' + os.environ['RELEASE_ID'] + '^{commit}') == os.environ['RELEASE_COMMIT']
print('PASS: all manifest commits retained; unavailable-pin gate is separate')
PY

# No exclusion/range arguments: create a complete, self-contained tag bundle.
git bundle create "$PRESERVATION_BUNDLE" --tags
git bundle verify "$PRESERVATION_BUNDLE"    # require complete history, no prerequisites
git bundle list-heads "$PRESERVATION_BUNDLE" 'refs/tags/*'
```

The operator must also retain the refreshed TSVs and the release receipt beside
the bundle. Set `RECOVERY_REPO` to a new empty scratch directory, then recover
into an isolated repository with no alternates:

```sh
git init --bare "$RECOVERY_REPO"
git -C "$RECOVERY_REPO" fetch "$PRESERVATION_BUNDLE" 'refs/tags/*:refs/tags/*'
# This fetch reads the local bundle file, not a network remote.
```

Repeat the per-pin checks above with `git -C "$RECOVERY_REPO"` for every Git
call and the saved TSVs as inputs. Require recovery success, not just successful
bundle creation. Install immutable retention refs in the object-owning canonical
repository before its branches can be deleted; local refs in this clone do not
protect an alternate store from its own GC. Server rules should forbid tag
update/deletion. An offline task cannot attest those rules or server publication.

### 2. Branch deletion, after the retention proof

The operator creates `approved-branches.tsv` in a scratch directory, retaining
the TSV header and unchanged rows for retired `MERGED-CANDIDATE` branches only.
The no-live-ref-name and idle-worktree review may remove candidates, never
automatically add HOLD rows. The two historical-harvest exceptions can be a
separate reviewed batch with the preserving tags named in the table above.
Set `APPROVED_BRANCHES` to that reviewed filename. The following local deletion
block intentionally supports only the merged first batch:

```sh
export APPROVED_BRANCHES
python3 -B - <<'PY'
import csv, os, subprocess
def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()
snapshot = {r['branch']: r for r in csv.DictReader(open('docs/ops/BRANCH-TRIAGE.tsv'), delimiter='\t')}
for row in csv.DictReader(open(os.environ['APPROVED_BRANCHES']), delimiter='\t'):
    name, tip = row['branch'], row['snapshot_commit']
    assert snapshot[name] == row and row['disposition'] == 'MERGED-CANDIDATE'
    assert git('rev-parse', 'refs/remotes/origin/' + name) == tip, 'branch moved'
    subprocess.run(['git', 'merge-base', '--is-ancestor', tip,
                    'refs/tags/archive/process-traces-before-release-prune-2026-11-08^{commit}'], check=True)
    exists = subprocess.run(['git', 'show-ref', '--verify', '--quiet', 'refs/heads/' + name]).returncode
    if exists == 0:
        assert git('rev-parse', 'refs/heads/' + name) == tip, 'local branch differs'
        # branch -d also refuses a branch checked out in a registered worktree.
        subprocess.run(['git', 'branch', '-d', '--', name], check=True)
    else:
        assert exists == 1
PY
```

Deleting a local branch or remote-tracking ref does not delete a server branch.
Remote removal belongs to the later connected owner session after server tag
retention is confirmed. For each **approved, still-identical** server branch,
the exact deletion command is below; the explicit lease refuses a moved tip:

```sh
git push --force-with-lease="refs/heads/$branch:$snapshot_commit" origin \
  ":refs/heads/$branch"
```

No push is part of the present task. Do not delete tracking refs to simulate
remote cleanup, force-delete an unexpected local tip, expire reflogs, rewrite
main, run aggressive GC or prune the shared object store.

### 3. File prune PR, after branch retention/deletion

Materialize the final approved paths from the file-group table in an explicit
newline-delimited `REVIEWED_DELETIONS_FILE` (no patterns, external paths or
directories containing unreviewed live files). Keep deferred groups out. First
implement that group's dependency migration and commit-scoped pin tests; those
implementation changes are future PR work, not changes supplied by this plan.
Set `PRUNE_BASE` to the release-day reviewed main commit.

```sh
git switch -c ops/release-day-file-prune "$PRUNE_BASE"
git rm --pathspec-from-file="$REVIEWED_DELETIONS_FILE"
# Apply reviewed caller/test/allowlist changes and CANONICAL.md/archive links.
python3 -B scripts/repin.py --write registry
python3 -B scripts/repin.py --check
python3 -B -m unittest tests.b5_analysis.test_frozen_files
python3 -B -m unittest tests.test_b5_seal_landing
# Add the affected group's focused modules, one invocation at a time.
# Full suite belongs to CI, never the machine running the blinded 8-worker job.
git diff --check
git diff --stat
git diff -- CANONICAL.md configs/pins/registry.json
git status --short
# Stage explicit reviewed paths, commit, then submit one bounded PR per group.
```

After migration, the frozen-files module must still prove the original identities
from tags rather than fail because main's computation was removed. A complete
suite in CI and an isolated reproduction from the actual release tag precede
merging any science-computation deletion. No real-data reproduction runs from
an agent under the present blinding or machine-load restrictions.

## Disk cleanup checklist — procedure only

These steps belong to Ed/the machine owner after jobs finish and any remaining
block/retention holds lift. No filesystem inventory of either machine was done
here. No estimate of reclaimable space is asserted. Deleting branch names saves
little disk while tags retain history; worktrees, environments, scratch and
verified redundant data copies are the practical space targets.

### Air

- Stop at the current analysis job boundary. Preserve its checkout, custody,
  environment and outputs until the release lead has accepted the receipt and
  designated the archival copy. Do not touch the long-running eight-worker job.
- Review old `jw-wt` worktrees individually. Record branch/HEAD, owner, clean
  status, untracked/ignored files and any active process. Retain uncommitted work,
  environment locks and unique audit artifacts. Only after the pin/bundle proof,
  remove a retired clean worktree with Git's worktree-removal mechanism; then
  prune stale worktree metadata. Do not recursively delete the parent directory.
- Review `/private/tmp` scratch by known task/owner and completion state. Age
  alone is not evidence of disposability. Exclude sockets, live process files,
  locks, unique reports and anything used by running jobs. Use an explicit
  reviewed list; no broad age-based `find ... rm` recipe.
- Remove venvs attached only to retired worktrees after preserving interpreter,
  dependency/lock and toolchain metadata. Keep the exact release environment
  through successful recovery/reproduction. No downloads or installations here.
- For the **jwgold** run, the PI brief says it was already copied to Dropbox
  and verified. Consult that existing verification receipt; do not claim this
  task reverified it. Match source identity and full manifest/checksums, confirm
  the cloud copy is server-resident and recoverable, preserve custody/retention
  records, then let Ed delete only the redundant local copy if the ruling covers
  it. A Finder badge or sync client status alone is insufficient.

### MBP

- Coordinate a desk boundary with the magistrate. Do not disturb collection,
  the analysis job, active worktrees, ledger roots, calibration dependencies or
  sealed outcomes. B5 release does not lift B6/BYTES/ALIGN holds automatically.
- Apply **Ed's stated retention ruling: external SSD plus server-confirmed
  iCloud** before deleting a redundant local archive copy. The SSD is an
  independent second copy; two folders on one disk are not independent copies.
- Through the owner-controlled offload procedure, bind each source archive to
  its full manifest/checksums and custody identity. Verify every file against
  both destinations, including nonempty/size checks and a recovery/read test.
  The cloud verification must establish remote server content, not merely a
  local placeholder, cached file or upload queue. No traversal commands or
  archive path list are supplied here.
- Record verification times, destination volume identity, cloud receipt,
  retention ruling and who verified recovery. Preserve manifests and custody
  records locally or in the designated durable record store. Leave failed or
  uncertain copies in place and retry verification, not deletion.
- Ed removes only the explicitly verified redundant source copies permitted by
  that ruling, then checks free space. Keep both retained copies; no trash
  emptying, cloud eviction or backup pruning as an implied follow-on action.

No current receipt, second-copy state or data-retention exception was validated
by this task. The first next step is to refresh this plan at the accepted B5
release receipt, then run the tag-and-bundle retention proof before any deletion.
