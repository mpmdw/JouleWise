# Under-90 item 5: ordered MINT authentication prefetch

2026-11-06; branch `sol/u90-item5`; starting head `76f3386ec`.

The explicit item-5 brief selects this bounded AGENT task over the older
generated queue. Mission M0 intake found no active stop card. The worktree
was initially clean. D-188 and the existing pack/producer/reported/sensitivity
implementations were inspected. No other agent was used.

## Change

Extract the original per-producer body of `_authenticate_v2_inputs` into
`_authenticate_v2_producer`. The original serial path invokes that body with
the same evidence core and shared evidence-root map. Eligible block-5 calls
compute both producers ahead with `pack_parallel.pack_map`; the original
producer loop consumes them in order. Failed outcomes recompute the original
body through `pp.consume` at that producer's position.

`joulewise/b5_analysis/mint_parallel.py` supplies the importable worker,
installs/restores its producer's process-local registry entry, and returns
the inputs, root bindings, archive census, governed-spec paths and pinned
producer identity. At consumption, spec authority precedes session-row replay,
and the reached producer's archive census is merged. The isolated core's
unloaded dataclass modules cannot be pickled directly: transport uses the
importable original core's identical component/member definitions and copies
every field without changing numerical values.

Keep serial execution for caller validator seams, caller sessions with earlier
reads, legacy manifests, overlapping root IDs between producers, and all normal
`pack_map` fallback conditions. Shared root IDs retain their original serial
cross-producer checks. Capture mint-owned session eligibility before its prefix
reads and carry it through recursive indexed dispatch. The CLI now passes its
existing `validate_bundle` function directly, allowing process transport rather
than transporting its previous equivalent local lambda. The pack environment
switch remains owned by `pack_map`.

No estimator, cache-key, registry pin, state-kernel or registered-output change
is intended. No forbidden bookkeeping file was edited.

## Verification

**Runtime verification is blocked, not passed.** Each requested module was
attempted individually with exactly this form and the supplied TMPDIR:

```
TMPDIR="$TMPDIR" nice -n 19 taskpolicy -b python3.13 -B -m unittest MODULE
```

| Module | Result |
| --- | --- |
| `tests.b5_analysis.test_mint_parallel` | wrapper exited 70 before Python |
| `tests.b5_analysis.test_producer_parallel` | wrapper exited 70 before Python |
| `tests.b5_analysis.test_mint_kept_units` | wrapper exited 70 before Python |
| `tests.b5_analysis.test_pack_parallel` | wrapper exited 70 before Python |

All attempts reported `nice: setpriority: Operation not permitted` and
`taskpolicy: setpriority(): Operation not permitted`. No lower-priority control
was removed and no sandbox bypass was attempted. No test code executed. The
new module received additional static-review edits after its initial blocked
attempt; it still needs its first runtime execution.

Static checks passed: AST syntax parsing of the three Python files, and
`git diff --check`. A separate AST comparison confirms the extracted producer
body matches the original body after only relocating the manifest-row lookup
and final result-map assignment. This is limited structural evidence, not a
runtime equivalence proof.

The new fast synthetic tests cover success (all returned fields, roots, session
record rows/counts/order, archive census), competing producer failures and
partial state, input-transport fallback, result-transport fallback, validator
seams, integrated input-loop scheduling, earlier-read fallback, and overlapping
root IDs. They replace expensive component/bracket science with small test
functions, while retaining the real producer control flow, archive checks,
plan/sidecar pins, fresh-core dataclass transport and spawned pack machinery.
The requested kept-unit tests remain the focused arithmetic regression gate.

No real measurement data, real restricted directory, real driver, full-size
synthetic pipeline, hardware measurement or network was used. The canonical
full suite was intentionally not run under the explicit targeted-test rules.

## Expected saving and open risk

Using the brief's approximately 347-second authentication span, balanced
producer work could ideally take approximately half as long: about 170 seconds
saved, taking the approximately 575-second mint toward 400 seconds and the
1,110-second step toward 940 seconds, before spawn/transport overhead and CPU
contention. This is an estimate from supplied synthetic profiling, not a new
benchmark. Worker sharing, cache duplication and producer imbalance can reduce
the saving.

The patch is **PROVISIONAL / runtime unverified**. The tests must establish
actual spawned transport, session replay, registry restoration and arithmetic
compatibility; static review alone cannot establish D-188 equivalence. The
owning lead must next run the four commands above in an environment that permits
the required priority controls, then perform the full-size synthetic comparison
and timing in the cloud. Any real-data equivalence work remains lead-owned.
