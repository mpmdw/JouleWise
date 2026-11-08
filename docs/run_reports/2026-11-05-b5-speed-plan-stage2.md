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

## Step 11

Each sensitivity pass keeps its complete primary self-check first, then derives
alpha/beta projections and extraction reports independently. The parent consumes
them in pack order, merges consumed archive censuses and retains the original
floor composition and contrast loops. The primary-bound pass still precedes the
wider-bound pass; disclosures and fill still follow both. Caller-owned consumer
and validator seams retain serial execution.

The retained full-size joined window matched all **449 registered outputs,
15 accumulated records and all archive censuses**. This includes the sensitivity
record, step results/output map, all three disclosure files and fill input.
Wall time at 3 workers was **2752.383 → 2607.381 s (5.3% reduction)**. The
[complete ledger](2026-11-05-b5-speed-plan-stage2-11.json) records each output
hash and both matching commitments; the output commitment is
`b18ebf2619b541ca79fbd7de8449c94b45968d03699458d61f648de01318fb92`.

This is one retained-prefix pair under variable load, not a reliable production
gain. Log phase boundaries showed the candidate's internal sensitivity/step-results
block taking longer, while the overall step finished sooner. No causal timing
attribution is established. Disclosure and fill replays remain in the measured
step. This benchmark version did not persist per-pack success/fallback counters
for step 11, so no full-size worker-consumption or kernel-only scaling claim is
made from its total time. The focused successful transport test explicitly
asserts successful worker results. The next slice adds parent-side telemetry.

Focused verification:

- `python3.13 -B -m unittest tests.b5_analysis.test_sensitivity_parallel`:
  1 test passed in 20.056 s, covering successful transport and competing
  project/extract/equality refusals with the same first refusal as serial.
- `python3.13 -B -m unittest tests.b5_analysis.test_sensitivity.PassTests`:
  20 tests passed in 13.660 s (primary checks, numeric equality, independent
  values, context isolation, monotonicity and pass order).
- `python3.13 -B -m unittest tests.b5_analysis.test_step11_null_outcomes`:
  9 tests passed in 9.715 s (D-190 null states through sensitivity, disclosures
  and fill).

An attempted run of the broader `tests.b5_analysis.test_sensitivity` module
completed its 20 pass tests, then was interrupted during `SeamTests.setUpClass`
in the unrelated synthetic fiducial pulse refit to preserve the user's test-time
budget. It is not counted as a passing module. The bounded class above was
rerun to obtain a complete result. No full suite was run.

## Step 5

The emitter opts into independent alpha/beta composition (archive, kept units,
bracket, primary context and ledger snapshot), followed by independent
authenticated bootstrap preparation. The common index/attempt selection,
Gamma authentication, consumer bindings, ordered manifest assembly, provisional
pinset authentication, `build_pinset`, output writes and mint retain their
original sequence. Other composition callers remain serial by default; an
existing session with earlier reads retains serial capability/first-read behavior.

Consumed successful preparations restore the worker's sealed extraction-spec
vocabulary authority before registering its first read row. Both composition
and bootstrap use this same consume helper. Failed workers recompute at the
original cursor, and worker-local producer registry entries are restored in a
`finally` block. No independent authentication is replaced by an earlier result.

The rebuilt joined prefix matched all **288 registered files, 8 accumulated
records and all archive censuses**, including pinset, block-5 input manifest,
copied plans/orders, aggregate floor, D-165 dominance replay and single-count
statement. Wall time at 3 workers was **1467.026 → 1348.711 s (8.1% reduction)**.
The [step-5 ledger](2026-11-05-b5-speed-plan-stage2-5.json) preserves every file
hash, record digest, matching aggregate commitments and parent-received pack
outcomes. The output commitment is
`da09390e94e12f1a4176678721a32d244d7aab59e3e054fb9cc03248643d3157`.
Both composition results and both bootstrap results succeeded and were consumed,
with shares 1/2 in each phase. The serial target dispatched neither preparation;
its prefix retained the already-implemented three-pack bracket scheduling.
This is one loaded-machine observation, not a production forecast.

`python3.13 -B -m unittest tests.b5_analysis.test_producer_parallel` passed
4 tests in 7.684 s: competing authenticated composition/preparation failures,
identical first refusal/partial rows, primary-context rejection, registry cleanup,
and successful vocabulary authority before census replay. An initial 3-test run
failed one assertion because invalid-JSON errors do not include a path; the
assertion now checks the distinct alpha invalid-JSON code versus beta's missing
input. The compared refusal strings were already identical. The parent-side
vocabulary handoff was found in review and regression-tested before benchmarking.

`python3.13 -B -m unittest
tests.b5_analysis.test_mint_kept_units.S10RelativeReportPathTests` passed 3 tests
in 4.745 s, retaining relative manifest bytes and path-escape refusals.

The benchmark now records parent-received pack outcome flags/shares and persists
each verified run snapshot before resetting its files. Incomplete benchmark JSON
has no `digests_equal` success flag. Git child processes now explicitly disable
external excludes, attributes, fsmonitor, hooks and signing as well as global/system
configuration and lazy fetching. These changes do not alter scientific consumers.

## Files and commits

| Slice | Commit | Runtime and focused tests |
|---|---|---|
| 3b | `b61dcf98e` | `context.py`, `dry_run.py`, `pack_parallel.py`; `test_pack_parallel.py` |
| 10 | `3ba677116` | `dry_run.py`, `pack_parallel.py`, `reported_parallel.py`; `test_reported_parallel.py` and shared transport tests |
| 11 | `948d7a2c9` | `sensitivity.py`, `sensitivity_parallel.py`; `test_sensitivity_parallel.py` |
| 5 | This report's final slice | `scripts/emit_floor_mint_pinset.py`, `scripts/mint_floor_artifact_generalized.py`, `producer_parallel.py`; `test_producer_parallel.py` |

Unqualified runtime names above are under `joulewise/b5_analysis/`; test names
are under `tests/b5_analysis/`. The shared synthetic harness is
`scripts/benchmark_b5_pack_parallel.py`. Documentation changes are this report,
`docs/process/b5_speed_plan.md` and the four per-step digest ledgers linked above.
Verification used Python 3.13; Python 3.11 was not run here.

All 14 changed Python files passed a syntax compilation check without creating
bytecode files. Scoped diff whitespace checks passed. The full unittest suite
was not run under the user's explicit busy-machine constraint; the focused
commands and corrected fixture failures are recorded above.

## Handoff and limits

Some Git review/status and local-commit commands omitted the explicit
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_NO_LAZY_FETCH=1` guard.
The shell did not supply those variables by default. Normal Git configuration
lookups by those commands therefore cannot be ruled out; this report does not
certify zero outside-clone configuration access. No such configuration path was
explicitly opened or searched. Benchmark/test commands use the guard, and all
remaining Git commands explicitly set it and disable external excludes,
attributes, fsmonitor and hooks. No measurement path was intentionally supplied
to Git. Git subprocess filesystem access was not traced beyond these guards.

Coordination files are intentionally untouched under the user's explicit fence.
No commit is pushed or promoted. Final promotion still needs the lead's review,
the sibling exception-cleanup item (a) before raising workers, and the authorized
blinded result-equivalence gate. Full-suite execution is explicitly forbidden
in this busy-machine session; only targeted unittest modules are run.
