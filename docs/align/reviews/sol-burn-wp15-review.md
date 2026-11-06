# Sol burn review: WP15 R1 runtime

Date: 2026-11-06  
Scope: the WP15 process invoked for each R1 segment, with emphasis on the
High Power model-D legs, clean shutdown, collector reuse, custody, and the
episode deadman. This was a synthetic-only review; no experiment or retained
data path was opened.

## Verdict

**FIXED / synthetic gate passes.** Four concrete fail-open or incomplete-close
defects were present. The patch changes no successful measurement arithmetic or
`runtime_result.json` construction: that object is still assembled from the
same measured fields at `joulewise/align/apple/r1_runtime.py:1241-1259` and
serialized at `joulewise/align/apple/r1_runtime.py:1302-1304`. The full
synthetic conformance test ran every runtime kind, including all three High
Power D legs and all three gated-D members, and remained green (16 tests total
in the focused module, 36.277 s).

## Findings and repairs

### F1 — collector teardown stopped after the first failure (HIGH, fixed)

The old `ManagedSession.close()` ran the synthetic unregister hook before the
SMC close and ran telemetry closers in a `finally`, but a `SystemExit` from the
SMC close escaped the `except Exception` boundary in `Segment.close`; multiple
telemetry closers also stopped at the first exception. A second close could
therefore stop a reused adapter twice. The replacement at
`joulewise/align/apple/r1_runtime.py:648-667` is explicitly idempotent, attempts
the unregister hook, SMC close, and every telemetry closer once, then re-raises
the first error. The regression at `tests/align/test_r1_runtime.py:198-211`
injects an SMC close failure and measures the exact once-only call order:
`unregister, session, powermetrics`.

### F2 — terminal custody omitted nested files with its own basename (HIGH, fixed)

The old basename filter excluded *every* `runtime_custody.json` below the
segment. A model bundle could therefore contain a same-named nested custody
file whose later mutation was invisible to the segment terminal digest. The
filter now excludes only the segment root terminal and its temporary file;
every nested regular file is hashed (`joulewise/align/apple/r1_runtime.py:582-599`).
The regression creates that exact nested name and verifies its SHA-256 appears
in the outer record (`tests/align/test_r1_runtime.py:161-169`).

### F3 — gated D trusted mutable step-D bytes (HIGH, fixed)

The three gated-D members derive their deadman from a sibling step-D result.
Previously the reader checked only JSON shape, so a missing terminal record or
a post-close edit could alter `T_dead`, `B_D`, and `N_chunk`. The reader now
requires the sibling custody schema, `status == complete`, and an exact SHA-256
binding for `runtime_result.json` before returning its slots
(`joulewise/align/apple/r1_runtime.py:851-866`). The regression proves missing
custody refuses, matching custody admits, and a one-byte-equivalent semantic
edit after custody refuses (`tests/align/test_r1_runtime.py:171-185`).

### F4 — malformed deadman slots could disable or corrupt the cap (HIGH, fixed)

`float(slots["T_dead"])` admitted `NaN`, infinity, zero, and negative values;
an invalid `B_D` silently became `None`, removing the decode-token cap. The
runtime now refuses before model execution unless `T_dead` is finite and
positive and `B_D` is an integer multiple of 1,024 in [1,024, 40,960]
(`joulewise/align/apple/r1_runtime.py:1118-1137`). The focused regression covers
`NaN` and the non-aligned value 1,025 (`tests/align/test_r1_runtime.py:187-196`).

## Shutdown and happy-path equivalence

The existing first-signal mechanism still ignores later TERM/INT/HUP signals
and arms the 15 s forced-exit watchdog (`joulewise/align/apple/r1_runtime.py:547-579`).
The existing process-level tests still demonstrate an aborted sensor session
ends with `session_end`, an interrupted model member finalizes its controller
bundle, TERM during powermetrics startup calls `stop_sampling`, and the
watchdog bounds teardown. The focused module also executes the success path
for every segment and passes the driver validators. Because the patch touches
only cleanup, terminal file enumeration, authenticated sibling admission, and
invalid-slot refusal, valid result field derivation and JSON serialization are
byte-identical; the successful conformance assertions are the executable
equivalence guard.

## Residual limits

This review makes no live-hardware claim. In particular, it does not validate
macOS SMC or powermetrics behavior, MLX model loading, APFS crash persistence,
or High Power restoration after an uncatchable SIGKILL. Those require the
separately controlled hardware rehearsal; this agent session did not and must
not perform it.

## Verification

- `python3 -m unittest tests.align.test_r1_runtime` — PASS, 16 tests, 36.277 s.
- `git diff --check` — PASS.

