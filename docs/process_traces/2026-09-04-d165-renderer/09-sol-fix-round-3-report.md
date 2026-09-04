# D165-OUTCOME-RENDERER-01 — Sol fix round 3

Date: 2026-09-04  
Seat: Sol implementation, effort xhigh  
Start HEAD: `fac32ce94ca55b423e090a56e4c678b6825f6059` (exact requested head)  
Branch: `feat/2026-09-04-d165-outcome-renderer`  
Authority: paper-I `09-magistrate-rulings-addendum-3.md`; Opus
`08-opus-counter-review.md` read in full before implementation.

## Outcome

R4-B1, R4-S1, R4-S2, and R4-S3 are implemented without changing the D-165
producer/validator, the frozen paper renderer, or `identity_pins.py`.

- OR-01 now uses a 24-code, registry-byte-exact reason-to-sentence map. An
  unmapped value — including the executed `sidecar.cells[1]` / quoted-`repr`
  diagnostic — returns an out-of-band refusal and cannot enter paper prose.
- The finalized `_v5` identity gate checks the full realized model and
  tokenizer pins, their floor-stack counterparts, artifact/runtime/telemetry
  joins, and invokes `identity_pins.stack_identity_sha256` on every
  authenticated manifest arm. Opus's genuine-Qwen2.5 manifest with only
  `model.{name,revision,family}` renamed refuses as `identity_not_v5`.
- The close-out mapping and raw-byte API is gone. The lane opens the close-out,
  finalized manifest, floor artifact, replay sidecar, and validator receipt
  from absolute paths under caller-supplied expected SHA-256 values; the
  receipt binds all four evidence digests and the validator identity; the
  owning validator is replayed; every file is reopened after replay.
- The renderer returns either immutable `OutcomeFillResult.fills` or a direct
  `OutcomeFillRefusal`. A refusal has no `fills` member, and issued fill values
  are guarded against `STOP_FILL`; the successor seam requires refusal on
  stderr with exit 2 and no substitution.
- The undefined `RENDERER_ISSUED` status was removed, `TOKEN_MISSING` restored
  for the blocked before-comparison cases, future oracles labelled with their
  owning receipt missions, decorative/stale fixture fields removed, and both
  registry rows now document the successor seam.

The fabricated-41x chain was made self-consistent, written through the new
path/digest/receipt boundary, and still refused because its cell identifiers
are outside the closed professor-facing label grammar.

## Earlier cures retained

- The before-comparison lane still reopens the exact row/log/manifest/plan-tree
  chain, checks exact-once writer bytes and census/custody, and replays both
  owning validators; its current ambiguous result remains unrenderable.
- Registered stage order remains fixed; no caller precedence channel exists.
- Source and census top-level close-out refusals remain authenticated by the
  D-165 validator. Only registered codes can now render; the census diagnostic
  correctly changed from a prose oracle to `STOP_FILL`.
- OB-01 retains the registered record order, component labels, list grammar,
  and byte-exact branch-B oracle.

## RED then GREEN evidence

### R4-B1 — closed registered reason map and prose hygiene

RED command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome.ResultsFillOutcomeTests.test_r4_b1_reason_map_is_closed_and_diagnostics_never_render
```

RED output:

```text
ERROR: test_r4_b1_reason_map_is_closed_and_diagnostics_never_render
AttributeError: module 'joulewise.results_fill_outcome' has no attribute 'CLOSEOUT_REASON_SENTENCES'
Ran 1 test in 0.000s
FAILED (errors=1)
```

GREEN output, same command:

```text
.
Ran 1 test in 1.659s
OK
```

### R4-S1 — authenticated identity-pin validation

RED command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome.ResultsFillOutcomeTests.test_r4_s1_renamed_qwen25_manifest_refuses_via_identity_validator
```

RED output:

```text
ERROR: test_r4_s1_renamed_qwen25_manifest_refuses_via_identity_validator
TypeError: render_outcome_fills() got an unexpected keyword argument 'closeout_path'
Ran 1 test in 1.607s
FAILED (errors=1)
```

GREEN output, same command:

```text
.
Ran 1 test in 1.630s
OK
```

### R4-S2 — governed paths, digests, receipt, and replay

RED command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome.ResultsFillOutcomeTests.test_r4_s2_closeout_requires_digest_bound_paths_and_replayed_receipt
```

RED output:

```text
FAIL: test_r4_s2_closeout_requires_digest_bound_paths_and_replayed_receipt
AssertionError: 'closeout' unexpectedly found in render_outcome_fills parameters
Ran 1 test in 0.000s
FAILED (failures=1)
```

GREEN output, same command:

```text
.
Ran 1 test in 1.662s
OK
```

### R4-S3 — direct structured refusal, never an in-band sentinel

RED command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome.ResultsFillOutcomeTests.test_r4_s3_refusal_is_out_of_band_from_fill_values
```

RED output:

```text
ERROR: test_r4_s3_refusal_is_out_of_band_from_fill_values
TypeError: render_outcome_fills() missing 1 required positional argument: 'closeout'
Ran 1 test in 0.000s
FAILED (errors=1)
```

GREEN output, same command:

```text
.
Ran 1 test in 1.642s
OK
```

## Final permitted verification

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome tests.test_d165_dominance_closeout
...........................................................
----------------------------------------------------------------------
Ran 59 tests in 11.504s

OK
```

```text
R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
.............
----------------------------------------------------------------------
Ran 13 tests in 2.720s

OK
```

Per the exhaustive preflight fence, no broader suite ran.

## Scope and handoff

Only authorized registry, outcome-renderer, isolated fixture/test, and this
process-trace paths changed. `joulewise/identity_pins.py` was intentionally
left unchanged and consumed through its existing validator. No commit, push,
merge, live-hardware action, or quiet-machine work was performed. The lead's
next exact step is final diff review plus any independent counter-review at
this uncommitted head.
