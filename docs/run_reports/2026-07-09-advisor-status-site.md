# 2026-07-09 Advisor Status Site Live-Depth Refresh

## Context

The Lakebed preview site was already source-derived and deployed, but it
had two advisor-facing weaknesses:

- the freshness banner could say the repo moved while the visible status
  body still showed stale next steps;
- the hand-authored Story page carried volatile counts that had drifted
  from the generated status surface.

User direction: deepen the advisor-facing project-status page, make it
observe live project status without manual refreshes, preserve links into
GitHub for the evidence trail, and record deployment/prod decisions in
the meta logs before changing the deployed preview.

## Decision Record

- D-051 records the source-of-truth policy: repo markdown remains
  authoritative; Lakebed adds fail-soft live overlays instead of becoming
  a second status database.
- C-021 records the review/deployment shape.

## Implementation

- Added `/api/live-status` to the Lakebed capsule. It fetches current
  GitHub raw markdown for `PROJECT_STATUS.md`, `RUN_STATE.md`,
  `TASK_QUEUE.md`, and `docs/risk_register.md`, caches each document for
  60 seconds in Lakebed storage, parses a narrow advisor-facing payload,
  and fails soft if GitHub is unavailable.
- Expanded the generated status cockpit with a live snapshot panel,
  advisor-attention cards, campaign-readiness rows, evidence cards, and
  claim-ceiling panels.
- Added browser polling for `/api/freshness` and `/api/live-status` so
  advisor-visible fields update in place without a manual refresh.
- Removed stale precise counts from the hand-authored Story page and
  linked the live advisor cockpit more directly.
- Updated `site_capsule/README.md` with production smoke checks,
  Lakebed inspection commands, and the live-status endpoint contract.

## Review

- A separate gpt-5.5-high read-only counterreview was spawned before
  deployment to look for generated-site bugs, deployment risks,
  stale-data risks, and missing meta-log obligations.
- Counterreview dispositions:
  - **Accepted/P1:** generated `docs/site/status.html` had to be rebuilt
    before deploy. Fixed by rerunning `python3 scripts/build_site.py` and
    verifying the generated page contains `data-live-panel`,
    `/api/live-status`, and `RESUME-CP5`.
  - **Accepted/P1:** capsule content modules had to be regenerated before
    deploy. Fixed with `python3 scripts/pack_capsule.py`; generated
    content modules are present under `site_capsule/server/content/`.
  - **Accepted/P1:** `/api/live-status` cache was append-only over full
    markdown bodies. Fixed by updating/replacing one row per source and
    deleting older rows for both live-doc and freshness caches.
  - **Accepted/P1:** live parser shape drift was fail-open. Fixed by
    returning `parseErrors` and `unavailable: true` when required fields
    are missing, and by making the status page show a live-parser warning.
  - **Accepted/P2:** stale advisor-facing counts/ranges in
    `PROJECT_STATUS.md` were either made historical or delegated to
    `RUN_STATE.md` / log files as count authorities.
  - **Accepted/P2:** verification and counterreview dispositions were
    recorded here before deploy.

## Verification

Completed before deploy:

- `python3 -m py_compile scripts/build_site.py` -> OK.
- `python3 -m unittest tests/test_build_site_parsers.py tests/test_pack_capsule.py`
  -> 32 tests, OK.
- `python3 scripts/build_site.py` -> rebuilt all generated site pages
  after network access was approved for `npx marked`.
- `python3 scripts/pack_capsule.py` -> packed 0.29 MiB capsule content.
- `npx lakebed build` -> Lakebed artifact validator passed after network
  access was approved for the CLI package.
- `python3 -m unittest discover -s tests` -> 734 tests, OK (skipped=10).

Production smoke checks after deploy:

- `GET /index` -> 200 `text/html`, 15475 bytes.
- `GET /status.html` -> 200 `text/html`, 25558 bytes.
- `GET /api/freshness` -> 200 JSON; 13/14 sources checked, 4 moved
  because local source commits could not be pushed from this environment,
  1 unchecked (`docs/run_reports/2026-07-09-advisor-status-site.md`,
  not present on GitHub main until push), no rate limit.
- `GET /api/live-status` -> 200 JSON; `unavailable: false`,
  `parseErrors: []`, next row `RESUME-CP5`, verification 734 tests,
  corpus 6 bundles.
- `npx lakebed deploy` -> updated
  `https://quiet-signal-6af8833395.lakebed.app`, outbound server fetch
  enabled.
- `git push origin HEAD:main` was attempted after local commits
  `bf9ffc5` and `a1ac0a7`; it failed because this environment lacks
  GitHub HTTPS credentials (`could not read Username for 'https://github.com'`).

## Follow-Up

- If GitHub raw fetches become rate-limited or unreliable, revisit D-051
  and consider authenticated server-side fetches.
- If advisor-specific state is needed, build an explicit advisor portal
  instead of expanding the anonymous public status endpoint.
