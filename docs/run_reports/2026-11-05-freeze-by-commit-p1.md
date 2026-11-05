# A346 / PR #649 — Phase 1, fix round 1 (2026-11-05)

Status: local fixes prepared on `lane/2026-11-05-freeze-by-commit-p1`.
Implementation commit: `2e0528ad8`; implementation base:
`92026c1849c0f053e56bdac6110c079211db2c31`. The branch was already checked out
at intake. Git metadata is writable and the finding fixes are committed.
No push, network, full suite, analysis pipeline or real-measurement read was
performed. This replaces the earlier report's obsolete read-only-Git claim.

## Intake and scope

Read the stop card (NONE), current status/workspace and queue, Mission M0,
AGENT_PLAN, orchestration, F1–F7, the rebind record, RUN_STATE 145–146/165,
and D-188–D-190. The user explicitly selects this bounded [AGENT] repair over
ordinary queue work and authorizes local commits. The existing untracked
`.pr/freeze-p1.md` was the requested PR-body draft; it is now updated/tracked.
No new branch was needed. No delegation, peer consult or external integration
was used. No advisor-visible scientific state changed.

The prior implementation changed Git identity and pin-location machinery,
not estimator/result arithmetic. Phase 1 still lands only after block-5
release. F4 remains an unissued stub pending the combined D-138/A178/L9-ENV-2
acceptance reissue. Phase 2 and mirror removal remain outside this repair.

## Finding dispositions and commits

| Finding | Commit | Result |
| --- | --- | --- |
| B1 | `1da9e978d` | Retired the worktree-byte pin/test on test_frozen_files.py under F1; added the clamp module to the rebind table. Final old-digest audit described below. |
| H1 | `ef2ff5a78` | Strict F3: exact registered analysis HEAD only; removed runtime descendant ledger and environment authority override; forge attempts refuse. |
| M1 | `f604e1655` | Documented r2-only paper/fill operation for all current families; TODO A346 for block/role selection; origin/main parameter honors its name; misleading custody test renamed. |
| M2 | `8a0357e8c` | Independent full literal commit/tag/tree pins cross-check RUN_STATE item 146 and all three existing annotated tags. |
| L1 | `6ef50adc4` | Warn when a content pointer is absent; family rewrite prints the registry-refresh command; regression covers it. |
| L2 | `25aa848d2` | Collection import check reads b5/collection as well as active analysis. |
| L3 | `2dd765162` | AttributeError becomes a closed identity-anchor refusal, with regression. |
| L5 | `36337b39b` | FrozenFilesTests clears/restores the exported registration variable in setUp. |
| L4 | This report's refresh commit; exact ID in .pr/freeze-p1.md | Replaced obsolete branch/commit/pytest claims; reconciled actual files and gates. |

H1 chooses the review's simpler alternative: F3 already requires a new
`b5/analysis-r<k>` tag for a ruled fix. A local ruling document, descendant
ledger, new local tag or arbitrary authority commit cannot grant admission.
Runtime rulings therefore cannot bypass decision-log resolution: that route
is gone. A successor must cite the owner's decision in docs/decision_log.md,
record old/new trees and receive a reviewed registration. The checkout's
registration is the sole metadata source, checked independently in M2.

M2 provenance limitation: item 146 originally printed only abbreviated
collection identity; item 165 named abbreviated r2; the original-analysis
annotated tag message printed its full commit/tree. Full tag-object literals
were not all present in those records. This fix adds a clearly labeled
clerical full-ID expansion to ruled item 146, derived from the already-existing
local annotated objects, and pins all nine values independently in the test.
It does not claim that table predated this fix or issue a new science ruling.

## Post-release operation (M1)

After landing, **paper and fill runs must run from a clean b5/analysis-r2
checkout**, including build_results_fill_input.py, issue_reported_energy.py,
produce_b5_disclosures.py, compare_b5_recompute.py and open_paper_input.
Main and unregistered descendant checkouts refuse analysis_descendant_unruled
for every currently supported custody family. A later correction needs the
strict-F3 successor procedure above. An exported
JOULEWISE_B5_FREEZE_REGISTRATION_COMMIT now refuses and must be unset.

