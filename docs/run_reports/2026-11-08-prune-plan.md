# Release-day prune preparation

Task branch: `ops/2026-11-08-prune-plan` (already created and clean at intake).
Base: `4e7e878a151d919faf56bb9131af1fcca4b7be75`, also the local `origin/main`.
The date follows the assigned branch/brief. This is a documentation-only plan,
not execution of a prune or a release.

## Work and findings

Read repository intake/stop-card, queue, Mission M0, source-of-truth map,
freeze-by-commit policy, targeted D-188–D-191 authority, existing prune report,
canonical map and relevant orchestration rules. No stop card was active. The
direct PI assignment is bounded `[AGENT]` planning work; no queue task was
registered. User instructions expressly leave coordination state unchanged.

Prepared:

- [PIN-INVENTORY](../ops/PIN-INVENTORY.md): scientific anchor table, existing
  tags, digest-family inventory, source-held digests, live/provisional status,
  actual seal-record commits and explicit unavailable-history gaps.
- [PRUNE-PLAN](../ops/PRUNE-PLAN.md): branch disposition, coupled file retirement
  groups, CANONICAL changes for future PRs, ordered tag/retention/deletion/PR
  commands, standalone-bundle recovery and Air/MBP cleanup procedures.
- [TAG-PINNING](../ops/TAG-PINNING.md): future driver identity contract and
  synthetic Git regression matrix; no frozen B5 implementation changes.
- Five supporting TSVs: `PIN-COMMITS.tsv`, `TAGS-TO-CREATE.tsv`,
  `BRANCH-TRIAGE.tsv`, `PIN-UNRESOLVED.tsv`, `SOURCE-DIGESTS.tsv`.

The source/Git-object census retains 1,131 distinct resolvable commits, including
900 from RUN_STATE, with 203 proposed retaining tags. It supplements the existing
27,160-literal tests/configs registry with 107 source SHA-256 occurrences in 27
files. Narrative references are conservatively retained; they are not all
scientific execution pins. The 754 unresolved textual candidates also contain
dates, activations, digest fragments, external model revisions and test values.

Five explicit commit citations do not resolve locally: `4cb222a19` (B5 final
ledger-only head), `050aaad13`, `498ad1d0`, `6bcd90a3`, `9a6f8880`. The inventory
gives their exact RUN_STATE locations and provisional future tag names. They
are excluded from executable tag targets. Recovery/owner disposition is needed
before claiming complete retention or retiring affected copies/records.

B6 and BYTES final ledger lines now resolve, despite the early UNRECORDED text
in their addenda; appended records supersede that pending status. BYTES's
registered analysis digest, manifest digest and registration digest were
recomputed from the retained pass-2 lane and match the recorded values. ALIGN v4
pins reside on the measurement lane and remain PROVISIONAL; no live gate was
inferred from their presence.

The branch table contains 1,482 locally recorded remote refs: 687 merged
candidates, 190 held refs (including symbolic origin HEAD), 605 held unmerged
refs. All require operational review before deletion; no server freshness,
worktree inventory or owner activity was checked. Two frozen harvest branches
are separately identified as possible pin-covered retirements after release.

Tags in this alternate-backed clone cannot protect the shared object store
from its own GC. The plan therefore requires a complete standalone Git bundle,
isolated recovery and retention refs in the object-owning repository. It keeps
main history and the original archive promise intact. Existing main-ancestry
checks are not silently changed to tag checks.

## Verification

| Command/check | Result | What it established or caught |
|---|---|---|
| `python3.13 -B -m unittest tests.b5_analysis.test_frozen_files` | PASS, 4 tests, 0.290 s | Current sealed/rebound source and seal-record pins remain valid |
| `python3.13 -B -m unittest tests.test_b5_seal_landing` | PASS, 9 tests, 2.230 s | Git-object seal landing and tiny constructed histories; no real measurement inputs |
| Read-only census using `git cat-file --batch-check`, `rev-parse`, `for-each-ref`, `rev-list`, targeted `git show` and source-text extraction | PASS for locally resolvable set | Found side-lane pins and five unavailable commit citations; no tag creation |
| `python3 -B /private/tmp/jw-prune-verify.py` (temporary validation script) | PASS for original 1,129 mapped commits / 203 targets, 687 merged candidates, 107 source digest locations | Per-commit `git merge-base --is-ancestor` against **proposed target commits**, exact branch snapshots and valid tag names; this is not evidence that proposed tags exist |
| Two additional `git merge-base --is-ancestor` checks against baseline | PASS | Initial and last-change seal-record commits, derived via the record's Git-log procedure; final total 1,131 |
| Shell `bash -n`, embedded Python AST parsing, local Markdown link checks | PASS: 6 shell blocks, 3 embedded Python blocks, 16 local links at validation | Runbook syntax only; mutation commands were not executed |
| Final staged `git diff --check` and scope review | PASS | Only new ops documentation/TSVs and this report |

Initial branch validation caught that `%(refname:short)` abbreviates symbolic
`refs/remotes/origin/HEAD` to `origin`. The table was corrected to explicit
`HEAD`/HOLD and verification changed to full ref names. No branch was deleted.
The merged-candidate count fell from 688 to 687. The final two seal-record rows
were separately verified after the main inventory check; no source changes
required rerunning the focused unit tests.

No check computed or changed a science number; these are source/metadata gates.
No full suite, analysis pipeline, native MLX test, model download, network call,
measurement or quiet-machine task ran. No code/tests changed, so no native MLX
tests are required for this documentation commit. Later runtime retirement must
run its owning lane's Metal tests outside this sandbox. Full CI belongs to the
eventual implementation/prune PRs, not the busy analysis machine.

## Scope, uncertainty and handoff

Only `docs/ops/` and this dated report were written in the repository. No edits
to RUN_STATE, TASK_QUEUE, the state kernel, `tests/test_gen_state.py`, CANONICAL,
registrations, frozen code, digests or existing tags. No cleanup, branch
retirement, retention-tag creation, bundle creation, push, merge or deployment
was performed. Temporary
metadata scripts under `/private/tmp` only handled source/Git metadata. No
delegation or cross-model consult was used; final checks remained with this
session. Fresh review is still required before the later destructive prune PRs.

External data roots were not opened, listed, statted or searched. Absolute data
paths in source were treated only as text. Air/MBP disk state, Dropbox's existing
jwgold verification, SSD copies, server-resident iCloud content, server branch
freshness and tag protection were not validated. The disk checklists state Ed's
retention conditions without claiming those conditions currently hold.

The actual accepted B5 release commit/receipt is deliberately unspecified.
B6/BYTES analysis identities and ALIGN registration/live gates remain owned by
their leads. The plan does not make old computation removable merely because
B5 has released: format readers, current imports, issued artifacts, kernel
pointers and live delivery branches need their migration/disposition first.

Next exact step: after the lead accepts the B5 release receipt, recover or
disposition the unavailable-history citations, refresh the TSVs and archive
target at release-day main, and run PRUNE-PLAN step 1 (tag creation plus bundle
and isolated retention proof). Branch/file deletion comes only after that.

Commit: this report is included with the ops documents in the local
`docs(ops): prepare pin-preserving release-day prune` commit; the final handoff
provides its resulting SHA. No push is authorized or performed.
