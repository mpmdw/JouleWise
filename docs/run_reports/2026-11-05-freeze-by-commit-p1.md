# A346 / PR #649 — Phase 1, fix round 2 (2026-11-05)

Status: local repair on `lane/2026-11-05-freeze-by-commit-p1`, starting at
`801bf6046`. This report supersedes the fix-round-1 verification and handoff.
The named branch was already checked out; no replacement branch was invented.
Implementation commit: `2e0528ad8`; pre-PR base:
`92026c1849c0f053e56bdac6110c079211db2c31`.

Read the local agent instructions, Mission M0, stop card (NONE), targeted
status/workspace/queue sections, orchestration, the freeze contract and rebind
record, and the targeted decision-log authority. The user's explicit blinded
repair brief controls this session. No delegation or external integration was
used. Coordination files are lead-owned: this round does not edit RUN_STATE,
TASK_QUEUE, the state kernel, or tests/test_gen_state.py, and registers no tasks.
The lead's `801bf6046` removed the previous coordination-file changes; tests
must not rely on the removed full-ID table.

No network, push, full suite, quiet-machine capture, analysis pipeline or
real-measurement read is authorized. No scientific result or release gate is
claimed. Phase 1 is prepared for landing after block-5 release; F4 remains an
unissued stub pending the combined D-138/A178/L9-ENV-2 acceptance reissue.
Phase 2 and mirror removal remain outside this repair.

## Findings and local commits

| Finding | Commit | Result |
| --- | --- | --- |
| X1 | `b4e55161b` | Cross-check independent full triples against pre-existing origin/main RUN_STATE abbreviations and the original-analysis tag message. RUN_STATE is read with git show, never from the worktree. |
| X2 | `e8a2a4dbf` | Resolve `/tmp` with pathlib for portable scratch repositories. The remaining PR occurrences were historical report prose, replaced here. |
| H1′ | `21cf8fb88` | Load only the origin/main registration blob; require a listed annotated analysis tag's commit/object/tree; retain distinct missing-ref and removed-override refusals. |
| X3 | Pending ruling | Broad registry regeneration and the full repin module read measurement artifacts; see the blocking conflict below. |
| Cleanup | This report's commit | Delete the committed .pr directory, replace stale report claims, and supply the PR body below for the offline lead. |

The F3 regressions use disposable repositories and fake origin/main refs.
They exercise ignored and assume-unchanged registration forgeries, an unreviewed
local tag/registration commit, the retired environment variable, missing origin
history, tag-object/tree tampering, and a legitimate reviewed successor. That
successor's registration is committed after its computation tag, then the test
checks out the computation commit and passes without a worktree registration.
The production entry point no longer accepts a caller-supplied registration.
The F1 frozen-tree tests inspect the PR's HEAD registration blob to validate
proposed metadata before merge; this test helper does not grant runtime admission.

Files changed this round: tests/test_freeze_by_commit.py,
tests/b5_analysis/test_frozen_files.py, joulewise/freeze_by_commit.py,
docs/process/freeze_p1_rebind.md, this report, and deletion of .pr/freeze-p1.md.
The old-digest audit and registry disposition are pending the X3 ruling.

## Verification

Commands use the existing `TMPDIR` environment, Python 3.13 stdlib unittest,
`-B`, and one test module at a time. No pytest or full-suite command is used.

| Command (prefix `TMPDIR="$TMPDIR"`) | Result |
| --- | --- |
| python3.13 -B -m unittest tests.test_freeze_by_commit.RegistrationAuthorityTests -q | 1 test, OK, 0.218 s |
| python3.13 -B -m unittest tests.test_freeze_by_commit -q | 18 tests, OK, 18.284 s |
| python3.13 -B -m unittest tests.test_repin -q | Blocked by the blinding conflict below; no full-module pass claimed. |
| python3.13 -B -m unittest tests.test_digest_pin_census -q | Running |
| python3.13 -B -m unittest tests.b5_analysis.test_frozen_files -q | Pending |
| python3.13 -B -m unittest tests.test_whole_window_inverted_corner_clamp -q | Pending |
| python3.13 -B -m unittest tests.test_paper_custody -q | Pending |

The full suite is prohibited while the seven-worker analysis job runs. Local
synthetic checks establish neither real-data equivalence nor hardware validation.
Final-head CI, independent delta review, block-5 release and the owning live
reproduction/calibration gates remain open.

## Blocking conflict / NEEDS_RULING

Question: how should X3's broad registry regeneration and full repin module be
reconciled with the standing prohibition on any real-measurement reads?

Evidence: `scripts/repin.py --write registry` invokes census.build_index over
all tracked files. RealTreeTests.test_committed_registry_kind_p_rows_are_current
calls registry_stale, whose checked targets include
`analysis/rpt001-v1/dataset.csv`, aggregates, claim indices and report tables.
The real pack generator also reads issued selection evidence. These paths were
identified from code and registry metadata; their contents were not opened.

Options considered: explicitly permit the necessary artifact reads, or preserve
blinding and authorize a bounded registry refresh with synthetic/metadata-only
verification. Recommendation: preserve blinding. Blocked work: broad registry
regeneration and a truthful full, unmodified tests.test_repin result. Independent
fixes and safe requested modules continue while the ruling is pending.

## PR body for the lead (offline handoff)

Prepare Phase 1 of freeze-by-commit for landing after block-5 release. F1 checks
historical collection/analysis Git trees; F7 uses content-based Python test pin
locations. Estimator arithmetic and scientific outputs are unchanged by this PR.

F3 admission now reads only the merged, reviewed registration at
`refs/remotes/origin/main:configs/analysis/b5/freeze_commits.json`, at the same
trust level as the former origin/main gate. A clean analysis checkout must equal
the peeled commit of a listed annotated `b5/analysis` or `b5/analysis-r<k>` tag,
with matching tag-object ID and tree. Missing origin/main and the retired runtime
override refuse distinctly. Worktree/index tricks and unreviewed local tags grant
no authority.

For a future ruled correction, cite the decision and old/new trees, create its
annotated successor analysis tag, then review and merge a registration update to
main listing that tag's full object/commit/tree triple. Make the merged main ref
and tag available locally, then run from the clean tagged computation checkout.
The registration commit follows the computation commit, resolving self-reference.
The loader itself performs no network access.

Independent full triples cross-check pre-existing upstream literals and tag
objects. Scratch-repository regressions cover both worktree forgery methods and
the legitimate successor route. F4 remains explicitly unissued; block/role
selection for future blocks and Phase 2 pruning remain open. The exact verification
ledger, X3 blocking conflict and remaining release gates are recorded above.
