# 2026-11-07 — independent ALIGN adversary-kit review

Branch: `align/2026-11-07-adversary-kit-review`. Clean intake head `67b4def8d`;
reviewed kit implementation `a29cded84`. Authority: Ed's independent-review brief
and its blinded/no-network/targeted-tests constraints. Desk work only; nothing
registered, armed, pushed or merged. The requested branch was already checked out.

**Verdict: ADMIT_WITH_FIXES for the DRAFT desk kit.** The full findings, source
pins, statistical derivations, failing-first evidence and test tails are in
[kit-review.md](../align/squeeze/sol/kit-review.md). This is not campaign or
claim admission, and native qualification remains unverified.

## Changes and commits

- `343671290` — `fix(align): fence hidden cache work and retain interrupted controls`.
  Evaluates hidden output plus cache state/auxiliary arrays before certifying an
  output; routes a hidden `SystemExit` through the generic runner's retained
  interruption path; refuses symlink manifests. All three had failing-first
  regressions. Adds a second import-gated native test.
- A following documentation commit contains this report, the independent review,
  and corrected kit instructions, including the public dose-identity warning.
  The exact documentation hash is available in the branch log and final handoff.

Files touched: `joulewise/align/squeeze/{config,control}.py`;
`tests/align/test_squeeze_{config,control,harness,native}.py`;
`docs/align/squeeze/ADVERSARY-KIT.md`;
`docs/align/squeeze/sol/kit-review.md`; this dated report. No configs, manifests,
estimator/protocol code, anchor/W1 bytes, or protected coordination files changed.

## Verification

Serial processes, Python 3.13, synthetic only; all final commands below exit 0.
Test runtime was seconds. No full/quick suite or pytest was run.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_squeeze_config` | 9 passed |
| `python3.13 -B -m unittest tests.align.test_squeeze_control` | 10 passed |
| `python3.13 -B scripts/check_squeeze_overlay.py` | 8 passed against actual pinned runner; no skips |
| `python3.13 -B -m unittest tests.align.test_squeeze_harness` | 8 skipped here; the same 8 ran through the overlay |
| `python3.13 -B -m unittest tests.align.test_squeeze_native` | 2 skipped: MLX absent; not native validation |
| `python3.13 -B -m joulewise.align.squeeze validate --kit configs/align/squeeze` | 13 configs validated |
| `python3.13 -B -m compileall -q joulewise/align/squeeze tests/align/test_squeeze_config.py tests/align/test_squeeze_control.py tests/align/test_squeeze_harness.py tests/align/test_squeeze_native.py` | Passed |
| `git diff --check` and staged checks | Passed |

Additional inline desk probes passed: exact rational order-statistic tails;
the isolated pure `7fbd95e31` split-threshold function at finite/no-finite
boundaries; and recovery of a synthetic 512-output dose from public identity
hashes without receipt access or compute. Only the named pure function AST was
executed, not that calibration script's imports, loader or CLI. The initial
identity probe hit the toy decoder's correctly enforced context cap; a final
combined probe with declared synthetic limit 4096 passed without forwards.

## Findings, remaining questions and handoff

- **Fixed HIGHs:** cache work was not explicitly fenced; `SystemExit` bypassed
  sampler cleanup and run-receipt return. **Fixed LOW:** manifest symlinks.
- **Open HIGH:** config-derived public identities reveal dose assignments to an
  analyst. The transcript monitor does not receive those identities. Which
  blinded export and sealed assignment-map boundary will the lead adopt?
  Recommendation: opaque public assignment IDs, full provenance evaluator-only.
- **Open study gate:** which attack addendum, feedback/selection budgets, joint
  alarm rule and independent cohort will be frozen? Recommendation: declare
  OR alarms and a valid joint false-positive budget if that is the intended
  security endpoint; report success and both-channel evasion. No rule is installed.
- **Statistics:** the old residual API's type-1 rank is not the corrected split
  rank. The named frozen calibration uses the corrected rank, but rank arithmetic
  alone establishes neither score exchangeability nor power. Injection adds a
  new prefill/call and needs its own detection curve, distinct from log omission.
- **Next exact action:** lead reviews the fixes and new tests, then runs
  `python3.13 -B -m unittest tests.align.test_squeeze_native` with MLX and Metal
  outside this sandbox, using the tiny models only. No download is required.
  Actual-model cache/trajectory, deadman, thermal/budget and external-meter
  integration follow only in a separately authorized quiet-machine session.
  Python 3.11, CI, merge-tree full suite and a fresh review of this patch remain
  lead-owned. No efficacy or main-track readiness is established by this review.

Checks that found something material: the cache spy exposed an incomplete
compute boundary; interruption tests exposed missing failed-run retention and
sampler cleanup; the metadata dictionary probe exposed a blinding risk. The
manifest test found a path-boundary defect. The pinned-runner checks confirmed
the fixes on synthetic episodes; the native gate produced no evidence because
it skipped. No claim-bearing measurement or result was produced.

No network or fetch, sealed path/data access, B5 analysis, model download,
external skill/consult/delegation, hardware collection, or process inspection/
signalling occurred. The host fixture census was omitted to avoid enumerating
the unrelated blinded job; these synchronous tests start no background fixture
services. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` are untouched; no kernel task was registered.