TODO A346: select registration by block or supply role before enabling other
blocks at this seam. The relevant role contracts are not mapped yet; inventing
a mapping in a small review repair would be unsound. require_origin_main=True
now independently requires a positive containment result. Paper custody uses
require_registered_analysis=True instead, retaining the clean-tree gate.

## Files touched in this fix round

- Production/tooling: joulewise/freeze_by_commit.py, identity_pins.py,
  paper_custody.py; configs/analysis/b5/freeze_commits.json; scripts/repin.py.
- Tests: tests/test_whole_window_inverted_corner_clamp.py,
  test_freeze_by_commit.py, test_paper_custody.py, test_repin.py;
  tests/b5_analysis/test_frozen_files.py.
- Records: .pr/freeze-p1.md, docs/process/freeze_p1_rebind.md, this report,
  RUN_STATE.md, TASK_QUEUE.md and docs/process/state_kernel.json.

The kernel's A346 status is now partial; its note records the fix and open
gates. TASK_QUEUE generated rows were regenerated from it; RUN_STATE adds a
hand-authored handoff and item-146 full-ID table. This is actual fix-round
bookkeeping, not a claim that the original implementation commit changed the
kernel or queue. PROJECT_STATUS is unchanged because scientific/advisor-visible
state did not change.

## Verification

All tests use Python 3.13 stdlib unittest, one process/module at a time, with
`TMPDIR=$TMPDIR` (the existing /private/tmp/jwsol/freeze-p1-fix1/tmp).
No pytest, package installation or full-suite command was attempted this round.
Final serial checks are recorded here; no unrun gate is marked green.

| Command (common prefix TMPDIR=$TMPDIR) | Result |
| --- | --- |
| python3.13 -B -m unittest tests.test_whole_window_inverted_corner_clamp -q | 33 tests, OK, 117.734 s; final rerun pending |
| python3.13 -B -m unittest tests.test_freeze_by_commit -q | 14 tests, OK, 9.279 s |
| JOULEWISE_B5_FREEZE_REGISTRATION_COMMIT=ffffffffffffffffffffffffffffffffffffffff python3.13 -B -m unittest tests.b5_analysis.test_frozen_files -q | 4 tests, OK, 4.599 s |
| python3.13 -B -m unittest tests.test_paper_custody -q | 33 tests, OK, 69.165 s; 147 owner-source, 5 grant-policy and 4 refusal-AST mutations killed |
| python3.13 -B -m unittest tests.test_digest_pin_census -q | Final serial run in progress |
| python3.13 -B /private/tmp/run-freeze-p1-repin.py | Pending; module loader excludes two unsafe real-tree tests |
| python3.13 -B scripts/gen_state.py --check | PASS |
| git diff --check | PASS before record refresh; final check pending |

Additional pre-final freeze tests passed (12 tests, 4.873 s). Runner times,
not wall-clock estimates, are used for the total. The final ledger update will
record total test time, syntax and the last whitespace check.

Safety exclusions from test_repin: the real registry freshness test hashes
archived measurement outputs (including analysis/rpt001-v1 and paper/trace
results). The real generator-family test can resolve off-clone /Users/edr
paths and consume issued selection evidence. Both are excluded before their
bodies run. Remaining synthetic tests and safe real-tree CLI/workflow checks
run. This is an explicit verification limitation, not a full-module pass.
No whole-tree digest census was run: it indexes measurement artifacts.

## Old-digest audit (B1)

Final audit update pending. Preliminary search covers every old file digest
for paths changed by the PR, from the pre-PR base, r2 and initial implementation
commit (not just Kind-P census targets). It searches tracked regular source,
Markdown and config JSON files, including PR/record content. It excludes
measurement artifacts, restricted directories and symlinks. The final report
will record all matches and their dispositions. No claim is made about
unopened measurement/restricted content.

## Remaining gates and next action

Local targeted results do not establish real-data equivalence, reproducibility,
release, final-head CI, independent delta review or the cold admission pass.
The previous executing review found the issues addressed here; its final delta
review remains the owning lead's next step. The full suite remains prohibited
in this session. No quiet-machine or hardware gate was attempted.

Next: complete the final local verification ledger and commit map, then hand
these local commits to the PR #649 lead for delta review. Keep A346 partial,
F4 and block/role selection open. Land only after block-5 release and the
remaining owning-lead gates. Do not push from this offline lane.
