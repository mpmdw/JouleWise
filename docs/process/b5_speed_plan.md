# Block-5 r2 speed plan — post-release only

2026-11-05. Branch `lane/2026-11-05-b5-speed-plan`, base `origin/main`
`92026c184`. **Engineering plan; the <2 h pipeline target is not yet
demonstrated.** The current release remains at `b5/analysis-r2^{}` =
`929fc65c9ce3ff82f0311d28acf76a682edd466f`. Do not merge this lane into its
release checkout, retag it, or restart that release with these changes.

Authority: [D-188](../decision_log.md#d-188-block-5-analysis-rewrite-under-result-equivalence-engineering-window-fresh-analysis-start-ed-2026-11-02),
[D-189/D-190](../decision_log.md#d-189-step-9b-claim-side-bound-non-issuance-is-a-blinded-non-stopping-outcome-ed-ruling-a-2026-11-04),
the [D-188 retrospective](../process_traces/2026-11-04-d188-retrospective/RETROSPECTIVE.md),
and the user's speed-plan brief. The store's design is documented in
`analysis_verified_store.py`, `analysis_member_pool.py`, `analysis_run_cache.py`
and `b5_analysis/parallel.py`. External design/custody paths cited in older
records were not followed. No real measurements, restricted directory, network,
or complete analysis run were used here.

## Cost map and proposed step budgets

“Now” is the user's dry-j measurement: seven workers, nice 5, concurrent load,
approximately 153 minutes. These are elapsed step times, not CPU totals.
The combined <1 minute for steps 2/3 is allocated 0.4/0.1 below solely to make
the schedule additive. Expected times are **budgets for the complete proposed
schedule**, including unimplemented work; they are not measured forecasts from
the changes in this lane. Stage-2 observations are recorded separately below.
All times are minutes.

| Step / owning code | Now | Dominant cost / serialization | Proposed change | Budget 7 / 10 workers | Equivalence risk | Test needed |
|---|---:|---|---|---:|---|---|
| 0 `RunState.prepare_initial` | 2 | Hashing/I/O: archives, original runs, supply census, ledger prefixes; packs serial by construction | **Implemented:** use existing ordered bulk `census_sources`, keeping comparisons/census application in source order | 1.5 / 1.5 | Low; read-ahead must preserve first refusal and partial census | Serial/bulk missing, corrupt, symlink, oversized-file cases; joined step-0 output digests |
| 1 `step_1`, `cli.validate_bundle` | 15 | CPU Python: strict validation, plist/JSON parsing, clock evidence, physics refits; spawned task fan-out already exists | Retain ordered pool and L1 prefilter. Measure hit/miss reasons and serialization cost before further changes; ten workers only after sibling cleanup fix | 15 / 12 | Existing parallel path; more workers can change deadline exposure | Strict-validation/store/refusal tests, firing-free consumed-prefix merge, same-input outputs |
| 2 `step_2`, `reduce` | ~0.4 | L3 hits / small reduction probes; already fans out | Keep current L3 path; no time-saving credit at seven workers | 0.4 / 0.4 | Do not drop refit-dependent stored-summary comparison | Rereduction-field mismatch and cache mutation tests |
| 3 `prepare_tripwires`, `build_context` | ~0.1 | Serial dependency on kept units; structural source replay | Leave tripwires and primary-context checks in place | 0.1 / 0.1 | Refusal identity/position is scientific behavior | Context/removed-reference tripwires |
| 3b `prepare_brackets`, `evaluate_window_bracket` | 27.5 | CPU Python strict/reduction/acceptance/ledger work plus authenticated copy-out; three packs evaluated serially by construction | Parallelize independent pack evaluations, transport their censuses/store deltas, consume alpha/beta/gamma serially. Prefix indexing was measured but **deferred** for lack of reliable wall gain | 12 / 10 | Medium for pack scheduling and deadline/store merging | Every copied-file/selection/census digest; nested ids; first bad source; three-pack serial/parallel refusal matrix |
| 4 `extract_indexed_pack`, `extract_cells` | 14 | Two pack programs already parallel, nested member pools; Python authentication/reduction dominates | Adopt sibling lane's item (a) exception cleanup before increasing workers; leave its fix owned there. Preserve L1/L2/L3 authentication | 14 / 12 | Cleanup, first-pack refusal and unused beta artifacts; independent authentication must remain | Sibling lane's exception cleanup regressions; worker shares, ordered refusals, output digests |
| 5 `emit_indexed_pinset`, generalized mint | 23.5 | Serial emit → mint is a real dependency; producer setup/re-authentication repeats alpha/beta work serially by construction | Parallelize only authenticated producer preparation, then retain ordered `build_pinset` and mint. Investigate hash verification of already authenticated intermediate inputs under D-188 | 18 / 16 | Medium: pinset provenance, independent reader sessions, first producer refusal | Exact pinset, mint, dominance and statement outputs; wrong-report hash, primary/sensitivity separation, producer-order failures |
| 8 `prepare_finalization`, finalizer | 9 | Serial dependency on minted floor; repeated claim-gate/bracket authentication, member CPU work | Retain finalization order; reuse eligible verified leaves and existing member pool. Do not replace finalizer with an earlier program's decision | 9 / 8 | Finalized attachment paths/digests and authentication identity | Finalized manifest/exclusions equality; missing attachment, archive and ledger tamper |
| 6 D-165 closeout | 5 | Serial dependency on finalized manifest; CPU re-authentication and dominance replay | Keep closeout; measure pool/scalar split before claiming scaling | 5 / 4.5 | Zero denominator is a stopping registered outcome here | Dominance replay/ratio bytes and stopping outcome identity |
| 9 `analyze-claims`, engine inputs | 12 | CPU Python repeated authentication/reduction, then serial contrasts and family adjustments | Retain contrasts/family order; use existing verified leaves/member pool. Do not parallelize statistical accumulation | 12 / 10 | Exact floating-point order, floor resolution, refusal position | Engine outputs, multiplicity decisions, refused-floor and not-estimable cases |
| 9b claim-side-bound | ~0 | Serial dependency on claim verdicts; structure-only eligibility and custody reads | No optimization | 0 / 0 | D-189 non-stopping outcome and absent sidecar must be identical | Existing D-189/D-190 tests and comparator presence/step-code checks |
| 10 issuer + `_reported_open` | 15.5 | Alpha/beta serial by construction; each issuer and custody opener independently replays/authenticates | Parallelize both pack computations/replays with isolated staging, then register outputs/roles serially. Shared supply-map/receipt writes must remain ordered | 9 / 8 | Medium: isolation of custody writes and preserving alpha-first refusal | Serial/parallel projection and custody output digests; early alpha failure cleans beta; opener re-authenticates changed bytes |
| 11 `_sensitivity`, disclosures, fill | 29 | Two sensitivity passes (primary-bound equality, then wider bound), each serial project/extract across packs; further disclosure/fill replays | Retain primary-bound equality pass. Parallelize independent pack derivations inside each pass; preserve bound-pass order, parent checks, contrast order and disclosure/fill dependency | 18 / 16 | Medium/high: sensitivity must never reach registered writers; null outcomes and first refusal must remain | Primary vs wider contexts, exact sensitivity/disclosure/fill outputs, D-190 nulls, first failing pack/consumer |
| **Total** | **~153** | | | **114 / 98.5** | **Conditional targets** | **End-to-end equivalence and measured wall time still required** |

Most child programs are Python `main(argv)` calls inside spawned workers, not
one external CLI subprocess per member. Git observations and pool start-up add
subprocess overhead, but the code does not support labeling every long step
“subprocess-bound.” The table's attribution is static inspection plus the
synthetic profiles below; no real dry-j runtime sidecars were opened.

## Critical path and admission conditions

Keep the registered step order:

```text
0 → 1 → 2 → 3 → 3b → 4 → 5 → 8 → 6 → 9 → 9b → 10 → 11
```

Parallelize work *inside* those steps. No later step becomes public or commits
outputs before the preceding step's outcome is decided. Speculative
cross-step execution is unnecessary for this plan and would complicate stop
semantics. Real dependencies include floor → finalization → closeout → claims,
claims → side bound, and primary outputs → sensitivity → disclosures → fill.
The three bracket packs, two reported-energy packs, two producer preparations,
and per-pack sensitivity kernels are serial only by construction.

| Step ends | Seven-worker target elapsed | Ten-worker target elapsed |
|---|---:|---:|
| 0 | 1.5 | 1.5 |
| 1 | 16.5 | 13.5 |
| 2 + 3 | 17 | 14 |
| 3b | 29 | 24 |
| 4 | 43 | 36 |
| 5 | 61 | 52 |
| 8 | 70 | 60 |
| 6 | 75 | 64.5 |
| 9 + 9b | 87 | 74.5 |
| 10 | 96 | 82.5 |
| 11 | **114** | **98.5** |

At seven workers, the proposed main gains are 15.5 minutes in 3b, 6.5 in 10,
11 in 11, 5.5 in 5, and 0.5 in 0: 39 minutes total. This leaves only six
minutes of margin. Ten-worker budgets additionally assume partial scaling of
existing pools, not 10/7 speedup for the entire pipeline. Ten heterogeneous M4
cores are not ten equally fast cores; fanless sustained thermals and the
reported concurrent job make linear extrapolation inappropriate.

Use one process budget for each step and its nested pools. Suggested active
member-work allocations: three brackets 2/2/3 at seven, 3/3/4 at ten; two-pack
work 3/4 and 5/5. Do not create three full-sized member pools. Account for
idle parent processes, resident store copies, serialized store payloads and
spawn RSS as well as active CPU workers. On the 24 GB target, measure peak
memory/swap before accepting ten workers. Explicit `--workers 10` is needed;
the existing automatic default caps at eight. Stage 1 used zero worker
processes for its profiles; stage 2 uses three for synthetic comparisons.
Neither stage changes the running job.

Admission is empirical: after release, meet these step budgets on synthetic
production-dispatch inputs first, then perform the authorized blinded
equivalence run and record complete wall time under stated load/niceness.
If bracket/issuer/sensitivity isolation misses a budget, the <2 h claim remains
unmet. Do not compensate by removing validators, the primary-bound check,
quantile proof, outputs, or registered members.

## Gain per risk and equivalence protocol

1. **Ordered bulk source census (implemented).** Reuse an existing, tested reader
   instead of adding a new authentication cache. At most the source-census
   fraction of the two-minute step is saved. It uses more CPU to overlap I/O.
2. **Three-pack bracket scheduling.** Largest readily identified independent
   serial region; target 15.5 minutes saved at seven. Requires D-188 comparison
   and careful ordered merge of censuses, deadlines, poison, entries and logs.
3. **Two-pack reported-energy scheduling.** Target 6.5 minutes; computation is
   independent, but custody publication has shared state. Stage before merge.
4. **Sensitivity pack scheduling.** Target 11 minutes; more consumers and
   bound-specific contexts make it riskier than brackets/issuer scheduling.
5. **Producer preparation scheduling/hash re-authentication in step 5.** Target
   5.5 minutes. Audit independent authority carefully before avoiding work.
6. **Numerical memoization, broader L3 relocation, acceptance/ledger caches.**
   Investigate after the above. The synthetic bracket profile spends about
   40% in repeated acceptance derivation (Decimal t quantiles/proofs), but
   caching a validator can skip protocol/registry checks, Decimal context
   effects or side effects. No such cache or mathematical change is made here.
   Temporary-copy L3 coverage and other retrospective debts remain owned by
   `lane/2026-11-05-b5-post-release-fixes`; coordinate before touching them.

**Deferred experiment: inventory prefix indexing.** Sorting once and using
binary prefix ranges preserves every tested byte and saves a little CPU, but
the full-size paired wall timings showed no reliable improvement. Keep its
candidate in the synthetic benchmark only. The production bracket module is
unchanged. Stage 1 therefore implemented one confirmed optimization, within
that brief's requested one-to-two range; stage 2 adds the scheduling work below.

The implemented census wiring is byte-preserving engineering:
no arithmetic, leaf eligibility, cache key, scientific policy, comparator
schema or frozen pin changes. Their evidence is copied-file, selection,
census, step-record and output-digest equality, plus first-refusal regressions.
Docs and the synthetic benchmark need no blinded-comparator rerun themselves.
This runtime change still belongs in the final post-release candidate's
equivalence check; this lane's synthetic evidence does not certify real data.

Pack scheduling, hash-based replacement of independent derivation, new caches,
changed read censuses/receipts or relocated stored outputs require the D-188
result-equivalence protocol before promotion. Compare every registered number
exactly, all admit/refuse/select decisions, refusal identity/position and
sidecar absence. Use the existing blinded comparator; report only match or
differing field names. Until release, D-188's r1 reference remains the oracle;
after release also retain r2 as the performance/result baseline. Any reference
disagreement needs adjudication, not a tolerance or comparator exemption.

Hash independence does not mean “trust another program's result.” Each reader
must independently authenticate the bytes it consumes. L1 strict validation,
L2 operative summaries and L3 reduction are eligible only under their existing
exact scalar/tree/session/physics keys. Program scopes may reuse hashes only
under unchanged complete lstat signatures. Hits replay authentication rows and
physics effects at the serial position; failed fills, deadline firings and
unconsumed results must not introduce entries. L3 currently is not path-free;
changing that flag alone would invalidate the premise. Wider-bound sensitivity
contexts must not share primary results by omitting the bound from a key.

## Reproducible synthetic evidence

Run from this clone, with outputs under the task's temporary directory:

```sh
TMPDIR=/private/tmp/jwsol/speed-plan/tmp \
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
python3.13 -B scripts/benchmark_b5_speed_plan.py \
  --baseline 92026c184 --bundle-count 125 --pairs 3 --joined-step0 \
  --output /private/tmp/jwsol/speed-plan/tmp/speed-full-size-pairs.json
```

The benchmark uses the repository's S0/S2 builders, expands timing-only S2
bundles to 125 selected members for the full-size copy/selection workload,
and uses `JoinedHarness` for the real step-0 path over three S3/S3b windows.
Joined step 0 receives an `artifacts/` directory directly through `RunState`;
the complete driver's fixed `restricted/` directory is never created/opened.
No synthetic result is represented as claim-valid or as live hardware evidence.
No default study index is accepted. Baseline functions are extracted from the
specified Git code object; the same input bytes feed both versions. Pair order
alternates, hashes are computed outside the timing interval, and separate
cProfile runs are excluded from wall-time medians. `py-spy` was unavailable.

The full-size timing and digest ledger is recorded in the
[run report](../run_reports/2026-11-05-b5-speed-plan.md): source census
1.372 → 1.085 seconds; joined step 0 4.642 → 3.870 seconds (16.6% faster).
The full-size prefix-index candidate was 2.072 → 2.150 seconds and is deferred.
Every paired digest matched. An initial unexpanded
57-selected-member profile showed whole-bracket ~5 seconds, with ~2 seconds
in acceptance arithmetic, ~1.6 in ledger loading, and ~1.4 in copy/selection.
It uses explicit mock capture/strict-validation seams: it cannot establish
production reduction cost or sustained whole-pipeline speed. Paired timings
vary under the concurrent job; use the complete pair ledger, not the fastest
sample. Full driver completion and a 7-vs-10-worker comparison remain post-release
work, outside this blinded, loaded-machine session.

## Stage 2 implementation measurements (3 workers)

Post-release scheduling work, in the requested order. The earlier measurements
above describe stage 1. Stage 2 uses the committed full-size S10 synthetic
joined window (125/125/107 members), real production-dispatch consumers and
`artifacts/` custody under `$TMPDIR`. It never invokes the real-data entry point
or creates/opens `restricted/`. Git observations are the documented
`JoinedHarness` seams. No worker pin or release tag changes.

| Step | Before / after (seconds) | Wall reduction | Equality evidence |
|---|---:|---:|---|
| 3b — independent pack brackets | 180.781 / 89.707 | 50.4% | All 277 registered files, 5 accumulated records and all archive censuses in the joined prefix match exactly |
| 10 — isolated issuer/opener packs | 433.000 / 205.929 | 52.4%, **cold restart only** | All 442 registered files, 14 accumulated records and all archive censuses match exactly |
| 11 — independent sensitivity pack derivations | 2752.383 / 2607.381 | 5.3%, single retained-prefix pair | All 449 registered files, 15 accumulated records and all archive censuses match exactly, including sensitivity, disclosures and fill |

These are single paired synthetic observations under the concurrent job, not
production forecasts. **Step 10 has no demonstrated warm pipeline gain:** an
initial warm-prefix pair was 131.653 / 256.824 s, the latter including 16.630 s
of benchmark-only retention. A warm-member-pool reuse experiment was deferred
after its serial baseline refused beta custody replay; its cause is unresolved
and its runtime changes are not included. See the report before interpreting
the cold-restart timing. The private pool transports frozen inputs, authentication
rows, archive censuses, deadlines and store deltas; it consumes packs in their
original order and recomputes failed work at its serial position. Mathematical
accumulation and registered writers retain their existing order.

Reproduce each slice with `scripts/benchmark_b5_pack_parallel.py --baseline
<parent-commit> --step <step> --output $TMPDIR/<name>.json`, using Python 3.13,
`TMPDIR=/private/tmp/jwsol/speed-impl/tmp`, `GIT_CONFIG_GLOBAL=/dev/null` and
`GIT_CONFIG_NOSYSTEM=1`. It fixes the process budget at 3, loads no external
index, and checks actual registered-file digests, complete step records and
archive censuses. The detailed method, refusal regressions and limitations are
in the [stage-2 report](../run_reports/2026-11-05-b5-speed-plan-stage2.md);
the [3b ledger](../run_reports/2026-11-05-b5-speed-plan-stage2-3b.json) and
[step-10 ledger](../run_reports/2026-11-05-b5-speed-plan-stage2-10.json), plus the
[step-11 ledger](../run_reports/2026-11-05-b5-speed-plan-stage2-11.json), preserve
the matching commitments and per-file hashes. Full joined production promotion
still needs the authorized blinded equivalence gate.
