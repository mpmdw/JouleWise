# P2-046A PROVISIONAL load-transition preparation — 2026-07-11

Status: **Part A complete in the worktree; Part B not executed.** All emitted
evidence is fixture-only or explicitly unadjudicated. This run did not invoke
`/usr/bin/powermetrics`, generate load, run a quiet-window capture, or draw a
physical-bound conclusion. P2-038 remains unamended and authoritative.

## Intake and workspace

- Followed root `AGENTS.md` and Mission M0 before edits.
- No active stop card was present. P2-046A was open as `[AGENT]`; P2-046B was
  and remains `[QUIET-MAC]`.
- Started from clean `impl/p2046a` at `f4fd36e4`.
- Baseline canonical suite: `Ran 1041 tests in 70.873s`,
  `OK (skipped=13)`.
- `origin/main` advanced externally during the run; the pinned worktree now
  reports `behind 3`. No fetch, merge, rebase, commit, or protected-file edit
  was performed.

## Delivered modules and artifacts

- `joulewise/load_transition_alignment.py`
  - pure, stdlib-only manifest/observation validation;
  - frozen midpoint-threshold response detection with two-sample persistence;
  - per-transition offset/support bound, directional median/residual summaries,
    and overall conservative support maximum;
  - stable refusal codes, arithmetic/schema re-derivation, canonical artifact
    identity, deterministic rendering, and atomic writes;
  - fixture status `PROVISIONAL_FIXTURE_ONLY`; future real-Mac status remains
    `PROVISIONAL_REAL_MAC_UNADJUDICATED` and review-required.
- `scripts/characterize_load_transition.py`
  - standalone offline driver binding manifest/observation byte hashes;
  - structured refusal on unreadable/non-finite/schema-invalid input;
  - no sampling, workload, controller, reducer, or CLI integration.
- `configs/calibration/p2_046_load_transition/manifest.json`
  - frozen eight-transition/four-block counterbalanced schedule;
  - exact analysis definitions, persistence/plateau minima, scope gate, and
    refusal policy.
- `tests/fixtures/p2046/`
  - valid hand-computable observation set;
  - malformed and missing-transition refusal inputs;
  - fixture README with closed-form calculations.
- `tests/test_load_transition_alignment.py`
  - ten focused tests for frozen order, hand math, output identity,
    malformed/missing/unobserved refusal, overlap refusal, artifact arithmetic
    re-derivation, total validation of wholly malformed transition artifacts,
    and future provisional Part-B status.
- `docs/contracts/load_transition_alignment.md`
  - formulas, observation/artifact schemas, refusal table, limitations, and
    lead-only Part-B operator runbook.

The existing `tests/fixtures/fake_powermetrics_process.py` was read only and
was not edited. Controller, reducer, CLI, `joulewise/uncertainty_evidence.py`,
`RUN_STATE.md`, `TASK_QUEUE.md`, and generated site files were not edited.

## Artifact schema summary

Schema: `joulewise.load_transition_alignment_artifact.v1`.

Top-level blocks are exact and closed: content-addressed `artifact_id`;
provisional status/disposition; manifest and observation byte-hash provenance;
raw-sample/marker source hashes; the frozen method block; transition records;
direction summaries; one overall conservative support-bound block; and
mandatory limitations.

Transition records retain marker and selected response-sample evidence plus
derived plateau medians/threshold, relative support endpoints, midpoint
offset, directional median center, residual, and
`max(abs(relative support endpoint))`. The validator re-derives transition,
direction, global-bound, and artifact-ID arithmetic before rendering.

The current fixture artifact says:

```text
evidence_status: PROVISIONAL_FIXTURE_ONLY
claim_disposition: NO_PHYSICAL_BOUND_CONCLUSION_PART_B_NOT_EXECUTED
p2_038_disposition: UNASSESSED_PENDING_P2_046B_QUIET_MAC
```

## Closed-form evidence

The frozen fixture has plateau medians `low=1 W`, `high=9 W`, threshold `5 W`.

- idle→load supports `[0,2]`, `[2,4]`, `[0,2]`, `[2,4]` seconds relative to
  markers: offsets `1,3,1,3`; median center `2`; residuals
  `-1,+1,-1,+1`; direction bound `4 s`.
- load→idle supports `[-1,1]`, `[1,3]`, `[-1,1]`, `[1,3]`: offsets
  `0,2,0,2`; median center `1`; residuals `-1,+1,-1,+1`; direction bound
  `3 s`.
- overall fixture-only conservative support bound: `max(4,3) = 4 s`.

These values test closed-form implementation only; they are not physical Mac
evidence and are not a confidence/tolerance bound.

## Determinism evidence

Two independent driver invocations against identical manifest/fixture bytes
produced byte-identical artifacts (`cmp` exit 0):

```text
37a44690cd4547120f6dd8941a327fccfc3b86f0ead33cc5fbc4da74dce64671  /tmp/p2046-artifact-1.json
37a44690cd4547120f6dd8941a327fccfc3b86f0ead33cc5fbc4da74dce64671  /tmp/p2046-artifact-2.json
```

Artifact identity inside both files:

```text
lta-2321badcb2eba04d8f309ce9cdd7ef199721dbc6755b2b749104fba4d8169814
```

The artifact binds manifest byte SHA-256
`fe44dfe61c8ace93e135a03123d3536533ba551ba9092cac4f987b5f3d813914`
and observation byte SHA-256
`90707482be104edf6f83ac914e412fa4533d98764086c2a8f3d99d55558c4005`.

## Verification tails

Focused:

```text
test_artifact_validator_returns_errors_for_wholly_malformed_transition ... ok
test_part_b_input_stays_provisional_and_requires_review ... ok
test_two_identical_fixture_runs_emit_byte_identical_artifacts ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.196s

OK
```

Canonical suite, written to `/tmp/p2046-canonical-tests.log`:

```text
ACCEPTANCE GATE SKIP: six frozen legacy corpus bundles require the retained runs/ corpus
NV-5 ACCEPTANCE GATE SKIP: localhost sockets unavailable; real client-worker subprocess parity was not exercised (PermissionError: [Errno 1] Operation not permitted)
make_figures: ERROR: bundle tree hash mismatch for example-mac-mlx-local__r1
----------------------------------------------------------------------
Ran 1051 tests in 69.850s

OK (skipped=13)
```

The `make_figures` error line is expected output from an existing negative
test; the suite result is green. Additional checks:

- `python3 -m py_compile joulewise/load_transition_alignment.py scripts/characterize_load_transition.py` — passed.
- `git diff --check` — passed.
- protected-file diff check — empty.

## Blocker and exact next step

P2-046B remains deliberately blocked from this agent session by the
`[QUIET-MAC]` gate. The next exact step is for the lead, in a clean controlled
quiet-machine session after rechecking stop-card/backup/readiness gates, to
follow `docs/contracts/load_transition_alignment.md`’s Part-B runbook, retain
raw marker/sample evidence, emit a
`PROVISIONAL_REAL_MAC_UNADJUDICATED` artifact twice with byte identity, and
adjudicate whether P2-038 is provisionally supported, must widen, or is
inconclusive. No result is promoted automatically.
