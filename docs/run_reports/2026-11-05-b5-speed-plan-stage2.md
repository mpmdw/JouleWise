# Block-5 speed plan, stage 2 — post-release engineering

Authority: the user's stage-2 brief and `docs/process/b5_speed_plan.md`;
D-188, D-189 and D-190 remain unchanged. Work is on
`lane/2026-11-05-b5-speed-plan`. The release tag is untouched. No network,
real measurement pipeline, restricted directory, quiet-machine operation or
coordination-state write is authorized or used. The worker pin is unchanged.

## Evidence method

`scripts/benchmark_b5_pack_parallel.py` restores the committed S10 synthetic
production-dispatch windows (125 ALPHA, 125 BETA, 107 GAMMA members). It uses
`JoinedHarness`'s existing synthetic Git observations, the real `RunState`,
`StepRunner`, validators, reductions and consumers. Custody is `artifacts/`
under `$TMPDIR`; the public driver's fixed `restricted/` entry point and
`scripts/run_b5_analysis.py` are never invoked. A path guard rejects blinded
locations. Git global/system config is disabled and lazy fetching is disabled.

All timing runs use 3 workers under the user's reported concurrent seven-worker
job, whose state and data are not inspected. Baseline functions come from Git
code objects. Comparisons include every registered output's actual SHA-256,
every accumulated step record and each archive census. Hashing is outside the
measured step. These are synthetic engineering results, not live validation
or proof of the two-hour production target.

## Step 3b

Independent pack brackets use a spawned pool with a shared process budget
(1/1/1 at 3 workers; the existing allocation rule at other counts). Each
consumed pack replays its authentication rows and archive census. Deadlines,
physics, poison and verified-store additions use the existing member-pool
consumption rules. Failed computations run again at their serial position,
preserving the original refusal and partial census. No bracket arithmetic,
acceptance rule, copied member or primary-context check is removed.

Private transport preserves frozen mappings, selected-window capabilities and
the context builder's replay callback. Roster identity bindings are restored
within the transported object graph. It changes no file format or cache key.

The full-size S10 joined prefix through 3b matched all 277 registered files,
5 accumulated records and all archive censuses. Step wall time at 3 workers:
180.781 → 89.707 s (50.4% reduction). The matching output commitment is
`68c2360c593b33e5a6fc97103408be676e1ff59084bedebdba97dafa22f48d52`;
the [complete digest ledger](2026-11-05-b5-speed-plan-stage2-3b.json) records
the output, record and census commitments before and after, plus every file hash.

Verification: `python3.13 -B -m unittest tests.b5_analysis.test_pack_parallel`
passed 5 tests in 45.474 s, including alpha-before-beta bracket refusal with
identical partial censuses/records, ordered authentication reads, unused-worker
deadline isolation, and transport of selected-window/issued-roster capabilities.
Two earlier test runs exposed incorrect fixture assumptions in the new
round-trip test (ordinary S0 has no source replay; recovered S0 is not hazard
admitted); the test now transports a genuinely issued roster and preserves the
real replay refusal. No production admission check was bypassed to make it pass.

## Step 10

Each pack computes its issuer and independent custody opener in a private
directory containing copies of the prior authenticated outputs. Receipt,
inventory and role-census paths retain the same relative names. The driver
re-authenticates public commitments, then publishes/registers alpha followed by
beta and adopts their original log counters. Unconsumed staging is removed;
a computation that escapes recomputes through the original serial call.
The benchmark applies the existing `JoinedHarness` synthetic Git observations
inside spawned openers as well as the parent; production receives no Git seam.

The initial fresh-pool candidate matched every digest but regressed from
131.653 to 256.824 s (including 16.630 s of benchmark-only input retention).
A cold restart, which lacks the original prefix's warm member workers, measured
433.000 to 205.929 s and also matched. That difference exposed an important
timing confound: a serialized store snapshot does not preserve a warm process
pool. Neither observation establishes a production gain. An experiment borrowing
the warm member pool was **deferred**: its full-prefix serial baseline admitted
alpha, then refused beta's custody replay (`paper_custody_validator_refused`),
with the same issued beta projection digest. The cause is not established. No
timing or equivalence claim is made for that failed experiment, and its runtime
changes are absent from the final implementation. Keep the bounded fresh pack
pool and the existing memo-shipment rules. No memo key, validator or parser
policy changes. Retention is now opt-in (`--retain-prefix`).

The successful cold-restart pair matched all **442 registered files, 14 step
records and all archive censuses**, including projections, basis, registered
inputs, receipts, inventories and role censuses. The
[step-10 ledger](2026-11-05-b5-speed-plan-stage2-10.json) preserves every output
hash and matching commitments. Both real spawned issuer/opener results were
`ok`, with member shares 1/2 at a configured budget of 3. This is a 52.4% cold
restart reduction, **not evidence of a warm pipeline speedup**; the initial warm
prefix observation regressed even after allowing for retention overhead.

`python3.13 -B -m unittest tests.b5_analysis.test_reported_parallel` passed
3 tests in 49.755 s: simultaneous issuer/opener failures preserve the first
pack, every staged/published byte and log counter matches serial, an escaped
staging computation reruns serially, and the opener refuses changed report
bytes. An initial test-fixture collision (identical addressed basis/receipt
payloads) was corrected with distinct synthetic documents, without changing
the production collision guard.

The shared transport/refusal module was rerun after staging cleanup and opaque
argument fallback changes: `python3.13 -B -m unittest
tests.b5_analysis.test_pack_parallel` passed 6 tests in 236.609 s under the
concurrent machine load.

## Handoff and limits

Coordination files are intentionally untouched under the user's explicit fence.
No commit is pushed or promoted. Final promotion still needs the lead's review,
the sibling exception-cleanup item (a) before raising workers, and the authorized
blinded result-equivalence gate. Full-suite execution is explicitly forbidden
in this busy-machine session; only targeted unittest modules are run.
