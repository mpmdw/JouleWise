# Advisor status site analysis

Status: pre-implementation analysis (implementation landed with this PR).
Date: 2026-07-09.

Live site inspected: `https://quiet-signal-6af8833395.lakebed.app/index`.
Lakebed docs consulted: `https://docs.lakebed.dev/`,
`https://docs.lakebed.dev/reference/`, and
`https://docs.lakebed.dev/capsule-api/`.

## Executive summary

The Lakebed deployment is a solid advisor-observability foundation: it serves
the generated site, carries per-source provenance stamps, and has a live
freshness API that checks whether the baked snapshot has drifted from `main`.

The main gap is depth and authority layering. The generated `status.html` page
is honest but thin: it shows phase, tests, queue, risks, and evidence links.
It does not yet show the project as an advisor would naturally inspect it:
current pause/gate, what changed since last check, what evidence is strongest,
what claims are allowed, what data collection is waiting on, what the advisor
can unblock, and what should be read next.

The live deployment is also currently stale relative to `main` for the two
source documents that matter most for "what next": `RUN_STATE.md` and
`TASK_QUEUE.md`. The freshness layer correctly reports that drift, but the page
content still says the next work is `P2-015` while the current repo queue has
`RESUME-CP5` at rank 0. For advisor use, that is the first fix: redeploy after
front-facing doc movement, and make the drift banner more prominent as a
"snapshot is stale" state rather than only a small bottom notice.

## Production facts observed

Network fetches were run against the live Lakebed app.

- `GET /index`: `200 text/html; charset=utf-8`, 15496 bytes.
- `GET /`: `200 text/html; charset=utf-8`, 739 bytes, Preact redirect shell.
- `GET /status.html`: `200 text/html; charset=utf-8`, 12056 bytes.
- `GET /roadmap.html`: `200 text/html; charset=utf-8`, 34453 bytes.
- `GET /style.css`: `200 text/css; charset=utf-8`, 27047 bytes.
- `HEAD /index` and `HEAD /status.html`: `404`. This is consistent with the
  Lakebed endpoints being registered for `GET` only, but it may surprise link
  checkers or preview unfurlers.
- `/api/freshness`: `200`, checked 14 sources, 0 unchecked, not rate-limited.
  It reported 2 moved sources: `RUN_STATE.md` and `TASK_QUEUE.md`.
- Freshness build payload reported `build.commit: 036913e`,
  `builtAt: 2026-07-09T01:33:32Z`.

Lakebed platform facts relevant to this site:

- Lakebed capsules are small full-stack TypeScript apps with
  `server/index.ts`, `client/index.tsx`, `shared/`, and optional
  `.env.lakebed.server`.
- External HTTP routes are expected to use `endpoint({ method, path },
  handler)`.
- If a `GET` endpoint and a client route share a path, direct HTTP requests
  hit the endpoint first.
- Claimed deploys are required before relying on hosted server env or outbound
  server-side fetch. This matches the current freshness API design.
- Hosted deploy inspection is private by default and available through
  `npx lakebed inspect`, `npx lakebed db dump`, and `npx lakebed logs`.

Live content observations:

- `status.html` shows `734 tests`, `6 bundles`, and next work as `P2-015`.
- `status.html` does not mention `RESUME-CP5` because the deployed snapshot was
  built before the current queue/state moved.
- `index` is hand-authored and contains stale numbers: `546` tests,
  `D-001...D-036`, and `C-001...C-010`, while current project docs are past
  those counts.
- `index` has far less source provenance than generated pages. The packer
  allows hand pages without source chips, which is practical but weakens their
  authority for advisor use.

## What works well

### 1. Source-derived observatory pages

`scripts/build_site.py` derives `status.html`, `roadmap.html`, `record.html`,
`library.html`, and long-form rendered docs from repo sources. It fails closed
when expected headings or tables move. That is exactly the right base for an
advisor view because the public page cannot silently invent project state.

### 2. Live freshness is real, not decorative

The Lakebed capsule packs page source stamps and compares them with GitHub
commits server-side. The current drift report is a real catch: it shows that
the deploy is behind `RUN_STATE.md` and `TASK_QUEUE.md`.

### 3. The information architecture already has useful rails

The nav split is good:

- Story
- Status
- Roadmap
- Record
- Results
- Process
- Research
- Sources

For an advisor, that maps to: why this matters, where it stands, what happens
next, what evidence exists, what data says, how the work is governed, what
questions it answers, and where the raw sources live.

### 4. Deployment constraints are documented

