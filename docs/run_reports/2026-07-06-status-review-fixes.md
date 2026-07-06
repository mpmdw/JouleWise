# Run Report: Status-Review Findings Fixed (2026-07-06)

Input: `docs/run_reports/2026-07-06-project-status-review.md` (independent
project/status review; user-directed intake). All three findings were
verified by reproduction before any change, judged genuine, and fixed in
the reviewer's suggested order. Nothing was deferred.

## Triage

- **P1 (event timestamp types)** — accepted as a correctness bug: it
  violated Slice 2N's own acceptance criterion ("reduction failures are
  structured") and the reducer docstring's "never crashes" promise.
  Reproduced exactly as described: `reduce_bundle` raised `ValueError`
  on a corrupted `sampling_started` timestamp, and `validate_bundle`
  raised `TypeError` on mixed-type timestamps.
- **P2 (validator blesses stale summaries)** — accepted; both
  reproductions confirmed (emptied `rail_manifest` and tampered
  `energy_request_j` validated clean). The reviewer offered "broaden the
  default or add a strict mode"; chose the strict mode (D-030) because
  the default is used in CI and on failed/unsupported bundles where a
  fresh reduction is not comparable.
- **P3 (adapter raw writes unguarded)** — accepted; by inspection the
  mock wrote `raw/` via a bare `Path.write_text`. Fixed with the
  reviewer's suggested helper shape.

## What Changed

**Commit `0803d1f` (P1 + P3):**

- `BundleReader.events()` validates every record's `timestamp_s` as a
  finite real number (str/bool/missing/`Infinity`/`NaN` rejected) with a
  line-numbered `BundleReadError`; the window/token/phase accessors can
  no longer leak raw cast errors. `_check_events` (the validate-bundle
  policy) emits `timestamp_s is not a finite number` problem strings and
  runs the ordering check only over clean records.
- New `joulewise.bundle.write_raw_artifact(context, name, data)`:
  adapters get the writer's plain-file-name validation and no-overwrite
  rule (shared implementation, shared collision space) without the
  writer's bundle-lifecycle authority. Mock telemetry converted;
  `adapter_contracts.md` now requires the helper for raw evidence.

**Commit `80c3d49` (P2, D-030):**

- `validate_bundle(path, strict=False)` — default unchanged
  (structural). `--strict` adds, for `status=succeeded` bundles only:
  measured window exists, summed curve is reducer-consumable (>= 2
  in-window samples for a nonzero window), and `summary_metrics.json`
  equals a fresh `reduce_bundle` of the raw artifacts (differing keys
  named in the problem). Strict composes reader + reducer, so it lives
  in `cli.py` (a `bundle_read` home would create an import cycle).
- Phase 4 aggregation inclusion rule and Phase 5 Stage 5.2 sample-bundle
  CI wiring updated to require `--strict`.

**Bookkeeping commit:** test-count sync (playbook M0, README,
`PROJECT_STATUS.md`, exit-checklist summary → 226), queue DOC-006 row,
`RUN_STATE.md`, this report.

## Verification

- Suite: `Ran 226 tests, OK (skipped=10)` (was 222 after P1+P3, 216
  before this session; skip composition unchanged).
- Reviewer reproductions re-run post-fix:
  - corrupted marker timestamp → `reduce_bundle` returns structured
    FAILED (`timestamp_s is not a finite number`), `validate-bundle`
    reports the problem string, no exception;
  - emptied rail manifest → default validation still structural-clean,
    `--strict` reports non-consumable curve + re-reduction mismatch;
  - tampered `energy_request_j` → `--strict` reports the mismatch naming
    the key, exit 2.
- All three fix commits pushed; CI green (see `RUN_STATE.md` for run
  numbers).

## Decision Log / Risks

- New: D-030 (strict validation gate). No risk-register changes; the
  review's bottom-line preconditions for real measurement ("timestamp
  hardening + backup protocol") are now half done — P0-002 (backup
  protocol) remains the open half.

## Review Points Not Requiring Action

The review's "What Is Good" and "Current Project Status" sections match
the repo's own records (queue order confirmed: P0-002, then P3-001, then
gated hardware work). Its fix-order step 4 ("then proceed with P0-002
and gated hardware evidence work") is exactly the standing queue.

## Next Best Task

Unchanged from the queue: **P0-002** (corpus backup protocol — needs the
user to name a destination; the review independently endorses closing it
before any real measurement), then **P3-001** (related-work draft).
