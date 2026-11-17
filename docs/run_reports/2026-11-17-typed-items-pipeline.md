# Typed RUN_STATE and pipeline landing, 2026-11-17

The lead assigned the Tier 1 build directly. Mission M0 found no active stop
card. The build followed the typed-items brief, spec and pipeline policy. The
legacy pointer source and the ratified charter bytes carry through from the
base. The lead owns the cutover after merge.

The writer allocates from a freshly fetched commit in a detached worktree,
retries stale pushes and spools refused requests on Git failures. CURRENT v2
projects recorded open statuses. Both fences workflows check typed records.
The landing installs PIPELINE and retires the October gate policy and the v3
charter candidate. The ledger preserves the Appendix A seed rows, including
the #800 batch with unfilled per-round counts.

Verification used the requested Python 3.13 acceptance suite, Python 3.11
`run_state_items.py check`, `gen_state.py --check`, the charter-registry and
documentation-freshness tests, and `git diff --check`. The A6 regression
interleaves two temporary clones at push time. A8 uses a local bare-repository
hook to advance the ref after each push advertisement. Ordinary hook
refusals are Git failures. Full shard verification runs on GitHub because
the local suite includes process-signaling tests.

The first CI run exposed Git 2.56's distinct stale-ref response and the
relaunch prompt's 25-line limit. The writer recognizes both Git responses
and verifies the remote ref advanced before retrying either. The prompt
keeps the new writer instruction on its own line within the existing limit.
The full matrix also caught the fixture initialization guard. The tests
use the repository's shared helpers to disable detached Git maintenance.

The suite checks 42 named acceptance scenarios. In R18, the seven transitions
to DRAFT are exercised at the replay boundary because the wire schema excludes
DRAFT as a target. The validator also checks that those inputs fail the schema.
The live cutover stays pending. After CI, the lead routes one cross-family
review. After merge, the lead runs `python3 scripts/run_state_add.py init` on
main and confirms that `python3 scripts/run_state_items.py check` exits 0.