`site_capsule/README.md` records the platform constraints that caused prior
deploy failures: artifact size, reserved paths, banned tokens in source,
runtime `Response` behavior, and outbound freshness mechanics. That makes the
deployment maintainable rather than magical.

## High-priority gaps

### Gap 1: The live page can be stale exactly where the advisor cares most

Current freshness says the snapshot is behind `RUN_STATE.md` and
`TASK_QUEUE.md`. The site does indicate drift, but the main page still renders
old queue content. An advisor will read the page body first and the drift
banner second.

Recommended change:

- Move freshness/drift status into the status page header as a first-viewport
  "Snapshot state" readout.
- If any source moved, show `Snapshot stale: N source docs moved since build`
  near the top, not only in the bottom banner.
- If `RUN_STATE.md` or `TASK_QUEUE.md` moved, label the status page as
  "planning snapshot stale" because those are authority docs for next action.

### Gap 2: Hand-authored Story page carries stale metrics

The `/index` story page is advisor-friendly but hand-maintained. It currently
contains old test counts, decision counts, council counts, and process counts.
That undermines trust because the generated status page is more current than
the entry page.

Recommended change:

- Either generate `index.html` from the same parsed sources, or strip precise
  moving counts from hand-authored copy.
- Add source chips to Story readouts, or make each readout come from a parsed
  source.
- Add an automated stale-number test for hand pages: fail if `index.html`
  contains old `Ran N tests`, `D-001...`, `C-001...`, or similar count patterns
  inconsistent with source docs.

### Gap 3: The status page lacks an advisor-specific "ask"

Advisors usually need to know what to do with a status page. Today the page
tells them what is next, but not what external decisions or feedback are
needed.

Recommended change:

Add an "Advisor attention" section with:

- scope/acceptance-bar status
- calendar/deadline status
- device access status
- wall-meter decision
- backup destination
- what feedback would change the plan

This can be parsed from `[ED-EXTERNAL]` rows in `TASK_QUEUE.md` and open risks
such as calendar/scope/device access.

### Gap 4: Evidence is linked, but not ranked

"Where the evidence lives" points to Sources, Risk Register, and critique. It
does not tell an advisor which evidence is most load-bearing.

Recommended change:

Add an Evidence Board with ranked evidence cards:

- harness works end-to-end
- strict re-derivation over real bundles
- suite substrate built and live-gated
- first energy measurements on M3 Max
- flagship 122B run
- KV replay feasibility verdict
- site freshness/deployment health

Each card should include: claim ceiling, source doc, run report, command or
artifact pointer, and current invalidation risk.

### Gap 5: Claims and gates are not visible enough

The project is unusually careful about claims, floors, and analysis plans. That
care is buried in contracts. An advisor page should surface it because it is a
major methodological strength.

Recommended change:

Add a "Claims allowed today" section:

- L0/L1 instrument/capability claims already supported.
- L2/L3 comparative claims wait on P2-015 floors and filled AP rows.
- Split-inference claims wait on Phase 3 hardware gates.
- Content/difficulty suite claims are prepped but not campaign-backed yet.

This should parse from `claims_ladder.md`, `analysis_plans.md`, and
`RUN_STATE.md`, or be generated from a compact source table added to the
contracts.

### Gap 6: Campaign readiness is fragmented

The next real work is data collection, but readiness is spread across queue
rows, run reports, stream logs, and specs.

Recommended change:

Add a "Campaign readiness" matrix:

| Item | State | Blocking condition | Evidence |
|---|---|---|---|
| CP-5 resume | active/pending/done | PR merge + methodology adjudication | stream log |
| P2-015 floors | queued | quiet Mac | task queue |
| P2-006 2M | queued after floors | quiet Mac + floor artifact | task queue |
| Suite manifests | ready/stale | text hash guard | configs + P2-025 |
| Affine envelope gate | pending | script/PR | task queue |
| Backup | interim | external destination | risk/queue |

This is the single most useful advisor-depth addition.

### Gap 7: Routing is mostly fine, but aliases and HEAD behavior are rough

The user-facing link `/index` works. Root `/` works through a client redirect.
However, `HEAD /index` and `HEAD /status.html` return 404, and extensionless
paths like `/status` return 404.

Recommended change:

- Add aliases for extensionless page paths: `/status`, `/roadmap`, `/record`,
  `/results`, `/process`, `/research`, `/sources`.
- If Lakebed supports HEAD endpoints, register them for main pages. If not,
  document that only GET is expected and make sure external previews use
  `/index`.
