# A346 / PR #649 — Phase 1, fix round 2 (2026-11-05)

Status: partial local repair; X3 requires a ruling. Work is on `lane/2026-11-05-freeze-by-commit-p1`, starting at
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
| Cleanup | `8ebff430c` | Delete the committed .pr directory, replace stale report claims, and supply the PR body below for the offline lead. |

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
docs/process/freeze_p1_rebind.md, this report,
docs/run_reports/2026-11-05-freeze-p1-old-digest-audit.json, and deletion of
.pr/freeze-p1.md. The registry itself remains unchanged this round; its stale
row is explicitly recorded as an open X3 blocker.

## Verification

Commands use the existing `TMPDIR` environment, Python 3.13 stdlib unittest,
`-B`, and one test module at a time. No pytest or full-suite command is used.

| Command (prefix `TMPDIR="$TMPDIR"`) | Result |
| --- | --- |
| python3.13 -B -m unittest tests.test_freeze_by_commit.RegistrationAuthorityTests -q | 1 test, OK, 0.218 s |
| python3.13 -B -m unittest tests.test_freeze_by_commit -q | 18 tests, OK, 18.284 s |
| tests.test_repin (explicit safe selection below) | 47 tests, OK, 27.277 s; two real-tree methods unrun. Full-module result BLOCKED. |
| python3.13 -B -m unittest tests.test_digest_pin_census -q | 23 tests, OK, 77.819 s |
| python3.13 -B -m unittest tests.b5_analysis.test_frozen_files -q | 4 tests, OK, 4.632 s |
| GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 python3.13 -B -m unittest tests.test_whole_window_inverted_corner_clamp -q | 33 tests, OK, 119.108 s |
| python3.13 -B -m unittest tests.test_paper_custody -q | 33 tests, OK, 66.406 s; 147 owner-source, 5 grant-policy and 4 refusal-AST mutations killed |

The exact safe repin selection (no test monkeypatches or skip decorators):

```sh
TMPDIR="$TMPDIR" python3.13 -B -m unittest \
  tests.test_repin.RegistryCheckTests \
  tests.test_repin.CommandFamilyTests \
  tests.test_repin.EraRecordTests \
  tests.test_repin.Block5EraRecordTests \
  tests.test_repin.SealedInventoryEraRecordTests \
  tests.test_repin.SealPinsEraRecordTests \
  tests.test_repin.RealTreeTests.test_cli_subcommand_aliases \
  tests.test_repin.RealTreeTests.test_ci_runs_the_repin_check -q
```

Unrun: RealTreeTests.test_committed_registry_kind_p_rows_are_current and
RealTreeTests.test_real_generator_families_pass. A full unmodified
`python3.13 -B -m unittest tests.test_repin -q` was not executed. This does
not meet the requested full-module gate. All independent safe verification
is complete: 158 tests passed across the selections above, plus the separate
one-test X1 check. Total runner-reported test time: 313.744 s (about 5.3 minutes).

Syntax check: compileall.compile_file on 735 explicitly tracked Python files
under joulewise/tests passed, with PYTHONPYCACHEPREFIX under TMPDIR. Git path
selection excludes restricted directories; no broad filesystem walk is used.

All 11 rebind-table digests match current allowed code/metadata bytes;
`git diff --check` passes. The current PR files have no hard-coded temporary
path tied to macOS. Protected coordination files match `801bf6046` exactly.

The full suite is prohibited while the seven-worker analysis job runs. Local
synthetic checks establish neither real-data equivalence nor hardware validation.
Final-head CI, independent delta review, block-5 release and the owning live
reproduction/calibration gates remain open.

## Repeated old-digest audit

The machine-readable audit at
[2026-11-05-freeze-p1-old-digest-audit.json](2026-11-05-freeze-p1-old-digest-audit.json)
records 37 predecessor digests and an exact 995-file search allowlist. The
source/prose/freeze-metadata scan explicitly includes configs/pins/registry.json.
Of 13 matching lines, 11 are the historical rebind table, one is collection-seal
provenance, and one is the stale registry row. That row is an unresolved CI
blocker, not a harmless occurrence. This narrower, reproducible search supersedes
the previous broad-audit/no-live-constraint claim. No assertion is made about
excluded measurement artifacts or unopened configs.

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
fixes and safe requested checks are complete. The ruling remains unanswered.
Next exact step: the lead must choose the authorized X3 route, then resume
registry regeneration and the outstanding full-module gate before delta review.

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
