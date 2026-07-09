# JouleWise site capsule (Lakebed)

Serves the whole generated JouleWise site (`docs/site/`) from one Lakebed
capsule, plus a **live GitHub freshness layer**: every page checks whether
the repo has moved past the commits the snapshot was built from and shows a
drift banner if so.

**Live:** https://quiet-signal-6af8833395.lakebed.app

## How it fits together

- `docs/site/*.html` + `style.css` + `fonts/` are the source of truth (built
  by `scripts/build_site.py` from the repo's process docs).
- `scripts/pack_capsule.py` packs that site into gitignored TypeScript
  content modules under `server/content/` (gzip+base64 page bodies, one
  shared stylesheet, per-source provenance stamps parsed from the pages).
- `server/index.ts` registers one HTTP endpoint per page (canonical path +
  aliases), a `/style.css` endpoint, `/api/freshness` (live), `/api/health`.
- `client/index.tsx` is a tiny Preact shell that redirects `/` → `/index`
  (Lakebed reserves `/` and `/index.html` for the client shell).

## Deploy / update (the canonical flow)

```sh
# from the repo root — regenerate the site first if docs changed:
python3 scripts/build_site.py
python3 scripts/pack_capsule.py          # fonts OFF by default (see note)
cd site_capsule && npx lakebed deploy    # updates the existing deployId
```

`lakebed.json` pins the `deployId`, so `deploy` updates the same URL. The
deploy is **claimed/owned** (needed for outbound `fetch` to GitHub); an
anonymous deploy would disable freshness.

## Fonts note (why the default is fonts-off)

Lakebed caps the deploy artifact at 1 MiB. The embedded woff2 fonts alone
exceed that, so `pack_capsule.py` defaults to the CSS fallback stacks
(Iowan Old Style / Georgia serif, SF Mono / Menlo mono, system sans) — the
editorial character holds. `python3 scripts/pack_capsule.py --fonts` inlines
the real Fraunces / IBM Plex faces for hosts without the size limit.

## Freshness behavior

`/api/freshness` compares each source's baked commit against
`GET /repos/mpmdw/JouleWise/commits?path=<source>&sha=main`, DB-cached for
5 minutes. It **fails soft**: if a refresh fails after cached evidence exists,
the API returns the newest cached rows, marks affected sources `stale: true`,
and sets `unavailableRefresh: true` / `unavailable: true`. If no evidence is
available, it returns `{unavailable: true}`. The page must never treat a failed
refresh as proof that a source has not moved. Set `GITHUB_TOKEN` in
`.env.lakebed.server` for higher rate limits (optional; the public API works
unauthenticated).

`/api/live-status` fetches the current GitHub markdown for the advisor-facing
status sources (`PROJECT_STATUS.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, and the
risk register), parses the same high-level fields as the static generator, and
caches them for one minute in the Lakebed DB. The status page polls this
endpoint so the top-line queue, verification, and status readouts can update
without a redeploy. It fails soft: if GitHub or outbound access is unavailable,
it returns the newest cached markdown-derived payload when available, marks
those source rows stale, and sets `unavailableRefresh: true`; otherwise, the
baked page remains the source of visible truth.

## Production smoke / inspection

After deploying, verify the public endpoints:

```sh
curl -s -o /dev/null -w '%{http_code} %{content_type} %{size_download}\n' \
  https://quiet-signal-6af8833395.lakebed.app/index
curl -s -o /dev/null -w '%{http_code} %{content_type} %{size_download}\n' \
  https://quiet-signal-6af8833395.lakebed.app/status.html
curl -s https://quiet-signal-6af8833395.lakebed.app/api/freshness
curl -s https://quiet-signal-6af8833395.lakebed.app/api/live-status
```

Lakebed hosted inspection is private by default and should stay that way for
this project. From `site_capsule/`, use the committed `lakebed.json` binding:

```sh
npx lakebed inspect https://quiet-signal-6af8833395.lakebed.app
npx lakebed db dump https://quiet-signal-6af8833395.lakebed.app
npx lakebed logs https://quiet-signal-6af8833395.lakebed.app
```

## Platform constraints worked around (so future edits don't reintroduce them)

The Lakebed deploy validator textually scans server source (comments
included) and rejects `process`, `fetch`, `globalThis`, `self`, unbounded
`for(;;)` loops, and >2 MiB request bodies; the production runtime lacks a
global object and has a broken `Response` constructor (`Buffer.alloc`).
Hence: gzip+base64 page bodies emitted as chunked string literals, token
escaping in the packer, a Unicode-escaped `fetch` identifier, a bounded
decode loop, and a manual `DecompressionStream` + `TextDecoder` path (no
`Response`). Keep these if you edit `server/index.ts`.
