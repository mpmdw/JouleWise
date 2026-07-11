# P2-040 Reducer-Version Compatibility Fix

Date: 2026-07-10  
Branch: `impl/p2040-remainder`  
Commit authority: none; changes remain uncommitted

## Scope And Finding

Review found one blocker: the committed remainder added governed field
`measurement_quality.runtime_cleanup_ok` while continuing to emit reducer
version 0.3.0. Strict comparison therefore invalidated summaries created
before that field existed but truthfully claiming the already-frozen 0.3.0
shape.

## Fix Status

- COMPLETE — `SUMMARY_REDUCER_VERSION` is 0.3.1.
- COMPLETE — 0.3.1 strict comparison is exact.
- COMPLETE — 0.3.0 comparison projects the fresh provenance version to 0.3.0
  and permits absence of exactly the paths in `ADDED_SINCE_0_3_0`, currently
  only `measurement_quality.runtime_cleanup_ok`.
- COMPLETE — stored 0.3.0 values and all other fields remain exact claims.
- COMPLETE — legacy, 0.2.x, missing/malformed, and unknown dispatch arms are
  unchanged.
- COMPLETE — tests pin passing 0.3.0 omission, failing 0.3.1 omission,
  failing tampered 0.3.1, and failing 0.3.0 absence outside the named set.
- COMPLETE — D-030 has an append-only amendment requiring a reducer patch
  bump for every governed output-shape addition and extension of the prior
  frozen version's named absence set; frozen versions are never reused.

## Dispatch Table

| Recorded summary class | Strict comparison |
|---|---|
| Frozen pre-D-033 legacy identity, provenance absent | Existing legacy additive-absence/null tolerance |
| `0.3.1` | Exact fresh reduction |
| `0.3.0` | Exact fresh reduction projected to provenance version 0.3.0, plus absence-only tolerance for `ADDED_SINCE_0_3_0` |
| `0.2.x`, missing/malformed, or unknown | Reject: `unsupported reducer version; re-reduction required` (current-era missing/non-object provenance retains its existing named error) |

## Verification

Focused strict/reducer run:

```text
Ran 84 tests in 1.908s
OK
```

Extended strict/reducer/schema run:

```text
Ran 104 tests in 1.997s
OK (skipped=1)
```

Canonical suite tail:

```text
FAIL: test_telemetry_measure_idle_with_fake_nvidia_smi
Ran 926 tests in 33.732s
FAILED (failures=1, skipped=12)
```

The sole failure is outside this diff. An isolated rerun reproduced it: the
pre-existing node-worker test gives its fake Python `nvidia-smi` process only
0.2 seconds, the capture file remained empty before termination, and the
handler correctly returned `telemetry_unavailable`. All reducer/version tests
passed. No out-of-scope node-worker or timing-test change was made.

## Blocker And Next Step

The retained `runs/` corpus is not present in this worktree. Lead must review
the uncommitted diff, adjudicate or rerun the unrelated node-worker timing
test, run the immutable six-bundle strict read-only gate, and commit by
pathspec. No quiet-Mac or live hardware command was run.
