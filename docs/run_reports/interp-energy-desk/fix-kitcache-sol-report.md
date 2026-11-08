Committed locally on `fix-kitcache`; working tree clean, nothing pushed.

- `d0cc5b7c2`: deleted both caches, retained batching/deduplication/working-first checks, fixed worktree alternates, imported Opus witnesses, and reverted generation symlink refusals. The pre-existing receipt path guard remains.
- `76be382aa`: recorded findings, timings, and handoff.

Touched the kit and receipt code, benchmark, two test modules, two generated provenance JSONs, and report/timing files.

Verification passed: **187 targeted unittest tests**, sequentially across six modules; `compileall`; pending/filled byte equality; and all 221 mutation refusal messages. All three Opus witnesses failed before the fix and pass afterward. `align_v4_kit.py --check` reaches the existing R0/R1 placeholder refusal without generated drift.

Before → after generation: **0.083 → 0.049 s** pending, **0.085 → 0.047 s** filled. Other rows slowed on this busy host, including receipt validation: **0.139 → 0.217 s**. No receipt speedup is claimed.

Exact commands, results, file list, and samples are in the [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-fix-kitcache/docs/run_reports/2026-11-08-fix-kitcache.md).

No blocking questions. Timing generalization and native readiness remain unverified. The lead’s next step is review/cherry-pick, exact-candidate receipt rebinding, and existing native gates. Coordination state was untouched.