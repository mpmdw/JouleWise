# PR #708 cold-review fixes

2026-11-10. Local seat `708-fixes`, branch
`ops/2026-11-10-file-prune-708-fixes`, starting at
`2df4fc6ec86a37d3a8449a6e365ff31acfe24fda` with a clean working tree.
Authority: the owner's bounded fixes brief and the
[Fable 5.2 cold review](2026-11-10-file-prune-fable-review.md).
No network, push, model download, analysis pipeline, measurement collection,
or interaction with the running blinded job. No agent delegation or consult.

## Disposition

| Finding | Applied change / evidence |
|---|---|
| F1 | Added exactly `"tests.test_prune_ops": 8.4` to `seconds_by_module`. The requested value is the review's timing observation, not a new performance claim. |
| F2 | Imported `tests.git_fixture.init_git_fixture` and used `init_git_fixture(self.repo, "-b", "main")`. |
| F4 | Qualified the evidence-directory citation and both file citations at the three care-audit locations with the release-prune archive tag. All three distinct Git objects resolve with `git cat-file -e`. |
| F5 | Restored `docs/legacy/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md` byte-for-byte from the archive tag, retaining the ALIGN provenance citation identified by the review. Marked its g1 row KEEP; corrected g1 and stack counts and CANONICAL's retired-material description. |
| F7 | Corrected `joulewise/gensuite.py` to `joulewise/gensuite/`. |
| F8 | Archive manifest reads now have a 10-second subprocess timeout; failed Git reads raise an assertion naming the archive tag and `git fetch --tags`. This is diagnostic text; no fetch runs. |
| F9 | Used an existing v5 config directory for the stage-list example and moved both historical Git object paths into prose. |
| F11 | Described the g3 prototype as temporary scratch, not preserved storage. Its file was not opened or checked. |

Copied `/private/tmp/jwsol/briefs/708-fable-review.md` verbatim to the linked
review file and verified byte equality. The review remains a historical
assessment of the original head; its original counts and CI observations
were not rewritten.

G1 now has **111 DELETE / 695 KEEP** decisions across 806 paths. The full
g1/g2/g4 deletion set is **409** paths, exactly the original set minus the
restored synthesis. All 409 deleted-file blob identities match the archive
tag. The restored synthesis also matches its archive blob (977,219 bytes).
The corrected prune snapshot has **4,762** tracked files; the committed
cold-review and this fixes report bring the fix branch to **4,764**.

## Files touched

- Test support: `scripts/test_timings.json`, `tests/test_prune_ops.py`,
  `tests/archived_campaign.py`.
- Retention: `docs/ops/FILE-PRUNE-G1.tsv` and the restored legacy synthesis.
- Documentation: `CANONICAL.md`, `docs/phase_2/window_runbook.md`,
  `docs/run_reports/2026-11-06-b5-care-audit.md`, and the g1/g3/g4 reports.
- Added records: the verbatim cold review and this fixes report.

## Verification

Python 3.13.18. Unittest modules ran one at a time, with `-B`, a synthetic
`TMPDIR`, and Git system/global config disabled. A supplementary Python audit
guard rejected outside-checkout `/Users/edr` access, real custody access and
network connections; it is not an OS guarantee for native subprocesses.
Git fixture subprocesses were reviewed as synthetic/local operations. No
guard denial occurred.

The exact module command was
`TMPDIR=/private/tmp/jwsol/squeeze/708-fixes/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null python3.13 -B /private/tmp/jwsol/squeeze/708-fixes/tmp/guard_run.py <module>`;
the scratch wrapper invokes `unittest` for that module.

| Selection / check | Result |
|---|---|
| `tests.test_shard_tests` | 8 tests OK, 4.077 s |
| `tests.test_git_fixture_maintenance` | 6 tests OK, 13.446 s |
| `tests.test_prune_ops` | 13 tests OK, 4.987 s |
| Archive-reader focused checks | Three original campaign metadata manifests parse; a tiny tagless Git fixture raises the named assertion; an injected timeout propagates and confirms the 10-second bound. |
| F4 `git cat-file -e` | Evidence tree plus both distinct file targets resolve. |
| F5 inventory / blob checks | 111 / 695 g1 decisions; 409 stack deletions; all deleted blobs match the archive; restored synthesis hash matches. |
| F9 directory checks | Current v5 stage directory and its order manifest exist; both archived historical directories resolve. |
| `PYTHONPYCACHEPREFIX=/private/tmp/jwsol/squeeze/708-fixes/tmp/pycache python3.13 -B -m compileall -q joulewise tests` | PASS; bytecode goes to scratch. |
| `git diff --cached --check -- . ':(exclude)docs/legacy/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md'` | PASS for authored changes. The exact archive restoration retains 29 historical trailing-whitespace lines. |
| Whole-PR whitespace comparison against `origin/main` | Original-head and staged diagnostics are byte-identical: 45 pre-existing warnings in `docs/ops/execution-2026-11-08/AIR-ALTERNATES-GRAPH.tsv`. This historical census was preserved. |
| Targeted documentation / registry metadata checks | Edited/added docs have no dangling decision references. None of the 13 staged paths is a registered pin holder or current file target; no registry regeneration is needed. |

Unittest wall time totaled about 23 seconds. No full suite or quick-tier worker
pool was run, per the brief and the active eight-worker analysis job. No
native MLX tests or hardware validation are required by these test-support
and documentation changes; none is claimed. Sealed lane sources, real
measurement data and custody were not consulted. Coordination state files
were preserved as instructed; no kernel task was registered.

## Handoff and limits

F3 is resolved by the lead's supplied disposition: shard 8 tempdir cleanup
race in `test_evidence_night`, shard 12 known `test_agent_identity` flake.
This seat did not inspect CI logs or independently verify that diagnosis.
F10 census TSVs and F12's MLX timing hint remain unchanged. F6 (PR gate
ledger) remains lead-owned; this offline seat did not edit the PR.

No implementation question remains open. The lead's next exact step is to
review the local fix commit, incorporate it into PR #708, and complete the
gate ledger using the final PR head and the now-committed review path. Full
CI and final merge authority remain with the lead. Nothing was pushed.
