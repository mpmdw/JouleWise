# Next observer spec

Status: draft. Scope: suite-aware observer surfaces for the generated site and
process docs.

## Purpose

The observer is a source-derived evidence surface, not a second dashboard with
hand-maintained state. It should help a reader answer:

- What is true now?
- What changed most recently?
- What happens next?
- What could invalidate the current story?
- Where is the evidence?

The existing site observatory already implements the core pattern:
fail-closed parsers over process docs, generated pages under `docs/site`, and
per-source provenance stamps. Suite next-layer work should extend that pattern
rather than inventing a separate status channel.

## Source-of-truth inputs

The observer may parse:

- `RUN_STATE.md`
- `TASK_QUEUE.md`
- `PROJECT_STATUS.md`
- `docs/run_reports/*.md`
- `docs/stream_logs/*.md`
- `docs/contracts/*.md`
- `docs/decision_log.md`
- `docs/council_log.md`
- `docs/risk_register.md`
- generated checkpoint artifacts once they exist

It must not treat generated HTML as source truth.

Stream logs may be parsed only for structured status/checkpoint fields and
artifact pointers. Public/generated observer pages must not quote raw
deliberation, reviewer rationale, or agent reasoning text from stream logs;
they should link to the source or summarize only canonical status fields.

## Suite-aware surfaces

Draft observer additions:

### Suite Readiness Strip

Shows the current suite pre-campaign state:

- CP-5 resume status
- P2-015/P2-006 quiet-window gate state
- suite follow-on readiness: envelope gate, real-tokenizer manifests,
  text-path hash guard
- latest strict validation count and suite test count from `RUN_STATE.md`

### Suite Evidence Matrix

Rows are suite profiles; columns are evidence layers:

- manifest committed
- sidecar committed
- byte-identical regeneration checked
- strict-valid mock run
- strict-valid real MLX run
- checkpoint gate
- analysis-plan row
- floor artifact applied
- campaign corpus available

Each cell must link to source docs or artifact paths. Empty means unknown or
not yet present, not failure.

### Checkpoint Verdict Feed

Once checkpoint artifacts exist, list:

- checkpoint ID
- verdict
- failure/advisory codes
- manifest hash
- bundle IDs
- generated-at timestamp
- source artifact path

This feed should be generated from machine-readable checkpoint JSON, not prose
scraping from run reports.

### Claim-Ceiling Guard

For pages that summarize suite results, surface the allowed claim ceiling:

- L0/L1 until floors and n are available
- L2 only with a filled AP row and floor clearance
- L3 only for plans with holdouts and prediction-error rules

This guard should quote IDs and links, not invent new claim language.

## Update flow

1. Update source docs and artifacts first.
2. Run `python3 scripts/build_site.py`.
3. For front-facing changes, follow the close-out rule in `RUN_STATE.md`:
   regenerate, pack, and redeploy the Lakebed capsule.
4. If parser expectations fail, update the source docs or parser tests before
   treating the site as current.
5. Do not manually patch generated HTML except as part of changing the
   generator.

## Acceptance criteria

- Build is fail-closed: missing expected headings, malformed tables, or stale
  machine-readable artifacts produce a nonzero build with a clear message.
- No hand-typed counts, statuses, queue ranks, or verdicts appear in generated
  observatory pages when a source parser can derive them.
- Every generated suite claim links to source docs/artifacts and displays
  source commit/dirty provenance.
- Mobile pages remain non-overflowing at the established 390px target.
- The observer never hides the P0 `RESUME-CP5` pause while it is active.
- The Lakebed snapshot freshness/drift story remains visible.

## Rationale

The observatory is useful precisely because it cannot become more optimistic
than the repo. Source-derived pages caught stale status once already. Extending
that discipline to suite checkpoint verdicts and campaign readiness prevents a
very plausible failure mode: the science is careful in contracts, but the
reader-facing surface quietly rounds it upward.

Rejected alternatives:

- Maintain a separate YAML/JSON status registry by hand. Rejected because it
  becomes a second source of truth.
- Put rich suite dashboards into run reports. Rejected because run reports are
  historical records, not live observer state.
- Show scoreboards before floor gates. Rejected because it invites claim
  inflation.

## Revisit triggers

- Checkpoint JSON artifacts land and need parser support.
- The public site becomes an advisor-facing or submission-facing deliverable
  with stricter accessibility/export requirements.
- Bundle-pack publication work changes the artifact index shape.