- Prefer server endpoints for these aliases rather than client routes, because
  Lakebed's documented routing order gives direct HTTP requests to matching
  `GET` endpoints before client routes.

### Gap 8: Lakebed runtime observability is underused

The deployment currently has an excellent `/api/freshness` endpoint, but the
analysis flow depends on external `curl` checks. Lakebed provides hosted
inspection commands for deploys, DB rows, and logs.

Recommended change:

- Add a short production-smoke section to `site_capsule/README.md` using
  `npx lakebed inspect`, `npx lakebed db dump`, and `npx lakebed logs`.
- Add a small deploy-health row to the advisor status page:
  build commit, built-at time, freshness checked-at time, moved source count,
  and whether freshness was unavailable/rate-limited.
- Keep inspection private. Do not deploy with public inspection unless a demo
  explicitly requires public logs/state.

## Proposed advisor-depth page shape

The status page should become the advisor's live cockpit. Suggested first
viewport:

1. Snapshot state
   - Fresh / stale / freshness unavailable.
   - Built commit, build time, sources moved.
   - If planning docs moved, say planning snapshot stale.

2. Current truth
   - Current phase.
   - Active pause/gate: `RESUME-CP5` if still active.
   - Test count and strict corpus count.
   - Next quiet-window work, but only after active P0/P1 gates.

3. Advisor attention
   - External asks and decisions.
   - Dates/deadlines missing.
   - Scope acceptance-bar missing.

Second viewport:

4. Campaign readiness matrix.
5. Evidence board.
6. Claims allowed today.
7. Risks that could invalidate current plan.

Third viewport:

8. Recent changes.
9. Next three queue items by lane.
10. Sources and run reports.

## Implementation plan

### Phase A: Correctness and drift

- Regenerate and redeploy after current source changes so `RESUME-CP5` appears
  if still active.
- Add prominent snapshot-state UI from `/api/freshness`.
- Add extensionless aliases.
- Remove or derive stale moving numbers from `index.html`.
- Add Lakebed production-smoke commands to `site_capsule/README.md`, including
  `npx lakebed inspect <url>`, `npx lakebed db dump <url>`, and
  `npx lakebed logs <url>`.

Acceptance:

- Live `/status.html` and `/roadmap.html` match current `TASK_QUEUE.md`.
- `/api/freshness` reports 0 moved sources immediately after deploy.
- `index` no longer contains stale test/decision/council counts.
- Hosted deploy inspection works from `site_capsule/` using the committed
  `lakebed.json` binding.

### Phase B: Advisor cockpit

- Add parsers for `[ED-EXTERNAL]` queue rows and high-impact open risks.
- Add Campaign Readiness matrix.
- Add Advisor Attention section.
- Add Evidence Board with source chips.

Acceptance:

- Build fails if `TASK_QUEUE.md` has no active external rows but the page tries
  to render an advisor ask.
- Every card links to a source doc or run report.
- No hand-entered queue ranks or test counts.

### Phase C: Claims and evidence depth

- Add a compact claims-status source table or parser over existing
  `claims_ladder.md` / `analysis_plans.md`.
- Render "Claims allowed today" and "Claims waiting on evidence."
- Add bundle/evidence pack pointers once P2-027 lands.

Acceptance:

- No L2/L3 language appears without an AP row and floor state.
- Claim cards show exact blockers.

### Phase D: Deployment hardening

- Add route alias tests in `tests/test_pack_capsule.py`.
- Add a production smoke checklist: GET `/index`, `/status.html`,
  `/roadmap.html`, `/api/freshness`, `/style.css`.
- Add a hand-page stale-number test or migrate Story to generated content.

Acceptance:

- Main page, status page, and roadmap are all either source-derived or tested
  against source-derived counts.
- Production smoke results are recorded in the deployment run report.

## Design guidance

Keep the current instrument aesthetic. It is distinctive and appropriate for a
measurement project. The depth should come from better evidence layering, not
more visual ornament.

Specific UI recommendations:

- Use dense but readable matrices for readiness and evidence.
- Keep advisor asks in plain language.
- Use badges sparingly: `fresh`, `stale`, `blocked`, `ready`, `waiting`.
- Keep provenance chips visible.
- Make stale snapshot state impossible to miss.
- Avoid turning the page into a marketing homepage. The advisor wants an
  instrument panel.

## Immediate next action

Before adding richer panels, redeploy the current source truth. The freshness
layer is already telling us the snapshot is behind. Once the live page reflects
`RESUME-CP5` and current queue state, implement Phase A and Phase B above.
